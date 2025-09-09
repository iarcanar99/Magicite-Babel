# Before Start System - User Guide

## 🚀 การใช้งาน Before Start System

### วิธีเริ่มใช้งาน

#### 1. เริ่มโปรแกรมปกติ (มี Before Start Check)
```bash
python MBB.py
```
หรือ
```bash
python mbb_launcher.py
```

#### 2. ข้าม Before Start Check
```bash
python MBB.py --skip-checks
```

#### 3. ข้ามด้วย Environment Variable
```bash
set MBB_SKIP_CHECKS=1
python MBB.py
```

### ระบบตรวจสอบ

#### 🔑 API Configuration
- ตรวจสอบไฟล์ `api_config.json` และ `settings.json`
- ทดสอบการเชื่อมต่อ API จริง
- แสดงสถานะ quota/credit
- **Action**: คลิก "Configure" เพื่อเปิด `model.py`

#### 💻 System Requirements  
- ตรวจสอบความละเอียดหน้าจอ
- ตรวจสอบ GPU/CUDA availability
- ตรวจสอบ memory ที่ใช้ได้
- **Action**: คลิก "Fix" เพื่อเปิด `advance_ui.py`

#### 📁 Data Files
- ตรวจสอบ `npc.json` format และความถูกต้อง
- ตรวจสอบ `settings.json`
- ตรวจสอบ EasyOCR models
- **Action**: คลิก "Manage" เพื่อเปิด NPC Manager

### สถานะการตรวจสอบ

- ✅ **Ready**: พร้อมใช้งาน
- ⚠️ **Warning**: มีปัญหาเล็กน้อย (สามารถใช้งานได้)
- ❌ **Error**: มีปัญหาที่ต้องแก้ไข

### ปุ่มต่างๆ

- **Configure/Fix/Manage**: เปิดไฟล์/โปรแกรมที่เกี่ยวข้อง
- **Skip Checks**: ข้ามการตรวจสอบและเริ่มโปรแกรมทันที
- **Start MBB**: เริ่มโปรแกรมหลัก (เปิดได้เมื่อผ่านการตรวจสอบ)

## 🔧 การพัฒนาและ Customization

### โครงสร้างไฟล์
```
Before_start/
├── before_start_ui.py      # Main UI
├── api_tester.py           # API testing utility
├── mbb_integration.py      # Integration guide
├── checkpoint.md           # Development progress
└── checkers/
    ├── __init__.py
    ├── api_checker.py      # API validation
    ├── system_checker.py   # System requirements
    └── data_checker.py     # Data files validation
```

### เพิ่ม Checker ใหม่

1. สร้างไฟล์ใน `checkers/` folder
2. สร้าง class ที่มี method `check_all()` 
3. Return format: `{"status": "ready/warning/error", "details": {}, "summary": "..."}`
4. เพิ่ม import ใน `before_start_ui.py`

### Customize UI

- แก้ไข `_create_check_section()` เพื่อเพิ่มส่วนตรวจสอบใหม่
- แก้ไข `_update_summary()` เพื่อปรับเกณฑ์การผ่าน/ไม่ผ่าน
- เพิ่ม action buttons ใน update methods

## 🐛 Troubleshooting

### ปัญหาที่พบบ่อย

1. **ModuleNotFoundError**: ติดตั้ง dependencies ที่ขาด
2. **FileNotFoundError**: ตรวจสอบ path ของไฟล์ config
3. **UnicodeError**: ใช้ encoding='utf-8' ในการอ่านไฟล์
4. **API Connection Failed**: ตรวจสอบ API key และ network

### Debug Mode

เพิ่ม debug output โดยแก้ไข:
```python
# ใน before_start_ui.py
print(f"Debug: {result}")
```

## 📈 Future Enhancements

- Auto-fix capabilities
- Background health monitoring  
- Config backup/restore
- Advanced diagnostics
- Cloud integration
## 🐛 Troubleshooting

### ปัญหาที่พบบ่อย

#### 1. **ไม่สามารถเปิด model.py ได้**
**อาการ:** คลิก "Configure" แล้วขึ้น error "name 'os' is not defined"

**วิธีแก้ไข:**
- **Windows (วิธีง่ายที่สุด):** Double-click ไฟล์ `model_config.bat` ในโฟลเดอร์โปรเจ็ค
- **วิธีทั่วไป:** 
  1. เปิด Command Prompt/Terminal
  2. `cd C:\MBB_PROJECT` (เปลี่ยนเป็น path โปรเจ็คของคุณ)
  3. `python model.py`

#### 2. **ModuleNotFoundError**
**วิธีแก้ไข:** ติดตั้ง dependencies ที่ขาด
```bash
pip install -r requirements.txt
```

#### 3. **FileNotFoundError**
**วิธีแก้ไข:** ตรวจสอบ path ของไฟล์ config และรันจากโฟลเดอร์โปรเจ็คหลัก

#### 4. **UnicodeError**
**วิธีแก้ไข:** ตรวจสอบให้แน่ใจว่าไฟล์ JSON ใช้ encoding UTF-8

#### 5. **API Connection Failed**
**วิธีแก้ไข:** 
- ตรวจสอบ API key ใน `api_config.json`
- ตรวจสอบการเชื่อมต่อ internet
- ลองใช้ VPN ถ้าพบปัญหา region lock

### 🛠️ Emergency Fixes

#### หาก Before Start UI ไม่ทำงาน:
```bash
# ข้ามการตรวจสอบและเริ่มโปรแกรมโดยตรง
python MBB.py --skip-checks

# หรือใช้ environment variable
set MBB_SKIP_CHECKS=1
python MBB.py
```

#### หาก model.py ไม่เปิด:
```bash
# Windows: ใช้ batch file
model_config.bat

# หรือรันโดยตรง
cd C:\MBB_PROJECT
python model.py
```

### 📞 Debug Mode

เพิ่ม debug output โดยแก้ไข `before_start_ui.py`:
```python
# ใน _run_checks_thread()
print(f"Debug API: {api_result}")
print(f"Debug System: {system_result}")
print(f"Debug Data: {data_result}")
```

### 🔄 Reset Configuration

หาก config file เสียหาย:
1. Backup `settings.json` และ `api_config.json`
2. ลบไฟล์เก่า
3. เริ่มโปรแกรมใหม่ (จะสร้าง default config)
4. ตั้งค่าใหม่ผ่าน UI

