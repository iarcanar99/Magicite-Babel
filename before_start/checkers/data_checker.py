# checkers/data_checker.py

import json
import os
from typing import Dict


class DataChecker:
    def __init__(self):
        self.project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.npc_file = os.path.join(self.project_root, "npc.json")
        self.settings_file = os.path.join(self.project_root, "settings.json")

    def check_all(self) -> dict:
        result = {"status": "ready", "details": {}}

        npc_check = self._check_npc_json()
        result["details"]["npc_json"] = npc_check
        if not npc_check["valid"]:
            result["status"] = "error"

        result["details"]["settings"] = self._check_settings()
        result["details"]["models"] = self._check_ocr_models()

        return result

    def _check_npc_json(self) -> dict:
        try:
            if os.path.exists(self.npc_file):
                with open(self.npc_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # นับตัวละครในแต่ละหมวด
                main_chars = len(data.get("main_characters", []))
                npcs = len(data.get("npcs", []))
                lore = len(data.get("lore", []))
                total_entries = main_chars + npcs + lore

                return {
                    "valid": True, 
                    "total_entries": total_entries,
                    "main_characters": main_chars,
                    "npcs": npcs,
                    "lore": lore,
                    "file_exists": True,
                    "summary": f"Main: {main_chars}, NPCs: {npcs}, Lore: {lore}"
                }
            else:
                return {"valid": False, "error": "npc.json not found", "file_exists": False}
        except json.JSONDecodeError as e:
            return {"valid": False, "error": f"JSON format error", "file_exists": True}
        except Exception as e:
            return {"valid": False, "error": str(e)[:30], "file_exists": False}

    def _check_settings(self) -> dict:
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    json.load(f)
                return {"valid": True, "file_exists": True}
            else:
                return {"valid": True, "file_exists": False, "note": "Will be created on first run"}
        except json.JSONDecodeError:
            return {"valid": False, "error": "Invalid JSON format", "file_exists": True}
        except Exception as e:
            return {"valid": False, "error": str(e)[:50], "file_exists": False}

    def _check_ocr_models(self) -> dict:
        try:
            # ตรวจสอบ EasyOCR models
            model_paths = [
                os.path.expanduser("~/.EasyOCR/model"),
                os.path.expanduser("~/.EasyOCR/model/craft_mlt_25k.pth"),
                os.path.expanduser("~/.EasyOCR/model/latin_g2.pth")
            ]
            
            models_found = 0
            for path in model_paths:
                if os.path.exists(path):
                    models_found += 1

            if models_found > 0:
                return {"downloaded": True, "models_found": models_found, "total_checked": len(model_paths)}
            else:
                return {"downloaded": False, "note": "Models will be downloaded on first OCR run"}
        except Exception as e:
            return {"downloaded": False, "error": str(e)[:50]}
