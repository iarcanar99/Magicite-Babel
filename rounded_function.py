def apply_rounded_corners_to_ui(self, radius=6):
    """🎨 ทำให้หน้าต่าง UI มีขอบโค้งมนแบบละเอียด

    Args:
        radius: รัศมีของขอบโค้ง (6px = ละเอียดมาก, เกือบจะเหลี่ยม แต่ไม่เหลี่ยม)
    """
    try:
        import logging

        logging.info(f"🎨 เริ่มใส่ขอบโค้งมน radius {radius}px...")

        # รอให้หน้าต่างแสดงผลและ settle ก่อน
        self.root.update_idletasks()

        # ดึงค่า HWND ของหน้าต่าง
        hwnd = windll.user32.GetParent(self.root.winfo_id())
        logging.info(f"🪟 HWND ที่ได้: {hwnd}")

        if hwnd:
            # สร้างภูมิภาค (region) โค้งมนตามขนาดปัจจุบัน
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            logging.info(f"📏 ขนาดหน้าต่าง: {width}x{height}")

            # สร้าง rounded rectangle region
            region = win32gui.CreateRoundRectRgn(
                0, 0, width + 1, height + 1, radius, radius
            )
            logging.info(f"🔄 สร้าง region: {region}")

            # ใช้ region กับหน้าต่าง
            result = win32gui.SetWindowRgn(hwnd, region, True)
            logging.info(f"✅ SetWindowRgn ผลลัพธ์: {result}")

            # ลบ region object หลังใช้งาน
            win32gui.DeleteObject(region)
            logging.info(f"🎊 ใส่ขอบโค้งมนสำเร็จ! radius={radius}px")
        else:
            logging.warning("⚠️ ไม่พบ HWND หน้าต่าง")

    except Exception as e:
        # ไม่ให้ error นี้ทำให้โปรแกรมหยุดทำงาน
        logging.error(f"❌ Error applying rounded corners to UI: {e}")
        import traceback

        traceback.print_exc()
