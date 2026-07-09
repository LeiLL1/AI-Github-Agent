"""
AI GitHub Agent - 文件解析器
"""
import re
from typing import Dict, List, Any, Optional
from pathlib import Path


class FileParser:
    """文件解析器"""
    
    def __init__(self):
        """初始化解析器"""
        self.parsers = {
            'python': self._parse_python,
            'javascript': self._parse_js,
            'typescript': self._parse_ts,
            'java': self._parse_java,
            'go': self._parse_go,
            'rust': self._parse_rust,
            'markdown': self._parse_markdown,
            'json': self._parse_json,
            'yaml': self._parse_yaml,
        }
    
    def parse(self, content: str, file_type: str) -> Dict[str, Any]:
        """
        解析文件内容
        
        Args:
            content: 文件内容
            file_type: 文件类型
            
        Returns:
            解析结果
        """
        parser = self.parsers.get(file_type.lower())
        
        if parser:
            return parser(content)
        
        return {'type': file_type, 'raw_content': content[:1000]}
    
    def get_file_type(self, filename: str) -> str:
        """
        获取文件类型
        
        Args:
            filename: 文件名
            
        Returns:
            文件类型
        """
        ext = Path(filename).suffix.lower().lstrip('.')
        
        type_mapping = {
            'py': 'python',
            'js': 'javascript',
            'jsx': 'javascript',
            'ts': 'typescript',
            'tsx': 'typescript',
            'java': 'java',
            'go': 'go',
            'rs': 'rust',
            'rb': 'ruby',
            'php': 'php',
            'c': 'c',
            'cpp': 'cpp',
            'h': 'c',
            'hpp': 'cpp',
            'cs': 'csharp',
            'swift': 'swift',
            'kt': 'kotlin',
            'scala': 'scala',
            'md': 'markdown',
            'json': 'json',
            'yaml': 'yaml',
            'yml': 'yaml',
            'toml': 'toml',
            'xml': 'xml',
            'html': 'html',
            'css': 'css',
            'scss': 'scss',
            'sql': 'sql',
            'sh': 'shell',
            'bash': 'shell',
            'zsh': 'shell',
            'ps1': 'powershell',
            'dockerfile': 'dockerfile',
        }
        
        return type_mapping.get(ext, ext)
    
    def _parse_python(self, content: str) -> Dict[str, Any]:
        """解析 Python 文件"""
        result = {
            'type': 'python',
            'imports': [],
            'classes': [],
            'functions': [],
            'docstring': '',
            'top_level_code': False
        }
        
        lines = content.split('\n')
        
        # 提取 docstring
        if lines:
            first_line = lines[0].strip()
            if first_line.startswith('"""') or first_line.startswith("'''"):
                # 找到 docstring 结尾
                quote = first_line[:3]
                if first_line.count(quote) >= 2:
                    result['docstring'] = first_line.strip(quote)
                else:
                    docstring_lines = [first_line.strip(quote)]
                    for line in lines[1:]:
                        if quote in line:
                            docstring_lines.append(line.split(quote)[0].strip())
                            break
                        docstring_lines.append(line.strip())
                    result['docstring'] = '\n'.join(docstring_lines)
        
        # 提取 imports
        import_patterns = [
            r'^(?:from\s+([\w.]+)\s+)?import\s+(.+)',
            r'^from\s+([\w.]+)\s+import\s+(.+)$'
        ]
        
        for line in lines:
            line = line.strip()
            for pattern in import_patterns:
                match = re.match(pattern, line)
                if match:
                    result['imports'].append(line)
                    break
        
        # 提取 classes
        class_pattern = r'^class\s+(\w+)(?:\([^)]*\))?:'
        for line in lines:
            match = re.search(class_pattern, line.strip())
            if match:
                result['classes'].append(match.group(1))
        
        # 提取 functions
        func_pattern = r'^(?:async\s+)?def\s+(\w+)\s*\('
        for line in lines:
            match = re.search(func_pattern, line.strip())
            if match:
                result['functions'].append(match.group(1))
        
        # 检查是否有顶层代码
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('#') and not stripped.startswith('"""') and not stripped.startswith("'''"):
                if not any(stripped.startswith(kw) for kw in ['import ', 'from ', 'class ', 'def ', 'async ']):
                    result['top_level_code'] = True
                    break
        
        return result
    
    def _parse_js(self, content: str) -> Dict[str, Any]:
        """解析 JavaScript 文件"""
        result = {
            'type': 'javascript',
            'imports': [],
            'exports': [],
            'functions': [],
            'classes': [],
            'react_components': []
        }
        
        lines = content.split('\n')
        
        # 提取 imports
        import_pattern = r'(?:import|require)\s*(?:\(?["\']([^"\']+)["\'])'
        for line in lines:
            match = re.search(import_pattern, line)
            if match:
                result['imports'].append(match.group(1))
        
        # 提取 exports
        export_pattern = r'export\s+(?:default\s+)?(?:const|let|var|function|class|async)\s+(\w+)'
        for line in lines:
            match = re.search(export_pattern, line)
            if match:
                result['exports'].append(match.group(1))
        
        # 提取 functions
        func_pattern = r'(?:function|const|let|var)\s+(\w+)\s*(?::\s*\w+\s*)?=\s*(?:async\s+)?(?:\([^)]*\)\s*)?(?:=>)?'
        for line in lines:
            match = re.search(func_pattern, line)
            if match:
                result['functions'].append(match.group(1))
        
        # 提取 classes
        class_pattern = r'class\s+(\w+)'
        for line in lines:
            match = re.search(class_pattern, line)
            if match:
                result['classes'].append(match.group(1))
                # 检查是否是 React 组件
                if match.group(1)[0].isupper():
                    result['react_components'].append(match.group(1))
        
        # 检查 React 组件
        component_pattern = r'(?:function|const)\s+([A-Z]\w+)\s*(?::\s*\w+\s*)?='
        for line in lines:
            match = re.search(component_pattern, line)
            if match:
                if match.group(1) not in result['react_components']:
                    result['react_components'].append(match.group(1))
        
        return result
    
    def _parse_ts(self, content: str) -> Dict[str, Any]:
        """解析 TypeScript 文件"""
        result = self._parse_js(content)
        result['type'] = 'typescript'
        
        lines = content.split('\n')
        
        # 提取 interfaces
        interface_pattern = r'interface\s+(\w+)'
        for line in lines:
            match = re.search(interface_pattern, line)
            if match:
                if 'interfaces' not in result:
                    result['interfaces'] = []
                result['interfaces'].append(match.group(1))
        
        # 提取 types
        type_pattern = r'type\s+(\w+)\s*='
        for line in lines:
            match = re.search(type_pattern, line)
            if match:
                if 'types' not in result:
                    result['types'] = []
                result['types'].append(match.group(1))
        
        # 提取 enums
        enum_pattern = r'enum\s+(\w+)'
        for line in lines:
            match = re.search(enum_pattern, line)
            if match:
                if 'enums' not in result:
                    result['enums'] = []
                result['enums'].append(match.group(1))
        
        return result
    
    def _parse_java(self, content: str) -> Dict[str, Any]:
        """解析 Java 文件"""
        result = {
            'type': 'java',
            'package': '',
            'imports': [],
            'classes': [],
            'interfaces': [],
            'methods': []
        }
        
        lines = content.split('\n')
        
        # 提取 package
        package_pattern = r'^package\s+([\w.]+);'
        for line in lines:
            match = re.search(package_pattern, line.strip())
            if match:
                result['package'] = match.group(1)
                break
        
        # 提取 imports
        import_pattern = r'^import\s+([\w.]+);'
        for line in lines:
            match = re.search(import_pattern, line.strip())
            if match:
                result['imports'].append(match.group(1))
        
        # 提取 classes
        class_pattern = r'(?:public|private|protected)?\s*(?:static)?\s*class\s+(\w+)'
        for line in lines:
            match = re.search(class_pattern, line.strip())
            if match:
                result['classes'].append(match.group(1))
        
        # 提取 interfaces
        interface_pattern = r'(?:public|private|protected)?\s*interface\s+(\w+)'
        for line in lines:
            match = re.search(interface_pattern, line.strip())
            if match:
                result['interfaces'].append(match.group(1))
        
        # 提取 methods
        method_pattern = r'(?:public|private|protected)?\s*(?:static)?\s*(?:\w+)\s+(\w+)\s*\('
        for line in lines:
            match = re.search(method_pattern, line.strip())
            if match:
                result['methods'].append(match.group(1))
        
        return result
    
    def _parse_go(self, content: str) -> Dict[str, Any]:
        """解析 Go 文件"""
        result = {
            'type': 'go',
            'package': '',
            'imports': [],
            'functions': [],
            'types': [],
            'interfaces': []
        }
        
        lines = content.split('\n')
        
        # 提取 package
        package_pattern = r'^package\s+(\w+)'
        for line in lines:
            match = re.search(package_pattern, line.strip())
            if match:
                result['package'] = match.group(1)
                break
        
        # 提取 imports
        in_import = False
        import_lines = []
        
        for line in lines:
            stripped = line.strip()
            if 'import' in stripped and not in_import:
                if '{' in stripped:
                    in_import = True
                    import_lines.append(stripped)
                elif stripped != 'import':
                    match = re.search(r'import\s+["\']([^"\']+)["\']', stripped)
                    if match:
                        result['imports'].append(match.group(1))
            elif in_import:
                import_lines.append(stripped)
                if '}' in stripped:
                    in_import = False
                    # 解析导入块
                    for imp_line in import_lines:
                        matches = re.findall(r'["\']([^"\']+)["\']', imp_line)
                        result['imports'].extend(matches)
        
        # 提取 functions
        func_pattern = r'func\s+(?:\([^)]+\)\s+)?(\w+)\s*\('
        for line in lines:
            match = re.search(func_pattern, line.strip())
            if match:
                result['functions'].append(match.group(1))
        
        # 提取 types
        type_pattern = r'type\s+(\w+)\s+(?:struct|interface)'
        for line in lines:
            match = re.search(type_pattern, line.strip())
            if match:
                result['types'].append(match.group(1))
        
        return result
    
    def _parse_rust(self, content: str) -> Dict[str, Any]:
        """解析 Rust 文件"""
        result = {
            'type': 'rust',
            'use_statements': [],
            'structs': [],
            'enums': [],
            'functions': [],
            'impl_blocks': []
        }
        
        lines = content.split('\n')
        
        # 提取 use 语句
        use_pattern = r'use\s+([\w:]+);?'
        for line in lines:
            match = re.search(use_pattern, line.strip())
            if match:
                result['use_statements'].append(match.group(1))
        
        # 提取 structs
        struct_pattern = r'struct\s+(\w+)'
        for line in lines:
            match = re.search(struct_pattern, line.strip())
            if match:
                result['structs'].append(match.group(1))
        
        # 提取 enums
        enum_pattern = r'enum\s+(\w+)'
        for line in lines:
            match = re.search(enum_pattern, line.strip())
            if match:
                result['enums'].append(match.group(1))
        
        # 提取 functions
        func_pattern = r'fn\s+(\w+)'
        for line in lines:
            match = re.search(func_pattern, line.strip())
            if match:
                result['functions'].append(match.group(1))
        
        # 提取 impl blocks
        impl_pattern = r'impl\s+(?:\w+\s+)?(?:for\s+)?(\w+)?'
        for line in lines:
            match = re.search(impl_pattern, line.strip())
            if match:
                target = match.group(1) or 'anonymous'
                result['impl_blocks'].append(target)
        
        return result
    
    def _parse_markdown(self, content: str) -> Dict[str, Any]:
        """解析 Markdown 文件"""
        result = {
            'type': 'markdown',
            'title': '',
            'headings': [],
            'code_blocks': [],
            'links': [],
            'images': []
        }
        
        lines = content.split('\n')
        
        # 提取标题
        title_pattern = r'^#\s+(.+)$'
        for line in lines:
            match = re.search(title_pattern, line.strip())
            if match:
                result['title'] = match.group(1).strip()
                break
        
        # 提取所有标题
        for line in lines:
            match = re.search(title_pattern, line.strip())
            if match:
                result['headings'].append(match.group(1).strip())
        
        # 提取代码块
        code_pattern = r'```(\w*)\n(.*?)```'
        matches = re.findall(code_pattern, content, re.DOTALL)
        for lang, code in matches:
            result['code_blocks'].append({
                'language': lang,
                'code': code.strip()
            })
        
        # 提取链接
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        for match in re.finditer(link_pattern, content):
            result['links'].append({
                'text': match.group(1),
                'url': match.group(2)
            })
        
        # 提取图片
        image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
        for match in re.finditer(image_pattern, content):
            result['images'].append({
                'alt': match.group(1),
                'url': match.group(2)
            })
        
        return result
    
    def _parse_json(self, content: str) -> Dict[str, Any]:
        """解析 JSON 文件"""
        import json
        
        result = {
            'type': 'json',
            'valid': True,
            'keys': []
        }
        
        try:
            data = json.loads(content)
            
            if isinstance(data, dict):
                result['keys'] = list(data.keys())
                result['root_type'] = 'object'
            elif isinstance(data, list):
                result['root_type'] = 'array'
                result['length'] = len(data)
                if data and isinstance(data[0], dict):
                    result['keys'] = list(data[0].keys()) if data[0] else []
            
            result['data'] = data
            
        except json.JSONDecodeError as e:
            result['valid'] = False
            result['error'] = str(e)
        
        return result
    
    def _parse_yaml(self, content: str) -> Dict[str, Any]:
        """解析 YAML 文件"""
        result = {
            'type': 'yaml',
            'valid': True,
            'keys': []
        }
        
        try:
            import yaml
            data = yaml.safe_load(content)
            
            if isinstance(data, dict):
                result['keys'] = list(data.keys())
            elif isinstance(data, list):
                result['is_array'] = True
                result['length'] = len(data)
            
            result['data'] = data
            
        except Exception as e:
            result['valid'] = False
            result['error'] = str(e)
        
        return result
