"""
Asset Management System for MBB Project
Centralized asset path management with PyInstaller compatibility
"""
import os
import sys
from PIL import Image, ImageTk
from resource_utils import resource_path


class AssetManager:
    """Centralized asset management system"""
    
    # Define all available assets for validation
    AVAILABLE_ASSETS = {
        # Application Icons
        "app_icon.ico",
        "mbb_icon.png",
        
        # UI Control Icons
        "red_icon.png",
        "black_icon.png",
        "theme.png",
        "setting.png",
        "camera.png",
        "expand.png",
        
        # Pin System Icons
        "pin.png",
        "unpin.png",
        "pin_black.png",
        "pin_white.png",
        
        # Action Icons
        "force.png",
        "s_force.png",
        "s_force_m.png",
        "confirm.png",
        "hide.png",
        "trans.png",
        "swap.png",
        "resize.png",
        "scale.png",
        "gap.png",
        "normal.png",
        "arrow.png",
        "fade.png",
        
        # Theme Icons
        "theme_0.png",
        "theme_A.png",
        "theme_C.png",
        
        # Background Assets
        "TUI_BG.png",
        "BG_lock.png",
        "white_lock.png",
        
        # Splash Screen Assets
        "MBB_splash.png",
        "MBB_splash_vid.mp4",
    }
    
    @staticmethod
    def get_asset_path(filename):
        """
        Get path to asset file with PyInstaller compatibility
        
        Args:
            filename (str): Asset filename (e.g., 'theme.png')
            
        Returns:
            str: Absolute path to asset file
            
        Raises:
            FileNotFoundError: If asset file doesn't exist
        """
        # Try assets/ folder first (preferred)
        assets_path = resource_path(os.path.join("assets", filename))
        if os.path.exists(assets_path):
            return assets_path
        
        # Fallback to root directory (legacy support)
        root_path = resource_path(filename)
        if os.path.exists(root_path):
            return root_path
        
        # Asset not found
        raise FileNotFoundError(f"Asset not found: {filename}")
    
    @staticmethod
    def load_icon(filename, size=None):
        """
        Load icon from assets with optional resize
        
        Args:
            filename (str): Icon filename (e.g., 'theme.png')
            size (tuple): Optional resize (width, height)
            
        Returns:
            ImageTk.PhotoImage: Loaded icon ready for Tkinter
            
        Raises:
            FileNotFoundError: If icon file doesn't exist
        """
        try:
            asset_path = AssetManager.get_asset_path(filename)
            image = Image.open(asset_path)
            
            if size:
                image = image.resize(size, Image.Resampling.LANCZOS)
            
            return ImageTk.PhotoImage(image)
        
        except Exception as e:
            print(f"Error loading icon {filename}: {e}")
            # Return a placeholder or re-raise
            raise
    
    @staticmethod
    def load_pil_image(filename, size=None):
        """
        Load PIL Image directly without converting to PhotoImage
        
        Args:
            filename (str): Image filename (e.g., 'red_icon.png')
            size (tuple): Optional resize (width, height)
            
        Returns:
            PIL.Image: PIL Image object for processing
            
        Raises:
            FileNotFoundError: If image file doesn't exist
        """
        try:
            asset_path = AssetManager.get_asset_path(filename)
            image = Image.open(asset_path)
            
            if size:
                image = image.resize(size, Image.Resampling.LANCZOS)
            
            return image
        
        except Exception as e:
            print(f"Error loading PIL image {filename}: {e}")
            raise
    
    @staticmethod
    def validate_asset(filename):
        """
        Validate if asset exists and is accessible
        
        Args:
            filename (str): Asset filename
            
        Returns:
            bool: True if asset is valid and accessible
        """
        try:
            AssetManager.get_asset_path(filename)
            return True
        except FileNotFoundError:
            return False
    
    @staticmethod
    def list_available_assets():
        """
        List all available assets in the system
        
        Returns:
            dict: Dictionary with asset status {'filename': exists_bool}
        """
        status = {}
        for asset in AssetManager.AVAILABLE_ASSETS:
            status[asset] = AssetManager.validate_asset(asset)
        return status
    
    @staticmethod
    def get_missing_assets():
        """
        Get list of missing assets
        
        Returns:
            list: List of missing asset filenames
        """
        missing = []
        for asset in AssetManager.AVAILABLE_ASSETS:
            if not AssetManager.validate_asset(asset):
                missing.append(asset)
        return missing
    
    @staticmethod
    def ensure_assets_folder():
        """
        Ensure assets folder exists and contains all necessary assets
        
        Returns:
            bool: True if all assets are available
        """
        missing = AssetManager.get_missing_assets()
        if missing:
            print(f"Missing assets: {missing}")
            return False
        return True


def test_asset_manager():
    """Test function for AssetManager"""
    print("Testing AssetManager...")
    
    # Test asset validation
    print("\\n=== Asset Status ===")
    assets_status = AssetManager.list_available_assets()
    for asset, exists in assets_status.items():
        status = "✅" if exists else "❌"
        print(f"{status} {asset}")
    
    # Test missing assets
    missing = AssetManager.get_missing_assets()
    if missing:
        print(f"\\n❌ Missing assets: {missing}")
    else:
        print("\\n✅ All assets available!")
    
    # Test icon loading (if assets available)
    if not missing:
        try:
            print("\\n=== Testing Icon Loading ===")
            icon = AssetManager.load_icon("red_icon.png", (20, 20))
            print("✅ Icon loading test passed")
        except Exception as e:
            print(f"❌ Icon loading test failed: {e}")


if __name__ == "__main__":
    test_asset_manager()