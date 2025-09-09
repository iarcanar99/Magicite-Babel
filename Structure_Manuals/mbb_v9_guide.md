# 🎯 MBB v9 Core Module Guide (mbb.py)

**ไฟล์หลัก:** `mbb.py`  
**คลาสหลัก:** `MagicBabelApp`, `TranslationMetrics`  
**เวอร์ชัน:** v9.1 build 19072025.04

## 🎯 Overview
MBB.py เป็นไฟล์หลักของ Magicite Babel ที่ทำหน้าที่เป็น **Central Coordinator** ควบคุมการทำงานของระบบแปลภาษาแบบ Real-time ด้วยพลัง AI โดยประสานงานระหว่าง OCR, AI Translation, UI Management, และ Settings System

## 🏗️ Architecture Overview

### 📋 Core System Flow
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   MBB.py        │◄──►│   Control_UI     │◄──►│   Settings      │
│ (Main Controller)│    │ (Control Panel)  │    │ (Config Manager)│
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Translation_UI  │    │   OCR Engine     │    │  AI Translators │
│ (Display Layer) │    │ (Image Processing)│    │ (Gemini/Claude) │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🔧 Core Classes

### 1. `TranslationMetrics` - Performance Tracking
```python
class TranslationMetrics:
    def __init__(self):
        self.total_translations = 0      # จำนวนการแปลทั้งหมด
        self.method_counts = {}          # แยกตาม method (OCR/Manual)
        self.start_time = time.time()    # เวลาเริ่มต้น
        
    def record_translation(self, combined_text, method):
        # บันทึกสถิติการแปล
        # Update counters และ performance metrics
```

### 2. `MagicBabelApp` - Main Application Controller
```python
class MagicBabelApp:
    def __init__(self, root):
        # Core Components
        self.root = root                    # Main tkinter window
        self.settings = Settings()          # Configuration manager
        self.control_ui = None             # Control panel instance
        self.translated_ui = None          # Display UI instance
        
        # Translation System
        self.translator = None             # Current AI translator
        self.text_corrector = None         # Text correction system
        self.hover_translator = None       # Hover translation feature
        
        # OCR & Processing
        self.ocr_reader = None            # EasyOCR instance
        self.ocr_cache = {}               # OCR result cache
        self.ocr_speed = "normal"         # Processing speed
        
        # State Management
        self.translation_event = threading.Event()
        self.is_running = False           # Translation active state
        self.current_area = "A+B"         # Active translation area
        self.current_preset = 1           # Active preset number
```

## 🚀 Initialization Workflow

### 📱 Splash Screen System
```python
def show_splash():
    # 1. อ่านการตั้งค่า splash_screen_type จาก settings.json
    # 2. ตรวจสอบไฟล์ MBB_splash_vid.mp4 และ MBB_splash.png
    # 3. แสดง video (5s) หรือ image (3s) ตามการตั้งค่า
    # 4. ใช้ quadratic fade-in animation (2s สำหรับ video)
    # 5. Single-thread timer-based updates (แก้ไข thread conflict)
    # 6. Delayed initialization (3s) เพื่อหลีกเลี่ยง resource contention

def delayed_splash():
    # เรียก splash screen หลังจาก heavy resources โหลดเสร็จ
    self.splash, self.splash_photo = show_splash()
    if self.splash:
        self.splash_start_time = time.time()
```

### 🎨 Theme Initialization
```python
# 1. โหลดธีมจาก settings.json
saved_theme = self.settings.get("theme", None)

# 2. ตรวจสอบความพร้อมใช้งานของธีม
if saved_theme and saved_theme in appearance_manager.get_available_themes():
    appearance_manager.set_theme(saved_theme)
else:
    # ใช้ธีมเริ่มต้น Theme2
    appearance_manager.set_theme("Theme2")
    self.settings.set("theme", "Theme2")
```

### 🤖 Component Initialization Order
1. **Settings System** → โหลดการตั้งค่าทั้งหมด
2. **Theme System** → ตั้งค่าธีมและสี
3. **Translation Engine** → เตรียม AI translator
4. **OCR Engine** → เตรียม EasyOCR
5. **UI Components** → สร้าง Control UI และ Translation UI
6. **Feature Modules** → เตรียม Hover Translation, NPC Manager
7. **Delayed Splash Screen** → 3s หลังจาก heavy resources โหลดเสร็จ (แก้ไข thread conflict)

## 🎛️ Control UI Integration

### 📡 Control UI Creation & Coordination
```python
def setup_control_ui(self):
    self.control_ui = Control_UI(
        root=self.control_window,
        force_translate=self.force_translate,           # ฟังก์ชันแปลแบบบังคับ
        switch_area=self.switch_area,                   # ฟังก์ชันสลับพื้นที่
        settings=self.settings,                         # Settings object
        parent_app=self,                               # Reference กลับมาที่ main app
        parent_callback=self.handle_control_ui_callbacks,  # General callbacks
        trigger_temporary_area_display_callback=self.trigger_temporary_area_display,
        toggle_click_callback=self.set_click_translate_mode,
        toggle_hover_callback=self.toggle_hover_translation
    )
```

### 🔄 Bidirectional Communication Patterns

#### **MBB → Control UI**
```python
# จาก MBB.py ไป Control_UI
self.control_ui.update_button_highlights()      # อัพเดต UI state
self.control_ui.select_preset_in_control_ui(preset_num)  # เลือก preset
self.control_ui.refresh_area_overlay_display()  # รีเฟรช area display

# State synchronization
self.control_ui.current_preset = self.current_preset
self.control_ui.has_unsaved_changes = False
```

#### **Control UI → MBB**
```python
# จาก Control_UI กลับมาที่ MBB.py
self.force_translate()                    # เรียกการแปลบังคับ
self.switch_area(area_name)              # สลับพื้นที่แปล
self.set_click_translate_mode(value)     # เปิด/ปิด click translate
self.toggle_hover_translation(value)     # เปิด/ปิด hover translate
self.handle_advance_ui_callback(settings_data)  # อัพเดต advance settings
```

## ⚙️ Settings System Coordination

### 📂 Settings Integration Patterns
```python
# การอ่านค่าจาก Settings
self.cpu_limit = self.settings.get("cpu_limit", 80)
self.current_preset = self.settings.get("current_preset", 1)
self.current_area = self.settings.get("current_area", "A+B")
hover_enabled = self.settings.get("enable_hover_translation", False)

# การเขียนค่าลง Settings
self.settings.set("current_preset", preset_number)
self.settings.set("enable_hover_translation", value)
self.settings.set("theme", theme_name)
self.settings.save_settings()  # บันทึกลงไฟล์
```

### 🔄 Settings Synchronization Flow
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│     User        │    │   Control_UI     │    │   MBB.py        │
│   Interaction   │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │ 1. Change setting     │                       │
         ├──────────────────────►│                       │
         │                       │ 2. Validate & update │
         │                       ├──────────────────────►│
         │                       │                       │ 3. Apply to system
         │                       │                       ├─────────────┐
         │                       │                       │             │
         │                       │ 4. Update Settings   │             ▼
         │                       │    object             │    ┌─────────────────┐
         │                       │◄──────────────────────┤    │   Settings.py   │
         │                       │                       │    │                 │
         │ 5. UI feedback        │                       │    │ - Validate      │
         │◄──────────────────────┤                       │    │ - Save to JSON  │
         │                       │                       │    │ - Backup        │
         │                       │                       │    └─────────────────┘
```

## 🔄 Translation Workflow

### 📷 OCR Processing Pipeline
```python
def continuous_translation(self):
    while self.is_running:
        # 1. CPU Usage Check
        if self.check_cpu_usage() > self.cpu_limit:
            time.sleep(self.cpu_check_interval)
            continue
            
        # 2. Screen Capture
        current_areas = self.get_active_areas()  # จาก current_area setting
        
        for area_name, coordinates in current_areas.items():
            # 3. Image Processing
            image = ImageGrab.grab(bbox=coordinates)
            processed_image = self.preprocess_image(image)
            
            # 4. OCR Recognition  
            ocr_result = self.ocr_reader.readtext(processed_image)
            
            # 5. Text Filtering & Validation
            filtered_text = self.filter_ocr_results(ocr_result)
            
            # 6. Cache Check
            if self.is_text_cached(filtered_text):
                continue
                
            # 7. AI Translation
            translated_text = self.translator.translate(filtered_text)
            
            # 8. Display Update
            self.translated_ui.update_display(translated_text, area_name)
```

### 🎯 Force Translation System
```python
def force_translate(self):
    """การแปลแบบบังคับ - เรียกจาก Control UI"""
    try:
        # 1. เคลียร์ cache ทั้งหมด
        self.ocr_cache.clear()
        
        # 2. บันทึกสถิติ
        self.translation_metrics.record_translation("force_translate", "manual")
        
        # 3. ทำการแปลทันที (ข้าม CPU limit check)
        self.perform_immediate_translation()
        
        # 4. แสดง feedback ใน Control UI
        if hasattr(self.control_ui, 'show_force_translate_feedback'):
            self.control_ui.show_force_translate_feedback()
            
    except Exception as e:
        self.logging_manager.log_error(f"Force translate error: {e}")
```

## 🎨 UI Management & Theme Coordination

### 🎭 Theme Application Flow
```python
def apply_theme_to_components(self):
    """ประยุกต์ธีมให้กับ UI components ทั้งหมด"""
    # 1. Main Window
    self.root.configure(bg=appearance_manager.bg_color)
    
    # 2. Control UI
    if self.control_ui:
        self.control_ui.theme = self.get_control_ui_theme()
        self.control_ui.apply_theme_updates()
    
    # 3. Translation UI  
    if self.translated_ui:
        self.translated_ui.apply_theme(appearance_manager.get_current_theme())
    
    # 4. Settings UI
    if hasattr(self, 'settings_ui') and self.settings_ui:
        self.settings_ui.refresh_theme()
```

### 🎨 Dynamic Theme Updates
```python
def update_theme(self, new_theme_name):
    """อัพเดตธีมแบบ dynamic"""
    # 1. เปลี่ยนธีมใน appearance_manager
    appearance_manager.set_theme(new_theme_name)
    
    # 2. บันทึกลง settings
    self.settings.set("theme", new_theme_name)
    self.settings.save_settings()
    
    # 3. อัพเดต UI ทั้งหมด
    self.apply_theme_to_components()
    
    # 4. รีเฟรช Control UI colors
    if self.control_ui:
        self.control_ui.update_theme_colors()
```

## 🔧 Feature Management Integration

### 🎛️ Feature Toggle System
```python
def toggle_hover_translation(self, value):
    """เปิด/ปิด Hover Translation feature"""
    try:
        if value:
            # เปิดใช้งาน
            if not self.hover_translator:
                self.init_hover_translator()
            self.hover_translator.start()
        else:
            # ปิดใช้งาน
            if self.hover_translator:
                self.hover_translator.stop()
        
        # อัพเดต settings
        self.settings.set("enable_hover_translation", value)
        self.settings.save_settings()
        
        # Sync กับ Control UI
        if self.control_ui:
            self.control_ui.hover_translation_var.set(value)
            
    except Exception as e:
        self.logging_manager.log_error(f"Toggle hover translation error: {e}")
```

### 📱 Click Translation System
```python
def set_click_translate_mode(self, value):
    """ตั้งค่าโหมดการแปลด้วยการคลิก"""
    try:
        # อัพเดต internal state
        self.click_translate_enabled = value
        
        # อัพเดต settings
        self.settings.set("enable_click_translate", value)
        self.settings.save_settings()
        
        # Sync กับ Control UI checkbox
        if self.control_ui:
            self.control_ui.click_translate_var.set(value)
        
        # จัดการ hotkey binding
        if value:
            self.register_click_translate_hotkey()
        else:
            self.unregister_click_translate_hotkey()
            
    except Exception as e:
        self.logging_manager.log_error(f"Set click translate mode error: {e}")
```

## 🎯 Area & Preset Management

### 📍 Area Switching Coordination
```python
def switch_area(self, area_name):
    """สลับพื้นที่การแปล - เรียกจาก Control UI"""
    try:
        # 1. Validate area name
        valid_areas = ["A", "B", "C", "A+B", "B+C", "A+B+C"]
        if area_name not in valid_areas:
            return False
        
        # 2. อัพเดต current_area
        old_area = self.current_area
        self.current_area = area_name
        
        # 3. บันทึกลง settings
        self.settings.set("current_area", area_name)
        self.settings.save_settings()
        
        # 4. อัพเดต Control UI highlights
        if self.control_ui:
            self.control_ui.update_area_highlights(area_name)
        
        # 5. รีเฟรช translation areas
        self.refresh_translation_areas()
        
        # 6. Log การเปลี่ยนแปลง
        self.logging_manager.log_info(f"Area switched: {old_area} → {area_name}")
        
        return True
        
    except Exception as e:
        self.logging_manager.log_error(f"Switch area error: {e}")
        return False
```

### 📋 Preset Management Flow
```python
def load_preset(self, preset_number):
    """โหลด preset - coordination กับ Control UI"""
    try:
        # 1. ตรวจสอบความถูกต้องของ preset number
        if not (1 <= preset_number <= 6):
            return False
        
        # 2. ดึงข้อมูล preset จาก settings
        preset_data = self.settings.get_preset(preset_number)
        if not preset_data:
            return False
        
        # 3. อัพเดต translation areas
        for area_name in ["A", "B", "C"]:
            if area_name in preset_data.get("areas", {}):
                coordinates = preset_data["areas"][area_name]
                self.settings.set_translate_area(area_name, coordinates)
        
        # 4. อัพเดต current preset
        old_preset = self.current_preset
        self.current_preset = preset_number
        self.settings.set("current_preset", preset_number)
        self.settings.save_settings()
        
        # 5. Sync กับ Control UI
        if self.control_ui:
            self.control_ui.current_preset = preset_number
            self.control_ui.has_unsaved_changes = False
            self.control_ui.update_preset_display()
        
        # 6. รีเฟรช area overlays
        self.refresh_area_overlay_display()
        
        self.logging_manager.log_info(f"Preset loaded: {old_preset} → {preset_number}")
        return True
        
    except Exception as e:
        self.logging_manager.log_error(f"Load preset error: {e}")
        return False
```

## 🧵 Threading & Performance Management

### ⚡ Performance Management System
```python
def check_cpu_usage(self):
    """ตรวจสอบการใช้งาน CPU"""
    current_time = time.time()
    if current_time - self.last_cpu_check >= self.cpu_check_interval:
        try:
            import psutil
            cpu_usage = psutil.cpu_percent(interval=0.1)
            self.last_cpu_check = current_time
            return cpu_usage
        except:
            return 0  # ถ้าไม่สามารถตรวจสอบได้
    return self.last_cpu_usage

def handle_advance_ui_callback(self, advance_settings):
    """จัดการ callback จาก Advance UI - ทดแทน update_cpu_limit เดิม"""
    try:
        # อัพเดต CPU limit
        if "cpu_limit" in advance_settings:
            new_limit = advance_settings["cpu_limit"]
            if 1 <= new_limit <= 100:
                self.cpu_limit = new_limit
                self.settings.set("cpu_limit", new_limit)
                self.logging_manager.log_info(f"CPU limit updated: {new_limit}%")
        
        # อัพเดต Screen Resolution
        if "screen_size" in advance_settings:
            screen_size = advance_settings["screen_size"]
            self.settings.set("screen_size", screen_size)
            self.logging_manager.log_info(f"Screen size updated: {screen_size}")
        
        # อัพเดต GPU OCR Setting  
        if "use_gpu_for_ocr" in advance_settings:
            use_gpu = advance_settings["use_gpu_for_ocr"]
            self.settings.set("use_gpu_for_ocr", use_gpu)
            self.logging_manager.log_info(f"GPU OCR updated: {use_gpu}")
            
        # อัพเดต Display Scale
        if "display_scale" in advance_settings:
            scale = advance_settings["display_scale"]
            self.settings.set("display_scale", scale)
            self.logging_manager.log_info(f"Display scale updated: {scale}")
        
        # บันทึกการตั้งค่าทั้งหมด
        self.settings.save_settings()
        return True
        
    except Exception as e:
        self.logging_manager.log_error(f"Handle advance settings error: {e}")
        return False
```

### 🔄 Translation Threading
```python
def start_translation_thread(self):
    """เริ่มต้น translation thread"""
    if not self.translation_thread or not self.translation_thread.is_alive():
        self.is_running = True
        self.translation_event.set()
        self.translation_thread = threading.Thread(
            target=self.continuous_translation,
            daemon=True
        )
        self.translation_thread.start()
        self.logging_manager.log_info("Translation thread started")

def stop_translation_thread(self):
    """หยุด translation thread"""
    self.is_running = False
    self.translation_event.clear()
    if self.translation_thread and self.translation_thread.is_alive():
        self.translation_thread.join(timeout=2.0)
    self.logging_manager.log_info("Translation thread stopped")
```

## 🚀 Advanced Features Integration

### 🖱️ Hover Translation Management
```python
def init_hover_translator(self):
    """เตรียม Hover Translation system"""
    try:
        from hover_translation import HoverTranslator
        
        self.hover_translator = HoverTranslator(
            parent_app=self,
            settings=self.settings,
            translator=self.translator,
            logging_manager=self.logging_manager
        )
        
        # เชื่อมต่อกับ main translation system
        self.hover_translator.set_ocr_reader(self.ocr_reader)
        self.hover_translator.set_text_corrector(self.text_corrector)
        
        self.logging_manager.log_info("Hover translator initialized")
        
    except Exception as e:
        self.logging_manager.log_error(f"Hover translator init error: {e}")
```

### 👥 NPC Manager Integration
```python
def open_npc_manager(self):
    """เปิด NPC Manager - เรียกจาก Control UI"""
    try:
        if not self.npc_manager_instance:
            from npc_manager_card import create_npc_manager_card
            
            self.npc_manager_instance = create_npc_manager_card(
                parent_app=self,
                settings=self.settings,
                logging_manager=self.logging_manager
            )
        
        # แสดงหน้าต่าง NPC Manager
        if hasattr(self.npc_manager_instance, 'show'):
            self.npc_manager_instance.show()
        
    except Exception as e:
        self.logging_manager.log_error(f"NPC Manager error: {e}")
```

### ⚙️ Advance UI Integration
```python
def init_advance_ui(self):
    """เตรียม Advance UI - จัดการ Screen & Performance Settings"""
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

def open_advance_ui(self):
    """เปิด Advance UI - เรียกจาก Control UI"""
    try:
        if not hasattr(self, 'advance_ui') or not self.advance_ui:
            self.init_advance_ui()
        
        # แสดงหน้าต่าง Advance UI
        if hasattr(self.advance_ui, 'create_advance_window'):
            self.advance_ui.create_advance_window()
        
    except Exception as e:
        self.logging_manager.log_error(f"Open Advance UI error: {e}")

def toggle_gpu_ocr(self, enabled):
    """Toggle GPU OCR - เรียกจาก Advance UI"""
    try:
        self.settings.set("use_gpu_for_ocr", enabled)
        
        # รีสตาร์ท OCR engine ด้วย setting ใหม่
        if hasattr(self, 'ocr_reader'):
            self.reinitialize_ocr_engine()
            
        action = "enabled" if enabled else "disabled"
        self.logging_manager.log_info(f"GPU OCR {action}")
        
    except Exception as e:
        self.logging_manager.log_error(f"Toggle GPU OCR error: {e}")

def handle_screen_resolution_change(self, width, height, scale):
    """จัดการเมื่อมีการเปลี่ยนความละเอียดหน้าจอ"""
    try:
        # อัพเดต screen size setting
        screen_size = f"{width}x{height}"
        self.settings.set("screen_size", screen_size)
        self.settings.set("display_scale", scale)
        
        # รีเฟรช area overlays ด้วยขนาดใหม่
        self.refresh_area_overlay_display()
        
        # อัพเดต Control UI หากจำเป็น
        if self.control_ui:
            self.control_ui.update_screen_info(width, height, scale)
            
        self.logging_manager.log_info(f"Screen resolution updated: {screen_size} @ {int(scale*100)}%")
        
    except Exception as e:
        self.logging_manager.log_error(f"Handle screen resolution change error: {e}")
```

## 🔧 Error Handling & Recovery

### ✅ Robust Error Management
```python
def safe_execute(self, operation, *args, **kwargs):
    """Safe execution wrapper สำหรับ critical operations"""
    try:
        return operation(*args, **kwargs)
    except Exception as e:
        self.logging_manager.log_error(f"Safe execute error in {operation.__name__}: {e}")
        self.handle_critical_error(e, operation.__name__)
        return None

def handle_critical_error(self, error, operation_name):
    """จัดการ error ที่สำคัญ"""
    # 1. Log detailed error
    self.logging_manager.log_error(f"Critical error in {operation_name}: {error}")
    
    # 2. แจ้งเตือนผู้ใช้ (ถ้าจำเป็น)
    if self.control_ui:
        self.control_ui.show_error_notification(f"Error in {operation_name}")
    
    # 3. Attempt graceful recovery
    self.attempt_recovery(operation_name)
```

### 🔄 Recovery Mechanisms
```python
def attempt_recovery(self, failed_operation):
    """พยายาม recover จาก error"""
    try:
        if failed_operation == "continuous_translation":
            # หยุดและรีสตาร์ท translation thread
            self.stop_translation_thread()
            time.sleep(1)
            self.start_translation_thread()
            
        elif failed_operation == "ocr_processing":
            # รีสตาร์ท OCR engine
            self.reinitialize_ocr_engine()
            
        elif failed_operation == "translator":
            # รีสตาร์ท translator
            self.reinitialize_translator()
            
    except Exception as e:
        self.logging_manager.log_error(f"Recovery failed: {e}")
```

## 📊 Performance Monitoring

### 📈 Translation Metrics Tracking
```python
def get_performance_report(self):
    """สร้างรายงานประสิทธิภาพ"""
    if not self.translation_metrics:
        return "No metrics available"
    
    report = self.translation_metrics.get_report()
    
    # เพิ่มข้อมูล system metrics
    report += f"\nCurrent CPU Limit: {self.cpu_limit}%"
    report += f"\nOCR Cache Size: {len(self.ocr_cache)}"
    report += f"\nActive Threads: {threading.active_count()}"
    
    return report
```

## 📱 Startup & Shutdown Management

### 🚀 Complete Startup Sequence
```python
def _complete_startup(self):
    """Complete startup process - ปรับปรุงเรื่อง delayed splash"""
    try:
        # 1. เตรียม logging system
        self.setup_logging_system()
        
        # 2. เตรียม translation components (heavy resources)
        self.setup_translator()
        self.setup_ocr_engine()
        self.setup_text_corrector()
        
        # 3. สร้าง UI components
        self.setup_translated_ui()
        self.setup_control_ui()
        
        # 4. เตรียม feature modules
        self.setup_feature_modules()
        
        # 5. โหลด presets และ areas
        self.load_current_preset()
        
        # 6. เริ่มต้น translation system
        if self.settings.get("auto_start_translation", True):
            self.start_translation_thread()
        
        # 7. แสดง UI
        self.show_ui_components()
        
        # 8. 🎬 เริ่ม delayed splash หลังจาก heavy resources โหลดเสร็จ
        self.root.after(3000, self.delayed_splash)  # รอ 3 วินาทีก่อนแสดง splash
        
        self.logging_manager.log_info("MBB startup completed successfully with delayed splash")
        
    except Exception as e:
        self.logging_manager.log_error(f"Startup error: {e}")
        self.handle_startup_failure(e)
```

### 🔚 Graceful Shutdown
```python
def cleanup_and_exit(self):
    """Graceful shutdown process"""
    try:
        self.logging_manager.log_info("Starting MBB shutdown process")
        
        # 1. หยุด translation thread
        self.stop_translation_thread()
        
        # 2. ปิด feature modules
        if self.hover_translator:
            self.hover_translator.cleanup()
        
        # 3. ปิด UI windows
        if self.control_ui:
            self.control_ui.cleanup()
        if self.translated_ui:
            self.translated_ui.cleanup()
        
        # 4. บันทึก settings สุดท้าย
        self.settings.save_settings()
        
        # 5. ปิด logging
        self.logging_manager.cleanup()
        
        # 6. ปิด main window
        self.root.quit()
        self.root.destroy()
        
    except Exception as e:
        print(f"Shutdown error: {e}")
        # Force exit ถ้า graceful shutdown ล้มเหลว
        import sys
        sys.exit(1)
```

## 🔗 Integration Summary

### 📡 Component Communication Matrix
```
Component         → MBB.py    → Control_UI  → Settings   → Others
─────────────────────────────────────────────────────────────────
MBB.py           │     -     │ Callbacks   │ Read/Write │ Direct
Control_UI       │ Callbacks │      -      │ Read/Write │ None  
Settings         │ Observer  │  Observer   │     -      │ Notify
Translation_UI   │ Direct    │    None     │   Read     │ None
Hover_Translator │ Parent    │    None     │   Read     │ OCR
NPC_Manager      │ Parent    │    None     │   Read     │ None
```

### 🔄 Data Flow Patterns
1. **Settings Changes**: Control_UI → Settings → MBB.py → Apply to System
2. **Translation Request**: Control_UI → MBB.py → Translation Engine → Display
3. **Area Switching**: Control_UI → MBB.py → Settings → UI Updates
4. **Preset Loading**: Control_UI → MBB.py → Settings → Area Coordinates → UI

---

## 🔗 Related Files
- [`control_ui.py`](control_ui.py) - Control panel interface
- [`settings.py`](settings.py) - Configuration management  
- [`translated_ui.py`](translated_ui.py) - Translation display
- [`hover_translation.py`](hover_translation.py) - Hover translation feature
- [`npc_manager_card.py`](npc_manager_card.py) - NPC management system

## 📚 See Also
- [Control UI Guide](control_ui_guide.md)
- [Settings System Guide](settings_system_guide.md) 
- [Translation System Guide](translation_system_guide.md)
- [Feature Manager Guide](feature_manager_guide.md)
- [Structure Guide](structure.md)