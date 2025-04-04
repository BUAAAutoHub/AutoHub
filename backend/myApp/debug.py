import struct

from django.http import JsonResponse, HttpResponse
from django.core import serializers

from myApp.models import *
from djangoProject.settings import DBG, USER_REPOS_DIR, BASE_DIR
import json
import os
import shutil
import sys
from myApp.userdevelop import genResponseStateInfo, genUnexpectedlyErrorInfo
import random


def echo(request):
  DBG("---- in " + sys._getframe().f_code.co_name + " ----")
  kwargs: dict = json.loads(request.body)
  # body = json.loads(request.POST)
  response = {}
  # echo_log = open(os.path.join(BASE_DIR, "echo.log"), "a")
  # print(json.dumps(body), file=echo_log) 
  # echo_log.close()
  response["request-headers"] = str(request.headers)
  response["request-scheme"] = str(request.scheme)
  response["request-method"] = str(request.method)
  response["request-absolute_uri"] = str(request.build_absolute_uri())
  response["request-body"] = kwargs
  return JsonResponse(response)
