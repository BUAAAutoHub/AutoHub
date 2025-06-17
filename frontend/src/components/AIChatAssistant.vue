<template>
  <div
    class="ai-assistant"
    :style="assistantStyle"
    ref="assistant"
    @mouseenter="showTooltip = true"
    @mouseleave="showTooltip = false"
  >
    <!-- 图标部分 - 只有图标可拖动 -->
    <img
      src="@/assets/AIassistant.png"
      alt="AI助手"
      class="assistant-icon"
      @click="handleIconClick"
      @mousedown="startDrag"
    />
    
    <!-- 悬浮提示文字 -->
    <transition name="fade-tooltip">
      <div v-if="showTooltip && !isDragging" class="assistant-tooltip">
        AI小助手
      </div>
    </transition>

    <transition name="slide-up">
      <div 
        v-if="isChatOpen" 
        class="chat-container"
        @mousedown.stop  
      >
        <div class="chat-header">
          <v-icon color="primary">mdi-robot-happy</v-icon>
          <h3>AI 小助手</h3>
          <v-spacer></v-spacer>
          <v-btn icon @click="toggleChat">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </div>
        
        <div class="messages-container" ref="messages">
            <div v-for="(msg, i) in messages" :key="i" :class="['message', msg.sender]">
            <!-- 消息内容气泡 -->
            <div class="message-bubble">
                <div class="message-content">{{ msg.text }}</div>
            </div>
            
            <!-- 消息底部信息（来源+时间） -->
            <div class="message-footer">
                <!-- 来源标签 -->
                <div v-if="msg.sender === 'ai' && msg.sources.length" class="message-sources">
                <span v-for="(source, idx) in msg.sources" :key="idx" class="source-tag">
                    {{ source }}
                </span>
                </div>
                
                <!-- 时间 -->
                <div class="message-time">{{ msg.time }}</div>
            </div>
            </div>
        </div>
        
        <!-- 固定在底部的输入区域 -->
        <div class="input-container">
            <div class="input-wrapper">
                <v-text-field
                v-model="message"
                outlined
                dense
                placeholder="输入问题..."
                hide-details
                @keyup.enter="sendMessage"
                class="message-input"
                :disabled="isThinking"
                ></v-text-field>
                <v-btn 
                icon 
                color="primary" 
                @click="sendMessage"
                :disabled="isThinking || !message.trim()"
                class="send-btn"
                >
                <v-icon>mdi-send</v-icon>
                </v-btn>
            </div>
            </div>
      </div>
    </transition>
  </div>
</template>

<script>
import axios from "axios"
export default {
  name: 'AIChatAssistant',
  props: {
    currentProjectId: {
      type: Number,
      default: -1
    }
  },
  data() {
    return {
      position: { x: window.innerWidth - 100, y: window.innerHeight - 180 },
      isDragging: false,
      dragOffset: { x: 0, y: 0 },
      showTooltip: false,
      isChatOpen: false,
      message: '',
      messages: [],
      contextStr: '', // 新增上下文标识字段
      cur_mask: '000',
      isThinking: false, // 新增思考状态
      dragMoved: false, // 新增字段：记录是否真的发生了移动
      // 来源映射定义
      sourceMap: {
        '100': '当前项目代码',
        '010': '项目用户手册',
        '001': '项目知识库'
      }
    }
  },
  mounted() {
    window.addEventListener('mousemove', this.onDrag);
    window.addEventListener('mouseup', this.stopDrag);
    this.loadPosition();
  },
  beforeDestroy() {
    window.removeEventListener('mousemove', this.onDrag);
    window.removeEventListener('mouseup', this.stopDrag);
  },
  computed: {
    assistantStyle() {
      return {
        top: (this.position.y - 5) + 'px', // 关键修改：整体上移20px
        left: this.position.x + 'px'
      }
    }
  },
  methods: {
    startDrag(e) {
      this.isDragging = true;
      this.dragMoved = false; // 初始化为 false
      this.dragOffset = {
        x: e.clientX - this.position.x,
        y: e.clientY - this.position.y
      };
      e.preventDefault();
    },
    // 边界检测
    onDrag(e) {
        if (!this.isDragging) return;

        const newX = e.clientX - this.dragOffset.x;
        const newY = e.clientY - this.dragOffset.y;

        // 如果移动超过一定距离（比如 3 像素），认为是拖动
        if (Math.abs(newX - this.position.x) > 3 || Math.abs(newY - this.position.y) > 3) {
        this.dragMoved = true;
        }

        const maxX = window.innerWidth - this.$refs.assistant.offsetWidth;
        const maxY = window.innerHeight - this.$refs.assistant.offsetHeight;

        this.position = {
        x: Math.min(maxX, Math.max(0, newX)),
        y: Math.min(maxY, Math.max(0, newY))
        };
    },
    stopDrag() {
      if (this.isDragging) {
        this.isDragging = false;
        this.savePosition();
      }
    },
    savePosition() {
      localStorage.setItem('aiAssistantPosition', JSON.stringify(this.position));
    },
    loadPosition() {
      const saved = localStorage.getItem('aiAssistantPosition');
      if (saved) this.position = JSON.parse(saved);
    },
    toggleChat() {
      this.isChatOpen = !this.isChatOpen;
      if (!this.isChatOpen) {
        this.contextStr = ''; // 关闭时重置上下文
        this.cur_mask = '000';
        this.messages = [];    // 可选：清空消息记录
      }
      if (this.isChatOpen) {
        this.$nextTick(() => {
          this.scrollToBottom();
          this.$refs.input?.focus();
        });
      }
    },
    // 图标点击处理函数
    handleIconClick() {
        // 只有在非拖动且无移动时才切换聊天窗口
        if (!this.isDragging && !this.dragMoved) {
            this.toggleChat();
        }
    },
    async sendMessage() {
        // 验证消息有效性
        if (!this.message.trim() || this.message.length > 200 || this.isThinking) return;
        
        // 保存用户消息
        const userMessage = this.message;
        this.message = '';
        
        // 立即显示用户消息
        this.messages.push({
            text: userMessage,
            sender: 'user',
            time: new Date().toLocaleTimeString()
        });
        
        // 强制DOM更新
        await this.$nextTick();
        this.scrollToBottom();

        console.log("cur_mask0: ", this.cur_mask)
        try {
            // 设置思考状态
            this.isThinking = true;
            
            // 实际API调用
            const response = await axios.post('/api/ai/chat', {
                pid: this.currentProjectId,
                message: userMessage,
                context: this.contextStr,
                cur_mask: this.cur_mask
            });
            
            this.contextStr = response.data.context
            this.cur_mask = response.data.cur_mask
            console.log("cur_mask: ", this.cur_mask)

            // 解析来源信息
            const sources = this.parseSources(response.data.cur_mask);

            // 添加AI回复
            this.messages.push({
                text: response.data.reply || '收到空回复',
                sender: 'ai',
                time: new Date().toLocaleTimeString(),
                sources: sources  // 添加来源数组
            });
        } catch (error) {
            console.error('API错误:', error);
            this.messages.push({
            text: '您好，有什么可以帮助你？',
            sender: 'ai',
            time: new Date().toLocaleTimeString(),
            sources: []
            });
        } finally {
            // 无论成功失败，都解除思考状态
            this.isThinking = false;
        }
        
        // 最终滚动到底部
        await this.$nextTick();
        this.scrollToBottom();
    },
    scrollToBottom() {
        const container = this.$refs.messages;
        if (container) {
            container.scrollTop = container.scrollHeight;
        }
    },
    // 解析来源信息
    parseSources(maskValue) {
      if (!maskValue || maskValue === '000') return [];
      
      const sources = [];
      // 检查每个来源位
      if (maskValue[0] === '1') sources.push(this.sourceMap['100']);
      if (maskValue[1] === '1') sources.push(this.sourceMap['010']);
      if (maskValue[2] === '1') sources.push(this.sourceMap['001']);
      
      return sources;
    }
  }
}
</script>

<style scoped>
/* 基础助手样式 */
.ai-assistant {
  position: fixed;
  z-index: 10001;
  cursor: default; /* 整个组件默认光标 */
}

/* 只有图标可拖动 */
.assistant-icon {
  width: 60px;
  height: 60px;
  cursor: pointer;
  transition: transform 0.2s;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));
}

.assistant-icon:hover {
  transform: scale(1.1);
  filter: drop-shadow(0 2px 6px rgba(0, 0, 0, 0.3));
}

/* 过渡动画 */
.slide-fade-enter-active {
  transition: all 0.3s ease;
}
.slide-fade-leave-active {
  transition: all 0.3s cubic-bezier(1, 0.5, 0.8, 1);
}
.slide-fade-enter,
.slide-fade-leave-to {
  transform: translateY(20px);
  opacity: 0;
}

.slide-up-enter-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.slide-up-leave-active {
  transition: all 0.2s cubic-bezier(0.4, 0, 1, 1);
}
.slide-up-enter,
.slide-up-leave-to {
  transform: translateY(20px);
  opacity: 0;
}

/* 悬浮提示文字 */
.assistant-tooltip {
  position: absolute;
  bottom: -32px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  white-space: nowrap;
  pointer-events: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.assistant-tooltip::after {
  content: "";
  position: absolute;
  top: -5px;
  left: 50%;
  margin-left: -5px;
  border-width: 5px;
  border-style: solid;
  border-color: transparent transparent rgba(0, 0, 0, 0.8) transparent;
}

.fade-tooltip-enter-active,
.fade-tooltip-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.fade-tooltip-enter,
.fade-tooltip-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(5px);
}

/* 聊天窗口容器 - 不可拖动 */
.chat-container {
  position: absolute;
  right: 0;
  bottom: 70px;
  width: 320px;
  height: 400px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  cursor: default; /* 聊天框默认光标 */
}

/* 头部样式 */
.chat-header {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  background: #f5f7fa;
  border-bottom: 1px solid #e1e4e8;
  cursor: default; /* 头部不可拖动 */
}

.chat-header h3 {
  margin: 0 0 0 8px;
  font-size: 16px;
  font-weight: 600;
}

/* 消息区域 - 允许文本选择 */
.messages-container {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  background: #fafbfc;
  min-height: 0;
  user-select: text;
  -webkit-user-select: text;
  cursor: text; /* 消息区域文本光标 */
}

/* 滚动条美化 */
.messages-container::-webkit-scrollbar {
  width: 6px;
}
.messages-container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

/* 消息整体样式 */
.message {
  display: flex;
  flex-direction: column;
  margin-bottom: 12px;
  max-width: 85%;
  width: fit-content;
}

.message.user {
  margin-left: auto;
  min-width: 20%;
}

.message.ai {
  margin-right: auto;
  min-width: 20%;
}

/* 消息气泡样式 */
.message-bubble {
  padding: 10px 14px;
  border-radius: 18px;
  word-wrap: break-word;
  position: relative;
}

.message.user .message-bubble {
  align-self: flex-end;
  background: #007bff;
  color: white;
  border-bottom-right-radius: 4px;
}

.message.ai .message-bubble {
  align-self: flex-start;
  background: #e9ecef;
  color: #333;
  border-bottom-left-radius: 4px;
  /*border-left: 3px solid #1976d2;*/
}

/* 消息内容样式 - 允许文本选择 */
.message-content {
  font-size: 14px;
  line-height: 1.4;
  white-space: pre-wrap;
  word-wrap: break-word;
  word-break: break-word;
  overflow-wrap: anywhere;
  max-width: 100%;
  user-select: text;
  -webkit-user-select: text;
}

/* 消息底部信息 */
.message-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 6px;
  width: 100%;
}

/* 来源标签样式 - 允许文本选择 */
.message-sources {
  display: flex;
  gap: 6px;
  font-size: 0.7rem;
  color: #666;
  user-select: text;
  -webkit-user-select: text;
}

.source-tag {
  background-color: #e0f7fa;
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid #80deea;
  user-select: text;
  -webkit-user-select: text;
  cursor: pointer; /* 来源标签可点击 */
}

/* 时间样式 - 允许文本选择 */
.message-time {
  font-size: 0.7rem;
  color: #999;
  min-width: 70px;
  text-align: right;
  user-select: text;
  -webkit-user-select: text;
}

/* 输入区域样式 */
.input-container {
  padding: 12px;
  border-top: 1px solid #e1e4e8;
  background: white;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.message-input {
  flex: 1;
}

.send-btn {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  margin: 0;
  z-index: 2;
}

/* 确保所有文本内容都可以选择 */
.message-bubble *,
.message-footer *,
.source-tag *,
.message-time * {
  user-select: text !important;
  -webkit-user-select: text !important;
}

</style>