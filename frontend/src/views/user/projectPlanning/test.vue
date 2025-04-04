<template>
    <el-popover placement="bottom" trigger="hover">
        <div slot="reference" class="plan" :style="{
            'background-color': statusColor,
            'margin-top': 0.1 * 30 + 'px'
        }" @click="onClick">
            <div class="runTime">
                <span>S:{{ item.start }}</span>
                <span>E:{{ item.end }}</span>
            </div>
            <div class="middle">任务：{{ item.name }}</div>
            <!-- <div class="passenger">{{item.passenger}}人</div> -->
        </div>

        <div class="detail">
            <span class="header">{{ data.name }}</span>
            <ul>
                <li>
                    <span>开始时间：</span><span>{{ item.start }}</span>
                </li>
                <li>
                    <span>结束时间：</span><span>{{ item.end }}</span>
                </li>
                <li>
                    <span>负责人：</span><span>{{ item.managerName }}</span>
                    
                </li>
                
                <li>
                    <span>任务简介：</span><span>{{ item.intro }}</span>
                </li>
                <li>
                    <span>任务状态：</span><span>{{ item.status == 'B' ? '进行中': '已完成' }}</span>
                </li>
                <li>
                    <span>任务标签：</span><span>{{ item.label }}</span>
                </li>
            </ul>
        </div>
    </el-popover>
</template>
  
<script>
import getIdenticon from "@/utils/identicon";
import dayjs from "dayjs";

const NOW_PLAN = "#D5F8EA";
const FUTHER_PLAN = "#BFF2FE";
const PAST_PLAN = "#F2F2F2";
export default {
    name: "Test",
    props: {
        data: Object,
        item: Object,
    },
    data() {
        return {
            dayjs: dayjs
        };
    },
    computed: {
        statusColor() {
            if(this.item.status == 'A') {
                return PAST_PLAN;
            } else if(this.item.status == 'B'){
                return NOW_PLAN;
            } else {
                return FUTHER_PLAN;
            }
        },
        startToString() {
            return dayjs(this.item.start).format("HH");
        },
        endToString() {
            return dayjs(this.item.end).format("HH");
        }
    },
    methods: {
        onClick() {
        },
        getIdenticon
    }
};
</script>
  
<style lang="scss" scoped>
.middle {
    flex: 1;
    text-align: center;
    padding-left: 5px;
}

.runTime {
    display: flex;
    flex-direction: column;
}

.plan {
    display: flex;
    align-items: center;
    box-sizing: border-box;
    height: 40px;
    
    border: 1px solid #f0f0f0;
    border-radius: 5px;
    color: #333333;
    padding-left: 5px;
    font-size: 0.8rem;
    // opacity: 0.8;
}

.detail {
    .header {
        text-align: center;
        font-size: 1rem;
    }
}

.detail ul {
    list-style: none;
    padding: 0px;

    li {
        span {
            display: inline-block;
            width: 80px;
            color: #777;
            font-size: 0.8rem;
        }

        span:first-child {
            text-align: right;
        }

        span:last-child {}
    }
}
</style>
  