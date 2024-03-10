import json

# 定义类别对应表
category_mapping = {
    "1": "Wear",
    "2": "Head",
    "3": "Face",
    "4": "Skin",
    "5": "Item",
    "6": "Front",
    "7": "Back"
}

# 读取原始 JSON 文件
with open('Avatar_output.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 创建一个字典，用于存储每个类别的数组
categorized_data = {category: [] for category in category_mapping.values()}

# 将数据分类到不同的数组中
for item in data:
    category = category_mapping.get(item['category'])
    if category:
        categorized_data[category].append(item)

# 将分类后的数据写入到新的 JSON 文件中
with open('categorized_avatar_data.json', 'w', encoding='utf-8') as f:
    json.dump(categorized_data, f, indent=4, ensure_ascii=False)

print("分类后的数据已写入到 categorized_avatar_data.json 文件中。")
