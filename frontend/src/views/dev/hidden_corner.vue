<template>
<v-main>

    <img :src="getIdenticon('20373866@buaa.edu.cn', 80, 'user')" width="80px" height="80px" />
    <img :src="getIdenticon('20373866@buaa.edu.cn', 100, 'user')" width="100px" height="100px" />
    <img :src="getIdenticon('20373866@buaa.edu.cn', 200, 'user')" width="200px" height="200px" />
    <v-img :src="getIdenticon('20373866@buaa.edu.cn', 200, 'user')" width="200px" height="200px" />
    <v-img :src="getIdenticon('20373866@buaa.edu.cn', 200, 'proj')" width="200px" height="200px" />

    <v-textarea v-model="url" label="URL"></v-textarea>
    <v-textarea v-model="data" label="DATA"></v-textarea>
    <v-btn @click="btnclick()">test</v-btn>
    <div>{{ msg }}</div>
</v-main>
</template>

<script>
import axios from "axios";
import getIdenticon from '@/utils/identicon.js'

export default {
    name: "hidden_corner", // 用来测试API的
    data() {
        return {
            msg: null,
            url: "/api/management/showUsers",
            data: "{\"managerId\": 1}"
        }
    },
    methods: {
        getIdenticon,
        btnclick() {
            // axios.post("/api/plan/watchAllProject", {userId: 2})
            axios.post(this.url, JSON.parse(this.data))
            .then((res) => {
                console.log(res)
                this.msg = res.data
            })
            .catch((err) => {
                console.log(err); this.msg = err
            })
        }
    }
}
</script>

<style scoped>

</style>