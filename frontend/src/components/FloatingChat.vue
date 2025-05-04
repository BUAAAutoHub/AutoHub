<template>
    <div class="floating-assistant">
      <div class="icon-wrapper">
        <!-- 使用透明背景的PNG图标 -->
        <img 
          src="@/assets/Chats.png" 
          alt="聊天"
          class="assistant-icon"
          @mouseover="showTooltip = true"
          @mouseleave="showTooltip = false"
          @click="openChatWindow"
        />
        <transition name="fade">
          <div v-if="showTooltip" class="tooltip">快速聊天</div>
        </transition>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    inject: ['selectedProj'], // 注入当前项目
    data() {
      return {
        showTooltip: false
      }
    },
    methods: {
        openChatWindow() {
            const route = this.$route;
            const isAllTask = route.path.includes('/allTask');
            const isNewPR = route.path.includes('/newPR');
            const isBranchDetail = route.path.includes('/dev'); 

            // 生成智能名称规则
            let defaultName = '';
            let source = '';
            if (isAllTask) {
                defaultName = this.generateTaskChatName();
                source = 'alltask';
            } else if (isNewPR) {
                defaultName = this.generatePRChatName();
                source = 'newpr';
            } else if (isBranchDetail) { // 分支详情页逻辑
                defaultName = this.generateBranchChatName();
                source = 'branch';
            }

            // 路由跳转参数
            const query = {
                from: 'float',
                _t: Date.now()
            };

            // 仅在有智能名称时添加参数
            if (defaultName) {
                Object.assign(query, {
                    projectId: this.selectedProj?.projectId,
                    defaultGroupName: encodeURIComponent(defaultName),
                    source: source // 使用动态source值
                })
            }

            this.$router.push({
                path: '/user/chat',
                query
            });
            },

            // 为allTask界面生成名称
            generateTaskChatName() {
                const baseName = this.selectedProj?.projectName || '当前项目'
                const cleanName = baseName
                    .replace(/[^a-zA-Z0-9\u4e00-\u9fa5]/g, '')
                    .substring(0, 10)
                
                const dateStr = new Date()
                    .toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' })
                    .replace(/\//g, '')
                
                return `${cleanName}_projectDiscussion_${dateStr}`
            },

            // 为newPR界面生成名称（需在PR界面添加路由判断）
            generatePRChatName() {
                const baseName = this.selectedProj?.projectName || '当前项目'
                // const prTitle = this.$route.query.title?.substring(0, 15) || '代码评审'
                // const branch = this.$route.query.branch ? 
                //     `_${this.$route.query.branch.substring(0, 10)}` : ''
                
                const dateStr = new Date()
                    .toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' })
                    .replace(/\//g, '')
                
                return `PR_${baseName}_${dateStr}`
            },
            generateBranchChatName() {
                const baseName = this.selectedProj?.projectName || '当前项目';
                const branchName = this.$route.params.branchname || '分支';
                
                // 清理特殊字符并截短
                const cleanProjName = baseName
                    .replace(/[^a-zA-Z0-9\u4e00-\u9fa5]/g, '')
                const cleanBranchName = branchName
                    .replace(/[^a-zA-Z0-9\u4e00-\u9fa5]/g, '')

                // 生成日期字符串
                const dateStr = new Date()
                    .toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' })
                    .replace(/\//g, '');

                return `${cleanProjName}_${cleanBranchName}_branchDiscussion_${dateStr}`;
            },

            // 优化路由判断方法
            isAllTaskRoute() {
                return this.$route.matched.some(route => 
                    route.path.includes('/allTask')
                )
            }
        }
  }
  </script>
  
  <style scoped>
  .floating-assistant {
    position: fixed;
    bottom: 30px;
    right: 30px;
    z-index: 1000;
  }
  
  .image-container {
    position: relative;
    display: inline-block;
  }
  
  .assistant-icon {
    width: 60px;
    height: 60px;
    cursor: pointer;
    transition: all 0.3s ease;
    border-radius: 8px; /* 可选轻微圆角 */
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }
  
  .assistant-icon:hover {
    transform: scale(1.1);
    filter: brightness(1.1);
  }
  
  .tooltip {
    position: absolute;
    bottom: -30px;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(0, 0, 0, 0.8);
    color: white;
    padding: 6px 12px;
    border-radius: 4px;
    font-size: 12px;
    white-space: nowrap;
    pointer-events: none;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
  
  /* 淡入淡出动画*/
  .fade-enter-active, .fade-leave-active {
    transition: opacity 0.2s;
  }
  .fade-enter, .fade-leave-to {
    opacity: 0;
  } 
  </style>