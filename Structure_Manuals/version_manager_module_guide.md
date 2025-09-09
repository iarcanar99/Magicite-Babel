# 🔄 Version Manager Guide

**ไฟล์:** `version_manager.py`  
**คลาสหลัก:** `VersionManager`  

## 🎯 Overview
Version Manager เป็นระบบจัดการเวอร์ชั่นแบบรวมศูนย์สำหรับ MBB ที่ช่วยควบคุมเลขเวอร์ชั่น, build number, และการแสดงผลเวอร์ชั่นในส่วนต่างๆ ของแอปพลิเคชัน

## 🏗️ Architecture

### 📋 Core Class Structure

```python
class VersionManager:
    def __init__(self):
        # *** MAIN VERSION CONTROL CENTER ***
        self.MAJOR_VERSION = "9"          # เวอร์ชั่นหลัก
        self.MINOR_VERSION = "1"          # เวอร์ชั่นย่อย  
        self.BUILD_DATE = "19072025"      # วันที่ build (DDMMYYYY)
        self.BUILD_REVISION = "04"        # ลำดับการแก้ไขในวัน
        
        # ข้อมูลโปรเจ็ค
        self.AUTHOR = "iarcanar"
        self.PROJECT_NAME = "MBB" 
        self.FULL_PROJECT_NAME = "Magicite Babel"
```

## 📊 Version Schema

### 🔢 Version Number Format
```
v{MAJOR}.{MINOR} build {BUILD_DATE}.{BUILD_REVISION}

Example: v9.1 build 19072025.04
```

### 📅 Build Number Format
```
{DD}{MM}{YYYY}.{XX}

Where:
- DD: วัน (01-31)
- MM: เดือน (01-12) 
- YYYY: ปี (2025)
- XX: ลำดับการแก้ไขในวัน (01-99)

Example: 19072025.04 = 19 July 2025, revision 04
```

## 🎯 Version Properties

### 📱 Display Formats

#### 1. **MBB Main Display** (`version_display_mbb`)
```python
@property
def version_display_mbb(self):
    """แสดงบนหน้าหลัก MBB เช่น V-9.1"""
    return f"V-{self.version_number}"

# Output: "V-9.1"
```

#### 2. **Settings Page Display** (`version_display_settings`)
```python
@property  
def version_display_settings(self):
    """แสดงบนหน้า Settings แบบเต็ม"""
    return f"{self.PROJECT_NAME} v{self.version_number} build {self.build_number} | by {self.AUTHOR}"

# Output: "MBB v9.1 build 19072025.04 | by iarcanar"
```

#### 3. **Version Number** (`version_number`)
```python
@property
def version_number(self):
    """เลขเวอร์ชั่นแบบสั้น เช่น 9.1"""
    return f"{self.MAJOR_VERSION}.{self.MINOR_VERSION}"

# Output: "9.1"
```

#### 4. **Build Number** (`build_number`)
```python
@property
def build_number(self):
    """Build number แบบเต็ม เช่น 19072025.04"""
    return f"{self.BUILD_DATE}.{self.BUILD_REVISION}"

# Output: "19072025.04"
```

## 🔧 Version Management Methods

### 📅 Build Date Management
```python
def update_build_today(self, revision="01"):
    """อัพเดต build เป็นวันที่ปัจจุบัน"""
    today = datetime.datetime.now()
    self.BUILD_DATE = today.strftime("%d%m%Y")
    self.BUILD_REVISION = revision
    return self.build_number

# Usage:
version_manager.update_build_today("01")  # 25072025.01
version_manager.update_build_today("02")  # 25072025.02
```

### 🔢 Version Incrementing
```python
def increment_minor_version(self):
    """เพิ่ม minor version (สำหรับฟีเจอร์ใหม่)"""
    current_minor = int(self.MINOR_VERSION)
    if current_minor < 9:
        self.MINOR_VERSION = str(current_minor + 1)
    return self.version_number

# Usage:
# v9.1 → v9.2
# v9.8 → v9.9
# v9.9 → v9.9 (max limit)
```

## 📋 Version Information

### 🗂️ Full Version Info
```python
@property
def version_full_info(self):
    """ข้อมูลเวอร์ชั่นแบบเต็ม"""
    return {
        "project_name": "MBB",
        "full_project_name": "Magicite Babel",
        "major": "9",
        "minor": "1", 
        "build_date": "19072025",
        "build_revision": "04",
        "version_number": "9.1",
        "build_number": "19072025.04",
        "author": "iarcanar",
        "display_mbb": "V-9.1",
        "display_settings": "MBB v9.1 build 19072025.04 | by iarcanar"
    }
```

## 🔌 Global Functions

### 📡 Export Functions
```python
def get_version_info():
    """ฟังก์ชันสำหรับเรียกใช้ข้อมูลเวอร์ชั่น"""
    return version_manager.version_full_info

def get_mbb_version():
    """เวอร์ชั่นสำหรับแสดงบนหน้าหลัก MBB"""
    return version_manager.version_display_mbb

def get_settings_version():
    """เวอร์ชั่นสำหรับแสดงบนหน้า Settings"""
    return version_manager.version_display_settings
```

### 📦 Module Exports
```python
__all__ = [
    'VersionManager',        # คลาสหลัก
    'version_manager',       # instance สำหรับใช้งาน
    'get_version_info',      # ข้อมูลเวอร์ชั่นเต็ม
    'get_mbb_version',       # แสดงบนหน้าหลัก
    'get_settings_version'   # แสดงบนหน้า Settings
]
```

## 🎯 Version Update Protocol

### 📋 Update Guidelines

#### 🔢 **Version Number Rules**
```python
# Major Version (9.x): เปลี่ยนเมื่อมีการปรับปรุงใหญ่
MAJOR_VERSION = "9"  # Current major version

# Minor Version (x.1-x.9): เพิ่มเมื่อมีโมดูลใหม่หรือฟีเจอร์ใหม่  
MINOR_VERSION = "1"  # Current: v9.1

# Build Number (DDMMYYYY.XX): อัพเดตทุกครั้งที่แก้ไข
BUILD_DATE = "19072025"     # 19 July 2025
BUILD_REVISION = "04"       # 4th revision of the day
```

#### 📅 **Build Number Protocol** 
```python
# Format: วันที่.ลำดับการแก้ไข
# Example: 19072025.01 = 19 July 2025, 1st revision

# วันนี้แก้ไขครั้งที่ 1
"19072025.01"

# วันนี้แก้ไขครั้งที่ 2  
"19072025.02"

# วันใหม่ รีเซ็ตเป็น 01
"20072025.01"
```

#### ⚙️ **การอัพเดตเวอร์ชั่น - ขั้นตอนบังคับ**
```python
# 1. อัพเดต version_manager.py
self.BUILD_DATE = "20072025"      # วันที่ใหม่
self.BUILD_REVISION = "01"        # รีเซ็ตเป็น 01

# 2. ตรวจสอบการแสดงผลใน MBB.py และ settings.py
get_mbb_version()      # V-9.1
get_settings_version() # MBB v9.1 build 20072025.01 | by iarcanar

# 3. อัพเดต Structure.md
Current Version: v9.1 build 20072025.01

# 4. ลบคู่มือเก่าที่ไม่ใช้ (ถ้ามี)
```

### 🎯 **การแสดงผลเวอร์ชั่น**

#### 📱 **หน้าหลัก MBB**
```python
# แสดงเป็น: V-9.1 (สีตาม theme)
version_label.config(text=get_mbb_version())
```

#### ⚙️ **หน้า Settings**  
```python
# แสดงเป็น: MBB v9.1 build 19072025.04 | by iarcanar
settings_version_label.config(text=get_settings_version())
```

## 🚀 Usage Examples

### 🔧 Basic Usage
```python
from version_manager import get_mbb_version, get_settings_version, get_version_info

# แสดงเวอร์ชั่นบนหน้าหลัก
mbb_version = get_mbb_version()
print(mbb_version)  # V-9.1

# แสดงเวอร์ชั่นบนหน้า Settings
settings_version = get_settings_version()  
print(settings_version)  # MBB v9.1 build 19072025.04 | by iarcanar

# ดึงข้อมูลเวอร์ชั่นทั้งหมด
version_info = get_version_info()
print(version_info["version_number"])  # 9.1
print(version_info["build_number"])    # 19072025.04
```

### ⚙️ Advanced Usage
```python
from version_manager import version_manager, VersionManager

# ใช้ global instance
current_version = version_manager.version_number
current_build = version_manager.build_number

# สร้าง instance ใหม่สำหรับการทดสอบ
test_version = VersionManager()
test_version.update_build_today("99")
print(test_version.build_number)  # 25072025.99

# เพิ่ม minor version
test_version.increment_minor_version()
print(test_version.version_number)  # 9.2
```

### 🎯 Integration Examples
```python
# ใน MBB.py
from version_manager import get_mbb_version

class MagicBabelApp:
    def create_main_ui(self):
        version_label = tk.Label(
            self.root,
            text=get_mbb_version(),  # V-9.1
            font=("Nasalization Rg", 14),
            fg=theme_color
        )

# ใน settings.py  
from version_manager import get_settings_version

class SettingsUI:
    def create_version_info(self):
        version_info = tk.Label(
            self.settings_window,
            text=get_settings_version(),  # MBB v9.1 build 19072025.04 | by iarcanar
            font=("Bai Jamjuree Light", 10)
        )
```

## 🔧 Development Workflow

### 📅 Daily Development
```python
# เมื่อเริ่มแก้ไขในวันใหม่
version_manager.update_build_today("01")

# แก้ไขครั้งที่ 2 ในวันเดียวกัน  
version_manager.BUILD_REVISION = "02"

# แก้ไขครั้งที่ 3
version_manager.BUILD_REVISION = "03"
```

### 🎯 Feature Development
```python
# เมื่อเพิ่มฟีเจอร์ใหม่
version_manager.increment_minor_version()  # 9.1 → 9.2
version_manager.update_build_today("01")   # รีเซ็ต build ใหม่

# ผลลัพธ์: v9.2 build 25072025.01
```

### 🔧 Bug Fix vs Feature
```python
# Bug Fix: เพิ่มแค่ build revision
# v9.1 build 19072025.01 → v9.1 build 19072025.02

# New Feature: เพิ่ม minor version + รีเซ็ต build  
# v9.1 build 19072025.04 → v9.2 build 20072025.01
```

---

## 🔗 Related Files
- [`MBB.py`](MBB.py) - Main application (version display)
- [`settings.py`](settings.py) - Settings UI (version info)
- [`Structure.md`](Structure.md) - Documentation (current version)
- [`FeatureManager.py`](FeatureManager.py) - Feature management

## 📚 See Also
- [Feature Manager Guide](feature_manager_guide.md)
- [Settings System Guide](settings_system_guide.md)
- [Main Application Guide](main_application_guide.md)