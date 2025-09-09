import anthropic
import os
from dotenv import load_dotenv
import re
import tkinter as tk
from tkinter import messagebox
import json
import difflib
import time
import logging
from text_corrector import TextCorrector, DialogueType

# เพิ่มการ import EnhancedNameDetector ถ้ามี
try:
    from enhanced_name_detector import EnhancedNameDetector
    HAS_ENHANCED_DETECTOR = True
except ImportError:
    HAS_ENHANCED_DETECTOR = False

load_dotenv()


class TranslatorClaude:
    def __init__(self, settings=None):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in .env file")
        self.client = anthropic.Anthropic(api_key=self.api_key)

        # ใช้ settings object ถ้ามี
        if settings:
            api_params = settings.get_api_parameters()
            self.model = api_params.get("model", "claude-3-5-haiku-20241022")
            self.displayed_model = api_params.get("displayed_model", "claude-3.5-haiku")
            self.max_tokens = api_params.get("max_tokens", 500)
            self.temperature = api_params.get("temperature", 0.7)
            self.top_p = api_params.get("top_p", 0.9)
        else:
            # ถ้าไม่มี settings ให้ใช้ค่าเริ่มต้น
            self.model = "claude-3-5-haiku-20241022"
            self.displayed_model = "claude-3.5-haiku"
            self.max_tokens = 500
            self.temperature = 0.7
            self.top_p = 0.9

        self.character_names_cache = set()
        self.character_info_cache = {}
        self.character_data = []
        self.context_data = {}
        self.character_styles = {}
        self.character_names_cache.add("???")
        self.load_npc_data()
        self.load_example_translations()
        self.text_corrector = TextCorrector()
        self.last_translations = {}

        # ดูว่าสามารถใช้ EnhancedNameDetector ได้หรือไม่
        self.enhanced_detector = None
        if HAS_ENHANCED_DETECTOR:
            try:
                self.enhanced_detector = EnhancedNameDetector(self.character_names_cache)
                logging.info("Initialized EnhancedNameDetector successfully")
            except Exception as e:
                logging.warning(f"Failed to initialize EnhancedNameDetector: {e}")
                self.enhanced_detector = None

        print(f"[Claude API] Initialized with model: {self.displayed_model}")

    def load_npc_data(self):
        try:
            with open("NPC.json", "r", encoding="utf-8") as file:
                npc_data = json.load(file)
                self.character_data = npc_data["main_characters"]
                self.context_data = npc_data["lore"]
                self.character_styles = npc_data["character_roles"]

                # โหลด word_fixes ถ้ามี
                if "word_fixes" in npc_data:
                    self.word_fixes = npc_data["word_fixes"]
                    logging.info(f"Loaded {len(self.word_fixes)} word fixes from NPC.json")
                else:
                    self.word_fixes = {}

                # Update character_names_cache
                self.character_names_cache = set()
                self.character_names_cache.add("???")

                # Load main characters
                for char in self.character_data:
                    self.character_names_cache.add(char["firstName"])
                    if char["lastName"]:
                        self.character_names_cache.add(
                            f"{char['firstName']} {char['lastName']}"
                        )

                # Add NPCs to character_names_cache
                for npc in npc_data["npcs"]:
                    self.character_names_cache.add(npc["name"])

                print("[Claude API] Successfully loaded NPC data")
        except FileNotFoundError:
            raise FileNotFoundError("NPC.json file not found")
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON in NPC.json")

    def load_example_translations(self):
        self.example_translations = {
            "'Tis": "ช่างเป็น...",
            "'I do": "ฉันเข้าใจ",
            "'do": "ฉันเข้าใจ",
            "'Twas": "มันเคยเป็น...",
            "Nay": "หามิได้",
            "Aye": "นั่นสินะ, นั่นแหล่ะ, เป็นเช่นนั้น",
            "Mayhaps": "บางที...",
            "Hm...": "อืม...",
            "Wait!": "เดี๋ยวก่อน!",
            "My friend...": "สหายข้า...",
            "Tataru?": "Tataru เหรอ?",
            "Estinien!": "Estinien!",
            "sigh": "เฮ่อ..",
            "Hmph.": "ฮึ่ม.",
            "Y'shtola: The aetheric fluctuations in this area are most peculiar. We should proceed with caution.": "Y'shtola: ความผันผวนของพลังอีเธอร์แถบนี้... น่าพิศวงยิ่งนัก เราควรก้าวต่อไปด้วยความระมัดระวัง",
            "Alphinaud: The political implications of our actions here could be far-reaching. We must consider every possible outcome.": "Alphinaud: นัยทางการเมืองจากการกระทำของพวกเราในครั้งนี้ อาจส่งผลกระทบไปไกล เราต้องนึกถึงทุกความเป็นไปได้อย่างถี่ถ้วน",
            "Alisaie: I won't stand idly by while others risk their lives. If we're to face this threat, we do so together.": "Alisaie: ฉันจะไม่ยืนดูดายในขณะที่คนอื่นเสี่ยงชีวิต ถ้าเราต้องเผชิญหน้ากับภัยคุกคามนี้ เราก็จะสู้ไปด้วยกันนี่แหล่ะ!",
            "Urianger: Pray, let us contemplate the implications of our recent discoveries. The path ahead may yet be fraught with unforeseen perils.": "Urianger: ข้าขอวิงวอน ให้พวกเราใคร่ครวญถึงนัยสำคัญแห่งการค้นพบล่าสุดของพวกเรา หนทางเบื้องหน้าอาจเต็มไปด้วยภยันตรายอันมิอาจคาดเดา",
            "Thancred: Sometimes, you have to take risks. Calculated risks, mind you. But risks all the same.": "Thancred: บางครั้งเราก็ต้องเสี่ยงบ้างล่ะนะ เสี่ยงแบบคำนวณแล้วน่ะ แต่ก็ยังเป็นการเสี่ยงอยู่ดี",
        }
        print("[Claude API] Example translations loaded")

    def update_parameters(
        self, model=None, max_tokens=None, temperature=None, top_p=None, **kwargs
    ):
        """อัพเดทค่าพารามิเตอร์สำหรับการแปล"""
        try:
            changes = []

            if model is not None:
                old_model = self.model
                # ตรวจสอบ model ID แทนชื่อที่แสดง
                if model != "claude-3-5-haiku-20241022":
                    raise ValueError(f"Invalid model for Claude translator: {model}")
                self.model = model
                self.displayed_model = "claude-3.5-haiku"  # ใช้ชื่อแสดงคงที่
                changes.append(f"Model: {old_model} -> {model}")

            if max_tokens is not None:
                old_tokens = self.max_tokens
                if not (100 <= max_tokens <= 1000):
                    raise ValueError(
                        f"Max tokens must be between 100 and 1000, got {max_tokens}"
                    )
                self.max_tokens = max_tokens
                changes.append(f"Max tokens: {old_tokens} -> {max_tokens}")

            if temperature is not None:
                old_temp = self.temperature
                if not (0.5 <= temperature <= 0.9):
                    raise ValueError(
                        f"Temperature must be between 0.5 and 0.9, got {temperature}"
                    )
                self.temperature = temperature
                changes.append(f"Temperature: {old_temp} -> {temperature}")
                
            if top_p is not None:
                old_top_p = self.top_p
                if not (0.0 <= top_p <= 1.0):
                    raise ValueError(
                        f"Top P must be between 0.0 and 1.0, got {top_p}"
                    )
                self.top_p = top_p
                changes.append(f"Top P: {old_top_p} -> {top_p}")

            if changes:
                print("\n[Claude API] Parameters updated:")
                for change in changes:
                    print(change)
                print(f"Current model: {self.displayed_model}")
            return True, None

        except ValueError as e:
            print(f"[Claude API] Parameter update failed: {str(e)}")
            return False, str(e)

    def is_translation_complete(self, source_text, translated_text):
        """
        ตรวจสอบว่าการแปลสมบูรณ์หรือไม่ โดยใช้เกณฑ์หลายอย่างประกอบกัน
        
        Args:
            source_text (str): ข้อความต้นฉบับภาษาอังกฤษ
            translated_text (str): ข้อความที่แปลแล้วเป็นภาษาไทย
            
        Returns:
            bool: True ถ้าการแปลสมบูรณ์, False ถ้าไม่สมบูรณ์
        """
        # ตรวจสอบกรณีที่แปลไม่ได้หรือว่างเปล่า
        if not translated_text or translated_text.strip() == "":
            return False
            
        # ตรวจสอบถ้ายังมีภาษาอังกฤษหลงเหลืออยู่มาก
        eng_char_count = sum(1 for c in translated_text if 'a' <= c.lower() <= 'z')
        total_char_count = len(translated_text)
        
        # หากมีตัวอักษรภาษาอังกฤษมากกว่า 60% แสดงว่าการแปลอาจไม่สมบูรณ์
        if total_char_count > 0 and eng_char_count / total_char_count > 0.6:
            return False
            
        # ตรวจสอบอัตราส่วนความยาว - การแปลภาษาไทยควรจะไม่สั้นกว่าต้นฉบับมาก
        eng_words = len(source_text.split())
        thai_chars = sum(1 for c in translated_text if '\u0e00' <= c <= '\u0e7f')
        
        # การแปลภาษาไทยที่ดีควรมีจำนวนตัวอักษรไทยมากกว่าจำนวนคำในภาษาอังกฤษ
        if eng_words > 3 and thai_chars < eng_words * 1.5:
            return False
            
        # ตรวจสอบว่ามีการแปลชื่อตัวละครหรือไม่
        if ":" in source_text:
            # มีรูปแบบ "Character: Dialogue"
            eng_name = source_text.split(":", 1)[0].strip()
            
            # ถ้าในต้นฉบับมีชื่อตัวละคร แต่ในฉบับแปลไม่มี ถือว่าแปลไม่สมบูรณ์
            if self.is_character_name(eng_name) and ":" not in translated_text:
                return False
                
            if ":" in translated_text:
                thai_name = translated_text.split(":", 1)[0].strip()
                
                # ถ้าชื่อในฉบับแปลเป็นภาษาอังกฤษทั้งหมด อาจเป็นไปได้ว่ายังไม่ได้แปลชื่อ
                # ยกเว้นกรณีชื่อตัวละครที่ไม่ควรแปล
                if all('a' <= c.lower() <= 'z' or c.isspace() or c in "'-" for c in thai_name):
                    # ตรวจสอบว่าเป็นชื่อที่ไม่ควรแปลหรือไม่
                    if not self._is_name_keep_original(eng_name):
                        # ถ้าควรแปลแต่ยังเป็นภาษาอังกฤษ ถือว่าแปลไม่สมบูรณ์
                        return False
        
        # ตรวจสอบคำเฉพาะที่มักพบในการแปลที่ไม่สมบูรณ์
        incomplete_indicators = [
            "I apologize", "sorry", "cannot", "translation", "original text",
            "here's", "here is", "English", "Thai"
        ]
        
        if any(indicator.lower() in translated_text.lower() for indicator in incomplete_indicators):
            return False
            
        # ผ่านเกณฑ์ทั้งหมด ถือว่าแปลสมบูรณ์
        return True
        
    def _is_name_keep_original(self, name):
        """
        ตรวจสอบว่าชื่อนี้ควรคงรูปแบบเดิมโดยไม่แปลหรือไม่
        
        Args:
            name (str): ชื่อที่ต้องการตรวจสอบ
            
        Returns:
            bool: True ถ้าควรคงชื่อเดิม, False ถ้าควรแปล
        """
        # ชื่อที่เป็นคำสากลหรือชื่อเฉพาะที่ไม่ควรแปล
        keep_original = [
            "???", "2?", "22?", "222?",  # ตัวละครลึกลับ
            "Player", "Farmer",  # ชื่อผู้เล่นหรือตัวละครหลัก
        ]
        
        # ตรวจสอบว่าตรงกับชื่อที่ไม่ควรแปลโดยตรงหรือไม่
        if any(name.strip() == orig for orig in keep_original):
            return True
            
        # ตรวจสอบว่าเป็นชื่อที่ขึ้นต้นด้วยคำที่ไม่ควรแปลหรือไม่
        title_keep_original = [
            "Mr", "Mr.", "Mrs", "Mrs.", "Ms", "Ms.", "Sir", "Lady", "Lord"
        ]
        
        for title in title_keep_original:
            if name.startswith(title + " "):
                return True
                
        return False

    def extract_character_name(self, text):
        """
        แยกชื่อผู้พูดและข้อความบทสนทนา
        
        Args:
            text: ข้อความที่ต้องการแยก เช่น "Character: Dialogue"
            
        Returns:
            tuple: (ชื่อผู้พูด, ข้อความบทสนทนา)
        """
        # กรณีข้อความว่าง
        if not text or not text.strip():
            return "", ""
            
        # ตรวจสอบรูปแบบ "Name: Dialogue"
        match = re.match(r"^([^:]+):\s*(.*)", text)
        if match:
            name, dialogue = match.groups()
            name = name.strip()
            dialogue = dialogue.strip()
            
            # กรณีพิเศษสำหรับ "???" หรือแบบแผนที่เป็นเลข 2
            if name == "???" or re.match(r"^2+\??$", name):
                name = "???"
                
            # ตรวจสอบว่าเป็นชื่อตัวละครที่รู้จักหรือไม่
            if name and name != "???" and name not in self.character_names_cache:
                # ใช้ enhanced_detector ถ้ามี
                is_character = False
                try:
                    if hasattr(self, "enhanced_detector") and self.enhanced_detector is not None:
                        # ลองหลายเมธอดที่อาจมีในคลาส EnhancedNameDetector
                        if hasattr(self.enhanced_detector, "is_likely_character_name"):
                            is_character = self.enhanced_detector.is_likely_character_name(name)
                        elif hasattr(self.enhanced_detector, "is_name"):
                            is_character = self.enhanced_detector.is_name(name)
                        else:
                            # ถ้าไม่มีเมธอดที่ต้องการ ใช้วิธีตรวจสอบพื้นฐานแทน
                            is_character = self.is_character_name(name)
                    else:
                        # ตรวจสอบด้วยกฎพื้นฐาน
                        is_character = self.is_character_name(name)
                except Exception as e:
                    print(f"[Claude API] Error checking character name: {e}")
                    # ใช้วิธีตรวจสอบด้วยตัวเอง
                    is_character = self.is_character_name(name)
                    
                if is_character:
                    print(f"[Claude API] Adding new character name: {name}")
                    self.character_names_cache.add(name)
                    
            return name, dialogue
            
        # กรณีไม่พบรูปแบบชื่อ-บทสนทนา
        return "", text

    def get_character_info(self, character_name):
        """
        ดึงข้อมูลตัวละครจากฐานข้อมูล
        
        Args:
            character_name: ชื่อตัวละคร
            
        Returns:
            dict: ข้อมูลตัวละคร หรือ None ถ้าไม่พบ
        """
        # กรณีพิเศษสำหรับตัวละครลึกลับ
        if character_name in ["???", "2", "22", "222", "2?"] or re.match(r"^2+\??$", character_name):
            return {
                "firstName": "???",
                "lastName": "",
                "fullName": "???",
                "gender": "unknown",
                "role": "Mystery character",
                "relationship": "Unknown",
                "pronouns": {
                    "subject": "ฉัน",
                    "object": "ฉัน",
                    "possessive": "ของฉัน"
                }
            }
            
        # ตรวจสอบใน cache ก่อน
        if character_name in self.character_info_cache:
            return self.character_info_cache[character_name]
            
        # ค้นหาในฐานข้อมูล
        for character in self.character_data:
            # ตรวจสอบชื่อแบบเต็ม
            if character.get("fullName", "") == character_name:
                self.character_info_cache[character_name] = character
                return character
                
            # ตรวจสอบชื่อแบบอื่นๆ
            if (character.get("firstName", "") == character_name or 
                character.get("lastName", "") == character_name or
                character.get("title", "") == character_name):
                self.character_info_cache[character_name] = character
                return character
                
        # กรณีไม่พบ ให้สร้างข้อมูลพื้นฐาน
        basic_info = {
            "firstName": character_name,
            "lastName": "",
            "fullName": character_name,
            "gender": "unknown",
            "role": "NPC",
            "relationship": "Unknown",
            "pronouns": {
                "subject": "ฉัน",
                "object": "ฉัน",
                "possessive": "ของฉัน"
            }
        }
        
        # เก็บลงใน cache
        self.character_info_cache[character_name] = basic_info
        return basic_info

    def is_valid_text(self, text):
        """ตรวจสอบความถูกต้องของข้อความ"""
        return bool(re.search(r"\b\w{3,}\b", text))

    def is_character_name(self, text):
        """
        ตรวจสอบว่าข้อความเป็นชื่อตัวละครหรือไม่ โดยใช้กฎพื้นฐาน
        
        Args:
            text: ข้อความที่ต้องการตรวจสอบ
            
        Returns:
            bool: True ถ้าเป็นชื่อตัวละคร, False ถ้าไม่ใช่
        """
        # ตรวจสอบกรณีว่างหรือสั้นเกินไป
        if not text or len(text) < 2:
            return False
            
        # ตรวจสอบถ้าอยู่ใน cache แล้ว
        if text in self.character_names_cache:
            return True
            
        # ตรวจสอบตัวละครลึกลับ
        if text == "???" or re.match(r"^2+\??$", text):
            return True
            
        # ตรวจสอบใน word_fixes (เพิ่มส่วนนี้)
        if hasattr(self, "word_fixes") and self.word_fixes:
            if text in self.word_fixes:
                # ถ้ามีการแก้ไขในฐานข้อมูล ให้ถือว่าเป็นชื่อตัวละคร
                return True
        
        # ทำความสะอาดข้อความเพื่อตรวจสอบ (ลบสัญลักษณ์พิเศษบางอย่างออก)
        clean_text = text
        for char in "!?.,;:\"'[]()*&^%$#@-_=+<>{}|\\": 
            clean_text = clean_text.replace(char, "")
        
        # หากหลังจากลบสัญลักษณ์พิเศษแล้วเหลือข้อความสั้นเกินไป ไม่น่าจะเป็นชื่อตัวละคร
        if len(clean_text.strip()) < 2:
            return False
        
        # ตรวจสอบว่าเป็นข้อความภาษาอังกฤษหรือไม่
        is_english = all(c.isalpha() or c.isspace() or c in "'-" for c in clean_text)
        if not is_english:
            # ถ้ามีตัวอักษรไทยปนมา อาจไม่ใช่ชื่อตัวละคร
            if any('\u0e00' <= c <= '\u0e7f' for c in clean_text):
                return False
                
        # ชื่อตัวละครมักจะขึ้นต้นด้วยตัวพิมพ์ใหญ่และไม่มีคำที่พบบ่อยในประโยค
        if not text[0].isupper() and not clean_text[0].isupper():
            return False
            
        # คำทั่วไปที่มักไม่ใช่ชื่อตัวละคร
        common_words = {
            "the", "a", "an", "this", "that", "these", "those", 
            "it", "they", "we", "you", "i", "me", "he", "she", 
            "and", "or", "but", "if", "when", "where", "how", "what", "why",
            "is", "are", "was", "were", "be", "been", "being",
            "have", "has", "had", "do", "does", "did", "will", "would", "should", "could", "can",
            "then", "than", "thank", "your", "my", "our", "their", "his", "her", "its",
            "there", "here", "very", "so", "such", "just", "not", "only", "also"
        }
        
        if clean_text.lower() in common_words:
            return False
            
        # ตรวจสอบผู้ที่อาจเป็นชื่อตัวละคร (เช่น Mr., Mrs., Sir, etc.)
        title_indicators = ["mr", "mr.", "mrs", "mrs.", "ms", "ms.", "sir", "lady", "lord",
                           "prince", "princess", "king", "queen", "duke", "duchess", "professor",
                           "dr", "dr.", "doctor", "captain", "lieutenant", "general", "commander",
                           "officer", "master", "mistress", "elder", "father", "mother", "brother",
                           "sister", "uncle", "aunt", "grandfather", "grandmother"]
                           
        for indicator in title_indicators:
            if clean_text.lower().startswith(indicator + " "):
                return True
                
        # ตรวจสอบว่ามีคำที่บ่งบอกว่าไม่ใช่ชื่อ
        non_name_indicators = ["said", "says", "replied", "asked", "whispered", "shouted",
                             "exclaimed", "interrupted", "continued", "began", "started",
                             "finished", "stopped", "paused", "thought", "wondered"]
                             
        for word in non_name_indicators:
            if word in clean_text.lower().split():
                return False
                
        # ตรวจสอบความยาว - ชื่อตัวละครมักจะไม่ยาวเกินไป
        words = clean_text.split()
        if len(words) > 4:  # ชื่อตัวละครมักจะไม่เกิน 4 คำ
            return False
            
        # ถ้ามีหลายคำ ทุกคำควรขึ้นต้นด้วยตัวพิมพ์ใหญ่ (ยกเว้นคำเชื่อม)
        connecting_words = {"of", "the", "and", "or", "but", "in", "on", "at", "by", "for", "with", "to", "from"}
        if len(words) > 1:
            for word in words:
                if (word.lower() not in connecting_words and 
                    not word[0].isupper() and 
                    len(word) > 1):  # ไม่ตรวจสอบคำที่มีเพียง 1 ตัวอักษร
                    return False
                
        # ผ่านเกณฑ์ทั้งหมด น่าจะเป็นชื่อตัวละคร
        return True

    def translate(
        self, text, character_name=None, dialogue_type=None, context=None, quality_required=False, retry=0
    ):
        """
        แปลข้อความจากภาษาอังกฤษเป็นภาษาไทย
        
        Args:
            text: ข้อความที่ต้องการแปล
            character_name: ชื่อตัวละครที่พูด (ถ้ามี)
            dialogue_type: ประเภทของบทสนทนา (ถ้ามี)
            context: บริบทเพิ่มเติม (ถ้ามี)
            quality_required: ต้องการคุณภาพสูงหรือไม่
            retry: จำนวนครั้งที่ลองแปลแล้ว
            
        Returns:
            str: ข้อความที่แปลแล้ว หรือข้อความแสดงข้อผิดพลาด
        """
        # ตรวจสอบข้อความว่าง
        if not text.strip():
            return ""

        # กรณีพิเศษสำหรับชื่อตัวละคร
        if character_name is None:
            extracted_name, extracted_text = self.extract_character_name(text)
            if extracted_name:
                character_name = extracted_name
                text = extracted_text

        # กรณีผู้พูดเป็น ??? หรือเลข 2
        if character_name in ["???", "2", "22", "222", "2?"] or re.match(r"^2+\??$", character_name):
            character_name = "???"
            if re.match(r"^2+\??$", text.strip()) or text.strip() == "???":
                return "???"

        # ตรวจสอบว่ามีตัวอย่างการแปลหรือไม่
        if text in self.example_translations:
            return self.example_translations[text]

        # ตรวจสอบหากเป็นเพียงชื่อตัวละคร
        if text in self.character_names_cache:
            return text

        # ตรวจสอบกรณีพิเศษสำหรับสัญลักษณ์หรือตัวเลข
        if re.match(r"^[\d\W]+$", text.strip()):
            return text.strip()

        # รวบรวมข้อมูลตัวละคร
        character_info = ""
        character_style = None

        if character_name and character_name != "???":
            char_data = self.get_character_info(character_name)
            if char_data:
                gender = char_data.get("gender", "unknown")
                role = char_data.get("role", "")
                relationship = char_data.get("relationship", "")
                
                if gender != "unknown":
                    character_info += f"พูดโดย {character_name}, เพศ{gender}, "
                else:
                    character_info += f"พูดโดย {character_name}, "
                
                if role:
                    character_info += f"บทบาท: {role}, "
                
                if relationship:
                    character_info += f"ความสัมพันธ์: {relationship}, "
                
                # ดึงสไตล์การพูดของตัวละคร
                character_role = char_data.get("role", "").lower()
                for role_key, style_data in self.character_styles.items():
                    if role_key.lower() in character_role:
                        character_style = style_data
                        break

        # สร้างคำแนะนำสำหรับการแปล
        system_prompt = (
            "คุณเป็นผู้แปลภาษามืออาชีพ แปลข้อความจากภาษาอังกฤษเป็นภาษาไทย กรุณาแปลข้อความที่ให้มาด้านล่างให้เป็นภาษาไทยที่เป็นธรรมชาติ\n\n"
            "คำแนะนำ:\n"
            "1. รักษาความหมายดั้งเดิมของข้อความให้มากที่สุด\n"
            "2. ใช้ภาษาที่เป็นธรรมชาติและเหมาะสมกับบริบท ไม่แปลตรงตัวจนแข็งกระด้าง\n"
            "3. คงเอกลักษณ์และสไตล์ของตัวละครในการแปล\n"
            "4. ข้อความตัวอย่างจะมีรูปแบบ \"English Text: ข้อความภาษาไทย\"\n"
            "5. คุณต้องตอบเฉพาะคำแปลภาษาไทยเท่านั้น ไม่ต้องมีข้อความอื่นใด\n"
            "6. ห้ามเปลี่ยนชื่อตัวละคร ให้คงตามข้อความภาษาอังกฤษ\n"
            "7. ไม่ต้องเพิ่มเครื่องหมายวงเล็บเพื่ออธิบายเพิ่มเติม\n"
            "8. ไม่ต้องเพิ่มหรือตัดทอนเนื้อหา\n"
            "9. หากเป็นชื่อสถานที่ อาวุธพิเศษ ชื่อ skill พิเศษ หรือคำเฉพาะในเกม ให้คงรูปแบบเดิมไว้\n"
        )

        # ปรับปรุงคำแนะนำเฉพาะตัวละคร
        if character_style:
            speaking_style = character_style.get("speaking_style", "")
            personality = character_style.get("personality", "")
            
            if speaking_style:
                system_prompt += f"10. ตัวละครนี้มีรูปแบบการพูดที่เป็นเอกลักษณ์: {speaking_style}\n"
            
            if personality:
                system_prompt += f"11. บุคลิกของตัวละครนี้คือ: {personality}\n"

        # เพิ่มข้อมูลตัวละคร
        if character_info:
            system_prompt += f"\nข้อมูลตัวละคร: {character_info}"

        # เพิ่มบริบทเพิ่มเติม
        if context:
            system_prompt += f"\nบริบทเพิ่มเติม: {context}"

        # ตัวอย่างการแปล
        system_prompt += "\n\nตัวอย่างการแปล:\n"
        examples = list(self.example_translations.items())[:5]  # ใช้ 5 ตัวอย่างแรก
        for eng, thai in examples:
            system_prompt += f"{eng}: {thai}\n"

        # ใช้ API Claude แปล
        try:
            start_time = time.time()
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=self.top_p,
                system=system_prompt,
                messages=[{"role": "user", "content": text}]
            )
            
            translation = message.content[0].text
            
            # ตรวจสอบชื่อตัวละครในการแปล
            if character_name and ":" in text:
                # กรณีข้อความมีรูปแบบ "Name: Dialogue"
                if ":" not in translation and translation.strip():
                    translation = f"{character_name}: {translation}"
            elif character_name and ":" not in text:
                # กรณีที่มีการส่ง character_name มาแต่ text ไม่มี : (เช่น เป็นคำพูดโดยตรง)
                # ตรวจสอบว่าการแปลมี character_name หรือไม่
                if not translation.startswith(f"{character_name}"):
                    # เพิ่ม character_name หน้าข้อความแปล
                    if character_name == "???":
                        translation = f"{character_name}: {translation}"
                    else:
                        translation = f"{character_name}: {translation}"
            
            # ตรวจสอบว่าการแปลสมบูรณ์หรือไม่
            if not self.is_translation_complete(text, translation):
                if retry < 2:  # ลองแปลใหม่ไม่เกิน 2 ครั้ง
                    print(f"[Claude API] Translation seems incomplete, retrying: {text[:30]}...")
                    return self.translate(text, character_name, dialogue_type, context, quality_required, retry + 1)
                else:
                    print(f"[Claude API] Translation may be incomplete even after retry: {text[:30]} -> {translation[:30]}...")
            
            # บันทึกผลการแปลล่าสุด
            translation_key = f"{text}|{character_name}"
            self.last_translations[translation_key] = translation
            
            time_taken = time.time() - start_time
            
            # Return เฉพาะคำแปลเท่านั้น
            return translation
            
        except Exception as e:
            error_msg = f"Translation error: {str(e)}"
            print(f"[Claude API] {error_msg}")
            return f"[Error] {error_msg}"

    def translate_choice(self, original_text, character_name=None):
        """
        แปลข้อความตัวเลือกจากเกม 
        แก้ปัญหาการแปลซ้ำโดยการตรวจจับและตัด "What will you say?" ออก
        แล้วแปลเฉพาะตัวเลือก จากนั้นติดหัวข้อภาษาไทยแบบตายตัวกลับมา
        
        Args:
            original_text: ข้อความที่ต้องการแปล
            character_name: ชื่อตัวละครที่เกี่ยวข้อง (ถ้ามี)
            
        Returns:
            str: ข้อความที่แปลแล้ว "คุณจะพูดว่าอย่างไร?\nตัวเลือกที่ 1\nตัวเลือกที่ 2"
        """
        print(f"[Claude API] translate_choice called with: '{original_text[:100]}...'")
        
        # ตรวจสอบข้อความว่าง
        if not original_text or not original_text.strip():
            return ""

        # ตรวจจับและตัด "What will you say?" ออก
        text_to_translate = original_text.strip()
        choices_only = text_to_translate
        
        # รูปแบบที่พบบ่อยของ "What will you say?"
        choice_headers = [
            "what will you say?",
            "what will you say",
            "whatwill you say?", 
            "what willyou say?",
            "what will yousay?",
            "whatwillyou say?",
            "whatwillyousay?"
        ]
        
        # ตรวจหาและตัดส่วน header ออก
        text_lower = text_to_translate.lower()
        header_found = False
        
        for header_pattern in choice_headers:
            if text_lower.startswith(header_pattern):
                # ตัดส่วน header ออก
                choices_only = text_to_translate[len(header_pattern):].strip()
                header_found = True
                print(f"[Claude API] Detected and removed header pattern: '{header_pattern}'")
                break
        
        # ถ้าไม่พบ header ที่ต้นข้อความ ลองหาในข้อความ
        if not header_found:
            for header_pattern in choice_headers:
                if header_pattern in text_lower:
                    # แยกข้อความโดยใช้ header เป็นตัวแบ่ง
                    parts = text_to_translate.split(header_pattern, 1)
                    if len(parts) > 1:
                        choices_only = parts[1].strip()
                        header_found = True
                        print(f"[Claude API] Found and removed header pattern in text: '{header_pattern}'")
                        break
        
        if not header_found:
            print("[Claude API] No 'What will you say?' header detected, translating full text")
        else:
            print(f"[Claude API] After header removal, choices text: '{choices_only[:100]}...'")

        # ถ้าไม่มีข้อความหลังตัด header ให้ใช้ข้อความเดิม
        if not choices_only.strip():
            choices_only = text_to_translate
            print("[Claude API] Empty choices after header removal, using original text")

        # แปลตัวเลือก
        translated_choices = self._translate_choices_content(choices_only, character_name)
        
        # ติดหัวข้อ "คุณจะพูดว่าอย่างไร?" แบบตายตัวกลับมา
        final_result = f"คุณจะพูดว่าอย่างไร?\n{translated_choices}"
        
        print(f"[Claude API] Final result with Thai header: '{final_result[:150]}...'")
        return final_result

    def _translate_choices_content(self, original_text, character_name=None):
        """
        แปลเนื้อหาตัวเลือกเท่านั้น (helper method สำหรับ translate_choice)
        
        Args:
            original_text: ข้อความตัวเลือกที่ต้องการแปล (ไม่รวม header)
            character_name: ชื่อตัวละครที่เกี่ยวข้อง (ถ้ามี)
            
        Returns:
            str: ข้อความตัวเลือกที่แปลแล้ว
        """
        # ตรวจสอบว่ามีตัวอย่างการแปลหรือไม่
        if original_text in self.example_translations:
            return self.example_translations[original_text]

        # กรณีเป็นชื่อตัวละคร
        if original_text in self.character_names_cache:
            return original_text

        # กรณีข้อความพิเศษ "???" หรือเลข 2
        if re.match(r"^2+\??$", original_text.strip()) or original_text.strip() == "???":
            return "???"

        # ตรวจสอบว่าข้อความดูเหมือนเป็นชื่อตัวละครหรือไม่
        if self.is_character_name(original_text):
            # ถ้าดูเหมือนเป็นชื่อตัวละคร ให้เก็บไว้ใน cache และคืนค่าเดิม
            print(f"[Claude API] Detected likely character name: {original_text}")
            self.character_names_cache.add(original_text)
            return original_text

        # หากเป็นลิสต์ของตัวเลือก แยกแปลทีละบรรทัด
        if "\n" in original_text and any(line.strip().startswith(("•", "-", "*", "1.", "2.", "3.")) for line in original_text.split("\n") if line.strip()):
            try:
                translated_lines = []
                for line in original_text.split("\n"):
                    if line.strip():
                        # แยกเครื่องหมายหน้าข้อกับเนื้อหา
                        prefix_match = re.match(r'^([•\-*\d\.]+\s*)(.*)', line)
                        if prefix_match:
                            prefix, content = prefix_match.groups()
                            if content.strip():
                                # แปลแค่ส่วนเนื้อหา
                                translated_content = self._translate_choice_single_line(content, character_name)
                                # ตรวจสอบผลลัพธ์การแปล
                                if translated_content:
                                    translated_lines.append(f"{prefix}{translated_content}")
                                else:
                                    # ถ้าแปลไม่สำเร็จ ใช้ข้อความเดิม
                                    translated_lines.append(line)
                            else:
                                translated_lines.append(line)  # เก็บบรรทัดว่างหรือมีแต่เครื่องหมาย
                        else:
                            # ไม่มีเครื่องหมายนำหน้า
                            if line.strip():
                                translated_line = self._translate_choice_single_line(line, character_name)
                                # ตรวจสอบผลลัพธ์การแปล
                                if translated_line:
                                    translated_lines.append(translated_line)
                                else:
                                    # ถ้าแปลไม่สำเร็จ ใช้ข้อความเดิม
                                    translated_lines.append(line)
                            else:
                                translated_lines.append(line)  # เก็บบรรทัดว่าง
                    else:
                        translated_lines.append(line)  # เก็บบรรทัดว่าง
                
                # รวมบรรทัดและคืนค่า
                result = "\n".join(translated_lines)
                return result if result else original_text  # ถ้าผลลัพธ์ว่างเปล่า ให้คืนข้อความเดิม
            except Exception as e:
                print(f"[Claude API] Error translating choice list: {e}")
                return original_text  # กรณีเกิด error ให้คืนข้อความเดิม
        
        # กรณีเป็นข้อความปกติ (ไม่ใช่ลิสต์)
        try:
            result = self._translate_choice_single_line(original_text, character_name)
            return result if result else original_text  # ถ้าผลลัพธ์ว่างเปล่า ให้คืนข้อความเดิม
        except Exception as e:
            print(f"[Claude API] Error in _translate_choices_content: {e}")
            return original_text  # กรณี error ให้คืนข้อความเดิม แทนที่จะคืน error message

    def _translate_choice_single_line(self, original_text, character_name=None):
        """
        แปลตัวเลือกบทสนทนาเพียงบรรทัดเดียว (helper method สำหรับ translate_choice)
        
        Args:
            original_text: ข้อความที่ต้องการแปล
            character_name: ชื่อตัวละครที่เกี่ยวข้อง (ถ้ามี)
            
        Returns:
            str: ข้อความที่แปลแล้ว หรือข้อความเดิมถ้าแปลไม่สำเร็จ
        """
        # ตรวจสอบข้อความว่าง
        if not original_text or not original_text.strip():
            return ""
            
        # ตรวจสอบว่ามีตัวอย่างการแปลหรือไม่
        if original_text in self.example_translations:
            return self.example_translations[original_text]

        # กรณีเป็นชื่อตัวละคร
        if original_text in self.character_names_cache:
            return original_text

        # กรณีข้อความพิเศษ "???" หรือเลข 2
        if re.match(r"^2+\??$", original_text.strip()) or original_text.strip() == "???":
            return "???"

        # สร้างคำแนะนำสำหรับการแปล
        system_prompt = (
            "คุณเป็นผู้แปลภาษามืออาชีพ แปลตัวเลือกบทสนทนาจากภาษาอังกฤษเป็นภาษาไทย\n\n"
            "คำแนะนำ:\n"
            "1. คุณกำลังแปลตัวเลือกในเกม ซึ่งต้องการความกระชับ ตรงประเด็น และเข้าใจง่าย\n"
            "2. รักษาน้ำเสียงและความหมายของข้อความเดิม\n"
            "3. หากเป็นชื่อเฉพาะ ให้คงตามต้นฉบับ\n"
            "4. ตอบเฉพาะคำแปลภาษาไทยเท่านั้น ไม่ต้องมีคำอธิบายเพิ่มเติม\n"
            "5. อย่าเพิ่มรูปแบบการแสดงผลใดๆ เช่น เครื่องหมายหัวข้อ (•) หรือตัวเลข\n"
        )

        if character_name:
            char_data = self.get_character_info(character_name)
            if char_data:
                gender = char_data.get("gender", "unknown")
                subject_pronoun = char_data.get("pronouns", {}).get("subject", "ฉัน")
                system_prompt += f"\nข้อความนี้เกี่ยวข้องกับตัวละคร {character_name}, เพศ {gender}, สรรพนามแทนตัวเอง '{subject_pronoun}'"

        # ใช้ API Claude แปล
        try:
            # เริ่มด้วยการสร้าง response ที่ปลอดภัย คือ ข้อความเดิม (เพื่อกันกรณีเกิด error)
            translation = original_text
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=self.top_p,
                system=system_prompt,
                messages=[{"role": "user", "content": original_text}]
            )
            
            # ตรวจสอบว่า response มีการตอบกลับเนื้อหาหรือไม่
            if not message or not hasattr(message, 'content') or not message.content or len(message.content) == 0:
                print(f"[Claude API] Empty response for choice: {original_text}")
                return original_text  # คืนค่าข้อความต้นฉบับถ้าการแปลว่างเปล่า
            
            # ตรวจสอบว่า content[0] มีอยู่จริงและมี text property หรือไม่
            if not message.content[0] or not hasattr(message.content[0], 'text'):
                print(f"[Claude API] Invalid content structure: {message.content}")
                return original_text
            
            # ดึงค่า text ออกมา
            translation_text = message.content[0].text
            
            # ตรวจสอบว่า translation_text มีค่าและไม่ว่างเปล่า
            if not translation_text or not translation_text.strip():
                print(f"[Claude API] Empty choice translation result for: {original_text}")
                return original_text  # คืนค่าข้อความต้นฉบับถ้าการแปลว่างเปล่า
            
            # อัพเดตค่า translation ที่ปลอดภัยแล้ว
            translation = translation_text
            
            # ตรวจสอบและแก้ไขรูปแบบ
            if not self.is_translation_complete(original_text, translation):
                # ถ้าข้อความแปลดูไม่สมบูรณ์ ลองแปลอีกครั้งโดยปรับลดอุณหภูมิ
                print(f"[Claude API] Choice translation seems incomplete, retrying with lower temperature: {original_text}")
                try:
                    retry_message = self.client.messages.create(
                        model=self.model,
                        max_tokens=self.max_tokens,
                        temperature=max(0.1, self.temperature - 0.3),  # ลดอุณหภูมิลง
                        top_p=self.top_p,
                        system=system_prompt,
                        messages=[{"role": "user", "content": original_text}]
                    )
                    
                    # ตรวจสอบการตอบกลับอีกครั้ง
                    if (retry_message and hasattr(retry_message, 'content') and 
                        retry_message.content and len(retry_message.content) > 0 and 
                        hasattr(retry_message.content[0], 'text')):
                        
                        retry_translation = retry_message.content[0].text
                        
                        # ตรวจสอบว่า retry_translation มีค่าและไม่ว่างเปล่า
                        if retry_translation and retry_translation.strip() and self.is_translation_complete(original_text, retry_translation):
                            translation = retry_translation
                except Exception as e:
                    # ถ้าลองแปลครั้งที่สองไม่สำเร็จ ใช้ผลลัพธ์จากครั้งแรก
                    print(f"[Claude API] Error during retry translation: {e}")
                    # ยังคงใช้ translation เดิม (มีการตั้งค่าไว้แล้วก่อนหน้านี้)
                    pass
            
            # ลบคำว่า "Translation:" หรือ "คำแปล:" ถ้ามี
            translation = re.sub(r'^(Translation:?|คำแปล:?)\s*', '', translation, flags=re.IGNORECASE)
            
            # ลบเครื่องหมายหัวข้อที่อาจถูกเพิ่มโดย AI
            translation = re.sub(r'^[•\-*]\s*', '', translation)
            
            return translation
            
        except Exception as e:
            error_msg = f"Choice single line translation error: {str(e)}"
            print(f"[Claude API] {error_msg}")
            return original_text  # กรณี error ให้คืนข้อความเดิม แทนที่จะคืน error message

    def force_retranslate_with_quality_check(self, original_text, character_name=None, dialogue_type=None, context=None):
        """
        บังคับให้แปลใหม่โดยเพิ่มการตรวจสอบคุณภาพ
        
        Returns:
            str: ข้อความที่แปลแล้ว หรือข้อความแสดงข้อผิดพลาด
        """
        try:
            translation = self.translate(original_text, character_name, dialogue_type, context, quality_required=True)
            
            # แปลแล้วแต่คุณภาพยังไม่ดีพอ พยายามปรับปรุง
            if translation and not self.is_translation_complete(original_text, translation):
                # ปรับลดอุณหภูมิและลองแปลอีกครั้ง
                temp_backup = self.temperature
                self.temperature = max(0.1, self.temperature - 0.2)
                
                try:
                    print(f"[Claude API] Quality check failed, retrying with lower temperature: {original_text[:30]}...")
                    better_translation = self.translate(original_text, character_name, dialogue_type, context, quality_required=True)
                    
                    if better_translation and self.is_translation_complete(original_text, better_translation):
                        translation = better_translation
                finally:
                    # คืนค่าอุณหภูมิ
                    self.temperature = temp_backup
            
            return translation
            
        except Exception as e:
            error_msg = f"Force retranslation error: {str(e)}"
            print(f"[Claude API] {error_msg}")
            return f"[Error] {error_msg}"

    def batch_translate(self, texts, batch_size=10, area_type=None):
        """แปลข้อความเป็นชุด"""
        translated_texts = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            translated_batch = [
                self.translate(text, character_name=None, dialogue_type=None, context=None) for text in batch
            ]
            translated_texts.extend(translated_batch)
        return translated_texts

    def adaptive_translation(self, text, max_retries=3, area_type=None):
        """พยายามแปลซ้ำหากเกิดข้อผิดพลาด"""
        for attempt in range(max_retries):
            try:
                translation = self.translate(text, character_name=None, dialogue_type=None, context=None)
                return translation
            except Exception as e:
                print(
                    f"Error in adaptive_translation (attempt {attempt+1}/{max_retries}): {e}"
                )
                time.sleep(1)  # รอสักครู่ก่อนลองใหม่

        # หากล้มเหลวทุกครั้ง ให้ใช้การแปลแบบ fallback
        return self.fallback_translation(text)

    def fallback_translation(self, text):
        """แปลแบบฉุกเฉินเมื่อไม่สามารถแปลปกติได้"""
        return f"[ไม่สามารถแปลได้: {text}]"

    def update_character_style(self, character_name, new_style):
        """อัพเดทสไตล์การพูดของตัวละคร"""
        self.character_styles[character_name] = new_style
        print(f"[Claude API] Updated style for {character_name}")

    def reload_data(self):
        """โหลดข้อมูล NPC ใหม่"""
        print("[Claude API] Reloading NPC data")
        self.load_npc_data()
        self.load_example_translations()

    def get_current_parameters(self):
        """Return current translation parameters"""
        return {
            "model": self.model,
            "displayed_model": self.displayed_model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
        }

    def analyze_translation_quality(self, original_text, translated_text):
        """วิเคราะห์คุณภาพการแปล (ใช้เฉพาะเมื่อต้องการตรวจสอบ)"""
        prompt = (
            "As a translation quality assessor for Final Fantasy XIV, evaluate this translation:\n"
            f"Original (English): {original_text}\n"
            f"Translation (Thai): {translated_text}\n"
            "Provide a brief assessment and score out of 10."
        )

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=200,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}],
            )
            assessment = response.content[0].text.strip()
            return assessment
        except Exception as e:
            print(f"[Claude API] Quality assessment error: {str(e)}")
            return "Unable to assess translation quality."


# Example usage
if __name__ == "__main__":
    try:
        translator = TranslatorClaude()

        # Single translation example
        text_to_translate = "Y'shtola: The aetheric fluctuations in this area are most peculiar. We should proceed with caution."
        translation = translator.translate(text_to_translate)
        print(f"\nOriginal: {text_to_translate}")
        print(f"Translation: {translation}")

        # Unknown character example
        unknown_character_text = "???: I apologize for startling you, but I have my reasons for lurking in the shadows."
        unknown_translation = translator.translate(unknown_character_text)
        print(f"\nOriginal: {unknown_character_text}")
        print(f"Translation: {unknown_translation}")

        # Batch translation example
        texts_to_translate = [
            "Urianger: Pray, let us consider the implications of our recent discoveries.",
            "Wuk Lamat: Wow! This place is amazing! I can't wait to explore every nook and cranny!",
            "Sphene: As princess of Alexandria, I must remain composed, but I admit this adventure excites me greatly.",
        ]

        print("\nBatch Translation Examples:")
        batch_translations = translator.batch_translate(texts_to_translate)
        for original, translated in zip(texts_to_translate, batch_translations):
            print(f"\nOriginal: {original}")
            print(f"Translation: {translated}")

    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
