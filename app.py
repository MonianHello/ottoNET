from flask import Flask, jsonify, request, make_response, send_file, send_from_directory, redirect, url_for
import sqlite3
import b30 as ratTools
import io
import os

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
        return send_file(ratTools.chunib30(request.cookies.get("db_id")), as_attachment=False), 200

@app.route('/api/playlog/<playlog_id>', methods=['POST'])
def playlog(playlog_id):
    if not playlog_id.isdigit():
        return jsonify(error='非法操作'), 403
    data = ratTools.single_music_playlog(playlog_id)
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
        return jsonify(ratTools.process_b30(request.cookies.get("db_id"))[:30]), 200

@app.route('/api/playlog', methods=['POST'])
def playlogapi():
    """
    返回playlog数据
    """
    if not ('db_id' in request.cookies):
        return jsonify(error='未登录'), 403
    else:
        return jsonify(ratTools.playlog(request.cookies.get("db_id"))), 200
    
@app.route('/api/r10', methods=['POST'])
def r10api():
    """
    返回r10数据
    """
    if not ('db_id' in request.cookies):
        return jsonify(error='未登录'), 403
    else:
        return jsonify(ratTools.process_r10(request.cookies.get("db_id"))[:10]), 200

@app.route('/api/rating_image', methods=['POST'])
def rating_imageapi():
    number = request.json.get('number')
    if number is None:
        return jsonify(error='非法操作'), 403

    rating_image = ratTools.create_rating_image(number)
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

    rating_image = ratTools.get_user_info_pic(id)
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
    for row in reversed(rows):
        row_dict = dict(zip(columns, row))
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

# 登录页面路由
@app.route('/test')
def testPage():
    """
    提供登录页面
    """
    return send_from_directory('static', 'test.html')

# 主页路由
@app.route('/card')
def cardPage():
    """
    提供主页页面
    """
    if 'db_id' not in request.cookies:
        return redirect(url_for('loginPage'))
    return send_from_directory('static', 'card.html')

# 服务路由
@app.route('/playlog')
def playlogPage():
    """
    提供游玩记录页面
    """
    if 'db_id' not in request.cookies:
        return redirect(url_for('loginPage'))
    return send_from_directory('static', 'playlog.html')

# 服务路由
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
