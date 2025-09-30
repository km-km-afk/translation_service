# tests/test_api.py
"""
Unit tests for the Translation API
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestHealthEndpoint:
    """Tests for health check endpoint"""
    
    def test_health_check(self):
        """Test health endpoint returns 200"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "translation-service"
        assert "timestamp" in data


class TestRootEndpoint:
    """Tests for root endpoint"""
    
    def test_root(self):
        """Test root endpoint returns service info"""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "service" in data
        assert "endpoints" in data


class TestTranslationEndpoint:
    """Tests for translation endpoint"""
    
    def test_translate_success(self):
        """Test successful translation"""
        payload = {
            "text": "Hello",
            "target_language": "ta",
            "source_language": "en"
        }
        
        response = client.post("/api/v1/translate", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert "translated_text" in data
        assert data["target_language"] == "ta"
        assert data["source_language"] == "en"
        assert "timestamp" in data
    
    def test_translate_missing_text(self):
        """Test translation with missing text"""
        payload = {
            "target_language": "ta"
        }
        
        response = client.post("/api/v1/translate", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_translate_empty_text(self):
        """Test translation with empty text"""
        payload = {
            "text": "",
            "target_language": "ta"
        }
        
        response = client.post("/api/v1/translate", json=payload)
        assert response.status_code == 422
    
    def test_translate_invalid_language(self):
        """Test translation with invalid language code"""
        payload = {
            "text": "Hello",
            "target_language": "xyz"
        }
        
        response = client.post("/api/v1/translate", json=payload)
        assert response.status_code == 400
    
    def test_translate_text_too_long(self):
        """Test translation with text exceeding max length"""
        payload = {
            "text": "a" * 1001,
            "target_language": "ta"
        }
        
        response = client.post("/api/v1/translate", json=payload)
        assert response.status_code == 422
    
    def test_translate_multiple_languages(self):
        """Test translation to different languages"""
        languages = ["ta", "hi", "kn", "bn"]
        
        for lang in languages:
            payload = {
                "text": "Thank you",
                "target_language": lang,
                "source_language": "en"
            }
            
            response = client.post("/api/v1/translate", json=payload)
            assert response.status_code == 200
            
            data = response.json()
            assert data["target_language"] == lang


class TestBulkTranslationEndpoint:
    """Tests for bulk translation endpoint"""
    
    def test_bulk_translate_success(self):
        """Test successful bulk translation"""
        payload = {
            "texts": ["Hello", "Thank you", "Goodbye"],
            "target_language": "ta",
            "source_language": "en"
        }
        
        response = client.post("/api/v1/translate/bulk", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert "translations" in data
        assert len(data["translations"]) == 3
        assert data["count"] == 3
        assert data["target_language"] == "ta"
    
    def test_bulk_translate_empty_list(self):
        """Test bulk translation with empty list"""
        payload = {
            "texts": [],
            "target_language": "ta"
        }
        
        response = client.post("/api/v1/translate/bulk", json=payload)
        assert response.status_code == 422
    
    def test_bulk_translate_too_many_items(self):
        """Test bulk translation with too many items"""
        payload = {
            "texts": ["text"] * 51,
            "target_language": "ta"
        }
        
        response = client.post("/api/v1/translate/bulk", json=payload)
        assert response.status_code == 400


class TestLogsEndpoint:
    """Tests for logs endpoint"""
    
    def test_get_logs(self):
        """Test retrieving logs"""
        # First make a translation to create a log
        payload = {
            "text": "Hello",
            "target_language": "ta"
        }
        client.post("/api/v1/translate", json=payload)
        
        # Now get logs
        response = client.get("/api/v1/logs?limit=10")
        assert response.status_code == 200
        
        data = response.json()
        assert "logs" in data
        assert "count" in data
    
    def test_get_statistics(self):
        """Test retrieving statistics"""
        response = client.get("/api/v1/logs/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_translations" in data
        assert "total_characters" in data


class TestSupportedLanguagesEndpoint:
    """Tests for supported languages endpoint"""
    
    def test_get_supported_languages(self):
        """Test retrieving supported languages"""
        response = client.get("/api/v1/languages")
        assert response.status_code == 200
        
        data = response.json()
        assert "languages" in data
        assert isinstance(data["languages"], dict)
        assert len(data["languages"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])