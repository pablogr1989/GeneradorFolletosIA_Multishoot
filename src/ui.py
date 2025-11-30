import streamlit as st
import sys
import os
import time
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from core import scraping, link_selector, compiler, brochure
from utils.cache_manager import cache_manager
from utils.metrics import MetricsTracker
from utils.api_openai import OpenAIClient
from utils.exporters import markdown_to_html, markdown_to_pdf
from utils.mock_responses import get_mock_compiled_content
from utils.language_detector import *

st.set_page_config(page_title="Generador de Folletos IA", page_icon="📄", layout="wide")
st.title("📄 Generador de Folletos Corporativos con IA")

openai_client = OpenAIClient()

# Sidebar
with st.sidebar:
    st.header("Configuración")
    
    company_name = st.text_input("Nombre de la empresa", "Hugging Face", disabled=openai_client.mock_mode)
    url = st.text_input("URL del sitio web", "https://huggingface.co", disabled=openai_client.mock_mode)
    selected_language = st.selectbox("Idioma del folleto", list(get_language_list().keys()), disabled=openai_client.mock_mode)
    tone = st.selectbox("Tono", ["formal", "humoristico"])
    use_cache = st.checkbox("Usar caché local", value=False)
    formats = st.multiselect("Formatos de salida", ["md", "html", "pdf"], default=["md"])
    
    generate_button = st.button("🚀 Generar Folleto", type="primary")

# Main content
if generate_button:
    metrics = MetricsTracker()
    metrics.start()
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    consolidated_content = None
    detected_lang = "es" # Default
    
    try:
        # ---------------------------------------------------------
        # LÓGICA MODO MOCK (Sin API Key)
        # ---------------------------------------------------------
        if openai_client.mock_mode:
            st.warning("⚠️ Modo MOCK activado (sin API key detectada). Usando datos de prueba offline.")
            
            # Simulamos carga rápida
            status_text.text("Modo Mock: Cargando contenido offline...")
            progress_bar.progress(50)
            time.sleep(0.5) 
            
            start = time.time()
            consolidated_content = get_mock_compiled_content(tone)
            metrics.record_stage("Carga Mock Offline", time.time() - start)
            
            detected_lang = "en" # Mock data esta en ingles, asi que es el unico idioma posible
            
            if not consolidated_content:
                st.error("Error: No se pudo cargar contenido mock")
                st.stop()
                
            progress_bar.progress(80)

        # ---------------------------------------------------------
        # LÓGICA MODO NORMAL (Con API Key)
        # ---------------------------------------------------------
        else:
            # PASO 1: Scraping
            status_text.text("Paso 1/5: Descargando página web...")
            progress_bar.progress(20)
            
            start = time.time()
            web_content = scraping.Web.get_data_with_cache(url, use_cache=use_cache)
            
            if not web_content:
                st.error("No se pudo descargar la página")
                st.stop()
            
            metrics.record_stage("Scraping", time.time() - start)
            
            # PASO 2: Extracción
            status_text.text("Paso 2/5: Extrayendo enlaces...")
            progress_bar.progress(40)
            
            [web_title, web_text, web_links] = scraping.Web.clean_text(web_content)
            detected_lang = detect_language(web_text) # Detectar idioma real de la web
            
            language = get_language_list()[selected_language]
            if is_language_supported(language): # Si queremos algun idioma especifico, sobreescribimos el lenguaje de la web
                detected_lang = language  
            
            st.info(f"✅ Título: {web_title} | Idioma: {detected_lang} | Enlaces: {len(web_links)}")
            
            # PASO 3: Selección con IA
            status_text.text("Paso 3/5: Seleccionando enlaces relevantes con IA...")
            progress_bar.progress(60)
            
            start = time.time()
            selector = link_selector.LinkSelector()
            selected_links = selector.select_relevant_links(url, web_links)
            metrics.record_stage("Seleccion", time.time() - start)
            
            if not selected_links or not selected_links.get("links"):
                st.error("No se encontraron enlaces relevantes")
                st.stop()
            
            with st.expander("📋 Enlaces seleccionados"):
                for link in selected_links["links"]:
                    st.write(f"- **{link['type']}**: {link['url']}")
            
            # PASO 4: Compilación
            status_text.text("Paso 4/5: Compilando contenido...")
            progress_bar.progress(80)
            
            start = time.time()
            consolidated_content = compiler.compile_links(selected_links, delay=1.0, use_cache=use_cache)
            metrics.record_stage("Compilacion", time.time() - start)

        # ---------------------------------------------------------
        # PASO 5: GENERACIÓN (Común para ambos modos)
        # ---------------------------------------------------------
        if consolidated_content:
            status_text.text("Paso 5/5: Generando folleto con IA...")
            progress_bar.progress(90)
            
            start = time.time()
            brochure_content = brochure.generate_brochure(
                company_name=company_name,
                compiled_content=consolidated_content,
                tone=tone,
                model="gpt-4o-mini",
                language=detected_lang
            )
            metrics.record_stage("Generacion", time.time() - start)
            
            progress_bar.progress(100)
            status_text.text("✅ Proceso completado")
            
            # Mostrar resultado
            st.success("¡Folleto generado exitosamente!")
            
            # Tabs para diferentes vistas
            tab1, tab2, tab3 = st.tabs(["📄 Markdown", "🌐 Preview", "📊 Métricas"])
            
            with tab1:
                st.markdown("### Contenido del folleto:")
                st.code(brochure_content, language="markdown")
                st.download_button(
                    "⬇️ Descargar Markdown",
                    brochure_content,
                    file_name=f"{company_name.lower().replace(' ', '_')}_brochure.md"
                )
            
            with tab2:
                st.markdown("### Vista previa:")
                st.markdown(brochure_content)
            
            with tab3:
                summary = metrics.get_summary()
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Tiempo total", f"{summary['total_time']:.2f}s")
                    st.metric("Tokens usados", summary['total_tokens'])
                
                with col2:
                    st.write("**Tiempos por etapa:**")
                    for stage, duration in summary['stages'].items():
                        st.write(f"- {stage}: {duration:.2f}s")
            
            # Exportar formatos
            if "html" in formats or "pdf" in formats:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                if "html" in formats:
                    html_file = markdown_to_html(brochure_content, f"{timestamp}_brochure.html")
                    st.success(f"✅ HTML generado: {html_file}")
                
                if "pdf" in formats:
                    pdf_file = markdown_to_pdf(brochure_content, f"{timestamp}_brochure.html", f"{timestamp}_brochure.pdf")
                    st.success(f"✅ PDF generado: {pdf_file}")
    
    except Exception as e:
        st.error(f"❌ Error: {e}")
        import traceback
        st.code(traceback.format_exc())

else:
    st.info("👈 Configura los parámetros y presiona 'Generar Folleto'")