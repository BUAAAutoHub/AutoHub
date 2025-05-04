<template>

    <!--style="display: flex; height: 100vh;"-->
    <div class="overflow-y-hidden collab-container font-size-14" style="display: flex;">
      <div class="user-list big-card-shadow">
        <div class="collab-header padding-10">
            <p class="margin-0">协作详情</p>
        </div>
        <div class="collab-content padding-10">
            <button
            v-if="isHost"
            class="save-button font-weight-500"
            @click="handleSaveCodeBeforeClose"
            title="保存代码"
            >保存代码</button>
            <div style="height: 0.5rem;"></div>
            <div class="guide">
                <div class="guide-header">
                    <p><h3 style="font-size: 20px;" class="font-weight-500">协作指南</h3></p>
                    <p class="font-size-16">1. 你可以在这里进行代码协作编辑。</p>
                    <p class="font-size-16">2. 主持人有邀请成员、保存代码和关闭房间的权限。</p>
                    <p class="font-size-16">3. 成员只能进行代码编辑。</p>
                </div>
            </div>
            <div class="user-list-header">
                <h3 style="font-size: 20px;" class="font-weight-500">在线用户</h3> 
                <button 
                v-if="isHost"
                class="invite-button"
                @click="copyInviteUrl"
                title="邀请成员"
                >+</button>
            </div>
            <ul>
                <li
                    v-for="(user, id) in users"
                    :key="id"
                    class="font-size-16 font-weight-500"
                    :style="{ color: user.color, marginBottom: '5px' }"
                >
                    {{ user.name }} - {{ user.isHost ? '房主' : '成员' }} {{ user.name === nickname ? '(我)' : '' }}
            </li>
            </ul>
        </div>
      </div>
      <div class="editor big-card-shadow">
        <div class="collab-header padding-10">
            <p class="margin-0">代码</p>
        </div>
        <div class="editor-instance">
            <YjsEditor 
            ref="yjsEditor"
            :roomName="roomName" 
            :initialCode="initialCode" 
            :isHost="isHost"
            :userName=nickname
            @update-users="handleUpdateUsers" 
            />
        </div>
      </div>
      <div class="code-assistant big-card-shadow">
        <div class="collab-header padding-10">
            <p class="margin-0">代码助手</p>
        </div>
            <v-card elevation="0" class="overflow-y-hidden overflow-x-hidden no-radius no-border code-assistant-content">
              
                <v-divider></v-divider>
  
                <v-card-title>人机协同</v-card-title>
                <v-card-text>AutoHub也很乐意对您选中的代码，或是整个文件进行代码优化</v-card-text>
                <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn width="" outlined @click="diagSelected"><v-icon>mdi-code-braces</v-icon>对选中代码</v-btn>
                </v-card-actions>
                <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn width="" outlined @click="diagWholeFile"><v-icon>mdi-code-braces</v-icon>对整个文件</v-btn>
                </v-card-actions>
  
                <v-divider></v-divider>
  
                <v-card-title>静态分析</v-card-title>
                <v-card-text>AutoHub帮助您管理源代码的质量，快速定位Bug、漏洞以及不优雅的地方</v-card-text>
                <!-- <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn width="" outlined @click="analySelected"><v-icon>mdi-code-braces</v-icon>对选中代码</v-btn>
                </v-card-actions> -->
                <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn width="" outlined @click="analyWholeFile"><v-icon>mdi-magnify-scan</v-icon>对整个文件</v-btn>
                </v-card-actions>
  
                <v-divider></v-divider>
  
                <v-card-title>单元测试</v-card-title>
                <v-card-text>AutoHub可以对您选中的代码，或是整个文件生成单元测试</v-card-text>
                <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn width="" outlined @click="unitTestSelected"><v-icon>mdi-check</v-icon>对选中代码</v-btn>
                </v-card-actions>
                <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn width="" outlined @click="unitTestWholeFile"><v-icon>mdi-check</v-icon>对整个文件</v-btn>
                </v-card-actions>
              <!-- <v-row style="height: 5rem"></v-row> -->
            </v-card>
      </div>
    </div>
  </template>
  
  <script>
  import YjsEditor from './YjsEditor.vue'
  import Cookies from 'js-cookie'
  
  export default {
    components: { YjsEditor },
    data() {
      return {
        users: {},
        roomName: '',
        initialCode: '',
        isHost: false,
        inviteUrl: '',
        nickname: '用户',
      }
    },
    methods: {
        // 获取 YjsEditor 的内容
        getEditorContent() {
            const editorContent = this.$refs.yjsEditor.getEditorContent();  // 调用 YjsEditor 组件的 getEditorContent 方法
            console.log('编辑器内容:', editorContent);
            return editorContent;
        },
        handleBeforeUnload(event) {
        // 只有在主持人时才会弹出保存提示框
            if (this.isHost) {
                // 设置浏览器默认的提示框（此时 confirm 的逻辑不会生效）
                event.returnValue = '你是否希望保存代码并关闭房间？';
  
                // 这里可以处理保存代码的逻辑（但需要在用户确认后进行）
                window.addEventListener('unload', this.handleSaveCodeBeforeClose);
            }
        },
        handleSaveCodeBeforeClose() {
            // 如果用户关闭了页面，保存代码到剪贴板
            const editorContent = this.getEditorContent(); 
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(editorContent).then(() => {
                    console.log('代码已保存到剪贴板！');
                }).catch(err => {
                    console.error('保存代码失败：', err);
                });
            } else {
                // 兼容不支持 clipboard API 的浏览器
                const textarea = document.createElement('textarea');
                textarea.value = editorContent;
                textarea.style.position = 'fixed'; // 避免页面跳动
                textarea.style.opacity = '0';
                document.body.appendChild(textarea);
                textarea.select();
                try {
                    document.execCommand('copy');
                    alert('代码已保存到剪贴板！');
                } catch (err) {
                    alert('保存代码失败：', err);
                }
                document.body.removeChild(textarea);
            }
        },
        handleUpdateUsers(users) {
            console.log('Updating users:', users)
            this.users = users
            const isHostStillInRoom = Object.values(users).some(user => user.isHost)
            if (!isHostStillInRoom) {
                alert('房主已离开，房间将关闭。');
                localStorage.removeItem(this.roomName);
                this.$router.push({ name: 'dev' });
            }
        },
        copyInviteUrl() {
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(this.inviteUrl).then(() => {
                alert('链接已复制！' + this.inviteUrl);
                }).catch(err => {
                console.error('复制失败:', err);
                alert('复制失败，请手动复制链接：' + this.inviteUrl);
                });
            } else {
                // 兼容不支持 clipboard API 的浏览器
                const textarea = document.createElement('textarea');
                textarea.value = this.inviteUrl;
                textarea.style.position = 'fixed'; // 避免页面跳动
                textarea.style.opacity = '0';
                document.body.appendChild(textarea);
                textarea.select();
                try {
                    document.execCommand('copy');
                    alert('链接已复制！（兼容模式）' + this.inviteUrl);
                } catch (err) {
                    alert('复制失败，请手动复制链接：' + this.inviteUrl);
                }
                document.body.removeChild(textarea);
            }
        },
  
        analyWholeFile() {
            const fileContent = this.$refs.yjsEditor.getEditorContent();  // 调用 YjsEditor 组件的 getEditorContent 方法
            if (fileContent.length <= 10) {
                this.$message({
                    type: 'error',
                    message: '喵呜~ 代码太短了啦 (ฅ´ω`ฅ) 再多写一点点好不好'
                })
                return
            }
            //如果文件长度大于Cookie最长长度，就不诊断了
            // if (fileContent.length > 4096) {
            //     this.$message({
            //         type: 'error',
            //         message: '文件太长了，AI会罢工的！'
            //     })
            //     return
            // }
            // Cookies.set('diag', fileContent)
            // console.log('cookies content:', Cookies.get('diag'))
            localStorage.setItem('diag', fileContent)
            console.log('localStorage content:', localStorage.getItem('diag'))
            window.open('/user/ai/analysis', '_blank')
        },
  
        diagSelected() {
            const selectedText = this.$refs.yjsEditor.getEditorSelection();  
            console.log(selectedText.length, 'diag选中的文本:', selectedText);
  
            //如果文件长度大于Cookie最长长度，就不诊断了
            if (selectedText.length > 4096) {
                this.$message({
                type: 'error',
                message: '文件太长了，AI会罢工的！'
                })
                return
            }
            if (selectedText.length <= 10) {
                this.$message({
                type: 'error',
                message: '喵呜~ 代码太短了啦 (ฅ´ω`ฅ) 再多写一点好不好'
                })
                return
            }
            Cookies.set('diag', selectedText)
            window.open('/user/ai/diagnosis', '_blank')
        },
        diagWholeFile() {
            const fileContent = this.$refs.yjsEditor.getEditorContent();  // 调用 YjsEditor 组件的 getEditorContent 方法
            //如果文件长度大于Cookie最长长度，就不诊断了
            if (fileContent.length > 4096) {
                this.$message({
                    type: 'error',
                    message: '文件太长了，AI会罢工的！'
                })
                return
            }
            Cookies.set('diag', fileContent)
            window.open('/user/ai/diagnosis', '_blank')
        },
        unitTestSelected() {
            const selectedText = this.$refs.yjsEditor.getEditorSelection();  
            console.log('选中的文本:', selectedText);
  
            //如果文件长度大于Cookie最长长度，就不诊断了
            if (selectedText.length > 4096) {
                this.$message({
                type: 'error',
                message: '文件太长了，AI会罢工的！'
                })
                return
            }
            if (selectedText.length <= 10) {
                this.$message({
                    type: 'error',
                    message: '代码这么短，怎么生成嘛'
                })
                return
            }
            Cookies.set('diag', selectedText)
            console.log('cookies content:', Cookies.get('diag'))
            window.open('/user/ai/testdata', '_blank')
        },
        unitTestWholeFile() {
            const fileContent = this.$refs.yjsEditor.getEditorContent();  // 调用 YjsEditor 组件的 getEditorContent 方法
            console.log('文件内容:', fileContent);
            //如果文件长度大于Cookie最长长度，就不诊断了
            if (fileContent.length > 4096) {
                this.$message({
                    type: 'error',
                    message: '文件太长了，AI会罢工的！'
                })
                return
            }
            // Cookies.set('diag', fileContent)
            // console.log('testgetFromCookie1', Cookies.get('diag'))
            // window.open('/user/ai/testdata', '_blank')
            Cookies.set('diag', fileContent, { path: '/' });
            console.log('Cookie 写入中...');
  
            setTimeout(() => {
                console.log('testgetFromCookie1写入', Cookies.get('diag'))
                console.log('Cookie 写入后尝试打开窗口...');
                window.open('/user/ai/testdata', '_blank');
            }, 200);  // 延迟 200 毫秒左右即可
  
        },
  
    },
    created() {
      console.log('Route params:', this.$route.params)
      this.roomName = this.$route.query.roomName || 'default-room'
      console.log('this.$route.query.host:', this.$route.query.host)
      this.isHost = this.$route.query.host === 'true'
      console.log('Room name:', this.roomName)
      console.log('Is host:', this.isHost)
      this.initialCode = sessionStorage.getItem('fileContent') || ''
      console.log('Initial code in Room:', this.initialCode)
  
      const curreentUrl = window.location.href
      if(curreentUrl.endsWith('&host=true')) {
        this.inviteUrl = curreentUrl.replace('&host=true', '')
      } else {
        this.inviteUrl = curreentUrl
      }
  
      // 弹出昵称输入框
        let nickname = ''
        while (true) {
            nickname = prompt('请输入你的昵称（不超过8个字符，不能有空格）')
            if (!nickname) {
                alert('昵称不能为空，请重新输入。')
                continue
            }
            if (nickname.length > 8) {
                alert('昵称不能超过8个字符，请重新输入。')
                continue
            }
            if (/\s/.test(nickname)) {
                alert('昵称不能包含空格，请重新输入。')
                continue
            }
            break
        }
  
        this.nickname = nickname
  
        window.addEventListener('beforeunload', this.handleBeforeUnload)
    },
    beforeDestroy() {
        console.log('Cleaning up before destroy')
        window.removeEventListener('beforeunload', this.handleBeforeUnload)
        localStorage.removeItem(this.roomName);
    },
  }
  </script>
  
  <style scoped>
  
  .v-card__title {
    padding-top: 8px;
    padding-bottom: 8px;
  }
  
  .no-radius {
    border-radius: 0 !important;
  }
  
  .no-border {
    border: none !important;
  }
  
  .padding-10 {
    padding: 10px;
  }
  
  .margin-0 {
    margin: 0;
  }
  
  .big-card-shadow {
    box-shadow: -2px 0 5px rgba(0, 0, 0, 0.05);
  }
  
  .font-weight-500 {
    font-weight: 500;
  }
  
  .font-size-14 {
    font-size: 14px;
  }
  
  .collab-container {
    height: 100vh;
    background-color: rgb(240, 240, 240);
    /* todo */
    flex-shrink: 0;
  }
  
  .overflow-y-hidden {
    overflow-y: hidden;
  }
  
  /* Add any styles you need here */
  .collab-header {
    background-color: rgb(250, 250, 250);
    width: 100%;
    padding: 5px 10px;
    font-weight: 500;
    display: flex;
    flex-shrink: 0;
    position: sticky;
  }
  
  .collab-content {
    background-color: rgb(255, 255, 255);
  }
  
  .user-list {
    width: 240px; 
    border-radius: 8px;
    margin: 8px;
    background-color: rgb(255, 255, 255);
  }
  
  .user-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  }
  
  .save-button {
    background-color: #2196F3;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 10px; /* 调整为更合适的内边距 */
    cursor: pointer;
    width: calc(100% - 10px); /* 宽度占满父容器，减去边距 */
    margin: 5px; /* 留出一点空隙 */
    text-align: center;
    display: inline-flex; /* 使用flex布局来居中文本 */
    justify-content: center; /* 使文字水平居中 */
    align-items: center; /* 使文字垂直居中 */
  }
  
  
  .invite-button {
  background-color: #2196F3;
  color: white;
  border: none;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  font-weight: bold;
  cursor: pointer;
  font-size: 16px;
  line-height: 20px;
  }
  
  .invite-button:hover {
  background-color: #2196F3;
  }
  
  /* .editor {
    flex: 1;
    padding: 10px; 
    overflow: auto;
  } */
  
  .editor {
  flex: 1;
  position: relative;
  /* padding: 10px; */
  overflow: hidden; /* 防止子元素超出 */
  display: flex;
  flex-direction: column;
  background-color: rgb(255, 255, 255);
  margin: 8px;
  border-radius: 8px;
  /* todo */
  box-sizing: border-box;
  }
  
  .editor-instance {
    /* position: absolute;
    top: 31px;
    width: 100%;
    flex: 1;
    overflow: auto; */
    position: absolute;
    top: 31px;
    width: 100%;
    flex: 1;
  }
  
  .code-assistant {
    width: 300px; 
    overflow-y: auto;
    margin: 8px;
    border-radius: 8px;
    display: flex;
    flex-direction: column;
    /* height: 100%; */
  }
  
  .code-assistant-content {
    flex: 1;
    background-color: rgb(255, 255, 255);
  }
  
  </style>
  