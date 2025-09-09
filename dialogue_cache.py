class DialogueCache:
    """
    คลาสสำหรับจัดการข้อมูล cache ของบทสนทนา การแปลชื่อตัวละคร และรูปแบบการพูด
    """

    def __init__(self):
        self.name_history = []  # เก็บประวัติชื่อที่ validate แล้ว
        self.last_speaker = None  # เก็บชื่อล่าสุดที่ validate แล้ว
        self.MAX_HISTORY = 5
        self.session_speakers = []
        self.name_translations = {}
        self.speaker_styles = {}  # เก็บรูปแบบการพูดของตัวละคร
        
        # *** OPTIMIZED CACHING FOR THAI OCR (Expert Validated) ***
        self.translation_cache = {}  # เก็บการแปลที่สมบูรณ์
        self.cache_timestamps = {}   # เก็บเวลาที่แคช
        self.cache_hit_count = {}    # NEW: Track usage frequency
        self.MAX_CACHE_SIZE = 75     # Reduced from 100 (expert recommendation)
        self.CACHE_TTL = 600         # Extended to 10 minutes (expert recommendation)
        self.high_priority_speakers = set()  # NEW: Important characters cache

    def add_validated_name(self, name):
        """เพิ่มชื่อที่ผ่านการ validate แล้วเท่านั้น"""
        if name and name != self.last_speaker:
            self.last_speaker = name
            if name not in self.name_history:
                self.name_history.append(name)
                if len(self.name_history) > self.MAX_HISTORY:
                    self.name_history.pop(0)

    def add_speaker(self, speaker_name, translated_name=None):
        """เพิ่มชื่อผู้พูดในเซสชั่น"""
        if speaker_name:
            if speaker_name not in self.session_speakers:
                self.session_speakers.append(speaker_name)
            self.last_speaker = speaker_name
            if translated_name:
                self.name_translations[speaker_name] = translated_name

    def get_speaker_translation(self, speaker_name):
        """ดึงการแปลชื่อที่เคยแปลไว้"""
        return self.name_translations.get(speaker_name)

    def get_last_speaker(self):
        """ดึงชื่อล่าสุดที่ validate แล้ว"""
        return self.last_speaker

    def get_recent_names(self):
        """ดึงประวัติชื่อที่ validate แล้ว"""
        return self.name_history

    def get_speaker_style(self, speaker_name):
        """ดึงรูปแบบการพูดของตัวละคร"""
        return self.speaker_styles.get(speaker_name, "")

    def set_speaker_style(self, speaker_name, style):
        """กำหนดรูปแบบการพูดของตัวละคร"""
        if speaker_name:
            self.speaker_styles[speaker_name] = style

    def clear(self):
        """ล้าง cache"""
        self.name_history.clear()
        self.last_speaker = None

    def clear_session(self):
        """ล้างข้อมูลเซสชั่น"""
        self.session_speakers.clear()
        self.name_translations.clear()
        self.speaker_styles.clear()
        self.last_speaker = None
        self.cache_hit_count.clear()
        self.translation_cache.clear()
        self.cache_timestamps.clear()

    def get_cache_key(self, original_text, speaker_name=None, dialogue_type=None):
        """สร้าง cache key สำหรับการแปล"""
        import hashlib
        
        # สร้าง key จาก text + speaker + type
        key_parts = [original_text]
        if speaker_name:
            key_parts.append(f"speaker:{speaker_name}")
        if dialogue_type:
            key_parts.append(f"type:{dialogue_type}")
        
        key_string = "|".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()

    def get_cached_translation(self, original_text, speaker_name=None, dialogue_type=None):
        """ดึงการแปลที่แคชไว้"""
        try:
            import time
            cache_key = self.get_cache_key(original_text, speaker_name, dialogue_type)
            
            if cache_key not in self.translation_cache:
                return None
            
            # Check TTL (optimized to avoid repeated time.time() calls)
            current_time = time.time()
            cached_time = self.cache_timestamps.get(cache_key, 0)
            if current_time - cached_time > self.CACHE_TTL:
                # Expired - remove
                self.translation_cache.pop(cache_key, None)
                self.cache_timestamps.pop(cache_key, None)
                self.cache_hit_count.pop(cache_key, None)  # NEW: Clean hit count
                return None

            # NEW: Increment hit count for smart eviction
            self.cache_hit_count[cache_key] = self.cache_hit_count.get(cache_key, 0) + 1
            
            return self.translation_cache[cache_key]
        except:
            return None

    def cache_translation(self, original_text, translated_text, speaker_name=None, dialogue_type=None):
        """เก็บการแปลลง cache"""
        try:
            import time
            
            # ทำความสะอาด cache ถ้าเต็ม
            # Use smart cleanup instead
            if len(self.translation_cache) >= self.MAX_CACHE_SIZE:
                self._smart_cleanup_cache()
            
            cache_key = self.get_cache_key(original_text, speaker_name, dialogue_type)
            self.translation_cache[cache_key] = translated_text
            self.cache_timestamps[cache_key] = time.time()
            self.cache_hit_count[cache_key] = 1  # NEW: Initialize hit count
        except:
            pass

    def _smart_cleanup_cache(self):
        """Smart cache cleanup prioritizing frequently used translations"""
        try:
            import time
            # Clean expired entries first
            current_time = time.time()
            expired_keys = []
            for key, timestamp in self.cache_timestamps.items():
                if current_time - timestamp > self.CACHE_TTL:
                    expired_keys.append(key)
            
            # Remove expired entries
            for key in expired_keys:
                self.translation_cache.pop(key, None)
                self.cache_timestamps.pop(key, None)
                self.cache_hit_count.pop(key, None)
            
            # If still over limit, remove least frequently used
            if len(self.translation_cache) >= self.MAX_CACHE_SIZE:
                # Sort by hit count (ascending) - remove low-hit entries
                sorted_keys = sorted(
                    self.cache_hit_count.keys(), 
                    key=lambda k: self.cache_hit_count.get(k, 0)
                )
                
                # Remove bottom 25% of entries
                keys_to_remove = sorted_keys[:self.MAX_CACHE_SIZE // 4]
                for key in keys_to_remove:
                    self.translation_cache.pop(key, None)
                    self.cache_timestamps.pop(key, None)
                    self.cache_hit_count.pop(key, None)
                    
        except Exception as e:
            # Fallback to simple cleanup if smart cleanup fails
            keys_to_remove = list(self.translation_cache.keys())[:10]
            for key in keys_to_remove:
                self.translation_cache.pop(key, None)
                self.cache_timestamps.pop(key, None)
                self.cache_hit_count.pop(key, None)

    def get_cache_stats(self):
        """Enhanced cache statistics for monitoring"""
        total_hits = sum(self.cache_hit_count.values())
        avg_hits = total_hits / len(self.cache_hit_count) if self.cache_hit_count else 0
        
        return {
            'cache_size': len(self.translation_cache),
            'max_size': self.MAX_CACHE_SIZE,
            'ttl_seconds': self.CACHE_TTL,
            'total_hits': total_hits,
            'avg_hits_per_entry': avg_hits,
            'high_priority_speakers': len(self.high_priority_speakers)
        }

    def add_high_priority_speaker(self, speaker_name):
        """Mark speaker as high priority (WoL, main NPCs)"""
        if speaker_name:
            self.high_priority_speakers.add(speaker_name)

    def is_high_priority_speaker(self, speaker_name):
        """Check if speaker should have priority in cache"""
        return speaker_name in self.high_priority_speakers
