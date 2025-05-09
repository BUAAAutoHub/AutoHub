<template>
    <v-app>
        <v-container>
            <v-col cols="12">
                <v-card>
                    <v-card-title>
                        <h2>请求进行代码评审 - {{ selectedProj.projectName }}</h2>
                        <v-btn 
                            :color="getTopicColor(user.topic)"
                            @click="generateShareLink"
                            class="ml-4"  
                        >
                            <v-icon left>mdi-share</v-icon>
                            生成分享链接
                        </v-btn>
                    </v-card-title>
                    <!-- 分享链接 -->
                    <el-dialog title="分享PR" :visible.sync="shareDialog" width="40%">
                        <el-form>
                            <el-form-item label="链接名称">
                            <el-input 
                                v-model="customLinkName" 
                                placeholder="给我的分享链接起个名字"
                                maxlength="20"
                                show-word-limit
                            ></el-input>
                            </el-form-item>
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
                    <v-card-text class="pa-4">
                        <v-row>
                            <v-col cols="12">
                              <div class="d-flex align-center">
                                <h2 class="mb-0 mr-2">代码仓库：</h2>
                                <el-select v-model="curRepoId" placeholder="请选择">
                                  <el-option v-for="item in repos" :key="item.value" :label="item.label" :value="item.value">
                                  </el-option>
                                </el-select>
                              </div>
                            </v-col>
                        </v-row>
                        <v-row>
                            <v-col cols="5">
                                <v-select
                                    v-model="srcBranch"
                                    label="源分支"
                                    placeholder="请选择"
                                    :items="branches"
                                    item-text="label"
                                    item-value="value"
                                >
                                </v-select>
                            </v-col>
                            <v-col cols="5">
                                <v-select
                                    v-model="dstBranch"
                                    label="目标分支"
                                    :items="branches"
                                    item-text="label"
                                    item-value="value"
                                >
                                </v-select>
                            </v-col>
                        </v-row>
                        <v-row>
                            <v-col cols="7">
                                <v-text-field v-model="title" label="标题" placeholder="请输入标题"></v-text-field>
                            </v-col>
                        </v-row>
                        <v-row>
                            <v-col cols="12">
                                <mavon-editor v-model="html" ref="md" style="min-height: 600px" />
                            </v-col>
                        </v-row>
                    </v-card-text>
                    <v-card-actions>
                        <v-btn color="primary" @click="handle_submit">新建</v-btn>
                        <v-btn @click="handle_cancel">取消</v-btn>
                    </v-card-actions>
                </v-card>
            </v-col>
        </v-container>
    </v-app>
</template>

<script>
import { Editor, Toolbar } from '@wangeditor/editor-for-vue'
import '@wangeditor/editor/dist/css/style.css';
import topicSetting from "@/utils/topic-setting";
import axios from 'axios';
import "mavon-editor/dist/css/index.css";
import introJs from "intro.js";
export default {
    props: {
        userId: {
            type: Number,
            default: null
        },
        projectId: {
            type: Number,
            default: null
        },
        slug: {
            type: String,
            default: ''
        }
    },
    created() {
        // 优先使用路由参数（分享链接场景）
        if (this.projectId && this.userId) {
            this.updateBindRepos();
            return;
        }
        
        // 本地访问场景
        if (this.selectedProj !== null) {
            this.updateBindRepos();
            this.userId = this.user.id;
            this.projectId = this.selectedProj.projectId;
        }
    },
    inject: {
        user: { default: null },
        selectedProj: { default: null },
        changeSelectedProj: { default: null }
    },

    components: { Editor, Toolbar },
    data() {
        return {
            curRepoId: undefined,
            curRepoName: undefined,
            branches: [],
            bindRepos: [],
            repos: [],
            bindReposBusy: true,
            userId: '',
            projId: undefined,
            repoId: undefined,
            srcBranch: '',
            dstBranch: '',
            editor: null,
            title: '',
            html: '',
            image: null,
            image_id: null,
            toolbarConfig: {},
            editorConfig: {
                placeholder: '请输入内容...',
                MENU_CONF: {
                    uploadImage: null,
                }
            },
            mode: 'default', // or 'simple'
            // 新增内容
            shareDialog: false,
            customLinkName: '',
            generatedLink: '',
        }
    },
    methods: {
        // 统一获取 projectId
        getProjectId() {
            // 优先级：props > selectedProj > 路由参数
            return this.projectId 
                || (this.selectedProj && this.selectedProj.projectId)
                || (this.$route.params.projectId ? parseInt(this.$route.params.projectId) : null);
        },

        // 统一获取 userId
        getUserId() {
            // 优先级：props > user 对象 > 路由参数
            return this.userId 
                || (this.user && this.user.id)
                || (this.$route.params.userId ? parseInt(this.$route.params.userId) : null);
        },

        onCreated(editor) {
            this.editor = Object.seal(editor) // 一定要用 Object.seal() ，否则会报错
        },


        handle_submit() {
            console.log(this.html)
            if (
                this.title && this.title.length > 0 &&
                this.html && this.html.length > 0
            ) {
                if (this.srcBranch === this.dstBranch) {
                    this.$message.error({
                        labels: 'error',
                        message: '源分支与目标分支不能相同'
                    });
                } else if (!this.srcBranch) {
                    this.$message.error({
                        labels: 'error',
                        message: '请选择源分支'
                    });
                } else if (!this.dstBranch) {
                    this.$message.error({
                        labels: 'error',
                        message: '请选择目标分支'
                    });
                }
                axios.post('/api/develop/gitPr', {
                    userId: this.userId,
                    projectId: this.projectId,
                    repoId: this.curRepoId,
                    branch: this.srcBranch,
                    title: this.title,
                    body: this.html,
                    base: this.dstBranch
                }).then( (res) => {
                    if (res.data.errcode === 0) {
                        this.$message.success({
                            labels: 'success',
                            message: '成功提交PR'
                        });
                    } else {
                        alert('/api/develop/gitPr error with not 0 err code (' + res.data.errcode + ') ' + res.data.message)
                    }
                })
            } else {
                this.$message.error({
                    labels: 'error',
                    message: '请填写标题和内容！'
                });
            }

        },
        handle_cancel() {
            this.title = '';
            this.html = '';
        },
        modifyUser() {
            alert('not implemented!')
        },
        updateBindRepos() {
            const projectId = this.getProjectId();
            const userId = this.getUserId();

            if (!projectId || !userId) {
                this.$message.error('缺失项目或用户信息');
                return;
            }

            this.bindReposBusy = true;
            axios.post('/api/develop/getBindRepos', {
                // userId: this.user.id,
                // projectId: this.selectedProj.projectId
                userId: userId,
                projectId: projectId
            // this.bindReposBusy = true;
            // axios.post('/api/develop/getBindRepos', {
            //     userId: this.user.id,
            //     projectId: this.selectedProj.projectId
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
                    for (var i = 0; i < this.bindRepos.length; i++) {
                        var newRepo = { value: this.bindRepos[i].id, label: this.bindRepos[i].repo };
                        this.repos.push(newRepo);
                    }
                    this.curRepoId = this.bindRepos[0].id;
                    this.curRepoName = this.bindRepos[0].repo;
                } else if (res.data.errcode === 3) {
                    this.startTour()
                } else {
                    this.bindReposBusy = false;
                    alert('/api/develop/getBindRepos error with not 0 err code (' + res.data.errcode + ') ' + res.data.message)
                }
            }).catch((err) => {
                alert('/api/develop/getBindRepos error' + err)
                this.bindReposBusy = false;
            })
        },

        updateBranch() {
            const projectId = this.getProjectId();
            const userId = this.getUserId();

            if (!projectId || !userId) {
            this.$message.error('缺失项目或用户信息');
            return;
            }
            this.branches = [];
            axios.post('/api/develop/getRepoBranches', {
                // userId: this.user.id,
                // projectId: this.selectedProj.projectId,
                userId: userId,
                projectId: projectId,
                repoId: this.curRepoId
            }).then((res) => {
                if (res.data.errcode === 0) {
                  const branch = res.data.data;
                  for (let i = 0; i < branch.length; i++) {
                    const newBranch = {label: branch[i].branchName, value: branch[i].branchName};
                    this.branches.push(newBranch);
                  }
                } else {
                    this.bindReposBusy = false;
                    alert('/api/develop/getBindRepos error with not 0 err code (' + res.data.errcode + ') ' + res.data.message)
                }
            }).catch((err) => {
                alert('/api/develop/getBindRepos error' + err)
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
        // 生成友好URL
        slugify(text) {
            return text.toString().toLowerCase()
            .replace(/\s+/g, '-')
            .replace(/[^\w-]+/g, '')
            .replace(/--+/g, '-')
            .replace(/^-+/, '')
            .replace(/-+$/, '');
        },

        // 生成分享链接
        generateShareLink() {
            const projectId = this.getProjectId();
            const projectName = (this.selectedProj && this.selectedProj.projectName) || '未知项目';
            const userId = this.getUserId();

            if (!projectId) {
                this.$message.error('无法获取项目ID');
                return;
            }
                if (!userId) {
                this.$message.error('无法获取用户ID');
                return;
            }

            // 生成默认链接名称
            const defaultName = `${this.selectedProj.projectName}_PR链接`;
            this.customLinkName = this.customLinkName || defaultName;
            
            // 生成友好URL
            const slug = this.slugify(this.customLinkName);
            
            // 新链接格式：/share/pr/[userid]/[projectid]-[slug]
            this.generatedLink = `${window.location.origin}/share/pr/${userId}/${projectId}/${slug}`;
            
            this.shareDialog = true;
        },

        // 复制链接（增强兼容性）
        async copyLink() {
            try {
            if (navigator.clipboard && window.isSecureContext) {
            await navigator.clipboard.writeText(this.generatedLink)
            } else {
            const input = document.createElement('input')
            input.value = this.generatedLink
            document.body.appendChild(input)
            input.select()
            document.execCommand('copy')
            document.body.removeChild(input)
            }

            this.copySuccess = true
            setTimeout(() => {
            this.copySuccess = false
            }, 2000)
        } catch (err) {
            console.error('复制失败:', err)
            this.$message.error('复制失败，请手动复制链接')
        }
        },
        getTopicColor: topicSetting.getColor,
        getRadialGradient: topicSetting.getRadialGradient,

    },
    beforeDestroy() {
        const editor = this.editor
        if (editor == null) return
        editor.destroy() // 组件销毁时，及时销毁编辑器
    },
    watch: {
        curRepoId() {

            this.updateBranch();
        }
    }
}
</script>


<style scoped>
.base {
    margin: 30px;
}

.mavon-editor {
  z-index: 10 !important;
}


.title {
    display: flex;
    flex-direction: row;
    margin: 10px;
}

.el-input {
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.editor {
    border: 2px solid #ccc;
    margin: 10px;
    border-radius: 5px;
    text-align: left;
}

.left-align-form .el-form-item {
    text-align: left;
}

.image-center-content {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100%;
}

.avatar-uploader .el-upload {
    border: 1px dashed #d9d9d9;
    border-radius: 6px;
    cursor: pointer;
    position: relative;
    overflow: hidden;
}

.avatar-uploader .el-upload:hover {
    border-color: #409EFF;
}

.avatar-uploader-icon {
    font-size: 28px;
    color: #8c939d;
    width: 200px;
    height: 150px;
    line-height: 150px;
    text-align: center;
}

.avatar {
    width: 200px;
    height: 150px;
    display: block;
}

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
    