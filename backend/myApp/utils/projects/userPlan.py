import json
import datetime

from django.http import JsonResponse
from django.utils import timezone
from django.views import View
from django.db.models import Q
from myApp.models import *
from myApp.utils.projects.userdevelop import genResponseStateInfo
from myApp.utils.projects.userChat import delete_user_from_groups

validTaskLabel = ["A", "B", "C", "D", "E"]
validTaskLabelContent = ["BUG", "ENHANCEMENT", "FEATURE", "DUPLICATE", "QUESTION"]

Label_Content_KV = {"BUG": "A", "ENHANCEMENT": "B", "FEATURE": "C", "DUPLICATE": "D", "QUESTION": "E"}


# --------------------project level--------------------
def getLabelName(label):
    label_dict = dict(Task.LABEL_LIST)
    if label not in validTaskLabel:
        return "None"
    else:
        return label_dict[label]


def canManage(userId, projectId):
    try:
        user = User.objects.get(id=userId)
        project = Project.objects.get(id=projectId)
        print("**********", userId, project.manager_id_id)
        if project.manager_id == user:
            print("heeee")
            return True
        if user.auth == 3:
            return True
        if user.auth == 2 and len(AssistantProject.objects.filter(assistant_id=userId, project_id=projectId)) != 0:
            return True
        return False
    except:
        return False


class newProject(View):
    def post(self, request):
        response = {"message": "404 not success", "errcode": 1}

        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)

        projectName = kwargs.get("projectName")
        projectIntro = kwargs.get("projectIntro")

        project = Project.objects.create(name=projectName, outline=projectIntro, manager_id=request.user, status="B")
        project.save()

        UserProject.objects.create(user_id=request.user, project_id=project, role=UserProject.DEVELOPER)
        response["errcode"] = 0
        response["message"] = "success"
        return JsonResponse(response)


class watchAllProject(View):
    def post(self, request):
        response = {"errcode": 1, "message": "404 not success"}
        userProjectRepo = UserProject.objects.filter(user_id=request.user)
        projectList = []
        for i in userProjectRepo:
            projectList.append(
                {
                    "projectId": i.project_id.id,
                    "projectName": i.project_id.name,
                    "projectIntro": i.project_id.outline,
                    "state": i.project_id.status,
                    "deadline": str(i.project_id.create_time.year)
                    + "-"
                    + str(i.project_id.create_time.month)
                    + "-"
                    + str(i.project_id.create_time.day),
                    "managerId": i.project_id.manager_id.id,
                    "managerName": i.project_id.manager_id.name,
                    "access": i.project_id.access,
                }
            )
        response["errcode"] = 0
        response["message"] = "success"
        response["data"] = projectList
        return JsonResponse(response)


class deleteProject(View):
    def post(self, request):
        response = {"errcode": 1, "message": "404 not success"}

        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)

        projectId = kwargs.get("projectId", -1)
        if Project.objects.filter(id=projectId).count() == 0:
            response["errcode"] = 1
            response["message"] = "project not exist"
            response["data"] = None
            return JsonResponse(response)

        tasks = Task.objects.filter(project_id=projectId)
        tasks.delete()
        Project.objects.filter(id=projectId).delete()
        response["errcode"] = 0
        response["message"] = "success"
        response["data"] = None
        return JsonResponse(response)


class modifyProject(View):
    def post(self, request):
        response = {"errcode": 1, "message": "404 not success"}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)

        projectId = kwargs.get("projectId", -1)
        if Project.objects.filter(id=projectId).count() == 0:
            response["errcode"] = 1
            response["message"] = "project not exist"
            response["data"] = None
            return JsonResponse(response)

        projectName = kwargs.get("projectName", "")
        if projectName != "":
            project = Project.objects.get(id=projectId)
            project.name = projectName
            project.save()

        projectOutline = kwargs.get("projectIntro", "")
        if projectOutline != "":
            project = Project.objects.get(id=projectId)
            project.outline = projectOutline
            project.save()

        response["errcode"] = 0
        response["message"] = "success"
        response["data"] = None
        return JsonResponse(response)


class modifyProjectStatus(View):
    def post(self, request):
        response = {"errcode": 1, "message": "404 not success"}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)

        projectId = kwargs.get("projectId", -1)
        status = kwargs.get("status", "")
        if Project.objects.filter(id=projectId).count() == 0:
            response["errcode"] = 1
            response["message"] = "project not exist"
            response["data"] = None
            return JsonResponse(response)

        project = Project.objects.get(id=projectId)
        project.status = status
        project.save()

        response["errcode"] = 0
        response["message"] = "success"
        response["data"] = None
        return JsonResponse(response)


# ----------------------task level----------------------


class addTask(View):
    def post(self, request):
        response = {"errcode": 1, "message": "404 not success"}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)

        name = kwargs.get("taskName", "")
        projectId = kwargs.get("projectId", 0)
        outline = kwargs.get("outlinte", "")
        if Project.objects.filter(id=projectId).count() == 0:
            response["errcode"] = 1
            response["message"] = "project not exist"
            response["data"] = None
            return JsonResponse(response)

        if UserProject.objects.filter(user_id=request.user, project_id=projectId, role=UserProject.NORMAL).count() > 0:
            response["errcode"] = 3
            response["message"] = "permission denied"
            response["data"] = None
            return JsonResponse(response)

        project = Project.objects.get(id=projectId)
        deadline = datetime.datetime(year=2030, month=12, day=31)
        task = Task.objects.create(name=name, project_id=project, deadline=deadline)
        task.status = Task.NOTSTART
        task.order = task.id
        task.outline = outline
        task.save()

        response["errcode"] = 0
        response["message"] = "success"
        response["data"] = name
        return JsonResponse(response)


class addSubTask(View):
    def post(self, request):
        response = {"errcode": 1, "message": "404 not success"}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)

        time = kwargs.get("deadline", "")
        year, month, day = time.split("-")
        year = int(year)
        month = int(month)
        day = int(day)
        contribute = kwargs.get("contribute", 0)
        name = kwargs.get("subTaskName", "")
        projectId = kwargs.get("projectId", -1)
        belongTask = kwargs.get("fatherTaskId", -1)
        managerId = kwargs.get("managerId", -1)
        label = kwargs.get("subTaskLabel", None)
        outline = kwargs.get("outline", "")

        t = kwargs.get("start_time", "")
        y, m, d = t.split("-")
        y = int(y)
        m = int(m)
        d = int(d)
        print(" ***A**AS*D*A*S*DSA**DS :", label)
        if Project.objects.filter(id=projectId).count() == 0:
            response["errcode"] = 1
            response["message"] = "project not exist"
            response["data"] = None
            return JsonResponse(response)
        if Task.objects.filter(id=belongTask).count() == 0:
            response["errcode"] = 1
            response["message"] = "task not exist"
            response["data"] = None
            return JsonResponse(response)
        if User.objects.filter(id=managerId).count() == 0:
            response["errcode"] = 1
            response["message"] = "user not exist"
            response["data"] = None
            return JsonResponse(response)
        if UserProject.objects.filter(user_id=request.user, project_id=projectId, role=UserProject.NORMAL).count() > 0:
            response["errcode"] = 3
            response["message"] = "permission denied"
            response["data"] = None
            return JsonResponse(response)
        if label not in validTaskLabelContent and not (label is None or len(label) == 0):
            response["errcode"] = 4
            response["message"] = "wrong Label"
            response["data"] = None
            return JsonResponse(response)
        # use time[0] as year time[1] as month time[2] as day
        deadline = datetime.datetime(year=year, month=month, day=day)
        startTime = datetime.datetime(year=y, month=m, day=d)
        task = Task.objects.create(
            name=name,
            deadline=deadline,
            contribute_level=contribute,
            project_id_id=projectId,
            parent_id_id=belongTask,
            start_time=startTime,
            task_label=Label_Content_KV[label],
            outline=outline,
        )
        task.status = Task.NOTSTART
        task.save()

        UserTask.objects.create(user_id_id=managerId, task_id=task)
        project = Project.objects.get(id=projectId)
        content = f'您有新任务"{task.name}"。该任务属于项目"{project.name}"'
        msg = Notice.objects.create(receiver_id=User.objects.get(id=managerId), read=Notice.N, content=content)
        msg.save()

        response["errcode"] = 0
        response["message"] = "success"
        response["data"] = None
        return JsonResponse(response)


class showTaskList(View):
    def post(self, request):
        response = {"errcode": 1, "message": "404 not success"}

        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)

        projectId = kwargs.get("projectId", -1)
        if Project.objects.filter(id=projectId).count() == 0:
            response["errcode"] = 1
            response["message"] = "project not exist"
            response["data"] = None
            return JsonResponse(response)

        taskList = Task.objects.filter(project_id_id=projectId, parent_id=None).order_by("order")
        data = []
        cur_time = timezone.now()
        for i in taskList:
            tmp = {"taskName": i.name, "taskId": i.id}
            subTasks = Task.objects.filter(parent_id=i)
            subTaskList = []
            for j in subTasks:
                sub_tmp = {
                    "deadline": j.deadline,
                    "contribute": j.contribute_level,
                    "intro": j.outline,
                    "managerId": UserTask.objects.get(task_id=j).user_id_id,
                    "managerName": UserTask.objects.get(task_id=j).user_id.name,
                    "subTaskName": j.name,
                    "subTaskId": j.id,
                    "start_time": j.start_time,
                    "complete_time": j.complete_time,
                    "subTaskLabel": getLabelName(j.task_label),
                    "subTaskOutline": j.outline,
                }

                if j.status != Task.COMPLETED:
                    if cur_time > j.deadline:
                        sub_tmp["status"] = "E"  # 延期未完成
                    elif cur_time < j.start_time:
                        sub_tmp["status"] = "C"  # 未开始
                    else:
                        sub_tmp["status"] = "B"  # 进行中
                else:
                    if j.complete_time > j.deadline:
                        sub_tmp["status"] = "D"  # 延期完成
                    else:
                        sub_tmp["status"] = "A"  # 按时完成

                subTaskList.append(sub_tmp)
            tmp["subTaskList"] = subTaskList
            data.append(tmp)
        response["errcode"] = 0
        response["message"] = "success"
        response["data"] = data
        return JsonResponse(response)


class modifyTaskContent(View):
    def post(self, request):
        response = {"errcode": 1, "message": "404 not success"}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)

        taskId = kwargs.get("taskId", -1)

        deadline = kwargs.get("deadline", "")
        year, month, day = deadline.split("-")
        year = int(year)
        month = int(month)
        day = int(day)
        contribute = kwargs.get("contribute", 0)
        taskName = kwargs.get("taskName", "")
        managerId = kwargs.get("managerId", -1)
        startTime = kwargs.get("start_time", "")
        label = kwargs.get("label", None)
        outline = kwargs.get("outline", "")
        y, m, d = startTime.split("-")
        y = int(y)
        m = int(m)
        d = int(d)

        if Task.objects.filter(id=taskId).count() == 0:
            response["errcode"] = 1
            response["message"] = "task not exist"
            response["data"] = None
            return JsonResponse(response)
        task = Task.objects.get(id=taskId)

        projectId = task.project_id_id
        if UserProject.objects.filter(user_id=request.user, project_id=projectId, role=UserProject.NORMAL).count() > 0:
            response["errcode"] = 3
            response["message"] = "permission denied"
            response["data"] = None
            return JsonResponse(response)

        task.deadline = datetime.datetime(year=year, month=month, day=day)
        task.start_time = datetime.datetime(year=y, month=m, day=d)
        task.contribute_level = contribute
        task.name = taskName
        task.outline = outline
        try:
            index = validTaskLabelContent.index(label)
            task.task_label = Task.LABEL_LIST[index][0]
            task.save()
            print(label, index, Task.LABEL_LIST[index][0])
        except ValueError:
            task.label = None
            task.save()
            print("元素 '{}' 不存在于label列表中".format(label))
        UserTask.objects.filter(task_id=task).delete()
        UserTask.objects.create(user_id_id=managerId, task_id=task)

        response["errcode"] = 0
        response["message"] = "success"
        response["data"] = None
        return JsonResponse(response)


class completeTask(View):
    def post(self, request):
        response = {"errcode": -1, "message": "404 not success"}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        userId = kwargs.get("userId", -1)
        projectId = kwargs.get("projectId", -1)
        taskId = kwargs.get("taskId", -1)
        if Task.objects.filter(id=taskId).count() == 0:
            response["errcode"] = 1
            response["message"] = "task not exist"
            response["data"] = None
            return JsonResponse(response)
        if not User.objects.filter(id=userId).exists():
            response["errcode"] = 2
            response["message"] = "user not exist"
            response["data"] = None
            return JsonResponse(response)

        task = Task.objects.get(id=taskId)
        if UserProject.objects.filter(user_id=userId, project_id=projectId, role=UserProject.NORMAL).count() > 0:
            response["errcode"] = 3
            response["message"] = "permission denied"
            response["data"] = None
            return JsonResponse(response)

        intro = kwargs.get("intro", "")

        task.status = Task.COMPLETED
        task.outline = intro
        task.complete_time = datetime.datetime.now()
        task.save()

        subtasks = Task.objects.filter(parent_id=taskId)
        for i in subtasks:
            i.status = Task.COMPLETED
            i.save()
        UserProjectActivity.objects.create(
            user_id=request.user, project_id=Project.objects.get(id=projectId), option=UserProjectActivity.FINISH_TASK
        )
        response["errcode"] = 0
        response["message"] = "success"
        response["data"] = None
        return JsonResponse(response)


class watchMyTask(View):
    def post(self, request):
        response = {"errcode": 1, "message": "404 not success"}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)

        projectId = kwargs.get("projectId", -1)
        if Project.objects.filter(id=projectId).count() == 0:
            response["errcode"] = 1
            response["message"] = "project not exist"
            response["data"] = None
            return JsonResponse(response)

        taskList = Task.objects.filter(project_id_id=projectId, parent_id=None).order_by("order")
        cur_time = timezone.now()
        data = []
        for i in taskList:
            tmp = {"taskName": i.name, "taskId": i.id}
            subTasks = UserTask.objects.filter(user_id=request.user, task_id__parent_id=i)
            subTaskList = []
            for subtask in subTasks:
                j = Task.objects.get(id=subtask.task_id_id)
                sub_tmp = {
                    "deadline": j.deadline,
                    "contribute": j.contribute_level,
                    "intro": j.outline,
                    "managerId": UserTask.objects.get(task_id=j).user_id_id,
                    "subTaskName": j.name,
                    "subTaskId": j.id,
                    "start_time": j.start_time,
                    "subTaskLabel": getLabelName(j.task_label),
                    "complete_time": j.complete_time,
                }

                if j.status != Task.COMPLETED:
                    if cur_time > j.deadline:
                        sub_tmp["status"] = "E"  # 延期未完成
                    elif cur_time < j.start_time:
                        sub_tmp["status"] = "C"  # 未开始
                    else:
                        sub_tmp["status"] = "B"  # 进行中
                else:
                    if j.complete_time > j.deadline:
                        sub_tmp["status"] = "D"  # 延期完成
                    else:
                        sub_tmp["status"] = "A"  # 按时完成

                subTaskList.append(sub_tmp)
            tmp["subTaskList"] = subTaskList
            data.append(tmp)

        response["errcode"] = 0
        response["message"] = "success"
        response["data"] = data
        return JsonResponse(response)


class removeTask(View):
    def post(self, request):
        response = {"errcode": 1, "message": "404 not success"}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)

        taskId = kwargs.get("taskId", -1)
        if Task.objects.filter(id=taskId).count() == 0:
            response["errcode"] = 1
            response["message"] = "task not exist"
            response["data"] = None
            return JsonResponse(response)

        task = Task.objects.get(id=taskId)
        projectId = task.project_id_id
        if UserProject.objects.filter(user_id=request.user, project_id=projectId, role=UserProject.NORMAL).count() > 0:
            response["errcode"] = 3
            response["message"] = "permission denied"
            response["data"] = None
            return JsonResponse(response)
        task.delete()

        subtasks = Task.objects.filter(parent_id=taskId)
        for i in subtasks:
            i.delete()

        response["errcode"] = 0
        response["message"] = "success"
        response["data"] = None
        return JsonResponse(response)


class getTaskReviews(View):
    def post(self, request):
        response = {"errcode": 1, "message": "404 not success"}

        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)

        taskId = kwargs.get("taskId", -1)
        if Task.objects.filter(id=taskId).count() == 0:
            response["errcode"] = 1
            response["message"] = "task not exist"
            response["data"] = None
            return JsonResponse(response)

        reviewList = TaskReview.objects.filter(task_id=taskId).order_by("create_time")
        reviews = []
        for i in reviewList:
            review = TaskReview.objects.get(pk=i.id)

            user = review.user_id
            reviews.append(
                {"userId": user.id, "userName": user.name, "content": review.content, "createTime": review.create_time}
            )
        response["errcode"] = 0
        response["message"] = "get task reviews ok"
        response["data"] = {"reviews": reviews}
        return JsonResponse(response)


class reviewTask(View):
    def post(self, request):
        response = {"errcode": 1, "message": "404 not success"}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)

        userId = kwargs.get("userId", -1)
        taskId = kwargs.get("taskId", -1)
        content = kwargs.get("content", -1)

        if Task.objects.filter(id=taskId).count() == 0:
            response["errcode"] = 1
            response["message"] = "task not exist"
            response["data"] = None
            return JsonResponse(response)
        task = Task.objects.get(id=taskId)
        project = task.project_id
        if User.objects.filter(id=userId).count() == 0:
            response["errcode"] = 2
            response["message"] = "user not exist"
            response["data"] = None
            return JsonResponse(response)
        user = User.objects.get(id=userId)
        if UserProject.objects.filter(user_id=user, project_id=project, role=UserProject.NORMAL).count() > 0:
            response["errcode"] = 3
            response["message"] = "permission denied"
            response["data"] = None
            return JsonResponse(response)

        TaskReview.objects.create(task_id=task, content=content, user_id=user, create_time=timezone.now())
        response["errcode"] = 0
        response["message"] = "success review"
        return JsonResponse(response)


# ----------member level---------------------------


class showPersonList(View):
    def post(self, request):
        response = {"errcode": 1, "message": "404 not success"}

        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)

        projectId = kwargs.get("projectId", -1)
        if Project.objects.filter(id=projectId).count() == 0:
            response["errcode"] = 1
            response["message"] = "project not exist"
            response["data"] = None
            return JsonResponse(response)

        personList = UserProject.objects.filter(project_id_id=projectId)
        res = []
        for person in personList:
            res.append(
                {
                    "peopleId": person.user_id.id,
                    "peopleName": person.user_id.name,
                    "peopleJob": person.role,
                    "peopleEmail": person.user_id.email,
                }
            )

        response["errcode"] = 0
        response["message"] = "success"
        response["data"] = res
        return JsonResponse(response)


class getRole(View):
    def post(self, request):
        response = {"errcode": 1, "message": "404 not success"}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)

        projectId = kwargs.get("projectId", -1)
        if Project.objects.filter(id=projectId).count() == 0:
            response["errcode"] = 1
            response["message"] = "project not exist"
            response["data"] = None
            return JsonResponse(response)
        project = Project.objects.get(id=projectId)
        userId = kwargs.get("userId", -1)
        if User.objects.filter(id=userId).count() == 0:
            response["errcode"] = 1
            response["message"] = "user not exist"
            response["data"] = None
            return JsonResponse(response)
        user = User.objects.get(id=userId)
        if UserProject.objects.filter(project_id=project, user_id=user).count() == 0:
            response["errcode"] = 1
            response["message"] = "user not in project"
            response["data"] = None
            return JsonResponse(response)
        up = UserProject.objects.get(user_id=user, project_id=project)
        response["errcode"] = 0
        response["message"] = "success"
        response["role"] = up.role
        return JsonResponse(response)


class modifyRole(View):
    def post(self, request):
        response = {"errcode": 1, "message": "404 not success"}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)

        projectId = kwargs.get("projectId", -1)
        if Project.objects.filter(id=projectId).count() == 0:
            response["errcode"] = 1
            response["message"] = "project not exist"
            response["data"] = None
            return JsonResponse(response)

        peopleId = kwargs.get("personId", -1)
        if User.objects.filter(id=peopleId).count() == 0:
            response["errcode"] = 1
            response["message"] = "user not exist"
            response["data"] = None
            return JsonResponse(response)

        role = kwargs.get("role", "")
        if role not in [UserProject.ADMIN, UserProject.NORMAL, UserProject.DEVELOPER, UserProject.REVIEWER]:
            response["errcode"] = 1
            response["message"] = "role not exist"
            response["data"] = None
            return JsonResponse(response)

        if (
            UserProject.objects.filter(
                Q(role=UserProject.ADMIN) | Q(role=UserProject.DEVELOPER),
                user_id=request.user,
                project_id_id=projectId,
            ).count()
            == 0
        ):
            response["errcode"] = 3
            response["message"] = "user not admin"
            response["data"] = None
            return JsonResponse(response)

        userProject = UserProject.objects.get(user_id=peopleId, project_id=projectId)
        userProject.role = role
        userProject.save()
        response["errcode"] = 0
        response["message"] = "success"
        response["data"] = None
        return JsonResponse(response)


class addMember(View):
    def post(self, request):
        response = {"errcode": 1, "message": "404 not success"}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)

        projectId = kwargs.get("projectId", -1)
        if Project.objects.filter(id=projectId).count() == 0:
            response["errcode"] = 1
            response["message"] = "project not exist"
            response["data"] = None
            return JsonResponse(response)

        nameOrEmail = kwargs.get("nameOrEmail", "")
        if User.objects.filter(name=nameOrEmail).count() == 0 and User.objects.filter(email=nameOrEmail).count() == 0:
            response["errcode"] = 1
            response["message"] = "user not exist"
            response["data"] = None
            return JsonResponse(response)

        if User.objects.filter(name=nameOrEmail).count() > 0:
            peopleId = User.objects.get(name=nameOrEmail).id
        else:
            peopleId = User.objects.get(email=nameOrEmail).id

        if UserProject.objects.filter(user_id_id=peopleId, project_id_id=projectId).count() != 0:
            response["errcode"] = 2
            response["message"] = "user already in project"
            response["data"] = None
            return JsonResponse(response)

        if (
            UserProject.objects.filter(user_id=request.user, project_id_id=projectId, role=UserProject.NORMAL).count()
            > 0
        ):
            response["errcode"] = 3
            response["message"] = "user not admin"
            response["data"] = None
            return JsonResponse(response)
        personList = UserProject.objects.filter(project_id_id=projectId)
        for person in personList:
            Cooperate.objects.create(user1_id_id=person.user_id.id, user2_id_id=peopleId, project_id_id=projectId)
            Cooperate.objects.create(user1_id_id=peopleId, user2_id_id=peopleId, project_id_id=projectId)
        UserProject.objects.create(user_id_id=peopleId, project_id_id=projectId, role=UserProject.NORMAL)
        response["errcode"] = 0
        response["message"] = "success"
        response["data"] = None
        return JsonResponse(response)


class removeMember(View):
    def post(self, request):
        response = {"errcode": 0, "message": "404 not success"}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)

        projectId = kwargs.get("projectId", -1)
        if Project.objects.filter(id=projectId).count() == 0:
            response["errcode"] = 1
            response["message"] = "project not exist"
            response["data"] = None
            return JsonResponse(response)

        peopleId = kwargs.get("personId", -1)
        if User.objects.filter(id=peopleId).count() == 0:
            response["errcode"] = 1
            response["message"] = "user not exist"
            response["data"] = None
            return JsonResponse(response)

        if UserProject.objects.filter(user_id=peopleId, project_id=projectId).count() == 0:
            response["errcode"] = 1
            response["message"] = "user not in project"
            response["data"] = None
            return JsonResponse(response)

        if (
            UserProject.objects.filter(user_id=request.user, project_id_id=projectId, role=UserProject.NORMAL).count()
            > 0
        ):
            response["errcode"] = 3
            response["message"] = "user not admin"
            response["data"] = None
            return JsonResponse(response)

        a = UserProject.objects.filter(user_id_id=peopleId, project_id_id=projectId)

        # ids=[]
        # for i in a:
        #     ids.append(i.user_id)
        delete_user_from_groups(user_id=int(peopleId), project_id=int(projectId))
        Cooperate.objects.filter(Q(user1_id=peopleId) | Q(user2_id=peopleId), project_id=projectId).delete()

        UserProject.objects.filter(user_id_id=peopleId, project_id_id=projectId).delete()
        UserProjectActivity.objects.filter(user_id_id=peopleId, project_id_id=projectId).delete()
        response["errcode"] = 0
        response["message"] = "success"
        response["data"] = None
        return JsonResponse(response)


class getEmail(View):
    def post(self, request):
        response = {"errcode": 0, "message": "404 not success"}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)

        peopleId = kwargs.get("personId", -1)
        if User.objects.filter(id=peopleId).count() == 0:
            response["errcode"] = 1
            response["message"] = "user not exist"
            return JsonResponse(response)

        user = User.objects.get(id=peopleId)
        email = str(user.email)
        response["errcode"] = 0
        response["message"] = "success"
        response["data"] = email
        return JsonResponse(response)


# -----------------notice level------------------------
class notice(View):
    def post(self, request):
        response = {"errcode": 1, "message": "404 not success"}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)

        taskId = kwargs.get("taskId", -1)
        deadline = kwargs.get("deadline", "")
        if Task.objects.filter(id=taskId).count() == 0:
            response["errcode"] = 1
            response["message"] = "task not exist"
            response["data"] = None
            return JsonResponse(response)
        task = Task.objects.get(id=taskId)
        project = Project.objects.get(id=task.project_id_id)
        user = UserTask.objects.get(task_id=task).user_id
        content = f'您的项目"{project.name}"中的任务"{task.name}"于"{deadline}"到期'
        msg = Notice.objects.create(receiver_id=user, read=Notice.N, content=content)
        msg.save()
        response["errcode"] = 0
        response["message"] = "success"
        response["data"] = None
        return JsonResponse(response)


class showNoticeList(View):
    def post(self, request):
        response = {"errcode": 1, "message": "404 not success"}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)

        userId = kwargs.get("userId")

        if User.objects.filter(id=userId).count() == 0:
            response["errcode"] = 1
            response["message"] = "user not exist"
            response["data"] = None
            return JsonResponse(response)

        noticeList = Notice.objects.filter(receiver_id=userId)
        data = []
        for notice in noticeList:
            sub_tmp = {
                "noticeId": notice.id,
                "content": notice.content,
                "create_time": notice.create_time,
                "read": notice.read,
                "url": notice.url,
            }
            data.append(sub_tmp)

        data.sort(key=lambda x: (x["read"] == Notice.Y, -x["create_time"].timestamp()))
        response["errcode"] = 0
        response["message"] = "success"
        response["data"] = data

        return JsonResponse(response)


class readNotice(View):
    def post(self, request):
        response = {"errcode": 1, "message": "404 not success"}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        noticeId = kwargs.get("noticeId", -1)
        userId = kwargs.get("userId", -1)
        if Notice.objects.filter(id=noticeId, receiver_id=userId).count() == 0:
            response["errcode"] = 1
            response["message"] = "notice not exist"
            response["data"] = None
            return JsonResponse(response)
        notice = Notice.objects.get(id=noticeId)
        notice.read = Notice.Y
        notice.save()

        response["errcode"] = 0
        response["message"] = "success"
        response["data"] = None

        return JsonResponse(response)


class removeNotice(View):
    def post(self, request):
        response = {"errcode": 1, "message": "404 not success"}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        noticeId = kwargs.get("noticeId", -1)
        if Notice.objects.filter(id=noticeId).count() == 0:
            response["errcode"] = 1
            response["message"] = "notice not exist"
            response["data"] = None
            return JsonResponse(response)
        this_notice = Notice.objects.get(id=noticeId)
        this_notice.delete()

        response["errcode"] = 0
        response["message"] = "success"
        response["data"] = None

        return JsonResponse(response)


class test(View):
    def post(self, request):
        response = {"errcode": 0, "message": "404 not success"}
        # try:
        #     kwargs: dict = json.loads(request.body)
        # except Exception:
        #     return JsonResponse(response)
        projects = Project.objects.all()
        ids = []
        for i in projects:
            tmp = {"id": i.id}
            u2p = UserProject.objects.filter(project_id=i.id)
            roles = []
            for j in u2p:
                roles.append(j.role)
            tmp["roles"] = roles
            tmp["status"] = i.status
            ids.append(tmp)

        response["errcode"] = 0
        response["message"] = "success"
        response["data"] = ids
        return JsonResponse(response)


class showContribute(View):
    def post(self, request):
        response = {"errcode": 0, "message": "404 not success"}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)

        projectId = kwargs.get("projectId", -1)
        if Project.objects.filter(id=projectId).count() == 0:
            response["errcode"] = 1
            response["message"] = "project not exist"
            response["data"] = None
            return JsonResponse(response)

        if (
            UserProject.objects.filter(user_id=request.user, project_id_id=projectId, role=UserProject.NORMAL).count()
            > 0
        ):
            response["errcode"] = 3
            response["message"] = "user not admin"
            response["data"] = None
            return JsonResponse(response)

        members = UserProject.objects.filter(project_id_id=projectId)
        ans = {}
        for member in members:
            i = member.user_id
            cb = 0
            tasks = UserTask.objects.filter(user_id=i)
            for task in tasks:
                j = task.task_id
                if j.project_id_id == projectId:
                    cb += j.contribute_level
            ans[i.name] = cb

        response["errcode"] = 0
        response["message"] = "success"
        response["data"] = ans
        return JsonResponse(response)


class changeOrder(View):
    def post(self, request):
        response = {"errcode": 0, "message": "404 not success"}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)

        projectId = kwargs.get("projectId", -1)
        if Project.objects.filter(id=projectId).count() == 0:
            response["errcode"] = 1
            response["message"] = "project not exist"
            response["data"] = None
            return JsonResponse(response)

        task1Id = kwargs.get("task1Id", -1)
        if Project.objects.filter(id=projectId).count() == 0:
            response["errcode"] = 1
            response["message"] = "task1 not exist"
            response["data"] = None
            return JsonResponse(response)

        task2Id = kwargs.get("task2Id", -1)
        if Project.objects.filter(id=projectId).count() == 0:
            response["errcode"] = 1
            response["message"] = "task2 not exist"
            response["data"] = None
            return JsonResponse(response)

        if task1Id == 0 or task2Id == 0:
            response["errcode"] = 0
            response["message"] = "not change"
            return JsonResponse(response)

        task1 = Task.objects.get(id=task1Id)
        task2 = Task.objects.get(id=task2Id)
        order1 = task1.order
        order2 = task2.order
        task1.order = order2
        task2.order = order1
        task1.save()
        task2.save()

        response["errcode"] = 0
        response["message"] = "success"
        return JsonResponse(response)


class ProjectInfo(View):
    def post(self, request):
        response = {"errcode": 0, "message": "404 not success"}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)

        projectId = kwargs.get("projectId", -1)
        if Project.objects.filter(id=projectId).count() == 0:
            response["errcode"] = 1
            response["message"] = "project not exist"
            response["data"] = None
            return JsonResponse(response)

        condition = Q(id=request.user.id) & (Q(auth=User.TEACHER) | Q(auth=User.ASSISTANT))
        if User.objects.filter(condition).count() == 0:
            response["errcode"] = 3
            response["message"] = "user not admin"
            response["data"] = request.user.id
            return JsonResponse(response)

        i = Project.objects.get(id=projectId)
        ans = {
            "projectId": i.id,
            "projectName": i.name,
            "projectIntro": i.outline,
            "state": i.status,
            "deadline": str(i.create_time.year) + "-" + str(i.create_time.month) + "-" + str(i.create_time.day),
            "managerId": i.manager_id.id,
            "managerName": i.manager_id.name,
            "access": i.access,
        }

        response["errcode"] = 0
        response["data"] = ans
        response["message"] = "success"
        return JsonResponse(response)


class getUserProjectAuths(View):
    def post(self, request):
        response = {"errcode": 0, "message": "404 not success"}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)

        response["message"] = "get user project authority ok"
        projectId = kwargs.get("projectId", -1)
        if Project.objects.filter(id=projectId).count() == 0:
            response["errcode"] = 2
            response["message"] = "project not exist"
            response["data"] = None
            return JsonResponse(response)
        project = Project.objects.get(id=projectId)

        personId = kwargs.get("personId", -1)
        if User.objects.filter(id=personId).count() == 0:
            response["errcode"] = 3
            response["message"] = "user not exist"
            response["data"] = None
            return JsonResponse(response)

        userId = kwargs.get("userId", -1)
        if User.objects.filter(id=userId).count() == 0:
            response["errcode"] = 3
            response["message"] = "user not exist"
            response["data"] = None
            return JsonResponse(response)

        userProject = UserProject.objects.filter(user_id=personId, project_id=projectId)
        if len(userProject) == 0:
            response["errcode"] = 4
            response["message"] = "no such user in project"
            response["data"] = None
            return JsonResponse(response)
        userProject = userProject.first()

        if not canManage(userId, projectId):
            response["errcode"] = 1
            response["message"] = "Insufficient authority"
            response["data"] = None
            return JsonResponse(response)

        personProject = UserProject.objects.filter(user_id=personId, project_id=projectId)
        if len(personProject) == 0:
            response["errcode"] = 4
            response["message"] = "no such user in project"
            response["data"] = None
            return JsonResponse(response)
        personProject = personProject.first()

        data = {}
        data["commitAuth"] = personProject.commitAuth
        data["editAuth"] = personProject.editAuth
        data["viewAuth"] = personProject.viewAuth

        response["data"] = data
        return JsonResponse(response)


class changeUserProjectAuths(View):
    def post(self, request):
        response = {"errcode": 0, "message": "404 not success"}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)

        response["message"] = "change user project authority ok"
        projectId = kwargs.get("projectId", -1)
        if Project.objects.filter(id=projectId).count() == 0:
            response["errcode"] = 2
            response["message"] = "project not exist"
            response["data"] = None
            return JsonResponse(response)
        project = Project.objects.get(id=projectId)

        personId = kwargs.get("personId", -1)
        if User.objects.filter(id=personId).count() == 0:
            response["errcode"] = 3
            response["message"] = "user not exist"
            response["data"] = None
            return JsonResponse(response)

        userId = kwargs.get("userId", -1)
        if User.objects.filter(id=userId).count() == 0:
            response["errcode"] = 3
            response["message"] = "user not exist"
            response["data"] = None
            return JsonResponse(response)

        userProject = UserProject.objects.filter(user_id=personId, project_id=projectId)
        if len(userProject) == 0:
            response["errcode"] = 4
            response["message"] = "no such user in project"
            response["data"] = None
            return JsonResponse(response)
        userProject = userProject.first()

        if not canManage(userId, projectId):
            response["errcode"] = 1
            response["message"] = "Insufficient authority"
            response["data"] = None
            return JsonResponse(response)

        personProject = UserProject.objects.filter(user_id=personId, project_id=projectId)
        if len(personProject) == 0:
            response["errcode"] = 4
            response["message"] = "no such user in project"
            response["data"] = None
            return JsonResponse(response)
        personProject = personProject.first()

        changeToCA = kwargs.get("changeToCommitAuth")
        changeToEA = kwargs.get("changeToEditAuth")
        changeToVA = kwargs.get("changeToViewAuth")

        if changeToCA != "Y" and changeToCA != "N":
            response["errcode"] = 5
            response["message"] = "undefined authority"
            response["data"] = None
            return JsonResponse(response)
        if changeToEA != "Y" and changeToEA != "N":
            response["errcode"] = 5
            response["message"] = "undefined authority"
            response["data"] = None
            return JsonResponse(response)
        if changeToVA != "Y" and changeToVA != "N":
            response["errcode"] = 5
            response["message"] = "undefined authority"
            response["data"] = None
            return JsonResponse(response)

        personProject.commitAuth = changeToCA
        personProject.editAuth = changeToEA
        personProject.viewAuth = changeToVA
        personProject.save()

        data = {}
        data["username"] = User.objects.get(id=userId).name

        response["data"] = data
        return JsonResponse(response)


class showCooperate(View):
    def post(self, request):
        response = {"errcode": -1, "message": "404 not success"}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        genResponseStateInfo(response, 0, "get project cooperate ok")
        projectId = kwargs.get("projectId", -1)
        if Project.objects.filter(id=projectId).count() == 0:
            return JsonResponse(genResponseStateInfo(response, 1, "project not exist"))
        data = []
        pairs = Cooperate.objects.filter(project_id=projectId)
        my_set = set()
        for pair in pairs:
            if (pair.user1_id_id, pair.user2_id_id) in my_set or (pair.user2_id_id, pair.user1_id_id) in my_set:
                continue
            my_set.add((pair.user1_id_id, pair.user2_id_id))
            my_set.add((pair.user2_id_id, pair.user1_id_id))
            data.append(
                {
                    "cooperateUser1_id": pair.user1_id_id,
                    "cooperateUser1_name": User.objects.get(id=pair.user1_id_id).name,
                    "cooperateUser2_id": pair.user2_id_id,
                    "cooperateUser2_name": User.objects.get(id=pair.user2_id_id).name,
                    "cooperateRelation": pair.relation,
                }
            )
        response["data"] = data
        return JsonResponse(response)


class showActivity(View):
    def post(self, request):
        response = {"errcode": -1, "message": "404 not success"}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        genResponseStateInfo(response, 0, "get project activity ok")
        projectId = kwargs.get("projectId", -1)
        # begin = kwargs.get("beginDate", -1)
        # end = kwargs.get("endDate", -1)
        if Project.objects.filter(id=projectId).count() == 0:
            return JsonResponse(genResponseStateInfo(response, 1, "project not exist"))
        tmp = UserProjectActivity.objects.filter(project_id=projectId)
        users = {}
        for item in tmp:
            if not item.user_id_id in users:
                users[item.user_id_id] = {"task": 0, "code": 0, "name": item.user_id.name}
            if item.option == UserProjectActivity.COMMIT_CODE:
                users[item.user_id_id]["code"] += 1
            else:
                users[item.user_id_id]["task"] += 1
        data = []
        for user in users:
            data.append(
                {
                    "userName": users[user]["name"],
                    "userId": user,
                    "task": users[user]["task"],
                    "code": users[user]["code"],
                }
            )
        response["data"] = data
        return JsonResponse(response)


class showProjectReviewers(View):
    def post(self, request):
        response = {"errcode": -1, "message": "404 not success"}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        genResponseStateInfo(response, 0, "get project reviewers ok")
        projectId = kwargs.get("projectId", -1)
        userId = kwargs.get("userId", -1)
        if Project.objects.filter(id=projectId).count() == 0:
            response["errcode"] = 1
            response["message"] = "project not exist"
            response["data"] = None
            return JsonResponse(response)

        if User.objects.filter(id=userId).count() == 0:
            response["errcode"] = 1
            response["message"] = "user not exist"
            response["data"] = None
            return JsonResponse(response)

        if (
            UserProject.objects.filter(
                Q(role=UserProject.ADMIN) | Q(role=UserProject.DEVELOPER),
                user_id=User.objects.get(id=userId),
                project_id_id=projectId,
            ).count()
            == 0
        ):
            response["errcode"] = 3
            response["message"] = "user not admin"
            response["data"] = None
            return JsonResponse(response)

        reviewers = UserProject.objects.filter(project_id_id=projectId, role=UserProject.REVIEWER)
        data = []
        for reviewers in reviewers:
            user = reviewers.user_id
            data.append({"userName": user.name, "userId": user.id})
        response["data"] = data
        return JsonResponse(response)
