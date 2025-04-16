import struct
import json
import os
import shutil
import sys
import subprocess
import json5

from django.http import JsonResponse, HttpResponse
from django.core import serializers
from django.views import View
from myApp.models import *
from djangoProject.settings import DBG, USER_REPOS_DIR, BASE_DIR
from myApp.utils.projects.userdevelop import *


def userDocListTemplate(userId, projectId, table):
    DBG("---- in " + sys._getframe().f_code.co_name + " ----")
    DBG("param" + str(locals()))
    response = {'message': "get userDocListTemplate ok", "errcode": 0}
    project = isProjectExists(projectId)
    if project == None:
        return genResponseStateInfo(response, 1, "project does not exists")
    userProject = isUserInProject(userId, projectId)
    if userProject == None:
        return genResponseStateInfo(response, 2, "user not in project")
    if userProject.viewAuth == UserProject.N:
        return genResponseStateInfo(response, 3, "no view auth")
    data = []
    tableEntries = table.objects.filter(user_id=userId)
    for entry in tableEntries:
        docEntry = Document.objects.get(id=entry.doc_id.id)
        if str(docEntry.project_id.id) != str(projectId):
            continue
        ownerName = User.objects.get(id=docEntry.user_id.id).name

        userAccessEntries = UserAccessDoc.objects.filter(doc_id=entry.doc_id.id)
        accessUser = []
        for entry in userAccessEntries:
            userName = User.objects.get(id=entry.user_id.id).name
            accessUser.append({"id": entry.user_id.id, "name": userName})

        isCollect = UserCollectDoc.objects.filter(user_id=userId, doc_id=docEntry.id).exists()

        data.append({"id": docEntry.id,
                     "name": docEntry.name,
                     "ownerName": ownerName,
                     "updateTime": docEntry.time,
                     "outline": docEntry.outline,
                     "content": docEntry.content,
                     "accessUser": accessUser,
                     "isCollect": isCollect})
    response["data"] = data
    return response


class UserDocList(View):
    def post(self, request):
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        try:
            response = userDocListTemplate(kwargs.get('userId'), kwargs.get('projectId'),
                UserAccessDoc)
        except Exception as e:
            return JsonResponse({'message': str(e), "errcode": -1})
        return JsonResponse(response)


class UserCollectDocList(View):
    def post(self, request):
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        try:
            response = userDocListTemplate(kwargs.get('userId'), kwargs.get('projectId'),
                UserCollectDoc)
        except Exception as e:
            return JsonResponse({'message': str(e), "errcode": -1})
        return JsonResponse(response)


def addDocToCollect(userId, projectId, docId):
    DBG("---- in " + sys._getframe().f_code.co_name + " ----")
    DBG("param" + str(locals()))
    response = {'message': "get addDocToCollect ok", "errcode": 0}
    project = isProjectExists(projectId)
    if project == None:
        return genResponseStateInfo(response, 1, "project does not exists")
    userProject = isUserInProject(userId, projectId)
    if userProject == None:
        return genResponseStateInfo(response, 2, "user not in project")
    docprev = UserCollectDoc.objects.filter(user_id=userId, doc_id=docId)
    if len(docprev) > 0:
        return genResponseStateInfo(response, 3, "doc already in collect")
    UserCollectDoc(user_id=User.objects.get(id=userId),
                   doc_id=Document.objects.get(id=docId)).save()
    return response


class AddDocToCollect(View):
    def post(self, request):
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        try:
            response = addDocToCollect(kwargs.get('userId'),
                                       kwargs.get('projectId'), kwargs.get('docId'))
        except Exception as e:
            return JsonResponse({'message': str(e), "errcode": -1})
        return JsonResponse(response)


def delDocFromCollect(userId, projectId, docId):
    DBG("---- in " + sys._getframe().f_code.co_name + " ----")
    DBG("param" + str(locals()))
    response = {'message': "get delDocFromCollect ok", "errcode": 0}
    project = isProjectExists(projectId)
    if project == None:
        return genResponseStateInfo(response, 1, "project does not exists")
    userProject = isUserInProject(userId, projectId)
    if userProject == None:
        return genResponseStateInfo(response, 2, "user not in project")
    UserCollectDoc.objects.filter(user_id=userId, doc_id=docId).delete()
    return response


class DelDocFromCollect(View):
    def post(self, request):
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        try:
            response = delDocFromCollect(kwargs.get('userId'),
                                         kwargs.get('projectId'), kwargs.get('docId'))
        except Exception as e:
            return JsonResponse({'message': str(e), "errcode": -1})
        return JsonResponse(response)


def userCreateDoc(userId, projectId, name, outline, content, accessUserId):
    DBG("---- in " + sys._getframe().f_code.co_name + " ----")
    DBG("param" + str(locals()))
    response = {'message': "get userCreateDoc ok", "errcode": 0}
    project = isProjectExists(projectId)
    if project == None:
        return genResponseStateInfo(response, 1, "project does not exists")
    userProject = isUserInProject(userId, projectId)
    if userProject == None:
        return genResponseStateInfo(response, 2, "user not in project")
    prevDoc = Document.objects.filter(name=name, project_id=projectId)
    if len(prevDoc) > 0:
        return genResponseStateInfo(response, 3, "duplicate doc")
    user = User.objects.get(id=userId)
    Document(name=name, outline=outline, content=content, project_id=project,
             user_id=user).save()
    doc = Document.objects.get(name=name, project_id=projectId, user_id=userId)
    for item in accessUserId:
        accessUser = User.objects.get(id=item)
        UserAccessDoc(user_id=accessUser, doc_id=doc).save()
    return response


class UserCreateDoc(View):
    def post(self, request):
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        try:
            response = userCreateDoc(kwargs.get('userId'),
                                     kwargs.get('projectId'), kwargs.get('name'),
                                     kwargs.get('outline'), kwargs.get('content'),
                                     kwargs.get('accessUserId'))
        except Exception as e:
            return JsonResponse({'message': str(e), "errcode": -1})
        return JsonResponse(response)


def userEditDocOther(userId, docId, projectId, name, accessUserId):
    DBG("---- in " + sys._getframe().f_code.co_name + " ----")
    DBG("param" + str(locals()))
    response = {'message': "get userEditDocOther ok", "errcode": 0}
    project = isProjectExists(projectId)
    if project == None:
        return genResponseStateInfo(response, 1, "project does not exists")
    userProject = isUserInProject(userId, projectId)
    if userProject == None:
        return genResponseStateInfo(response, 2, "user not in project")
    if userProject.editAuth == UserProject.N:
        return genResponseStateInfo(response, 3, "no edit auth")
    Document.objects.filter(id=docId).update(name=name)
    doc = Document.objects.get(id=docId)
    for item in accessUserId:
        accessUser = User.objects.get(id=item)
        UserAccessDoc.objects.get_or_create(user_id=accessUser, doc_id=doc)
    allUserAccessEntries = UserAccessDoc.objects.filter(doc_id=docId)
    for userAccessEntry in allUserAccessEntries:
        thisUserId = userAccessEntry.user_id.id
        if accessUserId.count(thisUserId) == 0:
            UserAccessDoc.objects.filter(doc_id=docId, user_id=thisUserId).delete()
    allUserCollectEntries = UserCollectDoc.objects.filter(doc_id=docId)
    for userCollectEntry in allUserCollectEntries:
        thisUserId = userCollectEntry.user_id.id
        if accessUserId.count(thisUserId) == 0:
            UserCollectDoc.objects.filter(doc_id=docId, user_id=thisUserId).delete()
    return response


class UserEditDocOther(View):
    def post(self, request):
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        try:
            response = userEditDocOther(kwargs.get('userId'), kwargs.get('docId'),
                                        kwargs.get('projectId'), kwargs.get('name'),
                                        kwargs.get('accessUserId'))
        except Exception as e:
            return JsonResponse({'message': str(e), "errcode": -1})
        return JsonResponse(response)


def userEditDocContent(userId, docId, projectId, content):
    DBG("---- in " + sys._getframe().f_code.co_name + " ----")
    DBG("param" + str(locals()))
    response = {'message': "get userEditDocContent ok", "errcode": 0}
    project = isProjectExists(projectId)
    if project == None:
        return genResponseStateInfo(response, 1, "project does not exists")
    userProject = isUserInProject(userId, projectId)
    if userProject == None:
        return genResponseStateInfo(response, 2, "user not in project")
    if userProject.editAuth == UserProject.N:
        return genResponseStateInfo(response, 3, "no edit auth")
    Document.objects.filter(id=docId).update(
        content=content, time=datetime.datetime.now()
    )
    return response


class UserEditDocContent(View):
    def post(self, request):
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        try:
            response = userEditDocContent(kwargs.get('userId'), kwargs.get('docId'),
                                          kwargs.get('projectId'), kwargs.get('content'))
        except Exception as e:
            return JsonResponse({'message': str(e), "errcode": -1})
        return JsonResponse(response)


def userGetDocLock(userId, projectId, docId):
    DBG("---- in " + sys._getframe().f_code.co_name + " ----")
    DBG("param" + str(locals()))
    response = {'message': "get userGetDocLock ok", "errcode": 0}
    project = isProjectExists(projectId)
    if project == None:
        return genResponseStateInfo(response, 1, "project does not exists")
    userProject = isUserInProject(userId, projectId)
    if userProject == None:
        return genResponseStateInfo(response, 2, "user not in project")
    if userProject.viewAuth == UserProject.N:
        return genResponseStateInfo(response, 4, "no view auth")
    doc = Document.objects.get(id=docId)
    user = User.objects.get(id=userId)
    try:
        UserDocLock(doc_id=doc, user_id=user).save()
    except Exception as e:
        return genResponseStateInfo(response, 3, "doc is being edited")
    return response


class UserGetDocLock(View):
    def post(self, request):
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        try:
            response = userGetDocLock(kwargs.get('userId'), kwargs.get('projectId'),
                                      kwargs.get('docId'))
        except Exception as e:
            return JsonResponse({'message': str(e), "errcode": -1})
        return JsonResponse(response)


def userReleaseDocLock(userId, projectId, docId):
    DBG("---- in " + sys._getframe().f_code.co_name + " ----")
    DBG("param" + str(locals()))
    response = {'message': "get userReleaseLock ok", "errcode": 0}
    project = isProjectExists(projectId)
    if project == None:
        return genResponseStateInfo(response, 1, "project does not exists")
    userProject = isUserInProject(userId, projectId)
    if userProject == None:
        return genResponseStateInfo(response, 2, "user not in project")

    UserDocLock.objects.filter(doc_id=docId, user_id=userId).delete()
    return response


class UserReleaseDocLock(View):
    def post(self, request):
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        try:
            response = userReleaseDocLock(kwargs.get('userId'), kwargs.get('projectId'),
                                          kwargs.get('docId'))
        except Exception as e:
            return JsonResponse({'message': str(e), "errcode": -1})
        return JsonResponse(response)


def userDelDoc(userId, projectId, docId):
    DBG("---- in " + sys._getframe().f_code.co_name + " ----")
    DBG("param" + str(locals()))
    response = {'message': "get userDelDoc ok", "errcode": 0}
    project = isProjectExists(projectId)
    if project == None:
        return genResponseStateInfo(response, 1, "project does not exists")
    userProject = isUserInProject(userId, projectId)
    if userProject == None:
        return genResponseStateInfo(response, 2, "user not in project")
    Document.objects.filter(id=docId).delete()
    return response


class UserDelDoc(View):
    def post(self, request):
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        try:
            response = userDelDoc(kwargs.get('userId'),
                                  kwargs.get('projectId'), kwargs.get('docId'))
        except Exception as e:
            return JsonResponse({'message': str(e), "errcode": -1})
        return JsonResponse(response)


def docTimeUpdate(userId, projectId, docId, updateTime):
    DBG("---- in " + sys._getframe().f_code.co_name + " ----")
    DBG("param" + str(locals()))
    response = {'message': "get docTimeUpdate ok", "errcode": 0}
    project = isProjectExists(projectId)
    if project == None:
        return genResponseStateInfo(response, 1, "project does not exists")
    userProject = isUserInProject(userId, projectId)
    if userProject == None:
        return genResponseStateInfo(response, 2, "user not in project")
    Document.objects.filter(id=docId).update(time=updateTime)
    return response


class DocTimeUpdate(View):
    def post(self, request):
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        try:
            response = userDelDoc(kwargs.get('userId'),
                                  kwargs.get('projectId'), kwargs.get('docId'),
                                  kwargs.get('updateTime'))
        except Exception as e:
            return JsonResponse({'message': str(e), "errcode": -1})
        return JsonResponse(response)


class IsDocLocked(View):
    def post(self, request):
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        docId = kwargs.get('docId')
        o = UserDocLock.objects.filter(doc_id=docId)
        response = {'message': "get isDocLocked ok", "errcode": 0}
        response["isLocked"] = True
        if len(o) == 0:
            response["isLocked"] = False
        return JsonResponse(response)
