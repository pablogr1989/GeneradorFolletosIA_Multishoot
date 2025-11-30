import pytest
from utils.validators import validate_selected_links, validate_compiled_content


class TestValidators:
    
    def test_validate_selected_links_valid(self):
        data = {
            "links": [
                {"type": "about page", "url": "https://example.com/about"},
                {"type": "careers page", "url": "https://example.com/careers"}
            ]
        }
        
        result = validate_selected_links(data)
        
        assert len(result["links"]) == 2
        assert result["links"][0]["type"] == "about page"
        assert result["links"][0]["url"] == "https://example.com/about"
    
    def test_validate_selected_links_empty(self):
        data = {"links": []}
        result = validate_selected_links(data)
        assert result["links"] == []
    
    def test_validate_selected_links_invalid_structure(self):
        data = {
            "links": [
                {"type": "about page"},  # Falta url
                {"url": "https://example.com"},  # Falta type
                {"type": "valid", "url": "https://valid.com"}  # Válido
            ]
        }
        
        result = validate_selected_links(data)
        # Debe recuperar solo el válido
        assert len(result["links"]) == 1
        assert result["links"][0]["url"] == "https://valid.com"
    
    def test_validate_compiled_content_valid(self):
        data = {
            "about page": "Contenido de about",
            "products page": "Contenido de productos",
            "careers page": "Contenido de carreras"
        }
        
        result = validate_compiled_content(data)
        
        assert len(result) == 3
        assert "about page" in result
        assert len(result["about page"]) > 0
    
    def test_validate_compiled_content_with_empty(self):
        data = {
            "about page": "Contenido valido",
            "empty page": "",
            "invalid page": None
        }
        
        result = validate_compiled_content(data)
        
        assert len(result) == 1
        assert "about page" in result
        assert "empty page" not in result


class TestMockMode:
    
    def test_mock_compiled_content_loads(self):
        from utils.mock_responses import get_mock_compiled_content
        
        content = get_mock_compiled_content("formal")
        
        assert content is not None
        assert isinstance(content, dict)
        assert len(content) > 0
    
    def test_mock_compiled_content_humoristico(self):
        from utils.mock_responses import get_mock_compiled_content
        
        content = get_mock_compiled_content("humoristico")
        
        assert content is not None
        assert isinstance(content, dict)