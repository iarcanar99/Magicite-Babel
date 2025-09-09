# -*- coding: utf-8 -*-
"""
Language Restriction Module for MBB v9
Ensures only English -> Thai translation is allowed
"""

import logging
import re


def detect_non_english_text(text):
    """
    Detect if text contains mostly non-English characters
    
    Args:
        text (str): Input text to analyze
        
    Returns:
        bool: True if text appears to be non-English
    """
    if not text or len(text.strip()) < 3:
        return False
        
    # Remove common game symbols and punctuation
    clean_text = re.sub(r'[.,!?:;"\'()\[\]{}\-_=+*/\\|`~@#$%^&]', '', text)
    clean_text = re.sub(r'\s+', '', clean_text)
    
    if len(clean_text) == 0:
        return False
    
    # Count English characters (a-z, A-Z, 0-9)
    english_chars = sum(1 for c in clean_text if c.isalnum() and ord(c) < 128)
    total_chars = len(clean_text)
    
    # Calculate English ratio
    english_ratio = english_chars / total_chars if total_chars > 0 else 0
    
    # Log detection for debugging
    if english_ratio < 0.7:
        logging.debug(f"Non-English text detected: {english_ratio:.2%} English characters in: {text[:30]}...")
        
    # If less than 70% English characters, consider it non-English
    return english_ratio < 0.7


def validate_translation_languages(source_lang, target_lang):
    """
    Validate that translation is only English -> Thai
    
    Args:
        source_lang (str): Source language
        target_lang (str): Target language
        
    Returns:
        tuple: (is_valid, error_message)
    """
    source = source_lang.lower().strip()
    target = target_lang.lower().strip()
    
    # Only allow English -> Thai
    if source != "english" or target != "thai":
        error_msg = f"Only English -> Thai translation supported. Requested: {source_lang} -> {target_lang}"
        logging.warning(f"Translation blocked: {error_msg}")
        return False, error_msg
        
    return True, None


def validate_input_text(text):
    """
    Validate that input text is suitable for English -> Thai translation
    
    Args:
        text (str): Input text
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not text or not text.strip():
        return False, "Empty text provided"
    
    # Check for non-English content
    if detect_non_english_text(text):
        error_msg = "Input text must be in English only"
        logging.warning(f"Translation blocked: {error_msg}. Text: {text[:50]}...")
        return False, error_msg
    
    # Check for suspicious patterns (Thai, Chinese, Japanese, etc.)
    suspicious_patterns = [
        r'[\u0E00-\u0E7F]',  # Thai
        r'[\u4E00-\u9FFF]',  # Chinese
        r'[\u3040-\u309F]',  # Hiragana
        r'[\u30A0-\u30FF]',  # Katakana
        r'[\u3400-\u4DBF]',  # CJK Extension A
    ]
    
    for pattern in suspicious_patterns:
        if re.search(pattern, text):
            error_msg = "Input text contains non-English characters"
            logging.warning(f"Translation blocked: Non-English characters detected in: {text[:50]}...")
            return False, error_msg
    
    return True, None