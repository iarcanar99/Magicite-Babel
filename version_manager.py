"""
MBB Version Manager
จัดการเวอร์ชั่นแบบรวมศูนย์สำหรับโปรเจ็ค MBB

Protocol การอัพเดตเวอร์ชั่น:
- Minor Version (.1-.9): เพิ่มโมดูลใหม่หรือฟีเจอร์ใหม่
- Build Number: วันที่ + ลำดับการแก้ไข (DDMMYYYY.XX)
- แก้ไขบัค/ปรับปรุงระบบเดิม: เพิ่มแค่ build number
"""

import datetime
import os
import json

class VersionManager:
    def __init__(self):
        # *** MAIN VERSION CONTROL CENTER ***
        self.MAJOR_VERSION = "9"
        self.MINOR_VERSION = "1"
        self.BUILD_DATE = "04082025"
        self.BUILD_REVISION = "01"
        
        # ข้อมูลเพิ่มเติม
        self.AUTHOR = "iarcanar"
        self.PROJECT_NAME = "MBB"
        self.FULL_PROJECT_NAME = "Magicite Babel"
    
    @property
    def version_number(self):
        """เลขเวอร์ชั่นแบบสั้น เช่น 9.1"""
        return f"{self.MAJOR_VERSION}.{self.MINOR_VERSION}"
    
    @property
    def build_number(self):
        """Build number แบบเต็ม เช่น 19072025.01"""
        return f"{self.BUILD_DATE}.{self.BUILD_REVISION}"
    
    @property
    def version_display_mbb(self):
        """แสดงบนหน้าหลัก MBB เช่น V-9.1"""
        return f"V-{self.version_number}"
    
    @property
    def version_display_settings(self):
        """แสดงบนหน้า Settings แบบเต็ม"""
        return f"{self.PROJECT_NAME} v{self.version_number} build {self.build_number} | by {self.AUTHOR}"
    
    @property
    def version_full_info(self):
        """ข้อมูลเวอร์ชั่นแบบเต็ม"""
        return {
            "project_name": self.PROJECT_NAME,
            "full_project_name": self.FULL_PROJECT_NAME,
            "major": self.MAJOR_VERSION,
            "minor": self.MINOR_VERSION,
            "build_date": self.BUILD_DATE,
            "build_revision": self.BUILD_REVISION,
            "version_number": self.version_number,
            "build_number": self.build_number,
            "author": self.AUTHOR,
            "display_mbb": self.version_display_mbb,
            "display_settings": self.version_display_settings
        }
    
    def update_build_today(self, revision="01"):
        """อัพเดต build เป็นวันที่ปัจจุบัน"""
        today = datetime.datetime.now()
        self.BUILD_DATE = today.strftime("%d%m%Y")
        self.BUILD_REVISION = revision
        return self.build_number
    
    def increment_minor_version(self):
        """เพิ่ม minor version (สำหรับฟีเจอร์ใหม่)"""
        current_minor = int(self.MINOR_VERSION)
        if current_minor < 9:
            self.MINOR_VERSION = str(current_minor + 1)
        return self.version_number

# สร้าง instance สำหรับใช้งานทั่วโปรเจ็ค
version_manager = VersionManager()

def get_version_info():
    """ฟังก์ชันสำหรับเรียกใช้ข้อมูลเวอร์ชั่น"""
    return version_manager.version_full_info

def get_mbb_version():
    """เวอร์ชั่นสำหรับแสดงบนหน้าหลัก MBB"""
    return version_manager.version_display_mbb

def get_settings_version():
    """เวอร์ชั่นสำหรับแสดงบนหน้า Settings"""
    return version_manager.version_display_settings

# Export สำหรับการใช้งาน
__all__ = [
    'VersionManager', 
    'version_manager', 
    'get_version_info', 
    'get_mbb_version', 
    'get_settings_version'
]
