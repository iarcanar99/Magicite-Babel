# 📱 Translated UI Module Guide

**ไฟล์:** `translated_ui.py`  
**คลาสหลัก:** `Translated_UI`  

## 🎯 Overview
Translated UI เป็นหน้าต่างแสดงผลการแปลหลักของ MBB ที่รับผิดชอบการแสดงข้อความที่แปลแล้ว พร้อมฟีเจอร์ต่างๆ เช่น Lock UI, Fade out, Typing animation และการควบคุมการแปล

## 🏗️ Architecture

### 📋 Core Classes

#### 1. `UIState` (Dataclass)
จัดการสถานะต่างๆ ของ UI
```python
@dataclass
class UIState:
    is_locked: bool = False          # สถานะล็อค UI
    is_typing: bool = False          # แอนิเมชันพิมพ์
    blinking: bool = False           # กะพริบข้อความ
    arrow_visible: bool = False      # แสดงลูกศร
    buttons_visible: bool = True     # แสดงปุ่มควบคุม
    fade_timer_id: Optional[str] = None     # Timer สำหรับ fade out
    is_fading: bool = False          # สถานะกำลัง fade out
    fadeout_enabled: bool = True     # เปิด/ปิด fade out
```

#### 2. `UIComponents`
เก็บอ้างอิงไปยัง UI components ต่างๆ
```python
class UIComponents:
    main_frame: tk.Frame             # กรอบหลัก
    canvas: tk.Canvas                # Canvas สำหรับข้อความ
    control_area: tk.Frame           # พื้นที่ปุ่มควบคุม
    buttons: Dict[str, tk.Button]    # ปุ่มต่างๆ
    scrollbar: ttk.Scrollbar         # แถบเลื่อน
```

#### 3. `ShadowConfig`
การจัดการพารามิเตอร์เงาแบบรวมศูนย์
```python
class ShadowConfig:
    # *** SHADOW PARAMETERS - CONTROL CENTER ***
    SHADOW_BLUR_RADIUS = 8      # Blur radius สำหรับเงา
    SHADOW_SPREAD = 6           # Spread ของเงา (stroke width)
    SHADOW_OFFSET_X = 2         # การเลื่อนเงาแนวขวาง
    SHADOW_OFFSET_Y = 2         # การเลื่อนเงาแนวตั้ง
    SHADOW_COLOR = "#000000"    # สีเงา
    BASE_FONT_SIZE = 24         # ขนาดฟอนต์อ้างอิง
```

#### 4. `BlurShadowEngine`
ระบบสร้างเงาแบบ blur ด้วย PIL ImageFilter
```python
class BlurShadowEngine:
    """Advanced blur shadow system using PIL ImageFilter"""
    
    def __init__(self):
        self.shadow_cache = {}  # Cache สำหรับ shadow textures
        self.max_cache_size = 50  # จำกัดขนาด cache
    
    def create_shadow_on_canvas(self, canvas, text, x, y, font, text_color):
        """สร้างเงา blur บน canvas"""
        # ใช้เทคนิค "Blur on Solid Shape"
        # 1. สร้าง solid shape ขนาดใหญ่
        # 2. Apply Gaussian blur
        # 3. วางเงาก่อน จากนั้นวางข้อความ
```

#### 5. `Translated_UI` (Main Class)
คลาสหลักที่รับผิดชอบทุกอย่าง

## 🎨 UI Features

### 🔒 Lock System
- **Lock Mode 0:** ปกติ - แสดงปุ่มควบคุมทั้งหมด
- **Lock Mode 1:** ล็อคบางส่วน - ซ่อนปุ่มบางตัว, Alpha ปิดใช้งาน
- **Lock Mode 2:** ล็อคเต็ม - ซ่อนปุ่มทั้งหมด

### 🎭 Visual Effects
- **Rounded Corners:** `ROUNDED_CORNER_RADIUS = 15px`
- **Fade Out:** อัตโนมัติหลังไม่มีการใช้งาน
- **Typing Animation:** แสดงข้อความทีละตัวอักษร
- **Alpha Transparency:** ปรับความโปร่งใสพื้นหลัง

### 🌟 Advanced Shadow System (New!)
- **Blur Shadow Rendering:** เทคนิค "Blur on Solid Shape" แทน 8-point offset
- **Intelligent Scaling:** เงาปรับขนาดอัตโนมัติตามฟอนต์
- **Centralized Configuration:** จัดการพารามิเตอร์เงาจากจุดเดียว
- **Performance Caching:** 50-item cache สำหรับ shadow textures
- **Professional Quality:** เงาคุณภาพระดับมืออาชีพ

### 🎯 Hover Translation
- **Force Hover:** กดค้างเมาส์บนปุ่ม Force เพื่อแปลอัตโนมัติ
- **Delay Timer:** ป้องกันการเรียกใช้งานมากเกินไป

## 🎛️ Control Buttons

### 📍 ตำแหน่งปุ่ม (จากซ้ายไปขวา):
1. **🔒 Lock** - ล็อค/ปลดล็อค UI
2. **⚡ Force** - บังคับแปลทันที
3. **🎯 Area** - สลับพื้นที่แปล
4. **⚙️ Settings** - เปิดหน้าตั้งค่า
5. **👥 NPC** - เปิด NPC Manager
6. **🎨 Theme** - เปิด Color Picker

### 🎨 Color Picker System
```python
class ImprovedColorAlphaPickerWindow:
    # Color picker แบบ modal พร้อม alpha control
    # บันทึกการเปลี่ยนแปลงทันที
    # ปิดเมื่อคลิกข้างนอก
```

## 🔧 Key Methods

### 🏗️ Initialization
```python
def __init__(self, root, toggle_translation, stop_translation, 
             force_translate, settings, ...):
    # รับ callback functions จาก main app
    # ตั้งค่า UI state และ components
    # โหลดไอคอนและสร้าง UI
```

### 🎨 UI Setup
```python
def setup_ui(self):
    # สร้างหน้าต่างหลักแบบ topmost
    # ตั้งค่า canvas สำหรับแสดงข้อความ
    # สร้างปุ่มควบคุมและ scrollbar
    # เริ่มต้น BlurShadowEngine สำหรับระบบเงา
```

### 📝 Text Display
```python
def update_text(self, new_text, npc_name=None):
    # อัพเดตข้อความในหน้าต่าง
    # จัดการ typing animation
    # ตรวจสอบ NPC name และ fade out
```

### 🎭 Animation System
```python
def start_typing_animation(self, text):
    # แสดงข้อความทีละตัวอักษร
    # คำนวณความเร็วตามความยาวข้อความ
    # จัดการ blinking effect
```

## 🌟 Shadow System Configuration

### 🎨 Shadow Parameters
```python
# จาก ShadowConfig class - ศูนย์กลางการควบคุมเงา
SHADOW_BLUR_RADIUS = 8      # รัศมี blur (ความนุ่มนวลของเงา)
SHADOW_SPREAD = 6           # ความหนาของเงา
SHADOW_OFFSET_X = 2         # การเลื่อนเงาแนวขวาง
SHADOW_OFFSET_Y = 2         # การเลื่อนเงาแนวตั้ง
SHADOW_COLOR = "#000000"    # สีเงา (ดำ)
BASE_FONT_SIZE = 24         # ขนาดฟอนต์อ้างอิงสำหรับการปรับขนาด
```

### 🔧 Intelligent Scaling Algorithm
```python
def calculate_smart_spread(self, font_size):
    """คำนวณขนาดเงาที่เหมาะสมตามฟอนต์"""
    # ใช้ square root scaling เพื่อรักษาความสมดุลทางสายตา
    scale_factor = math.sqrt(font_size / self.BASE_FONT_SIZE)
    return {
        'blur_radius': self.SHADOW_BLUR_RADIUS * scale_factor,
        'spread': self.SHADOW_SPREAD * scale_factor,
        'offset_x': self.SHADOW_OFFSET_X * scale_factor,
        'offset_y': self.SHADOW_OFFSET_Y * scale_factor
    }
```

### 🎯 Shadow Cache System
- **Cache Size:** 50 items สูงสุด
- **Cache Key:** text + font size + parameters hash
- **LRU Cleanup:** ลบรายการเก่าสุดเมื่อเต็ม
- **Performance:** ลดการคำนวณซ้ำได้ 80-90%

## ⚙️ Settings Integration

### 🔧 Settings ที่เกี่ยวข้อง:
```json
{
    "bg_alpha": 1.0,              // ความโปร่งใสพื้นหลัง
    "fadeout_delay": 10,          // วินาทีก่อน fade out
    "typing_speed": 50,           // ความเร็วพิมพ์ (ms)
    "theme_bg_color": "#2D2D2D",  // สีพื้นหลัง
    "theme_text_color": "#FFFFFF" // สีข้อความ
}
```

### 🎨 Theme System
- รองรับ Dark/Light theme
- ปรับสีอัตโนมัติตาม appearance_manager
- บันทึกการตั้งค่าทันที

## 🔄 Event Handling

### 🖱️ Mouse Events
- **Click:** การคลิกปุ่มต่างๆ
- **Hover:** Force translation hover
- **Drag:** ลากย้ายหน้าต่าง

### ⌨️ Keyboard Events
- **ESC:** ปิดหน้าต่าง
- **Hotkeys:** ควบคุมผ่าน keyboard shortcuts

## 🚀 Performance Features

### ⚡ Optimization
- **Throttling:** จำกัดการ resize (16ms)
- **Lazy Loading:** โหลดไอคอนตามต้องการ
- **Memory Management:** เคลียร์ timer อัตโนมัติ

### 🧵 Threading
- การแปลทำงานใน background thread
- UI update ใน main thread เท่านั้น
- ป้องกัน UI freeze

## 📱 Responsive Design

### 📏 Size Management
- Auto-resize ตามเนื้อหา
- Minimum/Maximum size constraints
- Scrollbar แบบ custom

### 🎯 Position Handling
- จำตำแหน่งหน้าต่าง
- ป้องกันการหลุดออกจากหน้าจอ
- Multi-monitor support

## 🔍 Debugging Features

### 📊 Logging
```python
logging.info("TranslatedUI initialized successfully")
logging.error(f"Error in _trigger_delayed_hover_force: {e}")
```

### 🐛 Error Handling
- Try-catch ครอบคลุม
- Graceful degradation
- User feedback เมื่อเกิดข้อผิดพลาด

## 🔗 Integration Points

### 📡 Main App Callbacks
- `toggle_translation()` - เปิด/ปิดการแปล
- `force_translate()` - บังคับแปลทันที
- `switch_area()` - สลับพื้นที่แปล
- `toggle_npc_manager_callback()` - เปิด NPC Manager

### 🎨 External Dependencies
- `appearance_manager` - จัดการธีม
- `FontObserver` - ตรวจสอบการเปลี่ยนฟอนต์
- `Settings` - การจัดการค่าตั้ง

## 📝 Usage Examples

### 🚀 Basic Usage
```python
translated_ui = Translated_UI(
    root=root,
    toggle_translation=app.toggle_translation,
    force_translate=app.force_translate,
    settings=app.settings,
    # ... other callbacks
)

# อัพเดตข้อความ
translated_ui.update_text("สวัสดีครับ", "นักรบแสง")

# เปลี่ยนธีม
translated_ui.apply_theme_colors()
```

## 🔧 Customization

### 🎨 VO Styling
```python
# เปลี่ยนรัศมีขอบโค้ง
ROUNDED_CORNER_RADIUS = 20  # เปลี่ยนที่นี่ที่เดียว

# ปรับ scrollbar
scrollbar_default_width = 6  # ความกว้าง default
scrollbar_hover_width = 12   # ความกว้างเมื่อ hover
```

---

## 🔗 Related Files
- [`settings.py`](settings.py) - การจัดการ settings
- [`appearance.py`](appearance.py) - ระบบธีม
- [`font_manager.py`](font_manager.py) - จัดการฟอนต์
- [`MBB.py`](MBB.py) - Main application

## 📚 See Also
- [Settings System Guide](settings_guide.md)
- [Control UI Guide](control_ui_guide.md)
- [Theme System Guide](theme_system_guide.md)