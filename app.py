from flask import Flask, jsonify, request, make_response, send_file, send_from_directory, redirect, url_for
import sqlite3
import b30 as rattools
import io
import os
import json

app = Flask(__name__, static_url_path='/static')

@app.route('/static/video/<path:filename>')
def serve_video(filename):
    # 设置缓存控制头
    return send_from_directory(app.static_folder, 'video/' + filename, cache_timeout=604800)

@app.route('/b30')
def b30pic():
    """
    返回b30图片
    """
    if not ('db_id' in request.cookies):
        return jsonify(error='未登录'), 403
    else:
        return send_file(rattools.chunib30(request.cookies.get("db_id")), as_attachment=False), 200

@app.route('/api/playlog/<playlog_id>', methods=['POST'])
def playlog(playlog_id):
    if not playlog_id.isdigit():
        return jsonify(error='非法操作'), 403
    data = rattools.single_music_playlog(playlog_id)
    return jsonify(data), 200

@app.route('/api/quicklogin', methods=['POST'])
def quickloginapi():
    """
    处理快速登录请求
    """
    if 'db_id' in request.cookies:
        return jsonify(error='已登录'), 403
    conn = sqlite3.connect('../rinsama-aqua/data/db.sqlite')
    cursor = conn.cursor()
    cursor.execute("SELECT id,user_name FROM chusan_user_data")
    rows = cursor.fetchall()
    columns = [description[0] for description in cursor.description]
    user_list = []
    for row in reversed(rows):
        row_dict = dict(zip(columns, row))
        user_list.append(row_dict)
    conn.close()

    try:
        id = request.json.get('id')
    except:
        id = False
    def check_id_in_list(id, user_list):
        for item in user_list:
            if item[0] == id:
                return True
        return False
    if(id):
        if(check_id_in_list(id, rows)):
            resp = make_response(jsonify(message='Login successful'))
            resp.set_cookie('db_id', str(id))
            return resp, 200
        else:
            return jsonify(error='非法操作'), 403
    else:
        return jsonify(user_list)  # 返回用户列表

@app.route('/api/news', methods=['POST'])
def newsapi():
    """
    返回服务器公告
    """
    if os.path.exists("news.md"):
        with open("news.md", 'r', encoding='utf-8') as file:
            news_content = file.read()
            return jsonify({"news": news_content}), 200
    else:
        return jsonify({"news": "内部绝赞测试中"}), 200

@app.route('/api/b30', methods=['POST'])
def b30api():
    """
    返回b30数据
    """
    if not ('db_id' in request.cookies):
        return jsonify(error='未登录'), 403
    else:
        return jsonify(rattools.process_b30(request.cookies.get("db_id"))[:30]), 200

@app.route('/api/playlog', methods=['POST'])
def playlogapi():
    """
    返回playlog数据
    """
    if not ('db_id' in request.cookies):
        return jsonify(error='未登录'), 403
    else:
        return jsonify(rattools.playlog(request.cookies.get("db_id"))), 200
    
@app.route('/api/r10', methods=['POST'])
def r10api():
    """
    返回r10数据
    """
    if not ('db_id' in request.cookies):
        return jsonify(error='未登录'), 403
    else:
        return jsonify(rattools.process_r10(request.cookies.get("db_id"))[:10]), 200

@app.route('/api/rating_image', methods=['POST'])
def rating_imageapi():
    number = request.json.get('number')
    if number is None:
        return jsonify(error='非法操作'), 403

    rating_image = rattools.create_rating_image(number)
    img_byte_array = io.BytesIO()
    rating_image.save(img_byte_array, format='PNG')
    img_byte_array.seek(0)
    
    return send_file(img_byte_array, mimetype='image/png')

@app.route('/api/user_info_image', methods=['POST'])
def user_info_imageapi():
    """
    返回个人信息图片
    """
    if not ('db_id' in request.cookies):
        return jsonify(error='未登录'), 403

    id = request.cookies.get("db_id")
    if id is None:
        return jsonify(error='非法操作'), 403

    rating_image = rattools.get_user_info_pic(id)
    img_byte_array = io.BytesIO()
    rating_image.save(img_byte_array, format='PNG')
    img_byte_array.seek(0)
    
    return send_file(img_byte_array, mimetype='image/png')

@app.route('/api/user_data', methods=['POST'])
def user_dataapi():
    """
    查询数据库中的 user_data
    """
    if not ('db_id' in request.cookies):
        return jsonify(error='未登录'), 403
    conn = sqlite3.connect('../rinsama-aqua/data/db.sqlite')
    cursor = conn.cursor()
    id = request.cookies.get("db_id")

    if not (id.isdecimal()):
        return jsonify(error='非法操作'), 403
    
    cursor.execute("SELECT * FROM chusan_user_data WHERE card_id = '{}'".format(id))
    rows = cursor.fetchall()
    columns = [description[0] for description in cursor.description]
    row_dict = dict(zip(columns, rows[0]))
    conn.close()
    
    return jsonify(row_dict)

@app.route('/api/login', methods=['POST'])
def loginapi():
    """
    处理用户登录请求
    """
    if 'db_id' in request.cookies:
        return jsonify(error='已登录'), 403
    
    aime_id = request.json.get('aime_id')

    if not (len(aime_id) == 20 and aime_id.isdecimal()):
        return jsonify(error='非法操作'), 403
    
    conn = sqlite3.connect('../rinsama-aqua/data/db.sqlite')
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM sega_card WHERE luid='{}'".format(aime_id))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        resp = make_response(jsonify(message='Login successful'))
        resp.set_cookie('aime_id', aime_id)
        resp.set_cookie('db_id', str(user[0]))
        return resp, 200
    else:
        return jsonify(error='未查询到用户'), 404

@app.route('/api/user_item')
def user_itemapi():

    if not ('db_id' in request.cookies):
        return jsonify(error='未登录'), 403
    else :
        user_id = request.cookies.get("db_id")
        
        try:
            assert(user_id.isdecimal())
        except AssertionError as e:
            return jsonify(error='非法操作'), 403
        
    json_data = []

    # 当前装备物品
    
    user_data_response = user_dataapi()
    try:
        if user_data_response.status_code == 200:
            user_data = json.loads((user_data_response.response)[0].decode('utf-8'))
    except:
        return jsonify(error='非法操作'), 403
    
    json_data.append(user_data)

    # 当前持有物品

    conn = sqlite3.connect('../rinsama-aqua/data/db.sqlite')
    cursor = conn.cursor()
    cursor.execute("SELECT item_id, item_kind, stock FROM chusan_user_item WHERE user_id = '{}'".format(user_id))
    rows = cursor.fetchall()

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

    #Trophy 部分

    user_trophy_list=[]
    matched_trophies = []

    for item in item_types['Trophy']:
        user_trophy_list.append(item['item_id'])

    try:
        assert(user_data["trophy_id"] in user_trophy_list)
    except AssertionError as e:
        return jsonify(error='账户数据异常(已设置的收藏品尚未获得，通常是由于绕过前端直接操作数据库造成的。)'), 403
    
    try:
        with open("masterdata/Trophy_output.json", 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        for trophy_id in user_trophy_list:
            for item in data:
                if str(item["id"]) == str(trophy_id):
                    trophy_name = item["str"]
                    explainText = item["explainText"]
                    rarity = int(item["rareType"])
                    # 因为有些歌是直接修改器改出来的，把不应该拿到的称号也一起发到账户里了。这里先简单屏蔽一下，以后再说：
                    if len(item["id"]) == 4 and int(item["id"][0]) in [5,6,7]:
                        continue
                    matched_trophies.append({
                        "id": trophy_id,
                        "name": trophy_name,
                        "explainText": explainText,
                        "rarity": rarity
                    })
                    break
        # print(json.dumps(matched_trophies, ensure_ascii=False, indent=4))
    except:
        pass

    json_data.append(matched_trophies)

    #nameplate 部分

    user_nameplate_list=[]
    matched_nameplates = []

    for item in item_types['Nameplate']:
        user_nameplate_list.append(item['item_id'])
    try:
        assert(user_data["nameplate_id"] in user_nameplate_list)
    except AssertionError as e:
        return jsonify(error='账户数据异常(已设置的收藏品尚未获得，通常是由于绕过前端直接操作数据库造成的。)'), 403
    
    try:
        with open("masterdata/Nameplate_output.json", 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        for nameplate_id in user_nameplate_list:
            for item in data:
                if str(item["id"]) == str(nameplate_id):
                    nameplate_name = item["str"]
                    explainText = item["explainText"]
                    matched_nameplates.append({
                        "id": nameplate_id,
                        "name": nameplate_name,
                        "explainText": explainText,
                        "src": "static/NamePlate/{}.png".format(str(nameplate_id).zfill(5))
                    })
                    break
        # print(json.dumps(matched_nameplates, ensure_ascii=False, indent=4))
    except:
        pass

    json_data.append(matched_nameplates)

    return jsonify(json_data)

@app.route('/')
def indexPage():
    """
    根据是否存在特定的cookie，重定向到不同的页面
    """
    if 'db_id' in request.cookies:
        return redirect(url_for('cardPage'))
    else:
        return redirect(url_for('loginPage'))

# 登录页面路由
@app.route('/login')
def loginPage():
    """
    提供登录页面
    """
    if 'db_id' in request.cookies:
        return redirect(url_for('cardPage'))
    return send_from_directory('static', 'login.html')

# 测试路由
@app.route('/test')
def testPage():
    """
    提供登录页面
    """
    if not ('db_id' in request.cookies):
        return jsonify(error='未登录'), 403
    else :
        user_id = request.cookies.get("db_id")
    
    return send_from_directory('static', 'test.html')

# 测试路由
@app.route('/items')
def itemsPage():
    """
    提供登录页面
    """
    if not ('db_id' in request.cookies):
        return jsonify(error='未登录'), 403
    else :
        user_id = request.cookies.get("db_id")
    
    return send_from_directory('static', 'items.html')

# 主页路由
@app.route('/card')
def cardPage():
    """
    提供主页页面
    """
    if 'db_id' not in request.cookies:
        return redirect(url_for('loginPage'))
    return send_from_directory('static', 'card.html')

# 游玩记录路由
@app.route('/playlog')
def playlogPage():
    """
    提供游玩记录页面
    """
    if 'db_id' not in request.cookies:
        return redirect(url_for('loginPage'))
    return send_from_directory('static', 'playlog.html')

# b30图片路由
@app.route('/b30')
def b30Page():
    """
    提供主页页面
    """
    if 'db_id' not in request.cookies:
        return redirect(url_for('loginPage'))
    return send_from_directory('static', 'b30.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081,debug=True)
