# 如何将本项目上传到 GitHub

本指南将帮助您将 `ai_manga_workflow` 项目上传到 GitHub。

## ⚠️ 重要安全提醒

**请务必确保 `.env` 文件已被添加到 `.gitignore` 中！**
`.env` 文件包含您的 `VOLCENGINE_ACCESS_KEY` 等敏感密钥，绝对不能上传到公开仓库。
我已经为您创建了 `.gitignore` 文件并排除了它。

## 第一步：在 GitHub 上创建仓库

1.  登录您的 [GitHub](https://github.com/) 账号。
2.  点击右上角的 **+** 号，选择 **New repository**。
3.  **Repository name**: 输入项目名称，例如 `ai_manga_workflow`。
4.  **Description**: (可选) 输入项目描述，例如 "Intelligent Manga Video Generation Workflow based on AgentKit"。
5.  **Public/Private**: 根据需要选择 Public（公开）或 Private（私有）。
6.  **Initialize this repository with**: 不要勾选任何选项（不要勾选 Add a README, .gitignore, license），因为我们本地已经有了。
7.  点击 **Create repository**。

## 第二步：在本地终端执行上传命令

在 Trae 的终端中，确保当前目录是 `/Users/bytedance/python_projects/ai_manga_workflow`，然后依次执行以下命令：

```bash
# 1. 初始化 git 仓库
git init

# 2. 添加所有文件到暂存区 (会自动忽略 .gitignore 中的文件)
git add .

# 3. 提交更改
git commit -m "Initial commit: AI Manga Workflow with AgentKit"

# 4. 关联远程仓库
# 请将下面的 URL 替换为您在第一步中创建的仓库地址
# 例如: git remote add origin https://github.com/your-username/ai_manga_workflow.git
git remote add origin <YOUR_GITHUB_REPOSITORY_URL>

# 5. 推送到 GitHub
git branch -M main
git push -u origin main
```

## 第三步：后续开发

后续如果您修改了代码，只需执行以下命令即可更新到 GitHub：

```bash
git add .
git commit -m "描述您的修改"
git push
```

## 关于部署

其他人克隆您的项目后，需要：
1.  根据 `README.md` 中的说明，在本地创建一个新的 `.env` 文件。
2.  填入他们自己的 `VOLCENGINE_ACCESS_KEY` 和其他配置信息。
3.  安装依赖 (`pip install -r requirements.txt`) 即可运行。
