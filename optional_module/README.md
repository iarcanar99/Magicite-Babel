# MBB Data Swap Tool - คู่มือการใช้งาน

## 📖 ภาพรวม
โปรแกรมเสริมสำหรับสลับข้อมูล NPC ระหว่างเกมต่างๆ ใน Magicite Babel

## 🚀 วิธีการใช้งาน

### 1. การเตรียมพร้อม
- ปิดโปรแกรม Magicite Babel ก่อนใช้งาน
- เตรียมไฟล์ข้อมูล NPC ของเกมต่างๆ (npc_*.json)

### 2. การติดตั้ง
```
1. คลิกไฟล์ build_swap_tool.bat
2. รอให้สร้าง MBB_Data_Swap_Tool.exe เสร็จ
3. เปิดไฟล์ .exe ที่สร้างขึ้น
```

### 3. การใช้งาน

#### 🔄 สลับข้อมูลเกม
1. **Select Folder** → เลือกโฟลเดอร์ที่มี npc.json
2. **Swap Data** → เลือกเกมที่ต้องการสลับไป
3. ยืนยันการสลับ

#### ➕ เพิ่มเกมใหม่
1. **เพิ่มเกมส์ใหม่** → ระบุชื่อเกม
2. โปรแกรมจะสร้างไฟล์ npc.json ใหม่อัตโนมัติ

## 📋 รูปแบบไฟล์ที่รองรับ

### ไฟล์ข้อมูล NPC ต้องมี:
```json
{
  "main_characters": [...],
  "npcs": [...],
  "lore": {...},
  "character_roles": {...},
  "_game_info": {
    "name": "ชื่อเกม",
    "code": "รหัสเกม",
    "description": "คำอธิบาย"
  }
}
```

## ⚠️ ข้อควรระวัง
- **ข้อมูลเดิมจะไม่หายไป** → จะเปลี่ยนชื่อเป็น npc_[รหัสเกม].json
- **ใช้กับโฟลเดอร์เดียวกับ MBB** → โดยปกติคือโฟลเดอร์หลักของโปรแกรม
- **หยุด MBB ก่อนสลับ** → ป้องกันปัญหาการอ่านไฟล์

## 🎮 ตัวอย่างการใช้งาน

### สลับจาก FFXIV ไป Monster Hunter:
```
1. เปิดโปรแกรม → Select Folder
2. Swap Data → เลือก "Monster Hunter"
3. ยืนยัน → ข้อมูล FFXIV จะกลายเป็น npc_ffxiv.json
4. ข้อมูล Monster Hunter จะกลายเป็น npc.json
```

### เพิ่มเกม Persona ใหม่:
```
1. เพิ่มเกมส์ใหม่ → ระบุ "Persona 5"
2. ข้อมูลเดิมจะเปลี่ยนชื่อ
3. สร้าง npc.json ใหม่สำหรับ Persona 5
```

## 🧪 การทดสอบระบบ

### ทดสอบไฟล์ NPC:
```bash
python test_npc_files.py
```

### ทดสอบการสลับข้อมูล (Command Line):
```bash
python test_swap.py
```

### ไฟล์ทดสอบที่มีให้:
- `npc.json` - Final Fantasy XIV (ไฟล์หลัก)
- `npc_genshin.json` - Genshin Impact
- `npc_monhun.json` - Monster Hunter  
- `npc_persona.json` - Persona 5
- `npc_wuwa.json` - Wuthering Waves

## 🔧 แก้ปัญหา

### ไม่สามารถสลับได้
- ตรวจสอบว่าไฟล์มีข้อมูล `_game_info`
- ปิดโปรแกรม MBB ก่อนสลับ
- รัน `test_npc_files.py` เพื่อตรวจสอบไฟล์

### ไม่พบไฟล์เกม
- ตรวจสอบว่าไฟล์อยู่ในโฟลเดอร์เดียวกัน
- ชื่อไฟล์ต้องขึ้นต้นด้วย "npc" และลงท้ายด้วย ".json"
- รัน `test_swap.py` เพื่อดูไฟล์ที่ตรวจพบ

### การทดสอบล้มเหลว
- ตรวจสอบไฟล์ JSON syntax ด้วย JSON validator
- ตรวจสอบว่ามี `_game_info` ครบถ้วน

---
*สร้างโดย MBB Optional Module - เวอร์ชัน 1.0*