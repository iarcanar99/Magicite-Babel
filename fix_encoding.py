#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MBB v9 Unicode/Encoding Fix
Fix encoding issues for Thai characters in Windows environment
"""

import sys
import os
import locale

def fix_encoding():
    """Fix encoding issues for Thai characters"""
    
    # Set environment variables for UTF-8
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['LANG'] = 'en_US.UTF-8'
    
    # Force stdout/stderr to UTF-8
    if sys.platform == 'win32':
        try:
            # Set console code page to UTF-8
            import subprocess
            subprocess.run(['chcp', '65001'], shell=True, capture_output=True)
        except:
            pass
    
    # Reconfigure stdout/stderr
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    
    print("[Encoding Fix] UTF-8 encoding applied successfully")
    print(f"[Encoding Fix] System encoding: {locale.getpreferredencoding()}")
    
if __name__ == "__main__":
    fix_encoding()