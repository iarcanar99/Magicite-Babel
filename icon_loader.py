"""
Utility function for finding icon files with assets folder fallback
Add this to your main modules to handle icon loading from assets/ folder
"""
import os
from PIL import Image, ImageTk

def load_icon(filename, size=None, fallback_to_root=True):
    """
    Load icon with assets/ folder priority and root fallback
    
    Args:
        filename (str): Icon filename (e.g., 'theme.png')
        size (tuple): Optional resize (width, height)
        fallback_to_root (bool): Try root folder if assets/ not found
    
    Returns:
        PIL.Image or ImageTk.PhotoImage: Loaded image
    """
    paths_to_try = [
        os.path.join('assets', filename),  # Try assets/ first
    ]
    
    if fallback_to_root:
        paths_to_try.append(filename)  # Fallback to root
    
    for path in paths_to_try:
        if os.path.exists(path):
            try:
                img = Image.open(path)
                if size:
                    img = img.resize(size, Image.Resampling.LANCZOS)
                return img
            except Exception as e:
                print(f"Error loading {path}: {e}")
                continue
    
    # If all fails, create a placeholder
    print(f"Warning: Could not load icon '{filename}' from any location")
    placeholder = Image.new('RGBA', size or (32, 32), (128, 128, 128, 255))
    return placeholder

def load_icon_tk(filename, size=None, fallback_to_root=True):
    """Load icon and return as ImageTk.PhotoImage"""
    img = load_icon(filename, size, fallback_to_root)
    return ImageTk.PhotoImage(img)

# Example usage:
# self.theme_icon = load_icon_tk("theme.png", (24, 24))
# self.expand_icon = load_icon_tk("expand.png", (28, 28))
