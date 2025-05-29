
<script>
import axios from "axios";

export default {
    name: "PrList",
    data() {
        return {
            prs: [
                {
                id: 1,
                author: 'TrickEye',
                title: 'PR title1',
                date: '20230403',
                fromBranchId: 2,
                toBranchId: 1,
                isOpen: true
                }, {
                id: 2,
                author: 'TrickEyeee',
                title: 'PR title2',
                date: '20230402',
                fromBranchId: 3,
                toBranchId: 1,
                isOpen: true
                }
            ],
            prsBusy: true,
        }
    }, 
    props: {
        selectedPrs: {
            type: Array,
            required: true
        }
    },
    emits: ['update:selectedPrs'],
    computed: {
        isAllSelected() {
            return Array.isArray(this.selectedPrs) && this.prs.length > 0 && this.selectedPrs.length === this.prs.length
        },
        selectedPrIds: {
            get() {
                return this.selectedPrs.map(pr => pr.id);
            },
            set(newIds) {
                // 根据新的选中 id 数组构造新的 selectedPrs
                const updated = this.prs.filter(pr => newIds.includes(pr.id));
                this.$emit('update:selectedPrs', updated);
            }
        }
    },
    methods: {
        toggleSelectAll() {
            if (this.isAllSelected) {
                this.$emit('update:selectedPrs', [])
            } else {
                this.$emit('update:selectedPrs', [...this.prs])
            }
        },
        updatePR() {
            if(!this.$route.params.userid || !this.$route.params.projid || !this.$route.params.repoid) {
                console.log('get pr failure with no params')
                return
            }
            this.prsBusy = true
            console.log('update pr list' + this.$route.params.userid + ' ' + this.$route.params.projid + ' ' + this.$route.params.repoid)
            axios.post('/api/develop/getPrList', {
                userId: this.$route.params.userid,
                projectId: this.$route.params.projid,
                repoId: this.$route.params.repoid,
            }).then((res) => {
                if (res.data.errcode === 0) {
                    let prs = res.data.data.map((cur, index, arr) => {
                        return {
                            id: cur.prId,
                            author: cur.prIssuer,
                            title: cur.prTitle,
                            date: cur.prTime,
                            isOpen: cur.isOpen,
                            ghLink: cur.ghLink,
                            fromBranchName: cur.fromBranchName,
                            toBranchName: cur.toBranchName
                        }
                    })
                    this.prs = prs
                    this.prsBusy = false
                } else {
                    console.log('get pr failure with not 0 err code + {' + res.data.errcode + ')' + res.data.message)
                    this.prsBusy = false
                }
            }).catch((err) => {
                console.log('get pr failure with err: ' + err)
                this.prsBusy = false
            })
        },
        isChecked(id) {
            return Array.isArray(this.selectedPrs) && this.selectedPrs.some(pr => pr.id === id)
        },
        togglePr(pr) {
            const exists = this.selectedPrs.find(p => p.id === pr.id)
            let updated
            if (exists) {
                updated = this.selectedPrs.filter(p => p.id !== pr.id)
            } else {
                updated = [...this.selectedPrs, pr]
            }
            this.$emit('update:selectedPrs', updated)
        }
    }, 
    mounted() {
        this.updatePR()
    },

}
</script>

<template>
  <div>

    <el-button type="primary" @click="toggleSelectAll">{{ isAllSelected ? '取消全选' : '全选所有 PR' }}</el-button>

    <el-skeleton :loading="prsBusy" animated>
        <template #default>
            <div class="pr-table-container">
                <el-table :data="prs" style="width: 100%">
                <el-table-column width="50">
                    <template #default="scope">
                        <el-checkbox
                            :label="scope.row.id"
                            v-model="selectedPrIds"
                        />
                    </template>
                </el-table-column>
                <el-table-column label="编号" prop="id">
                    <template #default="scope">
                    #{{ scope.row.id }} ({{ scope.row.isOpen ? '开启' : '已关闭' }})
                    </template>
                </el-table-column>
                <el-table-column label="作者" prop="author" />
                <el-table-column label="标题" prop="title" />
                <el-table-column label="合并信息">
                    <template #default="scope">
                    从分支“{{ scope.row.fromBranchName }}”合并到“{{ scope.row.toBranchName }}”
                    </template>
                </el-table-column>
                </el-table>
            </div>
        </template>
    </el-skeleton>

    <div v-if="!prsBusy && prs.length === 0">
      <p>合并请求似乎空空如也？现在就去GitHub上发一个吧！</p>
    </div>
  </div>
</template>

<style scoped>

.pr-table-container {
    max-height: 400px;
    overflow-y: auto;
    border: 1px solid #dcdfe6;
}

</style>