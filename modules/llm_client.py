"""Small LLM client with DeepSeek/OpenAI-compatible support."""

from typing import Any, Dict, List, Optional

import requests

import config


class LLMClient:
    """Call configured LLM providers and expose product-specific helpers."""

    def __init__(self, provider: Optional[str] = None, model: Optional[str] = None):
        self.provider = provider or config.DEFAULT_LLM_PROVIDER
        if self.provider not in config.LLM_PROVIDERS:
            self.provider = "deepseek"
        self.model = model or config.LLM_PROVIDERS[self.provider]["model"]

    def available_providers(self) -> List[str]:
        return [
            name for name, meta in config.LLM_PROVIDERS.items()
            if meta.get("api_key")
        ]

    def provider_status(self) -> Dict[str, bool]:
        return {
            name: bool(meta.get("api_key"))
            for name, meta in config.LLM_PROVIDERS.items()
        }

    def set_provider(self, provider: str, model: Optional[str] = None) -> None:
        if provider in config.LLM_PROVIDERS:
            self.provider = provider
            self.model = model or config.LLM_PROVIDERS[provider]["model"]

    def is_ready(self) -> bool:
        return bool(config.LLM_PROVIDERS.get(self.provider, {}).get("api_key"))

    def generate(self, prompt: str, system_prompt: str = "", max_tokens: int = 1800) -> str:
        meta = config.LLM_PROVIDERS.get(self.provider)
        if not meta or not meta.get("api_key"):
            return ""

        if meta.get("compatible") == "anthropic":
            return self._generate_anthropic(meta, prompt, system_prompt, max_tokens)
        return self._generate_openai_compatible(meta, prompt, system_prompt, max_tokens)

    def _generate_openai_compatible(
        self,
        meta: Dict[str, Any],
        prompt: str,
        system_prompt: str,
        max_tokens: int,
    ) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = requests.post(
            f"{meta['base_url']}/chat/completions",
            headers={
                "Authorization": f"Bearer {meta['api_key']}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model or meta["model"],
                "messages": messages,
                "temperature": 0.35,
                "max_tokens": max_tokens,
            },
            timeout=config.REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()

    def _generate_anthropic(
        self,
        meta: Dict[str, Any],
        prompt: str,
        system_prompt: str,
        max_tokens: int,
    ) -> str:
        payload: Dict[str, Any] = {
            "model": self.model or meta["model"],
            "max_tokens": max_tokens,
            "temperature": 0.35,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system_prompt:
            payload["system"] = system_prompt
        response = requests.post(
            f"{meta['base_url']}/messages",
            headers={
                "x-api-key": meta["api_key"],
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=config.REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
        return "".join(part.get("text", "") for part in data.get("content", [])).strip()

    def recommend_repo(self, repo: Dict[str, Any]) -> str:
        prompt = f"""
请为这个 GitHub 仓库生成 80 字以内的中文推荐理由。

项目: {repo.get('full_name')}
描述: {repo.get('description') or '无'}
语言: {repo.get('language') or 'Unknown'}
Stars: {repo.get('stargazers_count', 0)}
Forks: {repo.get('forks_count', 0)}
最近更新: {(repo.get('updated_at') or '')[:10]}
"""
        return self.generate(prompt, "你是专业的开源项目推荐助手。", max_tokens=300)

    def analyze_readme(self, repo: Dict[str, Any], readme: str) -> str:
        prompt = f"""
请基于 README 生成《3 分钟读懂该项目》，使用中文 Markdown。

项目: {repo.get('full_name')}
描述: {repo.get('description') or '无'}

README:
{readme[:12000]}

输出必须包含:
1. 项目简介
2. 项目解决的问题
3. 核心功能
4. 技术特点
5. 安装步骤
6. 快速开始
7. 使用方式
8. 注意事项
"""
        return self.generate(prompt, "你是严谨的开源项目阅读助手。", max_tokens=2200)

    def analyze_architecture(self, context: str) -> str:
        prompt = f"""
请分析下面 GitHub 项目的整体架构和核心代码模块，使用中文 Markdown。

{context}

重点覆盖 Main、Controller、Service、Agent、Workflow、Prompt、Tool、Memory、RAG、Config、Utils 等模块。
"""
        return self.generate(prompt, "你是资深软件架构师。", max_tokens=2200)

    def answer_question(self, question: str, context: str) -> str:
        prompt = f"""
请基于给定项目上下文回答用户问题。若上下文不足，请明确说明不确定之处。

项目上下文:
{context}

用户问题:
{question}
"""
        return self.generate(prompt, "你是专业、准确的代码学习助手。", max_tokens=1600)

    def compare_repos(self, repos: List[Dict[str, Any]]) -> str:
        repo_lines = "\n\n".join(
            f"""### {repo.get('full_name')}
- 描述: {repo.get('description') or '无'}
- 语言: {repo.get('language') or 'Unknown'}
- Stars: {repo.get('stargazers_count', 0)}
- Forks: {repo.get('forks_count', 0)}
- Issues: {repo.get('open_issues_count', 0)}
- 最近更新: {(repo.get('updated_at') or '')[:10]}
"""
            for repo in repos
        )
        prompt = f"""
请对比这些 GitHub 项目，并输出 Markdown 表格:

{repo_lines}

表格列为: 对比项、项目A、项目B。对比项包含项目定位、技术栈、Agent 能力、学习难度、社区活跃度、推荐指数。若超过两个项目，请扩展列。
"""
        return self.generate(prompt, "你是客观的技术选型分析师。", max_tokens=1800)

    def daily_report(self, repos: List[Dict[str, Any]], category: str) -> str:
        repo_lines = "\n".join(
            f"{idx + 1}. {repo.get('full_name')} - {repo.get('description') or '无'} "
            f"({repo.get('stargazers_count', 0)} stars, {repo.get('language') or 'Unknown'})"
            for idx, repo in enumerate(repos[:10])
        )
        prompt = f"""
请基于以下仓库生成《GitHub Daily Report》，类别: {category}。

{repo_lines}

包含今日概况、重点项目、技术趋势、学习建议。
"""
        return self.generate(prompt, "你是技术内容编辑。", max_tokens=1800)
