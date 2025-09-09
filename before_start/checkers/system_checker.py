# checkers/system_checker.py

import json
import os
import platform
import tkinter as tk
from typing import Dict

try:
    import psutil
except ImportError:
    psutil = None

try:
    import torch
except ImportError:
    torch = None

try:
    import ctypes
    from ctypes import windll
except ImportError:
    ctypes = None
    windll = None


class SystemChecker:
    def __init__(self):
        self.project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.settings_file = os.path.join(self.project_root, "settings.json")

    def check_all(self) -> dict:
        result = {"status": "ready", "details": {}}

        screen_info = self._check_screen_resolution()
        result["details"]["screen"] = screen_info
        
        # ถ้า resolution หรือ scale ไม่ตรง ให้เป็น warning
        if screen_info.get("resolution_mismatch") or screen_info.get("scale_warning"):
            result["status"] = "warning"

        result["details"]["gpu"] = self._check_gpu()
        result["details"]["memory"] = self._check_memory()
        result["details"]["platform"] = self._check_platform()

        return result

    def _detect_screen_info(self) -> dict:
        """ตรวจสอบข้อมูลหน้าจอแบบละเอียด (จาก advance_ui.py)"""
        # วิธีที่ 1: ลองใช้ ctypes (Windows)
        try:
            if ctypes and windll and os.name == 'nt':
                # Set DPI awareness
                try:
                    windll.shcore.SetProcessDpiAwareness(1)
                except:
                    pass

                # Get physical screen size
                physical_width = windll.user32.GetSystemMetrics(0)
                physical_height = windll.user32.GetSystemMetrics(1)

                # Get logical resolution จาก tkinter
                root = tk.Tk()
                root.withdraw()
                logical_width = root.winfo_screenwidth()
                logical_height = root.winfo_screenheight()
                root.destroy()

                # Calculate scale factor
                scale_factor = physical_width / logical_width if logical_width > 0 else 1.0

                return {
                    "physical_width": physical_width,
                    "physical_height": physical_height,
                    "logical_width": logical_width,
                    "logical_height": logical_height,
                    "scale_factor": scale_factor,
                    "method": "Windows DPI-aware"
                }
        except Exception as e:
            pass

        # วิธีที่ 2: Fallback - ใช้ tkinter เท่านั้น
        try:
            root = tk.Tk()
            root.withdraw()
            width = root.winfo_screenwidth()
            height = root.winfo_screenheight()
            root.destroy()

            return {
                "physical_width": width,
                "physical_height": height,
                "logical_width": width,
                "logical_height": height,
                "scale_factor": 1.0,
                "method": "Tkinter fallback"
            }
        except Exception as e:
            return {
                "physical_width": 1920,
                "physical_height": 1080,
                "logical_width": 1920,
                "logical_height": 1080,
                "scale_factor": 1.0,
                "method": "Default values"
            }

    def _check_screen(self) -> dict:
        try:
            root = tk.Tk()
            width = root.winfo_screenwidth()
            height = root.winfo_screenheight()
            root.destroy()

            current = f"{width}x{height}"
            
            # โหลดความละเอียดที่คาดหวังจาก settings
            expected = current  # default เป็น current resolution
            needs_fix = False
            
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                # ตรวจสอบ translate_areas เพื่อดูว่าได้ตั้งค่าสำหรับ resolution นี้หรือยัง
                areas = settings.get("translate_areas", {})
                area_a = areas.get("A", {})
                area_b = areas.get("B", {})
                
                # ถ้า areas ยังไม่ได้ตั้งค่า (coordinates เป็น 0) แสดงว่าต้องตั้งค่า
                if (area_a.get("start_x", 0) == 0 and area_a.get("start_y", 0) == 0 and 
                    area_b.get("start_x", 0) == 0 and area_b.get("start_y", 0) == 0):
                    needs_fix = True
                    expected = f"{current} (Areas not configured)"
                    
            except:
                needs_fix = True
                expected = f"{current} (Settings file issue)"

            return {
                "current": current,
                "expected": expected,
                "needs_fix": needs_fix,
                "message": f"Current: {current}" + (f", Expected: {expected}" if needs_fix else "")
            }
        except Exception as e:
            return {"current": "Unknown", "expected": "Unknown", "needs_fix": False, "error": str(e)}

    def _check_gpu(self) -> dict:
        try:
            if torch and torch.cuda.is_available():
                return {"cuda": True, "message": "CUDA Ready", "device_count": torch.cuda.device_count()}
            else:
                return {"cuda": False, "message": "CPU Mode (Slower performance)"}
        except:
            return {"cuda": False, "message": "PyTorch not found"}

    def _check_memory(self) -> dict:
        try:
            if psutil:
                memory = psutil.virtual_memory()
                available_gb = round(memory.available / (1024**3), 1)
                total_gb = round(memory.total / (1024**3), 1)
                return {"available": f"{available_gb}GB", "total": f"{total_gb}GB", "percent_used": memory.percent}
            else:
                return {"available": "Unknown (psutil not found)"}
        except:
            return {"available": "Unknown"}

    def _check_platform(self) -> dict:
        return {
            "system": platform.system(),
            "architecture": platform.architecture()[0],
            "python_version": platform.python_version()
        }

    def _check_screen_resolution(self) -> dict:
        """ตรวจสอบ resolution และ scale หน้าจอ"""
        try:
            # ตรวจสอบข้อมูลหน้าจอปัจจุบัน
            screen_info = self._detect_screen_info()
            current_width = screen_info["physical_width"]
            current_height = screen_info["physical_height"]
            scale_factor = screen_info["scale_factor"]
            
            current_resolution = f"{current_width}x{current_height}"
            
            # อ่านการตั้งค่าจาก settings.json
            saved_resolution = None
            resolution_mismatch = True  # ถือว่า mismatch ก่อนจนกว่าจะพิสูจน์ได้ว่าตรงกัน
            
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    
                # ลองหา resolution ในหลายจุด
                saved_resolution = (
                    settings.get("screen_resolution") or
                    settings.get("display_resolution") or
                    settings.get("resolution")
                )
                
                # ถ้าไม่มี อาจจะเก็บแยกเป็น width/height
                if not saved_resolution:
                    width = settings.get("screen_width") or settings.get("display_width")
                    height = settings.get("screen_height") or settings.get("display_height")
                    if width and height:
                        saved_resolution = f"{width}x{height}"
                
                # เปรียบเทียบ resolution
                if saved_resolution and saved_resolution == current_resolution:
                    resolution_mismatch = False
                    
            except Exception as e:
                pass
            
            # ถ้าไม่เจอข้อมูล resolution ใน settings ให้ถือว่า needs_fix
            if not saved_resolution:
                saved_resolution = "Not configured"
                resolution_mismatch = True
            
            # ตรวจสอบ scale (ควรเป็น 100% = 1.0)
            scale_warning = abs(scale_factor - 1.0) > 0.01  # tolerance สำหรับ floating point
            scale_percentage = round(scale_factor * 100)
            
            return {
                "current_resolution": current_resolution,
                "saved_resolution": saved_resolution,
                "resolution_mismatch": resolution_mismatch,
                "scale_factor": scale_factor,
                "scale_percentage": scale_percentage,
                "scale_warning": scale_warning,
                "method": screen_info["method"],
                "needs_fix": resolution_mismatch,
                "message": self._create_screen_message(current_resolution, saved_resolution, 
                                                     resolution_mismatch, scale_percentage, scale_warning)
            }
            
        except Exception as e:
            return {
                "current_resolution": "Unknown",
                "saved_resolution": "Unknown", 
                "resolution_mismatch": True,
                "scale_warning": False,
                "needs_fix": True,
                "error": str(e)[:50]
            }

    def _create_screen_message(self, current, saved, mismatch, scale_pct, scale_warn):
        """สร้างข้อความแสดงสถานะหน้าจอ"""
        lines = [f"• Resolution: {current}"]
        
        if mismatch:
            lines.append(f"  ⚠️ Settings: {saved} (mismatch)")
        elif saved != "Not set":
            lines.append(f"  ✓ Settings: {saved} (match)")
            
        if scale_warn:
            lines.append(f"  ❌ Scale: {scale_pct}% (should be 100%)")
        else:
            lines.append(f"  ✓ Scale: {scale_pct}%")
            
        return "\n".join(lines)

    def fix_resolution_settings(self) -> bool:
        """แก้ไขการตั้งค่า resolution ใน settings.json"""
        try:
            # ตรวจสอบ resolution ปัจจุบัน
            screen_info = self._detect_screen_info()
            current_resolution = f"{screen_info['physical_width']}x{screen_info['physical_height']}"
            
            # อ่าน settings.json
            settings = {}
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
            except:
                pass
            
            # อัพเดต resolution ในหลายจุดที่อาจมี
            settings["screen_resolution"] = current_resolution
            settings["display_resolution"] = current_resolution
            settings["screen_width"] = screen_info['physical_width']
            settings["screen_height"] = screen_info['physical_height']
            
            # บันทึกกลับไปยังไฟล์
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
                
            return True
            
        except Exception as e:
            return False
