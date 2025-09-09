# api_tester.py - ทดสอบ API แบบ real connection

import asyncio
import time
import sys
import os

# เพิ่ม parent directory เพื่อ import จาก MBB project
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import google.generativeai as genai
except ImportError:
    genai = None

try:
    import openai
except ImportError:
    openai = None

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None


class APITester:
    """ทดสอบ API แต่ละตัวด้วยการเชื่อมต่อจริง"""

    @staticmethod
    async def test_gemini(api_key: str, model_name: str = "gemini-pro") -> dict:
        """ทดสอบ Gemini API"""
        if not genai:
            return {"connected": False, "error": "google-generativeai library not installed"}
        
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_name)

            start_time = time.time()
            response = await asyncio.to_thread(
                model.generate_content,
                "Say 'OK' if you can read this",
                generation_config={"temperature": 0.1, "max_output_tokens": 10}
            )
            response_time = int((time.time() - start_time) * 1000)

            if response.text and 'OK' in response.text:
                return {
                    "connected": True,
                    "response_time": f"{response_time}ms",
                    "quota": "Available"
                }
            else:
                return {"connected": False, "error": "Invalid response"}

        except Exception as e:
            error_msg = str(e)
            if "API_KEY_INVALID" in error_msg or "invalid" in error_msg.lower():
                return {"connected": False, "error": "Invalid API key"}
            elif "QUOTA_EXCEEDED" in error_msg or "quota" in error_msg.lower():
                return {"connected": False, "error": "Quota exceeded"}
            elif "404" in error_msg or "not found" in error_msg.lower():
                return {"connected": False, "error": f"Model {model_name} not found"}
            else:
                return {"connected": False, "error": error_msg[:50]}

    @staticmethod
    async def test_openai(api_key: str) -> dict:
        """ทดสอบ OpenAI API"""
        try:
            openai.api_key = api_key

            start_time = time.time()
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Say OK"}],
                max_tokens=5,
                temperature=0,
            )

            response_time = int((time.time() - start_time) * 1000)

            if response.choices[0].message.content:
                return {
                    "connected": True,
                    "response_time": f"{response_time}ms",
                    "quota": "Available",
                }

        except Exception as e:
            error_msg = str(e)
            if "Incorrect API key" in error_msg:
                return {"connected": False, "error": "Invalid API key"}
            elif "Rate limit" in error_msg:
                return {"connected": False, "error": "Rate limit exceeded"}
            else:
                return {"connected": False, "error": error_msg[:50]}

    @staticmethod
    async def test_claude(api_key: str) -> dict:
        """ทดสอบ Claude API"""
        try:
            client = Anthropic(api_key=api_key)

            start_time = time.time()
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=10,
                messages=[{"role": "user", "content": "Say OK"}],
            )

            response_time = int((time.time() - start_time) * 1000)

            if response.content:
                return {
                    "connected": True,
                    "response_time": f"{response_time}ms",
                    "quota": "Available",
                }

        except Exception as e:
            error_msg = str(e)
            if "authentication" in error_msg.lower():
                return {"connected": False, "error": "Invalid API key"}
            else:
                return {"connected": False, "error": error_msg[:50]}


# Integration with before_start_ui.py
def integrate_real_api_testing():
    """
    แก้ไขใน before_start_ui.py - APIChecker class
    """

    # Replace _test_gemini method
    async def _test_gemini_real(self, api_key: str) -> dict:
        """ทดสอบ Gemini API แบบ real connection"""
        tester = APITester()
        return await tester.test_gemini(api_key)

    # Replace _test_openai method
    async def _test_openai_real(self, api_key: str) -> dict:
        """ทดสอบ OpenAI API แบบ real connection"""
        tester = APITester()
        return await tester.test_openai(api_key)

    # Replace _test_claude method
    async def _test_claude_real(self, api_key: str) -> dict:
        """ทดสอบ Claude API แบบ real connection"""
        tester = APITester()
        return await tester.test_claude(api_key)

    @staticmethod
    async def test_openai(api_key: str) -> dict:
        """ทดสอบ OpenAI API"""
        if not openai:
            return {"connected": False, "error": "openai library not installed"}
        
        try:
            client = openai.OpenAI(api_key=api_key)
            
            start_time = time.time()
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Say OK"}],
                max_tokens=5,
                temperature=0
            )
            response_time = int((time.time() - start_time) * 1000)

            if response.choices[0].message.content:
                return {
                    "connected": True,
                    "response_time": f"{response_time}ms",
                    "quota": "Available"
                }

        except Exception as e:
            error_msg = str(e)
            if "Incorrect API key" in error_msg or "authentication" in error_msg.lower():
                return {"connected": False, "error": "Invalid API key"}
            elif "Rate limit" in error_msg or "quota" in error_msg.lower():
                return {"connected": False, "error": "Rate limit exceeded"}
            else:
                return {"connected": False, "error": error_msg[:50]}

    @staticmethod
    async def test_claude(api_key: str) -> dict:
        """ทดสอบ Claude API"""
        if not Anthropic:
            return {"connected": False, "error": "anthropic library not installed"}
        
        try:
            client = Anthropic(api_key=api_key)

            start_time = time.time()
            response = await asyncio.to_thread(
                client.messages.create,
                model="claude-3-haiku-20240307",
                max_tokens=10,
                messages=[{"role": "user", "content": "Say OK"}]
            )
            response_time = int((time.time() - start_time) * 1000)

            if response.content:
                return {
                    "connected": True,
                    "response_time": f"{response_time}ms",
                    "quota": "Available"
                }

        except Exception as e:
            error_msg = str(e)
            if "authentication" in error_msg.lower() or "api_key" in error_msg.lower():
                return {"connected": False, "error": "Invalid API key"}
            else:
                return {"connected": False, "error": error_msg[:50]}


# Test script
async def main():
    tester = APITester()
    
    # Test with sample keys (will fail but show structure)
    print("Testing Gemini...")
    result = await tester.test_gemini("test_key")
    print(f"Result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
