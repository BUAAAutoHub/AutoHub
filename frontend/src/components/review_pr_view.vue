<script>
import axios from "axios";
import topicSetting from "@/utils/topic-setting";
import commit from "../views/user/reviews/Commit.vue";
import getIdenticon from "@/utils/identicon";

export default {
  name: "review_pr_view",
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
    updatePrList() {
      this.prListBusy = true
      console.log(this.prList)
      axios.post('/api/develop/getPrList', {
        userId: this.user.id,
        projectId: this.proj.id,
        repoId: this.selectedRepo.id,
      }).then((res) => {
        if (res.data.errcode === 0) {
          this.prList = res.data.data
          let today = new Date()
          // get past 10 days
          let statsPerDay = {}
          for (let i = 0; i < 10; i++) {
            let str = (today.getMonth() + 1) + '.' + today.getDate()
            statsPerDay[str] = 0
            today.setDate(today.getDate() - 1)
          }
          this.prListBusy = false
          this.statsPerDay = {
            label: Object.keys(statsPerDay).reverse(),
            value: Object.values(statsPerDay).reverse()
          }
        } else {
          console.log(res)
          alert('/api/reviews/getPrList error with not 0 err code (' + res.data.errcode + ') ' + res.data.message)
          this.prListBusy = false
        }
      }).catch((err) => {
        alert('/api/reviews/getPrList error' + err)
        this.prListBusy = false
      })
    },
    getTopicColor: topicSetting.getColor,
    getDarkColor: topicSetting.getDarkColor,
    reviewSelectedPr(pr) {
      console.log(pr.prId)
      this.$router.push({
        path: '/prReview/' + this.proj.id + '/' + this.selectedRepo.id + '/' + pr.prId,
        query: {
          prId: pr.prId,
          projId: this.proj.id,
          repoId: this.selectedRepo.id
        }
      })
    },

    getColor(status) {
      if (status) {
        return "red";
      } else {
        return "green"
      }
    },
    transform(status) {
      if (status) {
        return "未审核";
      } else {
        return "已审核"
      }
    },
    selectReviewer(pr) {
      this.selectForm.prId = pr.prId;
      this.selectForm.visible = true;
    },
    submitForm() {
      axios.post('/api/develop/assignPrReviewer', {
        userId: this.user.id,
        projectId: this.proj.id,
        prId: this.selectForm.prId,
        repoId: this.selectedRepo.id,
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
  },
  data() {
    return {
      tempReviewerName: '',
      prListBusy: false,
      prList: [
        {
          prId: 14,
          prIssuer: "ptwang773",
          prTitle: "test pr888",
          prTime: "2024-04-28T08:54:14Z",
          isOpen: false,
          ghLink: "https://github.com/ptwang773/test/pull/14",
          fromBranchName: "pr",
          toBranchName: "main"
        }
      ],
      selectForm: {
        prId: '',
        projectId:'',
        reviewerId: '',
        sha:'',
        visible: false,
      },
      reviewers: [],
      statsPerDay: {},
      isReviewer: true
    }
  }, watch: {
    selectedBranch() {
      this.updatePrList();
      this.updateReviewers();
    }
  }, created() {
    this.updatePrList();
    this.updateReviewers();

  }, inject: {
    user: { default: null },
    proj: { default: null },
    selectedRepo: { default: null },
    selectedBranch: { default: null }
  }
}
</script>

<template>
  <div>
    <v-card-title>仓库中的Pull Request记录</v-card-title>
    <p v-if="!prListBusy && prList.length > 0" style="margin-left: 15px">当前仓库中有 {{ this.prList.length }} 条 pr 记录，请选择要查看的
      pr
      ：</p>
    <p v-else-if="prList.length > 0" style="margin-left: 15px">正在从服务器中读取pr记录，请稍候...</p>
    <div v-if="!prListBusy && prList.length > 0">
      <v-simple-table dense>
        <thead>
          <tr>
            <th class="issuer">issuer</th>
            <th class="Title">title</th>
            <th class="status">status</th>
            <th class="branch">branch</th>
            <th class="time">time</th>
            <th class="reviewer">审核人员</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="pr in this.prList" :key="pr.prId" @click="reviewSelectedPr(pr)">
            <td class="need-mono">{{ pr.prIssuer }}</td>
            <td>{{ pr.prTitle }}</td>
            <td>
              <v-chip :color="getColor(pr.isOpen)" dark small>
                {{ transform(pr.isOpen) }}
              </v-chip>
            </td>
            <td class="need-mono">
              <span> <v-chip label small>{{ pr.fromBranchName }}</v-chip> → <v-chip label small>{{ pr.toBranchName
              }}</v-chip></span>
            </td>
            <td>{{ pr.prTime.slice(0, 10) }} {{ pr.prTime.slice(11, -1) }}</td>
            <td @click.stop style="width: 80px">
              <span v-if="pr.reviewerName">{{ pr.reviewerName }}</span>
              <span v-else-if="!isReviewer"> 暂无 </span>
              <el-button v-else @click="selectReviewer(pr)"> 分配审核人员</el-button>
            </td>
          </tr>
        </tbody>
      </v-simple-table>
      <br>


    </div>
    <v-skeleton-loader v-else-if="prListBusy" type="table" class="mx-auto" />
    <div v-else style="margin-top: -40px">
      <el-empty :image-size="200" description="当前仓库中没有pr记录"></el-empty>
    </div>
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