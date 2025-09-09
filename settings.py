import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import logging
from PIL import Image, ImageTk
from translator_factory import TranslatorFactory
from appearance import appearance_manager
from asset_manager import AssetManager
from advance_ui import AdvanceUI
from simplified_hotkey_ui import SimplifiedHotkeyUI  # import จากไฟล์ใหม่
from font_manager import FontUI, initialize_font_manager, FontUIManager
from version_manager import get_settings_version  # สำหรับจัดการเวอร์ชั่น
from utils_appearance import (
    SettingsUITheme,
    ModernButton,
    ModernEntry,
    ModernFrame,
)  # เพิ่ม import ใหม่

# เพิ่ม import สำหรับการจัดการ monitor position
try:
    import win32api
    import win32con

    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False
    print("Warning: win32api not available, using fallback positioning for Settings UI")


def is_valid_hotkey(hotkey):
    hotkey = hotkey.lower()
    valid_keys = set("abcdefghijklmnopqrstuvwxyz0123456789")
    valid_functions = set(
        ["f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "f10", "f11", "f12"]
    )
    valid_modifiers = set(["ctrl", "alt", "shift"])

    parts = hotkey.split("+")

    # กรณีที่มีแค่ key เดียว
    if len(parts) == 1:
        return parts[0] in valid_keys or parts[0] in valid_functions

    # กรณีที่มี modifier และ key
    if len(parts) > 1:
        modifiers = parts[:-1]
        key = parts[-1]
        return all(mod in valid_modifiers for mod in modifiers) and (
            key in valid_keys or key in valid_functions
        )

    return False


# ==================================================================
# ลบคลาส HotkeyUI แบบเก่าออกไปทั้งหมด (HotkeyUI ถูกลบไปแล้ว)
# ==================================================================


class Settings:
    VALID_MODELS = {
        "gemini-2.0-flash-lite": {
            "display_name": "gemini-2.0-flash-lite",
            "type": "gemini",
        },
        "gemini-2.0-flash": {
            "display_name": "gemini-2.0-flash",
            "type": "gemini",
        },
        "gemini-2.5-flash": {
            "display_name": "gemini-2.5-flash",
            "type": "gemini",
        },
    }

    DEFAULT_API_PARAMETERS = {
        # Main parameters for the model
        "model": "gemini-2.0-flash",
        "displayed_model": "gemini-2.0-flash",
        "max_tokens": 500,
        "temperature": 0.8,
        "top_p": 0.9,
        # Additional OCR settings for multiple languages
        "ocr_settings": {
            "languages": ["en", "ja"],
            "confidence_threshold": 0.65,
            "image_preprocessing": {
                "resize_factor": 2.0,
                "contrast": 1.5,
                "sharpness": 1.3,
                "threshold": 128,
            },
        },
        # Translation settings
        "translation_settings": {
            "source_languages": ["en", "ja"],
            "target_language": "th",
            "preserve_names": True,
            "modern_style": True,
            "flirty_tone": True,
            "use_emojis": True,
        },
        # FIX: แก้ไขส่วนจัดการอักขระพิเศษให้รองรับภาษาญี่ปุ่น
        "special_chars": {
            # เพิ่มช่วงอักขระภาษาญี่ปุ่น (ฮิรางานะ, คาตาคานะ, คันจิ)
            "japanese_range": [
                "\u3040-\u309f",  # Hiragana
                "\u30a0-\u30ff",  # Katakana
                "\u4e00-\u9faf",  # CJK Unified Ideographs (Common Kanji)
                "\uff00-\uffef",  # Full-width Roman and half-width Katakana
            ],
            # คงไว้สำหรับภาษาไทย
            "thai_range": ["\u0e00-\u0e7f"],
            # สัญลักษณ์ที่อนุญาตยังคงเดิม
            "allowed_symbols": ["...", "—", "!", "?", "💕", "✨", "🥺", "😏"],
        },
    }

    def __init__(self):
        # กำหนดค่า default ทั้งหมด รวมถึง field ใหม่
        self.default_settings = {
            "api_parameters": self.DEFAULT_API_PARAMETERS.copy(),
            "font_size": 24,
            "font": "IBM Plex Sans Thai Medium.ttf",  # ชื่อไฟล์ฟอนต์เริ่มต้น
            "line_spacing": -50,  # ค่า default สำหรับ line spacing
            "width": 960,
            "height": 240,
            "enable_force_translate": True,
            "enable_auto_hide": True,
            "enable_ui_toggle": True,  # อาจไม่ใช้ แต่คงไว้
            "enable_click_translate": False,  # เพิ่มการตั้งค่าใหม่สำหรับ Click Translate โดยค่าเริ่มต้นเป็น False
            "splash_screen_type": "video",  # ตัวเลือก: "image", "video", "off"
            "bg_color": appearance_manager.bg_color,  # ดึงจาก appearance_manager
            "translate_areas": {  # พิกัดเริ่มต้นยังไม่ได้กำหนด - ให้ผู้ใช้เลือกเอง
                "A": {"start_x": 0, "start_y": 0, "end_x": 0, "end_y": 0},
                "B": {"start_x": 0, "start_y": 0, "end_x": 0, "end_y": 0},
                "C": {"start_x": 0, "start_y": 0, "end_x": 0, "end_y": 0},
            },
            "current_area": "A+B",  # พื้นที่เริ่มต้น
            "current_preset": 1,  # preset เริ่มต้น
            "last_manual_preset_selection_time": 0,  # *** เพิ่ม field นี้ ***
            "display_scale": None,
            "use_gpu_for_ocr": False,
            "screen_size": "2560x1440",  # ขนาดหน้าจออ้างอิงเริ่มต้น
            "shortcuts": {  # ค่า default shortcuts
                "toggle_ui": "alt+l",
                "start_stop_translate": "f9",
                "force_translate": "r-click",
                "force_translate_key": "f10",  # ใหม่: hotkey สำหรับ force translate
            },
            "logs_ui": {  # ค่า default logs UI
                "width": 480,
                "height": 320,
                "font_size": 16,
                "visible": True,
            },
            "buffer_settings": {  # ค่า default buffer settings
                "cache_timeout": 300,
                "max_cache_size": 100,
                "similarity_threshold": 0.85,
            },
            "logs_settings": {  # ค่า default logs settings
                "enable_dual_logs": True,
                "translation_only_logs": True,
                "logs_path": "logs",
                "clean_logs_after_days": 7,
            },
            "area_presets": [],  # เริ่มต้น list ว่าง ให้ ensure_default_values จัดการ
            "custom_themes": {},  # เริ่มต้น custom themes ว่าง
            "theme": "Theme4",  # ธีมเริ่มต้น
            "show_starter_guide": True,  # แสดง guide ตอนเปิดครั้งแรก
            "cpu_limit": 80,  # ค่า default CPU limit
            "enable_hover_translation": False,  # เพิ่มค่า "enable_hover_translation" เข้าไปในไฟล์ settings.py
            "hover_preset_settings": {  # การตั้งค่าเปิด-ปิด hover สำหรับ preset แต่ละตัว
                1: True, 2: True, 3: True, 4: False, 5: False, 6: False
            },
            "ui_positions": {  # เพิ่มการเก็บตำแหน่งพิกัดหน้าต่าง UI
                "main_ui": "",  # ค่าว่างหมายถึงยังไม่ได้บันทึก
                "mini_ui": "",
                "translated_ui": "",
                "control_ui": "",
                "logs_ui": "",
                "monitor_info": {
                    "primary": "",  # ข้อมูลหน้าจอหลัก format: "WxH+X+Y"
                    "all_monitors": [],  # ข้อมูลหน้าจอทั้งหมด format: [{"w": width, "h": height, "x": pos_x, "y": pos_y}]
                },
            },
        }
        self.settings = {}  # เริ่มต้น settings เป็น dict ว่าง
        self.load_settings()  # โหลดค่าจากไฟล์ (ถ้ามี)

        # --- FIX: เพิ่มด่านตรวจและแก้ไขค่าภาษาที่ผิดทันทีหลังโหลด ---
        settings_corrected = False
        try:
            # ตรวจสอบลึกลงไปในโครงสร้าง settings
            if "api_parameters" in self.settings and isinstance(
                self.settings["api_parameters"], dict
            ):
                if "ocr_settings" in self.settings["api_parameters"] and isinstance(
                    self.settings["api_parameters"]["ocr_settings"], dict
                ):
                    if "languages" in self.settings["api_parameters"]["ocr_settings"]:
                        current_langs = self.settings["api_parameters"]["ocr_settings"][
                            "languages"
                        ]
                        # ถ้าเจอ "ko" ให้แก้ไขเป็น "ja" ทันที
                        if "ko" in current_langs:
                            logging.warning(
                                "CORRECTING 'ko' to 'ja' in loaded OCR settings."
                            )
                            new_langs = [
                                lang if lang != "ko" else "ja" for lang in current_langs
                            ]
                            self.settings["api_parameters"]["ocr_settings"][
                                "languages"
                            ] = new_langs
                            settings_corrected = True

                # ทำเช่นเดียวกันกับ translation_settings
                if "translation_settings" in self.settings[
                    "api_parameters"
                ] and isinstance(
                    self.settings["api_parameters"]["translation_settings"], dict
                ):
                    if (
                        "source_languages"
                        in self.settings["api_parameters"]["translation_settings"]
                    ):
                        current_src_langs = self.settings["api_parameters"][
                            "translation_settings"
                        ]["source_languages"]
                        if "ko" in current_src_langs:
                            logging.warning(
                                "CORRECTING 'ko' to 'ja' in loaded translation settings."
                            )
                            new_src_langs = [
                                lang if lang != "ko" else "ja"
                                for lang in current_src_langs
                            ]
                            self.settings["api_parameters"]["translation_settings"][
                                "source_languages"
                            ] = new_src_langs
                            settings_corrected = True
        except Exception as e:
            logging.error(f"Error during settings sanitization: {e}")
        # --- จบส่วนของด่านตรวจ ---

        self.ensure_default_values()  # ตรวจสอบและเติมค่า default ที่ขาดไป

        # ถ้ามีการแก้ไขค่า ให้บันทึกไฟล์ settings.json ที่ถูกต้องกลับไปทันที
        if settings_corrected:
            logging.info("Saving corrected settings back to settings.json.")
            self.save_settings()

    def validate_model_parameters(self, params):
        """Validate the given parameters."""
        if not isinstance(params, dict):
            raise ValueError("Parameters must be a dictionary")

        # Check for valid model
        if "model" in params:
            if params["model"] not in self.VALID_MODELS:
                valid_models = list(self.VALID_MODELS.keys())
                raise ValueError(f"Invalid model. Must be one of: {valid_models}")

        # Validate numeric values
        if "max_tokens" in params:
            max_tokens = int(params["max_tokens"])
            if not (100 <= max_tokens <= 2000):
                raise ValueError("max_tokens must be between 100 and 2000")

        if "temperature" in params:
            temp = float(params["temperature"])
            if not (0.1 <= temp <= 1.0):
                raise ValueError("temperature must be between 0.1 and 1.0")

        return True

    def get_display_scale(self):
        """Return the stored display scale or None if not set."""
        return self.settings.get("display_scale")

    def set_display_scale(self, scale):
        """Save the display scale if valid."""
        try:
            scale = float(scale)
            if 0.5 <= scale <= 3.0:
                self.settings["display_scale"] = scale
                self.save_settings()
                print(f"Display scale saved: {int(scale * 100)}%")
                return True
            else:
                print(f"Invalid scale value: {scale}")
                return False
        except Exception as e:
            print(f"Error saving display scale: {e}")
            return False

    def validate_display_scale(self, scale):
        """Validate the display scale value."""
        try:
            scale = float(scale)
            if 0.5 <= scale <= 3.0:
                return {
                    "is_valid": True,
                    "message": "Valid scale value",
                    "value": scale,
                }
            return {
                "is_valid": False,
                "message": f"Scale must be between 50% and 300%, got {int(scale * 100)}%",
                "value": None,
            }
        except (ValueError, TypeError):
            return {
                "is_valid": False,
                "message": "Invalid scale value type",
                "value": None,
            }

    def set_bg_color(self, color):
        """Set and save the background color."""
        self.settings["bg_color"] = color
        self.save_settings()
        appearance_manager.update_bg_color(color)

    def get(self, key, default=None):
        if key == "bg_color":
            return self.settings.get("bg_color", appearance_manager.bg_color)
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value
        self.save_settings()

    def load_settings(self):
        try:
            with open("settings.json", "r") as f:
                self.settings = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.settings = {}  # ถ้าไฟล์ไม่มีหรือเสีย ให้เริ่มจาก dict ว่าง

    def save_settings(self):
        """Save all current settings to file."""
        try:
            # จัดการ API parameters
            if "api_parameters" in self.settings:
                api_params = self.settings["api_parameters"]
                if "temperature" in api_params:
                    api_params["temperature"] = round(
                        float(api_params["temperature"]), 2
                    )
                if "top_p" in api_params:
                    api_params["top_p"] = round(float(api_params["top_p"]), 2)

            # จัดการ current_area
            if "current_area" in self.settings:
                current_areas = self.settings["current_area"]
                if isinstance(current_areas, list):
                    self.settings["current_area"] = "+".join(current_areas)

            # ตรวจสอบและจัดการ area_presets
            if "area_presets" not in self.settings:
                self.settings["area_presets"] = [
                    {"name": "Preset 1", "areas": "A+B"},
                    {"name": "Preset 2", "areas": "C"},
                    {"name": "Preset 3", "areas": "A"},
                    {"name": "Preset 4", "areas": "B"},
                    {"name": "Preset 5", "areas": "A+B+C"},
                ]

            # บันทึกไฟล์
            with open("settings.json", "w") as f:
                json.dump(self.settings, f, indent=4)

        except Exception as e:
            logging.error(f"Error saving settings: {e}")
            raise

    def ensure_default_values(self):
        """Add default values if missing and ensure preset structure."""
        changes_made = False  # Flag ตรวจสอบว่ามีการเปลี่ยนแปลงค่าหรือไม่

        # วนลูปตรวจสอบทุก key ใน default_settings
        for key, default_value in self.default_settings.items():
            if key not in self.settings:
                # ถ้า key ไม่มีใน settings ที่โหลดมา ให้ใช้ค่า default
                self.settings[key] = default_value
                changes_made = True
                logging.info(f"Added missing setting '{key}' with default value.")
            # --- ตรวจสอบโครงสร้างภายในที่ซับซ้อน (เช่น dicts) ---
            elif key == "api_parameters":
                # ตรวจสอบว่า key ย่อยใน api_parameters มีครบหรือไม่
                if not isinstance(self.settings[key], dict):
                    self.settings[key] = self.default_settings[key].copy()
                    changes_made = True
                else:
                    for sub_key, sub_default in self.default_settings[key].items():
                        if sub_key not in self.settings[key]:
                            self.settings[key][sub_key] = sub_default
                            changes_made = True
                            logging.info(f"Added missing api_parameter '{sub_key}'.")
                        # อาจเพิ่มการตรวจสอบ type ของ sub_key ได้อีก
            elif key == "translate_areas":
                if not isinstance(self.settings[key], dict):
                    self.settings[key] = self.default_settings[key].copy()
                    changes_made = True
                else:
                    for area in ["A", "B", "C"]:
                        if area not in self.settings[key] or not isinstance(
                            self.settings[key].get(area), dict
                        ):
                            self.settings[key][area] = {
                                "start_x": 0,
                                "start_y": 0,
                                "end_x": 0,
                                "end_y": 0,
                            }
                            changes_made = True
                            logging.info(
                                f"Added/Reset missing translate_area '{area}' - no coordinates set yet."
                            )
            elif key == "shortcuts":
                if not isinstance(self.settings[key], dict):
                    self.settings[key] = self.default_settings[key].copy()
                    changes_made = True
                else:
                    for action, default_hotkey in self.default_settings[key].items():
                        if action not in self.settings[key]:
                            self.settings[key][action] = default_hotkey
                            changes_made = True
                            logging.info(f"Added missing shortcut '{action}'.")
            elif key == "logs_ui":  # ตรวจสอบ key ย่อยของ logs_ui
                if not isinstance(self.settings[key], dict):
                    self.settings[key] = self.default_settings[key].copy()
                    changes_made = True
                else:
                    for sub_key, sub_default in self.default_settings[key].items():
                        if sub_key not in self.settings[key]:
                            self.settings[key][sub_key] = sub_default
                            changes_made = True
                            logging.info(f"Added missing logs_ui setting '{sub_key}'.")
            # --- จบการตรวจสอบโครงสร้างภายใน ---

        # --- ส่วนสำคัญ: ตรวจสอบและจัดการ area_presets ---
        # *** แก้ไข: เพิ่ม default สำหรับ preset 6 และปรับการตรวจสอบเป็น 6 ***
        default_presets_structure = [
            {"name": "dialog", "role": "dialog", "areas": "A+B", "coordinates": {}},
            {"name": "lore", "role": "lore", "areas": "C", "coordinates": {}},
            {"name": "choice", "role": "choice", "areas": "A+B", "coordinates": {}},
            {"name": "Preset 4", "role": "custom", "areas": "B", "coordinates": {}},
            {"name": "Preset 5", "role": "custom", "areas": "A+B+C", "coordinates": {}},
            {
                "name": "Preset 6",
                "role": "custom",
                "areas": "A+C",
                "coordinates": {},
            },  # เพิ่ม preset 6
        ]
        presets_changed_flag = False  # ใช้ flag แยกสำหรับ preset โดยเฉพาะ

        # ตรวจสอบ area_presets อีกครั้งหลัง ensure ค่า default ทั่วไปแล้ว
        current_presets = self.settings.get("area_presets", [])
        if (
            not isinstance(current_presets, list) or len(current_presets) != 6
        ):  # แก้เป็น 6
            logging.warning(
                "Area presets missing or invalid length. Recreating defaults with 6 presets."
            )
            # เก็บ custom names ของ 4, 5, 6 (ถ้ามี) ก่อนสร้างใหม่
            custom_names = {}
            if isinstance(current_presets, list):
                for i, p in enumerate(current_presets):
                    preset_num = i + 1
                    if (
                        isinstance(p, dict) and preset_num >= 4
                    ):  # ตรวจสอบ preset 4, 5, 6, ...
                        if "custom_name" in p and p["custom_name"]:
                            custom_names[preset_num] = p["custom_name"]

            # สร้าง default structure ใหม่
            new_presets = [p.copy() for p in default_presets_structure]  # ใช้ copy()

            # ใส่ custom names กลับเข้าไป
            for preset_num, name in custom_names.items():
                if 1 <= preset_num <= len(new_presets):  # ตรวจสอบขอบเขตของ new_presets
                    new_presets[preset_num - 1]["custom_name"] = name
                    logging.info(
                        f"Restored custom name '{name}' for preset {preset_num} during recreation."
                    )

            self.settings["area_presets"] = new_presets
            presets_changed_flag = True
            if "current_preset" not in self.settings or not (
                1 <= self.settings.get("current_preset", 1) <= 6
            ):  # แก้เป็น 6
                self.settings["current_preset"] = 1  # ตั้งเป็น 1 เมื่อสร้างใหม่
        else:
            # ตรวจสอบโครงสร้างแต่ละ preset ให้ครบ 6 ตัว
            for i in range(6):  # วนลูป 6 ครั้ง
                preset = current_presets[i]
                preset_num = i + 1
                default_struct = default_presets_structure[i]
                changed_this_preset = False
                existing_custom_name = None

                # ตรวจสอบ type ของ preset เอง
                if not isinstance(preset, dict):
                    if (
                        isinstance(current_presets[i], dict)
                        and "custom_name" in current_presets[i]
                    ):
                        existing_custom_name = current_presets[i]["custom_name"]
                    current_presets[i] = default_struct.copy()  # ใช้ copy()
                    preset = current_presets[i]  # อัพเดตตัวแปร preset ให้ชี้ไปที่ dict ใหม่
                    if existing_custom_name and preset_num >= 4:
                        preset["custom_name"] = existing_custom_name
                    presets_changed_flag = True
                    logging.info(f"Preset {preset_num} recreated due to invalid type.")
                else:
                    # เก็บ custom name เดิมไว้ก่อน (เผื่อต้องใช้)
                    if "custom_name" in preset:
                        existing_custom_name = preset["custom_name"]

                # ตรวจ/เพิ่ม 'role'
                expected_role = default_struct["role"]
                if preset.get("role") != expected_role:
                    preset["role"] = expected_role
                    changed_this_preset = True
                # ตรวจ/เพิ่ม 'name' (เฉพาะชื่อ default, custom_name จัดการแยก)
                expected_name = default_struct["name"]
                if preset.get("name") != expected_name:
                    preset["name"] = expected_name
                    changed_this_preset = True
                # บังคับ Preset 1, 2, 3 areas และ Log การเปลี่ยนแปลง
                if preset_num == 1 and preset.get("areas") != "A+B":
                    preset["areas"] = "A+B"
                    changed_this_preset = True
                    logging.info("Forcing Preset 1 areas to A+B")
                elif preset_num == 2 and preset.get("areas") != "C":
                    preset["areas"] = "C"
                    changed_this_preset = True
                    logging.info("Forcing Preset 2 areas to C")
                elif preset_num == 3 and preset.get("areas") != "A+B":
                    preset["areas"] = "A+B"
                    changed_this_preset = True
                    logging.info("Forcing Preset 3 areas to A+B")
                # ตรวจ/เพิ่ม coordinates
                if "coordinates" not in preset or not isinstance(
                    preset.get("coordinates"), dict
                ):
                    preset["coordinates"] = {}
                    changed_this_preset = True

                # รักษา/ลบ custom_name สำหรับ preset 4-6
                if preset_num >= 4:
                    if existing_custom_name:
                        if (
                            "custom_name" not in preset
                            or preset.get("custom_name") != existing_custom_name
                        ):
                            preset["custom_name"] = existing_custom_name
                            # การใส่ custom name กลับไม่นับเป็นการเปลี่ยนโครงสร้างที่ต้องเซฟซ้ำ นอกจากว่าค่ามันเปลี่ยนไปจริงๆ
                            logging.debug(
                                f"Corrected/Preserved custom name '{existing_custom_name}' for preset {preset_num}."
                            )
                    elif "custom_name" in preset:
                        # ถ้าไม่มี existing_custom_name แต่ใน dict มี key นี้อยู่ ให้ลบทิ้ง
                        del preset["custom_name"]
                        changed_this_preset = True
                        logging.info(
                            f"Removed empty/invalid custom_name field from preset {preset_num}."
                        )

                if changed_this_preset:
                    presets_changed_flag = True
                    logging.info(f"Preset {preset_num} structure updated/corrected.")

        # ตรวจ current_preset อีกครั้ง หลัง area_presets ถูกจัดการแล้ว (ใช้ len() เพื่อความปลอดภัย)
        num_presets = len(self.settings.get("area_presets", []))
        if not (
            1 <= self.settings.get("current_preset", 1) <= num_presets
        ):  # ใช้ num_presets ที่ถูกต้อง
            logging.warning(
                f"Invalid current_preset found ({self.settings.get('current_preset')}). Resetting to 1."
            )
            self.settings["current_preset"] = 1
            presets_changed_flag = True  # ถือว่ามีการแก้ไข

        # --- จบส่วน area_presets ---

        # บันทึกค่าลงไฟล์ ถ้ามีการเปลี่ยนแปลง หรือถ้าไฟล์ไม่มีอยู่
        if changes_made or presets_changed_flag or not os.path.exists("settings.json"):
            logging.info(
                "Saving settings due to missing values or preset structure changes."
            )
            self.save_settings()

    def get_preset(self, preset_number):
        """รับค่า preset ตามหมายเลข"""
        presets = self.settings.get("area_presets", [])
        if 1 <= preset_number <= len(presets):
            return presets[preset_number - 1]
        return None

    def get_preset_role(self, preset_number):
        """รับค่า role ของ preset ตามหมายเลข"""
        preset_data = self.get_preset(preset_number)
        if preset_data:
            # ใช้ค่า role จาก preset_data หรือ fallback เป็น 'custom' ถ้าไม่มี
            return preset_data.get("role", "custom")
        # ถ้าหา preset ไม่เจอ ให้ถือว่าเป็น custom (หรืออาจจะคืน None แล้วให้ที่เรียกไปจัดการ)
        logging.warning(
            f"Preset {preset_number} not found when getting role, assuming 'custom'."
        )
        return "custom"

    def get_preset_areas_list(self, preset_number):
        """รับรายการ areas ของ preset ตามหมายเลขในรูปแบบ list

        Args:
            preset_number (int): หมายเลข preset (1-6)

        Returns:
            list: รายการ areas เช่น ["A", "B"] หรือ ["A+B"] หรือ [] ถ้าไม่มี
        """
        preset_data = self.get_preset(preset_number)
        if preset_data and "areas" in preset_data:
            areas_str = preset_data["areas"]
            if areas_str:
                # แยก areas ที่อาจเป็น "A+B" หรือ "A" หรือ "B"
                if "+" in areas_str:
                    return areas_str.split("+")
                else:
                    return [areas_str]
        return []

    def get_preset_display_name(self, preset_number):
        """รับค่า name (ชื่อที่แสดง) ของ preset ตามหมายเลข

        ให้แสดงชื่อประเภทให้ชัดเจน:
        - preset 1 = "dialog"
        - preset 2 = "lore"
        - preset 3 = "Ex-choice"
        - preset 4 = "Preset 4" (หรือชื่อที่ผู้ใช้กำหนดเอง)
        - preset 5 = "Preset 5" (หรือชื่อที่ผู้ใช้กำหนดเอง)
        """
        # กำหนดชื่อคงที่สำหรับ preset 1-3
        if preset_number == 1:
            return "dialog"
        elif preset_number == 2:
            return "lore"
        elif preset_number == 3:
            return "Ex-choice"
        elif preset_number in [4, 5, 6]:  # แก้ไขตรงนี้: เพิ่ม 6 เข้าไปใน list
            # สำหรับ preset 4-6 ให้ตรวจสอบว่ามีชื่อ custom หรือไม่
            preset_data = self.get_preset(preset_number)
            if (
                preset_data
                and "custom_name" in preset_data
                and preset_data["custom_name"]
            ):
                return preset_data["custom_name"]
            # ถ้าไม่มีชื่อ custom ให้ใช้ชื่อเริ่มต้น (เช่น "Preset 4", "Preset 5", "Preset 6")
            return f"Preset {preset_number}"
        else:
            # สำหรับหมายเลขอื่นๆ ที่ไม่ใช่ 1-6 (ถ้ามีเข้ามา)
            logging.error(f"Invalid preset number requested: {preset_number}")
            return f"Unknown Preset {preset_number}"

    def set_preset_custom_name(self, preset_number, custom_name):
        """ตั้งชื่อ custom ให้กับ preset

        Args:
            preset_number (int): หมายเลข preset (1-6)
            custom_name (str): ชื่อ custom ที่ต้องการตั้ง
        """
        try:
            if not (1 <= preset_number <= 6):  # เปลี่ยนเป็น 6
                logging.error(f"Invalid preset number: {preset_number}")
                return False

            # ดึงข้อมูล presets ทั้งหมด
            presets = self.settings.get("area_presets", [])

            # หา index ของ preset ที่ต้องการ
            preset_index = preset_number - 1

            # ตรวจสอบว่า index อยู่ในขอบเขตหรือไม่
            if 0 <= preset_index < len(presets):
                # อัพเดตชื่อ custom
                presets[preset_index]["custom_name"] = custom_name
                # บันทึก presets กลับไปที่ settings
                self.settings["area_presets"] = presets
                # *** เพิ่มการเรียก save_settings() ที่นี่ ***
                self.save_settings()
                logging.info(
                    f"Set custom name for preset {preset_number} to '{custom_name}'"
                )
                return True
            else:
                logging.error(
                    f"Preset index {preset_index} out of bounds for preset {preset_number}"
                )
                return False

        except Exception as e:
            logging.error(f"Error setting custom name for preset {preset_number}: {e}")
            import traceback

            traceback.print_exc()
            return False

    def get_all_presets(self):
        """Return all preset data."""
        # Ensure the presets are loaded and potentially defaulted
        self.ensure_default_values()
        return self.settings.get("area_presets", [])

    def validate_coordinates(self, coordinates):
        """Validate the structure and values of coordinates data.

        Args:
            coordinates (dict): Dictionary containing area coordinates.
                                Expected format: {"A": {"start_x": ..., ...}, ...}

        Returns:
            bool: True if valid, False otherwise.
        """
        if not isinstance(coordinates, dict):
            logging.error("Invalid coordinates type: Expected dict")
            return False

        required_keys = {"start_x", "start_y", "end_x", "end_y"}

        for area, coords in coordinates.items():
            if area not in ["A", "B", "C"]:
                logging.error(f"Invalid area key in coordinates: {area}")
                return False

            if not isinstance(coords, dict):
                logging.error(
                    f"Invalid coordinates value type for area {area}: Expected dict"
                )
                return False

            if not required_keys.issubset(coords.keys()):
                logging.error(
                    f"Missing required keys in coordinates for area {area}. Expected: {required_keys}"
                )
                return False

            for key, value in coords.items():
                if key in required_keys and not isinstance(value, (int, float)):
                    logging.error(
                        f"Invalid coordinate value type for {key} in area {area}: Expected number, got {type(value)}"
                    )
                    return False

        return True

    def save_preset(self, preset_number, areas, coordinates):
        """บันทึกข้อมูล preset (areas และ coordinates)

        Args:
            preset_number (int): หมายเลข preset (1-6)
            areas (str): สตริงพื้นที่ที่ใช้งาน เช่น "A+B"
            coordinates (dict): พิกัดของแต่ละพื้นที่

        Returns:
            bool: True ถ้าบันทึกสำเร็จ, False ถ้าล้มเหลว
        """
        try:
            if not (1 <= preset_number <= 6):
                logging.error(f"Invalid preset number: {preset_number}")
                return False

            # ตรวจสอบความถูกต้องของ coordinates ก่อนบันทึก
            if not self.validate_coordinates(coordinates):
                logging.error(
                    f"Invalid coordinates data provided for preset {preset_number}. Aborting save."
                )
                return False

            # ดึงข้อมูล presets ทั้งหมด
            presets = self.settings.get("area_presets", [])

            # หา index ของ preset ที่ต้องการ
            preset_index = preset_number - 1

            # ตรวจสอบว่า index อยู่ในขอบเขตหรือไม่
            if 0 <= preset_index < len(presets):
                # *** สร้างสำเนาข้อมูลพิกัดก่อนบันทึก ***
                coords_copy = {}
                for area, coords in coordinates.items():
                    if isinstance(coords, dict) and all(
                        k in coords for k in ["start_x", "start_y", "end_x", "end_y"]
                    ):
                        coords_copy[area] = {
                            "start_x": coords["start_x"],
                            "start_y": coords["start_y"],
                            "end_x": coords["end_x"],
                            "end_y": coords["end_y"],
                        }

                # อัพเดตข้อมูล
                presets[preset_index]["areas"] = areas
                presets[preset_index]["coordinates"] = coords_copy  # ใช้สำเนาที่สร้างใหม่

                # บันทึก presets กลับไปที่ settings
                self.settings["area_presets"] = presets
                self.save_settings()

                # บันทึกรายละเอียดลง log เพื่อการตรวจสอบ
                for area, coords in coords_copy.items():
                    logging.info(
                        f"Preset {preset_number} saved area {area} coordinates: {coords}"
                    )

                logging.info(
                    f"Successfully saved preset {preset_number}: areas='{areas}', with {len(coords_copy)} coordinate sets"
                )
                return True
            else:
                logging.error(
                    f"Preset index {preset_index} out of bounds for preset {preset_number}"
                )
                return False

        except Exception as e:
            logging.error(f"Error saving preset {preset_number}: {e}")
            import traceback

            traceback.print_exc()
            return False

    def set_cpu_limit(self, limit):
        """Set the CPU usage limit."""
        if "cpu_limit" in self.settings:
            self.settings["cpu_limit"] = limit
            self.save_settings()

    def get_current_preset(self):
        """รับค่า preset ปัจจุบัน
        Returns:
            int: หมายเลข preset ปัจจุบัน (1-5)
        """
        return self.settings.get("current_preset", 1)

    def get_logs_settings(self):
        """Return the settings for the logs UI."""
        # รวม settings จาก logs_ui และ ui_positions
        logs_ui = self.settings.get(
            "logs_ui", {"width": 480, "height": 320, "font_size": 16, "font_family": "Bai Jamjuree", "visible": True}
        )

        # เพิ่มการดึง geometry จาก ui_positions
        logs_position = self.settings.get("ui_positions", {}).get("logs_ui", "")
        if logs_position:
            # แปลง geometry string เป็น x, y
            try:
                # format: "widthxheight+x+y"
                if "+" in logs_position and "x" in logs_position:
                    size_part, pos_part = logs_position.split("+", 1)
                    if "x" in size_part:
                        width_str, height_str = size_part.split("x")
                        # อัพเดต width, height จาก position (มีความแม่นยำกว่า)
                        logs_ui["width"] = int(width_str)
                        logs_ui["height"] = int(height_str)

                    # แยก x, y
                    pos_parts = pos_part.split("+")
                    if len(pos_parts) >= 2:
                        logs_ui["x"] = int(pos_parts[0])
                        logs_ui["y"] = int(pos_parts[1])
                    elif "+" in pos_part:
                        # กรณี x เป็นลบ
                        x_str = (
                            pos_parts[0] if pos_parts[0] != "" else "-" + pos_parts[1]
                        )
                        y_str = pos_parts[-1]
                        logs_ui["x"] = int(x_str)
                        logs_ui["y"] = int(y_str)
            except (ValueError, IndexError) as e:
                logging.warning(
                    f"Failed to parse logs_ui position '{logs_position}': {e}"
                )

        # เพิ่ม transparency_mode จาก settings หลัก
        logs_ui["transparency_mode"] = self.settings.get("logs_transparency_mode", "A")

        return logs_ui

    def set_logs_settings(
        self,
        width=None,
        height=None,
        font_size=None,
        font_family=None,
        visible=None,
        x=None,
        y=None,
        transparency_mode=None,
        logs_reverse_mode=None,
    ):
        """Update the logs UI settings."""
        if "logs_ui" not in self.settings:
            self.settings["logs_ui"] = {}

        if width is not None:
            self.settings["logs_ui"]["width"] = width
        if height is not None:
            self.settings["logs_ui"]["height"] = height
        if font_size is not None:
            self.settings["logs_ui"]["font_size"] = font_size
        if font_family is not None:
            self.settings["logs_ui"]["font_family"] = font_family
        if visible is not None:
            self.settings["logs_ui"]["visible"] = visible

        # บันทึก transparency_mode และ logs_reverse_mode ลงใน settings หลัก
        if transparency_mode is not None:
            self.settings["logs_transparency_mode"] = transparency_mode
        if logs_reverse_mode is not None:
            self.settings["logs_reverse_mode"] = logs_reverse_mode

        # บันทึก x, y ลงใน ui_positions
        if x is not None and y is not None and width is not None and height is not None:
            if "ui_positions" not in self.settings:
                self.settings["ui_positions"] = {}
            self.settings["ui_positions"]["logs_ui"] = f"{width}x{height}+{x}+{y}"

        self.save_settings()

    def clear_logs_position_cache(self):
        """เคลียร์ cache ของตำแหน่ง logs UI เพื่อใช้ smart positioning"""
        try:
            if (
                "ui_positions" in self.settings
                and "logs_ui" in self.settings["ui_positions"]
            ):
                del self.settings["ui_positions"]["logs_ui"]
                self.save_settings()
                print(
                    "Cleared logs UI position cache - will use smart positioning next time"
                )
                return True
        except Exception as e:
            print(f"Error clearing logs position cache: {e}")
        return False

    def get_shortcut(self, action, default=None):
        return self.settings.get("shortcuts", {}).get(action, default)

    def set_shortcut(self, action, shortcut):
        if "shortcuts" not in self.settings:
            self.settings["shortcuts"] = {}
        self.settings["shortcuts"][action] = shortcut
        self.save_settings()

    def set_screen_size(self, size):
        self.settings["screen_size"] = size
        self.save_settings()

    def set_gpu_for_ocr(self, use_gpu):
        self.settings["use_gpu_for_ocr"] = use_gpu
        self.save_settings()
        current_mode = "GPU" if use_gpu else "CPU"
        logging.info(f"Switched OCR to [{current_mode}]")
        print(f"Switched OCR to [{current_mode}]")

    def set_current_area(self, area):
        self.settings["current_area"] = area
        self.save_settings()

    def get_current_area(self):
        return self.settings.get("current_area", "A")

    def set_translate_area(self, start_x, start_y, end_x, end_y, area):
        """Save the translation area with deep copy to prevent reference issues."""
        if "translate_areas" not in self.settings:
            self.settings["translate_areas"] = {}

        # สร้าง dictionary ใหม่เสมอ ไม่ใช้การอ้างอิงไปยังข้อมูลอื่น
        self.settings["translate_areas"][area] = {
            "start_x": int(start_x),
            "start_y": int(start_y),
            "end_x": int(end_x),
            "end_y": int(end_y),
        }

        logging.info(
            f"Area {area} coordinates saved: ({start_x},{start_y}) to ({end_x},{end_y})"
        )

    def get_translate_area(self, area):
        """Return the translation area data with a new copy to prevent reference issues."""
        translate_areas = self.settings.get("translate_areas", {})
        area_data = translate_areas.get(area)

        # สร้างสำเนาข้อมูลพิกัดเพื่อป้องกันการอ้างอิงไปยังข้อมูลต้นฉบับ
        if area_data:
            return {
                "start_x": area_data.get("start_x", 0),
                "start_y": area_data.get("start_y", 0),
                "end_x": area_data.get("end_x", 0),
                "end_y": area_data.get("end_y", 0),
            }

        return None

    def set_api_parameters(
        self, model=None, max_tokens=None, temperature=None, top_p=None
    ):
        try:
            if "api_parameters" not in self.settings:
                self.settings["api_parameters"] = {}

            api_params = self.settings["api_parameters"]
            changes = []

            if model is not None:
                if model not in self.VALID_MODELS:
                    raise ValueError(f"Invalid model: {model}")
                old_model = api_params.get("model")
                model_info = self.VALID_MODELS[model]
                api_params.update(
                    {"model": model, "displayed_model": model_info["display_name"]}
                )
                changes.append(f"Model: {old_model} -> {model}")

            if max_tokens is not None:
                if not (100 <= max_tokens <= 1000):
                    raise ValueError("Max tokens must be between 100 and 1000")
                old_tokens = api_params.get("max_tokens")
                api_params["max_tokens"] = max_tokens
                changes.append(f"Max tokens: {old_tokens} -> {max_tokens}")

            if temperature is not None:
                if not (0.1 <= temperature <= 1.0):
                    raise ValueError("Temperature must be between 0.1 and 1.0")
                old_temp = api_params.get("temperature")
                api_params["temperature"] = temperature
                changes.append(f"Temperature: {old_temp} -> {temperature}")

            # บันทึก top_p สำหรับ Gemini models
            current_model_type = self.VALID_MODELS.get(
                model or api_params.get("model", ""), {}
            ).get("type")

            if current_model_type == "gemini":
                if top_p is not None:
                    if not (0.1 <= top_p <= 1.0):
                        raise ValueError("Top P must be between 0.1 and 1.0")
                    old_top_p = api_params.get("top_p")
                    api_params["top_p"] = top_p
                    changes.append(f"Top P: {old_top_p} -> {top_p}")

            self.save_settings()

            if changes:
                logging.info("\n=== API Parameters Updated ===")
                for change in changes:
                    logging.info(change)
                logging.info(f"Current Settings: {api_params}")
                logging.info("============================\n")

            return True, None
        except Exception as e:
            logging.error(f"Error setting API parameters: {str(e)}")
            return False, str(e)

    def get_displayed_model(self):
        """Return the model name for UI display."""
        api_params = self.get_api_parameters()
        return api_params.get(
            "displayed_model", api_params.get("model", "gemini-2.0-flash")
        )

    def get_api_parameters(self):
        """Return the current API parameters."""
        params = self.settings.get(
            "api_parameters", self.DEFAULT_API_PARAMETERS.copy()
        ).copy()

        # ตรวจสอบและลบ proxies ถ้ามี
        if "proxies" in params:
            del params["proxies"]

        # ปรับค่าต่างๆ ตามปกติ
        if "temperature" in params:
            params["temperature"] = round(params["temperature"], 2)
        if "top_p" in params:
            params["top_p"] = round(params["top_p"], 2)

        return params

    def get_all_settings(self):
        """รับการตั้งค่าทั้งหมดในรูปแบบ dictionary

        Returns:
            dict: การตั้งค่าทั้งหมดที่มีอยู่ในระบบ
        """
        return self.settings

    # +++ NEW METHOD +++
    def find_preset_by_areas(self, area_string):
        """ค้นหาหมายเลข preset (1-6) ที่มี area_string ตรงกัน

        Args:
            area_string (str): สตริงพื้นที่ที่ต้องการค้นหา (เช่น "A+B")

        Returns:
            int | None: หมายเลข preset ที่พบ หรือ None ถ้าไม่พบ
        """
        try:
            presets = self.get_all_presets()  # ใช้ get_all_presets เพื่อให้แน่ใจว่าข้อมูลล่าสุด
            # เรียงลำดับ area string ก่อนเปรียบเทียบ
            target_areas_sorted = (
                "+".join(sorted(area_string.split("+"))) if area_string else ""
            )

            for i, preset in enumerate(presets):
                preset_areas = preset.get("areas", "")
                preset_areas_sorted = (
                    "+".join(sorted(preset_areas.split("+"))) if preset_areas else ""
                )
                if preset_areas_sorted == target_areas_sorted:
                    return i + 1  # คืนหมายเลข preset (1-based)
            return None  # ไม่พบ preset ที่ตรงกัน
        except Exception as e:
            logging.error(f"Error finding preset by areas '{area_string}': {e}")
            return None

    # +++ NEW METHOD +++
    def get_preset_data(self, preset_number):
        """รับข้อมูล preset แบบเต็มรูปแบบตามหมายเลขที่กำหนด

        Args:
            preset_number (int): หมายเลข preset (1-6)

        Returns:
            dict | None: ข้อมูล preset ที่สมบูรณ์ หรือ None ถ้าไม่พบ
        """
        preset = self.get_preset(preset_number)  # ใช้ get_preset ที่มีอยู่
        if preset:
            # ตรวจสอบและเติมค่า default พื้นฐาน (ถ้าจำเป็น)
            if "name" not in preset:
                preset["name"] = (
                    f"Preset {preset_number}"  # ควรจะมาจาก ensure_default_values แล้ว
                )
            if "role" not in preset:
                preset["role"] = "custom"  # ควรจะมาจาก ensure_default_values แล้ว
            if "areas" not in preset:
                preset["areas"] = ""  # ควรจะมีค่า default ถ้า ensure ทำงานถูกต้อง
            if "coordinates" not in preset or not isinstance(
                preset.get("coordinates"), dict
            ):
                preset["coordinates"] = {}
            return preset
        return None

    def save_ui_position(self, ui_name, geometry_str):
        """บันทึกตำแหน่งของหน้าต่าง UI

        Args:
            ui_name (str): ชื่อของ UI ('main_ui', 'mini_ui', 'translated_ui', 'control_ui', 'logs_ui')
            geometry_str (str): ค่า geometry ของหน้าต่าง (format: 'WxH+X+Y')
        """
        # ตรวจสอบว่ามีโครงสร้าง ui_positions หรือไม่
        if "ui_positions" not in self.settings:
            self.settings["ui_positions"] = {}

        # บันทึกค่า geometry string
        self.settings["ui_positions"][ui_name] = geometry_str
        logging.info(f"บันทึกตำแหน่ง {ui_name}: {geometry_str}")

        # ไม่จำเป็นต้อง save_settings() ทันที เพื่อลดการเขียนไฟล์บ่อยๆ

    def get_ui_position(self, ui_name):
        """ดึงตำแหน่งของหน้าต่าง UI

        Args:
            ui_name (str): ชื่อของ UI ('main_ui', 'mini_ui', 'translated_ui', 'control_ui', 'logs_ui')

        Returns:
            str: ค่า geometry ของหน้าต่าง หรือ None หากไม่พบข้อมูล
        """
        if "ui_positions" in self.settings and ui_name in self.settings["ui_positions"]:
            return self.settings["ui_positions"][ui_name]
        return None

    def save_monitor_info(self, primary_monitor, all_monitors):
        """บันทึกข้อมูลของหน้าจอแสดงผล

        Args:
            primary_monitor (str): ข้อมูลหน้าจอหลัก format: "WxH+X+Y"
            all_monitors (list): ข้อมูลหน้าจอทั้งหมด format: [{"w": width, "h": height, "x": pos_x, "y": pos_y}]
        """
        if "ui_positions" not in self.settings:
            self.settings["ui_positions"] = {}
        if "monitor_info" not in self.settings["ui_positions"]:
            self.settings["ui_positions"]["monitor_info"] = {}

        self.settings["ui_positions"]["monitor_info"]["primary"] = primary_monitor
        self.settings["ui_positions"]["monitor_info"]["all_monitors"] = all_monitors
        logging.info(
            f"บันทึกข้อมูลหน้าจอ: หลัก={primary_monitor}, ทั้งหมด={len(all_monitors)} จอ"
        )

    def get_monitor_info(self):
        """ดึงข้อมูลของหน้าจอแสดงผล

        Returns:
            tuple: (primary_monitor, all_monitors) หรือ (None, None) หากไม่พบข้อมูล
        """
        if (
            "ui_positions" in self.settings
            and "monitor_info" in self.settings["ui_positions"]
        ):
            monitor_info = self.settings["ui_positions"]["monitor_info"]
            return (monitor_info.get("primary"), monitor_info.get("all_monitors"))
        return (None, None)

    def save_all_ui_positions(self):
        """บันทึกการตั้งค่าลงไฟล์ settings.json เพื่อบันทึกตำแหน่งหน้าต่าง UI"""
        self.save_settings()
        logging.info("บันทึกตำแหน่งหน้าต่าง UI ทั้งหมดลงไฟล์ settings.json สำเร็จ")


class SettingsUI:
    def __init__(
        self,
        parent,
        settings,
        apply_settings_callback,
        update_hotkeys_callback,
        main_app=None,
        toggle_click_callback=None,
        toggle_hover_callback=None,
    ):
        self.parent = parent
        self.settings = settings
        self.apply_settings_callback = apply_settings_callback
        self.update_hotkeys_callback = update_hotkeys_callback
        self.main_app = main_app  # เก็บ reference ของ MagicBabelApp
        self.toggle_click_callback = toggle_click_callback
        self.toggle_hover_callback = toggle_hover_callback
        self.settings_window = None
        self.settings_visible = False
        self.ocr_toggle_callback = None
        self.on_close_callback = None

        # Initialize modern theme - ต้องมาก่อน create_settings_window
        self.theme = SettingsUITheme

        # โหลดไอคอน MBB
        self.load_icons()

        self.create_settings_window()
        self.advance_ui = None
        self.hotkey_ui = None
        self.font_ui = None  # เพิ่มบรรทัดนี้เพื่อเก็บอ้างอิงถึง FontUI
        self.font_manager = None  # เพิ่มบรรทัดนี้เพื่อเก็บอ้างอิงถึง FontManager

    def load_icons(self):
        """โหลดไอคอน MBB สำหรับ header"""
        try:
            # โหลดไอคอน MBB ขนาด 64x64 px เหมาะสำหรับ header
            icon_size = (64, 64)
            self.mbb_icon = AssetManager.load_icon("mbb_icon.png", icon_size)
        except Exception as e:
            print(f"Warning: Could not load mbb_icon.png: {e}")
            self.mbb_icon = None

    def get_theme_color(self, color_key):
        """Get color from new theme or fallback to appearance_manager"""
        try:
            return SettingsUITheme.get_color(color_key)
        except:
            # Fallback to appearance_manager colors
            fallback_map = {
                "bg_primary": appearance_manager.bg_color,
                "bg_secondary": appearance_manager.bg_color,
                "bg_tertiary": "#333333",
                "text_primary": "white",
                "text_secondary": "#AAAAAA",
                "success": "#4CAF50",
                "error": "#FF5252",
                "border_normal": "#555555",
                "border_focus": "#6D6D6D",
            }
            return fallback_map.get(color_key, appearance_manager.bg_color)

    def get_theme_font(self, size="normal", weight="normal"):
        """Get font from new theme or fallback to default fonts"""
        try:
            return SettingsUITheme.get_font(size, weight)
        except:
            # Fallback to default fonts
            font_map = {
                "small": ("Bai Jamjuree Light", 8),
                "normal": ("Bai Jamjuree Light", 13),
                "medium": ("Bai Jamjuree Light", 13),
                "large": ("Bai Jamjuree Light", 17),
                "title": ("Nasalization Rg", 14),
            }
            font_tuple = font_map.get(size, ("Bai Jamjuree Light", 13))
            if weight == "bold":
                return (font_tuple[0], font_tuple[1], "bold")
            return font_tuple

    tk.Canvas.create_rounded_rect = lambda self, x1, y1, x2, y2, radius=25, **kwargs: (
        self.create_arc(
            x1, y1, x1 + 2 * radius, y1 + 2 * radius, start=90, extent=90, **kwargs
        )
        + self.create_arc(
            x2 - 2 * radius, y1, x2, y1 + 2 * radius, start=0, extent=90, **kwargs
        )
        + self.create_arc(
            x2 - 2 * radius, y2 - 2 * radius, x2, y2, start=270, extent=90, **kwargs
        )
        + self.create_arc(
            x1, y2 - 2 * radius, x1 + 2 * radius, y2, start=180, extent=90, **kwargs
        )
        + self.create_rectangle(x1 + radius, y1, x2 - radius, y2, **kwargs)
        + self.create_rectangle(x1, y1 + radius, x2, y2 - radius, **kwargs)
    )

    def create_settings_section(self, parent, title, colors):
        """
        สร้าง Section Frame ในสไตล์ Flat Design ที่มีเส้นขอบบางๆ และหัวข้อ
        """
        # ใช้ Frame ธรรมดาและกำหนดเส้นขอบผ่าน highlightbackground
        section_container = tk.Frame(
            parent,
            bg=colors["bg"],
            highlightbackground=colors["border"],
            highlightthickness=1,
        )
        section_container.pack(fill=tk.X, padx=10, pady=(8, 0))

        # Frame ด้านในสำหรับใส่เนื้อหาและหัวข้อ (เพื่อสร้าง padding)
        inner_frame = tk.Frame(section_container, bg=colors["bg"])
        inner_frame.pack(fill=tk.X, expand=True, padx=10, pady=10)

        # หัวข้อของ Section
        title_label = tk.Label(
            inner_frame,
            text=title,
            bg=colors["bg"],
            fg=colors["text_secondary"],
            font=self.theme.get_font("medium", "bold"),  # ยังคงใช้ font จาก theme เดิมได้
            anchor="w",
        )
        title_label.pack(fill=tk.X, pady=(0, 8))

        return inner_frame

    def create_settings_window(self):
        self.settings_window = tk.Toplevel(self.parent)
        self.settings_window.overrideredirect(True)
        # เพิ่มการตั้งค่าให้ window ทึบ ไม่มีความโปร่งใส
        self.settings_window.attributes("-alpha", 1.0)
        
        # ตั้งค่าไอคอน
        try:
            from icon_manager import set_window_icon_simple
            set_window_icon_simple(self.settings_window)
        except Exception:
            pass
            
        appearance_manager.apply_style(self.settings_window)
        self.create_settings_ui()
        self.settings_window.withdraw()

        # เพิ่ม protocol handler
        self.settings_window.protocol("WM_DELETE_WINDOW", self.close_settings)

    def set_ocr_toggle_callback(self, callback):
        self.ocr_toggle_callback = callback
        if self.advance_ui:
            self.advance_ui.settings_ui.ocr_toggle_callback = callback

    def open_settings(self, parent_x, parent_y, parent_width, mbb_side="left"):
        """Open settings window at specified position relative to parent

        Args:
            parent_x (int): X position ของหน้าต่าง MBB
            parent_y (int): Y position ของหน้าต่าง MBB
            parent_width (int): ความกว้างของหน้าต่าง MBB
            mbb_side (str): ตำแหน่งของ MBB ('left' หรือ 'right')
        """
        # ใช้ logic แบบฉลาดในการจัดตำแหน่ง Settings UI
        try:
            # ดึงขนาดของ Settings window
            self.settings_window.update_idletasks()
            settings_width = self.settings_window.winfo_reqwidth()
            if settings_width < 400:  # กำหนดขนาดขั้นต่ำ
                settings_width = 400

            gap = 20  # ระยะห่างระหว่าง MBB และ Settings

            # ดึงข้อมูลจอภาพ
            try:
                if HAS_WIN32:
                    # ใช้วิธีเดียวกับ control_ui.py
                    # สมมติว่า MBB window handle สามารถเข้าถึงได้ผ่าน parent
                    if hasattr(self, "parent") and hasattr(self.parent, "winfo_id"):
                        main_hwnd = int(self.parent.winfo_id())
                        hmonitor = win32api.MonitorFromWindow(
                            main_hwnd, win32con.MONITOR_DEFAULTTONEAREST
                        )

                        monitor_info = win32api.GetMonitorInfo(hmonitor)
                        monitor_rect = monitor_info[
                            "Work"
                        ]  # (left, top, right, bottom)

                        monitor_left = monitor_rect[0]
                        monitor_right = monitor_rect[2]

                        print(f"Settings UI: MBB on monitor: {monitor_rect}")

                    else:
                        # Fallback ใช้หน้าจอหลัก
                        monitor_left = 0
                        monitor_right = self.settings_window.winfo_screenwidth()
                else:
                    # ไม่มี win32api, ใช้หน้าจอหลัก
                    monitor_left = 0
                    monitor_right = self.settings_window.winfo_screenwidth()

            except Exception as e:
                print(f"Failed to get monitor info for Settings: {e}")
                # Fallback ใช้หน้าจอหลัก
                monitor_left = 0
                monitor_right = self.settings_window.winfo_screenwidth()

            # ตัดสินใจตำแหน่งตาม MBB side
            if mbb_side == "left":
                # MBB อยู่ซ้าย -> วาง Settings ด้านขวา
                x = parent_x + parent_width + gap
                # ตรวจสอบว่าไม่ล้นจอ
                if x + settings_width > monitor_right:
                    x = parent_x - settings_width - gap  # สลับไปซ้าย
            else:
                # MBB อยู่ขวา -> วาง Settings ด้านซ้าย
                x = parent_x - settings_width - gap
                # ตรวจสอบว่าไม่ล้นจอ
                if x < monitor_left:
                    x = parent_x + parent_width + gap  # สลับไปขวา

            y = parent_y

            print(f"Settings UI positioned at: {x}, {y} (MBB side: {mbb_side})")

        except Exception as e:
            print(f"Error in smart positioning for Settings, using fallback: {e}")
            # Fallback เป็นวิธีเดิม
            x = parent_x + parent_width + 20
            y = parent_y

        self.settings_window.geometry(f"+{x}+{y}")

        # ตั้งค่าความทึบแบบไม่มีความโปร่งใส
        self.settings_window.attributes("-alpha", 1.0)

        # โหลดการตั้งค่าปัจจุบัน
        self.font_size_var.set(str(self.settings.get("font_size")))
        self.font_var.set(self.settings.get("font"))

        # อัพเดตข้อความแสดงฟอนต์ปัจจุบัน
        font_name = self.settings.get("font")
        font_size = self.settings.get("font_size")
        self.font_display_label.config(text=f"{font_name} ({font_size}px)")

        # อัพเดตค่า width และ height
        self.width_entry.delete(0, tk.END)
        self.width_entry.insert(0, str(self.settings.get("width")))
        self.height_entry.delete(0, tk.END)
        self.height_entry.insert(0, str(self.settings.get("height")))

        # ตั้งค่า variables สำหรับ toggle switches
        self.force_translate_var.set(self.settings.get("enable_force_translate", True))
        self.auto_hide_var.set(self.settings.get("enable_auto_hide", True))
        self.click_translate_var.set(self.settings.get("enable_click_translate", False))

        # อัพเดตสถานะของ toggle switches
        self.indicators = getattr(self, "indicators", {})
        for indicator_id, data in self.indicators.items():
            variable = data["variable"]
            self.update_switch_ui(indicator_id, variable.get())

        # อัพเดตชอร์ตคัท
        toggle_ui_shortcut = self.settings.get_shortcut("toggle_ui", "alt+l")
        start_stop_shortcut = self.settings.get_shortcut("start_stop_translate", "f9")
        self.toggle_ui_btn.config(text=toggle_ui_shortcut.upper())
        self.start_stop_btn.config(text=start_stop_shortcut.upper())

        # แสดงหน้าต่าง
        self.settings_window.deiconify()
        self.settings_window.lift()
        self.settings_window.attributes("-topmost", True)
        self.settings_visible = True

        # รีเซ็ตข้อความบนปุ่ม
        if hasattr(self, "display_button"):
            self.display_button.config(text="SCREEN/CPU")
        if hasattr(self, "hotkey_button"):
            self.hotkey_button.config(text="HOTKEY")
        if hasattr(self, "font_button"):
            self.font_button.config(text="FONT")

    def create_tooltip(self, widget, text):
        """สร้าง tooltip สำหรับ widget"""

        def enter(event):
            # สร้าง tooltip
            x, y, _, _ = widget.bbox("insert")
            x += widget.winfo_rootx() + 25
            y += widget.winfo_rooty() + 25

            # สร้าง top level
            self.tooltip = tk.Toplevel(widget)
            self.tooltip.overrideredirect(True)
            self.tooltip.geometry(f"+{x}+{y}")

            # สร้าง label
            label = tk.Label(
                self.tooltip,
                text=text,
                bg="#333333",
                fg="white",
                relief=tk.SOLID,
                borderwidth=1,
                font=("Bai Jamjuree Light", 11),
                padx=5,
                pady=2,
            )
            label.pack()

        def leave(event):
            # ลบ tooltip
            if hasattr(self, "tooltip"):
                self.tooltip.destroy()

        # ผูก event
        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    def open(self):
        """Toggle the advance window visibility"""
        if self.advance_window is None or not self.advance_window.winfo_exists():
            self.create_advance_window()

        if self.advance_window.winfo_viewable():
            self.close()  # ถ้ากำลังแสดงอยู่ให้ซ่อน
            if hasattr(self.parent, "advance_button"):
                self.parent.advance_button.config(text="Screen/API")
        else:
            # คำนวณตำแหน่งให้อยู่ทางขวาของ settings ui โดยเว้นระยะ 5px
            parent_x = self.parent.winfo_x()
            parent_y = self.parent.winfo_y()
            parent_width = self.parent.winfo_width()

            # กำหนดตำแหน่งใหม่
            x = parent_x + parent_width + 5  # เว้นระยะห่าง 5px
            y = parent_y  # ให้อยู่ระดับเดียวกับ settings ui

            self.advance_window.geometry(f"+{x}+{y}")
            self.advance_window.deiconify()
            self.advance_window.lift()  # ยกให้อยู่บนสุด
            self.advance_window.attributes("-topmost", True)

            self.load_current_settings()
            self.is_changed = False
            self.update_save_button()

            if hasattr(self.parent, "advance_button"):
                self.parent.advance_button.config(text="Close Advanced")

    def close_settings(self):
        self.settings_window.withdraw()
        self.settings_visible = False
        if self.advance_ui:
            self.advance_ui.close()
        if self.hotkey_ui:
            self.hotkey_ui.close()
        # ไม่ปิด font manager เมื่อปิด settings window
        # ปล่อยให้ font manager ทำงานต่อไปได้

        self.hotkey_button.config(text="HotKey")  # รีเซ็ตข้อความบนปุ่ม
        self.font_button.config(text="FONT")  # รีเซ็ตข้อความบนปุ่มฟอนต์

        # เรียก callback ถ้ามี
        if hasattr(self, "on_close_callback") and self.on_close_callback:
            self.on_close_callback()

    def validate_window_size(self, event=None):
        """Validate and update window size from entries"""
        try:
            width = int(self.width_entry.get())
            height = int(self.height_entry.get())

            # กำหนดขนาดขั้นต่ำ-สูงสุด
            width = max(300, min(2000, width))
            height = max(200, min(1000, height))

            # Update entries with validated values
            self.width_entry.delete(0, tk.END)
            self.width_entry.insert(0, str(width))
            self.height_entry.delete(0, tk.END)
            self.height_entry.insert(0, str(height))

            # Save to settings
            self.settings.set("width", width)
            self.settings.set("height", height)

            return True

        except ValueError:
            messagebox.showerror(
                "Invalid Input", "Please enter valid numbers for width and height"
            )

            # Reset to current settings values
            self.width_entry.delete(0, tk.END)
            self.width_entry.insert(0, str(self.settings.get("width")))
            self.height_entry.delete(0, tk.END)
            self.height_entry.insert(0, str(self.settings.get("height")))

            return False

    def create_settings_ui(self):
        """Initialize and setup all UI components with a new flat design"""
        # --- 1. กำหนดชุดสีสำหรับ Flat Design ---
        colors = {
            "bg": "#2E2E2E",  # สีเทาเข้มสำหรับพื้นหลังหลัก
            "border": "#4A4A4A",  # สีเทาอ่อนสำหรับเส้นขอบ
            "text_primary": "#F0F0F0",  # สีขาวนวลสำหรับข้อความหลัก
            "text_secondary": "#AAAAAA",  # สีเทาสำหรับข้อความรอง
            "entry_bg": "#3C3C3C",  # สีพื้นหลังช่องกรอก
            "button_hover": "#454545",  # สีพื้นหลังปุ่มเมื่อเมาส์ชี้
            "accent": "#4A90E2",  # สีฟ้าสำหรับเน้นส่วนที่ Active (เช่น Toggle)
            "accent_success": "#50A254",  # สีเขียวสำหรับสถานะสำเร็จ
            "accent_error": "#D05454",  # สีแดงสำหรับปุ่มปิด หรือสถานะ Error
        }

        # --- 2. ตั้งค่าหน้าต่างหลัก ---
        self.settings_window.configure(bg=colors["bg"])
        self.settings_window.overrideredirect(True)
        self.settings_window.attributes("-alpha", 1.0)

        # --- 3. ส่วนหัว (Header) ---
        header_frame = tk.Frame(self.settings_window, bg=colors["bg"])
        header_frame.pack(fill=tk.X, padx=10, pady=10)

        # ปุ่มปิด (X) แบบ Flat
        close_label = tk.Label(
            header_frame,
            text="✕",
            bg=colors["bg"],
            fg=colors["text_secondary"],
            font=("Arial", 14),
        )
        close_label.place(x=5, y=0)
        close_label.bind("<Button-1>", lambda e: self.close_settings())
        close_label.bind(
            "<Enter>", lambda e: close_label.config(fg=colors["accent_error"])
        )
        close_label.bind(
            "<Leave>", lambda e: close_label.config(fg=colors["text_secondary"])
        )

        # Container สำหรับไอคอนและข้อความ (ใช้ expand=True เพื่อจัดกึ่งกลางแนวตั้ง)
        header_main_frame = tk.Frame(header_frame, bg=colors["bg"])
        header_main_frame.pack(expand=True, pady=(20, 0))

        if hasattr(self, "mbb_icon") and self.mbb_icon:
            icon_label = tk.Label(
                header_main_frame, image=self.mbb_icon, bg=colors["bg"]
            )
            icon_label.pack(side=tk.LEFT, padx=(10, 15))

        text_frame = tk.Frame(header_main_frame, bg=colors["bg"])
        text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Label(
            text_frame,
            text="SETTINGS",
            bg=colors["bg"],
            fg=colors["text_primary"],
            font=self.theme.get_font("title", "bold"),
            anchor="w",
        ).pack(fill=tk.X)
        tk.Label(
            text_frame,
            text="การตั้งค่าหน้าต่างแสดงผลการแปล (TUI)",
            bg=colors["bg"],
            fg=colors["text_secondary"],
            font=self.theme.get_font("normal"),
            anchor="w",
        ).pack(fill=tk.X)

        # Main content frame
        main_frame = tk.Frame(self.settings_window, bg=colors["bg"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 15))

        # --- 4. สร้าง Sections ใหม่ด้วยสไตล์ Flat ---
        tui_section = self.create_settings_section(
            main_frame, "หน้าต่างผลการแปล (TUI)", colors
        )
        features_section = self.create_settings_section(main_frame, "ฟีเจอร์เสริม", colors)
        advanced_section = self.create_settings_section(
            main_frame, "การตั้งค่าขั้นสูง", colors
        )
        info_section = self.create_settings_section(
            main_frame, "คีย์ลัดที่ใช้ในปัจจุบัน(ตั้งค่าในเมนู HOTKEY)", colors
        )

        # --- 5. ปรับแก้ Widgets ในแต่ละ Section ---

        # TUI Section Content
        font_frame = tk.Frame(tui_section, bg=colors["bg"])
        font_frame.pack(fill=tk.X, pady=2)
        tk.Label(
            font_frame,
            text="Font Settings:",
            width=15,
            anchor="w",
            bg=colors["bg"],
            fg=colors["text_primary"],
            font=self.theme.get_font("normal"),
        ).pack(side=tk.LEFT)
        self.font_display_label = tk.Label(
            font_frame,
            text=f"{self.settings.get('font')} ({self.settings.get('font_size')}px)",
            bg=colors["entry_bg"],
            fg=colors["text_primary"],
            font=self.theme.get_font("normal"),
            anchor="w",
            padx=10,
        )
        self.font_display_label.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4)
        self.font_size_var = tk.StringVar(value=str(self.settings.get("font_size", 24)))
        self.font_var = tk.StringVar(
            value=self.settings.get("font", "IBM Plex Sans Thai Medium")
        )

        size_frame = tk.Frame(tui_section, bg=colors["bg"])
        size_frame.pack(fill=tk.X, pady=(8, 2))
        entry_style = {
            "bg": colors["entry_bg"],
            "fg": colors["text_primary"],
            "insertbackground": colors["text_primary"],
            "relief": "flat",
            "highlightthickness": 0,
        }
        tk.Label(
            size_frame,
            text="Width:",
            anchor="w",
            bg=colors["bg"],
            fg=colors["text_primary"],
            font=self.theme.get_font("normal"),
        ).pack(side=tk.LEFT)
        self.width_entry = tk.Entry(size_frame, width=5, **entry_style)
        self.width_entry.pack(side=tk.LEFT, padx=5, ipady=4)
        tk.Label(
            size_frame,
            text="Height:",
            anchor="w",
            bg=colors["bg"],
            fg=colors["text_primary"],
            font=self.theme.get_font("normal"),
        ).pack(side=tk.LEFT, padx=(10, 0))
        self.height_entry = tk.Entry(size_frame, width=5, **entry_style)
        self.height_entry.pack(side=tk.LEFT, padx=5, ipady=4)
        self.width_entry.bind("<FocusOut>", self.validate_window_size)
        self.height_entry.bind("<FocusOut>", self.validate_window_size)

        # Apply Button
        self.apply_button = tk.Button(
            size_frame,
            text="APPLY",
            command=self.apply_settings,
            bg=colors["accent"],
            fg=colors["text_primary"],
            relief="flat",
            activebackground=colors["accent"],
            activeforeground=colors["text_primary"],
            bd=0,
            padx=15,
            font=self.theme.get_font("normal", "bold"),
        )
        self.apply_button.pack(side=tk.RIGHT)

        # Features Section Content
        self.force_translate_var = tk.BooleanVar(
            value=self.settings.get("enable_force_translate", True)
        )
        self.auto_hide_var = tk.BooleanVar(
            value=self.settings.get("enable_auto_hide", True)
        )
        self.click_translate_var = tk.BooleanVar(
            value=self.settings.get("enable_click_translate", False)
        )
        self.hover_translation_var = tk.BooleanVar(
            value=self.settings.get("enable_hover_translation", False)
        )

        self.create_toggle_switch(
            features_section,
            "บังคับแปลด้วย R-click บน TUI",
            self.force_translate_var,
            colors,
        )
        self.create_toggle_switch(
            features_section,
            "หยุดแปลเมื่อกด W,A,S,D (กดเดินในเกมส์)",
            self.auto_hide_var,
            colors,
        )
        self.create_toggle_switch(
            features_section, "แปลแบบ 1ครั้ง/1คลิ๊ก", self.click_translate_var, colors
        )
        self.create_toggle_switch(
            features_section,
            "ตรวจจับพื้นที่แปล ตามที่เมาส์ลากผ่าน(ต้องตั้ง preset ก่อน)",
            self.hover_translation_var,
            colors,
        )

        # Advanced Section Content
        button_frame = tk.Frame(advanced_section, bg=colors["bg"])
        button_frame.pack(fill=tk.X, pady=5)
        flat_button_style = {
            "bg": colors["bg"],
            "fg": colors["text_primary"],
            "activebackground": colors["button_hover"],
            "activeforeground": colors["text_primary"],
            "relief": "flat",
            "bd": 0,
            "width": 10,
        }

        self.font_button = tk.Button(
            button_frame, text="FONT", command=self.toggle_font_ui, **flat_button_style
        )
        self.display_button = tk.Button(
            button_frame,
            text="SCREEN/CPU",
            command=self.toggle_advance_ui,
            **flat_button_style,
        )
        self.model_button = tk.Button(
            button_frame,
            text="MODEL",
            command=self.toggle_model_settings,
            **flat_button_style,
        )
        self.hotkey_button = tk.Button(
            button_frame,
            text="HOTKEY",
            command=self.toggle_hotkey_ui,
            **flat_button_style,
        )

        for button in [
            self.font_button,
            self.display_button,
            self.model_button,
            self.hotkey_button,
        ]:
            button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2, ipady=5)
            button.bind(
                "<Enter>", lambda e, b=button: b.config(bg=colors["button_hover"])
            )
            button.bind("<Leave>", lambda e, b=button: b.config(bg=colors["bg"]))

        # Splash Screen Section Content (เพิ่มใหม่)
        splash_section = self.create_settings_section(
            main_frame, "ภาพเริ่มต้นโปรแกรม", colors
        )
        
        # Create splash screen type selection
        splash_frame = tk.Frame(splash_section, bg=colors["bg"])
        splash_frame.pack(fill=tk.X, pady=5)
        
        self.splash_type_var = tk.StringVar(
            value=self.settings.get("splash_screen_type", "video")
        )
        
        # Radio buttons for splash screen type
        splash_options = [
            ("ภาพนิ่ง", "image"),
            ("ภาพเคลื่อนไหว", "video"),
            ("ปิด", "off")
        ]
        
        for text, value in splash_options:
            rb = tk.Radiobutton(
                splash_frame,
                text=text,
                variable=self.splash_type_var,
                value=value,
                bg=colors["bg"],
                fg=colors["text_primary"],
                activebackground=colors["bg"],
                activeforeground=colors["text_primary"],
                selectcolor=colors["button_hover"],
                font=self.theme.get_font("normal"),
            )
            rb.pack(side=tk.LEFT, padx=10)
        
        # Note about requiring restart
        tk.Label(
            splash_section,
            text="* การเปลี่ยนแปลงจะมีผลในครั้งถัดไปที่เริ่มโปรแกรม",
            bg=colors["bg"],
            fg=colors["text_secondary"],
            font=self.theme.get_font("small"),
        ).pack(fill=tk.X, pady=(5, 0))

        # Info Section Content
        shortcut_frame = tk.Frame(info_section, bg=colors["bg"])
        shortcut_frame.pack(fill=tk.X)
        toggle_ui_shortcut = self.settings.get_shortcut("toggle_ui", "alt+l")
        start_stop_shortcut = self.settings.get_shortcut("start_stop_translate", "f9")
        force_translate_key_shortcut = self.settings.get_shortcut("force_translate_key", "f10")  # ใหม่

        shortcut_label_style = {
            "bg": colors["entry_bg"],
            "fg": colors["text_primary"],
            "font": self.theme.get_font("small", "bold"),
            "padx": 8,
            "pady": 3,
        }
        tk.Label(
            shortcut_frame,
            text="Toggle UI:",
            bg=colors["bg"],
            fg=colors["text_secondary"],
            font=self.theme.get_font("small"),
            anchor="e",
        ).pack(side=tk.LEFT, padx=(5, 5))
        self.toggle_ui_btn = tk.Label(
            shortcut_frame, text=toggle_ui_shortcut.upper(), **shortcut_label_style
        )
        self.toggle_ui_btn.pack(side=tk.LEFT)
        tk.Label(
            shortcut_frame,
            text="Start/Stop:",
            bg=colors["bg"],
            fg=colors["text_secondary"],
            font=self.theme.get_font("small"),
            anchor="e",
        ).pack(side=tk.LEFT, padx=(15, 5))
        self.start_stop_btn = tk.Label(
            shortcut_frame, text=start_stop_shortcut.upper(), **shortcut_label_style
        )
        self.start_stop_btn.pack(side=tk.LEFT)
        
        # แถวใหม่สำหรับ Force translate hotkeys
        shortcut_frame2 = tk.Frame(info_section, bg=colors["bg"])
        shortcut_frame2.pack(fill=tk.X, pady=(5, 0))
        
        tk.Label(
            shortcut_frame2,
            text="Force (Key):",
            bg=colors["bg"],
            fg=colors["text_secondary"],
            font=self.theme.get_font("small"),
            anchor="e",
        ).pack(side=tk.LEFT, padx=(5, 5))
        self.force_key_btn = tk.Label(
            shortcut_frame2, text=force_translate_key_shortcut.upper(), **shortcut_label_style
        )
        self.force_key_btn.pack(side=tk.LEFT)
        
        tk.Label(
            shortcut_frame2,
            text="Force (R-Click TUI):",
            bg=colors["bg"],
            fg=colors["text_secondary"],
            font=self.theme.get_font("small"),
            anchor="e",
        ).pack(side=tk.LEFT, padx=(15, 5))
        self.force_rclick_btn = tk.Label(
            shortcut_frame2, text="R-CLICK", **shortcut_label_style
        )
        self.force_rclick_btn.pack(side=tk.LEFT)

        self.version_label = tk.Label(
            info_section,
            text=get_settings_version(),  # ใช้ฟังก์ชันจาก version_manager
            bg=colors["bg"],
            fg="#A020F0",  # สีม่วงเหมือนกับโมเดล Gemini
            font=("JetBrains Mono NL Light", 10),  # ฟอนต์เหมือนกับโมเดล Gemini
            anchor="center",
        )
        self.version_label.pack(fill=tk.X, pady=(10, 0))

        # --- 6. อื่นๆ ---
        self.status_label = tk.Label(
            main_frame,
            text="",
            bg=colors["bg"],
            fg=colors["accent_success"],
            font=self.theme.get_font("normal", "bold"),
        )
        self.status_label.pack(pady=(5, 0))

        self.settings_window.bind("<Button-1>", self.start_move_settings)
        self.settings_window.bind("<ButtonRelease-1>", self.stop_move_settings)
        self.settings_window.bind("<B1-Motion>", self.do_move_settings)

        self.width_entry.insert(0, str(self.settings.get("width", 960)))
        self.height_entry.insert(0, str(self.settings.get("height", 240)))

    def toggle_advance_ui(self):
        """Toggle Advanced UI window"""
        if (
            self.advance_ui is None
            or not hasattr(self.advance_ui, "advance_window")
            or not self.advance_ui.advance_window.winfo_exists()
        ):
            self.advance_ui = AdvanceUI(
                self.settings_window,
                self.settings,
                self.apply_settings_callback,
                self.ocr_toggle_callback,
            )

        if self.advance_ui.advance_window.winfo_viewable():
            self.advance_ui.close()
            self.display_button.config(text="Screen/CPU")
        else:
            self.advance_ui.open()
            self.display_button.config(text="Close Screen")

    def on_model_window_close(self):
        """Callback ที่จะถูกเรียกเมื่อหน้าต่าง ModelSettings ปิดตัวลง"""
        if hasattr(self, "model_button") and self.model_button.winfo_exists():
            self.model_button.config(text="MODEL")
        logging.info("ModelSettings window closed, button state has been reset.")

    def toggle_model_settings(self):
        """Toggle Model Settings window and handle button state with callbacks."""
        # ตรวจสอบว่าหน้าต่างลูกเปิดอยู่หรือไม่
        is_open = (
            hasattr(self, "model_settings")
            and self.model_settings
            and self.model_settings.model_window
            and self.model_settings.model_window.winfo_exists()
            and self.model_settings.model_window.winfo_viewable()
        )

        if is_open:
            # ถ้าเปิดอยู่ ให้สั่งปิดผ่าน handle_close ของหน้าต่างลูก
            # ไม่ต้องเปลี่ยนข้อความปุ่มที่นี่ เพราะ callback จะจัดการเอง
            self.model_settings.handle_close()
        else:
            # ถ้าปิดอยู่ ให้เปิดหน้าต่างใหม่
            if not hasattr(self, "model_settings") or self.model_settings is None:
                from model import ModelSettings

                # ตรวจสอบว่า self.main_app มีเมธอด update_api_settings หรือไม่
                if hasattr(self.main_app, "update_api_settings"):
                    main_app_ref = self.main_app
                    logging.info("Found update_api_settings in main_app")
                else:
                    # ลองใช้ parent ถ้า main_app ไม่มี
                    if hasattr(self.parent, "update_api_settings"):
                        main_app_ref = self.parent
                        logging.info(
                            "Found update_api_settings in parent, using parent as main_app"
                        )
                    else:
                        main_app_ref = None
                        logging.warning(
                            "Could not find update_api_settings in either main_app or parent, model changes may not apply correctly"
                        )

                self.model_settings = ModelSettings(
                    self.settings_window,
                    self.settings,
                    self.apply_settings_callback,
                    main_app=main_app_ref,
                    on_close_callback=self.on_model_window_close,  # <--- ส่ง Callback ไปที่นี่
                )

            self.model_settings.open()
            self.model_button.config(text="Close Model")

    def toggle_hotkey_ui(self):
        """เปิด/ปิดหน้าต่าง Hotkey UI"""
        try:
            if (
                not hasattr(self, "simplified_hotkey_ui")
                or self.simplified_hotkey_ui is None
            ):
                self.simplified_hotkey_ui = SimplifiedHotkeyUI(
                    self.settings_window, self.settings, self.update_hotkeys_callback
                )

            if (
                self.simplified_hotkey_ui.window
                and self.simplified_hotkey_ui.window.winfo_exists()
            ):
                self.simplified_hotkey_ui.close()
                self.hotkey_button.config(text="HotKey")
            else:
                self.simplified_hotkey_ui.open()
                self.hotkey_button.config(text="Close Hotkeys")

        except Exception as e:
            logging.error(f"Error in toggle_hotkey_ui: {e}")
            messagebox.showerror("Error", f"เกิดข้อผิดพลาดในการเปิด Hotkey UI: {e}")

    def toggle_font_ui(self):
        """เปิด/ปิดหน้าต่าง Font Manager"""
        try:
            # สร้าง font_manager หากยังไม่มี
            if not self.font_manager:
                self.font_manager = initialize_font_manager(None, self.settings)

            # ใช้ FontUIManager เพื่อจัดการ instance
            font_ui_manager = FontUIManager.get_instance()
            
            # สร้าง callback ที่จะจัดการตาม target
            def apply_callback(font_data):
                # จัดการ font application ตาม target
                target = font_data.get("target", "translated_ui")
                
                logging.info(f"🔧 Font callback in settings - target: {target}, font: {font_data.get('font')}")
                
                # *** สำคัญ: Apply เฉพาะ target ที่เลือกเท่านั้น ***
                if target == "translated_ui" and self.main_app:
                    # Apply to translated_ui ONLY
                    logging.info("📌 Applying to translated_ui ONLY...")
                    if hasattr(self.main_app, 'translated_ui') and self.main_app.translated_ui:
                        if hasattr(self.main_app.translated_ui, 'update_font'):
                            self.main_app.translated_ui.update_font(font_data["font"])
                            logging.info(f"✅ Font applied to translated_ui")
                        else:
                            logging.warning("❌ translated_ui has no update_font method")
                    else:
                        logging.warning("❌ main_app has no translated_ui")
                    
                    # *** ไม่แจ้ง translated_logs ***
                    
                elif target == "translated_logs" and self.main_app:
                    # Apply to translated_logs ONLY
                    logging.info("📌 Applying to translated_logs ONLY...")
                    # ตรวจสอบทั้ง translated_logs และ translated_logs_instance
                    logs_instance = None
                    if hasattr(self.main_app, 'translated_logs') and self.main_app.translated_logs:
                        logs_instance = self.main_app.translated_logs
                        logging.info("✅ Found translated_logs")
                    elif hasattr(self.main_app, 'translated_logs_instance') and self.main_app.translated_logs_instance:
                        logs_instance = self.main_app.translated_logs_instance
                        logging.info("✅ Found translated_logs_instance")
                    
                    if logs_instance:
                        if hasattr(logs_instance, '_update_all_fonts'):
                            logging.info(f"🎨 Calling _update_all_fonts with font: {font_data['font']}")
                            logs_instance._update_all_fonts(font_data["font"])
                            # บันทึก font_family ใหม่
                            if hasattr(logs_instance, 'current_font_family'):
                                logs_instance.current_font_family = font_data["font"]
                                logging.info(f"✅ Updated current_font_family to: {font_data['font']}")
                            # บันทึก settings
                            if hasattr(logs_instance, 'save_settings'):
                                logs_instance.save_settings()
                                logging.info("✅ Saved translated_logs settings")
                            logging.info(f"✅ Font applied to translated_logs ONLY")
                        else:
                            logging.warning("❌ translated_logs has no _update_all_fonts method")
                    else:
                        logging.warning("❌ main_app has no translated_logs/translated_logs_instance")
                    
                    # *** ไม่แจ้ง translated_ui ***
                    
                else:
                    logging.info(f"⏩ Unknown target or no main_app: {target}")
                
                # *** ไม่อัพเดต global settings เพื่อป้องกันการ trigger observers ***
                # อัพเดตเฉพาะเมื่อต้องการให้ทั้งระบบรับรู้
                
                logging.info(f"✅ Font callback completed for target: {target}")
            
            # สร้างหรือดึง FontUI instance
            self.font_ui = font_ui_manager.get_or_create_font_ui(
                self.settings_window,
                self.font_manager,
                self.settings,
                apply_callback
            )
            
            # ถ้าหน้าต่างกำลังแสดงอยู่ ให้ปิด
            if (
                hasattr(self.font_ui, "font_window")
                and self.font_ui.font_window
                and self.font_ui.font_window.winfo_exists()
                and self.font_ui.font_window.winfo_viewable()
            ):
                self.font_ui.close_font_ui()
                self.font_button.config(text="FONT")
            # ถ้าหน้าต่างปิดอยู่ ให้เปิด
            else:
                self.font_ui.open_font_ui(
                    translated_ui=(
                        self.main_app.translated_ui
                        if hasattr(self.main_app, "translated_ui")
                        else None
                    )
                )
                self.font_button.config(text="Close Font")

        except Exception as e:
            logging.error(f"Error toggling font UI: {e}")
            messagebox.showerror("Error", f"เกิดข้อผิดพลาดในการเปิด Font Manager: {e}")

    def create_toggle_switch(self, parent, text, variable, colors):
        """สร้าง Toggle Switch สไตล์ Flat Design แบบสี่เหลี่ยมที่คมชัด"""
        container = tk.Frame(parent, bg=colors["bg"])
        container.pack(fill=tk.X, pady=4)

        label = tk.Label(
            container,
            text=text,
            bg=colors["bg"],
            fg=colors["text_primary"],
            font=self.theme.get_font("normal"),
            cursor="hand2",
            anchor="w",
        )
        label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # ใช้ Frame สำหรับ Track เพื่อให้เป็นสี่เหลี่ยมสมบูรณ์
        track_width, track_height = 42, 22
        track = tk.Frame(
            container,
            width=track_width,
            height=track_height,
            bg=colors["border"],  # สีเริ่มต้น (สถานะ Off)
        )
        track.pack(side=tk.RIGHT, padx=5)
        track.pack_propagate(False)  # ป้องกัน Frame หดตัว

        # ใช้ Label สำหรับ Knob เพื่อให้เป็นสี่เหลี่ยมทึบ
        knob_size = track_height - 6
        knob = tk.Label(track, bg="#FFFFFF")

        def update_switch_look(is_on):
            """อัปเดตหน้าตาของสวิตช์ (สีและตำแหน่ง Knob)"""
            knob_padding = 3
            if is_on:
                track.config(bg=colors["accent"])
                knob.place(
                    x=track_width - knob_size - knob_padding,
                    y=knob_padding,
                    width=knob_size,
                    height=knob_size,
                )
            else:
                track.config(bg=colors["border"])
                knob.place(
                    x=knob_padding, y=knob_padding, width=knob_size, height=knob_size
                )

        def save_toggle_state(*args):
            """บันทึกค่าของ Toggle ลงใน Settings"""
            new_state = variable.get()
            logging.info(f"SettingsUI: save_toggle_state called with text='{text}', new_state={new_state}")
            
            if "Force Translate" in text or "บังคับแปลด้วย R-click" in text:
                self.settings.set("enable_force_translate", new_state)
            elif "Hide UI" in text or "หยุดแปลเมื่อกด W,A,S,D" in text:
                self.settings.set("enable_auto_hide", new_state)
            elif "Click Translate" in text or "แปลแบบ 1ครั้ง/1คลิ๊ก" in text:
                self.settings.set("enable_click_translate", new_state)
                if self.toggle_click_callback:
                    logging.info(f"SettingsUI: Calling toggle_click_callback with {new_state}")
                    self.toggle_click_callback(new_state)
                else:
                    logging.warning("SettingsUI: toggle_click_callback is None")
            elif "Hover Translation" in text or "ตรวจจับพื้นที่แปล" in text:
                self.settings.set("enable_hover_translation", new_state)
                if self.toggle_hover_callback:
                    logging.info(f"SettingsUI: Calling toggle_hover_callback with {new_state}")
                    self.toggle_hover_callback(new_state)
                else:
                    logging.warning("SettingsUI: toggle_hover_callback is None")

        # ล้าง trace เก่า (ถ้ามี) เพื่อป้องกันการเรียกซ้ำซ้อน
        for mode, cb_name in variable.trace_info():
            variable.trace_remove(mode, cb_name)

        # ผูก BooleanVar กับฟังก์ชันต่างๆ
        variable.trace_add("write", lambda *args: update_switch_look(variable.get()))
        variable.trace_add("write", save_toggle_state)

        # ทำให้ทุกส่วนของ Widget กดเพื่อสลับค่าได้
        for widget in [container, label, track, knob]:
            widget.bind(
                "<Button-1>", lambda e: variable.set(not variable.get()), add="+"
            )

        # ตั้งค่าเริ่มต้นของสวิตช์เมื่อถูกสร้างขึ้น
        update_switch_look(variable.get())

    def toggle_switch_state(self, variable):
        """Toggle สถานะของ variable โดยตรง และอัพเดท UI"""
        # Toggle ค่า variable
        new_state = not variable.get()
        variable.set(new_state)

        # แสดงค่าใหม่
        print(f"Variable toggled to: {new_state}")

        # ค้นหา indicator ที่เกี่ยวข้องกับ variable นี้
        for indicator_id, data in self.indicators.items():
            if data["variable"] == variable:
                # อัพเดท UI ของ switch
                self.update_switch_ui(indicator_id, new_state)
                break

    def toggle_switch(self, indicator_id):
        """Toggle สถานะของ switch และอัพเดท UI"""
        if indicator_id not in self.indicators:
            return

        # ดึงข้อมูล
        indicator_data = self.indicators[indicator_id]
        indicator = indicator_data["indicator"]  # เปลี่ยนจาก ["canvas"] เป็น ["indicator"]
        bg = indicator_data["bg"]
        variable = indicator_data["variable"]

        # ตรวจสอบค่าปัจจุบัน
        current_value = variable.get()

        # Toggle ค่า variable
        variable.set(not current_value)

        # อัพเดท UI
        self.update_switch_ui(indicator_id, not current_value)

    def update_switch_ui(self, indicator_id, is_on):
        """อัพเดท UI ของ switch ตามสถานะใหม่"""
        if indicator_id not in self.indicators:
            return

        indicator_data = self.indicators[indicator_id]
        indicator = indicator_data["indicator"]
        bg = indicator_data["bg"]
        x_on = indicator_data.get("x_on", 22)
        x_off = indicator_data.get("x_off", 4)

        if is_on:  # เปิด
            indicator.place(x=x_on)
            bg.config(bg=self.theme.get_color("success"))  # สีเขียวจาก theme
        else:  # ปิด
            indicator.place(x=x_off)
            bg.config(bg=self.theme.get_color("border_normal"))  # สีเทาจาก theme

    def apply_settings(self, settings_dict=None):
        """Apply settings with validation and show temporary message"""
        try:
            # กรณีกดปุ่ม Apply จาก settings UI
            if settings_dict is None:
                try:
                    # รวบรวมค่าการตั้งค่าจาก UI
                    # ดึงค่าจากตัวแปรโดยตรงแทนการดึงจาก UI
                    font_size = int(self.font_size_var.get())
                    font = str(self.font_var.get()).strip()
                    width = max(300, min(2000, int(self.width_entry.get())))
                    height = max(200, min(1000, int(self.height_entry.get())))

                    # ดึงค่าจาก toggle switches โดยตรง
                    enable_force = bool(self.force_translate_var.get())
                    enable_auto_hide = bool(self.auto_hide_var.get())
                    # enable_auto_switch = bool(self.auto_switch_var.get())
                    enable_click_translate = bool(self.click_translate_var.get())
                    enable_hover_translation = bool(self.hover_translation_var.get())
                    
                    # ดึงค่า splash screen type
                    splash_type = self.splash_type_var.get()

                    # บันทึกค่าลง settings ทีละตัว
                    self.settings.set("font_size", font_size)
                    self.settings.set("font", font)
                    self.settings.set("width", width)
                    self.settings.set("height", height)
                    self.settings.set("enable_force_translate", enable_force)
                    self.settings.set("enable_auto_hide", enable_auto_hide)
                    # self.settings.set("enable_auto_area_switch", enable_auto_switch)
                    self.settings.set("enable_click_translate", enable_click_translate)
                    self.settings.set(
                        "enable_hover_translation", enable_hover_translation
                    )
                    self.settings.set("splash_screen_type", splash_type)

                    # สร้าง dict สำหรับส่งต่อให้ callback
                    settings_dict = {
                        "font_size": font_size,
                        "font": font,
                        "width": width,
                        "height": height,
                        "enable_force_translate": enable_force,
                        "enable_auto_hide": enable_auto_hide,
                        # "enable_auto_area_switch": enable_auto_switch,
                        "enable_click_translate": enable_click_translate,
                        "enable_hover_translation": enable_hover_translation,
                    }

                    # เรียก callback เพื่ออัพเดท UI อื่นๆ
                    if self.apply_settings_callback:
                        self.apply_settings_callback(settings_dict)
                        logging.info("Settings applied successfully")

                    # เปลี่ยนข้อความปุ่ม Apply ชั่วคราว - ใช้ theme colors
                    self.apply_button.config(
                        text="✓ APPLIED",
                        bg=self.theme.get_color("success"),
                        fg="white",
                        activebackground=self.theme.get_color("success"),
                        activeforeground="white",
                    )

                    # แสดงข้อความ success
                    self.status_label.config(text="Settings applied successfully!")

                    # รีเซ็ตกลับหลังจาก 2 วินาที - ใช้ theme colors
                    def reset_apply_button():
                        self.apply_button.config(
                            text="APPLY",
                            bg=self.theme.get_color("bg_secondary"),
                            fg=self.theme.get_color("text_primary"),
                            activebackground=self.theme.get_color("hover_light"),
                            activeforeground=self.theme.get_color("text_primary"),
                        )

                    self.settings_window.after(2000, reset_apply_button)
                    self.settings_window.after(
                        2000, lambda: self.status_label.config(text="")
                    )

                    # อัพเดท toggle switch UI อีกครั้งเพื่อความมั่นใจ
                    for indicator_id, data in self.indicators.items():
                        variable = data["variable"]
                        self.update_switch_ui(indicator_id, variable.get())

                    # พิมพ์ข้อมูลตัวแปรเพื่อการตรวจสอบ
                    print(f"Applied settings:")
                    print(f"- Force Translate: {enable_force}")
                    print(f"- Auto Hide: {enable_auto_hide}")
                    print(f"- Click Translate: {enable_click_translate}")
                    print(f"- Hover Translation: {enable_hover_translation}")

                    return True, None

                except ValueError as e:
                    self.status_label.config(
                        text=f"Error: {str(e)}", fg=self.theme.get_color("error")
                    )
                    self.settings_window.after(
                        3000,
                        lambda: self.status_label.config(
                            text="", fg=self.theme.get_color("success")
                        ),
                    )
                    raise ValueError(f"Invalid input value: {str(e)}")

            # กรณีเรียกจาก advance settings (คงเดิม)
            else:
                logging.info("Applying advanced settings")
                print(f"💾 [DEBUG] Applying advance settings: {settings_dict}")

                # อัพเดทค่าลง settings
                for key, value in settings_dict.items():
                    if value is not None:  # เฉพาะค่าที่ไม่เป็น None
                        self.settings.set(key, value)
                        print(f"💾 [DEBUG] Set {key} = {value}")

                # บันทึกไฟล์
                self.settings.save_settings()
                print("💾 [DEBUG] Advanced settings saved to file")

                # ไม่เรียก self.apply_settings_callback อีกครั้งเพื่อป้องกัน infinite loop
                # เพราะ callback นี้ถูกเรียกจาก advance_ui แล้ว
                print("💾 [DEBUG] Advanced settings applied successfully")

                return True, None

        except Exception as e:
            error_msg = f"Error applying settings: {str(e)}"
            logging.error(error_msg)

            # แสดงข้อความ error - ใช้ theme colors
            self.status_label.config(text=error_msg, fg=self.theme.get_color("error"))
            self.settings_window.after(
                3000,
                lambda: self.status_label.config(
                    text="", fg=self.theme.get_color("success")
                ),
            )

            return False, error_msg

    def reset_apply_button(self):
        """Reset the apply button text and status label"""
        self.apply_button.config(text="APPLY")
        self.status_label.config(text="")

    def start_move_settings(self, event):
        self.settings_x = event.x
        self.settings_y = event.y

    def stop_move_settings(self, event):
        self.settings_x = None
        self.settings_y = None

    def do_move_settings(self, event):
        deltax = event.x - self.settings_x
        deltay = event.y - self.settings_y
        x = self.settings_window.winfo_x() + deltax
        y = self.settings_window.winfo_y() + deltay
        self.settings_window.geometry(f"+{x}+{y}")

        if (
            self.hotkey_ui
            and self.hotkey_ui.hotkey_window
            and self.hotkey_ui.hotkey_window.winfo_exists()
        ):
            hotkey_window = self.hotkey_ui.hotkey_window
            hotkey_window.update_idletasks()
            settings_height = self.settings_window.winfo_height()
            hotkey_x = x - hotkey_window.winfo_width() - 5
            hotkey_y = y + settings_height - hotkey_window.winfo_height()
            hotkey_window.geometry(f"+{hotkey_x}+{hotkey_y}")

    def open_advance_ui(self):
        # สร้าง advance_ui ใหม่ถ้ายังไม่มีหรือถูกปิดไป
        if (
            self.advance_ui is None
            or not hasattr(self.advance_ui, "advance_window")
            or not self.advance_ui.advance_window.winfo_exists()
        ):
            self.advance_ui = AdvanceUI(
                self.settings_window, self.settings, self.apply_settings_callback, None
            )

        # เปิดหน้าต่าง advance_ui
        self.advance_ui.open()
