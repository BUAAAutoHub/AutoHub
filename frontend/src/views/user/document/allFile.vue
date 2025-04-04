<template>
  <div style="display: flex; flex-direction: column;">
    <v-tabs v-model="tab" fixed-tabs :color="getTopicColor(user.topic)" :slider-color="getDarkColor(user.topic)"
    align-with-title style="margin: 0px;">
    <v-tab @click="gotoAll">
      我的文档
    </v-tab>
    <v-tab @click="gotoCollect">
      收藏夹
    </v-tab>
    <v-tabs-slider></v-tabs-slider>
  </v-tabs>





  <v-data-table :headers="headers" :items="documentData" class="elevation-1" :search="searchFile"
    style="position:absolute;left:2.8%;width:94%;top:10%; padding: 0;">
    <template v-slot:[`item.name`]="{ item }">
      <v-icon>mdi-text-box-outline</v-icon>
      <a @click="openMd(item)" style="position:relative;left:2%;top:3%;">{{ item.name }}</a>
    </template>
    <template v-slot:[`item.updateTime`]="{ item }">
      {{ item.updateTime.slice(0, 10) + " " + item.updateTime.slice(11, 19) }}
    </template>
    <template v-slot:expanded-item="{ headers, item }">
      {{ item.outline }}
    </template>
    <template v-slot:no-data>
      <div>
        <el-empty :image-size="200" description="暂无文档"></el-empty>
      </div>
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
      <div style="width: 100%; height: 10%; position: relative">
        <v-text-field v-model="searchFile" label="请输入文档名称进行查询" class="mx-4"
          style="width: 30%; display: inline-block"></v-text-field>
        <v-btn style="
                top: 20%;
                right: 2%;
                height: 60%;
                width: 10%;
                position: absolute;
              " depressed :color="getTopicColor(user.topic)"
          @click="newDocumentForm.name = ''; newDocumentForm.intro = ''; dialog1 = true;"><strong
            style="color: white">创建文档</strong></v-btn>
      </div>
    </template>
    <template v-slot:[`item.collect`]="{ item }">
      <v-icon @click="addCollect(item)" v-if="!item.isCollect">mdi-star-outline</v-icon>
      <v-icon @click="cancelCollect(item)" v-else>mdi-star</v-icon>
      <v-icon @click="editStart(item)">mdi-pencil-outline</v-icon>
      <v-icon @click="handleDelete(item)">mdi-delete-outline</v-icon>
    </template>
    <template v-slot:[`item.limit`]="{ item }">
      <v-icon v-if="item.limit !== 'only read'">mdi-check-bold</v-icon>
    </template>
  </v-data-table>


  <v-dialog v-model="dialog1" hide-overlay width="1000px">
    <v-card width="1000px" style="position: relative;">

      <v-card-title>
        共享文档
      </v-card-title>

      <v-icon @click="dialog1 = false" style="position: absolute;right: 1%;top:1%;">mdi-close</v-icon>

      <v-card-text>
        <v-form>
          <v-text-field v-model="newDocumentForm.name" :counter="10" label="文档名称"
            style="width:80%;position: relative;left:2%" prepend-icon="mdi-map-marker"></v-text-field>
        </v-form>
      </v-card-text>
      <v-card-actions style="position:absolute;right:0%;bottom: 0%;">
        <v-btn text :color="getTopicColor(user.topic)" width="70px" @click="initPeople(); checkNameIntro()">
          下一步
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <v-dialog v-model="dialog2" hide-overlay width="1000px" style="height: 600px;">
    <v-card width="1000px" height="600px" style="position: relative;">

      <v-card-title>
        共享文档
      </v-card-title>
      <v-text-field v-model="search" label="请输入用户名称进行查找"
        style="position:absolute;right:10%;top:3%;height:100%;width: 25%;"></v-text-field>
      <v-icon @click="dialog2 = false" style="position: absolute;right: 1%;top:1%;">mdi-close</v-icon>
      <v-card-text style="position:relative;">
        <v-row no-gutters>
          <v-col md="2">
            <h3>具有权限的用户</h3>
          </v-col>
          <v-spacer></v-spacer>
          <v-col md="2" style="position: relative;">
            <v-icon style="position: absolute;right:15.5%;" @click="delPerson">mdi-minus-box-outline</v-icon>
          </v-col>
        </v-row>
        <v-list shaped>
          <v-list-item-group v-model="deleteGroup" multiple color="indigo">
            <v-list-item v-for="people in filter(peopleCanWrite, search)" :key="people.id"
              active-class="deep-purple--text text--accent-4">
              <template v-slot:default="{ active }">
                <v-list-item-avatar>
                  <v-avatar active-class="deep-purple--text text--accent-4" color="indigo">
                    <!--             <span class="white&#45;&#45;text text-h5">{{ people.peopleName[0] }}</span>-->
                    <v-img :src="getIdenticon(people.peopleName, 48, 'user')"></v-img>
                  </v-avatar>
                </v-list-item-avatar>
                <v-list-item-content>
                  <v-list-item-title>
                    {{ people.peopleName }}
                  </v-list-item-title>
                  <v-list-item-subtitle>
                    {{ people.peopleEmail }}
                  </v-list-item-subtitle>
                </v-list-item-content>
                <v-list-item-action>
                  <span v-if="user.id === people.peopleId"></span>
                  <v-checkbox v-else :input-value="active" color="deep-purple accent-4"></v-checkbox>
                </v-list-item-action>
              </template>
            </v-list-item>
          </v-list-item-group>
        </v-list>
      </v-card-text>

      <v-divider style="width: 900px;"></v-divider>

      <v-card-text style="position: relative;top:2%">
        <v-text-field v-model="searchNot" label="请输入用户名称进行查找"
          style="position:absolute;right:10%;top:-40%;height:100%;width: 25%;"></v-text-field>
        <v-row no-gutters>
          <v-col md="2">
            <h3>没有权限的用户</h3>
          </v-col>
          <v-spacer></v-spacer>
          <v-col md="2" style="position: relative;">
            <v-icon style="position: absolute;right:15.5%;" @click="addPerson">mdi-plus-box-outline</v-icon>
          </v-col>
        </v-row>
        <!-- <p class="ml-s" style="font-size: medium;">添加具有权限修改的用户</p> -->
        <v-list shaped max-height="5">
          <v-list-item-group v-model="addGroup" multiple color="indigo" active-class="deep-purple--text text--accent-4">
            <v-list-item v-for="people in filter(peopleCanNotWrite, searchNot)" :key="people.id">
              <template v-slot:default="{ active }">
                <v-list-item-avatar>
                  <v-avatar active-class="deep-purple--text text--accent-4" color="indigo">
                    <!--             <span class="white&#45;&#45;text text-h5">{{ people.peopleName[0] }}</span>-->
                    <v-img :src="getIdenticon(people.peopleName, 48, 'user')"></v-img>
                  </v-avatar>
                </v-list-item-avatar>
                <v-list-item-content>
                  <v-list-item-title>
                    {{ people.peopleName }}
                  </v-list-item-title>
                  <v-list-item-subtitle>
                    {{ people.peopleEmail }}
                  </v-list-item-subtitle>
                </v-list-item-content>
                <v-list-item-action>
                  <v-checkbox :input-value="active" color="deep-purple accent-4"></v-checkbox>
                </v-list-item-action>
              </template>
            </v-list-item>
          </v-list-item-group>
        </v-list>
      </v-card-text>
      <v-card-actions class="justify-end" style="position: absolute;bottom: 0%;right: 0%;">
        <v-btn text color="primary" width="70px" style="float: right" @click="dialog2 = false; dialog1 = true;">返回</v-btn>
        <v-btn text :color="getTopicColor(user.topic)" width="70px" style="float: right"
          @click="dialog2 = false; dialog1 = false; addDoc()">确认</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <v-dialog v-model="editDialog1" hide-overlay width="1000px">
    <v-card width="1000px" style="position: relative;">

      <v-card-title>
        共享文档
      </v-card-title>

      <v-icon @click="editDialog1 = false" style="position: absolute;right: 1%;top:1%;">mdi-close</v-icon>

      <v-card-text>
        <v-form>
          <v-text-field v-model="editDocumentForm.name" :counter="10" label="文档名称"
            style="width:80%;position: relative;left:2%" prepend-icon="mdi-map-marker"></v-text-field>
        </v-form>
      </v-card-text>
      <v-card-actions style="position:absolute;right:0%;bottom: 0%;">
        <v-btn text :color="getTopicColor(user.topic)" width="70px" @click="initEditPeople()">
          下一步
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <v-dialog v-model="editDialog2" hide-overlay width="1000px" style="height: 600px;">
    <v-card width="1000px" height="600px" style="position: relative;">

      <v-card-title>
        共享文档
      </v-card-title>
      <v-text-field v-model="search" label="请输入用户名称进行查找"
        style="position:absolute;right:10%;top:3%;height:100%;width: 25%;"></v-text-field>
      <v-icon @click="editDialog2 = false" style="position: absolute;right: 1%;top:1%;">mdi-close</v-icon>
      <v-card-text style="position:relative;">
        <v-row no-gutters>
          <v-col md="2">
            <h3>具有权限的用户</h3>
          </v-col>
          <v-spacer></v-spacer>
          <v-col md="2" style="position: relative;">
            <v-icon style="position: absolute;right:15.5%;" @click="delPerson">mdi-minus-box-outline</v-icon>
          </v-col>
        </v-row>
        <v-list shaped>
          <v-list-item-group v-model="deleteGroup" multiple color="indigo">
            <v-list-item v-for="people in filter(peopleCanWrite, search)" :key="people.peopleId"
              active-class="deep-purple--text text--accent-4">
              <template v-slot:default="{ active }">
                <v-list-item-avatar>
                  <v-avatar active-class="deep-purple--text text--accent-4" color="indigo">
                    <!--             <span class="white&#45;&#45;text text-h5">{{ people.name[0] }}</span>-->
                    <v-img :src="getIdenticon(people.peopleName, 48, 'user')"></v-img>
                  </v-avatar>
                </v-list-item-avatar>
                <v-list-item-content>
                  <v-list-item-title>
                    {{ people.peopleName }}
                  </v-list-item-title>
                  <v-list-item-subtitle>
                    {{ people.peopleEmail }}
                  </v-list-item-subtitle>
                </v-list-item-content>
                <v-list-item-action>
                  <span v-if="user.id === people.peopleId"></span>
                  <v-checkbox v-else :input-value="active" color="deep-purple accent-4"></v-checkbox>
                </v-list-item-action>
              </template>
            </v-list-item>
          </v-list-item-group>
        </v-list>
      </v-card-text>

      <v-divider style="width: 900px;"></v-divider>

      <v-card-text style="position: relative;top:2%">
        <v-text-field v-model="searchNot" label="请输入用户名称进行查找"
          style="position:absolute;right:10%;top:-40%;height:100%;width: 25%;"></v-text-field>
        <v-row no-gutters>
          <v-col md="2">
            <h3>没有权限的用户</h3>
          </v-col>
          <v-spacer></v-spacer>
          <v-col md="2" style="position: relative;">
            <v-icon style="position: absolute;right:15.5%;" @click="addPerson">mdi-plus-box-outline</v-icon>
          </v-col>
        </v-row>
        <!-- <p class="ml-s" style="font-size: medium;">添加具有权限修改的用户</p> -->
        <v-list shaped max-height="5">
          <v-list-item-group v-model="addGroup" multiple color="indigo" active-class="deep-purple--text text--accent-4">
            <v-list-item v-for="people in filter(peopleCanNotWrite, searchNot)" :key="people.peopleId">
              <template v-slot:default="{ active }">
                <v-list-item-avatar>
                  <v-avatar active-class="deep-purple--text text--accent-4" color="indigo">
                    <!--             <span class="white&#45;&#45;text text-h5">{{ people.name[0] }}</span>-->
                    <v-img :src="getIdenticon(people.peopleName, 48, 'user')"></v-img>
                  </v-avatar>
                </v-list-item-avatar>
                <v-list-item-content>
                  <v-list-item-title>
                    {{ people.peopleName }}
                  </v-list-item-title>
                  <v-list-item-subtitle>
                    {{ people.peopleEmail }}
                  </v-list-item-subtitle>
                </v-list-item-content>
                <v-list-item-action>
                  <v-checkbox :input-value="active" color="deep-purple accent-4"></v-checkbox>
                </v-list-item-action>
              </template>
            </v-list-item>
          </v-list-item-group>
        </v-list>
      </v-card-text>
      <v-card-actions class="justify-end" style="position: absolute;bottom: 0;right: 0;">
        <v-btn text color="primary" width="70px" style="float: right"
          @click="editDialog2 = false; editDialog1 = true;">返回</v-btn>
        <v-btn text :color="getTopicColor(user.topic)" width="70px" style="float: right"
          @click="editDialog2 = false; editDialog1 = false; edit()">确认</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <v-dialog v-model="dialog3">
    <v-card>
      <v-card-title>{{ doc.name }}</v-card-title>
      <v-card-subtitle>{{ doc.outline === '' ? '暂无简介' : doc.outline }}</v-card-subtitle>
      <v-card-text>
        <v-md-editor v-model="textList[doc.id]" height="400px" left-toolbar="undo redo | image" :disabled-menus="[]"
          @upload-image="handleUploadImage" @save="save()" @blur="blur()"></v-md-editor>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn :color="getDarkColor(user.topic)" text @click="save()">保存</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
  </div>
</template>

<script>
import {
  showPersonList, userDocList, userCollectDocList, addDocToCollect, delDocFromCollect, userCreateDoc,
  userEditDocOther, userDelDoc, userEditDocContent, userReleaseDocLock, userGetDocLock, isDocLocked
} from "@/api/user"
import getIdenticon from "@/utils/identicon";
import topicSetting from "@/utils/topic-setting";
import Cookies from "js-cookie"

export default {
  inject: {
    'user': { defualt: null },
    'selectedProj': { defualt: null },
  },
  data() {
    return {
      isCollect: false,
      doc: '',
      textList: {},
      expanded: [],
      addGroup: [1],
      deleteGroup: [1],
      deleteFlag: false,
      search: '',
      searchFile: '',
      dialog1: false,
      dialog2: false,
      editDialog1: false,
      editDialog2: false,
      dialog3: false,
      value: '',
      tab: '',
      searchNot: '',
      isCollectArr: [],
      item: [],
      headers: [
        {
          text: "名称",
          align: "start",
          sortable: false,
          value: "name",
        },
        { text: "所有者", value: "ownerName", sortable: false },
        { text: "最近更改时间", value: "updateTime" },
        { text: "", value: "collect", sortable: false },
      ],
      html: "",
      blogInfo: {
        blogMdContent: '',
        blogContent: ''
      },
      documentData: [
        {
          'documentId': '1',
          'documentName': '共享文档1',
          'format': 'latex',
          'owner': 'szx',
          'limit': 'can write',
          'changeTime': '2023-5-14',
          'collect': false,
          'intro': "blalalala"
        },
        {
          'documentId': '2',
          'documentName': '共享文档2',
          'format': 'latex',
          'owner': 'szx',
          'limit': 'only read',
          'changeTime': '2023-5-14',
          'collect': false,
          'intro': "blalalala"
        },
        {
          'documentId': '3',
          'documentName': '共享文档3',
          'format': 'latex',
          'owner': 'szx',
          'limit': 'only read',
          'changeTime': '2023-5-14',
          'collect': false,
          'intro': "blalalala"
        }
      ],
      peopleCanWrite: [
        {
          'name': 'szx',
          'id': 1,
          'email': '123'
        },
        {
          'name': 'ghy',
          'id': 2,
          'email': '123'
        },
      ],
      peopleCanNotWrite: [
        {
          'name': 'lr',
          'id': 3,
          'email': '123'
        },
        {
          'name': 'zhy',
          'id': 4,
          'email': '123'
        },
      ],
      allPeople: [],
      newDocumentForm: {
        name: '',
        intro: '',
        people: [],
      },
      editDocumentForm: {
        name: '',
        intro: '',
        people: [],
        id: "",
      },
      toolbars: {
        bold: true, // 粗体
        italic: true, // 斜体
        header: true, // 标题
        underline: true, // 下划线
        strikethrough: true, // 中划线
        mark: true, // 标记
        superscript: true, // 上角标
        subscript: true, // 下角标
        quote: true, // 引用
        ol: true, // 有序列表
        ul: true, // 无序列表
        link: true, // 链接
        imagelink: true, // 图片链接
        code: false, // code
        table: true, // 表格
        fullscreen: true, // 全屏编辑
        readmodel: true, // 沉浸式阅读
        htmlcode: true, // 展示html源码
        help: true, // 帮助
        /* 1.3.5 */
        undo: true, // 上一步
        redo: true, // 下一步
        trash: true, // 清空
        save: true, // 保存（触发events中的save事件）
        /* 1.4.2 */
        navigation: true, // 导航目录
        /* 2.1.8 */
        alignleft: true, // 左对齐
        aligncenter: true, // 居中
        alignright: true, // 右对齐
        /* 2.2.1 */
        subfield: true, // 单双栏模式
        preview: true, // 预览
      },
      collectDocList: []
    }
  },
  created() {
    this.getDocumentData();
    showPersonList({ projectId: this.selectedProj.projectId, userId: this.user.id }).then(
      res => {
        console.log(res);
        this.allPeople = res['data']['data'];
        console.log("allPeople");
        console.log(this.allPeople);
      }
    );
    userCollectDocList({ userId: this.user.id, projectId: this.selectedProj.projectId }).then(
      res => {
        console.log("userCollectDocList");
        console.log(res);
        this.collectDocList = res['data']['data'];
      }
    );
  },
  methods: {
    getIdenticon,
    blur() {
      console.log("123");
    },
    edit() {
      let arr = [];
      for (let i = 0; i < this.peopleCanWrite.length; i++) {
        arr.push(this.peopleCanWrite[i].peopleId);
      }
      console.log("edit");
      console.log(arr);
      userEditDocOther({
        userId: this.user.id, projectId: this.selectedProj.projectId, docId: this.editDocumentForm.id,
        name: this.editDocumentForm.name, accessUserId: arr
      }).then(
        res => {
          console.log("userEditDocOther");
          console.log(res);
          this.getDocumentData();
        }
      )
    },
    openMd(item) {
      this.doc = item;
      let lock = false;
      isDocLocked({ docId: item.id }).then(
        res => {
          console.log("isDocLocked");
          console.log(res);
          lock = res['data']['isLocked'];
          if (lock) {
            this.$message({
              type: 'error',
              message: '该文档正在被编辑！'
            })
          } else {
            Cookies.set('doc', JSON.stringify(this.doc));
            userGetDocLock({ userId: this.user.id, projectId: this.selectedProj.projectId, docId: item.id }).then(
              res => {
                console.log("userGetDocLock");
                console.log(res);
                this.getDocumentData();
                this.dialog3 = true;
              }
            )
          }
        }
      )
    },
    gotoCollect() {
      this.isCollect = true;
      this.getCollectList();
    },
    gotoAll() {
      this.isCollect = false;
      this.getDocumentData();
    },
    checkNameIntro() {
      console.log("check");
      if (this.newDocumentForm.name.trim() === "") {
        this.$message({
          type: "error",
          message: "共享文档名称不能为空！",
        });
      } else {
        for (let i = 0; i < this.documentData.length; i++) {
          if (this.documentData[i].name.trim() === this.newDocumentForm.name.trim()) {
            this.$message({
              type: 'error',
              message: '已存在同名文档！'
            })
            return;
          }
        }
        this.dialog1 = false; this.dialog2 = true;
      }
    },
    initEditPeople(item) {
      this.deleteGroup = [];
      this.addGroup = [];
      this.peopleCanWrite = [];
      this.peopleCanNotWrite = [];
      console.log("initEditPeople");
      console.log(this.allPeople);
      for (let i = 0; i < this.allPeople.length; i++) {
        let flag = false;
        for (let j = 0; j < this.item.accessUser.length; j++) {
          if (this.item.accessUser[j].id === this.allPeople[i].peopleId) {
            flag = true;
            break;
          }
        }
        if (flag) {
          this.peopleCanWrite.push(this.allPeople[i]);
        } else {
          this.peopleCanNotWrite.push(this.allPeople[i]);
        }
      }
      console.log(this.peopleCanNotWrite);
      console.log(this.peopleCanWrite);
      this.editDialog2 = true;
    },
    initPeople() {
      this.deleteGroup = [];
      this.addGroup = [];
      this.peopleCanWrite = [];
      this.peopleCanNotWrite = [];
      console.log("initPeople");
      console.log(this.allPeople);
      for (let i = 0; i < this.allPeople.length; i++) {
        if (this.allPeople[i].peopleId !== this.user.id) {
          this.peopleCanNotWrite.push(this.allPeople[i]);
        } else {
          this.peopleCanWrite.push(this.allPeople[i]);
        }
      }
      console.log(this.peopleCanNotWrite);
      console.log(this.peopleCanWrite);
    },
    getCollectList() {
      userCollectDocList({ userId: this.user.id, projectId: this.selectedProj.projectId }).then(
        res => {
          console.log("userCollectDocLis");
          console.log(res);
          this.collectDocList = res['data']['data'];
          console.log(this.collectDocList);
          console.log("finishGetCollectList");
          console.log(this.collectDocList);
          this.documentData = this.collectDocList;
        }
      )
    },
    isInCollect(item) {
      if (this.collectDocList === undefined) {
        return false;
      }
      for (let i = 0; i < this.collectDocList.length; i++) {
        if (this.collectDocList[i].id === item.id) {
          return true;
        }
      }
      return false;
    },
    delPerson() {
      console.log(this.deleteGroup);
      for (let i = 0; i < this.deleteGroup.length; i++) {
        this.peopleCanNotWrite.push(this.peopleCanWrite[this.deleteGroup[i]]);
      }
      let arr = [];
      for (let i = 0; i < this.peopleCanWrite.length; i++) {
        if (this.deleteGroup.indexOf(i) == -1) {
          arr.push(this.peopleCanWrite[i]);
        }
      }
      this.peopleCanWrite = arr;
    },
    addDoc() {
      let accessUserId = [];
      console.log(this.peopleCanWrite);
      for (let i = 0; i < this.peopleCanWrite.length; i++) {
        accessUserId.push(this.peopleCanWrite[i].peopleId);
      }
      userCreateDoc({
        userId: this.user.id, projectId: this.selectedProj.projectId, name: this.newDocumentForm.name,
        outline: this.newDocumentForm.intro, content: "", accessUserId: accessUserId
      }).then(
        res => {
          console.log(res);
          this.getDocumentData();
        }
      )
    },
    addCollect(item) {
      console.log("123");
      addDocToCollect({ userId: this.user.id, projectId: this.selectedProj.projectId, docId: item.id }).then(
        res => {
          console.log("addDocToCollect");
          console.log(res);
          this.getDocumentData();
        }
      )
    },
    cancelCollect(item) {
      delDocFromCollect({ userId: this.user.id, projectId: this.selectedProj.projectId, docId: item.id }).then(
        res => {
          console.log(res);
          if (this.isCollect) {
            this.getCollectList();
          } else {
            this.getDocumentData();
          }
        }
      )
    },
    addPerson() {
      console.log(this.addGroup);
      for (let i = 0; i < this.addGroup.length; i++) {
        this.peopleCanWrite.push(this.peopleCanNotWrite[this.addGroup[i]]);
      }
      let arr = [];
      for (let i = 0; i < this.peopleCanNotWrite.length; i++) {
        if (this.addGroup.indexOf(i) == -1) {
          arr.push(this.peopleCanNotWrite[i]);
        }
      }
      this.peopleCanNotWrite = arr;
    },
    getDocumentData() {
      userDocList({ userId: this.user.id, projectId: this.selectedProj.projectId }).then(
        res => {
          console.log("getDocumentData");
          console.log(res);
          this.documentData = res['data']['data'];
          console.log(this.documentData);
          for (let i = 0; i < this.documentData.length; i++) {
            this.textList[this.documentData[i].id] = this.documentData[i].content;
          }
        }
      )
    },
    editStart(item) {
      this.editDocumentForm.name = item.name;
      this.editDocumentForm.intro = item.outline;
      this.editDocumentForm.people = item.accessUser;
      this.editDocumentForm.id = item.id;
      this.dialog3 = false;
      this.editDialog1 = true;
      this.item = item;
    },
    save() {
      let accessUserId = [];
      for (let key in this.doc.accessUser) {
        accessUserId.push(key);
      }
      userEditDocContent({
        userId: this.user.id, projectId: this.selectedProj.projectId, docId: this.doc.id,
        content: this.textList[this.doc.id]
      }).then(
        res => {
          console.log("userEditDocContent");
          console.log(res);
          this.getDocumentData();
          this.$message({
            type: "success",
            message: "保存成功!",
          });
        }
      )
    },
    handleDelete(row) {
      userDelDoc({ userId: this.user.id, projectId: this.selectedProj.projectId, docId: row.id }).then(
        res => {
          console.log("userDelDoc");
          console.log(res);
          this.getDocumentData();
          this.open();
        }
      )
      this.$message({
        type: "success",
        message: "删除成功!",
      });
    },
    filter(arr, search) {
      if (search === '') {
        return arr;
      }
      let res = [];
      for (let i = 0; i < arr.length; i++) {
        if (arr[i].peopleName.indexOf(search) != -1) {
          res.push(arr[i]);
        }
      }
      return res;
    },
    close() {
      console.log('21312313213213212313213')
      this.$emit('close');
    },
    open() {
      this.$emit('open');
    },
    closeDialog() {
      console.log("closeDialog");
      this.dialog1 = false;
      this.dialog2 = false;
    },
    filterOnlyCapsText(value, search, item) {
      console.log(value);
      var s = item["documentName"];
      return (
        s != null &&
        search != null &&
        typeof s === "string" &&
        s.toString().toLocaleUpperCase().indexOf(search.toLocaleUpperCase()) !==
        -1
      );
    },
    //监听markdown变化
    change(value, render) {
      this.html = render;
      this.blogInfo.blogMdContent = value;
      this.blogInfo.blogContent = render;
    },
    //上传图片接口pos 表示第几个图片 
    handleUploadImage(event, insertImage, files) {
      for (let i in files) {
        const formData = new FormData();
        formData.append('file', files[i]);
        proxy.$axios.post(`${proxy.PATH}/uploadImg`, formData).then(
          response => {
            insertImage({
              url: response.data,
              desc: 'DESC',
            })
          },
          error => {
            console.log('请求失败了', error.message)
          }
        )
      }
    },
    handleEditorImgDel() {
      console.log('handleEditorImgDel');    //我这里没做什么操作，后续我要写上接口，从七牛云CDN删除相应的图片
    },
    getTopicColor: topicSetting.getColor,
    getDarkColor: topicSetting.getDarkColor,
    getLinearGradient: topicSetting.getLinearGradient,
    getRadialGradient: topicSetting.getRadialGradient,
    getUrl: topicSetting.getUrl
  },
  watch: {
    dialog3: {
      handler(newVal, oldVal) {
        if (newVal == false) {
          let doc = Cookies.get("doc");
          if (doc !== undefined) {
            doc = JSON.parse(doc);
            userReleaseDocLock({ userId: this.user.id, projectId: this.selectedProj.projectId, docId: doc.id }).then(
              res => {
                console.log("userReleaseDocLock");
                console.log(res);
              }
            )
            Cookies.set('doc', undefined);
          }
        }
      }
    }
  }
}
</script>
