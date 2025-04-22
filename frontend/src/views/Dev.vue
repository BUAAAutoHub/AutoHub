<script>
import { computed } from 'vue';
import bindGithubRepo from "../components/bind_repo.vue"
import bindedGithubRepos from "../components/repo_list.vue"
import repoView from "../components/repo_view.vue"
import axios from 'axios'
import topicSetting from "@/utils/topic-setting";
import introJs from "intro.js";
import 'intro.js/introjs.css';

export default {
    name: "Dev",
    components: {
        bindGithubRepo,
        bindedGithubRepos,
        repoView,
    },
    data() {
        return {
            bindRepos: [],
            bindReposBusy: true,
            // my_ghusername: 'trickeye',
            // my_ghuseremail: '20373866@buaa.edu.cn',
        }
    },
    created() {
        if (this.selectedProj !== null)
          this.updateBindRepos();
    },
    inject: {
        user: {default: null},
        selectedProj: {default: null},
        changeSelectedProj: {default: null}
    },
    provide() {
        return {
            proj: computed(() => {
                return {
                    id: this.selectedProj.projectId,
                    name: this.selectedProj.projectName,
                    intro: this.selectedProj.projectIntro
                }
            }),
            bindRepos: computed(() => this.bindRepos),
            bindReposBusy: computed (() => this.bindReposBusy),
            updateBindRepos: this.updateBindRepos,
        }
    },
    methods: {
        modifyUser() {
            alert('not implemented!')
        },
        updateBindRepos () {
            this.bindReposBusy = true;
            axios.post('/api/develop/getBindRepos', {
                userId: this.user.id,
                projectId: this.selectedProj.projectId
            }).then((res) => {
                if (res.data.errcode === 0) {
                    this.bindRepos = res.data.data.map((cur, index, arr) => {
                        let remotePath = cur.repoRemotePath;
                        remotePath = remotePath.split('/')
                        return {
                            id: cur.repoId,
                            user: remotePath[0],
                            repo: remotePath[1],
                            intro: cur.repoIntroduction
                        }
                    })
                    this.bindReposBusy = false;
                } else if (res.data.errcode === 3) {
                    this.bindReposBusy = false;
                    this.startTour();
                } else {
                    this.bindReposBusy = false;
                    alert('/api/reviews/getBindRepos error with not 0 err code (' + res.data.errcode + ') ' + res.data.message)
                }
            }).catch((err) => {
                alert('/api/reviews/getBindRepos error' + err)
                this.bindReposBusy = false;
            })
        },
        startTour() {
          let app = this.$root.$children[0]
          let userPage = app.$refs.userPage.$el
          introJs().setOptions({
            'prevLabel' : '上一步',
            'nextLabel' : '下一步',
            'doneLabel' : '知道了',
            steps: [
              {
                intro: "欢迎来到开发端！",
              },
              {
                intro: "您还没有绑定token!",
              },
              {
                element: userPage,
                intro: "点击进入用户主页设置token!",
                position: "left"
              },
            ],
            showStepNumbers: true,
            exitOnEsc: true,
            exitOnOverlayClick: false
          }).start();
        },
        // projSelected(proj) {
        //     console.log(JSON.stringify(this.selectedProj) + '<-' + JSON.stringify(proj));
        //     this.selectedProj = proj;
        //     console.log(JSON.stringify(this.selectedProj));
        // },
        getTopicColor: topicSetting.getColor,
        getRadialGradient: topicSetting.getRadialGradient
    }
}
</script>

<template>
    <v-app>
        <v-container v-if="selectedProj !== null">
            <v-row>
                <h1>开发 - {{ selectedProj.projectName }}</h1>
            </v-row>

            <v-row>
                <v-col cols="6">
                    <bindedGithubRepos />
                </v-col>
                <v-divider vertical></v-divider>
                <v-col cols="6">
                    <h2>或者绑定一个新的代码存储库</h2>
                    <bindGithubRepo />
                </v-col>
            </v-row>

            <v-row>
                <repoView />
            </v-row>
        </v-container>
        <v-container v-else>
            <v-row>
                <h1>开发</h1>
            </v-row>
            <v-row>
                <p>请选择一个项目以继续</p>
            </v-row>
            <v-row>
                <v-col cols="4" v-for="project in user.projects" :key="project.id">
                    <v-card>
                        <v-card-title>{{ project.name }}</v-card-title>
                        <v-card-actions>
                            <v-btn :color="getTopicColor(user.topic)" @click="changeSelectedProj(project)">开始！</v-btn>
                        </v-card-actions>
                    </v-card>
                </v-col>
            </v-row>
        </v-container>
    </v-app>
</template>


<style scoped>

</style>