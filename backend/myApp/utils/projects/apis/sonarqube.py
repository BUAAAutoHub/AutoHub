from sonarqube import SonarQubeClient

# 初始化 SonarQube 客户端
sonar = SonarQubeClient(sonarqube_url="http://localhost:9000", token="your_sonar_token")

# 示例：获取项目列表
projects = sonar.projects.search_projects()
print(projects)
