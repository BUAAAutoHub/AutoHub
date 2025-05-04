<template>
  <div
    class="ai-assistant"
    :style="assistantStyle"
    @mousedown="startDrag"
    ref="assistant"
    @mouseenter="showTooltip = true"
    @mouseleave="showTooltip = false"
  >
    <!-- 图标部分 -->
    <img
      src="@/assets/AIassistant.png"
      alt="AI助手"
      class="assistant-icon"
      @click="toggleChat"
    />
    
    <!-- 悬浮提示文字 -->
    <transition name="fade-tooltip">
      <div v-if="showTooltip && !isDragging" class="assistant-tooltip">
        AI小助手
      </div>
    </transition>

    <transition name="slide-up">
      <div v-if="isChatOpen" class="chat-container">
        <div class="chat-header">
          <v-icon color="primary">mdi-robot-happy</v-icon>
          <h3>AI 小助手</h3>
          <v-spacer></v-spacer>
          <v-btn icon @click="toggleChat">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </div>
        
        <div class="messages-container"  ref="messages">
          <div v-for="(msg, i) in messages" :key="i" :class="['message', msg.sender]">
            <div class="message-content">{{ msg.text }}</div>
            <div class="message-time">{{ msg.time }}</div>
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
                ></v-text-field>
                <v-btn 
                icon 
                color="primary" 
                @click="sendMessage"
                :disabled="!message.trim()"
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
      contextStr: '' // 新增上下文标识字段
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
      this.dragOffset = {
        x: e.clientX - this.position.x,
        y: e.clientY - this.position.y
      };
      e.preventDefault();
    },
    // 边界检测
    onDrag(e) {
        if (!this.isDragging) return;
        
        const maxX = window.innerWidth - this.$refs.assistant.offsetWidth;
        const maxY = window.innerHeight - this.$refs.assistant.offsetHeight;
        
        this.position = {
            x: Math.min(maxX, Math.max(0, e.clientX - this.dragOffset.x)),
            y: Math.min(maxY, Math.max(0, e.clientY - this.dragOffset.y))
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
        this.messages = [];    // 可选：清空消息记录
      }
      if (this.isChatOpen) {
        this.$nextTick(() => {
          this.scrollToBottom();
          this.$refs.input?.focus();
        });
      }
    },
    async sendMessage() {
        // 验证消息有效性
        if (!this.message.trim() || this.message.length > 200) return;
        
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

        try {
            // 实际API调用
            const response = await axios.post('/api/ai/chat', {
                pid: this.currentProjectId,
                message: userMessage,
                context: this.contextStr
            });

            this.contextStr = response.data.context

            // 添加AI回复
            this.messages.push({
                text: response.data.reply || '收到空回复',
                sender: 'ai',
                time: new Date().toLocaleTimeString()
            });
        } catch (error) {
            console.error('API错误:', error);
            //console.log('contextStr: ', this.contextStr);
            this.messages.push({
            //text: '抱歉，AI助手暂时无法响应',
            text: '您好，有什么可以帮助你？',
            sender: 'ai',
            time: new Date().toLocaleTimeString()
            });
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
        }
  }
}
</script>

<style scoped>
.ai-assistant {
  position: fixed;
  z-index: 10001;
}

.ai-assistant:active {
  cursor: grabbing;
}

.assistant-icon {
  width: 60px;
  height: 60px;
  cursor: pointer;
  transition: transform 0.2s;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));
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

/* 提示文字动画 */
.fade-tooltip-enter-active,
.fade-tooltip-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.fade-tooltip-enter,
.fade-tooltip-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(5px);
}

.assistant-icon:hover {
  transform: scale(1.1);
  filter: drop-shadow(0 2px 6px rgba(0, 0, 0, 0.3));
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

/* 聊天窗口容器 */
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
}

/* 头部样式 */
.chat-header {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  background: #f5f7fa;
  border-bottom: 1px solid #e1e4e8;
}

.chat-header h3 {
  margin: 0 0 0 8px;
  font-size: 16px;
  font-weight: 600;
}

/* 消息区域 */
.messages-container {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  background: #fafbfc;
  min-height: 0;
}

/* 消息气泡 */
.message {
  margin-bottom: 12px;
  max-width: 80%;
  width: fit-content;        /* 让气泡根据内容自适应 */
}

.message.user {
  margin-left: auto;
  min-width: 20%;           /* 防止过短消息 */
}

.message.ai {
  margin-right: auto;
  min-width: 20%;
}

.message-content {
  padding: 10px 14px;
  border-radius: 18px;
  font-size: 14px;
  line-height: 1.4;
  white-space: pre-wrap;       /* 保留换行符但自动换行 */
  word-wrap: break-word;      /* 允许长单词/URL换行 */
  word-break: break-word;     /* 更激进的长文本断行 */
  overflow-wrap: anywhere;    /* 确保任何字符位置都能换行 */
  max-width: 100%;           /* 防止超出容器 */
}

.message.user .message-content {
  background: #007bff;
  color: white;
  border-bottom-right-radius: 4px;
}

.message.ai .message-content {
  background: #e9ecef;
  color: #333;
  border-bottom-left-radius: 4px;
}

.message-time {
  font-size: 10px;
  color: #6c757d;
  text-align: right;
  margin-top: 4px;
}

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
  transform: translateY(-50%); /* 关键居中属性 */
  margin: 0;
  z-index: 2;
}

/* 动画效果 */
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

/* 滚动条美化 */
.messages-container::-webkit-scrollbar {
  width: 6px;
}
.messages-container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

</style>