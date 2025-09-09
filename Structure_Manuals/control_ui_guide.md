# 🎛️ Control UI Module Guide

**ไฟล์:** `control_ui.py`  
**คลาสหลัก:** `Control_UI`  

## 🎯 Overview
Control UI เป็นหน้าต่างควบคุมหลักของ MBB ที่ให้ผู้ใช้สามารถจัดการการแปล, สลับพื้นที่, ปรับ preset, และตั้งค่าต่างๆ ได้อย่างสะดวก พร้อมระบบ tooltip แบบ integrated

## 🏗️ Architecture

### 📋 Core Components

#### 1. **Main Control Panel**
```python
class Control_UI:
    def __init__(self, root, force_translate, switch_area, settings, ...):
        self.theme = {...}                    # Theme colors
        self.active_tooltips = []            # Tooltip management
        self.current_preset = 1              # Current preset number
        self.max_presets = 6                 # Maximum presets
        self.has_unsaved_changes = False     # Unsaved changes flag
```

#### 2. **Window Structure**
- **Size:** 340x260px (ขนาดที่เหมาะสมสำหรับการแสดงผลแบบกะทัดรัด)
- **Properties:** Topmost, Alpha 0.95, Override redirect  
- **Layout:** Vertical stack ของ control sections
- **Close Button:** ✕ สัญลักษณ์ปิดหน้าต่างที่มุมขวาบน (x=310, y=5)
- **Note:** ขนาด 340x260px เป็นขนาดที่ลงตัวสำหรับการแสดงผลทุกองค์ประกอบพอดี

## 🎨 Theme System

### 🎭 Color Scheme
```python
self.theme = {
    "bg": appearance_manager.bg_color,           # พื้นหลังหลัก
    "accent": appearance_manager.get_accent_color(),     # สี accent
    "accent_light": "...",                       # สี accent อ่อน
    "secondary": "...",                          # สีรอง
    "button_bg": "...",                          # พื้นหลังปุ่ม
    "text": "#ffffff",                           # สีข้อความ
    "text_dim": "#b2b2b2",                      # สีข้อความอ่อน
    "highlight": "...",                          # สี highlight
    "error": "#FF4136",                          # สีแสดงข้อผิดพลาด
    "success": "#4CAF50",                        # สีแสดงความสำเร็จ
    "button_inactive_bg": "#555555",             # ปุ่มไม่ active
    "border": "#444444"                          # สีขอบ
}
```

## 🎛️ Control Sections

### 1. **📍 Area Control Section**
```python
# Area switching และ display
- Area Display Toggle (SHOW/HIDE)
- Area Switching Buttons (A, B, C, A+B, B+C, All)
- Current area indicator
```

### 2. **🎯 Preset Management**
```python
# Preset system
- Preset selector (1-6)
- Save/Load preset buttons
- Unsaved changes indicator
- Active preset highlight
```

### 3. **⚡ Quick Actions**
```python
# Translation controls
- Force Translation button
- Manual translation trigger
- Area temporary display
```

### 4. **⚙️ Settings Toggle**
```python
# Feature toggles
- Click Translation ON/OFF switch
- Hover Translation ON/OFF switch  
- CPU Limit adjustment
```

### 5. **🔘 Close Button**
```python
# Window control
- Position: Top-right corner (x=310, y=5)
- Symbol: ✕ (Unicode U+2715)
- Colors: Gray (#808080) → White (#ffffff) on hover
- Function: Proper window closure with callback to main UI
```

## 🎯 Key Features

### 🔄 Area Management
```python
def show_area_ctrl(self):
    # แสดง overlay windows สำหรับ areas ที่เปิดใช้งาน
    # สร้าง red border overlay บนหน้าจอ
    
def hide_show_area_ctrl(self):
    # ซ่อน area overlay windows
    # เคลียร์ self.show_area_windows

def switch_area(self, area_name):
    # สลับไปยัง area ที่ระบุ
    # อัพเดต UI และ settings
    # เรียก callback ไปยัง main app
```

### 📋 Preset System
```python  
def save_preset(self, preset_number):
    # บันทึก current areas ลง preset
    # อัพเดต settings.json
    # แสดง confirmation

def load_preset(self, preset_number):
    # โหลด preset areas
    # ตรวจสอบ unsaved changes
    # อัพเดต UI display
```

### 🎛️ Toggle Switches
```python
def create_toggle_switch(self, parent, text, variable, callback):
    # สร้าง modern toggle switch
    # Animation effect เมื่อสลับ
    # Color coding (green=ON, red=OFF)
    
def toggle_click_translate(self, value):
    # เปิด/ปิด click translation
    # อัพเดต settings
    # เรียก callback
```

## 💬 Tooltip System

### 🎨 Advanced Tooltip
```python
def create_tooltip(self, widget, text_or_func, font_name=None, font_size=None):
    # สร้าง tooltip แบบ dynamic
    # รองรับ text หรือ function
    # Auto font selection (Thai/English)
    # Rounded corners effect

def _show_unified_tooltip(self, text, widget=None, font_size=10, header_color=None):
    # แสดง tooltip แบบ unified design
    # Multi-line support
    # Custom styling per line
    # Auto-positioning
```

### 🎯 Tooltip Management
```python
def hide_all_tooltips(self, force_immediate=False):
    # ซ่อน tooltip ทั้งหมด
    # Thread-safe operation
    # Prevention ของ memory leaks

self.active_tooltips = []          # เก็บ active tooltips
self.manual_force_tooltip = None   # Force button tooltip
self._hiding_tooltips = False      # Prevent recursive calls
```

## 🎨 UI Components

### 🎛️ Modern Buttons
```python
# Button styling
bg=self.theme["button_bg"]
fg=self.theme["text"] 
activebackground=self.theme["accent"]
relief="flat"
borderwidth=0
font=("FC Minimal Medium", 9)
```

### 🔄 Toggle Switches
```python
# ON State: Green background, white text
# OFF State: Red background, white text  
# Smooth transition animation
# Mouse hover effects
```

### 📊 Status Indicators
```python
# Preset status: Active/Inactive color coding
# Unsaved changes: Warning indicator
# Area display: Current area highlighting
# Connection status: Real-time updates
```

## 🔧 Key Methods

### 🏗️ Setup Methods
```python
def setup_window(self):
    # ตั้งค่าหน้าต่างหลัก
    # กำหนด geometry และ attributes
    # สร้าง main_frame

def setup_buttons(self):
    # สร้างปุ่มควบคุมทั้งหมด
    # ตั้งค่า layout และ styling
    # ผูก event handlers

def setup_bindings(self):
    # ผูก keyboard shortcuts
    # Mouse event bindings
    # Window event handlers
```

### 🎯 Control Methods
```python
def force_translate_action(self):
    # เรียก force translation
    # แสดง feedback tooltip
    # Handle exceptions

def toggle_show_area_ctrl(self):
    # Toggle area display overlay
    # อัพเดต button state
    # Manage overlay windows
```

## 🎨 Styling Features

### 🌈 Dynamic Theming
- ดึงสีจาก `appearance_manager`
- รองรับ light/dark theme
- Real-time theme updates
- Consistent color scheme

### 🎭 Visual Effects
- Rounded corner buttons
- Smooth hover transitions  
- Alpha transparency (0.95)
- Modern flat design

### 🔤 Typography
- **Header:** "FC Minimal Medium" 11pt bold
- **Buttons:** "FC Minimal Medium" 9pt
- **Tooltips:** Auto-selection Thai/English fonts
- **Status:** Color-coded text

## 🔗 Integration Points & Coordination Patterns

### 📡 MBB-Control UI Bidirectional Communication

#### **Control UI → MBB.py Callbacks**
```python
# Core callback functions ที่ส่งจาก Control UI ไป MBB.py
self.force_translate              # → MBB.force_translate()
self.switch_area_callback         # → MBB.switch_area(area_name)
self.toggle_click_callback        # → MBB.set_click_translate_mode(value)
self.toggle_hover_callback        # → MBB.toggle_hover_translation(value)
self.parent_callback              # → MBB.update_cpu_limit(new_limit)
self.trigger_temporary_area_display_callback  # → MBB.trigger_temporary_area_display()
```

#### **MBB.py → Control UI State Sync**
```python
# MBB.py เรียก Control UI เพื่อ sync state
self.control_ui.update_button_highlights()           # อัพเดต area button highlights
self.control_ui.select_preset_in_control_ui(preset_num)  # เลือก preset
self.control_ui.refresh_area_overlay_display()       # รีเฟรช area overlays
self.control_ui.current_preset = self.current_preset # Sync preset number
self.control_ui.has_unsaved_changes = False          # Clear unsaved flag
```

### ⚙️ Deep Settings Coordination

#### **Settings Read Patterns**
```python
# Control UI อ่านค่าจาก Settings ตอน initialization
self.current_preset = self.settings.get("current_preset", 1)
self.cpu_limit = self.settings.get("cpu_limit", 80)
self.click_translate_var.set(settings.get("enable_click_translate", False))
self.hover_translation_var.set(settings.get("enable_hover_translation", False))

# Dynamic reading สำหรับ preset และ area data
preset_data = self.settings.get_preset(preset_number)
area_coords = self.settings.get_translate_area(area_name)
current_area_string = self.settings.get("current_area", "A")
```

#### **Settings Write & Propagation Flow**
```python
# 1. Control UI แก้ไข settings
self.settings.set("current_preset", preset_number)
self.settings.set("enable_click_translate", value)
self.settings.save_settings()

# 2. Notify MBB.py ผ่าน callback
callback_result = self.toggle_click_callback(value)

# 3. MBB.py ประยุกต์การเปลี่ยนแปลงกับ system
# 4. MBB.py sync กลับมาที่ Control UI (ถ้าจำเป็น)
```

#### **Preset Management Coordination**
```python
def save_preset(self, preset_number):
    """บันทึก preset with full coordination"""
    # 1. รวบรวมข้อมูล current areas จาก settings
    current_areas = {
        "A": self.settings.get_translate_area("A"),
        "B": self.settings.get_translate_area("B"), 
        "C": self.settings.get_translate_area("C")
    }
    
    # 2. บันทึกลง settings
    self.settings.save_preset(preset_number, self.current_area, current_areas)
    
    # 3. อัพเดต MBB.py state ผ่าน parent_app
    if self.parent_app:
        self.parent_app.current_preset = preset_number
        self.parent_app.settings.set("current_preset", preset_number)
    
    # 4. อัพเดต Control UI visual state
    self.has_unsaved_changes = False
    self.update_preset_display()

def load_preset(self, preset_number):
    """โหลด preset with bidirectional sync"""
    # 1. โหลดจาก settings
    preset_data = self.settings.get_preset(preset_number)
    
    # 2. ประยุกต์ไปที่ translation areas
    for area_name, coordinates in preset_data.get("areas", {}).items():
        self.settings.set_translate_area(area_name, coordinates)
    
    # 3. Sync กับ MBB.py
    if self.parent_app:
        self.parent_app.load_preset(preset_number)  # ให้ MBB จัดการ coordination
    
    # 4. อัพเดต Control UI
    self.current_preset = preset_number
    self.update_ui_after_preset_load()
```

## 🚀 Performance Features

### ⚡ Optimization
- **Tooltip Management:** Prevent memory leaks
- **Event Throttling:** Smooth UI updates
- **Lazy Loading:** Create widgets on demand
- **Thread Safety:** Proper locking mechanisms

### 🧵 Threading Considerations
- UI updates ใน main thread เท่านั้น
- Background operations ใน separate threads
- Thread-safe tooltip management
- Proper cleanup on window close

## 📱 Responsive Behavior

### 🖱️ Mouse Interactions
- **Hover Effects:** Color changes, tooltips
- **Click Feedback:** Visual confirmation
- **Drag Support:** Window repositioning
- **Context Menus:** Right-click options

### ⌨️ Keyboard Support
- **Shortcuts:** Function key bindings
- **Focus Management:** Tab navigation
- **Accessibility:** Screen reader support

## 🐛 Error Handling

### ✅ Robust Error Management
```python
try:
    # Critical operations
except Exception as e:
    logging.error(f"Control_UI error: {e}")
    # Graceful fallback
```

### 🔍 Debugging Features
- Comprehensive logging
- State validation
- Error reporting
- Debug mode support

## 📝 Usage Examples

### 🚀 Basic Initialization
```python
control_ui = Control_UI(
    root=control_window,
    force_translate=app.force_translate,
    switch_area=app.switch_area,
    settings=app.settings,
    parent_app=app,
    toggle_click_callback=app.toggle_click_translate,
    toggle_hover_callback=app.toggle_hover_translate
)
```

### 🎛️ Preset Management
```python
# Save current configuration to preset 3
control_ui.save_preset(3)

# Load preset 2
control_ui.load_preset(2)

# Check for unsaved changes
if control_ui.has_unsaved_changes:
    # Show confirmation dialog
```

### 🎯 Area Control
```python
# Switch to area combination A+B  
control_ui.switch_area("A+B")

# Show area overlays
control_ui.show_area_ctrl()

# Hide area overlays
control_ui.hide_show_area_ctrl()
```

## 🔧 Customization

### 🎨 Theme Customization
```python
# Override theme colors
control_ui.theme["accent"] = "#FF6B6B"
control_ui.theme["button_bg"] = "#4ECDC4"

# Apply changes
control_ui.apply_theme_updates()
```

### 🎛️ Custom Controls
```python
# Add custom toggle switch
custom_var = tk.BooleanVar()
control_ui.create_toggle_switch(
    parent=control_ui.main_frame,
    text="Custom Feature",
    variable=custom_var,
    callback=custom_callback
)
```

---

## 🔗 Related Files
- [`settings.py`](settings.py) - Settings management
- [`appearance.py`](appearance.py) - Theme system  
- [`MBB.py`](MBB.py) - Main application
- [`translated_ui.py`](translated_ui.py) - Translation display

## 📚 See Also
- [Settings System Guide](settings_system_guide.md)
- [Translated UI Guide](translated_ui_guide.md)
- [Theme System Guide](theme_system_guide.md)
- [NPC Manager Guide](npc_manager_guide.md)