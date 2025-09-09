# 🌐 MBB Website Development Guide

**ไฟล์:** `index.html` (Main Website)  
**เวอร์ชั่นปัจจุบัน:** v9.1 (สิงหาคม 2025)  
**อัพเดตล่าสุด:** 2025-08-01  

## 📋 Overview

เว็บไซต์ MBB (Magicite Babel) เป็น Landing Page สำหรับโปรแกรมแปลภาษาเกมแบบเรียลไทม์ ออกแบบมาให้นำเสนอฟีเจอร์และดึงดูดผู้ใช้งานใหม่ พร้อมระบบดาวน์โหลดและข้อมูลการติดต่อ

## 🏗 Architecture & Structure

### 📁 ไฟล์หลัก
```
C:\MBB_PROJECT\
├── index.html           # เว็บไซต์หลัก v9.1
├── index_v8.html        # Backup เว็บไซต์ v8.0 (อ้างอิง)
└── Structure_Manuals/
    └── website_development_guide.md  # คู่มือนี้
```

### 🎨 Tech Stack
- **Framework:** Pure HTML5 + Tailwind CSS (CDN)
- **Icons:** Font Awesome 6.0
- **Fonts:** Google Fonts (Kanit)
- **Images:** Cloudinary CDN hosting
- **Responsive:** Mobile-first approach

## 📖 Content Strategy & Sections

### 🎯 Target Audience
- **หลัก:** ผู้เล่น FFXIV ชาวไทย
- **รอง:** ผู้เล่นเกมอื่นๆ ที่ต้องการแปลภาษา
- **คุณลักษณะ:** First-time visitors, มีความรู้ภาษาอังกฤษพื้นฐาน

### 📑 Structure Layout (v8 Style)

#### 1. **Hero Section** 
```html
<header class="hero-gradient">
    <!-- บทนำหลัก: ใช้เนื้อหาจาก v8 แต่ตัด API เจ้าอื่นออก -->
    <!-- เน้น Gemini AI เท่านั้น -->
</header>
```

#### 2. **Screenshot Gallery**
```html
<section class="slideshow">
    <!-- แสดงตัวอย่างการใช้งานจริง 16:9 ratio -->
    <!-- Slide captions พร้อม gradient background -->
</section>
```

#### 3. **Program UI Section**
```html
<section id="program-ui">
    <!-- แสดงโมดูลตามลำดับความสำคัญ -->
    <!-- MBB > Control_UI > Translated_UI > Translation_Logs > Manual Click+Hover > NPC Manager > Font Manager > Settings -->
</section>
```

#### 4. **Download Section**
```html
<section id="download">
    <!-- ข้อมูลเกมที่รองรับ + ปุ่มดาวน์โหลด -->
    <!-- API Key instructions (ย้ายมาจาก Settings) -->
</section>
```

#### 5. **Contact Section**
```html
<section class="contact">
    <!-- ข้อมูลติดต่อผู้พัฒนา -->
</section>
```

## 🎨 Design System

### 🎨 Colors
```css
/* Primary Colors */
--indigo-primary: #4f46e5
--purple-accent: #8b5cf6
--background-dark: #060d1a

/* UI States */
--success: #10b981
--warning: #f59e0b
--error: #ef4444
--info: #3b82f6
```

### 🖼 Image System
- **CDN:** Cloudinary (res.cloudinary.com/docoo51xb/)
- **Format:** PNG สำหรับ UI screenshots, JPG สำหรับ banners
- **Naming:** `MBB_site_[module]_[id].png`
- **Borders:** Purple light border สำหรับรูป Program UI

### 📱 Responsive Breakpoints
```css
/* Mobile First */
sm: 640px   /* Mobile landscape */
md: 768px   /* Tablet */
lg: 1024px  /* Desktop */
xl: 1280px  /* Large desktop */
```

## 🔧 Key Components & Features

### 1. **Program UI Images**
```css
.program-ui-image {
    border: 2px solid rgba(139, 92, 246, 0.6);
    border-radius: 12px;
}

.program-ui-image:hover {
    filter: drop-shadow(0 0 25px rgba(99, 102, 241, 0.7));
    border: 2px solid rgba(139, 92, 246, 0.9);
}
```

### 2. **Slideshow with Enhanced Captions**
```css
.slide-caption {
    position: absolute;
    bottom: 0;
    background: linear-gradient(transparent, rgba(0, 0, 0, 0.95));
    padding: 4rem 2rem 1.5rem;
}
```

### 3. **Gradient Buttons**
```css
.btn-primary {
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    transition: all 0.3s ease;
}
```

## 📝 Content Guidelines

### ✅ Writing Style (v8 Proven Formula)
- **Tone:** เป็นกันเอง, ใช้อีโมจิพอดี
- **Language:** ไทย (หลัก) + English terms with Thai explanations
- **Structure:** แนะนำ → อธิบาย → ประโยชน์ → Call-to-action

### 🎯 Module Descriptions (ลำดับความสำคัญ)

#### 1. **MBB - หน้าต่างหลัก**
- ศูนย์กลางควบคุม, ปุ่มหลัก (START, TUI, LOG, CON, MINI)
- **ใหม่ v9.1:** ระบบธีม, ปรับปรุงเสถียรภาพ

#### 2. **Control UI - ศูนย์ควบคุมทุกฟีเจอร์**
- Preset 1-6, พื้นที่แปล A/B/C, แปลซ้ำ, บันทึก/โหลด
- **ใหม่ v9.1:** Tooltips, จัดเรียงปุ่มใหม่

#### 3. **Translated UI (TUI) - หน้าต่างแสดงผลการแปล**
- ระบบล็อก 3 แบบ:
  - **ปกติ:** ปรับตำแหน่งได้เต็มที่
  - **ล็อก+ซ่อนพื้นหลัง:** เสพกราฟิกเกมเต็มตา
  - **ล็อก+มีพื้นหลัง:** ล็อกไม่ให้มือโดน + พื้นหลังอ่านง่าย

#### 4. **Translation Logs - ประวัติการแปล**
- Chat bubble style, Position lock, Smart cache
- **ใหม่ v9.1:** Font Manager access, สลับการเรียงข้อความได้

#### 5. **Manual Click & Hover - การแปลแบบควบคุม**
- คลิก/ชี้เพื่อแปล, สลับพื้นที่อัตโนมัติ

#### 6. **NPC Manager (ระบบข้อมูลตัวละคร)**
- การ์ดแสดงข้อมูล, รองรับหลายเกม
- **v9.1:** Complete Overhaul

#### 7. **Font Manager**
- v2.0 Target selection, TUI/LOG font management

#### 8. **Settings - การตั้งค่าและปรับแต่ง**
- ปุ่มลัด, CPU/GPU management, ความละเอียดหน้าจอ
- **หมายเหตุ:** ระบบธีมย้ายไป MBB แล้ว

### 🔑 API Key Section (ใหม่ - ย้ายจาก Settings)
```html
<!-- ใน Download Section -->
<div class="api-key-instructions">
    <h4>🔑 การรับ Gemini API Key:</h4>
    <ol>
        <li>กดปุ่ม "รับ API Key" → Google AI Studio</li>
        <li>คัดลอก API Key ที่ได้รับ</li>
        <li>นำไปใส่ในไฟล์ .env ในโฟลเดอร์โปรแกรม</li>
    </ol>
    <code>GEMINI_API_KEY=วาง_API_Key_ที่คัดลอกมา_ตรงนี้</code>
</div>
```

## 🚀 Version Updates (v8.0 → v9.1)

### ✅ เสร็จสิ้นแล้ว (100% Complete)
- [x] เปลี่ยน version references: 8.0 → 9.1, มิถุนายน → สิงหาคม
- [x] ใช้บทนำ v8 แต่ตัด AI อื่นออก (เหลือ Gemini เท่านั้น)
- [x] เปลี่ยนหัวข้อ: "หน้าตาโปรแกรม" → "UI และระบบหลัก"
- [x] ปรับ TUI: ระบบล็อก 3 แบบ
- [x] เพิ่ม Translation Logs: Font Manager access + สลับข้อความ
- [x] ย้ายระบบธีม: Settings → MBB
- [x] ย้าย API Key instructions: Settings → Download
- [x] เพิ่มปุ่ม "รับ API Key" ใน Hero section (jump to guide)
- [x] อัพเดต splash media: video + image transitions
- [x] เพิ่ม purple borders รอบ program UI images
- [x] ปรับปรุง slideshow captions พร้อม gradient
- [x] สร้าง fixed navigation buttons (jump to top/bottom)
- [x] แก้ไข video fade transition (2s fade out → 1s fade in)

### 🎯 **New Features Added (Aug 2025)**
- [x] **Video Splash System:** Auto-play video → smooth transition to image
- [x] **Navigation Buttons:** Fixed right-side buttons (50×120px vertical pill)
- [x] **API Key Shortcuts:** Hero button → Download instructions → Google AI Studio
- [x] **Enhanced Visuals:** Purple borders, gradient captions, hover effects
- [x] **Mobile Optimized:** Responsive navigation and media handling

### 🔮 สำหรับอนาคต
- [ ] รอรูปภาพ v9.1 ใหม่จากผู้ใช้
- [ ] อัพเดต Patch Notes เมื่อมีการปล่อยจริง
- [ ] เพิ่ม testimonials จากผู้ใช้งาน

## 🛠 Development Workflow

### 📋 Pre-Development Checklist
1. **อ่านคู่มือนี้ก่อนเริ่มงาน**
2. ตรวจสอบ `structure.md` สำหรับข้อมูล v9.1 features
3. ดู `index_v8.html` เป็น reference สำหรับเนื้อหาที่ดี
4. ตรวจสอบ technical guides ใน `Structure_Manuals/`

### 🔄 Making Changes
1. **อ่านไฟล์ก่อน:** ใช้ Read tool ดู section ที่จะแก้
2. **ทำความเข้าใจบริบท:** เช็คว่าส่วนนั้นเชื่อมโยงกับอะไรบ้าง
3. **แก้ไขตาม pattern:** ใช้ MultiEdit สำหรับการแก้หลายจุด
4. **เทสต์ responsive:** ตรวจสอบ mobile/tablet/desktop

### 📝 Content Updates
```markdown
หลักการสำคัญ:
- รักษา "น้ำเสียง" v8 ที่ได้รับการยอมรับ
- เน้น Gemini AI เป็นหลัก (ไม่พูดถึง AI อื่น)
- ใช้คำศัพท์ภาษาอังกฤษ + อธิบายไทย
- เรียงลำดับโมดูลตามความสำคัญ
- รักษาความสมดุลระหว่างเทคนิคและเข้าใจง่าย
```

## 🎯 SEO & Performance

### 🏷 Meta Tags
```html
<title>Magicite Babel v9.1 - แปลภาษาเกมแบบเรียลไทม์</title>
<meta name="description" content="แปลเกม FFXIV และเกมอื่นๆ ด้วย Gemini AI พร้อม NPC Manager และ Font Manager v2.0">
```

### ⚡ Performance
- **Images:** Cloudinary CDN + WebP support
- **CSS:** Tailwind CDN (ลด bundle size)
- **JS:** Minimal vanilla JS
- **Lazy Loading:** รูปภาพใหญ่

## 🐛 Common Issues & Solutions

### 1. **รูปภาพไม่โหลด**
```markdown
สาเหตุ: Cloudinary URL เปลี่ยน
แก้ไข: ตรวจสอบ URL ใน Cloudinary console
```

### 2. **Mobile Layout เพี้ยน**
```markdown
สาเหตุ: Tailwind responsive classes
แก้ไข: ใช้ mobile-first approach (sm:, md:, lg:)
```

### 3. **Content ยาวเกินไป**
```markdown
สาเหตุ: อธิบายเทคนิคมากเกินไป
แก้ไข: ใช้หลัก v8 - เน้นประโยชน์มากกว่าเทคนิค
```

## 📞 Development Support

### 🔗 Related Files
- `structure.md` - ข้อมูล v9.1 features
- `translated_logs.md` - Technical specs
- `translated_ui_guide.md` - UI technical details
- `index_v8.html` - Reference content

### 📋 Development Commands
```bash
# Preview (if using live server)
npx live-server --port=8080

# Validate HTML
npx html-validate index.html

# Check responsive
# Use browser dev tools
```

## ✅ Quality Checklist

### 🎯 Content Quality
- [ ] บทนำใช้สไตล์ v8 (ไม่มี AI อื่นนอกจาก Gemini)
- [ ] ลำดับโมดูลถูกต้อง (MBB → Control → TUI → Logs → Manual → NPC → Font → Settings)
- [ ] API Key instructions อยู่ใน Download section
- [ ] ระบบธีมอยู่ใน MBB section
- [ ] ระบบล็อก TUI อธิบาย 3 แบบ
- [ ] Translation Logs มี Font Manager + สลับข้อความ

### 🎨 Visual Quality  
- [ ] Purple borders รอบรูป Program UI
- [ ] Gradient captions ใน slideshow
- [ ] Responsive ทุก breakpoint
- [ ] Hover effects ทำงานได้
- [ ] Loading performance ดี

### 📱 Technical Quality
- [ ] HTML5 validation pass
- [ ] Accessibility (alt tags, semantic HTML)
- [ ] Cross-browser compatibility
- [ ] Mobile-first responsive
- [ ] SEO meta tags ครบ

---

**📝 หมายเหตุ:** คู่มือนี้จัดทำขึ้นจากประสบการณ์การพัฒนาเว็บไซต์ MBB v8.0 → v9.1 เพื่อให้นักพัฒนาเข้าใจบริบทและแนวทางการทำงานที่ถูกต้อง

**🔄 อัพเดต:** 01/08/2025 - Complete website overhaul with v8 content strategy + v9.1 features