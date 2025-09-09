# MBB Optional Module - Package Summary

## 📦 ส่วนประกอบของแพ็คเกจ

### ไฟล์หลัก
- `Manager.py` - ยูทิลิตี้ฟังก์ชันสำหรับจัดการไฟล์และสลับข้อมูล
- `swap_data.py` - GUI หลักสำหรับการสลับข้อมูล NPC
- `last_directory.txt` - เก็บตำแหน่งโฟลเดอร์ล่าสุด

### ไฟล์สำหรับการใช้งาน
- `build_swap_tool.bat` - ไฟล์ bat สำหรับสร้างโปรแกรม exe
- `README.md` - คู่มือการใช้งานสำหรับผู้ใช้
- `PACKAGE_INFO.md` - ไฟล์นี้

### ไฟล์ทดสอบ
- `test_module.py` - ทดสอบโมดูลพื้นฐาน
- `test_npc_files.py` - ทดสอบไฟล์ NPC ใน optional_module
- `test_swap.py` - ทดสอบการสลับข้อมูลแบบ command line

### ไฟล์ข้อมูลทดสอบ
- `npc.json` - Final Fantasy XIV (ไฟล์หลัก)
- `npc_genshin.json` - Genshin Impact
- `npc_monhun.json` - Monster Hunter
- `npc_persona.json` - Persona 5  
- `npc_wuwa.json` - Wuthering Waves

## ✅ การทดสอบความพร้อม

### ผลการทดสอบไฟล์ NPC (ล่าสุด):
```
[OK] Manager.py imports successfully
[TEST] Testing NPC files in optional_module:
Found 5 NPC files in optional_module:

--- Testing npc.json (3.41 KB) ---
  [OK] JSON loaded successfully
  [OK] main_characters: 4 items
  [OK] npcs: 4 items  
  [OK] lore: 5 items
  [OK] character_roles: 6 items
  [OK] _game_info: 3 items
  [OK] Game: Final Fantasy XIV (code: ffxiv)

--- Testing npc_genshin.json (3.4 KB) ---
  [OK] Game: Genshin Impact (code: genshin)

--- Testing npc_monhun.json (3.45 KB) ---
  [OK] Game: Monster Hunter (code: monhun)

--- Testing npc_persona.json (3.43 KB) ---
  [OK] Game: Persona 5 (code: persona)

--- Testing npc_wuwa.json (3.42 KB) ---
  [OK] Game: Wuthering Waves (code: wuwa)

[SUMMARY] Tested 5 NPC files - Ready for swap testing!
```

### วิธีทดสอบ:
```bash
# ทดสอบไฟล์ NPC
python test_npc_files.py

# ทดสอบการสลับ (Command Line)
python test_swap.py
```

## 🚀 วิธีการใช้งาน

### สำหรับผู้ใช้ทั่วไป:
1. รัน `build_swap_tool.bat`
2. ใช้ไฟล์ .exe ที่สร้างขึ้น
3. อ่านคู่มือใน `README.md`

### สำหรับผู้พัฒนา:
1. รัน `test_module.py` เพื่อทดสอบ
2. ใช้ `python swap_data.py` เพื่อทดสอบ GUI
3. ปรับแต่งไฟล์ตามต้องการ

## 🔧 Dependencies

### Python Packages:
- PyQt5 (GUI framework)
- json (built-in, สำหรับจัดการไฟล์ JSON)
- os, sys, time (built-in)

### External Tools:
- PyInstaller (สำหรับสร้าง exe)

## 📁 โครงสร้างข้อมูล

### ไฟล์ NPC ต้องมี:
```json
{
  "_game_info": {
    "name": "ชื่อเกม",
    "code": "รหัสเกม", 
    "description": "คำอธิบาย"
  }
}
```

## 🎯 Status: READY FOR DISTRIBUTION

### ✅ เสร็จสมบูรณ์:
- [x] โมดูลหลักทำงานได้ปกติ
- [x] GUI ทำงานได้สมบูรณ์
- [x] ไฟล์ build script พร้อมใช้งาน
- [x] คู่มือการใช้งานครบถ้วน
- [x] ผ่านการทดสอบแล้ว
- [x] ไฟล์ทดสอบครบชุด (5 เกม)
- [x] ระบบทดสอบการสลับพร้อมใช้งาน

### 🎮 เกมที่มีไฟล์ทดสอบ:
- **Final Fantasy XIV** (npc.json) - ไฟล์หลัก
- **Genshin Impact** (npc_genshin.json)
- **Monster Hunter** (npc_monhun.json)
- **Persona 5** (npc_persona.json)
- **Wuthering Waves** (npc_wuwa.json)

### 🧪 เครื่องมือทดสอบ:
- `test_npc_files.py` - ตรวจสอบไฟล์ NPC ทั้งหมด
- `test_swap.py` - ทดสอบการสลับแบบ command line
- ระบบ backup อัตโนมัติระหว่างทดสอบ

---
*MBB Optional Module v1.0 - พร้อมเผยแพร่*