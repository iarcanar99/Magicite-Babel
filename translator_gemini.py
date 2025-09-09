# translator_gemini.py
import os
from dotenv import load_dotenv
import re
import tkinter as tk
from tkinter import messagebox
import json
import difflib
import time
import logging
from enum import Enum
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from text_corrector import TextCorrector, DialogueType
from dialogue_cache import DialogueCache
from npc_file_utils import get_npc_file_path
from language_restriction import validate_translation_languages, validate_input_text

# เพิ่มการ import EnhancedNameDetector ถ้ามี
try:
    from enhanced_name_detector import EnhancedNameDetector

    HAS_ENHANCED_DETECTOR = True
except ImportError:
    HAS_ENHANCED_DETECTOR = False

load_dotenv()


class TranslatorGemini:
    def __init__(self, settings=None):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            # เพิ่มการแจ้งเตือนที่ชัดเจนเมื่อไม่พบ API Key
            error_msg = "GEMINI_API_KEY not found in .env file"
            logging.error(error_msg)
            messagebox.showerror(
                "API Key Error", f"{error_msg}\nPlease add your API key to .env file"
            )
            raise ValueError(error_msg)

        # Initialize Gemini API
        genai.configure(api_key=self.api_key)

        # ใช้ settings object ถ้ามี
        if settings:
            api_params = settings.get_api_parameters()
            self.model_name = api_params.get("model", "gemini-1.5-pro")
            self.max_tokens = api_params.get("max_tokens", 500)
            self.temperature = api_params.get("temperature", 0.7)
            self.top_p = api_params.get("top_p", 0.9)
        else:
            # ถ้าไม่มี settings ให้โหลดจากไฟล์
            try:
                with open("settings.json", "r") as f:
                    settings_data = json.load(f)
                    api_params = settings_data.get("api_parameters", {})
                    self.model_name = api_params.get("model", "gemini-1.5-pro")
                    self.max_tokens = api_params.get("max_tokens", 500)
                    self.temperature = api_params.get("temperature", 0.7)
                    self.top_p = api_params.get("top_p", 0.9)
            except (FileNotFoundError, json.JSONDecodeError):
                self.model_name = "gemini-1.5-pro"
                self.max_tokens = 500
                self.temperature = 0.7
                self.top_p = 0.9
                logging.warning("Could not load settings.json, using default values")

        # ตั้งค่า safety settings
        self.safety_settings = [
            {
                "category": HarmCategory.HARM_CATEGORY_HARASSMENT,
                "threshold": HarmBlockThreshold.BLOCK_NONE,
            },
            {
                "category": HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                "threshold": HarmBlockThreshold.BLOCK_NONE,
            },
            {
                "category": HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                "threshold": HarmBlockThreshold.BLOCK_NONE,
            },
            {
                "category": HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                "threshold": HarmBlockThreshold.BLOCK_NONE,
            },
        ]

        # Initialize Gemini model
        genai_model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config={
                "max_output_tokens": self.max_tokens,
                "temperature": self.temperature,
                "top_p": self.top_p,
            },
            safety_settings=self.safety_settings,
        )
        self.model = genai_model

        self.cache = DialogueCache()
        self.last_translations = {}
        self.character_names_cache = set()
        self.text_corrector = TextCorrector()
        self.load_npc_data()
        self.load_example_translations()

        # ดูว่าสามารถใช้ EnhancedNameDetector ได้หรือไม่
        self.enhanced_detector = None
        if HAS_ENHANCED_DETECTOR:
            try:
                self.enhanced_detector = EnhancedNameDetector(
                    self.character_names_cache
                )
                logging.info("Initialized EnhancedNameDetector successfully")
            except Exception as e:
                logging.warning(f"Failed to initialize EnhancedNameDetector: {e}")
                self.enhanced_detector = None

    def get_current_parameters(self):
        """Return current translation parameters"""
        # สำหรับ Gemini จะแสดงชื่อรุ่นที่ง่ายต่อการอ่าน
        displayed_model = self.model_name
        if self.model_name == "gemini-1.5-pro":
            displayed_model = "gemini-1.5-pro"
        elif self.model_name == "gemini-1.5-flash":
            displayed_model = "gemini-1.5-flash"

        return {
            "model": self.model_name,
            "displayed_model": displayed_model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
        }

    def load_npc_data(self):
        try:
            # --- START: โค้ดใหม่ ---
            file_path = get_npc_file_path()
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"NPC.json file not found at {file_path}")

            print(f"TranslatorGemini: กำลังโหลดข้อมูล NPC จาก: {file_path}")
            # --- END: โค้ดใหม่ ---

            with open(file_path, "r", encoding="utf-8") as file:
                npc_data = json.load(file)
                self.character_data = npc_data.get("main_characters", [])
                self.context_data = npc_data.get("lore", {})
                self.character_styles = npc_data.get("character_roles", {})

                if "word_fixes" in npc_data:
                    self.word_fixes = npc_data["word_fixes"]
                    logging.info(
                        f"Loaded {len(self.word_fixes)} word fixes from NPC.json"
                    )
                else:
                    self.word_fixes = {}

                # Update character_names_cache
                self.character_names_cache = set()
                self.character_names_cache.add("???")

                for char in self.character_data:
                    if char.get("firstName"):
                        self.character_names_cache.add(char["firstName"])
                        if char.get("lastName"):
                            self.character_names_cache.add(
                                f"{char['firstName']} {char['lastName']}"
                            )

                for npc in npc_data.get("npcs", []):
                    if npc.get("name"):
                        self.character_names_cache.add(npc["name"])

                logging.info("TranslatorGemini: Loaded NPC.json successfully")

        except FileNotFoundError as e:
            logging.error(f"TranslatorGemini: {e}")
            raise  # ส่งต่อ error
        except json.JSONDecodeError:
            logging.error("TranslatorGemini: Invalid JSON in NPC.json")
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
            # ตัวอย่างอื่นๆ (เหมือนกับในไฟล์ translator.py เดิม)
        }

    def update_parameters(
        self, model=None, max_tokens=None, temperature=None, top_p=None, **kwargs
    ):
        """อัพเดทค่าพารามิเตอร์สำหรับการแปล"""
        try:
            old_params = {
                "model": self.model_name,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "top_p": self.top_p,
            }

            changes = []

            if model is not None:
                # อัพเดทรายการ valid_models ให้รองรับ gemini-2.0-flash และ gemini-2.5-flash
                valid_models = [
                    "gemini-1.5-pro",
                    "gemini-1.5-flash",
                    "gemini-2.0-flash-lite",
                    "gemini-2.0-flash",
                    "gemini-2.5-flash",  # เพิ่มโมเดล gemini-2.5-flash
                ]
                if model not in valid_models:
                    raise ValueError(
                        f"Invalid model for Gemini translator. Must be one of: {', '.join(valid_models)}"
                    )
                self.model_name = model
                changes.append(f"Model: {old_params['model']} -> {model}")

            if max_tokens is not None:
                if not (100 <= max_tokens <= 2000):  # Gemini supports up to 2048 tokens
                    raise ValueError(
                        f"Max tokens must be between 100 and 2000, got {max_tokens}"
                    )
                self.max_tokens = max_tokens
                changes.append(
                    f"Max tokens: {old_params['max_tokens']} -> {max_tokens}"
                )

            if temperature is not None:
                if not (0.0 <= temperature <= 1.0):  # Gemini uses 0-1 scale
                    raise ValueError(
                        f"Temperature must be between 0.0 and 1.0, got {temperature}"
                    )
                self.temperature = temperature
                changes.append(
                    f"Temperature: {old_params['temperature']} -> {temperature}"
                )

            if top_p is not None:
                if not (0.0 <= top_p <= 1.0):
                    raise ValueError(f"Top P must be between 0.0 and 1.0, got {top_p}")
                self.top_p = top_p
                changes.append(f"Top P: {old_params['top_p']} -> {top_p}")

            # Re-initialize the model with new parameters
            logging.info(
                f"Recreating Gemini model with parameters: {self.model_name}, max_tokens={self.max_tokens}, temp={self.temperature}"
            )
            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config={
                    "max_output_tokens": self.max_tokens,
                    "temperature": self.temperature,
                    "top_p": self.top_p,
                },
                safety_settings=self.safety_settings,
            )
            logging.info(f"Successfully recreated Gemini model: {self.model}")

            if changes:
                logging.info("\n=== Gemini Parameters Updated ===")
                for change in changes:
                    logging.info(change)
                logging.info(f"Current model: {self.model_name}")
                logging.info("==========================\n")

            return changes

        except Exception as e:
            error_msg = f"Error updating Gemini parameters: {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)

    def is_translation_complete(self, original_text, translated_text):
        """ตรวจสอบว่าการแปลสมบูรณ์หรือไม่โดยเปรียบเทียบความยาวและเนื้อหาแบบยืดหยุ่น (เหมาะกับภาษาไทย)

        Args:
            original_text: ข้อความต้นฉบับ
            translated_text: ข้อความที่แปลแล้ว

        Returns:
            bool: True ถ้าการแปลดูเหมือนจะสมบูรณ์, False ถ้าอาจจะไม่สมบูรณ์
        """
        # กรณีไม่มีข้อความ
        if not original_text or not translated_text:
            return False

        # กรณีชื่อตัวละครพิเศษ - ให้ผ่านเสมอ
        if translated_text.strip() in ["???", "Y'shtola", "Yshtola"]:
            return True

        # กรณีข้อความต้นฉบับเป็นเลข 2 หรือรูปแบบที่เกี่ยวข้องกับ ???
        if (
            re.match(r"^2+\??$", original_text.strip())
            or original_text.strip() == "???"
        ):
            return translated_text.strip() == "???"

        # แยกชื่อผู้พูดออกจากเนื้อหา
        original_content = original_text
        translated_content = translated_text

        # ตรวจสอบและแยกชื่อผู้พูดออก
        if ":" in original_text:
            parts = original_text.split(":", 1)
            if len(parts) == 2:
                original_content = parts[1].strip()

        if ":" in translated_text:
            parts = translated_text.split(":", 1)
            if len(parts) == 2:
                translated_content = parts[1].strip()

        # คำนวณจำนวนคำ (สำหรับภาษาอังกฤษ) และความยาวตัวอักษร (สำหรับภาษาไทย)
        original_words = original_content.split()
        original_char_length = len(original_content)
        translated_words = translated_content.split()
        translated_char_length = len(translated_content)

        # ข้อความสั้นมาก (1-3 คำ) ถือว่าสมบูรณ์เสมอหากมีตัวอักษร
        if len(original_words) <= 3 and translated_char_length >= 2:
            return True

        # ถ้าเป็นเพียงชื่อ หรือคำทักทาย (5 คำหรือน้อยกว่า) ให้ผ่านง่ายๆ
        if len(original_words) <= 5 and translated_char_length >= 5:
            return True

        # สำหรับภาษาไทย ให้ใช้ความยาวตัวอักษรเทียบกัน (เพราะคำไทยสั้นกว่าภาษาอังกฤษมาก)
        # สัดส่วนความยาวตัวอักษรที่เหมาะสมสำหรับการแปลอังกฤษเป็นไทยประมาณ 1:0.6
        char_ratio = translated_char_length / max(1, original_char_length)

        # ถ้าสัดส่วนตัวอักษรต่ำกว่า 0.3 (30%) ของต้นฉบับ อาจจะไม่สมบูรณ์
        # แต่ตรวจสอบเฉพาะข้อความที่มีความยาวมากกว่า 50 ตัวอักษรเท่านั้น
        if original_char_length > 50 and char_ratio < 0.3:
            return False

        # ข้อความสั้นไม่จำเป็นต้องตรวจสอบวรรคตอน
        if original_char_length <= 50:
            return True

        # ตรวจสอบการตัดท้ายประโยค
        if translated_content.strip().endswith(("-", "...")):
            # อนุญาตให้จบด้วย ... ได้ แต่ไม่อนุญาตให้จบด้วย -
            if translated_content.strip().endswith("-"):
                return False
            # ถ้าจบด้วย ... แต่ต้นฉบับไม่ได้จบด้วย ... ให้ตรวจสอบความยาวเพิ่มเติม
            if not original_content.strip().endswith("...") and char_ratio < 0.5:
                return False

        # ผ่านทุกเงื่อนไข ถือว่าสมบูรณ์
        return True

    def translate(
        self,
        text,
        source_lang="English",
        target_lang="Thai",
        is_choice_option=False,
        is_lore_text=False,
    ):
        
        # LANGUAGE RESTRICTION: Only English to Thai allowed
        is_valid_lang, lang_error = validate_translation_languages(source_lang, target_lang)
        if not is_valid_lang:
            return f"[ERROR: {lang_error}]"
        
        # INPUT VALIDATION: Check for non-English text
        is_valid_text, text_error = validate_input_text(text)
        if not is_valid_text:
            return f"[ERROR: {text_error}]"
        """
        แปลข้อความพร้อมจัดการบริบทของตัวละคร
        Args:
            text: ข้อความที่ต้องการแปล
            source_lang: ภาษาต้นฉบับ (default: English)
            target_lang: ภาษาเป้าหมาย (default: Thai)
            is_choice_option: เป็นข้อความตัวเลือกหรือไม่ (default: False)
            is_lore_text: เป็นข้อความ Lore/บรรยายหรือไม่ (default: False)
        Returns:
            str: ข้อความที่แปลแล้ว
        """
        try:
            if not text:
                logging.warning("Empty text received for translation")
                return ""

            # --- [ โค้ดที่แก้ไขใหม่ทั้งหมดอยู่ตรงนี้ ] ---
            # ถ้าไม่ใช่โหมด Lore ให้พยายามแยกชื่อผู้พูดตามปกติ
            if not is_lore_text:
                try:
                    # ใช้ text_corrector instance ที่สร้างไว้แล้ว
                    speaker, content, dialogue_type = (
                        self.text_corrector.split_speaker_and_content(text)
                    )
                except (TypeError, ValueError, AttributeError) as e:
                    # กรณีที่ split_speaker_and_content มีปัญหา หรือส่งค่า None กลับมา
                    logging.warning(
                        f"Error splitting text content: {e}, treating as normal text"
                    )
                    speaker = None
                    content = text
                    dialogue_type = None
            else:
                # ถ้าเป็นโหมด Lore ให้ข้ามการแยกชื่อไปเลย
                speaker = None
                content = text
                dialogue_type = DialogueType.NORMAL
            # --- [ จบส่วนแก้ไข ] ---

            # ตรวจสอบ word_fixes สำหรับข้อความทั้งหมด
            if hasattr(self, "word_fixes") and text.strip() in self.word_fixes:
                fixed_text = self.word_fixes[text.strip()]
                if fixed_text == "???":
                    return "???"

            # ตรวจสอบกรณีพิเศษสำหรับเลข 2 และ ???
            if text.strip() in ["2", "2?", "22", "22?", "222", "222?", "???"]:
                return "???"

            # กรณีพิเศษเมื่อข้อความประกอบด้วยเลข 2 ซ้ำกันหลายครั้ง (2, 22, 222, 2222, ฯลฯ)
            if re.match(r"^2+\??$", text.strip()):
                return "???"

            # ใช้ EnhancedNameDetector ถ้ามี เพื่อตรวจสอบเพิ่มเติม
            if self.enhanced_detector:
                try:
                    # ตรวจสอบว่าข้อความอาจเป็นชื่อตัวละครหรือไม่
                    (
                        temp_speaker,
                        temp_content,
                        detected_type,
                    ) = self.enhanced_detector.enhanced_split_speaker_and_content(text)
                    if (
                        detected_type == DialogueType.CHARACTER
                        and temp_speaker == "???"
                    ):
                        return "???"
                    # ถ้าตรวจเจอชื่อในโหมดที่ไม่มี speaker ให้ใช้ชื่อที่เจอ
                    if not speaker and temp_speaker:
                        speaker, content, dialogue_type = (
                            temp_speaker,
                            temp_content,
                            detected_type,
                        )

                except Exception as e:
                    logging.warning(f"Error using EnhancedNameDetector: {e}")

            # ตรวจสอบว่าเป็นข้อความตัวเลือกหรือไม่
            if not is_choice_option:
                try:
                    is_choice, prompt_part, choices = self.is_similar_to_choice_prompt(
                        text
                    )
                    if is_choice:
                        return self.translate_choice(text)
                except Exception as choice_err:
                    logging.warning(f"Error checking choice prompt: {choice_err}")

            # กรณีมีชื่อผู้พูด
            if dialogue_type == DialogueType.CHARACTER and speaker:
                # กรณีพิเศษสำหรับ ???
                if speaker.startswith("?"):
                    speaker = "???"

                character_name = speaker
                dialogue = content

                # *** PERFORMANCE: ตรวจสอบ enhanced cache สำหรับการแปล ***
                cached_translation = self.cache.get_cached_translation(
                    dialogue, character_name, "character"
                )
                if cached_translation:
                    return f"{character_name}: {cached_translation}"

                # Legacy cache support
                if (
                    dialogue in self.last_translations
                    and character_name == self.cache.get_last_speaker()
                ):
                    translated_dialogue = self.last_translations[dialogue]
                    # บันทึกลง enhanced cache ด้วย
                    self.cache.cache_translation(
                        dialogue, translated_dialogue, character_name, "character"
                    )
                    return f"{character_name}: {translated_dialogue}"

                # 1. ดึงข้อมูลพื้นฐานของตัวละคร
                character_info = self.get_character_info(character_name)
                context = ""
                if character_info:
                    context = (
                        f"Character: {character_info['firstName']}, "
                        f"Gender: {character_info['gender']}, "
                        f"Role: {character_info['role']}, "
                        f"Relationship: {character_info['relationship']}"
                    )
                elif character_name == "???":
                    context = "Character: Unknown, Role: Mystery character"

                # 2. ดึงรูปแบบการพูด
                character_style = self.character_styles.get(character_name, "")
                if not character_style and character_name == "???":
                    character_style = (
                        "ใช้ภาษาที่เป็นปริศนา ชวนให้สงสัยในตัวตน แต่ยังคงบุคลิกที่น่าสนใจ"
                    )

                self.cache.add_speaker(character_name)

            else:
                # กรณีข้อความทั่วไป
                dialogue = text
                character_name = ""
                context = ""
                character_style = ""

            # สร้าง prompt และแปล
            special_terms = self.context_data.copy()
            example_prompt = "Here are examples of good translations:\n\n"
            for eng, thai in self.example_translations.items():
                example_prompt += f"English: {eng}\nThai: {thai}\n\n"

            prompt = (
                "You are a professional translator specializing in video game localization for Final Fantasy XIV. "
                "Your task is to translate English game text to Thai with these requirements:\n"
                "1. Translate the text COMPLETELY, never cut off or omit any part of the original message\n"
                "2. Translate the text naturally while preserving the character's tone and style\n"
                "3. NEVER translate any character names, place names, or special terms that appear in the database\n"
                "4. For any terms found in 'Special terms' section below, use the Thai explanations provided instead of translating directly\n"
                "5. **Use modern Thai vocabulary and expressions even when the original English is archaic or old-fashioned.** Only preserve the complexity of sentence structure, but NOT the archaic vocabulary. Always prioritize words that sound natural to modern Thai speakers regardless of how old-fashioned the English text appears.\n"
                "6. For very short text, treat it as either: phrase, exclamation, or name calling only\n"
                "8. Maintain character speech patterns and emotional expressions as described in 'Character's style'\n"
                "9. NEVER use polite particles or sentence-ending particles like 'ครับ/ค่ะ/เจ้าค่ะ/เพคะ/นะคะ/จ้ะ/ฮะ' - Final Fantasy characters don't use these Thai politeness markers\n"
                "10. **Pronouns and Politeness Levels - STRICTLY follow Character's style:**\n"
                "   - For characters with 'สุภาพ' (polite) style: Always use 'คุณ' or 'ท่าน' instead of 'แก'\n"
                "   - For gentle/refined characters (อ่อนโยน, เข้มแข็ง, ฉลาด): Use 'คุณ' or 'เธอ'\n"
                "   - For aggressive/rough characters (ห้าวหาญ, ดุดัน, โผงผาง, ห้วน): May use 'แก' sparingly\n"
                "   - Default for most characters: Use 'คุณ' - avoid 'แก' unless character style explicitly indicates roughness\n"
                "   - **AVOID formal/stiff pronouns**: NEVER use 'ข้าพเจ้า' - it's too formal and unnatural for game dialogue\n"
                "   - **First person alternatives**: Use 'ฉัน', 'ข้า', or character name instead of 'ข้าพเจ้า'\n"
                "   - **CRITICAL**: Check Character's style section above and strictly adhere to the personality described\n"
                "11. Focus on natural, conversational Thai that's easy to understand for modern players. Prefer everyday language unless the character style indicates otherwise\n"
                "12. IMPORTANT: Ensure your translation covers the ENTIRE original text, not just a part of it\n"
                "13. VERY IMPORTANT: Return ONLY the Thai translation, DO NOT include the original English text in your response\n"
                "14. DO NOT include any explanations, notes, or formatting - just the pure Thai translation text\n"
                f"Context: {context}\n"
                f"Character's style: {character_style}\n"
                f"Do not translate (use exactly as written): {', '.join(self.character_names_cache)}\n\n"
                "Special terms (use these Thai explanations instead of translating directly):\n"
            )

            for term, explanation in special_terms.items():
                prompt += f"{term}: {explanation}\n"

            prompt += f"\n{example_prompt}\nText to translate: {dialogue}"

            try:
                # สร้าง Content สำหรับ Gemini API
                generation_config = {
                    "max_output_tokens": self.max_tokens,
                    "temperature": self.temperature,
                    "top_p": self.top_p,
                }

                # แสดงข้อความเริ่มการแปลในคอนโซล
                print(
                    f"                                            ", end="\r"
                )  # เคลียร์บรรทัด
                print(f"[Gemini API] Translating: {dialogue[:40]}...", end="\r")

                # บันทึกเวลาเริ่มต้น
                start_time = time.time()

                # แก้ไขวิธีการเรียก API - ส่งเฉพาะ prompt (ไม่ส่ง dialogue แยก)
                response = self.model.generate_content(
                    prompt,  # ส่งเฉพาะ prompt เต็มๆ ไม่ต้องส่ง dialogue แยก
                    generation_config=generation_config,
                    safety_settings=self.safety_settings,
                )

                # คำนวณเวลาที่ใช้
                elapsed_time = time.time() - start_time

                # สำหรับ Gemini เราไม่มีจำนวน token ที่แน่นอน ให้ประมาณจากจำนวนคำ
                input_words = len(prompt.split())
                output_words = (
                    len(response.text.split()) if hasattr(response, "text") else 0
                )
                # ประมาณ token โดยเฉลี่ย 1 คำ = 1.3 token
                input_tokens = int(input_words * 1.3)
                output_tokens = int(output_words * 1.3)
                total_tokens = input_tokens + output_tokens

                # แสดงข้อมูลในคอนโซล
                short_model = (
                    self.model_name if hasattr(self, "model_name") else "gemini"
                )
                # แสดงชื่อเต็มของโมเดลให้ชัดเจน
                print(f"[Gemini API] Translation complete                ", end="\r")
                print(
                    f"[{short_model.upper()}] : {dialogue[:30]}... -> ~{total_tokens} tokens ({elapsed_time:.2f}s)"
                )
                logging.info(
                    f"[Gemini API] Estimated tokens: ~{input_tokens} (input) + ~{output_tokens} (output) = ~{total_tokens} tokens in {elapsed_time:.2f}s"
                )

                # ดึงข้อความจาก response และตรวจสอบอย่างปลอดภัย
                if hasattr(response, "text") and response.text:
                    translated_dialogue = response.text.strip()
                else:
                    raise ValueError("No response text from Gemini API")

                # ทำความสะอาดข้อความแปล
                translated_dialogue = re.sub(
                    r"\b(ครับ|ค่ะ|ครับ/ค่ะ)\b", "", translated_dialogue
                ).strip()
                for term in special_terms:
                    translated_dialogue = re.sub(
                        r"\b" + re.escape(term) + r"\b",
                        term,
                        translated_dialogue,
                        flags=re.IGNORECASE,
                    )

                # ตรวจสอบและแทนที่กรณีพิเศษสำหรับเลข 2 และ ???
                if re.match(r"^2+\??$", dialogue.strip()) or dialogue.strip() == "???":
                    translated_dialogue = "???"

                # ตรวจสอบกรณีเลข 2 เป็นส่วนหนึ่งของประโยค
                if dialogue.strip() and re.match(r"^\s*2+\s*$", dialogue.strip()):
                    translated_dialogue = "???"

                # สร้างข้อความผลลัพธ์สุดท้าย
                if character_name:
                    # ตรวจสอบเพิ่มเติมหากชื่อตัวละครเป็นเลข 2
                    if (
                        re.match(r"^2+$", character_name)
                        or character_name.strip() == "???"
                    ):
                        character_name = "???"
                    final_translation = f"{character_name}: {translated_dialogue}"
                else:
                    final_translation = translated_dialogue

                # ตรวจสอบความสมบูรณ์ของการแปล
                if not self.is_translation_complete(text, final_translation):
                    # ตรวจสอบเงื่อนไขที่ไม่ต้องแปลซ้ำ
                    skip_retranslation = False

                    # กรณีข้อความสั้น ไม่ต้องแปลซ้ำ
                    if len(text.split()) <= 5:
                        skip_retranslation = True
                        logging.info("Skip retranslation for short text")

                    # กรณีชื่อตัวละครพิเศษ ไม่ต้องแปลซ้ำ
                    if any(name in text for name in ["Y'shtola", "Yshtola", "???"]):
                        skip_retranslation = True
                        logging.info("Skip retranslation for character names")

                    # กรณีมีตัวละครพูด ให้ตรวจสอบความยาวเพิ่มเติม
                    if ":" in text and len(text.split(":")[1].strip()) < 30:
                        skip_retranslation = True
                        logging.info("Skip retranslation for short dialogue")

                    if not skip_retranslation:
                        logging.warning(
                            "Translation appears incomplete, retrying with stronger prompt"
                        )

                        # ลองแปลอีกครั้งด้วย prompt ที่เน้นย้ำความสมบูรณ์มากขึ้น
                        enhanced_prompt = (
                            prompt
                            + "\n\nVERY IMPORTANT: You MUST translate the ENTIRE text completely. Do not cut off or truncate any part of the message."
                        )

                        retry_response = self.model.generate_content(
                            enhanced_prompt,
                            generation_config=generation_config,
                            safety_settings=self.safety_settings,
                        )

                        if hasattr(retry_response, "text") and retry_response.text:
                            retry_translation = retry_response.text.strip()

                            # ทำความสะอาดข้อความแปล
                            retry_translation = re.sub(
                                r"\b(ครับ|ค่ะ|ครับ/ค่ะ)\b", "", retry_translation
                            ).strip()

                            # เปรียบเทียบความยาวและคุณภาพ - ถ้าแปลใหม่ยาวกว่ามากๆ ถึงจะเอามาใช้
                            if len(retry_translation) > len(translated_dialogue) * 1.3:
                                translated_dialogue = retry_translation

                                if character_name:
                                    final_translation = (
                                        f"{character_name}: {translated_dialogue}"
                                    )
                                else:
                                    final_translation = translated_dialogue

                # *** PERFORMANCE: บันทึกลง enhanced cache ***
                self.last_translations[dialogue] = translated_dialogue

                # บันทึกลง enhanced cache with context
                if character_name:
                    self.cache.cache_translation(
                        dialogue, translated_dialogue, character_name, "character"
                    )
                    self.cache.add_validated_name(character_name)  # เพิ่มชื่อเข้า cache
                else:
                    self.cache.cache_translation(
                        dialogue, translated_dialogue, None, "normal"
                    )

                return final_translation

            except Exception as api_error:
                logging.error(f"Gemini API error: {str(api_error)}")
                # ลองใช้วิธีเรียก API อีกแบบหนึ่ง (กรณี model เก่า)
                try:
                    response = self.model.generate_content(
                        [{"role": "user", "parts": [prompt]}],
                        generation_config=generation_config,
                        safety_settings=self.safety_settings,
                    )

                    if hasattr(response, "text") and response.text:
                        translated_dialogue = response.text.strip()

                        # ทำความสะอาดข้อความแปล
                        translated_dialogue = re.sub(
                            r"\b(ครับ|ค่ะ|ครับ/ค่ะ)\b", "", translated_dialogue
                        ).strip()

                        if character_name:
                            return f"{character_name}: {translated_dialogue}"
                        return translated_dialogue
                    else:
                        raise ValueError("No response text from alternative API call")
                except Exception as alt_error:
                    logging.error(f"Alternative API call also failed: {str(alt_error)}")
                    return f"[Error: {str(api_error)}]"

        except Exception as e:
            logging.error(f"Unexpected error in translation: {str(e)}")
            return f"[Error: {str(e)}]"

    def is_similar_to_choice_prompt(self, text, threshold=0.7):
        """ตรวจสอบและแยกส่วนประกอบของ choice dialogue

        Args:
            text: ข้อความที่ต้องการตรวจสอบ
            threshold: ระดับความคล้ายคลึงที่ยอมรับได้

        Returns:
            tuple: (is_choice, prompt_part, choices) หรือ (False, None, None) ถ้าไม่ใช่ choice
        """
        try:
            # 1. รูปแบบ prompts ที่บ่งบอกว่าเป็น choice dialogue
            choice_prompts = [
                "What will you say?",
                "What would you like to ask?",
                "Choose your response.",
                "Select an option.",
                "How would you like to respond?",
                "Select a dialogue option.",
                "คุณจะพูดว่าอะไร?",
                "คุณจะพูดว่าอย่างไร?",
                "เลือกตัวเลือกของคุณ",
            ]

            # 2. ตรวจสอบการมีอยู่ของ prompt ที่แน่นอน
            clean_text = text.strip()

            # เช็คแบบเข้มงวดตามรูปแบบที่แน่นอน
            # ตรวจสอบว่าข้อความขึ้นต้นด้วย prompt หรือไม่
            for prompt in choice_prompts:
                if clean_text.startswith(prompt) or clean_text.lower().startswith(
                    prompt.lower()
                ):
                    # พบ prompt ที่ตรงกัน
                    parts = clean_text.split(prompt, 1)
                    if len(parts) == 2:
                        prompt_part = prompt
                        choices_part = parts[1].strip()

                        # ดึงตัวเลือกออกมา
                        choices = []

                        # วิธีที่ 1: แยกตามบรรทัด (วิธีที่มีประสิทธิภาพที่สุด)
                        if "\n" in choices_part:
                            lines = [
                                line.strip()
                                for line in choices_part.split("\n")
                                if line.strip()
                            ]
                            if lines:
                                choices = lines

                        # วิธีที่ 2: แยกตามตัวเลือก
                        if not choices:
                            number_starters = self._extract_choices_by_starters(
                                choices_part, ["1.", "2.", "3.", "4."]
                            )
                            if number_starters:
                                choices = number_starters

                        # วิธีที่ 3: แยกตามอักษร
                        if not choices:
                            letter_starters = self._extract_choices_by_starters(
                                choices_part, ["A.", "B.", "C.", "D."]
                            )
                            if letter_starters:
                                choices = letter_starters

                        # วิธีที่ 4: แยกตามเครื่องหมายวรรคตอน
                        if not choices and any(
                            mark in choices_part for mark in [".", "!", "?"]
                        ):
                            import re

                            split_by_punct = re.split(r"(?<=[.!?])\s+", choices_part)
                            if len(split_by_punct) > 1:
                                choices = [
                                    choice.strip()
                                    for choice in split_by_punct
                                    if choice.strip()
                                ]

                        # วิธีที่ 5: ถ้าวิธีข้างต้นล้มเหลว แต่มีข้อความหลัง prompt
                        if not choices and choices_part:
                            choices = [choices_part]

                        # ถ้าพบตัวเลือก
                        if choices:
                            return True, prompt_part, choices
                    else:
                        # กรณีพบเฉพาะ prompt โดยไม่มีเนื้อหาตามหลัง
                        return True, prompt, []

                # 3. ตรวจสอบว่า prompt อยู่ในข้อความหรือไม่ (แม้ไม่ได้อยู่ที่ต้นข้อความ)
                if prompt in clean_text or prompt.lower() in clean_text.lower():
                    idx = max(clean_text.lower().find(prompt.lower()), 0)
                    if idx < 20:  # ถ้าอยู่ในช่วงต้นข้อความ (ในระยะ 20 ตัวอักษรแรก)
                        # แยกข้อความส่วนก่อนและหลัง prompt
                        before_prompt = clean_text[:idx].strip()
                        after_prompt = clean_text[idx + len(prompt) :].strip()

                        # ถ้าส่วนก่อน prompt มีน้อยกว่า 10 ตัวอักษร และหลัง prompt มีเนื้อหา
                        if len(before_prompt) < 10 and after_prompt:
                            # แยกตัวเลือกเช่นเดียวกับด้านบน
                            choices = []

                            # แยกตามบรรทัด
                            if "\n" in after_prompt:
                                lines = [
                                    line.strip()
                                    for line in after_prompt.split("\n")
                                    if line.strip()
                                ]
                                if lines:
                                    choices = lines

                            # ถ้าไม่มีตัวเลือก ให้ใช้ข้อความทั้งหมดหลัง prompt
                            if not choices:
                                choices = [after_prompt]

                            return True, prompt, choices

            # 4. ตรวจสอบรูปแบบที่อาจเกิดจาก OCR ผิดพลาด
            ocr_variants = [
                "Whatwill you say?",
                "What willyou say?",
                "WhatwilI you say?",
                "What wiIl you say?",
                "Vhat will you say?",
                "VVhat will you say?",
            ]

            for variant in ocr_variants:
                if variant in clean_text or variant.lower() in clean_text.lower():
                    # พบ variant ที่น่าจะเป็น "What will you say?"
                    standard_prompt = "What will you say?"
                    idx = max(clean_text.lower().find(variant.lower()), 0)
                    after_variant = clean_text[idx + len(variant) :].strip()

                    # แยกตัวเลือกเช่นเดียวกับด้านบน
                    choices = []

                    # แยกตามบรรทัด
                    if "\n" in after_variant:
                        lines = [
                            line.strip()
                            for line in after_variant.split("\n")
                            if line.strip()
                        ]
                        if lines:
                            choices = lines

                    # ถ้าไม่มีตัวเลือก ให้ใช้ข้อความทั้งหมดหลัง variant
                    if not choices:
                        choices = [after_variant]

                    return True, standard_prompt, choices

            # ไม่ใช่ choice dialogue
            return False, None, None

        except Exception as e:
            logging.warning(f"Error in is_similar_to_choice_prompt: {str(e)}")
            # กรณีเกิด error ให้ส่งค่าที่ปลอดภัย
            return False, None, None

    def _extract_choices_by_starters(self, text, starters):
        """แยกตัวเลือกจากข้อความโดยใช้คำเริ่มต้นที่กำหนด

        Args:
            text: ข้อความที่ต้องการแยกตัวเลือก
            starters: list ของคำเริ่มต้น เช่น ["1.", "2."]

        Returns:
            list: รายการตัวเลือกที่แยกได้
        """
        try:
            choices = []

            # กรณีไม่มีข้อความ
            if not text:
                return []

            # ตรวจสอบว่ามีคำเริ่มต้นในข้อความหรือไม่
            found_starter = False
            for starter in starters:
                if starter in text:
                    found_starter = True
                    break

            if not found_starter:
                return []

            # วิธีที่ 1: ใช้ regex ที่มีประสิทธิภาพมากขึ้น
            import re

            pattern = "|".join(re.escape(starter) for starter in starters)
            regex = rf"({pattern})\s*(.*?)(?=(?:{pattern})|$)"

            matches = re.findall(regex, text, re.DOTALL)
            if matches:
                for match in matches:
                    starter, choice_text = match
                    if choice_text.strip():
                        choices.append(f"{starter} {choice_text.strip()}")
                return choices

            # วิธีที่ 2: ถ้า regex ล้มเหลว ใช้วิธีแยกแบบดั้งเดิม
            remaining_text = text
            current_choice = ""
            current_starter = None

            for i, starter in enumerate(starters):
                if starter in remaining_text:
                    # ถ้ามี starter ปัจจุบันและเจอ starter ใหม่
                    if current_starter:
                        # เก็บตัวเลือกปัจจุบัน
                        if current_choice:
                            choices.append(
                                f"{current_starter} {current_choice.strip()}"
                            )

                    # แยกข้อความที่ starter
                    parts = remaining_text.split(starter, 1)
                    remaining_text = parts[1] if len(parts) > 1 else ""
                    current_starter = starter
                    current_choice = remaining_text

                    # ตรวจสอบ starter ถัดไป
                    next_starter_pos = float("inf")
                    for next_starter in starters[i + 1 :]:
                        pos = remaining_text.find(next_starter)
                        if pos != -1 and pos < next_starter_pos:
                            next_starter_pos = pos

                    # ถ้ามี starter ถัดไป
                    if next_starter_pos != float("inf"):
                        current_choice = remaining_text[:next_starter_pos]
                        remaining_text = remaining_text[next_starter_pos:]

                    # เก็บตัวเลือกปัจจุบัน
                    if current_choice:
                        choices.append(f"{current_starter} {current_choice.strip()}")

            # เก็บตัวเลือกสุดท้าย
            if (
                current_starter
                and current_choice
                and not any(starter in current_choice for starter in starters)
            ):
                choices.append(f"{current_starter} {current_choice.strip()}")

            return choices

        except Exception as e:
            logging.warning(f"Error extracting choices by starters: {str(e)}")
            return []

    def translate_choice(self, text):
        """
        แปลข้อความตัวเลือกจากเกม - Enhanced with Caching
        แก้ปัญหาการแปลซ้ำโดยการตรวจจับและตัด "What will you say?" ออก
        แล้วแปลเฉพาะตัวเลือก จากนั้นติดหัวข้อภาษาไทยแบบตายตัวกลับมา

        Args:
            text (str): ข้อความที่มีโครงสร้าง choice ที่ต้องการแปล

        Returns:
            str: ข้อความที่แปลแล้ว "คุณจะพูดว่าอย่างไร?\nตัวเลือกที่ 1\nตัวเลือกที่ 2"
        """
        try:
            # *** PERFORMANCE: ตรวจสอบ choice cache ก่อน ***
            cached_choice = self.cache.get_cached_translation(text, None, "choice")
            if cached_choice:
                return cached_choice
            # แยก replace operation ออกมาก่อนเพื่อหลีกเลี่ยง backslash ใน f-string
            text_preview = text[:150].replace("\n", "<NL>")
            logging.info(
                f"TranslatorGemini: translate_choice called with input text: '{text_preview}'"
            )

            # ตรวจจับและตัด "What will you say?" ออก
            text_to_translate = text.strip()
            choices_only = text_to_translate

            # รูปแบบที่พบบ่อยของ "What will you say?"
            choice_headers = [
                "what will you say?",
                "what will you say",
                "whatwill you say?",
                "what willyou say?",
                "what will yousay?",
                "whatwillyou say?",
                "whatwillyousay?",
            ]

            # ตรวจหาและตัดส่วน header ออก
            text_lower = text_to_translate.lower()
            header_found = False

            for header_pattern in choice_headers:
                if text_lower.startswith(header_pattern):
                    # ตัดส่วน header ออก
                    choices_only = text_to_translate[len(header_pattern) :].strip()
                    header_found = True
                    logging.info(
                        f"TranslatorGemini: Detected and removed header pattern: '{header_pattern}'"
                    )
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
                            logging.info(
                                f"TranslatorGemini: Found and removed header pattern in text: '{header_pattern}'"
                            )
                            break

            if not header_found:
                logging.info(
                    "TranslatorGemini: No 'What will you say?' header detected, translating full text"
                )
            else:
                logging.info(
                    f"TranslatorGemini: After header removal, choices text: '{choices_only[:100]}...'"
                )

            # ถ้าไม่มีข้อความหลังตัด header ให้ใช้ข้อความเดิม
            if not choices_only.strip():
                choices_only = text_to_translate
                logging.info(
                    "TranslatorGemini: Empty choices after header removal, using original text"
                )

            # เพิ่ม FFXIV context สำหรับการแปล choice
            special_terms = self.context_data.copy()
            special_terms_text = ""
            if special_terms:
                special_terms_text = (
                    "\nSpecial FFXIV terms (use Thai explanations provided):\n"
                )
                for term, explanation in special_terms.items():
                    special_terms_text += f"- {term}: {explanation}\n"

            # ใช้ prompt สำหรับแปลเฉพาะตัวเลือกพร้อม FFXIV context
            prompt_parts = [
                "You are a highly skilled translator for the game Final Fantasy XIV.",
                "Translate the following player choice options from English to Thai.",
                "Each choice option should be translated as a natural, concise Thai phrase suitable for game dialogue selection.",
                "",
                "**PLAYER CHARACTER VOICE GUIDELINES:**",
                "- These are responses from the main protagonist (Warrior of Light) - can be male or female",
                "- Use a **brave, determined, and confident** tone throughout",
                "- Each choice may have different emotions to give players variety:",
                "  * Some choices may be serious and heroic",
                "  * Some may be humorous or witty",
                "  * Some may be challenging or defiant",
                "- Maintain the protagonist's strong, decisive personality in all options",
                "",
                "CRITICAL REQUIREMENTS:",
                "1. Translate each choice option into natural Thai with appropriate protagonist voice.",
                "2. Preserve the newline structure exactly - each choice on its own line.",
                "3. Output ONLY the Thai translation. NO English, NO explanations, NO prefixes.",
                "4. Preserve proper names and character names as they appear in the original.",
                "5. **PRONOUNS**: Use 'คุณ' instead of 'แก' for politeness - these are player dialogue choices.",
                "6. **AVOID FORMAL LANGUAGE**: Never use 'ข้าพเจ้า' - use 'ฉัน' or 'ข้า' for first person instead.",
                "7. Use modern, natural Thai expressions that sound appropriate for a brave protagonist.",
                "8. **FFXIV TERMS**: For any special terms listed below, use the Thai explanations provided.",
                special_terms_text,
                f"CHOICE OPTIONS TO TRANSLATE:\n{choices_only}",
                "",
                "TRANSLATED CHOICES (Thai only):",
            ]

            prompt = "\n".join(prompt_parts)

            generation_config = {
                "max_output_tokens": self.max_tokens
                + 150,  # Increased buffer for longer choices
                "temperature": max(
                    0.05, self.temperature - 0.2
                ),  # Lower temperature for more deterministic structural output
                "top_p": (
                    self.top_p if self.top_p <= 0.95 else 0.95
                ),  # Ensure top_p is reasonable
            }
            start_time = time.time()
            # แยก replace operation ออกมาก่อน
            text_head_preview = text[:50].replace("\n", "<NL>")
            logging.info(
                f"TranslatorGemini: Sending to Gemini (choice). Input head: '{text_head_preview}' Temp: {generation_config['temperature']:.2f}"
            )

            response = self.model.generate_content(
                prompt,
                generation_config=generation_config,
                safety_settings=self.safety_settings,
            )
            elapsed_time = time.time() - start_time

            # Token counting (simplified)
            prompt_tokens_est = len(prompt.split())
            completion_text = (
                response.text if hasattr(response, "text") and response.text else ""
            )
            completion_tokens_est = len(completion_text.split())
            # แยก replace operation ออกมาก่อน
            text_short_preview = text[:30].replace("\n", "<NL>")
            logging.info(
                f"[Gemini API - Choice] Est. Tokens: P~{prompt_tokens_est}, C~{completion_tokens_est}. Time: {elapsed_time:.2f}s. Input: '{text_short_preview}'"
            )

            if hasattr(response, "text") and response.text:
                translated_text_block = response.text.strip()
                # แยก replace operation ออกมาก่อน
                translated_preview = translated_text_block[:150].replace("\n", "<NL>")
                logging.info(
                    f"TranslatorGemini: translate_choice - Received from Gemini: '{translated_preview}'"
                )

                # Basic cleaning
                if translated_text_block.lower().startswith("thai:"):
                    translated_text_block = translated_text_block[5:].strip()

                # Additional cleaning for unwanted prefixes
                prefixes_to_remove = [
                    "translation:",
                    "แปล:",
                    "ภาษาไทย:",
                    "thai translation:",
                    "translated output:",
                    "output:",
                ]
                for prefix in prefixes_to_remove:
                    if translated_text_block.lower().startswith(prefix):
                        translated_text_block = translated_text_block[
                            len(prefix) :
                        ].strip()
                        break

                # ติดหัวข้อ "คุณจะพูดว่าอย่างไร?" แบบตายตัวกลับมา
                final_result = f"คุณจะพูดว่าอย่างไร?\n{translated_text_block}"

                # *** PERFORMANCE: บันทึกลง choice cache ***
                self.cache.cache_translation(text, final_result, None, "choice")

                # แยก replace operation ออกมาก่อน
                final_preview = final_result[:150].replace("\n", "<NL>")
                logging.info(
                    f"TranslatorGemini: translate_choice - Final result with Thai header: '{final_preview}'"
                )

                return final_result
            else:
                # แยก replace operation ออกมาก่อน
                text_error_preview = text[:70].replace("\n", "<NL>")
                logging.error(
                    f"TranslatorGemini: translate_choice - No response text from Gemini API for input: '{text_error_preview}'"
                )
                # ติดหัวข้อไทยแม้เกิด error
                return f"คุณจะพูดว่าอย่างไร?\n[Gemini Error: No Translation]\n{text}"

        except Exception as e:
            # แยก replace operation ออกมาก่อน
            text_exception_preview = text[:70].replace("\n", "<NL>")
            logging.error(
                f"TranslatorGemini: translate_choice - Exception: {str(e)} for input: '{text_exception_preview}'"
            )
            # ติดหัวข้อไทยแม้เกิด exception
            return f"คุณจะพูดว่าอย่างไร?\n[Translation Error: {str(e)}]\n{text}"

    def get_character_info(self, character_name):
        # จัดการกับกรณีพิเศษสำหรับ ??? และ เลข 2
        if character_name in ["???", "2", "22", "222"] or re.match(
            r"^2+$", character_name
        ):
            return {
                "firstName": "???",
                "gender": "unknown",
                "role": "Mystery character",
                "relationship": "Unknown/Mysterious",
                "pronouns": {"subject": "ฉัน", "object": "ฉัน", "possessive": "ของฉัน"},
            }

        # ตรวจสอบเพิ่มเติมด้วย EnhancedNameDetector
        if self.enhanced_detector:
            try:
                # ถ้าชื่อเป็นตัวเลขหรือมีรูปแบบคล้าย ??? ให้แก้ไขเป็น ???
                if re.match(r"^[2\?]+\??$", character_name):
                    return {
                        "firstName": "???",
                        "gender": "unknown",
                        "role": "Mystery character",
                        "relationship": "Unknown/Mysterious",
                        "pronouns": {
                            "subject": "ฉัน",
                            "object": "ฉัน",
                            "possessive": "ของฉัน",
                        },
                    }
            except Exception as e:
                logging.warning(f"Error in enhanced checking for character name: {e}")

        # ค้นหาข้อมูลตัวละครตามปกติ
        for char in self.character_data:
            if (
                character_name == char["firstName"]
                or character_name == f"{char['firstName']} {char['lastName']}".strip()
            ):
                return char
        return None

    def batch_translate(self, texts, batch_size=10):
        """แปลข้อความเป็นชุด"""
        translated_texts = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            translated_batch = [self.translate(text) for text in batch]
            translated_texts.extend(translated_batch)
        return translated_texts

    def analyze_translation_quality(self, original_text, translated_text):
        """วิเคราะห์คุณภาพการแปล"""
        # มีการเปลี่ยนแปลงในส่วนที่เรียกใช้ API
        prompt = (
            "As a translation quality assessor, evaluate the following translation from English to Thai. "
            "Consider factors such as accuracy, naturalness, and preservation of the original tone and style. "
            f"Original (English): {original_text}\n"
            f"Translation (Thai): {translated_text}\n"
            "Provide a brief assessment and a score out of 10."
        )

        try:
            # ส่งคำขอไปยัง Gemini API
            response = self.model.generate_content(
                [{"role": "user", "parts": [prompt]}]
            )
            return response.text.strip()
        except Exception as e:
            logging.error(f"Error in translation quality analysis: {str(e)}")
            return "Unable to assess translation quality due to an error."

    def reload_data(self):
        """โหลดข้อมูลใหม่และล้าง cache"""
        print("TranslatorGemini: Reloading NPC data...")
        self.load_npc_data()
        self.load_example_translations()
        self.cache.clear_session()
        self.last_translations.clear()
        print("TranslatorGemini: Data reloaded successfully")

    def analyze_custom_prompt(self, prompt_with_text):
        """Process a custom prompt with AI"""
        try:
            # มีการเปลี่ยนแปลงในส่วนที่เรียกใช้ API
            response = self.model.generate_content(
                [{"role": "user", "parts": [prompt_with_text]}],
                generation_config={
                    "max_output_tokens": self.max_tokens * 2,
                    "temperature": self.temperature,
                    "top_p": self.top_p,
                },
            )
            return response.text.strip()

        except Exception as e:
            logging.error(f"Error in custom prompt analysis: {e}")
            raise ValueError(f"Failed to process text with AI: {str(e)}")

    def force_retranslate_with_quality_check(
        self, original_text, previous_translation=None, min_quality_score=6.5
    ):
        """ตรวจสอบคุณภาพการแปลล่าสุดและพยายามแปลใหม่ให้ดีขึ้นเมื่อกด force translate

        Args:
            original_text: ข้อความต้นฉบับภาษาอังกฤษ
            previous_translation: การแปลก่อนหน้านี้ (ถ้ามี)
            min_quality_score: คะแนนคุณภาพขั้นต่ำที่ยอมรับได้ (0-10)

        Returns:
            str: ข้อความที่แปลใหม่หรือปรับปรุงแล้ว
        """
        try:
            print(f"ทำการตรวจสอบและแปลใหม่ผ่าน Force translate")
            logging.info(f"Force retranslation triggered for: {original_text[:50]}...")

            # ถ้าไม่มีการแปลก่อนหน้า ให้แปลก่อน
            if not previous_translation:
                previous_translation = self.translate(original_text)

            # ตรวจสอบคุณภาพการแปลก่อนหน้า
            quality_assessment = self.analyze_translation_quality(
                original_text, previous_translation
            )

            # แยกคะแนนออกจากข้อความ (ทำการ extract คะแนน 0-10)
            try:
                score_match = re.search(r"(\d+(\.\d+)?)/10", quality_assessment)
                quality_score = float(score_match.group(1)) if score_match else 0
                logging.info(f"Current translation quality score: {quality_score}/10")
            except (AttributeError, ValueError):
                quality_score = 0
                logging.warning(
                    f"Could not extract quality score from: {quality_assessment}"
                )

            # ถ้าคุณภาพต่ำกว่าเกณฑ์ ให้แปลใหม่ด้วยวิธีที่ปรับปรุง
            if quality_score < min_quality_score:
                logging.info(
                    f"Translation quality below threshold ({quality_score} < {min_quality_score}), attempting improved translation"
                )

                # เพิ่มอุณหภูมิเล็กน้อยและลดค่า top_p เพื่อให้ได้ผลลัพธ์ที่หลากหลายขึ้น
                current_temp = self.temperature
                current_top_p = self.top_p

                try:
                    # ปรับพารามิเตอร์ชั่วคราวสำหรับการแปลที่ดีขึ้น
                    enhanced_temp = min(
                        current_temp + 0.15, 0.95
                    )  # เพิ่มอุณหภูมิแต่ไม่เกิน 0.95
                    enhanced_top_p = max(
                        current_top_p - 0.05, 0.8
                    )  # ลด top_p แต่ไม่ต่ำกว่า 0.8

                    print(
                        f"ปรับค่าพารามิเตอร์ชั่วคราว: temp {current_temp}->{enhanced_temp}, top_p {current_top_p}->{enhanced_top_p}"
                    )
                    self.update_parameters(
                        temperature=enhanced_temp, top_p=enhanced_top_p
                    )

                    # สร้าง prompt ที่เข้มข้นขึ้นพร้อมตัวอย่างการแปลที่ไม่ดี
                    enhanced_prompt = (
                        "You are a professional Thai translator specializing in video game localization. "
                        "Your task is to translate this game dialogue from English to Thai with IMPROVED quality. "
                        "The previous translation was rated as inadequate.\n\n"
                        f"Original English: {original_text}\n\n"
                        f"Previous translation (NOT GOOD ENOUGH): {previous_translation}\n\n"
                        "Problems with the previous translation: "
                        f"{quality_assessment}\n\n"
                        "Rules for your improved translation:\n"
                        "1. Translate the text COMPLETELY and ACCURATELY\n"
                        "2. Maintain the character's tone, style, and personality\n"
                        "3. Use natural, conversational Thai that sounds good when spoken\n"
                        "4. NEVER use polite endings like ครับ/ค่ะ unless they're in the original\n"
                        "5. Preserve all character names exactly as they appear\n"
                        "6. Fully capture the meaning, nuance, and emotion of the original text\n"
                        "7. Return ONLY the improved Thai translation, with NO English or explanations\n"
                    )

                    # แปลใหม่ด้วย prompt ที่ปรับปรุงแล้ว
                    generation_config = {
                        "max_output_tokens": self.max_tokens,
                        "temperature": self.temperature,
                        "top_p": self.top_p,
                    }

                    retry_response = self.model.generate_content(
                        enhanced_prompt,
                        generation_config=generation_config,
                        safety_settings=self.safety_settings,
                    )

                    # ดึงข้อความแปลที่ปรับปรุงแล้ว
                    if hasattr(retry_response, "text") and retry_response.text:
                        improved_translation = retry_response.text.strip()

                        # ทำความสะอาดข้อความแปล
                        improved_translation = re.sub(
                            r"\b(ครับ|ค่ะ|ครับ/ค่ะ)\b", "", improved_translation
                        ).strip()

                        # ตรวจสอบคุณภาพการแปลใหม่
                        new_quality = self.analyze_translation_quality(
                            original_text, improved_translation
                        )

                        # ลองแยกคะแนนจากการประเมินครั้งใหม่
                        try:
                            new_score_match = re.search(
                                r"(\d+(\.\d+)?)/10", new_quality
                            )
                            new_quality_score = (
                                float(new_score_match.group(1))
                                if new_score_match
                                else 0
                            )
                            logging.info(
                                f"New translation quality score: {new_quality_score}/10"
                            )
                        except (AttributeError, ValueError):
                            new_quality_score = 0

                        # คืนค่าที่ดีที่สุดระหว่างการแปลใหม่กับการแปลเดิม
                        if new_quality_score > quality_score or len(
                            improved_translation
                        ) > len(previous_translation):
                            logging.info(
                                f"Using improved translation with score {new_quality_score} (previous: {quality_score})"
                            )

                            # อัพเดตการแปลล่าสุดในแคช
                            speaker, content, dialogue_type = (
                                self.text_corrector.split_speaker_and_content(
                                    original_text
                                )
                            )
                            if dialogue_type == DialogueType.CHARACTER and speaker:
                                # ถ้ามีชื่อตัวละคร แยกออกจากการแปล
                                if ":" in improved_translation:
                                    parts = improved_translation.split(":", 1)
                                    if len(parts) == 2:
                                        improved_content = parts[1].strip()
                                    else:
                                        improved_content = improved_translation
                                else:
                                    improved_content = improved_translation

                                self.last_translations[content] = improved_content
                                result = f"{speaker}: {improved_content}"
                            else:
                                self.last_translations[original_text] = (
                                    improved_translation
                                )
                                result = improved_translation

                            return result
                        else:
                            logging.info(
                                f"Keeping original translation as it's better or equal"
                            )
                            return previous_translation
                    else:
                        logging.warning(
                            "No text in retry response, keeping original translation"
                        )
                        return previous_translation

                finally:
                    # คืนค่าพารามิเตอร์เดิม
                    self.update_parameters(
                        temperature=current_temp, top_p=current_top_p
                    )
                    logging.info(
                        f"Restored original parameters: temp={current_temp}, top_p={current_top_p}"
                    )
            else:
                logging.info(
                    f"Translation quality is already good ({quality_score} >= {min_quality_score}), no retranslation needed"
                )
                return previous_translation

        except Exception as e:
            logging.error(f"Error in force retranslation: {str(e)}")
            print(f"เกิดข้อผิดพลาดในการแปลใหม่: {str(e)}")
            # กรณีเกิดข้อผิดพลาด ให้คืนค่าการแปลเดิม
            return previous_translation or self.translate(original_text)
