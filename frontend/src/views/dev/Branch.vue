<template>
<!--    <p>this is branch specific view</p>-->
<!--    <p>projId: {{projId}} so proj is {{this.proj}}</p>-->
<!--    <p>repoId: {{repoId}} so repo is {{this.repo}}</p>-->
<!--    <p>branchName: {{branchName}}</p>-->
<!--    <p>commitHistory: {{commitHistory}}</p>-->

    <v-container>
        <h1 :style="'color: ' + getDarkColor(user.topic)">分支详情 - {{branchName}}</h1>
        <v-row>
          <v-col cols="12">
            <v-tabs :color="getDarkColor(user.topic)" :slider-color="getDarkColor(user.topic)" v-model="tabs">
              <v-tab>提交记录&统计</v-tab>
              <v-tab :disabled="!graphReady">查看仓库文件</v-tab>
            </v-tabs>
          </v-col>
        </v-row>

        <v-tabs-items v-model="tabs">
          <v-tab-item :value="0">
            <v-row>
              <v-col cols="3" class="px-3">
                <h2>提交记录</h2>
                <v-list class="overflow-y-auto" max-height="calc(100vh - 250px)">
                  <v-list-item v-for="commit in commitHistory" :key="commit.id">
                    <v-list-item-content>
                      <v-tooltip bottom>
                        <template v-slot:activator="{ on, attrs}">
                          <v-list-item-title v-bind="attrs" v-on="on">{{commit.commitMessage}}</v-list-item-title>
                        </template>
                        <span>{{commit.commitMessage}}</span>
                      </v-tooltip>
                      <v-list-item-subtitle>{{new Date(commit.commitTime).toLocaleString()}} - {{commit.commithash.slice(0, 6)}} - {{commit.author}}</v-list-item-subtitle>
                    </v-list-item-content>
                  </v-list-item>
                </v-list>
              </v-col>
              <v-divider vertical></v-divider>
              <v-col cols="9" class="">
                <v-container fluid>
                  <v-row dense>
                    <v-col v-for="(entry, index) in [daily, monthly, yearly]" :key="index" :cols="entry.col">
                      <v-card :color="entry.color" class="text-center align-center">
                        <v-sparkline
                            :labels="index === 0 ? [] : entry.label"
                            :value="entry.data"
                            auto-line-width
                            smooth
                            padding="20"
                            stroke-linecap="round"
                            :show-labels="false"
                            auto-draw
                        ></v-sparkline>
                        <v-card-title>从 {{entry.label[0]}} 到 {{entry.label[entry.label.length-1]}} 的提交</v-card-title>
                        <v-card-actions>
                          <v-spacer></v-spacer>
                          <v-btn :color="getDarkColor(user.topic)" plain v-if="entry.col === 4" @click="entry.col = 12">展开</v-btn>
                          <v-btn :color="getDarkColor(user.topic)" plain v-else @click="entry.col = 4">收起</v-btn>
                        </v-card-actions>
                      </v-card>
                    </v-col>
                  </v-row>
                  <br>
                  <v-divider></v-divider>
                  <br>
                  <v-row dense>
                    <v-col cols="12">
                      <v-card :style="getLinearGradient(user.topic)">
                        <v-container fluid>
                          <v-row>
                            <v-col cols="8">
                              <div ref="user_specific_pie_chart" style="height: 20em" class="indigo lighten-4"></div>
                            </v-col>
                            <v-col cols="4">
                              <v-list dense max-height="20em" class="overflow-y-auto">
                                <v-list-item v-for="user in perUser" :key="user.key">
                                  <v-list-item-content>
                                    <v-list-item-title>{{user.key}}</v-list-item-title>
                                    <v-list-item-subtitle>{{user.value}} 次提交</v-list-item-subtitle>
                                  </v-list-item-content>
                                </v-list-item>
                              </v-list>
                            </v-col>
                          </v-row>
                        </v-container>
                        <v-card-title>用户提交数量</v-card-title>
                      </v-card>
                    </v-col>
                  </v-row>
                </v-container>
              </v-col>
            </v-row>
          </v-tab-item>
          <v-tab-item :value="1">

<!--            <v-container fluid>-->
<!--              <v-row>-->
<!--                <v-col cols="12">-->
<!--                  <v-card min-height="1000px">-->
<!--                    <v-card-title>文件列表</v-card-title>-->
<!--                    <v-card-text>-->
                      <FileView/>
<!--                    </v-card-text>-->
<!--                  </v-card>-->
<!--                </v-col>-->
<!--              </v-row>-->
<!--            </v-container>-->

          </v-tab-item>
        </v-tabs-items>




    </v-container>
</template>

<script>
import axios from "axios";
import * as echarts from 'echarts';

import FileView from './File.vue'
import test from './test.vue'
import {computed} from "vue";
import topicSetting from "@/utils/topic-setting";

export default {
    name: "Branch",
    components: {
        FileView,
        test
    },
    data() {
        return {
            tabs: null,
            projId: this.$route.params.projid,
            repoId: this.$route.params.repoid,
            branchName: this.$route.params.branchname,
            proj: null,
            repos: null,
            repo: null,
            branches: null,
            commitHistory: null,
            daily: {
                col: 4,
                color: '#FFCDD2',
                title: '过去三十日内的提交',
                label: [],
                data: []
            },
            monthly: {
                col: 4,
                color: '#B2EBF2',
                title: '过去一年内的提交',
                label: [],
                data: []
            },
            yearly: {
                col: 4,
                color: '#C8E6C9',
                title: '过去十年内的提交',
                label: [],
                data: []
            },
            perUser: [],
            graphReady: false
        }
    },
    provide() {
        return {
            repo: computed(() => this.repo),
            branchName: computed(() => this.branchName)
        }
    },
    created() {
        console.log(this.branchName)
        this.proj = this.user.projects.reduce((acc, cur) => cur.projectId == this.projId ? cur : acc, null)
        if (this.proj === null) {
            alert('proj not found')
            // window.location.pathname = '/dev'
        }

        axios.post('/api/develop/getBindRepos', {userId: this.user.id, projectId: this.projId})
            .then((res) => {
                if (res.data.errcode === 0) {
                    this.repos = res.data.data.map((cur, index, arr) => {
                        let remotePath = cur.repoRemotePath.split('/')
                        return {
                            id: cur.repoId,
                            user: remotePath[0],
                            repo: remotePath[1],
                            intro: cur.repoIntroduction
                        }
                    })
                    this.repo = this.repos.reduce((acc, cur) => cur.id == this.repoId ? cur : acc, null)
                    if (this.repo === null) {
                        alert('repo not found')
                        // window.location.pathname = '/dev'
                    }
                } else {
                    alert('/api/reviews/getBindRepos error with not 0 err code (' + res.data.errcode + ') ' + res.data.message)
                }
            }).catch((err) => {
                alert('/api/reviews/getBindRepos error' + err)
            })

        axios.post('/api/develop/getRepoBranches', {userId: this.user.id, repoId: this.repoId, projectId: this.projId})
            .then((res) => {
                if (res.data.errcode === 0) {
                    this.branches = res.data.data.map((cur, index, arr) => { return cur.branchName })
                    let branch = this.branches.reduce((acc, cur) => cur == this.branchName ? cur : acc, null)
                    if (branch === null) {
                        alert('branch ' + this.branchName + ' not found in branches ' + this.branches)
                        // window.location.pathname = '/dev'
                    }
                } else {
                    alert('/api/reviews/getBranches error with not 0 err code (' + res.data.errcode + ') ' + res.data.message)
                }
            }).catch((err) => {
                alert('/api/reviews/getBranches error' + err)
            })

        axios.post('/api/develop/getCommitHistory', {
            userId: this.user.id, projectId: this.projId, repoId: this.repoId, branchName: this.branchName})
            .then((res) => {
            if (res.data.errcode === 0) {
                this.commitHistory = res.data.data.map((cur, index, arr) => {
                    return {
                        id: index,
                        author: cur.author,
                        authorEmail: cur.authorEmail,
                        commithash: cur.commithash,
                        commitMessage: cur.commitMessage,
                        commitTime: cur.commitTime
                    }
                })
                this.prep_data_in_time_scope()
                this.prep_data_in_user_scope()
                this.draw_pie_chart()
                this.graphReady = true
            } else {
                alert('/api/reviews/getCommitHistory error with not 0 err code (' + res.data.errcode + ') ' + res.data.message)
            }
        }).catch((err) => {
            alert('/api/reviews/getCommitHistory error' + err)
        })
    },
    inject: {
        user: {default: null}
    },
    methods: {
        prep_data_in_time_scope() {
            // 获取commitHistory最后一个元素的日期
            let last_commit = this.commitHistory[this.commitHistory.length - 1]
            let last_commit_time = new Date(last_commit.commitTime)
            last_commit_time.setDate(last_commit_time.getDate() - 1)
            // 从 last_commit_time 开始，每天加一天，直到今天，每天的日期作为key，value为0
            let daily = {}
            let today = new Date()
            while (today >= last_commit_time) {
                let key = last_commit_time.toLocaleDateString()
                daily[key] = 0
                last_commit_time.setDate(last_commit_time.getDate() + 1)
            }
            // 遍历commitHistory，每个元素的日期作为key，value加一
            this.commitHistory.forEach((cur, index, arr) => {
                let key = new Date(cur.commitTime).toLocaleDateString()
                if (daily[key] === undefined) {
                    daily[key] = 1
                } else {
                    daily[key] += 1
                }
            })
            // 将daily的key和value分别放入label和data
            this.daily.label = Object.keys(daily)
            // 除了第一个和最后一个，将this.daily.label其他元素换为''
            for (let i = 1; i < this.daily.label.length - 1; i++) {
                this.daily.label[i] = ''
            }
            this.daily.data = Object.values(daily)

            // 从 last_commit_time 开始，每月加一月，直到今天，每月的日期作为key，value为0
            let monthly = {}
            last_commit_time = new Date(last_commit.commitTime)
            last_commit_time.setMonth(last_commit_time.getMonth() - 1)
            while (today >= last_commit_time) {
                let key = last_commit_time.getFullYear() + '-' + (last_commit_time.getMonth() + 1)
                monthly[key] = 0
                last_commit_time.setMonth(last_commit_time.getMonth() + 1)
            }
            // 遍历commitHistory，每个元素的日期作为key，value加一
            this.commitHistory.forEach((cur, index, arr) => {
                let key = new Date(cur.commitTime).getFullYear() + '-' + (new Date(cur.commitTime).getMonth() + 1)
                if (monthly[key] === undefined) {
                    monthly[key] = 1
                } else {
                    monthly[key] += 1
                }
            })
            // 将monthly的key和value分别放入label和data
            this.monthly.label = Object.keys(monthly)
            this.monthly.data = Object.values(monthly)

            // 从 last_commit_time 开始，每年加一年，直到今天，每年的日期作为key，value为0
            let yearly = {}
            last_commit_time = new Date(last_commit.commitTime)
            last_commit_time.setFullYear(last_commit_time.getFullYear() - 1)
            while (today >= last_commit_time) {
                let key = last_commit_time.getFullYear()
                yearly[key] = 0
                last_commit_time.setFullYear(last_commit_time.getFullYear() + 1)
            }
            // 遍历commitHistory，每个元素的日期作为key，value加一
            this.commitHistory.forEach((cur, index, arr) => {
                let key = new Date(cur.commitTime).getFullYear()
                if (yearly[key] === undefined) {
                    yearly[key] = 1
                } else {
                    yearly[key] += 1
                }
            })
            // 将yearly的key和value分别放入label和data
            this.yearly.label = Object.keys(yearly)
            this.yearly.data = Object.values(yearly)
        },
        prep_data_in_user_scope() {
            // 遍历commitHistory，统计每个author的commit次数
            let user = {}
            this.commitHistory.forEach((cur, index, arr) => {
                if (user[cur.author] === undefined) {
                    user[cur.author] = 1
                } else {
                    user[cur.author] += 1
                }
            })
            // 将 user 转换为 {key, value}的数组
            for (let key in user) {
                this.perUser.push({key: key, value: user[key]})
            }
            this.perUser.sort((a, b) => {
                return b.value - a.value
            })
        },
        draw_pie_chart() {
            console.log('echarts=')
            console.log(echarts)
            let pieChart = echarts.init(this.$refs.user_specific_pie_chart)
            window.addEventListener('resize', () => {pieChart.resize()})
            pieChart.setOption({
                title: {
                    text: '', left: 'center'
                },
                legend: {
                    orient: 'vertical',
                    left: 10,
                    data: this.perUser.label
                },
                tooltip: {
                    trigger: 'item',
                    formatter: function(args) {
                        return args.data.key + ' : ' + args.data.value + '次'
                    }
                },
                series: [
                    {
                        name: '提交次数',
                        type: 'pie',
                        radius: ['50%', '70%'],
                        avoidLabelOverlap: false,
                        labelLine: {
                            show: false
                        },
                        data: this.perUser
                    }
                ]
            })

        },
        getLinearGradient: topicSetting.getLinearGradient,
        getTopicColor: topicSetting.getColor,
        getDarkColor: topicSetting.getDarkColor,
    }
}
</script>

<style scoped>

</style>