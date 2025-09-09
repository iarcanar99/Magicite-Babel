# 🎛️ FeatureManager Module Guide

**ไฟล์:** `FeatureManager.py`  
**คลาสหลัก:** `FeatureManager`  

## 🎯 Overview
FeatureManager เป็นระบบจัดการฟีเจอร์ของ MBB ที่ช่วยควบคุมการเปิด/ปิดฟีเจอร์ต่างๆ ตามเวอร์ชั่นของแอปพลิเคชัน เพื่อให้สามารถแยกฟีเจอร์สำหรับ beta และ release version ได้

## 🏗️ Architecture

### 📋 Core Class Structure

```python
class FeatureManager:
    def __init__(self, app_version="beta"):
        self.app_version = app_version
        self.basic_features = {...}      # ฟีเจอร์พื้นฐาน
        self.advanced_features = {...}   # ฟีเจอร์ขั้นสูง
```

## 🎮 Feature Categories

### 🔧 Basic Features (พื้นฐาน)
```python
self.basic_features = {
    "ocr_translation": True,     # ฟีเจอร์แปลภาษาด้วย OCR
    "model_selection": True,     # เลือก AI model  
    "area_selection": True,      # เลือกพื้นที่แปล
    "preset_system": True,       # ระบบ preset
    "click_translate": True,     # แปลเมื่อคลิก
}
```

**หมายเหตุ:** ฟีเจอร์พื้นฐานเปิดใช้งานทุกเวอร์ชั่น (beta และ release)

### ⚡ Advanced Features (ขั้นสูง)
```python
self.advanced_features = {
    "hover_translation": True,       # แปลเมื่อ hover เมาส์
    "smart_area_switching": False,   # สลับพื้นที่อัตโนมัติ  
    "npc_manager": True,            # จัดการข้อมูล NPC
    "theme_customization": True,     # ปรับแต่งธีม
}
```

**หมายเหตุ:** ฟีเจอร์ขั้นสูงอาจปิดในเวอร์ชั่น beta เพื่อความเสถียร

## 🔄 Version Management

### 📊 Version Types
```python
# Beta Version (Default)
app_version = "beta"
- ฟีเจอร์พื้นฐาน: ✅ เปิดทั้งหมด
- ฟีเจอร์ขั้นสูง: ⚠️ เปิดบางส่วน (ตาม configuration)

# Release Version  
app_version = "release"
- ฟีเจอร์พื้นฐาน: ✅ เปิดทั้งหมด
- ฟีเจอร์ขั้นสูง: ✅ เปิดทั้งหมด (ยกเว้น swap_data)
```

### 🎯 Release Version Logic
```python
if app_version.lower() == "release":
    for feature in self.advanced_features:
        if feature != "swap_data":  # คงสถานะปิดสำหรับ swap_data
            self.advanced_features[feature] = True
```

## 🔧 Key Methods

### ✅ Feature Checking
```python
def is_feature_enabled(self, feature_name):
    """
    ตรวจสอบว่าฟีเจอร์นี้เปิดใช้งานหรือไม่
    
    Args:
        feature_name (str): ชื่อของฟีเจอร์ที่ต้องการตรวจสอบ
        
    Returns:
        bool: True ถ้าฟีเจอร์เปิดใช้งาน, False ถ้าปิด
    """
    # Priority: basic_features → advanced_features → False
```

### 📋 Feature Listing
```python
def get_disabled_features(self):
    """รับรายการฟีเจอร์ที่ถูกปิดไว้"""
    disabled = []
    
    # ตรวจสอบ basic features
    for feature, enabled in self.basic_features.items():
        if not enabled:
            disabled.append(feature)
            
    # ตรวจสอบ advanced features  
    for feature, enabled in self.advanced_features.items():
        if not enabled:
            disabled.append(feature)
            
    return disabled
```

## 🎯 Feature Definitions

### 🔧 Basic Features Explained

#### 1. **OCR Translation** (`ocr_translation`)
- **หน้าที่:** ฟีเจอร์หลักในการแปลภาษาด้วย OCR
- **สถานะ:** เปิดเสมอ (core functionality)
- **เกี่ยวข้อง:** `screen_capture.py`, `translator_*.py`

#### 2. **Model Selection** (`model_selection`)
- **หน้าที่:** เลือก AI model (Gemini, Claude, GPT)
- **สถานะ:** เปิดเสมอ
- **เกี่ยวข้อง:** `settings.py`, `translator_factory.py`

#### 3. **Area Selection** (`area_selection`)
- **หน้าที่:** เลือกพื้นที่หน้าจอสำหรับแปล
- **สถานะ:** เปิดเสมอ  
- **เกี่ยวข้อง:** `control_ui.py`, Area A/B/C system

#### 4. **Preset System** (`preset_system`)
- **หน้าที่:** บันทึกและโหลด preset ของพื้นที่แปล
- **สถานะ:** เปิดเสมอ
- **เกี่ยวข้อง:** `settings.py` (area_presets)

#### 5. **Click Translate** (`click_translate`)
- **หน้าที่:** แปลเมื่อคลิกพื้นที่
- **สถานะ:** เปิดเสมอ
- **เกี่ยวข้อง:** `MBB.py` click detection

### ⚡ Advanced Features Explained

#### 1. **Hover Translation** (`hover_translation`)
- **หน้าที่:** แปลเมื่อ hover เมาส์บนพื้นที่
- **สถานะ:** เปิด (ทั้ง beta และ release)
- **เกี่ยวข้อง:** `hover_translation.py`

#### 2. **Smart Area Switching** (`smart_area_switching`)
- **หน้าที่:** สลับพื้นที่แปลอัตโนมัติตามบริบท
- **สถานะ:** ปิด (ยังไม่เสถียร)
- **เกี่ยวข้อง:** Future feature

#### 3. **NPC Manager** (`npc_manager`)
- **หน้าที่:** จัดการข้อมูล NPC และตัวละคร
- **สถานะ:** เปิด
- **เกี่ยวข้อง:** `npc_manager_card.py`

#### 4. **Theme Customization** (`theme_customization`)
- **หน้าที่:** ปรับแต่งธีมและสีต่างๆ
- **สถานะ:** เปิด
- **เกี่ยวข้อง:** `appearance.py`, `theme_system_guide.md`

## 🔌 Integration Points

### 📡 Main App Integration
```python
# ใน MBB.py
from FeatureManager import FeatureManager

class MagicBabelApp:
    def __init__(self):
        self.feature_manager = FeatureManager("release")  # หรือ "beta"
        
    def check_feature_availability(self, feature_name):
        return self.feature_manager.is_feature_enabled(feature_name)
```

### 🎛️ UI Integration  
```python
# ตรวจสอบก่อนแสดง UI elements
if self.feature_manager.is_feature_enabled("npc_manager"):
    self.create_npc_manager_button()
    
if self.feature_manager.is_feature_enabled("hover_translation"):
    self.setup_hover_translation()
```

### ⚙️ Settings Integration
```python
# ปิดการตั้งค่าสำหรับฟีเจอร์ที่ปิดอยู่
disabled_features = self.feature_manager.get_disabled_features()
for feature in disabled_features:
    self.hide_feature_settings(feature)
```

## 🚀 Usage Examples

### 🔧 Basic Usage
```python
# สร้าง FeatureManager
feature_manager = FeatureManager("release")

# ตรวจสอบฟีเจอร์
if feature_manager.is_feature_enabled("hover_translation"):
    print("Hover translation is available!")
    enable_hover_features()
else:
    print("Hover translation is disabled")
    
# ดูฟีเจอร์ที่ปิด
disabled = feature_manager.get_disabled_features()
print(f"Disabled features: {disabled}")
```

### 🎯 Advanced Usage
```python
# Dynamic feature checking
def setup_application_features(self):
    features_to_check = [
        "ocr_translation",
        "hover_translation", 
        "npc_manager",
        "theme_customization"
    ]
    
    for feature in features_to_check:
        if self.feature_manager.is_feature_enabled(feature):
            self.enable_feature(feature)
            logging.info(f"Feature enabled: {feature}")
        else:
            self.disable_feature(feature)
            logging.info(f"Feature disabled: {feature}")

# Conditional UI creation
def create_control_ui(self):
    # พื้นฐาน - แสดงเสมอ
    self.create_basic_controls()
    
    # ขั้นสูง - ตรวจสอบก่อน
    if self.feature_manager.is_feature_enabled("npc_manager"):
        self.add_npc_manager_button()
        
    if self.feature_manager.is_feature_enabled("theme_customization"):
        self.add_theme_picker()
```

## 🎨 Feature Configuration

### 🛠️ Custom Feature Sets
```python
# สร้าง FeatureManager แบบกำหนดเอง
class CustomFeatureManager(FeatureManager):
    def __init__(self, app_version="beta"):
        super().__init__(app_version)
        
        # เพิ่มฟีเจอร์ใหม่
        self.experimental_features = {
            "ai_auto_translate": False,
            "voice_recognition": False,
            "gesture_control": False
        }
    
    def is_feature_enabled(self, feature_name):
        # ตรวจสอบ experimental features ด้วย
        if feature_name in self.experimental_features:
            return self.experimental_features[feature_name]
        return super().is_feature_enabled(feature_name)
```

### 🔧 Runtime Feature Toggle
```python
def toggle_feature(self, feature_name, enabled):
    """เปิด/ปิดฟีเจอร์ระหว่างการทำงาน"""
    if feature_name in self.basic_features:
        self.basic_features[feature_name] = enabled
        logging.info(f"Basic feature '{feature_name}' {'enabled' if enabled else 'disabled'}")
        
    elif feature_name in self.advanced_features:
        self.advanced_features[feature_name] = enabled
        logging.info(f"Advanced feature '{feature_name}' {'enabled' if enabled else 'disabled'}")
        
    else:
        logging.warning(f"Unknown feature: {feature_name}")
```

## 🐛 Error Handling

### ✅ Robust Feature Checking
```python
def is_feature_enabled(self, feature_name):
    try:
        # ตรวจสอบในฟีเจอร์พื้นฐานก่อน
        if feature_name in self.basic_features:
            return self.basic_features[feature_name]

        # ตรวจสอบในฟีเจอร์ขั้นสูง
        if feature_name in self.advanced_features:
            return self.advanced_features[feature_name]

        # ไม่พบฟีเจอร์ในรายการที่กำหนด
        logging.warning(f"FeatureManager: ไม่พบฟีเจอร์ '{feature_name}' ในรายการ")
        return False
        
    except Exception as e:
        logging.error(f"Error checking feature '{feature_name}': {e}")
        return False  # Safe default
```

### 🔍 Logging & Debugging
```python
import logging

# เพิ่ม debug logging
def __init__(self, app_version="beta"):
    logging.info(f"FeatureManager initialized with version: {app_version}")
    
    # Log enabled features
    enabled_basic = [f for f, enabled in self.basic_features.items() if enabled]
    enabled_advanced = [f for f, enabled in self.advanced_features.items() if enabled]
    
    logging.info(f"Enabled basic features: {enabled_basic}")
    logging.info(f"Enabled advanced features: {enabled_advanced}")
```

## 🔧 Best Practices

### ✅ Recommended Patterns
```python
# 1. ตรวจสอบฟีเจอร์ก่อนใช้งานเสมอ
if self.feature_manager.is_feature_enabled("npc_manager"):
    self.open_npc_manager()

# 2. ใช้ early return เพื่อ clean code
def setup_hover_translation(self):
    if not self.feature_manager.is_feature_enabled("hover_translation"):
        return
    
    # Setup hover translation logic here
    self.hover_translator = HoverTranslator()

# 3. Group feature checks
required_features = ["ocr_translation", "model_selection"]
if all(self.feature_manager.is_feature_enabled(f) for f in required_features):
    self.start_translation_service()
```

### ❌ Common Pitfalls
```python
# ❌ ไม่ตรวจสอบฟีเจอร์
def bad_example(self):
    self.npc_manager.show()  # อาจ error หากฟีเจอร์ปิด

# ✅ ตรวจสอบฟีเจอร์ก่อน
def good_example(self):
    if self.feature_manager.is_feature_enabled("npc_manager"):
        self.npc_manager.show()
    else:
        logging.info("NPC Manager feature is disabled")
```

---

## 🔗 Related Files
- [`MBB.py`](MBB.py) - Main application integration
- [`settings.py`](settings.py) - Settings system
- [`control_ui.py`](control_ui.py) - UI feature controls
- [`version_manager.py`](version_manager.py) - Version management

## 📚 See Also
- [Version Manager Guide](version_manager_guide.md)
- [Settings System Guide](settings_system_guide.md)
- [Main Application Guide](main_application_guide.md)