#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
import random
import math
import time


class LoadingIndicator:
    def __init__(self, parent_window, width=120, height=60):
        self.parent_window = parent_window
        self.base_width = width
        self.base_height = height
        self.window = None
        self.canvas = None
        self.is_showing = False
        self._animation_job = None
        self.num_bars = 10

        # ใช้สีเริ่มต้น (จะถูกโอเวอร์ไรด์ถ้ามี appearance_manager)
        self.bar_color = "#FF5733"

        # รองรับการใช้ appearance_manager จากภายนอก
        self.appearance_manager = None

        self.animation_speed = 50
        self.bars = []
        self.actual_bar_width = 0
        self.actual_spacing = 0
        self.max_bar_pixel_height = 0
        self.min_bar_pixel_height = 0
        self.bar_current_heights_ratio = [
            random.uniform(0.2, 0.8) for _ in range(self.num_bars)
        ]
        self.bar_target_heights_ratio = [
            random.uniform(0.1, 1.0) for _ in range(self.num_bars)
        ]
        self.bar_animation_factors = [
            random.uniform(0.04, 0.08) for _ in range(self.num_bars)
        ]

    def set_appearance_manager(self, appearance_manager):
        """ตั้งค่า appearance_manager จากภายนอกหลังสร้าง instance"""
        self.appearance_manager = appearance_manager
        if hasattr(self.appearance_manager, "get_accent_color"):
            self.bar_color = self.appearance_manager.get_accent_color()

    def create_window(self):
        if self.window and self.window.winfo_exists():
            try:
                self.window.destroy()
            except tk.TclError:
                pass

        self.window = tk.Toplevel(self.parent_window)
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)

        # ใช้วิธีการที่ดีกว่าในการทำให้พื้นหลังโปร่งใส
        try:
            # ใช้สี magic pink สำหรับทำให้โปร่งใส
            self.window.configure(bg="#FF00FF")  # สีชมพูแสงจำนวน
            self.window.wm_attributes("-transparentcolor", "#FF00FF")
        except Exception as e:
            print(f"Warning: Could not set transparency: {e}")
            # Fallback หากไม่สามารถทำให้โปร่งใสได้
            self.window.configure(bg="#000000")
            self.window.attributes("-alpha", 0.9)

        # สร้าง canvas โดยใช้สีเดียวกันกับที่จะทำให้โปร่งใส
        self.canvas = tk.Canvas(
            self.window,
            width=self.base_width,
            height=self.base_height,
            bg="#FF00FF",  # ใช้สีเดียวกับ transparent color
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack()
        self._setup_bars()

    def _setup_bars(self):
        if not self.canvas or not self.canvas.winfo_exists():
            return
        self.canvas.delete("all")
        self.bars = []

        canvas_w = self.base_width
        canvas_h = self.base_height
        if self.num_bars == 0:
            return

        # คำนวณขนาดแท่งและระยะห่าง
        self.actual_bar_width = min(8, max(3, int(canvas_w * 0.06)))
        self.actual_spacing = max(2, int(self.actual_bar_width * 0.8))

        # คำนวณตำแหน่งให้อยู่กลาง
        total_content_width = (self.num_bars * self.actual_bar_width) + (
            max(0, self.num_bars - 1) * self.actual_spacing
        )
        start_x_offset = (canvas_w - total_content_width) / 2

        # ปรับความสูงเป็น 50% แทน 20%
        self.min_bar_pixel_height = int(canvas_h * 0.1)
        self.max_bar_pixel_height = int(canvas_h * 0.6)

        # สร้างแท่งทั้งหมด
        for i in range(self.num_bars):
            x0 = start_x_offset + i * (self.actual_bar_width + self.actual_spacing)

            # *** เพิ่มการเยื้องกันของจังหวะ - ทำให้แต่ละแท่งเริ่มต้นต่างกัน ***
            # สร้างค่าเริ่มต้นที่หลากหลายมากขึ้น ใช้ pattern แบบ sine wave
            phase_offset = (i / self.num_bars) * 2 * 3.14159  # Full wave cycle
            initial_ratio = 0.3 + 0.5 * (
                0.5 + 0.5 * math.sin(phase_offset + random.uniform(-0.5, 0.5))
            )

            # กำหนดความสูงเริ่มต้นด้วยค่าที่คำนวณใหม่
            self.bar_current_heights_ratio[i] = initial_ratio

            # ปรับ target ratio ให้แตกต่างกันมากขึ้นด้วย
            self.bar_target_heights_ratio[i] = random.uniform(0.1, 1.0)

            # *** เพิ่มความแตกต่างของความเร็วการเคลื่อนไหวเป็น 2 เท่า ***
            # ปรับ range ของ animation factors ให้กว้างขึ้นจาก (0.04, 0.08) เป็น (0.02, 0.12)
            self.bar_animation_factors[i] = random.uniform(0.02, 0.12)

            # คำนวณความสูงเริ่มต้น
            initial_h_px = self.min_bar_pixel_height + (
                self.bar_current_heights_ratio[i]
                * (self.max_bar_pixel_height - self.min_bar_pixel_height)
            )

            # คำนวณตำแหน่ง
            y_bottom = canvas_h - 5  # เว้นระยะจากขอบล่าง
            y_top = y_bottom - initial_h_px

            # กำหนดรัศมีความโค้ง
            corner_radius = min(self.actual_bar_width // 2, 4)

            # สร้างความโค้งมนด้านบน
            top_oval = self.canvas.create_oval(
                x0,
                y_top - corner_radius,
                x0 + self.actual_bar_width,
                y_top + corner_radius,
                fill=self.bar_color,
                outline="",
            )

            # สร้างส่วนกลาง (สี่เหลี่ยม)
            middle_rect = self.canvas.create_rectangle(
                x0,
                y_top,
                x0 + self.actual_bar_width,
                y_bottom,
                fill=self.bar_color,
                outline="",
            )

            # สร้างความโค้งมนด้านล่าง
            bottom_oval = self.canvas.create_oval(
                x0,
                y_bottom - corner_radius,
                x0 + self.actual_bar_width,
                y_bottom + corner_radius,
                fill=self.bar_color,
                outline="",
            )

            # เก็บทั้งสามส่วน (กลาง, บน, ล่าง)
            self.bars.append((middle_rect, top_oval, bottom_oval))

    def _animate_bars(self):
        if (
            not self.is_showing
            or not self.canvas
            or not self.window
            or not self.window.winfo_exists()
        ):
            if self._animation_job:
                try:
                    if self.window and self.window.winfo_exists():
                        self.window.after_cancel(self._animation_job)
                except tk.TclError:
                    pass
                self._animation_job = None
            return

        canvas_h = self.base_height

        for i in range(self.num_bars):
            if not (i < len(self.bars) and self.bars[i] and self.canvas.winfo_exists()):
                continue

            middle_rect, top_oval, bottom_oval = self.bars[i]
            current_h_ratio = self.bar_current_heights_ratio[i]
            target_h_ratio = self.bar_target_heights_ratio[i]
            factor = self.bar_animation_factors[i]

            # คำนวณค่าใหม่อย่างนุ่มนวล
            new_h_ratio = current_h_ratio + (target_h_ratio - current_h_ratio) * factor

            # ตรวจสอบว่าถึงเป้าหมายแล้วหรือยัง
            if abs(target_h_ratio - new_h_ratio) < 0.02:
                new_h_ratio = target_h_ratio

                # *** สร้างเป้าหมายใหม่ด้วยการกระจายความแตกต่างมากกว่าเดิม ***
                # ใช้ pattern การเคลื่อนไหวที่ซับซ้อนขึ้น
                current_time = time.time()
                wave_factor = 0.5 + 0.5 * math.sin(current_time * 0.5 + i * 0.5)

                # สร้างช่วงที่แตกต่างกันสำหรับแต่ละแท่ง
                if i % 3 == 0:  # แท่งที่ 0, 3, 6, 9
                    new_target = random.uniform(
                        0.7, 1.0
                    ) * wave_factor + random.uniform(0.1, 0.3)
                elif i % 3 == 1:  # แท่งที่ 1, 4, 7
                    new_target = random.uniform(0.3, 0.8) * (
                        1 - wave_factor
                    ) + random.uniform(0.2, 0.4)
                else:  # แท่งที่ 2, 5, 8
                    new_target = random.uniform(
                        0.1, 0.6
                    ) * wave_factor + random.uniform(0.3, 0.5)

                # จำกัดค่าให้อยู่ในช่วง 0.1 - 1.0
                new_target = max(0.1, min(1.0, new_target))

                self.bar_target_heights_ratio[i] = new_target

                # *** เพิ่มการสร้างความเร็วใหม่ที่แตกต่างกันมากขึ้นอีก 2 เท่า ***
                # ขยาย range ของความเร็วให้แตกต่างกันมากขึ้น
                self.bar_animation_factors[i] = random.uniform(0.015, 0.15)

            self.bar_current_heights_ratio[i] = new_h_ratio

            # คำนวณความสูงใหม่
            current_bar_h_pixel = self.min_bar_pixel_height + (
                new_h_ratio * (self.max_bar_pixel_height - self.min_bar_pixel_height)
            )
            current_bar_h_pixel = max(
                self.min_bar_pixel_height,
                min(current_bar_h_pixel, self.max_bar_pixel_height),
            )

            # คำนวณตำแหน่งใหม่
            y_bottom = canvas_h - 5
            y_top = y_bottom - current_bar_h_pixel
            corner_radius = min(self.actual_bar_width // 2, 4)

            try:
                # อัพเดทส่วนกลาง (สี่เหลี่ยม)
                rect_coords = self.canvas.coords(middle_rect)
                if len(rect_coords) == 4:
                    self.canvas.coords(
                        middle_rect, rect_coords[0], y_top, rect_coords[2], y_bottom
                    )

                # อัพเดทส่วนบน (วงรี)
                self.canvas.coords(
                    top_oval,
                    rect_coords[0],
                    y_top - corner_radius,
                    rect_coords[2],
                    y_top + corner_radius,
                )

                # อัพเดทส่วนล่าง (วงรี)
                self.canvas.coords(
                    bottom_oval,
                    rect_coords[0],
                    y_bottom - corner_radius,
                    rect_coords[2],
                    y_bottom + corner_radius,
                )
            except tk.TclError:
                # ข้าม Object ที่ถูกลบไปแล้ว
                continue

        # จำกัดการอัพเดทให้เป็น smooth animation
        if self.is_showing and self.window and self.window.winfo_exists():
            self._animation_job = self.window.after(
                self.animation_speed, self._animate_bars
            )

    def show(self):
        """แสดงไอคอนกำลังโหลด"""
        if not self.is_showing:
            self.is_showing = True

            # อัพเดทสีจาก appearance_manager ถ้ามี
            if self.appearance_manager and hasattr(
                self.appearance_manager, "get_accent_color"
            ):
                self.bar_color = self.appearance_manager.get_accent_color()

            if not self.window:
                self.create_window()

            # ปรับตำแหน่งให้อยู่ตรงกลาง parent_window
            if self.parent_window and self.parent_window.winfo_exists():
                try:
                    x = (
                        self.parent_window.winfo_x()
                        + (self.parent_window.winfo_width() // 2)
                        - (self.base_width // 2)
                    )
                    y = (
                        self.parent_window.winfo_y()
                        + (self.parent_window.winfo_height() // 2)
                        - (self.base_height // 2)
                    )
                    self.window.geometry(
                        f"{self.base_width}x{self.base_height}+{x}+{y}"
                    )
                except tk.TclError:
                    # ใช้ตำแหน่งเริ่มต้นถ้าไม่สามารถหาตำแหน่งของ parent ได้
                    self.window.geometry(
                        f"{self.base_width}x{self.base_height}+100+100"
                    )

            # เริ่มต้นการเคลื่อนไหว
            self._animate_bars()

    def hide(self):
        """ซ่อนไอคอนกำลังโหลด"""
        self.is_showing = False
        if self._animation_job and self.window and self.window.winfo_exists():
            try:
                self.window.after_cancel(self._animation_job)
                self._animation_job = None
            except tk.TclError:
                pass

        if self.window and self.window.winfo_exists():
            try:
                self.window.withdraw()  # ซ่อนหน้าต่างแทนที่จะทำลาย
            except tk.TclError:
                pass


# ทดสอบการทำงานของ LoadingIndicator ถ้าเรียกโดยตรง
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Test Loading Indicator")
    root.geometry("500x300")

    def toggle_loading():
        global loading_indicator, is_visible
        if is_visible:
            loading_indicator.hide()
            button.config(text="Show Loading")
            is_visible = False
        else:
            loading_indicator.show()
            button.config(text="Hide Loading")
            is_visible = True

    button = tk.Button(root, text="Show Loading", command=toggle_loading)
    button.pack(pady=20)

    loading_indicator = LoadingIndicator(root)
    is_visible = False

    root.mainloop()
