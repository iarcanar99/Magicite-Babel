# simple_model_config.py - Simple API Configuration UI

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os

class SimpleModelConfig:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MBB - API Configuration")
        self.root.geometry("500x400")
        self.root.configure(bg='#2b2b2b')
        
        # Variables
        self.api_key_var = tk.StringVar()
        self.model_var = tk.StringVar()
        
        # Load current settings
        self.load_current_settings()
        
        self.create_ui()
        
    def create_ui(self):
        # Title
        title_label = tk.Label(self.root, text="API Configuration", 
                              font=('Arial', 16, 'bold'), 
                              bg='#2b2b2b', fg='white')
        title_label.pack(pady=20)
        
        # Main frame
        main_frame = tk.Frame(self.root, bg='#2b2b2b')
        main_frame.pack(expand=True, fill='both', padx=20, pady=10)
        
        # API Key section
        api_frame = tk.LabelFrame(main_frame, text="API Key", 
                                 font=('Arial', 12, 'bold'),
                                 bg='#3b3b3b', fg='white', bd=2)
        api_frame.pack(fill='x', pady=10)
        
        tk.Label(api_frame, text="Current API Key:", 
                bg='#3b3b3b', fg='white').pack(anchor='w', padx=10, pady=5)
        
        api_entry = tk.Entry(api_frame, textvariable=self.api_key_var, 
                           font=('Arial', 10), width=50, show='*')
        api_entry.pack(padx=10, pady=5)
        
        # Show/Hide API Key button
        show_btn = tk.Button(api_frame, text="Show/Hide Key", 
                           command=self.toggle_api_visibility,
                           bg='#4b4b4b', fg='white')
        show_btn.pack(pady=5)
        
        # Model selection
        model_frame = tk.LabelFrame(main_frame, text="AI Model", 
                                   font=('Arial', 12, 'bold'),
                                   bg='#3b3b3b', fg='white', bd=2)
        model_frame.pack(fill='x', pady=10)
        
        tk.Label(model_frame, text="Select Model:", 
                bg='#3b3b3b', fg='white').pack(anchor='w', padx=10, pady=5)
        
        models = [
            "gemini-2.0-flash",
            "gemini-2.0-flash-lite", 
            "gemini-2.5-flash",
        ]
        
        model_combo = ttk.Combobox(model_frame, textvariable=self.model_var, 
                                  values=models, state='readonly', width=47)
        model_combo.pack(padx=10, pady=5)
        
        # Instructions
        info_frame = tk.LabelFrame(main_frame, text="Instructions", 
                                  font=('Arial', 12, 'bold'),
                                  bg='#3b3b3b', fg='white', bd=2)
        info_frame.pack(fill='x', pady=10)
        
        instructions = """
1. Enter your API key above
2. Select the AI model you want to use
3. Click 'Save Settings' to apply changes
4. Close this window to return to MBB

API Key formats:
• Gemini: AIza...
        """
        
        tk.Label(info_frame, text=instructions, justify='left',
                bg='#3b3b3b', fg='#cccccc', font=('Arial', 9)).pack(padx=10, pady=10)
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg='#2b2b2b')
        button_frame.pack(fill='x', pady=20)
        
        save_btn = tk.Button(button_frame, text="Save Settings", 
                           command=self.save_settings,
                           bg='#4CAF50', fg='white', font=('Arial', 12, 'bold'),
                           padx=20, pady=10)
        save_btn.pack(side='left', padx=10)
        
        test_btn = tk.Button(button_frame, text="Test API", 
                           command=self.test_api,
                           bg='#2196F3', fg='white', font=('Arial', 12),
                           padx=20, pady=10)
        test_btn.pack(side='left', padx=10)
        
        close_btn = tk.Button(button_frame, text="Close", 
                            command=self.root.destroy,
                            bg='#f44336', fg='white', font=('Arial', 12),
                            padx=20, pady=10)
        close_btn.pack(side='right', padx=10)
        
    def load_current_settings(self):
        """โหลดการตั้งค่าปัจจุบัน"""
        try:
            # Load API key
            with open('api_config.json', 'r') as f:
                api_config = json.load(f)
                self.api_key_var.set(api_config.get('api_key', ''))
        except:
            self.api_key_var.set('')
            
        try:
            # Load model
            with open('settings.json', 'r') as f:
                settings = json.load(f)
                model = settings.get('api_parameters', {}).get('model', 'gemini-2.0-flash')
                self.model_var.set(model)
        except:
            self.model_var.set('gemini-2.0-flash')
    
    def toggle_api_visibility(self):
        """แสดง/ซ่อน API key"""
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, tk.LabelFrame):
                        for entry in child.winfo_children():
                            if isinstance(entry, tk.Entry):
                                if entry['show'] == '*':
                                    entry.config(show='')
                                else:
                                    entry.config(show='*')
    
    def save_settings(self):
        """บันทึกการตั้งค่า"""
        api_key = self.api_key_var.get().strip()
        model = self.model_var.get()
        
        if not api_key:
            messagebox.showerror("Error", "Please enter an API key")
            return
            
        if not model:
            messagebox.showerror("Error", "Please select a model")
            return
        
        try:
            # Save API key
            api_config = {
                "api_key": api_key,
                "status": "active",
                "last_reset": 0
            }
            
            with open('api_config.json', 'w') as f:
                json.dump(api_config, f, indent=2)
            
            # Update settings.json
            try:
                with open('settings.json', 'r') as f:
                    settings = json.load(f)
            except:
                settings = {}
                
            if 'api_parameters' not in settings:
                settings['api_parameters'] = {}
                
            settings['api_parameters']['model'] = model
            settings['api_parameters']['displayed_model'] = model
            
            with open('settings.json', 'w') as f:
                json.dump(settings, f, indent=2)
            
            messagebox.showinfo("Success", "Settings saved successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    def test_api(self):
        """ทดสอบ API (พื้นฐาน)"""
        api_key = self.api_key_var.get().strip()
        model = self.model_var.get()
        
        if not api_key:
            messagebox.showerror("Error", "Please enter an API key first")
            return
            
        # Basic validation
        valid = False
        if "gemini" in model.lower() and api_key.startswith("AIza"):
            valid = True
            
        if valid:
            messagebox.showinfo("Test Result", f"✓ API key format is valid for {model}")
        else:
            messagebox.showwarning("Test Result", f"⚠ API key format may not match {model}")
    
    def run(self):
        """รัน UI"""
        self.root.mainloop()

if __name__ == "__main__":
    app = SimpleModelConfig()
    app.run()
