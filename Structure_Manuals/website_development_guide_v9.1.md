# คู่มือการพัฒนาหน้าเว็บ Magicite Babel v9.1

**เวอร์ชั่น:** v9.1.2  
**วันที่อัปเดต:** 10 สิงหาคม 2025  
**ไฟล์หลัก:** `C:\MBB_PROJECT\index_v9_glass.html`  
**ผู้พัฒนา:** iarcanar

## ภาพรวมของเว็บไซต์

เว็บไซต์ Magicite Babel เป็น **Single Page Application (SPA)** ที่ใช้เทคโนโลยี **Glass Morphism Design** เป็นหลัก ออกแบบให้เป็น Landing Page สำหรับโปรแกรมแปลภาษาเกม พร้อมข้อมูลที่ครบถ้วนสำหรับผู้ใช้งาน รวมถึงระบบ Interactive Elements ที่ทันสมัย

---

## เทคโนโลยีและเครื่องมือที่ใช้

### 🎨 Frontend Framework & Libraries
| เทคโนโลยี | เวอร์ชั่น | CDN/Source |
|-----------|---------|------------|
| **HTML5** | Standard | โครงสร้างหลัก |
| **Tailwind CSS** | Latest | `https://cdn.tailwindcss.com` |
| **Font Awesome** | 6.0.0-beta3 | `https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css` |
| **Google Fonts** | Kanit | `https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500;700&display=swap` |
| **Vanilla JavaScript** | ES6+ | Embedded ในไฟล์ HTML |

### 🎯 Design System
- **Glass Morphism** - ดีไซน์หลักที่ใช้ backdrop-filter และ transparency
- **Animated Background** - Liquid blob animations (3 blobs)
- **Particle System** - 50 animated particles floating upward
- **Responsive Design** - Mobile-first approach รองรับทุกขนาดหน้าจอ

### 🖼️ Media & Resources
- **Cloudinary CDN** - สำหรับเก็บรูปภาพและวิดีโอ
- **Video Background** - Splash screen แบบ autoplay พร้อม fallback เป็นรูปภาพ
- **Image Lightbox** - ระบบขยายรูปภาพแบบ modal
- **Slideshow System** - Auto-advance ทุก 8 วินาที

---

## โครงสร้างของเว็บไซต์

### 📁 Section Layout
1. **Animated Background & Particles** - พื้นหลัง animated
2. **Splash Screen** - วิดีโอ/รูปภาพเริ่มต้น
3. **Hero Section** - แนะนำโปรแกรมและฟีเจอร์ใหม่
4. **Performance Highlights** - ความสามารถของ v9.1 (NEW)
5. **Screenshot Gallery** - ตัวอย่างการใช้งาน (Slideshow)
6. **Program UI** - คู่มือส่วนต่างๆ ของโปรแกรม
7. **Latest Updates** - อัปเดตล่าสุด (พร้อม Patch Notes Modal)
8. **Download & API** - ดาวน์โหลดและคู่มือติดตั้ง
9. **Footer** - ข้อมูลติดต่อและลิงก์
10. **Modals & Interactive Elements** - Patch Notes, Image Lightbox

### 🔗 Navigation System
- **Smooth Scrolling** - การเลื่อนหน้าจออย่างนุ่มนวลสำหรับ anchor links
- **Navigation Orb** - ปุ่มลัดข้าง Fixed position (กลับด้านบน/ลงด้านล่าง)
- **Anchor Links** - ลิงก์ภายในหน้าเว็บ
- **Shortcut Buttons** - ปุ่มลัดไปยังส่วนสำคัญ

---

## ลิงก์และทรัพยากรสำคัญ

### 🌐 External Links
| ประเภท | URL | จุดประสงค์ | ตำแหน่งในเว็บ |
|--------|-----|-----------|-------------|
| **Gemini API** | `https://aistudio.google.com/app/apikey` | รับ API Key สำหรับใช้งาน | Hero Section, Installation Guide |
| **Beta Access** | `https://docs.google.com/forms/d/e/1FAIpQLScUaGT4VTcAb__oupReSR6yjhgnuDjsngOoBj3pOe2lFWbqCQ/viewform` | ขอเข้าร่วมทดสอบ Beta | Download Section |

### 🖼️ Cloudinary Media Resources
| ประเภทไฟล์ | Resource ID | คำอธิบาย | ใช้ในส่วน |
|-----------|-------------|----------|----------|
| **Video** | `MBB_splash_vid_spdga7.mp4` | วิดีโอ Splash Screen | Main Splash |
| **Images** | `MBB_splash_uwntfk.png` | รูป Splash Screen (fallback) | Main Splash |
| **UI Screenshots** | `MBB_site_main_ui_oshz4v.png` | UI หลักของโปรแกรม | Hero Section |
| **Gallery** | `banner-01_gfmys5.png` ถึง `banner-06_sa5rot.jpg` | รูปภาพในแกลเลอรี่ | Screenshot Gallery |
| **Program UI** | `MBBv9_mini_zjm2ty.png`, `MBBv9_mbb_znmona.png` | UI ของโปรแกรมต่างๆ | Program UI Section |
| **TUI** | `MBBv9_TUI_pwryhd.png` | Translation UI | Program UI Section |
| **Control** | `MBBv9_control_ui_taju6v.png` | Control UI | Program UI Section |
| **LOG** | `MBBv9_LOG_el8p9s.png` | Translation Logs | Program UI Section |
| **NPC Manager** | `MBBv9_NPC_manager_z34fd7.png` | NPC Manager | Program UI Section |
| **Installation** | `MBBv9_first_start_wfkgup.png` | คู่มือติดตั้งครั้งแรก | Download Section |
| **Icons** | `MBB_icon_oua6nq.png` | ไอคอนโปรแกรม | Latest Updates |

### 📱 Internal Navigation Links
| ID | Section | คำอธิบาย | Target Element |
|----|---------|----------|---------------|
| `#program-ui` | Program UI | ส่วนแสดง UI ของโปรแกรม | Program UI Section |
| `#download` | Download | ส่วนดาวน์โหลด | Download & API Section |
| `#installation-guide` | Installation | คู่มือติดตั้งครั้งแรก | ภายใน Download Section |
| `#npc-manager` | NPC Manager | ส่วนอธิบาย NPC Manager | Program UI Section |
| `#latest-updates` | Updates | อัปเดตล่าสุด | Latest Updates Section |

---

## ฟีเจอร์พิเศษและระบบ Interactive

### ✨ Interactive Elements
| ฟีเจอร์ | คำอธิบาย | การทำงาน |
|--------|----------|---------|
| **Slideshow Gallery** | เปลี่ยนรูปอัตโนมัติทุก 8 วินาที | JavaScript `setInterval` + Manual controls |
| **Image Lightbox** | คลิกรูปเพื่อขยาย | Click `.image-container-lightbox` → Modal |
| **Patch Notes Modal** | Modal แสดงรายละเอียดการอัปเดต | Button trigger + ESC key support |
| **Discord ID Copy** | คลิกคัดลอก Discord ID | Clipboard API + fallback |
| **Miqo'te Wiggle Animation** | ไอคอนส่ายทุก 3 วินาที | CSS animation + JavaScript trigger |
| **Video to Image Transition** | Splash video → image fallback | Auto-detect video end/error |

### 🎨 Visual Effects
| เอฟเฟกต์ | คำอธิบาย | Implementation |
|---------|----------|----------------|
| **Glass Morphism Cards** | การ์ดแบบแก้วด้วย backdrop-filter | `.glass-card` class |
| **Liquid Blob Animation** | พื้นหลัง animated blobs (3 blobs) | CSS `@keyframes float-blob` |
| **Particle System** | อนุภาคลอยขึ้น-ลง (50 particles) | JavaScript generated particles |
| **Hover Effects** | เอฟเฟกต์เมื่อ hover ปุ่มและรูปภาพ | CSS transitions + transforms |
| **Shimmer Effects** | แสงระยิบระยับ | CSS `@keyframes shimmer` |

---

## การกำหนดค่าสำคัญ

### 🎨 CSS Custom Properties
```css
:root {
    --primary-color-1: #6366f1;    /* สีหลัก Indigo */
    --primary-color-2: #8b5cf6;    /* สีหลัก Purple */
    --accent-color: #06b6d4;       /* สีเสริม Cyan */
}
```

### 🖼️ Animation Settings
| Animation | Duration | Delay | Loop |
|-----------|----------|-------|------|
| **Slideshow** | 8s | - | Infinite |
| **Particle Float** | 10-20s | 0-15s random | Infinite |
| **Blob Float** | 20s | 0s, 5s, 10s | Infinite |
| **Miqo'te Wiggle** | 0.4s | Every 3s | On trigger |
| **Shimmer** | 3s | - | Infinite |

### 🎬 Video Settings
- **Format:** MP4
- **Autoplay:** เปิด (muted, playsinline)
- **Fallback:** รูปภาพสำหรับอุปกรณ์ที่ไม่รองรับ
- **Timeout:** 5 วินาที (หากโหลดไม่ได้)
- **Transition:** 1s fade out/in

---

## JavaScript Functions และ Events

### 🔧 Core Functions
```javascript
// 1. Particle System Generation - สร้าง particles 50 ตัว
// 2. Slideshow functionality - ควบคุม slideshow
// 3. Video Splash Screen to Image Fallback - จัดการ video transition
// 4. Navigation Orb Functions - scroll to top/bottom
// 5. Patch Notes Modal - เปิด/ปิด modal
// 6. Miqo'te Wiggle Animation - animation trigger
// 7. Smooth Scrolling for Anchor Links - smooth scroll
// 8. Image Lightbox - ขยายรูปภาพ
// 9. Copy Discord ID Function - คัดลอก Discord ID
```

### 📱 Event Listeners
| Event Type | Target | Function |
|------------|--------|----------|
| `DOMContentLoaded` | document | Initialize particles, video handling |
| `click` | `.thumbnail`, navigation buttons | Slideshow control |
| `click` | `#viewAllUpdates` | Open patch notes modal |
| `click` | `.image-container-lightbox` | Open image lightbox |
| `click` | anchor links | Smooth scroll |
| `keydown` | document | ESC key handling |

---

## คำแนะนำสำหรับการพัฒนาต่อ

### 🔧 การเพิ่มเนื้อหาใหม่
1. **เพิ่มรูปภาพใหม่:**
   - อัปโหลดไปที่ Cloudinary
   - เปลี่ยน URL ในไฟล์ HTML
   - เพิ่ม `alt` attribute สำหรับ accessibility

2. **เพิ่ม Section ใหม่:**
   - เพิ่มใน HTML structure
   - เพิ่ม anchor link ใน navigation
   - เพิ่ม CSS class ตามต้องการ

3. **แก้ไขสี:**
   - ปรับใน CSS custom properties ส่วนบน
   - หรือใช้ Tailwind utilities

### 📱 การปรับปรุง Responsive
```css
/* Tailwind Breakpoints */
sm: 640px   /* Mobile landscape */
md: 768px   /* Tablet */
lg: 1024px  /* Desktop */
xl: 1280px  /* Large desktop */
```

**Best Practices:**
- ใช้ mobile-first approach
- ทดสอบในหน้าจอขนาดต่างๆ
- ปรับ Navigation Orb สำหรับ mobile (ขนาดเล็กลง)

### 🎯 การเพิ่มฟีเจอร์ Interactive
1. **JavaScript Functions:**
   - เพิ่มฟังก์ชันใหม่ในส่วน `<script>` ด้านล่าง
   - ใช้ `DOMContentLoaded` สำหรับ initialization

2. **Modal ใหม่:**
   - ทำตาม pattern ของ Patch Notes Modal
   - เพิ่ม backdrop click และ ESC key handling

3. **Animations:**
   - เพิ่ม `@keyframes` ใหม่ในส่วน CSS
   - ใช้ CSS `animation` หรือ `transition`

### 🔄 การอัปเดตข้อมูล
1. **เวอร์ชั่นใหม่:**
   - แก้ไขเลขเวอร์ชั่นและวันที่ทุกที่ที่ปรากฏ
   - อัปเดต title และ meta description

2. **ฟีเจอร์ใหม่:**
   - เพิ่มใน Performance Highlights section
   - เพิ่มใน Latest Updates section
   - อัปเดต Patch Notes Modal

3. **ลิงก์ดาวน์โหลด:**
   - อัปเดต URL ในส่วน Download
   - ตรวจสอบ external links ให้ใช้งานได้

---

## การทดสอบและ Quality Assurance

### ✅ Testing Checklist
**Functionality Testing:**
- [ ] ทดสอบทุก anchor link
- [ ] ตรวจสอบการโหลดรูปภาพและวิดีโอ
- [ ] ทดสอบ slideshow (auto + manual)
- [ ] ทดสอบ modals (open/close/ESC key)
- [ ] ทดสอบ image lightbox
- [ ] ทดสอบ Discord ID copy function

**Responsive Testing:**
- [ ] Mobile (320px - 640px)
- [ ] Tablet (640px - 1024px) 
- [ ] Desktop (1024px+)
- [ ] Navigation Orb behavior
- [ ] Text readability

**Performance Testing:**
- [ ] ตรวจสอบ JavaScript console สำหรับ errors
- [ ] Loading time ของรูปภาพ
- [ ] Video autoplay และ fallback
- [ ] Animation performance

### 🐛 การแก้ไขปัญหาที่พบบ่อย
| ปัญหา | สาเหตุที่เป็นไปได้ | วิธีแก้ไข |
|-------|-----------------|-----------|
| **รูปไม่โหลด** | Cloudinary URL เปลี่ยน | ตรวจสอบ URL ใน Cloudinary console |
| **แอนิเมชันกระตุก** | CSS transitions ไม่เหมาะสม | ปรับ duration และ easing function |
| **Modal ไม่ปิด** | Event listeners ไม่ทำงาน | ตรวจสอบ JavaScript console |
| **Responsive ผิดรูป** | Tailwind classes ผิด | ใช้ mobile-first approach |
| **Video ไม่เล่น** | Browser policy | ตรวจสอบ muted + autoplay attributes |

---

## File Structure และ Dependencies

### 📁 Related Files
```
C:\MBB_PROJECT\
├── index_v9_glass.html          # ไฟล์หลัก (เวอร์ชั่นปัจจุบัน)
├── Structure_Manuals\
│   ├── website_development_guide_v9.1.md  # คู่มือนี้
│   ├── website_development_guide.md       # คู่มือเก่า (v8 reference)
│   └── mbb_v9_guide.md                   # Technical specs
└── Release note\
    └── MBB_release_note_v9.1.md         # Release notes
```

### 🔗 Dependencies
**External Dependencies:**
- Tailwind CSS (CDN)
- Font Awesome 6 (CDN)  
- Google Fonts Kanit (CDN)
- Cloudinary Media Files

**Internal Dependencies:**
- ไม่มี - ทุกอย่าง embedded ในไฟล์เดียว

---

## Version History และ Changelog

### 📋 v9.1.2 (10 สิงหาคม 2025)
**เพิ่มใหม่:**
- Navigation shortcuts ปรับปรุง
- "การแปลอัจฉริยะ" → "การแปลอัจฉริยะ (NPC Manager)" with shortcut
- API Key button ใน Hero section → Installation guide
- Footer menu → Program UI section
- TUI heading prefix เพิ่ม

**แก้ไข:**
- Anchor links navigation
- User experience improvements

### 📋 v9.1.1 (ก่อนหน้า)
- Performance Highlights section
- Glass morphism design overhaul
- Video splash screen system
- Interactive elements enhancement
- Patch notes modal system

---

## Support และ Documentation

### 📞 Contact Information
- **ผู้พัฒนา:** iarcanar
- **Discord:** iarcanar#0
- **เวอร์ชั่นปัจจุบัน:** 9.1

### 📚 Additional Resources
- **Project Overview:** `C:\MBB_PROJECT\structure.md`
- **Technical Guides:** `C:\MBB_PROJECT\Structure_Manuals\*.md`
- **Release Notes:** `C:\MBB_PROJECT\Release note\MBB_release_note_v9.1.md`

---

**⚠️ หมายเหตุสำคัญ:** 
- คู่มือนี้ควรอัปเดตทุกครั้งที่มีการเปลี่ยนแปลงหน้าเว็บ
- เก็บ backup ของเวอร์ชั่นที่ทำงานได้ดีก่อนทำการแก้ไขครั้งใหญ่
- ทดสอบใน multiple browsers และ devices ก่อน deploy

**🎯 การใช้งานคู่มือนี้:**
1. อ่านส่วน "ภาพรวมของเว็บไซต์" เพื่อเข้าใจโครงสร้าง
2. ดู "ลิงก์และทรัพยากรสำคัญ" เพื่อทำความเข้าใจ dependencies
3. ใช้ "คำแนะนำสำหรับการพัฒนาต่อ" เป็น guideline
4. ปฏิบัติตาม "Testing Checklist" ก่อนทำการอัปเดต