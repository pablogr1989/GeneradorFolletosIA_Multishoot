# Archivo: src/utils/pdf_renderer.py
import sys
from playwright.sync_api import sync_playwright
from pathlib import Path

def render_pdf(html_path, output_path):
    html_file = Path(html_path).resolve()
    pdf_file = Path(output_path).resolve()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Cargar archivo local
        page.goto(f"file:///{html_file}")
        
        # Generar PDF con opciones de formato
        page.pdf(
            path=str(pdf_file),
            format="A4",
            print_background=True,
            margin={"top": "20mm", "bottom": "20mm", "left": "20mm", "right": "20mm"}
        )
        browser.close()

if __name__ == "__main__":
    # Recibimos los argumentos desde la línea de comandos
    if len(sys.argv) < 3:
        print("Uso: python pdf_renderer.py <input_html> <output_pdf>")
        sys.exit(1)
        
    in_html = sys.argv[1]
    out_pdf = sys.argv[2]
    
    try:
        render_pdf(in_html, out_pdf)
        print("SUCCESS") # Señal de éxito para el script padre
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)