import tkinter as tk
from tkinter import ttk, messagebox
import logging
from appearance import appearance_manager
from advance_ui import AdvanceUI
from settings import Settings, is_valid_hotkey
from simplified_hotkey_ui import SimplifiedHotkeyUI  # เพิ่มบรรทัดนี้

# เพิ่ม import สำหรับการจัดการ monitor position
try:
    import win32api
    import win32con
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False
    print("Warning: win32api not available, using fallback positioning for Settings UI")


class HotkeyUI:
    def __init__(
        self, parent, settings, apply_settings_callback, update_hotkeys_callback,
        toggle_click_callback=None, toggle_hover_callback=None
    ):
        self.parent = parent
        self.settings = settings
        self.apply_settings_callback = apply_settings_callback
        self.update_hotkeys_callback = update_hotkeys_callback
        self.toggle_click_callback = toggle_click_callback
        self.toggle_hover_callback = toggle_hover_callback
        self.settings_window = None
        self.settings_visible = False
        self.ocr_toggle_callback = None
        self.advance_ui = None

        # เปลี่ยนจาก self.hotkey_ui เป็น self.simplified_hotkey_ui
        self.hotkey_ui = None  # ตัวเก่า - คงไว้ชั่วคราว
        self.simplified_hotkey_ui = None  # ตัวใหม่

        self.create_settings_window()

    def show(self):
        """แสดงหน้าต่าง HotkeyUI"""
        try:
            if self.hotkey_window is None or not self.hotkey_window.winfo_exists():
                self.create_hotkey_window()
                # ตั้งค่า size เริ่มต้นที่แน่นอน
                self.hotkey_window.geometry("340x320")

            # แสดงหน้าต่าง
            self.hotkey_window.deiconify()
            self.hotkey_window.attributes("-topmost", True)
            self.hotkey_window.lift()

            # รอให้หน้าต่างแสดงเสร็จก่อน
            self.hotkey_window.update_idletasks()

            # โหลดค่า hotkeys ปัจจุบัน
            self.load_current_hotkeys()

            # บังคับให้อัพเดต Entry widgets โดยตรง
            self.hotkey_window.after(50, self.force_update_entries)

            return self.hotkey_window
        except Exception as e:
            print(f"Error showing hotkey window: {e}")
            return None

    def create_hotkey_window(self):
        self.hotkey_window = tk.Toplevel(self.parent)
        self.hotkey_window.title("Hotkey Settings")
        self.hotkey_window.geometry("340x320")  # เพิ่มขนาดให้ใหญ่กว่าเดิม
        self.hotkey_window.overrideredirect(True)
        self.hotkey_window.resizable(True, True)  # อนุญาตให้ขยายขนาดได้
        appearance_manager.apply_style(self.hotkey_window)

        # ปรับขนาดฟอนต์ให้ใหญ่ขึ้น
        title_label = tk.Label(
            self.hotkey_window,
            text="ตั้งค่า Hotkey",
            bg=appearance_manager.bg_color,
            fg="#00FFFF",  # สีฟ้าเพื่อเน้นหัวข้อ
            font=("Bai Jamjuree Light", 15, "bold"),
            justify=tk.CENTER,
        )
        title_label.pack(pady=(10, 5))

        description_label = tk.Label(
            self.hotkey_window,
            text="พิมพ์ตัวอักษรคีย์ลัดที่ต้องการ\nแล้วกด save",
            bg=appearance_manager.bg_color,
            fg="white",
            font=("Bai Jamjuree Light", 13),
            justify=tk.LEFT,
        )
        description_label.pack(pady=5, padx=15)

        # Toggle UI
        toggle_frame = tk.Frame(self.hotkey_window, bg=appearance_manager.bg_color)
        toggle_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(
            toggle_frame,
            text="Toggle UI:",
            bg=appearance_manager.bg_color,
            fg=appearance_manager.fg_color,
        ).pack(side=tk.LEFT)
        self.toggle_ui_entry = tk.Entry(toggle_frame, textvariable=self.toggle_ui_var)
        self.toggle_ui_entry.pack(side=tk.RIGHT, expand=True, fill=tk.X)

        # Start/Stop
        start_stop_frame = tk.Frame(self.hotkey_window, bg=appearance_manager.bg_color)
        start_stop_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(
            start_stop_frame,
            text="Start/Stop Translate:",
            bg=appearance_manager.bg_color,
            fg=appearance_manager.fg_color,
        ).pack(side=tk.LEFT)
        self.start_stop_entry = tk.Entry(
            start_stop_frame, textvariable=self.start_stop_var
        )
        self.start_stop_entry.pack(side=tk.RIGHT, expand=True, fill=tk.X)

        # เพิ่ม Force Translate (R-Click)
        force_frame = tk.Frame(self.hotkey_window, bg=appearance_manager.bg_color)
        force_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(
            force_frame,
            text="Force Translate:",
            bg=appearance_manager.bg_color,
            fg=appearance_manager.fg_color,
        ).pack(side=tk.LEFT)
        self.force_translate_entry = tk.Entry(
            force_frame, textvariable=self.force_translate_var
        )
        self.force_translate_entry.pack(side=tk.RIGHT, expand=True, fill=tk.X)

        # Default และ Save Button
        button_frame = tk.Frame(self.hotkey_window, bg=appearance_manager.bg_color)
        button_frame.pack(pady=10)

        # เพิ่มปุ่ม Default
        default_button = appearance_manager.create_styled_button(
            button_frame, "Default", self.reset_to_default
        )
        default_button.pack(side=tk.LEFT, padx=5)

        # ปุ่ม Save
        self.save_button = appearance_manager.create_styled_button(
            button_frame, "Save", self.save_hotkeys
        )
        self.save_button.pack(side=tk.LEFT, padx=5)

        # ปุ่มปิด
        close_button = appearance_manager.create_styled_button(
            self.hotkey_window, "X", self.close
        )
        close_button.place(x=5, y=5, width=20, height=20)

        # Bindings
        self.hotkey_window.bind("<Button-1>", self.start_move)
        self.hotkey_window.bind("<ButtonRelease-1>", self.stop_move)
        self.hotkey_window.bind("<B1-Motion>", self.do_move)

    def adjust_hotkey_ui(self):
        """ปรับปรุงการแสดงผลของ Hotkey UI ให้มีขนาดคงที่"""
        try:
            # กำหนดขนาดคงที่สำหรับหน้าต่าง
            FIXED_WIDTH = 340
            FIXED_HEIGHT = 320

            # ปรับขนาดช่องกรอกให้กว้างขึ้น และกำหนดสีพื้นหลังชัดเจน
            entry_config = {
                "width": 12,
                "bg": "#333333",
                "fg": "#00FFFF",  # สีฟ้าเพื่อให้เห็นได้ชัดเจน
                "font": ("Consolas", 12),
                "insertbackground": "white",  # สีของ cursor
                "justify": "center",
            }

            # อัพเดทช่องกรอกทั้งหมด
            if hasattr(self, "toggle_ui_entry"):
                self.toggle_ui_entry.config(**entry_config)

            if hasattr(self, "start_stop_entry"):
                self.start_stop_entry.config(**entry_config)

            if hasattr(self, "force_translate_entry"):
                self.force_translate_entry.config(**entry_config)

            # กำหนดขนาดคงที่ - สำคัญมาก เพื่อป้องกันการขยายขนาดซ้ำซ้อน
            self.hotkey_window.geometry(f"{FIXED_WIDTH}x{FIXED_HEIGHT}")
            print(f"Fixed HotkeyUI window size to {FIXED_WIDTH}x{FIXED_HEIGHT}")

        except Exception as e:
            print(f"Error adjusting hotkey UI: {e}")

    def print_current_hotkeys(self):
        """แสดงค่าปัจจุบันของ hotkeys เพื่อการ debug"""
        print("\n=== Current Hotkey Settings ===")
        print(f"Variable values:")
        print(f"- toggle_ui_var: '{self.toggle_ui_var.get()}'")
        print(f"- start_stop_var: '{self.start_stop_var.get()}'")
        print(f"- force_translate_var: '{self.force_translate_var.get()}'")

        print("\nEntry values:")
        if hasattr(self, "toggle_ui_entry"):
            print(f"- toggle_ui_entry: '{self.toggle_ui_entry.get()}'")
        if hasattr(self, "start_stop_entry"):
            print(f"- start_stop_entry: '{self.start_stop_entry.get()}'")
        if hasattr(self, "force_translate_entry"):
            print(f"- force_translate_entry: '{self.force_translate_entry.get()}'")

        print("\nSettings values:")
        print(f"- toggle_ui: '{self.settings.get_shortcut('toggle_ui', 'alt+l')}'")
        print(
            f"- start_stop_translate: '{self.settings.get_shortcut('start_stop_translate', 'f9')}'"
        )
        print(
            f"- force_translate: '{self.settings.get_shortcut('force_translate', 'r-click')}'"
        )
        print("==============================\n")

    def reset_to_default(self):
        """รีเซ็ตค่าเป็นค่าเริ่มต้น"""
        self.toggle_ui_var.set("alt+l")
        self.start_stop_var.set("f9")
        self.force_translate_var.set("r-click")

    def load_current_hotkeys(self):
        """โหลดค่า hotkey ปัจจุบันและอัพเดตแสดงใน Entry fields"""
        try:
            # ดึงค่าจาก settings โดยมีค่าเริ่มต้นถ้าไม่พบค่า
            toggle_ui = self.settings.get_shortcut("toggle_ui", "alt+l")
            start_stop = self.settings.get_shortcut("start_stop_translate", "f9")
            force_translate = self.settings.get_shortcut("force_translate", "r-click")

            print(
                f"DEBUG: Loading hotkeys - Toggle: '{toggle_ui}', Start/Stop: '{start_stop}', Force: '{force_translate}'"
            )

            # กรณีค่าเป็นค่าว่าง ใช้ค่าเริ่มต้น
            if not toggle_ui:
                toggle_ui = "alt+l"
            if not start_stop:
                start_stop = "f9"
            if not force_translate:
                force_translate = "r-click"

            # อัพเดต StringVar สำหรับผูกกับ Entry
            self.toggle_ui_var.set(toggle_ui)
            self.start_stop_var.set(start_stop)
            self.force_translate_var.set(force_translate)

            # อัพเดต Entry widgets โดยตรง
            if hasattr(self, "toggle_ui_entry"):
                self.toggle_ui_entry.delete(0, tk.END)
                self.toggle_ui_entry.insert(0, toggle_ui)

            if hasattr(self, "start_stop_entry"):
                self.start_stop_entry.delete(0, tk.END)
                self.start_stop_entry.insert(0, start_stop)

            if hasattr(self, "force_translate_entry"):
                self.force_translate_entry.delete(0, tk.END)
                self.force_translate_entry.insert(0, force_translate)

            print(
                f"Successfully loaded hotkeys: Toggle UI: {toggle_ui}, Start/Stop: {start_stop}, Force: {force_translate}"
            )
        except Exception as e:
            print(f"Error loading hotkeys: {e}")

    def force_update_entries(self):
        """บังคับอัพเดตค่าใน Entry โดยตรงโดยไม่พึ่ง StringVar"""
        # ข้อมูลจาก settings
        toggle_ui = self.settings.get_shortcut("toggle_ui", "alt+l")
        start_stop = self.settings.get_shortcut("start_stop_translate", "f9")
        force_translate = self.settings.get_shortcut("force_translate", "r-click")

        # อัพเดตโดยตรงไปที่ Entry widgets
        if hasattr(self, "toggle_ui_entry") and self.toggle_ui_entry.winfo_exists():
            self.toggle_ui_entry.delete(0, tk.END)
            self.toggle_ui_entry.insert(0, toggle_ui)
            print(f"Updated toggle_ui_entry directly: '{toggle_ui}'")

        if hasattr(self, "start_stop_entry") and self.start_stop_entry.winfo_exists():
            self.start_stop_entry.delete(0, tk.END)
            self.start_stop_entry.insert(0, start_stop)
            print(f"Updated start_stop_entry directly: '{start_stop}'")

        if (
            hasattr(self, "force_translate_entry")
            and self.force_translate_entry.winfo_exists()
        ):
            self.force_translate_entry.delete(0, tk.END)
            self.force_translate_entry.insert(0, force_translate)
            print(f"Updated force_translate_entry directly: '{force_translate}'")

        self.toggle_ui_var.set(toggle_ui)
        self.start_stop_var.set(start_stop)
        self.force_translate_var.set(force_translate)

        # หลังจากอัพเดต entries เสร็จแล้ว ให้ปรับขนาดหน้าต่างให้คงที่
        self.hotkey_window.after(100, self.adjust_hotkey_ui)

    def save_hotkeys(self):
        """บันทึกค่า hotkey ใหม่"""
        toggle_ui = self.toggle_ui_var.get().lower()
        start_stop = self.start_stop_var.get().lower()
        force_translate = self.force_translate_var.get().lower()

        # ตรวจสอบความถูกต้องของค่า
        valid_toggleui = is_valid_hotkey(toggle_ui)
        valid_startstop = is_valid_hotkey(start_stop)
        # ยกเว้น r-click ซึ่งเป็นค่าพิเศษ
        valid_force = force_translate == "r-click" or is_valid_hotkey(force_translate)

        if valid_toggleui and valid_startstop and valid_force:
            self.settings.set_shortcut("toggle_ui", toggle_ui)
            self.settings.set_shortcut("start_stop_translate", start_stop)
            self.settings.set_shortcut("force_translate", force_translate)

            self.save_button.config(text="Saved!")
            print(
                f"New hotkeys saved: Toggle UI: {toggle_ui}, Start/Stop: {start_stop}, Force: {force_translate}"
            )
            # แสดงข้อความชั่วคราวเมื่อบันทึกสำเร็จ
            feedback = tk.Label(
                self.hotkey_window,
                text="บันทึกคีย์ลัดเรียบร้อยแล้ว!",
                bg="#1E8449",
                fg="white",
                font=("Bai Jamjuree Light", 13),
                padx=10,
                pady=5,
            )
            feedback.place(relx=0.5, rely=0.9, anchor="center")

            # ซ่อนข้อความหลังจาก 2 วินาที
            self.hotkey_window.after(2000, feedback.destroy)

            # คืนค่าปุ่มกลับเป็นปกติ
            self.hotkey_window.after(2000, lambda: self.save_button.config(text="Save"))

            # เรียกใช้ callback เพื่ออัพเดต hotkeys ในระบบ
            if self.update_hotkeys_callback:
                self.update_hotkeys_callback()
        else:
            messagebox.showerror("Invalid Hotkey", "กรุณากรอกคีย์ลัดที่ถูกต้อง")

    def close(self):
        if self.hotkey_window and self.hotkey_window.winfo_exists():
            self.save_button.config(text="Save")
            self.hotkey_window.withdraw()

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.x = None
        self.y = None

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.hotkey_window.winfo_x() + deltax
        y = self.hotkey_window.winfo_y() + deltay
        self.hotkey_window.geometry(f"+{x}+{y}")


class SettingsUI:
    def __init__(
        self,
        parent,
        settings,
        apply_settings_callback,
        update_hotkeys_callback,
        main_app=None,
    ):
        self.parent = parent
        self.settings = settings
        self.apply_settings_callback = apply_settings_callback
        self.update_hotkeys_callback = update_hotkeys_callback
        self.settings_window = None
        self.settings_visible = False
        self.ocr_toggle_callback = None
        self.advance_ui = None
        self.main_app = main_app  # เพิ่มการเก็บ main_app
        self.tooltip = None  # เพิ่มตัวแปรสำหรับเก็บ tooltip

        # ประกาศตัวแปรสำหรับ UI
        self.hover_translation_var = tk.BooleanVar()
        self.hover_translation_var.set(
            self.settings.get("enable_hover_translation", False)
        )

        # ประกาศ attribute สำหรับ SimplifiedHotkeyUI
        self.simplified_hotkey_ui = None

        self.create_settings_window()

    def create_settings_window(self):
        self.settings_window = tk.Toplevel(self.parent)
        self.settings_window.overrideredirect(True)

        # กำหนดความโปร่งใสเป็น 100% (ไม่โปร่งใส)
        self.settings_window.attributes("-alpha", 1.0)

        # ใช้ appearance_manager สำหรับสไตล์อื่นๆ แต่ไม่ใช้ความโปร่งใสจาก manager
        appearance_manager.bg_color = appearance_manager.bg_color
        appearance_manager.fg_color = appearance_manager.fg_color
        self.settings_window.configure(bg=appearance_manager.bg_color)

        self.create_settings_ui()
        self.settings_window.withdraw()

    def create_tooltip(self, widget, text):
        """สร้าง tooltip แสดงข้อความเมื่อนำเมาส์ไปวางเหนือ widget"""

        def enter(event):
            x, y, _, _ = widget.bbox("insert")
            x += widget.winfo_rootx() + 25
            y += widget.winfo_rooty() + 20

            # สร้าง Toplevel window
            self.tooltip = tk.Toplevel(widget)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{x}+{y}")

            label = tk.Label(
                self.tooltip,
                text=text,
                justify=tk.LEFT,
                background="#ffffe0",
                relief=tk.SOLID,
                borderwidth=1,
                font=("Bai Jamjuree Light", 10),
            )
            label.pack(ipadx=5, ipady=3)

        def leave(event):
            if self.tooltip:
                self.tooltip.destroy()
                self.tooltip = None

        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    def open_settings(self, parent_x, parent_y, parent_width, mbb_side='left'):
        """Open settings window at specified position relative to parent
        
        Args:
            parent_x (int): X position ของหน้าต่าง MBB
            parent_y (int): Y position ของหน้าต่าง MBB  
            parent_width (int): ความกว้างของหน้าต่าง MBB
            mbb_side (str): ตำแหน่งของ MBB ('left' หรือ 'right')
        """
        # ใช้ logic แบบฉลาดในการจัดตำแหน่ง Settings UI (เหมือนใน settings.py)
        try:
            # ดึงขนาดของ Settings window
            self.settings_window.update_idletasks()
            settings_width = self.settings_window.winfo_reqwidth()
            if settings_width < 400:  # กำหนดขนาดขั้นต่ำ
                settings_width = 400
                
            gap = 20  # ระยะห่างระหว่าง MBB และ Settings
            
            # ดึงข้อมูลจอภาพ
            try:
                if HAS_WIN32:
                    # ใช้หน้าจอหลักสำหรับ fallback
                    monitor_left = 0
                    monitor_right = self.settings_window.winfo_screenwidth()
                else:
                    # ไม่มี win32api, ใช้หน้าจอหลัก
                    monitor_left = 0
                    monitor_right = self.settings_window.winfo_screenwidth()
                    
            except Exception as e:
                print(f"Failed to get monitor info for Settings: {e}")
                # Fallback ใช้หน้าจอหลัก
                monitor_left = 0
                monitor_right = self.settings_window.winfo_screenwidth()
            
            # ตัดสินใจตำแหน่งตาม MBB side
            if mbb_side == 'left':
                # MBB อยู่ซ้าย -> วาง Settings ด้านขวา
                x = parent_x + parent_width + gap
                # ตรวจสอบว่าไม่ล้นจอ
                if x + settings_width > monitor_right:
                    x = parent_x - settings_width - gap  # สลับไปซ้าย
            else:
                # MBB อยู่ขวา -> วาง Settings ด้านซ้าย  
                x = parent_x - settings_width - gap
                # ตรวจสอบว่าไม่ล้นจอ
                if x < monitor_left:
                    x = parent_x + parent_width + gap  # สลับไปขวา
                    
            y = parent_y
            
            print(f"Settings UI positioned at: {x}, {y} (MBB side: {mbb_side})")
            
        except Exception as e:
            print(f"Error in smart positioning for Settings, using fallback: {e}")
            # Fallback เป็นวิธีเดิม
            x = parent_x + parent_width + 20
            y = parent_y
            
        self.settings_window.geometry(f"+{x}+{y}")

        # แน่ใจว่าความโปร่งใสเป็น 100% (ไม่โปร่งใส)
        self.settings_window.attributes("-alpha", 1.0)

        self.font_size_var.set(str(self.settings.get("font_size")))
        self.font_var.set(self.settings.get("font"))
        # ... (โค้ดส่วนที่เหลือของ open_settings เหมือนเดิม) ...

        # --- เพิ่มการอัพเดท font_display_label (ถ้ายังไม่มี) ---
        font_name = self.settings.get("font")
        font_size = self.settings.get("font_size")
        if hasattr(self, "font_display_label"):
            self.font_display_label.config(text=f"{font_name} ({font_size}px)")
        # ----------------------------------------------------

        self.width_entry.delete(0, tk.END)
        self.width_entry.insert(0, str(self.settings.get("width")))
        self.height_entry.delete(0, tk.END)
        self.height_entry.insert(0, str(self.settings.get("height")))
        self.force_translate_var.set(self.settings.get("enable_force_translate", True))
        self.auto_hide_var.set(self.settings.get("enable_auto_hide", True))

        # บังคับให้ auto_area_switch เป็น False ใน settings (เอาออกแล้ว)
        # self.settings.set("enable_auto_area_switch", False)

        self.click_translate_var.set(self.settings.get("enable_click_translate", False))
        self.hover_translation_var.set(
            self.settings.get("enable_hover_translation", False)
        )

        # อัพเดทชอร์ตคัท (ถ้ามีปุ่ม)
        if hasattr(self, "toggle_ui_btn") and hasattr(self, "start_stop_btn"):
            toggle_ui_shortcut = self.settings.get_shortcut("toggle_ui", "alt+l")
            start_stop_shortcut = self.settings.get_shortcut(
                "start_stop_translate", "f9"
            )
            self.toggle_ui_btn.config(text=toggle_ui_shortcut.upper())
            self.start_stop_btn.config(text=start_stop_shortcut.upper())

        self.settings_window.deiconify()
        self.settings_window.lift()
        self.settings_window.attributes("-topmost", True)
        self.settings_visible = True

        # รีเซ็ตข้อความบนปุ่ม (ถ้ามี)
        if hasattr(self, "display_button"):
            self.display_button.config(text="SCREEN/CPU")
        if hasattr(self, "hotkey_button"):
            self.hotkey_button.config(text="HOTKEY")
        if hasattr(self, "font_button"):
            self.font_button.config(text="FONT")
        if hasattr(self, "model_button"):
            self.model_button.config(text="MODEL")

    def close_settings(self):
        self.settings_window.withdraw()
        self.settings_visible = False

        # *** เพิ่มการตรวจสอบก่อนเรียก .close() ***
        if hasattr(self, "advance_ui") and self.advance_ui:
            self.advance_ui.close()
        # *****************************************

        # ปิด SimplifiedHotkeyUI
        if (
            hasattr(self, "simplified_hotkey_ui") and self.simplified_hotkey_ui
        ):  # เพิ่มการตรวจสอบ
            self.simplified_hotkey_ui.close()

        if hasattr(self, "hotkey_button"):  # ตรวจสอบก่อน config
            self.hotkey_button.config(text="HotKey")

        # เรียก callback ถ้ามี
        if hasattr(self, "on_close_callback") and self.on_close_callback:
            self.on_close_callback()

    def create_toggle_switch(self, parent, text, variable, state=tk.NORMAL):
        """ปรับปรุงสร้าง toggle switch ที่รองรับการใช้ custom style และ state"""
        frame = tk.Frame(parent, bg=appearance_manager.bg_color)
        frame.pack(pady=5, padx=10, fill=tk.X)

        label = tk.Label(
            frame,
            text=text,
            bg=appearance_manager.bg_color,
            fg=appearance_manager.fg_color,
            font=("Bai Jamjuree Light", 13),
        )
        label.pack(side=tk.LEFT)

        switch = ttk.Checkbutton(
            frame, style="Switch.TCheckbutton", variable=variable, state=state
        )
        switch.pack(side=tk.RIGHT)

        return frame

    def create_settings_section(self, parent, title, padx=10, pady=5):
        """Create a section with title and frame"""
        section_frame = tk.Frame(parent, bg=appearance_manager.bg_color, bd=1)
        section_frame.pack(fill=tk.X, padx=padx, pady=pady)

        # สร้างป้ายชื่อด้วยกรอบสวยงาม
        title_frame = tk.Frame(section_frame, bg="#383838", bd=0)
        title_frame.pack(fill=tk.X)

        title_label = tk.Label(
            title_frame,
            text=title,
            font=("Bai Jamjuree Light", 13),
            bg="#383838",
            fg="white",
            anchor="w",
            padx=10,
            pady=3,
        )
        title_label.pack(fill=tk.X)

        # กรอบเนื้อหา
        content_frame = tk.Frame(section_frame, bg=appearance_manager.bg_color, bd=0)
        content_frame.pack(fill=tk.X, pady=(0, 5), padx=5)

        return content_frame

    def _on_click_translate_change(self, *args):
        """จัดการเมื่อ Click Translate toggle เปลี่ยนค่า"""
        try:
            new_value = self.click_translate_var.get()
            logging.info(f"SettingsUI: Click Translate changed to {new_value}")
            
            # อัพเดทค่าใน settings
            self.settings.set("enable_click_translate", new_value)
            
            # เรียก callback ถ้ามี
            if self.toggle_click_callback:
                self.toggle_click_callback(new_value)
            else:
                logging.warning("SettingsUI: No toggle_click_callback provided")
                
        except Exception as e:
            logging.error(f"Error in _on_click_translate_change: {e}")
    
    def _on_hover_translation_change(self, *args):
        """จัดการเมื่อ Hover Translation toggle เปลี่ยนค่า"""
        try:
            new_value = self.hover_translation_var.get()
            logging.info(f"SettingsUI: Hover Translation changed to {new_value}")
            
            # อัพเดทค่าใน settings
            self.settings.set("enable_hover_translation", new_value)
            
            # เรียก callback ถ้ามี
            if self.toggle_hover_callback:
                self.toggle_hover_callback(new_value)
            else:
                logging.warning("SettingsUI: No toggle_hover_callback provided")
                
        except Exception as e:
            logging.error(f"Error in _on_hover_translation_change: {e}")

    def create_settings_ui(self):
        """Initialize and setup all UI components for the main settings window"""
        # --- ส่วนหัวและ Frame หลัก ---
        self.settings_window.geometry("420x580")
        self.settings_window.configure(bg=appearance_manager.bg_color)
        header_frame = tk.Frame(self.settings_window, bg=appearance_manager.bg_color)
        header_frame.pack(fill=tk.X, pady=(5, 0))
        close_label = tk.Label(
            header_frame,
            text="×",
            font=("Arial", 14, "bold"),
            bg="#FF5252",
            fg="white",
            padx=4,
            pady=0,
        )
        close_label.place(x=5, y=5)
        close_label.bind("<Button-1>", lambda e: self.close_settings())
        close_label.bind(
            "<Enter>", lambda e: close_label.config(bg="#FF7B7B", cursor="hand2")
        )
        close_label.bind("<Leave>", lambda e: close_label.config(bg="#FF5252"))
        tk.Label(
            header_frame,
            text="SETTINGS",
            bg=appearance_manager.bg_color,
            fg=appearance_manager.get_accent_color(),
            font=("Nasalization Rg", 14, "bold"),
        ).pack(pady=(5, 0))
        tk.Label(
            header_frame,
            text="ปรับแต่งหน้าต่างแสดงผล (TUI) และฟังก์ชันการทำงาน",
            bg=appearance_manager.bg_color,
            fg="#AAAAAA",
            font=("Bai Jamjuree Light", 11),
        ).pack(pady=(0, 5))
        main_frame = tk.Frame(self.settings_window, bg=appearance_manager.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 5))

        # --- SECTION 1: TUI DISPLAY SETTINGS ---
        tui_section = self.create_settings_section(main_frame, "หน้าต่างผลการแปล (TUI)")

        # Font Settings
        font_frame = tk.Frame(tui_section, bg=appearance_manager.bg_color)
        font_frame.pack(fill=tk.X, pady=2)
        tk.Label(
            font_frame,
            text="Font Settings:",
            width=15,
            anchor="w",
            bg=appearance_manager.bg_color,
            fg="white",
            font=("Bai Jamjuree Light", 13),
        ).pack(side=tk.LEFT)
        # ใช้ค่าเริ่มต้นที่ถูกต้องเมื่อสร้าง Label ครั้งแรก
        initial_font = self.settings.get("font", "IBM Plex Sans Thai Medium.ttf")
        initial_font_size = self.settings.get("font_size", 24)
        self.font_display_label = tk.Label(
            font_frame,
            text=f"{initial_font} ({initial_font_size}px)",
            bg="#333333",
            fg="white",
            font=("Bai Jamjuree Light", 11),
            anchor="w",
            padx=10,
        )
        self.font_display_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        # สร้าง StringVar หลังจากมี Label แล้ว
        self.font_size_var = tk.StringVar(value=str(initial_font_size))
        self.font_var = tk.StringVar(value=initial_font)

        # Window Width & Height
        size_frame = tk.Frame(tui_section, bg=appearance_manager.bg_color)
        size_frame.pack(fill=tk.X, pady=2)
        tk.Label(
            size_frame,
            text="Width (px):",
            width=10,
            anchor="w",
            bg=appearance_manager.bg_color,
            fg="white",
            font=("Bai Jamjuree Light", 13),
        ).pack(side=tk.LEFT)
        self.width_entry = tk.Entry(
            size_frame,
            width=5,
            bg="#383838",
            fg="white",
            insertbackground="white",
            bd=1,
            relief=tk.SOLID,
            font=("Consolas", 11),
        )
        self.width_entry.pack(side=tk.LEFT, padx=5)
        self.width_entry.bind("<FocusOut>", self.validate_window_size)
        self.width_entry.bind("<Return>", self.validate_window_size)
        tk.Label(
            size_frame,
            text="Height (px):",
            anchor="w",
            bg=appearance_manager.bg_color,
            fg="white",
            font=("Bai Jamjuree Light", 13),
        ).pack(side=tk.LEFT, padx=(10, 0))
        self.height_entry = tk.Entry(
            size_frame,
            width=5,
            bg="#383838",
            fg="white",
            insertbackground="white",
            bd=1,
            relief=tk.SOLID,
            font=("Consolas", 11),
        )
        self.height_entry.pack(side=tk.LEFT, padx=5)
        self.height_entry.bind("<FocusOut>", self.validate_window_size)
        self.height_entry.bind("<Return>", self.validate_window_size)
        self.apply_button = tk.Button(
            size_frame,
            text="APPLY",
            command=self.apply_settings,
            bg="#1E88E5",
            fg="white",
            activebackground="#1565C0",
            activeforeground="white",
            bd=0,
            relief=tk.RAISED,
            font=("Nasalization Rg", 10, "bold"),
            padx=10,
            pady=2,
            cursor="hand2",
        )
        self.apply_button.pack(side=tk.RIGHT, padx=(10, 5))
        self.apply_button.bind(
            "<Enter>", lambda e: self.apply_button.config(bg="#1565C0")
        )
        self.apply_button.bind(
            "<Leave>", lambda e: self.apply_button.config(bg="#1E88E5")
        )

        # --- SECTION 2: FEATURES TOGGLES ---
        features_section = self.create_settings_section(main_frame, "การตั้งค่าฟังก์ชัน")
        self.indicators = {}

        # BooleanVars
        self.force_translate_var = tk.BooleanVar(
            value=self.settings.get("enable_force_translate", True)
        )
        self.auto_hide_var = tk.BooleanVar(
            value=self.settings.get("enable_auto_hide", True)
        )
        self.click_translate_var = tk.BooleanVar(
            value=self.settings.get("enable_click_translate", False)
        )
        self.hover_translation_var = tk.BooleanVar(
            value=self.settings.get("enable_hover_translation", False)
        )

        # สร้าง Toggles พื้นฐาน
        self.create_toggle_switch(
            features_section, "Force Translate with R-click", self.force_translate_var
        )
        self.create_toggle_switch(
            features_section, "Hide UI with W,A,S,D keys", self.auto_hide_var
        )

        # --- Click Translate Toggle ---
        # ** ผูก Trace กับเมธอดใหม่ **
        current_traces_click = self.click_translate_var.trace_info()
        for mode, cb_name in current_traces_click:
            if mode == "write":
                try:
                    self.click_translate_var.trace_remove("write", cb_name)
                except:
                    pass
        callback_name_click = self.click_translate_var.trace_add(
            "write", self._on_click_translate_change
        )
        logging.info(
            f"SettingsUI: Trace added for click_translate_var. Callback name: {callback_name_click}"
        )
        self.create_toggle_switch(
            features_section, "Click Translate Mode", self.click_translate_var
        )

        # --- Hover Translate Toggle ---
        # ** ผูก Trace กับเมธอดใหม่ **
        current_traces_hover = self.hover_translation_var.trace_info()
        for mode, cb_name in current_traces_hover:
            if mode == "write":
                try:
                    self.hover_translation_var.trace_remove("write", cb_name)
                except:
                    pass
        callback_name_hover = self.hover_translation_var.trace_add(
            "write", self._on_hover_translation_change
        )
        logging.info(
            f"SettingsUI: Trace added for hover_translation_var. Callback name: {callback_name_hover}"
        )
        self.create_toggle_switch(
            features_section, "Hover Translation", self.hover_translation_var
        )

        # --- SECTION 3: ADVANCED SETTINGS ---
        advanced_section = self.create_settings_section(main_frame, "การตั้งค่าขั้นสูง")
        button_style = {
            "font": ("Nasalization Rg", 9),
            "width": 10,
            "padx": 5,
            "pady": 2,
            "bd": 1,
            "relief": tk.RAISED,
            "cursor": "hand2",
        }
        button_frame = tk.Frame(advanced_section, bg=appearance_manager.bg_color)
        button_frame.pack(fill=tk.X, pady=5)
        self.font_button = tk.Button(
            button_frame,
            text="FONT",
            command=self.toggle_font_ui,
            bg="#404040",
            fg="white",
            **button_style,
        )
        self.font_button.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        self.display_button = tk.Button(
            button_frame,
            text="SCREEN/CPU",
            command=self.toggle_advance_ui,
            bg="#404040",
            fg="white",
            **button_style,
        )
        self.display_button.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        self.model_button = tk.Button(
            button_frame,
            text="MODEL",
            command=self.toggle_model_settings,
            bg="#404040",
            fg="white",
            **button_style,
        )
        self.model_button.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        self.hotkey_button = tk.Button(
            button_frame,
            text="HOTKEY",
            command=self.toggle_hotkey_ui,
            bg="#404040",
            fg="white",
            **button_style,
        )
        self.hotkey_button.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        for button in [
            self.font_button,
            self.display_button,
            self.model_button,
            self.hotkey_button,
        ]:
            button.bind("<Enter>", lambda e, b=button: b.config(bg="#606060"))
            button.bind("<Leave>", lambda e, b=button: b.config(bg="#404040"))

        # --- SECTION 4: SHORTCUTS AND INFO ---
        info_section = self.create_settings_section(main_frame, "ข้อมูลโปรแกรม")
        shortcut_frame = tk.Frame(info_section, bg=appearance_manager.bg_color)
        shortcut_frame.pack(fill=tk.X)
        toggle_ui_shortcut = self.settings.get_shortcut("toggle_ui", "alt+l")
        start_stop_shortcut = self.settings.get_shortcut("start_stop_translate", "f9")
        tk.Label(
            shortcut_frame,
            text="Toggle UI:",
            bg=appearance_manager.bg_color,
            fg="#AAAAAA",
            font=("IBM Plex Sans Thai Medium", 8),
            width=8,
            anchor="e",
        ).pack(side=tk.LEFT, padx=(5, 2))
        self.toggle_ui_btn = tk.Label(
            shortcut_frame,
            text=toggle_ui_shortcut.upper(),
            bg="#333333",
            fg="white",
            font=("IBM Plex Sans Thai Medium", 8, "bold"),
            bd=1,
            relief=tk.RAISED,
            padx=5,
            pady=1,
            width=6,
            anchor="center",
        )
        self.toggle_ui_btn.pack(side=tk.LEFT)
        tk.Frame(shortcut_frame, width=10, bg=appearance_manager.bg_color).pack(
            side=tk.LEFT
        )
        tk.Label(
            shortcut_frame,
            text="Start/Stop:",
            bg=appearance_manager.bg_color,
            fg="#AAAAAA",
            font=("IBM Plex Sans Thai Medium", 8),
            width=8,
            anchor="e",
        ).pack(side=tk.LEFT, padx=(0, 2))
        self.start_stop_btn = tk.Label(
            shortcut_frame,
            text=start_stop_shortcut.upper(),
            bg="#333333",
            fg="white",
            font=("IBM Plex Sans Thai Medium", 8, "bold"),
            bd=1,
            relief=tk.RAISED,
            padx=5,
            pady=1,
            width=6,
            anchor="center",
        )
        self.start_stop_btn.pack(side=tk.LEFT)
        version_frame = tk.Frame(info_section, bg=appearance_manager.bg_color)
        version_frame.pack(fill=tk.X, pady=5)
        self.version_label = tk.Label(
            version_frame,
            text="==MBB v-9.0-beta build 13072025== by iarcanar",
            bg=appearance_manager.bg_color,
            fg="#A020F0",  # สีม่วงเหมือนกับโมเดล Gemini
            font=("JetBrains Mono NL Light", 11),  # ฟอนต์เหมือนกับโมเดล Gemini
            anchor="center",
        )
        self.version_label.pack(fill=tk.X)

        # --- Status message label ---
        self.status_label = tk.Label(
            main_frame,
            text="",
            bg=appearance_manager.bg_color,
            fg="#4CAF50",
            font=("Bai Jamjuree Light", 13, "bold"),
        )
        self.status_label.pack(pady=2)

        # --- Window Movement Bindings ---
        self.settings_window.bind("<Button-1>", self.start_move_settings)
        self.settings_window.bind("<ButtonRelease-1>", self.stop_move_settings)
        self.settings_window.bind("<B1-Motion>", self.do_move_settings)

        # --- ตั้งค่าเริ่มต้น ---
        self.width_entry.delete(0, tk.END)
        self.width_entry.insert(0, str(self.settings.get("width", 960)))
        self.height_entry.delete(0, tk.END)
        self.height_entry.insert(0, str(self.settings.get("height", 240)))

        logging.info("Settings UI create_settings_ui finished.")

    def apply_settings(self, settings_dict=None):
        """Apply settings with validation and show temporary message"""
        try:
            # กรณีกดปุ่ม Apply จาก settings UI
            if settings_dict is None:
                try:
                    # รวบรวมค่าการตั้งค่าจาก UI
                    font_size = int(self.font_size_var.get())
                    font = str(self.font_var.get()).strip()
                    width = max(300, min(2000, int(self.width_entry.get())))
                    height = max(200, min(1000, int(self.height_entry.get())))

                    # ดึงค่าจาก toggle switches โดยตรง
                    enable_force = bool(self.force_translate_var.get())
                    enable_auto_hide = bool(self.auto_hide_var.get())
                    enable_click_translate = bool(self.click_translate_var.get())
                    enable_hover_translation = bool(self.hover_translation_var.get())

                    # บันทึกค่าลง settings ทีละตัว
                    self.settings.set("font_size", font_size)
                    self.settings.set("font", font)
                    self.settings.set("width", width)
                    self.settings.set("height", height)
                    self.settings.set("enable_force_translate", enable_force)
                    self.settings.set("enable_auto_hide", enable_auto_hide)
                    self.settings.set("enable_click_translate", enable_click_translate)
                    self.settings.set(
                        "enable_hover_translation", enable_hover_translation
                    )

                    # สร้าง dict สำหรับส่งต่อให้ callback
                    settings_dict = {
                        "font_size": font_size,
                        "font": font,
                        "width": width,
                        "height": height,
                        "enable_force_translate": enable_force,
                        "enable_auto_hide": enable_auto_hide,
                        "enable_click_translate": enable_click_translate,
                        "enable_hover_translation": enable_hover_translation,
                    }

                    # เรียก callback เพื่ออัพเดต UI อื่นๆ
                    if self.apply_settings_callback:
                        self.apply_settings_callback(settings_dict)
                        logging.info("Settings applied successfully")

                    # เปลี่ยนข้อความปุ่ม Apply ชั่วคราว
                    self.apply_button.config(text="✓ APPLIED", bg="#4CAF50")  # สีเขียว

                    # แสดงข้อความ success
                    self.status_label.config(text="Settings applied successfully!")

                    # รีเซ็ตกลับหลังจาก 2 วินาที
                    self.settings_window.after(
                        2000,
                        lambda: self.apply_button.config(text="APPLY", bg="#1E88E5"),
                    )
                    self.settings_window.after(
                        2000, lambda: self.status_label.config(text="")
                    )

                    # อัพเดท toggle switch UI อีกครั้งเพื่อความมั่นใจ (ถ้ามี indicators)
                    if hasattr(self, "indicators"):
                        for indicator_id, data in self.indicators.items():
                            variable = data["variable"]
                            self.update_switch_ui(indicator_id, variable.get())

                    # พิมพ์ข้อมูลตัวแปรเพื่อการตรวจสอบ
                    print(f"Applied settings:")
                    print(f"- Force Translate: {enable_force}")
                    print(f"- Auto Hide: {enable_auto_hide}")
                    print(f"- Click Translate: {enable_click_translate}")
                    print(f"- Hover Translate: {enable_hover_translation}")

                    return True, None

                except ValueError as e:
                    self.status_label.config(text=f"Error: {str(e)}", fg="#FF5252")
                    self.settings_window.after(
                        3000, lambda: self.status_label.config(text="", fg="#4CAF50")
                    )
                    raise ValueError(f"Invalid input value: {str(e)}")

            # กรณีเรียกจาก advance settings
            else:
                logging.info("Applying advanced settings")
                # อัพเดทค่าลง settings
                for key, value in settings_dict.items():
                    self.settings.set(key, value)

                # บันทึกไฟล์
                self.settings.save_settings()

                if self.apply_settings_callback:
                    self.apply_settings_callback(settings_dict)

                return True, None

        except Exception as e:
            error_msg = f"Error applying settings: {str(e)}"
            logging.error(error_msg)

            # แสดงข้อความ error
            self.status_label.config(text=error_msg, fg="#FF5252")
            self.settings_window.after(
                3000, lambda: self.status_label.config(text="", fg="#4CAF50")
            )

            return False, error_msg

    def open_advance_ui(self):
        if (
            self.advance_ui is None
            or not hasattr(self.advance_ui, "advance_window")
            or not self.advance_ui.advance_window.winfo_exists()
        ):
            self.advance_ui = AdvanceUI(
                self.settings_window, self.settings, self.apply_settings_callback, None
            )
        self.advance_ui.open()

    def toggle_model_settings(self):
        """เปิด/ปิดหน้าต่างการตั้งค่า Model"""
        try:
            # เรียกใช้ advance_ui ที่มีการตั้งค่า Model
            if (
                self.advance_ui is None
                or not hasattr(self.advance_ui, "advance_window")
                or not self.advance_ui.advance_window.winfo_exists()
            ):
                self.advance_ui = AdvanceUI(
                    self.settings_window,
                    self.settings,
                    self.apply_settings_callback,
                    None,
                )

            # เรียกเมธอด _open_model_settings ของ advance_ui
            if hasattr(self.advance_ui, "_open_model_settings"):
                self.advance_ui._open_model_settings()
            else:
                # ถ้าไม่มีเมธอดที่ต้องการให้เปิดแบบปกติแทน
                self.advance_ui.open()

        except Exception as e:
            logging.error(f"Error in toggle_model_settings: {e}")
            messagebox.showerror("Error", f"เกิดข้อผิดพลาดในการเปิดการตั้งค่า Model: {e}")

    def toggle_font_ui(self):
        """เปิด/ปิดหน้าต่างการตั้งค่าฟอนต์"""
        try:
            # ตรวจสอบว่ามีการนำเข้า FontUI หรือไม่
            try:
                from font_manager import FontUI

                has_font_ui = True
            except ImportError:
                has_font_ui = False

            if has_font_ui:
                # สร้างหรือเปิด FontUI
                if not hasattr(self, "font_ui") or self.font_ui is None:
                    self.font_ui = FontUI(self.settings_window, self.settings)

                self.font_ui.open()
            else:
                # แจ้งเตือนหากไม่พบ FontUI
                messagebox.showinfo(
                    "Font Settings", "Font UI is not available in this version"
                )

        except Exception as e:
            logging.error(f"Error in toggle_font_ui: {e}")
            messagebox.showerror("Error", f"เกิดข้อผิดพลาดในการเปิดการตั้งค่าฟอนต์: {e}")

    def start_move_settings(self, event):
        self.settings_x = event.x
        self.settings_y = event.y

    def stop_move_settings(self, event):
        self.settings_x = None
        self.settings_y = None

    def do_move_settings(self, event):
        if hasattr(self, "settings_x") and hasattr(self, "settings_y"):
            deltax = event.x - self.settings_x
            deltay = event.y - self.settings_y
            x = self.settings_window.winfo_x() + deltax
            y = self.settings_window.winfo_y() + deltay
            self.settings_window.geometry(f"+{x}+{y}")

            # เคลื่อนย้าย SimplifiedHotkeyUI แทนที่ HotkeyUI เดิม
            if (
                hasattr(self, "simplified_hotkey_ui")
                and self.simplified_hotkey_ui
                and hasattr(self.simplified_hotkey_ui, "window")
                and self.simplified_hotkey_ui.window
                and self.simplified_hotkey_ui.window.winfo_exists()
            ):
                window = self.simplified_hotkey_ui.window
                # ตำแหน่งด้านขวา
                hotkey_x = x + self.settings_window.winfo_width() + 10
                hotkey_y = y + 50
                window.geometry(f"+{hotkey_x}+{hotkey_y}")

    def move_window(self, event):
        self.settings_window.geometry(
            f"+{event.x_root - self.last_pos[0]}+{event.y_root - self.last_pos[1]}"
        )

    def save_last_pos(self, event):
        self.last_pos = (event.x, event.y)

    def apply_settings_handler(self):
        success, error_msg = self.apply_settings()
        if not success:
            messagebox.showerror("Error", error_msg)
        else:
            feedback = tk.Label(
                self.settings_window,
                text="Settings applied!",
                bg="#1E8449",
                fg="white",
                font=("Bai Jamjuree Light", 13),
                padx=10,
                pady=5,
            )
            feedback.place(relx=0.5, rely=0.9, anchor="center")
            self.settings_window.after(2000, feedback.destroy)

    def toggle_hover_translation(self, value=None):
        """เปิด/ปิดระบบ Hover Translation"""
        try:
            # ถ้าไม่ได้ระบุค่า ให้ใช้ค่าจาก hover_translation_var
            if value is None:
                if hasattr(self, "hover_translation_var"):
                    value = self.hover_translation_var.get()
                else:
                    value = self.settings.get("enable_hover_translation", False)

            # บันทึกค่าลงใน settings
            self.settings.set("enable_hover_translation", value)

            # ถ้ามี callback สำหรับส่งต่อไปยัง MBB ให้เรียกใช้
            if (
                hasattr(self, "main_app")
                and self.main_app
                and hasattr(self.main_app, "toggle_hover_translation")
            ):
                self.main_app.toggle_hover_translation(value)
                logging.info(f"Toggled hover translation: {value}")
            else:
                logging.warning(
                    "Main app reference not found or missing toggle_hover_translation method"
                )
        except Exception as e:
            logging.error(f"Error toggling hover translation: {e}")

    def update_switch_ui(self, indicator_id, is_on):
        """อัพเดท UI ของ switch ตามสถานะใหม่ และจัดการสถานะ DISABLED"""
        if indicator_id not in self.indicators:
            return

        indicator_data = self.indicators[indicator_id]
        indicator = indicator_data["indicator"]
        bg = indicator_data["bg"]
        variable = indicator_data["variable"]  # เพิ่มการดึง variable
        x_on = indicator_data.get("x_on", 22)
        x_off = indicator_data.get("x_off", 4)
        # ดึง widget หลักของ switch (Checkbutton)
        switch_widget = None
        # หากรอบ Frame ที่สร้าง switch
        parent_frame = indicator.master
        for child in parent_frame.winfo_children():
            if isinstance(child, ttk.Checkbutton):
                switch_widget = child
                break

        # ตรวจสอบสถานะ DISABLED
        is_disabled = switch_widget and switch_widget.instate(["disabled"])

        if is_disabled:
            # ถ้า DISABLED ให้เป็นสีเทาจางๆ ทั้งคู่
            indicator.place(x=x_off)  # ตำแหน่งปิดเสมอ
            indicator.config(bg="#757575")  # สีเทาจางสำหรับตัวเลื่อน
            bg.config(bg="#424242")  # สีเทาเข้มสำหรับพื้นหลัง
        elif is_on:  # เปิด (Enabled)
            indicator.place(x=x_on)
            indicator.config(bg="white")  # สีขาวปกติ
            bg.config(bg="#4CAF50")  # สีเขียว
        else:  # ปิด (Enabled)
            indicator.place(x=x_off)
            indicator.config(bg="white")  # สีขาวปกติ
            bg.config(bg="#555555")  # สีเทาปกติ
