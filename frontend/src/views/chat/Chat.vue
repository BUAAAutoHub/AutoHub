<script>
import axios from "axios"
import getIdenticon from "@/utils/identicon";
import {computed} from "vue";
import topicSetting from "@/utils/topic-setting";

export default {
    name: "Chat",

    data() {
        return {
            selectedRoom: 0,
            messageInput: '',
            chatRooms: [],
            createSheet: false,
            inviteSheet: false,
            expelSheet: false,
            createRoomName: '',
            createRoomDesc: '',
            projectPopulation: [],
            selectedPopulation: [],
            expelledPopulation: [],
            inviteNominees: computed(() => this.projectPopulation.filter((item, index) => {
              return this.chatRooms[this.selectedRoom].users.find((user, index) => {
                return user.userId === item.peopleId
              }) === undefined
            })),
            inviteSelected: [],
            messageServiceAvailable: false
        }
    },
    inject: {
      user: {default: null},
      proj: {default: null}
    },
    created() {
        // this.initWS(1)
        this.updateChatRooms()
        this.updatePopulation()
        this.initMessagingService()
    },
    methods: {
        getIdenticon,
        updateChatRooms() {
            console.log('updating chat rooms...')
            // 保存现有的ws和history
            let tempWS = {}
            let tempHistory = {}
            this.chatRooms.forEach((item, index) => {
              if (item.ws !== null) {
                tempWS[item.id] = item.ws
                tempHistory[item.id] = item.history
              }
            })

            // 调用API更新chatRooms
            this.chatRooms = []
            axios.post('/api/chat/discussions', {
              projectId: this.proj.projectId,
              userId: this.user.id
            }).then((res) => {
              console.log(res.data)
              if (res.data.errcode === 0) {
                let chatRooms = res.data.data.discussions.map((item, index) => {
                  return {
                    id: item.roomId,
                    title: item.roomName,
                    desc: item.outline,
                    users: item.users,
                    history: [],
                    selectedUser: null
                  }
                })
                console.log(chatRooms)
                // 去除chatRooms中id重复的项目
                let temp = {}
                chatRooms.forEach((item, index) => {
                  if (temp[item.id] === undefined) {
                    temp[item.id] = item
                  }
                })
                this.chatRooms = Object.values(temp)
                console.log(chatRooms)
                this.selectedRoom = 0
              } else {
                throw new Error('get discussion list failure with non 0 errcode (' + res.data.errcode + ')')
              }
            }).catch((err) => {
              this.chatRooms = []
              console.error(err)
              this.$message({
                type: 'error',
                message: 'get discussion list failure with error: ' + err
              })
            }).finally(() => {
              // 重新分配ws
              this.chatRooms.forEach((item, index) => {
                if (tempWS[item.id] !== undefined) {
                  item.ws = tempWS[item.id]
                  tempWS[item.id] = undefined
                  item.history = tempHistory[item.id]
                } else {
                  item.ws = this.initWS(item.id)
                  this.getChatHistory(item)
                }
              })

              // 关闭多余的ws
              for (const [key, value] of Object.entries(tempWS)) {
                if (value !== undefined) {
                  value.close()
                }
              }
            })
        },
        createChatRoom() {
            if (this.createRoomName === '') {
              this.$message({
                type: 'warning',
                message: '请输入聊天室名称'
              })
              return
            } else if (this.createRoomDesc === '') {
              this.$message({
                type: 'warning',
                message: '请输入聊天室简介'
              })
              return
            }
            let users = this.selectedPopulation.map((item, index) => {
              return item.peopleId
            })
            axios.post('/api/chat/createRoom', {
              projectId: this.proj.projectId,
              roomName: this.createRoomName,
              outline: this.createRoomDesc,
              currentUserId: this.user.id,
              users: users
            }).finally(() => {
              this.updateChatRooms()
            })

            this.createRoomName = ''
            this.createRoomDesc = ''
            this.selectedPopulation = []
            this.expelledPopulation = this.projectPopulation
            this.createSheet = false
        },
        getChatHistory(room) {
            axios.post('/api/chat/getRoomMessages', {
              roomId: room.id,
              userId: this.user.id
            }).then((res) => {
              console.log(res.data)
              room.history = []
              if (res.data.errcode === 0) {
                res.data.data.messages.reverse().map((item, index) => {
                  room.history.push({
                    from: item.senderName,
                    content: item.content,
                    time: item.time,
                    type: 'group'
                  })
                })
                // 去除room.history中time相同的项目
                let temp = {}
                room.history.forEach((item, index) => {
                  if (temp[item.time] === undefined) {
                    temp[item.time] = item
                  }
                })
                room.history = Object.values(temp)
              } else {
                throw new Error('get room messages failure with non 0 errcode (' + res.data.errcode + ')')
              }
            }).catch((err) => {
              console.error(err)
              this.$message({
                type: 'error',
                message: 'get room messages failure with error: ' + err
              })
            })
        },
        inviteUserToChat(roomId, userId) {
          axios.post('/api/chat/addPerson', {
            roomId: roomId,
            userId: userId,
          }).then((res) => {
            console.log(res)
          }).finally(() => {
            this.messageInput = `${this.user.name}` + '邀请' + `${this.inviteNominees[this.inviteSelected].peopleName}` + '加入了聊天室'
            this.sendMsg()
            setTimeout(() => {
              this.updateChatRooms()
              this.inviteSheet = false
            }, 2000)
          })

        },
        updatePopulation() {
          axios.post('/api/plan/showPersonList', {
            projectId: this.proj.projectId,
            userId: this.user.id
          }).then((res) => {
            if (res.data.errcode !== 0) {
              throw new Error('get person list failure with non 0 errcode (' + res.data.errcode + ')')
            } else {
              this.projectPopulation = res.data.data.filter((item, index) => {
                return item.peopleId !== this.user.id
              })
              this.expelledPopulation = res.data.data.filter((item, index) => {
                return item.peopleId !== this.user.id
              })
              console.log(res.data.data)
            }
          }).catch((err) => {
            console.error(err)
            this.$message({
              type: 'error',
              message: 'get person list failure with error: ' + err
            })
          })
        },
        initWS(rid) {
          console.log('initWS: connecting to ws://127.0.0.1/:8000/ws/chat/' + this.user.id.toString() + '/' + rid.toString())
          const socket = new WebSocket('ws://127.0.0.1:8000/ws/chat/' + this.user.id.toString() + '/' + rid.toString());

          const onopen = (e) => {
            console.log('socket opened')
            // socket.send(JSON.stringify({
            //   sender: this.user.id,
            //   type: 1,
            //   message: this.user.name + ' has joined the group chat!'
            // }))
          }

          socket.onopen = onopen

          const onmessage = (fromName, fromId, content, time) => {
            // 找到this.chatRooms中id为rid的room
            let room = this.chatRooms.find((item, index) => {
              return item.id === rid
            })
            if (room === undefined) {
              console.error('room not found')
            } else {
              room.history.splice(0, 0, {
                from: fromName,
                type: 'group',
                content: content,
                time: time
              })
              if (this.messageServiceAvailable && document.visibilityState === 'hidden' && fromName !== this.user.name) {
                const notification = new Notification(`来自讨论室 ${room.title} 的一条新消息`, {
                  body: `${fromName}: ${content}`,
                  icon: getIdenticon(fromName, 100, 'user')
                })
              }
            }
          }

          socket.onmessage = function (event) {
            console.log('Message from server ', event.data);
            var data = JSON.parse(event.data)
            onmessage(data.senderName, data.senderId, data.content, data.time)
          };

          socket.onerror = function (event) {
            console.error('WebSocket error observed:', event)
          }

          socket.onclose = function (e) {
            console.log('Socket is closed.', e.reason);
          }

          return socket
        },
        sendMsg() {
            if ((this.messageInput || '').length > 80) {
              this.$message({
                type: 'error',
                message: '消息太长了'
              })
              return
            }
            if (this.messageInput === '') {
              this.$message({
                type: 'error',
                message: '消息不能为空'
              })
              return
            }
            console.log('will send: ' + this.messageInput)
            this.chatRooms[this.selectedRoom].ws.send(JSON.stringify({
                sender: this.user.id,
                type: 1,
                message: this.messageInput
            }));
            this.messageInput = ''
        },
        initMessagingService() {
          if ("Notification" in window) {
            console.log('Notification is supported, initing messaging service')
            Notification.requestPermission().then(permission => {
              if (permission === "granted") {
                console.log('Notification permission granted')
                this.messageServiceAvailable = true;
                const notification = new Notification('已注册消息通知', {
                  icon: '../../favicon.ico',
                  body: "消息通知已开启，AutoHub会在收到新消息时显示提醒",
                })
              } else {
                console.log('Notification permission denied')
                this.messageServiceAvailable = false;
              }
            })
          }
        },
        expelUser(room, expelledUser) {
          console.log(room, expelledUser)
          axios.post('/api/chat/deletePerson', {
            userId: expelledUser.userId,
            roomId: room.id
          }).finally(() => {
            this.messageInput = `${this.user.name}` + '将' + `${expelledUser.userName}` + '移出了讨论室'
            this.sendMsg()
            setTimeout(() => {
              this.updateChatRooms()
              this.expelSheet = false
            }, 2000)
          })
        },
        getDarkColor: topicSetting.getDarkColor,
        getTopicColor: topicSetting.getColor,
        getLinearGradient: topicSetting.getLinearGradient,
        getRadialGradient: topicSetting.getRadialGradient
    },
    beforeRouteLeave(to, from, next) {
      console.log('leaving chat room, closing all ws')
      this.chatRooms.forEach((item, index) => {
        item.ws.close()
      })
      next()
    },
}
</script>

<template>
<v-container>
    <h1>聊天室</h1>
    <v-row>
        <v-col cols="3">
            <v-list>
                <v-list-item-group v-model="selectedRoom" mandatory>
                    <v-list-item two-line v-for="item in chatRooms" :key="item.id">
                        <v-list-item-content>
                          <v-list-item-title style="font-weight: bold"><span :style="'color: ' + getDarkColor(user.topic)">{{ item.title }}</span> <span class="float-end grey--text">{{item.desc}}</span> </v-list-item-title>
                          <v-list-item-subtitle>
                            {{item.history.length === 0 ? '还没有消息哦' : item.history[0].from + ' : ' + item.history[0].content}}
                            <span class="float-end">{{item.history.length === 0 ? '' : new Date(item.history[0].time).toLocaleTimeString()}}</span>
                          </v-list-item-subtitle>
                        </v-list-item-content>
                    </v-list-item>
                </v-list-item-group>
                <v-divider></v-divider>
                <v-list-item ripple @click="createSheet = !createSheet">
                    <v-list-item-content><span :style="'color: ' + getDarkColor(user.topic)">创建新的聊天室</span></v-list-item-content>
                    <v-list-item-icon>
                      <v-icon :color="getDarkColor(user.topic)">mdi-plus-circle</v-icon>
                    </v-list-item-icon>
                </v-list-item>


                <v-dialog v-model="createSheet">
                  <v-card>
                    <v-card-title>
                      创建新的聊天室
                    </v-card-title>
                    <v-card-text>
                      <v-row>
                        <v-spacer></v-spacer>
                        <v-col cols="5">
                          <v-text-field label="聊天室名称" v-model="createRoomName"></v-text-field>
                        </v-col>
                        <v-col cols="5">
                          <v-text-field label="聊天室简介" v-model="createRoomDesc"></v-text-field>
                        </v-col>
                        <v-spacer></v-spacer>
                      </v-row>
                      <v-row>
                        <v-spacer></v-spacer>
                        <v-col cols="5">
                          从右边选择聊天室成员

                          <v-chip pill class="ma-2 accent-1" color="green"
                            @click="() => {
                              this.$message({
                                type: 'error',
                                message: '把自己踢出聊天室，这也太狠了！'
                              })
                            }"
                          >
                            <v-avatar left><v-img :src="getIdenticon(user.name, 50, 'user')" ></v-img></v-avatar>
                            您
                          </v-chip>

                          <v-chip v-for="item in selectedPopulation" class="ma-2 accent-1" color="green" :key="item.peopleId"
                            @click="() => {
                              expelledPopulation.push(item)
                              selectedPopulation.splice(selectedPopulation.indexOf(item), 1)
                            }"
                          >
                            <v-avatar left><v-img :src="getIdenticon(item.peopleName, 50, 'user')" ></v-img></v-avatar>
                            {{ item.peopleName }}
                          </v-chip>

                        </v-col>

                        <v-col cols="5">
                          <span v-if="expelledPopulation.length !== 0">不在聊天室的成员：</span>
                          <span v-else>大家都在聊天室里了哦</span>

                          <v-chip v-for="item in expelledPopulation" :key="item.peopleId" class="ma-2"
                            @click="() => {
                              selectedPopulation.push(item)
                              expelledPopulation.splice(expelledPopulation.indexOf(item), 1)
                            }"
                          >
                            <v-avatar left><v-img :src="getIdenticon(item.peopleName, 50, 'user')" ></v-img></v-avatar>
                            {{ item.peopleName }}
                          </v-chip>
                        </v-col>
                        <v-spacer></v-spacer>
                      </v-row>
                    </v-card-text>
                    <v-card-actions>
                      <v-spacer></v-spacer>
                      <v-btn plain :color="getDarkColor(user.topic)" @click="createChatRoom">创建！</v-btn>
                    </v-card-actions>
                  </v-card>
                </v-dialog>
            </v-list>
        </v-col>

        <v-col cols="9">
            <v-row v-if="chatRooms.length > 0">
                <v-col cols="12">
                  <v-card>
                      <v-card-title class="v-app-bar-title">{{ chatRooms[selectedRoom].title }}</v-card-title>
                      <v-card-subtitle>
                        <v-icon v-if="this.chatRooms[this.selectedRoom].ws !== undefined && this.chatRooms[this.selectedRoom].ws.readyState === 1" class="green--text">mdi-circle</v-icon>
                        <v-icon v-else class="yellow--text">mdi-circle</v-icon>
                        {{chatRooms[selectedRoom].desc === '' ? '这个聊天室没有简介哦' : chatRooms[selectedRoom].desc }} | {{chatRooms[selectedRoom].users.length}} 名成员
                      </v-card-subtitle>
                      <v-card-text>
                        <span v-for="user in chatRooms[selectedRoom].users" :key="user.userId">
                            <v-btn fab @click="chatRooms[selectedRoom].selectedUser = chatRooms[selectedRoom].selectedUser === user ? null : user">
                              <v-avatar size="50px" class="mx-1">
                                <v-img :alt="user.username" :src="getIdenticon(user.userName, 50, 'user')"></v-img>
                              </v-avatar>
                            </v-btn>
                        </span>
<!--                        {{chatRooms[selectedRoom].selectedUser === null ? 'null' : chatRooms[selectedRoom].selectedUser.name}}-->
                        <v-avatar class="mx-1 float-end">
                          <v-icon size="50px" @click="inviteSheet = !inviteSheet" :color="getDarkColor(user.topic)">mdi-plus-circle</v-icon>
                        </v-avatar>
                      </v-card-text>
                      <v-expand-transition>
                        <div v-if="chatRooms[selectedRoom].selectedUser !== null">
                          <v-divider></v-divider>
                          <v-card-actions>
                            <v-avatar size="50px" class="mx-1"><v-img :src="getIdenticon(chatRooms[selectedRoom].selectedUser.userName, 50, 'user')"></v-img></v-avatar>
                            <strong>{{chatRooms[selectedRoom].selectedUser.userName}}</strong>
                            <strong>{{chatRooms[selectedRoom].selectedUser.userName === this.user.name ? '（您自己）' : ''}}</strong>
                            <v-spacer></v-spacer>
                            <v-btn v-if="chatRooms[selectedRoom].selectedUser.userName !== this.user.name" color="red" class="white--text" @click="expelSheet = !expelSheet"><v-icon>mdi-alert</v-icon>移除群聊</v-btn>
                          </v-card-actions>
                        </div>
                      </v-expand-transition>
                  </v-card>
                </v-col>

                <v-bottom-sheet inset v-model="expelSheet">
                  <v-card v-if="chatRooms[selectedRoom].selectedUser !== null">
                    <v-card-title>删除成员确认</v-card-title>
                    <v-card-text>警告！这样做会导致成员 {{ chatRooms[selectedRoom].selectedUser.userName }} 无法访问聊天室“{{chatRooms[selectedRoom].title }}”。您确定要删除成员 {{ chatRooms[selectedRoom].selectedUser.userName }} 吗？</v-card-text>
                    <v-card-actions>
                      <v-spacer></v-spacer>
                      <v-btn color="green" class="white--text" @click="expelSheet = !expelSheet">再想想</v-btn>
                      <v-btn color="red" class="white--text" @click="() => expelUser(chatRooms[selectedRoom], chatRooms[selectedRoom].selectedUser)"><v-icon>mdi-alert</v-icon>我确定</v-btn>
                    </v-card-actions>
                    <div style="height: 50vh"></div>
                  </v-card>
                </v-bottom-sheet>

                <v-dialog v-model="inviteSheet">
                  <v-card>
                    <v-card-title>邀请新成员加入聊天室</v-card-title>
                    <v-card-text v-if="inviteNominees.length !== 0">
                      <v-chip-group
                          mandatory
                          v-model="inviteSelected"
                          active-class="primary--text">
                        <v-chip v-for="item in inviteNominees" class="ma-2" :key="item.peopleId"
                                  @click="() => {
                                expelledPopulation.push(item)
                                selectedPopulation.splice(selectedPopulation.indexOf(item), 1)
                              }"
                          >
                            <v-avatar left><v-img :src="getIdenticon(item.peopleName, 50, 'user')" ></v-img></v-avatar>
                            {{ item.peopleName }}
                        </v-chip>
                      </v-chip-group>
                      <v-divider></v-divider>
                      <v-card-subtitle v-if="inviteNominees[inviteSelected] !== undefined">要邀请 {{inviteNominees[inviteSelected].peopleName}} 进入群聊“{{ chatRooms[selectedRoom].title }}”吗？</v-card-subtitle>
                      <v-card-actions>
                        <v-btn plain :color="getDarkColor(user.topic)" @click="() => inviteUserToChat(chatRooms[selectedRoom].id, inviteNominees[inviteSelected].peopleId)">确定邀请</v-btn>
                        <v-btn plain class="red--text" @click="() => inviteSheet = !inviteSheet">我再想想</v-btn>
                      </v-card-actions>
                    </v-card-text>
                    <v-card-text v-else>
                      <v-card-subtitle>项目所有的成员都在聊天室里了！</v-card-subtitle>
                      <v-card-actions>
                        <v-btn plain :color="getDarkColor(user.topic)" @click="() => inviteSheet = !inviteSheet">好</v-btn>
                      </v-card-actions>
                    </v-card-text>

                  </v-card>
                </v-dialog>
            </v-row>
            <v-row v-if="chatRooms.length > 0">
                <v-col cols="12">
                    <v-card>
                        <v-card-text>
                          <v-row>
                            <v-spacer></v-spacer>
                            <v-col cols="10">
                              <v-text-field
                                  rounded filled counter="80"
                                  label="输入消息"
                                  v-model="messageInput"
                                  :append-outer-icon="'mdi-send'"
                                  @click:append-outer="sendMsg"
                                  @keydown.enter="sendMsg"
                              ></v-text-field>
                            </v-col>
                            <v-spacer></v-spacer>
                          </v-row>
                            <v-list min-height="600" max-height="600" class="overflow-auto scroll-y">
                                <v-list-item-group>
<!--                                  <v-slide-y-transition class="py-0" group tag="v-list-item-group">-->
                                    <template v-for="item in chatRooms[selectedRoom].history">
                                      <v-divider :key="item.id"></v-divider>
                                      <v-list-item disabled two-line :key="item.id" v-if="user.name !== item.from" >
                                        <v-list-item-avatar size="40px">
                                          <v-img :src="getIdenticon(item.from, 50, 'user')"></v-img>
                                        </v-list-item-avatar>
                                        <v-list-item-content>
                                          <v-list-item-title class="text--primary" style="font-weight: bold; font-size: large;">{{ item.content }}</v-list-item-title>
                                          <v-list-item-subtitle>{{ item.from }}<span class="float-end">{{ new Date(item.time).getDate() === new Date().getDate() ? new Date(item.time).toLocaleTimeString() : new Date(item.time).toLocaleString() }}</span></v-list-item-subtitle>
                                        </v-list-item-content>
                                      </v-list-item>
                                      <v-list-item disabled two-line :key="item.id" v-else :style="getLinearGradient(user.topic)">
                                        <v-list-item-content>
                                          <v-list-item-title class="text--primary" style="font-weight: bold; font-size: large;"><span class="float-end">{{ item.content }}</span></v-list-item-title>
                                          <v-list-item-subtitle>{{ new Date(item.time).getDate() === new Date().getDate() ? new Date(item.time).toLocaleTimeString() : new Date(item.time).toLocaleString() }}<span class="float-end">您</span></v-list-item-subtitle>
                                        </v-list-item-content>
                                        <v-list-item-avatar size="40px">
                                          <v-img :src="getIdenticon(item.from, 50, 'user')"></v-img>
                                        </v-list-item-avatar>
                                      </v-list-item>
                                    </template>
<!--                                  </v-slide-y-transition>-->
                                </v-list-item-group>
                            </v-list>
                        </v-card-text>
                    </v-card>
                </v-col>
            </v-row>
            <v-row v-else>
              <v-col cols="12">
                <v-card>
                  <v-card-title>还没有讨论室哦</v-card-title>
                  <v-card-text>
                    <v-card-actions>
                      <v-btn plain class="green--text accent-1" @click="createSheet = !createSheet">去创建！</v-btn>
                    </v-card-actions>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
        </v-col>
    </v-row>
</v-container>
</template>

<style>
.v-enter-active {
  animation: slideInLeft-enter 0.3s;
}

.v-leave-active {
  animation: slideInLeft-enter 0.3s reverse;
}

@keyframes slideInLeft-enter {
  0% {
    opacity: 0%;
    transform: translateX(-100%);
  }
  100% {
    opacity: 100%;
    transform: translateX(0);
  }
}
</style>