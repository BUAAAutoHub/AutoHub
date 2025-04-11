<template>
  <v-container fluid fill-height :style="getRadialGradient(user.topic)">
    <v-row align="center" justify="center">
      <v-col cols="12">
        <v-card class="mx-auto" width="800" height="300" padding="16">
          <v-img
              :src="getIdenticon(this.user.name, 100, 'user')"
              height="300"
              gradient="to bottom, rgba(255,255,255,.3), rgba(255,255,255,.9) 30%, rgba(255,255,255,.9) 70%, rgba(255,255,255,.3)"
          >
            <v-card-title class="headline font-weight text-left">查看个人信息</v-card-title>
            <v-divider></v-divider>
            <v-row align="center">
              <v-col cols="3" class="text-center">
                <v-avatar
                    color="indigo"
                    size="100"
                >
                  <v-img :src="getIdenticon(this.user.name, 100, 'user')"></v-img>
                </v-avatar>
                <strong class="d-block"> {{ userInfo.username }} </strong>
              </v-col>
              <v-col cols="8">
                <v-text-field label="用户名" v-model="userInfo.username" :rules="editRules.username" outlined
                              dense></v-text-field>
                <v-text-field label="邮箱" v-model="userInfo.email" :rules="editRules.email" outlined
                              dense></v-text-field>
              </v-col>
            </v-row>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn color="red" text @click="openModifyTokenDialog">修改token</v-btn>
              <v-btn color="red" text @click="openChangePasswordDialog">修改密码</v-btn>
              <v-btn color="primary" text :disabled="!editValid()" @click="save">保存</v-btn>
              <v-btn color="primary" text @click="back">返回</v-btn>
            </v-card-actions>
          </v-img>
        </v-card>
      </v-col>
    </v-row>
    <v-dialog v-if="showChangePassword" v-model="showChangePassword" width="500">
      <template>
        <v-container class="pa-0">
          <v-card>
            <v-card-title class="headline font-weight text-left">修改密码</v-card-title>
            <v-divider></v-divider>
            <v-card-text>
              <v-row>
                <v-col cols="4">
                  <div class="input-label">原密码：</div>
                </v-col>
                <v-col cols="8">
                  <div class="input-field">
                    <v-text-field v-model="oldPassword" :rules="registerRules.user_oldPassword" outlined dense
                                  type="password"></v-text-field>
                  </div>
                </v-col>
              </v-row>
              <v-row>
                <v-col cols="4">
                  <div class="input-label">新密码：</div>
                </v-col>
                <v-col cols="8">
                  <div class="input-field">
                    <v-text-field v-model="newPassword" :rules="registerRules.user_newPassword" outlined dense
                                  type="password"></v-text-field>
                  </div>
                </v-col>
              </v-row>
              <v-row>
                <v-col cols="4">
                  <div class="input-label">确认新密码：</div>
                </v-col>
                <v-col cols="8">
                  <div class="input-field">
                    <v-text-field v-model="confirmNewPassword" :rules="registerRules.user_confirmNewPassword" outlined
                                  dense type="password"></v-text-field>
                  </div>
                </v-col>
              </v-row>
            </v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn color="red" text @click="closeChangePasswordDialog">取消</v-btn>
              <v-btn color="blue" text :disabled="!valid()" @click="changePassword">确认修改</v-btn>
            </v-card-actions>
          </v-card>
        </v-container>
      </template>
    </v-dialog>
    <el-dialog
        title="修改token"
        :visible.sync="showModifyToken"
        width="50%"
        :before-close="cancelModifyToken">
      <el-form label-position="lab" label-iwdth="80px" ref="newReviewForm">
        <el-form-item label="token">
          <el-input type="textarea" :rows="3" v-model="token"></el-input>
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="cancelModifyToken">取 消</el-button>
        <el-button type="primary" @click="modifyToken">确 定</el-button>
      </span>
    </el-dialog>
  </v-container>
</template>

<script>
import axios from "axios";
import util from "@/views/util";
import Cookies from "js-cookie";
import getIdenticon from "@/utils/identicon";
import {sha256} from "js-sha256";
import topicSetting from '@/utils/topic-setting.js'

export default {
  name: "profile",
  inject: {
    user: {default: null},
    reload: {default: null},
    updateUser: {default: null},
  },
  data() {
    return {
      // 用户信息
      showedUserName: '', // 显示在头像下方的用户名
      userInfo: {
        username: '',
        email: '',
        avatar: '',
      },
      editRules: {
        username: [
          function (v) {
            return /^[\u4E00-\u9FA5A-Za-z0-9]+$/.test(v) || `用户名只能包含中文、英文或数字，且不能为空`;
          },
        ],
        email: [
          function (v) {
            return /[\w]+@[A-Za-z0-9]+(\.[A-Za-z0-9]+){1,2}/.test(v) || `非法的邮箱格式`;
          },
        ],
      },
      // 修改密码对话框的显示
      showChangePassword: false,
      //
      showModifyToken: false,
      // 修改密码相关变量
      oldPassword: '',
      newPassword: '',
      confirmNewPassword: '',
      registerRules: {
        user_oldPassword: [
          function (v) {
            return /^.+$/.test(v) || `旧密码不能为空`;
          },
        ],
        user_newPassword: [
          function (v) {
            return /^.{6,}$/.test(v) || `新密码长度至少为6位`;
          },
        ],
        user_confirmNewPassword: [
          function (v) {
            return /^.{6,}$/.test(v) || `确认密码长度至少为6位`;
          },
        ],
      },
      token: '',
    };
  },
  created() {
    this.showProfile()
  },
  methods: {
    getIdenticon,
    editValid() {
      return /^[\u4E00-\u9FA5A-Za-z0-9]+$/.test(this.userInfo.username)
          && /[\w]+@[A-Za-z0-9]+(\.[A-Za-z0-9]+){1,2}/.test(this.userInfo.email);
    },
    valid() {
      return /^.+$/.test(this.oldPassword)
          && /^.{6,}$/.test(this.newPassword)
          && /^.{6,}$/.test(this.confirmNewPassword)
    },
    showProfile() {
      // 调用后端接口获取用户信息
      axios.post("/api/showProfile", {userId: this.user.id})
          .then((response) => {
            console.log(response)
            if (response.data.errcode === 1) {
              this.$message({
                type: 'error',
                message: "获取用户信息失败"
              });
            } else {
              this.showedUserName = response.data.data.userName
              this.userInfo.username = response.data.data.userName
              this.userInfo.email = response.data.data.userEmail
            }
          })
          .catch((err) => {
            console.error(err);
            this.userMessages = null
          })
    },
    // 保存用户信息
    save() {
      // 获取用户修改后的用户名和邮箱
      const name = this.userInfo.username
      const email = this.userInfo.email
      if (!util.trim(name) || !util.trim(email)) {
        this.$message({
          type: 'error',
          message: "用户名或邮箱不能为空"
        });
        return;
      } else if (name.length > 8) {
        this.$message({
          type: 'error',
          message: "用户名不能超过8个字符"
        });
        return
      }
      console.log(name)
      console.log(email)
      // 调用后端接口保存用户信息
      axios.post('/api/editProfile', {
        userId: this.user.id,
        userName: name,
        userEmail: email
      })
          .then(response => {
            console.log(1111111)
            if (response.data.errcode === 0) {
              this.$message({
                type: 'success',
                message: "保存成功"
              });
              this.showProfile();
              console.log(response.data.data)
              Cookies.set('user', JSON.stringify(response.data.data))
              this.updateUser()
              console.log("1241442342")
              console.log(Cookies.get('user'))
              console.log(this.user)
            } else if (response.data.errcode === 1) {
              this.$message({
                type: 'error',
                message: "保存失败"
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
            }
          })
          .catch(error => {
            console.log(error)
          })
    },
    // 修改密码
    async changePassword() {
      if (!util.trim(this.oldPassword)) {
        this.$message({
          type: 'error',
          message: "原密码不能为空"
        });
        return;
      }
      if (!util.trim(this.newPassword)) {
        this.$message({
          type: 'error',
          message: "新密码不能为空"
        });
        return;
      }
      if (this.newPassword !== this.confirmNewPassword) {
        this.$message({
          type: 'error',
          message: "请保证新密码和确认新密码内容一致"
        });
        return;
      }
      let secretOldPassword = sha256(this.oldPassword)
      let secretNewPassword = sha256(this.newPassword)
      console.log(secretOldPassword)
      console.log(secretNewPassword)
      axios.post('/api/user/information/password', {
        userId: this.user.id,
        oldPassword: secretOldPassword,
        newPassword: secretNewPassword,
      })
          .then((response) => {
            if (response.data.errcode === 1) { // TODO
              this.$message({
                type: 'error',
                message: "请重新确认原密码"
              });
            } else {
              this.showChangePassword = false;
              this.oldPassword = ''
              this.newPassword = ''
              this.confirmNewPassword = ''
              this.$message({
                type: 'success',
                message: "密码修改成功"
              });
            }
          })
          .catch(error => {
            console.log(error)
          })
    },
    async modifyToken() {
      if (!util.trim(this.token)) {
        this.$message.error('token不能为空！')
        return;
      }
      axios.post('/api/modifyToken', {
        userId: this.user.id,
        token: this.token
      }).then((response) => {
        if (response.data.errcode === 0) {
          this.$message.success(response.data.message)
        }
      })
      this.showModifyToken = false
      this.token = ''
    },
    cancelModifyToken() {
      this.showModifyToken = false
      this.token = ''
    },
    openChangePasswordDialog() {
      this.oldPassword = ''
      this.newPassword = ''
      this.confirmNewPassword = ''
      this.showChangePassword = true;
    },
    openModifyTokenDialog() {
      this.showModifyToken = true;
      axios.post('/api/checkToken', {
        userId: this.user.id
      }).then((response) => {
        if (response.data.data.flag === 0) {
          this.$message.info('you have not set token yet')
        } else {
          this.$message.info('you have already set token')
        }
      })
    },
    closeChangePasswordDialog() {
      this.showChangePassword = false;
      this.oldPassword = ''
      this.newPassword = ''
      this.confirmNewPassword = ''
    },
    back() {

      this.$router.go(-1);
    },
    getRadialGradient: topicSetting.getRadialGradient,
  },
};
</script>

<style scoped>
.v-text-field {
  margin: 16px;
}

.v-card-actions {
  margin-top: 8px;
}

.v-card-text {
  margin-top: 24px !important;
}

.input-label {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  height: 48px;
  font-size: 16px;
}

.input-field {
  display: flex;
  align-items: center;
  height: 48px;
}

/*
.input-row {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}
.input-label {
  width: 120px;
  text-align: right;
  margin-right: 16px;
  font-weight: bold;
}
.input-field {
  flex: 1;
}
*/
</style>
