from django.db import models


class User(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    create_time = models.DateTimeField(auto_now_add=True)
    last_login_time = models.DateTimeField()
    NORMAL = 'A'
    ILLEGAL = 'B'
    STATUS_LIST = (
        (NORMAL, 'NORMAL'),
        (ILLEGAL, 'ILLEGAL'),
    )

    STUDENT = 1
    ASSISTANT = 2
    TEACHER = 3
    AUTH_LIST = (
        (STUDENT, 'STUDENT'),
        (ASSISTANT, 'ASSISTANT'),
        (TEACHER, 'TEACHER')
    )
    auth = models.IntegerField(choices=AUTH_LIST, default=STUDENT)

    RED = 'A'
    ORANGE = 'B'
    GREEN = 'C'
    BLUE = 'D'
    PURPLE = 'E'
    COLOR_LIST = (
        (RED, 'RED'),
        (ORANGE, 'ORG'),
        (GREEN, 'GREEN'),
        (BLUE, 'BLUE'),
        (PURPLE, 'PUR')
    )
    color = models.CharField(max_length=10, choices=COLOR_LIST)
    status = models.CharField(max_length=2, choices=STATUS_LIST)
    token = models.CharField(max_length=255, null=True)


class Project(models.Model):
    id = models.AutoField(primary_key=True)
    create_time = models.DateTimeField(auto_now_add=True)
    progress = models.IntegerField(default=0)
    COMPLETED = 'A'
    INPROGRESS = 'B'
    NOTSTART = 'C'
    ILLEGAL = 'D'
    NORMAL = 'A'
    DISABLE = 'B'
    STATUS_LIST = (
        (COMPLETED, 'COMPLETED'),
        (INPROGRESS, 'INPROGRESS'),
        (NOTSTART, 'NOTSTART'),
        (ILLEGAL, 'ILLEGAL'),
    )

    ACCESS_LIST = (
        (NORMAL, 'NORMAL'),
        (DISABLE, 'DISABLE'),
    )
    status = models.CharField(max_length=2, choices=STATUS_LIST)
    access = models.CharField(max_length=2, choices=ACCESS_LIST, default=NORMAL)
    name = models.CharField(max_length=255)
    outline = models.TextField()
    manager_id = models.ForeignKey(User, on_delete=models.CASCADE)


class Task(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    create_time = models.DateTimeField(auto_now_add=True)
    start_time = models.DateTimeField(default="2050-12-31")
    complete_time = models.DateTimeField(default="2050-12-31")
    deadline = models.DateTimeField()
    outline = models.TextField()
    COMPLETED = 'A'
    INPROGRESS = 'B'
    NOTSTART = 'C'
    STATUS_LIST = (
        (COMPLETED, 'COMPLETED'),
        (INPROGRESS, 'INPROGRESS'),
        (NOTSTART, 'NOTSTART'),
    )
    status = models.CharField(max_length=2, choices=STATUS_LIST)
    contribute_level = models.IntegerField(default=0)
    parent_id = models.ForeignKey('self', on_delete=models.CASCADE, null=True)
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)

    BUG = 'A'
    ENHANCE = 'B'
    FEATURE = 'C'
    DUPLICATE = "D"
    QUESTION = "E"
    LABEL_LIST = (
        (BUG, 'BUG'),
        (ENHANCE, 'ENHANCEMENT'),
        (FEATURE, 'FEATURE'),
        (DUPLICATE, "DUPLICATE"),
        (QUESTION, "QUESTION")
    )
    task_label = models.CharField(max_length=255, choices=LABEL_LIST, default=None, null=True)


class TaskReview(models.Model):
    id = models.AutoField(primary_key=True)
    task_id = models.ForeignKey(Task, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    create_time = models.DateTimeField()


class Group(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    outline = models.TextField()
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE)
    PRIVATE = 'PRI'
    PUBLIC = 'PUB'
    TYPE_LIST = (
        (PRIVATE, 'PRIVATE'),
        (PUBLIC, 'PUBLIC')
    )
    type = models.CharField(max_length=5, choices=TYPE_LIST)


class Notice(models.Model):
    id = models.AutoField(primary_key=True)
    content = models.TextField()
    receiver_id = models.ForeignKey(User, on_delete=models.CASCADE)
    Y = 'Y'
    N = 'N'
    YON = (
        (Y, 'Y'),
        (N, 'N'),
    )
    read = models.CharField(max_length=3, choices=YON, default=N)
    create_time = models.DateTimeField(auto_now_add=True)
    url = models.CharField(max_length=255,default="")


class MyFile(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    path = models.CharField(max_length=255)
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE)


class Message(models.Model):
    id = models.AutoField(primary_key=True)
    TEXT = 'A'
    PIC = 'B'
    FILE = 'C'
    TYPE_LIST = (
        (TEXT, 'TEXT'),
        (PIC, 'PIC'),
        (FILE, 'FILE'),
    )
    CHECKED, UNCHECKED = 'C', 'UC'
    STATUS_LIST = (
        (CHECKED, 'CHECKED'),
        (UNCHECKED, 'UNCHECKED'),
    )
    status = models.CharField(max_length=2, choices=STATUS_LIST)
    type = models.CharField(max_length=2, choices=TYPE_LIST)
    content = models.CharField(max_length=255)  # TODO use FILE
    group_id = models.ForeignKey(Group, on_delete=models.CASCADE)
    send_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receive_user')
    receive_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='send_user')
    time = models.DateTimeField(auto_now_add=True)


class Document(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    outline = models.TextField()
    content = models.TextField()
    time = models.DateTimeField(auto_now_add=True)
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)


class UserCollectDoc(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    doc_id = models.ForeignKey(Document, on_delete=models.CASCADE)


class UserAccessDoc(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    doc_id = models.ForeignKey(Document, on_delete=models.CASCADE)


class UserDocLock(models.Model):
    doc_id = models.ForeignKey(Document, on_delete=models.CASCADE, unique=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)


class Post(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    content = models.TextField()
    post_time = models.TimeField(auto_now_add=True)
    PROJ_ALL = 'PROJ_ALL'
    PROJ_ONE = 'PROJ_ONE'
    SYS_PROJ = 'SYS_PROJ'
    SYS_ALL = 'SYS_ALL'
    TYPE_LIST = (
        (PROJ_ALL, 'PROJ_ALL'),
        (PROJ_ONE, 'PROJ_ONE'),
        (SYS_PROJ, 'SYS_PROJ'),
        (SYS_ALL, 'SYS_ALL'),
    )
    post_type = models.CharField(max_length=10, choices=TYPE_LIST)
    receiver_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_id')
    is_received = models.BooleanField()
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='receiver_id')
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)


class Repo(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    local_path = models.CharField(max_length=255)  # TODO
    remote_path = models.CharField(max_length=255)


class Progress(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    COMMIT = 'A'
    ISSUE = 'B'
    PR = 'C'
    TYPE_LIST = (
        (COMMIT, 'COMMIT'),
        (ISSUE, 'ISSUE'),
        (PR, 'PR'),
    )
    type = models.CharField(max_length=2, choices=TYPE_LIST)
    remote_path = models.CharField(max_length=255)
    repo_id = models.ForeignKey(Repo, on_delete=models.CASCADE)


class UserProject(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE)
    NORMAL = 'A'
    ADMIN = 'B'
    DEVELOPER = "C"
    REVIEWER = "D"
    ROLE_LIST = (
        (NORMAL, 'NORMAL'),
        (ADMIN, 'ADMIN'),
        (DEVELOPER, 'DEVELOPER'),
        (REVIEWER, 'REVIEWER'),
    )

    role = models.CharField(max_length=3, choices=ROLE_LIST)
    Y = 'Y'
    N = 'N'
    YON = (
        (Y, 'Y'),
        (N, 'N'),
    )

    commitAuth = models.CharField(max_length=3, choices=YON, default=N)
    editAuth = models.CharField(max_length=3, choices=YON, default=N)
    viewAuth = models.CharField(max_length=3, choices=YON, default=Y)


class UserGroup(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    NORMAL = 'A'
    ADMIN = 'B'
    ROLE_LIST = (
        (NORMAL, 'NORMAL'),
        (ADMIN, 'ADMIN'),
    )
    role = models.CharField(max_length=2, choices=ROLE_LIST)


class UserTask(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    task_id = models.ForeignKey(Task, on_delete=models.CASCADE)


class UserDocument(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    document_id = models.ForeignKey(Document, on_delete=models.CASCADE)


class UserProjectRepo(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE)
    repo_id = models.ForeignKey(Repo, on_delete=models.CASCADE)


class ProgressTask(models.Model):
    repo_id = models.ForeignKey(Repo, on_delete=models.CASCADE)
    progress_id = models.ForeignKey(Progress, on_delete=models.CASCADE)


class AssistantProject(models.Model):
    assistant_id = models.ForeignKey(User, on_delete=models.CASCADE)
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE)


class Commit(models.Model):
    id = models.AutoField(primary_key=True)
    repo_id = models.ForeignKey(Repo, on_delete=models.CASCADE)
    sha = models.CharField(max_length=255)
    committer_name = models.CharField(max_length=255)
    committer_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, default=None)
    Y = 'Y'
    N = 'N'
    YON = (
        (Y, 'Y'),
        (N, 'N'),
    )
    review_status = models.CharField(max_length=3, choices=YON, default=None, null=True)
    reviewer_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, default=None,
                                    related_name='reviewer_commits')


class CommitComment(models.Model):
    commit_id = models.ForeignKey(Commit, on_delete=models.CASCADE)
    reviewer_id = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.CharField(max_length=255)


class Pr(models.Model):
    id = models.AutoField(primary_key=True)
    applicant_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, default=None)
    applicant_name = models.CharField(max_length=255, null=True, default=None)
    repo_id = models.ForeignKey(Repo, on_delete=models.CASCADE)
    reviewer_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, default=None, related_name='pr_reviewer')
    src_branch = models.CharField(max_length=255)
    dst_branch = models.CharField(max_length=255)
    pr_number = models.IntegerField(default=0)
    OPEN = 1
    CLOSED = 2
    MERGED = 3
    DRAFT = 4
    PR_STATUS_LIST = {
        (OPEN, 1),
        (CLOSED, 2),
        (MERGED, 3),
        (DRAFT, 4)
    }
    pr_status = models.IntegerField(choices=PR_STATUS_LIST, default=None, null=True)


class Pr_Task(models.Model):
    pr_id = models.ForeignKey(Pr, on_delete=models.CASCADE)
    task_id = models.ForeignKey(Task, on_delete=models.CASCADE)


class Pr_Comment(models.Model):
    pr_id = models.ForeignKey(Pr, on_delete=models.CASCADE)
    commenter_id = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.CharField(max_length=255)


class Cooperate(models.Model):
    user1_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user1_cooperate")
    user2_id = models.ForeignKey(User, on_delete=models.CASCADE)
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE)
    relation = models.IntegerField(default=0)


class FileUserCommit(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    repo_id = models.ForeignKey(Repo, on_delete=models.CASCADE)
    branch = models.CharField(max_length=255)
    file = models.CharField(max_length=255)
    commit_sha = models.CharField(max_length=255)


class UserProjectActivity(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE)
    complete_time = models.DateTimeField(default="2050-12-31")
    FINISH_TASK = "A"
    COMMIT_CODE = "B"
    OPTION_LIST = {
        (FINISH_TASK, "A"),
        (COMMIT_CODE, "B")
    }
    option = models.CharField(max_length=1, choices=OPTION_LIST, default=None, null=True)

class KnowledgeDatabase(models.Model):
    project_id  = models.ForeignKey(Project, on_delete=models.CASCADE)
    question    = models.CharField(max_length=4096)
    answer      = models.CharField(max_length=4096)
    record_time = models.DateTimeField(default="2050-12-31")

class Bot(models.Model):
    '''
        Date        :   2025/4/21
        Author      :   tangling
        Description :   model for BOT(in github)
    '''
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    token = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class ProjectRepoBot(models.Model):
    '''
        Date        :   2025/4/21
        Author      :   tangling
        Description :   model for ProjectBot
    '''
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE)
    repo = models.ForeignKey(Repo, on_delete=models.CASCADE)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

class BotRule(models.Model):
    """BOT规则配置"""
    repo = models.ForeignKey(Repo, on_delete=models.CASCADE)
    rule_type = models.CharField(max_length=20)  # 'PR' or 'ISSUE'
    rule_name = models.CharField(max_length=100)  # 规则名称
    rule_content = models.TextField()  # 规则内容（JSON格式）
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class BotLabel(models.Model):
    """BOT标签配置"""
    repo = models.ForeignKey(Repo, on_delete=models.CASCADE)
    label_name = models.CharField(max_length=50)
    label_color = models.CharField(max_length=7)  # hex color code
    label_description = models.TextField()
    is_active = models.BooleanField(default=True)
