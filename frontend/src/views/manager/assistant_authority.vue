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
        <template #item.userProject="{item}">
<!--          <v-btn class="ml-1" small outlined @click="gotoUserPage(item)">用户所在项目</v-btn>-->
          <v-tooltip bottom>
            <template v-slot:activator="{ on, attrs }">
              <v-btn icon color="blue" v-bind="attrs" v-on="on" @click="openSetAssistProj(item)">
                编辑
              </v-btn>
            </template>
            <span>管理助教负责的项目</span>
          </v-tooltip>
        </template>
      </v-data-table>
    </v-card>

    <v-dialog v-model="showSetAssistProj" width="700">
      <template>
        <v-container class="pa-0">
          <v-card>
            <v-card-title class="headline font-weight text-left"> 编辑助教{{assistantDialogMessage.name}}允许管理的项目 </v-card-title>
            <v-text-field
            v-model="search"
            append-icon="mdi-magnify"
            label="支持按项目名和创建人搜索"
            single-line
            hide-details
            style="margin-left: 10px; "
        ></v-text-field>
            <v-divider></v-divider>
              <v-data-table
              :headers="headers1"
              :items="projectMessages"
              :search="search">
                <template #item.isManage="{item}">
                  <v-chip :color="getColor(item.isManage)" dark @click="changeManageInfo(item)">
                    {{ transform(item.isManage) }}
                  </v-chip>
                </template>

              </v-data-table>

            <v-card-actions>
              <v-spacer></v-spacer>

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
import {windows} from "codemirror/src/util/browser";

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
          text: '助教名',
          align: 'start',
          // sortable: false,
          value: 'name',
        },
        { text: '邮箱', value: 'email' },
        { text: '注册时间', value: 'registerTime' },


        {
          text: '权限设置',
          sortable: false,
          value: 'userProject'
        },
      ],
      headers1: [
        {
          text: '项目名',
          align: 'start',
          value: 'name'
        },
        {
          text: '创建人',
          value: 'leader'
        },

        {
          text: '权限',
          value: 'isManage'
        }
      ],

      userMessages: [],
      projectMessages: [],
      // 重置用户密码dialog相关信息
      showResetPassword: false,
      userResetPasswordDialogMessage: '',
      // 用户状态dialog相关信息
      showChangeUserStatus: false,
      userStatusDialogMessage: '',

      // 用户个人信息dialog相关信息
      showUserProfile: false,
      userProfileDialogMessage: '',
      // 跳转到用户端的相关信息
      gotoUserProjectPageMessage: '',
      // 修改助教管理项目相关
      showSetAssistProj: false,
      assistantDialogMessage: '',
      currentProject: ''
    }
  },
  created() {
    this.showAssistantMessages()
  },

  methods: {
    pro(registerTime) {
      return util.processTime(registerTime);
    },
    // 显示管理员信息
    showAssistantMessages() {
      console.log(this.user.id)
      axios.post("/api/management/showAssistants", {managerId: this.user.id})
          .then((response) => {
            console.log(response)
            if (response.data.errcode === 1) {
              this.$message({
                type: 'error',
                message: "您没有权限"
              });
            } else {
              this.userMessages = response.data.users
            }
          })
          .catch((err) => {
            console.error(err);
            this.userMessages = null
          })
    },

    // 打开重置用户密码窗口
    openResetPasswordDialog(item) {
      this.userResetPasswordDialogMessage = item
      console.log("open reset password dialog")
      console.log(this.userResetPasswordDialogMessage)
      this.showResetPassword = true
    },
    // 关闭重置用户密码窗口
    closeResetPasswordDialog() {
      this.showResetPassword = false
      console.log("close reset password dialog")
      this.userResetPasswordDialogMessage = ''
    },
    openSetAssistProj(item) {
      this.assistantDialogMessage = item
      console.log("open set proj dialog")
      console.log(this.assistantDialogMessage)
      this.showSetAssistProj = true
      this.showProjectMessages(item)
    },
    closeSetAssistProj() {
      this.showSetAssistProj = false
      console.log("close set proj dialog")
      this.assistantDialogMessage = ''
    },
    // 重置用户密码
    resetPassword() {
      let userId = this.userResetPasswordDialogMessage.id
      axios.post("/api/management/resetUserPassword", {managerId: this.user.id, userId: userId})
          .then((response) => {
            console.log(response.data)
            if (response.data.errcode === 1) {
              this.$message({
                type: 'error',
                message: "您没有该权限"
              });
            } else {
              this.$message({
                type: 'success',
                message: "成功将用户" + response.data.name + "的密码修改为" + response.data.resetPassword
              });
            }
          })
          .catch((err) => {
            console.error(err);
          })
      this.showResetPassword = false
      this.userResetPasswordDialogMessage = ''
    },
    // 设置助教管理项目
    changeAssistProj() {
      let assistantId = this.assistantDialogMessage.id
      this.showSetAssistProj = false
      this.assistantDialogMessage = ''
    },
    // 打开修改用户状态窗口，并显示当前状态
    openChangeUserStatusDialog(item) {
      console.log(item)
      console.log("open change user status dialog")
      this.userStatusDialogMessage = item
      this.selectedStatus = item.status
      this.showChangeUserStatus = true
    },
    // 关闭修改用户状态窗口
    closeChangeUserStatusDialog() {
      this.showChangeUserStatus = false
      console.log("close change user status dialog")
      this.userStatusDialogMessage = ''
      this.selectedStatus = ''
    },

    showProjectMessages(item) {
      console.log(this.user.id)
      axios.post("/api/management/showAssistantProjects", {teacherId: this.user.id, assistantId: item.id})
          .then((response) => {
            console.log("errcode is:" + response.data.errcode)
            if (response.data.errcode === 1) {
              window.alert("您没有权限")
            } else if (response.data.errcode === 2) {
              window.alert("该项非助教")
            } else if (response.data.errcode === 3) {
              window.alert("该项是教师")
            } else {
              this.projectMessages = response.data.projects
              console.log(this.projectMessages)
            }
          })
          .catch((err) => {
            console.error(err);
            this.projectMessages = null
          })
    },
    // 修改用户状态
    changeStatus() {
      console.log(this.selectedStatus)
      let userId = this.userStatusDialogMessage.id
      let managerId = this.user.id
      axios.post("/api/management/changeUserStatus", {
        managerId: managerId,
        userId: userId,
        changeToStatus: this.selectedStatus
      })
          .then((response) => {
            this.showChangeUserStatus = false
            console.log(response.data)
            if (response.data.errcode === 1) {
              this.$message({
                type: 'error',
                message: "您没有该权限"
              });
            } else if (response.data.errcode === 2) {
              let showStatus;
              if (this.selectedStatus === 'A') {
                showStatus = "正常"
              } else {
                showStatus = "禁用"
              }
              this.$message({
                type: 'info',
                message: "用户" + this.userStatusDialogMessage.name + "的状态已为" + showStatus
              });
            } else {
              if (this.selectedStatus === 'A') {
                this.$message({
                  type: 'success',
                  message: "成功将用户" + this.userStatusDialogMessage.name + "的状态恢复为正常"
                });
              } else {
                this.$message({
                  type: 'success',
                  message: "成功将用户" + this.userStatusDialogMessage.name + "的状态修改为禁用"
                });
              }
            }
            this.userStatusDialogMessage = ''
            this.selectedStatus = ''
            this.showUserMessages()
          })
          .catch((err) => {
            this.showChangeUserStatus = false
            this.userStatusDialogMessage = ''
            this.selectedStatus = ''
            console.error(err);
          })
    },
    // 打开用户个人信息窗口
    openUserProfileDialog(item) {
      console.log(item)
      this.userProfileDialogMessage = item
      this.showUserProfile = true
    },
    // 关闭用户个人信息窗口
    closeUserProfileDialog() {
      this.showUserProfile = false
      this.userProfileDialogMessage = ''
    },
    // 保存用户个人信息的修改
    saveProfile() { // TODO
      this.showUserProfile = false
    },
    // 跳转到用户端页面

    changeManageInfo(item) {
      console.log("114514")
      console.log(item)
      if (item.isManage === 1) {
        console.log(this.assistantDialogMessage.id)
        console.log(this.user.id)
        axios.post("api/management/removeAssistantProject", {
          managerId: this.user.id,
          userId: this.assistantDialogMessage.id,
          projectId: item.projectId
        }).then((response) => {
          console.log(response.data)
          if (response.data.errcode === 1) {
            this.$message({
              type: 'error',
              message: "您没有权限"
            });
          } else if (response.data.errcode === 2) {
            this.$message({
              type: 'error',
              message: "无需删除"
            });
          } else {
            this.$message({
              type: 'error',
              message: "成功将助教 " + this.assistantDialogMessage.name + " 对项目 " + item.name + " 的权限撤销 "
            })
            console.log("已删除")
          }
        }).catch((err) => {
          console.error(err);
        })
      } else {
        console.log(this.assistantDialogMessage.id)
        console.log(this.user.id)
        axios.post("api/management/addAssistantProject", {
          managerId: this.user.id,
          userId: this.assistantDialogMessage.id,
          projectId: item.projectId
        }).then((response) => {
          console.log(response.data.errcode)
          if (response.data.errcode === 1) {
            this.$message({
              type: 'error',
              message: "您没有权限"
            });
          } else if (response.data.errcode === 2) {
            this.$message({
              type: 'error',
              message: "无需添加"
            });
          } else {
            this.$message({
              type: 'success',
              message: "成功将 " + item.name + " 分配给助教 " + this.assistantDialogMessage.name + " 管理 "
            })
            console.log("已添加")
          }
        }).catch((err) => {
          console.error(err);
        })
      }
      this.showSetAssistProj = false;

    },
    getColor(isManage) {
      if (isManage === 0) {
        return "red";
      } else if (isManage === 1) {
        return "green";
      }
    },
    transform(isManage) {
      if (isManage === 0) {
        return "OFF"
      } else if (isManage === 1) {
        return "ON"
      }
    },
  },
}
</script>

<style scoped>

</style>