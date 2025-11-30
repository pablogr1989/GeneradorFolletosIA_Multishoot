import pytest
import os
from utils.cache_manager import CacheManager


class TestCacheManager:
    
    def test_get_cache_filename(self):
        url = "https://example.com/page"
        filename = CacheManager.get_cache_filename(url)
        
        assert filename.endswith(".html")
        assert len(filename) > 10  # Hash MD5
    
    def test_save_and_load_cache(self):
        test_url = "https://test-cache-example.com"
        test_content = "<html><body>Test Content</body></html>"
        
        CacheManager.save_to_cache(test_url, test_content)
        loaded = CacheManager.load_from_cache(test_url)
        
        assert loaded == test_content
    
    def test_cache_validity(self):
        test_url = "https://test-validity.com"
        test_content = "<html>Fresh content</html>"
        
        CacheManager.save_to_cache(test_url, test_content)
        
        # Recién guardado, debe ser válido
        assert CacheManager.is_cache_valid(test_url, max_age_hours=1)


class TestLanguageDetector:
    
    def test_detect_spanish(self):
        from utils.language_detector import detect_language
        
        text = "Hola, esta es una prueba en español. Necesitamos suficiente texto para detectar el idioma correctamente."
        lang = detect_language(text)
        
        assert lang == "es"
    
    def test_detect_english(self):
        from utils.language_detector import detect_language
        
        text = "Hello, this is a test in English. We need enough text to detect the language properly."
        lang = detect_language(text)
        
        assert lang == "en"
    
    def test_detect_short_text_defaults_english(self):
        from utils.language_detector import detect_language
        
        text = "Hi"
        lang = detect_language(text)
        
        assert lang == "en"