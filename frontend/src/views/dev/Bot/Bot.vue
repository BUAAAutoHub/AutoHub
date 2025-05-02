<template>
    <el-row :gutter="20" class="layout-container">
        <!-- 左侧导航 -->
        <el-col :span="4">
            <div class="sidebar">
                <el-menu default-active="bot" class="el-menu-vertical-demo" @select="handleNav">
                    <el-menu-item index="bot">Bot 绑定</el-menu-item>
                    <el-menu-item index="rules">规则管理</el-menu-item>
                    <el-menu-item index="labels">标签管理</el-menu-item>
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
                        <el-button type="primary" @click="checkProject" :loading="checking">🔍 检查项目</el-button>
                    </el-row>
                
                    <!-- 未绑定 Bot 提示 -->
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
                        <el-form :inline="true" :model="form">
                        <el-form-item label="GitHub Token">
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
                        <el-form-item>
                            <el-button
                            type="primary"
                            :loading="binding"
                            @click="bindBot"
                            >
                            绑定
                            </el-button>
                        </el-form-item>
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
                        <el-button style="float: right;" type="primary" size="small" @click="addRule">➕ 新增规则</el-button>
                    </div>

                    <el-table :data="rules" stripe>
                        <el-table-column label="Label" width="120">
                            <template slot-scope="scope">
                                <el-tag :style="{ backgroundColor: scope.row.color, color: '#fff' }">
                                {{ scope.row.label }}
                                </el-tag>
                            </template>
                        </el-table-column>
                        <el-table-column label="Prompt内容" prop="prompt"></el-table-column>
                        <el-table-column label="操作" width="180">
                            <template slot-scope="scope">
                                <el-button size="mini" @click="editRule(scope.$index)" >编辑</el-button>
                                <el-button size="mini" type="danger" @click="deleteRule(scope.$index)">删除</el-button>
                            </template>
                        </el-table-column>
                    </el-table>
                    </el-card>

                    <!-- Label 区块 -->
                    <el-card class="box-card" id="labels-section">
                        <div slot="header" class="clearfix">
                        <span>标签管理</span>
                        <el-button style="float: right;" type="primary" size="small" @click="addLabel">➕ 新增标签</el-button>
                        </div>
                
                        <el-table :data="labels" stripe>
                            <el-table-column label="Label" width="120">
                                <template slot-scope="scope">
                                <el-tag :style="{ backgroundColor: scope.row.color, color: '#fff' }">
                                    {{ scope.row.label }}
                                </el-tag>
                                </template>
                            </el-table-column>
                            <el-table-column label="Prompt内容" prop="prompt"></el-table-column>
                            <el-table-column label="操作" width="180">
                                <template slot-scope="scope">
                                <el-button size="mini" @click="editLabel(scope.$index)">编辑</el-button>
                                <el-button size="mini" type="danger" @click="deleteLabel(scope.$index)">删除</el-button>
                                </template>
                            </el-table-column>
                        </el-table>
                    </el-card>

                    <!-- 添加/编辑 Rule 弹窗 -->
                    <el-dialog :title="editIndex === null ? '新增规则' : '编辑规则'" :visible.sync="ruleModalVisible">
                        <el-form :model="currentRule" label-width="80px">
                            <el-form-item label="Prompt">
                                <el-input type="textarea" v-model="currentRule.prompt" rows="3"></el-input>
                            </el-form-item>
                            <el-form-item label="Label">
                                <el-input v-model="currentRule.label"></el-input>
                            </el-form-item>
                            <el-form-item label="颜色">
                                <el-color-picker v-model="currentRule.color"></el-color-picker>
                            </el-form-item>
                        </el-form>
                        <div slot="footer">
                            <el-button @click="ruleModalVisible = false">取消</el-button>
                            <el-button type="primary" @click="saveRule">保存</el-button>
                        </div>
                    </el-dialog>
                
                    <!-- 添加/编辑 Label 弹窗 -->
                    <el-dialog :title="editIndex === null ? '新增标签' : '编辑标签'" :visible.sync="labelModalVisible">
                        <el-form :model="currentLabel" label-width="80px">
                            <el-form-item label="Prompt">
                                <el-input type="textarea" v-model="currentLabel.prompt" rows="3"></el-input>
                            </el-form-item>
                                <el-form-item label="Label">
                            <el-input v-model="currentLabel.label"></el-input>
                            </el-form-item>
                            <el-form-item label="颜色">
                                <el-color-picker v-model="currentLabel.color"></el-color-picker>
                            </el-form-item>
                        </el-form>
                        <div slot="footer">
                            <el-button @click="labelModalVisible = false">取消</el-button>
                            <el-button type="primary" @click="saveLabel">保存</el-button>
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
        botToken: '',
        showBindModal: false,
        rules: [],
        ruleModalVisible: false,
        currentRule: { prompt: '', label: '', color: '#409EFF' },
        labels: [],
        labelModalVisible: false,
        currentLabel: { prompt: '', label: '', color: '#409EFF' },
        editIndex: null,
        checking: false,

        form: {
            name: '',
            token: '',
        },
        binding: false,
        bindResult: {
            success: false,
            message: '',
        },
      }
    },
    methods: {
        handleNav(index) {
            const sectionMap = {
                bot: 'bot-section',
                rules: 'rules-section',
                labels: 'labels-section'
            }
            const targetId = sectionMap[index]
            const el = document.getElementById(targetId)
            if (el) {
                el.scrollIntoView({ behavior: 'smooth', block: 'start' })
            }
        },
        addLabel() {
            this.editIndex = null
            this.currentLabel = { prompt: '', label: '', color: '#409EFF' }
            this.labelModalVisible = true
        },
        editLabel(index) {
            this.editIndex = index
            this.currentLabel = { ...this.labels[index] }
            this.labelModalVisible = true
        },
        saveLabel() {
            if (this.editIndex === null) {
            this.labels.push({ ...this.currentLabel })
            } else {
            this.$set(this.labels, this.editIndex, { ...this.currentLabel })
            }
            this.labelModalVisible = false
        },
        deleteLabel(index) {
            this.labels.splice(index, 1)
        },
      addRule() {
        this.editIndex = null
        this.currentRule = { prompt: '', label: '', color: '#409EFF' }
        this.ruleModalVisible = true
      },
      editRule(index) {
        this.editIndex = index
        this.currentRule = { ...this.rules[index] }
        this.ruleModalVisible = true
      },
      saveRule() {
        if (this.editIndex === null) {
          this.rules.push({ ...this.currentRule })
        } else {
          this.$set(this.rules, this.editIndex, { ...this.currentRule })
        }
        this.ruleModalVisible = false
      },
      deleteRule(index) {
        this.rules.splice(index, 1)
      },
      checkProject() {
        this.checking = true
        // 模拟后端请求
        setTimeout(() => {
          this.$message.success('检查完成，未发现问题！')
          this.checking = false
        }, 1500)
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
                this.$message.success('绑定成功'); // 弹出成功提示
                this.botBound = true;
            } else {
                this.bindResult = {
                    success: false,
                    message: response.data.message || '绑定失败，请检查 token 是否正确',
                };
            }
        })


        // try {
        //     // 模拟调用后端 API 进行绑定
        //     const response = await this.$axios.post('/api/bot/bind', {
        //     token: this.form.token,
        //     });

        //     if (response.data.success) {
        //     this.bindResult = {
        //         success: true,
        //         message: 'Bot 绑定成功！',
        //     };
        //     } else {
        //     this.bindResult = {
        //         success: false,
        //         message: response.data.message || '绑定失败，请检查 token 是否正确',
        //     };
        //     }
        // } catch (error) {
        //     this.bindResult = {
        //     success: false,
        //     message: '网络错误或服务器异常',
        //     };
        // } finally {
        //     this.binding = false;
        // }
    }
    }
  }
  </script>
  
<style scoped>
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
  