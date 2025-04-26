import smtplib
import sys
import json

from email.mime.text import MIMEText
from email.utils import formataddr
from django.http import JsonResponse
from django.views import View
from djangoProject.settings import DBG


JIHUB_EMAIL_ADDR    = "jihubserver@163.com" # 邮箱地址
JIHUB_EMAIL_PW      = "JiHub123"            # 邮箱密码
IMAP_SMTP_PW        = "OKDMSQZPUHMDKBXD"    # 邮箱 imap/smtp 服务密码

def mail(title, content, recv_name, recv_email):
    '''
        title       :   邮件名
        contenrt    :   邮件内容
        recv_name   :   收件人昵称
        recv_email  :   收件人邮箱地址，如 "123@buaa.edu.cn"
    '''
    DBG("---- in " + sys._getframe().f_code.co_name + " ----")
    DBG("param" + str(locals()))
    ret = True
    try:
        msg = MIMEText(content,'plain','utf-8')
        msg['From'] = formataddr(["JiHub" , JIHUB_EMAIL_ADDR]) # 括号里的对应发件人邮箱昵称、发件人邮箱账号
        msg['To'] = formataddr([recv_name , recv_email]) # 括号里的对应收件人邮箱昵称、收件人邮箱账号
        msg['Subject'] = title # 邮件的主题，也可以说是标题

        server=smtplib.SMTP_SSL("smtp.163.com", 465)  # 发件人邮箱中的SMTP服务器，端口是 465
        server.login(JIHUB_EMAIL_ADDR, IMAP_SMTP_PW)  # 括号中对应的是发件人邮箱账号、邮箱密码
        server.sendmail(JIHUB_EMAIL_ADDR,[recv_email,]
                        ,msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
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
class MailTest(View):
    def post(self, request):
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        try:
            state = mail(kwargs.get('title'), kwargs.get('content'),
                        kwargs.get('recv_name'), kwargs.get('recv_email'))
        except Exception as e:
            return JsonResponse({'message': str(e), "errcode": -1})
        return JsonResponse({'message': str(state), "errcode": 0})
