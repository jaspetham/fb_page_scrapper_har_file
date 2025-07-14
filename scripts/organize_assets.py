import os
import hashlib
import shutil
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Pillow library not found. Please install it using: pip install Pillow")
    exit()

def get_file_hash(filepath):
    """Calculates the SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def organize_and_copy_assets(target_dir):
    """
    Groups images by content, finds the best quality version of each, 
    and organizes them in-place within the target directory.
    """
    if not os.path.isdir(target_dir):
        print(f"Error: Target directory '{target_dir}' not found.")
        return

    temp_dir = os.path.join(target_dir, "temp_unique_assets")
    Path(temp_dir).mkdir(parents=True, exist_ok=True)
    print(f"--- Organizing assets in '{target_dir}' ---")

    # Group files by hash
    image_groups = {}
    print("\n--- Grouping duplicate images ---")
    for filename in os.listdir(target_dir):
        filepath = os.path.join(target_dir, filename)
        if os.path.isfile(filepath) and filepath != temp_dir: # Exclude the temp directory itself
            try:
                file_hash = get_file_hash(filepath)
                if file_hash not in image_groups:
                    image_groups[file_hash] = []
                
                with Image.open(filepath) as img:
                    width, height = img.size
                    file_size = os.path.getsize(filepath)
                    image_groups[file_hash].append({
                        "path": filepath,
                        "size_kb": file_size / 1024,
                        "resolution": width * height
                    })
            except Exception as e:
                print(f"Could not process file {filepath}: {e}")

    # Find the best image in each group and copy it to temp_dir
    print("\n--- Selecting best quality image from each group and moving to temporary location ---")
    final_image_count = 0
    for file_hash, files in image_groups.items():
        if not files:
            continue
        
        # Find the best quality image in the group (highest resolution, then largest size)
        best_image = max(files, key=lambda x: (x['resolution'], x['size_kb']))
        
        source_path = best_image['path']
        destination_path = os.path.join(temp_dir, os.path.basename(source_path))
        
        try:
            shutil.copy2(source_path, destination_path)
            print(f"Copied best version: {os.path.basename(destination_path)}")
            final_image_count += 1
        except shutil.Error as e:
            print(f"Error copying file {os.path.basename(source_path)} to temp: {e}")

    # Clear the original target directory
    print("\n--- Clearing original assets directory ---")
    for filename in os.listdir(target_dir):
        filepath = os.path.join(target_dir, filename)
        if os.path.isfile(filepath):
            os.remove(filepath)
        elif os.path.isdir(filepath) and filepath != temp_dir: # Remove other subdirectories if any, but not temp_dir
            shutil.rmtree(filepath)

    # Move unique, high-quality images back to the target directory
    print("\n--- Moving unique assets back to original directory ---")
    for filename in os.listdir(temp_dir):
        filepath = os.path.join(temp_dir, filename)
        shutil.move(filepath, target_dir)

    # Remove the temporary directory
    shutil.rmtree(temp_dir)

    print(f"\n--- Task Complete ---")
    print(f"A total of {final_image_count} unique, high-quality images have been organized in '{target_dir}'.")

if __name__ == "__main__":
    source_directory = "assets"
    destination_directory = "assets"
    organize_and_copy_assets(source_directory, destination_directory)
