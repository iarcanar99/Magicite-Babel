import tkinter as tk
from tkinter import ttk, messagebox
import logging
from loggings import LoggingManager
from utils_appearance import SettingsUITheme, ModernButton, ModernEntry, ModernFrame
import threading
import time


class AdvanceUI:
    def __init__(
        self, parent, settings, apply_settings_callback, ocr_toggle_callback=None
    ):
        self.parent = parent
        self.settings = settings
        self.apply_settings_callback = apply_settings_callback
        self.ocr_toggle_callback = ocr_toggle_callback
        self.advance_window = None
        self.is_changed = False

        # ตัวแปรสำหรับเก็บค่า CPU Limit ที่เลือกใน UI
        self.cpu_limit_var = tk.IntVar(value=self.settings.get("cpu_limit", 100))

        # Initialize theme
        self.theme = SettingsUITheme

        # Variables for dragging
        self.dragging = False
        self.start_x = 0
        self.start_y = 0

        # สร้างหน้าต่างทันทีแบบเดิม
        self.create_advance_window()

    def set_cpu_limit(self, limit):
        """อัพเดทค่าใน UI และตั้งค่าสถานะว่ามีการเปลี่ยนแปลง"""
        if self.cpu_limit_var.get() != limit:
            self.cpu_limit_var.set(limit)
            self.update_cpu_buttons(limit)
            self.on_change()  # เรียกเพื่อให้ปุ่ม Save ทำงาน

    def update_cpu_buttons(self, active_limit):
        """อัพเดตสถานะปุ่ม CPU limit ให้ไฮไลท์ปุ่มที่ถูกเลือก"""
        btn_map = {
            50: getattr(self, "cpu_50_btn", None),
            60: getattr(self, "cpu_60_btn", None),
            80: getattr(self, "cpu_80_btn", None),
            100: getattr(self, "cpu_100_btn", None),
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

    def create_cpu_section(self, parent):
        """สร้างส่วนตั้งค่า CPU Performance"""
        section_frame = tk.LabelFrame(
            parent,
            text="CPU Performance",
            bg=self.theme.get_color("bg_secondary"),
            fg=self.theme.get_color("text_primary"),
            font=self.theme.get_font("medium", "bold"),
            bd=1,
            relief="solid",
        )
        section_frame.pack(fill="x", pady=(0, 12))

        cpu_frame = tk.Frame(section_frame, bg=self.theme.get_color("bg_secondary"))
        cpu_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(
            cpu_frame,
            text="CPU Usage Limit:",
            bg=self.theme.get_color("bg_secondary"),
            fg=self.theme.get_color("text_primary"),
            font=self.theme.get_font("normal"),
        ).pack(side="left", anchor="w")

        buttons_container = tk.Frame(cpu_frame, bg=self.theme.get_color("bg_secondary"))
        buttons_container.pack(side="right", padx=(10, 0))

        self.cpu_50_btn = ModernButton.create(
            buttons_container,
            text="50%",
            command=lambda: self.set_cpu_limit(50),
            width=5,
        )
        self.cpu_50_btn.pack(side="left", padx=(0, 3))

        self.cpu_60_btn = ModernButton.create(
            buttons_container,
            text="60%",
            command=lambda: self.set_cpu_limit(60),
            width=5,
        )
        self.cpu_60_btn.pack(side="left", padx=3)

        self.cpu_80_btn = ModernButton.create(
            buttons_container,
            text="80%",
            command=lambda: self.set_cpu_limit(80),
            width=5,
        )
        self.cpu_80_btn.pack(side="left", padx=3)

        self.cpu_100_btn = ModernButton.create(
            buttons_container,
            text="100%",
            command=lambda: self.set_cpu_limit(100),
            width=5,
        )
        self.cpu_100_btn.pack(side="left", padx=(3, 0))
        
        # Ensure the 100% button is initially highlighted if it's the default
        initial_cpu_limit = self.settings.get("cpu_limit", 100)
        if initial_cpu_limit == 100:
            self.update_cpu_buttons(100)

    def show_cpu_limit_feedback(self, limit):
        """แสดง Feedback เมื่อบันทึกค่า CPU Limit"""
        # ฟังก์ชันนี้สามารถนำโค้ดเดิมจาก control_ui.py มาใช้ได้
        # หรือจะรวม Feedback ไปกับการกด Save หลักทีเดียวก็ได้
        # ในที่นี้ เราจะให้ Feedback รวมไปกับการกด Save หลัก
        logging.info(f"CPU Limit will be set to {limit}% upon saving.")

    def check_screen_resolution(self):
        """ตรวจสอบขนาดหน้าจอที่ตั้งค่าในวินโดว์
        Returns:
            dict: ผลการตรวจสอบ
        """
        try:
            # ดึงข้อมูลหน้าจอที่แท้จริงโดยใช้เมธอดใหม่
            screen_info = self.get_true_screen_info()

            # ใช้ข้อมูล physical resolution เป็นค่าปัจจุบัน
            current_width = screen_info["physical_width"]
            current_height = screen_info["physical_height"]
            scale_factor = screen_info["scale_factor"]

            # ดึงค่าที่ตั้งไว้ใน settings มาเทียบ
            expected_resolution = self.settings.get("screen_size", "2560x1440")
            expected_width, expected_height = map(int, expected_resolution.split("x"))

            # แสดงค่า scale เป็น percentage
            scale_percent = int(scale_factor * 100)

            # เปรียบเทียบค่า (ให้มี tolerance ±5%)
            width_tolerance = expected_width * 0.05
            height_tolerance = expected_height * 0.05

            if (
                abs(current_width - expected_width) > width_tolerance
                or abs(current_height - expected_height) > height_tolerance
            ):
                return {
                    "is_valid": False,
                    "message": (
                        f"ความละเอียดหน้าจอไม่ตรงกับการตั้งค่า!\n"
                        f"ปัจจุบัน: {current_width}x{current_height} (Scale: {scale_percent}%)\n"
                        f"ที่ตั้งไว้: {expected_width}x{expected_height}\n"
                        f"กรุณาตรวจสอบการตั้งค่าความละเอียดหน้าจอ"
                    ),
                    "current": f"{current_width}x{current_height}",
                    "expected": expected_resolution,
                    "scale": scale_factor,
                }

            return {
                "is_valid": True,
                "current": f"{current_width}x{current_height}",
                "expected": expected_resolution,
                "scale": scale_factor,
            }

        except Exception as e:
            print(f"Error checking screen resolution: {e}")
            return {
                "is_valid": False,
                "message": f"เกิดข้อผิดพลาดในการตรวจสอบความละเอียด: {str(e)}",
                "current": "Unknown",
                "expected": "Unknown",
                "scale": 1.0,
            }

    def get_true_screen_info(self):
        """ดึงข้อมูลความละเอียดหน้าจอที่แท้จริงและค่า scale ที่ถูกต้อง โดยใช้หลายวิธีร่วมกัน

        Returns:
            dict: {
                "physical_width": ความกว้างทางกายภาพ,
                "physical_height": ความสูงทางกายภาพ,
                "scale_factor": ค่า scale factor ที่แท้จริง,
                "logical_width": ความกว้างหลังคำนวณ scale,
                "logical_height": ความสูงหลังคำนวณ scale,
                "detection_method": วิธีการที่ใช้ตรวจสอบ
            }
        """
        print("🔍 [DEBUG] Getting screen info...")

        # วิธีที่ 1: ลองใช้ win32api
        try:
            import win32api
            import win32con

            print("🔍 [DEBUG] Trying Win32API method...")

            device_mode = win32api.EnumDisplaySettings(
                None, win32con.ENUM_CURRENT_SETTINGS
            )
            physical_width = device_mode.PelsWidth
            physical_height = device_mode.PelsHeight
            print(f"🔍 [DEBUG] Win32API physical: {physical_width}x{physical_height}")

            # ดึง logical resolution จาก tkinter
            root = tk._default_root or self.advance_window
            logical_width = root.winfo_screenwidth()
            logical_height = root.winfo_screenheight()
            print(f"🔍 [DEBUG] Tkinter logical: {logical_width}x{logical_height}")

            # คำนวณ scale factor
            scale_factor = physical_width / logical_width if logical_width > 0 else 1.0
            print(f"🔍 [DEBUG] Calculated scale: {scale_factor}")

            return {
                "physical_width": physical_width,
                "physical_height": physical_height,
                "scale_factor": scale_factor,
                "logical_width": logical_width,
                "logical_height": logical_height,
                "detection_method": "Win32API + Tkinter",
            }

        except Exception as e:
            print(f"🔍 [DEBUG] Win32API method failed: {e}")

        # วิธีที่ 2: ลองใช้ ctypes
        try:
            import ctypes
            from ctypes import windll

            print("🔍 [DEBUG] Trying ctypes method...")

            # Get DPI awareness
            try:
                windll.shcore.SetProcessDpiAwareness(1)
            except:
                pass

            # Get physical screen size
            physical_width = windll.user32.GetSystemMetrics(0)
            physical_height = windll.user32.GetSystemMetrics(1)
            print(f"🔍 [DEBUG] Ctypes physical: {physical_width}x{physical_height}")

            # ดึง logical resolution จาก tkinter
            root = tk._default_root or self.advance_window
            logical_width = root.winfo_screenwidth()
            logical_height = root.winfo_screenheight()
            print(f"🔍 [DEBUG] Tkinter logical: {logical_width}x{logical_height}")

            # คำนวณ scale factor
            scale_factor = physical_width / logical_width if logical_width > 0 else 1.0
            print(f"🔍 [DEBUG] Calculated scale: {scale_factor}")

            return {
                "physical_width": physical_width,
                "physical_height": physical_height,
                "scale_factor": scale_factor,
                "logical_width": logical_width,
                "logical_height": logical_height,
                "detection_method": "Ctypes + Tkinter",
            }

        except Exception as e:
            print(f"🔍 [DEBUG] Ctypes method failed: {e}")

        # วิธีที่ 3: Fallback - ใช้ tkinter เท่านั้น
        try:
            print("🔍 [DEBUG] Using Tkinter fallback...")
            root = tk._default_root or self.advance_window
            logical_width = root.winfo_screenwidth()
            logical_height = root.winfo_screenheight()
            print(f"🔍 [DEBUG] Tkinter only: {logical_width}x{logical_height}")

            return {
                "physical_width": logical_width,
                "physical_height": logical_height,
                "scale_factor": 1.0,
                "logical_width": logical_width,
                "logical_height": logical_height,
                "detection_method": "Tkinter Fallback",
            }

        except Exception as e:
            print(f"🔍 [DEBUG] Tkinter fallback failed: {e}")

        # วิธีสุดท้าย: Default values
        print("🔍 [DEBUG] Using default values...")
        return {
            "physical_width": 1920,
            "physical_height": 1080,
            "scale_factor": 1.0,
            "logical_width": 1920,
            "logical_height": 1080,
            "detection_method": "Default Values",
        }

    def get_simple_screen_info(self):
        """ดึงข้อมูลหน้าจอแบบง่าย ใช้ tkinter เท่านั้น"""
        try:
            print("🔍 [DEBUG] Getting simple screen info using tkinter...")

            # ใช้ advance_window หรือ parent
            root_window = self.advance_window or self.parent
            logical_width = root_window.winfo_screenwidth()
            logical_height = root_window.winfo_screenheight()

            print(f"🔍 [DEBUG] Tkinter screen size: {logical_width}x{logical_height}")

            return {
                "physical_width": logical_width,
                "physical_height": logical_height,
                "scale_factor": 1.0,
                "logical_width": logical_width,
                "logical_height": logical_height,
                "detection_method": "Tkinter Simple",
            }

        except Exception as e:
            print(f"🔍 [DEBUG] Simple method failed: {e}")
            return {
                "physical_width": 1920,
                "physical_height": 1080,
                "scale_factor": 1.0,
                "logical_width": 1920,
                "logical_height": 1080,
                "detection_method": "Hardcoded Default",
            }

    def create_advance_window(self):
        """สร้างหน้าต่าง Advanced Settings แบบ Modern Design"""
        if self.advance_window is None or not self.advance_window.winfo_exists():
            self.advance_window = tk.Toplevel(self.parent)
            self.advance_window.title("Screen & Advance")
            self.advance_window.geometry("450x500")  # เพิ่มความกว้างและความสูงรองรับ cpu settings
            self.advance_window.overrideredirect(True)
            self.advance_window.configure(bg=self.theme.get_color("bg_primary"))

            # Main container with padding
            main_container = tk.Frame(
                self.advance_window, bg=self.theme.get_color("bg_primary")
            )
            main_container.pack(fill="both", expand=True, padx=16, pady=16)

            # Title bar with drag functionality
            self.create_title_bar(main_container)

            # Content sections
            self.create_screen_section(main_container)
            self.create_gpu_section(main_container)

            # cpu limit section
            self.create_cpu_section(main_container)

            # Bottom buttons
            self.create_bottom_buttons(main_container)

            # Setup drag functionality for entire window
            self.setup_drag_events(self.advance_window)

            # เริ่มต้นด้วยการซ่อนหน้าต่าง
            self.advance_window.withdraw()

    def create_title_bar(self, parent):
        """สร้าง title bar พร้อม close button และ drag functionality"""
        title_frame = tk.Frame(parent, bg=self.theme.get_color("bg_primary"))
        title_frame.pack(fill="x", pady=(0, 12))

        # Title with drag functionality
        title_label = tk.Label(
            title_frame,
            text="Screen & Advance",
            font=self.theme.get_font("title", "bold"),
            bg=self.theme.get_color("bg_primary"),
            fg=self.theme.get_color("text_primary"),
            cursor="fleur",
        )
        title_label.pack(side="left")

        # Bind drag events to title
        self.setup_drag_events(title_label)

        # Close button
        self.create_close_button(title_frame)

    def create_close_button(self, parent):
        """สร้าง close button แบบ modern"""
        close_frame = tk.Frame(parent, bg=self.theme.get_color("bg_primary"))
        close_frame.pack(side="right")

        close_btn = tk.Button(
            close_frame,
            text="✕",
            font=self.theme.get_font("medium", "bold"),
            bg=self.theme.get_color("bg_secondary"),
            fg=self.theme.get_color("text_secondary"),
            activebackground=self.theme.get_color("error"),
            activeforeground="white",
            relief="flat",
            bd=0,
            width=3,
            height=1,
            cursor="hand2",
            command=self.close,
        )
        close_btn.pack()

        # Hover effect สำหรับ close button
        def on_enter(e):
            close_btn.config(bg=self.theme.get_color("error"), fg="white")

        def on_leave(e):
            close_btn.config(
                bg=self.theme.get_color("bg_secondary"),
                fg=self.theme.get_color("text_secondary"),
            )

        close_btn.bind("<Enter>", on_enter)
        close_btn.bind("<Leave>", on_leave)

    def create_screen_section(self, parent):
        """สร้างส่วน Screen Resolution"""
        # Section frame
        section_frame = tk.LabelFrame(
            parent,
            text="Screen Resolution",
            bg=self.theme.get_color("bg_secondary"),
            fg=self.theme.get_color("text_primary"),
            font=self.theme.get_font("medium", "bold"),
            bd=1,
            relief="solid",
        )
        section_frame.pack(fill="x", pady=(0, 12))

        # Current Resolution Display
        current_frame = tk.Frame(section_frame, bg=self.theme.get_color("bg_secondary"))
        current_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(
            current_frame,
            text="Current:",
            bg=self.theme.get_color("bg_secondary"),
            fg=self.theme.get_color("text_primary"),
            font=self.theme.get_font("normal"),
        ).pack(side="left")

        self.current_res_label = tk.Label(
            current_frame,
            text="Detecting...",
            bg=self.theme.get_color("bg_secondary"),
            fg=self.theme.get_color("success"),
            font=self.theme.get_font("normal"),
        )
        self.current_res_label.pack(side="right", padx=5)

        # Width setting
        width_frame = tk.Frame(section_frame, bg=self.theme.get_color("bg_secondary"))
        width_frame.pack(fill="x", padx=10, pady=2)

        tk.Label(
            width_frame,
            text="Set Width:",
            bg=self.theme.get_color("bg_secondary"),
            fg=self.theme.get_color("text_primary"),
            font=self.theme.get_font("normal"),
        ).pack(side="left")

        self.screen_width_var = tk.StringVar()
        width_combo = ttk.Combobox(
            width_frame,
            values=["1920", "2560", "3440", "3840"],
            textvariable=self.screen_width_var,
            width=8,
            state="readonly",
        )
        width_combo.pack(side="right", padx=5)
        width_combo.bind("<<ComboboxSelected>>", self.on_change)

        # Height setting
        height_frame = tk.Frame(section_frame, bg=self.theme.get_color("bg_secondary"))
        height_frame.pack(fill="x", padx=10, pady=2)

        tk.Label(
            height_frame,
            text="Set Height:",
            bg=self.theme.get_color("bg_secondary"),
            fg=self.theme.get_color("text_primary"),
            font=self.theme.get_font("normal"),
        ).pack(side="left")

        self.screen_height_var = tk.StringVar()
        height_combo = ttk.Combobox(
            height_frame,
            values=["1080", "1440", "1440", "2160"],
            textvariable=self.screen_height_var,
            width=8,
            state="readonly",
        )
        height_combo.pack(side="right", padx=5)
        height_combo.bind("<<ComboboxSelected>>", self.on_change)

        # Display Scale setting
        scale_frame = tk.Frame(section_frame, bg=self.theme.get_color("bg_secondary"))
        scale_frame.pack(fill="x", padx=10, pady=(5, 10))

        tk.Label(
            scale_frame,
            text="Display Scale:",
            bg=self.theme.get_color("bg_secondary"),
            fg=self.theme.get_color("text_primary"),
            font=self.theme.get_font("normal"),
        ).pack(side="left")

        self.scale_var = tk.StringVar()
        scale_combo = ttk.Combobox(
            scale_frame,
            values=["100%", "125%", "150%", "175%", "200%"],
            textvariable=self.scale_var,
            width=8,
            state="readonly",
        )
        scale_combo.pack(side="right", padx=5)
        scale_combo.bind("<<ComboboxSelected>>", self.on_change)

    def create_gpu_section(self, parent):
        """สร้างส่วน GPU Settings"""
        # Section frame
        section_frame = tk.LabelFrame(
            parent,
            text="OCR Performance",
            bg=self.theme.get_color("bg_secondary"),
            fg=self.theme.get_color("text_primary"),
            font=self.theme.get_font("medium", "bold"),
            bd=1,
            relief="solid",
        )
        section_frame.pack(fill="x", pady=(0, 12))

        # GPU toggle
        gpu_frame = tk.Frame(section_frame, bg=self.theme.get_color("bg_secondary"))
        gpu_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(
            gpu_frame,
            text="Use GPU for OCR:",
            bg=self.theme.get_color("bg_secondary"),
            fg=self.theme.get_color("text_primary"),
            font=self.theme.get_font("normal"),
        ).pack(side="left")

        self.gpu_var = tk.BooleanVar()
        gpu_check = tk.Checkbutton(
            gpu_frame,
            variable=self.gpu_var,
            bg=self.theme.get_color("bg_secondary"),
            fg=self.theme.get_color("text_primary"),
            selectcolor=self.theme.get_color("bg_tertiary"),
            activebackground=self.theme.get_color("bg_secondary"),
            command=self.on_change,
        )
        gpu_check.pack(side="right", padx=5)

    def create_bottom_buttons(self, parent):
        """สร้างปุ่มด้านล่าง"""
        button_frame = tk.Frame(parent, bg=self.theme.get_color("bg_primary"))
        button_frame.pack(fill="x", pady=(20, 0))

        # Save button
        self.save_button = ModernButton.create(
            button_frame, text="Save", command=self.save_settings, width=10
        )
        self.save_button.pack(side="right", padx=(10, 0))

        # Check Status button
        check_button = ModernButton.create(
            button_frame,
            text="Check Status",
            command=self.check_resolution_status,  # เปลี่ยนกลับมาใช้ method หลัก
            width=12,
        )
        check_button.pack(side="right")

    def setup_drag_events(self, widget):
        """Setup drag functionality for a widget"""

        def start_drag(event):
            self.dragging = True
            self.start_x = event.x_root
            self.start_y = event.y_root

        def drag_window(event):
            if self.dragging:
                # Calculate new position
                delta_x = event.x_root - self.start_x
                delta_y = event.y_root - self.start_y

                # Get current window position
                current_x = self.advance_window.winfo_x()
                current_y = self.advance_window.winfo_y()

                # Set new position
                new_x = current_x + delta_x
                new_y = current_y + delta_y

                self.advance_window.geometry(f"+{new_x}+{new_y}")

                # Update start position for next movement
                self.start_x = event.x_root
                self.start_y = event.y_root

        def end_drag(event):
            self.dragging = False

        widget.bind("<Button-1>", start_drag)
        widget.bind("<B1-Motion>", drag_window)
        widget.bind("<ButtonRelease-1>", end_drag)

    def load_current_settings(self):
        """โหลดค่าปัจจุบันจาก settings"""
        # Screen resolution
        screen_size = self.settings.get("screen_size", "2560x1440")
        width, height = screen_size.split("x")
        self.screen_width_var.set(width)
        self.screen_height_var.set(height)

        # Display scale
        scale = self.settings.get_display_scale()
        if scale:
            scale_percent = int(scale * 100)
            self.scale_var.set(f"{scale_percent}%")
        else:
            self.scale_var.set("100%")

        # GPU setting
        self.gpu_var.set(self.settings.get("use_gpu_for_ocr", False))

        # CPU Limit setting
        cpu_limit = self.settings.get("cpu_limit", 100)
        self.cpu_limit_var.set(cpu_limit)
        self.update_cpu_buttons(cpu_limit)

        # Set initial resolution display (don't auto-check to avoid slowdown)
        self.current_res_label.config(
            text="Click 'Check Status' to detect",
            fg=self.theme.get_color("text_secondary"),
        )

        # Reset change flag
        self.is_changed = False
        self.update_save_button()

    def on_change(self, event=None):
        """Mark settings as changed"""
        self.is_changed = True
        self.update_save_button()

    def update_save_button(self):
        """Update save button state based on changes"""
        if hasattr(self, "save_button"):
            if self.is_changed:
                self.save_button.config(
                    text="SAVE",
                    bg=self.theme.get_color("active_bg"),
                    fg=self.theme.get_color("active_text"),  # สีดำ
                    activebackground=self.theme.get_color("active_bg"),
                    activeforeground=self.theme.get_color("active_text"),  # สีดำ
                )
            else:
                self.save_button.config(
                    text="Save",
                    bg=self.theme.get_color("bg_secondary"),
                    fg=self.theme.get_color("text_primary"),  # สีขาว
                    activebackground=self.theme.get_color("hover_light"),
                    activeforeground=self.theme.get_color("text_primary"),  # สีขาว
                )

    def check_resolution_status(self):
        """ตรวจสอบสถานะความละเอียดหน้าจอและปรับค่า combobox อัติโนมัติ"""
        print("🔍 [DEBUG] Check resolution status called")
        try:
            self.current_res_label.config(
                text="Checking...", fg=self.theme.get_color("text_secondary")
            )
            self.advance_window.update()  # Force update UI

            # ลอง method หลักก่อน
            try:
                screen_info = self.get_true_screen_info()
                print(f"🔍 [DEBUG] Screen info from main method: {screen_info}")
            except Exception as e:
                print(f"🔍 [DEBUG] Main method failed, trying simple method: {e}")
                screen_info = self.get_simple_screen_info()
                print(f"🔍 [DEBUG] Screen info from simple method: {screen_info}")

            current_width = screen_info["physical_width"]
            current_height = screen_info["physical_height"]
            current_scale = screen_info["scale_factor"]
            method = screen_info["detection_method"]

            # บันทึกค่าใน combobox ก่อนการปรับ
            old_width = self.screen_width_var.get()
            old_height = self.screen_height_var.get()
            old_scale = self.scale_var.get()

            print(
                f"🔍 [DEBUG] Detected: {current_width}x{current_height}, Scale: {current_scale}, Method: {method}"
            )
            print(
                f"🔍 [DEBUG] Current settings: {old_width}x{old_height}, Scale: {old_scale}"
            )

            # *** AUTO-UPDATE COMBOBOX VALUES ***
            self.screen_width_var.set(str(current_width))
            self.screen_height_var.set(str(current_height))

            # ปรับ scale เป็น percentage
            scale_percent = int(current_scale * 100)
            self.scale_var.set(f"{scale_percent}%")

            # แสดงผลลัพธ์ใน label
            result_text = f"{current_width}x{current_height} ({scale_percent}%)"
            self.current_res_label.config(
                text=result_text, fg=self.theme.get_color("success")
            )

            # *** ตรวจสอบการเปลี่ยนแปลง ***
            settings_changed = (
                old_width != str(current_width)
                or old_height != str(current_height)
                or old_scale != f"{scale_percent}%"
            )

            if settings_changed:
                # มีการเปลี่ยนแปลง - ทำให้ปุ่ม save เปลี่ยนสถานะ
                self.on_change()

                # แสดงข้อความเตือน
                warning_msg = (
                    f"Settings Updated Automatically!\n\n"
                    f"Detected Resolution: {current_width}x{current_height}\n"
                    f"Detected Scale: {scale_percent}%\n"
                    f"Previous Settings: {old_width}x{old_height}, {old_scale}\n\n"
                    f"⚠️ IMPORTANT: Please click 'Save' to apply these settings.\n"
                    f"Incorrect screen settings will cause OCR detection errors!"
                )

                messagebox.showwarning("Screen Settings Updated", warning_msg)

            else:
                # ไม่มีการเปลี่ยนแปลง
                messagebox.showinfo(
                    "Screen Check",
                    f"Screen settings are correct!\n\n"
                    f"Current Resolution: {result_text}\n"
                    f"Detection Method: {method}",
                )

            print(f"✅ [DEBUG] Resolution check completed: {result_text}")

        except Exception as e:
            error_msg = f"Detection Failed: {str(e)}"
            print(f"❌ [ERROR] Resolution check failed: {e}")
            import traceback

            print(f"❌ [ERROR] Traceback: {traceback.format_exc()}")

            self.current_res_label.config(
                text=error_msg, fg=self.theme.get_color("error")
            )

            # แสดง error popup
            messagebox.showerror(
                "Screen Check Error", f"Failed to detect screen resolution:\n{str(e)}"
            )

    def save_settings(self):
        """Save current settings with validation"""
        try:
            # ตรวจสอบความถูกต้องของค่าที่จะบันทึก
            user_width = int(self.screen_width_var.get())
            user_height = int(self.screen_height_var.get())
            scale_text = self.scale_var.get().rstrip("%")
            user_scale = float(scale_text) / 100.0 if scale_text else 1.0

            # ตรวจสอบกับค่าจริงของหน้าจอ
            try:
                screen_info = self.get_true_screen_info()
                actual_width = screen_info["physical_width"]
                actual_height = screen_info["physical_height"]
                actual_scale = screen_info["scale_factor"]

                # ตรวจสอบความแตกต่าง
                width_diff = abs(user_width - actual_width)
                height_diff = abs(user_height - actual_height)
                scale_diff = abs(user_scale - actual_scale)

                # ถ้าแตกต่างมาก ให้เตือน
                tolerance = 0.05  # 5% tolerance
                if (
                    width_diff > actual_width * tolerance
                    or height_diff > actual_height * tolerance
                    or scale_diff > 0.1
                ):  # 10% tolerance สำหรับ scale

                    warning_msg = (
                        f"⚠️ CRITICAL WARNING ⚠️\n\n"
                        f"Screen settings do not match actual display:\n\n"
                        f"Your Settings: {user_width}x{user_height} ({int(user_scale*100)}%)\n"
                        f"Actual Display: {actual_width}x{actual_height} ({int(actual_scale*100)}%)\n\n"
                        f"🚨 This WILL cause OCR detection errors!\n"
                        f"The program cannot translate text correctly with wrong screen settings.\n\n"
                        f"Do you want to:\n"
                        f"• Click 'Yes' to save anyway (NOT RECOMMENDED)\n"
                        f"• Click 'No' to use correct detection values"
                    )

                    result = messagebox.askyesno(
                        "Screen Settings Mismatch", warning_msg, icon="warning"
                    )

                    if not result:
                        # ผู้ใช้เลือก No - ปรับใช้ค่าที่ถูกต้อง
                        self.screen_width_var.set(str(actual_width))
                        self.screen_height_var.set(str(actual_height))
                        self.scale_var.set(f"{int(actual_scale * 100)}%")
                        messagebox.showinfo(
                            "Settings Corrected",
                            f"Settings have been corrected to:\n"
                            f"{actual_width}x{actual_height} ({int(actual_scale*100)}%)",
                        )
                        return  # ไม่บันทึกแต่ให้ผู้ใช้กด save อีกครั้ง

            except:
                # ถ้าตรวจสอบไม่ได้ ให้ดำเนินการปกติ
                pass

            # บันทึกการตั้งค่า
            screen_size = f"{user_width}x{user_height}"
            self.settings.set_screen_size(screen_size)

            # Save CPU limit setting
            cpu_limit_value = self.cpu_limit_var.get()
            self.settings.set_cpu_limit(cpu_limit_value)

            # Save display scale
            if scale_text:
                self.settings.set_display_scale(user_scale)

            # Save GPU setting
            self.settings.set_gpu_for_ocr(self.gpu_var.get())

            # Apply settings through callback
            if self.apply_settings_callback:
                advance_settings = {
                    "screen_size": screen_size,
                    "display_scale": user_scale,
                    "use_gpu_for_ocr": self.gpu_var.get(),
                    "cpu_limit": cpu_limit_value,
                }
                self.apply_settings_callback(advance_settings)

            # บังคับให้บันทึกการตั้งค่าทั้งหมดลงไฟล์ settings.json
            self.settings.save_settings()

            # Show success feedback
            self.show_save_feedback()
            self.is_changed = False
            self.update_save_button()

        except Exception as e:
            print(f"❌ Save settings failed: {e}")
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")

    def show_save_feedback(self):
        """แสดง feedback การบันทึก"""
        if hasattr(self, "save_button"):
            original_text = self.save_button.cget("text")
            self.save_button.config(
                text="✓ Saved!",
                bg=self.theme.get_color("success"),
                fg="white",  # ใช้สีขาวสำหรับปุ่ม success
                activebackground=self.theme.get_color("success"),
                activeforeground="white",
            )

            # รีเซ็ตหลัง 2 วินาที
            self.advance_window.after(
                2000, lambda: self.reset_save_button(original_text)
            )

    def reset_save_button(self, original_text):
        """รีเซ็ตปุ่ม save"""
        if hasattr(self, "save_button") and self.save_button.winfo_exists():
            if self.is_changed:
                # ยังคงมีการเปลี่ยนแปลง
                self.save_button.config(
                    text=original_text,
                    bg=self.theme.get_color("active_bg"),
                    fg=self.theme.get_color("active_text"),
                    activebackground=self.theme.get_color("active_bg"),
                    activeforeground=self.theme.get_color("active_text"),
                )
            else:
                # ไม่มีการเปลี่ยนแปลง
                self.save_button.config(
                    text=original_text,
                    bg=self.theme.get_color("bg_secondary"),
                    fg=self.theme.get_color("text_primary"),
                    activebackground=self.theme.get_color("hover_light"),
                    activeforeground=self.theme.get_color("text_primary"),
                )

    def open(self):
        """Show the advanced settings window"""
        if not self.advance_window.winfo_viewable():
            # Position window
            x = self.parent.winfo_x() + self.parent.winfo_width() + 10
            y = self.parent.winfo_y()
            self.advance_window.geometry(f"+{x}+{y}")

            # Show window
            self.advance_window.deiconify()
            self.advance_window.lift()
            self.advance_window.attributes("-topmost", True)

            # Reset state
            self.load_current_settings()
            self.is_changed = False
            self.update_save_button()

    def close(self):
        """Hide the advanced settings window"""
        if self.advance_window and self.advance_window.winfo_exists():
            self.advance_window.withdraw()
            self.is_changed = False
            if hasattr(self, "save_button"):
                self.save_button.config(
                    text="Save",
                    bg=self.theme.get_color("bg_secondary"),
                    fg=self.theme.get_color("text_primary"),
                    activebackground=self.theme.get_color("hover_light"),
                    activeforeground=self.theme.get_color("text_primary"),
                )
