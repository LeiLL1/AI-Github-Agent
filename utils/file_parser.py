"""
AI GitHub Agent - 文件解析器
"""
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import Counter


# 常见代码文件后缀 -> 语言映射
EXTENSION_LANGUAGE_MAP = {
    '.py': 'Python',
    '.js': 'JavaScript',
    '.ts': 'TypeScript',
    '.jsx': 'JavaScript',
    '.tsx': 'TypeScript',
    '.java': 'Java',
    '.c': 'C',
    '.h': 'C',
    '.cpp': 'C++',
    '.hpp': 'C++',
    '.cc': 'C++',
    '.cs': 'C#',
    '.go': 'Go',
    '.rs': 'Rust',
    '.rb': 'Ruby',
    '.php': 'PHP',
    '.swift': 'Swift',
    '.kt': 'Kotlin',
    '.m': 'Objective-C',
    '.sh': 'Shell',
    '.bash': 'Shell',
    '.zsh': 'Shell',
    '.html': 'HTML',
    '.htm': 'HTML',
    '.css': 'CSS',
    '.scss': 'SCSS',
    '.sass': 'Sass',
    '.less': 'Less',
    '.vue': 'Vue',
    '.svelte': 'Svelte',
    '.json': 'JSON',
    '.yaml': 'YAML',
    '.yml': 'YAML',
    '.xml': 'XML',
    '.md': 'Markdown',
    '.markdown': 'Markdown',
    '.sql': 'SQL',
    '.r': 'R',
    '.scala': 'Scala',
    '.dart': 'Dart',
    '.lua': 'Lua',
    '.pl': 'Perl',
    '.toml': 'TOML',
    '.ini': 'INI',
    '.cfg': 'INI',
}

# 常见配置文件名
CONFIG_FILE_NAMES = {
    'package.json', 'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml',
    'requirements.txt', 'Pipfile', 'Pipfile.lock', 'pyproject.toml', 'setup.py',
    'setup.cfg', 'poetry.lock', 'conda.yml', 'environment.yml',
    'Gemfile', 'Gemfile.lock', 'composer.json', 'composer.lock',
    'Cargo.toml', 'Cargo.lock', 'go.mod', 'go.sum',
    'pom.xml', 'build.gradle', 'build.gradle.kts',
    'Makefile', 'CMakeLists.txt', 'configure', 'autogen.sh',
    '.gitignore', '.gitattributes', '.editorconfig',
    '.eslintrc', '.eslintrc.js', '.eslintrc.json', '.prettierrc',
    '.dockerignore', 'Dockerfile', 'docker-compose.yml', 'docker-compose.yaml',
    'tsconfig.json', 'webpack.config.js', 'vite.config.js', 'vite.config.ts',
    'babel.config.js', '.babelrc', 'rollup.config.js',
    'README.md', 'README.rst', 'README.txt', 'README',
    'LICENSE', 'LICENSE.md', 'LICENSE.txt',
    'CHANGELOG.md', 'CONTRIBUTING.md', 'CODE_OF_CONDUCT.md',
}

# 文档文件后缀
DOCUMENT_EXTENSIONS = {'.md', '.markdown', '.rst', '.txt', '.adoc'}

# 图片文件后缀
IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.bmp', '.ico'}


class FileParser:
    """文件解析器 - 用于解析 GitHub 仓库中的各种文件"""

    def __init__(self, max_file_size: int = 1024 * 1024):
        """
        初始化文件解析器

        Args:
            max_file_size: 单个文件最大解析大小（字节），默认 1MB
        """
        self.max_file_size = max_file_size

    # ============================================================
    # 语言识别
    # ============================================================
    def detect_language(self, file_path: str) -> Optional[str]:
        """
        根据文件后缀检测编程语言

        Args:
            file_path: 文件路径

        Returns:
            语言名称，未识别返回 None
        """
        ext = Path(file_path).suffix.lower()
        return EXTENSION_LANGUAGE_MAP.get(ext)

    def is_code_file(self, file_path: str) -> bool:
        """判断是否为代码文件"""
        ext = Path(file_path).suffix.lower()
        lang = EXTENSION_LANGUAGE_MAP.get(ext)
        return lang is not None and lang not in {'JSON', 'YAML', 'XML', 'TOML', 'INI', 'Markdown'}

    def is_document_file(self, file_path: str) -> bool:
        """判断是否为文档文件"""
        ext = Path(file_path).suffix.lower()
        return ext in DOCUMENT_EXTENSIONS

    def is_image_file(self, file_path: str) -> bool:
        """判断是否为图片文件"""
        ext = Path(file_path).suffix.lower()
        return ext in IMAGE_EXTENSIONS

    def is_config_file(self, file_path: str) -> bool:
        """判断是否为配置文件"""
        filename = Path(file_path).name
        return filename in CONFIG_FILE_NAMES

    # ============================================================
    # 文件读取
    # ============================================================
    def read_file(self, file_path: str, encoding: str = 'utf-8') -> Optional[str]:
        """
        读取文件内容

        Args:
            file_path: 文件路径
            encoding: 编码格式

        Returns:
            文件内容，失败返回 None
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return None

            # 大小限制
            if path.stat().st_size > self.max_file_size:
                return None

            # 尝试指定编码，失败则尝试其他常见编码
            for enc in [encoding, 'utf-8', 'gbk', 'latin-1']:
                try:
                    return path.read_text(encoding=enc)
                except UnicodeDecodeError:
                    continue
            return None
        except Exception:
            return None

    # ============================================================
    # 代码统计
    # ============================================================
    def count_lines(self, content: str) -> Dict[str, int]:
        """
        统计代码行数

        Args:
            content: 文件内容

        Returns:
            包含 total/code/comment/blank 的字典
        """
        if not content:
            return {'total': 0, 'code': 0, 'comment': 0, 'blank': 0}

        lines = content.split('\n')
        total = len(lines)
        blank = 0
        comment = 0
        code = 0

        in_block_comment = False

        for line in lines:
            stripped = line.strip()

            # 空行
            if not stripped:
                blank += 1
                continue

            # 块注释（多行）
            if in_block_comment:
                comment += 1
                if '*/' in stripped:
                    in_block_comment = False
                continue

            # 块注释开始
            if stripped.startswith('/*'):
                comment += 1
                if '*/' not in stripped[2:]:
                    in_block_comment = True
                continue

            # 单行注释
            if (stripped.startswith('#') or
                stripped.startswith('//') or
                stripped.startswith('--')):
                comment += 1
                continue

            # Python 单行块注释 # ...
            code += 1

        return {
            'total': total,
            'code': code,
            'comment': comment,
            'blank': blank,
        }

    # ============================================================
    # 文件信息提取
    # ============================================================
    def get_file_info(self, file_path: str, content: Optional[str] = None) -> Dict[str, Any]:
        """
        获取文件的完整信息

        Args:
            file_path: 文件路径
            content: 文件内容（可选，不传则自动读取）

        Returns:
            文件信息字典
        """
        path = Path(file_path)
        filename = path.name
        ext = path.suffix.lower()

        info = {
            'path': file_path,
            'name': filename,
            'extension': ext,
            'language': self.detect_language(file_path),
            'is_code': self.is_code_file(file_path),
            'is_document': self.is_document_file(file_path),
            'is_image': self.is_image_file(file_path),
            'is_config': self.is_config_file(file_path),
        }

        # 读取内容
        if content is None:
            content = self.read_file(file_path)

        if content is not None:
            line_stats = self.count_lines(content)
            info['size'] = len(content.encode('utf-8'))
            info['lines'] = line_stats
            info['chars'] = len(content)
        else:
            info['size'] = 0
            info['lines'] = {'total': 0, 'code': 0, 'comment': 0, 'blank': 0}
            info['chars'] = 0

        return info

    # ============================================================
    # 目录统计
    # ============================================================
    def analyze_directory(self, dir_path: str, max_files: int = 1000) -> Dict[str, Any]:
        """
        分析目录中的文件分布

        Args:
            dir_path: 目录路径
            max_files: 最多分析的文件数

        Returns:
            目录分析结果
        """
        directory = Path(dir_path)
        if not directory.exists() or not directory.is_dir():
            return {'error': f'目录不存在: {dir_path}'}

        languages = Counter()
        extensions = Counter()
        file_types = {'code': 0, 'document': 0, 'image': 0, 'config': 0, 'other': 0}
        total_lines = {'code': 0, 'comment': 0, 'blank': 0, 'total': 0}

        file_count = 0

        try:
            for file_path in directory.rglob('*'):
                if not file_path.is_file():
                    continue

                if file_count >= max_files:
                    break

                # 跳过常见的忽略目录
                if any(part in {'__pycache__', '.git', 'node_modules', 'venv', '.venv', 'dist', 'build', '.idea', '.vscode'}
                       for part in file_path.parts):
                    continue

                file_count += 1
                ext = file_path.suffix.lower()

                if ext:
                    extensions[ext] += 1

                lang = self.detect_language(str(file_path))
                if lang:
                    languages[lang] += 1

                if self.is_code_file(str(file_path)):
                    file_types['code'] += 1
                elif self.is_document_file(str(file_path)):
                    file_types['document'] += 1
                elif self.is_image_file(str(file_path)):
                    file_types['image'] += 1
                elif self.is_config_file(str(file_path)):
                    file_types['config'] += 1
                else:
                    file_types['other'] += 1

                # 只对代码文件统计行数（避免读大文件）
                if self.is_code_file(str(file_path)):
                    try:
                        if file_path.stat().st_size < self.max_file_size:
                            content = file_path.read_text(encoding='utf-8', errors='ignore')
                            stats = self.count_lines(content)
                            total_lines['code'] += stats['code']
                            total_lines['comment'] += stats['comment']
                            total_lines['blank'] += stats['blank']
                            total_lines['total'] += stats['total']
                    except Exception:
                        pass

        except Exception as e:
            return {'error': f'分析失败: {e}'}

        return {
            'total_files': file_count,
            'languages': dict(languages.most_common(10)),
            'extensions': dict(extensions.most_common(15)),
            'file_types': file_types,
            'total_lines': total_lines,
        }

    # ============================================================
    # 依赖文件解析
    # ============================================================
    def parse_requirements_txt(self, content: str) -> List[Dict[str, str]]:
        """
        解析 requirements.txt

        Args:
            content: 文件内容

        Returns:
            依赖列表 [{'name': '...', 'version': '...', 'extras': '...'}]
        """
        deps = []
        if not content:
            return deps

        # 匹配: name[extras]==version, name>=version, name~=version 等
        pattern = re.compile(
            r'^(?P<name>[a-zA-Z0-9_\-\.]+)'
            r'(?:\[(?P<extras>[^\]]+)\])?'
            r'(?P<op>==|>=|<=|!=|~=|>|<)'
            r'(?P<version>[^\s;#]+)'
        )

        for line in content.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            # 移除行内注释
            if '#' in line:
                line = line.split('#', 1)[0].strip()

            match = pattern.match(line)
            if match:
                deps.append({
                    'name': match.group('name'),
                    'version': match.group('version'),
                    'operator': match.group('op'),
                    'extras': match.group('extras') or '',
                })
            elif line and not line.startswith('-'):
                # 没有版本号的依赖
                name = re.split(r'[\s<>=!~]', line)[0].strip()
                if name:
                    deps.append({
                        'name': name,
                        'version': '',
                        'operator': '',
                        'extras': '',
                    })

        return deps

    def parse_package_json(self, content: str) -> Dict[str, Any]:
        """
        解析 package.json

        Args:
            content: 文件内容

        Returns:
            解析后的字典
        """
        import json
        try:
            data = json.loads(content)
            return {
                'name': data.get('name', ''),
                'version': data.get('version', ''),
                'description': data.get('description', ''),
                'author': data.get('author', ''),
                'license': data.get('license', ''),
                'dependencies': data.get('dependencies', {}),
                'devDependencies': data.get('devDependencies', {}),
                'scripts': data.get('scripts', {}),
            }
        except Exception:
            return {}

    def parse_pyproject_toml(self, content: str) -> Dict[str, Any]:
        """
        解析 pyproject.toml（简化版，不依赖 toml 库）

        Args:
            content: 文件内容

        Returns:
            解析结果
        """
        result = {
            'project_name': '',
            'version': '',
            'dependencies': [],
            'optional_dependencies': {},
        }

        if not content:
            return result

        # 提取项目名
        name_match = re.search(r'^name\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
        if name_match:
            result['project_name'] = name_match.group(1)

        # 提取版本
        version_match = re.search(r'^version\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
        if version_match:
            result['version'] = version_match.group(1)

        # 提取依赖列表
        in_deps = False
        for line in content.split('\n'):
            stripped = line.strip()
            if stripped.startswith('dependencies'):
                in_deps = True
                continue
            if in_deps:
                if not stripped or (stripped.startswith('[') and not stripped.startswith('"')):
                    in_deps = False
                    continue
                # 简单解析 "包名>=1.0" 形式
                match = re.match(r'^["\']([^"\']+)["\']', stripped)
                if match:
                    result['dependencies'].append(match.group(1))

        return result

    # ============================================================
    # README 解析
    # ============================================================
    def extract_readme_sections(self, content: str) -> List[Dict[str, str]]:
        """
        提取 README 的章节

        Args:
            content: README 内容

        Returns:
            章节列表 [{'level': int, 'title': str, 'content': str}]
        """
        if not content:
            return []

        sections = []
        pattern = re.compile(r'^(#{1,6})\s+(.+?)$', re.MULTILINE)
        matches = list(pattern.finditer(content))

        for i, match in enumerate(matches):
            level = len(match.group(1))
            title = match.group(2).strip()
            start = match.end()

            # 章节内容到下一个标题为止
            if i + 1 < len(matches):
                end = matches[i + 1].start()
            else:
                end = len(content)

            section_content = content[start:end].strip()

            sections.append({
                'level': level,
                'title': title,
                'content': section_content,
            })

        return sections

    # ============================================================
    # 代码搜索/提取
    # ============================================================
    def extract_imports(self, content: str, language: str) -> List[str]:
        """
        提取 import 语句

        Args:
            content: 代码内容
            language: 编程语言

        Returns:
            导入列表
        """
        imports = []

        if language == 'Python':
            for match in re.finditer(r'^(?:from\s+(\S+)\s+)?import\s+(.+)$', content, re.MULTILINE):
                if match.group(1):
                    imports.append(match.group(1))
                else:
                    imports.extend(m.strip() for m in match.group(2).split(','))

        elif language in ('JavaScript', 'TypeScript'):
            for match in re.finditer(r'import\s+(?:.+?\s+from\s+)?["\']([^"\']+)["\']', content):
                imports.append(match.group(1))
            for match in re.finditer(r'require\s*\(\s*["\']([^"\']+)["\']\s*\)', content):
                imports.append(match.group(1))

        elif language == 'Go':
            for match in re.finditer(r'import\s+(?:\(\s*)?["\']([^"\']+)["\']', content):
                imports.append(match.group(1))

        elif language == 'Java':
            for match in re.finditer(r'import\s+([\w\.]+);', content):
                imports.append(match.group(1))

        return list(dict.fromkeys(imports))  # 去重保序

    def extract_functions(self, content: str, language: str) -> List[Dict[str, Any]]:
        """
        提取函数定义（简化版）

        Args:
            content: 代码内容
            language: 编程语言

        Returns:
            函数列表 [{'name': str, 'line': int}]
        """
        functions = []

        if language == 'Python':
            pattern = re.compile(r'^(\s*)def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', re.MULTILINE)
            for match in pattern.finditer(content):
                functions.append({
                    'name': match.group(2),
                    'line': content[:match.start()].count('\n') + 1,
                    'type': 'function',
                })
            # 类
            class_pattern = re.compile(r'^class\s+([a-zA-Z_][a-zA-Z0-9_]*)', re.MULTILINE)
            for match in class_pattern.finditer(content):
                functions.append({
                    'name': match.group(1),
                    'line': content[:match.start()].count('\n') + 1,
                    'type': 'class',
                })

        elif language in ('JavaScript', 'TypeScript'):
            pattern = re.compile(r'function\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', re.MULTILINE)
            for match in pattern.finditer(content):
                functions.append({
                    'name': match.group(1),
                    'line': content[:match.start()].count('\n') + 1,
                    'type': 'function',
                })
            # 箭头函数 const xxx = () =>
            arrow_pattern = re.compile(r'const\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(?:async\s*)?(?:\([^)]*\)\s*=>|\w+\s*=>)', re.MULTILINE)
            for match in arrow_pattern.finditer(content):
                functions.append({
                    'name': match.group(1),
                    'line': content[:match.start()].count('\n') + 1,
                    'type': 'arrow_function',
                })

        elif language == 'Java':
            pattern = re.compile(r'(?:public|private|protected)?\s*(?:static\s+)?[\w<>\[\]]+\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', re.MULTILINE)
            for match in pattern.finditer(content):
                name = match.group(1)
                if name not in ('if', 'while', 'for', 'switch'):
                    functions.append({
                        'name': name,
                        'line': content[:match.start()].count('\n') + 1,
                        'type': 'method',
                    })

        return functions

    # ============================================================
    # 工具方法
    # ============================================================
    def get_file_size_category(self, size_bytes: int) -> str:
        """
        文件大小分类

        Args:
            size_bytes: 字节数

        Returns:
            分类: tiny/small/medium/large/huge
        """
        if size_bytes < 1024:
            return 'tiny'
        elif size_bytes < 10 * 1024:
            return 'small'
        elif size_bytes < 100 * 1024:
            return 'medium'
        elif size_bytes < 1024 * 1024:
            return 'large'
        else:
            return 'huge'

    def is_text_file(self, file_path: str) -> bool:
        """
        简单判断文件是否为文本文件（基于后缀）

        Args:
            file_path: 文件路径

        Returns:
            是否为文本
        """
        text_extensions = set(EXTENSION_LANGUAGE_MAP.keys()) | DOCUMENT_EXTENSIONS | {
            '.txt', '.csv', '.log', '.env', '.gitignore', '.conf',
        }
        return Path(file_path).suffix.lower() in text_extensions

    def summarize_file(self, file_path: str, content: Optional[str] = None) -> Dict[str, Any]:
        """
        汇总文件信息（用于显示在 UI 上）

        Args:
            file_path: 文件路径
            content: 内容（可选）

        Returns:
            汇总信息
        """
        info = self.get_file_info(file_path, content)

        summary = {
            'path': info['path'],
            'name': info['name'],
            'language': info['language'] or 'Unknown',
            'size': info['size'],
            'size_category': self.get_file_size_category(info['size']),
            'lines': info['lines'],
            'type': 'code' if info['is_code'] else (
                'doc' if info['is_document'] else (
                'config' if info['is_config'] else (
                'image' if info['is_image'] else 'other'))),
        }

        # 对代码文件，额外提取函数/类
        if info['is_code'] and info['language'] and content:
            summary['functions'] = self.extract_functions(content, info['language'])
            summary['imports'] = self.extract_imports(content, info['language'])

        return summary