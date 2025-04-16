from django.http import JsonResponse

from myApp.models import User, UserProject, Project
from djangoProject.settings import response_json
import datetime
import json

from myApp.utils.projects.userdevelop import genResponseStateInfo

# 返回给前端的 ErrorCode
Success = 0
Email_Duplicated = 2
Username_Duplicated = 3
None_Existed_User = 1
Password_Wrong = 2
Invalid_Status = 3
Modification_Failed = 1
Modification_Profile_Failed = 1
Show_User_Profile_Failed = 1

# 返回给前端的信息
Register_Success_Message = 'register ok'
Login_Success_Message = 'login ok'
Email_Duplicated_Message = 'email duplicated'
Username_Duplicated_Message = 'username duplicated'
None_Existed_User_Message = 'no user or email'
Password_Wrong_Message = 'error password'
Invalid_Status_Message = 'error status'
Modification_Failed_Message = 'fail to change'
Modification_Success_Message = 'change password ok'
Modification_Profile_Failed_Message = 'fail to edit profile'
Show_User_Profile_Failed_Message = 'fail to show profile'


def testtesttest(request):
    return response_json(
        errcode=0,
        message='this is test')


def register(request):
    """
        register api,
        1. check whether have duplicated username.
        2. check whether have duplicated email.
    """
    kwargs: dict = json.loads(request.body)
    username, email = kwargs.get('username'), kwargs.get('email')

    # Step 1. Check
    users = User.objects.filter(email=email)
    if not len(users) == 0:
        return response_json(
            errcode=Email_Duplicated,
            message=Email_Duplicated_Message
        )

    # Step 2. Check
    users = User.objects.filter(name=username)
    if not len(users) == 0:
        return response_json(
            errcode=Username_Duplicated,
            message=Username_Duplicated_Message
        )

    # Step 3. Create
    u = User(name=username,
             password=kwargs.get('password'),
             email=email,
             status=User.NORMAL,
             color='D',
             create_time=datetime.datetime.now(),
             last_login_time=datetime.datetime.now(),
             auth=User.STUDENT)
    u.save()
    return response_json(
        errcode=Success,
        message=Register_Success_Message
    )


def login(request):
    """
        login api:
        1. Get specific user according to `username`.
        2. Check whether the user has limit.
        2. Check password correct.
    """
    kwargs: dict = json.loads(request.body)
    # Step 1. Check
    user = User.objects.filter(name=kwargs.get('userNameOrEmail'))
    if len(user) == 0:
        user = User.objects.filter(email=kwargs.get('userNameOrEmail'))
        if len(user) == 0:
            return response_json(
                errcode=None_Existed_User,
                message=None_Existed_User_Message
            )

    # Step 2. Check
    user = user.first()
    if user.status == User.ILLEGAL:
        return response_json(
            errcode=Invalid_Status,
            message=Invalid_Status_Message
        )

    # Step 3. Check
    if not user.password == kwargs.get('password'):
        return response_json(
            errcode=Password_Wrong,
            message=Password_Wrong_Message
        )

    # Step 4. Login & Session
    request.session['userId'] = user.id
    projects = [{'id': p.id, 'name': p.name} for p in user.project_set.all()]
    for up in UserProject.objects.filter(user_id=user.id):
        project = Project.objects.filter(id=int(up.project_id.id)).first()
        projects.append({'id': project.id, 'name': project.name})
    user.last_login_time = datetime.datetime.now()
    user.save()
    return response_json(
        errcode=Success,
        message=Login_Success_Message,
        data={
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'projects': projects,
            'status': user.status,
            'topic': user.color,
            'auth': user.auth
        }
    )


def get_user_information(request):
    kwargs: dict = json.loads(request.body)

    manager = User.objects.get(id=int(kwargs.get('managerId')))
    if manager.auth == 1:
        return response_json(
            errcode=1,
            message='not admin'
        )
    user = User.objects.get(id=int(kwargs.get('userId')))
    projects = [{'id': p.id, 'name': p.name} for p in user.project_set.all()]
    for up in UserProject.objects.filter(user_id=user.id):
        project = Project.objects.filter(id=int(up.project_id.id)).first()
        projects.append({'id': project.id, 'name': project.name})
    return response_json(
        errcode=Success,
        message=Login_Success_Message,
        data={
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'projects': projects,
            'status': user.status,
            'topic': user.color,
            'auth': user.auth,
        }
    )


def modify_password(request):
    """
        modify password api
        0. Check Authentication.
        1. Check whether there exists target user, according to `id`.
        2. Check user password correct, according to `oldPassword`.
        3. Modification.
    """
    kwargs: dict = json.loads(request.body)
    # Step 0. Check, todo
    # Step 1. Check
    user = User.objects.get(id=int(kwargs.get('userId')))
    if user is None:
        return response_json(
            errcode=Modification_Failed,
            message=Modification_Failed_Message
        )

    if not user.password == kwargs.get('oldPassword'):
        return response_json(
            errcode=Modification_Failed,
            message=Modification_Failed_Message
        )

    try:
        user.password = kwargs.get('newPassword')
        user.save()
        return response_json(
            errcode=Success,
            message=Modification_Success_Message
        )
    except Exception as exp:
        return response_json(
            errcode=Modification_Failed,
            message=Modification_Failed_Message
        )


def show(request):
    kwargs: dict = json.loads(request.body)
    user = User.objects.filter(id=int(kwargs.get('userId')))
    if len(user) == 0:
        return response_json(
            errcode=Show_User_Profile_Failed,
            message=Show_User_Profile_Failed_Message,
        )

    user = user.first()
    return response_json(
        errcode=Success,
        message="show profile ok",
        data={
            'userName': user.name,
            'userEmail': user.email,
            'photo': None,
        }
    )


def modify_information(request):
    """
        modify_information 用于修改用户的 username 或者 email. 前端逻辑如下:
        - 若用户只更改email, 则传来用户原先的username.
        - 若用户只更改username, 则传来用户原先的email.
        - 若用户二者都更改, 则同时传来新email和新username.
    """

    kwargs: dict = json.loads(request.body)
    user = User.objects.filter(id=int(kwargs.get('userId'))).first()

    users = User.objects.filter(name=str(kwargs.get('userName')))
    if not (len(users) == 1 and users.first().id == user.id) and not len(users) == 0:
        return response_json(
            errcode=Username_Duplicated,
            message=Username_Duplicated_Message
        )

    users = User.objects.filter(email=str(kwargs.get('userEmail')))
    if not (len(users) == 1 and users.first().id == user.id) and not len(users) == 0:
        return response_json(
            errcode=Email_Duplicated,
            message=Email_Duplicated_Message
        )

    try:
        user.name = str(kwargs.get('userName'))
        user.email = str(kwargs.get('userEmail'))
        user.save()

        projects = [{'id': p.id, 'name': p.name} for p in user.project_set.all()]
        for up in UserProject.objects.filter(user_id=user.id):
            project = Project.objects.filter(id=int(up.project_id.id)).first()
            projects.append({'id': project.id, 'name': project.name})
        return response_json(
            errcode=Success,
            message='edit profile ok',
            data={
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'projects': projects,
                'status': user.status,
                'topic': user.color,
                'auth': user.auth
            }
        )
    except Exception as exp:
        return response_json(
            errcode=Modification_Profile_Failed,
            message=Modification_Profile_Failed_Message
        )


def save_topic(request):
    kwargs: dict = json.loads(request.body)

    user = User.objects.get(id=int(request.session['userId']))
    user.color = kwargs.get('topic')
    user.save()

    projects = [{'id': p.id, 'name': p.name} for p in user.project_set.all()]
    for up in UserProject.objects.filter(user_id=user.id):
        project = Project.objects.filter(id=int(up.project_id.id)).first()
        projects.append({'id': project.id, 'name': project.name})
    return response_json(
        errcode=Success,
        data={
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'projects': projects,
            'status': user.status,
            'topic': user.color,
            'auth': user.auth
        }
    )


def modify_token(request):
    response = {'message': "404 not success", "errcode": -1}
    try:
        kwargs: dict = json.loads(request.body)
    except Exception:
        return JsonResponse(response)
    response = {}
    genResponseStateInfo(response, 0, "modify token ok")
    userId = str(kwargs.get('userId'))
    token = str(kwargs.get('token'))

    if not User.objects.filter(id=userId).exists():
        return genResponseStateInfo(response, 1, "user not exist")
    user = User.objects.get(id=userId)
    user.token = token
    user.save()
    return JsonResponse(response)


def check_token(request):
    response = {'message': "404 not success", "errcode": -1}
    try:
        kwargs: dict = json.loads(request.body)
    except Exception:
        return JsonResponse(response)
    response = {}
    genResponseStateInfo(response, 0, "check token ok")
    userId = str(kwargs.get('userId'))
    if not User.objects.filter(id=userId).exists():
        return genResponseStateInfo(response, 1, "user not exist")
    user = User.objects.get(id=userId)
    response["data"] = {}
    if user.token is not None:
        response["message"] = "you already have token"
        response["data"]["flag"] = 1
    else:
        response["message"] = "you don't have token"
        response["data"]["flag"] = 0
    return JsonResponse(response)
