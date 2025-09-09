# Game Data Manager - ระบบจัดการข้อมูลเกมสำหรับ MBB
import json
import os
import shutil
from datetime import datetime
from typing import Dict, Optional, Any
import glob

class GameManager:
    """คลาสจัดการข้อมูลเกมทั้งหมด"""
    
    def __init__(self, config_file: str = "games_config.json"):
        self.config_file = config_file
        self.config = {}
        self.load_config()
    
    def load_config(self) -> None:
        """โหลดการตั้งค่าเกมจากไฟล์"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading config: {e}")
                self._create_default_config()
        else:
            self._create_default_config()
    
    def _create_default_config(self) -> None:
        """สร้างไฟล์ config เริ่มต้น"""
        self.config = {
            "version": "1.0",
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "games": {
                "magicite_babel": {
                    "id": "magicite_babel",
                    "name": "Magicite Babel",
                    "npc_file": "NPC.json",
                    "presets_file": "settings.json",
                    "description": "เกมหลัก Magicite Babel",
                    "created_date": datetime.now().strftime("%Y-%m-%d"),
                    "last_played": None
                }
            },
            "active_game": "magicite_babel",
            "backup": {
                "auto_backup": True,
                "backup_on_switch": True,
                "max_backups": 10,
                "backup_directory": "backups/"
            },
            "settings": {
                "show_game_info": True,
                "confirm_before_switch": True,
                "auto_reload_data": True
            }
        }
        self.save_config()
    
    def save_config(self) -> None:
        """บันทึกการตั้งค่าลงไฟล์"""
        try:
            self.config["last_updated"] = datetime.now().strftime("%Y-%m-%d")
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
        except IOError as e:
            print(f"Error saving config: {e}")
    
    def get_active_game(self) -> Optional[Dict[str, Any]]:
        """ดึงข้อมูลเกมปัจจุบัน"""
        active_id = self.config.get("active_game")
        games = self.config.get("games", {})
        return games.get(active_id) if active_id else None
    
    def get_all_games(self) -> Dict[str, Dict[str, Any]]:
        """ดึงข้อมูลเกมทั้งหมด"""
        return self.config.get("games", {})
    
    def get_game_info(self, game_id: str) -> Optional[Dict[str, Any]]:
        """ดึงข้อมูลเกมตาม ID"""
        games = self.config.get("games", {})
        return games.get(game_id)
    
    def switch_game(self, game_id: str, auto_backup: bool = True) -> Dict[str, Any]:
        """สลับเกม
        
        Args:
            game_id: ID ของเกมที่จะสลับไป
            auto_backup: สำรองข้อมูลเกมปัจจุบันก่อนสลับ
            
        Returns:
            Dict ข้อมูลเกมใหม่ที่สลับไป
            
        Raises:
            ValueError: ถ้าไม่พบเกมที่ระบุ
        """
        games = self.config.get("games", {})
        if game_id not in games:
            raise ValueError(f"Game '{game_id}' not found")
        
        # สำรองข้อมูลเกมปัจจุบัน
        current_game = self.get_active_game()
        if current_game and auto_backup:
            self.backup_game_data(current_game["id"])
        
        # สลับเกม
        old_active = self.config.get("active_game")
        self.config["active_game"] = game_id
        
        # อัพเดต last_played
        games[game_id]["last_played"] = datetime.now().isoformat()
        
        # กู้คืนข้อมูลเกมใหม่
        new_game = games[game_id]
        success = self.restore_game_data(game_id)
        
        if success:
            self.save_config()
            return {
                "success": True,
                "game": new_game,
                "previous_game": old_active,
                "message": f"สลับเป็นเกม '{new_game['name']}' เรียบร้อย"
            }
        else:
            # กลับคืนถ้าไม่สำเร็จ
            self.config["active_game"] = old_active
            return {
                "success": False,
                "game": None,
                "previous_game": old_active,
                "message": f"ไม่สามารถกู้คืนข้อมูลเกม '{new_game['name']}' ได้"
            }