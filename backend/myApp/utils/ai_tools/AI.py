import subprocess

import os
from django.http import JsonResponse
from django.views import View
import json
import datetime
from djangoProject.settings import BASE_DIR
from myApp.models import *
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, SummarizationPipeline


import re
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

        pre_prompt = "generate code with following instruction: "
        post_prompt = "Your response must strictly follows rules below: " \
            "1. you should only generate code without any other additional information" \
            "2. your response must follow the format <start> code <end>"

        reply = code_expert_generate(pre_prompt + text + post_prompt)

        reply = ''.join(re.findall(r'<start>(.*?)<end>', reply, re.DOTALL))

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

        prefix = "please help me analyze the following code, and generate code review briefly. 请使用中文进行回复\n"

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

        pre_prompt = "Please generate unit test for the following code: "
        
        post_prompt = "Your response must strictly follows rules below: " \
            "1. you should only generate code without any other additional information" \
            "2. your response must follow the format <start> code <end>" \

        reply = code_expert_generate(pre_prompt + text + post_prompt)

        reply = ''.join(re.findall(r'<start>(.*?)<end>', reply, re.DOTALL))

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

        prompt_stage_1 = "请使用中文进行回复 Please summarize the following contexts briefly as possible"
        summary = simple_llm_generate(prompt_stage_1 + text)

        prompt_stage_2 = "请使用中文进行回复 Given the summary of a discussion, you should refine and transform it by Question-Answer pair format. " \
        "We wish the response belikes multi-turns conversation, " \
        "please explicitly use signals like <Question>, <Answer> and <end> to represent the start and end" \
        "Hence, your answer should follows: " \
        "<Question>: sth. <end> <Answer>: sth. <end> <Question>: sth. <end> <Answer>: sth. <end> ..."
        qa_reply = simple_llm_generate(prompt_stage_2 + summary)

        qa_pairs = knowledge_formatting(qa_reply)
        # save_to_knowledge_database(pid, qa_pairs)
        print("#######")
        print(qa_reply)
        print("Get QA Pair", qa_pairs)
        print("#######")
        response = {'errcode': 0, 'reply': summary, 'qa_pairs':qa_pairs}
        return JsonResponse(response)


class SaveQAPairs(View):
    def post(self, request):
        response = {'errcode': 1, 'message': "Save failed"}

        try:
            kwargs: dict = json.loads(request.body)
        except Exception as e:
            response['message'] = f"Invalid JSON: {str(e)}"
            return JsonResponse(response)

        try:
            pid = kwargs.get("pid")
            qa_pairs = kwargs.get("qa_pairs")
            if not pid or not qa_pairs:
                raise ValueError("Missing pid or qa_pairs")
        except Exception as e:
            response['message'] = f"Invalid keys: {str(e)}"
            return JsonResponse(response)

        try:
            save_to_knowledge_database(pid, qa_pairs)
        except Exception as e:
            response['message'] = f"Database error: {str(e)}"
            return JsonResponse(response)

        response = {'errcode': 0, 'message': "Save successful"}
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
            print("this is kwargs: ", kwargs)
            text = kwargs.get("message")
            prefixs = kwargs.get("context")
            
            pid = kwargs.get("pid")
            # cur_mask = '111'
            cur_mask = kwargs.get("cur_mask") # 3-bits, str, 当前项目代码 / 该项目的用户手册 / 该项目相关知识库
            if len(cur_mask) == 0:
                cur_mask = '000'
            cur_mask_list = list(cur_mask)
            print("this is cur_mask_list: ", cur_mask_list)
        except Exception:
            response = {'errcode': 1, 'message': "keys not found"}
            return JsonResponse(response)

        valid_prefixs = context_decode(prefixs) if len(prefixs) > 0 else []

        # valid_prefixs = []
        # for msg in prefixs:
        #     if "content" in msg and msg["content"].strip():
        #         valid_prefixs.append(msg)
        #     else:
        #         print(f"警告：跳过空内容消息: {msg}")

        decision = " <要求>: 对于新问题，是否需要除了当前上下文以外的内容？你需要且仅可以输出一个3位二进制掩码，这三位分别对应阅读当前项目代码、AutoHub项目的用户手册（问到AutoHub有关的任何问题时代表需要它）、该项目相关知识库（当你发现一些名词，你有极大可能会在知识库中找到相关内容！！），1代表需要，0代表不需要，例如，你需要代码、不需要用户手册、需要项目相关知识库，如果你可以直接完成这个任务，则输出000即可，如果你需要其中任何一项内容，则将对应位置置为1，请不要产出任何其他输出，只需要输出这个三bit掩码！！！"
        print("this is decision: ", text + decision)
        print("this is prefixs: ", valid_prefixs)
        mask, _ = memorized_llm_make_decision(text + decision, valid_prefixs)

        if len(prefixs) == 0:
            prefixs = []

        print("mask from llm", mask)

        # # TODO check
        # if len(prefixs) == 0:
        #     if pid != -1:
        #         prefixs = load_knowledge_formatting_conversation(pid)
        #     else:
        #         pass
        # else:
        #     prefixs = context_decode(prefixs)
        if int(mask[0]) == 1 and cur_mask_list[0] == '0': # code
            # code = read_r_files(pid)

            root='/home/auto/AutoHub/backend/userRepos'
            try:
                proj = Project.objects.get(id=pid)
            except Project.DoesNotExist:
                print(f"Project with id {pid} does not exist.")
                return ""

            user_repo_entries = UserProjectRepo.objects.filter(project_id=proj)
            for entry in user_repo_entries:
                user = entry.user_id.id
                repo = entry.repo_id.name

            # pwd = UserProjectRepo.objects.filter(project_id=project_id)
            # pwd = os.path.join(root, 'user'+str(user), repo, 'backend/myApp/utils/ai_tools/')
            pwd = os.path.join(root, 'user'+str(user), repo)
            print(f'finding {pwd}')
            code = print_tree(pwd)

            # 确保代码内容不为空
            if not code or not code.strip():
                code = "项目代码为空或不可用"
            valid_prefixs.append({"role": "user", "content": code})
            cur_mask_list[0] = '1'
        if int(mask[1]) == 1 and cur_mask_list[1] == '0': # user instruction
            # pass
            file_info = prepare_file()
            valid_prefixs.append(file_info)
            cur_mask_list[1] = '1'
        if int(mask[2]) == 1 and cur_mask_list[2] == '0': # knowledge
            knowledge = load_knowledge_formatting_conversation(pid)
            for info in knowledge:
                valid_prefixs.append(info)
            cur_mask_list[2] = '1'

        pre_prompt = "请使用中文进行回复 Please refer to the previous discussion and generate corresponding answer for question: "

        reply, context = memorized_llm_generate(pre_prompt + text, valid_prefixs)
        cur_mask_str = ''.join(cur_mask_list)
        
        response = {'errcode': 0, "reply": reply, "context": context_encode(context), 'cur_mask': cur_mask_str}
        print(f"this is response: 这是回复：{response}")
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

