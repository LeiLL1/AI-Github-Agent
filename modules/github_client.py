"""GitHub API client used by AI GitHub Agent."""

import base64
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import requests

import config


class GitHubClient:
    def __init__(self, token: Optional[str] = None):
        self.base_url = config.GITHUB_API_BASE
        self.token = token or config.GITHUB_TOKEN
        self.headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "AI-GitHub-Agent",
        }
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"

    def _request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        response = requests.get(
            f"{self.base_url}{endpoint}",
            headers=self.headers,
            params=params,
            timeout=config.REQUEST_TIMEOUT,
        )
        if response.status_code == 404:
            return None
        if response.status_code in (403, 429):
            remaining = response.headers.get("X-RateLimit-Remaining")
            reset = response.headers.get("X-RateLimit-Reset")
            if remaining == "0" and reset:
                reset_at = datetime.fromtimestamp(int(reset)).strftime("%Y-%m-%d %H:%M")
                raise RuntimeError(f"GitHub API rate limit exceeded. Reset at {reset_at}.")
        response.raise_for_status()
        return response.json()

    def search_repos(
        self,
        query: str,
        language: str = "",
        min_stars: int = 0,
        license_id: str = "",
        recent: bool = False,
        sort: str = "stars",
        order: str = "desc",
        per_page: int = 10,
    ) -> List[Dict[str, Any]]:
        q = query.strip()
        if language and language.lower() != "all":
            q = f"{q} language:{language}"
        if min_stars:
            q = f"{q} stars:>={min_stars}"
        if license_id:
            q = f"{q} license:{license_id}"
        if recent:
            recent_date = (datetime.now(timezone.utc).date() - timedelta(days=180)).isoformat()
            q = f"{q} pushed:>{recent_date}"
        data = self._request(
            "/search/repositories",
            {
                "q": q,
                "sort": sort,
                "order": order,
                "per_page": min(max(per_page, 1), 50),
            },
        )
        return data.get("items", []) if data else []

    def resolve_repo(self, value: str) -> Optional[Dict[str, Any]]:
        full_name = self.normalize_repo_name(value)
        if full_name:
            return self.get_repo(full_name)
        results = self.search_repos(f"{value} in:name", sort="stars", per_page=1)
        return results[0] if results else None

    def get_repo(self, full_name_or_owner: str, repo: Optional[str] = None) -> Optional[Dict[str, Any]]:
        full_name = f"{full_name_or_owner}/{repo}" if repo else full_name_or_owner
        full_name = self.normalize_repo_name(full_name)
        if not full_name:
            return None
        return self._request(f"/repos/{full_name}")

    def get_readme(self, full_name: str) -> str:
        data = self._request(f"/repos/{full_name}/readme")
        if not data or not data.get("content"):
            return ""
        raw = data["content"].replace("\n", "")
        try:
            return base64.b64decode(raw).decode("utf-8", errors="replace")
        except Exception:
            return ""

    def get_contents(self, full_name: str, path: str = "") -> List[Dict[str, Any]]:
        endpoint = f"/repos/{full_name}/contents"
        if path:
            endpoint += f"/{path}"
        data = self._request(endpoint)
        if not data:
            return []
        return data if isinstance(data, list) else [data]

    def get_file_content(self, full_name: str, path: str) -> str:
        data = self._request(f"/repos/{full_name}/contents/{path}")
        if not data or not data.get("content"):
            return ""
        if data.get("encoding") == "base64":
            return base64.b64decode(data["content"]).decode("utf-8", errors="replace")
        return data.get("content", "")

    def get_repo_structure(self, full_name: str, max_items: int = config.MAX_STRUCTURE_ITEMS) -> List[Dict[str, Any]]:
        structure: List[Dict[str, Any]] = []
        queue = [""]
        ignored = {
            ".git", "node_modules", "dist", "build", "target", ".venv", "venv",
            "__pycache__", ".next", ".turbo", "vendor",
        }

        while queue and len(structure) < max_items:
            path = queue.pop(0)
            for item in self.get_contents(full_name, path):
                name = item.get("name", "")
                if name in ignored:
                    continue
                structure.append(item)
                if item.get("type") == "dir" and len(structure) < max_items:
                    queue.append(item.get("path", ""))
        return structure[:max_items]

    def get_languages(self, full_name: str) -> Dict[str, int]:
        return self._request(f"/repos/{full_name}/languages") or {}

    def get_releases(self, full_name: str, per_page: int = 5) -> List[Dict[str, Any]]:
        return self._request(f"/repos/{full_name}/releases", {"per_page": per_page}) or []

    def get_topics(self, full_name: str) -> List[str]:
        data = self._request(f"/repos/{full_name}/topics")
        return data.get("names", []) if data else []

    def get_issues(self, full_name: str, per_page: int = 5) -> List[Dict[str, Any]]:
        return self._request(
            f"/repos/{full_name}/issues",
            {"state": "open", "per_page": per_page},
        ) or []

    def get_pull_requests(self, full_name: str, per_page: int = 5) -> List[Dict[str, Any]]:
        return self._request(
            f"/repos/{full_name}/pulls",
            {"state": "open", "per_page": per_page},
        ) or []

    def get_contributors(self, full_name: str, per_page: int = 10) -> List[Dict[str, Any]]:
        return self._request(
            f"/repos/{full_name}/contributors",
            {"per_page": per_page},
        ) or []

    def search_files(self, full_name: str, query: str, per_page: int = 5) -> List[Dict[str, Any]]:
        words = " ".join(word for word in query.split()[:5] if len(word) > 2)
        if not words:
            return []
        data = self._request(
            "/search/code",
            {"q": f"repo:{full_name} {words}", "per_page": per_page},
        )
        return data.get("items", []) if data else []

    def daily_recommendations(self, category: str, per_page: int = 10) -> List[Dict[str, Any]]:
        today = datetime.now(timezone.utc).date()
        recent = today - timedelta(days=30)
        week = today - timedelta(days=7)
        queries = {
            "今日热门项目": f"stars:>500 pushed:>{recent.isoformat()}",
            "AI 新项目": f"AI LLM agent created:>{recent.isoformat()} stars:>20",
            "Star 增长最快项目": f"stars:>100 pushed:>{week.isoformat()}",
            "Agent 项目": "agent llm stars:>50",
            "RAG 项目": "RAG retrieval augmented generation stars:>50",
            "Spring AI 项目": "spring-ai stars:>10",
        }
        query = queries.get(category, queries["今日热门项目"])
        return self.search_repos(query, sort="stars", per_page=per_page)

    @staticmethod
    def normalize_repo_name(value: str) -> str:
        value = (value or "").strip().rstrip("/")
        if value.startswith("https://github.com/"):
            value = value.replace("https://github.com/", "", 1)
        if value.startswith("http://github.com/"):
            value = value.replace("http://github.com/", "", 1)
        if value.endswith(".git"):
            value = value[:-4]
        parts = [part for part in value.split("/") if part]
        return "/".join(parts[:2]) if len(parts) >= 2 else ""
