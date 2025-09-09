import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk
import logging
from tkinter import messagebox

logging.basicConfig(level=logging.INFO)


def create_rounded_rectangle(self, x1, y1, x2, y2, radius=25, **kwargs):
    """วาดสี่เหลี่ยมมุมโค้งบน Canvas

    Args:
        x1, y1: พิกัดมุมบนซ้าย
        x2, y2: พิกัดมุมล่างขวา
        radius: รัศมีมุมโค้ง (pixel)
        **kwargs: พารามิเตอร์อื่นๆ สำหรับ create_polygon

    Returns:
        int: ID ของรูปที่วาด
    """
    points = [
        x1 + radius,
        y1,
        x2 - radius,
        y1,
        x2,
        y1,
        x2,
        y1 + radius,
        x2,
        y2 - radius,
        x2,
        y2,
        x2 - radius,
        y2,
        x1 + radius,
        y2,
        x1,
        y2,
        x1,
        y2 - radius,
        x1,
        y1 + radius,
        x1,
        y1,
    ]

    return self.create_polygon(points, **kwargs, smooth=True)


# เพิ่มเมธอดให้กับคลาส Canvas
tk.Canvas.create_rounded_rectangle = create_rounded_rectangle


class AppearanceManager:
    def __init__(self):
        self.bg_color = "#2c2c2c"
        self.fg_color = "white"
        self.highlight_color = "yellow"
        self.opacity = 0.9
        self.font_name = "Nasalization Rg"
        self.font_size = 12
        self.letter_spacing = 3
        self.button_border_width = 1
        self.button_style = {
            "bg": self.bg_color,
            "fg": self.fg_color,
            "relief": tk.FLAT,
            "bd": self.button_border_width,
            "highlightthickness": self.button_border_width,
            "highlightbackground": self.fg_color,
            "activebackground": self.bg_color,
            "activeforeground": self.fg_color,
        }
        self.custom_font = None

        # สร้างชุดธีมหลากหลายสี
        self.themes = {
            "purple": {
                "name": "Purple Magic",
                "accent": "#6c5ce7",  # สีหลัก (ม่วง)
                "accent_light": "#a29bfe",  # สีม่วงอ่อน (hover)
                "highlight": "#6c5ce7",  # ใช้สีม่วงให้สอดคล้องกับธีม
                "secondary": "#00c2cb",  # สีรอง
                "text": "#ffffff",  # สีข้อความปกติ
                "text_dim": "#b2b2b2",  # สีข้อความที่อ่อนลง
                "button_bg": "#262637",  # สีพื้นหลังปุ่ม
            },
            "blue": {
                "name": "Ocean Blue",
                "accent": "#1E88E5",  # สีฟ้า
                "accent_light": "#64B5F6",  # สีฟ้าอ่อน
                "highlight": "#1E88E5",  # ใช้สีฟ้าเหมือนสีหลัก
                "secondary": "#03A9F4",  # สีฟ้ารอง
                "text": "#ffffff",
                "text_dim": "#b2b2b2",
                "button_bg": "#262637",
            },
            "green": {
                "name": "Emerald",
                "accent": "#2E7D32",  # สีเขียว
                "accent_light": "#4CAF50",  # สีเขียวอ่อน
                "highlight": "#2E7D32",  # ใช้สีเขียวเหมือนสีหลัก
                "secondary": "#00BFA5",  # สีเขียวรอง
                "text": "#ffffff",
                "text_dim": "#b2b2b2",
                "button_bg": "#262637",
            },
            "red": {
                "name": "Ruby Red",
                "accent": "#C62828",  # สีแดง
                "accent_light": "#EF5350",  # สีแดงอ่อน
                "highlight": "#C62828",  # ใช้สีแดงเหมือนสีหลัก
                "secondary": "#FF5252",  # สีแดงรอง
                "text": "#ffffff",
                "text_dim": "#b2b2b2",
                "button_bg": "#262637",
            },
        }

        # ค่าสีตีมเริ่มต้น กรณีไม่มีสีที่ตั้งค่าใน preset ผู้ใช้
        self.current_theme = "purple"

        # เพิ่มตัวแปรสำหรับเก็บ callback
        self.theme_change_callback = None

    # ปรับปรุงเมธอด get_theme_colors ที่มีอยู่แล้ว
    def get_theme_colors(self):
        """ดึงค่าสีทั้งหมดของธีมปัจจุบัน"""
        theme = self.themes.get(self.current_theme, self.themes["purple"])
        return theme

    def create_color_picker_dialog(
        self, parent, initial_color="#6c5ce7", title="เลือกสีธีม"
    ):
        """แสดงหน้าต่างเลือกสีแบบกำหนดเอง

        Args:
            parent: parent widget
            initial_color: สีเริ่มต้น
            title: หัวข้อหน้าต่าง

        Returns:
            str: สีที่เลือกในรูปแบบ hex code หรือ None ถ้ายกเลิก
        """
        from tkinter import colorchooser

        result = colorchooser.askcolor(initial_color, title=title)
        return result[1] if result[1] else None

    def create_custom_theme(self, primary_color, secondary_color, name="Custom Theme"):
        """สร้างธีมใหม่จากสีที่ผู้ใช้เลือก

        Args:
            primary_color: สีหลัก (hex code)
            secondary_color: สีรอง (hex code)
            name: ชื่อธีมใหม่

        Returns:
            str: รหัสธีมที่สร้างใหม่
        """
        # สร้าง ID ธีมใหม่
        theme_id = f"custom_{len(self.themes) + 1}"

        # คำนวณสีลูกอัตโนมัติ
        accent_light = self.lighten_color(primary_color, 1.3)

        # สร้างธีมใหม่
        self.themes[theme_id] = {
            "name": name,
            "accent": primary_color,  # สีหลัก
            "accent_light": accent_light,  # สีหลักที่อ่อนกว่า (hover)
            "highlight": primary_color,  # ใช้สีหลักเป็นสีไฮไลท์
            "secondary": secondary_color,  # สีรอง
            "text": "#ffffff",  # สีข้อความปกติ
            "text_dim": "#b2b2b2",  # สีข้อความที่อ่อนลง
            "button_bg": "#262637",  # สีพื้นหลังปุ่ม
        }

        # บันทึกธีมใหม่ลงใน settings ถ้ามี
        if hasattr(self, "settings") and self.settings:
            custom_themes = self.settings.get("custom_themes", {})
            custom_themes[theme_id] = self.themes[theme_id]
            self.settings.set("custom_themes", custom_themes)

        return theme_id

    def create_theme_manager_ui(self, parent, settings=None):
        """สร้างหน้า UI จัดการธีม

        Args:
            parent: parent widget
            settings: Settings object (optional)

        Returns:
            tk.Frame: frame หลักของหน้าจัดการธีม
        """
        self.settings = settings  # เก็บ settings เพื่อบันทึกธีมที่สร้างขึ้น

        # Main frame with padding
        main_frame = tk.Frame(parent, bg=self.bg_color)

        # Title section
        title_frame = tk.Frame(main_frame, bg=self.bg_color)
        title_frame.pack(fill=tk.X, pady=(5, 10))

        # Title label
        title_label = tk.Label(
            title_frame,
            text="UI Color",
            font=("Arial", 12, "bold"),
            fg=self.get_theme_color("text", "#ffffff"),
            bg=self.bg_color,
        )
        title_label.pack(side=tk.LEFT)

        # Close button
        close_button = tk.Button(
            title_frame,
            text="×",
            font=("Arial", 16, "bold"),
            fg=self.get_theme_color("text", "#ffffff"),
            bg=self.bg_color,
            bd=0,
            padx=10,
            pady=0,
            command=lambda: parent.destroy(),
        )
        close_button.pack(side=tk.RIGHT)

        # Hover effect for close button
        def on_close_enter(e):
            close_button.config(fg="#FF4444")

        def on_close_leave(e):
            close_button.config(fg=self.get_theme_color("text", "#ffffff"))

        close_button.bind("<Enter>", on_close_enter)
        close_button.bind("<Leave>", on_close_leave)

        # Add separator using secondary color
        separator = tk.Frame(
            main_frame,
            height=1,
            bg=self.get_theme_color("secondary", self.get_accent_color()),
        )
        separator.pack(fill=tk.X, pady=(0, 10))

        # สร้างส่วนเลือกธีมที่มีอยู่
        theme_frame = tk.Frame(main_frame, bg=self.bg_color)
        theme_frame.pack(fill=tk.X, pady=(0, 10))

        theme_label = tk.Label(
            theme_frame,
            text="Select theme:",
            font=("Arial", 10),
            fg=self.get_theme_color("text", "#ffffff"),
            bg=self.bg_color,
        )
        theme_label.pack(side=tk.LEFT, padx=(0, 10))

        # แสดงเฉพาะธีมที่ผู้ใช้สร้างเท่านั้น (ไม่รวมธีมเริ่มต้น)
        theme_ids = []  # เก็บ ID
        theme_names = []  # เก็บชื่อที่แสดง

        # สร้างการ mapping ระหว่างชื่อธีมและ ID
        self.theme_name_to_id = {}  # สร้าง dict ใหม่เพื่อเก็บ mapping

        # กรองเฉพาะธีมของผู้ใช้เท่านั้น (ขึ้นต้นด้วย "Theme")
        if settings and "custom_themes" in settings.settings:
            custom_themes = settings.settings["custom_themes"]
            for theme_id, theme_data in custom_themes.items():
                # เพิ่มเฉพาะธีมที่เป็นของผู้ใช้ (Theme1, Theme2, ...)
                if theme_id.startswith("Theme"):
                    theme_ids.append(theme_id)
                    theme_display_name = theme_data["name"]
                    theme_names.append(theme_display_name)
                    self.theme_name_to_id[theme_display_name] = theme_id

                    # เพิ่มธีมเข้าไปในคลังธีมด้วย (ถ้ายังไม่มี)
                    if theme_id not in self.themes:
                        self.themes[theme_id] = theme_data

        # ถ้าไม่มีธีมของผู้ใช้เลย ให้สร้างธีมเริ่มต้น
        if not theme_names:
            # สร้างธีมเริ่มต้น 1 ธีม
            default_themes = [
                {"name": "Red Theme", "accent": "#C62828", "secondary": "#FF5252"}
            ]

            for i, theme_data in enumerate(default_themes):
                theme_id = f"Theme{i+1}"
                theme_display_name = theme_data["name"]

                # สร้างธีมใหม่
                accent_light = self.lighten_color(theme_data["accent"], 1.3)
                new_theme = {
                    "name": theme_display_name,
                    "accent": theme_data["accent"],
                    "accent_light": accent_light,
                    "highlight": theme_data["accent"],
                    "secondary": theme_data["secondary"],
                    "text": "#ffffff",
                    "text_dim": "#b2b2b2",
                    "button_bg": "#262637",
                }

                # เพิ่มธีมใหม่ลงในคลังธีม
                self.themes[theme_id] = new_theme

                # เพิ่มลงใน list แสดงผล
                theme_ids.append(theme_id)
                theme_names.append(theme_display_name)
                self.theme_name_to_id[theme_display_name] = theme_id

                # บันทึกลง settings ถ้ามี
                if settings:
                    custom_themes = settings.get("custom_themes", {})
                    custom_themes[theme_id] = new_theme
                    settings.set("custom_themes", custom_themes)

            # บันทึกการเปลี่ยนแปลง
            if settings:
                settings.save_settings()

        # ตั้งค่าตัวแปรเริ่มต้นเป็นชื่อของธีมปัจจุบัน
        if self.current_theme in self.themes:
            current_theme_name = self.themes[self.current_theme]["name"]
        else:
            current_theme_name = theme_names[0] if theme_names else "ธีมสีม่วง"

        theme_var = tk.StringVar(value=current_theme_name)

        # Style the combobox
        combo_style = ttk.Style()
        combo_style.theme_use("clam")
        combo_style.configure(
            "Theme.TCombobox",
            fieldbackground=self.get_theme_color("button_bg", "#262637"),
            background=self.get_theme_color("button_bg", "#262637"),
            foreground=self.get_theme_color("text", "#ffffff"),
            bordercolor=self.get_theme_color("secondary", self.get_accent_color()),
            arrowcolor=self.get_theme_color("secondary", self.get_accent_color()),
            borderwidth=1,
            relief="flat",
        )
        combo_style.map(
            "Theme.TCombobox",
            fieldbackground=[("focus", self.get_theme_color("button_bg", "#262637"))],
            bordercolor=[("focus", self.get_accent_color())],
        )

        # สร้าง combobox ที่แสดงชื่อธีม
        theme_combo = ttk.Combobox(
            theme_frame,
            textvariable=theme_var,
            values=theme_names,
            width=10,
            style="Theme.TCombobox",
        )
        theme_combo.pack(side=tk.LEFT)

        # โค้ดอัพเดตธีมเมื่อเลือก combobox
        def update_theme_display(*args):
            selected_name = theme_var.get()

            # หา ID จากชื่อธีมที่เลือก
            if selected_name in self.theme_name_to_id:
                theme_id = self.theme_name_to_id[selected_name]

                # อัพเดตการแสดงผล
                theme_name_entry.config(textvariable=theme_name_var)
                theme_name_var.set(selected_name)

                # อัพเดตแถบสีตัวอย่าง
                primary_preview.config(bg=self.themes[theme_id]["accent"])
                secondary_preview.config(bg=self.themes[theme_id]["secondary"])

                # อัพเดตชื่อธีมในช่องข้อความอัตโนมัติ
                theme_name_var.set(selected_name)

        theme_var.trace("w", update_theme_display)

        # ฟังก์ชันสำหรับบันทึกและใช้ธีมที่เลือกในคราวเดียวกัน
        def apply_theme():
            # รับค่าชื่อใหม่จากช่องข้อความ
            new_name = theme_name_var.get().strip()

            # หากไม่มีชื่อ ใช้ชื่อเริ่มต้นที่ไม่ซ้ำ
            if not new_name:
                new_name = f"Theme {len(theme_names) + 1}"
                theme_name_var.set(new_name)

            # รับค่าสีที่เลือก
            primary = primary_preview.cget("bg")
            secondary = secondary_preview.cget("bg")

            # หา theme_id จากชื่อที่เลือกใน combobox
            selected_name = theme_var.get()
            theme_id = self.theme_name_to_id.get(selected_name, None)

            if not theme_id:
                # แจ้งเตือน
                status_label.config(
                    text="Theme not found. Please select a theme.",
                    fg="#F44336",  # สีแดง
                )
                main_frame.after(3000, lambda: status_label.config(text=""))
                return

            # ถ้าชื่อถูกเปลี่ยน ต้องอัพเดต mapping
            old_name = self.themes[theme_id]["name"]
            if new_name != old_name:
                # ตรวจสอบว่าชื่อใหม่ซ้ำกับชื่อธีมอื่นหรือไม่
                if (
                    new_name in self.theme_name_to_id
                    and self.theme_name_to_id[new_name] != theme_id
                ):
                    # ถ้าชื่อซ้ำ เพิ่มเลขต่อท้าย
                    count = 1
                    base_name = new_name
                    while (
                        new_name in self.theme_name_to_id
                        and self.theme_name_to_id[new_name] != theme_id
                    ):
                        new_name = f"{base_name} ({count})"
                        count += 1
                    # อัพเดตชื่อในช่องข้อความ
                    theme_name_var.set(new_name)

                # ลบ mapping เก่า
                if old_name in self.theme_name_to_id:
                    del self.theme_name_to_id[old_name]

                # เพิ่ม mapping ใหม่
                self.theme_name_to_id[new_name] = theme_id

                # อัพเดตค่าใน combobox
                theme_names = list(theme_combo["values"])
                index = theme_names.index(old_name) if old_name in theme_names else -1
                if index >= 0:
                    theme_names[index] = new_name
                    theme_combo["values"] = theme_names
                    theme_var.set(new_name)

            # บันทึกและใช้ธีมที่อัพเดตแล้ว
            success = self._update_theme(theme_id, new_name, primary, secondary)

            # แสดงข้อความแจ้งเตือน
            if success:
                status_label.config(
                    text=f"Theme '{new_name}' saved successfully!",
                    fg="#4CAF50",  # สีเขียว
                )
            else:
                status_label.config(
                    text="Error saving theme",
                    fg="#F44336",  # สีแดง
                )

            # รีเซ็ตข้อความหลัง 3 วินาที
            main_frame.after(3000, lambda: status_label.config(text=""))

        # ปุ่ม APPLY (ใช้งานและบันทึกในคราวเดียว)
        apply_button = tk.Button(
            theme_frame,
            text="APPLY",
            command=apply_theme,
            bg=self.get_accent_color(),  # ใช้สีหลักของธีม
            fg="white",
            activebackground=self.get_theme_color("secondary"),  # ใช้สีรองเมื่อกด
            activeforeground="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=4,
            bd=0,
            relief=tk.FLAT,
            cursor="hand2",
        )
        apply_button.pack(side=tk.RIGHT, padx=(10, 0))

        # เพิ่ม hover effect ด้วยสีรอง
        def on_apply_enter(e):
            apply_button.config(bg=self.get_theme_color("secondary"))

        def on_apply_leave(e):
            apply_button.config(bg=self.get_accent_color())

        apply_button.bind("<Enter>", on_apply_enter)
        apply_button.bind("<Leave>", on_apply_leave)

        # แสดงชื่อธีมปัจจุบันแบบใหญ่และอยู่กลาง (คลิกเพื่อแก้ไขได้)
        theme_name_var = tk.StringVar(value=current_theme_name)

        theme_name_frame = tk.Frame(main_frame, bg=self.bg_color)
        theme_name_frame.pack(fill=tk.X, pady=(10, 5))

        # สร้าง Entry ที่ดูเหมือน Label แต่แก้ไขได้
        theme_name_entry = tk.Entry(
            theme_name_frame,
            textvariable=theme_name_var,
            bg=self.bg_color,
            fg=self.get_accent_color(),
            font=("Arial", 12, "bold"),
            bd=0,
            highlightthickness=0,
            justify="center",
            cursor="hand2",
        )
        theme_name_entry.pack(expand=True)

        # เพิ่ม hover effect
        def on_name_enter(e):
            theme_name_entry.config(fg=self.get_theme_color("secondary"))

        def on_name_leave(e):
            theme_name_entry.config(fg=self.get_accent_color())

        def on_name_focus(e):
            theme_name_entry.config(
                bg=self.get_theme_color("button_bg", "#262637"),
                highlightthickness=1,
                highlightcolor=self.get_accent_color(),
            )
            theme_name_entry.select_range(0, "end")

        def on_name_unfocus(e):
            theme_name_entry.config(bg=self.bg_color, highlightthickness=0)

        theme_name_entry.bind("<Enter>", on_name_enter)
        theme_name_entry.bind("<Leave>", on_name_leave)
        theme_name_entry.bind("<FocusIn>", on_name_focus)
        theme_name_entry.bind("<FocusOut>", on_name_unfocus)
        theme_name_entry.bind("<Return>", lambda e: apply_theme())

        # เก็บ reference
        name_entry = theme_name_entry

        # สร้างส่วนปรับแต่งธีม
        separator2 = tk.Frame(
            main_frame, height=1, bg=self.get_theme_color("button_bg", "#262637")
        )
        separator2.pack(fill=tk.X, pady=15)

        custom_label = tk.Label(
            main_frame,
            text="Customize",
            font=("Arial", 11, "bold"),
            fg=self.get_theme_color("text", "#ffffff"),
            bg=self.bg_color,
        )
        custom_label.pack(anchor="w", pady=(0, 5))

        # ส่วนเลือกสีหลัก
        colors_container = tk.Frame(main_frame, bg=self.bg_color)
        colors_container.pack(fill=tk.X, pady=(0, 10))

        # Primary color frame
        primary_frame = tk.Frame(colors_container, bg=self.bg_color)
        primary_frame.pack(fill=tk.X, pady=5)

        primary_label = tk.Label(
            primary_frame,
            text="Primary:",
            font=("Arial", 10),
            fg=self.get_theme_color("text", "#ffffff"),
            bg=self.bg_color,
            width=8,
            anchor="w",
        )
        primary_label.pack(side=tk.LEFT)

        # Primary color preview with better styling
        primary_preview = tk.Frame(
            primary_frame,
            bg=(
                self.themes[self.current_theme]["accent"]
                if self.current_theme in self.themes
                else "#6c5ce7"
            ),
            width=60,
            height=28,
            cursor="hand2",
            relief=tk.FLAT,
            highlightbackground=self.get_theme_color("secondary"),
            highlightthickness=1,
        )
        primary_preview.pack(side=tk.RIGHT, padx=(0, 5))
        primary_preview.pack_propagate(False)

        # เพิ่ม binding เพื่อให้คลิกที่กล่องสีได้โดยตรง
        primary_preview.bind(
            "<Button-1>", lambda e: self._select_theme_color(primary_preview)
        )

        # ส่วนเลือกสีรอง
        secondary_frame = tk.Frame(colors_container, bg=self.bg_color)
        secondary_frame.pack(fill=tk.X, pady=5)

        secondary_label = tk.Label(
            secondary_frame,
            text="Secondary:",
            font=("Arial", 10),
            fg=self.get_theme_color("text", "#ffffff"),
            bg=self.bg_color,
            width=8,
            anchor="w",
        )
        secondary_label.pack(side=tk.LEFT)

        # Secondary color preview with better styling
        secondary_preview = tk.Frame(
            secondary_frame,
            bg=(
                self.themes[self.current_theme]["secondary"]
                if self.current_theme in self.themes
                else "#00c2cb"
            ),
            width=60,
            height=28,
            cursor="hand2",
            relief=tk.FLAT,
            highlightbackground=self.get_theme_color("secondary"),
            highlightthickness=1,
        )
        secondary_preview.pack(side=tk.RIGHT, padx=(0, 5))
        secondary_preview.pack_propagate(False)

        # เพิ่ม binding เพื่อให้คลิกที่กล่องสีได้โดยตรง
        secondary_preview.bind(
            "<Button-1>", lambda e: self._select_theme_color(secondary_preview)
        )

        # เพิ่มคำแนะนำ
        hint_label = tk.Label(
            main_frame,
            text="Click color box to change",
            bg=self.bg_color,
            fg=self.get_theme_color("secondary", "#888888"),
            font=("Arial", 8),
        )
        hint_label.pack(anchor="e", pady=(0, 5))

        # สร้าง Label สำหรับแสดงข้อความแจ้งเตือน
        status_frame = tk.Frame(main_frame, bg=self.bg_color)
        status_frame.pack(fill=tk.X, pady=(10, 5))

        status_label = tk.Label(
            status_frame,
            text="",
            bg=self.bg_color,
            fg="#4CAF50",
            font=("Arial", 9),
            wraplength=280,
        )
        status_label.pack(fill=tk.X)

        # Add close functionality on click outside
        def close_on_click_outside(event):
            try:
                # ยกเว้น combobox dropdown และ widget ที่เกี่ยวข้อง
                widget = event.widget

                # ตรวจสอบ widget class ที่ไม่ควรถูกถือเป็น "outside click"
                widget_class = str(widget.__class__.__name__)
                widget_str = str(widget)

                # รายการ widget ที่ควรยกเว้น
                excluded_widgets = [
                    "Combobox",
                    "Listbox",
                    "Scrollbar",
                    "Entry",
                    "Button",
                ]

                # ตรวจสอบ class name และ widget string
                if any(excluded in widget_class for excluded in excluded_widgets):
                    return

                if any(
                    excluded.lower() in widget_str.lower()
                    for excluded in excluded_widgets
                ):
                    return

                # ตรวจสอบ widget hierarchy อย่างละเอียด
                current_widget = widget
                for _ in range(10):  # ตรวจสอบ 10 level ขึ้นไป
                    if current_widget == parent:
                        return
                    if hasattr(current_widget, "master") and current_widget.master:
                        current_widget = current_widget.master
                    else:
                        break

                # ตรวจสอบเพิ่มเติมด้วย winfo_containing
                try:
                    widget_at_pos = parent.winfo_containing(event.x_root, event.y_root)
                    if widget_at_pos and str(widget_at_pos).startswith(str(parent)):
                        return
                except:
                    pass

                # If we get here, the click was outside
                if hasattr(parent, "destroy"):
                    parent.destroy()

            except Exception as e:
                # หากเกิด error ก็ไม่ปิดหน้าต่าง
                pass

        # Bind to parent window after a delay to avoid immediate closing
        # เปลี่ยนจาก bind_all เป็น bind เฉพาะ parent เพื่อลดปัญหา
        def setup_close_binding():
            # ใช้ bind แทน bind_all เพื่อจำกัด scope
            parent.bind("<Button-1>", close_on_click_outside, add="+")
            # เพิ่มการปิดด้วย ESC key
            parent.bind("<Escape>", lambda e: parent.destroy())
            parent.focus_set()  # ให้ parent รับ focus เพื่อรับ ESC

        parent.after(200, setup_close_binding)

        # อัพเดตการแสดงผลครั้งแรก
        update_theme_display()

        return main_frame

    def _update_theme(self, theme_id, name, primary, secondary):
        """อัพเดตธีมที่มีอยู่ด้วยค่าใหม่

        Args:
            theme_id: รหัสของธีม
            name: ชื่อธีมใหม่
            primary: สีหลัก (hex code)
            secondary: สีรอง (hex code)

        Returns:
            bool: สถานะการอัพเดต (สำเร็จหรือไม่)
        """
        try:
            if not theme_id or theme_id not in self.themes:
                print(f"Theme ID '{theme_id}' not found in themes")
                return False

            # ตรวจสอบว่าเป็นชื่อที่ถูกต้อง
            if not name or not isinstance(name, str) or len(name.strip()) == 0:
                print("Invalid theme name")
                return False

            # ตรวจสอบค่าสี
            if not primary.startswith("#") or not secondary.startswith("#"):
                print("Invalid color format, must be #RRGGBB")
                return False

            # คำนวณสีลูกอัตโนมัติ
            try:
                accent_light = self.lighten_color(primary, 1.3)
            except Exception as e:
                print(f"Error calculating accent_light: {e}")
                accent_light = primary  # ใช้สีเดิมถ้าคำนวณไม่ได้

            # อัพเดตธีมที่มีอยู่แล้ว
            self.themes[theme_id].update(
                {
                    "name": name,
                    "accent": primary,
                    "accent_light": accent_light,
                    "highlight": primary,
                    "secondary": secondary,
                    # คงค่าอื่นๆ ไว้
                    "text": self.themes[theme_id].get("text", "#ffffff"),
                    "text_dim": self.themes[theme_id].get("text_dim", "#b2b2b2"),
                    "button_bg": self.themes[theme_id].get("button_bg", "#262637"),
                }
            )

            # บันทึกลง settings ถ้ามี
            if hasattr(self, "settings") and self.settings:
                try:
                    custom_themes = self.settings.get("custom_themes", {})
                    custom_themes[theme_id] = self.themes[theme_id]
                    self.settings.set("custom_themes", custom_themes)
                    self.settings.save_settings()  # บันทึกการเปลี่ยนแปลงทันที
                except Exception as e:
                    print(f"Error saving theme to settings: {e}")
                    # ไม่ return False เพราะธีมได้อัพเดตในโปรแกรมแล้ว

            # สลับไปใช้ธีมที่อัพเดตแล้วและบันทึกว่าเป็นธีมปัจจุบัน
            self.set_theme(theme_id)

            return True

        except Exception as e:
            print(f"Error updating theme: {e}")
            return False

    def _select_theme_color(self, preview_widget):
        """แสดงหน้าต่างเลือกสีและอัพเดทสีของ preview widget

        Args:
            preview_widget: widget ที่ใช้แสดงตัวอย่างสี
        """
        current_color = preview_widget.cget("bg")
        new_color = self.create_color_picker_dialog(preview_widget, current_color)
        if new_color:
            preview_widget.config(bg=new_color)

    def set_theme(self, theme_name):
        """ตั้งค่าธีมปัจจุบัน"""
        # ตรวจสอบว่าเป็น ID ที่มีอยู่ในคลังธีม
        if theme_name in self.themes:
            self.current_theme = theme_name

            # บันทึกการเปลี่ยนแปลงลง settings ถ้ามี
            if hasattr(self, "settings") and self.settings:
                self.settings.set("theme", theme_name)
                self.settings.save_settings()
                print(f"Theme {theme_name} saved to settings.json")
            else:
                print("ไม่พบ settings object ในการบันทึกธีม")

            # เรียก callback ถ้ามี
            if hasattr(self, "theme_change_callback") and self.theme_change_callback:
                try:
                    self.theme_change_callback()
                except Exception as e:
                    print(f"Error in theme_change_callback: {e}")

            return True
        elif (
            theme_name.startswith("Theme")
            and hasattr(self, "settings")
            and self.settings
        ):
            # กรณีเป็น Theme ID ที่มีในผู้ใช้แต่ไม่มีในคลังธีม
            custom_themes = self.settings.get("custom_themes", {})
            if theme_name in custom_themes:
                # โหลดธีมจาก settings เข้าคลังธีม
                self.themes[theme_name] = custom_themes[theme_name]
                self.current_theme = theme_name

                # บันทึกลง settings
                self.settings.set("theme", theme_name)
                self.settings.save_settings()
                print(f"Imported theme {theme_name} saved to settings.json")

                # เรียก callback
                if (
                    hasattr(self, "theme_change_callback")
                    and self.theme_change_callback
                ):
                    try:
                        self.theme_change_callback()
                    except Exception as e:
                        print(f"Error in theme_change_callback: {e}")

                return True

        # กรณีไม่พบธีม ใช้ธีมม่วงเป็นค่าเริ่มต้น
        print(f"Theme '{theme_name}' not found, using default")
        self.current_theme = "purple"
        return False

    def set_theme_change_callback(self, callback):
        """ตั้งค่า callback ที่จะเรียกเมื่อธีมเปลี่ยน

        Args:
            callback: ฟังก์ชันที่จะเรียกเมื่อธีมเปลี่ยน
        """
        self.theme_change_callback = callback

    def load_custom_themes(self, settings):
        """โหลดธีมที่ผู้ใช้สร้างเองจาก settings

        Args:
            settings: Settings object
        """
        if settings:
            try:
                self.settings = settings
                custom_themes = settings.get("custom_themes", {})

                # จัดการกรณีไม่มีธีมผู้ใช้หรือมีน้อยกว่า 5 ธีม
                if not custom_themes or len(custom_themes) < 5:
                    # สร้างธีมเริ่มต้นสำหรับส่วนที่ขาด
                    default_themes = [
                        {
                            "name": "ธีมเริ่มต้น",
                            "accent": "#6c5ce7",
                            "secondary": "#00c2cb",
                        },
                        {"name": "ธีมฟ้า", "accent": "#1E88E5", "secondary": "#03A9F4"},
                        {"name": "ธีมเขียว", "accent": "#2E7D32", "secondary": "#00BFA5"},
                        {"name": "ธีมแดง", "accent": "#C62828", "secondary": "#FF5252"},
                        {"name": "ธีมดำ", "accent": "#333333", "secondary": "#888888"},
                    ]

                    # สร้างเฉพาะธีมที่ขาด
                    existing_numbers = set()
                    for theme_id in custom_themes:
                        if theme_id.startswith("Theme"):
                            try:
                                num = int(theme_id[5:])
                                existing_numbers.add(num)
                            except ValueError:
                                pass

                    # เติมธีมที่ขาด
                    for i in range(1, 6):
                        if i not in existing_numbers and len(custom_themes) < 5:
                            theme_id = f"Theme{i}"
                            theme_data = default_themes[i - 1]

                            # สร้างธีมใหม่
                            accent_light = self.lighten_color(theme_data["accent"], 1.3)
                            new_theme = {
                                "name": theme_data["name"],
                                "accent": theme_data["accent"],
                                "accent_light": accent_light,
                                "highlight": theme_data["accent"],
                                "secondary": theme_data["secondary"],
                                "text": "#ffffff",
                                "text_dim": "#b2b2b2",
                                "button_bg": "#262637",
                            }

                            # เพิ่มธีมใหม่ลงในคลังธีม
                            custom_themes[theme_id] = new_theme

                    # บันทึกการเปลี่ยนแปลง
                    settings.set("custom_themes", custom_themes)
                    settings.save_settings()

                # โหลดธีมผู้ใช้ทั้งหมดเข้าคลังธีม
                for theme_id, theme_data in custom_themes.items():
                    self.themes[theme_id] = theme_data

                # ดูว่าควรใช้ธีมไหนเป็นธีมปัจจุบัน
                current_theme = settings.get("theme", "purple")
                
                if current_theme in self.themes:
                    self.current_theme = current_theme
                elif current_theme in custom_themes:
                    self.current_theme = current_theme
                else:
                    self.current_theme = "purple"  # ใช้ธีมม่วงเป็นค่าเริ่มต้น

            except Exception as e:
                print(f"Error loading custom themes: {e}")
                self.current_theme = "purple"  # ใช้ธีมม่วงเป็นค่าเริ่มต้น

    def apply_theme_to_button(self, button, is_active=False, is_accent=False):
        """ประยุกต์ใช้ธีมกับปุ่มแบบเต็มรูปแบบ

        Args:
            button: ปุ่มที่ต้องการปรับสี
            is_active: True ถ้าปุ่มกำลังถูกเลือก/active
            is_accent: True ถ้าต้องการใช้สีหลักแทนสี button_bg
        """
        theme = self.get_theme_colors()

        # เลือกสีตามประเภทของปุ่ม
        if is_active:  # ปุ่มที่กำลังถูกเลือก
            bg_color = "#404060"  # สีเข้มสำหรับปุ่มที่เลือก
            text_color = theme.get("highlight", "#00FFFF")
            hover_color = theme.get("accent_light", "#a29bfe")
        elif is_accent:  # ปุ่มหลัก (เช่น Start Translation)
            bg_color = theme.get("accent", "#6c5ce7")
            text_color = "#ffffff"
            hover_color = theme.get("accent_light", "#a29bfe")
        else:  # ปุ่มปกติ
            bg_color = theme.get("button_bg", "#262637")
            text_color = "#ffffff"
            hover_color = theme.get("accent", "#6c5ce7")

        # ปรับตามประเภทของ button
        if hasattr(button, "itemconfig") and hasattr(button, "button_bg"):
            # สำหรับปุ่มที่สร้างด้วย Canvas
            button.itemconfig(button.button_bg, fill=bg_color)
            if hasattr(button, "button_text"):
                button.itemconfig(button.button_text, fill=text_color)
            button.original_bg = bg_color
            button.hover_bg = hover_color
            button.selected = is_active
        else:
            # สำหรับปุ่มธรรมดา
            button.configure(bg=bg_color, fg=text_color)
            button.configure(activebackground=hover_color)

    def get_current_theme(self):
        """ดึงชื่อธีมปัจจุบัน"""
        return self.current_theme

    def get_theme_color(self, color_name, default=None):  # เพิ่ม default=None
        """ดึงค่าสีเฉพาะจากธีมปัจจุบัน

        Args:
            color_name: ชื่อของสีที่ต้องการ (accent, highlight, secondary, text, text_dim, button_bg, etc.)
            default: ค่า default ที่จะคืนหากไม่พบสีในธีม (optional)

        Returns:
            str: ค่าสีในรูปแบบ hex code
        """
        theme = self.themes.get(
            self.current_theme, self.themes.get("purple", {})
        )  # ใช้ purple เป็น fallback ถ้า current_theme ไม่มี

        # กำหนดค่าเริ่มต้นภายใน หากไม่พบใน theme หรือ default ที่ส่งมา
        default_colors = {
            "accent": "#6c5ce7",
            "accent_light": "#a29bfe",
            "highlight": "#6c5ce7",
            "secondary": "#00c2cb",
            "text": "#ffffff",
            "text_dim": "#b2b2b2",
            "button_bg": "#262637",
            "error": "#e74c3c",  # เพิ่ม error ด้วย
            # เพิ่มสีอื่นๆ ที่อาจจำเป็น
        }

        # 1. ลองดึงจาก theme ปัจจุบัน
        color_value = theme.get(color_name)

        # 2. ถ้าไม่เจอใน theme, ลองใช้ default ที่ส่งมา
        if color_value is None and default is not None:
            color_value = default

        # 3. ถ้ายังไม่มี ให้ใช้ default จาก default_colors
        if color_value is None:
            color_value = default_colors.get(
                color_name, self.fg_color
            )  # ใช้ fg_color เป็น fallback สุดท้าย

        return color_value

    def get_accent_color(self):
        """ดึงสีหลักของธีมปัจจุบัน"""
        return self.get_theme_color("accent")

    def get_highlight_color(self):
        """ดึงสีไฮไลท์ของธีมปัจจุบัน"""
        return self.get_theme_color("highlight")

    def get_available_themes(self):
        """ดึงรายชื่อธีมที่มีทั้งหมด"""
        return [(theme_id, data["name"]) for theme_id, data in self.themes.items()]

    def cycle_theme(self):
        """เปลี่ยนไปยังธีมถัดไป"""
        theme_keys = list(self.themes.keys())
        current_index = theme_keys.index(self.current_theme)
        next_index = (current_index + 1) % len(theme_keys)
        self.current_theme = theme_keys[next_index]
        return self.current_theme, self.themes[self.current_theme]["name"]

    def update_bg_color(self, new_color):
        """Update background color and related styles"""
        self.bg_color = new_color
        self.button_style.update({"bg": new_color, "activebackground": new_color})

    def apply_bg_color(self, widget):
        """Apply current background color to widget"""
        widget.configure(bg=self.bg_color)

    def load_custom_font(self, root):
        try:
            # เพิ่มการตรวจสอบว่าฟอนต์ "Bai Jamjuree Light" มีในระบบหรือไม่
            # และใช้เป็นทางเลือกหากฟอนต์หลักไม่มี
            available_fonts = list(tkfont.families())

            if "Bai Jamjuree Light" in available_fonts:
                logging.info("Found Bai Jamjuree Light font in system")
                # ใช้เป็นฟอนต์เริ่มต้นสำหรับข้อความภาษาไทย
                self.thai_font = "Bai Jamjuree Light"
            elif "Bai Jamjuree" in available_fonts:
                logging.info("Found Bai Jamjuree font in system")
                self.thai_font = "Bai Jamjuree"
            else:
                logging.info(
                    "Bai Jamjuree fonts not found, using IBM Plex Sans Thai Medium as fallback"
                )
                self.thai_font = "IBM Plex Sans Thai Medium"

            self.custom_font = tkfont.Font(family=self.font_name, size=self.font_size)
            logging.info(f"Font loaded successfully: {self.font_name}")

            # สร้างฟอนต์สำหรับข้อความภาษาไทยด้วย
            self.thai_custom_font = tkfont.Font(
                family=self.thai_font, size=self.font_size
            )
            logging.info(f"Thai font loaded successfully: {self.thai_font}")

            return self.custom_font
        except Exception as e:
            logging.warning(f"Failed to load font: {e}. Using system default.")
            self.custom_font = tkfont.Font(family="TkDefaultFont", size=self.font_size)
            self.thai_font = "TkDefaultFont"
            self.thai_custom_font = self.custom_font
            return self.custom_font

    def apply_style(self, window):
        window.configure(bg=self.bg_color)
        window.attributes("-alpha", self.opacity)
        self.custom_font = self.load_custom_font(window)
        self.button_style["font"] = self.custom_font

        style = ttk.Style()
        style.configure(
            "Switch.TCheckbutton",
            background=self.bg_color,
            foreground=self.fg_color,
            font=self.custom_font,
        )
        style.map(
            "Switch.TCheckbutton",
            background=[("active", self.bg_color)],
            foreground=[("active", self.fg_color)],
        )

        return self.custom_font

    def create_styled_button(self, parent, text, command=None, hover_bg=None):
        text = text.upper()
        spaced_text = " ".join(text)
        button = tk.Button(
            parent, text=spaced_text, command=command, **self.button_style
        )
        original_bg = self.button_style["bg"]
        hover_bg = hover_bg if hover_bg else original_bg
        button.bind("<Enter>", lambda e: button.config(bg=hover_bg))
        button.bind("<Leave>", lambda e: button.config(bg=original_bg))
        return button

    def create_modern_button(
        self,
        parent,
        text,
        command,
        width=95,
        height=30,
        fg="#ffffff",
        bg=None,
        hover_bg=None,
        font=("Nasalization Rg", 10),
        corner_radius=10,
    ):
        """สร้างปุ่มโมเดิร์นด้วย Canvas"""
        # ใช้สีจากธีมปัจจุบันถ้าไม่ได้ระบุ
        if bg is None:
            bg = self.get_theme_color("button_bg")
        if hover_bg is None:
            hover_bg = self.get_accent_color()

        # สร้าง canvas สำหรับวาดปุ่ม
        canvas = tk.Canvas(
            parent,
            width=width,
            height=height,
            bg=self.bg_color,
            highlightthickness=0,
            bd=0,
        )

        # วาดพื้นหลังปุ่มด้วยสี่เหลี่ยมมุมโค้ง
        button_bg = canvas.create_rounded_rectangle(
            0, 0, width, height, radius=corner_radius, fill=bg, outline=""
        )

        # สร้างข้อความบนปุ่ม
        button_text = canvas.create_text(
            width // 2, height // 2, text=text, fill=fg, font=font
        )

        # ผูกคำสั่งเมื่อคลิก
        if command:
            canvas.bind("<Button-1>", lambda event: command())

        # เพิ่ม metadata สำหรับการใช้งานภายหลัง
        canvas.selected = False
        canvas.original_bg = bg
        canvas.hover_bg = hover_bg
        canvas.button_bg = button_bg
        canvas.button_text = button_text
        canvas._is_hovering = False

        # สร้าง hover effect - ใช้ itemconfig ไม่ใช้ config เพื่อปรับแต่งรูปร่าง
        def on_enter(event):
            if hasattr(canvas, "selected") and canvas.selected:
                return
            canvas._is_hovering = True
            canvas.itemconfig(button_bg, fill=hover_bg)

        def on_leave(event):
            canvas._is_hovering = False
            if not hasattr(canvas, "selected") or not canvas.selected:
                canvas.itemconfig(button_bg, fill=canvas.original_bg)

        canvas.bind("<Enter>", on_enter)
        canvas.bind("<Leave>", on_leave)

        # ใช้ method itemconfig แทน config เพื่อปรับแต่งรูปร่าง
        def custom_config(**kwargs):
            try:
                if "text" in kwargs and canvas.winfo_exists():
                    canvas.itemconfig(button_text, text=kwargs["text"])
                if "fg" in kwargs and canvas.winfo_exists():
                    canvas.itemconfig(button_text, fill=kwargs["fg"])
                if "bg" in kwargs and canvas.winfo_exists():
                    # อัพเดตเฉพาะถ้าไม่ได้อยู่ในสถานะ hover
                    if not canvas._is_hovering:
                        canvas.itemconfig(button_bg, fill=kwargs["bg"])

                    # อัพเดตสีเดิมเสมอ เพื่อให้เมื่อออกจาก hover จะใช้สีนี้
                    canvas.original_bg = kwargs["bg"]
            except Exception as e:
                print(f"Error in button custom_config (appearance.py): {e}")

        # เก็บ method custom_config ไว้สำหรับใช้งาน
        canvas.custom_config = custom_config

        return canvas

    def create_styled_entry(self, parent, **kwargs):
        entry = tk.Entry(
            parent,
            bg=self.bg_color,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            font=self.custom_font,
            **kwargs,
        )
        return entry

    def create_styled_label(self, parent, text, **kwargs):
        # ดึง font จาก kwargs ถ้ามี หรือใช้ค่าเริ่มต้น
        font = kwargs.pop("font", self.custom_font)

        # ถ้าไม่ได้ระบุฟอนต์เฉพาะ ให้ใช้ Bai Jamjuree Light แทน IBM Plex Sans Thai Medium สำหรับข้อความทั่วไป
        if (
            isinstance(font, tuple)
            and len(font) >= 1
            and font[0] == "IBM Plex Sans Thai Medium"
        ):
            # เก็บขนาดและสไตล์ฟอนต์เดิม
            font_size = font[1] if len(font) > 1 else 10
            font_style = font[2] if len(font) > 2 else ""
            # สร้างฟอนต์ใหม่โดยเปลี่ยนชื่อฟอนต์เป็น thai_font
            font = (self.thai_font, font_size, font_style)

        # ตรวจสอบว่าข้อความมีตัวอักษรไทยหรือไม่
        contains_thai = False
        thai_pattern = r"[\u0E00-\u0E7F]"  # ช่วงอักขระไทย Unicode
        import re

        if re.search(thai_pattern, text):
            contains_thai = True

        # ถ้าเป็นข้อความภาษาไทย และฟอนต์ที่กำหนดไม่ได้ระบุชัดเจน ให้ใช้ thai_custom_font
        if (
            contains_thai
            and font == self.custom_font
            and hasattr(self, "thai_custom_font")
        ):
            font = self.thai_custom_font

        label = tk.Label(
            parent,
            text=text,
            bg=self.bg_color,
            fg=self.fg_color,
            font=font,
            **kwargs,
        )
        return label

    def create_styled_text(self, parent, **kwargs):
        text_widget = tk.Text(
            parent,
            bg=self.bg_color,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            font=self.custom_font,
            **kwargs,
        )
        text_widget.tag_configure("highlight", background=self.highlight_color)
        return text_widget

    def create_styled_scale(self, parent, **kwargs):
        """
        สร้าง scale widget พร้อม frame และ value label

        Returns:
            tuple: (frame, scale) โดย
                  frame คือ container ที่มี scale และ label
                  scale คือ ttk.Scale widget ที่ใช้ควบคุมค่า
        """
        frame = tk.Frame(parent, bg=self.bg_color)
        digits = kwargs.pop("digits", 0)

        style = ttk.Style()
        style.configure(
            "Custom.Horizontal.TScale",
            background=self.bg_color,
            troughcolor=self.lighten_color(self.bg_color),
        )

        scale = ttk.Scale(frame, style="Custom.Horizontal.TScale", **kwargs)
        scale.pack(side=tk.LEFT, fill=tk.X, expand=True)

        value_var = tk.StringVar()
        value_label = tk.Label(
            frame, textvariable=value_var, bg=self.bg_color, fg=self.fg_color, width=5
        )
        value_label.pack(side=tk.RIGHT, padx=(5, 0))

        def update_value(event=None):
            value = scale.get()
            value_var.set(f"{value:.{digits}f}")

        scale.bind("<Motion>", update_value)
        scale.bind("<ButtonRelease-1>", update_value)
        update_value()

        return (frame, scale)

    def create_advance_ui_frame(self, parent):
        frame = tk.Frame(parent, bg=self.bg_color)
        return frame

    def create_api_parameter_form(self, parent):
        form_frame = tk.Frame(parent, bg=self.bg_color)

        model_frame = tk.Frame(form_frame, bg=self.bg_color)
        model_frame.pack(fill=tk.X, pady=5)
        model_label = self.create_styled_label(model_frame, "Model:")
        model_label.pack(side=tk.LEFT)
        model_combo = self.create_styled_combobox(
            model_frame,
            values=["gemini-2.0-flash-lite", "gemini-2.0-flash", "gemini-2.5-flash"],
        )
        model_combo.pack(side=tk.RIGHT, expand=True, fill=tk.X)

        max_tokens_frame = tk.Frame(form_frame, bg=self.bg_color)
        max_tokens_frame.pack(fill=tk.X, pady=5)
        max_tokens_label = self.create_styled_label(max_tokens_frame, "Max Tokens:")
        max_tokens_label.pack(side=tk.LEFT)
        max_tokens_tuple = self.create_styled_scale(
            max_tokens_frame, from_=100, to=1000, orient=tk.HORIZONTAL
        )
        max_tokens_tuple[0].pack(side=tk.RIGHT, expand=True, fill=tk.X)

        temp_frame = tk.Frame(form_frame, bg=self.bg_color)
        temp_frame.pack(fill=tk.X, pady=5)
        temp_label = self.create_styled_label(temp_frame, "Temperature:")
        temp_label.pack(side=tk.LEFT)
        temp_tuple = self.create_styled_scale(
            temp_frame, from_=0.5, to=0.9, orient=tk.HORIZONTAL, digits=2
        )
        temp_tuple[0].pack(side=tk.RIGHT, expand=True, fill=tk.X)

        top_p_frame = tk.Frame(form_frame, bg=self.bg_color)
        top_p_frame.pack(fill=tk.X, pady=5)
        top_p_label = self.create_styled_label(top_p_frame, "Top P:")
        top_p_label.pack(side=tk.LEFT)
        top_p_tuple = self.create_styled_scale(
            top_p_frame, from_=0.5, to=0.9, orient=tk.HORIZONTAL, digits=2
        )
        top_p_tuple[0].pack(side=tk.RIGHT, expand=True, fill=tk.X)

        # Store references
        form_frame.model_combo = model_combo
        form_frame.max_tokens_scale = max_tokens_tuple[1]
        form_frame.temp_scale = temp_tuple[1]
        form_frame.top_p_scale = top_p_tuple[1]

        # Hide top_p for Claude
        def on_model_change(event):
            is_claude = model_combo.get() == "claude-3-haiku"
            if is_claude:
                top_p_frame.pack_forget()
            else:
                top_p_frame.pack(fill=tk.X, pady=5)

        model_combo.bind("<<ComboboxSelected>>", on_model_change)
        return form_frame

    def create_save_button(self, parent, command):
        return self.create_styled_button(parent, "Save", command)

    def create_parameter_description(self, parent):
        desc_frame = tk.Frame(parent, bg=self.bg_color)

        descriptions = {
            "Model": "โมเดล AI ที่ใช้ในการแปลภาษา",
            "Max Tokens": "จำนวนโทเค็นสูงสุดที่ใช้ในการแปล (100-1000)",
            "Temperature": "ความสร้างสรรค์ในการแปล (0.5-0.9)",
            "Top P": "ความหลากหลายของคำศัพท์ (0.5-0.9)",
        }

        for i, (param, desc) in enumerate(descriptions.items()):
            label = self.create_styled_label(desc_frame, f"{param}: {desc}")
            label.pack(anchor="w", pady=2)

        return desc_frame

    def lighten_color(self, color, factor=1.3):
        """เพิ่มความสว่างของสี

        Args:
            color: สี hex code เช่น #RRGGBB
            factor: ค่า factor ที่ใช้ปรับความสว่าง (>1 = สว่างขึ้น)

        Returns:
            str: สีใหม่ในรูปแบบ hex code
        """
        from colorsys import rgb_to_hls, hls_to_rgb
        import re

        # แปลง hex เป็น RGB
        hex_pattern = r"#?([\da-fA-F]{2})([\da-fA-F]{2})([\da-fA-F]{2})"
        if re.match(hex_pattern, color):
            # แยก hex ออกมา
            hex_color = color.lstrip("#")
            r, g, b = [int(hex_color[i : i + 2], 16) / 255.0 for i in (0, 2, 4)]
            h, l, s = rgb_to_hls(r, g, b)
            l = min(1.0, l * factor)  # ป้องกันค่าเกิน 1.0
            r, g, b = hls_to_rgb(h, l, s)
            return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
        return color

    def darken_color(self, color, factor=0.7):
        """ลดความสว่างของสี (ทำให้มืดลง)

        Args:
            color: สี hex code เช่น #RRGGBB
            factor: ค่า factor ที่ใช้ปรับความสว่าง (<1 = มืดลง)

        Returns:
            str: สีใหม่ในรูปแบบ hex code
        """
        from colorsys import rgb_to_hls, hls_to_rgb
        import re

        # แปลง hex เป็น RGB
        hex_pattern = r"#?([\da-fA-F]{2})([\da-fA-F]{2})([\da-fA-F]{2})"
        if re.match(hex_pattern, color):
            # แยก hex ออกมา
            hex_color = color.lstrip("#")
            r, g, b = [int(hex_color[i : i + 2], 16) / 255.0 for i in (0, 2, 4)]
            h, l, s = rgb_to_hls(r, g, b)
            l = max(0.0, l * factor)  # ป้องกันค่าต่ำกว่า 0.0
            r, g, b = hls_to_rgb(h, l, s)
            return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
        return color

    def create_styled_combobox(self, parent, **kwargs):
        combo = ttk.Combobox(parent, **kwargs)
        combo.configure(style="Custom.TCombobox")
        return combo


appearance_manager = AppearanceManager()
