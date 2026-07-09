"""AI GitHub Agent Streamlit application."""

import html
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))

import config
from modules.analyzer import Analyzer
from modules.github_client import GitHubClient
from modules.intent_router import IntentRouter
from modules.knowledge_base import KnowledgeBase
from modules.learning_path import LearningPathGenerator
from modules.llm_client import LLMClient


st.set_page_config(
    page_title="AI GitHub Agent",
    page_icon="AI",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    [data-testid="stSidebarNav"] { display: none; }
    .block-container { max-width: 1280px; padding-top: 1.2rem; padding-bottom: 4.5rem; }
    .main .block-container { padding-left: 3rem; padding-right: 3rem; }
    .hero-panel {
        border: 1px solid #e6e8ef;
        border-radius: 14px;
        padding: 1.15rem 1.25rem;
        background: linear-gradient(180deg, #ffffff 0%, #f7f9fc 100%);
        margin-bottom: 1rem;
    }
    .hero-title {
        font-size: 2.05rem;
        line-height: 1.15;
        font-weight: 760;
        color: #182032;
        margin-bottom: 0.35rem;
    }
    .hero-subtitle {
        color: #667085;
        font-size: 0.98rem;
        margin-bottom: 0.85rem;
    }
    .stat-strip {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 0.65rem;
        margin-top: 0.75rem;
    }
    .stat-pill {
        border: 1px solid #edf0f5;
        border-radius: 10px;
        padding: 0.65rem 0.75rem;
        background: #ffffff;
    }
    .stat-label { color: #667085; font-size: 0.76rem; }
    .stat-value { color: #1d2939; font-size: 1rem; font-weight: 700; margin-top: 0.1rem; }
    .section-label {
        color: #475467;
        font-size: 0.84rem;
        font-weight: 650;
        margin: 0.75rem 0 0.35rem 0;
    }
    .repo-card {
        border: 1px solid #e6e8ef;
        border-radius: 12px;
        padding: 0.95rem 1rem;
        margin: 0.65rem 0;
        background: #ffffff;
    }
    .repo-title { font-size: 1.05rem; font-weight: 750; margin-bottom: 0.25rem; }
    .repo-desc { color: #475467; font-size: 0.91rem; min-height: 1.25rem; }
    .repo-meta {
        color: #667085;
        display: flex;
        flex-wrap: wrap;
        gap: 0.45rem;
        margin-top: 0.55rem;
        font-size: 0.82rem;
    }
    .repo-chip {
        border: 1px solid #edf0f5;
        border-radius: 999px;
        background: #f8fafc;
        padding: 0.18rem 0.55rem;
    }
    .answer-summary {
        border-left: 3px solid #2f6fed;
        background: #f7faff;
        padding: 0.8rem 0.95rem;
        border-radius: 10px;
        margin: 0.35rem 0;
    }
    .muted { color: #667085; font-size: 0.9rem; }
    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e6e8ef;
        padding: 0.7rem;
        border-radius: 10px;
    }
    div[data-testid="stChatMessage"] {
        border-radius: 12px;
    }
    .stButton > button {
        border-radius: 9px;
        min-height: 2.35rem;
    }
    @media (max-width: 900px) {
        .main .block-container { padding-left: 1rem; padding-right: 1rem; }
        .stat-strip { grid-template-columns: repeat(2, minmax(0, 1fr)); }
        .hero-title { font-size: 1.65rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def init_state() -> None:
    if "github" not in st.session_state:
        st.session_state.github = GitHubClient()
    if "llm" not in st.session_state:
        st.session_state.llm = LLMClient()
    if "kb" not in st.session_state:
        st.session_state.kb = KnowledgeBase()
    if "analyzer" not in st.session_state:
        st.session_state.analyzer = Analyzer()
    if "learning" not in st.session_state:
        st.session_state.learning = LearningPathGenerator()
    if "router" not in st.session_state:
        st.session_state.router = IntentRouter()
    st.session_state.setdefault("search_results", [])
    st.session_state.setdefault("current_repo", None)
    st.session_state.setdefault("analysis", None)
    st.session_state.setdefault("compare_repos", [])
    st.session_state.setdefault("chat_messages", [])
    st.session_state.setdefault("chat_memory", {})
    st.session_state.setdefault("last_user_message", "")
    st.session_state.setdefault("last_answer", "")


def main() -> None:
    init_state()
    page = render_sidebar()

    if page == "智能聊天":
        render_chat()
    elif page == "数据概览":
        render_home()
    elif page == "项目搜索":
        render_search()
    elif page == "项目分析":
        render_analysis()
    elif page == "AI 问答":
        render_qa()
    elif page == "项目对比":
        render_compare()
    elif page == "我的收藏":
        render_favorites()
    elif page == "每日推荐":
        render_daily()


def render_sidebar() -> str:
    st.sidebar.title("AI GitHub Agent")
    page = st.sidebar.radio(
        "导航",
        ["智能聊天", "数据概览", "项目搜索", "项目分析", "AI 问答", "项目对比", "我的收藏", "每日推荐"],
    )
    st.sidebar.divider()

    provider_labels = {
        name: meta["label"] for name, meta in config.LLM_PROVIDERS.items()
    }
    providers = list(config.LLM_PROVIDERS.keys())
    with st.sidebar.expander("模型设置", expanded=False):
        provider = st.selectbox(
            "LLM Provider",
            providers,
            index=providers.index(st.session_state.llm.provider)
            if st.session_state.llm.provider in providers
            else 0,
            format_func=lambda item: provider_labels[item],
        )
        models = config.LLM_PROVIDERS[provider]["models"]
        model = st.selectbox("Model", models)
        st.session_state.llm.set_provider(provider, model)

    status = st.session_state.llm.provider_status()
    st.sidebar.caption("连接状态")
    st.sidebar.write(f"DeepSeek: {'已配置' if status['deepseek'] else '未配置'}")
    st.sidebar.write(f"GitHub Token: {'已配置' if config.GITHUB_TOKEN else '未配置'}")
    if not status.get(provider):
        st.sidebar.warning("当前 LLM 未配置 API key，应用会使用规则分析兜底。")
    return page


def render_chat() -> None:
    stats = st.session_state.kb.get_statistics()
    st.markdown(
        f"""
        <div class="hero-panel">
            <div class="hero-title">AI GitHub Agent</div>
            <div class="hero-subtitle">用一句话完成开源项目搜索、对比、介绍和学习规划。</div>
            <div class="stat-strip">
                <div class="stat-pill"><div class="stat-label">收藏项目</div><div class="stat-value">{stats["favorites_count"]}</div></div>
                <div class="stat-pill"><div class="stat-label">学习记录</div><div class="stat-value">{stats["learning_records"]}</div></div>
                <div class="stat-pill"><div class="stat-label">问答记录</div><div class="stat-value">{stats["qa_count"]}</div></div>
                <div class="stat-pill"><div class="stat-label">当前项目</div><div class="stat-value">{(st.session_state.current_repo or {}).get("full_name", "未选择")}</div></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-label">常用任务</div>', unsafe_allow_html=True)
    quick_prompts = [
        ("找 Agent 项目", "帮我找适合学习 AI Agent 的 Python 项目"),
        ("项目对比", "对比 LangGraph、CrewAI 和 AutoGen"),
        ("项目介绍", "介绍一下 langchain-ai/langchain"),
        ("学习计划", "给我一个 2 周学习计划"),
    ]
    cols = st.columns(4)
    for idx, (label, prompt) in enumerate(quick_prompts):
        with cols[idx]:
            if st.button(label, use_container_width=True, help=prompt):
                submit_chat(prompt)
                st.rerun()

    toolbar_left, toolbar_mid, toolbar_right = st.columns([0.9, 0.9, 4.2])
    if toolbar_left.button("清空"):
        st.session_state.chat_messages = []
        st.session_state.chat_memory = {}
        st.session_state.last_user_message = ""
        st.session_state.last_answer = ""
        st.rerun()
    if toolbar_mid.button("重试") and st.session_state.last_user_message:
        submit_chat(st.session_state.last_user_message, regenerate=True)
        st.rerun()
    toolbar_right.caption("也可以直接输入 GitHub URL、owner/repo、或“对比第 1 和第 3 个”。")

    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"], unsafe_allow_html=message["role"] == "assistant")

    user_input = st.chat_input("输入 GitHub 项目需求、对比问题或学习目标...")
    if user_input:
        submit_chat(user_input)
        st.rerun()

    render_chat_artifacts()

    if st.session_state.last_answer:
        with st.expander("复制最近回答"):
            st.code(st.session_state.last_answer, language="markdown")


def submit_chat(message: str, regenerate: bool = False) -> None:
    if not regenerate:
        st.session_state.chat_messages.append({"role": "user", "content": message})
    st.session_state.last_user_message = message
    with st.spinner("AI GitHub Agent 正在搜索、分析和总结..."):
        answer = handle_chat_message(message)
    st.session_state.last_answer = answer
    st.session_state.chat_messages.append({"role": "assistant", "content": answer})


def handle_chat_message(message: str) -> str:
    memory = st.session_state.chat_memory
    routed = st.session_state.router.route(message, memory)
    intent = routed["intent"]

    if intent in ("search", "refine_search"):
        return chat_search(routed)
    if intent == "compare":
        return chat_compare(routed)
    if intent == "intro":
        return chat_intro(routed)
    if intent == "learning":
        return chat_learning(routed)
    if intent == "followup":
        return chat_followup(routed)
    return chat_general(routed)


def chat_search(routed: Dict[str, Any]) -> str:
    filters = routed["filters"]
    query = routed["query"]
    if routed["intent"] == "refine_search" and st.session_state.chat_memory.get("last_search_query"):
        query = st.session_state.chat_memory["last_search_query"]
        filters = {**st.session_state.chat_memory.get("last_filters", {}), **filters}

    repos = st.session_state.github.search_repos(
        query=query,
        language=filters.get("language", ""),
        min_stars=filters.get("min_stars", 0),
        license_id=filters.get("license", ""),
        recent=filters.get("recent", False),
        sort="updated" if filters.get("recent") else "stars",
        per_page=10 if "更多" in routed["raw"] else 5,
    )
    repos = rank_recommendations(repos, routed["raw"], filters)
    st.session_state.search_results = repos
    st.session_state.chat_memory["last_search_query"] = query
    st.session_state.chat_memory["last_filters"] = filters
    st.session_state.chat_memory["last_repos"] = repos

    if not repos:
        return f"没有找到明显匹配 `{query}` 的项目。可以换成更具体的技术词，例如 `LangGraph RAG Python`。"
    return format_recommendations(repos, routed["raw"])


def chat_compare(routed: Dict[str, Any]) -> str:
    repos = resolve_repos_from_route(routed)
    if len(repos) < 2:
        return "我还缺少至少 2 个项目。你可以输入 `对比 langchain-ai/langgraph 和 crewAIInc/crewAI`，或先搜索后说 `对比第 1 和第 3 个`。"

    st.session_state.compare_repos = repos
    st.session_state.chat_memory["last_compare_repos"] = repos
    basic = format_compare_table(repos)

    if st.session_state.llm.is_ready():
        try:
            report = st.session_state.llm.compare_repos(repos)
            return f"{basic}\n\n{report}"
        except Exception as exc:
            return f"{basic}\n\nLLM 对比报告生成失败: {exc}"
    return basic + "\n\n推荐选择：新手优先选文档清晰、示例多、最近仍活跃维护的项目；生产环境还需要人工复核 License、Release 节奏和 issue 响应。"


def chat_intro(routed: Dict[str, Any]) -> str:
    repo = resolve_single_repo(routed)
    if not repo:
        return "我没能识别到具体项目。请提供 GitHub URL 或 `owner/repo`，例如 `microsoft/autogen`。"
    run_analysis(repo["full_name"], load_issues=False)
    analysis = st.session_state.analysis
    if not analysis:
        return "项目数据获取失败，请稍后重试。"
    st.session_state.chat_memory["current_repo"] = repo["full_name"]
    return format_project_intro(analysis)


def chat_learning(routed: Dict[str, Any]) -> str:
    repo = resolve_single_repo(routed)
    if repo:
        run_analysis(repo["full_name"], load_issues=False)
    elif not st.session_state.analysis and st.session_state.chat_memory.get("current_repo"):
        run_analysis(st.session_state.chat_memory["current_repo"], load_issues=False)

    analysis = st.session_state.analysis
    if not analysis:
        return "请先告诉我要学习哪个项目，例如 `给 langchain-ai/langgraph 一个 2 周学习计划`。"
    st.session_state.chat_memory["current_repo"] = analysis["repo"]["full_name"]
    return format_learning_plan(analysis, routed["period"], routed["level"])


def chat_followup(routed: Dict[str, Any]) -> str:
    raw = routed["raw"]
    if routed["indexes"]:
        repos = repos_from_indexes(routed["indexes"])
        if len(repos) >= 2:
            return chat_compare({**routed, "repos": [repo["full_name"] for repo in repos]})
        if len(repos) == 1:
            run_analysis(repos[0]["full_name"], load_issues=False)
            return format_project_intro(st.session_state.analysis)
    if "学习" in raw or "路线" in raw or "计划" in raw:
        return chat_learning(routed)
    if "新手" in raw or "简单" in raw or "更多" in raw:
        routed["intent"] = "refine_search"
        routed["filters"]["difficulty"] = "入门"
        return chat_search(routed)
    return chat_general(routed)


def chat_general(routed: Dict[str, Any]) -> str:
    context = ""
    if st.session_state.analysis:
        context = st.session_state.analysis.get("context", "")
    if st.session_state.llm.is_ready() and context:
        try:
            return st.session_state.llm.answer_question(routed["raw"], context)
        except Exception as exc:
            return f"我尝试基于当前项目回答，但 LLM 调用失败: {exc}"
    if st.session_state.search_results:
        return "你可以继续说：`对比第 1 和第 3 个`、`介绍第 1 个`、`给第 1 个学习计划`，我会基于刚才的推荐继续处理。"
    return "我主要处理 GitHub 项目搜索、介绍、对比和学习规划。你可以直接输入：`帮我找适合学习 RAG 的 Python 项目`。"


def render_home() -> None:
    st.title("AI GitHub Agent")
    st.caption("帮助开发者发现、理解和学习 GitHub 开源项目的智能助手。")

    stats = st.session_state.kb.get_statistics()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("收藏项目", stats["favorites_count"])
    c2.metric("学习记录", stats["learning_records"])
    c3.metric("问答记录", stats["qa_count"])
    c4.metric("学习笔记", stats["notes_count"])

    st.subheader("快速开始")
    keyword = st.text_input("输入技术关键词", value="LangGraph", placeholder="Spring AI / RAG / MCP / FastAPI")
    if st.button("搜索项目", type="primary"):
        st.session_state.quick_keyword = keyword
        st.session_state.search_results = []
        st.rerun()

    st.subheader("推荐方向")
    cols = st.columns(4)
    for idx, topic in enumerate(["AI Agent", "LangGraph", "RAG", "MCP", "Spring AI", "OCR", "LLM", "FastAPI"]):
        with cols[idx % 4]:
            if st.button(topic, use_container_width=True):
                st.session_state.quick_keyword = topic
                st.session_state.search_results = []
                st.rerun()


def render_search() -> None:
    st.header("项目搜索与推荐")
    default_keyword = st.session_state.pop("quick_keyword", "")
    with st.form("search_form"):
        c1, c2, c3, c4 = st.columns([3, 1.2, 1.2, 1])
        keyword = c1.text_input("关键词", value=default_keyword, placeholder="LangGraph / RAG / MCP / Spring AI")
        language = c2.selectbox("语言", ["All", "Python", "Java", "Go", "Rust", "TypeScript", "JavaScript"])
        sort = c3.selectbox("排序", ["stars", "forks", "updated"])
        per_page = c4.slider("数量", 5, 20, config.SEARCH_PER_PAGE)
        submitted = st.form_submit_button("搜索", type="primary")

    if submitted and keyword.strip():
        with st.spinner("正在搜索 GitHub..."):
            repos = st.session_state.github.search_repos(keyword, language=language, sort=sort, per_page=per_page)
            st.session_state.search_results = repos
        st.success(f"找到 {len(st.session_state.search_results)} 个项目")

    if st.session_state.search_results:
        st.subheader("推荐结果")
        for idx, repo in enumerate(st.session_state.search_results):
            render_repo_card(repo, idx)


def render_repo_card(repo: Dict[str, Any], idx: int) -> None:
    analyzer = st.session_state.analyzer
    score = analyzer.recommendation_score(repo)
    reason = rule_recommendation(repo, score)
    with st.container():
        c1, c2 = st.columns([4, 1.2])
        with c1:
            st.markdown(f"<div class='repo-title'><a href='{repo.get('html_url')}'>{repo.get('full_name')}</a></div>", unsafe_allow_html=True)
            st.write(repo.get("description") or "暂无描述")
        with c2:
            st.metric("推荐指数", f"{score}/10")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Stars", repo.get("stargazers_count", 0))
        m2.metric("Forks", repo.get("forks_count", 0))
        m3.metric("语言", repo.get("language") or "Unknown")
        m4.metric("更新", (repo.get("updated_at") or "")[:10])
        st.write(f"推荐理由: {reason}")
        b1, b2, b3 = st.columns([1, 1, 4])
        if b1.button("分析", key=f"analyze_{idx}"):
            st.session_state.current_repo = repo
            st.session_state.analysis = None
            st.rerun()
        if b2.button("收藏", key=f"fav_{idx}"):
            st.session_state.kb.add_favorite(repo)
            st.toast("已收藏")


def render_analysis() -> None:
    st.header("项目分析")
    default_repo = ""
    if st.session_state.current_repo:
        default_repo = st.session_state.current_repo.get("full_name", "")
    repo_input = st.text_input("GitHub Repository", value=default_repo, placeholder="owner/repo 或 GitHub URL")

    c1, c2, c3 = st.columns([1, 1, 4])
    analyze = c1.button("开始分析", type="primary")
    load_issues = c2.checkbox("含 Issues/PR", value=False)

    if analyze and repo_input:
        run_analysis(repo_input, load_issues=load_issues)

    if st.session_state.analysis:
        show_analysis(st.session_state.analysis)


def run_analysis(repo_input: str, load_issues: bool = False) -> None:
    full_name = st.session_state.github.normalize_repo_name(repo_input)
    if not full_name:
        st.error("请输入正确格式，例如 langchain-ai/langgraph")
        return

    with st.spinner("正在获取仓库、README、目录结构和技术栈..."):
        repo = st.session_state.github.get_repo(full_name)
        if not repo:
            st.error("无法获取仓库信息")
            return
        readme = st.session_state.github.get_readme(repo["full_name"])
        structure = st.session_state.github.get_repo_structure(repo["full_name"])
        languages = st.session_state.github.get_languages(repo["full_name"])
        releases = st.session_state.github.get_releases(repo["full_name"])
        topics = st.session_state.github.get_topics(repo["full_name"])
        issues = st.session_state.github.get_issues(repo["full_name"]) if load_issues else []
        prs = st.session_state.github.get_pull_requests(repo["full_name"]) if load_issues else []

        analyzer = st.session_state.analyzer
        tech_stack = analyzer.detect_tech_stack(repo, languages, structure, readme)
        modules = analyzer.identify_core_modules(structure)
        directories = analyzer.summarize_structure(structure)
        key_files = analyzer.key_files_for_learning(structure)
        learning_path = st.session_state.learning.generate(repo, tech_stack, key_files)
        context = analyzer.build_context(repo, readme, structure, tech_stack, modules)

    readme_report = ""
    if readme and st.session_state.llm.is_ready():
        with st.spinner("正在生成 README 智能分析..."):
            try:
                readme_report = st.session_state.llm.analyze_readme(repo, readme)
            except Exception as exc:
                readme_report = f"LLM 分析失败: {exc}"
    if not readme_report:
        readme_report = fallback_readme_report(repo, readme)

    st.session_state.current_repo = repo
    st.session_state.analysis = {
        "repo": repo,
        "readme": readme,
        "readme_report": readme_report,
        "structure": structure,
        "directories": directories,
        "languages": languages,
        "tech_stack": tech_stack,
        "modules": modules,
        "key_files": key_files,
        "learning_path": learning_path,
        "context": context,
        "releases": releases,
        "topics": topics,
        "issues": issues,
        "prs": prs,
    }
    st.session_state.kb.add_learning_record(repo["full_name"], "analyze", {"items": len(structure)})


def show_analysis(analysis: Dict[str, Any]) -> None:
    repo = analysis["repo"]
    st.subheader(repo["full_name"])
    st.caption(repo.get("description") or "")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Stars", repo.get("stargazers_count", 0))
    c2.metric("Forks", repo.get("forks_count", 0))
    c3.metric("语言", repo.get("language") or "Unknown")
    c4.metric("License", (repo.get("license") or {}).get("name", "Unknown"))

    if st.button("保存到知识库"):
        st.session_state.kb.add_favorite(repo, analysis["readme_report"])
        st.success("已保存到收藏和知识库")

    tabs = st.tabs(["README", "项目结构", "技术栈", "学习路线", "核心代码", "元数据"])
    with tabs[0]:
        st.markdown(analysis["readme_report"])
    with tabs[1]:
        st.dataframe(analysis["directories"], use_container_width=True, hide_index=True)
        with st.expander("完整目录样本"):
            st.code("\n".join(item.get("path", "") for item in analysis["structure"][:160]))
    with tabs[2]:
        show_tech_stack(analysis["tech_stack"])
    with tabs[3]:
        st.dataframe(analysis["learning_path"], use_container_width=True, hide_index=True)
    with tabs[4]:
        modules = analysis["modules"]
        if modules:
            st.dataframe(modules, use_container_width=True, hide_index=True)
        else:
            st.info("暂未识别到明显核心模块。")
        st.write(st.session_state.analyzer.architecture_summary(repo, modules))
        if st.button("生成 AI 架构报告"):
            if not st.session_state.llm.is_ready():
                st.warning("当前 LLM 未配置 API key。")
            else:
                with st.spinner("正在生成架构分析..."):
                    report = st.session_state.llm.analyze_architecture(analysis["context"])
                st.markdown(report)
    with tabs[5]:
        st.write("Topics:", ", ".join(analysis["topics"]) or "无")
        st.write("Releases:", len(analysis["releases"]))
        st.write("Open Issues:", len(analysis["issues"]))
        st.write("Open Pull Requests:", len(analysis["prs"]))


def show_tech_stack(tech_stack: Dict[str, List[str]]) -> None:
    rows = [{"类别": key, "技术": ", ".join(values) if values else "未识别"} for key, values in tech_stack.items()]
    st.dataframe(rows, use_container_width=True, hide_index=True)
    st.markdown("### 技术栈分析报告")
    for key, values in tech_stack.items():
        if values:
            st.write(f"- {key}: {', '.join(values)}")


def render_qa() -> None:
    st.header("AI 问答")
    repo_name = st.text_input(
        "当前项目",
        value=(st.session_state.current_repo or {}).get("full_name", ""),
        placeholder="先在项目分析页加载项目，或输入 owner/repo",
    )

    presets = [
        "这个项目解决什么问题？",
        "如何启动项目？",
        "Agent 是如何工作的？",
        "Workflow 在哪里？",
        "Prompt 在哪个文件？",
        "RAG 是如何实现的？",
        "哪些代码最值得阅读？",
        "适合新手学习吗？",
    ]
    cols = st.columns(4)
    for idx, question in enumerate(presets):
        if cols[idx % 4].button(question, use_container_width=True):
            st.session_state.qa_question = question

    question = st.text_area("你的问题", value=st.session_state.get("qa_question", ""), height=110)
    if st.button("提问", type="primary") and question.strip():
        if not repo_name:
            st.warning("请先选择一个项目。")
            return
        ensure_context(repo_name)
        analysis = st.session_state.analysis
        context = analysis["context"] if analysis else ""
        if not st.session_state.llm.is_ready():
            answer = fallback_answer(question, analysis)
        else:
            with st.spinner("正在结合 README 和源码结构回答..."):
                try:
                    answer = st.session_state.llm.answer_question(question, context)
                except Exception as exc:
                    answer = f"LLM 调用失败: {exc}\n\n{fallback_answer(question, analysis)}"
        st.session_state.kb.add_qa_record(repo_name, question, answer)
        st.markdown(answer)

    if repo_name:
        records = st.session_state.kb.get_qa_records(repo_name, limit=8)
        if records:
            st.subheader("历史问答")
            for record in records:
                with st.expander(record["question"]):
                    st.markdown(record["answer"])


def ensure_context(repo_name: str) -> None:
    current = (st.session_state.current_repo or {}).get("full_name")
    if st.session_state.analysis and current == repo_name:
        return
    run_analysis(repo_name, load_issues=False)


def render_compare() -> None:
    st.header("项目对比")
    text = st.text_area(
        "输入要对比的仓库，每行一个",
        value="langchain-ai/langgraph\ncrewAIInc/crewAI",
        height=120,
    )
    if st.button("开始对比", type="primary"):
        repos = []
        with st.spinner("正在获取项目数据..."):
            for line in text.splitlines():
                full_name = st.session_state.github.normalize_repo_name(line)
                if full_name:
                    repo = st.session_state.github.get_repo(full_name)
                    if repo:
                        repos.append(repo)
        st.session_state.compare_repos = repos

    repos = st.session_state.compare_repos
    if repos:
        rows = []
        for repo in repos:
            rows.append({
                "项目": repo.get("full_name"),
                "项目定位": repo.get("description") or "无",
                "技术栈": repo.get("language") or "Unknown",
                "社区活跃度": f"{repo.get('stargazers_count', 0)} stars / {repo.get('forks_count', 0)} forks",
                "学习难度": difficulty(repo),
                "推荐指数": f"{st.session_state.analyzer.recommendation_score(repo)}/10",
            })
        st.dataframe(rows, use_container_width=True, hide_index=True)
        if st.button("生成 AI 对比报告"):
            if not st.session_state.llm.is_ready():
                st.warning("当前 LLM 未配置 API key。")
            else:
                with st.spinner("正在生成对比报告..."):
                    report = st.session_state.llm.compare_repos(repos)
                st.markdown(report)


def render_favorites() -> None:
    st.header("我的收藏")
    favorites = st.session_state.kb.get_favorites()
    if not favorites:
        st.info("暂无收藏项目。")
        return

    for idx, fav in enumerate(favorites):
        with st.container():
            c1, c2 = st.columns([4, 1])
            with c1:
                st.markdown(f"### [{fav['full_name']}]({fav.get('html_url') or ''})")
                st.write(fav.get("description") or "暂无描述")
                st.caption(f"收藏时间: {fav.get('added_at')} | 阅读次数: {fav.get('view_count', 0)}")
            with c2:
                if st.button("分析", key=f"favorite_analyze_{idx}"):
                    st.session_state.kb.mark_viewed(fav["full_name"])
                    run_analysis(fav["full_name"])
                    st.rerun()
                if st.button("取消收藏", key=f"favorite_remove_{idx}"):
                    st.session_state.kb.remove_favorite(fav["full_name"])
                    st.rerun()
            notes = st.text_area("学习笔记", value=fav.get("notes") or "", key=f"note_{idx}", height=90)
            if st.button("保存笔记", key=f"save_note_{idx}"):
                st.session_state.kb.update_notes(fav["full_name"], notes)
                st.success("笔记已保存")
            if fav.get("analysis_report"):
                with st.expander("分析报告"):
                    st.markdown(fav["analysis_report"])

    st.subheader("学习记录")
    st.dataframe(st.session_state.kb.get_learning_records(), use_container_width=True, hide_index=True)


def render_daily() -> None:
    st.header("每日项目推荐")
    category = st.selectbox(
        "推荐类型",
        ["今日热门项目", "AI 新项目", "Star 增长最快项目", "Agent 项目", "RAG 项目", "Spring AI 项目"],
    )
    if st.button("获取推荐", type="primary"):
        with st.spinner("正在扫描 GitHub..."):
            st.session_state.daily_repos = st.session_state.github.daily_recommendations(category)

    repos = st.session_state.get("daily_repos", [])
    if repos:
        for idx, repo in enumerate(repos):
            render_repo_card(repo, idx + 1000)
        if st.button("生成 GitHub Daily Report"):
            if st.session_state.llm.is_ready():
                with st.spinner("正在生成日报..."):
                    report = st.session_state.llm.daily_report(repos, category)
            else:
                report = fallback_daily_report(repos, category)
            st.markdown(report)
            st.download_button("下载 Markdown", report, file_name="github_daily_report.md")


PROJECT_ALIASES = {
    "langchain": "langchain-ai/langchain",
    "langgraph": "langchain-ai/langgraph",
    "crewai": "crewAIInc/crewAI",
    "crew ai": "crewAIInc/crewAI",
    "autogen": "microsoft/autogen",
    "auto gen": "microsoft/autogen",
    "spring ai": "spring-projects/spring-ai",
    "llamaindex": "run-llama/llama_index",
    "llama index": "run-llama/llama_index",
}


def render_chat_artifacts() -> None:
    repos = st.session_state.get("search_results", [])
    if repos:
        st.divider()
        st.markdown("### 推荐项目")
        for idx, repo in enumerate(repos[:5], start=1):
            score = st.session_state.analyzer.recommendation_score(repo)
            repo_name = html.escape(repo.get("full_name") or "")
            repo_desc = html.escape(repo.get("description") or "暂无描述")
            repo_url = html.escape(repo.get("html_url") or "")
            repo_lang = html.escape(repo.get("language") or "Unknown")
            st.markdown(
                f"""
                <div class="repo-card">
                    <div class="repo-title">{idx}. <a href="{repo_url}">{repo_name}</a></div>
                    <div class="repo-desc">{repo_desc}</div>
                    <div class="repo-meta">
                        <span class="repo-chip">Stars {format_count(repo.get('stargazers_count', 0))}</span>
                        <span class="repo-chip">Forks {format_count(repo.get('forks_count', 0))}</span>
                        <span class="repo-chip">{repo_lang}</span>
                        <span class="repo-chip">更新 {(repo.get('pushed_at') or repo.get('updated_at') or '')[:10]}</span>
                        <span class="repo-chip">推荐 {score}/10</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            c1, c2, c3, c4 = st.columns([1, 1, 1, 4])
            with c1:
                if c1.button("查看介绍", key=f"chat_intro_{idx}"):
                    run_analysis(repo["full_name"], load_issues=False)
                    answer = format_project_intro(st.session_state.analysis)
                    st.session_state.chat_messages.append({"role": "assistant", "content": answer})
                    st.session_state.last_answer = answer
                    st.rerun()
            with c2:
                if c2.button("加入对比", key=f"chat_compare_add_{idx}"):
                    add_compare_repo(repo)
                    st.toast("已加入对比")
            with c3:
                if c3.button("学习计划", key=f"chat_plan_{idx}"):
                    run_analysis(repo["full_name"], load_issues=False)
                    answer = format_learning_plan(st.session_state.analysis, "2 周", "普通开发者")
                    st.session_state.chat_messages.append({"role": "assistant", "content": answer})
                    st.session_state.last_answer = answer
                    st.rerun()
            c4.caption(rule_recommendation(repo, score))

    if st.session_state.get("compare_repos"):
        with st.expander("当前对比列表"):
            st.dataframe(
                [{"项目": repo.get("full_name"), "Stars": repo.get("stargazers_count", 0), "语言": repo.get("language") or "Unknown"} for repo in st.session_state.compare_repos],
                use_container_width=True,
                hide_index=True,
            )


def rank_recommendations(repos: List[Dict[str, Any]], user_need: str, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    need = user_need.lower()
    ranked = []
    for repo in repos:
        score = st.session_state.analyzer.recommendation_score(repo)
        text = f"{repo.get('full_name', '')} {repo.get('description') or ''}".lower()
        for token in need.split():
            if len(token) > 2 and token in text:
                score += 0.25
        if filters.get("difficulty") == "入门":
            size = repo.get("size", 0) or 0
            if size < 30000:
                score += 0.6
            if repo.get("has_wiki") or repo.get("homepage"):
                score += 0.2
        if repo.get("license"):
            score += 0.2
        if repo.get("pushed_at") or repo.get("updated_at"):
            score += 0.1
        ranked.append((score, repo))
    ranked.sort(key=lambda item: item[0], reverse=True)
    return [repo for _, repo in ranked]


def format_recommendations(repos: List[Dict[str, Any]], user_need: str) -> str:
    top = repos[0]
    lines = [
        f"""
<div class="answer-summary">
我找到了 <b>{len(repos)}</b> 个相关项目。最值得先看的是
<b>{html.escape(top.get('full_name') or '')}</b>：
{html.escape(top.get('description') or '暂无描述')}
</div>
""",
        "下面的项目卡片可以直接查看介绍、加入对比或生成学习计划。",
        "",
        "你也可以继续问：`对比第 1 和第 3 个`、`介绍第 1 个`、`换成更适合新手的`。",
    ]
    return "\n".join(lines)


def resolve_repos_from_route(routed: Dict[str, Any]) -> List[Dict[str, Any]]:
    repos = []
    for repo_name in routed.get("repos", []):
        repo = st.session_state.github.resolve_repo(repo_name)
        if repo:
            repos.append(repo)
    if routed.get("indexes"):
        repos.extend(repos_from_indexes(routed["indexes"]))
    if not repos:
        for name in candidate_project_names(routed["raw"]):
            repo = st.session_state.github.resolve_repo(name)
            if repo:
                repos.append(repo)
    unique = []
    seen = set()
    for repo in repos:
        full_name = repo.get("full_name")
        if full_name and full_name not in seen:
            seen.add(full_name)
            unique.append(repo)
    return unique


def resolve_single_repo(routed: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    repos = resolve_repos_from_route(routed)
    if repos:
        return repos[0]
    current = st.session_state.chat_memory.get("current_repo")
    if current:
        return st.session_state.github.resolve_repo(current)
    if st.session_state.current_repo:
        return st.session_state.current_repo
    return None


def repos_from_indexes(indexes: List[int]) -> List[Dict[str, Any]]:
    repos = st.session_state.search_results or st.session_state.chat_memory.get("last_repos", [])
    selected = []
    for index in indexes:
        if 1 <= index <= len(repos):
            selected.append(repos[index - 1])
    return selected


def candidate_project_names(text: str) -> List[str]:
    lowered = text.lower()
    names = []
    for alias, full_name in PROJECT_ALIASES.items():
        if alias in lowered:
            names.append(full_name)
    cleaned = text
    for token in ["对比", "比较", "介绍", "分析", "一下", "和", "与", "以及", "哪个", "更适合", "项目"]:
        cleaned = cleaned.replace(token, " ")
    for part in cleaned.replace("，", " ").replace(",", " ").replace("、", " ").split():
        if "/" in part:
            names.append(part)
        elif re_like_project_name(part):
            names.append(part)
    return names


def re_like_project_name(value: str) -> bool:
    if len(value) < 3:
        return False
    lowered = value.lower()
    blocked = {"github", "agent", "rag", "python", "java", "typescript", "react", "项目"}
    return lowered not in blocked and any(ch.isalpha() for ch in value)


def add_compare_repo(repo: Dict[str, Any]) -> None:
    current = st.session_state.compare_repos
    if not any(item.get("full_name") == repo.get("full_name") for item in current):
        current.append(repo)


def format_compare_table(repos: List[Dict[str, Any]]) -> str:
    headers = ["维度"] + [repo.get("full_name", "") for repo in repos]
    rows = [
        ["项目定位"] + [repo.get("description") or "无" for repo in repos],
        ["技术栈"] + [repo.get("language") or "Unknown" for repo in repos],
        ["社区热度"] + [f"{repo.get('stargazers_count', 0)} stars / {repo.get('forks_count', 0)} forks" for repo in repos],
        ["维护活跃度"] + [activity_level(repo) for repo in repos],
        ["文档质量"] + [doc_quality(repo) for repo in repos],
        ["上手难度"] + [difficulty(repo) for repo in repos],
        ["License"] + [(repo.get("license") or {}).get("name", "Unknown") for repo in repos],
        ["风险点"] + [risk_summary(repo) for repo in repos],
        ["推荐指数"] + [f"{st.session_state.analyzer.recommendation_score(repo)}/10" for repo in repos],
    ]
    lines = ["总体结论：下面是基于 GitHub 公开元数据的初步对比，License 和商业合规仍建议人工复核。", ""]
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for row in rows:
        lines.append("| " + " | ".join(str(cell).replace("|", "/") for cell in row) + " |")
    lines.append("\n推荐选择：")
    easiest = min(repos, key=lambda repo: (repo.get("size", 0) or 0))
    hottest = max(repos, key=lambda repo: repo.get("stargazers_count", 0) or 0)
    lines.append(f"- 如果你是新手，优先看 `{easiest.get('full_name')}`。")
    lines.append(f"- 如果你看重社区热度，优先评估 `{hottest.get('full_name')}`。")
    lines.append("- 如果你要生产使用，请继续核实 Release、Issue 响应、License 和依赖生态。")
    return "\n".join(lines)


def format_project_intro(analysis: Dict[str, Any]) -> str:
    repo = analysis["repo"]
    tech = ", ".join(
        item for values in analysis["tech_stack"].values() for item in values
    ) or (repo.get("language") or "Unknown")
    dirs = "\n".join(f"- `{row['目录']}`：{row['说明']}" for row in analysis["directories"][:8]) or "- 未获取到目录结构"
    modules = "\n".join(f"- {row['模块']}：{row['文件']}" for row in analysis["modules"][:8]) or "- 暂未识别明显核心模块"
    return f"""
## {repo.get('full_name')} 项目介绍

### 一句话总结
{repo.get('description') or '该项目暂无 GitHub description，需要结合 README 继续确认定位。'}

### 项目概述
- Stars / Forks：{repo.get('stargazers_count', 0)} / {repo.get('forks_count', 0)}
- 主要语言：{repo.get('language') or 'Unknown'}
- License：{(repo.get('license') or {}).get('name', 'Unknown')}
- 最近更新：{(repo.get('pushed_at') or repo.get('updated_at') or '')[:10]}

### 技术栈
{tech}

### 目录结构解读
{dirs}

### 关键模块
{modules}

### 优势
- 有公开仓库数据可追踪，便于学习和选型。
- 可以从 README、入口文件、配置和核心模块逐层阅读。

### 局限或风险
- README 质量、Release 节奏、Issue 响应和 License 需要继续核实。
- AI 总结不能替代安全审计或商业合规审查。

### 快速上手建议
1. 先读 README 并跑通最小示例。
2. 查看配置文件和入口文件。
3. 沿核心模块阅读主调用链。
4. 做一个小功能改造并记录学习笔记。
"""


def format_learning_plan(analysis: Dict[str, Any], period: str, level: str) -> str:
    repo = analysis["repo"]
    steps = analysis["learning_path"]
    if period == "3 天":
        phases = ["第 1 天：运行和理解 README", "第 2 天：阅读入口与核心模块", "第 3 天：完成小改造并总结"]
    elif period == "2 周":
        phases = [
            "第 1-2 天：读 README、安装依赖、跑通示例",
            "第 3-4 天：阅读入口文件和配置文件",
            "第 5-7 天：阅读核心业务模块并画出调用链",
            "第 8-10 天：阅读 Workflow / Prompt / Tool / RAG 等关键能力",
            "第 11-13 天：完成一个二次开发小功能",
            "第 14 天：整理技术笔记和复盘",
        ]
    else:
        phases = ["阶段 1：运行项目", "阶段 2：阅读核心模块", "阶段 3：实践改造", "阶段 4：总结输出"]

    step_lines = "\n".join(
        f"- {row['步骤']}：{row['目标']}（重点：`{row['重点文件']}`）"
        for row in steps
    )
    phase_lines = "\n".join(f"- {phase}" for phase in phases)
    return f"""
## {repo.get('full_name')} 学习规划

- 学习周期：{period}
- 用户水平：{level}
- 学习目标：从运行项目到理解核心结构，再完成一个小功能改造。

### 分阶段计划
{phase_lines}

### 推荐阅读路线
{step_lines}

### 实践任务
- 跑通官方示例或最小 Demo。
- 记录项目结构和核心调用链。
- 修改一个配置、Prompt、Tool、API 或示例流程。
- 输出一篇学习笔记或技术分享。

### 最终产出
- 可运行 Demo
- 项目结构笔记
- 核心流程图
- 一个二次开发小功能
"""


def activity_level(repo: Dict[str, Any]) -> str:
    pushed = (repo.get("pushed_at") or repo.get("updated_at") or "")[:10]
    issues = repo.get("open_issues_count", 0) or 0
    if not pushed:
        return "未知"
    if issues > 0:
        return f"较活跃，最近更新 {pushed}"
    return f"最近更新 {pushed}"


def doc_quality(repo: Dict[str, Any]) -> str:
    if repo.get("has_pages") or repo.get("homepage"):
        return "较好，有主页或文档入口"
    if repo.get("description"):
        return "中等，可先读 README"
    return "信息较少"


def risk_summary(repo: Dict[str, Any]) -> str:
    risks = []
    if not repo.get("license"):
        risks.append("License 不清晰")
    if (repo.get("open_issues_count", 0) or 0) > 500:
        risks.append("Issue 较多")
    if not risks:
        risks.append("需复核维护节奏")
    return "、".join(risks)


def format_count(value: Any) -> str:
    try:
        number = int(value or 0)
    except (TypeError, ValueError):
        return "0"
    if number >= 1000000:
        return f"{number / 1000000:.1f}M"
    if number >= 1000:
        return f"{number / 1000:.1f}K"
    return str(number)


def fallback_readme_report(repo: Dict[str, Any], readme: str) -> str:
    description = repo.get("description") or "README 暂无足够描述。"
    readme_preview = readme[:1200] if readme else "未获取到 README。"
    return f"""
## 3 分钟读懂该项目

### 项目简介
{description}

### 项目解决的问题
根据仓库描述和 README，该项目面向 `{repo.get('full_name')}` 相关场景，具体细节建议继续阅读 README 和核心目录。

### 核心功能
- 提供开源项目中的主要能力实现
- 包含可学习的工程结构和技术选型
- 可结合源码进一步分析入口、配置和核心模块

### 技术特点
主要语言: {repo.get('language') or 'Unknown'}

### 安装步骤 / 快速开始 / 使用方式 / 注意事项
以下是 README 摘录:

```text
{readme_preview}
```
"""


def fallback_answer(question: str, analysis: Optional[Dict[str, Any]]) -> str:
    if not analysis:
        return "当前没有足够项目上下文。请先在项目分析页加载仓库。"
    modules = analysis.get("modules", [])
    files = "\n".join(f"- {row['模块']}: {row['文件']}" for row in modules[:8]) or "暂未识别到核心文件。"
    return f"""
基于当前已获取的 README 和目录结构，可以先这样判断:

{analysis.get('repo', {}).get('description') or '该项目暂无描述。'}

相关核心文件:
{files}

你的问题是: {question}

当前未启用 LLM，因此这是规则分析结果。配置 API key 后可以得到更深入的自然语言回答。
"""


def fallback_daily_report(repos: List[Dict[str, Any]], category: str) -> str:
    lines = [f"# GitHub Daily Report - {category}", "", "## 今日推荐"]
    for idx, repo in enumerate(repos[:10], start=1):
        lines.append(
            f"{idx}. [{repo.get('full_name')}]({repo.get('html_url')}) - "
            f"{repo.get('description') or '暂无描述'} "
            f"({repo.get('stargazers_count', 0)} stars)"
        )
    lines.append("\n## 学习建议\n优先选择 README 清晰、最近仍在更新、示例和测试完整的项目。")
    return "\n".join(lines)


def rule_recommendation(repo: Dict[str, Any], score: float) -> str:
    stars = repo.get("stargazers_count", 0) or 0
    updated = (repo.get("updated_at") or "")[:10]
    language = repo.get("language") or "Unknown"
    if score >= 8:
        return f"社区关注度高，{language} 技术栈清晰，最近更新于 {updated}，适合作为重点学习对象。"
    if stars > 100:
        return f"已有一定社区基础，适合用于了解 {language} 方向的工程实践。"
    return f"项目体量可能较轻，适合作为快速浏览或专项学习素材。"


def difficulty(repo: Dict[str, Any]) -> str:
    stars = repo.get("stargazers_count", 0) or 0
    size = repo.get("size", 0) or 0
    if size > 80000 or stars > 50000:
        return "较高"
    if size > 15000 or stars > 5000:
        return "中等"
    return "较低"


if __name__ == "__main__":
    main()
