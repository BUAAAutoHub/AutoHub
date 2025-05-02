<template> 
    <div class="yjs-editor">
        <div class="editor-toolbar">
            <select v-model="selectedLanguage" @change="changeLanguage" class="language-selector">
            <option v-for="lang in languages" :key="lang.value" :value="lang.value">
                {{ lang.label }}
            </option>
            </select>
        </div>
        <div ref="editorContainer" class="editor-container"></div>
    </div>
  </template>
  
  
<script>
import CodeMirror from 'codemirror'
import * as Y from 'yjs'
import { WebsocketProvider } from 'y-websocket'
import { CodemirrorBinding } from 'y-codemirror'
// 引入语言 mode
import 'codemirror/mode/javascript/javascript.js'
import 'codemirror/mode/python/python.js'
import 'codemirror/mode/markdown/markdown.js'
import 'codemirror/mode/htmlmixed/htmlmixed.js'
import 'codemirror/mode/xml/xml.js'
import 'codemirror/mode/css/css.js'
import 'codemirror/mode/clike/clike.js' // Java/C/C++

// 自动补全插件
import 'codemirror/addon/hint/show-hint.js'
import 'codemirror/addon/hint/show-hint.css'
//import 'codemirror/addon/hint/javascript-hint.js'

  
  export default {
    props: {
        userName: {
            type: String,
            default: '用户'
        },
        roomName: {
            type: String,
            required: true
        },
        initialCode: {
            type: String,
            default: ''
        },
        isHost: {
            type: Boolean,
            default: false
        }
    },
    data() {
      return {
        provider: null,
        ydoc: null,
        ytext: null,
        yMap: null,
        editor: null,
        connectionStatus: 'Disconnect',
        selectedLanguage: 'javascript',
        languages: [
            { label: 'JavaScript', value: 'javascript' },
            { label: 'Python', value: 'python' },
            { label: 'Markdown', value: 'markdown' },
            { label: 'HTML', value: 'htmlmixed' },
            { label: 'CSS', value: 'css' },
            { label: 'Java', value: 'text/x-java' },
            { label: 'C++', value: 'text/x-c++src' },
        ],
      }
    },
    created() {
        console.log('Room name:', this.roomName)
        console.log('Initial Code:', this.initialCode)
        console.log('Is Host:', this.isHost)
    },
    mounted() {
        this.$nextTick(() => {
            this.initEditor()
        })
    },
    beforeDestroy() {
      if (this.provider) {
        this.provider.disconnect()
      }
    },
    methods: {
        // 获取编辑器内容
        getEditorContent() {
            return this.editor.getValue();
        },
        initEditor() {
            console.log('Initializing editor... host:', this.isHost)
            // Initialize Yjs document and WebSocket provider
            this.ydoc = new Y.Doc()
            this.provider = new WebsocketProvider(
            'wss://demos.yjs.dev/ws', // Use the public WebSocket server
            this.roomName,
            this.ydoc
            )

            // 设置本地用户的颜色
            const randomColor = this.getNiceColor()
            this.provider.awareness.setLocalStateField('user', {
                name: this.userName,
                color: randomColor,
                isHost: this.isHost,
            })

            // 监听 awareness 更新
            this.provider.awareness.on('change', this.handleAwarenessChange)
    
            // Initialize Yjs text and binding to CodeMirror
            this.ytext = this.ydoc.getText('codemirror')
            this.yMap = this.ydoc.getMap(this.roomName)

            if(this.isHost) {
                const alreadyInitialized = sessionStorage.getItem('initialized_' + this.roomName);

                if (!alreadyInitialized) {
                    this.ytext.insert(0, this.initialCode);
                    this.yMap.set('initialized', true);
                    sessionStorage.setItem('initialized_' + this.roomName, 'true');
                }

            }

            this.editor = CodeMirror(this.$refs.editorContainer, {
            mode: this.selectedLanguage,
            lineNumbers: true,
            lineWrapping: true,
            extraKeys: {
                'Ctrl-Space': 'autocomplete', // 按 Ctrl+Space 弹出补全
                'Cmd-Space': 'autocomplete'   // macOS 支持
            },
                hintOptions: {
                completeSingle: false // 不自动选中唯一结果（更自然）
                }
            })

            // ✅ 输入时自动触发补全（可选）
            this.editor.on('inputRead', (cm, change) => {
                if (change.text[0].match(/[\w.]/)) {
                cm.showHint()
                }
            })

            this.$refs.editorContainer.editorInstance = this.editor
        
            new CodemirrorBinding(this.ytext, this.editor, this.provider.awareness)
        },

        async changeLanguage() {
            this.editor.setOption('mode', this.selectedLanguage)
            // 根据语言动态加载对应的 hint 插件
            switch (this.selectedLanguage) {
                case 'javascript':
                    await import('codemirror/addon/hint/javascript-hint.js')
                    break
                    case 'python':
                    // 无官方的hint
                    break
                    case 'htmlmixed':
                    await import('codemirror/addon/hint/html-hint.js')
                    break
                    case 'css':
                    await import('codemirror/addon/hint/css-hint.js')
                    break
                    case 'markdown':
                    // 没有标准的 markdown-hint，可以跳过或者自定义
                    break
                    case 'text/x-java':
                    case 'text/x-c++src':
                    // 没有官方 hint，可能需要自己实现或跳过
                    break
                    default:
                    break
            }
        },
        

        handleAwarenessChange() {
            const states = this.provider.awareness.getStates()
            const users = {}
            states.forEach((state, clientID) => {
                if (state.user) {
                    users[clientID] = state.user
                }
            })
            this.$emit('update-users', users)
        },
        getNiceColor() {
            const hue = Math.floor(Math.random() * 360); // 色相随机
            const saturation = 70 + Math.random() * 30;  // 饱和度 70%~100%
            const lightness = 60 + Math.random() * 10;   // 亮度 60%~70%
            return this.hslToHex(hue, saturation, lightness);
        },
        hslToHex(h, s, l) {
            s /= 100;
            l /= 100;

            const k = n => (n + h / 30) % 12;
            const a = s * Math.min(l, 1 - l);
            const f = n =>
            Math.round(255 * (l - a * Math.max(-1, Math.min(k(n) - 3, Math.min(9 - k(n), 1)))));

            return `#${[f(0), f(8), f(4)]
            .map(x => x.toString(16).padStart(2, '0'))
            .join('')}`;
        },
        toggleConnection() {
            if (this.provider.shouldConnect) {
                this.provider.disconnect()
                this.connectionStatus = 'Connect'
            } else {
                this.provider.connect()
                this.connectionStatus = 'Disconnect'
            }
        },
    },
  }
  </script>
  
<style>


.yjs-editor {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.editor-toolbar {
  height: 31px;
  width: 100%;
  /* 上面 runnable */
  display: flex;
  align-items: center;
  padding: 10px 16px;
  margin-bottom: 5px;
  background-color: rgb(255, 255, 255);
  border-bottom: 1px solid #ddd;
  font-family: 'Segoe UI', sans-serif;
  /* todo */
  flex-shrink: 0;
}

.language-selector {
  appearance: none; /* 移除默认样式 */
  /* border: 1px solid #ccc; */
  border-radius: 5px;
  padding: 3px 0;
  color: #333;
  cursor: pointer;
  /* box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); */
  transition: border-color 0.2s, box-shadow 0.2s;
  background-image: url("data:image/svg+xml,%3Csvg fill='gray' height='16' viewBox='0 0 24 24' width='16' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M7 10l5 5 5-5z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
  background-size: 16px;
  padding-right: 36px;
}

.language-selector:hover {
  border-color: #888;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.editor-container {
  flex: 1;
  width: 100%;
  overflow: auto;
}


/* PADDING */

.CodeMirror-lines {
  padding: 4px 0; /* Vertical padding around content */
}


/* GUTTER */

.CodeMirror-gutters {
  border-right: 1px solid #ddd; /* 行号区域右侧的边框线 */
  background-color: rgb(255,255,255);    /* 行号区域的背景颜色 */
  white-space: nowrap;            /* 防止行号换行 */
}
.CodeMirror-linenumbers {}
.CodeMirror-linenumber {
  padding: 0 3px 0 5px;
  min-width: 20px;
  text-align: right;
  color: #999;
  white-space: nowrap;
}

/* 可以用 editor.setGutterMarker 给某一行左侧加图标或标记（比如断点、折叠标记等）；
    .CodeMirror-guttermarker 是默认 marker 的样式（颜色是黑色）
    .CodeMirror-guttermarker-subtle 是“次要标记”，颜色更浅一点 */
.CodeMirror-guttermarker { color: black; }
.CodeMirror-guttermarker-subtle { color: #999; }

/* CURSOR */

.CodeMirror-cursor {
  border-left: 1px solid black;
  border-right: none;
  width: 0;
}
/* Shown when moving in bi-directional text */
.CodeMirror div.CodeMirror-secondarycursor {
  border-left: 1px solid silver;
}
.cm-fat-cursor .CodeMirror-cursor {
  width: auto;
  border: 0 !important;
  background: #7e7;
}
.cm-fat-cursor div.CodeMirror-cursors {
  z-index: 1;
}
.cm-fat-cursor .CodeMirror-line::selection,
.cm-fat-cursor .CodeMirror-line > span::selection, 
.cm-fat-cursor .CodeMirror-line > span > span::selection { background: transparent; }
.cm-fat-cursor .CodeMirror-line::-moz-selection,
.cm-fat-cursor .CodeMirror-line > span::-moz-selection,
.cm-fat-cursor .CodeMirror-line > span > span::-moz-selection { background: transparent; }
.cm-fat-cursor { caret-color: transparent; }
@-moz-keyframes blink {
  0% {}
  50% { background-color: transparent; }
  100% {}
}
@-webkit-keyframes blink {
  0% {}
  50% { background-color: transparent; }
  100% {}
}
@keyframes blink {
  0% {}
  50% { background-color: transparent; }
  100% {}
}

/* Can style cursor different in overwrite (non-insert) mode */
.CodeMirror-overwrite .CodeMirror-cursor {}

.cm-tab { display: inline-block; text-decoration: inherit; }

/* 垂直参考线 */
.CodeMirror-rulers {
  position: absolute;
  left: 0; right: 0; top: -50px; bottom: 0;
  overflow: hidden;
}
.CodeMirror-ruler {
  border-left: 1px solid #ccc;
  top: 0; bottom: 0;
  position: absolute;
}

/* DEFAULT THEME */

.cm-s-default .cm-header {color: blue;}
.cm-s-default .cm-quote {color: #090;}
.cm-negative {color: #d44;}
.cm-positive {color: #292;}
.cm-header, .cm-strong {font-weight: bold;}
.cm-em {font-style: italic;}
.cm-link {text-decoration: underline;}
.cm-strikethrough {text-decoration: line-through;}

.cm-s-default .cm-keyword {color: #708;}
.cm-s-default .cm-atom {color: #219;}
.cm-s-default .cm-number {color: #164;}
.cm-s-default .cm-def {color: #00f;}
.cm-s-default .cm-variable,
.cm-s-default .cm-punctuation,
.cm-s-default .cm-property,
.cm-s-default .cm-operator {}
.cm-s-default .cm-variable-2 {color: #05a;}
.cm-s-default .cm-variable-3, .cm-s-default .cm-type {color: #085;}
.cm-s-default .cm-comment {color: #a50;}
.cm-s-default .cm-string {color: #a11;}
.cm-s-default .cm-string-2 {color: #f50;}
.cm-s-default .cm-meta {color: #555;}
.cm-s-default .cm-qualifier {color: #555;}
.cm-s-default .cm-builtin {color: #30a;}
.cm-s-default .cm-bracket {color: #997;}
.cm-s-default .cm-tag {color: #170;}
.cm-s-default .cm-attribute {color: #00c;}
.cm-s-default .cm-hr {color: #999;}
.cm-s-default .cm-link {color: #00c;}

.cm-s-default .cm-error {color: #f00;}
.cm-invalidchar {color: #f00;}

.CodeMirror-composing { border-bottom: 2px solid; }

/* Default styles for common addons */

div.CodeMirror span.CodeMirror-matchingbracket {color: #0b0;}
div.CodeMirror span.CodeMirror-nonmatchingbracket {color: #a22;}
.CodeMirror-matchingtag { background: rgba(255, 150, 0, .3); }
.CodeMirror-activeline-background {background: #e8f2ff;}

/* STOP */

/* The rest of this file contains styles related to the mechanics of
   the editor. You probably shouldn't touch them. */

   .CodeMirror {
  /* Set height, width, borders, and global font properties here */
  font-family: monospace;
  width: 100%;
  height: calc(100vh);
  white-space: pre-wrap;
  word-break: break-word;
  overflow-x: hidden;
  /* color: black;
  direction: ltr; */
}
/* .CodeMirror {
  position: relative;
  overflow: hidden;
  background: white;
} */

.CodeMirror-scroll {
  overflow: scroll !important; /* Things will break if this is overridden */
  /* 50px is the magic margin used to hide the element's real scrollbars */
  /* See overflow: hidden in .CodeMirror */
  margin-bottom: -50px; margin-right: -50px;
  padding-bottom: 50px;;
  height: 100%;
  outline: none; /* Prevent dragging from highlighting the element */
  position: relative; 
  z-index: 0;
}
.CodeMirror-sizer {
  position: relative;
  border-right: 50px solid transparent;
}


/* The fake, visible scrollbars. Used to force redraw during scrolling
   before actual scrolling happens, thus preventing shaking and
   flickering artifacts. */
.CodeMirror-vscrollbar, .CodeMirror-hscrollbar, .CodeMirror-scrollbar-filler, .CodeMirror-gutter-filler {
  position: absolute;
  z-index: 6;
  display: none;
  outline: none;
}
.CodeMirror-vscrollbar {
  right: 0; top: 0;
  overflow-x: hidden;
  overflow-y: scroll;
}
.CodeMirror-hscrollbar {
  bottom: 0; left: 0;
  overflow-y: hidden;
  overflow-x: scroll;
}
.CodeMirror-scrollbar-filler {
  right: 0; bottom: 0;
}
.CodeMirror-gutter-filler {
  left: 0; bottom: 0;
}

.CodeMirror-gutters {
  position: absolute; left: 0; top: 0;
  min-height: 100%;
  z-index: 3;
}
.CodeMirror-gutter {
  white-space: normal;
  height: 100%;
  display: inline-block;
  vertical-align: top;
  margin-bottom: -50px;
}
.CodeMirror-gutter-wrapper {
  position: absolute;
  z-index: 4;
  background: none !important;
  border: none !important;
}
.CodeMirror-gutter-background {
  position: absolute;
  top: 0; bottom: 0;
  z-index: 4;
}
.CodeMirror-gutter-elt {
  position: absolute;
  cursor: default;
  z-index: 4;
}
.CodeMirror-gutter-wrapper ::selection { background-color: transparent }
.CodeMirror-gutter-wrapper ::-moz-selection { background-color: transparent }

.CodeMirror-lines {
  cursor: text;
  min-height: 1px; /* prevents collapsing before first draw */
}
.CodeMirror pre.CodeMirror-line,
.CodeMirror pre.CodeMirror-line-like {
  /* Reset some styles that the rest of the page might have set */
  -moz-border-radius: 0; -webkit-border-radius: 0; border-radius: 0;
  border-width: 0;
  background: transparent;
  font-family: inherit;
  font-size: inherit;
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  word-break: break-word;
  line-height: inherit;
  color: inherit;
  z-index: 2;
  position: relative;
  overflow: visible;
  -webkit-tap-highlight-color: transparent;
  -webkit-font-variant-ligatures: contextual;
  font-variant-ligatures: contextual;
}
.CodeMirror-wrap pre.CodeMirror-line,
.CodeMirror-wrap pre.CodeMirror-line-like {
  word-wrap: break-word;
  white-space: pre-wrap;
  word-break: normal;
}

.CodeMirror-linebackground {
  position: absolute;
  left: 0; right: 0; top: 0; bottom: 0;
  z-index: 0;
}

.CodeMirror-linewidget {
  position: relative;
  z-index: 2;
  padding: 0.1px; /* Force widget margins to stay inside of the container */
}

.CodeMirror-widget {}

.CodeMirror-rtl pre { direction: rtl; }

.CodeMirror-code {
  outline: none;
}

/* Force content-box sizing for the elements where we expect it */
.CodeMirror-scroll,
.CodeMirror-sizer,
.CodeMirror-gutter,
.CodeMirror-gutters,
.CodeMirror-linenumber {
  -moz-box-sizing: content-box;
  box-sizing: content-box;
}

.CodeMirror-measure {
  position: absolute;
  width: 100%;
  height: 0;
  overflow: hidden;
  visibility: hidden;
}

.CodeMirror-cursor {
  position: absolute;
  pointer-events: none;
}
.CodeMirror-measure pre { position: static; }

div.CodeMirror-cursors {
  visibility: hidden;
  position: relative;
  z-index: 3;
}
div.CodeMirror-dragcursors {
  visibility: visible;
}

.CodeMirror-focused div.CodeMirror-cursors {
  visibility: visible;
}

.CodeMirror-selected { background: #d9d9d9; }
.CodeMirror-focused .CodeMirror-selected { background: #d7d4f0; }
.CodeMirror-crosshair { cursor: crosshair; }
.CodeMirror-line::selection, .CodeMirror-line > span::selection, .CodeMirror-line > span > span::selection { background: #d7d4f0; }
.CodeMirror-line::-moz-selection, .CodeMirror-line > span::-moz-selection, .CodeMirror-line > span > span::-moz-selection { background: #d7d4f0; }

.cm-searching {
  background-color: #ffa;
  background-color: rgba(255, 255, 0, .4);
}

/* Used to force a border model for a node */
.cm-force-border { padding-right: .1px; }

@media print {
  /* Hide the cursor when printing */
  .CodeMirror div.CodeMirror-cursors {
    visibility: hidden;
  }
}

/* See issue #2901 */
.cm-tab-wrap-hack:after { content: ''; }

/* Help users use markselection to safely style text background */
span.CodeMirror-selectedtext { background: none; }

  </style>
  