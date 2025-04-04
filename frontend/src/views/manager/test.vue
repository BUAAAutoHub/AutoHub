<template>
  <v-container>
    <v-row>
      <v-col cols="6">
        <v-card class="fill-height">
          <v-card-title class="white">不同规模项目个数-饼状图</v-card-title>
          <v-card-text class="d-flex flex-column" style="width: 100%; height: 100%">
            <div ref="myChart" style="height: 300px"></div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="6">
        <v-card class="fill-height">
          <v-card-title class="white">不同规模项目个数-表格</v-card-title>
          <v-card-text>
            <v-data-table :headers="headers" :items="chartData" hide-default-footer>
              <template v-slot:item.value="{ item }">
                {{ item.value }}
              </template>
            </v-data-table>
            <div v-if="chartData.length === 0">暂无数据</div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>


<script>
import * as echarts from 'echarts'

export default {
  data() {
    return {
      chartData: [],
      headers: [
        { text: '项目规模', value: 'name' },
        { text: '个数', value: 'value' }
      ]
    }
  },
  mounted() {
    // 计算饼状图数据并更新 chartData 数组
    let data = [
      {value: 335, name: '微小型（1~3人）'},
      {value: 310, name: '小型（4~7人）'},
      {value: 234, name: '中型（8~15人）'},
      {value: 135, name: '大型（16~30人）'},
      {value: 1548, name: '巨大型（>30人）'}
    ]
    this.chartData = data.map(item => ({
      name: item.name,
      value: item.value
    }))

    // 创建 ECharts 实例并绘制饼状图
    let myChart = echarts.init(this.$refs.myChart)
    // 窗口变化时重新渲染饼状图位置
    window.addEventListener('resize', () => {
      myChart.resize()
    })
    console.log(myChart)
    myChart.setOption({
      title: {
        text: '',
        left: 'center'
      },
      tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b}: {c} ({d}%)'
      },
      legend: {
        orient: 'vertical',
        left: 10,
        data: ['微小型（1~3人）', '小型（4~7人）', '中型（8~15人）', '大型（16~30人）', '巨大型（>30人）']
      },
      series: [
        {
          name: '项目规模',
          type: 'pie',
          radius: ['50%', '70%'],
          center: ['50%', '50%'], // 设置饼状图的位置
          avoidLabelOverlap: false,
          label: {
            show: false,
            position: 'center'
          },
          labelLine: {
            show: false
          },
          data: data
        }
      ]
    })
  }
}
</script>
