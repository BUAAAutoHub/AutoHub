import json

from github import Github
from github.GithubException import GithubException
from django.views import View
from django.http import JsonResponse
from myApp.models import Project, Repo, Bot, ProjectRepoBot, User, UserProjectRepo, BotLabel, BotRule
from myApp.utils.projects.userdevelop import isProjectExists, isUserInProject, validate_token, _getPrs, _getIssues
from myApp.utils.projects.projectBotRule import BotRuleManager, BotLabelManager
from myApp.utils.projects.apis.github import add_labels, _get_item_content, _add_comment, _add_labels
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_NAME = "AutoBOT-buaa"


def check_repo_membership(github_token: str, repo_full_name: str, botname: str) -> bool:
    """
    Date        : 2025/4/22
    Author      : tangling
    Description : 检查BOT是否在仓库中
    """
    g = Github(github_token)
    try:
        repo = g.get_repo(repo_full_name)
        bot = g.get_user(botname)
        # 检查直接协作者
        if repo.has_in_collaborators(bot):
            return True
        # 检查团队权限（针对 Organization 仓库）
        if repo.organization:
            for team in repo.organization.get_teams():
                if team.has_in_members(bot) and team.has_in_repos(repo):
                    return True
        return False

    except GithubException as e:
        return False


class BotManager:
    """
    Date        : 2025/4/22
    Author      : tangling
    Description : BOT 管理
    """

    def __init__(self, project_id):
        self.project_id = project_id
        self.project = Project.objects.get(id=project_id)

    def create_bot(self, name, token, user_id):
        """创建新的BOT"""
        if not Bot.objects.filter(name=name).exists():
            bot = Bot.objects.create(name=name, token=token, created_by_id=user_id)
        else:
            bot = Bot.objects.get(name=name)
            bot.token = token
            bot.save()
        return bot

    def add_bot_to_project(self, bot_id, user_id, repo_id):
        """将BOT添加到项目"""
        projectGet = isProjectExists(self.project_id)
        userProject = isUserInProject(user_id, self.project_id)
        repo = Repo.objects.filter(id=repo_id)
        userToken = User.objects.get(id=user_id).token

        # 没有这个项目
        if projectGet == None:
            return 1, "project does not exists"

        # 用户不在项目中
        if userProject == None or not User.objects.filter(id=user_id).exists():
            return 2, "user not in project"

        # 没有这个仓库
        if repo == None or not UserProjectRepo.objects.filter(project_id=self.project_id, repo_id=repo_id).exists():
            return 3, "no such repo in project"

        # token 无效
        if userToken is None or validate_token(userToken) == False:
            return 4, "invalid token"

        # bot 已经在项目里了
        if ProjectRepoBot.objects.filter(project_id=self.project_id, repo_id=repo_id, bot_id=bot_id).exists():
            print(f"this is bot id:{bot_id}, this is project id:{self.project_id}, this is repo id:{repo_id}")
            return 5, "bot is already in the project"

        # 判断 github 的仓库中是否有 bot
        bot = Bot.objects.get(id=bot_id)
        result = check_repo_membership(userToken, Repo.objects.get(id=repo_id).remote_path, bot.name)
        if result == False:
            return 6, "BOT is not in your repository"

        ProjectRepoBot.objects.create(project_id=self.project_id, bot_id=bot_id, repo_id=repo_id, added_by_id=user_id)

        return 0, "success invite BOT"


# TODO：权限管理
class BotCreate(View):
    """
    Date        : 2025/4/22
    Author      : tangling
    Description : 在自己的项目拉入BOT
    """

    def post(self, request):
        """创建BOT的API"""
        try:
            kwargs = json.loads(request.body)
            user_id = kwargs.get("userId")
            project_id = kwargs.get("projectId")  # projectId in our model
            repo_id = kwargs.get("repoId")  # repoId in our model
            name = kwargs.get("name")  # username on github
            token = kwargs.get("token")  # Bot's token on github

            bot_manager = BotManager(project_id)
            bot = bot_manager.create_bot(name, token, user_id)
            errcode, message = bot_manager.add_bot_to_project(bot.id, user_id, repo_id)

            return JsonResponse({"errcode": errcode, "message": message})

        except Exception as e:
            return JsonResponse({"errcode": 6, "message": str(e)})


class BotRemove(View):
    """
    Date        : 2025/5/3
    Author      : tangling
    Description : 删除BOT
    """
    def post(self, request):
        try:
            kwargs = json.loads(request.body)
            user_id = kwargs.get("userId")
            project_id = kwargs.get("projectId")  # projectId in our model
            repo_id = kwargs.get("repoId")  # repoId in our model
            bot = ProjectRepoBot.objects.get(project_id=project_id, repo_id=repo_id)
            bot.delete()
            return JsonResponse({"errcode": 0, "message": "successfully delete the bot"})

        except Exception as e:
            return JsonResponse({"errcode": 6, "message": str(e)})

class DisableOrEnableBot(View):
    """
    Date        : 2025/4/22
    Author      : tangling
    Description : 关闭 Bot 功能
    """

    def post(self, request):
        """关闭 Bot 功能"""
        try:
            kwargs = json.loads(request.body)
            user_id = kwargs.get("userId")
            project_id = kwargs.get("projectId")
            repo_id = kwargs.get("repoId")

            project_repo_bot = ProjectRepoBot.objects.get(project_id=project_id, repo_id=repo_id)

            project_repo_bot.is_active = not project_repo_bot.is_active
            project_repo_bot.save()
            return JsonResponse({"errcode": 0, "message": "successfully disable the bot"})

        except Exception as e:
            return JsonResponse({"errcode": 1, "message": str(e)})


class getActive(View):
    """
    Date        : 2025/5/3
    Author      : tangling
    Description : 获得 BOT 的使能状态      
    """
    def post(self, request):
        try:
            kwargs: dict = json.loads(request.body)
            project_id = kwargs.get("projectId")
            repo_id = kwargs.get("repoId")
            is_active = ProjectRepoBot.objects.get(project_id=project_id, 
                                                repo_id=repo_id).is_active
            return JsonResponse({"errcode": 0, "message": "successfully get active", "data":is_active})
        except Exception as e:
            return JsonResponse({"errcode": 1, "message": str(e)})

class getExist(View):
    """
    
    """
    def post(self, request):
        try:
            kwargs: dict = json.loads(request.body)
            project_id = kwargs.get("projectId")
            repo_id = kwargs.get("repoId")
            count = ProjectRepoBot.objects.filter(project_id=project_id, 
                                                repo_id=repo_id).count()
            exist = count > 0
            return JsonResponse({"errcode": 0, "message": "successfully get exist", "data":exist})
        except Exception as e:
            return JsonResponse({"errcode": 1, "message": str(e)})

"""
下面是关于规范检查和打标签的 BotRuleManager
"""


class AutoReviewBot:
    """
    Date        : 2025/4/26
    Author      : tangling
    Description : 自动审核BOT
    """

    def __init__(self, project_id: int, repo_id: int):
        self.project_id = project_id
        self.repo_id = repo_id
        self.repo = Repo.objects.get(id=repo_id)
        self.bot = ProjectRepoBot.objects.get(project_id=project_id, repo_id=repo_id).bot
        self.token = self.bot.token if self.bot else None
        self.active = ProjectRepoBot.objects.get(project_id=project_id, repo_id=repo_id).is_active
        self.rule_manager = BotRuleManager(repo_id)
        self.label_manager = BotLabelManager(repo_id)

    def process_item(self, item_type: str, item_number: int):
        """处理单个PR或Issue"""
        # 获取项目规则
        custom_rules = BotRule.objects.filter(repo_id=self.repo_id, rule_type=item_type, is_active=True)

        # 合并默认规则和自定义规则
        all_rules = self.rule_manager.get_default_rules(item_type)
        all_rules.extend([json.loads(rule.rule_content) for rule in custom_rules])

        # 获取项目标签
        available_labels = list(
            BotLabel.objects.filter(repo_id=self.repo_id, is_active=True).values_list("label_name", flat=True)
        )

        # 获取内容
        print(f"this is item_type:{item_type}, this is item_number:#{item_number}")
        content = _get_item_content(self.token, self.repo.remote_path,
                                    item_type=item_type, item_number=item_number)

        data = []
        comment_messages = []
        # 应用规则
        for rule in all_rules:
            if rule["action"] == "comment":
                result = self.rule_manager.evaluate_rule(rule, content)
                if not result["is_valid"]:
                    message = str(result["message"]) + "," + str(",".join(result["suggestions"]))
                    if message.strip():
                        comment_messages.append(message)
            elif rule["action"] == "label":
                suggested_labels = self.label_manager.get_suggested_labels(content, available_labels)
                _add_labels(self.token, self.repo.remote_path,
                            item_type, item_number, suggested_labels)
                data.append(f"处理{item_type}#{item_number}:\n提供标签：{suggested_labels}")

        if comment_messages:
            final_comment = "\n\n".join(comment_messages)
            _add_comment(self.token, self.repo.remote_path,
                        item_type, item_number, final_comment)
            data.append(f"处理{item_type}#{item_number}:\n反馈信息：{final_comment}")

        return data

    def run_scheduled_review(self):
        # 获取需要审核的PR和Issue
        data = []
        if not self.active:
            return -1, data
        prs_to_review = _getPrs(self.repo_id, self.token)
        issues_to_review = _getIssues(self.repo_id, self.token)
        if not isinstance(prs_to_review, list) or not isinstance(issues_to_review, list):
            return -1, data
        
        pr_set = set()
        # 处理PR
        for pr in prs_to_review:
            if pr['isOpen']:
                print(f"this is {pr}")
                pr_set.add(pr['prId'])
                result = self.process_item("PR", pr['prId'])
                for ele in result:
                    data.append(ele)
        # 处理Issue
        for issue in issues_to_review:
            if issue['issueId'] not in pr_set and issue['isOpen']:
                result = self.process_item("ISSUE", issue['issueId'])
                for ele in result:
                    data.append(ele)
        return 0, data

class AutoReview(View):
    """
        Date        : 2025/5/2
        Author      : tangling
        Description : 用户点击按钮触发该 API
    """
    def post(self, request):
        try:
            kwargs = json.loads(request.body)
            project_id = kwargs.get("projectId")
            repo_id = kwargs.get("repoId")
            
            # 创建新的 AutoReviewBot 准备触发
            print(f"this is pro:{project_id}, this is repo:{repo_id}")
            autoreviewBot = AutoReviewBot(project_id, repo_id)
            success, data = autoreviewBot.run_scheduled_review()
            if success == 0:
                return  JsonResponse({"errcode": 0, "message": "successfully review the bot","data": data})
            elif success == -1:
                return  JsonResponse({"errcode": 3, "message": "please enable the bot first"})
            else:
                return  JsonResponse({"errcode": 1, "message": "fail review the bot"})
        except Exception as e:
            return JsonResponse({"errcode": 2, "message": str(e)})
