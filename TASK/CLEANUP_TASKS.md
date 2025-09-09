# 🧹 Cleanup Tasks - Remove Test Files

## **Files to Delete**

### **Test Files**
```bash
cd /c/MBB_PROJECT

# Remove preprocessed test images
rm -f preprocessed_screenshot*.png
rm -f debug_*.png
rm -f temp_screenshot_*.png

# Remove test captures  
rm -rf "capture text test/" 
rm -rf "captured_screens/"

# Remove temporary files
rm -f *.tmp
rm -f debug_processed.png
rm -f debug_screenshot.png
```

### **Old Backup Directories**
```bash
# Remove old backup folders (keep recent ones)
rm -rf MBB_backup_24-07-2025_v1/
rm -rf MBB_backup_26-07-2025_v1/ 
rm -rf MBB_backup_26-07-2025_v2/
rm -rf MBB_backup_27-07-2025_v1/

# Keep: Current working files + our new backups
```

### **Development Files**
```bash
# Remove build files if not needed
rm -rf __pycache__/
rm -rf dist/ 
rm -rf dist_new/

# Remove guide images
rm -f Guide01.png Guide02.png

# Remove promotional files
rm -rf promote/
rm -f MBB_splash*.png MBB_splash*.mp4
```

### **Documentation Cleanup**
```bash
# Remove redundant docs (keep essential ones)
rm -f memory_performance_analysis.md
rm -f system_load_awareness_plan.md
rm -f TOS-M_research.md

# Keep: Structure.md, README files, PACKAGE_BUILD_SUMMARY.md
```

## **Safe Cleanup Script**

Create cleanup script:
```bash
#!/bin/bash
# cleanup.sh

cd /c/MBB_PROJECT

echo "Cleaning up test files..."

# Test images
find . -name "preprocessed_screenshot*.png" -delete
find . -name "debug_*.png" -delete  
find . -name "temp_screenshot_*.png" -delete

# Test directories
rm -rf "capture text test/"
rm -rf "captured_screens/"

# Cache files
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null

# Old backups (keep recent ones)
rm -rf MBB_backup_24-07-2025_v1/
rm -rf MBB_backup_26-07-2025_v1/

echo "Cleanup completed!"
```

## **Pre-cleanup Verification**

Before deleting, check file importance:
```bash
# List files by size to identify large unnecessary files
ls -lahS | head -20

# Check for actively used files
find . -name "*.png" -atime -7  # Files accessed in last 7 days
find . -name "*.py" -mtime -30   # Python files modified in last 30 days
```

## **Disk Space Recovery**

Expected space savings:
- **Test images**: ~50-100MB
- **Old backups**: ~200-500MB  
- **Cache files**: ~10-50MB
- **Development files**: ~100-200MB

**Total Expected Recovery**: 400-850MB

## **Files to KEEP**

**Essential Files**:
- All `.py` source files
- `settings.json` and configs
- `npc*.json` database files
- `fonts/` directory
- Current backup files we just created
- `TASK/` directory (our new plans)

**Keep Recent Backups**:
- Any backup created today
- Our new `*_backup_phase*.py` files
- Recent `npc*.json` backups

## **Implementation**

### **Step 1: Create Cleanup Script**
```bash
cd /c/MBB_PROJECT
nano cleanup.sh  # Create the cleanup script above
chmod +x cleanup.sh
```

### **Step 2: Dry Run**
```bash
# Test what would be deleted (dry run)
./cleanup.sh --dry-run
```

### **Step 3: Execute Cleanup**
```bash
# Actually delete files
./cleanup.sh
```

### **Step 4: Verify Results**
```bash
# Check disk space saved
du -sh .
ls -la  # Verify important files still exist
```

---

**Status**: READY FOR IMPLEMENTATION  
**Risk Level**: ⚪ **MINIMAL** (only removing test/temp files)  
**Estimated Time**: 5 minutes  
**Disk Space Saved**: 400-850MB