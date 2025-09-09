# 📦 Git Repository Management Guide - MBB v9.5

## 🎯 **Overview**
คู่มือการจัดการ Git Repository สำหรับ Magicite Babel v9.5 เพื่อความปลอดภัยและการกู้คืนระบบ

---

## 🚀 **Production Release Protocol (COMPLETED)**

### **Step 1: Repository Initialization**
```bash
# สร้าง Git repository และ initial commit
cd C:\MBB_PROJECT
git init
git add .
git commit -m "🎉 Initial release: MBB v9.5 Complete Enhanced Edition

Features:
- Real-time OCR translation system for RPG games
- Advanced choice dialog detection for FFXIV
- Enhanced CPU control (50-100%)
- Smart caching system with 75-entry capacity
- Unicode support and language validation
- Professional UI with clean design

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"

git branch -M main
```

### **Step 2: Remote Repository Setup**
```bash
# เชื่อมต่อกับ GitHub และ push
git remote add origin https://github.com/iarcanar99/Magicite-Babel.git
git push -u origin main
```

### **Step 3: Release Tag Creation**
```bash
# สร้าง release tag สำหรับ v9.5
git tag -a v9.5 -m "MBB v9.5 - Complete Enhanced Edition

Major Features:
🧠 Advanced Choice Dialog Detection
🎛️ Enhanced CPU Control (50-100%)  
✨ UI/UX Improvements
🔧 Performance Optimizations
🎮 FFXIV Specialization

Technical Enhancements:
- 15+ choice dialog pattern recognition
- Smart area processing
- OCR error tolerance
- Memory optimization
- Bug fixes and stability improvements

Production ready with expert validation."

git push origin v9.5
```

### **Step 4: Documentation Update**
```bash
# อัพเดต README.md ให้ตรงกับสไตล์เว็บไซต์
git add README.md
git commit -m "📝 Update README.md to match website tone and style

- เปลี่ยนเป็นภาษาไทยเป็นหลักตามเว็บไซต์
- เพิ่มการบรรยายเชิงลึกเกี่ยวกับฟีเจอร์ต่างๆ
- ปรับโทนให้เป็นมิตรและใกล้ชิดกับผู้ใช้
- เน้นจุดเด่นของ NPC Manager และ Choice Dialog Detection
- รวมข้อมูลการใช้งานและแก้ปัญหาแบบครบถ้วน

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"

git push origin main
```

---

## 🛡️ **Emergency Recovery Protocols**

### **🚨 Complete System Recovery**
หากระบบมีปัญหาร้ายแรง ใช้คำสั่งนี้เพื่อกลับไปยัง v9.5 ที่ทราบว่าเสถียร:

```bash
# กลับไปยัง v9.5 tag (safe state)
git reset --hard v9.5
git push --force-with-lease origin main

# หากต้องการบังคับ push (ใช้เมื่อจำเป็น)
git push --force origin main
```

### **🔍 Selective Recovery (ปลอดภัยกว่า)**
เลือกเฉพาะ commit ที่ต้องการกู้คืน:

```bash
# ดู commit history
git log --oneline --graph

# เลือก commit ที่ต้องการ
git cherry-pick [commit-hash]
git push origin main

# ตัวอย่าง: กู้คืน README update
git cherry-pick 1065a03
```

### **📋 Current Git History v9.5**
```
1065a03 - 📝 Update README.md to match website tone and style
f9df783 - 🎉 Initial release: MBB v9.5 Complete Enhanced Edition (tag: v9.5)
```

---

## 🔒 **Safe Development Protocol**

### **Before Making Any Changes**
```bash
# ตรวจสอบสถานะปัจจุบัน
git status
git log --oneline -5

# สร้าง backup commit
git add -A
git commit -m "💾 Backup before [describe your changes]"
git push origin main
```

### **During Development**
```bash
# Commit เป็นระยะ
git add [specific files]
git commit -m "🔧 [describe specific change]"

# หรือ commit ทั้งหมด
git add -A
git commit -m "✨ [feature description]"
```

### **After Testing**
```bash
# Push การเปลี่ยนแปลงที่ทดสอบแล้ว
git push origin main

# สำหรับการอัพเดตใหญ่ สร้าง tag ใหม่
git tag -a v9.6 -m "Version 9.6 - [feature summary]"
git push origin v9.6
```

---

## 🌳 **Branch Management Strategy**

### **Create Backup Branch**
ก่อนทำการเปลี่ยนแปลงใหญ่:

```bash
# สร้าง backup branch
git checkout -b backup-v9.5-$(date +%Y%m%d)
git push -u origin backup-v9.5-$(date +%Y%m%d)

# กลับไป main branch
git checkout main
```

### **Feature Development**
```bash
# สร้าง feature branch
git checkout -b feature/new-enhancement
# ... ทำการพัฒนา ...
git add -A
git commit -m "✨ Add new enhancement"

# Merge กลับเข้า main
git checkout main
git merge feature/new-enhancement
git push origin main

# ลบ feature branch
git branch -d feature/new-enhancement
```

---

## 📊 **Version Tagging Convention**

### **Semantic Versioning**
```bash
# Major release (breaking changes)
git tag -a v10.0 -m "Major release: [breaking changes]"

# Minor release (new features)
git tag -a v9.6 -m "Minor release: [new features]" 

# Patch release (bug fixes)
git tag -a v9.5.1 -m "Patch release: [bug fixes]"
```

### **Tag Management**
```bash
# ดู tags ทั้งหมด
git tag -l

# ลบ tag (local)
git tag -d v9.5.1

# ลบ tag (remote)
git push origin --delete v9.5.1

# Push tags ทั้งหมด
git push origin --tags
```

---

## ⚠️ **Critical Safety Rules**

### **❌ NEVER DO**
```bash
# อย่าใช้ --force กับ main branch เว้นแต่เป็นเหตุฉุกเฉิน
git push --force origin main  # ⚠️ อันตราย!

# อย่าลบ tags ที่เป็น release
git tag -d v9.5  # ⚠️ อย่าทำ!

# อย่า reset กับ public commits
git reset --hard HEAD~5  # ⚠️ อันตรายถ้า push แล้ว

# อย่า commit ไฟล์ส่วนตัว
git add npc*.json  # ⚠️ ข้อมูลส่วนตัว!
git add api_config.json  # ⚠️ API keys!
```

### **✅ ALWAYS DO**
```bash
# ใช้ --force-with-lease แทน --force
git push --force-with-lease origin main

# สร้าง backup ก่อนการเปลี่ยนแปลงใหญ่
git tag -a backup-$(date +%Y%m%d) -m "Backup before major changes"

# ตรวจสอบสถานะก่อน push
git status && git log --oneline -3
```

---

## 🔍 **Troubleshooting Common Issues**

### **Push Rejected**
```bash
# ดึงการเปลี่ยนแปลงล่าสุด
git fetch origin
git merge origin/main

# หรือ rebase
git rebase origin/main
```

### **Merge Conflicts**
```bash
# แก้ไข conflicts ในไฟล์
git add [resolved-files]
git commit -m "🔧 Resolve merge conflicts"
```

### **Undo Last Commit**
```bash
# ยกเลิก commit ล่าสุด (keep changes)
git reset HEAD~1

# ยกเลิก commit และ changes
git reset --hard HEAD~1  # ⚠️ ระวัง!
```

---

## 📞 **Emergency Contacts**

### **Repository Information**
- **GitHub URL**: https://github.com/iarcanar99/Magicite-Babel
- **Main Branch**: main
- **Stable Tag**: v9.5
- **Last Known Good Commit**: f9df783 (Initial release)

### **Recovery Commands Quick Reference**
```bash
# กลับไป stable version
git reset --hard v9.5

# ดู commit history
git log --oneline --graph

# สร้าง emergency backup
git tag -a emergency-$(date +%Y%m%d-%H%M) -m "Emergency backup"
git push origin emergency-$(date +%Y%m%d-%H%M)
```

---

**📝 Last Updated**: January 9, 2025  
**Version**: 9.5  
**Status**: Production Ready  
**Repository**: https://github.com/iarcanar99/Magicite-Babel.git