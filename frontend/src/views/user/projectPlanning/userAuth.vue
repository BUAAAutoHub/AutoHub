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
        <template #item.peopleJob="{item}">
          <v-chip :color="getColor(item.peopleJob)" dark>
            {{ transform(item.peopleJob) }}
<!--            <v-text v-if="item.status==='A'"> 正常 </v-text>-->
<!--            <v-text v-if="item.status==='B'"> 禁用 </v-text>-->
          </v-chip>
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
              <v-btn icon color="blue" v-bind="attrs" v-on="on" @click="changeUserAuth(item)">
                编辑
              </v-btn>
            </template>
            <span>管理该成员权限</span>
          </v-tooltip>
        </template>
      </v-data-table>
    </v-card>

    <v-dialog v-model="showChangeUserAuth" width="300">
      <template>
        <v-container class="pa-0">
          <v-card>
            <v-card-title class="headline font-weight text-left"> 修改 {{curUserName}} 对项目的权限 </v-card-title>
            <v-divider></v-divider>
            <div style="margin-top: 20px"></div>
            <p style="margin-left: 50px">提交权限<el-switch
                v-model="curCommitAuth"
                active-color="#13ce66"
                inactive-color="#ff4949"
                style="margin-left: 70px">
              </el-switch></p>
              <p style="margin-left: 50px">编辑权限<el-switch
                v-model="curEditAuth"
                active-color="#13ce66"
                inactive-color="#ff4949"
                style="margin-left: 70px">
              </el-switch>
              </p>
             <p style="margin-left: 50px">查看权限<el-switch
                v-model="curViewAuth"
                active-color="#13ce66"
                inactive-color="#ff4949"
                style="margin-left: 70px">
              </el-switch>
             </p>

              <v-card-actions>
                <v-spacer></v-spacer>
                  <v-btn color="red" text @click="closeChangeUserAuthDialog()">取消</v-btn>
                <v-btn color="blue" text @click="changeAuth()">确认</v-btn>
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
    selectedProj: {default: null}
    //setFrom: { default: null}
  },
  data () {
    return {
      msg: null,
      search: '',
      value: '',
      options: {
        pagination: false
      },
      headers: [
        {
          text: '用户名',
          align: 'start',
          // sortable: false,
          value: 'peopleName',
        },
        { text: '邮箱', value: 'peopleEmail' },
        { text: '角色', value: 'peopleJob' },
        // {
        //   text: '',
        //   sortable: false,
        //   value: 'changeStatus'
        // },
        {
          text: '管理',
          sortable: false,
          value: 'userProject'
        },
      ],
      headers1: [
        {
          text: '提交权限',
          align: 'start',
          value: 'commitAuth'
        },
        {
          text: '编辑权限',
          value: 'editAuth'
        },
        {
          text: '查看权限',
          value: 'viewAuth'
        }
      ],
      userMessages: [
        // {
        //   name: 'user1',
        //   id: '1',
        //   email: '123@qq.com',
        //   registerTime: '2023.1.1',
        //   status: 'A',
        // },
        // {
        //   name: 'faskfl',
        //   id: '2',
        //   email: 'gers@qq.com',
        //   registerTime: '2023.2.1',
        //   status: 'B',
        // },
        // {
        //   name: 'saga',
        //   id: '3',
        //   email: '53@qq.com',
        //   registerTime: '2023.3.1',
        //   status: 'A',
        // },
      ],
      authMessages: '',
      curCommitAuth: false,
      curEditAuth: false,
      curViewAuth: false,
      curUserId: '',
      curUserName: '',
      // 重置用户密码dialog相关信息
      // 用户状态dialog相关信息
      showChangeUserAuth: false,
      userStatusDialogMessage: '',
      selectedStatus: '',
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

  methods: {
    // 显示用户信息
    showUserMessages() {
      console.log(this.selectedProj.projectId)
      axios.post("/api/plan/showPersonList", {
        projectId: this.selectedProj.projectId,
        userId: this.user.id})
          .then((response) => {
            console.log(response)
            if (response.data.errcode === 1) {
              this.$message({
                type: 'error',
                message: "项目不存在"
              });
            } else {
              this.userMessages = response.data.data
              console.log(this.userMessages)
            }
          })
          .catch((err) => {
            console.error(err);
            this.userMessages = null
          })
    },
    getUserAuthList(item) {
      this.curUserId = item.peopleId
      this.curUserName = item.peopleName
      console.log("11111")
      console.log(this.user.id)
      console.log(this.selectedProj.managerId)
      axios.post("api/plan/getUserProjectAuths", {
        projectId: this.selectedProj.projectId,
        personId: item.peopleId,
        userId: this.user.id
      })
          .then((response) => {
            console.log(response)
            if (response.data.errcode === 1) {
              this.$message({
                type: 'error',
                message: "您没有权限"
              })
            } else if (response.data.errcode === 2) {
              this.$message({
                type: 'error',
                message: "项目不存在"
              })
            } else if (response.data.errcode === 3) {
              this.$message({
                type: 'error',
                message: '找不到当前用户'
              })
            } else {
              this.curCommitAuth = response.data.data.commitAuth === 'Y'
              this.curEditAuth = response.data.data.editAuth === 'Y'
              this.curViewAuth = response.data.data.viewAuth === 'Y'
            }
          })
    },
    changeUserAuth(item) {
      this.showChangeUserAuth = true
      this.getUserAuthList(item)
      this.curCommitAuth = false
      this.curEditAuth = false
      this.curViewAuth = false
    },
    closeChangeUserAuthDialog() {
      this.showChangeUserAuth = false
      this.authMessages = ''
      this.curCommitAuth = false
      this.curEditAuth = false
      this.curViewAuth = false
      this.curUserName = ''
      this.curUserId = ''
    },
    changeAuth() {
      console.log("112312413124")
      let changedCommitAuth = this.curCommitAuth ? 'Y' : "N"
      let changedEditAuth = this.curEditAuth ? 'Y' : 'N'
      let changedViewAuth = this.curViewAuth ? 'Y' : 'N'
      axios.post("api/plan/changeUserProjectAuths", {
        projectId: this.selectedProj.projectId,
        personId: this.curUserId,
        userId: this.user.id,
        changeToCommitAuth: changedCommitAuth,
        changeToEditAuth: changedEditAuth,
        changeToViewAuth: changedViewAuth
      })
          .then(() => {
            this.$message({
              type: 'success',
              message: '修改权限成功'
            })
          })
      this.showChangeUserAuth = false
      this.curCommitAuth = ''
      this.curViewAuth = ''
      this.curEditAuth = ''
      this.curUserId = ''
    },
    getColor(role) {
      if (role === 'A') {
        return 'orange';
      } else if (role === 'B') {
        return 'green';
      } else if (role === 'C') {
        return 'blue';
      } else if (role === 'D') {
        return 'purple';
      }
    },
    transform(role) {
      if (role === 'A') {
        return '开发人员'
      } else if (role === 'B') {
        return '管理员'
      } else if (role === 'C') {
        return '负责人'
      } else if (role === 'D') {
        return '审核人员'
      }
    },
    authColor(auth) {
      if (auth === 'Y') {
        return 'red'
      } else if (auth === 'N') {
        return 'green'
      }
    },
    authTransform(auth) {
      if (auth === 'Y') {
        return 'OFF'
      } else if (auth === 'N') {
        return 'ON'
      }
    },
  }
}
</script>

<style scoped>

</style>