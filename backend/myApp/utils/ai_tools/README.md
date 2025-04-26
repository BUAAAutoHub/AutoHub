# AI Tool Doc

## Code Analysis
API: https://api.zhizengzeng.com/v1/chat/completions

Prompt: You are a helpful assistant. Please analyze the following code and provide the analysis in English: {code}

```
request['code']
```

## Generate Commit Message

CodeTrans

```
request -> kwargs
userId = kwargs.get('userId')
projectId = kwargs.get('projectId')
repoId = kwargs.get('repoId')
branch = kwargs.get('branch')
files = kwargs.get('files')
```


## Generate Label
API: https://api.zhizengzeng.com/v1/chat/completions

Prompt: Given the following description {outline}, select appropriate tags from the following list to summarize it:

bug, documentation, duplicate, enhancement, good first issue, help wanted, invalid, question, wontfix

```
request['outline']
```