'''Purpose of main.py: The heart of the application - sets up and runs the FastAPI server
What it does:

Initializes FastAPI application
Sets up CORS middleware for cross-origin requests
Defines all API endpoints (routes)
Handles global exception handling
Initializes services (translation & logging)
Starts the uvicorn server'''


from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime
import logging

from models import TranslationRequest, BulkTranslationRequest, TranslationResponse, BulkTranslationResponse, HealthResponse
from services.translation_service import TranslationService
from services.logging_service import LoggingService
from utils.validators import validate_language_code, validate_text_length
from config import settings

#logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

#Initialize FastAPI app
app = FastAPI(
    title="Translation Microservice",
    description="A lightweight, scalable translation API service",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Initialize services
translation_service = TranslationService()
logging_service = LoggingService()


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )


@app.get("/", tags=["Root"])
async def root():
    return {
        "service": "Translation Microservice",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "translate": "/api/v1/translate",
            "bulk_translate": "/api/v1/translate/bulk",
            "logs": "/api/v1/logs",
            "supported_languages": "/api/v1/languages"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        service="translation-service",
        version="1.0.0"
    )


@app.post("/api/v1/translate", response_model=TranslationResponse, tags=["Translation"])
async def translate_text(request: TranslationRequest):
    try:
        validate_text_length(request.text, settings.MAX_TEXT_LENGTH)
        validate_language_code(request.target_language)
        
        if request.source_language:
            validate_language_code(request.source_language)
        
        #Perform translation
        translated_text = translation_service.translate(
            text=request.text,
            target_lang=request.target_language,
            source_lang=request.source_language
        )
        
        log_entry = logging_service.log_translation(
            original_text=request.text,
            translated_text=translated_text,
            source_lang=request.source_language or "auto",
            target_lang=request.target_language,
            char_count=len(request.text)
        )
        
        logger.info(f"Translation completed: {request.target_language} - {len(request.text)} chars")
        
        return TranslationResponse(
            original_text=request.text,
            translated_text=translated_text,
            source_language=request.source_language or "auto",
            target_language=request.target_language,
            timestamp=log_entry["timestamp"],
            character_count=len(request.text)
        )
        
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Translation error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")


@app.post("/api/v1/translate/bulk", response_model=BulkTranslationResponse, tags=["Translation"])
async def bulk_translate(request: BulkTranslationRequest):
    try:
        if not request.texts:
            raise ValueError("No texts provided for translation")
        
        if len(request.texts) > settings.MAX_BULK_SIZE:
            raise ValueError(f"Maximum {settings.MAX_BULK_SIZE} texts allowed per request")
        
        validate_language_code(request.target_language)
        
        if request.source_language:
            validate_language_code(request.source_language)
        
        for text in request.texts:
            validate_text_length(text, settings.MAX_TEXT_LENGTH)
        
        translations = []
        for text in request.texts:
            translated = translation_service.translate(
                text=text,
                target_lang=request.target_language,
                source_lang=request.source_language
            )
            translations.append(translated)
            
            logging_service.log_translation(
                original_text=text,
                translated_text=translated,
                source_lang=request.source_language or "auto",
                target_lang=request.target_language,
                char_count=len(text)
            )
        
        logger.info(f"Bulk translation completed: {len(translations)} texts")
        
        return BulkTranslationResponse(
            translations=translations,
            target_language=request.target_language,
            source_language=request.source_language or "auto",
            count=len(translations),
            timestamp=datetime.utcnow()
        )
        
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Bulk translation error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Bulk translation failed: {str(e)}")


@app.get("/api/v1/logs", tags=["Logging"])
async def get_logs(limit: int = 50):
    try:
        if limit > 500:
            limit = 500
        
        logs = logging_service.get_logs(limit=limit)
        return {
            "count": len(logs),
            "logs": logs
        }
    except Exception as e:
        logger.error(f"Error retrieving logs: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve logs")


@app.get("/api/v1/logs/stats", tags=["Logging"])
async def get_statistics():
    try:
        stats = logging_service.get_statistics()
        return stats
    except Exception as e:
        logger.error(f"Error retrieving statistics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve statistics")


@app.get("/api/v1/languages", tags=["Reference"])
async def get_supported_languages():
    return {
        "languages": translation_service.get_supported_languages()
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )