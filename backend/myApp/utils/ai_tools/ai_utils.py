from openai import OpenAI
import re
from myApp.models import *


'''
    msg: str
    reply: str
'''
def simple_llm_generate(msg):
    client = OpenAI(
            base_url="http://localhost:11434/v1",   
            api_key="ollama"
    )

    messages = [
        {"role": "system", "content": "You are an AI assistant."}
    ]
    messages.append({"role": "user", "content": msg})

    response = client.chat.completions.create(
        model="qwen2.5:14b",
        # model="llama3.2:1b",
        # model="deepseek-r1:7b",
        # model="llama3.2:3b",
        messages=messages,
        temperature=0.5,
        max_tokens=1024
    )
    reply = response.choices[0].message.content

    return reply

# TODO check
def memorized_llm_generate(msg, prefixs):
    client = OpenAI(
            base_url="http://localhost:11434/v1",   
            api_key="ollama"
    )

    messages = [
        {"role": "system", "content": "You are an AI assistant."}
    ]

    for prefix_msg in prefixs:
        messages.append(prefix_msg)
    # for prefix_msg in prefixs:
    #     messages.append({"role": "user", "content": prefix_msg['content']})
    #     messages.append({"role": "assistant", "content": prefix_msg['content']})

    messages.append({"role": "user", "content": msg})

    response = client.chat.completions.create(
        model="qwen2.5:14b",
        # model="llama3.2:1b",
        # model="deepseek-r1:7b",
        # model="llama3.2:3b", 
        messages=messages,
        temperature=0.5,
        max_tokens=1024
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
def save_to_knowledge_database(pid, qa_pairs):
    proj = Project.objects.get(id=pid)
    for pair in qa_pairs:
        KnowledgeDatabase.objects.create(
            project_id = proj,
            question = pair['question'],
            answer = pair['answer']
        )


# def load_knowledge_formatting_qa(pid):
#     proj = Project.objects.get(id=pid)
    
#     knowledge_records = KnowledgeDatabase.objects.filter(project_id=proj)
#     result = [{"question": record.question, "answer": record.answer} for record in knowledge_records]

#     return result
    

def load_knowledge_formatting_conversation(pid):
    proj = Project.objects.get(id=pid)
    
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
            model="llama3.2:3b", 
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
        