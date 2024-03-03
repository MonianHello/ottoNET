import os
import xml.etree.ElementTree as ET
import json
import shutil

# search xml

def search_and_copy(src_folder, dst_folder, extension):
    if not os.path.exists(dst_folder):
        os.makedirs(dst_folder)
    for root, dirs, files in os.walk(src_folder):
        for file in files:
            if file.endswith(extension):
                src_file_path = os.path.join(root, file)
                parent_dir = os.path.basename(root)
                file_name, file_extension = os.path.splitext(file)
                new_file_name = f"{file_name}_{parent_dir}{file_extension}"
                dst_file_path = os.path.join(dst_folder, new_file_name)
                shutil.copy2(src_file_path, dst_file_path)
                print(f"Copied {src_file_path} to {dst_file_path}")

search_and_copy('D:/Chunithm/SDHD - CHUNITHM SUN PLUS', 'D:/Chunithm/ottoNET/dds/xmlfiles', '.xml')

# 定义文件夹路径
folder_path = 'xmlfiles'

### xml2dir

# 获取文件夹中所有文件
files = os.listdir(folder_path)

# 遍历文件
for file in files:
    if file.endswith('.xml'):
        # 提取xxx部分
        prefix = file.split('_')[0]
        
        # 创建文件夹（如果不存在）
        if not os.path.exists(os.path.join(folder_path, prefix)):
            os.makedirs(os.path.join(folder_path, prefix))
        print(file)
        # 移动文件
        shutil.move(os.path.join(folder_path, file), os.path.join(folder_path, prefix, file))

### dir2json

# 遍历文件夹
for folder_name in os.listdir(folder_path):
    folder_full_path = os.path.join(folder_path, folder_name)
    
    # 确保遍历的是文件夹
    if os.path.isdir(folder_full_path):
        # 创建一个空字典，用于存储合并后的数据
        merged_data = {}

        # 遍历文件夹中的每个文件
        for file_name in os.listdir(folder_full_path):
            if file_name.endswith('.xml'):
                file_path = os.path.join(folder_full_path, file_name)
                
                # 使用ElementTree解析XML文件
                try:
                    tree = ET.parse(file_path)
                    root = tree.getroot()
                except:
                    continue

                # 将XML转换为字典
                xml_data = {}
                for elem in root.iter():
                    if elem.tag not in xml_data:
                        xml_data[elem.tag] = elem.text
                    else:
                        if not isinstance(xml_data[elem.tag], list):
                            xml_data[elem.tag] = [xml_data[elem.tag]]
                        xml_data[elem.tag].append(elem.text)
                # 合并数据到总字典中
                for key, value in xml_data.items():
                    print(key, value)
                    if key in merged_data:
                        merged_data[key].append(value)
                    else:
                        merged_data[key] = [value]

        # 创建xxxdata文件夹（如果不存在）
        output_folder_path = os.path.join('output')
        if not os.path.exists(output_folder_path):
            os.makedirs(output_folder_path)
        
        # 将合并后的数据写入JSON文件
        output_file_path = os.path.join(output_folder_path, folder_name + 'data.json')
        with open(output_file_path, 'w') as json_file:
            json.dump(merged_data, json_file, indent=4)
