import os
import sys
from openai import OpenAI, APIError, APIConnectionError, RateLimitError, AuthenticationError
from dotenv import load_dotenv
from utils.utils import get_config_path
from utils.logger import logger
from utils.metrics import metrics_tracker

class OpenAIClient:
    
    def __init__(self):
        try:
            load_dotenv(get_config_path())
        except Exception as e:
            logger.error(f"Error al cargar el archivo .env: {e}")
            sys.exit(1)
        
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.mock_mode = not self.api_key or self.api_key.strip() == ""
        
        if self.mock_mode:
            logger.info("\n*** MODO MOCK ACTIVADO (sin API key) ***\n")
            self.client = None
        else:
            try:
                self.client = OpenAI(api_key=self.api_key, timeout=90.0)
            except Exception as e:
                logger.error(f"Error al inicializar el cliente de OpenAI: {e}")
                sys.exit(1)
    
    def call_openai(self, messages, model="gpt-4o-mini", max_tokens=1000, temperature=0.7):
        try:    
            completion = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )            
            response_text = completion.choices[0].message.content

            metrics_tracker.add_tokens(
                model,
                completion.usage.prompt_tokens,
                completion.usage.completion_tokens
            )
            
            return {
                "response": response_text,
                "model": completion.model,
                "tokens": {
                    "total": completion.usage.total_tokens,
                    "prompt": completion.usage.prompt_tokens,
                    "completion": completion.usage.completion_tokens
                }
            }
            
        except AuthenticationError as e:
            logger.error(f"Error de autenticacion: API key invalida o incorrecta")
            logger.error(f"   Detalles: {e}")
            sys.exit(1)
        
        except RateLimitError as e:
            logger.error(f"Error: Has excedido tu limite de uso o cuota")
            logger.error(f"   Detalles: {e}")
            sys.exit(1)
            
        except APIConnectionError as e:
            logger.error(f"Error de conexion: No se pudo conectar con OpenAI")
            logger.error(f"   Verifica tu conexion a internet")
            logger.error(f"   Detalles: {e}")
            sys.exit(1)
            
        except APIError as e:
            logger.error(f"Error de la API de OpenAI:")
            logger.error(f"   Codigo: {e.status_code if hasattr(e, 'status_code') else 'N/A'}")
            logger.error(f"   Mensaje: {e}")
            sys.exit(1)
            
        except Exception as e:
            logger.error(f"Error inesperado: {e}")
            logger.error(f"   Tipo de error: {type(e).__name__}")
            sys.exit(1)