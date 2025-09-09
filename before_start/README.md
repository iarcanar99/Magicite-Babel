# MBB Before Start System

🎯 **ระบบตรวจสอบความพร้อมก่อนเริ่มใช้งาน MBB**

## ✨ ฟีเจอร์หลัก

- ✅ **ตรวจสอบ API Configuration** - ทดสอบการเชื่อมต่อ API จริง
- ✅ **ตรวจสอบ System Requirements** - หน้าจอ, GPU, Memory
- ✅ **ตรวจสอบ Data Files** - NPC.json, Settings, OCR Models
- ✅ **เชื่อมโยงกับระบบเดิม** - เปิด model.py, advance_ui.py, NPC Manager
- ✅ **Modern Dark UI** - ใช้ CustomTkinter

## 🚀 การใช้งาน

### เริ่มโปรแกรมปกติ (มี System Check):
```bash
python MBB.py
```

### ข้าม System Check:
```bash
python MBB.py --skip-checks
```

### ใช้ Environment Variable:
```bash
set MBB_SKIP_CHECKS=1
python MBB.py
```

### เปิด Before Start แยก:
```bash
cd Before_start
python before_start_ui.py
```

## 🛠️ การตั้งค่า API (แก้ไขปัญหาแล้ว!)

เมื่อกด "Configure" ในหน้า API Configuration:

### วิธีที่ 1 (แนะนำ):
```bash
python simple_model_config.py
```

### วิธีที่ 2 (Windows):
```
Double-click: model_config.bat
```

### วิธีที่ 3 (Manual):
แก้ไขไฟล์ `api_config.json`:
```json
{
  "api_key": "YOUR_API_KEY_HERE",
  "status": "active"
}
```

## 📁 โครงสร้างไฟล์

```
MBB_PROJECT/
├── Before_start/
│   ├── before_start_ui.py          # Main UI
│   ├── api_tester.py               # Real API testing
│   ├── checkpoint.md               # Development log
│   ├── USER_GUIDE.md               # User manual
│   └── checkers/
│       ├── api_checker.py          # API validation
│       ├── system_checker.py       # System check
│       └── data_checker.py         # Data files check
├── simple_model_config.py          # 🆕 Simple API config UI
├── model_launcher.py               # Model.py wrapper
├── model_config.bat                # Windows batch file
└── mbb_launcher.py                 # Alternative launcher
```

## 🔍 สถานะการตรวจสอบ

- **✅ Ready**: พร้อมใช้งาน
- **⚠️ Warning**: มีปัญหาเล็กน้อย (ใช้งานได้)  
- **❌ Error**: ต้องแก้ไขก่อนใช้งาน

## 🐛 Troubleshooting

### ปัญหา: ไม่สามารถเปิด Model Configuration ได้
**แก้ไข:** ใช้ `simple_model_config.py` แทน
```bash
python simple_model_config.py
```

### ปัญหา: Before Start UI ไม่ทำงาน
**แก้ไข:** ข้ามการตรวจสอบ
```bash
python MBB.py --skip-checks
```

### ปัญหา: API Connection Failed
**แก้ไข:** 
1. ตรวจสอบ API key ใน `api_config.json`
2. ตรวจสอบ internet connection
3. ลองใช้ VPN

## 🎉 สรุป

Before Start System ช่วยให้ผู้ใช้ใหม่สามารถตั้งค่า MBB ได้อย่างถูกต้องและง่ายดาย โดยมีระบบตรวจสอบหลายขั้นตอนและการแก้ไขปัญหาอัตโนมัติ

**การพัฒนาเสร็จสิ้น:** 2025-06-25 ✅
