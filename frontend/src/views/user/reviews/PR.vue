<script>
  import axios from "axios";
  import topicSetting from "@/utils/topic-setting";
  import {marked} from "marked";
  import getIdenticon from "@/utils/identicon";
  export default {
    components: {
      marked
    },
    created() {
      this.prId = this.$route.query.prId
      this.projId = this.$route.query.projId
      this.repoId = this.$route.query.repoId
      console.log(this.prId)
      console.log(this.projId)
      console.log(this.repoId)
      this.getPrDetail();
      this.getTaskList();
      this.getAssociatedTaskList();
      this.getUserRole();
      this.updateReviewers()
    },
    inject: {
      user: {default: null},
    },
    data() {
      return{
        prId: '',
        projId: '',
        repoId: '',
        getPrDetailBusy: true,
        prDetail: [],
        commits: [],
        taskDialogOpen: false,
        tasks: [],
        headers: [
          {
            text: '任务编号',
            align: 'start',
            value: 'taskId'
          },
          {
            text: '任务名称',
            value: 'taskName'
          },

          {
            text: '',
            value: 'isManage'
          }
        ],
        isProjectReviewer: false,
        reviewStatus: '',
        associatedTasks: [],
        body: '',
        reviewers: [],
        selectForm: {
          prId: '',
          projectId:'',
          reviewerId: '',
          sha:'',
          visible: false,
        },
      }
    },
    methods: {
      marked() {
        return marked
      },
      getDarkColor: topicSetting.getDarkColor,
      selectReviewer() {
        this.selectForm.prId = this.prId
        this.selectForm.visible = true;
      },
      updateReviewers() {
        axios.post('/api/plan/showProjectReviewers', {
          userId: this.user.id,
          projectId: this.projId,
        }).then((res) => {
          if (res.data.errcode === 0) {
            this.reviewers = res.data.data
          } else {
            console.log(res)
            this.isReviewer = false
          }
        }).catch((err) => {
          alert('/api/plan/showProjectReviewers error' + err)
        })
      },
      submitForm() {
        axios.post('/api/develop/assignPrReviewer', {
          userId: this.user.id,
          projectId: this.projId,
          prId: this.prId,
          repoId: this.repoId,
          reviewerId: this.selectForm.reviewerId
        }).then((res) => {
          if (res.data.errcode === 0) {
            this.$message({
              type: 'success',
              message: '成功分配审核人员'
            })
            this.selectForm.visible = false;
            this.selectForm.reviewerId = undefined;
            location.reload()
          } else {
            console.log(res)
            alert('/api/plan/showProjectReviewers error with not 0 err code (' + res.data.errcode + ') ' + res.data.message)
          }
        }).catch((err) => {
          alert('/api/plan/showProjectReviewers error' + err)
        })
      },
    getIdenticon,
      getUserRole() {
        axios.post("api/develop/isProjectReviewer", {
          userId: this.user.id,
          projectId: this.projId
        })
            .then((res) => {
              if (res.data.errcode !== 0) {
                console.log(res.data)
              } else {
                this.isProjectReviewer = true
              }
            })
      },
      addTask(task) {
        axios.post("api/develop/associatePrTask", {
          userId: this.user.id,
          projectId: this.projId,
          repoId: this.repoId,
          prId: this.prId,
          taskId: task.taskId
        })
            .then((res) => {
              if (res.data.errcode === 9) {
                console.log(res.data)
                this.$message({
                  type: 'error',
                  message: '当前任务已经被绑定，不可重复操作'
                })
              } else if (res.data.errcode === 8) {
                this.$message({
                  type: 'error',
                  message: '当前任务已被完成，不可关联'
                })
              } else if (res.data.errcode === 7) {
                this.$message({
                  type: 'error',
                  message: '此任务不存在此项目中'
                })
              } else {
                this.associatedTasks.push({taskId: task.taskId, taskName: task.taskName})
                this.$message({
                  type: 'success',
                  message: '绑定任务项成功！'
                })
              }
            })
      },
      removeTask(task) {
        axios.post("api/develop/deletePrTask", {
          userId: this.user.id,
          projectId: this.projId,
          repoId: this.repoId,
          prId: this.prId,
          taskId: task.taskId
        })
            .then((res) => {
              if (res.data.errcode === 8) {
                console.log(res.data)
                this.$message({
                  type: 'error',
                  message: 'PR已完成，无法解除关联'
                })
              } else {
                for (let i = 0; i < this.associatedTasks.length; i++) {
                  if (task.taskId === this.associatedTasks.at(i).taskId) {
                    this.associatedTasks.splice(i, 1)
                    break;
                  }
                }
                this.$message({
                  type: 'success',
                  message: '解除关联成功'
                })
              }
            })
      },
      getPrDetail() {
        axios.post("api/develop/getPrDetails", {
          userId: this.user.id,
          projectId: this.projId,
          repoId: this.repoId,
          prId: this.prId
        })
            .then((res) => {
              if (res.data.errcode !== 0) {
                console.log("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                this.$message({
                  type: 'error',
                  message: '获取pr详情失败，错误码为' + res.data.errcode
                })
                this.getPrDetailBusy = false
              } else {
                this.prDetail = res.data.data
                this.commits = res.data.data.commits
                console.log(this.prDetail)
                this.reviewStatus = this.prDetail.state
                this.body = res.data.data.body
                this.getPrDetailBusy = false
              }
            })
        console.log(this.prDetail)
      },
      getTaskList() {
        axios.post("api/develop/showCanAssociateTasks", {
          projectId: this.projId
        })
            .then((res) => {
              if (res.data.errcode === 0) {
                this.tasks = res.data.data
              }
            })
      },
      getAssociatedTaskList() {
        axios.post("api/develop/getPrAssociatedTasks", {
          prId: this.prId,
          repoId: this.repoId
        })
            .then((res) => {
              if (res.data.errcode !== 0) {
                console.log(res.data)
                this.$message({
                  type: 'error',
                  message: '获取已绑定任务失败'
                })
              } else {
                this.associatedTasks = res.data.data
              }
            })
      },
      checkCommit(commit) {
        console.log(commit)
        this.$router.push({
          path: '/commitReview/' + this.projId + '/' + this.repoId + '/' + this.prDetail.branch + '/' + commit.sha + "?branchName=" + this.prDetail.branch + "&projId=" + this.projId + "&repoId=" + this.repoId + "&commitSha=" + commit.sha,
          query: {
            commit: commit,
            branchName: this.prDetail.branch,
            projId: this.projId,
            repoId: this.repoId
          }
        })
      },
      reviewPr(result) {
        axios.post("api/develop/resolvePr", {
          userId: this.user.id,
          prId: this.prId,
          projectId: this.projId,
          repoId: this.repoId,
          action: result
        })
            .then((res) => {
              console.log(res.data)
              if (res.data.errcode === -1) {
                this.$message({
                  type: 'error',
                  message: '两分支上有冲突，请在本地解决冲突后再通过PR'
                })
              } else if (res.data.errcode !== 0) {
                this.$message({
                  type: 'error',
                  message: '发生错误，审核失败'
                })
              } else {
                this.$message({
                  type: 'success',
                  message: '审核成功'
                })
                this.reviewStatus = result === 1 ? 'merged' : 'closed'
              }
            })
      },
      openTaskDialog() {
        this.taskDialogOpen = true
        console.log(this.taskDialogOpen)
      },
      goBack() {
        this.prDetail = []
        this.tasks = []
        this.reviewStatus = ''
        this.associatedTasks = ''
        this.$router.go(-1)
      },
      getColor(status) {
        if (status === 'open') {
          return "blue";
        } else if (status === 'closed') {
          return "red"
        } else if (status === 'merged') {
          return "green"
        } else {
          return "purple"
        }
      },
      transform(status) {
        if (status === 'open') {
          return "未审核";
        } else if (status === 'closed') {
          return "已拒绝"
        } else if (status === 'merged') {
          return "已合并"
        } else {
          return "未知状态"
        }
      },
    }
  }
</script>

<template>
<div style="margin: 15px">
  <el-page-header @back="goBack" content="PR评审" style="margin-top: 40px"></el-page-header>
  <h1 style="margin-top: 20px; margin-left: 20px"><v-chip label >!{{this.prId}}</v-chip>  {{this.prDetail.title}}</h1>

  <div style="margin: 10px 0 0 20px">
    <div>
      <div v-if="!this.prDetail.reviewerName && isProjectReviewer" style="margin-top: 10px; margin-bottom: 10px">
        <el-button type="primary" style="color: white" @click="this.selectReviewer" v-if="this.reviewers.length > 0">+分配审核人员</el-button>
        <el-button type="primary" style="color: white" @click="this.selectReviewer" v-else disabled>+分配审核人员</el-button>
      </div>
        <div v-else-if="this.prDetail.reviewerName" style="margin-top: 10px; margin-bottom: 10px"> 该项目审核人员：{{this.prDetail.reviewerName}} </div>
        <div v-else style="margin-top: 10px; margin-bottom: 10px"> 该项目暂未分配审核人员 </div>
    </div>
    <v-chip :color="getColor(reviewStatus)" dark small label v-if="!getPrDetailBusy">
      <v-icon small>mdi-source-pull</v-icon>{{ transform(reviewStatus) }}
    </v-chip>
    <v-chip v-else dark small label>
        <v-icon small>mdi-source-pull</v-icon>加载中
    </v-chip>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>{{this.prDetail.pr_applicant}}</b>
    <span style="color: grey">&nbsp;&nbsp;创建于：{{this.prDetail.created_time.slice(0,10)}} {{this.prDetail.created_time.slice(11,-1)}}
      <v-chip label small style="margin-left: 10px"> {{prDetail.branch}}</v-chip> → <v-chip label small>{{prDetail.base}}</v-chip>
      <el-button style="margin-left: 85%; margin-top: -40000px; color: white" type="success" @click="this.openTaskDialog"  v-if="this.isProjectReviewer === true && this.prDetail.state === 'open'">
        +关联任务项
      </el-button>
    </span>
    <div style="display: inline-block; margin-top: -20px; padding: -20px; margin-bottom: -20px"  v-if="this.isProjectReviewer === true && this.prDetail.state === 'open'">
      <v-chip :color="'green'" dark style="margin-right: 30px" @click="reviewPr(1)">
        同意
      </v-chip>
      <v-chip :color="'red'" dark @click="reviewPr(0)">
        拒绝
      </v-chip>
    </div>
    <div style="margin: 10px 0 0 0">
      <v-card style="margin-top: 30px">
        <div v-if="reviewStatus === 'open'">
          <h4 style="color: red; padding: 30px">
            <v-icon style="color:red">mdi-close-circle-outline</v-icon>当前尚有未通过的审查/测试
          </h4>
          <div style="padding: 0 0 30px 70px ">
            至少需要1名审查人员后才能合并， 已通过审查人数 0 人
          </div>
        </div>
        <div v-else-if="reviewStatus === 'merged'">
          <h4 style="color: green; padding: 30px">
            <v-icon style="color:green">mdi-check-circle-outline</v-icon>当前的pr请求已经通过
          </h4>
        </div>
      </v-card>
      <v-card style="margin-top: 20px">
        <h4 style="padding: 20px">
            PR描述
          </h4>
          <div style="padding: 0 0 20px 60px ">
            <div v-html="this.body"></div>
          </div>
      </v-card>


      <div style="margin-top: 20px">
        <b style="font-size: 0.6cm">提交记录 ({{this.commits.length}})</b><span style="color: rgb(128,128,128); font-size: 0.4cm">&nbsp;*您可以点击表项跳转到相应commit</span>
      </div>
      <v-row>
        <v-col cols="8">
          <v-simple-table dense style="margin-top: 20px" v-if="this.commits.length > 0 && !getPrDetailBusy">
            <thead>
            <tr>
              <th class="title">committer</th>
              <th class="title">sha</th>
              <th class="title">time</th>
            </tr>
            </thead>
            <tbody>
            <tr v-for="commit in commits" :key="commit.sha" @click="checkCommit(commit)">
              <td class="need-mono">{{commit.author}}</td>
              <td class="need-mono">
                <v-tooltip bottom>
                      <template v-slot:activator="{on, attrs}">
                        <span v-bind="attrs" v-on="on"><v-chip small label>{{commit.sha.slice(0,6)}}</v-chip></span>
                      </template>
                      <span>{{commit.sha}}</span>
                  </v-tooltip>
              </td>
              <td>{{commit.time.slice(0, 10)}} {{commit.time.slice(11, -1)}}</td>
            </tr>
            </tbody>
          </v-simple-table>
          <el-empty :image-size="200" description="当前仓库中没有pr记录" v-else-if="!getPrDetailBusy"></el-empty>
          <v-skeleton-loader v-else type="table" class="mx-auto" />
        </v-col>

        <v-divider vertical></v-divider>

        <v-col cols="4">
          <v-card><h3 style="padding: 10px">已关联任务项({{this.associatedTasks.length}})</h3>
            <div style="margin-left: 30px;margin-top: 10px">
               <v-data-table
              :headers="headers"
              :items="associatedTasks">
                <template v-slot:item="{item}">
                  <tr>
                    <td style="max-width: 50px; overflow: hidden; text-overflow: ellipsis;"><v-chip small label>{{item.taskId}}</v-chip></td>
                    <td style="max-width: 150px; overflow: hidden; text-overflow: ellipsis;">{{item.taskName}}</td>
                    <td><v-chip :color="'red'" dark @click="removeTask(item)">
                    -
                  </v-chip></td>
                  </tr>
                </template>

              </v-data-table>
            </div>
          </v-card>
        </v-col>
      </v-row>
    </div>
  </div>

  <v-dialog v-model="taskDialogOpen" width="700">
    <template>
      <v-container class="pa-0">
        <v-card>
          <v-card-title class="headline font-weight text-left">关联任务项到当前 Pull Request 请求</v-card-title>
          <v-data-table
              :headers="headers"
              :items="tasks">
                <template #item.isManage="{item}">
                  <v-chip :color="'green'" dark @click="addTask(item)">
                    +
                  </v-chip>
                </template>

              </v-data-table>
        </v-card>
      </v-container>
    </template>
  </v-dialog>

  <el-dialog title="分配审核人员" :visible.sync="selectForm.visible" width="40%">
      <el-form :model="selectForm" ref="form" label-width="140px">
        <el-form-item>
          <el-radio-group v-model="selectForm.reviewerId">
            <div style="display: flex; align-items: center;">
            <el-radio v-for="item in reviewers" :label="item.userId" :key="item.userId">
              <div style="display: flex; align-items: center;">
                  <img :src="getIdenticon(item.userName, 50, 'user')" alt="User Avatar"
                    style="width: 50px; height: 50px; border-radius: 50%; margin-right: 10px;">
                  <span>{{ item.userName }}</span>
                </div>
            </el-radio>
            </div>
          </el-radio-group> </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="submitForm" style="color: white">提交</el-button>
          </el-form-item>
      </el-form>
    </el-dialog>
</div>
</template>

<style scoped>

</style>