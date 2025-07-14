import json
import sys
import re
import base64
from datetime import datetime

def extract_message_text_from_har(file_path):
    extracted_texts = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            har_data = json.load(f)

        if 'log' in har_data and 'entries' in har_data['log']:
            for entry in har_data['log']['entries']:
                try:
                    if 'response' in entry and 'content' in entry['response']:
                        content = entry['response']['content']
                        content_text = content.get('text')
                        content_encoding = content.get('encoding')

                        if content_text:
                            if content_encoding == 'base64':
                                try:
                                    decoded_text = base64.b64decode(content_text).decode('utf-8', errors='ignore')
                                    content_text = decoded_text
                                except Exception as e:
                                    continue # Skip this entry if decoding fails

                            # Try to parse content_text as JSON first
                            try:
                                json_content = json.loads(content_text)
                                # The original logic for finding messages in JSON was a placeholder.
                                # To properly extract 'message.text' from a parsed JSON object,
                                # you'd need to recursively traverse the JSON structure.
                                # For simplicity, if the whole content is JSON, and you're looking
                                # for "message":{"text":"..."} specifically, you might need to
                                # adjust this part or rely more on the regex for non-JSON content.
                                # For now, I'll assume the regex part is what you want to primarily
                                # apply for message extraction, even if the overall content is JSON.
                                pass

                            except json.JSONDecodeError:
                                # This block will be executed if content_text is not a complete JSON,
                                # or if you prefer to use regex even on JSON strings for "message":{"text":"..."}
                                message_text_pattern = r'"message":{"text":"((?:[^"\\]|\\"|\\\\|\\/|\\b|\\f|\\n|\\r|\\t|\\u[0-9a-fA-F]{4})*?)"}'
                                message_matches = list(re.finditer(message_text_pattern, content_text))

                                for msg_match in message_matches:
                                    unescaped_text = ""
                                    try:
                                        json_string_to_load = f'"{msg_match.group(1)}"'
                                        unescaped_text = json.loads(json_string_to_load)
                                    except json.JSONDecodeError:
                                        unescaped_text = msg_match.group(1)

                                    # Remove newline characters from the extracted text
                                    unescaped_text = unescaped_text.replace('\n', '')
                                    extracted_texts.append(unescaped_text)

                except KeyError:
                    pass # Skip entries that don't have the expected structure
        else:
            print(f"Error: Invalid HAR file structure in {file_path}. Missing 'log' or 'entries'.", file=sys.stderr)

    except FileNotFoundError:
        print(f"Error: File not found at {file_path}", file=sys.stderr)
    except json.JSONDecodeError:
        print(f"Error: Could not decode HAR JSON from {file_path}. Please ensure it's a valid HAR JSON file.", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)

    return extracted_texts

def clean_unicode_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Remove carriage returns
        content = content.replace('\r', '')

        # Replace multiple newlines with a single newline
        content = re.sub(r'\n+', '\n', content)

        # Replace multiple spaces with a single space
        content = re.sub(r' +', ' ', content)

        # Ensure that `cleaned_content` is defined from `content`
        cleaned_content_lines = [line.strip() for line in content.split('\n') if line.strip()]
        cleaned_content = '\n'.join(cleaned_content_lines)


        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
    except FileNotFoundError:
        print(f"Error: File not found at {file_path} for unicode cleaning.", file=sys.stderr)
    except Exception as e:
        print(f"An error occurred during unicode cleaning of {file_path}: {e}", file=sys.stderr)

if __name__ == "__main__":
    input_file_path = "sources/www.facebook.com.har"
    output_file_path = "delivery.log"

    extracted_texts = extract_message_text_from_har(input_file_path)

    if extracted_texts:
        try:
            with open(output_file_path, 'w', encoding='utf-8') as outfile:
                for text in extracted_texts:
                    outfile.write(text + '\n')
            print(f"Extracted message texts saved to {output_file_path}")
            clean_unicode_from_file(output_file_path)
            print(f"Cleaned unicode characters in {output_file_path}")
        except IOError as e:
            print(f"Error writing to output file {output_file_path}: {e}", file=sys.stderr)
    else:
        print(f"No 'message.text' found using regex in {input_file_path}", file=sys.stderr)