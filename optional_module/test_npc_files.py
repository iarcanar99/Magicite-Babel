"""
Test script for Optional Module NPC files
ทดสอบไฟล์ NPC ในโฟลเดอร์ optional_module โดยเฉพาะ
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from Manager import (
        get_files,
        read_json_file,
        get_game_info_from_json,
        format_size
    )
    print("[OK] Manager.py imports successfully")
except ImportError as e:
    print(f"[ERROR] Manager.py import failed: {e}")
    exit(1)

# Test files in optional_module directory
print("\n[TEST] Testing NPC files in optional_module:")

current_dir = os.path.dirname(os.path.abspath(__file__))
files = get_files(current_dir, ['.json'])
npc_files = [f for f in files if 'npc' in f['name'].lower()]

print(f"Found {len(npc_files)} NPC files in optional_module:")

# Test each NPC file
for file_info in npc_files:
    file_path = file_info['full_path']
    file_name = file_info['name']
    file_size = format_size(file_info['size'])
    
    print(f"\n--- Testing {file_name} ({file_size}) ---")
    
    # Test JSON loading
    try:
        data = read_json_file(file_path)
        if data:
            print(f"  [OK] JSON loaded successfully")
            
            # Check required sections
            required_sections = ['main_characters', 'npcs', 'lore', 'character_roles', '_game_info']
            missing_sections = []
            
            for section in required_sections:
                if section not in data:
                    missing_sections.append(section)
                else:
                    count = len(data[section]) if isinstance(data[section], (list, dict)) else "N/A"
                    print(f"  [OK] {section}: {count} items")
            
            if missing_sections:
                print(f"  [WARNING] Missing sections: {missing_sections}")
            
            # Check game info specifically
            game_info = get_game_info_from_json(file_path)
            if game_info:
                print(f"  [OK] Game: {game_info['name']} (code: {game_info['code']})")
            else:
                print(f"  [ERROR] No game info found!")
                
        else:
            print(f"  [ERROR] Failed to load JSON")
            
    except Exception as e:
        print(f"  [ERROR] Exception: {e}")

print(f"\n[SUMMARY] Tested {len(npc_files)} NPC files")
print("Ready for swap testing!")
