import json
import os

from django.http import FileResponse
from django.views import View
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from myApp.models import Project, MyFile
from myApp.utils.format.request import getResp


SUCCESS             = 0
DEFAULT_ERR_CODE    = 1
PROJECT_NOT_FOUND   = 2
FILE_NOT_FOUND      = 3

class uploadFile(View):
    '''
        Date        :   2025/4/18
        Author      :   tangling
        Description :   上传文件
    '''
    def post(self, request):
        # define the default failure response
        response = getResp()

        # get project_id from post request
        project_id = request.POST.get("project_id")

        # check if there is any project corresponding with the target project id
        if Project.objects.filter(id = project_id).count() == 0:
            response = getResp(
                errcode  = PROJECT_NOT_FOUND,
                message  = "project not exist"
            )
            return JsonResponse(response)

        # check if there is any files to upload
        file = request.FILES.get("file", None)
        if file is None:
            response = getResp(
                errcode  = FILE_NOT_FOUND,
                message  = "file not exist"
            )
            return JsonResponse(response)

        # formally upload the file
        # target folder_path : myApp/files/{project_id}
        folder_path = os.path.join("myApp/files", project_id)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        path = "myApp/files/%s/%s" % (project_id, file.name)
        with open(path, 'wb+') as f:
            # write in files in chunks
            for chunk in file.chunks():
                f.write(chunk)
        file = MyFile.objects.create(project_id_id = project_id, path = path,
                                    name = file.name)
        file.save()
        response = getResp(
            errcode  = SUCCESS,
            message  = "success"
        )
        return JsonResponse(response)

class downloadFile(View):
    '''
        Date        :   2025/4/18
        Author      :   tangling
        Description :   下载文件
    '''
    def post(self, request):
        response = getResp()
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)

        project_id = kwargs.get("project_id", -1)
        if Project.objects.filter(id=project_id).count() == 0:
            response = getResp(
                errcode  = PROJECT_NOT_FOUND,
                message  = "project not exist"
            )
            return JsonResponse(response)

        file_name = kwargs.get("fileName")
        try:
            file = MyFile.objects.get(project_id_id=project_id, name=file_name)
            file = open(file.path, 'rb')
            response = FileResponse(file, content_type='application/octet-stream')
            response['fileName'] = f'attachment; filename="{file.name}"'
            return response
        except ObjectDoesNotExist:
            response = getResp(
                errcode  = FILE_NOT_FOUND,
                message  = "file not exist"
            )
            return JsonResponse(response)


class watchFiles(View):
    '''
        Date        :   2025/4/18
        Author      :   tangling
        Description :   阅读文件
    '''
    def post(self, request):
        response = getResp()
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)

        project_id = kwargs.get("project_id", -1)
        if Project.objects.filter(id=project_id).count() == 0:
            response = getResp(
                errcode  = PROJECT_NOT_FOUND,
                message  = "project not exist"
            )
            return JsonResponse(response)

        files = MyFile.objects.filter(project_id_id=project_id)
        response = getResp(
            errcode  = SUCCESS,
            message  = "success"
        )
        response['data'] = []
        for file in files:
            response['data'].append({"name": file.name, "path": file.path})
        return JsonResponse(response)
