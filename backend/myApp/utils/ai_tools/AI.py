import subprocess

import os
from django.http import JsonResponse
from django.views import View
import json
import datetime
from djangoProject.settings import BASE_DIR
from myApp.models import *
from myApp.utils.projects.userdevelop import genResponseStateInfo, isUserInProject, isProjectExists, is_independent_git_repository, \
    genUnexpectedlyErrorInfo, validate_token
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, SummarizationPipeline
import nltk
from nltk.tokenize import WordPunctTokenizer

from myApp.models import *
from myApp.utils.ai_tools.ai_utils import *
from myApp.utils.projects.userChat import get_room_content_api

pipeline = None
os.environ['GH_TOKEN'] = 'ghp_123456'


'''
    urls:
    path("api/ai/prompt", AI.PromptGenerateCode.as_view()),
    path("api/ai/codeReview", AI.GenerateCodeReview.as_view()),
    path("api/ai/unitTest", AI.GenerateUnitTest.as_view()),
    path("api/ai/summary", AI.SummarizeDiscussion.as_view()),
    path("api/ai/chat", AI.ChatWithProjectExpert.as_view()),
    path("api/ai/generateLabel", AI.GenerateLabelwithDiscription.as_view()),
'''


def load_codeTrans_model():
    global pipeline
    if pipeline is None:
        model_path = BASE_DIR + "/myApp/codeTrans/base/"
        print("model path:", model_path)
        pipeline = SummarizationPipeline(
            model=AutoModelForSeq2SeqLM.from_pretrained(model_path),
            tokenizer=AutoTokenizer.from_pretrained(model_path),
            device="cpu"
        )


'''
    path("api/ai/prompt", AI.PromptGenerateCode.as_view()),
    返回: response('answer')
'''
class PromptGenerateCode(View):
    def post(self, request):
        response = {'errcode': 1, 'message': "404 not success"}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        
        text = kwargs.get("message")

        reply = simple_llm_generate(text)

        response = {'errcode': 0, 'reply': reply}

        return JsonResponse(response)

'''
    path("api/ai/codeReview", AI.GenerateCodeReview.as_view()),
'''
class GenerateCodeReview(View):
    def post(self, request):
        response = {'errcode': 1, 'message': "404 not success"}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        
        text = kwargs.get("code")

        prefix = "please help me analyze the following code, and generate code review briefly.\n"

        reply = simple_llm_generate(prefix + text)
        print(f"{reply}!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        response = {'errcode': 0, 'data': reply}

        return JsonResponse(response)


'''
    path("api/ai/unitTest", AI.GenerateUnitTest.as_view()),
'''
class GenerateUnitTest(View):
    def post(self, request):
        response = {'errcode': 1, 'message': "404 not success"}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        
        text = kwargs.get("code")

        conditional_prompt = "Please generate unit test for the following code: "

        reply = simple_llm_generate(conditional_prompt + text)

        response = {'errcode': 0, 'reply': reply}

        return JsonResponse(response)


'''
    path("api/ai/summary", AI.SummarizeDiscussion.as_view()),
'''
class SummarizeDiscussion(View):
    def post(self, request):
        response = {'errcode': 1, 'message': "404 not success"}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
    
        try:
            pid = kwargs.get("pid")
            rid = kwargs.get("rid")
            uid = kwargs.get("uid")
        except Exception:
            response = {'errcode': 1, 'message': "keys not found"}
            return JsonResponse(response)

        user = User.objects.get(id=uid)

        text = get_room_content_api(rid, user)
        text = formatting_discussion_context(text)

        prompt_stage_1 = "Please summarize the following contexts briefly as possible"
        summary = simple_llm_generate(prompt_stage_1 + text)

        response = {'errcode': 0, 'reply': summary}

        prompt_stage_2 = "Given the summary of a discussion, you should refine and transform it by Question-Answer pair format. " \
        "We wish the response belikes multi-turns conversation, " \
        "please explicitly use signals like <Question>, <Answer> and <end> to represent the start and end" \
        "Hence, your answer should follows: " \
        "<Question>: sth. <end> <Answer>: sth. <end> <Question>: sth. <end> <Answer>: sth. <end> ..."
        qa_reply = simple_llm_generate(prompt_stage_2 + summary)

        qa_pairs = knowledge_formatting(qa_reply)
        save_to_knowledge_database(pid, qa_pairs)

        return JsonResponse(response)


'''
    path("api/ai/chat", AI.ChatWithProjectExpert.as_view()),
    支持多轮对话, 需要返回context
'''
class ChatWithProjectExpert(View):
    def post(self, request):
        response = {'errcode': 1, 'message': "404 not success"}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        
        try:
            text = kwargs.get("message")
            prefixs = kwargs.get("context")
            pid = kwargs.get("pid")
        except Exception:
            response = {'errcode': 1, 'message': "keys not found"}
            return JsonResponse(response)

        print(f"this is prefixs : {prefixs}===========")

        # TODO check
        if len(prefixs) == 0:
            if pid != -1:
                prefixs = load_knowledge_formatting_conversation(pid)
            else:
                pass
        else:
            prefixs = context_decode(prefixs)

        reply, context = memorized_llm_generate(text, prefixs)

        response = {'errcode': 0, "reply": reply, "context": context_encode(context)}
        print(response)
        return JsonResponse(response)


'''
    path("api/ai/generateLabel", AI.GenerateLabelwithDiscription.as_view()),
'''
class GenerateLabelwithDiscription(View):
    def post(self, request):
        response = {'errcode': 1, 'message': "404 not success"}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        text = kwargs.get('text')
        conditional_prompt_pre = "Given the following description: \n"
        conditional_prompt_post = "\nSelect appropriate tags from the following list to summarize it: " \
                        "bug, documentation, duplicate, enhancement, good first issue, help wanted, invalid, question, wontfix"

        reply = simple_llm_generate(conditional_prompt_pre + text + conditional_prompt_post)

        response = {'errcode': 0, 'reply': reply}

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


