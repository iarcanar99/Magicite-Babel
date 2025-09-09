# แผนพัฒนา Before Start UI - ระบบตรวจสอบก่อนเริ่ม MBB

## 🎯 วัตถุประสงค์
สร้างระบบตรวจสอบความพร้อมก่อนเริ่มโปรแกรม MBB เพื่อป้องกันปัญหาที่เกิดจากการตั้งค่าไม่ถูกต้อง โดยเฉพาะ API key ที่ผิดพลาด

## 📋 ขอบเขตการตรวจสอบ

### 1. **API Configuration Check**
- ตรวจสอบไฟล์ `api_keys.json` มีอยู่หรือไม่
- ตรวจสอบ format ของ API keys
- **ทดสอบการเชื่อมต่อ API จริง** (ส่ง test request)
- แสดงสถานะ quota/credit คงเหลือ (ถ้า API รองรับ)

### 2. **System Requirements Check**
- ตรวจสอบความละเอียดหน้าจอ
- ตรวจสอบ GPU/CUDA availability (สำหรับ EasyOCR)
- ตรวจสอบ memory ที่ใช้ได้
- ตรวจสอบ dependencies ที่จำเป็น

### 3. **Data Files Check**
- ตรวจสอบ `NPC.json` format และความถูกต้อง
- ตรวจสอบ `settings.json`
- ตรวจสอบ models สำหรับ EasyOCR
- ตรวจสอบไฟล์ icons และ resources

## 🏗️ โครงสร้าง UI

### Main Window Layout
```
┌─────────────────────────────────────────┐
│      MBB Pre-Start System Check         │
├─────────────────────────────────────────┤
│                                         │
│  [✓] API Configuration      [Config]    │
│      Gemini API: Ready                  │
│      Quota: 1M tokens remaining         │
│                                         │
│  [✗] Screen Resolution      [Fix]       │
│      Current: 1920x1080                 │
│      Expected: 2560x1440                │
│                                         │
│  [✓] NPC Database          [View]       │
│      File: Valid (125 entries)          │
│                                         │
│  [!] GPU/CUDA              [Info]       │
│      CPU Mode (Slower performance)      │
│                                         │
│  ─────────────────────────────────      │
│                                         │
│  Overall Status: 2 Issues Found         │
│                                         │
│  [Fix All Issues]    [Skip]   [Start]   │
└─────────────────────────────────────────┘
```

## 🔧 Technical Implementation

### File Structure
```
before_start_ui.py     # Main UI และ orchestrator
├── checkers/
│   ├── api_checker.py      # ตรวจสอบ API
│   ├── system_checker.py   # ตรวจสอบระบบ
│   └── data_checker.py     # ตรวจสอบไฟล์ข้อมูล
├── fixers/
│   ├── api_fixer.py        # แก้ไข/ตั้งค่า API
│   ├── screen_fixer.py     # แก้ไขการตั้งค่าหน้าจอ
│   └── data_fixer.py       # แก้ไขไฟล์ข้อมูล
└── utils/
    ├── api_tester.py       # ทดสอบ API จริง
    └── logger.py           # บันทึก log
```

### Check Results Structure
```python
{
    "api_check": {
        "status": "ready|warning|error",
        "details": {
            "gemini": {"connected": True, "quota": "1M tokens"},
            "gpt": {"connected": False, "error": "Invalid API key"},
            "claude": {"connected": True, "quota": "100K tokens"}
        },
        "action_needed": "Configure GPT API key"
    },
    "system_check": {
        "status": "warning",
        "details": {
            "screen": {"current": "1920x1080", "expected": "2560x1440"},
            "gpu": {"cuda": False, "message": "Running in CPU mode"},
            "memory": {"available": "8GB", "recommended": "16GB"}
        }
    },
    "data_check": {
        "status": "ready",
        "details": {
            "npc_json": {"valid": True, "entries": 125},
            "settings": {"valid": True},
            "models": {"downloaded": True}
        }
    }
}
```

## 📱 Features

### 1. **Smart Detection**
- Auto-detect ปัญหาที่พบบ่อย
- แนะนำวิธีแก้ไขที่เหมาะสม
- จำ settings ที่เคยแก้ไข

### 2. **Quick Actions**
- **[Config]** - เปิด model.py สำหรับตั้งค่า API
- **[Fix]** - เปิด advance_ui.py สำหรับตั้งค่าหน้าจอ
- **[View]** - เปิด NPC Manager
- **[Info]** - แสดงข้อมูลเพิ่มเติม

### 3. **Skip Options**
- Skip specific checks
- "Don't show again" สำหรับ warnings
- Force start แม้มี errors (พร้อม warning)

### 4. **API Test Features**
```python
async def test_gemini_api(api_key):
    """ทดสอบ Gemini API"""
    try:
        # ส่ง minimal request
        response = await gemini_client.generate_content(
            "Test connection",
            generation_config={"max_output_tokens": 10}
        )
        
        # ตรวจสอบ quota (ถ้า API support)
        quota_info = await gemini_client.get_quota_info()
        
        return {
            "status": "connected",
            "response_time": "120ms",
            "quota": quota_info
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "suggestion": "Please check your API key"
        }
```

## 🎨 UI Design Principles

### 1. **Clear Visual Feedback**
- ✅ Green = Ready
- ⚠️ Yellow = Warning (can proceed)
- ❌ Red = Error (should fix)
- ℹ️ Blue = Information

### 2. **Progressive Disclosure**
- แสดงเฉพาะปัญหาที่สำคัญ
- ซ่อนรายละเอียดที่ไม่จำเป็น
- ขยายดูรายละเอียดเมื่อคลิก

### 3. **Actionable Messages**
- ไม่แค่บอกว่ามีปัญหา
- บอกวิธีแก้ไขที่ชัดเจน
- มีปุ่มนำทางไปยังที่ต้องแก้ไข

## 🚀 Implementation Steps

### Phase 1: Core Checking System
1. สร้าง `before_start_ui.py` พื้นฐาน
2. Implement API checker with real testing
3. Implement system checker
4. Implement data checker

### Phase 2: UI Development
1. สร้าง GUI with customtkinter
2. เพิ่ม progress indicators
3. เพิ่ม action buttons
4. เพิ่ม animations และ transitions

### Phase 3: Integration
1. แก้ไข MBB.py ให้เรียก before_start_ui ก่อน
2. เพิ่ม command line arguments
3. เพิ่ม auto-fix capabilities
4. เพิ่ม logging และ diagnostics

### Phase 4: Enhancement
1. Cache test results
2. Background checking while running
3. Auto-update checks
4. Export diagnostic reports

## 🔄 Integration with MBB

### Modified MBB startup flow:
```python
def main():
    # 1. เรียก Before Start UI
    checker = BeforeStartUI()
    check_result = checker.run_checks()
    
    # 2. ถ้าไม่ผ่านและผู้ใช้ไม่ force start
    if not check_result.passed and not check_result.force_start:
        return
    
    # 3. เริ่ม MBB ปกติ
    app = MagicBabelApp()
    app.run()
```

## 📊 Success Metrics

1. **ลดปัญหา API key ผิด** > 90%
2. **ลดเวลา troubleshooting** > 70%
3. **User satisfaction** เพิ่มขึ้น
4. **Support tickets** ลดลง

## 🛡️ Error Prevention

### Common Issues to Catch:
1. **Invalid API Keys**
   - Wrong format
   - Expired keys
   - Wrong API selected

2. **Screen Resolution Mismatch**
   - Game on different monitor
   - Scaling issues
   - Multi-monitor setup

3. **Missing Dependencies**
   - EasyOCR models
   - CUDA libraries
   - Required fonts

4. **Corrupted Data Files**
   - Invalid JSON format
   - Missing required fields
   - Encoding issues

## 📝 Future Enhancements

1. **Cloud Config Sync**
   - Backup settings to cloud
   - Share configs between PCs
   - Quick restore

2. **Auto-Fix System**
   - Download missing models
   - Auto-correct JSON files
   - Update dependencies

3. **Health Monitoring**
   - Real-time system monitoring
   - Performance metrics
   - Usage statistics

4. **Guided Setup Wizard**
   - First-time user experience
   - Step-by-step configuration
   - Video tutorials integration