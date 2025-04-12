

import requests

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


def load_prior_knowledge(id):
    pass