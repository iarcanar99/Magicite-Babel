import threading
import time
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
from tkinter import messagebox  # <--- เพิ่ม messagebox
from PIL import (
    ImageTk,
    Image,
)  # สำหรับการจัดการรูปภาพ
import logging
import json
import os
from appearance import appearance_manager
from settings import Settings
from asset_manager import AssetManager

# imports สำหรับการทำขอบโค้งมน
import win32gui
import win32con
import win32api
from ctypes import windll

logging.basicConfig(level=logging.INFO)


class Control_UI:
    def __init__(
        self,
        root,
        force_translate,
        switch_area,
        settings,
        parent_app=None,
        parent_callback=None,
        trigger_temporary_area_display_callback=None,
        toggle_click_callback=None,
        toggle_hover_callback=None,
    ):
        logging.info("Control_UI.__init__ started")
        self.root = root
        self.force_translate = force_translate
        self.switch_area_callback = switch_area
        self.settings = settings
        self.parent_root = None
        self.parent_app = parent_app
        self.parent_callback = parent_callback
        self.trigger_temporary_area_display_callback = (
            trigger_temporary_area_display_callback
        )
        self.toggle_click_callback = toggle_click_callback
        self.toggle_hover_callback = toggle_hover_callback

        # *** เพิ่มระบบจัดการ tooltip ที่เป็นระเบียบ ***
        self.active_tooltips = []  # เก็บ tooltip ที่แสดงอยู่ทั้งหมด
        self.manual_force_tooltip = None  # tooltip เฉพาะสำหรับ force button
        self._hiding_tooltips = False  # ป้องกันการเรียกซ้ำ

        # *** กำหนด self.theme ที่นี่ ก่อนเรียก setup_buttons ***
        self.theme = {
            "bg": appearance_manager.bg_color,
            "accent": appearance_manager.get_accent_color(),
            "accent_light": appearance_manager.get_theme_color("accent_light"),
            "secondary": appearance_manager.get_theme_color("secondary"),
            "button_bg": appearance_manager.get_theme_color(
                "button_bg"
            ),  # สำคัญ: ต้องมี "button_bg"
            "text": appearance_manager.get_theme_color("text", "#ffffff"),
            "text_dim": appearance_manager.get_theme_color("text_dim", "#b2b2b2"),
            "highlight": appearance_manager.get_highlight_color(),
            "error": appearance_manager.get_theme_color("error", "#FF4136"),
            "success": appearance_manager.get_theme_color("success", "#4CAF50"),
            "button_inactive_bg": appearance_manager.get_theme_color(
                "button_inactive_bg", "#555555"
            ),
            "border": appearance_manager.get_theme_color("border", "#444444"),
            "fg": appearance_manager.get_theme_color("text", "#ffffff"),
        }
        # ตรวจสอบว่า button_bg มีค่าหรือไม่ ถ้าไม่มีให้ใส่ fallback
        if not self.theme.get("button_bg"):
            self.theme["button_bg"] = "#262637"  # Fallback color

        # *** ตัวแปรสำหรับ toggle hover settings UI ***
        self.hover_settings_window = None
        self.hover_settings_is_open = False  # Flag ง่ายๆ สำหรับติดตาม state

        self.click_translate_var = tk.BooleanVar()
        self.click_translate_var.set(settings.get("enable_click_translate", False))

        self.hover_translation_var = tk.BooleanVar()
        self.hover_translation_var.set(settings.get("enable_hover_translation", False))

        #         self.cpu_limit = self.settings.get("cpu_limit", 80)

        self.x = None
        self.y = None

        self.current_preset = self.settings.get("current_preset", 1)
        self.max_presets = 6
        self.presets = self.settings.get_all_presets()
        self.has_unsaved_changes = False

        initial_area_str = self.settings.get("current_area", "A+B")
        initial_areas = initial_area_str.split("+")
        self.area_states = {
            "A": "A" in initial_areas,
            "B": "B" in initial_areas,
            "C": "C" in initial_areas,
        }
        if not any(self.area_states.values()):
            self.area_states["A"] = True
            initial_area_str = "A"

        self.ensure_preset_area_consistency()

        self.ui_cache = {
            "position_x": None,
            "position_y": None,
            "current_area": initial_area_str,
        }

        self.show_area_windows = {}
        self.is_area_shown = False
        self.top = None

        # *** ตัวแปรสำหรับ Reset Hold functionality ***
        self.is_resetting = False
        self.reset_progress = 0
        self.reset_timer = None
        self.original_reset_text = "RESET"

        self.setup_window()  # setup_window ควรจะใช้ self.theme ที่เพิ่งกำหนดไป
        self.setup_buttons()  # ตอนนี้ setup_buttons สามารถใช้ self.theme.get("button_bg") ได้แล้ว
        self.setup_bindings()

        self._sync_current_preset_with_translate_areas()

        self.root.update_idletasks()

        self.update_button_highlights()
        self.update_preset_buttons()

        # ตั้งค่าเริ่มต้นปุ่ม show-hide ให้ถูกต้อง (แก้ไขจากปัญหาฟังก์ชันซ้ำ)
        self.root.after(100, self._fix_show_hide_button_initial_state)

        self.update_display(
            self.settings.get("current_area", "A"),
            self.settings.get("current_preset", 1),
        )

        if self.toggle_click_callback is None:
            logging.warning("Control_UI: toggle_click_callback is not provided.")
        if self.toggle_hover_callback is None:
            logging.warning("Control_UI: toggle_hover_callback is not provided.")
        if self.parent_callback is None:
            logging.warning("Control_UI: parent_callback (CPU Limit) is not provided.")

        logging.info("Control_UI __init__ complete.")
        
        # อัพเดตสถานะปุ่ม EDIT ครั้งแรก
        self.root.after(100, self.update_edit_button_state)  # ใช้ after เพื่อให้ UI แสดงผลเสร็จก่อน

    def _fix_show_hide_button_initial_state(self):
        """แก้ไขสีปุ่ม show-hide ให้ถูกต้องตั้งแต่เริ่มต้น (เนื่องจากมีฟังก์ชัน create_utility_bar ซ้ำ)"""
        try:
            if (
                hasattr(self, "show_hide_area_button_ctrl")
                and self.show_hide_area_button_ctrl.winfo_exists()
            ):
                # บังคับให้เป็นสีแดงตั้งแต่เริ่มต้น เนื่องจาก is_area_shown = False
                self.show_hide_area_button_ctrl.config(
                    text="SHOW",
                    bg=self.theme.get("bg", "#1a1a1a"),  # ใช้พื้นหลังโปร่งใส
                    fg=self.theme.get("error", "#e74c3c"),
                )
                logging.debug("Fixed show-hide button initial state to red text")
        except Exception as e:
            logging.error(f"Error fixing show-hide button initial state: {e}")

    def toggle_show_area_ctrl(self):
        """
        Toggle the persistent display of selected areas from Control UI.
        Manages its own state (self.is_area_shown) and windows (self.show_area_windows).
        """
        if self.is_area_shown:
            self.hide_show_area_ctrl()  # เรียกเมธอดใหม่สำหรับซ่อน
            if (
                hasattr(self, "show_hide_area_button_ctrl")
                and self.show_hide_area_button_ctrl.winfo_exists()
            ):
                self.show_hide_area_button_ctrl.config(
                    text="SHOW",
                    bg=self.theme.get("bg", "#1a1a1a"),  # พื้นหลังโปร่งใส
                    fg=self.theme.get("error", "#e74c3c"),
                )
        else:
            self.show_area_ctrl()  # เรียกเมธอดใหม่สำหรับแสดง
            if (
                hasattr(self, "show_hide_area_button_ctrl")
                and self.show_hide_area_button_ctrl.winfo_exists()
            ):
                self.show_hide_area_button_ctrl.config(
                    text="HIDE",
                    bg=self.theme.get("accent", "#6c5ce7"),  # สี active
                    fg=self.theme.get("text", "#ffffff"),  # อักษรสีขาว
                )

    def show_area_ctrl(self):
        """
        Shows all currently selected areas as red overlay windows.
        This version is managed by Control_UI.
        """
        if not hasattr(self, "settings"):
            logging.error(
                "Control_UI: Settings object not available in show_area_ctrl."
            )
            return
        if not self.parent_app or not hasattr(self.parent_app, "root"):
            logging.error(
                "Control_UI: parent_app or parent_app.root not available for creating overlay windows."
            )
            return

        try:
            self.hide_show_area_ctrl()  # ล้างของเก่าก่อนเสมอ

            current_area_string_from_settings = self.settings.get("current_area", "A")
            active_areas = current_area_string_from_settings.split("+")

            if not active_areas or all(not a for a in active_areas):
                logging.warning("Control_UI: No active areas defined to show.")
                self.is_area_shown = False
                if (
                    hasattr(self, "show_hide_area_button_ctrl")
                    and self.show_hide_area_button_ctrl.winfo_exists()
                ):
                    self.show_hide_area_button_ctrl.config(
                        text="SHOW",
                        bg=self.theme.get("button_inactive_bg", "#555555"),
                        fg=self.theme.get("error", "#e74c3c"),
                    )
                return

            overlay_parent = self.parent_app.root

            for area_code in active_areas:
                if not area_code.strip():
                    continue

                translate_area = self.settings.get_translate_area(area_code)
                if not translate_area or not all(
                    k in translate_area
                    for k in ["start_x", "start_y", "end_x", "end_y"]
                ):
                    logging.warning(
                        f"Control_UI: Coordinates for area '{area_code}' are incomplete or missing in show_area_ctrl."
                    )
                    continue

                window = tk.Toplevel(overlay_parent)
                window.overrideredirect(True)
                window.attributes("-alpha", 0.4)
                window.attributes("-topmost", True)

                scale_x, scale_y = self.get_screen_scale()

                try:
                    start_x = float(translate_area["start_x"])
                    start_y = float(translate_area["start_y"])
                    end_x = float(translate_area["end_x"])
                    end_y = float(translate_area["end_y"])
                except (ValueError, TypeError) as e:
                    logging.error(
                        f"Control_UI: Invalid coordinate value for area '{area_code}'. Error: {e}"
                    )
                    if window.winfo_exists():
                        window.destroy()
                    continue

                x = int(start_x * scale_x)
                y = int(start_y * scale_y)
                width = int((end_x - start_x) * scale_x)
                height = int((end_y - start_y) * scale_y)

                if width <= 0 or height <= 0:
                    logging.warning(
                        f"Control_UI: Calculated invalid size for area '{area_code}': {width}x{height}. Skipping display."
                    )
                    if window.winfo_exists():
                        window.destroy()
                    continue

                window.geometry(f"{width}x{height}+{x}+{y}")
                canvas = tk.Canvas(
                    window, bg="red", highlightthickness=0
                )  # พื้นหลังกรอบเป็นสีแดง
                canvas.pack(fill=tk.BOTH, expand=True)
                window.lift()
                self.show_area_windows[area_code] = window

            self.is_area_shown = True
            if (
                hasattr(self, "show_hide_area_button_ctrl")
                and self.show_hide_area_button_ctrl.winfo_exists()
            ):
                self.show_hide_area_button_ctrl.config(
                    text="HIDE",
                    bg=self.theme.get("accent", "#6c5ce7"),  # สี active
                    fg=self.theme.get("text", "#ffffff"),  # อักษรสีขาว
                )

        except Exception as e:
            logging.error(f"Error in Control_UI show_area_ctrl: {str(e)}")
            self.is_area_shown = False
            if (
                hasattr(self, "show_hide_area_button_ctrl")
                and self.show_hide_area_button_ctrl.winfo_exists()
            ):
                self.show_hide_area_button_ctrl.config(
                    text="SHOW",
                    bg=self.theme.get("bg", "#1a1a1a"),  # พื้นหลังโปร่งใส
                    fg=self.theme.get("error", "#e74c3c"),
                )

    def hide_show_area_ctrl(self):
        """
        Hides all currently displayed area overlay windows.
        This version is managed by Control_UI.
        """
        for area_code, window in list(
            self.show_area_windows.items()
        ):  # ใช้ list() เพื่อให้ลบจาก dict ได้อย่างปลอดภัย
            if window and window.winfo_exists():
                try:
                    window.destroy()
                except tk.TclError:
                    pass  # อาจจะถูกทำลายไปแล้ว
            # ไม่จำเป็นต้อง del จาก dict ใน loop, clear() ทีเดียวหลัง loop

        self.show_area_windows.clear()
        self.is_area_shown = False  # ตั้งค่าสถานะ
        if (
            hasattr(self, "show_hide_area_button_ctrl")
            and self.show_hide_area_button_ctrl.winfo_exists()
        ):
            self.show_hide_area_button_ctrl.config(
                text="SHOW",
                bg=self.theme.get("bg", "#1a1a1a"),  # พื้นหลังโปร่งใส
                fg=self.theme.get("error", "#e74c3c"),
            )

    def create_toggle_switch(
        self, parent, text, variable, command, width=40, height=20
    ):
        """สร้าง Toggle Switch ที่ดูดีและใช้งานง่ายด้วย Canvas"""
        # ตรวจสอบว่า theme โหลดหรือยัง ถ้ายัง ให้ใช้ค่า fallback
        current_theme = getattr(self, "theme", {})
        bg_color = current_theme.get("bg", "#1a1a1a")

        container = tk.Frame(parent, bg=bg_color)

        if text:
            label = tk.Label(
                container,
                text=text,
                bg=bg_color,
                fg=current_theme.get("fg", "white"),
                font=("FC Minimal Medium", 10),  # ปรับ font ให้เหมาะสม
                anchor="w",
            )
            label.pack(side=tk.LEFT, padx=(0, 5))

        canvas = tk.Canvas(
            container,
            width=width,
            height=height,
            bg=bg_color,
            highlightthickness=0,
            cursor="hand2",
        )
        canvas.pack(side=tk.LEFT)  # หรือ RIGHT ตามต้องการ

        # สีและขนาด
        padding = 2
        knob_radius = (height - 2 * padding) / 2
        # ป้องกันค่าติดลบถ้า height เล็กไป
        knob_diameter = max(0, height - 2 * padding)
        off_x = padding
        on_x = width - knob_diameter - padding
        bg_on_color = current_theme.get("success", "#4CAF50")
        bg_off_color = current_theme.get("button_inactive_bg", "#555555")
        knob_color = current_theme.get("fg", "white")
        bg_outline = current_theme.get("border", "#444444")

        # --- วาดพื้นหลัง (Track) ---
        try:
            # ส่วนโค้งด้านซ้าย
            canvas.create_oval(
                padding,
                padding,
                height - padding,
                height - padding,  # ใช้ height สำหรับเส้นผ่านศูนย์กลาง
                fill=bg_off_color,
                outline=bg_outline,
                tags="track",
            )
            # ส่วนโค้งด้านขวา
            canvas.create_oval(
                width - height + padding,
                padding,  # เลื่อน x ไปด้านขวา
                width - padding,
                height - padding,  # ใช้ height สำหรับเส้นผ่านศูนย์กลาง
                fill=bg_off_color,
                outline=bg_outline,
                tags="track",
            )
            # ส่วนสี่เหลี่ยมตรงกลาง
            canvas.create_rectangle(
                height / 2,
                padding,  # เริ่มจากกึ่งกลางส่วนโค้งซ้าย
                width - height / 2,
                height - padding,  # สิ้นสุดที่กึ่งกลางส่วนโค้งขวา
                fill=bg_off_color,
                outline=bg_off_color,
                tags="track",  # ใช้สีเดียวกับ oval เพื่อให้ดูเชื่มกัน
            )
        except tk.TclError as e_draw:
            logging.error(
                f"Error drawing toggle switch track: {e_draw}. Maybe invalid dimensions?"
            )
            # อาจจะวาดสี่เหลี่ยมง่ายๆแทนถ้า error
            canvas.create_rectangle(
                0, 0, width, height, fill=bg_off_color, tags="track"
            )

        # --- วาดตัวเลื่อน (Knob) ---
        try:
            knob = canvas.create_oval(
                off_x,
                padding,
                off_x + knob_diameter,
                padding + knob_diameter,
                fill=knob_color,
                outline=knob_color,
                tags="knob",
            )
        except tk.TclError as e_knob:
            logging.error(f"Error drawing toggle switch knob: {e_knob}")
            knob = None  # กำหนดเป็น None ถ้าสร้างไม่ได้

        # --- ฟังก์ชันภายในสำหรับอัพเดท UI ---
        def update_switch_ui(is_on):
            if not knob:
                return  # ออกถ้าสร้าง knob ไม่สำเร็จ
            try:
                target_x = on_x if is_on else off_x
                current_coords = canvas.coords(knob)
                if not current_coords:
                    # logging.warning("Could not get knob coordinates for toggle switch update.")
                    # ลองวาดใหม่ที่ตำแหน่งเป้าหมายเลย
                    canvas.coords(
                        knob,
                        target_x,
                        padding,
                        target_x + knob_diameter,
                        padding + knob_diameter,
                    )
                else:
                    current_x = current_coords[0]
                    # ตรวจสอบว่าต้องย้ายหรือไม่ ป้องกันการคำนวณที่ผิดพลาด
                    if abs(target_x - current_x) > 0.1:  # ใช้ค่า threshold เล็กน้อย
                        canvas.move(knob, target_x - current_x, 0)

                # เปลี่ยนสีพื้นหลัง track
                bg_color = bg_on_color if is_on else bg_off_color
                outline_color = bg_color if is_on else bg_outline
                canvas.itemconfigure("track", fill=bg_color, outline=outline_color)
            except tk.TclError as e_update:
                logging.error(f"Error updating toggle switch UI: {e_update}")
            except Exception as e_gen_update:
                logging.error(
                    f"Generic error updating toggle switch UI: {e_gen_update}"
                )

        # --- ฟังก์ชันภายในสำหรับ Toggle ---
        def toggle(event=None):
            new_state = not variable.get()
            variable.set(new_state)
            update_switch_ui(new_state)
            if command:
                try:
                    command(new_state)
                except Exception as e_cmd:
                    logging.error(f"Error executing toggle switch command: {e_cmd}")

        # --- ผูก Event ---
        canvas.bind("<Button-1>", toggle)

        # --- ตั้งค่า UI เริ่มต้น ---
        # เรียก update_switch_ui ครั้งแรกเพื่อแสดงสถานะปัจจุบันของ variable
        update_switch_ui(variable.get())

        # --- ทำให้ label คลิกได้ด้วย (ถ้ามี) ---
        if text and "label" in locals() and label.winfo_exists():
            label.bind("<Button-1>", toggle)
            label.configure(cursor="hand2")

        # +++ เก็บ Reference +++
        # เก็บ reference ของ canvas และฟังก์ชัน update UI ไว้กับ container
        container.switch_canvas = canvas
        container.update_ui_func = update_switch_ui

        # --- คืนค่า container ---
        return container

    def toggle_click_translate(self, value):
        """จัดการเมื่อมีการเปลี่ยนสถานะ Click Translate mode"""
        # บันทึกค่าใหม่ลงใน settings
        self.settings.set("enable_click_translate", value)

        # อัพเดท UI (เช่น เปลี่ยนสี หรือข้อความบนปุ่ม Force)
        force_button = getattr(self, "force_button", None)
        if force_button:
            if value:
                # ถ้าเปิด Click Translate mode ให้เน้นปุ่ม Force ให้ชัดเจนขึ้น
                force_button.config(bg="#e74c3c")  # สีแดงเข้ม
                force_button.config(
                    text="Translate 1 Time"
                )  # เปลี่ยนจาก "TOUCH" เป็น "Translate 1 Time"
                force_button.config(cursor="hand2")
                force_button.config(width=15)  # ขยายขนาดปุ่มให้แสดงข้อความได้พอดี
            else:
                # ถ้าปิด Click Translate mode ให้กลับไปใช้สีปกติ
                force_button.config(bg=self.theme.get("accent", "#00aaff"))
                force_button.config(text="FORCE")
                force_button.config(cursor="hand2")  # เก็บ cursor เป็น hand2
                force_button.config(width=7)  # คืนค่าขนาดปกติ

        # แจ้ง log การเปลี่ยนแปลง
        mode_str = "เปิด" if value else "ปิด"
        logging.info(f"{mode_str} Click Translate mode")

        # ฟังก์ชัน Force Button hover เดิมถูกลบออกแล้ว - ใช้ระบบ tooltip ปกติ

        # ฟังก์ชัน Force Button cooldown check เดิมถูกลบออกแล้ว - ใช้ระบบ tooltip ปกติ

        # ฟังก์ชัน Force Button hover leave เดิมถูกลบออกแล้ว - ใช้ระบบ tooltip ปกติ

        # ฟังก์ชัน Force feedback เดิมถูกลบออกแล้ว - ไม่จำเป็นสำหรับระบบปกติ

        # ฟังก์ชัน reset force hover state เดิมถูกลบออกแล้ว - ไม่จำเป็นสำหรับระบบปกติ

    def create_tooltip(self, widget, text_or_func, font_name=None, font_size=None):
        """
        สร้าง tooltip สำหรับ widget ที่กำหนด - ระบบปลอดภัยและเสถียร
        มี delay ป้องกันการกระพริบเมื่อ hover ข้าม elements ย่อย

        Args:
            widget: Widget ที่ต้องการสร้าง tooltip
            text_or_func: ข้อความ (str) หรือฟังก์ชันที่ส่งคืนข้อความที่จะแสดงใน tooltip
            font_name (str, optional): ชื่อฟอนต์สำหรับ tooltip
            font_size (int, optional): ขนาดฟอนต์สำหรับ tooltip
        """
        # เก็บ reference ของ timer และ tooltip ใน dictionary เพื่อให้ access ได้จากทุก nested function
        tooltip_data = {
            "hide_timer": None,
            "show_timer": None,  # เพิ่ม timer สำหรับ delay การแสดง
            "current_tooltip": None,
            "is_hovering": False,
            "is_creating": False,  # ป้องกันการสร้าง tooltip ซ้ำ
        }

        def show_tooltip(event):
            try:
                # ป้องกันการสร้าง tooltip ซ้ำขณะที่กำลังสร้างอยู่
                if tooltip_data["is_creating"]:
                    return

                # ตั้งสถานะว่ากำลัง hover อยู่
                tooltip_data["is_hovering"] = True

                # *** ซ่อน tooltip อื่นๆ ทั้งหมดก่อนสร้างใหม่ (บังคับทันที) ***
                self.hide_all_tooltips(force_immediate=True)

                # ยกเลิก timer การซ่อนถ้ามี (ป้องกันการกระพริบ)
                if tooltip_data["hide_timer"]:
                    self.root.after_cancel(tooltip_data["hide_timer"])
                    tooltip_data["hide_timer"] = None

                # ยกเลิก timer การแสดงเก่าถ้ามี
                if tooltip_data.get("show_timer"):
                    self.root.after_cancel(tooltip_data["show_timer"])
                    tooltip_data["show_timer"] = None

                # *** เพิ่ม delay 600ms ก่อนแสดง tooltip ***
                def delayed_show():
                    # ตรวจสอบว่ายังคง hover อยู่
                    if not tooltip_data["is_hovering"]:
                        return

                    try:
                        tooltip_data["is_creating"] = True

                        # ล้าง tooltip เก่าของ widget นี้เท่านั้น
                        if (
                            tooltip_data["current_tooltip"]
                            and tooltip_data["current_tooltip"].winfo_exists()
                        ):
                            try:
                                tooltip_data["current_tooltip"].destroy()
                            except:
                                pass
                            tooltip_data["current_tooltip"] = None

                        # กำหนดค่าเริ่มต้น
                        actual_text = (
                            text_or_func() if callable(text_or_func) else text_or_func
                        )
                        final_font_size = font_size or 10

                        # ใช้ unified tooltip method และเก็บ tooltip object ที่ได้
                        new_tooltip = self._show_unified_tooltip(
                            actual_text, widget, final_font_size
                        )
                        if new_tooltip:
                            tooltip_data["current_tooltip"] = new_tooltip

                        # รีเซ็ตสถานะการสร้าง tooltip เมื่อสำเร็จ
                        tooltip_data["is_creating"] = False

                    except Exception as e:
                        logging.error(f"Error in delayed tooltip show: {e}")
                        tooltip_data["is_creating"] = False

                # ตั้ง timer สำหรับแสดง tooltip หลัง 600ms
                tooltip_data["show_timer"] = self.root.after(600, delayed_show)
                return

            except Exception as e:
                logging.error(f"Error showing tooltip: {e}")
                tooltip_data["is_creating"] = False  # รีเซ็ตสถานะแม้เกิด error

        def hide_tooltip_safely(event=None):
            """ซ่อน tooltip ทันทีเมื่อเมาส์หลุดออก - ไม่มี delay"""
            try:
                # ตั้งสถานะว่าไม่ได้ hover อยู่แล้ว
                tooltip_data["is_hovering"] = False

                # ยกเลิก timer การแสดงถ้ามี
                if tooltip_data.get("show_timer"):
                    self.root.after_cancel(tooltip_data["show_timer"])
                    tooltip_data["show_timer"] = None

                # ยกเลิก timer การซ่อนเก่าถ้ามี
                if tooltip_data["hide_timer"]:
                    self.root.after_cancel(tooltip_data["hide_timer"])
                    tooltip_data["hide_timer"] = None

                # *** ซ่อนทันทีโดยไม่มี delay ***
                if (
                    tooltip_data["current_tooltip"]
                    and tooltip_data["current_tooltip"].winfo_exists()
                ):
                    try:
                        tooltip_data["current_tooltip"].destroy()
                        logging.debug(
                            f"Tooltip hidden immediately for widget: {widget}"
                        )
                    except Exception as destroy_error:
                        logging.error(f"Error destroying tooltip: {destroy_error}")
                    tooltip_data["current_tooltip"] = None

                # ลบจาก active_tooltips ถ้ามี
                if hasattr(self, "active_tooltips") and tooltip_data["current_tooltip"]:
                    try:
                        self.active_tooltips.remove(tooltip_data["current_tooltip"])
                    except ValueError:
                        pass  # ไม่มีในลิสต์

            except Exception as e:
                logging.error(f"Error hiding tooltip safely: {e}")

        def on_tooltip_enter(event=None):
            """เมื่อเมาส์เข้าสู่พื้นที่ tooltip"""
            tooltip_data["is_hovering"] = True
            # ยกเลิก timer การซ่อนและการแสดง
            if tooltip_data["hide_timer"]:
                self.root.after_cancel(tooltip_data["hide_timer"])
                tooltip_data["hide_timer"] = None
            if tooltip_data.get("show_timer"):
                self.root.after_cancel(tooltip_data["show_timer"])
                tooltip_data["show_timer"] = None

        def on_tooltip_leave(event=None):
            """เมื่อเมาส์ออกจากพื้นที่ tooltip - ซ่อนทันที"""
            hide_tooltip_safely()

        # ผูก events กับ widget หลัก - ใช้ระบบที่เชื่อถือได้
        def on_widget_enter(event):
            # ยกเลิก timer การซ่อนถ้ามี
            if tooltip_data["hide_timer"]:
                self.root.after_cancel(tooltip_data["hide_timer"])
                tooltip_data["hide_timer"] = None
            show_tooltip(event)

        def on_widget_leave(event):
            # ซ่อนทันทีและยกเลิก timer การแสดง
            if tooltip_data.get("show_timer"):
                self.root.after_cancel(tooltip_data["show_timer"])
                tooltip_data["show_timer"] = None
            hide_tooltip_safely(event)

        widget.bind("<Enter>", on_widget_enter)
        widget.bind("<Leave>", on_widget_leave)

        # เก็บ callbacks ไว้ใน widget สำหรับผูกกับ tooltip ที่จะสร้างขึ้น
        widget._tooltip_enter_callback = on_tooltip_enter
        widget._tooltip_leave_callback = on_tooltip_leave

        # ฟังก์ชัน Force Button tooltip พิเศษถูกลบออกแล้ว - ใช้ระบบปกติ

    def _create_integrated_force_tooltip(self, widget, text, font_size=12):
        """
        สร้าง tooltip สำหรับ Force Button ที่ทำงานร่วมกับ hover effects โดยไม่ขัดแย้ง
        ไม่ bind events ใหม่ แต่เก็บ tooltip data ไว้ให้ hover handlers เรียกใช้
        """
        # เก็บ tooltip data ไว้ใน widget
        widget._force_tooltip_text = text
        widget._force_tooltip_font_size = font_size
        widget._force_tooltip_data = {
            "hide_timer": None,
            "show_timer": None,
            "current_tooltip": None,
            "is_hovering": False,
            "is_creating": False,
        }

        # สร้าง callback functions ที่ hover effects จะเรียกใช้
        def show_force_tooltip():
            """แสดง tooltip สำหรับ force button"""
            try:
                tooltip_data = widget._force_tooltip_data

                if tooltip_data["is_creating"]:
                    return

                tooltip_data["is_hovering"] = True

                # ซ่อน tooltip อื่นๆ ก่อน
                self.hide_all_tooltips(force_immediate=True)

                # ยกเลิก timers เก่า
                if tooltip_data.get("show_timer"):
                    self.root.after_cancel(tooltip_data["show_timer"])
                    tooltip_data["show_timer"] = None
                if tooltip_data.get("hide_timer"):
                    self.root.after_cancel(tooltip_data["hide_timer"])
                    tooltip_data["hide_timer"] = None

                # เพิ่ม delay 600ms ก่อนแสดง
                def delayed_show():
                    if tooltip_data["is_hovering"]:
                        try:
                            tooltip_data["is_creating"] = True
                            self._show_unified_tooltip(text, widget, font_size)
                            tooltip_data["is_creating"] = False
                        except Exception as e:
                            logging.error(f"Error showing force tooltip: {e}")
                            tooltip_data["is_creating"] = False

                tooltip_data["show_timer"] = self.root.after(600, delayed_show)

            except Exception as e:
                logging.error(f"Error in show_force_tooltip: {e}")

        def hide_force_tooltip():
            """ซ่อน tooltip สำหรับ force button"""
            try:
                tooltip_data = widget._force_tooltip_data
                tooltip_data["is_hovering"] = False

                # ยกเลิก show timer
                if tooltip_data.get("show_timer"):
                    self.root.after_cancel(tooltip_data["show_timer"])
                    tooltip_data["show_timer"] = None

                # ซ่อนทันที
                self.hide_all_tooltips(force_immediate=True)

            except Exception as e:
                logging.error(f"Error in hide_force_tooltip: {e}")

        # เก็บ callbacks ไว้ใน widget
        widget._tooltip_enter_callback = lambda event=None: show_force_tooltip()
        widget._tooltip_leave_callback = lambda event=None: hide_force_tooltip()

    def hide_all_tooltips(self, force_immediate=False):
        """
        ซ่อน tooltip ทั้งหมดที่แสดงอยู่ - ระบบรวมศูนย์ที่ปลอดภัย

        Args:
            force_immediate (bool): ถ้าเป็น True จะบังคับให้ซ่อนทันทีโดยไม่สนใจ flag ป้องกัน
        """
        try:
            # ป้องกันการเรียกซ้ำขณะที่กำลังปิด tooltip อยู่ (เว้นแต่จะ force)
            if (
                not force_immediate
                and hasattr(self, "_hiding_tooltips")
                and self._hiding_tooltips
            ):
                return

            self._hiding_tooltips = True

            # ปิด tooltip ทั่วไป
            tooltips_to_remove = []
            for tooltip in self.active_tooltips:
                if tooltip and tooltip.winfo_exists():
                    try:
                        # ยกเลิก auto hide timer ถ้ามี
                        if hasattr(tooltip, "_auto_hide_timer"):
                            try:
                                tooltip.after_cancel(tooltip._auto_hide_timer)
                            except:
                                pass
                        tooltip.destroy()
                    except Exception as e:
                        logging.error(f"Error destroying tooltip: {e}")
                    tooltips_to_remove.append(tooltip)
                else:
                    tooltips_to_remove.append(tooltip)

            # ลบ tooltip ที่ปิดแล้วออกจาก list
            for tooltip in tooltips_to_remove:
                if tooltip in self.active_tooltips:
                    self.active_tooltips.remove(tooltip)

            # ปิด force button tooltip เฉพาะ
            if (
                hasattr(self, "manual_force_tooltip")
                and self.manual_force_tooltip is not None
            ):
                if self.manual_force_tooltip.winfo_exists():
                    try:
                        # ยกเลิก auto hide timer ถ้ามี
                        if hasattr(self.manual_force_tooltip, "_auto_hide_timer"):
                            try:
                                self.manual_force_tooltip.after_cancel(
                                    self.manual_force_tooltip._auto_hide_timer
                                )
                            except:
                                pass
                        self.manual_force_tooltip.destroy()
                    except Exception as e:
                        logging.error(f"Error destroying force tooltip: {e}")
                self.manual_force_tooltip = None

            logging.debug("All tooltips hidden successfully")

        except Exception as e:
            logging.error(f"Error in hide_all_tooltips: {e}")
            # ล้างข้อมูลในกรณีที่เกิดข้อผิดพลาด
            if hasattr(self, "active_tooltips"):
                self.active_tooltips.clear()
            if hasattr(self, "manual_force_tooltip"):
                self.manual_force_tooltip = None
        finally:
            # คืนค่าสถานะ
            self._hiding_tooltips = False

    def hide_tooltip(self):
        """ซ่อน tooltip ถ้ามีการแสดงอยู่ - เวอร์ชันที่ปลอดภัย"""
        try:
            self.hide_all_tooltips()
        except Exception as e:
            logging.error(f"Error in hide_tooltip: {e}")

    def _show_unified_tooltip(self, text, widget=None, font_size=10, header_color=None):
        """
        แสดง tooltip ที่ตำแหน่งเดียวกันทั้งหมด - ใต้ control UI กึ่งกลาง
        พร้อม design สวยงามแบบ modern UI ไม่มีขอบ และรองรับสีหัวข้อแบบไดนามิก

        Args:
            text: ข้อความที่จะแสดง
            widget: widget ที่เรียกใช้ (ใช้สำหรับการหาสี theme)
            font_size: ขนาดฟอนต์
            header_color: สีหัวข้อ (ถ้าไม่กำหนดจะใช้สีจาก theme)
        """
        try:
            self.hide_all_tooltips(force_immediate=True)

            tooltip = tk.Toplevel(self.root)
            tooltip.wm_overrideredirect(True)
            tooltip.attributes("-topmost", False)  # ให้แสดงใต้ control UI
            tooltip.attributes("-alpha", 0.0)  # เริ่มต้นที่ alpha 0 (ซ่อนก่อน)

            # ขนาดและฟอนต์มาตรฐาน
            standard_font_size = 11
            standard_width = 280  # เพิ่มขนาดกว้างขึ้นเล็กน้อย
            standard_padding_x = 18
            standard_padding_y_top = 20
            standard_padding_y_bottom = 15

            # กำหนดสีหัวข้อ - ใช้สีจาก theme หรือสีที่กำหนด
            if not header_color:
                # พยายามหาสีจาก widget ที่เรียกใช้
                if widget:
                    try:
                        # ถ้าเป็นปุ่ม preset ให้ใช้สี accent
                        if hasattr(widget, "preset_num"):
                            # preset 3 (Ex-Choice) ใช้สีพิเศษ
                            if widget.preset_num == 3:
                                header_color = "#FF8C00"  # สีส้มเข้มพิเศษ
                            else:
                                header_color = self.theme.get("accent", "#6c5ce7")
                        # ถ้าเป็นปุ่ม area ให้ใช้สี accent_light
                        elif (
                            hasattr(widget, "cget")
                            and "area" in str(widget.cget("text")).lower()
                        ):
                            header_color = self.theme.get("accent_light", "#87CEFA")
                        # ถ้าเป็นปุ่ม CPU ให้ใช้สีส้ม
                        elif hasattr(widget, "cget") and "%" in str(
                            widget.cget("text")
                        ):
                            header_color = "#FFA500"  # สีส้ม
                        # ถ้าเป็นปุ่ม Save ให้ใช้สีเขียว
                        elif (
                            hasattr(widget, "cget")
                            and "save" in str(widget.cget("text")).lower()
                        ):
                            header_color = self.theme.get("success", "#4CAF50")
                        # ถ้าเป็นปุ่ม Reset ให้ใช้สีแดง
                        elif (
                            hasattr(widget, "cget")
                            and "reset" in str(widget.cget("text")).lower()
                        ):
                            header_color = "#FF6B6B"
                        else:
                            header_color = self.theme.get("accent", "#6c5ce7")
                    except:
                        header_color = self.theme.get("accent", "#6c5ce7")
                else:
                    header_color = self.theme.get("accent", "#6c5ce7")

            # สร้างกรอบพื้นหลังแบบขอบโค้งมน
            bg_frame = tk.Frame(tooltip, bg="#1a1a1a", relief="flat", bd=0)  # สีดำเข้ม
            bg_frame.pack(fill="both", expand=True)

            # เพิ่มขอบโค้งมนให้ tooltip ใหม่ - ใช้วิธีเดียวกับ UI หลัก
            def apply_rounded_corners():
                try:
                    # อัพเดท UI ให้แสดงผลเสร็จก่อน
                    tooltip.update_idletasks()
                    # ใช้ฟังก์ชัน create_rounded_frame ที่มีอยู่แล้ว
                    self.create_rounded_frame(tooltip, radius=15)
                    # แสดง tooltip หลังจากทำขอบโค้งเสร็จแล้ว
                    tooltip.attributes("-alpha", 0.95)
                    logging.debug(
                        f"Applied rounded corners to tooltip and made visible"
                    )
                except Exception as e:
                    # หากทำขอบโค้งไม่สำเร็จ ให้แสดง tooltip แบบปกติ
                    tooltip.attributes("-alpha", 0.95)
                    logging.debug(f"Could not apply rounded corners to tooltip: {e}")

            # ใช้ delay เล็กน้อยเพื่อให้ tooltip พร้อมแสดงผล
            tooltip.after(10, apply_rounded_corners)

            # จัดการข้อความแบบใหม่ - แยกหัวข้อและเนื้อหา
            lines = text.split("\n")
            formatted_content = []

            # ฟังก์ชันตรวจสอบภาษาและเลือกฟอนต์ที่เหมาะสม
            def get_font_for_text(text_line, size, is_header=False):
                """เลือกฟอนต์ตามภาษาของข้อความ"""
                # ตรวจสอบว่ามีตัวอักษรไทยหรือไม่
                has_thai = any("\u0e00" <= char <= "\u0e7f" for char in text_line)

                if has_thai:
                    # ใช้ฟอนต์ Anuphan สำหรับข้อความไทย (ไม่ใช้ bold ตามที่ขอ)
                    return ("Anuphan", size)
                else:
                    # ใช้ฟอนต์ FC Minimal สำหรับข้อความอังกฤษ (ไม่ใช้ bold ตามที่ขอ)
                    return ("FC Minimal", size)

            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    formatted_content.append("")
                    continue

                if ":" in line and i == 0:  # บรรทัดแรกที่มี : ถือว่าเป็นหัวข้อ
                    parts = line.split(":", 1)
                    if len(parts) == 2:
                        header = parts[0].strip()
                        description = parts[1].strip()
                        formatted_content.append(f"● {header}")
                        if description:
                            formatted_content.append(f"  {description}")
                    else:
                        formatted_content.append(f"● {line}")
                elif (
                    line.startswith("⚠️")
                    or line.startswith("✅")
                    or line.startswith("🔸")
                ):
                    # บรรทัดที่มีไอคอนพิเศษ
                    formatted_content.append(f"  {line}")
                elif line.startswith("-") or line.startswith("•"):
                    # รายการย่อย
                    clean_line = line.lstrip("-• ").strip()
                    formatted_content.append(f"  • {clean_line}")
                else:
                    # เนื้อหาทั่วไป
                    formatted_content.append(f"  {line}")

            # สร้าง Rich Text widget แทน Label ธรรมดา
            import tkinter.font as tkFont

            # ใช้ฟอนต์ที่เหมาะสมสำหรับ text widget หลัก (default เป็นภาษาอังกฤษ)
            default_font = get_font_for_text(text, standard_font_size)

            text_widget = tk.Text(
                bg_frame,
                bg="#1a1a1a",
                fg="#ffffff",
                relief="flat",
                bd=0,
                wrap="word",
                width=1,  # จะคำนวณใหม่
                height=1,  # จะคำนวณใหม่
                font=default_font,
                selectbackground="#3a3a3a",
                selectforeground="#ffffff",
                state="disabled",  # ไม่ให้แก้ไขได้
                cursor="arrow",
            )

            # เพิ่มเนื้อหาพร้อมสี
            text_widget.config(state="normal")

            for i, line in enumerate(formatted_content):
                if i == 0 and line.startswith("●"):  # หัวข้อ
                    text_widget.insert("end", line + "\n", "header")
                elif line.strip():
                    text_widget.insert("end", line + "\n", "content")
                else:
                    text_widget.insert("end", "\n")

            # กำหนดสไตล์ข้อความ - ใช้ฟอนต์ตามภาษาและไม่ใช้ Bold
            # สำหรับ header - ตรวจสอบภาษาจากบรรทัดแรก
            first_line = formatted_content[0] if formatted_content else ""
            header_font = get_font_for_text(first_line, standard_font_size + 1)

            text_widget.tag_config(
                "header",
                foreground=header_color,
                font=header_font,  # ไม่ใช้ bold ตามที่ขอ
            )

            # สำหรับ content - ใช้ฟอนต์ปกติ
            content_font = get_font_for_text(text, standard_font_size)
            text_widget.tag_config(
                "content",
                foreground="#e0e0e0",
                font=content_font,
            )

            text_widget.config(state="disabled")

            # คำนวณขนาดที่เหมาะสม - ใช้ฟอนต์ที่เหมาะสมตามภาษา
            default_font_obj = tkFont.Font(family=default_font[0], size=default_font[1])
            max_line_width = 0
            line_count = len(formatted_content)

            for line in formatted_content:
                if line.strip():
                    # ใช้ฟอนต์ที่เหมาะสมสำหรับแต่ละบรรทัด
                    line_font = get_font_for_text(line, standard_font_size)
                    font_obj = tkFont.Font(family=line_font[0], size=line_font[1])
                    line_width = font_obj.measure(line)
                    max_line_width = max(max_line_width, line_width)

            # กำหนดขนาด text widget
            char_width = default_font_obj.measure("0")
            text_width = min(max(max_line_width // char_width + 5, 25), 50)  # จำกัดขนาด
            text_height = max(line_count, 2)

            text_widget.config(width=text_width, height=text_height)
            text_widget.pack(
                padx=standard_padding_x,
                pady=(standard_padding_y_top, standard_padding_y_bottom),
                fill="both",
                expand=True,
            )

            # อัปเดตและคำนวณขนาด
            tooltip.update_idletasks()

            # ตำแหน่งตรงกลางใต้ control UI พร้อม overlap - ใช้ absolute coordinates
            self_x = self.root.winfo_rootx()  # ตำแหน่งจริงในระบบพิกัด Windows
            self_y = self.root.winfo_rooty()  # ตำแหน่งจริงในระบบพิกัด Windows
            self_width = self.root.winfo_width()
            self_height = self.root.winfo_height()

            tooltip_width = tooltip.winfo_reqwidth()
            tooltip_height = tooltip.winfo_reqheight()

            # ตำแหน่ง X: กึ่งกลางของ control UI
            tooltip_x = self_x + (self_width // 2) - (tooltip_width // 2)

            # ตำแหน่ง Y: ใต้ control UI ห่างออกไป 5px ตามที่ขอ
            tooltip_y = self_y + self_height + 5

            # ตรวจสอบขอบเขตหน้าจอ - ใช้ virtual screen สำหรับ multi-monitor
            try:
                import tkinter as tk_temp

                temp_root = tk_temp.Tk()
                temp_root.withdraw()

                # ใช้ virtual screen dimensions สำหรับหลายจอภาพ
                virtual_width = temp_root.winfo_vrootwidth()
                virtual_height = temp_root.winfo_vrootheight()
                virtual_x = temp_root.winfo_vrootx()
                virtual_y = temp_root.winfo_vrooty()

                temp_root.destroy()

                # ปรับตำแหน่ง X ถ้าเลยขอบ virtual screen
                if tooltip_x + tooltip_width > virtual_x + virtual_width:
                    tooltip_x = virtual_x + virtual_width - tooltip_width - 10
                if tooltip_x < virtual_x + 10:
                    tooltip_x = virtual_x + 10

                # ปรับตำแหน่ง Y ถ้าเลยขอบ virtual screen
                if tooltip_y + tooltip_height > virtual_y + virtual_height:
                    tooltip_y = self_y - tooltip_height - 5  # แสดงด้านบนแทน ห่าง 5px
                if tooltip_y < virtual_y:
                    tooltip_y = virtual_y + 10

            except Exception as e:
                logging.warning(
                    f"Could not get virtual screen info, using fallback: {e}"
                )
                # Fallback ใช้วิธีเดิมถ้าไม่สามารถหา virtual screen ได้
                screen_width = self.root.winfo_screenwidth()
                screen_height = self.root.winfo_screenheight()

                if tooltip_x + tooltip_width > screen_width:
                    tooltip_x = screen_width - tooltip_width - 10
                if tooltip_x < 10:
                    tooltip_x = 10

                if tooltip_y + tooltip_height > screen_height:
                    tooltip_y = self_y - tooltip_height - 5  # แสดงด้านบนแทน ห่าง 5px

            tooltip.geometry(f"+{tooltip_x}+{tooltip_y}")

            # เก็บ tooltip สำหรับการจัดการ
            if not hasattr(self, "active_tooltips"):
                self.active_tooltips = []
            self.active_tooltips.append(tooltip)

            # ใช้ระบบ callback ที่ผูกกับ source widget สำหรับการซ่อน
            if widget and hasattr(widget, "_tooltip_leave_callback"):

                def auto_hide_unified():
                    """ซ่อน unified tooltip เมื่อเมาส์ออกจากปุ่มต้นทาง"""
                    try:
                        if tooltip and tooltip.winfo_exists():
                            tooltip.destroy()
                        if (
                            hasattr(self, "active_tooltips")
                            and tooltip in self.active_tooltips
                        ):
                            self.active_tooltips.remove(tooltip)
                        logging.debug(
                            f"Unified tooltip hidden via source widget callback"
                        )
                    except Exception as e:
                        logging.debug(f"Error in auto_hide_unified: {e}")

                # แทนที่ callback เดิมชั่วคราว
                original_callback = widget._tooltip_leave_callback

                def combined_callback(event=None):
                    auto_hide_unified()
                    if original_callback:
                        original_callback(event)

                widget._tooltip_leave_callback = combined_callback

            logging.debug(f"Unified tooltip shown at ({tooltip_x}, {tooltip_y})")

            # ส่งกลับ tooltip object เพื่อให้ caller สามารถเก็บไว้ได้
            return tooltip

        except Exception as e:
            logging.error(f"Error showing unified tooltip: {e}")
            return None

    def add_button_hover_effect(self, button, hover_color=None, original_color=None):
        """
        เพิ่ม hover effect ให้กับปุ่ม tkinter Button

        Args:
            button: tkinter Button object
            hover_color: สีเมื่อ hover (ถ้าไม่กำหนดจะใช้สีรอง)
            original_color: สีเดิมของปุ่ม (ถ้าไม่กำหนดจะใช้ bg ปัจจุบัน)
        """
        if not hover_color:
            # ใช้สีรองเป็น hover color
            hover_color = self.theme.get(
                "secondary", self.theme.get("accent_light", "#87CEFA")
            )

        if not original_color:
            original_color = button.cget("bg")

        def on_enter(event):
            # เช็คว่าปุ่มไม่ได้ถูก disable และยังมี bg color
            if button.cget("state") != "disabled":
                try:
                    button.config(bg=hover_color)
                except tk.TclError:
                    pass  # ignore if button is destroyed

        def on_leave(event):
            # เช็คว่าปุ่มไม่ได้ถูก disable และยังมี bg color
            if button.cget("state") != "disabled":
                try:
                    button.config(bg=original_color)
                except tk.TclError:
                    pass  # ignore if button is destroyed

        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

        # เก็บสีเดิมไว้ใน button object เผื่อต้องใช้ภายหลัง
        button._original_bg = original_color
        button._hover_bg = hover_color

        # เพิ่มฟังก์ชันช่วยสำหรับอัปเดตสีเมื่อ state เปลี่ยน
        def update_hover_colors(new_original=None, new_hover=None):
            if new_original:
                button._original_bg = new_original
                original_color = new_original
            if new_hover:
                button._hover_bg = new_hover

        button.update_hover_colors = update_hover_colors

    def create_rounded_frame(self, frame, radius=15):
        """ทำให้ frame มีขอบโค้งมน

        Args:
            frame: tk.Frame ที่ต้องการทำให้โค้งมน
            radius: รัศมีของขอบโค้ง
        """
        try:
            # รอให้ frame แสดงผล
            frame.update_idletasks()

            # ดึงค่า HWND ของ frame
            hwnd = windll.user32.GetParent(frame.winfo_id())

            # ลบกรอบและหัวข้อ
            style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
            style &= ~win32con.WS_CAPTION
            style &= ~win32con.WS_THICKFRAME
            win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)

            # สร้างภูมิภาค (region) โค้งมน
            width = frame.winfo_width()
            height = frame.winfo_height()
            region = win32gui.CreateRoundRectRgn(0, 0, width, height, radius, radius)

            # กำหนดภูมิภาคให้กับ frame
            win32gui.SetWindowRgn(hwnd, region, True)

            return True
        except Exception as e:
            print(f"Error creating rounded frame: {e}")
            return False

    def ensure_preset_area_consistency(self):
        """
        ตรวจสอบและรักษาความสอดคล้องระหว่าง preset และสถานะพื้นที่
        กำหนดค่าเริ่มต้นสำหรับ preset ทั้ง 6 ปุ่ม
        """
        try:
            # ตรวจสอบว่ามี presets ครบหรือไม่
            if len(self.presets) < 6:  # เปลี่ยนจาก 5 เป็น 6
                # สร้าง default presets ถ้ายังไม่มี
                default_presets = [
                    {"name": "dialog", "areas": "A+B", "role": "dialog"},
                    {"name": "lore", "areas": "C", "role": "lore"},
                    {"name": "Ex-Choice", "areas": "A+B", "role": "choice"},
                    {"name": "custom1", "areas": "B", "role": "custom"},
                    {"name": "custom2", "areas": "B+C", "role": "custom"},
                    {"name": "custom3", "areas": "A+C", "role": "custom"},
                ]
                self.settings.set("area_presets", default_presets)
                self.presets = default_presets

            # ตรวจสอบว่า preset 1 (dialog) มีพื้นที่ A+B หรือไม่
            if len(self.presets) >= 1:
                preset_1 = self.presets[0]
                if preset_1.get("areas") != "A+B":
                    # ถ้าไม่ใช่ ให้อัพเดตเป็น A+B
                    preset_1["areas"] = "A+B"
                    preset_1["role"] = (
                        "dialog" if "role" not in preset_1 else preset_1["role"]
                    )
                    # บันทึกกลับไปที่ settings
                    self.settings.save_preset(1, "A+B", preset_1.get("coordinates", {}))

                # อัพเดตสถานะพื้นที่ให้ตรงกับ preset ปัจจุบัน
                current_preset_data = self.settings.get_preset(self.current_preset)
                if current_preset_data:
                    current_areas = current_preset_data.get("areas", "A+B").split("+")
                    for area in ["A", "B", "C"]:
                        self.area_states[area] = area in current_areas
                else:
                    # หากไม่มีข้อมูล preset ปัจจุบัน ใช้ค่าเริ่มต้น
                    self.area_states["A"] = True
                    self.area_states["B"] = True
                    self.area_states["C"] = False

            else:
                # ในกรณีที่ไม่สามารถโหลดข้อมูล preset ได้ ให้ใช้ค่าเริ่มต้น
                self.area_states["A"] = True
                self.area_states["B"] = True
                self.area_states["C"] = False

        except Exception as e:
            print(f"Error ensuring preset-area consistency: {e}")
            # ในกรณีที่เกิดข้อผิดพลาด ให้ใช้ค่าเริ่มต้น
            self.area_states["A"] = True
            self.area_states["B"] = True
            self.area_states["C"] = False

    def setup_window(self):
        """
        ตั้งค่าหน้าต่างหลักของ Control UI
        """
        logging.info("Setting up Control UI window")

        self.root.title("Control UI")
        # *** ปรับขนาดหน้าต่างให้พอดีกับเนื้อหา ***
        self.root.geometry("340x260")  # ลดความสูงจาก 440 เป็น 260
        self.root.overrideredirect(True)
        self.root.attributes("-alpha", 0.95)
        self.root.attributes("-topmost", True)

        # ดึงค่าสีจาก appearance_manager โดยตรง
        self.theme = {
            "bg": appearance_manager.bg_color,
            "accent": appearance_manager.get_accent_color(),
            "accent_light": appearance_manager.get_theme_color("accent_light"),
            "secondary": appearance_manager.get_theme_color("secondary"),
            "button_bg": appearance_manager.get_theme_color("button_bg"),
            "text": appearance_manager.get_theme_color("text", "#ffffff"),
            "text_dim": appearance_manager.get_theme_color("text_dim", "#b2b2b2"),
            "highlight": appearance_manager.get_highlight_color(),
            "error": appearance_manager.get_theme_color("error", "#FF4136"),
            "success": appearance_manager.get_theme_color("success", "#4CAF50"),
            "button_inactive_bg": appearance_manager.get_theme_color(
                "button_inactive_bg", "#555555"
            ),
            "border": appearance_manager.get_theme_color("border", "#444444"),
            "fg": appearance_manager.get_theme_color("text", "#ffffff"),  # เพิ่ม fg
        }

        # สร้าง main frame - แก้ไขการจัดวางให้ title area อยู่บนสุด
        self.main_frame = tk.Frame(
            self.root,
            bg=self.theme["bg"],
            highlightthickness=0,
            padx=3,
            pady=0,  # ไม่มี padding เพื่อให้ title frame อยู่บนสุดของหน้าต่าง
            bd=0,
        )
        self.main_frame.pack(fill=tk.BOTH, expand=True, anchor="n")  # เพิ่ม anchor="n" ให้อยู่บนสุด

        # Close button - วางมุมขวาบนของหน้าต่าง
        self.close_button = tk.Label(
            self.root,
            text="✕",  # ใช้ symbol ✕ ที่ดูสวยกว่า
            font=("Arial", 10, "bold"),  # ลดขนาดให้เหมาะสม
            bg=self.theme["bg"],  # ใช้สีพื้นหลังของธีม
            fg="#808080",  # สีเทาอ่อน
            cursor="hand2",
            width=2,
            height=1,
            relief="flat",
            bd=0,
            padx=2,
            pady=1
        )
        self.close_button.place(x=310, y=5)  # วางมุมขวาบน (340-30=310)
        self.close_button.lift()
        
        # Event handlers สำหรับ close button
        def on_close_enter(event):
            self.close_button.config(fg="#ffffff")  # เปลี่ยนเป็นสีขาว
        
        def on_close_leave(event):
            self.close_button.config(fg="#808080")  # กลับเป็นสีเทาอ่อน
        
        def on_close_click(event):
            self.close_window()
        
        self.close_button.bind("<Enter>", on_close_enter)
        self.close_button.bind("<Leave>", on_close_leave)
        self.close_button.bind("<Button-1>", on_close_click)
        
        # Main Title at the top (Control UI)
        self.main_title_label = tk.Label(
            self.main_frame,
            text="Control UI",
            font=("FC Minimal Medium", 12, "bold"),
            bg=self.theme["bg"],
            fg=self.theme["accent"],
        )
        self.main_title_label.pack(pady=(5, 0))  # Center at top with small padding
        

        # Header Separator - REMOVED (ลบเส้นแบ่งด้านบนออก)

        # *** เพิ่มการทำขอบโค้งมนเหมือน MBB ***
        # รอให้หน้าต่างแสดงผลเสร็จก่อนจึงทำขอบโค้ง
        self.root.after(100, lambda: self.create_rounded_frame(self.root, radius=15))
        
    def debug_button_position(self):
        """Debug method เพื่อตรวจสอบตำแหน่งของ close button"""
        try:
            print(f"DEBUG: Window geometry: {self.root.geometry()}")
            print(f"DEBUG: Main frame: {self.main_frame.winfo_width()}x{self.main_frame.winfo_height()}")
            print(f"DEBUG: Close button visible: {self.close_button.winfo_ismapped()}")
            print(f"DEBUG: Close button: {self.close_button.winfo_width()}x{self.close_button.winfo_height()}")
            print(f"DEBUG: Close button position: x={self.close_button.winfo_x()}, y={self.close_button.winfo_y()}")
            
            # ลองยก close button ขึ้นมาด้านบนและตรวจสอบอีกครั้ง
            self.close_button.lift()
            self.root.after(10, lambda: print(f"DEBUG: After lift - Close button visible: {self.close_button.winfo_ismapped()}"))
        except Exception as e:
            print(f"DEBUG: Error getting widget info: {e}")

    def load_preset(self, preset_number=None):
        """
        โหลด preset ตามหมายเลขที่กำหนด หรือใช้ preset ปัจจุบัน
        และอัพเดท UI รวมถึงแจ้ง MBB (คล้าย _complete_preset_switch)

        Args:
            preset_number: หมายเลข preset (1-5) หรือไม่ระบุ (ใช้ค่าปัจจุบัน)
        """
        try:
            # ถ้าไม่ระบุหมายเลข preset ให้ใช้ค่าปัจจุบัน
            if preset_number is None:
                preset_number = self.current_preset

            # ตรวจสอบว่า preset_number อยู่ในช่วงที่ถูกต้อง
            if not (1 <= preset_number <= self.max_presets):
                preset_number = 1  # ถ้าไม่ถูกต้อง ใช้ preset 1

            # ไม่เปลี่ยน current_preset ที่นี่ เพราะอาจเป็นการโหลดเพื่อแสดงผลชั่วคราว
            # หรือถ้าเป็นการโหลดถาวร ควรเรียกผ่าน select_preset/_complete_preset_switch

            # ดึงข้อมูล preset จาก settings
            preset_data = self.settings.get_preset(preset_number)
            if not preset_data:
                logging.error(
                    f"Cannot find preset data for {preset_number} during load_preset"
                )
                preset_data = self.settings.get_preset(1)  # Fallback to preset 1
                if not preset_data:
                    logging.error(
                        "Failed to load even Preset 1 data during load_preset."
                    )
                    return False  # Indicate failure

            # ดึงข้อมูลพื้นที่และพิกัด
            area_config = preset_data.get("areas", "A")
            coordinates = preset_data.get("coordinates", {})

            # *** ส่วนที่แตกต่าง: เราอาจจะแค่ต้องการอัพเดท state และ UI ชั่วคราว ***
            # *** หรือถ้าเป็นการโหลดถาวร ก็ควรทำเหมือน _complete_preset_switch ***

            # --- สมมติว่าเป็นการโหลดเพื่อใช้งานจริง ---
            self.current_preset = (
                preset_number  # ถ้าเป็นการโหลดถาวร ก็ต้องตั้ง current_preset
            )
            self.settings.set("current_preset", self.current_preset)

            # อัพเดตพิกัด (เหมือน _complete_preset_switch)
            if isinstance(coordinates, dict):
                for area, coords in coordinates.items():
                    if isinstance(coords, dict) and all(
                        k in coords for k in ["start_x", "start_y", "end_x", "end_y"]
                    ):
                        self.settings.set_translate_area(
                            coords["start_x"],
                            coords["start_y"],
                            coords["end_x"],
                            coords["end_y"],
                            area,
                        )
                    else:
                        logging.warning(
                            f"Invalid coordinates data for area {area} in preset {preset_number} during load_preset: {coords}"
                        )

            # อัพเดตสถานะการแสดงพื้นที่ใน Control UI ให้ตรงกับ preset
            active_areas = area_config.split("+")
            for area in ["A", "B", "C"]:
                self.area_states[area] = area in active_areas

            # อัพเดต UI ของ Control UI
            self.update_preset_buttons()
            self.update_button_highlights()

            # แจ้งการเปลี่ยนแปลงพื้นที่ไปยัง MBB.py
            if self.switch_area_callback:
                self.switch_area_callback(active_areas)

            self.has_unsaved_changes = False  # การโหลด preset ถือว่าเป็นการ re-sync

            logging.info(
                f"Loaded preset {preset_number}. Active areas set to: {area_config}"
            )
            return True
            # --- จบส่วนสมมติว่าโหลดถาวร ---

        except Exception as e:
            print(f"Error loading preset: {e}")
            logging.error(f"Error loading preset: {e}")
            # Fallback logic (อาจจะไม่จำเป็นถ้าใช้ _complete_preset_switch)
            for area in ["A", "B", "C"]:
                self.area_states[area] = area in ["A", "B"]
            self.update_button_highlights()
            return False

    def show_preset_switch_feedback(self, old_preset, new_preset):
        """แสดงข้อความแจ้งเตือนเมื่อมีการสลับ preset

        Args:
            old_preset: หมายเลข preset เดิม
            new_preset: หมายเลข preset ใหม่
        """
        try:
            # สร้างหน้าต่างแจ้งเตือน
            feedback = tk.Toplevel(self.root)
            feedback.overrideredirect(True)
            feedback.configure(bg=self.theme["bg"])
            feedback.attributes("-alpha", 0.9)
            feedback.attributes("-topmost", True)

            # สร้าง frame หลักแบบโค้งมน
            main_frame = tk.Frame(feedback, bg=self.theme["bg"], padx=15, pady=10)
            main_frame.pack()

            # สร้างข้อความที่สวยงาม
            msg_frame = tk.Frame(main_frame, bg=self.theme["bg"])
            msg_frame.pack()

            # ดึงชื่อของพื้นที่จาก preset
            old_areas = "unknown"
            new_areas = "unknown"

            if old_preset <= len(self.presets):
                old_areas = self.presets[old_preset - 1].get("areas", "unknown")
            if new_preset <= len(self.presets):
                new_areas = self.presets[new_preset - 1].get("areas", "unknown")

            # ดึงชื่อที่จะแสดงของ preset
            old_display_name = self.settings.get_preset_display_name(old_preset)
            new_display_name = self.settings.get_preset_display_name(new_preset)

            # สร้างข้อความแจ้งเตือน
            tk.Label(
                msg_frame,
                text=f"Switched preset",
                fg=self.theme["highlight"],
                bg=self.theme["bg"],
                font=("FC Minimal Medium", 10),
            ).pack(side=tk.TOP)

            tk.Label(
                msg_frame,
                text=f"{old_display_name} ({old_areas}) → {new_display_name} ({new_areas})",
                fg="#2ecc71",
                bg=self.theme["bg"],
                font=("FC Minimal Medium", 10),
            ).pack(side=tk.TOP)

            # คำนวณตำแหน่ง (กลางจอ)
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()

            feedback_width = 220  # กำหนดขนาดของ feedback
            feedback_height = 80

            x = (screen_width - feedback_width) // 2
            y = (screen_height - feedback_height) // 2

            # กำหนดตำแหน่ง
            feedback.geometry(f"{feedback_width}x{feedback_height}+{x}+{y}")

            # เอฟเฟกต์ fade-in fade-out
            feedback.attributes("-alpha", 0.0)

            def fade_in():
                for i in range(0, 10):
                    if feedback.winfo_exists():
                        feedback.attributes("-alpha", i / 10)
                        feedback.update()
                        feedback.after(20)

            def fade_out():
                for i in range(10, -1, -1):
                    if feedback.winfo_exists():
                        feedback.attributes("-alpha", i / 10)
                        feedback.update()
                        feedback.after(20)
                    if feedback.winfo_exists():
                        feedback.destroy()

            fade_in()
            feedback.after(1500, fade_out)  # แสดง 1.5 วินาที
        except Exception as e:
            print(f"Error showing preset switch feedback: {e}")

    def save_preset(self):
        """บันทึก preset ปัจจุบันพร้อมพิกัด"""
        current_areas = self.get_current_area_string()

        # *** โหลดข้อมูล preset เดิมก่อน ***
        preset_data = self.settings.get_preset(self.current_preset)
        if preset_data is None:
            logging.error(
                f"Could not load existing preset data for preset {self.current_preset}. Aborting save."
            )
            # อาจจะแสดงข้อความแจ้งเตือนผู้ใช้
            return

        # *** สร้าง dictionary ใหม่เพื่อเก็บพิกัด ***
        # - ใช้ dictionary ใหม่เพื่อป้องกันการอ้างอิงถึงออบเจ็กต์เดิม
        new_coordinates = {}

        # รวบรวมพิกัดใหม่ของพื้นที่ที่ *กำลัง* เลือก (จาก settings ที่อาจถูกอัปเดตจากการ crop)
        for area in current_areas.split("+"):
            area_coords = self.settings.get_translate_area(area)
            if area_coords:
                # *** สร้างสำเนาพิกัดเพื่อป้องกันการอ้างอิงไปยังออบเจกต์เดิม ***
                new_coordinates[area] = {
                    "start_x": area_coords["start_x"],
                    "start_y": area_coords["start_y"],
                    "end_x": area_coords["end_x"],
                    "end_y": area_coords["end_y"],
                }

        # บันทึกเฉพาะพื้นที่ที่กำลังเลือกและพิกัดที่เพิ่งสร้างใหม่
        # *** ไม่ใช้ existing_coordinates.update ที่อาจทำให้เกิดการอ้างอิงร่วมกัน ***
        logging.info(
            f"Saving preset {self.current_preset} with areas '{current_areas}' and {len(new_coordinates)} coordinate sets"
        )
        self.settings.save_preset(self.current_preset, current_areas, new_coordinates)

        # เพิ่มบรรทัดนี้: บันทึกค่า current_preset ลง settings เพื่อการโหลดครั้งถัดไป
        self.settings.set("current_preset", self.current_preset)
        # บันทึก settings ทันที (เพื่อความแน่ใจว่าจะถูกบันทึก)
        if hasattr(self.settings, "save_settings"):
            self.settings.save_settings()

        # ตั้งค่า has_unsaved_changes เป็น False
        self.has_unsaved_changes = False

        # เรียก update_button_highlights เพื่ออัปเดท UI ของปุ่ม Save โดยเฉพาะ
        self.update_button_highlights()

        # แสดง feedback
        self.show_save_feedback()

        logging.info(
            f"Saved preset {self.current_preset} successfully. Save button should now be disabled."
        )
        
        # อัพเดตสถานะปุ่ม EDIT หลังจาก save
        self.update_edit_button_state()

    def load_current_preset(self):
        """โหลด preset พร้อมพิกัด"""
        if self.current_preset <= len(self.presets):
            preset = self.presets[self.current_preset - 1]

            # โหลดพื้นที่
            areas = preset["areas"].split("+")
            for area in ["A", "B", "C"]:
                self.area_states[area] = area in areas

            # โหลดพิกัด
            if "coordinates" in preset:
                for area, coords in preset["coordinates"].items():
                    self.settings.set_translate_area(
                        coords["start_x"],
                        coords["start_y"],
                        coords["end_x"],
                        coords["end_y"],
                        area,
                    )

            self.update_button_highlights()
            self.update_preset_display()

    def update_preset_display(self):
        """อัพเดทการแสดงผลชื่อ preset ที่ label หลัก"""
        try:  # เพิ่ม try-except เพื่อความปลอดภัย
            if hasattr(self, "preset_label") and self.preset_label.winfo_exists():
                # *** แก้ไขจุดนี้: ใช้ชื่อที่ต้องการแสดงโดยตรงจาก settings ***
                display_name = self.settings.get_preset_display_name(
                    self.current_preset
                )
                self.preset_label.config(text=display_name)
        except Exception as e:
            logging.error(f"Error updating preset display label: {e}")

    def show_save_feedback(self):
        """แสดงข้อความ feedback เมื่อบันทึก preset แบบโมเดิร์น"""
        try:
            feedback = tk.Toplevel(self.root)
            feedback.overrideredirect(True)
            feedback.configure(bg=self.theme["bg"])
            feedback.attributes("-alpha", 0.9)
            feedback.attributes("-topmost", True)

            # คำนวณตำแหน่งให้แสดงทับ control ui
            win_width = self.root.winfo_width()
            win_height = self.root.winfo_height()
            win_x = self.root.winfo_x()
            win_y = self.root.winfo_y()

            # สร้าง frame หลักแบบโค้งมน
            main_frame = tk.Frame(feedback, bg=self.theme["bg"], padx=15, pady=10)
            main_frame.pack()

            # สร้างข้อความที่สวยงาม
            msg_frame = tk.Frame(main_frame, bg=self.theme["bg"])
            msg_frame.pack()

            # ไอคอนเช็คถูก
            check_label = tk.Label(
                msg_frame,
                text="✓",
                fg="#2ecc71",  # สีเขียว
                bg=self.theme["bg"],
                font=("FC Minimal Medium", 14, "bold"),
            )
            check_label.pack(side=tk.LEFT, padx=(0, 5))

            # ข้อความ
            tk.Label(
                msg_frame,
                text=f"บันทึก Preset {self.current_preset} แล้ว!",
                fg="#2ecc71",
                bg=self.theme["bg"],
                font=("FC Minimal Medium", 11),
            ).pack(side=tk.LEFT)

            # แสดงผลทับตำแหน่งของ control ui
            feedback.update_idletasks()
            feedback_width = feedback.winfo_width()
            feedback_height = feedback.winfo_height()

            # จัดให้อยู่ตรงกลางของ control ui
            center_x = win_x + (win_width // 2) - (feedback_width // 2)
            center_y = win_y + (win_height // 2) - (feedback_height // 2)
            feedback.geometry(f"+{center_x}+{center_y}")

            # เอฟเฟกต์ fade-in fade-out
            feedback.attributes("-alpha", 0.0)

            def fade_in():
                for i in range(0, 10):
                    if feedback.winfo_exists():
                        feedback.attributes("-alpha", i / 10)
                        feedback.update()
                        feedback.after(20)

            def fade_out():
                for i in range(10, -1, -1):
                    if feedback.winfo_exists():
                        feedback.attributes("-alpha", i / 10)
                        feedback.update()
                        feedback.after(20)
                    if feedback.winfo_exists():
                        feedback.destroy()

            fade_in()
            feedback.after(1000, fade_out)
        except Exception as e:
            print(f"Error showing save feedback: {e}")
            # Fallback ในกรณีที่มีข้อผิดพลาด
            simple_feedback = tk.Toplevel(self.root)
            simple_feedback.overrideredirect(True)
            simple_feedback.configure(bg="black")
            simple_feedback.attributes("-topmost", True)

            # จัดให้อยู่ตรงกลางของ control ui
            x = self.root.winfo_x() + (self.root.winfo_width() // 2)
            y = self.root.winfo_y() + (self.root.winfo_height() // 2)

            message_label = tk.Label(
                simple_feedback,
                text=f"บันทึก Preset {self.current_preset} แล้ว!",
                fg="lime",
                bg="black",
                font=("FC Minimal Medium", 16),  # เพิ่มขนาดฟอนต์ 30% (12->16)
            )
            message_label.pack(padx=20, pady=10)

            # จัดตำแหน่งให้อยู่ตรงกลาง
            simple_feedback.update_idletasks()
            w = simple_feedback.winfo_width()
            h = simple_feedback.winfo_height()
            simple_feedback.geometry(f"+{x-w//2}+{y-h//2}")

            simple_feedback.after(1500, simple_feedback.destroy)

    def get_preset_tooltip_text(self, preset_num):
        """ส่งคืนข้อความ tooltip สำหรับปุ่ม preset แต่ละตัว"""
        try:
            preset_data = self.settings.get_preset(preset_num)
            if not preset_data:
                return f"Preset {preset_num}: ไม่มีข้อมูล"

            display_name = self.settings.get_preset_display_name(preset_num)
            areas = preset_data.get("areas", "")

            # สร้างข้อความ tooltip แบบละเอียด
            if preset_num == 1:
                return f"{display_name}: สำหรับบทสนทนาหลัก\n🔸 พื้นที่: {areas}\n🔸 แปลชื่อผู้พูด + เนื้อหา"
            elif preset_num == 2:
                return f"{display_name}: สำหรับข้อมูล Lore\n🔸 พื้นที่: {areas}\n🔸 แปลคำอธิบายและข้อมูลเสริม"
            elif preset_num == 3:
                return f"{display_name}: สำหรับเกมอื่นนอกเหนือจาก FFXIV\n🔸 พื้นที่ A: เลือกพื้นที่ว่างเปล่าเล็กๆ เอาไว้\n🔸 พื้นที่ B: crop ตัวเลือกทั้งหมดในกรอบเดียว\n⚡ ปุ่มพิเศษสำหรับเกมที่มีระบบตัวเลือก"
            else:
                # preset 4, 5, 6 ใช้คำอธิบายเดียวกันทั้งหมด (ตายตัว)
                return f"Custom Preset: ปรับแต่งได้อิสระ\n🔸 ใช้งานได้ทั้ง 3 พื้นที่ (A, B, C)\n🔸 เลือกพื้นที่และกำหนดตำแหน่งได้ตามต้องการ\n🔸 เปลี่ยนชื่อได้โดยกดที่ชื่อ preset ด้านบนสุด"

        except Exception as e:
            logging.error(f"Error getting preset tooltip text: {e}")
            return f"Preset {preset_num}: Error loading info"

    def auto_resize_font(self, button, text, max_width, start_size=9, min_size=6):
        """ปรับขนาดฟอนต์ของปุ่มให้เหมาะสมกับความกว้างที่กำหนด

        Args:
            button: ปุ่มที่ต้องการปรับขนาดฟอนต์
            text: ข้อความที่จะแสดงบนปุ่ม
            max_width: ความกว้างสูงสุดที่ยอมรับได้ (หน่วยเป็นพิกเซล)
            start_size: ขนาดฟอนต์เริ่มต้น
            min_size: ขนาดฟอนต์ต่ำสุดที่ยอมรับได้
        """
        current_size = start_size
        font_family = "FC Minimal Medium"  # ฟอนต์ปกติที่ใช้
        button.config(text=text)

        # ตรวจสอบความกว้างของข้อความด้วยฟอนต์ปัจจุบัน
        font = tkFont.Font(family=font_family, size=current_size)
        text_width = font.measure(text)

        # ถ้าข้อความกว้างเกินไป ให้ลดขนาดฟอนต์ลงทีละขั้น
        while text_width > max_width and current_size > min_size:
            current_size -= 1
            font = tkFont.Font(family=font_family, size=current_size)
            text_width = font.measure(text)

        # ตั้งค่าฟอนต์ใหม่ให้กับปุ่ม
        button.config(font=(font_family, current_size))

        # ถ้ายังยาวเกินไป ให้ตัดข้อความและเพิ่ม ... ต่อท้าย
        if text_width > max_width:
            # คำนวณความยาวข้อความที่เหมาะสม
            ratio = max_width / text_width
            max_chars = int(len(text) * ratio) - 3  # หักลบความยาวของ "..."
            truncated_text = text[:max_chars] + "..."
            button.config(text=truncated_text)

    def handle_toggle_change(self, toggle_type, new_value):
        """
        จัดการเมื่อ Toggle Switch ใน Control UI ถูกกด
        อัพเดทค่า setting และเรียก Callback ไปยัง MBB.py
        """
        try:
            if toggle_type == "click_translate":
                setting_key = "enable_click_translate"
                callback_func = self.toggle_click_callback
                log_prefix = "Click Translate"
                # อัพเดทสถานะปุ่ม Force ทันที (อาจจะย้ายไปทำใน MBB แทน)
                self._update_force_button_ui(new_value)
            elif toggle_type == "hover_translate":
                setting_key = "enable_hover_translation"
                callback_func = self.toggle_hover_callback
                log_prefix = "Hover Translate"
            else:
                logging.warning(
                    f"Unknown toggle type in handle_toggle_change: {toggle_type}"
                )
                return

            logging.info(f"ControlUI: {log_prefix} toggled to {new_value}")

            # 1. อัพเดทค่าใน Settings
            self.settings.set(setting_key, new_value)
            # settings.py ควรจะจัดการ save_settings() เองเมื่อ set()

            # 2. เรียก Callback ไปยัง MBB.py (ถ้ามี)
            if callback_func:
                logging.debug(
                    f"ControlUI: Calling callback {callback_func.__name__}({new_value})"
                )
                callback_func(new_value)  # แจ้ง MBB ให้เปิด/ปิดการทำงานจริง
            else:
                logging.warning(f"ControlUI: Callback for {log_prefix} is missing!")

            # 3. อัพเดท UI ของ Toggle (อาจจะไม่จำเป็นถ้า Variable ผูกกับ UI โดยตรง แต่ทำเผื่อไว้)
            if toggle_type == "click_translate":
                self.update_click_translate_toggle(new_value)
            elif toggle_type == "hover_translate":
                self.update_hover_translate_toggle(new_value)

        except Exception as e:
            logging.error(
                f"Error handling toggle change for {toggle_type}: {e}", exc_info=True
            )

    def _update_force_button_ui(self, click_translate_enabled):
        """อัพเดท UI ของปุ่ม Force - ใช้ระบบปกติไม่มีการจัดการพิเศษ"""
        force_button = getattr(self, "force_button", None)
        if force_button and force_button.winfo_exists():
            current_theme_button_bg = self.theme.get("button_bg", "#262637")
            current_theme_accent_light = self.theme.get(
                "accent_light",
                self.lighten_color(current_theme_button_bg, 0.2),
            )
            current_theme_error_bg = self.theme.get("error", "#e74c3c")
            current_theme_text_color = self.theme.get("text", "white")

            # ล้าง event bindings เก่า
            force_button.unbind("<Enter>")
            force_button.unbind("<Leave>")

            if click_translate_enabled:
                force_button.config(
                    text="Translate 1 Time",  # เปลี่ยนจาก "TOUCH" เป็น "Translate 1 Time"
                    cursor="hand2",
                    bg=current_theme_error_bg,
                    fg=current_theme_text_color,
                    width=15,  # ขยายขนาดปุ่มให้แสดงข้อความได้พอดี
                )
            else:
                force_button.config(
                    text="FORCE",
                    cursor="hand2",
                    bg=current_theme_button_bg,
                    fg=current_theme_text_color,
                    width=7,  # คืนค่าขนาดปกติ
                )

            # *** เพิ่ม hover effects กลับมาให้ทำงานร่วมกับ tooltip system ***
            def on_hover_enter(event):
                if force_button.winfo_exists():
                    # 1. แสดง hover effect ก่อน (เปลี่ยนสี)
                    force_button.config(bg=current_theme_accent_light)

                    # 2. เรียก tooltip event handler หากมี
                    if hasattr(force_button, "_tooltip_enter_callback"):
                        try:
                            # สร้าง dummy event object ถ้าไม่มี
                            import types

                            dummy_event = types.SimpleNamespace()
                            dummy_event.widget = force_button
                            force_button._tooltip_enter_callback(dummy_event)
                        except Exception as e:
                            logging.debug(f"Tooltip enter callback error: {e}")

            def on_hover_leave(event):
                if force_button.winfo_exists():
                    # 1. เปลี่ยนสีกลับก่อน
                    if click_translate_enabled:
                        force_button.config(bg=current_theme_error_bg)
                    else:
                        force_button.config(bg=current_theme_button_bg)

                    # 2. เรียก tooltip event handler หากมี
                    if hasattr(force_button, "_tooltip_leave_callback"):
                        try:
                            import types

                            dummy_event = types.SimpleNamespace()
                            dummy_event.widget = force_button
                            force_button._tooltip_leave_callback(dummy_event)
                        except Exception as e:
                            logging.debug(f"Tooltip leave callback error: {e}")

            # Bind hover effects ที่จะทำงานร่วมกับ tooltip
            force_button.bind("<Enter>", on_hover_enter)
            force_button.bind("<Leave>", on_hover_leave)

            logging.debug(
                "Force button updated with hover effects + tooltip integration"
            )
        else:
            logging.warning(
                "_update_force_button_ui: Force button not found or destroyed."
            )

    def setup_buttons(self):
        """สร้างและจัดวางปุ่มควบคุมทั้งหมดด้วย Layout ใหม่ที่แบ่งเป็นโหมด"""
        # ล้าง UI เก่า (ถ้ามี)
        if hasattr(self, "main_frame") and self.main_frame.winfo_exists():
            for widget in self.main_frame.winfo_children():
                if widget not in [
                    getattr(self, "title_label", None),
                ]:
                    try:
                        if widget.winfo_exists():
                            widget.destroy()
                    except tk.TclError:
                        pass
        else:
            logging.error("setup_buttons: self.main_frame does not exist.")
            return

        theme_bg = self.theme.get("bg", "#1a1a1a")

        # --- สร้าง Frame หลักสำหรับแต่ละโหมด ---
        self.content_frame = tk.Frame(self.main_frame, bg=theme_bg)
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 0))  # ลบ top padding เพื่อให้ title area มีที่

        self.usage_frame = tk.Frame(self.content_frame, bg=theme_bg)
        self.edit_frame = tk.Frame(self.content_frame, bg=theme_bg)

        # สร้าง UI สำหรับแต่ละโหมด
        self.create_usage_mode_ui(self.usage_frame)
        self.create_edit_mode_ui(self.edit_frame)

        # สร้าง Utility Bar ที่ด้านล่างสุด
        self.create_utility_bar(self.main_frame)

        # เริ่มต้นโดยการแสดง Usage Mode
        self.usage_frame.pack(fill=tk.BOTH, expand=True)
        self.edit_frame.pack_forget()

        # Sync สถานะ Toggle ตอนเริ่มต้น
        self._sync_startup_toggle_states()

    def create_usage_mode_ui(self, parent):
        """สร้าง UI สำหรับโหมดใช้งานปกติ (เลือก Preset, Force, Toggles)"""
        theme_bg = self.theme.get("bg", "#1a1a1a")
        inactive_bg = self.theme.get("button_bg", "#262637")
        theme_text_color = self.theme.get("text", "white")
        theme_accent_light = self.theme.get("accent_light", "#87CEFA")
        button_font_preset_btn = ("FC Minimal Medium", 11)

        # --- Presets Section ---
        preset_title_frame = tk.Frame(parent, bg=theme_bg)
        preset_title_frame.pack(fill=tk.X, pady=(5, 8))  # เพิ่ม padding เพื่อให้ดูสมดุล
        self.preset_title_label = tk.Label(
            preset_title_frame,
            text="PRESET: dialog",  # แสดงชื่อ preset แทน "..."
            bg=theme_bg,
            fg=self.theme.get("accent", "#6c5ce7"),
            font=("FC Minimal Medium", 11),
        )
        self.preset_title_label.pack(anchor="center")

        system_preset_row = tk.Frame(parent, bg=theme_bg)
        system_preset_row.pack(fill=tk.X, padx=5)
        custom_preset_row = tk.Frame(parent, bg=theme_bg)
        custom_preset_row.pack(fill=tk.X, padx=5, pady=(2, 0))
        for i in range(3):
            system_preset_row.grid_columnconfigure(i, weight=1)
            custom_preset_row.grid_columnconfigure(i, weight=1)

        self.preset_buttons = []
        max_text_width_preset = 90
        preset_definitions = [
            (system_preset_row, range(1, 4)),
            (custom_preset_row, range(4, 7)),
        ]

        for frame, num_range in preset_definitions:
            for i, preset_num in enumerate(num_range):
                display_name = self.settings.get_preset_display_name(preset_num)
                btn = tk.Button(
                    frame,
                    text=display_name,
                    command=lambda n=preset_num: self.select_preset(n),
                    font=button_font_preset_btn,
                    height=1,
                    bd=0,
                    relief="flat",
                    cursor="hand2",
                    bg=inactive_bg,
                    fg=theme_text_color,
                    activebackground=theme_accent_light,
                )
                self.auto_resize_font(btn, display_name, max_text_width_preset)
                btn.grid(row=0, column=i, padx=2, pady=1, sticky="ew")
                btn.preset_num = preset_num
                btn.selected = False
                self.preset_buttons.append(btn)
                self.add_button_hover_effect(btn)

                # เพิ่ม tooltips สำหรับปุ่ม preset
                preset_info = self.get_preset_tooltip_text(preset_num)
                self.create_tooltip(btn, preset_info)

        # --- Core Actions Section ---
        action_frame = tk.Frame(parent, bg=theme_bg)
        action_frame.pack(pady=(10, 5), padx=5, fill=tk.X)  # ลด top padding จาก 15 เป็น 10

        self.force_button = tk.Button(
            action_frame,
            text="FORCE",
            command=self.force_translate,
            font=("FC Minimal Medium", 11),
            height=1,
            bg=inactive_bg,
            fg=theme_text_color,
            activebackground=theme_accent_light,
            activeforeground=theme_text_color,
            bd=0,
            relief="flat",
            cursor="hand2",
            padx=8,
            width=7,
        )
        self.force_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        self._create_integrated_force_tooltip(
            self.force_button, "Force Translate: บังคับแปลใหม่อีกครั้งทันที", font_size=11
        )

        toggles_frame = tk.Frame(action_frame, bg=theme_bg)
        toggles_frame.pack(side=tk.RIGHT)

        self.click_translate_switch_container = self.create_toggle_switch(
            toggles_frame,
            "manual-click",
            self.click_translate_var,
            lambda value: self.handle_toggle_change("click_translate", value),
            width=38,
            height=18,
        )
        self.click_translate_switch_container.pack(anchor="e", pady=(0, 2))
        # เพิ่ม tooltip สำหรับ click translate toggle
        self.create_tooltip(
            self.click_translate_switch_container,
            "Click Translate\nเปิด: แปลเมื่อคลิกเฉพาะครั้ง\nปิด: แปลแบบ auto ตามปกติ",
        )

        hover_area_frame = tk.Frame(toggles_frame, bg=theme_bg)
        hover_area_frame.pack(anchor="e", pady=(2, 0), fill=tk.X)

        try:
            setting_tk_image = AssetManager.load_icon("setting.png", (18, 18))
            self.hover_settings_button = tk.Button(
                hover_area_frame,
                image=setting_tk_image,
                command=self.open_hover_settings,
                bg=theme_bg,
                activebackground=theme_accent_light,
                width=20,
                height=20,
                bd=0,
                relief="flat",
                cursor="hand2",
            )
            self.hover_settings_button.image = setting_tk_image
        except Exception:
            self.hover_settings_button = tk.Button(
                hover_area_frame,
                text="⚙",
                command=self.open_hover_settings,
                bg=theme_bg,
                font=("FC Minimal Medium", 10),
            )

        self.hover_settings_button.pack(side="left", padx=(0, 4))
        self.create_tooltip(
            self.hover_settings_button, "ตั้งค่าเปิด-ปิด พื้นที่ Hover\nพื้นที่ๆถูกปิดไว้จะไม่ถูก detect"
        )
        self.hover_translate_switch_container = self.create_toggle_switch(
            hover_area_frame,
            "hover area",
            self.hover_translation_var,
            lambda value: self.handle_toggle_change("hover_translate", value),
            width=38,
            height=18,
        )
        self.hover_translate_switch_container.pack(side="left")
        # เพิ่ม tooltip สำหรับ hover translate toggle
        self.create_tooltip(
            self.hover_translate_switch_container,
            "Hover Translate\nเปิด: แปลเมื่อ hover เมาส์\nปิด: ปิดการแปลแบบ hover",
        )

    def create_edit_mode_ui(self, parent):
        """สร้าง UI สำหรับโหมดแก้ไข Preset"""
        theme_bg = self.theme.get("bg", "#1a1a1a")
        inactive_bg = self.theme.get("button_bg", "#262637")
        theme_text_color = self.theme.get("text", "white")
        theme_accent_light = self.theme.get("accent_light", "#87CEFA")
        button_font_large_def = ("FC Minimal Medium", 11)
        button_font_area_toggle = ("FC Minimal Medium", 11, "bold")

        # --- Define Areas Section ---
        define_frame = tk.Frame(parent, bg=theme_bg)
        define_frame.pack(pady=(10, 8), fill=tk.X, padx=5)
        define_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.define_area_a_button_ctrl = tk.Button(
            define_frame,
            text="เลือกพื้นที่ A",
            command=self.start_selection_a,
            font=button_font_large_def,
            bg=inactive_bg,
            fg=theme_text_color,
            activebackground=theme_accent_light,
            activeforeground=theme_text_color,
            height=1,
            bd=0,
            relief="flat",
            cursor="hand2",
        )
        self.define_area_a_button_ctrl.grid(
            row=0, column=0, padx=(0, 2), pady=2, sticky="ew"
        )
        # เพิ่ม tooltip สำหรับปุ่มเลือกพื้นที่ A
        self.create_tooltip(
            self.define_area_a_button_ctrl, "เลือกพื้นที่ A: crop เฉพาะชื่อผู้พูด"
        )

        self.define_area_b_button_ctrl = tk.Button(
            define_frame,
            text="เลือกพื้นที่ B",
            command=self.start_selection_b,
            font=button_font_large_def,
            bg=inactive_bg,
            fg=theme_text_color,
            activebackground=theme_accent_light,
            activeforeground=theme_text_color,
            height=1,
            bd=0,
            relief="flat",
            cursor="hand2",
        )
        self.define_area_b_button_ctrl.grid(
            row=0, column=1, padx=2, pady=2, sticky="ew"
        )
        # เพิ่ม tooltip สำหรับปุ่มเลือกพื้นที่ B
        self.create_tooltip(
            self.define_area_b_button_ctrl, "เลือกพื้นที่ B: crop เฉพาะบทพูดของผู้พูด"
        )

        self.define_area_c_button_ctrl = tk.Button(
            define_frame,
            text="เลือกพื้นที่ C",
            command=self.start_selection_c,
            font=button_font_large_def,
            bg=inactive_bg,
            fg=theme_text_color,
            activebackground=theme_accent_light,
            activeforeground=theme_text_color,
            height=1,
            bd=0,
            relief="flat",
            cursor="hand2",
        )
        self.define_area_c_button_ctrl.grid(
            row=0, column=2, padx=(2, 0), pady=2, sticky="ew"
        )
        # เพิ่ม tooltip สำหรับปุ่มเลือกพื้นที่ C
        self.create_tooltip(
            self.define_area_c_button_ctrl,
            "เลือกพื้นที่ C: crop ข้อความบรรยาย หรือคำอธิบายทั่วไป",
        )

        # --- Toggle Areas & Save Section ---
        edit_action_frame = tk.Frame(parent, bg=theme_bg)
        edit_action_frame.pack(pady=(8, 10), fill=tk.X, padx=5)

        self.save_button = tk.Button(
            edit_action_frame,
            text="Save Preset",
            command=self.save_preset,
            font=("FC Minimal Medium", 11),
            width=12,
            height=1,
            bd=0,
            relief="flat",
            cursor="hand2",
            state=tk.DISABLED,
            bg=inactive_bg,
            fg=theme_text_color,
        )
        self.save_button.pack(side=tk.LEFT, padx=(0, 10))
        # เพิ่ม tooltip สำหรับปุ่ม save
        self.create_tooltip(
            self.save_button,
            "บันทึก Preset\nบันทึกการตั้งค่าพื้นที่และตำแหน่งปัจจุบัน\nลงใน preset ที่เลือกอยู่",
        )

        self.add_button_hover_effect(
            self.save_button, hover_color=self.theme.get("success", "#4CAF50")
        )

        toggle_area_active_container = tk.Frame(edit_action_frame, bg=theme_bg)
        toggle_area_active_container.pack(side=tk.LEFT, expand=True, fill=tk.X)
        toggle_area_active_centered = tk.Frame(
            toggle_area_active_container, bg=theme_bg
        )
        toggle_area_active_centered.pack(anchor="center")
        self.button_a, self.button_b, self.button_c = None, None, None
        for area_char_toggle in ["A", "B", "C"]:
            btn_toggle = tk.Button(
                toggle_area_active_centered,
                text=area_char_toggle,
                command=lambda a=area_char_toggle: self.area_button_click(a),
                font=button_font_area_toggle,
                width=4,
                height=1,
                bd=0,
                relief="flat",
                cursor="hand2",
                bg=inactive_bg,
                fg=theme_text_color,
            )
            btn_toggle.pack(side=tk.LEFT, padx=5)
            setattr(self, f"button_{area_char_toggle.lower()}", btn_toggle)
            self.add_button_hover_effect(btn_toggle)

            # เพิ่ม tooltips สำหรับปุ่ม area toggle
            area_tooltips = {
                "A": "พื้นที่ A: เปิด/ปิดการแปลชื่อผู้พูดหรือข้อความสั้นๆ",
                "B": "พื้นที่ B: เปิด/ปิดการแปลบทสนทนาหลักหรือเนื้อหาสำคัญ",
                "C": "พื้นที่ C: เปิด/ปิดการแปลข้อมูลเสริม เช่น lore หรือคำอธิบาย",
            }
            self.create_tooltip(btn_toggle, area_tooltips[area_char_toggle])

    def create_utility_bar(self, parent):
        """สร้างแถบเครื่องมือด้านล่างสุด พร้อมปุ่ม Edit"""
        theme_bg = self.theme.get("bg", "#1a1a1a")
        button_font_normal = ("FC Minimal Medium", 10)
        theme_text_dim_color = self.theme.get("text_dim", "#b2b2b2")
        theme_error_color = self.theme.get("error", "#FF4136")
        theme_accent_light = self.theme.get("accent_light", "#87CEFA")
        theme_text_color = self.theme.get("text", "white")
        theme_accent = self.theme.get("accent", "#6c5ce7")

        bottom_separator = tk.Frame(
            parent, height=1, bg=self.theme.get("border", "#444444")
        )
        bottom_separator.pack(fill=tk.X, padx=10, pady=(8, 3), side=tk.BOTTOM)  # ลดเหลือ 8,3 จาก 15,5

        utility_bar = tk.Frame(parent, bg=theme_bg, height=40)
        utility_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=(0, 5), padx=5)  # ลด bottom padding จาก 10 เป็น 5
        utility_bar.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # *** SHOW/HIDE Button - ปรับสไตล์ใหม่ ***
        self.show_hide_area_button_ctrl = tk.Button(
            utility_bar,
            text="SHOW",
            command=self.toggle_show_area_ctrl,
            font=button_font_normal,
            bg=theme_bg,  # พื้นหลังโปร่งใส
            fg=self.theme.get("error", "#e74c3c"),
            activebackground=theme_accent,
            activeforeground=theme_text_color,
            width=9,
            height=1,
            bd=0,
            relief="flat",
            cursor="hand2",
            highlightthickness=0,
            takefocus=False,  # ป้องกันการได้รับ focus
        )
        self.show_hide_area_button_ctrl.grid(row=0, column=0, sticky="ew", padx=2)
        self._apply_utility_button_style(self.show_hide_area_button_ctrl)
        # เพิ่ม tooltip สำหรับปุ่ม Show/Hide area
        self.create_tooltip(
            self.show_hide_area_button_ctrl,
            "แสดง/ซ่อนกรอบพื้นที่บนหน้าจอ\nเพื่อดูขอบเขตการแปลแบบ real-time",
        )

        # *** Camera Button - ปรับสไตล์ใหม่ ***
        try:
            camera_tk_image = AssetManager.load_icon("camera.png", (20, 20))
            self.camera_button = tk.Button(
                utility_bar,
                image=camera_tk_image,
                command=self.capture_screen,
                bg=theme_bg,  # พื้นหลังโปร่งใส
                activebackground=theme_accent,
                width=28,
                height=28,
                bd=0,
                relief="flat",
                cursor="hand2",
                highlightthickness=0,
                takefocus=False,  # ป้องกันการได้รับ focus
            )
            self.camera_button.image = camera_tk_image
        except Exception:
            self.camera_button = tk.Button(
                utility_bar,
                text="📷",
                command=self.capture_screen,
                font=("FC Minimal Medium", 12),
                bg=theme_bg,  # พื้นหลังโปร่งใส
                fg=theme_text_dim_color,
                activebackground=theme_accent,
                activeforeground=theme_text_color,
                bd=0,
                relief="flat",
                cursor="hand2",
                highlightthickness=0,
                takefocus=False,  # ป้องกันการได้รับ focus
            )
        self.camera_button.grid(row=0, column=1, sticky="ew", padx=2)
        self._apply_utility_button_style(self.camera_button)
        # เพิ่ม tooltip สำหรับปุ่ม camera
        self.create_tooltip(
            self.camera_button,
            "ถ่ายภาพหน้าจอ\nบันทึกภาพหน้าจอปัจจุบันลงโฟลเดอร์ captured_screens",
        )

        # *** RESET Button - ปรับสไตล์ใหม่ ***
        self.reset_area_button = tk.Button(
            utility_bar,
            text="RESET",
            font=button_font_normal,
            bg=theme_bg,  # พื้นหลังโปร่งใส
            fg=theme_text_dim_color,
            activebackground=theme_error_color,
            activeforeground=theme_text_color,
            width=9,
            height=1,
            bd=0,
            relief="flat",
            cursor="hand2",
            highlightthickness=0,
            takefocus=False,  # ป้องกันการได้รับ focus
        )
        self.reset_area_button.grid(row=0, column=2, sticky="ew", padx=2)
        self._apply_utility_button_style(self.reset_area_button)
        # เพิ่ม tooltip สำหรับปุ่ม reset
        self.create_tooltip(
            self.reset_area_button,
            "ล้าง Preset: กดค้าง 3วินาทีเพื่อยืนยัน\nเมื่อ reset แล้วต้องตั้งค่า preset ใหม่ทั้งหมดก่อนใช้งาน",
        )

        self.reset_area_button.bind("<ButtonPress-1>", self.start_reset_hold)
        self.reset_area_button.bind("<ButtonRelease-1>", self.cancel_reset_hold)

        # *** EDIT Button - ปรับสไตล์ใหม่ ***
        self.edit_mode_button = tk.Button(
            utility_bar,
            text="EDIT",
            command=self.toggle_edit_mode,
            font=button_font_normal,
            bg=theme_bg,  # พื้นหลังโปร่งใส
            fg=theme_text_dim_color,
            activebackground=theme_accent,
            activeforeground=theme_text_color,
            width=9,
            height=1,
            bd=0,
            relief="flat",
            cursor="hand2",
            highlightthickness=0,
            takefocus=False,  # ป้องกันการได้รับ focus
        )
        self.edit_mode_button.grid(row=0, column=3, sticky="ew", padx=2)
        self._apply_utility_button_style(self.edit_mode_button, is_edit_button=True)
        # เพิ่ม tooltip สำหรับปุ่ม edit mode
        self.create_tooltip(
            self.edit_mode_button,
            "EDIT: เปิดเพื่อตั้งค่าพื้นที่ preset\nกด save เพื่อบันทึก",
        )

    def _apply_utility_button_style(self, button, is_edit_button=False):
        """
        ปรับแต่งสไตล์ของปุ่มใน utility bar ให้มีความสม่ำเสมอ
        - ค่าเริ่มต้น: มองเห็นแค่ตัวอักษร ไม่เห็นกรอบปุ่ม
        - hover: แสดงกรอบปุ่มพร้อมขอบเส้นบางๆ
        - active: พื้นหลังสี theme และอักษรขาว
        - edit button: มี animation เรืองแสงเมื่อ active
        """
        theme_bg = self.theme.get("bg", "#1a1a1a")
        theme_accent = self.theme.get("accent", "#6c5ce7")
        theme_text_color = self.theme.get("text", "white")
        border_color = "#404040"  # สีเทาอ่อนสำหรับขอบ
        
        # ตัวแปรสำหรับ animation ของปุ่ม EDIT
        if is_edit_button:
            button._animation_timer = None
            button._animation_phase = 0
            button._is_edit_active = False
        
        def on_enter(event):
            """เมื่อ hover เข้า - แสดงกรอบปุ่ม"""
            if button.winfo_exists():
                current_bg = button.cget("bg")
                # ถ้าไม่ใช่สถานะ active ให้แสดง hover effect
                if current_bg == theme_bg or current_bg == "SystemButtonFace":
                    button.configure(
                        bg=theme_bg,
                        relief="solid",
                        bd=1,
                        highlightbackground=border_color,
                        highlightcolor=border_color,
                        highlightthickness=1,
                    )

        def on_leave(event):
            """เมื่อ hover ออก - ซ่อนกรอบปุ่ม"""
            if button.winfo_exists():
                current_bg = button.cget("bg")
                # ถ้าไม่ใช่สถานะ active ให้ซ่อนกรอบ
                if current_bg == theme_bg or "SystemButton" in current_bg:
                    button.configure(
                        relief="flat",
                        bd=0,
                        highlightthickness=0,
                    )
        
        def on_focus_in(event):
            """เมื่อได้รับ focus - ไม่แสดงกรอบ"""
            if button.winfo_exists():
                button.configure(
                    relief="flat",
                    bd=0,
                    highlightthickness=0,
                )
        
        def on_focus_out(event):
            """เมื่อสูญเสีย focus - ไม่แสดงกรอบ"""
            if button.winfo_exists():
                button.configure(
                    relief="flat",
                    bd=0,
                    highlightthickness=0,
                )
        
        def on_button_press(event):
            """เมื่อกดปุ่ม - ไม่แสดงกรอบ"""
            if button.winfo_exists():
                button.configure(
                    relief="flat",
                    bd=0,
                    highlightthickness=0,
                )
        
        def on_button_release(event):
            """เมื่อปล่อยปุ่ม - ไม่แสดงกรอบ"""
            if button.winfo_exists():
                button.configure(
                    relief="flat",
                    bd=0,
                    highlightthickness=0,
                )
        
        def start_edit_animation():
            """เริ่ม animation สำหรับปุ่ม EDIT เมื่ออยู่ในสถานะเปิด"""
            if not is_edit_button or not button.winfo_exists():
                return
                
            def animate():
                if not button.winfo_exists() or not button._is_edit_active:
                    return
                    
                try:
                    # สร้าง effect เรืองแสงแบบช้าๆ
                    button._animation_phase += 1
                    phase = button._animation_phase
                    
                    # คำนวณความเข้มของแสง (0.0 - 1.0)
                    import math
                    intensity = (math.sin(phase * 0.1) + 1) / 2  # ค่าระหว่าง 0-1
                    
                    # ปรับสีพื้นหลังตาม intensity
                    base_color = theme_accent
                    # แปลง hex เป็น RGB
                    r = int(base_color[1:3], 16)
                    g = int(base_color[3:5], 16)
                    b = int(base_color[5:7], 16)
                    
                    # เพิ่มความสว่าง
                    glow_factor = 0.3 * intensity  # ความเข้มของการเรืองแสง
                    new_r = min(255, int(r + (255 - r) * glow_factor))
                    new_g = min(255, int(g + (255 - g) * glow_factor))
                    new_b = min(255, int(b + (255 - b) * glow_factor))
                    
                    new_color = f"#{new_r:02x}{new_g:02x}{new_b:02x}"
                    
                    button.configure(bg=new_color)
                    
                    # ตั้งเวลาสำหรับ frame ถัดไป
                    button._animation_timer = button.after(100, animate)  # 100ms = animation ช้าๆ
                    
                except Exception as e:
                    logging.error(f"Error in edit button animation: {e}")
            
            animate()
        
        def stop_edit_animation():
            """หยุด animation ของปุ่ม EDIT"""
            if not is_edit_button or not button.winfo_exists():
                return
                
            button._is_edit_active = False
            if hasattr(button, '_animation_timer') and button._animation_timer:
                try:
                    button.after_cancel(button._animation_timer)
                except:
                    pass
                button._animation_timer = None
            
            # คืนสีเป็นสีปกติ
            button.configure(bg=theme_bg)
        
        # เก็บฟังก์ชัน animation ไว้ใน button object
        if is_edit_button:
            button.start_animation = start_edit_animation
            button.stop_animation = stop_edit_animation
        
        # Bind hover events
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        
        # Bind focus events เพื่อป้องกันการแสดงกรอบ
        button.bind("<FocusIn>", on_focus_in)
        button.bind("<FocusOut>", on_focus_out)
        
        # Bind button events เพื่อป้องกันการแสดงกรอบเมื่อคลิก
        button.bind("<Button-1>", on_button_press, add="+")  # add="+" เพื่อไม่ให้แทนที่ binding เดิม
        button.bind("<ButtonRelease-1>", on_button_release, add="+")

    def _recursively_set_bg(self, parent_widget, color):
        """ไล่เปลี่ยนสีพื้นหลังของ widget และลูกๆ ของมันทั้งหมด"""
        try:
            parent_widget.config(bg=color)
        except tk.TclError:
            pass  # บาง widget อาจไม่มี property 'bg'

        for child in parent_widget.winfo_children():
            # เรียกใช้ตัวเองกับ widget ลูก
            self._recursively_set_bg(child, color)

    def has_valid_coordinates(self, preset_number=None):
        """เช็คว่า preset มีพิกัดที่ถูกต้องหรือไม่"""
        if preset_number is None:
            preset_number = self.current_preset
            
        try:
            preset_data = self.settings.get_preset(preset_number)
            coordinates = preset_data.get("coordinates", {})
            
            # เช็คทุก area ที่ใช้งานใน preset นี้
            preset_areas = preset_data.get("areas", "")
            active_areas = []
            if "A" in preset_areas:
                active_areas.append("A")
            if "B" in preset_areas:
                active_areas.append("B") 
            if "C" in preset_areas:
                active_areas.append("C")
            
            # ตรวจสอบว่าทุก active area มีพิกัดที่ไม่ใช่ 0
            for area in active_areas:
                area_coords = coordinates.get(area, {})
                start_x = area_coords.get("start_x", 0)
                start_y = area_coords.get("start_y", 0)
                end_x = area_coords.get("end_x", 0)
                end_y = area_coords.get("end_y", 0)
                
                # ถ้าพิกัดใดพิกัดหนึ่งเป็น 0 หมดหรือไม่มีขนาด แสดงว่าไม่ได้ตั้งค่า
                if start_x == 0 and start_y == 0 and end_x == 0 and end_y == 0:
                    return False
                if abs(end_x - start_x) < 10 or abs(end_y - start_y) < 10:  # พื้นที่เล็กเกินไป
                    return False
                    
            return True
            
        except Exception as e:
            logging.error(f"Error checking coordinates for preset {preset_number}: {e}")
            return False

    def update_edit_button_state(self):
        """อัพเดตสถานะของปุ่ม EDIT ตามการมีพิกัดของ preset ปัจจุบัน"""
        if not hasattr(self, "edit_mode_button") or not self.edit_mode_button.winfo_exists():
            return
            
        # ถ้าอยู่ใน edit mode อยู่แล้ว ไม่ต้องเปลี่ยนสี
        if self.edit_frame.winfo_ismapped():
            return
            
        has_coords = self.has_valid_coordinates()
        
        if has_coords:
            # preset มีพิกัดแล้ว - ใช้สีปกติ
            self.edit_mode_button.config(
                bg=self.theme.get("bg", "#1a1a1a"),
                fg=self.theme.get("text_dim", "#b2b2b2"),
                font=("FC Minimal Medium", 10)  # ฟอนต์ปกติ
            )
        else:
            # preset ยังไม่มีพิกัด - ใช้สีแดงเด่น
            self.edit_mode_button.config(
                bg="#e74c3c",  # สีแดงเด่น
                fg="#ffffff",  # ตัวอักษรขาว
                font=("FC Minimal Medium", 10, "bold")  # ตัวหนา
            )

    def update_area_buttons_lock_state(self):
        """อัพเดตสถานะการล็อกของปุ่ม area ตาม preset role"""
        try:
            preset_data = self.settings.get_preset(self.current_preset)
            preset_role = preset_data.get("role", "custom")
            
            # ตรวจสอบว่าปุ่มมีอยู่จริงและอยู่ใน edit mode
            if not (hasattr(self, "button_a") and hasattr(self, "button_b") and hasattr(self, "button_c")):
                return
            if not self.edit_frame.winfo_ismapped():
                return
                
            # สีสำหรับปุ่มที่ล็อก
            locked_bg = "#555555"  # สีเทาเข้ม
            locked_fg = "#888888"  # ตัวอักษรเทาอ่อน
            normal_bg = self.theme.get("button_bg", "#262637")
            normal_fg = self.theme.get("text", "white")
            
            if preset_role == "dialog":
                # Dialog preset: ล็อก A และ B ให้เปิดเสมอ, ปล่อย C ให้ปรับได้
                if self.button_a.winfo_exists():
                    self.button_a.config(state=tk.DISABLED, bg=locked_bg, fg=locked_fg, cursor="")
                if self.button_b.winfo_exists(): 
                    self.button_b.config(state=tk.DISABLED, bg=locked_bg, fg=locked_fg, cursor="")
                if self.button_c.winfo_exists():
                    self.button_c.config(state=tk.NORMAL, cursor="hand2")
                    
            elif preset_role == "lore":
                # Lore preset: ล็อก C ให้เปิดเสมอ, ปล่อย A และ B ให้ปรับได้
                if self.button_a.winfo_exists():
                    self.button_a.config(state=tk.NORMAL, cursor="hand2")
                if self.button_b.winfo_exists():
                    self.button_b.config(state=tk.NORMAL, cursor="hand2")
                if self.button_c.winfo_exists():
                    self.button_c.config(state=tk.DISABLED, bg=locked_bg, fg=locked_fg, cursor="")
                    
            else:
                # Custom preset: ปล่อยทุกปุ่มให้ปรับได้
                for button in [self.button_a, self.button_b, self.button_c]:
                    if button and button.winfo_exists():
                        button.config(state=tk.NORMAL, cursor="hand2")
                        
            # อัพเดตสีปุ่มตามสถานะ area ปัจจุบัน
            self.update_button_highlights()
            
        except Exception as e:
            logging.error(f"Error updating area buttons lock state: {e}")

    def toggle_edit_mode(self):
        """สลับระหว่าง Usage Mode และ Edit Mode"""
        edit_button = getattr(self, "edit_mode_button", None)
        theme_bg = self.theme.get("bg", "#1a1a1a")
        active_bg = self.theme.get("accent", "#6c5ce7")
        active_fg = self.theme.get("text", "#ffffff")
        inactive_bg = "#555555"
        edit_mode_bg = "#111111"

        if self.edit_frame.winfo_ismapped():
            # --- กลับสู่ Usage Mode ---
            self.edit_frame.pack_forget()
            self.usage_frame.pack(fill=tk.BOTH, expand=True)

            # เปลี่ยนพื้นหลังทั้งหมดกลับเป็นสีปกติของ Theme
            self._recursively_set_bg(self.main_frame, theme_bg)

            # เปลี่ยนสถานะปุ่ม Edit กลับเป็น Inactive และหยุด animation
            if edit_button:
                edit_button.config(text="EDIT")
                # หยุด animation ถ้ามี
                if hasattr(edit_button, 'stop_animation'):
                    edit_button.stop_animation()
                
                # อัพเดตสถานะปุ่ม EDIT ตามพิกัดของ preset ปัจจุบัน
                self.update_edit_button_state()

            # เรียกอัพเดทสีปุ่มทั้งหมดใน Usage Mode ให้ถูกต้อง
            self.update_preset_buttons()

        else:
            # --- เข้าสู่ Edit Mode ---
            self.usage_frame.pack_forget()
            self.edit_frame.pack(fill=tk.BOTH, expand=True)

            # เปลี่ยนพื้นหลังทั้งหมดเป็นสีของโหมดแก้ไข
            self._recursively_set_bg(self.main_frame, edit_mode_bg)

            # เปลี่ยนสถานะปุ่ม Edit เป็น Active และเริ่ม animation
            if edit_button:
                edit_button.config(text="DONE", bg=active_bg, fg=active_fg)
                # เริ่ม animation ถ้าเป็นปุ่ม edit
                if hasattr(edit_button, 'start_animation'):
                    edit_button._is_edit_active = True
                    edit_button.start_animation()

            # **สำคัญ:** เรียก update_button_highlights() อีกครั้ง
            # เพื่อคืนค่าสีปุ่มที่ Active (เช่น A, B) หลังจากถูกทาสีดำทับไป
            self.update_button_highlights()
            
            # อัพเดตสถานะการล็อกของปุ่ม area ตาม preset role
            self.update_area_buttons_lock_state()

    def _sync_startup_toggle_states(self):
        """Sync สถานะของ toggle switches กับ backend เมื่อ startup"""
        try:
            logging.info("ControlUI: Syncing startup toggle states...")

            # Sync Click Translate Toggle
            click_enabled = self.click_translate_var.get()
            if click_enabled and self.toggle_click_callback:
                logging.info(
                    f"ControlUI: Syncing click translate state: {click_enabled}"
                )
                self.toggle_click_callback(click_enabled)

            # Sync Hover Translate Toggle
            hover_enabled = self.hover_translation_var.get()
            if hover_enabled and self.toggle_hover_callback:
                logging.info(
                    f"ControlUI: Syncing hover translate state: {hover_enabled}"
                )
                self.toggle_hover_callback(hover_enabled)

            logging.info("ControlUI: Toggle states sync completed")

        except Exception as e:
            logging.error(f"Error syncing startup toggle states: {e}")

    def open_hover_settings(self):
        """เปิด/ปิดหน้าต่างตั้งค่า hover translation presets (Toggle Switch แบบง่าย)"""
        try:
            logging.info(
                f"open_hover_settings called, is_open: {self.hover_settings_is_open}"
            )

            if self.hover_settings_is_open:
                # ปิด UI
                logging.info("Closing hover settings UI")
                if self.hover_settings_window:
                    try:
                        self.hover_settings_window.destroy()
                    except:
                        pass
                    self.hover_settings_window = None

                self.hover_settings_is_open = False
                logging.info("Hover settings UI closed")

            else:
                # เปิด UI
                logging.info("Opening hover settings UI")
                if (
                    self.parent_app
                    and hasattr(self.parent_app, "hover_translator")
                    and self.parent_app.hover_translator
                ):
                    settings_ui = self.parent_app.hover_translator.open_settings_ui()
                    if (
                        settings_ui
                        and hasattr(settings_ui, "window")
                        and settings_ui.window
                    ):
                        self.hover_settings_window = settings_ui.window
                        self.hover_settings_is_open = True
                        logging.info("Hover settings UI opened")
                    else:
                        logging.warning("Failed to create hover settings UI")
                else:
                    logging.warning("Hover translator not available")

        except Exception as e:
            logging.error(f"Error in open_hover_settings: {e}")
            self.hover_settings_window = None
            self.hover_settings_is_open = False

    def edit_preset_name(self, event, preset_number=None):
        """แสดงหน้าต่าง dialog ให้ผู้ใช้แก้ไขชื่อของ preset

        Args:
            event: เหตุการณ์ที่เกิดขึ้น (การคลิก)
            preset_number: หมายเลข preset ที่ต้องการแก้ไขชื่อ (ถ้าไม่ระบุจะใช้ preset ปัจจุบัน)
        """
        # ถ้าไม่ระบุ preset_number ให้ใช้ preset ปัจจุบัน
        if preset_number is None:
            preset_number = self.current_preset

        # อนุญาตให้แก้ไขได้เฉพาะ preset 4 และ 5 เท่านั้น
        if preset_number < 4:
            # แสดงข้อความแจ้งเตือนว่าไม่สามารถแก้ไขชื่อได้
            messagebox.showinfo(
                "ไม่สามารถแก้ไขชื่อได้",
                f"Preset {preset_number} (1-3) เป็น preset ระบบ ไม่สามารถแก้ไขชื่อได้",
                parent=self.root,
            )
            return

        try:
            # รับชื่อปัจจุบันของ preset
            current_name = self.settings.get_preset_display_name(preset_number)

            # สร้างหน้าต่าง dialog สำหรับป้อนชื่อใหม่
            dialog = tk.Toplevel(self.root)
            dialog.title(f"แก้ไขชื่อ Preset {preset_number}")
            dialog.configure(bg=self.theme.get("bg", "#1a1a1a"))
            dialog.resizable(False, False)
            dialog.transient(self.root)
            dialog.grab_set()

            # จัดตำแหน่งหน้าต่าง dialog ให้อยู่ตรงกลางของ Control UI
            x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 150
            y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 60
            dialog.geometry(f"320x150+{x}+{y}")

            # กำหนด padding และกรอบที่เห็นชัดเจน
            outer_frame = tk.Frame(
                dialog,
                bg=self.theme.get("accent_light", "#8075e5"),
                padx=2,
                pady=2,
                highlightbackground=self.theme.get("accent", "#6c5ce7"),
                highlightthickness=1,
            )
            outer_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

            # สร้าง UI elements
            main_frame = tk.Frame(
                outer_frame, bg=self.theme.get("bg", "#1a1a1a"), padx=12, pady=12
            )
            main_frame.pack(fill=tk.BOTH, expand=True)

            # ไอคอนและหัวข้อในแถวเดียวกัน
            header_frame = tk.Frame(main_frame, bg=self.theme.get("bg", "#1a1a1a"))
            header_frame.pack(fill=tk.X, pady=(0, 10))

            # ไอคอน (ถ้ามี)
            try:
                icon = tk.Label(
                    header_frame,
                    text="✏️",  # ใช้ emoji แทนไอคอน
                    bg=self.theme.get("bg", "#1a1a1a"),
                    fg=self.theme.get("accent", "#6c5ce7"),
                    font=("Segoe UI Emoji", 14),
                )
                icon.pack(side=tk.LEFT, padx=(0, 5))
            except:
                pass  # ถ้าไม่สามารถแสดงไอคอนได้ ก็ข้ามไป

            # ข้อความอธิบาย
            label = tk.Label(
                header_frame,
                text=f"ป้อนชื่อใหม่สำหรับ Preset {preset_number}:",
                bg=self.theme.get("bg", "#1a1a1a"),
                fg=self.theme.get("text", "#ffffff"),
                font=("FC Minimal Medium", 11),
                anchor="w",
            )
            label.pack(side=tk.LEFT, fill=tk.X, expand=True)

            # Entry สำหรับป้อนชื่อใหม่ ปรับให้มีขอบชัดเจน
            entry_frame = tk.Frame(
                main_frame, bg=self.theme.get("accent_light", "#8075e5"), padx=1, pady=1
            )
            entry_frame.pack(fill=tk.X, pady=(0, 15))

            entry_var = tk.StringVar(value=current_name)
            entry = tk.Entry(
                entry_frame,
                textvariable=entry_var,
                bg=self.theme.get("button_bg", "#262637"),
                fg=self.theme.get("text", "#ffffff"),
                insertbackground=self.theme.get("text", "#ffffff"),  # สีของ cursor
                font=("FC Minimal Medium", 14),
                bd=0,  # ไม่มีขอบภายใน
                relief="flat",
                highlightthickness=0,
            )
            entry.pack(fill=tk.X, padx=1, pady=1)
            entry.select_range(0, tk.END)  # เลือกข้อความทั้งหมด
            entry.focus_set()  # ให้ focus อยู่ที่ entry

            # Frame สำหรับปุ่ม
            button_frame = tk.Frame(main_frame, bg=self.theme.get("bg", "#1a1a1a"))
            button_frame.pack(fill=tk.X)

            # ฟังก์ชันสำหรับบันทึกชื่อใหม่
            def save_name():
                new_name = entry_var.get().strip()
                if not new_name:
                    messagebox.showwarning("ข้อผิดพลาด", "กรุณาป้อนชื่อ", parent=dialog)
                    return

                # บันทึกชื่อใหม่
                self.settings.set_preset_custom_name(preset_number, new_name)

                # อัพเดต UI
                self.update_preset_display()
                self.update_preset_buttons()

                # ปิดหน้าต่าง dialog
                dialog.destroy()

                # แสดงข้อความแจ้งเตือนว่าบันทึกสำเร็จ
                self.show_name_change_feedback(preset_number, new_name)

            # ฟังก์ชันสำหรับยกเลิก
            def cancel():
                dialog.destroy()

            # ปุ่มยกเลิก
            cancel_btn = tk.Button(
                button_frame,
                text="ยกเลิก",
                command=cancel,
                bg=self.theme.get("button_bg", "#262637"),
                fg=self.theme.get("text", "#ffffff"),
                activebackground=self.theme.get("button_bg", "#262637"),
                activeforeground=self.theme.get("text", "#ffffff"),
                font=("FC Minimal Medium", 10),
                width=8,
                bd=0,
                relief="flat",
                cursor="hand2",
            )
            cancel_btn.pack(side=tk.RIGHT, padx=(5, 0))

            # ปุ่มบันทึก
            save_btn = tk.Button(
                button_frame,
                text="บันทึก",
                command=save_name,
                bg=self.theme.get("accent", "#6c5ce7"),
                fg=self.theme.get("text", "#ffffff"),
                activebackground=self.theme.get("accent_light"),
                activeforeground=self.theme.get("text", "#ffffff"),
                font=("FC Minimal Medium", 10),
                width=8,
                bd=0,
                relief="flat",
                cursor="hand2",
            )
            save_btn.pack(side=tk.RIGHT, padx=(0, 5))

            # ทำให้สามารถกด Enter เพื่อบันทึกได้
            entry.bind("<Return>", lambda event: save_name())
            # ทำให้สามารถกด Escape เพื่อยกเลิกได้
            dialog.bind("<Escape>", lambda event: cancel())

            # ไม่ใช้ rounded corners กับหน้าต่างนี้เพื่อให้แสดงผลเต็มที่
            # self.apply_rounded_corners_to_toplevel(dialog)

            # ตั้งค่าตัวแปรเป็น None ไม่ว่าจะเกิดข้อผิดพลาดหรือไม่
            dialog.protocol("WM_DELETE_WINDOW", cancel)

        except Exception as e:
            logging.error(f"Error in edit_preset_name: {e}")
            import traceback

            traceback.print_exc()

    def show_name_change_feedback(self, preset_number, new_name):
        """แสดงข้อความแจ้งเตือนเมื่อเปลี่ยนชื่อ preset สำเร็จ

        Args:
            preset_number: หมายเลข preset ที่เปลี่ยนชื่อ
            new_name: ชื่อใหม่ของ preset
        """
        try:
            # สร้างหน้าต่าง feedback
            feedback = tk.Toplevel(self.root)
            feedback.overrideredirect(True)
            feedback.configure(bg=self.theme["bg"])
            feedback.attributes("-alpha", 0.9)
            feedback.attributes("-topmost", True)

            # สร้าง frame หลัก
            main_frame = tk.Frame(feedback, bg=self.theme["bg"], padx=15, pady=10)
            main_frame.pack()

            # สร้างข้อความ
            msg_frame = tk.Frame(main_frame, bg=self.theme["bg"])
            msg_frame.pack()

            # ไอคอนเช็คถูก
            check_label = tk.Label(
                msg_frame,
                text="✓",
                fg="#2ecc71",  # สีเขียว
                bg=self.theme["bg"],
                font=("FC Minimal Medium", 14, "bold"),
            )
            check_label.pack(side=tk.LEFT, padx=(0, 5))

            # ข้อความ
            name_text = tk.Label(
                msg_frame,
                text=f"เปลี่ยนชื่อ Preset {preset_number} เป็น",
                fg="#2ecc71",
                bg=self.theme["bg"],
                font=("FC Minimal Medium", 11),
            )
            name_text.pack(side=tk.LEFT)

            # แสดงชื่อใหม่ในบรรทัดถัดไป
            new_name_text = tk.Label(
                main_frame,
                text=f'"{new_name}"',
                fg=self.theme["highlight"],
                bg=self.theme["bg"],
                font=("FC Minimal Medium", 10),
            )
            new_name_text.pack(pady=(5, 0))

            # คำนวณขนาดและตำแหน่ง
            feedback.update_idletasks()
            feedback_width = feedback.winfo_width()
            feedback_height = feedback.winfo_height()

            # จัดให้อยู่ตรงกลางของ control ui
            center_x = (
                self.root.winfo_rootx()
                + (self.root.winfo_width() // 2)
                - (feedback_width // 2)
            )
            center_y = (
                self.root.winfo_rooty()
                + (self.root.winfo_height() // 2)
                - (feedback_height // 2)
            )
            feedback.geometry(f"+{center_x}+{center_y}")

            # เอฟเฟกต์ fade-in fade-out
            feedback.attributes("-alpha", 0.0)

            def fade_in():
                for i in range(0, 10):
                    if feedback.winfo_exists():
                        feedback.attributes("-alpha", i / 10)
                        feedback.update()
                        feedback.after(20)

            def fade_out():
                for i in range(10, -1, -1):
                    if feedback.winfo_exists():
                        feedback.attributes("-alpha", i / 10)
                        feedback.update()
                        feedback.after(20)
                    if feedback.winfo_exists():
                        feedback.destroy()

            fade_in()
            feedback.after(1500, fade_out)  # แสดง 1.5 วินาที
        except Exception as e:
            logging.error(f"Error showing name change feedback: {e}")

    def apply_rounded_corners_to_toplevel(self, window):
        """ทำให้หน้าต่าง Toplevel มีขอบโค้งมน

        Args:
            window: หน้าต่าง Toplevel ที่ต้องการทำให้มีขอบโค้งมน
        """
        try:
            # รอให้หน้าต่างแสดงผล
            window.update_idletasks()

            # ดึงค่า HWND ของหน้าต่าง
            hwnd = windll.user32.GetParent(window.winfo_id())

            # ลบกรอบและหัวข้อ (ถ้าต้องการ)
            # style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
            # style &= ~win32con.WS_CAPTION
            # style &= ~win32con.WS_THICKFRAME
            # win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)

            # สร้างภูมิภาค (region) โค้งมน
            width = window.winfo_width()
            height = window.winfo_height()
            region = win32gui.CreateRoundRectRgn(0, 0, width, height, 10, 10)

            # กำหนดภูมิภาคให้กับหน้าต่าง
            win32gui.SetWindowRgn(hwnd, region, True)

        except Exception as e:
            logging.error(f"Error applying rounded corners to toplevel: {e}")
            import traceback

            traceback.print_exc()

    def select_preset(self, preset_number):
        """เลือก preset ตามหมายเลข
        Args:
            preset_number (int): หมายเลข preset (1-5)
        """
        if 1 <= preset_number <= self.max_presets:
            if self.has_unsaved_changes:
                # สร้างหน้าต่างแจ้งเตือน
                warning = tk.Toplevel(self.root)
                warning.title("คำเตือน")
                warning.geometry("300x150")
                warning.configure(bg="#1a1a1a")
                warning.transient(self.root)
                warning.grab_set()

                # จัดการตำแหน่งหน้าต่าง
                x = self.root.winfo_x() + (self.root.winfo_width() - 300) // 2
                y = self.root.winfo_y() + (self.root.winfo_height() - 150) // 2
                warning.geometry(f"+{x}+{y}")

                # สร้าง UI elements
                message = tk.Label(
                    warning,
                    text="คุณยังไม่ได้บันทึกการเปลี่ยนแปลง\nต้องการบันทึกก่อนเปลี่ยน Preset หรือไม่?",
                    bg="#1a1a1a",
                    fg="white",
                    font=("FC Minimal Medium", 11),
                )
                message.pack(pady=20)

                button_frame = tk.Frame(warning, bg="#1a1a1a")
                button_frame.pack(pady=10)

                def save_and_switch():
                    self.save_preset()
                    self.has_unsaved_changes = False
                    self._complete_preset_switch(preset_number)
                    warning.destroy()

                def switch_without_save():
                    self.has_unsaved_changes = False
                    self._complete_preset_switch(preset_number)
                    warning.destroy()

                # สร้างปุ่ม
                save_btn = tk.Button(
                    button_frame,
                    text="บันทึก",
                    command=save_and_switch,
                    bg="#404040",
                    fg="#00FFFF",
                    font=("FC Minimal Medium", 11),
                    width=10,
                )
                save_btn.pack(side=tk.LEFT, padx=5)

                no_save_btn = tk.Button(
                    button_frame,
                    text="ไม่บันทึก",
                    command=switch_without_save,
                    bg="#404040",
                    fg="white",
                    font=("FC Minimal Medium", 11),
                    width=10,
                )
                no_save_btn.pack(side=tk.LEFT, padx=5)

            else:
                self._complete_preset_switch(preset_number)

    def _complete_preset_switch(self, preset_number):
        """ดำเนินการเปลี่ยน Preset หลังจากยืนยัน (ถ้าจำเป็น)"""
        try:
            # 1. อัปเดต Preset ปัจจุบันใน Control UI
            self.current_preset = preset_number
            logging.info(f"Control UI internal preset set to: {preset_number}")

            # 2. โหลดข้อมูล preset เพื่อใช้งาน
            preset_data = self.settings.get_preset(preset_number)
            if not preset_data:
                logging.warning(f"Could not get preset data for number {preset_number}")
                preset_data = {"areas": "A", "coordinates": {}}

            # 3. อัพเดตสถานะ area_states ตาม preset
            area_string = preset_data.get("areas", "A")
            active_areas = area_string.split("+")
            for area in ["A", "B", "C"]:
                self.area_states[area] = area in active_areas

            # 4. สำคัญ!!! โหลดพิกัดจาก preset ไปยัง translate_areas ใน settings
            coordinates = preset_data.get("coordinates", {})
            if isinstance(coordinates, dict):
                for area in active_areas:
                    area_coords = coordinates.get(area)
                    if isinstance(area_coords, dict) and all(
                        k in area_coords
                        for k in ["start_x", "start_y", "end_x", "end_y"]
                    ):
                        # สร้างสำเนาพิกัดก่อนตั้งค่า
                        self.settings.set_translate_area(
                            area_coords["start_x"],
                            area_coords["start_y"],
                            area_coords["end_x"],
                            area_coords["end_y"],
                            area,
                        )
                        logging.debug(
                            f"Loaded coordinates for area {area} from preset {preset_number}"
                        )

            # 5. อัปเดต UI ของ Control UI (ไฮไลท์ปุ่ม Preset)
            self.update_preset_buttons()

            # 6. อัปเดต title label เพื่อแสดง preset ปัจจุบัน
            self.update_preset_display()

            # 7. *** สำคัญ: ลบพิกัดของพื้นที่ที่ไม่ได้อยู่ใน preset ปัจจุบันออกจาก translate_areas ***
            # เพื่อป้องกันการค้างอยู่ของพิกัดจาก preset อื่น
            for area in ["A", "B", "C"]:
                if area not in active_areas:
                    # ลบพิกัดพื้นที่ที่ไม่ได้ใช้
                    empty_coords = {"start_x": 0, "start_y": 0, "end_x": 0, "end_y": 0}
                    self.settings.set_translate_area(
                        empty_coords["start_x"],
                        empty_coords["start_y"],
                        empty_coords["end_x"],
                        empty_coords["end_y"],
                        area,
                    )
                    logging.debug(f"Reset coordinates for unused area {area}")

            # 8. *** สำคัญ: ล้างสถานะ Unsaved Changes เพราะเราเพิ่งโหลด preset ใหม่ ***
            self.has_unsaved_changes = False
            self.update_button_highlights()  # อัพเดทสถานะปุ่ม Save

            # 9. แจ้งการเปลี่ยนแปลงพื้นที่ไปยัง MBB.py ผ่าน Callback
            if self.switch_area_callback:
                # *** ดึง Area String ของ Preset ใหม่ ***
                new_preset_data = self.settings.get_preset(preset_number)
                new_area_str = "A"  # Fallback
                if new_preset_data and isinstance(new_preset_data.get("areas"), str):
                    new_area_str = new_preset_data["areas"]
                else:
                    logging.warning(
                        f"Could not get area string for preset {preset_number} in _complete_preset_switch. Falling back to 'A'."
                    )

                # *** ส่ง Area String ที่ถูกต้องไปใน Callback ***
                self.switch_area_callback(
                    areas=new_area_str,
                    preset_number_override=preset_number,
                    source="control_ui",
                )
                logging.info(
                    f"Callback sent to MBB: switch_area(areas='{new_area_str}', preset_override={preset_number}, source='control_ui')"
                )
            else:
                logging.warning("switch_area_callback not set in Control_UI!")

            # 10. แสดง feedback การสลับ preset (ถ้ามี callback)
            if self.trigger_temporary_area_display_callback:
                try:
                    # ดึง area string จาก preset ใหม่ที่เพิ่งตั้งค่าไป
                    new_preset_data = self.settings.get_preset(preset_number)
                    if new_preset_data and "areas" in new_preset_data:
                        area_string_for_feedback = new_preset_data["areas"]
                        self.trigger_temporary_area_display_callback(
                            area_string_for_feedback
                        )
                        logging.info(
                            f"Triggered temporary display for areas: {area_string_for_feedback}"
                        )
                    else:
                        logging.warning(
                            f"Could not get area string for preset {preset_number} for feedback."
                        )
                except Exception as e:
                    logging.error(f"Error triggering temporary area display: {e}")

            logging.info(f"Preset switch to {preset_number} completed in Control UI.")
            
            # อัพเดตสถานะปุ่ม EDIT ตามพิกัดของ preset ใหม่
            self.update_edit_button_state()
            
            # อัพเดตสถานะการล็อกปุ่ม area (ถ้าอยู่ใน edit mode)
            if self.edit_frame.winfo_ismapped():
                self.update_area_buttons_lock_state()

        except Exception as e:
            logging.error(f"Error during preset switch completion: {e}")
            import traceback

            traceback.print_exc()
            messagebox.showerror(
                "Error", f"An error occurred while switching presets: {e}"
            )

    # +++ NEW METHOD +++
    def select_preset_button(self, preset_num):
        """
        อัปเดต UI เพื่อแสดงผลว่า Preset นี้ถูกเลือก (โดยไม่มีการ trigger callback กลับไป MBB)
        เมธอดนี้มีไว้สำหรับ MBB.py เรียกใช้ผ่าน sync_last_used_preset
        """
        if not (1 <= preset_num <= self.max_presets):
            logging.warning(
                f"Control_UI received invalid preset number to select: {preset_num}"
            )
            return

        # 1. อัปเดต internal state ของ Control UI
        self.current_preset = preset_num
        logging.debug(f"Control UI externally set to preset: {preset_num}")

        # 2. อัปเดต UI (ไฮไลท์ปุ่ม, title)
        self.update_preset_buttons()
        self.update_preset_display()

        # 3. สำคัญ: ไม่เรียก self.switch_area_callback หรือ _complete_preset_switch ที่นี่!

    # +++ NEW METHOD +++
    def clear_unsaved_changes_flag(self):
        """
        ล้างสถานะ 'has_unsaved_changes' และอัปเดตสถานะปุ่ม Save
        มีไว้สำหรับ MBB.py เรียกใช้เมื่อ preset เปลี่ยนจากแหล่งอื่น
        """
        self.has_unsaved_changes = False
        self.update_button_highlights()
        logging.debug("Control UI unsaved changes flag cleared.")

    def update_preset_buttons(self):
        """อัพเดทการแสดงผลของปุ่ม Preset ทั้งหมด (ไฮไลท์, ข้อความ)"""
        try:
            active_bg = self.theme.get("accent", "#6c5ce7")
            active_fg = self.theme.get("text", "#ffffff")
            inactive_bg = self.theme.get("button_bg", "#262637")
            inactive_fg = self.theme.get("text_dim", "#b2b2b2")

            for btn in self.preset_buttons:
                if btn and btn.winfo_exists():
                    preset_num = btn.preset_num
                    is_selected = preset_num == self.current_preset
                    btn.selected = is_selected
                    display_name = self.settings.get_preset_display_name(preset_num)
                    btn.configure(text=display_name)
                    if is_selected:
                        # ปุ่มที่ Active: พื้นหลังสีหลัก, ตัวอักษรสีขาว
                        btn.configure(bg=active_bg, fg=active_fg)
                    else:
                        # ปุ่มที่ไม่ Active: พื้นหลังสีปกติ, ตัวอักษรสีจาง
                        btn.configure(bg=inactive_bg, fg=inactive_fg)

            # *** แก้ไข: อัพเดต Preset Title Label ***
            if (
                hasattr(self, "preset_title_label")
                and self.preset_title_label.winfo_exists()
            ):
                current_display_name = self.settings.get_preset_display_name(
                    self.current_preset
                )
                self.preset_title_label.config(text=f"PRESET: {current_display_name}")
                # เปลี่ยนสีถ้าเป็น custom preset ที่ยังไม่ได้ตั้งชื่อเอง
                is_default_custom_name = (
                    self.current_preset >= 4
                    and current_display_name == f"Preset {self.current_preset}"
                )
                title_fg = (
                    inactive_fg if is_default_custom_name else active_bg
                )  # ใช้ inactive_fg หรือ active_bg (สี accent)
                self.preset_title_label.config(fg=title_fg)
                # เปิด/ปิด การคลิกแก้ไขชื่อตาม preset
                if self.current_preset >= 4:
                    self.preset_title_label.configure(cursor="hand2")
                    self.preset_title_label.bind("<Button-1>", self.edit_preset_name)
                else:
                    self.preset_title_label.configure(cursor="")
                    self.preset_title_label.unbind("<Button-1>")

        except Exception as e:
            print(f"Error updating preset buttons: {e}")
            logging.error(f"Error updating preset buttons: {e}")
            import traceback

            traceback.print_exc()

    def apply_rounded_corners(self):
        """ทำให้หน้าต่างมีขอบโค้งมน"""
        try:
            # รอให้ window แสดงผล
            self.root.update_idletasks()

            # ดึงค่า HWND ของ window
            hwnd = windll.user32.GetParent(self.root.winfo_id())

            # ลบกรอบและหัวข้อ
            style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
            style &= ~win32con.WS_CAPTION
            style &= ~win32con.WS_THICKFRAME
            win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)

            # สร้างภูมิภาค (region) โค้งมน
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            region = win32gui.CreateRoundRectRgn(0, 0, width, height, 15, 15)

            # กำหนดภูมิภาคให้กับ window
            win32gui.SetWindowRgn(hwnd, region, True)

        except Exception as e:
            print(f"Error applying rounded corners: {e}")

    def update_theme(self, accent_color=None, highlight_color=None):
        """อัพเดท UI ของ Control UI ตาม Theme ปัจจุบัน"""
        try:
            logging.info("Control_UI: Starting theme update...")
            # ดึงค่าสีล่าสุดจาก appearance_manager
            theme_bg = appearance_manager.bg_color
            theme_accent = appearance_manager.get_accent_color()
            theme_accent_light = appearance_manager.get_theme_color("accent_light")
            theme_secondary = appearance_manager.get_theme_color("secondary", "#4A4A4A")
            theme_button_bg = appearance_manager.get_theme_color("button_bg", "#262637")
            theme_text = appearance_manager.get_theme_color("text", "#FFFFFF")
            theme_text_dim = appearance_manager.get_theme_color("text_dim", "#B2B2B2")
            theme_highlight = appearance_manager.get_highlight_color()
            theme_error = appearance_manager.get_theme_color(
                "error", "#FF4136"
            )  # ใช้สีแดงที่สอดคล้องกัน
            theme_success = appearance_manager.get_theme_color("success", "#4CAF50")
            theme_button_inactive_bg = appearance_manager.get_theme_color(
                "button_inactive_bg", "#555555"
            )
            theme_border = appearance_manager.get_theme_color("border", "#444444")

            self.theme = {
                "bg": theme_bg,
                "accent": theme_accent,
                "accent_light": theme_accent_light,
                "secondary": theme_secondary,
                "button_bg": theme_button_bg,
                "text": theme_text,
                "text_dim": theme_text_dim,
                "highlight": theme_highlight,
                "error": theme_error,
                "success": theme_success,
                "button_inactive_bg": theme_button_inactive_bg,
                "border": theme_border,
                "fg": theme_text,  # เพิ่ม fg เข้าไปใน theme dictionary ด้วย
            }
            logging.debug(f"Control_UI: Theme dictionary updated: {self.theme}")

            if hasattr(self, "root") and self.root.winfo_exists():
                self.root.configure(bg=theme_bg)
            if hasattr(self, "main_frame") and self.main_frame.winfo_exists():
                self.main_frame.configure(bg=theme_bg)

            # อัปเดตปุ่มปิด (X)
            if hasattr(self, "close_button") and self.close_button.winfo_exists():
                # อัปเดตสีพื้นหลังปกติ
                self.close_button.config(bg=theme_bg)

                # อัปเดต hover events เพื่อให้ใช้สีพื้นหลังใหม่ที่ถูกต้อง
                self.close_button.unbind("<Enter>")
                self.close_button.unbind("<Leave>")

                def on_themed_close_enter(event):
                    self.close_button.config(bg="#E53935", cursor="hand2")

                def on_themed_close_leave(event):
                    self.close_button.config(bg=self.theme.get("bg"), cursor="")

                self.close_button.bind("<Enter>", on_themed_close_enter)
                self.close_button.bind("<Leave>", on_themed_close_leave)

            if hasattr(self, "title_label") and self.title_label.winfo_exists():
                self.title_label.configure(bg=theme_bg, fg=theme_accent)
            # Header separator - REMOVED

            # อัปเดตพื้นหลังของ Frames ย่อยๆ และ Labels ภายใน
            if hasattr(self, "main_frame") and self.main_frame.winfo_exists():
                for child_widget in self.main_frame.winfo_children():
                    if (
                        isinstance(child_widget, tk.Frame)
                        and child_widget.winfo_exists()
                    ):
                        child_widget.configure(bg=theme_bg)
                        for sub_child_widget in child_widget.winfo_children():
                            if (
                                isinstance(sub_child_widget, tk.Frame)
                                and sub_child_widget.winfo_exists()
                            ):
                                sub_child_widget.configure(bg=theme_bg)
                                for (
                                    grand_child_widget
                                ) in sub_child_widget.winfo_children():
                                    if (
                                        isinstance(grand_child_widget, tk.Label)
                                        and grand_child_widget.winfo_exists()
                                    ):
                                        if "CPU Limit:" in grand_child_widget.cget(
                                            "text"
                                        ):
                                            grand_child_widget.configure(
                                                bg=theme_bg, fg=theme_text
                                            )
                                        elif "ℹ️" in grand_child_widget.cget("text"):
                                            grand_child_widget.configure(
                                                bg=theme_bg, fg=theme_accent
                                            )
                            elif (
                                isinstance(sub_child_widget, tk.Label)
                                and sub_child_widget.winfo_exists()
                            ):
                                if "PRESET:" in sub_child_widget.cget("text").upper():
                                    is_default_custom_name = (
                                        self.current_preset >= 4
                                        and self.settings.get_preset_display_name(
                                            self.current_preset
                                        )
                                        == f"Preset {self.current_preset}"
                                    )
                                    label_fg = (
                                        theme_text_dim
                                        if is_default_custom_name
                                        else theme_accent
                                    )
                                    sub_child_widget.configure(bg=theme_bg, fg=label_fg)
                                elif hasattr(sub_child_widget.master, "switch_canvas"):
                                    sub_child_widget.configure(
                                        bg=theme_bg, fg=theme_text
                                    )

            active_fg_color = theme_text
            inactive_fg_color = theme_text_dim

            # ปุ่ม Camera
            camera_btn = getattr(self, "camera_button", None)
            if camera_btn and camera_btn.winfo_exists():
                camera_btn.configure(
                    bg=theme_button_bg, activebackground=theme_accent_light
                )

            # ปุ่ม Define Area A, B, C
            define_area_buttons_list = [
                getattr(self, "define_area_a_button_ctrl", None),
                getattr(self, "define_area_b_button_ctrl", None),
                getattr(self, "define_area_c_button_ctrl", None),
            ]
            for btn in define_area_buttons_list:
                if btn and btn.winfo_exists():
                    btn.configure(
                        bg=theme_button_bg,
                        fg=theme_text,
                        activebackground=theme_accent_light,
                        activeforeground=theme_text,
                    )

            # ปุ่ม Force
            force_btn = getattr(self, "force_button", None)
            if force_btn and force_btn.winfo_exists():
                is_click_on = self.click_translate_var.get()
                f_bg = theme_error if is_click_on else theme_button_bg
                f_text = (
                    "Translate 1 Time" if is_click_on else "FORCE"
                )  # เปลี่ยนจาก "TOUCH" เป็น "Translate 1 Time"
                f_width = 15 if is_click_on else 7  # ปรับขนาดปุ่มตามสถานะ
                force_btn.configure(
                    text=f_text,
                    bg=f_bg,
                    fg=theme_text,
                    width=f_width,  # เพิ่มการจัดการ width
                    activebackground=(
                        self.lighten_color(
                            f_bg, 0.2
                        )  # ใช้ self.lighten_color (ไม่มี underscore)
                        if is_click_on
                        else theme_accent_light
                    ),
                    activeforeground=theme_text,
                )
                # ปุ่ม Force - เพิ่ม hover effects ที่ทำงานร่วมกับ tooltip
                force_btn.unbind("<Enter>")
                force_btn.unbind("<Leave>")

                # เพิ่ม hover effects ที่ทำงานร่วมกับ tooltip system
                def on_themed_hover_enter(event):
                    if force_btn.winfo_exists():
                        # 1. แสดง hover effect ก่อน
                        force_btn.config(bg=theme_accent_light)

                        # 2. เรียก tooltip callback หากมี
                        if hasattr(force_btn, "_tooltip_enter_callback"):
                            try:
                                import types

                                dummy_event = types.SimpleNamespace()
                                dummy_event.widget = force_btn
                                force_btn._tooltip_enter_callback(dummy_event)
                            except Exception as e:
                                logging.debug(f"Tooltip enter callback error: {e}")

                def on_themed_hover_leave(event):
                    if force_btn.winfo_exists():
                        # 1. เปลี่ยนสีกลับ
                        force_btn.config(bg=f_bg)

                        # 2. เรียก tooltip callback หากมี
                        if hasattr(force_btn, "_tooltip_leave_callback"):
                            try:
                                import types

                                dummy_event = types.SimpleNamespace()
                                dummy_event.widget = force_btn
                                force_btn._tooltip_leave_callback(dummy_event)
                            except Exception as e:
                                logging.debug(f"Tooltip leave callback error: {e}")

                force_btn.bind("<Enter>", on_themed_hover_enter)
                force_btn.bind("<Leave>", on_themed_hover_leave)

                logging.debug(
                    "Force button theme updated with hover effects + tooltip integration"
                )

            # ปุ่ม Show/Hide Area
            show_hide_btn = getattr(self, "show_hide_area_button_ctrl", None)
            if show_hide_btn and show_hide_btn.winfo_exists():
                if hasattr(self, "is_area_shown") and self.is_area_shown:
                    sh_bg = self.theme.get("error", "#FF4136")
                else:
                    sh_bg = self.theme.get("button_bg", "#262637")

                show_hide_btn.configure(
                    bg=sh_bg,
                    fg=self.theme.get("text", "white"),
                    activebackground=self.theme.get("accent_light", "#87CEFA"),
                    activeforeground=self.theme.get("text", "white"),
                )

            # ปุ่ม Toggle Area A, B, C (Active State)
            area_toggle_buttons_map = {
                "A": getattr(self, "button_a", None),
                "B": getattr(self, "button_b", None),
                "C": getattr(self, "button_c", None),
            }
            current_role = self.settings.get_preset_role(self.current_preset)
            is_custom = current_role == "custom" or self.current_preset >= 4
            disabled_bg_toggle = "#303030"
            disabled_fg_toggle = "#606060"
            for area, btn in area_toggle_buttons_map.items():
                if btn and btn.winfo_exists():
                    is_area_active = self.area_states.get(area, False)
                    if not is_custom:
                        btn.configure(
                            bg=disabled_bg_toggle,
                            fg=disabled_fg_toggle,
                            state=tk.DISABLED,
                            cursor="",
                        )
                    else:
                        final_bg = (
                            theme_accent
                            if is_area_active
                            else (
                                theme_secondary
                                if area in ["B", "C"] and not is_area_active
                                else theme_button_bg
                            )
                        )
                        final_fg = (
                            active_fg_color
                            if is_area_active
                            else (
                                theme_text
                                if area in ["B", "C"] and not is_area_active
                                else inactive_fg_color
                            )
                        )
                        btn.configure(
                            bg=final_bg,
                            fg=final_fg,
                            state=tk.NORMAL,
                            cursor="hand2",
                            activebackground=theme_accent_light,
                            activeforeground=active_fg_color,
                            relief=tk.SUNKEN if is_area_active else tk.FLAT,
                        )

            # ปุ่ม CPU Limit
            cpu_btn_map = {
                50: getattr(self, "cpu_50_btn", None),
                60: getattr(self, "cpu_60_btn", None),
                80: getattr(self, "cpu_80_btn", None),
            }
            #             current_cpu = self.settings.get("cpu_limit", 80)
            for limit, btn in cpu_btn_map.items():
                if btn and btn.winfo_exists():
                    is_cpu_active = limit == current_cpu
                    cpu_bg = theme_accent if is_cpu_active else theme_button_bg
                    cpu_fg = active_fg_color if is_cpu_active else theme_text
                    btn.configure(
                        bg=cpu_bg,
                        fg=cpu_fg,
                        activebackground=theme_accent_light,
                        activeforeground=active_fg_color,
                        relief=tk.SUNKEN if is_cpu_active else tk.FLAT,
                    )

            # ปุ่ม Preset Numbers (P1-P6)
            preset_buttons_list = getattr(self, "preset_buttons", [])
            for btn in preset_buttons_list:
                if btn and btn.winfo_exists():
                    is_btn_selected = btn.preset_num == self.current_preset
                    preset_btn_bg = theme_accent if is_btn_selected else theme_button_bg
                    preset_btn_fg = (
                        active_fg_color if is_btn_selected else inactive_fg_color
                    )
                    btn.configure(
                        bg=preset_btn_bg,
                        fg=preset_btn_fg,
                        activebackground=theme_accent_light,
                        activeforeground=active_fg_color,
                        relief=tk.SUNKEN if is_btn_selected else tk.FLAT,
                    )
                    display_name_p_btn = self.settings.get_preset_display_name(
                        btn.preset_num
                    )
                    self.auto_resize_font(btn, display_name_p_btn, 70)

            # ปุ่ม Save
            save_btn_widget = getattr(self, "save_button", None)
            if save_btn_widget and save_btn_widget.winfo_exists():
                save_bg = theme_error if self.has_unsaved_changes else theme_button_bg
                save_state = tk.NORMAL if self.has_unsaved_changes else tk.DISABLED
                save_cursor = "hand2" if self.has_unsaved_changes else ""
                save_btn_widget.configure(
                    bg=save_bg,
                    fg=theme_text,
                    activebackground=(
                        self.lighten_color(
                            save_bg, 0.2
                        )  # ใช้ self.lighten_color (ไม่มี underscore)
                        if self.has_unsaved_changes
                        else theme_accent_light
                    ),
                    activeforeground=theme_text,
                    state=save_state,
                    cursor=save_cursor,
                    relief=tk.RAISED if self.has_unsaved_changes else tk.FLAT,
                    bd=1 if self.has_unsaved_changes else 0,
                )

            # --- อัพเดท Toggle Switches (Canvas-based) ---
            toggles_to_update_list = [
                (
                    getattr(self, "click_translate_switch_container", None),
                    self.click_translate_var,
                ),
                (
                    getattr(self, "hover_translate_switch_container", None),
                    self.hover_translation_var,
                ),
            ]
            for container_widget, var_obj in toggles_to_update_list:
                if container_widget and container_widget.winfo_exists():
                    container_widget.configure(bg=theme_bg)
                    for child_w in container_widget.winfo_children():
                        if isinstance(child_w, tk.Label) and child_w.winfo_exists():
                            child_w.configure(bg=theme_bg, fg=theme_text)
                        elif isinstance(child_w, tk.Canvas) and child_w.winfo_exists():
                            # Canvas bg is colorkey, do not change to theme_bg here
                            pass

                    if hasattr(container_widget, "update_ui_func"):
                        container_widget.update_ui_func(var_obj.get())
                        logging.debug(
                            f"Control_UI: Re-rendered toggle switch: {container_widget}"
                        )
                    else:
                        logging.warning(
                            f"update_ui_func missing for toggle: {container_widget}"
                        )

            if hasattr(self, "root") and self.root.winfo_exists():
                self.root.update_idletasks()
            logging.info("Control_UI: Theme update process completed.")

        except Exception as e:
            logging.error(f"Control_UI: Error during theme update: {e}")
            import traceback

            logging.error(traceback.format_exc())

    def lighten_color(self, color, factor=1.3):
        """ทำให้สีอ่อนลงตามค่า factor

        Args:
            color: สีเริ่มต้นในรูปแบบ hex (#RRGGBB)
            factor: ค่าที่ใช้ในการทำให้อ่อนลง (ค่ามากกว่า 1)

        Returns:
            str: สีที่อ่อนลงในรูปแบบ hex
        """
        if not isinstance(color, str) or not color.startswith("#"):
            return color

        try:
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)

            r = min(int(r * factor), 255)
            g = min(int(g * factor), 255)
            b = min(int(b * factor), 255)

            return f"#{r:02x}{g:02x}{b:02x}"
        except Exception as e:
            print(f"Error lightening color: {e}")
            return color

    def get_current_area_string(self):
        """รับสตริงแสดงพื้นที่ที่เลือกในปัจจุบัน"""
        active = [area for area in ["A", "B", "C"] if self.area_states[area]]
        return "+".join(active) if active else "A"

    def load_current_area_states(self):
        """โหลดสถานะพื้นที่ปัจจุบัน"""
        saved_area = self.settings.get("current_area", "A+B")
        if saved_area:
            areas = saved_area.split("+")
            for area in ["A", "B", "C"]:
                self.area_states[area] = area in areas

    def switch_speed(self, speed_mode):
        """สลับระหว่างโหมดความเร็วโดยใช้สีจากธีม"""
        self.current_speed = speed_mode

        # อัพเดตสถานะและการแสดงผลของปุ่มความเร็ว
        if speed_mode == "normal":
            # เลือก Normal
            self.normal_speed_button.selected = True
            self.high_speed_button.selected = False

            # อัพเดตสีทันทีไม่ต้องมี delay
            self.normal_speed_button.config(
                fg=self.theme["highlight"], bg=self.theme["button_bg"]
            )
            self.high_speed_button.config(
                fg=self.theme["text_dim"], bg=self.theme["button_bg"]
            )
        else:
            # เลือก High
            self.normal_speed_button.selected = False
            self.high_speed_button.selected = True

            # อัพเดตสีทันทีไม่ต้องมี delay
            self.normal_speed_button.config(
                fg=self.theme["text_dim"], bg=self.theme["button_bg"]
            )
            self.high_speed_button.config(
                fg=self.theme["highlight"], bg=self.theme["button_bg"]
            )

        # เรียก callback ถ้ามี
        if hasattr(self, "speed_callback"):
            self.speed_callback(speed_mode)

        else:
            # เลือก High
            self.normal_speed_button.selected = False
            self.high_speed_button.selected = True

            # อัพเดตสีด้วยเอฟเฟกต์
            def update_colors():
                # Normal
                self.normal_speed_button.config(
                    fg=self.theme["text_dim"], bg=self.theme["button_bg"]
                )
                # High
                self.high_speed_button.config(
                    fg=self.theme["highlight"], bg=self.theme["button_bg"]
                )

            # เพิ่มเอฟเฟกต์เล็กน้อย
            self.high_speed_button.config(bg=self.theme["accent_light"])
            self.root.after(100, update_colors)

        # เรียก callback ถ้ามี
        if hasattr(self, "speed_callback"):
            self.speed_callback(speed_mode)

    def position_below_main_ui(self):
        """จัดตำแหน่ง Control UI ให้อยู่ด้านล่างของ Main UI"""
        if hasattr(self.root.master, "winfo_x") and hasattr(
            self.root.master, "winfo_y"
        ):
            main_x = self.root.master.winfo_x()
            main_y = self.root.master.winfo_y()
            main_height = self.root.master.winfo_height()

            new_x = main_x
            new_y = main_y + main_height + 5

            self.ui_cache["position_x"] = new_x
            self.ui_cache["position_y"] = new_y

            self.root.geometry(f"+{new_x}+{new_y}")

    def show_window(self):
        """แสดงหน้าต่าง Control UI"""
        if self.root.winfo_exists():
            if self.ui_cache["position_x"] is not None:
                self.restore_cached_position()
            else:
                # เปลี่ยนจาก position_below_main_ui เป็น position_right_of_main_ui
                self.position_right_of_main_ui()

            # โหลดสถานะที่บันทึกไว้
            current_areas = self.ui_cache["current_area"].split("+")
            for area in ["A", "B", "C"]:
                self.area_states[area] = area in current_areas

            self.root.deiconify()
            self.root.lift()
            self.root.attributes("-topmost", True)
            self.update_button_highlights()
            self.update_preset_display()

    def restore_cached_position(self):
        """กู้คืนตำแหน่งจากแคช"""
        if (
            self.ui_cache["position_x"] is not None
            and self.ui_cache["position_y"] is not None
        ):
            self.root.geometry(
                f"+{self.ui_cache['position_x']}+{self.ui_cache['position_y']}"
            )

    def position_smartly_relative_to_main_ui(self):
        """วางตำแหน่ง Control UI อย่างฉลาด - เลือกด้านซ้ายหรือขวาของ Main UI ตามตำแหน่ง และจัดขอบบนให้เท่ากัน

        ฟังก์ชันใหม่ที่มีการตรวจสอบตำแหน่ง Main UI และตัดสินใจว่าจะวาง Control UI ด้านไหน
        """
        return self.position_right_of_main_ui()  # เรียกใช้ฟังก์ชันที่ปรับปรุงแล้ว

    def position_right_of_main_ui(self):
        """
        [แก้ไข] วางตำแหน่งหน้าต่าง Control UI อย่างฉลาด โดยจะตรวจสอบว่า Main UI อยู่บนจอภาพใด
        และวาง Control UI ไว้ด้านซ้ายหรือขวาบนจอภาพเดียวกันนั้น
        """
        if not hasattr(self, "parent_root") or not self.parent_root.winfo_exists():
            logging.warning(
                "Cannot position Control UI: parent_root (Main UI) is not available."
            )
            return

        # ดึงข้อมูลตำแหน่งและขนาดของ Main UI
        main_x = self.parent_root.winfo_x()
        main_y = self.parent_root.winfo_y()
        main_width = self.parent_root.winfo_width()

        # ดึงขนาดของ Control UI
        self.root.update_idletasks()
        control_width = self.root.winfo_width()
        control_height = self.root.winfo_height()

        monitor_left, monitor_top, monitor_width, monitor_height = 0, 0, 0, 0

        # --- ตรรกะใหม่: การตรวจจับจอภาพที่ Main UI อยู่ ---
        try:
            # ดึง handle ของจอภาพที่หน้าต่าง Main UI แสดงอยู่
            main_hwnd = int(self.parent_root.winfo_id())
            hmonitor = win32api.MonitorFromWindow(
                main_hwnd, win32con.MONITOR_DEFAULTTONEAREST
            )

            # ดึงข้อมูลของจอภาพนั้นๆ (ใช้ 'Work' เพื่อไม่ให้ทับ Taskbar)
            monitor_info = win32api.GetMonitorInfo(hmonitor)
            monitor_rect = monitor_info[
                "Work"
            ]  # ผลลัพธ์คือ tuple (left, top, right, bottom)

            monitor_left = monitor_rect[0]
            monitor_top = monitor_rect[1]
            monitor_width = monitor_rect[2] - monitor_left
            monitor_height = monitor_rect[3] - monitor_top

            logging.info(f"Main UI is on monitor with geometry: {monitor_rect}")

        except Exception as e:
            logging.error(
                f"Failed to get specific monitor info, falling back to primary screen. Error: {e}"
            )
            # หากเกิดข้อผิดพลาด ให้กลับไปใช้ตรรกะเดิม (อิงจากจอหลัก)
            monitor_left = 0
            monitor_top = 0
            monitor_width = self.root.winfo_screenwidth()
            monitor_height = self.root.winfo_screenheight()
        # --- สิ้นสุดตรรกะใหม่ ---

        gap = 10  # ลดระยะห่างเพื่อให้ดูชิดกันมากขึ้น

        # ตัดสินใจว่าจะวางซ้ายหรือขวา โดยอิงจากตำแหน่งของ Main UI บน "จอของมันเอง"
        main_center_on_its_monitor = main_x - monitor_left + (main_width // 2)
        monitor_center_x = monitor_width // 2

        if main_center_on_its_monitor <= monitor_center_x:
            # Main UI ค่อนไปทางซ้ายของจอ -> วาง Control UI ไว้ด้านขวา
            new_x = main_x + main_width + gap
            # แต่ถ้าวางขวาแล้วล้นจอของมัน ให้สลับไปวางด้านซ้ายแทน
            if new_x + control_width > monitor_left + monitor_width:
                new_x = main_x - control_width - gap
        else:
            # Main UI ค่อนไปทางขวาของจอ -> วาง Control UI ไว้ด้านซ้าย
            new_x = main_x - control_width - gap
            # แต่ถ้าวางซ้ายแล้วล้นจอของมัน ให้สลับไปวางด้านขวาแทน
            if new_x < monitor_left:
                new_x = main_x + main_width + gap

        # จัดตำแหน่งแนวตั้งให้ขอบบนตรงกัน
        new_y = main_y

        # ตรวจสอบขอบเขตแนวตั้งอีกครั้ง เพื่อให้แน่ใจว่าไม่ล้นจอบน-ล่าง
        if new_y < monitor_top:
            new_y = monitor_top
        if new_y + control_height > monitor_top + monitor_height:
            new_y = monitor_top + monitor_height - control_height

        # กำหนดตำแหน่งสุดท้ายและบันทึกลงแคช
        self.root.geometry(f"+{new_x}+{new_y}")
        self.ui_cache["position_x"] = new_x
        self.ui_cache["position_y"] = new_y
        logging.info(f"Control UI positioned on the same monitor at ({new_x}, {new_y})")

    def close_window(self):
        """ปิดหน้าต่าง Control UI และแจ้ง Main UI ผ่าน callback"""
        try:
            # ปิด tooltip และ overlay ที่อาจจะเปิดอยู่
            self.hide_all_tooltips()
            self.hide_show_area_ctrl()

            if self.root.winfo_exists():
                if self.root.state() != "withdrawn":
                    self.root.withdraw()

            # ### ส่วนที่เพิ่มเข้ามา ###
            # ตรวจสอบว่ามี parent_app และ callback method หรือไม่
            if hasattr(self, "parent_app") and self.parent_app:
                if hasattr(self.parent_app, "on_control_close"):
                    logging.info(
                        "Control_UI: Calling on_control_close callback in parent app."
                    )
                    # เรียก callback ใน Main UI เพื่ออัปเดตสถานะปุ่ม "CON"
                    self.parent_app.on_control_close()
                else:
                    logging.warning(
                        "Control_UI: Parent app does not have on_control_close method."
                    )
            else:
                logging.warning(
                    "Control_UI: Parent app not set, cannot send close signal."
                )

        except Exception as e:
            logging.error(f"Error closing Control UI window: {e}")

    def update_display(self, area_string, preset_number=None):
        """
        Updates the Control UI's display based on the state provided by MBB.py.
        This method ONLY updates the UI and internal state; it does NOT trigger
        callbacks or save actions. Now includes updating toggle switches.

        Args:
            area_string (str): The string representing active areas (e.g., "A+B").
            preset_number (int, optional): The preset number that corresponds
                                            to this state. Defaults to None.
        """
        logging.info(
            f"Control_UI received update_display: areas='{area_string}', preset={preset_number}"
        )
        try:
            # --- Update Internal State ---
            if preset_number is not None and self.current_preset != preset_number:
                if 1 <= preset_number <= self.max_presets:
                    self.current_preset = preset_number
                    logging.debug(
                        f"Control_UI preset updated to {preset_number} by external call."
                    )
                else:
                    logging.warning(
                        f"Received invalid preset number {preset_number} in update_display."
                    )

            active_areas = area_string.split("+") if area_string else []
            for area in ["A", "B", "C"]:
                self.area_states[area] = area in active_areas
            logging.debug(
                f"Control_UI area_states updated to: {self.area_states} based on '{area_string}'"
            )

            # --- Refresh UI Elements ---
            self.update_preset_buttons()  # Preset buttons highlight/text
            self.update_button_highlights()  # Area buttons highlight/lock & Save button state

            # อัพเดท Toggle Switches ทั้งสอง
            self.update_click_translate_toggle(
                self.settings.get("enable_click_translate", False)
            )
            self.update_hover_translate_toggle(
                self.settings.get("enable_hover_translation", False)
            )
            # อัพเดท UI ปุ่ม Force ตามสถานะ Click Translate
            self._update_force_button_ui(self.click_translate_var.get())

            # *** เพิ่มการตรวจสอบว่า attribute มีอยู่หรือไม่ ***
            if not hasattr(self, "has_unsaved_changes"):
                self.has_unsaved_changes = False
                logging.debug("Initialized has_unsaved_changes in update_display")

            logging.info(
                f"Control_UI update_display finished. Preset: {self.current_preset}, Areas: {self.get_current_area_string()}, Unsaved: {self.has_unsaved_changes}, ClickT: {self.click_translate_var.get()}, HoverT: {self.hover_translation_var.get()}"
            )

        except Exception as e:
            logging.error(f"Error in Control_UI.update_display: {e}", exc_info=True)

    def update_click_translate_toggle(self, is_enabled):
        """อัพเดทสถานะและ UI ของ Click Translate Toggle Switch"""
        try:
            logging.info(
                f"ControlUI: update_click_translate_toggle received value: {is_enabled}"
            )

            # 1. อัพเดท BooleanVar
            var_updated = False
            if hasattr(self, "click_translate_var"):
                current_var_value = self.click_translate_var.get()
                if current_var_value != is_enabled:
                    self.click_translate_var.set(is_enabled)
                    var_updated = True
                    logging.info(
                        f"ControlUI: Set click_translate_var to {self.click_translate_var.get()}"
                    )
                else:
                    logging.debug(
                        f"ControlUI: click_translate_var already has value {is_enabled}"
                    )
            else:
                logging.error(
                    "ControlUI: click_translate_var not found. Cannot update."
                )
                return

            # 2. อัพเดท UI ของ Toggle Switch
            # ตรวจสอบว่ามี container และฟังก์ชันอัพเดทหรือไม่
            # ใช้ getattr เพื่อป้องกัน AttributeError ถ้า self.click_translate_switch_container ยังไม่ได้ถูกสร้าง
            toggle_container = getattr(self, "click_translate_switch_container", None)

            if toggle_container and toggle_container.winfo_exists():
                if hasattr(toggle_container, "update_ui_func"):
                    logging.debug(
                        f"ControlUI: Explicitly calling update_ui_func for Click Translate toggle UI ({is_enabled})"
                    )
                    toggle_container.update_ui_func(is_enabled)
                else:
                    logging.error(
                        "ControlUI: update_ui_func not found on click_translate_switch_container!"
                    )
            elif (
                toggle_container is not None
            ):  # Attribute exists, but widget doesn't (likely destroyed)
                logging.warning(
                    "ControlUI: click_translate_switch_container widget destroyed or not available for UI update."
                )
            # else: # The attribute self.click_translate_switch_container itself doesn't exist yet.
            # This might happen if update_display is called before setup_buttons fully completes.
            # It's less of an error and more of a timing issue if it resolves later.
            # logging.debug("ControlUI: click_translate_switch_container attribute does not exist yet.")

            # 3. อัพเดท UI ปุ่ม Force ด้วย (ถ้าค่า BooleanVar มีการเปลี่ยนแปลง)
            if var_updated:
                self._update_force_button_ui(is_enabled)

        except Exception as e:
            logging.error(f"Error updating Click Translate toggle: {e}", exc_info=True)

    def update_hover_translate_toggle(self, is_enabled):
        """อัพเดทสถานะและ UI ของ Hover Translate Toggle Switch"""
        try:
            logging.info(
                f"ControlUI: update_hover_translate_toggle called with {is_enabled}"
            )

            # 1. อัพเดท BooleanVar
            if hasattr(self, "hover_translation_var"):
                if self.hover_translation_var.get() != is_enabled:
                    self.hover_translation_var.set(is_enabled)
            else:
                logging.warning("ControlUI: hover_translation_var not found.")
                return

            # *** แก้ไข NameError: กำหนดค่าให้ตัวแปร container ***
            container = None
            if hasattr(self, "hover_translate_switch_container"):
                container = self.hover_translate_switch_container
                logging.debug(
                    f"ControlUI: Found hover_translate_switch_container: {container}"
                )
            else:
                logging.warning(
                    "ControlUI: hover_translate_switch_container not found yet"
                )
                # ถ้ายังไม่มี container ให้ retry หลัง 100ms
                if hasattr(self, "root") and self.root.winfo_exists():
                    self.root.after(
                        100, lambda: self.update_hover_translate_toggle(is_enabled)
                    )
                return

            # 2. อัพเดท UI ของ Toggle Switch
            if container and container.winfo_exists():
                if hasattr(container, "update_ui_func"):
                    container.update_ui_func(is_enabled)
                    logging.info(
                        f"ControlUI: Successfully updated hover toggle UI to {is_enabled}"
                    )
                else:
                    logging.warning(
                        "ControlUI: update_ui_func not found on hover_translate_switch_container."
                    )
            elif hasattr(self, "hover_translate_switch_container"):
                logging.warning(
                    "ControlUI: hover_translate_switch_container found but widget destroyed or not available."
                )

        except Exception as e:
            logging.error(f"Error updating Hover Translate toggle: {e}", exc_info=True)

    def update_button_highlights(self):
        """Update button colors, handle role locking, and update save button state."""
        button_map = {
            "A": getattr(self, "button_a", None),
            "B": getattr(self, "button_b", None),
            "C": getattr(self, "button_c", None),
        }

        try:
            # ดึงสีและ Role ปัจจุบัน
            current_preset_role = self.settings.get_preset_role(self.current_preset)
            # แก้ไขเงื่อนไขตรงนี้: ให้ preset 4 และ 5 เป็น custom เสมอ
            is_custom_preset = (
                current_preset_role == "custom" or self.current_preset >= 4
            )

            active_bg = self.theme.get("accent", "#6c5ce7")
            active_fg = self.theme.get("text", "#ffffff")
            inactive_bg = self.theme.get("button_bg", "#262637")
            inactive_fg = self.theme.get("text_dim", "#b2b2b2")
            disabled_bg = "#303030"  # สีสำหรับปุ่ม Area ที่ถูกล็อค
            disabled_fg = "#606060"
            theme_text_color = self.theme.get(
                "text", "#ffffff"
            )  # สีข้อความทั่วไปสำหรับปุ่ม Save

            # --- อัพเดตสถานะปุ่ม Area A, B, C และการล็อค ---
            for area, button in button_map.items():
                if button and button.winfo_exists():
                    is_active = self.area_states.get(area, False)
                    button.selected = is_active

                    # ตรวจสอบว่าพื้นที่นี้ถูกจำกัดสำหรับ preset ปัจจุบันหรือไม่
                    is_area_restricted = False
                    if self.current_preset < 4:  # preset 1-3 มีการจำกัด
                        if self.current_preset == 1:  # Dialog: อนุญาต A,B เท่านั้น
                            is_area_restricted = area == "C"
                        elif self.current_preset == 2:  # Lore: อนุญาต C เท่านั้น
                            is_area_restricted = area in ["A", "B"]
                        elif self.current_preset == 3:  # Choice: อนุญาต A+B (A=mockup)
                            is_area_restricted = area == "C"

                    # ล็อคปุ่มถ้าพื้นที่ถูกจำกัด
                    if is_area_restricted:
                        button.configure(
                            bg=disabled_bg,
                            fg=disabled_fg,
                            relief="flat",
                            state=tk.DISABLED,
                            cursor="",
                        )
                    else:
                        # ปลดล็อคปุ่มถ้าพื้นที่ไม่ถูกจำกัด
                        button.configure(state=tk.NORMAL, cursor="hand2")
                        if is_active:
                            button.configure(
                                bg=active_bg, fg=active_fg, relief="sunken"
                            )
                        else:
                            button.configure(
                                bg=inactive_bg, fg=inactive_fg, relief="flat"
                            )

            # --- อัพเดตสถานะปุ่ม "เลือกพื้นที่" A, B, C ---
            define_area_buttons = {
                "A": getattr(self, "define_area_a_button_ctrl", None),
                "B": getattr(self, "define_area_b_button_ctrl", None),
                "C": getattr(self, "define_area_c_button_ctrl", None),
            }

            for area, define_button in define_area_buttons.items():
                if define_button and define_button.winfo_exists():
                    # ตรวจสอบว่าพื้นที่นี้ถูกจำกัดสำหรับ preset ปัจจุบันหรือไม่
                    is_area_restricted = False
                    if self.current_preset < 4:  # preset 1-3 มีการจำกัด
                        if self.current_preset == 1:  # Dialog: อนุญาต A,B เท่านั้น
                            is_area_restricted = area == "C"
                        elif self.current_preset == 2:  # Lore: อนุญาต C เท่านั้น
                            is_area_restricted = area in ["A", "B"]
                        elif self.current_preset == 3:  # Choice: อนุญาต A+B (A=mockup)
                            is_area_restricted = area == "C"

                    # ล็อคปุ่มถ้าพื้นที่ถูกจำกัด
                    if is_area_restricted:
                        define_button.configure(
                            bg=disabled_bg,
                            fg=disabled_fg,
                            relief="flat",
                            state=tk.DISABLED,
                            cursor="",
                        )
                    else:
                        # ปลดล็อคปุ่มถ้าพื้นที่ไม่ถูกจำกัด
                        define_button.configure(
                            bg=inactive_bg,
                            fg=inactive_fg,
                            relief="flat",
                            state=tk.NORMAL,
                            cursor="hand2",
                        )

            # --- ตรวจสอบสถานะ unsaved changes ---
            # *** เพิ่มการตรวจสอบว่า attribute มีอยู่หรือไม่ ***
            if not hasattr(self, "has_unsaved_changes"):
                self.has_unsaved_changes = False
                logging.debug(
                    "Initialized has_unsaved_changes in update_button_highlights"
                )

            # สำคัญ: ถ้า self.has_unsaved_changes เป็น True อยู่แล้ว
            # ให้ข้ามการตรวจสอบและใช้ค่านั้นเลย
            if not self.has_unsaved_changes:
                # 1. เปรียบเทียบ Area String ปัจจุบันกับใน Preset
                active_areas_list = self.get_active_areas()
                current_area_str = (
                    "+".join(sorted(active_areas_list)) if active_areas_list else ""
                )

                preset_data = self.settings.get_preset(self.current_preset)
                preset_areas_list = []
                if preset_data and isinstance(preset_data.get("areas"), str):
                    preset_areas_list = sorted(preset_data["areas"].split("+"))
                preset_areas_str = (
                    "+".join(preset_areas_list) if preset_areas_list else ""
                )

                # ตรวจสอบเพิ่มเติม: ถ้าทั้งคู่ว่าง ให้ถือว่าไม่มีการเปลี่ยนแปลง
                if not current_area_str and not preset_areas_str:
                    areas_changed = False
                else:
                    areas_changed = current_area_str != preset_areas_str

                if areas_changed:
                    logging.debug(
                        f"Unsaved change detected: Area string mismatch ('{current_area_str}' vs '{preset_areas_str}')"
                    )

                # 2. เปรียบเทียบ Coordinates ปัจจุบันกับใน Preset
                coords_changed = self.check_coordinate_changes()

                # 3. กำหนดค่า has_unsaved_changes
                self.has_unsaved_changes = areas_changed or coords_changed

                if areas_changed:
                    logging.debug(
                        f"Unsaved change detected: Area string mismatch ('{current_area_str}' vs '{preset_areas_str}')"
                    )
                if coords_changed:
                    logging.debug(
                        f"Unsaved change detected: Coordinate mismatch found by check_coordinate_changes()"
                    )
            else:
                # หากมีการตั้งค่า has_unsaved_changes = True จากภายนอก
                # บันทึกล็อกด้วย
                logging.debug("has_unsaved_changes was already set to True externally")

            # --- อัพเดทปุ่ม Save ---
            if hasattr(self, "save_button") and self.save_button.winfo_exists():
                # เปิด/ปิด และเปลี่ยนสีปุ่ม Save ตามค่า has_unsaved_changes เท่านั้น
                if self.has_unsaved_changes:
                    # มีการเปลี่ยนแปลง: ใช้สี Error และ เปิดใช้งาน
                    self.save_button.configure(
                        bg=self.theme.get("error", "#e74c3c"),
                        fg=theme_text_color,
                        relief="raised",
                        bd=1,
                        state=tk.NORMAL,
                        cursor="hand2",
                    )
                else:
                    # ไม่มีการเปลี่ยนแปลง: ใช้สีปกติ และ ปิดใช้งาน
                    self.save_button.configure(
                        bg=inactive_bg,
                        fg=theme_text_color,
                        relief="flat",
                        bd=0,
                        state=tk.DISABLED,
                        cursor="",
                    )

            logging.debug(
                f"Updated highlights. Role: '{current_preset_role}'. Has unsaved changes: {self.has_unsaved_changes}. Preset: {self.current_preset}."
            )

        except Exception as e:
            logging.error(f"Error in update_button_highlights: {e}")
            import traceback

            traceback.print_exc()

    def get_active_areas(self):
        """Return list of active areas in correct order"""
        return [area for area in ["A", "B", "C"] if self.area_states[area]]

    def check_coordinate_changes(self):
        """ตรวจสอบว่ามีการเปลี่ยนแปลงพิกัดหรือไม่ โดยเปรียบเทียบกับที่บันทึกใน preset"""
        try:
            # ดึงข้อมูล preset ปัจจุบัน
            preset_data = self.settings.get_preset(self.current_preset)
            if not preset_data:
                logging.debug(
                    f"Preset {self.current_preset} data not found for change check."
                )
                return False  # ไม่มีข้อมูล preset ให้เปรียบเทียบ

            # ดึงข้อมูล role เพื่อใช้ในการตรวจสอบ
            current_preset_role = self.settings.get_preset_role(self.current_preset)
            is_custom_preset = (
                current_preset_role == "custom" or self.current_preset >= 4
            )

            # [1] ถ้าเป็น system preset (1-3) ให้ตรวจสอบเฉพาะพิกัดที่เปลี่ยนไป ไม่สนใจ area ที่ต่างกัน
            if not is_custom_preset:
                # ตรวจสอบเฉพาะพิกัดที่เปลี่ยนไปสำหรับพื้นที่ที่กำหนดไว้แล้วใน preset
                preset_coordinates = preset_data.get("coordinates", {})
                preset_areas = preset_data.get("areas", "").split("+")

                # เพิ่มล็อกการตรวจสอบ
                logging.debug(
                    f"Checking system preset {self.current_preset} ({preset_areas}) for coordinate changes"
                )

                for area in preset_areas:
                    current_area_coords = self.settings.get_translate_area(area)
                    preset_area_coords = preset_coordinates.get(area)

                    if current_area_coords and preset_area_coords:
                        # ตรวจสอบพิกัดทุกค่า เปรียบเทียบทีละตัว
                        if (
                            current_area_coords.get("start_x")
                            != preset_area_coords.get("start_x")
                            or current_area_coords.get("start_y")
                            != preset_area_coords.get("start_y")
                            or current_area_coords.get("end_x")
                            != preset_area_coords.get("end_x")
                            or current_area_coords.get("end_y")
                            != preset_area_coords.get("end_y")
                        ):
                            # พบความแตกต่างของพิกัด - ต้องบันทึก
                            logging.debug(
                                f"Coordinate change detected in system preset area {area}: Current={current_area_coords}, Preset={preset_area_coords}"
                            )
                            return True  # พบการเปลี่ยนแปลงพิกัด
                    elif bool(current_area_coords) != bool(preset_area_coords):
                        # กรณีพิกัดหายไปหรือเพิ่มเข้ามา
                        logging.debug(
                            f"Coordinate presence mismatch in system preset for area {area}"
                        )
                        return True

                # สำหรับ System preset ไม่ตรวจสอบการเปลี่ยน active areas
                logging.debug(
                    f"No coordinate changes detected in system preset {self.current_preset}"
                )
                return False

            # [2] สำหรับ custom preset (4-6) คงเดิม
            else:
                # ตรวจสอบว่า active areas เปลี่ยนไปจาก preset หรือไม่
                active_areas = self.get_active_areas()
                preset_areas = preset_data.get("areas", "").split("+")

                # ตรวจสอบว่า active areas ต่างจาก preset areas หรือไม่
                active_areas_sorted = sorted(active_areas)
                preset_areas_sorted = sorted(preset_areas)

                if active_areas_sorted != preset_areas_sorted:
                    logging.debug(
                        f"Area selection changed: {active_areas_sorted} vs {preset_areas_sorted}"
                    )
                    return True

                # ตรวจสอบการเปลี่ยนแปลงพิกัด
                preset_coordinates = preset_data.get("coordinates", {})
                for area in active_areas:
                    current_area_coords = self.settings.get_translate_area(area)
                    preset_area_coords = preset_coordinates.get(area)

                    if current_area_coords and preset_area_coords:
                        if (
                            current_area_coords.get("start_x")
                            != preset_area_coords.get("start_x")
                            or current_area_coords.get("start_y")
                            != preset_area_coords.get("start_y")
                            or current_area_coords.get("end_x")
                            != preset_area_coords.get("end_x")
                            or current_area_coords.get("end_y")
                            != preset_area_coords.get("end_y")
                        ):
                            logging.debug(
                                f"Coordinate change detected in custom preset area {area}"
                            )
                            return True
                    elif bool(current_area_coords) != bool(preset_area_coords):
                        logging.debug(f"Coordinate presence mismatch for area {area}")
                        return True

                return False

        except Exception as e:
            logging.error(f"Error in check_coordinate_changes: {e}")
            import traceback

            traceback.print_exc()
            return False  # คืน False ถ้าเกิดข้อผิดพลาด

    def setup_bindings(self):
        """Setup window movement bindings"""
        self.root.bind("<Button-1>", self.start_move)
        self.root.bind("<ButtonRelease-1>", self.stop_move)
        self.root.bind("<B1-Motion>", self.on_drag)

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.x = None
        self.y = None

    def on_drag(self, event):
        """จัดการการลากหน้าต่าง"""
        if self.x is not None and self.y is not None:
            deltax = event.x - self.x
            deltay = event.y - self.y
            x = self.root.winfo_x() + deltax
            y = self.root.winfo_y() + deltay
            self.root.geometry(f"+{x}+{y}")

            self.ui_cache["position_x"] = x
            self.ui_cache["position_y"] = y

    def area_button_click(self, area):
        """Toggle area on/off and update UI, then notify MBB.py
        Args:
            area (str): พื้นที่ที่ถูกคลิก (A, B, หรือ C)
        """
        # --- เพิ่มการตรวจสอบ Role สำหรับ preset 1-3 ---
        current_preset_role = self.settings.get_preset_role(self.current_preset)

        # ตรวจสอบการจำกัดพื้นที่สำหรับ preset 1-3
        if self.current_preset < 4:
            # preset Dialog(1): อนุญาต A และ B เท่านั้น, ปิด C
            if self.current_preset == 1 and area == "C":
                logging.info(
                    f"Area '{area}' not allowed for Preset {self.current_preset} (Dialog)"
                )
                return

            # preset lore(2): อนุญาต C เท่านั้น
            elif self.current_preset == 2 and area in ["A", "B"]:
                logging.info(
                    f"Area '{area}' not allowed for Preset {self.current_preset} (Lore)"
                )
                return

            # preset choice(3): อนุญาต A+B (A=mockup), ปิด C เท่านั้น
            elif self.current_preset == 3 and area == "C":
                logging.info(
                    f"Area '{area}' not allowed for Preset {self.current_preset} (Choice)"
                )
                return
        # --- จบการตรวจสอบ Role ---

        try:
            # สลับสถานะของพื้นที่ที่คลิก
            new_state = not self.area_states[area]

            # ตรวจสอบว่าจะมีอย่างน้อย 1 พื้นที่เปิดอยู่เสมอ
            other_active_areas = any(
                self.area_states[a] for a in ["A", "B", "C"] if a != area
            )

            # อนุญาตให้ปิดได้ถ้ายังมีพื้นที่อื่นเปิดอยู่ หรือถ้ากำลังจะเปิดพื้นที่นี้
            if new_state or other_active_areas:
                # 1. อัพเดท State ภายใน Control_UI
                self.area_states[area] = new_state

                # 2. อัพเดท UI ของ Control_UI ทันที (จะมีการตั้ง has_unsaved_changes ข้างใน)
                self.update_button_highlights()

                # 3. รวบรวมพื้นที่ที่เปิดใช้งาน *หลังจาก* อัพเดท state แล้ว
                active_areas = self.get_active_areas()  # ได้เป็น list เช่น ['A', 'B']

                # 4. แจ้งการเปลี่ยนแปลงพื้นที่ไปยัง MBB.py ผ่าน Callback
                if active_areas and self.switch_area_callback:
                    # ส่งพารามิเตอร์ preset_number_override ด้วยเพื่อป้องกันการสลับไป preset เริ่มต้น
                    self.switch_area_callback(
                        active_areas, preset_number_override=self.current_preset
                    )
                    # 5. กระตุ้นให้ MBB.py ทำการแปลใหม่ (ถ้า callback มีอยู่)
                    if self.force_translate:
                        self.force_translate()

                logging.info(
                    f"Area {area} toggled. Control UI state updated. Active areas requested: {self.get_active_areas()}"
                )
            else:
                # กรณีพยายามปิดปุ่มสุดท้าย ไม่ทำอะไร
                logging.warning(f"Cannot deactivate the last active area ({area}).")

        except Exception as e:
            logging.error(f"Error in area_button_click: {e}")
            import traceback

            traceback.print_exc()

    def capture_screen(self):
        """Capture screen function"""
        try:
            from screen_capture import ScreenCapture

            capturer = ScreenCapture()
            filepath = capturer.capture_primary_screen()
            if filepath:
                self.show_capture_feedback()
        except Exception as e:
            logging.error(f"Screen capture error: {e}")

    def show_capture_feedback(self):
        """Show capture feedback"""
        feedback = tk.Toplevel(self.root)
        feedback.overrideredirect(True)
        feedback.configure(bg="black")
        x = self.root.winfo_x() + self.camera_button.winfo_x()
        y = self.root.winfo_y() + self.camera_button.winfo_y()
        tk.Label(
            feedback,
            text="Captured!",
            fg="lime",
            bg="black",
            font=("FC Minimal Medium", 10),
        ).pack(padx=10, pady=5)
        feedback.geometry(f"+{x+30}+{y}")
        feedback.after(1000, feedback.destroy)

    def _sync_current_preset_with_translate_areas(self):
        """บังคับให้ preset ที่กำลังใช้อยู่มีพิกัดที่ถูกต้องจาก translate_areas"""
        try:
            preset_data = self.settings.get_preset(self.current_preset)
            if preset_data:
                area_config = preset_data.get("areas", "A")
                coordinates = preset_data.get("coordinates", {})

                # แยกพื้นที่ที่ active ก่อน
                active_areas = area_config.split("+")

                # อัพเดท area_states ภายใน Control UI
                for area in ["A", "B", "C"]:
                    self.area_states[area] = area in active_areas

                # 1. ดึงพิกัดจาก preset เพื่อตั้งค่าใน translate_areas
                if isinstance(coordinates, dict):
                    for area in active_areas:
                        coords = coordinates.get(area)
                        if isinstance(coords, dict) and all(
                            k in coords
                            for k in ["start_x", "start_y", "end_x", "end_y"]
                        ):
                            # *** สร้างสำเนาพิกัดก่อนบันทึกลง settings ***
                            new_coords = {
                                "start_x": coords["start_x"],
                                "start_y": coords["start_y"],
                                "end_x": coords["end_x"],
                                "end_y": coords["end_y"],
                            }
                            # อัพเดทพิกัดใน Settings หลัก
                            self.settings.set_translate_area(
                                new_coords["start_x"],
                                new_coords["start_y"],
                                new_coords["end_x"],
                                new_coords["end_y"],
                                area,
                            )
                            logging.info(
                                f"Synced coordinates for area {area} from preset {self.current_preset}: {new_coords}"
                            )
                        else:
                            logging.warning(
                                f"Invalid coordinates data for area {area} in preset {self.current_preset}"
                            )

                # อัพเดท UI ทั้งหมด
                self.update_preset_buttons()
                self.update_button_highlights()

                # แจ้ง callback เพื่อให้ MBB.py อัพเดตการแสดงผล (ถ้ามี)
                if self.switch_area_callback:
                    self.switch_area_callback(
                        active_areas, preset_number_override=self.current_preset
                    )

                logging.info(
                    f"Preset {self.current_preset} synced with translate areas. Active areas: {active_areas}"
                )
            else:
                logging.warning(
                    f"Cannot sync: preset {self.current_preset} data not found"
                )
        except Exception as e:
            logging.error(f"Error syncing current preset with translate areas: {e}")
            import traceback

            traceback.print_exc()

    # +++ NEW METHOD +++
    def is_active(self):
        """
        ตรวจสอบว่า Control UI ยังทำงานอยู่หรือไม่
        """
        return (
            hasattr(self, "root")
            and self.root
            and hasattr(self.root, "winfo_exists")
            and self.root.winfo_exists()
        )

    def dummy_force(self):
        """ฟังก์ชันจำลองสำหรับการทดสอบ force translate"""
        print("Force translate triggered")

    def dummy_switch(self, area, preset_number_override=None, source=None):
        """ฟังก์ชันจำลองสำหรับการทดสอบการสลับพื้นที่

        Args:
            area: รหัสพื้นที่ที่ต้องการสลับ
            preset_number_override: เลข preset ที่ต้องการให้ใช้แทนค่าปัจจุบัน (optional)
            source: แหล่งที่มาของคำสั่งเปลี่ยนพื้นที่ (optional)
        """
        print(
            f"Switch area: {area}, Preset override: {preset_number_override}, Source: {source}"
        )

    # ฟังก์ชันเกี่ยวกับ Area ที่ย้ายมาจาก MBB.py
    def start_selection_a(self):
        """เริ่มการเลือกพื้นที่ A สำหรับชื่อผู้พูด"""
        # ตรวจสอบการจำกัดพื้นที่สำหรับ preset 1-3
        if self.current_preset < 4:
            # preset lore(2): ไม่อนุญาต A
            if self.current_preset == 2:
                logging.info(
                    f"Area selection 'A' not allowed for Preset {self.current_preset} (Lore)"
                )
                return

        self.start_selection("A")

    def start_selection_b(self):
        """เริ่มการเลือกพื้นที่ B สำหรับบทสนทนาหลัก"""
        # ตรวจสอบการจำกัดพื้นที่สำหรับ preset 1-3
        if self.current_preset < 4:
            # preset lore(2): ไม่อนุญาต B
            if self.current_preset == 2:
                logging.info(
                    f"Area selection 'B' not allowed for Preset {self.current_preset} (Lore)"
                )
                return

        self.start_selection("B")

    def start_selection_c(self):
        """เริ่มการเลือกพื้นที่ C สำหรับข้อความเสริม"""
        # ตรวจสอบการจำกัดพื้นที่สำหรับ preset 1-3
        if self.current_preset < 4:
            # preset Dialog(1) และ choice(3): ไม่อนุญาต C
            if self.current_preset in [1, 3]:
                logging.info(
                    f"Area selection 'C' not allowed for Preset {self.current_preset}"
                )
                return

        self.start_selection("C")

    def start_selection(self, area):
        """เริ่มการเลือกพื้นที่แปลใหม่
        Args:
            area (str): พื้นที่ที่ต้องการเลือก ('A', 'B', หรือ 'C')
        """
        # เก็บสถานะการแสดงพื้นที่เดิมไว้
        was_showing_area = self.is_area_shown

        # ซ่อนหน้าต่างแสดงพื้นที่เดิม (ถ้ามี) เพื่อไม่ให้ซ้ำซ้อน
        self.hide_show_area()
        self.root.withdraw()

        # สร้างหน้าต่างสำหรับเลือกพื้นที่
        self.top = tk.Toplevel(self.root)
        screen_size = self.settings.get("screen_size", "2560x1440")
        self.top.geometry(
            f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0"
        )
        self.top.attributes("-topmost", True)
        self.top.attributes("-alpha", 0.3)
        self.top.overrideredirect(True)
        self.top.lift()
        self.top.focus_force()

        # สร้าง Canvas สำหรับวาดพื้นที่เลือก
        self.selection_canvas = tk.Canvas(
            self.top, bg="white", cursor="crosshair", highlightthickness=0
        )
        self.selection_canvas.pack(fill=tk.BOTH, expand=True)

        # แสดงข้อความแนะนำ
        instruction_text = ""
        if area == "A":
            instruction_text = "เลือกพื้นที่ A สำหรับชื่อผู้พูด (ลากเมาส์)"
        elif area == "B":
            instruction_text = "เลือกพื้นที่ B สำหรับข้อความสนทนา (ลากเมาส์)"
        elif area == "C":
            instruction_text = "เลือกพื้นที่ C สำหรับข้อความเสริม (ลากเมาส์)"

        self.instruction_label = tk.Label(
            self.top,
            text=instruction_text,
            fg="black",
            bg="white",
            font=("FC Minimal Medium", 39),  # เพิ่มขนาดฟอนต์ 30% (30->39)
        )
        self.instruction_label.place(relx=0.5, rely=0.5, anchor="center")

        # ตัวแปรสำหรับเก็บจุดเริ่มต้นและสิ้นสุดการลาก
        self.start_x = None
        self.start_y = None
        self.selection_rect = None

        # Bind events
        self.selection_canvas.bind(
            "<ButtonPress-1>", lambda e: self.start_drag(e, area)
        )
        self.selection_canvas.bind("<B1-Motion>", self.update_selection)
        self.selection_canvas.bind(
            "<ButtonRelease-1>", lambda e: self.finish_selection(e, area)
        )
        self.top.bind("<Escape>", lambda e: self.cancel_selection())

    def start_drag(self, event, area):
        """เริ่มลากเพื่อเลือกพื้นที่
        Args:
            event: tkinter event object
            area: พื้นที่ที่กำลังเลือก ('A', 'B', หรือ 'C')
        """
        self.start_x = event.x
        self.start_y = event.y
        if self.selection_rect:
            self.selection_canvas.delete(self.selection_rect)
        self.instruction_label.place_forget()

    def update_selection(self, event):
        """อัพเดทพื้นที่ที่กำลังเลือกขณะลากเมาส์
        Args:
            event: tkinter event object
        """
        if self.selection_rect:
            self.selection_canvas.delete(self.selection_rect)
        self.selection_rect = self.selection_canvas.create_rectangle(
            self.start_x,
            self.start_y,
            event.x,
            event.y,
            outline="red",
            fill="red",
            stipple="gray50",
        )

    def finish_selection(self, event, area):
        """
        จัดการการเลือกพื้นที่เสร็จสิ้น, บันทึกพิกัด, และอัพเดท State ส่วนกลาง
        Args:
            event: tkinter event object
            area: พื้นที่ที่กำลังเลือก ('A', 'B', หรือ 'C')
        """
        if self.start_x is not None and self.start_y is not None:
            try:
                # คำนวณค่าพิกัดและปรับ scale
                scale_x, scale_y = self.get_screen_scale()
                # ใช้ min/max เพื่อให้แน่ใจว่า start < end เสมอ
                raw_x1 = min(self.start_x, event.x)
                raw_y1 = min(self.start_y, event.y)
                raw_x2 = max(self.start_x, event.x)
                raw_y2 = max(self.start_y, event.y)

                # แปลงกลับเป็นพิกัดอ้างอิง (ไม่ scale) เพื่อบันทึก
                x1 = raw_x1 / scale_x
                y1 = raw_y1 / scale_y
                x2 = raw_x2 / scale_x
                y2 = raw_y2 / scale_y

                # ตรวจสอบขนาดพื้นที่ขั้นต่ำ
                min_width_pixels = 10
                min_height_pixels = 10
                if (raw_x2 - raw_x1) < min_width_pixels or (
                    raw_y2 - raw_y1
                ) < min_height_pixels:
                    messagebox.showwarning(
                        "พื้นที่เล็กเกินไป",
                        f"กรุณาเลือกพื้นที่ขนาดอย่างน้อย {min_width_pixels}x{min_height_pixels} พิกเซล",
                    )
                else:
                    # บันทึกค่าพิกัดลงใน settings
                    self.settings.set_translate_area(x1, y1, x2, y2, area)

                    # อัพเดทสถานะปุ่ม
                    self.area_states[area] = True

                    # อัพเดท UI ทันที
                    self.update_button_highlights()

                    # แจ้งเตือนว่ามีการเปลี่ยนแปลงที่ยังไม่ได้บันทึก
                    self.has_unsaved_changes = True

                    # อัพเดทหน้าจอ
                    new_areas = self.get_current_area_string()
                    self.ui_cache["current_area"] = new_areas

                    # แสดงพื้นที่ให้ดูชั่วคราว (ถ้ามี callback)
                    if self.trigger_temporary_area_display_callback:
                        self.trigger_temporary_area_display_callback(new_areas)

                    def close_and_maybe_show_area():
                        if self.top and self.top.winfo_exists():
                            self.top.destroy()
                            self.top = None
                        self.root.deiconify()

                    # หน่วงเวลาเล็กน้อยก่อนปิดหน้าต่างเลือกพื้นที่
                    self.root.after(100, close_and_maybe_show_area)
                    return

            except Exception as e:
                logging.error(f"Error in finish_selection: {e}")
                messagebox.showerror("Error", f"เกิดข้อผิดพลาด: {e}")

        # กรณีไม่มีการเลือกพื้นที่ หรือเกิดข้อผิดพลาด
        self.close_selection()

    def close_selection(self):
        """ปิดหน้าต่างเลือกพื้นที่"""
        if self.top and self.top.winfo_exists():
            self.top.destroy()
            self.top = None
        self.root.deiconify()

    def get_screen_scale(self):
        """คำนวณอัตราส่วนขนาดหน้าจอเทียบกับการตั้งค่า
        Returns:
            tuple: (scale_x, scale_y)
        """
        # ขอขนาดหน้าจอจริง
        actual_width = self.root.winfo_screenwidth()
        actual_height = self.root.winfo_screenheight()

        # ดึงค่าขนาดหน้าจอจากการตั้งค่า
        screen_size = self.settings.get(
            "screen_size", f"{actual_width}x{actual_height}"
        )
        try:
            set_width, set_height = map(int, screen_size.split("x"))
        except:
            set_width, set_height = actual_width, actual_height

        return actual_width / set_width, actual_height / set_height

    def scale_coordinates(self, x, y):
        """ปรับขนาดพิกัดตาม scale
        Args:
            x, y: พิกัดที่ต้องการปรับ scale
        Returns:
            tuple: (scaled_x, scaled_y)
        """
        scale_x, scale_y = self.get_screen_scale()
        return x * scale_x, y * scale_y

    def cancel_selection(self):
        """ยกเลิกการเลือกพื้นที่"""
        self.close_selection()

    def hide_show_area(self):
        """ซ่อนหน้าต่างแสดงพื้นที่ (ถ้ามี)"""
        if hasattr(self, "is_area_shown") and self.is_area_shown:
            # ถ้ามีการแสดงพื้นที่อยู่ ให้ซ่อนก่อน
            self.is_area_shown = False

    def switch_area(self, areas, preset_number_override=None, source="unknown"):
        """
        สลับพื้นที่การแสดงผล

        Args:
            areas (str): รหัสพื้นที่ เช่น "A", "B", "A+B"
            preset_number_override (int, optional): หมายเลข preset ที่ต้องการใช้แทน
            source (str, optional): แหล่งที่มาของคำสั่งเปลี่ยนพื้นที่ (optional)

        Returns:
            bool: True ถ้าสำเร็จ
        """
        try:
            logging.info(f"Control_UI switch_area called: {areas} (source: {source})")

            # แยกรหัสพื้นที่
            area_codes = areas.split("+")

            # ตรวจสอบความถูกต้องของรหัสพื้นที่
            for code in area_codes:
                if code not in ["A", "B", "C"]:
                    logging.warning(f"Invalid area code: {code}")
                    return False

            # อัพเดทสถานะพื้นที่
            self.area_states = {
                "A": "A" in area_codes,
                "B": "B" in area_codes,
                "C": "C" in area_codes,
            }

            # อัพเดท UI
            self.update_area_button_highlights(areas)
            self.update_button_highlights()

            # บันทึกค่าล่าสุดใน cache
            self.ui_cache["current_area"] = areas

            # ใช้ preset อื่นถ้ามีการระบุ
            if preset_number_override is not None:
                self.sync_last_used_preset(preset_number_override, source=source)

            # เรียกใช้ callback ถ้ามี (อาจทำให้ MBB.switch_area ถูกเรียกซ้ำ แต่มีการป้องกันไว้แล้ว)
            if self.switch_area_callback:
                self.switch_area_callback(areas, preset_number_override, source)

            return True
        except Exception as e:
            logging.error(f"Error in Control_UI switch_area: {e}")
            return False

    def sync_last_used_preset(
        self, preset_num, source="unknown", area_config_override=None, update_ui=True
    ):
        """
        อัพเดทข้อมูล preset ล่าสุดที่ใช้ ทั้งใน internal state, settings และ UI

        Args:
            preset_num (int): หมายเลข preset
            source (str): แหล่งที่มา (control_ui, auto, hover, etc)
            area_config_override (str, optional): พื้นที่ที่ต้องการใช้แทนที่พื้นที่ปกติของ preset
            update_ui (bool): ต้องการอัพเดท UI หรือไม่
        """
        try:
            if not isinstance(preset_num, int) or preset_num < 1 or preset_num > 6:
                logging.warning(f"Invalid preset number: {preset_num}, must be 1-6")
                return

            # อัพเดท internal state
            self.current_preset = preset_num

            # บันทึกลงใน settings
            self.settings.set("active_preset", preset_num)
            self.settings.set("current_preset", preset_num)

            # ดึงค่าพื้นที่จาก preset นี้
            preset_data = self.settings.get_preset(preset_num)

            # ใช้ค่า override ถ้ามี
            area_to_use = area_config_override or preset_data.get("areas", "A+B")

            # อัพเดท UI
            if update_ui:
                self.update_control_ui_preset_active(preset_num)

                # อัพเดทไฮไลต์ปุ่ม area
                self.update_highlight_on_preset_change(area_to_use)

                # อัพเดตข้อมูลที่แสดงใน UI
                self.update_display(area_to_use, preset_num)

            logging.info(f"Synced last used preset: {preset_num} (source: {source})")
        except Exception as e:
            logging.error(f"Error syncing last used preset: {e}")

    def switch_area_directly(self, dialogue_type):
        """สลับพื้นที่โดยตรงตามประเภทข้อความ (ใช้เมื่อต้องการสลับอัตโนมัติ)

        Args:
            dialogue_type: ประเภทข้อความ ("normal", "name_only", "message_only", "choice", ฯลฯ)

        Returns:
            bool: True ถ้ามีการสลับพื้นที่ False ถ้าไม่มีการสลับพื้นที่
        """
        try:
            current_areas = self.get_current_area_string().split("+")
            current_areas_set = set(current_areas)

            # กำหนดพื้นที่ที่เหมาะสมสำหรับแต่ละประเภทข้อความ
            if dialogue_type == "normal":
                # บทสนทนาปกติ (มีทั้งชื่อและข้อความ) - ใช้พื้นที่ A+B
                target_areas = ["A", "B"]
            elif dialogue_type == "name_only":
                # แสดงเฉพาะชื่อผู้พูด - ใช้พื้นที่ A
                target_areas = ["A"]
            elif dialogue_type == "message_only":
                # แสดงเฉพาะข้อความ - ใช้พื้นที่ B
                target_areas = ["B"]
            elif dialogue_type == "choice":
                # ตัวเลือก - ใช้พื้นที่ B
                target_areas = ["B"]
            else:
                # ประเภทข้อความที่ไม่รู้จัก - คงพื้นที่เดิม
                logging.warning(
                    f"Unknown dialogue type: {dialogue_type}, keeping current areas"
                )
                return False

            # ตรวจสอบความจำเป็นในการสลับพื้นที่
            target_areas_set = set(target_areas)
            if current_areas_set == target_areas_set:
                # พื้นที่ปัจจุบันเหมาะสมกับประเภทข้อความอยู่แล้ว
                return False

            # สลับพื้นที่
            new_area_str = "+".join(target_areas)
            self.switch_area(new_area_str, source="auto")
            logging.info(
                f"Auto switched from {'+'.join(current_areas)} to {new_area_str}"
            )
            return True
        except Exception as e:
            logging.error(f"Error in switch_area_directly: {e}")
            return False

    def update_area_button_highlights(self, areas):
        """อัพเดทไฮไลต์ปุ่ม A, B, C ตามพื้นที่ที่ระบุ
        Args:
            areas (str): Area string เช่น "A", "B", "A+B"
        """
        try:
            # แยกรหัสพื้นที่
            area_codes = areas.split("+")

            # อัพเดทสถานะพื้นที่
            self.area_states = {
                "A": "A" in area_codes,
                "B": "B" in area_codes,
                "C": "C" in area_codes,
            }

            # บันทึกค่าล่าสุดใน cache
            self.ui_cache["current_area"] = areas
        except Exception as e:
            logging.error(f"Error updating area button highlights: {e}")

    def is_show_area_active(self):
        """ตรวจสอบว่ามีการเปิด show area ค้างไว้หรือไม่"""
        return hasattr(self, "is_area_shown") and self.is_area_shown

    def update_highlight_on_preset_change(self, areas):
        """
        อัพเดทสถานะไฮไลต์ของปุ่ม A/B/C หลังจากมีการเปลี่ยน preset
        Args:
            areas (str): Area string ของ preset ใหม่
        """
        self.update_area_button_highlights(areas)
        self.update_preset_buttons()
        self.update_button_highlights()

    def start_reset_hold(self, event):
        """เริ่มการ hold ปุ่ม reset"""
        if self.is_resetting:
            return

        self.is_resetting = True
        self.reset_progress = 0

        # เปลี่ยนสีปุ่มเป็นสีแดงอ่อน และรีเซ็ตฟอนต์เป็นขนาดปกติก่อน
        self.reset_area_button.configure(
            bg="#e74c3c", 
            relief="flat",  # ใช้ flat แทน sunken
            bd=0,
            highlightthickness=0,
            font=("FC Minimal Medium", 10),  # ใช้ฟอนต์ขนาดปกติ
            fg=self.theme.get("text", "#ffffff")  # อักษรสีขาวเพื่อให้เห็นชัดบนพื้นหลังแดง
        )

        # เริ่มการนับถอยหลัง
        self.update_reset_progress()

    def cancel_reset_hold(self, event):
        """ยกเลิกการ hold ปุ่ม reset"""
        if not self.is_resetting:
            return

        # ยกเลิก timer ถ้ามี
        if self.reset_timer:
            self.root.after_cancel(self.reset_timer)
            self.reset_timer = None

        # รีเซ็ตสถานะปุ่ม
        self.is_resetting = False
        self.reset_progress = 0
        self.reset_area_button.configure(
            text=self.original_reset_text,
            bg=self.theme.get("bg", "#1a1a1a"),  # กลับเป็นพื้นหลังโปร่งใส
            relief="flat",
            bd=0,
            highlightthickness=0,
            font=("FC Minimal Medium", 10),  # รีเซ็ตฟอนต์เป็นขนาดปกติ
            fg=self.theme.get("text_dim", "#b2b2b2")  # รีเซ็ตสีอักษรเป็นสีปกติ
        )

    def update_reset_progress(self):
        """อัพเดท progress การ reset"""
        if not self.is_resetting:
            return

        self.reset_progress += 1

        # สร้าง visual feedback แบบง่าย
        dots = "." * (self.reset_progress % 4)  # จำนวนจุดที่เพิ่มขึ้น
        progress_text = f"{3 - (self.reset_progress // 10)}{dots}"

        if self.reset_progress < 30:
            self.reset_area_button.configure(
                text=progress_text,
                font=("FC Minimal Medium", 14),  # ใช้ฟอนต์และขนาดใหม่
                fg=self.theme.get("accent", "#6c5ce7"),  # ใช้สีหลักของ Theme
                relief="flat",
                bd=0,
                highlightthickness=0
            )
            self.reset_timer = self.root.after(100, self.update_reset_progress)
        else:
            self.execute_reset_areas()

    def execute_reset_areas(self):
        """ทำการ reset พิกัดของทุกพื้นที่ในทุก preset 1-6"""
        try:
            # รีเซ็ตข้อความปุ่มก่อน
            self.reset_area_button.configure(
                text="DONE!",
                bg="#2ecc71",  # สีเขียว
                relief="flat",
                bd=0,
                highlightthickness=0,
                font=("FC Minimal Medium", 10),  # รีเซ็ตฟอนต์เป็นขนาดปกติ
                fg=self.theme.get("text", "#ffffff")  # อักษรสีขาว
            )

            # รีเซ็ตพิกัดทุกพื้นที่ในระบบ translate_areas (ส่วนกลาง)
            for area in ["A", "B", "C"]:
                self.settings.set_translate_area(
                    0, 0, 0, 0, area  # start_x  # start_y  # end_x  # end_y  # area
                )

            # รีเซ็ตพิกัดในทุก preset (1-6)
            default_coordinates = {
                "A": {"start_x": 0, "start_y": 0, "end_x": 0, "end_y": 0},
                "B": {"start_x": 0, "start_y": 0, "end_x": 0, "end_y": 0},
                "C": {"start_x": 0, "start_y": 0, "end_x": 0, "end_y": 0},
            }

            # วนลูปรีเซ็ททุก preset 1-6
            for preset_num in range(1, 7):
                preset_data = self.settings.get_preset(preset_num)
                if preset_data:
                    # เก็บ areas และ role เดิมไว้ รีเซ็ตแค่ coordinates
                    areas = preset_data.get("areas", "A+B")

                    # บันทึกพิกัดใหม่ (รีเซ็ต) ลงใน preset
                    self.settings.save_preset(preset_num, areas, default_coordinates)

                    logging.info(f"Reset coordinates for preset {preset_num}")

            # ตั้งค่า has_unsaved_changes เป็น True
            self.has_unsaved_changes = True

            # อัพเดท UI
            self.update_button_highlights()

            # บังคับให้ซ่อนพื้นที่แสดงผล (ถ้ามี) เพราะพิกัดใหม่ไม่มีขนาด
            if self.is_area_shown:
                self.hide_show_area_ctrl()

            logging.info("Reset ALL area coordinates to (0,0,0,0) for ALL presets 1-6")

            # แสดงข้อความ "DONE!" ชั่วคราว
            self.root.after(1000, self._reset_button_to_normal)

        except Exception as e:
            logging.error(f"Error executing reset areas: {e}")
            self.reset_area_button.configure(
                text="ERROR",
                bg="#e74c3c",  # สีแดง
                relief="flat",
                bd=0,
                highlightthickness=0,
                font=("FC Minimal Medium", 10),  # รีเซ็ตฟอนต์เป็นขนาดปกติ
                fg=self.theme.get("text", "#ffffff")  # อักษรสีขาว
            )
            self.root.after(2000, self._reset_button_to_normal)
        finally:
            self.is_resetting = False

    def _reset_button_to_normal(self):
        """คืนสถานะปุ่ม reset เป็นปกติ"""
        if hasattr(self, "reset_area_button") and self.reset_area_button.winfo_exists():
            self.reset_area_button.configure(
                text=self.original_reset_text,
                bg=self.theme.get("bg", "#1a1a1a"),  # ใช้พื้นหลังโปร่งใส
                relief="flat",
                bd=0,
                highlightthickness=0,
                font=("FC Minimal Medium", 10),  # รีเซ็ตฟอนต์ให้เป็นขนาดปกติ
                fg=self.theme.get("text_dim", "#b2b2b2"),  # รีเซ็ตสีอักษรให้เป็นสีปกติ
            )

    def save_last_preset_to_settings(self, preset_num, source="unknown"):
        """
        บันทึกข้อมูล preset ล่าสุดที่ใช้งานลงใน settings และซิงค์ระบบต่างๆ
        Args:
            preset_num: หมายเลข preset ที่ใช้ล่าสุด (1-6)
            source: แหล่งที่มาของการเปลี่ยนแปลง เช่น "hover", "control_ui", "auto"
        Returns:
            bool: True ถ้าสำเร็จ, False ถ้าล้มเหลว
        """
        try:
            if not isinstance(preset_num, int) or preset_num < 1 or preset_num > 6:
                logging.warning(f"Invalid preset number: {preset_num}, must be 1-6")
                return False

            self.settings["active_preset"] = preset_num
            self.sync_last_used_preset(preset_num, source=source)
            logging.info(
                f"Saved last preset {preset_num} to settings (source: {source})"
            )
            return True
        except Exception as e:
            logging.error(f"Error saving last preset to settings: {e}")
            return False

    def update_control_ui_preset_active(self, preset_num, force_update=False):
        """
        บังคับอัพเดทการแสดงผลปุ่ม preset บน control_ui
        Args:
            preset_num: หมายเลข preset ที่ต้องการให้เป็น active (1-6)
            force_update: บังคับอัพเดทแม้จะเป็น preset เดิม
        """
        try:
            # ตรวจสอบความถูกต้องของข้อมูล
            if not isinstance(preset_num, int) or preset_num < 1 or preset_num > 6:
                logging.warning(f"Invalid preset number: {preset_num}, must be 1-6")
                return False

            # อัพเดท internal state
            if self.current_preset != preset_num or force_update:
                self.current_preset = preset_num
                self.update_preset_buttons()
                logging.info(f"Updated control UI preset active: {preset_num}")
            return True
        except Exception as e:
            logging.error(f"Error updating control UI preset active: {e}")
            return False


if __name__ == "__main__":
    root = tk.Tk()

    def dummy_force():
        print("Force translate triggered")

    print("This module is running in test mode")
