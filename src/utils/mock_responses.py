import json
import os
from utils.logger import logger

def get_mock_compiled_content(tone="formal"):
    offline_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "offline",
        f"mock_compiled_{tone}_content.json"
    )
    
    try:
        with open(offline_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Error: No se encontro offline/mock_compiled_{tone}_content.json")
        logger.error("Ejecuta primero con API key para generar datos mock")
        return {}
    except Exception as e:
        logger.error(f"Error cargando mock data: {e}")
        return {}