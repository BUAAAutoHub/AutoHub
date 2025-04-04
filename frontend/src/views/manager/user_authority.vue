<template>
  <v-container>
    <v-card>
      <v-card-title>
        <v-text-field
            v-model="search"
            append-icon="mdi-magnify"
            label="搜索"
            single-line
            hide-details
        ></v-text-field>
      </v-card-title>
      <v-data-table
          :headers="headers"
          :items="userMessages"
          :search="search"
      >
        <template #item.auth="{item}">
          <v-chip :color="getColor(item.auth)" dark @click="openChangeUserAuthorityDialog(item)">
            {{ transform(item.auth) }}
<!--            <v-text v-if="item.status==='A'"> 正常 </v-text>-->
<!--            <v-text v-if="item.status==='B'"> 禁用 </v-text>-->
          </v-chip>
        </template>
        <template #item.registerTime="{item}">
          {{ pro(item.registerTime) }}
        </template>
<!--        <template #item.changeStatus="{item}">-->
<!--          <v-btn class="ml-1" small outlined @click="openChangeUserStatusDialog(item)">修改用户状态</v-btn>-->
<!--        </template>-->
        <!--
        <template #item.userProfile="{item}">
          <v-btn class="ml-1" small outlined @click="openUserProfileDialog(item)">用户个人信息</v-btn>
        </template>
        -->

      </v-data-table>
    </v-card>
    <v-dialog v-model="showChangeUserAuthority" width="300">
      <template>
        <v-container class="pa-0">
          <v-card>
            <v-card-title class="headline font-weight text-left"> 修改用户{{userAuthorityDialogMessage.name}}的权限 </v-card-title>
            <v-divider></v-divider>
            <v-card-text>
              <v-radio-group v-model="selectedAuthority">
                <v-radio v-for="i in authorityList" :key="i.value" :label="i.label" :value="i.value"></v-radio>
              </v-radio-group>
            </v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn color="red" text @click="closeChangeUserAuthorityDialog">取消</v-btn>
              <v-btn color="blue" text @click="changeAuthority">确认修改</v-btn>
            </v-card-actions>
          </v-card>
        </v-container>
      </template>
    </v-dialog>
    <v-dialog v-model="showUserProfile" width="500">
      <template>
        <v-container class="pa-0">
          <v-card>
            <v-card-title class="headline font-weight text-left"> 用户{{userProfileDialogMessage.name}}的个人信息 </v-card-title>
            <v-divider></v-divider>

            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn color="red" text @click="closeUserProfileDialog">关闭</v-btn>
              <v-btn color="blue" text @click="saveProfile">确认修改</v-btn>
            </v-card-actions>
          </v-card>
        </v-container>
      </template>
    </v-dialog>
  </v-container>
</template>

<script>
import axios from "axios";
import Cookies from "js-cookie";
import util from "@/views/util";
export default {
  inject: {
    user: { default: null },
    //setFrom: { default: null}
  },
  data () {
    return {
      msg: null,
      search: '',
      headers: [
        {
          text: '用户名',
          align: 'start',
          // sortable: false,
          value: 'name',
        },
        { text: '邮箱', value: 'email' },
        { text: '注册时间', value: 'registerTime' },
        { text: '权限等级', value: 'auth' },
      ],
      userMessages: [
      ],
      // 用户权限dialog相关信息
      showChangeUserAuthority: false,
      userAuthorityDialogMessage: '',
      selectedAuthority: '',
      authorityList: [
        {
          label: '教师',
          value: 3
        },
        {
          label: '助教',
          value: 2
        },
        {
          label: '用户',
          value: 1
        },
      ],
      // 用户个人信息dialog相关信息
      showUserProfile: false,
      userProfileDialogMessage: '',
      // 跳转到用户端的相关信息
      gotoUserProjectPageMessage: '',
    }
  },
  created() {
    this.showUserMessages()
  },
  // TODO：传给后端管理员id，如果报错，不显示信息而显示弹窗
  methods: {
    pro(registerTime) {
      return util.processTime(registerTime);
    },
    // 显示用户信息
    showUserMessages() {
      console.log(this.user.id)
      axios.post("/api/management/showUsers", {managerId: this.user.id})
          .then((response) => {
            console.log(response)
            if (response.data.errcode === 1) {
              this.$message({
                type: 'error',
                message: "您没有权限"
              });
            } else {
              this.userMessages = response.data.users
              // for (let i = 0; i < response.data.users.length; i++) {
              //   console.log(response.data.users[i].auth)
              //   console.log(response.data.users[i].id)
              // }
            }
          })
          .catch((err) => {
            console.error(err);
            this.userMessages = null
          })
    },
    // 打开修改用户权限窗口，并显示当前状态
    openChangeUserAuthorityDialog(item) {
      console.log(item)
      console.log("open change user authority dialog")
      this.userAuthorityDialogMessage = item
      this.selectedAuthority = item.auth
      this.showChangeUserAuthority = true
    },
    // 关闭修改用户权限窗口
    closeChangeUserAuthorityDialog() {
      this.showChangeUserAuthority = false
      console.log("close change user authority dialog")
      this.userAuthorityDialogMessage = ''
      this.selectedAuthority = ''
    },
    // 修改用户权限
    changeAuthority() {
      console.log(this.selectedAuthority)
      let userId = this.userAuthorityDialogMessage.id
      let managerId = this.user.id
      axios.post("/api/management/isProjectAdmin", {
        userId: userId,
        managerId: managerId
      })
          .then((res) => {
            if (res.data.data === 1) {
              this.$message({
                type: 'error',
                message: '该用户参加了项目，无法授权为管理员'
              })
            } else {
              axios.post("/api/management/changeUserAuthority", {
        managerId: managerId,
        userId: userId,
        changeToAuthority: this.selectedAuthority
      })
          .then((response) => {
            this.showChangeUserAuthority = false
            console.log(response.data)
            if (response.data.errcode === 1) {
              this.$message({
                type: 'error',
                message: "您没有该权限"
              });
            } else if (response.data.errcode === 2) {
              let showAuthority;
              if (this.selectedAuthority === 3) {
                showAuthority = "教师"
              } else if (this.selectedAuthority === 2) {
                showAuthority = "助教"
              } else {
                showAuthority = "用户"
              }
              this.$message({
                type: 'info',
                message: "用户" + this.userAuthorityDialogMessage.name + "的角色已为" + showAuthority
              });
            } else {
              if (this.selectedAuthority === 3) {
                this.$message({
                  type: 'success',
                  message: "成功将用户" + this.userAuthorityDialogMessage.name + "的角色修改为教师"
                });
              } else if (this.selectedAuthority === 2) {
                this.$message({
                  type: 'success',
                  message: "成功将用户" + this.userAuthorityDialogMessage.name + "的角色修改为助教"
                });
              } else {
                this.$message({
                  type: 'success',
                  message: "成功将用户" + this.userAuthorityDialogMessage.name + "的角色修改为用户"
                });
              }
            }
            this.userAuthorityDialogMessage = ''
            this.selectedAuthority = ''
            this.showUserMessages()
          })
          .catch((err) => {
            this.showChangeUserAuthority = false
            this.userAuthorityDialogMessage = ''
            this.selectedAuthority = ''
            console.error(err);
          })
            }
          })
    },
    // 打开用户个人信息窗口
    openUserProfileDialog(item) {
      console.log(item)
      this.userProfileDialogMessage = item
      this.showUserProfile = true
    },
    // 关闭用户个人信息窗口
    closeUserProfileDialog(item) {
      this.showUserProfile = false
      this.userProfileDialogMessage = ''
    },
    // 保存用户个人信息的修改
    saveProfile() { // TODO
      this.showUserProfile = false
    },
    // 跳转到用户端页面
    gotoUserPage(item) {
      console.log("232534")
      Cookies.set('manager', Cookies.get('user'))
      console.log(Cookies.get('manager'))
      axios.post("/api/getUserInfo", {
        managerId: this.user.id,
        userId: item.id,
      })
          .then((response) => {
            console.log(response.data)
            if (response.data.errcode === 1) {
              this.$message({
                type: 'error',
                message: "用户不存在"
              });
            } else {
              Cookies.set('user', JSON.stringify(response.data.data))
              this.$message({
                type: 'success',
                message: "跳转成功"
              });
              Cookies.set("from", 0)
              window.location.href = '/manager/assistantAuthority'
            }
          })
          .catch((err) => {
            console.error(err);
          })
    },
    getColor(auth) {
      if (auth === 3) {
        return "green";
      } else if (auth === 2) {
        return "orange";
      } else if (auth === 1) {
        return "blue";
      }
    },
    transform(auth) {
      if (auth === 3) {
        return "教师";
      } else if (auth === 2) {
        return "助教";
      } else if (auth === 1) {
        return "用户";
      }
    },
  },
}
</script>

<style scoped>

</style>