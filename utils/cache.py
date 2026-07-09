"""
AI GitHub Agent - 缓存管理器
"""
import os
import json
import hashlib
import time
from typing import Any, Optional, Callable
from pathlib import Path
import config


class CacheManager:
    """缓存管理器"""
    
    def __init__(self, cache_dir: Optional[str] = None, default_ttl: int = 3600):
        """
        初始化缓存管理器
        
        Args:
            cache_dir: 缓存目录
            default_ttl: 默认过期时间（秒）
        """
        self.cache_dir = Path(cache_dir or config.CACHE_DIR)
        self.default_ttl = default_ttl
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_cache_path(self, key: str) -> Path:
        """获取缓存文件路径"""
        # 对 key 进行哈希处理，确保文件名安全
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.json"
    
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存
        
        Args:
            key: 缓存键
            
        Returns:
            缓存值或 None
        """
        cache_path = self._get_cache_path(key)
        
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # 检查过期
            expires_at = cache_data.get('expires_at', 0)
            if expires_at and time.time() > expires_at:
                # 过期，删除缓存
                cache_path.unlink()
                return None
            
            return cache_data.get('value')
            
        except Exception as e:
            print(f"读取缓存失败: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        设置缓存
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒）
            
        Returns:
            是否成功
        """
        cache_path = self._get_cache_path(key)
        
        try:
            cache_data = {
                'key': key,
                'value': value,
                'created_at': time.time(),
                'expires_at': time.time() + (ttl or self.default_ttl)
            }
            
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2, default=str)
            
            return True
            
        except Exception as e:
            print(f"保存缓存失败: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        删除缓存
        
        Args:
            key: 缓存键
            
        Returns:
            是否成功
        """
        cache_path = self._get_cache_path(key)
        
        if cache_path.exists():
            try:
                cache_path.unlink()
                return True
            except Exception as e:
                print(f"删除缓存失败: {e}")
                return False
        
        return True
    
    def clear(self, pattern: Optional[str] = None) -> int:
        """
        清除缓存
        
        Args:
            pattern: 文件名模式（可选）
            
        Returns:
            清除的缓存数量
        """
        count = 0
        
        for cache_file in self.cache_dir.glob("*.json"):
            if pattern and pattern not in cache_file.name:
                continue
            
            try:
                cache_file.unlink()
                count += 1
            except Exception:
                pass
        
        return count
    
    def clear_expired(self) -> int:
        """
        清除过期缓存
        
        Returns:
            清除的缓存数量
        """
        count = 0
        current_time = time.time()
        
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                
                expires_at = cache_data.get('expires_at', 0)
                if expires_at and current_time > expires_at:
                    cache_file.unlink()
                    count += 1
                    
            except Exception:
                pass
        
        return count
    
    def get_cache_info(self, key: str) -> Optional[dict]:
        """
        获取缓存信息
        
        Args:
            key: 缓存键
            
        Returns:
            缓存信息
        """
        cache_path = self._get_cache_path(key)
        
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            current_time = time.time()
            expires_at = cache_data.get('expires_at', 0)
            
            return {
                'key': key,
                'created_at': cache_data.get('created_at'),
                'expires_at': expires_at,
                'ttl_remaining': max(0, expires_at - current_time) if expires_at else None,
                'size': cache_path.stat().st_size
            }
            
        except Exception:
            return None
    
    def list_caches(self) -> list:
        """
        列出所有缓存
        
        Returns:
            缓存列表
        """
        caches = []
        
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                
                current_time = time.time()
                expires_at = cache_data.get('expires_at', 0)
                
                caches.append({
                    'key': cache_data.get('key', ''),
                    'file': cache_file.name,
                    'created_at': cache_data.get('created_at'),
                    'expires_at': expires_at,
                    'is_expired': expires_at > 0 and current_time > expires_at,
                    'size': cache_file.stat().st_size
                })
                
            except Exception:
                pass
        
        return caches
    
    def get_or_compute(self, key: str, compute_fn: Callable[[], Any], ttl: Optional[int] = None) -> Any:
        """
        获取缓存或计算
        
        Args:
            key: 缓存键
            compute_fn: 计算函数
            ttl: 过期时间
            
        Returns:
            缓存值或计算结果
        """
        # 尝试获取缓存
        value = self.get(key)
        
        if value is not None:
            return value
        
        # 计算新值
        value = compute_fn()
        
        # 保存缓存
        self.set(key, value, ttl)
        
        return value
    
    def get_stats(self) -> dict:
        """
        获取缓存统计
        
        Returns:
            统计信息
        """
        total_size = 0
        total_count = 0
        expired_count = 0
        current_time = time.time()
        
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                total_count += 1
                total_size += cache_file.stat().st_size
                
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                
                expires_at = cache_data.get('expires_at', 0)
                if expires_at and current_time > expires_at:
                    expired_count += 1
                    
            except Exception:
                pass
        
        return {
            'total_count': total_count,
            'total_size': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'expired_count': expired_count,
            'active_count': total_count - expired_count
        }
