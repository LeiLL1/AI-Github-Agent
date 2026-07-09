"""Rule-based repository analysis helpers."""

from pathlib import Path
from typing import Any, Dict, List


DIRECTORY_DESCRIPTIONS = {
    "src": "核心源代码",
    "app": "应用入口或业务代码",
    "lib": "库代码或公共模块",
    "pkg": "公共包",
    "cmd": "命令行入口",
    "internal": "内部实现模块",
    "docs": "项目文档",
    "examples": "示例代码",
    "test": "测试代码",
    "tests": "测试代码",
    "config": "配置文件",
    "configs": "配置文件",
    "scripts": "脚本工具",
    "tools": "工具模块",
    "prompts": "Prompt 模板",
    "templates": "模板文件",
    "assets": "静态资源",
    "public": "前端公共资源",
    ".github": "GitHub 工作流与社区配置",
}

TECH_KEYWORDS = {
    "前端": {
        "React": ["react", "next"],
        "Vue": ["vue", "nuxt"],
        "Next.js": ["next.js", "nextjs", "next/"],
    },
    "后端": {
        "Spring Boot": ["spring-boot", "spring boot", "springframework"],
        "Spring AI": ["spring-ai", "spring ai"],
        "FastAPI": ["fastapi"],
        "Django": ["django"],
        "Flask": ["flask"],
    },
    "AI 框架": {
        "LangChain": ["langchain"],
        "LangGraph": ["langgraph"],
        "AutoGen": ["autogen"],
        "CrewAI": ["crewai"],
        "LlamaIndex": ["llamaindex", "llama_index"],
    },
    "数据库": {
        "MySQL": ["mysql"],
        "PostgreSQL": ["postgres", "postgresql"],
        "Redis": ["redis"],
        "MongoDB": ["mongodb", "mongo"],
        "Milvus": ["milvus"],
        "ChromaDB": ["chromadb", "chroma"],
    },
    "部署": {
        "Docker": ["dockerfile", "docker-compose", "docker "],
        "Kubernetes": ["kubernetes", "k8s", "helm"],
    },
}

MODULE_RULES = {
    "Main": ["main.", "app.", "__main__", "server.", "index."],
    "Controller/API": ["controller", "route", "api", "endpoint"],
    "Service": ["service", "manager", "handler"],
    "Agent": ["agent", "assistant", "chatbot"],
    "Workflow": ["workflow", "pipeline", "graph", "chain", "orchestrator"],
    "Prompt": ["prompt", "template"],
    "Tool": ["tool", "function_call", "function-call"],
    "Memory": ["memory", "history", "buffer"],
    "RAG": ["rag", "retriever", "embedding", "vector", "index"],
    "Config": ["config", "settings", ".env", "application."],
    "Utils": ["util", "helper", "common"],
}


class Analyzer:
    def summarize_structure(self, structure: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        rows = []
        seen = set()
        for item in structure:
            if item.get("type") != "dir":
                continue
            path = item.get("path", "")
            top = path.split("/")[0].lower()
            if top in seen:
                continue
            seen.add(top)
            rows.append({
                "目录": path,
                "说明": DIRECTORY_DESCRIPTIONS.get(top, "项目目录"),
            })
        return rows[:30]

    def identify_core_modules(self, structure: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        modules: List[Dict[str, str]] = []
        files = [item for item in structure if item.get("type") == "file"]
        for label, keywords in MODULE_RULES.items():
            matches = []
            for item in files:
                path = item.get("path", "")
                low = path.lower()
                if any(keyword in low for keyword in keywords):
                    matches.append(path)
            if matches:
                modules.append({
                    "模块": label,
                    "文件": "\n".join(matches[:6]),
                    "说明": self._module_description(label),
                })
        return modules

    def detect_tech_stack(
        self,
        repo: Dict[str, Any],
        languages: Dict[str, int],
        structure: List[Dict[str, Any]],
        readme: str,
    ) -> Dict[str, List[str]]:
        text = " ".join([
            repo.get("full_name", ""),
            repo.get("description") or "",
            readme[:20000],
            " ".join(item.get("path", "") for item in structure),
        ]).lower()

        result: Dict[str, List[str]] = {
            "开发语言": list(languages.keys()) or ([repo.get("language")] if repo.get("language") else []),
            "前端": [],
            "后端": [],
            "AI 框架": [],
            "数据库": [],
            "部署": [],
        }
        for category, techs in TECH_KEYWORDS.items():
            for tech, keywords in techs.items():
                if any(keyword in text for keyword in keywords):
                    result[category].append(tech)
        return result

    def architecture_summary(self, repo: Dict[str, Any], modules: List[Dict[str, str]]) -> str:
        language = repo.get("language") or "Unknown"
        if any(row["模块"] == "Agent" for row in modules):
            style = "Agent/Workflow 驱动"
        elif any(row["模块"] == "RAG" for row in modules):
            style = "RAG 检索增强生成"
        elif any(row["模块"] == "Controller/API" for row in modules):
            style = "API 服务分层"
        else:
            style = "常规开源项目结构"
        return f"该项目主要使用 {language}，结构上接近 {style}。建议先从入口、配置和核心业务模块读起。"

    def build_context(
        self,
        repo: Dict[str, Any],
        readme: str,
        structure: List[Dict[str, Any]],
        tech_stack: Dict[str, List[str]],
        modules: List[Dict[str, str]],
    ) -> str:
        structure_text = "\n".join(item.get("path", "") for item in structure[:80])
        modules_text = "\n".join(f"- {m['模块']}: {m['文件']}" for m in modules[:12])
        tech_text = "\n".join(f"- {k}: {', '.join(v) or '未识别'}" for k, v in tech_stack.items())
        return f"""
项目: {repo.get('full_name')}
简介: {repo.get('description') or '无'}
语言: {repo.get('language') or 'Unknown'}
Stars: {repo.get('stargazers_count', 0)}
Forks: {repo.get('forks_count', 0)}

技术栈:
{tech_text}

核心模块:
{modules_text or '未识别'}

目录结构:
{structure_text}

README 摘录:
{readme[:6000]}
""".strip()

    @staticmethod
    def recommendation_score(repo: Dict[str, Any]) -> float:
        stars = repo.get("stargazers_count", 0) or 0
        forks = repo.get("forks_count", 0) or 0
        issues = repo.get("open_issues_count", 0) or 0
        size = repo.get("size", 0) or 0
        score = 5 + min(stars / 2000, 2.2) + min(forks / 500, 1.2)
        if issues > 0:
            score += 0.4
        if size > 0:
            score += 0.2
        return round(min(score, 10), 1)

    @staticmethod
    def key_files_for_learning(structure: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        files = [item.get("path", "") for item in structure if item.get("type") == "file"]
        buckets = {
            "入口文件": ["main", "app", "server", "index", "__main__"],
            "配置文件": ["config", "settings", "pyproject", "package.json", "pom.xml", "go.mod", "cargo.toml"],
            "核心业务": ["src", "core", "service", "agent", "workflow", "rag"],
            "测试代码": ["test", "spec"],
        }
        result = {}
        for label, keywords in buckets.items():
            result[label] = [path for path in files if any(k in path.lower() for k in keywords)][:8]
        return result

    @staticmethod
    def _module_description(label: str) -> str:
        descriptions = {
            "Main": "项目启动入口或主流程",
            "Controller/API": "HTTP/API 接口层",
            "Service": "业务服务层",
            "Agent": "智能体核心逻辑",
            "Workflow": "流程编排或图执行逻辑",
            "Prompt": "提示词模板与提示构造",
            "Tool": "工具调用或外部能力封装",
            "Memory": "上下文、历史或缓存管理",
            "RAG": "检索、向量化、索引或生成增强模块",
            "Config": "运行配置与环境参数",
            "Utils": "通用工具函数",
        }
        return descriptions.get(label, "核心模块")
