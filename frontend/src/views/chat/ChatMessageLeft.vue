<template>
  <div class="chat_left">
    <div class="chat_left_item_2">
      <div class="chat_left_time">{{ time }}</div>
      <div class="chat_left_content">
        {{content}}
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "ChatMessageLeft",
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
.chat_left{
  width: 100%;
  margin-left: 10px;
  min-height: 120px;
  box-sizing: content-box;
  margin-top: 20px;
}

.chat_left_item_2{
  width: 55%;
  height: auto;
  float: left;
  margin-top: 10px;
}
.chat_left_item_2 .chat_left_time{
  width: 100%;
  text-align: left;
  height: auto;

}
.chat_left_item_2 .chat_left_content{
  padding: 15px;
  margin-top: 10px;
  float: left;
  background-color: #f4f5f7;
  border-radius: 10px;
  border-top-left-radius: 0px;
  height: auto;
}
</style>
