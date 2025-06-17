
## 安装环境（linux）

git clone git@github.com:BUAAAutoHub/AutoHub.git

### backend：

```bash
conda create -yn autohub python=3.12 # 建议用conda
conda activate autohub
cd AutoHub/
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple # 换源
pip install -r requirements.txt
sudo apt install gh
# source rebuildsqlist.sh
```

### sonarqube
```bash
sudo docker pull sonarqube # 网不好，可以本地下载再上传
sudo docker run -d --name sonarqube -p 9000:9000 -e SONAR_ES_BOOTSTRAP_CHECKS_DISABLE=true sonarqube:latest
export PATH=/home/auto/sonarqube/sonar-scanner-7.1.0.4889-linux-x64/bin:$PATH
```

### ollama
bash install_ollama.sh
ollama serve

### frontend：

```bash
sudo apt install nodejs npm
sudo npm install -g pnpm
pnpm install
```

### 注意

在项目中全局搜索`10.254.47.34`，替换为机器的ip


## 运行
### backend：
注意后端terminal最好挂上梯子
同时需要初始化gh，可参照https://zhuanlan.zhihu.com/p/601200139
```bash
python manage.py runserver 0.0.0.0:8000
```


### frontend：

```bash
pnpm run dev
```

#### 管理员账号密码

**username**: system
**password**: 111111

