import subprocess
import json

from typing import Union, List, Dict


def add_labels(remote_path: str, issue_number: int, labels: Union[str, List[str]], token: str) -> bool:
    """
    Date        : 2025/4/24
    Author      : yanfan
    Description : 为指定的 Issue/PR 添加标签
    Args:
        remote_path: 仓库路径 (格式: "BUAAAutoHub/AutoHub")
        issue_number: Issue/PR 编号
        labels: 要添加的标签，可以是单个字符串或字符串列表，必须是已有的label
        token: GitHub token
    Returns:
        bool: 是否成功添加标签
    """
    if isinstance(labels, str):
        labels = [labels]

    try:
        command = [
            "gh",
            "api",
            "-H",
            "Accept: application/vnd.github+json",
            "-H",
            "X-GitHub-Api-Version: 2022-11-28",
            "-H",
            f"Authorization: token {token}",
            f"/repos/{remote_path}/issues/{issue_number}/labels",
        ]

        for label in labels:
            command.append("-f")
            command.append(f"labels[]={label}")
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.returncode == 0

    except subprocess.CalledProcessError as e:
        print(f"添加标签失败: {e.stderr}")
        return False

def _get_item_content(self, item_type: str, item_number: int) -> Dict:
    """获取PR或Issue的内容"""
    if item_type == 'PR':
        command = [
            "gh",
            "api",
            "-H",
            "Accept: application/vnd.github+json",
            "-H",
            f"Authorization: token {self.token}",
            f"/repos/{self.repo.remote_path}/pulls/{item_number}",
        ]
    else:  # ISSUE
        command = [
            "gh",
            "api",
            "-H",
            "Accept: application/vnd.github+json",
            "-H",
            f"Authorization: token {self.token}",
            f"/repos/{self.repo.remote_path}/issues/{item_number}",
        ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        return {}
    data = json.loads(result.stdout)
    return {
        "title": data.get("title", ""),
        "body": data.get("body", ""),
        "labels": [label["name"] for label in data.get("labels", [])],
        "state": data.get("state", ""),
        "created_at": data.get("created_at", ""),
        "updated_at": data.get("updated_at", ""),
    }

def _add_comment(self, item_type: str, item_number: int, message: str):
    """添加评论"""
    if item_type == 'PR':
        endpoint = f"/repos/{self.repo.remote_path}/issues/{item_number}/comments"
    else:  # ISSUE
        endpoint = f"/repos/{self.repo.remote_path}/issues/{item_number}/comments"
    command = [
        "gh",
        "api",
        "-H",
        "Accept: application/vnd.github+json",
        "-H",
        f"Authorization: token {self.token}",
        endpoint,
        "-f",
        f"body={message}",
    ]
    subprocess.run(command, capture_output=True, text=True)

def _add_labels(self, item_type: str, item_number: int, labels: List[str]):
    """添加标签"""
    if not labels:
        return
    if item_type == 'PR':
        endpoint = f"/repos/{self.repo.remote_path}/issues/{item_number}/labels"
    else:  # ISSUE
        endpoint = f"/repos/{self.repo.remote_path}/issues/{item_number}/labels"
    command = [
        "gh",
        "api",
        "-H",
        "Accept: application/vnd.github+json",
        "-H",
        f"Authorization: token {self.token}",
        endpoint,
        "-f",
        f"labels={','.join(labels)}",
    ]
    subprocess.run(command, capture_output=True, text=True)