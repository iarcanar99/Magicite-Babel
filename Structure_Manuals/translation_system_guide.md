# 🔄 Translation System Guide

**ไฟล์หลัก:** `translator_factory.py`, `translator_gemini.py`, `translator_claude.py`, `translator.py`  
**คลาสหลัก:** `TranslatorFactory`, `TranslatorGemini`, `TranslatorClaude`, `Translator`  

## 🎯 Overview
Translation System เป็นระบบแปลภาษาหลักของ MBB ที่รองรับ AI models หลายตัว (Gemini, Claude, OpenAI GPT) พร้อมระบบ caching, text correction, และ NPC context awareness

## 🏗️ Architecture

### 📋 Core Components

#### 1. `TranslatorFactory` (Factory Pattern)
```python
class TranslatorFactory:
    @staticmethod
    def create_translator(settings):
        # สร้าง translator ตามประเภท model ใน settings
        # ปัจจุบันรองรับเฉพาะ Gemini models
        
    @staticmethod  
    def validate_model_type(model):
        # ตรวจสอบประเภท model
        # รองรับ: "gemini" models เท่านั้น
```

#### 2. `TranslatorGemini` (Primary Translator)
```python
class TranslatorGemini:
    def __init__(self, settings=None):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = genai.GenerativeModel(...)
        self.cache = DialogueCache()
        self.text_corrector = TextCorrector()
        self.character_names_cache = set()
```

#### 3. `TranslatorClaude` (Claude Support)
```python
class TranslatorClaude:
    def __init__(self, settings=None):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.client = anthropic.Anthropic(...)
        self.enhanced_detector = EnhancedNameDetector()
```

#### 4. `Translator` (OpenAI GPT Support)
```python
class Translator:
    def __init__(self, settings=None):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(...)
        self.cache = DialogueCache()
```

## 🤖 Supported AI Models

### 🔥 Gemini Models (Primary)
```python
SUPPORTED_MODELS = {
    "gemini-2.0-flash-lite": "Fast, lightweight model",
    "gemini-2.0-flash": "Balanced performance and quality", 
    "gemini-2.5-flash": "Latest model with enhanced capabilities"
}

# Configuration
generation_config = {
    "max_output_tokens": 500,
    "temperature": 0.7,
    "top_p": 0.9
}

# Safety Settings (ปิดการกรองทั้งหมด)
safety_settings = [
    {"category": HarmCategory.HARM_CATEGORY_HARASSMENT, "threshold": HarmBlockThreshold.BLOCK_NONE},
    {"category": HarmCategory.HARM_CATEGORY_HATE_SPEECH, "threshold": HarmBlockThreshold.BLOCK_NONE},
    # ... และอื่นๆ
]
```

### 🧠 Claude Models (Alternative)
```python
SUPPORTED_MODELS = {
    "claude-3-5-haiku-20241022": "Fast and efficient",
    "claude-3-5-sonnet": "Balanced model",
    "claude-3-opus": "Most capable model"
}
```

### 🤖 OpenAI GPT Models (Legacy)
```python
SUPPORTED_MODELS = {
    "gpt-4o": "Latest GPT-4 optimized",
    "gpt-4": "Standard GPT-4",
    "gpt-3.5-turbo": "Fast and cost-effective"
}
```

## 🎮 Language Support

### 🔄 Translation Pairs
```python
# Primary Support
English → Thai    # translator_gemini.py
Japanese → Thai   # translator_gemini_JP.py

# Language Detection
source_languages = ["en", "ja", "auto"]
target_language = "th"  # Fixed to Thai

# OCR Languages
ocr_languages = ["en", "ja"]  # English and Japanese text recognition
```

### 🎯 Language-Specific Features
```python
# Japanese Translation (translator_gemini_JP.py)
- Hiragana/Katakana support: "\u3040-\u309f", "\u30a0-\u30ff" 
- Kanji support: "\u4e00-\u9faf"
- Full-width characters: "\uff00-\uffef"

# English Translation (translator_gemini.py)
- Standard ASCII support
- Special character handling
- Context-aware translation
```

## 🎭 Character Context System

### 👥 NPC Data Loading  
```python
def load_npc_data(self):
    # โหลดจาก NPC.json
    self.character_data = npc_data["main_characters"]
    self.context_data = npc_data["lore"] 
    self.character_styles = npc_data["character_roles"]
    self.word_fixes = npc_data["word_fixes"]  # คำที่แก้ไขแล้ว
```

### 🎨 Character-Aware Translation
```python
def detect_character_name(self, text):
    # ตรวจสอบชื่อตัวละครในข้อความ
    # ใช้ EnhancedNameDetector (ถ้ามี)
    # คืนค่า character info และ context

def apply_character_style(self, character_name, translated_text):
    # ปรับสไตล์การแปลตามตัวละคร
    # ใช้ข้อมูลจาก character_roles
    # รักษาบุคลิกของตัวละคร
```

### 📝 Dialogue Type Detection
```python
from text_corrector import TextCorrector, DialogueType

# Dialogue Types
DialogueType.NORMAL      # บทสนทนาปกติ
DialogueType.CHOICE      # ตัวเลือกสนทนา  
DialogueType.SYSTEM      # ข้อความระบบ
DialogueType.NARRATIVE   # บรรยาย

# Processing
speaker, content, dialogue_type = text_corrector.split_speaker_and_content(text)
```

## 💾 Caching System

### 🔄 Dialogue Cache
```python
from dialogue_cache import DialogueCache

class DialogueCache:
    def __init__(self):
        self.cache = {}           # Translation cache
        self.max_cache_size = 100 # Maximum entries
        self.cache_timeout = 300  # 5 minutes timeout
        
    def get_cached_translation(self, text, character_name=None):
        # ดึง translation ที่แคชไว้
        
    def cache_translation(self, original, translated, character_name=None):
        # บันทึก translation ลงแคช
```

### ⚡ Performance Benefits
- **Reduce API Calls:** หลีกเลี่ยงการแปลข้อความซ้ำ
- **Faster Response:** ตอบสนองเร็วขึ้นสำหรับข้อความที่เคยแปล
- **Cost Optimization:** ลดค่าใช้จ่าย API calls

## 🔧 Text Processing Pipeline

### 1. **Pre-Processing**
```python
def preprocess_text(self, text):
    # ลบอักขระพิเศษที่ไม่ต้องการ
    # แปลง encoding ให้ถูกต้อง
    # ตรวจสอบ word_fixes
    # Handle special cases (???, 2, 22, 222)
```

### 2. **Character Detection**
```python
def detect_speaker_and_content(self, text):
    # แยกชื่อผู้พูดออกจากเนื้อหา
    # ระบุประเภทของ dialogue
    # ดึงข้อมูล context ของตัวละคร
```

### 3. **Translation**
```python
def translate(self, text, source_lang="auto", target_lang="th"):
    # เรียก AI API สำหรับแปล
    # ใช้ context ของตัวละคร
    # ปรับสไตล์ตามบุคลิก
```

### 4. **Post-Processing**
```python
def postprocess_translation(self, translated_text, character_name=None):
    # แก้ไขคำผิดที่ทราบ (word_fixes)
    # ปรับแต่งสไตล์ตามตัวละคร
    # ตรวจสอบคุณภาพการแปล
```

## 🎯 Translation Methods

### 🔄 Standard Translation
```python
def translate(self, text, source_lang="English", target_lang="Thai", is_choice_option=False):
    """
    แปลข้อความพร้อมจัดการบริบทของตัวละคร
    
    Args:
        text: ข้อความที่ต้องการแปล
        source_lang: ภาษาต้นฉบับ
        target_lang: ภาษาเป้าหมาย  
        is_choice_option: เป็นข้อความตัวเลือกหรือไม่
        
    Returns:
        str: ข้อความที่แปลแล้ว
    """
```

### 🎲 Choice Translation
```python
def translate_choice(self, text):
    """แปลข้อความตัวเลือกแบบพิเศษ"""
    # ใช้ FFXIV context จาก NPC.json
    # น้ำเสียงตัวเอก (Warrior of Light): กล้าหาญ หนักแน่น มั่นใจ
    # อารมณ์หลากหลาย: เอาจริง, ขำขัน, ประชดประชัน
    # รักษาความหมายที่แม่นยำพร้อมบุคลิกตัวเอก
```

### 📦 Batch Translation
```python
def batch_translate(self, texts, batch_size=10):
    """แปลข้อความหลายข้อความพร้อมกัน"""
    # ประหยัด API calls
    # ประมวลผลแบบ batch
    # รักษา context ระหว่างข้อความ
```

## 📊 Quality Control

### ✅ Translation Quality Check
```python
def analyze_translation_quality(self, original_text, translated_text):
    """วิเคราะห์คุณภาพการแปล"""
    # ตรวจสอบความสมบูรณ์
    # วิเคราะห์ความเหมาะสม
    # ให้คะแนนคุณภาพ
    
def is_translation_complete(self, original_text, translated_text):
    """ตรวจสอบว่าการแปลสมบูรณ์หรือไม่"""
    # เปรียบเทียบความยาว
    # ตรวจสอบเนื้อหาสำคัญ
```

### 🔄 Force Retry System
```python
def force_retranslate_with_quality_check(self, text, max_retries=3):
    """แปลซ้ำพร้อมตรวจสอบคุณภาพ"""
    # ลองแปลใหม่หากคุณภาพไม่ดี
    # จำกัดจำนวนครั้งการลองใหม่
    # Log การทำงานเพื่อ debugging
```

## 🔌 API Integration

### 🔑 API Key Management
```python
# Environment Variables (.env file)
GEMINI_API_KEY=your_gemini_api_key_here
ANTHROPIC_API_KEY=your_claude_api_key_here  
OPENAI_API_KEY=your_openai_api_key_here

# Error Handling
if not self.api_key:
    error_msg = "API_KEY not found in .env file"
    messagebox.showerror("API Key Error", error_msg)
    raise ValueError(error_msg)
```

### ⚙️ Model Configuration
```python
# From Settings
api_params = settings.get_api_parameters()
self.model_name = api_params.get("model", "gemini-2.0-flash")
self.max_tokens = api_params.get("max_tokens", 500)
self.temperature = api_params.get("temperature", 0.7)
self.top_p = api_params.get("top_p", 0.9)
```

## 🚀 Performance Features

### ⚡ Optimization Strategies
```python
# Smart Caching
- Translation cache with timeout
- Character context cache
- Search result cache

# Request Optimization  
- Batch processing for multiple texts
- Request debouncing for real-time translation
- Connection pooling for API calls

# Memory Management
- Limited cache size
- Automatic cache cleanup
- Efficient data structures
```

### 🧵 Threading Considerations
- API calls ใน background threads
- UI updates ใน main thread เท่านั้น
- Thread-safe caching mechanisms
- Proper error handling across threads

## 🐛 Error Handling

### ✅ Robust Error Management
```python
try:
    response = self.model.generate_content(prompt)
    translated_text = response.text
except Exception as e:
    logging.error(f"Translation API error: {e}")
    # Fallback strategies:
    # 1. Try different model
    # 2. Use cached translation
    # 3. Return error message
    return f"Translation Error: {str(e)}"
```

### 🔍 Error Categories
```python
# API Errors
- Rate limiting (429)
- Authentication errors (401)
- Service unavailable (503)
- Network timeouts

# Content Errors  
- Content filtering blocks
- Text too long
- Invalid characters
- Empty responses

# System Errors
- File not found (NPC.json)
- JSON decode errors
- Memory issues
- Threading errors
```

## 📝 Usage Examples

### 🚀 Basic Translation
```python
# Initialize translator
translator_factory = TranslatorFactory()
translator = translator_factory.create_translator(settings)

# Simple translation
result = translator.translate("Hello, how are you?")
print(result)  # สวัสดี คุณเป็นอย่างไรบ้าง?

# Character-aware translation
result = translator.translate("Alphinaud: We must proceed carefully.", source_lang="English")
print(result)  # อัลฟิโน: เราต้องดำเนินการอย่างระมัดระวัง
```

### 🎯 Advanced Usage
```python
# Batch translation
texts = ["Hello", "Goodbye", "Thank you"]
results = translator.batch_translate(texts)

# Choice translation with Warrior of Light voice
choice_text = "What will you say?\nWe won't let you lay a finger on the reflections!\nYou're aware of the connection between the worlds?"
result = translator.translate_choice(choice_text)
# Result: "คุณจะพูดว่าอย่างไร?\nเราจะไม่ยอมให้คุณแตะต้องโลกสะท้อนเด็ดขาด!\nคุณทราบถึงความเชื่อมโยงระหว่างโลกต่างๆ ใช่ไหม?"

# Quality check
quality_score = translator.analyze_translation_quality(original, translated)
if quality_score < 0.7:
    # Retry translation
    better_result = translator.force_retranslate_with_quality_check(original)
```

## 🔧 Customization

### 🎨 Custom Prompts
```python
# แก้ไข translation prompts ใน translator files
TRANSLATION_PROMPT = """
แปลข้อความต่อไปนี้จาก{source_lang}เป็น{target_lang}
โดยคำนึงถึงบริบทของเกมและตัวละคร

ข้อความ: {text}
ตัวละคร: {character_name}
บริบท: {character_context}

แปล:
"""
```

### ⚙️ Custom Models
```python
# เพิ่ม model ใหม่ใน TranslatorFactory
def validate_model_type(model):
    if "custom-model" in model:
        return "custom"
    # ... existing logic
    
# สร้าง custom translator class
class CustomTranslator:
    def __init__(self, settings):
        # Custom implementation
        pass
```

---

## 🛠️ Recent Updates & Fixes

### 🎲 Choice Translation Context Fix (04/08/2025)
**Problem:** translate_choice() method ไม่ใช้บริบทจาก NPC.json ทำให้แปล "reflections" เป็น "เงาสะท้อน" แทนที่จะเป็น "โลกสะท้อน"

**Solution Implemented:**
1. **FFXIV Context Integration:** เพิ่ม self.context_data เข้าไปในโพรมต์ของ translate_choice()
2. **Warrior of Light Voice:** เพิ่มน้ำเสียงตัวเอกที่กล้าหาญ หนักแน่น มั่นใจ
3. **Emotional Range:** รองรับอารมณ์หลากหลาย (เอาจริง, ขำขัน, ประชดประชัน)

**Impact:** 
- "reflections" → "โลกสะท้อน" ✅
- Choice translations มีน้ำเสียงตัวเอกที่ชัดเจน ✅
- ใช้บริบท FFXIV อย่างถูกต้อง ✅

---

## 🔗 Related Files
- [`text_corrector.py`](text_corrector.py) - Text preprocessing และ correction
- [`dialogue_cache.py`](dialogue_cache.py) - Translation caching system  
- [`enhanced_name_detector.py`](enhanced_name_detector.py) - Advanced character detection
- [`npc_file_utils.py`](npc_file_utils.py) - NPC data utilities
- [`NPC.json`](NPC.json) - Character และ context data

## 📚 See Also
- [Settings System Guide](settings_system_guide.md)
- [Text Corrector Guide](text_corrector_guide.md)
- [NPC Manager Guide](npc_manager_guide.md)
- [Dialogue Cache Guide](dialogue_cache_guide.md)