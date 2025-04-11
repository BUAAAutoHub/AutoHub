<template>
  <v-container>
    <v-row>
      <v-col cols="6">
        <v-container>
          <v-card class="fill-height">
            <v-card-title :style="getLinearGradient(user.topic)"><strong :style="'color : ' + getTopicColor(user.topic)">请输入待诊断的代码</strong></v-card-title>
            <v-divider></v-divider>
            <v-card-text class="d-flex flex-column" style="width: 100%; height: 100%">
              <textarea ref="cm" v-model="code" style="height: calc(100vh - 250px); width: 100%"></textarea>
              <!--<div ref="myChart" style="height: 300px"></div>-->
<!--              <v-textarea-->
<!--                  outlined-->
<!--                  label="Code"-->
<!--                  v-model="code"-->
<!--                  auto-grow-->
<!--                  color="blue"-->
<!--                  rows="5">-->
<!--                  outlined-->
<!--                  name="input-7-4"-->
<!--                  label="Code"-->
<!--                  v-model="code"-->
<!--                  height="350px"-->
<!--              </v-textarea>-->
            </v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn :color="getTopicColor(user.topic)" :loading="resultBusy" text :disabled="!valid()" @click="startDiagnosis()">确定</v-btn>
            </v-card-actions>
          </v-card>
        </v-container>
      </v-col>
      <v-col cols="6">
        <v-container>
          <v-card class="fill-height">
            <v-card-title :style="getLinearGradient(user.topic)"><strong :style="'color : ' + getTopicColor(user.topic)">代码诊断结果</strong></v-card-title>
            <v-divider></v-divider>
            <v-card-text class="d-flex flex-column" style="width: 100%; height: 100%">
<!--              &lt;!&ndash;<div ref="myChart" style="height: 300px"></div>&ndash;&gt;-->
<!--              <v-textarea-->
<!--                  outlined-->
<!--                  label="Result"-->
<!--                  v-model="result"-->
<!--                  auto-grow-->
<!--                  color="blue"-->
<!--                  rows="5"-->
<!--                  disabled-->
<!--              ></v-textarea>-->
<!--              {{ result }}-->
              <textarea ref="cm2" v-model="result" style="height: calc(100vh - 250px); width: 100%"></textarea>

            </v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn :color="getTopicColor(user.topic)" text @click="download">下载诊断结果</v-btn>
            </v-card-actions>
          </v-card>
        </v-container>
      </v-col>
    </v-row>
  </v-container>
</template>
<!--<template>-->
<!--  <v-container fluid>-->
<!--    <v-row align="center" justify="center" style="min-height: calc(100vh - 64px);">-->
<!--      <v-col cols="12" sm="8" md="6" lg="4" class="d-flex justify-center">-->
<!--        <v-card class="elevation-12">-->
<!--          <v-card-text class="mt-4 mb-4">-->
<!--            <v-form>-->
<!--              <v-row>-->
<!--                <v-col cols="12" class="mb-3">-->
<!--                  <v-text-field label="请输入要诊断的代码" v-model="userNameOrEmail" outlined></v-text-field>-->
<!--                </v-col>-->
<!--                <v-col cols="12" class="mb-3">-->
<!--                  <v-btn color="blue darken-2" class="white&#45;&#45;text" block @click="login">确定</v-btn>-->
<!--                </v-col>-->
<!--              </v-row>-->
<!--            </v-form>-->
<!--          </v-card-text>-->
<!--        </v-card>-->
<!--        <v-card class="elevation-12" style="max-width: 500px;">-->
<!--          <v-card-text class="mt-4 mb-4">-->
<!--            <v-form>-->
<!--              <v-row>-->
<!--                <v-col cols="12" class="mb-3">-->
<!--                  <v-text-field label="请输入要诊断的代码" v-model="userNameOrEmail" outlined></v-text-field>-->
<!--                </v-col>-->
<!--                <v-col cols="12" class="mb-3">-->
<!--                  <v-btn color="blue darken-2" class="white&#45;&#45;text" block @click="login">确定</v-btn>-->
<!--                </v-col>-->
<!--              </v-row>-->
<!--            </v-form>-->
<!--          </v-card-text>-->
<!--        </v-card>-->
<!--      </v-col>-->
<!--    </v-row>-->
<!--  </v-container>-->
<!--</template>-->

<script>
import axios from "axios";
import Cookies from 'js-cookie'
import * as CodeMirror from 'codemirror/lib/codemirror.js'
import "@/utils/cm-settings.js"
import topicSetting from "@/utils/topic-setting";
import {downloadStrAsFile} from "@/utils/file-system";

export default {
  name: "Diagnosis",
  data () {
    return {
      code: '',
      result: "暂无诊断结果。请在左侧输入代码并点击确认，以获取诊断结果。",
      resultBusy: false,
      cmEditor: null,
      cmViewer: null
    }
  },
  inject: ['user'],
  methods: {
    valid() {
      return this.code !== ''
    },
    getFromCookie() {
      if (Cookies.get('diag') !== undefined) {
        this.code = Cookies.get('diag')
        this.cmEditor.setValue(this.code)
        Cookies.remove('diag')
      } else {
        this.code = ''
        this.cmEditor.setValue(this.code)
      }
    },
    // 代码诊断
    startDiagnosis() {
      console.log(this.code)
      this.resultBusy = true;
      axios.post("/api/ai/CodeReview", {code: this.code})
          .then((response) => {
            console.log(response)
            if (response.data.errcode === 1) {
              this.$message({
                type: 'error',
                message: "未知错误"
              });
            } else {
              this.result = response.data.data
              this.cmViewer.setValue(this.result)
            }
          })
          .catch((err) => {
            console.error(err);
            this.result = null
          }).finally(() => {
            this.resultBusy = false;
      })
    },
    editorOnChange() {
      console.log('editor changed!')
      this.code = this.cmEditor.getValue()
    },
    getTopicColor: topicSetting.getDarkColor,
    getLinearGradient: topicSetting.getLinearGradient,
    downloadStrAsFile,
    download() {
      this.downloadStrAsFile(
          '# JiHub AI 代码诊断\n\n## 输入代码\n\n```\n' + this.code + '\n```\n\n## 代码诊断结果\n\n' + this.result + '\n\nGenerated by [JiHub AI](http://jihub.eastasia.cloudapp.azure.com/)\n\n' + new Date().toLocaleString(),
          `诊断结果-${new Date().toLocaleString()}.md`)
      this.$message.success('下载成功！')
    }
  },
  created() {
  },
  mounted() {
    this.cmEditor = CodeMirror.fromTextArea(this.$refs.cm, {
      theme: 'idea',
      lineNumbers: true,
      line: true,
      lineWrapping: true
    });

    this.cmEditor.on('change', this.editorOnChange)

    this.cmViewer = CodeMirror.fromTextArea(this.$refs.cm2, {
      mode: 'markdown',
      theme: 'idea',
      lineNumbers: true,
      line: true,
      lineWrapping: true,
      readOnly: true
    })

    this.cmViewer.setValue(this.result)
    this.getFromCookie()
  }
}
</script>

<style>
.CodeMirror {
  height: 50vh;
}
</style>