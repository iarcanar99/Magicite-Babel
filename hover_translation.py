import tkinter as tk
import threading
import time
import logging
from pynput import mouse
import json
import win32api
import win32con


class HoverTranslator:
    """
    คลาสสำหรับระบบ Hover Translation ที่ช่วยให้ผู้ใช้สามารถเปลี่ยน preset โดยการเลื่อนเมาส์ไปยังพื้นที่ที่ต้องการ
    ทำงานผ่านระบบ preset เท่านั้น ไม่ยุ่งกับ translation loop
    
    [Updated] ใช้ Overlay Canvas Method เพื่อแก้ปัญหา taskbar โผล่ในเกม fullscreen
    """

    def __init__(self, root, settings, callbacks, control_ui_instance):
        self.root = root
        self.settings = settings
        self.callbacks = callbacks
        self.control_ui = control_ui_instance
        if self.control_ui is None:
            logging.error(
                "HoverTranslator FATAL: Control UI instance received is None!"
            )
            self.enabled = False
        else:
            logging.info(
                f"HoverTranslator initialized with Control UI instance: {self.control_ui}"
            )
            if not hasattr(self.control_ui, "select_preset"):
                logging.error(
                    "HoverTranslator FATAL: Provided Control UI instance does NOT have 'select_preset' method!"
                )

        # สถานะเริ่มต้น
        self.enabled = False
        self.is_processing = False
        self.last_processed_time = 0
        self.last_processed_preset = None
        
        # ### ระบบ Preset Selection สำหรับ Hover ###
        # กำหนด preset ที่อนุญาตให้ hover (ค่าเริ่มต้นเฉพาะ core presets)
        self.allowed_hover_presets = {1: True, 2: True, 3: True, 4: False, 5: False, 6: False}
        self.load_hover_preset_settings()  # โหลดจาก settings
        # ### สิ้นสุดส่วนตัวแปร Preset Selection ###
        
        # Settings UI instance
        self.settings_ui = None
        
        # ### [NEW] ตัวแปรสำหรับระบบ Overlay Canvas ###
        self.overlay_window = None
        self.overlay_canvas = None
        self.button_items = {}  # เก็บ canvas items ของปุ่ม {preset_num: {rect, text, bounds}}
        # ### สิ้นสุดส่วนตัวแปรใหม่ ###
        
        # ### [NEW v1.1] ตัวแปรสำหรับ State Management เพื่อป้องกันการกระพริบ ###
        self.current_displayed_preset = None  # preset ที่ปุ่มแสดงอยู่ปัจจุบัน
        self.current_hover_preset = None      # preset ที่เมาส์อยู่ปัจจุบัน
        self.is_button_displayed = False      # สถานะว่าปุ่มแสดงอยู่หรือไม่
        # ### สิ้นสุดส่วนตัวแปร State Management ###
        
        # ### ตัวแปรสำหรับระบบ Debounce Timer (ปรับปรุงสำหรับ Canvas) ###
        self.hover_enter_timer = None       # เก็บ ID ของ timer ที่จะแสดงปุ่ม
        self.pending_preset_num = None      # เก็บ preset ที่กำลังรอการยืนยัน
        self.button_hide_timer = None       # เก็บ ID ของ timer สำหรับซ่อนปุ่ม
        # ### สิ้นสุดส่วนตัวแปรใหม่ ###
        
        # ### [NEW] ตัวแปรสำหรับ 3-second Auto-Hide Timer ###
        self.auto_hide_timer = None         # เก็บ ID ของ timer สำหรับ auto-hide 3 วินาที
        self.is_mouse_on_button = False     # สถานะว่าเมาส์อยู่บนปุ่มหรือไม่
        # ### สิ้นสุดตัวแปร Auto-Hide Timer ###
        
        # ### [NEW v1.3] ตัวแปรสำหรับการแปลต่อเนื่อง ###
        self.last_button_bounds = None      # เก็บตำแหน่งปุ่มล่าสุด (x1, y1, x2, y2)
        self.last_button_preset = None      # เก็บ preset ของปุ่มล่าสุด
        self.continuous_translation_timer = None  # timer สำหรับตรวจจับการแปลต่อเนื่อง
        # ### สิ้นสุดตัวแปรการแปลต่อเนื่อง ###
        
        # ### [NEW] Cache สำหรับ performance ###
        self._scale_cache = None
        self._scale_cache_time = 0
        # ### สิ้นสุด Cache ###

        self.immunity_time = 3.0
        self.display_time = 2.0
        self.fade_duration = 0.5
        self.hover_windows = {}
        self.fade_jobs = {}
        self.mouse_listener = None
        self.last_mouse_pos = (0, 0)
        
        # ### ปรับเปลี่ยนจาก core_preset_roles เป็น dynamic mapping ###
        self.allowed_preset_mapping = {}  # เปลี่ยนชื่อให้ชัดเจน
        # ### สิ้นสุดการปรับเปลี่ยน ###
        
        self.processing_thread = None
        self.thread_active = False

        self.update_preset_data()
        logging.debug("HoverTranslator __init__ complete.")

    def load_hover_preset_settings(self):
        """โหลดการตั้งค่า preset ที่อนุญาตสำหรับ hover จาก settings"""
        try:
            # อ่านจาก settings.json ถ้ามี
            hover_settings = self.settings.get("hover_preset_settings", {})
            if hover_settings:
                # แปลง string keys เป็น integer keys สำหรับ Python
                converted_settings = {}
                for key, value in hover_settings.items():
                    try:
                        int_key = int(key)
                        converted_settings[int_key] = value
                    except (ValueError, TypeError):
                        logging.warning(f"Invalid key in hover_preset_settings: {key}")
                
                self.allowed_hover_presets.update(converted_settings)
                logging.info(f"Loaded hover preset settings: {self.allowed_hover_presets}")
            else:
                # ใช้ค่าเริ่มต้น และบันทึกลง settings
                self.save_hover_preset_settings()
                logging.info(f"Using default hover preset settings: {self.allowed_hover_presets}")
        except Exception as e:
            logging.error(f"Error loading hover preset settings: {e}")

    def save_hover_preset_settings(self):
        """บันทึกการตั้งค่า preset ที่อนุญาตสำหรับ hover ลง settings"""
        try:
            # แปลง integer keys เป็น string keys สำหรับ JSON compatibility
            json_compatible_settings = {}
            for key, value in self.allowed_hover_presets.items():
                json_compatible_settings[str(key)] = value
            
            self.settings.set("hover_preset_settings", json_compatible_settings)
            logging.info(f"Saved hover preset settings: {self.allowed_hover_presets}")
        except Exception as e:
            logging.error(f"Error saving hover preset settings: {e}")

    def update_allowed_preset(self, preset_num, enabled):
        """อัพเดทการเปิด/ปิด hover สำหรับ preset ที่ระบุ"""
        if preset_num in self.allowed_hover_presets:
            self.allowed_hover_presets[preset_num] = enabled
            self.save_hover_preset_settings()
            self.update_preset_data()  # อัพเดท mapping ใหม่
            logging.info(f"Updated hover preset {preset_num}: {'enabled' if enabled else 'disabled'}")
            return True
        return False

    def open_settings_ui(self):
        """เปิดหน้าต่างตั้งค่า hover presets"""
        logging.info("HoverTranslator.open_settings_ui called")
        
        # สร้าง settings UI ใหม่เสมอ
        self.settings_ui = HoverSettingsUI(self.root, self, self.settings)
        self.settings_ui.show()
        
        return self.settings_ui

    def update_preset_data(self):
        """อัพเดทข้อมูล preset จาก settings ตาม allowed_hover_presets"""
        try:
            self.allowed_preset_mapping = {}
            all_presets = self.settings.get_all_presets()

            for idx, preset in enumerate(all_presets):
                preset_num = idx + 1
                
                # ตรวจสอบว่า preset นี้อนุญาตให้ hover หรือไม่
                if not self.allowed_hover_presets.get(preset_num, False):
                    continue
                    
                areas_str = preset.get("areas", "")
                coordinates = preset.get("coordinates", {})

                if areas_str and coordinates:
                    self.allowed_preset_mapping[preset_num] = {
                        "role": preset.get("role", ""),
                        "name": preset.get("name", f"Preset {preset_num}"),
                        "custom_name": preset.get("custom_name", ""),
                        "areas": areas_str.split("+"),
                        "coordinates": coordinates,
                    }

            logging.info(
                f"Updated allowed preset mapping: {len(self.allowed_preset_mapping)} allowed presets found"
            )
        except Exception as e:
            logging.error(f"Error updating preset data: {e}")

    def force_update_preset_data(self):
        """
        บังคับอัพเดทข้อมูล preset ทันที
        เรียกใช้ฟังก์ชันนี้เมื่อมีการเปลี่ยนแปลงพื้นที่ในหน้า control_ui
        """
        try:
            # อัพเดทข้อมูล preset
            self.update_preset_data()

            # เคลียร์สถานะเดิม เพื่อให้ระบบทำงานใหม่กับพื้นที่ที่อัพเดทแล้ว
            self.current_hover_area = None
            self.is_processing = False
            self.clear_hover_windows()
            # [NEW] เคลียร์ overlay canvas ด้วย
            self.hide_confirmation_button()
            # ### [NEW v1.1] รีเซ็ตสถานะ hover เมื่ออัพเดท preset ###
            self.reset_hover_state()
            # ### สิ้นสุดการรีเซ็ตสถานะ ###

            logging.info("Forced update of preset data completed")
            return True
        except Exception as e:
            logging.error(f"Error in force_update_preset_data: {e}")
            return False

    def toggle(self, enabled=None):
        """เปิด/ปิดระบบ Hover Translation"""
        if enabled is not None:
            self.enabled = enabled
        else:
            self.enabled = not self.enabled

        logging.info(
            f"HoverTranslator toggle called. Setting enabled state to: {self.enabled}"
        )

        if self.enabled:
            if self.control_ui is None:
                logging.error(
                    "Cannot enable HoverTranslator: Control UI instance is missing."
                )
                self.enabled = False
                return self.enabled

            logging.info("Hover Translation enabling...")
            self.update_preset_data()
            # [NEW] สร้าง overlay window เมื่อเปิดใช้งาน
            self.create_overlay_window()
            self.start_mouse_tracking()
        else:
            logging.info("Hover Translation disabling...")
            self.stop_mouse_tracking()
            self.clear_hover_windows()
            self.hide_confirmation_button() # เคลียร์ปุ่มยืนยัน
            # [NEW] ทำลาย overlay window เมื่อปิดใช้งาน
            self.destroy_overlay_window()
            # ### [NEW v1.1] รีเซ็ตสถานะเมื่อปิดระบบ ###
            self.reset_hover_state()
            # ### สิ้นสุดการรีเซ็ตสถานะ ###

        logging.info(
            f"Hover Translation final enabled state: {self.enabled}"
        )
        return self.enabled

    def reset_hover_state(self):
        """[v1.3] รีเซ็ตสถานะ hover ทั้งหมดเมื่อปิดระบบ"""
        self.current_displayed_preset = None
        self.current_hover_preset = None
        self.is_button_displayed = False
        self.pending_preset_num = None
        # ### [NEW] รีเซ็ตสถานะ Auto-Hide Timer ###
        self.is_mouse_on_button = False
        if self.auto_hide_timer:
            self.root.after_cancel(self.auto_hide_timer)
            self.auto_hide_timer = None
        # ### สิ้นสุดการรีเซ็ต Auto-Hide ###
        # ### [NEW v1.3] รีเซ็ตสถานะการแปลต่อเนื่อง ###
        self.last_button_bounds = None
        self.last_button_preset = None
        if self.continuous_translation_timer:
            self.root.after_cancel(self.continuous_translation_timer)
            self.continuous_translation_timer = None
        # ### สิ้นสุดการรีเซ็ตการแปลต่อเนื่อง ###
        logging.debug("Hover state reset completed with all timers cleared")

    # ### [NEW] ฟังก์ชันสำหรับ Overlay Canvas System ###
    
    def cleanup(self):
        """ล้าง resources ทั้งหมดอย่างปลอดภัย"""
        try:
            logging.info("Starting HoverTranslator cleanup...")
            
            # หยุดการทำงานก่อน
            self.enabled = False
            
            # หยุด mouse tracking
            self.stop_mouse_tracking()
            
            # ทำลาย overlay window
            self.destroy_overlay_window()
            
            # รีเซ็ตสถานะทั้งหมด
            self.reset_hover_state()
            
            # ล้าง cache
            self._scale_cache = None
            self._scale_cache_time = 0
            
            # ปิด settings UI ถ้าเปิดอยู่
            if hasattr(self, 'settings_ui') and self.settings_ui:
                if hasattr(self.settings_ui, 'close'):
                    self.settings_ui.close()
                self.settings_ui = None
            
            logging.info("HoverTranslator cleanup completed")
        except Exception as e:
            logging.error(f"Error during HoverTranslator cleanup: {e}")
    
    def get_cached_screen_scale(self):
        """ดึงค่า screen scale แบบมี cache เพื่อประสิทธิภาพ"""
        try:
            current_time = time.time()
            # Cache เป็นเวลา 1 วินาที
            if self._scale_cache and current_time - self._scale_cache_time < 1.0:
                return self._scale_cache
            
            # ดึงค่าใหม่และเก็บ cache
            self._scale_cache = self.callbacks.get("get_screen_scale", lambda: (1, 1))()
            self._scale_cache_time = current_time
            return self._scale_cache
        except Exception as e:
            logging.error(f"Error getting screen scale: {e}")
            return (1, 1)
    
    def create_overlay_window(self):
        """สร้าง transparent overlay window คลุมทั้งหน้าจอ"""
        if self.overlay_window and self.overlay_window.winfo_exists():
            logging.debug("Overlay window already exists")
            return
            
        try:
            self.overlay_window = tk.Toplevel(self.root)
            self.overlay_window.withdraw()  # ซ่อนก่อน
            self.overlay_window.overrideredirect(True)
            
            # ตั้งค่าให้คลุมทั้งหน้าจอ
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            self.overlay_window.geometry(f"{screen_width}x{screen_height}+0+0")
            
            # ทำให้โปร่งใสและ click-through (ยกเว้นตำแหน่งปุ่ม)
            self.overlay_window.attributes("-alpha", 0.05)  # เพิ่มจาก 0.01 เพื่อให้ Windows รับ click ได้ดีขึ้น
            self.overlay_window.attributes("-topmost", True)
            self.overlay_window.attributes("-transparentcolor", "black")
            
            # สร้าง canvas
            self.overlay_canvas = tk.Canvas(
                self.overlay_window, 
                bg="black", 
                highlightthickness=0,
                width=screen_width,
                height=screen_height
            )
            self.overlay_canvas.pack(fill="both", expand=True)
            
            # Bind click event
            self.overlay_canvas.bind("<Button-1>", self.on_canvas_click)
            
            # แสดง overlay (จะมองไม่เห็นเพราะโปร่งใส)
            self.overlay_window.deiconify()
            self.overlay_window.update_idletasks()
            
            logging.info("Overlay window created successfully")
            
        except Exception as e:
            logging.error(f"Error creating overlay window: {e}")
            self.overlay_window = None
            self.overlay_canvas = None
    
    def destroy_overlay_window(self):
        """[v1.1] ทำลาย overlay window และรีเซ็ตสถานะ"""
        try:
            if self.overlay_window and self.overlay_window.winfo_exists():
                self.overlay_window.destroy()
            self.overlay_window = None
            self.overlay_canvas = None
            self.button_items = {}
            # ### [NEW v1.1] รีเซ็ตสถานะเมื่อทำลาย overlay ###
            self.current_displayed_preset = None
            self.current_hover_preset = None
            self.is_button_displayed = False
            # ### สิ้นสุดการรีเซ็ตสถานะ ###
            logging.info("Overlay window destroyed and state reset")
        except Exception as e:
            logging.error(f"Error destroying overlay window: {e}")
    
    def on_canvas_click(self, event):
        """จัดการ click บน canvas"""
        try:
            x, y = event.x, event.y
            logging.debug(f"Canvas clicked at ({x}, {y})")
            
            # ตรวจสอบว่าคลิกบนปุ่มไหน
            for preset_num, button_data in self.button_items.items():
                if "bounds" in button_data:
                    x1, y1, x2, y2 = button_data["bounds"]
                    if x1 <= x <= x2 and y1 <= y <= y2:
                        logging.info(f"Canvas button clicked for preset {preset_num}")
                        self.confirm_preset_switch(preset_num)
                        break
            else:
                logging.debug(f"Canvas clicked outside button area: ({x}, {y})")
        except Exception as e:
            logging.error(f"Error in on_canvas_click: {e}", exc_info=True)
    
    # ### สิ้นสุดฟังก์ชัน Overlay Canvas System ###

    def start_mouse_tracking(self):
        """เริ่มต้นการติดตามตำแหน่งเมาส์"""
        if self.mouse_listener is None or not self.mouse_listener.is_alive():
            try:
                logging.debug("Attempting to start mouse listener...")
                self.mouse_listener = mouse.Listener(on_move=self.on_mouse_move)
                self.mouse_listener.start()
                
                if self.mouse_listener.is_alive():
                    logging.info("Mouse listener started successfully.")
                else:
                    logging.error("Mouse listener failed to start!")
                    self.mouse_listener = None
                    return

                # เริ่ม thread สำหรับการประมวลผล
                self.thread_active = True
                self.processing_thread = threading.Thread(
                    target=self.processing_loop,
                    daemon=True,
                    name="HoverProcessingThread",
                )
                self.processing_thread.start()
                logging.info(
                    f"Hover processing thread started (ID: {self.processing_thread.ident})."
                )
            except Exception as e:
                logging.error(
                    f"Error starting mouse tracking: {e}", exc_info=True
                )
                # Reset สถานะถ้าเกิดข้อผิดพลาด
                if self.mouse_listener:
                    try:
                        self.mouse_listener.stop()
                    except:
                        pass
                    self.mouse_listener = None
                self.thread_active = False
                self.processing_thread = None
        else:
            logging.warning("Mouse listener already running.")

    def stop_mouse_tracking(self):
        """หยุดการติดตามตำแหน่งเมาส์"""
        try:
            self.thread_active = False
            if self.processing_thread and self.processing_thread.is_alive():
                self.processing_thread.join(timeout=1.0)
            self.processing_thread = None

            if self.mouse_listener and self.mouse_listener.is_alive():
                self.mouse_listener.stop()
                self.mouse_listener.join()
            self.mouse_listener = None
            
            # เรียกใช้ hide เพื่อเคลียร์ทุกอย่างที่เกี่ยวข้องกับปุ่มและ timer
            self.hide_confirmation_button()
            
            logging.info("Mouse tracking stopped completely.")
        except Exception as e:
            logging.error(
                f"Error stopping mouse tracking: {e}", exc_info=True
            )
            self.processing_thread = None
            self.mouse_listener = None

    def on_mouse_move(self, x, y):
        """callback เมื่อเมาส์เคลื่อนที่"""
        logging.debug(f"Mouse moved: ({x}, {y})")
        if not self.enabled:
            return
        self.last_mouse_pos = (x, y)

    def processing_loop(self):
        """[v1.1] loop การประมวลผลที่ทำงานใน thread แยก - ปรับปรุงประสิทธิภาพ"""
        logging.info("Hover processing loop starting.")
        while self.thread_active:
            logging.debug("Hover processing loop tick.")
            try:
                # ### [NEW v1.1] ข้ามการตรวจสอบถ้าไม่จำเป็น ###
                if self.should_skip_processing():
                    time.sleep(0.2)  # หน่วงเวลานานขึ้นเมื่อไม่ต้องทำงาน
                    continue
                # ### สิ้นสุดการตรวจสอบการข้าม ###
                
                if self.enabled and hasattr(self, "last_mouse_pos"):
                    self.check_mouse_position(
                        self.last_mouse_pos[0], self.last_mouse_pos[1]
                    )
                else:
                    logging.debug(
                        f"Skipping check_mouse_position (enabled={self.enabled}, has_last_pos={hasattr(self, 'last_mouse_pos')})"
                    )
                    pass
            except Exception as e:
                logging.error(
                    f"Error in processing loop iteration: {e}", exc_info=True
                )

            time.sleep(0.10)  # ลดจาก 150ms เป็น 100ms เพื่อตอบสนองเร็วขึ้นในการสลับพื้นที่
        logging.info("Hover processing loop finished.")

    def should_skip_processing(self):
        """[v1.3] ตรวจสอบว่าควรข้ามการประมวลผลหรือไม่ - แก้ไขการ skip ที่เข้มงวดเกินไป"""
        
        # ข้ามถ้าไม่มี preset ที่อนุญาต
        if not self.allowed_preset_mapping:
            return True
            
        # ### [FIX v1.3] ลบการ skip ที่ป้องกันการตรวจจับการเปลี่ยนพื้นที่ ###
        # เดิม: ข้ามถ้าปุ่มแสดงอยู่และเมาส์อยู่ใน preset เดียวกัน
        # ปัญหา: ทำให้ไม่ตรวจจับการเปลี่ยนพื้นที่เมื่อมีปุ่มแสดงอยู่
        # แก้ไข: ให้ตรวจสอบเฉพาะ cooldown และการมี mapping เท่านั้น
        # ### สิ้นสุดการแก้ไข ###
            
        # ข้ามถ้าอยู่ในช่วง cooldown (รักษา logic เดิม)
        if hasattr(self, 'last_processed_time'):
            current_time = time.time()
            if current_time - self.last_processed_time < 0.1:  # ลด cooldown จาก 0.5 เป็น 0.1 วินาที
                return True
        
        return False

    def check_continuous_translation(self, x, y):
        """[NEW v1.3] ตรวจจับการแปลต่อเนื่อง - เมาส์อยู่บริเวณปุ่มเดิมหลังจากคลิกแล้ว"""
        # ถ้าไม่มีปุ่มแสดงอยู่ และมีตำแหน่งปุ่มล่าสุด
        if (not self.is_button_displayed and 
            self.last_button_bounds and 
            self.last_button_preset == self.current_hover_preset):
            
            x1, y1, x2, y2 = self.last_button_bounds
            
            # ตรวจสอบว่าเมาส์อยู่ในบริเวณที่เคยมีปุ่มหรือไม่
            if x1 <= x <= x2 and y1 <= y <= y2:
                # เมาส์อยู่บริเวณปุ่มเดิม -> แสดงปุ่มใหม่สำหรับการแปลต่อเนื่อง
                if not self.continuous_translation_timer:
                    self.continuous_translation_timer = self.root.after(
                        300, lambda: self.show_continuous_translation_button()
                    )
                    logging.debug(f"Detected mouse in last button area for preset {self.current_hover_preset}, starting continuous translation timer")
            else:
                # เมาส์ไม่อยู่บริเวณปุ่มเดิม -> ยกเลิก timer
                if self.continuous_translation_timer:
                    self.root.after_cancel(self.continuous_translation_timer)
                    self.continuous_translation_timer = None

    def show_continuous_translation_button(self):
        """[NEW v1.3] แสดงปุ่มสำหรับการแปลต่อเนื่อง"""
        if (self.current_hover_preset and 
            not self.is_button_displayed and
            self.last_button_preset == self.current_hover_preset):
            
            self.show_confirmation_button(self.current_hover_preset)
            logging.info(f"Showing continuous translation button for preset {self.current_hover_preset}")
        
        # ล้าง timer
        self.continuous_translation_timer = None

    def check_mouse_position(self, x, y):
        """[v1.1] ตรวจสอบตำแหน่งเมาส์แบบ Smart - ไม่ทำงานซ้ำถ้าอยู่ preset เดียวกัน"""
        # การตรวจสอบเงื่อนไขเบื้องต้นยังคงเหมือนเดิม
        if not self.enabled or self.is_processing:
            return

        is_translation_active = False
        if "is_translation_active" in self.callbacks:
            try:
                is_translation_active = self.callbacks["is_translation_active"]()
                if not is_translation_active:
                    self.hide_confirmation_button()
                    return
            except Exception as e:
                logging.error(f"Error calling is_translation_active callback: {e}")
                return
        
        # ตรวจหา preset ที่เมาส์ชี้อยู่
        preset_found_this_check = None
        try:
            scale_x, scale_y = self.get_cached_screen_scale()  # ใช้ cache แทน
            for preset_num, preset_data in self.allowed_preset_mapping.items():
                if "coordinates" not in preset_data: continue
                for area, coords in preset_data["coordinates"].items():
                    if not all(k in coords for k in ["start_x", "start_y", "end_x", "end_y"]): continue
                    
                    start_x_scaled = int(coords["start_x"] * scale_x)
                    start_y_scaled = int(coords["start_y"] * scale_y)
                    end_x_scaled = int(coords["end_x"] * scale_x)
                    end_y_scaled = int(coords["end_y"] * scale_y)
                    
                    if (start_x_scaled <= x <= end_x_scaled) and (start_y_scaled <= y <= end_y_scaled):
                        preset_found_this_check = preset_num
                        break
                if preset_found_this_check: break
        except Exception as e:
            logging.error(f"Error during area check in check_mouse_position: {e}")
            return

        # ### [NEW v1.3] Smart Logic: ทำงานเฉพาะเมื่อ preset เปลี่ยน หรือเมื่อต้องตรวจจับการแปลต่อเนื่อง ###
        if preset_found_this_check == self.current_hover_preset:
            # เมาส์ยังอยู่ใน preset เดียวกัน -> ตรวจจับการแปลต่อเนื่อง
            self.check_continuous_translation(x, y)
            return
        
        # preset เปลี่ยนแล้ว -> อัปเดตสถานะและดำเนินการ
        old_preset = self.current_hover_preset
        self.current_hover_preset = preset_found_this_check
        
        logging.debug(f"Preset changed from {old_preset} to {preset_found_this_check}")
        
        # ### [FIX v1.3.2] ยกเลิก timer ทั้งหมดก่อนดำเนินการใดๆ ###
        if self.hover_enter_timer:
            self.root.after_cancel(self.hover_enter_timer)
            self.hover_enter_timer = None
            
        if self.button_hide_timer:
            self.root.after_cancel(self.button_hide_timer)
            self.button_hide_timer = None
            
        # ### [IMPORTANT v1.3.2] ยกเลิก auto-hide timer เมื่อเข้าพื้นที่ใหม่ ###
        if self.auto_hide_timer:
            self.root.after_cancel(self.auto_hide_timer)
            self.auto_hide_timer = None
            logging.debug(f"Cancelled auto-hide timer due to area change to preset {preset_found_this_check}")
        # ### สิ้นสุดการยกเลิก auto-hide timer ###
            
        if self.continuous_translation_timer:
            self.root.after_cancel(self.continuous_translation_timer)
            self.continuous_translation_timer = None
        # ### สิ้นสุดการยกเลิก timer ###
        
        if preset_found_this_check is not None:
            # เข้าสู่พื้นที่ preset ใหม่
            self.pending_preset_num = preset_found_this_check
            
            # ### [FIX v1.3.1] Smart Instant Switch: เช็คเมาส์บนปุ่มก่อนซ่อน ###
            if self.is_button_displayed:
                # ถ้าเมาส์อยู่บนปุ่ม ไม่ให้สลับ (เพื่อให้ผู้ใช้คลิกได้)
                if self.is_mouse_on_button:
                    logging.debug(f"Mouse on button, preventing switch to preserve user click ability")
                    return
                
                # เมาส์ไม่อยู่บนปุ่ม -> สลับได้
                logging.debug(f"Instant switch to Preset {preset_found_this_check} (mouse not on button)")
                # ใช้ thread-safe method
                self.root.after(0, lambda: self.show_confirmation_button(preset_found_this_check))
            else:
                # ไม่มีปุ่มแสดง -> ใช้ delay 200ms ตามเดิม
                self.hover_enter_timer = self.root.after(200, lambda: self.show_confirmation_button(preset_found_this_check))
                logging.debug(f"Mouse entered NEW Preset {preset_found_this_check}. Starting 200ms timer for button.")
            # ### สิ้นสุด Smart Instant Switch ###
        else:
            # ออกจากพื้นที่ preset ทั้งหมด
            logging.debug("Mouse left all areas.")
            
            # ### [FIX v1.3.2] Gentle Hide: ใช้เวลา 3 วินาทีเหมือน auto-hide เพื่อป้องกันการกระพริบ ###
            # ใช้ auto-hide timer แทน button_hide_timer เพื่อให้ผู้ใช้มีเวลาเลื่อนเมาส์ไปยังปุ่ม
            if self.is_button_displayed:
                # ยกเลิก auto-hide timer เก่า (ถ้ามี)
                if self.auto_hide_timer:
                    self.root.after_cancel(self.auto_hide_timer)
                    
                # ตั้ง auto-hide timer ใหม่ 3 วินาที
                self.auto_hide_timer = self.root.after(3000, self.auto_hide_button)
                logging.debug("Mouse left all areas. Scheduled gentle button hide in 3 seconds (allowing time to reach button).")
            # ### สิ้นสุด Gentle Hide ###
            
            # รีเซ็ตสถานะ pending
            if self.pending_preset_num is not None:
                self.pending_preset_num = None
        # ### สิ้นสุด Smart Logic ###

    def show_confirmation_button(self, preset_num):
        """[v1.3.1] แสดงปุ่มยืนยันบน overlay canvas - แก้ไขการป้องกันการแสดงซ้ำอย่างชาญฉลาด"""
        
        # Validation
        if not isinstance(preset_num, int) or preset_num < 1 or preset_num > 6:
            logging.error(f"Invalid preset_num: {preset_num}")
            return
        
        # ทำให้แน่ใจว่ามี overlay
        if not self.overlay_window or not self.overlay_window.winfo_exists():
            logging.warning("Overlay window not available, cannot show button")
            return
        
        # ### [FIX v1.3.1] Smart Button Protection: ไม่ซ่อนปุ่มถ้าเมาส์อยู่บนปุ่ม ###
        if (self.is_button_displayed and 
            self.current_displayed_preset == preset_num):
            logging.debug(f"Button already displayed for preset {preset_num}, skipping...")
            return
            
        # ถ้าเมาส์อยู่บนปุ่ม ไม่ให้ซ่อนปุ่ม (ป้องกันการคลิกไม่ได้)
        if self.is_mouse_on_button and self.is_button_displayed:
            logging.debug(f"Mouse on button, preventing hide to allow user click")
            return
            
        # ซ่อนปุ่มเก่าเฉพาะเมื่อเมาส์ไม่อยู่บนปุ่ม
        if self.is_button_displayed and not self.is_mouse_on_button:
            self.hide_confirmation_button()
        # ### สิ้นสุด Smart Button Protection ###

        if preset_num not in self.allowed_preset_mapping:
            logging.warning(f"Preset {preset_num} not in allowed mapping. Cannot show confirmation button.")
            return

        preset_data = self.allowed_preset_mapping[preset_num]
        
        positioning_area_code = None
        area_preference_order = ['A', 'B', 'C']
        
        # ดึงค่า "areas" ซึ่งเป็น list อยู่แล้วมาโดยตรง ไม่ต้อง .split()
        active_areas_in_preset = preset_data.get("areas", [])
        if not isinstance(active_areas_in_preset, list):
            # เพิ่มการป้องกันเผื่อข้อมูลมีรูปแบบไม่สอดคล้องกัน
            active_areas_in_preset = []
        
        for area_code in area_preference_order:
            if area_code in active_areas_in_preset and area_code in preset_data.get("coordinates", {}):
                positioning_area_code = area_code
                break
        
        if positioning_area_code is None:
            logging.warning(f"Preset {preset_num} has no valid/defined coordinates for its active areas ({active_areas_in_preset}). Cannot show confirmation button.")
            return
        
        logging.info(f"Using Area '{positioning_area_code}' to position confirmation button for Preset {preset_num}.")

        coords = preset_data["coordinates"][positioning_area_code]
        scale_x, scale_y = self.get_cached_screen_scale()  # ใช้ cache แทน
        
        # ### [v1.1] ปรับตำแหน่งปุ่มให้แสดงเหนือกล่อง area เพื่อไม่บังชื่อตัวละคร ###
        btn_width = 90     # ขนาดกะทัดรัด
        btn_height = 32    # ความสูงพอดี
        gap = 8            # ระยะห่างจากขอบบนของ area
        
        btn_x = int(coords["start_x"] * scale_x)  # X: ซ้ายเหมือนเดิม
        btn_y = int(coords["start_y"] * scale_y) - btn_height - gap  # Y: เหนือ area
        # ### สิ้นสุดการปรับตำแหน่งปุ่ม ###

        # วาดปุ่มบน canvas
        # สร้างสี่เหลี่ยมพื้นหลัง
        rect = self.overlay_canvas.create_rectangle(
            btn_x, btn_y, 
            btn_x + btn_width, btn_y + btn_height,
            fill="white", 
            outline="#CCCCCC",
            width=1,
            tags=f"button_{preset_num}"
        )
        
        # สร้างข้อความ
        text = self.overlay_canvas.create_text(
            btn_x + btn_width//2, 
            btn_y + btn_height//2,
            text="แปล",
            fill="#424242",
            font=("Bai Jamjuree", 10),
            tags=f"button_{preset_num}"
        )
        
        # ### [NEW] เพิ่ม Hover Effect บนปุ่ม ###
        def on_button_hover_enter(event):
            """เมื่อเมาส์เข้าปุ่ม - เปลี่ยนสีและหยุดการนับเวลา auto-hide"""
            try:
                self.is_mouse_on_button = True
                # เปลี่ยนสีปุ่มเป็น hover state
                self.overlay_canvas.itemconfig(rect, fill="#E8E8E8", outline="#00C853")
                self.overlay_canvas.itemconfig(text, fill="#2E7D32")
                # หยุดการนับเวลา auto-hide
                if self.auto_hide_timer:
                    self.root.after_cancel(self.auto_hide_timer)
                    self.auto_hide_timer = None
                logging.debug(f"Mouse entered button for preset {preset_num}, auto-hide timer paused")
            except Exception as e:
                logging.error(f"Error in on_button_hover_enter: {e}")
        
        def on_button_hover_leave(event):
            """เมื่อเมาส์ออกจากปุ่ม - เปลี่ยนกลับสีปกติและเริ่มนับเวลา auto-hide ใหม่"""
            try:
                self.is_mouse_on_button = False
                # เปลี่ยนสีกลับเป็นปกติ
                self.overlay_canvas.itemconfig(rect, fill="white", outline="#CCCCCC")
                self.overlay_canvas.itemconfig(text, fill="#424242")
                # เริ่มนับเวลา auto-hide ใหม่
                self.start_auto_hide_timer()
                logging.debug(f"Mouse left button for preset {preset_num}, auto-hide timer restarted")
            except Exception as e:
                logging.error(f"Error in on_button_hover_leave: {e}")
        
        # Bind hover events ลงบน canvas items
        self.overlay_canvas.tag_bind(f"button_{preset_num}", "<Enter>", on_button_hover_enter)
        self.overlay_canvas.tag_bind(f"button_{preset_num}", "<Leave>", on_button_hover_leave)
        # ### สิ้นสุด Hover Effect ###
        
        # เก็บข้อมูลปุ่ม
        self.button_items[preset_num] = {
            "rect": rect,
            "text": text,
            "bounds": (btn_x, btn_y, btn_x + btn_width, btn_y + btn_height),
            "preset": preset_num
        }
        
        # ### [NEW v1.3] เก็บตำแหน่งปุ่มล่าสุดสำหรับการแปลต่อเนื่อง ###
        self.last_button_bounds = (btn_x, btn_y, btn_x + btn_width, btn_y + btn_height)
        self.last_button_preset = preset_num
        # ### สิ้นสุดการเก็บตำแหน่งปุ่มล่าสุด ###
        
        # ### [NEW v1.1] อัปเดตสถานะการแสดงปุ่ม ###
        self.current_displayed_preset = preset_num
        self.is_button_displayed = True
        # ### สิ้นสุดการอัปเดตสถานะ ###
        
        # Fade in effect
        if self.overlay_window and self.overlay_window.winfo_exists():
            self.overlay_window.attributes("-alpha", 0.95)
        
        # ### [NEW] เริ่ม Auto-Hide Timer 3 วินาที ###
        self.start_auto_hide_timer()
        # ### สิ้นสุด Auto-Hide Timer ###
        
        logging.info(f"Button displayed on canvas for preset {preset_num} at ({btn_x}, {btn_y}) with hover effect and auto-hide timer")

    def start_auto_hide_timer(self):
        """[NEW] เริ่ม Timer สำหรับซ่อนปุ่มอัตโนมัติใน 3 วินาที"""
        # ยกเลิก timer เก่าก่อน (ถ้ามี)
        if self.auto_hide_timer:
            self.root.after_cancel(self.auto_hide_timer)
        
        # ตั้ง timer ใหม่ 3 วินาที
        self.auto_hide_timer = self.root.after(3000, self.auto_hide_button)
        logging.debug("Auto-hide timer started (3 seconds)")
    
    def auto_hide_button(self):
        """[NEW] ซ่อนปุ่มอัตโนมัติหลังจาก 3 วินาที (เฉพาะเมื่อเมาส์ไม่อยู่บนปุ่ม)"""
        if not self.is_mouse_on_button:
            self.hide_confirmation_button()
            logging.info("Auto-hide triggered: Button hidden after 3 seconds")
        else:
            logging.debug("Auto-hide skipped: Mouse is still on button")

    def hide_confirmation_button(self):
        """[v1.1] ซ่อนและทำลายปุ่มยืนยันบน canvas และยกเลิก Timer ที่เกี่ยวข้องทั้งหมด"""
        try:
            # ยกเลิก Timer ที่อาจกำลังรอแสดงปุ่มอยู่
            if self.hover_enter_timer:
                self.root.after_cancel(self.hover_enter_timer)
                self.hover_enter_timer = None
                
            # ยกเลิก Timer ที่อาจกำลังรอซ่อนปุ่มอยู่
            if self.button_hide_timer:
                self.root.after_cancel(self.button_hide_timer)
                self.button_hide_timer = None
            
            # ### [NEW] ยกเลิก Auto-Hide Timer ###
            if self.auto_hide_timer:
                self.root.after_cancel(self.auto_hide_timer)
                self.auto_hide_timer = None
            # ### สิ้นสุดการยกเลิก Auto-Hide Timer ###
            
            # ### [NEW v1.3] ยกเลิก Continuous Translation Timer ###
            if self.continuous_translation_timer:
                self.root.after_cancel(self.continuous_translation_timer)
                self.continuous_translation_timer = None
            # ### สิ้นสุดการยกเลิก Continuous Translation Timer ###
                
            # ลบ canvas items ทั้งหมด
            if self.overlay_canvas and self.button_items:
                for preset_num, button_data in list(self.button_items.items()):
                    try:
                        if "rect" in button_data:
                            self.overlay_canvas.delete(button_data["rect"])
                        if "text" in button_data:
                            self.overlay_canvas.delete(button_data["text"])
                    except Exception as e:
                        logging.debug(f"Error deleting canvas item: {e}")
            
            # ทำให้ overlay โปร่งใสสุด (เกือบมองไม่เห็น)
            if self.overlay_window and self.overlay_window.winfo_exists():
                self.overlay_window.attributes("-alpha", 0.05)  # ใช้ 0.05 แทน 0.01
            
            # ### [NEW v1.1] รีเซ็ตสถานะการแสดงปุ่มให้สะอาด ###
            self.button_items = {}
            self.pending_preset_num = None
            self.current_displayed_preset = None
            self.is_button_displayed = False
            # ### [NEW] รีเซ็ตสถานะ hover ###
            self.is_mouse_on_button = False
            # ### สิ้นสุดการรีเซ็ตสถานะ ###
            
            logging.debug("Canvas button hidden and all timers cleared")
        except Exception as e:
            logging.error(f"Error in hide_confirmation_button: {e}")

    def confirm_preset_switch(self, preset_num):
        """[v1.3] ดำเนินการสลับ Preset หรือ Force Translate ผ่าน control_ui โดยตรง"""
        
        # ### [NEW] ยกเลิก Auto-Hide Timer เมื่อคลิกปุ่ม ###
        if self.auto_hide_timer:
            self.root.after_cancel(self.auto_hide_timer)
            self.auto_hide_timer = None
        # ### สิ้นสุดการยกเลิก Auto-Hide Timer ###
        
        # ### [NEW v1.3] บันทึกตำแหน่งเมาส์ปัจจุบันก่อนซ่อนปุ่ม ###
        current_mouse_pos = self.last_mouse_pos
        # ### สิ้นสุดการบันทึกตำแหน่งเมาส์ ###
        
        # ซ่อนปุ่มยืนยันทันทีที่คลิก
        self.hide_confirmation_button()
        
        # ตรวจสอบว่า preset ที่กำลังจะทำงาน คืออันเดียวกับที่ใช้อยู่หรือไม่
        current_active_preset = self.settings.get("current_preset", 1)

        if current_active_preset == preset_num:
            # ตรรกะใหม่: ถ้าเป็น Preset เดิม ให้เรียกใช้ force_translate ของ control_ui
            logging.info(f"Hover confirmation on current preset ({preset_num}). Triggering Force Translate via Control_UI.")
            
            if hasattr(self, 'control_ui') and self.control_ui and hasattr(self.control_ui, 'force_translate'):
                self.control_ui.force_translate()
                
                # ### [NEW v1.3] ตั้ง timer เพื่อตรวจจับการแปลต่อเนื่อง ###
                self.root.after(500, lambda: self.setup_continuous_translation_detection(current_mouse_pos, preset_num))
                # ### สิ้นสุดการตั้ง timer การแปลต่อเนื่อง ###
            else:
                logging.warning("Cannot force translate: control_ui or its force_translate reference is missing.")
        else:
            # ตรรกะเดิม: ถ้าเป็น Preset ใหม่ ให้ทำการสลับพื้นที่
            logging.info(f"User confirmed switch to Preset {preset_num}.")
            
            if preset_num in self.allowed_preset_mapping:
                self.process_hover_area(preset_num, self.allowed_preset_mapping[preset_num])
            else:
                logging.error(f"Cannot confirm switch: Preset {preset_num} data not found.")
    
    def setup_continuous_translation_detection(self, mouse_pos, preset_num):
        """[NEW v1.3] ตั้งค่าการตรวจจับการแปลต่อเนื่องหลังจากคลิกปุ่ม"""
        if not self.enabled or not self.last_button_bounds:
            return
            
        x, y = mouse_pos
        x1, y1, x2, y2 = self.last_button_bounds
        
        # ตรวจสอบว่าเมาส์ยังอยู่ในบริเวณปุ่มเดิมหรือไม่
        if x1 <= x <= x2 and y1 <= y <= y2:
            # เมาส์ยังอยู่บริเวณเดิม -> เริ่มการตรวจจับการแปลต่อเนื่อง
            if not self.continuous_translation_timer:
                self.continuous_translation_timer = self.root.after(
                    200, lambda: self.show_continuous_translation_button()
                )
                logging.info(f"Setup continuous translation detection for preset {preset_num}")

    def process_hover_area(self, preset_num, preset_data):
        """ประมวลผลเมื่อพบว่าเมาส์อยู่ในพื้นที่ preset"""
        # *** Log ตอนเริ่มทำงานของเมธอดนี้ ***
        logging.info(f"--- Starting process_hover_area for Preset {preset_num} ---")
        try:
            # *** เพิ่ม: ตรวจสอบ cooldown อย่างเคร่งครัด ***
            current_time = time.time()
            elapsed_time = current_time - self.last_processed_time
            cooldown_time = 1.0  # กำหนด cooldown 1 วินาที (สามารถปรับได้)

            # เพิ่ม cooldown ยาวขึ้นถ้ากำลังจะสลับไปยัง preset เดิม
            if preset_num == self.last_processed_preset and elapsed_time < 2.0:
                logging.debug(
                    f"Process Hover: Ignoring repeated hover on same preset (cooldown: {elapsed_time:.2f}s < 2.0s)"
                )
                return

            # ตรวจสอบเวลาที่ผ่านไป
            if elapsed_time < cooldown_time:
                logging.debug(
                    f"Process Hover: Within cooldown period ({elapsed_time:.2f}s < {cooldown_time}s)"
                )
                return

            # *** เพิ่ม: ตรวจสอบ unsaved changes ***
            if (
                self.control_ui
                and hasattr(self.control_ui, "has_unsaved_changes")
                and self.control_ui.has_unsaved_changes
            ):
                # สามารถเพิ่มการแจ้งเตือนหรือขอยืนยันได้ที่นี่
                logging.warning(
                    f"Process Hover: Unsaved changes detected before switching to preset {preset_num}"
                )

            show_visual_feedback = not getattr(self, "manual_show_area_detected", False)
            if show_visual_feedback:
                logging.debug(
                    f"Process Hover: Showing visual feedback for Preset {preset_num}"
                )
                self.show_hover_area(preset_data)
            else:
                logging.debug(
                    "Process Hover: Skipping visual feedback due to manual show area."
                )

            # *** ตรวจสอบ Control UI Instance ก่อนเรียก ***
            if self.control_ui:
                logging.debug(
                    f"Process Hover: Control UI instance exists: {self.control_ui}"
                )
                if hasattr(self.control_ui, "select_preset"):
                    logging.info(
                        f"Process Hover: Calling control_ui.select_preset({preset_num})..."
                    )
                    try:
                        # เรียกใช้ select_preset ของ control_ui
                        self.control_ui.select_preset(preset_num)
                        logging.info(
                            f"Process Hover: control_ui.select_preset({preset_num}) called successfully."
                        )
                    except Exception as call_error:
                        logging.error(
                            f"Process Hover: Error calling control_ui.select_preset({preset_num}): {call_error}",
                            exc_info=True,
                        )
                else:
                    logging.error(
                        "Process Hover: Control UI instance does NOT have 'select_preset' method."
                    )
            else:
                logging.error(
                    "Process Hover: Control UI instance is None. Cannot trigger preset change."
                )

            # บันทึกเวลาล่าสุดที่ประมวลผล
            self.last_processed_time = current_time
            # อัพเดท preset ล่าสุดที่ประมวลผลไปแล้ว
            self.last_processed_preset = preset_num
            logging.debug(
                f"Process Hover: Updated last_processed_preset to {preset_num}, last_processed_time set."
            )

            # เริ่มการ Fade out ของกรอบสีเขียว (ถ้าแสดงไป)
            if show_visual_feedback:
                display_time = int(self.display_time * 1000)
                if self.root and self.root.winfo_exists():
                    logging.debug(
                        f"Process Hover: Scheduling fade out in {display_time}ms"
                    )
                    self.root.after(display_time, self.start_fade_out_all_windows)
                else:
                    logging.warning(
                        "Process Hover: Root window invalid, cannot schedule fade out."
                    )
        except Exception as e:
            logging.error(
                f"Error processing hover area for Preset {preset_num}: {e}",
                exc_info=True,
            )
            if "show_feedback" in self.callbacks:
                try:
                    self.callbacks["show_feedback"](f"Error processing hover: {e}")
                except Exception as cb_e:
                    logging.error(f"Error calling show_feedback callback: {cb_e}")
        finally:
            # จบการประมวลผลเสมอ
            self.is_processing = False
            logging.info(f"--- Finished process_hover_area for Preset {preset_num} ---")

    def notify_external_preset_change(self, preset_num):
        """
        รับการแจ้งเตือนเมื่อ preset ถูกเปลี่ยนจากแหล่งอื่น (เช่น Control UI, Auto-switch)
        อัปเดตสถานะภายในเพื่อป้องกันการ trigger ซ้ำทันที และซิงค์ข้อมูล preset ให้ตรงกัน

        Args:
            preset_num (int): หมายเลข preset ที่เปลี่ยนเป็น (1-6)
        """
        if not self.enabled:
            return

        logging.info(
            f"HoverTranslator notified of external preset change to: {preset_num}"
        )

        # อัพเดตตัวแปรสถานะปัจจุบัน
        self.current_active_preset = preset_num

        # อัปเดต preset ล่าสุดที่ประมวลผล
        self.last_processed_preset = preset_num

        # ตั้งค่า immunity_time ที่เหมาะสม
        # กำหนดเป็น 1/3 ของค่าปกติ เพื่อให้ตอบสนองได้เร็วขึ้นหากผู้ใช้ต้องการ hover ต่อ
        # แต่ยังป้องกันการ trigger ซ้ำโดยไม่ตั้งใจในระยะเวลาสั้นๆ
        current_time = time.time()
        short_immunity = self.immunity_time / 3
        self.last_processed_time = current_time - (self.immunity_time - short_immunity)
        logging.debug(
            f"Set short immunity period ({short_immunity:.1f}s) after external change"
        )

        # บังคับอัปเดตข้อมูล preset ทันที เพื่อให้มีข้อมูลล่าสุด
        if hasattr(self, "force_update_preset_data"):
            self.force_update_preset_data()
            logging.debug("Forced preset data update after external change")
        else:
            logging.warning("force_update_preset_data method not available")

        # เคลียร์ hover windows ที่แสดงอยู่ (ถ้ามี)
        if hasattr(self, "clear_hover_windows"):
            self.clear_hover_windows()
            logging.debug("Cleared hover windows after external preset change")
        else:
            logging.warning("clear_hover_windows method not available")

    def show_hover_area(self, preset_data):
        """แสดงพื้นที่ preset ด้วยเส้นกรอบสีเขียว"""
        try:
            # ล้างหน้าต่างเก่าก่อน
            self.clear_hover_windows()

            # ดึงค่า scale ของหน้าจอ
            scale_x, scale_y = self.get_cached_screen_scale()  # ใช้ cache แทน

            # สร้างหน้าต่างสำหรับแต่ละพื้นที่
            for area in preset_data["areas"]:
                if area in preset_data["coordinates"]:
                    coords = preset_data["coordinates"][area]

                    # ปรับพิกัดด้วย scale
                    start_x = int(coords["start_x"] * scale_x)
                    start_y = int(coords["start_y"] * scale_y)
                    end_x = int(coords["end_x"] * scale_x)
                    end_y = int(coords["end_y"] * scale_y)

                    # สร้างหน้าต่าง
                    window = tk.Toplevel(self.root)
                    window.overrideredirect(True)
                    window.attributes("-alpha", 0.9)  # ปรับให้เห็นชัดกว่าเดิม
                    window.attributes("-topmost", True)

                    # กำหนดตำแหน่งและขนาด
                    width = end_x - start_x
                    height = end_y - start_y
                    window.geometry(f"{width}x{height}+{start_x}+{start_y}")
                    window.config(bg="#330033")  # ใช้สีม่วงเข้มแทนค่าว่าง

                    # สร้าง canvas สำหรับวาดเส้นกรอบ
                    canvas = tk.Canvas(window, highlightthickness=0, bg="#330033", bd=0)
                    canvas.pack(fill=tk.BOTH, expand=True)

                    # วาดเส้นกรอบสีเขียว
                    border_width = 3  # ความหนาของเส้นกรอบ
                    canvas.create_rectangle(
                        border_width // 2,
                        border_width // 2,
                        width - border_width // 2,
                        height - border_width // 2,
                        outline="#00ff00",  # สีเขียว
                        width=border_width,
                    )

                    # ทำให้พื้นหลังโปร่งใส
                    window.wm_attributes("-transparentcolor", "#330033")

                    # เก็บอ้างอิงหน้าต่าง
                    self.hover_windows[area] = window

        except Exception as e:
            logging.error(f"Error showing hover area: {e}")

    def start_fade_out_all_windows(self):
        """เริ่มต้น fade out หน้าต่างทั้งหมด"""
        # ยกเลิก fade job ที่อาจกำลังทำงานอยู่
        for job_id in self.fade_jobs.values():
            if job_id:
                try:
                    self.root.after_cancel(job_id)
                except Exception:
                    pass
        self.fade_jobs.clear()

        # เริ่ม fade out ใหม่
        for area, window in list(self.hover_windows.items()):
            if window and window.winfo_exists():
                # คำนวณ parameters สำหรับ fade
                steps = 10
                current_alpha = 0.9
                step_alpha = current_alpha / steps
                interval = int(
                    (self.fade_duration * 1000) / steps
                )  # คำนวณ interval จาก fade_duration

                # เริ่ม fade
                self.fade_window(
                    area, window, current_alpha, step_alpha, steps, interval, 0
                )

    def fade_window(self, area, window, start_alpha, step_alpha, steps, interval, current_step):
        """Fade out หน้าต่างทีละขั้น"""
        if not window.winfo_exists() or current_step >= steps:
            # ถ้าหน้าต่างถูกทำลายไปแล้วหรือ fade ครบแล้ว ให้ล้างออกและจบการทำงาน
            if window.winfo_exists():
                window.destroy()
            if area in self.hover_windows:
                del self.hover_windows[area]
            if area in self.fade_jobs:
                del self.fade_jobs[area]
            return

        # คำนวณ alpha ใหม่
        new_alpha = start_alpha - (step_alpha * current_step)
        if new_alpha < 0:
            new_alpha = 0

        # ปรับค่า alpha
        window.attributes("-alpha", new_alpha)

        # กำหนด next step
        next_step = current_step + 1
        job_id = self.root.after(
            interval,
            lambda: self.fade_window(
                area, window, start_alpha, step_alpha, steps, interval, next_step
            ),
        )

        # เก็บ job_id สำหรับยกเลิกถ้าจำเป็น
        self.fade_jobs[area] = job_id

    def clear_hover_windows(self):
        """ล้างหน้าต่าง hover ทั้งหมด"""
        try:
            # ยกเลิก fade jobs ทั้งหมด
            for job_id in self.fade_jobs.values():
                if job_id:
                    try:
                        self.root.after_cancel(job_id)
                    except Exception:
                        pass
            self.fade_jobs.clear()

            # ทำลายหน้าต่างทั้งหมด
            for window in self.hover_windows.values():
                if window and window.winfo_exists():
                    window.destroy()

            self.hover_windows = {}
        except Exception as e:
            logging.error(f"Error clearing hover windows: {e}")



class HoverSettingsUI:
    """UI สำหรับตั้งค่า Hover Translation Presets (ปรับปรุงใหม่ทั้งหมด)"""

    def __init__(self, parent, hover_translator, settings):
        self.parent = parent
        self.hover_translator = hover_translator
        self.settings = settings
        self.window = None
        self.preset_switches = {}

    def show(self):
        logging.info("HoverSettingsUI.show() called")
        
        if self.window and self.window.winfo_exists():
            logging.info("Window already exists, lifting and focusing")
            self.window.lift()
            self.window.focus_force()
            return
        
        logging.info("Creating new window")
        self.create_window()

    def create_window(self):
        self.window = tk.Toplevel(self.parent)
        self.window.title("ตั้งค่า Hover Translation")
        # ปรับขนาดให้เหมาะสมกับ Layout ใหม่
        self.window.geometry("400x300")
        self.window.resizable(False, False)
        self.window.transient(self.parent)
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)  # เป็น topmost เสมอ
        self.window.attributes("-alpha", 0.95)    # โปร่งแสงเล็กน้อยเพื่อไม่บดบังเกม

        # *** รักษา topmost state เสมอ ***
        def maintain_topmost():
            try:
                if self.window and self.window.winfo_exists():
                    self.window.attributes("-topmost", True)
                    self.window.after(1000, maintain_topmost)  # ตรวจสอบทุก 1 วินาที
            except:
                pass
        self.window.after(1000, maintain_topmost)

        bg_color = "#2D2D2D"
        fg_color = "white"
        accent_color = "#4CAF50"
        disabled_color = "#616161"

        self.window.configure(bg=bg_color)

        main_frame = tk.Frame(self.window, bg=bg_color, relief="raised", bd=1)
        main_frame.pack(fill="both", expand=True, padx=2, pady=2)

        header_frame = tk.Frame(main_frame, bg=bg_color)
        header_frame.pack(fill="x", padx=10, pady=(5, 0))

        close_btn = tk.Button(header_frame, text="×", font=("Arial", 14, "bold"), bg=bg_color, fg="#888888", relief="flat", cursor="hand2", command=self.close, bd=0)
        close_btn.pack(side="right")
        
        def on_close_enter(e): close_btn.configure(fg="#FF4444")
        def on_close_leave(e): close_btn.configure(fg="#888888")
        close_btn.bind("<Enter>", on_close_enter)
        close_btn.bind("<Leave>", on_close_leave)

        title_frame = tk.Frame(main_frame, bg=bg_color)
        title_frame.pack(fill="x", padx=15, pady=(5, 10))
        
        # ปรับขนาดฟอนต์ตามที่คุณต้องการ
        title_label = tk.Label(title_frame, text="เลือกเปิดการใช้งาน Hover", font=("Bai Jamjuree", 16), bg=bg_color, fg=fg_color)
        title_label.pack()

        # ▼▼▼ START: แก้ไข Layout เป็น .grid() ▼▼▼
        switches_container = tk.Frame(main_frame, bg=bg_color)
        switches_container.pack(fill="both", expand=True, padx=10, pady=(10, 15))
        # กำหนดให้แต่ละคอลัมน์มีน้ำหนักเท่ากัน เพื่อการจัดวางที่สมดุล
        switches_container.grid_columnconfigure((0, 1, 2), weight=1)

        all_presets = self.settings.get_all_presets()
        if not all_presets:
            error_label = tk.Label(switches_container, text="เกิดข้อผิดพลาด: ไม่พบข้อมูล Preset", font=("Bai Jamjuree", 12), bg=bg_color, fg="#FF6B6B")
            error_label.pack(pady=20)
            self.center_window()
            return

        # วนลูปสร้างสวิตช์และจัดวางลงใน grid
        for idx in range(len(all_presets)):
            if idx >= 6: break
            
            preset_num = idx + 1
            preset_data = all_presets[idx]
            
            # คำนวณแถวและคอลัมน์
            row = idx // 3
            col = idx % 3
            
            self.create_compact_preset_switch(switches_container, preset_num, preset_data, row, col, bg_color, fg_color, accent_color, disabled_color)

        self.center_window()
        self.make_draggable(main_frame)
        self.window.bind("<Escape>", lambda e: self.close())
        
        # *** แจ้ง control_ui ว่า window ถูกสร้างแล้ว ***
        self.notify_control_ui_window_created()
        
        self.window.focus_set()

    def notify_control_ui_window_created(self):
        """แจ้ง control_ui ว่า window ถูกสร้างแล้ว"""
        try:
            if (self.hover_translator and 
                hasattr(self.hover_translator, 'control_ui') and 
                self.hover_translator.control_ui and
                hasattr(self.hover_translator.control_ui, 'hover_settings_window')):
                self.hover_translator.control_ui.hover_settings_window = self.window
                logging.info("HoverSettingsUI: Notified control_ui that window is created")
        except Exception as e:
            logging.error(f"Error notifying control_ui about window creation: {e}")

    def make_draggable(self, widget):
        def start_move(event):
            self.window.x = event.x
            self.window.y = event.y
        def stop_move(event):
            self.window.x = None
            self.window.y = None
        def do_move(event):
            if self.window.x is not None and self.window.y is not None:
                deltax = event.x - self.window.x
                deltay = event.y - self.window.y
                x = self.window.winfo_x() + deltax
                y = self.window.winfo_y() + deltay
                self.window.geometry(f"+{x}+{y}")
        
        widget.bind("<Button-1>", start_move)
        widget.bind("<ButtonRelease-1>", stop_move)
        widget.bind("<B1-Motion>", do_move)

        # ทำให้วิดเจ็ตลูกๆ ลากได้ด้วย
        for child in widget.winfo_children():
            child.bind("<Button-1>", start_move)
            child.bind("<ButtonRelease-1>", stop_move)
            child.bind("<B1-Motion>", do_move)

    def create_compact_preset_switch(self, parent, preset_num, preset_data, row, col, bg_color, fg_color, accent_color, disabled_color):
        """สร้าง switch และจัดวางลง grid (แก้ไขใหม่)"""
        switch_container = tk.Frame(parent, bg=bg_color)
        # จัดวาง container ลงใน grid ของ parent
        switch_container.grid(row=row, column=col, pady=5)

        preset_name = self.get_compact_preset_name(preset_data, preset_num)
        
        # ปรับขนาดฟอนต์ของชื่อ
        name_label = tk.Label(switch_container, text=preset_name, font=("Bai Jamjuree", 12), bg=bg_color, fg=fg_color, anchor="center")
        name_label.pack(pady=(0, 5))

        current_state = self.hover_translator.allowed_hover_presets.get(preset_num, False)

        switch_canvas = tk.Canvas(switch_container, width=45, height=22, bg=bg_color, highlightthickness=0, cursor="hand2")
        switch_canvas.pack()

        self.preset_switches[preset_num] = {
            'canvas': switch_canvas,
            'state': current_state,
            'preset_num': preset_num
        }

        self.draw_switch(switch_canvas, current_state, accent_color, disabled_color)
        
        switch_canvas.bind("<Button-1>", lambda e, num=preset_num: self.toggle_switch(num, accent_color, disabled_color))

    def get_compact_preset_name(self, preset_data, preset_num):
        """ดึงชื่อ preset จริงสำหรับแสดงผล"""
        display_name = self.settings.get_preset_display_name(preset_num)
        display_name = display_name.capitalize()
        # ปรับการตัดคำให้เหมาะสมกับฟอนต์ใหม่
        return display_name[:10] + "..." if len(display_name) > 10 else display_name

    def draw_switch(self, canvas, state, accent_color, disabled_color):
        """วาด switch (ดีไซน์สี่เหลี่ยมคม)"""
        canvas.delete("all")

        width = 45
        height = 22
        padding = 2

        on_color = accent_color
        off_color = disabled_color
        knob_color = "white"

        bg_color = on_color if state else off_color

        # วาดพื้นหลังสี่เหลี่ยมคม (Track)
        canvas.create_rectangle(padding, padding, width - padding, height - padding, fill=bg_color, outline="")

        # วาดตัวเลื่อนสี่เหลี่ยมคม (Knob)
        knob_height = height - (padding * 2)
        knob_width = knob_height - 4 # ทำให้เป็นสี่เหลี่ยมจัตุรัสมากขึ้น

        if state:  # สถานะเปิด (อยู่ทางขวา)
            x0 = width - padding - knob_width
        else:  # สถานะปิด (อยู่ทางซ้าย)
            x0 = padding

        y0 = padding
        canvas.create_rectangle(x0, y0, x0 + knob_width, y0 + knob_height, fill=knob_color, outline="")

    def toggle_switch(self, preset_num, accent_color, disabled_color):
        if preset_num in self.preset_switches:
            switch_data = self.preset_switches[preset_num]
            new_state = not switch_data['state']
            
            switch_data['state'] = new_state
            self.hover_translator.update_allowed_preset(preset_num, new_state)
            
            self.draw_switch(switch_data['canvas'], new_state, accent_color, disabled_color)
            
            logging.info(f"Toggled hover preset {preset_num}: {new_state}")
            
    def center_window(self):
        """จัดตำแหน่ง HoverSettingsUI อย่างฉลาด - ใช้ logic เดียวกับ Control UI"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        
        # ใช้ logic เดียวกับ Control UI ในการจัดตำแหน่ง
        x, y = self.position_smart_relative_to_control_ui(width, height)
        self.window.geometry(f"+{x}+{y}")

    def position_smart_relative_to_control_ui(self, settings_width, settings_height):
        """
        วางตำแหน่ง HoverSettingsUI อย่างฉลาด โดยตรวจสอบตำแหน่ง Control UI
        และวางไว้อีกด้านพร้อมเว้นระยะห่าง 10px (ใช้ logic เดียวกับ Control UI)
        """
        try:
            # ตรวจสอบว่ามี Control UI หรือไม่
            if not (self.hover_translator and 
                   hasattr(self.hover_translator, 'control_ui') and 
                   self.hover_translator.control_ui and
                   hasattr(self.hover_translator.control_ui, 'root')):
                # Fallback ไปกลางจอ
                x = (self.window.winfo_screenwidth() // 2) - (settings_width // 2)
                y = (self.window.winfo_screenheight() // 2) - (settings_height // 2)
                return x, y

            control_ui_root = self.hover_translator.control_ui.root
            
            # ดึงข้อมูลตำแหน่งและขนาดของ Control UI
            control_x = control_ui_root.winfo_x()
            control_y = control_ui_root.winfo_y()
            control_width = control_ui_root.winfo_width()

            monitor_left, monitor_top, monitor_width, monitor_height = 0, 0, 0, 0

            # ตรวจจับจอภาพที่ Control UI อยู่ (ใช้ logic เดียวกับ Control UI)
            try:
                # ดึง handle ของจอภาพที่หน้าต่าง Control UI แสดงอยู่
                control_hwnd = int(control_ui_root.winfo_id())
                hmonitor = win32api.MonitorFromWindow(control_hwnd, win32con.MONITOR_DEFAULTTONEAREST)

                # ดึงข้อมูลของจอภาพนั้นๆ
                monitor_info = win32api.GetMonitorInfo(hmonitor)
                monitor_rect = monitor_info['Work']  # ไม่ทับ Taskbar

                monitor_left = monitor_rect[0]
                monitor_top = monitor_rect[1]
                monitor_width = monitor_rect[2] - monitor_left
                monitor_height = monitor_rect[3] - monitor_top

            except Exception as e:
                # หากเกิดข้อผิดพลาด ใช้จอหลัก
                monitor_left = 0
                monitor_top = 0
                monitor_width = self.window.winfo_screenwidth()
                monitor_height = self.window.winfo_screenheight()

            # gap เดียวกับ Control UI
            gap = 10

            # ตัดสินใจวางซ้ายหรือขวา (logic เดียวกับ Control UI)
            control_center_on_monitor = control_x - monitor_left + (control_width // 2)
            monitor_center_x = monitor_width // 2

            if control_center_on_monitor <= monitor_center_x:
                # Control UI อยู่ซ้าย -> วาง HoverSettings ด้านขวา
                new_x = control_x + control_width + gap
                # ตรวจสอบไม่ให้ล้นจอ
                if new_x + settings_width > monitor_left + monitor_width:
                    new_x = control_x - settings_width - gap
            else:
                # Control UI อยู่ขวา -> วาง HoverSettings ด้านซ้าย  
                new_x = control_x - settings_width - gap
                # ตรวจสอบไม่ให้ล้นจอ
                if new_x < monitor_left:
                    new_x = control_x + control_width + gap

            # จัดตำแหน่งแนวตั้งให้ขอบบนตรงกัน (เหมือน Control UI)
            new_y = control_y

            # ตรวจสอบขอบเขตแนวตั้ง
            if new_y < monitor_top:
                new_y = monitor_top
            if new_y + settings_height > monitor_top + monitor_height:
                new_y = monitor_top + monitor_height - settings_height

            return new_x, new_y

        except Exception as e:
            logging.error(f"Error positioning HoverSettingsUI: {e}")
            # Fallback ไปกลางจอ
            x = (self.window.winfo_screenwidth() // 2) - (settings_width // 2)
            y = (self.window.winfo_screenheight() // 2) - (settings_height // 2)
            return x, y
        
    def close(self):
        if self.window:
            logging.info("HoverSettingsUI.close() called")
            
            # แจ้ง control_ui ว่าหน้าต่างปิดแล้ว
            try:
                if (self.hover_translator and 
                    hasattr(self.hover_translator, 'control_ui') and 
                    self.hover_translator.control_ui and
                    hasattr(self.hover_translator.control_ui, 'hover_settings_is_open')):
                    self.hover_translator.control_ui.hover_settings_is_open = False
                    self.hover_translator.control_ui.hover_settings_window = None
                    logging.info("HoverSettingsUI: Notified control_ui that window is closed")
            except Exception as e:
                logging.error(f"Error notifying control_ui: {e}")
            
            # ทำลาย window
            try:
                self.window.destroy()
                logging.info("HoverSettingsUI: Window destroyed successfully")
            except Exception as e:
                logging.error(f"Error destroying window: {e}")
            
            self.window = None
            logging.info("HoverSettingsUI: Window reference cleared")
        else:
            logging.info("HoverSettingsUI.close() called but window is already None")
