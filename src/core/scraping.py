import requests
from bs4 import BeautifulSoup
from utils.cache_manager import cache_manager
from playwright.sync_api import sync_playwright
from utils.logger import logger
from utils.robots_checker import robots_checker

class Web:
    
    @classmethod
    def get_data(cls, url):
        if not robots_checker.can_fetch(url):
            logger.error(f"Acceso bloqueado por robots.txt: {url}")
            return None
        
        try:
            headers = {'User-Agent': 'BrochureBot/1.0 (Educational Project)'}
            logger.info(f"Descargando: {url}")
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            logger.info(f"Descarga exitosa: {url}")
            return response.text
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al descargar {url}: {e}")
            return None    
        
    @classmethod
    def clean_text(cls, text):
        soup = BeautifulSoup(text, 'html.parser')
        links = [a.get('href') for a in soup.find_all('a', href=True)]
        title = soup.title.string if soup.title else "Sin título"
        # Eliminar contenido irrelevante
        for irrelevant in soup.body(["script", "style", "img", "input", "noscript", "svg", "footer", "nav", "aside"]):
            irrelevant.decompose()
        # Extraer texto plano
        text = soup.body.get_text(separator="\n", strip=True)
        # Recortar texto para no exceder el contexto del modelo
        text = text[:12000]
        return [title, text, links]
    
    @staticmethod
    def get_data_dynamic(url, timeout=30):
        try:              
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, timeout=timeout * 1000)
                page.wait_for_timeout(3000)
                content = page.content()
                browser.close()
                return content
                
        except ImportError:
            logger.error("Playwright no esta instalado. Usa: pip install playwright && playwright install chromium")
            return None
        except Exception as e:
            logger.error(f"Error con Playwright en {url}: {e}")
            return None
        
    @classmethod
    def get_data_with_cache(cls, url, use_cache=False, max_age_hours=12):        
        if use_cache and cache_manager.is_cache_valid(url, max_age_hours):
            cached = cache_manager.load_from_cache(url)
            if cached:
                return cached
        
        html = cls.get_data(url)
        
        if html:
            cache_manager.save_to_cache(url, html)
        
        return html