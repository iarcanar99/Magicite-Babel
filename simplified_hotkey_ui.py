import tkinter as tk
from tkinter import ttk
from utils_appearance import SettingsUITheme, ModernButton, ModernEntry, ModernFrame
import ctypes
import win32api
import win32con


def is_valid_hotkey(hotkey):
    hotkey = hotkey.lower()
    valid_keys = set("abcdefghijklmnopqrstuvwxyz0123456789")
    valid_functions = set(
        ["f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "f10", "f11", "f12"]
    )
    valid_modifiers = set(["ctrl", "alt", "shift"])

    parts = hotkey.split("+")

    if len(parts) == 1:
        return parts[0] in valid_keys or parts[0] in valid_functions

    if len(parts) > 1:
        modifiers = parts[:-1]
        key = parts[-1]
        return all(mod in valid_modifiers for mod in modifiers) and (
            key in valid_keys or key in valid_functions
        )

    return False


class ToolTip:
    """สร้าง Tooltip สำหรับ Widget ใน Tkinter"""

    def __init__(
        self, widget, text, bg="#1E1E1E", fg="#FFFFFF", font=("Bai Jamjuree Light", 16)
    ):
        self.widget = widget
        self.text = text
        self.bg = bg
        self.fg = fg
        self.font = font
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        """แสดง tooltip เมื่อเมาส์อยู่เหนือ widget"""
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        # สร้างหน้าต่าง Toplevel สำหรับ tooltip
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)  # ไม่แสดงขอบหน้าต่าง
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

        # สร้างเฟรมและข้อความ
        frame = tk.Frame(self.tooltip_window, bg=self.bg, bd=2, relief=tk.SOLID)
        frame.pack(fill=tk.BOTH, expand=True)

        label = tk.Label(
            frame,
            text=self.text,
            justify="left",
            bg=self.bg,
            fg=self.fg,
            font=self.font,
            wraplength=350,
            padx=10,
            pady=8,
        )
        label.pack()

    def hide_tooltip(self, event=None):
        """ซ่อน tooltip เมื่อเมาส์ออกจาก widget"""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


class SimplifiedHotkeyUI:
    """UI แสดงการตั้งค่าคีย์ลัดแบบเรียบง่าย ออกแบบใหม่เพื่อหลีกเลี่ยงปัญหาทางเทคนิค"""

    def __init__(self, parent, settings, update_callback):
        self.parent = parent
        self.settings = settings
        self.callback = update_callback
        self.window = None
        self.x = None
        self.y = None
        self.is_showing = False
        self._temp_message = None

        # Initialize theme system
        self.theme = SettingsUITheme

        # กำหนดขนาดหน้าต่างเป็นตัวแปร - ปรับความสูงให้เพียงพอ
        self.window_width = 420
        self.window_height = 450

        # StringVars for hotkey entries
        self.toggle_ui_var = tk.StringVar()
        self.start_stop_var = tk.StringVar()
        self.force_translate_var = tk.StringVar()
        self.force_translate_key_var = tk.StringVar()  # ใหม่: สำหรับ force translate keyboard hotkey

    def set_english_keyboard(self):
        """บังคับให้ใช้คีย์บอร์ดภาษาอังกฤษ"""
        try:
            # ใช้ LoadKeyboardLayout API เพื่อโหลด US English keyboard (0x0409)
            # 0x0409 คือ US English keyboard layout code
            # 0x0000 คือ default HKL_NEXT
            user32 = ctypes.WinDLL("user32", use_last_error=True)
            # 0x00000409 คือ US English keyboard
            result = user32.LoadKeyboardLayoutW("00000409", 0)

            if result:
                print("เปลี่ยนเป็นแป้นพิมพ์ภาษาอังกฤษสำเร็จ")
            else:
                print("ไม่สามารถเปลี่ยนภาษาแป้นพิมพ์ได้")

            # วิธีสำรอง: ใช้ keybd_event เพื่อจำลองการกด Alt+Shift เพื่อสลับภาษา
            # กด ALT
            win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
            # กด SHIFT
            win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)
            # ปล่อย SHIFT
            win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)
            # ปล่อย ALT
            win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)

            return True
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการเปลี่ยนภาษาแป้นพิมพ์: {e}")
            return False

    def open(self):
        """เปิดหน้าต่าง Hotkey UI"""
        try:
            if not self.window or not self.window.winfo_exists():
                self.create_window()
                self.load_current_hotkeys()
                self.position_window()
            else:
                self.window.deiconify()
                self.position_window()

            self.window.lift()
            self.is_showing = True

            # บังคับให้ใช้คีย์บอร์ดภาษาอังกฤษ
            self.set_english_keyboard()

            # แสดงข้อความแจ้งเตือนการใช้ภาษาอังกฤษ
            self.show_temp_message("โปรดใช้แป้นพิมพ์ภาษาอังกฤษเท่านั้น", 2000, "#3498DB")

        except Exception as e:
            print(f"Error opening window: {e}")
            self.show_temp_message(f"เกิดข้อผิดพลาด: {str(e)}", 2000, "#E74C3C")

    def close(self):
        """ปิดหน้าต่าง Hotkey UI"""
        try:
            if self.window and self.window.winfo_exists():
                self.window.destroy()
                self.window = None
                self.is_showing = False
            else:
                self.window = None
                self.is_showing = False
        except Exception as e:
            print(f"Error closing window: {e}")

    def create_window(self):
        """สร้างหน้าต่าง Hotkey UI แบบ Modern Design"""
        try:
            # ทำลายหน้าต่างเก่าถ้ามี
            if self.window and self.window.winfo_exists():
                self.window.destroy()

            self.window = tk.Toplevel(self.parent)
            self.window.title("Hotkey Settings")
            self.window.geometry(f"{self.window_width}x{self.window_height}")  # ใช้ตัวแปร
            self.window.overrideredirect(True)
            self.window.configure(bg=self.theme.get_color("bg_primary"))

            # เพิ่ม event เมื่อปิดหน้าต่าง
            self.window.protocol("WM_DELETE_WINDOW", self.close)

            # === Modern Title Bar Section ===
            title_frame = tk.Frame(self.window, bg=self.theme.get_color("bg_primary"))
            title_frame.pack(fill=tk.X, pady=(10, 5))

            title_label = tk.Label(
                title_frame,
                text="⌨️ ตั้งค่า Hotkey",
                bg=self.theme.get_color("bg_primary"),
                fg=self.theme.get_color("text_primary"),
                font=self.theme.get_font("title", "bold"),
            )
            title_label.pack()

            # === Simple Instructions ===
            instructions_frame = tk.Frame(self.window, bg=self.theme.get_color("bg_primary"))
            instructions_frame.pack(fill=tk.X, padx=20, pady=(5, 15))

            # คำอธิบายสั้นๆ แบบกระชับ
            desc_label = tk.Label(
                instructions_frame,
                text="💡 รองรับ: F1-F12, A-Z, 0-9, Alt/Ctrl/Shift+ปุ่ม",
                bg=self.theme.get_color("bg_primary"),
                fg=self.theme.get_color("accent"),  # ใช้สีสวยโดดเด่น
                font=self.theme.get_font("normal", "bold"),
                justify="center",
            )
            desc_label.pack()

            usage_label = tk.Label(
                instructions_frame,
                text="🎯 วิธีใช้: คลิกช่อง → กดปุ่มที่ต้องการ → Enter เพื่อบันทึก",
                bg=self.theme.get_color("bg_primary"),
                fg=self.theme.get_color("text_secondary"),
                font=self.theme.get_font("small"),
                justify="center",
            )
            usage_label.pack(pady=(3, 0))

            # === Hotkey Settings Card with Default Button ===
            hotkey_card = ModernFrame.create_card(self.window, padding="md")
            hotkey_card.pack(fill=tk.X, padx=20, pady=(5, 10))  # ลด padding ด้านบน

            # Header frame สำหรับหัวข้อและปุ่ม Default
            header_frame = tk.Frame(
                hotkey_card, bg=self.theme.get_color("bg_secondary")
            )
            header_frame.pack(fill=tk.X, pady=(0, self.theme.get_spacing("md")))

            # หัวข้อ
            title_label = tk.Label(
                header_frame,
                text="🎮 คีย์ลัดหลัก",
                bg=self.theme.get_color("bg_secondary"),
                fg=self.theme.get_color("text_primary"),
                font=self.theme.get_font("medium", "bold"),
            )
            title_label.pack(side=tk.LEFT)

            # ปุ่ม Default ด้านขวา
            self.default_button = ModernButton.create(
                header_frame, "🔄 Default", command=self.reset_to_default, width=12
            )
            self.default_button.pack(side=tk.RIGHT)

            # เพิ่ม tooltip สำหรับปุ่ม Default
            ToolTip(self.default_button, "รีเซ็ตคีย์ลัดเป็นค่าเริ่มต้น")

            # Separator line
            separator = tk.Frame(
                hotkey_card, height=1, bg=self.theme.get_color("border_light")
            )
            separator.pack(
                fill="x",
                padx=self.theme.get_spacing("md"),
                pady=(0, self.theme.get_spacing("md")),
            )

            # Toggle UI entry
            toggle_frame = tk.Frame(
                hotkey_card, bg=self.theme.get_color("bg_secondary")
            )
            toggle_frame.pack(
                fill=tk.X, pady=self.theme.get_spacing("md")
            )  # เพิ่ม spacing

            toggle_label = tk.Label(
                toggle_frame,
                text="Toggle Mini UI:",
                bg=self.theme.get_color("bg_secondary"),
                fg=self.theme.get_color("text_primary"),
                font=self.theme.get_font("normal"),
                width=15,
                anchor="w",
            )
            toggle_label.pack(side=tk.LEFT, padx=(0, 15))  # เพิ่ม spacing

            self.toggle_ui_entry = self.create_modern_hotkey_entry(
                toggle_frame, self.toggle_ui_var, "Toggle mini UI:"
            )
            self.toggle_ui_entry.pack(side=tk.RIGHT)

            # เพิ่ม tooltip สำหรับ Toggle mini UI
            ToolTip(self.toggle_ui_entry, "แนะนำให้ใช้: Alt+L")

            # Start/Stop entry
            start_frame = tk.Frame(hotkey_card, bg=self.theme.get_color("bg_secondary"))
            start_frame.pack(
                fill=tk.X, pady=self.theme.get_spacing("md")
            )  # เพิ่ม spacing

            start_label = tk.Label(
                start_frame,
                text="Start/Stop:",
                bg=self.theme.get_color("bg_secondary"),
                fg=self.theme.get_color("text_primary"),
                font=self.theme.get_font("normal"),
                width=15,
                anchor="w",
            )
            start_label.pack(side=tk.LEFT, padx=(0, 15))  # เพิ่ม spacing

            self.start_stop_entry = self.create_modern_hotkey_entry(
                start_frame, self.start_stop_var, "Start/Stop:"
            )
            self.start_stop_entry.pack(side=tk.RIGHT)

            # เพิ่ม tooltip สำหรับ Start/Stop
            ToolTip(self.start_stop_entry, "แนะนำให้ใช้: F9")

            # Force translate key entry (F1-F12 - สามารถตั้งค่าได้) - ย้ายมาไว้ที่ 3
            force_key_frame = tk.Frame(hotkey_card, bg=self.theme.get_color("bg_secondary"))
            force_key_frame.pack(
                fill=tk.X, pady=self.theme.get_spacing("md")
            )  # เพิ่ม spacing

            force_key_label = tk.Label(
                force_key_frame,
                text="Force (Key):",
                bg=self.theme.get_color("bg_secondary"),
                fg=self.theme.get_color("text_primary"),
                font=self.theme.get_font("normal"),
                width=15,
                anchor="w",
            )
            force_key_label.pack(side=tk.LEFT, padx=(0, 15))  # เพิ่ม spacing

            self.force_translate_key_entry = self.create_modern_hotkey_entry(
                force_key_frame, self.force_translate_key_var, "Force Key:"
            )
            self.force_translate_key_entry.pack(side=tk.RIGHT)

            # เพิ่ม tooltip สำหรับ Force translate key
            ToolTip(self.force_translate_key_entry, "แนะนำให้ใช้: F10")

            # Force translate entry (คลิกขวา - แสดงให้เห็นแต่แก้ไขไม่ได้) - ย้ายมาไว้ล่างสุด
            force_frame = tk.Frame(hotkey_card, bg=self.theme.get_color("bg_secondary"))
            force_frame.pack(
                fill=tk.X, pady=self.theme.get_spacing("md")
            )  # เพิ่ม spacing

            force_label = tk.Label(
                force_frame,
                text="Force (R-Click TUI):",
                bg=self.theme.get_color("bg_secondary"),
                fg=self.theme.get_color("text_secondary"),  # สีเทาเพื่อแสดงว่าแก้ไขไม่ได้
                font=self.theme.get_font("normal"),
                width=15,
                anchor="w",
            )
            force_label.pack(side=tk.LEFT, padx=(0, 15))  # เพิ่ม spacing

            # Entry แบบ disabled สำหรับ r-click
            self.force_translate_entry = tk.Entry(
                force_frame,
                textvariable=self.force_translate_var,
                width=14,
                bg=self.theme.get_color("bg_quaternary"),  # สีเทาเข้มกว่า
                fg=self.theme.get_color("text_secondary"),  # สีเทา
                font=self.theme.get_font("normal"),
                justify="center",
                relief="flat",
                bd=1,
                state="disabled",  # ไม่ให้แก้ไขได้
                highlightthickness=1,
                highlightbackground=self.theme.get_color("border_light"),
            )
            self.force_translate_entry.pack(side=tk.RIGHT)

            # เพิ่ม tooltip สำหรับ Force translate r-click
            ToolTip(self.force_translate_entry, "คลิกขวาบนหน้าต่างการแปล (TUI) เพื่อบังคับแปล")

            # === Close Button with Red Hover Effect ===
            close_button = tk.Button(
                self.window,
                text="✕",
                command=self.close,
                bg=self.theme.get_color("bg_secondary"),
                fg=self.theme.get_color("text_primary"),
                activebackground="#FF4444",  # สีแดงชัดเจนเมื่อ active
                activeforeground=self.theme.get_color("text_primary"),
                font=self.theme.get_font("normal"),
                relief="flat",
                bd=0,
                width=2,
                height=1,
                cursor="hand2",
            )
            close_button.place(x=8, y=8)

            # เก็บสีเดิมไว้ในตัวแปร
            original_bg = self.theme.get_color("bg_secondary")
            
            # เพิ่ม hover effect สีแดงสำหรับปุ่ม Close
            def on_close_enter(event):
                close_button.config(bg="#FF4444")  # สีแดงชัดเจน

            def on_close_leave(event):
                close_button.config(bg=original_bg)

            # ผูก hover events โดยตรง
            close_button.bind("<Enter>", on_close_enter)
            close_button.bind("<Leave>", on_close_leave)
            
            # ป้องกันการขัดแย้งกับ window movement - เฉพาะ motion events เท่านั้น
            def stop_motion_propagation(event):
                return "break"
            
            close_button.bind("<B1-Motion>", stop_motion_propagation)

            # === Window Movement ===
            self.window.bind("<Button-1>", self.start_move)
            self.window.bind("<ButtonRelease-1>", self.stop_move)
            self.window.bind("<B1-Motion>", self.do_move)

            # เมื่อหน้าต่างได้รับ focus ให้บังคับใช้ภาษาอังกฤษ
            self.window.bind("<FocusIn>", lambda e: self.set_english_keyboard())

        except Exception as e:
            print(f"Error creating window: {e}")

    def enforce_english_input(self, event):
        """บังคับให้ใช้ภาษาอังกฤษในการป้อนข้อมูล"""
        # ถ้าเป็นตัวอักษรที่ไม่ใช่ ASCII (เช่น ภาษาไทย) ให้ยกเลิกการป้อนและบังคับใช้ภาษาอังกฤษ
        if event.char and ord(event.char) > 127:
            self.set_english_keyboard()
            return "break"  # ยกเลิกการป้อนข้อมูล
        return None

    def create_modern_hotkey_entry(self, frame, variable, label_text):
        """สร้าง Modern Hotkey Entry Field พร้อม visual feedback"""
        entry = tk.Entry(
            frame,
            textvariable=variable,
            width=14,
            bg=self.theme.get_color("bg_tertiary"),
            fg=self.theme.get_color("text_primary"),
            insertbackground=self.theme.get_color("text_primary"),
            font=self.theme.get_font("normal"),
            justify="center",
            relief="flat",
            bd=1,
            highlightthickness=2,
            highlightbackground=self.theme.get_color("border_normal"),
            highlightcolor=self.theme.get_color("border_focus"),
        )

        # ตัวแปรเก็บสถานะการรอรับปุ่มกด
        entry.is_listening = False
        # ตัวแปรเก็บค่า modifier keys ที่กดอยู่
        entry.modifiers = set()
        # ตัวแปรเก็บค่าปุ่มหลักที่กด
        entry.key_pressed = None

        def on_entry_click(event):
            """เมื่อคลิกที่ Entry"""
            # เลือกข้อความทั้งหมดทันทีเมื่อคลิก
            entry.select_range(0, tk.END)
            entry.focus_set()

            # เปลี่ยนสีพื้นหลังเป็นสี focus
            entry.config(bg=self.theme.get_color("hover_light"))

            # เข้าสู่โหมดรอรับปุ่มกด
            entry.is_listening = True
            entry.delete(0, tk.END)
            entry.insert(0, "⌨️ กำลังรอรับปุ่ม...")

            # บังคับใช้ภาษาอังกฤษ
            self.set_english_keyboard()

        def on_key_press(event):
            """เมื่อกดปุ่มใดๆ ในโหมดรอรับปุ่มกด"""
            # ถ้าไม่ได้อยู่ในโหมดรอรับปุ่มกด ให้ทำงานปกติ
            if not entry.is_listening:
                return

            # ตรวจสอบภาษา
            self.enforce_english_input(event)

            key = event.keysym.lower()

            # กรณีกด Escape ให้ยกเลิกการแก้ไข
            if key == "escape":
                entry.is_listening = False
                entry.delete(0, tk.END)
                entry.insert(0, self.get_original_value(label_text))
                entry.select_clear()
                entry.config(bg=self.theme.get_color("bg_tertiary"))
                self.window.focus_set()
                return "break"

            # รายการ modifier keys
            modifiers = {
                "control_l",
                "control_r",
                "alt_l",
                "alt_r",
                "shift_l",
                "shift_r",
            }

            # กรณีกด modifier key
            if key in modifiers:
                # แปลงชื่อปุ่มให้อ่านง่าย
                if "control" in key:
                    entry.modifiers.add("ctrl")
                elif "alt" in key:
                    entry.modifiers.add("alt")
                elif "shift" in key:
                    entry.modifiers.add("shift")

                # แสดงผล modifier ที่กดอยู่ + visual feedback
                display_text = "+".join(sorted(entry.modifiers))
                if display_text:
                    display_text += "+"
                entry.delete(0, tk.END)
                entry.insert(0, display_text)
                entry.config(bg=self.theme.get_color("success"))  # สีเขียวเมื่อกด modifier

                return "break"

            # กรณีกดปุ่ม F1-F12
            if key.startswith("f") and key[1:].isdigit() and 1 <= int(key[1:]) <= 12:
                entry.key_pressed = key

                # สร้าง hotkey จาก modifier + key
                hotkey_parts = list(sorted(entry.modifiers))
                hotkey_parts.append(key)
                hotkey = "+".join(hotkey_parts)

                # บันทึกค่า + visual feedback
                entry.delete(0, tk.END)
                entry.insert(0, hotkey)
                entry.config(bg=self.theme.get_color("success"))  # สีเขียวเมื่อสำเร็จ

                # ออกจากโหมดรอรับปุ่มกดและ inactive entry
                entry.is_listening = False
                entry.modifiers = set()
                entry.key_pressed = None
                entry.config(state=tk.DISABLED)  # inactive entry

                # บันทึก hotkey
                self.save_single_hotkey(label_text, hotkey)

                # คืนค่าสีปกติและ active entry หลัง 1.5 วินาที
                self.window.after(
                    1500,
                    lambda: (
                        entry.config(
                            bg=self.theme.get_color("bg_tertiary"), state=tk.NORMAL
                        )
                    ),
                )

                return "break"

            # กรณีกดปุ่มอักษร a-z, 0-9
            if (len(key) == 1 and key.isalnum()) or key == "r-click":
                entry.key_pressed = key

                # สร้าง hotkey จาก modifier + key
                hotkey_parts = list(sorted(entry.modifiers))
                hotkey_parts.append(key)
                hotkey = "+".join(hotkey_parts)

                # บันทึกค่า + visual feedback
                entry.delete(0, tk.END)
                entry.insert(0, hotkey)
                entry.config(bg=self.theme.get_color("success"))  # สีเขียวเมื่อสำเร็จ

                # ออกจากโหมดรอรับปุ่มกดและ inactive entry
                entry.is_listening = False
                entry.modifiers = set()
                entry.key_pressed = None
                entry.config(state=tk.DISABLED)  # inactive entry

                # บันทึก hotkey
                self.save_single_hotkey(label_text, hotkey)

                # คืนค่าสีปกติและ active entry หลัง 1.5 วินาที
                self.window.after(
                    1500,
                    lambda: (
                        entry.config(
                            bg=self.theme.get_color("bg_tertiary"), state=tk.NORMAL
                        )
                    ),
                )

                return "break"

            # กรณีกด Enter เพื่อบันทึก (ถ้ามี hotkey ใน entry)
            if key == "return":
                current_value = entry.get()
                if (
                    current_value
                    and current_value != "⌨️ กำลังรอรับปุ่ม..."
                    and is_valid_hotkey(current_value)
                ):
                    # บันทึก hotkey + visual feedback
                    entry.config(bg=self.theme.get_color("success"))
                    entry.config(state=tk.DISABLED)  # inactive entry

                    # บันทึก hotkey
                    self.save_single_hotkey(label_text, current_value)

                    # ออกจากโหมดรอรับปุ่มกด
                    entry.is_listening = False
                    entry.modifiers = set()
                    entry.key_pressed = None

                    # คืนค่าสีปกติและ active entry หลัง 1.5 วินาที
                    self.window.after(
                        1500,
                        lambda: (
                            entry.config(
                                bg=self.theme.get_color("bg_tertiary"), state=tk.NORMAL
                            )
                        ),
                    )
                else:
                    # ถ้าไม่มีค่าหรือค่าไม่ถูกต้อง ให้ยกเลิก
                    entry.is_listening = False
                    entry.delete(0, tk.END)
                    entry.insert(0, self.get_original_value(label_text))
                    entry.select_clear()
                    entry.config(bg=self.theme.get_color("bg_tertiary"))
                    self.window.focus_set()

                return "break"

            # ถ้าไม่ใช่ปุ่มที่ใช้งานได้ ให้ยกเลิก
            return "break"

        def on_key_release(event):
            """เมื่อปล่อยปุ่มใดๆ ในโหมดรอรับปุ่มกด"""
            if not entry.is_listening:
                return

            key = event.keysym.lower()

            # รายการ modifier keys
            modifiers = {
                "control_l",
                "control_r",
                "alt_l",
                "alt_r",
                "shift_l",
                "shift_r",
            }

            # กรณีปล่อย modifier key
            if key in modifiers:
                # ลบ modifier ที่ปล่อยแล้วออกจากรายการ
                if "control" in key and "ctrl" in entry.modifiers:
                    entry.modifiers.remove("ctrl")
                elif "alt" in key and "alt" in entry.modifiers:
                    entry.modifiers.remove("alt")
                elif "shift" in key and "shift" in entry.modifiers:
                    entry.modifiers.remove("shift")

                # แสดงผล modifier ที่กดอยู่
                display_text = "+".join(sorted(entry.modifiers))
                if display_text:
                    display_text += "+"
                entry.delete(0, tk.END)
                entry.insert(0, display_text)

                # คืนค่าสีปกติถ้าไม่มี modifier
                if not entry.modifiers:
                    entry.config(bg=self.theme.get_color("hover_light"))

                return "break"

        def on_focus_out(event):
            """เมื่อ focus ออกจาก Entry"""
            entry.select_clear()
            entry.is_listening = False
            entry.config(bg=self.theme.get_color("bg_tertiary"))

            # ถ้าข้อความเป็น "กำลังรอรับปุ่ม..." หรือไม่มีการตั้งค่า ให้คืนค่าเดิม
            if "กำลังรอรับปุ่ม" in entry.get() or not entry.get():
                entry.delete(0, tk.END)
                entry.insert(0, self.get_original_value(label_text))

        # ผูก events
        entry.bind("<FocusIn>", on_entry_click)
        entry.bind("<Button-1>", on_entry_click)  # เพิ่ม event เมื่อคลิกเมาส์ให้ highlight ทันที
        entry.bind("<KeyPress>", on_key_press)
        entry.bind("<KeyRelease>", on_key_release)
        entry.bind("<FocusOut>", on_focus_out)

        # บังคับใช้ภาษาอังกฤษเมื่อมีการเปลี่ยน focus ไปที่ entry นี้
        entry.bind(
            "<FocusIn>", lambda e: (on_entry_click(e), self.set_english_keyboard())
        )

        return entry

    def load_current_hotkeys(self):
        """โหลดค่า hotkey ปัจจุบัน"""
        toggle_ui = self.settings.get_shortcut("toggle_ui", "alt+h")
        start_stop = self.settings.get_shortcut("start_stop_translate", "f9")
        force_translate = self.settings.get_shortcut("force_translate", "r-click")
        force_translate_key = self.settings.get_shortcut("force_translate_key", "f10")  # ใหม่

        self.toggle_ui_var.set(toggle_ui)
        self.start_stop_var.set(start_stop)
        self.force_translate_var.set(force_translate)
        self.force_translate_key_var.set(force_translate_key)  # ใหม่

    def reset_to_default(self):
        """รีเซ็ตค่าเป็นค่าเริ่มต้นและบันทึกทันที"""
        # ค่าเริ่มต้น
        default_values = {
            "toggle_ui": "alt+l",
            "start_stop_translate": "f9", 
            "force_translate": "r-click",
            "force_translate_key": "f10"  # ใหม่
        }
        
        # ตั้งค่าใน variables
        self.toggle_ui_var.set(default_values["toggle_ui"])
        self.start_stop_var.set(default_values["start_stop_translate"])
        self.force_translate_var.set(default_values["force_translate"])
        self.force_translate_key_var.set(default_values["force_translate_key"])  # ใหม่

        # อัพเดต entries ให้แสดงค่าใหม่
        if hasattr(self, "toggle_ui_entry"):
            self.toggle_ui_entry.delete(0, tk.END)
            self.toggle_ui_entry.insert(0, default_values["toggle_ui"])
        if hasattr(self, "start_stop_entry"):
            self.start_stop_entry.delete(0, tk.END)
            self.start_stop_entry.insert(0, default_values["start_stop_translate"])
        if hasattr(self, "force_translate_entry"):
            self.force_translate_entry.config(state="normal")  # เปิดชั่วคราวเพื่อแก้ไข
            self.force_translate_entry.delete(0, tk.END)
            self.force_translate_entry.insert(0, default_values["force_translate"])
            self.force_translate_entry.config(state="disabled")  # ปิดกลับ
        if hasattr(self, "force_translate_key_entry"):  # ใหม่
            self.force_translate_key_entry.delete(0, tk.END)
            self.force_translate_key_entry.insert(0, default_values["force_translate_key"])

        # *** ใหม่: บันทึกค่าลง settings ทันที ***
        try:
            for key, value in default_values.items():
                self.settings.set_shortcut(key, value)
            
            # เรียก callback เพื่ออัพเดตระบบ
            if self.callback:
                self.callback()
                
            # ยกเลิก focus จาก entry ทั้งหมด
            self.clear_entry_focus()
            
            # แสดงข้อความสำเร็จ
            self.show_temp_message(
                "✅ รีเซ็ตและบันทึกค่าเริ่มต้นแล้ว!", 1500, self.theme.get_color("success")
            )
            
        except Exception as e:
            # แสดงข้อความแจ้งเตือนกรณีเกิดข้อผิดพลาด
            self.show_temp_message(
                f"⚠️ เกิดข้อผิดพลาดในการบันทึก: {str(e)}", 2000, self.theme.get_color("error")
            )

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.x = None
        self.y = None

    def do_move(self, event):
        if self.x is not None and self.y is not None:
            deltax = event.x - self.x
            deltay = event.y - self.y
            x = self.window.winfo_x() + deltax
            y = self.window.winfo_y() + deltay
            # ต้องเก็บขนาดหน้าต่างไว้ด้วยเมื่อลาก
            self.window.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")

    def get_original_value(self, label_text):
        """รับค่าเดิมตาม label"""
        if "Toggle mini UI" in label_text:
            return self.settings.get_shortcut("toggle_ui", "alt+h")
        elif "Start/Stop" in label_text:
            return self.settings.get_shortcut("start_stop_translate", "f9")
        elif "Force Key" in label_text:  # ใหม่
            return self.settings.get_shortcut("force_translate_key", "f10")
        elif "Force" in label_text:
            return self.settings.get_shortcut("force_translate", "r-click")
        return ""

    def save_single_hotkey(self, label_text, value):
        """บันทึกคีย์ลัดเดี่ยว"""
        try:
            if "Toggle mini UI" in label_text:
                self.settings.set_shortcut("toggle_ui", value.lower())
            elif "Start/Stop" in label_text:
                self.settings.set_shortcut("start_stop_translate", value.lower())
            elif "Force Key" in label_text:  # ใหม่
                self.settings.set_shortcut("force_translate_key", value.lower())
            elif "Force" in label_text:
                self.settings.set_shortcut("force_translate", value.lower())

            if self.callback:
                self.callback()

            # แสดงข้อความสำเร็จชั่วคราว
            self.show_temp_message("✅ บันทึกแล้ว!", 1000, self.theme.get_color("success"))
            
            # *** แก้ไข: ยกเลิก focus จาก entry หลังบันทึก ***
            self.clear_entry_focus()

        except Exception as e:
            # แสดงข้อความแจ้งเตือนกรณีเกิดข้อผิดพลาด
            self.show_temp_message(
                f"⚠️ เกิดข้อผิดพลาด: {str(e)}", 2000, self.theme.get_color("error")
            )
            
    def clear_entry_focus(self):
        """ยกเลิก focus จาก entry ทั้งหมดหลังบันทึก"""
        try:
            # ให้ focus ไปที่หน้าต่างหลักแทน
            self.window.focus_set()
            
            # clear focus จาก entry ทั้งหมด
            for entry in [self.toggle_ui_entry, self.start_stop_entry, self.force_translate_entry, self.force_translate_key_entry]:  # เพิ่ม entry ใหม่
                if hasattr(self, entry.winfo_name()) and entry.winfo_exists():
                    entry.select_clear()  # ยกเลิกการเลือกข้อความ
                    
        except Exception:
            pass  # ไม่ให้ error ขัดขวางการทำงาน

    def show_temp_message(self, message, duration=1500, color="#4CAF50", font_size=12):
        """แสดงข้อความชั่วคราวด้านล่างของหน้าต่างแบบ Modern

        Args:
            message: ข้อความที่ต้องการแสดง
            duration: ระยะเวลาที่แสดง (ms)
            color: สีพื้นหลัง (success: #4CAF50, error: #F44336, warning: #FF9800)
            font_size: ขนาดตัวอักษร
        """
        # ลบข้อความเก่า ถ้ามี
        if hasattr(self, "_temp_message") and self._temp_message is not None:
            try:
                self._temp_message.destroy()
            except:
                pass

        # สร้างข้อความใหม่แบบ Modern
        self._temp_message = tk.Label(
            self.window,
            text=message,
            bg=color,
            fg=self.theme.get_color("text_primary"),
            font=self.theme.get_font("normal"),
            padx=self.theme.get_spacing("md"),
            pady=self.theme.get_spacing("sm"),
            relief="flat",
            bd=0,
        )
        self._temp_message.place(relx=0.5, rely=0.92, anchor="center")

        # กำหนดเวลาให้หายไป
        self.window.after(duration, self._hide_temp_message)

    def _hide_temp_message(self):
        """ซ่อนข้อความชั่วคราว"""
        if hasattr(self, "_temp_message") and self._temp_message is not None:
            self._temp_message.destroy()
            self._temp_message = None

    def position_window(self):
        """จัดตำแหน่งหน้าต่างให้อยู่ด้านขวาของ settings"""
        if self.parent and self.window:
            # รับตำแหน่งและขนาดของ parent (settings window)
            parent_x = self.parent.winfo_x()
            parent_y = self.parent.winfo_y()
            parent_width = self.parent.winfo_width()

            # กำหนดตำแหน่งใหม่ แต่เก็บขนาดเดิมไว้
            new_x = parent_x + parent_width + 10  # ห่างจากขอบขวา 10 pixels
            new_y = parent_y  # ความสูงเดียวกับ parent

            # ใช้ขนาดเดียวกันกับ create_window()
            self.window.geometry(
                f"{self.window_width}x{self.window_height}+{new_x}+{new_y}"
            )
