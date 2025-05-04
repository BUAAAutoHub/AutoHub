import json

from typing import List, Dict

from django.http import JsonResponse
from django.views import View
from myApp.utils.ai_tools.ai_utils import simple_llm_generate_3b
from myApp.models import BotLabel, BotRule
from myApp.utils.ai_tools.ai_utils import simple_llm_generate


DEFAULT_LABELS = [
    # 技术类
    {"name": "bug", "color": "#d73a4a", "description": "Something isn't working"},
    {"name": "enhancement", "color": "#a2eeef", "description": "New feature or improvement"},
    {"name": "documentation", "color": "#0075ca", "description": "Documentation changes"},
    {"name": "refactor", "color": "#7057ff", "description": "Code refactoring"},
    {"name": "dependencies", "color": "#0366d6", "description": "Dependency updates"},
    
    # 状态类
    {"name": "help wanted", "color": "#008672", "description": "Extra attention needed"},
    {"name": "good first issue", "color": "#7057ff", "description": "Good for newcomers"},
    {"name": "wontfix", "color": "#ffffff", "description": "Will not be fixed"},
    {"name": "duplicate", "color": "#cfd3d7", "description": "Duplicate issue"},
    
    # 优先级类
    {"name": "critical", "color": "#b60205", "description": "Highest priority issue"},
    {"name": "high priority", "color": "#ff9f1c", "description": "Urgent issue"},
    {"name": "low priority", "color": "#0e8a16", "description": "Low urgency issue"}
]

PR_RULES = [
    {
        "name": "title_check",
        "description": "检查PR标题是否规范",
        "prompt": "请检查这个PR标题是否规范：{title}。规范要求：1. 不能为空 2. 不能是默认值 3. 应该描述更改内容",
        "action": "comment"
    },
    {
        "name": "description_check",
        "description": "检查PR描述是否完整",
        "prompt": "请检查这个PR描述是否完整：{body}。要求：1. 不能为空 2. 至少50字 3. 包含更改目的和内容",
        "action": "comment"
    },
    {
        "name": "add_label",
        "description": "为PR打标签",
        "action": "label"                    
    }
]

ISSUE_RULES = [
    {
        "name": "title_check",
        "description": "检查Issue标题是否规范",
        "prompt": "请检查这个Issue标题是否规范：{title}。规范要求：1. 不能为空 2. 不能是默认值 3. 应该描述问题",
        "action": "comment"
    },
    {
        "name": "description_check",
        "description": "检查Issue描述是否完整",
        "prompt": "请检查这个Issue描述是否完整：{body}。要求：1. 不能为空 2. 至少50字 3. 包含更改目的和内容",
        "action": "comment"
    },
    {
        "name": "add_label",
        "description": "为Issue打标签",
        "action": "label"                    
    }
]

class BotRuleManager:
    """BOT规则管理器"""
    def __init__(self, repo_id: int):
        self.repo_id = repo_id

    def get_default_rules(self, rule_type: str) -> List[Dict]:
        """获取默认规则"""
        if rule_type == 'PR':
            return PR_RULES
        else:  # ISSUE
            return ISSUE_RULES

    def evaluate_rule(self, rule: Dict, content: Dict) -> Dict:
        """使用LLM评估规则"""
        prompt = rule["prompt"].format(**content)
        format_prompt = """
        你必须严格按以下 JSON 格式返回，不要包含任何额外解释或注释：
        {
            "is_valid": true/false,  # 整体是否规范
            "message": "总体反馈信息",  # 简要说明合规情况
            "suggestions": [  # 改进建议列表
                "建议1：...",
                "建议2：...",
            ]
        }
        """
        response = simple_llm_generate_3b(prompt + format_prompt)
        print(response)
        # TODO 指定返回具体格式
        try:
            result = json.loads(response)
        except json.JSONDecodeError:
            print('返回格式错误！')
        
        return {
            "is_valid": result["is_valid"],
            "message": result["message"],
            "suggestions": result["suggestions"]
        }

class BotLabelManager:
    """BOT标签管理器"""
    def __init__(self, repo_id: int):
        self.repo_id = repo_id
        self.default_labels = DEFAULT_LABELS

    def get_suggested_labels(self, content: Dict, labels: List[str]) -> List[str]:
        """使用LLM建议标签
        
        Args:
            content: GitHub issue/PR 数据字典，包含 title, body 等字段
            labels: 可用的标签列表
        """
        # 组合标题和内容作为分析文本
        analysis_text = f"{content.get('title', '')}\n\n{content.get('body', '')}"
        default_label_names = [label["name"] for label in self.default_labels]
        tarlabels = labels + default_label_names
        # TODO 指定返回具体格式 
        prompt = f"""
        根据以下内容建议合适的标签：
        内容：{analysis_text}
        可用标签：{', '.join(tarlabels)}
        请返回最相关的3个标签。
    
        要求：
        1. 你必须严格按以下 JSON 格式返回，不要包含任何额外解释或注释：
        {{
            "suggested_labels": [  # 推荐的label
                "label1：...",
                "label2：...",
            ]
        }} 
        2. 必须从上述可用标签中选择
        3. 最多推荐3个最相关标签

        示例输出：{
            ["bug", "documentation"]
        }
        """
        response = simple_llm_generate_3b(prompt)
        print(response)
        result = json.loads(response)
        print(result)
        return result["suggested_labels"]

class AddLabel2db(View):
    """
        Date        : 2025/5/3
        Author      : tangling
        Description : 用户加标签，存储到数据库中
    """
    def post(self, request):
        try:
            kwargs: dict = json.loads(request.body)
            repo_id = kwargs.get("repoId")
            label_name = kwargs.get("labelName")
            label_color = kwargs.get("labelColor")
            label_description = kwargs.get("labelDescription")
            
            botlabel = BotLabel.objects.filter(repo_id=repo_id,label_name=label_name)
            # 如果没有，则创建
            if botlabel.count() == 0:
                BotLabel.objects.create(repo_id=repo_id,label_name=label_name,
                                label_color=label_color,label_description=label_description)
            else:
                print(label.name for label in botlabel)
                return JsonResponse({"errcode":2, "message":"the label is already in repo!"})
            return JsonResponse({"errcode":0, "message":"successfully add label"})
        except Exception as e:
            return JsonResponse({"errcode":1, "message": str(e)})

class RemoveLabelFromdb(View):
    """
        Date        : 2025/5/3
        Author      : tangling
        Description : 在数据库中删除 Label
    """
    def post(self, request):
        try:
            kwargs: dict = json.loads(request.body)
            repo_id = kwargs.get("repoId")
            label_name = kwargs.get("labelName")
            botlabel = BotLabel.objects.filter(repo_id=repo_id,label_name=label_name)
            if botlabel.count() == 0:
                return JsonResponse({"errcode":2, "message":"the label is not in the repo"})
            for label in botlabel:
                label.delete()
            return JsonResponse({"errcode":0, "message":"successfully delete label"})
        except Exception as e:
            return JsonResponse({"errcode":1, "message": str(e)})    

class getLabels(View):
    """
        Date        : 2025/5/3
        Author      : tangling
        Description : 得到 Label 列表
    """    
    def post(self, request):
        try:
            kwargs: dict = json.loads(request.body)
            repo_id = kwargs.get("repoId")
            botlabels = BotLabel.objects.filter(repo_id=repo_id)
            resultLabels = []
            for label in DEFAULT_LABELS:
                resultLabels.append({
                    "name": label['name'],
                    "color": label['color'],
                    "description": label['description'],
                    "default": 1,
                })
            for label in botlabels:
                resultLabels.append({
                    "name": label.label_name,
                    "color": label.label_color,
                    "description": label.label_description,
                    "default": 0
                })
            return JsonResponse({"errcode":0, "message":"successfully get labels", "labels":resultLabels})
        except Exception as e:
            return JsonResponse({"errcode":1, "message": str(e)})    

class AddRule2db(View):
    """
        Date        : 2025/5/3
        Author      : tangling
        Description : 用户加规则，存储到数据库中
    """
    def post(self, request):
        try:
            kwargs: dict = json.loads(request.body)
            repo_id = kwargs.get("repoId")
            rule_type = kwargs.get("ruleType")
            rule_name = kwargs.get("ruleName")
            rule_content = kwargs.get("ruleContent")
            botrule = BotRule.objects.filter(repo_id=repo_id,rule_name=rule_name,rule_type=rule_type)
            # 如果没有，则创建
            if botrule.count() == 0:
                BotRule.objects.create(repo_id=repo_id,rule_type=rule_type,
                                       rule_name=rule_name,rule_content=rule_content)
            else:
                return JsonResponse({"errcode":2, "message":"the rule is already in repo!"})
            return JsonResponse({"errcode":0, "message":"successfully add label"})
        except Exception as e:
            return JsonResponse({"errcode":1, "message": str(e)})

class RemoveRuleFromdb(View):
    """
        Date        : 2025/5/3
        Author      : tangling
        Description : 在数据库中删除 Rule
    """
    def post(self, request):
        try:
            kwargs: dict = json.loads(request.body)
            repo_id = kwargs.get("repoId")
            rule_name = kwargs.get("ruleName")
            rule_type = kwargs.get("ruleType")
            botrule = BotRule.objects.filter(repo_id=repo_id,rule_name=rule_name,rule_type=rule_type)
            if botrule.count() == 0:
                return JsonResponse({"errcode":2, "message":"the rule is not in the repo"})
            for rule in botrule:
                rule.delete()
            return JsonResponse({"errcode":0, "message":"successfully delete rule"})
        except Exception as e:
            return JsonResponse({"errcode":1, "message": str(e)})    

class getRules(View):
    """
        Date        : 2025/5/3
        Author      : tangling
        Description : 得到 Rule 列表
    """    
    def post(self, request):
        try:
            kwargs: dict = json.loads(request.body)
            repo_id = kwargs.get("repoId")
            botrules = BotRule.objects.filter(repo_id=repo_id)
            print(botrules,"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            resultRules = []
            for rule in PR_RULES:
                resultRules.append({
                    "type": "PR",
                    "name": rule['name'],
                    "content": json.dumps(rule),
                    "default": 1
                })
            for rule in ISSUE_RULES:
                resultRules.append({
                    "type": "ISSUE",
                    "name": rule['name'],
                    "content": json.dumps(rule),
                    "default": 1                    
                })
            for rule in botrules:
                resultRules.append({
                    "type": rule.rule_type,
                    "name": rule.rule_name,
                    "content": rule.rule_content,
                    "default": 0
                })
            return JsonResponse({"errcode":0, "message":"successfully get rules", "rules":resultRules})
        except Exception as e:
            return JsonResponse({"errcode":1, "message": str(e)})    
