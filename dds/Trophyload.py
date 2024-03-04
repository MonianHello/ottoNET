import json

with open("output/Trophydata.json", 'r') as json_file:
    data = json.load(json_file)

max_list_length = max([len(value) for key, value in data.items() if key in ['dataName', 'str', 'explainText', 'rareType']])

merged_data = []

for i in range(max_list_length):
    merged_item = {}
    for key, value in data.items():
        if key in ['explainText', 'rareType']:
            if i < len(value):
                merged_item[key] = value[i]
            else:
                merged_item[key] = None
        if key in ['str']:
            if i < len(value):
                merged_item[key] = value[i][1]
            else:
                merged_item[key] = None
        if key in ['dataName']:
            if i < len(value):
                idvaule = value[i].replace('trophy', '').lstrip('0')
                if idvaule == '':
                    idvaule = "0"
                merged_item["id"] = idvaule
            else:
                merged_item["id"] = None
    merged_data.append(merged_item)

for item in merged_data:
    print(item)
    
output_file = "Trophy_output.json"

with open(output_file, 'w', encoding='utf-8') as json_out:
    json.dump(merged_data, json_out, indent=4, ensure_ascii=False)
