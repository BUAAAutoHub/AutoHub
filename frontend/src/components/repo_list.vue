<script>

import axios from "axios";
import topicSetting from "@/utils/topic-setting";

export default {
    name: "bindedGithubRepos",
    inject: {
        user: { default: null },
        proj: { default: null },
        bindRepos: {default: null},
        bindReposBusy: {default: null},
        updateBindRepos: {default: () => {}} // default is a function that returns nothing
    },
    data() {
        return {
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
          //     intro: "doc introduction. A Bonded repo of #" + this.proj.id + " called " + this.proj.name
          //   }
          // ]
        }
    },
    methods: {
        unbind(repo) {
            axios.post('/api/develop/userUnbindRepo',
                {
                    userId: this.user.id,
                    projectId: this.proj.id,
                    repoId: repo.id
                }).then((res) => { this.updateBindRepos() })
                .catch((err) => { alert('哦不，好像解绑失败了！'); this.bindingInProgress = false; })
        },
        getTopicColor: topicSetting.getColor,
    }
}

</script>

<template>
    <div>
        <h2>已绑定的代码存储库</h2>
        <p v-if="!bindReposBusy">项目“{{ proj.name }}”已绑定 {{ bindRepos.length }} 个代码存储库。</p>
        <p v-else>正在加载项目“{{ proj.name }}”已绑定的代码存储库列表...</p>
        <v-divider></v-divider>
        <br/>
        <v-skeleton-loader v-if="bindReposBusy"
                type="list-item, list-item, list-item"
        ></v-skeleton-loader>
        <v-expansion-panels v-else-if="bindRepos.length > 0">
            <v-expansion-panel
                    v-for="repo in bindRepos"
                    :key="repo.id"
            >
                <v-expansion-panel-header>
                    {{ repo.user }} / {{ repo.repo }}
                </v-expansion-panel-header>
                <v-expansion-panel-content>
                        <div class="description" v-if="repo.intro !== ''">{{ repo.intro }}</div>
                        <div class="description" v-else>存储库的简介空空如也</div>
                  <br>
                  <v-row>
                    <v-col cols="6"  class="text-center"><v-btn :color="getTopicColor(user.topic)" link :href="'https://github.com/' + repo.user + '/' + repo.repo" target="_blank"><v-icon>mdi-github</v-icon>GitHub</v-btn></v-col>
                    <v-col cols="6"  class="text-center"><v-btn :color="getTopicColor(user.topic)" @click="unbind(repo)"><v-icon>mdi-link-variant-off</v-icon>Unbind</v-btn></v-col>
                  </v-row>
                </v-expansion-panel-content>
            </v-expansion-panel>
        </v-expansion-panels>
        <v-card v-else>
            <v-card-title>
                <v-icon>mdi-github</v-icon>
                <span class="headline ml-3">还没有绑定代码存储库</span>
            </v-card-title>
            <v-divider></v-divider>
            <v-card-subtitle>
                <span class="subtitle-1 ml-4">唔，快去绑定一个代码存储库开始记录你的工作吧！</span>
            </v-card-subtitle>
        </v-card>
    </div>
</template>

<style scoped>
.description {
    word-break:normal;
    width:auto;
    display:block;
    white-space:pre-wrap;
    word-wrap : break-word ;
    overflow: hidden ;
    line-height: 1.5rem;
}
</style>