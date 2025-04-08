from myApp.models import *
from djangoProject.settings import response_json
import json

SUCCESS = 0

def get_room_content(request):
    kwargs: dict = json.loads(request.body)

    roomId = int(kwargs.get('roomId'))
    group = Group.objects.get(id = roomId)
    user = User.objects.get(id = int(kwargs.get('userId')))

    messages = [
        {
            'content': message.content,
            'senderName': message.send_user.name,
            'senderId': message.send_user.id,
            'time': message.time
        } for message in Message.objects.filter(group_id = roomId, receive_user = user)
    ]

    return response_json(
        errcode = SUCCESS,
        data = {
            'messages': messages
        }
    )


def get_user_public_groups(request):
    kwargs: dict = json.loads(request.body)

    projectId = int(kwargs.get('projectId'))
    userId = int(kwargs.get('userId'))

    discussions = []
    for association in UserGroup.objects.filter(user = userId):
        group = Group.objects.get(id = association.group.id)
        if group.type == 'PUB' and group.project_id_id == projectId:
            discussions.append({
                'roomId': group.id,
                'roomName': group.name,
                'outline': group.outline,
                'users': [
                    {
                        'userId': asso.user.id,
                        'userName': asso.user.name
                    } for asso in UserGroup.objects.filter(group = group)
                ]
            })

    return response_json(
        errcode = SUCCESS,
        data = {
            'discussions': discussions
        }
    )


def get_user_private_groups(request):
    kwargs: dict = json.loads(request.body)

    projectId = int(kwargs.get('projectId'))
    userId = int(request.session['userId'])

    privates = []
    for association in UserGroup.objects.filter(user = userId):
        group = Group.objects.get(id = association.group.id)
        if group.type == 'PRI' and group.project_id == projectId:
            privates.append({
                'roomId': group.id,
                'roomName': group.name,
                'outline': group.outline
            })

    return response_json(
        errcode = SUCCESS,
        data = {
            'privates': privates
        }
    )


def create_public_group(request):
    kwargs: dict = json.loads(request.body)
    project = Project.objects.get(id=kwargs.get('projectId'))
    currentUser = User.objects.get(id=kwargs.get('currentUserId'))
    group = Group(
        name = kwargs.get('roomName'),
        outline = kwargs.get('outline'),
        project_id = project,
        type = 'PUB'
    )
    group.save()

    association = UserGroup(
        user = currentUser,
        group = group,
        role = 'A'
    )
    association.save()

    for user_info in kwargs.get('users'):
        user = User.objects.get(id=user_info)
        association = UserGroup(
            user = user,
            group = group,
            role = 'A'
        )
        association.save()

    return response_json(
        errcode = SUCCESS,
        data = {
            'roomId': group.id,
        }
    )


def create_private_group(request):
    kwargs: dict = json.loads(request.body)
    project = Project.objects.get(id=kwargs.get('projectId'))
    currentUser = User.objects.get(id=kwargs.get('currentUserId'))
    group = Group(
        name = kwargs.get('roomName'),
        outline = kwargs.get('outline'),
        project_id = project,
        type = 'PRI'
    )
    group.save()

    association = UserGroup(
        user = currentUser,
        group = group,
        role = 'A'
    )
    association.save()
    user = User.objects.get(id=kwargs.get('UserId'))
    association = UserGroup(
        user = user,
        group = group,
        role = 'A'
    )
    association.save()

    return response_json(
        errcode = SUCCESS,
        data = {
            'roomId': group.id,
        }
    )


def add_user_to_group(request):
    kwargs: dict = json.loads(request.body)

    user = User.objects.get(id = int(kwargs.get('userId')))
    group = Group.objects.get(id = int(kwargs.get('roomId')))

    association = UserGroup.objects.filter(user = user, group = group)
    if not len(association) == 0:
        return response_json(
            errcode = SUCCESS,
        )
    association = UserGroup(
        user = user,
        group = group,
        role = 'A'
    )
    association.save()
    return response_json(
        errcode = SUCCESS
    )


def delete_user_from_group(request):
    kwargs: dict = json.loads(request.body)

    user = User.objects.get(id = int(kwargs.get('userId')))
    room = Group.objects.get(id = int(kwargs.get('roomId')))
    association = UserGroup.objects.filter(user = user, group = room)
    association.delete()

    return response_json(
        errcode = SUCCESS
    )


def delete_user_from_groups(user_id: int, project_id: int):
    user = User.objects.get(id = int(user_id))
    project = Project.objects.get(id = int(project_id))

    groups = Group.objects.filter(project_id = project)
    for group in groups:
        association = UserGroup.objects.filter(user = user, group = group)
        if not len(association) == 0:
            association.first().delete()
