<script>
import axios from "axios";
import topicSetting from "@/utils/topic-setting";
import commit from "../views/user/reviews/Commit.vue";
import getIdenticon from "@/utils/identicon";

export default {
  name: "review_commit_view",
  computed: {
    commit() {
      return commit
    }
  },
  data() {
    return {
      commitHistoryBusy: true,
      commitHistory: [
        {

        }
      ],
      commitStatus:[

      ],
      statsPerDay: {},
      tempReviewerName: '',
      selectForm: {
        prId: '',
        projectId:'',
        reviewerId: '',
        sha:'',
        visible: false,
      },
      reviewers: [],
      isReviewer: true
    }
  },
  methods: {
    updateReviewers() {
      axios.post('/api/plan/showProjectReviewers', {
        userId: this.user.id,
        projectId: this.proj.id,
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
    checkFresh() {
      axios.post("api/develop/checkRefreshRepo", {
        userId: this.user.id,
        projectId: this.proj.id,
        repoId: this.selectedRepo.id
      })
          .then((res) => {
            console.log(res.data)
            if (res.data.needRefresh === 1) {
              this.$message({
                type: 'warning',
                message: '请等待当前页面数据更新'
              })
              this.fresh()
            }
          })
    },
    fresh() {
      axios.post("/api/develop/refreshRepo", {
        userId: this.user.id,
        projectId: this.proj.id,
        repoId: this.selectedRepo.id
      })
    },
      updateCommitHistory() {
          this.commitHistoryBusy = true
          axios.post('/api/develop/getCommitHistory', {
            userId: this.user.id,
            projectId: this.proj.id,
            repoId: this.selectedRepo.id,
            branchName: this.selectedBranch.name
          }).then((res) => {
              if (res.data.errcode === 0) {

                  let today = new Date()

                  // get past 10 days
                  let statsPerDay = {}
                  for (let i = 0; i < 10; i++) {
                      let str = (today.getMonth() + 1) + '.' + today.getDate()
                      statsPerDay[str] = 0
                      today.setDate(today.getDate() - 1)
                  }

                  // this.commitHistory = res.data.data.map((cur, index) => {
                  //     let time = new Date(cur.commitTime)
                  //     let str = (time.getMonth() + 1) + '.' + time.getDate()
                  //     if (str in statsPerDay)
                  //         statsPerDay[str] += 1
                  //     return {
                  //         id: index,
                  //         committer: cur.author,
                  //         committerEmail: cur.authorEmail,
                  //         hash: cur.commithash,
                  //         message: cur.commitMessage,
                  //         time: cur.commitTime,
                  //         status: cur.status
                  //     }
                  // })
                this.commitHistory = res.data.data
                  this.commitHistoryBusy = false

                  this.statsPerDay = {
                      label: Object.keys(statsPerDay).reverse(),
                      value: Object.values(statsPerDay).reverse()
                  }
              } else {
                  console.log(res)
                  alert('/api/reviews/getCommitHistory error with not 0 err code (' + res.data.errcode + ') ' + res.data.message)
                  this.commitHistoryBusy = false
              }
          }).catch((err) => {
              alert('/api/reviews/getBindRepos error' + err)
              this.commitHistoryBusy = false
          })
      },
      getTopicColor: topicSetting.getColor,
      getDarkColor: topicSetting.getDarkColor,
      reviewSelectedCommit(commit) {
        console.log(commit)
        this.$router.push({
          path: '/commitReview/' + this.proj.id + '/' + this.selectedRepo.id + '/' + this.selectedBranch.name + '/' + commit.commithash,
          query: {
            branchName: this.selectedBranch.name,
            projId: this.proj.id,
            repoId: this.selectedRepo.id,
            commitSha: commit.commithash
          }
        })
      },
      getColor(status) {
        if (status === null) {
          return "blue";
        } else if (status === 'Y') {
          return "green";
        } else if (status === 'N') {
          return "red"
        }
      },
      transform(status) {
        if (status === null) {
          return "待审核";
        } else if (status === 'Y') {
          return "审核通过";
        } else if (status === 'N') {
          return "审核未通过"
        }
      },
      selectReviewer(commit) {
      console.log(this.commitHistory)
      console.log
      this.selectForm.sha = commit.commithash;
      this.selectForm.visible = true;
      console.log(commit.reviewerName)
    },
    submitForm() {
      axios.post('/api/develop/assignCommitReviewer', {
        userId: this.user.id,
        projectId: this.proj.id,
        repoId: this.selectedRepo.id,
        reviewerId: this.selectForm.reviewerId,
        sha:this.selectForm.sha,
        branch: this.selectedBranch.name
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
          alert('/api/plan/assignCommitReviewer error with not 0 err code (' + res.data.errcode + ') ' + res.data.message)
        }
      }).catch((err) => {
        alert('/api/plan/assignCommitReviewer error' + err)
      })
    },
    getIdenticon,
  },
   watch: {
    selectedBranch() {
        this.updateCommitHistory()
    }
  }, created() {
        this.checkFresh()
        this.updateCommitHistory()
        this.updateReviewers();

  }, inject: {
    user: {default: null},
    proj: {default: null},
    selectedRepo: {default: null},
    selectedBranch: {default: null}
  }
}
</script>

<template>
<div>
<v-card-title>分支<span class="need-mono"> “{{ selectedBranch.name }}” </span>上的提交记录</v-card-title>

  <p v-if="!commitHistoryBusy" style="margin-left: 15px">分支<span class="need-mono"> “{{selectedBranch.name}}” </span>中有 {{ commitHistory.length }} 条提交记录，请选择要查看的commit：</p>
  <p v-else>正在与服务器同步分支{{selectedBranch.name}}上的最新提交记录...</p>
  <div v-if="!commitHistoryBusy">
      <v-simple-table dense>
          <thead>
          <tr>
              <th class="committer">committer</th>
              <th class="message">message</th>
              <th class="status">status</th>
              <th class="hash">hash</th>
              <th class="time">time</th>
              <th class="reviewer">审核人员</th>
          </tr>
          </thead>
          <tbody>
          <tr v-for="commit in commitHistory.slice(0)" :key="commit.id" @click="reviewSelectedCommit(commit)">
              <td class="need-mono">{{commit.author}}</td>
              <td>{{commit.commitMessage}}</td>
              <td>
                <v-chip :color="getColor(commit.status)" dark small>
                  {{ transform(commit.status) }}
                </v-chip>
              </td>
              <td class="need-mono">
                  <v-tooltip bottom>
                      <template v-slot:activator="{on, attrs}">
                        <span v-bind="attrs" v-on="on"><v-chip small label>{{commit.commithash.slice(0,6)}}</v-chip></span>
                      </template>
                      <span>{{commit.commithash}}</span>
                  </v-tooltip>
              </td>
              <td>{{new Date(commit.commitTime).toLocaleString()}}</td>
              <td @click.stop style="width: 80px">
              <span v-if="commit.reviewerName">{{ commit.reviewerName }}</span>
                <span v-else-if="!isReviewer"> 暂无 </span>
              <el-button v-else @click="selectReviewer(commit)"> 分配审核人员 </el-button>
              </td>
          </tr>
          </tbody>
      </v-simple-table>
      <br>


  </div>
  <v-skeleton-loader v-else type="table" class="mx-auto" />
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
.need-mono {
  font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
}
</style>