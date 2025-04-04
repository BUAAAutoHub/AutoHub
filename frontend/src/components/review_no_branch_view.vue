<script>
import {computed} from "vue";
import review_commit_view from "@/components/review_commit_view.vue";
import review_pr_view from "@/components/review_pr_view.vue"
import axios from "axios";

export default {
  name: "reviewNoBranchView",
  components: {
    review_commit_view,
    review_pr_view
  },
  methods: {
    data() {
      return {
        selectedBranchIndex: 0,
        branches: [{
          id: 0,
          name: 'master',
          lastCommit: {}
        }],
        branchBusy: true
      }
    }, inject: {
      user: {default: null},
      proj: {default: null},
      selectedRepo: {default: null}
    }, provide() {
      return {
      }
    }, created() {

    }
  }
}
</script>

<template>
<div>
<!--  <p>I am branch view, I am aware that my proj = {{ proj }}, and that my selected repo = {{ selectedRepo }}</p>-->

<!--  <v-col cols="3">-->
<!--    <v-card-title>分支</v-card-title>-->
<!--    <div v-if="branchBusy">-->
<!--        <v-card-title><v-progress-circular indeterminate></v-progress-circular>正在与服务器同步分支</v-card-title>-->
<!--    </div>-->
<!--    <v-list outlined shaped v-if="!branchBusy" class="overflow-y-auto">-->
<!--      <v-list-item-group v-model="selectedBranchIndex" mandatory>-->
<!--        <v-list-item v-for="branch in branches" :key="branch.id" two-line>-->
<!--          <v-list-item-content>-->
<!--            <v-list-item-title>-->
<!--              <div style="display: inline-block;" class="need-mono">{{ branch.name }}</div>-->
<!--              <p style="margin-top: -15px"></p>-->
<!--              <div class="subtitle-2" style="display: inline-block;">更新于{{new Date(branch.lastCommit.commitDate).toLocaleString() }}</div>-->
<!--            </v-list-item-title>-->
<!--            <v-list-item-subtitle>{{ branch.lastCommit.commitMessage }}</v-list-item-subtitle>-->
<!--          </v-list-item-content>-->
<!--        </v-list-item>-->
<!--      </v-list-item-group>-->
<!--    </v-list>-->
<!--      <v-skeleton-loader v-else type="list-item-three-line"></v-skeleton-loader>-->
<!--&lt;!&ndash;      <v-progress-circular v-else indeterminate></v-progress-circular>&ndash;&gt;-->
<!--  </v-col>-->

<!--  <v-divider vertical></v-divider>-->


    <review_pr_view/>


</div>
</template>



<style scoped>
.need-mono {
  font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
}
</style>