import hashlib
import os
from datetime import datetime, timedelta
from utils.utils import get_data_path
from utils.logger import logger

class CacheManager:
    
    @staticmethod
    def get_cache_filename(url):
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return f"{url_hash}.html"
    
    @staticmethod
    def is_cache_valid(url, max_age_hours=12):
        cache_file = get_data_path(CacheManager.get_cache_filename(url))
        
        if not os.path.exists(cache_file):
            return False
        
        file_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
        age = datetime.now() - file_time
        
        return age < timedelta(hours=max_age_hours)
    
    @staticmethod
    def load_from_cache(url):
        cache_file = get_data_path(CacheManager.get_cache_filename(url))
        
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                logger.error(f"Error leyendo cache: {e}")
        
        return None
    
    @staticmethod
    def save_to_cache(url, html_content):
        cache_file = get_data_path(CacheManager.get_cache_filename(url))
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
        except Exception as e:
            logger.error(f"Error guardando en cache: {e}")
    
    @staticmethod
    def get_cache_age(url):
        cache_file = get_data_path(CacheManager.get_cache_filename(url))
        
        if not os.path.exists(cache_file):
            return None
        
        file_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
        age = datetime.now() - file_time
        
        hours = int(age.total_seconds() / 3600)
        minutes = int((age.total_seconds() % 3600) / 60)
        
        return f"{hours}h {minutes}m"


cache_manager = CacheManager()