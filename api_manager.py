import os
import time
import json
import logging
from dotenv import load_dotenv, set_key
from pathlib import Path

# โหลด environment variables
load_dotenv()

class APIKeyManager:
    """
    คลาสสำหรับจัดการ API Keys แบบรวมศูนย์
    ทำให้โปรแกรมสามารถใช้ API Key จากที่นี้ได้โดยตรง ไม่ต้องอ่านจาก .env ทุกครั้ง
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(APIKeyManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize API keys from environment variables"""
        self._gemini_api_key = os.environ.get("GEMINI_API_KEY", "")
        self._is_modified = False
        self._subscribers = []
        self._logger = logging.getLogger(__name__)
        self._logger.info("APIKeyManager initialized")
        
    def register_subscriber(self, callback):
        """Register a callback function to be called when API keys change"""
        if callback not in self._subscribers:
            self._subscribers.append(callback)
            
    def unregister_subscriber(self, callback):
        """Unregister a callback function"""
        if callback in self._subscribers:
            self._subscribers.remove(callback)
            
    def _notify_subscribers(self, key_type):
        """Notify all subscribers that a key has changed"""
        for callback in self._subscribers:
            try:
                callback(key_type)
            except Exception as e:
                self._logger.error(f"Error notifying subscriber: {e}")
    
    @property
    def gemini_api_key(self):
        """Get the Google Gemini API key"""
        return self._gemini_api_key
    
    @gemini_api_key.setter
    def gemini_api_key(self, value):
        """Set the Google Gemini API key"""
        if self._gemini_api_key != value:
            self._gemini_api_key = value
            os.environ["GEMINI_API_KEY"] = value or ""
            self._is_modified = True
            self._notify_subscribers("gemini")
    
    def save_to_env_file(self):
        """Save API keys to .env file"""
        if not self._is_modified:
            return True
            
        env_path = os.path.join(os.getcwd(), ".env")
        try:
            # ถ้าไฟล์ไม่มีอยู่ ให้สร้างใหม่
            if not os.path.exists(env_path):
                with open(env_path, "w", encoding="utf-8") as f:
                    f.write("# API Keys for Magicite Babel\n")
                    f.write("# --------------------------\n")
            
            # อ่านค่าเดิมก่อน
            env_data = {}
            if os.path.exists(env_path):
                try:
                    with open(env_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            if line.strip() and not line.strip().startswith('#') and '=' in line:
                                key, value = line.strip().split('=', 1)
                                env_data[key.strip()] = value.strip()
                except Exception as e:
                    self._logger.error(f"ไม่สามารถอ่านไฟล์ .env ได้: {e}")
            
            # อัพเดทค่า
            env_data["GEMINI_API_KEY"] = self._gemini_api_key
            
            try:
                # บันทึกค่าลงไฟล์แบบปลอดภัย
                temp_path = env_path + ".tmp"
                with open(temp_path, 'w', encoding='utf-8') as f:
                    f.write("# API Keys for Magicite Babel\n")
                    f.write("# --------------------------\n")
                    f.write("# เสามารถใส่ API key ที่ต้องการใช้ในการแปลที่นี่\n\n")
                    
                    # เขียน API keys
                    f.write(f"# API key สำหรับ Google Gemini (https://ai.google.dev/)\n")
                    f.write(f"GEMINI_API_KEY={env_data.get('GEMINI_API_KEY', '')}\n\n")
                    
                    # เขียนค่าอื่นๆ ที่ไม่ใช่ API keys กลับไป
                    f.write("# อย่าแก้ไขส่วนนี้หากไม่เข้าใจ\n")
                    for key, value in env_data.items():
                        if key != "GEMINI_API_KEY":
                            f.write(f"{key}={value}\n")
                
                # ใช้ os.replace เพราะปลอดภัยกว่าในการเขียนทับไฟล์
                import os
                if os.path.exists(env_path):
                    try:
                        # สำรองไฟล์เดิมเผื่อมีปัญหา
                        backup_path = env_path + ".bak"
                        if os.path.exists(backup_path):
                            os.remove(backup_path)
                        import shutil
                        shutil.copy2(env_path, backup_path)
                    except Exception as e:
                        self._logger.warning(f"ไม่สามารถสำรองไฟล์ .env ได้: {e}")
                
                # เขียนไฟล์ใหม่แทนที่ไฟล์เดิม
                try:
                    if os.path.exists(env_path):
                        os.replace(temp_path, env_path)
                    else:
                        os.rename(temp_path, env_path)
                    self._is_modified = False
                    return True
                except Exception as e:
                    self._logger.error(f"ไม่สามารถบันทึกไฟล์ .env ได้: {e}")
                    return False
                
            except Exception as e:
                self._logger.error(f"เกิดข้อผิดพลาดในการบันทึก API keys: {e}")
                return False
                
        except Exception as e:
            self._logger.error(f"เกิดข้อผิดพลาดในการบันทึก API keys: {e}")
            return False
    
    def reload_from_env(self):
        """โหลด API keys ใหม่จากไฟล์ .env"""
        try:
            load_dotenv(override=True)
            self._gemini_api_key = os.environ.get("GEMINI_API_KEY", "")
            self._is_modified = False
            self._notify_subscribers("all")
            return True
        except Exception as e:
            self._logger.error(f"เกิดข้อผิดพลาดในการโหลด API keys: {e}")
            return False
    
    def has_key(self, key_type):
        """ตรวจสอบว่ามี API key สำหรับ service นี้หรือไม่"""
        if key_type.lower() == "gemini":
            return bool(self._gemini_api_key)
        return False
    
    def get_key(self, key_type):
        """รับ API key ตามประเภทที่ต้องการ"""
        if key_type.lower() == "gemini":
            return self._gemini_api_key
        return None

# สร้าง instance เดียวสำหรับทั้งโปรแกรม
api_manager = APIKeyManager()
