"""
Cutscene Text Processor
จัดการการแยกชื่อตัวละครและข้อความจาก cutscene
"""

import re
import time
import logging
from typing import Dict, Optional, Tuple


class CutsceneTextProcessor:
    """
    ประมวลผลข้อความจาก OCR สำหรับ cutscene
    แยกชื่อตัวละครและบทพูดออกจากกัน
    """
    
    def __init__(self):
        # UI keywords ที่ไม่ควรเป็นชื่อตัวละคร
        self.ui_keywords = {
            'next', 'skip', 'menu', 'close', 'back', 'auto', 
            'log', 'save', 'load', 'config', 'exit', 'cancel',
            'yes', 'no', 'ok', 'confirm'
        }
        
        # Common false positives
        self.false_positives = {
            'chapter', 'scene', 'act', 'part', 'episode',
            'location', 'time', 'date', 'day', 'night'
        }
        
        logging.info("CutsceneTextProcessor initialized")
    
    def process_ocr_text(self, ocr_text: str) -> Dict:
        """
        แยกชื่อและข้อความจาก OCR result
        
        Args:
            ocr_text: ข้อความจาก OCR
            
        Returns:
            dict: {
                'type': 'cutscene_with_speaker' | 'narration',
                'speaker': str or None,
                'content': str,
                'confidence': float
            }
        """
        if not ocr_text or not ocr_text.strip():
            return {
                'type': 'empty',
                'content': '',
                'confidence': 0.0
            }
        
        # ทำความสะอาดข้อความ
        cleaned_text = self._clean_text(ocr_text)
        lines = cleaned_text.split('\n')
        
        # กรณีมีหลายบรรทัด
        if len(lines) >= 2:
            potential_name = lines[0].strip()
            content_lines = [line.strip() for line in lines[1:] if line.strip()]
            content = ' '.join(content_lines)
            
            # ตรวจสอบว่าบรรทัดแรกน่าจะเป็นชื่อ
            name_validation = self._validate_speaker_name(potential_name)
            
            if name_validation['is_valid']:
                return {
                    'type': 'cutscene_with_speaker',
                    'speaker': potential_name,
                    'content': content,
                    'confidence': name_validation['confidence']
                }
        
        # กรณีบรรทัดเดียว หรือไม่พบชื่อ
        return {
            'type': 'narration',
            'speaker': None,
            'content': cleaned_text.replace('\n', ' '),
            'confidence': 0.8
        }
    
    def _clean_text(self, text: str) -> str:
        """
        ทำความสะอาดข้อความ OCR
        """
        # ลบ whitespace ที่ไม่จำเป็น
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # แทนที่ multiple spaces ด้วย single space
        text = re.sub(r' {2,}', ' ', text)
        
        # คืนค่า newlines ที่สำคัญกลับมา
        # (OCR มักจะแยกชื่อกับข้อความด้วย newline)
        text = re.sub(r'([A-Za-z\']+)\s+([A-Z][a-z])', r'\1\n\2', text)
        
        return text
    
    def _validate_speaker_name(self, text: str) -> Dict:
        """
        ตรวจสอบว่าข้อความน่าจะเป็นชื่อตัวละคร
        
        Returns:
            dict: {
                'is_valid': bool,
                'confidence': float (0.0-1.0)
            }
        """
        confidence = 1.0
        
        # 1. ความยาวต้องเหมาะสม (2-30 ตัวอักษร)
        if len(text) < 2:
            return {'is_valid': False, 'confidence': 0.0}
        if len(text) > 30:
            confidence *= 0.7
        
        # 2. ต้องขึ้นต้นด้วยตัวใหญ่
        if not text[0].isupper():
            return {'is_valid': False, 'confidence': 0.0}
        
        # 3. ตรวจสอบ UI keywords
        if text.lower() in self.ui_keywords:
            return {'is_valid': False, 'confidence': 0.0}
        
        # 4. ตรวจสอบ false positives
        if text.lower() in self.false_positives:
            return {'is_valid': False, 'confidence': 0.0}
        
        # 5. ตรวจสอบอักขระ
        # อนุญาต: ตัวอักษร, space, apostrophe, hyphen
        if not re.match(r"^[A-Za-z\s'\-]+$", text):
            confidence *= 0.5
        
        # 6. ตรวจสอบรูปแบบชื่อ
        # ชื่อปกติมักมี 1-3 คำ
        word_count = len(text.split())
        if word_count > 4:
            confidence *= 0.6
        elif word_count == 1:
            confidence *= 0.95  # ชื่อคำเดียวก็เป็นไปได้
        
        # 7. ตรวจสอบว่าไม่ใช่ประโยค
        # ประโยคมักมี verb หรือ preposition
        common_words = {'is', 'are', 'was', 'were', 'the', 'a', 'an', 'in', 'on', 'at'}
        words = set(text.lower().split())
        if words.intersection(common_words):
            confidence *= 0.3
        
        # 8. ตรวจสอบตัวเลข
        if any(char.isdigit() for char in text):
            # อนุญาตตัวเลขบางกรณี เช่น "2B", "9S"
            if re.match(r'^[A-Za-z0-9]{1,3}$', text):
                confidence *= 0.9
            else:
                confidence *= 0.4
        
        is_valid = confidence >= 0.5
        return {'is_valid': is_valid, 'confidence': confidence}
    
    def extract_speaker_from_line(self, text: str) -> Optional[Tuple[str, str]]:
        """
        พยายามแยกชื่อผู้พูดจากบรรทัดเดียว
        สำหรับกรณี "Name: dialogue" หรือ "Name - dialogue"
        
        Returns:
            tuple: (speaker, content) หรือ None
        """
        # Pattern 1: "Name: dialogue"
        match = re.match(r'^([A-Z][A-Za-z\s\']+)[:：]\s*(.+)', text)
        if match:
            speaker = match.group(1).strip()
            content = match.group(2).strip()
            validation = self._validate_speaker_name(speaker)
            if validation['is_valid']:
                return (speaker, content)
        
        # Pattern 2: "Name - dialogue"
        match = re.match(r'^([A-Z][A-Za-z\s\']+)\s*[-–—]\s*(.+)', text)
        if match:
            speaker = match.group(1).strip()
            content = match.group(2).strip()
            validation = self._validate_speaker_name(speaker)
            if validation['is_valid']:
                return (speaker, content)
        
        return None


class SessionSpeakerCache:
    """
    เก็บข้อมูลชื่อตัวละครที่พบในเซสชั่นปัจจุบัน
    """
    
    def __init__(self, max_speakers: int = 50):
        self.speakers = {}
        self.max_speakers = max_speakers
        self.creation_order = []
        
    def add_speaker(self, name: str) -> None:
        """เพิ่มชื่อผู้พูดใหม่"""
        if name in self.speakers:
            self.speakers[name]['count'] += 1
            self.speakers[name]['last_seen'] = time.time()
        else:
            # ถ้าเต็มแล้ว ลบตัวเก่าสุดออก
            if len(self.speakers) >= self.max_speakers and self.creation_order:
                oldest = self.creation_order.pop(0)
                del self.speakers[oldest]
            
            self.speakers[name] = {
                'first_seen': time.time(),
                'last_seen': time.time(),
                'count': 1
            }
            self.creation_order.append(name)
    
    def get_speaker_info(self, name: str) -> Optional[Dict]:
        """ดึงข้อมูลผู้พูด"""
        return self.speakers.get(name)
    
    def is_known_speaker(self, name: str) -> bool:
        """ตรวจสอบว่าเคยเจอชื่อนี้หรือไม่"""
        return name in self.speakers
    
    def get_frequency(self, name: str) -> int:
        """ดึงความถี่การปรากฏของชื่อ"""
        if name in self.speakers:
            return self.speakers[name]['count']
        return 0
    
    def clear(self) -> None:
        """ล้าง cache"""
        self.speakers.clear()
        self.creation_order.clear()


# Test functions
if __name__ == "__main__":
    # ทดสอบ processor
    processor = CutsceneTextProcessor()
    
    # Test cases จากภาพตัวอย่าง
    test_cases = [
        "Hexga\nAaah... the bliss.",
        "Sciel\nSave it for tomorrow. Let's do something else tonight.",
        "Verso\nWhat do you have in mind?",
        "Next\nThis should not be detected as name",
        "The ancient ruins stretch endlessly...",
        "Y'shtola: The aether here is unstable."
    ]
    
    print("=== Cutscene Text Processor Test ===\n")
    
    for i, test in enumerate(test_cases, 1):
        print(f"Test {i}:")
        print(f"Input: {repr(test)}")
        result = processor.process_ocr_text(test)
        print(f"Result: {result}")
        print("-" * 50)