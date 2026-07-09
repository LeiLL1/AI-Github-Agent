"""
AI GitHub Agent - 搜索引擎
"""
from typing import List, Dict, Optional, Any
import re
from .github_client import GitHubClient
from .llm_client import LLMClient


class SearchEngine:
    """GitHub 项目搜索引擎"""
    
    def __init__(self, github_client: GitHubClient, llm_client: Optional[LLMClient] = None):
        """
        初始化搜索引擎
        
        Args:
            github_client: GitHub 客户端
            llm_client: LLM 客户端（可选）
        """
        self.github_client = github_client
        self.llm_client = llm_client
    
    def search(
        self,
        query: str,
        language: Optional[str] = None,
        sort: str = "stars",
        per_page: int = 20
    ) -> List[Dict]:
        """
        搜索 GitHub 项目
        
        Args:
            query: 搜索关键词
            language: 编程语言过滤
            sort: 排序方式
            per_page: 每页数量
            
        Returns:
            搜索结果列表
        """
        # 构建查询
        search_query = query
        if language:
            search_query += f" language:{language}"
        
        # 执行搜索
        results = self.github_client.search_repos(
            query=search_query,
            sort=sort,
            per_page=per_page
        )
        
        return results
    
    def recommend(self, query: str, limit: int = 10) -> List[Dict]:
        """
        智能推荐项目
        
        Args:
            query: 搜索关键词
            limit: 返回数量
            
        Returns:
            推荐项目列表
        """
        # 搜索项目
        results = self.search(query, per_page=limit * 2)
        
        if not results:
            return []
        
        # 筛选高质量项目
        high_quality = self._filter_high_quality(results)
        
        # 为每个项目生成推荐理由
        if self.llm_client:
            for repo in high_quality:
                try:
                    reason = self.llm_client.recommend_repo(repo)
                    repo['recommendation_reason'] = reason
                except Exception:
                    repo['recommendation_reason'] = self._generate_basic_reason(repo)
        else:
            for repo in high_quality:
                repo['recommendation_reason'] = self._generate_basic_reason(repo)
        
        # 计算推荐指数
        for repo in high_quality:
            repo['recommendation_score'] = self._calculate_score(repo)
        
        # 按推荐指数排序
        high_quality.sort(key=lambda x: x.get('recommendation_score', 0), reverse=True)
        
        return high_quality[:limit]
    
    def _filter_high_quality(self, repos: List[Dict]) -> List[Dict]:
        """
        筛选高质量项目
        
        Args:
            repos: 项目列表
            
        Returns:
            高质量项目列表
        """
        filtered = []
        
        for repo in repos:
            # 检查基本质量指标
            stars = repo.get('stargazers_count', 0)
            forks = repo.get('forks_count', 0)
            has_description = bool(repo.get('description'))
            
            # 过滤条件
            if stars < 10:  # 至少 10 个 star
                continue
            
            if not has_description:  # 必须有描述
                continue
            
            # 检查是否最近更新（一年内）
            updated_at = repo.get('updated_at', '')
            if updated_at:
                try:
                    from datetime import datetime
                    from dateutil import parser
                    update_date = parser.parse(updated_at)
                    days_since_update = (datetime.now() - update_date).days
                    if days_since_update > 365:
                        continue
                except Exception:
                    pass
            
            filtered.append(repo)
        
        return filtered
    
    def _generate_basic_reason(self, repo: Dict) -> str:
        """
        生成基本推荐理由
        
        Args:
            repo: 仓库信息
            
        Returns:
            推荐理由
        """
        stars = repo.get('stargazers_count', 0)
        forks = repo.get('forks_count', 0)
        language = repo.get('language', 'Unknown')
        description = repo.get('description', '')
        
        reasons = []
        
        # Star 数量
        if stars > 10000:
            reasons.append("热门项目，社区认可度高")
        elif stars > 1000:
            reasons.append("受关注的优质项目")
        elif stars > 100:
            reasons.append("潜力项目")
        
        # Fork 比例
        fork_ratio = forks / max(stars, 1)
        if fork_ratio > 0.3:
            reasons.append("社区参与度高，有良好的二次开发生态")
        
        # 语言
        reasons.append(f"使用 {language} 开发")
        
        # 描述关键词
        keywords = {
            'ai': 'AI 相关',
            'llm': '大语言模型相关',
            'agent': 'Agent 开发',
            'rag': 'RAG 技术',
            'fastapi': 'FastAPI 框架',
            'react': 'React 前端',
            'django': 'Django 框架',
            'spring': 'Spring 生态'
        }
        
        desc_lower = description.lower()
        for kw, desc in keywords.items():
            if kw in desc_lower:
                reasons.append(desc)
                break
        
        return '；'.join(reasons[:3]) if reasons else "值得关注的项目"
    
    def _calculate_score(self, repo: Dict) -> float:
        """
        计算推荐指数
        
        Args:
            repo: 仓库信息
            
        Returns:
            推荐指数 (0-100)
        """
        stars = repo.get('stargazers_count', 0)
        forks = repo.get('forks_count', 0)
        issues = repo.get('open_issues_count', 0)
        
        # 基础分数（来自 star）
        star_score = min(50, stars / 100)  # 最高 50 分
        
        # Fork 分数
        fork_score = min(20, forks / 50)  # 最高 20 分
        
        # 社区活跃度（低 issue 数量 = 高活跃度）
        issue_score = max(0, 15 - issues / 10)  # 最高 15 分
        
        # 描述完整性
        desc_score = 15 if repo.get('description') else 0
        
        return star_score + fork_score + issue_score + desc_score
    
    def search_by_topic(self, topic: str, per_page: int = 20) -> List[Dict]:
        """
        按主题搜索项目
        
        Args:
            topic: 主题标签
            per_page: 每页数量
            
        Returns:
            项目列表
        """
        query = f"topic:{topic}"
        return self.github_client.search_repos(query, per_page=per_page)
    
    def search_trending(
        self,
        language: Optional[str] = None,
        date_range: str = "daily"
    ) -> List[Dict]:
        """
        搜索趋势项目
        
        Args:
            language: 编程语言
            date_range: 时间范围 (daily, weekly, monthly)
            
        Returns:
            趋势项目列表
        """
        # 构建查询
        query_parts = [f"created:>{self._get_date_limit(date_range)}"]
        
        if language:
            query_parts.append(f"language:{language}")
        
        query = " ".join(query_parts)
        
        return self.github_client.search_repos(query, sort="stars", per_page=30)
    
    def _get_date_limit(self, date_range: str) -> str:
        """获取日期限制"""
        from datetime import datetime, timedelta
        
        if date_range == "daily":
            days = 1
        elif date_range == "weekly":
            days = 7
        elif date_range == "monthly":
            days = 30
        else:
            days = 1
        
        date = datetime.now() - timedelta(days=days)
        return date.strftime("%Y-%m-%d")
    
    def compare(self, repos: List[Dict]) -> Dict[str, Any]:
        """
        对比多个项目
        
        Args:
            repos: 项目列表
            
        Returns:
            对比结果
        """
        if not repos:
            return {}
        
        comparison = {
            'projects': [],
            'metrics': {},
            'winner': {}
        }
        
        # 收集项目信息
        for repo in repos:
            comparison['projects'].append({
                'full_name': repo.get('full_name'),
                'description': repo.get('description'),
                'stars': repo.get('stargazers_count', 0),
                'forks': repo.get('forks_count', 0),
                'issues': repo.get('open_issues_count', 0),
                'language': repo.get('language'),
                'license': repo.get('license', {}).get('name'),
                'updated': repo.get('updated_at', '')[:10]
            })
        
        # 收集指标
        metrics = ['stars', 'forks', 'issues']
        
        for metric in metrics:
            values = [p.get(metric, 0) for p in comparison['projects']]
            max_val = max(values) if values else 0
            
            comparison['metrics'][metric] = {
                'values': values,
                'max': max_val,
                'winner': comparison['projects'][values.index(max_val)]['full_name'] if max_val > 0 else None
            }
        
        # 综合评分
        for repo in comparison['projects']:
            score = (
                repo['stars'] / 100 +
                repo['forks'] / 50 +
                (100 - min(repo['issues'], 100)) / 10
            )
            repo['score'] = round(score, 2)
        
        # 排序
        comparison['projects'].sort(key=lambda x: x.get('score', 0), reverse=True)
        
        if comparison['projects']:
            comparison['winner']['overall'] = comparison['projects'][0]['full_name']
        
        return comparison
