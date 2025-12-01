import re
import time
from datetime import datetime
from utils.api_openai import OpenAIClient
from utils.utils import get_prompts_path
from utils.language_detector import get_language_name
from utils.logger import logger
from utils.metrics import metrics_tracker

# Constante de secciones fijas requerida por la Tarea 8
SECTIONS = [
    "Resumen", 
    "Propuesta de valor", 
    "Productos/Servicios", 
    "Clientes", 
    "Cultura", 
    "Carreras", 
    "Contacto"
]

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
        
        # Generar lista de secciones para el prompt
        sections_list = chr(10).join(f"- {s}" for s in SECTIONS)
        
        user_message = f"""Empresa: {company_name}
        
        IMPORTANTE: Genera el folleto en {lang_name}.

        El folleto DEBE usar exactamente estos encabezados conceptuales, **TRADUCIDOS AL IDIOMA {lang_name}** y formateados como Markdown (##):
        {sections_list}

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

    def translate_brochure(self, brochure_text, target_language="es", model="gpt-4o-mini"):
        if self.openai_client.mock_mode:
            logger.info("MODO MOCK: Saltando traducción real")
            return f"{brochure_text}\n\n[TRADUCCION SIMULADA A {target_language.upper()}]"
        
        system_prompt = self.load_prompt("translator_system.md")
        # Fallback simple si no existe el archivo
        if not system_prompt:
             system_prompt = "Eres un traductor experto. Traduce el contenido manteniendo el formato Markdown."

        lang_name = get_language_name(target_language)
        
        user_message = f"""Traduce el siguiente folleto Markdown al idioma: {lang_name}.
        Recuerda preservar estrictamente el formato.
        
        FOLLETO ORIGINAL:
        {brochure_text}"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        logger.info(f"\nTraduciendo folleto a {lang_name} con {model}...")
        
        start = time.time()
        result = self.openai_client.call_openai(
            messages=messages,
            model=model,
            max_tokens=4000,
            temperature=0.3 # Temperatura baja para ser fiel al original
        )
        metrics_tracker.record_stage(f"Traduccion ({target_language})", time.time() - start)
        
        translated_text = result["response"].strip()
        
        if translated_text.startswith("```markdown"):
            translated_text = translated_text.replace("```markdown", "").replace("```", "").strip()
        elif translated_text.startswith("```"):
            translated_text = translated_text.replace("```", "").strip()
            
        logger.info(f"Traducción completada. Tokens usados: {result['tokens']['total']}")
        return translated_text

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

        # 1. PAGE: ABOUT
        about_text = compiled_content.get("about page", "")
        lines_about = about_text.split('\n')
        if len(lines_about) > 3:
            data["descripcion_en"] = lines_about[3]

        match_models = re.search(r"Browse ([\d\w\+]+) models", about_text)
        if match_models: data["stats"]["modelos"] = match_models.group(1)

        match_datasets = re.search(r"Browse ([\d\w\+]+) datasets", about_text)
        if match_datasets: data["stats"]["datasets"] = match_datasets.group(1)

        match_orgs = re.search(r"More than ([\d\w\,]+) organizations", about_text)
        if match_orgs: data["stats"]["orgs"] = match_orgs.group(1)

        # 2. PAGE: CUSTOMERS
        customers_text = compiled_content.get("customers page", "")
        target_clients = ["Google", "Amazon", "Microsoft", "IBM", "NVIDIA"]
        for client in target_clients:
            if client in customers_text or client in about_text:
                data["empresas_destacadas"].append(client)

        # 3. PAGE: CAREERS
        careers_text = compiled_content.get("careers page", "")
        match_mission = re.search(r"mission is to (.*?)\.", careers_text)
        if match_mission: 
            data["mision_en"] = f"to {match_mission.group(1)}"

        keywords_areas = ["Engineering", "Research", "Sales", "Customer Success", "Science"]
        for area in keywords_areas:
            if area in careers_text:
                data["areas_trabajo"].append(area)

        keywords_benefits = ["Flexible Work", "Health Insurance", "Equity", "Parental Leave"]
        for ben in keywords_benefits:
            if ben in careers_text:
                data["beneficios"].append(ben)
                
        if "diversity" in careers_text: data["cultura_headers"].append("Diversity & Inclusion")
        if "development" in careers_text: data["cultura_headers"].append("Professional Development")
        if "well-being" in careers_text: data["cultura_headers"].append("Well-being")
        if "collaboration" in careers_text or "community" in careers_text: data["cultura_headers"].append("Collaboration")

        return data

    def generate_formal_brochure_mock(self, compiled_content):
        data = self.extract_formal_info_from_compiled(compiled_content)        
        
        texto = f"""# Hugging Face
## The AI community building the future.

### Summary
At **Hugging Face**, our mission is: "{data['mision_en']}".
{data['descripcion_en']}

### Value Proposition
We are the leading platform where the machine learning community collaborates on models, datasets, and applications.

### Products/Services
- **AI Models**: Access to over {data['stats']['modelos']} models.
- **Datasets**: A collection of over {data['stats']['datasets']} datasets.
- **AI Applications**: Tools to build demos and applications (Spaces).
- **Enterprise Solutions**: Enterprise-grade security and dedicated support (Enterprise Hub).

### Customers
We serve a wide variety of industries. More than **{data['stats']['orgs']} organizations** use our platform, including prominent names like:
"""
        # Lista de clientes
        for empresa in data['empresas_destacadas']:
            texto += f"- **{empresa}** \n"

        texto += """
### Culture
"""
        # Lista de cultura (simulando los párrafos del original con los headers extraídos)
        for valor in data['cultura_headers']:
            texto += f"- **{valor}** \n"

        texto += """
### Careers
We are constantly seeking diverse talent. We offer opportunities in areas such as:
"""
        # Lista de áreas
        for area in data['areas_trabajo']:
            texto += f"- {area}\n"

        texto += "\n**Benefits**:\n"
        for beneficio in data['beneficios']:
            texto += f"- {beneficio}\n"

        texto += """
### Contact
For more information, visit our [website](https://huggingface.co/).

### Legal Note
Content generated offline for testing.
"""
        return texto

    def extract_humorous_info_from_compiled(self, compiled_content):
        data = {
            "stats": {"modelos": "1M+", "datasets": "250k+"},
            "empresas_detectadas": [],
            "beneficios_detectados": []
        }
        about_text = compiled_content.get("about page", "")
        match_models = re.search(r"Browse ([\d\w\+]+) models", about_text)
        if match_models: data["stats"]["modelos"] = match_models.group(1)

        match_datasets = re.search(r"Browse ([\d\w\+]+) datasets", about_text)
        if match_datasets: data["stats"]["datasets"] = match_models.group(1) # Corrected logic based on data extraction template

        customers_text = compiled_content.get("customers page", "")
        combined_text = about_text + customers_text
        target_companies = ["NVIDIA", "Meta", "Amazon", "Google"]
        for company in target_companies:
            if company in combined_text or (company == "Meta" and "AI at Meta" in combined_text):
                data["empresas_detectadas"].append(company)

        careers_text = compiled_content.get("careers page", "")
        if "Flexible Work" in careers_text: data["beneficios_detectados"].append("flexibility")
        if "Unlimited PTO" in careers_text: data["beneficios_detectados"].append("unlimited time off")
        return data

    def generate_humorous_brochure_mock(self, compiled_content):     
        data = self.extract_humorous_info_from_compiled(compiled_content)
                
        seccion_clientes = ""
        if "NVIDIA" in data["empresas_detectadas"]:
            seccion_clientes += "- **NVIDIA**: With over 585 models on our platform.\n"
        if "Meta" in data["empresas_detectadas"]:
            seccion_clientes += "- **AI at Meta**: Using our resources to drive their innovation.\n"
    
        otros_gigantes = [empresa for empresa in ["Amazon", "Google"] if empresa in data["empresas_detectadas"]]
        if len(otros_gigantes) > 0:
            nombres = " and ".join(otros_gigantes)
            seccion_clientes += f"- **{nombres}**: They've also found their place in our community.\n"

        texto = f"""# Hugging Face
## The AI community building the future. 🤗

### Summary
Our mission is to democratize ML and make AI as accessible as a coffee on the corner. We create a platform where the ML community collaborates on models, datasets, and apps, like we're all at one big algorithm party. 🎉 Come explore, create, and discover!

### Value Proposition
Where AI lives! We create the world's largest collaboration platform for ML.

### Products/Services
- **Models**: Over {data['stats']['modelos']} models, from text generation to images, so you can find the one that best suits your needs. Find your algorithmic soulmate!
- **Datasets**: Access over {data['stats']['datasets']} datasets for any ML task. It's like a free data buffet! 🍽️
- **Spaces**: Interactive applications where you can experiment with AI models in real time. More fun than an amusement park! 🎢
- **Enterprise Solutions**: Advanced options for organizations looking to scale their AI with security and dedicated support. Because AI needs a safe place to play too! 🏰

### Customers
We serve a wide range of industries, from technology to health, education, and entertainment. Our clients include everything from curious startups to giants like Google, Microsoft, and Amazon. If you're looking for an AI solution, you're in the right place!

### Culture
- **Diversity**: We believe all voices count, like in a choir where every note matters. 🎶
- **Continuous Development**: We offer reimbursement for conferences and training. Never stop learning!
- **Wellbeing**: Flexible hours and hybrid work options. Because life is more than just work!
- **Equity**: All employees are shareholders and share in the company's success. Together we are stronger! 💪

### Careers
Looking to join our team? We're currently seeking passionate people in various areas, from ML engineering to sales. We offer benefits like flexible hours, unlimited time off, and the chance to work with some of the best in the industry. Click on [see jobs](https://apply.workable.com/huggingface/) to join the fun!

### Contact
We're here to help! If you have questions or want to know more about our solutions, don't hesitate to get in touch. Visit us at [Hugging Face](https://huggingface.co) or email us at **contact@huggingface.co**. See you soon! 👋

### Legal Note
Content generated offline for testing.
"""
        return texto

def generate_brochure(company_name, compiled_content, tone="formal", model="gpt-4o-mini", language = 'en'):
    generator = BrochureGenerator()
    return generator.generate_brochure(company_name, compiled_content, tone=tone, model=model, language=language)

def translate_brochure(brochure_text, target_language="es", model="gpt-4o-mini"):
    generator = BrochureGenerator()
    return generator.translate_brochure(brochure_text, target_language, model)