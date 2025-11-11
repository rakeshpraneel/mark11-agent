import os
from app.core.settings import settings

def initiate():

    try:
        GOOGLE_API_KEY = settings.GOOGLE_API_KEY
        os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
        print("✅ Gemini API key setup complete.")
    except Exception as e:
        print(
            f"🔑 Authentication Error: Please make sure you have added 'GOOGLE_API_KEY' to your Kaggle secrets. Details: {e}"
        )       