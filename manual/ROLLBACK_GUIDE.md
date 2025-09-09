# 🔄 Complete Rollback Guide

## **Emergency Rollback Commands**

### **Quick Rollback All Changes**
```bash
cd /c/MBB_PROJECT

# Restore all backup files
cp settings_backup_phase1.json settings.json
cp dialogue_cache_backup_phase2.py dialogue_cache.py  
cp control_ui_backup_phase3.py control_ui.py
cp advance_ui_backup_phase3.py advance_ui.py

# Restart MBB to apply changes
```

---

## **Individual Phase Rollbacks**

### **Phase 1: CPU Limit Rollback**
```bash
# Restore settings.json
cp settings_backup_phase1.json settings.json

# Verify rollback
grep "cpu_limit" settings.json
# Should show: "cpu_limit": 80,
```

### **Phase 2: Cache System Rollback** 
```bash
# Restore dialogue_cache.py
cp dialogue_cache_backup_phase2.py dialogue_cache.py

# Verify file size
wc -l dialogue_cache.py
# Should show: 158 lines
```

### **Phase 3: CPU Monitoring Rollback**
```bash
# Restore UI files
cp control_ui_backup_phase3.py control_ui.py
cp advance_ui_backup_phase3.py advance_ui.py

# Verify CPU monitoring restored
grep -n "cpu_limit" control_ui.py
# Should find monitoring code
```

---

## **Verification After Rollback**

### **Step 1: File Integrity Check**
```bash
# Check file sizes match originals
ls -la settings.json dialogue_cache.py control_ui.py advance_ui.py

# Compare with backup directory if needed
```

### **Step 2: Launch Test**
1. Start MBB v9
2. Open Advanced Settings 
3. Verify CPU limit shows 80%
4. Perform test translation
5. Check logs for any errors

### **Step 3: Functionality Verification**
- [x] Translation works normally
- [x] Advanced Settings opens without errors
- [x] CPU monitoring displays (if Phase 3 rolled back)
- [x] Cache functionality working
- [x] No error messages in logs

---

## **Partial Rollback Scenarios**

### **Scenario 1: Phase 1 Issues**
**Problem**: CPU 100% causes system instability
**Solution**: 
```bash
# Roll back to 80% but keep other optimizations
cp settings_backup_phase1.json settings.json
# Keep Phases 2 & 3 changes
```

### **Scenario 2: Phase 2 Issues** 
**Problem**: Cache optimization causes translation errors
**Solution**:
```bash
# Roll back cache only
cp dialogue_cache_backup_phase2.py dialogue_cache.py
# Keep CPU limit at 100% and monitoring changes
```

### **Scenario 3: Phase 3 Issues**
**Problem**: Missing CPU UI causes user confusion
**Solution**:
```bash
# Roll back UI changes only
cp advance_ui_backup_phase3.py advance_ui.py
# Keep performance optimizations
```

---

## **Backup File Locations**

All backup files are stored in the main project directory:
- `settings_backup_phase1.json` - Original settings
- `dialogue_cache_backup_phase2.py` - Original cache system  
- `control_ui_backup_phase3.py` - Original control UI
- `advance_ui_backup_phase3.py` - Original advanced UI

---

## **Re-optimization After Rollback**

If you need to rollback and re-apply changes:

### **Safe Re-implementation Order**:
1. **Start with Phase 1 only** - CPU limit to 90% (compromise)
2. **Test for stability** - Run for 30+ minutes  
3. **Apply Phase 2 partially** - Remove TTL but keep timestamps
4. **Gradual optimization** - Increment changes slowly

### **Conservative Settings**:
- CPU Limit: 90% instead of 100%
- Cache Size: 75 instead of 50
- Keep some monitoring for debugging

---

## **Support Information**

### **If All Rollbacks Fail**:
1. **Full project restore** from your backup directory
2. **Fresh git clone** if using version control
3. **Contact support** with error logs

### **Performance Baseline Recovery**:
After rollback, performance should return to:
- Original translation speeds (60% slower than Yariman)
- Stable CPU usage at 80% limit
- Full monitoring and UI functionality

---

**Created**: 2025-01-09  
**Status**: READY FOR USE  
**Priority**: CRITICAL REFERENCE