import mimetypes
import datetime
import subprocess
import requests
import json
import os
import sys

from django.http import JsonResponse, FileResponse
from django.views import View
from myApp.models import *
from djangoProject.settings import DBG, USER_REPOS_DIR, BASE_DIR
from django.db.models import Q

repo_semaphore = {}
os.environ['GH_TOKEN'] = 'ghp_123456'
# os.environ["HOME"] = BASE_DIR
# def getSemaphore(repoId):
#     repoId = str(repoId)
#     if not repo_semaphore.__contains__(repoId):
#         repo_semaphore[repoId] = True
#         return
#     while repo_semaphore[repoId] == True:
#         continue
#     repo_semaphore[repoId] = True
#     return
#
#
# def releaseSemaphore(repoId):
#     repo_semaphore[repoId] = False
#     return


MERET = 0


def getCounter():
    global MERET
    MERET = MERET + 1
    return MERET - 1


def isProjectExists(projectId):
    try:
        project = Project.objects.get(id=projectId)
        return project
    except Exception as e:
        return None


def isUserInProject(userId, projectId):
    try:
        userProject = UserProject.objects.get(user_id=userId, project_id=projectId)
        return userProject
    except Exception as e:
        return None


def genUnexpectedlyErrorInfo(response, e):
    response["errcode"] = -1
    response['message'] = "unexpectedly error : " + str(e)
    return response


def genResponseStateInfo(response, errcode, message):
    response["errcode"] = errcode
    response['message'] = message
    return response


def checkCMDError(err, errcode, response):
    if "Failed" in err or "422" in err or "fatal" in err or "403" in err or "rejected" in err:
        print("err is :", err)
        response["message"] = "error at gh api :" + err
        response["errcode"] = errcode
        return True, response
    else:
        return False, response


def needRefresh(token, repo):
    try:
        remotePath = repo.remote_path
        localPath = repo.local_path
        remote_command = [
            "gh", "api",
            "-H", "Accept: application/vnd.github.v3+json",
            "-H", f"Authorization: token {token}",
            f"/repos/{remotePath}/branches"
        ]
        remote_result = subprocess.run(remote_command, capture_output=True, text=True, cwd=localPath, check=True)
        remote_branches = []
        if remote_result.returncode == 0:
            remote_data = json.loads(remote_result.stdout)
            if isinstance(remote_data, list):
                remote_branches = [branch['name'] for branch in remote_data]
        local_result = subprocess.run(["git", "branch"], capture_output=True, text=True, cwd=localPath, check=True)
        local_branches = []
        if local_result.returncode == 0:
            local_branches = [branch.strip()[2:] for branch in local_result.stdout.split('\n') if
                              branch.strip() != ""]
        new_branches = set(remote_branches) - set(local_branches)
        if new_branches:
            return True
        for branch in local_branches:
            remote_commit = None
            remote_branch_command = [
                "gh", "api",
                "-H", "Accept: application/vnd.github.v3+json",
                "-H", f"Authorization: token {token}",
                f"/repos/{remotePath}/commits/{branch}"
            ]
            remote_branch_result = subprocess.run(remote_branch_command, capture_output=True, text=True,
                                                  cwd=localPath, check=True)
            if remote_branch_result.returncode == 0:
                remote_data = json.loads(remote_branch_result.stdout)
                if 'sha' in remote_data:
                    remote_commit = remote_data['sha']
            local_commit_result = subprocess.run(["git", "rev-parse", branch], capture_output=True, text=True,
                                                 cwd=localPath, check=True)
            local_commit = None
            if local_commit_result.returncode == 0:
                local_commit = local_commit_result.stdout.strip()
            if remote_commit and local_commit and remote_commit != local_commit:
                return True
            else:
                return True
        return False
    except Exception as e:
        return True, e


class CheckRefreshRepo(View):
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        response = {}
        genResponseStateInfo(response, 0, "check repo refresh ok")
        userId = str(kwargs.get('userId'))
        projectId = str(kwargs.get('projectId'))
        repoId = str(kwargs.get('repoId'))
        project = isProjectExists(projectId)
        if project == None:
            return JsonResponse(genResponseStateInfo(response, 1, "project does not exists"))
        userProject = isUserInProject(userId, projectId)
        if userProject == None or not User.objects.filter(id=userId).exists():
            return JsonResponse(genResponseStateInfo(response, 2, "user not in project"))

        if not UserProjectRepo.objects.filter(project_id=projectId, repo_id=repoId).exists():
            return JsonResponse(genResponseStateInfo(response, 3, "no such repo in project"))
        repo = Repo.objects.get(id=repoId)
        token = User.objects.get(id=userId).token
        if token is None or validate_token(token) == False:
            return JsonResponse(genResponseStateInfo(response, 4, "invalid token"))
        try:
            remotePath = repo.remote_path
            localPath = repo.local_path
            remote_command = [
                "gh", "api",
                "-H", "Accept: application/vnd.github.v3+json",
                "-H", f"Authorization: token {token}",
                f"/repos/{remotePath}/branches"
            ]
            remote_result = subprocess.run(remote_command, capture_output=True, text=True, cwd=localPath, check=True)
            remote_branches = []
            if remote_result.returncode == 0:
                remote_data = json.loads(remote_result.stdout)
                if isinstance(remote_data, list):
                    remote_branches = [branch['name'] for branch in remote_data]
            local_result = subprocess.run(["git", "branch"], capture_output=True, text=True, cwd=localPath, check=True)
            local_branches = []
            if local_result.returncode == 0:
                local_branches = [branch.strip().split(' ')[-1] for branch in local_result.stdout.split('\n') if
                                  branch.strip() != ""]
            new_branches = set(remote_branches) - set(local_branches)
            if new_branches:
                print(new_branches)
                response["message"] = "check ok & have some new branches"
                response["needRefresh"] = 1
                return JsonResponse(response)
            for branch in local_branches:
                remote_commit = None
                remote_branch_command = [
                    "gh", "api",
                    "-H", "Accept: application/vnd.github.v3+json",
                    "-H", f"Authorization: token {token}",
                    f"/repos/{remotePath}/commits/{branch}"
                ]
                remote_branch_result = subprocess.run(remote_branch_command, capture_output=True, text=True,
                                                      cwd=localPath, check=True)
                if remote_branch_result.returncode == 0:
                    remote_data = json.loads(remote_branch_result.stdout)
                    if 'sha' in remote_data:
                        remote_commit = remote_data['sha']
                local_commit_result = subprocess.run(["git", "rev-parse", branch], capture_output=True, text=True,
                                                     cwd=localPath, check=True)
                local_commit = None
                if local_commit_result.returncode == 0:
                    local_commit = local_commit_result.stdout.strip()
                if remote_commit and local_commit and remote_commit != local_commit:
                    response["message"] = f"check ok & {branch} have some new commits"
                    response["needRefresh"] = 1
                    return JsonResponse(response)
                elif remote_commit and local_commit and remote_commit == local_commit:
                    response["needRefresh"] = 0
                    return JsonResponse(response)
                else:
                    return JsonResponse(genResponseStateInfo(response, 5, "wrong to check"))
        except Exception as e:
            return JsonResponse(genUnexpectedlyErrorInfo(response, e))


class RefreshRepo(View):
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        response = {}
        genResponseStateInfo(response, 0, "repo refresh ok")
        userId = str(kwargs.get('userId'))
        projectId = str(kwargs.get('projectId'))
        repoId = str(kwargs.get('repoId'))
        project = isProjectExists(projectId)
        if project == None:
            return JsonResponse(genResponseStateInfo(response, 1, "project does not exists"))
        userProject = isUserInProject(userId, projectId)
        if userProject == None or not User.objects.filter(id=userId).exists():
            return JsonResponse(genResponseStateInfo(response, 2, "user not in project"))

        if not UserProjectRepo.objects.filter(project_id=projectId, repo_id=repoId).exists():
            return JsonResponse(genResponseStateInfo(response, 3, "no such repo in project"))
        repo = Repo.objects.get(id=repoId)
        token = User.objects.get(id=userId).token
        if token is None or validate_token(token) == False:
            return JsonResponse(genResponseStateInfo(response, 4, "invalid token"))
        localPath = repo.local_path
        try:
            # 重新克隆远程仓库
            remotePath = repo.remote_path
            result = subprocess.run(
                ["git", "pull", "origin"],
                capture_output=True, text=True)
            print(result.stderr)
            if result.returncode == 0:
                # 获取本地和远程分支列表
                branch_result = subprocess.run(
                    ["git", "branch", "-a"],
                    capture_output=True, text=True, cwd=localPath)
                if branch_result.returncode != 0:
                    return JsonResponse(genResponseStateInfo(response, 5, "failed to get branch list"))
                # 解析分支列表并创建本地分支
                branches = branch_result.stdout.strip().split('\n')
                for branch in branches:
                    # 去掉分支名前的空格和 * 符号
                    branch_name = branch.strip().lstrip('* ')
                    # 忽略 HEAD 指针和远程分支
                    if branch_name != "HEAD" and not branch_name.startswith("remotes/origin/HEAD"):
                        if branch_name.startswith("remotes/origin"):
                            branch_name = branch_name.split("/")[-1]
                        subprocess.run(["git", "checkout", branch_name], cwd=localPath)
                return JsonResponse(response)
            else:
                return JsonResponse(genResponseStateInfo(response, 5, "failed to refresh repository"))
        except Exception as e:
            print(e)
            return JsonResponse(genUnexpectedlyErrorInfo(response, e))


class GetProjectName(View):
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        response = {}
        genResponseStateInfo(response, 0, "get project name ok")
        response["data"] = {}
        response["data"]["name"] = ""
        userId = str(kwargs.get('userId'))
        projectId = str(kwargs.get('projectId'))
        project = isProjectExists(projectId)
        if project == None:
            return JsonResponse(genResponseStateInfo(response, 1, "project does not exists"))
        userProject = isUserInProject(userId, projectId)
        if userProject == None:
            return JsonResponse(genResponseStateInfo(response, 2, "user not in project"))

        response["data"]["name"] = project.name
        return JsonResponse(response)


class GetBindRepos(View):
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        response = {}
        genResponseStateInfo(response, 0, "get bind repos ok")
        response["data"] = []
        userId = str(kwargs.get('userId'))
        projectId = str(kwargs.get('projectId'))
        project = isProjectExists(projectId)
        if project == None:
            return JsonResponse(genResponseStateInfo(response, 1, "project does not exists"))
        userProject = isUserInProject(userId, projectId)
        if userProject == None:
            return JsonResponse(genResponseStateInfo(response, 2, "user not in project"))
        user = User.objects.get(id=userId)
        token = user.token
        # check if repo exists
        if token is None:
            return JsonResponse(genResponseStateInfo(response, 3, "null token"))
        if not validate_token(token):
            return JsonResponse(genResponseStateInfo(response, 4, "wrong token with this user"))
        print(11111111111111)
        try:
            userProjectRepos = UserProjectRepo.objects.filter(project_id=projectId)
            print(22222222)
            for userProjectRepo in userProjectRepos:
                repoId = userProjectRepo.repo_id.id
                repo = Repo.objects.get(id=repoId)
                print(33333333)
                command = [
                    "gh", "api",
                    "-H", "Accept: application/vnd.github.v3+json",
                    "-H", f"Authorization: token {token}",
                    f"/repos/{repo.remote_path}"
                ]
                result = subprocess.run(command, capture_output=True, text=True,
                                        cwd=repo.local_path,check=True)
                desc = json.loads(result.stdout)
                print("out is :",result.stdout)
                print("err is :",result.stderr)
                response["out"] = result.stdout
                response["fuck"] = result.stderr
                response["data"].append({"repoId": repoId,
                                         "repoRemotePath": repo.remote_path,
                                         "name": repo.name,
                                         "repoIntroduction": desc["description"]})
        except Exception as e:
            print(e)
            print("Command failed with exit code:", e.returncode)
            print("Output:", e.output)
            print("Error:", e.stderr)
            return JsonResponse(genUnexpectedlyErrorInfo(response, e))

        return JsonResponse(response)


def getDir(nowPath, owner, repo, branch, token, data):
    # print(nowPath)
    command = [
        "gh", "api",
        "-H", "Accept: application/vnd.github+json",
        "-H", "X-GitHub-Api-Version: 2022-11-28",
        "-H", f"Authorization: token {token}",
        f"/repos/{owner}/{repo}/contents/{nowPath}?ref={branch}",
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    if result.returncode == 0:
        files = json.loads(result.stdout)
        for file in files:
            if file["type"] == "dir":
                data.append({"name": file["name"], "children": []})

                if nowPath == "":
                    nextPath = str(file["name"])
                else:
                    nextPath = nowPath + "/" + str(file["name"])
                # print("****" + nextPath)
                flag = getDir(nextPath, owner, repo, branch, token, data[-1]["children"])
                if flag == -1:
                    return -1
            else:
                data.append({"name": file['name']})
    else:
        return -1


class GetRepoAllFiles(View):
    def post(self, request):
        # 检查权限
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        response = {}
        genResponseStateInfo(response, 0, "get file tree ok")
        userId = str(kwargs.get('userId'))
        projectId = str(kwargs.get('projectId'))
        repoId = str(kwargs.get('repoId'))
        branch = str(kwargs.get('branch'))
        project = isProjectExists(projectId)
        if project == None:
            return JsonResponse(genResponseStateInfo(response, 1, "project does not exists"))
        userProject = isUserInProject(userId, projectId)
        if userProject == None:
            return JsonResponse(genResponseStateInfo(response, 2, "user not in project"))
        if not UserProjectRepo.objects.filter(project_id=projectId, repo_id=repoId).exists():
            return JsonResponse(genResponseStateInfo(response, 3, "no such repo in project"))
        repo = Repo.objects.get(pk=repoId)
        owner = str.split(repo.remote_path, "/")[0]
        repo = str.split(repo.remote_path, "/")[1]

        user = User.objects.get(id=userId)
        token = user.token
        print(owner, repo)
        data = []
        try:
            flag = getDir("", owner, repo, branch, token, data)
        except subprocess.CalledProcessError as e:
            print("命令执行失败:", e)
            print("错误输出:", e.stderr)
            response["message"] = str(e)
            response["errcode"] = -1
            return JsonResponse(response)
        if flag == -1:
            return JsonResponse(genResponseStateInfo(response, 4, "wrong in getDir"))
        response["data"] = data
        return JsonResponse(response)


class GetRepoFile(View):
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        response = {}
        genResponseStateInfo(response, 0, "get repo all files ok")
        userId = str(kwargs.get('userId'))
        projectId = str(kwargs.get('projectId'))
        repoId = str(kwargs.get('repoId'))
        filePath = str(kwargs.get('filePath'))
        project = isProjectExists(projectId)
        if project == None:
            return JsonResponse(genResponseStateInfo(response, 1, "project does not exists"))
        userProject = isUserInProject(userId, projectId)
        if userProject == None:
            return JsonResponse(genResponseStateInfo(response, 2, "user not in project"))
        if not UserProjectRepo.objects.filter(project_id=projectId, repo_id=repoId).exists():
            return JsonResponse(genResponseStateInfo(response, 3, "no such repo in project"))
        repo = Repo.objects.get(pk=repoId)
        file_path = repo.local_path + "/" + filePath
        try:
            if not os.path.isfile(file_path):
                return JsonResponse(genResponseStateInfo(response, 1, "file does not exists"))
            with open(file_path, 'r') as file:
                file_content = file.read()
            content_type, _ = mimetypes.guess_type(file_path)
            return FileResponse(file_content, content_type=content_type)
        except FileNotFoundError:
            return JsonResponse(genResponseStateInfo(response, 1, "file does not exists"))


def check_repo_exists(token, repoRemotePath):
    owner, repo_name = repoRemotePath.split('/')
    print(os.environ.get('GH_TOKEN'))
    check_command = [
        "gh", "api",
        f"/repos/{owner}/{repo_name}",
        "-H", f"Authorization: token {token}"
    ]
    try:
        result = subprocess.run(check_command, capture_output=True, text=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False


class UserBindRepo(View):
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        response = {}
        genResponseStateInfo(response, 0, "bind ok")
        userId = str(kwargs.get('userId'))
        projectId = str(kwargs.get('projectId'))
        repoRemotePath = kwargs.get('repoRemotePath')
        DBG("userId=" + userId + " projectId=" + projectId + " repoRemotePath=" + repoRemotePath)
        project = isProjectExists(projectId)
        if project is None:
            return JsonResponse(genResponseStateInfo(response, 1, "project does not exists"))
        userProject = isUserInProject(userId, projectId)
        if userProject is None or not User.objects.filter(id=userId).exists():
            return JsonResponse(genResponseStateInfo(response, 2, "user not in project"))
        user = User.objects.get(id=userId)
        token = user.token
        # check if repo exists
        if token is None or not validate_token(token):
            return JsonResponse(genResponseStateInfo(response, 3, "wrong token with this user"))

        repoName = repoRemotePath.split("/")[-1]
        userReposDir = os.path.join(USER_REPOS_DIR, "user" + userId)
        localPath = os.path.join(userReposDir, repoName)
        print(localPath)
        if not os.path.exists(userReposDir):
            os.makedirs(userReposDir)

        if not check_repo_exists(token, repoRemotePath):
            return JsonResponse(genResponseStateInfo(response, 4, "wrong remote path"))
        if Repo.objects.filter(remote_path=repoRemotePath).exists():
            repo = Repo.objects.get(remote_path=repoRemotePath)
            localPath = repo.local_path
        if not os.path.exists(localPath):
            clone_command = [
                'git', 'clone', f"https://{token}@github.com/{repoRemotePath}.git",
                f"{localPath}"
            ]
            result = subprocess.run(clone_command, capture_output=True, text=True, cwd=userReposDir)
            print(result.stdout)
            print(result.stderr)
            if result.returncode != 0:
                return JsonResponse(genResponseStateInfo(response, 5, "clone failed"))
        repo, _ = Repo.objects.get_or_create(
            remote_path=repoRemotePath,
            defaults={'name': repoName, 'local_path': localPath}
        )

        userProjectRepoEntry, _ = UserProjectRepo.objects.get_or_create(
            user_id=user, project_id=project, repo_id=repo
        )
        return JsonResponse(response)


class UserUnbindRepo(View):
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        response = {}
        genResponseStateInfo(response, 0, "unbind ok")
        userId = str(kwargs.get('userId'))
        projectId = str(kwargs.get('projectId'))
        repoId = str(kwargs.get('repoId'))
        project = isProjectExists(projectId)
        if project == None:
            return JsonResponse(genResponseStateInfo(response, 1, "project does not exists"))
        userProject = isUserInProject(userId, projectId)
        if userProject == None:
            return JsonResponse(genResponseStateInfo(response, 2, "user not in project"))

        if not UserProjectRepo.objects.filter(user_id=userId, project_id=projectId, repo_id=repoId).exists():
            return JsonResponse(genResponseStateInfo(response, 3, "no such repo in project that bind by this user"))

        try:
            userProjectRepo = UserProjectRepo.objects.get(user_id=userId, project_id=projectId, repo_id=repoId)
            userProjectRepo.delete()
        except Exception as e:
            return JsonResponse(genUnexpectedlyErrorInfo(response, e))

        return JsonResponse(response)


class GetRepoBranches(View):
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        response = {}
        genResponseStateInfo(response, 0, "get branches ok")
        userId = str(kwargs.get('userId'))
        projectId = str(kwargs.get('projectId'))
        repoId = str(kwargs.get('repoId'))
        project = isProjectExists(projectId)
        if project == None:
            return JsonResponse(genResponseStateInfo(response, 1, "project does not exists"))
        userProject = isUserInProject(userId, projectId)
        if userProject == None or not User.objects.filter(id=userId).exists():
            return JsonResponse(genResponseStateInfo(response, 2, "user not in project"))

        if not UserProjectRepo.objects.filter(project_id=projectId, repo_id=repoId).exists():
            return JsonResponse(genResponseStateInfo(response, 3, "no such repo in project"))
        token = User.objects.get(id=userId).token
        if token is None or validate_token(token) == False:
            return JsonResponse(genResponseStateInfo(response, 4, "invalid token"))

        data = []
        try:
            remotePath = Repo.objects.get(id=repoId).remote_path
            command = [
                "gh", "api",
                "-H", "Accept: application/vnd.github+json",
                "-H", "X-GitHub-Api-Version: 2022-11-28",
                "-H", f"Authorization: token {token}",
                f"/repos/{remotePath}/branches",
            ]
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            print("err is :", result.stderr)
            flag, response = checkCMDError(result.stderr, 5, response)
            if flag:
                return JsonResponse(response)
            ghInfo = json.loads(result.stdout)
            for it in ghInfo:
                sha = it["commit"]["sha"]
                cmd = [
                    "gh", "api",
                    "-H", "Accept: application/vnd.github+json",
                    "-H", "X-GitHub-Api-Version: 2022-11-28",
                    "-H", f"Authorization: token {token}",
                    f"/repos/{remotePath}/commits/{sha}",
                ]
                cmd_result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                print("out is :", cmd_result.stdout)
                flag, response = checkCMDError(cmd_result.stderr, 6, response)
                if flag:
                    return JsonResponse(response)
                commitInfo = json.loads(cmd_result.stdout)
                data.append({"branchName": it["name"],
                             "lastCommit": {
                                 "sha": sha,
                                 "authorName": commitInfo["commit"]["author"]["name"],
                                 "authorEmail": commitInfo["commit"]["author"]["email"],
                                 "commitDate": commitInfo["commit"]["author"]["date"],
                                 "commitMessage": commitInfo["commit"]["message"]
                             }
                             })
            response["data"] = data
        except Exception as e:
            return JsonResponse(genUnexpectedlyErrorInfo(response, e))
        return JsonResponse(response)


class GetCommitHistory(View):
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        response = {}
        genResponseStateInfo(response, 0, "get commit history ok")
        userId = str(kwargs.get('userId'))
        projectId = str(kwargs.get('projectId'))
        repoId = str(kwargs.get('repoId'))
        branchName = kwargs.get('branchName')
        project = isProjectExists(projectId)
        if project == None:
            return JsonResponse(genResponseStateInfo(response, 1, "project does not exists"))
        userProject = isUserInProject(userId, projectId)
        if userProject == None or not User.objects.filter(id=userId).exists():
            return JsonResponse(genResponseStateInfo(response, 2, "user not in project"))

        if not UserProjectRepo.objects.filter(project_id=projectId, repo_id=repoId).exists():
            return JsonResponse(genResponseStateInfo(response, 3, "no such repo in project"))

        repo = Repo.objects.get(id=repoId)
        token = User.objects.get(id=userId).token
        if token is None or validate_token(token) == False:
            return JsonResponse(genResponseStateInfo(response, 5, "invalid token"))

        data = []
        try:
            localPath = repo.local_path
            remotePath = repo.remote_path
            if not is_independent_git_repository(localPath):
                return JsonResponse(genResponseStateInfo(response, 4, "this is not git repository???"))
            cmd = [
                "gh", "api",
                "-H", "Accept: application/vnd.github+json",
                "-H", "X-GitHub-Api-Version: 2022-11-28",
                "-H", f"Authorization: token {token}",
                f"/repos/{remotePath}/commits?sha={branchName}",
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            flag, response = checkCMDError(result.stderr, 5, response)
            if flag:
                print("err is ", result.stderr)
                return JsonResponse(response)
            ghInfo = json.loads(result.stdout)
            for info in ghInfo:
                sha = info["sha"]
                if not Commit.objects.filter(sha=sha).exists():
                    tmp_commit = Commit.objects.create(repo_id=Repo.objects.get(id=repoId), sha=sha,
                                                       committer_name=info["commit"]["author"]["name"])
                else:
                    tmp_commit = Commit.objects.filter(sha=sha)[0]
                if tmp_commit.reviewer_id is not None:
                    reviewerId = tmp_commit.reviewer_id_id
                    reviewerName = User.objects.get(id=reviewerId).name
                else:
                    reviewerId = None
                    reviewerName = None
                data.append({"commithash": sha, "author": info["commit"]['author']['name'],
                             "authorEmail": info['commit']['author']['email'],
                             "commitTime": info["commit"]["author"]["date"],
                             "commitMessage": info["commit"]["message"],
                             "status": tmp_commit.review_status,
                             "reviewerId": reviewerId,
                             "reviewerName": reviewerName, }
                            )
                response["data"] = data
        except Exception as e:
            return JsonResponse(genUnexpectedlyErrorInfo(response, e))
        return JsonResponse(response)


class GetIssueList(View):
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        response = {}
        genResponseStateInfo(response, 0, "get issue list ok")
        userId = str(kwargs.get('userId'))
        projectId = str(kwargs.get('projectId'))
        repoId = str(kwargs.get('repoId'))
        project = isProjectExists(projectId)
        if project == None:
            return JsonResponse(genResponseStateInfo(response, 1, "project does not exists"))
        userProject = isUserInProject(userId, projectId)
        if userProject == None or not User.objects.filter(id=userId).exists():
            return JsonResponse(genResponseStateInfo(response, 2, "user not in project"))

        if not UserProjectRepo.objects.filter(project_id=projectId, repo_id=repoId).exists():
            return JsonResponse(genResponseStateInfo(response, 3, "no such repo in project"))

        token = User.objects.get(id=userId).token
        if token is None or validate_token(token) == False:
            return JsonResponse(genResponseStateInfo(response, 4, "invalid token"))

        data = []
        try:
            remotePath = Repo.objects.get(id=repoId).remote_path
            cmd = [
                "gh", "api",
                "-H", "Accept: application/vnd.github+json",
                "-H", "X-GitHub-Api-Version: 2022-11-28",
                "-H", f"Authorization: token {token}",
                f"/repos/{remotePath}/issues?state=all",
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            flag, response = checkCMDError(result.stderr, 5, response)
            if flag:
                print("err is :", result.stderr)
                return JsonResponse(response)
            ghInfo = json.loads(result.stdout)
            for it in ghInfo:
                data.append({"issueId": it["number"],
                             "issuer": it["user"]["login"],
                             "issueTitle": it["title"],
                             "issueTime": it["updated_at"],
                             "isOpen": it["state"] == "open",
                             "ghLink": it["html_url"]})
            response["data"] = data
        except Exception as e:
            return JsonResponse(genUnexpectedlyErrorInfo(response, e))
        return JsonResponse(response)


class GetPrList(View):
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        response = {}
        genResponseStateInfo(response, 0, "get pr list ok")
        userId = str(kwargs.get('userId'))
        projectId = str(kwargs.get('projectId'))
        repoId = str(kwargs.get('repoId'))
        project = isProjectExists(projectId)
        if project == None:
            return JsonResponse(genResponseStateInfo(response, 1, "project does not exists"))
        userProject = isUserInProject(userId, projectId)
        if userProject == None or not User.objects.filter(id=userId).exists():
            return JsonResponse(genResponseStateInfo(response, 2, "user not in project"))

        if not UserProjectRepo.objects.filter(project_id=projectId, repo_id=repoId).exists():
            return JsonResponse(genResponseStateInfo(response, 3, "no such repo in project"))

        token = User.objects.get(id=userId).token
        if token is None or validate_token(token) == False:
            return JsonResponse(genResponseStateInfo(response, 4, "invalid token"))

        data = []
        try:
            repo = Repo.objects.get(id=repoId)
            remotePath = repo.remote_path
            cmd = [
                "gh", "api",
                "-H", "Accept: application/vnd.github+json",
                "-H", "X-GitHub-Api-Version: 2022-11-28",
                "-H", f"Authorization: token {token}",
                f"/repos/{remotePath}/pulls?state=all",
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            flag, response = checkCMDError(result.stderr, 5, response)
            if flag:
                print("err is :", result.stderr)
                return JsonResponse(response)
            ghInfo = json.loads(result.stdout)
            for it in ghInfo:
                if not Pr.objects.filter(pr_number=it["number"], repo_id=repo).exists():
                    Pr.objects.create(pr_number=it["number"], repo_id=repo, applicant_name=it["user"]["login"],
                                      src_branch=it["head"]["ref"], dst_branch=it["base"]["ref"])
                pr = Pr.objects.get(pr_number=it["number"], repo_id=repo)
                if pr.reviewer_id is None:
                    reviewerId = None
                    reviewerName = None
                else:
                    reviewerId = pr.reviewer_id_id
                    reviewerName = User.objects.get(id=reviewerId).name
                data.append({"prId": it["number"],
                             "prIssuer": it["user"]["login"],
                             "prTitle": it["title"],
                             "reviewerId": reviewerId,
                             "reviewerName": reviewerName,
                             "prTime": it["updated_at"],
                             "isOpen": it["state"] == "open",
                             "ghLink": it["html_url"],
                             "fromBranchName": it["head"]["ref"],
                             "toBranchName": it["base"]["ref"]})
            response["data"] = data
        except Exception as e:
            return JsonResponse(genUnexpectedlyErrorInfo(response, e))
        return JsonResponse(response)


def _getFileTree(dirPath):
    if os.path.isfile(dirPath):
        return {"name": os.path.basename(dirPath)}
    children = []
    fs = os.listdir(dirPath)
    for f in fs:
        if f == ".git":
            continue
        children.append(_getFileTree(os.path.join(dirPath, f)))
    return {"name": os.path.basename(dirPath), "children": children}


class GetFileTree(View):
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        response = {}
        genResponseStateInfo(response, 0, "get file tree ok")
        userId = str(kwargs.get('userId'))
        projectId = str(kwargs.get('projectId'))
        repoId = str(kwargs.get('repoId'))
        branch = str(kwargs.get('branch'))
        project = isProjectExists(projectId)
        if project == None:
            return JsonResponse(genResponseStateInfo(response, 1, "project does not exists"))
        userProject = isUserInProject(userId, projectId)
        if userProject == None or not User.objects.filter(id=userId).exists():
            return JsonResponse(genResponseStateInfo(response, 2, "user not in project"))

        if not UserProjectRepo.objects.filter(project_id=projectId, repo_id=repoId).exists():
            return JsonResponse(genResponseStateInfo(response, 3, "no such repo in project"))
        repo = Repo.objects.get(id=repoId)

        token = User.objects.get(id=userId).token
        if token is None or validate_token(token) == False:
            return JsonResponse(genResponseStateInfo(response, 4, "invalid token"))
        data = []
        localPath = repo.local_path
        try:
            cmd = ["git", "checkout", f"{branch}"]
            subprocess.run(cmd, cwd=localPath)
            r = _getFileTree(localPath)
            for item in r["children"]:
                data.append(item)
            response["data"] = data
            return JsonResponse(response)
        except Exception as e:
            return JsonResponse(genUnexpectedlyErrorInfo(response, e))


class GetContent(View):
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        response = {}
        genResponseStateInfo(response, 0, "get file ok")
        userId = str(kwargs.get('userId'))
        projectId = str(kwargs.get('projectId'))
        repoId = str(kwargs.get('repoId'))
        branch = str(kwargs.get('branch'))
        path = str(kwargs.get('path'))
        project = isProjectExists(projectId)
        if project == None:
            return JsonResponse(genResponseStateInfo(response, 1, "project does not exists"))
        userProject = isUserInProject(userId, projectId)
        if userProject == None:
            return JsonResponse(genResponseStateInfo(response, 2, "user not in project"))

        if not UserProjectRepo.objects.filter(project_id=projectId, repo_id=repoId).exists():
            return JsonResponse(genResponseStateInfo(response, 3, "no such repo in project"))
        repo = Repo.objects.get(id=repoId)

        token = User.objects.get(id=userId).token
        if token is None or validate_token(token) == False:
            return JsonResponse(genResponseStateInfo(response, 4, "invalid token"))
        localPath = repo.local_path
        try:
            cmd = ["git", "checkout", f"{branch}"]
            subprocess.run(cmd, cwd=localPath, check=True)
            filePath = localPath + path  # os.path.join(localPath, path)
            DBG(filePath)
            data = "警告：这是一个二进制文件，请登录 github 查看"
            try:
                data = open(filePath).read()
            except Exception as e:
                pass
            response["data"] = data
            return JsonResponse(response)
        except Exception as e:
            return JsonResponse(genUnexpectedlyErrorInfo(response, e))


import re


def validate_token_format(token):
    # 定义符合要求的token前缀列表
    valid_prefixes = ['ghp_', 'gho_', 'ghu_', 'ghs_', 'ghr_']
    # 使用正则表达式检查token是否以有效的前缀开头
    pattern = '|'.join(valid_prefixes)
    if re.match(pattern, token):
        return True
    return False


def validate_token(token):
    if not validate_token_format(token):
        return False
    headers = {'Authorization': 'token ' + token, 'Content-Type': 'application/json; charset=utf-8'}
    response = requests.get('https://api.github.com/user', headers=headers)
    print(token, response.status_code)
    if response.status_code == 200:
        return True
    print("Response body:", response.text)
    print("Response headers:", response.headers)
    return False


def is_independent_git_repository(path):
    print(os.path.join(path, '.git'))
    if os.path.exists(os.path.join(path, '.git')):
        return True
    else:
        return False


class GitCommit(View):
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        genResponseStateInfo(response, 0, "git commit ok")

        userId = kwargs.get('userId')
        projectId = kwargs.get('projectId')
        repoId = kwargs.get('repoId')

        files = kwargs.get('files')
        branch = kwargs.get('branch')
        message = kwargs.get('message')

        project = isProjectExists(projectId)
        if project == None:
            return JsonResponse(genResponseStateInfo(response, 1, "project does not exists"))
        userProject = isUserInProject(userId, projectId)
        if userProject == None:
            return JsonResponse(genResponseStateInfo(response, 2, "user not in project"))
        if not UserProjectRepo.objects.filter(project_id=projectId, repo_id=repoId).exists():
            return JsonResponse(genResponseStateInfo(response, 3, "no such repo in project"))
        repo = Repo.objects.get(id=repoId)

        user = User.objects.get(id=userId)
        token = user.token

        if repo == None:
            return JsonResponse(genResponseStateInfo(response, 4, "no such repo"))
        localPath = repo.local_path
        try:
            remotePath = repo.remote_path
            print(localPath)
            print("is git :", is_independent_git_repository(localPath))
            if not is_independent_git_repository(localPath):
                return JsonResponse(genResponseStateInfo(response, 999, " not git dir"))
            if validate_token(token):
                t = subprocess.run(["git", "config", "--global", "user.name", "JiHub"], cwd=localPath,capture_output=True,text=True)
                print(t.stdout)
                print(t.stderr)
                subprocess.run(["git", "config", "--global", "user.email", "JiHub@buaa.edu.cn"], cwd=localPath,check=True)
                subprocess.run(["git", "checkout", branch], cwd=localPath, check=True)
                subprocess.run(["git", "remote", "add", "tmp", f"https://{token}@github.com/{remotePath}.git"],
                               cwd=localPath)
                for file in files:
                    path = os.path.join(localPath, file.get('path'))
                    print(path)
                    content = file.get('content')
                    print("$$$$$$$$$$ modify file ", path)
                    try:
                        with open(path, 'w') as f:
                            f.write(content)
                    except Exception as e:
                        print(f"Failed to overwrite file {path}: {e}")
                    subprocess.run(["git", "add", path], cwd=localPath, check=True)
                subprocess.run(["git", "commit", "-m", message], cwd=localPath, check=True)

                result = subprocess.run(["git", "push", "tmp", branch], cwd=localPath, stderr=subprocess.PIPE,
                                        text=True)
                print("err is ", result.stderr)
                if "fatal" in result.stderr or "403" in result.stderr or "rejected" in result.stderr:
                    subprocess.run(["git", "reset", "--hard", "HEAD^1"], cwd=localPath, check=True)
                    subprocess.run(["git", "remote", "rm", "tmp"], cwd=localPath)
                    response["message"] = result.stderr
                    errcode = 7
                else:
                    result = subprocess.run(["git", "log", "-1", "--pretty=format:%H"], cwd=localPath,
                                            capture_output=True, text=True, check=True)
                    current_commit_sha = result.stdout.strip()
                    print(current_commit_sha)
                    Commit.objects.create(repo_id=repo, sha=current_commit_sha, committer_name=user.name,
                                          committer_id=user,
                                          review_status=None)
                    # cooperate & file commit update
                    for file in files:
                        FileUserCommit.objects.create(user_id=user,
                                                      repo_id=repo,
                                                      branch=branch, file=file['path'], commit_sha=current_commit_sha)
                        # modify Cooperate
                        tmp = FileUserCommit.objects.filter(repo_id=repo, branch=branch, file=file['path']).exclude(
                            user_id=user)
                        if tmp.exists():
                            for item in tmp:
                                user2 = item.user_id
                                if not Cooperate.objects.filter(user1_id=user, user2_id=user2,
                                                                project_id=project).exists():
                                    Cooperate.objects.create(user1_id=user, user2_id=user2, project_id=project)
                                cooperate = Cooperate.objects.get(user1_id=user, user2_id=user2, project_id=project)
                                cooperate.relation += 1
                                cooperate.save()
                                if not Cooperate.objects.filter(user1_id=user2, user2_id=user,
                                                                project_id=project).exists():
                                    Cooperate.objects.create(user1_id=user2, user2_id=user, project_id=project)
                                cooperate = Cooperate.objects.get(user1_id=user2, user2_id=user, project_id=project)
                                cooperate.relation += 1
                                cooperate.save()
                    UserProjectActivity.objects.create(user_id=user, project_id=project,
                                                       option=UserProjectActivity.COMMIT_CODE)

                    content = f"您的项目\"{project.name}\"有新的提交，位于仓库\"{repo.name}\"的分支\"{branch}\"，" \
                              f"请分配审核人员。"
                    filtered_user = UserProject.objects.filter(
                        Q(role=UserProject.ADMIN) | Q(role=UserProject.DEVELOPER),
                        project_id=project
                    )
                    for up in filtered_user:
                        msg = Notice.objects.create(receiver_id=up.user_id, read=Notice.N, content=content,
                                                    url=f"commitReview/{projectId}/{repoId}/"
                                                        f"{branch}/{current_commit_sha}?branchName={branch}&projId={projectId}&"
                                                        f"repoId={repoId}&commitSha={current_commit_sha}"
                        )
                        msg.save()

                    errcode = 0
                subprocess.run(["git", "remote", "rm", "tmp"], cwd=localPath)
                response['errcode'] = errcode
            else:
                return JsonResponse(genResponseStateInfo(response, 6, f"wrong token {token} with this user"))
        except Exception as e:
            subprocess.run(["git", "remote", "rm", "tmp"], cwd=localPath)
            return JsonResponse(genUnexpectedlyErrorInfo(response, e))
        return JsonResponse(response)


class GitPr(View):
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        response = {}
        genResponseStateInfo(response, 0, "git pr ok")

        userId = kwargs.get('userId')
        projectId = kwargs.get('projectId')
        repoId = kwargs.get('repoId')
        branch = kwargs.get('branch')
        title = kwargs.get('title')
        body = kwargs.get('body')
        base = kwargs.get('base')

        project = isProjectExists(projectId)
        if project == None:
            return JsonResponse(genResponseStateInfo(response, 1, "project does not exists"))
        userProject = isUserInProject(userId, projectId)
        if userProject == None or not User.objects.filter(id=userId).exists():
            return JsonResponse(genResponseStateInfo(response, 2, "user not in project"))
        if not UserProjectRepo.objects.filter(project_id=projectId, repo_id=repoId).exists():
            return JsonResponse(genResponseStateInfo(response, 3, "no such repo in project"))
        repo = Repo.objects.get(id=repoId)
        if repo == None:
            return JsonResponse(genResponseStateInfo(response, 4, "no such repo"))
        applicant = User.objects.get(id=userId)
        token = applicant.token
        try:
            localPath = Repo.objects.get(id=repoId).local_path
            remotePath = Repo.objects.get(id=repoId).remote_path
            if token is not None or validate_token(token):
                command = [
                    "gh", "api",
                    "-H", "Accept: application/vnd.github+json",
                    "-H", "X-GitHub-Api-Version: 2022-11-28",
                    "-H", f"Authorization: token {token}",
                    f"/repos/{remotePath}/pulls",
                    "-f", f"title={title}",
                    "-f", f"body={body}",
                    "-f", f"head={branch}",
                    "-f", f"base={base}"
                ]

                result = subprocess.run(command, cwd=localPath, capture_output=True, text=True)
                if "Failed" in result.stderr or "422" in result.stderr or "fatal" in result.stderr or "403" in result.stderr or "rejected" in result.stderr:
                    print(result.stdout)
                    print(result.stderr)
                    response["message"] = json.loads(result.stdout)["errors"][0]["message"]
                    response["errcode"] = 7
                    return JsonResponse(response)
                output = json.loads(result.stdout)
                print("------- pr number:", output["number"])
                Pr.objects.create(applicant_id=applicant, repo_id=repo, src_branch=branch, dst_branch=base,
                                  pr_number=output["number"], applicant_name=applicant.name, pr_status=Pr.OPEN)
                response['errcode'] = 0
                content = f"您的项目\"{project.name}\"有新的合并请求，位于仓库\"{repo.name}\"，" \
                          f"请分配审核人员。"
                prId = output["number"]
                for up in UserProject.objects.filter(
                        Q(role=UserProject.ADMIN) | Q(role=UserProject.DEVELOPER),
                        project_id=project
                ):
                    msg = Notice.objects.create(receiver_id=up.user_id, read=Notice.N, content=content,
                                                url=f"prReview/{projectId}/{repoId}/{prId}"
                                                    f"?prId={prId}&projId={projectId}&repoId={repoId}"
                                                )
                    msg.save()
            else:
                return JsonResponse(genResponseStateInfo(response, 6, "wrong token with this user"))
        except Exception as e:
            return JsonResponse(genUnexpectedlyErrorInfo(response, e))
        return JsonResponse(response)


class GitBranchCommit(View):
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        genResponseStateInfo(response, 0, "git commit ok")

        userId = kwargs.get('userId')
        projectId = kwargs.get('projectId')
        repoId = kwargs.get('repoId')

        files = kwargs.get('files')
        branch = kwargs.get('branch')
        message = kwargs.get('message')
        dstBranch = kwargs.get("dstBranch")
        project = isProjectExists(projectId)
        if project == None:
            return JsonResponse(genResponseStateInfo(response, 1, "project does not exists"))
        userProject = isUserInProject(userId, projectId)
        if userProject == None:
            return JsonResponse(genResponseStateInfo(response, 2, "user not in project"))
        if not UserProjectRepo.objects.filter(project_id=projectId, repo_id=repoId).exists():
            return JsonResponse(genResponseStateInfo(response, 3, "no such repo in project"))
        repo = Repo.objects.get(id=repoId)

        user = User.objects.get(id=userId)
        token = user.token

        if repo == None:
            return JsonResponse(genResponseStateInfo(response, 4, "no such repo"))
        localPath = repo.local_path
        try:
            remotePath = repo.remote_path
            print(validate_token(token))
            if token is not None or not validate_token(token):
                subprocess.run(['git', 'credential-cache', 'exit'], cwd=localPath)
                subprocess.run(["git", "config", "--unset-all", "user.name"], cwd=localPath)
                subprocess.run(["git", "config", "--unset-all", "user.email"], cwd=localPath)
                subprocess.run(['git', 'checkout', branch], cwd=localPath, check=True)
                result = subprocess.run(["git", "checkout", "-b", dstBranch], cwd=localPath, stderr=subprocess.PIPE,
                                        text=True)
                if "fatal" in result.stderr or "403" in result.stderr or "rejected" in result.stderr:
                    response["message"] = result.stderr
                    response["errcode"] = 7
                    return JsonResponse(response)
                subprocess.run(["git", "remote", "add", "tmp", f"https://{token}@github.com/{remotePath}.git"],
                               cwd=localPath)
                for file in files:
                    path = os.path.join(localPath, file.get('path'))
                    content = file.get('content')
                    try:
                        with open(path, 'w') as f:
                            f.write(content)
                    except Exception as e:
                        print(f"Failed to overwrite file {path}: {e}")
                    subprocess.run(["git", "add", path], cwd=localPath)
                subprocess.run(["git", "commit", "-m", message], cwd=localPath)

                result = subprocess.run(["git", "push", "tmp", dstBranch], cwd=localPath, stderr=subprocess.PIPE,
                                        text=True)
                print("err is ", result.stderr)
                if "fatal" in result.stderr or "403" in result.stderr or "rejected" in result.stderr:
                    subprocess.run(["git", "branch", "-D", dstBranch], cwd=localPath)
                    subprocess.run(["git", "remote", "rm", "tmp"], cwd=localPath)
                    response["message"] = result.stderr
                    errcode = 7
                else:
                    result = subprocess.run(["git", "log", "-1", "--pretty=format:%H"], cwd=localPath,
                                            capture_output=True, text=True)
                    current_commit_sha = result.stdout.strip()
                    print(current_commit_sha)
                    Commit.objects.create(repo_id=repo, sha=current_commit_sha, committer_name=user.name,
                                          committer_id=user,
                                          review_status=None)
                    for file in files:
                        FileUserCommit.objects.create(user_id=user,
                                                      repo_id=repo,
                                                      branch=branch, file=file['path'],
                                                      commit_sha=current_commit_sha)
                        # modify Cooperate
                        tmp = FileUserCommit.objects.filter(repo_id=repo, branch=branch, file=file['path']).exclude(
                            user_id=user)
                        if tmp.exists():
                            for item in tmp:
                                user2 = item.user_id
                                if not Cooperate.objects.filter(user1_id=user, user2_id=user2,
                                                                project_id=project).exists():
                                    Cooperate.objects.create(user1_id=user, user2_id=user2, project_id=project)
                                cooperate = Cooperate.objects.get(user1_id=user, user2_id=user2, project_id=project)
                                cooperate.relation += 1
                                cooperate.save()
                                if not Cooperate.objects.filter(user1_id=user2, user2_id=user,
                                                                project_id=project).exists():
                                    Cooperate.objects.create(user1_id=user2, user2_id=user, project_id=project)
                                cooperate = Cooperate.objects.get(user1_id=user2, user2_id=user, project_id=project)
                                cooperate.relation += 1
                                cooperate.save()
                    UserProjectActivity.objects.create(user_id=user, project_id=project,
                                                       option=UserProjectActivity.COMMIT_CODE)

                    content = f"您的项目\"{project.name}\"有新的提交，位于仓库\"{repo.name}\"的分支\"{branch}\"，" \
                              f"请分配审核人员。"
                    for up in UserProject.objects.filter(
                            Q(role=UserProject.ADMIN) | Q(role=UserProject.DEVELOPER),
                            project_id=project
                    ):
                        msg = Notice.objects.create(receiver_id=up.user_id, read=Notice.N, content=content,
                                                    url=f"commitReview/{projectId}/{repoId}/"
                                                        f"{branch}/{current_commit_sha}?branchName={branch}&projId={projectId}&"
                                                        f"repoId={repoId}&commitSha={current_commit_sha}"
                        )
                        msg.save()

                    errcode = 0
                subprocess.run(["git", "remote", "rm", "tmp"], cwd=localPath)
                subprocess.run(["git", "config", "--unset-all", "user.name"], cwd=localPath)
                subprocess.run(["git", "config", "--unset-all", "user.email"], cwd=localPath)
                response['errcode'] = errcode
            else:
                return JsonResponse(genResponseStateInfo(response, 6, "wrong token with this user"))
        except Exception as e:
            subprocess.run(["git", "remote", "rm", "tmp"], cwd=localPath)
            return JsonResponse(genUnexpectedlyErrorInfo(response, e))
        return JsonResponse(response)


class IsProjectReviewer(View):
    def post(self, request):
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        genResponseStateInfo(response, 0, "check reviewer ok")
        userId = kwargs.get('userId')
        projectId = kwargs.get('projectId')
        response['flag'] = 0
        if not UserProject.objects.filter(project_id=projectId, user_id=userId).exists():
            return JsonResponse(genResponseStateInfo(response, 2, "user is not in Project"))
        tmp = UserProject.objects.get(project_id=projectId, user_id=userId)
        if tmp is None or tmp.role == UserProject.NORMAL:
            return JsonResponse(genResponseStateInfo(response, 1, "user is not reviewer"))
        else:
            if tmp.role == UserProject.REVIEWER:
                response['flag'] = 1
            elif tmp.role == UserProject.DEVELOPER:
                response['flag'] = 2
            elif tmp.role == UserProject.ADMIN:
                response['flag'] = 3
            else:
                response['flag'] = 0
            return JsonResponse(response)


def isProjectReviewer(userId, projectId):
    if not UserProject.objects.filter(project_id=projectId, user_id=userId).exists():
        return False
    tmp = UserProject.objects.get(project_id=projectId, user_id=userId)
    if tmp is None or tmp.role == UserProject.NORMAL:
        return False
    else:
        return True


def getCommitComment(commitId, projectId):
    comments = []
    commitComments = CommitComment.objects.filter(commit_id=commitId)
    for commit in commitComments:
        reviewer = User.objects.get(id=commit.reviewer_id_id)
        if UserProject.objects.filter(project_id=projectId, user_id=reviewer.id).exists():
            role = UserProject.objects.get(project_id=projectId, user_id=reviewer.id).role
        else:
            role = None
        comments.append({"commenterName": reviewer.name, "comment": commit.comment, "commenterId": reviewer.id,
                         "commenterRole": role})
    return comments


class GetCommitDetails(View):
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        genResponseStateInfo(response, 0, "get commit ok")
        sha = kwargs.get('sha')
        userId = kwargs.get('userId')
        projectId = kwargs.get('projectId')
        repoId = kwargs.get('repoId')
        branch = kwargs.get('branch')
        project = isProjectExists(projectId)
        if project == None:
            return JsonResponse(genResponseStateInfo(response, 1, "project does not exists"))
        userProject = isUserInProject(userId, projectId)
        if userProject == None:
            return JsonResponse(genResponseStateInfo(response, 2, "user not in project"))
        if not UserProjectRepo.objects.filter(project_id=projectId, repo_id=repoId).exists():
            return JsonResponse(genResponseStateInfo(response, 3, "no such repo in project"))
        repo = Repo.objects.get(id=repoId)
        if repo is None:
            return JsonResponse(genResponseStateInfo(response, 4, "no such repo"))
        if not User.objects.filter(id=userId).exists():
            return JsonResponse(genResponseStateInfo(response, 5, "user is not exist"))
        token = User.objects.get(id=userId).token
        if token is None or validate_token(token) == False:
            return JsonResponse(genResponseStateInfo(response, 6, "invalid token"))

        owner = str.split(repo.remote_path, "/")[0]
        repo_name = str.split(repo.remote_path, "/")[1]
        command = [
            "gh", "api",
            "-H", "Accept: application/vnd.github+json",
            "-H", "X-GitHub-Api-Version: 2022-11-28",
            "-H", f"Authorization: token {token}",
            f"/repos/{owner}/{repo_name}/commits/{sha}"
        ]
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            remotePath = repo.remote_path
            localPath = repo.local_path
            output = result.stdout
            data = json.loads(output)
            commit = {}

            commit["sha"] = data["sha"]

            if not Commit.objects.filter(sha=sha).exists():
                tmp_commit = Commit.objects.create(repo_id=repo, sha=sha,
                                                   committer_name=data["commit"]["committer"]["name"])
            else:
                tmp_commit = Commit.objects.filter(sha=sha)[0]
            changes = []
            for file in data["files"]:
                prev = subprocess.run(['git', 'show', f'{sha}^:{file["filename"]}'], text=True,
                                      capture_output=True,
                                      cwd=localPath)
                if "fatal" in prev.stderr:
                    prev = None
                else:
                    prev = prev.stdout
                next = subprocess.run(['git', 'show', f'{sha}:{file["filename"]}'], text=True,
                                      capture_output=True,
                                      cwd=localPath, check=True)
                patch = file.get("patch", None)
                changes.append({"filename": file["filename"], "status": file["status"], "patch": patch,
                                "prev_file": prev, "now_file": next.stdout})
            commit["files"] = changes
            commit["committer_name"] = tmp_commit.committer_name
            commit["comments"] = getCommitComment(tmp_commit.id, projectId)
            commit["status"] = tmp_commit.review_status
            commit["reviewerName"] = tmp_commit.reviewer_id.name if tmp_commit.reviewer_id is not None else None
            commit["commit_time"] = data["commit"]["committer"]["date"]
            commit["commit_message"] = data["commit"]["message"]
            response["commit"] = commit
            return JsonResponse(response)
        except subprocess.CalledProcessError as e:
            print("命令执行失败:", e)
            print("错误输出:", e.stderr)
            response["message"] = str(e)
            response["errcode"] = -1
            return JsonResponse(response)


class AssignCommitReviewer(View):
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        genResponseStateInfo(response, 0, "assign commit reviewer ok")
        sha = kwargs.get('sha')
        userId = kwargs.get('userId')
        projectId = kwargs.get('projectId')
        repoId = kwargs.get('repoId')
        reviewerId = kwargs.get('reviewerId')
        branch = kwargs.get('branch')
        project = isProjectExists(projectId)
        if project == None:
            return JsonResponse(genResponseStateInfo(response, 1, "project does not exists"))
        userProject = isUserInProject(userId, projectId)
        userProject2 = isUserInProject(reviewerId, projectId)
        if userProject is None or userProject2 is None:
            return JsonResponse(genResponseStateInfo(response, 2, "user not in project"))
        if not UserProjectRepo.objects.filter(project_id=projectId, repo_id=repoId).exists():
            return JsonResponse(genResponseStateInfo(response, 3, "no such repo in project"))
        repo = Repo.objects.get(id=repoId)
        if repo is None:
            return JsonResponse(genResponseStateInfo(response, 4, "no such repo"))
        if not User.objects.filter(id=userId).exists():
            return JsonResponse(genResponseStateInfo(response, 5, "user is not exist"))
        if not User.objects.filter(id=reviewerId).exists():
            return JsonResponse(genResponseStateInfo(response, 6, "reviewer is not exist"))
        if not isProjectReviewer(reviewerId, projectId):
            return JsonResponse(genResponseStateInfo(response, 7, "this is not  reviewer"))
        if not Commit.objects.filter(sha=sha).exists():
            return JsonResponse(genResponseStateInfo(response, 8, "commit is not exists"))
        if not userProject.role == UserProject.DEVELOPER:
            return JsonResponse(genResponseStateInfo(response, 9, "permission denied"))

        tmp_commit = Commit.objects.filter(sha=sha)[0]
        if tmp_commit.reviewer_id is not None:
            return JsonResponse(genResponseStateInfo(response, 10, "can not assign twice"))
        tmp_commit.reviewer_id = User.objects.get(id=reviewerId)
        tmp_commit.save()
        content = f"您有新的提交审核待处理。该提交属于项目\"{project.name}\"下的\"{repo.name}\"仓库\""
        msg = Notice.objects.create(receiver_id=User.objects.get(id=reviewerId), read=Notice.N, content=content,
                                    url=f"commitReview/{projectId}/{repoId}/"
                                        f"{branch}/{sha}?branchName={branch}&projId={projectId}&"
                                        f"repoId={repoId}&commitSha={sha}")
        msg.save()
        return JsonResponse(response)


class AssignPrReviewer(View):
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        genResponseStateInfo(response, 0, "assign pr reviewer ok")
        prId = kwargs.get('prId')
        userId = kwargs.get('userId')
        projectId = kwargs.get('projectId')
        repoId = kwargs.get('repoId')
        reviewerId = kwargs.get('reviewerId')
        project = isProjectExists(projectId)
        if project == None:
            return JsonResponse(genResponseStateInfo(response, 1, "project does not exists"))
        userProject = isUserInProject(userId, projectId)
        userProject2 = isUserInProject(reviewerId, projectId)
        if userProject is None or userProject2 is None:
            return JsonResponse(genResponseStateInfo(response, 2, "user not in project"))
        if not UserProjectRepo.objects.filter(project_id=projectId, repo_id=repoId).exists():
            return JsonResponse(genResponseStateInfo(response, 3, "no such repo in project"))
        repo = Repo.objects.get(id=repoId)
        if repo is None:
            return JsonResponse(genResponseStateInfo(response, 4, "no such repo"))
        if not User.objects.filter(id=userId).exists():
            return JsonResponse(genResponseStateInfo(response, 5, "user is not exist"))
        if not User.objects.filter(id=reviewerId).exists():
            return JsonResponse(genResponseStateInfo(response, 6, "reviewer is not exist"))
        if not isProjectReviewer(reviewerId, projectId):
            return JsonResponse(genResponseStateInfo(response, 7, "this is not  reviewer"))
        if not Pr.objects.filter(pr_number=prId, repo_id=repo).exists():
            return JsonResponse(genResponseStateInfo(response, 8, "pr is not exists"))
        if not userProject.role == UserProject.DEVELOPER:
            return JsonResponse(genResponseStateInfo(response, 9, "permission denied"))

        pr = Pr.objects.filter(pr_number=prId, repo_id=repo)[0]
        if pr.reviewer_id is not None:
            return JsonResponse(genResponseStateInfo(response, 10, "can not assign twice"))
        pr.reviewer_id = User.objects.get(id=reviewerId)
        pr.save()
        content = f"您有新的合并请求审核待处理。该合并请求属于项目\"{project.name}\"下的\"{repo.name}\"仓库\""
        msg = Notice.objects.create(receiver_id=User.objects.get(id=reviewerId), read=Notice.N, content=content,
                                    url=f"prReview/{projectId}/{repoId}/{prId}"
                                        f"?prId={prId}&projId={projectId}&repoId={repoId}")
        msg.save()
        return JsonResponse(response)


class ModifyCommitStatus(View):
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        genResponseStateInfo(response, 0, "modify commit status ok")
        sha = kwargs.get('sha')
        userId = kwargs.get('userId')
        projectId = kwargs.get('projectId')
        repoId = kwargs.get('repoId')
        status = kwargs.get('reviewStatus')
        project = isProjectExists(projectId)
        if project == None:
            return JsonResponse(genResponseStateInfo(response, 1, "project does not exists"))
        userProject = isUserInProject(userId, projectId)
        if userProject == None:
            return JsonResponse(genResponseStateInfo(response, 2, "user not in project"))
        if not UserProjectRepo.objects.filter(project_id=projectId, repo_id=repoId).exists():
            return JsonResponse(genResponseStateInfo(response, 3, "no such repo in project"))
        repo = Repo.objects.get(id=repoId)
        if repo is None:
            return JsonResponse(genResponseStateInfo(response, 4, "no such repo"))
        if not User.objects.filter(id=userId).exists():
            return JsonResponse(genResponseStateInfo(response, 5, "user is not exist"))

        if not isProjectReviewer(userId, projectId):
            return JsonResponse(genResponseStateInfo(response, 6, "permission denied"))
        if not Commit.objects.filter(sha=sha).exists():
            return JsonResponse(genResponseStateInfo(response, 7, "commit is not exists"))

        tmp_commit = Commit.objects.filter(sha=sha)[0]
        if tmp_commit.review_status is not None:
            return JsonResponse(genResponseStateInfo(response, 8, "can not approve/reject twice"))
        if not tmp_commit.reviewer_id == User.objects.get(id=userId):
            return JsonResponse(genResponseStateInfo(response, 9, "you are not this commit's reviewer"))
        if status == 0 or status == 1:
            tmp_commit.review_status = Commit.Y if status == 1 else Commit.N
            tmp_commit.save()
            if status == 1:
                content = f"您的提交已被同意。该提交属于项目\"{project.name}\"下的\"{repo.name}\"仓库\""
            else:
                content = f"您的提交已被拒绝。该提交属于项目\"{project.name}\"下的\"{repo.name}\"仓库\""
            if tmp_commit.committer_id is not None:
                msg = Notice.objects.create(receiver_id=tmp_commit.committer_id, read=Notice.N, content=content)
                msg.save()
        else:
            return JsonResponse(
                genResponseStateInfo(response, 10, "wrong review status, must approve/reject please"))
        return JsonResponse(response)


class CommentCommit(View):
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        genResponseStateInfo(response, 0, "comment commit ok")
        sha = kwargs.get('sha')
        userId = kwargs.get('userId')
        projectId = kwargs.get('projectId')
        repoId = kwargs.get('repoId')
        comment = kwargs.get('comment')
        project = isProjectExists(projectId)
        if project == None:
            return JsonResponse(genResponseStateInfo(response, 1, "project does not exists"))
        userProject = isUserInProject(userId, projectId)
        if userProject == None:
            return JsonResponse(genResponseStateInfo(response, 2, "user not in project"))
        if not UserProjectRepo.objects.filter(project_id=projectId, repo_id=repoId).exists():
            return JsonResponse(genResponseStateInfo(response, 3, "no such repo in project"))
        repo = Repo.objects.get(id=repoId)
        if repo is None:
            return JsonResponse(genResponseStateInfo(response, 4, "no such repo"))
        if not User.objects.filter(id=userId).exists():
            return JsonResponse(genResponseStateInfo(response, 5, "user is not exist"))
        token = User.objects.get(id=userId).token
        if token is None or validate_token(token) == False:
            return JsonResponse(genResponseStateInfo(response, 6, "invalid token"))

        if not isProjectReviewer(userId, projectId):
            return JsonResponse(genResponseStateInfo(response, 7, "permission denied"))

        if not Commit.objects.filter(sha=sha).exists():
            return JsonResponse(genResponseStateInfo(response, 8, "commit is not exists"))

        reviewer = User.objects.get(id=userId)
        tmp_commit = Commit.objects.filter(sha=sha)[0]
        CommitComment.objects.create(commit_id=tmp_commit, reviewer_id=reviewer, comment=comment)
        return JsonResponse(response)


class ShowCanAssociateTasks(View):
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        genResponseStateInfo(response, 0, "show associate tasks ok")
        projectId = kwargs.get('projectId')
        project = isProjectExists(projectId)
        if project == None:
            return JsonResponse(genResponseStateInfo(response, 1, "project does not exists"))
        tasks = Task.objects.filter(project_id=project)
        data = []
        for task in tasks:
            if task.status == Task.COMPLETED:
                continue
            data.append({"taskName": task.name, "taskId": task.id})
        response["data"] = data
        return JsonResponse(response)


class AssociatePrTask(View):
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        genResponseStateInfo(response, 0, "associate pr with task ok")
        userId = kwargs.get('userId')
        projectId = kwargs.get('projectId')
        repoId = kwargs.get('repoId')
        prId = kwargs.get('prId')
        taskId = kwargs.get('taskId')
        project = isProjectExists(projectId)
        if project == None:
            return JsonResponse(genResponseStateInfo(response, 1, "project does not exists"))
        userProject = isUserInProject(userId, projectId)
        user = User.objects.get(id=userId)
        if userProject is None or user is None:
            return JsonResponse(genResponseStateInfo(response, 2, "user not in project"))
        if not UserProjectRepo.objects.filter(project_id=projectId, repo_id=repoId).exists():
            return JsonResponse(genResponseStateInfo(response, 3, "no such repo in project"))
        repo = Repo.objects.get(id=repoId)
        if repo is None:
            return JsonResponse(genResponseStateInfo(response, 4, "no such repo"))
        if not User.objects.filter(id=userId).exists():
            return JsonResponse(genResponseStateInfo(response, 5, "user is not exist"))

        if Pr.objects.filter(pr_number=prId, repo_id=repo).exists():
            pr = Pr.objects.get(pr_number=prId, repo_id=repo)
        else:
            return JsonResponse(genResponseStateInfo(response, 6, f"no sucn pr{prId} in repo{repoId}"))

        if pr.applicant_id != user and pr.applicant_id is not None:
            return JsonResponse(genResponseStateInfo(response, 10, "you can not associate"))

        if not Task.objects.filter(id=taskId, project_id=project).exists():
            return JsonResponse(genResponseStateInfo(response, 7, "no such task in project"))
        task = Task.objects.get(id=taskId)
        if task.status == Task.COMPLETED:
            return JsonResponse(genResponseStateInfo(response, 8, "task is completed"))

        if Pr_Task.objects.filter(pr_id=pr, task_id=task).exists():
            return JsonResponse(genResponseStateInfo(response, 9, f"pr {prId} have already associated task {task.id}"))
        Pr_Task.objects.create(pr_id=pr, task_id=task)

        return JsonResponse(response)


class ResolvePr(View):
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        genResponseStateInfo(response, 0, "pr resolve ok")
        userId = kwargs.get('userId')
        projectId = kwargs.get('projectId')
        repoId = kwargs.get('repoId')
        prId = kwargs.get('prId')
        action = kwargs.get('action')
        project = isProjectExists(projectId)
        if project == None:
            return JsonResponse(genResponseStateInfo(response, 1, "project does not exists"))
        userProject = isUserInProject(userId, projectId)
        user = User.objects.get(id=userId)
        if userProject is None or user is None:
            return JsonResponse(genResponseStateInfo(response, 2, "user not in project"))
        if not UserProjectRepo.objects.filter(project_id=projectId, repo_id=repoId).exists():
            return JsonResponse(genResponseStateInfo(response, 3, "no such repo in project"))
        repo = Repo.objects.get(id=repoId)
        if repo is None:
            return JsonResponse(genResponseStateInfo(response, 4, "no such repo"))
        if not User.objects.filter(id=userId).exists():
            return JsonResponse(genResponseStateInfo(response, 5, "user is not exist"))
        token = user.token
        if token is None or validate_token(token) == False:
            return JsonResponse(genResponseStateInfo(response, 6, "invalid token"))
        if not isProjectReviewer(userId, projectId):
            return JsonResponse(genResponseStateInfo(response, 7, "Insufficient authority"))

        owner = str.split(repo.remote_path, "/")[0]
        repo_name = str.split(repo.remote_path, "/")[1]

        if Pr.objects.filter(pr_number=prId, repo_id=repo).exists():
            pr = Pr.objects.get(pr_number=prId, repo_id=repo)
            if not pr.reviewer_id == user:
                return JsonResponse(genResponseStateInfo(response, 10, "you are not this pr's reviewer"))

        try:
            if action == 0:
                command = [
                    "gh", "api",
                    "--method", "PATCH",
                    "-H", "Accept: application/vnd.github+json",
                    "-H", "X-GitHub-Api-Version: 2022-11-28",
                    "-H", f"Authorization: token {token}",
                    f"/repos/{owner}/{repo_name}/pulls/{prId}",
                    "-f", "state=closed"
                ]
            else:
                command = [
                    "gh", "api",
                    "--method", "PUT",
                    "-H", "Accept: application/vnd.github+json",
                    "-H", "X-GitHub-Api-Version: 2022-11-28",
                    "-H", f"Authorization: token {token}",
                    f"/repos/{owner}/{repo_name}/pulls/{prId}/merge"
                ]

            result = subprocess.run(command, capture_output=True, text=True, check=True)
            print("out is ", result.stdout)
            print("err is ", result.stderr)
            if "conflict" in result.stderr:
                response["message"] = result.stderr
                errcode = 8
            elif "fatal" in result.stderr or "403" in result.stderr or "rejected" in result.stderr:
                response["message"] = result.stderr
                errcode = 9
            else:
                errcode = 0

            if Pr.objects.filter(pr_number=prId, repo_id=repo).exists():
                pr = Pr.objects.get(pr_number=prId, repo_id=repo)
                pr.status = Pr.MERGED if action == 1 else Pr.CLOSED
            else:
                command = [
                    "gh", "api",
                    "-H", "Accept: application/vnd.github+json",
                    "-H", "X-GitHub-Api-Version: 2022-11-28",
                    "-H", f"Authorization: token {token}",
                    f"/repos/{owner}/{repo_name}/pulls/{prId}"
                ]
                output = subprocess.run(command, capture_output=True, text=True, check=True)
                output = json.loads(output.stdout)
                print("+++++++++++\n", output)
                pr = Pr.objects.create(repo_id=repo, src_branch=output["head"]["label"].split(':')[1],
                                       dst_branch=output["base"]["label"].split(':')[1],
                                       pr_number=output["number"], applicant_name=output["user"]["login"],
                                       pr_status=Pr.MERGED if action == 1 else Pr.CLOSED)
            pr.reviewer_id = user
            pr.save()

            if action == 1:
                pr_tasks = Pr_Task.objects.filter(pr_id=pr)
                tasks = [pr_task.task_id for pr_task in pr_tasks]
                for task in tasks:
                    if task.status == Task.COMPLETED:
                        continue
                    task.status = Task.COMPLETED
                    task.complete_time = datetime.datetime.now()
                    print(task.id, " is completed with pr")
                    task.save()
                    subtasks = Task.objects.filter(parent_id=task.id)
                    for i in subtasks:
                        if i.status == Task.COMPLETED:
                            continue
                        i.status = Task.COMPLETED
                        i.complete_time = datetime.datetime.now()
                        print(i.id, " is completed with pr")
                        i.save()
            UserProjectActivity.objects.create(user_id=user, project_id=project,
                                               option=UserProjectActivity.FINISH_TASK)
            response['errcode'] = errcode
            if errcode == 0:
                if action == 1:
                    content = f"您的合并请求已被同意。该pr属于项目\"{project.name}\"下的\"{repo.name}\"仓库\""
                else:
                    content = f"您的合并请求已被拒绝。该pr属于项目\"{project.name}\"下的\"{repo.name}\"仓库\""
                if pr.applicant_id is not None:
                    msg = Notice.objects.create(receiver_id=pr.applicant_id, read=Notice.N, content=content)
                    msg.save()
            return JsonResponse(response)
        except subprocess.CalledProcessError as e:
            print("命令执行失败:", e)
            print("错误输出:", e.stderr)
            response["message"] = e.stderr
            response["errcode"] = -1
            return JsonResponse(response)


def getPrStatus(status, merged):
    if status == "closed" and merged:
        return Pr.MERGED
    elif status == "open":
        return Pr.OPEN
    elif status == "closed" and not merged:
        return Pr.CLOSED
    else:
        return Pr.DRAFT


def parsePrStatus(status):
    if status == 1:
        return "open"
    elif status == 2:
        return "closed"
    elif status == 3:
        return "merged"
    else:
        return "draft"


class GetPrDetails(View):
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        genResponseStateInfo(response, 0, "get pr details ok")
        prId = kwargs.get('prId')
        userId = kwargs.get('userId')
        projectId = kwargs.get('projectId')
        repoId = kwargs.get('repoId')

        project = isProjectExists(projectId)
        if project == None:
            return JsonResponse(genResponseStateInfo(response, 1, "project does not exists"))
        userProject = isUserInProject(userId, projectId)
        if userProject == None:
            return JsonResponse(genResponseStateInfo(response, 2, "user not in project"))
        if not UserProjectRepo.objects.filter(project_id=projectId, repo_id=repoId).exists():
            return JsonResponse(genResponseStateInfo(response, 3, "no such repo in project"))
        repo = Repo.objects.get(id=repoId)
        if repo is None:
            return JsonResponse(genResponseStateInfo(response, 4, "no such repo"))
        if not User.objects.filter(id=userId).exists():
            return JsonResponse(genResponseStateInfo(response, 5, "user is not exist"))
        token = User.objects.get(id=userId).token
        if token is None or validate_token(token) == False:
            return JsonResponse(genResponseStateInfo(response, 6, "invalid token"))

        owner = str.split(repo.remote_path, "/")[0]
        repo_name = str.split(repo.remote_path, "/")[1]
        command = [
            "gh", "api",
            "-H", "Accept: application/vnd.github+json",
            "-H", "X-GitHub-Api-Version: 2022-11-28",
            "-H", f"Authorization: token {token}",
            f"/repos/{owner}/{repo_name}/pulls/{prId}"
        ]
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            output = result.stdout
            jsonOutput = json.loads(output)
            if not Pr.objects.filter(pr_number=prId, repo_id=repo).exists():
                pr = Pr.objects.create(repo_id=repo, src_branch=jsonOutput["head"]["label"].split(':')[1],
                                       dst_branch=jsonOutput["base"]["label"].split(':')[1],
                                       pr_number=prId, applicant_name=jsonOutput["user"]["login"])
            else:
                pr = Pr.objects.get(repo_id=repo, pr_number=prId)
            pr.pr_status = getPrStatus(jsonOutput["state"], jsonOutput["merged"])
            pr.save()
            data = {
                "state": parsePrStatus(pr.pr_status),
                "title": jsonOutput["title"],
                "body": jsonOutput["body"],
                "reviewerName": pr.reviewer_id.name if pr.reviewer_id is not None else None,
                "reviewerId": pr.reviewer_id.id if pr.reviewer_id is not None else None, 
                "merge_commit_sha": jsonOutput["merge_commit_sha"],
                "branch": jsonOutput["head"]["ref"],
                "base": jsonOutput["base"]["ref"],
                "pr_applicant": jsonOutput["user"]["login"],
                "created_time": jsonOutput["created_at"],
                "updated_time": jsonOutput["updated_at"],
                "closed_time": jsonOutput["closed_at"],
                "merged_time": jsonOutput["merged_at"],
                "commits": []
            }
            command = [
                "gh", "api",
                "-H", "Accept: application/vnd.github+json",
                "-H", "X-GitHub-Api-Version: 2022-11-28",
                "-H", f"Authorization: token {token}",
                f"/repos/{owner}/{repo_name}/pulls/{prId}/commits"
            ]
            res = subprocess.run(command, capture_output=True, text=True, check=True)
            out = json.loads(res.stdout)
            for commit in out:
                sha = commit["sha"]
                if Commit.objects.filter(sha=sha).exists():
                    commit_obj = Commit.objects.get(sha=sha)
                else:
                    commit_obj = Commit.objects.create(
                        repo_id=repo,
                        sha=sha,
                        committer_name=commit["commit"]["committer"]["name"]
                    )
                data["commits"].append({"commitId": commit_obj.pk,
                                        "sha": sha, "author": commit["commit"]["author"]["name"],
                                        "time": commit["commit"]["author"]["date"],
                                        "message": commit["commit"]["message"]})
            response["data"] = data
            return JsonResponse(response)
        except subprocess.CalledProcessError as e:
            print("命令执行失败:", e)
            print("错误输出:", e.stderr)
            response["message"] = e.stderr
            response["errcode"] = -1
            return JsonResponse(response)


class GetFileCommits(View):
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        genResponseStateInfo(response, 0, "get user commits for file ok")
        userId = kwargs.get('userId')
        projectId = kwargs.get('projectId')
        repoId = kwargs.get('repoId')
        file = kwargs.get('file')
        branch = kwargs.get('branch')

        project = isProjectExists(projectId)
        if project == None:
            return JsonResponse(genResponseStateInfo(response, 1, "project does not exists"))
        userProject = isUserInProject(userId, projectId)
        if userProject == None:
            return JsonResponse(genResponseStateInfo(response, 2, "user not in project"))
        if not UserProjectRepo.objects.filter(project_id=projectId, repo_id=repoId).exists():
            return JsonResponse(genResponseStateInfo(response, 3, "no such repo in project"))
        repo = Repo.objects.get(id=repoId)
        if repo is None:
            return JsonResponse(genResponseStateInfo(response, 4, "no such repo"))
        if not User.objects.filter(id=userId).exists():
            return JsonResponse(genResponseStateInfo(response, 5, "user is not exist"))

        fileUserCommits = FileUserCommit.objects.filter(repo_id=repoId, file=file, branch=branch)
        commits = {}
        for fuc in fileUserCommits:
            if not (fuc.user_id_id in commits):
                commits[fuc.user_id_id] = []
            commits[fuc.user_id_id].append(fuc.commit_sha)
            print(fuc.commit_sha)
        data = []
        for key in commits.keys():
            data.append({"userId": key, "userName": User.objects.get(id=key).name, "commits": commits[key],
                         "count": len(commits[key])})
        response["data"] = data
        return JsonResponse(response)


class GetPrAssociatedTasks(View):
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        genResponseStateInfo(response, 0, "get pr associated tasks ok")
        prId = kwargs.get('prId')
        repoId = kwargs.get('repoId')
        repo = Repo.objects.get(id=repoId)
        if repo is None:
            return JsonResponse(genResponseStateInfo(response, 2, "no such repo"))
        if not Pr.objects.filter(pr_number=prId, repo_id=repo).exists():
            return JsonResponse(genResponseStateInfo(response, 1, "pr does not exist"))
        pr = Pr.objects.get(pr_number=prId, repo_id=repo)
        data = []
        pt_set = set()
        for pt in Pr_Task.objects.filter(pr_id=pr.id):
            if (prId, pt.task_id_id) in pt_set:
                continue
            else:
                pt_set.add((prId, pt.task_id_id))
            task = Task.objects.get(id=pt.task_id_id)
            data.append({
                "taskName": task.name,
                "taskId": task.id
            })
        response["data"] = data
        return JsonResponse(response)


class DeletePrTask(View):
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        genResponseStateInfo(response, 0, "delete pr associated task ok")

        userId = kwargs.get('userId')
        projectId = kwargs.get('projectId')
        repoId = kwargs.get('repoId')
        prId = kwargs.get('prId')
        taskId = kwargs.get('taskId')

        project = isProjectExists(projectId)
        if project == None:
            return JsonResponse(genResponseStateInfo(response, 1, "project does not exists"))
        userProject = isUserInProject(userId, projectId)
        user = User.objects.get(id=userId)
        if userProject is None or user is None:
            return JsonResponse(genResponseStateInfo(response, 2, "user not in project"))
        if not UserProjectRepo.objects.filter(project_id=projectId, repo_id=repoId).exists():
            return JsonResponse(genResponseStateInfo(response, 3, "no such repo in project"))
        repo = Repo.objects.get(id=repoId)
        if repo is None:
            return JsonResponse(genResponseStateInfo(response, 4, "no such repo"))
        if not User.objects.filter(id=userId).exists():
            return JsonResponse(genResponseStateInfo(response, 5, "user is not exist"))

        if Pr.objects.filter(pr_number=prId, repo_id=repo).exists():
            pr = Pr.objects.get(pr_number=prId, repo_id=repo)
        else:
            return JsonResponse(genResponseStateInfo(response, 6, "no such pr in repo"))

        if pr.applicant_id != user and pr.applicant_id is not None:
            return JsonResponse(genResponseStateInfo(response, 9, "you can not delete associate"))

        if not Task.objects.filter(id=taskId, project_id=project).exists():
            return JsonResponse(genResponseStateInfo(response, 7, "no such task in project"))
        task = Task.objects.get(id=taskId)
        if task.status == Task.COMPLETED:
            return JsonResponse(genResponseStateInfo(response, 8, "task is completed"))

        try:
            prTask = Pr_Task.objects.get(pr_id=pr.id, task_id=taskId)
            prTask.delete()
        except Exception as e:
            return JsonResponse(genUnexpectedlyErrorInfo(response, e))

        return JsonResponse(response)
