import json
import sys
from urllib.parse import urljoin
from utils.api_openai import OpenAIClient
from utils.utils import get_prompts_path
from utils.logger import logger
from utils.validators import validate_selected_links

class LinkSelector:
    
    def __init__(self):
        self.openai_client = OpenAIClient()
    
    @staticmethod
    def load_prompt(prompt_filename):
        try:
            prompt_path = get_prompts_path(prompt_filename)
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logger.error(f"Error: No se encontro el archivo {prompt_path}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Error al leer el prompt: {e}")
            sys.exit(1)
    
    @staticmethod
    def load_json_prompts(prompt_filename):       
        prompt_path = get_prompts_path(prompt_filename)
        
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Convertir el contenido del assistant que está en formato JSON a string
                # para evitar que el LLM lo vea como un objeto y se confunda
                for message in data:
                    if message.get("role") == "assistant":
                        message["content"] = json.dumps(message["content"])
                        
                return data
        except Exception as e:
            logger.error(f"Error cargando prompts multi-shot desde {file_name}: {e}")
            return []
    
    @staticmethod
    def normalize_url(base_url, link):
        if link.startswith('http://') or link.startswith('https://'):
            return link
        
        return urljoin(base_url, link)
    
    @staticmethod
    def normalize_links(base_url, links):
        normalized = []
        for link in links:
            try:
                normalized_link = LinkSelector.normalize_url(base_url, link)
                if normalized_link and not normalized_link.startswith('#') and not normalized_link.startswith('javascript:'):
                    normalized.append(normalized_link)
            except Exception as e:
                logger.error(f"Error normalizando enlace '{link}': {e}")
                continue
        
        seen = set()
        unique_links = []
        for link in normalized:
            if link not in seen:
                seen.add(link)
                unique_links.append(link)
        
        return unique_links

    def select_relevant_links(self, base_url, links_list, model="gpt-4o-mini", max_tokens=2000):        
            normalized_links = self.normalize_links(base_url, links_list)
            
            if len(normalized_links) > 200:
                normalized_links = normalized_links[:200]
                logger.info(f"Advertencia: Se limitaron los enlaces a 200 para no exceder el contexto")
            
            system_prompt = self.load_prompt("link_system.md")
            
            messages = [
                        {"role": "system", "content": system_prompt}
                    ]            
            few_shots = self.load_json_prompts("link_multishot_prompts.json")         
            
            messages.extend(few_shots)                        
            
            user_message = f"""Sitio web base: {base_url} 
            Enlaces encontrados ({len(normalized_links)} total):{chr(10).join(f"- {link}" for link in normalized_links)}
            Selecciona los enlaces mas relevantes y devuelve el JSON.""" 
            
            messages.append({"role": "user", "content": user_message})
            
            logger.info(f"Analizando {len(normalized_links)} enlaces con {model}...")
            
            # Intentar hasta 3 veces si falla el parseo
            for attempt in range(1, 4):
                
                result = self.openai_client.call_openai(
                    messages=messages,
                    model=model,
                    max_tokens=max_tokens,
                    temperature=0.3
                )
                
                # Verificar si call_openai devolvió un error irrecuperable
                if result.get("response") == "Error irrecuperable":
                    logger.error("Error irrecuperable de la API en call_openai.")
                    return {"links": []}
                
                response_text = result["response"].strip()
                
                logger.info(f"Respuesta recibida (intento {attempt}/3). Tokens usados: {result['tokens']['total']}")
                
                try:
                    # Limpiar bloques de markdown
                    if response_text.startswith("```json"):
                        response_text = response_text.replace("```json", "").replace("```", "").strip()
                    elif response_text.startswith("```"):
                        response_text = response_text.replace("```", "").strip()
                    
                    # Intentar parsear JSON
                    parsed_result = json.loads(response_text)
                    
                    # Validar estructura
                    validated_result = validate_selected_links(parsed_result)
                    
                    if validated_result and validated_result.get("links"):
                        logger.info(f"Enlaces seleccionados: {len(validated_result['links'])}")
                        return validated_result
                    else:
                        raise ValueError("Validación retornó estructura vacía")
                    
                except (json.JSONDecodeError, ValueError) as e:
                    logger.warning(f"Intento {attempt}/3 falló: {e}")
                    
                    if attempt < 3:
                        # Añadir mensaje de corrección para el siguiente intento
                        messages.append({"role": "assistant", "content": response_text})
                        messages.append({
                            "role": "user", 
                            "content": f"""ERROR: Tu respuesta anterior no tiene el formato JSON correcto.

    IMPORTANTE: Debes responder ÚNICAMENTE con un objeto JSON válido con esta estructura exacta:
    {{
    "links": [
        {{"type": "about page", "url": "https://ejemplo.com/about"}},
        {{"type": "careers page", "url": "https://ejemplo.com/careers"}}
    ]
    }}

    NO incluyas texto adicional, explicaciones, ni bloques de código markdown.
    Intenta de nuevo con el formato correcto."""
                        })
                        logger.info(f"Reintentando con instrucciones de formato más estrictas...")
                    else:
                        # Último intento falló
                        logger.error(f"Todos los intentos fallaron. Respuesta recibida:\n{response_text[:500]}")
                        return {"links": []}


def select_links(base_url, links_list, model="gpt-4o-mini"):
    selector = LinkSelector()
    return selector.select_relevant_links(base_url, links_list, model=model)