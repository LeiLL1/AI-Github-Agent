"""Learning path generation."""

from typing import Any, Dict, List, Optional


class LearningPathGenerator:
    def generate(
        self,
        repo: Dict[str, Any],
        tech_stack: Dict[str, List[str]],
        key_files: Dict[str, List[str]],
    ) -> List[Dict[str, str]]:
        text = " ".join(
            [repo.get("full_name", ""), repo.get("description") or ""]
            + [item for values in tech_stack.values() for item in values]
        ).lower()

        steps = [
            ("Step1 阅读 README", "先建立项目目标、使用场景和快速开始的全局认识。", "README.md"),
            ("Step2 本地运行项目", "按安装步骤准备依赖，优先跑通最小示例。", self._first(key_files.get("配置文件"))),
            ("Step3 阅读入口文件", "理解启动流程、参数加载和主调用链。", self._first(key_files.get("入口文件"))),
            ("Step4 阅读配置文件", "梳理环境变量、模型、数据库和第三方服务配置。", self._first(key_files.get("配置文件"))),
            ("Step5 阅读核心业务模块", "跟随一次主要请求或任务执行路径阅读核心代码。", self._first(key_files.get("核心业务"))),
        ]

        if any(token in text for token in ["agent", "langgraph", "crewai", "autogen", "mcp"]):
            steps.extend([
                ("Step6 阅读 Workflow", "看清状态流转、节点编排和异常处理方式。", "workflow / graph"),
                ("Step7 阅读 Prompt", "理解系统提示、任务提示和变量注入方式。", "prompts / templates"),
                ("Step8 阅读 Tool Calling", "理解工具注册、参数校验和结果回传。", "tools"),
                ("Step9 阅读 Memory", "理解对话历史、长期记忆或缓存策略。", "memory / store"),
                ("Step10 做一次小改造", "新增一个工具或节点，验证你是否真正理解主链路。", "examples / tests"),
            ])
        elif any(token in text for token in ["rag", "retriever", "embedding", "vector", "llamaindex"]):
            steps.extend([
                ("Step6 阅读数据加载", "理解文档解析、切分和清洗流程。", "loader / parser"),
                ("Step7 阅读 Embedding", "理解向量模型、批处理和缓存。", "embedding"),
                ("Step8 阅读向量库", "理解索引创建、召回和过滤条件。", "vectorstore / index"),
                ("Step9 阅读生成链路", "理解检索结果如何进入 Prompt 并生成答案。", "rag / chain"),
                ("Step10 调整检索参数", "尝试修改 top_k、chunk_size 或 rerank 策略。", "config / examples"),
            ])
        else:
            steps.extend([
                ("Step6 阅读测试代码", "通过测试用例理解功能边界。", self._first(key_files.get("测试代码"))),
                ("Step7 阅读扩展点", "寻找插件、接口、抽象类或公共 API。", self._first(key_files.get("核心业务"))),
                ("Step8 做一次实践", "修复一个 issue 或添加一个小功能。", "issues / examples"),
            ])

        return [
            {"步骤": title, "目标": goal, "重点文件": file_hint or "按项目实际结构确认"}
            for title, goal, file_hint in steps
        ]

    @staticmethod
    def to_markdown(path: List[Dict[str, str]]) -> str:
        lines = ["## 学习路线"]
        for row in path:
            lines.append(f"### {row['步骤']}")
            lines.append(f"- 目标: {row['目标']}")
            lines.append(f"- 重点文件: `{row['重点文件']}`")
        return "\n".join(lines)

    @staticmethod
    def _first(values: Optional[List[str]]) -> str:
        return values[0] if values else ""
