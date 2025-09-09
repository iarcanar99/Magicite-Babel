"""
Enhanced NPC Checker for Cutscene Support
ตรวจสอบและจัดการชื่อตัวละครสำหรับ cutscene
"""

import time
import logging
from typing import Dict, Optional, List
from difflib import SequenceMatcher

class EnhancedNPCChecker:
    def __init__(self, npc_manager):
        self.npc_manager = npc_manager
        self.temp_speakers = {}  # เก็บชื่อใหม่ชั่วคราว
        self.speaker_history = []  # ประวัติการใช้ชื่อ
        self.max_history = 50
        
    def check_speaker(self, speaker_name: str) -> Dict:
        """
        ตรวจสอบชื่อผู้พูดกับฐานข้อมูล
        
        Returns:
            {
                'found': True/False,
                'source': 'npc_database'/'temp_cache'/'new_speaker',
                'display_color': 'white'/'blue',
                'confidence': 0.0-1.0,
                'npc_data': {...} หรือ None
            }
        """
        # 1. ตรวจสอบใน NPC.json ก่อน (exact match)
        npc_data = self.npc_manager.find_character(speaker_name)
        if npc_data:
            self._add_to_history(speaker_name, 'npc_database')
            return {
                'found': True,
                'source': 'npc_database',
                'display_color': 'white',
                'confidence': 1.0,
                'npc_data': npc_data
            }
        
        # 2. ตรวจสอบ fuzzy match กับ NPC database
        fuzzy_match = self._fuzzy_find_character(speaker_name)
        if fuzzy_match and fuzzy_match['similarity'] >= 0.85:
            self._add_to_history(fuzzy_match['name'], 'npc_database')
            return {
                'found': True,
                'source': 'npc_database',
                'display_color': 'white',
                'confidence': fuzzy_match['similarity'],
                'npc_data': fuzzy_match['data'],
                'matched_name': fuzzy_match['name']
            }
        
        # 3. ตรวจสอบใน temp cache
        if speaker_name in self.temp_speakers:
            self.temp_speakers[speaker_name]['count'] += 1
            self.temp_speakers[speaker_name]['last_seen'] = time.time()
            self._add_to_history(speaker_name, 'temp_cache')
            
            return {
                'found': True,
                'source': 'temp_cache',
                'display_color': 'blue',
                'confidence': min(0.7 + (self.temp_speakers[speaker_name]['count'] * 0.05), 0.95),
                'npc_data': None
            }
        
        # 4. เพิ่มเป็นชื่อใหม่
        self.temp_speakers[speaker_name] = {
            'first_seen': time.time(),
            'last_seen': time.time(),
            'count': 1
        }
        self._add_to_history(speaker_name, 'new_speaker')
        
        return {
            'found': True,
            'source': 'new_speaker',
            'display_color': 'blue',
            'confidence': 0.7,
            'npc_data': None
        }
    
    def _fuzzy_find_character(self, name: str) -> Optional[Dict]:
        """ค้นหาชื่อที่คล้ายกันใน NPC database"""
        best_match = None
        best_similarity = 0.0
        
        # ดึงรายชื่อทั้งหมดจาก NPC database
        all_characters = self.npc_manager.get_all_characters()
        
        for char in all_characters:
            # Check firstName
            if char.get('firstName'):
                similarity = SequenceMatcher(None, name.lower(), char['firstName'].lower()).ratio()
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = {
                        'name': char['firstName'],
                        'data': char,
                        'similarity': similarity
                    }
            
            # Check lastName if exists
            if char.get('lastName'):
                full_name = f"{char['firstName']} {char['lastName']}"
                similarity = SequenceMatcher(None, name.lower(), full_name.lower()).ratio()
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = {
                        'name': full_name,
                        'data': char,
                        'similarity': similarity
                    }
        
        return best_match if best_similarity >= 0.7 else None
    
    def _add_to_history(self, speaker_name: str, source: str):
        """เพิ่มประวัติการใช้ชื่อ"""
        self.speaker_history.append({
            'name': speaker_name,
            'source': source,
            'timestamp': time.time()
        })
        
        # จำกัดขนาด history
        if len(self.speaker_history) > self.max_history:
            self.speaker_history.pop(0)
    
    def get_recent_speakers(self, limit: int = 10) -> List[str]:
        """ดึงรายชื่อผู้พูดล่าสุด"""
        seen = set()
        recent = []
        
        for entry in reversed(self.speaker_history):
            if entry['name'] not in seen:
                seen.add(entry['name'])
                recent.append(entry['name'])
                if len(recent) >= limit:
                    break
        
        return recent
    
    def get_speaker_stats(self) -> Dict:
        """ดึงสถิติการใช้ชื่อ"""
        stats = {
            'total_speakers': len(self.temp_speakers) + len(set(h['name'] for h in self.speaker_history if h['source'] == 'npc_database')),
            'new_speakers': len(self.temp_speakers),
            'known_speakers': len(set(h['name'] for h in self.speaker_history if h['source'] == 'npc_database')),
            'total_dialogs': len(self.speaker_history)
        }
        return stats
    
    def suggest_speaker_for_save(self) -> List[Dict]:
        """แนะนำชื่อใหม่ที่ควรบันทึกลง NPC.json"""
        suggestions = []
        
        for name, data in self.temp_speakers.items():
            if data['count'] >= 3:  # ใช้มากกว่า 3 ครั้ง
                suggestions.append({
                    'name': name,
                    'count': data['count'],
                    'first_seen': data['first_seen'],
                    'confidence': min(0.7 + (data['count'] * 0.05), 1.0)
                })
        
        # เรียงตามจำนวนการใช้
        suggestions.sort(key=lambda x: x['count'], reverse=True)
        return suggestions
