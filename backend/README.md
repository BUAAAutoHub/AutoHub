# BACKEND

注意：后端项目必须在 Linux 环境下运行。

## 运行后端项目：

重新建立数据库：

- source rebuildsqlist.sh

项目根目录下执行：

- python manage.py runserver

## 更新数据库表
如果更改了数据库表，需要在项目根目录下执行：
- python manage.py makemigrations
- python manage.py migrate

如果数据库提示表已存在或字段已存在错误，请删库并重新建库。

## 数据库 rebuild

目前自定义了 rebuilddb 命令来重置数据库信息，在项目根目录下执行：
-  python manage.py rebuilddb 

时，会先删除数据库所有表中的条目，将所有的自增 id 重置为 1，然后向数据库表中插入一些初始化条目，如 10 个 用户和 10 个项目。

可以自行修改 `myApp/management/commands/rebuilddb.py` 中 `buildDataBase` 函数来初始化数据库信息。

## api 开发
- 在 myApp/<你负责的模块>.py 中添加视图函数
- 在 djangoProject/urls.py 中添加视图函数 url
- 在 apifox中撰写接口文档
- 在 apifox中进行接口测试
- settings.py 中提供了调试打印函数 `DBG`
