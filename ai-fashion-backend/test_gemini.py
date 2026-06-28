import google.generativeai as genai
from config import settings

genai.configure(api_key=settings.gemini_api_key)

print("Available models:")
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"  - {model.name}")