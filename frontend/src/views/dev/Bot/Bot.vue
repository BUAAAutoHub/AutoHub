<!-- action: comment or label-->
<!-- rule content: 字段名和字段值用双引号包裹-->
<template>
    <el-row :gutter="20" class="layout-container">
        <!-- 左侧导航 -->
        <el-col :span="4">
            <div class="sidebar">
                <el-menu default-active="bot" class="el-menu-vertical-demo" @select="handleNav">
                    <el-menu-item index="bot">Bot 绑定</el-menu-item>
                    <el-menu-item index="rules">规则管理</el-menu-item>
                    <el-menu-item index="labels">标签管理</el-menu-item>
                    <el-menu-item index="logs">日志记录</el-menu-item>
                </el-menu>
            </div>
        </el-col>

        <!-- 右侧内容区域 -->
        <el-col :span="20">
            <div class="project-bot">
                <!-- 你的卡片区块都写在这里 -->
                <div class="project-bot">
                    <!-- 标题栏 -->
                    <el-row justify="space-between" type="flex" class="header">
                        <h2>项目 Bot 管理</h2>
                        <!-- <el-button
                                    size="mini"
                                    icon="el-icon-edit"
                                    type="primary"
                                    plain
                                    @click="editRule(scope.$index)"
                                    ></el-button> -->
                        <el-button type="primary" @click="checkProject" plain :loading="checking">🔍 检查项目</el-button>
                    </el-row>
                
                    <!-- 未绑定 Bot 提示 -->
                    <el-skeleton v-if="loadingBotStatus" animated style="margin-bottom: 12px;">
                        <el-skeleton-item variant="text" />
                    </el-skeleton>
                    <el-alert
                        v-if="!botBound"
                        title="当前项目未绑定 Bot，请先绑定"
                        type="warning"
                        show-icon
                        class="mb-2"
                    >
                    </el-alert>

                    <!-- bot绑定 区块 -->
                    <el-card class="box-card" id="bot-section">
                        <div slot="header" class="clearfix">
                        <span>Bot 绑定</span>
                        </div>

                        <!-- 输入 token -->
                        <el-form :inline="true" :model="form" class="bot-control">
                            <el-form-item label="信息">
                                <el-input
                                v-model="form.name"
                                placeholder="请输入 GitHub 用户名"
                                clearable
                                style="width: 300px"
                                />
                                <el-input
                                v-model="form.token"
                                placeholder="请输入 GitHub 个人访问令牌"
                                clearable
                                style="width: 300px"
                                />
                            </el-form-item>

                            <!-- 主操作按钮：绑定 -->
                            <el-form-item>
                                <el-button
                                type="primary"
                                :loading="binding"
                                icon="el-icon-link"
                                @click="bindBot"
                                class="assistant-button"
                                >
                                绑定 Bot
                                </el-button>
                            </el-form-item>


                            <!-- 状态切换按钮：启用/禁用 -->
                            <el-form-item v-if="botBound">
                            <!-- <el-form-item> -->
                                <el-tooltip content="禁用 Bot 功能" v-if="botEnabled">
                                <el-button
                                    type="warning"
                                    icon="el-icon-switch-button"
                                    @click="changeBotStatus"
                                    plain
                                >
                                    禁用
                                </el-button>
                                </el-tooltip>
                                <el-tooltip content="启用 Bot 功能" v-else>
                                <el-button
                                    type="success"
                                    icon="el-icon-check"
                                    @click="changeBotStatus"
                                    plain
                                >
                                    启用
                                </el-button>
                                </el-tooltip>
                            </el-form-item>

                            <!-- 删除 Bot -->
                            <!-- <el-form-item v-if="botBound">
                                <el-button
                                type="danger"
                                icon="el-icon-delete"
                                @click="removeBot"
                                plain
                                >
                                移除
                                </el-button>
                            </el-form-item> -->

                        </el-form>


                        <!-- 绑定结果提示 -->
                        <el-alert
                        v-if="bindResult.message"
                        :title="bindResult.message"
                        :type="bindResult.success ? 'success' : 'error'"
                        show-icon
                        :closable="false"
                        class="mt-2"
                        />
                    </el-card>
                
                    <!-- Rules 区块 -->
                    <el-card class="box-card" id="rules-section">
                        <div slot="header" class="clearfix">
                            <span>规则管理</span>
                            <el-button style="float: right;" type="primary" size="small" @click="addRule" class="assistant-button">➕ 新增规则</el-button>
                        </div>

                        <el-table :data="rules" stripe :loading="loadingRules">
                        
                            <!-- 标题 + 类型合并列 -->
                            <el-table-column label="规则" width="220">
                                <template slot-scope="scope">
                                    <div style="display: flex; align-items: center; flex-wrap: wrap;">
                                        <el-tag
                                            size="mini"
                                            :type="scope.row.type === 'PR' ? 'success' : 'warning'"
                                            style="margin-left: 6px;"
                                        >
                                            {{ scope.row.type }}
                                        </el-tag>
                                        <el-tag size="mini" type="info">{{ scope.row.name }}</el-tag>
                                    </div>
                                </template>
                            </el-table-column>

                            <!-- 内容列：省略显示 + tooltip -->
                            <el-table-column label="描述">
                                <template slot-scope="scope">
                                    <el-tooltip class="item" effect="dark" :content="scope.row.content.description" placement="top-start">
                                    <span class="text-ellipsis">{{ scope.row.content.description }}</span>
                                    </el-tooltip>
                                </template>
                            </el-table-column>

                            <!-- action列 -->
                            <el-table-column label="action">
                                <template slot-scope="scope">
                                    <el-tag size="mini" type="info">{{ scope.row.content.action }}</el-tag>
                                </template>
                            </el-table-column>

                            <!-- 操作列 -->
                            <el-table-column label="操作" width="140">
                                <template slot-scope="scope">
                                    <el-button
                                    size="mini"
                                    icon="el-icon-info"
                                    type="primary"
                                    plain
                                    @click="editRule(scope.$index)"
                                    ></el-button>
                                    <el-button
                                    size="mini"
                                    icon="el-icon-delete"
                                    type="danger"
                                    plain
                                    @click="deleteRule(scope.$index)"
                                    ></el-button>
                                </template>
                            </el-table-column>
                        </el-table>
                    </el-card>

                    <!-- Label 区块 -->
                    <el-card class="box-card" id="labels-section">
                        <div slot="header" class="clearfix">
                        <span>标签管理</span>
                        <el-button style="float: right;" type="primary" size="small" @click="addLabel" class="assistant-button">➕ 新增标签</el-button>
                        </div>
                
                        <el-table :data="labels" stripe :loading="loadingLabels">
                            <el-table-column label="Label" width="220">
                                <template slot-scope="scope">
                                    <el-tag :style="{ backgroundColor: scope.row.color, color: '#fff' }">
                                        {{ scope.row.name }}
                                    </el-tag>
                                </template>
                            </el-table-column>
                            <el-table-column label="描述" prop="description"></el-table-column>
                            <!-- 操作列 -->
                            <el-table-column label="操作" width="140">
                                <template slot-scope="scope">
                                    <el-button
                                    size="mini"
                                    icon="el-icon-info"
                                    type="primary"
                                    plain
                                    @click="editLabel(scope.$index)"
                                    ></el-button>
                                    <el-button
                                    size="mini"
                                    icon="el-icon-delete"
                                    type="danger"
                                    plain
                                    @click="deleteLabel(scope.$index)"
                                    ></el-button>
                                </template>
                            </el-table-column>
                        </el-table>
                    </el-card>

                    <!-- 日志 区块 -->
                    <el-card class="box-card" id="logs-section">
                        <div slot="header" class="clearfix">
                            <span>日志记录</span>
                        </div>
                
                        <!-- todo：记录每一次检查项目的时间以及从后端返回的结果-->
                        <el-empty v-if="!logs.length" description="暂无日志记录" />
                        <el-timeline>
                            <el-timeline-item
                                v-for="(log, index) in logs"
                                :key="index"
                                :timestamp="log.time"
                                :type="log.success ? 'success' : 'danger'"
                            >
                            <div>{{ log.result }}</div>

                            <!-- 如果有详情，则显示可折叠区域 -->
                            <div v-if="log.details && log.details.length">
                            <div
                                class="log-detail"
                                :class="{ collapsed: !log.expanded }"
                            >
                                <div v-for="(detail, i) in log.details" :key="i">
                                {{ detail }}
                                </div>
                            </div>
                            </div>

                            </el-timeline-item>
                        </el-timeline>
                    </el-card>

                    <!-- 添加/编辑 Rule 弹窗 -->
                    <el-dialog :title="editIndex === null ? '新增规则' : '规则详情'" :visible.sync="ruleModalVisible">
                        <el-form :model="currentRule" label-width="80px">
                            <el-form-item label="标题">
                                <el-input v-model="currentRule.name"></el-input>
                            </el-form-item>
                            <el-form-item label="描述">
                                <el-input v-model="currentRule.content.description"></el-input>
                            </el-form-item>
                            <el-form-item label="类型">
                                <el-select v-model="currentRule.type" placeholder="选择类型" size="mini">
                                    <el-option label="PR" value="PR"></el-option>
                                    <el-option label="ISSUE" value="ISSUE"></el-option>
                                </el-select>
                            </el-form-item>
                            <el-form-item label="action">
                                <el-select v-model="currentRule.content.action" placeholder="选择action" size="mini">
                                    <el-option label="comment" value="comment"></el-option>
                                    <el-option label="label" value="label"></el-option>
                                </el-select>
                            </el-form-item>
                            <el-form-item label="内容">
                                <el-input type="textarea" v-model="currentRule.content.prompt" rows="3"></el-input>
                            </el-form-item>
                        </el-form>
                        <div slot="footer" v-if="editIndex == null">
                            <el-button @click="ruleModalVisible = false" class="assistant-button">取消</el-button>
                            <el-button type="primary" @click="saveRule" class="assistant-button">保存</el-button>
                        </div>
                    </el-dialog>
                
                    <!-- 添加/编辑 Label 弹窗 -->
                    <el-dialog :title="editIndex === null ? '新增标签' : '标签详情'" :visible.sync="labelModalVisible">
                        <el-form :model="currentLabel" label-width="80px">
                            <el-form-item label="Label">
                                <el-input v-model="currentLabel.name"></el-input>
                            </el-form-item>
                            <el-form-item label="描述">
                                <el-input type="textarea" v-model="currentLabel.description" rows="3"></el-input>
                            </el-form-item>
                            <el-form-item label="颜色">
                                <el-color-picker v-model="currentLabel.color"></el-color-picker>
                            </el-form-item>
                        </el-form>
                        <div slot="footer" v-if="editIndex == null">
                            <el-button @click="labelModalVisible = false" class="assistant-button">取消</el-button>
                            <el-button type="primary" @click="saveLabel" class="assistant-button">保存</el-button>
                        </div>
                    </el-dialog>
                </div>
            </div>
        </el-col>
    </el-row> 
</template>
  
<script>
import axios from "axios";
import util from "@/views/util";
  export default {
    name: 'ProjectBot',
    data() {
      return {
        botBound: false,
        botEnabled: true,
        botToken: '',
        showBindModal: false,

        loadingBotStatus: true,

        loadingRules: false,
        rules: [],
        ruleModalVisible: false,
        currentRule: {
            type: '',          
            name: '',          
            default: 0,  
            content: {
                name: '',        
                description: '', 
                prompt: '',      
                action: ''      
            }
        },
        loadingLabels: false,
        labels: [],
        labelModalVisible: false,
        currentLabel: { name:'', description:'', default: 0, color: '#409EFF' },
        editIndex: null,
        checking: false,

        githubUsername: localStorage.getItem('githubUsername') || '',
        form: {
            name: '',
            token: '',
        },
        binding: false,
        bindResult: {
            success: false,
            message: '',
        },
        logs: [],
      }
    },
    methods: {
        isDuplicateRule(rule) {
            return this.rules.some(r => r.name === rule.name && r.type === rule.type);
        },
        isDuplicateLabel(label) {
            return this.labels.some(l => l.name === label.name);
        },
        handleNav(index) {
            const sectionMap = {
                bot: 'bot-section',
                rules: 'rules-section',
                labels: 'labels-section',
                logs: 'logs-section'
            }
            const targetId = sectionMap[index]
            const el = document.getElementById(targetId)
            if (el) {
                el.scrollIntoView({ behavior: 'smooth', block: 'start' })
            }
        },
        addLabel() {
            this.editIndex = null
            this.currentLabel= { name:'', description:'', default: 0, color: '#409EFF' },
            this.labelModalVisible = true
        },
        editLabel(index) {
            this.editIndex = index
            this.currentLabel = { ...this.labels[index] }
            this.labelModalVisible = true
        },
        async saveLabel() {
            const newLabel = this.currentLabel;
            if (!newLabel.name) {
                this.$message.error('标签名称不能为空');
                return;
            }

            if (this.isDuplicateRule(newLabel)) {
                this.$message.error('已有相同名称的标签，请修改后再试');
                return;
            }

            try {
                const response = await axios.post('/api/bot/addlabel2db', {
                    repoId: this.$route.params.repoid,
                    labelName: this.currentLabel.name,
                    labelColor: this.currentLabel.color,
                    labelDescription: this.currentLabel.description
                });
                if(response.data.errcode == 0) {
                    console.log("新增/编辑标签成功");
                } else {
                    this.$message.error("新增/编辑标签失败"+response.data.errcode+ response.data.massage)
                }
            } catch (err) {
                this.$message.error(err+" 新增/编辑标签失败")
            } finally {
                if (this.editIndex === null) {
                    this.labels.push({ ...this.currentLabel })
                } else {
                    this.$set(this.labels, this.editIndex, { ...this.currentLabel })
                }
                this.labelModalVisible = false
            }
        },
        async deleteLabel(index) {
            try {
                const response = await axios.post('/api/bot/removelabel', {
                    repoId: this.$route.params.repoid,
                    labelName: this.labels[index].name
                });
                if(response.data.errcode == 0) {
                    this.labels.splice(index, 1)
                    console.log("删除标签成功");
                } else {
                    this.$message.error("删除标签失败"+response.data.errcode+ response.data.massage)
                }
            } catch (err) {
                this.$message.error(err+" 删除标签失败")
            } 
        },
        addRule() {
            this.editIndex = null
            this.currentRule = {
                type: '',          
                name: '',          
                default: 0,  
                content: {
                    name: '',        
                    description: '', 
                    prompt: '',      
                    action: ''      
                }
            }
            this.ruleModalVisible = true 
        },
        editRule(index) {
            this.editIndex = index
            this.currentRule = { ...this.rules[index] }
            this.ruleModalVisible = true
        },
        async saveRule() {
            const newRule = this.currentRule;
            if (!newRule.name || !newRule.type) {
                this.$message.error('规则名称和类型不能为空');
                return;
            }

            if (this.isDuplicateRule(newRule)) {
                this.$message.error('已有相同名称和类型的规则，请修改后再试');
                return;
            }
            try {
                const response = await axios.post('/api/bot/addrule2db', {
                    repoId: this.$route.params.repoid,
                    ruleType: this.currentRule.type,
                    ruleName: this.currentRule.name,
                    ruleContent: JSON.stringify(this.currentRule.content)
                });
                if(response.data.errcode == 0) {
                    console.log("新增规则成功");
                } else {
                    this.$message.error("新增规则失败"+response.data.errcode+ response.data.massage)
                }
            } catch (err) {
                this.$message.error(err+" 新增规则失败")
            } finally 
            {
                if (this.editIndex === null) {
                this.rules.push({ ...this.currentRule })
                } else {
                this.$set(this.rules, this.editIndex, { ...this.currentRule })
                }
                this.ruleModalVisible = false
            }   
        },
        async deleteRule(index) {
            try {
                const response = await axios.post('/api/bot/removerule', {
                    repoId: this.$route.params.repoid,
                    ruleName: this.rules[index].name,
                    ruleType: this.rules[index].type
                });
                if(response.data.errcode == 0) {
                    this.rules.splice(index, 1)
                    console.log("删除规则成功");
                } else {
                    this.$message.error("删除规则失败"+response.data.errcode+ response.data.massage)
                }
            } catch (err) {
                this.$message.error(err+" 删除规则失败")
            }
        },
        async checkProject() {
            this.checking = true
            try {
                const projId = this.$route.params.projid;
                const repoId = this.$route.params.repoid;

                const res = await axios.post('/api/bot/autoreview', {
                    projectId: projId,
                    repoId
                });

                if(res.data.errcode == 0) {
                    const logEntry = {
                        time: new Date().toLocaleString(),
                        result: res.data.message || '检查完成，未发现问题！',
                        success: res.data.errcode === 0,
                        details: res.data.data || [] 
                    };
                    this.logs.unshift(logEntry);
                    this.$message.success(logEntry.result);
                } else {
                    const logEntry = {
                        time: new Date().toLocaleString(),
                        result: '检查失败：ERR'+(res.data.errcode + " "+ res.data.message || '未知错误'),
                        success: false,
                        details: []
                    };
                    this.logs.unshift(logEntry);
                    this.$message.error(logEntry.result)
                }   
            } catch (error) {
                const logEntry = {
                    time: new Date().toLocaleString(),
                    result: '检查失败：'+(error.message || '未知错误'),
                    success: false,
                    details: []
                };
                this.logs.unshift(logEntry);
                this.$message.error(logEntry.result)
            } finally {
                this.checking = false;
            }
        },
        async bindBot() {
            if (!util.trim(this.form.token)) {
                this.bindResult = {
                    success: false,
                    message: '请输入有效的 GitHub Token',
                };
                return;
            }

            const userId = this.$route.params.userid;
            const projId = this.$route.params.projid;
            const repoId = this.$route.params.repoid;
            console.log('userId:', userId, 'projId:', projId, 'repoId:', repoId);
            console.log("api test imformation:" + 'userId:', userId, 'projId:', projId, 'repoId:', repoId)

            //axios.post('/api/bot/createBot', {
            axios.post('/api/bot/createBot', {
                userId: userId,
                projectId: projId,
                repoId: repoId,
                name: this.form.name, // username on github
                token: this.form.token,
            }).then((response) => {
                console.log("bot response: "+response.data.errcode + " "+response.data.message)
                if(response.data.errcode == 0) {
                    this.$message.success(response.data.message)
                    this.binding = true;
                    this.bindResult = {
                        success: true,
                        message: 'Bot 绑定成功！',
                    };
                    
                    this.form.token = ''; // 清空 token 输入
                    this.botBound = true;
                    // 保存绑定的 GitHub 用户名到 localStorage
                    localStorage.setItem('githubUsername', this.form.name);
                    
                    this.$message.success('绑定成功'); // 弹出成功提示
                } else {
                    this.bindResult = {
                        success: false,
                        message: response.data.message || '绑定失败，请检查 token 是否正确',
                    };
                }
            })
        },
        async changeBotStatus() {
            try {
                // 调用后端接口移除绑定的 Bot
                const userId = this.$route.params.userid;
                const projId = this.$route.params.projid;

                console.log("remove bot api data check:" + "userId:"+userId+" projectId:"+projId+" name:"+this.githubUsername)
                
                const response = await axios.post('/api/bot/disableBot', {
                    userId: userId,
                    projectId: projId,
                    repoId: this.$route.params.repoid,
                });

                console.log("disableBot response:", response.data.errcode + response.data.message)

                if(response.data.errcode == 0){
                    // 更新 UI 状态，表示 Bot 被禁用
                    this.bindResult = {
                        success: true,
                        message: this.botEnabled?'Bot 已成功禁用！':'Bot 已成功启用！',
                    };
                    this.botEnabled = !this.botEnabled;

                    this.$message.success(this.botEnabled?'Bot 已成功禁用！':'Bot 已成功启用！');
                } else {
                    console.log("disableBot result:" +response.data.errcode, response.data.message)
                    this.$message.error((this.botEnabled?'禁用':'启用')+' Bot 失败，请稍后再试');
                }
            } catch (error) {
                this.$message.error((this.botEnabled?'禁用':'启用')+' Bot 失败，请稍后再试');
            }
        },
        async fetchRules() {
            this.loadingRules = true;
            try {
                const response = await axios.post('/api/bot/getrules', {
                    repoId: this.$route.params.repoid
                });
                if(response.data.errcode == 0) {
                    this.rules = response.data.rules.map(rule => {
                        let parsedContent = {};
                        try {
                            parsedContent = JSON.parse(rule.content);
                        } catch (e) {
                            console.warn('解析规则 content 出错：', e);
                        }
                        return {
                            ...rule,
                            content: parsedContent
                        };
                    }) || [];
                    this.rules.forEach((rule, index) => {
                    console.log(`Rule ${index + 1}:`);
                    console.log("  type:", rule.type);
                    console.log("  name:", rule.name);
                    console.log("  default:", rule.default);
                    console.log("  content:", rule.content);
                    console.log("  description:", rule.content.description);
                    });
                } else {
                    this.$message.error('获取规则列表失败')
                    console.error(response.data.errcode + " " + response.data.message)
                }
            } catch (err) {
                this.$message.error('获取规则列表失败');
                console.error(err)
            } finally {
                this.loadingRules = true;
            }
        },
        async fetchLabels() {
            this.loadingLabels = true;
            try {
                const response = await axios.post('/api/bot/getlabels', {
                    repoId: this.$route.params.repoid
                });
                if(response.data.errcode == 0) {
                    this.labels = response.data.labels || []
                    console.log("fetchLabels labels: " + this.labels)
                } else {
                    this.$message.error('获取标签列表失败')
                    console.error(response.data.errcode + " " + response.data.message)
                }
            } catch (err) {
                this.$message.error('获取标签列表失败');
                console.error(err)
            } finally {
                this.loadingLabels = false;
            }
        },
        async fetchBotStatus() {
            this.loadingBotStatus = true;
            try {
                console.log("fetchBotStatus api data: "+this.$route.params.repoid, this.$route.params.projid)
                
                const responseExi = await axios.post('/api/bot/getexist', {
                    repoId: this.$route.params.repoid,
                    projectId: this.$route.params.projid,
                })

                if(responseExi.data.errcode == 0) {
                    const response = await axios.post('/api/bot/getactive', {
                        repoId: this.$route.params.repoid,
                        projectId: this.$route.params.projid,
                    });

                    if(response.data.errcode == 0) {
                        this.botBound = responseExi.data.data;
                        this.botEnabled = response.data.data;
                        console.log("fetchBotStatus result: " + this.botBound, this.botEnabled);
                    } else {
                        this.$message.error('获取bot使能状态失败')
                        console.error("fetchBotStatus-active:" +response.data.errcode, response.data.message)
                    }
                } else {
                    this.$message.error('获取bot存在状态失败')
                    console.error("fetchBotStatus-exist:" +response.data.errcode, response.data.message)
                }
                
            } catch (err) {
                this.$message.error('获取bot使能状态失败')
                console.error(err)
            } finally {
                this.loadingBotStatus = false;
            }
        },
    },
    
    mounted() {
        this.fetchBotStatus();
        this.fetchRules();
        this.fetchLabels();
    }
}
</script>
  
<style scoped>
    .text-ellipsis {
        display: inline-block;
        max-width: 100%;
        overflow: hidden;
        white-space: nowrap;
        text-overflow: ellipsis;
    }

    .sidebar {
        top: 20px;
        background-color: #fff;
        padding: 10px;
    }
    .el-menu-vertical-demo {
        border-right: none;
    }

    .el-button {
        background-color: #F6F8FA;
        border: 1px solid #E5E8EB;
    }
    .el-button-delete {
        background-color: #dc3545;
        color: white;
    }
    .assistant-button:hover {
        color: black;
        background-color: rgb(239, 242, 245) !important;
    }


    .project-bot {
        padding: 20px;
    }
    .header {
        margin-bottom: 20px;
    }
    .mb-2 {
        margin-bottom: 16px;
    }
    .box-card {
        margin: 10px 0;
    }
</style>
  