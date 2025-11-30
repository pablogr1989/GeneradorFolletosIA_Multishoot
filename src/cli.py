import sys
import time
from datetime import datetime
from core import scraping, link_selector, compiler, brochure
from utils.utils import *
from utils.args_manager import args_manager
from utils.cache_manager import cache_manager
from utils.api_openai import OpenAIClient
from utils.mock_responses import get_mock_compiled_content
from utils.logger import logger
from utils.language_detector import *
from utils.exporters import markdown_to_html, markdown_to_pdf
from utils.metrics import metrics_tracker

def download_html(test_url):
    logger.info("- PASO 1: Descargando página web...")
    use_cache_decision = None

    # Verificar si hay cache y preguntar
    if cache_manager.is_cache_valid(test_url):
        age = cache_manager.get_cache_age(test_url)
        logger.info(f"\nSe encontro cache disponible (edad: {age})")
        response = input("Usar cache para esta sesion? (s/n): ").lower().strip()
        use_cache_decision = (response == 's')
    else:
        use_cache_decision = False

    web_content = scraping.Web.get_data_with_cache(test_url, use_cache=use_cache_decision)
    return web_content, use_cache_decision

def extract_and_clean_links(web_content):
    logger.info("\n- PASO 2: Extrayendo enlaces y limpiando contenido...")
    [web_title, web_text, web_links] = scraping.Web.clean_text(web_content)  
    
    detected_lang = detect_language(web_text)
    lang_name = get_language_name(detected_lang)
    logger.info(f"Idioma de la web: {lang_name}")    
    return web_links, detected_lang

def get_relevant_links(test_url, web_links):
    logger.info(f"\n- PASO 3: Seleccionando enlaces relevantes con IA...")
    selector = link_selector.LinkSelector()
    selected_links = selector.select_relevant_links(test_url, web_links)    
    
    if not selected_links or not selected_links.get("links"):
        logger.error("\nNo se encontraron enlaces relevantes")
        sys.exit(1)
        
    display_selected_links(selected_links)
    save_json_with_timestamp(selected_links, "selected_links")    
    return selected_links
    

def run_normal_mode(test_url):    
    #########################################################################
    #                         PASO 1 - DESCARGAR HTML                       #
    #########################################################################
    start = time.time()
    web_content, use_cache_decision = download_html(test_url)
    metrics_tracker.record_stage("Scraping inicial", time.time() - start)
    #########################################################################
    #                        PASO 2 - LIMPIAR Y EXTRAER                     #
    #########################################################################
    start = time.time()
    web_links, detected_lang = extract_and_clean_links(web_content)
    metrics_tracker.record_stage("Limpiar y extraer links", time.time() - start)
    #########################################################################
    #                   PASO 3 - SELECCIONAR ENLACES CON IA                 #
    #########################################################################
    start = time.time()
    selected_links = get_relevant_links(test_url, web_links)
    metrics_tracker.record_stage("Seleccion de enlaces con IA", time.time() - start)

    #########################################################################
    #                PASO 4 - EXTRAER CONTENIDO DE ENLANCES                 #
    #########################################################################
    start = time.time()
    logger.info(f"\nPASO 4: Compilando contenido de paginas seleccionadas...")
    consolidated_content = compiler.compile_links(selected_links, delay=1.5, use_cache=use_cache_decision)    
    save_json_with_timestamp(consolidated_content, "compiled_content")    
    metrics_tracker.record_stage("Extraer y compilar contenido", time.time() - start)
    
    return consolidated_content, detected_lang


def run_mock_mode(tone):
    #########################################################################
    #                 PASO 1 - CARGANDO CONTENIDO OFFLINE                   #
    #########################################################################
    start = time.time()
    logger.info(f"MODO MOCK: Cargando datos offline (tono: {tone})")
    consolidated_content = get_mock_compiled_content(tone)
    metrics_tracker.record_stage("Carga de contenido offline", time.time() - start)
    
    if not consolidated_content:
        logger.error("Error: No se pudo cargar contenido mock")
        sys.exit(1)
    
    return consolidated_content

def write_brochure(brochure_content, formats, suffix=""):
    start = time.time()
    if brochure_content:
        filename = f"brochure{suffix}"
        save_md_with_timestamp(brochure_content, filename)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if 'html' in formats:            
            markdown_to_html(brochure_content, f"{timestamp}_{filename}.html")
        
        if 'pdf' in formats:            
            markdown_to_pdf(brochure_content, f"{timestamp}_{filename}.html", f"{timestamp}_{filename}.pdf")
    else:
        logger.error(f"Error al generar el folleto {suffix}")
    metrics_tracker.record_stage(f"Exportar folleto {suffix}", time.time() - start)

def run_generate_brochure(company_name, consolidated_content, tone, detected_lang, target_language, formats):    
    #########################################################################
    #                 PASO 5 - GENERAR FOLLETO CORPORATIVO                  #
    #########################################################################
    logger.info(f"\nPASO 5: Generando folleto corporativo (Origen: {detected_lang})...")
    brochure_content = brochure.generate_brochure(
        company_name=company_name,
        compiled_content=consolidated_content,
        tone=tone,
        model="gpt-4o-mini",
        language=detected_lang # Generamos en el idioma fuente primero
    )
    
    # Guardar original
    write_brochure(brochure_content, formats, suffix="_original")

    #########################################################################
    #                 PASO 6 - TRADUCCIÓN AUTOMÁTICA             #
    #########################################################################
    # Si el idioma destino es diferente al origen, traducimos
    if brochure_content and target_language != detected_lang:
        logger.info(f"\nPASO 6: Traduciendo folleto a {target_language}...")
        translated_content = brochure.translate_brochure(
            brochure_text=brochure_content,
            target_language=target_language,
            model="gpt-4o-mini"
        )
        # Guardar traducido
        write_brochure(translated_content, formats, suffix=f"_{target_language}")
    else:
        logger.info(f"\nPASO 6: Omitiendo traducción debido a que el idioma de la web es la misma que el lenguaje introducido")
    

def main():
    metrics_tracker.start()
    args_manager.parse_args()
    openai_client = OpenAIClient()
    
    company_name = args_manager.get('company')
    test_url = args_manager.get('url')
    tone = args_manager.get('tone')
    formats = args_manager.get('format')
    target_language = args_manager.get('language')
    
    if not target_language:
        target_language = "es"  # Idioma por defecto
        logger.info(f"Nota: No se especificó idioma destino (--language). Usando '{target_language}' por defecto.")
        
    if not test_url:
        test_url = "https://huggingface.co"
        logger.info(f"Nota: No se especificó url en los argumentos, utilizando url por defecto {test_url}")
        
    logger.info("=" * 60)
    logger.info("GENERADOR DE FOLLETOS CORPORATIVOS CON IA")
    logger.info("=" * 60)
    logger.info(f"\nEmpresa: {company_name}")
    logger.info(f"URL a analizar: {test_url}")
    logger.info(f"Tono: {tone}")
    logger.info(f"Idioma destino: {target_language}\n")
    
    if openai_client.mock_mode:
        consolidated_content = run_mock_mode(tone)
        detected_lang = "en" # Asumimos inglés para el mock
    else:
        consolidated_content, detected_lang = run_normal_mode(test_url)       
        
    if not consolidated_content:
        logger.error("No se pudo obtener contenido compilado")
        sys.exit(1)
    
    # Llamamos al flujo de generación y traducción
    run_generate_brochure(company_name, consolidated_content, tone, detected_lang, target_language, formats)       
    
    logger.info("\n" + "=" * 60)
    logger.info("Proceso completado")
    logger.info("=" * 60)
    metrics_tracker.print_summary()
        

if __name__ == "__main__":
    main()