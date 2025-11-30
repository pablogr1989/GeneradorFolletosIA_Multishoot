import markdown
import subprocess
import sys
import os
from utils.utils import get_outputs_path
from utils.logger import logger

def markdown_to_html(markdown_text, output_filename=None):
    html_content = markdown.markdown(
        markdown_text,
        extensions=['extra', 'codehilite', 'toc']
    )
    
    # Plantilla con fuente Segoe UI Emoji para Windows
    html_template = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Documento</title>
    <style>
        body {{
            font-family: 'Segoe UI Emoji', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            padding: 40px;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
        }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        li {{ margin-bottom: 5px; }}
        /* Estilo para bloques de código */
        pre {{ background: #f4f4f4; padding: 10px; border-radius: 5px; }}
    </style>
</head>
<body>
{html_content}
</body>
</html>
"""
    
    if output_filename:
        html_path = get_outputs_path(output_filename)
        try:
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_template)
            return html_path
        except Exception as e:
            logger.error(f"Error al guardar HTML: {e}")
            return None
    return html_template

def html_to_pdf_playwright(html_path, output_filename):
    """
    Llama a un subproceso independiente para generar el PDF.
    Esto evita el conflicto de Event Loops en Windows.
    """
    pdf_path = get_outputs_path(output_filename)
    
    # Ruta al script renderizador (asumiendo que está en la misma carpeta utils)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    renderer_script = os.path.join(current_dir, "pdf_renderer.py")
    
    # Comando: python pdf_renderer.py input.html output.pdf
    cmd = [sys.executable, renderer_script, html_path, pdf_path]
    
    try:
        logger.info("Iniciando generación de PDF en subproceso...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and "SUCCESS" in result.stdout:
            logger.info(f"PDF generado exitosamente: {pdf_path}")
            return pdf_path
        else:
            logger.error(f"Error en el subproceso: {result.stderr}")
            # Si falla, logueamos también lo que salió por stdout por si acaso
            logger.error(f"Output del subproceso: {result.stdout}")
            return None
            
    except Exception as e:
        logger.error(f"Error al ejecutar el script de PDF: {e}")
        return None

def markdown_to_pdf(markdown_text, html_filename, pdf_filename):
    html_path = markdown_to_html(markdown_text, html_filename)
    if html_path:
        return html_to_pdf_playwright(html_path, pdf_filename)
    return None