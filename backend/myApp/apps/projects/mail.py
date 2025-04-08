import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from djangoProject.settings import DBG 
import sys

jihubemail_addr = "jihubserver@163.com" # 邮箱地址
jihubemail_pw = "JiHub123" # 邮箱密码
imap_smtp_pw = "OKDMSQZPUHMDKBXD" # 邮箱 imap/smtp 服务密码

# title : 邮件名
# content : 邮件内容
# recv_name : 收件人昵称，建议为收件人在 jihub 中的用户名
# recv_email : 收件人邮箱地址，如 "20373696@buaa.edu.cn"
def mail(title, content, recv_name, recv_email):
  DBG("---- in " + sys._getframe().f_code.co_name + " ----")
  DBG("param" + str(locals()))
  ret = True
  try:
    msg = MIMEText(content,'plain','utf-8')
    msg['From'] = formataddr(["JiHub" , jihubemail_addr]) # 括号里的对应发件人邮箱昵称、发件人邮箱账号
    msg['To'] = formataddr([recv_name , recv_email]) # 括号里的对应收件人邮箱昵称、收件人邮箱账号
    msg['Subject'] = title # 邮件的主题，也可以说是标题
 
    server=smtplib.SMTP_SSL("smtp.163.com", 465)  # 发件人邮箱中的SMTP服务器，端口是 465
    server.login(jihubemail_addr, imap_smtp_pw)  # 括号中对应的是发件人邮箱账号、邮箱密码
    server.sendmail(jihubemail_addr,[recv_email,],msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
    server.quit()  # 关闭连接
  except Exception:
    DBG("send mail fail!")
    ret=False
  return ret

# 参考：
# ret=mail("jihubtest", "this is jihubtest", "ghy", "20373696@buaa.edu.cn")
# if ret:
#     print("邮件发送成功")
# else:
#     print("邮件发送失败")


# mail test api

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

class MailTest(View):
  def post(self, request):
    response = {'message': "404 not success", "errcode": -1}
    try:
      kwargs: dict = json.loads(request.body)
    except Exception:
      return JsonResponse(response)
    try:
      state = mail(kwargs.get('title'), kwargs.get('content'), kwargs.get('recv_name'), kwargs.get('recv_email'))
    except Exception as e:
      return JsonResponse({'message': str(e), "errcode": -1}) 
    return JsonResponse({'message': str(state), "errcode": 0})