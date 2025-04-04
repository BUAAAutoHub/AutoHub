<template>
  <v-container fluid fill-height :style="getRadialGradient(selectedTopic)">
    <v-row align="center" justify="center">
      <v-col cols="12">
        <v-card class="mx-auto" width="500" height="350" padding="16">
          <v-img
            :src="getUrl(selectedTopic)"
            width="500" height="350"
            gradient="131deg, rgba(255,255,255,0.6) 0%, rgba(255,255,255,0.8) 24%, rgba(0,0,0,0) 100%"
          >
            <v-card-title class="headline font-weight text-left">主题设置</v-card-title>
            <v-divider></v-divider>
            <!--          <v-row align="center">-->
            <!--            <v-col cols="3" class="text-center">-->

            <!--            </v-col>-->
            <!--            <v-col cols="8">-->

            <!--            </v-col>-->
            <!--          </v-row>-->
            <v-card-text>
              <v-radio-group v-model="selectedTopic">
                <v-radio v-for="i in topicList" :key="i.value" :label="i.label" :value="i.value" :color="i.color"></v-radio>
              </v-radio-group>
            </v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn :color="getColor(selectedTopic)" @click="back">返回</v-btn>
              <v-btn :color="getColor(selectedTopic)" @click="save">保存主题</v-btn>
            </v-card-actions>
          </v-img>
        </v-card>
      </v-col>
    </v-row>
<!--  <v-container class="pa-0">-->
<!--    <v-card>-->
<!--      <v-card-title class="headline font-weight text-left"> 用户{{userProfileDialogMessage.name}}的个人信息 </v-card-title>-->
<!--      <v-divider></v-divider>-->

<!--      <v-card-actions>-->
<!--        <v-spacer></v-spacer>-->
<!--        <v-btn color="red" text @click="closeUserProfileDialog">关闭</v-btn>-->
<!--        <v-btn color="blue" text @click="saveProfile">确认修改</v-btn>-->
<!--      </v-card-actions>-->
<!--    </v-card>-->
  </v-container>
</template>

<script>
import axios from "axios";
import Cookies from "js-cookie";
import topicSetting from '@/utils/topic-setting.js'

export default {
  name: "topic",
  inject: {
    user: { default: null },
    updateUser: {default: null},
    updateTopic: {default: null},
  },
  data () {
    return {
      selectedTopic: this.user.topic,
      topicList: [
        {
          label: '红色系',
          value: 'A',
          color: 'red'
        },
        {
          label: '橙色系',
          value: 'B',
          color: 'orange'
        },
        {
          label: '绿色系',
          value: 'C',
          color: 'green'
        },
        {
          label: '蓝色系',
          value: 'D',
          color: 'blue'
        },
        {
          label: '紫色系',
          value: 'E',
          color: 'purple'
        },
      ],
    }
  },
  methods: {
    back() {
      this.$router.go(-1);
    },
    save() {
      console.log(this.selectedTopic)
      axios.post("/api/saveTopic", {userId: this.user.id, topic: this.selectedTopic})
          .then((response) => {
            console.log(response)
            if (response.data.errcode === 0) {
              this.$message({
                type: 'success',
                message: "主题保存成功"
              });
              console.log(response.data.data)
              Cookies.set('user', JSON.stringify(response.data.data))
              this.updateUser()
              this.updateTopic()
              console.log(Cookies.get('user'))
              console.log(this.user)
            } else {
              this.$message({
                type: 'error',
                message: "主题保存失败"
              });
            }
          })
          .catch((err) => {
            console.error(err);
          })
    },
    getUrl: topicSetting.getUrl,
    getColor: topicSetting.getColor,
    getRadialGradient: topicSetting.getRadialGradient,
  },
}
</script>

<style scoped>

</style>