# 重构后的文件组织架构

## 文件目录结构

```
myApp/
├── apps/                           # 核心功能应用模块
│   ├── __init__.py
│   ├── user/                      # 基础功能（用户、权限等）
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py           # 用户模型
│   │   │   └── organization.py  # 组织模型
│   │   └── views/
│   ├── projects/                  # 项目管理模块
│   │   ├── models/
│   │   │   └── project.py        # 项目/里程碑模型
│   │   └── github/               # GitHub集成子模块
│   │       ├── webhooks.py       # Webhook处理器
│   │       └── sync.py           # 仓库同步逻辑
│   ├── ai_tools/                 # AI功能模块
│   │   ├── ml_models/            # 机器学习模型（可.gitignore）
│   │   ├── predictors.py         # 预测功能（工时/风险）
│   │   └── code_analyzer.py      # 智能代码分析
│   └── integrations/             # 第三方集成
│       ├── github_api.py         # GitHub API封装
│       └── ai_services.py        # AI服务接口（如OpenAI）
├── utils/                        # 通用工具
│   ├── decorators.py            # 自定义装饰器
│   ├── github_webhook_validator.py  # Webhook签名验证
│   └── ai_pipelines/            # AI数据处理管道
├── requirements/
│   ├── base.txt                 # 核心依赖
│   ├── ai.txt                   # AI相关依赖
│   └── github.txt               # GitHub集成依赖
├── tests/
│   ├── test_github_api.py
│   └── test_ai_predictions.py
└── manage.py
```