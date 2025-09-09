"""
Simple test script for MBB Optional Module
ทดสอบฟังก์ชันพื้นฐานของโมดูลสลับข้อมูล
"""

import sys
import os

# เพิ่ม path เพื่อให้นำเข้าโมดูลได้
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from Manager import (
        get_files,
        read_json_file,
        get_game_info_from_json,
        format_size,
        format_timestamp
    )
    print("[OK] Manager.py imports successfully")
except ImportError as e:
    print(f"[ERROR] Manager.py import failed: {e}")

try:
    import PyQt5.QtWidgets
    print("[OK] PyQt5 is available")
except ImportError as e:
    print(f"[ERROR] PyQt5 import failed: {e}")

# Testing get_files function
print("\n[FOLDER] Testing get_files function:")
try:
    project_path = "C:/MBB_PROJECT"
    if os.path.exists(project_path):
        files = get_files(project_path, ['.json'])
        npc_files = [f for f in files if 'npc' in f['name'].lower()]
        print(f"Found {len(npc_files)} NPC files")
        
        for file in npc_files:
            print(f"  - {file['name']} ({format_size(file['size'])})")
    else:
        print(f"[ERROR] Project path not found: {project_path}")
except Exception as e:
    print(f"[ERROR] get_files test failed: {e}")

# Testing NPC file reading
print("\n[FILE] Testing NPC file reading:")
try:
    npc_path = "C:/MBB_PROJECT/npc.json"
    if os.path.exists(npc_path):
        data = read_json_file(npc_path)
        if data:
            print("[OK] npc.json loaded successfully")
            
            # Check game info
            game_info = get_game_info_from_json(npc_path)
            if game_info:
                print(f"[OK] Game info found: {game_info['name']}")
            else:
                print("[WARNING] No game info in npc.json")
        else:
            print("[ERROR] Failed to load npc.json")
    else:
        print(f"[ERROR] npc.json not found at: {npc_path}")
except Exception as e:
    print(f"[ERROR] NPC file test failed: {e}")

print("\n[RESULT] Test Summary:")
print("If all tests show [OK], the module is ready to use!")
print("If any test shows [ERROR], please check the dependencies or file paths.")
