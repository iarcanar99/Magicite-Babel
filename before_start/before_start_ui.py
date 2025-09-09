# before_start_ui_improved.py - ระบบตรวจสอบความพร้อมก่อนเริ่ม MBB (ปรับปรุงแล้ว)

import customtkinter as ctk
from tkinter import messagebox
import tkinter.font as tkfont
import subprocess
import sys
import os
import threading
import json
from checkers import APIChecker, SystemChecker, DataChecker


class BeforeStartUI:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("MBB Pre-Start System Check")
        self.root.geometry("850x600")  # เพิ่มขนาดหน้าต่าง
        self.root.resizable(False, False)
        
        # Add flag to track window state
        self._is_destroyed = False
        self.root.protocol("WM_DELETE_WINDOW", self._on_window_close)
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Load custom font
        self._load_custom_font()
        
        # Initialize checkers
        self.api_checker = APIChecker()
        self.system_checker = SystemChecker() 
        self.data_checker = DataChecker()
        
        # Check results
        self.check_results = {}
        self.can_start = False
        self.force_start = False
        self.auto_start_timer = None
        self.auto_start_countdown = 5
        
        # Skip check preference
        self.skip_next_time = ctk.BooleanVar(value=self._load_skip_preference())
        
        # UI Components
        self.status_labels = {}
        self.status_icons = {}
        self.action_buttons = {}
        
        self._setup_ui()
        
        # ตรวจสอบว่าต้อง skip หรือไม่
        if self.skip_next_time.get():
            self._safe_after(100, self._auto_skip_and_start)
        else:
            self._safe_after(100, self.run_all_checks)

    def _load_custom_font(self):
        """โหลดฟอนต์ Anuphan.ttf"""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            font_path = os.path.join(project_root, "fonts", "Anuphan.ttf")
            
            if os.path.exists(font_path):
                try:
                    import ctypes
                    gdi32 = ctypes.windll.gdi32
                    gdi32.AddFontResourceW(font_path)
                except:
                    pass
                
                self.font_loaded = True
            else:
                self.font_loaded = False
                
        except Exception:
            self.font_loaded = False
    def _get_anuphan_font(self, size=14, weight="normal"):
        """สร้างฟอนต์ Anuphan สำหรับ CTk components"""
        if self.font_loaded:
            try:
                return ctk.CTkFont(family="Anuphan", size=size, weight=weight)
            except:
                return ctk.CTkFont(size=size, weight=weight)
        else:
            return ctk.CTkFont(size=size, weight=weight)

    def _load_skip_preference(self):
        """โหลดการตั้งค่า skip check จากไฟล์"""
        try:
            pref_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "skip_preference.json")
            if os.path.exists(pref_file):
                with open(pref_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get("skip_next_time", False)
        except:
            pass
        return False

    def _save_skip_preference(self):
        """บันทึกการตั้งค่า skip check"""
        try:
            pref_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "skip_preference.json")
            with open(pref_file, 'w', encoding='utf-8') as f:
                json.dump({"skip_next_time": self.skip_next_time.get()}, f)
        except:
            pass
    
    def _safe_after(self, delay, func, *args):
        """Safely call root.after with checks"""
        try:
            if not self._is_destroyed and self.root.winfo_exists():
                return self.root.after(delay, func, *args)
        except Exception:
            pass
        return None
    
    def _on_window_close(self):
        """Handle window close event"""
        self._is_destroyed = True
        self.root.destroy()
    def _auto_skip_and_start(self):
        """ข้ามการตรวจสอบและเริ่มโปรแกรมทันที"""
        self.summary_label.configure(
            text="⚡ กำลังข้ามการตรวจสอบและเริ่มโปรแกรมอัตโนมัติ...",
            font=self._get_anuphan_font(size=18, weight="bold"),
            text_color="#fbbf24"
        )
        self.force_start = True
        self._safe_after(1000, self.start_mbb)

    def _setup_ui(self):
        # Header
        header_frame = ctk.CTkFrame(self.root, height=80)
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        header_frame.pack_propagate(False)

        ctk.CTkLabel(header_frame, text="MBB Pre-Start System Check",
                    font=self._get_anuphan_font(size=26, weight="bold")).pack(pady=5)
        
        ctk.CTkLabel(header_frame, text="กำลังตรวจสอบความพร้อมของระบบ...",
                    font=self._get_anuphan_font(size=14, weight="normal"), 
                    text_color="gray").pack()

        # Main content - 3 columns layout
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Left column - API
        left_frame = ctk.CTkFrame(main_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(15, 5), pady=15)
        self._create_check_section(left_frame, "🔑 API Configuration", "api")
        # Middle column - System
        middle_frame = ctk.CTkFrame(main_frame)
        middle_frame.pack(side="left", fill="both", expand=True, padx=5, pady=15)
        self._create_check_section(middle_frame, "💻 System Requirements", "system")

        # Right column - Data
        right_frame = ctk.CTkFrame(main_frame)
        right_frame.pack(side="left", fill="both", expand=True, padx=(5, 15), pady=15)
        self._create_check_section(right_frame, "📁 Data Files", "data")

        # Summary
        self.summary_frame = ctk.CTkFrame(self.root)
        self.summary_frame.pack(fill="x", padx=20, pady=10)
        
        self.summary_label = ctk.CTkLabel(self.summary_frame, text="กำลังตรวจสอบ...", 
                                         font=self._get_anuphan_font(size=16, weight="normal"))
        self.summary_label.pack(pady=10)

        # Action buttons frame
        button_frame = ctk.CTkFrame(self.root)
        button_frame.pack(fill="x", padx=20, pady=(0, 20))

        # Skip checkbox (ซ้าย)
        skip_frame = ctk.CTkFrame(button_frame, fg_color="transparent")
        skip_frame.pack(side="left", padx=5)
        
        self.skip_checkbox = ctk.CTkCheckBox(
            skip_frame, 
            text="ข้ามการตรวจสอบในครั้งต่อไป (Skip checks next time)",
            variable=self.skip_next_time,
            command=self._save_skip_preference,
            font=self._get_anuphan_font(size=14, weight="normal")
        )
        self.skip_checkbox.pack()
        # Action buttons (ขวา)
        action_frame = ctk.CTkFrame(button_frame, fg_color="transparent")
        action_frame.pack(side="right")

        self.cancel_auto_btn = ctk.CTkButton(
            action_frame, text="Cancel Auto Start", 
            command=self.cancel_auto_start,
            fg_color="orange", width=140, state="disabled"
        )
        self.cancel_auto_btn.pack(side="left", padx=5)

        self.start_btn = ctk.CTkButton(
            action_frame, text="Start MBB", 
            command=self.start_mbb,
            state="disabled", width=150, 
            fg_color="green",
            font=self._get_anuphan_font(size=16, weight="bold")
        )
        self.start_btn.pack(side="left", padx=5)

    def _create_check_section(self, parent, title: str, key: str):
        # Section header with icon
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        # Status icon (จะอัปเดตทีหลัง)
        self.status_icons[key] = ctk.CTkLabel(
            header_frame, text="⏳", 
            font=ctk.CTkFont(size=24),
            width=30
        )
        self.status_icons[key].pack(side="left", padx=(0, 5))
        # Title
        ctk.CTkLabel(
            header_frame, text=title, 
            font=self._get_anuphan_font(size=16, weight="bold"),
            anchor="w"
        ).pack(side="left", fill="x", expand=True)

        # Status text
        self.status_labels[f"{key}_status"] = ctk.CTkLabel(
            parent, text="กำลังตรวจสอบ...",
            font=self._get_anuphan_font(size=14, weight="normal"), 
            text_color="gray",
            anchor="w"
        )
        self.status_labels[f"{key}_status"].pack(fill="x", padx=(40, 10), pady=(0, 5))

        # Details with larger font
        self.status_labels[f"{key}_details"] = ctk.CTkLabel(
            parent, text="", 
            font=self._get_anuphan_font(size=14, weight="normal"),
            anchor="w", justify="left", 
            text_color="#e0e0e0"
        )
        self.status_labels[f"{key}_details"].pack(fill="x", padx=(40, 10), pady=(0, 10))

        # Action button (only for API and System)
        if key != "data":
            self.action_buttons[key] = ctk.CTkButton(
                parent, text="Configure", 
                width=100, height=30, 
                state="disabled", 
                font=self._get_anuphan_font(size=14, weight="normal")
            )
            self.action_buttons[key].pack(padx=40, pady=(0, 10))
    def _update_status_icon(self, key: str, status: str):
        """อัปเดตไอคอนสถานะ"""
        if self._is_destroyed:
            return
            
        icon_map = {
            "ready": "✅",
            "warning": "⚠️", 
            "error": "❌",
            "checking": "⏳"
        }
        
        color_map = {
            "ready": "#10b981",    # เขียว
            "warning": "#f59e0b",  # ส้ม
            "error": "#ef4444",    # แดง
            "checking": "#6b7280"  # เทา
        }
        
        icon = icon_map.get(status, "❓")
        color = color_map.get(status, "#6b7280")
        
        self.status_icons[key].configure(text=icon, text_color=color)

    def run_all_checks(self):
        # ยกเลิก auto start timer หากมี
        if self.auto_start_timer:
            if self.auto_start_timer and not self._is_destroyed:
                self.root.after_cancel(self.auto_start_timer)
            self.auto_start_timer = None
            
        # คืนสีพื้นหลัง summary frame
        self.summary_frame.configure(fg_color=["gray90", "gray13"])
        
        # คืนปุ่มให้เป็นปกติ
        self.start_btn.configure(text="Start MBB")
        self.cancel_auto_btn.configure(state="disabled")
        
        thread = threading.Thread(target=self._run_checks_thread)
        thread.daemon = True
        thread.start()
    def _run_checks_thread(self):
        try:
            # Check API
            if not self._is_destroyed:
                self._update_status("api", "กำลังตรวจสอบ API...", "gray")
                self._safe_after(0, self._update_status_icon, "api", "checking")
                
            api_result = self.api_checker.check_all()
            self.check_results["api"] = api_result
            
            if not self._is_destroyed:
                self._safe_after(0, self._update_api_display, api_result)

            # Check System
            if not self._is_destroyed:
                self._update_status("system", "กำลังตรวจสอบระบบ...", "gray")
                self._safe_after(0, self._update_status_icon, "system", "checking")
                
            system_result = self.system_checker.check_all()
            self.check_results["system"] = system_result
            
            if not self._is_destroyed:
                self._safe_after(0, self._update_system_display, system_result)

            # Check Data
            if not self._is_destroyed:
                self._update_status("data", "กำลังตรวจสอบไฟล์ข้อมูล...", "gray")
                self._safe_after(0, self._update_status_icon, "data", "checking")
                
            data_result = self.data_checker.check_all()
            self.check_results["data"] = data_result
            
            if not self._is_destroyed:
                self._safe_after(0, self._update_data_display, data_result)

            # Update summary
            if not self._is_destroyed:
                self._safe_after(0, self._update_summary)
                
        except Exception:
            # Window destroyed or other error
            pass

    def _update_status(self, key: str, message: str, color: str):
        def update():
            try:
                if not self._is_destroyed and hasattr(self, 'status_labels') and f"{key}_status" in self.status_labels:
                    self.status_labels[f"{key}_status"].configure(
                        text=message, 
                        text_color=color
                    )
            except Exception:
                pass
        
        self._safe_after(0, update)
    def _update_api_display(self, result: dict):
        if self._is_destroyed:
            return
            
        status = result["status"]
        self._update_status_icon("api", status)
        
        status_text = {
            "ready": "พร้อมใช้งาน", 
            "warning": "มีคำเตือน", 
            "error": "ต้องแก้ไข"
        }.get(status, "Unknown")
        
        status_color = {
            "ready": "#10b981", 
            "warning": "#f59e0b", 
            "error": "#ef4444"
        }.get(status, "gray")
        
        self._update_status("api", status_text, status_color)
        
        details = result.get("details", {})
        detail_lines = []
        for api_name, api_info in details.items():
            if api_info.get("connected"):
                detail_lines.append(f"• {api_name}: ✓ เชื่อมต่อสำเร็จ")
                if api_info.get("quota"):
                    detail_lines.append(f"  โควต้า: {api_info['quota']}")
            else:
                detail_lines.append(f"• {api_name}: ✗ {api_info.get('error', 'ยังไม่ได้ตั้งค่า')}")
        
        self.status_labels["api_details"].configure(text="\n".join(detail_lines))
        
        # Enable action button if there are issues
        if status in ["warning", "error"]:
            self.action_buttons["api"].configure(state="normal", command=self.open_model_config)
    def _update_system_display(self, result: dict):
        if self._is_destroyed:
            return
            
        status = result["status"]
        self._update_status_icon("system", status)
        
        status_text = {
            "ready": "พร้อมใช้งาน", 
            "warning": "มีคำเตือน", 
            "error": "ต้องแก้ไข"
        }.get(status, "Unknown")
        
        status_color = {
            "ready": "#10b981", 
            "warning": "#f59e0b", 
            "error": "#ef4444"
        }.get(status, "gray")
        
        self._update_status("system", status_text, status_color)
        
        details = result.get("details", {})
        detail_lines = []
        
        screen_info = details.get("screen", {})
        if screen_info:
            current_res = screen_info.get('current_resolution', 'Unknown')
            saved_res = screen_info.get('saved_resolution', 'Not configured')
            scale_pct = screen_info.get('scale_percentage', 100)
            
            detail_lines.append(f"• ความละเอียด: {current_res}")
            
            if screen_info.get("resolution_mismatch"):
                if saved_res == "Not configured":
                    detail_lines.append("  ⚠️ ยังไม่ได้ตั้งค่าความละเอียด")
                else:
                    detail_lines.append(f"  ⚠️ ไม่ตรงกับค่าที่บันทึก: {saved_res}")
            else:
                detail_lines.append(f"  ✓ ตั้งค่าถูกต้อง")
            
            if screen_info.get("scale_warning"):
                detail_lines.append(f"• Scale: {scale_pct}% ❌")
                detail_lines.append("  โปรดตั้งค่า Display Scale เป็น 100%")
            else:
                detail_lines.append(f"• Scale: {scale_pct}% ✓")
        
        gpu_info = details.get("gpu", {})
        if gpu_info:
            detail_lines.append(f"• GPU: {gpu_info.get('message', 'Unknown')}")
            
        memory_info = details.get("memory", {})
        if memory_info:
            detail_lines.append(f"• หน่วยความจำ: {memory_info.get('available', 'Unknown')}")
        
        self.status_labels["system_details"].configure(text="\n".join(detail_lines))
        
        # แสดงปุ่ม Fix Resolution หากจำเป็น
        if screen_info.get("resolution_mismatch"):
            self.action_buttons["system"].configure(
                state="normal", 
                text="Fix Resolution",
                command=self.fix_resolution_settings
            )
        else:
            self.action_buttons["system"].configure(
                state="disabled", 
                text="Fix Resolution"
            )
    def _update_data_display(self, result: dict):
        if self._is_destroyed:
            return
            
        status = result["status"]
        self._update_status_icon("data", status)
        
        status_text = {
            "ready": "พร้อมใช้งาน", 
            "warning": "มีคำเตือน", 
            "error": "ต้องแก้ไข"
        }.get(status, "Unknown")
        
        status_color = {
            "ready": "#10b981", 
            "warning": "#f59e0b", 
            "error": "#ef4444"
        }.get(status, "gray")
        
        self._update_status("data", status_text, status_color)
        
        details = result.get("details", {})
        detail_lines = []
        
        # NPC.json
        npc_info = details.get("npc_json", {})
        if npc_info.get("valid"):
            summary = npc_info.get("summary", "")
            detail_lines.append(f"• ฐานข้อมูล NPC: ✓ พบแล้ว")
            detail_lines.append(f"  {summary}")
        else:
            detail_lines.append(f"• ฐานข้อมูล NPC: ✗ {npc_info.get('error', 'ไม่พบไฟล์')}")
        
        # Settings
        settings_info = details.get("settings", {})
        if settings_info.get("valid"):
            detail_lines.append("• การตั้งค่า: ✓ ถูกต้อง")
        else:
            detail_lines.append("• การตั้งค่า: ✗ ไม่ถูกต้อง")
        
        # OCR Models
        models_info = details.get("models", {})
        if models_info.get("downloaded"):
            detail_lines.append("• OCR Models: ✓ พร้อมใช้งาน")
        else:
            detail_lines.append("• OCR Models: ⚠️ จะดาวน์โหลดเมื่อใช้งานครั้งแรก")
        
        self.status_labels["data_details"].configure(text="\n".join(detail_lines))

    def _update_summary(self):
        if self._is_destroyed:
            return
            
        error_count = sum(1 for r in self.check_results.values() if r.get("status") == "error")
        warning_count = sum(1 for r in self.check_results.values() if r.get("status") == "warning")

        # หยุด auto start timer หากมีอยู่
        if self.auto_start_timer:
            if self.auto_start_timer and not self._is_destroyed:
                self.root.after_cancel(self.auto_start_timer)
            self.auto_start_timer = None

        if error_count > 0:
            self.summary_label.configure(
                text=f"❌ พบปัญหา {error_count} รายการที่ต้องแก้ไข", 
                text_color="#ef4444", 
                font=self._get_anuphan_font(size=18, weight="bold")
            )
            self.can_start = False
            self.start_btn.configure(state="disabled")
        elif warning_count > 0:
            self.summary_label.configure(
                text=f"⚠️ พบคำเตือน {warning_count} รายการ (สามารถดำเนินการต่อได้)", 
                text_color="#f59e0b", 
                font=self._get_anuphan_font(size=18, weight="bold")
            )
            self.can_start = True
            self.start_btn.configure(state="normal")
        else:
            # ทุกอย่างผ่านการตรวจสอบแล้ว
            self._show_success_message()
            self.can_start = True
            self.start_btn.configure(state="normal")
    def _show_success_message(self):
        """แสดงข้อความสำเร็จแบบสวยๆ และเริ่ม countdown"""
        # เปลี่ยนสีพื้นหลัง summary frame
        self.summary_frame.configure(fg_color="#065f46")  # เขียวเข้ม
        
        # แสดงข้อความหลัก
        self.summary_label.configure(
            text="🎉 การตั้งค่าผ่านการตรวจสอบแล้ว ระบบพร้อมใช้งาน!", 
            text_color="#34d399",  # เขียวสว่าง
            font=self._get_anuphan_font(size=20, weight="bold")
        )
        
        # เริ่ม countdown
        self.auto_start_countdown = 5
        self._start_auto_countdown()

    def _start_auto_countdown(self):
        """เริ่มนับถอยหลังสำหรับการรันอัติโนมัติ"""
        if self._is_destroyed:
            return
            
        # เปิดใช้งานปุ่ม Cancel Auto Start
        self.cancel_auto_btn.configure(state="normal")
        
        if self.auto_start_countdown > 0:
            # อัปเดตข้อความ countdown
            countdown_text = (
                f"🎉 การตั้งค่าผ่านการตรวจสอบแล้ว ระบบพร้อมใช้งาน!\n"
                f"⏰ เริ่มโปรแกรมอัติโนมัติใน {self.auto_start_countdown} วินาที..."
            )
            self.summary_label.configure(
                text=countdown_text,
                font=self._get_anuphan_font(size=18, weight="bold")
            )
            
            # อัปเดตปุ่ม Start
            self.start_btn.configure(text=f"Start Now ({self.auto_start_countdown})")
            
            self.auto_start_countdown -= 1
            self.auto_start_timer = self._safe_after(1000, self._start_auto_countdown)
        else:
            # เวลาหมด - รันโปรแกรม
            self._auto_start_program()
    def cancel_auto_start(self):
        """ยกเลิกการรันอัติโนมัติ"""
        if self.auto_start_timer:
            if self.auto_start_timer and not self._is_destroyed:
                self.root.after_cancel(self.auto_start_timer)
            self.auto_start_timer = None
        
        # คืนสีพื้นหลัง summary frame
        self.summary_frame.configure(fg_color=["gray90", "gray13"])
        
        # แสดงข้อความปกติ
        self.summary_label.configure(
            text="✅ ระบบพร้อมใช้งาน (ยกเลิกการรันอัติโนมัติแล้ว)",
            text_color="#10b981",
            font=self._get_anuphan_font(size=16, weight="normal")
        )
        
        # คืนปุ่มให้เป็นปกติ
        self.start_btn.configure(text="Start MBB")
        self.cancel_auto_btn.configure(state="disabled")

    def _auto_start_program(self):
        """รันโปรแกรมอัติโนมัติ"""
        if self._is_destroyed:
            return
            
        # แสดงข้อความสุดท้าย
        self.summary_label.configure(
            text="🚀 กำลังเริ่มโปรแกรม MBB...",
            text_color="#60a5fa",  # น้ำเงินสว่าง
            font=self._get_anuphan_font(size=18, weight="bold")
        )
        
        # เปลี่ยนปุ่ม
        self.start_btn.configure(text="Starting...", state="disabled")
        self.cancel_auto_btn.configure(state="disabled")
        
        # รอสักครู่แล้วเริ่มโปรแกรม
        self._safe_after(1000, self.start_mbb)
    def open_model_config(self):
        """เปิด API Configuration"""
        try:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            # ลองใช้ simple_model_config.py ก่อน
            simple_config_path = os.path.join(project_root, "simple_model_config.py")
            if os.path.exists(simple_config_path):
                subprocess.Popen([sys.executable, simple_config_path], cwd=project_root)
                messagebox.showinfo("Info", "เปิด API Configuration แล้ว")
                return
            
            # สำหรับ Windows: ลองใช้ batch file
            if os.name == 'nt':
                bat_path = os.path.join(project_root, "model_config.bat")
                if os.path.exists(bat_path):
                    subprocess.Popen([bat_path], cwd=project_root, shell=True)
                    messagebox.showinfo("Info", "เปิด Model Configuration แล้ว")
                    return
            
            # ลองใช้ model_launcher.py
            launcher_path = os.path.join(project_root, "model_launcher.py")
            if os.path.exists(launcher_path):
                subprocess.Popen([sys.executable, launcher_path], cwd=project_root)
                messagebox.showinfo("Info", "เปิด Model Configuration แล้ว")
                return
            
            # ลองเปิด model.py โดยตรง
            model_path = os.path.join(project_root, "model.py")
            subprocess.Popen([sys.executable, model_path], cwd=project_root, shell=True)
            messagebox.showinfo("Info", "เปิด Model Configuration แล้ว")
            
        except Exception as e:
            messagebox.showerror("Error", f"ไม่สามารถเปิด Model Configuration ได้: {str(e)}")
    def fix_resolution_settings(self):
        """แก้ไขการตั้งค่า resolution ใน settings.json"""
        try:
            success = self.system_checker.fix_resolution_settings()
            
            if success:
                messagebox.showinfo("แก้ไขสำเร็จ", 
                    "แก้ไขการตั้งค่าความละเอียดหน้าจอเรียบร้อยแล้ว\n"
                    "กรุณาตรวจสอบระบบใหม่อีกครั้ง")
                
                # รีเซ็ต action button
                self.action_buttons["system"].configure(state="disabled", text="Fix Resolution")
                
                # รันการตรวจสอบระบบใหม่
                thread = threading.Thread(target=self._run_single_check, args=("system",))
                thread.daemon = True
                thread.start()
            else:
                messagebox.showerror("เกิดข้อผิดพลาด", 
                    "ไม่สามารถแก้ไขการตั้งค่าได้\n"
                    "กรุณาลองใหม่หรือแก้ไขด้วยตนเอง")
                
        except Exception as e:
            messagebox.showerror("เกิดข้อผิดพลาด", f"เกิดข้อผิดพลาด: {str(e)}")

    def _run_single_check(self, check_type: str):
        """รันการตรวจสอบเฉพาะส่วน"""
        if check_type == "system":
            self._update_status("system", "กำลังตรวจสอบระบบ...", "gray")
            self._update_status_icon("system", "checking")
            result = self.system_checker.check_all()
            self.check_results["system"] = result
            self._safe_after(0, self._update_system_display, result)
            self._safe_after(0, self._update_summary)
    def start_mbb(self):
        # ยกเลิก auto start timer หากมี
        if self.auto_start_timer:
            if self.auto_start_timer and not self._is_destroyed:
                self.root.after_cancel(self.auto_start_timer)
            self.auto_start_timer = None
        
        # บันทึก preference
        self._save_skip_preference()
        
        # Set destroyed flag before destroying
        self._is_destroyed = True
        self.root.destroy()

    def run(self):
        self.root.mainloop()
        return {
            "can_start": self.can_start or self.force_start,
            "force_start": self.force_start,
            "check_results": self.check_results,
        }


if __name__ == "__main__":
    checker = BeforeStartUI()
    result = checker.run()
    
    if result["can_start"]:
        print("Starting MBB...")
        try:
            import sys
            import os
            
            # พยายามรัน MBB.py แทนการ import โดยตรง
            mbb_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "MBB.py")
            if os.path.exists(mbb_path):
                import subprocess
                subprocess.run([sys.executable, mbb_path])
            else:
                # Fallback: import และสร้าง app
                sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                from MBB import MagicBabelApp
                
                # สร้าง tkinter root สำหรับ MBB
                import tkinter as tk
                mbb_root = tk.Tk()
                app = MagicBabelApp(mbb_root)
                app.mainloop()
        except ImportError:
            print("MBB module not found. Please run from project root.")
        except Exception as e:
            print(f"Error starting MBB: {e}")
    else:
        print("System check failed or cancelled by user")