<!--<template>-->
<!--  <v-container fluid>-->
<!--    <v-row align="center" justify="center" class="blue lighten-5" style="min-height: calc(100vh - 64px);">-->
<!--      <v-col cols="6">-->
<!--        <iframe src="../../login.html" ref="iframe" width="100%" height="500px" scrolling="no" frameborder="null"></iframe>-->
<!--      </v-col>-->
<!--      <v-col cols="12" sm="8" md="6" lg="4" class="d-flex justify-center">-->
<!--        <v-card class="elevation-12" style="max-width: 500px;">-->
<!--          <v-card-text class="mt-4 mb-4">-->
<!--            <v-form @submit.prevent="register">-->
<!--              <v-row>-->
<!--                <v-col cols="12" class="mb-3">-->
<!--                  <v-text-field label="用户名" v-model="username" :rules="registerRules.user_name" outlined dense></v-text-field>-->
<!--                </v-col>-->
<!--                <v-col cols="12" class="mb-3">-->
<!--                  <v-text-field label="邮箱" v-model="email" :rules="registerRules.user_email" outlined dense></v-text-field>-->
<!--                </v-col>-->
<!--                <v-col cols="12" class="mb-3">-->
<!--                  <v-text-field label="密码" v-model="password" :rules="registerRules.user_password" outlined dense type="password"></v-text-field>-->
<!--                </v-col>-->
<!--                <v-col cols="12" class="mb-3">-->
<!--                  <v-text-field label="确认密码" v-model="confirmPassword" :rules="registerRules.user_confirmPassword" outlined dense type="password"></v-text-field>-->
<!--                </v-col>-->
<!--                <v-col cols="12" class="mb-3">-->
<!--                  <v-btn color="blue darken-2" class="white&#45;&#45;text" :disabled="!valid()" block @click="register">注册账号</v-btn>-->
<!--                </v-col>-->
<!--                <v-col cols="12" class="text-center">-->
<!--                  <span class="caption grey&#45;&#45;text text&#45;&#45;darken-1">已有账号？</span>-->
<!--                  <v-btn color="transparent" class="grey&#45;&#45;text text&#45;&#45;darken-1" text @click="$router.push('/login')">前往登录</v-btn>-->
<!--                </v-col>-->
<!--              </v-row>-->
<!--            </v-form>-->
<!--          </v-card-text>-->
<!--        </v-card>-->
<!--      </v-col>-->
<!--    </v-row>-->
<!--  </v-container>-->
<!--</template>-->

<!--<script>-->
<!--import axios from "axios";-->
<!--import util from "@/views/util";-->
<!--import { sha256 } from 'js-sha256'-->

<!--export default {-->
<!--  name: "Register",-->
<!--  data() {-->
<!--    return {-->
<!--      username: '',-->
<!--      email: '',-->
<!--      password: '',-->
<!--      confirmPassword: '',-->
<!--      registerRules: {-->
<!--        user_name: [-->
<!--          function (v) {-->
<!--            return /^[\u4E00-\u9FA5A-Za-z0-9]+$/.test(v) || `用户名只能包含中文、英文或数字，且不能为空`;-->
<!--          },-->
<!--        ],-->
<!--        user_email: [-->
<!--          function (v) {-->
<!--            return /[\w]+@[A-Za-z]+(\.[A-Za-z0-9]+){1,2}/.test(v) || `非法的邮箱格式`;-->
<!--          },-->
<!--        ],-->
<!--        user_password: [-->
<!--          function (v) {-->
<!--            return /^.{6,}$/.test(v) || `密码长度至少为6位`;-->
<!--          },-->
<!--        ],-->
<!--        user_confirmPassword: [-->
<!--          function (v) {-->
<!--            return /^.{6,}$/.test(v) || `确认密码长度至少为6位`;-->
<!--          },-->
<!--        ],-->
<!--      },-->
<!--    }-->
<!--  },-->
<!--  methods: {-->
<!--    valid() {-->
<!--      return /^[\u4E00-\u9FA5A-Za-z0-9]+$/.test(this.username)-->
<!--        && /[\w]+@[A-Za-z]+(\.[A-Za-z0-9]+){1,2}/.test(this.email)-->
<!--        && /^.{6,}$/.test(this.password)-->
<!--        && /^.{6,}$/.test(this.confirmPassword)-->
<!--    },-->
<!--    register() {-->
<!--      if(!util.trim(this.username) || !util.trim(this.email)-->
<!--          || !util.trim(this.password) || !util.trim(this.confirmPassword)){-->
<!--        this.$message({-->
<!--          type: 'error',-->
<!--          message: "请完整填写所有注册信息"-->
<!--        });-->
<!--        return;-->
<!--      }-->
<!--      if (this.password !== this.confirmPassword) {-->
<!--        this.$message({-->
<!--          type: 'error',-->
<!--          message: "请保证密码和确认密码的一致性"-->
<!--        });-->
<!--        return-->
<!--      }-->
<!--      let secretPassword = sha256(this.password)-->
<!--      console.log(secretPassword)-->
<!--      axios.post("/api/register", {-->
<!--        username: this.username,-->
<!--        email: this.email,-->
<!--        password: secretPassword-->
<!--      })-->
<!--          .then((response) => {-->
<!--            console.log(response.data)-->
<!--            if (response.data.errcode === 1) {-->
<!--              this.$message({-->
<!--                type: 'error',-->
<!--                message: "发生未知错误，无法注册，请联系管理员"-->
<!--              });-->
<!--            } else if (response.data.errcode === 2) {-->
<!--              this.$message({-->
<!--                type: 'error',-->
<!--                message: "该邮箱已被使用"-->
<!--              });-->
<!--            } else if (response.data.errcode === 3) {-->
<!--              this.$message({-->
<!--                type: 'error',-->
<!--                message: "该用户名已被使用"-->
<!--              });-->
<!--            } else {-->
<!--              this.$message({-->
<!--                type: 'success',-->
<!--                message: "注册成功"-->
<!--              });-->
<!--              console.log("??????????")-->
<!--              window.location.href = '/login'-->
<!--            }-->
<!--          })-->
<!--          .catch((err) => {-->
<!--            console.error(err)-->
<!--            window.alert('发生未知错误，无法注册，请联系管理员')-->
<!--          })-->
<!--    }-->
<!--  }-->
<!--}-->
<!--</script>-->

<!--<style scoped>-->

<!--</style>-->