<script>
import axios from "axios";
import topicSetting from "@/utils/topic-setting";

export default {
  name: "commit_view",
  methods: {
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

                  this.commitHistory = res.data.data.map((cur, index) => {
                      let time = new Date(cur.commitTime)
                      let str = (time.getMonth() + 1) + '.' + time.getDate()
                      if (str in statsPerDay)
                          statsPerDay[str] += 1
                      return {
                          id: index,
                          committer: cur.author,
                          committerEmail: cur.authorEmail,
                          hash: cur.commithash,
                          message: cur.commitMessage,
                          time: cur.commitTime
                      }
                  })
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
      getDarkColor: topicSetting.getDarkColor
  },
  data() {
    return {
      commitHistoryBusy: true,
      commitHistory: [
        {

        }
      ],
      statsPerDay: {}
    }
  }, watch: {
    selectedBranch() {
        this.updateCommitHistory()
    }
  }, created() {
        this.updateCommitHistory()
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

  <p v-if="!commitHistoryBusy">分支<span class="need-mono"> “{{selectedBranch.name}}” </span>中有 {{ commitHistory.length }} 条提交记录。最新的提交记录：</p>
  <p v-else>正在与服务器同步分支{{selectedBranch.name}}上的最新提交记录...</p>
  <div v-if="!commitHistoryBusy">
      <v-simple-table dense>
          <thead>
          <tr>
              <th class="committer">committer</th>
              <th class="message">message</th>
              <th class="hash">hash</th>
              <th class="time">time</th>
          </tr>
          </thead>
          <tbody>
          <tr v-for="commit in commitHistory.slice(0, 5)" :key="commit.id">
              <td class="need-mono">{{commit.committer}}</td>
              <td>{{commit.message}}</td>
              <td class="need-mono">
                  <v-tooltip bottom>
                      <template v-slot:activator="{on, attrs}">
                          <span v-bind="attrs" v-on="on">{{commit.hash.slice(0,6)}}</span>
                      </template>
                      <span>{{commit.hash}}</span>
                  </v-tooltip>
              </td>
              <td>{{new Date(commit.time).toLocaleString()}}</td>
          </tr>
          </tbody>
      </v-simple-table>
      <br>
      <v-divider></v-divider>
      <br>
      <v-card-title>过去10天的提交记录数量</v-card-title>
      <v-sparkline
              :labels="statsPerDay.label"
              :value="statsPerDay.value"
              :color="getDarkColor(user.topic)"
              auto-line-width
              smooth
              padding="20"
              stroke-linecap="round"
              show-labels
              auto-draw
      ></v-sparkline>
      <br> <v-divider></v-divider> <br>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn width="10rem" :color="getTopicColor(user.topic)" link :to="'/dev/bot/' + user.id +'/'+ proj.id + '/' + selectedRepo.id + '/'" target="_blank"><v-icon>mdi-account</v-icon>项目BOT</v-btn>
        <v-btn width="10rem" :color="getTopicColor(user.topic)" link :href="'https://github.com/' + selectedRepo.user + '/' + selectedRepo.repo + '/tree/' + selectedBranch.name" target="_blank"><v-icon>mdi-github</v-icon>在GitHub查看</v-btn>
        <v-btn width="10rem" :color="getTopicColor(user.topic)" link :to="'/dev/' + proj.id + '/' + selectedRepo.id + '/' + selectedBranch.name + '/'" target="_blank"><v-icon>mdi-send</v-icon>浏览详情</v-btn>
      </v-card-actions>
  </div>
  <v-skeleton-loader v-else type="table" class="mx-auto" />

</div>
</template>


<style scoped>
.need-mono {
  font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
}
</style>