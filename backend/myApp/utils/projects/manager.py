import json
import sys
import random

from hashlib import sha256
from django.http import JsonResponse
from django.views import View
from djangoProject.settings import DBG
from myApp.models import User, Project, AssistantProject, UserProject
from myApp.utils.projects.userdevelop import genResponseStateInfo
from myApp.utils.format.request import getResp

validUserStatus     = {"A", "B"}
validAuthority      = { 1 ,  2 ,  3 }
validProjectStatus  = {"A", "B", "C"}
validTaskStatus     = {"A", "B", "C"}
validMessageStatus  = {"A", "B"}

def _is_Admin(userId):
    '''
        Date        :   2025/4/18
        Author      :   tangling
        Description :   检查是否为管理员（非学生权限）
    '''
    try:
        auth = User.objects.get(id=userId).auth
        if auth == User.STUDENT:
            return False
        return True
    except Exception:
        return False


def _gen_Rand_Str(randLength=6):
    '''
        Date        :   2025/4/18
        Author      :   tangling
        Description :   生成随机字符串
    '''
    randStr = ''
    baseStr = 'ABCDEFGHIGKLMNOPORSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789'
    length = len(baseStr) - 1
    for i in range(randLength):
        randStr += baseStr[random.randint(0, length)]
    return randStr

def _get_user_list(auth_filter=None):
    '''
        Date        :   2025/4/18
        Author      :   tangling
        Description :   按要求得到对应条件的user_list
    '''
    users = []
    query = User.objects.all()
    if auth_filter is not None:
        query = query.filter(auth=auth_filter)

    for user in query:
        users.append({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "registerTime": user.create_time,
            "status": user.status,
            "auth": user.auth
        })
    return users

BAD_PERM_RESP = getResp(
    errcode     = 1,
    message     = "Insufficient authority"
)

class ShowUsers(View):
    '''
        Date        :   2025/4/18
        Author      :   tangling
        Description :   展示所有用户
    '''
    def post(self, request):
        # get request body info
        response = getResp()
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)

        managerId = kwargs.get('managerId')
        if not _is_Admin(managerId):
            return JsonResponse(BAD_PERM_RESP)

        # get all users' info
        users = _get_user_list()
        response = getResp(
            errcode     = 0,
            message     = "get users ok"
        )

        response["users"] = users
        return JsonResponse(response)


class ShowAdmins(View):
    '''
        Date        :   2025/4/18
        Author      :   tangling
        Description :   展示所有管理员
    '''
    def post(self, request):
        response = getResp()
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)

        managerId = kwargs.get('managerId')
        if not _is_Admin(managerId):
            return JsonResponse(BAD_PERM_RESP)

        users = _get_user_list(auth__ne=User.STUDENT)
        response = getResp(
            errcode     = 0,
            message     = "get admins ok"
        )
        response["users"] = users
        return JsonResponse(response)


class ShowAssistants(View):
    '''
        Date        :   2025/4/18
        Author      :   tangling
        Description :   展示所有助教
    '''
    def post(self, request):
        response = getResp()
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)

        managerId = kwargs.get('managerId')
        if not _is_Admin(managerId):
            return JsonResponse(BAD_PERM_RESP)

        users = _get_user_list(User.ASSISTANT)
        response = getResp(
            errcode     = 0,
            message     = "get assistants ok"
        )
        response["users"] = users
        return JsonResponse(response)


class ShowTeachers(View):
    '''
        Date        :   2025/4/18
        Author      :   tangling
        Description :   展示所有教师
    '''
    def post(self, request):
        response = getResp()
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)

        managerId = kwargs.get('managerId')
        if not _is_Admin(managerId):
            return JsonResponse(BAD_PERM_RESP)

        users = _get_user_list(User.TEACHER)
        response = getResp(
            errcode     = 0,
            message     = "get teachers ok"
        )
        response["users"] = users
        return JsonResponse(response)


class ChangeUserStatus(View):
    '''
        Date        :   2025/4/19
        Author      :   tangling
        Description :   修改用户状态
    '''
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = getResp()
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)

        managerId = kwargs.get('managerId')
        if not _is_Admin(managerId):
            return JsonResponse(BAD_PERM_RESP)

        # get userId and changeToStatus from request
        userId = kwargs.get('userId')
        changeToStatus = kwargs.get('changeToStatus')
        # get user Object from db
        user = User.objects.get(id=userId)
        # no need to change
        if user.status == changeToStatus:
            response = getResp(
                errcode     = 2,
                message     = "no need change"
            )
            return JsonResponse(response)
        if changeToStatus in validUserStatus:
            # change user object
            user.status = changeToStatus
            user.save()
            # get response
            response = getResp(
                errcode     = 0,
                message     = "change status ok"
            )
            response["name"] = user.name
            return JsonResponse(response)

        response = getResp(
            errcode     = 3,
            message     = "invalid status"
        )
        return JsonResponse(response)


class ResetUserPassword(View):
    '''
        Date        :   2025/4/19
        Author      :   tangling
        Description :   修改用户密码
    '''
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = getResp()
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)

        managerId = kwargs.get('managerId')
        if not _is_Admin(managerId):
            return JsonResponse(BAD_PERM_RESP)

        # get user object
        userId = kwargs.get('userId')
        user = User.objects.get(id=userId)
        # get new password's sha256 code
        user.password = sha256(_gen_Rand_Str().encode('utf-8')).hexdigest()
        user.save()

        response = getResp(
            errcode     = 0,
            message     = "reset password ok"
        )
        response["name"] = user.name
        response["resetPassword"] = _gen_Rand_Str()
        return JsonResponse(response)

def _get_project_list(managerId, auth):
    '''
        Date        :   2025/4/19
        Author      :   tangling
        Description :   根据权限获取项目列表
    '''
    projects = []
    query = Project.objects.all()

    # 如果不是教师，只获取助理管理的项目
    if auth != User.TEACHER:
        query = query.filter(assistantproject__assistant_id=managerId)

    for project in query:
        leader = User.objects.get(id=project.manager_id.id)
        projects.append({
            "name"      : project.name,
            "projectId" : project.id,
            "leader"    : leader.name,
            "leaderId"  : leader.id,
            "email"     : leader.email,
            "createTime": project.create_time,
            "progress"  : project.progress,
            "status"    : project.status,
            "access"    : project.access
        })
    return projects

class ShowAllProjects(View):
    '''
        Date        :   2025/4/19
        Author      :   tangling
        Description :   展示所有项目
    '''
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = getResp()
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)

        managerId = kwargs.get('managerId')
        if not _is_Admin(managerId):
            return JsonResponse(BAD_PERM_RESP)

        auth = User.objects.get(id=managerId).auth
        projects = _get_project_list(managerId, auth)
        response = getResp(
            errcode     = 0,
            message     = "get projects ok"
        )
        response["projects"] = projects
        return JsonResponse(response)


class ChangeProjectStatus(View):
    '''
        Date        :   2025/4/19
        Author      :   tangling
        Description :   改变项目状态
    '''
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = getResp()
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)

        managerId = kwargs.get('managerId')
        if not _is_Admin(managerId):
            return JsonResponse(BAD_PERM_RESP)

        projectId = kwargs.get('projectId')
        changeToStatus = kwargs.get('changeToStatus')
        project = Project.objects.get(id=projectId)
        projectName = project.name
        if project.status == changeToStatus:
            response = getResp(
                errcode     = 2,
                message     = "no need to change"
            )
            return JsonResponse(response)
        if changeToStatus in validProjectStatus:
            project.status = changeToStatus
            project.save()
            response = getResp(
                errcode     = 0,
                message     = "change status ok"
            )
            response["name"] = projectName
            return JsonResponse(response)
        response = getResp(
            errcode     = 3,
            message     = "invalid status"
        )
        return JsonResponse(response)


class ChangeProjectAccess(View):
    '''
        Date        :   2025/4/19
        Author      :   tangling
        Description :   改变项目access
    '''
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = getResp()
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)

        managerId = kwargs.get('managerId')
        if not _is_Admin(managerId):
            return JsonResponse(BAD_PERM_RESP)

        projectId = kwargs.get('projectId')
        changeToAccess = kwargs.get('changeToAccess')
        project = Project.objects.get(id=projectId)
        projectName = project.name
        if project.access == changeToAccess:
            response = getResp(
                errcode     = 2,
                message     = "no need change"
            )
            return JsonResponse(response)

        project.access = changeToAccess
        project.save()
        response = getResp(
            errcode     = 0,
            message     = "change access ok"
        )
        response["name"] = projectName
        return JsonResponse(response)


class ShowUsersLogin(View):
    '''
        Date        : 2025/04/19
        Author      : tangling
        Description : 展示登录用户
    '''
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = getResp()
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)

        managerId = kwargs.get('managerId')
        if not _is_Admin(managerId):
            return JsonResponse(BAD_PERM_RESP)

        loginMessages = []
        users = User.objects.all()
        for user in users:
            loginMessages.append({
                "name"  :   user.name,
                "email" :   user.email,
                "loginTime" : user.last_login_time
            })
        response = getResp(
            errcode     = 0,
            message     = "get login messages ok"
        )
        response["loginMessages"] = loginMessages
        return JsonResponse(response)


class GetUserNum(View):
    '''
        Date        : 2025/04/19
        Author      : tangling
        Description : 获取用户数目
    '''
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = getResp()
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)

        managerId = kwargs.get('managerId')
        if not _is_Admin(managerId):
            return JsonResponse(BAD_PERM_RESP)

        response = getResp(
            errcode     = 0,
            message     = "get users num ok"
        )
        response["userSum"] = User.objects.count()
        return JsonResponse(response)


class GetProjectNum(View):
    '''
        Date        : 2025/04/19
        Author      : tangling
        Description : 获取项目数目
    '''
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = getResp()
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)

        managerId = kwargs.get('managerId')
        if not _is_Admin(managerId):
            return JsonResponse(BAD_PERM_RESP)

        response = getResp(
            errcode     = 0,
            message     = "get projects num ok"
        )
        response["projectSum"] = Project.objects.count()
        return JsonResponse(response)


TINY_SCALE  = 4
SMALL_SCALE = 8
MID_SCALE   = 16
BIG_SCALE   = 31
class GetProjectScale(View):
    '''
        Date        : 2025/04/19
        Author      : tangling
        Description : 获取不同规模项目数目
    '''
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = getResp()
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)

        managerId = kwargs.get('managerId')
        if not _is_Admin(managerId):
            return JsonResponse(BAD_PERM_RESP)

        response = getResp(
            errcode     = 0,
            message     = "get numbers of different scale projects ok"
        )
        tiny    = 0
        small   = 0
        medium  = 0
        big     = 0
        large   = 0
        projects = Project.objects.all()
        for project in projects:
            usersNum = int(UserProject.objects.filter(project_id=project.id).count())
            if usersNum < TINY_SCALE:
                tiny = tiny + 1
            elif usersNum < SMALL_SCALE:
                small = small + 1
            elif usersNum < MID_SCALE:
                medium = medium + 1
            elif usersNum < BIG_SCALE:
                big = big + 1
            else:
                large = large + 1
        response["tinyNum"  ] = tiny
        response["smallNum" ] = small
        response["mediumNum"] = medium
        response["bigNum"   ] = big
        response["largeNum" ] = large
        return JsonResponse(response)


class ShowAssistantProjects(View):
    '''
        Date        : 2025/04/19
        Author      : tangling
        Description : 展示助教管理项目
    '''
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = getResp()
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)

        managerId = kwargs.get('managerId')
        if not _is_Admin(managerId):
            return JsonResponse(BAD_PERM_RESP)

        userId = kwargs.get('assistantId')
        userAuth = User.objects.get(id=userId).auth
        if userAuth != User.ASSISTANT:
            response = getResp(
                errcode     = 2,
                message     = "queried user is not assistant"
            )
            return JsonResponse(response)
        elif userAuth == User.TEACHER:
            response = getResp(
                errcode     = 3,
                message     = "queried user is teacher"
            )
            return JsonResponse(response)

        projects = []
        for project in Project.objects.all():
            leader = User.objects.get(id=project.manager_id.id)
            if AssistantProject.objects.filter(assistant_id=userId,
                                            project_id=project.pk).count() != 0:
                isManage = 1
            else:
                isManage = 0
            projects.append({
                "name"      : project.name,
                "projectId" : project.id,
                "leader"    : leader.name,
                "leaderId"  : leader.id,
                "email"     : leader.email,
                "createTime": project.create_time,
                "progress"  : project.progress,
                "status"    : project.status,
                "access"    : project.access,
                "isManage"  : isManage  # 不在助理管理项目中，设置 isManage 为 0
            })
        response = getResp(
            errcode     = 0,
            message     = "get assistant projects ok"
        )
        response["projects"] = projects
        return JsonResponse(response)


class ChangeUserAuthority(View):
    '''
        Date        : 2025/04/19
        Author      : tangling
        Description : 修改用户权限
    '''
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = getResp()
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)

        managerId   = kwargs.get('managerId')
        userId      = kwargs.get('userId')
        managerAuth = User.objects.get(id=managerId).auth
        user        = User.objects.get(id=userId)
        userAuth    = user.auth
        changeToAuth= kwargs.get('changeToAuthority')

        if changeToAuth not in validAuthority:
            response = getResp(
                errcode     = 3,
                message     = "Invalid authority"
            )
            return JsonResponse(response)
        if managerAuth < changeToAuth or managerAuth <= userAuth:
            return JsonResponse(BAD_PERM_RESP)

        if userAuth == changeToAuth:
            response = getResp(
                errcode     = 2,
                message     = "no need to change"
            )
            return JsonResponse(response)
        user.auth = changeToAuth
        user.save()
        response = getResp(
            errcode     = 0,
            message     = "change user auth ok"
        )
        response["data"] = {"username": User.objects.get(id=userId).name}
        return JsonResponse(response)


class AddAssistantProject(View):
    '''
        Date        : 2025/04/19
        Author      : tangling
        Description : 为助教添加项目
    '''
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = getResp()
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)

        managerId = kwargs.get('managerId')
        if not _is_Admin(managerId):
            return JsonResponse(BAD_PERM_RESP)

        userId = kwargs.get('userId')
        projectId = kwargs.get('projectId')
        if not User.objects.filter(id=userId).exists():
            response = getResp(
                errcode     = 3,
                message     = "assistant does not exists"
            )
            return JsonResponse(response)
        if not Project.objects.filter(id=projectId).exists():
            response = getResp(
                errcode     = 3,
                message     = "project does not"
            )
            return JsonResponse(response)
        
        user = User.objects.get(id=userId)
        project = Project.objects.get(id=projectId)

        if not len(AssistantProject.objects.filter(assistant_id=userId, 
                                                project_id=projectId)) == 0:
            response = getResp(
                errcode     = 2,
                message     = "no need to add"
            )
            return JsonResponse(response)

        ap = AssistantProject.objects.create(
            assistant_id=user,
            project_id=project
        )
        ap.save()
                
        response = getResp(
            errcode     = 0,
            message     = "add assistant project ok"
        )
        response["username"] = User.objects.filter(id=userId).first().name
        return JsonResponse(response)


class RemoveAssistantProject(View):
    '''
        Date        : 2025/04/19
        Author      : tangling
        Description : 为助教移除项目
    '''
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = getResp()
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)

        managerId = kwargs.get('managerId')
        if not _is_Admin(managerId):
            return JsonResponse(BAD_PERM_RESP)

        managerId = kwargs.get('managerId')
        userId = kwargs.get('userId')
        projectId = kwargs.get('projectId')
        if not User.objects.filter(id=managerId).exists():
            response = getResp(
                errcode     = 3,
                message     = "teacher does not exists"
            )
            return JsonResponse(response)
        if not User.objects.filter(id=userId).exists():
            response = getResp(
                errcode     = 3,
                message     = "assistant does not exists"
            )
            return JsonResponse(response)

        if not Project.objects.filter(id=projectId).exists():
            response = getResp(
                errcode     = 3,
                message     = "project does not exists"
            )
            return JsonResponse(response)

        ap = AssistantProject.objects.filter(assistant_id=userId, project_id=projectId)
        if len(ap) == 0:
            response = getResp(
                errcode     = 2,
                message     = "no need to remove"
            )
            return JsonResponse(response)
        ap.delete()
        
        response = getResp(
            errcode     = 0,
            message     = "remove assistant project ok"
        )
        response["username"] = User.objects.filter(id=userId).first().name
        return JsonResponse(response)


class IsProjectAdmin(View):
    '''
        Date        : 2025/04/19
        Author      : tangling
        Description : 判断用户是否为项目管理员
    '''

    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = getResp()
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)

        managerId = kwargs.get('managerId')
        if not _is_Admin(managerId):
            return JsonResponse(BAD_PERM_RESP)
        
        userId = kwargs.get('userId')
        result = UserProject.objects.filter(user_id_id=userId).exists()
        if result:
            response['data'] = 1
        else:
            response['data'] = 0
        
        response = getResp(
            errcode     = 0,
            message     = "query user ok"
        )
        return JsonResponse(response)
