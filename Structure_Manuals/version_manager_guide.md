# 🔄 Version Manager Usage Guide

## การใช้งาน Version Manager แบบรวมศูนย์

### 📁 ไฟล์หลัก: `version_manager.py`
ไฟล์นี้เป็นจุดควบคุมเวอร์ชั่นเดียวของทั้งโปรเจ็ค

### 🎯 การแสดงผลเวอร์ชั่น

#### หน้าหลัก MBB
```python
from version_manager import get_mbb_version
from appearance import appearance_manager

# แสดงผล: V-9.1 
version_text = get_mbb_version()

# สีตาม theme จาก appearance_manager
version_color = appearance_manager.get_theme_color('accent', '#A020F0')
```

#### หน้า Settings  
```python
from version_manager import get_settings_version

# แสดงผล: MBB v9.1 build 19072025 | by iarcanar
version_text = get_settings_version()
```

### ⚙️ การอัพเดตเวอร์ชั่น

#### 1. แก้ไขบัค/ปรับปรุงระบบเดิม
```python
# แก้ไขใน version_manager.py
self.BUILD_REVISION = "02"  # เปลี่ยนจาก "01" เป็น "02"
```

#### 2. เพิ่มฟีเจอร์ใหม่
```python
# แก้ไขใน version_manager.py  
self.MINOR_VERSION = "2"        # เปลี่ยนจาก "1" เป็น "2"
self.BUILD_DATE = "20072025"    # วันที่ใหม่
self.BUILD_REVISION = "01"      # รีเซ็ตเป็น "01"
```

#### 3. อัพเดตเป็นวันปัจจุบันแบบอัตโนมัติ
```python
from version_manager import version_manager

# อัพเดตเป็นวันนี้ ครั้งแรก
version_manager.update_build_today("01")

# อัพเดตเป็นวันนี้ ครั้งที่ 2
version_manager.update_build_today("02")
```

### 📋 ขั้นตอนการอัพเดตเวอร์ชั่น (บังคับทำทุกครั้ง)

1. **แก้ไข** `version_manager.py`
   - `BUILD_DATE` = วันที่ปัจจุบัน
   - `BUILD_REVISION` = ลำดับการแก้ไข  
   - `MINOR_VERSION` = เพิ่มถ้ามีฟีเจอร์ใหม่

2. **ตรวจสอบ** การแสดงผล
   - หน้าหลัก MBB: `V-9.1`
   - หน้า Settings: `MBB v9.1 build 19072025 | by iarcanar`

3. **อัพเดต** `Structure.md`
   - Current Version ในส่วน Version Management Protocol

4. **ลบ** คู่มือที่ไม่ใช้ (ถ้ามี)

### 🎨 Theme Color สำหรับเวอร์ชั่น
```python
theme_colors = {
    "default": "#A020F0",  # สีม่วง
    "dark": "#A020F0", 
    "blue": "#4169E1",
    "green": "#32CD32",
    "red": "#FF4500",
    "purple": "#A020F0"
}
```

### 📝 ตัวอย่างการแก้ไข

#### วันที่ 19/07/2025 - แก้ไขครั้งที่ 1
```python
self.BUILD_DATE = "19072025"
self.BUILD_REVISION = "01"
```

#### วันที่ 19/07/2025 - แก้ไขครั้งที่ 2  
```python
self.BUILD_DATE = "19072025"
self.BUILD_REVISION = "02"
```

#### วันที่ 20/07/2025 - เพิ่มฟีเจอร์ใหม่
```python
self.MINOR_VERSION = "2"        # เพิ่มจาก "1"
self.BUILD_DATE = "20072025"    
self.BUILD_REVISION = "01"      # รีเซ็ต
```

### ✅ ประโยชน์ของระบบใหม่
- **รวมศูนย์**: แก้ไขเวอร์ชั่นจากจุดเดียว
- **สีตาม Theme**: หน้าหลักใช้สีตาม theme อัตโนมัติ
- **แสดงผลชัดเจน**: หน้าหลักแสดงแค่ V-9.1, Settings แสดงแบบเต็ม
- **Protocol ชัด**: มีกติกาการอัพเดตที่ชัดเจน
- **ไม่พลาด**: ขั้นตอนบังคับป้องกันการลืมอัพเดต
