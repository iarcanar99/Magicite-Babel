# 📚 MBB Project Documentation Structure

**Magicite Babel v9.1** - โปรแกรมแปลเกมแบบ Real-time ด้วยพลัง AI

## 🎯 Project Overview
- **Real-time Translation:** ENG→TH, JP→TH ด้วย AI (Gemini, Claude, GPT)
- **Area-Preset System:** 6 Presets, 3 Areas สำหรับจัดการพื้นที่แปล
- **Modern UI:** TUI, Control UI, Settings UI ด้วย dark theme
- **Advanced Features:** Hover Translation v1.1, NPC Manager, CPU Management, **Splash Screen System**

## 📁 Documentation Location
**คู่มือ Structure.md เป็นเหมือนสารบัญอยู่ในโฟลเดอร์หลัก**

## 📋 Complete Documentation Index

### 🚀 **Core Module Guides** (ใหม่!) 
**📁 ตำแหน่ง: `C:\MBB_PROJECT\Structure_Manuals\`**

- [`mbb_v9_guide.md`](Structure_Manuals/mbb_v9_guide.md) - 🎯 **MBB Core Module** - ไฟล์หลักและ Central Coordinator (ใหม่!)
- [`translated_ui_guide.md`](Structure_Manuals/translated_ui_guide.md) - 📱 **Translated UI Module** - หน้าต่างแสดงผลการแปล
- [`settings_system_guide.md`](Structure_Manuals/settings_system_guide.md) - ⚙️ **Settings System** - ระบบจัดการการตั้งค่า
- [`control_ui_guide.md`](Structure_Manuals/control_ui_guide.md) - 🎛️ **Control UI Module** - หน้าต่างควบคุมหลัก (อัพเดต!)
- [`npc_manager_guide.md`](Structure_Manuals/npc_manager_guide.md) - 👥 **NPC Manager** - ระบบจัดการ NPC
- [`translation_system_guide.md`](Structure_Manuals/translation_system_guide.md) - 🔄 **Translation System** - ระบบแปลภาษา AI
- [`feature_manager_guide.md`](Structure_Manuals/feature_manager_guide.md) - 🎛️ **Feature Manager** - ระบบจัดการฟีเจอร์
- [`version_manager_module_guide.md`](Structure_Manuals/version_manager_module_guide.md) - 🔄 **Version Manager** - ระบบควบคุมเวอร์ชั่น
- [`font_manager_guide.md`](Structure_Manuals/font_manager_guide.md) - 🔤 **Font Manager v2.0** - ระบบจัดการฟอนต์บน TUI และ LOG (Complete Overhaul 26/07/2025)
- [`advance_ui_guide.md`](Structure_Manuals/advance_ui_guide.md) - ⚙️ **Advance UI** - Screen & Performance Settings Management (CPU Migration 26/07/2025)

### 🎨 **System Guides**
**📁 ตำแหน่ง: `C:\MBB_PROJECT\Structure_Manuals\`**

- [`theme_system_guide.md`](Structure_Manuals/theme_system_guide.md) - 🎨 **Theme System ครบครัน**
- [`version_manager_guide.md`](Structure_Manuals/version_manager_guide.md) - 🔄 **Version Manager แบบรวมศูนย์** (เดิม)
- [`translated_logs.md`](Structure_Manuals/translated_logs.md) - 📊 **Translated Logs Module**

### 🚀 **Getting Started** (Future)
- **README.md** - คู่มือเริ่มต้นใช้งาน
- **quick_start.md** - 3 ขั้นตอนเริ่มใช้งาน 
- **api_setup.md** - วิธีตั้งค่า API Keys

### 🎮 **User Guides** (Future)
- **features_guide.md** - คู่มือฟีเจอร์ทั้งหมด
- **User_Guide_Advanced_Techniques.md** - เทคนิค 2 แบบ
- **troubleshooting.md** - แก้ปัญหาที่พบบ่อย

### 🔧 **Technical Guides** (Future)
- **hover_translation_guide.md** - Hover Translation v1.1
- **TUI_Complete_Guide.md** - การพัฒนา TUI ครบครัน
- **PRE_START_SYSTEM_SUMMARY.md** - ระบบตรวจสอบก่อนเริ่ม

### 📦 **Build & Distribution** (26/07/2025)
- **BUILD_PLAN_V91_COMPLETE.md** - แผนการ build v9.1 streamlined
- **build_mbb_v91_production.bat** - Script สำหรับ build production
- **MBB_v91_production.spec** - PyInstaller spec ที่ optimize แล้ว
- **pin_border_guide.md** - ฟีเจอร์ขอบ PIN

### 📦 **Project Management** (Future)
- **MBB_v9_package_plan.md** - แผนการแพ็คเกจ v9.0

## 🏗️ Core Architecture Summary

**Main:** `MBB.py`, `FeatureManager.py`, `settings.py/.json`
**Translation:** `translator_gemini.py` (ENG), `translator_gemini_JP.py` (JP), `translator_claude.py`
**UI:** `control_ui.py`, `translated_ui.py`, `mini_ui.py`, `advance_ui.py`
**Systems:** `before_start/`, `hover_translation.py`, `npc_manager_card.py`, `appearance.py`
**Splash Screen:** `MBB_splash_vid.mp4` (video), `MBB_splash.png` (image)

**Language Switching:** เปลี่ยนชื่อไฟล์ manual (translator_gemini.py ↔ translator_gemini_JP.py)

## 🎬 Splash Screen System
- **Files:** `MBB_splash_vid.mp4` (60% screen width, 5s duration), `MBB_splash.png` (transparent PNG)
- **Settings:** `splash_screen_type` in settings.json → "video" | "image" | "off"
- **Features:** Queue-based video playback, quadratic fade-in (2s for video), auto-fallback to image
- **Architecture:** Thread-safe video capture → Queue → Main thread UI update

## 🔄 Key Workflows
- **Translation Flow:** OCR → Priority Check → Quality Gate → AI Translation → Display
- **Preset Management:** เลือก Preset → ตรวจสอบ Unsaved Changes → Area Restrictions → Save
- **Language Switching:** Manual file rename (ENG ↔ JP)
- **MBB-Control UI Coordination:** Settings Change → Control UI → MBB.py → System Apply → UI Sync
- **Settings Propagation:** Control UI → Settings → MBB.py → Feature Modules → UI Updates

## 📈 Development Status (กรกฎาคม 2025)
- ✅ **เสร็จสมบูรณ์:** Hover Translation v1.3.4, Modern UI Redesign, CPU Management, **Splash Screen System**
- 🔧 **ปรับปรุงล่าสุด:** Hover Translation Stability, **Font Manager v2.0 Complete Overhaul (26/07/2025)**, Theme UI Stability, Code Cleanup, Force Translate Hotkey System, **Translated Logs v2.1.0**, **Splash Screen (19/07/2025)**
- 🎯 **พัฒนาต่อ:** TUI Professional Development, Optional Module Enhancement

## 🔄 Version Management Protocol
**Current Version:** v9.1 build 19072025.04
**Centralized Version Control:** `version_manager.py`

### 📋 Version Update Guidelines

#### 🔢 Version Number Rules
- **Major Version (9.x):** เปลี่ยนเมื่อมีการปรับปรุงใหญ่
- **Minor Version (x.1-x.9):** เพิ่มเมื่อมีโมดูลใหม่หรือฟีเจอร์ใหม่
- **Build Number (DDMMYYYY.XX):** อัพเดตทุกครั้งที่แก้ไข
  - Format: วันที่.ลำดับการแก้ไข เช่น `19072025.01`
  - ตัวอย่าง: วันนี้แก้ไขครั้งที่ 2 = `19072025.02`

#### 🎯 การแสดงผลเวอร์ชั่น
- **หน้าหลัก MBB:** `V-9.1` (สีตาม theme)
- **หน้า Settings:** `MBB v9.1 build 19072025 | by iarcanar` (แบบเต็ม)

#### ⚙️ การอัพเดตเวอร์ชั่น
**ไฟล์หลัก:** `version_manager.py` (ควบคุมทุกอย่างจากจุดเดียว)

**เมื่อแก้ไขโค้ด - ขั้นตอนบังคับ:**
1. **อัพเดต** `version_manager.py` → `BUILD_DATE` และ `BUILD_REVISION`
2. **ตรวจสอบ** การแสดงผลใน MBB.py และ settings.py
3. **อัพเดต** `Structure.md` → Current Version ในส่วนนี้
4. **ลบ** คู่มือเก่าที่ไม่ใช้ (ถ้ามี)

**ตัวอย่างการแก้ไข:**
- แก้บัค = เพิ่ม build revision: `19072025.01` → `19072025.02`
- เพิ่มฟีเจอร์ = เพิ่ม minor: `v9.1` → `v9.2` + reset build: `20072025.01`

---
**💡 หมายเหตุ:** เอกสารทั้งหมดอยู่ในโฟลเดอร์ `structure_guides/` เพื่อความเป็นระเบียบ