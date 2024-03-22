import os
import xml.etree.ElementTree as ET
import shutil

# search dds

def search_and_copy(src_folder, dst_folder, extension):
    if not os.path.exists(dst_folder):
        os.makedirs(dst_folder)
    for root, dirs, files in os.walk(src_folder):
        for file in files:
            if file.endswith(extension):
                src_file_path = os.path.join(root, file)
                parent_dir = os.path.basename(root)
                file_name, file_extension = os.path.splitext(file)
                # new_file_name = f"{file_name}_{parent_dir}{file_extension}"
                new_file_name = f"{file}"
                dst_file_path = os.path.join(dst_folder, new_file_name)
                shutil.copy2(src_file_path, dst_file_path)
                print(f"Copied {src_file_path} to {dst_file_path}")

search_and_copy('D:\Chunithm\SDHD - CHUNITHM LUMINOUS', 'D:\Chunithm\LUMINOUSdds', '.dds')