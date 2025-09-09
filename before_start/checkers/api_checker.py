# checkers/api_checker.py

import json
import os
import sys
import asyncio
from typing import Dict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from api_tester import APITester
except ImportError:
    APITester = None


class APIChecker:
    def __init__(self):
        self.project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.api_config_file = os.path.join(self.project_root, "api_config.json")
        self.settings_file = os.path.join(self.project_root, "settings.json")
        self.env_file = os.path.join(self.project_root, ".env")
        self.test_timeout = 10
        
        # Load environment variables from .env file
        self._load_env_file()

    def _load_env_file(self):
        """Load environment variables from .env file"""
        if os.path.exists(self.env_file):
            try:
                # Store all values from .env file, allowing later ones to override earlier ones
                env_vars = {}
                with open(self.env_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip()
                            # Store the value (even if empty, but we'll prefer non-empty later)
                            env_vars[key] = value
                
                # Set environment variables, preferring non-empty values
                for key, value in env_vars.items():
                    if value:  # Only set if value is not empty
                        os.environ[key] = value
                
            except Exception as e:
                print(f"Warning: Could not load .env file: {e}")

    def check_all(self) -> dict:
        result = {"status": "ready", "details": {}, "action_needed": None, "summary": ""}

        current_model = self._get_current_model()
        api_key = self._get_api_key(current_model)

        if not api_key or api_key == "YOUR_API_KEY_HERE":
            result["status"] = "error"
            result["details"][current_model] = {"connected": False, "error": "API key not configured"}
            result["action_needed"] = "Configure API key"
            result["summary"] = f"Need to configure API key for {current_model}"
            return result

        test_result = self._test_current_api(current_model, api_key)
        result["details"][current_model] = test_result

        if test_result["connected"]:
            result["status"] = "ready"
            result["summary"] = f"OK - {current_model} ready"
        else:
            result["status"] = "error"
            result["action_needed"] = "Fix API configuration"
            result["summary"] = f"ERROR - {current_model}: {test_result.get('error', 'Connection failed')}"

        return result

    def _get_current_model(self) -> str:
        """Get current model from settings.json, fallback to default"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                return settings.get("api_parameters", {}).get("model", "gemini-2.0-flash")
        except:
            pass
        
        # Default to gemini if settings not available
        return "gemini-2.0-flash"

    def _get_api_key(self, model_name: str) -> str:
        """Get API key from multiple sources: api_config.json, .env file, environment variables"""
        
        # 1. Try api_config.json first
        try:
            if os.path.exists(self.api_config_file):
                with open(self.api_config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                api_key = config.get("api_key", "")
                if api_key and api_key != "YOUR_API_KEY_HERE":
                    return api_key
        except Exception:
            pass
        
        # 2. Try environment variables based on model type
        env_key = self._get_env_key_for_model(model_name)
        api_key = os.environ.get(env_key, "")
        if api_key and api_key != "YOUR_API_KEY_HERE":
            return api_key
            
        # 3. Try alternative environment variable names
        alt_keys = self._get_alternative_env_keys(model_name)
        for alt_key in alt_keys:
            api_key = os.environ.get(alt_key, "")
            if api_key and api_key != "YOUR_API_KEY_HERE":
                return api_key
        
        return ""

    def _get_env_key_for_model(self, model_name: str) -> str:
        """Get the environment variable key based on model name"""
        model_lower = model_name.lower()
        
        if "gemini" in model_lower:
            return "GEMINI_API_KEY"
        elif "gpt" in model_lower or "openai" in model_lower:
            return "OPENAI_API_KEY"
        elif "claude" in model_lower:
            return "CLAUDE_API_KEY"
        else:
            return "GEMINI_API_KEY"  # Default fallback

    def _get_alternative_env_keys(self, model_name: str) -> list:
        """Get alternative environment variable key names"""
        model_lower = model_name.lower()
        
        if "gemini" in model_lower:
            return ["GOOGLE_API_KEY", "GEMINI_KEY"]
        elif "gpt" in model_lower or "openai" in model_lower:
            return ["OPENAI_KEY"]
        elif "claude" in model_lower:
            return ["ANTHROPIC_API_KEY", "CLAUDE_KEY"]
        else:
            return []

    def _test_current_api(self, model_name: str, api_key: str) -> dict:
        if not APITester:
            return self._basic_validation(model_name, api_key)
        
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            if "gemini" in model_name.lower():
                result = loop.run_until_complete(APITester.test_gemini(api_key, model_name))
            elif "gpt" in model_name.lower():
                result = loop.run_until_complete(APITester.test_openai(api_key))
            elif "claude" in model_name.lower():
                result = loop.run_until_complete(APITester.test_claude(api_key))
            else:
                result = {"connected": False, "error": "Unknown model"}
            
            loop.close()
            return result
        except Exception as e:
            return {"connected": False, "error": f"Test failed: {str(e)[:50]}"}

    def _basic_validation(self, model_name: str, api_key: str) -> dict:
        if not api_key or len(api_key) < 10:
            return {"connected": False, "error": "Invalid API key format"}
        
        if "gemini" in model_name.lower() and not api_key.startswith("AIza"):
            return {"connected": False, "error": "Invalid Gemini API key"}
        elif ("gpt" in model_name.lower() or "openai" in model_name.lower()) and not api_key.startswith("sk-"):
            return {"connected": False, "error": "Invalid OpenAI API key"}
        elif "claude" in model_name.lower() and not api_key.startswith("sk-ant-"):
            return {"connected": False, "error": "Invalid Claude API key"}

        return {"connected": True, "quota": "Format validation passed"}
