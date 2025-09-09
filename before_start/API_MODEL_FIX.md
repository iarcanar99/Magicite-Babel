# 🔧 API Model Fix - แก้ไขปัญหา API Checker

## 🐛 ปัญหาที่พบ
แม้ว่า API key จะถูกต้อง แต่ Before Start UI แสดง:
```
❌ Error: gemini-2.0-flash: ✗ 404 models/gemini-pro is not found for API version
```

## 🔍 สาเหตุ
API tester ใช้ hardcode model name เป็น `"gemini-pro"` แทนที่จะใช้ model name จาก settings.json ที่เป็น `"gemini-2.0-flash"`

## ✅ วิธีแก้ไข

### 1. แก้ไข `api_tester.py`:
```python
# เก่า (ผิด):
async def test_gemini(api_key: str) -> dict:
    model = genai.GenerativeModel("gemini-pro")  # hardcode ผิด

# ใหม่ (ถูก):
async def test_gemini(api_key: str, model_name: str = "gemini-pro") -> dict:
    model = genai.GenerativeModel(model_name)  # ใช้ parameter
```

### 2. แก้ไข `api_checker.py`:
```python
# ส่ง model name ไปยัง tester
if "gemini" in model_name.lower():
    result = loop.run_until_complete(APITester.test_gemini(api_key, model_name))
```

## 🎯 ผลลัพธ์
ตอนนี้ API checker จะใช้ model name ที่ถูกต้องจาก settings.json:
- ✅ `gemini-2.0-flash` → ใช้ gemini-2.0-flash
- ✅ `gemini-1.5-pro` → ใช้ gemini-1.5-pro
- ✅ `gpt-4o` → ใช้ gpt-4o

## 🧪 การทดสอบ
```bash
cd Before_start
python -c "from checkers import APIChecker; checker = APIChecker(); result = checker.check_all(); print('Status:', result['status'])"
```

**ผลลัพธ์ที่คาดหวัง:**
```
Status: ready
Summary: OK - gemini-2.0-flash ready
```

## ✨ สถานะ: แก้ไขแล้ว ✅

ระบบ Before Start ตอนนี้ตรวจสอบ API ได้อย่างถูกต้องแล้ว!
