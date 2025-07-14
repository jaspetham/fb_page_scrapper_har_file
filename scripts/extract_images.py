import json
import base64
import os
from pathlib import Path
import re

def extract_images(har_file_path, output_dir):
    # Create the output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Read the HAR file
    try:
        with open(har_file_path, 'r', encoding='utf-8') as f:
            har_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: HAR file not found at '{har_file_path}'")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{har_file_path}'")
        return

    # Counter for unique filenames
    image_counter = 0

    # Iterate through the entries in the HAR log
    for entry in har_data['log']['entries']:
        response = entry.get('response', {})
        content = response.get('content', {})
        mime_type = content.get('mimeType', '')
        
        # Check if the entry is an image and is base64 encoded
        if mime_type.startswith('image/') and content.get('encoding') == 'base64':
            image_counter += 1
            
            # Get the image data and decode it
            base64_text = content.get('text')
            if not base64_text:
                continue
                
            try:
                image_data = base64.b64decode(base64_text)
            except (ValueError, TypeError):
                print(f"Warning: Could not decode base64 for an image entry. Skipping.")
                continue

            # Determine the file extension
            extension = mime_type.split('/')[-1]
            if '?' in extension: # clean up cases like 'jpeg?foo=bar'
                extension = extension.split('?')[0]
            
            # Sanitize extension
            extension = re.sub(r'[^a-zA-Z0-9]', '', extension)
            if not extension:
                extension = 'jpg' # default extension

            # Create a unique filename
            filename = f"image_{image_counter}.{extension}"
            file_path = os.path.join(output_dir, filename)
            
            # Write the image data to a file
            try:
                with open(file_path, 'wb') as img_file:
                    img_file.write(image_data)
                print(f"Saved: {file_path}")
            except IOError as e:
                print(f"Error writing file {file_path}: {e}")

    print(f"\nExtraction complete. Found and saved {image_counter} images to '{output_dir}'.")

if __name__ == "__main__":
    har_file_path = 'sources/www.facebook.com.har'
    output_dir = 'assets' 
    extract_images(har_file_path, output_dir)
