from langdetect import detect, DetectorFactory
from utils.logger import logger

# Seed fijo para resultados consistentes
DetectorFactory.seed = 0


def detect_language(text):
    try:
        if not text or len(text) < 50:
            logger.warning("Texto muy corto para detectar idioma, usando 'en' por defecto")
            return "en"
        
        # Tomar muestra del texto (primeros 1000 caracteres)
        sample = text[:1000]
        
        lang = detect(sample)
        logger.info(f"Idioma detectado: {lang}")
        return lang
        
    except Exception as e:
        logger.error(f"Error detectando idioma: {e}, usando 'en' por defecto")
        return "en"

def is_language_supported(language):
    return language in ['es', 'en', 'fr', 'de', 'it', 'pt', 'nl', 'ru', 'zh', 'ja', 'ko', 'ar']
    

def get_language_name(lang_code):
    languages = {
        'en': 'inglés',
        'es': 'español',
        'fr': 'francés',
        'de': 'alemán',
        'it': 'italiano',
        'pt': 'portugués',
        'nl': 'holandés',
        'ru': 'ruso',
        'zh-cn': 'chino',
        'ja': 'japonés',
        'ko': 'coreano',
        'ar': 'arabe'
    }
    return languages.get(lang_code, lang_code)

def get_language_list():
    language_options = {
        'Inglés': 'en',
        'Español': 'es',
        'Francés': 'fr',
        'Alemán': 'de',
        'Italiano': 'it',
        'Portugués': 'pt',
        'Holandés': 'nl',
        'Ruso': 'ru',
        'Chino': 'zh-cn',
        'Japonés': 'ja',
        'Coreano': 'ko',
        'Árabe': 'ar'
    }
    return language_options