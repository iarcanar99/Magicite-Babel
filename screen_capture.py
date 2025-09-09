import os
from PIL import ImageGrab
from datetime import datetime
import logging


class ScreenCapture:
    def __init__(self, base_dir="captured_screens"):
        self.base_dir = base_dir
        self.categories = {
            "raw": f"{base_dir}/raw",
            "processed": f"{base_dir}/processed",
        }
        self._init_directories()

    def _init_directories(self):
        for path in self.categories.values():
            os.makedirs(path, exist_ok=True)

    def capture_primary_screen(self):
        try:
            # จับภาพเฉพาะหน้าจอหลัก
            screen = ImageGrab.grab(all_screens=False)

            # สร้างชื่อไฟล์ด้วย timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screen_{timestamp}.png"

            # บันทึกภาพต้นฉบับ
            filepath = os.path.join(self.categories["raw"], filename)
            screen.save(filepath)

            logging.info(f"Captured screen saved to: {filepath}")
            return filepath

        except Exception as e:
            logging.error(f"Screen capture failed: {e}")
            return None
