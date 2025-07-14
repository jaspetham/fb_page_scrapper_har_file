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
    project_root = os.path.dirname(os.path.abspath(__file__)) # Get the directory of the current script

    har_file_path = os.path.join(project_root, "sources", "www.facebook.com.har")
    assets_dir_path = os.path.join(project_root, "assets")
    output_dir_path = os.path.join(project_root, "out")
    history_json_file_path = os.path.join(output_dir_path, "history.json")

    # --- File Validation ---
    print("\n--- Validating required files and directories ---")

    # 1. Validate HAR file existence
    if not os.path.exists(har_file_path):
        print(f"Error: Required file not found: {har_file_path}", file=sys.stderr)
        print("Please ensure 'www.facebook.com.har' is placed in the 'sources' directory.", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"Validated: HAR file found at {har_file_path}")

    # 2. Validate assets directory existence (and create if not exists, as it's an output target for extract_images)
    if not os.path.exists(assets_dir_path):
        print(f"Warning: Assets directory '{assets_dir_path}' not found. Creating it now.", file=sys.stderr)
        try:
            os.makedirs(assets_dir_path)
        except OSError as e:
            print(f"Error creating assets directory {assets_dir_path}: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"Validated: Assets directory found at {assets_dir_path}")

    # 3. Validate output directory existence (and create if not exists, as it's an output target for history.json and company_profile.xml)
    if not os.path.exists(output_dir_path):
        print(f"Warning: Output directory '{output_dir_path}' not found. Creating it now.", file=sys.stderr)
        try:
            os.makedirs(output_dir_path)
        except OSError as e:
            print(f"Error creating output directory {output_dir_path}: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"Validated: Output directory found at {output_dir_path}")

    print("--- File validation complete ---")

    # 1. Extract Images
    print("\n--- Step 1: Extracting images ---")
    extract_images(har_file_path, assets_dir_path)

    # 2. Extract Messages and Clean Text Content
    print("\n--- Step 2: Extracting messages and cleaning text content ---")
    extracted_texts_list = extract_message_text_from_har(har_file_path) # Renamed for clarity

    if extracted_texts_list:
        try:
            with open(history_json_file_path, 'w', encoding='utf-8') as outfile:
                # Write the entire list of strings as a single JSON array
                json.dump(extracted_texts_list, outfile, ensure_ascii=False, indent=4) # Added indent for readability
            print(f"Extracted message texts (as JSON array) saved to {history_json_file_path}")
            print(f"Note: Newline characters and non-standard symbols are removed from text content during extraction.")

        except IOError as e:
            print(f"Error writing to output file {history_json_file_path}: {e}", file=sys.stderr)
    else:
        print(f"No relevant 'text' messages found in {har_file_path}", file=sys.stderr)

    # 3. Organize Assets (remove duplicates, keep highest quality)
    print("\n--- Step 3: Organizing assets ---")
    organize_and_copy_assets(assets_dir_path)

    # 4. Generate Company Profile XML
    print("\n--- Step 4: Generating company profile XML ---")
    generate_company_profile()

    print("\n--- All scripts finished ---")

if __name__ == "__main__":
    run_all_scripts()