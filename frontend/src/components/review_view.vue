<script>
import {computed} from 'vue'
import reviewBranchView from './review_branch_view.vue'
import issue_view from "@/components/issue_view.vue";
import pr_view from "@/components/pr_view.vue";
import topicSetting from "@/utils/topic-setting";
export default {
    name: "reviewView",
    components: {
      reviewBranchView,
      issue_view,
      pr_view
    },
    data() {
      return {
        selectedRepo: 0,
        // bondedRepos: [
        //   {
        //     id: 1,
        //     user: "opencv",
        //     repo: "opencv",
        //     intro: "opencv introduction. A Bonded repo of #" + this.proj.id + " called " + this.proj.name
        //   }, {
        //     id: 2,
        //     user: "buaa2023sw",
        //     repo: "doc",
        //     intro: "doc introduction"
        //   }
        // ]
      }
    },
    inject: {
        user: {default: null},
        proj: { default: null },
        bindRepos: {default: null},
        bindReposBusy: {default: null}
    },
    provide() {
        return {
          selectedRepo: computed(() => this.bindRepos[this.selectedRepo])
        }
    },
    methods: {
      getTopicColor: topicSetting.getColor,
      getDarkColor: topicSetting.getDarkColor,
      getRadialGradient: topicSetting.getRadialGradient
    }
}
</script>

<template>
<v-col cols="12" class="px-1">
  <h2 v-if="bindReposBusy">代码存储库</h2>
  <h2 v-else-if="bindRepos.length > 0">代码存储库 - {{ bindRepos[selectedRepo].user }} / {{ bindRepos[selectedRepo].repo}}</h2>
  <h2 v-else>代码存储库</h2>

  <v-skeleton-loader v-if="bindReposBusy" type="card"></v-skeleton-loader>
  <div v-else-if="bindRepos.length > 0">
      <v-tabs :color="getDarkColor(user.topic)" v-model="selectedRepo">
          <v-tab v-for="repository in bindRepos" :key="repository.id">{{ repository.repo }}</v-tab>
      </v-tabs>
      <v-tabs-items v-model="selectedRepo">
          <v-tab-item v-for="repository in bindRepos" :key="repository.id">
              <p v-if="bindRepos[selectedRepo].intro !== ''">代码存储库介绍：{{ bindRepos[selectedRepo].intro }}</p>
              <p v-else>这个代码存储库没有介绍哦</p>
              <v-row><v-col class="ma-1"><el-card><reviewBranchView /></el-card></v-col></v-row>
          </v-tab-item>
      </v-tabs-items>
  </div>
  <div v-else>
      <p>这个项目还没有绑定代码存储库哦</p>
  </div>
</v-col>
</template>