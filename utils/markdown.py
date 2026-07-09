"""
AI GitHub Agent - Markdown 解析器
"""
import re
from typing import List, Dict, Any, Optional
from markdown import Markdown


class MarkdownParser:
    """Markdown 解析器"""
    
    def __init__(self):
        """初始化解析器"""
        self.md = Markdown(extensions=[
            'tables',
            'fenced_code',
            'codehilite',
            'nl2br',
            'sane_lists'
        ])
    
    def parse(self, content: str) -> str:
        """
        解析 Markdown
        
        Args:
            content: Markdown 内容
            
        Returns:
            HTML 内容
        """
        return self.md.convert(content)
    
    def extract_sections(self, content: str) -> List[Dict[str, str]]:
        """
        提取章节
        
        Args:
            content: Markdown 内容
            
        Returns:
            章节列表
        """
        sections = []
        
        # 按标题分割
        pattern = r'^(#{1,6})\s+(.+)$'
        lines = content.split('\n')
        
        current_section = None
        current_content = []
        
        for line in lines:
            match = re.match(pattern, line)
            
            if match:
                # 保存上一个章节
                if current_section:
                    sections.append({
                        'level': current_section['level'],
                        'title': current_section['title'],
                        'content': '\n'.join(current_content).strip()
                    })
                
                # 开始新章节
                level = len(match.group(1))
                title = match.group(2).strip()
                current_section = {'level': level, 'title': title}
                current_content = []
            else:
                if current_section is not None:
                    current_content.append(line)
        
        # 保存最后一个章节
        if current_section:
            sections.append({
                'level': current_section['level'],
                'title': current_section['title'],
                'content': '\n'.join(current_content).strip()
            })
        
        return sections
    
    def extract_code_blocks(self, content: str) -> List[Dict[str, str]]:
        """
        提取代码块
        
        Args:
            content: Markdown 内容
            
        Returns:
            代码块列表
        """
        code_blocks = []
        
        # 匹配 fenced code blocks
        pattern = r'```(\w*)\n(.*?)```'
        matches = re.findall(pattern, content, re.DOTALL)
        
        for lang, code in matches:
            code_blocks.append({
                'language': lang,
                'code': code.strip()
            })
        
        return code_blocks
    
    def extract_links(self, content: str) -> List[Dict[str, str]]:
        """
        提取链接
        
        Args:
            content: Markdown 内容
            
        Returns:
            链接列表
        """
        links = []
        
        # 匹配 [text](url) 格式
        pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        matches = re.findall(pattern, content)
        
        for text, url in matches:
            links.append({
                'text': text,
                'url': url
            })
        
        return links
    
    def extract_images(self, content: str) -> List[Dict[str, str]]:
        """
        提取图片
        
        Args:
            content: Markdown 内容
            
        Returns:
            图片列表
        """
        images = []
        
        # 匹配 ![alt](url) 格式
        pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
        matches = re.findall(pattern, content)
        
        for alt, url in matches:
            images.append({
                'alt': alt,
                'url': url
            })
        
        return images
    
    def extract_tables(self, content: str) -> List[List[List[str]]]:
        """
        提取表格
        
        Args:
            content: Markdown 内容
            
        Returns:
            表格列表，每个表格是行列表
        """
        tables = []
        
        # 匹配表格
        lines = content.split('\n')
        current_table = []
        in_table = False
        
        for line in lines:
            # 检查是否是表格行
            if '|' in line:
                if not in_table:
                    in_table = True
                    current_table = []
                
                # 解析表格行
                cells = [cell.strip() for cell in line.split('|')]
                # 移除首尾空单元格
                if cells and cells[0] == '':
                    cells = cells[1:]
                if cells and cells[-1] == '':
                    cells = cells[:-1]
                
                # 跳过分隔行 (|---|---|)
                if not all(re.match(r'^-+$', cell) for cell in cells):
                    current_table.append(cells)
            else:
                if in_table:
                    tables.append(current_table)
                    in_table = False
                    current_table = []
        
        # 保存最后一个表格
        if in_table and current_table:
            tables.append(current_table)
        
        return tables
    
    def extract_headings(self, content: str) -> List[Dict[str, Any]]:
        """
        提取标题
        
        Args:
            content: Markdown 内容
            
        Returns:
            标题列表
        """
        headings = []
        
        pattern = r'^(#{1,6})\s+(.+)$'
        lines = content.split('\n')
        
        for line in lines:
            match = re.match(pattern, line)
            if match:
                level = len(match.group(1))
                text = match.group(2).strip()
                headings.append({
                    'level': level,
                    'text': text,
                    'id': self._generate_id(text)
                })
        
        return headings
    
    def _generate_id(self, text: str) -> str:
        """生成标题 ID"""
        # 转小写，替换空格为连字符，移除非字母数字字符
        text = text.lower()
        text = re.sub(r'\s+', '-', text)
        text = re.sub(r'[^a-z0-9\-]', '', text)
        return text
    
    def extract_installation(self, content: str) -> Optional[str]:
        """
        提取安装说明
        
        Args:
            content: Markdown 内容
            
        Returns:
            安装说明
        """
        # 关键词
        keywords = ['install', '安装', 'setup', 'getting started', '快速开始', '入门']
        
        sections = self.extract_sections(content)
        
        for section in sections:
            title_lower = section['title'].lower()
            if any(kw in title_lower for kw in keywords):
                return section['content']
        
        return None
    
    def extract_quick_start(self, content: str) -> Optional[str]:
        """
        提取快速开始指南
        
        Args:
            content: Markdown 内容
            
        Returns:
            快速开始指南
        """
        keywords = ['quick start', 'quickstart', '快速开始', 'getting started', '入门指南', 'tutorial']
        
        sections = self.extract_sections(content)
        
        for section in sections:
            title_lower = section['title'].lower()
            if any(kw in title_lower for kw in keywords):
                return section['content']
        
        return None
    
    def extract_dependencies(self, content: str) -> List[str]:
        """
        提取依赖项
        
        Args:
            content: Markdown 内容
            
        Returns:
            依赖列表
        """
        dependencies = []
        
        # 匹配常见的依赖文件引用
        patterns = [
            r'(?:pip install|npm install|yarn add|go get|apt install)\s+([^\n]+)',
            r'(?:requirements\.txt|package\.json|Pipfile|Cargo\.toml|go\.mod):?\s*\n((?:\s*-?\s*[^\n]+\n)*)',
            r'```\w*\n((?:[^\n]+\n)*)```',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                # 分割多行依赖
                lines = match.strip().split('\n')
                for line in lines:
                    line = line.strip().lstrip('-* ')
                    if line and line not in dependencies:
                        dependencies.append(line)
        
        return dependencies[:20]  # 限制数量
    
    def summarize(self, content: str, max_length: int = 500) -> str:
        """
        摘要内容
        
        Args:
            content: 内容
            max_length: 最大长度
            
        Returns:
            摘要
        """
        # 移除代码块
        content = re.sub(r'```[\s\S]*?```', '', content)
        
        # 移除图片和链接
        content = re.sub(r'!\[.*?\]\(.*?\)', '', content)
        content = re.sub(r'\[([^\]]+)\]\(.*?\)', r'\1', content)
        
        # 移除标题标记
        content = re.sub(r'^#{1,6}\s+', '', content, flags=re.MULTILINE)
        
        # 移除多余空行
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # 截断
        if len(content) > max_length:
            content = content[:max_length] + '...'
        
        return content.strip()
    
    def to_plain_text(self, content: str) -> str:
        """
        转换为纯文本
        
        Args:
            content: Markdown 内容
            
        Returns:
            纯文本
        """
        # 移除代码块
        content = re.sub(r'```[\s\S]*?```', '', content)
        
        # 移除行内代码
        content = re.sub(r'`([^`]+)`', r'\1', content)
        
        # 移除图片
        content = re.sub(r'!\[.*?\]\(.*?\)', '', content)
        
        # 转换链接为纯文本
        content = re.sub(r'\[([^\]]+)\]\(.*?\)', r'\1', content)
        
        # 移除标题标记
        content = re.sub(r'^#{1,6}\s+', '', content, flags=re.MULTILINE)
        
        # 移除加粗和斜体
        content = re.sub(r'\*\*([^\*]+)\*\*', r'\1', content)
        content = re.sub(r'\*([^\*]+)\*', r'\1', content)
        content = re.sub(r'__([^_]+)__', r'\1', content)
        content = re.sub(r'_([^_]+)_', r'\1', content)
        
        return content.strip()
