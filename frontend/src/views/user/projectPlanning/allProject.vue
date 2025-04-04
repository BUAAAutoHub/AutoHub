<template>
  <div style="width: 100%; height: 100%">
    <div class="one">
      <h1 style="position: absolute; left: 5%; top: 10%">项目</h1>
    </div>
    <div style="margin-bottom: 70px; justify-content: center; /* 水平居中 */ display: flex;">
      <div class="block" style="margin-left: 40%;">
        <span class="demonstration">选择项目 {{ ' ' }}</span>
        <el-select style="margin-right: 5%;" v-model="curProj" placeholder="请选择">
          <el-option v-for="item in projects" :key="item.id" :label="item.name" :value="item.id">
          </el-option>
        </el-select>
        <span class="demonstration">选择时间范围 {{ ' ' }}</span>
        <el-date-picker v-model="startEnd" type="daterange" range-separator="至" start-placeholder="开始日期"
          end-placeholder="结束日期" format="yyyy-MM-dd" :picker-options="pickerOptions" unlink-panels>
        </el-date-picker>
      </div>
      <div style="width: 90%; margin-top: 30px; justify-content: center; /* 水平居中 */ display: flex;">
        <v-gantt-chart style="margin-left: 5%;" :startTime="startTime" :endTime="endTime" :datas="filterDatas" :scale="1440"
          :cellHeight="50" :cellWidth="100">
          <template v-slot:block="{ data, item }">
            <!-- 你的容器块组件 -->
            <Test :data="data" :item="item"></Test>
          </template>
          <template v-slot:left="{ data }">
            <!-- 你的行名组件 -->
            <TestLeft :data="data"></TestLeft>
          </template>
          <template v-slot:title> 任务日程表 </template>
        </v-gantt-chart>
      </div>
    </div>
    <div class="three">
      <v-data-table :headers="headers" :items="projectData" :single-expand="true" :items-per-page="5" show-expand
        :expanded.sync="expanded" class="elevation-1" item-key="projectId" :search="search"
        :custom-filter="filterOnlyCapsText">
        <template v-slot:no-data>
          <div style="text-align: center;">
            <img src="../../../assets/search.png" height="150px" width="150px" />
          </div>
          <div style="font-size:20px;font-weight: bold">
            没有找到数据
          </div>
          <!-- <v-img
           max-height="30%"
           max-width="30%"
           style  src="@/assets/search.png"></v-img>="position:absolute;left:35%;right:35%;top:5%" -->
        </template>
        <template v-slot:no-results>
          <div style="text-align: center;">
            <img src="../../../assets/search.png" height="150px" width="150px" />
          </div>
          <div style="font-size:20px;font-weight: bold">
            没有找到数据
          </div>
        </template>
        <template v-slot:top>
          <div style="width: 100%; height: 100%; position: relative">
            <v-text-field v-model="search" label="请输入项目名称进行查询" class="mx-4"
              style="width: 30%; display: inline-block"></v-text-field>
            <v-btn style="
                top: 20%;
                right: 2%;
                height: 60%;
                width: 10%;
                position: absolute;
              " depressed :color="getTopicColor(user.topic)" @click="setupDialog = true">创建项目
            </v-btn>
          </div>
        </template>
        <template v-slot:expanded-item="{ headers, item }">
          <td :colspan="headers.length">
            {{ item.projectIntro }}
          </td>
        </template>
        <template v-slot:[`item.managerName`]="{ item }">
          <div style="position: relative">
            <v-avatar size="25" color="indigo">
              <!--              <span class="white&#45;&#45;text text-h6">{{ item.managerName[0] }}</span>-->
              <v-img :src="getIdenticon(item.managerName, 25, 'user')"></v-img>
            </v-avatar>
            <div style="position: absolute; left: 20%; bottom: 3%">
              {{ item.managerName }}
            </div>
          </div>
        </template>
        <template v-slot:[`item.projectName`]="{ item }">
          <v-icon small>mdi-application-export</v-icon>
          <a @click="getProj(item)" style="position:relative;left:5%;">{{ item.projectName }}</a>
        </template>
        <template v-slot:[`item.actions`]="{ item }">
          <v-icon small class="mr-2" @click="handleEdit(item)">
            mdi-pencil
          </v-icon>
          <v-icon small @click="handleDelete(item)"> mdi-delete</v-icon>
        </template>
        <template v-slot:[`item.state`]="{ item }">
          <v-chip :color="getColor(item.state)" dark @click="handleState(item)">
            {{ transform(item.state) }}
          </v-chip>
        </template>
      </v-data-table>
    </div>

    <el-dialog title="创建项目" :visible.sync="setupDialog" width="50%">
      <el-form :label-position="labelPosition" label-width="80px" :model="form" ref="form">
        <el-form-item label="项目名称">
          <el-input v-model="form.name"></el-input>
        </el-form-item>
        <el-form-item label="活动概述">
          <el-input type="textarea" v-model="form.intro" :autosize="{ minRows: 5, maxRows: 10 }"></el-input>
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="cancelSetupProject">取 消</el-button>
        <el-button type="primary" @click="setupProject">确 定</el-button>
      </span>
    </el-dialog>

    <el-dialog title="编辑项目" :visible.sync="editDialog" width="50%">
      <el-form :label-position="labelPosition" label-width="80px" :model="form" ref="form">
        <el-form-item label="项目名称">
          <el-input v-model="form.name"></el-input>
        </el-form-item>
        <el-form-item label="活动概述">
          <el-input type="textarea" v-model="form.intro" :autosize="{ minRows: 5, maxRows: 10 }"></el-input>
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="editDialog = false">取 消</el-button>
        <el-button type="primary" @click="editProject">确 定</el-button>
      </span>
    </el-dialog>
    <!-- <div class="card-wrapper">
      <project-table class="component"/>
    </div> -->
  </div>
</template>

<script>
import {
  deleteProject,
  modifyProject,
  newProject,
  watchAllProject,
  showTaskList,
  modifyProjectStatus,
} from "@/api/user";
import Cookies from "js-cookie";
import getIdenticon from "@/utils/identicon";
import topicSetting from "@/utils/topic-setting";
import dayjs from "dayjs" //时间库
import Test from "./test.vue"; //你自己的gantt条容器
import TestLeft from "./test-left.vue"; //你自己的行名称组件

export default {
  // inject: ['user', 'selectedProj'],
  name: "AllProject",
  created() {
    this.get_project();
  },
  watch: {
    startEnd(newValue, oldValue) {
      // 在 message 数据变化时执行的操作

      //var dates = newValue.split(',');

      // 解析起始日期和结束日期
      var startDate = new Date(newValue[0]);
      var endDate = new Date(newValue[1]);

      // 格式化日期
      var formattedStartDate = this.formatDate(startDate);
      var formattedEndDate = this.formatDate(endDate);
      this.startTime = formattedStartDate;
      this.endTime = formattedEndDate;
      console.log(this.startTime + '  ' + this.endTime)
      this.filter();
    },
    curProj() {
      this.getTaskList();
    }
  },
  inject: {
    user: { default: null },
    selectedProj: { default: null },
    updateUserProj: { default: null },
  },
  components: {
    Test,
    TestLeft
  },
  provide() {
    return {
      user: this.user,
      projectData: this.projectData
    };
  },
  data() {
    return {
      tasks: [],
      projects: [],
      curProj: '',
      startEnd: ['2023-01-01', '2024-12-31'],
      startTime: '2023-01-01',//时间轴开始时间
      endTime: '2024-12-31',
      filterDatas:[],
      datas: [
        {
          id: 'arrayOne',
          name: 'sala',
          gtArray: [
            {
              name: 'itemOne',
              start: '2024-06-06',
              end: '2024-06-09'
              // ...其他属性
            },
            {
              name: 'itemTwo',
              start: '2024-06-10',
              end: '2024-06-12'
              // ...其他属性
            }
          ],
          //...其他属性
        },

        {
          id: 'arrayTwo',
          name: 'sala',
          gtArray: [
            {
              name: 'itemOne',
              start: '2024-06-06',
              end: '2024-06-09'
              // ...其他属性
            },
            {
              name: 'itemTwo',
              start: '2024-06-10',
              end: '2024-06-12'
              // ...其他属性
            }
          ],
          //...其他属性
        }
        //... 其他数组数据
      ],
      labelPosition: "left",
      headers: [
        {
          text: "名称",
          align: "start",
          sortable: false,
          value: "projectName",
        },
        { text: "状态", value: "state" },
        { text: "创建时间", value: "deadline", sortable: true },
        { text: "负责人", value: "managerName" },
        { text: "", value: "actions", sortable: false },
        { text: "", value: "data-table-expand" },
      ],
      projectData: [
        // {
        //   "name": 'ppppp1',
        //   "state": '进行中',
        //   "time": "2002-12-18",
        //   "owner": 'szx',
        //   "access": "A"/"B" 增加项目正常/禁用字段
        //   "intro": 'very good'
        // },
        // {
        //   "name": 'ppppp2',
        //   "state": '进行中',
        //   "time": "2002-12-17",
        //   "owner": 'szx',
        //   'intro': 'very bad'
        // }
      ],
      search: "",
      setupDialog: false,
      editDialog: false,
      form: {
        name: "",
        intro: "",
        id: "",
      },
      expanded: [],
    };
  },
  methods: {
    getIdenticon,
    formatDate(date) {
    var year = date.getFullYear();
    var month = (date.getMonth() + 1).toString().padStart(2, '0');
    var day = date.getDate().toString().padStart(2, '0');

    return year + '-' + month + '-' + day;
},
    filter() {
      this.filterDatas = [];
      for(var i = 0; i < this.datas.length; i++) {
        var s = this.datas[i].gtArray[0].start;
        var e = this.datas[i].gtArray[0].end;
        if(e < this.startTime || s > this.endTime) {
          continue;
        }else {
          this.filterDatas.push(this.datas[i]);
        }
      }
    },
    setDatas() {
      this.datas = [];
      for (var i = 0; i < this.tasks.length; i++) {
        var subList = this.tasks[i].subTaskList;
        for (var j = 0; j < subList.length; j++) {
          var newItem = {
            id: this.tasks[i].taskId,
            name: this.tasks[i].taskName,
            isFirst: false,
            gtArray: []
        };
        var subTask = {
          name: subList[j].subTaskName,
          start: subList[j].start_time.substring(0, 10),
          end: subList[j].deadline.substring(0, 10),
          intro: subList[j].intro,
          status: subList[j].status,
          label: subList[j].subTaskLabel,
          id: subList[j].managerId,
          managerName: subList[j].managerName
        }
        newItem.gtArray.push(subTask);
        if (j == 0) {
          newItem.isFirst = true;
        }
        this.datas.push(newItem);
      }
    }
    this.filter();
  },
  getTaskList() {
    showTaskList({ userId: this.user.id, projectId: this.curProj }).then(
      res => {
        console.log("showTaskList");
        console.log(res);
        this.tasks = res['data']['data'];
        this.setDatas();
        this.tasks.forEach((task) => {
          this.$set(task, 'displayReviews', false);
        })
        console.log(this.tasks);
        console.log(this.tasks[0].subTaskList)
      }
    );
  },
  getProj(project) {
    console.log("getProj");
    console.log(JSON.stringify(project));
    let manager = Cookies.get("manager")
    if (project.access === "B" && manager === undefined) { // 项目禁用，且不是管理员跳转
      this.$message({
        type: 'error',
        message: "该项目已被禁用"
      });
    } else {
      Cookies.set("proj", JSON.stringify(project));
      window.location.href = "/allTask";
    }
    // this.proj = Cookies.get(proj);
  },
  filterOnlyCapsText(value, search, item) {
    console.log(value);
    var s = item["projectName"];
    return (
      s != null &&
      search != null &&
      typeof s === "string" &&
      s.toString().toLocaleUpperCase().indexOf(search.toLocaleUpperCase()) !==
      -1
    );
  },
  get_project() {
    Cookies.remove("proj");
    console.log("get_project");
    watchAllProject({ userId: this.user.id }).then((res) => {
      this.projectData = res["data"]["data"];
      console.log(this.projectData);
      this.projects = [];
      if (this.projectData.length > 0) {
        this.curProj = this.projectData[0].projectId;
      }
      for (var i = 0; i < this.projectData.length; i++) {
        var item = {
          id: this.projectData[i].projectId,
          name: this.projectData[i].projectName
        };
        this.projects.push(item);
      }
    });
  },
  handleEdit(row) {
    this.form.id = row.projectId;
    this.form.name = row.projectName;
    this.form.intro = row.projectIntro;
    this.editDialog = true;
  },
  handleDelete(row) {
    this.$confirm("此操作将永久删除该项目, 是否继续?", "提示", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning",
    })
      .then(() => {
        this.$message({
          type: "success",
          message: "删除成功!",
        });
        deleteProject({
          projectId: row.projectId,
          userId: this.user.id,
        }).then((res) => {
          this.get_project();
          this.updateUserProj();
        });
      })
      .catch(() => {
        this.$message({
          type: "info",
          message: "已取消删除",
        });
      });
  },
  handleState(item) {
    if (item.state == "B") {
      this.handleComplete(item);
    } else if (item.state == "A") {
      this.handleNotComplete(item);
    }
  },
  handleComplete(row) {
    this.$confirm("确定已完成项目?", "提示", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning",
    })
      .then(() => {
        this.$message({
          type: "success",
          message: "项目已完成!",
        });
        modifyProjectStatus({
          projectId: row.projectId,
          userId: this.user.id,
          status: "A",
        }).then((res) => {
          console.log(res);
          this.get_project();
        });
      })
      .catch(() => {
        this.$message({
          type: "info",
          message: "已取消",
        });
      });
  },
  handleNotComplete(row) {
    this.$confirm("确定重新进行项目?", "提示", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning",
    })
      .then(() => {
        this.$message({
          type: "warning",
          message: "项目已恢复进行!",
        });
        modifyProjectStatus({
          projectId: row.projectId,
          userId: this.user.id,
          status: "B",
        }).then((res) => {
          console.log(res);
          this.get_project();
        });
      })
      .catch(() => {
        this.$message({
          type: "info",
          message: "已取消",
        });
      });
  },
  cancelSetupProject() {
    this.setupDialog = false;
    this.form = {
      name: "",
      intro: "",
    };
  },
  setupProject() {
    // console.log(this.search);
    // console.log("submit");
    if (this.form.name.trim() === "") {
      this.$message({
        type: "error",
        message: "项目名不能为空！",
      });
      return;
    } else if (this.form.name.length > 16) {
      this.$message({
        type: "error",
        message: "项目名称不能超过16个字符！",
      });
      return;
    }
    for (let i = 0; i < this.projectData.length; i++) {
      if (this.form.name === this.projectData[i].projectName) {
        this.$message({
          type: "error",
          message: "已存在同名项目",
        });
        return;
      }
    }
    this.setupDialog = false;
    newProject({
      projectName: this.form.name,
      projectIntro: this.form.intro,
      userId: this.user.id,
    }).then((res) => {
      console.log(this.user.id);
      console.log(res);
      this.updateUserProj();
      this.get_project();
    });
    this.form = {
      name: "",
      intro: "",
    };
  },
  editProject() {
    if (this.form.name.trim() === "") {
      this.$message({
        type: "error",
        message: "项目名不能为空！",
      });
      return;
    }
    for (let i = 0; i < this.projectData.length; i++) {
      if (
        this.form.name === this.projectData[i].projectName &&
        this.form.id != this.projectData[i].projectId
      ) {
        this.$message({
          type: "error",
          message: "已存在同名项目",
        });
        return;
      }
    }
    this.editDialog = false;
    modifyProject({
      projectId: this.form.id,
      projectName: this.form.name,
      projectIntro: this.form.intro,
    }).then((res) => {
      this.get_project();
      this.updateUserProj();
    });
    this.form = {
      name: "",
      intro: "",
    };
  },
  transform(state) {
    if (state === "A") {
      return "已完成";
    } else if (state === "B") {
      return "进行中";
    } else if (state === "C") {
      return "未开始";
    } else if (state === "D") {
      return "不合法";
    }
  },
  getColor(state) {
    if (state === "A") {
      return "blue";
    } else if (state === "B") {
      return "green";
    }
  },
  getTopicColor: topicSetting.getColor
},
};
</script>

<style scoped>
.one {
  height: 10%;
  position: relative;
}

.two {
  height: 10%;
}

.three {
  position: absolute;
  left: 5%;
  right: 5%;
  height: 80%;
}

.xiangmu {
  position: absolute;
  left: 20%;
}

.card-wrapper {
  position: fixed;
  bottom: 0;
  margin-top: 20px;
  /* 与上面内容的间距 */
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 5px;
  background-color: #f9f9f9;
  box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
  /* 添加阴影效果 */
}</style>
