# ⚙️ Settings System Guide

**ไฟล์หลัก:** `settings.py`, `settings.json`  
**คลาสหลัก:** `Settings`, `SettingsUI`  

## 🎯 Overview
Settings System เป็นระบบจัดการการตั้งค่าของ MBB ทั้งหมด ครอบคลุมการบันทึก/โหลดค่าจาก JSON, UI สำหรับแก้ไข, และการ validation ค่าต่างๆ

## 🏗️ Architecture

### 📋 Core Classes

#### 1. `Settings` (Main Configuration Manager)
จัดการข้อมูลการตั้งค่าทั้งหมด
```python
class Settings:
    VALID_MODELS = {...}        # โมเดล AI ที่รองรับ
    DEFAULT_API_PARAMETERS = {...}   # ค่า default API
    
    def __init__(self):
        self.default_settings = {...}  # ค่า default ทั้งหมด
        self.settings = {}             # ค่าปัจจุบัน
```

#### 2. `SettingsUI` (Settings Interface)
หน้าต่างการตั้งค่าแบบ GUI
```python
class SettingsUI:
    def __init__(self, parent, settings, callbacks...):
        self.theme = SettingsUITheme   # ธีมสำหรับ UI
        self.advance_ui = None         # Advanced settings
        self.hotkey_ui = None         # Hotkey configuration
        self.font_ui = None           # Font management
```

## 📁 Settings Structure

### 🔧 Main Categories

#### 1. **API Parameters**
```json
{
  "api_parameters": {
    "model": "gemini-2.0-flash",
    "max_tokens": 500,
    "temperature": 0.8,
    "top_p": 0.9
  }
}
```

#### 2. **OCR Settings**
```json
{
  "ocr_settings": {
    "languages": ["en", "ja"],
    "confidence_threshold": 0.65,
    "image_preprocessing": {
      "resize_factor": 2.0,
      "contrast": 1.5,
      "sharpness": 1.3
    }
  }
}
```

#### 3. **Translation Areas**
```json
{
  "translate_areas": {
    "A": {"start_x": 0, "start_y": 0, "end_x": 0, "end_y": 0},
    "B": {"start_x": 0, "start_y": 0, "end_x": 0, "end_y": 0},
    "C": {"start_x": 0, "start_y": 0, "end_x": 0, "end_y": 0}
  },
  "current_area": "A+B",
  "current_preset": 1
}
```

#### 4. **UI Appearance**
```json
{
  "font": "IBM Plex Sans Thai Medium.ttf",
  "font_size": 24,
  "line_spacing": -50,
  "width": 960,
  "height": 240,
  "bg_color": "#2D2D2D",
  "bg_alpha": 1.0
}
```

#### 5. **Shortcuts & Hotkeys**
```json
{
  "shortcuts": {
    "toggle_ui": "alt+l",
    "start_stop_translate": "f9",
    "force_translate": "r-click",
    "force_translate_key": "f10"
  }
}
```

#### 6. **Splash Screen System** 🎬
```json
{
  "splash_screen_type": "video"  // "video" | "image" | "off"
}
```

**ประเภท Splash Screen:**
- **`"video"`** - แสดงวิดีโอ `MBB_splash_vid.mp4` เป็นเวลา 5 วินาที
- **`"image"`** - แสดงรูปภาพ `MBB_splash.png` เป็นเวลา 3 วินาที  
- **`"off"`** - ปิดการแสดง splash screen

**🛠️ Thread Fix Implementation (01/08/2025):**
- **Delayed Initialization**: รอ 3 วินาทีหลังจาก heavy resources โหลดเสร็จก่อนแสดง splash
- **Single Thread**: ใช้ timer-based updates แทน multi-threading เพื่อหลีกเลี่ยง thread conflict
- **Resource Contention Fix**: แก้ปัญหาวิดีโอแสดงแค่ 1 วินาทีเนื่องจาก resource contention ระหว่าง startup

**การตั้งค่าผลกระทบต่อ:**
- **Application Startup**: การเปลี่ยน splash type ไม่ส่งผลต่อ startup performance
- **Memory Usage**: Video splash ใช้ memory เพิ่มระหว่างการแสดงผล
- **Thread Safety**: ระบบใหม่ป้องกัน UI thread conflicts อย่างสมบูรณ์

## 🎛️ Supported AI Models

### 🤖 Valid Models
```python
VALID_MODELS = {
    "gemini-2.0-flash-lite": {
        "display_name": "gemini-2.0-flash-lite",
        "type": "gemini"
    },
    "gemini-2.0-flash": {
        "display_name": "gemini-2.0-flash", 
        "type": "gemini"
    },
    "gemini-2.5-flash": {
        "display_name": "gemini-2.5-flash",
        "type": "gemini"
    }
}
```

## 🔧 Key Methods

### 📁 File Management
```python
def load_settings(self):
    # โหลดจาก settings.json
    # ตรวจสอบและเติมค่า default ที่ขาดหาย
    
def save_settings(self):
    # บันทึกลง settings.json
    # Backup ก่อนบันทึก
    
def ensure_default_values(self):
    # ตรวจสอบและเติมค่า default
    # จัดการ presets structure
```

### ✅ Validation
```python
def validate_model_parameters(self, params):
    # ตรวจสอบความถูกต้องของ API parameters
    
def validate_display_scale(self, scale):
    # ตรวจสอบ display scale (0.5-3.0)
    
def is_valid_hotkey(hotkey):
    # ตรวจสอบ hotkey format
    # รองรับ modifiers: ctrl, alt, shift
    # รองรับ keys: a-z, 0-9, f1-f12
```

### 🎨 Theme Integration
```python
def get_theme_color(self, color_key):
    # ดึงสีจาก SettingsUITheme
    # Fallback ไป appearance_manager
    
def get_theme_font(self, size="normal", weight="normal"):
    # ดึงฟอนต์ตาม theme
    # รองรับขนาด: small, normal, medium, large, title
```

## 📱 Settings UI Components

### 🏗️ Main Window Structure
```python
def create_settings_window(self):
    # สร้างหน้าต่างหลัก (600x700px)
    # ตั้งค่า topmost และ resizable
    # ใช้ SettingsUITheme สำหรับสี/ฟอนต์
```

### 🎛️ UI Tabs
1. **General Tab** - ตั้งค่าทั่วไป
2. **Advanced Tab** - ตั้งค่าขั้นสูง (AdvanceUI)
3. **Hotkeys Tab** - จัดการ hotkeys (SimplifiedHotkeyUI)
4. **Fonts Tab** - จัดการฟอนต์ (FontUI)

### 🎨 Modern UI Components
```python
# ใช้ utils_appearance สำหรับ modern UI
ModernButton()    # ปุ่มแบบ modern
ModernEntry()     # ช่องกรอกข้อมูล
ModernFrame()     # กรอบแบบ modern
```

## 🔄 Preset System

### 📋 Area Presets Structure
```python
{
  "area_presets": [
    {
      "name": "Preset 1",
      "areas": {
        "A": {"start_x": 100, "start_y": 200, ...},
        "B": {"start_x": 300, "start_y": 400, ...},
        "C": {"start_x": 500, "start_y": 600, ...}
      }
    }
  ]
}
```

### 🎯 Preset Management
- สูงสุด 6 presets
- แต่ละ preset มี 3 areas (A, B, C)
- Auto-generate ชื่อ preset หากไม่ระบุ
- ตรวจสอบ manual selection time

## 🎨 Theme System Integration

### 🎭 Theme Colors
```python
SettingsUITheme = {
    "bg_primary": "#1E1E1E",     # พื้นหลังหลัก
    "bg_secondary": "#2D2D2D",   # พื้นหลังรอง
    "text_primary": "#FFFFFF",   # ข้อความหลัก
    "text_secondary": "#AAAAAA", # ข้อความรอง
    "success": "#4CAF50",        # สีเขียว (สำเร็จ)
    "error": "#FF5252",          # สีแดง (ผิดพลาด)
    "border_normal": "#555555",  # ขอบปกติ
    "border_focus": "#6D6D6D"    # ขอบเมื่อ focus
}
```

### 🖋️ Theme Fonts
```python
"fonts": {
    "small": ("Bai Jamjuree Light", 8),
    "normal": ("Bai Jamjuree Light", 13),
    "medium": ("Bai Jamjuree Light", 13),
    "large": ("Bai Jamjuree Light", 17),
    "title": ("Nasalization Rg", 14)
}
```

## 🔗 Integration Points

### 📡 Main App Callbacks
```python
def __init__(self, ..., callbacks):
    self.apply_settings_callback     # ประยุกต์ใช้การตั้งค่า
    self.update_hotkeys_callback     # อัพเดต hotkeys
    self.toggle_click_callback       # เปิด/ปิด click translate
    self.toggle_hover_callback       # เปิด/ปิด hover translate
```

### 🎛️ Sub-UI Integration
- **AdvanceUI:** ตั้งค่าขั้นสูง
- **SimplifiedHotkeyUI:** จัดการ hotkeys
- **FontUI:** จัดการฟอนต์
- **FontUIManager:** ประสานงานฟอนต์

## 🚀 Performance Features

### ⚡ Optimization
- **Lazy Initialization:** สร้าง sub-UI เมื่อต้องการ
- **Settings Validation:** ตรวจสอบความถูกต้องก่อนบันทึก
- **Backup System:** สำรองก่อนแก้ไข settings.json

### 🔄 Auto-Sync
- การเปลี่ยนแปลงใน UI sync กับ settings ทันที
- Font changes propagate ไปยัง FontObserver
- Theme changes ส่งผลต่อ appearance_manager

## 📝 Default Values

### 🎯 Core Defaults
```python
{
    "font_size": 24,
    "width": 960,
    "height": 240,
    "enable_force_translate": True,
    "enable_auto_hide": True,
    "splash_screen_type": "video",
    "current_area": "A+B",
    "current_preset": 1,
    "use_gpu_for_ocr": False,
    "cpu_limit": 80
}
```

## 🐛 Error Handling

### ✅ Validation Rules
- **Hotkey Format:** `modifier+key` (เช่น `ctrl+f1`)
- **Display Scale:** 0.5 - 3.0
- **Font Size:** 8 - 72px
- **CPU Limit:** 1 - 100%

### 🔧 Recovery Mechanisms
- **Missing Settings:** เติมค่า default อัตโนมัติ
- **Invalid Values:** ใช้ค่า fallback
- **Corrupted JSON:** สร้างไฟล์ใหม่

## 📚 Usage Examples

### 🚀 Basic Usage
```python
# สร้าง Settings object
settings = Settings()

# โหลดการตั้งค่า
settings.load_settings()

# เข้าถึงค่า
font_size = settings.get("font_size", 24)
current_model = settings.get("api_parameters", {}).get("model")

# แก้ไขค่า
settings.set("font_size", 28)
settings.save_settings()
```

### 🎛️ Settings UI
```python
# สร้าง Settings UI
settings_ui = SettingsUI(
    parent=root,
    settings=settings,
    apply_settings_callback=app.apply_settings,
    update_hotkeys_callback=app.update_hotkeys,
    main_app=app
)

# แสดง Settings window
settings_ui.show_settings()
```

## 🔧 Customization

### 🎨 Custom Theme
```python
# แก้ไขสีธีม
SettingsUITheme["bg_primary"] = "#1A1A1A"
SettingsUITheme["text_primary"] = "#F0F0F0"

# เพิ่มฟอนต์ใหม่
SettingsUITheme["fonts"]["xl"] = ("CustomFont", 20)
```

### ⚙️ Custom Validation
```python
def custom_validate_setting(self, key, value):
    if key == "custom_setting":
        return 0 <= value <= 100
    return True
```

---

## 🔗 Related Files
- [`settings.json`](settings.json) - ไฟล์ข้อมูลการตั้งค่า
- [`utils_appearance.py`](utils_appearance.py) - Modern UI components
- [`advance_ui.py`](advance_ui.py) - Advanced settings UI
- [`simplified_hotkey_ui.py`](simplified_hotkey_ui.py) - Hotkey configuration
- [`font_manager.py`](font_manager.py) - Font management system

## 📚 See Also
- [Advanced UI Guide](advance_ui_guide.md)
- [Font Manager Guide](font_manager_guide.md)
- [Theme System Guide](theme_system_guide.md)
- [Translated UI Guide](translated_ui_guide.md)