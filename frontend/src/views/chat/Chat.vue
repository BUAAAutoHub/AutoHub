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
            messageServiceAvailable: false,
            // 新增数据
            searchDialog: false,
            searchText: '',
            searchResults: [],
            searchLoading: false,
            deleteDialog: false,
            currentDeleteRoom: null,
            // 新增默认群聊名称状态
            defaultGroupName: '',
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
        // // 在created钩子中增加路由参数解析
        // const routeQuery = this.$route.query
        // if (routeQuery.defaultGroupName) {
        //     this.defaultGroupName = routeQuery.defaultGroupName
        //     this.createRoomName = routeQuery.defaultGroupName // 自动填充默认名称
        // }

        // if (this.$route.query.from === 'float') {
        //   this.$nextTick(() => {
        //     this.createSheet = true
        //   })
        // }
        if (this.$route.query.from === 'float') {
            this.$nextTick(() => {
                const query = this.$route.query;
                console.log('路由参数:', query); // 调试
            
                // 3. 智能填充默认值
                this.createRoomName = query.defaultGroupName || '快速讨论组';
                
                // 4. 自动选择当前项目成员（排除自己）
                this.selectedPopulation = this.projectPopulation.filter(user => 
                    user.peopleId !== this.user.id
                );

                // 5. 自动打开创建对话框
                this.createSheet = true;

                // 6. 添加防抖避免重复创建
                this.debouncedCreate = _.debounce(() => {
                    this.createChatRoom();
                }, 3000);
            
            })
        }
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
                  this.scrollToBottom() // 添加
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
          // 自动生成默认名称时的处理逻辑
            if (this.createRoomName === this.defaultGroupName) {
                // 添加时间戳保证唯一性
                const timestamp = new Date().toLocaleDateString().replace(/\//g, '-')
                this.createRoomName = `${this.defaultGroupName}_${timestamp}`
            }

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
              // 成功后重置默认名称
              this.defaultGroupName = ''
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
                res.data.data.messages.map((item, index) => {
                  room.history.push({
                    from: item.senderName,
                    content: item.content,
                    time: item.time,
                    type: 'group'
                  })
                  this.scrollToBottom() // 添加
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
          console.log('initWS: connecting to ws://10.254.47.34/:8000/ws/chat/' + this.user.id.toString() + '/' + rid.toString())
          const socket = new WebSocket('ws://10.254.47.34:8000/ws/chat/' + this.user.id.toString() + '/' + rid.toString());

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
              // room.history.splice(0, 0, {
              //   from: fromName,
              //   type: 'group',
              //   content: content,
              //   time: time
              // })
              room.history.push({
                from: fromName,
                type: 'group',
                content: content,
                time: time
              })
              this.scrollToBottom()
              if (this.messageServiceAvailable && document.visibilityState === 'hidden' && fromName !== this.user.name) {
                const notification = new Notification(`来自讨论室 ${room.title} 的一条新消息`, {
                  body: `${fromName}: ${content}`,
                  icon: getIdenticon(fromName, 100, 'user')
                })
              }
            }
          }

          // socket.onmessage = function (event) {
          //   console.log('Message from server ', event.data);
          //   var data = JSON.parse(event.data)
          //   onmessage(data.senderName, data.senderId, data.content, data.time)
          // };

          socket.onmessage = (event) => { // 改为箭头函数保持 this 指向
            var data = JSON.parse(event.data)
            this.$nextTick(() => {
              const room = this.chatRooms.find(r => r.id === rid)
              if (room) {
                room.history.push({
                  from: data.senderName,
                  content: data.content,
                  time: data.time,
                  type: 'group'
                })
                this.scrollToBottom()
              }
            })
          }

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
            this.scrollToBottom() // 新增
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
        formatTime(time) {
          const date = new Date(time);
          const now = new Date();
          
          // 如果是今天显示时间，否则显示日期
          return date.toDateString() === now.toDateString() 
            ? date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
            : date.toLocaleDateString();
        },
        scrollToBottom() {
          this.$nextTick(() => {
            const container = this.$el.querySelector('.message-list')
            if (container) {
              container.scrollTop = container.scrollHeight
            }
          })
        },
        // 搜索内容方法
        async searchMessages() {
          if (!this.searchText.trim()) return;
          
          this.searchLoading = true;
          try {
            const res = await axios.post('/api/chat/searchMsg', {
              roomId: this.chatRooms[this.selectedRoom].id,
              searchText: this.searchText,
              userId: this.user.id
            });
            this.searchResults = res.data.data.messages || [];
          } catch (error) {
            console.error('搜索失败:', error);
            this.$message.error('搜索失败: ' + error.response?.data?.message || error.message);
          } finally {
            this.searchLoading = false;
          }
        },
        highlightText(text) {
          if (!this.searchText) return text;
          const regex = new RegExp(`(${this.searchText})`, 'gi');
          return text.replace(regex, '<span class="highlight">$1</span>');
        },
        
        // 显示删除确认对话框
        showDeleteConfirm(room) {
          this.currentDeleteRoom = room
          this.deleteDialog = true
        },

        // 执行删除操作
        async confirmDeleteRoom() {
          try {
            const res = await axios.post('/api/chat/deleteRoom', {
              roomId: this.currentDeleteRoom.id,
              userId: this.user.id
            })

            if (res.data.errcode === 0) {
              // 从列表中移除
              this.chatRooms = this.chatRooms.filter(r => r.id !== this.currentDeleteRoom.id)
              
              // 如果删除的是当前选中的聊天室
              if (this.selectedRoom >= this.chatRooms.length) {
                this.selectedRoom = Math.max(0, this.chatRooms.length - 1)
              }
              
              this.$message.success('聊天室已删除')
            } else {
              throw new Error(res.data.message)
            }
          } catch (error) {
            this.$message.error(`删除失败: ${error.message}`)
          } finally {
            this.deleteDialog = false
            this.currentDeleteRoom = null
          }
        },

        // 判断是否显示删除按钮
        canDeleteRoom(room) {
          // 调试，可以删除
          return true
          // 示例逻辑：创建者或管理员可以删除
          // return this.user.role === 'admin' || room.creatorId === this.user.id
        },
        // 生成链接
        linkify(text) {
          const urlRegex = /(\b(https?|ftp|file):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/gi;
          return text.replace(urlRegex, url => {
            return `<a href="${url}" target="_blank" class="message-link">${url}</a>`;
          });
        },
        // 新增生成摘要方法
        async generateSummary() {
            this.summaryLoading = true
            console.log('pid: ', this.proj.projectId)
            console.log('uid: ', this.user.id)
            console.log('rid: ', this.chatRooms[this.selectedRoom].id)
            try {
                const res = await axios.post('/api/ai/summary', {
                    pid: this.proj.projectId,
                    uid: this.user.id,
                    rid: this.chatRooms[this.selectedRoom].id
                })
                
                if (res.data && res.data.reply) {
                    this.summaryContent = res.data.reply
                    this.summaryDialog = true
                } else {
                    throw new Error(res.data.message)
                }
            } catch (error) {
                
                this.$message.error('生成摘要失败: ' + error.message)
            } finally {
                this.summaryLoading = false
            }
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
                            <v-list-item-title style="font-weight: bold">
                            <span :style="'color: ' + getDarkColor(user.topic)">{{ item.title }}</span>
                            <span class="float-end grey--text">{{item.desc}}</span>
                          </v-list-item-title>
                          <v-list-item-subtitle>
                            {{item.history.length === 0 ? '还没有消息哦' : item.history[0].from + ' : ' + item.history[0].content}}
                            <span class="float-end">{{item.history.length === 0 ? '' : new Date(item.history[0].time).toLocaleTimeString()}}</span>
                          </v-list-item-subtitle>
                        </v-list-item-content>

                        <!-- 添加删除按钮 -->
                        <v-list-item-action v-if="canDeleteRoom(item)">
                          <v-btn icon @click.stop="showDeleteConfirm(item)">
                            <v-icon color="error">mdi-delete</v-icon>
                          </v-btn>
                        </v-list-item-action>
                    </v-list-item>

                    <!-- 添加删除确认对话框 -->
                    <v-dialog v-model="deleteDialog" max-width="500">
                      <v-card>
                        <v-card-title class="headline">删除聊天室确认</v-card-title>
                        <v-card-text>
                          确定要永久删除聊天室 "{{ currentDeleteRoom?.title }}" 吗？该操作不可逆！
                          <br>
                          <span class="red--text">所有聊天记录和成员信息都将被清除！</span>
                        </v-card-text>
                        <v-card-actions>
                          <v-spacer></v-spacer>
                          <v-btn text @click="deleteDialog = false">取消</v-btn>
                          <v-btn color="error" @click="confirmDeleteRoom">确认删除</v-btn>
                        </v-card-actions>
                      </v-card>
                    </v-dialog>
                </v-list-item-group>
                <v-divider></v-divider>
                <v-list-item ripple @click="createSheet = !createSheet">
                    <v-list-item-content>
                      <span :style="'color: ' + getDarkColor(user.topic)">创建新的聊天室</span>
                    </v-list-item-content>
                    <v-list-item-icon>
                      <v-icon :color="getDarkColor(user.topic)">mdi-plus-circle</v-icon>
                    </v-list-item-icon>
                </v-list-item>
              </v-list>


                <v-dialog v-model="createSheet">
                  <v-card>
                    <v-card-title>
                      创建新的聊天室
                      <v-chip v-if="defaultGroupName" small color="primary" class="ml-2">
                      智能建议名称
                      </v-chip>
                    </v-card-title>
                    <v-card-text>
                      <v-row>
                        <v-spacer></v-spacer>
                        <v-col cols="5">
                          <v-text-field 
                        label="聊天室名称"
                        v-model="createRoomName"
                        :hint="defaultGroupName ? '基于当前项目生成的建议名称' : ''"
                        persistent-hint
                        :rules="[
                            v => !!v || '名称不能为空',
                            v => v.length <= 20 || '名称最多20个字符',
                            v => !/[_\-]{2,}/.test(v) || '连续符号不易识别'
                        ]"
                        >
                        <template v-slot:prepend>
                            <v-icon :color="getTopicColor(user.topic)">mdi-forum</v-icon>
                        </template>
                        </v-text-field>
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

                      <!-- 添加智能命名说明 -->
                    <v-alert v-if="defaultGroupName" type="info" dense outlined class="mt-3">
                    <div class="text-caption">
                        智能命名规则：
                        <v-chip x-small color="info">项目名称</v-chip> + 
                        <v-chip x-small color="info">快速讨论组</v-chip> + 
                        <v-chip x-small color="info">创建日期</v-chip>
                    </div>
                    </v-alert>
                    </v-card-text>
                    <v-card-actions>
                      <v-spacer></v-spacer>
                      <v-btn plain :color="getDarkColor(user.topic)" @click="createChatRoom">创建！</v-btn>
                    </v-card-actions>
                  </v-card>
                </v-dialog>
        </v-col>

        <v-col cols="9">
            <v-row v-if="chatRooms.length > 0">
                <v-col cols="12">
                  <v-card>
                      <!-- 群聊头部信息 -->
                        <v-card-title class="d-flex align-center">
                            <div>
                                <div class="text-h5">{{ chatRooms[selectedRoom].title }}</div>
                                <div class="text-caption grey--text mt-1">
                                    <v-icon small 
                                            :color="chatRooms[selectedRoom].ws?.readyState === 1 ? 'green' : 'yellow'">
                                        mdi-circle
                                    </v-icon>
                                    {{ chatRooms[selectedRoom].desc || '这个聊天室没有简介哦' }} · 
                                    {{ chatRooms[selectedRoom].users.length }}名成员
                                </div>
                            </div>
                            <v-spacer></v-spacer>
                            <!-- 新增生成摘要按钮 -->
                            <v-btn 
                                icon 
                                @click="generateSummary"
                                :loading="summaryLoading"
                                color="primary"
                                class="mr-2"
                            >
                                <v-icon>mdi-text-box-search</v-icon>
                                <template v-slot:loader>
                                    <v-progress-circular indeterminate size="24"></v-progress-circular>
                                </template>
                            </v-btn>
                            <v-btn icon @click="searchDialog = true">
                                <v-icon>mdi-magnify</v-icon>
                            </v-btn>
                        </v-card-title>

                        <!-- 新增摘要对话框 -->
                        <v-dialog v-model="summaryDialog" max-width="800">
                            <v-card>
                                <v-card-title class="headline">
                                    讨论摘要
                                    <v-spacer></v-spacer>
                                    <v-btn 
                                        icon
                                        @click="summaryDialog = false"
                                    >
                                        <v-icon>mdi-close</v-icon>
                                    </v-btn>
                                </v-card-title>
                                
                                <v-divider></v-divider>
                                
                                <v-card-text class="pa-4">
                                    <div v-if="summaryContent" class="summary-content">
                                        <pre style="white-space: pre-wrap;">{{ summaryContent }}</pre>
                                    </div>
                                    
                                    <v-alert
                                        v-else
                                        type="info"
                                        outlined
                                        class="mt-4"
                                    >
                                        正在生成讨论摘要，请稍候...
                                    </v-alert>
                                </v-card-text>

                                <v-card-actions>
                                    <v-spacer></v-spacer>
                                    <v-btn 
                                        color="primary"
                                        @click="summaryDialog = false"
                                    >
                                        关闭
                                    </v-btn>
                                </v-card-actions>
                            </v-card>
                        </v-dialog>

                        <!-- 成员列表 -->
                        <v-card-text class="py-2">
                          <v-row justify="space-between" align="center" no-gutters>
                            <!-- 成员列表 -->
                            <v-col cols="auto" class="d-flex flex-wrap">
                              <v-btn 
                                v-for="user in chatRooms[selectedRoom].users" 
                                :key="user.userId" 
                                fab 
                                small
                                class="ma-1"
                                @click="chatRooms[selectedRoom].selectedUser = user"
                              >
                                <v-avatar size="40">
                                  <v-img :src="getIdenticon(user.userName, 50, 'user')"/>
                                </v-avatar>
                              </v-btn>
                            </v-col>
                            
                            <!-- 添加按钮 -->
                            <v-col cols="auto" class="ml-auto">
                              <template v-if="$vuetify.breakpoint.mdAndUp">
                                <v-btn 
                                  color="primary"
                                  @click="inviteSheet = true"
                                  class="ml-2"
                                >
                                  <v-icon left>mdi-account-plus</v-icon>
                                  添加成员
                                </v-btn>
                              </template>
                              <template v-else>
                                <v-btn 
                                  icon
                                  @click="inviteSheet = true"
                                  class="ml-2"
                                >
                                  <v-icon large color="primary">mdi-account-plus</v-icon>
                                </v-btn>
                              </template>
                            </v-col>
                          </v-row>
                        </v-card-text>

                        <!-- 聊天内容区域 -->
                        <v-card-text>
                            <div class="chat-container">
                                <!-- 消息列表 -->
                                <div class="message-list">
                                    <template v-for="(item, index) in chatRooms[selectedRoom].history">
                                        <!-- 接收消息 -->
                                        <div v-if="user.name !== item.from" 
                                            :key="index + 'received'"
                                            class="d-flex align-start mb-4">
                                            <v-avatar size="40" class="message-avatar">
                                                <v-img :src="getIdenticon(item.from, 50, 'user')"/>
                                            </v-avatar>
                                            <div class="message-bubble received-message">
                                                <div class="font-weight-bold text-caption">{{ item.from }}</div>
                                                <div v-html="linkify(item.content)"></div>
                                                <span class="message-time">{{ formatTime(item.time) }}</span>
                                            </div>
                                        </div>

                                        <!-- 发送消息 -->
                                        <div v-else 
                                            :key="index + 'sent'"
                                            class="d-flex justify-end mb-4">
                                            <div class="message-bubble sent-message">
                                                <div v-html="linkify(item.content)"></div>
                                                <span class="message-time">
                                                    {{ formatTime(item.time) }} · 已送达
                                                </span>
                                            </div>
                                            <v-avatar size="40" class="message-avatar">
                                                <v-img :src="getIdenticon(item.from, 50, 'user')"/>
                                            </v-avatar>
                                        </div>
                                    </template>
                                </div>

                                <!-- 输入框 -->
                                <div class="input-footer">
                                    <v-text-field
                                        v-model="messageInput"
                                        class="rounded-input"
                                        outlined
                                        dense
                                        placeholder="输入消息..."
                                        counter="80"
                                        hide-details
                                        @keydown.enter="sendMsg"
                                        append-icon="mdi-send"
                                        @click:append="sendMsg">
                                        <template v-slot:prepend>
                                            <v-icon color="primary">mdi-message-text</v-icon>
                                        </template>
                                    </v-text-field>
                                </div>
                            </div>                      </v-card-text>
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

                <!-- 邀请成员对话框 -->
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
            
                <!-- 搜索对话框 -->
                <v-dialog v-model="searchDialog" max-width="600">
                    <v-card>
                        <v-card-title class="headline">搜索聊天记录</v-card-title>
                        <v-card-text>
                            <v-text-field
                                v-model="searchText"
                                label="输入搜索关键词"
                                outlined
                                clearable
                                @keydown.enter="searchMessages"
                                append-icon="mdi-magnify"
                                @click:append="searchMessages">
                            </v-text-field>

                            <v-progress-linear
                                v-if="searchLoading"
                                indeterminate
                                color="primary">
                            </v-progress-linear>

                            <div v-if="searchResults.length > 0" class="search-results">
                                <div v-for="(msg, index) in searchResults" 
                                    :key="index" 
                                    class="search-item pa-2 mb-2">
                                    <div class="d-flex align-center">
                                        <v-avatar size="36" class="mr-2">
                                            <v-img :src="getIdenticon(msg.senderName, 50, 'user')"/>
                                        </v-avatar>
                                        <div>
                                            <div class="font-weight-bold">{{ msg.senderName }}</div>
                                            <div v-html="highlightText(msg.content)"></div>
                                            <div class="text-caption grey--text">
                                                {{ formatTime(msg.time) }}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div v-else-if="searchText && !searchLoading" class="text-center py-4">
                                没有找到相关结果
                            </div>
                        </v-card-text>
                    </v-card>
                 </v-dialog>
            </v-row>

            <!-- 空状态 -->
            <v-row v-else>
              <v-col cols="12">
                <v-card>
                  <v-card-title>还没有讨论室哦</v-card-title>
                  <v-card-text>
                    <v-card-actions>
                      <v-btn plain 
                                      class="green--text accent-1"
                                      @click="createSheet = true">
                                    去创建！
                                </v-btn>
                    </v-card-actions>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
        </v-col>
    </v-row>
</v-container>
</template>

<style scoped lang="scss">
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
/* 整体聊天容器 */
.chat-container {
  background: white; /* 整体背景设为白色 */
  height: calc(100vh - 280px);
  display: flex;
  flex-direction: column;
}

/* 消息列表区域 */
.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: white; /* 消息区域背景白 */
}

/* 通用气泡样式 */
.message-bubble {
  max-width: 70%;
  margin: 8px 0;
  padding: 12px 16px;
  border-radius: 20px;
  position: relative;
  color: #000; /* 强制黑色字体 */
  font-family: 'Helvetica Neue', sans-serif;
}

/* 他人消息气泡 */
.received-message {
  background: #B3E5FC; /* 浅蓝色 */
  border-radius: 18px 18px 18px 4px;
}

/* 自己消息气泡 */
.sent-message {
  background: #A5D6A7; /* 浅绿色 */
  border-radius: 18px 18px 4px 18px;
}

/* 可选其他颜色方案 */
/*
.received-message { background: #F8BBD0; } 浅粉色 
.sent-message { background: #80DEEA; } 浅青色
*/

/* 时间戳样式 */
.message-time {
  font-size: 0.75rem;
  color: rgba(0, 0, 0, 0.6); /* 半透明黑色 */
  margin-top: 4px;
  display: block;
}

/* 输入框容器 */
.input-footer {
  background: white;
  padding: 16px;
  border-top: 1px solid #eee;
}

/* 输入框样式 */
.rounded-input {
  border-radius: 30px;
  background: white;
}

/* 头像调整 */
.message-avatar {
  margin: 0 8px;
  align-self: flex-end;
}

/* 高亮样式 */
.highlight {
  background-color: #fff9c4;
  color: #c17900;
  padding: 2px 4px;
  border-radius: 3px;
}

/* 搜索对话框优化 */
.v-card__title .v-input {
  max-width: 300px;
}

/* 添加删除按钮悬停效果 */
.v-list-item__action .v-btn:hover {
  transform: scale(1.2);
  transition: transform 0.2s;
}

/* 危险操作强调色 */
.delete-warning {
  border-left: 4px solid #ff5252;
  padding-left: 12px;
}

/* 新增智能提示样式 */
.v-chip--recommend {
  border: 1px dashed currentColor;
  background: rgba(255,255,255,0.1) !important;
}

.message-link {
  color: #2196F3 !important;
  text-decoration: underline;
  word-break: break-all;
  &:hover {
    color: #1976D2 !important;
    text-decoration: none;
  }
}
</style>