'''Purpose: Defines the structure of requests and responses using Pydantic
What it does:

Validates incoming request data
Ensures correct data types
Provides automatic API documentation
Serializes response data'''

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime


class TranslationRequest(BaseModel):
    """Request model for single translation"""
    text: str = Field(..., description="Text to translate", min_length=1, max_length=1000)
    target_language: str = Field(..., description="Target language ISO code", min_length=2, max_length=5)
    source_language: Optional[str] = Field(None, description="Source language ISO code (auto-detect if not provided)")
    
    @validator('text')
    def text_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Text cannot be empty")
        return v.strip()
    
    @validator('target_language', 'source_language')
    def normalize_language_code(cls, v):
        if v:
            return v.lower().strip()
        return v

    class Config:
        schema_extra = {
            "example": {
                "text": "Hello, how are you?",
                "target_language": "ta",
                "source_language": "en"
            }
        }


class BulkTranslationRequest(BaseModel):
    """Request model for bulk translation"""
    texts: List[str] = Field(..., description="List of texts to translate", min_items=1, max_items=50)
    target_language: str = Field(..., description="Target language ISO code")
    source_language: Optional[str] = Field(None, description="Source language ISO code")
    
    @validator('texts')
    def validate_texts(cls, v):
        cleaned = [text.strip() for text in v if text.strip()]
        if not cleaned:
            raise ValueError("At least one non-empty text is required")
        return cleaned
    
    @validator('target_language', 'source_language')
    def normalize_language_code(cls, v):
        if v:
            return v.lower().strip()
        return v

    class Config:
        schema_extra = {
            "example": {
                "texts": ["Hello", "Good morning", "Thank you"],
                "target_language": "hi",
                "source_language": "en"
            }
        }


class TranslationResponse(BaseModel):
    """Response model for single translation"""
    original_text: str
    translated_text: str
    source_language: str
    target_language: str
    timestamp: datetime
    character_count: int

    class Config:
        schema_extra = {
            "example": {
                "original_text": "Hello, how are you?",
                "translated_text": "வணக்கம், நீங்கள் எப்படி இருக்கிறீர்கள்?",
                "source_language": "en",
                "target_language": "ta",
                "timestamp": "2025-09-30T10:30:00",
                "character_count": 19
            }
        }


class BulkTranslationResponse(BaseModel):
    """Response model for bulk translation"""
    translations: List[str]
    target_language: str
    source_language: str
    count: int
    timestamp: datetime

    class Config:
        schema_extra = {
            "example": {
                "translations": ["வணக்கம்", "காலை வணக்கம்", "நன்றி"],
                "target_language": "ta",
                "source_language": "en",
                "count": 3,
                "timestamp": "2025-09-30T10:30:00"
            }
        }


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    timestamp: datetime
    service: str
    version: str

    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2025-09-30T10:30:00",
                "service": "translation-service",
                "version": "1.0.0"
            }
        }
