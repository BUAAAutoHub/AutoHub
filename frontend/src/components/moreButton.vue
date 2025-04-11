<template>
    <el-dropdown trigger="click" :teleported="false">
        <div class="more-button">
            <i :class="'iconfont icon-xiala'"></i>
        </div>
        <template #dropdown>
            <el-dropdown-menu>
                <el-dropdown-item @click="">
                    <el-icon>
                    </el-icon>
                </el-dropdown-item>
                <el-dropdown-item @click="">
                    <el-icon>
                    </el-icon>
                </el-dropdown-item>
                <el-dropdown-item divided @click="">
                    <el-icon>

                    </el-icon>
                </el-dropdown-item>
                <el-dropdown-item @click="">
                    <el-icon>

                    </el-icon>
                </el-dropdown-item>
                <el-dropdown-item @click="">
                    <el-icon>

                    </el-icon>
                </el-dropdown-item>
                <el-dropdown-item divided @click="">
                    <el-icon>

                    </el-icon>
                </el-dropdown-item>
                <el-dropdown-item @click="">
                    <el-icon>

                    </el-icon>
                </el-dropdown-item>
            </el-dropdown-menu>
        </template>
    </el-dropdown>
</template>
  
<script>

</script>
  
<style>
.more-button {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 43px;
    cursor: pointer;
    border-left: 1px solid var(--el-border-color-light);
    transition: all 0.3s;

    &:hover {
        background-color: var(--el-color-info-light-9);
    }

    .iconfont {
        font-size: 12.5px;
    }
}
</style>