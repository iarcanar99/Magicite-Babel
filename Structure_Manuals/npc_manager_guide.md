# 👥 NPC Manager Module Guide

**ไฟล์:** `npc_manager_card.py`  
**คลาสหลัก:** `NPCManagerCard`, `CardView`  

## 🎯 Overview
NPC Manager เป็นระบบจัดการข้อมูล NPC (Non-Player Character) ในเกม ที่ให้ผู้ใช้สามารถเพิ่ม, แก้ไข, ลบ, และค้นหาข้อมูล NPC ได้แบบ real-time พร้อมระบบ Card View ที่สวยงาม

## 🏗️ Architecture

### 📋 Core Classes

#### 1. `NPCManagerCard` (Main Manager)
```python
class NPCManagerCard:
    def __init__(self, parent, reload_callback=None, logging_manager=None, ...):
        self.current_game_info = {...}    # ข้อมูลเกมปัจจุบัน
        self.data = {}                    # ข้อมูล NPC ทั้งหมด
        self.saved_state = {...}          # สถานะที่บันทึกไว้
        self.font_size = 19               # ขนาดฟอนต์ (ลดเป็น 80%)
```

#### 2. `CardView` (Individual Card UI)
```python
class CardView:
    def __init__(self, parent, data, section_type, font_config, ...):
        self.card_frame = tk.Frame(...)   # กรอบการ์ด
        self.data = data                  # ข้อมูล NPC
        self.detail_mode = False          # โหมดแสดงรายละเอียด
```

## 🎮 Game Integration

### 🎯 Game Detection
```python
# อ่านข้อมูลเกมจาก npc.json
self.current_game_info = get_game_info_from_npc_file()

# Structure ของ game info
{
    "name": "Final Fantasy XIV",
    "code": "ffxiv", 
    "description": "MMORPG with rich NPC interactions"
}
```

### 🔄 Game Swapping
```python
# Optional module integration
try:
    from optional_module.swap_data import MainWindow as SwapDataWindow
    HAS_SWAP_DATA = True
except ImportError:
    HAS_SWAP_DATA = False

# Callback เมื่อเปลี่ยนเกม
self.on_game_swapped_callback = on_game_swapped_callback
```

## 🎨 UI Structure

### 📱 Window Configuration
```python
# ขนาดหน้าต่าง (ลดเป็น 80% จากเดิม)
default_width = 880    # จาก 1100
default_height = 772   # จาก 840
minimum_size = (456, 416)  # ขนาดต่ำสุด

# Properties
- Topmost: True (ปักหมุด)
- Resizable: True
- Center positioned: True
```

### 🎭 Theme & Styling
```python
# Font Configuration (ลดขนาด 80%)
self.font = "Bai Jamjuree Light"
self.font_size = 19              # หลัก
self.font_size_large_bold = 17   # หัวข้อใหญ่
self.font_size_medium_bold = 14  # หัวข้อกลาง
self.font_size_medium = 13       # ข้อความปกติ
self.font_size_small = 12        # ข้อความเล็ก
self.font_size_xsmall = 10       # ข้อความเล็กมาก

# Color Scheme
card_bg = "#252525"              # พื้นหลังการ์ด
border_color = "#2D2D2D"         # สีขอบ
highlight_color = "#3D3D3D"      # สี highlight
text_color = "#FFFFFF"           # สีข้อความ
```

## 🃏 Card System

### 🎨 Card View Features
```python
class CardView:
    # Card Layout
    - Header: NPC name และ navigation
    - Content: ข้อมูลหลักของ NPC
    - Actions: ปุ่ม Edit, Delete, Copy
    - Hover Effects: เปลี่ยนสีเมื่อ hover
```

### 📋 Card Data Structure
```python
{
    "name": "Alphinaud",
    "role": "Archon",
    "description": "Member of the Scions of the Seventh Dawn",
    "location": "Mor Dhona",
    "notes": "Twin brother of Alisaie",
    "tags": ["scion", "archon", "story"]
}
```

### 🎛️ Card Interactions
```python
def _handle_card_click(self, event, data):
    # คลิกเพื่อดูรายละเอียด
    # เปิด detail view

def _on_edit_click(self, event=None):
    # แก้ไขข้อมูล NPC
    # เปิด edit dialog

def _on_delete_click(self):
    # ลบ NPC (พร้อม confirmation)
    # อัพเดต UI
```

## 🔍 Search & Filter System

### 🎯 Real-time Search
```python
# Search Cache System
self._search_cache = {}          # แคช search results
self._search_delay = None        # Debounce timer
self._lazy_load_complete = False # Lazy loading status

# Search Implementation
def perform_search(self, search_term):
    # ค้นหาใน name, role, description, notes, tags
    # แสดงผลแบบ real-time
    # เก็บผลลัพธ์ในแคช
```

### 📊 Filter Categories
- **By Role:** ตำแหน่งหน้าที่ของ NPC
- **By Location:** สถานที่ที่พบ NPC
- **By Tags:** แท็กที่กำหนดไว้
- **By Game:** เกมที่ NPC อยู่

## 💾 Data Management

### 📁 File Handling
```python
# NPC Data Files
- npc.json           # ข้อมูล NPC หลัก
- npc_ffxiv.json     # Final Fantasy XIV NPCs
- npc_wuwa.json      # Wuthering Waves NPCs
- npc_persona.json   # Persona series NPCs
- npc_monhun.json    # Monster Hunter NPCs

# File Operations
def load_data(self):
    # โหลดข้อมูลจากไฟล์ JSON
    # ตรวจสอบความถูกต้อง
    # เก็บใน data cache

def save_data(self):
    # บันทึกข้อมูลลง JSON
    # สร้าง backup ก่อนบันทึก
    # ตรวจสอบ write permission
```

### 🔄 State Preservation
```python
self.saved_state = {
    "search_term": "",           # คำค้นหาล่าสุด
    "current_section": None,     # section ที่เลือก
    "scroll_position": 0,        # ตำแหน่ง scroll
    "window_geometry": None      # ขนาด/ตำแหน่งหน้าต่าง
}
```

## 🎛️ Key Features

### ➕ Add/Edit NPC
```python
def add_new_npc(self):
    # เปิด dialog สำหรับเพิ่ม NPC ใหม่
    # Validate input data
    # เพิ่มลงใน data structure
    # อัพเดต UI

def edit_npc(self, npc_data):
    # เปิด dialog สำหรับแก้ไข
    # Pre-fill ข้อมูลเดิม
    # บันทึกการเปลี่ยนแปลง
    # Refresh card display
```

### 🗑️ Delete NPC
```python
def delete_npc(self, npc_id):
    # แสดง confirmation dialog
    # ลบออกจาก data structure
    # อัพเดต JSON file
    # Refresh UI display
```

### 📋 Copy Function
```python
def copy_npc_name(self, name):
    # คัดลอกชื่อ NPC ไปยัง clipboard
    # แสดง feedback tooltip
    # ใช้สำหรับ quick reference
```

## 🎨 Advanced UI Features

### 🎭 Detail View Mode
```python
def show_detail_view(self, npc_data):
    # แสดงรายละเอียดแบบเต็ม
    # Expandable sections
    # Rich text formatting
    # Image support (ถ้ามี)
```

### 🔄 Navigation System
```python
def navigate_to_role(self, role_name):
    # กรอง NPC ตาม role
    # เลื่อนไปยังตำแหน่งที่ต้องการ
    # Highlight matching cards
```

### 📌 Pin/Topmost Toggle
```python
def toggle_topmost(self):
    # เปลี่ยนสถานะ always on top
    # อัพเดต icon และ tooltip
    # บันทึกสถานะ
```

## 🔌 Integration Points

### 📡 Main App Callbacks
```python
self.reload_callback              # รีโหลดข้อมูล
self.stop_translation_callback    # หยุดการแปลเมื่อเปิด NPC Manager
self.on_game_swapped_callback     # เปลี่ยนเกม
self.on_close_callback           # ปิด NPC Manager
```

### 🎮 Optional Module Integration
```python
# Swap Data Module (ถ้ามี)
if HAS_SWAP_DATA and HAS_PYQT5:
    # เปิด QT window สำหรับ swap data
    # ประสานงานกับ PyQt5 application
```

## 🚀 Performance Features

### ⚡ Optimization
```python
# Lazy Loading
self._lazy_load_complete = False  # โหลดข้อมูลตามต้องการ

# Search Debouncing  
self._search_delay = None         # หลีกเลี่ยงการค้นหาซ้ำ

# Data Caching
self.data_cache = {}              # แคชข้อมูลที่ใช้บ่อย
self._search_cache = {}           # แคช search results
```

### 🧵 Memory Management
```python
# Timer Management
self._all_timers = []             # ติดตาม timer ทั้งหมด
self._active_bindings = []        # ติดตาม event bindings
self._is_destroyed = False        # ป้องกัน memory leaks

def cleanup(self):
    # ยกเลิก timers ทั้งหมด
    # ลบ event bindings
    # เคลียร์ references
```

## 🐛 Error Handling

### ✅ Robust Error Management
```python
# File Operations
try:
    with open(npc_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
except FileNotFoundError:
    # สร้างไฟล์ใหม่พร้อมโครงสร้างพื้นฐาน
except json.JSONDecodeError:
    # แสดงข้อผิดพลาดและใช้ backup
except Exception as e:
    # Log error และแสดง user-friendly message
```

### 🔍 Logging Integration
```python
# ใช้ LoggingManager หรือ fallback
try:
    from loggings import LoggingManager
except ImportError:
    # Mock LoggingManager class
    class LoggingManager:
        def log_info(self, message): print(f"INFO: {message}")
        def log_error(self, message): print(f"ERROR: {message}")
```

## 📝 Usage Examples

### 🚀 Basic Initialization
```python
npc_manager = NPCManagerCard(
    parent=root,
    reload_callback=app.reload_npc_data,
    logging_manager=app.logging_manager,
    stop_translation_callback=app.stop_translation,
    on_game_swapped_callback=app.on_game_changed
)

# แสดง NPC Manager
npc_manager.show_window()
```

### 🃏 Card Operations
```python
# เพิ่ม NPC ใหม่
new_npc = {
    "name": "Tataru Taru",
    "role": "Secretary", 
    "description": "Lalafell secretary of the Scions",
    "location": "Rising Stones"
}
npc_manager.add_npc(new_npc)

# ค้นหา NPC
npc_manager.search_npcs("Tataru")

# แก้ไข NPC
npc_manager.edit_npc("Tataru Taru", updated_data)
```

## 🔧 Customization

### 🎨 UI Customization
```python
# เปลี่ยนขนาดฟอนต์
npc_manager.font_size = 22
npc_manager.update_font_sizes()

# เปลี่ยนสีธีม
npc_manager.update_theme_colors({
    "card_bg": "#1E1E1E",
    "text_color": "#E0E0E0"
})
```

### 📊 Data Structure Customization
```python
# เพิ่ม field ใหม่
custom_fields = ["affinity", "faction", "quest_giver"]
npc_manager.add_custom_fields(custom_fields)

# Custom validators
def validate_npc_data(data):
    required_fields = ["name", "role"]
    return all(field in data for field in required_fields)
```

---

## 🔗 Related Files
- [`npc_file_utils.py`](npc_file_utils.py) - NPC file operations
- [`npc.json`](npc.json) - Main NPC data file
- [`optional_module/`](optional_module/) - Swap data functionality
- [`loggings.py`](loggings.py) - Logging system

## 📚 See Also
- [Settings System Guide](settings_system_guide.md)
- [Control UI Guide](control_ui_guide.md) 
- [Translated UI Guide](translated_ui_guide.md)
- [Optional Module Guide](optional_module_guide.md)