<script>
import { computed } from 'vue';
import bindGithubRepo from "@/components/bind_repo.vue"
import bindedGithubRepos from "@/components/repo_list.vue"
import repoView from "@/components/repo_view.vue"
import reviewView from "@/components/review_view.vue"
import axios from 'axios'
import topicSetting from "@/utils/topic-setting";
import introJs from "intro.js";

export default {
    name: "Dev",
    components: {
        bindGithubRepo,
        bindedGithubRepos,
        repoView,
        reviewView
    },
    data() {
        return {
            bindRepos: [],
            bindReposBusy: true,
            curUserId: '',
            generatedLink: '',     // 新增：存储生成的链接
            shareDialog: false    // 新增：控制对话框显示
        }
    },
    created() {
        if (this.selectedProj !== null)
          this.updateBindRepos();
        this.curUserId = this.$route.query.id
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
                    this.startTour()
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
        generateShareLink() {
            // 直接获取当前页面完整URL
            this.generatedLink = window.location.href;
            this.shareDialog = true;
        },
        copyLink() {
            navigator.clipboard.writeText(this.generatedLink).then(() => {
                this.$message.success('链接已复制到剪贴板');
                this.shareDialog = false;
            }).catch(err => {
                console.error('复制失败:', err);
                this.$message.error('复制失败，请手动复制');
            });
        },
        getTopicColor: topicSetting.getColor,
        getRadialGradient: topicSetting.getRadialGradient
    }
}
</script>

<template>
  <keep-alive>
    <v-app>
        <v-container v-if="selectedProj !== null" style="margin-top: 30px">
            <v-row>
                <h1>代码评审 - {{ selectedProj.projectName }}</h1>
                <v-btn 
                    :color="getTopicColor(user.topic)"
                    @click="generateShareLink"
                    class="ml-4"  
                >
                    <v-icon left>mdi-share</v-icon>
                    生成分享链接
                </v-btn>
            </v-row>

            <!-- 分享链接 -->
            <el-dialog title="分享Commit评审" :visible.sync="shareDialog" width="40%">
                <el-form>
                    <el-form-item label="分享链接">
                        <div class="copy-link-row">
                            <el-input 
                            v-model="generatedLink" 
                            readonly
                            class="flex-grow"
                            />
                            <v-tooltip bottom>
                            <template v-slot:activator="{ on }">
                                <v-btn 
                                icon
                                @click="copyLink"
                                class="ml-2"
                                v-on="on"
                                >
                                <v-icon>mdi-content-copy</v-icon>
                                </v-btn>
                            </template>
                            <span>复制链接</span>
                            </v-tooltip>
                        </div>
                        </el-form-item>
                </el-form>
                </el-dialog>

            <v-row>
              <keep-alive>
                <reviewView />
              </keep-alive>
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
    </keep-alive>
</template>


<style scoped>
/* 强制让 append 成为 flex 容器 */
.share-link-input >>> .el-input-group__append {
  display: flex !important;
  align-items: center !important;
  padding: 0 8px !important;
  white-space: nowrap !important;
  background: #f5f7fa; /* 可选：确保背景和输入框一致 */
}

/* 修复按钮尺寸 */
.share-link-input >>> .v-btn {
  height: 24px !important;
  min-width: 24px !important;
  padding: 0 !important;
  margin: 0 !important;
  line-height: normal !important;
}

/* tooltip 默认生成 span，有时会被当 block 处理 */
.share-link-input >>> .v-tooltip {
  display: inline-flex !important;
  align-items: center;
}

.copy-link-row {
  display: flex;
  align-items: center;
  width: 100%;
}

.copy-link-row .flex-grow {
  flex-grow: 1;
}
</style>