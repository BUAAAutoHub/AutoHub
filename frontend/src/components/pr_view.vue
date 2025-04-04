
<script>
import axios from "axios";
import topicSetting from "@/utils/topic-setting";

export default {
  name: "pr_view",
  data() {
    return {
      prs: [
        {
          id: 1,
          author: 'TrickEye',
          title: 'PR title1',
          date: '20230403',
          fromBranchId: 2,
          toBranchId: 1,
          isOpen: true
        }, {
          id: 2,
          author: 'TrickEyeee',
          title: 'PR title2',
          date: '20230402',
          fromBranchId: 3,
          toBranchId: 1,
          isOpen: true
        }
      ],
      prsBusy: true,
    }
  }, methods: {
      updatePR() {
          this.prsBusy = true
          axios.post('/api/develop/getPrList', {
              userId: this.user.id,
              projectId: this.proj.id,
              repoId: this.selectedRepo.id
          }).then((res) => {
              if (res.data.errcode === 0) {
                  let prs = res.data.data.map((cur, index, arr) => {
                      return {
                          id: cur.prId,
                          author: cur.prIssuer,
                          title: cur.prTitle,
                          date: cur.prTime,
                          isOpen: cur.isOpen,
                          ghLink: cur.ghLink,
                          fromBranchName: cur.fromBranchName,
                          toBranchName: cur.toBranchName
                      }
                  })
                  this.prs = prs
                  this.prsBusy = false
              } else {
                  console.log('get pr failure with not 0 err code + {' + res.data.errcode + ')' + res.data.message)
                  this.prsBusy = false
              }
          }).catch((err) => {
              console.log('get pr failure with err: ' + err)
              this.prsBusy = false
          })
      },
    getTopicColor: topicSetting.getColor
  }, inject: {
        user: {default: null},
        proj: {default: null},
        selectedRepo: {default: null}
  }, created() {
      this.updatePR()
  }
}
</script>

<template>
<div>
<!--  <p>This is pr view</p>-->

  <v-skeleton-loader v-if="this.prsBusy" type="button, table" />
  <v-row v-else-if="this.prs.length > 0">
    <v-col>
      <v-simple-table dense>
        <tbody>
        <tr v-for="pr in prs" :key="pr.id">
          <td>#{{pr.id}} ({{pr.isOpen ? '开启' : '已关闭'}})</td>
          <td>{{pr.author}}</td>
          <td>{{pr.title}}</td>
          <td>从分支“{{pr.fromBranchName}}”合并到“{{pr.toBranchName}}”</td>
        </tr>
        </tbody>
      </v-simple-table>
    </v-col>
  </v-row>
  <v-row v-else>
  <v-col>
    <p>合并请求似乎空空如也？现在就去GitHub上发一个吧！</p>
  </v-col>
  </v-row>

  <v-card-actions>
    <v-spacer></v-spacer>

    <v-btn :color="getTopicColor(user.topic)" link :href="'https://github.com/' + selectedRepo.user + '/' + selectedRepo.repo + '/pulls'" target="_blank">
      <v-icon>mdi-github</v-icon>在GitHub浏览
    </v-btn>
  </v-card-actions>
</div>
</template>


<style scoped>

</style>