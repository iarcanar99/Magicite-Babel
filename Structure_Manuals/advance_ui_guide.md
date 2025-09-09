# ⚙️ Advance UI Complete Guide

**MBB v9.1** - Screen & Performance Settings Management  
**อัพเดตล่าสุด:** 26 กรกฎาคม 2025 - Advance UI ที่รับผิดชอบ CPU Management

---

## 🎯 Overview
Advance UI เป็นหน้าต่างจัดการการตั้งค่าขั้นสูงสำหรับ **Screen Resolution**, **CPU Performance**, และ **OCR Performance** ที่ย้ายมาจาก Control UI เพื่อให้การจัดการเป็นระบบมากขึ้น

### ✨ Key Features
- **📺 Screen Resolution Management** - จัดการความละเอียดหน้าจอและ display scale
- **⚡ CPU Performance Control** - ควบคุม CPU usage limit (50%, 60%, 80%)
- **🎮 GPU OCR Toggle** - เปิด/ปิดการใช้ GPU สำหรับ OCR processing
- **🎨 Modern UI Design** - ใช้ SettingsUITheme สำหรับ consistent design
- **💾 Real-time Validation** - ตรวจสอบความถูกต้องของการตั้งค่าแบบ real-time

---

## 🏗️ Architecture Overview

### 📦 Core Components
```python
# ไฟล์หลัก
advance_ui.py
├── AdvanceUI           # Main UI class
├── Screen Section      # Resolution & scale management
├── CPU Section         # Performance limit control
└── GPU Section         # OCR performance settings

# เชื่อมต่อกับ
├── mbb.py             # MBB Core coordination
├── control_ui.py      # เรียกใช้จาก Control UI
├── settings.py        # การตั้งค่าหลัก
└── utils_appearance.py # UI theme และ components
```

### 🔄 Data Flow
```
Control UI → Open Advance UI → AdvanceUI → Settings Update
     ↓                              ↓
User Changes Settings → Validation → apply_settings_callback → MBB.py
```

---

## 🎨 User Interface Design

### 🖼️ UI Layout (400x500px)
```
┌─────────────────────────────────────────────┐
│ Screen & Advance                       [✕] │
├─────────────────────────────────────────────┤
│                                             │
│ 📺 Screen Resolution                       │
│ ┌─────────────────────────────────────────┐ │
│ │ Width: [2560] Height: [1440]            │ │
│ │ Scale: [100%] ▼                         │ │
│ │ [Check Resolution] [Auto Detect]        │ │
│ └─────────────────────────────────────────┘ │
│                                             │
│ 🎮 OCR Performance                         │
│ ┌─────────────────────────────────────────┐ │
│ │ ☑ Use GPU for OCR Processing            │ │
│ └─────────────────────────────────────────┘ │
│                                             │
│ ⚡ CPU Performance                          │
│ ┌─────────────────────────────────────────┐ │
│ │ CPU Usage Limit: [50%] [60%] [80%]      │ │
│ └─────────────────────────────────────────┘ │
│                                             │
│                          [Save] [Cancel]   │
└─────────────────────────────────────────────┘
```

### 🎨 Color Scheme & Theme
```python
# ใช้ SettingsUITheme จาก utils_appearance.py
colors = {
    "bg_primary": "#2e2e2e",      # Main background
    "bg_secondary": "#3a3a3a",    # Section backgrounds
    "text_primary": "#e0e0e0",    # Main text
    "active_bg": "#4a6a4a",       # Selected CPU button
    "active_text": "#ffffff",     # Selected text
    "accent": "#c4a777"           # Gold accent (Save button)
}
```

---

## 🔧 Technical Implementation

### 🏗️ Core Class Structure
```python
class AdvanceUI:
    def __init__(self, parent, settings, apply_settings_callback, ocr_toggle_callback=None):
        """
        Args:
            parent: Parent window (Control UI)
            settings: Settings manager instance
            apply_settings_callback: Callback ไปยัง MBB.py
            ocr_toggle_callback: Callback สำหรับ GPU OCR toggle
        """
        self.parent = parent
        self.settings = settings
        self.apply_settings_callback = apply_settings_callback
        self.ocr_toggle_callback = ocr_toggle_callback
        self.advance_window = None
        self.is_changed = False
        
        # CPU limit variable
        self.cpu_limit_var = tk.IntVar(value=settings.get("cpu_limit", 80))
        
        # Theme initialization
        self.theme = SettingsUITheme
        
        # Create window immediately
        self.create_advance_window()
```

### 📺 Screen Resolution Section
```python
def create_screen_section(self, parent):
    """สร้างส่วน Screen Resolution Management"""
    section_frame = tk.LabelFrame(
        parent,
        text="Screen Resolution",
        bg=self.theme.get_color("bg_secondary"),
        fg=self.theme.get_color("text_primary"),
        font=self.theme.get_font("medium", "bold")
    )
    section_frame.pack(fill="x", pady=(0, 12))
    
    # Width & Height inputs
    resolution_frame = tk.Frame(section_frame, bg=self.theme.get_color("bg_secondary"))
    resolution_frame.pack(fill="x", padx=10, pady=5)
    
    # Width input
    tk.Label(resolution_frame, text="Width:", **label_style).pack(side="left")
    self.screen_width_var = tk.StringVar(value=str(self.settings.get("screen_width", 2560)))
    width_entry = ModernEntry.create(resolution_frame, textvariable=self.screen_width_var)
    width_entry.pack(side="left", padx=5)
    width_entry.bind("<KeyRelease>", self.on_change)
    
    # Height input  
    tk.Label(resolution_frame, text="Height:", **label_style).pack(side="left", padx=(10,0))
    self.screen_height_var = tk.StringVar(value=str(self.settings.get("screen_height", 1440)))
    height_entry = ModernEntry.create(resolution_frame, textvariable=self.screen_height_var)
    height_entry.pack(side="left", padx=5)
    height_entry.bind("<KeyRelease>", self.on_change)
    
    # Scale dropdown
    scale_frame = tk.Frame(section_frame, bg=self.theme.get_color("bg_secondary"))
    scale_frame.pack(fill="x", padx=10, pady=5)
    
    tk.Label(scale_frame, text="Scale:", **label_style).pack(side="left")
    self.scale_var = tk.StringVar(value=f"{int(self.settings.get('display_scale', 1.0) * 100)}%")
    scale_combo = ttk.Combobox(
        scale_frame,
        textvariable=self.scale_var,
        values=["100%", "125%", "150%", "175%", "200%"],
        width=8,
        state="readonly"
    )
    scale_combo.pack(side="right", padx=5)
    scale_combo.bind("<<ComboboxSelected>>", self.on_change)
    
    # Action buttons
    button_frame = tk.Frame(section_frame, bg=self.theme.get_color("bg_secondary"))
    button_frame.pack(fill="x", padx=10, pady=10)
    
    check_btn = ModernButton.create(
        button_frame,
        text="Check Resolution",
        command=self.check_current_resolution
    )
    check_btn.pack(side="left", padx=2)
    
    auto_detect_btn = ModernButton.create(
        button_frame,
        text="Auto Detect", 
        command=self.auto_detect_resolution
    )
    auto_detect_btn.pack(side="left", padx=2)
```

### ⚡ CPU Performance Section
```python
def create_cpu_section(self, parent):
    """สร้างส่วนตั้งค่า CPU Performance"""
    section_frame = tk.LabelFrame(
        parent,
        text="CPU Performance",
        bg=self.theme.get_color("bg_secondary"),
        fg=self.theme.get_color("text_primary"),
        font=self.theme.get_font("medium", "bold"),
        bd=1,
        relief="solid"
    )
    section_frame.pack(fill="x", pady=(0, 12))
    
    cpu_frame = tk.Frame(section_frame, bg=self.theme.get_color("bg_secondary"))
    cpu_frame.pack(fill="x", padx=10, pady=10)
    
    tk.Label(
        cpu_frame,
        text="CPU Usage Limit:",
        bg=self.theme.get_color("bg_secondary"),
        fg=self.theme.get_color("text_primary"),
        font=self.theme.get_font("normal")
    ).pack(side="left")
    
    # CPU limit buttons
    buttons_container = tk.Frame(cpu_frame, bg=self.theme.get_color("bg_secondary"))
    buttons_container.pack(side="right")
    
    # 50% Button
    self.cpu_50_btn = ModernButton.create(
        buttons_container,
        text="50%",
        command=lambda: self.set_cpu_limit(50),
        width=6
    )
    self.cpu_50_btn.pack(side="left", padx=2)
    
    # 60% Button
    self.cpu_60_btn = ModernButton.create(
        buttons_container,
        text="60%",
        command=lambda: self.set_cpu_limit(60),
        width=6
    )
    self.cpu_60_btn.pack(side="left", padx=2)
    
    # 80% Button
    self.cpu_80_btn = ModernButton.create(
        buttons_container,
        text="80%",
        command=lambda: self.set_cpu_limit(80),
        width=6
    )
    self.cpu_80_btn.pack(side="left", padx=2)
    
    # Initialize button states
    self.update_cpu_buttons(self.cpu_limit_var.get())

def set_cpu_limit(self, limit):
    """อัพเดทค่าใน UI และตั้งค่าสถานะว่ามีการเปลี่ยนแปลง"""
    if self.cpu_limit_var.get() != limit:
        self.cpu_limit_var.set(limit)
        self.update_cpu_buttons(limit)
        self.on_change()  # เรียกเพื่อให้ปุ่ม Save ทำงาน

def update_cpu_buttons(self, active_limit):
    """อัพเดตสถานะปุ่ม CPU limit ให้ไฮไลท์ปุ่มที่ถูกเลือก"""
    btn_map = {
        50: self.cpu_50_btn,
        60: self.cpu_60_btn,
        80: self.cpu_80_btn
    }
    
    active_bg = self.theme.get_color("active_bg")
    inactive_bg = self.theme.get_color("bg_secondary")
    active_fg = self.theme.get_color("active_text")
    inactive_fg = self.theme.get_color("text_primary")
    
    for value, btn in btn_map.items():
        if btn and btn.winfo_exists():
            if value == active_limit:
                btn.config(bg=active_bg, fg=active_fg)
            else:
                btn.config(bg=inactive_bg, fg=inactive_fg)
```

### 🎮 GPU OCR Section
```python
def create_gpu_section(self, parent):
    """สร้างส่วน GPU Settings"""
    section_frame = tk.LabelFrame(
        parent,
        text="OCR Performance",
        bg=self.theme.get_color("bg_secondary"),
        fg=self.theme.get_color("text_primary"),
        font=self.theme.get_font("medium", "bold"),
        bd=1,
        relief="solid"
    )
    section_frame.pack(fill="x", pady=(0, 12))
    
    gpu_frame = tk.Frame(section_frame, bg=self.theme.get_color("bg_secondary"))
    gpu_frame.pack(fill="x", padx=10, pady=10)
    
    # GPU checkbox
    self.gpu_var = tk.BooleanVar(value=self.settings.get("use_gpu_for_ocr", False))
    gpu_checkbox = tk.Checkbutton(
        gpu_frame,
        text="Use GPU for OCR Processing",
        variable=self.gpu_var,
        bg=self.theme.get_color("bg_secondary"),
        fg=self.theme.get_color("text_primary"),
        font=self.theme.get_font("normal"),
        selectcolor=self.theme.get_color("active_bg"),
        activebackground=self.theme.get_color("bg_secondary"),
        command=self.on_gpu_toggle
    )
    gpu_checkbox.pack(anchor="w")

def on_gpu_toggle(self):
    """จัดการเมื่อมีการ toggle GPU OCR"""
    if self.ocr_toggle_callback:
        self.ocr_toggle_callback(self.gpu_var.get())
    self.on_change()
```

---

## 🔍 Advanced Features

### 🖥️ Screen Resolution Detection
```python
def get_true_screen_info(self):
    """ดึงข้อมูลความละเอียดหน้าจอที่แท้จริงและค่า scale ที่ถูกต้อง"""
    try:
        # Method 1: ลองใช้ Win32API
        import win32api
        import win32con
        
        # Get device context
        hdc = win32api.GetDC(0)
        
        # Physical resolution (actual pixels)
        physical_width = win32api.GetDeviceCaps(hdc, win32con.HORZRES)
        physical_height = win32api.GetDeviceCaps(hdc, win32con.VERTRES)
        
        # Logical resolution (scaled)
        logical_width = win32api.GetDeviceCaps(hdc, win32con.DESKTOPHORZRES)  
        logical_height = win32api.GetDeviceCaps(hdc, win32con.DESKTOPVERTRES)
        
        # Calculate scale factor
        scale_factor = logical_width / physical_width
        
        win32api.ReleaseDC(0, hdc)
        
        return {
            "physical_width": logical_width,    # Use logical as "physical"
            "physical_height": logical_height,
            "scale_factor": scale_factor,
            "logical_width": physical_width,    # Swap for correct display
            "logical_height": physical_height,
            "detection_method": "Win32API"
        }
        
    except ImportError:
        # Fallback: ใช้ tkinter
        return self.get_screen_info_fallback()

def check_screen_resolution(self):
    """ตรวจสอบความละเอียดหน้าจอปัจจุบันกับการตั้งค่า"""
    try:
        screen_info = self.get_true_screen_info()
        
        current_width = screen_info["physical_width"]
        current_height = screen_info["physical_height"]  
        scale_factor = screen_info["scale_factor"]
        
        # เปรียบเทียบกับการตั้งค่า
        expected_resolution = self.settings.get("screen_size", "2560x1440")
        expected_width, expected_height = map(int, expected_resolution.split("x"))
        
        # ตรวจสอบความแตกต่าง (tolerance ±5%)
        width_tolerance = expected_width * 0.05
        height_tolerance = expected_height * 0.05
        
        if (abs(current_width - expected_width) > width_tolerance or 
            abs(current_height - expected_height) > height_tolerance):
            
            return {
                "is_valid": False,
                "message": (
                    f"ความละเอียดหน้าจอไม่ตรงกับการตั้งค่า!\n"
                    f"ปัจจุบัน: {current_width}x{current_height} (Scale: {int(scale_factor*100)}%)\n"
                    f"ที่ตั้งไว้: {expected_width}x{expected_height}\n"
                    f"กรุณาตรวจสอบการตั้งค่าความละเอียดหน้าจอ"
                ),
                "current": f"{current_width}x{current_height}",
                "expected": expected_resolution,
                "scale": scale_factor
            }
        
        return {
            "is_valid": True,
            "current": f"{current_width}x{current_height}",
            "expected": expected_resolution,
            "scale": scale_factor
        }
        
    except Exception as e:
        return {
            "is_valid": False,
            "message": f"เกิดข้อผิดพลาดในการตรวจสอบความละเอียด: {str(e)}",
            "current": "Unknown",
            "expected": "Unknown", 
            "scale": 1.0
        }

def auto_detect_resolution(self):
    """ตรวจหาความละเอียดอัตโนมัติและอัพเดต UI"""
    try:
        screen_info = self.get_true_screen_info()
        
        # อัพเดต UI fields
        self.screen_width_var.set(str(screen_info["physical_width"]))
        self.screen_height_var.set(str(screen_info["physical_height"]))
        self.scale_var.set(f"{int(screen_info['scale_factor'] * 100)}%")
        
        # Mark as changed
        self.on_change()
        
        # แสดง feedback
        messagebox.showinfo(
            "Auto Detection Complete",
            f"ตรวจพบความละเอียด: {screen_info['physical_width']}x{screen_info['physical_height']}\n"
            f"Scale: {int(screen_info['scale_factor'] * 100)}%\n"
            f"Method: {screen_info['detection_method']}"
        )
        
    except Exception as e:
        messagebox.showerror("Detection Error", f"ไม่สามารถตรวจหาความละเอียดได้: {str(e)}")
```

---

## 💾 Settings Management

### 🔄 Save Settings Process
```python
def save_settings(self):
    """Save current settings with validation"""
    try:
        # Validate input values
        user_width = int(self.screen_width_var.get())
        user_height = int(self.screen_height_var.get())
        scale_text = self.scale_var.get().rstrip("%")
        user_scale = float(scale_text) / 100.0 if scale_text else 1.0
        cpu_limit_value = self.cpu_limit_var.get()
        
        # Screen resolution validation
        screen_info = self.get_true_screen_info()
        actual_width = screen_info["physical_width"]
        actual_height = screen_info["physical_height"]
        actual_scale = screen_info["scale_factor"]
        
        # Warning หากค่าไม่ตรงกับจริง
        width_diff = abs(user_width - actual_width)
        height_diff = abs(user_height - actual_height)
        scale_diff = abs(user_scale - actual_scale)
        
        if width_diff > 100 or height_diff > 100 or scale_diff > 0.1:
            result = messagebox.askyesno(
                "Resolution Mismatch Warning",
                f"การตั้งค่าไม่ตรงกับหน้าจอปัจจุบัน:\n\n"
                f"ที่ตั้ง: {user_width}x{user_height} @ {int(user_scale*100)}%\n"
                f"จริง: {actual_width}x{actual_height} @ {int(actual_scale*100)}%\n\n"
                f"ต้องการบันทึกต่อไปหรือไม่?"
            )
            if not result:
                return
        
        # Save to settings
        screen_size = f"{user_width}x{user_height}"
        self.settings.set("screen_size", screen_size)
        self.settings.set("screen_width", user_width)
        self.settings.set("screen_height", user_height) 
        self.settings.set("display_scale", user_scale)
        self.settings.set("cpu_limit", cpu_limit_value)
        self.settings.set("use_gpu_for_ocr", self.gpu_var.get())
        
        # Call parent callback
        if self.apply_settings_callback:
            advance_settings = {
                "screen_size": screen_size,
                "display_scale": user_scale,
                "use_gpu_for_ocr": self.gpu_var.get(),
                "cpu_limit": cpu_limit_value
            }
            self.apply_settings_callback(advance_settings)
        
        # Force save to file
        self.settings.save_settings()
        
        # Show success feedback
        self.show_save_feedback()
        self.is_changed = False
        self.update_save_button()
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save settings: {str(e)}")

def show_save_feedback(self):
    """แสดง feedback การบันทึก"""
    if hasattr(self, 'save_btn') and self.save_btn.winfo_exists():
        original_text = self.save_btn.cget("text")
        original_bg = self.save_btn.cget("bg")
        
        # แสดง feedback
        self.save_btn.config(text="✓ Saved!", bg="#4CAF50")
        
        # รีเซ็ตหลัง 2 วินาที
        self.advance_window.after(2000, lambda: self.save_btn.config(
            text=original_text, 
            bg=original_bg
        ))
```

---

## 🚀 Integration with MBB Core

### 🔗 MBB Coordination
```python
# ใน mbb.py
def init_advance_ui(self):
    """เตรียม Advance UI"""
    try:
        from advance_ui import AdvanceUI
        
        self.advance_ui = AdvanceUI(
            parent=self.control_window,
            settings=self.settings,
            apply_settings_callback=self.handle_advance_ui_callback,
            ocr_toggle_callback=self.toggle_gpu_ocr
        )
        
        self.logging_manager.log_info("Advance UI initialized")
        
    except Exception as e:
        self.logging_manager.log_error(f"Advance UI init error: {e}")

def handle_advance_ui_callback(self, advance_settings):
    """จัดการ callback จาก Advance UI"""
    try:
        # อัพเดต CPU limit
        if "cpu_limit" in advance_settings:
            new_limit = advance_settings["cpu_limit"]
            if 1 <= new_limit <= 100:
                self.cpu_limit = new_limit
                self.logging_manager.log_info(f"CPU limit updated: {new_limit}%")
        
        # อัพเดต Screen Resolution
        if "screen_size" in advance_settings:
            screen_size = advance_settings["screen_size"] 
            self.logging_manager.log_info(f"Screen size updated: {screen_size}")
            
            # รีเฟรช area overlays ด้วยขนาดใหม่
            self.refresh_area_overlay_display()
        
        # อัพเดต GPU OCR Setting
        if "use_gpu_for_ocr" in advance_settings:
            use_gpu = advance_settings["use_gpu_for_ocr"]
            self.reinitialize_ocr_engine()  # รีสตาร์ท OCR กับ setting ใหม่
            self.logging_manager.log_info(f"GPU OCR updated: {use_gpu}")
            
        # อัพเดต Display Scale
        if "display_scale" in advance_settings:
            scale = advance_settings["display_scale"]
            self.logging_manager.log_info(f"Display scale updated: {scale}")
        
        return True
        
    except Exception as e:
        self.logging_manager.log_error(f"Handle advance settings error: {e}")
        return False
```

### 🎛️ Control UI Integration
```python
# ใน control_ui.py
def create_advance_button(self):
    """สร้างปุ่มเปิด Advance UI"""
    advance_btn = tk.Button(
        self.settings_frame,
        text="Screen & Advance",
        bg="#4a4a4a",
        fg="#e0e0e0", 
        font=("IBM Plex Sans Thai Medium", 9),
        bd=0,
        padx=8,
        pady=4,
        cursor="hand2",
        relief="flat",
        command=self.open_advance_ui
    )
    advance_btn.pack(side=tk.LEFT, padx=2)

def open_advance_ui(self):
    """เปิด Advance UI"""
    try:
        if hasattr(self.mbb_app, 'advance_ui') and self.mbb_app.advance_ui:
            # ถ้ามี Advance UI แล้ว ให้แสดงหน้าต่าง
            if hasattr(self.mbb_app.advance_ui, 'advance_window'):
                if (self.mbb_app.advance_ui.advance_window and 
                    self.mbb_app.advance_ui.advance_window.winfo_exists()):
                    self.mbb_app.advance_ui.advance_window.lift()
                else:
                    self.mbb_app.advance_ui.create_advance_window()
            else:
                self.mbb_app.advance_ui.create_advance_window()
        else:
            # สร้างใหม่
            self.mbb_app.init_advance_ui()
            
    except Exception as e:
        logging.error(f"Open Advance UI error: {e}")
```

---

## 🎨 UI Components Details

### 🖱️ Drag Functionality
```python
def setup_drag_functionality(self, widget):
    """ตั้งค่าการลาก UI"""
    def start_drag(event):
        self.dragging = True
        self.start_x = event.x
        self.start_y = event.y

    def on_drag(event):
        if self.dragging:
            x = self.advance_window.winfo_rootx() + event.x - self.start_x
            y = self.advance_window.winfo_rooty() + event.y - self.start_y
            self.advance_window.geometry(f"+{x}+{y}")

    def stop_drag(event):
        self.dragging = False

    widget.bind("<Button-1>", start_drag)
    widget.bind("<B1-Motion>", on_drag)
    widget.bind("<ButtonRelease-1>", stop_drag)
```

### 🎨 Modern Button Integration
```python
def create_bottom_buttons(self, parent):
    """สร้างปุ่ม Save และ Cancel"""
    button_frame = tk.Frame(parent, bg=self.theme.get_color("bg_primary"))
    button_frame.pack(fill="x", pady=(20, 0))
    
    # Cancel button
    cancel_btn = ModernButton.create(
        button_frame,
        text="Cancel",
        command=self.close_window,
        style="secondary"
    )
    cancel_btn.pack(side="right", padx=(5, 0))
    
    # Save button  
    self.save_btn = ModernButton.create(
        button_frame,
        text="Save Settings",
        command=self.save_settings,
        style="primary"
    )
    self.save_btn.pack(side="right")
    
    # Initially disable save if no changes
    self.update_save_button()

def update_save_button(self):
    """อัพเดตสถานะปุ่ม Save"""
    if hasattr(self, 'save_btn') and self.save_btn.winfo_exists():
        if self.is_changed:
            self.save_btn.config(state="normal", bg=self.theme.get_color("accent"))
        else:
            self.save_btn.config(state="disabled", bg="#666666")
```

---

## 🔍 Error Handling & Validation

### 🛡️ Input Validation
```python
def validate_resolution_input(self, width_str, height_str):
    """ตรวจสอบความถูกต้องของ input resolution"""
    try:
        width = int(width_str)
        height = int(height_str)
        
        # ตรวจสอบ range
        if not (800 <= width <= 7680):  # 800p to 8K
            return False, f"Width must be between 800-7680 (got {width})"
            
        if not (600 <= height <= 4320):  # 600p to 8K
            return False, f"Height must be between 600-4320 (got {height})"
            
        # ตรวจสอบ aspect ratio ที่สมเหตุสมผล
        aspect_ratio = width / height
        if not (1.0 <= aspect_ratio <= 3.0):  # 1:1 to 3:1
            return False, f"Unusual aspect ratio: {aspect_ratio:.2f}"
            
        return True, "Valid"
        
    except ValueError:
        return False, "Invalid number format"

def on_resolution_change(self, *args):
    """เรียกเมื่อมีการเปลี่ยน resolution input"""
    try:
        width_str = self.screen_width_var.get()
        height_str = self.screen_height_var.get()
        
        is_valid, message = self.validate_resolution_input(width_str, height_str)
        
        if is_valid:
            self.on_change()  # Mark as changed
            # ลบ error styling หากมี
            if hasattr(self, 'width_entry'):
                self.width_entry.config(bg="white")
            if hasattr(self, 'height_entry'):
                self.height_entry.config(bg="white")
        else:
            # แสดง error styling
            if hasattr(self, 'width_entry'):
                self.width_entry.config(bg="#ffcccc")
            if hasattr(self, 'height_entry'):
                self.height_entry.config(bg="#ffcccc")
                
    except Exception as e:
        logging.error(f"Resolution validation error: {e}")
```

### 📊 Performance Monitoring
```python
def monitor_settings_performance(self):
    """ตรวจสอบประสิทธิภาพการตั้งค่า"""
    try:
        # ตรวจสอบ CPU usage ปัจจุบัน
        import psutil
        current_cpu = psutil.cpu_percent(interval=0.1)
        cpu_limit = self.cpu_limit_var.get()
        
        # ตรวจสอบ GPU usage (ถ้าเปิดใช้งาน)
        gpu_enabled = self.gpu_var.get()
        
        # สร้าง performance report
        report = {
            "cpu_usage": current_cpu,
            "cpu_limit": cpu_limit,
            "cpu_status": "OK" if current_cpu < cpu_limit else "HIGH",
            "gpu_enabled": gpu_enabled,
            "timestamp": time.time()
        }
        
        return report
        
    except Exception as e:
        logging.error(f"Performance monitoring error: {e}")
        return None
```

---

## 📋 Usage Examples

### 💻 Basic Usage
```python
# สร้าง Advance UI
advance_ui = AdvanceUI(
    parent=main_window,
    settings=settings_manager,
    apply_settings_callback=handle_settings_change,
    ocr_toggle_callback=toggle_gpu_processing
)

# Callback functions
def handle_settings_change(advance_settings):
    """จัดการเมื่อมีการเปลี่ยนการตั้งค่า"""
    cpu_limit = advance_settings.get("cpu_limit", 80)
    screen_size = advance_settings.get("screen_size", "2560x1440")
    use_gpu = advance_settings.get("use_gpu_for_ocr", False)
    
    print(f"Settings updated: CPU {cpu_limit}%, Screen {screen_size}, GPU {use_gpu}")

def toggle_gpu_processing(enabled):
    """Toggle GPU OCR processing"""
    if enabled:
        initialize_gpu_ocr()
    else:
        initialize_cpu_ocr()
```

### 🔧 Advanced Configuration
```python
# Custom validation
def custom_resolution_validator(width, height):
    """Custom resolution validation"""
    if width == 1920 and height == 1080:
        return True, "Standard 1080p"
    elif width == 2560 and height == 1440:
        return True, "Standard 1440p"  
    elif width == 3840 and height == 2160:
        return True, "Standard 4K"
    else:
        return False, "Non-standard resolution"

advance_ui.set_resolution_validator(custom_resolution_validator)

# Performance monitoring
def monitor_performance():
    """ตรวจสอบประสิทธิภาพ"""
    if hasattr(advance_ui, 'monitor_settings_performance'):
        report = advance_ui.monitor_settings_performance()
        if report and report["cpu_status"] == "HIGH":
            print(f"Warning: CPU usage {report['cpu_usage']}% exceeds limit {report['cpu_limit']}%")

# Schedule monitoring
import threading
threading.Timer(30.0, monitor_performance).start()  # ทุก 30 วินาที
```

---

## 🔧 Troubleshooting

### ❗ Common Issues

#### 1. Screen Resolution ตรวจไม่พบ
```python
# สาเหตุ: ไม่มี win32api หรือ permission issue
# แก้ไข: ใช้ fallback method
def get_screen_info_fallback(self):
    """Fallback method ใช้ tkinter"""
    root = tk.Tk()
    root.withdraw()
    
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    
    root.destroy()
    
    return {
        "physical_width": width,
        "physical_height": height,
        "scale_factor": 1.0,
        "detection_method": "Tkinter Fallback"
    }
```

#### 2. CPU buttons ไม่ highlight
```python
# สาเหตุ: Theme colors ไม่ถูกต้อง
# แก้ไข: ตรวจสอบ theme initialization
if not hasattr(self, 'theme') or not self.theme:
    from utils_appearance import SettingsUITheme
    self.theme = SettingsUITheme
```

#### 3. Settings ไม่บันทึก
```python
# สาเหตุ: apply_settings_callback ไม่ทำงาน
# แก้ไข: ตรวจสอบ callback
if self.apply_settings_callback:
    try:
        self.apply_settings_callback(settings_data)
    except Exception as e:
        logging.error(f"Callback error: {e}")
        # บันทึกโดยตรง
        self.settings.save_settings()
```

---

## 📊 Change Log

### v2.0 (26/07/2025) - CPU Management Migration
- ✅ **CPU Management Migration** - ย้าย CPU limit control จาก Control UI มาที่ Advance UI
- ✅ **Enhanced Screen Detection** - ปรับปรุงการตรวจหา screen resolution ด้วย Win32API
- ✅ **Real-time Validation** - เพิ่มการตรวจสอบ input แบบ real-time
- ✅ **Modern UI Integration** - ใช้ SettingsUITheme และ Modern components
- ✅ **Performance Monitoring** - เพิ่มระบบตรวจสอบประสิทธิภาพ

### v1.x (เก่า)
- Basic screen resolution settings
- Simple GPU toggle
- No CPU management (อยู่ใน Control UI)

---

## 🎯 Future Enhancements

### 🚀 Planned Features
- **Multi-Monitor Support** - รองรับหน้าจอหลายตัว
- **Performance Profiles** - โปรไฟล์การตั้งค่าสำหรับสถานการณ์ต่างๆ
- **Advanced GPU Settings** - การตั้งค่า GPU แบบละเอียด
- **Resolution Presets** - ความละเอียดที่ตั้งไว้ล่วงหน้า
- **Real-time Performance Graph** - กราฟแสดง CPU/GPU usage
- **Settings Export/Import** - นำเข้า/ส่งออกการตั้งค่า

---

**📝 หมายเหตุ:** Advance UI เป็นส่วนสำคัญในการจัดการประสิทธิภาพของ MBB ควรตรวจสอบการตั้งค่าให้เหมาะสมกับฮาร์ดแวร์ของผู้ใช้

**🔗 Related Guides:**
- [MBB Core Guide](mbb_v9_guide.md)
- [Control UI Guide](control_ui_guide.md)
- [Settings System Guide](settings_system_guide.md)