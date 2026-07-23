# AI GitHub Agent

AI GitHub Agent 是一个面向开发者的 GitHub 开源项目发现、分析和学习助手。项目基于 Streamlit 构建，能够搜索 GitHub 仓库、读取 README 和目录结构、识别技术栈与核心模块，并结合可选的大模型能力生成项目解读、架构分析、问答、对比报告和学习路线。

即使没有配置大模型 API Key，应用也可以通过规则分析完成基础搜索、项目结构识别、推荐评分和兜底报告；配置 DeepSeek、OpenAI 或 Anthropic 后，可以获得更完整的中文总结和自然语言分析。

## 功能特性

- GPT 风格智能聊天：普通问题自然对话，明确提出找项目时自动切换到 GitHub 推荐流程，并支持连续追问筛选。
- GitHub 项目搜索：支持关键词、语言、Stars、License、最近更新等条件。
- 推荐卡片：每轮默认给出 10 个项目，展示简介、技术、GitHub Stars 和评分，主卡片可直接打开 GitHub。
- 推荐排序：根据 Stars、Forks、Issue、项目体量和用户需求生成推荐指数。
- 项目分析：获取仓库元数据、README、目录结构、语言分布、Topics、Releases、Issues 和 Pull Requests。
- README 解读：生成“3 分钟读懂该项目”的中文 Markdown 报告。
- 技术栈识别：自动识别开发语言、前端、后端、AI 框架、数据库和部署相关技术。
- 核心模块识别：按 Main、API、Service、Agent、Workflow、Prompt、Tool、Memory、RAG、Config、Utils 等维度定位关键文件。
- 学习路线：根据仓库结构生成从运行项目到阅读核心代码的分阶段学习路径。
- AI 问答：基于 README、目录结构和技术栈回答项目相关问题。
- 项目对比：从推荐卡片加入候选项目，在侧边栏统一开始对比，并按项目行展示简介、技术、GitHub Stars 和评分。
- 我的收藏：保存关注项目、分析报告、学习记录和个人笔记。
- 每日推荐：按热门项目、AI 新项目、Agent、RAG、Spring AI 等类别生成 GitHub Daily Report。

## 技术栈

- Python
- Streamlit
- Requests
- python-dotenv
- SQLite
- GitHub REST API
- DeepSeek / OpenAI / Anthropic API，可选

## 项目结构

```text
AI Github Agent/
├── app.py                    # Streamlit 主应用，包含聊天、搜索、分析、问答、对比、收藏、日报等页面
├── config.py                 # 环境变量、目录、GitHub 和 LLM Provider 配置
├── requirements.txt          # Python 依赖
├── modules/
│   ├── github_client.py      # GitHub REST API 封装
│   ├── llm_client.py         # DeepSeek/OpenAI/Anthropic 调用封装
│   ├── analyzer.py           # 仓库结构、技术栈、推荐指数等规则分析
│   ├── intent_router.py      # 聊天意图识别
│   ├── learning_path.py      # 学习路线生成
│   ├── knowledge_base.py     # SQLite 收藏、问答、学习记录和笔记
│   ├── search_engine.py      # 项目搜索与推荐封装
│   └── file_parser.py        # 代码文件解析工具
├── utils/
│   ├── cache.py              # 本地缓存管理
│   ├── file_parser.py        # 文件类型、依赖、README 和代码结构解析工具
│   └── markdown.py           # Markdown 辅助工具
└── pages/                    # Streamlit 多页面入口文件
```

运行后会自动创建以下本地目录：

```text
data/       # SQLite 数据库，默认 data/knowledge_base.db
cache/      # 本地缓存
knowledge/  # 预留知识库目录
logs/       # 日志目录
```

## 环境要求

建议使用 Python 3.10 或更高版本。

```powershell
cd "D:\PythonProjects\MyAgent\AI Github Agent"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

如果你使用的是 cmd：

```cmd
cd /d "D:\PythonProjects\MyAgent\AI Github Agent"
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
```

## 配置环境变量

在项目根目录创建 `.env` 文件。最小可用配置如下：

```env
GITHUB_TOKEN=your_github_token

DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_API_BASE=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat

DEFAULT_LLM_PROVIDER=deepseek
```

`GITHUB_TOKEN` 是可选项，但建议配置。未配置时仍可搜索公开仓库，只是 GitHub API 限额更低。

如果要切换其他模型服务，可以配置：

```env
OPENAI_API_KEY=your_openai_api_key
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini

ANTHROPIC_API_KEY=your_anthropic_api_key
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

DEFAULT_LLM_PROVIDER=openai
DEFAULT_MODEL=gpt-4o-mini
```

其他可选配置：

```env
GITHUB_API_BASE=https://api.github.com
REQUEST_TIMEOUT=30
SEARCH_PER_PAGE=10
MAX_STRUCTURE_ITEMS=160
```

## 启动应用

在项目根目录执行：

```powershell
streamlit run app.py
```

也可以使用：

```powershell
python -m streamlit run app.py
```

启动后浏览器会打开 Streamlit 页面。侧边栏包含以下入口：

- 智能聊天
- 数据概览
- 项目搜索
- 项目分析
- AI 问答
- 项目对比
- 我的收藏
- 每日推荐

## 使用示例

在智能聊天页可以直接输入：

```text
帮我找适合学习 AI Agent 的 Python 项目
```

```text
介绍 langchain-ai/langgraph
```

```text
对比 langchain-ai/langgraph 和 crewAIInc/crewAI
```

```text
给 microsoft/autogen 一个 2 周学习计划
```

在项目分析页可以输入：

```text
langchain-ai/langgraph
```

或粘贴完整 GitHub URL：

```text
https://github.com/langchain-ai/langgraph
```

## 数据存储

应用使用本地 SQLite 保存个人数据，默认路径为：

```text
data/knowledge_base.db
```

其中包含：

- 收藏项目
- README 分析报告
- AI 问答记录
- 学习记录
- 学习笔记

这些数据只保存在本机项目目录中，不会自动上传到远程服务。

## 无 API Key 时的行为

未配置 LLM API Key 时，应用仍然可以：

- 搜索 GitHub 项目
- 获取仓库 README、目录结构和元数据
- 识别技术栈和核心模块
- 生成规则版推荐理由
- 生成兜底版 README 报告
- 保存收藏、学习记录和笔记

需要 LLM API Key 的能力包括：

- 深度 README 解读
- AI 架构报告
- 基于项目上下文的自然语言问答
- AI 项目对比报告
- GitHub Daily Report 文案生成

## 常见问题

### GitHub API rate limit exceeded

这是 GitHub API 限流。建议在 `.env` 中配置 `GITHUB_TOKEN`，或者等待限额重置。

### 当前 LLM 未配置 API key

说明当前选择的模型服务没有对应 API Key。可以在 `.env` 中配置 DeepSeek、OpenAI 或 Anthropic，然后重启 Streamlit 应用。

### 搜索结果为空

可以尝试换成更具体的关键词，例如 `LangGraph RAG Python`、`MCP server TypeScript`、`Spring AI agent`，也可以降低 Stars 或语言过滤条件。

### 项目路径中有空格

当前目录名是 `AI Github Agent`，执行命令时建议始终用英文双引号包裹路径：

```powershell
cd "D:\PythonProjects\MyAgent\AI Github Agent"
```

## 开发说明

- 主应用逻辑集中在 `app.py`。
- GitHub 数据访问逻辑集中在 `modules/github_client.py`。
- LLM 适配逻辑集中在 `modules/llm_client.py`。
- 仓库分析规则集中在 `modules/analyzer.py`。
- 本地知识库逻辑集中在 `modules/knowledge_base.py`。
- 新增页面时可以参考 `pages/` 目录，也可以继续在 `app.py` 的侧边栏路由中扩展。
