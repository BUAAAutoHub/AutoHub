import json
import re

from djangoProject.settings import response_json
from myApp.models import Group, User, Message, UserGroup, Project
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

SUCCESS = 0


def get_room_content_api(roomId: int, user: User):
    messages = [
        {
            "content": message.content,
            "senderName": message.send_user.name,
            "senderId": message.send_user.id,
            "time": message.time,
        }
        for message in Message.objects.filter(group_id=roomId, receive_user=user)
    ]
    return messages


def _get_room_content_(request):
    """
    Date        :   2025/4/19
    Author      :   yanfan
    Description :   获取房间聊天记录
    """
    kwargs: dict = json.loads(request.body)
    roomId = kwargs.get("roomId") # int(request.GET.get("roomId"))
    group = Group.objects.get(id=roomId)
    user = User.objects.get(id=kwargs.get("userId"))
    messages = get_room_content_api(roomId, user)
    return response_json(errcode=SUCCESS, data={"messages": messages})


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
    """
    Date        :   2025/4/19
    Author      :   yanfan
    Description :   获取用户的公共讨论组
    """
    kwargs: dict = json.loads(request.body)

    projectId = int(kwargs.get("projectId"))
    userId = int(kwargs.get("userId"))

    discussions = []
    for association in UserGroup.objects.filter(user=userId):
        group = Group.objects.get(id=association.group.id)
        if group.type == "PUB" and group.project_id_id == projectId:
            discussions.append(
                {
                    "roomId": group.id,
                    "roomName": group.name,
                    "outline": group.outline,
                    "users": [
                        {"userId": asso.user.id, "userName": asso.user.name}
                        for asso in UserGroup.objects.filter(group=group)
                    ],
                }
            )

    return response_json(errcode=SUCCESS, data={"discussions": discussions})


def get_user_private_groups(request):
    """
    Date        :   2025/4/19
    Author      :   yanfan
    Description :   获取用户的私密讨论组
    """
    kwargs: dict = json.loads(request.body)

    projectId = int(kwargs.get("projectId"))
    userId = int(request.session["userId"])

    privates = []
    for association in UserGroup.objects.filter(user=userId):
        group = Group.objects.get(id=association.group.id)
        if group.type == "PRI" and group.project_id == projectId:
            privates.append({"roomId": group.id, "roomName": group.name, "outline": group.outline})

    return response_json(errcode=SUCCESS, data={"privates": privates})


def create_public_group(request):
    """
    Date        :   2025/4/19
    Author      :   yanfan
    Description :   创建公共讨论组
    """
    kwargs: dict = json.loads(request.body)
    project = Project.objects.get(id=kwargs.get("projectId"))
    currentUser = User.objects.get(id=kwargs.get("currentUserId"))
    group = Group(name=kwargs.get("roomName"), outline=kwargs.get("outline"), project_id=project, type="PUB")
    group.save()

    association = UserGroup(user=currentUser, group=group, role="A")
    association.save()

    for user_info in kwargs.get("users"):
        user = User.objects.get(id=user_info)
        association = UserGroup(user=user, group=group, role="A")
        association.save()

    return response_json(
        errcode=SUCCESS,
        data={
            "roomId": group.id,
        },
    )



def delete_public_group(request):
    """
    Date        :   2025/5/04
    Author      :   yanfan
    Description :   删除公共讨论组
    """
    kwargs = json.loads(request.body)
    room_id = int(kwargs.get("roomId", 0))

    try:
        group = Group.objects.get(id=room_id)
    except ObjectDoesNotExist:
        return response_json(
            errcode=1,
            message="讨论组不存在"
        )

    if group.type != "PUB":
        return response_json(
            errcode=1,
            message="只允许删除公共讨论组"
        )

    with transaction.atomic():
        # 删除消息
        qs_msg = Message.objects.filter(group_id=room_id)
        deleted_messages = qs_msg.count()
        qs_msg.delete()

        # 删除用户‑讨论组关联
        UserGroup.objects.filter(group=group).delete()

        # 删除讨论组
        group.delete()

    return response_json(
        errcode=SUCCESS,
        message="删除成功",
        data={
            "deletedRoomId": room_id,
            "deletedMessages": deleted_messages
        }
    )

def create_private_group(request):
    """
    Date        :   2025/4/19
    Author      :   yanfan
    Description :   创建私密讨论组
    """
    kwargs: dict = json.loads(request.body)
    project = Project.objects.get(id=kwargs.get("projectId"))
    currentUser = User.objects.get(id=kwargs.get("currentUserId"))
    group = Group(name=kwargs.get("roomName"), outline=kwargs.get("outline"), project_id=project, type="PRI")
    group.save()

    association = UserGroup(user=currentUser, group=group, role="A")
    association.save()
    user = User.objects.get(id=kwargs.get("UserId"))
    association = UserGroup(user=user, group=group, role="A")
    association.save()

    return response_json(
        errcode=SUCCESS,
        data={
            "roomId": group.id,
        },
    )


def add_user_to_group(request):
    """
    Date        :   2025/4/19
    Author      :   yanfan
    Description :   添加用户到讨论组
    """
    kwargs: dict = json.loads(request.body)

    user = User.objects.get(id=int(kwargs.get("userId")))
    group = Group.objects.get(id=int(kwargs.get("roomId")))

    association = UserGroup.objects.filter(user=user, group=group)
    if not len(association) == 0:
        return response_json(
            errcode=SUCCESS,
        )
    association = UserGroup(user=user, group=group, role="A")
    association.save()
    return response_json(errcode=SUCCESS)


def delete_user_from_group(request):
    """
    Date        :   2025/4/19
    Author      :   yanfan
    Description :   删除用户从讨论组
    """
    kwargs: dict = json.loads(request.body)

    user = User.objects.get(id=int(kwargs.get("userId")))
    room = Group.objects.get(id=int(kwargs.get("roomId")))
    association = UserGroup.objects.filter(user=user, group=room)
    association.delete()

    return response_json(errcode=SUCCESS)


def delete_user_from_groups(user_id: int, project_id: int):
    """
    Date        :   2025/4/19
    Author      :   yanfan
    Description :   删除用户从讨论组
    """
    user = User.objects.get(id=int(user_id))
    project = Project.objects.get(id=int(project_id))

    groups = Group.objects.filter(project_id=project)
    for group in groups:
        association = UserGroup.objects.filter(user=user, group=group)
        if not len(association) == 0:
            association.first().delete()


def search_from_message(request):
    """
    Date        :   2025/4/19
    Author      :   tangling
    Description :   搜索聊天室中的消息
    """
    kwargs: dict = json.loads(request.body)

    roomId = int(kwargs.get("roomId"))
    search_text = kwargs.get("searchText", "").lower()  # 获取搜索文本并转换为小写
    user = User.objects.get(id=int(kwargs.get("userId")))

    # 获取所有消息
    messages = Message.objects.filter(group_id=roomId, receive_user=user)

    # 通过正则表达式匹配
    pattern = re.compile(".*".join(re.escape(word) for word in search_text.split()))

    # 过滤包含搜索文本的消息
    matched_messages = [
        {
            "content": message.content,
            "senderName": message.send_user.name,
            "senderId": message.send_user.id,
            "time": message.time,
        }
        for message in messages
        if pattern.search(message.content)  # 使用正则表达式搜索
    ]

    return response_json(errcode=SUCCESS, data={"messages": matched_messages})
