import subprocess
from typing import Union, List


def add_issue_labels(remote_path: str, issue_number: int, labels: Union[str, List[str]], token: str) -> bool:
    """
    为指定的 Issue 添加标签

    Args:
        remote_path: 仓库路径 (格式: "owner/repo")
        issue_number: Issue 编号
        labels: 要添加的标签，可以是单个字符串或字符串列表
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

        # 添加所有标签
        for label in labels:
            command.append("-f")
            command.append(f"labels[]={label}")
        print(command)
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.returncode == 0

    except subprocess.CalledProcessError as e:
        print(f"添加 Issue 标签失败: {e.stderr}")
        return False


def add_pr_labels(remote_path: str, pr_number: int, labels: Union[str, List[str]], token: str) -> bool:
    """
    为指定的 PR 添加标签
    注意：在 GitHub API 中，PR 也被视为一种特殊的 Issue，使用相同的标签接口

    Args:
        remote_path: 仓库路径 (格式: "owner/repo")
        pr_number: PR 编号
        labels: 要添加的标签，可以是单个字符串或字符串列表
        token: GitHub token

    Returns:
        bool: 是否成功添加标签
    """
    return add_issue_labels(remote_path, pr_number, labels, token)


def test_add_issue_labels():
    labels = ["bug2"]
    add_issue_labels("BUAAAutoHub/AutoHub", 1, labels, "11")


def test_add_pr_labels():
    labels = ["bug2"]
    add_pr_labels("BUAAAutoHub/AutoHub", 2, labels, "11")


if __name__ == "__main__":
    test_add_issue_labels()
    test_add_pr_labels()
