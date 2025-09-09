# mbb_integration.py - วิธีเชื่อมต่อ Before Start UI กับ MBB

# 1. แก้ไขใน MBB.py - เพิ่มที่ด้านล่างสุดของไฟล์


def main():
    """Entry point ใหม่สำหรับ MBB"""
    # Import before_start_ui_improved (ใช้ตัวใหม่ที่ปรับปรุงแล้ว)
    try:
        from before_start.before_start_ui_improved import BeforeStartUI

        # รัน pre-start checks
        print("Running pre-start system check...")
        checker = BeforeStartUI()
        check_result = checker.run()

        # ตรวจสอบผลลัพธ์
        if not check_result["can_start"]:
            print("System check failed or cancelled by user")
            return

        # แสดง warnings ถ้ามี
        if check_result["force_start"]:
            print("Warning: Starting with unresolved issues")

    except ImportError:
        # ถ้าไม่มี before_start_ui_improved ให้ลองใช้ตัวเดิม
        try:
            from before_start.before_start_ui import BeforeStartUI
            
            print("Running pre-start system check...")
            checker = BeforeStartUI()
            check_result = checker.run()

            if not check_result["can_start"]:
                print("System check failed or cancelled by user")
                return

            if check_result["force_start"]:
                print("Warning: Starting with unresolved issues")
                
        except ImportError:
            # ถ้าไม่มี before_start_ui ให้ทำงานปกติ
            print("Before Start UI not found, starting normally...")
        except Exception as e:
            print(f"Error in pre-start check: {e}")
            # Continue anyway
    except Exception as e:
        print(f"Error in pre-start check: {e}")
        # Continue anyway

    # เริ่ม MBB ปกติ
    print("Starting MBB...")
    app = MagicBabelApp()
    app.mainloop()


# 2. แก้ไขส่วนท้ายของ MBB.py
if __name__ == "__main__":
    # เปลี่ยนจาก
    # app = MagicBabelApp()
    # app.mainloop()

    # เป็น
    main()


# 3. สร้าง launcher script ใหม่ (mbb_launcher.py)
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run
from MBB import main
main()
"""


# 4. สำหรับ .exe build - แก้ไข mbb.spec
"""
# ใน mbb.spec เพิ่ม before_start_ui และ dependencies

a = Analysis(
    ['mbb_launcher.py'],  # ใช้ launcher แทน
    pathex=[],
    binaries=[],
    datas=[
        ('before_start_ui.py', '.'),
        ('checkers/*.py', 'checkers'),
        ('api_tester.py', '.'),
        # ... other data files
    ],
    hiddenimports=[
        'before_start_ui',
        'checkers.api_checker',
        'checkers.system_checker', 
        'checkers.data_checker',
        'api_tester'
    ],
    # ... rest of config
)
"""


# 5. Quick bypass option - เพิ่มใน MBB.py
"""
# อ่าน command line arguments
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--skip-checks', action='store_true', 
                   help='Skip pre-start system checks')
args = parser.parse_args()

if not args.skip_checks:
    # Run before_start_ui
    pass
"""


# 6. Environment variable bypass
"""
# ใน main() function
if os.environ.get('MBB_SKIP_CHECKS') != '1':
    # Run checks
    pass
"""
