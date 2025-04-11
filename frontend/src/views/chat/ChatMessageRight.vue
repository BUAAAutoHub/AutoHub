<template>
  <div class="chat_right">
    <div class="chat_right_item_2">
      <div class="chat_right_time">{{time}}</div>
      <div class="chat_right_content">
        {{content}}
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "ChatMessageRight",
  components:{
  },
  data() {
  },
  props:{
    time:{
      type:String,
      default:'--:--'
    },
    content:{
      type:String,
      default:'啦啦啦啦啦啦啦啦啦啦啦啦啦啦啦啦啦啦啦啦啦啦啦啦啦啦啦啦啦啦啦啦啦啦啦啦啦啦啦啦啦啦啦啦啦啦啦啦啦啦'
    }
  }
}
</script>

<style scoped>
/* 右边 */
.chat_right{
  width: 100%;
  margin-top: 20px;
}
.chat_right_item_2{
  width: 55%;
  height: auto;
  float: right;
  box-sizing: content-box;
  margin-top: 10px;
  margin-right: 10px;
}
.chat_right_time{
  width: 100%;
  margin-right: 10px;
  box-sizing: content-box;
  text-align: right;
}
.chat_right_content{
  float: right;
  padding: 15px;
  height: auto;
  border-radius: 10px;
  margin-top: 10px;
  border-top-right-radius: 0px;
  background-color: #445b53;
  color: white;
}

</style>
