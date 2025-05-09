import json
import sys

from django.http import JsonResponse
from django.views import View
from djangoProject.settings import DBG
from myApp.utils.projects.userdevelop import isProjectExists, genResponseStateInfo, isUserInProject, datetime
from myApp.models import UserProject, Document, User, UserAccessDoc, UserCollectDoc, UserDocLock
from myApp.utils.format.request import getResp


def userDocListTemplate(userId, projectId, table):
    """
    Date        :   2025/4/19
    Author      :   yanfan
    Description :   获取用户在指定项目中的文档列表及其相关信息。
    """
    DBG("---- in " + sys._getframe().f_code.co_name + " ----")
    DBG("param" + str(locals()))
    response = getResp(0, "get userDocListTemplate ok")
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

        data.append(
            {
                "id": docEntry.id,
                "name": docEntry.name,
                "ownerName": ownerName,
                "updateTime": docEntry.time,
                "outline": docEntry.outline,
                "content": docEntry.content,
                "accessUser": accessUser,
                "isCollect": isCollect,
            }
        )
    response["data"] = data
    return response


class UserDocList(View):
    def post(self, request):
        """
        Date        :   2025/4/19
        Author      :   yanfan
        Description :   获取用户在指定项目中的文档列表及其相关信息。
        """
        response = getResp(-1, "404 not success")
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        try:
            response = userDocListTemplate(kwargs.get("userId"), kwargs.get("projectId"), UserAccessDoc)
        except Exception as e:
            return JsonResponse({"message": str(e), "errcode": -1})
        return JsonResponse(response)


class UserCollectDocList(View):
    def post(self, request):
        """
        Date        :   2025/4/19
        Author      :   yanfan
        Description :   获取用户在指定项目中的文档列表及其相关信息。
        """
        response = getResp(-1, "404 not success")
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        try:
            response = userDocListTemplate(kwargs.get("userId"), kwargs.get("projectId"), UserCollectDoc)
        except Exception as e:
            return JsonResponse({"message": str(e), "errcode": -1})
        return JsonResponse(response)


class AddDocToCollect(View):
    def addDocToCollect(self, userId, projectId, docId):
        """
        Date        :   2025/4/19
        Author      :   yanfan
        Description :   将文档添加到用户收藏夹
        """
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        DBG("param" + str(locals()))
        response = getResp(0, "get addDocToCollect ok")
        project = isProjectExists(projectId)
        if project == None:
            return genResponseStateInfo(response, 1, "project does not exists")
        userProject = isUserInProject(userId, projectId)
        if userProject == None:
            return genResponseStateInfo(response, 2, "user not in project")
        docprev = UserCollectDoc.objects.filter(user_id=userId, doc_id=docId)
        if len(docprev) > 0:
            return genResponseStateInfo(response, 3, "doc already in collect")
        UserCollectDoc(user_id=User.objects.get(id=userId), doc_id=Document.objects.get(id=docId)).save()
        return response

    def post(self, request):
        """
        Date        :   2025/4/19
        Author      :   yanfan
        Description :   将文档添加到用户收藏夹
        """
        response = {"message": "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        try:
            response = self.addDocToCollect(kwargs.get("userId"), kwargs.get("projectId"), kwargs.get("docId"))
        except Exception as e:
            return JsonResponse({"message": str(e), "errcode": -1})
        return JsonResponse(response)


class DelDocFromCollect(View):
    def delDocFromCollect(self, userId, projectId, docId):
        """
        Date        :   2025/4/19
        Author      :   yanfan
        Description :   删除用户收藏夹中的文档
        """
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        DBG("param" + str(locals()))
        response = getResp(0, "get delDocFromCollect ok")
        project = isProjectExists(projectId)
        if project == None:
            return genResponseStateInfo(response, 1, "project does not exists")
        userProject = isUserInProject(userId, projectId)
        if userProject == None:
            return genResponseStateInfo(response, 2, "user not in project")
        UserCollectDoc.objects.filter(user_id=userId, doc_id=docId).delete()
        return response

    def post(self, request):
        """
        Date        :   2025/4/19
        Author      :   yanfan
        Description :   删除用户收藏夹中的文档
        """
        response = getResp(-1, "404 not success")
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        try:
            response = self.delDocFromCollect(kwargs.get("userId"), kwargs.get("projectId"), kwargs.get("docId"))
        except Exception as e:
            return JsonResponse({"message": str(e), "errcode": -1})
        return JsonResponse(response)


class UserCreateDoc(View):
    def userCreateDoc(self, userId, projectId, name, outline, content, accessUserId):
        """
        Date        :   2025/4/19
        Author      :   yanfan
        Description :   创建文档
        """
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        DBG("param" + str(locals()))
        response = getResp(0, "get userCreateDoc ok")
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
        Document(name=name, outline=outline, content=content, project_id=project, user_id=user).save()
        doc = Document.objects.get(name=name, project_id=projectId, user_id=userId)
        for item in accessUserId:
            accessUser = User.objects.get(id=item)
            UserAccessDoc(user_id=accessUser, doc_id=doc).save()
        
        return response

    def post(self, request):
        """
        Date        :   2025/4/19
        Author      :   yanfan
        Description :   创建文档
        """
        try:
            kwargs: dict = json.loads(request.body)
        except Exception as e:
            return JsonResponse({"message": str(e), "errcode": -1})
        try:
            response = self.userCreateDoc(
                kwargs.get("userId"),
                kwargs.get("projectId"),
                kwargs.get("name"),
                kwargs.get("outline"),
                kwargs.get("content"),
                kwargs.get("accessUserId"),
            )
        except Exception as e:
            return JsonResponse({"message": str(e), "errcode": -1})
        return JsonResponse(response)


class UserEditDocOther(View):
    def userEditDocOther(self, userId, docId, projectId, name, accessUserId):
        """
        Date        :   2025/4/19
        Author      :   yanfan
        Description :   修改文档
        """
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        DBG("param" + str(locals()))
        response = getResp(0, "get userEditDocOther ok")
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

    def post(self, request):
        """
        Date        :   2025/4/19
        Author      :   yanfan
        Description :   修改文档
        """
        try:
            kwargs: dict = json.loads(request.body)
        except Exception as e:
            return JsonResponse({"message": str(e), "errcode": -1})
        try:
            response = self.userEditDocOther(
                kwargs.get("userId"),
                kwargs.get("docId"),
                kwargs.get("projectId"),
                kwargs.get("name"),
                kwargs.get("accessUserId"),
            )
        except Exception as e:
            return JsonResponse({"message": str(e), "errcode": -1})
        return JsonResponse(response)


class UserEditDocContent(View):
    def userEditDocContent(self, userId, docId, projectId, content):
        """
        Date        :   2025/4/19
        Author      :   yanfan
        Description :   修改文档
        """
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        DBG("param" + str(locals()))
        response = getResp(0, "get userEditDocContent ok")
        project = isProjectExists(projectId)
        if project == None:
            return genResponseStateInfo(response, 1, "project does not exists")
        userProject = isUserInProject(userId, projectId)
        if userProject == None:
            return genResponseStateInfo(response, 2, "user not in project")
        if userProject.editAuth == UserProject.N:
            return genResponseStateInfo(response, 3, "no edit auth")
        Document.objects.filter(id=docId).update(content=content, time=datetime.datetime.now())
        return response

    def post(self, request):
        """
        Date        :   2025/4/19
        Author      :   yanfan
        Description :   修改文档
        """
        try:
            kwargs: dict = json.loads(request.body)
        except Exception as e:
            return JsonResponse({"message": str(e), "errcode": -1})
        try:
            response = self.userEditDocContent(
                kwargs.get("userId"), kwargs.get("docId"), kwargs.get("projectId"), kwargs.get("content")
            )
        except Exception as e:
            return JsonResponse({"message": str(e), "errcode": -1})
        return JsonResponse(response)


class UserGetDocLock(View):
    def userGetDocLock(self, userId, projectId, docId):
        """
        Date        :   2025/4/19
        Author      :   yanfan
        Description :   获取文档锁
        """
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        DBG("param" + str(locals()))
        response = {"message": "get userGetDocLock ok", "errcode": 0}
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

    def post(self, request):
        """
        Date        :   2025/4/19
        Author      :   yanfan
        Description :   获取文档锁
        """
        try:
            kwargs: dict = json.loads(request.body)
        except Exception as e:
            return JsonResponse({"message": str(e), "errcode": -1})
        try:
            response = self.userGetDocLock(kwargs.get("userId"), kwargs.get("projectId"), kwargs.get("docId"))
        except Exception as e:
            return JsonResponse({"message": str(e), "errcode": -1})
        return JsonResponse(response)


class UserReleaseDocLock(View):

    def userReleaseDocLock(self, userId, projectId, docId):
        """
        Date        :   2025/4/19
        Author      :   yanfan
        Description :   释放文档锁
        """
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        DBG("param" + str(locals()))
        response = getResp(0, "get userReleaseLock ok")
        project = isProjectExists(projectId)
        if project == None:
            return genResponseStateInfo(response, 1, "project does not exists")
        userProject = isUserInProject(userId, projectId)
        if userProject == None:
            return genResponseStateInfo(response, 2, "user not in project")

        UserDocLock.objects.filter(doc_id=docId, user_id=userId).delete()
        return response

    def post(self, request):
        """
        Date        :   2025/4/19
        Author      :   yanfan
        Description :   释放文档锁
        """
        try:
            kwargs: dict = json.loads(request.body)
        except Exception as e:
            return JsonResponse({"message": str(e), "errcode": -1})
        try:
            response = self.userReleaseDocLock(kwargs.get("userId"), kwargs.get("projectId"), kwargs.get("docId"))
        except Exception as e:
            return JsonResponse({"message": str(e), "errcode": -1})
        return JsonResponse(response)


class UserDelDoc(View):
    def userDelDoc(self, userId, projectId, docId):
        """
        Date        :   2025/4/19
        Author      :   yanfan
        Description :   删除文档
        """
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        DBG("param" + str(locals()))
        response = getResp(0, "get userDelDoc ok")
        project = isProjectExists(projectId)
        if project == None:
            return genResponseStateInfo(response, 1, "project does not exists")
        userProject = isUserInProject(userId, projectId)
        if userProject == None:
            return genResponseStateInfo(response, 2, "user not in project")
        Document.objects.filter(id=docId).delete()
        return response

    def post(self, request):
        """
        Date        :   2025/4/19
        Author      :   yanfan
        Description :   删除文档
        """
        try:
            kwargs: dict = json.loads(request.body)
        except Exception as e:
            return JsonResponse({"message": str(e), "errcode": -1})
        try:
            response = self.userDelDoc(kwargs.get("userId"), kwargs.get("projectId"), kwargs.get("docId"))
        except Exception as e:
            return JsonResponse({"message": str(e), "errcode": -1})
        return JsonResponse(response)


class DocTimeUpdate(View):
    def docTimeUpdate(self, userId, projectId, docId, updateTime):
        """
        Date        :   2025/4/19
        Author      :   yanfan
        Description :   更新文档时间
        """
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        DBG("param" + str(locals()))
        response = getResp(0, "get docTimeUpdate ok")
        project = isProjectExists(projectId)
        if project == None:
            return genResponseStateInfo(response, 1, "project does not exists")
        userProject = isUserInProject(userId, projectId)
        if userProject == None:
            return genResponseStateInfo(response, 2, "user not in project")
        Document.objects.filter(id=docId).update(time=updateTime)
        return response

    def post(self, request):
        """
        Date        :   2025/4/19
        Author      :   yanfan
        Description :   更新文档时间
        """
        try:
            kwargs: dict = json.loads(request.body)
        except Exception as e:
            return JsonResponse({"message": str(e), "errcode": -1})
        try:
            response = self.docTimeUpdate(
                kwargs.get("userId"), kwargs.get("projectId"), kwargs.get("docId"), kwargs.get("updateTime")
            )
        except Exception as e:
            return JsonResponse({"message": str(e), "errcode": -1})
        return JsonResponse(response)


class IsDocLocked(View):
    def post(self, request):
        """
        Date        :   2025/4/19
        Author      :   yanfan
        Description :   判断文档是否被锁定
        """
        try:
            kwargs: dict = json.loads(request.body)
        except Exception as e:
            return JsonResponse({"message": str(e), "errcode": -1})
        docId = kwargs.get("docId")
        o = UserDocLock.objects.filter(doc_id=docId)
        response = getResp(0, "get isDocLocked ok")
        response["isLocked"] = True
        if len(o) == 0:
            response["isLocked"] = False
        return JsonResponse(response)
