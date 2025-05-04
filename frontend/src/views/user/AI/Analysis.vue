<template>
    <div>
        <!-- Loading 遮罩 -->
        <div v-if="loading" class="loading-overlay">
            <div class="spinner"></div>
            <p style="color: white; margin-top: 1rem;">加载中，请稍候...</p>
        </div>

        <!-- 页面主内容-->
        <div class="code-analysis-container" v-show="!loading">
            <h1>静态代码分析报告</h1>
        
            <!-- 概览卡片 -->
            <div class="overview-cards">
                <el-card class="metric-card" shadow="hover">
                <div class="metric-content">
                    <div class="metric-icon">
                    <i class="el-icon-document"></i>
                    </div>
                    <div class="metric-info">
                    <div class="metric-value">{{ metrics.files }}</div>
                    <div class="metric-label">文件数</div>
                    </div>
                </div>
                </el-card>
        
                <el-card class="metric-card" shadow="hover">
                <div class="metric-content">
                    <div class="metric-icon">
                    <i class="el-icon-warning-outline"></i>
                    </div>
                    <div class="metric-info">
                    <div class="metric-value">{{ metrics.bugs }}</div>
                    <div class="metric-label">Bug数</div>
                    </div>
                </div>
                </el-card>
        
                <el-card class="metric-card" shadow="hover">
                <div class="metric-content">
                    <div class="metric-icon">
                    <i class="el-icon-lock"></i>
                    </div>
                    <div class="metric-info">
                    <div class="metric-value">{{ metrics.vulnerabilities }}</div>
                    <div class="metric-label">漏洞数</div>
                    </div>
                </div>
                </el-card>
        
                <el-card class="metric-card" shadow="hover">
                <div class="metric-content">
                    <div class="metric-icon">
                    <i class="el-icon-s-opportunity"></i>
                    </div>
                    <div class="metric-info">
                    <div class="metric-value">{{ metrics.code_smells }}</div>
                    <div class="metric-label">代码异味</div>
                    </div>
                </div>
                </el-card>
            </div>
    
            <!-- 详细指标 -->
            <!-- <el-card class="detailed-metrics" shadow="never">
                <h2>详细指标</h2>
                <el-table :data="metricsTableData" style="width: 100%">
                <el-table-column prop="name" label="指标名称" width="180"></el-table-column>
                <el-table-column prop="value" label="值"></el-table-column>
                <el-table-column prop="description" label="说明"></el-table-column>
                </el-table>
            </el-card> -->
            <!-- 详细指标 -->
            <el-card class="detailed-metrics" shadow="never">
                <h2>详细指标</h2>
                <el-table 
                    :data="metricsTableData.filter(item => item.value !== undefined)" 
                    style="width: 100%"
                    empty-text="暂无详细指标数据"
                >
                    <el-table-column prop="name" label="指标名称" width="180"></el-table-column>
                    <el-table-column prop="value" label="值">
                    <template slot-scope="scope">
                        {{ scope.row.value || '无数据' }}
                    </template>
                    </el-table-column>
                    <el-table-column prop="description" label="说明"></el-table-column>
                </el-table>
            </el-card>
    
            <!-- 问题列表 -->
            <el-card class="issues-list" shadow="never">
                <h2>发现问题 ({{ issues.length }})</h2>
                <el-table :data="issues" style="width: 100%">
                <el-table-column prop="type" label="类型" width="120">
                    <template slot-scope="scope">
                    <el-tag :type="getIssueTypeTag(scope.row.type)">
                        {{ scope.row.type }}
                    </el-tag>
                    </template>
                </el-table-column>
                <el-table-column prop="severity" label="严重程度" width="120">
                    <template slot-scope="scope">
                        <el-tag :type="getSeverityTag(scope.row.severity)">
                            {{ scope.row.severity }}
                        </el-tag>
                    </template>
                </el-table-column>
                <el-table-column prop="file" label="所在行号" width="180">
                    <template slot-scope="scope">
                        <!-- <span class="file-link" @click="showFileLocation(scope.row)"> -->
                        <span >
                            {{ scope.row.line }}
                        </span>
                    </template>
                </el-table-column>
                <el-table-column prop="message" label="问题描述"></el-table-column>
                </el-table>
            </el-card>
        </div>
    </div>
  </template>
  
<script>
import axios from "axios";
import Cookies from 'js-cookie'
  export default {
    data() {
      return {
        loading: true,
        code: "",
        metrics: {
          coverage: "0.0",
          complexity: "2",
          reliability_rating: "1.0",
          code_smells: "0",
          duplicated_lines_density: "0.0",
          functions: "1",
          security_rating: "5.0",
          classes: "0",
          sqale_rating: "1.0",
          bugs: "0",
          ncloc: "60",
          files: "1",
          vulnerabilities: "1"
        },
        issues: [
          {
            type: "VULNERABILITY",
            message: "Make sure this SonarQube token gets revoked, changed, and removed from the code.",
            severity: "BLOCKER",
            line: 3,
            file: "your_code.py"
          }
        ]
      };
    },
    computed: {
      metricsTableData() {
        return [
          { name: "测试覆盖率", value: this.metrics.coverage==undefined ? undefined : this.metrics.coverage + "%", description: "代码被测试覆盖的比例" },
          { name: "复杂度", value: this.metrics.complexity, description: "代码的圈复杂度" },
          { name: "可靠性评级", value: this.metrics.reliability_rating, description: "1.0为最高评级" },
          { name: "重复代码率", value: this.metrics.duplicated_lines_density == undefined ? undefined : this.metrics.duplicated_lines_density + "%", description: "重复代码比例" },
          { name: "函数数量", value: this.metrics.functions, description: "代码中的函数/方法数量" },
          { name: "安全评级", value: this.metrics.security_rating, description: "5.0为最低评级" },
          { name: "类数量", value: this.metrics.classes, description: "代码中的类数量" },
          { name: "技术债务评级", value: this.metrics.sqale_rating, description: "1.0为最高评级" },
          { name: "代码行数", value: this.metrics.ncloc, description: "非注释代码行数" }
        ];
      }
    },
    methods: {
        getFromCookie() {
            // console.log('getFromCookie', Cookies.get('diag'))
            // if (Cookies.get('diag') !== undefined) {
            //     this.code = Cookies.get('diag')
            //     Cookies.remove('diag')
            // } else {
            //     this.code = ''
            // }
            console.log('getFromLocalStorage', localStorage.getItem('diag'))
            if(localStorage.getItem('diag') !== undefined) {
                this.code = localStorage.getItem('diag')
                localStorage.removeItem('diag')
            } else {
                this.code = ''
            }
        },
        async fetchInfo() {
            try {
                const response = await axios.post("/api/develop/sonarAnalysis", {
                    code: this.code
                });
                if(response.data.errcode == 0) {
                    this.metrics = response.data.data.metrics;
                    console.log("获取分析数据成功 metrics", response.data.data.metrics, response.data.data.metrics.bugs, this.metrics.bugs);
                    this.issues = response.data.data.issues;
                    console.log("获取分析数据成功 issues", response.data.data.issues);
                    this.$message({
                        type: 'success',
                        message: "获取分析数据成功"
                    });
                } else {
                    this.$message({
                        type: 'error',
                        message: "获取分析数据失败+ " + response.data.errcode + " " + response.data.message
                    });
                }
            } catch (error) {
                console.error("获取分析数据失败:", error);
            }
        },
        getIssueTypeTag(type) {
            const map = {
            "VULNERABILITY": "danger",
            "BUG": "warning",
            "CODE_SMELL": "info"
            };
            return map[type] || "";
        },
        getSeverityTag(severity) {
            const map = {
            "BLOCKER": "danger",
            "CRITICAL": "warning",
            "MAJOR": "",
            "MINOR": "info",
            "INFO": "success"
            };
            return map[severity] || "";
        },
        showFileLocation(issue) {
            // 在实际应用中，这里可以跳转到代码编辑器或显示代码片段
            this.$message.info(`定位到文件: ${issue.file} 第 ${issue.line} 行`);
        }
    },
    async mounted() {
        this.loading = true;
        this.getFromCookie();
        await this.fetchInfo();
        this.loading = false;
    }
  };
  </script>
  
  <style scoped>
  .code-analysis-container {
    padding: 20px;
    max-width: 1200px;
    margin: 0 auto;
  }
  
  h1 {
    color: #303133;
    margin-bottom: 20px;
  }
  
  h2 {
    color: #606266;
    margin-bottom: 15px;
  }
  
  .overview-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
  }
  
  .metric-card {
    border-radius: 8px;
  }
  
  .metric-content {
    display: flex;
    align-items: center;
  }
  
  .metric-icon {
    font-size: 24px;
    margin-right: 15px;
    color: #409EFF;
  }
  
  .metric-value {
    font-size: 24px;
    font-weight: bold;
    color: #303133;
  }
  
  .metric-label {
    color: #909399;
    font-size: 14px;
  }
  
  .detailed-metrics, .issues-list {
    margin-bottom: 30px;
    border-radius: 8px;
  }
  
  .file-link {
    color: #409EFF;
    cursor: pointer;
    text-decoration: underline;
  }
  
  .file-link:hover {
    color: #66b1ff;
  }

  /* loading */
  .loading-overlay {
  position: fixed;
  z-index: 10000;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(30, 30, 30, 0.8);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.spinner {
  border: 8px solid #f3f3f3;
  border-top: 8px solid #3f51b5;
  border-radius: 50%;
  width: 60px;
  height: 60px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
  </style>