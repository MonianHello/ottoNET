import sqlite3
import json

# 连接到数据库
conn = sqlite3.connect('../rinsama-aqua/data/db.sqlite')
cursor = conn.cursor()

# 查询并提取数据
user_id = 3  # 假设你想要查询的用户ID为1
cursor.execute("SELECT item_id, item_kind, stock FROM chusan_user_item WHERE user_id = '{}'".format(user_id))
rows = cursor.fetchall()

# 组织数据为JSON格式
item_types = {
    "Nameplate": [],
    "Frame": [],
    "Trophy": [],
    "Skill": [],
    "Ticket": [],
    "Present": [],
    "Music": [],
    "Map Icon": [],
    "System Voice": [],
    "Symbol Chat": [],
    "Avatar Accessory": []
}

for row in rows:
    item_id = row[0]
    item_kind = row[1]
    stock = row[2]
    if item_kind == 1:
        item_types["Nameplate"].append({"item_id": item_id, "stock": stock})
    elif item_kind == 2:
        item_types["Frame"].append({"item_id": item_id, "stock": stock})
    elif item_kind == 3:
        item_types["Trophy"].append({"item_id": item_id, "stock": stock})
    elif item_kind == 4:
        item_types["Skill"].append({"item_id": item_id, "stock": stock})
    elif item_kind == 5:
        item_types["Ticket"].append({"item_id": item_id, "stock": stock})
    elif item_kind == 6:
        item_types["Present"].append({"item_id": item_id, "stock": stock})
    elif item_kind == 7:
        item_types["Music"].append({"item_id": item_id, "stock": stock})
    elif item_kind == 8:
        item_types["Map Icon"].append({"item_id": item_id, "stock": stock})
    elif item_kind == 9:
        item_types["System Voice"].append({"item_id": item_id, "stock": stock})
    elif item_kind == 10:
        item_types["Symbol Chat"].append({"item_id": item_id, "stock": stock})
    elif item_kind == 11:
        item_types["Avatar Accessory"].append({"item_id": item_id, "stock": stock})

# 输出JSON格式的数据
print(item_types["Trophy"])
