<template>
  <v-container>
    <v-card>
      <v-card-title>
        <v-text-field
            v-model="search"
            append-icon="mdi-magnify"
            label="搜索"
            single-line
            hide-details
        ></v-text-field>
      </v-card-title>
      <v-data-table
          :headers="headers"
          :items="loginMessages"
          :search="search"
      >
        <template #item.loginTime="{item}">
          {{ pro(item.loginTime) }}
        </template>
      </v-data-table>
    </v-card>
  </v-container>
</template>

<script>
import axios from "axios";
import util from "@/views/util";
export default {
  inject: {
    user: { default: null }
  },
  data () {
    return {
      msg: null,
      data: "{\"managerId\": 1}",
      search: '',
      headers: [
        {
          text: '用户名',
          align: 'start',
          // sortable: false,
          value: 'name',
        },
        { text: '邮箱', value: 'email' },
        { text: '最近一次登录时间', value: 'loginTime' },
      ],
      loginMessages: [
        // {
        //   name: 'Frozen Yogurt',
        //   email: '123@qq.com',
        //   loginTime: '2023.1.1'
        // },
        // {
        //   name: 'aaaa',
        //   email: '1920@qq.com',
        //   loginTime: '2023.1.2'
        // },
        // {
        //   name: 'hfsak',
        //   email: '4239@qq.com',
        //   loginTime: '2023.1.3'
        // },
        // {
        //   name: 'Frozen Yogurt',
        //   email: '123@qq.com',
        //   loginTime: '2023.1.1'
        // },
        // {
        //   name: 'Frozen Yogurt',
        //   email: '123@qq.com',
        //   loginTime: '2023.1.1'
        // },
      ],
    }
  },
  created() {
    this.showLoginMessages()
  },
  // TODO：传给后端管理员id，如果报错，不显示信息而显示弹窗
  methods: {
    pro(loginTime) {
      return util.processTime(loginTime);
    },
    showLoginMessages() {
      axios.post("/api/management/showUsersLogin", {managerId: this.user.id})
          .then((response) => {
            console.log(response)
            if (response.data.errcode === 1) {
              window.alert("您没有权限")
            } else {
              this.loginMessages = response.data.loginMessages
            }
          })
          .catch((err) => {
            console.error(err);
            this.loginMessages = null
          })
    },
  },
}
</script>

<style scoped>

</style>