<script>
import axios from "axios";

export default {
    name: "IssueList",
    data() {
        return {
        issues: [
            {
            id: 1,
            issuer: 'TrickEye',
            title: 'issue title1',
            isOpen: true
            }, {
            id: 2,
            issuer: 'TrickEye',
            title: 'issue title2',
            isOpen: false
            }
        ],
        
        issuesBusy: true,
        }
    },
    props: {
        selectedIssues: {
            type: Array,
            required: true
        }
    },
    emits: ['update:selectedIssues'],
    computed: {
        isAllSelected() {
            return Array.isArray(this.selectedIssues) && this.issues.length > 0 && this.selectedIssues.length === this.issues.length
        },
        selectedIssueIds: {
            get() {
                return this.selectedIssues.map(Issue => Issue.id);
            },
            set(newIds) {
                // 根据新的选中 id 数组构造新的 selectedIssues
                const updated = this.issues.filter(issue => newIds.includes(issue.id));
                this.$emit('update:selectedIssues', updated);
            }
        }
    },
    methods: {
        toggleSelectAll() {
            if (this.isAllSelected) {
                this.$emit('update:selectedIssues', []);
            } else {
                this.$emit('update:selectedIssues', [...this.issues]);
            }
        },
        updateIssue() {
            if(!this.$route.params.userid || !this.$route.params.projid || !this.$route.params.repoid) {
                console.log('get issue failure with no params')
                return
            }
            this.issuesBusy = true
            axios.post('/api/develop/getIssueList', {
                userId: this.$route.params.userid,
                projectId: this.$route.params.projid,
                repoId: this.$route.params.repoid,
            }).then((res) => {
                if (res.data.errcode === 0) {
                    let issues = res.data.data.map((cur, index, arr) => {
                        return {
                            id: cur.issueId,
                            issuer: cur.issuer,
                            title: cur.issueTitle,
                            time: cur.issueTime,
                            isOpen: cur.isOpen,
                            ghLink: cur.ghLink
                        }
                    })
                    this.issues = issues
                    this.issuesBusy = false
                } else {
                    console.log(res);
                    alert('/api/reviews/getIssueList error with not 0 err code (' + res.data.errcode + ') ' + res.data.message)
                    this.issuesBusy = false
                }
            }).catch((err) => {
                alert('/api/reviews/getIssueList error' + err)
                this.issuesBusy = false
            })
        },
        isChecked(id) {
            return Array.isArray(this.selectedIssues) && this.selectedIssues.some(issue => issue.id === id)
        },
        toggleIssue(issue) {
            const exists = this.selectedIssues.find(i => i.id === issue.id)
            let updated
            if (exists) {
                updated = this.selectedIssues.filter(i => i.id !== issue.id)
            } else {
                updated = [...this.selectedIssues, issue]
            }
            this.$emit('update:selectedIssues', updated)
        }
    }, 
    mounted() {
        this.updateIssue()
    },
}
</script>

<template>
  <div>

    <el-button type="primary" @click="toggleSelectAll">{{ isAllSelected ? '取消全选' : '全选' }}</el-button>

    <el-skeleton :loading="issuesBusy" animated>
        <template #default>
            <div class="issue-table-container">
                <el-table :data="issues" style="width: 100%">
                <el-table-column width="50">
                    <template #default="scope">
                        <el-checkbox
                            :label="scope.row.id"
                            v-model="selectedIssueIds"
                        />
                        <!-- <el-checkbox
                            :checked="isChecked(scope.row.id)"
                            @change="() => toggleIssue(scope.row)"
                        /> -->

                    </template>
                </el-table-column>
                <el-table-column label="编号" prop="id">
                    <template #default="scope">
                    #{{ scope.row.id }} ({{ scope.row.isOpen ? '开启' : '已关闭' }})
                    </template>
                </el-table-column>
                <el-table-column label="作者" prop="issuer" />
                <el-table-column label="标题" prop="title" />
                </el-table>
            </div>
        </template>
    </el-skeleton>

    <div v-if="!issuesBusy && issues.length === 0">
      <p>事务似乎空空如也？现在就去GitHub上发一个吧！</p>
    </div>
  </div>
</template>

<style scoped>

.issue-table-container {
    max-height: 400px;
    overflow-y: auto;
    border: 1px solid #dcdfe6;
    background-color: antiquewhite;
}

</style>