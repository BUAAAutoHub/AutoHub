<template>
  <div style="position: relative; width: 100%; height: 100%">
    <div id="burnup-chart" style="position: absolute; width: 80%; height: 40%; left: 10%; top: 6%">
      燃尽图
    </div>
    <div ref="chart" style="position: absolute; width: 80%; height: 40%; left: 10%; top: 52%">
      进度显示图
    </div>
      <div ref="collChart" style="position: absolute; width: 80%; height: 40%; left: 10%; top: 98%">
      协作关系图
      </div>

    <v-btn class="ma-2" :color="getTopicColor(user.topic)" @click="back">
      <v-icon dark left> mdi-arrow-left </v-icon>
      返回
    </v-btn>
  </div>
</template>

<script>
import * as echarts from "echarts";
import topicSetting from "@/utils/topic-setting";

export default {
  data() {
    return {
      chartData: {
        workloads: [], // 工作量
        expectedDates: [], // 预期完成日期
        actualDates: [], // 实际完成日期
        dates: [], // 日期
        resWorkloads: [],
      },
    };
  },
  mounted() {
    //   this.drawB();
    this.drawP();
    this.drawB();
    this.drawCollaboration();
  },
  inject: {
    user: { default: null }
  },
  methods: {
    transform(state) {
      if (state === 'A') {
        return '已完成';
      } else if (state === 'B') {
        return '进行中';
      } else if (state === 'C') {
        return '未开始';
      } else if (state === 'D') {
        return '不合法';
      }
    },
    getColor(state) {
      if (state === "A") {
        return "green";
      } else if (state === "B") {
        return "orange";
      } else if (state === "C") {
        return "blue";
      } else if (state === "D") {
        return "red";
      }
    },
    drawP() {
      console.log(echarts) // Don't delete this. This is to avoid build errors
      var chart1 = echarts.init(this.$refs.chart);
      window.addEventListener("resize", function () {
        chart1.resize();
      });

      let projectItem = this.$route.query.projectItem; //每个任务的名称
      let projectItemStart = this.$route.query.projectItemStart;//每个任务的启动时间
      let projectItemEnd = this.$route.query.projectItemEnd; //每个任务的结束时间
      let projectState = this.$route.query.projectState;

      //   let projectItem = ["1", "2"]; //每个任务的名称
      //   let projectItemStart = ["2022-5-24", "2022-5-27"]; //每个任务的启动时间
      //   let projectItemEnd = ["2022-5-27", "2022-5-29"]; //每个任务的结束时间
      //   let projectState = ["A", "B"];

      let projectItemStartValue = projectItemStart.map((item) => {
        return new Date(item).valueOf();
      });
      console.log(projectItemStartValue);
      let projectItemDuringValue = projectItemEnd.map((item, i) => {
        return new Date(item).valueOf() - projectItemStartValue[i];
      });
      console.log(projectItemDuringValue);
      let dateMin = projectItemStartValue[0];
      for (let i = 0; i < projectItemStartValue.length; i++) {
        if (projectItemStartValue[i] < dateMin) {
          dateMin = projectItemStartValue[i];
        }
      }
      console.log(dateMin);
      var option = {
        title: {
          text: "任务进度显示图",
        },
        tooltip: {
          trigger: "axis",
          formatter: function (params) {
            var tar = params[1];
            let state = projectState[tar.dataIndex];
            let startTime = projectItemStartValue[tar.dataIndex];
            let endTime = projectItemStartValue[tar.dataIndex] + projectItemDuringValue[tar.dataIndex];
            var s;
            if (state === 'A') {
              s = '已完成';
            } else if (state === 'B') {
              s = '进行中';
            } else if (state === 'C') {
              s = '未开始';
            } else if (state === 'D') {
              s = '延期已完成';
            } else if (state === 'E') {
              s = '延期未完成';
            }
            return (
              tar.name +
              "<br/>" +
              tar.seriesName +
              " : " + new Date(startTime).getFullYear() + "-" + (new Date(startTime).getMonth() + 1) + "-" + new Date(startTime).getDate()
              + "-->" + new Date(endTime).getFullYear() + "-" + (new Date(startTime).getMonth() + 1) + "-" + new Date(endTime).getDate() +
              "<br/>" + "状态：" + s
            );
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
          data: projectItem,
        },
        xAxis: {
          type: "value",
          min: dateMin,
          axisLabel: {
            color: "#333", // 坐标轴文字颜色
            formatter: function (param) {
              let date = new Date(param);
              let dateLabel =
                date.getFullYear() +
                "-" +
                (date.getMonth() + 1) +
                "-" +
                date.getDate();
              return dateLabel;
            },
          },
        },
        series: [
          {
            name: "Placeholder",
            type: "bar",
            stack: "Total",
            itemStyle: {
              borderColor: "transparent",
              color: "transparent",
            },
            emphasis: {
              itemStyle: {
                borderColor: "transparent",
                color: "transparent",
              },
            },
            data: projectItemStartValue,
          },
          {
            name: "周期",
            type: "bar",
            stack: "Total",
            itemStyle: {
              normal: {
                color: function (params) {
                  let state = projectState[params.dataIndex];
                  if (state === 'A') {
                    return 'green';
                  } else if (state === 'B') {
                    return 'orange';
                  } else if (state === 'C') {
                    return 'blue';
                  } else if (state === 'D') {
                    return 'red';
                  } else if (state === 'E') {
                    return 'yellow';
                  }
                },
              }
            },
            data: projectItemDuringValue,
          },
        ],
      };
      // 使用刚指定的配置项和数据显示图表。
      chart1.setOption(option);
    },
    drawB() {
      // 模拟数据
      this.chartData.workloads = this.$route.query.workloads;
      this.chartData.expectedDates = this.$route.query.expectedDates;

      for (let i = 0; i < this.chartData.workloads.length; i++) {
        this.chartData.workloads[i] = parseInt(this.chartData.workloads[i]);
      }

      for (let i = 0; i < this.$route.query.actualDates.length; i++) {
        if (this.$route.query.actualDates[i] !== "2050-12-31") {
          this.chartData.actualDates.push(this.$route.query.actualDates[i]);
        }
      }

      let sum = 0;
      for (let i = 0; i < this.chartData.workloads.length; i++) {
        sum += this.chartData.workloads[i];
      }
      console.log(sum);

      let expectedDatesValue = this.chartData.expectedDates.map((item) => {
        return new Date(item).valueOf();
      });

      let notSortDatesValue = [];
      for (let i = 0; i < expectedDatesValue.length; i++) {
        notSortDatesValue.push(expectedDatesValue[i]);
      }

      expectedDatesValue.sort()[0];

      var newArr = new Set(expectedDatesValue);
      var timeArr = Array.from(newArr);

      let resWorkloadsE = [];
      let res = sum;
      for (let i = 0; i < timeArr.length; i++) {
        for (let j = 0; j < notSortDatesValue.length; j++) {
          if (notSortDatesValue[j] == timeArr[i]) {
            res -= this.chartData.workloads[j];
          }
        }
        resWorkloadsE.push([timeArr[i], res]);
      }

      console.log(resWorkloadsE);

      for (let i = 0; i < this.chartData.actualDates.length; i++) {
        if (this.chartData.actualDates[i] == "") {
          this.chartData.actualDates.splice(i, 1);
        }
      }

      let actualDatesValue = this.chartData.actualDates.map((item) => {
        return new Date(item).valueOf();
      });

      let notSortADatesValue = [];
      for (let i = 0; i < actualDatesValue.length; i++) {
        notSortADatesValue.push(actualDatesValue[i]);
      }

      actualDatesValue.sort()[0];

      var newArr1 = new Set(actualDatesValue);
      var timeArr1 = Array.from(newArr1);

      let resWorkloadsA = [];
      // console.log(notSortDatesValue);
      // console.log(timeArr);
      res = sum;
      for (let i = 0; i < timeArr1.length; i++) {
        for (let j = 0; j < notSortADatesValue.length; j++) {
          if (notSortADatesValue[j] == timeArr1[i]) {
            res -= this.chartData.workloads[j];
          }
        }
        // resWorkloadsA[timeArr1[i]] = res;
        resWorkloadsA.push([timeArr1[i], res]);
      }
      console.log(resWorkloadsA);

      let dateMin;
      if (actualDatesValue.length == 0) {
        dateMin = expectedDatesValue[0];
      } else {
        dateMin =
          expectedDatesValue[0] < actualDatesValue[0]
            ? expectedDatesValue[0]
            : actualDatesValue[0];
      }
      dateMin = dateMin - 24 * 60 * 60 * 1000;
      resWorkloadsA.push([dateMin, sum]);
      resWorkloadsE.push([dateMin, sum]);

      function sortByField(x, y) {
        return x[0] - y[0];
      }
      resWorkloadsA.sort(sortByField);
      resWorkloadsE.sort(sortByField);

      // 绘制燃尽图
      console.log(echarts) // Don't delete this. This is to avoid build errors
      const chart2 = echarts.init(document.getElementById("burnup-chart"));
      window.addEventListener("resize", function () {
        chart2.resize();
      });

      chart2.setOption({
        title: {
          text: "燃尽图",
        },
        legend: {
          data: ["预期中的剩余工作量", "实际的剩余工作量"],
          y: "bottom",
          x: "center",
        },
        tooltip: {
          trigger: "axis",
          formatter: function (params) {
            return params[0]["seriesName"] + ":" + params[0]["value"][1];
          },
        },
        xAxis: {
          type: "value",
          min: dateMin,
          axisLabel: {
            color: "#333", // 坐标轴文字颜色
            formatter: function (param) {
              let date = new Date(param);
              let dateLabel =
                date.getFullYear() +
                "-" +
                (date.getMonth() + 1) +
                "-" +
                date.getDate();
              return dateLabel;
            },
          },
        },
        yAxis: {
          type: "value",
        },
        series: [
          {
            name: "预期中的剩余工作量",
            type: "line",
            data: resWorkloadsE,
          },
          {
            name: "实际的剩余工作量",
            type: "line",
            data: resWorkloadsA,
          },
        ],
      });
    },
    drawCollaboration() {
      const nodes = [
        { id: 1, name: 'Node 1', category: 0 }, // 节点1
        { id: 2, name: 'Node 2', category: 1 }, // 节点2
        { id: 3, name: 'Node 3', category: 0 }, // 节点3
        // 添加更多节点...
      ];

      // 假设的边数组数据
      const links = [
        { source: 1, target: 2, value: 5 }, // 连接节点1和节点2，权值为5
        { source: 2, target: 3, value: 8 }, // 连接节点2和节点3，权值为8
        // 添加更多边...
      ];

      // 将数据放入 data 对象
      const data = {
        nodes: nodes,
        links: links
      };

      // 创建 ECharts 实例
      const myChart = echarts.init(this.$refs.collChart);

      // 配置图形
      const option = {
        series: [{
          type: 'graph',
          layout: 'none',
          data: data.nodes,
          links: data.links,
          lineStyle: {
            normal: {
              width: function (value) {
                // 根据权值动态调整线条粗细
                return value * 0.1; // 这里可以根据具体情况调整
              }
            }
          },
          emphasis: {
            focus: 'adjacency'
          }
        }]
      };

      // 使用配置项显示图形
      myChart.setOption(option);
    },
    back() {
      this.$router.go(-1);
    },
    getTopicColor: topicSetting.getColor
  },
};
</script>
