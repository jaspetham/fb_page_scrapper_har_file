import os
import google.generativeai as genai
from dotenv import load_dotenv
import sys

# --- Path Setup ---
# Get the absolute path of the script's directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Get the absolute path of the project's root directory (assuming the script is in a 'scripts' folder)
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

def get_file_contents(directory):
    """Reads all files in a directory and returns their content as a dictionary."""
    file_contents = {}
    # Ensure the directory path is absolute
    abs_directory = os.path.join(PROJECT_ROOT, directory)
    if not os.path.isdir(abs_directory):
        print(f"Warning: Directory not found: {abs_directory}")
        return file_contents

    for root, _, files in os.walk(abs_directory):
        for file in files:
            path = os.path.join(root, file)
            # Create a relative path to use as a key
            relative_path = os.path.relpath(path, PROJECT_ROOT)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    file_contents[relative_path] = f.read()
            except (UnicodeDecodeError, IOError):
                # For binary files or files that can't be read, just note their path.
                file_contents[relative_path] = f"Binary file (not read): {os.path.basename(path)}"
    return file_contents

def generate_company_profile():
    """
    Generates a detailed company profile using Gemini AI based on project files.
    """
    print("Loading environment variables from .env file...")
    # Load .env from the project root
    dotenv_path = os.path.join(PROJECT_ROOT, '.env')
    load_dotenv(dotenv_path=dotenv_path)

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found in .env file.")
        print(f"Please ensure a .env file exists at '{PROJECT_ROOT}/.env' with your Gemini API key.")
        print("Example: GEMINI_API_KEY=your_api_key_here")
        sys.exit(1)

    print("Configuring Gemini AI...")
    genai.configure(api_key=api_key)

    selected_model_name = ""
    try:
        # List available models that support generateContent
        print("\nFetching available Gemini models...")
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)

        if not available_models:
            print("No models found that support 'generateContent'. Please check your API key and permissions.")
            sys.exit(1)

        print("Available models for content generation:")
        for i, model_name in enumerate(available_models):
            print(f"{i + 1}. {model_name}")

        while True:
            try:
                # Try to get model from env, if not, ask user
                env_model = os.getenv("GEMINI_MODEL")
                if env_model and env_model in available_models:
                    print(f"\nUsing GEMINI_MODEL from .env: {env_model}")
                    selected_model_name = env_model
                    break
                else:
                    if env_model:
                        print(f"Warning: Model '{env_model}' from .env not found or does not support 'generateContent'.")

                    choice = input(f"\nEnter the number of the model you want to use (1-{len(available_models)}): ")
                    choice_index = int(choice) - 1
                    if 0 <= choice_index < len(available_models):
                        selected_model_name = available_models[choice_index]
                        break
                    else:
                        print("Invalid choice. Please enter a number within the given range.")
            except ValueError:
                print("Invalid input. Please enter a number.")

        print(f"\nUsing Gemini model: {selected_model_name}")
        model = genai.GenerativeModel(selected_model_name)

    except AttributeError:
        print("\n---")
        print("Error: The 'google.generativeai' library seems to have an issue (AttributeError).")
        print("This often means your library version is outdated or there's a conflict.")
        print("Please run 'pip install --upgrade google-generativeai' and check for any 'google.py' files in your project.")
        print("---\n")
        sys.exit(1)
    except Exception as e: # Catch other potential errors during model initialization or listing
        print(f"Error initializing or listing Gemini models: {e}")
        sys.exit(1)


    print("Reading files from 'assets' and 'out' directories...")
    assets_contents = get_file_contents('assets')
    out_contents = get_file_contents('out')

    # Construct the prompt
    prompt_parts = [
        "You are an expert business consultant and web developer. Your task is to generate a detailed company profile in XML format. This profile will serve as the foundation for building a new website for the company.",
        "Analyze the provided data, which includes social media history, company introduction, and a list of asset files (images). From this data, create a comprehensive company profile.",
        "The XML output should be well-structured and include the following sections:",
        "1. **CompanyDetails**: Basic information like name, tenure, mission, contact info.",
        "2. **BrandIdentity**: Core branding elements, including brand names used and brand voice.",
        "3. **ProductsAndServices**: Detailed breakdown of products, services, features, and categories.",
        "4. **TargetAudience**: Description of the ideal customers.",
        "5. **MarketPositioning**: Analysis of the company's position in the market, its strengths, and unique selling propositions.",
        "6. **WebsiteFoundation**: Strategic recommendations for the website, including key sections, features, and calls-to-action.",
        "7. **ProfileValuation**: An evaluation of the generated profile's completeness and utility for website development.",
        "\nHere is the data:\n"
    ]

    for path, content in out_contents.items():
        prompt_parts.append(f"--- Content from {path} ---\n{content}\n")

    prompt_parts.append("--- Asset Files (Mainly Images) ---\n")
    for path in assets_contents.keys():
        prompt_parts.append(f"- {path}\n")

    prompt = "\n".join(prompt_parts)

    print("Generating company profile with Gemini AI. This may take a moment...")
    try:
        response = model.generate_content(prompt)
        generated_xml = response.text
    except Exception as e:
        print(f"An error occurred while communicating with the Gemini API: {e}")
        sys.exit(1)


    # Clean up the response from markdown code blocks if present
    if '```xml' in generated_xml:
        generated_xml = generated_xml.split('```xml\n')[1].split('```')[0]
    elif '```' in generated_xml:
         generated_xml = generated_xml.split('```\n')[1].split('```')[0]


    output_path = os.path.join(PROJECT_ROOT, "out/company_profile.xml")
    print(f"Saving generated profile to {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(generated_xml)

    print(f"Company profile XML generated successfully at: {output_path}")

if __name__ == "__main__":
    try:
        import dotenv
        import google.generativeai
    except ImportError:
        print("One or more required packages are not installed.")
        print("Please run: pip install python-dotenv google-generativeai")
        sys.exit(1)

    generate_company_profile()