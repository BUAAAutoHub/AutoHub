# Provide 定义：App.vue 会提供什么样的属性供子部件获取：

## user 属性

首先包括用户的id, name, email

然后包括用户加入的项目：是一个数组，每个元素分别有id和name属性

```json
{
    "id": 1,
    "name": "TrickEye",
    "email": "trickeye@buaa.edu.cn",
    "projects": [{
      "id": 1,
      "name": "Project1"
    }, {
      "id": 2,
      "name": "Project2"
    }]
}
```

## selectedProj 属性

主要是在具体某一项目中会提供，其他场合下为 null

```json
{
  "id": 1,
  "name": "Project1"
}
```