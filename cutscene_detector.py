"""
Cutscene Detection Module for MBB
ตรวจจับและแยกชื่อ+ข้อความจาก cutscene text
"""

import re
import logging
from typing import Optional, Dict, Tuple

class CutsceneDetector:
    def __init__(self):
        # Patterns สำหรับตรวจจับ cutscene text
        self.cutscene_patterns = [
            # Pattern 1: ชื่อบรรทัดแรก, ข้อความบรรทัดถัดไป
            (r'^([A-Z][a-zA-Z\s\']{1,30})$\n+(.+)', 'newline_format'),
            
            # Pattern 2: ชื่อ: ข้อความ (format เดียวบรรทัด)
            (r'^([A-Z][a-zA-Z\s\']+)[:：]\s*(.+)', 'colon_format'),
            
            # Pattern 3: [ชื่อ] ข้อความ
            (r'^\[([A-Z][a-zA-Z\s\']+)\]\s*(.+)', 'bracket_format'),
            
            # Pattern 4: ชื่อ - ข้อความ
            (r'^([A-Z][a-zA-Z\s\']+)\s*[-–—]\s*(.+)', 'dash_format')
        ]
        
        # Character validation patterns
        self.name_validation = {
            'min_length': 2,
            'max_length': 30,
            'invalid_chars': r'[0-9!@#$%^&*()+=\[\]{};"|<>?/\\]',
            'valid_chars': r'^[A-Za-z\s\'\-]+$'
        }
        
    def detect_cutscene(self, ocr_text: str) -> Optional[Dict]:
        """
        ตรวจจับว่า text เป็น cutscene format หรือไม่
        
        Returns:
            {
                'type': 'cutscene',
                'format': 'newline_format',
                'speaker': 'Character Name',
                'content': 'Dialog text',
                'confidence': 0.95
            }
        """
        if not ocr_text or not ocr_text.strip():
            return None
            
        # Clean text
        text = ocr_text.strip()
        
        # Try each pattern
        for pattern, format_type in self.cutscene_patterns:
            match = re.match(pattern, text, re.MULTILINE | re.DOTALL)
            if match:
                speaker = match.group(1).strip()
                content = match.group(2).strip()
                
                # Validate speaker name
                if self._is_valid_speaker_name(speaker):
                    confidence = self._calculate_confidence(speaker, content, format_type)
                    
                    return {
                        'type': 'cutscene',
                        'format': format_type,
                        'speaker': speaker,
                        'content': content,
                        'confidence': confidence
                    }
        
        # ถ้าไม่ match pattern ใดเลย อาจเป็น narration/lore text
        return None
    
    def _is_valid_speaker_name(self, name: str) -> bool:
        """ตรวจสอบว่าชื่อน่าเชื่อถือหรือไม่"""
        # ความยาว
        if len(name) < self.name_validation['min_length'] or \
           len(name) > self.name_validation['max_length']:
            return False
        
        # ต้องขึ้นต้นด้วยตัวใหญ่
        if not name[0].isupper():
            return False
        
        # ไม่มีอักขระแปลกๆ
        if re.search(self.name_validation['invalid_chars'], name):
            return False
        
        # ตรวจสอบว่ามีแต่ตัวอักษร, space, apostrophe, hyphen
        if not re.match(self.name_validation['valid_chars'], name):
            return False
        
        # ไม่ใช่คำทั่วไปที่อาจเป็น false positive
        common_words = ['The', 'This', 'That', 'There', 'These', 'Those', 
                       'What', 'Where', 'When', 'Who', 'Why', 'How']
        if name in common_words:
            return False
        
        return True
    
    def _calculate_confidence(self, speaker: str, content: str, format_type: str) -> float:
        """คำนวณความมั่นใจในการตรวจจับ"""
        confidence = 0.7  # Base confidence
        
        # Format confidence boost
        format_scores = {
            'newline_format': 0.15,  # Most common in cutscenes
            'colon_format': 0.1,
            'bracket_format': 0.05,
            'dash_format': 0.05
        }
        confidence += format_scores.get(format_type, 0)
        
        # Speaker name quality
        if len(speaker) >= 3 and len(speaker) <= 20:
            confidence += 0.05
        
        # Content quality (ต้องมีความยาวพอสมควร)
        if len(content) >= 10:
            confidence += 0.05
        
        # Has proper punctuation
        if any(content.endswith(p) for p in ['.', '!', '?', '...', '。']):
            confidence += 0.05
        
        return min(confidence, 1.0)
    
    def split_mixed_text(self, text: str) -> Tuple[Optional[str], str]:
        """
        แยกข้อความที่อาจมีชื่อปนกับเนื้อหา
        ใช้ในกรณีที่ OCR อ่านมาติดกัน
        
        Returns:
            (speaker_name, content) หรือ (None, full_text)
        """
        # Try to find speaker pattern at the beginning
        for pattern, _ in self.cutscene_patterns[:3]:  # Skip dash format
            # Modify pattern to not require end of string
            modified_pattern = pattern.replace('$', '')
            match = re.match(modified_pattern, text)
            if match:
                speaker = match.group(1).strip()
                if self._is_valid_speaker_name(speaker):
                    # Extract content after speaker
                    content_start = match.end(1)
                    content = text[content_start:].strip()
                    # Remove separators
                    content = re.sub(r'^[:：\-–—\s]+', '', content)
                    return speaker, content
        
        return None, text


# ตัวอย่างการใช้งาน
if __name__ == "__main__":
    detector = CutsceneDetector()
    
    # Test cases จากภาพตัวอย่าง
    test_cases = [
        "Hexga\nAaah... the bliss.",
        "Sciel\nSave it for tomorrow. Let's do something else tonight.",
        "Verso\nWhat do you have in mind?",
        "This is just normal text without speaker",
        "Y'shtola: The aether here is unstable...",
        "[Alphinaud] We must proceed with caution."
    ]
    
    for text in test_cases:
        result = detector.detect_cutscene(text)
        if result:
            print(f"✓ Detected: {result['speaker']} -> {result['content'][:30]}...")
            print(f"  Format: {result['format']}, Confidence: {result['confidence']}")
        else:
            print(f"✗ Not a cutscene: {text[:50]}...")
        print()
