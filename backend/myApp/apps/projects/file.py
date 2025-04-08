from django.http import HttpResponse
from django.http import StreamingHttpResponse, FileResponse
import json
from django.views import View
from django.http import JsonResponse
from myApp.models import *
from django.core.exceptions import ObjectDoesNotExist
import os


class uploadFile(View):
    def post(self, request):
        response = {'errcode': 1, 'message': "404 not success"}

        projectId = request.POST.get("projectId")
        print(projectId)
        if Project.objects.filter(id=projectId).count() == 0:
            response['errcode'] = projectId
            response['message'] = "project not exist"
            return JsonResponse(response)

        File = request.FILES.get("file", None)
        if File is None:
            response['errcode'] = 2
            response['message'] = "file not exist"
            return JsonResponse(response)
        else:
            folder_path = os.path.join("myApp/files", projectId)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            path = "myApp/files/%s/%s" % (projectId, File.name)
            with open(path, 'wb+') as f:
                # 分块写入文件;
                for chunk in File.chunks():
                    f.write(chunk)
            file = MyFile.objects.create(project_id_id=projectId, path=path, name=File.name)
            file.save()
            response['errcode'] = 0
            response['message'] = "success"
            return JsonResponse(response)


def file_iterator(file, chunk_size=512):
    with open(file) as f:
        while True:
            c = f.read(chunk_size)
            if c:
                yield c
            else:
                break


class downloadFile(View):
    def post(self, request):
        response = {'errcode': 0, 'message': "404 not success"}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)

        projectId = kwargs.get("projectId", -1)
        if Project.objects.filter(id=projectId).count() == 0:
            response['errcode'] = 1
            response['message'] = "project not exist"
            return JsonResponse(response)

        file_name = kwargs.get("fileName")
        try:
            file = MyFile.objects.get(project_id_id=projectId, name=file_name)
            file = open(file.path, 'rb')
            response = FileResponse(file, content_type='application/octet-stream')
            response['fileName'] = f'attachment; filename="{file.name}"'
            return response
        except ObjectDoesNotExist:
            response['errcode'] = 1
            response['message'] = "file not exist"
            return JsonResponse(response)


class watchFiles(View):
    def post(self, request):
        response = {'errcode': 0, 'message': "404 not success"}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)

        projectId = kwargs.get("projectId", -1)
        if Project.objects.filter(id=projectId).count() == 0:
            response['errcode'] = 1
            response['message'] = "project not exist"
            return JsonResponse(response)

        files = MyFile.objects.filter(project_id_id=projectId)
        response['errcode'] = 0
        response['message'] = "success"
        response['data'] = []
        for file in files:
            response['data'].append({"name": file.name, "path": file.path})
        return JsonResponse(response)
