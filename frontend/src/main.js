import Vue from 'vue'

import vGanttChart from 'v-gantt-chart';
import App from './App.vue'
import router from './router'
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'
import axios from "axios"
import VueAxios from 'vue-axios'

import './assets/main.css'
import vuetify from './plugins/vuetify'
import '@babel/polyfill'

import AllTask from "@/views/user/projectPlanning/allTask.vue"
import AllFile from "@/views/user/document/allFile.vue"

import mavonEditor from "mavon-editor"
import VueMarkdownEditor from '@kangc/v-md-editor'
import createKatexPlugin from '@kangc/v-md-editor/lib/plugins/katex/cdn.js';
import '@kangc/v-md-editor/lib/style/base-editor.css';
import vuepressTheme from '@kangc/v-md-editor/lib/theme/vuepress.js';
import Prism from 'prismjs';

VueMarkdownEditor.use(vuepressTheme);
VueMarkdownEditor.use(createKatexPlugin());
Vue.use(VueMarkdownEditor);
VueMarkdownEditor.use(vuepressTheme, {
    Prism,
    extend(md) {
        // md为 markdown-it 实例，可以在此处进行修改配置,并使用 plugin 进行语法扩展
        // md.set(option).use(plugin);
    },
});
axios.defaults.baseURL = 'http://10.254.47.34:8000/'
Vue.use(ElementUI, axios, VueAxios)
axios.defaults.withCredentials = true;
Vue.use(mavonEditor);
Vue.config.productionTip = false
Vue.component('AllTask', AllTask);
Vue.component('AllFile', AllFile);
Vue.use(vGanttChart);
new Vue({
    router,
    vuetify,
    render: (h) => h(App)
}).$mount('#app')
