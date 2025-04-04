<script>
import topicSetting from "@/utils/topic-setting";
import axios from "axios";

export default {
  name: 'Database',
  inject: ['user', 'proj'],
  data () {
    return {
      entries: {},
      uploadDialog: false,
      fileInput: null,
      fileNameInput: '',
      fileExtInput: '',
      fileMajorInput: 0,
      fileMinorInput: 0,
      filePatchInput: 0,

      changeNameAllow: true,
      minPatch: -1,

      downloading: false,
      downloadProgressBannerContent: 'Downloading...',
      uploading: false,
      uploadProgressBannerContent: 'Uploading...'
    }
  },
  methods: {
    upload() {
      this.uploading = true
      console.log(this.fileInput)
      console.log(this.fileNameInput)
      console.log(this.fileExtInput)
      console.log(this.fileMajorInput)
      console.log(this.fileMinorInput)
      console.log(this.filePatchInput)
      console.log(new Date().getTime())
      console.log(`${this.fileNameInput}-${new Date().getTime()}-${this.fileMajorInput}-${this.fileMinorInput}-${this.filePatchInput}.${this.fileExtInput}`)
      this.fileInput = new File([this.fileInput], `${this.fileNameInput}-${new Date().getTime()}-${this.fileMajorInput}-${this.fileMinorInput}-${this.filePatchInput}.${this.fileExtInput}`, {type: this.fileInput.type})
      let data = new FormData()
      data.append('projectId', this.proj.projectId)
      data.append('file', this.fileInput)
      let config =  {
        method: 'post',
        maxBodyLength: Infinity,
        url: '/api/file/uploadFile',
        data : data,
        onUploadProgress: this.uploadProgressChanged
      };

      axios(config)
        .then((response) => {
          console.log(JSON.stringify(response.data));
          this.$message.success('上传文件成功')
        })
        .catch((error) => {
          console.log(error);
          this.$message.error('上传文件失败')
        })
        .finally(() => {
          this.updateDatabase()
          this.uploadDialog = false
          this.uploading = false
        })
    },
    downloadProgressChanged(progressiveEvent) {
      this.downloadProgressBannerContent = `Downloading... ${Math.round(progressiveEvent.loaded / progressiveEvent.total * 100)}%`
    },
    uploadProgressChanged(progressiveEvent) {
      this.uploadProgressBannerContent = `Uploading... ${Math.round(progressiveEvent.loaded / progressiveEvent.total * 100)}%`
    },
    download(file) {
      if (this.downloading === true) {
        this.$message.error('正在下载文件，请在当前文件下载完成后重试')
        return
      }
      this.downloading = true

      console.log(file)
      // 组合成文件名
      const filename = file.fullname
      axios.post('/api/file/downloadFile', {
        projectId: this.proj.projectId,
        fileName: filename
      }, {
        responseType: 'blob',
        onDownloadProgress: this.downloadProgressChanged
      }).then((res) => {
        const blob = new Blob([res.data]);
        const url = URL.createObjectURL(blob);

        const tempLink = document.createElement('a');
        tempLink.href = url;
        tempLink.setAttribute('download', file.name + file.ext);
        document.body.appendChild(tempLink);
        tempLink.click();
        document.body.removeChild(tempLink);

        URL.revokeObjectURL(url);
        this.$message.success('下载文件成功，请检查浏览器下载页面')
      }).catch(err => {
        this.$message.error('下载文件失败')
        console.log(err)
      }).finally(() => {
        this.downloading = false
      })
    },
    mapFileToEntry(filename) {
      // 获取filename的拓展名和文件名
      const ext = '.' + filename.split('.').pop()
      const name = filename.split('.').slice(0, -1).join('.')

      const names = name.split('-')
      if (names.length !== 5) {
        console.log(filename + ' does not seem to be a valid file in jihub database, skipping...')
        return null
      } else {
        let name = names[0]
        let time = new Date(parseInt(names[1]))
        let major = parseInt(names[2])
        let minor = parseInt(names[3])
        let patch = parseInt(names[4])
        return { name: name, ext: ext, time: time, major: major, minor: minor, patch: patch, fullname: filename }
      }
    },
    updateDatabase() {
      axios.post('/api/file/watchFiles', {
        projectId: this.proj.projectId
      }).then(res => {
        console.log(res)
        if (res.data.errcode !== 0) { throw new Error() }
        let tempEntries = {}
        res.data.data.forEach((item) => {
          let entry = this.mapFileToEntry(item.name)
          if (entry !== null) {
            if (tempEntries[entry.name + entry.ext] === undefined) {
              tempEntries[entry.name + entry.ext] = { expand: false, files: [] }
              tempEntries[entry.name + entry.ext].files.push(entry)
            } else {
              tempEntries[entry.name + entry.ext].files.push(entry)
            }
          }
        })
        this.entries = tempEntries
      }).catch(err => {
        this.$message.error('获取文件列表失败')
        console.log(err)
      })
    },
    initUploadDialog(selectedEntry, selectedName) {
      if (selectedEntry === null) {
        this.fileInput = null
        this.fileNameInput = ''
        this.fileExtInput = ''
        this.changeNameAllow = true
        this.fileMajorInput = 0
        this.fileMinorInput = 0
        this.filePatchInput = 0
        this.uploadDialog = true
        this.minPatch = -1
      } else {
        console.log('non null selected entry: ', selectedEntry, selectedName)
        this.fileInput = null
        // 提取selectedName的文件名和拓展名
        this.fileNameInput = selectedName.split('.').slice(0, -1).join('.')
        this.fileExtInput = selectedName.split('.').pop()
        // 不允许更改
        this.changeNameAllow = false
        this.fileMajorInput = 0
        this.fileMinorInput = 0
        this.filePatchInput = 0
        this.uploadDialog = true
        // 找到最后的文件版本号
        let lastfile = selectedEntry.files[selectedEntry.files.length - 1]
        this.minPatch = 1000000 * lastfile.major + 1000 * lastfile.minor + lastfile.patch
        console.log('min vercode', this.minPatch)
      }
    },
    onFileInput() {
      console.log('on file input')
      if (this.fileInput !== undefined && this.fileInput !== null && this.fileInput.size >= 50000000) {
        this.$msgbox('文件大小超过50MB，JiHub暂时不支持过大的文件上传', '文件过大')
        this.fileInput = null
      }
      if (this.changeNameAllow && Object.keys(this.entries).indexOf(this.fileInput.name) !== -1) {
        this.$msgbox('重复文件，请检查数据库', '重复文件')
        this.fileInput = null
      }
      if (this.changeNameAllow) {
        this.fileNameInput = this.fileInput === undefined ? '' : this.fileInput.name.split('.').slice(0, -1).join('.')
        this.fileExtInput = this.fileInput === undefined ? '' : this.fileInput.name.split('.').pop()
      } else if (this.fileInput !== undefined && (this.fileInput.name.split('.').slice(0, -1).join('.') !== this.fileNameInput || this.fileInput.name.split('.').pop() !== this.fileExtInput)) {
        this.$msgbox('选择的文件与文件系列名不同，请注意检查', '文件名不同')
      }
      if (this.changeNameAllow && this.fileInput !== undefined && this.fileInput.name.indexOf('-') !== -1) {
        this.$msgbox('选中的文件名含有\'-\'，不过，您可以在JiHub修改此文件名', '含有非法符号')
      }
    },
    getTopicColor: topicSetting.getColor,
    getDarkColor: topicSetting.getDarkColor,
    getLinearGradient: topicSetting.getLinearGradient,
    getRadialGradient: topicSetting.getRadialGradient,
    checkLeadingZero(n) {
      if (n === '0') return true
      else return n[0] === '0'
    }
  },
  created() {
    this.updateDatabase()
  }
}


</script>

<template>
  <v-container>
    <v-snackbar timeout="-1" v-model="downloading" :color="getDarkColor(user.topic)" class="white--text">{{ downloadProgressBannerContent }}</v-snackbar>
    <v-snackbar timeout="-1" v-model="uploading" :color="getDarkColor(user.topic)" class="white--text">{{ uploadProgressBannerContent }}</v-snackbar>

    <v-row><v-col cols="12"><h1 :style="'color: ' + getDarkColor(user.topic)">团队数据库</h1></v-col></v-row>

    <v-row>
      <template v-for="(entry, name) in entries">
        <v-col :cols="entry.expand ? 12 : 4">
          <v-hover v-slot="{ hover }">
            <v-card min-height="13rem" :style="hover ? getRadialGradient(user.topic) : ''">
              <v-card-title><strong :style="'color: ' + getDarkColor(user.topic)">{{ name }}</strong></v-card-title>
              <v-card-text>
                <div>最新版本：<span class="float-end">{{ entry.files[entry.files.length - 1].major }}.{{ entry.files[entry.files.length - 1].minor }}.{{ entry.files[entry.files.length - 1].patch }}</span></div>
                <div>最新更新：<span class="float-end">{{ entry.files[entry.files.length - 1].time.toLocaleString() }}</span></div>
                <div>共有：<span class="float-end">{{entry.files.length}} 次上传</span></div>
              </v-card-text>
              <v-card-actions>
                <v-btn plain @click="() => initUploadDialog(entry, name)">上传新版本</v-btn>
                <v-spacer></v-spacer>
                <v-btn plain @click="() => download(entry.files[entry.files.length - 1])">下载最新版本</v-btn>
                <v-btn plain @click="entry.expand = !entry.expand">{{ entry.expand ? '收回' : '展开' }}</v-btn>
              </v-card-actions>

              <v-expand-transition>
                <div v-show="entry.expand">
                  <v-divider></v-divider>

                  <v-card-text>
                    <v-timeline dense>
                      <v-timeline-item :color="getTopicColor(user.topic)" v-for="file in entry.files" :key="file.time.getTime()">
                        <v-hover v-slot="{ hover }">
                          <v-card :style="'transition-duration: 0.5s;' + (hover ? getLinearGradient(user.topic) : '')">
                            <v-card-title>
                              <strong class="d-inline-block" :style="'width: 10rem; color: ' + getDarkColor(user.topic)">{{ file.major }}.{{ file.minor }}.{{ file.patch }}</strong>
                              <strong class="grey--text">上传于：{{ file.time.toLocaleString() }}</strong>
                              <v-spacer></v-spacer>
                              <v-btn :color="getDarkColor(user.topic)" class="white--text" @click="() => download(file)">下载</v-btn>
                            </v-card-title>
                          </v-card>
                        </v-hover>
                      </v-timeline-item>
                      <v-timeline-item :color="getTopicColor(user.topic)" icon="mdi-upload">
                        <v-hover v-slot="{ hover }">
                          <v-card @click="() => initUploadDialog(entry, name)" :style="'transition-duration: 0.5s;' + (hover ? getLinearGradient(user.topic) : '')">
                            <v-card-title>
                              <strong class="d-inline-block" :style="'width: 10rem; color: ' + getDarkColor(user.topic)">上传新版本</strong>
                              <v-spacer></v-spacer>
                            </v-card-title>
                          </v-card>
                        </v-hover>
                      </v-timeline-item>
                    </v-timeline>
                  </v-card-text>
                </div>
              </v-expand-transition>
            </v-card>
          </v-hover>
        </v-col>
      </template>

      <v-col cols="4">
        <v-hover v-slot="{hover}">
          <v-card @click="() => initUploadDialog(null)" min-height="13rem" max-height="13rem" :style="hover ? getRadialGradient(user.topic) : ''">
            <v-card-title><strong :style="'color: ' + getDarkColor(user.topic)">创建新的文件系列</strong></v-card-title>
            <v-card-text>上传一个文件，使用版本代码在JiHub上持续追溯，随时下载，项目成员也可上传最新进展</v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn @click="() => initUploadDialog(null)" plain>开始</v-btn>
            </v-card-actions>
          </v-card>
        </v-hover>
      </v-col>
    </v-row>

    <v-dialog v-model="uploadDialog" persistent>
      <v-card>
        <v-card-title>上传文件</v-card-title>
        <v-card-text>
          <v-form>
            <v-row>
              <v-col cols="6">
                <v-file-input
                    truncate-length="100"
                    show-size
                    v-model="fileInput"
                    label="上传文件"
                    @change="onFileInput"
                    outlined></v-file-input>
              </v-col>
              <v-col cols="4">
                <v-scroll-y-transition>
                  <v-text-field
                      :disabled="!changeNameAllow"
                      v-if="fileInput"
                      v-model="fileNameInput"
                      label="文件系列名"
                      :rules="[(v) => v.indexOf('-') === -1 ? true : '文件名不允许有\'-\'符号']"
                      prepend-icon="mdi-file"
                      counter="16"
                      outlined></v-text-field>
                </v-scroll-y-transition>
              </v-col>
              <v-col cols="2">
                <v-scroll-y-transition>
                  <v-text-field
                      :disabled="!changeNameAllow"
                      v-if="fileInput"
                      v-model="fileExtInput"
                      label="文件拓展名"
                      :rules="[(v) => v !== '', (v) => v.indexOf('.') === -1 ? true : '拓展名不允许\'.\'符号']"
                      prepend-icon="mdi-file"
                      counter="10"
                      outlined></v-text-field>
                </v-scroll-y-transition>
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="4">
                <v-scroll-y-transition>
                  <v-text-field
                      v-if="fileInput && fileNameInput !== '' && fileNameInput.indexOf('-') === -1 && fileNameInput.length <= 16 && fileExtInput !== '' && fileExtInput.length <= 10"
                      v-model="fileMajorInput"
                      label="主版本号"
                      :rules="[(v) => v !== '', (v) => v >= 0 ? true : '版本号必须为正整数', (v) => (v !== '0' && v.startsWith('0')) ? '不允许前导零' : true, (v) => v <= 999 ? true : '版本号太大了']"
                      prepend-icon="mdi-file"
                      counter="3"
                      outlined></v-text-field>
                </v-scroll-y-transition>
              </v-col>
              <v-col cols="4">
                <v-scroll-y-transition>
                  <v-text-field
                      v-if="fileInput && fileNameInput !== '' && fileNameInput.indexOf('-') === -1 && fileNameInput.length <= 16 && fileExtInput !== '' && fileExtInput.length <= 10"
                      v-model="fileMinorInput"
                      label="小版本号"
                      :rules="[(v) => v !== '', (v) => v >= 0 ? true : '版本号必须为正整数', (v) => (v !== '0' && v.startsWith('0')) ? '不允许前导零' : true, (v) => v <= 999 ? true : '版本号太大了']"
                      prepend-icon="mdi-file"
                      counter="3"
                      outlined></v-text-field>
                </v-scroll-y-transition>
              </v-col>
              <v-col cols="4">
                <v-scroll-y-transition>
                  <v-text-field
                      v-if="fileInput && fileNameInput !== '' && fileNameInput.indexOf('-') === -1 && fileNameInput.length <= 16 && fileExtInput !== '' && fileExtInput.length <= 10"
                      v-model="filePatchInput"
                      label="修订号"
                      :rules="[(v) => v !== '', (v) => v >= 0 ? true : '版本号必须为正整数', (v) => (v !== '0' && v.startsWith('0')) ? '不允许前导零' : true, (v) => v <= 999 ? true : '版本号太大了']"
                      prepend-icon="mdi-file"
                      counter="3"
                      outlined></v-text-field>
                </v-scroll-y-transition>
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        <template v-if="fileInput && fileNameInput !== '' && fileNameInput.indexOf('-') === -1 && fileNameInput.length <= 16 && fileExtInput !== '' && fileExtInput.length <= 10">
          <v-card-text>
            <v-card-title><strong>{{fileNameInput}}.{{fileExtInput}}</strong></v-card-title>
            <v-timeline dense>
              <v-timeline-item :color="getTopicColor(user.topic)" v-if="!changeNameAllow">
                <v-hover v-slot="{ hover }">
                  <v-card :style="'transition-duration: 0.5s;' + (hover ? getLinearGradient(user.topic) : '')">
                    <v-card-title>
                      <strong class="d-inline-block" :style="'width: 15rem; color: ' + getDarkColor(user.topic)">{{ Math.floor(minPatch / 1000000) }}.{{ Math.floor((minPatch / 1000) % 1000) }}.{{ minPatch % 1000 }}</strong>
                      <strong class="grey--text">此前的版本</strong>
                      <v-spacer></v-spacer>
                      <v-btn :color="getDarkColor(user.topic)" class="white--text" disabled>下载（不可用）</v-btn>
                    </v-card-title>
                  </v-card>
                </v-hover>
              </v-timeline-item>
              <v-timeline-item :color="getTopicColor(user.topic)" icon="mdi-upload">
                <v-hover v-slot="{ hover }">
                  <v-card :style="'transition-duration: 0.5s;' + (hover ? getLinearGradient(user.topic) : '')">
                    <v-card-title>
                      <strong class="d-inline-block" :style="'width: 15rem; color: ' + getDarkColor(user.topic)" v-if="changeNameAllow || (1000000 * fileMajorInput + 1000 * fileMinorInput + filePatchInput > minPatch)">{{ fileMajorInput }}.{{ fileMinorInput }}.{{ filePatchInput }}</strong>
                      <strong class="d-inline-block" :style="'width: 15rem; color: red'" v-else>{{ fileMajorInput }}.{{ fileMinorInput }}.{{ filePatchInput }}（过时或重复版本）</strong>
                      <strong class="grey--text">上传于：{{ new Date().toLocaleString() }}</strong>
                      <v-spacer></v-spacer>
                      <v-btn :color="getDarkColor(user.topic)" class="white--text" disabled>下载（不可用）</v-btn>
                    </v-card-title>
                  </v-card>
                </v-hover>
              </v-timeline-item>
            </v-timeline>
          </v-card-text>
        </template>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn plain color="red" @click="uploadDialog = !uploadDialog">取消</v-btn>
          <v-btn plain :color="getDarkColor(user.topic)" :disabled="!(fileInput && fileNameInput !== '' && fileNameInput.indexOf('-') === -1 && fileNameInput.length <= 16 && fileExtInput !== '' && fileExtInput.length <= 10 && fileExtInput.indexOf('.') === -1 && (changeNameAllow || (1000000 * fileMajorInput + 1000 * fileMinorInput + filePatchInput > minPatch)) && 0 <= fileMajorInput && fileMajorInput <= 999 && 0 <= fileMinorInput && fileMinorInput <= 999 && 0 <= filePatchInput && filePatchInput <= 999 && !checkLeadingZero(fileMajorInput) && !checkLeadingZero(fileMinorInput) && !checkLeadingZero(filePatchInput))" @click="upload">确定上传</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>

</template>

<style scoped>

</style>