"""
Icon Manager for MBB Project
Version: v1.0
Purpose: Centralized icon management for all windows
Features: Taskbar icon, title bar icon, fallback handling
"""

import os
import logging
from typing import Optional


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    import sys
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)


def set_window_icon(window, icon_filename: str = "assets/app_icon.ico", log_manager=None) -> bool:
    """
    Set icon for tkinter window (both taskbar and title bar)
    
    Args:
        window: tkinter window object (Tk or Toplevel)
        icon_filename: relative path to icon file
        log_manager: optional logging manager
        
    Returns:
        bool: True if icon was set successfully, False otherwise
    """
    try:
        icon_path = resource_path(icon_filename)
        
        if not os.path.exists(icon_path):
            if log_manager:
                log_manager.log_warning(f"Icon file not found: {icon_path}")
            else:
                logging.warning(f"Icon file not found: {icon_path}")
            return False
        
        # Method 1: iconbitmap for title bar (traditional method)
        window.iconbitmap(icon_path)
        
        # Method 2: iconphoto for taskbar (modern method, better Windows support)
        try:
            from PIL import Image, ImageTk
            
            # Load icon with PIL and convert to PhotoImage
            icon_image = Image.open(icon_path)
            
            # Resize icon for taskbar (32x32 is optimal for Windows taskbar)
            icon_image = icon_image.resize((32, 32), Image.Resampling.LANCZOS)
            icon_photo = ImageTk.PhotoImage(icon_image)
            
            # Set icon for taskbar (True means apply to all windows)
            window.iconphoto(True, icon_photo)
            
            # Store reference to prevent garbage collection
            if not hasattr(window, '_icon_references'):
                window._icon_references = []
            window._icon_references.append(icon_photo)
            
            if log_manager:
                log_manager.log_info(f"Set taskbar and title bar icon from: {icon_path}")
            else:
                logging.info(f"Set taskbar and title bar icon from: {icon_path}")
                
            return True
            
        except ImportError:
            # PIL not available, use iconbitmap only
            if log_manager:
                log_manager.log_warning("PIL not available, using iconbitmap only")
            else:
                logging.warning("PIL not available, using iconbitmap only")
            return True
            
        except Exception as e:
            # PIL failed, but iconbitmap might still work
            if log_manager:
                log_manager.log_warning(f"Failed to set taskbar icon: {e}")
                log_manager.log_info(f"Using iconbitmap only from: {icon_path}")
            else:
                logging.warning(f"Failed to set taskbar icon: {e}")
                logging.info(f"Using iconbitmap only from: {icon_path}")
            return True
            
    except Exception as e:
        if log_manager:
            log_manager.log_error(f"Failed to set window icon: {e}")
        else:
            logging.error(f"Failed to set window icon: {e}")
        return False


def set_window_icon_simple(window, icon_filename: str = "assets/app_icon.ico") -> bool:
    """
    Simplified version without logging for quick use
    
    Args:
        window: tkinter window object
        icon_filename: relative path to icon file
        
    Returns:
        bool: True if successful, False otherwise
    """
    return set_window_icon(window, icon_filename, None)


# For backward compatibility
def setup_window_icon(window, log_manager=None):
    """Backward compatibility function"""
    return set_window_icon(window, "assets/app_icon.ico", log_manager)