import logging
from translator import Translator
from translator_claude import TranslatorClaude
from translator_gemini import TranslatorGemini


class TranslatorFactory:
    @staticmethod
    def create_translator(settings):
        """สร้าง translator ตามประเภทของ model ที่กำหนดใน settings"""
        try:
            api_params = settings.get_api_parameters()
            if not api_params:
                logging.error("No API parameters found in settings")
                raise ValueError("No API parameters found in settings")

            model = api_params.get("model")
            logging.info(f"Creating translator for model: {model}")

            if not model:
                logging.error("No model specified in API parameters")
                raise ValueError("No model specified in API parameters")

            # ตรวจสอบประเภทของ model
            model_type = TranslatorFactory.validate_model_type(model)
            if not model_type:
                logging.error(f"Unknown model type for: {model}")
                raise ValueError(f"Unknown model type for: {model}")

            logging.info(f"Validated model type: {model_type} for model: {model}")

            # สร้าง translator ตามประเภท
            if model_type == "gemini":
                logging.info(f"Creating Gemini Translator with model: {model}")
                translator = TranslatorGemini(settings)
                logging.info(
                    f"Successfully created TranslatorGemini instance: {type(translator).__name__}"
                )
                return translator

            elif model_type == "claude":
                logging.info(f"Creating Claude Translator with model: {model}")
                translator = TranslatorClaude(settings)
                logging.info(
                    f"Successfully created TranslatorClaude instance: {type(translator).__name__}"
                )
                return translator

            else:
                # ใช้ GPT translator เป็นค่าเริ่มต้น
                logging.info(f"Creating GPT Translator with model: {model}")
                translator = Translator(settings)
                logging.info(
                    f"Successfully created Translator instance: {type(translator).__name__}"
                )
                return translator

        except Exception as e:
            logging.error(f"Error creating translator: {str(e)}")
            # ถ้าเกิดข้อผิดพลาด ให้ให้รู้ว่าเกิดปัญหา
            raise ValueError(f"Failed to create translator: {str(e)}")

    @staticmethod
    def validate_model_type(model):
        """ตรวจสอบประเภทของ model โดยวิเคราะห์จากชื่อ"""
        model = model.lower()  # แปลงเป็นตัวพิมพ์เล็กเพื่อการเปรียบเทียบที่แม่นยำ

        # ตรวจสอบโดยใช้คำสำคัญในชื่อ
        if "gemini" in model:
            logging.info(f"Model '{model}' identified as Gemini type")
            return "gemini"
        elif "claude" in model:
            logging.info(f"Model '{model}' identified as Claude type")
            return "claude"
        elif "gpt" in model or model.startswith("text-") or model.startswith("ft:"):
            logging.info(f"Model '{model}' identified as GPT (OpenAI) type")
            return "gpt"
        else:
            # กรณีไม่ทราบประเภท ให้แจ้งเตือนและกำหนดเป็น GPT (ค่าเริ่มต้น)
            logging.warning(f"Unknown model type: '{model}', defaulting to GPT type")
            return "gpt"
