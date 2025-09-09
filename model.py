import tkinter as tk
from tkinter import ttk, messagebox, font
import logging
from utils_appearance import SettingsUITheme, ModernButton, ModernEntry, ModernFrame
import os
from dotenv import load_dotenv, set_key

# เพิ่ม import สำหรับการจัดการไฟล์
import os.path


class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.id = None
        self.x = self.y = 0

        # ผูกเหตุการณ์ทั้งหมดที่จำเป็น
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
        self.widget.bind("<ButtonPress>", self.on_leave)
        self.widget.bind("<Motion>", self.on_motion)  # เพิ่มการติดตามการเคลื่อนไหวของเมาส์

    def on_enter(self, event=None):
        # กำหนดเวลาแสดง tooltip เมื่อเมาส์เข้า widget
        self.schedule()

    def on_leave(self, event=None):
        # ยกเลิกการแสดง tooltip เมื่อเมาส์ออกหรือคลิก
        self.unschedule()
        self.hide_tooltip()

    def on_motion(self, event=None):
        # อัพเดตตำแหน่งเมาส์เมื่อมีการเคลื่อนไหว
        self.x = event.x
        self.y = event.y

    def schedule(self):
        # ตั้งเวลาแสดง tooltip
        self.unschedule()
        self.id = self.widget.after(500, self.show_tooltip)  # 500ms = 0.5 วินาที

    def unschedule(self):
        # ยกเลิกการตั้งเวลา
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None

    def show_tooltip(self):
        # แสดง tooltip
        if self.tip_window:
            return

        # คำนวณตำแหน่งที่จะแสดง tooltip
        x = self.widget.winfo_rootx() + self.x + 15
        y = self.widget.winfo_rooty() + self.y + 10

        # สร้างหน้าต่าง tooltip
        self.tip_window = tk.Toplevel(self.widget)
        self.tip_window.wm_overrideredirect(True)  # ไม่แสดงเฟรมหน้าต่าง
        self.tip_window.wm_geometry(f"+{x}+{y}")

        # สร้างกรอบและป้ายข้อความ
        frame = tk.Frame(
            self.tip_window,
            bg=SettingsUITheme.COLORS["bg_secondary"],
            bd=1,
            relief=tk.SOLID,
        )
        frame.pack(fill=tk.BOTH, expand=True)

        label = tk.Label(
            frame,
            text=self.text,
            font=("Bai Jamjuree Light", 12),
            bg=SettingsUITheme.COLORS["bg_secondary"],
            fg=SettingsUITheme.COLORS["text_primary"],
            justify=tk.LEFT,
            padx=10,
            pady=8,
            wraplength=350,
        )
        label.pack()

        # ตั้งค่า attributes เพื่อให้ tooltip อยู่เหนือหน้าต่างอื่น
        self.tip_window.attributes("-topmost", True)

        # เพิ่ม event binding เมื่อหน้าต่างหลักถูกเคลื่อนย้าย ให้ tooltip หายไป
        self.widget.winfo_toplevel().bind("<Configure>", lambda e: self.hide_tooltip())

    def hide_tooltip(self):
        # ซ่อน tooltip
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


# ฟังก์ชันสร้าง tooltip
def add_tooltip(widget, text):
    """สร้าง tooltip สำหรับ widget ที่กำหนด"""
    return ToolTip(widget, text)


class ModelSettings:
    def __init__(
        self,
        parent,
        settings,
        apply_settings_callback,
        main_app=None,
        on_close_callback=None,
    ):
        self.parent = parent
        self.settings = settings
        self.apply_settings_callback = apply_settings_callback
        self.is_adjusting_scale = False
        self.on_close_callback = on_close_callback  # เพิ่มบรรทัดนี้

        # โหลด .env ถ้ามี
        load_dotenv()

        # ตรวจสอบว่า main_app มีเมธอด update_api_settings หรือไม่
        if main_app and hasattr(main_app, "update_api_settings"):
            self.main_app = main_app
            logging.info("ModelSettings: main_app with update_api_settings found")
        else:
            if main_app:
                logging.warning(
                    "ModelSettings: main_app does not have update_api_settings"
                )
            else:
                logging.warning("ModelSettings: main_app not provided")
            self.main_app = main_app

        self.model_window = None
        self.window_created = False

    def create_model_window(self):
        if self.model_window is None or not self.model_window.winfo_exists():
            self.model_window = tk.Toplevel(self.parent)
            self.model_window.title("Model Settings")
            self.model_window.geometry("420x680")  # ลดความสูงลงเพื่อให้กระชับ
            self.model_window.overrideredirect(True)
            self.model_window.configure(bg=SettingsUITheme.COLORS["bg_primary"])

            # Main Container - ลด padding
            main_container = tk.Frame(
                self.model_window, bg=SettingsUITheme.COLORS["bg_primary"]
            )
            main_container.pack(expand=True, fill=tk.BOTH, padx=8, pady=8)

            # === Header section ===
            self.create_header_section(main_container)

            # === API Keys Section ===
            self.create_api_keys_section(main_container)

            # === Parameters Section (แสดงทั้งหมด ไม่มี toggle) ===
            self.create_parameters_section(main_container)

            # Window movement
            self.model_window.bind("<Button-1>", self.start_move)
            self.model_window.bind("<ButtonRelease-1>", self.stop_move)
            self.model_window.bind("<B1-Motion>", self.do_move)

            self.window_created = True
            self.model_window.withdraw()

            # ผูก Protocol การปิดหน้าต่างเข้ากับ handle_close
            self.model_window.protocol("WM_DELETE_WINDOW", self.handle_close)

            self.window_created = True
            self.model_window.withdraw()

            # ตัวแปรเก็บค่าเริ่มต้นสำหรับเปรียบเทียบ
            self.original_values = {}

            # Load current settings
            self.load_current_settings()

    def handle_close(self):
        """จัดการการปิดหน้าต่างและเรียก callback กลับไปที่ parent"""
        # เรียก callback ที่ได้รับมาจาก parent (ถ้ามี)
        if self.on_close_callback:
            self.on_close_callback()

        # ซ่อนหน้าต่าง (เหมือนที่ฟังก์ชัน close() ทำ)
        self.close()

    def create_header_section(self, parent):
        """สร้างส่วนหัวของหน้าต่าง - ปรับ layout ให้สมดุลและดูเป็นมืออาชีพ"""
        header_frame = tk.Frame(parent, bg=SettingsUITheme.COLORS["bg_primary"])
        header_frame.pack(fill=tk.X, pady=(0, 8))  # ลด pady

        # ส่วนหัวข้อและปุ่มปิด - ใช้ grid สำหรับ layout ที่ดีกว่า
        title_frame = tk.Frame(header_frame, bg=SettingsUITheme.COLORS["bg_primary"])
        title_frame.pack(fill=tk.X, pady=(4, 0))  # ลด pady

        # ตั้งค่า grid weights เพื่อให้ชื่ออยู่กึ่งกลาง
        title_frame.grid_columnconfigure(0, weight=1)  # ช่องว่างซ้าย
        title_frame.grid_columnconfigure(1, weight=0)  # ชื่อ
        title_frame.grid_columnconfigure(2, weight=1)  # ช่องว่างขวา (มีปุ่มปิด)

        # ชื่อหน้าต่าง - จัดกึ่งกลาง
        title_label = tk.Label(
            title_frame,
            text="Model & API Settings",
            font=("Bai Jamjuree Light", 16, "bold"),
            bg=SettingsUITheme.COLORS["bg_primary"],
            fg=SettingsUITheme.COLORS["text_primary"],
        )
        title_label.grid(row=0, column=1, pady=4)  # ลด pady

        # ปุ่มปิด - ปรับปรุงให้เล็กลงและชิดบนขวามากกว่า
        self.close_button = tk.Button(
            title_frame,
            text="✕",
            command=self.handle_close,  # <--- แก้ไขตรงนี้ จาก self.close เป็น self.handle_close
            bg=SettingsUITheme.COLORS["bg_primary"],
            fg="white",
            font=("Bai Jamjuree Light", 14, "bold"),
            bd=0,
            padx=8,
            pady=4,
            cursor="hand2",
            relief="flat",
        )
        self.close_button.grid(
            row=0, column=2, sticky="ne", padx=(0, 4), pady=2
        )  # ชิดขวามากกว่า

        # เพิ่ม hover effect แบบ formal สำหรับปุ่มปิด
        def on_close_enter(e):
            self.close_button.config(bg="#dc3545", relief="solid", bd=1)

        def on_close_leave(e):
            self.close_button.config(
                bg=SettingsUITheme.COLORS["bg_primary"], relief="flat", bd=0
            )

        self.close_button.bind("<Enter>", on_close_enter)
        self.close_button.bind("<Leave>", on_close_leave)

        # Model Selection - จัดกึ่งกลาง (ลบ label "AI Model:")
        model_frame = tk.Frame(header_frame, bg=SettingsUITheme.COLORS["bg_primary"])
        model_frame.pack(fill=tk.X, pady=(8, 0))  # ลด pady

        # Container สำหรับ combobox เพื่อจัดกึ่งกลาง - ไม่มี label
        combo_container = tk.Frame(model_frame, bg=SettingsUITheme.COLORS["bg_primary"])
        combo_container.pack()

        self.model_var = tk.StringVar()
        
        # ลบ debug logs ตามคำขอ
        model_options = list(self.settings.VALID_MODELS.keys())

        self.model_combo = ttk.Combobox(
            combo_container,
            values=model_options,
            textvariable=self.model_var,
            width=25,
            state="readonly",
            font=("Bai Jamjuree Light", 12),
        )
        self.model_combo.pack()
        self.model_combo.bind("<<ComboboxSelected>>", self.on_model_change)

        # Style combobox ให้เป็นสีเทาเข้มตั้งแต่เริ่มต้น
        self.configure_combobox_style()

    def configure_combobox_style(self):
        """กำหนด style ของ combobox ให้เป็นสีเทาเข้มและฟอนต์ที่เหมาะสม"""
        style = ttk.Style()
        style.theme_use("clam")

        # Configure combobox style
        style.configure(
            "Dark.TCombobox",
            fieldbackground=SettingsUITheme.COLORS["bg_tertiary"],
            background=SettingsUITheme.COLORS["bg_tertiary"],
            foreground=SettingsUITheme.COLORS["text_primary"],
            borderwidth=1,
            relief="solid",
            arrowcolor=SettingsUITheme.COLORS["text_primary"],
            font=("Bai Jamjuree Light", 12),
        )

        # Configure dropdown listbox
        style.map(
            "Dark.TCombobox",
            fieldbackground=[
                ("readonly", SettingsUITheme.COLORS["bg_tertiary"]),
                ("focus", SettingsUITheme.COLORS["bg_tertiary"]),
            ],
            selectbackground=[("readonly", SettingsUITheme.COLORS["bg_tertiary"])],
            selectforeground=[("readonly", SettingsUITheme.COLORS["text_primary"])],
            background=[("readonly", SettingsUITheme.COLORS["bg_tertiary"])],
        )

        # Apply style to combobox
        self.model_combo.configure(style="Dark.TCombobox")

    def create_api_keys_section(self, parent):
        """สร้างส่วน API Keys - แสดงเฉพาะของโมเดลที่เลือก"""
        # API Keys Card
        self.api_card = tk.Frame(
            parent, bg=SettingsUITheme.COLORS["bg_secondary"], relief="solid", bd=1
        )
        self.api_card.pack(fill=tk.X, pady=(0, 8))  # ลด pady

        # หัวข้อส่วน API Keys
        api_header_frame = tk.Frame(
            self.api_card, bg=SettingsUITheme.COLORS["bg_secondary"]
        )
        api_header_frame.pack(fill=tk.X, padx=12, pady=(8, 4))  # ลด pady

        api_header = tk.Label(
            api_header_frame,
            text="API Keys",
            bg=SettingsUITheme.COLORS["bg_secondary"],
            fg=SettingsUITheme.COLORS["text_primary"],
            font=("Bai Jamjuree Light", 12, "bold"),  # ลดขนาดฟอนต์
        )
        api_header.pack(side=tk.LEFT)

        # ปุ่ม Apply ด้านขวา
        self.apply_button = ModernButton(
            api_header_frame, text="APPLY", command=self.apply_settings
        )
        self.apply_button.pack(side=tk.RIGHT)
        self.apply_button.button.config(state=tk.DISABLED)

        # ตัวแปร API Keys - เหลือแค่ Google
        self.google_key_var = tk.StringVar(
            value=self._mask_api_key(os.getenv("GEMINI_API_KEY", ""))
        )

        # Initialize entry references - เหลือแค่ Google
        self.google_key_entry = None

        # Container สำหรับ API Keys (จะเปลี่ยนตามโมเดล)
        self.api_keys_container = tk.Frame(
            self.api_card, bg=SettingsUITheme.COLORS["bg_secondary"]
        )
        self.api_keys_container.pack(fill=tk.X, padx=12, pady=(0, 8))  # ลด pady

        # ข้อมูลเพิ่มเติม
        info_frame = tk.Frame(self.api_card, bg=SettingsUITheme.COLORS["bg_secondary"])
        info_frame.pack(fill=tk.X, padx=12, pady=(4, 8))  # ลด pady

        info_label = tk.Label(
            info_frame,
            text="💡 หากเห็น ••• แสดงว่ามี API Key อยู่แล้ว",
            font=("Bai Jamjuree Light", 10),  # ลดขนาดฟอนต์
            bg=SettingsUITheme.COLORS["bg_secondary"],
            fg=SettingsUITheme.COLORS["text_secondary"],
        )
        info_label.pack(anchor="w")

        detailed_info = (
            "API Key ใช้สำหรับเชื่อมต่อ AI models จากค่ายต่างๆ\n"
            "• หากเห็น ••• หมายความว่ามี key อยู่แล้ว\n"
            "• กรอก API KEY ให้ตรงกับผู้ให้บริการ\n"
            "• หากไม่จำเป็นต้องเปลี่ยน ห้ามแก้ไข!"
        )
        add_tooltip(info_label, detailed_info)

    def update_api_keys_display(self, selected_model):
        """อัปเดตการแสดงผล API Keys ตามโมเดลที่เลือก - แก้ปัญหาแสดงทุก API Key"""
        # ล้าง container เดิม
        for widget in self.api_keys_container.winfo_children():
            widget.destroy()

        # กำหนดข้อมูล API Key ตามโมเดล
        api_key_info = self.get_api_key_info_for_model(selected_model)

        if api_key_info:
            label_text, key_var, tooltip_text = api_key_info

            entry_frame = tk.Frame(
                self.api_keys_container, bg=SettingsUITheme.COLORS["bg_secondary"]
            )
            entry_frame.pack(fill=tk.X, pady=4)

            label = tk.Label(
                entry_frame,
                text=label_text,
                font=("Bai Jamjuree Light", 13, "bold"),
                bg=SettingsUITheme.COLORS["bg_secondary"],
                fg=SettingsUITheme.COLORS["text_primary"],
                width=18,
                anchor="w",
            )
            label.pack(side=tk.LEFT)

            # สร้าง entry สำหรับ API key พร้อมฟอนต์ใหญ่กว่าปกติ
            entry = ModernEntry(entry_frame, textvariable=key_var, show="*", width=35)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0))

            # ปรับแต่ง entry ให้มีฟอนต์ใหญ่กว่าปกติและ auto-select เมื่อคลิก
            entry.entry.config(font=("Bai Jamjuree Light", 14))
            entry.entry.bind("<KeyRelease>", self.check_for_changes)
            entry.entry.bind("<FocusIn>", self._on_api_key_focus)
            entry.entry.bind("<Button-1>", self._on_api_key_click)

            # เก็บ reference ของ entry
            self.google_key_entry = entry

            # เพิ่ม tooltip
            add_tooltip(label, tooltip_text)

    def _on_api_key_focus(self, event):
        """จัดการเมื่อ API key entry ได้รับ focus - auto select ทั้งหมด"""
        event.widget.select_range(0, tk.END)
        event.widget.icursor(tk.END)  # ย้าย cursor ไปท้าย

    def _on_api_key_click(self, event):
        """จัดการเมื่อคลิกที่ API key entry - auto select ทั้งหมดทันที"""
        # ใช้ after เพื่อให้แน่ใจว่าการคลิกเสร็จสิ้นก่อน
        event.widget.after(10, lambda: event.widget.select_range(0, tk.END))

    def get_api_key_info_for_model(self, model_name):
        """ดึงข้อมูล API Key ตามโมเดลที่เลือก - เหลือแค่ Gemini"""
        # เนื่องจากใช้แค่ Gemini แล้ว ให้ return Google API key เสมอ
        return ("Google AI API Key:", self.google_key_var, "สำหรับ Gemini models")

    def create_parameters_section(self, parent):
        """สร้างส่วนพารามิเตอร์แบบ compact ในหน้าเดียว"""
        # Parameters Card
        params_card = tk.Frame(
            parent, bg=SettingsUITheme.COLORS["bg_secondary"], relief="solid", bd=1
        )
        params_card.pack(fill=tk.BOTH, expand=True, pady=(2, 0))

        # หัวข้อส่วน Parameters
        params_header = tk.Label(
            params_card,
            text="Model Parameters",
            bg=SettingsUITheme.COLORS["bg_secondary"],
            fg=SettingsUITheme.COLORS["text_primary"],
            font=("Bai Jamjuree Light", 12, "bold"),
        )
        params_header.pack(pady=(6, 2))

        # Container สำหรับพารามิเตอร์
        self.params_container = tk.Frame(
            params_card, bg=SettingsUITheme.COLORS["bg_secondary"]
        )
        self.params_container.pack(fill=tk.BOTH, expand=True, padx=6, pady=(0, 6))

        # สร้าง Frame สำหรับพารามิเตอร์ของ Gemini เท่านั้น
        self.gemini_frame = tk.Frame(
            self.params_container, bg=SettingsUITheme.COLORS["bg_secondary"]
        )

        # สร้าง parameters สำหรับ Gemini เท่านั้น
        self.create_compact_gemini_parameters()

        # ลงทะเบียนการ track การเปลี่ยนแปลงของพารามิเตอร์
        self.setup_parameter_tracking()

    def _create_compact_parameter_control(
        self,
        parent,
        title,
        hint,
        description,
        value,
        min_val,
        max_val,
        step,
        value_var_name,
        scale_var_name,
        update_func,
        adjust_minus,
        adjust_plus,
    ):
        """ฟังก์ชันช่วยในการสร้าง control แบบ compact สำหรับพารามิเตอร์"""
        # สร้าง frame สำหรับพารามิเตอร์ - compact
        param_frame = tk.Frame(parent, bg=SettingsUITheme.COLORS["bg_secondary"])
        param_frame.pack(fill=tk.X, pady=1, padx=2)  # ลด pady เหลือ 1

        # ส่วนหัวข้อและค่าปัจจุบัน - จัดแนวนอน
        header = tk.Frame(param_frame, bg=SettingsUITheme.COLORS["bg_secondary"])
        header.pack(fill=tk.X)

        # ชื่อพารามิเตอร์และค่าในบรรทัดเดียว
        title_label = tk.Label(
            header,
            text=title,
            font=("Bai Jamjuree Light", 10, "bold"),  # ลดฟอนต์
            bg=SettingsUITheme.COLORS["bg_secondary"],
            fg=SettingsUITheme.COLORS["text_primary"],
        )
        title_label.pack(side=tk.LEFT)

        # ค่าปัจจุบัน
        value_label = tk.Label(
            header,
            text=str(value),
            font=("Bai Jamjuree Light", 10, "bold"),  # ลดฟอนต์
            bg=SettingsUITheme.COLORS["bg_secondary"],
            fg=SettingsUITheme.COLORS["success"],
            width=6,
        )
        value_label.pack(side=tk.RIGHT)

        # ค่าที่แนะนำ - บรรทัดใหม่
        hint_label = tk.Label(
            param_frame,
            text=f"{description} {hint}",
            font=("Bai Jamjuree Light", 8),  # ลดฟอนต์
            bg=SettingsUITheme.COLORS["bg_secondary"],
            fg=SettingsUITheme.COLORS["text_secondary"],
        )
        hint_label.pack(anchor="w", pady=(0, 1))  # ลด pady

        # Scale control - compact
        scale_frame = tk.Frame(param_frame, bg=SettingsUITheme.COLORS["bg_secondary"])
        scale_frame.pack(fill=tk.X, pady=1)

        # ปุ่มลด
        minus_btn = tk.Button(
            scale_frame,
            text=f"-{step}",
            bg=SettingsUITheme.COLORS["bg_tertiary"],
            fg=SettingsUITheme.COLORS["text_primary"],
            bd=0,
            padx=2,  # ลดขนาด
            pady=0,  # ลดขนาด
            font=("Bai Jamjuree Light", 8),  # ลดฟอนต์
            command=adjust_minus,
        )
        minus_btn.pack(side=tk.LEFT)

        # Scale
        scale = tk.Scale(
            scale_frame,
            from_=min_val,
            to=max_val,
            orient=tk.HORIZONTAL,
            resolution=step,
            bg=SettingsUITheme.COLORS["bg_secondary"],
            fg=SettingsUITheme.COLORS["text_primary"],
            highlightthickness=0,
            command=update_func,
            troughcolor=SettingsUITheme.COLORS["bg_tertiary"],
            activebackground=SettingsUITheme.COLORS["success"],
            bd=0,
            sliderrelief=tk.FLAT,
            sliderlength=12,  # ลดขนาด
            takefocus=1,
            length=160,  # ลดขนาด
        )
        scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)  # ลด padx
        scale.set(value)

        # ปุ่มเพิ่ม
        plus_btn = tk.Button(
            scale_frame,
            text=f"+{step}",
            bg=SettingsUITheme.COLORS["bg_tertiary"],
            fg=SettingsUITheme.COLORS["text_primary"],
            bd=0,
            padx=2,  # ลดขนาด
            pady=0,  # ลดขนาด
            font=("Bai Jamjuree Light", 8),  # ลดฟอนต์
            command=adjust_plus,
        )
        plus_btn.pack(side=tk.RIGHT)

        # บันทึกตัวแปรไว้ใน instance
        setattr(self, value_var_name, value_label)
        setattr(self, scale_var_name, scale)

        # ผูกอีเวนต์ scale อย่างถูกต้อง - แก้ไขให้เป็นฟังก์ชันที่ถูกต้อง
        scale.bind("<ButtonPress-1>", self.lock_movement_during_scale)
        scale.bind("<ButtonRelease-1>", self.unlock_movement_after_scale)

        # เพิ่ม binding เพื่อให้การอัปเดทค่าทำงานอย่างถูกต้อง
        scale.bind("<Motion>", lambda e: update_func(scale.get()))
        scale.bind("<Button-1>", lambda e: update_func(scale.get()))

        return scale

    def create_compact_gemini_parameters(self):
        """สร้าง UI แบบ compact สำหรับพารามิเตอร์ของโมเดล Gemini"""

        # === Max Tokens ===
        self._create_compact_parameter_control(
            parent=self.gemini_frame,
            title="Max Tokens:",
            hint="(50-800)",
            description="ความยาวข้อความที่จะสร้าง",
            value=500,
            min_val=50,
            max_val=800,
            step=25,
            value_var_name="gemini_token_value_label",
            scale_var_name="gemini_max_tokens",
            update_func=lambda val: self.update_gemini_value_labels("tokens", val),
            adjust_minus=lambda: self.adjust_gemini_value("tokens", -25),
            adjust_plus=lambda: self.adjust_gemini_value("tokens", 25),
        )

        # === Temperature ===
        self._create_compact_parameter_control(
            parent=self.gemini_frame,
            title="Temperature:",
            hint="(0.1-1.0)",
            description="ความสร้างสรรค์",
            value=0.8,
            min_val=0.1,
            max_val=1.0,
            step=0.05,
            value_var_name="gemini_temp_value_label",
            scale_var_name="gemini_temperature",
            update_func=lambda val: self.update_gemini_value_labels("temperature", val),
            adjust_minus=lambda: self.adjust_gemini_value("temperature", -0.05),
            adjust_plus=lambda: self.adjust_gemini_value("temperature", 0.05),
        )

        # === Top P ===
        self._create_compact_parameter_control(
            parent=self.gemini_frame,
            title="Top P:",
            hint="(0.1-1.0)",
            description="ความหลากหลายของคำ",
            value=0.9,
            min_val=0.1,
            max_val=1.0,
            step=0.05,
            value_var_name="gemini_top_p_value_label",
            scale_var_name="gemini_top_p",
            update_func=lambda val: self.update_gemini_value_labels("top_p", val),
            adjust_minus=lambda: self.adjust_gemini_value("top_p", -0.05),
            adjust_plus=lambda: self.adjust_gemini_value("top_p", 0.05),
        )

    def _get_detailed_description(self, title, description):
        """ให้คำอธิบายละเอียดสำหรับแต่ละพารามิเตอร์"""
        if "Max Tokens" in title:
            return """ความยาวข้อความที่จะสร้าง

    ค่าต่ำ: ข้อความสั้น ประหยัดการใช้ token
    ค่าสูง: ข้อความยาว รายละเอียดมากขึ้นสำหรับแปลข้อความเช่นบทความขนาดยาว

    แนะนำสำหรับการแปลเกม: 300-500 tokens"""

        elif "Temperature" in title:
            return """ระดับความแน่นอน/สร้างสรรค์ในการเลือกคำ

    ค่าต่ำ (0.1-0.3): ผลลัพธ์แน่นอน สม่ำเสมอ เหมาะกับข้อเท็จจริง
    ค่ากลาง (0.4-0.7): สมดุล เหมาะกับการแปลเกม
    ค่าสูง (0.8-1.0): สร้างสรรค์ หลากหลาย เหมาะกับเนื้อหาบรรยาย

    แนะนำสำหรับการแปลเกม: 0.6-0.7"""

        elif "Top P" in title:
            return """ความหลากหลายของคำศัพท์ที่เลือกใช้

    ค่าต่ำ: เลือกใช้คำศัพท์ที่พบบ่อย (คำปกติ)
    ค่าสูง: เพิ่มโอกาสใช้คำที่หลากหลาย (เบียวมากขึ้น)

    แนะนำสำหรับการแปลเกม: 0.8-0.9"""

        return description

    def _mask_api_key(self, key):
        """แสดง API Key แบบปกปิด (มาส์ก) ถ้ามีค่าอยู่แล้ว"""
        if key and len(key) > 0:
            return "•••••••••••••••"  # แสดงเป็น bullet points ถ้ามี key อยู่แล้ว
        return ""

    def _check_available_api_keys(self):
        """ตรวจสอบว่ามี Google API Key สำหรับ Gemini หรือไม่"""
        has_google = bool(os.getenv("GEMINI_API_KEY", "").strip())

        return {
            "google": has_google,
            "available": ["Google"] if has_google else [],
            "count": 1 if has_google else 0,
        }

    def _check_env_file_permissions(self):
        """ตรวจสอบสิทธิ์การเข้าถึงไฟล์ .env"""
        env_path = os.path.join(os.getcwd(), ".env")
        can_read = False
        can_write = False

        # ตรวจสอบการอ่าน
        try:
            if os.path.exists(env_path):
                with open(env_path, "r") as f:
                    f.read(1)  # ลองอ่าน 1 ไบต์แรก
                can_read = True
        except:
            pass

        # ตรวจสอบการเขียน
        if os.path.exists(env_path):
            try:
                # ทดสอบเปิดในโหมดเขียนแบบเพิ่มข้อมูล (ไม่ทำลายข้อมูลเดิม)
                with open(env_path, "a") as f:
                    pass
                can_write = True
            except:
                pass
        else:
            # ทดสอบสร้างไฟล์ใหม่
            try:
                parent_dir = os.path.dirname(env_path)
                if not os.path.exists(parent_dir):
                    os.makedirs(parent_dir, exist_ok=True)
                with open(env_path, "w") as f:
                    pass
                can_write = True
                # ลบไฟล์ทดสอบที่สร้างขึ้น
                os.remove(env_path)
            except:
                pass

        return {"can_read": can_read, "can_write": can_write, "path": env_path}

    def _update_env_file(self, env_vars):
        """บันทึกค่าลงในไฟล์ .env - รองรับเฉพาะ GEMINI_API_KEY"""
        # Path หลัก
        env_path = os.path.join(os.getcwd(), ".env")
        # Path สำรองในกรณีไม่มีสิทธิ์เขียน
        backup_env_path = os.path.join(os.getcwd(), ".env.user")

        # ดึงค่า Google API Key ปัจจุบัน
        current_env = {}

        # เพิ่ม Google API Key ที่ไม่ได้อยู่ในรายการอัปเดต (คงค่าเดิม)
        if "GEMINI_API_KEY" not in env_vars:
            current_env["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY", "")

        # เพิ่ม API Key ที่ต้องการอัปเดต
        for key, value in env_vars.items():
            current_env[key] = value

        # พยายามเขียนไฟล์หลัก (.env)
        try:
            with open(env_path, "w", encoding="utf-8") as f:
                for key, value in current_env.items():
                    f.write(f"{key}={value}\n")
            logging.info(f"บันทึกการเปลี่ยนแปลง API Key ลงในไฟล์ {env_path} สำเร็จ")
            return True
        except Exception as e:
            logging.warning(f"ไม่สามารถเขียนไฟล์ {env_path}: {e}")

            # พยายามเขียนไฟล์สำรอง (.env.user)
            try:
                with open(backup_env_path, "w", encoding="utf-8") as f:
                    for key, value in current_env.items():
                        f.write(f"{key}={value}\n")
                logging.info(
                    f"บันทึกการเปลี่ยนแปลง API Key ลงในไฟล์สำรอง {backup_env_path} สำเร็จ"
                )

                # ตั้งค่า environment variables สำหรับเซสชันปัจจุบัน
                for key, value in env_vars.items():
                    os.environ[key] = value

                return True
            except Exception as e2:
                logging.error(f"ไม่สามารถเขียนไฟล์สำรอง {backup_env_path}: {e2}")

                # ตั้งค่า environment variables สำหรับเซสชันปัจจุบัน (แม้จะไม่สามารถบันทึกลงไฟล์ได้)
                for key, value in env_vars.items():
                    os.environ[key] = value

                return False

    def show_parameter_frames(self, selected_model):
        """แสดง frame พารามิเตอร์ - เหลือแค่ Gemini"""
        # แสดง Gemini frame เสมอเพราะใช้แค่ Gemini
        self.gemini_frame.pack(fill=tk.X, padx=2, pady=2)

    def load_current_settings(self):
        """โหลดค่าปัจจุบันจาก settings - เหลือแค่ Gemini"""
        try:
            api_params = self.settings.get_api_parameters()
            displayed_model = self.settings.get_displayed_model()

            # ตั้งค่า model - ตรวจสอบว่าอยู่ในตัวเลือกที่มีหรือไม่
            # FIX: ดึงรายชื่อโมเดลที่ถูกต้องจาก Settings class โดยตรง
            valid_models = list(self.settings.VALID_MODELS.keys())

            if displayed_model in valid_models:
                self.model_var.set(displayed_model)
            else:
                # ถ้าไม่อยู่ในตัวเลือกที่มี ให้ใช้ค่าเริ่มต้นเป็น gemini-2.0-flash
                logging.info(f"โมเดลเดิม {displayed_model} ไม่อยู่ในตัวเลือกที่มี ใช้ค่าเริ่มต้นแทน")
                self.model_var.set("gemini-2.0-flash")

            # โหลด Google API Key จาก environment variables
            self.google_key_var.set(self._mask_api_key(os.getenv("GEMINI_API_KEY", "")))

            # โหลดค่าพารามิเตอร์
            max_tokens = api_params.get("max_tokens", 500)
            temperature = api_params.get("temperature", 0.8)
            top_p = api_params.get("top_p", 0.9)

            # อัพเดตค่าใน Gemini
            if hasattr(self, "gemini_max_tokens"):
                self.gemini_max_tokens.set(max_tokens)
            if hasattr(self, "gemini_temperature"):
                self.gemini_temperature.set(temperature)
            if hasattr(self, "gemini_top_p"):
                self.gemini_top_p.set(top_p)

            # อัพเดตค่า value labels สำหรับ Gemini
            if hasattr(self, "gemini_token_value_label"):
                self.gemini_token_value_label.config(text=str(max_tokens))
            if hasattr(self, "gemini_temp_value_label"):
                self.gemini_temp_value_label.config(text=str(temperature))
            if hasattr(self, "gemini_top_p_value_label"):
                self.gemini_top_p_value_label.config(text=str(top_p))

            # ตรวจสอบการผูก event สำหรับ Gemini
            if hasattr(self, "gemini_max_tokens"):
                self.gemini_max_tokens.config(
                    command=lambda val: self.update_gemini_value_labels("tokens", val)
                )
                self.gemini_max_tokens.bind(
                    "<ButtonPress-1>", self.lock_movement_during_scale
                )
                self.gemini_max_tokens.bind(
                    "<ButtonRelease-1>", self.unlock_movement_after_scale
                )
            if hasattr(self, "gemini_temperature"):
                self.gemini_temperature.config(
                    command=lambda val: self.update_gemini_value_labels(
                        "temperature", val
                    )
                )
                self.gemini_temperature.bind(
                    "<ButtonPress-1>", self.lock_movement_during_scale
                )
                self.gemini_temperature.bind(
                    "<ButtonRelease-1>", self.unlock_movement_after_scale
                )
            if hasattr(self, "gemini_top_p"):
                self.gemini_top_p.config(
                    command=lambda val: self.update_gemini_value_labels("top_p", val)
                )
                self.gemini_top_p.bind(
                    "<ButtonPress-1>", self.lock_movement_during_scale
                )
                self.gemini_top_p.bind(
                    "<ButtonRelease-1>", self.unlock_movement_after_scale
                )

            # บันทึกค่าเริ่มต้นเพื่อเปรียบเทียบการเปลี่ยนแปลง
            self.store_original_values()

            # แสดง UI ตามโมเดลปัจจุบัน
            self.show_parameter_frames(self.model_var.get())

            # ทำให้ปุ่ม Apply ไม่สามารถกดได้เมื่อเริ่มต้น
            self.apply_button.config(state=tk.DISABLED)
        except Exception as e:
            logging.error(f"Error loading current settings: {e}")
            messagebox.showerror(
                "Error", f"เกิดข้อผิดพลาดในการโหลดค่าปัจจุบัน: {e}", parent=self.model_window
            )
            
    def store_original_values(self):
        """เก็บค่าเริ่มต้นของพารามิเตอร์เพื่อเปรียบเทียบการเปลี่ยนแปลง - เหลือแค่ Gemini"""
        selected_model = self.model_var.get()

        # อ่านค่าจาก scale widgets โดยตรง
        max_tokens = self.gemini_max_tokens.get()
        temperature = self.gemini_temperature.get()
        top_p = self.gemini_top_p.get()
        google_key = self.google_key_var.get()

        self.original_values = {
            "model": selected_model,
            "gemini_max_tokens": max_tokens,
            "gemini_temperature": temperature,
            "gemini_top_p": top_p,
            "google_key": google_key,
        }

    def check_for_changes(self, *args):
        """ตรวจสอบว่ามีการเปลี่ยนแปลงค่าหรือไม่ - เหลือแค่ Gemini"""
        if not self.original_values:
            return False

        selected_model = self.model_var.get()

        # ตรวจสอบการเปลี่ยนแปลงของ Google API Key
        google_key = self.google_key_var.get()
        api_key_changed = google_key != self.original_values.get("google_key", "")

        # ตรวจสอบการเปลี่ยนแปลงค่าพารามิเตอร์ Gemini - อ่านค่าปัจจุบันจาก scales
        current_max_tokens = self.gemini_max_tokens.get()
        current_temperature = self.gemini_temperature.get()
        current_top_p = self.gemini_top_p.get()

        # เปรียบเทียบค่า
        model_changed = selected_model != self.original_values["model"]
        tokens_changed = current_max_tokens != self.original_values["gemini_max_tokens"]
        temp_changed = (
            abs(current_temperature - self.original_values["gemini_temperature"])
            > 0.001
        )  # เปรียบเทียบ float ปลอดภัย
        top_p_changed = (
            abs(current_top_p - self.original_values["gemini_top_p"]) > 0.001
        )  # เปรียบเทียบ float ปลอดภัย

        has_changes = (
            model_changed
            or tokens_changed
            or temp_changed
            or top_p_changed
            or api_key_changed
        )

        # ปรับสถานะปุ่ม Apply
        if has_changes:
            self.apply_button.button.config(
                state=tk.NORMAL,
                bg=SettingsUITheme.COLORS["success"],
                fg=SettingsUITheme.COLORS["text_primary"],
            )
        else:
            self.apply_button.button.config(
                state=tk.DISABLED,
                bg=SettingsUITheme.COLORS["bg_tertiary"],
                fg=SettingsUITheme.COLORS["text_disabled"],
            )

        return has_changes

    def on_model_change(self, event):
        """จัดการการเปลี่ยนแปลงโมเดลที่เลือก - เหลือแค่ Gemini"""
        selected_model = self.model_var.get()

        # อัปเดตการแสดงผล API Keys ตามโมเดลที่เลือก
        self.update_api_keys_display(selected_model)

        # แสดง frame ตามโมเดลที่เลือก (Gemini เสมอ)
        self.show_parameter_frames(selected_model)

        # โหลดค่าพารามิเตอร์ตาม model ปัจจุบัน
        self.load_model_specific_parameters(selected_model)

        # ตรวจสอบการเปลี่ยนแปลงเพื่อปรับสถานะปุ่ม Apply
        self.check_for_changes()

    def setup_parameter_tracking(self):
        """ตั้งค่าการติดตามการเปลี่ยนแปลงของพารามิเตอร์ - เหลือแค่ Gemini"""
        # ไม่ต้องทำอะไรเพราะ command ถูกตั้งค่าไว้แล้วใน _create_compact_parameter_control
        logging.info("Parameter tracking setup completed - Gemini only")

    def apply_settings(self):
        try:
            selected_model = self.model_var.get()

            # ตรวจสอบและบันทึก API Keys ที่มีการเปลี่ยนแปลง
            env_updates = {}

            # อ่านค่า API Key ปัจจุบัน - เหลือแค่ Google
            google_key = self.google_key_var.get()

            # ตรวจสอบการเปลี่ยนแปลงของ Google API Key
            if google_key != self._mask_api_key(os.getenv("GEMINI_API_KEY", "")):
                # ถ้าช่องว่างเปล่า = ลบ key
                if not google_key or google_key.strip() == "":
                    env_updates["GEMINI_API_KEY"] = ""
                    logging.info("Removing Google API key")
                # ถ้าไม่ใช่ masked value ให้บันทึกค่าใหม่
                elif "•" not in google_key:
                    env_updates["GEMINI_API_KEY"] = google_key

            # ตรวจสอบว่าจะมี Google API Key เหลืออยู่หรือไม่
            will_have_google = (
                "GEMINI_API_KEY" not in env_updates
                or env_updates["GEMINI_API_KEY"] != ""
            )

            # ถ้าไม่มี Google API Key เหลือเลย ให้แจ้งเตือนและยกเลิก
            if not will_have_google:
                messagebox.showerror(
                    "ผิดพลาด",
                    "ต้องมี Google AI API Key ในระบบ\nกรุณาเพิ่ม API Key",
                    parent=self.model_window,
                )
                return False

            # สร้าง parameters สำหรับ Gemini เท่านั้น
            # อ่านค่าจาก scale widgets โดยตรงและตรวจสอบความถูกต้อง
            max_tokens_raw = self.gemini_max_tokens.get()
            temperature_raw = self.gemini_temperature.get()
            top_p_raw = self.gemini_top_p.get()

            # แปลงค่าให้เป็นชนิดที่ถูกต้องและตรวจสอบขอบเขต
            max_tokens_value = max(50, min(800, int(max_tokens_raw)))
            temperature_value = round(float(temperature_raw), 2)
            top_p_value = round(float(top_p_raw), 2)

            # ตรวจสอบขอบเขตอีกครั้งหลังปัดเศษ
            temperature_value = max(0.1, min(1.0, temperature_value))
            top_p_value = max(0.1, min(1.0, top_p_value))

            api_parameters = {
                "model": selected_model,
                "max_tokens": max_tokens_value,
                "temperature": temperature_value,
                "top_p": top_p_value,
            }

            # แสดงหน้าต่างยืนยันการเปลี่ยนการตั้งค่า
            confirm = messagebox.askyesno(
                "ยืนยันการเปลี่ยนการตั้งค่า",
                f"คุณต้องการบันทึกการตั้งค่าใหม่สำหรับโมเดล {selected_model} หรือไม่?\n\nหมายเหตุ: การเปลี่ยนโมเดลจะทำให้ต้องรีสตาร์ทระบบการแปล",
                icon="question",
                parent=self.model_window,
            )

            if not confirm:
                return False

            # บันทึก API Keys ลงไฟล์ .env ถ้ามีการเปลี่ยนแปลง
            if env_updates:
                # ลองบันทึกด้วย method ที่ปรับปรุงใหม่
                env_update_success = self._update_env_file(env_updates)

                if not env_update_success:
                    # แสดงข้อความแจ้งเตือนแบบไม่บล็อกการทำงาน
                    messagebox.showinfo(
                        "ข้อมูลการบันทึก API Keys",
                        "ไม่สามารถบันทึก API Keys ลงไฟล์ .env ได้ (เกิดจากไม่มีสิทธิ์เขียนไฟล์)\n\n"
                        "ระบบได้บันทึกไฟล์สำรองไว้ที่ .env.user\n"
                        "และจะใช้ API Keys ใหม่สำหรับเซสชันนี้\n\n"
                        "คำแนะนำ: สามารถคัดลอกไฟล์ .env.user ไปทับไฟล์ .env ด้วยตนเอง",
                        parent=self.model_window,
                    )

                # ตั้งค่า environment variables ใหม่สำหรับเซสชันนี้ (ทำเสมอ)
                for key, value in env_updates.items():
                    os.environ[key] = value
                    logging.info(f"Updated environment variable {key}")

            # ตรวจสอบก่อนบันทึก
            self.settings.validate_model_parameters(api_parameters)

            # บันทึกค่าโดยตรง
            success, error = self.settings.set_api_parameters(**api_parameters)
            if not success:
                raise ValueError(error)

            new_settings = {"api_parameters": api_parameters}

            # บังคับให้บันทึกลงไฟล์
            self.settings.save_settings()

            # แสดง log ในคอนโซล
            self.log_new_model_settings(api_parameters)

            # แสดง log การบันทึก API keys
            if env_updates:
                keys_updated = ", ".join(
                    [k.replace("_API_KEY", "") for k in env_updates.keys()]
                )
                logging.info(f"API Keys updated: {keys_updated}")

            # เรียกใช้ callback เพื่ออัพเดท UI
            if callable(self.apply_settings_callback):
                self.apply_settings_callback(new_settings)

            # เรียกใช้ update_api_settings จาก main_app
            update_success = False
            if self.main_app and hasattr(self.main_app, "update_api_settings"):
                try:
                    logging.info(
                        f"Calling update_api_settings from main_app for model: {selected_model}"
                    )
                    update_success = self.main_app.update_api_settings()
                    logging.info(
                        f"update_api_settings result from main_app: {update_success}"
                    )
                except Exception as e:
                    logging.error(
                        f"Error calling update_api_settings from main_app: {e}"
                    )
                    messagebox.showerror(
                        "Error", f"การอัพเดทโมเดลล้มเหลว: {e}", parent=self.model_window
                    )
                    return False
            else:
                logging.error(
                    "Could not find update_api_settings method in main_app"
                )
                messagebox.showerror(
                    "Error",
                    "ไม่พบวิธีการอัพเดทโมเดล กรุณารีสตาร์ทโปรแกรม",
                    parent=self.model_window,
                )
                return False

            if not update_success:
                messagebox.showwarning(
                    "Warning",
                    "การอัพเดทโมเดลไม่สมบูรณ์ อาจต้องรีสตาร์ทโปรแกรม",
                    parent=self.model_window,
                )
                return False

            # อัปเดตค่าเริ่มต้นหลังจากบันทึกสำเร็จ
            self.store_original_values()

            # แสดงสถานะการบันทึก
            self.apply_button.config(
                text="✓", bg="#43A047", fg="white"
            )
            self.model_window.after(
                1500,
                lambda: self.apply_button.config(
                    text="APPLY", state=tk.DISABLED, bg="#333333", fg="#757575"
                ),
            )
            return True

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"เกิดข้อผิดพลาดในการบันทึกการตั้งค่า: {str(e)}",
                parent=self.model_window,
            )
            logging.error(f"Failed to apply settings: {str(e)}", exc_info=True)
            return False

    def log_new_model_settings(self, params):
        """แสดงค่าพารามิเตอร์ใหม่ในคอนโซลให้อ่านง่าย"""
        model = params.get("model", "Unknown")

        # สร้างกรอบสำหรับข้อความ
        border = "=" * 50

        # แสดงข้อมูลในคอนโซล
        print(f"\n{border}")
        print(f"🔄 MODEL SETTINGS CHANGED")
        print(f"{border}")
        print(f"📚 Model: {model}")

        # แสดงพารามิเตอร์ต่างๆ
        for key, value in params.items():
            if key != "model":
                print(f"🔹 {key}: {value}")

        print(f"{border}\n")

        # บันทึกลง log ด้วย
        logging.info(f"Model settings changed - Model: {model}, Parameters: {params}")

    def open(self):
        """เปิดหน้าต่างการตั้งค่าโมเดล - แบบ compact ไม่มี toggle"""
        if not self.window_created:
            self.create_model_window()

        # ตรวจสอบสิทธิ์การเข้าถึงไฟล์ .env
        file_perms = self._check_env_file_permissions()
        if not file_perms["can_write"]:
            # แสดงคำเตือนเกี่ยวกับสิทธิ์การเข้าถึง
            warning_txt = (
                "⚠️ ไม่สามารถเขียนไฟล์ .env - การเปลี่ยนแปลง API Keys จะใช้ได้เฉพาะเซสชันนี้"
            )

            # สร้าง label แสดงคำเตือน (ถ้ายังไม่มี)
            if not hasattr(self, "permission_warning_label"):
                self.permission_warning_label = tk.Label(
                    self.model_window,
                    text=warning_txt,
                    font=("Bai Jamjuree Light", 12, "bold"),
                    bg="#FFC107",  # สีพื้นหลังเหลือง
                    fg="#212121",  # สีข้อความดำ
                    pady=5,
                    anchor="center",
                )
                self.permission_warning_label.pack(fill=tk.X, side=tk.BOTTOM)

        # โหลดค่าปัจจุบันจาก settings
        self.load_current_settings()

        # จัดตำแหน่งหน้าต่าง - วางด้านขวาของหน้าต่าง settings (parent) ห่าง 10px
        parent_x = self.parent.winfo_rootx() + self.parent.winfo_width() + 10
        parent_y = self.parent.winfo_rooty()
        self.model_window.geometry(f"+{parent_x}+{parent_y}")

        # แสดงหน้าต่าง
        self.model_window.deiconify()
        self.model_window.lift()
        self.model_window.focus_set()

        # ทำให้ปุ่ม Apply ไม่สามารถกดได้เมื่อเริ่มต้น
        self.apply_button.config(state=tk.DISABLED, bg="#333333", fg="#757575")

    def close(self):
        """Hide the model settings window"""
        if self.model_window and self.window_created:
            self.model_window.withdraw()

    def start_move(self, event):
        # ป้องกันการเคลื่อนไหวเมื่อคลิกปุ่มปิด
        if hasattr(self, "close_button") and event.widget == self.close_button:
            return
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.x = None
        self.y = None

    def do_move(self, event):
        # ป้องกันการเคลื่อนไหวเมื่อคลิกปุ่มปิด
        if hasattr(self, "close_button") and event.widget == self.close_button:
            return
        if (
            hasattr(self, "x")
            and hasattr(self, "y")
            and self.x is not None
            and self.y is not None
        ):
            deltax = event.x - self.x
            deltay = event.y - self.y
            x = self.model_window.winfo_x() + deltax
            y = self.model_window.winfo_y() + deltay
            self.model_window.geometry(f"+{x}+{y}")

    def lock_movement_during_scale(self, event=None):
        """ล็อคการเคลื่อนที่ของหน้าต่าง Model Settings เมื่อกำลังปรับ Scale"""
        print("Locking UI movement during scale adjustment")
        self.is_adjusting_scale = True  # ตั้งค่า flag

        # ถอด binding การเคลื่อนที่ออกชั่วคราว
        if hasattr(self, "model_window") and self.model_window:
            self.old_motion_binding = self.model_window.bind("<B1-Motion>")
            self.model_window.unbind("<B1-Motion>")

    def unlock_movement_after_scale(self, event=None):
        """ปลดล็อคการเคลื่อนที่ของหน้าต่าง Model Settings หลังจากปรับ Scale เสร็จ"""
        print("Unlocking UI movement after scale adjustment")
        self.is_adjusting_scale = False  # รีเซ็ต flag

        # ผูก binding การเคลื่อนที่อีกครั้ง
        if hasattr(self, "model_window") and self.model_window:
            self.model_window.bind("<B1-Motion>", self.do_move)

    def load_model_specific_parameters(self, model_name):
        """โหลดค่าพารามิเตอร์ตามโมเดลที่เลือก - เหลือแค่ Gemini"""
        current_params = self.settings.get_api_parameters()

        # ตั้งค่าพารามิเตอร์สำหรับ Gemini
        max_tokens = current_params.get("max_tokens", 500)
        temperature = current_params.get("temperature", 0.8)
        top_p = current_params.get("top_p", 0.9)

        # ตั้งค่าสำหรับ Gemini
        self.gemini_max_tokens.set(max_tokens)
        self.gemini_temperature.set(temperature)
        self.gemini_top_p.set(top_p)

        # อัพเดตค่า label
        if hasattr(self, "gemini_token_value_label"):
            self.gemini_token_value_label.config(text=str(max_tokens))
        if hasattr(self, "gemini_temp_value_label"):
            self.gemini_temp_value_label.config(text=str(temperature))
        if hasattr(self, "gemini_top_p_value_label"):
            self.gemini_top_p_value_label.config(text=str(top_p))

    def update_gemini_value_labels(self, param_type, value):
        """อัพเดตค่า label สำหรับการแสดงผลค่าปัจจุบันของพารามิเตอร์ Gemini"""
        try:
            # แปลงค่าที่ได้รับให้เป็นชนิดที่ถูกต้อง
            if param_type == "tokens":
                # แปลงค่าที่ได้รับให้เป็นชนิดที่ถูกต้อง
                if isinstance(value, str):
                    converted_value = int(float(value))
                else:
                    converted_value = int(value)

                # อัปเดท label และ scale ให้ตรงกัน
                self.gemini_token_value_label.config(text=str(converted_value))
                # ให้แน่ใจว่า scale มีค่าเดียวกัน
                if self.gemini_max_tokens.get() != converted_value:
                    self.gemini_max_tokens.set(converted_value)

            elif param_type == "temperature":
                # ตรวจสอบและแปลงค่า temperature
                if isinstance(value, str):
                    converted_value = round(float(value), 2)  # ปัดทศนิยม 2 ตำแหน่ง
                else:
                    converted_value = round(float(value), 2)

                # อัปเดท label และ scale ให้ตรงกัน
                self.gemini_temp_value_label.config(text=str(converted_value))
                # ให้แน่ใจว่า scale มีค่าเดียวกัน
                if (
                    abs(self.gemini_temperature.get() - converted_value) > 0.001
                ):  # เปรียบเทียบ float อย่างปลอดภัย
                    self.gemini_temperature.set(converted_value)

            elif param_type == "top_p":
                # ตรวจสอบและแปลงค่า top_p
                if isinstance(value, str):
                    converted_value = round(float(value), 2)  # ปัดทศนิยม 2 ตำแหน่ง
                else:
                    converted_value = round(float(value), 2)

                # อัปเดท label และ scale ให้ตรงกัน
                self.gemini_top_p_value_label.config(text=str(converted_value))
                # ให้แน่ใจว่า scale มีค่าเดียวกัน
                if (
                    abs(self.gemini_top_p.get() - converted_value) > 0.001
                ):  # เปรียบเทียบ float อย่างปลอดภัย
                    self.gemini_top_p.set(converted_value)

            # ตรวจสอบการเปลี่ยนแปลงเพื่อเปิด/ปิดปุ่ม Apply
            self.check_for_changes()

        except Exception as e:
            logging.error(f"Error updating Gemini value labels: {e}")
            logging.error(f"Raw value was: {value} (type: {type(value)})")

    def adjust_gemini_value(self, param_type, delta):
        """ปรับค่าพารามิเตอร์ Gemini ขึ้นหรือลงตามปุ่มที่กด"""
        try:
            if param_type == "tokens":
                current = self.gemini_max_tokens.get()
                new_value = current + delta
                # ทำให้อยู่ในช่วงที่กำหนด (50-800 ตามที่ระบุ)
                new_value = max(50, min(800, new_value))
                self.gemini_max_tokens.set(new_value)
                self.update_gemini_value_labels("tokens", new_value)

            elif param_type == "temperature":
                current = self.gemini_temperature.get()
                new_value = current + delta
                # ทำให้อยู่ในช่วงที่กำหนด (0.1-1.0)
                new_value = max(0.1, min(1.0, new_value))
                # ปัดเป็นจุดทศนิยม 2 ตำแหน่งสำหรับ step 0.05
                new_value = round(new_value, 2)
                self.gemini_temperature.set(new_value)
                self.update_gemini_value_labels("temperature", new_value)

            elif param_type == "top_p":
                current = self.gemini_top_p.get()
                new_value = current + delta
                # ทำให้อยู่ในช่วงที่กำหนด (0.1-1.0)
                new_value = max(0.1, min(1.0, new_value))
                # ปัดเป็นจุดทศนิยม 2 ตำแหน่งสำหรับ step 0.05
                new_value = round(new_value, 2)
                self.gemini_top_p.set(new_value)
                self.update_gemini_value_labels("top_p", new_value)

            # ตรวจสอบการเปลี่ยนแปลง
            self.check_for_changes()

        except Exception as e:
            logging.error(f"Error adjusting Gemini value: {e}")
            logging.error(f"param_type: {param_type}, delta: {delta}")
