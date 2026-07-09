"""Intent routing for the chat-first AI GitHub Agent."""

import re
from typing import Any, Dict, List


REPO_PATTERN = re.compile(
    r"(?:https?://github\.com/)?([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)(?:\.git)?"
)


class IntentRouter:
    """Lightweight deterministic router for V1 chat interactions."""

    SEARCH_WORDS = ["找", "搜索", "推荐", "有没有", "项目", "仓库", "repo", "repository"]
    COMPARE_WORDS = ["对比", "比较", "区别", "哪个更", "vs", "VS"]
    INTRO_WORDS = ["介绍", "分析", "总结", "讲讲", "是什么", "读懂"]
    LEARNING_WORDS = ["学习", "路线", "计划", "规划", "上手", "源码", "2 周", "两周", "一周", "3 天"]
    LEARNING_PLAN_WORDS = ["路线", "计划", "规划", "源码", "2 周", "两周", "一周", "3 天", "一个月"]
    MORE_WORDS = ["更多", "换一批", "再来", "更适合", "更简单", "新手", "生产", "商用", "活跃"]

    def route(self, message: str, memory: Dict[str, Any]) -> Dict[str, Any]:
        text = (message or "").strip()
        lowered = text.lower()
        repos = self.extract_repos(text)
        indexes = self.extract_indexes(text)
        filters = self.extract_filters(text)

        if self._contains(text, self.COMPARE_WORDS) or len(repos) >= 2 or len(indexes) >= 2:
            intent = "compare"
        elif self._contains(text, self.SEARCH_WORDS) and not repos:
            intent = "search"
        elif self._contains(text, self.LEARNING_PLAN_WORDS) or (
            repos and self._contains(text, self.LEARNING_WORDS)
        ):
            intent = "learning"
        elif repos and self._contains(text, self.INTRO_WORDS):
            intent = "intro"
        elif repos and not self._contains(text, self.SEARCH_WORDS):
            intent = "intro"
        elif self._contains(text, self.MORE_WORDS) and memory.get("last_search_query"):
            intent = "refine_search"
        elif self._contains(text, self.SEARCH_WORDS):
            intent = "search"
        elif "第" in text and indexes:
            intent = "followup"
        else:
            intent = "chat"

        return {
            "intent": intent,
            "raw": text,
            "repos": repos,
            "indexes": indexes,
            "filters": filters,
            "query": self.extract_query(text, filters, repos),
            "period": self.extract_period(text),
            "level": self.extract_level(text),
        }

    def extract_repos(self, text: str) -> List[str]:
        seen = []
        for match in REPO_PATTERN.findall(text):
            repo = match.strip().strip(".,，。)")
            if repo not in seen:
                seen.append(repo)
        return seen

    def extract_indexes(self, text: str) -> List[int]:
        indexes = []
        for number in re.findall(r"第\s*(\d+)\s*个?", text):
            indexes.append(int(number))
        for number in re.findall(r"\b(\d+)\b", text):
            value = int(number)
            if 1 <= value <= 20 and value not in indexes:
                indexes.append(value)
        return indexes

    def extract_filters(self, text: str) -> Dict[str, Any]:
        filters: Dict[str, Any] = {}
        language_map = {
            "python": "Python",
            "java": "Java",
            "go": "Go",
            "rust": "Rust",
            "typescript": "TypeScript",
            "javascript": "JavaScript",
            "react": "TypeScript",
            "next": "TypeScript",
        }
        lowered = text.lower()
        for key, language in language_map.items():
            if key in lowered:
                filters["language"] = language
                break

        star_match = re.search(r"(\d+)\s*(?:star|stars|\u661f)", lowered)
        if star_match:
            filters["min_stars"] = int(star_match.group(1))
        elif "热门" in text or "生产" in text:
            filters["min_stars"] = 500

        if "最近" in text or "活跃" in text or "维护" in text:
            filters["recent"] = True
        if "新手" in text or "简单" in text or "入门" in text:
            filters["difficulty"] = "入门"
        elif "进阶" in text or "深入" in text or "源码" in text:
            filters["difficulty"] = "进阶"
        if "mit" in lowered:
            filters["license"] = "mit"
        elif "apache" in lowered:
            filters["license"] = "apache-2.0"
        return filters

    def extract_query(self, text: str, filters: Dict[str, Any], repos: List[str]) -> str:
        if repos:
            return repos[0]
        query = text
        noise = [
            "帮我", "请", "找", "搜索", "推荐", "几个", "一些", "适合", "学习",
            "项目", "仓库", "GitHub", "github", "开源", "的", "有没有",
            "更适合", "新手", "生产环境", "商用",
        ]
        for word in noise:
            query = query.replace(word, " ")
        query = re.sub(r"\s+", " ", query).strip()
        return query or text

    def extract_period(self, text: str) -> str:
        if "2周" in text or "两周" in text or "2 周" in text:
            return "2 周"
        if "1周" in text or "一周" in text or "1 周" in text:
            return "1 周"
        if "3天" in text or "三天" in text or "3 天" in text:
            return "3 天"
        if "一个月" in text or "1个月" in text or "1 个月" in text:
            return "1 个月"
        return "1 周"

    def extract_level(self, text: str) -> str:
        if "新手" in text or "入门" in text or "零基础" in text:
            return "新手"
        if "进阶" in text or "深入" in text or "源码" in text:
            return "有经验开发者"
        return "普通开发者"

    @staticmethod
    def _contains(text: str, words: List[str]) -> bool:
        lowered = text.lower()
        return any(word.lower() in lowered for word in words)
