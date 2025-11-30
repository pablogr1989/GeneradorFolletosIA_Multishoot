import pytest
import os
from core.brochure import BrochureGenerator
from utils.mock_responses import get_mock_compiled_content


class TestBrochureGeneration:
    
    def test_brochure_mock_formal(self):
        generator = BrochureGenerator()
        generator.openai_client.mock_mode = True
        compiled = get_mock_compiled_content("formal")
        
        brochure = generator.generate_brochure(
            company_name="Test Company",
            compiled_content=compiled,
            tone="formal"
        )
        
        assert brochure is not None
        assert "Hugging Face" in brochure
    
    def test_brochure_mock_humoristico(self):
        generator = BrochureGenerator()
        compiled = get_mock_compiled_content("humoristico")
        
        brochure = generator.generate_brochure(
            company_name="Funny Corp",
            compiled_content=compiled,
            tone="humoristico"
        )
        
        assert brochure is not None
        assert "Funny Corp" in brochure
    
    def test_brochure_structure_has_required_sections(self):
        generator = BrochureGenerator()
        compiled = get_mock_compiled_content("formal")
        
        brochure = generator.generate_brochure(
            company_name="Company X",
            compiled_content=compiled,
            tone="formal"
        )
        
        # Verificar que tiene headers
        assert "##" in brochure, "Falta headers de nivel 2"

        # Verificar "Qué hacemos" (en español o inglés)
        has_what_we_do = "Qué hacemos" in brochure or "What We Do" in brochure or "What we do" in brochure
        assert has_what_we_do, "Falta seccion 'Qué hacemos' o 'What We Do'"

        # Verificar otras secciones (español o inglés)
        has_products = "Productos" in brochure or "Products" in brochure
        assert has_products, "Falta seccion Productos/Products"

        has_contact = "Contacto" in brochure or "Contact" in brochure
        assert has_contact, "Falta seccion Contacto/Contact"


class TestExporters:
    
    def test_markdown_to_html(self):
        from utils.exporters import markdown_to_html
        
        markdown_text = """# Test Title
## Subtitle
- Item 1
- Item 2
"""
        
        html = markdown_to_html(markdown_text)
        
        assert html is not None
        assert "<h1>" in html or "Test Title" in html
        assert "<h2>" in html or "Subtitle" in html
        assert "<li>" in html or "Item" in html