'''Purpose: Validates and sanitizes all incoming data
What it does:

Validates language codes (ISO 639-1 format)
Checks text length limits
Sanitizes user input
Validates bulk requests'''

import re
from typing import Set


#list of ISO 639-1 language codes
SUPPORTED_LANGUAGE_CODES: Set[str] = {
    'aa', 'ab', 'ae', 'af', 'ak', 'am', 'an', 'ar', 'as', 'av', 'ay', 'az',
    'ba', 'be', 'bg', 'bh', 'bi', 'bm', 'bn', 'bo', 'br', 'bs',
    'ca', 'ce', 'ch', 'co', 'cr', 'cs', 'cu', 'cv', 'cy',
    'da', 'de', 'dv', 'dz',
    'ee', 'el', 'en', 'eo', 'es', 'et', 'eu',
    'fa', 'ff', 'fi', 'fj', 'fo', 'fr', 'fy',
    'ga', 'gd', 'gl', 'gn', 'gu', 'gv',
    'ha', 'he', 'hi', 'ho', 'hr', 'ht', 'hu', 'hy', 'hz',
    'ia', 'id', 'ie', 'ig', 'ii', 'ik', 'io', 'is', 'it', 'iu',
    'ja', 'jv',
    'ka', 'kg', 'ki', 'kj', 'kk', 'kl', 'km', 'kn', 'ko', 'kr', 'ks', 'ku', 'kv', 'kw', 'ky',
    'la', 'lb', 'lg', 'li', 'ln', 'lo', 'lt', 'lu', 'lv',
    'mg', 'mh', 'mi', 'mk', 'ml', 'mn', 'mr', 'ms', 'mt', 'my',
    'na', 'nb', 'nd', 'ne', 'ng', 'nl', 'nn', 'no', 'nr', 'nv', 'ny',
    'oc', 'oj', 'om', 'or', 'os',
    'pa', 'pi', 'pl', 'ps', 'pt',
    'qu',
    'rm', 'rn', 'ro', 'ru', 'rw',
    'sa', 'sc', 'sd', 'se', 'sg', 'si', 'sk', 'sl', 'sm', 'sn', 'so', 'sq', 'sr', 'ss', 'st', 'su', 'sv', 'sw',
    'ta', 'te', 'tg', 'th', 'ti', 'tk', 'tl', 'tn', 'to', 'tr', 'ts', 'tt', 'tw', 'ty',
    'ug', 'uk', 'ur', 'uz',
    've', 'vi', 'vo',
    'wa', 'wo',
    'xh',
    'yi', 'yo',
    'za', 'zh', 'zu',
    'zh-cn', 'zh-tw'
}


def validate_language_code(lang_code: str) -> bool:
    if not lang_code:
        raise ValueError("Language code cannot be empty")
    
    lang_code = lang_code.lower().strip()
    
    if not re.match(r'^[a-z]{2}(-[a-z]{2})?$', lang_code):
        raise ValueError(
            f"Invalid language code format: '{lang_code}'. "
            "Must be 2 lowercase letters (e.g., 'en', 'ta') or "
            "2 lowercase letters followed by hyphen and 2 more letters (e.g., 'zh-cn')"
        )
    
    if lang_code not in SUPPORTED_LANGUAGE_CODES:
        raise ValueError(
            f"Unsupported language code: '{lang_code}'. "
            "Please use a valid ISO 639-1 language code."
        )
    
    return True


def validate_text_length(text: str, max_length: int = 1000) -> bool:
    if not text:
        raise ValueError("Text cannot be empty")
    
    if not text.strip():
        raise ValueError("Text cannot be only whitespace")
    
    if len(text) > max_length:
        raise ValueError(
            f"Text too long: {len(text)} characters. "
            f"Maximum allowed: {max_length} characters"
        )
    
    return True


def sanitize_text(text: str) -> str:
    text = text.replace('\x00', '')

    text = re.sub(r'\s+', ' ', text)
    
    text = text.strip()
    
    return text


def is_valid_bulk_request(texts: list, max_items: int = 50) -> bool:
    if not texts:
        raise ValueError("Texts list cannot be empty")
    
    if not isinstance(texts, list):
        raise ValueError("Texts must be a list")
    
    if len(texts) > max_items:
        raise ValueError(
            f"Too many texts: {len(texts)}. "
            f"Maximum allowed: {max_items} texts per request"
        )
    
    non_empty_count = 0
    for i, text in enumerate(texts):
        if not isinstance(text, str):
            raise ValueError(f"Item at index {i} is not a string")
        
        if text.strip():
            non_empty_count += 1
    
    if non_empty_count == 0:
        raise ValueError("At least one non-empty text is required")
    
    return True