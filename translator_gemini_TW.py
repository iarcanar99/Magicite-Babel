# translator_gemini.py - Japanese to Thai Translation
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

        # ดึงค่าพารามิเตอร์จาก settings object ที่ได้รับมาเสมอ
        api_params = settings.get_api_parameters()
        self.model_name = api_params.get("model", "gemini-2.0-flash")
        self.max_tokens = api_params.get("max_tokens", 500)
        self.temperature = api_params.get("temperature", 0.7)
        self.top_p = api_params.get("top_p", 0.9)

        logging.info(f"TranslatorGemini initialized with model: {self.model_name}")

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
        # รูปแบบข้อมูลสกิลที่ต้องแปลแบบพิเศษ
        self.skill_patterns = [
            r"能量|攻擊|傷害|冷卻|消耗|範圍|效果|狀態",
            r"\d+%|\d+秒|\d+SP|\d+\.?\d*m",
            r"對.*造成|使.*減少|增加.*%",
        ]
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
        # แสดงชื่อรุ่นสำหรับการแปล ไต้หวัน→ไทย
        displayed_model = self.model_name + " (TW→TH)"

        return {
            "model": self.model_name,
            "displayed_model": displayed_model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
        }

    def load_npc_data(self):
        try:
            file_path = get_npc_file_path()
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"NPC.json file not found at {file_path}")

            print(f"TranslatorGemini TW: กำลังโหลดข้อมูล NPC จาก: {file_path}")

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

                logging.info("TranslatorGemini JP: Loaded NPC.json successfully")

        except FileNotFoundError as e:
            logging.error(f"TranslatorGemini JP: {e}")
            raise  # ส่งต่อ error
        except json.JSONDecodeError:
            logging.error("TranslatorGemini JP: Invalid JSON in NPC.json")
            raise ValueError("Invalid JSON in NPC.json")

    def load_example_translations(self):
        # ตัวอย่างการแปลสำหรับภาษาไต้หวัน (จีนตัวเต็ม) → ไทย
        self.example_translations = {
            "是": "ใช่",
            "不是": "ไม่ใช่",
            "你好": "สวัสดี",
            "謝謝": "ขอบคุณ",
            "對不起": "ขอโทษ",
            "辛苦了": "เหนื่อยหน่อยนะ",
            "原來如此": "อย่างนี้นี่เอง",
            "我知道了": "ฉันเข้าใจแล้ว",
            "等一下": "เดี๋ยวก่อน",
            "沒問題": "ไม่เป็นไร",
            "加油": "สู้ๆ นะ",
            "拜託了": "ขอร้องล่ะ, ฝากด้วยนะ",
            "等等": "เดี๋ยวก่อน!",
            "原來是這樣": "อ๋อ เป็นแบบนี้นี่เอง",
            "能量爆破": "Energy Blast - พลังระเบิด",
            "冷卻時間8秒": "Cooldown: 8 วินาที",
            "消耗60SP": "ใช้ SP: 60",
            "自身周圍半徑3.5m範圍的敵人": "ศัตรูในระยะ 3.5 เมตร รอบตัวผู้ใช้",
            "對周圍敵人造成攻擊力208%的傷害並且暈眩": "สร้างความเสียหาย 208% ของพลังโจมตี ให้กับศัตรูรอบข้าง และทำให้มึนงง",
            "【額外效果】對「無力」狀態的敵人造成的傷害量增加10%": "[เอฟเฟกต์เพิ่มเติม] สร้างความเสียหายเพิ่มขึ้น 10% ต่อศัตรูที่อยู่ในสถานะ 'อ่อนแอ'",
            "在競技場中，使被命中的敵人角色SP減少8%": "ใน Arena ลด SP ของศัตรูที่โดนโจมตี 8%",
            "點擊按鈕使用": "คลิกปุ่มเพื่อใช้งาน",
        }

    def update_parameters(self, new_parameters):
        """อัปเดตพารามิเตอร์การแปล"""
        try:
            if "model" in new_parameters:
                self.model_name = new_parameters["model"]
            if "max_tokens" in new_parameters:
                self.max_tokens = new_parameters["max_tokens"]
            if "temperature" in new_parameters:
                self.temperature = new_parameters["temperature"]
            if "top_p" in new_parameters:
                self.top_p = new_parameters["top_p"]

            # สร้าง model ใหม่ด้วยพารามิเตอร์ที่อัปเดต
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

            logging.info(
                f"TranslatorGemini JP: Updated parameters successfully: {new_parameters}"
            )

        except Exception as e:
            error_msg = f"Error updating Gemini JP parameters: {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)

    def is_translation_complete(self, original_text, translated_text):
        """ตรวจสอบว่าการแปลสมบูรณ์หรือไม่โดยเปรียบเทียบความยาวและเนื้อหาแบบยืดหยุ่น (เหมาะกับภาษาไทย)

        Args:
            original_text: ข้อความต้นฉบับ (ญี่ปุ่น)
            translated_text: ข้อความที่แปลแล้ว (ไทย)

        Returns:
            bool: True ถ้าการแปลดูเหมือนจะสมบูรณ์, False ถ้าอาจจะไม่สมบูรณ์
        """
        # กรณีไม่มีข้อความ
        if not translated_text or not translated_text.strip():
            return False

        # กรณีชื่อตัวละครพิเศษ - ให้ผ่านเสมอ
        if translated_text.strip() == "???":
            return True

        # กรณีข้อความต้นฉบับเป็นเลข 2 หรือรูปแบบที่เกี่ยวข้องกับ ???
        if (
            re.match(r"^2+\??$", original_text.strip())
            or original_text.strip() == "???"
        ):
            return True

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

        # คำนวณจำนวณอักขระสำหรับภาษาญี่ปุ่นและไทย
        original_char_length = len(original_content)
        translated_char_length = len(translated_content)
        char_ratio = (
            translated_char_length / original_char_length
            if original_char_length > 0
            else 1
        )

        # ข้อความสั้นมาก (1-3 อักขระ) ถือว่าสมบูรณ์เสมอหากมีตัวอักษร
        if original_char_length <= 3 and translated_char_length > 0:
            return True

        # สำหรับญี่ปุ่น→ไทย สัดส่วนความยาวประมาณ 1:1.2-1.5 (ไทยยาวกว่าญี่ปุ่นเล็กน้อย)
        # ถ้าสัดส่วนตัวอักษรต่ำกว่า 0.4 (40%) อาจจะไม่สมบูรณ์
        if original_char_length > 30 and char_ratio < 0.4:
            return False

        # ข้อความสั้นไม่จำเป็นต้องตรวจสอบวรรคตอน
        if original_char_length <= 30:
            return True

        # ตรวจสอบการตัดท้ายประโยค
        if translated_content.strip().endswith("-"):
            return False
        # ถ้าจบด้วย ... แต่ต้นฉบับไม่ได้จบด้วย ... ให้ตรวจสอบความยาวเพิ่มเติม
        if not original_content.strip().endswith("...") and char_ratio < 0.6:
            return False

        # ผ่านทุกเงื่อนไข ถือว่าสมบูรณ์
        return True

    def translate(
        self,
        text,
        source_lang="Japanese",
        target_lang="Thai",
        is_choice_option=False,
        is_lore_text=False,
    ):
        """
        แปลข้อความญี่ปุ่นพร้อมจัดการบริบทของตัวละคร
        Args:
            text: ข้อความที่ต้องการแปล (ญี่ปุ่น)
            source_lang: ภาษาต้นฉบับ (default: Japanese)
            target_lang: ภาษาเป้าหมาย (default: Thai)
            is_choice_option: เป็นข้อความตัวเลือกหรือไม่ (default: False)
        Returns:
            str: ข้อความที่แปลแล้ว (ไทย)
        """
        try:
            if not text:
                logging.warning("Empty text received for translation")
                return ""

            # ใส่ try-except เพื่อป้องกันกรณี split_speaker_and_content เกิด error
            if not is_lore_text:
                # โค้ดเดิมทั้งหมดที่เกี่ยวกับการแยกชื่อ (ตั้งแต่ try...except) จะต้องถูกย่อหน้าเข้ามาอยู่ใต้ if นี้
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
            # <<-- เพิ่ม 2 บรรทัดนี้
            else:
                # ถ้าเป็น Lore Text ไม่ต้องแยกชื่อ
                speaker = None
                content = text
                dialogue_type = DialogueType.NORMAL

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
                    speaker, content, detected_type = (
                        self.enhanced_detector.enhanced_split_speaker_and_content(text)
                    )
                    if detected_type == DialogueType.CHARACTER and speaker == "???":
                        return "???"
                except Exception as e:
                    logging.warning(f"Error using EnhancedNameDetector: {e}")

            # ตรวจสอบว่าเป็นข้อมูลสกิลหรือไม่
            is_skill = self.is_skill_description(text)
            if is_skill:
                logging.info(f"Detected skill description: {text[:50]}...")

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

                # ตรวจสอบ cache สำหรับการแปล
                if (
                    dialogue in self.last_translations
                    and character_name == self.cache.get_last_speaker()
                ):
                    translated_dialogue = self.last_translations[dialogue]
                    return f"{character_name}: {translated_dialogue}"

                # 1. ดึงข้อมูลพื้นฐานของตัวละคร
                character_info = self.get_character_info(character_name)
                context = ""
                if is_skill:
                    context = "This is a game skill description. Focus on clarity and technical accuracy."
                elif character_info:
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
            for jp, thai in self.example_translations.items():
                example_prompt += f"Japanese: {jp}\nThai: {thai}\n\n"

            prompt = (
                "You are a professional translator specializing in video game localization for Tree of Savior M. "
                "Your task is to translate Taiwanese (Traditional Chinese) game text to Thai with these requirements:\n"
                "**SKILL/GAME DATA TRANSLATION RULES:**\n"
                "1. For skill descriptions, maintain this format: 'English Skill Name - Thai Description'\n"
                "2. Keep game terms consistent: SP, HP, MP, Cooldown, DPS should remain in English\n"
                "3. For percentages and numbers: '208%' stays as '208%', '3.5m' becomes '3.5 เมตร'\n"
                "4. Time units: '8秒' = '8 วินาที', '3分鐘' = '3 นาที'\n"
                "5. For skill effects, use clear Thai: '造成傷害' = 'สร้างความเสียหาย', '增加' = 'เพิ่ม', '減少' = 'ลด'\n"
                "6. Status effects in brackets: ['狀態名稱'] = \"สถานะ 'ชื่อสถานะ'\"\n"
                "7. Range descriptions: '周圍半徑X米' = 'ในระยะ X เมตร รอบตัว'\n"
                "**GENERAL RULES:**\n"
                "8. Translate the text COMPLETELY from Taiwanese (Traditional Chinese), never cut off or omit any part\n"
                "9. JUST For character names, place names, and other proper nouns, translate them into English. Ensure consistency.\n"
                "10. Use modern Thai vocabulary that sounds natural to Thai gamers\n"
                "11. For skill descriptions, prioritize clarity and understanding over literal translation\n"
                "12. Keep the technical precision but make it readable in Thai\n"
                "13. The final output must NOT contain any original Taiwanese (Traditional Chinese) characters whatsoever.\n"
                "**EXAMPLES OF GOOD TRANSLATIONS:**\n"
                "女神萊瑪 → Goddess Laima\n"
                "能量爆破 → Energy Blast - พลังระเบิด\n"
                "消耗60SP → ใช้ SP: 60\n"
                "冷卻時間8秒 → Cooldown: 8 วินาที\n"
                "對周圍敵人造成攻擊力208%的傷害 → สร้างความเสียหาย 208% ของพลังโจมตี ให้กับศัตรูรอบข้าง\n"
            )

            for term, explanation in special_terms.items():
                prompt += f"{term}: {explanation}\n"

            # แก้ไขบรรทัดสุดท้ายของ prompt
            prompt += f"\nText to translate from Taiwanese (Traditional Chinese) to Thai: {dialogue}"

            prompt += f"\nText to translate from Japanese to Thai: {dialogue}"

            # Debug: แสดงข้อความที่ส่งไป API
            logging.info(f"[DEBUG] Original text: '{text}'")
            logging.info(f"[DEBUG] Dialogue to translate: '{dialogue}'")
            logging.info(f"[DEBUG] Character name: '{character_name}'")

            try:
                # สร้าง Content สำหรับ Gemini API
                generation_config = {
                    "max_output_tokens": self.max_tokens,
                    "temperature": self.temperature,
                    "top_p": self.top_p,
                }

                start_time = time.time()

                # ส่งคำขอไปยัง Gemini API
                response = self.model.generate_content(
                    prompt,
                    generation_config=generation_config,
                    safety_settings=self.safety_settings,
                )

                elapsed_time = time.time() - start_time

                # คำนวณ tokens โดยประมาณ
                input_tokens = len(prompt) // 4
                output_tokens = 0
                total_tokens = input_tokens

                if hasattr(response, "text") and response.text:
                    output_tokens = len(response.text) // 4
                    total_tokens = input_tokens + output_tokens

                logging.info(
                    f"[Gemini JP API] Estimated tokens: ~{input_tokens} (input) + ~{output_tokens} (output) = ~{total_tokens} tokens in {elapsed_time:.2f}s"
                )

                # ดึงข้อความจาก response และตรวจสอบอย่างปลอดภัย
                if hasattr(response, "text") and response.text:
                    translated_text = response.text
                else:
                    raise ValueError("No response text from Gemini JP API")

                # ทำความสะอาดข้อความแปล
                translated_text = re.sub(
                    r"\b(ครับ|ค่ะ|ครับ/ค่ะ)\b", "", translated_text
                ).strip()
                for term in special_terms:
                    translated_text = re.sub(
                        r"\b" + re.escape(term) + r"\b",
                        term,
                        translated_text,
                        flags=re.IGNORECASE,
                    )

                # ตรวจสอบและแทนที่กรณีพิเศษสำหรับเลข 2 และ ???
                if re.match(r"^2+\??$", dialogue.strip()) or dialogue.strip() == "???":
                    translated_text = "???"

                # ตรวจสอบกรณีเลข 2 เป็นส่วนหนึ่งของประโยค
                if dialogue.strip() and re.match(r"^\s*2+\s*$", dialogue.strip()):
                    translated_text = "???"

                # สร้างข้อความผลลัพธ์สุดท้าย
                if character_name:
                    # ตรวจสอบเพิ่มเติมหากชื่อตัวละครเป็นเลข 2
                    if (
                        re.match(r"^2+$", character_name)
                        or character_name.strip() == "???"
                    ):
                        character_name = "???"
                    final_translation = f"{character_name}: {translated_text}"
                else:
                    final_translation = translated_text

                # บันทึกลง cache เฉพาะคำแปลที่สมบูรณ์
                if character_name:
                    self.cache.add_validated_name(character_name)  # เพิ่มชื่อเข้า cache

                return final_translation

            except Exception as api_error:
                logging.error(f"Primary API call failed: {str(api_error)}")
                return f"[Translation Error: {str(api_error)}]"

        except Exception as e:
            logging.error(f"Error in translation: {str(e)}")
            return f"[Error: Translation failed - {str(e)}]"

    def translate_choice(self, text):
        """
        แปลข้อความตัวเลือกจากเกมญี่ปุ่น
        แก้ปัญหาการแปลซ้ำโดยการตรวจจับและตัดส่วนหัวข้อออก
        แล้วแปลเฉพาะตัวเลือก จากนั้นติดหัวข้อภาษาไทยแบบตายตัวกลับมา

        Args:
            text (str): ข้อความที่มีโครงสร้าง choice ที่ต้องการแปล (ญี่ปุ่น)

        Returns:
            str: ข้อความที่แปลแล้ว "คุณจะพูดว่าอย่างไร?\nตัวเลือกที่ 1\nตัวเลือกที่ 2"
        """
        try:
            # แยก replace operation ออกมาก่อนเพื่อหลีกเลี่ยง backslash ใน f-string
            text_preview = text[:150].replace("\n", "<NL>")
            logging.info(
                f"TranslatorGemini JP: translate_choice called with input text: '{text_preview}'"
            )

            # ตรวจจับและตัดส่วนหัวข้อภาษาญี่ปุ่นออก
            text_to_translate = text.strip()
            choices_only = text_to_translate

            # รูปแบบที่พบบ่อยของคำถามในเกมที่ใช้ภาษาจีนตัวเต็ม (ไต้หวัน)
            choice_headers = [
                "你要怎麼說？",
                "你要怎麼說?",
                "該怎麼回答？",
                "該怎麼回答?",
                "要怎麼回應？",
                "要怎麼回應?",
            ]

            # ตรวจหาและตัดส่วน header ออก
            header_found = False

            for header_pattern in choice_headers:
                if text_to_translate.startswith(header_pattern):
                    # ตัดส่วน header ออก
                    choices_only = text_to_translate[len(header_pattern) :].strip()
                    header_found = True
                    logging.info(
                        f"TranslatorGemini JP: Detected and removed header pattern: '{header_pattern}'"
                    )
                    break

            # ถ้าไม่พบ header ที่ต้นข้อความ ลองหาในข้อความ
            if not header_found:
                for header_pattern in choice_headers:
                    if header_pattern in text_to_translate:
                        # แยกข้อความโดยใช้ header เป็นตัวแบ่ง
                        parts = text_to_translate.split(header_pattern, 1)
                        if len(parts) > 1:
                            choices_only = parts[1].strip()
                            header_found = True
                            logging.info(
                                f"TranslatorGemini JP: Found and removed header pattern in text: '{header_pattern}'"
                            )
                            break

            if not header_found:
                logging.info(
                    "TranslatorGemini JP: No Japanese choice header detected, translating full text"
                )
            else:
                logging.info(
                    f"TranslatorGemini JP: After header removal, choices text: '{choices_only[:100]}...'"
                )

            # ถ้าไม่มีข้อความหลังตัด header ให้ใช้ข้อความเดิม
            if not choices_only.strip():
                choices_only = text_to_translate
                logging.info(
                    "TranslatorGemini JP: Empty choices after header removal, using original text"
                )

            # ใช้ prompt สำหรับแปลเฉพาะตัวเลือกจากญี่ปุ่น
            prompt_parts = [
                "You are a highly skilled translator for the game Final Fantasy XIV.",
                "Translate the following player choice options from Taiwanese (Traditional Chinese) to Thai.",
                "Each choice option should be translated as a natural, concise Thai phrase suitable for game dialogue selection.",
                "CRITICAL REQUIREMENTS:",
                "1. Translate each choice option from Taiwanese (Traditional Chinese) into natural Thai.",
                "2. Preserve the newline structure exactly - each choice on its own line.",
                "3. Output ONLY the Thai translation. NO Chinese, NO explanations, NO prefixes.",
                "4. Preserve proper names and character names as they appear in the original.",
                "5. **PRONOUNS**: Use 'คุณ' instead of 'แก' for politeness - these are player dialogue choices.",
                "6. **AVOID FORMAL LANGUAGE**: Never use 'ข้าพเจ้า' - use 'ฉัน' or 'ข้า' for first person instead.",
                "7. **Chinese considerations**: Handle sentence-ending particles (嗎, 吧, etc.) appropriately and keep Thai natural.",
                "8. Use modern, natural Thai expressions that sound appropriate for player responses.",
                "",
                f"CHOICE OPTIONS TO TRANSLATE (FROM TAIWANESE/TRADITIONAL CHINESE):\n{choices_only}",
                "",
                "TRANSLATED CHOICES (Thai only):",
            ]

            prompt = "\n".join(prompt_parts)

            generation_config = {
                "max_output_tokens": self.max_tokens,
                "temperature": self.temperature,
                "top_p": self.top_p,
            }

            start_time = time.time()

            # ส่งคำขอไปยัง Gemini API
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config,
                safety_settings=self.safety_settings,
            )

            elapsed_time = time.time() - start_time

            # คำนวณ tokens โดยประมาณ
            prompt_tokens_est = len(prompt) // 4
            completion_tokens_est = (
                len(response.text) // 4
                if hasattr(response, "text") and response.text
                else 0
            )

            # แยก replace operation ออกมาก่อน
            text_short_preview = text[:30].replace("\n", "<NL>")

            logging.info(
                f"[Gemini JP API - Choice] Est. Tokens: P~{prompt_tokens_est}, C~{completion_tokens_est}. Time: {elapsed_time:.2f}s. Input: '{text_short_preview}'"
            )

            if hasattr(response, "text") and response.text:
                translated_choices = response.text
                # แยก replace operation ออกมาก่อน
                translated_choices = translated_choices.replace(
                    "Japanese:", ""
                ).replace("Japanese :", "")
                translated_choices = translated_choices.replace("จากญี่ปุ่น:", "").replace(
                    "ภาษาญี่ปุ่น:", ""
                )

                # Basic cleaning
                translated_choices = translated_choices.replace("Thai:", "").replace(
                    "Thai :", ""
                )
                translated_choices = translated_choices.replace("ไทย:", "").replace(
                    "ภาษาไทย:", ""
                )

                # Additional cleaning for unwanted prefixes
                prefixes_to_remove = [
                    "TRANSLATED CHOICES (Thai only):",
                    "การแปล:",
                ]
                for prefix in prefixes_to_remove:
                    if translated_choices.strip().startswith(prefix):
                        translated_choices = translated_choices.replace(
                            prefix, "", 1
                        ).strip()
                        break

                # ติดหัวข้อ "คุณจะพูดว่าอย่างไร?" แบบตายตัวกลับมา
                final_result = f"คุณจะพูดว่าอย่างไร?\n{translated_choices.strip()}"

                # แยก replace operation ออกมาก่อน
                final_preview = final_result[:150].replace("\n", "<NL>")
                logging.info(
                    f"TranslatorGemini JP: Final choice translation result: '{final_preview}'"
                )

                return final_result
            else:
                # แยก replace operation ออกมาก่อน
                text_error_preview = text[:70].replace("\n", "<NL>")
                logging.error(
                    f"TranslatorGemini JP: No response text from Gemini API for choice: '{text_error_preview}'"
                )
                # ติดหัวข้อไทยแม้เกิด error
                return f"คุณจะพูดว่าอย่างไร?\n[Gemini Error: No Translation]\n{text}"

        except Exception as e:
            # แยก replace operation ออกมาก่อน
            text_exception_preview = text[:70].replace("\n", "<NL>")
            logging.error(
                f"TranslatorGemini JP: Error in translate_choice: {str(e)}, Input: '{text_exception_preview}'"
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
                "lastName": "",
                "gender": "Unknown",
                "role": "Mystery character",
                "relationship": "Unknown",
            }

        for char in self.character_data:
            if (
                char.get("firstName") == character_name
                or character_name == f"{char['firstName']} {char['lastName']}".strip()
            ):
                return char
        return None

    def is_skill_description(self, text):
        """ตรวจสอบว่าข้อความเป็นข้อมูลสกิลหรือไม่"""
        try:
            import re

            # ตรวจสอบคำสำคัญของสกิล
            skill_keywords = [
                "能量",
                "攻擊",
                "傷害",
                "冷卻",
                "消耗",
                "SP",
                "範圍",
                "效果",
                "狀態",
            ]
            number_patterns = [r"\d+%", r"\d+秒", r"\d+SP", r"\d+\.?\d*m"]

            # ตรวจสอบว่ามีคำสำคัญสกิล
            has_skill_keyword = any(keyword in text for keyword in skill_keywords)

            # ตรวจสอบว่ามีรูปแบบตัวเลข
            has_numbers = any(re.search(pattern, text) for pattern in number_patterns)

            # ตรวจสอบว่ามีโครงสร้างข้อมูลสกิล
            has_skill_structure = (
                ("造成" in text and "傷害" in text)
                or ("增加" in text)
                or ("減少" in text)
            )

            return has_skill_keyword and (has_numbers or has_skill_structure)

        except Exception as e:
            logging.warning(f"Error checking skill description: {e}")
            return False

    def is_similar_to_choice_prompt(self, text):
        """ตรวจสอบว่าข้อความมีลักษณะคล้ายกับ choice prompt หรือไม่ (สำหรับญี่ปุ่น)"""
        try:
            text_lower = text.lower().strip()

            # รูปแบบคำถามในเกมที่ใช้ภาษาจีนตัวเต็ม (ไต้หวัน)
            choice_patterns = ["你要怎麼說", "該怎麼回答", "要怎麼回應"]

            # ตรวจสอบว่ามีรูปแบบคำถามหรือไม่
            has_question = any(pattern in text for pattern in choice_patterns)

            if has_question:
                # แยกส่วนคำถามและตัวเลือก
                for pattern in choice_patterns:
                    if pattern in text:
                        parts = text.split(pattern, 1)
                        if len(parts) > 1:
                            prompt_part = pattern
                            choices_part = parts[1].strip()
                            return True, prompt_part, choices_part

            return False, "", ""

        except Exception as e:
            logging.warning(f"Error checking Japanese choice prompt: {str(e)}")
            return False, "", ""

    def process_preset_area_c(self, ocr_text, preset_info=None):
        """
        ประมวลผล OCR text สำหรับ Area C (Lore text)
        สำหรับการแปลข้อความ lore และเนื้อเรื่อง
        """
        try:
            # สำหรับ lore text ให้แปลแบบ direct translation
            return self.translate(ocr_text, source_lang="Japanese", target_lang="Thai")
        except Exception as e:
            logging.warning(
                f"Lore processing failed: {e}, falling back to normal translation"
            )
            return self.translate(ocr_text, source_lang="Japanese", target_lang="Thai")

    def reload_data(self):
        """โหลดข้อมูลใหม่และล้าง cache"""
        print("TranslatorGemini JP: Reloading NPC data...")
        self.load_npc_data()
        self.load_example_translations()
        self.cache.clear_session()
        self.last_translations.clear()
        print("TranslatorGemini JP: Data reloaded successfully")

    def batch_translate(self, texts, batch_size=5):
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
            "As a translation quality assessor, evaluate the following translation from Japanese to Thai. "
            "Consider factors such as accuracy, naturalness, and preservation of the original tone and style. "
            f"Original Japanese: {original_text}\n"
            f"Thai Translation: {translated_text}\n"
            "Provide a brief assessment and a score out of 10."
        )

        try:
            # ส่งคำขอไปยัง Gemini API
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "max_output_tokens": 200,
                    "temperature": 0.3,
                    "top_p": 0.8,
                },
                safety_settings=self.safety_settings,
            )

            if hasattr(response, "text") and response.text:
                return response.text.strip()
            else:
                return "Unable to assess translation quality - no response."

        except Exception as e:
            logging.error(f"Error in translation quality analysis: {str(e)}")
            return "Unable to assess translation quality due to an error."

    def analyze_custom_prompt(self, prompt_with_text):
        """Process a custom prompt with AI"""
        try:
            response = self.model.generate_content(
                prompt_with_text,
                generation_config={
                    "max_output_tokens": self.max_tokens,
                    "temperature": self.temperature,
                    "top_p": self.top_p,
                },
                safety_settings=self.safety_settings,
            )

            if hasattr(response, "text") and response.text:
                return response.text.strip()
            else:
                return "[No response from AI]"

        except Exception as e:
            logging.error(f"Error in custom prompt analysis: {e}")
            raise ValueError(f"Failed to process text with AI: {str(e)}")

    def force_retranslate(
        self, original_text, previous_translation=None, min_quality_score=6.5
    ):
        """
        บังคับให้แปลใหม่ด้วยพารามิเตอร์ที่เข้มข้นกว่า

        Args:
            original_text: ข้อความต้นฉบับภาษาญี่ปุ่น
            previous_translation: การแปลก่อนหน้านี้ (ถ้ามี)
            min_quality_score: คะแนนคุณภาพขั้นต่ำที่ยอมรับได้ (0-10)

        Returns:
            str: ข้อความที่แปลใหม่หรือปรับปรุงแล้ว
        """
        try:
            logging.info(f"Force retranslation triggered for: {original_text[:50]}...")

            # ถ้าไม่มีการแปลก่อนหน้า ให้แปลก่อน
            if not previous_translation:
                previous_translation = self.translate(original_text)

            # ตรวจสอบคุณภาพการแปลก่อนหน้า
            quality_assessment = self.analyze_translation_quality(
                original_text, previous_translation
            )

            # ปรับพารามิเตอร์ให้เข้มข้นขึ้น
            enhanced_temp = min(0.9, self.temperature + 0.2)
            enhanced_top_p = min(0.95, self.top_p + 0.05)

            # สร้าง model instance ใหม่สำหรับการแปลที่เข้มข้นขึ้น
            enhanced_model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config={
                    "max_output_tokens": int(self.max_tokens * 1.2),
                    "temperature": enhanced_temp,
                    "top_p": enhanced_top_p,
                },
                safety_settings=self.safety_settings,
            )

            # สร้าง prompt ที่เข้มข้นขึ้นพร้อมตัวอย่างการแปลที่ไม่ดี
            enhanced_prompt = (
                "You are an expert Japanese to Thai translator with years of experience in game localization. "
                "The previous translation was rated as inadequate.\n\n"
                f"Original Japanese text: {original_text}\n"
                f"Previous translation (NOT GOOD ENOUGH): {previous_translation}\n\n"
                "Problems with the previous translation: "
                f"{quality_assessment}\n\n"
                "Rules for your improved translation:\n"
                "1. Focus on natural, flowing Thai that captures the original meaning precisely\n"
                "2. Maintain the character's tone, style, and personality\n"
                "3. Use contemporary Thai expressions that feel natural to modern speakers\n"
                "4. NEVER use polite endings like ครับ/ค่ะ unless they're in the original\n"
                "5. Preserve all character names exactly as they appear\n"
                "6. Fully capture the meaning, nuance, and emotion of the original text\n"
                "7. Handle Japanese keigo and politeness levels appropriately for Thai context\n"
                f"\nProvide ONLY your improved Thai translation of: {original_text}"
            )

            # แปลใหม่ด้วย prompt ที่ปรับปรุงแล้ว
            start_time = time.time()

            response = enhanced_model.generate_content(
                enhanced_prompt,
                generation_config={
                    "max_output_tokens": int(self.max_tokens * 1.2),
                    "temperature": enhanced_temp,
                    "top_p": enhanced_top_p,
                },
                safety_settings=self.safety_settings,
            )

            elapsed_time = time.time() - start_time

            if hasattr(response, "text") and response.text:
                improved_translation = response.text.strip()

                # ทำความสะอาด
                improved_translation = re.sub(
                    r"\b(ครับ|ค่ะ|ครับ/ค่ะ)\b", "", improved_translation
                ).strip()

                logging.info(
                    f"Force retranslation completed in {elapsed_time:.2f}s: {improved_translation[:50]}..."
                )

                return improved_translation
            else:
                logging.warning(
                    "Force retranslation failed, returning previous translation"
                )
                return previous_translation

        except Exception as e:
            logging.error(f"Error in force retranslation: {str(e)}")
            print(f"เกิดข้อผิดพลาดในการแปลใหม่: {str(e)}")
            # กรณีเกิดข้อผิดพลาด ให้คืนค่าการแปลเดิม
            return previous_translation if previous_translation else original_text

    def _extract_choices_by_starters(self, text, starters):
        """แยกตัวเลือกจากข้อความโดยใช้คำเริ่มต้นที่กำหนด (สำหรับญี่ปุ่น)

        Args:
            text: ข้อความที่ต้องการแยกตัวเลือก
            starters: list ของคำเริ่มต้น เช่น ["1.", "2."]

        Returns:
            list: รายการของตัวเลือกที่แยกได้
        """
        try:
            choices = []
            lines = text.split("\n")
            current_choice = ""
            current_starter = None

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # ตรวจสอบว่าบรรทัดนี้เริ่มด้วย starter หรือไม่
                found_starter = None
                for starter in starters:
                    if line.startswith(starter):
                        found_starter = starter
                        break

                if found_starter:
                    # ถ้าเจอ starter ใหม่ และมี choice เก่าอยู่ ให้บันทึก choice เก่าก่อน
                    if current_starter and current_choice:
                        choices.append(f"{current_starter} {current_choice.strip()}")

                    # เริ่ม choice ใหม่
                    current_starter = found_starter
                    current_choice = line[len(found_starter) :].strip()
                else:
                    # ถ้าไม่ใช่ starter ใหม่ แต่มี choice ปัจจุบันอยู่ ให้เชื่อมต่อ
                    if current_starter:
                        current_choice += " " + line

            # เพิ่ม choice สุดท้าย
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
