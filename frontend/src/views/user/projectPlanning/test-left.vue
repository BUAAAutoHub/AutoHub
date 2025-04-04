<template>
    <div class="name">
        <div class="carId" style="display: flex; justify-content: center;">
            <span v-if="data.isFirst">冲刺：{{ data.name }}</span>
            <v-icon v-else style="margin-left: 10%;">mdi-arrow-right-bottom</v-icon>
        </div>
    </div>
</template>
  
<script>
export default {
    name: "TestLeft",
    props: {
        data: Object
    }
};
</script>
  
<style scoped>
.name {
    display: flex;
    justify-content: center;
    box-sizing: border-box;
    overflow: hidden;
    height: 100%;
    width: 100%;
    padding: 0 5px 0 0;
    border-radius: 8px 0 0 8px;
    align-items: center;
}

.colorBar {
    width: 10px;
    height: 100%;
}

.carId {
    flex: 1;
}

.type {
    padding: 0 5px 0 0;
    font-size: 1.2rem;
}
</style>
  