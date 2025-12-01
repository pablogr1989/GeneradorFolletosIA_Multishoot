import streamlit as st
import sys
import os
import time
import asyncio 
from datetime import datetime

# --- PARCHE PARA WINDOWS + PLAYWRIGHT ---
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
# ----------------------------------------

# Asegurar que el path raíz está en sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from core import scraping, link_selector, compiler, brochure
from utils.cache_manager import cache_manager
from utils.metrics import MetricsTracker
from utils.api_openai import OpenAIClient
from utils.exporters import markdown_to_html, markdown_to_pdf
from utils.utils import save_md
from utils.mock_responses import get_mock_compiled_content
from utils.language_detector import *
from utils.logger import logger 

# Configuración de la página
st.set_page_config(page_title="Generador de Folletos IA", page_icon="📄", layout="wide")
st.title("📄 Generador de Folletos Corporativos con IA")

openai_client = OpenAIClient()


def render_brochure_tab(content, language_code, file_paths, company_name):
    """
    Muestra el contenido y los botones de descarga usando rutas PRE-GENERADAS.
    """
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Código Markdown")
        st.code(content, language="markdown")
    
    with col2:
        st.subheader("Vista Previa")
        container = st.container(height=500)
        container.markdown(content)

    st.divider()
    st.subheader("📥 Descargas")
    
    d_col1, d_col2, d_col3 = st.columns(3)
    
    # 1. Descargar Markdown desde directorio
    if file_paths.get('md') and os.path.exists(file_paths['md']):
        with d_col1:
            with open(file_paths['md'], "r", encoding="utf-8") as f:
                st.download_button(
                    label=f"⬇️ Markdown ({language_code})",
                    data=f,
                    file_name=os.path.basename(file_paths['md']),
                    mime="text/markdown",
                    use_container_width=True,
                    key=f"btn_md_{language_code}"
                )
    else:
        # Si no se ha creado por algun motivo, lo crea desde memoria
        safe_company = company_name.lower().replace(' ', '_')
        md_filename = f"{safe_company}_brochure_{language_code}.md"
        with d_col1:
            st.download_button(
                label=f"⬇️ Markdown ({language_code})",
                data=content,
                file_name=md_filename,
                mime="text/markdown",
                use_container_width=True,
                key=f"btn_md_{language_code}" 
            )

    # 2. Descargar HTML (Desde archivo pre-generado)
    if file_paths.get('html') and os.path.exists(file_paths['html']):
        with d_col2:
            with open(file_paths['html'], "r", encoding="utf-8") as f:
                st.download_button(
                    label=f"⬇️ HTML ({language_code})",
                    data=f,
                    file_name=os.path.basename(file_paths['html']),
                    mime="text/html",
                    use_container_width=True,
                    key=f"btn_html_{language_code}"
                )

    # 3. Descargar PDF (Desde archivo pre-generado)
    if file_paths.get('pdf') and os.path.exists(file_paths['pdf']):
        with d_col3:
            with open(file_paths['pdf'], "rb") as f:
                st.download_button(
                    label=f"⬇️ PDF ({language_code})",
                    data=f,
                    file_name=os.path.basename(file_paths['pdf']),
                    mime="application/pdf",
                    use_container_width=True,
                    key=f"btn_pdf_{language_code}"
                )
    elif file_paths.get('pdf'):
        st.warning("⚠️ El archivo PDF expiró o fue borrado.")


def generate_export_files(content, company_name, lang_code, formats):
    """
    Genera los archivos físicos una sola vez y devuelve sus rutas.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_company = company_name.lower().replace(' ', '_')
    base_name = f"{timestamp}_{safe_company}_{lang_code}"
    
    paths = {'html': None, 'pdf': None, 'md' : None}
    
    md_filename = f"{base_name}"
    md_path = save_md(content, md_filename)
    if md_path:
        paths['md'] = md_path
    
    if "html" in formats or "pdf" in formats:
        # Generamos HTML
        html_file = f"{base_name}.html"
        paths['html'] = markdown_to_html(content, html_file)
        
        if "pdf" in formats and paths['html']:
            # Generamos PDF desde el HTML
            pdf_file = f"{base_name}.pdf"
            paths['pdf'] = markdown_to_pdf(content, paths['html'], pdf_file)
            
            # Limpieza opcional del HTML si el usuario no lo pidió explícitamente
            if "html" not in formats and os.path.exists(paths['html']):
                os.remove(paths['html'])
                paths['html'] = None

    return paths

# -------------------------------------------------------------------------
# SIDEBAR
# -------------------------------------------------------------------------
with st.sidebar:
    st.header("Configuración")
    
    company_name = st.text_input("Nombre de la empresa", "Hugging Face", disabled=openai_client.mock_mode)
    url = st.text_input("URL del sitio web", "https://huggingface.co", disabled=openai_client.mock_mode)
    
    with st.expander("Modelos IA"):
        model_selector = st.selectbox("Selección de Enlaces", ["gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"], index=0)
        model_writer = st.selectbox("Redacción", ["gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"], index=0)
        model_translator = st.selectbox("Traducción", ["gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"], index=0)
    
    lang_options = list(get_language_list().keys())
    default_lang_index = lang_options.index("Español") if "Español" in lang_options else 0
    selected_language = st.selectbox(
        "Idioma de destino (Traducción)", 
        lang_options, 
        index=default_lang_index,
        disabled=openai_client.mock_mode
    )
    
    tone = st.selectbox("Tono", ["formal", "humoristico"])

    use_cache = st.checkbox("Usar caché local", value=False)
    formats = st.multiselect("Formatos de descarga", ["html", "pdf"], default=["html", "pdf"])
    
    st.divider()
    generate_button = st.button("Generar Folleto", type="primary")

# -------------------------------------------------------------------------
# LÓGICA PRINCIPAL
# -------------------------------------------------------------------------
if generate_button:
    # 1. Limpieza de estado anterior
    if 'results' in st.session_state:
        del st.session_state['results']

    # 2. Validaciones
    if not url:
        st.error("⚠️ Por favor, introduce una URL válida.")
        st.stop()
    if not company_name:
        company_name = "Empresa"

    # 3. Ejecución
    metrics = MetricsTracker()
    metrics.start()
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    consolidated_content = None
    detected_lang = "es"
    
    try:
        logger.info("="*60)
        logger.info("INICIANDO GENERACIÓN DESDE UI")
        
        if openai_client.mock_mode:
            st.warning("⚠️ Modo MOCK activado.")
            progress_bar.progress(50)
            consolidated_content = get_mock_compiled_content(tone)
            detected_lang = "en"
        else:
            # Scraping
            status_text.text("Paso 1/5: Scraping...")
            progress_bar.progress(10)
            start = time.time()
            web_content = scraping.Web.get_data_with_cache(url, use_cache=use_cache)
            if not web_content:
                st.error("❌ Error de acceso a la web.")
                st.stop()
            metrics.record_stage("Scraping", time.time() - start)

            # Extracción
            status_text.text("Paso 2/5: Analizando...")
            progress_bar.progress(25)
            [web_title, web_text, web_links] = scraping.Web.clean_text(web_content)
            detected_lang = detect_language(web_text)
            
            # Selección
            status_text.text("Paso 3/5: Seleccionando enlaces...")
            progress_bar.progress(40)
            start = time.time()
            selector = link_selector.LinkSelector()
            selected_links = selector.select_relevant_links(url, web_links, model=model_selector)
            metrics.record_stage("Seleccion", time.time() - start)
            
            if not selected_links or not selected_links.get("links"):
                st.error("❌ La IA no encontró enlaces relevantes.")
                st.stop()

            # Compilación
            status_text.text("Paso 4/5: Compilando contenido...")
            progress_bar.progress(60)
            start = time.time()
            consolidated_content = compiler.compile_links(selected_links, delay=1.0, use_cache=use_cache)
            metrics.record_stage("Compilacion", time.time() - start)

        if consolidated_content:
            # Generación
            status_text.text("Paso 5/6: Redactando...")
            progress_bar.progress(80)
            start = time.time()
            brochure_original = brochure.generate_brochure(
                company_name=company_name,
                compiled_content=consolidated_content,
                tone=tone,
                model=model_writer,
                language=detected_lang
            )
            metrics.record_stage("Generacion", time.time() - start)

            # Traducción
            target_lang_code = get_language_list()[selected_language]
            brochure_translated = None
            
            if target_lang_code and target_lang_code != detected_lang:
                status_text.text("Paso 6/6: Traduciendo...")
                progress_bar.progress(90)
                start = time.time()
                brochure_translated = brochure.translate_brochure(
                    brochure_text=brochure_original,
                    target_language=target_lang_code,
                    model=model_translator
                )
                metrics.record_stage("Traduccion", time.time() - start)
            
            progress_bar.progress(100)
            status_text.success("✅ ¡Completado!")
            
            # --- GENERACIÓN DE ARCHIVOS FÍSICOS
            logger.info("Generando archivos físicos (PDF/HTML)...")
            
            paths_original = generate_export_files(
                brochure_original, company_name, f"{detected_lang}_original", formats
            )
            
            paths_translated = {}
            if brochure_translated:
                paths_translated = generate_export_files(
                    brochure_translated, company_name, f"{target_lang_code}_translated", formats
                )

            # --- GUARDADO EN SESSION STATE ---
            st.session_state['results'] = {
                'original': {
                    'content': brochure_original,
                    'lang': detected_lang,
                    'files': paths_original
                },
                'translated': {
                    'content': brochure_translated,
                    'lang': target_lang_code,
                    'files': paths_translated
                } if brochure_translated else None,
                'metrics': metrics.get_summary(),
                'company_name': company_name
            }
            logger.info("Resultados guardados en session_state.")

    except Exception as e:
        st.error(f"❌ Error: {e}")
        logger.error(f"Error UI: {e}", exc_info=True)

# -------------------------------------------------------------------------
# RENDERIZADO DE RESULTADOS
# -------------------------------------------------------------------------
if 'results' in st.session_state:
    res = st.session_state['results']
    
    st.success("¡Folleto generado exitosamente!")
    
    # Etiquetas de pestañas
    tabs_labels = [f"📄 Original ({res['original']['lang']})"]
    if res['translated']:
        tabs_labels.append(f"🌍 Traducido ({res['translated']['lang']})")
    tabs_labels.append("📊 Métricas")
    
    tabs = st.tabs(tabs_labels)
    
    # Tab Original
    with tabs[0]:
        render_brochure_tab(
            content=res['original']['content'], 
            language_code=res['original']['lang'], 
            file_paths=res['original']['files'],
            company_name=res['company_name']
        )
    
    # Tab Traducido
    if res['translated']:
        with tabs[1]:
            render_brochure_tab(
                content=res['translated']['content'], 
                language_code=res['translated']['lang'], 
                file_paths=res['translated']['files'],
                company_name=res['company_name']
            )
            
    # Tab Métricas
    with tabs[-1]:
        summary = res['metrics']
        c1, c2 = st.columns(2)
        c1.metric("Tiempo Total", f"{summary['total_time']:.2f}s")
        c1.metric("Tokens Totales", summary['total_tokens'])
        c2.write("**Detalle por etapa:**")
        for stage, duration in summary['stages'].items():
            c2.write(f"- {stage}: {duration:.2f}s")

else:
    if not generate_button:
        st.info("👈 Configura los parámetros y pulsa 'Generar Folleto'")