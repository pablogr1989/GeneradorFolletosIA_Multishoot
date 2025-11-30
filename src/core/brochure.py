import re
import time
from datetime import datetime
from utils.api_openai import OpenAIClient
from utils.utils import get_prompts_path
from utils.language_detector import get_language_name
from utils.logger import logger
from utils.metrics import metrics_tracker

class BrochureGenerator:
    
    def __init__(self):
        self.openai_client = OpenAIClient()
    
    @staticmethod
    def load_prompt(prompt_filename):
        try:
            prompt_path = get_prompts_path(prompt_filename)
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logger.error(f"Error: No se encontro el archivo {prompt_filename}")
            return None
        except Exception as e:
            logger.error(f"Error al leer el prompt: {e}")
            return None
      
    def generate_brochure_normal(self, company_name, compiled_content, tone, model, max_tokens, language="en"):
        base_prompt = self.load_prompt("brochure_system.md")
        tone_prompt = self.load_prompt(f"tone_{tone}.md")
        
        if not compiled_content:
            logger.error("Contenido compilado vacio")
            return None
        
        if not base_prompt or not tone_prompt:
            logger.error("No hay prompt para hacer el folleto")
            return None
        
        system_prompt = base_prompt + "\n\n" + tone_prompt
        
        content_summary = ""
        for page_type, content in compiled_content.items():
            content_summary += f"\n\n## [{page_type.upper()}]\n{content[:8000]}\n"
        
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        lang_name = get_language_name(language)
        
        user_message = f"""Empresa: {company_name}
        
        IMPORTANTE: Genera el folleto en {lang_name}.

        Contenido extraido de las paginas web:
        {content_summary}

        Fecha actual: {current_date}

        Genera el folleto corporativo en Markdown."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        logger.info(f"\nGenerando folleto con {model}...")
        logger.info(f"Tono: {tone}")
        
        result = self.openai_client.call_openai(
            messages=messages,
            model=model,
            max_tokens=max_tokens,
            temperature=0.7
        )
        
        brochure_text = result["response"].strip()
        
        if brochure_text.startswith("```markdown"):
            brochure_text = brochure_text.replace("```markdown", "").replace("```", "").strip()
        elif brochure_text.startswith("```"):
            brochure_text = brochure_text.replace("```", "").strip()
        
        logger.info(f"Folleto generado. Tokens usados: {result['tokens']['total']}")
        
        return brochure_text
    
    def generate_brochure(self, company_name, compiled_content, tone="formal", model="gpt-4o-mini", max_tokens=4000, language="en"):
        if self.openai_client.mock_mode:
            if tone == "formal":
                start = time.time()
                text = self.generate_formal_brochure_mock(compiled_content)
                metrics_tracker.record_stage(f"Generar folleto formal offline", time.time() - start)
            else:
                start = time.time()
                text = self.generate_humorous_brochure_mock(compiled_content)     
                metrics_tracker.record_stage(f"Generar folleto humoristico offline", time.time() - start)       
        else:
            start = time.time()
            text = self.generate_brochure_normal(company_name, compiled_content, tone, model, max_tokens, language)
            metrics_tracker.record_stage(f"Generar folleto con IA", time.time() - start)   
        
        return text

    def extract_formal_info_from_compiled(self, compiled_content):
        # Estructura base por si faltan datos
        data = {
            "mision_en": "",
            "descripcion_en": "",
            "stats": {
                "modelos": "1M+",
                "datasets": "250k+",
                "orgs": "50,000",
                "apps": "Spaces" 
            },
            "empresas_destacadas": [],
            "cultura_headers": [],
            "areas_trabajo": [],
            "beneficios": []
        }

        # 1. PAGE: ABOUT (Estadísticas y Misión principal)
        about_text = compiled_content.get("about page", "")
        
        # Extraer Misión / Descripción corta (Líneas 3 y 4 del raw text en about page)
        # "The AI community building the future."
        # "The platform where the machine learning community collaborates..."
        lines_about = about_text.split('\n')
        if len(lines_about) > 3:
            data["descripcion_en"] = lines_about[3] # "The platform where..."

        # Extraer números exactos usando Regex simple porque están en el texto
        # "Browse 1M+ models"
        match_models = re.search(r"Browse ([\d\w\+]+) models", about_text)
        if match_models: data["stats"]["modelos"] = match_models.group(1)

        # "Browse 250k+ datasets"
        match_datasets = re.search(r"Browse ([\d\w\+]+) datasets", about_text)
        if match_datasets: data["stats"]["datasets"] = match_datasets.group(1)

        # "More than 50,000 organizations"
        match_orgs = re.search(r"More than ([\d\w\,]+) organizations", about_text)
        if match_orgs: data["stats"]["orgs"] = match_orgs.group(1)

        # 2. PAGE: CUSTOMERS (Lista de clientes)
        customers_text = compiled_content.get("customers page", "")
        # El PDF destaca: Google, Amazon, Microsoft, IBM, NVIDIA. 
        # Buscamos si existen en el texto del JSON para confirmarlos.
        target_clients = ["Google", "Amazon", "Microsoft", "IBM", "NVIDIA"]
        for client in target_clients:
            if client in customers_text or client in about_text:
                data["empresas_destacadas"].append(client)

        # 3. PAGE: CAREERS (Misión, Cultura, Áreas y Beneficios)
        careers_text = compiled_content.get("careers page", "")

        # Misión exacta: "Our mission is to democratize good machine learning."
        match_mission = re.search(r"mission is to (.*?)\.", careers_text)
        if match_mission: 
            data["mision_en"] = f"to {match_mission.group(1)}"

        # Áreas de trabajo (Headers detectados en el texto "open jobs")
        # En el JSON aparecen como "Product\n2 open jobs", "Sales\n1 open job", etc.
        # Extraemos las palabras clave
        keywords_areas = ["Engineering", "Research", "Sales", "Customer Success", "Science"]
        for area in keywords_areas:
            if area in careers_text:
                data["areas_trabajo"].append(area)

        # Beneficios (Listados bajo "Perks & Benefits")
        keywords_benefits = ["Flexible Work", "Health Insurance", "Equity", "Parental Leave"]
        for ben in keywords_benefits:
            if ben in careers_text:
                data["beneficios"].append(ben)
                
        # Cultura (Headers bajo "Our Culture")
        # El JSON tiene frases como "We value development", "We care about your well-being".
        # Mapeamos a lo que extraemos
        if "diversity" in careers_text: data["cultura_headers"].append("Diversity & Inclusion")
        if "development" in careers_text: data["cultura_headers"].append("Professional Development")
        if "well-being" in careers_text: data["cultura_headers"].append("Well-being")
        if "collaboration" in careers_text or "community" in careers_text: data["cultura_headers"].append("Collaboration")

        return data

    def generate_formal_brochure_mock(self, compiled_content):
        
        data = self.extract_formal_info_from_compiled(compiled_content)        
        
        
        texto = f"""# Hugging Face
## The AI community building the future.

### ¿Qué hacemos?
En **Hugging Face**, nuestra misión es: "{data['mision_en']}".
{data['descripcion_en']}

### Productos/Servicios
- **Modelos de IA**: Acceso a más de {data['stats']['modelos']} de modelos.
- **Conjuntos de Datos**: Una colección de más de {data['stats']['datasets']} conjuntos de datos.
- **Aplicaciones de IA**: Herramientas para construir demos y aplicaciones (Spaces).
- **Soluciones Empresariales**: Seguridad de nivel empresarial y soporte dedicado (Enterprise Hub).

### Para quién
Servimos a una amplia variedad de industrias y sectores, incluyendo:
- Tecnología
- Educación
- Salud
- Finanzas
- Investigación

### Casos de éxito o Clientes destacados
Más de **{data['stats']['orgs']} organizaciones** utilizan la plataforma de Hugging Face, incluyendo nombres destacados como:\n"""
        # Lista de clientes
        texto += "\n"
        for empresa in data['empresas_destacadas']:
            texto += f"- **{empresa}** \n"

        texto += """
### Cultura y Valores\n"""
        # Lista de cultura (simulando los párrafos del original con los headers extraídos)
        for valor in data['cultura_headers']:
            texto += f"- **{valor}** \n"

        texto += """
### Únete a nosotros
Estamos en constante búsqueda de talento diverso. Ofrecemos oportunidades en áreas como:\n"""
        # Lista de áreas
        for area in data['areas_trabajo']:
            texto += f"- {area}\n"

        texto += "\n**Beneficios para empleados** incluyen:\n"
        for beneficio in data['beneficios']:
            texto += f"- {beneficio}\n"

        texto += """
### Contacto
Para más información, visita nuestra [página web](https://huggingface.co/) o contáctanos.

### Nota legal
Contenido generado a partir de fuentes públicas el 2025-11-26. Verificar antes de uso externo.\n"""
        return texto

    def extract_humorous_info_from_compiled(self, compiled_content):
        data = {
            "stats": {
                "modelos": "1M+",  # Valor por defecto seguro
                "datasets": "250k+"
            },
            "empresas_detectadas": [], # Para validar qué empresas poner en Casos de Éxito
            "beneficios_detectados": []
        }

        # 1. Extracción de Estadísticas (About Page)
        about_text = compiled_content.get("about page", "")
        
        # Regex para capturar los números reales del momento
        match_models = re.search(r"Browse ([\d\w\+]+) models", about_text)
        if match_models: 
            data["stats"]["modelos"] = match_models.group(1)

        match_datasets = re.search(r"Browse ([\d\w\+]+) datasets", about_text)
        if match_datasets: 
            data["stats"]["datasets"] = match_datasets.group(1)

        # 2. Validación de Empresas (Customers Page & About Page)
        # El folleto creativo menciona específicamente a estas 4.
        # Las buscamos en el JSON para confirmar que podemos incluirlas.
        customers_text = compiled_content.get("customers page", "")
        combined_text = about_text + customers_text
        
        target_companies = ["NVIDIA", "Meta", "Amazon", "Google"]
        for company in target_companies:
            # Buscamos "AI at Meta" o "Meta"
            if company in combined_text or (company == "Meta" and "AI at Meta" in combined_text):
                data["empresas_detectadas"].append(company)

        # 3. Validación de Beneficios (Careers Page)
        # Para asegurar que la sección "Únete a nosotros" tiene base real
        careers_text = compiled_content.get("careers page", "")
        if "Flexible Work" in careers_text: data["beneficios_detectados"].append("flexibilidad")
        if "Unlimited PTO" in careers_text: data["beneficios_detectados"].append("tiempo libre")
        
        return data

    def generate_humorous_brochure_mock(self, compiled_content):     
        
        data = self.extract_humorous_info_from_compiled(compiled_content)
                
        seccion_clientes = ""
        if "NVIDIA" in data["empresas_detectadas"]:
            seccion_clientes += "- **NVIDIA**: Con más de 585 modelos en nuestra plataforma.\n"
        if "Meta" in data["empresas_detectadas"]:
            seccion_clientes += "- **AI at Meta**: Utilizan nuestros recursos para impulsar su innovación.\n"
    
        # Agrupamos Amazon y Google si ambos están presentes (como en el PDF objetivo)
        otros_gigantes = [empresa for empresa in ["Amazon", "Google"] if empresa in data["empresas_detectadas"]]
        if len(otros_gigantes) > 0:
            nombres = " y ".join(otros_gigantes)
            seccion_clientes += f"- **{nombres}**: También han encontrado su lugar en nuestra comunidad.\n"

        # Plantilla de Texto con f-strings
        # Aquí es donde reside la "personalidad" del folleto (los emojis y chistes)
        texto = f"""# Hugging Face
## La comunidad de IA que está construyendo el futuro. 🤗

### ¿Qué hacemos?
En Hugging Face, nuestra misión es democratizar el aprendizaje automático (ML) y hacer que la inteligencia artificial (IA) sea tan accesible como un café en la esquina. Creamos una plataforma donde la comunidad de ML colabora en modelos, conjuntos de datos y aplicaciones, como si estuviéramos todos en una gran fiesta de algoritmos. 🎉 ¡Ven a explorar, crear y descubrir!

### Productos/Servicios
- **Modelos de IA**: Más de {data['stats']['modelos']} de modelos, desde generación de texto hasta imágenes, para que encuentres el que mejor se adapte a tus necesidades.
- **Conjuntos de Datos**: Accede a más de {data['stats']['datasets']} conjuntos de datos para cualquier tarea de ML. ¡Es como un buffet libre, pero de datos! 🍽️
- **Espacios**: Aplicaciones interactivas donde puedes experimentar con modelos de IA en tiempo real. ¡Más divertido que un parque de atracciones! 🎢
- **Soluciones Empresariales**: Opciones avanzadas para organizaciones que buscan escalar su IA con seguridad y soporte dedicado. ¡Porque la IA también necesita un lugar seguro para jugar! 🏰

### Para quién
Servimos a una amplia gama de industrias, desde tecnología hasta salud, educación y entretenimiento. Nuestros clientes incluyen desde startups curiosas hasta gigantes como Google, Microsoft y Amazon. Si buscas una solución de IA, ¡estás en el lugar correcto!

### Casos de éxito o Clientes destacados
{seccion_clientes}
### Cultura y Valores
- **Diversidad e Inclusión**: Creemos que todas las voces cuentan, como en un coro donde cada nota es importante. 🎶
- **Desarrollo Continuo**: Ofrecemos reembolsos para conferencias y formación. ¡Nunca dejes de aprender!
- **Bienestar**: Flexibilidad en horarios y opciones de trabajo híbrido. ¡Porque la vida es más que solo trabajo!
- **Equidad**: Todos los empleados son accionistas y comparten el éxito de la empresa. ¡Juntos somos más fuertes! 💪

### Únete a nosotros
¿Te gustaría ser parte de nuestro equipo? Actualmente estamos buscando personas apasionadas en diversas áreas, desde ingeniería de ML hasta ventas. Ofrecemos beneficios como horarios flexibles, tiempo libre ilimitado y la oportunidad de trabajar con algunos de los mejores en la industria. ¡Haz clic en [ver empleos](https://apply.workable.com/huggingface/) para unirte a la diversión!

### Contacto
¡Estamos aquí para ayudarte! Si tienes preguntas o quieres saber más sobre nuestras soluciones, no dudes en ponerte en contacto. Visítanos en [Hugging Face](https://huggingface.co) o envíanos un correo a **contact@huggingface.co**. ¡Esperamos verte pronto! 👋

### Nota legal
Contenido generado a partir de fuentes públicas el 2025-11-26. Verificar antes de uso externo.
"""
        return texto

def generate_brochure(company_name, compiled_content, tone="formal", model="gpt-4o-mini", language = 'en'):
    generator = BrochureGenerator()
    return generator.generate_brochure(company_name, compiled_content, tone=tone, model=model, language=language)