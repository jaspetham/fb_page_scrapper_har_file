import os
import google.generativeai as genai
from dotenv import load_dotenv

# --- Configuration ---
# Load environment variables from .env file
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# --- Main Script ---
if not API_KEY:
    print("Error: GEMINI_API_KEY not found in your .env file.")
    print("Please ensure you have a .env file with GEMINI_API_KEY=YOUR_KEY_HERE")
else:
    try:
        # Configure the generative AI library with your API key
        genai.configure(api_key=API_KEY)

        print("Attempting to list available Gemini models...")
        models_found = False
        for m in genai.list_models():
            # Only list models that support the 'generateContent' method
            if 'generateContent' in m.supported_generation_methods:
                print(f"- Found model: {m.name}")
                models_found = True

        if not models_found:
            print("\nNo models found that support 'generateContent'.")
            print("Possible reasons:")
            print("  1. Your API key might be incorrect or lack necessary permissions.")
            print("  2. Network issues (firewall, proxy, SSL interception) are preventing connection.")
            print("  3. The Generative Language API might not be enabled in your Google Cloud Project.")

    except Exception as e:
        print(f"\nAn error occurred while trying to list models: {e}")
        print("This often indicates a problem connecting to the Gemini API servers.")