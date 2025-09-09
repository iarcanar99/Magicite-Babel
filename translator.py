import openai
from openai import OpenAI
import os
from dotenv import load_dotenv
import re
import tkinter as tk
from tkinter import messagebox
import json
import difflib
import time
import logging
import numpy as np
from enum import Enum
from text_corrector import TextCorrector, DialogueType
from dialogue_cache import DialogueCache
import requests

load_dotenv()


class Translator:
    def __init__(self, settings=None):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in .env file")
        # สร้าง client OpenAI แบบใหม่
        self.client = OpenAI(api_key=self.api_key)

        # ใช้ settings object ถ้ามี
        if settings:
            api_params = settings.get_api_parameters()
            self.model = api_params.get("model", "gpt-4o")
            self.max_tokens = api_params.get("max_tokens", 500)
            self.temperature = api_params.get("temperature", 0.7)
            self.top_p = api_params.get("top_p", 0.9)
        else:
            # ถ้าไม่มี settings ให้โหลดจากไฟล์
            try:
                with open("settings.json", "r") as f:
                    settings_data = json.load(f)
                    api_params = settings_data.get("api_parameters", {})
                    self.model = api_params.get("model", "gpt-4o")
                    self.max_tokens = api_params.get("max_tokens", 500)
                    self.temperature = api_params.get("temperature", 0.7)
                    self.top_p = api_params.get("top_p", 0.9)
            except (FileNotFoundError, json.JSONDecodeError):
                self.model = "gpt-4o"
                self.max_tokens = 500
                self.temperature = 0.7
                self.top_p = 0.9
                logging.warning("Could not load settings.json, using default values")

        self.cache = DialogueCache()
        self.last_translations = {}
        self.character_names_cache = set()
        self.text_corrector = TextCorrector()
        self.load_npc_data()
        self.load_example_translations()

    def get_current_parameters(self):
        """Return current translation parameters"""
        return {
            "model": self.model,  # สำหรับ GPT ใช้ค่าเดียวกันทั้ง model และ displayed_model
            "displayed_model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
        }

    def load_npc_data(self):
        try:
            with open("NPC.json", "r", encoding="utf-8") as file:
                npc_data = json.load(file)
                self.character_data = npc_data["main_characters"]
                self.context_data = npc_data["lore"]
                self.character_styles = npc_data["character_roles"]

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

                # Load NPCs
                for npc in npc_data["npcs"]:
                    self.character_names_cache.add(npc["name"])

                logging.info(
                    "Translator: Loaded NPC.json successfully"
                )  # เปลี่ยนเป็น logging แทน print

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
            # ตัวอย่างประโยคยาว
            # Y'shtola - เพิ่มความเป็นสาวเฟียส มากประสบการณ์ เชือดเฉือน
            "This is no different from the teleportation magicks to which we are all accustomed, magicks that allow for the transportation of those inanimate objects one considers to be an extension of oneself.": "สิ่งนี้ไม่ต่างอะไรจากวิชาวาร์ปที่พวกเราคุ้นเคยกันดี วิชาที่อนุญาตให้เคลื่อนย้ายวัตถุไร้ชีวิตที่เราถือว่าเป็นส่วนขยายของตัวตนเรา",
            "I myself have plenty of regrets, and one day they'll die with me. Gone to dust with my good deeds and unfulfilled dreams.": "ตัวข้าเองก็มีความเสียใจมากมาย และวันหนึ่งมันก็จะตายไปพร้อมกับข้า สลายเป็นธุลีพร้อมกับการกระทำดีและความฝันที่ไม่เคยเป็นจริง",
            "While I appreciate your advice, I will not heed it. Convinced though you may be of this truth, it is yours and not mine.": "แม้ข้าจะซาบซึ้งในคำแนะนำของท่าน แต่ข้าจะไม่ทำตาม ท่านอาจมั่นใจในความจริงของท่าน แต่นั่นคือของท่าน ไม่ใช่ของข้า",
            # Urianger - ภาษาโบราณ ซับซ้อน
            "Thine arrival is timely as ever. Thou didst chance to overhear my conversation with Livingway, I presume.": "การมาถึงของท่านช่างเหมาะเวลายิ่งนัก ข้าเดาว่าท่านคงบังเอิญได้ยินบทสนทนาของข้ากับ Livingway",
            "When G'raha Tia did contrive to deliver the First at the price of his own life, I was complicit in the scheme. A sacrifice averted, for a mercy.": "เมื่อ G'raha Tia วางแผนช่วย the First โดยแลกด้วยชีวิตของเขาเอง ข้าร่วมสมรู้ในแผนการนั้น การเสียสละที่ถูกยับยั้ง ด้วยความเมตตา",
            "Selfish wants born of everlasting regrets. Most days I put them from my mind, but could think of naught else when asked to swallow the same bitter draught. Subterfuge and sacrifice. Mayhap the right moral choice, but one I regard with great trepidation.": "ความปรารถนาอันเห็นแก่ตัวที่เกิดจากความเสียใจอันไม่รู้จบ วันส่วนใหญ่ข้าขับไล่มันออกจากความคิด แต่กลับนึกถึงแต่สิ่งเหล่านี้เมื่อถูกขอให้กลืนยาขมรสเดียวกัน การหลอกลวงและการเสียสละ อาจเป็นทางเลือกทางศีลธรรมที่ถูกต้อง แต่เป็นสิ่งที่ข้าหวั่นเกรงยิ่งนัก",
            # G'raha Tia - เพิ่มความอยากรู้อยากเห็น เนิร์ดประวัติศาสตร์
            "A facility for processing souls. As distressing as the very concept is, I confess I'm curious to see the technology employed.": "สถานที่สำหรับประมวลผลวิญญาณงั้นเหรอ! แม้แนวคิดนี้จะชวนให้หวาดวิตก แต่ผมขอสารภาพว่าอดสงสัยไม่ได้ว่าพวกเขาใช้เทคโนโลยีอะไรกัน",
            "Is this a dead star?": "นี่เป็นดาวที่ตายแล้วใช่ไหม? น่าทึ่งจัง... ไม่คิดว่าจะได้เห็นกับตาตัวเอง",
            "There's a wind!": "มีลมพัดมา! นี่อาจเป็นร่องรอยประวัติศาสตร์ที่สำคัญ!",
            # Alphinaud - กึ่งทางการ แฝงความเป็นเด็กหนุ่ม
            "What? Their world is dead?": "อะไรนะ? โลกของพวกเขาตายไปแล้วเหรอ? ไม่น่าเชื่อเลย...",
            "Come, let us follow the wind. It will not lead us astray. He would not.": "มาเถอะ ตามลมนี้ไป มันคงไม่นำเราหลงทาง เขาคงไม่ทำแบบนั้นกับเราหรอก",
            "But we accept this. That our existence may seem pointless. That sorrow, rage and despair will always dog our heels. And we press on regardless!": "แต่เราก็ยอมรับมันนะ ว่าการมีชีวิตอยู่ของเราอาจดูไร้ความหมาย ว่าความเศร้า ความโกรธ และความสิ้นหวังจะไล่ตามเราไปตลอด แต่เราก็ก้าวต่อไปอยู่ดี!",
            # Venat/Hydaelyn - เพิ่มความฉลาด อบอุ่น มีวิสัยทัศน์
            "We must find a way to defeat despair. To unite and prepare as many as possible for the struggle ahead.": "พวกเราต้องหาหนทางเอาชนะความสิ้นหวัง เพื่อรวมใจและเตรียมพร้อมให้มากที่สุดเท่าที่จะทำได้ สำหรับการต่อสู้ที่รออยู่เบื้องหน้า",
            "I have faith in mankind's potential. As long as he believes in himself, there is naught he cannot achieve. So I will not give up on him. On us.": "ข้ามีศรัทธาในศักยภาพของมนุษยชาติ ตราบใดที่มนุษย์เชื่อมั่นในตนเอง ไม่มีสิ่งใดที่พวกเขาทำไม่ได้ ข้าจึงจะไม่ยอมแพ้ในตัวพวกเขา ในพวกเรา",
            "Fare you well, my light of the future. Till we meet again.": "เดินทางให้ปลอดภัย แสงสว่างแห่งอนาคตของข้า จนกว่าเราจะพบกันอีกครั้ง",
            # ตัวละครรอง (1 ประโยคต่อตัวละคร)
            # Meteion - เย็นชา/สองบุคลิก
            "True salvation lies not in dying. It lies in not being born. This is the gift I would give to you. To all life on beautiful Etheirys.": "การหลุดพ้นที่แท้จริงไม่ได้อยู่ที่การตาย แต่อยู่ที่การไม่ได้ถือกำเนิด นี่คือของขวัญที่ข้าจะมอบให้เจ้า ให้แก่สรรพชีวิตบน Etheirys อันงดงาม",
            # Estinien - นักรบมังกร
            "Yet lasting peace does not come to those who simply retreat from conflict. You must be willing to confront it. To stare into the face of your foe and see yourself in him.": "สันติภาพที่ยั่งยืนไม่ได้มาจากการเพียงแค่ถอยหนีจากความขัดแย้ง เจ้าต้องกล้าที่จะเผชิญหน้ากับมัน กล้าที่จะจ้องมองใบหน้าศัตรู และเห็นตัวเองในตัวเขา",
            # Alisaie
            "That's right! Our quest doesn't end here. We'll press on and we will find you!": "ใช่แล้ว! ภารกิจของเราไม่จบแค่นี้หรอก เราจะมุ่งหน้าต่อไป แล้วเราจะตามหาเธอให้เจอ!",
            # Livingway
            "As I live and breathe! I live and breathe! The environment itself shouldn't kill us.": "ในเมื่อฉันยังมีชีวิตและหายใจอยู่! ฉันยังหายใจได้อยู่นะ! สภาพแวดล้อมนี้ไม่น่าจะฆ่าพวกเราได้หรอก",
            # ChaiNuzz
            "To do so would be little different from entrusting our affairs to Lord Vauthry. We must learn to stand on our own two feet, and I would have them present to witness my attempt.": "การทำเช่นนั้นก็ไม่ต่างกับการมอบกิจการของเราให้ลอร์ด Vauthry ดูแล พวกเรา...พวกเราต้องเรียนรู้ที่จะยืนบนขาของตัวเอง และข้า...ข้าอยากให้พวกเขาอยู่ที่นี่...เพื่อเป็นพยานในความพยายามของข้า",
            # Varshahn
            "I am Varshahn, Servant to the satrap. My task was in fact to wake these good men and women. If you will allow...": "ข้าคือ Varshahn ผู้รับใช้ของผู้ปกครอง ภารกิจของข้าคือการปลุกสุภาพบุรุษและสุภาพสตรีเหล่านี้ หากท่านอนุญาต...",
            # Cophcoodg
            "Intellect was once our pride. Overnight it became our shame. Our works, monuments to futility.": "ปัญญาเคยเป็นความภาคภูมิของพวกเรา แล้วเพียงชั่วข้ามคืน มันกลับกลายเป็นความอัปยศ ผลงานของเรา กลายเป็นอนุสรณ์แห่งความสูญเปล่า",
        }

    def update_parameters(
        self, model=None, max_tokens=None, temperature=None, top_p=None, **kwargs
    ):
        """อัพเดทค่าพารามิเตอร์สำหรับการแปล"""
        try:
            old_params = {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "top_p": self.top_p,
            }

            changes = []

            if model is not None:
                valid_models = ["gpt-4o", "gpt-4o-mini"]
                if model not in valid_models:
                    raise ValueError(
                        f"Invalid model for GPT translator. Must be one of: {', '.join(valid_models)}"
                    )
                self.model = model  # model ID และ displayed_model เป็นค่าเดียวกันสำหรับ GPT
                changes.append(f"Model: {old_params['model']} -> {model}")

            if max_tokens is not None:
                if not (100 <= max_tokens <= 1000):
                    raise ValueError(
                        f"Max tokens must be between 100 and 1000, got {max_tokens}"
                    )
                self.max_tokens = max_tokens
                changes.append(
                    f"Max tokens: {old_params['max_tokens']} -> {max_tokens}"
                )

            if temperature is not None:
                if not (0.5 <= temperature <= 0.9):
                    raise ValueError(
                        f"Temperature must be between 0.5 and 0.9, got {temperature}"
                    )
                self.temperature = temperature
                changes.append(
                    f"Temperature: {old_params['temperature']} -> {temperature}"
                )

            if top_p is not None:
                if not (0.5 <= top_p <= 0.9):
                    raise ValueError(f"Top P must be between 0.5 and 0.9, got {top_p}")
                self.top_p = top_p
                changes.append(f"Top P: {old_params['top_p']} -> {top_p}")

            if changes:
                print("\n=== GPT Parameters Updated ===")
                for change in changes:
                    print(change)
                print(f"Current model: {self.model}")
                print("==========================\n")

            return True, None

        except ValueError as e:
            print(f"[GPT] Parameter update failed: {str(e)}")
            return False, str(e)

    def _call_openai_api(
        self, model, messages, temperature, max_tokens=None, top_p=None
    ):
        """เรียกใช้ OpenAI API และวัดประสิทธิภาพ"""
        try:
            # บันทึกเวลาเริ่มต้น
            start_time = time.time()

            # กำหนดพารามิเตอร์
            params = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
            }

            if max_tokens is not None:
                params["max_tokens"] = max_tokens

            if top_p is not None:
                params["top_p"] = top_p

            # เรียกใช้ API
            if hasattr(self, "client") and self.client:
                response = self.client.chat.completions.create(**params)
            else:
                response = openai.ChatCompletion.create(**params)

            # คำนวณเวลาที่ใช้
            elapsed_time = time.time() - start_time

            # แสดงข้อมูลการใช้ token
            if hasattr(response, "usage"):
                prompt_tokens = response.usage.prompt_tokens
                completion_tokens = response.usage.completion_tokens
                total_tokens = response.usage.total_tokens

                # แสดงข้อมูลในคอนโซล
                print(
                    f"                                            ", end="\r"
                )  # เคลียร์บรรทัด
                model_display = model
                # ถ้าเป็น GPT-4o-mini ให้แสดงเต็มๆ ไม่ย่อ
                if model.startswith("gpt-"):
                    model_display = model.upper()  # แปลงเป็นตัวใหญ่ทั้งหมดให้เห็นชัดเจน

                first_message = (
                    messages[-1]["content"][:30]
                    if messages and len(messages) > 0
                    else ""
                )
                print(
                    f"[{model_display}] : {first_message}... -> {total_tokens} tokens ({elapsed_time:.2f}s)"
                )
                logging.info(
                    f"[OpenAI API] Tokens: {prompt_tokens} (prompt) + {completion_tokens} (completion) = {total_tokens} tokens in {elapsed_time:.2f}s"
                )

            return response

        except Exception as e:
            logging.error(f"Error calling OpenAI API: {e}")
            raise

    def translate(
        self, text, source_lang="English", target_lang="Thai", is_choice_option=False
    ):
        """
        แปลข้อความพร้อมจัดการบริบทของตัวละคร
        Args:
            text: ข้อความที่ต้องการแปล
            source_lang: ภาษาต้นฉบับ (default: English)
            target_lang: ภาษาเป้าหมาย (default: Thai)
            is_choice_option: เป็นข้อความตัวเลือกหรือไม่ (default: False)
        Returns:
            str: ข้อความที่แปลแล้ว
        """
        try:
            if not text:
                logging.warning("Empty text received for translation")
                return ""

            # แสดงข้อความเริ่มการแปลในคอนโซล
            print(f"กำลังแปล: {text[:30]}..." + " " * 20, end="\r")

            # ใช้ text_corrector instance ที่สร้างไว้แล้ว
            speaker, content, dialogue_type = (
                self.text_corrector.split_speaker_and_content(text)
            )

            # เพิ่มการตรวจสอบพิเศษสำหรับ 22
            if text.strip() in ["22", "22?", "222", "222?"]:
                return "???"

            # กรณีพิเศษสำหรับ ??? หรือ 222
            if text.strip() in ["222", "222?", "???"]:
                return "???"

            # ตรวจสอบว่าเป็นข้อความตัวเลือกหรือไม่
            if not is_choice_option:
                is_choice, prompt_part, choices = self.is_similar_to_choice_prompt(text)
                if is_choice:
                    return self.translate_choice(text)

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
            example_prompt = "Here are examples of good translations:\\n\\n"
            for eng, thai in self.example_translations.items():
                example_prompt += f"English: {eng}\\nThai: {thai}\\n\\n"

            prompt = (
                "You are a professional translator specializing in video game localization for Final Fantasy XIV. "
                "Your task is to translate English game text to Thai with these requirements:\\n"
                "1. Translate the text naturally while preserving the character's tone and style\\n"
                "2. NEVER translate any character names, place names, or special terms that appear in the database\\n"
                "3. For any terms found in 'Special terms' section below, use the Thai explanations provided instead of translating directly\\n"
                "4. When encountering archaic/medieval English (e.g., 'thee', 'thou', 'wouldst'), translate to elegant Thai that conveys similar historical weight\\n"
                "5. For very short text, treat it as either: phrase, exclamation, or name calling only\\n"
                "6. If the text contains unclear parts, translate what you can understand and mark unclear parts with [...]\\n"
                "7. Maintain character speech patterns and emotional expressions as described in 'Character's style'\\n"
                "8. Use ellipsis (...) or em dash (—) for pauses as in the original\\n"
                "9. Avoid formal polite particles (ครับ/ค่ะ) unless specified in character's style\\n"
                "10. Focus on natural, conversational Thai that matches the game context and the character's unique voice\\n"
                f"Context: {context}\\n"
                f"Character's style: {character_style}\\n"
                f"Do not translate (use exactly as written): {', '.join(self.character_names_cache)}\\n\\n"
                "Special terms (use these Thai explanations instead of translating):\\n"
            )

            for term, explanation in special_terms.items():
                prompt += f"{term}: {explanation}\\n"
            prompt += f"\\n{example_prompt}\\nText to translate: {dialogue}"

            try:
                response = self._call_openai_api(
                    self.model,
                    [{"role": "user", "content": prompt}],
                    self.temperature,
                    self.max_tokens,
                    self.top_p,
                )
                translated_dialogue = response.choices[0].message.content.strip()

                # เพิ่มโค้ดนี้เพื่อลบ "Thai:" prefix
                if translated_dialogue.startswith("Thai:"):
                    translated_dialogue = translated_dialogue[
                        5:
                    ].strip()  # ตัด "Thai:" และช่องว่างออก

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

                # บันทึกลง cache
                self.last_translations[dialogue] = translated_dialogue

                if character_name:
                    self.cache.add_validated_name(character_name)  # เพิ่มชื่อเข้า cache
                    return f"{character_name}: {translated_dialogue}"
                return translated_dialogue

            except ValueError as e:
                logging.error(f"Error in is_similar_to_choice_prompt: {str(e)}")
                return self.translate_choice(text)

        except Exception as e:
            logging.error(f"Unexpected error in translation: {str(e)}")
            return f"[Error: {str(e)}]"

    def is_similar_to_choice_prompt(
        self, text, threshold=0.7
    ):  # ลดระดับ threshold ลงเพื่อความยืดหยุ่น
        """
        ตรวจสอบและแยกส่วนประกอบของ choice dialogue ด้วยความยืดหยุ่นที่มากขึ้น
        Returns:
            tuple: (is_choice, prompt_part, choices)
        """
        try:
            # 1. ถ้าไม่มีข้อความหรือสั้นเกินไป ถือว่าไม่ใช่ choice
            if not text or len(text) < 5:  # ปรับลดขนาดขั้นต่ำลง
                return False, None, []

            # 2. ตัวอย่างรูปแบบ header ที่ต้องตรวจจับ - เพิ่มรูปแบบที่อาจมี OCR errors
            choice_headers = [
                "What will you say?",
                "What will you say",  # ไม่มี ?
                "What wiII you say?",  # OCR อาจเข้าใจผิดระหว่าง l กับ I
                "What wlll you say?",  # OCR อาจเข้าใจผิดระหว่าง i กับ l
                "VVhat will you say?",  # OCR อาจเข้าใจผิดระหว่าง W กับ VV
                "What will you do?",
                "Select an option.",
                "Choose your response.",
                "คุณจะพูดว่าอย่างไร?",
            ]

            # 3. ตรวจสอบโดยใช้ fuzzy matching สำหรับความยืดหยุ่นมากขึ้น
            for header in choice_headers:
                # ใช้การตรวจสอบแบบยืดหยุ่นมากขึ้น
                clean_header = header.lower().replace("?", "").replace(".", "").strip()
                clean_text = text.lower().replace("?", "").replace(".", "").strip()

                if clean_header in clean_text:
                    # หาตำแหน่งที่ใกล้เคียงที่สุดในข้อความ
                    idx = clean_text.find(clean_header)
                    if idx <= 10:  # ถ้าพบใกล้กับจุดเริ่มต้นของข้อความ
                        # แยกข้อความส่วนที่เหลือหลังจาก header
                        text_parts = re.split(
                            f"{re.escape(clean_header)}",
                            clean_text,
                            flags=re.IGNORECASE,
                            maxsplit=1,
                        )

                        if len(text_parts) > 1:
                            remaining_text = text_parts[1].strip()

                            # 4. แยก header และกำหนดให้เป็นรูปแบบมาตรฐาน
                            header = "What will you say?"

                            # ถ้าพบ header ภาษาไทย
                            if "คุณจะพูด" in clean_text:
                                header = "คุณจะพูดว่าอย่างไร?"

                            # 5. แยกตัวเลือก - ปรับปรุงการแยกตัวเลือก
                            # ลองใช้ newline ก่อน เพราะเป็นตัวแบ่งที่ชัดเจนที่สุด
                            choices = [
                                c.strip()
                                for c in re.split(r"\n+", remaining_text)
                                if c.strip()
                            ]

                            # ถ้าแยกด้วย newline ไม่ได้ ลองใช้เครื่องหมายวรรคตอนอื่นๆ
                            if len(choices) <= 1:
                                choices = [
                                    c.strip()
                                    for c in re.split(r"[.!?]+", remaining_text)
                                    if c.strip()
                                ]

                                # ถ้ายังแยกไม่ได้ ลองแยกด้วยคำเริ่มต้นที่พบบ่อย
                                if len(choices) <= 1:
                                    common_starts = [
                                        "I suppose",
                                        "I think",
                                        "I will",
                                        "I'll",
                                        "I can",
                                        "We should",
                                        "We can",
                                        "We will",
                                        "We'll",
                                        "Yes",
                                        "No",
                                        "Perhaps",
                                        "Maybe",
                                        "The ",
                                        "But ",
                                        "So ",
                                        "You ",
                                        "Let's",
                                        "Please",
                                        "Thank",
                                        "Very",
                                        "We won't",
                                        "We take",  # เพิ่มตามตัวอย่างในภาพ
                                    ]

                                    temp_choices = self._extract_choices_by_starters(
                                        remaining_text, common_starts
                                    )
                                    if temp_choices:
                                        choices = temp_choices

                            # 6. ต้องมีอย่างน้อย 1 ตัวเลือก
                            if choices:
                                return True, header, choices

                    # หากพบ header แต่ไม่สามารถแยกตัวเลือกได้ ให้ระบุ header อย่างเดียว
                    return True, header, []

            return False, None, []

        except Exception as e:
            logging.error(f"Error in is_similar_to_choice_prompt: {str(e)}")
            return False, None, []

    def _extract_choices_by_starters(self, text, starters):
        """แยกตัวเลือกจากข้อความโดยใช้คำเริ่มต้นที่กำหนด"""
        choices = []
        remaining = text

        # เตรียมคำขึ้นต้นสำหรับการตรวจจับด้วย regex
        pattern = "|".join(re.escape(start) for start in starters)

        # แยกด้วย regex
        splits = re.split(f"({pattern})", remaining, flags=re.IGNORECASE)

        # จัดกลุ่มตัวเลือก
        current_choice = ""
        for i, part in enumerate(splits):
            if i == 0 and part.strip():
                # ถ้าส่วนแรกมีเนื้อหา ให้เริ่มตัวเลือกแรก
                current_choice = part.strip()
                if current_choice:
                    choices.append(current_choice)
                    current_choice = ""
            elif part.strip() and any(
                part.lower().startswith(start.lower()) for start in starters
            ):
                # พบคำขึ้นต้นใหม่ เพิ่มตัวเลือกเก่าและเริ่มตัวเลือกใหม่
                if current_choice:
                    choices.append(current_choice)
                current_choice = part.strip()
            elif part.strip():
                # ต่อเนื้อหากับตัวเลือกปัจจุบัน
                current_choice += " " + part.strip()

        # เพิ่มตัวเลือกสุดท้าย
        if current_choice:
            choices.append(current_choice)

        return [c.strip() for c in choices if c.strip()]

    def translate_choice(self, text):
        """แปลข้อความตัวเลือกของผู้เล่น
        Args:
            text: ข้อความที่จะแปล เช่น "What will you say?\nOption 1\nOption 2"
        Returns:
            str: ข้อความที่แปลแล้ว เช่น "คุณจะพูดว่าอย่างไร?\nตัวเลือก 1\nตัวเลือก 2"
        """
        try:
            # 1. ตรวจสอบและแยกส่วนประกอบ
            is_choice, header, choices = self.is_similar_to_choice_prompt(text)

            if is_choice:
                # 2. กำหนด header ภาษาไทยแบบคงที่
                translated_header = "คุณจะพูดว่าอย่างไร?"
                translated_choices = []

                # 3. แปลเฉพาะส่วน choices โดยตัด header ออก
                for choice in choices:
                    choice = choice.strip()
                    if not choice:
                        continue

                    # 4. แปลแต่ละตัวเลือก โดยใช้ is_choice_option=True
                    translated_choice = self.translate(choice, is_choice_option=True)
                    if translated_choice:
                        # 5. ตรวจสอบและป้องกันการซ้ำซ้อนกับ header
                        if translated_choice != translated_header:
                            translated_choices.append(translated_choice)

                # 6. รวมผลลัพธ์ในรูปแบบที่ถูกต้อง
                if translated_choices:
                    # ใช้ \n เพียงครั้งเดียวระหว่าง header และ choices
                    result = f"{translated_header}\n" + "\n".join(translated_choices)
                    logging.debug(f"Choice translation result: {result}")
                    return result

                # 7. กรณีไม่มี choices ส่งคืนเฉพาะ header
                return translated_header

            # 8. กรณีไม่ใช่ข้อความตัวเลือก แปลปกติ
            return self.translate(text)

        except Exception as e:
            logging.error(f"Error in translating choices: {str(e)}")
            return f"[Error in choice translation: {str(e)}]"

    def get_character_info(self, character_name):
        if character_name == "???":
            return {
                "firstName": "???",
                "gender": "unknown",
                "role": "Mystery character",
                "relationship": "Unknown/Mysterious",
                "pronouns": {"subject": "ฉัน", "object": "ฉัน", "possessive": "ของฉัน"},
            }
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
        prompt = (
            "As a translation quality assessor, evaluate the following translation from English to Thai. "
            "Consider factors such as accuracy, naturalness, and preservation of the original tone and style. "
            f"Original (English): {original_text}\n"
            f"Translation (Thai): {translated_text}\n"
            "Provide a brief assessment and a score out of 10."
        )

        try:
            # เปลี่ยนเป็นการใช้ client ใหม่
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": "Assess the translation quality."},
                ],
                max_tokens=200,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logging.error(f"Error in translation quality analysis: {str(e)}")
            return "Unable to assess translation quality due to an error."

    def reload_data(self):
        """โหลดข้อมูลใหม่และล้าง cache"""
        print("Translator: Reloading NPC data...")
        self.load_npc_data()
        self.load_example_translations()
        self.cache.clear_session()
        self.last_translations.clear()
        print("Translator: Data reloaded successfully")

    def analyze_custom_prompt(self, prompt_with_text):
        """
        Process a custom prompt with AI

        Args:
            prompt_with_text: The prompt followed by the text to analyze

        Returns:
            str: The AI response
        """
        try:
            # Build a system message that tells the model to process the JSON data
            system_message = (
                "You are an AI assistant that helps with JSON data analysis and improvement. "
                "You're specialized in working with character data for RPG games and stories. "
                "Process the text according to the instructions provided in the prompt. "
                "When returning JSON, ensure it is properly formatted and valid."
            )

            # Send to API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt_with_text},
                ],
                max_tokens=self.max_tokens
                * 2,  # Double the token limit for JSON analysis
                temperature=self.temperature,
                top_p=self.top_p,
            )

            # Extract and return the response content
            return response.choices[0].message.content.strip()

        except Exception as e:
            logging.error(f"Error in custom prompt analysis: {e}")
            raise ValueError(f"Failed to process text with AI: {str(e)}")


class TranslatorGemini:
    """
    คลาส TranslatorGemini สำหรับให้ import ได้ถูกต้อง
    นี่เป็นเพียงคลาสชั่วคราวเพื่อแก้ไขปัญหาที่ import ไม่ได้
    จะถูกแทนที่ด้วย TranslatorFactory ในอนาคต
    """

    def __init__(self, settings):
        """
        เริ่มต้น TranslatorGemini

        Args:
            settings: อินสแตนซ์ของ Settings
        """
        self.settings = settings
        self.model_name = "GEMINI-2.0-FLASH"  # ใช้ 2.0 Flash เป็นค่าเริ่มต้น
        self.is_active = False
        self.char_limit = 2500
        logging.info(f"Initialized {self.model_name} translator")

    def translate(self, text, source_lang="auto", target_lang="th"):
        """
        แปลข้อความด้วย Gemini (จำลอง)

        Args:
            text: ข้อความที่ต้องการแปล
            source_lang: ภาษาต้นทาง (default: auto)
            target_lang: ภาษาปลายทาง (default: th)

        Returns:
            str: ข้อความที่แปลแล้ว
        """
        # เช็คว่าข้อความว่างหรือไม่
        if not text or len(text.strip()) == 0:
            return ""

        # จำลองการแปล (เพิ่ม [TH] ไว้ข้างหน้า)
        translated = f"[TH] {text}"

        # จำลองความล่าช้าของการแปล
        time.sleep(0.1)

        logging.info(f"Translated: {text[:30]}... -> {translated[:30]}...")
        return translated

    def check_api_key(self):
        """
        ตรวจสอบว่า API key ใช้งานได้หรือไม่

        Returns:
            bool: True ถ้า API key ใช้งานได้
        """
        # จำลองว่า API key ใช้งานได้เสมอ
        return True

    def get_languages(self):
        """
        ดึงรายการภาษาที่รองรับ

        Returns:
            list: รายการภาษาที่รองรับ
        """
        # รายการภาษาจำลอง
        langs = [
            {"code": "en", "name": "English"},
            {"code": "th", "name": "Thai"},
            {"code": "ja", "name": "Japanese"},
            {"code": "ko", "name": "Korean"},
            {"code": "zh", "name": "Chinese"},
        ]
        return langs


if __name__ == "__main__":
    try:
        translator = Translator()

        # ตัวอย่างการแปลข้อความเดี่ยว
        test_cases = [
            "Y'shtola: The aetheric fluctuations in this area are most peculiar.",
            "Y'shtola: We should proceed with caution.",
            "???: Who goes there?",
            "What will you say?\nYes, of course.\nI'm not sure about this.",
            "The wind howls through the ancient ruins.",
        ]

        print("=== Translation Test Cases ===")
        for text in test_cases:
            translated = translator.translate(text)
            print(f"\nOriginal: {text}")
            print(f"Translation: {translated}")

    except ValueError as e:
        print(f"Error: {e}")
