# services/translation_service.py
'''Purpose: Core business logic for translating text
What it does:

Handles both mock and real Google Translate API
Manages translation logic
Switches between translation modes
Provides list of supported languages'''

import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)


class TranslationService:
    def __init__(self, use_google_api: bool = False, api_key: Optional[str] = None):
        self.use_google_api = use_google_api
        self.api_key = api_key
        
        self.mock_translations = self._initialize_mock_translations()
        
        if use_google_api and api_key:
            self._initialize_google_translate()
        
        logger.info(f"TranslationService initialized (Google API: {use_google_api})")
    
    def _initialize_mock_translations(self) -> Dict:
        #mock translation dictionary
        return {
            'en_ta': {
                'hello': 'வணக்கம்',
                'good morning': 'காலை வணக்கம்',
                'good evening': 'மாலை வணக்கம்',
                'thank you': 'நன்றி',
                'please': 'தயவுசெய்து',
                'yes': 'ஆம்',
                'no': 'இல்லை',
                'how are you': 'நீங்கள் எப்படி இருக்கிறீர்கள்',
                'goodbye': 'பிரியாவிடை',
                'welcome': 'வரவேற்கிறோம்',
            },
            'en_hi': {
                'hello': 'नमस्ते',
                'good morning': 'सुप्रभात',
                'good evening': 'शुभ संध्या',
                'thank you': 'धन्यवाद',
                'please': 'कृपया',
                'yes': 'हाँ',
                'no': 'नहीं',
                'how are you': 'आप कैसे हैं',
                'goodbye': 'अलविदा',
                'welcome': 'स्वागत है',
            },
            'en_kn': {
                'hello': 'ನಮಸ್ಕಾರ',
                'good morning': 'ಶುಭೋದಯ',
                'good evening': 'ಶುಭ ಸಂಜೆ',
                'thank you': 'ಧನ್ಯವಾದ',
                'please': 'ದಯವಿಟ್ಟು',
                'yes': 'ಹೌದು',
                'no': 'ಇಲ್ಲ',
                'how are you': 'ನೀವು ಹೇಗಿದ್ದೀರಿ',
                'goodbye': 'ವಿದಾಯ',
                'welcome': 'ಸ್ವಾಗತ',
            },
            'en_bn': {
                'hello': 'হ্যালো',
                'good morning': 'সুপ্রভাত',
                'good evening': 'শুভ সন্ধ্যা',
                'thank you': 'ধন্যবাদ',
                'please': 'দয়া করে',
                'yes': 'হ্যাঁ',
                'no': 'না',
                'how are you': 'তুমি কেমন আছো',
                'goodbye': 'বিদায়',
                'welcome': 'স্বাগতম',
            },
            'en_es': {
                'hello': 'hola',
                'good morning': 'buenos días',
                'good evening': 'buenas noches',
                'thank you': 'gracias',
                'please': 'por favor',
                'yes': 'sí',
                'no': 'no',
                'how are you': 'cómo estás',
                'goodbye': 'adiós',
                'welcome': 'bienvenido',
            },
            'en_fr': {
                'hello': 'bonjour',
                'good morning': 'bonjour',
                'good evening': 'bonsoir',
                'thank you': 'merci',
                'please': "s'il vous plaît",
                'yes': 'oui',
                'no': 'non',
                'how are you': 'comment allez-vous',
                'goodbye': 'au revoir',
                'welcome': 'bienvenue',
            },
        }
    
    def _initialize_google_translate(self):
        try:
            from google.cloud import translate_v2 as translate
            self.translate_client = translate.Client()
            logger.info("Google Translate API initialized successfully")
        except ImportError:
            logger.warning("Google Translate library not installed. Install with: pip install google-cloud-translate")
            self.use_google_api = False
        except Exception as e:
            logger.error(f"Failed to initialize Google Translate API: {str(e)}")
            self.use_google_api = False
    
    def translate(
        self,
        text: str,
        target_lang: str,
        source_lang: Optional[str] = None
    ) -> str:
        if self.use_google_api:
            return self._translate_with_google(text, target_lang, source_lang)
        else:
            return self._translate_with_mock(text, target_lang, source_lang)
    
    def _translate_with_google(
        self,
        text: str,
        target_lang: str,
        source_lang: Optional[str] = None
    ) -> str:
        try:
            if source_lang:
                result = self.translate_client.translate(
                    text,
                    target_language=target_lang,
                    source_language=source_lang
                )
            else:
                result = self.translate_client.translate(
                    text,
                    target_language=target_lang
                )
            
            return result['translatedText']
        except Exception as e:
            logger.error(f"Google Translate API error: {str(e)}")
            raise Exception(f"Translation failed: {str(e)}")
    
    def _translate_with_mock(
        self,
        text: str,
        target_lang: str,
        source_lang: Optional[str] = None
    ) -> str:
        #Default source language to English if not specified
        source = source_lang or 'en'
        
        dict_key = f"{source}_{target_lang}"
        
        if dict_key not in self.mock_translations:
            #Return a formatted response indicating mock translation
            return f"[MOCK-{target_lang.upper()}] {text}"
        
        text_lower = text.lower().strip()
        translation_dict = self.mock_translations[dict_key]
        
        if text_lower in translation_dict:
            return translation_dict[text_lower]
        
        words = text_lower.split()
        translated_words = []
        
        for word in words:
            clean_word = word.strip('.,!?;:')
            if clean_word in translation_dict:
                translated_words.append(translation_dict[clean_word])
            else:
                translated_words.append(word)
        
        if any(w in translation_dict for w in [w.strip('.,!?;:') for w in words]):
            return ' '.join(translated_words)
        
        return f"[MOCK-{target_lang.upper()}] {text}"
    
    def get_supported_languages(self) -> Dict:
        """Get list of supported languages"""
        if self.use_google_api:
            try:
                results = self.translate_client.get_languages()
                return {lang['language']: lang['name'] for lang in results}
            except Exception as e:
                logger.error(f"Failed to get supported languages: {str(e)}")

        return {
            'en': 'English',
            'ta': 'Tamil',
            'hi': 'Hindi',
            'kn': 'Kannada',
            'bn': 'Bengali',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'ja': 'Japanese',
            'zh': 'Chinese',
            'ar': 'Arabic',
            'ko': 'Korean',
        }