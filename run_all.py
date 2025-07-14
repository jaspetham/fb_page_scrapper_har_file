import os
import sys
import json # Ensure json is imported

# Add the 'scripts' directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

from extract_images import extract_images
from extract_messages_regex import extract_message_text_from_har
from organize_assets import organize_and_copy_assets
from generate_company_profile import generate_company_profile

def run_all_scripts():
    print("--- Running all data processing scripts ---")

    # Define paths relative to the root directory
    har_file = "sources/www.facebook.com.har"
    assets_dir = "assets"
    history_json_file = "out/history.json"

    # 1. Extract Images
    print("\n--- Step 1: Extracting images ---")
    extract_images(har_file, assets_dir)

    # 2. Extract Messages and Clean Text Content
    print("\n--- Step 2: Extracting messages and cleaning text content ---")
    extracted_texts_list = extract_message_text_from_har(har_file) # Renamed for clarity

    if extracted_texts_list:
        try:
            with open(history_json_file, 'w', encoding='utf-8') as outfile:
                # Write the entire list of strings as a single JSON array
                json.dump(extracted_texts_list, outfile, ensure_ascii=False, indent=4) # Added indent for readability
            print(f"Extracted message texts (as JSON array) saved to {history_json_file}")
            print(f"Note: Newline characters and non-standard symbols are removed from text content during extraction.")

        except IOError as e:
            print(f"Error writing to output file {history_json_file}: {e}", file=sys.stderr)
    else:
        print(f"No relevant 'text' messages found in {har_file}", file=sys.stderr)



    # 3. Organize Assets (remove duplicates, keep highest quality)
    print("\n--- Step 3: Organizing assets ---")
    organize_and_copy_assets(assets_dir)

    # 4. Generate Company Profile XML
    print("\n--- Step 4: Generating company profile XML ---")
    generate_company_profile()


    print("\n--- All scripts finished ---")

if __name__ == "__main__":
    run_all_scripts()
