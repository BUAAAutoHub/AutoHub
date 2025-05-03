<template>
    <v-app id="main_page">
      <v-app-bar app clipped-left ref="appBar" color="white" dark extension-height="50" :absolute="true" :src=topic>
        <v-toolbar-title style="font-weight: bold"> <span style="font-size: 32px;">JiHub</span><span v-if="existManager()">
            - Admin
            Override</span></v-toolbar-title>
  
        <v-spacer></v-spacer>
  
  
        <template>
          <v-badge :content="this.noReadNoticeList.length" :value="this.noReadNoticeList.length > 0" color="red" overlap class="mr-4">
            <v-icon v-if="existUser()" @click="checkClock" style="font-size: 40px;">mdi-clock-outline</v-icon>
          </v-badge>
        </template>
        <v-tooltip bottom>
          <template v-slot:activator="{ on, attrs }">
            <v-btn v-if="existManager()" icon color="white" v-bind="attrs" v-on="on" @click="gotoManagerPage"
              style="font-size: 24px;">
              <v-icon>mdi-link-variant</v-icon>
            </v-btn>
          </template>
          <span style="font-size: 24px;">管理端</span>
        </v-tooltip>
  
        <v-menu offset-y :close-on-content-click="false">
          <template v-slot:activator="{ on, attrs }">
            <v-chip ref="userPage" v-if="user" outlined v-bind="attrs" v-on="on" style="font-size: 20px;">{{ user.name }}</v-chip>
            <div v-bind="attrs" v-on="on">
          <v-img :src="getIdenticon(user.name, 40, 'user')" contain width="50" height="50" style="border-radius: 50%;"></v-img>
          </div>
          </template>
          <v-card v-if="user" min-width="300px">
            <v-img gradient="transparent 0%, rgba(255, 255, 255, 80%) 80%, white 100%"
              :src="getIdenticon(user.name, 300, 'user')" class="shades--text black--text align-end">
              <v-card-title style="font-weight: bold; font-size: xx-large;">欢迎, {{ user.name }}</v-card-title>
            </v-img>
  
            <v-list>
              <v-list-item link to="/profile">
                <v-list-item-title>个人信息</v-list-item-title>
              </v-list-item>
              <v-list-item link to="/topic">
                <v-list-item-title>主题设置</v-list-item-title>
              </v-list-item>
              <v-list-item link @click="logoff()">
                <v-list-item-title>退出登录</v-list-item-title>
              </v-list-item>
            </v-list>
          </v-card>
  
          <v-card v-else min-width="200px" link to="/login">
            <v-card-title>请登录</v-card-title>
          </v-card>
        </v-menu>
  
        <template v-if="showLabel()" v-slot:extension>
          <v-tab link to="/allProject/">
            <v-icon large>mdi-home-outline</v-icon>
            <span style="font-size: 24px;">主页</span>
          </v-tab>
  
  
  
          <v-menu :open-on-hover="true" :close-on-click="false" :close-on-content-click="false"
            transition="scroll-y-transition" v-if="user.projects.length" offset-y>
            <template v-slot:activator="{ on, attrs }">
              <v-btn text v-bind="attrs" v-on="on">
                <span style="font-size: 24px;">规划</span>
                <v-icon v-if="attrs['aria-expanded'] === 'false'" right>
                  mdi-menu-down
                </v-icon>
                <v-icon v-else>
                  mdi-menu-up
                </v-icon>
              </v-btn>
            </template>
  
            <v-card min-width="200px">
              <v-list class="grey lighten-3">
  
                <v-list-item :style="'color: ' + getDarkColor(user.topic)" link :to="'/allTask'">
                  <v-list-item-avatar>
                    <v-icon :color="getDarkColor(user.topic)">mdi-ballot-outline</v-icon>
                  </v-list-item-avatar>
  
                  <v-list-item-content>
                    <v-list-item-title>任务列表</v-list-item-title>
                  </v-list-item-content>
                </v-list-item>
  
                <v-list-item :style="'color: ' + getDarkColor(user.topic)" link :to="'/allPerson'">
                  <v-list-item-avatar>
                    <v-icon :color="getDarkColor(user.topic)">mdi-account-outline</v-icon>
                  </v-list-item-avatar>
  
                  <v-list-item-content>
                    <v-list-item-title>人员列表</v-list-item-title>
                  </v-list-item-content>
                </v-list-item>
  
                <v-list-item :style="'color: ' + getDarkColor(user.topic)" @click="gotoPic">
                  <v-list-item-avatar>
                    <v-icon :color="getDarkColor(user.topic)">mdi-align-vertical-bottom</v-icon>
                  </v-list-item-avatar>
                  <v-list-item-content>
                    <v-list-item-title>图表展示</v-list-item-title>
                  </v-list-item-content>
                </v-list-item>
                <v-list-item :style="'color: ' + getDarkColor(user.topic)" link :to="'/userAuth'">
                  <v-list-item-avatar>
                    <v-icon :color="getDarkColor(user.topic)">mdi-account-lock-open</v-icon>
                  </v-list-item-avatar>
                  <v-list-item-content>
                    <v-list-item-title>权限管理</v-list-item-title>
                  </v-list-item-content>
                </v-list-item>
              </v-list>
            </v-card>
  
          </v-menu>
  
  
          <v-menu :open-on-hover="true" :close-on-click="false" :close-on-content-click="false"
            transition="scroll-y-transition" v-if="user.projects.length" offset-y>
            <template v-slot:activator="{ on, attrs }">
              <v-btn text v-bind="attrs" v-on="on">
                <span style="font-size: 24px;">开发</span>
                <v-icon v-if="attrs['aria-expanded'] === 'false'" right>
                  mdi-menu-down
                </v-icon>
                <v-icon v-else>
                  mdi-menu-up
                </v-icon>
              </v-btn>
            </template>
  
            <v-card min-width="200px">
              <v-list class="grey lighten-3">
                <v-list-item-group>
                  <v-list-item :style="'color: ' + getDarkColor(user.topic)"
                    @click="codeReviewExpanded = !codeReviewExpanded" class="parent-item">
                    <v-list-item-avatar>
                      <v-icon :color="getDarkColor(user.topic)">mdi-account-edit</v-icon>
                    </v-list-item-avatar>
                    <v-list-item-content>
                      <v-list-item-title>代码评审</v-list-item-title>
                    </v-list-item-content>
                    <v-list-item-action>
                      <v-icon>{{ codeReviewExpanded ? 'mdi-chevron-up' : 'mdi-chevron-down' }}</v-icon>
                    </v-list-item-action>
                  </v-list-item>
                  <v-expand-transition>
                    <div v-if="codeReviewExpanded" class="child-items">
                      <v-list-item link :to="'/commitReview'" style="padding-left: 30px">
                        <v-list-item-avatar>
                          <v-icon :color="getDarkColor(user.topic)">mdi-source-branch-check</v-icon>
                        </v-list-item-avatar>
                        <v-list-item-content>
                          <v-list-item-title>Commit评审</v-list-item-title>
                        </v-list-item-content>
                      </v-list-item>
                      <v-list-item link :to="'/prReview'" style="padding-left: 30px">
                        <v-list-item-avatar>
                          <v-icon :color="getDarkColor(user.topic)">mdi-source-pull</v-icon>
                        </v-list-item-avatar>
                        <v-list-item-content>
                          <v-list-item-title>PR评审</v-list-item-title>
                        </v-list-item-content>
                      </v-list-item>
                      <v-list-item link :to="'/newPR'" style="padding-left: 30px">
                        <v-list-item-avatar>
                          <v-icon :color="getDarkColor(user.topic)">mdi-check-circle-outline</v-icon>
                        </v-list-item-avatar>
                        <v-list-item-content>
                          <v-list-item-title>新建PR</v-list-item-title>
                        </v-list-item-content>
                      </v-list-item>
                      <v-list-item link :to="'/newIssue'" style="padding-left: 30px">
                        <v-list-item-avatar>
                          <v-icon :color="getDarkColor(user.topic)">mdi-check-circle-outline</v-icon>
                        </v-list-item-avatar>
                        <v-list-item-content>
                          <v-list-item-title>新建Issue</v-list-item-title>
                        </v-list-item-content>
                      </v-list-item>
                    </div>
                  </v-expand-transition>
                </v-list-item-group>
  
  
                <v-list-item :style="'color: ' + getDarkColor(user.topic)" link :to="'/dev'">
                  <v-list-item-avatar>
                    <v-icon :color="getDarkColor(user.topic)">mdi-microsoft-visual-studio-code</v-icon>
                  </v-list-item-avatar>
                  <v-list-item-content>
                    <v-list-item-title>代码</v-list-item-title>
                  </v-list-item-content>
                </v-list-item>
  
                <v-list-item :style="'color: ' + getDarkColor(user.topic)" link :to="'/user/ai/diagnosis'">
                  <v-list-item-avatar>
                    <v-icon :color="getDarkColor(user.topic)">mdi-atom-variant</v-icon>
                  </v-list-item-avatar>
                  <v-list-item-content>
                    <v-list-item-title>代码诊断</v-list-item-title>
                  </v-list-item-content>
                </v-list-item>
  
                <v-list-item :style="'color: ' + getDarkColor(user.topic)" link :to="'/user/ai/testdata'">
                  <v-list-item-avatar>
                    <v-icon :color="getDarkColor(user.topic)">mdi-palette-outline</v-icon>
                  </v-list-item-avatar>
                  <v-list-item-content>
                    <v-list-item-title>生成测试数据</v-list-item-title>
                  </v-list-item-content>
                </v-list-item>
                <v-list-item :style="'color: ' + getDarkColor(user.topic)" link :to="'/user/database'">
                  <v-list-item-avatar>
                    <v-icon :color="getDarkColor(user.topic)">mdi-database</v-icon>
                  </v-list-item-avatar>
                  <v-list-item-content>
                    <v-list-item-title>团队数据库</v-list-item-title>
                  </v-list-item-content>
                </v-list-item>
              </v-list>
            </v-card>
  
          </v-menu>
  
          <v-menu :open-on-hover="true" :close-on-click="false" :close-on-content-click="false"
            transition="scroll-y-transition" v-if="user.projects.length" offset-y>
            <template v-slot:activator="{ on, attrs }">
              <v-btn text v-bind="attrs" v-on="on">
                <span style="font-size: 24px;">沟通</span>
                <v-icon v-if="attrs['aria-expanded'] === 'false'" right>
                  mdi-menu-down
                </v-icon>
                <v-icon v-else>
                  mdi-menu-up
                </v-icon>
              </v-btn>
            </template>
  
            <v-card min-width="200px">
              <v-list class="grey lighten-3">
  
                <!-- <v-dialog width="1300" v-model="dialog" fullscreen transition="dialog-bottom-transition" hide-overlay>
                  <template v-slot:activator="{ on, attrs }">
                    <v-list-item :style="'color: ' + getDarkColor(user.topic)">
                      <v-list-item-avatar>
                        <v-icon :color="getDarkColor(user.topic)">mdi-file-document-outline</v-icon>
                      </v-list-item-avatar>
                      <v-list-item-content>
                        <v-list-item-title v-bind="attrs" v-on="on">共享文档</v-list-item-title>
                      </v-list-item-content>
                    </v-list-item>
                  </template>
                  <AllFile @close="closeDocument" @open="openDocument"></AllFile>
                </v-dialog> -->
                <v-list-item :style="'color: ' + getDarkColor(user.topic)" link :to="'/allFile'">
                  <v-list-item-avatar>
                    <v-icon :color="getDarkColor(user.topic)">mdi-file-document-outline</v-icon>
                  </v-list-item-avatar>
  
                  <v-list-item-content>
                    <v-list-item-title>共享文档</v-list-item-title>
                  </v-list-item-content>
                </v-list-item>
  
                <v-list-item :style="'color: ' + getDarkColor(user.topic)" link :to="'/user/chat'">
                  <v-list-item-avatar>
                    <v-icon :color="getDarkColor(user.topic)">mdi-account-group-outline</v-icon>
                  </v-list-item-avatar>
  
                  <v-list-item-content>
                    <v-list-item-title>讨论室</v-list-item-title>
                  </v-list-item-content>
                </v-list-item>
              </v-list>
            </v-card>
  
          </v-menu>
          <!-- <v-tabs v-model="routeSelect"> -->
          <!-- <v-tab link to="/allProject/">项目</v-tab> -->
          <!-- <v-tab link to="/allProject/allTask/">Plan</v-tab>
            <v-tab link to="/dev/">Dev</v-tab>
            <v-tab link to="/allProject/allPerson">Team</v-tab> -->
          <!--          <v-tab-->
          <!--                  v-for="project in user.projects"-->
          <!--                  :key="project.id"-->
          <!--                  link :to="'/' + ['proj', 'plan', 'dev'][drawerSelect] + '/' + project.id"-->
          <!--                  @click="selectedProj=project.id"-->
          <!--          >{{ project.name }}</v-tab>-->
          <!--          <v-tab v-for="project in user.projects" :key="project.id" link :to="'/proj/' + project.id">{{ project.name }}</v-tab>-->
  
          <!--          <v-tab link to="/newproj"><v-icon class="px-1">mdi-plus-circle</v-icon> new project</v-tab>-->
          <!-- </v-tabs> -->
        </template>
      </v-app-bar>
      <v-navigation-drawer
        v-model="drawer"
        app
        clipped
        permanent
        v-if="((user && user.auth !== 1)) "
      >
        <!-- <div style="background-color: aqua;width: 100%;">
  
        </div> -->
        <v-list subheader v-if="user.auth !== 1">
          <v-list-item link to="/manager/home">
            <v-list-item-icon><v-icon>mdi-home-outline</v-icon></v-list-item-icon>
            <v-list-item-title>主页</v-list-item-title>
          </v-list-item>
          <v-list-item link to="/manager/userMessages">
            <v-list-item-icon
            ><v-icon>mdi-account-multiple</v-icon></v-list-item-icon
            >
            <v-list-item-title>用户信息</v-list-item-title>
          </v-list-item>
          <v-list-item link to="/manager/loginMessages">
            <v-list-item-icon><v-icon>mdi-history</v-icon></v-list-item-icon>
            <v-list-item-title>用户登录信息</v-list-item-title>
          </v-list-item>
          <v-list-item link to="/manager/projectMessages">
            <v-list-item-icon
            ><v-icon>mdi-book-edit-outline</v-icon></v-list-item-icon
            >
            <v-list-item-title>项目信息</v-list-item-title>
          </v-list-item>
          <v-list-item link to="/manager/userAuthority">
            <v-list-item-icon
            ><v-icon>mdi-gavel</v-icon></v-list-item-icon
            >
            <v-list-item-title>用户权限管理</v-list-item-title>
          </v-list-item>
          <v-list-item link to="/manager/assistantAuthority" v-if="user.auth === 3">
            <v-list-item-icon><v-icon>mdi-mouse</v-icon></v-list-item-icon>
            <v-list-item-title>助教权限管理</v-list-item-title>
          </v-list-item>
          <v-list-item link to="/manager/assistantMessages" v-else>
            <v-list-item-icon><v-icon>mdi-mouse</v-icon></v-list-item-icon>
            <v-list-item-title>查看助教</v-list-item-title>
          </v-list-item>
          <v-list-item link to="/manager/teacherMessages">
            <v-list-item-icon><v-icon>mdi-group</v-icon></v-list-item-icon>
            <v-list-item-title>查看教师</v-list-item-title>
          </v-list-item>
        </v-list>
  <!--        <v-list>-->
  <!--        <v-list-item-group v-if="user.status === 'C'">-->
  <!--          <v-list-item link to="/manager">-->
  <!--            <v-list-item-icon-->
  <!--              ><v-icon>mdi-home-outline</v-icon></v-list-item-icon-->
  <!--            >-->
  <!--            <v-list-item-title>主页</v-list-item-title>-->
  <!--          </v-list-item>-->
  <!--          <v-list-item link to="/manager/userMessages">-->
  <!--            <v-list-item-icon-->
  <!--              ><v-icon>mdi-account-multiple</v-icon></v-list-item-icon-->
  <!--            >-->
  <!--            <v-list-item-title>用户信息</v-list-item-title>-->
  <!--          </v-list-item>-->
  <!--          <v-list-item link to="/manager/loginMessages">-->
  <!--            <v-list-item-icon><v-icon>mdi-history</v-icon></v-list-item-icon>-->
  <!--            <v-list-item-title>用户登录信息</v-list-item-title>-->
  <!--          </v-list-item>-->
  <!--          <v-list-item link to="/manager/projectMessages">-->
  <!--            <v-list-item-icon-->
  <!--              ><v-icon>mdi-book-edit-outline</v-icon></v-list-item-icon-->
  <!--            >-->
  <!--            <v-list-item-title>项目信息</v-list-item-title>-->
  <!--          </v-list-item>-->
  <!--        </v-list-item-group>-->
  <!--      </v-list>-->
  
      </v-navigation-drawer>
      <el-dialog title="创建项目" :visible.sync="setupDialog" width="50%" :before-close="handleClose">
        <el-form :label-position="labelPosition" label-width="80px" :model="form" ref="form">
          <el-form-item label="项目名称">
            <el-input v-model="form.name"></el-input>
          </el-form-item>
          <el-form-item label="活动概述">
            <el-input type="textarea" v-model="form.intro" :autosize="{ minRows: 5, maxRows: 10 }"></el-input>
          </el-form-item>
        </el-form>
        <span slot="footer" class="dialog-footer">
          <el-button @click="cancelSetupProject">取 消</el-button>
          <el-button type="primary" @click="setupProject">确 定</el-button>
        </span>
      </el-dialog>
  
      <el-dialog title="我的提醒" :visible.sync="clockDialog" width="50%">
        <b style="color: rgb(128,128,128);">您可以点击跳转到对应页面</b>
        <v-simple-table>
          <thead>
            <tr>
              <th class="text-left" style="width: 60px">
                已读
              </th>
              <th class="text-left" style="width: 50px">
                Id
              </th>
              <th class="text-left">
                内容
              </th>
              <th class="text-left">
                链接
              </th>
              <th class="text-left">
                时间
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="notice in noticeList" :key="notice.noticeId"
              @mouseenter="arr[notice.taskId] = true" @mouseleave="arr[notice.taskId] = false">
              <td>
                <v-icon v-if="notice.read === 'N'" @click="handleReadNotice(notice.noticeId)">mdi-checkbox-marked</v-icon>
                <v-icon v-else color="green">mdi-checkbox-marked</v-icon>
              </td>
              <td>{{ notice.noticeId }}</td>
              <td>{{ notice.content }}</td>
              <td>  <v-btn icon color="blue" v-bind="attrs" v-on="on" @click="gotoProjectDetailPage(item)">
                  <v-icon @click="jumpTo(notice)">mdi-link-variant</v-icon>
                </v-btn>
              </td>
              <td>{{ new Date(notice.create_time).toLocaleString() }}</td>
              <td>
                <v-icon @click="handleDeleteNotice(notice.noticeId)">mdi-delete</v-icon>
              </td>
            </tr>
          </tbody>
        </v-simple-table>
      </el-dialog>
  
      <v-main>
        <router-view v-if="showRouterView" />
      </v-main>
  
  
      <el-dialog title="提醒列表" width="30%" :before-close="handleClose">
        <span>这是一段信息</span>
        <span slot="footer" class="dialog-footer">
          <el-button @click="dialogVisible = false">取 消</el-button>
          <el-button type="primary" @click="dialogVisible = false">确 定</el-button>
        </span>
      </el-dialog>
  
    </v-app>
  </template>
  
  <script>
  import Cookies from "js-cookie"
  import { computed } from "vue"
  import {
    newProject, showTaskList, watchAllProject, getEmail, showNoticeList, removeNotice,
    userReleaseDocLock, readNotice
  } from "@/api/user"
  import axios from "axios"
  import AllTask from "@/views/user/projectPlanning/allTask.vue"
  import AllFile from "@/views/user/document/allFile.vue"
  import getIdenticon from "@/utils/identicon";
  import topicSetting from "@/utils/topic-setting";
  // import allTask from "@/views/user/projectPlanning/allTask"
  console.log("entered login page");
  let user = Cookies.get("user");
  let proj;
  console.log(user);
  if (user === undefined) { // 用户未登录
    console.log("not logged in");
    if (window.location.pathname !== "/login") {
      window.location.href = '/login'
    }
  } else { // 用户已登录
     // 路由守卫
     // 合法的普通用户路径
    let userpath = (
      window.location.pathname !== "/workDetail" && 
      window.location.pathname !== "/allFile" &&
      window.location.pathname !== "/allPerson" && 
      window.location.pathname !== "/allTask" &&
      window.location.pathname !== "/picture" && 
      !window.location.pathname.startsWith("/plan") &&
      !window.location.pathname.startsWith("/allProject") && 
      window.location.pathname !== "/home" &&
      !window.location.pathname.startsWith("/dev") && 
      window.location.pathname !== "/profile" &&
      window.location.pathname !== "topic" &&
      !window.location.pathname.startsWith("/user") && 
      !window.location.pathname.startsWith("/commitReview") &&
      !window.location.pathname.startsWith("/prReview")) &&
      !window.location.pathname.startsWith("/room");
  
      // 合法的纯管理员路径（位于管理端）
    let managerpath = (
      window.location.pathname !== "/profile" &&
      window.location.pathname !== "topic" && 
      !window.location.pathname.startsWith("/manager")) 
    user = JSON.parse(user)
    proj = undefined;
    if (user !== undefined) {
      if (user.auth === 1) { // 普通用户
        proj = Cookies.get("proj");
        console.log(proj)
        if (proj !== undefined) {
          if (userpath) {
            window.location.href = "/allTask"
          }
          // if (window.location.pathname !== "/allTask") {
          //   window.location.href = "/allTask"
          // }
        } else {
          if (userpath) {
            window.location.href = "/allProject"
          }
          // if (window.location.pathname !== "/allProject") {
          //   window.location.href = "/allProject"
          // }
        }
      } else { // 管理员
        if (managerpath) {
          window.location.href = "/manager/home"
        }
        // if (window.location.pathname !== "/manager/home") {
        //   window.location.href = "/manager/home"
        // }
      }
    }
  }
  
  export default {
    name: "App",
    // created() {
    //     this.$watch(() => this.drawerIndex, (to, from) => {
    //         console.log('drawerIndex change!')
    //         this.showRouterView = false;
    //         this.$nextTick(() => (this.showRouterView = true));
    //     })
    // }
    created() {
      console.log("created");
      window.addEventListener('scroll', () => {
        this.scrollUp = this.isScrollTop()
      })
      this.updateUserProj();
      this.updateTopic();
      this.createCheckClock()
  
      let doc = Cookies.get("doc");
      console.log("cookies");
      console.log(doc);
      if (doc !== undefined && doc !== 'undefined') {
        doc = JSON.parse(doc);
        console.log(proj);
        userReleaseDocLock({ userId: user.id, projectId: JSON.parse(proj).projectId, docId: doc.id }).then(
          res => {
            console.log("userReleaseDocLock");
            console.log(res);
          }
        )
      }
      Notification.requestPermission()
  
      let proj = Cookies.get("proj");
      if (proj !== undefined && proj !== 'undefined') {
        proj = JSON.parse(proj)
        this.proj = proj;
      }
  
      this.getTaskList()
      this.createCheckClock()
  
      console.log('setting interval...')
      this.updateNoticeList()
      setInterval(() => {
        this.updateNoticeList();
      }, 5000)
    },
    components: {
      AllTask,
      AllFile,
    },
    watch: {
      selectedProj(n, o) {
        console.log("selectedProj change! from " + o + " to " + n);
        this.showRouterView = false;
        this.$nextTick(() => (this.showRouterView = true));
      },
    },
    data: () => {
      return {
        // from: -1, // -1普通用户，0从用户页面跳转，1从项目页面跳转，存入Cookie
        topic: "https://fastly.picsum.photos/id/53/1280/1280.jpg?hmac=QP5opo-oENp5iFwsSiWH8azQuR0w0bwps6MT6yvhKwA",
        labelPosition: "left",
        drawer: true,
        mini: true,
        showRouterView: true,
        user: user,
        proj: null,
        drawerIndex: null,
        routeSelect: null,
        selectedProj: null,
        setupDialog: false,
        selectedItem: null,
        dialog: false,
        clockDialog: false,
        editClockDialog: false,
        form: {
          name: "",
          intro: "",
          id: "",
        },
        projectData: [],
        tasks: [],
        scrollUp: true,
        clockList: [],
        noticeList: [],
        noReadNoticeList: [],
        showNoReadNotice: '',
        checkNoReadNotice: false,
        arr: [],
        whatisclicked: null,
        codeReviewExpanded: false
      };
    },
    beforeUpdate() {
      // this.drawer = user && proj && showLabel();
      this.showLabel();
      let proj = Cookies.get("proj");
      if (proj !== undefined) {
        proj = JSON.parse(proj)
        this.proj = proj;
      }
    },
    provide() {
      return {
        user: computed(() => this.user),
        proj: computed(() => this.proj),
        //from: computed(() => this.from),
        selectedProj: computed(() => this.proj),
        changeSelectedProj: this.changeSelectedProj,
        updateUserProj: this.updateUserProj,
        updateUser: this.updateUser,
        updateTopic: this.updateTopic,
        getProj: this.getProj,
        //setFrom: this.setFrom,
        // reload:this.reload
      };
    },
    methods: {
      getIdenticon,
      // setFrom(from) {
      //   console.log("setFrom")
      //   this.from = from
      //   console.log(this.from)
      // },
      updateTopic() {
        if (this.user.topic === 'A') { // 红色
          this.topic = "https://fastly.picsum.photos/id/859/1919/1919.jpg?hmac=24AoHo7Jc5TRRRaJfWO0B4z2wW5Jl14r56rVKeMfpZI"
        } else if (this.user.topic === 'B') { // 橙色
          this.topic = "https://fastly.picsum.photos/id/360/1925/1280.jpg?hmac=vX9T-qgnqfOUqLnxlsxCZfkKn_wi-9vtPKdbq7H6EgU"
        } else if (this.user.topic === 'C') { // 绿色
          this.topic = "https://fastly.picsum.photos/id/509/4608/3456.jpg?hmac=ZvNo59d3NP2XjQE75AaROWBTpW2BAzZgWb0-Jso0l9Y"
        } else if (this.user.topic === 'D') { // 蓝色
          this.topic = "https://fastly.picsum.photos/id/53/1280/1280.jpg?hmac=QP5opo-oENp5iFwsSiWH8azQuR0w0bwps6MT6yvhKwA"
        } else { // 紫色
          this.topic = "https://fastly.picsum.photos/id/723/5000/3333.jpg?hmac=Lq_OA9h0W8RDhE3xt44qzGv5PtQVLSnVCjoizkIiQNs"
        }
      },
      updateUser() {
        var userCookie = Cookies.get("user")
        if (userCookie !== undefined) {
          this.user = JSON.parse(userCookie)
        }
      },
      updateNoticeList() {
        console.log("updating NoticeList...")
        showNoticeList({ userId: this.user.id }).then(
          res => {
            this.noticeList = res['data']['data']
            this.noticeList.forEach(item => {
              // 如果两个时间小于5秒，就弹出提醒
              if (Math.abs(new Date(item.deadline) - new Date()) < 5000) {
                console.log(Math.abs(new Date(item.deadline) - new Date()))
                this.$message({
                  showClose: true,
                  message: "有到期的截止日期！",
                  type: "warning",
                  duration: 0,
                });
                if ("Notification" in window) {
                  Notification.requestPermission().then(function (permission) {
                    if (permission === "granted") {
                      let notification = new Notification("有到期的截止日期！", {
                        body: "请及时处理！"
                      });
                    }
                  });
                }
              }
            })
            console.log(this.noReadNoticeList);
          }
        )
      },
      checkClock() {
        this.clockDialog = true;
        showNoticeList({ userId: this.user.id }).then(
          res => {
            this.noticeList = res['data']['data'];
            console.log(this.noticeList);
          }
        )
      },
      createCheckClock() {
        showNoticeList({ userId: this.user.id }).then(
          res => {
            this.noticeList = res['data']['data'];
            console.log(this.noticeList);
            for (let i = 0; i < this.noticeList.length; i++) {
              if (this.noticeList.at(i).read === 'N') {
                for(let j = 0; j < this.noReadNoticeList.length; j++) {
                  if (this.noReadNoticeList.at(j).noticeId === this.noticeList.at(i).noticeId) {
                    return
                  }
                }
                this.noReadNoticeList.push(this.noticeList.at(i))
              }
            }
          }
        )
      },
      jumpTo(notice) {
        console.log(notice.url)
        if (notice.url !== '') {
          this.$router.push(notice.url)
        }
        this.clockDialog = false
      },
      closeDocument() {
        this.dialog = false;
      },
      openDocument() {
        this.dialog = true;
      },
      getEmail(id) {
        getEmail({ id: id }).then(
          res => {
            console.log("getEmail");
            console.log(res);
            console.log(id);
            return res['data']['data'];
          }
        )
      },
      get_project() {
        Cookies.remove("proj");
        console.log("get_project");
        watchAllProject({ userId: this.user.id }).then(
          res => {
            this.projectData = res['data']['data'];
            console.log(this.projectData);
          }
        )
      },
      getTaskList() {
        console.log(this.user.id);
        console.log(this.selectedProj);
        showTaskList({ userId: this.user.id, projectId: this.proj.projectId }).then(
          res => {
            console.log("getTaskList");
            console.log(res);
            this.tasks = res['data']['data'];
            console.log(this.tasks);
          }
        );
      },
      gotoPic() {
        showTaskList({ userId: this.user.id, projectId: this.proj.projectId }).then(
          res => {
            console.log("getTaskList");
            console.log(res);
            this.tasks = res['data']['data'];
            console.log(this.tasks);
            let projectItem = [];
            let projectItemStart = [];
            let projectItemEnd = [];
            let workloads = [];
            let expectedDates = [];
            let actualDates = [];
            let projectState = [];
            console.log(this.tasks);
            for (let i = 0; i < this.tasks.length; i++) {
              for (let j = 0; j < this.tasks[i].subTaskList.length; j++) {
                projectItem.push(this.tasks[i].subTaskList[j].subTaskName);
                projectItemStart.push(this.tasks[i].subTaskList[j].start_time.slice(0, 10));
                projectItemEnd.push(this.tasks[i].subTaskList[j].deadline.slice(0, 10));
                workloads.push(parseInt(this.tasks[i].subTaskList[j].contribute));
                expectedDates.push(this.tasks[i].subTaskList[j].deadline.slice(0, 10));
                actualDates.push(this.tasks[i].subTaskList[j].complete_time.slice(0, 10));
                projectState.push(this.tasks[i].subTaskList[j].status);
              }
            }
            console.log(this.tasks); console.log(projectItem); console.log(projectItemStart); console.log(projectItemEnd);
            if (projectItem.length == 0) {
              this.$message({
                type: 'info',
                message: '您还没有任务'
              })
              return;
            }
            this.$router.push({
              path: '/picture'
              , query: {
                projectItem: projectItem, projectItemStart: projectItemStart, projectItemEnd: projectItemEnd,
                workloads: workloads, expectedDates: expectedDates, actualDates: actualDates, projectState: projectState
              }
            });
          });
      },
      getProj(item) {
        console.log("getProj");
        console.log(item);
        console.log(JSON.stringify(item));
        Cookies.set('proj', JSON.stringify(item));
        window.location.href = '/allTask';
        this.proj = Cookies.get(proj);
      },
      existManager() {
        return Cookies.get("manager");
      },
      existUser() {
        console.log("111111")
        console.log(Cookies.get("user"))
        if (Cookies.get("user") === undefined) {
          return false;
        }
        let tmp = JSON.parse(Cookies.get("user"))
        return tmp.status === 'A'
      },
      //gotoHomePage() {
      //window.location.href = '/allProject'
      //},
      gotoManagerPage() {
        console.log("122343243242432525")
        console.log(Cookies.get("from"))
        Cookies.set("user", Cookies.get("manager"))
        Cookies.remove("manager");
        Cookies.remove("proj");
        console.log("user")
        console.log(Cookies.get("user"))
        console.log("manager")
        console.log(Cookies.get("manager"))
        let from = Cookies.get("from")
        if (from === "0") {
          Cookies.remove("from");
          window.location.href = '/manager/userMessages'
        }
        if (from === "1") {
          Cookies.remove("from");
          window.location.href = '/manager/projectMessages'
        }
      },
      showLabel() {
        if (this.user === null || this.user === undefined || this.user.auth !== 1) {
          return false;
        }
        console.log("showLabel");
        console.log(this.proj);
        console.log(this.user);
        console.log(this.$route.path);
  
        console.log(this.user !== null && this.proj !== undefined &&
          !window.location.pathname.startsWith("/manager") &&
          this.$route.path !== "/allProject/" &&
          !window.location.pathname.startsWith("/login") &&
          !window.location.pathname.startsWith("/register"));
  
        return (
          this.user !== null && this.user !== undefined &&
          this.proj !== null && this.proj !== undefined &&
          !window.location.pathname.startsWith("/manager") &&
          this.$route.path !== "/allProject/" &&
          !window.location.pathname.startsWith("/login") &&
          !window.location.pathname.startsWith("/register") &&
          !window.location.pathname.startsWith("/profile") &&
          !window.location.pathname.startsWith("/topic")
        );
      },
      // getSelectedProj() {
      //     let pid = this.$route.params.projid;
      //     if (pid === undefined) return null;
      //     else return pid;
      // },
      // getDrawerSelection() {
      //   let drawerSelection = this.$route.
      // },
      logoff() {
        Cookies.remove("user");
        Cookies.remove("manager");
        Cookies.remove("proj");
        Cookies.remove("from")
        window.location.href = "/login";
      },
      handleClose(done) {
        this.$confirm("确认关闭？")
          .then(() => {
            done();
          })
          .catch(() => { });
        this.whatisclicked = null
      },
      cancelSetupProject() {
        this.setupDialog = false;
        this.form = {
          name: '',
          intro: ''
        }
        this.whatisclicked = null
      },
      setupProject() {
        // console.log(this.search);
        // console.log("submit");
        this.whatisclicked = null
        watchAllProject({ userId: this.user.id }).then(
          res => {
            this.projectData = res['data']['data'];
            console.log(this.projectData);
          }
        )
        if (this.form.name.trim() === "") {
          this.$message({
            type: 'error',
            message: '项目名不能为空！'
          });
          return;
        }
        for (let i = 0; i < this.projectData.length; i++) {
          if (this.form.name === this.projectData[i].projectName) {
            this.$message({
              type: 'error',
              message: '已存在同名项目'
            });
            return;
          }
        }
        this.setupDialog = false;
        newProject({ projectName: this.form.name, projectIntro: this.form.intro, userId: this.user.id }).then(
          res => {
            console.log(this.user.id);
            console.log(res);
            this.updateUserProj();
            this.get_project();
          }
        );
        this.form = {
          name: '',
          intro: ''
        }
      },
      handleReadNotice(noticeId) {
        this.$confirm("确认已读？")
          .then(() => {
            readNotice({ noticeId: noticeId, userId: this.user.id }).then(
              res => {
                showNoticeList({ userId: this.user.id }).then(
                  res => {
                    this.noticeList = res.data.data
                    this.noReadNoticeList.splice(0, 1)
                  }
                )
              }
            )
          })
      },
      handleDeleteNotice(noticeId) {
        this.$confirm("确认删除提醒？")
          .then(() => {
            removeNotice({ noticeId: noticeId }).then(
              res => {
                showNoticeList({ userId: this.user.id }).then(
                  res => {
                    this.noticeList = res['data']['data'];
                    for (let i = 0; i < this.noReadNoticeList.length; i++) {
                      if (this.noReadNoticeList.at(i).noticeId === noticeId) {
                        this.noReadNoticeList.splice(0, 1)
                        break
                      }
                    }
                    console.log(this.noticeList);
                  }
                )
              }
            )
          })
          .catch(() => { });
      },
      changeSelectedProj(proj) {
        this.selectedProj = proj;
      },
      updateUserProj() {
        if (this.user !== undefined) {
          axios
            .post("/api/plan/watchAllProject", {
              userId: this.user.id,
            })
            .then((res) => {
              console.log("updateProj");
              console.log(res);
              if (res.data.errcode === 0) {
                this.user.projects = res['data']['data'];
                Cookies.set("user", JSON.stringify(this.user));
              } else {
                alert(
                  "watchAllProject failure! with non 0 errcode " + res.data.errcode
                );
              }
            })
            .catch((err) => {
              alert("watchAllProject failure! with error " + err);
            });
        }
      },
      isScrollTop() {
        if (document.body.scrollHeight > (window.innerHeight || document.documentElement.clientHeight)) {
          let scrollTop = window.scrollY || document.documentElement.scrollTop || document.body.scrollTop || 0;
          return scrollTop === 0
        }
      },
      getTaskName(taskId) {
        // this.getTaskList();
        console.log("getTaskName is called");
        console.log(this.tasks);
        for (let i = 0; i < this.tasks.length; i++) {
          for (let j = 0; j < this.tasks[i].subTaskList.length; j++) {
            if (this.tasks[i].subTaskList[j].subTaskId === taskId) {
              return this.tasks[i].subTaskList[j].subTaskName;
            }
          }
        }
      },
      getTopicColor: topicSetting.getColor,
      getDarkColor: topicSetting.getDarkColor,
      getLinearGradient: topicSetting.getLinearGradient,
      getLinearGradientLiteral: topicSetting.getLinearGradientLiteral,
    },
  };
  </script>
  
  <style scoped>
  #username {
    font-size: 1.2em;
    line-height: 1.2em;
  }
  
  .parent-item {
    /* 添加一些样式，比如背景色或边框 */
  
  }
  
  /* 子级列表项的样式 */
  .child-items {
    /* 可以根据需要指定子项的样式，比如缩进、边距等 */
  
  }
  
  /* 指定子级列表项中的标题样式 */
  .child-items v-list-item-title {
    /* 添加子项标题的样式 */
    font-weight: bold;
  }
  </style>