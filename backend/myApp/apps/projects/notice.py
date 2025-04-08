import struct

from django.http import JsonResponse, HttpResponse
from django.core import serializers
from django.views import View
from myApp.models import *
from djangoProject.settings import DBG, USER_REPOS_DIR, BASE_DIR
import json
import os
import shutil
import sys
import subprocess
import json5
from myApp.userdevelop import *


# Functions for backend calls

def userPostNoticeToAll(userId, projectId, name, content):
    DBG("---- in " + sys._getframe().f_code.co_name + " ----")
    response = {'message': "post ok", "errcode": 0}
    project = isProjectExists(projectId)
    if project == None:
        return genResponseStateInfo(response, 1, "project does not exists")
    userProject = isUserInProject(userId, projectId)
    if userProject == None:
        return genResponseStateInfo(response, 2, "user not in project")
    if str(project.manager_id.id) != str(userId):
        return genResponseStateInfo(response, 3, "user is not a manager")
    userProjectEntries = UserProject.objects.filter(project_id=projectId)
    postList = list()
    for userProjectEntry in userProjectEntries:
        postList.append(Post(name=name, content=content, post_type=Post.PROJ_ALL,
                             receiver_id=userProjectEntry.user_id, is_received=False,
                             user_id=userProject.user_id, project_id=userProject.project_id))
    Post.objects.bulk_create(postList)
    return response


def userPostNoticeToOne(userId, projectId, name, content, receiverId):
    DBG("---- in " + sys._getframe().f_code.co_name + " ----")
    response = {'message': "post ok", "errcode": 0}
    project = isProjectExists(projectId)
    if project == None:
        return genResponseStateInfo(response, 1, "project does not exists")
    userProject = isUserInProject(userId, projectId)
    if userProject == None:
        return genResponseStateInfo(response, 2, "user not in project")
    receiverProject = isUserInProject(receiverId, projectId)
    if receiverProject == None:
        return genResponseStateInfo(response, 3, "receiver not in project")

    Post(name=name, content=content, post_type=Post.PROJ_ONE,
         receiver_id=receiverProject.user_id, is_received=False,
         user_id=userProject.user_id, project_id=userProject.project_id).save()
    return response


def sysPostNoticeInProject(projectId, name, content):
    DBG("---- in " + sys._getframe().f_code.co_name + " ----")
    response = {'message': "post ok", "errcode": 0}
    project = isProjectExists(projectId)
    if project == None:
        return genResponseStateInfo(response, 1, "project does not exists")

    userProjectEntries = UserProject.objects.filter(project_id=projectId)
    postList = list()
    for userProjectEntry in userProjectEntries:
        postList.append(Post(name=name, content=content, post_type=Post.SYS_PROJ,
                             receiver_id=userProjectEntry.user_id, is_received=False,
                             project_id=project))
    Post.objects.bulk_create(postList)
    return response


def sysPostNoticeToAll(name, content):
    DBG("---- in " + sys._getframe().f_code.co_name + " ----")
    response = {'message': "post ok", "errcode": 0}
    userEntries = User.objects.all()
    postList = list()
    for user in userEntries:
        postList.append(Post(name=name, content=content, post_type=Post.SYS_ALL,
                             receiver_id=user, is_received=False))
    Post.objects.bulk_create(postList)
    return response


def genPostResponse(post, send_user_name, project_name):
    js = {}
    js["id"] = post.id
    js["name"] = post.name
    js["content"] = post.content
    js["post_time"] = post.post_time
    js["type"] = post.post_type
    js["send_user_name"] = send_user_name
    js["project_name"] = project_name
    return js


def userGetNotice(userId):
    DBG("---- in " + sys._getframe().f_code.co_name + " ----")
    response = {'message': "post ok", "errcode": 0}
    newPost = []
    historyPost = []
    user = User.objects.get(id=userId)
    postEntries = Post.objects.filter(receiver_id=user)
    for post in postEntries:
        send_user_name = "system"
        project_name = "system"
        if post.user_id != None:
            send_user_name = User.objects.get(id=post.user_id.id).name
        if post.project_id != None:
            project_name = Project.objects.get(id=post.project_id.id).name
        if post.is_received == False:
            newPost.append(genPostResponse(post, send_user_name, project_name))
        else:
            historyPost.append(genPostResponse(post, send_user_name, project_name))

    response["newPost"] = newPost
    response["historyPost"] = historyPost
    return response


def userConfirmNotice(userId, postId):
    DBG("---- in " + sys._getframe().f_code.co_name + " ----")
    response = {'message': "post ok", "errcode": 0}
    Post.objects.filter(id=postId).update(is_received=True)
    return response


class UserPostNoticeToAll(View):
    def post(self, request):
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        return JsonResponse(userPostNoticeToAll(kwargs.get('userId'), kwargs.get('projectId'),
                                                kwargs.get('name'), kwargs.get('content')))


class UserPostNoticeToOne(View):
    def post(self, request):
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        return JsonResponse(userPostNoticeToOne(kwargs.get('userId'), kwargs.get('projectId'),
                                                kwargs.get('name'), kwargs.get('content'),
                                                kwargs.get('receiverId')))


class SysPostNoticeInProject(View):
    def post(self, request):
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        return JsonResponse(sysPostNoticeInProject(kwargs.get('projectId'),
                                                   kwargs.get('name'), kwargs.get('content')))


class SysPostNoticeToAll(View):
    def post(self, request):
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        return JsonResponse(sysPostNoticeToAll(kwargs.get('name'), kwargs.get('content')))


class UserGetNotice(View):
    def post(self, request):
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        return JsonResponse(userGetNotice(kwargs.get('userId')))


class UserConfirmNotice(View):
    def post(self, request):
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        return JsonResponse(userConfirmNotice(kwargs.get('userId'), kwargs.get('postId')))
