import subprocess

import os
from django.http import JsonResponse
from django.views import View
import json
import datetime
from djangoProject.settings import BASE_DIR
from myApp.models import *
from myApp.utils.projects.userdevelop import (
    genResponseStateInfo,
    isUserInProject,
    isProjectExists,
    is_independent_git_repository,
    genUnexpectedlyErrorInfo,
    validate_token,
)
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, SummarizationPipeline
import nltk
from nltk.tokenize import WordPunctTokenizer

from myApp.utils.ai_tools.ai_utils import *

pipeline = None


"""
    Models:
        代码分析 - API
        Label生成 - API
        Commit Msg生成 - codeTrans

    其实codeTrans能够执行的任务：
        1. 代码文档生成
        2. 代码摘要生成
        3. 代码评论生成
        4. Git提及信息生成
    ref: https://aclanthology.org/P18-1103.pdf
"""


def load_codeTrans_model():
    global pipeline
    if pipeline is None:
        model_path = BASE_DIR + "/myApp/codeTrans/base/"
        print("model path:", model_path)
        pipeline = SummarizationPipeline(
            model=AutoModelForSeq2SeqLM.from_pretrained(model_path),
            tokenizer=AutoTokenizer.from_pretrained(model_path),
            device="cpu",
        )


"""
    统一把用户端输入写到request['text']里面
    返回: response('answer')
"""


class PromptGenerateCode(View):
    def post(self, request):
        response = {"errcode": 0, "message": "404 not success"}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)

        text = kwargs.get("text")

        reply = simple_llm_generate(text)

        response = {"answer": reply}

        return JsonResponse(response)


class GenerateCodeReview(View):
    def post(self, request):
        response = {"errcode": 0, "message": "404 not success"}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)

        text = kwargs.get("text")

        reply = simple_llm_generate(text)

        response = {"answer": reply}

        return JsonResponse(response)


"""
    直接把讨论拼接成一个字符串传入即可
    'text' 讨论, 'pid' 项目id
"""


class SummarizeDiscussion(View):
    def post(self, request):
        response = {"errcode": 0, "message": "404 not success"}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)

        try:
            text = kwargs.get("text")
            pid = kwargs.get("pid")
        except Exception:
            response = {"errcode": 1, "message": "keys not found"}
            return JsonResponse(response)

        conditional_prompt = (
            "Please summarize the following contexts briefly and refine the response by Question-Answer pair. "
            "We wish the response belikes multi-turns conversation, "
            "please explicitly use signals like <Question> and <Answer> and use <end> to denotes it's finish."
            "Hence, your answer should follows: "
            "<Question>: sth. <end> <Answer>: sth. <end> <Question>: sth. <end> <Answer>: sth. <end> ..."
        )

        reply = simple_llm_generate(text + conditional_prompt)

        qa_pairs = knowledge_formatting(reply)
        save_to_knowledge_database(pid, qa_pairs)

        # save_to_database(reply)

        response = {"answer": reply}

        return JsonResponse(response)


"""
    'text' 问题, 'pid' 项目id
    有个问题：是否要支持多轮对话？
"""


class ChatWithProjectExpert(View):
    def post(self, request):
        response = {"errcode": 0, "message": "404 not success"}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)

        try:
            text = kwargs.get("text")
            pid = kwargs.get("pid")
        except Exception:
            response = {"errcode": 1, "message": "keys not found"}
            return JsonResponse(response)

        # prefixs = load_knowledge_formating_qa(pid)
        prefixs = load_knowledge_formating_conversation(pid)

        reply = memorized_llm_generate(text, prefixs)

        response = {"answer": reply}

        return JsonResponse(response)


class GenerateLabelwithDiscription(View):
    def post(self, request):
        response = {"errcode": 0, "message": "404 not success"}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        text = kwargs.get("text")
        conditional_prompt_pre = "Given the following description: "
        conditional_prompt_post = (
            "select appropriate tags from the following list to summarize it: "
            "bug, documentation, duplicate, enhancement, good first issue, help wanted, invalid, question, wontfix"
        )

        reply = simple_llm_generate(conditional_prompt_pre + text + conditional_prompt_post)

        response = {"answer": reply}

        return JsonResponse(response)


# class GenerateCommitMessage(View):
#     def post(self, request):
#         response = {'errcode': 0, 'message': "404 not success"}
#         try:
#             kwargs: dict = json.loads(request.body)
#         except Exception:
#             return JsonResponse(response)
#         userId = kwargs.get('userId')
#         projectId = kwargs.get('projectId')
#         repoId = kwargs.get('repoId')
#         branch = kwargs.get('branch')
#         files = kwargs.get('files')
#         project = isProjectExists(projectId)
#         if project == None:
#             return JsonResponse(genResponseStateInfo(response, 1, "project does not exists"))
#         userProject = isUserInProject(userId, projectId)
#         if userProject == None:
#             return JsonResponse(genResponseStateInfo(response, 2, "user not in project"))
#         if not UserProjectRepo.objects.filter(project_id=projectId, repo_id=repoId).exists():
#             return JsonResponse(genResponseStateInfo(response, 3, "no such repo in project"))
#         repo = Repo.objects.get(id=repoId)

#         user = User.objects.get(id=userId)
#         token = user.token
#         if repo == None:
#             return JsonResponse(genResponseStateInfo(response, 4, "no such repo"))
#         try:
#             localPath = repo.local_path
#             remotePath = repo.remote_path
#             print(localPath)
#             print("is git :", is_independent_git_repository(localPath))
#             if not is_independent_git_repository(localPath):
#                 return JsonResponse(genResponseStateInfo(response, 999, " not git dir"))
#             if validate_token(token):
#                 subprocess.run(["git", "checkout", branch], cwd=localPath, check=True)
#                 # subprocess.run(["git", "remote", "add", "tmp", f"https://{token}@github.com/{remotePath}.git"],
#                 #                cwd=localPath)
#                 # subprocess.run(['git', 'pull', f'{branch}'], cwd=localPath)
#                 print(1111)
#                 for file in files:
#                     path = os.path.join(localPath, file.get('path'))
#                     print(2222)
#                     content = file.get('content')
#                     print("$$$$$$$$$$ modify file ", path, content)
#                     try:
#                         with open(path, 'w') as f:
#                             f.write(content)
#                     except Exception as e:
#                         print(f"Failed to overwrite file {path}: {e}")
#                 diff = subprocess.run(["git", "diff"], cwd=localPath, capture_output=True,
#                                       text=True, check=True)
#                 print("diff is :", diff.stdout)
#                 if diff.stdout is None:
#                     return JsonResponse(genResponseStateInfo(response, 7, "you have not modify file"))
#                 subprocess.run(["git", "reset", "--hard", "HEAD"], cwd=localPath, check=True)
#                 # subprocess.run(["git", "remote", "rm", "tmp"], cwd=localPath)
#             else:
#                 return JsonResponse(genResponseStateInfo(response, 6, "wrong token with this user"))
#         except Exception as e:
#             subprocess.run(["git", "reset", "--hard", "HEAD"], cwd=repo.local_path, check=True)
#             return JsonResponse(genUnexpectedlyErrorInfo(response, e))

#         load_codeTrans_model()
#         nltk.data.path.append(BASE_DIR + "/myApp/codeTrans/tokenizers/")
#         # nltk.data.path.append("/home/ptwang/Code/SE-SMP-backend/myApp/codeTrans/tokenizers/")  # check here
#         tokenized_list = WordPunctTokenizer().tokenize(diff.stdout)
#         tokenized_code = ' '.join(tokenized_list)
#         print("tokenized code: " + tokenized_code)
#         # 进行摘要生成
#         output = pipeline([tokenized_code])
#         print(output[0]['summary_text'])

#         response['errcode'] = 0
#         response['message'] = "success"
#         # response['data'] = chat["choices"][0]["message"]["content"]
#         response['data'] = output[0]['summary_text']
#         return JsonResponse(response)


# class GenerateLabel(View):
#     def post(self, request):
#         response = {'errcode': 0, 'message': "404 not success"}
#         try:
#             kwargs: dict = json.loads(request.body)
#         except Exception:
#             return JsonResponse(response)
#         outline = kwargs.get('outline')
#         messages = [
#             {"role": "system", "content": "You are a helpful assistant."},
#             {"role": "user",
#              "content": "Given the following description: " + outline +
#                         "\n, select appropriate tags from the following list to summarize it: "
#                         "bug, documentation, duplicate, enhancement, good first issue, help wanted, invalid, question, wontfix"},
#         ]
#         chat = simple_request(messages)
#         print(chat, "*******", "error" in chat)
#         if "error" in chat:
#             error_message = chat['error'].get('message', 'Unknown error')
#             response['errcode'] = -1
#             response['message'] = f"Error from service: {error_message}"
#             return JsonResponse(response)
#         response['errcode'] = 0
#         response['message'] = "success"
#         response['data'] = chat["choices"][0]["message"]["content"]
#         return JsonResponse(response)
