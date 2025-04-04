<script>
import { computed } from 'vue'
import axios from "axios";
import topicSetting from "@/utils/topic-setting";

export default {
  name: "issue_view",
  data() {
    return {
      issues: [
        {
          id: 1,
          issuer: 'TrickEye',
          title: 'issue title1',
          isOpen: true
        }, {
          id: 2,
          issuer: 'TrickEye',
          title: 'issue title2',
          isOpen: false
        }
      ],
      filteredIssues: computed(() => {
        if (this.statusFilter === 1) {
          return this.issues
        } else {
          return this.issues.filter((cur, index, arr) => {
            return cur.isOpen === (this.statusFilter === 0)
          })
        }
      }),
      issuesBusy: true,
      statusFilter: 0,
      statuses: ['Open', 'All', 'Closed']
    }
  },
  inject: {
    user: {default: null},
    proj: {default: null},
    selectedRepo: {default: null}
  },
  methods: {
    updateIssue() {
        this.issuesBusy = true
        axios.post('/api/develop/getIssueList', {
            userId: this.user.id,
            repoId: this.selectedRepo.id,
            projectId: this.proj.id
        }).then((res) => {
            if (res.data.errcode === 0) {
                let issues = res.data.data.map((cur, index, arr) => {
                    return {
                        id: cur.issueId,
                        issuer: cur.issuer,
                        title: cur.issueTitle,
                        time: cur.issueTime,
                        isOpen: cur.isOpen,
                        ghLink: cur.ghLink
                    }
                })
                this.issues = issues
                this.issuesBusy = false
            } else {
                console.log(res);
                alert('/api/reviews/getIssueList error with not 0 err code (' + res.data.errcode + ') ' + res.data.message)
                this.issuesBusy = false
            }
        }).catch((err) => {
            alert('/api/reviews/getIssueList error' + err)
            this.issuesBusy = false
        })
    },
    issueFilter() {
      return this.issues.filter((issue) => {
        if (issue.isOpen && this.statusFilter === 2) return false;
        if (!issue.isOpen && this.statusFilter === 0) return false;
        else return true;
      })
    },
    getTopicColor: topicSetting.getColor
  }, created() {
    this.updateIssue()
  }
}
</script>

<template>
<div>
<!--  <p>this is issue view.</p>-->
<!--    <p>{{ this.issues.length }}</p>-->
  <v-skeleton-loader v-if="this.issuesBusy" type="button, table" />
  <v-row v-else-if="this.issues.length !== 0">
    <v-col>
      <v-simple-table dense>
        <tbody>
        <tr v-for="issue in filteredIssues" :key="issue.id">
          <td>#{{issue.id}} ({{issue.isOpen ? '开启' : '已关闭'}})</td>
          <td>{{issue.issuer}}</td>
          <td>{{issue.title}}</td>
        </tr>
        </tbody>
      </v-simple-table>
    </v-col>
  </v-row>
  <v-row v-else>
    <v-col>
      <p>似乎事务空空如也？现在就去GitHub上发一个吧！</p>
    </v-col>
  </v-row>

  <v-card-actions>
    <v-btn
        :color="getTopicColor(user.topic)"
        @click="statusFilter = (statusFilter + 1) % 3; filteredIssues = issueFilter()"
    >
      筛选状态：{{ statuses[statusFilter] }}
    </v-btn>

    <v-spacer></v-spacer>

    <v-btn :color="getTopicColor(user.topic)" link :href="'https://github.com/' + selectedRepo.user + '/' + selectedRepo.repo + '/issues'" target="_blank">
      <v-icon>mdi-github</v-icon>在GitHub浏览
    </v-btn>
  </v-card-actions>
</div>
</template>



<style scoped>

</style>