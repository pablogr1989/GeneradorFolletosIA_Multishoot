import os
from datetime import datetime
import json
from utils.logger import logger

def get_project_root():
    current_file = os.path.abspath(__file__)
    utils_dir = os.path.dirname(current_file)      # src/utils/
    src_dir = os.path.dirname(utils_dir)           # src/
    project_root = os.path.dirname(src_dir)        # project root
    return project_root


def get_config_path(filename=".env"):
    return os.path.join(get_project_root(), "config", filename)


def get_prompts_path(filename):
    return os.path.join(get_project_root(), "prompts", filename)


def get_outputs_path(filename):
    return os.path.join(get_project_root(), "outputs", filename)


def get_data_path(filename):
    return os.path.join(get_project_root(), "data", filename)


def get_tests_path(filename):
    return os.path.join(get_project_root(), "tests", filename)

def save_json_with_timestamp(data, filename_prefix):    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = get_outputs_path(f"{timestamp}_{filename_prefix}.json")
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Resultado guardado en: {output_file}")
        return output_file
    except Exception as e:
        logger.info(f"No se pudo guardar el archivo: {e}")
        return None
    
def save_md_with_timestamp(data, filename_prefix):       
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    brochure_file = get_outputs_path(f"{timestamp}_{filename_prefix}.md")
    try:
        with open(brochure_file, 'w', encoding='utf-8', errors='replace') as f:
            f.write(data)
        logger.info(f"\nFolleto guardado en: {brochure_file}")
    except Exception as e:
        logger.info(f"No se pudo guardar el folleto: {e}")
        
def save_md(data, filename):      
    brochure_file = get_outputs_path(f"{filename}.md")
    try:
        with open(brochure_file, 'w', encoding='utf-8', errors='replace') as f:
            f.write(data)
        logger.info(f"\nFolleto guardado en: {brochure_file}")
        return brochure_file
    except Exception as e:
        logger.info(f"No se pudo guardar el folleto: {e}")
        return None


def display_selected_links(selected_links):
    logger.info("\n" + "=" * 60)
    logger.info("RESULTADOS")
    logger.info("=" * 60)
    
    if selected_links and selected_links.get("links"):
        logger.info(f"\nSe seleccionaron {len(selected_links['links'])} enlaces relevantes:\n")
        
        for i, link_info in enumerate(selected_links['links'], 1):
            logger.info(f"{i}. [{link_info['type'].upper()}]")
            logger.info(f"   {link_info['url']}\n")
    else:
        logger.info("\nNo se encontraron enlaces relevantes")
        
def display_consolidated_content(consolidated_content):
    logger.info("\n" + "=" * 60)
    logger.info("RESUMEN DE CONTENIDO COMPILADO")
    logger.info("=" * 60)
    
    for page_type, content in consolidated_content.items():
        logger.info(f"\n[{page_type.upper()}]: {len(content)} caracteres")