# 🔒 Security Configuration

## ⚠️ IMPORTANT: API Key Setup

**NEVER commit your actual API keys to Git!**

### Setup Instructions:

1. **Copy the example file:**
   ```bash
   cp api_config.json.example api_config.json
   ```

2. **Add your Google API Key:**
   ```json
   {
     "api_key": "YOUR_ACTUAL_GOOGLE_API_KEY_HERE",
     "status": "active",
     "last_reset": 0
   }
   ```

3. **Verify .gitignore protection:**
   - `api_config.json` is already in `.gitignore`
   - This prevents accidental commits of your API key

### Security Best Practices:

- ✅ Keep API keys in local files only
- ✅ Use environment variables when possible
- ✅ Rotate keys regularly
- ✅ Monitor Google Cloud Console for unauthorized usage
- ❌ Never share API keys in screenshots or logs
- ❌ Never commit actual keys to version control

### If You Accidentally Committed a Key:

1. **Immediately rotate/revoke the key** in Google Cloud Console
2. **Remove from Git history** using this guide
3. **Generate a new key** for your project

## 🛡️ Additional Security

- All sensitive configuration files are listed in `.gitignore`
- Local development files are protected
- No credentials are stored in source code