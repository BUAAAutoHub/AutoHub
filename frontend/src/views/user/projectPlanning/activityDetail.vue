<template>
  <div style="position: relative;width: 100%;height: 100%;">
    <div
        ref="taskChart"
        style="position: absolute; width: 80%; height: 40%; left: 10%; top: 10%"
    >
      任务活跃度显示图
    </div>
    <div
        ref="codeChart"
        style="position: absolute; width: 80%; height: 40%; left: 10%; top: 50%"
    >
      代码活跃度显示图
    </div>
    <v-btn class="ma-2" color="primary" dark @click="back">
      <v-icon dark left> mdi-arrow-left</v-icon>
      返回
    </v-btn>
  </div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'MemberActivityChart',
  mounted() {
    this.drawTaskP()
    this.drawCodeP()
  },
  methods: {
    back() {
      this.$router.go(-1);
    },
    drawTaskP() {
      var taskChart = echarts.init(this.$refs.taskChart);
      window.addEventListener("resize", function () {
        taskChart.resize();
      });

      let userName = this.$route.query.userList
      let userTaskAct = this.$route.query.taskActList

      var option = {
        title: {
          text: "任务活跃度统计图",
        },
        tooltip: {
          trigger: "axis",
          formatter: function (params) {
            console.log(params);
            return params[0]['axisValue'] + "的任务活跃度为：" + params[0]['value'];
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
            name: "任务活跃度",
            type: "bar",
            stack: "Total",
            data: userTaskAct,
          },
        ],
      };
      taskChart.setOption(option);
    },
    drawCodeP() {
      var codeChart = echarts.init(this.$refs.codeChart);
      window.addEventListener("resize", function () {
        codeChart.resize();
      });

      let userName = this.$route.query.userList
      let userCodeAct = this.$route.query.codeActList

      var option = {
        title: {
          text: "代码活跃度统计图",
        },
        tooltip: {
          trigger: "axis",
          formatter: function (params) {
            console.log(params);
            return params[0]['axisValue'] + "的代码活跃度为：" + params[0]['value'];
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
            name: "代码活跃度",
            type: "bar",
            stack: "Total",
            data: userCodeAct,
          },
        ],
      };
      codeChart.setOption(option);
    },
  }
}
</script>
