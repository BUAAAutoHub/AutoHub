<template>
  <v-container fluid>
    <v-row align="center" justify="center" class="lighten-5 login-background"
           :style="'min-height: calc(100vh - 64px); background-image: url(' + bingPicOfTheDayUrl + ');'">
      <v-col cols="12">
        <v-container fluid class="no-blur" >
          <v-row>
            <v-col cols="12" sm="12" md="6" lg="6" xl="6" >
              <iframe src="../../login-logo.html" ref="iframe" width="100%" height="500px" scrolling="no" frameborder="null"></iframe>
            </v-col>
            <v-col cols="12" sm="12" md="6" lg="6" xl="6">
              <v-card class="elevation-12 mx-sm-auto" style="max-width: 500px;">
                <v-card-text class="mt-4 mb-4">
                  <v-form v-if="!flag" @submit.prevent="register" >

              <v-row>
                <v-col cols="12" class="mb-3">
                  <v-text-field label="用户名" v-model="registerData.username" :rules="registerData.registerRules.user_name" outlined dense></v-text-field>
                </v-col>
                <v-col cols="12" class="mb-3">
                  <v-text-field label="邮箱" v-model="registerData.email" :rules="registerData.registerRules.user_email" outlined dense></v-text-field>
                </v-col>
                <v-col cols="12" class="mb-3">
                  <v-text-field label="密码" v-model="registerData.password" :rules="registerData.registerRules.user_password" outlined dense type="password"></v-text-field>
                </v-col>
                <v-col cols="12" class="mb-3">
                  <v-text-field label="确认密码" v-model="registerData.confirmPassword" :rules="registerData.registerRules.user_confirmPassword" outlined dense type="password"></v-text-field>
                </v-col>
                <v-col cols="12" class="mb-3">
                  <v-btn color="blue darken-2" class="white--text" :disabled="!registerValid()" block @click="register">注册账号</v-btn>
                </v-col>
                <v-col cols="12" class="text-center">
                  <span class="caption grey--text text--darken-1">已有账号？</span>
                  <v-btn color="transparent" class="grey--text text--darken-1" text @click="gotoLogin">前往登录</v-btn>
                </v-col>
              </v-row>
            </v-form>
            <v-form v-if= "flag" @submit.prevent="login">
                    <v-row>
                      <v-col cols="12" class="mb-3">
                        <v-text-field label="用户名或邮箱" v-model="loginData.userNameOrEmail" outlined dense></v-text-field>
                      </v-col>
                      <v-col cols="12" class="mb-3">
                        <v-text-field label="密码" v-model="loginData.password" outlined dense type="password"></v-text-field>
                      </v-col>
                      <v-col cols="12" class="mb-3">
                        <v-checkbox label="不以加密形式传输密码（适用于前后端测试）" v-model="loginData.noEncrypt" hide-details></v-checkbox>
                      </v-col>
                      <v-col cols="12" class="mb-3">
                        <v-btn color="blue darken-2" class="white--text" :disabled="!loginValid()" block @click="login">登录</v-btn>
                      </v-col>
                      <v-col cols="12" class="text-center">
                        <span class="caption grey--text text--darken-1">没有账号？</span>
                        <v-btn color="transparent" class="grey--text text--darken-1" text @click="gotoRegister">前往注册</v-btn>
                      </v-col>
                    </v-row>
                  </v-form>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </v-container>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import util from './util'
import Cookies from 'js-cookie'
import axios from "axios"
import { sha256 } from 'js-sha256'

// if (Cookies.get('manager') !== undefined) { // 此时管理员在用户端
//   window.location.href = '/allProject';
// } else if (Cookies.get('user') !== undefined) {
//   // alert('您已处于登录状态');
//   let user = Cookies.get('user')
//   if (user.status === 'C') { // 当前用户为管理员
//     window.location.href = '/manager/home'
//   } else { // 当前用户为普通用户
//     window.location.href = '/allProject';
//   }
// }
// if (Cookies.get('user') !== undefined) {
//   // alert('您已处于登录状态');
//   window.location.href = '/allProject';
// }

export default {
  name: "login",
  data() {
    return {
      flag: true,
      loginData: {
        userNameOrEmail: '',
        password: '',
        noEncrypt: false
      },
      registerData: {
        username: '',
        email: '',
        password: '',
        confirmPassword: '',
        registerRules: {
          user_name: [
            function (v) {
              return /^[\u4E00-\u9FA5A-Za-z0-9]+$/.test(v) || `用户名只能包含中文、英文或数字，且不能为空`;
            },
          ],
          user_email: [
            function (v) {
              return /[\w]+@[A-Za-z0-9]+(\.[A-Za-z0-9]+){1,2}/.test(v) || `非法的邮箱格式`;
            },
          ],
          user_password: [
            function (v) {
              return /^.{6,}$/.test(v) || `密码长度至少为6位`;
            },
          ],
          user_confirmPassword: [
            function (v) {
              return /^.{6,}$/.test(v) || `确认密码长度至少为6位`;
            },
          ],
        },
      },
      bingPicOfTheDayUrl: ''
    }
  },
  methods: {
    gotoLogin() {
      this.registerDataClear()
      this.loginDataClear()
      this.flag = true
    },
    gotoRegister() {
      this.registerDataClear()
      this.loginDataClear()
      this.flag = false
    },
    loginValid() {
      return this.loginData.userNameOrEmail !== '' && this.loginData.password !== ''
    },
    registerValid() {
      return /^[\u4E00-\u9FA5A-Za-z0-9]+$/.test(this.registerData.username)
          && /[\w]+@[A-Za-z0-9]+(\.[A-Za-z0-9]+){1,2}/.test(this.registerData.email)
          && /^.{6,}$/.test(this.registerData.password)
          && /^.{6,}$/.test(this.registerData.confirmPassword)
    },
    loginDataClear() {
      this.loginData.userNameOrEmail = ''
      this.loginData.password = ''
      this.loginData.noEncrypt = false
    },
    registerDataClear() {
      this.registerData.username = ''
      this.registerData.email = ''
      this.registerData.password = ''
      this.registerData.confirmPassword = ''
    },
    async login() {
      if(!util.trim(this.loginData.userNameOrEmail) || !util.trim(this.loginData.password)){
        this.$message({
          type: 'error',
          message: "用户名或邮箱、密码不能为空"
        });
        return;
      }
      // console.log(this.userNameOrEmail)
      // console.log(this.password)
      // console.log({
      //   userNameOrEmail: this.userNameOrEmail,
      //   password: this.password
      // })
      let secretPassword = this.loginData.noEncrypt ? this.loginData.password : sha256(this.loginData.password)
      console.log(secretPassword)
      axios.post("/api/login", {
        userNameOrEmail: this.loginData.userNameOrEmail,
        password: secretPassword
      })
          .then((response) => {
            console.log(response.data)
            if (response.data.errcode === 1) {
              this.$message({
                type: 'error',
                message: "用户不存在"
              });
            } else if (response.data.errcode === 2) {
              this.$message({
                type: 'error',
                message: "密码错误，如果你是早些时候注册的账户，试试不以加密形式传输密码"
              });
            } else if (response.data.errcode === 3) {
              this.$message({
                type: 'error',
                message: "您的账户目前已被禁用，请联系管理员"
              });
            } else {
              Cookies.set('user', JSON.stringify(response.data.data))
              this.$message({
                type: 'success',
                message: "登录成功"
              });
              console.log(response.data.data)
              if (response.data.data.auth !== 1) { // 管理员
                window.location.href = '/manager/home'
              } else { // 用户
                window.location.href = '/allProject'
              }
              this.loginDataClear()
              this.registerDataClear()
            }
          })
          .catch((err) => {
            console.error(err);
          })
    },
    register() {
      if(!util.trim(this.registerData.username) || !util.trim(this.registerData.email)
          || !util.trim(this.registerData.password) || !util.trim(this.registerData.confirmPassword)){
        this.$message({
          type: 'error',
          message: "请完整填写所有注册信息"
        });
        return;
      }
      if (this.registerData.password !== this.registerData.confirmPassword) {
        this.$message({
          type: 'error',
          message: "请保证密码和确认密码的一致性"
        });
        return
      }
      let secretPassword = sha256(this.registerData.password)
      console.log(secretPassword)
      axios.post("/api/register", {
        username: this.registerData.username,
        email: this.registerData.email,
        password: secretPassword
      })
          .then((response) => {
            console.log(response.data)
            if (response.data.errcode === 1) {
              this.$message({
                type: 'error',
                message: "发生未知错误，无法注册，请联系管理员"
              });
            } else if (response.data.errcode === 2) {
              this.$message({
                type: 'error',
                message: "该邮箱已被使用"
              });
            } else if (response.data.errcode === 3) {
              this.$message({
                type: 'error',
                message: "该用户名已被使用"
              });
            } else {
              this.$message({
                type: 'success',
                message: "注册成功"
              });
              this.loginData.userNameOrEmail = this.registerData.username
              this.registerDataClear()
              this.flag = true
            }
          })
          .catch((err) => {
            console.error(err)
            window.alert('发生未知错误，无法注册，请联系管理员')
          })
    }
  },
  created() {
    // 若去掉注释，会报错！
    // axios.get('/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=zh-CN')
    //     .then((response) => {
    //       console.log(response.data.images[0].url)
    //       this.bingPicOfTheDayUrl = 'https://cn.bing.com' + response.data.images[0].url
    //     })
    //     .catch((err) => {
    //       console.error(err);
    //     })
  }
}
</script>

<style scoped>
.login-background {
  background-image: url('https://cn.bing.com//th?id=OHR.SaksunFaroe_ZH-CN7150180007_1920x1080.jpg&rf=LaDigue_1920x1080.jpg&pid=hp');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;

}

.login-background::before {
  content: "";
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  top: 0;
  background: linear-gradient(rgba(70, 118, 184, 80%), rgba(128, 128, 128, .8));
  background-size: cover;
}

.no-blur {
  backdrop-filter: blur(20px);
}
</style>