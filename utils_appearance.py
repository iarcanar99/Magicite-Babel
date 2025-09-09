# utils_appearance.py
# Settings UI Theme Manager - Independent from MBB appearance system
# Created for advance_ui.py, simplified_hotkey_ui.py and related settings UI

import tkinter as tk
from tkinter import ttk


class SettingsUITheme:
    """
    Central theme manager สำหรับ Settings UI Group
    ใช้ Dark theme แบบอิสระจาก MBB appearance_manager
    """
    
    # Color Palette - Gray-based Dark Theme
    COLORS = {
        # Backgrounds
        'bg_primary': '#1E1E1E',        # พื้นหลังหลัก (เข้มสุด)
        'bg_secondary': '#2D2D2D',      # พื้นหลังปุ่ม/card
        'bg_tertiary': '#3D3D3D',       # พื้นหลัง input fields
        'bg_quaternary': '#252525',     # พื้นหลัง panels
        
        # Interactive States
        'hover_light': '#4D4D4D',       # สีเมื่อ hover (อ่อน)
        'hover_medium': '#5D5D5D',      # สีเมื่อ hover (เข้ม)
        'hover_dark': '#404040',        # สีเมื่อ hover (เข้มมาก)
        
        # Active/Selected States (สีขาว + ตัวอักษรดำ)
        'active_bg': '#FFFFFF',         # ปุ่มที่เปิดค้าง - พื้นหลัง  
        'active_text': '#000000',       # ปุ่มที่เปิดค้าง - ตัวอักษร
        'active_border': '#DDDDDD',     # ขอบปุ่มที่เปิดค้าง
        
        # Text Colors
        'text_primary': '#FFFFFF',      # ตัวอักษรหลัก (ขาวใส)
        'text_secondary': '#CCCCCC',    # ตัวอักษรรอง (ขาวอ่อน)
        'text_tertiary': '#AAAAAA',     # ตัวอักษร hint/placeholder
        'text_disabled': '#888888',     # ตัวอักษร disabled
        
        # Borders & Outlines
        'border_focus': '#6D6D6D',      # ขอบเมื่อ focus
        'border_normal': '#404040',     # ขอบปกติ
        'border_light': '#555555',      # ขอบอ่อน
        'border_disabled': '#333333',   # ขอบ disabled
        
        # Semantic Colors (เพิ่มในอนาคตถ้าจำเป็น)
        'success': '#4CAF50',           # สีเขียว สำหรับสถานะสำเร็จ
        'warning': '#FF9800',           # สีส้ม สำหรับ warning
        'error': '#F44336',             # สีแดง สำหรับ error
    }
    
    # Font Settings
    FONTS = {
        'family': 'Segoe UI',           # System font
        'size_small': 10,
        'size_normal': 11,
        'size_medium': 12,
        'size_large': 14,
        'size_title': 16,
    }
    
    # Spacing Scale
    SPACING = {
        'xs': 4,
        'sm': 8,
        'md': 12,
        'lg': 16,
        'xl': 20,
        'xxl': 24,
    }
    
    @classmethod
    def get_color(cls, key: str) -> str:
        """ดึงสีจาก color palette"""
        return cls.COLORS.get(key, '#FFFFFF')
    
    @classmethod
    def get_font(cls, size_key: str = 'normal', weight: str = 'normal') -> tuple:
        """สร้าง font tuple สำหรับ tkinter"""
        family = cls.FONTS['family']
        size = cls.FONTS.get(f'size_{size_key}', cls.FONTS['size_normal'])
        return (family, size, weight)
    
    @classmethod
    def get_spacing(cls, key: str) -> int:
        """ดึงค่า spacing"""
        return cls.SPACING.get(key, 8)


class ModernButton:
    """Helper class สำหรับสร้าง modern button"""
    
    def __init__(self, parent, text: str, command=None, is_active: bool = False, 
                 width: int = None, height: int = None):
        """
        สร้าง modern button ตาม Settings UI theme
        
        Args:
            parent: parent widget
            text: ข้อความในปุ่ม
            command: callback function
            is_active: ปุ่มอยู่ในสถานะ active หรือไม่
            width, height: ขนาดปุ่ม
        """
        self.theme = SettingsUITheme
        self.is_active = is_active
        self._text = text
        
        if is_active:
            bg_color = self.theme.get_color('active_bg')
            fg_color = self.theme.get_color('active_text')  # สีดำ
            active_bg = self.theme.get_color('active_bg')
            active_fg = self.theme.get_color('active_text')  # สีดำ
        else:
            bg_color = self.theme.get_color('bg_secondary')
            fg_color = self.theme.get_color('text_primary')  # สีขาว
            active_bg = self.theme.get_color('hover_light')
            active_fg = self.theme.get_color('text_primary')  # สีขาว
        
        self.button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg_color,
            fg=fg_color,
            activebackground=active_bg,
            activeforeground=active_fg,  # เพิ่มการตั้งค่า active foreground
            font=self.theme.get_font('normal'),
            relief='flat',
            bd=0,
            padx=self.theme.get_spacing('md'),
            pady=self.theme.get_spacing('sm'),
            cursor='hand2'
        )
        
        if width:
            self.button.config(width=width)
        if height:
            self.button.config(height=height)
            
        # เพิ่ม hover effect
        self._add_hover_effect()
    
    def pack(self, **kwargs):
        """Pack the button"""
        self.button.pack(**kwargs)
    
    def config(self, **kwargs):
        """Configure the button"""
        self.button.config(**kwargs)
    
    def set_text(self, text: str):
        """เปลี่ยนข้อความในปุ่ม"""
        self._text = text
        self.button.config(text=text)
    
    def update_colors(self, bg_color: str = None):
        """อัปเดตสีของปุ่ม"""
        if bg_color:
            if bg_color == 'success':
                new_bg = self.theme.get_color('success')
                new_fg = self.theme.get_color('text_primary')
            elif bg_color == 'bg_tertiary':
                new_bg = self.theme.get_color('bg_tertiary')
                new_fg = self.theme.get_color('text_disabled')
            else:
                new_bg = self.theme.get_color(bg_color)
                new_fg = self.theme.get_color('text_primary')
            
            self.button.config(bg=new_bg, fg=new_fg)
    
    def _add_hover_effect(self):
        """เพิ่ม hover effect ให้ปุ่ม"""
        if self.is_active:
            normal_bg = self.theme.get_color('active_bg')
            hover_bg = self.theme.get_color('active_bg')  # active ไม่เปลี่ยนสี hover
        else:
            normal_bg = self.theme.get_color('bg_secondary')
            hover_bg = self.theme.get_color('hover_light')
        
        def on_enter(e):
            self.button.config(bg=hover_bg)
            
        def on_leave(e):
            self.button.config(bg=normal_bg)
            
        self.button.bind("<Enter>", on_enter)
        self.button.bind("<Leave>", on_leave)
    
    @staticmethod
    def create(parent, text: str, command=None, is_active: bool = False, 
               width: int = None, height: int = None) -> tk.Button:
        """
        สร้าง modern button ตาม Settings UI theme (เก่า - เพื่อ backward compatibility)
        """
        theme = SettingsUITheme
        
        if is_active:
            bg_color = theme.get_color('active_bg')
            fg_color = theme.get_color('active_text')  # สีดำ
            active_bg = theme.get_color('active_bg')
            active_fg = theme.get_color('active_text')  # สีดำ
        else:
            bg_color = theme.get_color('bg_secondary')
            fg_color = theme.get_color('text_primary')  # สีขาว
            active_bg = theme.get_color('hover_light')
            active_fg = theme.get_color('text_primary')  # สีขาว
        
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg_color,
            fg=fg_color,
            activebackground=active_bg,
            activeforeground=active_fg,  # เพิ่มการตั้งค่า active foreground
            font=theme.get_font('normal'),
            relief='flat',
            bd=0,
            padx=theme.get_spacing('md'),
            pady=theme.get_spacing('sm'),
            cursor='hand2'
        )
        
        if width:
            btn.config(width=width)
        if height:
            btn.config(height=height)
            
        # เพิ่ม hover effect
        ModernButton._add_hover_effect_static(btn, is_active)
        
        return btn
    
    @staticmethod
    def _add_hover_effect_static(button: tk.Button, is_active: bool):
        """เพิ่ม hover effect ให้ปุ่ม (static version)"""
        theme = SettingsUITheme
        
        if is_active:
            normal_bg = theme.get_color('active_bg')
            hover_bg = theme.get_color('active_bg')  # active ไม่เปลี่ยนสี hover
        else:
            normal_bg = theme.get_color('bg_secondary')
            hover_bg = theme.get_color('hover_light')
        
        def on_enter(e):
            button.config(bg=hover_bg)
            
        def on_leave(e):
            button.config(bg=normal_bg)
            
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)


class ModernEntry:
    """Helper class สำหรับสร้าง modern entry field"""
    
    def __init__(self, parent, placeholder: str = "", width: int = None, textvariable=None, show: str = None):
        """สร้าง modern entry field"""
        self.theme = SettingsUITheme
        self.placeholder = placeholder
        
        self.entry = tk.Entry(
            parent,
            bg=self.theme.get_color('bg_tertiary'),
            fg=self.theme.get_color('text_primary'),
            insertbackground=self.theme.get_color('text_primary'),
            font=self.theme.get_font('normal'),
            relief='flat',
            bd=1,
            highlightthickness=1,
            highlightbackground=self.theme.get_color('border_normal'),
            highlightcolor=self.theme.get_color('border_focus'),
            textvariable=textvariable,
            show=show
        )
        
        if width:
            self.entry.config(width=width)
            
        # เพิ่ม placeholder effect
        if placeholder and not show:  # ไม่แสดง placeholder สำหรับ password field
            self._add_placeholder()
    
    def pack(self, **kwargs):
        """Pack the entry"""
        self.entry.pack(**kwargs)
    
    def bind(self, event, callback):
        """Bind event to entry"""
        self.entry.bind(event, callback)
    
    def config(self, **kwargs):
        """Configure the entry"""
        self.entry.config(**kwargs)
    
    def _add_placeholder(self):
        """เพิ่ม placeholder effect"""
        placeholder_color = self.theme.get_color('text_tertiary')
        normal_color = self.theme.get_color('text_primary')
        
        def on_focus_in(e):
            if self.entry.get() == self.placeholder:
                self.entry.delete(0, tk.END)
                self.entry.config(fg=normal_color)
        
        def on_focus_out(e):
            if not self.entry.get():
                self.entry.insert(0, self.placeholder)
                self.entry.config(fg=placeholder_color)
        
        # Set initial placeholder
        self.entry.insert(0, self.placeholder)
        self.entry.config(fg=placeholder_color)
        
        self.entry.bind('<FocusIn>', on_focus_in)
        self.entry.bind('<FocusOut>', on_focus_out)
    
    @staticmethod
    def create(parent, placeholder: str = "", width: int = None) -> tk.Entry:
        """สร้าง modern entry field (เก่า - เพื่อ backward compatibility)"""
        theme = SettingsUITheme
        
        entry = tk.Entry(
            parent,
            bg=theme.get_color('bg_tertiary'),
            fg=theme.get_color('text_primary'),
            insertbackground=theme.get_color('text_primary'),
            font=theme.get_font('normal'),
            relief='flat',
            bd=1,
            highlightthickness=1,
            highlightbackground=theme.get_color('border_normal'),
            highlightcolor=theme.get_color('border_focus')
        )
        
        if width:
            entry.config(width=width)
            
        # เพิ่ม placeholder effect
        if placeholder:
            ModernEntry._add_placeholder_static(entry, placeholder)
            
        return entry
    
    @staticmethod
    def _add_placeholder_static(entry: tk.Entry, placeholder: str):
        """เพิ่ม placeholder effect (static version)"""
        theme = SettingsUITheme
        placeholder_color = theme.get_color('text_tertiary')
        normal_color = theme.get_color('text_primary')
        
        def on_focus_in(e):
            if entry.get() == placeholder:
                entry.delete(0, tk.END)
                entry.config(fg=normal_color)
        
        def on_focus_out(e):
            if not entry.get():
                entry.insert(0, placeholder)
                entry.config(fg=placeholder_color)
        
        # Set initial placeholder
        entry.insert(0, placeholder)
        entry.config(fg=placeholder_color)
        
        entry.bind('<FocusIn>', on_focus_in)
        entry.bind('<FocusOut>', on_focus_out)


class ModernFrame:
    """Helper class สำหรับสร้าง modern frame/card"""
    
    def __init__(self, parent, bg_color: str = 'bg_secondary', relief: str = 'flat', bd: int = 0, title: str = None, padding: str = 'md'):
        """สร้าง modern frame"""
        self.theme = SettingsUITheme
        
        bg = self.theme.get_color(bg_color)
        
        self.frame = tk.Frame(
            parent,
            bg=bg,
            relief=relief,
            bd=bd
        )
        
        # เพิ่ม padding ถ้าต้องการ
        if title:
            self._add_title(title, padding)
    
    def pack(self, **kwargs):
        """Pack the frame"""
        self.frame.pack(**kwargs)
    
    def config(self, **kwargs):
        """Configure the frame"""
        self.frame.config(**kwargs)
    
    def _add_title(self, title: str, padding: str):
        """เพิ่มหัวข้อให้ frame"""
        pad_value = self.theme.get_spacing(padding)
        
        title_label = tk.Label(
            self.frame,
            text=title,
            bg=self.frame.cget('bg'),
            fg=self.theme.get_color('text_primary'),
            font=self.theme.get_font('medium', 'bold')
        )
        title_label.pack(pady=(pad_value, pad_value//2), padx=pad_value, anchor='w')
        
        # สร้าง separator
        separator = tk.Frame(
            self.frame,
            height=1,
            bg=self.theme.get_color('border_light')
        )
        separator.pack(fill='x', padx=pad_value, pady=(0, pad_value//2))
    
    @staticmethod
    def create_card(parent, title: str = None, padding: str = 'md') -> tk.Frame:
        """สร้าง modern card frame (เก่า - เพื่อ backward compatibility)"""
        theme = SettingsUITheme
        
        card = tk.Frame(
            parent,
            bg=theme.get_color('bg_secondary'),
            relief='flat',
            bd=1,
            highlightbackground=theme.get_color('border_light'),
            highlightthickness=1
        )
        
        # เพิ่ม padding
        pad_value = theme.get_spacing(padding)
        
        if title:
            # เพิ่มหัวข้อ card
            title_label = tk.Label(
                card,
                text=title,
                bg=theme.get_color('bg_secondary'),
                fg=theme.get_color('text_primary'),
                font=theme.get_font('medium', 'bold')
            )
            title_label.pack(pady=(pad_value, pad_value//2), padx=pad_value, anchor='w')
            
            # สร้าง separator
            separator = tk.Frame(
                card,
                height=1,
                bg=theme.get_color('border_light')
            )
            separator.pack(fill='x', padx=pad_value, pady=(0, pad_value//2))
        
        return card


# Usage example:
if __name__ == "__main__":
    # ตัวอย่างการใช้งาน
    root = tk.Tk()
    root.title("Settings UI Theme Demo")
    root.configure(bg=SettingsUITheme.get_color('bg_primary'))
    
    # สร้าง card
    card = ModernFrame.create_card(root, "Example Settings Card")
    card.pack(pady=20, padx=20, fill='x')
    
    # สร้างปุ่มปกติ
    normal_btn = ModernButton.create(card, "Normal Button")
    normal_btn.pack(pady=5)
    
    # สร้างปุ่ม active
    active_btn = ModernButton.create(card, "Active Button", is_active=True)
    active_btn.pack(pady=5)
    
    # สร้าง entry field
    entry = ModernEntry.create(card, "Enter text here...", width=30)
    entry.pack(pady=5)
    
    root.mainloop()
