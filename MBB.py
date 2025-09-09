from enum import Enum
import json
from pydoc import text
import random
import subprocess
import sys
import os
import traceback
import tkinter as tk
from tkinter import (
    ttk,
    messagebox,
    Checkbutton,
    BooleanVar,
)  # เพิ่ม Checkbutton, BooleanVar
from tkinter import Label  # เพิ่ม import Label
import math  # เพิ่ม import math
from PIL import ImageGrab, ImageEnhance, Image, ImageTk, ImageDraw, ImageFilter
import win32gui
import win32con
from ctypes import windll

# Lazy import for EasyOCR to avoid PyInstaller issues
easyocr = None


def get_easyocr():
    """Lazy loading function for EasyOCR to avoid PyInstaller import issues"""
    global easyocr
    if easyocr is None:
        try:
            import easyocr as _easyocr

            easyocr = _easyocr
        except Exception as e:
            logging.error(f"Failed to import EasyOCR: {e}")
            # Check if EasyOCR installation marker exists before showing prompt
            easyocr_marker = "easyocr_installed.txt"
            if not os.path.exists(easyocr_marker):
                # Show installation prompt only if marker file doesn't exist
                show_easyocr_installation_prompt()
            else:
                # EasyOCR marker exists but import failed - likely a PATH or environment issue
                messagebox.showwarning(
                    "EasyOCR Import Error",
                    "EasyOCR installation detected but failed to load.\n\n"
                    "This might be due to:\n"
                    "1. Missing dependencies\n"
                    "2. Python environment issues\n"
                    "3. Incomplete installation\n\n"
                    "Try restarting your computer or reinstalling EasyOCR.",
                )
            return None
    return easyocr


def show_easyocr_installation_prompt():
    """Show installation prompt for EasyOCR"""
    response = messagebox.askquestion(
        "EasyOCR Installation Required",
        "EasyOCR is required for OCR functionality but is not installed.\n\n"
        "Would you like to run the Final Installation to install EasyOCR?\n\n"
        "Click 'Yes' to run installer, or 'No' to continue without OCR.",
        icon="question",
    )

    if response == "yes":
        try:
            # Try to run the EasyOCR installer - check multiple possible locations
            installer_paths = [
                "install_easyocr.bat",  # Same directory as exe
                "quick_install_easyocr.bat",  # Quick installer
                os.path.join(
                    os.path.dirname(__file__), "install_easyocr.bat"
                ),  # Script directory
                os.path.join(
                    os.path.dirname(__file__), "quick_install_easyocr.bat"
                ),  # Quick installer in script dir
                os.path.join(
                    os.getcwd(), "install_easyocr.bat"
                ),  # Current working directory
                os.path.join(
                    os.getcwd(), "quick_install_easyocr.bat"
                ),  # Quick installer in cwd
            ]

            installer_found = False
            for installer_path in installer_paths:
                if os.path.exists(installer_path):
                    subprocess.Popen([installer_path], shell=True)
                    messagebox.showinfo(
                        "Installer Started",
                        "EasyOCR installer has been started.\n\n"
                        "Please restart MBB after installation completes.",
                    )
                    installer_found = True
                    break

            if not installer_found:
                # Show options instead of just error
                response = messagebox.askyesno(
                    "Install EasyOCR",
                    "EasyOCR installer not found in the expected location.\n\n"
                    "Would you like to install EasyOCR manually now?\n\n"
                    "Click 'Yes' to open command prompt for manual installation,\n"
                    "or 'No' to continue without OCR functionality.",
                )

                if response:
                    # Create a temporary installer script and run it
                    try:
                        temp_installer_path = "temp_easyocr_installer.bat"
                        temp_installer_content = """@echo off
echo Installing EasyOCR...
echo This may take a few minutes...
echo.
python -m pip install easyocr
if %errorlevel% equ 0 (
    echo.
    echo Installation Successful!
    echo Please restart MBB to use OCR functionality.
    echo.
    echo EasyOCR installation completed > easyocr_installed.txt
) else (
    echo.
    echo Installation Failed!
    echo Please check your internet connection and try again.
    echo.
)
pause
del "%~f0"
"""

                        # Write temporary installer
                        with open(temp_installer_path, "w") as f:
                            f.write(temp_installer_content)

                        # Run the temporary installer
                        subprocess.Popen([temp_installer_path], shell=True)
                        messagebox.showinfo(
                            "Installation Started",
                            "EasyOCR installation has started.\n\n"
                            "Please wait for it to complete and restart MBB.",
                        )

                    except Exception as temp_error:
                        # Fallback to direct command prompt
                        try:
                            subprocess.Popen(
                                [
                                    "cmd",
                                    "/k",
                                    "echo Installing EasyOCR... && "
                                    "pip install easyocr && "
                                    "echo. && "
                                    "echo Installation complete! Please restart MBB. && "
                                    "pause",
                                ],
                                shell=True,
                            )
                            messagebox.showinfo(
                                "Manual Installation Started",
                                "A command prompt has been opened for manual installation.\n\n"
                                "Please follow the instructions and restart MBB when done.",
                            )
                        except Exception as cmd_error:
                            messagebox.showerror(
                                "Installation Error",
                                f"Could not start installation.\n\n"
                                f"Please manually run: pip install easyocr\n\n"
                                f"Errors: {temp_error}, {cmd_error}",
                            )
        except Exception as e:
            messagebox.showerror(
                "Installation Error", f"Failed to start installer: {e}"
            )
    else:
        messagebox.showwarning(
            "OCR Disabled",
            "OCR functionality will be disabled.\n\n"
            "You can install EasyOCR later by running install_easyocr.bat",
        )


import time
import threading
import difflib
import logging
import numpy as np
import cv2
from text_corrector import TextCorrector
import translated_ui
from text_corrector import DialogueType
from control_ui import Control_UI
from translator import Translator
from translator_claude import TranslatorClaude
from translator_gemini import TranslatorGemini
from settings import Settings, SettingsUI
from advance_ui import AdvanceUI
from mini_ui import MiniUI
from loggings import LoggingManager
from translator_factory import TranslatorFactory
import keyboard
import re
from appearance import appearance_manager
import importlib.util
import warnings
from translated_logs import Translated_Logs
from asset_manager import AssetManager
from font_manager import FontSettings, initialize_font_manager
from hover_translation import HoverTranslator
from FeatureManager import FeatureManager  # เพิ่ม import FeatureManager จากไฟล์ใหม่
from version_manager import get_mbb_version
from npc_manager_card import create_npc_manager_card
from npc_file_utils import get_game_info_from_npc_file


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# --- สิ้นสุดการตรวจสอบ import ---

# ยกเลิกการใช้งาน Tesseract OCR
TESSERACT_AVAILABLE = False

warnings.filterwarnings("ignore", category=UserWarning)

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Import npc_manager silently
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
npc_manager_path = os.path.join(current_dir, "npc_manager_card.py")  # เปลี่ยนเป็นไฟล์ใหม่


def create_rounded_rectangle(self, x1, y1, x2, y2, radius=25, **kwargs):
    """วาดสี่เหลี่ยมมุมโค้งบน Canvas

    Args:
        x1, y1: พิกัดมุมบนซ้าย
        x2, y2: พิกัดมุมล่างขวา
        radius: รัศมีมุมโค้ง
        **kwargs: พารามิเตอร์อื่นๆ เช่น fill, outline

    Returns:
        int: ID ของรูปที่วาด
    """
    # ปรับค่ารัศมีหากขนาดของสี่เหลี่ยมเล็กเกินไป
    width, height = x2 - x1, y2 - y1
    radius = min(radius, width // 2, height // 2)

    # กำหนดจุดที่ใช้ในการวาด
    # เพิ่มจุดระหว่างมุมเพื่อให้เส้นโค้งเรียบขึ้น
    points = [
        # บนซ้าย
        x1,
        y1 + radius,
        x1,
        y1 + radius // 2,  # เพิ่มจุดระหว่าง
        x1 + radius // 2,
        y1,  # เพิ่มจุดระหว่าง
        x1 + radius,
        y1,
        # บนขวา
        x2 - radius,
        y1,
        x2 - radius // 2,
        y1,  # เพิ่มจุดระหว่าง
        x2,
        y1 + radius // 2,  # เพิ่มจุดระหว่าง
        x2,
        y1 + radius,
        # ล่างขวา
        x2,
        y2 - radius,
        x2,
        y2 - radius // 2,  # เพิ่มจุดระหว่าง
        x2 - radius // 2,
        y2,  # เพิ่มจุดระหว่าง
        x2 - radius,
        y2,
        # ล่างซ้าย
        x1 + radius,
        y2,
        x1 + radius // 2,
        y2,  # เพิ่มจุดระหว่าง
        x1,
        y2 - radius // 2,  # เพิ่มจุดระหว่าง
        x1,
        y2 - radius,
    ]

    # เพิ่ม smooth=True เพื่อให้เส้นโค้งเรียบขึ้น
    return self.create_polygon(points, **kwargs, smooth=True)


# เพิ่มเมธอดให้กับ tk.Canvas
tk.Canvas.create_rounded_rectangle = create_rounded_rectangle


class TranslationMetrics:
    """คลาสสำหรับติดตามผลการแปล"""

    def __init__(self):
        self.total_translations = 0
        self.placeholder_count = 0
        self.uncertain_count = 0  # [?]
        self.very_uncertain_count = 0  # [??]
        self.fallback_success = 0
        self.similar_name_matches = 0
        self.context_guesses = 0
        self.emergency_detections = 0
        self.unknown_speakers_count = 0  # ชื่อที่ไม่มีในฐานข้อมูลแต่ยอมรับได้

    def record_translation(self, combined_text, method):
        """บันทึกข้อมูลการแปล"""
        self.total_translations += 1

        if "[ผู้พูด]" in combined_text:
            self.placeholder_count += 1
        elif "[??]" in combined_text:
            self.very_uncertain_count += 1
        elif "[?]" in combined_text:
            self.uncertain_count += 1

        if method == "similar_name":
            self.similar_name_matches += 1
            self.fallback_success += 1
        elif method == "context_guess":
            self.context_guesses += 1
            self.fallback_success += 1
        elif method == "emergency":
            self.emergency_detections += 1
            self.fallback_success += 1
        elif method == "unknown_speaker":
            self.unknown_speakers_count += 1
            self.fallback_success += 1

    def get_report(self):
        """สร้างรายงานสถิติ"""
        if self.total_translations == 0:
            return "No translations recorded yet"

        placeholder_rate = (self.placeholder_count / self.total_translations) * 100
        uncertain_rate = (self.uncertain_count / self.total_translations) * 100
        very_uncertain_rate = (
            self.very_uncertain_count / self.total_translations
        ) * 100
        fallback_rate = (self.fallback_success / self.total_translations) * 100

        report = f"""
=== Translation Quality Report ===
Total translations: {self.total_translations}

Name Detection Rates:
- Placeholder [ผู้พูด]: {self.placeholder_count} ({placeholder_rate:.1f}%)
- Uncertain [?]: {self.uncertain_count} ({uncertain_rate:.1f}%)
- Very uncertain [??]: {self.very_uncertain_count} ({very_uncertain_rate:.1f}%)

Fallback Success:
- Total fallback successes: {self.fallback_success} ({fallback_rate:.1f}%)
- Similar name matches: {self.similar_name_matches}
- Context guesses: {self.context_guesses}
- Emergency detections: {self.emergency_detections}
- Unknown speakers (not in DB): {self.unknown_speakers_count}

Overall Quality Score: {100 - placeholder_rate:.1f}%
Target: > 95% (< 5% placeholder rate)
"""
        return report


class MagicBabelApp:
    def __init__(self, root):
        self.root = root
        self.root.withdraw()
        self.root.attributes("-topmost", False)  # เริ่มต้นด้วย unpin
        self.translation_event = threading.Event()
        self.ocr_cache = {}
        self.ocr_speed = "normal"
        self.cache_timeout = 1.0
        self.cpu_limit = 80
        self.cpu_check_interval = 1.0
        self.last_cpu_check = time.time()
        self.ocr_interval = 0.3
        self.last_ocr_time = time.time()
        self.same_text_count = 0
        self.last_signatures = {}

        # Screen Capture Optimization - Cache variables
        self.cached_scale_x = None
        self.cached_scale_y = None
        self.scale_cache_timestamp = 0
        self.scale_cache_timeout = 10.0  # Cache scaling for 10 seconds
        self.full_screen_capture_cache = None
        self.full_screen_capture_timestamp = 0
        self.full_screen_cache_timeout = 0.05  # Cache full screen capture for 50ms (ลดจาก 100ms สำหรับ rapid detection)

        # ✅ เพิ่มตัวแปรสำหรับเก็บ instance ของ NPC Manager
        self.npc_manager_instance = None

        # Game info management
        # FIX: เรียกใช้ฟังก์ชันเพื่ออ่านข้อมูลจาก npc.json โดยตรง
        self.current_game_info = get_game_info_from_npc_file()

        # เพิ่มการตรวจสอบเผื่อในกรณีที่ไฟล์ npc.json ไม่มีข้อมูล _game_info
        if not self.current_game_info:
            self.logging_manager.log_warning(
                "No _game_info found in NPC file, using default."
            )
            self.current_game_info = {
                "name": "N/A",
                "code": "default",
                "description": "No game info found in NPC.json",
            }

        # สร้าง Settings ก่อนเพื่อใช้ในการตรวจสอบ splash screen
        self.settings = Settings()

        def show_splash():
            # อ่านค่าจาก settings.json โดยตรง
            try:
                import json

                with open("settings.json", "r", encoding="utf-8") as f:
                    settings_data = json.load(f)
                splash_type = settings_data.get("splash_screen_type", "video")
            except Exception as e:
                splash_type = "video"  # ใช้ค่าเริ่มต้นถ้าอ่านไม่ได้

            if splash_type == "off":
                return None, None

            splash = tk.Toplevel(root)
            splash.overrideredirect(True)
            splash.attributes("-topmost", True)

            # Check for video or image based on settings
            video_path = resource_path("MBB_splash_vid.mp4")
            image_path = resource_path("MBB_splash.png")

            try:
                screen_width = splash.winfo_screenwidth()
                screen_height = splash.winfo_screenheight()

                # Use video if setting is "video" and file exists
                if splash_type == "video" and os.path.exists(video_path):
                    # ✅ Proper Fix Solution 2.1: Single Thread + Timer Approach
                    # ไม่ใช้ thread แยก - ทำทุกอย่างใน main thread

                    # Use 60% of screen width for video
                    target_width = int(screen_width * 0.6)

                    # Get video properties
                    cap = cv2.VideoCapture(video_path)
                    video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    video_fps = cap.get(cv2.CAP_PROP_FPS)

                    # Calculate dimensions maintaining aspect ratio
                    aspect_ratio = video_width / video_height
                    target_height = int(target_width / aspect_ratio)

                    # Center the splash window
                    x = (screen_width - target_width) // 2
                    y = (screen_height - target_height) // 2
                    splash.geometry(f"{target_width}x{target_height}+{x}+{y}")
                    splash.configure(bg="black")

                    # Create video label
                    video_label = tk.Label(splash, bg="black")
                    video_label.pack(fill="both", expand=True)

                    # Set initial alpha to 0 (invisible)
                    splash.attributes("-alpha", 0.0)
                    splash.update()

                    # Store state variables
                    splash.cap = cap
                    splash.start_time = time.time()
                    splash.frame_interval = int(
                        1000 / min(video_fps, 30)
                    )  # milliseconds, cap at 30fps
                    splash.target_width = target_width
                    splash.target_height = target_height
                    splash.video_label = video_label

                    def update_frame():
                        """อัพเดต frame ใน main thread เท่านั้น"""
                        try:
                            elapsed = time.time() - splash.start_time

                            # Check if should end (after 5 seconds) - ตรวจสอบให้แน่ใจ
                            if elapsed >= 5.0:
                                try:
                                    if (
                                        hasattr(splash, "cap")
                                        and splash.cap is not None
                                    ):
                                        splash.cap.release()
                                    if splash.winfo_exists():
                                        splash.destroy()
                                except (tk.TclError, AttributeError):
                                    # Window already destroyed or cap doesn't exist
                                    pass
                                return

                            # Read frame
                            ret, frame = splash.cap.read()

                            if not ret:
                                # Loop video - เมื่อจบวิดีโอให้ loop กลับไปเริ่มใหม่
                                splash.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                                ret, frame = splash.cap.read()

                                # ถ้ายังอ่านไม่ได้ ให้แสดงภาพดำแทน
                                if not ret:
                                    # สร้างภาพสีดำแทนวิดีโอ
                                    black_frame = np.zeros(
                                        (splash.target_height, splash.target_width, 3),
                                        dtype=np.uint8,
                                    )
                                    frame = black_frame
                                    ret = True

                            if ret:
                                # Process frame in main thread
                                frame = cv2.resize(
                                    frame, (splash.target_width, splash.target_height)
                                )
                                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                                # Calculate alpha - quadratic fade in for 2 seconds
                                if elapsed < 2.0:
                                    progress = elapsed / 2.0
                                    alpha = progress * progress  # Quadratic ease-in
                                else:
                                    alpha = 1.0

                                # Update UI (ทำใน main thread)
                                img = Image.fromarray(frame)
                                photo = ImageTk.PhotoImage(img)
                                splash.video_label.configure(image=photo)
                                splash.video_label.image = photo

                                # Update window alpha
                                if splash.winfo_exists():
                                    splash.attributes("-alpha", alpha)
                                else:
                                    # ถ้า window ไม่มีแล้วให้หยุด
                                    return

                            # Schedule next frame update
                            if splash.winfo_exists():
                                splash.after(splash.frame_interval, update_frame)
                            else:
                                # Window destroyed, stop updates
                                return

                        except Exception as e:
                            print(f"Splash screen error: {e}")
                            import traceback

                            traceback.print_exc()

                            try:
                                if hasattr(splash, "cap") and splash.cap is not None:
                                    splash.cap.release()
                                if splash.winfo_exists():
                                    splash.destroy()
                            except (tk.TclError, AttributeError):
                                # Window already destroyed or cap doesn't exist
                                pass

                    # Start frame updates (ทำงานใน main thread)
                    splash.after(1, update_frame)

                    return splash, None

                # Use image if setting is "image" or video not available
                elif splash_type == "image" or (
                    splash_type == "video" and not os.path.exists(video_path)
                ):
                    if os.path.exists(image_path):
                        image = Image.open(image_path)
                        image = image.convert("RGBA")

                        # Use 60% of screen width for consistency
                        target_width = int(screen_width * 0.6)
                        aspect_ratio = image.width / image.height
                        target_height = int(target_width / aspect_ratio)

                        image = image.resize(
                            (target_width, target_height), Image.Resampling.LANCZOS
                        )
                        photo = ImageTk.PhotoImage(image)

                        # Create window
                        x = (screen_width - target_width) // 2
                        y = (screen_height - target_height) // 2
                        splash.geometry(f"{target_width}x{target_height}+{x}+{y}")

                        # ✅ แก้ไขตรงนี้: ทำให้พื้นหลังของหน้าต่างโปร่งใส
                        # 1. บอกให้ Window Manager รู้ว่า "สีดำ" คือสีที่โปร่งใส
                        splash.wm_attributes("-transparentcolor", "black")
                        # 2. ตั้งค่าพื้นหลังของหน้าต่างให้เป็นสีดำ (ซึ่งจะถูกทำให้โปร่งใส)
                        splash.configure(bg="black")

                        # Create label with image
                        # 3. ตั้งค่าพื้นหลังของ Label ให้เป็นสีดำด้วย เพื่อให้มันโปร่งใสตามหน้าต่าง
                        label = tk.Label(
                            splash, image=photo, bg="black", bd=0, highlightthickness=0
                        )
                        label.photo = photo
                        label.pack(fill="both", expand=True)

                        # Show with slight fade in to avoid jarring appearance
                        splash.attributes("-alpha", 0.0)
                        splash.update()

                        # Quick fade in (0.3 seconds)
                        for i in range(0, 10):
                            alpha = i / 10.0
                            splash.attributes("-alpha", alpha)
                            splash.update()
                            time.sleep(0.03)

                        # Schedule close after remaining time (~4.7 seconds)
                        def close_splash():
                            try:
                                if splash.winfo_exists():
                                    splash.destroy()
                            except (tk.TclError, AttributeError):
                                # Window already destroyed or doesn't exist
                                pass

                        splash.after(4700, close_splash)

                        return splash, photo
                    else:
                        print(f"No image file found at {image_path}")
                        try:
                            if splash.winfo_exists():
                                splash.destroy()
                        except (tk.TclError, AttributeError):
                            pass
                        return None, None

            except Exception as e:
                print(f"Error loading splash screen: {e}")
                traceback.print_exc()
                try:
                    if splash.winfo_exists():
                        splash.destroy()
                except (tk.TclError, AttributeError):
                    pass
                return None, None

        def _delayed_splash_screen():
            """เรียกแสดง splash screen หลังจากระบบโหลดเสร็จแล้ว"""
            print("🎬 Starting delayed splash screen...")
            self.splash, self.splash_photo = show_splash()
            if self.splash:
                self.splash_start_time = time.time()
                print("✅ Splash screen started successfully")
            else:
                print("ℹ️ Splash screen disabled or failed to load")

        # แสดง splash screen หลังจาก delay 3 วินาที เพื่อให้ทรัพยากรหนักโหลดก่อน
        def delayed_splash():
            self.splash, self.splash_photo = show_splash()
            if self.splash:
                self.splash_start_time = time.time()
                print("✅ Splash screen started after delay")

        # รอ 3 วินาทีก่อนแสดง splash
        self.root.after(3000, delayed_splash)

        # ตัวแปรเริ่มต้น
        self.splash = None
        self.splash_photo = None
        self.splash_start_time = None

        self._cpu_monitor_event = threading.Event()
        self._stop_cpu_monitor_event = threading.Event()
        self._cpu_monitor_thread_instance = None
        self._processing_intensive_task = False
        self.tooltip_window = None

        self._last_preset_switch_display_time = 0.0
        self._min_preset_display_interval = 1.8
        self._active_temp_area_widgets = {}

        self.settings = Settings()
        self.show_guide_var = BooleanVar()
        self.show_guide_var.set(self.settings.get("show_starter_guide", True))

        self.logging_manager = LoggingManager(
            self.settings
        )  # self.logging_manager ถูกสร้างที่นี่

        # [START] โค้ดที่ย้าย/แก้ไข
        self.set_window_properties()  # เรียกใช้เมธอดหลังจาก self.logging_manager ถูกสร้าง
        # [END] โค้ดที่ย้าย/แก้ไข

        self.feature_manager = FeatureManager(app_version="beta")

        disabled_features = self.feature_manager.get_disabled_features()
        if disabled_features:
            self.logging_manager.log_info(
                f"ฟีเจอร์ที่ถูกปิดในเวอร์ชั่นนี้: {', '.join(disabled_features)}"
            )

        self.cpu_limit = self.settings.get("cpu_limit", 80)
        try:
            import psutil

            self.has_psutil = True
            self.logging_manager.log_info("psutil available - CPU monitoring enabled")
        except ImportError:
            self.has_psutil = False
            self.logging_manager.log_warning(
                "psutil not available - CPU monitoring disabled"
            )

        self.font_manager = initialize_font_manager(None, self.settings)
        appearance_manager.settings = self.settings

        # โหลดธีมจาก settings ก่อนสร้าง UI เพื่อให้ version_label ใช้สีถูกต้อง
        self.logging_manager.log_info("โหลดข้อมูลธีมและการตั้งค่าจาก AppearanceManager...")
        appearance_manager.load_custom_themes(self.settings)
        saved_theme_name_val_init_final = self.settings.get("theme", None)

        if (
            saved_theme_name_val_init_final
            and saved_theme_name_val_init_final
            in self.settings.get("custom_themes", {})
        ):
            if appearance_manager.set_theme(saved_theme_name_val_init_final):
                self.logging_manager.log_info(
                    f"โหลดธีม {saved_theme_name_val_init_final} จาก settings.json"
                )
            else:
                default_theme_name_val_init_final = "Theme2"
                appearance_manager.set_theme(default_theme_name_val_init_final)
                self.settings.set("theme", default_theme_name_val_init_final)
                self.logging_manager.log_warning(
                    f"ไม่พบธีม {saved_theme_name_val_init_final} ในระบบ, ใช้ธีมเริ่มต้น {default_theme_name_val_init_final}"
                )
        else:
            default_theme_name_val_init_final = "Theme2"
            appearance_manager.set_theme(default_theme_name_val_init_final)
            self.settings.set("theme", default_theme_name_val_init_final)
            self.logging_manager.log_info(
                f"ใช้ธีมเริ่มต้น {default_theme_name_val_init_final}"
            )

        self.text_corrector = TextCorrector()
        try:
            self.text_corrector.reload_data()
            self.logging_manager.log_info(
                f"Loaded {len(self.text_corrector.names) if hasattr(self.text_corrector, 'names') else 0} character names during init (TextCorrector)"
            )
        except Exception as e_tc_init_load_final:
            self.logging_manager.log_error(
                f"Error initializing TextCorrector or reloading its NPC data: {e_tc_init_load_final}"
            )

        # ระบบ cache ชื่อผู้พูดล่าสุด
        self.recent_speakers_cache = []
        self.max_recent_speakers = 5

        # เพิ่มตัวแปรใหม่สำหรับระบบ speaker detection ที่ปรับปรุง
        self.speaker_frequency = {}
        self.max_speaker_frequency_entries = 100
        self.translation_metrics = TranslationMetrics()

        self.paddle_ocr_engine = None
        self.has_paddleocr = False
        self.logging_manager.log_info(
            "Using EasyOCR with improved line grouping (PaddleOCR disabled)"
        )

        self.hotkeys = {}
        self.blink_interval = 500
        self.init_variables()
        self.load_shortcuts()
        self.load_icons()

        self.last_main_ui_pos = None
        self.last_mini_ui_pos = None
        self.last_translated_ui_pos = None

        self.mini_ui = MiniUI(self.root, self.show_main_ui_from_mini)
        self.mini_ui.set_toggle_translation_callback(self.toggle_translation)
        if hasattr(self, "blink_interval"):
            self.mini_ui.blink_interval = self.blink_interval
        else:
            self.blink_interval = 500
            self.mini_ui.blink_interval = self.blink_interval
            self.logging_manager.log_warning(
                "MagicBabelApp.blink_interval was not set by init_variables, using default 500ms in __init__."
            )

        self.create_main_ui()
        self.create_translated_ui()
        self.create_translated_logs()
        self.create_settings_ui()
        self.root.after(50, self.reset_mini_button_state)

        control_root = tk.Toplevel(self.root)
        control_root.protocol("WM_DELETE_WINDOW", lambda: self.on_control_close())

        # ตั้งค่าไอคอนสำหรับ Control UI
        try:
            from icon_manager import set_window_icon_simple

            set_window_icon_simple(control_root)
        except Exception:
            pass

        self.control_ui = Control_UI(
            control_root,
            self.force_translate,
            self.switch_area,
            self.settings,
            parent_app=self,
            parent_callback=self.set_cpu_limit,
            trigger_temporary_area_display_callback=self.trigger_temporary_area_display,
            toggle_click_callback=self.set_click_translate_mode,
            toggle_hover_callback=self.toggle_hover_translation,
        )
        control_root.withdraw()

        # Sync hover translation state after Control UI is created
        hover_enabled = self.settings.get("enable_hover_translation", False)
        if hover_enabled:
            logging.info("Syncing hover translation state after Control UI creation")
            # Delay to ensure UI is fully initialized
            self.root.after(500, lambda: self.toggle_hover_translation(hover_enabled))

        appearance_manager.set_theme_change_callback(self._apply_theme_update)
        self.logging_manager.log_info(
            "Theme change callback registered with AppearanceManager."
        )
        self.custom_font = appearance_manager.apply_style(self.root)

        current_theme_applied_val_init_final = appearance_manager.get_current_theme()
        current_accent_color_val_init_final = appearance_manager.get_accent_color()
        self.logging_manager.log_info(
            f"ธีมที่กำลังใช้งาน: {current_theme_applied_val_init_final}, สีหลัก: {current_accent_color_val_init_final}"
        )

        model_log_name_val_init_final = self.settings.get_displayed_model()
        screen_log_size_val_init_final = self.settings.get("screen_size", "2560x1440")
        use_gpu_log_setting_val_init_final = self.settings.get("use_gpu_for_ocr", False)
        self.logging_manager.log_info("=== MagicBabel System Configuration ===")
        self.logging_manager.log_info(
            f"Default Translation Model: {model_log_name_val_init_final}"
        )
        self.logging_manager.log_info(
            f"Target Game Screen Size: {screen_log_size_val_init_final}"
        )
        self.logging_manager.log_info(
            f"EasyOCR GPU Usage Setting: {'Enabled' if use_gpu_log_setting_val_init_final else 'Disabled'}"
        )
        self.logging_manager.log_info(
            "PaddleOCR will use default/auto GPU/CPU detection based on installed 'paddlepaddle' library."
        )
        self.logging_manager.log_info("=======================================")

        self.current_game_info = get_game_info_from_npc_file()

        self.sync_initial_areas()

        self.init_ocr_and_translation()
        self.bind_events()
        self.apply_saved_settings()

        self.root.after(5000, self._complete_startup)  # รอ 5 วินาทีเสมอ

        if self.has_psutil:
            self._cpu_monitor_thread_instance = threading.Thread(
                target=self._cpu_monitor_thread, daemon=True, name="CPUMonitorThread"
            )
            self._cpu_monitor_thread_instance.start()
            self.logging_manager.log_info("CPU Monitor thread started.")
        else:
            self.logging_manager.log_info(
                "CPU Monitor thread not started (psutil unavailable)."
            )

    # เมื่อต้องการปล่อยเวอร์ชั่นเต็ม ให้เปลี่ยน app_version เป็น "release"
    # self.feature_manager = FeatureManager(app_version="release")

    def _show_feature_disabled_message(self, feature_name):
        """แสดงข้อความเมื่อผู้ใช้พยายามเข้าถึงฟีเจอร์ที่ถูกปิดในเวอร์ชั่นทดสอบ"""
        try:
            version_info = (
                "เวอร์ชั่นทดลอง"
                if self.feature_manager.app_version == "beta"
                else self.feature_manager.app_version
            )
            messagebox.showinfo(
                "ฟีเจอร์ยังไม่เปิดใช้งาน",
                f"ฟีเจอร์ '{feature_name}' ยังไม่เปิดให้ใช้งานใน{version_info}\n\n"
                f"ฟีเจอร์นี้จะเปิดให้ใช้งานในเวอร์ชั่นถัดไป",
            )
            self.logging_manager.log_info(
                f"ผู้ใช้พยายามเข้าถึงฟีเจอร์ '{feature_name}' ที่ยังไม่เปิดใช้งาน"
            )
        except Exception as e:
            self.logging_manager.log_error(f"เกิดข้อผิดพลาดในการแสดงข้อความแจ้งเตือน: {e}")

    def _complete_startup(self):
        """แยกฟังก์ชันสำหรับจัดการส่วนสุดท้ายของการเริ่มต้นโปรแกรม"""
        try:
            # ตรวจสอบว่าผ่านมา 5 วินาทีหรือยัง
            if hasattr(self, "splash_start_time"):
                elapsed = time.time() - self.splash_start_time
                if elapsed < 5.0:
                    # ถ้ายังไม่ครบ 5 วินาที ให้รอต่อ
                    remaining = int((5.0 - elapsed) * 1000)
                    self.root.after(remaining, self._complete_startup)
                    return

            # ปิด splash screen (ถ้ายังเปิดอยู่)
            if hasattr(self, "splash") and self.splash and self.splash.winfo_exists():
                try:
                    # ถ้าเป็นวิดีโอ จะมี self.splash.playing attribute
                    if hasattr(self.splash, "playing"):
                        self.splash.playing = False  # หยุดวิดีโอ
                        # รอให้ thread จบการทำงาน
                        time.sleep(0.2)
                    else:
                        # สำหรับรูปภาพ ถ้ายังแสดงอยู่ให้ fade out
                        current_alpha = float(self.splash.attributes("-alpha"))
                        if current_alpha > 0:
                            steps = int(current_alpha * 10)
                            for i in range(steps, -1, -1):
                                alpha = i / 10.0
                                self.splash.attributes("-alpha", alpha)
                                self.splash.update()
                                time.sleep(0.02)

                    # ปิด splash window อย่างปลอดภัย
                    if hasattr(self, "splash") and self.splash is not None:
                        try:
                            if self.splash.winfo_exists():
                                self.splash.destroy()
                        except tk.TclError:
                            # Window ถูก destroy ไปแล้ว - ไม่เป็นไร
                            pass
                        finally:
                            self.splash = None
                except Exception as e:
                    self.logging_manager.log_error(f"Error closing splash: {e}")
                    # ทำความสะอาด splash reference
                    if hasattr(self, "splash"):
                        self.splash = None

            # แสดง main window และตั้งค่าให้ไม่มีขอบ
            self.root.deiconify()
            self.root.overrideredirect(True)  # สำคัญ: ต้องตั้งค่าหลังจาก deiconify
            self.root.update()  # บังคับให้ window อัพเดท

            # ตรวจสอบสถานะ PIN และแสดงขอบถ้าจำเป็น (หลังจาก window พร้อมแล้ว)
            if self.root.attributes("-topmost"):
                # รอให้ window render เสร็จก่อนแสดงขอบ
                self.root.after(100, lambda: self._update_pin_border(True))

            self.logging_manager.log_info("MagicBabel application started and ready")

            # Splash screen จะถูกแสดงหลัง delay แล้ว
            print("Application fully started and ready")

            # เพิ่มการโหลดข้อมูล NPC
            self.reload_npc_data()
            self.logging_manager.log_info("Reloaded NPC data during startup")

            # โหลดตำแหน่ง UI ที่บันทึกไว้จากการใช้งานครั้งก่อน
            self.logging_manager.log_info(
                "กำลังโหลดตำแหน่งหน้าต่าง UI จากการใช้งานครั้งก่อน..."
            )
            self.load_ui_positions()

            # เริ่มต้นระบบ Hover Translation
            self.init_hover_translator()

            # เริ่มต้นระบบตรวจสอบความสอดคล้องของ TUI state
            self.root.after(2000, self.ensure_tui_state_consistency)

            # *** แก้ไข: แสดง Starter Guide เฉพาะเมื่อตั้งค่าไว้ หรือเมื่อ force_show=True ***
            # ใช้ after เพื่อให้แน่ใจว่า main window แสดงก่อน
            # และตรวจสอบค่าจาก self.show_guide_var (ซึ่งโหลดค่าจาก settings มาแล้ว)
            if self.show_guide_var.get():
                self.root.after(1000, self.show_starter_guide)  # ไม่ต้องส่ง force_show

        except Exception as e:
            self.logging_manager.log_error(f"Error in _complete_startup: {e}")
            # กรณีเกิดข้อผิดพลาด ให้แสดง main window
            self.root.deiconify()
            self.root.overrideredirect(True)

    def set_window_properties(self):
        """ตั้งค่าชื่อและไอคอนของหน้าต่างหลักเพื่อแสดงใน Taskbar/Task Manager"""
        # ตั้งชื่อหน้าต่าง
        self.root.title("MBB-V-8")
        self.logging_manager.log_info("ตั้งชื่อหน้าต่างเป็น MBB-V-8")  # เพิ่ม log

        # ตั้งค่าไอคอนด้วย Icon Manager
        from icon_manager import set_window_icon

        set_window_icon(self.root, "assets/app_icon.ico", self.logging_manager)

    def is_translating(self):
        """ตรวจสอบว่าการแปลหลักกำลังทำงานอยู่หรือไม่

        Returns:
            bool: True ถ้ากำลังแปลอยู่, False ถ้าไม่ได้แปลอยู่
        """
        return getattr(self, "is_translating", False)

    def init_hover_translator(self):
        """เริ่มต้นระบบ Hover Translation โดยตรวจสอบการเปิดใช้งานฟีเจอร์ก่อน"""
        try:
            # ตรวจสอบว่าฟีเจอร์นี้เปิดใช้งานหรือไม่
            if not self.feature_manager.is_feature_enabled("hover_translation"):
                logging.info("Hover Translation feature is disabled in this version")
                return  # ไม่ต้องสร้าง hover_translator

            logging.info("Attempting to initialize Hover Translator...")  # เพิ่ม Log
            hover_callbacks = {
                "get_screen_scale": self.get_screen_scale,
                "is_manual_show_area_active": self.is_show_area_active,
                # แก้ไขตรงนี้: ใช้ lambda เพื่อส่งค่า is_translating โดยตรง
                "is_translation_active": lambda: self.is_translating,
                # "show_feedback": self.show_feedback_message,
            }
            # ตรวจสอบว่า self.control_ui มีอยู่จริงก่อนส่งต่อ
            if hasattr(self, "control_ui") and self.control_ui:
                logging.info(
                    f"Control UI instance provided to HoverTranslator: {self.control_ui}"
                )  # เพิ่ม Log
                self.hover_translator = HoverTranslator(
                    self.root,
                    self.settings,
                    hover_callbacks,
                    control_ui_instance=self.control_ui,  # ส่ง control_ui instance ที่สร้างไว้แล้ว
                )
                logging.info("Hover Translation system initialized successfully.")
            else:
                logging.error(
                    "Control UI instance is not available when initializing Hover Translator!"
                )  # เพิ่ม Log Error
                self.hover_translator = None  # ไม่สร้างถ้า control_ui ไม่มี
        except Exception as e:
            self.logging_manager.log_error(
                f"Error initializing Hover Translator: {e}", exc_info=True
            )  # เพิ่ม exc_info=True
            self.hover_translator = None

    def select_preset_in_control_ui(self, preset_num):
        """สั่งให้ control_ui เลือก preset (เหมือนผู้ใช้กดปุ่มเอง)"""
        if hasattr(self, "control_ui") and self.control_ui:
            # เรียกฟังก์ชัน select_preset ซึ่งจะทำทุกขั้นตอนที่จำเป็น
            self.control_ui.select_preset(preset_num)
            logging.info(
                f"Control UI selected preset {preset_num} via hover translation"
            )

    def toggle_hover_translation(self, value):
        """
        เปิด/ปิดระบบ Hover Translation และอัพเดท UI ที่เกี่ยวข้อง
        ถูกเรียกใช้โดย Callback จาก SettingsUI หรือ ControlUI
        """
        try:
            logging.info(f"MBB: toggle_hover_translation called with value: {value}")

            # ตรวจสอบว่า control_ui และ hover_translator พร้อมหรือไม่
            if not hasattr(self, "control_ui") or not self.control_ui:
                logging.warning(
                    "MBB: Control UI not initialized yet when toggling hover translation"
                )
                # บันทึกค่าไว้ก่อน และ retry หลัง 500ms
                self.settings.set("enable_hover_translation", value)
                if value:  # ถ้าพยายามเปิด ให้ retry
                    self.root.after(500, lambda: self.toggle_hover_translation(value))
                return

            if not hasattr(self, "hover_translator") or not self.hover_translator:
                logging.warning("MBB: Hover translator not initialized yet")
                # บันทึกค่าไว้ก่อน และ retry หลัง 500ms
                self.settings.set("enable_hover_translation", value)
                if value:  # ถ้าพยายามเปิด ให้ retry
                    self.root.after(500, lambda: self.toggle_hover_translation(value))
                return

            # ตรวจสอบว่าฟีเจอร์นี้ถูกเปิดใช้งานหรือไม่
            if not self.feature_manager.is_feature_enabled("hover_translation"):
                self._show_feature_disabled_message("Hover Translation")

                # รีเซ็ต UI elements ที่เกี่ยวข้องให้เป็น OFF
                if value == True:  # ถ้ากำลังพยายามเปิด
                    # อัพเดท Control UI
                    if hasattr(self, "control_ui") and self.control_ui:
                        if hasattr(self.control_ui, "update_hover_translate_toggle"):
                            self.control_ui.update_hover_translate_toggle(False)

                    # อัพเดท Settings UI
                    if hasattr(self, "settings_ui") and self.settings_ui:
                        if hasattr(self.settings_ui, "hover_translation_var"):
                            self.settings_ui.hover_translation_var.set(False)

                    # อัพเดทค่าใน Settings
                    self.settings.set("enable_hover_translation", False)

                return  # ออกจากฟังก์ชัน ไม่ดำเนินการต่อ

            logging.info(f"MBB: toggle_hover_translation called with value: {value}")

            # 1. อัพเดทค่าใน Settings
            current_setting = self.settings.get("enable_hover_translation", False)
            if current_setting != value:
                self.settings.set("enable_hover_translation", value)
                logging.debug(
                    f"MBB: Setting 'enable_hover_translation' updated to {value}"
                )
            else:
                logging.debug(
                    f"MBB: Setting 'enable_hover_translation' is already {value}"
                )

            # 2. สั่งเปิด/ปิดการทำงานจริงของ HoverTranslator
            hover_ready = hasattr(self, "hover_translator") and self.hover_translator
            enabled_state = False  # สถานะเริ่มต้น
            if hover_ready:
                try:
                    enabled_state = self.hover_translator.toggle(value)
                    logging.info(
                        f"MBB: Hover Translator toggled. Reported state: {enabled_state}"
                    )
                except Exception as toggle_err:
                    logging.error(
                        f"MBB: Error calling hover_translator.toggle: {toggle_err}",
                        exc_info=True,
                    )
                    # ถ้า toggle ไม่สำเร็จ ควรตั้งค่า setting กลับไปเป็น False และแจ้งเตือน
                    self.settings.set("enable_hover_translation", False)
                    value = False  # อัพเดทค่า value ที่จะส่งไป UI
                    enabled_state = False
                    messagebox.showerror(
                        "Hover Error", f"Failed to toggle Hover system: {toggle_err}"
                    )
            else:
                logging.warning(
                    "MBB: Hover Translation system not initialized or unavailable. Cannot toggle functionality."
                )
                # ถ้า Hover ทำงานไม่ได้ ควรตั้งค่า setting เป็น False ด้วย
                self.settings.set("enable_hover_translation", False)
                value = False  # อัพเดทค่า value ที่จะส่งไป UI

            # *** 3. สั่งให้ Control UI อัพเดท Toggle Switch ของตัวเอง ***
            control_ui_ready = hasattr(self, "control_ui") and self.control_ui
            if control_ui_ready:
                if hasattr(self.control_ui, "update_hover_translate_toggle"):
                    logging.debug(
                        f"MBB: Calling control_ui.update_hover_translate_toggle({value})"
                    )
                    # ต้องแน่ใจว่าเรียกด้วยค่า value ล่าสุด (ซึ่งอาจเปลี่ยนเป็น False ถ้า toggle ไม่สำเร็จ)
                    self.control_ui.update_hover_translate_toggle(value)
                else:
                    logging.warning(
                        "MBB: control_ui missing 'update_hover_translate_toggle' method."
                    )
            else:
                logging.warning("MBB: control_ui instance not available for UI update.")

            # 4. (Optional but recommended) อัพเดท Settings UI Toggle ด้วย (เผื่อ trace_add มีปัญหา)
            settings_ui_ready = hasattr(self, "settings_ui") and self.settings_ui
            if settings_ui_ready:
                if hasattr(self.settings_ui, "hover_translation_var"):
                    if self.settings_ui.hover_translation_var.get() != value:
                        logging.debug(
                            f"MBB: Forcing SettingsUI hover_translation_var to {value}"
                        )
                        self.settings_ui.hover_translation_var.set(
                            value
                        )  # อัพเดท BooleanVar โดยตรง
                else:
                    logging.warning("MBB: settings_ui missing 'hover_translation_var'.")

        except Exception as e:
            logging.error(f"MBB: Error in toggle_hover_translation: {e}", exc_info=True)
            messagebox.showerror(
                "Hover Error", f"Failed to toggle Hover Translation:\n{e}"
            )

    def set_click_translate_mode(self, value):
        """
        ตั้งค่าโหมด Click Translate และอัพเดท UI ที่เกี่ยวข้อง
        ถูกเรียกใช้โดย Callback จาก SettingsUI หรือ ControlUI
        """
        try:
            # Log ค่าที่ได้รับเข้ามาทันที
            logging.info(
                f"MBB: set_click_translate_mode called with value: {value} (Type: {type(value)})"
            )

            # ตรวจสอบประเภทข้อมูล (ควรจะเป็น bool)
            if not isinstance(value, bool):
                logging.warning(
                    f"MBB: Received non-boolean value in set_click_translate_mode: {value}. Attempting to convert."
                )
                # พยายามแปลงค่า ถ้าไม่แน่ใจประเภท
                if isinstance(value, (int, float)):
                    value = bool(value)
                elif isinstance(value, str):
                    value = value.lower() in ["true", "1", "t", "y", "yes"]
                else:
                    logging.error(
                        "MBB: Cannot convert received value to boolean. Aborting mode set."
                    )
                    return  # ออกถ้าแปลงค่าไม่ได้

            # 1. อัพเดทค่าใน Settings
            current_setting = self.settings.get("enable_click_translate", False)
            if current_setting != value:
                self.settings.set("enable_click_translate", value)
                logging.info(
                    f"MBB: Setting 'enable_click_translate' updated to {value}"
                )  # ใช้ info แทน debug
            else:
                logging.debug(
                    f"MBB: Setting 'enable_click_translate' is already {value}"
                )

            # 2. อัพเดทการทำงานหลัก (เช่น translation_event)
            if hasattr(self, "translation_event") and isinstance(
                self.translation_event, threading.Event
            ):
                if value:  # เปิด Click Translate
                    self.translation_event.clear()
                    self._update_status_line("🖱️ Click Translate Mode: ON")
                    logging.debug(
                        "MBB: Translation event cleared (Click Translate ON)."
                    )
                else:  # ปิด Click Translate (เปิด Auto Translate)
                    self.translation_event.set()
                    self._update_status_line("⚡ Auto Translate Mode: ON")
                    logging.debug("MBB: Translation event set (Click Translate OFF).")
            else:
                logging.warning("MBB: translation_event not found or invalid type.")

            # *** 3. สั่งให้ Control UI อัพเดท Toggle Switch ของตัวเอง ***
            # สร้างฟังก์ชันย่อยเพื่อเรียกการอัปเดท UI (สำหรับใช้กับ root.after)
            def update_control_ui_toggle():
                control_ui_ready = hasattr(self, "control_ui") and self.control_ui
                if control_ui_ready:
                    logging.debug(
                        "MBB: Checking Control UI readiness for Click Translate toggle update..."
                    )
                    # ตรวจสอบว่า Control UI และหน้าต่างของมันยังอยู่
                    if self.control_ui.root and self.control_ui.root.winfo_exists():
                        if hasattr(self.control_ui, "update_click_translate_toggle"):
                            logging.info(
                                f"MBB: Scheduling control_ui.update_click_translate_toggle({value}) via root.after"
                            )  # ใช้ info
                            try:
                                self.control_ui.update_click_translate_toggle(value)
                                logging.info(
                                    f"MBB: control_ui.update_click_translate_toggle({value}) call successful."
                                )  # ใช้ info
                                # เพิ่ม: เรียกอัพเดท UI ปุ่ม Force ใน Control UI ด้วย
                                if hasattr(self.control_ui, "_update_force_button_ui"):
                                    logging.debug(
                                        f"MBB: Calling control_ui._update_force_button_ui({value})"
                                    )
                                    self.control_ui._update_force_button_ui(value)
                                else:
                                    logging.warning(
                                        "MBB: control_ui missing '_update_force_button_ui' method."
                                    )
                            except Exception as update_err:
                                logging.error(
                                    f"MBB: Error during control_ui.update_click_translate_toggle call: {update_err}",
                                    exc_info=True,
                                )
                        else:
                            logging.error(
                                "MBB: control_ui missing 'update_click_translate_toggle' method."
                            )  # ใช้ error
                    else:
                        logging.warning(
                            "MBB: control_ui root window destroyed or not available. Cannot update toggle."
                        )
                else:
                    logging.error(
                        "MBB: control_ui instance not available for UI update."
                    )  # ใช้ error

            # *** ใช้ self.root.after(0, ...) เพื่อให้แน่ใจว่าการอัพเดท UI ทำใน Main Thread ***
            if hasattr(self, "root") and self.root.winfo_exists():
                self.root.after(0, update_control_ui_toggle)
            else:
                logging.error(
                    "MBB: Root window not available, cannot schedule Control UI update."
                )

            # 4. (Optional) สั่งให้ Settings UI อัพเดท Toggle ของตัวเอง (อาจไม่จำเป็น)
            settings_ui_ready = hasattr(self, "settings_ui") and self.settings_ui
            if settings_ui_ready:
                if hasattr(self.settings_ui, "click_translate_var"):
                    if self.settings_ui.click_translate_var.get() != value:
                        logging.debug(
                            f"MBB: Forcing SettingsUI click_translate_var to {value}"
                        )
                        self.settings_ui.click_translate_var.set(value)
                else:
                    logging.warning("MBB: settings_ui missing 'click_translate_var'.")

        except Exception as e:
            logging.error(f"MBB: Error in set_click_translate_mode: {e}", exc_info=True)

    def show_feedback_message(self, message):
        """แสดงข้อความแจ้งเตือนสั้นๆ"""
        try:
            if hasattr(self, "translated_ui") and self.translated_ui:
                # ถ้ามีเมธอด show_feedback_message ใน translated_ui ให้ใช้
                if hasattr(self.translated_ui, "show_feedback_message"):
                    self.translated_ui.show_feedback_message(message)
                    return

            # ถ้าไม่มี ให้สร้างหน้าต่างแจ้งเตือนชั่วคราวเอง
            feedback = tk.Toplevel(self.root)
            feedback.overrideredirect(True)
            feedback.attributes("-alpha", 0.9)
            feedback.attributes("-topmost", True)

            # ใช้สีตาม theme
            bg_color = (
                self.appearance_manager.bg_color
                if hasattr(self, "appearance_manager")
                else "#262637"
            )
            text_color = (
                self.appearance_manager.get_theme_color("text")
                if hasattr(self, "appearance_manager")
                else "#ffffff"
            )

            # สร้าง label สำหรับข้อความ
            label = tk.Label(
                feedback,
                text=message,
                font=("Anuphan", 16),
                fg=text_color,
                bg=bg_color,
                padx=20,
                pady=10,
            )
            label.pack()

            # จัดตำแหน่งให้อยู่ตรงกลางจอ
            feedback.update_idletasks()
            width = feedback.winfo_width()
            height = feedback.winfo_height()
            x = (self.root.winfo_screenwidth() // 2) - (width // 2)
            y = (self.root.winfo_screenheight() // 2) - (height // 2)
            feedback.geometry(f"{width}x{height}+{x}+{y}")

            # ให้หน้าต่างหายไปหลังจาก 1.5 วินาที
            def fade_out():
                for i in range(10, -1, -1):
                    if feedback.winfo_exists():
                        feedback.attributes("-alpha", i / 10)
                        feedback.update()
                        time.sleep(0.03)
                    if feedback.winfo_exists():
                        feedback.destroy()

            self.root.after(
                1500, lambda: threading.Thread(target=fade_out, daemon=True).start()
            )

        except Exception as e:
            logging.error(f"Error showing feedback message: {e}")

    def _clear_active_temp_areas(self):
        """ทำลายหน้าต่างและยกเลิก animation ของ temporary areas ที่กำลังแสดงผลอยู่"""
        # logging.debug(f"Clearing active temporary areas: {list(self._active_temp_area_widgets.keys())}")
        for area, widgets in list(self._active_temp_area_widgets.items()):
            if widgets:
                fade_job = widgets.get("fade_job")
                window = widgets.get("window")

                # ยกเลิก after job ถ้ามี
                if fade_job:
                    try:
                        self.root.after_cancel(fade_job)
                        # logging.debug(f"Cancelled fade job for area {area}")
                    except ValueError:  # อาจจะถูก cancel ไปแล้ว
                        pass
                    except Exception as e:
                        logging.warning(
                            f"Error cancelling fade job for area {area}: {e}"
                        )

                # ทำลายหน้าต่างถ้ายังอยู่
                if window and window.winfo_exists():
                    try:
                        window.destroy()
                        # logging.debug(f"Destroyed temporary window for area {area}")
                    except tk.TclError:  # อาจจะถูกทำลายไปแล้ว
                        pass
                    except Exception as e:
                        logging.warning(
                            f"Error destroying temporary window for area {area}: {e}"
                        )

        # เคลียร์ dictionary
        self._active_temp_area_widgets.clear()
        # logging.debug("Active temporary areas cleared.")

    def trigger_temporary_area_display(self, area_string):
        try:
            # อ่านค่า is_show_area_active จาก control_ui มาเก็บในตัวแปร local ก่อน
            is_manual_show_area_active_in_control_ui = False
            if (
                hasattr(self, "control_ui")
                and self.control_ui
                and hasattr(self.control_ui, "is_show_area_active")
            ):
                is_manual_show_area_active_in_control_ui = (
                    self.control_ui.is_show_area_active()
                )

            if is_manual_show_area_active_in_control_ui:
                logging.info(
                    "MBB.py: Manual 'Show Area' (from Control_UI) is active, skipping temporary display."
                )
                return

            current_time = time.time()
            # ตรวจสอบว่า _last_preset_switch_display_time และ _min_preset_display_interval มีอยู่
            if not hasattr(self, "_last_preset_switch_display_time"):
                self._last_preset_switch_display_time = 0.0
            if not hasattr(self, "_min_preset_display_interval"):
                self._min_preset_display_interval = 1.8

            time_since_last = current_time - self._last_preset_switch_display_time

            if hasattr(self, "_clear_active_temp_areas"):
                self._clear_active_temp_areas()
            else:
                logging.warning(
                    "MBB.py: _clear_active_temp_areas method not found for temporary display."
                )

            areas_to_display = sorted(
                [a for a in area_string.split("+") if a in ["A", "B", "C"]]
            )
            if not areas_to_display:
                logging.warning(
                    f"MBB.py: No valid areas in area_string for temporary display: '{area_string}'"
                )
                return

            if hasattr(self, "_show_quick_area") and hasattr(
                self, "_show_animated_area"
            ):
                if time_since_last < self._min_preset_display_interval:
                    # logging.info(f"MBB.py: Rapid preset switch. Showing quick temporary area display for {areas_to_display}.")
                    self._show_quick_area(areas_to_display, duration=1000)
                else:
                    # logging.info(f"MBB.py: Showing animated temporary area display for areas: {areas_to_display}")
                    self._show_animated_area(
                        areas_to_display, duration=1800, fade_duration=300
                    )
            else:
                logging.warning(
                    "MBB.py: Methods for showing temporary area display (_show_quick_area or _show_animated_area) not found."
                )

            self._last_preset_switch_display_time = current_time

        except AttributeError as ae:  # จับ AttributeError โดยเฉพาะ
            self.logging_manager.log_error(
                f"MBB.py trigger_temporary_area_display AttributeError: {ae} - Attribute likely missing from MagicBabelApp or Control_UI."
            )
            import traceback

            self.logging_manager.log_error(traceback.format_exc())
        except Exception as e:
            self.logging_manager.log_error(
                f"Error in MBB.py trigger_temporary_area_display: {e}"
            )

            self.logging_manager.log_error(traceback.format_exc())

    def _show_animated_area(self, areas_to_display, duration=1800, fade_duration=300):
        """แสดงพื้นที่ที่ระบุพร้อม Animation Fade-in/Fade-out และ Label"""
        try:
            logging.info(
                f"--- Starting _show_animated_area for: {areas_to_display} ---"
            )  # Log เริ่มต้น
            base_alpha = 0.6  # ความโปร่งใสสูงสุดตอนแสดงผล
            steps = 10  # จำนวนขั้นในการ fade
            interval = (
                fade_duration // steps if steps > 0 else fade_duration
            )  # เวลาระหว่างแต่ละ step (ms)
            if interval <= 0:
                interval = 10  # ป้องกัน interval เป็น 0 หรือลบ

            # *** เพิ่ม: ล้างข้อมูลเก่าก่อนเริ่มสร้างใหม่ (ย้ายมาจาก trigger) ***
            self._clear_active_temp_areas()

            created_windows = 0  # ตัวนับจำนวน window ที่สร้างสำเร็จ

            for area in areas_to_display:
                logging.debug(f"Processing area: {area}")
                translate_area = self.settings.get_translate_area(area)

                # *** เพิ่ม Log ตรวจสอบข้อมูลพิกัด ***
                if not translate_area:
                    logging.warning(
                        f"No coordinates found for area '{area}' in settings."
                    )
                    continue
                logging.debug(f"Coordinates for area '{area}': {translate_area}")

                # คำนวณพิกัดและขนาด
                scale_x, scale_y = self.get_screen_scale()
                start_x_coord = translate_area.get("start_x", 0)
                start_y_coord = translate_area.get("start_y", 0)
                end_x_coord = translate_area.get("end_x", 0)
                end_y_coord = translate_area.get("end_y", 0)

                x = int(start_x_coord * scale_x)
                y = int(start_y_coord * scale_y)
                width = int((end_x_coord - start_x_coord) * scale_x)
                height = int((end_y_coord - start_y_coord) * scale_y)

                # *** เพิ่ม Log ตรวจสอบขนาด ***
                logging.debug(
                    f"Calculated geometry for area '{area}': w={width}, h={height}, x={x}, y={y}"
                )

                # ป้องกันขนาดเล็กหรือติดลบ
                if width <= 1 or height <= 1:
                    logging.warning(
                        f"Area '{area}' size is invalid ({width}x{height}), skipping display."
                    )
                    continue

                # สร้างหน้าต่าง Toplevel
                try:
                    window = tk.Toplevel(self.root)
                    window.overrideredirect(True)
                    window.attributes("-topmost", True)
                    window.geometry(f"{width}x{height}+{x}+{y}")
                    window.config(bg="black")  # สีที่จะทำให้โปร่งใส
                    window.attributes("-transparentcolor", "black")

                    # สร้างกรอบสีแดงบางๆ ภายใน Canvas
                    canvas = tk.Canvas(
                        window, bg="black", highlightthickness=0
                    )  # Canvas ใช้ bg สีโปร่งใส
                    canvas.pack(fill=tk.BOTH, expand=True)
                    canvas.create_rectangle(
                        1, 1, width - 1, height - 1, outline="red", width=2
                    )  # วาดกรอบ

                    # ตั้งค่า Alpha เริ่มต้นเป็น 0 (มองไม่เห็น)
                    window.attributes("-alpha", 0.0)

                    # สร้าง Label ตัวอักษร (A, B, C) บน Canvas
                    label_font = ("Nasalization Rg", 18, "bold")
                    label_widget = tk.Label(
                        canvas, text=area, fg="white", bg="red", font=label_font, padx=4
                    )
                    canvas.create_window(
                        5, 2, window=label_widget, anchor="nw"
                    )  # ตำแหน่งมุมบนซ้าย

                    logging.debug(f"Window and label created for area '{area}'.")
                    created_windows += 1

                    # เก็บ widget ไว้ใน dictionary (สำคัญ: ต้องทำก่อนเริ่ม animation)
                    self._active_temp_area_widgets[area] = {
                        "window": window,
                        "label": label_widget,
                        "fade_job": None,
                    }

                    # --- Fade In Animation ---
                    # ใช้ nested function เพื่อให้แน่ใจว่า lambda จับค่า window และ area ที่ถูกต้อง ณ เวลาสร้าง
                    def create_fade_in_lambda(target_area, target_window, step_num):
                        def step_action():
                            # ตรวจสอบก่อนทำงานในแต่ละ step
                            if target_area not in self._active_temp_area_widgets:
                                return
                            active_widgets = self._active_temp_area_widgets[target_area]
                            win = active_widgets.get("window")
                            if (
                                not win
                                or not win.winfo_exists()
                                or win != target_window
                            ):  # ตรวจสอบว่าเป็น window เดิมหรือไม่
                                if target_area in self._active_temp_area_widgets:
                                    del self._active_temp_area_widgets[target_area]
                                return

                            current_alpha = (step_num / steps) * base_alpha
                            try:
                                win.attributes("-alpha", current_alpha)
                            except tk.TclError:
                                if target_area in self._active_temp_area_widgets:
                                    del self._active_temp_area_widgets[target_area]
                                return

                            if step_num < steps:
                                next_step_lambda = create_fade_in_lambda(
                                    target_area, target_window, step_num + 1
                                )
                                job_id = self.root.after(interval, next_step_lambda)
                                if target_area in self._active_temp_area_widgets:
                                    self._active_temp_area_widgets[target_area][
                                        "fade_job"
                                    ] = job_id
                            else:
                                # เมื่อ Fade In เสร็จ ตั้งเวลาสำหรับ Fade Out
                                fade_out_delay = duration - fade_duration
                                if fade_out_delay < 0:
                                    fade_out_delay = 100
                                # สร้าง lambda สำหรับ fade out โดยเฉพาะ
                                fade_out_lambda = (
                                    lambda: self._fade_out_and_destroy_temp_area(
                                        target_area, base_alpha, steps, interval
                                    )
                                )
                                job_id = self.root.after(
                                    fade_out_delay, fade_out_lambda
                                )
                                if target_area in self._active_temp_area_widgets:
                                    self._active_temp_area_widgets[target_area][
                                        "fade_job"
                                    ] = job_id

                        return step_action

                    # เริ่ม Fade In สำหรับ window ปัจจุบัน
                    initial_fade_in_lambda = create_fade_in_lambda(area, window, 1)
                    self.root.after(
                        10, initial_fade_in_lambda
                    )  # หน่วงเล็กน้อยก่อนเริ่ม fade แรก

                except Exception as create_error:
                    logging.error(
                        f"Error creating window/widgets for area '{area}': {create_error}"
                    )
                    # พยายามทำลาย window ที่อาจสร้างไปแล้วบางส่วน
                    if "window" in locals() and window.winfo_exists():
                        try:
                            window.destroy()
                        except:
                            pass
                    continue  # ไปยัง area ถัดไป

            logging.info(
                f"--- Finished _show_animated_area, created {created_windows} windows ---"
            )

        except Exception as e:
            self.logging_manager.log_error(f"Error in _show_animated_area: {e}")
            self._clear_active_temp_areas()  # เคลียร์ทั้งหมดถ้ามีปัญหา

    def _fade_out_and_destroy_temp_area(self, area, start_alpha, steps, interval):
        """จัดการ Animation Fade-out และทำลายหน้าต่างชั่วคราว"""
        if area not in self._active_temp_area_widgets:
            return  # ไม่มี area นี้แล้ว

        widgets = self._active_temp_area_widgets[area]
        window = widgets.get("window")
        if not window or not window.winfo_exists():
            if area in self._active_temp_area_widgets:
                del self._active_temp_area_widgets[area]
            return

        # --- Fade Out Animation ---
        def fade_out_step(current_step):
            # ตรวจสอบก่อนทำงานในแต่ละ step
            if area not in self._active_temp_area_widgets:
                return
            local_widgets = self._active_temp_area_widgets[area]
            local_window = local_widgets.get("window")
            if not local_window or not local_window.winfo_exists():
                if area in self._active_temp_area_widgets:
                    del self._active_temp_area_widgets[area]
                return  # หยุดถ้า window ถูกลบไปแล้ว

            current_alpha = (current_step / steps) * start_alpha
            try:
                local_window.attributes("-alpha", current_alpha)
            except tk.TclError:  # Window อาจถูกทำลายไปแล้ว
                if area in self._active_temp_area_widgets:
                    del self._active_temp_area_widgets[area]
                return

            if current_step > 0:
                job_id = self.root.after(
                    interval, lambda s=current_step - 1: fade_out_step(s)
                )
                # ตรวจสอบอีกครั้งก่อน assign job_id
                if area in self._active_temp_area_widgets:
                    self._active_temp_area_widgets[area]["fade_job"] = job_id
            else:
                # เมื่อ Fade Out เสร็จ ทำลายหน้าต่างและลบออกจาก dict
                try:
                    if local_window.winfo_exists():
                        local_window.destroy()
                except:
                    pass  # ป้องกัน error ถ้า window หายไปแล้ว
                finally:
                    if area in self._active_temp_area_widgets:
                        del self._active_temp_area_widgets[area]
                    # logging.debug(f"Fade out complete, temporary area {area} destroyed.")

        # เริ่ม Fade Out (เริ่มจาก step เต็ม)
        fade_out_step(steps)

    def _show_quick_area(self, areas_to_display, duration=1000):
        """แสดงพื้นที่อย่างรวดเร็วโดยไม่มี Animation หรือ Label"""
        try:
            logging.info(f"--- Starting _show_quick_area for: {areas_to_display} ---")
            quick_alpha = 0.5  # ความโปร่งใสของกรอบแบบเร็ว

            # *** เพิ่ม: ล้างข้อมูลเก่าก่อนเริ่มสร้างใหม่ (ย้ายมาจาก trigger) ***
            self._clear_active_temp_areas()

            created_windows = 0

            for area in areas_to_display:
                logging.debug(f"Processing quick area: {area}")
                translate_area = self.settings.get_translate_area(area)

                if not translate_area:
                    logging.warning(
                        f"No coordinates found for area '{area}' in settings (quick)."
                    )
                    continue
                logging.debug(f"Coordinates for quick area '{area}': {translate_area}")

                # คำนวณพิกัดและขนาด
                scale_x, scale_y = self.get_screen_scale()
                start_x_coord = translate_area.get("start_x", 0)
                start_y_coord = translate_area.get("start_y", 0)
                end_x_coord = translate_area.get("end_x", 0)
                end_y_coord = translate_area.get("end_y", 0)

                x = int(start_x_coord * scale_x)
                y = int(start_y_coord * scale_y)
                width = int((end_x_coord - start_x_coord) * scale_x)
                height = int((end_y_coord - start_y_coord) * scale_y)

                logging.debug(
                    f"Calculated quick geometry for area '{area}': w={width}, h={height}, x={x}, y={y}"
                )

                # ป้องกันขนาดเล็กหรือติดลบ
                if width <= 1 or height <= 1:
                    logging.warning(
                        f"Area '{area}' size is invalid ({width}x{height}), skipping quick display."
                    )
                    continue

                # สร้างหน้าต่าง Toplevel
                try:
                    window = tk.Toplevel(self.root)
                    window.overrideredirect(True)
                    window.attributes("-topmost", True)
                    window.geometry(f"{width}x{height}+{x}+{y}")
                    window.config(bg="black")
                    window.attributes("-transparentcolor", "black")
                    canvas = tk.Canvas(window, bg="black", highlightthickness=0)
                    canvas.pack(fill=tk.BOTH, expand=True)
                    canvas.create_rectangle(
                        1, 1, width - 1, height - 1, outline="red", width=2
                    )  # วาดกรอบ

                    window.attributes(
                        "-alpha", quick_alpha
                    )  # แสดงผลทันทีด้วย alpha ที่กำหนด
                    created_windows += 1

                    # เก็บ widget (เฉพาะ window) และตั้งเวลาทำลาย
                    self._active_temp_area_widgets[area] = {
                        "window": window,
                        "label": None,
                        "fade_job": None,
                    }
                    destroy_lambda = lambda a=area: self._destroy_temp_area(a)
                    job_id = self.root.after(duration, destroy_lambda)
                    # ตรวจสอบก่อน assign job_id
                    if area in self._active_temp_area_widgets:
                        self._active_temp_area_widgets[area]["fade_job"] = job_id

                except Exception as create_error:
                    logging.error(
                        f"Error creating quick window for area '{area}': {create_error}"
                    )
                    if "window" in locals() and window.winfo_exists():
                        try:
                            window.destroy()
                        except:
                            pass
                    continue  # ไปยัง area ถัดไป

            logging.info(
                f"--- Finished _show_quick_area, created {created_windows} windows ---"
            )

        except Exception as e:
            self.logging_manager.log_error(f"Error in _show_quick_area: {e}")
            self._clear_active_temp_areas()  # เคลียร์ทั้งหมดถ้ามีปัญหา

    def _destroy_temp_area(self, area):
        """ทำลายหน้าต่างของ temporary area ที่ระบุ"""
        if area in self._active_temp_area_widgets:
            widgets = self._active_temp_area_widgets[area]
            window = widgets.get("window")
            if window and window.winfo_exists():
                try:
                    window.destroy()
                except:
                    pass  # ป้องกัน error ถ้า window หายไปแล้ว
            # ใช้ pop เพื่อลบและคืนค่า ถ้าต้องการ log เพิ่มเติม
            self._active_temp_area_widgets.pop(area, None)
            # logging.debug(f"Quick temporary area {area} destroyed.")

    # ============================================================================
    # Callback Handler for Control UI Events
    # ============================================================================
    def handle_control_ui_event(self, event_name, value):
        """
        จัดการ Event ที่ส่งมาจาก Control UI (เช่น การเปลี่ยนโหมด Click Translate)

        Args:
            event_name (str): ชื่อของ event ที่เกิดขึ้น (เช่น "click_translate_mode_changed")
            value: ค่าที่เกี่ยวข้องกับ event (เช่น True/False สำหรับ click_translate)
        """
        if event_name == "click_translate_mode_changed":
            # ตรวจสอบว่า translation_event ถูกสร้างหรือยัง
            # ควรจะถูกสร้างใน init_variables หรือ init_ocr_and_translation
            if not hasattr(self, "translation_event") or not isinstance(
                self.translation_event, threading.Event
            ):
                logging.error("Translation event not initialized or invalid type.")
                # อาจจะแจ้งเตือนผู้ใช้หรือพยายามสร้างใหม่ แต่ตอนนี้แค่ log error
                return

            logging.info(f"Received click_translate_mode_changed event: {value}")

            # อัพเดทสถานะ UI ทันที
            if value:
                self._update_status_line("🖱️ Click Translate Mode: ON")
            else:
                self._update_status_line("⚡ Auto Translate Mode: ON")

            # จัดการการทำงานของลูปแปลภาษา
            if value:
                # ถ้า Click Translate เปิด: ให้ลูปหยุดรอ (โดยการ clear event)
                # การ clear จะทำให้ wait() ในลูป block จนกว่าจะมีการ set()
                self.translation_event.clear()
                logging.debug(
                    "Translation event cleared (Click Translate ON). Loop will wait."
                )
            else:
                # ถ้า Click Translate ปิด: ปลุกให้ลูปทำงานต่อ (โดยการ set event)
                # การ set จะทำให้ wait() ในลูปที่กำลัง block อยู่หลุดออกมาทำงานต่อ
                self.translation_event.set()
                logging.debug(
                    "Translation event set (Click Translate OFF). Loop will resume."
                )

            # หมายเหตุ: เราไม่จำเป็นต้องเปลี่ยนค่า self.is_translating ที่นี่
            # เพราะการ Start/Stop การแปลโดยรวมยังคงควบคุมด้วยปุ่ม Start/Stop หลัก
            # Click Translate เป็นเพียงการควบคุมว่าจะให้ลูปทำงาน *อัตโนมัติ* หรือไม่
            # เมื่อ is_translating เป็น False ลูปจะไม่ทำงานอยู่แล้ว ไม่ว่า Click Translate จะเป็นอะไรก็ตาม

    def toggle_theme(self):
        """เปิดหน้าต่างจัดการธีม"""
        # ตรวจสอบว่ามีหน้าต่างจัดการธีมเปิดอยู่หรือไม่
        if (
            hasattr(self, "theme_manager_window")
            and self.theme_manager_window.winfo_exists()
        ):
            # ถ้ามีหน้าต่างเปิดอยู่แล้ว ให้ปิด
            self.theme_manager_window.destroy()
            # ไม่จำเป็นต้องจัดการสีปุ่ม theme ที่นี่ เพราะ _apply_theme_update จะจัดการเมื่อธีมเปลี่ยน
            return

        # เพิ่ม debug appearance_manager
        appearance_manager.set_theme_change_callback(self._apply_theme_update)
        self.logging_manager.log_info("Theme change callback re-registered.")

        # สร้างหน้าต่างใหม่
        self.theme_manager_window = tk.Toplevel(self.root)
        self.theme_manager_window.title("Theme Manager")
        self.theme_manager_window.overrideredirect(True)

        # ปรับขนาดหน้าต่างให้เล็กลง
        window_width = 350
        window_height = 320

        # คำนวณตำแหน่งให้อยู่ข้างๆ หน้าต่างหลัก
        x = self.root.winfo_x() + self.root.winfo_width() + 10
        y = self.root.winfo_y()

        self.theme_manager_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # กำหนดสีพื้นหลัง (ดึงจาก appearance_manager)
        self.theme_manager_window.configure(bg=appearance_manager.bg_color)

        # สร้าง UI จัดการธีม
        theme_ui = appearance_manager.create_theme_manager_ui(
            self.theme_manager_window, self.settings
        )
        theme_ui.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # *** Callback ถูกตั้งค่าถาวรใน __init__ แล้ว ไม่ต้องตั้งค่าที่นี่ ***
        # appearance_manager.set_theme_change_callback(self._apply_theme_update)

        # ผูก events สำหรับการเคลื่อนย้ายหน้าต่าง
        self.theme_manager_window.bind("<Button-1>", self.start_move_theme_window)
        self.theme_manager_window.bind("<B1-Motion>", self.do_move_theme_window)

        # จัดการเมื่อปิดหน้าต่าง (อาจจะไม่จำเป็น ถ้า callback จัดการถูกต้อง)
        self.theme_manager_window.protocol("WM_DELETE_WINDOW", self.close_theme_manager)

        # รอให้หน้าต่างแสดงผลเสร็จ แล้วทำให้ขอบโค้งมน
        self.theme_manager_window.update_idletasks()
        self.apply_rounded_corners_to_theme_window()  # เมธอดนี้อาจจะต้องปรับปรุงให้ใช้ Windows API หรือวิธีอื่นที่เหมาะสม

        # บันทึกลอก
        self.logging_manager.log_info("เปิดหน้าต่างจัดการธีม")

    def restart_control_ui(self):
        """รีสตาร์ท Control UI เพื่อใช้ธีมใหม่"""
        try:
            # ตรวจสอบว่ามี control_ui หรือไม่
            if not hasattr(self, "control_ui") or not self.control_ui:
                self.logging_manager.log_info(
                    "Control UI not found, nothing to restart"
                )
                return False

            # เก็บข้อมูลสถานะปัจจุบันไว้
            current_areas = self.current_area
            current_preset = (
                self.control_ui.current_preset
                if hasattr(self.control_ui, "current_preset")
                else 1
            )
            was_visible = False
            control_ui_pos = None

            # ตรวจสอบตำแหน่งและสถานะการแสดงผลปัจจุบัน
            if hasattr(self, "control_ui") and self.control_ui.root.winfo_exists():
                was_visible = self.control_ui.root.state() != "withdrawn"
                # เก็บตำแหน่งปัจจุบัน
                if was_visible:
                    control_ui_pos = (
                        self.control_ui.root.winfo_x(),
                        self.control_ui.root.winfo_y(),
                    )
                # ปิดหน้าต่างเดิม
                self.control_ui.root.destroy()

            # บันทึกข้อมูลเกี่ยวกับการรีสตาร์ท
            self.logging_manager.log_info("Restarting Control UI with current theme")
            self.logging_manager.log_info(
                f"Current areas: {current_areas}, Preset: {current_preset}"
            )

            # สร้าง Control UI ใหม่
            control_root = tk.Toplevel(self.root)
            control_root.protocol("WM_DELETE_WINDOW", lambda: self.on_control_close())

            # ตั้งค่าไอคอนสำหรับ Control UI
            try:
                from icon_manager import set_window_icon_simple

                set_window_icon_simple(control_root)
            except Exception:
                pass

            self.control_ui = Control_UI(
                control_root, self.force_translate, self.switch_area, self.settings
            )

            # เพิ่มบรรทัดนี้เพื่อตั้งค่า callback สำหรับ CPU limit
            self.control_ui.set_cpu_limit_callback(self)

            # คืนค่าสถานะเดิม
            areas = (
                current_areas.split("+")
                if isinstance(current_areas, str)
                else current_areas
            )
            for area in ["A", "B", "C"]:
                self.control_ui.area_states[area] = area in areas

            # คืนค่า preset
            self.control_ui.current_preset = current_preset
            self.control_ui.update_preset_display()
            self.control_ui.update_button_highlights()

            # เพิ่ม callback สำหรับปรับความเร็ว OCR
            self.control_ui.speed_callback = self.set_ocr_speed

            # คืนค่าตำแหน่งหน้าต่าง (ถ้ามี)
            if control_ui_pos and control_root.winfo_exists():
                control_root.geometry(f"+{control_ui_pos[0]}+{control_ui_pos[1]}")

            # เปิดหน้าต่างหากเดิมเปิดอยู่
            if was_visible:
                self.control_ui.show_window()
                self.con_button.config(bg="#404040")  # ปรับสีปุ่มให้แสดงว่าเปิดอยู่
            else:
                control_root.withdraw()

            self.logging_manager.log_info("Control UI restarted successfully")
            return True

        except Exception as e:
            self.logging_manager.log_error(f"Error restarting Control UI: {e}")
            # ถ้าเกิดข้อผิดพลาดให้พยายามสร้าง Control UI ใหม่แบบพื้นฐาน
            try:
                if not hasattr(self, "control_ui") or not self.control_ui:
                    control_root = tk.Toplevel(self.root)
                    control_root.protocol(
                        "WM_DELETE_WINDOW", lambda: self.on_control_close()
                    )

                    # ตั้งค่าไอคอนสำหรับ Control UI
                    try:
                        from icon_manager import set_window_icon_simple

                        set_window_icon_simple(control_root)
                    except Exception:
                        pass

                    self.control_ui = Control_UI(
                        control_root,
                        self.force_translate,
                        self.switch_area,
                        self.settings,
                    )
                    control_root.withdraw()
            except:
                pass
            return False

    def start_move_theme_window(self, event):
        """เริ่มต้นการเคลื่อนย้ายหน้าต่าง Theme Manager"""
        self.theme_x = event.x
        self.theme_y = event.y

    def do_move_theme_window(self, event):
        """เคลื่อนย้ายหน้าต่าง Theme Manager"""
        if hasattr(self, "theme_x") and hasattr(self, "theme_y"):
            deltax = event.x - self.theme_x
            deltay = event.y - self.theme_y
            x = self.theme_manager_window.winfo_x() + deltax
            y = self.theme_manager_window.winfo_y() + deltay
            self.theme_manager_window.geometry(f"+{x}+{y}")

    def close_theme_manager(self):
        """ปิดหน้าต่าง Theme Manager และรีเซ็ต callback"""
        if (
            hasattr(self, "theme_manager_window")
            and self.theme_manager_window.winfo_exists()
        ):
            self.theme_manager_window.destroy()
        appearance_manager.set_theme_change_callback(None)

    def apply_rounded_corners_to_theme_window(self):
        """ปรับให้หน้าต่าง Theme Manager ไม่มีขอบวินโดว์ (ไม่ต้องมีขอบโค้ง)"""
        try:
            # รอให้หน้าต่างแสดงผลเสร็จ
            self.theme_manager_window.update_idletasks()

            # ใช้เพียง overrideredirect แทนการใช้ Windows API
            self.theme_manager_window.overrideredirect(True)

        except Exception as e:
            self.logging_manager.log_error(f"Error applying window style: {e}")

    def _apply_theme_update(self):
        """
        Apply the current theme to all relevant UI components in MBB.py and Control_UI.
        """
        # --- กำหนด log_func และ log_func_error ที่จุดเริ่มต้นของเมธอด ---
        if hasattr(self, "logging_manager") and self.logging_manager is not None:
            log_func = getattr(self.logging_manager, "log_info", print)
            log_func_error = getattr(self.logging_manager, "log_error", print)
        else:
            log_func = print
            log_func_error = lambda msg: print(f"ERROR_MBB_APPLY_THEME: {msg}")
            log_func_error(
                "MBB.py: logging_manager not available in _apply_theme_update. Using basic print for logging."
            )

        log_func(
            "MBB.py: _apply_theme_update called. Applying theme to MBB UI and Control UI..."
        )

        # ส่วนที่ 1: อัปเดต UI ของ MBB.py เอง
        try:
            log_func("MBB.py: Updating MBB's own UI components...")

            theme_accent = appearance_manager.get_accent_color()
            theme_highlight = appearance_manager.get_highlight_color()
            theme_button_bg = appearance_manager.get_theme_color("button_bg", "#262637")
            theme_bg_color = appearance_manager.bg_color
            theme_text = appearance_manager.get_theme_color("text", "#ffffff")
            theme_text_dim = appearance_manager.get_theme_color("text_dim", "#b2b2b2")
            bottom_bg = "#141414"

            # อัพเดต version_label สีตามธีม
            if (
                hasattr(self, "version_label")
                and self.version_label
                and self.version_label.winfo_exists()
            ):
                try:
                    self.version_label.configure(fg=theme_accent)
                    log_func("MBB.py: Version label color updated successfully")
                except tk.TclError as e:
                    log_func_error(f"MBB.py: Failed to update version label color: {e}")

            # (โค้ดอัปเดต UI ของ MBB.py ทั้งหมดยังคงเหมือนเดิม ตามที่พี่ธีมีอยู่)
            # main_frame
            if (
                hasattr(self, "main_frame")
                and self.main_frame
                and self.main_frame.winfo_exists()
            ):
                self.main_frame.configure(bg=theme_bg_color)
            # header_frame and its children
            if hasattr(self, "header_frame") and self.header_frame.winfo_exists():
                self.header_frame.configure(bg=theme_bg_color)
                for widget in self.header_frame.winfo_children():
                    try:
                        if isinstance(widget, tk.Frame):  # Title Frame
                            widget.configure(bg=theme_bg_color)
                            for (
                                sub_widget
                            ) in widget.winfo_children():  # Labels in Title Frame
                                if isinstance(sub_widget, tk.Label):
                                    # ตรวจสอบว่าเป็น MagiciteBabel title หรือไม่
                                    if "MagiciteBabel" in str(sub_widget.cget("text")):
                                        sub_widget.configure(
                                            fg=theme_accent, bg=theme_bg_color
                                        )
                                    # version_label จะถูกอัพเดตแยกต่างหากข้างบนแล้ว
                                    elif sub_widget == getattr(
                                        self, "version_label", None
                                    ):
                                        # ข้าม version_label เพราะอัพเดตแล้วข้างบน
                                        continue
                                    else:
                                        sub_widget.configure(
                                            fg=theme_text, bg=theme_bg_color
                                        )
                        # อัพเดทปุ่มปิด (แบบใหม่)
                        if (
                            hasattr(self, "exit_button")
                            and self.exit_button.winfo_exists()
                        ):
                            # อัพเดทสีพื้นหลังปกติ
                            self.exit_button_original_bg = theme_bg_color

                            # เก็บสถานะ hover ปัจจุบัน
                            is_hovering = False
                            if (
                                self.exit_button.cget("bg") == "#E53935"
                            ):  # ถ้าสีปัจจุบันเป็นสีแดง แสดงว่ากำลัง hover
                                is_hovering = True

                            # อัพเดทสีตามสถานะ hover
                            if is_hovering:
                                # ถ้ากำลัง hover ก็คงสีแดงไว้
                                self.exit_button.config(bg="#E53935")
                            else:
                                # ถ้าไม่ได้ hover ให้ใช้สีพื้นหลังตามธีม
                                self.exit_button.config(bg=theme_bg_color)

                            # อัพเดทสีข้อความเป็นสีขาวเสมอ
                            self.exit_button.config(fg="white")

                            # อัพเดทสี activebackground เป็นสีแดงเข้มกว่าเดิม
                            self.exit_button.config(activebackground="#D32F2F")

                            # อัพเดท binding สำหรับ hover effect
                            self.exit_button.unbind("<Enter>")
                            self.exit_button.unbind("<Leave>")

                            # สร้าง binding ใหม่
                            def on_exit_hover_updated(event):
                                self.exit_button.config(bg="#E53935", cursor="hand2")

                            def on_exit_leave_updated(event):
                                self.exit_button.config(bg=theme_bg_color, cursor="")

                            self.exit_button.bind("<Enter>", on_exit_hover_updated)
                            self.exit_button.bind("<Leave>", on_exit_leave_updated)
                        # --- จบส่วนปรับปรุงปุ่มปิด (X) ---
                    except tk.TclError:
                        continue

            # start_stop_button
            if (
                hasattr(self, "start_stop_button")
                and self.start_stop_button.winfo_exists()
            ):
                current_text = self.start_stop_button.cget("text")
                if current_text == "STOP":
                    self.start_stop_button.configure(
                        bg="#404060",
                        fg=theme_text,
                        activebackground=self._lighten_color("#404060", 0.2),
                    )
                else:
                    self.start_stop_button.configure(
                        bg=theme_accent,
                        fg=theme_text,
                        activebackground=appearance_manager.get_theme_color(
                            "accent_light"
                        ),
                    )
            # --- อัพเดต NPC Manager button (FIXED & COMPLETE) ---
            if (
                hasattr(self, "npc_manager_button")
                and self.npc_manager_button.winfo_exists()
            ):
                # ตรวจสอบว่าเป็นปุ่มแบบใหม่ (multiline) หรือไม่ โดยเช็คจาก attribute '_bg_item'
                if hasattr(self.npc_manager_button, "_bg_item"):
                    is_hovering = getattr(
                        self.npc_manager_button, "_is_hovering", False
                    )

                    # FIX: ใช้ attribute ที่ถูกต้องสำหรับปุ่ม multiline
                    # เราจะใช้ _original_bg และ _hover_bg ที่ตั้งค่าไว้ตอนสร้างปุ่ม
                    # theme_button_bg คือสีพื้นหลังปกติของปุ่มจากธีม
                    self.npc_manager_button._original_bg = theme_button_bg
                    current_fill = (
                        self.npc_manager_button._hover_bg
                        if is_hovering
                        else self.npc_manager_button._original_bg
                    )

                    # 1. อัปเดตสีพื้นหลัง
                    self.npc_manager_button.itemconfig(
                        self.npc_manager_button._bg_item, fill=current_fill
                    )

                    # 2. อัปเดตสีข้อความบรรทัดที่ 1 (NPC Manager)
                    # _text_items เป็น list ที่เก็บ ID ของข้อความทั้ง 2 บรรทัด
                    if (
                        hasattr(self.npc_manager_button, "_text_items")
                        and len(self.npc_manager_button._text_items) > 0
                    ):
                        self.npc_manager_button.itemconfig(
                            self.npc_manager_button._text_items[0], fill=theme_text
                        )

                    # 3. อัปเดตสีข้อความบรรทัดที่ 2 (ชื่อเกม)
                    if hasattr(self.npc_manager_button, "_text_line2_item"):
                        self.npc_manager_button.itemconfig(
                            self.npc_manager_button._text_line2_item, fill=theme_accent
                        )
                else:
                    # Fallback สำหรับปุ่มแบบเก่า (ถ้ายังมีการใช้งาน)
                    self.logging_manager.log_warning(
                        "Found an old-style NPC Manager button. Please update it to multiline."
                    )
                    is_selected = getattr(self.npc_manager_button, "selected", False)
                    is_hovering = getattr(
                        self.npc_manager_button, "_is_hovering", False
                    )
                    self.npc_manager_button.original_bg = theme_button_bg
                    self.npc_manager_button.hover_bg = theme_accent
                    current_fill = (
                        self.npc_manager_button.hover_bg
                        if is_hovering
                        else self.npc_manager_button.original_bg
                    )
                    if is_selected:
                        current_fill = theme_highlight

                    if hasattr(self.npc_manager_button, "button_bg"):
                        self.npc_manager_button.itemconfig(
                            self.npc_manager_button.button_bg, fill=current_fill
                        )
                    if hasattr(self.npc_manager_button, "button_text"):
                        self.npc_manager_button.itemconfig(
                            self.npc_manager_button.button_text, fill=theme_text
                        )

            # theme_button, settings_icon_button, guide_button
            if hasattr(self, "theme_button") and self.theme_button.winfo_exists():
                self.theme_button.configure(bg=bottom_bg, activebackground=bottom_bg)
            if (
                hasattr(self, "settings_icon_button")
                and self.settings_icon_button.winfo_exists()
            ):
                self.settings_icon_button.configure(
                    bg=bottom_bg, activebackground=bottom_bg
                )
            if hasattr(self, "guide_button") and self.guide_button.winfo_exists():
                self.guide_button.configure(
                    bg="#1F1F1F",
                    fg="#A0A0A0",
                    activebackground="#2A2A2A",
                    activeforeground=theme_text,
                )
            # status_label, blink_label
            if hasattr(self, "status_label") and self.status_label.winfo_exists():
                self.status_label.configure(fg=theme_accent, bg=theme_bg_color)
                if self.status_label.master and isinstance(
                    self.status_label.master, tk.Frame
                ):
                    self.status_label.master.configure(bg=theme_bg_color)
            if hasattr(self, "blink_label") and self.blink_label.winfo_exists():
                self.blink_label.configure(bg=theme_bg_color)
                if self.blink_label.master and isinstance(
                    self.blink_label.master, tk.Frame
                ):
                    self.blink_label.master.configure(bg=theme_bg_color)
            # bottom_container and its children
            if (
                hasattr(self, "bottom_container")
                and self.bottom_container.winfo_exists()
            ):
                self.bottom_container.configure(bg=bottom_bg)
                if (
                    hasattr(self, "tooltip_info_bar")
                    and self.tooltip_info_bar.winfo_exists()
                ):
                    self.tooltip_info_bar.configure(bg=bottom_bg)
                    if (
                        hasattr(self, "tooltip_label")
                        and self.tooltip_label.winfo_exists()
                    ):
                        self.tooltip_label.configure(bg=bottom_bg, fg=theme_text)
                    if hasattr(self, "info_label") and self.info_label.winfo_exists():
                        self.update_info_label_with_model_color()  # This should handle its own theme update
                for child in self.bottom_container.winfo_children():
                    if isinstance(child, tk.Frame) and child.winfo_exists():
                        child.configure(bg=bottom_bg)
                        for sub_child in child.winfo_children():
                            if (
                                isinstance(sub_child, tk.Frame)
                                and sub_child.winfo_exists()
                            ):
                                sub_child.configure(bg=bottom_bg)
            # อัพเดทสีปุ่ม TUI, LOG, MINI, CON
            bottom_buttons_map = {
                "tui": getattr(self, "tui_button", None),
                "log": getattr(self, "log_button", None),
                "mini": getattr(self, "mini_button", None),
                "con": getattr(self, "con_button", None),
            }
            bottom_button_states = getattr(self, "bottom_button_states", {})
            for name, button in bottom_buttons_map.items():
                if button and button.winfo_exists():
                    # *** เพิ่มเงื่อนไขพิเศษสำหรับปุ่ม MINI ***
                    if name == "mini":
                        # MINI ใช้สีเริ่มต้นเสมอ (ไม่มี toggle effect)
                        inactive_bg = appearance_manager.get_theme_color(
                            "button_bg", "#262637"
                        )
                        inactive_fg = appearance_manager.get_theme_color(
                            "text_dim", "#b2b2b2"
                        )
                        button.configure(
                            bg=inactive_bg,
                            fg=inactive_fg,
                            activebackground=appearance_manager.get_accent_color(),
                            activeforeground=appearance_manager.get_theme_color(
                                "text", "#ffffff"
                            ),
                        )
                        continue  # ข้ามไปปุ่มถัดไป

                    # สำหรับปุ่มอื่นๆ ใช้โค้ดเดิม
                    is_active = bottom_button_states.get(name, False)
                    current_bg = (
                        appearance_manager.get_highlight_color()
                        if is_active
                        else appearance_manager.get_theme_color("button_bg", "#262637")
                    )
                    current_fg = (
                        appearance_manager.get_theme_color("text", "#ffffff")
                        if is_active
                        else appearance_manager.get_theme_color("text_dim", "#b2b2b2")
                    )
                    button.configure(
                        bg=current_bg,
                        fg=current_fg,
                        activebackground=appearance_manager.get_accent_color(),
                        activeforeground=appearance_manager.get_theme_color(
                            "text", "#ffffff"
                        ),
                    )

            # --- อัพเดตปุ่ม Topmost (Pin/Unpin) ถ้ามี ---
            if hasattr(self, "topmost_button") and self.topmost_button.winfo_exists():
                # อัพเดทสีพื้นหลังของปุ่ม
                self.topmost_button.configure(bg=bottom_bg, activebackground=bottom_bg)

            log_func("MBB.py: Successfully updated MBB's own UI components.")
        except Exception as e_mbb_ui_update:
            log_func_error(
                f"MBB.py: Error during MBB UI component update: {e_mbb_ui_update}"
            )

            log_func_error(traceback.format_exc())

        # ส่วนที่ 2: เรียกอัปเดต Control UI (ใช้ log_func และ log_func_error ที่ define ไว้ตอนต้นสุด)
        if (
            hasattr(self, "control_ui")
            and self.control_ui
            and hasattr(self.control_ui, "root")
            and self.control_ui.root.winfo_exists()
            and hasattr(self.control_ui, "update_theme")
        ):
            try:
                log_func("MBB.py: Attempting to call control_ui.update_theme()...")
                self.control_ui.update_theme()  # ไม่ต้องส่ง arguments
                log_func("MBB.py: control_ui.update_theme() called successfully.")
            except Exception as e_control_ui_update:
                log_func_error(
                    f"MBB.py: Error when calling control_ui.update_theme(): {e_control_ui_update}"
                )

                log_func_error(traceback.format_exc())
        else:
            log_func(
                "MBB.py: Control UI instance, its root, or its update_theme method is not available. Skipping Control UI theme update."
            )

        # ส่วนที่ 3: บังคับอัปเดต UI หลักของ MBB (เหมือนเดิม)
        try:
            if hasattr(self, "root") and self.root.winfo_exists():
                self.root.update_idletasks()
            log_func("MBB.py: Root UI update_idletasks called.")
        except Exception as e_root_update:
            log_func_error(
                f"MBB.py: Error calling root.update_idletasks(): {e_root_update}"
            )

        # ส่วนที่ 4: อัพเดทธีม Mini UI
        if hasattr(self, "mini_ui") and self.mini_ui:
            try:
                log_func("MBB.py: Attempting to call mini_ui.update_theme()...")
                # เรียกใช้เมธอด update_theme ของ mini_ui โดยตรง
                self.mini_ui.update_theme()
                log_func("MBB.py: mini_ui.update_theme() called successfully.")
            except Exception as e_mini_ui_update:
                log_func_error(
                    f"MBB.py: Error when calling mini_ui.update_theme(): {e_mini_ui_update}"
                )
                log_func_error(traceback.format_exc())
        else:
            log_func(
                "MBB.py: Mini UI instance not available. Skipping Mini UI theme update."
            )

        # ส่วนที่ 5: อัพเดทสีขอบ PIN ถ้ากำลังแสดงอยู่
        if hasattr(self, "root") and self.root.attributes("-topmost"):
            if (
                hasattr(self, "border_window")
                and self.border_window
                and self.border_window.winfo_exists()
            ):
                try:
                    log_func("MBB.py: Updating PIN border color...")
                    self._update_pin_border(True)  # อัพเดทขอบใหม่ด้วยสีจาก theme ใหม่
                    log_func("MBB.py: PIN border color updated successfully.")
                except Exception as e_border_update:
                    log_func_error(
                        f"MBB.py: Error updating PIN border color: {e_border_update}"
                    )

        log_func("MBB.py: _apply_theme_update process finished.")

    def update_mini_ui_theme(self, accent_color=None, highlight_color=None):
        """อัพเดทธีมสำหรับ Mini UI - เวอร์ชันใหม่ที่ใช้ mini_ui.update_theme()"""
        if not hasattr(self, "mini_ui") or not self.mini_ui:
            return

        try:
            # เรียกใช้เมธอด update_theme ของ mini_ui โดยตรง
            self.mini_ui.update_theme(accent_color, highlight_color)
            self.logging_manager.log_info(
                "Mini UI theme updated via mini_ui.update_theme()"
            )
        except Exception as e:
            self.logging_manager.log_error(f"Error updating mini UI theme: {e}")
            self.logging_manager.log_error(traceback.format_exc())

    def create_modern_button(
        self,
        parent,
        text,
        command,
        width=95,
        height=25,
        fg="#ffffff",
        bg=None,
        hover_bg=None,
        font=("Nasalization Rg", 10),
        corner_radius=15,
    ):
        """สร้างปุ่มโมเดิร์นสำหรับ Control UI"""
        # กำหนดค่าสีเริ่มต้นจากธีมปัจจุบันถ้าไม่ได้ระบุมา
        if bg is None:
            bg = appearance_manager.get_theme_color("button_bg")
        if hover_bg is None:
            hover_bg = appearance_manager.get_accent_color()

        # บันทึกสีที่ใช้สำหรับดีบัก
        self.logging_manager.log_info(
            f"Creating button '{text}' with bg={bg}, hover={hover_bg}"
        )

        # สร้าง canvas สำหรับวาดปุ่ม
        canvas = tk.Canvas(
            parent,
            width=width,
            height=height,
            bg=appearance_manager.bg_color,
            highlightthickness=0,
            bd=0,
        )

        # วาดรูปทรงปุ่ม
        button_bg = canvas.create_rounded_rectangle(
            0, 0, width, height, radius=corner_radius, fill=bg, outline=""
        )

        # สร้างข้อความบนปุ่ม
        button_text = canvas.create_text(
            width // 2, height // 2, text=text, fill=fg, font=font
        )

        # ผูกคำสั่งเมื่อคลิก
        canvas.bind("<Button-1>", lambda event: command())

        # เพิ่ม tag สำหรับระบุสถานะ hover
        canvas._is_hovering = False

        # สร้าง hover effect
        def on_enter(event):
            if hasattr(canvas, "selected") and canvas.selected:
                return

            canvas._is_hovering = True

            # สำหรับปุ่ม START ให้สีสว่างขึ้นเล็กน้อย
            if text == "START" or text == "STOP":
                # ใช้สีที่สว่างขึ้นจากสีปกติ
                lighter_color = self._lighten_color(canvas.original_bg, 0.2)
                canvas.itemconfig(button_bg, fill=lighter_color)
            else:
                canvas.itemconfig(button_bg, fill=canvas.hover_bg)

        def on_leave(event):
            # ยกเลิกสถานะ hover
            canvas._is_hovering = False

            if not hasattr(canvas, "selected") or not canvas.selected:
                # ใช้สีเดิมของปุ่ม
                current_bg = canvas.original_bg
                canvas.itemconfig(button_bg, fill=current_bg)

        canvas.bind("<Enter>", on_enter)
        canvas.bind("<Leave>", on_leave)

        # เพิ่ม metadata สำหรับการใช้งานภายหลัง
        canvas.selected = False
        canvas.original_bg = bg
        canvas.hover_bg = hover_bg
        canvas.button_bg = button_bg
        canvas.button_text = button_text

        # สร้างฟังก์ชันที่ใช้ itemconfig แทน config
        def update_button(text=None, fg=None, bg=None):
            try:
                if text is not None and canvas.winfo_exists():
                    canvas.itemconfig(button_text, text=text)
                if fg is not None and canvas.winfo_exists():
                    canvas.itemconfig(button_text, fill=fg)
                if bg is not None and canvas.winfo_exists():
                    # ถ้าไม่ได้อยู่ในสถานะ hover ให้อัพเดทเฉพาะรูปทรง
                    if not canvas._is_hovering:
                        canvas.itemconfig(button_bg, fill=bg)
                    # อัพเดทสีเดิมเสมอ
                    canvas.original_bg = bg
            except Exception as e:
                print(f"Error in button update: {e}")

        canvas.update_button = update_button
        return canvas

    def create_modern_button_multiline(
        self,
        parent,
        text_line1,
        text_line2,
        text_line2_color=None,
        command=None,
        width=95,
        height=50,  # เพิ่มความสูงเริ่มต้น
        fg="#ffffff",
        bg=None,
        hover_bg=None,
        font_line1=("Nasalization Rg", 10),
        font_line2=("Nasalization Rg", 8),
        corner_radius=15,
    ):
        """สร้างปุ่มโมเดิร์นแบบ 2 บรรทัดสำหรับ NPC Manager"""
        # กำหนดค่าสีเริ่มต้นจากธีมปัจจุบันถ้าไม่ได้ระบุมา
        if bg is None:
            bg = appearance_manager.get_theme_color("button_bg")
        if hover_bg is None:
            hover_bg = appearance_manager.get_accent_color()
        if text_line2_color is None:
            text_line2_color = appearance_manager.get_accent_color()

        # สร้าง canvas สำหรับวาดปุ่ม
        canvas = tk.Canvas(
            parent,
            width=width,
            height=height,
            bg=appearance_manager.bg_color,
            highlightthickness=0,
            bd=0,
        )

        # วาดรูปทรงปุ่ม
        button_bg = canvas.create_rounded_rectangle(
            0, 0, width, height, radius=corner_radius, fill=bg, outline=""
        )

        # สร้างข้อความบรรทัดที่ 1
        button_text_1 = canvas.create_text(
            width // 2, height // 3, text=text_line1, fill=fg, font=font_line1
        )

        # สร้างข้อความบรรทัดที่ 2
        button_text_2 = canvas.create_text(
            width // 2,
            (height // 3) * 2,
            text=text_line2,
            fill=text_line2_color,
            font=font_line2,
        )

        # ผูกคำสั่งเมื่อคลิก
        if command:
            canvas.bind("<Button-1>", lambda event: command())

        # เพิ่ม tag สำหรับระบุสถานะ hover
        canvas._is_hovering = False
        canvas._original_bg = bg
        canvas._hover_bg = hover_bg
        canvas._text_items = [button_text_1, button_text_2]
        canvas._bg_item = button_bg

        # สร้าง hover effect
        def on_enter(event):
            if not canvas._is_hovering:
                canvas._is_hovering = True
                canvas.itemconfig(canvas._bg_item, fill=canvas._hover_bg)

        def on_leave(event):
            if canvas._is_hovering:
                canvas._is_hovering = False
                canvas.itemconfig(canvas._bg_item, fill=canvas._original_bg)

        canvas.bind("<Enter>", on_enter)
        canvas.bind("<Leave>", on_leave)

        # เก็บ reference สำหรับ update ภายหลัง
        canvas._text_line2_item = button_text_2
        canvas._update_game_name = lambda name: canvas.itemconfig(
            button_text_2, text=name
        )

        return canvas

    def create_breathing_effect(self):
        """สร้าง breathing effect แบบสมูทสำหรับไฟแสดงสถานะ"""

        # คลาสสำหรับจัดการ breathing effect
        class BreathingEffect:
            def __init__(self, label, interval=30, min_alpha=0.3, max_alpha=1.0):
                self.label = label
                self.interval = interval
                self.min_alpha = min_alpha
                self.max_alpha = max_alpha
                self.current_alpha = min_alpha
                self.step = 0.05
                self.direction = 1  # 1 = เพิ่มค่า, -1 = ลดค่า
                self.active = False
                self.after_id = None  # เพิ่มตัวแปรเก็บ ID ของ after callback

                # ใช้รูปภาพเดิม
                from asset_manager import AssetManager

                self.original_image = AssetManager.load_pil_image(
                    "red_icon.png", (20, 20)
                )

                # สร้างภาพไว้ใช้งาน
                self.create_images()

            def create_images(self):
                """สร้างภาพสำหรับแสดงผล breathing effect"""
                # สร้างภาพวงกลมสีแดงที่มีความโปร่งใสต่างๆ จากรูปภาพเดิม
                self.images = {}
                self.current_image = None

                for alpha in range(30, 101, 5):  # 0.3 ถึง 1.0 ในขั้นที่ 0.05
                    alpha_val = alpha / 100

                    # คัดลอกภาพต้นฉบับ
                    img = self.original_image.copy().convert("RGBA")

                    # ปรับค่า alpha ของภาพ
                    data = img.getdata()
                    new_data = []
                    for item in data:
                        # ถ้าเป็นพิกเซลที่มีสี (ไม่ใช่พื้นที่โปร่งใส)
                        if item[3] > 0:
                            # คงค่าสี RGB เดิม แต่ปรับค่า alpha
                            new_data.append(
                                (item[0], item[1], item[2], int(255 * alpha_val))
                            )
                        else:
                            new_data.append(item)  # คงค่าพิกเซลที่โปร่งใสเดิมไว้

                    img.putdata(new_data)

                    # เก็บภาพไว้ใน dict
                    self.images[alpha_val] = ImageTk.PhotoImage(img)

                # กำหนดภาพเริ่มต้น
                self.current_image = self.images[self.min_alpha]
                self.label.config(image=self.current_image)

            def start(self):
                """เริ่ม breathing effect"""
                self.active = True
                self.breathe()

            def stop(self):
                """หยุด breathing effect อย่างสมบูรณ์"""
                self.active = False
                # ยกเลิกการตั้งเวลา callback ถ้ามี
                if self.after_id is not None:
                    self.label.after_cancel(self.after_id)
                    self.after_id = None
                # รีเซ็ตไปที่ภาพเริ่มต้น
                self.label.config(image=self.black_icon)

            def breathe(self):
                """สร้าง breathing effect แบบต่อเนื่อง"""
                if not self.active:
                    return

                # คำนวณค่า alpha ใหม่
                self.current_alpha += self.step * self.direction

                # เช็คขอบเขตและเปลี่ยนทิศทาง
                if self.current_alpha >= self.max_alpha:
                    self.current_alpha = self.max_alpha
                    self.direction = -1
                elif self.current_alpha <= self.min_alpha:
                    self.current_alpha = self.min_alpha
                    self.direction = 1

                # หาค่า alpha ที่ใกล้เคียงที่สุดที่มีในแคช
                closest_alpha = min(
                    self.images.keys(), key=lambda x: abs(x - self.current_alpha)
                )

                # อัพเดทรูปภาพ
                self.label.config(image=self.images[closest_alpha])

                # เรียกตัวเองอีกครั้งหลังจากพักตามเวลาที่กำหนด
                if self.active:  # ตรวจสอบอีกครั้งก่อนตั้งเวลาเรียกตัวเอง
                    self.after_id = self.label.after(self.interval, self.breathe)

        # สร้างและเก็บ instance ของ BreathingEffect
        self.breathing_effect = BreathingEffect(self.blink_label)
        # ให้ breathing effect เข้าถึง self.black_icon เพื่อใช้ในการรีเซ็ต
        self.breathing_effect.black_icon = self.black_icon

        return self.breathing_effect

    def on_settings_close(self):
        """เรียกเมื่อหน้าต่าง Settings ถูกปิด"""
        # ปุ่ม Settings เป็น icon แล้ว ไม่ต้องอัพเดทข้อความ
        pass

    def on_npc_manager_close(self):
        """จัดการเมื่อ NPC Manager ถูกปิด (ถูกเรียกโดย NPC Manager)"""
        try:
            # ปลดล็อค UI เมื่อ NPC Manager ปิด
            self.unlock_ui_movement()

            # อัปเดตสถานะปุ่ม NPC Manager
            if hasattr(self, "npc_manager_button"):
                self.update_button_highlight(self.npc_manager_button, False)

            # บันทึกลอก
            self.logging_manager.log_info("NPC Manager closed, UI unlocked")
        except Exception as e:
            self.logging_manager.log_error(f"Error in on_npc_manager_close: {e}")
            # พยายามปลดล็อค UI ในกรณีเกิดข้อผิดพลาด
            try:
                self.unlock_ui_movement()
            except:
                pass

    def on_translated_ui_close(self):
        """เรียกเมื่อหน้าต่าง Translated UI ถูกปิด"""
        # อัพเดทสถานะปุ่ม - ปิด
        self.update_bottom_button_state("tui", False)

    def on_translated_logs_close(self):
        """เรียกเมื่อหน้าต่าง Translated Logs ถูกปิด"""
        # อัพเดทสถานะปุ่ม - ปิด
        self.update_bottom_button_state("log", False)

    def on_translated_ui_close(self):
        """เรียกเมื่อหน้าต่าง Translated UI ถูกปิด"""
        # อัพเดทสถานะปุ่ม TUI - ปิด highlight
        self.update_bottom_button_state("tui", False)
        self.logging_manager.log_info(
            "Translated UI closed - TUI button highlight removed"
        )

    def on_control_close(self):
        """เรียกเมื่อหน้าต่าง Control UI ถูกปิด"""
        # อัพเดทสถานะปุ่ม - ปิด
        self.update_bottom_button_state("con", False)

    def on_mini_ui_close(self):
        """เรียกเมื่อหน้าต่าง Mini UI ถูกปิด"""
        # อัพเดทสถานะหรือแสดง main UI ถ้าจำเป็น
        self.root.deiconify()

    def init_mini_ui(self):
        self.mini_ui = MiniUI(self.root, self.show_main_ui_from_mini)
        self.mini_ui.set_toggle_translation_callback(self.toggle_translation)
        self.mini_ui.blink_interval = self.blink_interval

    def create_translated_logs(self):
        try:
            logging.info("Creating translated logs window...")

            # สร้าง window
            self.translated_logs_window = tk.Toplevel(self.root)

            # เพิ่ม protocol handler (สำหรับการปิดด้วยปุ่ม X ของ Window Manager)
            self.translated_logs_window.protocol(
                "WM_DELETE_WINDOW", lambda: self.on_translated_logs_close()
            )

            # ✅ แก้ไข: เพิ่ม on_close_callback เข้าไปในตอนสร้าง instance
            # เพื่อให้เมื่อกดปุ่ม X ภายในหน้าต่าง Log จะมีการเรียกฟังก์ชัน on_translated_logs_close() ด้วย
            self.translated_logs_instance = Translated_Logs(
                self.translated_logs_window,
                self.settings,
                on_close_callback=self.on_translated_logs_close,  # << เพิ่ม argument นี้
                main_app=self,  # เพิ่ม reference ของ main app
            )

            self.logging_manager.log_info("Translated logs created successfully")

        except Exception as e:
            self.logging_manager.log_error(f"Error creating translated logs: {e}")
            logging.exception("Detailed error in create_translated_logs:")
            self.translated_logs_instance = None

    def load_shortcuts(self):
        self.toggle_ui_shortcut = self.settings.get_shortcut("toggle_ui", "alt+h")
        self.start_stop_shortcut = self.settings.get_shortcut(
            "start_stop_translate", "f9"
        )
        self.force_translate_key_shortcut = self.settings.get_shortcut(
            "force_translate_key", "f10"
        )  # ใหม่

    def handle_error(self, error_message):
        self.logging_manager.log_error(f"Error: {error_message}")

    def load_icons(self):
        from asset_manager import AssetManager

        self.blink_icon = AssetManager.load_icon("red_icon.png", (20, 20))
        self.black_icon = AssetManager.load_icon("black_icon.png", (20, 20))
        self.pin_icon = AssetManager.load_icon("pin.png", (20, 20))
        self.unpin_icon = AssetManager.load_icon("unpin.png", (20, 20))

    def create_main_ui(self):
        # กำหนดขนาดหน้าต่างหลักของ MBB
        self.root.geometry("300x400")
        self.root.overrideredirect(True)

        current_bg_color = appearance_manager.bg_color

        # สร้าง frame หลักแบบธรรมดา (ไม่มี padding)
        self.main_frame = tk.Frame(
            self.root, bg=current_bg_color, bd=0, highlightthickness=0
        )
        self.main_frame.pack(expand=True, fill=tk.BOTH)

        # เตรียมสำหรับการแสดงขอบเมื่อ PIN (จะสร้างตอน toggle)
        self.border_window = None

        # ไม่แสดงขอบตอนเริ่มต้น เพราะเริ่มด้วย unpin

        # *** เพิ่มขอบโค้งมนให้หน้าต่างหลัก (ใช้วิธีการใหม่) ***
        self.root.after(100, self._apply_rounded_corners_to_window)

        # สร้าง header frame
        header_frame = tk.Frame(
            self.main_frame, bg=current_bg_color, bd=0, highlightthickness=0, height=60
        )
        header_frame.pack(fill=tk.X, pady=(10, 5))
        header_frame.pack_propagate(False)

        # Title section (ซ้ายบน)
        title_frame = tk.Frame(
            header_frame, bg=current_bg_color, bd=0, highlightthickness=0
        )
        title_frame.pack(side=tk.LEFT, padx=15)

        app_title = tk.Label(
            title_frame,
            text="MagiciteBabel",
            font=("Nasalization Rg", 14, "bold"),
            bg=current_bg_color,
            fg=appearance_manager.get_accent_color(),
        )
        app_title.pack(anchor=tk.W)

        # สีสำหรับเวอร์ชั่น - ใช้สีเหมือนกับ app_title
        try:
            # ใช้ get_accent_color() เหมือนกับ app_title
            version_color = appearance_manager.get_accent_color()
        except:
            version_color = "#A020F0"  # สีเริ่มต้น

        self.version_label = tk.Label(
            title_frame,
            text=get_mbb_version(),  # ใช้ฟังก์ชันจาก version_manager
            font=("JetBrains Mono NL Light", 8),
            bg=current_bg_color,
            fg=version_color,  # ใช้สีเหมือนกับ app_title
        )
        self.version_label.pack(anchor=tk.W)

        # สร้าง Frame เพื่อวางตำแหน่งปุ่มปิดที่มุมขวาบน
        exit_container = tk.Frame(
            header_frame, bg=current_bg_color, width=40, height=40
        )
        exit_container.place(x=300, y=0, anchor="ne")
        exit_container.pack_propagate(False)  # ทำให้ Frame คงขนาดที่กำหนด

        # สร้างปุ่มปิดแบบธรรมดาแทน Canvas
        self.exit_button = tk.Button(
            exit_container,
            text="×",
            font=("Arial", 18, "bold"),
            fg="white",
            bg=current_bg_color,
            activebackground="#E53935",  # สีแดงเข้มเมื่อกด
            activeforeground="white",
            bd=0,
            relief="flat",
            cursor="",
            padx=5,
            pady=0,
            command=self.exit_program,
        )
        self.exit_button.pack(fill="both", expand=True)

        # ลบตัวแปรเก่าที่เกี่ยวกับ exit_canvas เพื่อป้องกันความสับสน
        if hasattr(self, "exit_canvas"):
            del self.exit_canvas
        if hasattr(self, "exit_bg"):
            del self.exit_bg
        if hasattr(self, "exit_text"):
            del self.exit_text

        # เพิ่ม hover effect ที่ชัดเจนด้วย bind
        def on_exit_hover(event):
            self.exit_button.config(bg="#E53935", cursor="hand2")  # สีแดงเข้ม

        def on_exit_leave(event):
            self.exit_button.config(bg=current_bg_color, cursor="")

        # ผูก events
        self.exit_button.bind("<Enter>", on_exit_hover)
        self.exit_button.bind("<Leave>", on_exit_leave)

        # เก็บตัวแปรสีเดิมไว้เพื่อใช้ในการอัพเดทธีม
        self.exit_button_original_bg = current_bg_color

        # Content frame (ส่วนกลาง)
        content_frame = tk.Frame(
            self.main_frame, bg=current_bg_color, bd=0, highlightthickness=0
        )
        content_frame.pack(
            fill=tk.BOTH, expand=True, pady=(0, 10)
        )  # เพิ่ม pady จาก 5 เป็น 10

        # *** ปุ่ม START แบบไม่โค้ง และชิดขอบ ***
        start_frame = tk.Frame(
            content_frame, bg=current_bg_color, bd=0, highlightthickness=0
        )
        start_frame.pack(fill=tk.X, padx=0, pady=(5, 15))  # เปลี่ยน padx จาก 15 เป็น 0

        # สร้างปุ่ม START ด้วยสีที่ถูกต้องตั้งแต่เริ่มต้น
        self.start_stop_button = tk.Button(
            start_frame,
            text="START",
            command=self.toggle_translation,
            font=("Nasalization Rg", 18, "bold"),
            fg="#ffffff",
            bg=appearance_manager.get_accent_color(),
            activebackground=appearance_manager.get_theme_color("accent_light"),
            height=2,  # ความสูงเป็น lines
            bd=0,
            relief="flat",
            cursor="hand2",
        )
        self.start_stop_button.pack(fill=tk.X, padx=15)  # ปรับ padding ภายในปุ่ม

        # เพิ่ม hover effect สำหรับปุ่ม START
        def on_start_hover(event):
            # สร้างสีที่สว่างขึ้นจากสีหลักของธีม
            current_bg = self.start_stop_button.cget("bg")
            if current_bg != "#404060":  # ถ้าไม่ได้อยู่ในสถานะ STOP
                # ใช้สีสว่างจากธีม โดยดึงจาก appearance_manager โดยตรง
                accent_light = appearance_manager.get_theme_color("accent_light")
                if not accent_light:  # ถ้าไม่มีสี accent_light ในธีม
                    # สร้างสีที่สว่างขึ้น 20% จากสีปัจจุบัน
                    accent_light = self._lighten_color(current_bg, 0.2)
                self.start_stop_button.configure(bg=accent_light)

        def on_start_leave(event):
            # กลับไปใช้สีปกติ
            if hasattr(self, "is_translating") and self.is_translating:
                self.start_stop_button.configure(bg="#404060")
            else:
                # ใช้สีหลักจากธีม
                accent_color = appearance_manager.get_accent_color()
                self.start_stop_button.configure(bg=accent_color)

        # ผูก hover events
        self.start_stop_button.bind("<Enter>", on_start_hover)
        self.start_stop_button.bind("<Leave>", on_start_leave)

        # บังคับอัพเดทสีทันทีหลังสร้าง
        self.root.after(100, self._update_start_button_color)

        # ตัวบอกตำแหน่งสถานะ Ready
        status_frame = tk.Frame(
            content_frame, bg=current_bg_color, bd=0, highlightthickness=0
        )
        status_frame.pack(fill=tk.X, padx=15, pady=(5, 5))

        self.status_label = tk.Label(
            status_frame,
            text="Ready",
            font=("Nasalization Rg", 10),
            bg=current_bg_color,
            fg=appearance_manager.get_accent_color(),  # ✅ ใช้สีหลัก
        )
        self.status_label.pack(side=tk.LEFT)

        blink_label_image = self.black_icon if hasattr(self, "black_icon") else None
        self.blink_label = tk.Label(
            status_frame, image=blink_label_image, bg=current_bg_color, bd=0
        )
        if not blink_label_image:
            self.blink_label.config(text="●", fg="black")
        self.blink_label.pack(side=tk.RIGHT)

        # *** ปุ่ม NPC Manager ***
        npc_frame = tk.Frame(
            content_frame, bg=current_bg_color, bd=0, highlightthickness=0
        )
        npc_frame.pack(fill=tk.X, padx=15, pady=(5, 10))

        # NPC Manager Button
        if self.feature_manager.is_feature_enabled("npc_manager"):
            # FIX: ดึงชื่อเกมจาก self.current_game_info ที่เราโหลดไว้ใน __init__
            game_name_for_button = self.current_game_info.get("name", "N/A")

            npc_hover_intensity = 0.15

            self.npc_manager_button = self.create_modern_button_multiline(
                parent=npc_frame,
                text_line1="NPC Manager",
                text_line2=game_name_for_button,  # FIX: ใช้ตัวแปรชื่อเกมที่เพิ่งดึงมา
                text_line2_color=appearance_manager.get_accent_color(),
                command=self.toggle_npc_manager,
                width=230,
                height=50,
                fg="#ffffff",
                bg=appearance_manager.get_theme_color("button_bg"),
                hover_bg=self._lighten_color(
                    appearance_manager.get_theme_color("button_bg"), npc_hover_intensity
                ),
                font_line1=("Nasalization Rg", 11),
                font_line2=("Nasalization Rg", 8),
                corner_radius=17,
            )
        else:
            # Fallback (ส่วนนี้เหมือนเดิม)
            self.npc_manager_button = self.create_modern_button(
                npc_frame,
                "NPC Manager",
                lambda: self._show_feature_disabled_message("NPC Manager"),
                fg="#aaaaaa",
                bg="#404040",
                hover_bg="#505050",
                font=("Nasalization Rg", 10),
                width=230,
                height=35,
                corner_radius=17,
            )
        self.npc_manager_button.pack(anchor="center")

        # *** แถบแสดงข้อมูล Model และ Screen พร้อม Tooltip ***
        bottom_bg = "#141414"  # สีเข้มขึ้นนิดหนึ่ง
        self.bottom_container = tk.Frame(
            self.root,
            bg=bottom_bg,
            height=150,
            bd=0,
            highlightthickness=0,  # เพิ่มจาก 120 เป็น 150
        )
        self.bottom_container.pack(side=tk.BOTTOM, fill=tk.X)
        self.bottom_container.pack_propagate(False)

        # *** แถบ tooltip / info ที่เต็มความกว้างและสูงขึ้น ***
        self.tooltip_info_bar = tk.Frame(
            self.bottom_container,
            bg=bottom_bg,
            height=50,
            bd=0,
            highlightthickness=0,  # เพิ่มจาก 35 เป็น 50
        )
        self.tooltip_info_bar.pack(fill=tk.X, side=tk.TOP)
        self.tooltip_info_bar.pack_propagate(False)

        # สร้าง Label สำหรับ tooltip และ info ในหน้าต่างเดียวกัน
        # ใช้ place แทน pack เพื่อควบคุมตำแหน่งได้แม่นยำ
        self.tooltip_label = tk.Label(
            self.tooltip_info_bar,
            text="",
            font=("Anuphan", 16),
            bg=bottom_bg,
            fg="#ffffff",
            justify=tk.CENTER,
        )

        self.info_label = tk.Label(
            self.tooltip_info_bar,
            text=self.get_current_settings_info(),
            bg=bottom_bg,
            fg="#b2b2b2",
            font=("Anuphan", 12),
            justify=tk.CENTER,
        )

        # เริ่มต้นแสดง info_label
        self.info_label.place(relx=0.5, rely=0.5, anchor="center")
        self.update_info_label_with_model_color()

        # เก็บสถานะการแสดงผล และตัวแปรสำหรับ fade effect
        self._tooltip_active = False
        self._tooltip_hide_timer = None  # Timer สำหรับหน่วงเวลาก่อนแสดงข้อมูลโมเดล
        self._fade_job = None  # Job ID สำหรับ fade animation
        self._current_alpha = 1.0  # Alpha value ปัจจุบัน (1.0 = ทึบ, 0.0 = โปร่งใส)

        # ผูก event เมื่อ tooltip_info_bar ถูกคลิก (สำหรับ debug หรือรีเซ็ตสถานะ)
        self.tooltip_info_bar.bind("<Button-1>", self._force_show_info)

        # Bottom container Frame สำหรับปุ่มควบคุม TUI, LOG, MINI, CON
        button_container = tk.Frame(
            self.bottom_container, bg=bottom_bg, height=40, bd=0, highlightthickness=0
        )
        button_container.pack(fill=tk.X, pady=(5, 0))
        button_centered_frame = tk.Frame(
            button_container, bg=bottom_bg, bd=0, highlightthickness=0
        )
        button_centered_frame.pack(anchor=tk.CENTER)

        # ปุ่ม TUI, LOG, MINI, CON
        bottom_button_font = ("Nasalization Rg", 9)
        bottom_button_group_width = 5
        bottom_button_height = 1
        bottom_button_padx_in_button = 8
        bottom_button_pady_in_button = 2
        bottom_inactive_bg = appearance_manager.get_theme_color("button_bg", "#262637")
        bottom_inactive_fg = appearance_manager.get_theme_color("text_dim", "#b2b2b2")
        bottom_active_bg = appearance_manager.get_accent_color()
        bottom_active_fg = appearance_manager.get_theme_color("text", "#ffffff")
        bottom_hover_bg = appearance_manager.get_accent_color()

        # สร้างปุ่ม TUI
        self.tui_button = tk.Button(
            button_centered_frame,
            text="TUI",
            command=self.toggle_translated_ui,
            font=bottom_button_font,
            width=bottom_button_group_width,
            height=bottom_button_height,
            bg=bottom_inactive_bg,
            fg=bottom_inactive_fg,
            activebackground=bottom_hover_bg,
            activeforeground=bottom_active_fg,
            bd=0,
            relief="flat",
            cursor="hand2",
            padx=bottom_button_padx_in_button,
            pady=bottom_button_pady_in_button,
        )
        self.tui_button.pack(side=tk.LEFT, padx=10)

        # สร้างปุ่ม LOG
        self.log_button = tk.Button(
            button_centered_frame,
            text="LOG",
            command=self.toggle_translated_logs,
            font=bottom_button_font,
            width=bottom_button_group_width,
            height=bottom_button_height,
            bg=bottom_inactive_bg,
            fg=bottom_inactive_fg,
            activebackground=bottom_hover_bg,
            activeforeground=bottom_active_fg,
            bd=0,
            relief="flat",
            cursor="hand2",
            padx=bottom_button_padx_in_button,
            pady=bottom_button_pady_in_button,
        )
        self.log_button.pack(side=tk.LEFT, padx=10)

        # สร้างปุ่ม MINI
        self.mini_button = tk.Button(
            button_centered_frame,
            text="MINI",
            command=self.toggle_mini_ui,
            font=bottom_button_font,
            width=bottom_button_group_width,
            height=bottom_button_height,
            bg=bottom_inactive_bg,
            fg=bottom_inactive_fg,
            activebackground=bottom_hover_bg,
            activeforeground=bottom_active_fg,
            bd=0,
            relief="flat",
            cursor="hand2",
            padx=bottom_button_padx_in_button,
            pady=bottom_button_pady_in_button,
        )
        self.mini_button.pack(side=tk.LEFT, padx=10)

        # ตั้งค่า hover effect พิเศษสำหรับปุ่ม MINI (แยกจากปุ่มอื่น)
        def mini_on_enter(event):
            # ใช้สีหลักของธีมเมื่อ hover
            theme_accent = appearance_manager.get_accent_color()
            theme_text = appearance_manager.get_theme_color("text", "#ffffff")
            self.mini_button.config(bg=theme_accent, fg=theme_text, cursor="hand2")

        def mini_on_leave(event):
            # กลับไปใช้สีเริ่มต้นเสมอเมื่อ leave (ไม่มีการตรวจสอบสถานะ toggle)
            inactive_bg = appearance_manager.get_theme_color("button_bg", "#262637")
            inactive_fg = appearance_manager.get_theme_color("text_dim", "#b2b2b2")
            self.mini_button.config(bg=inactive_bg, fg=inactive_fg, cursor="")

        # ลบ binding เดิมของปุ่ม MINI (ถ้ามี)
        self.mini_button.unbind("<Enter>")
        self.mini_button.unbind("<Leave>")

        # ผูก hover events ใหม่
        self.mini_button.bind("<Enter>", mini_on_enter)
        self.mini_button.bind("<Leave>", mini_on_leave)

        # สร้างปุ่ม CON
        self.con_button = tk.Button(
            button_centered_frame,
            text="CON",
            command=self.toggle_control,
            font=bottom_button_font,
            width=bottom_button_group_width,
            height=bottom_button_height,
            bg=bottom_inactive_bg,
            fg=bottom_inactive_fg,
            activebackground=bottom_hover_bg,
            activeforeground=bottom_active_fg,
            bd=0,
            relief="flat",
            cursor="hand2",
            padx=bottom_button_padx_in_button,
            pady=bottom_button_pady_in_button,
        )
        self.con_button.pack(side=tk.LEFT, padx=10)

        # ตั้งค่า hover effect สำหรับปุ่มด้านล่าง
        for button_key, button in {
            "tui": self.tui_button,
            "log": self.log_button,
            "mini": self.mini_button,
            "con": self.con_button,
        }.items():
            # ต้องใช้ lambda ที่ bind parameter เพื่อให้แต่ละปุ่มมี handler ของตัวเอง
            def create_handlers(btn, key):
                theme_accent = appearance_manager.get_accent_color()
                theme_text = appearance_manager.get_theme_color("text", "#ffffff")
                inactive_bg = appearance_manager.get_theme_color("button_bg", "#262637")
                inactive_fg = appearance_manager.get_theme_color("text_dim", "#b2b2b2")

                def on_enter(e):
                    # แสดงสีเมื่อ hover เฉพาะเมื่อปุ่มไม่ได้ active อยู่
                    if not self.bottom_button_states.get(key, False):
                        btn.config(bg=theme_accent, fg=theme_text, cursor="hand2")

                def on_leave(e):
                    # คืนสีเดิมเมื่อ leave เฉพาะเมื่อปุ่มไม่ได้ active อยู่
                    if not self.bottom_button_states.get(key, False):
                        btn.config(bg=inactive_bg, fg=inactive_fg, cursor="")

                return on_enter, on_leave

            on_enter, on_leave = create_handlers(button, button_key)
            button.bind("<Enter>", on_enter, add="+")
            button.bind("<Leave>", on_leave, add="+")

        # Frame สำหรับปุ่มล่างสุด
        bottom_control_frame = tk.Frame(
            self.bottom_container, bg=bottom_bg, height=40, bd=0, highlightthickness=0
        )
        bottom_control_frame.pack(fill=tk.X, pady=(0, 5))

        # ปุ่ม Guide (ซ้ายล่าง)
        self.guide_button = tk.Button(
            bottom_control_frame,
            text="Guide",
            command=lambda: self.show_starter_guide(force_show=True),
            font=("Nasalization Rg", 10, "bold"),
            height=1,
            bg="#1F1F1F",  # สีเทาเข้ม (คงเดิม)
            fg="#A0A0A0",  # สีตัวอักษรเทา (คงเดิม)
            activebackground="#2A2A2A",
            activeforeground="#FFFFFF",
            bd=0,
            relief="flat",
            cursor="hand2",
            padx=15,
            pady=4,
        )
        self.guide_button.pack(side=tk.LEFT, padx=15, pady=(8, 0))

        # เพิ่ม hover effect แบบเดียวกับปุ่มอื่น
        def guide_on_enter(event):
            self.guide_button.config(
                bg=appearance_manager.get_accent_color(), fg="#FFFFFF", cursor="hand2"
            )

        def guide_on_leave(event):
            self.guide_button.config(bg="#1F1F1F", fg="#A0A0A0", cursor="")

        self.guide_button.bind("<Enter>", guide_on_enter)
        self.guide_button.bind("<Leave>", guide_on_leave)

        # ปุ่ม Settings และ Theme (ขวาล่าง)
        settings_frame = tk.Frame(
            bottom_control_frame, bg=bottom_bg, bd=0, highlightthickness=0
        )
        settings_frame.pack(side=tk.RIGHT, padx=15, pady=(8, 0))

        # ปุ่ม Theme
        try:
            self.theme_icon = AssetManager.load_icon("theme.png", (20, 20))
            self.theme_button = tk.Button(
                settings_frame,
                image=self.theme_icon,
                command=self.toggle_theme,
                bg=bottom_bg,
                activebackground=bottom_bg,
                bd=0,
                highlightthickness=0,
                borderwidth=0,
                cursor="hand2",
            )
        except Exception as e:
            logging.error(f"Error loading theme icon: {e}")
            # Fallback to text button
            self.theme_button = tk.Button(
                settings_frame,
                text="🎨",
                command=self.toggle_theme,
                bg=bottom_bg,
                activebackground=bottom_bg,
                bd=0,
                highlightthickness=0,
                borderwidth=0,
                cursor="hand2",
                font=("Segoe UI Emoji", 12),
            )
        except Exception as e:
            logging.error(f"Error loading theme_icon: {e}")
            self.theme_button = tk.Button(
                settings_frame,
                text="🎨",
                command=self.toggle_theme,
                bg=bottom_bg,
                activebackground=bottom_bg,
                bd=0,
                highlightthickness=0,
                borderwidth=0,
                cursor="hand2",
            )
        self.theme_button.pack(side=tk.LEFT, padx=(0, 5))

        # เพิ่ม hover effect สำหรับปุ่ม theme ให้ใช้สีรอง
        def on_theme_enter(e):
            secondary_color = appearance_manager.get_theme_color(
                "secondary", appearance_manager.get_accent_color()
            )
            self.theme_button.config(bg=secondary_color)

        def on_theme_leave(e):
            self.theme_button.config(bg=bottom_bg)

        self.theme_button.bind("<Enter>", on_theme_enter)
        self.theme_button.bind("<Leave>", on_theme_leave)

        # เพิ่ม tooltip
        self.create_tooltip(self.theme_button, "จัดการธีม")

        # --- เพิ่มโค้ดสร้างปุ่ม Pin/Unpin ตรงนี้ ---
        try:
            # ตรวจสอบว่าโหลดไอคอนมาแล้วหรือยัง
            if not hasattr(self, "pin_icon") or not hasattr(self, "unpin_icon"):
                self.load_icons()  # เรียกโหลดไอคอนถ้ายังไม่ได้โหลด

            # เริ่มด้วย topmost = False (unpin)
            initial_topmost = False
            self.root.attributes("-topmost", initial_topmost)

            # สร้างปุ่ม topmost โดยใช้ไอคอนที่เหมาะสมตามสถานะเริ่มต้น
            self.topmost_button = tk.Button(
                settings_frame,
                image=self.pin_icon if initial_topmost else self.unpin_icon,
                command=self.toggle_topmost,
                bg=bottom_bg,
                activebackground=bottom_bg,
                bd=0,
                highlightthickness=0,
                borderwidth=0,
                cursor="hand2",
            )
            # บันทึกสถานะเริ่มต้น
            self.topmost_button._is_pinned = initial_topmost

            # สร้าง tooltip สำหรับปุ่ม
            self.create_tooltip(
                self.topmost_button, "unpin" if initial_topmost else "Pin"
            )

            # แสดงปุ่มในแถวเดียวกับปุ่ม theme
            self.topmost_button.pack(side=tk.LEFT, padx=(0, 5))

        except Exception as e:
            logging.error(f"Error creating pin/unpin button: {e}")

        # *** ปุ่ม Settings ใหม่ (icon) ***
        try:
            self.settings_icon = AssetManager.load_icon("setting.png", (20, 20))
            self.settings_icon_button = tk.Button(
                settings_frame,
                image=self.settings_icon,
                command=self.toggle_settings,
                bg=bottom_bg,
                activebackground=bottom_bg,
                bd=0,
                highlightthickness=0,
                borderwidth=0,
                cursor="hand2",
            )
        except Exception as e:
            logging.error(f"Error loading settings icon: {e}")
            # Fallback to text button
            self.settings_icon_button = tk.Button(
                settings_frame,
                text="⚙️",
                command=self.toggle_settings,
                bg=bottom_bg,
                activebackground=bottom_bg,
                bd=0,
                highlightthickness=0,
                borderwidth=0,
                cursor="hand2",
                font=("Segoe UI Emoji", 12),
            )
        except Exception as e:
            logging.error(f"Error loading settings icon: {e}")
            self.settings_icon_button = tk.Button(
                settings_frame,
                text="⚙️",
                command=self.toggle_settings,
                bg=bottom_bg,
                activebackground=bottom_bg,
                bd=0,
                highlightthickness=0,
                borderwidth=0,
                cursor="hand2",
                font=("Segoe UI Emoji", 12),
            )
        self.settings_icon_button.pack(side=tk.LEFT)

        # เก็บ reference ของ header_frame สำหรับการอัพเดต theme
        self.header_frame = header_frame

        # Setup hover effects และ tooltips สำหรับปุ่มล่าง
        self.bottom_button_states = {
            "tui": False,
            "log": False,
            "mini": False,
            "con": False,
        }

        # *** เพิ่ม tooltips สำหรับปุ่ม TUI, LOG, MINI, CON ***
        self._setup_bottom_button_tooltips()

        # เพิ่ม tooltips สำหรับปุ่มอื่นๆ
        self.create_tooltip(self.guide_button, "เปิด/ปิด คู่มือใช้งาน")
        self.create_tooltip(self.theme_button, "เปลี่ยนธีมสี")
        self.create_tooltip(self.settings_icon_button, "ตั้งค่าโปรแกรม")
        self.create_tooltip(self.start_stop_button, "[เริ่ม-หยุด] การแปล")
        self.create_tooltip(self.npc_manager_button, "จัดการข้อมูลตัวละคร")
        self.create_tooltip(self.exit_button, "ปิดโปรแกรม")

        # อัพเดทการไฮไลต์ปุ่ม START สำหรับสถานะการแปล
        self.update_button_highlight(self.start_stop_button, False)

        # ตั้งค่าพฤติกรรมปุ่มทั้งหมด
        self._setup_bottom_buttons_behavior()

    def reset_mini_button_state(self):
        """
        รีเซ็ตสถานะปุ่ม MINI เป็น 'ปิด' เสมอ และปรับสีให้เป็นสีเริ่มต้น
        เมธอดนี้ใช้เพื่อป้องกันไม่ให้ปุ่ม MINI ติดค้างในสถานะ 'เปิด'
        """
        # 1. ตั้งค่าสถานะใน dictionary เป็น False
        if hasattr(self, "bottom_button_states"):
            self.bottom_button_states["mini"] = False

        # 2. รีเซ็ตสีปุ่มให้เป็นสีเริ่มต้น (inactive)
        if hasattr(self, "mini_button") and self.mini_button.winfo_exists():
            inactive_bg = appearance_manager.get_theme_color("button_bg", "#262637")
            inactive_fg = appearance_manager.get_theme_color("text_dim", "#b2b2b2")
            theme_accent = appearance_manager.get_accent_color()
            theme_text = appearance_manager.get_theme_color("text", "#ffffff")

            self.mini_button.config(
                bg=inactive_bg,
                fg=inactive_fg,
                activebackground=theme_accent,
                activeforeground=theme_text,
            )

    def _apply_rounded_corners_to_window(self):
        """เพิ่มขอบโค้งมนให้หน้าต่างหลักด้วย Windows API"""
        try:
            # สำหรับ Windows ใช้ Windows API
            if sys.platform == "win32":
                # แก้ไข: ใช้ from ctypes import windll แทน import windll

                # รอให้หน้าต่างอัพเดท
                self.root.update_idletasks()

                # ใช้ SetWindowRgn สร้างขอบโค้งมน
                hwnd = windll.user32.GetParent(self.root.winfo_id())
                if hwnd:
                    # สร้าง rounded rectangle region
                    region = windll.gdi32.CreateRoundRectRgn(
                        0,
                        0,
                        self.root.winfo_width(),
                        self.root.winfo_height(),
                        12,  # รัศมีมุมโค้ง
                        12,
                    )
                    windll.user32.SetWindowRgn(hwnd, region, True)
                    self.logging_manager.log_info(
                        "Applied rounded corners to main window"
                    )
            else:
                # สำหรับ OS อื่นๆ ใช้วิธีอื่น
                self.logging_manager.log_info(
                    "Rounded corners not supported on this OS"
                )
        except Exception as e:
            self.logging_manager.log_error(f"Could not apply rounded corners: {e}")

    def update_bottom_button_state(self, button_key, is_active):
        """ศูนย์กลางการอัพเดทสถานะและสีของปุ่มด้านล่าง (TUI, LOG, MINI, CON)

        Args:
            button_key (str): ชื่อปุ่ม ('tui', 'log', 'mini', 'con')
            is_active (bool): สถานะ toggle (True = เปิด, False = ปิด)
        """
        # ตรวจสอบข้อมูลนำเข้า
        if button_key not in ["tui", "log", "mini", "con"]:
            self.logging_manager.log_warning(f"Invalid button key: {button_key}")
            return

        # *** เพิ่มเงื่อนไขพิเศษสำหรับปุ่ม MINI ***
        # MINI ไม่ใช้ toggle effect เนื่องจากเป็นการสลับหน้าต่าง
        if button_key == "mini":
            return  # ออกจากฟังก์ชันเลย ไม่ต้องทำการอัพเดทสถานะและสี

        # ดึงปุ่มตามชื่อ
        button_map = {
            "tui": self.tui_button,
            "log": self.log_button,
            "mini": self.mini_button,
            "con": self.con_button,
        }

        button = button_map[button_key]

        # ดึงสีจากธีม
        theme_highlight = appearance_manager.get_highlight_color()
        theme_text = appearance_manager.get_theme_color("text", "#ffffff")
        theme_accent = appearance_manager.get_accent_color()
        inactive_bg = appearance_manager.get_theme_color("button_bg", "#262637")
        inactive_fg = appearance_manager.get_theme_color("text_dim", "#b2b2b2")

        # อัพเดทสถานะใน dictionary
        self.bottom_button_states[button_key] = is_active

        # อัพเดทสีปุ่มตามสถานะ
        if is_active:
            # เปิด - ใช้สีหลักของธีม
            button.config(
                bg=theme_accent,  # สีหลักจากธีม (เหมือนตอน hover)
                fg=theme_text,  # สีข้อความปกติ
                activebackground=theme_highlight,
                activeforeground=theme_text,
            )
            self.logging_manager.log_info(f"Button {button_key} toggled ON")
        else:
            # ปิด - ใช้สีเริ่มต้น
            button.config(
                bg=inactive_bg,  # สีเทาอ่อน
                fg=inactive_fg,  # สีข้อความจาง
                activebackground=theme_accent,
                activeforeground=theme_text,
            )
            self.logging_manager.log_info(f"Button {button_key} toggled OFF")

    def sync_tui_button_state(self):
        """ประสานสถานะปุ่ม TUI ให้ตรงกับสถานะจริงของ translated_ui_window"""
        try:
            if (
                hasattr(self, "translated_ui_window")
                and self.translated_ui_window.winfo_exists()
            ):
                # ตรวจสอบสถานะจริงของหน้าต่าง
                is_visible = self.translated_ui_window.state() != "withdrawn"

                # ตรวจสอบสถานะปัจจุบันของปุ่ม
                current_button_state = self.bottom_button_states.get("tui", False)

                # ถ้าสถานะไม่ตรงกัน ให้ซิงค์
                if is_visible != current_button_state:
                    self.update_bottom_button_state("tui", is_visible)
                    self.logging_manager.log_info(
                        f"TUI button state synced: {is_visible}"
                    )
                    return True
            else:
                # หน้าต่างไม่มีอยู่ ปุ่มควรเป็น inactive
                if self.bottom_button_states.get("tui", False):
                    self.update_bottom_button_state("tui", False)
                    self.logging_manager.log_info(
                        "TUI button state synced: False (window doesn't exist)"
                    )
                    return True
            return False
        except Exception as e:
            self.logging_manager.log_error(f"Error syncing TUI button state: {e}")
            return False

    def ensure_tui_state_consistency(self):
        """ตรวจสอบและรักษาความสอดคล้องของสถานะ TUI ในกรณีต่างๆ"""
        try:
            # ตรวจสอบและซิงค์สถานะปุ่ม TUI
            self.sync_tui_button_state()

            # กำหนดเวลาการตรวจสอบครั้งต่อไป (ทุก 5 วินาที)
            self.root.after(5000, self.ensure_tui_state_consistency)

        except Exception as e:
            self.logging_manager.log_error(f"Error in TUI state consistency check: {e}")

    def _setup_bottom_buttons_behavior(self):
        """ตั้งค่าพฤติกรรม hover และ toggle สำหรับปุ่มด้านล่าง (TUI, LOG, MINI, CON)"""
        button_map = {
            "tui": self.tui_button,
            "log": self.log_button,
            "mini": self.mini_button,
            "con": self.con_button,
        }

        for button_key, button in button_map.items():
            # ตั้งค่าสีเริ่มต้น
            button_bg = appearance_manager.get_theme_color("button_bg", "#262637")
            button_fg = appearance_manager.get_theme_color("text_dim", "#b2b2b2")
            button.configure(bg=button_bg, fg=button_fg)

            # สร้าง closure สำหรับ event handler
            def make_event_handlers(btn, btn_key):
                # สีหลักของธีม
                theme_accent = appearance_manager.get_accent_color()
                theme_text = appearance_manager.get_theme_color("text", "#ffffff")
                # สีเริ่มต้น
                normal_bg = appearance_manager.get_theme_color("button_bg", "#262637")
                normal_fg = appearance_manager.get_theme_color("text_dim", "#b2b2b2")

                def on_enter(event):
                    # ถ้าไม่ได้อยู่ในสถานะ active ให้เปลี่ยนสีเป็นสีหลักของธีม
                    if not self.bottom_button_states.get(btn_key, False):
                        btn.config(bg=theme_accent, fg=theme_text, cursor="hand2")

                def on_leave(event):
                    # ถ้าไม่ได้อยู่ในสถานะ active ให้กลับไปใช้สีเริ่มต้น
                    if not self.bottom_button_states.get(btn_key, False):
                        btn.config(bg=normal_bg, fg=normal_fg, cursor="")

                return on_enter, on_leave

            # สร้างและผูก event handlers
            on_enter, on_leave = make_event_handlers(button, button_key)
            button.bind("<Enter>", on_enter, add="+")
            button.bind("<Leave>", on_leave, add="+")

    def _get_accent_light_color(self):
        """ดึงสี accent_light จากธีมปัจจุบัน หรือสร้างขึ้นถ้าไม่มี

        Returns:
            str: hex color code สำหรับสี accent_light
        """
        accent_light = appearance_manager.get_theme_color("accent_light")
        if not accent_light:
            # ถ้าธีมไม่มีสี accent_light กำหนดเอง โดยทำให้สว่างขึ้น 25%
            accent_color = appearance_manager.get_accent_color()
            accent_light = self._lighten_color(accent_color, 0.25)
        return accent_light

    def _update_start_button_color(self):
        """อัพเดทสีปุ่ม START ตามธีมปัจจุบัน"""
        try:
            if (
                hasattr(self, "start_stop_button")
                and self.start_stop_button.winfo_exists()
            ):
                # อัพเดทสีตามธีมปัจจุบัน
                accent_color = appearance_manager.get_accent_color()
                accent_light = appearance_manager.get_theme_color("accent_light")

                self.start_stop_button.configure(
                    bg=accent_color, activebackground=accent_light
                )
                self.logging_manager.log_info(
                    f"Updated START button color to: {accent_color}"
                )
        except Exception as e:
            self.logging_manager.log_error(f"Error updating START button color: {e}")

    def _setup_enhanced_tooltips(self):
        """ตั้งค่าระบบ tooltip ใหม่ที่แสดงในแถบล่าง"""
        # ตัวแปรสำหรับเก็บสถานะ tooltip
        self._tooltip_timer = None
        self._tooltip_active = False

    def _show_tooltip_in_bar(self, text):
        """แสดง tooltip ในแถบด้านล่างทันที โดยไม่ใช้ fade effect เมื่อ hover"""
        try:
            # ยกเลิกทุก timer และ fade jobs ที่กำลังทำงานอยู่
            if self._tooltip_hide_timer:
                try:
                    self.root.after_cancel(self._tooltip_hide_timer)
                except:
                    pass
                self._tooltip_hide_timer = None

            if hasattr(self, "_fade_job") and self._fade_job:
                try:
                    self.root.after_cancel(self._fade_job)
                except:
                    pass
                self._fade_job = None

            # ตรวจสอบว่า widgets มีอยู่
            if not hasattr(self, "tooltip_label") or not hasattr(self, "info_label"):
                self.logging_manager.log_warning("Tooltip widgets not initialized")
                return

            if (
                not self.tooltip_label.winfo_exists()
                or not self.info_label.winfo_exists()
            ):
                self.logging_manager.log_warning("Tooltip widgets do not exist")
                return

            # ซ่อน info label ทันที (ไม่ใช้ fade)
            self.info_label.place_forget()

            # แสดง tooltip ทันที
            self.tooltip_label.config(text=text, fg="#ffffff")  # ใช้สีขาวเต็ม
            self.tooltip_label.place(relx=0.5, rely=0.5, anchor="center")
            self._tooltip_active = True

        except Exception as e:
            self.logging_manager.log_error(f"Error in _show_tooltip_in_bar: {e}")

    def _hide_tooltip_from_bar(self):
        """ซ่อน tooltip และนับเวลาก่อนแสดงข้อมูล Model info กลับมา"""
        try:
            # ยกเลิก fade jobs ที่กำลังทำงานอยู่
            if hasattr(self, "_fade_job") and self._fade_job:
                try:
                    self.root.after_cancel(self._fade_job)
                except:
                    pass
                self._fade_job = None

            # ตรวจสอบว่า widgets มีอยู่
            if not hasattr(self, "tooltip_label") or not hasattr(self, "info_label"):
                return

            if (
                not self.tooltip_label.winfo_exists()
                or not self.info_label.winfo_exists()
            ):
                return

            # ซ่อน tooltip ทันที
            self.tooltip_label.place_forget()
            self._tooltip_active = False

            # เริ่มนับเวลา 2 วินาทีก่อนแสดงข้อมูลโมเดลกลับมา
            self._start_info_hide_timer()

        except Exception as e:
            self.logging_manager.log_error(f"Error in _hide_tooltip_from_bar: {e}")

    # เพิ่มเมธอดใหม่เพื่อจัดการ state เมื่อ fade เสร็จสมบูรณ์
    def _start_tooltip_fade_complete(self):
        """จัดการสถานะเมื่อ fade tooltip เสร็จสมบูรณ์"""
        self.tooltip_label.place_forget()  # ซ่อน tooltip ทันที
        self._tooltip_active = False

    def _show_tooltip_after_fade(self, text):
        """แสดง tooltip หลังจาก fade out info label เสร็จ"""
        try:
            # ซ่อน info label และแสดง tooltip
            self.info_label.place_forget()
            self.tooltip_label.config(text=text)

            # รีเซ็ต alpha และแสดงผลทันที
            self._current_alpha = 1.0  # เริ่มด้วย alpha เต็ม
            self.tooltip_label.config(fg="#ffffff")  # สีข้อความปกติทันที
            self.tooltip_label.place(relx=0.5, rely=0.5, anchor="center")
            self._tooltip_active = True
        except Exception as e:
            self.logging_manager.log_error(f"Error in _show_tooltip_after_fade: {e}")

    def _setup_other_tooltips(self):
        """ตั้งค่า tooltips สำหรับปุ่มอื่นๆ"""
        tooltip_data = {
            "start_stop_button": "[เริ่ม-หยุด] การแปล",
            "npc_manager_button": "จัดการข้อมูลตัวละคร",
            "theme_button": "เปลี่ยนธีมสี",
            "settings_icon_button": "ตั้งค่าโปรแกรม",
            "guide_button": "เปิด/ปิด คู่มือใช้งาน",
            "exit_canvas": "ปิดโปรแกรม",
        }

        for widget_name, tooltip_text in tooltip_data.items():
            widget = getattr(self, widget_name, None)
            if widget:
                if widget_name == "exit_canvas":
                    # Canvas ต้องผูก event พิเศษ
                    widget.bind(
                        "<Enter>",
                        lambda e, text=tooltip_text: self._show_tooltip_in_bar(text),
                        add="+",
                    )
                    widget.bind(
                        "<Leave>", lambda e: self._hide_tooltip_from_bar(), add="+"
                    )
                else:
                    # ปุ่มปกติ
                    widget.bind(
                        "<Enter>",
                        lambda e, text=tooltip_text: self._show_tooltip_in_bar(text),
                        add="+",
                    )
                    widget.bind(
                        "<Leave>", lambda e: self._hide_tooltip_from_bar(), add="+"
                    )

    def _setup_bottom_button_tooltips(self):
        """ตั้งค่า tooltips สำหรับปุ่ม TUI, LOG, MINI, CON ให้แสดงในแถบเดียวกัน"""
        button_descriptions = {
            "tui": "หน้าต่างแสดงคำแปลหลัก",
            "log": "หน้าต่างแสดงประวัติการแปล",
            "mini": "สลับเป็น UI ขนาดเล็ก",
            "con": "ควบคุมพื้นที่การแปล",
        }

        # ตรวจสอบว่า tooltip system พร้อมใช้งานหรือไม่
        if not (hasattr(self, "tooltip_label") and hasattr(self, "info_label")):
            self.logging_manager.log_warning(
                "Tooltip system not initialized, skipping bottom button tooltips"
            )
            return

        for button_key in ["tui", "log", "mini", "con"]:
            button = getattr(self, f"{button_key}_button", None)
            if button and button.winfo_exists():
                description = button_descriptions[button_key]

                def make_handlers(btn_key, desc):
                    def on_enter(event):
                        # แสดง tooltip และซ่อนข้อมูล model/screen
                        self._show_tooltip_in_bar(desc)
                        # อัพเดทสีปุ่มตอน hover (ถ้าไม่ได้ active)
                        if not self.bottom_button_states.get(btn_key, False):
                            button = getattr(self, f"{btn_key}_button", None)
                            if button and button.winfo_exists():
                                current_hover_bg = appearance_manager.get_accent_color()
                                button.config(bg=current_hover_bg)

                    def on_leave(event):
                        # ซ่อน tooltip และแสดงข้อมูล model/screen กลับมา
                        self._hide_tooltip_from_bar()
                        # กลับไปใช้สีปกติ (ถ้าไม่ได้ active)
                        if not self.bottom_button_states.get(btn_key, False):
                            button = getattr(self, f"{btn_key}_button", None)
                            if button and button.winfo_exists():
                                current_inactive_bg = (
                                    appearance_manager.get_theme_color(
                                        "button_bg", "#262637"
                                    )
                                )
                                button.config(bg=current_inactive_bg)

                    return on_enter, on_leave

                try:
                    on_enter, on_leave = make_handlers(button_key, description)
                    button.bind("<Enter>", on_enter)
                    button.bind("<Leave>", on_leave)
                except Exception as e:
                    self.logging_manager.log_error(
                        f"Error setting up tooltip for {button_key}: {e}"
                    )

    def update_area_button_highlights(self, areas):
        """
        อัพเดทสีปุ่มตามพื้นที่ที่กำลังทำงาน (ใน MBB.py)
        เมธอดนี้จะถูกเรียกเมื่อมีการเปลี่ยนแปลง area จาก MBB.py เอง
        แต่ปุ่ม Select Area A, B, C ได้ถูกย้ายไปที่ Control_UI แล้ว
        ดังนั้นเมธอดนี้ใน MBB.py อาจจะไม่จำเป็นต้องอัปเดตปุ่มเหล่านั้นอีก
        หรือถ้ามีปุ่มอื่นๆ ที่เกี่ยวข้องกับ Area บน MBB UI หลัก ก็ให้อัปเดตเฉพาะปุ่มเหล่านั้น
        """
        # logging.debug(f"MBB.py: update_area_button_highlights called with areas: {areas}")

        # เนื่องจากปุ่ม Select Area A, B, C หลักๆ ถูกย้ายไปที่ Control_UI แล้ว
        # และ Control_UI มีกลไกการอัปเดตไฮไลท์ของตัวเอง (self.control_ui.update_button_highlights())
        # ส่วนนี้ใน MBB.py อาจจะไม่จำเป็นต้องทำอะไรกับปุ่มเหล่านั้นอีก
        # เว้นแต่ว่าจะมีปุ่มอื่นบน Main UI ของ MBB ที่ต้องการอัปเดตตาม 'areas'

        # ถ้ามีปุ่มอื่นบน MBB UI ที่ต้องอัปเดตตาม 'areas' ให้ใส่โค้ดอัปเดตปุ่มเหล่านั้นที่นี่
        # ตัวอย่าง:
        # if hasattr(self, 'some_other_area_related_button_on_mbb_ui'):
        #     # ... โค้ดอัปเดต some_other_area_related_button_on_mbb_ui ...
        #     pass

        # โดยทั่วไปแล้ว เมื่อ MBB.py เรียก self.control_ui.update_display(self.current_area, self.current_preset)
        # Control_UI ควรจะจัดการอัปเดตไฮไลท์ของปุ่มบน Control UI เอง

        # ถ้าไม่มีปุ่มอื่นที่เกี่ยวข้องบน MBB UI, เมธอดนี้อาจจะไม่ต้องทำอะไรเลย
        pass

    def create_tooltip(self, widget, text):
        """สร้าง tooltip ที่แสดงในแถบสถานะทันที ไม่มีการล่าช้า

        Args:
            widget: Widget ที่ต้องการเพิ่ม tooltip
            text: ข้อความที่จะแสดงใน tooltip (ภาษาไทย)
        """

        def show_tooltip(event):
            """แสดง tooltip ทันทีเมื่อ hover"""
            self._show_tooltip_in_bar(text)
            return None

        def hide_tooltip(event):
            """ซ่อน tooltip ทันทีเมื่อ leave"""
            self._hide_tooltip_from_bar()
            return None

        # ลบ event bindings เดิม (ถ้ามี)
        widget.unbind("<Enter>")
        widget.unbind("<Leave>")

        # ผูก event ใหม่
        widget.bind("<Enter>", show_tooltip)
        widget.bind("<Leave>", hide_tooltip)

        # เพิ่มการจัดการเมื่อ widget ถูกทำลาย
        def on_destroy(event):
            # ซ่อน tooltip ถ้าถูกแสดงอยู่
            if hasattr(self, "_tooltip_active") and self._tooltip_active:
                self._hide_tooltip_from_bar()

        widget.bind("<Destroy>", on_destroy, add="+")

    def _lighten_color(self, hex_color, factor):
        """ทำให้สีสว่างขึ้นตาม factor (0.0-1.0)

        Args:
            hex_color (str): รหัสสี hex เช่น "#ff0000"
            factor (float): ค่าที่จะทำให้สว่างขึ้น (0.0 = ไม่เปลี่ยน, 1.0 = ขาวสนิท)

        Returns:
            str: รหัสสีใหม่ที่สว่างขึ้น
        """
        try:
            # แปลง hex เป็น RGB
            hex_color = hex_color.lstrip("#")
            rgb = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

            # เพิ่มความสว่าง
            rgb = tuple(min(255, int(c + (255 - c) * factor)) for c in rgb)

            # แปลงกลับเป็น hex
            return "#%02x%02x%02x" % rgb
        except Exception as e:
            logging.error(f"Error in _lighten_color: {e}")
            return hex_color  # คืนค่าสีเดิมถ้าเกิดข้อผิดพลาด

    def _show_tooltip_internal(self, widget, text):
        """สร้างและแสดง Tooltip สำหรับ Widget ที่ระบุ"""
        # ซ่อน tooltip เก่าก่อน (ถ้ามี)
        if (
            hasattr(self, "tooltip_window")
            and self.tooltip_window
            and self.tooltip_window.winfo_exists()
        ):
            try:
                self.tooltip_window.destroy()
            except tk.TclError:  # อาจถูกทำลายไปแล้ว
                pass
            self.tooltip_window = None

        # สร้าง tooltip window ใหม่
        self.tooltip_window = tk.Toplevel(self.root)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.attributes("-topmost", True)

        # ทำให้หน้าต่างโปร่งใส
        self.tooltip_window.configure(bg="black")
        self.tooltip_window.wm_attributes("-transparentcolor", "black")

        # สร้าง Label สำหรับแสดงข้อความด้วยฟอนต์ใหม่และสีขาว
        self.tooltip_label = tk.Label(
            self.tooltip_window,
            text=text,
            font=("Anuphan", 16),  # ใช้ฟอนต์ Anuphan ขนาด 16
            fg="#FFFFFF",  # สีขาว
            bg="black",
            justify=tk.CENTER,
            bd=0,
        )
        self.tooltip_label.pack()

        # *** คำนวณตำแหน่งใหม่ - เลื่อนขึ้น 40px จากเดิม ***
        self.root.update_idletasks()
        parent_x = self.root.winfo_rootx()
        parent_y = self.root.winfo_rooty()
        parent_width = self.root.winfo_width()
        parent_height = self.root.winfo_height()

        x = parent_x + (parent_width // 2)
        y = parent_y + (parent_height // 2) + 30  # เปลี่ยนจาก +70 เป็น +30

        # ปรับให้วางตรงกลาง
        try:
            self.tooltip_window.update_idletasks()  # บังคับคำนวณขนาด
            width = self.tooltip_window.winfo_width()
            if width > 0:  # ตรวจสอบว่า width > 0
                self.tooltip_window.geometry(f"+{x - width//2}+{y}")
            else:  # ถ้าคำนวณ width ไม่ได้ ให้วางตำแหน่งคร่าวๆ
                self.tooltip_window.geometry(f"+{x - 50}+{y}")  # สมมติว่ากว้าง 100
        except tk.TclError:  # Handle กรณี window ถูกทำลายระหว่าง update
            self.tooltip_window = None

    def _hide_tooltip_internal(self):
        """ซ่อนและทำลาย Tooltip ที่กำลังแสดงอยู่"""
        if (
            hasattr(self, "tooltip_window")
            and self.tooltip_window
            and self.tooltip_window.winfo_exists()
        ):
            try:
                self.tooltip_window.destroy()
            except tk.TclError:
                pass  # อาจถูกทำลายไปแล้ว
            self.tooltip_window = None

    def toggle_translated_ui(self):
        """Toggle Translated UI visibility without affecting translation state"""
        try:
            if self.translated_ui_window.winfo_exists():
                if self.translated_ui_window.state() == "withdrawn":
                    # เปิดหน้าต่าง
                    self.translated_ui_window.deiconify()
                    self.translated_ui_window.lift()
                    # อัพเดทสถานะปุ่ม - เปิด
                    self.update_bottom_button_state("tui", True)
                    self.logging_manager.log_info("TUI toggled ON by user")
                else:
                    # ปิดหน้าต่าง
                    self.translated_ui_window.withdraw()
                    # อัพเดทสถานะปุ่ม - ปิด
                    self.update_bottom_button_state("tui", False)
                    self.logging_manager.log_info("TUI toggled OFF by user")
            else:
                # กรณีหน้าต่างถูกทำลายไปแล้ว ให้สร้างใหม่
                self.create_translated_ui()
                self.translated_ui_window.deiconify()
                # อัพเดทสถานะปุ่ม - เปิด
                self.update_bottom_button_state("tui", True)
                self.logging_manager.log_info("TUI recreated and toggled ON")

            # ตรวจสอบความสอดคล้องหลังจาก toggle
            self.root.after(100, self.sync_tui_button_state)

        except Exception as e:
            self.logging_manager.log_error(f"Error toggling TUI: {e}")
            # พยายาม recovery
            try:
                self.sync_tui_button_state()
            except:
                pass

    def toggle_translated_logs(self):
        """Toggle Translated Logs visibility independently"""
        logging.info("Attempting to toggle translated logs")

        # 1. ตรวจสอบว่า instance ถูกสร้างสำเร็จหรือไม่
        if (
            not hasattr(self, "translated_logs_instance")
            or self.translated_logs_instance is None
        ):
            logging.error(
                "translated_logs_instance is missing or was not created successfully."
            )
            # ลองสร้างใหม่
            logging.info("Attempting to recreate translated_logs_instance...")
            self.create_translated_logs()

            if (
                not hasattr(self, "translated_logs_instance")
                or self.translated_logs_instance is None
            ):
                logging.error("Failed to create/recreate translated_logs_instance.")
                messagebox.showwarning(
                    "Logs ไม่พร้อมใช้งาน", "ไม่สามารถเปิด/ปิดหน้าต่างประวัติการแปลได้"
                )
                # ปรับสถานะปุ่มเป็นปิด
                self.update_bottom_button_state("log", False)
                return

        # 2. ตรวจสอบหน้าต่าง
        if (
            not hasattr(self, "translated_logs_window")
            or not self.translated_logs_window.winfo_exists()
        ):
            logging.info(
                "Translated logs window doesn't exist or was destroyed, attempting to show/recreate..."
            )
            try:
                # ตรวจสอบตำแหน่งของ MBB window และข้อมูลจอภาพ
                mbb_side = self.get_mbb_window_position_side()
                monitor_info = self.get_mbb_current_monitor_info()

                # แสดงหน้าต่าง พร้อมข้อมูลตำแหน่ง MBB และจอภาพ
                self.translated_logs_instance.show_window(mbb_side, monitor_info)

                if (
                    self.translated_logs_window.winfo_exists()
                    and self.translated_logs_window.state() != "withdrawn"
                ):
                    self.translated_logs_instance.is_visible = True
                    # อัพเดทสถานะปุ่ม - เปิด
                    self.update_bottom_button_state("log", True)
                else:
                    logging.error(
                        "Failed to show the translated logs window after attempting."
                    )
                    messagebox.showerror("ข้อผิดพลาด", "ไม่สามารถแสดงหน้าต่างประวัติการแปลได้")
                    # อัพเดทสถานะปุ่ม - ปิด
                    self.update_bottom_button_state("log", False)
            except Exception as show_err:
                logging.error(
                    f"Error trying to show translated logs window: {show_err}"
                )
                messagebox.showerror(
                    "ข้อผิดพลาด", f"เกิดปัญหาในการแสดงหน้าต่าง Logs: {show_err}"
                )
                # อัพเดทสถานะปุ่ม - ปิด
                self.update_bottom_button_state("log", False)
        # 3. กรณีหน้าต่างมีอยู่แล้ว: สลับการแสดงผล
        elif self.translated_logs_window.winfo_exists():
            if self.translated_logs_window.state() == "withdrawn":
                # ตรวจสอบตำแหน่งของ MBB window และข้อมูลจอภาพ
                mbb_side = self.get_mbb_window_position_side()
                monitor_info = self.get_mbb_current_monitor_info()

                # แสดงหน้าต่าง พร้อมใช้ smart positioning
                self.translated_logs_instance.show_window(mbb_side, monitor_info)
                self.translated_logs_instance.is_visible = True
                # อัพเดทสถานะปุ่ม - เปิด
                self.update_bottom_button_state("log", True)
            else:
                # ซ่อนหน้าต่าง
                self.translated_logs_window.withdraw()
                self.translated_logs_instance.is_visible = False
                # อัพเดทสถานะปุ่ม - ปิด
                self.update_bottom_button_state("log", False)

    def toggle_control(self):
        """Toggle the control UI window visibility and sync its state."""
        try:
            # ตรวจสอบว่า control_ui instance และ หน้าต่างของมันมีอยู่หรือไม่
            if (
                hasattr(self, "control_ui")
                and self.control_ui
                and hasattr(self.control_ui, "root")
                and self.control_ui.root.winfo_exists()
            ):
                # ถ้ามีอยู่แล้ว และกำลังซ่อนอยู่
                if self.control_ui.root.state() == "withdrawn":
                    # สั่งให้ Control UI อัพเดทการแสดงผลตาม state ปัจจุบันของ MBB ก่อนแสดง
                    current_preset_num = self.settings.get("current_preset", 1)
                    self.control_ui.update_display(
                        self.current_area, current_preset_num
                    )
                    logging.info(
                        f"Syncing Control UI before showing: areas='{self.current_area}', preset={current_preset_num}"
                    )

                    # กำหนดให้ control_ui มีการอ้างอิงถึง root window ของ main UI
                    if (
                        hasattr(self.control_ui, "parent_root")
                        and self.control_ui.parent_root != self.root
                    ):
                        self.control_ui.parent_root = self.root

                    # ลบค่าตำแหน่งที่บันทึกไว้เพื่อบังคับให้คำนวณตำแหน่งใหม่ตามที่ต้องการ
                    self.control_ui.ui_cache["position_x"] = None
                    self.control_ui.ui_cache["position_y"] = None

                    # แสดงหน้าต่าง Control UI
                    self.control_ui.show_window()  # เมธอดนี้จะเรียก position_right_of_main_ui ให้เอง

                    # อัพเดทสถานะปุ่ม - เปิด
                    self.update_bottom_button_state("con", True)
                # ถ้ามีอยู่แล้ว และกำลังแสดงอยู่
                else:
                    # ซ่อนหน้าต่าง Control UI
                    self.control_ui.close_window()  # เมธอดนี้อาจจะจัดการ withdraw

                    # อัพเดทสถานะปุ่ม - ปิด
                    self.update_bottom_button_state("con", False)

            # ถ้ายังไม่มี control_ui instance หรือหน้าต่างถูกทำลายไปแล้ว
            else:
                logging.info("Creating new Control UI instance.")
                control_root = tk.Toplevel(self.root)
                control_root.protocol(
                    "WM_DELETE_WINDOW", lambda: self.on_control_close()
                )

                # ตั้งค่าไอคอนสำหรับ Control UI
                try:
                    from icon_manager import set_window_icon_simple

                    set_window_icon_simple(control_root)
                except Exception:
                    pass

                # สร้าง instance ใหม่
                self.control_ui = Control_UI(
                    control_root,
                    self.force_translate,
                    self.switch_area,
                    self.settings,
                )

                # กำหนดให้ control_ui มีการอ้างอิงถึง root window ของ main UI
                self.control_ui.parent_root = self.root

                # ลงทะเบียน callback สำหรับ CPU limit
                if hasattr(self.control_ui, "set_cpu_limit_callback"):
                    self.control_ui.set_cpu_limit_callback(self.set_cpu_limit)
                    logging.info("CPU limit callback registered with new Control UI.")
                else:
                    logging.warning(
                        "Newly created Control UI does not have set_cpu_limit_callback method."
                    )

                # สั่งให้ Control UI อัพเดทการแสดงผลตาม state ปัจจุบันของ MBB ทันทีหลังสร้าง
                current_preset_num = self.settings.get("current_preset", 1)
                self.control_ui.update_display(self.current_area, current_preset_num)
                logging.info(
                    f"Syncing new Control UI after creation: areas='{self.current_area}', preset={current_preset_num}"
                )

                # แสดงหน้าต่าง Control UI ที่สร้างใหม่
                self.control_ui.show_window()

                # อัพเดทสถานะปุ่ม - เปิด
                self.update_bottom_button_state("con", True)

        except Exception as e:
            self.logging_manager.log_error(f"Error in toggle_control: {e}")

            traceback.print_exc()
            # อาจจะแสดง messagebox แจ้งผู้ใช้
            messagebox.showerror("Error", f"Could not toggle Control Panel: {e}")

    def sync_last_used_preset(
        self,
        preset_num,
        source="unknown",
        area_config_override=None,
        update_control_ui=True,
        update_overlay=True,
    ):
        """
        ศูนย์กลางการซิงค์ข้อมูล preset ล่าสุดที่ใช้งานไปยังทุกโมดูลที่เกี่ยวข้อง

        Args:
            preset_num (int): หมายเลข preset ที่ใช้ล่าสุด (1-6)
            source (str): แหล่งที่มาของการเปลี่ยนแปลง ("hover", "control_ui", "auto_switch", "manual_crop", "init")
            area_config_override (str, optional): ค่า area string ที่ต้องการบังคับใช้ (เช่น จาก switch_area). Defaults to None.
            update_control_ui (bool): ควรอัปเดต Control UI หรือไม่
            update_overlay (bool): ควรแสดง/รีเฟรช overlay พื้นที่หรือไม่
        """
        if not (1 <= preset_num <= 6):
            logging.error(f"Attempted to sync invalid preset number: {preset_num}")
            return False  # คืน False เพื่อบอกว่าไม่สำเร็จ

        try:
            # --- กำหนด Area String ที่จะใช้ ---
            final_area_config_string = None
            if area_config_override is not None:
                # ถ้ามี override ส่งมา ให้ใช้ค่านั้นเลย
                final_area_config_string = area_config_override
                logging.debug(
                    f"sync_last_used_preset: Using area_config_override: '{final_area_config_string}'"
                )
            else:
                # ถ้าไม่มี override ให้ดึงจาก preset data
                preset_data = self.settings.get_preset_data(preset_num)
                if preset_data:
                    final_area_config_string = preset_data.get(
                        "areas", "A"
                    )  # ใช้ "A" เป็น fallback
                    logging.debug(
                        f"sync_last_used_preset: Using area from preset data {preset_num}: '{final_area_config_string}'"
                    )
                else:
                    logging.error(
                        f"Could not retrieve preset data for preset {preset_num} in sync (when no override)."
                    )
                    return False  # ถ้าไม่มี override และหา preset data ไม่เจอ ก็ทำต่อไม่ได้

            # ตรวจสอบว่า state เปลี่ยนแปลงจริงหรือไม่ (เปรียบเทียบทั้ง preset และ final area string)
            current_internal_preset = getattr(self, "current_preset", None)
            current_internal_area = getattr(self, "current_area", None)

            if (
                current_internal_preset == preset_num
                and current_internal_area == final_area_config_string
            ):
                logging.debug(
                    f"sync_last_used_preset called for state ({final_area_config_string}, Preset {preset_num}) which is already active. Source: {source}. No change."
                )
                return False  # ไม่มีการเปลี่ยนแปลง state

            previous_preset = (
                self.current_preset if hasattr(self, "current_preset") else None
            )
            logging.info(
                f"Syncing preset to {preset_num} (Area: {final_area_config_string}) from source: {source}"
            )

            # 1. อัปเดตสถานะภายในของ MagicBabelApp *** โดยใช้ final_area_config_string ***
            self.current_preset = preset_num
            self.current_area = final_area_config_string  # <--- ใช้ค่าที่ตัดสินใจแล้ว

            # 2. บันทึกค่าลง settings *** เฉพาะเมื่อ source ไม่ใช่ unknown หรือ init ***
            #    การบันทึก current_area ตอนนี้จะใช้ค่า final_area_config_string ที่ถูกต้องแล้ว
            if source not in ["unknown", "init"]:
                self.settings.set("current_preset", self.current_preset)
                self.settings.set("current_area", self.current_area)
                logging.debug(
                    f"sync_last_used_preset: Saved current_preset={self.current_preset}, current_area='{self.current_area}' to settings (source: {source})."
                )
                # บันทึกเวลา Manual Selection ถ้า source มาจาก user action
                if source in [
                    "control_ui",
                    "manual_crop",
                    "hover",
                ]:  # เพิ่ม hover เข้าไปด้วย
                    self.last_manual_preset_selection_time = time.time()
                    self.settings.set(
                        "last_manual_preset_selection_time",
                        self.last_manual_preset_selection_time,
                    )
                    logging.debug(
                        "sync_last_used_preset: Updated last_manual_preset_selection_time."
                    )
            else:
                logging.debug(
                    f"sync_last_used_preset: Skipped saving current_preset/area to settings (source: {source})."
                )

            # 3. อัปเดต Control UI (ถ้าต้องการ) *** ส่ง final_area_config_string ไป ***
            if (
                update_control_ui
                and hasattr(self, "control_ui")
                and self.control_ui.is_active()
            ):
                self.control_ui.update_display(
                    self.current_area, self.current_preset
                )  # ส่งค่าที่อัพเดทแล้วไป
                if source != "control_ui":
                    if hasattr(self.control_ui, "clear_unsaved_changes_flag"):
                        self.control_ui.clear_unsaved_changes_flag()
                    else:
                        logging.warning(
                            "Control UI missing clear_unsaved_changes_flag method."
                        )

            # 4. อัปเดต Show Area Overlay (ถ้าต้องการและเปิดอยู่)
            if (
                update_overlay
                and hasattr(self, "control_ui")
                and hasattr(self.control_ui, "is_area_shown")
                and self.control_ui.is_area_shown
            ):
                # เรียก refresh จาก control_ui แทน
                if hasattr(self.control_ui, "show_area_ctrl"):
                    self.control_ui.show_area_ctrl()
                else:
                    logging.warning("Control UI missing show_area_ctrl method.")

            # 5. แจ้ง HoverTranslator (ถ้ามีและทำงานอยู่ และ source ไม่ใช่ hover)
            if (
                hasattr(self, "hover_translator")
                and self.hover_translator.enabled
                and source != "hover"
            ):
                if hasattr(self.hover_translator, "notify_external_preset_change"):
                    self.hover_translator.notify_external_preset_change(
                        self.current_preset
                    )
                else:
                    logging.warning(
                        "HoverTranslator missing notify_external_preset_change method."
                    )

            # 6. อัปเดต UI หลัก และอื่นๆ
            self.update_area_button_highlights(
                self.current_area
            )  # อัพเดทไฮไลท์ปุ่ม A/B/C บน Main UI

            # 7. แสดง feedback บน TUI (ถ้า preset เปลี่ยน)
            if previous_preset != self.current_preset and hasattr(
                self, "translated_ui"
            ):
                # ดึงข้อมูล preset อีกครั้งเพื่อดึงชื่อ preset ที่ถูกต้อง
                preset_data_for_feedback = self.settings.get_preset_data(
                    self.current_preset
                )
                if preset_data_for_feedback:
                    preset_name = preset_data_for_feedback.get(
                        "custom_name"
                    ) or preset_data_for_feedback.get(
                        "name", f"Preset {self.current_preset}"
                    )
                    feedback_message = (
                        f"Preset: {preset_name} ({self.current_area}) [Src: {source}]"
                    )
                    if (
                        hasattr(self.translated_ui, "window")
                        and self.translated_ui.window
                        and self.translated_ui.window.winfo_exists()
                        and self.translated_ui.window.state() == "normal"
                    ):
                        self.translated_ui.show_feedback_message(
                            feedback_message, duration=3000
                        )
                    else:
                        self.logging_manager.log_info(
                            "Cannot show feedback - Translated UI not visible (this is normal if TUI is closed)."
                        )
                else:
                    logging.warning(
                        f"Could not get preset data for feedback message (Preset {self.current_preset})."
                    )

            # 8. Trigger การแปลใหม่ เพราะ state เปลี่ยน
            self.force_next_translation = True

            return True  # คืน True บอกว่ามีการเปลี่ยนแปลงและ sync สำเร็จ

        except Exception as e:
            logging.error(f"Error in sync_last_used_preset: {e}")

            traceback.print_exc()
            return False

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
            # เรียกใช้ sync_last_used_preset ที่เป็นเมธอดหลักในการซิงค์
            if hasattr(self, "sync_last_used_preset"):
                return self.sync_last_used_preset(preset_num, source)
            else:
                # ทำงานแบบพื้นฐานถ้ายังไม่มี sync_last_used_preset
                self.settings.set("current_preset", preset_num)
                # บันทึกเวลาเฉพาะถ้ามาจาก hover หรือ control_ui
                if source in ["hover", "control_ui"]:
                    self.settings.set("last_manual_preset_selection_time", time.time())
                logging.info(
                    f"Saved preset {preset_num} as last used preset (from {source})"
                )
                return True
        except Exception as e:
            logging.error(f"Error in save_last_preset_to_settings: {e}")
            return False

    def update_control_ui_preset_active(self, preset_num, force_update=False):
        # บังคับอัพเดตการแสดงผลปุ่ม preset บน control_ui
        if hasattr(self, "control_ui") and self.control_ui:
            # Check if the Control UI window is actually active/visible
            if not self.control_ui.is_active():
                logging.debug(
                    "Control UI is not active, skipping preset button update from hover."
                )
                return

            if force_update:
                # แก้ไขตรงนี้: เพิ่มโค้ดบังคับอัพเดต UI
                if hasattr(self.control_ui, "update_display"):
                    current_area = self.current_area
                    self.control_ui.update_display(current_area, preset_num)
                    logging.info(
                        f"Force updated control UI preset to {preset_num} with areas {current_area}"
                    )
                else:
                    logging.warning("Control UI missing update_display method")
            else:
                # อัพเดตตามปกติ
                # *** เพิ่มบรรทัดนี้เพื่ออัพเดทปุ่ม ***
                if hasattr(self.control_ui, "select_preset_button"):
                    self.control_ui.select_preset_button(preset_num)
                    logging.debug(
                        f"Updating control UI preset highlight to {preset_num} from hover."
                    )
                else:
                    logging.warning("Control UI missing select_preset_button method")

    def is_show_area_active(self):
        # ตรวจสอบว่ามีการเปิด show area ค้างไว้หรือไม่
        return hasattr(self, "show_area_windows") and bool(self.show_area_windows)

    def set_ocr_speed(self, speed_mode):
        """
        ตั้งค่าความเร็วในการ OCR
        Args:
            speed_mode: 'normal' หรือ 'high'
        """
        self.ocr_speed = speed_mode
        self.cache_timeout = 0.5 if speed_mode == "high" else 1.0
        self.logging_manager.log_info(f"OCR speed set to: {speed_mode}")

        # อัพเดท settings
        self.settings.set("ocr_speed", speed_mode)
        self.settings.save_settings()

    def add_message(self, text, is_force_retranslation=False):
        if hasattr(self, "translated_logs_instance") and self.translated_logs_instance:
            self.translated_logs_instance.add_message(
                text, is_force_retranslation=is_force_retranslation
            )

    def get_current_settings_info(self):
        """รับข้อมูล Model และ Screen Size ปัจจุบันในรูปแบบสองบรรทัด"""
        model = self.settings.get_displayed_model()  # ใช้ displayed_model แทน model ID
        screen_size = self.settings.get("screen_size", "2560x1440")
        # แยกเป็น 2 บรรทัด
        return f"MODEL: {model}\nSCREEN: {screen_size}"

    def update_info_label_with_model_color(self):
        """อัพเดทข้อความบน info_label ให้แสดงชื่อโมเดลแบบโดดเด่น"""
        if not hasattr(self, "info_label"):
            return

        # รับข้อมูลโมเดลปัจจุบัน
        model = self.settings.get_displayed_model().lower()
        screen_size = self.settings.get("screen_size", "1920x1080")

        # กำหนดสีตามประเภทของโมเดล (ใช้กับทั้ง label)
        text_color = "#b2b2b2"  # สีเริ่มต้น
        model_icon = "•"  # สัญลักษณ์เริ่มต้น

        if "gpt" in model:
            text_color = "#3498db"  # สีน้ำเงินสำหรับโมเดล GPT
            model_icon = "⦿"
        elif "claude" in model:
            text_color = "#FF8C00"  # สีส้มสำหรับโมเดล Claude
            model_icon = "◉"
        elif "gemini" in model:
            text_color = "#A020F0"  # สีม่วงสำหรับโมเดล Gemini
            model_icon = "✦"
        else:
            text_color = "#2ecc71"  # สีเขียวสำหรับโมเดลอื่นๆ

        # เตรียมข้อความแบบมีสัญลักษณ์ - แบบ 2 บรรทัด
        model_text = model.upper()
        display_text = f"{model_icon} MODEL: {model_text}\nSCREEN: {screen_size}"

        # อัพเดทข้อความและสี
        self.info_label.config(
            text=display_text,
            bg="#141414",
            fg=text_color,
            font=("JetBrains Mono NL Light", 10),
            height=2,  # เพิ่มเป็น 2 บรรทัด
        )

    def _fade_widget(self, widget, target_alpha, duration=200, callback=None):
        """สร้าง fade effect สำหรับ widget ด้วยการเปลี่ยนสี"""
        # ยกเลิก fade job เดิม (ถ้ามี)
        if hasattr(self, "_fade_job") and self._fade_job:
            try:
                self.root.after_cancel(self._fade_job)
            except:
                pass
        self._fade_job = None

        # ตั้งค่าเริ่มต้น
        if not hasattr(self, "_current_alpha"):
            self._current_alpha = 0.0 if target_alpha > 0.5 else 1.0

        start_alpha = self._current_alpha
        steps = 6  # ลดจำนวนขั้นลงเพื่อให้เร็วขึ้น
        step_duration = max(duration // steps, 10)  # ระยะเวลาต่อขั้น (ขั้นต่ำ 10ms)

        # กำหนดสี (ไม่เปลี่ยนจากสีเดิม แต่ใช้ alpha เปลี่ยนความโปร่งใสของสีเท่านั้น)
        if widget == self.info_label:
            # ไม่กำหนดสีเอง แต่ใช้สีจาก update_info_label_with_model_color
            current_fg = widget.cget("fg")
            original_color = current_fg
        else:
            original_color = "#ffffff"  # สีเดิมของ tooltip label

        bg_color = "#141414"  # สีพื้นหลัง

        def fade_step(step):
            if step <= steps and widget.winfo_exists():
                # คำนวณ alpha สำหรับขั้นปัจจุบัน
                progress = step / steps
                current_alpha = start_alpha + (target_alpha - start_alpha) * progress
                self._current_alpha = current_alpha

                try:
                    # กำหนดพฤติกรรมตาม alpha
                    if current_alpha <= 0.1 and target_alpha < 0.5:
                        # fade out เกือบหมด - เตรียมซ่อน widget
                        blended_color = self._blend_colors(
                            original_color, bg_color, 0.1
                        )
                        widget.configure(fg=blended_color)
                        if step == steps:  # ถ้าเป็นขั้นสุดท้ายแล้ว
                            widget.place_forget()
                    else:
                        # fade in หรือ fade out บางส่วน - แสดง widget
                        widget.place(relx=0.5, rely=0.5, anchor="center")
                        # เปลี่ยนสีเพื่อจำลอง fade
                        blended_color = self._blend_colors(
                            original_color, bg_color, current_alpha
                        )
                        widget.configure(fg=blended_color)

                    # ขั้นถัดไป
                    if step < steps:
                        # สร้าง variable binding สำหรับ closure
                        next_step = step + 1
                        self._fade_job = self.root.after(
                            step_duration, lambda step=next_step: fade_step(step)
                        )
                    else:
                        # fade เสร็จแล้ว
                        if target_alpha <= 0.1:
                            # ซ่อน widget เมื่อ fade out เสร็จ
                            widget.place_forget()
                        else:
                            # แสดง widget เต็มที่เมื่อ fade in เสร็จ
                            if widget == self.info_label:
                                # ไม่ต้องกำหนดสีที่นี่ แต่จะให้ callback จัดการ
                                pass
                            else:
                                widget.configure(fg=original_color)

                        # เรียก callback
                        if callback:
                            self._fade_job = None
                            callback()
                except Exception as e:
                    self.logging_manager.log_error(f"Error in fade step {step}: {e}")
                    # ถ้าเกิดข้อผิดพลาด เรียก callback ถ้ามี
                    if callback:
                        callback()
            elif callback:  # ถ้า widget ไม่มีแล้ว แต่มี callback
                callback()

        # เริ่ม fade
        fade_step(1)

    def _blend_colors(self, color1, color2, alpha):
        """ผสมสีสองสีตาม alpha value

        Args:
            color1: สีแรก (hex)
            color2: สีที่สอง (hex)
            alpha: ค่า alpha (0.0-1.0)

        Returns:
            str: สีที่ผสมแล้ว (hex)
        """
        try:
            # แปลง hex เป็น RGB
            def hex_to_rgb(hex_color):
                hex_color = hex_color.lstrip("#")
                return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

            # แปลงสีเป็น RGB
            rgb1 = hex_to_rgb(color1)
            rgb2 = hex_to_rgb(color2)

            # ผสมสี
            blended_rgb = tuple(
                int(rgb1[i] * alpha + rgb2[i] * (1 - alpha)) for i in range(3)
            )

            # แปลงกลับเป็น hex
            return "#%02x%02x%02x" % blended_rgb
        except:
            return color1  # ถ้าเกิดข้อผิดพลาด ใช้สีเดิม

    def _start_info_hide_timer(self):
        """เริ่มนับเวลา 2 วินาทีก่อนแสดงข้อมูลโมเดลกลับมา"""
        # ยกเลิก timer เดิม (ถ้ามี)
        if hasattr(self, "_tooltip_hide_timer") and self._tooltip_hide_timer:
            try:
                self.root.after_cancel(self._tooltip_hide_timer)
            except:
                pass
            self._tooltip_hide_timer = None

        # ตั้ง timer ใหม่ - แน่ใจว่าใช้ method reference ที่ถูกต้อง
        self._tooltip_hide_timer = self.root.after(2000, self._show_info_with_fade)

    def _show_info_with_fade(self):
        """แสดงข้อมูลโมเดลกลับมาด้วย fade effect และสีที่ถูกต้อง"""
        try:
            if not self._tooltip_active:  # ถ้าไม่มี tooltip แสดงอยู่
                # ซ่อน tooltip label ก่อน (ถ้ามี)
                if hasattr(self, "tooltip_label") and self.tooltip_label.winfo_exists():
                    self.tooltip_label.place_forget()

                # รีเซ็ต alpha เป็น 0 ก่อน fade in
                self._current_alpha = 0.0

                # ตรวจสอบว่า info_label ยังมีอยู่
                if hasattr(self, "info_label") and self.info_label.winfo_exists():
                    # อัพเดทข้อความและสีด้วยฟังก์ชันมาตรฐาน
                    self.update_info_label_with_model_color()

                    # ปรับความโปร่งใสเริ่มต้น
                    self.info_label.configure(fg="#141414")  # สีพื้นหลังเพื่อเริ่ม fade in
                    self.info_label.place(relx=0.5, rely=0.5, anchor="center")

                    # เริ่ม fade in
                    self._fade_widget(
                        self.info_label,
                        1.0,
                        duration=200,
                        callback=self._finish_info_fade_in,
                    )
        except Exception as e:
            self.logging_manager.log_error(f"Error in _show_info_with_fade: {e}")

    def _finish_info_fade_in(self):
        """จัดการสถานะและสีเมื่อ fade in ของ info label เสร็จสมบูรณ์"""
        try:
            if hasattr(self, "info_label") and self.info_label.winfo_exists():
                # อัพเดทสีอีกครั้งตามโมเดลที่ใช้งาน (เพื่อความแน่ใจ)
                self.update_info_label_with_model_color()
        except Exception as e:
            self.logging_manager.log_error(f"Error in _finish_info_fade_in: {e}")

    def _force_show_info(self, event=None):
        """บังคับแสดงข้อมูลโมเดลทันที (เมื่อคลิกที่แถบ info)"""
        try:
            # ยกเลิกทุก timer และ fade job
            if self._tooltip_hide_timer:
                try:
                    self.root.after_cancel(self._tooltip_hide_timer)
                except:
                    pass
                self._tooltip_hide_timer = None

            if self._fade_job:
                try:
                    self.root.after_cancel(self._fade_job)
                except:
                    pass
                self._fade_job = None

            # ซ่อน tooltip และแสดง info ทันที
            if hasattr(self, "tooltip_label") and self.tooltip_label.winfo_exists():
                self.tooltip_label.place_forget()
            self._tooltip_active = False

            # แสดง info label ทันทีด้วย fade effect
            if hasattr(self, "info_label") and self.info_label.winfo_exists():
                # รีเซ็ต alpha และ fade in
                self._current_alpha = 0.0
                self.info_label.configure(fg="#141414")  # เริ่มต้นด้วยสีพื้นหลัง
                self.info_label.place(relx=0.5, rely=0.5, anchor="center")
                self._fade_widget(self.info_label, 1.0, duration=150)

        except Exception as e:
            self.logging_manager.log_error(f"Error in _force_show_info: {e}")

    def toggle_topmost(self):
        # อ่านสถานะปัจจุบัน
        current_state = bool(self.root.attributes("-topmost"))
        # เปลี่ยนสถานะเป็นตรงข้าม
        new_state = not current_state
        # กำหนดสถานะใหม่
        self.root.attributes("-topmost", new_state)

        # เปลี่ยนไอคอนตามสถานะใหม่
        self.topmost_button.config(
            image=self.pin_icon if new_state else self.unpin_icon
        )

        # อัพเดท tooltip ด้วยเมธอดใหม่
        self.update_pin_tooltip(new_state)

        # อัพเดทขอบตาม PIN state
        self._update_pin_border(new_state)

        # บันทึกล็อกเพื่อดีบัก
        self.logging_manager.log_info(
            f"Topmost state changed: {current_state} -> {new_state}"
        )
        self.logging_manager.log_info(f"New tooltip: {'unpin' if new_state else 'Pin'}")

    def update_pin_tooltip(self, is_pinned=None):
        """อัพเดท tooltip ของปุ่มปักหมุดตามสถานะปัจจุบัน

        Args:
            is_pinned: สถานะการปักหมุด (True/False) หรือ None เพื่อตรวจสอบสถานะปัจจุบัน
        """
        # ตรวจสอบสถานะปัจจุบันถ้าไม่ได้ระบุ
        if is_pinned is None:
            is_pinned = bool(self.root.attributes("-topmost"))

        # ลบ tooltip เดิมถ้ามี
        if hasattr(self.topmost_button, "_tooltip") and self.topmost_button._tooltip:
            try:
                self.topmost_button._tooltip.destroy()
            except Exception:
                pass  # กรณีที่อาจมีข้อผิดพลาดในการทำลาย tooltip
            self.topmost_button._tooltip = None
            self.topmost_button._tooltip_visible = False

        # กำหนดข้อความตามสถานะการปักหมุด
        tooltip_text = "unpin" if is_pinned else "Pin"

        # ล้าง event bindings เดิม
        self.topmost_button.unbind("<Enter>")
        self.topmost_button.unbind("<Leave>")
        self.topmost_button.unbind("<Motion>")

        # สร้าง tooltip ใหม่
        self.create_tooltip(self.topmost_button, tooltip_text)

        # บันทึกสถานะปัจจุบันไว้ใน widget
        self.topmost_button._is_pinned = is_pinned

    def _update_pin_border(self, is_pinned):
        """
        อัปเดตการแสดงขอบตามสถานะ PIN (เวอร์ชันแก้ไขจากต้นฉบับ)
        - ใช้กลไก Canvas + transparentcolor เดิมที่ทำงานได้ดีอยู่แล้ว
        - ปรับขนาดและตำแหน่งเพื่อสร้างระยะห่าง 2px
        - เปลี่ยนการวาดเส้นตรง 4 เส้นเป็นการวาดสี่เหลี่ยมมุมโค้งรัศมี 10 (ลดจาก 18)

        Args:
            is_pinned (bool): True เมื่อ PIN อยู่, False เมื่อ UNPIN
        """
        try:
            # ตรวจสอบว่าหน้าต่างหลักพร้อมใช้งานหรือไม่
            if (
                not hasattr(self, "root")
                or not self.root.winfo_exists()
                or self.root.winfo_width() <= 1
            ):
                if is_pinned:
                    self.root.after(100, lambda: self._update_pin_border(is_pinned))
                return

            if is_pinned:
                # สร้างหน้าต่างและ canvas ถ้ายังไม่มี (ใช้โค้ดโครงสร้างเดิม)
                if self.border_window is None or not self.border_window.winfo_exists():
                    self.border_window = tk.Toplevel(self.root)
                    self.border_window.overrideredirect(True)
                    self.border_window.attributes("-topmost", True)
                    self.border_window.attributes("-transparentcolor", "black")

                    self.border_canvas = tk.Canvas(
                        self.border_window,
                        highlightthickness=0,
                        bg="black",  # พื้นหลังโปร่งใส
                    )
                    self.border_canvas.pack(fill=tk.BOTH, expand=True)

                # --- [จุดแก้ไขที่ 1] คำนวณตำแหน่งและขนาดใหม่เพื่อให้มีระยะห่าง ---
                gap = 2  # ระยะห่าง 2px ระหว่าง UI กับเส้นขอบ
                x = self.root.winfo_x() - gap
                y = self.root.winfo_y() - gap
                width = self.root.winfo_width() + (gap * 2)
                height = self.root.winfo_height() + (gap * 2)

                # กำหนดขนาดและตำแหน่งใหม่ให้หน้าต่างขอบ
                self.border_window.geometry(f"{width}x{height}+{x}+{y}")

                # --- [จุดแก้ไขที่ 2] วาดขอบโค้งมนรัศมี 10 แทนเส้นตรง 4 เส้น ---
                self.border_canvas.delete("all")
                border_color = appearance_manager.get_accent_color()
                border_thickness = 2
                radius = 10  # <<< ลดความโค้งจาก 18 เป็น 10

                padding = border_thickness // 2  # ป้องกันเส้นขอบถูกตัด
                self.border_canvas.create_rounded_rectangle(
                    padding,
                    padding,
                    width - padding,
                    height - padding,
                    radius=radius,
                    outline=border_color,
                    width=border_thickness,
                )

                # ทำให้ border window ไม่รับ mouse events
                def pass_through(event):
                    return "break"

                self.border_window.bind("<Button-1>", pass_through)
                self.border_window.bind("<ButtonRelease-1>", pass_through)
                self.border_window.bind("<B1-Motion>", pass_through)

                self.root.lift()
                self.logging_manager.log_info(
                    f"PIN border shown with color: {border_color}"
                )

            else:
                # (ส่วนนี้จะเหมือนโค้ดเดิมของคุณทุกประการ)
                if self.border_window and self.border_window.winfo_exists():
                    self.border_window.destroy()
                    self.border_window = None

        except Exception as e:
            self.logging_manager.log_error(f"เกิดข้อผิดพลาดในการอัปเดตขอบ PIN: {e}")

    def _on_window_configure(self, event):
        """จัดการเมื่อหน้าต่างเปลี่ยนขนาดหรือย้ายตำแหน่ง (เวอร์ชันแก้ไขจากต้นฉบับ)"""
        # อัปเดตขอบถ้ากำลัง PIN อยู่และมี border window
        if self.root.attributes("-topmost"):
            if (
                hasattr(self, "border_window")
                and self.border_window
                and self.border_window.winfo_exists()
            ):
                # ใช้ Logic เดียวกันกับ _update_pin_border เพื่อให้ขอบขยับตาม
                gap = 2
                x = self.root.winfo_x() - gap
                y = self.root.winfo_y() - gap
                width = self.root.winfo_width() + (gap * 2)
                height = self.root.winfo_height() + (gap * 2)
                self.border_window.geometry(f"{width}x{height}+{x}+{y}")

                # วาดขอบใหม่บน canvas ที่มีอยู่
                self.border_canvas.delete("all")
                border_color = appearance_manager.get_accent_color()
                border_thickness = 2
                radius = 10  # ใช้ค่าเดียวกับใน _update_pin_border
                padding = border_thickness // 2

                self.border_canvas.create_rounded_rectangle(
                    padding,
                    padding,
                    width - padding,
                    height - padding,
                    radius=radius,
                    outline=border_color,
                    width=border_thickness,
                )

    def toggle_npc_manager(self):
        """
        เปิด/ปิด และจัดการ instance ของ NPC Manager
        นี่คือฟังก์ชันศูนย์กลางที่จะถูกเรียกจากทุกที่
        """
        self.logging_manager.log_info("Toggle NPC Manager requested...")

        try:
            # ตรวจสอบว่าฟีเจอร์เปิดใช้งานหรือไม่
            if not self.feature_manager.is_feature_enabled("npc_manager"):
                self._show_feature_disabled_message("NPC Manager")
                return

            # ตรวจสอบว่าหน้าต่าง NPC Manager มีอยู่และยังทำงานได้หรือไม่
            if (
                self.npc_manager_instance
                and self.npc_manager_instance.is_window_showing()
            ):
                self.logging_manager.log_info(
                    "NPC Manager is already showing, hiding it."
                )
                self.npc_manager_instance.hide_window()
                if hasattr(self, "npc_manager_button"):
                    self.update_button_highlight(self.npc_manager_button, False)
            else:
                self.logging_manager.log_info(
                    "NPC Manager not showing, creating/showing it."
                )

                if self.is_translating:
                    self.logging_manager.log_info(
                        "Stopping translation before opening NPC Manager"
                    )
                    self.stop_translation()

                if (
                    not self.npc_manager_instance
                    or not self.npc_manager_instance.window.winfo_exists()
                ):
                    self.logging_manager.log_info(
                        "Creating a new NPCManagerCard instance."
                    )
                    # FIX: แก้ไขชื่อ callback ให้ถูกต้องตรงนี้
                    self.npc_manager_instance = create_npc_manager_card(
                        self.root,
                        self.reload_npc_data,
                        self.logging_manager,
                        self.stop_translation,
                        on_game_swapped_callback=self.trigger_restart_after_swap,
                    )
                    self.npc_manager_instance.on_close_callback = (
                        self.on_npc_manager_close
                    )

                self.npc_manager_instance.show_window()
                if hasattr(self, "npc_manager_button"):
                    self.update_button_highlight(self.npc_manager_button, True)

        except Exception as e:
            error_msg = f"Failed to toggle NPC Manager: {str(e)}"
            self.logging_manager.log_error(error_msg)
            messagebox.showerror("Error", error_msg)
            self.npc_manager_instance = None
            if hasattr(self, "npc_manager_button"):
                self.update_button_highlight(self.npc_manager_button, False)

    def _finish_npc_manager_loading(self):
        """จัดการการทำงานหลังเสร็จสิ้นการโหลด NPC Manager"""
        try:
            # ปลดล็อค UI การเคลื่อนย้าย
            self.unlock_ui_movement()

            # ตรวจสอบว่า NPC Manager ยังแสดงอยู่หรือไม่ และอัปเดตสถานะปุ่ม
            if hasattr(self, "npc_manager") and self.npc_manager is not None:
                is_visible = (
                    hasattr(self.npc_manager, "window")
                    and self.npc_manager.window.winfo_exists()
                    and self.npc_manager.window.state() != "withdrawn"
                    and self.npc_manager.window.winfo_viewable()
                )
                if hasattr(self, "npc_manager_button"):
                    self.update_button_highlight(self.npc_manager_button, is_visible)
        except Exception as e:
            self.logging_manager.log_error(f"Error in _finish_npc_manager_loading: {e}")
            # พยายามปลดล็อค UI ในกรณีเกิดข้อผิดพลาด
            try:
                self.unlock_ui_movement()
            except:
                pass

    def reload_npc_data(self):
        """Reload NPC data and update related components"""
        self.logging_manager.log_info("Reloading NPC data...")

        if hasattr(self, "translator") and self.translator:
            self.translator.reload_data()
            self.logging_manager.log_info("Translator data reloaded")

        if hasattr(self, "text_corrector") and self.text_corrector:
            self.text_corrector.reload_data()
            # เพิ่มการตรวจสอบว่ามีข้อมูลหลังจาก reload หรือไม่
            if hasattr(self.text_corrector, "names"):
                self.logging_manager.log_info(
                    f"Loaded {len(self.text_corrector.names)} character names from NPC data"
                )
                if len(self.text_corrector.names) == 0:
                    self.logging_manager.log_warning(
                        "No character names found after reload!"
                    )

        if hasattr(self, "translated_ui"):
            if hasattr(self.text_corrector, "names"):
                character_names = self.text_corrector.names
                self.translated_ui.update_character_names(character_names)
                self.logging_manager.log_info(
                    f"Updated Translated_UI with {len(character_names)} character names"
                )

        self.logging_manager.log_info("NPC data reload completed")

    def trigger_restart_after_swap(self):
        """รับ Callback เพื่อสั่งปิดโปรแกรมหลักหลังจากสลับข้อมูลสำเร็จ"""
        self.logging_manager.log_info(
            "Restart triggered after data swap. Exiting program."
        )
        self.exit_program()

    def show_main_ui_from_mini(self):
        self.save_ui_positions()
        self.mini_ui.mini_ui.withdraw()
        self.root.deiconify()
        self.root.overrideredirect(True)  # เพิ่มบรรทัดนี้
        # ไม่ตั้ง topmost อัตโนมัติ ให้คงสถานะเดิมไว้
        self.root.lift()
        if self.last_main_ui_pos:
            self.root.geometry(self.last_main_ui_pos)

    def create_translated_ui(self):
        self.translated_ui_window = tk.Toplevel(self.root)
        self.translated_ui_window.protocol(
            "WM_DELETE_WINDOW", lambda: self.on_translated_ui_close()
        )

        character_names = set()
        if hasattr(self, "text_corrector"):
            if (
                not hasattr(self.text_corrector, "names")
                or len(self.text_corrector.names) == 0
            ):
                try:
                    self.logging_manager.log_info(
                        "Loading NPC data in create_translated_ui"
                    )
                    self.text_corrector.reload_data()
                except Exception as e:
                    self.logging_manager.log_error(f"Error reloading NPC data: {e}")

            if hasattr(self.text_corrector, "names"):
                character_names = self.text_corrector.names
                self.logging_manager.log_info(
                    f"Sending {len(character_names)} character names to Translated_UI"
                )
        else:
            self.logging_manager.log_warning("text_corrector not found!")

        font_settings = (
            getattr(self.font_manager, "font_settings", None)
            if hasattr(self, "font_manager")
            else None
        )

        # ✅ ส่งฟังก์ชัน toggle_npc_manager และ on_close_callback เป็น callback
        self.translated_ui = translated_ui.Translated_UI(
            self.translated_ui_window,
            self.toggle_translation,
            self.stop_translation,
            self.force_translate,
            self.toggle_main_ui,
            self.toggle_ui,
            self.settings,
            self.switch_area,
            self.logging_manager,
            character_names=character_names,
            main_app=self,
            font_settings=font_settings,
            toggle_npc_manager_callback=self.toggle_npc_manager,
            on_close_callback=self.on_translated_ui_close,  # ✅ เพิ่ม callback สำหรับการปิดหน้าต่าง
        )

        window_width = self.settings.get("width", 960)
        window_height = self.settings.get("height", 240)
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        self.translated_ui_window.geometry(f"+{x}+{y}")
        self.translated_ui_window.withdraw()

        # ตรวจสอบและซิงค์สถานะ TUI button หลังจากสร้าง UI
        self.root.after(100, self.sync_tui_button_state)

    def create_settings_ui(self):
        # ส่ง self เป็น main_app เข้าไปให้ SettingsUI
        self.settings_ui = SettingsUI(
            self.root,
            self.settings,
            self.apply_settings,
            self.update_hotkeys,
            main_app=self,
            toggle_click_callback=self.set_click_translate_mode,
            toggle_hover_callback=self.toggle_hover_translation,
        )
        self.settings_ui.set_ocr_toggle_callback(self.ocr_toggle_callback)
        self.settings_ui.on_close_callback = self.on_settings_close  # เพิ่มบรรทัดนี้
        self.settings_ui.close_settings()

    def init_ocr_and_translation(self):
        """Initialize OCR และ translator"""
        try:
            # ส่วน OCR initialization ยังคงเหมือนเดิม
            translate_area = self.settings.get_translate_area("A")
            self.start_x = translate_area["start_x"]
            self.start_y = translate_area["start_y"]
            self.end_x = translate_area["end_x"]
            self.end_y = translate_area["end_y"]

            # เก็บประเภท OCR สำหรับแสดงข้อมูลในภายหลัง
            use_gpu = self.settings.get("use_gpu_for_ocr", False)
            ocr_type = "GPU" if use_gpu else "CPU"

            # บันทึกข้อมูล OCR
            self.logging_manager.log_info(f"Initializing OCR with GPU: {use_gpu}")

            # สร้าง OCR reader
            try:
                easyocr_module = get_easyocr()
                if easyocr_module is None:
                    self.reader = None
                    self.logging_manager.log_warning(
                        "EasyOCR not available - OCR functionality disabled"
                    )
                    return

                self.reader = easyocr_module.Reader(["en", "ch_tra"], gpu=use_gpu)
                self.logging_manager.log_info(
                    f"Initialized OCR with languages: English, Korean"
                )
                self.logging_manager.log_info(f"OCR type: {ocr_type}")
            except Exception as e:
                self.logging_manager.log_error(f"Error initializing OCR reader: {e}")
                self.reader = None
                self.logging_manager.log_warning(
                    "OCR functionality disabled due to initialization error"
                )

            # สร้าง text_corrector
            try:
                self.text_corrector = TextCorrector()
                # เพิ่มบรรทัดนี้เพื่อให้แน่ใจว่ามีการโหลดข้อมูล
                self.text_corrector.reload_data()
                self.logging_manager.log_info("TextCorrector initialized successfully")
            except Exception as e:
                self.logging_manager.log_error(f"Error initializing TextCorrector: {e}")
                raise ValueError(f"Failed to initialize TextCorrector: {e}")

            # ดึงข้อมูลการตั้งค่า model
            api_params = self.settings.get_api_parameters()
            if not api_params or "model" not in api_params:
                self.logging_manager.log_error("No model specified in API parameters")
                raise ValueError("No model specified in API parameters")

            model_name = api_params["model"]
            self.logging_manager.log_info(
                f"Creating translator for model: {model_name}"
            )

            # เก็บข้อมูล translator เดิมถ้ามี
            translator_before = None
            old_class = "None"
            if hasattr(self, "translator") and self.translator is not None:
                translator_before = self.translator
                old_class = translator_before.__class__.__name__
                self.logging_manager.log_info(f"Previous translator: {old_class}")

            # รีเซ็ต translator เป็น None ก่อนสร้างใหม่
            self.translator = None

            try:
                self.translator = TranslatorFactory.create_translator(self.settings)
                if not self.translator:
                    self.logging_manager.log_error(
                        f"TranslatorFactory returned None for model: {model_name}"
                    )
                    raise ValueError(
                        f"Failed to create translator for model: {model_name}"
                    )

                # ตรวจสอบประเภทของ translator ที่ได้
                translator_class = self.translator.__class__.__name__
                self.logging_manager.log_info(
                    f"Successfully created {translator_class} instance: {translator_class}"
                )

                # Log current parameters
                params = self.translator.get_current_parameters()
                self.logging_manager.log_info(f"\nCurrent translator parameters:")
                self.logging_manager.log_info(f"Model: {params.get('model')}")
                self.logging_manager.log_info(f"Max tokens: {params.get('max_tokens')}")
                self.logging_manager.log_info(
                    f"Temperature: {params.get('temperature')}"
                )
                self.logging_manager.log_info(f"Top P: {params.get('top_p', 'N/A')}")

                # บันทึกเพิ่มเติมว่าเป็นการเปลี่ยนแปลงประเภทหรือไม่
                if translator_before:
                    new_class = self.translator.__class__.__name__
                    if old_class != new_class:
                        self.logging_manager.log_info(
                            f"Translator type changed: {old_class} -> {new_class}"
                        )
                    else:
                        self.logging_manager.log_info(
                            f"Translator type unchanged: {new_class}"
                        )

                del translator_before  # คืนหน่วยความจำ

            except Exception as e:
                self.logging_manager.log_error(f"Error creating translator: {e}")
                raise ValueError(f"Failed to create translator: {e}")

            return True

        except Exception as e:
            self.logging_manager.log_error(
                f"Error initializing OCR and translation: {e}"
            )
            raise

    def get_cached_ocr_result(self, area, image_hash):
        """ดึงผลลัพธ์ OCR จาก cache ด้วยระบบหมดอายุแบบปรับตามเนื้อหา"""
        if area in self.ocr_cache:
            cached_time, cached_hash, result = self.ocr_cache[area]
            current_time = time.time()

            # ปรับเวลาหมดอายุตามความยาวของข้อความ - ข้อความยาวอยู่ในแคชได้นานกว่า
            text_length = len(result) if result else 0
            expiry_time = min(self.cache_timeout * (1 + text_length / 100), 2.0)

            if (current_time - cached_time < expiry_time) and cached_hash == image_hash:
                return result
        return None

    def cache_ocr_result(self, area, image_hash, result):
        """เก็บผลลัพธ์ OCR ลง cache พร้อมการจัดการพื้นที่แคช"""
        self.ocr_cache[area] = (time.time(), image_hash, result)

        # จำกัดขนาดแคช ไม่ให้ใหญ่เกินไป
        if len(self.ocr_cache) > 10:  # เก็บแค่ 10 entry
            # ลบรายการที่เก่าที่สุด
            oldest_area = min(self.ocr_cache.keys(), key=lambda k: self.ocr_cache[k][0])
            del self.ocr_cache[oldest_area]

    def toggle_ocr_gpu(self):
        current_use_gpu = self.settings.get("use_gpu_for_ocr", False)
        new_use_gpu = not current_use_gpu
        self.settings.set_gpu_for_ocr(new_use_gpu)
        use_gpu = self.settings.get("use_gpu_for_ocr")

        easyocr_module = get_easyocr()
        if easyocr_module is None:
            self.reader = None
            self.logging_manager.log_warning(
                "Cannot toggle OCR GPU - EasyOCR not available"
            )
            return

        self.reader = easyocr_module.Reader(["en"], gpu=use_gpu)
        self.logging_manager.log_info(f"Switched OCR to {'GPU' if use_gpu else 'CPU'}")

    def ocr_toggle_callback(self):
        self.reinitialize_ocr()

    def init_variables(self):
        self.is_translating = False
        self.is_resizing = False
        self.translation_thread = None
        self.last_text = ""
        self.last_translation = ""
        self.last_translation_time = 0
        self.last_force_time = 0
        self.force_next_translation = False
        self.blinking = False
        self.mini_ui_blinking = False

        # เพิ่มตัวแปรเก็บสถานะ choice detection
        self.last_detected_as_choice = False
        self.last_choice_detection_time = 0
        self.choice_detection_cache_duration = 5.0  # จำสถานะ choice นาน 5 วินาที

        # *** PERFORMANCE: Image Preprocessing Cache - Balanced for Rapid Text Detection ***
        self.preprocessing_cache = {}  # เก็บ preprocessed images
        self.preprocessing_cache_max_size = 15  # จำกัดขนาด cache (ลดลงเพื่อความเร็ว)
        self.preprocessing_cache_timeout = (
            3.0  # Cache timeout 3 วินาที (ลดจาก 30s สำหรับ rapid dialogue)
        )

        # *** RAPID DETECTION: Variables for tracking fast dialogue changes ***
        self.rapid_dialogue_mode = False  # Track if we're in rapid dialogue
        self.consecutive_fast_changes = 0  # Count consecutive fast text changes
        self.last_text_change_time = 0  # Track when text last changed

        # *** กำหนด self.blink_interval ที่นี่ ถ้ายังไม่ได้กำหนดใน __init__ ก่อนเรียก init_variables ***
        # หรือถ้า __init__ กำหนด default แล้ว ที่นี่จะเป็นการ override (ถ้าจำเป็น)
        if not hasattr(self, "blink_interval"):  # เช็คเผื่อ __init__ ไม่ได้ตั้งไว้
            self.blink_interval = 500  # Interval การกระพริบ (ms)
            self.logging_manager.log_info(
                f"Blink interval set to {self.blink_interval}ms in init_variables (as it was not pre-set)."
            )
        else:
            self.logging_manager.log_info(
                f"Blink interval is {self.blink_interval}ms (from pre-set or init_variables default)."
            )

        self.main_window_pos = None
        self.translated_window_pos = None
        self.mini_ui_pos = None
        self.settings_window_pos = None
        self.show_area_window = None
        self.x = None
        self.y = None
        self.current_area = "A"  # ค่าเริ่มต้น
        self._logged_waiting_for_click = False
        self._logged_skipping_translation = False  # เอาธงลงเมื่อไม่ได้ Skip

        # *** ปรับปรุง: ค่าเริ่มต้นของ OCR ที่คำนึงถึงการประหยัด CPU ***
        self.ocr_interval = 0.5  # เปลี่ยนจาก 0.3 เป็น 0.5 วินาที
        self.max_ocr_interval = 3.0  # เปลี่ยนจาก 2.0 เป็น 3.0 วินาที
        self.cpu_check_interval = 1.0  # เช็ค CPU ทุก 1 วินาที
        self.cache_timeout = 1.0  # เก็บแคช OCR นาน 1 วินาที
        self.same_text_threshold = 20  # จำนวนครั้งของข้อความซ้ำก่อนจะเพิ่ม interval

        # ตัวแปรเพิ่มเติมสำหรับการควบคุม CPU
        self.last_ocr_time = time.time()
        self.same_text_count = 0
        self.last_signatures = {}

    def bind_events(self):
        self.root.bind("<Button-1>", self.start_move)
        self.root.bind("<ButtonRelease-1>", self.stop_move)
        self.root.bind("<B1-Motion>", self.do_move)

        # Bind event สำหรับอัพเดทขอบเมื่อหน้าต่างเปลี่ยนขนาด
        self.root.bind("<Configure>", self._on_window_configure)

        toggle_ui_shortcut = self.settings.get_shortcut("toggle_ui", "alt+h")
        start_stop_shortcut = self.settings.get_shortcut("start_stop_translate", "f9")

        if self.settings.get("enable_ui_toggle"):
            if "toggle_ui" in self.hotkeys:
                keyboard.remove_hotkey(self.hotkeys["toggle_ui"])
            self.hotkeys["toggle_ui"] = keyboard.add_hotkey(
                toggle_ui_shortcut, self.toggle_ui
            )

        if "start_stop_translate" in self.hotkeys:
            keyboard.remove_hotkey(self.hotkeys["start_stop_translate"])
        self.hotkeys["start_stop_translate"] = keyboard.add_hotkey(
            start_stop_shortcut, self.toggle_translation
        )

        # เพิ่ม hotkey สำหรับ force translate key
        force_translate_key_shortcut = self.settings.get_shortcut(
            "force_translate_key", "f10"
        )
        if "force_translate_key" in self.hotkeys:
            keyboard.remove_hotkey(self.hotkeys["force_translate_key"])
        self.hotkeys["force_translate_key"] = keyboard.add_hotkey(
            force_translate_key_shortcut, self.force_translate
        )

        if self.settings.get("enable_auto_hide"):
            for key in ["w", "a", "s", "d"]:
                if key in self.hotkeys:
                    keyboard.remove_hotkey(self.hotkeys[key])
                self.hotkeys[key] = keyboard.add_hotkey(
                    key, self.hide_and_stop_translation
                )

        self.logging_manager.log_info(
            f"Hotkeys bound: Toggle UI: {toggle_ui_shortcut}, Start/Stop Translate: {start_stop_shortcut}, Force Translate Key: {force_translate_key_shortcut}"
        )

    def update_hotkeys(self):
        self.load_shortcuts()
        self.remove_all_hotkeys()
        self.bind_events()

        # ตรวจสอบความสอดคล้องของ TUI state หลังจากอัพเดต hotkeys
        self.root.after(500, self.sync_tui_button_state)

        self.logging_manager.log_info(
            f"Hotkeys updated: Toggle UI: {self.toggle_ui_shortcut}, Start/Stop Translate: {self.start_stop_shortcut}, Force Translate Key: {self.force_translate_key_shortcut}"
        )

    def apply_saved_settings(self):
        # ถ้ามี font_manager ให้ใช้ในการอัพเดทฟอนต์
        if (
            hasattr(self, "font_manager")
            and hasattr(self.font_manager, "font_settings")
            and hasattr(self, "translated_ui")
        ):
            # ใช้เมธอดใหม่เพื่ออัพเดทการตั้งค่าฟอนต์
            font_name = self.settings.get("font")
            font_size = self.settings.get("font_size")
            self.update_font_settings(font_name, font_size)

            # ยังคงอัพเดตส่วนอื่นๆ ตามปกติ
            self.translated_ui.update_transparency(self.settings.get("transparency"))
            self.translated_ui_window.geometry(
                f"{self.settings.get('width')}x{self.settings.get('height')}"
            )
        else:
            # โค้ดเดิมถ้ายังไม่มี font_manager
            self.translated_ui.update_transparency(self.settings.get("transparency"))
            self.translated_ui.adjust_font_size(self.settings.get("font_size"))
            self.translated_ui.update_font(self.settings.get("font"))
            self.translated_ui_window.geometry(
                f"{self.settings.get('width')}x{self.settings.get('height')}"
            )

        self.remove_all_hotkeys()
        self.bind_events()

    def remove_all_hotkeys(self):
        for key in list(self.hotkeys.keys()):
            try:
                keyboard.remove_hotkey(self.hotkeys[key])
                del self.hotkeys[key]
            except Exception:
                pass
        self.hotkeys.clear()

    def toggle_settings(self):
        """Toggle the settings UI window visibility"""
        if self.settings_ui.settings_visible:
            self.settings_ui.close_settings()
            # ปุ่ม Settings เป็น icon แล้ว ไม่ต้องอัพเดทข้อความ
        else:
            # หยุดการแปลก่อนเปิดหน้าต่าง settings
            if self.is_translating:
                self.logging_manager.log_info(
                    "Stopping translation before opening Settings"
                )
                self.stop_translation()

            # ตรวจสอบตำแหน่งของ MBB window และส่งข้อมูลไปด้วย
            mbb_side = self.get_mbb_window_position_side()

            self.settings_ui.open_settings(
                self.root.winfo_x(),
                self.root.winfo_y(),
                self.root.winfo_width(),
                mbb_side,  # เพิ่มพารามิเตอร์ใหม่
            )
            # ปุ่ม Settings เป็น icon แล้ว ไม่ต้องอัพเดทข้อความ

    def apply_settings(self, settings_dict):
        """Apply settings and update UI components"""
        try:
            # --- START: ส่วนที่เพิ่มเพื่อรับค่าจาก Advance UI ---
            # ตรวจสอบและอัพเดทค่า CPU Limit
            if "cpu_limit" in settings_dict:
                self.set_cpu_limit(settings_dict["cpu_limit"])

            # ตรวจสอบและอัพเดทค่า use_gpu_for_ocr
            if "use_gpu_for_ocr" in settings_dict:
                new_gpu_setting = settings_dict["use_gpu_for_ocr"]
                if self.settings.get("use_gpu_for_ocr") != new_gpu_setting:
                    self.settings.set_gpu_for_ocr(new_gpu_setting)
                    self.reinitialize_ocr()  # สั่งให้ OCR เริ่มต้นใหม่ด้วยค่า GPU/CPU ใหม่

            # ตรวจสอบและอัพเดทค่าอื่นๆ จาก Advance UI
            if "screen_size" in settings_dict:
                self.settings.set("screen_size", settings_dict["screen_size"])

            if "display_scale" in settings_dict:
                self.settings.set("display_scale", settings_dict["display_scale"])
            # --- END: ส่วนที่เพิ่มเพื่อรับค่าจาก Advance UI ---

            # อัพเดท translated UI ถ้ามีการเปลี่ยนแปลงที่เกี่ยวข้อง
            if hasattr(self, "translated_ui") and self.translated_ui:
                if "transparency" in settings_dict:
                    self.translated_ui.update_transparency(
                        settings_dict["transparency"]
                    )

                # ใช้ font_manager ถ้ามี ในการอัพเดตการตั้งค่าฟอนต์
                if hasattr(self, "font_manager") and hasattr(
                    self.font_manager, "font_settings"
                ):
                    font_updated = False
                    font_name = None
                    font_size = None

                    if "font" in settings_dict:
                        font_name = settings_dict["font"]
                        font_updated = True

                    if "font_size" in settings_dict:
                        font_size = settings_dict["font_size"]
                        font_updated = True

                    if font_updated:
                        # ใช้เมธอดใหม่เพื่ออัพเดตฟอนต์
                        self.update_font_settings(font_name, font_size)
                else:
                    # ใช้โค้ดเดิมถ้ายังไม่มี font_manager (เพื่อความเข้ากันได้กับเวอร์ชันเก่า)
                    if "font_size" in settings_dict:
                        self.translated_ui.adjust_font_size(settings_dict["font_size"])
                    if "font" in settings_dict:
                        self.translated_ui.update_font(settings_dict["font"])

                # อัพเดทขนาดหน้าต่าง
                if "width" in settings_dict and "height" in settings_dict:
                    width = settings_dict["width"]
                    height = settings_dict["height"]
                    self.translated_ui.root.geometry(f"{width}x{height}")

                    # Force update UI
                    self.translated_ui.force_check_overflow()
                    self.translated_ui.root.update_idletasks()

            # อัพเดทค่า flags
            if "enable_force_translate" in settings_dict:
                self.enable_force_translate = settings_dict["enable_force_translate"]
            if "enable_auto_hide" in settings_dict:
                self.enable_auto_hide = settings_dict["enable_auto_hide"]
            if "enable_ui_toggle" in settings_dict:
                self.enable_ui_toggle = settings_dict["enable_ui_toggle"]

            # อัพเดท info label ถ้ามี
            if hasattr(self, "info_label"):
                self.update_info_label_with_model_color()

            logging.info("Settings applied successfully")
            return True

        except Exception as e:
            error_msg = f"Error applying settings: {e}"
            logging.error(error_msg)
            messagebox.showerror("Error", error_msg)
            return False

    def update_font_settings(self, font_name=None, font_size=None):
        """
        อัพเดตการตั้งค่าฟอนต์และแจ้งให้ components ทั้งหมดที่เกี่ยวข้องทราบ

        Args:
            font_name: ชื่อฟอนต์ใหม่ (ถ้ามี)
            font_size: ขนาดฟอนต์ใหม่ (ถ้ามี)
        """
        # ตรวจสอบว่ามี font_manager และ font_settings หรือไม่
        if not hasattr(self, "font_manager") or not hasattr(
            self.font_manager, "font_settings"
        ):
            return

        font_settings = self.font_manager.font_settings

        if font_name is None:
            font_name = font_settings.font_name
        if font_size is None:
            font_size = font_settings.font_size

        # อัพเดตการตั้งค่าฟอนต์ผ่าน font_settings
        font_settings.apply_font(font_name, font_size)

        # บันทึกล็อก
        self.logging_manager.log_info(f"อัพเดตฟอนต์เป็น {font_name} ขนาด {font_size}")

    def reinitialize_ocr(self):
        use_gpu = self.settings.get("use_gpu_for_ocr", False)

        easyocr_module = get_easyocr()
        if easyocr_module is None:
            self.reader = None
            self.logging_manager.log_warning(
                "Cannot reinitialize OCR - EasyOCR not available"
            )
            return

        self.reader = easyocr_module.Reader(["en"], gpu=use_gpu)
        self.logging_manager.log_info(
            f"OCR reinitialized with [{'GPU' if use_gpu else 'CPU'}]"
        )

    def update_api_settings(self):
        """อัพเดท API settings และสร้าง translator ใหม่ตามประเภท model

        Returns:
            bool: True ถ้าการอัพเดทสำเร็จ, False ถ้าไม่สำเร็จ

        หมายเหตุ: ฟังก์ชันนี้ทำหน้าที่หลักในการรีสตาร์ทระบบการแปลเมื่อมีการเปลี่ยนโมเดล
        """
        try:
            api_params = self.settings.get_api_parameters()
            if not api_params:
                logging.error("No API parameters found in settings")
                return False

            # ตรวจสอบประเภทของ translator ปัจจุบัน (ป้องกัน AttributeError)
            is_claude = (
                hasattr(self, "translator")
                and self.translator
                and isinstance(self.translator, TranslatorClaude)
            )
            is_gemini = (
                hasattr(self, "translator")
                and self.translator
                and isinstance(self.translator, TranslatorGemini)
            )
            is_openai = (
                hasattr(self, "translator")
                and self.translator
                and isinstance(self.translator, Translator)
                and not (is_claude or is_gemini)
            )

            current_translator_type = "unknown"
            if is_claude:
                current_translator_type = "claude"
            elif is_gemini:
                current_translator_type = "gemini"
            elif is_openai:
                current_translator_type = "openai"

            # ตรวจสอบประเภทของโมเดลใหม่
            new_model = api_params["model"]
            new_model_type = TranslatorFactory.validate_model_type(new_model)

            logging.info(
                f"Current translator type: {current_translator_type}, class: {self.translator.__class__.__name__}"
            )
            logging.info(f"New model: {new_model}, model type: {new_model_type}")

            # บันทึกการเปลี่ยนแปลงพารามิเตอร์
            self.logging_manager.log_info("\n=== API Parameters Updated ===")
            self.logging_manager.log_info(
                f"Current translator type: {current_translator_type}"
            )
            self.logging_manager.log_info(f"New model type: {new_model_type}")
            self.logging_manager.log_info(
                f"Model: {getattr(self.translator, 'model', 'unknown')} -> {new_model}"
            )
            self.logging_manager.log_info(
                f"Max tokens: {getattr(self.translator, 'max_tokens', 'N/A')} -> {api_params.get('max_tokens', 'N/A')}"
            )
            self.logging_manager.log_info(
                f"Temperature: {getattr(self.translator, 'temperature', 'N/A')} -> {api_params.get('temperature', 'N/A')}"
            )

            # ตรวจสอบว่าต้องสร้าง translator ใหม่หรือไม่
            model_changed = current_translator_type != new_model_type

            # ลบส่วนการตรวจสอบการเปลี่ยนแปลงพารามิเตอร์ที่ซ้ำซ้อน
            # และใช้ตัวแปรที่กำหนดไว้แล้ว
            previous_model_type = current_translator_type
            current_model_type = new_model_type

            if model_changed:
                # ยืนยันการรีสตาร์ทอีกรอบ (ครั้งที่ 2)
                confirm = messagebox.askyesno(
                    "ยืนยันการรีสตาร์ทระบบแปล",
                    f"การเปลี่ยนโมเดลจาก {previous_model_type} เป็น {current_model_type} จำเป็นต้องรีสตาร์ทระบบการแปล\n\nต้องการดำเนินการต่อหรือไม่?",
                    icon="warning",
                )

                if not confirm:
                    self.logging_manager.log_info("User cancelled restart process")
                    return False

                self.logging_manager.log_info(
                    f"Model changed from {previous_model_type} to {current_model_type}. Restarting translation system."
                )

                # =======================================
                # ส่วนสำคัญ: เริ่มกระบวนการรีสตาร์ทระบบแปล
                # =======================================

                # แสดงให้ผู้ใช้เห็นว่ากำลังรีสตาร์ทระบบจริงๆ
                # สร้างหน้าต่างแสดงการโหลด
                loading_window = tk.Toplevel(self.root)
                loading_window.title("กำลังรีสตาร์ทระบบแปล...")
                loading_window.geometry("300x120")
                loading_window.resizable(False, False)
                loading_window.configure(background="#141414")
                loading_window.attributes("-topmost", True)

                # จัดวางตำแหน่งให้อยู่กลาง
                if hasattr(self, "root"):
                    x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 150
                    y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 60
                    loading_window.geometry(f"+{x}+{y}")

                # ข้อความ
                message_label = tk.Label(
                    loading_window,
                    text=f"กำลังรีสตาร์ทระบบการแปลเพื่อเปลี่ยนเป็นโมเดล {new_model}...\nโปรดรอสักครู่",
                    bg="#141414",
                    fg="#ffffff",
                    font=("Segoe UI", 10),
                )
                message_label.pack(pady=(20, 10))

                # Progress bar
                progress = ttk.Progressbar(
                    loading_window,
                    orient="horizontal",
                    mode="indeterminate",
                    length=250,
                )
                progress.pack(pady=10)
                progress.start()

                # อัพเดทหน้าต่าง
                loading_window.update()

                # เก็บข้อมูลสถานะการแปลก่อนรีเซ็ต
                is_translating = getattr(self, "is_translating", False)

                # หยุดการแปลถ้ากำลังแปลอยู่
                if is_translating:
                    self.logging_manager.log_info(
                        "Stopping ongoing translation process"
                    )
                    self.stop_translation()

                # ปิดทุกหน้าต่างที่เกี่ยวข้องกับการแปล
                if (
                    hasattr(self, "translated_ui_window")
                    and self.translated_ui_window.winfo_exists()
                ):
                    self.translated_ui_window.withdraw()

                if (
                    hasattr(self, "translated_logs_window")
                    and self.translated_logs_window.winfo_exists()
                ):
                    self.translated_logs_window.withdraw()

                # บังคับให้การประมวลผลทุกส่วนทำงานเสร็จ
                self.root.update_idletasks()
                self.root.update()

                # รอให้กระบวนการทุกอย่างเสร็จสิ้น
                time.sleep(0.5)

                # ล้างข้อมูลเดิมทั้งหมด
                self.logging_manager.log_info(
                    "Clearing all translation-related variables"
                )

                # จัดการกับตัวแปรเดิม
                old_translator = self.translator
                self.translator = None

                # ล้างข้อมูลแคช
                if hasattr(self, "_ocr_cache"):
                    self._ocr_cache.clear()

                # ล้างข้อมูลใน text_corrector
                if hasattr(self, "text_corrector"):
                    self.text_corrector = TextCorrector()

                # อัพเดทความคืบหน้า
                progress["value"] = 30
                loading_window.update()

                # บังคับให้ garbage collector ทำงาน
                import gc

                # ทำลายตัวแปรเดิม
                del old_translator
                # บังคับให้คืนหน่วยความจำ
                gc.collect()

                # อัพเดทความคืบหน้า
                progress["value"] = 60
                loading_window.update()

                # ========================================================
                # ข้อสำคัญ: รีสตาร์ทระบบแปลโดยเรียกใช้ฟังก์ชันเริ่มต้นใหม่
                # init_ocr_and_translation() จะสร้าง translator ใหม่ตามโมเดล
                # ที่กำหนดใน settings ซึ่งถูกอัพเดทแล้วด้วยโมเดลใหม่
                # ========================================================

                self.logging_manager.log_info(
                    "====== RESTARTING TRANSLATION SYSTEM ======"
                )

                # สร้าง translator ใหม่โดยการรีสตาร์ทระบบ
                try:
                    # สร้าง translator ใหม่โดยการรีสตาร์ทระบบ
                    self.init_ocr_and_translation()

                    # ตรวจสอบว่าสร้างสำเร็จหรือไม่
                    if not self.translator:
                        error_message = f"Failed to create translator instance for {current_model_type}"
                        self.logging_manager.log_error(error_message)
                        messagebox.showerror("รีสตาร์ทล้มเหลว", error_message)
                        loading_window.destroy()
                        return False

                    # ตรวจสอบว่าเป็นประเภทที่ถูกต้องหรือไม่
                    if current_model_type == "claude" and not isinstance(
                        self.translator, TranslatorClaude
                    ):
                        error_message = f"Expected TranslatorClaude but got {self.translator.__class__.__name__}"
                        self.logging_manager.log_error(error_message)
                        messagebox.showerror("รีสตาร์ทล้มเหลว", error_message)
                        loading_window.destroy()
                        return False
                    elif current_model_type == "gemini" and not isinstance(
                        self.translator, TranslatorGemini
                    ):
                        error_message = f"Expected TranslatorGemini but got {self.translator.__class__.__name__}"
                        self.logging_manager.log_error(error_message)
                        messagebox.showerror("รีสตาร์ทล้มเหลว", error_message)
                        loading_window.destroy()
                        return False
                    elif current_model_type == "openai" and not (
                        isinstance(self.translator, Translator)
                        and not isinstance(
                            self.translator, (TranslatorClaude, TranslatorGemini)
                        )
                    ):
                        error_message = f"Expected Translator (OpenAI) but got {self.translator.__class__.__name__}"
                        self.logging_manager.log_error(error_message)
                        messagebox.showerror("รีสตาร์ทล้มเหลว", error_message)
                        loading_window.destroy()
                        return False

                except Exception as e:
                    self.logging_manager.log_error(
                        f"Failed to reinitialize translation system: {e}"
                    )
                    messagebox.showerror(
                        "รีสตาร์ทล้มเหลว", f"ไม่สามารถสร้างระบบแปลใหม่ได้: {e}"
                    )
                    loading_window.destroy()
                    return False

                # ตรวจสอบว่าสร้างสำเร็จหรือไม่
                translator_class_name = self.translator.__class__.__name__
                self.logging_manager.log_info(
                    f"Successfully created new translator: {translator_class_name} with model: {new_model}"
                )

                # ตรวจสอบประเภทของ translator ที่ได้
                self.logging_manager.log_info(
                    f"New translator class: {translator_class_name}"
                )
                self.logging_manager.log_info(
                    f"New translator parameters: {self.translator.get_current_parameters()}"
                )

                # อัพเดทความคืบหน้า
                progress["value"] = 100
                loading_window.update()

                # ปิดหน้าต่างโหลด
                loading_window.destroy()

                # ========================================================
                # ข้อสำคัญ: คืนสถานะของหน้าต่างและการแปลหลังจากรีสตาร์ท
                # ========================================================

                # แสดงหน้าต่างที่ถูกซ่อนไว้
                if (
                    hasattr(self, "translated_ui_window")
                    and self.translated_ui_window.winfo_exists()
                ):
                    if is_translating:
                        self.translated_ui_window.deiconify()

                if (
                    hasattr(self, "translated_logs_window")
                    and self.translated_logs_window.winfo_exists()
                    and self.translated_logs_instance.is_visible
                ):
                    self.translated_logs_window.deiconify()

                # คืนสถานะการแปลถ้าเดิมกำลังแปลอยู่
                if is_translating:
                    self.logging_manager.log_info("Restoring translation state")
                    self.is_translating = True
                    # เริ่มการแปลใหม่
                    self.toggle_translation()

                # แสดงข้อความสำเร็จ
                messagebox.showinfo(
                    "รีสตาร์ทสำเร็จ",
                    f"รีสตาร์ทระบบการแปลและเปลี่ยนโมเดลเป็น {new_model} เรียบร้อยแล้ว",
                )

            else:
                # ถ้าประเภทเดียวกัน อัพเดทพารามิเตอร์ในตัวที่มีอยู่
                try:
                    self.translator.update_parameters(
                        model=api_params["model"],
                        max_tokens=api_params["max_tokens"],
                        temperature=api_params["temperature"],
                        top_p=api_params.get("top_p", 0.9),
                    )
                    self.logging_manager.log_info(
                        f"Updated translator parameters: {api_params}"
                    )
                except Exception as e:
                    self.logging_manager.log_error(
                        f"Failed to update translator parameters: {e}"
                    )
                    messagebox.showerror("Error", f"ไม่สามารถอัพเดทพารามิเตอร์ได้: {e}")
                    return False

            # แสดงการตั้งค่าปัจจุบัน
            try:
                # ใช้ get_all_settings ถ้ามี หรือใช้ __dict__ แทนถ้าไม่มี
                if hasattr(self.settings, "get_all_settings"):
                    current_settings = self.settings.get_all_settings()
                else:
                    # ใช้ self.settings โดยตรงถ้าเป็น dictionary
                    current_settings = (
                        self.settings.settings
                        if hasattr(self.settings, "settings")
                        else {}
                    )

                self.logging_manager.log_info(f"Current Settings: {current_settings}")
                self.logging_manager.log_info("============================\n")
            except Exception as e:
                self.logging_manager.log_error(f"Error getting current settings: {e}")
                # ไม่ return False เพราะไม่ใช่ข้อผิดพลาดสำคัญ

            # อัพเดท info label ด้วยสีตามโมเดล
            if hasattr(self, "info_label"):
                self.update_info_label_with_model_color()

            # อัพเดท screen size display
            if hasattr(self, "get_current_settings_info"):
                info_text = self.get_current_settings_info()
                if hasattr(self, "info_label"):
                    self.info_label.config(text=info_text)

            return True

        except Exception as e:
            error_message = f"Error updating API settings: {e}"
            self.logging_manager.log_error(error_message)
            messagebox.showerror("Error", f"เกิดข้อผิดพลาดในการอัพเดทการตั้งค่า API: {e}")
            return False

    def sync_initial_areas(self):
        """
        Synchronize the initial area state based on saved settings.
        Sets MBB.current_area and updates relevant UI components.
        """
        try:
            # 1. โหลดหมายเลข preset ล่าสุดจาก settings
            current_preset_num = self.settings.get("current_preset", 1)

            # 2. โหลดข้อมูล preset จาก settings
            preset_data = self.settings.get_preset(current_preset_num)

            initial_area_str = "A+B"  # Default ถ้าหา preset ไม่เจอ
            if preset_data and "areas" in preset_data:
                # ใช้พื้นที่จาก preset ที่โหลดมา
                initial_area_str = preset_data["areas"]
                # กรณีพิเศษ: ทำให้ preset 1 เป็น "A+B" เสมอ (ถ้าข้อมูลไม่ตรง)
                if current_preset_num == 1 and initial_area_str != "A+B":
                    initial_area_str = "A+B"
                    logging.warning("Preset 1 definition corrected to 'A+B'.")
                    # อาจต้องพิจารณาบันทึกการแก้ไขนี้กลับไปที่ settings หรือไม่
                    # self.settings.save_preset(1, "A+B", preset_data.get("coordinates", {}))
            else:
                logging.warning(
                    f"Preset {current_preset_num} data not found or 'areas' key missing. Defaulting to 'A+B'."
                )
                # ถ้า preset ที่บันทึกไว้หาไม่เจอ ให้กลับไปใช้ preset 1
                current_preset_num = 1
                initial_area_str = "A+B"
                self.settings.set(
                    "current_area", current_preset_num
                )  # บันทึก preset fallback

            # 3. กำหนด State หลักใน MBB.py
            self.current_area = initial_area_str

            # 4. อัพเดทค่าใน settings ให้ตรงกัน
            self.settings.set("current_area", self.current_area)

            # 5. อัพเดทปุ่มไฮไลท์ใน Main UI
            # (จะถูกเรียกอีกครั้งหลัง update_ui_theme แต่เรียกที่นี่เพื่อให้ state เริ่มต้นถูกต้อง)
            self.update_area_button_highlights(self.current_area)

            # 6. สั่งให้ Control UI อัพเดทการแสดงผล (ถ้ามีอยู่)
            if hasattr(self, "control_ui") and self.control_ui:
                # ตรวจสอบว่า control_ui ยังไม่ถูกทำลาย
                if self.control_ui.root.winfo_exists():
                    # ส่งค่า area string และ preset number ปัจจุบันไปให้อัพเดท
                    self.control_ui.update_display(
                        self.current_area, current_preset_num
                    )
                    logging.info(
                        f"Instructed Control UI to update display: areas='{self.current_area}', preset={current_preset_num}"
                    )
                else:
                    logging.warning(
                        "Control UI root window does not exist during sync_initial_areas."
                    )

            # บันทึก log การ sync
            self.logging_manager.log_info(
                f"Initial areas synced: MBB.current_area set to '{self.current_area}' based on Preset {current_preset_num}"
            )

            # ไม่จำเป็นต้องเรียก update_ui_theme หรือ update_area_button_highlights ซ้ำที่นี่
            # เพราะจะถูกเรียกต่อใน __init__ อยู่แล้ว

        except Exception as e:
            self.logging_manager.log_error(f"Error in sync_initial_areas: {e}")
            # Fallback ในกรณีเกิดข้อผิดพลาดร้ายแรง
            self.current_area = "A+B"
            self.settings.set("current_area", "A+B")
            self.settings.set("current_preset", 1)
            self.update_area_button_highlights("A+B")
            if (
                hasattr(self, "control_ui")
                and self.control_ui
                and self.control_ui.root.winfo_exists()
            ):
                self.control_ui.update_display("A+B", 1)

            traceback.print_exc()

    def update_button_highlight(self, button, is_active):
        """
        อัพเดทสถานะไฮไลท์ของปุ่ม (เวอร์ชันแก้ไข รองรับปุ่มทุกรูปแบบ)
        """
        try:
            if not button or not button.winfo_exists():
                return

            highlight_color = appearance_manager.get_highlight_color()
            theme_accent_color = appearance_manager.get_accent_color()
            theme_text_color = appearance_manager.get_theme_color("text", "#ffffff")
            theme_bg_color = appearance_manager.bg_color

            if isinstance(button, tk.Canvas):
                if hasattr(button, "_bg_item"):
                    button.selected = is_active
                    if is_active:
                        # สถานะ Active
                        button.itemconfig(button._bg_item, fill=highlight_color)
                        # FIX: ทำให้ข้อความทั้ง 2 บรรทัดเป็นสีขาวเพื่อให้อ่านง่าย
                        if hasattr(button, "_text_items"):
                            button.itemconfig(button._text_items[0], fill="white")
                        if hasattr(button, "_text_line2_item"):
                            button.itemconfig(button._text_line2_item, fill="white")
                    else:
                        # สถานะ Inactive
                        button.itemconfig(button._bg_item, fill=button._original_bg)
                        if hasattr(button, "_text_items"):
                            button.itemconfig(
                                button._text_items[0], fill=theme_text_color
                            )
                        if hasattr(button, "_text_line2_item"):
                            button.itemconfig(
                                button._text_line2_item, fill=theme_accent_color
                            )
                else:
                    self.logging_manager.log_warning(
                        "update_button_highlight received an unknown Canvas button type."
                    )

            elif isinstance(button, tk.Button):
                if is_active:
                    button.configure(fg=highlight_color, bg="#404060")
                else:
                    if button == self.start_stop_button:
                        button.configure(fg="white", bg=theme_accent_color)
                    else:
                        button.configure(fg="white", bg=theme_bg_color)
            else:
                self.logging_manager.log_warning(
                    f"update_button_highlight called on an unsupported widget type: {type(button)}"
                )

        except Exception as e:
            import traceback

            self.logging_manager.log_error(
                f"Error in update_button_highlight: {e}\n{traceback.format_exc()}"
            )

    def get_screen_scale(self):
        """คำนวณ scale factor สำหรับหน้าจอ - ใช้ cache เพื่อประสิทธิภาพ"""
        current_time = time.time()

        # ตรวจสอบ cache
        if (
            self.cached_scale_x is not None
            and self.cached_scale_y is not None
            and current_time - self.scale_cache_timestamp < self.scale_cache_timeout
        ):
            return self.cached_scale_x, self.cached_scale_y

        # คำนวณใหม่ถ้า cache หมดอายุ
        screen_size = self.settings.get("screen_size", "2560x1440")
        screen_width, screen_height = map(int, screen_size.split("x"))
        scale_x = self.root.winfo_screenwidth() / screen_width
        scale_y = self.root.winfo_screenheight() / screen_height

        # บันทึกใน cache
        self.cached_scale_x = scale_x
        self.cached_scale_y = scale_y
        self.scale_cache_timestamp = current_time

        return scale_x, scale_y

    def scale_coordinates(self, x, y):
        """ปรับค่าพิกัดตาม scale ของหน้าจอ"""
        scale_x, scale_y = self.get_screen_scale()
        return int(x * scale_x), int(y * scale_y)

    def preprocess_image(self, image, area_type="normal"):
        """
        ปรับปรุงคุณภาพของภาพก่อนส่งเข้า OCR - Optimized Version with Caching
        ลดการประมวลผลที่หนักเพื่อประสิทธิภาพในการเล่นเกม

        Args:
            image: PIL.Image object
            area_type: ประเภทของพื้นที่ ('normal', 'choice', 'cutscene')

        Returns:
            PIL.Image: ภาพที่ผ่านการปรับปรุงแล้ว
        """
        try:
            # *** PERFORMANCE: ตรวจสอบ cache ก่อน ***
            cached_image = self.get_cached_preprocessed_image(image, area_type)
            if cached_image is not None:
                return cached_image

            # *** PERFORMANCE OPTIMIZATION: ลดการประมวลผลที่หนัก ***

            # ปรับแต่งเบื้องต้นตามประเภทพื้นที่
            if area_type == "choice":  # ตัวเลือก
                # ใช้ PIL เท่านั้น - ไม่ใช้ OpenCV CLAHE ที่หนัก
                # แปลงเป็นภาพขาวดำและปรับ contrast พอสมควร
                gray = image.convert("L")
                enhancer = ImageEnhance.Contrast(gray)
                processed = enhancer.enhance(1.4)  # เพิ่ม contrast พอสมควร

            elif area_type == "cutscene":  # คัทซีน
                # *** ลบ cv2.fastNlMeansDenoising ที่หนักมาก ***
                # ใช้การ resize และ contrast แทน
                gray = image.convert("L")
                # ขยายภาพเล็กน้อยเพื่อความชัด
                width = int(image.width * 1.2)
                height = int(image.height * 1.2)
                resized = gray.resize((width, height), Image.Resampling.LANCZOS)

                # ปรับ contrast เบาๆ
                enhancer = ImageEnhance.Contrast(resized)
                processed = enhancer.enhance(1.2)

            else:  # ข้อความทั่วไป - Simplified processing
                # ลดความซับซ้อน: ใช้ค่าคงที่แทนการคำนวณ dynamic
                resize_factor = 1.5
                contrast_factor = 1.3

                # ลด condition checking เหลือแค่กรณีจำเป็น
                image_size = image.width * image.height
                if image_size < 5000:  # ภาพเล็กมาก
                    resize_factor = 2.0
                elif image_size > 200000:  # ภาพใหญ่มาก
                    resize_factor = 1.2

                # 1. ขยายภาพ
                width = int(image.width * resize_factor)
                height = int(image.height * resize_factor)
                resized = image.resize((width, height), Image.Resampling.LANCZOS)

                # 2. ปรับ contrast
                enhancer = ImageEnhance.Contrast(resized)
                enhanced = enhancer.enhance(contrast_factor)

                # 3. แปลงเป็นภาพขาวดำ
                processed = enhanced.convert("L")

                # *** ลบ Sharpness enhancement ที่ไม่จำเป็น ***

            # *** PERFORMANCE: เก็บผลลัพธ์ลง cache ***
            self.cache_preprocessed_image(image, area_type, processed)

            return processed

        except Exception as e:
            logging.error(f"Error in image preprocessing: {e}")
            # ถ้าเกิดข้อผิดพลาด ให้ใช้ภาพต้นฉบับ
            return image

    def get_image_cache_key(self, image, area_type):
        """สร้าง cache key สำหรับ preprocessed image"""
        try:
            # ใช้ image signature และ area_type เป็น key
            import hashlib

            img_bytes = image.tobytes()
            hash_obj = hashlib.md5(img_bytes[:1024])  # ใช้แค่ 1KB แรกเพื่อความเร็ว
            hash_obj.update(area_type.encode())
            return hash_obj.hexdigest()
        except:
            return None

    def get_cached_preprocessed_image(self, image, area_type):
        """ดึง preprocessed image จาก cache - Optimized for rapid text detection"""
        try:
            cache_key = self.get_image_cache_key(image, area_type)
            if not cache_key or cache_key not in self.preprocessing_cache:
                return None

            cached_data = self.preprocessing_cache[cache_key]
            cached_time = cached_data["timestamp"]

            # *** RAPID DETECTION: ใช้ timeout ที่สั้นลงสำหรับ responsive detection ***
            import time

            current_time = time.time()

            # *** RAPID DETECTION: ปรับ timeout ตาม rapid dialogue mode ***
            if self.rapid_dialogue_mode:
                effective_timeout = 0.5  # 500ms สำหรับ rapid dialogue mode
                # ในโหมด rapid ให้ sensitive มากขึ้น
            else:
                # ตรวจสอบว่า dialog เปลี่ยนเร็วหรือไม่
                time_since_last_translation = current_time - self.last_translation_time

                if time_since_last_translation < 2.0:
                    effective_timeout = 1.0  # 1 วินาที สำหรับ dialogue ที่เปลี่ยนเร็ว
                else:
                    effective_timeout = (
                        self.preprocessing_cache_timeout
                    )  # 3 วินาที สำหรับ dialogue ปกติ

            if current_time - cached_time > effective_timeout:
                del self.preprocessing_cache[cache_key]
                return None

            return cached_data["image"]
        except:
            return None

    def cache_preprocessed_image(self, image, area_type, processed_image):
        """เก็บ preprocessed image ลง cache"""
        try:
            cache_key = self.get_image_cache_key(image, area_type)
            if not cache_key:
                return

            # ทำความสะอาด cache ถ้าเต็ม
            if len(self.preprocessing_cache) >= self.preprocessing_cache_max_size:
                # ลบ entry เก่าที่สุด
                oldest_key = min(
                    self.preprocessing_cache.keys(),
                    key=lambda k: self.preprocessing_cache[k]["timestamp"],
                )
                del self.preprocessing_cache[oldest_key]

            import time

            self.preprocessing_cache[cache_key] = {
                "image": processed_image,
                "timestamp": time.time(),
            }
        except:
            pass

    def update_rapid_dialogue_tracking(self, text_changed=False):
        """
        Track rapid dialogue mode for optimized responsiveness
        ติดตาม rapid dialogue mode เพื่อปรับ cache behavior

        Args:
            text_changed: Whether new text was detected
        """
        try:
            import time

            current_time = time.time()

            if text_changed:
                # Calculate time since last text change
                if self.last_text_change_time > 0:
                    time_diff = current_time - self.last_text_change_time

                    # Consider it "fast" if text changed within 1.5 seconds
                    if time_diff < 1.5:
                        self.consecutive_fast_changes += 1
                    else:
                        self.consecutive_fast_changes = 0

                self.last_text_change_time = current_time

                # Enter rapid mode if we have 2+ consecutive fast changes
                if self.consecutive_fast_changes >= 2:
                    self.rapid_dialogue_mode = True
                    self.logging_manager.log_info(
                        "🚀 Entered RAPID dialogue mode - optimizing for fast text detection"
                    )

            # Exit rapid mode if no text changes for 5 seconds
            elif (
                self.rapid_dialogue_mode
                and current_time - self.last_text_change_time > 5.0
            ):
                self.rapid_dialogue_mode = False
                self.consecutive_fast_changes = 0
                self.logging_manager.log_info(
                    "🐌 Exited rapid dialogue mode - back to normal detection"
                )

        except Exception as e:
            pass  # Fail silently to not interrupt main flow

    def get_full_screen_capture(self):
        """
        ดึงภาพหน้าจอทั้งหมดแล้วใช้ cache เพื่อประสิทธิภาพสูงสุด

        Returns:
            PIL.Image: ภาพหน้าจอทั้งหมด หรือ None ถ้าเกิดข้อผิดพลาด
        """
        current_time = time.time()

        # ตรวจสอบ cache
        if (
            self.full_screen_capture_cache is not None
            and current_time - self.full_screen_capture_timestamp
            < self.full_screen_cache_timeout
        ):
            return self.full_screen_capture_cache

        try:
            # จับภาพหน้าจอทั้งหมด (ครั้งเดียว)
            full_screen = ImageGrab.grab()

            # บันทึกใน cache
            self.full_screen_capture_cache = full_screen
            self.full_screen_capture_timestamp = current_time

            return full_screen

        except Exception as e:
            self.logging_manager.log_error(f"Error capturing full screen: {e}")
            return None

    def crop_area_from_full_screen(self, full_screen_image, area_config):
        """
        ตัดพื้นที่ที่ต้องการจากภาพหน้าจอทั้งหมด

        Args:
            full_screen_image: PIL.Image ของหน้าจอทั้งหมด
            area_config: dict ที่มี start_x, start_y, end_x, end_y

        Returns:
            PIL.Image: ภาพพื้นที่ที่ถูกตัด หรือ None ถ้าเกิดข้อผิดพลาด
        """
        try:
            scale_x, scale_y = self.get_screen_scale()

            # คำนวณพิกัดที่ scale แล้ว
            x1 = int(min(area_config["start_x"], area_config["end_x"]) * scale_x)
            y1 = int(min(area_config["start_y"], area_config["end_y"]) * scale_y)
            x2 = int(max(area_config["start_x"], area_config["end_x"]) * scale_x)
            y2 = int(max(area_config["start_y"], area_config["end_y"]) * scale_y)

            # ตรวจสอบความถูกต้องของพิกัด
            if x1 >= x2 or y1 >= y2:
                self.logging_manager.log_warning(
                    f"Invalid crop area: ({x1},{y1},{x2},{y2})"
                )
                return None

            # ตรวจสอบว่าพิกัดไม่เกินขอบเขตของภาพ
            img_width, img_height = full_screen_image.size
            x1 = max(0, min(x1, img_width))
            y1 = max(0, min(y1, img_height))
            x2 = max(0, min(x2, img_width))
            y2 = max(0, min(y2, img_height))

            # ตัดภาพ
            cropped = full_screen_image.crop((x1, y1, x2, y2))
            return cropped

        except Exception as e:
            self.logging_manager.log_error(f"Error cropping area from full screen: {e}")
            return None

    def capture_area_optimized(self, area_name):
        """
        Optimized area capture method ที่ใช้ single full-screen capture

        Args:
            area_name: ชื่อพื้นที่ (A, B, C)

        Returns:
            PIL.Image: ภาพพื้นที่ที่ถูกตัด หรือ None ถ้าเกิดข้อผิดพลาด
        """
        translate_area = self.settings.get_translate_area(area_name)
        if not translate_area:
            return None

        # ตรวจสอบพื้นที่ว่าง
        if (
            translate_area["start_x"] == translate_area["end_x"]
            or translate_area["start_y"] == translate_area["end_y"]
        ):
            return None

        # ใช้ optimized full-screen capture
        full_screen = self.get_full_screen_capture()
        if full_screen is not None:
            return self.crop_area_from_full_screen(full_screen, translate_area)
        else:
            # Fallback to individual capture
            scale_x, scale_y = self.get_screen_scale()
            x1 = int(min(translate_area["start_x"], translate_area["end_x"]) * scale_x)
            y1 = int(min(translate_area["start_y"], translate_area["end_y"]) * scale_y)
            x2 = int(max(translate_area["start_x"], translate_area["end_x"]) * scale_x)
            y2 = int(max(translate_area["start_y"], translate_area["end_y"]) * scale_y)

            if x1 >= x2 or y1 >= y2:
                return None

            return ImageGrab.grab(bbox=(x1, y1, x2, y2))

    def get_enhanced_image_signature(self, image):
        """
        Enhanced image signature optimized for rapid text detection
        Uses perceptual hashing with higher sensitivity for text changes

        Args:
            image: PIL.Image object

        Returns:
            tuple: Enhanced signature for comparison
        """
        try:
            # Convert to grayscale for consistent processing
            gray = image.convert("L")

            # Resize to standard size for comparison (32x32 for good balance)
            resized = gray.resize((32, 32), Image.Resampling.LANCZOS)

            # Convert to numpy array
            img_array = np.array(resized)

            # Create perceptual hash using DCT-like approach
            # Split into 4x4 blocks and calculate mean for each block
            signature = []
            block_size = 8  # 32/8 = 4 blocks per dimension

            for i in range(0, 32, block_size):
                for j in range(0, 32, block_size):
                    block = img_array[i : i + block_size, j : j + block_size]
                    signature.append(np.mean(block))

            # Add overall image statistics for additional robustness
            signature.extend(
                [
                    np.mean(img_array),  # Overall brightness
                    np.std(img_array),  # Contrast
                    np.min(img_array),  # Darkest point
                    np.max(img_array),  # Brightest point
                ]
            )

            return tuple(signature)

        except Exception as e:
            self.logging_manager.log_error(
                f"Error creating enhanced image signature: {e}"
            )
            # Fallback to simple hash
            return tuple([hash(str(image.tobytes()))])

    def compare_image_signatures(self, sig1, sig2, threshold=0.92):
        """
        Compare two image signatures optimized for rapid text detection
        Lower threshold for higher sensitivity to text changes

        Args:
            sig1, sig2: Image signatures to compare
            threshold: Similarity threshold (0.0-1.0, lowered from 0.95 to 0.92 for better text detection)

        Returns:
            bool: True if images are considered similar (unchanged)
        """
        try:
            if len(sig1) != len(sig2):
                return False

            # Calculate normalized correlation coefficient
            sig1_array = np.array(sig1)
            sig2_array = np.array(sig2)

            # Handle edge case where standard deviation is 0
            if np.std(sig1_array) == 0 or np.std(sig2_array) == 0:
                return np.array_equal(sig1_array, sig2_array)

            correlation = np.corrcoef(sig1_array, sig2_array)[0, 1]

            # Handle NaN case
            if np.isnan(correlation):
                return False

            return correlation >= threshold

        except Exception as e:
            self.logging_manager.log_error(f"Error comparing image signatures: {e}")
            # Fallback to simple equality check
            return sig1 == sig2

    def invalidate_capture_cache(self):
        """
        Invalidate all capture caches - call when screen resolution changes or settings update
        """
        self.cached_scale_x = None
        self.cached_scale_y = None
        self.scale_cache_timestamp = 0
        self.full_screen_capture_cache = None
        self.full_screen_capture_timestamp = 0
        self.logging_manager.log_info("Screen capture cache invalidated")

    def test_capture_optimization(self):
        """
        Performance test method for screen capture optimization
        Compares old vs new capture methods for performance analysis
        """
        import time

        self.logging_manager.log_info("=== Screen Capture Optimization Test ===")

        # Test areas
        test_areas = ["A", "B", "C"]

        # Test 1: Full-screen capture performance
        start_time = time.time()
        full_screen = self.get_full_screen_capture()
        full_screen_time = time.time() - start_time

        if full_screen:
            self.logging_manager.log_info(
                f"Full-screen capture: {full_screen_time:.4f}s"
            )

            # Test 2: Area cropping performance
            total_crop_time = 0
            successful_crops = 0

            for area in test_areas:
                translate_area = self.settings.get_translate_area(area)
                if translate_area:
                    start_time = time.time()
                    cropped = self.crop_area_from_full_screen(
                        full_screen, translate_area
                    )
                    crop_time = time.time() - start_time
                    total_crop_time += crop_time

                    if cropped:
                        successful_crops += 1
                        self.logging_manager.log_info(
                            f"Area {area} crop: {crop_time:.4f}s"
                        )

            avg_crop_time = total_crop_time / len(test_areas) if test_areas else 0
            self.logging_manager.log_info(f"Average crop time: {avg_crop_time:.4f}s")
            self.logging_manager.log_info(
                f"Successful crops: {successful_crops}/{len(test_areas)}"
            )

            # Test 3: Cache performance
            start_time = time.time()
            cached_screen = self.get_full_screen_capture()  # Should use cache
            cache_time = time.time() - start_time
            self.logging_manager.log_info(
                f"Cached full-screen capture: {cache_time:.4f}s"
            )

            # Test 4: Scale calculation cache
            start_time = time.time()
            scale_x1, scale_y1 = self.get_screen_scale()
            first_scale_time = time.time() - start_time

            start_time = time.time()
            scale_x2, scale_y2 = self.get_screen_scale()  # Should use cache
            cached_scale_time = time.time() - start_time

            self.logging_manager.log_info(
                f"First scale calculation: {first_scale_time:.4f}s"
            )
            self.logging_manager.log_info(
                f"Cached scale calculation: {cached_scale_time:.4f}s"
            )

            # Performance summary
            total_optimized_time = full_screen_time + total_crop_time
            estimated_old_time = (
                len(test_areas) * full_screen_time
            )  # Rough estimate of old method

            if estimated_old_time > 0:
                performance_gain = (
                    (estimated_old_time - total_optimized_time) / estimated_old_time
                ) * 100
                self.logging_manager.log_info(
                    f"Estimated performance gain: {performance_gain:.1f}%"
                )

            self.logging_manager.log_info(
                "=== Screen Capture Optimization Test Complete ==="
            )
            return True
        else:
            self.logging_manager.log_error("Full-screen capture failed during test")
            return False

    def _cpu_monitor_thread(self):
        """
        Thread ที่ทำงานในเบื้องหลังเพื่อตรวจสอบการใช้งาน CPU อย่างต่อเนื่อง
        และส่งสัญญาณเมื่อ CPU เกินขีดจำกัดที่ตั้งไว้
        """
        import psutil  # Import ใน Thread โดยตรง

        # ตรวจสอบค่าเริ่มต้น/ค่าที่อาจยังไม่ได้ตั้ง
        if not hasattr(self, "cpu_limit"):
            self.cpu_limit = self.settings.get("cpu_limit", 80)
        if not hasattr(self, "cpu_check_interval"):
            # ดึงค่า cpu_check_interval ที่เหมาะสมจาก set_cpu_limit logic
            # หรือกำหนดค่าเริ่มต้นที่ปลอดภัยหากยังไม่ได้เรียก set_cpu_limit
            current_limit_for_interval = self.settings.get("cpu_limit", 80)
            if current_limit_for_interval <= 50:
                self.cpu_check_interval = 0.5
            elif current_limit_for_interval <= 60:
                self.cpu_check_interval = 0.7
            else:
                self.cpu_check_interval = 1.0
            self.logging_manager.log_info(
                f"CPUMonitorThread: Initial cpu_check_interval set to {self.cpu_check_interval:.2f}s based on limit {current_limit_for_interval}%"
            )

        while not self._stop_cpu_monitor_event.is_set():
            try:
                # หน่วงเวลาก่อนตรวจสอบครั้งถัดไป
                # ใช้ Event wait เพื่อให้สามารถหยุด Thread ได้ทันที
                if self._stop_cpu_monitor_event.wait(timeout=self.cpu_check_interval):
                    break  # ถ้าได้รับ Event ให้หยุด ก็ออกจาก Loop

                current_cpu = psutil.cpu_percent(
                    interval=None
                )  # interval=None จะ non-blocking

                if current_cpu > self.cpu_limit:
                    if not self._cpu_monitor_event.is_set():  # ส่ง Event ถ้ายังไม่ได้ส่ง
                        self._cpu_monitor_event.set()
                        # บรรทัดที่แก้ไข: เปลี่ยนจาก log_debug เป็น log_info
                        self.logging_manager.log_info(
                            f"CPUMonitorThread: CPU usage {current_cpu:.1f}% exceeded limit {self.cpu_limit}%. Signaling main loop."
                        )
                # else:
                # Optional: อาจจะ clear event ที่นี่ถ้า CPU กลับมาปกติ
                # แต่การ clear ใน translation_loop จะดีกว่า เพราะ main loop เป็นคนจัดการ ocr_interval
                # pass

            except Exception as e:
                self.logging_manager.log_error(f"Error in CPU monitor thread: {e}")
                # กรณีเกิด Error หนักๆ อาจจะต้องพิจารณาหยุด Thread หรือรอสักพักแล้วลองใหม่
                if self._stop_cpu_monitor_event.wait(
                    timeout=5.0
                ):  # รอ 5 วินาที ก่อนลองใหม่
                    break
        self.logging_manager.log_info("CPU Monitor thread stopped.")

    def check_cpu_usage(self):
        """
        ตรวจสอบการใช้ CPU ปัจจุบัน (เมธอดนี้อาจจะไม่ถูกเรียกใช้โดยตรงจาก translation_loop อีกต่อไป)
        Returns:
            float: เปอร์เซ็นต์การใช้งาน CPU ปัจจุบัน, หรือ -1 ถ้า psutil ไม่มี.
        """
        if not self.has_psutil:
            # self.logging_manager.log_debug("psutil not available for check_cpu_usage.") # อาจจะ log บ่อยไป
            return -1
        try:

            # interval=None ทำให้ non-blocking และคืนค่า CPU usage ตั้งแต่การเรียกครั้งก่อน
            # หรือถ้าเป็นครั้งแรก จะคืน 0.0 หลังจาก sleep สั้นๆ เพื่อคำนวณ
            # เพื่อให้ได้ค่าที่ real-time ขึ้น อาจจะต้องมี interval เล็กน้อย
            # แต่การเรียกจากนอก _cpu_monitor_thread ควรระวังเรื่อง blocking
            current_cpu = psutil.cpu_percent(interval=0.01)  # type: ignore # ให้ interval สั้นๆ พอ
            return current_cpu
        except Exception as e:
            self.logging_manager.log_error(
                f"Error in check_cpu_usage (direct call): {e}"
            )
            return -1

    def set_cpu_limit(self, limit):
        """ตั้งค่าลิมิต CPU พร้อมกับการปรับแต่งที่เข้มงวดขึ้น

        Args:
            limit (int): เปอร์เซ็นต์ลิมิต CPU (0-100)
        """
        if not 0 <= limit <= 100:
            limit = 80

        self.cpu_limit = limit  # Thread ใหม่จะอ่านค่านี้
        self.settings.set("cpu_limit", limit)
        # self.settings.save_settings() # set() จัดการให้แล้ว

        # แสดง Log บนคอนโซลโดยตรง
        print(f"✅ CPU limit has been set to {limit}%")  # <<< เพิ่มบรรทัดนี้

        self.logging_manager.log_info(f"CPU limit set to {limit}%")

        # ปรับค่าพื้นฐานของ OCR และการตรวจสอบ CPU ทันที
        if limit <= 50:
            self.ocr_interval = 1.2
            self.max_ocr_interval = 6.0
            self.cpu_check_interval = 0.5  # Thread จะใช้ค่านี้
            self.cache_timeout = 2.0
            self.same_text_threshold = 15
            self.set_ocr_speed("normal")  # บังคับใช้โหมดปกติ
            self.logging_manager.log_info(
                "Applied ultra-aggressive CPU saving settings. OCR forced to normal."
            )
        elif limit <= 60:
            self.ocr_interval = 0.8
            self.max_ocr_interval = 4.0
            self.cpu_check_interval = 0.7  # Thread จะใช้ค่านี้
            self.cache_timeout = 1.5
            self.same_text_threshold = 18
            # ไม่บังคับ ocr_speed ที่นี่ ให้คงค่าเดิมถ้าผู้ใช้ตั้งไว้
            self.logging_manager.log_info("Applied aggressive CPU saving settings.")
        else:  # 80% ขึ้นไป
            self.ocr_interval = 0.5
            self.max_ocr_interval = 2.5
            self.cpu_check_interval = 1.0  # Thread จะใช้ค่านี้
            self.cache_timeout = 1.0
            self.same_text_threshold = 20
            # ไม่บังคับ ocr_speed ที่นี่
            self.logging_manager.log_info("Applied standard CPU settings.")

        # แจ้งเตือนถ้า psutil ไม่มี
        if not self.has_psutil:
            self.logging_manager.log_warning(
                "psutil not available. CPU limit changes may have reduced effect on OCR intervals."
            )

    def smart_ocr_config(self, is_potential_choice=False):
        """
        กำหนดค่าคอนฟิกสำหรับ EasyOCR แบบไดนามิกตามประเภทของข้อความที่คาดการณ์
        Args:
            is_potential_choice (bool): True ถ้าคาดว่าพื้นที่นั้นอาจเป็นตัวเลือก (choice)
        Returns:
            dict: Configuration dictionary สำหรับ EasyOCR
        """
        if is_potential_choice:
            # คอนฟิกสำหรับการตรวจจับตัวเลือก (choice detection) ต้องการข้อมูลตำแหน่ง (detail=1)
            # และไม่รวมย่อหน้า (paragraph=False) เพื่อให้ได้แต่ละบรรทัดแยกกัน
            # text_threshold อาจจะต้องปรับค่าเพื่อให้จับข้อความตัวเลือกได้ดีที่สุด
            self.logging_manager.log_info("Using OCR config for potential choice area.")
            return {
                "detail": 1,
                "paragraph": False,
                "width_ths": 0.7,  # จากแผน OCR_refactor_plan.md
                "height_ths": 0.5,  # จากแผน OCR_refactor_plan.md
                "y_ths": 0.5,  # จากแผน OCR_refactor_plan.md
                "text_threshold": 0.5,  # อาจปรับค่านี้เพื่อความแม่นยำในการจับตัวเลือก
            }
        else:
            # คอนฟิกสำหรับการอ่านข้อความทั่วไป (คล้ายของเดิม)
            # ใช้ self.ocr_speed เพื่อกำหนด confidence ตามโค้ดเดิมใน capture_and_ocr
            confidence = 0.6 if self.ocr_speed == "high" else 0.7
            self.logging_manager.log_info(
                f"Using general OCR config with confidence: {confidence}"
            )
            return {
                "detail": 0,
                "paragraph": True,
                "min_size": 3,  # ค่าเดิมจาก MBB.py
                "text_threshold": confidence,
            }

    def _get_bbox_y_center(self, bbox):
        """คำนวณพิกัดกึ่งกลางแกน Y ของ bounding box"""
        if (
            not bbox or len(bbox) < 2
        ):  # bbox ควรมีอย่างน้อย 2 จุด (เช่น top-left, bottom-right) หรือ 4 จุด
            return 0
        min_y = min(p[1] for p in bbox)
        max_y = max(p[1] for p in bbox)
        return (min_y + max_y) / 2

    def _get_bbox_height(self, bbox):
        """คำนวณความสูงของ bounding box"""
        if not bbox or len(bbox) < 2:
            return 0
        min_y = min(p[1] for p in bbox)
        max_y = max(p[1] for p in bbox)
        return max_y - min_y

    def _group_into_lines_easyocr(self, ocr_results):
        """
        จัดกลุ่มผลลัพธ์ EasyOCR ให้เป็นบรรทัดของข้อความ
        Input: ocr_results = List of (bbox, text, confidence) จาก EasyOCR
        Output: List of strings, โดยแต่ละ string คือข้อความที่รวมกันในหนึ่งบรรทัด
        """
        if not ocr_results:
            self.logging_manager.log_info(
                "_group_into_lines_easyocr: Received empty ocr_results."
            )
            return []

        # แปลง EasyOCR format เป็น format ที่ _group_into_lines() คาดหวัง
        # EasyOCR: (bbox, text, confidence) → PaddleOCR: [bbox, text, confidence]
        converted_results = []
        for bbox, text, confidence in ocr_results:
            if text and text.strip():  # เฉพาะข้อความที่ไม่ว่าง
                converted_results.append([bbox, text, confidence])

        if not converted_results:
            return []

        # ใช้ logic เดียวกับ _group_into_lines() แต่ปรับให้เข้ากับ EasyOCR format
        try:
            # เรียงตามตำแหน่ง Y แล้วตาม X
            sorted_results = sorted(
                converted_results, key=lambda item: (item[0][0][1], item[0][0][0])
            )
        except (IndexError, TypeError) as e:
            self.logging_manager.log_warning(
                f"_group_into_lines_easyocr: Error sorting results: {e}. Using original order."
            )
            sorted_results = converted_results

        lines = []
        current_line_texts = []
        current_y = None
        y_tolerance = 10  # ความต่างของ Y ที่ยอมรับได้สำหรับบรรทัดเดียวกัน

        for result in sorted_results:
            bbox, text, confidence = result
            try:
                # คำนวณ Y กึ่งกลางของ bounding box
                if isinstance(bbox, list) and len(bbox) >= 2:
                    if isinstance(
                        bbox[0], list
                    ):  # EasyOCR format: [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
                        y_center = sum(point[1] for point in bbox) / len(bbox)
                    else:  # Simple format: [x1, y1, x2, y2]
                        y_center = (bbox[1] + bbox[3]) / 2
                else:
                    y_center = 0

                # ตรวจสอบว่าอยู่บรรทัดเดียวกันหรือไม่
                if current_y is None or abs(y_center - current_y) <= y_tolerance:
                    # บรรทัดเดียวกัน
                    current_line_texts.append(text)
                    current_y = y_center if current_y is None else current_y
                else:
                    # บรรทัดใหม่
                    if current_line_texts:
                        lines.append(" ".join(current_line_texts))
                    current_line_texts = [text]
                    current_y = y_center

            except (IndexError, TypeError, KeyError) as e:
                self.logging_manager.log_warning(
                    f"_group_into_lines_easyocr: Error processing bbox {bbox}: {e}"
                )
                # ถ้าไม่สามารถประมวลผล bbox ได้ ให้เพิ่มเป็นบรรทัดแยก
                if current_line_texts:
                    lines.append(" ".join(current_line_texts))
                    current_line_texts = []
                lines.append(text)
                current_y = None

        # เพิ่มบรรทัดสุดท้าย
        if current_line_texts:
            lines.append(" ".join(current_line_texts))

        self.logging_manager.log_info(
            f"_group_into_lines_easyocr: Grouped {len(ocr_results)} OCR results into {len(lines)} lines"
        )
        return [line.strip() for line in lines if line.strip()]
        """
        จัดกลุ่มผลลัพธ์ OCR (ที่มี bounding boxes) ให้เป็นบรรทัดของข้อความ
        Input: ocr_results = List of (bbox, text, confidence), คาดว่าเรียงจากบนลงล่างมาแล้วระดับหนึ่ง
        Output: List of strings, โดยแต่ละ string คือข้อความที่รวมกันในหนึ่งบรรทัด
        """
        if not ocr_results:
            self.logging_manager.log_info(
                "_group_into_lines: Received empty ocr_results."
            )
            return []

        # Pre-sort results by y-coordinate of the top-left point of the bbox, then by x-coordinate
        # This helps in processing elements in a more natural reading order.
        # bbox for PaddleOCR is [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
        try:
            sorted_ocr_results_for_grouping = sorted(
                ocr_results, key=lambda item: (item[0][0][1], item[0][0][0])
            )
        except IndexError as e_sort_group:
            self.logging_manager.log_warning(
                f"_group_into_lines: Error sorting ocr_results (IndexError: {e_sort_group}). Using original order."
            )
            sorted_ocr_results_for_grouping = ocr_results
        except Exception as e_sort_other_group:
            self.logging_manager.log_warning(
                f"_group_into_lines: Unexpected error sorting ocr_results ({type(e_sort_other_group).__name__}: {e_sort_other_group}). Using original order."
            )
            sorted_ocr_results_for_grouping = ocr_results

        lines_data = []
        current_line_elements = []

        if not sorted_ocr_results_for_grouping:  # Check after attempting sort
            return []

        # Calculate average box height more robustly
        valid_box_heights = [
            self._get_bbox_height(item[0])
            for item in sorted_ocr_results_for_grouping
            if item[0] and len(item[0]) == 4  # Ensure bbox is valid
        ]
        if valid_box_heights:
            avg_box_height = sum(valid_box_heights) / len(valid_box_heights)
        else:
            avg_box_height = 20  # Default if no valid boxes
        if avg_box_height <= 0:  # Prevent division by zero or negative tolerance
            avg_box_height = 20

        # y_tolerance: if the vertical distance between centers is greater than this, it's a new line.
        # Consider also if the bottom of the last box is significantly above the top of the current box.
        y_tolerance_center_diff = (
            avg_box_height * 0.4
        )  # Reduced from 0.6 to 0.4, more sensitive to new lines for choice dialogue
        y_tolerance_overlap = (
            avg_box_height * 0.2
        )  # Reduced from 0.3 to 0.2, more sensitive

        self.logging_manager.log_info(
            f"_group_into_lines: avg_box_height={avg_box_height:.2f}, y_tolerance_center_diff={y_tolerance_center_diff:.2f}, y_tolerance_overlap={y_tolerance_overlap:.2f}"
        )

        for item_bbox, item_text, item_confidence in sorted_ocr_results_for_grouping:
            # Ensure item_bbox is valid before processing
            if (
                not item_bbox
                or len(item_bbox) != 4
                or not all(isinstance(p, list) and len(p) == 2 for p in item_bbox)
            ):
                self.logging_manager.log_warning(
                    f"_group_into_lines: Skipping item with invalid bbox: {item_bbox}"
                )
                continue

            item_y_center = self._get_bbox_y_center(item_bbox)
            item_x_start = item_bbox[0][0]  # Top-left x
            item_min_y = min(p[1] for p in item_bbox)
            item_max_y = max(p[1] for p in item_bbox)

            if not current_line_elements:
                current_line_elements.append(
                    {
                        "text": item_text,
                        "x_start": item_x_start,
                        "y_center": item_y_center,
                        "min_y": item_min_y,
                        "max_y": item_max_y,
                        "bbox": item_bbox,
                    }
                )
            else:
                last_element = current_line_elements[-1]
                last_y_center = last_element["y_center"]
                last_max_y = last_element["max_y"]

                # Condition for starting a new line:
                # 1. Significant difference in y-centers OR
                # 2. Current element starts clearly below the last element (gap > tolerance_overlap)
                is_new_line = False
                if abs(item_y_center - last_y_center) > y_tolerance_center_diff:
                    is_new_line = True
                    logging.debug(
                        f"New line due to Y-center diff: |{item_y_center:.1f} - {last_y_center:.1f}| > {y_tolerance_center_diff:.1f} for '{item_text}'"
                    )
                elif item_min_y > (last_max_y + y_tolerance_overlap):
                    is_new_line = True
                    logging.debug(
                        f"New line due to Y-gap: {item_min_y:.1f} > ({last_max_y:.1f} + {y_tolerance_overlap:.1f}) for '{item_text}'"
                    )

                if is_new_line:
                    if current_line_elements:  # Finalize the previous line
                        lines_data.append(list(current_line_elements))  # Store a copy
                    current_line_elements = [  # Start a new line
                        {
                            "text": item_text,
                            "x_start": item_x_start,
                            "y_center": item_y_center,
                            "min_y": item_min_y,
                            "max_y": item_max_y,
                            "bbox": item_bbox,
                        }
                    ]
                else:  # Append to the current line
                    current_line_elements.append(
                        {
                            "text": item_text,
                            "x_start": item_x_start,
                            "y_center": item_y_center,
                            "min_y": item_min_y,
                            "max_y": item_max_y,
                            "bbox": item_bbox,
                        }
                    )

        if current_line_elements:  # Add the last accumulated line
            lines_data.append(list(current_line_elements))

        final_lines = []
        for line_idx, line_elements in enumerate(lines_data):
            # Sort elements within each line by their x_start coordinate
            line_elements.sort(key=lambda e: e["x_start"])
            # Join the text of sorted elements
            assembled_line = " ".join([e["text"] for e in line_elements])
            final_lines.append(assembled_line)
            logging.debug(
                f"_group_into_lines: Assembled line {line_idx}: '{assembled_line}' from {len(line_elements)} elements."
            )

        self.logging_manager.log_info(
            f"_group_into_lines: Grouped OCR results into {len(final_lines)} lines: {final_lines}"
        )
        return final_lines

    def _detect_choice_format(self, lines):
        """
        ตรวจจับรูปแบบ choice format จากรายการบรรทัดข้อความ
        Input: lines = List of strings, โดยแต่ละ string คือบรรทัดข้อความ
        Output: Tuple (is_choice (bool), header (str or None), choices (List[str] or empty list))
        """
        if not lines:
            self.logging_manager.log_info("_detect_choice_format: No lines provided.")
            return False, None, []

        # Patterns for choice headers - made slightly more flexible
        # Allowing for potential OCR errors or variations.
        choice_headers_patterns = [
            r"^\s*what\s+will\s+you\s+say\s*\??\s*$",  # "What will you say?" with flexible spacing and optional ?
            r"^\s*what\s+will\s+you\s+do\s*\??\s*$",  # "What will you do?"
            r"^\s*select\s+an\s+option\s*:?\s*$",  # "Select an option"
            r"^\s*choose\s+your\s+response\s*:?\s*$",  # "Choose your response"
            # Thai patterns - if your OCR can detect Thai headers directly
            r"^\s*คุณจะพูดว่าอย่างไร\s*\??\s*$",
            r"^\s*คุณจะพูดอะไร\s*\??\s*$",
        ]

        header_line_index = -1
        detected_header_text = None
        max_header_lines_to_check = min(
            2, len(lines)
        )  # Check only the first 1 or 2 lines for a header

        for i in range(max_header_lines_to_check):
            line_text = lines[
                i
            ].strip()  # Ensure leading/trailing spaces are removed for matching
            for pattern_idx, pattern in enumerate(choice_headers_patterns):
                if re.match(pattern, line_text, re.IGNORECASE):
                    detected_header_text = lines[
                        i
                    ]  # Use the original line text, not stripped, for header
                    header_line_index = i
                    self.logging_manager.log_info(
                        f"_detect_choice_format: Found potential header '{detected_header_text.strip()}' at line {i} using pattern index {pattern_idx}."
                    )
                    break
            if detected_header_text:
                break

        if detected_header_text is not None:
            # Choices start from the line after the header
            potential_choices_lines = lines[header_line_index + 1 :]
            actual_choices = []

            # Filter and clean choices
            # A choice should not be another header, should have content,
            # and should not be excessively long if it's just a short option.
            for choice_line in potential_choices_lines:
                stripped_choice = choice_line.strip()
                if not stripped_choice:  # Skip empty lines
                    continue

                is_another_header = False
                for (
                    pattern
                ) in (
                    choice_headers_patterns
                ):  # Check if this "choice" is actually another header
                    if re.match(pattern, stripped_choice, re.IGNORECASE):
                        is_another_header = True
                        break
                if is_another_header:
                    logging.debug(
                        f"_detect_choice_format: Line '{stripped_choice}' looks like another header, stopping choice collection here."
                    )
                    break  # Stop if we encounter another header

                # Add more conditions if needed (e.g., length constraints, specific markers)
                # For FFXIV, choices are usually distinct lines of text.
                if len(stripped_choice) > 1:  # Must have some content
                    # ตรวจสอบว่าบรรทัดนี้เป็นตัวเลือกที่ติดกันหลายตัวหรือไม่
                    # เช่น "I suppose I ought to thank you both as well. You were never one to forsake a friend, Alphinaud. I'll be counting on you."

                    # หากข้อความยาวมากและมีจุดคั่นหลายจุด อาจเป็นตัวเลือกที่ติดกัน
                    if len(stripped_choice) > 80 and stripped_choice.count(".") >= 2:
                        # ลองแยกตามจุด (.) ที่ตามด้วยช่องว่างและตัวอักษรใหญ่
                        potential_splits = re.split(r"\.(\s+[A-Z])", stripped_choice)
                        if len(potential_splits) >= 3:  # หากแยกได้อย่างน้อย 2 ส่วน
                            # รวมกันใหม่เป็นประโยคแยก
                            split_choices = []
                            current_sentence = potential_splits[0].strip()

                            for i in range(1, len(potential_splits), 2):
                                if i + 1 < len(potential_splits):
                                    if (
                                        current_sentence
                                        and not current_sentence.endswith(".")
                                    ):
                                        current_sentence += "."
                                    split_choices.append(current_sentence)
                                    current_sentence = potential_splits[i + 1].strip()

                            # เพิ่มประโยคสุดท้าย
                            if current_sentence:
                                if current_sentence and not current_sentence.endswith(
                                    "."
                                ):
                                    current_sentence += "."
                                split_choices.append(current_sentence)

                            # ตรวจสอบว่าผลลัพธ์สมเหตุสมผลหรือไม่
                            if len(split_choices) >= 2 and len(split_choices) <= 4:
                                self.logging_manager.log_info(
                                    f"_detect_choice_format: Split long choice into {len(split_choices)} parts: {split_choices}"
                                )
                                actual_choices.extend(split_choices)
                                continue

                    # หากไม่ได้แยก ให้เพิ่มเป็นตัวเลือกเดียว
                    actual_choices.append(
                        stripped_choice
                    )  # Keep original spacing within the choice line

            if actual_choices:
                # Heuristic: If we have a header and at least one plausible choice line.
                # For FFXIV, usually 2-4 choices. If many more, it might be misinterpretation.
                if (
                    len(actual_choices) > 0 and len(actual_choices) <= 5
                ):  # Accept 1 to 5 choices
                    self.logging_manager.log_info(
                        f"_detect_choice_format: Detected choice format. Header: '{detected_header_text.strip()}', Choices: {actual_choices}"
                    )
                    return True, detected_header_text.strip(), actual_choices
                else:
                    self.logging_manager.log_info(
                        f"_detect_choice_format: Header found ('{detected_header_text.strip()}'), but number of choices ({len(actual_choices)}) is unusual. Treating as non-choice."
                    )
                    return False, None, []  # Treat as non-choice if choice count is off
            else:
                self.logging_manager.log_info(
                    f"_detect_choice_format: Header-like string found ('{detected_header_text.strip()}'), but no valid choice lines followed."
                )
                return False, None, []  # No valid choices found after header

        self.logging_manager.log_info(
            "_detect_choice_format: No choice format detected based on headers."
        )
        return False, None, []

    # detect_choice_with_layout() method ถูกลบออกแล้ว (ไม่ใช้ PaddleOCR)

    def capture_and_ocr(self):
        """ฟังก์ชันจับภาพและแปลงเป็นข้อความด้วย OCR ที่มีการควบคุม CPU ใช้งาน - Optimized Version"""
        active_areas = (
            self.current_area.split("+")
            if isinstance(self.current_area, str)
            else [self.current_area]
        )
        results = []
        screen_changed_overall = False  # ติดตามว่ามีการเปลี่ยนแปลงในพื้นที่ใดพื้นที่หนึ่งหรือไม่

        self._update_status_line("OCR scanning...")

        if not hasattr(self, "last_signatures"):
            self.last_signatures = {}

        # ดึง role ของ preset ปัจจุบันเพื่อใช้ในการตัดสินใจเกี่ยวกับ is_potential_choice_area
        current_preset_num = self.settings.get("current_preset", 1)
        current_preset_role = self.settings.get_preset_role(current_preset_num)
        # แก้ไข log_debug เป็น log_info
        self.logging_manager.log_info(
            f"Current preset role for OCR config: {current_preset_role}"
        )

        # OPTIMIZATION: Single full-screen capture for all areas
        full_screen = self.get_full_screen_capture()
        if full_screen is None:
            self.logging_manager.log_error(
                "Failed to capture full screen, fallback to individual captures"
            )
            # Continue with old method as fallback

        for area in active_areas:
            # 🔍 DEBUG: แสดงการพิจารณาแต่ละ area
            self.logging_manager.log_info(
                f"[PRESET-CHOICE-DEBUG] Processing area '{area}' with preset role '{current_preset_role}'"
            )

            # ✨ CHOICE PRESET SPECIAL HANDLING: Skip Area A เมื่อใช้ choice preset
            if current_preset_role == "choice" and area == "A":
                self.logging_manager.log_info(
                    f"[PRESET-CHOICE-DEBUG] ✅ SKIPPING Area A for choice preset (as intended)"
                )
                continue

            translate_area = self.settings.get_translate_area(area)
            if not translate_area:
                self.logging_manager.log_warning(
                    f"No translate_area defined for area: {area}"
                )
                continue

            start_x = translate_area["start_x"]
            start_y = translate_area["start_y"]
            end_x = translate_area["end_x"]
            end_y = translate_area["end_y"]

            if start_x == end_x or start_y == end_y:
                self.logging_manager.log_warning(
                    f"Area {area} has zero size, skipping."
                )
                continue

            is_potential_choice_area = (current_preset_role == "choice") or (
                area == "B"
            )
            # แก้ไข log_debug เป็น log_info
            self.logging_manager.log_info(
                f"Area '{area}': is_potential_choice_area = {is_potential_choice_area} (Preset role: {current_preset_role})"
            )

            try:
                # OPTIMIZATION: Use optimized full-screen capture and cropping
                if full_screen is not None:
                    img = self.crop_area_from_full_screen(full_screen, translate_area)
                    if img is None:
                        self.logging_manager.log_warning(
                            f"Failed to crop area {area}, skipping."
                        )
                        continue
                else:
                    # Fallback to individual capture if full-screen failed
                    scale_x, scale_y = self.get_screen_scale()
                    x1 = int(min(start_x, end_x) * scale_x)
                    y1 = int(min(start_y, end_y) * scale_y)
                    x2 = int(max(start_x, end_x) * scale_x)
                    y2 = int(max(start_y, end_y) * scale_y)

                    if x1 >= x2 or y1 >= y2:
                        self.logging_manager.log_warning(
                            f"Invalid bbox for area {area}: ({x1},{y1},{x2},{y2}), skipping."
                        )
                        continue

                    img = ImageGrab.grab(bbox=(x1, y1, x2, y2))

                signature = self.get_image_signature(img)

                area_screen_changed = False
                if (
                    area not in self.last_signatures
                    or signature != self.last_signatures[area]
                ):
                    area_screen_changed = True
                    screen_changed_overall = True
                    self.last_signatures[area] = signature
                    # แก้ไข log_debug เป็น log_info
                    self.logging_manager.log_info(
                        f"Area '{area}': Image signature changed or new."
                    )
                else:
                    cached_result = self.get_cached_ocr_result(area, str(signature))
                    if cached_result:
                        results.append((area, cached_result))
                        # แก้ไข log_debug เป็น log_info
                        self.logging_manager.log_info(
                            f"Area '{area}': Used cached OCR result."
                        )
                        continue
                    else:
                        area_screen_changed = True
                        screen_changed_overall = True
                        # แก้ไข log_debug เป็น log_info
                        self.logging_manager.log_info(
                            f"Area '{area}': Signature same, but no valid cache. Re-OCR."
                        )

                if area_screen_changed:
                    img_processed = self.preprocess_image(img)

                    timestamp_ms = int(time.time() * 1000)
                    temp_path = os.path.join(
                        os.getcwd(), f"temp_screenshot_{area}_{timestamp_ms}.png"
                    )

                    try:
                        img_processed.save(temp_path)

                        ocr_params = self.smart_ocr_config(
                            is_potential_choice=is_potential_choice_area
                        )
                        # แก้ไข log_debug เป็น log_info
                        self.logging_manager.log_info(
                            f"Area '{area}': OCRing with params: {ocr_params}"
                        )

                        if self.reader is None:
                            self.logging_manager.log_warning(
                                f"Area '{area}': OCR not available - skipping"
                            )
                            return ""

                        ocr_output_list = self.reader.readtext(temp_path, **ocr_params)

                        text = ""
                        if ocr_params["detail"] == 1:
                            # สำหรับ choice areas ใช้ _group_into_lines_easyocr() เพื่อรักษาการแยกบรรทัด
                            if is_potential_choice_area:
                                # ใช้ _group_into_lines_easyocr() เพื่อจัดกลุ่มเป็นบรรทัด (รองรับ EasyOCR format)
                                lines = self._group_into_lines_easyocr(ocr_output_list)
                                text = "\n".join(lines) if lines else ""
                                self.logging_manager.log_info(
                                    f"Area '{area}' (choice area) grouped into {len(lines)} lines: {lines}"
                                )
                            else:
                                # สำหรับ normal areas ใช้วิธีเดิม
                                text = " ".join(
                                    [item[1] for item in ocr_output_list if item[1]]
                                )
                                self.logging_manager.log_info(
                                    f"Area '{area}' (normal area) OCR raw texts: {[item[1] for item in ocr_output_list]}"
                                )
                        else:
                            text = " ".join(ocr_output_list).strip()
                            # แก้ไข log_debug เป็น log_info
                            self.logging_manager.log_info(
                                f"Area '{area}' (detail=0) OCR raw texts: {ocr_output_list}"
                            )

                        if text:
                            self.cache_ocr_result(area, str(signature), text)
                            results.append((area, text))
                            self.logging_manager.log_info(
                                f"Area '{area}' OCR successful, text: {text[:50]}..."
                            )
                        else:
                            self.logging_manager.log_info(
                                f"Area '{area}' OCR: No text detected."
                            )
                            self.cache_ocr_result(area, str(signature), "")
                            results.append((area, ""))

                        cpu_limit = self.settings.get("cpu_limit", 80)
                        if cpu_limit <= 50:
                            time.sleep(0.3)
                        elif cpu_limit <= 60:
                            time.sleep(0.2)
                        elif cpu_limit <= 80:
                            time.sleep(0.1)

                    except Exception as ocr_err:
                        self.logging_manager.log_error(
                            f"Error during OCR for area {area} on {temp_path}: {ocr_err}"
                        )
                    finally:
                        try:
                            if os.path.exists(temp_path):
                                os.remove(temp_path)
                        except Exception as e_remove:
                            self.logging_manager.log_warning(
                                f"Could not remove temp file {temp_path}: {e_remove}"
                            )

            except Exception as e:
                self._update_status_line(f"Error in area {area}: {str(e)}")
                self.logging_manager.log_error(f"Error processing area {area}: {e}")

                self.logging_manager.log_error(traceback.format_exc())
                continue

        if not screen_changed_overall and not results:
            # แก้ไข log_debug เป็น log_info
            self.logging_manager.log_info(
                "No screen changes and no cached results to return for any active area."
            )

        return results

    def get_image_signature(self, image, enhanced=False):
        """สร้าง signature จากภาพเพื่อใช้ในการเปรียบเทียบความเหมือน

        Args:
            image (PIL.Image): ภาพที่ต้องการสร้าง signature
            enhanced (bool): ใช้ enhanced signature algorithm หรือไม่

        Returns:
            tuple: signature ของภาพในรูปแบบ tuple
        """
        if enhanced:
            return self.get_enhanced_image_signature(image)
        try:
            # แปลงเป็น grayscale และลดขนาด
            gray = np.array(image.convert("L"))

            # ลดขนาดภาพให้เล็กลงเพื่อเพิ่มประสิทธิภาพในการเปรียบเทียบ
            # ขนาด 32x32 เพียงพอสำหรับตรวจจับความเปลี่ยนแปลงของข้อความ
            h, w = gray.shape
            if w > 32 or h > 32:
                aspect_ratio = w / h
                if aspect_ratio > 1:
                    new_w, new_h = 32, int(32 / aspect_ratio)
                else:
                    new_w, new_h = int(32 * aspect_ratio), 32

                # ต้องไม่น้อยกว่า 8 พิกเซล
                new_w = max(8, new_w)
                new_h = max(8, new_h)

                resized = cv2.resize(gray, (new_w, new_h))
            else:
                resized = gray

            # สร้าง signature แบบง่าย - แบ่งภาพเป็นบล็อกและหาค่าเฉลี่ยแต่ละบล็อก
            block_size = 4  # ขนาดบล็อกที่ใช้ในการสร้าง signature
            signature = []

            h, w = resized.shape
            for i in range(0, h, block_size):
                if i + block_size > h:
                    continue
                for j in range(0, w, block_size):
                    if j + block_size > w:
                        continue
                    block = resized[i : i + block_size, j : j + block_size]
                    signature.append(np.mean(block))

            # แปลงเป็น tuple เพื่อให้ใช้เป็น hash key ได้
            return tuple(signature)

        except Exception as e:
            self.logging_manager.log_error(f"Error creating image signature: {e}")
            # สร้าง signature แบบง่ายกว่าในกรณีที่เกิดข้อผิดพลาด
            return tuple([hash(str(image.tobytes()))])

    def capture_and_ocr_all_areas(self):
        """ทำ OCR ทุกพื้นที่ (A, B, และ C) ในคราวเดียว เพื่อใช้ในการตรวจสอบประเภทข้อความ - Optimized Version"""
        results = {}

        # OPTIMIZATION: Single full-screen capture for all areas
        full_screen = self.get_full_screen_capture()
        if full_screen is None:
            self.logging_manager.log_error(
                "Failed to capture full screen in capture_and_ocr_all_areas, fallback to individual captures"
            )

        # ลูปทำ OCR ทั้ง 3 พื้นที่
        for area in ["A", "B", "C"]:
            translate_area = self.settings.get_translate_area(area)
            if not translate_area:
                continue

            start_x = translate_area["start_x"]
            start_y = translate_area["start_y"]
            end_x = translate_area["end_x"]
            end_y = translate_area["end_y"]

            # ตรวจสอบพื้นที่ว่าง
            if start_x == end_x or start_y == end_y:
                continue

            try:
                # OPTIMIZATION: Use optimized full-screen capture and cropping
                if full_screen is not None:
                    img = self.crop_area_from_full_screen(full_screen, translate_area)
                    if img is None:
                        continue
                else:
                    # Fallback to individual capture if full-screen failed
                    scale_x, scale_y = self.get_screen_scale()
                    x1 = int(min(start_x, end_x) * scale_x)
                    y1 = int(min(start_y, end_y) * scale_y)
                    x2 = int(max(start_x, end_x) * scale_x)
                    y2 = int(max(start_y, end_y) * scale_y)
                    img = ImageGrab.grab(bbox=(x1, y1, x2, y2))

                # สร้าง hash ของภาพอย่างง่าย
                img_array = np.array(img)
                img_hash = hash(img_array.tobytes())

                # ตรวจสอบแคช
                cached_result = self.get_cached_ocr_result(area, img_hash)
                if cached_result:
                    results[area] = cached_result
                    continue

                # ทำ OCR
                img = self.preprocess_image(img)

                # บันทึกภาพชั่วคราว
                temp_path = f"temp_screenshot_{area}_{int(time.time()*1000)}.png"
                try:
                    # บันทึกและอ่านข้อความจากภาพ
                    img.save(temp_path)

                    # ปรับระดับความมั่นใจ OCR ตามความเร็ว
                    confidence = 0.6 if self.ocr_speed == "high" else 0.7
                    if self.reader is None:
                        self.logging_manager.log_warning(
                            "OCR not available for text detection"
                        )
                        return ""

                    result = self.reader.readtext(
                        temp_path,
                        detail=0,
                        paragraph=True,
                        min_size=3,
                        text_threshold=confidence,
                    )

                    text = " ".join(result)

                    # เพิ่มผลลัพธ์ถ้ามีข้อความ
                    if text:
                        self.cache_ocr_result(area, img_hash, text)
                        results[area] = text

                finally:
                    # ทำความสะอาดไฟล์ชั่วคราว
                    try:
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
                    except Exception as e:
                        self.logging_manager.log_warning(
                            f"Could not remove temp file {temp_path}: {e}"
                        )

            except Exception as e:
                self._update_status_line(f"Error in OCR area {area}: {str(e)}")
                continue

        return results

    def check_for_background_dialogue(self):
        """
        ตรวจสอบพื้นที่ในเบื้องหลังว่ามีบทสนทนาปกติหรือข้อความตัวเลือกหรือไม่ - Optimized Version
        เหมาะสำหรับใช้เมื่ออยู่ในพื้นที่ C และต้องการตรวจสอบว่ามีข้อความในพื้นที่ A+B หรือไม่

        Returns:
            str: ประเภทข้อความที่พบ หรือ None ถ้าไม่พบข้อความที่เปลี่ยนไป
        """
        # ถ้าไม่ได้อยู่ในพื้นที่ C ไม่จำเป็นต้องตรวจสอบพื้นหลัง
        current_areas = (
            self.current_area.split("+")
            if isinstance(self.current_area, str)
            else self.current_area
        )
        if set(current_areas) != set(["C"]):
            return None

        self._update_status_line("Checking background for dialogue text...")
        self.logging_manager.log_info(
            "Checking background for dialogue while in area C"
        )

        # OPTIMIZATION: Single full-screen capture for all background areas
        full_screen = self.get_full_screen_capture()
        if full_screen is None:
            self.logging_manager.log_error(
                "Failed to capture full screen in check_for_background_dialogue, fallback to individual captures"
            )

        # ทำ OCR พื้นที่ A และ B เพื่อตรวจสอบว่ามีข้อความสนทนาปกติหรือไม่
        background_texts = {}

        # ให้ความสำคัญสูงกับการตรวจสอบพื้นที่ B ก่อน (เพื่อหา choice dialogue)
        # ตรวจสอบพื้นที่ B ก่อนเสมอเพื่อความรวดเร็ว
        priority_areas = ["B", "A"]

        for area in priority_areas:
            translate_area = self.settings.get_translate_area(area)
            if not translate_area:
                continue

            start_x = translate_area["start_x"]
            start_y = translate_area["start_y"]
            end_x = translate_area["end_x"]
            end_y = translate_area["end_y"]

            # ตรวจสอบพื้นที่ว่าง
            if start_x == end_x or start_y == end_y:
                continue

            try:
                # OPTIMIZATION: Use optimized full-screen capture and cropping
                if full_screen is not None:
                    img = self.crop_area_from_full_screen(full_screen, translate_area)
                    if img is None:
                        continue
                else:
                    # Fallback to individual capture if full-screen failed
                    scale_x, scale_y = self.get_screen_scale()
                    x1 = int(min(start_x, end_x) * scale_x)
                    y1 = int(min(start_y, end_y) * scale_y)
                    x2 = int(max(start_x, end_x) * scale_x)
                    y2 = int(max(start_y, end_y) * scale_y)
                    img = ImageGrab.grab(bbox=(x1, y1, x2, y2))

                # ทำ OCR แบบรวดเร็ว (ใช้ความเร็วสูง)
                img = self.preprocess_image(img)

                # บันทึกภาพชั่วคราว
                temp_path = f"temp_background_{area}_{int(time.time()*1000)}.png"
                try:
                    img.save(temp_path)
                    # ใช้ค่าความเชื่อมั่นต่ำลงและความเร็วสูงสำหรับการตรวจสอบเบื้องหลัง
                    if self.reader is None:
                        self.logging_manager.log_warning(
                            "OCR not available for text detection"
                        )
                        return ""

                    result = self.reader.readtext(
                        temp_path,
                        detail=0,
                        paragraph=True,
                        min_size=3,
                        text_threshold=0.5,  # ค่าต่ำกว่าปกติเพื่อให้ตรวจจับได้มากขึ้น
                    )

                    text = " ".join(result)
                    if text:
                        background_texts[area] = text

                        # ตรวจสอบ choice dialogue ทันทีสำหรับพื้นที่ B
                        if area == "B":
                            # ให้ความสำคัญกับการตรวจหา "What will you say?"
                            if (
                                "what will you say" in text.lower()
                                or "whatwill you say" in text.lower()
                                or "what willyou say" in text.lower()
                            ):
                                self.logging_manager.log_info(
                                    f"Found choice dialogue in background area B: '{text[:30]}...'"
                                )
                                return (
                                    "choice"  # พบ choice dialogue ในพื้นหลัง - สลับพื้นที่ทันที
                                )
                finally:
                    # ทำความสะอาดไฟล์ชั่วคราว
                    try:
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
                    except Exception as e:
                        self.logging_manager.log_warning(
                            f"Could not remove temp file {temp_path}: {e}"
                        )
            except Exception as e:
                self._update_status_line(
                    f"Error in background check area {area}: {str(e)}"
                )
                continue

        # ตรวจสอบว่าพบบทสนทนาทั้งในพื้นที่ A และ B หรือไม่
        if "A" in background_texts and "B" in background_texts:
            name_text = background_texts["A"].strip()
            dialogue_text = background_texts["B"].strip()

            # ตรวจสอบว่าพื้นที่ A มีชื่อตัวละครจริงๆ หรือไม่
            if name_text and len(name_text) < 25:  # ชื่อตัวละครมักสั้นกว่า 25 ตัวอักษร
                self.logging_manager.log_info(
                    f"Found character name '{name_text}' in background area A"
                )

                # ตรวจสอบว่าพื้นที่ B มีข้อความบทสนทนาจริงๆ หรือไม่
                if dialogue_text and len(dialogue_text) > 5:  # บทสนทนามักยาวกว่า 5 ตัวอักษร
                    self.logging_manager.log_info(
                        f"Found dialogue text in background area B: '{dialogue_text[:30]}...'"
                    )
                    return "normal"  # พบบทสนทนาปกติในพื้นหลัง

        # ตรวจสอบเพิ่มเติมว่าพบข้อความตัวเลือกในพื้นที่ B หรือไม่
        if "B" in background_texts:
            b_text = background_texts["B"]

            # ใช้ฟังก์ชันเต็มรูปแบบในการตรวจสอบอีกครั้ง
            if self.is_choice_dialogue(b_text):
                self.logging_manager.log_info(
                    "Found choice dialogue in background area B"
                )
                return "choice"

        return None  # ไม่พบรูปแบบข้อความที่ต้องการในพื้นหลัง

    def _is_choice_dialogue_quick_check(self, text):
        """ตรวจสอบอย่างรวดเร็วว่าเป็น choice dialogue หรือไม่
        ใช้เฉพาะกับการตรวจสอบพื้นหลังเพื่อความรวดเร็ว

        Args:
            text (str): ข้อความที่ต้องการตรวจสอบ
        Returns:
            bool: True ถ้าเป็น choice dialogue
        """
        # ทำความสะอาดข้อความก่อนตรวจสอบ
        cleaned_text = text.strip().lower()

        # รูปแบบที่พบบ่อยในข้อความตัวเลือก - เน้นรูปแบบที่มักพบในเกม
        choice_patterns = [
            "what will you say?",
            "what will you say",
            "whatwill you say",
            "what willyou say",
            "what will yousay",
            "whatwillyou say",
        ]

        # ตรวจสอบอย่างรวดเร็วเฉพาะรูปแบบหลักๆ
        for pattern in choice_patterns:
            if pattern in cleaned_text:
                self._update_status_line(
                    f"Quick check: Choice dialogue detected: {pattern}"
                )
                return True

            return False

    def detect_dialogue_type_improved(self, texts):
        """วิเคราะห์ประเภทของข้อความจากผลลัพธ์ OCR ด้วยความแม่นยำสูงขึ้น

        Args:
            texts: dict ของพื้นที่และข้อความที่ได้จาก OCR

        Returns:
            str: ประเภทข้อความ ("normal", "narrator", "choice" ฯลฯ)
        """
        # ถ้าไม่มีข้อความ
        if not texts:
            return "unknown"

        # 1. ตรวจสอบบทสนทนาปกติ (normal dialogue) - มีทั้งชื่อและข้อความ (ให้ priority สูงสุด)
        if "A" in texts and "B" in texts and texts["A"] and texts["B"]:
            name_text = texts["A"].strip()
            dialogue_text = texts["B"].strip()

            # ชื่อตัวละครมักสั้น (ไม่เกิน 25 ตัวอักษร) และไม่ใช่ตัวเลขหรือเครื่องหมาย
            if (
                name_text
                and len(name_text) < 25
                and any(c.isalpha() for c in name_text)
            ):
                # ตรวจสอบว่าชื่อมีความยาวมากกว่า 1 ตัวอักษร
                if len(name_text) > 1:
                    # ตรวจสอบเพิ่มเติมว่าข้อความใน B มีลักษณะของบทสนทนา
                    if len(dialogue_text) > 3:  # ข้อความต้องมีความยาวพอสมควร
                        self.logging_manager.log_info(
                            f"Detected normal dialogue (A+B): '{name_text}: {dialogue_text[:30]}...'"
                        )
                        return "normal"

        # 2. ตรวจสอบ choice dialogue (ตัวเลือก) - ต้องตรวจสอบหลังจากบทสนทนาปกติ
        if "B" in texts and texts["B"]:
            if self.is_choice_dialogue(texts["B"]):
                self.logging_manager.log_info("Detected choice dialogue in area B")
                return "choice"

        # 3. ตรวจสอบกรณีพิเศษ - มีเฉพาะข้อความในพื้นที่ B
        if "B" in texts and texts["B"] and (not "A" in texts or not texts["A"]):
            b_text = texts["B"]

            # ตรวจสอบว่ามีชื่อคนพูดในข้อความหรือไม่
            speaker, content, _ = self.text_corrector.split_speaker_and_content(b_text)
            if speaker:
                self.logging_manager.log_info(
                    f"Detected dialogue with speaker in text: '{speaker}'"
                )
                return "speaker_in_text"
            else:
                # กรณีพิเศษ - อาจเป็นบทสนทนาต่อเนื่องจากคนเดิม
                # ตรวจสอบว่าข้อความมีลักษณะของบทสนทนาหรือไม่
                if ('"' in b_text or "'" in b_text) and len(b_text) > 5:
                    self.logging_manager.log_info(
                        f"Detected dialogue without name: '{b_text[:30]}...'"
                    )
                    return "dialog_without_name"

        # 4. ตรวจสอบบทบรรยาย (narrator text) ในพื้นที่ C
        # ต้องตรวจสอบเป็นอันดับสุดท้าย เพื่อลดความผิดพลาดในการตรวจจับ
        if "C" in texts and texts["C"]:
            narrator_text = texts["C"]
            # ถ้าข้อความไม่มีชื่อคน และมีความยาวพอสมควร น่าจะเป็นบทบรรยาย
            speaker, content, _ = self.text_corrector.split_speaker_and_content(
                narrator_text
            )

            # ต้องเป็นข้อความที่ยาวพอสมควร และไม่มีชื่อนำหน้า
            if not speaker and len(narrator_text) > 20:  # เพิ่มความยาวขั้นต่ำจาก 15 เป็น 20
                # เพิ่มการตรวจสอบลักษณะของบทบรรยาย
                # บทบรรยายมักไม่มีเครื่องหมายคำพูดในช่วงต้น และมักมีคำบรรยาย
                if '"' not in narrator_text[:15] and "'" not in narrator_text[:15]:
                    # ตรวจสอบคำที่พบบ่อยในบทบรรยาย
                    narrator_words = [
                        "the",
                        "a",
                        "an",
                        "there",
                        "it",
                        "they",
                        "you",
                        "your",
                        "this",
                        "that",
                        "he",
                        "she",
                        "his",
                        "her",
                        "their",
                        "its",
                        "our",
                        "we",
                        "I",
                        "my",
                        "me",
                        "when",
                        "as",
                        "if",
                        "then",
                        "while",
                        "after",
                        "before",
                    ]
                    word_count = sum(
                        1
                        for word in narrator_words
                        if f" {word} " in f" {narrator_text.lower()} "
                    )

                    # ต้องมีคำบรรยายอย่างน้อย 2 คำ (เพิ่มความเข้มงวด)
                    if word_count >= 2:
                        self.logging_manager.log_info(
                            f"Detected narrator text in area C: '{narrator_text[:30]}...'"
                        )
                        return "narrator"

        # 5. กรณีที่ไม่สามารถระบุได้
        return "unknown"

    def smart_switch_area(self):
        """
        สลับพื้นที่อัตโนมัติ (เพิ่มการตรวจสอบ Grace Period และเช็คการเปิดใช้งานฟีเจอร์)
        """
        # ตรวจสอบว่าฟีเจอร์นี้เปิดใช้งานหรือไม่
        if not self.feature_manager.is_feature_enabled("smart_area_switching"):
            logging.debug("Smart area switching feature is disabled in this version")
            return False

        # 1. ตรวจสอบว่าเปิดใช้งาน Auto Switch หรือไม่
        if not self.settings.get(
            "enable_auto_area_switch", False
        ):  # ค่า default เป็น False
            # self._update_status_line("Auto switch disabled") # อาจจะไม่ต้องแสดงบ่อย
            logging.debug("Auto area switching is disabled.")
            return False

        # 2. --- เพิ่ม: ตรวจสอบ Grace Period หลังจาก Manual Switch ---
        manual_selection_grace_period = 15  # วินาที
        last_manual_time = self.settings.get("last_manual_preset_selection_time", 0)
        current_time_for_check = time.time()  # ใช้เวลาเดียวกันตลอดการตรวจสอบ

        if current_time_for_check - last_manual_time < manual_selection_grace_period:
            time_left = manual_selection_grace_period - (
                current_time_for_check - last_manual_time
            )
            logging.info(
                f"Manual preset selection grace period active ({time_left:.1f}s left). Skipping auto-switch."
            )
            return False  # ข้าม Auto-Switch
        # --- จบการตรวจสอบ Grace Period ---

        # 3. ตรวจสอบ Cooldown ของ Auto Switch เอง (ป้องกันการสลับถี่เกินไป)
        if not hasattr(self, "_last_auto_switch_time"):
            self._last_auto_switch_time = 0
        auto_switch_cooldown_duration = 3.0
        if (
            current_time_for_check - self._last_auto_switch_time
            < auto_switch_cooldown_duration
        ):
            logging.debug(f"Auto-switch cooldown active.")
            return False

        # 4. ตรวจสอบพื้นที่ปัจจุบัน
        current_areas = (
            self.current_area.split("+")
            if isinstance(self.current_area, str)
            else self.current_area
        )
        current_areas_set = set(current_areas)

        # 5. ตรวจสอบพื้นหลังถ้าอยู่ในโหมด Lore (Area C)
        if current_areas_set == set(["C"]):
            background_type = self.check_for_background_dialogue()
            if background_type in ["normal", "choice"]:
                target_preset = self.find_appropriate_preset(background_type) or 1
                preset_data = self.settings.get_preset(target_preset)
                target_area_string = (
                    preset_data.get("areas", "A+B") if preset_data else "A+B"
                )

                # ตรวจสอบว่าต้องสลับจริงหรือไม่
                if (
                    self.current_area == target_area_string
                    and self.settings.get("current_preset") == target_preset
                ):
                    logging.debug("Already in correct state for background dialogue.")
                    return False

                self._update_status_line(
                    f"✓ BG {background_type}, switching to P{target_preset}"
                )
                logging.info(
                    f"Auto switching from C to P{target_preset} ({target_area_string}) due to background {background_type}"
                )
                # เรียก switch_area พร้อม preset override
                # แก้ไขตรงนี้: เพิ่ม source="auto_switch" เพื่อระบุแหล่งที่มาของการเปลี่ยนแปลง
                switched = self.switch_area(
                    target_area_string,
                    preset_number_override=target_preset,
                    source="auto_switch",
                )
                if switched:
                    self._last_auto_switch_time = time.time()  # บันทึกเวลา auto switch
                    self.force_next_translation = True  # บังคับแปลหลังสลับ
                    return True
                else:
                    return False  # ถ้า switch_area ไม่ทำงาน

        # 6. ทำ OCR ทุกพื้นที่เพื่อวิเคราะห์ประเภท
        all_texts = self.capture_and_ocr_all_areas()
        if not all_texts:
            logging.debug("Smart Switch: No text detected.")
            return False

        # 7. วิเคราะห์ประเภทข้อความ
        dialogue_type = self.detect_dialogue_type_improved(all_texts)
        logging.info(f"Detected dialogue type: {dialogue_type}")

        # 8. ตรวจสอบความเสถียร
        self.update_detection_history(dialogue_type)
        stability_info = self.area_detection_stability_system()
        logging.debug(f"Stability check: {stability_info}")

        required_consecutive = (
            3 if dialogue_type == "narrator" and current_areas_set == {"A", "B"} else 2
        )
        min_confidence = 75

        if (
            not stability_info["is_stable"]
            or stability_info["stable_type"] != dialogue_type
            or stability_info["confidence"].get(dialogue_type, 0) < min_confidence
            or stability_info["consecutive_detections"] < required_consecutive
        ):
            logging.debug(f"Waiting for stable detection of {dialogue_type}...")
            return False  # ยังไม่เสถียรพอ

        # 9. ค้นหา Preset ที่เหมาะสมและสลับพื้นที่
        if dialogue_type != "unknown":
            target_preset = self.find_appropriate_preset(dialogue_type)
            if target_preset is None:
                logging.warning(f"No appropriate preset found for {dialogue_type}.")
                return False

            preset_data = self.settings.get_preset(target_preset)
            target_area_string = (
                preset_data.get("areas", "A+B") if preset_data else "A+B"
            )
            current_preset_num = self.settings.get("current_preset", 1)

            # ตรวจสอบว่าต้องสลับจริงหรือไม่ (Preset และ Area ต้องตรงกัน)
            if (
                current_preset_num == target_preset
                and self.current_area == target_area_string
            ):
                logging.debug(f"Already in correct preset/area for {dialogue_type}.")
                return False

            # --- ทำการสลับ ---
            self._update_status_line(
                f"✓ Auto switching to P{target_preset} for {dialogue_type}"
            )
            logging.info(
                f"Auto switching preset: P{current_preset_num} -> P{target_preset} ({target_area_string}) for type: {dialogue_type}"
            )
            # แก้ไขตรงนี้: เพิ่ม source="auto_switch" เพื่อระบุแหล่งที่มาของการเปลี่ยนแปลง
            switched = self.switch_area(
                target_area_string,
                preset_number_override=target_preset,
                source="auto_switch",
            )
            if switched:
                self._last_auto_switch_time = time.time()  # บันทึกเวลา auto switch
                return True
            else:
                return False  # ถ้า switch_area ไม่ทำงาน

        return False  # ถ้าไม่เข้าเงื่อนไขใดๆ

    def is_choice_dialogue(self, text):
        """ตรวจสอบว่าเป็น choice dialogue หรือไม่ - Enhanced version for FFXIV"""
        # ทำความสะอาดข้อความก่อนตรวจสอบ
        cleaned_text = text.strip().lower()

        # เพิ่มการตรวจสอบแบบ fuzzy matching
        cleaned_text_no_space = cleaned_text.replace(" ", "")

        # Log ข้อความที่กำลังตรวจสอบ
        self.logging_manager.log_info(f"Checking for choice dialogue: '{text[:50]}...'")
        self.logging_manager.log_info(f"Cleaned text: '{cleaned_text[:50]}...'")

        # Enhanced patterns for FFXIV choice dialogues
        choice_patterns = [
            # Standard FFXIV patterns
            "what will you say?",
            "what will you say",
            "whatwill you say?",
            "what willyou say?",
            "what will yousay?",
            "whatwillyou say?",
            "whatwillyousay?",
            # Additional common choice headers
            "choose your response",
            "select an option",
            "pick your answer",
            "what do you say",
            "how will you respond",
            "your response:",
            "your answer:",
        ]

        # ตรวจสอบแบบ exact match ก่อน
        for pattern in choice_patterns:
            # ตรวจสอบคำขึ้นต้น
            if cleaned_text.startswith(pattern):
                self._update_status_line(
                    f"Choice dialogue detected (exact match): {pattern}"
                )
                self.logging_manager.log_info(
                    f"Choice detected - exact match: {pattern}"
                )
                return True

            # ตรวจสอบในส่วนต้นของข้อความ (ภายใน 50 ตัวอักษรแรก - เพิ่มจาก 30)
            if pattern in cleaned_text[:50]:
                self._update_status_line(
                    f"Choice dialogue detected near beginning: {pattern}"
                )
                self.logging_manager.log_info(
                    f"Choice detected - near beginning: {pattern}"
                )
                return True

        # ตรวจสอบแบบ fuzzy matching สำหรับกรณี OCR อาจผิดพลาด
        if "whatwillyousay" in cleaned_text_no_space[:50]:
            self._update_status_line(
                "Choice dialogue detected (fuzzy match without spaces)"
            )
            self.logging_manager.log_info(
                "Choice detected - fuzzy match without spaces"
            )
            return True

        # เพิ่มการตรวจสอบแบบมีช่องว่างผิดที่

        # ตรวจจับ OCR errors ที่พบบ่อย
        ocr_error_patterns = [
            r"what\s*wil+\s*you\s*say",  # "what will you say" พร้อม OCR errors
            r"contestisn'?t\s*over\s*yet",  # "contest isn't over yet" รวมกัน
            r"won'?tlet",  # "won't let" รวมกัน
            r"take\s*back\s*what\s*was\s*stolen",  # รูปแบบ choice ที่พบใน logs
        ]

        for pattern in ocr_error_patterns:
            if re.search(pattern, cleaned_text, re.IGNORECASE):
                self._update_status_line(
                    f"Choice dialogue detected (OCR error pattern): {pattern}"
                )
                self.logging_manager.log_info(
                    f"Choice detected - OCR error pattern: {pattern}"
                )
                return True

        # ตรวจสอบการมีอยู่ของคำสำคัญที่บ่งบอกถึง choice dialogue หลายคำในประโยคเดียว
        choice_keywords = ["contest", "take back", "stolen", "won't let", "get away"]
        keyword_count = sum(1 for keyword in choice_keywords if keyword in cleaned_text)

        if keyword_count >= 3:  # ถ้าพบคำสำคัญ 3 คำขึ้นไป น่าจะเป็น choice
            self._update_status_line(
                f"Choice dialogue detected (multiple keywords): {keyword_count} matches"
            )
            self.logging_manager.log_info(
                f"Choice detected - multiple keywords: {keyword_count} matches"
            )
            return True
        # ลบช่องว่างที่ซ้ำกันและทำให้เป็นช่องว่างเดียว
        normalized_text = re.sub(r"\s+", " ", cleaned_text)
        if "what will you say" in normalized_text[:50]:
            self._update_status_line("Choice dialogue detected (normalized spaces)")
            self.logging_manager.log_info("Choice detected - normalized spaces")
            return True

        # ตรวจสอบแบบมีตัวอักษรแทรกระหว่างคำ (OCR error)
        fuzzy_pattern = re.sub(r"\s+", r".{0,2}", "what will you say")
        if re.search(fuzzy_pattern, cleaned_text[:50]):
            self._update_status_line("Choice dialogue detected (fuzzy regex)")
            self.logging_manager.log_info("Choice detected - fuzzy regex")
            return True

        # Enhanced detection for numbered/bulleted choices without headers
        lines = text.strip().split('\n')
        if 2 <= len(lines) <= 5:  # Typical choice count
            numbered_pattern = r'^[1-9][.)]\s*'
            bulleted_pattern = r'^[►▶•◆▪▫⚫⚪→]\s*'
            
            numbered_count = 0
            bulleted_count = 0
            
            for line in lines:
                line_stripped = line.strip()
                if re.match(numbered_pattern, line_stripped):
                    numbered_count += 1
                elif re.match(bulleted_pattern, line_stripped):
                    bulleted_count += 1
            
            # If most lines are numbered or bulleted, it's likely a choice
            if numbered_count >= 2 or bulleted_count >= 2:
                self._update_status_line(
                    f"Choice dialogue detected (numbered/bulleted format): {numbered_count} numbered, {bulleted_count} bulleted"
                )
                self.logging_manager.log_info(
                    f"Choice detected - numbered/bulleted format: {numbered_count} numbered, {bulleted_count} bulleted lines"
                )
                return True
            
            # Additional heuristic: if all lines are short and similar length
            if all(10 <= len(line.strip()) <= 60 for line in lines):
                line_lengths = [len(line.strip()) for line in lines]
                avg_length = sum(line_lengths) / len(line_lengths)
                length_variance = sum((l - avg_length) ** 2 for l in line_lengths) / len(line_lengths)
                
                # Low variance in line lengths often indicates choices
                if length_variance < 200:  # Threshold for similarity
                    self._update_status_line(
                        f"Choice dialogue detected (uniform short lines): {len(lines)} lines, avg length {avg_length:.1f}"
                    )
                    self.logging_manager.log_info(
                        f"Choice detected - uniform short lines: {len(lines)} lines, avg length {avg_length:.1f}, variance {length_variance:.1f}"
                    )
                    return True

        # Log เมื่อไม่พบ choice
        self.logging_manager.log_info(
            f"No choice pattern found in: '{cleaned_text[:50]}...'"
        )

        return False

    def toggle_translation(self):
        try:
            if not self.is_translating:
                # ตรวจสอบและรอ thread เดิมให้จบก่อน
                if self.translation_thread and self.translation_thread.is_alive():
                    self.translation_thread.join(timeout=1)

                if not self.is_resizing:
                    # ตรวจสอบพื้นที่ที่เปิดใช้งาน
                    active_areas = (
                        self.current_area.split("+")
                        if isinstance(self.current_area, str)
                        else [self.current_area]
                    )
                    valid_areas = True

                    for area in active_areas:
                        translate_area = self.settings.get_translate_area(area)
                        if not translate_area:
                            valid_areas = False
                            break
                        start_x = translate_area["start_x"]
                        start_y = translate_area["start_y"]
                        end_x = translate_area["end_x"]
                        end_y = translate_area["end_y"]
                        if start_x == end_x or start_y == end_y:
                            valid_areas = False
                            break

                    if not valid_areas:
                        messagebox.showwarning(
                            "Warning",
                            f"Please select translation areas for all active areas: {', '.join(active_areas)}",
                        )
                        return

                    # เริ่มการแปล
                    self.is_translating = True
                    self.translation_event.set()

                    # แก้ไขตรงนี้: ใช้ config แทน update_button สำหรับ Button ธรรมดา
                    self.start_stop_button.config(text="STOP")

                    # เพิ่มการไฮไลท์ปุ่มเมื่อเริ่มการแปล
                    self.update_button_highlight(self.start_stop_button, True)
                    self.blinking = True
                    self.blink_label.after(self.blink_interval, self.blink)

                    # แสดง UI
                    self.translated_ui_window.deiconify()
                    # อัพเดทสถานะปุ่ม TUI เป็นเปิด
                    self.update_bottom_button_state("tui", True)

                    # เริ่ม translation thread
                    self.translation_thread = threading.Thread(
                        target=self.translation_loop,
                        daemon=True,
                        name="TranslationThread",
                    )
                    self.translation_thread.start()
                    self.logging_manager.log_info("Translation thread started")
                else:
                    return
            else:
                self.stop_translation()
                # เพิ่มการยกเลิกไฮไลท์ปุ่มเมื่อหยุดการแปล
                self.update_button_highlight(self.start_stop_button, False)
                self.translation_event.clear()
                if self.translation_thread:
                    self.translation_thread.join(timeout=2)
                self.is_translating = False

            self.mini_ui.update_translation_status(self.is_translating)

        except Exception as e:
            self.logging_manager.log_error(
                f"An error occurred in toggle_translation: {e}"
            )
            messagebox.showerror("Error", f"An error occurred: {e}")
            self.is_translating = False
            self.mini_ui.update_translation_status(False)
            # กรณีเกิดข้อผิดพลาด ยกเลิกไฮไลท์ปุ่ม
            self.update_button_highlight(self.start_stop_button, False)

    def stop_translation(self):
        """หยุดการแปล"""
        if self.is_translating:
            try:
                # ล็อคการเคลื่อนย้าย UI ก่อนเริ่มการทำงานหนัก
                self.lock_ui_movement()

                # ตั้งค่าสถานะการแปล
                self.is_translating = False
                self.translation_event.clear()
                self.start_stop_button.config(text="START")
                self.blinking = False
                self.mini_ui.update_translation_status(False)

                # หยุดไฟกระพริบ
                if hasattr(self, "breathing_effect"):
                    self.breathing_effect.stop()
                # รีเซ็ตไปใช้ไอคอนสีดำ
                self.blink_label.config(image=self.black_icon)

                # 🔧 [FIX] ซ่อน translated UI เมื่อหยุดแปล
                if (
                    hasattr(self, "translated_ui_window")
                    and self.translated_ui_window.winfo_exists()
                ):
                    self.translated_ui_window.withdraw()
                    # อัพเดทสถานะปุ่ม TUI เป็นปิด
                    self.update_bottom_button_state("tui", False)
                    self.logging_manager.log_info(
                        "TUI hidden on stop_translation - TUI button state updated"
                    )

                # แสดงสถิติ speaker (สำหรับ debug)
                if hasattr(self, "get_speaker_statistics"):
                    stats = self.get_speaker_statistics()
                    if stats["total_dialogues"] > 0:
                        self.logging_manager.log_info(f"=== Speaker Statistics ===")
                        self.logging_manager.log_info(
                            f"Total speakers: {stats['total_speakers']}"
                        )
                        self.logging_manager.log_info(
                            f"Total dialogues: {stats['total_dialogues']}"
                        )
                        if stats["most_frequent"]:
                            self.logging_manager.log_info(
                                f"Most frequent: '{stats['most_frequent'][0]}' ({stats['most_frequent'][1]} times)"
                            )

                        # แสดง top 5
                        self.logging_manager.log_info("Top 5 speakers:")
                        for i, (name, count) in enumerate(
                            stats["frequency_list"][:5], 1
                        ):
                            self.logging_manager.log_info(
                                f"  {i}. {name}: {count} times"
                            )

                # แสดงรายงานคุณภาพการแปล
                if hasattr(self, "translation_metrics"):
                    quality_report = self.translation_metrics.get_report()
                    self.logging_manager.log_info(quality_report)

                    # บันทึกรายงานลงไฟล์
                    try:
                        import datetime

                        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

                        # สร้างโฟลเดอร์ logs ถ้ายังไม่มี
                        import os

                        logs_dir = "logs"
                        if not os.path.exists(logs_dir):
                            os.makedirs(logs_dir)

                        report_file = f"logs/translation_quality_report_{timestamp}.txt"

                        with open(report_file, "w", encoding="utf-8") as f:
                            f.write(quality_report)
                            f.write(f"\n\nGenerated at: {datetime.datetime.now()}\n")
                        self.logging_manager.log_info(
                            f"Quality report saved to: {report_file}"
                        )
                    except Exception as e:
                        self.logging_manager.log_error(
                            f"Failed to save quality report: {e}"
                        )

                    # รีเซ็ต metrics สำหรับ session ถัดไป
                    self.translation_metrics = TranslationMetrics()

                # 🔧 [FIX] ปลดล็อค UI movement ทันทีหลังจากทำงานเสร็จ
                self.unlock_ui_movement()

                # บันทึกล็อก
                self.logging_manager.log_info(
                    "Translation stopped and UI hidden successfully"
                )

            except Exception as e:
                self.logging_manager.log_error(f"Error in stop_translation: {e}")
                # 🔧 [FIX] ปลดล็อค UI และซ่อนไอคอนในกรณีเกิดข้อผิดพลาด
                try:
                    self.unlock_ui_movement()
                except:
                    pass
                try:
                    if (
                        hasattr(self, "translated_ui_window")
                        and self.translated_ui_window.winfo_exists()
                    ):
                        self.translated_ui_window.withdraw()
                except:
                    pass

    def _hide_translated_ui_safely(self):
        """ซ่อน translated UI อย่างปลอดภัย"""
        if self.translated_ui_window.winfo_exists():
            self.translated_ui_window.withdraw()

    def text_similarity(self, text1, text2):
        return difflib.SequenceMatcher(None, text1, text2).ratio()

    def test_area_switching(self):
        """ทดสอบระบบสลับพื้นที่อัตโนมัติ"""
        try:
            # แสดงพื้นที่ปัจจุบัน
            current_areas = (
                self.current_area.split("+")
                if isinstance(self.current_area, str)
                else self.current_area
            )
            self._update_status_line(f"Current areas: {'+'.join(current_areas)}")
            self.logging_manager.log_info(
                f"Testing auto area switch. Current areas: {'+'.join(current_areas)}"
            )

            # ทดสอบการตรวจจับในพื้นหลัง (สำหรับพื้นที่ C)
            if set(current_areas) == set(["C"]):
                self._update_status_line("Testing background detection for area C...")
                background_type = self.check_for_background_dialogue()
                if background_type:
                    self._update_status_line(
                        f"Found {background_type} dialogue in background"
                    )
                    messagebox.showinfo(
                        "Background Detection",
                        f"พบข้อความประเภท {background_type} ในพื้นหลัง\nโปรแกรมจะสลับไปยังพื้นที่ที่เหมาะสม",
                    )

            # ทดสอบการตรวจจับและสลับพื้นที่อัตโนมัติ
            self._update_status_line("Testing smart area switching...")
            result = self.smart_switch_area()

            # แสดงผลการทดสอบ
            if result:
                new_areas = (
                    self.current_area.split("+")
                    if isinstance(self.current_area, str)
                    else self.current_area
                )
                messagebox.showinfo(
                    "Auto Area Switch Test",
                    f"สลับพื้นที่สำเร็จ\nจาก: {'+'.join(current_areas)}\nไปยัง: {'+'.join(new_areas)}",
                )
            else:
                # ตรวจสอบว่าทำไมจึงไม่มีการสลับพื้นที่
                if not self.settings.get("enable_auto_area_switch", True):
                    messagebox.showinfo(
                        "Auto Area Switch Test",
                        "การสลับพื้นที่อัตโนมัติถูกปิดอยู่\nเปิดการตั้งค่า 'Auto Area Detection' ในหน้า Settings",
                    )
                else:
                    messagebox.showinfo(
                        "Auto Area Switch Test",
                        "ไม่จำเป็นต้องสลับพื้นที่\nพื้นที่ปัจจุบันเหมาะสมกับประเภทข้อความแล้ว",
                    )

            return result
        except Exception as e:
            error_msg = f"เกิดข้อผิดพลาดในการทดสอบ: {str(e)}"
            self.logging_manager.log_error(error_msg)
            messagebox.showerror("Test Error", error_msg)
            return False

    def explain_area_switching(self):
        """แสดงหน้าต่างอธิบายระบบสลับพื้นที่อัตโนมัติ"""
        explanation = """
        ระบบสลับพื้นที่อัตโนมัติใน MagicBabel

        หลักการทำงาน:
        1. ตรวจจับประเภทข้อความอัตโนมัติ
        - บทสนทนาปกติ (มีชื่อ+ข้อความ) -> ใช้พื้นที่ A+B
        - บทบรรยาย -> ใช้พื้นที่ C
        - ข้อความตัวเลือก -> ใช้พื้นที่ B

        2. การตรวจสอบพิเศษสำหรับพื้นที่ C:
        - เมื่ออยู่ในพื้นที่ C (บทบรรยาย) ระบบจะตรวจสอบพื้นที่ A+B ในเบื้องหลังบ่อยขึ้น
        - หากพบว่าข้อความเปลี่ยนกลับเป็นบทสนทนาปกติ จะสลับกลับไปยังพื้นที่ A+B โดยอัตโนมัติ

        3. การป้องกันการสลับพื้นที่ถี่เกินไป:
        - ระบบมีกลไกป้องกันการสลับพื้นที่ไปมาเร็วเกินไป
        - ช่วงเวลาขั้นต่ำระหว่างการสลับพื้นที่: 3 วินาที

        การเปิด/ปิดระบบ:
        - ตั้งค่า "Auto Area Detection" ในหน้า Settings
        - เมื่อปิดการทำงาน จะต้องสลับพื้นที่ด้วยตนเองผ่าน Control Panel

        การทดสอบ:
        - ใช้ฟังก์ชัน test_area_switching() เพื่อทดสอบระบบ
        - วิธีใช้: เรียกฟังก์ชันนี้ผ่าน Python console หรือสร้างปุ่มทดสอบ
        """

        info_window = tk.Toplevel(self.root)
        info_window.title("ระบบสลับพื้นที่อัตโนมัติ")
        info_window.geometry("600x500")
        info_window.configure(bg="#1a1a1a")

        # สร้าง Text widget สำหรับแสดงข้อความ
        text_widget = tk.Text(
            info_window,
            wrap=tk.WORD,
            bg="#1a1a1a",
            fg="white",
            font=("IBM Plex Sans Thai Medium", 12),
            padx=20,
            pady=20,
        )
        text_widget.pack(expand=True, fill=tk.BOTH)
        text_widget.insert(tk.END, explanation)
        text_widget.config(state=tk.DISABLED)  # ทำให้ข้อความไม่สามารถแก้ไขได้

        # สร้างปุ่มปิดแบบง่าย ใช้ Button แทน Canvas
        close_button = tk.Button(
            info_window,
            text="×",
            font=("Arial", 14, "bold"),
            command=info_window.destroy,
            bg="#FF4136",
            fg="white",
            bd=0,
            padx=5,
            pady=0,
        )
        guide_width = 600  # กำหนดค่าความกว้างของหน้าต่าง guide
        close_button.place(x=guide_width - 35, y=10)

        # เพิ่ม hover effect
        close_button.bind(
            "<Enter>", lambda e: close_button.configure(bg="#FF6B6B", cursor="hand2")
        )
        close_button.bind("<Leave>", lambda e: close_button.configure(bg="#FF4136"))

        # ทำให้หน้าต่างอยู่ด้านบนและตรงกลางหน้าจอ
        info_window.update_idletasks()
        width = info_window.winfo_width()
        height = info_window.winfo_height()
        x = (info_window.winfo_screenwidth() // 2) - (width // 2)
        y = (info_window.winfo_screenheight() // 2) - (height // 2)
        info_window.geometry(f"{width}x{height}+{x}+{y}")
        info_window.attributes("-topmost", True)

    def area_detection_stability_system(self):
        """ระบบตรวจสอบความเสถียรของการตรวจจับรูปแบบข้อความเพื่อลดการสลับพื้นที่ไม่จำเป็น

        ฟังก์ชันนี้จะเก็บประวัติการตรวจจับประเภทข้อความและคำนวณความมั่นใจ
        ก่อนที่จะอนุญาตให้สลับพื้นที่ เพื่อป้องกันการสลับพื้นที่ไปมาบ่อยเกินไป

        Returns:
            dict: ข้อมูลเกี่ยวกับความเสถียรของการตรวจจับ
        """
        # สร้างหรืออัพเดตตัวแปรเก็บประวัติการตรวจจับ
        if not hasattr(self, "_detection_history"):
            self._detection_history = {
                "normal": [],  # บทสนทนาปกติ (A+B)
                "narrator": [],  # บทบรรยาย (C)
                "choice": [],  # ตัวเลือก (B)
                "other": [],  # ประเภทอื่นๆ (B)
                "unknown": [],  # ไม่สามารถระบุประเภทได้
                "last_stable_type": None,  # ประเภทล่าสุดที่มั่นคง
                "last_stable_time": 0,  # เวลาล่าสุดที่มีการเปลี่ยนประเภทที่มั่นคง
                "consecutive_detections": 0,  # จำนวนครั้งที่ตรวจพบประเภทเดิมติดต่อกัน
                "current_type": None,  # ประเภทปัจจุบัน
                "stability_score": 0,  # คะแนนความเสถียร (0-100)
            }

        # ระบบวิเคราะห์ความเสถียร
        history = self._detection_history
        current_time = time.time()

        # ประเภทข้อความที่สมเหตุสมผลที่จะสลับไปมา
        valid_types = ["normal", "narrator", "choice", "other"]

        # ตัดประวัติที่เก่าเกิน 10 วินาที
        for dtype in valid_types + ["unknown"]:
            history[dtype] = [d for d in history[dtype] if current_time - d <= 10]

        # คำนวณความถี่ของแต่ละประเภทในช่วง 5 วินาทีล่าสุด
        recent_window = 5  # ช่วงเวลาที่พิจารณา (วินาที)
        recent_counts = {}
        for dtype in valid_types:
            recent_counts[dtype] = len(
                [d for d in history[dtype] if current_time - d <= recent_window]
            )

        total_recent = sum(recent_counts.values())

        # คำนวณความมั่นใจของแต่ละประเภท
        confidence = {}
        for dtype in valid_types:
            if total_recent > 0:
                confidence[dtype] = (recent_counts[dtype] / total_recent) * 100
            else:
                confidence[dtype] = 0

        # ตรวจสอบว่ามีประเภทไหนที่มั่นใจมากพอ (มากกว่า 70%)
        stable_type = None
        max_confidence = 0
        for dtype, conf in confidence.items():
            if conf > max_confidence:
                max_confidence = conf
                stable_type = dtype

        # ตรวจสอบว่าประเภทนั้นมีความมั่นใจสูงพอ
        is_stable = max_confidence >= 70

        # อัพเดตข้อมูลความเสถียร
        if is_stable and stable_type != history["last_stable_type"]:
            history["last_stable_type"] = stable_type
            history["last_stable_time"] = current_time
            history["consecutive_detections"] = 1
        elif is_stable and stable_type == history["last_stable_type"]:
            history["consecutive_detections"] += 1

        # คะแนนความเสถียรขึ้นอยู่กับจำนวนครั้งที่ตรวจพบประเภทเดิมติดต่อกัน
        if history["consecutive_detections"] >= 3:
            history["stability_score"] = 100  # มั่นคงมาก (ตรวจพบประเภทเดิม 3 ครั้งขึ้นไป)
        else:
            history["stability_score"] = (
                history["consecutive_detections"] * 33
            )  # 33%, 66%, 99%

        # อัพเดตประเภทปัจจุบัน
        history["current_type"] = stable_type if is_stable else history["current_type"]

        return {
            "is_stable": is_stable,
            "stable_type": stable_type,
            "confidence": confidence,
            "stability_score": history["stability_score"],
            "consecutive_detections": history["consecutive_detections"],
            "time_since_last_stable": (
                current_time - history["last_stable_time"]
                if history["last_stable_time"] > 0
                else float("inf")
            ),
        }

    def switch_area_directly(self, dialogue_type):
        """สลับพื้นที่โดยตรงตามประเภทข้อความ (ใช้เมื่อ control_ui ไม่พร้อมใช้งาน)

        Args:
            dialogue_type: ประเภทข้อความ ("normal", "narrator", "choice", ฯลฯ)

        Returns:
            bool: True ถ้ามีการสลับพื้นที่ False ถ้าไม่มีการสลับพื้นที่
        """
        current_areas = (
            self.current_area.split("+")
            if isinstance(self.current_area, str)
            else self.current_area
        )
        current_areas_set = set(current_areas)

        # กำหนดพื้นที่ที่เหมาะสมสำหรับแต่ละประเภทข้อความ
        if dialogue_type == "normal":
            # บทสนทนาปกติ (มีทั้งชื่อและข้อความ) - ใช้พื้นที่ A+B
            target_areas = ["A", "B"]
        elif dialogue_type == "narrator":
            # บทบรรยาย - ใช้พื้นที่ C
            target_areas = ["C"]
        elif dialogue_type == "choice":
            # ตัวเลือก - ใช้พื้นที่ B
            target_areas = ["B"]
        elif dialogue_type in ["speaker_in_text", "dialog_without_name"]:
            # ข้อความที่มีชื่อคนพูดอยู่ในข้อความ หรือไม่มีชื่อ - ใช้พื้นที่ B
            target_areas = ["B"]
        else:
            # ประเภทข้อความที่ไม่รู้จัก - คงพื้นที่เดิม
            self._update_status_line(
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
        self.switch_area(new_area_str)
        self._update_status_line(f"✓ Auto switched to area: {new_area_str}")
        self.logging_manager.log_info(
            f"Auto switched from {'+'.join(current_areas)} to {new_area_str}"
        )

        return True

    def update_detection_history(self, dialogue_type):
        """บันทึกประวัติการตรวจจับประเภทข้อความ

        Args:
            dialogue_type: ประเภทข้อความที่ตรวจพบ ("normal", "narrator", "choice", ฯลฯ)
        """
        if not hasattr(self, "_detection_history"):
            self.area_detection_stability_system()  # สร้างถ้ายังไม่มี

        # เพิ่มเวลาปัจจุบันลงในประวัติของประเภทที่ตรวจพบ
        current_time = time.time()

        # จัดประเภทข้อความให้เข้ากับหมวดหมู่หลัก
        if dialogue_type == "normal":
            self._detection_history["normal"].append(current_time)
        elif dialogue_type == "narrator":
            self._detection_history["narrator"].append(current_time)
        elif dialogue_type == "choice":
            self._detection_history["choice"].append(current_time)
        elif dialogue_type in ["speaker_in_text", "dialog_without_name"]:
            self._detection_history["other"].append(current_time)
        else:
            self._detection_history["unknown"].append(current_time)

    def normalize_text(self, text):  # เพิ่ม self
        if not text:
            return ""
        text = re.sub(r"\s+", " ", text.strip())
        text = re.sub(r"[,.;:!?]+", ".", text)
        return text

    def is_valid_language_text(self, text):
        """ตรวจสอบว่าข้อความเป็นภาษาที่อนุญาตหรือไม่"""
        if not text or not text.strip():
            return False

        # นับจำนวนตัวอักษรแต่ละประเภท
        total_chars = len(text)
        thai_chars = len(re.findall(r"[\u0E00-\u0E7F]", text))
        english_chars = len(re.findall(r"[a-zA-Z]", text))
        number_chars = len(re.findall(r"[0-9]", text))
        space_punct = len(re.findall(r"[\s\.\,\!\?\:\;\-\(\)\[\]\{\}\'\"\/]", text))

        # ตัวอักษรที่อนุญาต
        allowed_chars = thai_chars + english_chars + number_chars + space_punct

        # คำนวณเปอร์เซ็นต์ตัวอักษรที่อนุญาต
        if total_chars > 0:
            allowed_percentage = (allowed_chars / total_chars) * 100

            # ถ้ามีตัวอักษรที่อนุญาตมากกว่า 80% ถือว่าใช้ได้
            if allowed_percentage >= 80:
                return True

        # ตรวจสอบภาษาที่ไม่อนุญาต
        # ภาษาเกาหลี
        if re.search(r"[\uAC00-\uD7AF]", text):
            self.logging_manager.log_info(f"Rejected Korean text: {text[:30]}...")
            return False

        # ภาษาจีน
        if re.search(r"[\u4E00-\u9FFF]", text):
            self.logging_manager.log_info(f"Rejected Chinese text: {text[:30]}...")
            return False

        # ภาษาญี่ปุ่น (Hiragana, Katakana, Kanji)
        if re.search(r"[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]", text):
            self.logging_manager.log_info(f"Rejected Japanese text: {text[:30]}...")
            return False

        # ภาษาอาหรับ
        if re.search(r"[\u0600-\u06FF]", text):
            self.logging_manager.log_info(f"Rejected Arabic text: {text[:30]}...")
            return False

        # ภาษารัสเซีย/ซิริลลิก
        if re.search(r"[\u0400-\u04FF]", text):
            self.logging_manager.log_info(f"Rejected Cyrillic text: {text[:30]}...")
            return False

        return True

    def clean_ocr_text(self, text):
        """ทำความสะอาดข้อความจาก OCR"""
        if not text:
            return ""

        # ลบตัวอักษรที่ไม่ต้องการออก
        # เก็บเฉพาะ ไทย, อังกฤษ, ตัวเลข, และเครื่องหมายพื้นฐาน
        cleaned = re.sub(
            r"[^\u0E00-\u0E7Fa-zA-Z0-9\s\.\,\!\?\:\;\-\(\)\[\]\{\}\'\"\/]", "", text
        )

        # ลบช่องว่างซ้ำๆ
        cleaned = re.sub(r"\s+", " ", cleaned)

        # ลบช่องว่างหน้าหลัง
        cleaned = cleaned.strip()

        return cleaned

    def _update_recent_speakers(self, speaker_name):
        """
        อัปเดต cache ชื่อผู้พูดล่าสุดและความถี่

        Args:
            speaker_name: ชื่อผู้พูดที่ต้องการอัปเดต
        """
        # กรองชื่อที่ไม่ต้องการ track
        if speaker_name and speaker_name not in ["[ผู้พูด]", "???", "[??]", "[?]"]:
            # ลบเครื่องหมาย [?] หรือ [??] ออกก่อน track
            clean_name = speaker_name.replace("[?]", "").replace("[??]", "").strip()

            if clean_name:
                # อัปเดตความถี่
                if clean_name in self.speaker_frequency:
                    self.speaker_frequency[clean_name] += 1
                else:
                    self.speaker_frequency[clean_name] = 1

                    # จำกัดขนาด frequency dict
                    if len(self.speaker_frequency) > self.max_speaker_frequency_entries:
                        # ลบรายการที่ใช้น้อยที่สุดออก
                        least_used = min(
                            self.speaker_frequency, key=self.speaker_frequency.get
                        )
                        del self.speaker_frequency[least_used]
                        self.logging_manager.log_info(
                            f"Removed least used speaker from frequency: '{least_used}'"
                        )

                # ลบชื่อเดิมออกจาก cache ก่อน (ถ้ามี)
                if clean_name in self.recent_speakers_cache:
                    self.recent_speakers_cache.remove(clean_name)

                # เพิ่มชื่อไปด้านหน้า
                self.recent_speakers_cache.insert(0, clean_name)

                # จำกัดขนาด cache
                if len(self.recent_speakers_cache) > self.max_recent_speakers:
                    self.recent_speakers_cache.pop()

                # Log frequency อัปเดต (สำหรับ debug)
                if self.speaker_frequency[clean_name] % 5 == 0:  # log ทุก 5 ครั้ง
                    self.logging_manager.log_info(
                        f"Speaker frequency update: '{clean_name}' = {self.speaker_frequency[clean_name]} times"
                    )

    def _guess_speaker_from_context(self, message_part):
        """
        พยายามเดาผู้พูดจาก context และ cache อย่างฉลาด

        Args:
            message_part: ข้อความบทสนทนา

        Returns:
            str หรือ None: ชื่อที่เดาได้หรือ None
        """

        # 1. ถ้ามีผู้พูดล่าสุดเพียงคนเดียว น่าจะเป็นคนเดิม
        if len(self.recent_speakers_cache) == 1:
            return self.recent_speakers_cache[0]

        # 2. ลองหาชื่อจากข้อความเอง (emergency detection)
        potential_name = self._emergency_name_detection(message_part)
        if potential_name:
            return potential_name

        # 3. ใช้ชื่อที่ใช้บ่อยที่สุดใน session นี้
        if hasattr(self, "speaker_frequency") and self.speaker_frequency:
            # หาชื่อที่ใช้บ่อยที่สุด
            most_frequent = max(self.speaker_frequency, key=self.speaker_frequency.get)
            if self.speaker_frequency[most_frequent] >= 3:  # ใช้อย่างน้อย 3 ครั้ง
                self.logging_manager.log_info(
                    f"Using most frequent speaker: '{most_frequent}' (count: {self.speaker_frequency[most_frequent]})"
                )
                return most_frequent

        # 4. ตรวจสอบ pattern ของข้อความ
        # ถ้าข้อความมีคำว่า "ฉัน", "ข้า", "I", "me" อาจเป็นตัวละครหลัก
        if any(
            word in message_part.lower()
            for word in ["ฉัน", "ข้า", "i ", "me ", "i'm", "i am"]
        ):
            # ลองหาตัวละครหลักจาก frequency
            if hasattr(self, "speaker_frequency") and self.speaker_frequency:
                # เรียงลำดับตามความถี่
                sorted_speakers = sorted(
                    self.speaker_frequency.items(), key=lambda x: x[1], reverse=True
                )
                if sorted_speakers and sorted_speakers[0][1] >= 5:  # ตัวละครที่พูดมากที่สุด
                    protagonist = sorted_speakers[0][0]
                    self.logging_manager.log_info(
                        f"Guessing protagonist from frequency: '{protagonist}'"
                    )
                    return protagonist

        return None

    def _find_similar_name_in_cache(self, detected_name):
        """
        หาชื่อที่คล้ายกันใน cache โดยใช้ fuzzy matching

        Args:
            detected_name: ชื่อที่ OCR ตรวจพบ

        Returns:
            str หรือ None: ชื่อที่คล้ายกันที่สุดใน cache หรือ None ถ้าไม่พบ
        """
        if not detected_name or len(self.recent_speakers_cache) == 0:
            return None

        detected_clean = detected_name.lower().strip()

        for cached_name in self.recent_speakers_cache:
            cached_clean = cached_name.lower().strip()

            # Exact match
            if detected_clean == cached_clean:
                return cached_name

            # Fuzzy matching (similarity >= 80%)
            similarity = self._calculate_name_similarity(detected_clean, cached_clean)
            if similarity >= 0.8:
                self.logging_manager.log_info(
                    f"Found similar name: '{detected_name}' -> '{cached_name}' (similarity: {similarity:.2f})"
                )
                return cached_name

        return None

    def _calculate_name_similarity(self, name1, name2):
        """
        คำนวณความคล้ายกันของชื่อโดยใช้ difflib

        Args:
            name1: ชื่อแรก
            name2: ชื่อที่สอง

        Returns:
            float: ค่าความคล้าย (0.0-1.0)
        """
        import difflib

        return difflib.SequenceMatcher(None, name1, name2).ratio()

    def _emergency_name_detection(self, message_part):
        """
        ตรวจจับชื่อฉุกเฉินจากข้อความโดยตรง
        เช่น ข้อความที่มีรูปแบบ "Hello Kaidate, how are you?"

        Args:
            message_part: ข้อความบทสนทนา

        Returns:
            str หรือ None: ชื่อที่พบหรือ None
        """
        import re

        # หาคำที่ขึ้นต้นด้วยตัวพิมพ์ใหญ่และมีความยาวเหมาะสม (2-15 ตัวอักษร)
        potential_names = re.findall(r"\b[A-Z][a-zA-Z]{1,14}\b", message_part)

        for name in potential_names:
            # ตรวจสอบว่าเป็นชื่อที่เคยพบใน npc.json หรือไม่
            if hasattr(self.text_corrector, "names") and name.lower() in [
                n.lower() for n in self.text_corrector.names
            ]:
                self.logging_manager.log_info(
                    f"Emergency detection found known name: '{name}'"
                )
                return name

            # ตรวจสอบว่าอยู่ใน recent cache หรือไม่
            for cached_name in self.recent_speakers_cache:
                if (
                    self._calculate_name_similarity(name.lower(), cached_name.lower())
                    >= 0.8
                ):
                    self.logging_manager.log_info(
                        f"Emergency detection found similar to cache: '{name}' -> '{cached_name}'"
                    )
                    return cached_name

            # ตรวจสอบว่าเป็นชื่อที่ใช้บ่อยใน session หรือไม่
            if hasattr(self, "speaker_frequency") and name in self.speaker_frequency:
                if self.speaker_frequency[name] >= 2:  # ใช้อย่างน้อย 2 ครั้ง
                    self.logging_manager.log_info(
                        f"Emergency detection found frequent name: '{name}'"
                    )
                    return name

        return None

    def get_speaker_statistics(self):
        """
        ดูสถิติการใช้ชื่อผู้พูดใน session นี้

        Returns:
            dict: สถิติต่างๆ
        """
        if not self.speaker_frequency:
            return {
                "total_speakers": 0,
                "total_dialogues": 0,
                "most_frequent": None,
                "frequency_list": [],
            }

        total_dialogues = sum(self.speaker_frequency.values())
        sorted_speakers = sorted(
            self.speaker_frequency.items(), key=lambda x: x[1], reverse=True
        )

        return {
            "total_speakers": len(self.speaker_frequency),
            "total_dialogues": total_dialogues,
            "most_frequent": sorted_speakers[0] if sorted_speakers else None,
            "frequency_list": sorted_speakers[:10],  # Top 10
        }

    def reset_speaker_data(self):
        """
        รีเซ็ตข้อมูล speaker ทั้งหมด (ใช้เมื่อเริ่มเกมใหม่)
        """
        self.recent_speakers_cache.clear()
        self.speaker_frequency.clear()
        self.logging_manager.log_info("Speaker data has been reset")

    def translation_loop(self):
        """จัดการการแปลและแสดงผล (บังคับ Format Choice Output ขั้นสุดท้ายก่อนส่งให้ UI)"""
        last_translated_text = ""
        waiting_for_message = False
        waiting_for_name = False
        temp_name = None
        temp_message = None
        is_processing = False
        last_processing_time = time.time()

        last_ocr_time = time.time()
        same_text_count = 0
        last_ocr_raw_text = ""

        last_auto_switch_check = 0
        auto_switch_interval = 3.0
        background_check_interval = 1.5
        auto_switch_cooldown_end_time = 0

        self._logged_skipping_translation = False
        self._logged_waiting_for_click = False

        dialogue_type_enum_available = "DialogueType" in globals() and isinstance(
            DialogueType, type(Enum)
        )

        def get_dialogue_type_value(enum_member_name, fallback_string):
            if dialogue_type_enum_available and hasattr(DialogueType, enum_member_name):
                return getattr(DialogueType, enum_member_name)
            return fallback_string

        dt_choice = get_dialogue_type_value("CHOICE", "choice")
        dt_narrator = get_dialogue_type_value("NARRATOR", "narrator")
        dt_normal = get_dialogue_type_value("NORMAL", "normal")
        dt_speaker_in_text = get_dialogue_type_value(
            "SPEAKER_IN_TEXT", "speaker_in_text"
        )
        dt_dialog_without_name = get_dialogue_type_value(
            "DIALOG_WITHOUT_NAME", "dialog_without_name"
        )
        dt_unknown = get_dialogue_type_value("UNKNOWN", "unknown")

        while self.is_translating:
            raw_message_part_for_choice_check = ""
            message_part_for_choice_in_dialog = ""
            was_structurally_detected_as_choice = False
            parsed_choice_header_from_layout = None
            parsed_choices_from_layout = []
            combined_text_from_layout = None
            combined_text = ""
            final_dialogue_type = dt_unknown

            try:
                if is_processing:
                    time.sleep(0.05)
                    continue

                current_time = time.time()
                time_since_last_ocr_action = current_time - last_ocr_time

                if (
                    self.has_psutil
                    and hasattr(self, "_cpu_monitor_event")
                    and self._cpu_monitor_event.is_set()
                ):
                    self.logging_manager.log_info(
                        f"MainLoop: Detected CPU overload signal. Current ocr_interval: {self.ocr_interval:.2f}s"
                    )
                    current_cpu_limit_for_adjustment = self.settings.get(
                        "cpu_limit", 80
                    )
                    if current_cpu_limit_for_adjustment <= 50:
                        self.ocr_interval = min(
                            self.max_ocr_interval, self.ocr_interval * 1.5
                        )
                    elif current_cpu_limit_for_adjustment <= 60:
                        self.ocr_interval = min(
                            self.max_ocr_interval, self.ocr_interval * 1.3
                        )
                    else:
                        self.ocr_interval = min(
                            self.max_ocr_interval, self.ocr_interval * 1.2
                        )
                    self.logging_manager.log_info(
                        f"MainLoop: Increased ocr_interval to {self.ocr_interval:.2f}s due to CPU overload."
                    )
                    self._cpu_monitor_event.clear()
                    last_ocr_time = current_time

                if self.settings.get("enable_auto_area_switch", False):
                    if current_time >= auto_switch_cooldown_end_time:
                        manual_selection_grace_period = 15
                        last_manual_time = self.settings.get(
                            "last_manual_preset_selection_time", 0
                        )
                        if (
                            current_time - last_manual_time
                            < manual_selection_grace_period
                        ):
                            pass
                        else:
                            current_areas_before_check = (
                                self.current_area.split("+")
                                if isinstance(self.current_area, str)
                                else [self.current_area]
                            )
                            check_interval_for_auto_switch = (
                                background_check_interval
                                if set(current_areas_before_check) == set(["C"])
                                else auto_switch_interval
                            )
                            if (
                                current_time - last_auto_switch_check
                                >= check_interval_for_auto_switch
                            ):
                                area_switched = self.smart_switch_area()
                                last_auto_switch_check = current_time
                                if area_switched:
                                    self.logging_manager.log_info(
                                        "Auto Area Switch triggered a change. Cooldown initiated."
                                    )
                                    auto_switch_cooldown_end_time = current_time + 5.0
                                    waiting_for_message = False
                                    waiting_for_name = False
                                    temp_name = None
                                    temp_message = None
                                    is_processing = False
                                    self.force_next_translation = True
                                    continue

                current_adaptive_ocr_interval = self.ocr_interval
                if same_text_count > 0:
                    current_adaptive_ocr_interval = min(
                        self.ocr_interval * (1 + (same_text_count * 0.05)),
                        self.max_ocr_interval,
                    )

                if (
                    time_since_last_ocr_action < current_adaptive_ocr_interval
                    and not self.force_next_translation
                ):
                    time.sleep(0.05)
                    continue

                click_translate_enabled = self.settings.get(
                    "enable_click_translate", False
                )
                if click_translate_enabled and not self.force_next_translation:
                    if not self._logged_waiting_for_click:
                        self._update_status_line(
                            "Waiting for click [Click Translate Mode]..."
                        )
                        self.logging_manager.log_info(
                            "Click Translate Mode: Waiting for click."
                        )
                        self._logged_waiting_for_click = True
                    time.sleep(0.1)
                    continue
                else:
                    self._logged_waiting_for_click = False

                is_processing = True
                last_ocr_time = current_time

                current_preset_num = self.settings.get("current_preset", 1)
                current_preset_role = self.settings.get_preset_role(current_preset_num)
                self.logging_manager.log_info(
                    f"Translation loop: Cycle Start. Preset: {current_preset_num} (Role: {current_preset_role}), Force: {self.force_next_translation}"
                )

                # ตรวจสอบ cache ของ choice detection
                use_cached_choice_detection = False
                if (
                    hasattr(self, "last_detected_as_choice")
                    and hasattr(self, "last_choice_detection_time")
                    and hasattr(self, "choice_detection_cache_duration")
                ):
                    time_since_last_choice_detection = (
                        current_time - self.last_choice_detection_time
                    )
                    if (
                        time_since_last_choice_detection
                        < self.choice_detection_cache_duration
                        and self.last_detected_as_choice
                    ):
                        use_cached_choice_detection = True
                        self.logging_manager.log_info(
                            f"Using cached choice detection (age: {time_since_last_choice_detection:.1f}s)"
                        )

                if current_preset_role == "choice":
                    choice_area_key_for_layout = self.settings.get(
                        f"preset_{current_preset_num}_choice_area", "B"
                    )
                    active_areas_for_current_preset = (
                        self.settings.get_preset_areas_list(current_preset_num)
                    )
                    if not active_areas_for_current_preset:
                        active_areas_for_current_preset = (
                            self.current_area.split("+")
                            if isinstance(self.current_area, str)
                            else [self.current_area]
                        )

                    if choice_area_key_for_layout in active_areas_for_current_preset:
                        self.logging_manager.log_info(
                            f"Preset role is 'choice', attempting layout-based detection for Area '{choice_area_key_for_layout}'."
                        )
                        translate_area_config = self.settings.get_translate_area(
                            choice_area_key_for_layout
                        )
                        if translate_area_config:
                            start_x, start_y, end_x, end_y = (
                                translate_area_config["start_x"],
                                translate_area_config["start_y"],
                                translate_area_config["end_x"],
                                translate_area_config["end_y"],
                            )
                            screen_size_str = self.settings.get(
                                "screen_size", "2560x1440"
                            )
                            s_w, s_h = map(int, screen_size_str.split("x"))
                            scale_x = self.root.winfo_screenwidth() / s_w
                            scale_y = self.root.winfo_screenheight() / s_h
                            x1, y1 = int(min(start_x, end_x) * scale_x), int(
                                min(start_y, end_y) * scale_y
                            )
                            x2, y2 = int(max(start_x, end_x) * scale_x), int(
                                max(start_y, end_y) * scale_y
                            )

                            if x1 < x2 and y1 < y2:
                                img_choice_area = ImageGrab.grab(bbox=(x1, y1, x2, y2))
                                # Layout-based choice detection ด้วย PaddleOCR ถูกปิดใช้งาน
                                # ใช้ EasyOCR choice detection แทน
                                self.logging_manager.log_info(
                                    f"Layout-based choice detection skipped (PaddleOCR disabled). Using EasyOCR for Area '{choice_area_key_for_layout}'."
                                )
                            else:
                                self.logging_manager.log_warning(
                                    f"Invalid bbox for Area '{choice_area_key_for_layout}' in layout-based choice detection."
                                )
                        else:
                            self.logging_manager.log_warning(
                                f"No translate_area_config for Area '{choice_area_key_for_layout}' in layout-based choice detection."
                            )
                    else:
                        self.logging_manager.log_info(
                            f"Designated choice area '{choice_area_key_for_layout}' not active for current 'choice' preset, skipping layout detection."
                        )

                    # PaddleOCR choice detection สำหรับทุก preset ถูกปิดใช้งาน
                    # ใช้ EasyOCR enhanced line grouping แทน
                    # พยายามตรวจจับ choice ในทุก preset โดยใช้ Area B เป็นหลัก
                    try:
                        active_areas_for_all_preset = (
                            self.settings.get_preset_areas_list(current_preset_num)
                        )
                        if not active_areas_for_all_preset:
                            active_areas_for_all_preset = (
                                self.current_area.split("+")
                                if isinstance(self.current_area, str)
                                else [self.current_area]
                            )

                        choice_detection_area = (
                            "B"  # ใช้ Area B เป็นพื้นที่หลักในการตรวจจับ choice
                        )
                        if choice_detection_area in active_areas_for_all_preset:
                            self.logging_manager.log_info(
                                f"Attempting PaddleOCR choice detection for all presets using Area '{choice_detection_area}'."
                            )
                            translate_area_config = self.settings.get_translate_area(
                                choice_detection_area
                            )

                            if (
                                translate_area_config
                                and self.has_paddleocr
                                and self.paddle_ocr_engine
                            ):
                                start_x, start_y, end_x, end_y = (
                                    translate_area_config["start_x"],
                                    translate_area_config["start_y"],
                                    translate_area_config["end_x"],
                                    translate_area_config["end_y"],
                                )
                                screen_size_str = self.settings.get(
                                    "screen_size", "2560x1440"
                                )
                                s_w, s_h = map(int, screen_size_str.split("x"))
                                scale_x = self.root.winfo_screenwidth() / s_w
                                scale_y = self.root.winfo_screenheight() / s_h
                                x1, y1 = int(min(start_x, end_x) * scale_x), int(
                                    min(start_y, end_y) * scale_y
                                )
                                x2, y2 = int(max(start_x, end_x) * scale_x), int(
                                    max(start_y, end_y) * scale_y
                                )

                                if x1 < x2 and y1 < y2:
                                    img_choice_area = ImageGrab.grab(
                                        bbox=(x1, y1, x2, y2)
                                    )
                                    img_choice_area_processed = self.preprocess_image(
                                        img_choice_area
                                    )
                                    temp_choice_layout_path = os.path.join(
                                        os.getcwd(),
                                        f"temp_choice_all_preset_{int(time.time()*1000)}.png",
                                    )
                                    try:
                                        img_choice_area_processed.save(
                                            temp_choice_layout_path
                                        )
                                        (
                                            is_struct_choice_all,
                                            header_struct_all,
                                            choices_struct_all,
                                        ) = self.detect_choice_with_layout(
                                            temp_choice_layout_path
                                        )

                                        if is_struct_choice_all:
                                            was_structurally_detected_as_choice = True
                                            parsed_choice_header_from_layout = (
                                                header_struct_all
                                            )
                                            parsed_choices_from_layout = (
                                                choices_struct_all
                                            )
                                            if header_struct_all and choices_struct_all:
                                                combined_text_from_layout = (
                                                    f"{header_struct_all}\n"
                                                    + "\n".join(choices_struct_all)
                                                )
                                            elif choices_struct_all:
                                                combined_text_from_layout = "\n".join(
                                                    choices_struct_all
                                                )
                                            elif header_struct_all:
                                                combined_text_from_layout = (
                                                    header_struct_all
                                                )
                                            if combined_text_from_layout:
                                                final_dialogue_type = dt_choice
                                            self.logging_manager.log_info(
                                                f"PaddleOCR choice detection for all presets succeeded in Area '{choice_detection_area}'!"
                                            )
                                        else:
                                            self.logging_manager.log_info(
                                                f"PaddleOCR choice detection for all presets did NOT identify choice in Area '{choice_detection_area}'."
                                            )
                                    except Exception as e_choice_all:
                                        self.logging_manager.log_error(
                                            f"Error during PaddleOCR choice detection for all presets: {e_choice_all}"
                                        )
                                    finally:
                                        if os.path.exists(temp_choice_layout_path):
                                            try:
                                                os.remove(temp_choice_layout_path)
                                            except Exception as e_remove_all:
                                                self.logging_manager.log_warning(
                                                    f"Could not remove temp choice file: {e_remove_all}"
                                                )
                                else:
                                    self.logging_manager.log_warning(
                                        f"Invalid bbox for Area '{choice_detection_area}' in all-preset choice detection."
                                    )
                            else:
                                if not (self.has_paddleocr and self.paddle_ocr_engine):
                                    self.logging_manager.log_info(
                                        "PaddleOCR not available for all-preset choice detection."
                                    )
                        else:
                            self.logging_manager.log_info(
                                f"Area '{choice_detection_area}' not active for current preset, skipping all-preset choice detection."
                            )
                    except Exception as e_all_preset_choice:
                        self.logging_manager.log_error(
                            f"Error in all-preset choice detection: {e_all_preset_choice}"
                        )

                results_from_capture_ocr = []
                if not was_structurally_detected_as_choice:
                    results_from_capture_ocr = self.capture_and_ocr()
                    if not results_from_capture_ocr:
                        self.logging_manager.log_info(
                            "capture_and_ocr returned no results. Skipping this cycle."
                        )
                        is_processing = False
                        continue

                raw_texts_for_similarity = []
                processed_results_for_fallback = []

                if results_from_capture_ocr:
                    for area_ocr, text_ocr_content in results_from_capture_ocr:
                        raw_texts_for_similarity.append(text_ocr_content)
                        processed_results_for_fallback.append(
                            (area_ocr, text_ocr_content)
                        )
                        if area_ocr == "B":
                            raw_message_part_for_choice_check = text_ocr_content.strip()

                # ✨ CHOICE PRESET SPECIAL HANDLING: จัดการ choice preset ใน main flow
                choice_text_override = None
                choice_dialogue_type_override = None
                if current_preset_role == "choice" and processed_results_for_fallback:
                    self.logging_manager.log_info(
                        f"[PRESET-CHOICE-DEBUG] ✅ Processing choice preset in MAIN flow"
                    )
                    self.logging_manager.log_info(
                        f"[PRESET-CHOICE-DEBUG] OCR results: {processed_results_for_fallback}"
                    )

                    # ดึงข้อความจาก Area B เท่านั้น (skip Area A)
                    text_from_B_main = ""
                    for area_main, text_main in processed_results_for_fallback:
                        if area_main == "B" and text_main.strip():
                            text_from_B_main = self.text_corrector.correct_text(
                                text_main
                            ).strip()
                            self.logging_manager.log_info(
                                f"[PRESET-CHOICE-DEBUG] Found Area B text: '{text_from_B_main}'"
                            )
                            break

                    if text_from_B_main:
                        # ตรวจสอบ choice indicators
                        text_lower_main = text_from_B_main.lower()
                        choice_indicators_main = [
                            bool(re.match(r"^1\.", text_from_B_main.strip())),
                            bool(re.match(r"^2\.", text_from_B_main.strip())),
                            text_from_B_main.count("\n") >= 2
                            and len(text_from_B_main) < 200,
                            any(
                                keyword in text_lower_main
                                for keyword in [
                                    "contest",
                                    "take back",
                                    "stolen",
                                    "won't let",
                                ]
                            ),
                        ]

                        self.logging_manager.log_info(
                            f"[PRESET-CHOICE-DEBUG] Choice indicators: {choice_indicators_main}"
                        )

                        if any(choice_indicators_main):
                            choice_text_override = (
                                f"What will you say?\n{text_from_B_main}"
                            )
                            choice_dialogue_type_override = (
                                dt_choice  # ✨ สำคัญ: ตั้งค่า dialogue type เป็น choice
                            )
                            self.logging_manager.log_info(
                                f"[PRESET-CHOICE-DEBUG] ✅ SUCCESS! Added 'What will you say?' - Final: '{choice_text_override}'"
                            )
                            self.logging_manager.log_info(
                                f"[PRESET-CHOICE-DEBUG] ✅ Set final_dialogue_type = dt_choice for choice formatting"
                            )
                        else:
                            choice_text_override = text_from_B_main
                            choice_dialogue_type_override = (
                                dt_choice  # ✨ ยังคงเป็น choice แม้ไม่มี indicators
                            )
                            self.logging_manager.log_info(
                                f"[PRESET-CHOICE-DEBUG] ❌ No choice indicators, using as-is: '{choice_text_override}'"
                            )
                            self.logging_manager.log_info(
                                f"[PRESET-CHOICE-DEBUG] ✅ Still set final_dialogue_type = dt_choice (choice preset should always use choice format)"
                            )
                    else:
                        self.logging_manager.log_info(
                            f"[PRESET-CHOICE-DEBUG] ❌ No text found in Area B"
                        )

                current_ocr_text_joined = ""
                if (
                    was_structurally_detected_as_choice
                    and combined_text_from_layout is not None
                ):
                    current_ocr_text_joined = combined_text_from_layout
                    combined_text = combined_text_from_layout
                    self.logging_manager.log_info(
                        f"Using combined_text from layout-based choice: '{combined_text[:100]}...'"
                    )
                elif choice_text_override is not None:
                    # ✨ ใช้ choice_text_override จาก choice preset
                    current_ocr_text_joined = choice_text_override
                    combined_text = choice_text_override
                    self.logging_manager.log_info(
                        f"[PRESET-CHOICE-DEBUG] ✅ Using choice_text_override as combined_text: '{combined_text[:100]}...'"
                    )
                else:
                    current_ocr_text_joined = " ".join(raw_texts_for_similarity)
                    self.logging_manager.log_info(
                        "Proceeding with combined_text to be built from general capture_and_ocr results."
                    )

                normalized_current = self.normalize_text(current_ocr_text_joined)
                normalized_last = self.normalize_text(last_ocr_raw_text)

                self.logging_manager.log_info(
                    f"Normalized current OCR text for similarity: '{normalized_current[:100]}...'"
                )
                self.logging_manager.log_info(
                    f"Normalized last OCR text for similarity: '{normalized_last[:100]}...'"
                )

                if (
                    normalized_current == normalized_last
                    and not self.force_next_translation
                    and not (
                        was_structurally_detected_as_choice
                        and combined_text_from_layout is not None
                    )
                ):
                    same_text_count += 1
                    if not self._logged_skipping_translation:
                        self._update_status_line("Skipping translation (same text).")
                        self.logging_manager.log_info(
                            f"Skipping translation (same text detected, count: {same_text_count})."
                        )
                        self._logged_skipping_translation = True
                    if same_text_count > self.same_text_threshold:
                        self.force_next_translation = True
                        same_text_count = 0
                        self.logging_manager.log_info(
                            "Forcing translation due to prolonged same text."
                        )
                    is_processing = False

                    # *** RAPID DETECTION: Update tracking even when no text change ***
                    self.update_rapid_dialogue_tracking(text_changed=False)
                    continue
                else:
                    same_text_count = 0
                    last_ocr_raw_text = current_ocr_text_joined
                    self._logged_skipping_translation = False

                    # *** RAPID DETECTION: Track text changes for rapid dialogue mode ***
                    self.update_rapid_dialogue_tracking(text_changed=True)

                if not was_structurally_detected_as_choice:
                    text_to_translate_override = None
                    was_detected_as_choice_original_method = False

                    # ตรวจสอบ choice dialogue ด้วยวิธีดั้งเดิม หรือใช้ cache
                    if use_cached_choice_detection:
                        was_detected_as_choice_original_method = True
                        self.logging_manager.log_info(
                            "Using cached choice detection: True"
                        )
                    elif raw_message_part_for_choice_check and self.is_choice_dialogue(
                        raw_message_part_for_choice_check
                    ):
                        was_detected_as_choice_original_method = True
                        # บันทึกผลการตรวจจับลง cache
                        self.last_detected_as_choice = True
                        self.last_choice_detection_time = current_time
                        self.logging_manager.log_info(
                            f"is_choice_dialogue (original method on raw Area B text) returned: True. Text: '{raw_message_part_for_choice_check[:70]}...'"
                        )
                        # Log เพิ่มเติมเพื่อ debug
                        self.logging_manager.log_info(
                            f"Choice detected! Full text: '{raw_message_part_for_choice_check}'"
                        )
                    else:
                        # รีเซ็ต cache ถ้าไม่ใช่ choice
                        self.last_detected_as_choice = False
                        self.logging_manager.log_info(
                            f"is_choice_dialogue (original method on raw Area B text) returned: False. Text was: '{raw_message_part_for_choice_check[:70]}...'"
                        )
                        # Log เพิ่มเติมเพื่อ debug
                        self.logging_manager.log_info(
                            f"Choice NOT detected. Full text: '{raw_message_part_for_choice_check}'"
                        )

                    if current_preset_role == "choice":
                        self.logging_manager.log_info(
                            "Building combined_text for 'choice' preset (fallback from layout detection)."
                        )
                        # 🔍 DEBUG: เพิ่ม debug logging สำหรับ Preset 3 (Ex-Choice)
                        self.logging_manager.log_info(
                            f"[PRESET-CHOICE-DEBUG] ✅ Entered choice logic - current_preset_role: '{current_preset_role}'"
                        )
                        self.logging_manager.log_info(
                            f"[PRESET-CHOICE-DEBUG] processed_results_for_fallback: {processed_results_for_fallback}"
                        )

                        text_from_B_corrected = ""
                        area_b_found_in_results = False
                        for area_fb, text_fb_raw_ocr in processed_results_for_fallback:
                            if area_fb == "B":
                                text_from_B_corrected = (
                                    self.text_corrector.correct_text(
                                        text_fb_raw_ocr
                                    ).strip()
                                )
                                area_b_found_in_results = True
                                # 🔍 DEBUG: แสดงข้อความดิบจาก Area B
                                self.logging_manager.log_info(
                                    f"[PRESET-CHOICE-DEBUG] Raw OCR from Area B: '{text_fb_raw_ocr}'"
                                )
                                self.logging_manager.log_info(
                                    f"[PRESET-CHOICE-DEBUG] Corrected text from Area B: '{text_from_B_corrected}'"
                                )
                                break
                        if area_b_found_in_results and text_from_B_corrected:
                            # 🔍 DEBUG: แสดงสถานะ Area B
                            self.logging_manager.log_info(
                                f"[PRESET-CHOICE-DEBUG] ✅ Area B found with text: '{text_from_B_corrected}'"
                            )
                            self.logging_manager.log_info(
                                f"[PRESET-CHOICE-DEBUG] was_detected_as_choice_original_method: {was_detected_as_choice_original_method}"
                            )

                            if not was_detected_as_choice_original_method:
                                # ตรวจสอบว่าข้อความมี pattern ของ choice หรือไม่
                                # แม้ OCR จะผิดพลาดบ้าง
                                text_lower = text_from_B_corrected.lower()

                                # รูปแบบที่บ่งบอกว่าน่าจะเป็น choice (แม้ไม่มี header)
                                choice_indicators = [
                                    # Pattern ของตัวเลือกที่ขึ้นต้นด้วยหมายเลข
                                    bool(
                                        re.match(r"^1\.", text_from_B_corrected.strip())
                                    ),
                                    bool(
                                        re.match(r"^2\.", text_from_B_corrected.strip())
                                    ),
                                    # Pattern ของข้อความสั้นๆ หลายบรรทัด
                                    text_from_B_corrected.count("\n") >= 2
                                    and len(text_from_B_corrected) < 200,
                                    # คำที่มักพบใน choice dialogue
                                    any(
                                        keyword in text_lower
                                        for keyword in [
                                            "contest",
                                            "take back",
                                            "stolen",
                                            "won't let",
                                        ]
                                    ),
                                ]

                                # 🔍 DEBUG: แสดงผลการตรวจสอบ choice indicators
                                self.logging_manager.log_info(
                                    f"[PRESET-CHOICE-DEBUG] text_lower: '{text_lower}'"
                                )
                                self.logging_manager.log_info(
                                    f"[PRESET-CHOICE-DEBUG] Choice indicators check:"
                                )
                                self.logging_manager.log_info(
                                    f"[PRESET-CHOICE-DEBUG]   - Starts with '1.': {choice_indicators[0]}"
                                )
                                self.logging_manager.log_info(
                                    f"[PRESET-CHOICE-DEBUG]   - Starts with '2.': {choice_indicators[1]}"
                                )
                                self.logging_manager.log_info(
                                    f"[PRESET-CHOICE-DEBUG]   - Multi-line & short: {choice_indicators[2]} (lines: {text_from_B_corrected.count('\n')}, length: {len(text_from_B_corrected)})"
                                )
                                self.logging_manager.log_info(
                                    f"[PRESET-CHOICE-DEBUG]   - Has keywords: {choice_indicators[3]}"
                                )
                                self.logging_manager.log_info(
                                    f"[PRESET-CHOICE-DEBUG] Overall choice_indicators: {choice_indicators}"
                                )
                                self.logging_manager.log_info(
                                    f"[PRESET-CHOICE-DEBUG] any(choice_indicators): {any(choice_indicators)}"
                                )

                                # ถ้ามีตัวบ่งชี้ว่าเป็น choice ให้เพิ่ม header
                                if any(choice_indicators):
                                    modified_text_B = (
                                        f"What will you say?\n{text_from_B_corrected}"
                                    )
                                    text_to_translate_override = modified_text_B
                                    # 🔍 DEBUG: แสดงผลสำเร็จ
                                    self.logging_manager.log_info(
                                        f"[PRESET-CHOICE-DEBUG] ✅ SUCCESS! Choice detected - added 'What will you say?'"
                                    )
                                    self.logging_manager.log_info(
                                        f"[PRESET-CHOICE-DEBUG] Final text to translate: '{modified_text_B}'"
                                    )
                                    self.logging_manager.log_info(
                                        "Preset 'choice': Detected choice indicators, prepended 'What will you say?'."
                                    )
                                else:
                                    # ถ้าไม่มีตัวบ่งชี้ ให้ใช้ข้อความเดิมโดยไม่เพิ่ม header
                                    text_to_translate_override = text_from_B_corrected
                                    # 🔍 DEBUG: แสดงผลไม่ผ่าน
                                    self.logging_manager.log_info(
                                        f"[PRESET-CHOICE-DEBUG] ❌ NO CHOICE DETECTED - using text as-is"
                                    )
                                    self.logging_manager.log_info(
                                        f"[PRESET-CHOICE-DEBUG] Final text to translate: '{text_from_B_corrected}'"
                                    )
                                    self.logging_manager.log_info(
                                        "Preset 'choice': No clear choice indicators, using text as-is."
                                    )
                            else:
                                # ถ้าตรวจพบเป็น choice อยู่แล้ว ใช้ข้อความเดิม
                                text_to_translate_override = (
                                    raw_message_part_for_choice_check
                                )
                                # 🔍 DEBUG: แสดงผลเมื่อ choice ถูกตรวจพบแล้ว
                                self.logging_manager.log_info(
                                    f"[PRESET-CHOICE-DEBUG] ✅ Choice already detected by original method"
                                )
                                self.logging_manager.log_info(
                                    f"[PRESET-CHOICE-DEBUG] Using raw_message_part_for_choice_check: '{raw_message_part_for_choice_check}'"
                                )
                                self.logging_manager.log_info(
                                    "Preset 'choice' (fallback): Original is_choice_dialogue=True on raw B. Using raw B text."
                                )
                        else:
                            # 🔍 DEBUG: แสดงผลเมื่อไม่พบ Area B หรือข้อความว่าง
                            self.logging_manager.log_info(
                                f"[PRESET-CHOICE-DEBUG] ❌ Area B not found or empty!"
                            )
                            self.logging_manager.log_info(
                                f"[PRESET-CHOICE-DEBUG] area_b_found_in_results: {area_b_found_in_results}"
                            )
                            self.logging_manager.log_info(
                                f"[PRESET-CHOICE-DEBUG] text_from_B_corrected: '{text_from_B_corrected}'"
                            )
                            self.logging_manager.log_info(
                                "Preset 'choice' (fallback): Area B text (after correction or raw) is empty or Area B not found in OCR results."
                            )

                        if (
                            text_to_translate_override is not None
                            and text_to_translate_override.strip()
                        ):
                            combined_text = text_to_translate_override
                            final_dialogue_type = dt_choice
                        elif not combined_text and processed_results_for_fallback:
                            combined_text = " ".join(
                                [
                                    self.text_corrector.correct_text(t[1]).strip()
                                    for t in processed_results_for_fallback
                                    if t[1].strip()
                                ]
                            )
                            self.logging_manager.log_info(
                                f"Preset 'choice' (fallback): No override from B, combined all fallback results: '{combined_text[:100]}...'"
                            )
                            if combined_text:
                                final_dialogue_type = dt_choice
                            else:
                                final_dialogue_type = dt_unknown
                                self.logging_manager.log_info(
                                    "Preset 'choice' (fallback): Combined all results is empty."
                                )

                    elif current_preset_role == "lore":
                        self.logging_manager.log_info(
                            "Building combined_text for 'lore' preset."
                        )
                        for area_fb, text_fb_raw_ocr in processed_results_for_fallback:
                            if area_fb == "C":
                                combined_text = self.text_corrector.correct_text(
                                    text_fb_raw_ocr
                                ).strip()
                                break
                        if combined_text:
                            final_dialogue_type = dt_narrator
                        else:
                            final_dialogue_type = dt_unknown
                        self.logging_manager.log_info(
                            f"'lore' preset: combined_text='{combined_text[:100]}...', type: {final_dialogue_type}"
                        )

                    elif current_preset_role == "dialog":
                        self.logging_manager.log_info(
                            "Building combined_text for 'dialog' preset."
                        )
                        if was_detected_as_choice_original_method:
                            self.logging_manager.log_info(
                                "'dialog' preset: Detected as choice by original method (using raw Area B text)."
                            )
                            if raw_message_part_for_choice_check:
                                combined_text = raw_message_part_for_choice_check
                                final_dialogue_type = dt_choice
                                self.logging_manager.log_info(
                                    f"'dialog' preset (is choice by B): using RAW text from B for combined_text: '{combined_text[:100]}...'"
                                )
                            else:
                                self.logging_manager.log_warning(
                                    "'dialog' preset (is choice by B): Raw Area B text was empty. Cannot form combined_text."
                                )
                                combined_text = ""
                                final_dialogue_type = dt_unknown
                        else:
                            self.logging_manager.log_info(
                                "'dialog' preset: Not detected as choice by original method. Processing A/B pairing."
                            )
                            name_part_dialog = ""
                            message_part_dialog = ""
                            found_name_dialog = False
                            found_message_dialog = False
                            for (
                                area_fb,
                                text_fb_raw_ocr,
                            ) in processed_results_for_fallback:
                                if area_fb == "A":
                                    text_fb_corrected_A = (
                                        self.text_corrector.correct_text(
                                            text_fb_raw_ocr
                                        ).strip()
                                    )
                                    if text_fb_corrected_A:
                                        name_part_dialog = text_fb_corrected_A
                                        found_name_dialog = True
                                elif area_fb == "B":
                                    message_part_dialog = (
                                        self.text_corrector.correct_text(
                                            text_fb_raw_ocr
                                        ).strip()
                                    )
                                    if message_part_dialog:
                                        found_message_dialog = True
                            self.logging_manager.log_info(
                                f"'dialog' preset (A/B pairing): found_A={found_name_dialog} (Name: '{name_part_dialog}'), found_B={found_message_dialog} (Msg: '{message_part_dialog[:50]}...')"
                            )
                            if found_name_dialog and found_message_dialog:
                                speaker_in_B, content_in_B, _ = (
                                    self.text_corrector.split_speaker_and_content(
                                        message_part_dialog
                                    )
                                )
                                if speaker_in_B:
                                    combined_text = f"{speaker_in_B}: {content_in_B}"
                                    final_dialogue_type = dt_speaker_in_text
                                else:
                                    combined_text = (
                                        f"{name_part_dialog}: {message_part_dialog}"
                                    )
                                    final_dialogue_type = dt_normal
                                waiting_for_message = False
                                waiting_for_name = False
                                temp_name = None
                                temp_message = None
                                self.logging_manager.log_info(
                                    f"'dialog' preset (A+B): combined_text='{combined_text[:100]}...', type: {final_dialogue_type}"
                                )
                            elif not found_name_dialog and found_message_dialog:
                                self.logging_manager.log_info(
                                    "'dialog' preset (A/B pairing): Area A empty, Area B has text. Processing B directly."
                                )
                                
                                # Enhanced choice detection for Area B when Area A is empty
                                # This handles FFXIV choice dialogs that appear only in Area B
                                is_potential_choice = False
                                
                                # Check if B contains choice indicators even without the standard "What will you say?" header
                                choice_indicators = [
                                    # Standard patterns
                                    "what will you say",
                                    "choose your response",
                                    "select an option",
                                    # Numbered patterns (common in FFXIV)
                                    r"^\d+\.",  # Lines starting with numbers (1., 2., etc.)
                                    r"^[►▶•◆]",  # Lines starting with bullet points
                                    # Multiple short lines pattern (typical choice format)
                                ]
                                
                                message_lower = message_part_dialog.lower()
                                lines_in_message = message_part_dialog.split('\n')
                                
                                # Check for choice patterns
                                for pattern in choice_indicators:
                                    if isinstance(pattern, str):
                                        if pattern in message_lower:
                                            is_potential_choice = True
                                            self.logging_manager.log_info(
                                                f"Choice indicator found in B: '{pattern}'"
                                            )
                                            break
                                    else:
                                        for line in lines_in_message:
                                            if re.match(pattern, line.strip()):
                                                is_potential_choice = True
                                                self.logging_manager.log_info(
                                                    f"Choice pattern matched in B: '{pattern}' on line: '{line}'"
                                                )
                                                break
                                
                                # Additional heuristic: Multiple short lines (2-4 lines) often indicate choices
                                if not is_potential_choice and 2 <= len(lines_in_message) <= 4:
                                    # Check if lines are relatively short (typical for choices)
                                    avg_line_length = sum(len(line.strip()) for line in lines_in_message) / len(lines_in_message)
                                    if avg_line_length < 50:  # Short lines typical for choices
                                        is_potential_choice = True
                                        self.logging_manager.log_info(
                                            f"Potential choice detected: {len(lines_in_message)} short lines (avg length: {avg_line_length:.1f})"
                                        )
                                
                                if is_potential_choice:
                                    # Process as choice dialogue
                                    combined_text = message_part_dialog
                                    final_dialogue_type = dt_choice
                                    self.logging_manager.log_info(
                                        f"'dialog' preset (A empty, B has text - CHOICE DETECTED): combined_text='{combined_text[:100]}...', type: CHOICE"
                                    )
                                else:
                                    # Process normally
                                    speaker_in_B, content_in_B, _ = (
                                        self.text_corrector.split_speaker_and_content(
                                            message_part_dialog
                                        )
                                    )
                                    if speaker_in_B:
                                        combined_text = f"{speaker_in_B}: {content_in_B}"
                                        final_dialogue_type = dt_speaker_in_text
                                    else:
                                        combined_text = message_part_dialog
                                        final_dialogue_type = dt_dialog_without_name
                                    self.logging_manager.log_info(
                                        f"'dialog' preset (A empty, B has text): combined_text='{combined_text[:100]}...', type: {final_dialogue_type}"
                                    )
                                
                                waiting_for_message = False
                                waiting_for_name = False
                                temp_name = None
                                temp_message = None
                            elif found_name_dialog and not found_message_dialog:
                                current_time_wait_name = time.time()
                                if (
                                    waiting_for_message
                                    and temp_name == name_part_dialog
                                ):
                                    if current_time_wait_name - self.last_name_time < (
                                        hasattr(self, "name_wait_timeout")
                                        and self.name_wait_timeout
                                        or 0.7
                                    ):
                                        self.logging_manager.log_info(
                                            f"'dialog' preset (A has text, B empty): Still waiting for message for '{temp_name}'. Skipping cycle."
                                        )
                                        is_processing = False
                                        continue
                                    else:
                                        self.logging_manager.log_info(
                                            f"'dialog' preset (A has text, B empty): Timeout waiting for message for '{temp_name}'. Skipping cycle."
                                        )
                                        waiting_for_message = False
                                        temp_name = None
                                        is_processing = False
                                        continue
                                else:
                                    temp_name = name_part_dialog
                                    self.last_name_time = current_time_wait_name
                                    waiting_for_message = True
                                    self.logging_manager.log_info(
                                        f"'dialog' preset (A has text, B empty): Found speaker '{temp_name}', starting to wait for message. Skipping cycle."
                                    )
                                    is_processing = False
                                    continue
                            else:
                                self.logging_manager.log_info(
                                    "'dialog' preset (A/B pairing): Both Area A and B are effectively empty. Skipping cycle."
                                )
                                is_processing = False
                                continue
                    else:
                        self.logging_manager.log_info(
                            "Building combined_text for 'custom' preset."
                        )
                        name_part_custom = ""
                        message_part_custom = ""
                        c_part_custom = ""
                        raw_text_B_for_custom_choice_check = ""
                        for area_fb, text_fb_raw_ocr in processed_results_for_fallback:
                            text_fb_corrected = self.text_corrector.correct_text(
                                text_fb_raw_ocr
                            ).strip()
                            if area_fb == "A":
                                name_part_custom = text_fb_corrected
                            elif area_fb == "B":
                                message_part_custom = text_fb_corrected
                                raw_text_B_for_custom_choice_check = (
                                    text_fb_raw_ocr.strip()
                                )
                            elif area_fb == "C":
                                c_part_custom = text_fb_corrected
                        if message_part_custom and self.is_choice_dialogue(
                            raw_text_B_for_custom_choice_check
                        ):
                            combined_text = raw_text_B_for_custom_choice_check
                            final_dialogue_type = dt_choice
                            was_detected_as_choice_original_method = True
                            self.logging_manager.log_info(
                                f"'custom' preset: Detected as choice (raw B). combined_text='{combined_text[:100]}...'"
                            )
                        elif name_part_custom and message_part_custom:
                            combined_text = f"{name_part_custom}: {message_part_custom}"
                            final_dialogue_type = dt_normal
                        elif message_part_custom:
                            speaker, content, _ = (
                                self.text_corrector.split_speaker_and_content(
                                    message_part_custom
                                )
                            )
                            if speaker:
                                combined_text = f"{speaker}: {content}"
                                final_dialogue_type = dt_speaker_in_text
                            else:
                                combined_text = message_part_custom
                                final_dialogue_type = dt_dialog_without_name
                        elif c_part_custom:
                            combined_text = c_part_custom
                            final_dialogue_type = dt_narrator
                        elif name_part_custom:
                            self.logging_manager.log_info(
                                "'custom' preset: Only Area A has text. Waiting for B or C. Skipping cycle."
                            )
                            is_processing = False
                            continue
                        else:
                            self.logging_manager.log_info(
                                "'custom' preset: No usable text in A, B, or C. Skipping cycle."
                            )
                            is_processing = False
                            continue
                        if combined_text:
                            self.logging_manager.log_info(
                                f"'custom' preset: combined_text='{combined_text[:100]}...', type: {final_dialogue_type}"
                            )

                # ✨ Apply choice_dialogue_type_override if set by choice preset
                if choice_dialogue_type_override is not None:
                    final_dialogue_type = choice_dialogue_type_override
                    self.logging_manager.log_info(
                        f"[PRESET-CHOICE-DEBUG] ✅ Applied choice_dialogue_type_override: final_dialogue_type = {final_dialogue_type}"
                    )

                self.logging_manager.log_info(
                    f"Final combined_text before translation check: '{combined_text[:100]}...' (Type: {final_dialogue_type}, StructurallyDetectedChoice: {was_structurally_detected_as_choice})"
                )

                if combined_text and combined_text.strip():
                    # ✨ Apply choice_dialogue_type_override if set by choice preset
                    if choice_dialogue_type_override is not None:
                        final_dialogue_type = choice_dialogue_type_override
                        self.logging_manager.log_info(
                            f"[PRESET-CHOICE-DEBUG] ✅ Applied choice_dialogue_type_override: final_dialogue_type = {final_dialogue_type}"
                        )

                    # ใช้ค่า cached ถ้ามี หรือคำนวณใหม่
                    effective_was_detected_as_choice = (
                        was_structurally_detected_as_choice
                        or (
                            not was_structurally_detected_as_choice
                            and final_dialogue_type == dt_choice
                            and was_detected_as_choice_original_method
                        )
                        or (
                            use_cached_choice_detection and self.last_detected_as_choice
                        )
                    )

                    # ✨ เพิ่มการตรวจสอบสำหรับ choice preset เฉพาะ
                    current_preset_num_for_check = self.settings.get(
                        "current_preset", 1
                    )
                    current_preset_role_for_check = self.settings.get_preset_role(
                        current_preset_num_for_check
                    )
                    if current_preset_role_for_check == "choice":
                        effective_was_detected_as_choice = (
                            True  # Force choice detection สำหรับ choice preset
                        )
                        self.logging_manager.log_info(
                            f"[PRESET-CHOICE-DEBUG] ✅ Forced effective_was_detected_as_choice = True for choice preset"
                        )

                    self.logging_manager.log_info(f"DEBUG Choice Detection Values:")
                    self.logging_manager.log_info(
                        f"  - was_structurally_detected_as_choice: {was_structurally_detected_as_choice}"
                    )
                    self.logging_manager.log_info(
                        f"  - final_dialogue_type == dt_choice: {final_dialogue_type == dt_choice}"
                    )
                    self.logging_manager.log_info(
                        f"  - was_detected_as_choice_original_method: {was_detected_as_choice_original_method}"
                    )
                    self.logging_manager.log_info(
                        f"  - use_cached_choice_detection: {use_cached_choice_detection}"
                    )
                    self.logging_manager.log_info(
                        f"  - self.last_detected_as_choice: {getattr(self, 'last_detected_as_choice', 'N/A')}"
                    )
                    self.logging_manager.log_info(
                        f"Effective was_detected_as_choice for UI formatting: {effective_was_detected_as_choice}"
                    )
                    similarity_processed = self.text_similarity(
                        combined_text, self.last_text
                    )
                    basic_should_translate = (
                        similarity_processed < 0.85 or self.force_next_translation
                    )

                    # 🛡️ SAFETY NET: ตรวจสอบ dialog readiness ก่อนส่ง API (จุดสุดท้าย)
                    if basic_should_translate:
                        dialog_readiness = self._validate_combined_text_readiness(
                            combined_text, self.current_area
                        )
                        should_translate = basic_should_translate and dialog_readiness

                        if basic_should_translate and not dialog_readiness:
                            self.logging_manager.log_info(
                                "SAFETY NET: Translation blocked - missing speaker in dialog preset"
                            )
                    else:
                        should_translate = basic_should_translate
                    self.logging_manager.log_info(
                        f"Similarity with last_text ('{self.last_text[:50]}...'): {similarity_processed:.2f}, force_next: {self.force_next_translation}, -> should_translate: {should_translate}"
                    )

                    if should_translate:
                        if self.translator:
                            self._update_status_line(
                                f"Translating: {combined_text[:30]}..."
                            )
                            translated_text_raw = ""
                            try:
                                self.logging_manager.log_info(
                                    f"Sending to translator (Role: {current_preset_role}, Type: {final_dialogue_type}): '{combined_text[:70]}...'"
                                )
                                # ใช้ translate_choice() เมื่อตรวจจับเป็น choice dialogue
                                current_preset_num_for_check = self.settings.get(
                                    "current_preset", 1
                                )
                                current_preset_role_for_check = (
                                    self.settings.get_preset_role(
                                        current_preset_num_for_check
                                    )
                                )
                                is_lore_preset_active = (
                                    current_preset_role_for_check == "lore"
                                )

                                # ใช้ translate_choice() เมื่อตรวจจับเป็น choice dialogue
                                if effective_was_detected_as_choice:
                                    self.logging_manager.log_info(
                                        "Using translate_choice() for detected choice dialogue"
                                    )
                                    translated_text_raw = (
                                        self.translator.translate_choice(combined_text)
                                    )
                                else:
                                    # <<-- แก้ไขบรรทัดนี้
                                    translated_text_raw = self.translator.translate(
                                        combined_text,
                                        is_lore_text=is_lore_preset_active,
                                    )
                            except Exception as translate_error:
                                self.logging_manager.log_error(
                                    f"Error during translation call: {translate_error}"
                                )
                                translated_text_raw = f"[Translation Error]"

                            if (
                                translated_text_raw
                                and len(translated_text_raw.strip()) > 0
                                and not translated_text_raw.startswith("[Error")
                            ):
                                self.logging_manager.log_info(
                                    f"DEBUG: Translation successful. effective_was_detected_as_choice={effective_was_detected_as_choice}"
                                )
                                self.logging_manager.log_info(
                                    f"DEBUG: translated_text_raw length={len(translated_text_raw)}, content: '{translated_text_raw[:100]}...'"
                                )

                                final_text_for_ui = translated_text_raw
                                if effective_was_detected_as_choice:
                                    self.logging_manager.log_info(
                                        f"Choice translation complete - formatting for UI: '{translated_text_raw[:100]}...'"
                                    )

                                    # ลบ prefix ที่อาจเหลือจาก AI
                                    cleaned_result = translated_text_raw

                                    # **แปลง <NL> tags เป็น newline ก่อนประมวลผล**
                                    cleaned_result = cleaned_result.replace(
                                        "<NL>", "\n"
                                    )
                                    # เพิ่มการแปลงรูปแบบ newline อื่นๆ ด้วย
                                    cleaned_result = cleaned_result.replace("\\n", "\n")
                                    cleaned_result = cleaned_result.replace(
                                        "\r\n", "\n"
                                    )
                                    cleaned_result = cleaned_result.replace("\r", "\n")
                                    # ลบ newlines ซ้ำ
                                    cleaned_result = re.sub(
                                        r"\n+", "\n", cleaned_result
                                    )
                                    self.logging_manager.log_info(
                                        f"Converted <NL> tags to newlines: '{cleaned_result[:100]}...'"
                                    )
                                    self.logging_manager.log_info(
                                        f"Debug newlines count: {cleaned_result.count(chr(10))} newlines found"
                                    )

                                    # **แทนที่ header ที่ Gemini แปลมาด้วย header ที่ต้องการ (fix ตายตัว)**
                                    possible_headers = [
                                        # ภาษาไทย - เพิ่มทุกรูปแบบที่เป็นไปได้
                                        "จะว่ายังไงดี?",  # <- เพิ่มใหม่: คำแปลที่พบในภาพ
                                        "จะว่ายังไงดี",  # <- เพิ่มใหม่: แบบไม่มีเครื่องหมายคำถาม
                                        "จะพูดอะไรดี?",  # <- เพิ่มใหม่
                                        "จะพูดอะไรดี",  # <- เพิ่มใหม่
                                        "จะว่าอะไรดี?",  # <- เพิ่มใหม่
                                        "จะว่าอะไรดี",  # <- เพิ่มใหม่
                                        # รูปแบบเดิมที่มีอยู่แล้ว
                                        "ท่านจะว่าอย่างไร?",
                                        "ท่านจะพูดอะไร?",
                                        "ท่านจะกล่าวอย่างไร?",
                                        "คุณจะว่าอย่างไร?",
                                        "คุณจะพูดอะไร?",
                                        "คุณจะกล่าวอย่างไร?",
                                        "เจ้าจะว่าอย่างไร?",
                                        "เจ้าจะพูดอะไร?",
                                        "จะว่าอย่างไร?",
                                        "จะพูดอะไร?",
                                        "พูดอะไรดี?",
                                        "ว่าอย่างไร?",
                                        # ภาษาอังกฤษ (กรณี AI ไม่แปล)
                                        "What will you say?",
                                        "What will you say",
                                        "Whatwillyousay",
                                    ]

                                    for old_header in possible_headers:
                                        if cleaned_result.startswith(old_header):
                                            cleaned_result = cleaned_result.replace(
                                                old_header, "คุณจะพูดว่าอย่างไร?", 1
                                            )
                                            self.logging_manager.log_info(
                                                f"Replaced header '{old_header}' with 'คุณจะพูดว่าอย่างไร?'"
                                            )
                                            break

                                    # **ตรวจสอบว่าข้อความขึ้นต้นด้วย header ที่ต้องการหรือไม่**
                                    if not cleaned_result.startswith("คุณจะพูดว่าอย่างไร?"):
                                        # ถ้าไม่ใช่ ให้เพิ่ม header เข้าไป
                                        cleaned_result = (
                                            "คุณจะพูดว่าอย่างไร?\n" + cleaned_result
                                        )
                                        self.logging_manager.log_info(
                                            "Added default header to beginning of text"
                                        )
                                    unwanted_prefixes = [
                                        "thai:",
                                        "translation:",
                                        "แปล:",
                                        "ภาษาไทย:",
                                        "thai translation:",
                                        "translated output:",
                                        "output:",
                                        "ผลการแปล:",
                                        "คำแปล:",
                                        "translated:",
                                        "result:",
                                    ]
                                    for prefix in unwanted_prefixes:
                                        if cleaned_result.lower().startswith(
                                            prefix.lower()
                                        ):
                                            cleaned_result = cleaned_result[
                                                len(prefix) :
                                            ].strip()
                                            self.logging_manager.log_info(
                                                f"Removed prefix: {prefix}"
                                            )
                                            break

                                    # Log ผลลัพธ์หลังทำความสะอาด
                                    self.logging_manager.log_info(
                                        f"Cleaned result: '{cleaned_result[:100]}...'"
                                    )

                                    # สร้าง format ที่ UI รู้จักสำหรับ choice dialogue
                                    lines = cleaned_result.split("\n")
                                    formatted_choices = []

                                    # วิเคราะห์เพื่อแยก header และ choices อย่างละเอียดมากขึ้น
                                    choices_start_index = 0
                                    header_found = ""

                                    # **Debug: แสดง lines ที่แยกได้**
                                    self.logging_manager.log_info(
                                        f"Lines from cleaned_result split: {len(lines)} lines found: {lines[:5]}"
                                    )  # แสดงแค่ 5 บรรทัดแรก

                                    # ถ้าบรรทัดแรกเป็น header (มีคำถาม) ให้ข้าม
                                    if lines and len(lines) > 1:
                                        first_line = lines[0].strip()
                                        # ตรวจสอบ header ที่หลากหลายมากขึ้น
                                        header_keywords = [
                                            "พูด",
                                            "กล่าว",
                                            "ตอบ",
                                            "จะ",
                                            "คุณ",
                                            "ท่าน",
                                            "เจ้า",
                                            "ว่า",
                                            "อย่างไร",
                                            "ดี",
                                            "ไร",
                                        ]

                                        # **เพิ่มเงื่อนไขการตรวจสอบ header**
                                        is_header = (
                                            "?" in first_line
                                            or any(
                                                keyword in first_line
                                                for keyword in header_keywords
                                            )
                                            or len(first_line.split()) <= 10  # บรรทัดสั้น
                                            or first_line.count(" ") <= 8  # คำน้อย
                                        )

                                        self.logging_manager.log_info(
                                            f"First line analysis: '{first_line}' -> is_header: {is_header}"
                                        )

                                        if is_header:
                                            choices_start_index = 1
                                            header_found = first_line
                                            self.logging_manager.log_info(
                                                f"Found header line: '{first_line}', choices start at index {choices_start_index}"
                                            )
                                        else:
                                            self.logging_manager.log_info(
                                                f"First line doesn't look like header: '{first_line}', treating as choice"
                                            )

                                        # กรณีพิเศษ: header และ choice แรกอยู่บรรทัดเดียวกัน (เช่น "คำถาม choice1")
                                        if (
                                            not is_header
                                            and len(first_line.split()) > 10
                                        ):  # บรรทัดยาวมาก อาจรวม header+choice
                                            # พยายามแยก header ออกจาก choice
                                            potential_splits = [
                                                "!",
                                                "?",
                                                "นะ",
                                                "เหรอ",
                                                "มั้ย",
                                                "หรือ",
                                                "ดี",
                                                "ไร",
                                            ]
                                            for split_word in potential_splits:
                                                if split_word in first_line:
                                                    parts = first_line.split(
                                                        split_word, 1
                                                    )
                                                    if (
                                                        len(parts) == 2
                                                        and len(parts[0].strip()) <= 50
                                                    ):  # header ไม่ควรยาวเกิน 50 ตัวอักษร
                                                        header_found = (
                                                            parts[0].strip()
                                                            + split_word
                                                        )
                                                        # เอาส่วนที่เหลือมาเป็น choice แรก
                                                        remaining = parts[1].strip()
                                                        if remaining:
                                                            lines.insert(
                                                                1, remaining
                                                            )  # แทรกเป็นบรรทัดที่ 2
                                                        lines[0] = (
                                                            header_found  # แทนที่บรรทัดแรกด้วย header
                                                        )
                                                        choices_start_index = 1
                                                        self.logging_manager.log_info(
                                                            f"Split combined line - Header: '{header_found}', First choice: '{remaining}'"
                                                        )
                                                        break
                                    else:
                                        # ถ้ามีบรรทัดเดียว หรือไม่มีบรรทัด ให้ใช้ header เริ่มต้น
                                        header_found = "คุณจะพูดว่าอย่างไร?"
                                        if lines:
                                            choices_start_index = (
                                                0  # ใช้ทั้งหมดเป็น choices
                                            )
                                        self.logging_manager.log_info(
                                            f"Using default header for single/empty lines. Lines count: {len(lines)}, choices_start_index: {choices_start_index}"
                                        )

                                    # รวบรวม choices
                                    for i in range(choices_start_index, len(lines)):
                                        line = lines[i].strip()
                                        if line:  # ข้าม empty lines
                                            # ลบเครื่องหมายหรือหมายเลขข้อที่อาจมีอยู่หน้า choice
                                            cleaned_choice = line
                                            # ลบหมายเลขข้อ เช่น "1.", "2)", "(1)"
                                            cleaned_choice = re.sub(
                                                r"^[\(\[]?\d+[\)\]\.]?\s*",
                                                "",
                                                cleaned_choice,
                                            )
                                            # ลบ bullet points
                                            cleaned_choice = re.sub(
                                                r"^[-•·*]\s*", "", cleaned_choice
                                            )

                                            if cleaned_choice:
                                                formatted_choices.append(cleaned_choice)
                                                self.logging_manager.log_info(
                                                    f"Added choice from line {i}: '{cleaned_choice[:50]}...'"
                                                )

                                    self.logging_manager.log_info(
                                        f"Total formatted_choices found: {len(formatted_choices)}"
                                    )

                                    # **ถ้าไม่มี choices จากการแยกบรรทัด ลองแยกด้วยเครื่องหมายวรรคตอน**
                                    if not formatted_choices and cleaned_result:
                                        self.logging_manager.log_info(
                                            "No choices from line splitting, trying punctuation splitting"
                                        )

                                        # แยกด้วยเครื่องหมายสิ้นสุดประโยค
                                        punct_split = re.split(
                                            r"(?<=[.!?])\s+", cleaned_result
                                        )
                                        if len(punct_split) > 1:
                                            # บรรทัดแรกเป็น header ที่เหลือเป็น choices
                                            header_found = (
                                                punct_split[0].strip()
                                                if not header_found
                                                else header_found
                                            )
                                            for sentence in punct_split[1:]:
                                                sentence = sentence.strip()
                                                if sentence:
                                                    formatted_choices.append(sentence)
                                                    self.logging_manager.log_info(
                                                        f"Added choice from punctuation split: '{sentence}'"
                                                    )

                                        # ถ้ายังไม่ได้ ลองแยกด้วยคำที่บ่งบอกถึงตัวเลือก
                                        if not formatted_choices:
                                            choice_indicators = [
                                                "เรา",
                                                "ดังนั้น",
                                                "แต่",
                                                "หรือ",
                                                "และ",
                                                "ถ้า",
                                                "เพราะ",
                                            ]
                                            for indicator in choice_indicators:
                                                if (
                                                    cleaned_result.count(indicator) >= 2
                                                ):  # มีมากกว่า 1 ครั้ง
                                                    parts = cleaned_result.split(
                                                        indicator
                                                    )
                                                    if len(parts) > 2:  # ได้หลายส่วน
                                                        header_found = (
                                                            parts[0].strip()
                                                            if not header_found
                                                            else header_found
                                                        )
                                                        for i, part in enumerate(
                                                            parts[1:], 1
                                                        ):
                                                            choice_text = (
                                                                indicator + part.strip()
                                                            )
                                                            if choice_text.strip():
                                                                formatted_choices.append(
                                                                    choice_text
                                                                )
                                                                self.logging_manager.log_info(
                                                                    f"Added choice from indicator '{indicator}': '{choice_text}'"
                                                                )
                                                        break

                                    # **ถ้ายังไม่ได้เลย ใช้วิธีสุดท้าย: แยกตามความยาว**
                                    if not formatted_choices and cleaned_result:
                                        self.logging_manager.log_info(
                                            "No choices from any method, splitting by length"
                                        )
                                        words = cleaned_result.split()
                                        if len(words) > 20:  # ถ้ามีคำเยอะ
                                            # แยกเป็นชิ้นๆ ประมาณ 10-15 คำต่อชิ้น
                                            chunk_size = 12
                                            chunks = [
                                                " ".join(words[i : i + chunk_size])
                                                for i in range(
                                                    0, len(words), chunk_size
                                                )
                                            ]
                                            if len(chunks) >= 2:
                                                header_found = (
                                                    chunks[0]
                                                    if not header_found
                                                    else header_found
                                                )
                                                for chunk in chunks[1:]:
                                                    if chunk.strip():
                                                        formatted_choices.append(
                                                            chunk.strip()
                                                        )
                                                        self.logging_manager.log_info(
                                                            f"Added choice from length split: '{chunk[:50]}...'"
                                                        )

                                    # สร้างข้อความที่ UI รู้จักได้
                                    if formatted_choices:
                                        # **บังคับใช้ header เริ่มต้นเสมอ (fix ตายตัว)**
                                        display_header = "คุณจะพูดว่าอย่างไร?"
                                        final_text_for_ui = (
                                            display_header
                                            + "\n"
                                            + "\n".join(formatted_choices)
                                        )
                                        self.logging_manager.log_info(
                                            f"SUCCESS: Formatted {len(formatted_choices)} choices for UI with FIXED header"
                                        )
                                        self.logging_manager.log_info(
                                            f"Choices: {formatted_choices}"
                                        )
                                    else:
                                        # ถ้าไม่มี choices ที่ชัดเจน ลองแยกด้วยวิธีอื่น
                                        self.logging_manager.log_warning(
                                            "FALLBACK: No choices found after standard parsing, trying alternative method"
                                        )

                                        # ลองแยกด้วยเครื่องหมายวรรคตอนอื่นๆ
                                        alternative_splits = re.split(
                                            r"[.!?]\s+", cleaned_result
                                        )
                                        if len(alternative_splits) > 1:
                                            alt_choices = [
                                                s.strip()
                                                for s in alternative_splits
                                                if s.strip()
                                            ]
                                            if alt_choices:
                                                # **บังคับใช้ header เริ่มต้นเสมอ**
                                                final_text_for_ui = (
                                                    "คุณจะพูดว่าอย่างไร?\n"
                                                    + "\n".join(alt_choices)
                                                )
                                                self.logging_manager.log_info(
                                                    f"FALLBACK SUCCESS: Alternative parsing found {len(alt_choices)} choices"
                                                )
                                            else:
                                                final_text_for_ui = (
                                                    "คุณจะพูดว่าอย่างไร?\n" + cleaned_result
                                                )
                                                self.logging_manager.log_info(
                                                    "FALLBACK: Using full cleaned result"
                                                )
                                        else:
                                            # ใช้ทั้งก้อนถ้าแยกไม่ได้ แต่ยังคงใส่ header choice
                                            final_text_for_ui = (
                                                "คุณจะพูดว่าอย่างไร?\n" + cleaned_result
                                            )
                                            self.logging_manager.log_info(
                                                "FALLBACK: No clear choices found, using full cleaned result with FIXED choice header"
                                            )

                                    self.logging_manager.log_info(
                                        f"Final formatted choice text for UI (length: {len(final_text_for_ui)}, newlines: {final_text_for_ui.count(chr(10))}): '{final_text_for_ui[:150]}...'"
                                    )

                                if (
                                    final_text_for_ui != last_translated_text
                                    or self.force_next_translation
                                ):
                                    self._update_status_line("✓ Translation updated")
                                    self.root.after(
                                        0,
                                        # <<-- แก้ไข lambda ในบรรทัดนี้
                                        lambda txt=final_text_for_ui: self.translated_ui.update_text(
                                            txt, is_lore_text=is_lore_preset_active
                                        ),
                                    )
                                    if (
                                        hasattr(self, "translated_logs_instance")
                                        and self.translated_logs_instance
                                    ):
                                        # ส่ง force translate flag และ lore mode flag ไปยัง translated_logs
                                        self.translated_logs_instance.add_message(
                                            final_text_for_ui,
                                            is_force_retranslation=self.force_next_translation,
                                            is_lore_text=is_lore_preset_active,  # <<-- เพิ่มบรรทัดนี้
                                        )
                                    last_translated_text = final_text_for_ui
                                    self.last_translation = final_text_for_ui
                                    self.last_text = combined_text
                                    self.last_translation_time = current_time
                                    self.logging_manager.log_info(
                                        f"UI Updated. last_text set to: '{self.last_text[:70]}...'"
                                    )
                                    if self.force_next_translation:
                                        self.logging_manager.log_info(
                                            "Resetting force_next_translation after successful forced translation."
                                        )
                                        self.force_next_translation = False
                                    self._logged_skipping_translation = False
                                else:
                                    self._update_status_line("Same translation result.")
                                    self.logging_manager.log_info(
                                        "Translation result is the same as last time. Not updating UI."
                                    )
                                    if self.force_next_translation:
                                        self.logging_manager.log_info(
                                            "Resetting force_next_translation as translated text was same as previous (even though forced)."
                                        )
                                        self.force_next_translation = False
                            else:
                                self._update_status_line(
                                    "Translation failed or returned empty."
                                )
                                self.logging_manager.log_warning(
                                    "Translation failed or returned empty text."
                                )
                                if self.force_next_translation:
                                    self.logging_manager.log_info(
                                        "Resetting force_next_translation due to translation failure/empty result."
                                    )
                                    self.force_next_translation = False
                        else:
                            self._update_status_line("Translator not available.")
                            self.logging_manager.log_warning(
                                "Translator not available for translation."
                            )
                            if self.force_next_translation:
                                self.logging_manager.log_info(
                                    "Resetting force_next_translation as translator is not available."
                                )
                                self.force_next_translation = False
                            time.sleep(1)
                    else:
                        self._update_status_line(
                            "Skipping translation (text similar and not forced)."
                        )
                        self.logging_manager.log_info(
                            "Skipping translation: Text is too similar to previous and not forced."
                        )
                else:
                    self._update_status_line("No text to translate.")
                    self.logging_manager.log_info(
                        "No combined_text was formed. Skipping translation cycle."
                    )
                    if self.force_next_translation:
                        self.logging_manager.log_info(
                            "Resetting force_next_translation because combined_text was empty."
                        )
                        self.force_next_translation = False

                is_processing = False

            except Exception as e:
                self._update_status_line(f"Loop Error: {str(e)[:50]}...")
                self.logging_manager.log_error(f"Translation loop error: {e}")

                self.logging_manager.log_error(traceback.format_exc())
                is_processing = False
                if (
                    hasattr(self, "force_next_translation")
                    and self.force_next_translation
                ):
                    self.logging_manager.log_info(
                        "Resetting force_next_translation due to an exception in the loop."
                    )
                    self.force_next_translation = False
                time.sleep(0.5)

    def _has_speaker_in_message(self, text):
        """
        ตรวจสอบว่าข้อความมีชื่อผู้พูดหรือไม่ (รวมชื่อที่ไม่มีในฐานข้อมูล)

        Args:
            text: ข้อความที่ต้องการตรวจสอบ

        Returns:
            bool: True ถ้ามีชื่อผู้พูด, False ถ้าไม่มี
        """
        try:
            if not text or not text.strip():
                return False

            # วิธีที่ 1: ใช้ text_corrector (สำหรับชื่อที่รู้จัก)
            speaker, content, dialogue_type = (
                self.text_corrector.split_speaker_and_content(text)
            )
            if speaker is not None and len(speaker.strip()) > 0:
                self.logging_manager.log_info(
                    f"Speaker detected by text_corrector: '{speaker}'"
                )
                return True

            # วิธีที่ 2: Basic pattern matching (สำหรับชื่อที่ไม่รู้จัก)
            # ตรวจสอบรูปแบบ "ชื่อ: ข้อความ" แบบพื้นฐาน
            basic_patterns = [": ", " - ", " – ", " : "]
            for pattern in basic_patterns:
                if pattern in text:
                    parts = text.split(pattern, 1)
                    if len(parts) == 2:
                        potential_speaker = parts[0].strip()
                        content = parts[1].strip()

                        # ตรวจสอบว่า potential_speaker ดูเป็นชื่อหรือไม่
                        if self._looks_like_speaker_name(potential_speaker):
                            self.logging_manager.log_info(
                                f"Speaker detected by basic pattern: '{potential_speaker}'"
                            )
                            return True

            self.logging_manager.log_info(f"No speaker found in text: '{text[:50]}...'")
            return False

        except Exception as e:
            self.logging_manager.log_error(f"Error in _has_speaker_in_message: {e}")
            return False  # กรณีเกิดข้อผิดพลาด ถือว่าไม่มีชื่อผู้พูด

    def _looks_like_speaker_name(self, text):
        """
        ตรวจสอบว่าข้อความดูเหมือนชื่อผู้พูดหรือไม่ (แบบพื้นฐาน)

        Args:
            text: ข้อความที่ต้องการตรวจสอบ

        Returns:
            bool: True ถ้าดูเหมือนชื่อผู้พูด
        """
        if not text or not text.strip():
            return False

        text = text.strip()

        # เกณฑ์พื้นฐาน
        if len(text) < 2 or len(text) > 30:  # ความยาวต้องสมเหตุสมผล
            return False

        # ไม่ควรมีตัวเลขเยอะ
        digit_count = sum(1 for c in text if c.isdigit())
        if digit_count > len(text) // 2:  # มากกว่าครึ่งเป็นตัวเลข
            return False

        # ไม่ควรมีสัญลักษณ์แปลกๆ เยอะ
        special_chars = sum(
            1 for c in text if not (c.isalnum() or c.isspace() or c in "'-_.")
        )
        if special_chars > 2:
            return False

        # ผ่านเกณฑ์พื้นฐาน
        return True

    def _is_dialog_preset(self, current_preset):
        """
        ตรวจสอบว่า preset ปัจจุบันเป็น dialog preset หรือไม่

        Args:
            current_preset: preset ปัจจุบัน (อาจเป็น string หรือ list)

        Returns:
            bool: True ถ้าเป็น dialog preset
        """
        try:
            if isinstance(current_preset, list):
                # ถ้าเป็น list ให้ตรวจสอบว่ามี A+B หรือไม่ (โดยปกติ dialog จะเป็น A+B)
                return "A" in current_preset and "B" in current_preset
            elif isinstance(current_preset, str):
                # ถ้าเป็น string ให้ตรวจสอบว่าเป็น A+B pattern หรือไม่
                preset_lower = current_preset.lower()
                return "a" in preset_lower and "b" in preset_lower
            else:
                return False

        except Exception as e:
            self.logging_manager.log_error(f"Error in _is_dialog_preset: {e}")
            return False

    def _validate_combined_text_readiness(self, combined_text, current_preset):
        """
        ตรวจสอบว่า combined_text พร้อมสำหรับการแปลใน dialog preset หรือไม่

        Args:
            combined_text: ข้อความที่รวมแล้ว (อาจมีหรือไม่มีชื่อผู้พูด)
            current_preset: preset ปัจจุบัน

        Returns:
            bool: True ถ้าพร้อมแปล, False ถ้าควรรอ
        """
        try:
            # ✨ CHOICE PRESET SPECIAL HANDLING: Choice preset ไม่ต้องตรวจสอบ dialog readiness
            current_preset_num = self.settings.get("current_preset", 1)
            current_preset_role = self.settings.get_preset_role(current_preset_num)
            if current_preset_role == "choice":
                self.logging_manager.log_info(
                    f"[PRESET-CHOICE-DEBUG] ✅ Choice preset detected - skipping dialog validation"
                )
                return True  # Choice preset เสมอพร้อมแปล

            # ตรวจสอบเฉพาะ dialog preset เท่านั้น
            if not self._is_dialog_preset(current_preset):
                return True  # preset อื่นไม่ต้องตรวจสอบ

            # ตรวจสอบว่ามีชื่อผู้พูดหรือไม่
            has_speaker = self._has_speaker_in_message(combined_text)

            # ถ้าไม่มีชื่อผู้พูด ตรวจสอบว่าเป็น choice หรือไม่
            if not has_speaker:
                if self.is_choice_dialogue(combined_text):
                    self.logging_manager.log_info(
                        "Combined text validation: Choice dialogue detected, proceeding without speaker"
                    )
                    return True  # เป็น choice → พร้อมแปล
                else:
                    self.logging_manager.log_info(
                        f"Combined text validation: Missing speaker in dialog preset. Text: '{combined_text[:50]}...'"
                    )
                    return False  # ไม่มีชื่อ + ไม่ใช่ choice → รอ

            return True  # มีชื่อผู้พูด → พร้อมแปล

        except Exception as e:
            self.logging_manager.log_error(
                f"Error in _validate_combined_text_readiness: {e}"
            )
            return True  # กรณีเกิดข้อผิดพลาด ให้ดำเนินการต่อเพื่อความปลอดภัย

    def _process_normal_dialogue_ab(self, name_part, message_part, current_time):
        """
        ประมวลผลบทสนทนาปกติ A+B พร้อมระบบ fallback ที่ปรับปรุงแล้ว

        Args:
            name_part: ข้อความจากพื้นที่ A (ชื่อตัวละคร)
            message_part: ข้อความจากพื้นที่ B (บทสนทนา)
            current_time: เวลาปัจจุบัน
        """
        try:
            # ตรวจสอบคุณภาพของชื่อที่พบ
            name_quality = 0.0
            if hasattr(self.text_corrector, "enhanced_detector"):
                name_quality = (
                    self.text_corrector.enhanced_detector.evaluate_name_quality(
                        name_part
                    )
                )

            # ตรวจสอบว่าข้อความมีชื่อนำหน้าอยู่แล้วหรือไม่
            speaker, content, dialogue_type = (
                self.text_corrector.split_speaker_and_content(message_part)
            )

            # กำหนดค่า threshold ใหม่ที่ต่ำลง
            QUALITY_THRESHOLD = 0.2  # ลดจาก 0.3 เป็น 0.2
            VERY_LOW_THRESHOLD = 0.05  # ลดจาก 0.1 เป็น 0.05
            EMERGENCY_THRESHOLD = 0.01  # เพิ่มใหม่สำหรับกรณีฉุกเฉิน

            combined_text = ""
            method_used = "direct"  # สำหรับ tracking

            if speaker:
                # Case 1: มีชื่อใน B - ใช้เลย
                combined_text = f"{speaker}: {content}"
                self.logging_manager.log_info(f"Using speaker from B: '{speaker}'")
                self._update_recent_speakers(speaker)
                method_used = "speaker_b"

            elif name_quality >= QUALITY_THRESHOLD:
                # Case 2: ชื่อจาก A คุณภาพดี - ใช้ได้
                combined_text = f"{name_part}: {message_part}"
                self.logging_manager.log_info(
                    f"Using name from A: '{name_part}' (quality: {name_quality:.2f})"
                )
                self._update_recent_speakers(name_part)
                method_used = "quality_a"

            elif name_quality >= VERY_LOW_THRESHOLD and name_part.strip():
                # Case 3: ชื่อคุณภาพต่ำแต่ยังพอใช้ได้ - ใช้พร้อมเครื่องหมาย [?]
                combined_text = f"{name_part}[?]: {message_part}"
                self.logging_manager.log_info(
                    f"Using uncertain name: '{name_part}' (quality: {name_quality:.2f})"
                )
                self._update_recent_speakers(name_part)
                method_used = "uncertain"

            elif name_quality >= EMERGENCY_THRESHOLD and name_part.strip():
                # Case 4 (ใหม่): ชื่อคุณภาพต่ำมาก แต่ยังพอใช้ได้ - ใช้พร้อมเครื่องหมาย [??]
                combined_text = f"{name_part}[??]: {message_part}"
                self.logging_manager.log_info(
                    f"Using very uncertain name: '{name_part}' (quality: {name_quality:.2f})"
                )
                self._update_recent_speakers(name_part)
                method_used = "very_uncertain"

            else:
                # Case 5: ไม่มีชื่อหรือคุณภาพต่ำมาก - ใช้ smart fallback

                # 5.1 ตรวจสอบ Unknown Speaker (ชื่อที่ไม่รู้จักแต่มีความยาวเหมาะสม)
                if (
                    name_part
                    and name_part.strip()
                    and len(name_part.strip()) >= 2
                    and len(name_part.strip()) <= 20
                ):
                    # ถ้ามีชื่อที่ดูเป็นชื่อจริง (2-20 ตัวอักษร) ให้ใช้ได้เลย แม้ไม่มีในฐานข้อมูล
                    combined_text = f"{name_part.strip()}: {message_part}"
                    self.logging_manager.log_info(
                        f"Using unknown speaker (not in database): '{name_part.strip()}' (quality: {name_quality:.2f})"
                    )
                    self._update_recent_speakers(name_part.strip())
                    method_used = "unknown_speaker"

                # 5.2 ลองหาชื่อคล้ายกันใน cache
                elif not combined_text:
                    similar_name = self._find_similar_name_in_cache(name_part)
                    if similar_name:
                        combined_text = f"{similar_name}: {message_part}"
                        self.logging_manager.log_info(
                            f"Using similar cached name: '{name_part}' -> '{similar_name}'"
                        )
                        self._update_recent_speakers(similar_name)
                        method_used = "similar_name"

                # 5.3 ลองเดาจาก context
                elif not combined_text:
                    guessed_speaker = self._guess_speaker_from_context(message_part)
                    if guessed_speaker:
                        combined_text = f"{guessed_speaker}: {message_part}"
                        self.logging_manager.log_info(
                            f"Using context-guessed speaker: '{guessed_speaker}'"
                        )
                        self._update_recent_speakers(guessed_speaker)
                        method_used = "context_guess"

                # 5.4 สุดท้าย: ใช้ placeholder
                if not combined_text:
                    combined_text = f"[ผู้พูด]: {message_part}"
                    self.logging_manager.log_info(
                        f"No valid name found, using placeholder"
                    )
                    method_used = "placeholder"

            # บันทึก metrics
            self.translation_metrics.record_translation(combined_text, method_used)

            # แปลข้อความ
            self._update_status_line(f"กำลังแปล (A+B): {combined_text[:50]}...")
            translated_text = self.translator.translate(combined_text)

            # แสดงผลการแปล
            if translated_text and translated_text != self.last_translation:
                self.root.after(
                    0, lambda: self.translated_ui.update_text(translated_text)
                )
                self.last_translation = translated_text
                self.last_text = combined_text
                self.last_translation_time = current_time
                self.force_next_translation = False

        except Exception as e:
            self.logging_manager.log_error(f"Error in _process_normal_dialogue_ab: {e}")
            # Fallback: แปลข้อความโดยไม่มีชื่อ
            self._update_status_line(f"กำลังแปล (A+B): {message_part[:30]}...")
            translated_text = self.translator.translate(f"[ผู้พูด]: {message_part}")

            if translated_text and translated_text != self.last_translation:
                self.root.after(
                    0, lambda: self.translated_ui.update_text(translated_text)
                )
                self.last_translation = translated_text
                self.last_text = message_part
                self.last_translation_time = current_time
                self.force_next_translation = False

    def _update_status_line(self, message):
        """อัพเดทข้อความสถานะโดยใช้ LoggingManager"""
        # ลบบรรทัด print("\r...") ออกไปเลย
        # print(f"\r{message:<60}", end="", flush=True) # <--- ลบบรรทัดนี้ทิ้ง

        # เหลือแค่การเรียก LoggingManager อย่างเดียว
        self.logging_manager.update_status(message)

    def save_ui_positions(self):
        self.last_main_ui_pos = self.root.geometry()
        if hasattr(self, "mini_ui"):
            self.last_mini_ui_pos = self.mini_ui.mini_ui.geometry()
        if hasattr(self, "translated_ui_window"):
            self.last_translated_ui_pos = self.translated_ui_window.geometry()

    def do_move(self, event):
        # ตรวจสอบว่าไม่ได้อยู่ในระหว่างการทำงานหนัก
        if (
            hasattr(self, "_processing_intensive_task")
            and self._processing_intensive_task
        ):
            return  # ไม่อนุญาตให้เคลื่อนย้ายหน้าต่างระหว่างการทำงานหนัก

        if self.x is not None and self.y is not None:
            deltax = event.x - self.x
            deltay = event.y - self.y
            x = self.root.winfo_x() + deltax
            y = self.root.winfo_y() + deltay
            self.root.geometry(f"+{x}+{y}")
        self.save_ui_positions()

    def lock_ui_movement(self):
        """ล็อคการเคลื่อนย้ายหน้าต่างชั่วคราวเพื่อป้องกันการเคลื่อนที่โดยไม่ตั้งใจ"""
        self._processing_intensive_task = True
        self.logging_manager.log_info("UI movement locked")

    def unlock_ui_movement(self):
        """ปลดล็อคการเคลื่อนย้ายหน้าต่าง"""
        self._processing_intensive_task = False
        self.logging_manager.log_info("UI movement unlocked")

    def _finish_stopping_translation(self):
        """จัดการการทำงานสุดท้ายหลังหยุดการแปล เช่น ปลดล็อค UI"""
        # ลบการตรวจสอบและเรียก hide_loading_indicator
        # ปลดล็อค UI การเคลื่อนย้าย
        self.unlock_ui_movement()

    def toggle_ui(self):
        if self.settings.get("enable_ui_toggle"):
            self.save_ui_positions()
            if self.root.state() == "normal":
                # สลับจาก Main UI เป็น Mini UI
                self.main_window_pos = self.root.geometry()
                self.root.withdraw()
                self.mini_ui.mini_ui.deiconify()
                self.mini_ui.mini_ui.lift()
                self.mini_ui.mini_ui.attributes("-topmost", True)
                if self.last_mini_ui_pos:
                    self.mini_ui.mini_ui.geometry(self.last_mini_ui_pos)
            else:
                # สลับจาก Mini UI เป็น Main UI
                self.root.deiconify()
                # ไม่ตั้ง topmost อัตโนมัติ ให้คงสถานะเดิมไว้
                self.root.lift()
                if self.last_main_ui_pos:
                    self.root.geometry(self.last_main_ui_pos)
                self.mini_ui.mini_ui.withdraw()

            # ทำให้แน่ใจว่า Translated UI ยังคงแสดงอยู่ถ้ากำลังแปลอยู่
            if self.is_translating and self.translated_ui_window.winfo_exists():
                self.translated_ui_window.lift()
                self.translated_ui_window.attributes("-topmost", True)

            # อัพเดทสถานะของ Mini UI
            if hasattr(self, "mini_ui"):
                self.mini_ui.update_translation_status(self.is_translating)

    def toggle_mini_ui(self):
        """Toggle between Main UI and Mini UI"""
        self.save_ui_positions()

        if self.root.state() == "normal":
            # ตรวจสอบและปิด pin border ก่อนสลับไป Mini UI
            if hasattr(self, "topmost_button") and self.topmost_button._is_pinned:
                # ถ้ากำลัง pin อยู่ ให้ unpin ก่อน
                self.toggle_topmost()

            # Switch to Mini UI
            main_x = self.root.winfo_x()
            main_y = self.root.winfo_y()
            main_width = self.root.winfo_width()
            main_height = self.root.winfo_height()

            self.root.withdraw()
            self.mini_ui.mini_ui.deiconify()
            self.mini_ui.mini_ui.lift()
            self.mini_ui.mini_ui.attributes("-topmost", True)

            # Position Mini UI at the center of Main UI's last position
            self.mini_ui.position_at_center_of_main(
                main_x, main_y, main_width, main_height
            )

            # *** ลบการอัพเดทสถานะปุ่ม MINI ที่นี่ ***
            # self.update_bottom_button_state("mini", True)  <-- ลบบรรทัดนี้
        else:
            # Switch to Main UI
            self.root.deiconify()
            self.root.lift()
            # ไม่ตั้ง topmost อัตโนมัติ ให้คงสถานะเดิมไว้
            if self.last_main_ui_pos:
                self.root.geometry(self.last_main_ui_pos)
            self.mini_ui.mini_ui.withdraw()

            # *** ลบการอัพเดทสถานะปุ่ม MINI ที่นี่ ***
            # self.update_bottom_button_state("mini", False)  <-- ลบบรรทัดนี้

        # Update Mini UI status
        if hasattr(self, "mini_ui"):
            self.mini_ui.update_translation_status(self.is_translating)

        # รีเซ็ตสถานะปุ่ม MINI ทุกครั้งหลังจาก toggle
        self.reset_mini_button_state()

    def toggle_main_ui(self):
        self.save_ui_positions()
        if self.root.state() == "normal":
            self.root.withdraw()
        else:
            self.root.deiconify()
            self.root.overrideredirect(True)  # เพิ่มบรรทัดนี้
            if self.last_main_ui_pos:
                self.root.geometry(self.last_main_ui_pos)

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.x = None
        self.y = None

    def update_mini_ui_move(self):
        original_do_move = self.mini_ui.do_move_mini_ui

        def new_do_move_mini_ui(event):
            original_do_move(event)
            self.save_ui_positions()

        self.mini_ui.do_move_mini_ui = new_do_move_mini_ui

    def setup_ui_position_tracking(self):
        self.update_mini_ui_move()
        self.load_ui_positions()

    def blink(self):
        """สร้าง breathing effect แทนการกระพริบ"""
        if self.blinking:
            # ถ้ายังไม่มี breathing_effect ให้สร้างใหม่
            if not hasattr(self, "breathing_effect"):
                self.breathing_effect = self.create_breathing_effect()

            # เริ่ม breathing effect
            self.breathing_effect.start()
        else:
            # หยุด breathing effect เมื่อไม่ได้ทำงาน
            if hasattr(self, "breathing_effect"):
                self.breathing_effect.stop()
                # รีเซ็ตกลับไปที่ไอคอนสีดำเมื่อหยุด
                self.blink_label.config(image=self.black_icon)

    def force_translate(self):
        """
        บังคับให้แปลข้อความใหม่ และเรียนรู้จากผลลัพธ์
        สามารถใช้ได้ในทั้งโหมดปกติและโหมด Click Translate
        """
        current_time = time.time()
        if current_time - self.last_force_time >= 2:

            # เพิ่มข้อความสถานะพิเศษสำหรับ Click Translate mode
            if self.settings.get("enable_click_translate", False):
                self._update_status_line(
                    "✓ Translation triggered (Click Translate mode)"
                )
            else:
                self._update_status_line("✓ Force translating...")

            self.force_next_translation = True
            self.last_force_time = current_time

            # เก็บสถานะก่อน force translate
            self.pre_force_state = {
                "text": self.last_text if hasattr(self, "last_text") else "",
            }

            # ล้างแคชชั่วคราว
            self.ocr_cache.clear()

            # หลังจากแปลแล้ว 2 วินาที ให้ตรวจสอบและเรียนรู้
            self.root.after(2000, self.learn_from_force_translate)

    def learn_from_force_translate(self):
        """
        เรียนรู้จากผลลัพธ์หลังจาก force translate
        """
        # หากไม่มีข้อมูลก่อน force หรือหลัง force ให้ข้าม
        if not hasattr(self, "pre_force_state") or not hasattr(self, "last_text"):
            return

        pre_text = self.pre_force_state.get("text", "")
        post_text = self.last_text

        # ถ้ามีความแตกต่างระหว่างข้อความก่อนและหลัง force translate
        if pre_text != post_text and pre_text and post_text:
            # สกัดชื่อจากข้อความก่อนและหลัง force translate
            pre_speaker, _, _ = self.text_corrector.split_speaker_and_content(pre_text)
            post_speaker, _, _ = self.text_corrector.split_speaker_and_content(
                post_text
            )

            # ถ้ามีการเปลี่ยนแปลงชื่อ
            if pre_speaker != post_speaker and pre_speaker and post_speaker:
                # บันทึกรูปแบบการแก้ไขเพื่อใช้ในอนาคต
                self.logging_manager.log_info(
                    f"เรียนรู้การแก้ไขชื่อ: '{pre_speaker}' -> '{post_speaker}'"
                )

                if hasattr(self.text_corrector, "enhanced_detector"):
                    # สอนให้ detector รู้จักชื่อที่ถูกต้อง
                    self.text_corrector.enhanced_detector.learn_correction(
                        pre_speaker, post_speaker
                    )

                    # เพิ่มชื่อที่ถูกต้องเข้าไปในรายการชื่อล่าสุด
                    self.text_corrector.enhanced_detector.add_recent_name(post_speaker)

                    # บันทึกลงฐานข้อมูลถาวรถ้าเป็นชื่อใหม่
                    if (
                        post_speaker not in self.text_corrector.names
                        and post_speaker not in self.text_corrector.confirmed_names
                    ):
                        self.text_corrector.save_new_friend(
                            post_speaker,
                            "Character",
                            f"Learned from force translate correction",
                        )

    def update_highlight_on_preset_change(self, areas):
        """อัพเดทการแสดงพื้นที่ไฮไลท์เมื่อมีการเปลี่ยน preset
        Args:
            areas (list): รายการพื้นที่ที่ต้องแสดง
        """
        try:
            # ถ้ากำลังแสดงพื้นที่อยู่
            area_is_shown = False
            if (
                hasattr(self, "control_ui")
                and self.control_ui
                and hasattr(self.control_ui, "is_show_area_active")
            ):
                area_is_shown = self.control_ui.is_show_area_active()

            if area_is_shown:
                # บันทึกสถานะการแสดงผล
                was_showing = True
                # ซ่อนพื้นที่เก่า
                self.hide_show_area()
                # แสดงพื้นที่ใหม่ทันที
                self.show_area()
                # อัพเดทสถานะปุ่ม
                self.show_area_button.update_button(text="HIDE AREA")
                self.update_button_highlight(self.show_area_button, True)

            logging.info(f"Updated highlight areas: {areas}")

        except Exception as e:
            logging.error(f"Error updating highlights: {e}")

    def switch_area(self, areas, preset_number_override=None, source="unknown"):
        try:
            # ส่วนของการตรวจสอบ Input และหา new_area_str (เหมือนเดิม)
            if isinstance(areas, list):
                valid_areas = sorted([a for a in areas if a in ["A", "B", "C"]])
            elif isinstance(areas, str):
                valid_areas = sorted(
                    [a for a in areas.split("+") if a in ["A", "B", "C"]]
                )
            elif areas is None:
                logging.warning(
                    "MBB.py switch_area received None for 'areas'. Aborting switch."
                )
                return False
            else:
                logging.error(
                    f"MBB.py Invalid type for 'areas' in switch_area: {type(areas)}. Aborting switch."
                )
                return False

            if not valid_areas:
                logging.warning(
                    "MBB.py No valid areas provided to switch_area. Defaulting to 'A'."
                )
                valid_areas = ["A"]
            new_area_str = "+".join(valid_areas)

            # Logic การหา Target Preset (เหมือนเดิม)
            current_preset_in_settings = self.settings.get("current_preset", 1)
            target_preset_num = current_preset_in_settings

            if not hasattr(self, "max_presets"):  # ตรวจสอบว่า self.max_presets มีอยู่หรือไม่
                self.max_presets = 6  # กำหนดค่า default ถ้ายังไม่มี

            if preset_number_override is not None:
                if 1 <= preset_number_override <= self.max_presets:
                    target_preset_num = preset_number_override
                else:
                    logging.warning(
                        f"MBB.py Invalid preset override {preset_number_override} ignored. Keeping {target_preset_num}."
                    )
            else:
                found_preset = self.settings.find_preset_by_areas(new_area_str)
                if found_preset:
                    target_preset_num = found_preset
                else:
                    if current_preset_in_settings >= 4:  # Custom Preset
                        target_preset_num = current_preset_in_settings
                    # else: ถ้าเป็น System Preset (1-3) และ area ไม่ตรง, จะยังคง target_preset_num เป็น current_preset_in_settings
                    # ซึ่งอาจจะทำให้เกิดการเรียก sync_last_used_preset โดยที่ area ไม่ตรงกับ preset นั้น
                    # แต่ sync_last_used_preset จะใช้ area_config_override อยู่แล้ว

            current_internal_preset = getattr(self, "current_preset", None)
            current_internal_area = getattr(self, "current_area", None)

            # --- จุดแก้ไขสำคัญ: ดึงค่า is_area_shown จาก control_ui ---
            control_ui_is_showing_area = False  # ค่าเริ่มต้น
            if (
                hasattr(self, "control_ui")
                and self.control_ui
                and hasattr(self.control_ui, "is_show_area_active")
            ):
                try:
                    control_ui_is_showing_area = self.control_ui.is_show_area_active()
                except Exception as e_cui_check:
                    # logging.error(f"MBB.py: Error accessing control_ui.is_show_area_active(): {e_cui_check}")
                    control_ui_is_showing_area = False  # Fallback
            # --- สิ้นสุดจุดแก้ไขสำคัญ ---

            if (
                current_internal_preset == target_preset_num
                and current_internal_area == new_area_str
            ):
                # logging.debug(f"MBB.py switch_area called for state ({new_area_str}, Preset {target_preset_num}) which is already active. Source: {source}. No change.")
                # ถึงแม้ state จะไม่เปลี่ยน แต่ถ้า overlay เปิดอยู่ ควรจะ refresh ที่ control_ui
                if control_ui_is_showing_area:
                    if (
                        hasattr(self, "control_ui")
                        and self.control_ui
                        and hasattr(self.control_ui, "show_area_ctrl")
                    ):
                        # logging.debug("MBB.py: Requesting Control_UI to refresh its area overlay (no state change).")
                        # การ refresh จริงๆ ควรเกิดจาก Control_UI.update_display() เมื่อถูกเรียก
                        pass
                return False  # ไม่มีการเปลี่ยนแปลง state

            # --- จุดแก้ไขสำคัญ: ใช้ control_ui_is_showing_area ที่ดึงมาแล้ว ---
            sync_successful = self.sync_last_used_preset(
                preset_num=target_preset_num,
                source=source,
                area_config_override=new_area_str,
                update_control_ui=True,
                update_overlay=control_ui_is_showing_area,  # <--- ใช้ตัวแปรนี้
            )
            # --- สิ้นสุดจุดแก้ไขสำคัญ ---

            if sync_successful:
                return True
            else:
                # logging.info(f"MBB.py switch_area: sync_last_used_preset indicated no change or failed. Source='{source}'.")
                return False

        except AttributeError as ae:
            self.logging_manager.log_error(f"MBB.py switch_area AttributeError: {ae}")

            self.logging_manager.log_error(traceback.format_exc())
            return False
        except Exception as e:
            self.logging_manager.log_error(f"Error in MBB.py switch_area: {e}")

            self.logging_manager.log_error(traceback.format_exc())
            return False

    def _refresh_area_overlay(self):
        """Instructs the Control_UI to refresh its area overlay display."""
        try:
            # ตรวจสอบว่า control_ui และเมธอดที่จำเป็นต้องใช้มีอยู่หรือไม่
            if (
                hasattr(self, "control_ui")
                and self.control_ui
                and hasattr(self.control_ui, "is_show_area_active")
                and hasattr(self.control_ui, "hide_show_area_ctrl")
                and hasattr(self.control_ui, "show_area_ctrl")
            ):

                # รีเฟรชเฉพาะเมื่อพื้นที่กำลังถูกแสดงผลโดย control UI
                if self.control_ui.is_show_area_active():
                    self.logging_manager.log_info(
                        "Requesting Control_UI to refresh area overlay."
                    )
                    # มอบหมายให้ control_ui ทำการซ่อนและแสดงพื้นที่เอง
                    self.control_ui.hide_show_area_ctrl()
                    # ใช้ root.after เพื่อให้ UI thread มีเวลาประมวลผลการซ่อนก่อนแสดงอีกครั้ง
                    self.root.after(50, self.control_ui.show_area_ctrl)
                else:
                    self.logging_manager.log_info(
                        "Area overlay is not active, no refresh needed."
                    )
            else:
                self.logging_manager.log_warning(
                    "Cannot refresh area overlay: Control_UI or its required methods are not available."
                )

        except Exception as e:
            self.logging_manager.log_error(
                f"Error occurred in _refresh_area_overlay: {e}"
            )
            # เพิ่มการแสดง traceback เพื่อให้เห็นรายละเอียดของข้อผิดพลาด
            import traceback

            self.logging_manager.log_error(traceback.format_exc())

    def hide_and_stop_translation(self):
        """ซ่อน UI และหยุดการแปลเมื่อกดปุ่ม WASD (ใช้กับฟีเจอร์ auto-hide)"""
        if self.settings.get("enable_auto_hide") and self.is_translating:
            try:

                # บังคับให้อัพเดท UI ทันทีเพื่อให้เห็นไอคอน
                self.root.update_idletasks()

                # บันทึกล็อก
                self.logging_manager.log_info(
                    "Auto-hide triggered - hiding UI and stopping translation"
                )

                # หยุดการแปล
                self.is_translating = False
                self.translation_event.clear()
                self.start_stop_button.config(text="START")
                self.blinking = False
                self.mini_ui.update_translation_status(False)

                # หยุดไฟกระพริบ
                if hasattr(self, "breathing_effect"):
                    self.breathing_effect.stop()
                # รีเซ็ตไปใช้ไอคอนสีดำ
                self.blink_label.config(image=self.black_icon)

                # ซ่อน translated_ui_window
                if (
                    hasattr(self, "translated_ui_window")
                    and self.translated_ui_window.winfo_exists()
                ):
                    self.translated_ui_window.withdraw()

                # จัดการ thread ในเบื้องหลัง
                def stop_translation_background():
                    try:
                        if (
                            self.translation_thread
                            and self.translation_thread.is_alive()
                        ):
                            self.translation_thread.join(timeout=5)
                            self.logging_manager.log_info(
                                "Translation thread stopped by auto-hide"
                            )

                        # ปลดล็อค UI หลังเสร็จสิ้น - ลบการเรียก hide_loading_indicator
                        self.root.after(
                            1000, lambda: self._finish_stopping_translation()
                        )
                    except Exception as e:
                        self.logging_manager.log_error(
                            f"Error in hide_and_stop_translation background: {e}"
                        )
                        # ปลดล็อค UI ในกรณีที่เกิดข้อผิดพลาด - ลบการเรียก hide_loading_indicator
                        self.root.after(0, lambda: self._finish_stopping_translation())

                # เริ่ม thread สำหรับหยุดการแปลในเบื้องหลัง
                threading.Thread(
                    target=stop_translation_background, daemon=True
                ).start()

            except Exception as e:
                self.logging_manager.log_error(
                    f"Error in hide_and_stop_translation: {e}"
                )
                # ปลดล็อค UI ในกรณีเกิดข้อผิดพลาด - ลบการเรียก hide_loading_indicator
                self._finish_stopping_translation()

    def load_ui_positions(self):
        """โหลดตำแหน่งพิกัดหน้าต่าง UI จาก settings.json

        Function นี้จะโหลดตำแหน่งพิกัดหน้าต่าง UI ที่บันทึกไว้ และปรับตำแหน่งหน้าต่างตามที่บันทึกไว้
        โดยคำนึงถึงกรณีที่ผู้ใช้อาจมีการเปลี่ยนแปลงขนาดหน้าจอหรือจำนวนหน้าจอ
        """
        try:
            # โหลดข้อมูลหน้าจอที่บันทึกไว้
            saved_primary, saved_monitors = self.settings.get_monitor_info()

            # ดึงข้อมูลหน้าจอปัจจุบัน
            current_primary = self.get_primary_monitor_info()
            current_monitors = self.get_all_monitors_info()

            # ตรวจสอบว่าขนาดหน้าจอหรือจำนวนหน้าจอเปลี่ยนแปลงหรือไม่
            screen_changed = False
            if saved_primary != current_primary or (
                saved_monitors and len(saved_monitors) != len(current_monitors)
            ):
                screen_changed = True
                self.logging_manager.log_info(
                    "ตรวจพบการเปลี่ยนแปลงขนาดหน้าจอหรือจำนวนหน้าจอ"
                )

            # ปรับตำแหน่งหน้าต่าง UI ต่างๆ
            self._set_ui_position("main_ui", self.root, screen_changed)

            if hasattr(self, "mini_ui") and hasattr(self.mini_ui, "mini_ui"):
                self._set_ui_position("mini_ui", self.mini_ui.mini_ui, screen_changed)

            if hasattr(self, "translated_ui_window"):
                self._set_ui_position(
                    "translated_ui", self.translated_ui_window, screen_changed
                )

            if hasattr(self, "control_ui") and hasattr(self.control_ui, "window"):
                self._set_ui_position(
                    "control_ui", self.control_ui.window, screen_changed
                )

            if hasattr(self, "translated_logs_window"):
                self._set_ui_position(
                    "logs_ui", self.translated_logs_window, screen_changed
                )

            self.logging_manager.log_info("โหลดตำแหน่งพิกัดหน้าต่าง UI ทั้งหมดสำเร็จ")
            return True
        except Exception as e:
            self.logging_manager.log_error(
                f"เกิดข้อผิดพลาดในการโหลดตำแหน่งพิกัดหน้าต่าง UI: {e}"
            )
            return False

    def get_all_monitors_info(self):
        """ดึงข้อมูลเกี่ยวกับหน้าจอทั้งหมดที่เชื่อมต่อกับระบบ

        Returns:
            list: รายการของหน้าจอทั้งหมด โดยแต่ละรายการเป็น dict ที่มีค่า w, h, x, y
        """
        monitors = []
        try:
            # ดึงขนาดหน้าจอหลัก
            primary_width = self.root.winfo_screenwidth()
            primary_height = self.root.winfo_screenheight()

            # เพิ่มหน้าจอหลักเข้าไปในรายการ
            monitors.append({"w": primary_width, "h": primary_height, "x": 0, "y": 0})

            # บน Windows สามารถใช้ pywin32 หรือ screeninfo เพื่อดึงข้อมูลหน้าจอเพิ่มเติม
            # แต่เพื่อลดการพึ่งพาไลบรารีเพิ่มเติม เราจะใช้วิธีการนี้
            # ถ้าต้องการรองรับหลายจอแสดงผลแบบสมบูรณ์ จะต้องใช้ไลบรารีเพิ่มเติม

            # ตรวจสอบว่าหน้าจอรวมกว้างกว่าหน้าจอหลักหรือไม่ (เป็นการตรวจสอบอย่างหยาบๆ)
            total_width = self.root.winfo_vrootwidth()
            total_height = self.root.winfo_vrootheight()

            # ถ้ามีหน้าจอเพิ่มเติม (พบว่าความกว้างรวมมากกว่าหน้าจอหลัก)
            if total_width > primary_width:
                # สมมติว่าหน้าจอเพิ่มเติมอยู่ทางขวา
                monitors.append(
                    {
                        "w": total_width - primary_width,
                        "h": total_height,
                        "x": primary_width,
                        "y": 0,
                    }
                )

            self.logging_manager.log_info(f"พบหน้าจอทั้งหมด {len(monitors)} จอ")
            return monitors
        except Exception as e:
            self.logging_manager.log_error(f"เกิดข้อผิดพลาดในการดึงข้อมูลหน้าจอทั้งหมด: {e}")
            return [{"w": 0, "h": 0, "x": 0, "y": 0}]  # ค่าเริ่มต้นถ้าเกิดข้อผิดพลาด

    def get_primary_monitor_info(self):
        """ดึงข้อมูลเกี่ยวกับหน้าจอหลัก

        Returns:
            str: สตริงที่แสดงข้อมูลหน้าจอหลัก format: "WxH+X+Y"
        """
        try:
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            # หาตำแหน่ง offset ของหน้าจอหลัก (โดยปกติจะเป็น 0,0)
            screen_x = 0
            screen_y = 0

            # สร้างสตริงรูปแบบเดียวกับ geometry
            monitor_info = f"{screen_width}x{screen_height}+{screen_x}+{screen_y}"
            self.logging_manager.log_info(f"หน้าจอหลัก: {monitor_info}")
            return monitor_info
        except Exception as e:
            self.logging_manager.log_error(f"เกิดข้อผิดพลาดในการดึงข้อมูลหน้าจอหลัก: {e}")
            return "0x0+0+0"  # ค่าเริ่มต้นถ้าเกิดข้อผิดพลาด

    def get_mbb_window_position_side(self):
        """ตรวจสอบว่าหน้าต่าง MBB อยู่ฝั่งซ้ายหรือขวาของจอ

        Returns:
            str: 'left' หรือ 'right' ตามตำแหน่งของ MBB window
        """
        try:
            # ดึงข้อมูลตำแหน่งและขนาดของ MBB window
            main_x = self.root.winfo_x()
            main_width = self.root.winfo_width()

            # ตรวจหาจอภาพที่ MBB อยู่
            try:
                import win32api
                import win32con

                # ดึง handle ของจอภาพที่หน้าต่าง MBB แสดงอยู่
                main_hwnd = int(self.root.winfo_id())
                hmonitor = win32api.MonitorFromWindow(
                    main_hwnd, win32con.MONITOR_DEFAULTTONEAREST
                )

                # ดึงข้อมูลของจอภาพนั้นๆ
                monitor_info = win32api.GetMonitorInfo(hmonitor)
                monitor_rect = monitor_info["Work"]  # (left, top, right, bottom)

                monitor_left = monitor_rect[0]
                monitor_width = monitor_rect[2] - monitor_left

                self.logging_manager.log_info(f"MBB on monitor: {monitor_rect}")

            except Exception as e:
                self.logging_manager.log_warning(
                    f"Failed to get specific monitor info, using primary screen: {e}"
                )
                # Fallback ใช้หน้าจอหลัก
                monitor_left = 0
                monitor_width = self.root.winfo_screenwidth()

            # คำนวณตำแหน่งศูนย์กลางของ MBB บนจอภาพที่มันอยู่
            main_center_on_its_monitor = main_x - monitor_left + (main_width // 2)
            monitor_center_x = monitor_width // 2

            # ตัดสินใจฝั่งซ้าย/ขวา
            if main_center_on_its_monitor <= monitor_center_x:
                side = "left"
            else:
                side = "right"

            self.logging_manager.log_info(f"MBB window position: {side} side of screen")
            return side

        except Exception as e:
            self.logging_manager.log_error(
                f"Error determining MBB window position: {e}"
            )
            return "left"  # default fallback

    def get_mbb_current_monitor_info(self):
        """ดึงข้อมูลจอภาพที่ MBB window อยู่ปัจจุบัน

        Returns:
            dict: ข้อมูลจอภาพ {'left': x, 'top': y, 'right': x, 'bottom': y, 'width': w, 'height': h}
        """
        try:
            import win32api
            import win32con

            # ดึง handle ของจอภาพที่หน้าต่าง MBB แสดงอยู่
            main_hwnd = int(self.root.winfo_id())
            hmonitor = win32api.MonitorFromWindow(
                main_hwnd, win32con.MONITOR_DEFAULTTONEAREST
            )

            # ดึงข้อมูลของจอภาพนั้นๆ
            monitor_info = win32api.GetMonitorInfo(hmonitor)
            work_area = monitor_info[
                "Work"
            ]  # (left, top, right, bottom) - ไม่รวม taskbar

            monitor_data = {
                "left": work_area[0],
                "top": work_area[1],
                "right": work_area[2],
                "bottom": work_area[3],
                "width": work_area[2] - work_area[0],
                "height": work_area[3] - work_area[1],
            }

            self.logging_manager.log_info(f"MBB current monitor: {monitor_data}")
            return monitor_data

        except Exception as e:
            self.logging_manager.log_warning(
                f"Failed to get specific monitor info, using primary screen: {e}"
            )
            # Fallback ใช้หน้าจอหลัก
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            return {
                "left": 0,
                "top": 0,
                "right": screen_width,
                "bottom": screen_height,
                "width": screen_width,
                "height": screen_height,
            }

    def clear_logs_position_cache_and_reposition(self):
        """เคลียร์ cache ตำแหน่ง logs UI และใช้ smart positioning ทันที"""
        try:
            # เคลียร์ cache
            success = self.settings.clear_logs_position_cache()
            if success:
                self.logging_manager.log_info("Cleared logs UI position cache")

                # ถ้า logs window เปิดอยู่ ให้ reposition ทันที
                if (
                    hasattr(self, "translated_logs_instance")
                    and self.translated_logs_instance
                    and hasattr(self, "translated_logs_window")
                    and self.translated_logs_window.winfo_exists()
                    and self.translated_logs_window.state() != "withdrawn"
                ):

                    mbb_side = self.get_mbb_window_position_side()
                    self.translated_logs_instance.check_screen_size_and_adjust(mbb_side)
                    self.logging_manager.log_info(
                        f"Repositioned logs UI to {mbb_side} side"
                    )

                return True
        except Exception as e:
            self.logging_manager.log_error(f"Error clearing logs position cache: {e}")
        return False

    def _set_ui_position(self, ui_name, window, screen_changed):
        """ตั้งค่าตำแหน่งหน้าต่าง UI ตามข้อมูลที่บันทึกไว้

        Args:
            ui_name (str): ชื่อของ UI ('main_ui', 'mini_ui', 'translated_ui', 'control_ui', 'logs_ui')
            window (tk.Tk/tk.Toplevel): หน้าต่าง UI ที่ต้องการปรับตำแหน่ง
            screen_changed (bool): True ถ้าขนาดหน้าจอหรือจำนวนหน้าจอเปลี่ยนแปลง
        """
        if not window or not window.winfo_exists():
            return

        # ดึงข้อมูลตำแหน่งที่บันทึกไว้
        saved_geometry = self.settings.get_ui_position(ui_name)

        if not saved_geometry:
            return

        try:
            # ถ้าหน้าจอเปลี่ยนแปลง ให้ตรวจสอบว่าตำแหน่งที่บันทึกไว้ยังอยู่ในหน้าจอหรือไม่
            if screen_changed:
                # แยกส่วนประกอบของ geometry: WxH+X+Y
                match = re.match(r"(\d+)x(\d+)\+(\d+)\+(\d+)", saved_geometry)
                if match:
                    width, height, x, y = map(int, match.groups())

                    # ตรวจสอบว่าตำแหน่งอยู่ในหน้าจอหรือไม่
                    screen_width = window.winfo_screenwidth()
                    screen_height = window.winfo_screenheight()

                    # ปรับตำแหน่งให้อยู่ในหน้าจอ
                    if x + width > screen_width:
                        x = max(0, screen_width - width)
                    if y + height > screen_height:
                        y = max(0, screen_height - height)

                    # สร้าง geometry ใหม่
                    saved_geometry = f"{width}x{height}+{x}+{y}"

            # ตั้งค่าตำแหน่งหน้าต่าง
            window.geometry(saved_geometry)
            self.logging_manager.log_info(f"ตั้งค่าตำแหน่ง {ui_name}: {saved_geometry}")
        except Exception as e:
            self.logging_manager.log_error(f"เกิดข้อผิดพลาดในการตั้งค่าตำแหน่ง {ui_name}: {e}")

    def exit_program(self):
        self.logging_manager.log_info("MBB.py: Initiating program exit...")

        # *** เพิ่ม: หยุด CPU Monitor Thread ***
        if (
            hasattr(self, "_stop_cpu_monitor_event") and self._stop_cpu_monitor_event
        ):  # Check if event exists
            self._stop_cpu_monitor_event.set()  # ส่งสัญญาณให้ Thread หยุด
        if (
            hasattr(self, "_cpu_monitor_thread_instance")
            and self._cpu_monitor_thread_instance
        ):
            if self._cpu_monitor_thread_instance.is_alive():
                self.logging_manager.log_info(
                    "Waiting for CPU Monitor thread to finish..."
                )
                self._cpu_monitor_thread_instance.join(
                    timeout=1.0
                )  # รอ Thread จบการทำงาน
            if not self._cpu_monitor_thread_instance.is_alive():
                self.logging_manager.log_info("CPU Monitor thread has finished.")
            else:
                self.logging_manager.log_warning(
                    "CPU Monitor thread did not finish in time."
                )
        # --- สิ้นสุดส่วนที่เพิ่ม ---

        # ทำความสะอาด timer และ fade jobs ก่อนปิดโปรแกรม
        if hasattr(self, "_tooltip_hide_timer") and self._tooltip_hide_timer:
            try:
                self.root.after_cancel(self._tooltip_hide_timer)
            except:
                pass  # Ignore error if already cancelled or gone

        if hasattr(self, "_fade_job") and self._fade_job:
            try:
                self.root.after_cancel(self._fade_job)
            except:
                pass  # Ignore error

        if hasattr(self, "is_translating") and self.is_translating:
            self.stop_translation()  # stop_translation ควรจะจัดการเรื่อง thread ของตัวเอง
            if (
                hasattr(self, "translation_thread")
                and self.translation_thread
                and self.translation_thread.is_alive()
            ):
                self.logging_manager.log_info(
                    "MBB.py: Waiting for translation thread to finish before exit (after stop_translation call)..."
                )
                self.translation_thread.join(timeout=2.0)  # เพิ่ม timeout เล็กน้อย
                if self.translation_thread.is_alive():
                    self.logging_manager.log_warning(
                        "Translation thread did not finish cleanly during exit."
                    )

        if (
            hasattr(self, "control_ui")
            and self.control_ui
            and hasattr(
                self.control_ui, "is_area_shown"
            )  # ควรเป็น is_show_area_active()
            and hasattr(self.control_ui, "hide_show_area_ctrl")
        ):
            try:
                # เรียกใช้ method ที่ถูกต้องจาก control_ui เพื่อตรวจสอบสถานะ
                if self.control_ui.is_show_area_active():
                    self.logging_manager.log_info(
                        "MBB.py: Instructing Control_UI to hide its area overlay before exit."
                    )
                    self.control_ui.hide_show_area_ctrl()  # เรียกเพื่อซ่อน
            except Exception as e:
                self.logging_manager.log_error(
                    f"MBB.py: Error calling control_ui.hide_show_area_ctrl() during exit: {e}"
                )

        if hasattr(self, "remove_all_hotkeys"):
            self.remove_all_hotkeys()

        try:
            if (
                hasattr(self, "settings")
                and hasattr(self.settings, "save_monitor_info")
                and hasattr(self, "get_primary_monitor_info")
                and hasattr(self, "get_all_monitors_info")
            ):
                primary_monitor_info = self.get_primary_monitor_info()
                all_monitors_info = self.get_all_monitors_info()
                self.settings.save_monitor_info(primary_monitor_info, all_monitors_info)

            ui_elements_to_save = {
                "main_ui": self.root,
                "mini_ui": (
                    getattr(self.mini_ui, "mini_ui", None)
                    if hasattr(self, "mini_ui")
                    else None
                ),
                "translated_ui": getattr(self, "translated_ui_window", None),
                "control_ui": (
                    getattr(self.control_ui, "root", None)
                    if hasattr(self, "control_ui")
                    else None
                ),
                "logs_ui": getattr(self, "translated_logs_window", None),
            }

            if hasattr(self, "settings") and hasattr(self.settings, "save_ui_position"):
                for name, widget in ui_elements_to_save.items():
                    if (
                        widget
                        and hasattr(widget, "winfo_exists")
                        and widget.winfo_exists()
                    ):
                        try:
                            self.settings.save_ui_position(name, widget.geometry())
                        except Exception as e:
                            self.logging_manager.log_error(
                                f"MBB.py: Error saving position for {name}: {e}"
                            )

            # settings.save_all_ui_positions() อาจจะไม่จำเป็นถ้า save_ui_position บันทึกทันที
            # หรือถ้ามันทำหน้าที่ commit การเปลี่ยนแปลงทั้งหมด ก็ควรเรียก
            if hasattr(self, "settings") and hasattr(
                self.settings, "save_settings"
            ):  # settings.json หลัก
                self.settings.save_settings()
                self.logging_manager.log_info("MBB.py: Main settings.json saved.")

        except Exception as e:
            self.logging_manager.log_error(
                f"MBB.py: Error saving UI positions or monitor info during exit: {e}"
            )

        if hasattr(keyboard, "unhook_all"):
            try:
                keyboard.unhook_all()
                self.logging_manager.log_info("MBB.py: All keyboard hotkeys unhooked.")
            except Exception as e:
                self.logging_manager.log_error(f"MBB.py: Error unhooking keyboard: {e}")

        # ปิดหน้าต่าง UI ย่อยๆ ก่อน
        # Control UI and Settings UI
        if (
            hasattr(self, "control_ui")
            and self.control_ui
            and hasattr(self.control_ui, "root")
            and self.control_ui.root.winfo_exists()
        ):
            try:
                self.control_ui.root.destroy()
                self.logging_manager.log_info("MBB.py: Control_UI window destroyed.")
            except Exception as e:
                self.logging_manager.log_error(
                    f"MBB.py: Error destroying Control_UI window: {e}"
                )

        if (
            hasattr(self, "settings_ui")
            and self.settings_ui
            and hasattr(
                self.settings_ui, "settings_window"
            )  # ชื่อ attribute อาจจะต้องเช็คใน SettingsUI
            and self.settings_ui.settings_window  # และเช็คว่าไม่เป็น None
            and self.settings_ui.settings_window.winfo_exists()
        ):
            try:
                self.settings_ui.settings_window.destroy()
                self.logging_manager.log_info("MBB.py: Settings_UI window destroyed.")
            except Exception as e:
                self.logging_manager.log_error(
                    f"MBB.py: Error destroying Settings_UI window: {e}"
                )

        # Other windows
        windows_to_close_mbb = []
        if hasattr(self, "translated_ui_window") and self.translated_ui_window:
            windows_to_close_mbb.append(self.translated_ui_window)
        if hasattr(self, "translated_logs_window") and self.translated_logs_window:
            windows_to_close_mbb.append(self.translated_logs_window)
        if (
            hasattr(self, "mini_ui")
            and hasattr(self.mini_ui, "mini_ui")
            and self.mini_ui.mini_ui
        ):
            windows_to_close_mbb.append(self.mini_ui.mini_ui)
        if hasattr(self, "guide_window") and self.guide_window:  # เพิ่ม guide_window
            windows_to_close_mbb.append(self.guide_window)

        for window in windows_to_close_mbb:
            try:
                if window and window.winfo_exists():
                    # Get window info before destroy
                    window_info = "unknown"
                    try:
                        window_info = window.wm_title()
                    except:
                        window_info = str(window)

                    # Destroy window
                    window.destroy()
                    self.logging_manager.log_info(
                        f"MBB.py: Closed window: {window_info}"
                    )
            except Exception as e:
                # Log error without accessing window properties
                self.logging_manager.log_error(
                    f"MBB.py: Error destroying a sub-window: {e}"
                )

        # บันทึก Font settings ถ้ามี
        if hasattr(self, "font_manager") and hasattr(
            self.font_manager, "font_settings"
        ):
            if hasattr(self.font_manager.font_settings, "save_settings"):
                try:
                    self.font_manager.font_settings.save_settings()
                    self.logging_manager.log_info(
                        "MBB.py: Font settings saved before exit."
                    )
                except Exception as e:
                    self.logging_manager.log_error(
                        f"MBB.py: Could not save font settings: {e}"
                    )

        # สุดท้าย ปิด root window
        try:
            if self.root and self.root.winfo_exists():
                self.root.quit()  # Should be called before destroy for Tkinter mainloop
                self.root.destroy()
                self.logging_manager.log_info("MBB.py: Root window destroyed.")
        except Exception as e:
            self.logging_manager.log_error(f"MBB.py: Error destroying root window: {e}")

        self.logging_manager.log_info("MagicBabel application closed.")
        if sys and hasattr(sys, "exit"):
            sys.exit(0)  # Ensure the program truly exits

    def show_starter_guide(self, force_show=False):  # เพิ่ม parameter force_show
        """แสดงหน้าต่างแนะนำการใช้งานโปรแกรมสำหรับผู้ใช้ใหม่ รองรับไฟล์คู่มือแบบไดนามิก"""
        try:
            # *** 1. ตรวจสอบว่าหน้าต่าง Guide เปิดอยู่แล้วหรือไม่ ***
            if (
                hasattr(self, "guide_window")
                and self.guide_window
                and self.guide_window.winfo_exists()
            ):
                # ถ้าหน้าต่าง Guide เปิดอยู่แล้ว ให้ปิดแทน (toggle)
                self.logging_manager.log_info(
                    "Starter Guide window already exists. Closing it."
                )
                try:
                    self.guide_window.destroy()
                    self.guide_window = None
                    self.logging_manager.log_info("Guide window closed successfully.")
                except Exception as e:
                    self.logging_manager.log_error(f"Error closing guide window: {e}")
                return

            # *** 2. ตรวจสอบค่า show_guide_var และ force_show (เหมือนเดิม) ***
            if not force_show and not self.show_guide_var.get():
                self.logging_manager.log_info(
                    "Starter guide is disabled by user setting. Skipping."
                )
                return

            # --- ส่วนที่เหลือคือการสร้างหน้าต่างใหม่ (เหมือนเดิม แต่มีการปรับปรุง event handling) ---
            self.logging_manager.log_info("===== เริ่มต้นการแสดง Starter Guide =====")

            # ค้นหาไฟล์ guide*.png (เหมือนเดิม)
            guide_files = []
            current_dir = (
                os.getcwd()
            )  # ใช้ os.getcwd() หรือ os.path.dirname(__file__) ตามความเหมาะสม
            try:  # เพิ่ม try-except รอบ getcwd เผื่อกรณีพิเศษ
                current_dir = os.path.dirname(os.path.abspath(__file__))
            except NameError:
                current_dir = os.getcwd()

            self.logging_manager.log_info(f"ค้นหาไฟล์ใน directory: {current_dir}")

            # ค้นหาใน current directory
            for file in os.listdir(current_dir):
                if file.lower().startswith("guide") and (
                    file.lower().endswith(".png") or file.lower().endswith(".jpg")
                ):
                    guide_files.append(os.path.join(current_dir, file))
                    # logging.info(f"พบไฟล์: {file}") # อาจจะ log เยอะไป

            # ค้นหาในโฟลเดอร์ Guide
            guide_dir = os.path.join(current_dir, "Guide")
            if os.path.exists(guide_dir) and os.path.isdir(guide_dir):
                self.logging_manager.log_info(f"ค้นหาไฟล์ในโฟลเดอร์ Guide: {guide_dir}")
                for file in os.listdir(guide_dir):
                    if file.lower().startswith("guide") and (
                        file.lower().endswith(".png") or file.lower().endswith(".jpg")
                    ):
                        # เช็คว่าไฟล์ซ้ำกับที่เจอใน current dir หรือไม่
                        full_path = os.path.join(guide_dir, file)
                        if full_path not in guide_files:
                            guide_files.append(full_path)
                            # logging.info(f"พบไฟล์ในโฟลเดอร์ Guide: {file}") # อาจจะ log เยอะไป

            # เรียงลำดับไฟล์ (เหมือนเดิม)
            def extract_number(filename):
                try:
                    match = re.search(r"guide(\d+)", os.path.basename(filename).lower())
                    if match:
                        return int(match.group(1))
                    return 999
                except:
                    return 999

            guide_files.sort(key=extract_number)
            self.logging_manager.log_info(f"พบไฟล์ guide ทั้งหมด {len(guide_files)} ไฟล์")

            if not guide_files:
                self.logging_manager.log_warning("ไม่พบไฟล์คู่มือ guide*.png เลย")
                messagebox.showwarning("ไม่พบคู่มือ", "ไม่พบไฟล์คู่มือ (guide*.png)")
                return

            # สร้างหน้าต่างใหม่
            self.guide_window = tk.Toplevel(self.root)
            self.guide_window.title("Starter Guide")
            self.guide_window.overrideredirect(True)
            self.guide_window.attributes("-topmost", True)

            # การคำนวณตำแหน่งกลางจอ (เหมือนเดิม)
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            guide_width = 800
            guide_height = 600
            x_pos = (screen_width - guide_width) // 2
            y_pos = (screen_height - guide_height) // 2
            self.guide_window.geometry(f"{guide_width}x{guide_height}+{x_pos}+{y_pos}")
            self.guide_window.configure(bg="#333333")

            # *** 3. เพิ่ม Protocol Handler สำหรับการปิดหน้าต่าง ***
            def handle_guide_close():
                self.logging_manager.log_info("Guide window closed.")
                if hasattr(self, "guide_window") and self.guide_window:
                    # *** 5. เพิ่มการตรวจสอบว่าหน้าต่างยังมีอยู่ก่อนทำลาย ***
                    # (อาจถูกทำลายไปแล้วโดยวิธีอื่น)
                    if self.guide_window.winfo_exists():
                        self.guide_window.destroy()
                    # ในทุกกรณี ตั้งค่าตัวแปรกลับเป็น None
                    self.guide_window = None

            self.guide_window.protocol("WM_DELETE_WINDOW", handle_guide_close)

            # โหลดภาพคู่มือ (เหมือนเดิม)
            self.guide_photo_images = []
            successful_loads = 0
            for img_file in guide_files:
                try:
                    image = Image.open(img_file)
                    img_width, img_height = image.size
                    ratio = min(
                        (guide_width - 40) / img_width,
                        (guide_height - 100) / img_height,
                    )
                    new_width = int(img_width * ratio)
                    new_height = int(img_height * ratio)
                    resized_image = image.resize(
                        (new_width, new_height), Image.Resampling.LANCZOS
                    )
                    photo = ImageTk.PhotoImage(resized_image)
                    self.guide_photo_images.append(photo)
                    successful_loads += 1
                except Exception as e:
                    self.logging_manager.log_error(
                        f"ไม่สามารถโหลดไฟล์ {os.path.basename(img_file)}: {e}"
                    )

            if successful_loads == 0:
                self.logging_manager.log_error("ไม่สามารถโหลดไฟล์คู่มือใดๆ ได้เลย")
                handle_guide_close()  # เรียกใช้ฟังก์ชันปิดที่สร้างไว้
                messagebox.showerror("ข้อผิดพลาด", "ไม่สามารถโหลดไฟล์คู่มือได้")
                return

            # ติดตามหน้าปัจจุบัน (เหมือนเดิม)
            self.current_guide_page = 0
            self.total_guide_pages = len(self.guide_photo_images)
            self.logging_manager.log_info(
                f"จำนวนหน้าคู่มือทั้งหมด: {self.total_guide_pages} หน้า"
            )

            # สร้าง frame หลัก (เหมือนเดิม)
            main_frame = tk.Frame(self.guide_window, bg="#333333")
            main_frame.pack(fill=tk.BOTH, expand=True)

            # ปุ่มปิด (ใช้ handle_guide_close)
            close_button = tk.Button(
                self.guide_window,
                text="×",
                font=("Arial", 16, "bold"),
                bg="#FF4136",
                fg="white",
                bd=0,
                padx=10,
                pady=0,
                command=handle_guide_close,  # <--- เรียกฟังก์ชันที่สร้างไว้
            )
            close_button.place(x=guide_width - 40, y=10)
            close_button.bind(
                "<Enter>", lambda e: close_button.config(bg="#FF6B6B", cursor="hand2")
            )
            close_button.bind("<Leave>", lambda e: close_button.config(bg="#FF4136"))

            # สร้างแคนวาส (เหมือนเดิม)
            self.guide_canvas = tk.Canvas(
                main_frame,
                width=guide_width,
                height=guide_height - 80,
                bg="#333333",
                highlightthickness=0,
            )
            self.guide_canvas.pack(pady=(20, 0))

            # สร้าง frame ล่าง (เหมือนเดิม)
            bottom_frame = tk.Frame(main_frame, bg="#333333", height=60)
            bottom_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=10)
            bottom_frame.pack_propagate(False)

            # Checkbutton "ไม่ต้องแสดงอีก" (เหมือนเดิม)
            dont_show_check = Checkbutton(
                bottom_frame,
                text="ไม่ต้องแสดงอีก",
                variable=self.show_guide_var,
                onvalue=False,
                offvalue=True,
                command=self._toggle_show_guide_setting,
                bg="#333333",
                fg="#FFFFFF",
                selectcolor="#444444",
                activebackground="#333333",
                activeforeground="#FFFFFF",
                bd=0,
                font=("Anuphan", 14),
            )
            dont_show_check.pack(side=tk.LEFT, padx=(20, 0), anchor=tk.W)

            # Frame กลางสำหรับปุ่มนำทาง (เหมือนเดิม)
            nav_center_frame = tk.Frame(bottom_frame, bg="#333333")
            nav_center_frame.pack(expand=True)

            # ปุ่มย้อนกลับ (เหมือนเดิม)
            self.prev_button = tk.Button(
                nav_center_frame,
                text="<",
                font=("Arial", 14, "bold"),
                bg="#555555",
                fg="#FFFFFF",
                bd=0,
                padx=10,
                pady=0,
                command=self.show_prev_guide_page,
            )
            self.prev_button.pack(side=tk.LEFT, padx=(0, 10))

            # เลขหน้า (เหมือนเดิม)
            page_frame = tk.Frame(nav_center_frame, bg="#444444", padx=10, pady=3)
            page_frame.pack(side=tk.LEFT)
            self.page_label = tk.Label(
                page_frame,
                text=f"1/{self.total_guide_pages}",
                font=("Arial", 12, "bold"),
                bg="#444444",
                fg="#FFFFFF",
            )
            self.page_label.pack()

            # ปุ่มถัดไป (เหมือนเดิม)
            self.next_button = tk.Button(
                nav_center_frame,
                text=">",
                font=("Arial", 14, "bold"),
                bg="#555555",
                fg="#FFFFFF",
                bd=0,
                padx=10,
                pady=0,
                command=self.show_next_guide_page,
            )
            self.next_button.pack(side=tk.LEFT, padx=(10, 0))

            # Hover effect ปุ่ม Prev/Next (เหมือนเดิม)
            for button in [self.prev_button, self.next_button]:
                button.bind(
                    "<Enter>",
                    lambda e, b=button: b.config(bg="#777777", cursor="hand2"),
                )
                button.bind("<Leave>", lambda e, b=button: b.config(bg="#555555"))

            # ตั้งค่าสถานะปุ่มเริ่มต้น (เหมือนเดิม)
            if self.current_guide_page == 0:
                self.prev_button.config(state=tk.DISABLED)
            if self.total_guide_pages <= 1:
                self.next_button.config(state=tk.DISABLED)

            # ผูกปุ่ม Escape (ใช้ handle_guide_close)
            self.guide_window.bind("<Escape>", lambda e: handle_guide_close())

            # เพิ่มการเคลื่อนย้ายหน้าต่าง
            self.guide_drag_x = 0
            self.guide_drag_y = 0

            def start_drag(event):
                # *** ตรวจสอบก่อนเริ่มลาก ***
                if (
                    hasattr(self, "guide_window")
                    and self.guide_window
                    and self.guide_window.winfo_exists()
                ):
                    self.guide_drag_x = event.x
                    self.guide_drag_y = event.y
                else:  # ถ้าหน้าต่างไม่มีแล้ว ไม่ต้องทำอะไร
                    self.guide_drag_x = None
                    self.guide_drag_y = None

            def do_drag(event):
                # *** 4. ตรวจสอบว่าหน้าต่างยังอยู่ และเริ่มลากหรือยัง ก่อนเข้าถึง winfo ***
                if (
                    hasattr(self, "guide_window")
                    and self.guide_window
                    and self.guide_window.winfo_exists()
                    and self.guide_drag_x is not None
                ):
                    try:
                        deltax = event.x - self.guide_drag_x
                        deltay = event.y - self.guide_drag_y
                        x = self.guide_window.winfo_x() + deltax
                        y = self.guide_window.winfo_y() + deltay
                        self.guide_window.geometry(f"+{x}+{y}")
                    except tk.TclError as e:
                        # จัดการ error กรณี window หายไประหว่างลาก
                        logging.warning(
                            f"Error during guide drag (window might be closed): {e}"
                        )
                        self.guide_drag_x = None  # หยุดการลาก
                        self.guide_drag_y = None
                else:
                    # หยุดการลากถ้าหน้าต่างหายไปหรือไม่เคยเริ่มลาก
                    self.guide_drag_x = None
                    self.guide_drag_y = None

            # ผูกเหตุการณ์คลิกและลาก (เหมือนเดิม)
            for widget in [
                main_frame,
                self.guide_canvas,
                bottom_frame,
                nav_center_frame,
                page_frame,
                self.page_label,
            ]:
                widget.bind("<Button-1>", start_drag)
                widget.bind("<B1-Motion>", do_drag)

            # แสดงภาพคู่มือหน้าแรก
            self.update_guide_page()  # เรียกเมธอดนี้

            self.logging_manager.log_info(
                f"แสดงหน้าต่าง Starter Guide ({self.total_guide_pages} หน้า) สำเร็จ"
            )

        except Exception as e:
            self.logging_manager.log_error(f"เกิดข้อผิดพลาดในการแสดง Starter Guide: {e}")

            self.logging_manager.log_error(traceback.format_exc())
            if (
                hasattr(self, "guide_window")
                and self.guide_window
                and self.guide_window.winfo_exists()
            ):
                try:
                    self.guide_window.destroy()
                except:
                    pass
                self.guide_window = None  # ตั้งค่ากลับเป็น None

    def _toggle_show_guide_setting(self):
        """อัพเดทค่า setting 'show_starter_guide' เมื่อ Checkbutton ถูกคลิก"""
        try:
            new_value = self.show_guide_var.get()
            self.settings.set("show_starter_guide", new_value)
            # ไม่จำเป็นต้อง save_settings() ที่นี่ เพราะ set() จัดการให้แล้ว
            self.logging_manager.log_info(
                f"Setting 'show_starter_guide' updated to: {new_value}"
            )
        except Exception as e:
            self.logging_manager.log_error(
                f"Error updating show_starter_guide setting: {e}"
            )

    def resize_guide_image(self, image, width, height):
        """ปรับขนาดรูปภาพให้พอดีกับพื้นที่แสดงผล แต่ยังคงรักษาสัดส่วน"""
        try:
            img_width, img_height = image.size
            ratio = min(width / img_width, height / img_height)

            new_width = int(img_width * ratio)
            new_height = int(img_height * ratio)

            return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        except Exception as e:
            self.logging_manager.log_error(f"ข้อผิดพลาดในการปรับขนาดภาพ: {e}")
            return image  # คืนค่าภาพเดิมถ้าปรับขนาดไม่สำเร็จ

    def update_guide_page(self):
        """อัพเดทหน้าคู่มือตามหน้าปัจจุบัน"""
        try:
            # ล้างแคนวาส
            self.guide_canvas.delete("all")

            # ตรวจสอบความถูกต้องของดัชนีหน้า
            if not hasattr(self, "guide_photo_images") or not self.guide_photo_images:
                self.logging_manager.log_error("ไม่พบรายการภาพคู่มือ")
                return

            if not hasattr(self, "total_guide_pages"):
                self.total_guide_pages = len(self.guide_photo_images)

            if self.current_guide_page < 0:
                self.current_guide_page = 0
            elif self.current_guide_page >= self.total_guide_pages:
                self.current_guide_page = self.total_guide_pages - 1

            # บันทึกล็อกการเปลี่ยนหน้า
            self.logging_manager.log_info(
                f"กำลังแสดงหน้าที่ {self.current_guide_page + 1}/{self.total_guide_pages}"
            )

            # แสดงภาพตรงกลางแคนวาส
            canvas_width = self.guide_canvas.winfo_width()
            canvas_height = self.guide_canvas.winfo_height()

            if canvas_width <= 1:  # ถ้ายังไม่ได้เรนเดอร์
                canvas_width = 800
            if canvas_height <= 1:
                canvas_height = 540  # 600 - 60

            self.guide_canvas.create_image(
                canvas_width // 2,
                canvas_height // 2,
                image=self.guide_photo_images[self.current_guide_page],
            )

            # อัพเดทเลขหน้า
            if hasattr(self, "page_label"):
                self.page_label.config(
                    text=f"{self.current_guide_page + 1}/{self.total_guide_pages}"
                )

            # อัพเดทสถานะปุ่มย้อนกลับ
            if hasattr(self, "prev_button"):
                if self.current_guide_page == 0:
                    self.prev_button.config(state=tk.DISABLED)
                else:
                    self.prev_button.config(state=tk.NORMAL)

            # อัพเดทสถานะปุ่มถัดไป
            if hasattr(self, "next_button"):
                if self.current_guide_page >= self.total_guide_pages - 1:
                    self.next_button.config(state=tk.DISABLED)
                else:
                    self.next_button.config(state=tk.NORMAL)

        except Exception as e:
            self.logging_manager.log_error(f"เกิดข้อผิดพลาดในการอัพเดทหน้าคู่มือ: {e}")

    def show_next_guide_page(self):
        """แสดงหน้าคู่มือถัดไป"""
        if (
            hasattr(self, "total_guide_pages")
            and self.current_guide_page < self.total_guide_pages - 1
        ):
            self.current_guide_page += 1
            self.update_guide_page()
            self.logging_manager.log_info(
                f"เปลี่ยนไปหน้าถัดไป: {self.current_guide_page + 1}/{self.total_guide_pages}"
            )

    def show_prev_guide_page(self):
        """แสดงหน้าคู่มือก่อนหน้า"""
        if hasattr(self, "total_guide_pages") and self.current_guide_page > 0:
            self.current_guide_page -= 1
            self.update_guide_page()
            self.logging_manager.log_info(
                f"เปลี่ยนไปหน้าก่อนหน้า: {self.current_guide_page + 1}/{self.total_guide_pages}"
            )


def main():
    """Simple entry point for MBB - starts the program directly"""
    try:
        root = tk.Tk()
        app = MagicBabelApp(root)
        app.setup_ui_position_tracking()
        root.mainloop()
    except Exception as e:
        messagebox.showerror(
            "Critical Error",
            f"An unexpected error occurred: {e}\n\nPlease check the log file for details.",
        )


def check_first_run():
    """Check if this is the first run and show setup if needed"""
    setup_marker = "setup_completed.txt"
    easyocr_marker = "easyocr_installed.txt"

    # If setup was already completed, skip
    if os.path.exists(setup_marker):
        return

    # If EasyOCR marker file exists (from installer), skip
    if os.path.exists(easyocr_marker):
        with open(setup_marker, "w") as f:
            f.write("Setup completed - EasyOCR installer was run\n")
        return

    # Try to detect EasyOCR installation using safer method
    try:
        # Use subprocess to check EasyOCR instead of direct import
        # to avoid PyInstaller import issues
        result = subprocess.run(
            [sys.executable, "-c", "import easyocr; print('OK')"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0 and "OK" in result.stdout:
            # EasyOCR is available
            with open(easyocr_marker, "w") as f:
                f.write(f"EasyOCR detected on {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            with open(setup_marker, "w") as f:
                f.write("Setup completed - EasyOCR was already installed\n")
            return
    except Exception as e:
        logging.info(f"EasyOCR detection failed (expected): {e}")
        pass

    # Show first run setup
    try:
        import first_run_setup

        setup = first_run_setup.FirstRunSetup()
        setup.run()
    except Exception as e:
        logging.error(f"Failed to show first run setup: {e}")
        # Create marker to prevent loop
        with open(setup_marker, "w") as f:
            f.write("Setup skipped due to error\n")


if __name__ == "__main__":
    # Check for first run before starting main application
    check_first_run()
    main()
