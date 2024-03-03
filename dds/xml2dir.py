import os
import shutil

# 定义文件夹路径
folder_path = 'xmlfiles'

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
        
        # 移动文件
        shutil.move(os.path.join(folder_path, file), os.path.join(folder_path, prefix, file))
