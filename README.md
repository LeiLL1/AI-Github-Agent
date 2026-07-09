# AI GitHub Agent

AI GitHub Agent 是一个用于发现、理解和学习 GitHub 开源项目的 Streamlit 应用。

## 功能

- 根据关键词搜索 GitHub Repository
- 基于 Stars、Forks、更新时间生成推荐结果
- 获取 README、目录结构、语言、Release、Issues、Pull Requests
- 生成《3 分钟读懂该项目》
- 分析项目结构、核心模块和技术栈
- 生成项目学习路线
- 支持基于 README 和源码结构的自然语言问答
- 支持多个 Repository 对比
- 收藏项目、保存分析报告和学习笔记
- 生成 GitHub Daily Report

## 环境要求

建议使用 Python 3.10 或更高版本。仓库中旧的 `venv` 如果不可用，请新建环境。

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 配置

在 `.env` 中配置 API key：

```env
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_API_BASE=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat

GITHUB_TOKEN=your_github_token
DEFAULT_LLM_PROVIDER=deepseek
```

`GITHUB_TOKEN` 可选，但配置后 GitHub API 限额更高。

## 启动

```powershell
streamlit run app.py
```

主应用的侧边栏包含全部 V1.0 功能入口。

