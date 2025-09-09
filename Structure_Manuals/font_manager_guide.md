# 🔤 Font Manager Complete Guide

**MBB v9.1** - ระบบจัดการฟอนต์บน TUI และ LOG แบบครบครัน  
**อัพเดตล่าสุด:** 26 กรกฎาคม 2025 - Font Manager v2.0 Complete Overhaul

---

## 🎯 Overview
Font Manager เป็นระบบจัดการฟอนต์ที่ผ่านการ redesign ครั้งใหญ่ เพื่อให้ผู้ใช้สามารถปรับแต่งฟอนต์สำหรับ **TUI (Translated UI)** และ **LOG (Translated Logs)** ได้อย่างมีประสิทธิภาพ

### ✨ Key Features
- **🎨 Modern Flat Design** - UI สะอาด เรียบหรู ไม่ฉูดฉาด
- **🎯 Target Selection** - เลือกปลายทางการ apply (TUI หรือ LOG) ได้แยกกัน
- **📱 Responsive UI** - ขนาด 880x620px พร้อม resize functionality
- **🖱️ Enhanced UX** - พื้นที่คลิกและลาก UI ที่กว้างขวาง
- **💾 Settings Integration** - บันทึกและโหลดการตั้งค่า target mode อัตโนมัติ

---

## 🏗️ Architecture Overview

### 📦 Core Components
```python
# ไฟล์หลัก
font_manager.py
├── FontManager        # Core font management logic
├── FontUI            # UI components and interactions  
└── FontSettings      # Settings integration

# เชื่อมต่อกับ
├── settings.py       # การตั้งค่าหลัก
├── mbb.py           # MBB Core coordination
└── control_ui.py    # เรียกใช้จาก Control UI
```

### 🔄 Data Flow
```
Control UI → Open Font Manager → FontUI → FontManager → Settings
     ↓                                        ↓
User Interaction → Target Selection → Apply → Callback → Settings Update
```

---

## 🎨 User Interface Design

### 🖼️ UI Layout (880x620px)
```
┌─────────────────────────────────────────────────────────────┐
│ 📋 จัดการฟอนต์บน TUI และ LOG                      [✕]     │
├─────────────────────────────────────────────────────────────┤
│ [เพิ่มฟอนต์] [ขนาด: - 20 +]                    [Apply]   │
├─────────────────────────────────────────────────────────────┤
│ 🎯 เลือกปลายทางสำหรับการ Apply ฟอนต์:                    │
│ ┌────────────────────┐  ┌─────────────────────────────────┐ │
│ │ 🖥️ หน้าต่างแปลหลัก   │  │ 📄 หน้าต่างประวัติการแปล        │ │
│ │ (TUI)              │  │ (LOG)                         │ │
│ │ ○ Selected/● Not   │  │ ○ Selected/● Not              │ │
│ └────────────────────┘  └─────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ รายการฟอนต์  │ │ตัวอย่างฟอนต์                               │
│ ┌─────────────┐ │ ┌─────────────────────────────────────────┐ │
│ │ Anuphan     │ │ │ ทดสอบภาษาไทย Aa Bb 123              │ │
│ │ Arial       │ │ │ ขนาด: 20px                            │ │
│ │ Bai Jamjuree│ │ │                                       │ │
│ │ ...         │ │ │                                       │ │
│ └─────────────┘ │ └─────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 🎨 Color Scheme (Muted Tones)
```python
# พื้นหลังหลัก
background = "#2e2e2e"      # Dark grey

# Target Selection
selected_bg = "#4a5a4a"     # Muted green for selected
unselected_bg = "#1a1a1a"   # Black for unselected
selected_text = "#c4a777"   # Muted gold
unselected_text = "#505050" # Dark grey
indicator_selected = "#c4a777"  # Gold dot
indicator_unselected = "#000000" # Black dot

# Buttons
button_bg = "#5a5a5a"       # Muted grey
button_hover = "#6a6a6a"    # Slightly lighter
apply_button = "#c4a777"    # Muted gold
```

---

## 🔧 Technical Implementation

### 🎯 Target Selection System
```python
class FontUI:
    def __init__(self):
        self.target_mode = tk.StringVar()
        # โหลดจาก settings หรือใช้ default
        saved_target = settings.get("font_target_mode", "translated_ui")
        self.target_mode.set(saved_target)
    
    def _update_target_colors(self):
        """อัพเดตสีตาม selection"""
        selected = self.target_mode.get()
        
        if selected == "translated_ui":
            # TUI = Active, LOG = Inactive
            self.translated_ui_rb.config(
                fg="#c4a777", selectcolor="#c4a777", bg="#4a5a4a"
            )
            self.translated_logs_rb.config(
                fg="#505050", selectcolor="#000000", bg="#1a1a1a"  
            )
        else:
            # LOG = Active, TUI = Inactive
            # ...opposite colors
```

### 🖱️ Enhanced User Experience
```python
def create_target_selection(self):
    """สร้าง target selection ที่คลิกได้ทั้งพื้นที่"""
    
    # Main UI Frame - clickable area
    ui_option_frame = tk.Frame(
        options_frame, 
        bg="#2a3a2a", 
        relief="solid", 
        bd=1, 
        cursor="hand2"  # แสดง hand cursor
    )
    
    # Icon + RadioButton
    ui_icon_label = tk.Label(ui_option_frame, text="🖥️", cursor="hand2")
    self.translated_ui_rb = tk.Radiobutton(...)
    
    # Make entire frame clickable
    def ui_frame_click(event):
        self.target_mode.set("translated_ui")
        self._update_target_colors()
    
    ui_option_frame.bind("<Button-1>", ui_frame_click)
    ui_icon_label.bind("<Button-1>", ui_frame_click)
```

### 📱 Drag & Drop Enhancement
```python
def setup_drag_areas(self):
    """เพิ่มพื้นที่สำหรับลาก UI"""
    
    def bind_drag_to_widget(widget):
        try:
            widget.bind("<Button-1>", self._start_move)
            widget.bind("<B1-Motion>", self._on_motion)
        except:
            pass
    
    # Bind to multiple areas for better UX
    drag_widgets = [
        header_frame, header_label, main_frame,
        top_controls_frame, left_controls, buttons_frame,
        font_size_frame, right_controls, apply_frame
    ]
    
    for widget in drag_widgets:
        bind_drag_to_widget(widget)
```

---

## ⚙️ Settings Integration

### 💾 Settings Storage
```python
# settings.json เก็บค่า
{
    "font": "IBM Plex Sans Thai Medium",
    "font_size": 20,
    "font_target_mode": "translated_ui"  # ใหม่!
}
```

### 🔄 Callback System
```python
def apply_font(self):
    """Apply ฟอนต์พร้อม save settings"""
    try:
        target_value = self.target_mode.get()
        
        # บันทึกลง settings
        if self.settings:
            self.settings.set("font", selected_font)
            self.settings.set("font_size", selected_size)
            self.settings.set("font_target_mode", target_value)  # เพิ่ม!
        
        # เรียก callback ไปยัง MBB
        if self.apply_callback:
            self.apply_callback({
                "font": selected_font,
                "font_size": selected_size,
                "target": target_value  # ส่ง target ไปด้วย
            })
            
        logging.info(f"Font applied: {selected_font} -> {target_value}")
        
    except Exception as e:
        logging.error(f"Apply font error: {e}")
```

---

## 🚀 Integration with MBB Core

### 🔗 MBB Coordination
```python
# mbb.py
def init_font_manager(self):
    """เตรียม Font Manager"""
    try:
        from font_manager import FontManager, FontUI
        
        self.font_manager = FontManager(
            settings=self.settings,
            logging_manager=self.logging_manager
        )
        
        # เชื่อมต่อกับ Control UI
        if self.control_ui:
            self.control_ui.font_manager = self.font_manager
            
    except Exception as e:
        self.logging_manager.log_error(f"Font Manager init error: {e}")

def handle_font_change(self, font_data):
    """จัดการเมื่อมีการเปลี่ยนฟอนต์"""
    try:
        target = font_data.get("target", "translated_ui")
        font_name = font_data.get("font")
        font_size = font_data.get("font_size")
        
        if target == "translated_ui":
            # อัพเดต TUI
            if self.translated_ui:
                self.translated_ui.update_font(font_name, font_size)
                
        elif target == "translated_logs":
            # อัพเดต LOG
            if hasattr(self, 'translated_logs') and self.translated_logs:
                self.translated_logs.update_font(font_name, font_size)
        
        self.logging_manager.log_info(
            f"Font updated: {font_name} ({font_size}px) -> {target}"
        )
        
    except Exception as e:
        self.logging_manager.log_error(f"Handle font change error: {e}")
```

### 🎛️ Control UI Integration
```python
# control_ui.py
def open_font_manager(self):
    """เปิด Font Manager จาก Control UI"""
    try:
        if not hasattr(self, 'font_ui') or not self.font_ui:
            from font_manager import FontUI
            
            self.font_ui = FontUI(
                parent=self.root,
                font_manager=self.font_manager,
                settings=self.settings,
                apply_callback=self.mbb_app.handle_font_change  # callback!
            )
        
        self.font_ui.open_font_ui()
        
    except Exception as e:
        logging.error(f"Open font manager error: {e}")
```

---

## 🎨 UI Component Details

### 🎯 Target Selection Component
```python
def create_enhanced_target_selection(self):
    """สร้าง target selection แบบ professional"""
    
    # Section container
    target_section = tk.Frame(
        main_frame, 
        bg="#1a1a1a",     # Dark background
        relief="solid", 
        bd=1
    )
    target_section.pack(fill=tk.X, pady=(4, 10), padx=4)
    
    # Header with separator
    target_header = tk.Label(
        target_section,
        text="🎯 เลือกปลายทางสำหรับการ Apply ฟอนต์",
        font=("IBM Plex Sans Thai Medium", 11, "bold"),
        bg="#1a1a1a", 
        fg="#f0f0f0"
    )
    target_header.pack(fill=tk.X, padx=6, pady=(6, 2))
    
    # Separator line
    separator = tk.Frame(target_section, bg="#4a4a4a", height=1)
    separator.pack(fill=tk.X, padx=8, pady=(2, 8))
    
    # Options in horizontal layout
    options_frame = tk.Frame(target_section, bg="#1a1a1a")
    options_frame.pack(fill=tk.X, padx=16, pady=(0, 12))
    
    # TUI Option
    self._create_target_option(
        options_frame, 
        "translated_ui",
        "🖥️", 
        "หน้าต่างแปลหลัก (TUI)",
        "#2a3a2a"  # Green tint
    )
    
    # LOG Option  
    self._create_target_option(
        options_frame,
        "translated_logs", 
        "📄",
        "หน้าต่างประวัติการแปล (LOG)",
        "#3a2a2a"  # Red tint
    )
```

### 🔄 Resize Handle System
```python
def create_resize_functionality(self):
    """สร้างระบบ resize ที่ซ่อนแต่ใช้งานได้"""
    
    # Resize handle between panels (hidden)
    resize_handle = tk.Frame(
        fonts_frame, 
        bg="#3a3a3a",  # Same as background - invisible
        width=4, 
        cursor="sb_h_double_arrow"
    )
    resize_handle.pack(side=tk.LEFT, fill=tk.Y, padx=1)
    
    # Bind resize events
    resize_handle.bind("<Button-1>", self._start_resize_panels)
    resize_handle.bind("<B1-Motion>", self._on_resize_panels)
    resize_handle.bind("<ButtonRelease-1>", self._end_resize_panels)
    
    # Bottom-right resize area (completely invisible)
    resize_area = tk.Frame(
        main_frame,
        bg="#2e2e2e",  # Match background exactly
        cursor="bottom_right_corner",
        width=15, height=15,
        bd=0, relief="flat", highlightthickness=0
    )
    resize_area.place(relx=1.0, rely=1.0, anchor="se", x=-2, y=-2)
```

---

## 🔍 Error Handling & Logging

### 🛡️ Exception Management
```python
def safe_font_operation(func):
    """Decorator สำหรับ safe font operations"""
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            logging.error(f"Font operation error in {func.__name__}: {e}")
            self.show_temporary_notification(
                f"❌ เกิดข้อผิดพลาด: {e}", 
                color="#d32f2f"
            )
            return False
    return wrapper

@safe_font_operation
def apply_font(self):
    # Implementation with automatic error handling
    pass
```

### 📊 Logging System
```python
def setup_logging(self):
    """ตั้งค่า logging สำหรับ Font Manager"""
    
    logging.info("Font Manager v2.0 initialized")
    logging.info(f"Available fonts: {len(self.get_available_fonts())}")
    logging.info(f"Target mode: {self.target_mode.get()}")
    
def log_font_change(self, font_name, font_size, target):
    """Log การเปลี่ยนฟอนต์"""
    logging.info(f"Font applied: {font_name} ({font_size}px) -> {target}")
    
    # เก็บ statistics
    if not hasattr(self, 'font_change_count'):
        self.font_change_count = 0
    self.font_change_count += 1
```

---

## 🚀 Performance Optimizations

### ⚡ UI Responsiveness
```python
def optimize_ui_performance(self):
    """เพิ่มประสิทธิภาพ UI"""
    
    # Lazy loading for font preview
    def lazy_update_preview():
        if hasattr(self, '_preview_timer'):
            self.font_window.after_cancel(self._preview_timer)
        self._preview_timer = self.font_window.after(300, self._do_update_preview)
    
    # Debounce font size changes
    self.font_size.trace_add("write", lambda *args: lazy_update_preview())
    
    # Efficient canvas updates
    def batch_canvas_updates(self):
        """รวม canvas updates เพื่อลด flickering"""
        if not hasattr(self, '_canvas_update_pending'):
            self._canvas_update_pending = True
            self.font_window.after_idle(self._flush_canvas_updates)
```

### 💾 Memory Management
```python
def cleanup_resources(self):
    """ทำความสะอาด resources เมื่อปิด UI"""
    try:
        # Cancel pending timers
        if hasattr(self, '_preview_timer'):
            self.font_window.after_cancel(self._preview_timer)
        if hasattr(self, 'notification_timer'):
            self.font_window.after_cancel(self.notification_timer)
        
        # Clear references
        self.font_manager = None
        self.apply_callback = None
        
        logging.info("Font Manager resources cleaned up")
        
    except Exception as e:
        logging.error(f"Cleanup error: {e}")
```

---

## 📋 Usage Examples

### 💻 Basic Usage
```python
# เปิด Font Manager จาก Control UI
def open_font_manager_example():
    font_ui = FontUI(
        parent=root,
        font_manager=font_manager,
        settings=settings,
        apply_callback=handle_font_change
    )
    font_ui.open_font_ui()

# Callback สำหรับรับการเปลี่ยนฟอนต์
def handle_font_change(font_data):
    font_name = font_data["font"]
    font_size = font_data["font_size"] 
    target = font_data["target"]
    
    print(f"Font changed: {font_name} ({font_size}px) -> {target}")
    
    # อัพเดต UI ตาม target
    if target == "translated_ui":
        update_tui_font(font_name, font_size)
    elif target == "translated_logs":
        update_logs_font(font_name, font_size)
```

### 🎨 Advanced Customization
```python
# Custom color scheme
def apply_custom_theme():
    custom_colors = {
        "background": "#1e1e1e",
        "selected_bg": "#3a4a5a", 
        "selected_text": "#ffd700",
        "unselected_bg": "#0a0a0a",
        "unselected_text": "#404040"
    }
    
    font_ui.apply_color_scheme(custom_colors)

# Custom font validation
def custom_font_validator(font_name):
    """ตรวจสอบฟอนต์ก่อน apply"""
    if not font_name:
        return False, "กรุณาเลือกฟอนต์"
    
    if len(font_name) > 50:
        return False, "ชื่อฟอนต์ยาวเกินไป"
        
    return True, "OK"

font_ui.set_font_validator(custom_font_validator)
```

---

## 🔧 Troubleshooting

### ❗ Common Issues

#### 1. Target Selection ไม่แสดงครบ
```python
# สาเหตุ: Frame packing ผิด
# แก้ไข:
logs_option_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
# ไม่ใช่:
logs_option_frame.pack(anchor=tk.W)  # ผิด!
```

#### 2. สีปุ่มไม่เปลี่ยนตาม selection  
```python
# สาเหตุ: ไม่ได้เรียก _update_target_colors()
# แก้ไข:
def ui_frame_click(event):
    self.target_mode.set("translated_ui")
    self._update_target_colors()  # จำเป็น!
```

#### 3. UI ลากไม่ได้
```python
# สาเหตุ: พื้นที่ bind น้อยเกินไป
# แก้ไข: เพิ่ม binding ใน multiple widgets
for widget in [header_frame, main_frame, top_controls_frame]:
    widget.bind("<Button-1>", self._start_move)
    widget.bind("<B1-Motion>", self._on_motion)
```

### 🔧 Debug Tools
```python
def debug_font_manager(self):
    """Debug information สำหรับ Font Manager"""
    print("=== Font Manager Debug Info ===")
    print(f"Target mode: {self.target_mode.get()}")
    print(f"Selected font: {self.selected_font.get()}")
    print(f"Font size: {self.font_size.get()}")
    print(f"Available fonts: {len(self.font_manager.get_available_fonts())}")
    print(f"Settings: {self.settings.get_all() if self.settings else 'None'}")
```

---

## 📊 Change Log

### v2.0 (26/07/2025) - Complete Overhaul
- ✅ **Modern Flat Design** - เปลี่ยนจาก bright colors เป็น muted tones
- ✅ **Enhanced Target Selection** - แยกเป็น section โดดเด่น พร้อม icons
- ✅ **Full Clickable Areas** - คลิกได้จากทั้งพื้นที่ของปุ่ม
- ✅ **Improved UX** - พื้นที่ลาก UI ที่กว้างขวาง
- ✅ **Settings Integration** - บันทึก/โหลด target mode อัตโนมัติ
- ✅ **Remove Font Removal** - ยกเลิกฟีเจอร์ลบฟอนต์ตามคำขอ
- ✅ **Hidden Resize Areas** - ทำให้ resize areas ล่องหนแต่ยังใช้งานได้
- ✅ **Color Consistency** - แก้ไขสีปุ่มปรับขนาดให้เป็น muted tone

### v1.x (เก่า)
- Basic font selection และ apply functionality
- Simple UI design with bright colors  
- Limited target selection options

---

## 🎯 Future Enhancements

### 🚀 Planned Features
- **Font Preview Enhanced** - แสดงตัวอย่างแบบ real-time
- **Font Categories** - จัดหมวดหมู่ฟอนต์ (Thai, English, Monospace)
- **Font Favorites** - เก็บฟอนต์ที่ชื่นชอบ
- **Export/Import Settings** - นำเข้า/ส่งออกการตั้งค่าฟอนต์
- **Font Validation** - ตรวจสอบฟอนต์ก่อน apply
- **Keyboard Shortcuts** - shortcut keys สำหรับการเปลี่ยนฟอนต์เร็ว

---

**📝 หมายเหตุ:** คู่มือนี้อัพเดตตาม Font Manager v2.0 ที่ผ่านการ overhaul ครั้งใหญ่ หากพบปัญหาหรือต้องการเพิ่มเติมฟีเจอร์ กรุณาแจ้งผ่าน MBB development team

**🔗 Related Guides:** 
- [MBB Core Guide](mbb_v9_guide.md)
- [Settings System Guide](settings_system_guide.md)  
- [Control UI Guide](control_ui_guide.md)