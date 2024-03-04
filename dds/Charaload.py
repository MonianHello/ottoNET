import json

with open("output/Charadata.json", 'r') as json_file:
    data = json.load(json_file)

max_list_length = max([len(value) for key, value in data.items() if key in ['id', 'str', 'explainText']])

merged_data = []

for i in range(max_list_length):
    merged_item = {}
    for key, value in data.items():
        if key in ['id']:
            if i < len(value):
                merged_item[key] = value[i]
            else:
                merged_item[key] = None
        if key in ['str']:
            if i < len(value):
                merged_item[key] = value[i][2]
                merged_item["type"] = value[i][3]

            else:
                merged_item[key] = None
        if key in ['id']:
            id = value[i][2][:-1]
            if id == "":
                id = "0"
            if i < len(value):
                merged_item[key] = id
            else:
                merged_item[key] = None
    merged_data.append(merged_item)

for item in merged_data:
    print(item)
output_file = "Chara_output.json"

with open(output_file, 'w', encoding='utf-8') as json_out:
    json.dump(merged_data, json_out, indent=4, ensure_ascii=False)
