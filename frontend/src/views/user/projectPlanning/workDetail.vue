<template>
    <div style="position: relative;width: 100%;height: 100%;">
        <div
      ref="chart"
      style="position: absolute; width: 80%; height: 40%; left: 10%; top: 10%"
    >
      进度显示图
    </div>
    <v-btn class="ma-2" color="primary" dark @click="back">
      <v-icon dark left> mdi-arrow-left </v-icon>
      返回
    </v-btn>
    </div>
</template>
  
<script>
import * as echarts from 'echarts'

export default {
    name: 'TaskProgressChart',
    mounted() {
        this.drawP();
    },
    methods: {
        back() {
            this.$router.go(-1);
        },
        drawP() {
            var chart1 = echarts.init(this.$refs.chart);
            window.addEventListener("resize", function () {
                chart1.resize();
            });

            let personName = this.$route.query.nameList;
            let personWorkloads = this.$route.query.valueList;
    //   let projectItem = this.$route.query.projectItem; //每个任务的名称
    //   let projectItemStart = this.$route.query.projectItemStart;//每个任务的启动时间
    //   let projectItemEnd = this.$route.query.projectItemEnd; //每个任务的结束时间
    //   let projectState = this.$route.query.projectState;
      var option = {
        title: {
          text: "团队工作量统计图",
        },
        tooltip: {
          trigger: "axis",
          formatter: function (params) {
            console.log(params);
            return params[0]['axisValue'] + "的工作量为：" + params[0]['value'];
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
          data: personName,
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
            name: "工作量",
            type: "bar",
            stack: "Total",
            // itemStyle: {
            //   normal: {
            //     color: function (params) {
            //       let state = projectState[params.dataIndex];
            //       if (state === "A") {
            //             return "green";
            //         } else if (state === "B") {
            //             return "orange";
            //         } else if (state === "C") {
            //             return "blue";
            //         } else if (state === "D") {
            //             return "red";
            //         }
            //   },
            // }
        // },
            data: personWorkloads,
          },
        ],
      };
      // 使用刚指定的配置项和数据显示图表。
      chart1.setOption(option);
    },
    }
  }
  </script>
  