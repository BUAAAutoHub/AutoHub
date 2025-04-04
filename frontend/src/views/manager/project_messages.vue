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
          :items="projectMessages"
          :search="search"
      >
        <template #item.access="{item}">
          <v-chip :color="getColor(item.access)" dark @click="openChangeProjectAccessDialog(item)">
            {{ transform(item.access) }}
<!--            <v-text v-if="item.access==='A'"> 正常 </v-text>-->
<!--            <v-text v-if="item.access==='B'"> 禁用 </v-text>-->
          </v-chip>
        </template>

<!--        <template #item.progress="{item}">-->
<!--          {{ item.progress }} %-->
<!--        </template>-->
<!--        <template #item.changeAccess="{item}">-->
<!--          <v-btn class="ml-1" small outlined @click="openChangeProjectAccessDialog(item)">修改项目状态</v-btn>-->
<!--        </template>-->
        <template #item.projectDetail="{item}">
          <v-tooltip bottom>
            <template v-slot:activator="{ on, attrs }">
              <v-btn icon color="blue" v-bind="attrs" v-on="on" @click="gotoProjectDetailPage(item)">
                <v-icon>mdi-link-variant</v-icon>
              </v-btn>
            </template>
            <span>以项目负责人身份进入用户端的项目界面</span>
          </v-tooltip>
        </template>
<!--        <template #item.projectDetail="{item}">-->
<!--          <v-btn class="ml-1" small outlined @click="gotoProjectDetailPage(item)">项目详细信息</v-btn>-->
<!--        </template>-->
        <template #item.createTime="{item}">
          {{ pro(item.createTime) }}
        </template>
      </v-data-table>
    </v-card>
    <v-dialog v-model="showChangeProjectAccess" width="300">
      <template>
        <v-container class="pa-0">
          <v-card>
            <v-card-title class="headline font-weight text-left"> 修改项目状态 </v-card-title>
            <v-card-text> 项目名:{{ changeProjectAccessMessage.name }} / 创建人:{{ changeProjectAccessMessage.leader }}</v-card-text>
            <v-divider></v-divider>
            <v-card-text>
              <v-radio-group v-model="selectedAccess">
                <v-radio v-for="i in accessList" :key="i.value" :label="i.label" :value="i.value"></v-radio>
              </v-radio-group>
            </v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn color="red" text @click="closeChangeProjectAccessDialog">取消</v-btn>
              <v-btn color="blue" text @click="changeAccess">确认修改</v-btn>
            </v-card-actions>
          </v-card>
        </v-container>
      </template>
    </v-dialog>
  </v-container>
</template>

<script>
import axios from "axios";
import util from "@/views/util";
import Cookies from "js-cookie";

export default {
  inject: {
    user: { default: null },
    getProj: { default: null },
    //setFrom: { default: null }
  },
  data () {
    return {
      search: '',
      headers: [
        {
          text: '项目名',
          align: 'start',
          // sortable: false,
          value: 'name',
        },
        { text: '创建人', value: 'leader' },
        { text: '创建人邮箱', value: 'email' },
        { text: '创建时间', value: 'createTime' },
        // { text: '完成进度', value: 'progress' },
        { text: '状态', value: 'access' },
        {
          text: '',
          sortable: false,
          value: 'changeAccess'
        },
        {
          text: '',
          sortable: false,
          value: 'projectDetail'
        },
      ],
      projectMessages: [
        // {
        //   name: 'project1',
        //   projectId: 0,
        //   leader: '123',
        //   leaderId: 1,
        //   email: '123@qq.com',
        //   createTime: '2023.1.1',
        //   progress: 80,
        //   status: 'A',
        //   access: 'A',
        // },
        // {
        //   name: 'faskfl',
        //   projectId: 1,
        //   leader: '432gsdf',
        //   leaderId: 2,
        //   email: 'gers@qq.com',
        //   createTime: '2023.2.1',
        //   progress: '60',
        //   status: 'B',
        //   access: 'A',
        // },
        // {
        //   name: 'project3',
        //   projectId: 2,
        //   leader: '435',
        //   leaderId: 1,
        //   email: '53@qq.com',
        //   createTime: '2023.3.1',
        //   progress: '100',
        //   status: 'A',
        //   access: 'A'
        // },
      ],
      showChangeProjectAccess: false,
      changeProjectAccessMessage: '',
      selectedAccess: '',
      accessList: [
        {
          label: '正常',
          value: 'A'
        },
        {
          label: '禁用',
          value: 'B'
        },
      ],
    }
  },
  created() {
    this.showProjectMessages()
  },
  // TODO：传给后端管理员id，如果报错，不显示信息而显示弹窗
  methods: {
    pro(createTime) {
      return util.processTime(createTime);
    },
    // 显示项目信息
    showProjectMessages() {
      console.log(this.user.id)
      axios.post("/api/management/showAllProjects", {managerId: this.user.id})
          .then((response) => {
            console.log(response)
            if (response.data.errcode === 1) {
              window.alert("您没有权限")
            } else {
              this.projectMessages = response.data.projects
            }
          })
          .catch((err) => {
            console.error(err);
            this.projectMessages = null
          })
    },
    // 打开修改项目状态窗口，并显示当前状态
    openChangeProjectAccessDialog(item) {
      console.log(item)
      this.changeProjectAccessMessage = item
      this.selectedAccess = item.access
      this.showChangeProjectAccess = true
    },
    // 关闭修改项目状态窗口
    closeChangeProjectAccessDialog() {
      this.showChangeProjectAccess = false
    },
    // 修改项目状态
    changeAccess() {
      console.log(this.selectedAccess)
      let projectId = this.changeProjectAccessMessage.projectId
      let managerId = this.user.id
      axios.post("/api/management/changeProjectAccess", {
        managerId: managerId,
        projectId: projectId,
        changeToAccess: this.selectedAccess
      })
          .then((response) => {
            this.showChangeProjectAccess = false
            console.log(response.data)
            if (response.data.errcode === 1) {
              this.$message({
                type: 'error',
                message: "您没有权限"
              });
            } else if (response.data.errcode === 2) {
              let showAccess;
              if (this.selectedAccess === 'A') {
                showAccess = "正常"
              } else {
                showAccess = "禁用"
              }
              this.$message({
                type: 'success',
                message: "项目" + this.changeProjectAccessMessage.name + "的状态已为" + showAccess
              });
            } else {
              if (this.selectedAccess === 'A') {
                this.$message({
                  type: 'success',
                  message: "成功将项目" + this.changeProjectAccessMessage.name + "的状态恢复为正常"
                });
              } else {
                this.$message({
                  type: 'success',
                  message: "成功将项目" + this.changeProjectAccessMessage.name + "的状态修改为禁用"
                });
              }
              this.showProjectMessages()
            }
            this.changeProjectAccessMessage = ''
            this.selectedAccess = ''
          })
          .catch((err) => {
            this.showChangeProjectAccess = false
            this.changeProjectAccessMessage = ''
            this.selectedAccess = ''
            console.error(err);
          })
    },
    // 跳转到项目详情页面
    gotoProjectDetailPage(item) {
      console.log("232534")
      Cookies.set('manager', Cookies.get('user'))
      console.log(Cookies.get('manager'))
      console.log(item.projectId)
      console.log(item.leaderId)
      axios.post("/api/getUserInfo", {
        managerId: this.user.id,
        userId: item.leaderId,
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
            }
          })
          .catch((err) => {
            console.error(err);
          })
      axios.post("/api/plan/ProjectInfo", {
        projectId: item.projectId,
      })
          .then((response) => {
            console.log(response.data)
            if (response.data.errcode === 1) {
              this.$message({
                type: 'error',
                message: "项目不存在"
              });
            } else if (response.data.errcode === 3) {
              this.$message({
                type: 'error',
                message: "您不具有该权限"
              });
            } else {
              console.log(response.data.data)
              this.$message({
                type: 'success',
                message: "跳转成功"
              });
              Cookies.set("from", 1)
              this.getProj(response.data.data)
              // window.location.href = '/allProject'
            }
          })
          .catch((err) => {
            console.error(err);
          })
    },
    getColor(access) {
      if (access === "A") {
        return "green";
      } else if (access === "B") {
        return "red";
      }
    },
    transform(access) {
      if (access === "A") {
        return "正常";
      } else if (access === "B") {
        return "禁用";
      }
    },
  },
}
</script>

<style scoped>

</style>