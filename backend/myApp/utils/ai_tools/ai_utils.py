import json
import os
import time
from openai import OpenAI
import re
from myApp.models import *

'''
    deepseek: sk-bf1011f6dfbe4946a1946704535163d4
'''

def code_expert_generate(msg):
    # client = OpenAI(
    #         base_url="http://localhost:11434/v1",   
    #         api_key="ollama"
    # )

    # messages = [
    #     {"role": "system", "content": "You are an AI assistant."}
    # ]
    # messages.append({"role": "user", "content": msg})

    # response = client.chat.completions.create(
    #     model="qwen2.5-coder:7b",
    #     messages=messages,
    #     temperature=0.5,
    #     max_tokens=1024
    # )
    # reply = response.choices[0].message.content

    client = OpenAI(
            base_url="https://api.moonshot.cn/v1",   
            api_key="sk-mxIsBuUj47JLogq9NSWNaQtUD2CVEmia6vC9Dcnpq7A4d7ox"
    )
    
    messages = [
        {"role": "system", "content": "You are an AI assistant."}
    ]
    messages.append({"role": "user", "content": msg})

    response = client.chat.completions.create(
        model="moonshot-v1-8k",
        # model="deepseek-r1:7b",
        # model="llama3.2:3b", 
        messages=messages,
        temperature=0.5,
    )
    
    reply = response.choices[0].message.content

    return reply


def simple_llm_generate_3b(msg):
    client = OpenAI(
            base_url="http://localhost:11434/v1",   
            api_key="ollama"
    )

    messages = [
        {"role": "system", "content": "You are an AI assistant."}
    ]
    messages.append({"role": "user", "content": msg})

    response = client.chat.completions.create(
        model="llama3.2",
        messages=messages,
        temperature=0.5,
        max_tokens=1024
    )
    reply = response.choices[0].message.content

    return reply



def simple_llm_generate_1b(msg):
    client = OpenAI(
            base_url="http://localhost:11434/v1",   
            api_key="ollama"
    )

    messages = [
        {"role": "system", "content": "You are a code expert."}
    ]
    messages.append({"role": "user", "content": msg})

    response = client.chat.completions.create(
        model="llama3.2:1b",
        messages=messages,
        temperature=0.5,
        max_tokens=1024
    )
    reply = response.choices[0].message.content

    return reply


'''
    msg: str
    reply: str
'''
def simple_llm_generate(msg):
    messages = [
        {"role": "system", "content": "You are an AI assistant."}
    ]
    messages.append({"role": "user", "content": msg})

    try:
        client = OpenAI(
                base_url="https://api.moonshot.cn/v1",   
                api_key="sk-mxIsBuUj47JLogq9NSWNaQtUD2CVEmia6vC9Dcnpq7A4d7ox"
        )
        response = client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=messages,
            temperature=0.5,
        )
    except:
        try:
            print("KIMI failed! DS try!")
            client = OpenAI(
                    base_url="https://api.deepseek.com",   
                    api_key="sk-bf1011f6dfbe4946a1946704535163d4"
            )
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                temperature=0.5,
            )
        except:
            print("KIMI & DS failed! local Qwen instead")
            print("KIMI & DS failed! local Qwen instead")
            print("KIMI & DS failed! local Qwen instead")
            client = OpenAI(
                    base_url="http://localhost:11434/v1",   
                    api_key="ollama"
            )
            response = client.chat.completions.create(
                model="qwen2.5:14b",
                messages=messages,
                temperature=0.5,
            )
    
    reply = response.choices[0].message.content

    return reply


def memorized_llm_make_decision(msg, prefixs):
    messages = [
        {"role": "system", "content": "You are an AI assistant."}
    ]

    for prefix_msg in prefixs:
        messages.append(prefix_msg)

    messages.append({"role": "user", "content": msg})

    try:
        client = OpenAI(
                base_url="https://api.deepseek.com",   
                api_key="sk-bf1011f6dfbe4946a1946704535163d4"
        )
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0.5,
        )
    except:
        try:
            print("DS-reasoner failed! try KIMI!")
            client = OpenAI(
                    base_url="https://api.moonshot.cn/v1",   
                    api_key="sk-mxIsBuUj47JLogq9NSWNaQtUD2CVEmia6vC9Dcnpq7A4d7ox"
            )
            response = client.chat.completions.create(
                model="moonshot-v1-8k",
                messages=messages,
                temperature=0.5,
            )
        except:
            print("KIMI & DS failed! local Qwen instead")
            print("KIMI & DS failed! local Qwen instead")
            print("KIMI & DS failed! local Qwen instead")
            client = OpenAI(
                    base_url="http://localhost:11434/v1",   
                    api_key="ollama"
            )
            response = client.chat.completions.create(
                model="qwen2.5:14b",
                messages=messages,
                temperature=0.5,
            )
    
    reply = response.choices[0].message.content
    
    messages.append({"role": "assistant", "content": reply})

    messages.pop(0) # pop the system prompt

    return reply, messages




# TODO check
def memorized_llm_generate(msg, prefixs):
    messages = [
        {"role": "system", "content": "You are an AI assistant."}
    ]

    for prefix_msg in prefixs:
        messages.append(prefix_msg)

    messages.append({"role": "user", "content": msg})

    try:
        client = OpenAI(
                base_url="https://api.moonshot.cn/v1",   
                api_key="sk-mxIsBuUj47JLogq9NSWNaQtUD2CVEmia6vC9Dcnpq7A4d7ox"
        )
        response = client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=messages,
            temperature=0.5,
        )
    except:
        try:
            print("KIMI failed! DS try!")
            client = OpenAI(
                    base_url="https://api.deepseek.com",   
                    api_key="sk-bf1011f6dfbe4946a1946704535163d4"
            )
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                temperature=0.5,
            )
        except:
            print("KIMI & DS failed! local Qwen instead")
            print("KIMI & DS failed! local Qwen instead")
            print("KIMI & DS failed! local Qwen instead")
            client = OpenAI(
                    base_url="http://localhost:11434/v1",   
                    api_key="ollama"
            )
            response = client.chat.completions.create(
                model="qwen2.5:14b",
                messages=messages,
                temperature=0.5,
            )
    
    reply = response.choices[0].message.content
    
    messages.append({"role": "assistant", "content": reply})

    messages.pop(0) # pop the system prompt

    return reply, messages


'''
    <Question>: What is the capital of France? <end> <Answer>: Paris. <end>
    <Question>: What is 2 + 2? <end> <Answer>: 4. <end>
'''
def knowledge_formatting(text):
    # identify the <Question> <Answer> and save 
    pattern = r"<Question>:\s*(.*?)\s*<end>\s*<Answer>:\s*(.*?)\s*<end>"
    matches = re.findall(pattern, text, re.DOTALL)

    # 构建字典列表
    qa_list = [{"question": q.strip(), "answer": a.strip()} for q, a in matches]
    return qa_list


'''
    pid: project_id
    qa_pairs: return from knowledge_formatting
'''
# def save_to_knowledge_database(pid, qa_pairs):
#     proj = Project.objects.get(id=pid)
#     for pair in qa_pairs:
#         KnowledgeDatabase.objects.create(
#             project_id = proj,
#             question = pair['question'],
#             answer = pair['answer']
#         )


# def load_knowledge_formatting_qa(pid):
#     proj = Project.objects.get(id=pid)
    
#     knowledge_records = KnowledgeDatabase.objects.filter(project_id=proj)
#     result = [{"question": record.question, "answer": record.answer} for record in knowledge_records]

#     return result
    

def load_knowledge_formatting_conversation(pid):
    try:
        proj = Project.objects.get(id=pid)
    except Project.DoesNotExist:
        print(f"Project with id {pid} does not exist.")
        return []
    
    knowledge_records = KnowledgeDatabase.objects.filter(project_id=proj)
    # result = [{"user": record.question, "assistant": record.answer} for record in knowledge_records]

    result = []
    for record in knowledge_records:
        question = {"role": "user", "content": record.question}
        answer = {"role": "assistant", "content": record.answer}
        result.append(question)
        result.append(answer)

    return result

'''
    [
        {
            "role": "user",
            "content": "..."
        }
        {
            "role": "assistant",
            "content": "..."
        }
    ]

    "<role>...<end><content>...<end>"
'''
def context_encode(conversation) -> str:
    context = ""
    for msg in conversation:
        context += "<role>" + msg['role'] + "<end>"
        context += "<content>" + msg['content'] + "<end>"

    return context

def context_decode(conversation):
    pattern = r"<role>\s*(.*?)\s*<end>\s*<content>\s*(.*?)\s*<end>"
    matches = re.findall(pattern, conversation, re.DOTALL)

    context = [{"role": r.strip(), "content": c.strip()} for r, c in matches]
    return context

    
def formatting_discussion_context(context):
    '''
        messages = [
            {
                "content": message.content,
                "senderName": message.send_user.name,
                "senderId": message.send_user.id,
                "time": message.time,
            }
            for message in Message.objects.filter(group_id=roomId, receive_user=user)
        ]
    '''
    string = ""
    for msg in context:
        string += f"<start><user_{msg['senderId']}>:"
        string += f"{msg['content']}<end>"

    return string

'''
    LLM based on ollama, request api with OpenAI lib
    support multi-turns conversation
'''
class LocalLLM():
    def __init__(self):
        self.client = OpenAI(
            base_url="http://localhost:11434/v1",   # ollama API 地址
            api_key="ollama"                        # 可以是任意值
        )
        # init chat history
        self.messages = [
            {"role": "system", "content": "You are an AI assistant."}  # 可选：设置 AI 行为
        ]

    def load_knowledge(self, QApair):
        '''
            QApair = [
                {"question": "Sun is bigger than earth?", "anwser": "yes"},
                ...
            ]
        '''
        for qa in QApair:
            self.messages.append({"role": "user", "content": qa['question']})
            self.messages.append({"role": "assistant", "content": qa['answer']} )

    '''
        改成stream可能需要前端配合
    '''
    def chat(self, msg):
        self.messages.append({"role": "user", "content": msg})

        response = self.client.chat.completions.create(
            # model="llama3.2:1b",
            model="llama3.2", 
            # model="deepseek-r1:7b",
            messages=self.messages,
            temperature=0.5,
            max_tokens=1024
        )
        reply = response.choices[0].message.content

        self.messages.append({"role": "assistant", "content": reply})

        return reply
    
    def reset_history(self):
        self.messages = [
            {"role": "system", "content": "You are an AI assistant."} 
        ]
        

def load_knowledge_formatting_conversation(pid):
    try:
        proj = Project.objects.get(id=pid)
    except Project.DoesNotExist:
        print(f"Project with id {pid} does not exist.")
        return []
    knowledge_records = KnowledgeDatabase.objects.filter(project_id=proj)

    result = []
    for record in knowledge_records:
        question = {"role": "user", "content": record.question}
        answer = {"role": "assistant", "content": record.answer}
        result.append(question)
        result.append(answer)

    return result


def save_to_knowledge_database(pid, qa_pairs):
    """
    Date        : 2025/5/24
    Author      : sunyanfan
    Description : 保存知识到数据库，并导出为 JSON 文件
    """
    proj = Project.objects.get(id=pid)

    # 1. 保存到数据库
    for pair in qa_pairs:
        KnowledgeDatabase.objects.create(
            project_id=proj,
            question=pair['question'],
            answer=pair['answer']
        )

    # 2. 导出为 JSON 文件
    knowledge_list = load_knowledge_formatting_conversation(pid)
    folder_path = os.path.join("myApp/files", str(pid))
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    timestamp = int(time.time() * 1000)
    file_name = f"qa_knowledge-{timestamp}-0-0-0.json"
    file_path = os.path.join(folder_path, file_name)

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(knowledge_list, f, ensure_ascii=False, indent=2)

    # 3. 更新 MyFile 表
    file_obj, created = MyFile.objects.get_or_create(
        project_id_id=pid,
        name=file_name,
        defaults={"path": file_path}
    )
    if not created:
        file_obj.path = file_path
        file_obj.save()


def read_r_files(pid):
    root = '/home/auto/AutoHub/backend/userRepos'
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
    pwd = os.path.join(root, 'user'+str(user), repo, 'backend/myApp/utils/ai_tools/')
    print("this is pwd: ", pwd)
    result_string = ""

    # 递归读取文件夹
    for root, dirs, files in os.walk(pwd):
        print(f"正在访问文件夹: {root}")
        print(files)
        for file in files:
            
            file_path = os.path.join(root, file)
            
            if os.path.isfile(file_path):
                print(f"访问文件: {file_path}")
                try:
                    print("this is file_path: ", file_path)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        result_string += f"\n\n\n # {file_path} # \n\n\n"
                        result_string += f.read() + "\n"  # 每个文件的内容加到结果字符串中，并加换行
                        print(f"已读取文件: {file_path}")
                except Exception as e:
                    print(f"无法读取文件 {file_path}: {e}")
    # print(result_string)
    return result_string


def prepare_file():
    from pathlib import Path
    client = OpenAI(
            base_url="https://api.moonshot.cn/v1",   
            api_key="sk-mxIsBuUj47JLogq9NSWNaQtUD2CVEmia6vC9Dcnpq7A4d7ox"
    )
    path = '/home/auto/AutoHub/backend/myApp/files/11/AutoHub_用户手册-1747544699039-1-1-1.docx'

    # xlnet.pdf 是一个示例文件, 我们支持 pdf, doc 以及图片等格式, 对于图片和 pdf 文件，提供 ocr 相关能力
    file_object = client.files.create(file=Path(path), purpose="file-extract")
    
    # 获取结果
    # file_content = client.files.retrieve_content(file_id=file_object.id)
    # 注意，之前 retrieve_content api 在最新版本标记了 warning, 可以用下面这行代替
    # 如果是旧版本，可以用 retrieve_content
    file_content = client.files.content(file_id=file_object.id).text

    return {
        "role": "system",
        "content": file_content,
    }


def print_tree(pwd, level=0):

    result = ""
    for item in os.listdir(pwd):
        item_path = os.path.join(pwd, item)
        
        result += "    " * level + "|-- " + item
        
        if os.path.isdir(item_path):
            result += print_tree(item_path, level + 1)

    return result