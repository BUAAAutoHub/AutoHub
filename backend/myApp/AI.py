import subprocess

import openai
import requests
from openai import OpenAI
import os
from django.http import JsonResponse
from django.views import View
import json
import datetime

from myApp.models import *
from myApp.userdevelop import genResponseStateInfo, isUserInProject, isProjectExists, is_independent_git_repository, \
    genUnexpectedlyErrorInfo, validate_token
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, SummarizationPipeline
import nltk
from nltk.tokenize import WordPunctTokenizer

pipeline = None
os.environ['GH_TOKEN'] = 'ghp_123456'


def load_codeTrans_model():
    global pipeline
    if pipeline is None:
        # model_path = "/home/ptwang/Code/SE-SMP-backend/myApp/codeTrans/base/"
        model_path = "/root/project/SE-SMP-backend/myApp/codeTrans/base/"
        print("model path:", model_path)
        pipeline = SummarizationPipeline(
            model=AutoModelForSeq2SeqLM.from_pretrained(model_path),
            tokenizer=AutoTokenizer.from_pretrained(model_path),
            device="cpu"
        )


# openai.organization = "org-fBoqj45hvJisAEGMR5cvPnDS"
api_key = "sk-proj-123456"

text = """class getEmail(View):
    def post(self, request):
        response = {'errcode': 0, 'message': "404 not success"}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)

        peopleId = kwargs.get("personId", -1)
        if User.objects.filter(id=peopleId).count() == 0:
            response['errcode'] = 1
            response['message'] = "user not exist"
            return JsonResponse(response)

        user = User.objects.get(id=peopleId)
        email = str(user.email)
        response['errcode'] = 0
        response['message'] = "success"
        response['data'] = email
        return JsonResponse(response)"""


# model = openai.ChatCompletion.create(
#     model="gpt-3.5-turbo",
#     messages=[
#         {"role": "system", "content": "You are a helpful assistant."},
#         {"role": "user", "content": "请针对以下代码给我生成单元测试代码," + text+", speak English"},
#     ]
# )
# print(model)

def request_trash(messages):
    url = 'https://api.zhizengzeng.com/v1/chat/completions'

    headers = {

        'Content-Type': 'application/json',

        'Authorization': 'Bearer sk-123456'
    }

    data = {

        "model": "gpt-3.5-turbo",

        "messages": messages,

        "stream": False

    }

    response = requests.post(url, json=data, headers=headers)

    return response.json()


class UnitTest(View):
    def post(self, request):
        response = {'errcode': 0, 'message': "404 not success"}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)

        text = kwargs.get("code")

        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user",
             "content": "Please generate unit test code for the following code: " + text +
                        ", and provide the tests in English."}]
        chat = request_trash(messages)
        if "error" in chat:
            error_message = chat['error'].get('message', 'Unknown error')
            response['errcode'] = -1
            response['message'] = f"Error from service: {error_message}"
            return JsonResponse(response)
        response['errcode'] = 0
        response['message'] = "success"
        response['data'] = chat["choices"][0]["message"]["content"]
        return JsonResponse(response)


class CodeReview(View):
    def post(self, request):
        response = {'errcode': 0, 'message': "404 not success"}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)

        text = kwargs.get("code")
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user",
             "content": "Please analyze the following code: " + text + ", and provide the analysis in English"},
        ]
        chat = request_trash(messages)
        if "error" in chat:
            error_message = chat['error'].get('message', 'Unknown error')
            response['errcode'] = -1
            response['message'] = f"Error from service: {error_message}"
            return JsonResponse(response)
        response['errcode'] = 0
        response['message'] = "success"
        response['data'] = chat["choices"][0]["message"]["content"]

        return JsonResponse(response)


class GenerateCommitMessage(View):
    def post(self, request):
        response = {'errcode': 0, 'message': "404 not success"}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        userId = kwargs.get('userId')
        projectId = kwargs.get('projectId')
        repoId = kwargs.get('repoId')
        branch = kwargs.get('branch')
        files = kwargs.get('files')
        project = isProjectExists(projectId)
        if project == None:
            return JsonResponse(genResponseStateInfo(response, 1, "project does not exists"))
        userProject = isUserInProject(userId, projectId)
        if userProject == None:
            return JsonResponse(genResponseStateInfo(response, 2, "user not in project"))
        if not UserProjectRepo.objects.filter(project_id=projectId, repo_id=repoId).exists():
            return JsonResponse(genResponseStateInfo(response, 3, "no such repo in project"))
        repo = Repo.objects.get(id=repoId)

        user = User.objects.get(id=userId)
        token = user.token
        if repo == None:
            return JsonResponse(genResponseStateInfo(response, 4, "no such repo"))
        try:
            localPath = repo.local_path
            remotePath = repo.remote_path
            print(localPath)
            print("is git :", is_independent_git_repository(localPath))
            if not is_independent_git_repository(localPath):
                return JsonResponse(genResponseStateInfo(response, 999, " not git dir"))
            if validate_token(token):
                subprocess.run(["git", "checkout", branch], cwd=localPath, check=True)
                # subprocess.run(["git", "remote", "add", "tmp", f"https://{token}@github.com/{remotePath}.git"],
                #                cwd=localPath)
                # subprocess.run(['git', 'pull', f'{branch}'], cwd=localPath)
                print(1111)
                for file in files:
                    path = os.path.join(localPath, file.get('path'))
                    print(2222)
                    content = file.get('content')
                    print("$$$$$$$$$$ modify file ", path, content)
                    try:
                        with open(path, 'w') as f:
                            f.write(content)
                    except Exception as e:
                        print(f"Failed to overwrite file {path}: {e}")
                diff = subprocess.run(["git", "diff"], cwd=localPath, capture_output=True,
                                      text=True, check=True)
                print("diff is :", diff.stdout)
                if diff.stdout is None:
                    return JsonResponse(genResponseStateInfo(response, 7, "you have not modify file"))
                subprocess.run(["git", "reset", "--hard", "HEAD"], cwd=localPath, check=True)
                # subprocess.run(["git", "remote", "rm", "tmp"], cwd=localPath)
            else:
                return JsonResponse(genResponseStateInfo(response, 6, "wrong token with this user"))
        except Exception as e:
            subprocess.run(["git", "reset", "--hard", "HEAD"], cwd=repo.local_path, check=True)
            return JsonResponse(genUnexpectedlyErrorInfo(response, e))

        # messages = [
        #     {"role": "system", "content": "You are a helpful assistant."},
        #     {"role": "user", "content": "请针对以下git diff内容,为此次commit生成一些合适的message," +
        #                                 diff.stdout + ", speak English"},
        # ]
        # chat = request_trash(messages)

        load_codeTrans_model()
        nltk.data.path.append("/root/project/SE-SMP-backend/myApp/codeTrans/tokenizers/")
        # nltk.data.path.append("/home/ptwang/Code/SE-SMP-backend/myApp/codeTrans/tokenizers/")  # check here
        tokenized_list = WordPunctTokenizer().tokenize(diff.stdout)
        tokenized_code = ' '.join(tokenized_list)
        print("tokenized code: " + tokenized_code)
        # 进行摘要生成
        output = pipeline([tokenized_code])
        print(output[0]['summary_text'])

        response['errcode'] = 0
        response['message'] = "success"
        # response['data'] = chat["choices"][0]["message"]["content"]
        response['data'] = output[0]['summary_text']
        return JsonResponse(response)


class GenerateLabel(View):
    def post(self, request):
        response = {'errcode': 0, 'message': "404 not success"}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        outline = kwargs.get('outline')
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user",
             "content": "Given the following description: " + outline +
                        "\n, select appropriate tags from the following list to summarize it: "
                        "bug, documentation, duplicate, enhancement, good first issue, help wanted, invalid, question, wontfix"},
        ]
        chat = request_trash(messages)
        print(chat, "*******", "error" in chat)
        if "error" in chat:
            error_message = chat['error'].get('message', 'Unknown error')
            response['errcode'] = -1
            response['message'] = f"Error from service: {error_message}"
            return JsonResponse(response)
        response['errcode'] = 0
        response['message'] = "success"
        response['data'] = chat["choices"][0]["message"]["content"]
        return JsonResponse(response)
