from pydantic import BaseModel, Field, ValidationError
from typing import List
from utils.logger import logger


class SelectedLink(BaseModel):
    type: str = Field(..., description="Tipo de enlace (ej: about, careers)")
    url: str = Field(..., description="URL del enlace")
    score: int = Field(..., description="Puntuación de relevancia (0-100)", ge=0, le=100)
    rationale: str = Field(..., description="Justificación breve de por qué es relevante")

class SelectedLinksResponse(BaseModel):
    links: List[SelectedLink] = Field(default_factory=list, description="Lista de enlaces seleccionados")
    
class CompiledPage(BaseModel):
    url: str = Field(..., description="URL de la pagina")
    title: str = Field(default="", description="Titulo de la pagina")
    content: str = Field(..., description="Contenido de la pagina")


class CompiledContentResponse(BaseModel):
    pages: dict = Field(default_factory=dict, description="Contenido compilado por tipo de pagina")


def validate_selected_links(data):
    try:
        validated = SelectedLinksResponse(**data)
        logger.info(f"JSON validado correctamente: {len(validated.links)} enlaces")
        return validated.model_dump()
    except ValidationError as e:
        logger.error(f"Error de validacion JSON: {e}")
        logger.warning("Intentando recuperar datos parciales...")
        
        if isinstance(data, dict) and "links" in data:
            valid_links = []
            for link in data["links"]:
                if isinstance(link, dict) and "type" in link and "url" in link:
                    link_data = {
                        "type": link["type"],
                        "url": link["url"],
                        "score": link.get("score", 0),
                        "rationale": link.get("rationale", "Faltante")
                    }
                    valid_links.append(link_data)
            
            if valid_links:
                logger.info(f"Recuperados {len(valid_links)} enlaces validos con valores de score/rationale por defecto.")
                return {"links": valid_links}
        
        logger.error("No se pudo recuperar ningun enlace valido")
        return {"links": []}


def validate_compiled_content(data):
    try:
        if not isinstance(data, dict):
            logger.error("Compiled content no es un diccionario")
            return {}
        
        validated = {}
        for page_type, content in data.items():
            if isinstance(content, str) and len(content) > 0:
                validated[page_type] = content
                logger.debug(f"Validado {page_type}: {len(content)} caracteres")
            else:
                logger.warning(f"Contenido invalido para {page_type}")
        
        logger.info(f"Compiled content validado: {len(validated)} tipos de pagina")
        return validated
        
    except Exception as e:
        logger.error(f"Error validando compiled content: {e}")
        return {}