<script>
import axios from "axios";
import Cookies from 'js-cookie'
import * as CodeMirror from 'codemirror/lib/codemirror.js'
import 'codemirror/theme/idea.css'
import 'codemirror/theme/eclipse.css'
import 'codemirror/theme/material.css'
import "@/utils/cm-settings.js"
import topicSetting from "@/utils/topic-setting";
import { downloadStrAsFile } from "@/utils/file-system";
import * as echarts from 'echarts'
import moreButton from '../../components/moreButton.vue';

export default {
  name: "FileView",
  components: {
    moreButton
  },
  data() {
    return {
      tree: [],
      files: {
        html: 'mdi-language-html5',
        js: 'mdi-nodejs',
        json: 'mdi-code-json',
        md: 'mdi-language-markdown',
        pdf: 'mdi-file-pdf',
        png: 'mdi-file-image',
        txt: 'mdi-file-document-outline',
        xls: 'mdi-file-excel',
        vue: 'mdi-vuejs'
      },
      items: [],
      cmEditor: null,
      sheet: false,
      fileContent: '选择一个文件以查看其内容',
      selectedText: '',
      fileTreeReady: false,
      fileContentReady: false,

      newFileData: {
        name: '',
        file: '',
        visible: false
      },
      dropdownVisible: false,
      curType: '',
      curFilePath: '',
      curFileName: '',
      nextFilePath: '',
      filePathList: [],
      commitVisible: false,
      treeDisable: false,
      commitForm: {
        title: '提交到 ' + this.branchName + ' 分支',
        commitMessage: '',
        newBranch: '',
        isNewBranch: false,
        editList: [],
        subDisable: false
      },
      showDialog: false,
      fileChart: null
    }
  },
  inject: {
    user: { default: null },
    proj: { default: null },
    repo: { default: null },
    branchName: { default: null }
  },
  methods: {
    downloadStrAsFile,
    getFileExt(obj, path) {
      if (obj['children'] === undefined) {
        obj['file'] = 'unknown'
        obj['path'] = path + '/' + obj['name']
        if (obj['name'].indexOf('.') !== -1) {
          obj['file'] = obj['name'].split('.').pop()
        }
      } else {
        for (let i = 0; i < obj['children'].length; i++) {
          this.getFileExt(obj['children'][i], path + '/' + obj['name'])
        }
      }
    },
    file2style() {
      if (this.curType === '') {
        return 'null'
      }

      let file = this.curType;
      if (file === 'html') {
        return 'htmlmixed'
      } else if (file === 'js') {
        return 'javascript'
      } else if (file === 'json') {
        return 'javascript'
      } else if (file === 'md') {
        return 'markdown'
      } else if (file === 'vue') {
        return 'vue'
      } else if (file === 'css') {
        return 'css'
      } else if (file === 'xml') {
        return 'xml'
      } else if (file === 'c' || file === 'cpp' || file === 'h') {
        return 'clike'
      } else if (file === 'py') {
        return 'python'
      } else {
        return 'null'
      }
    },
    onCursorActivity() {
      this.selectedText = this.cmEditor.getSelection()
    },
    analyWholeFile() {
        if (this.fileContent.length <= 10) {
            this.$message({
                type: 'error',
                message: '喵呜~ 代码太短了啦 (ฅ´ω`ฅ) 再多写一点好不好'
            })
            return
        }
        //如果文件长度大于Cookie最长长度，就不诊断了
        // if (this.fileContent.length > 4096) {
        //     this.$message({
        //         type: 'error',
        //         message: '文件太长了，AI会罢工的！'
        //     })
        //     return
        // }
        // Cookies.set('diag', this.fileContent)
        // console.log('cookies content:', Cookies.get('diag'))
        localStorage.setItem('diag', this.fileContent)
        console.log('localStorage content:', localStorage.getItem('diag'))
        window.open('/user/ai/analysis', '_blank')
    },
    diagSelected() {
      //如果文件长度大于Cookie最长长度，就不诊断了
      if (this.selectedText.length > 4096) {
        this.$message({
          type: 'error',
          message: '文件太长了，AI会罢工的！'
        })
        return
      }
      if (this.selectedText.length <= 10) {
        this.$message({
          type: 'error',
          message: '喵呜~ 代码太短了啦 (ฅ´ω`ฅ) 再多写一点好不好'
        })
        return
      }
      Cookies.set('diag', this.selectedText)
      window.open('/user/ai/diagnosis', '_blank')
    },
    diagWholeFile() {
      //如果文件长度大于Cookie最长长度，就不诊断了
      if (this.fileContent.length > 4096) {
        this.$message({
          type: 'error',
          message: '文件太长了，AI会罢工的！'
        })
        return
      }
      Cookies.set('diag', this.fileContent)
      window.open('/user/ai/diagnosis', '_blank')
    },
    unitTestSelected() {
      //如果文件长度大于Cookie最长长度，就不诊断了
      if (this.selectedText.length > 4096) {
        this.$message({
          type: 'error',
          message: '文件太长了，AI会罢工的！'
        })
        return
      }
      if (this.selectedText.length <= 10) {
        this.$message({
          type: 'error',
          message: '代码这么短，怎么生成嘛'
        })
        return
      }
      Cookies.set('diag', this.selectedText)
      window.open('/user/ai/testdata', '_blank')
    },
    unitTestWholeFile() {
      //如果文件长度大于Cookie最长长度，就不诊断了
      if (this.fileContent.length > 4096) {
        this.$message({
          type: 'error',
          message: '文件太长了，AI会罢工的！'
        })
        return
      }
      Cookies.set('diag', this.fileContent)
      window.open('/user/ai/testdata', '_blank')
    },

    tabClick() {
      if (this.treeDisable) {
        this.nextFilePath = this.curFilePath;
        return;
      }
      if (this.nextFilePath == this.curFilePath) {
        return;
      }
      for (var i = 0; i < this.filePathList.length; i++) {
        if (this.filePathList[i].path == this.curFilePath) {
          if (this.filePathList[i].content != this.cmEditor.getValue()) {
            this.filePathList[i].newContent = this.cmEditor.getValue();
            this.filePathList[i].changed = true;
          } else {
            this.filePathList[i].changed = false;
          }
        }
      }
      for (var i = 0; i < this.filePathList.length; i++) {
        if (this.filePathList[i].path == this.nextFilePath) {
          this.curFilePath = this.filePathList[i].path;
          this.fileContent = this.filePathList[i].changed ? this.filePathList[i].newContent : this.filePathList[i].content;
          this.curType = this.filePathList[i].file;
          this.cmEditor.setValue(this.fileContent);
          this.cmEditor.setOption('mode', this.file2style());
        }
      }
    },
    tabRemove() {
      if (this.treeDisable) {
        this.nextFilePath = this.curFilePath;
        return;
      }
      for (var i = 0; i < this.filePathList.length; i++) {
        if (this.filePathList[i].path == this.nextFilePath) {
          if (this.filePathList[i].content != this.cmEditor.getValue()) {
            this.openForm();
            return;
          } else {
            this.filePathList.splice(i, 1);
          }
        }
      }
      if (this.filePathList.length == 0) {
        this.curFilePath = '';
        this.fileContent = '选择一个文件以查看其内容';
        this.cmEditor.setValue(this.fileContent);
        this.cmEditor.setOption('mode', '');

      } else {
        var now = this.filePathList.length - 1;
        this.fileContent = this.filePathList[now].changed ? this.filePathList[now].newContent : this.filePathList[now].content;
        this.curFilePath = this.filePathList[now].path;
        this.nextFilePath = this.curFilePath;
        this.curType = this.filePathList[now].file;
        this.cmEditor.setValue(this.fileContent);
        this.cmEditor.setOption('mode', this.file2style());
      }
    },
    openForm() {
      this.commitForm.editList = [];
      for (var i = 0; i < this.filePathList.length; i++) {
        if (this.filePathList[i].path == this.curFilePath) {
          if (this.cmEditor.getValue() != this.filePathList[i].content) {
            this.filePathList[i].changed = true;
            this.filePathList[i].newContent = this.cmEditor.getValue();
          }
        }
        if (this.filePathList[i].changed == true) {
          var editFile = { path: this.filePathList[i].path, content: this.filePathList[i].newContent, isCommit: true };
          this.commitForm.editList.push(editFile);
        }
      }
      if (this.commitForm.editList.length == 0) {
        this.$message({
          message: '当前未修改任何文件',
          type: 'warning'
        });
        return;
      }
      var files = [];
      for (var i = 0; i < this.commitForm.editList.length; i++) {
        if (this.commitForm.editList[i].isCommit) {
          var file = { path: this.commitForm.editList[i].path.slice(1), content: this.commitForm.editList[i].content };
          files.push(file);
        }
      }
      axios.post('api/ai/generateCommitMessage', {
        userId: this.user.id,
        projectId: this.proj.projectId,
        repoId: this.$route.params.repoid,
        branch: this.branchName,
        files: files,
      }).then((res) => {
        if (res.data.errcode !== 0) {
          alert('/api/develop/generateCommitMessage errcode not 0: ' + res.data.message)
        } else {
          this.commitForm.commitMessage = res.data.data;
        }
      }).catch((err) => {
        alert('/api/develop/commit error' + err)
        console.log(err);
      })
      this.commitVisible = true;
    },
    cancelEdit() {
      for (var i = 0; i < this.filePathList.length; i++) {
        if (this.filePathList[i].path == this.curFilePath) {
          this.fileContent = this.filePathList[i].content;
          this.cmEditor.setValue(this.fileContent);
          this.cmEditor.setOption('mode', this.file2style());
        }
        if (this.filePathList[i].changed == true) {
          this.filePathList[i].changed = false;
          this.tabClick();
        }
      }
    },
    submitForm() {
      this.subDisable = true;
      var files = [];
      for (var i = 0; i < this.commitForm.editList.length; i++) {
        if (this.commitForm.editList[i].isCommit) {
          var file = { path: this.commitForm.editList[i].path.slice(1), content: this.commitForm.editList[i].content };
          files.push(file);
        }
      }
      if (files.length === 0) {
        this.subDisable = false;
        this.$message({
          message: '请重新选择commit文件，当前未选中任何文件',
          type: 'warning'
        });
        return;
      }
      let api = this.commitForm.isNewBranch ? '/api/develop/gitBranchCommit' : '/api/develop/gitCommit'
      axios.post(api, {
        userId: this.user.id,
        projectId: this.proj.projectId,
        repoId: this.$route.params.repoid,
        branch: this.branchName,
        dstBranch: this.commitForm.newBranch,
        files: files,
        message: this.commitForm.commitMessage
      }).then((res) => {
        if (res.data.errcode !== 0) {
          alert('/api/reviews/commit errcode not 0: ' + res.data.message)
        } else {
          for (var i = 0; i < this.commitForm.editList.length; i++) {
            for (var j = 0; j < this.filePathList.length; j++) {
              if (this.filePathList[j].path == this.commitForm.editList[i].path) {
                this.filePathList[j].changed = false;
                this.filePathList[j].content = this.filePathList[j].newContent;
              }
            }
          }
        }
      }).catch((err) => {
        alert('/api/reviews/commit error' + err)
        console.log(err);
      }).finally(() => {
        this.commitVisible = false;
        this.subDisable = false;
        this.commitForm.title = '提交到 ' + this.branchName + ' 分支';
        this.commitForm.commitMessage = '';
        this.commitForm.newBranch = '';
        this.commitForm.isNewBranch = false;
        this.commitForm.editList = [];
        this.commitForm.subDisable = false;
      })

    },
    getBtnColor: topicSetting.getColor,
    getTopicColor: topicSetting.getDarkColor,
    getRadialGradient: topicSetting.getRadialGradient,
    getLinearGradient: topicSetting.getLinearGradient,
    onClickCollab() {
        console.log('entered method: onClickCollab');
        if (!this.curFilePath || !this.fileContent) {
            this.$message({
            type: 'warning',
            message: '请先选择一个文件进行协同编辑'
            });
            return;
        }
        // 获取当前文件 & 工作区
        const filePath = this.curFilePath;
        const fileType = this.curType;
        const content = this.cmEditor.getValue();

        // 生成roomName
        const roomName = `${this.user.id}_${Date.now()}`;

        // todo 定期清理 存入 localStorage 以便协同页面读取
        const collabData = {
            filePath,
            fileType,
            content,
            userId: this.user.id,
            projId: this.proj.projectId,
            roomName: roomName,
            repoId: this.$route.params.repoid,
            branch: this.branchName
        };
        localStorage.setItem(`collab_${roomName}`, JSON.stringify(collabData));

        // 生成链接
        const baseUrl = window.location.origin;
        // todo 链接待修改
        const collabUrl = `${baseUrl}/room?roomName=${roomName}`;

        // 提示用户复制链接邀请他人
        this.$prompt('复制以下链接邀请他人加入协同编辑：', '协同编辑链接', {
            confirmButtonText: '点击进入协同编辑',
            inputValue: collabUrl,
            inputReadonly: true,
            closeOnClickModal: false,
            beforeClose: (action, instance, done) => {
                if (action === 'confirm') {
                    console.log("file content: "+this.fileContent);
                    sessionStorage.setItem('fileContent', this.fileContent);
                    window.open(`/room?roomName=${roomName}&host=true`, '_blank');
                }
                done();
            }
        });

    },
    showContribution() {
      console.log('enter method: showContribution')
      if (!this.curFilePath) {
        this.$message.error('还未选择文件！')
      } else {
        this.showDialog = true
      }
    },
    hideContribution() {
      this.showDialog = false
      setTimeout(() => {
        if (this.fileChart) {
          this.fileChart.dispose()
        }
      }, 1000)
    },
    drawFileP() {
      if (this.fileChart) {
        this.fileChart.dispose()
      }
      this.fileChart = echarts.init(this.$refs.fileChart);
      window.addEventListener("resize", () => {
        this.fileChart.resize();
      });

      let userName = []
      let userCommitCnt = []
      axios.post('/api/develop/getFileCommits', {
        repoId: this.$route.params.repoid,
        file: this.curFilePath.substring(1),
        branch: this.branchName,
        userId: this.user.id,
        projectId: this.proj.projectId
      }).then((res) => {
        const data = res.data.data
        console.log(data)
        for (let entry of data) {
          userName.push(entry.userName)
          userCommitCnt.push(entry.count)
        }
        console.log(userName)
        console.log(userCommitCnt)

        let option = {
          title: {
            text: "文件贡献度统计图",
          },
          tooltip: {
            trigger: "axis",
            formatter: function (params) {
              console.log(params);
              return params[0]['axisValue'] + "的文件贡献度为：" + params[0]['value'];
            },
          },
          grid: {
            left: "3%",
            right: "4%",
            bottom: "30%",
            containLabel: true,
          },
          yAxis: {
            type: "category",
            splitLine: {
              show: false,
            },
            data: userName,
          },
          xAxis: {
            type: "value",
            axisLabel: {
              color: "#333", // 坐标轴文字颜色
              formatter: function (param) {
                return param;
              },
            },
          },
          series: [
            {
              name: "文件贡献度",
              type: "bar",
              stack: "Total",
              data: userCommitCnt,
            },
          ],
        };
        this.fileChart.setOption(option);
      })
    },
    checkFresh() {
      axios.post("api/develop/checkRefreshRepo", {
        userId: this.user.id,
        projectId: this.proj.projectId,
        repoId: this.$route.params.repoid
      })
        .then((res) => {
          console.log(res.data)
          if (res.data.needRefresh === 1) {
            this.$message({
              type: 'warning',
              message: '请等待当前页面数据更新'
            })
            this.fresh()
          }
        })
    },
    fresh() {
      axios.post("api/develop/refreshRepo", {
        userId: this.user.id,
        projectId: this.proj.projectId,
        repoId: this.$route.params.repoid
      })
    },
    handleCommand(command) {
      if (command == "a") {
        this.showContribution();
      } else if (command == "b") {
        console.log("bbb");
        var name = this.curFilePath.split("/").pop();
        downloadStrAsFile(this.fileContent, name);
      } else if (command == "c") {
        this.newFile();
      } else if(command == "d") {
        // 多人协同编辑
        console.log("clicked collaborative editing");
        this.onClickCollab();
      }
    },

    newFile() {
      this.newFileData.visible = true;
    },
    createNewFile() {
      if (this.newFileData.name == "") {
        this.$message({
          type: 'warning',
          message: '请填写文件名'
        })
      }
      var name;
      if (!this.newFileData.name.includes(".")) {
        this.newFileData.name = this.newFileData.name + ".txt";
      }
      name = this.newFileData.name;
      for(var i = 0; i < this.items.length; i++) {
        if(this.items[i].file != undefined){
          if(this.items[i].name == name) {
            this.$message({
              type:'warning',
              message:'文件已存在，请重新填写文件名'
            })
            return;
          }
        }
      }

      var file = name.split(".").pop()

      var item = {file:file, name:name, path: "/" + name};
      this.items.push(item);

      var newFile = { file: file, path: "/" + name, name: name, content: 'newFile', newContent: '', changed: true, removed: false };
            this.filePathList.push(newFile);
            this.curFilePath = newFile.path;
            this.nextFilePath = this.curFilePath;
            this.curFileName = newFile.name;
            this.fileContent = newFile.newContent;
            this.curType = newFile.file;
            this.cmEditor.setValue(this.fileContent)
            this.cmEditor.setOption('mode', this.file2style())
            this.$message({
              type:'success',
              message:'成功新建文件'
            })
            this.newFileData.visible = false;
            this.newFileData.name = '';
    }
  },
  created() {
    this.fileTreeReady = false;
    axios.post('/api/develop/getFileTree', {
      userId: this.user.id,
      projectId: this.proj.projectId,
      repoId: this.$route.params.repoid,
      branch: this.branchName
    }).then((res) => {
      if (res.data.errcode === 0) {
        console.log(res.data.data)
        this.items = res.data.data             // [{file: ,   path: }]
        for (let i = 0; i < this.items.length; i++) {
          this.getFileExt(this.items[i], '')
        }
        console.log("tree:\n");
        console.log(this.items);
      } else {
        alert('/api/reviews/getFileTree errcode not 0: ' + res.data.message)
      }
    }).catch((err) => {
      alert('/api/reviews/getFileTree error' + err)
      console.log(err);
    }).finally(() => {
      this.fileTreeReady = true;
    })
  },
  watch: {
    tree() {
      console.log('selected file change!')
      console.log(this.tree);
      if (this.tree[0]['file'] !== undefined) {
        this.treeDisable = true;
        if (this.curFilePath === this.tree[0]['path']) {
          this.treeDisable = false;
          return;
        }
        for (var i = 0; i < this.filePathList.length; i++) {
          if (this.filePathList[i].path === this.curFilePath) {
            if (this.filePathList[i].content !== this.cmEditor.getValue()) {
              this.filePathList[i].newContent = this.cmEditor.getValue();
              this.filePathList[i].changed = true;
            } else {
              this.filePathList[i].changed = false;
            }
          }
        }
        for (var i = 0; i < this.filePathList.length; i++) {
          if (this.filePathList[i].path === this.tree[0]['path']) {
            this.curFilePath = this.tree[0]['path'];
            this.nextFilePath = this.tree[0]['path'];
            this.curFileName = this.tree[0]['name'];
            this.curType = this.tree[0]['file'];
            this.fileContent = this.fileContent = this.filePathList[i].changed ? this.filePathList[i].newContent : this.filePathList[i].content;
            this.cmEditor.setValue(this.fileContent)
            this.cmEditor.setOption('mode', this.file2style())
            this.treeDisable = false;
            return;
          }
        }
        this.fileContentReady = false;
        this.cmEditor.setValue('正在努力拉取文件！\n\n  ')
        this.cmEditor.setOption('mode', '')
        axios.post('/api/develop/getContent', {
          userId: this.user.id,
          projectId: this.proj.projectId,
          repoId: this.$route.params.repoid,
          branch: this.branchName,
          path: this.tree[0]['path']
        }).then((res) => {
          if (res.data.errcode === 0) {
            console.log(res.data.data)
            var newFile = { file: this.tree[0]['file'], path: this.tree[0]['path'], name: this.tree[0]['name'], content: this.fileContent = res.data.data, newContent: '', changed: false, removed: false };
            this.filePathList.push(newFile);
            this.curFilePath = newFile.path;
            this.nextFilePath = this.curFilePath;
            this.curFileName = newFile.name;
            this.fileContent = newFile.content;
            this.curType = newFile.file;
            this.cmEditor.setValue(this.fileContent)
            this.cmEditor.setOption('mode', this.file2style())
          } else {
            alert('/api/reviews/getFileContent errcode not 0: ' + res.data.message)
          }
        }).catch((err) => {
          alert('/api/reviews/getFileContent error' + err)
          console.log(err);
        }).finally(() => {
          this.fileContentReady = true;
          this.treeDisable = false;
        })
      }
    }
  },
  mounted() {
    this.cmEditor = CodeMirror.fromTextArea(this.$refs.cm1, {
      theme: 'material',
      lineNumbers: true,
      line: true,
      readOnly: false,
      lineWrapping: true
    });

    this.cmEditor.on('cursorActivity', this.onCursorActivity);
    this.checkFresh();
  }
}

</script>

<template>
  <v-container>
    <v-row style="margin-top: 20px">
      <v-col :cols="fileContentReady ? 2 : 3">
        <div class="tabs-menu">
          <h2>文件树</h2>
        </div>
        <v-card height="300px" class="overflow-y-auto">
          <v-treeview v-if="fileTreeReady" :items="items" :activatable="!treeDisable" :active.sync="tree" item-key="name"
            open-on-click dense return-object>
            <template v-slot:prepend="{ item, open }">
              <v-icon v-if="!item.file" :color="getTopicColor(user.topic)">
                {{ open ? 'mdi-folder-open' : 'mdi-folder' }}
              </v-icon>
              <v-icon v-else :color="getTopicColor(user.topic)">
                {{ files[item.file] !== undefined ? files[item.file] : 'mdi-file-document' }}
              </v-icon>
            </template>
          </v-treeview>
          <v-skeleton-loader v-else type="list-item-three-line@5" class="mt-2"></v-skeleton-loader>
        </v-card>
        <div class="commit-div">
            
            <p> <el-button size="medium" class="commit-button" @click="cancelEdit">取消修改</el-button></p>
           <p>  <el-button type="primary" size="medium" @click="openForm" class="commit-button" style="color: white">创建提交</el-button></p>
          
          <!-- <div style="display: flex; justify-content: center;">
            <p> <el-button size="medium" class="commit-button" @click="cancelEdit">取消修改</el-button></p>
           <p>  <el-button type="primary" size="medium" @click="openForm" class="commit-button" style="color: white">创建提交</el-button></p>
          </div> -->
        </div>
        <el-dialog :title="commitForm.title" :visible.sync="commitVisible" width="40%">
          <el-form :model="commitForm" ref="form" label-width="140px">
            <el-form-item>
              <el-checkbox v-for="item in commitForm.editList" :key="item.path" v-model="item.isCommit">{{ item.path
              }}</el-checkbox>
            </el-form-item>
            <el-form-item label="commit message">
              <el-input v-model="commitForm.commitMessage"></el-input>
            </el-form-item>

            <el-form-item>
              <el-checkbox v-model="commitForm.isNewBranch">是否提交到新分支</el-checkbox>
            </el-form-item>
            <el-form-item label="分支名称" v-if="commitForm.isNewBranch">
              <el-input v-model="commitForm.newBranch"></el-input>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="submitForm">提交</el-button>
            </el-form-item>
          </el-form>
        </el-dialog>
      </v-col>

      <v-col :cols="fileContentReady ? 7 : 9">
        <div class="tabs-menu" v-show="filePathList.length">
          <el-tabs v-model="nextFilePath" type="card" @tab-click="tabClick" @tab-remove="tabRemove">
            <el-tab-pane v-for="item in filePathList" :key="item.path" :label="item.name" :name="item.path"
              :closable="true">
              <template #label>
                <v-icon :color="getTopicColor(user.topic)">
                  {{ files[item.file] !== undefined ? files[item.file] : 'mdi-file-document' }}
                </v-icon>
                {{ item.name }}
                <v-icon v-if="item.changed" color="black">mdi-circle-small</v-icon>
              </template>
            </el-tab-pane>
          </el-tabs>
          <el-dropdown class="moreButton" @command="handleCommand">
            <el-button type="primary" style="color: white">
              更多功能<i class="el-icon-arrow-down el-icon--right"></i>
            </el-button>

            <el-dropdown-menu slot="dropdown">
              <!-- <el-dropdown-item command="a">查看文件贡献图</el-dropdown-item> -->
              <el-dropdown-item command="b">下载当前文件</el-dropdown-item>
              <el-dropdown-item command="c">新建文件</el-dropdown-item>
              <el-dropdown-item command="d">多人协同编辑</el-dropdown-item>
            </el-dropdown-menu>
          </el-dropdown>
          <el-dialog title="新建文件" :visible.sync="newFileData.visible" width="40%">
                <el-form :model="newFileData" ref="form" label-width="140px">
                  <el-form-item label="文件名">
                    <el-input v-model="newFileData.name"></el-input>
                  </el-form-item>
                  <el-form-item>
                    <el-button type="primary" @click="createNewFile">新建</el-button>
                  </el-form-item>
                </el-form>
              </el-dialog>
        </div>
        <div v-show="filePathList.length === 0" style="height: 10%; position: relative">
          <el-dropdown class="moreButton">
            <el-button type="primary" style="color: white">
              更多功能<i class="el-icon-arrow-down el-icon--right"></i>
            </el-button>
            <el-dropdown-menu slot="dropdown">
              <el-dropdown-item>请先选择文件</el-dropdown-item>
            </el-dropdown-menu>
          </el-dropdown>
        </div>
        <v-card max-height="calc(100vh - 300px)" min-height="calc(100vh - 300px)">
          <textarea ref="cm1" v-model='fileContent' style="height: calc(100vh - 300px); width: 100%"></textarea>
        </v-card>
      </v-col>

       <v-col cols="3" v-if="fileContentReady">
            <h2 :style="'text-decoration: none; color: ' + getTopicColor(user.topic)">代码助手</h2>
            <v-card max-height="calc(100vh - 300px)" min-height="calc(100vh - 300px)" class="overflow-y-auto overflow-x-hidden">
        
                <v-divider></v-divider>

                <v-card-title>人机协同</v-card-title>
                <v-card-text>AutoHub也很乐意对您选中的代码，或是整个文件进行代码优化</v-card-text>
                <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn width="" outlined :color="getTopicColor(user.topic)" @click="diagSelected"><v-icon>mdi-code-braces</v-icon>对选中代码</v-btn>
                </v-card-actions>
                <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn width="" outlined :color="getTopicColor(user.topic)" @click="diagWholeFile"><v-icon>mdi-code-braces</v-icon>对整个文件</v-btn>
                </v-card-actions>

                <v-divider></v-divider>

                <v-card-title>静态分析</v-card-title>
                <v-card-text>AutoHub帮助您管理源代码的质量，快速定位Bug、漏洞以及不优雅的地方</v-card-text>
                <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn width="" outlined :color="getTopicColor(user.topic)" @click="analyWholeFile"><v-icon>mdi-magnify-scan</v-icon>对整个文件</v-btn>
                </v-card-actions>
                
                <v-divider></v-divider>

                <v-card-title>单元测试</v-card-title>
                <v-card-text>AutoHub可以对您选中的代码，或是整个文件生成单元测试</v-card-text>
                <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn width="" outlined :color="getTopicColor(user.topic)" @click="unitTestSelected"><v-icon>mdi-check</v-icon>对选中代码</v-btn>
                </v-card-actions>
                <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn width="" outlined :color="getTopicColor(user.topic)" @click="unitTestWholeFile"><v-icon>mdi-check</v-icon>对整个文件</v-btn>
                </v-card-actions>

            </v-card>
          </v-col>
    </v-row>
    <el-dialog :visible.sync="showDialog" width="70%" :before-close="hideContribution" @opened="drawFileP">
      <div style="position: relative;width: 100%;height: 300px">
        <div ref="fileChart" style="position: absolute; width: 80%; height: 60%; left: 10%; top: 10%">
        </div>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button type="primary" @click="hideContribution">确 定</el-button>
      </span>
    </el-dialog>
  </v-container>
</template>

<style>
.CodeMirror {
  height: calc(100vh - 300px);
}

.v-card__title {
    padding-top: 8px;
    padding-bottom: 8px;
}

.need-mono {
  font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
}

.tabs-menu {
  display: flex;
  position: relative;
  width: 100%;
  height: 10%;
}

.moreButton {
  position: absolute;
  right: 0;
}

.commit-div {
  /* margin-top: 100px;
  height: 150px;
  display: flex;
  justify-content: center; */
  margin-top: 20px;
}

.commit-button {
  width: 100%;
}
</style>