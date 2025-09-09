# Translated Logs Module - คู่มือการพัฒนา

## ข้อมูลเวอร์ชั่น
- **เวอร์ชั่น**: 2.1.0
- **อัพเดตล่าสุด**: 2025-07-18
- **สถานะ**: Stable Production Ready

## ภาพรวม
โมดูล `translated_logs.py` เป็นส่วนของระบบแสดงประวัติการแปลภาษาแบบ realtime ในรูปแบบ chat interface ที่ทันสมัย พร้อมระบบ Smart Cache และ Position Lock ที่เสถียร

## โครงสร้างหลัก

### Classes

#### 1. `LightweightChatBubble`
- **วัตถุประสงค์**: สร้าง bubble แสดงข้อความแต่ละรายการ
- **คุณสมบัติ**: 
  - รองรับ font ที่เปลี่ยนแปลงได้
  - ปรับขนาดตาม content อัตโนมัติ
  - ประสิทธิภาพสูง ใช้ tk.Frame และ tk.Label

#### 2. `Translated_Logs`
- **วัตถุประสงค์**: คลาสหลักจัดการ UI และระบบต่างๆ
- **ระบบย่อย**:
  - Smart Cache System
  - Position Lock System
  - Font Management
  - Animation System

## ระบบสำคัญ

### 1. Position Lock System
```python
# การใช้งาน
self.toggle_position_lock()  # เปิด/ปิด lock mode

# เมื่อเปิด lock:
- บันทึกตำแหน่งและขนาดปัจจุบันทันที
- ใช้ตำแหน่งที่ล็อกในทุกการเปิดครั้งต่อไป
- ไอคอนเปลี่ยนเป็น 🔒 (สีแดง)
- สถานะแสดง "Position Locked"

# เมื่อปิด lock:
- เคลียร์ข้อมูลล็อกทั้งหมด
- เปลี่ยนสถานะเป็น "Smart Mode" 
- smart positioning จะทำงานในรอบถัดไป
- ไอคอนกลับเป็น 🔓 (สีเทา)
- ไม่ปรับตำแหน่งทันทีเพื่อป้องกัน UI หาย
```

### 2. Smart Cache System
```python
# ระบบแทนที่ข้อความอัจฉริยะ
self.enable_smart_replacement = True/False

# การทำงาน:
- ตรวจจับการแปลซ้ำของข้อความเดิม
- แทนที่ bubble ล่าสุดแทนการเพิ่มใหม่
- ลดความซ้ำซ้อนและเพิ่มประสิทธิภาพ
```

### 3. Font Management
```python
# ระบบจัดการฟอนต์
self.font_manager = FontManager()
self.font_settings = FontSettings()

# การเปลี่ยนฟอนต์:
- รองรับการเปลี่ยน font family และ size
- อัปเดต bubble ทั้งหมดพร้อมกัน
- บันทึกค่าใน settings อัตโนมัติ
```

## Controls หลัก

### Bottom Controls
1. **Lock Button** (`🔓`/`🔒`): ล็อก/ปลดล็อกตำแหน่ง
2. **Transparency Button**: ปรับความโปร่งใส
3. **Reverse Button** (`↕`): เรียงลำดับข้อความ
4. **Smart Button** (`ON`/`OFF`): เปิด/ปิด smart replacement
5. **Font Button**: เปิด font manager

### Header Controls
- **Font Size Controls** (`-`/`+`): ปรับขนาดฟอนต์
- **Close Button** (`✕`): ปิดหน้าต่าง

## การตั้งค่า

### Settings Keys
```python
# ตำแหน่งและขนาด
"logs_width": int
"logs_height": int
"logs_x": int  
"logs_y": int

# โหมดต่างๆ
"logs_position_locked": bool
"logs_locked_geometry": str
"logs_reverse_mode": bool

# ฟอนต์
"logs_font_family": str
"logs_font_size": int
```

### ไฟล์ที่เกี่ยวข้อง
- `settings.py`: การจัดการ settings
- `appearance.py`: การจัดการสีและธีม
- `font_manager.py`: การจัดการฟอนต์

## API หลัก

### การเพิ่มข้อความ
```python
# เพิ่มข้อความใหม่
logs.add_message("Speaker: ข้อความ", is_force_retranslation=False)

# หรือ
logs.add_message_from_translation("ข้อความ", is_force_translate=False)
```

### การจัดการ UI
```python
# แสดง/ซ่อน
logs.show_window()
logs.hide_window()

# ล้างข้อมูล
logs.clear_logs()

# cleanup
logs.cleanup()
```

## Performance & Optimization

### Memory Management 
- จำกัดจำนวน bubble สูงสุด (auto-cleanup เมื่อเกิน limit)
- ใช้ LightweightChatBubble สำหรับประสิทธิภาพสูง
- Smart animation system ที่ปรับปรุงแล้ว
- Optimized imports (ลบ duplicate imports)

### Code Quality
- **Version 2.1.0**: ลดโค้ดซ้ำซ้อน 15%
- Centralized imports (time, hashlib ที่ module level)
- Reduced verbose logging สำหรับ production
- Cleaned unused debugging functions

### Scroll Performance
- Custom scrollbar ที่เร็วกว่า tkinter มาตรฐาน
- Smart repack (repack เฉพาะเมื่อจำเป็น)
- Throttled updates (60fps max) สำหรับ smooth experience

## Debugging

### Logging
```python
# เปิด debug logging
logging.basicConfig(level=logging.INFO)

# ดู cache stats
stats = logs.get_cache_stats()
```

### Common Issues
1. **ฟอนต์ไม่เปลี่ยน**: ตรวจสอบ font_manager connection
2. **ตำแหน่งไม่บันทึก**: ตรวจสอบ settings.py
3. **Performance ช้า**: ตรวจสอบจำนวน bubble และ animation

## การพัฒนาต่อ

### การเพิ่มฟีเจอร์ใหม่
1. เพิ่มปุ่มใน `setup_bottom_controls()`
2. สร้างฟังก์ชัน handler
3. อัปเดต settings หากจำเป็น
4. เพิ่ม binding events

### การปรับปรุง Performance
1. ใช้ `root.after()` แทน `time.sleep()`
2. จำกัดการ repack bubbles
3. ใช้ `_add_hover_effect()` สำหรับ buttons
4. ปรับปรุง scroll animation

## Architecture Decisions

### Design Patterns
- **Observer Pattern**: FontSettings observers
- **Singleton Pattern**: FontUIManager
- **Strategy Pattern**: Smart positioning
- **Cache Pattern**: Message cache system

### UI Design
- **Flat Design**: ไม่มี rounded corners
- **Minimal Colors**: ใช้สีเทาเป็นหลัก
- **Consistent Spacing**: ใช้ dynamic padding
- **Responsive Layout**: ปรับตาม content

## ไฟล์ Dependencies

### Required Files
```
translated_logs.py      # Main module
appearance.py          # Color management  
settings.py           # Settings management
font_manager.py       # Font management

# Icon files (optional)
normal.png           # Unlock icon
BG_lock.png         # Lock icon  
swap.png            # Reverse icon
trans.png           # Transparency icon
resize.png          # Resize handle icon
```

### Python Dependencies
```python
tkinter             # UI framework
PIL (Pillow)        # Image processing
win32gui           # Windows API (optional)
win32api           # Windows API (optional)
```

## Version History

### Version 2.1.0 (2025-07-18) - Current ✅
**Major Fixes & Optimizations:**
- **Fixed**: Position lock system ปลอดภัย - UI ไม่หายเมื่อ unlock
- **Optimized**: ลดโค้ดซ้ำซ้อน 15% (centralized imports, removed unused functions)
- **Improved**: Status label position ไม่ทับ resize icon (+100px margin)
- **Enhanced**: Flat design buttons สำหรับ Smart mode และ Font manager
- **Cleaned**: Reduced verbose logging, improved code maintainability

**Technical Changes:**
- Centralized `time` และ `hashlib` imports
- แก้ไข unlock button ให้ปลด flag เท่านั้น (ไม่ปรับตำแหน่งทันที)
- ลบฟังก์ชัน debugging ที่ไม่ใช้
- อัพเดต documentation ให้ครบถ้วน

### Version 2.0.x Features
- Smart cache system ✅
- Position lock system ✅  
- Font management ✅
- Flat design UI ✅
- Performance optimizations ✅
- Custom scrollbar ✅
- Animation system ✅

### Future Improvements
- [ ] Export chat history
- [ ] Search functionality  
- [ ] Custom themes
- [ ] Keyboard shortcuts
- [ ] Multi-language UI
- [ ] Plugin system

---

**Note**: This module is part of the MBB_PROJECT translation system. See `Structure.md` for overall project documentation.
