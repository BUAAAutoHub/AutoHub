from typing import List, Dict

class BotRuleManager:
    """BOT规则管理器"""
    def __init__(self, repo_id: int):
        self.repo_id = repo_id
        self.llm = 1 # TODO LLMService() 初始化LLM服务

    def get_default_rules(self, rule_type: str) -> List[Dict]:
        """获取默认规则"""
        if rule_type == 'PR':
            return [
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
        else:  # ISSUE
            return [
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

    def evaluate_rule(self, rule: Dict, content: Dict) -> Dict:
        """使用LLM评估规则"""
        prompt = rule["prompt"].format(**content)
        response = self.llm.generate(prompt)
        # TODO 指定返回具体格式
        return {
            "is_valid": response.get("is_valid", False),
            "message": response.get("message", ""),
            "suggestions": response.get("suggestions", [])
        }

class BotLabelManager:
    """BOT标签管理器"""
    def __init__(self, repo_id: int):
        self.repo_id = repo_id
        self.llm = 1 # TODO LLMService()

    def get_suggested_labels(self, content: Dict, labels: List[str]) -> List[str]:
        """使用LLM建议标签
        
        Args:
            content: GitHub issue/PR 数据字典，包含 title, body 等字段
            labels: 可用的标签列表
        """
        # 组合标题和内容作为分析文本
        analysis_text = f"{content.get('title', '')}\n\n{content.get('body', '')}"
        # TODO 指定返回具体格式 
        prompt = f"""
        根据以下内容建议合适的标签：
        内容：{analysis_text}
        可用标签：{', '.join(labels)}
        请返回最相关的3个标签。
        """
        response = self.llm.generate(prompt)
        return response.get("suggested_labels", [])
