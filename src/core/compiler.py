import time
from core import scraping
from utils.logger import logger
from utils.validators import validate_compiled_content

class Compiler:
    
    @staticmethod
    def compile_pages(selected_links, delay=1.5, use_cache=False):
        compiled_data = {}
        
        if not selected_links or "links" not in selected_links:
            logger.info("No hay enlaces para compilar")
            return compiled_data
        
        total_links = len(selected_links["links"])
        logger.info(f"\nCompilando {total_links} paginas...")
        
        for i, link_info in enumerate(selected_links["links"], 1):
            url = link_info.get("url")
            page_type = link_info.get("type", "unknown")
            
            logger.info(f"[{i}/{total_links}] Descargando {page_type}: {url}")
            
            html = scraping.Web.get_data_with_cache(url, use_cache=use_cache)
            
            if html:
                [title, cleaned_text, links] = scraping.Web.clean_text(html)
                
                if len(cleaned_text) < 100:
                    logger.info(f"   Contenido insuficiente, intentando con navegador dinamico...")
                    html = scraping.Web.get_data_dynamic(url)
                    if html:
                        [title, cleaned_text, links] = scraping.Web.clean_text(html)
                        logger.info(f"   Contenido obtenido con navegador")
                
                if page_type not in compiled_data:
                    compiled_data[page_type] = []
                
                compiled_data[page_type].append({
                    "url": url,
                    "title": title,
                    "content": cleaned_text
                })
                
                logger.info(f"   Extraidos {len(cleaned_text)} caracteres")
            else:
                logger.info(f"   Error: No se pudo descargar")
            
            if i < total_links:
                time.sleep(delay)
        
        logger.info(f"\nCompilacion completada: {len(compiled_data)} tipos de paginas")
        return compiled_data
    
    @staticmethod
    def consolidate_by_type(compiled_data):
        consolidated = {}
        
        for page_type, pages in compiled_data.items():
            consolidated_text = ""
            
            for page in pages:
                consolidated_text += f"\n--- {page['url']} ---\n"
                consolidated_text += page['content']
                consolidated_text += "\n\n"
            
            consolidated[page_type] = consolidated_text.strip()
        
        return validate_compiled_content(consolidated)


def compile_links(selected_links, delay=1.5, use_cache=False):
    compiler = Compiler()
    compiled = compiler.compile_pages(selected_links, delay=delay, use_cache=use_cache)
    return compiler.consolidate_by_type(compiled)