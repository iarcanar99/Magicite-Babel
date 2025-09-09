"""
Command Line Swap Test - ทดสอบการสลับข้อมูลแบบง่าย
สำหรับทดสอบก่อนใช้ GUI จริง
"""

import sys
import os
import shutil

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from Manager import (
        get_files,
        get_game_info_from_json,
        swap_npc_files
    )
    print("[OK] Manager.py loaded successfully")
except ImportError as e:
    print(f"[ERROR] {e}")
    exit(1)

def list_available_files():
    """แสดงรายการไฟล์ NPC ที่มี"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    files = get_files(current_dir, ['.json'])
    npc_files = [f for f in files if 'npc' in f['name'].lower()]
    
    print("\n=== Available NPC Files ===")
    
    main_file = None
    other_files = []
    
    for file_info in npc_files:
        file_path = file_info['full_path']
        file_name = file_info['name']
        
        game_info = get_game_info_from_json(file_path)
        game_name = game_info['name'] if game_info else "Unknown"
        
        if file_name.lower() == 'npc.json':
            main_file = (file_path, file_name, game_name)
            print(f"[CURRENT] {file_name} -> {game_name}")
        else:
            other_files.append((file_path, file_name, game_name))
    
    print("\n[AVAILABLE]")
    for i, (file_path, file_name, game_name) in enumerate(other_files, 1):
        print(f"  {i}. {file_name} -> {game_name}")
    
    return main_file, other_files

def test_swap():
    """ทดสอบการสลับข้อมูล"""
    print("=== MBB Data Swap Test ===")
    
    main_file, other_files = list_available_files()
    
    if not main_file:
        print("[ERROR] npc.json not found!")
        return
    
    if not other_files:
        print("[ERROR] No other NPC files found!")
        return
    
    # ให้ผู้ใช้เลือกไฟล์ที่จะสลับ
    print(f"\nCurrent game: {main_file[2]}")
    print("Select game to swap to:")
    
    try:
        choice = input("Enter number (or 'q' to quit): ").strip()
        
        if choice.lower() == 'q':
            print("Test cancelled.")
            return
        
        choice_num = int(choice) - 1
        
        if choice_num < 0 or choice_num >= len(other_files):
            print("[ERROR] Invalid choice!")
            return
        
        target_file = other_files[choice_num]
        target_path = target_file[0]
        target_name = target_file[2]
        
        print(f"\nSwapping from '{main_file[2]}' to '{target_name}'...")
        
        # Backup ก่อนทดสอบ (เผื่อไฟล์เสีย)
        backup_dir = "backup_test"
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        main_backup = os.path.join(backup_dir, "npc.json.backup")
        target_backup = os.path.join(backup_dir, f"{os.path.basename(target_path)}.backup")
        
        shutil.copy2(main_file[0], main_backup)
        shutil.copy2(target_path, target_backup)
        print(f"[INFO] Backup created in {backup_dir}/")
        
        # ทดสอบการสลับ
        success, error_msg = swap_npc_files(main_file[0], target_path)
        
        if success:
            print(f"[SUCCESS] Swap completed!")
            print(f"- Previous '{main_file[2]}' data is now in npc_{get_game_info_from_json(main_backup)['code']}.json")
            print(f"- Current npc.json now contains '{target_name}' data")
            
            # แสดงสถานะหลังสลับ
            print("\n=== Post-swap Status ===")
            main_file_new, other_files_new = list_available_files()
            
        else:
            print(f"[FAILED] {error_msg}")
            
            # Restore backup หากล้มเหลว
            print("[INFO] Restoring from backup...")
            shutil.copy2(main_backup, main_file[0])
            shutil.copy2(target_backup, target_path)
            print("[INFO] Files restored.")
    
    except ValueError:
        print("[ERROR] Please enter a valid number!")
    except KeyboardInterrupt:
        print("\nTest cancelled by user.")
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")

if __name__ == "__main__":
    test_swap()
