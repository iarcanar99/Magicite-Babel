import logging


class FeatureManager:
    """จัดการฟีเจอร์ที่เปิดใช้งานในแต่ละเวอร์ชั่นของโปรแกรม"""

    def __init__(self, app_version="beta"):
        """
        กำหนดฟีเจอร์ที่เปิดใช้งานตามเวอร์ชั่น
        Args:
            app_version (str): เวอร์ชั่นของแอพ ("beta", "release")
        """
        self.app_version = app_version

        # ฟีเจอร์พื้นฐานที่เปิดใช้งานทุกเวอร์ชั่น
        self.basic_features = {
            "ocr_translation": True,  # ฟีเจอร์แปลภาษาด้วย OCR
            "model_selection": True,  # เลือก AI model
            "area_selection": True,  # เลือกพื้นที่แปล
            "preset_system": True,  # ระบบ preset
            "click_translate": True,  # แปลเมื่อคลิก
        }

        # ฟีเจอร์ขั้นสูงที่อาจปิดในเวอร์ชั่นทดสอบ
        self.advanced_features = {
            "hover_translation": True,  # แปลเมื่อ hover เมาส์
            "smart_area_switching": False,  # สลับพื้นที่อัตโนมัติ
            "npc_manager": True,  # จัดการข้อมูล NPC
            "theme_customization": True,  # ปรับแต่งธีม
        }

        # เปิดฟีเจอร์ทั้งหมดในเวอร์ชั่น release
        if app_version.lower() == "release":
            for feature in self.advanced_features:
                if feature != "swap_data":  # คงสถานะปิดสำหรับ swap_data
                    self.advanced_features[feature] = True

    def is_feature_enabled(self, feature_name):
        """
        ตรวจสอบว่าฟีเจอร์นี้เปิดใช้งานหรือไม่
        Args:
            feature_name (str): ชื่อของฟีเจอร์ที่ต้องการตรวจสอบ

        Returns:
            bool: True ถ้าฟีเจอร์เปิดใช้งาน, False ถ้าปิด
        """
        # ตรวจสอบในฟีเจอร์พื้นฐานก่อน
        if feature_name in self.basic_features:
            return self.basic_features[feature_name]

        # ตรวจสอบในฟีเจอร์ขั้นสูง
        if feature_name in self.advanced_features:
            return self.advanced_features[feature_name]

        # ไม่พบฟีเจอร์ในรายการที่กำหนด
        logging.warning(f"FeatureManager: ไม่พบฟีเจอร์ '{feature_name}' ในรายการ")
        return False

    def get_disabled_features(self):
        """รับรายการฟีเจอร์ที่ถูกปิดไว้"""
        disabled = []

        for feature, enabled in self.basic_features.items():
            if not enabled:
                disabled.append(feature)

        for feature, enabled in self.advanced_features.items():
            if not enabled:
                disabled.append(feature)

        return disabled
