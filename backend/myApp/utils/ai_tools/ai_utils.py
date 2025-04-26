from openai import OpenAI
import re
from myApp.models import KnowledgeDatabase, Project


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
        # model="llama3.2:1b",
        model="llama3.2:3b", 
        # model="deepseek-r1:7b",
        messages=messages,
        temperature=0.5,
        max_tokens=1024
    )
    reply = response.choices[0].message.content

    return reply


def memorized_llm_generate(msg, prefixs):
    client = OpenAI(
            base_url="http://localhost:11434/v1",   
            api_key="ollama"
    )

    messages = [
        {"role": "system", "content": "You are an AI assistant."}
    ]

    for prefix_msg in prefixs:
        messages.append({"role": "user", "content": prefix_msg['user']})
        messages.append({"role": "assistant", "content": prefix_msg['assistant']})

    messages.append({"role": "user", "content": msg})

    response = client.chat.completions.create(
        # model="llama3.2:1b",
        model="llama3.2:3b", 
        # model="deepseek-r1:7b",
        messages=messages,
        temperature=0.5,
        max_tokens=1024
    )
    reply = response.choices[0].message.content

    return reply


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


def load_knowledge_formating_qa(pid):
    proj = Project.objects.get(id=pid)
    
    knowledge_records = KnowledgeDatabase.objects.filter(project_id=proj)
    result = [{"question": record.question, "answer": record.answer} for record in knowledge_records]

    return result
    

def load_knowledge_formating_conversation(pid):
    proj = Project.objects.get(id=pid)
    
    knowledge_records = KnowledgeDatabase.objects.filter(project_id=proj)
    result = [{"user": record.question, "assistant": record.answer} for record in knowledge_records]

    return result
    

'''
    LLM based on Ollama, request with OpenAI lib
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
        