import sqlite3
import json
import os
import hashlib
from PIL import Image, ImageFont, ImageDraw, ImageFilter

def create_rating_image(number):
    """
    根据给定的数字和等级，创建一个评分图片。
    :param number: 整数，将被除以100来得到要显示的评分数字。
    :return: 一个带有透明背景的PIL图像对象，其中数字在高度上居中。
    """
    number = int(number)

    if number <= 399:
        level='green'
    elif number <= 699:
        level='orange'
    elif number <= 999:
        level='red'
    elif number <= 1199:
        level='purple'
    elif number <= 1324:
        level='bronze'
    elif number <= 1449:
        level='silver'
    elif number <= 1524:
        level='gold'
    elif number <= 1599:
        level='platinum'
    else:
        level='rainbow'

     # 将输入的整数转换为xx.xx格式的字符串
    number /= 100
    formatted_number = f"{number:.2f}"  # 保留两位小数，但不在整数部分填充0
    
    # 评分图片存储的目录
    rating_dir = 'assets/rating'
    
    # 分割格式化后的数字为整数部分和小数部分
    integer_part, decimal_part = formatted_number.split('.')
    
    # 创建列表存储对应的图片文件名
    image_files = []
    
    # 添加整数部分的数字图片文件名，对于小于10的数字不添加前导零
    for digit in integer_part:
        image_files.append(f'rating_{level}_{int(digit):02d}.png')
    
    # 添加小数点图片文件名
    image_files.append(f'rating_{level}_comma.png')
    
    # 添加小数部分的数字图片文件名，确保每个数字都是两位数
    for digit in decimal_part:
        image_files.append(f'rating_{level}_{int(digit):02d}.png')
    
    # 加载图片并计算总宽度和最大高度
    images = [Image.open(os.path.join(rating_dir, file)).convert("RGBA") for file in image_files]
    total_width = sum(img.width for img in images)
    max_height = max(img.height for img in images)
    
    # 创建新图像
    result_image = Image.new('RGBA', (total_width, max_height), (0, 0, 0, 0))
    
    # 粘贴数字到新图像，确保高度上居中
    current_width = 0
    for i, img in enumerate(images):
        # 通过索引判断当前是否为小数点图片
        if image_files[i].endswith('_comma.png'):
            # 小数点位置稍低
            offset_y = max_height - img.height
        else:
            # 数字居中
            offset_y = (max_height - img.height) // 2
        result_image.paste(img, (current_width, offset_y), img)
        current_width += img.width
    
    # 返回最终的图片
    return result_image

def calculate_rating(constant, score):
    #歌曲定数、分数=>rating
    if score >= 1009000:
        return constant + 2.15
    elif 1007500 <= score < 1009000:
        return constant + 2.0 + 0.15 * (score - 1007500) / 1500
    elif 1005000 <= score < 1007500:
        return constant + 1.5 + 0.5 * (score - 1005000) / 2500
    elif 1000000 <= score < 1005000:
        return constant + 1.0 + 0.5 * (score - 1000000) / 5000
    elif 975000 <= score < 1000000:
        return constant + (score - 975000) / 25000
    elif 925000 <= score < 975000:
        return constant - 3.0 + 3.0 * (score - 925000) / 50000
    elif 900000 <= score < 925000:
        return constant - 5.0 + 2.0 * (score - 900000) / 25000
    elif 800000 <= score < 900000:
        return (constant - 5.0) / 2 + (constant - 5.0) / 2 * (score - 800000) / 100000
    else:
        return 0

def single_music_playlog(playlogid):
    conn = sqlite3.connect('../rinsama-aqua/data/db.sqlite')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM chusan_user_playlog WHERE id = '{}'".format(playlogid))
    rows = cursor.fetchall()
    columns = [description[0] for description in cursor.description]
    user_data = []
    for row in reversed(rows):
        row_dict = dict(zip(columns, row))
        user_data.append(row_dict)
    conn.close()
    difficulty_mapping = {
        "0": "basic",
        "1": "advanced",
        "2": "expert",
        "3": "master",
        "4": "ultima",
        "5": "worldsend"
    }
    exdiff_mapping = {
        "0": "lev_adv",
        "1": "lev_bas",
        "2": "lev_exp",
        "3": "lev_mas",
        "4": "lev_ult",
        "5": "lev_we"
    }

    # 读取歌曲信息
    with open("masterdata/musics.json", "r", encoding='utf-8') as f:
        musics = json.load(f)
    with open('masterdata/musics_local.json', 'r', encoding='utf-8') as f:
        sdhd_music_data = json.load(f)
    with open('masterdata/music-ex.json', 'r', encoding='utf-8') as f:
        ex_data = json.load(f)
    music_info = {music['id']: music for music in musics}
    sdhd_music_info = {music['id']: music for music in sdhd_music_data}
    ex_info = {music['id']: music for music in ex_data}
    # 解析用户数据
    user_playlog = []
    
    # 遍历用户数据，计算rating，并构造需要的数据结构
    for record in user_data:
        music_id = str(record["music_id"])
        difficult_id = str(record["level"])
        score = int(record["score"])
        isdeleted = False
        try:
            music = music_info[music_id]
        except KeyError:
            try:
                music = sdhd_music_info[music_id]
                isdeleted = True
                music['jaketFile'] = "dummy.png"
            except KeyError:
                continue
        try:
            music_ex_info = ex_info[music_id]
        except KeyError:
            continue
        difficulty_level = difficulty_mapping[difficult_id]
        if difficulty_level in music['difficulties']:
            difficulty = music['difficulties'][difficulty_level]
            rating = calculate_rating(difficulty, score)
            user_playlog.append({
                #以下为游玩信息
                'score': score,
                'rating': rating,
                'userPlayDate':record['user_play_date'],
                'track':record['track'],
                'isClear':record['is_clear'],
                'isNewRecord':record['is_new_record'],
                'isFullCombo': record['is_full_combo'],
                'isAllJustice': record['is_all_justice'],
                'isdeleted': isdeleted,

                'countcritical':record['judge_heaven']+record['judge_critical'],                
                'countjustice':record['judge_justice'],
                'countattack':record['judge_attack'],
                'countmiss':record['judge_guilty'],
                
                #以下为歌曲信息
                #详细Level(13.8)
                'playLevel': difficulty,
                #简要Level(13+)
                'playLevelshort': music_ex_info[exdiff_mapping[difficult_id]],
                # 物量
                # 'notesair': music_ex_info[exdiff_mapping[difficult_id]+'_notes_air'],
                # 'notesflick': music_ex_info[exdiff_mapping[difficult_id]+'_notes_flick'],
                # 'noteshold': music_ex_info[exdiff_mapping[difficult_id]+'_notes_hold'],
                # 'notesslide': music_ex_info[exdiff_mapping[difficult_id]+'_notes_slide'],
                # 'notestap': music_ex_info[exdiff_mapping[difficult_id]+'_notes_tap'],
                'designer': music_ex_info[exdiff_mapping[difficult_id]+'_designer'],
                #难度
                'musicDifficulty': difficulty_level,
                'version': music_ex_info['version'],
                'musicName': music['name'],
                'jacketFile': music['jaketFile'],
                'musicID': music_ex_info['id'] ,
                #分类
                #['niconico', 'ORIGINAL', 'イロドリミドリ', '東方Project', 'POPS & ANIME', 'VARIETY', 'ゲキマイ']
                'catname': music_ex_info['catname'] ,
                'artist': music_ex_info['artist'] ,
                'bpm': music_ex_info['bpm'] ,
                # 'exInfo': music_ex_info,
            })

    return user_playlog

def playlog(id):
    conn = sqlite3.connect('../rinsama-aqua/data/db.sqlite')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM chusan_user_playlog WHERE user_id = '{}'".format(id))
    rows = cursor.fetchall()
    columns = [description[0] for description in cursor.description]
    user_data = []
    count = 0
    for row in reversed(rows):
        row_dict = dict(zip(columns, row))
        user_data.append(row_dict)
        count += 1
    conn.close()
    difficulty_mapping = {
        "0": "basic",
        "1": "advanced",
        "2": "expert",
        "3": "master",
        "4": "ultima",
        "5": "world's end"
    }

    # 读取歌曲信息
    with open("masterdata/musics.json", "r", encoding='utf-8') as f:
        musics = json.load(f)
    with open('masterdata/musics_local.json', 'r', encoding='utf-8') as f:
        sdhd_music_data = json.load(f)
    music_info = {music['id']: music for music in musics}
    sdhd_music_info = {music['id']: music for music in sdhd_music_data}
    # 解析用户数据
    user_playlog = []
    
    # 遍历用户数据，计算rating，并构造需要的数据结构
    for record in user_data:
        music_id = str(record["music_id"])
        difficult_id = str(record["level"])
        score = int(record["score"])
        isdeleted = False
        try:
            music = music_info[music_id]
        except KeyError:
            try:
                music = sdhd_music_info[music_id]
                isdeleted = True
                music['jaketFile'] = "dummy.png"
            except KeyError:
                print("没有id为{music_id}的歌曲信息")
                continue
        difficulty_level = difficulty_mapping[difficult_id]
        if difficulty_level in music['difficulties']:
            difficulty = music['difficulties'][difficulty_level]
            rating = calculate_rating(difficulty, score)
            if difficulty_level == "world's end":
                rating = None
            user_playlog.append({
                'dbPlaylogID':record['id'],
                'musicName': music['name'],
                'jacketFile': music['jaketFile'],
                #['niconico', 'ORIGINAL', 'イロドリミドリ', '東方Project', 'POPS & ANIME', 'VARIETY', 'ゲキマイ']
                'genreNames': music['genreNames'][0],
                'playLevel': difficulty,
                'musicDifficulty': difficulty_level,
                'score': score,
                'rating': rating,
                'userPlayDate':record['user_play_date'],
                'track':record['track'],
                'isClear':record['is_clear'],
                'isNewRecord':record['is_new_record'],
                'isFullCombo': record['is_full_combo'],
                'isAllJustice': record['is_all_justice'],
                'isdeleted': isdeleted,
            })

    return user_playlog

def process_r10(id):
    # 获取用户r30数据
    conn = sqlite3.connect('../rinsama-aqua/data/db.sqlite')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM chusan_user_playlog WHERE user_id = '{}'".format(id))
    rows = cursor.fetchall()
    columns = [description[0] for description in cursor.description]
    user_data = []
    count = 0
    for row in reversed(rows):
        if count >= 30:
            break
        row_dict = dict(zip(columns, row))
        user_data.append(row_dict)
        count += 1
    conn.close()

    #关于r30是最近游玩的30次（可以是30次同一首歌曲），还是最近游玩的三十首歌曲（不能重复），我不知道。
    #下面的内容是以后者为前提编写的，等我搞明白再说吧：

    #     # 获取用户数据
    # conn = sqlite3.connect('../rinsama-aqua/data/db.sqlite')
    # cursor = conn.cursor()
    # cursor.execute("SELECT * FROM chusan_user_playlog WHERE user_id = '{}'".format(id))
    # rows = cursor.fetchall()
    # columns = [description[0] for description in cursor.description]
    # user_data = []
    # count = 0
    # music_list = []
    # for row in rows:
    #     music_list.append(row[22])
    # for row in reversed(rows):
    #     if count >= 30:
    #         break
    #     if row[22] in music_list:
    #         music_list.remove(row[22])
    #         row_dict = dict(zip(columns, row))
    #         user_data.append(row_dict)
    #         count += 1
    # print(len(user_data))
    # assert(len(user_data)==30)
    # conn.close()

    difficulty_mapping = {
        "0": "basic",
        "1": "advanced",
        "2": "expert",
        "3": "master",
        "4": "ultima",
        "5": "worldsend"
    }

    # 读取歌曲信息
    with open("masterdata/musics.json", "r", encoding='utf-8') as f:
        musics = json.load(f)
    with open('masterdata/musics_local.json', 'r', encoding='utf-8') as f:
        sdhd_music_data = json.load(f)
    music_info = {music['id']: music for music in musics}
    sdhd_music_info = {music['id']: music for music in sdhd_music_data}
    # 解析用户数据
    rating_list = []
    
    # 遍历用户数据，计算rating，并构造需要的数据结构
    for record in user_data:
        music_id = str(record["music_id"])
        difficult_id = str(record["level"])
        score = int(record["score"])
        isdeleted = False
        try:
            music = music_info[music_id]
        except KeyError:
            try:
                music = sdhd_music_info[music_id]
                isdeleted = True
                music['jaketFile'] = "dummy.png"
            except KeyError:
                continue
        difficulty_level = difficulty_mapping[difficult_id]
        if difficulty_level in music['difficulties']:
            difficulty = music['difficulties'][difficulty_level]
            rating = calculate_rating(difficulty, score)
            rating_list.append({
                'musicName': music['name'],
                'jacketFile': music['jaketFile'],
                'playLevel': difficulty,
                'musicDifficulty': difficulty_level,
                'score': score,
                'rating': rating,
                'isdeleted': isdeleted,
            })

    # 将rating_list按照rating降序排序
    rating_list.sort(key=lambda x: x['rating'], reverse=True)
    return rating_list

def process_b30(id):
    # 获取用户数据
    conn = sqlite3.connect('../rinsama-aqua/data/db.sqlite')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM chusan_user_music_detail WHERE user_id = '{}'".format(id))
    rows = cursor.fetchall()
    columns = [description[0] for description in cursor.description]
    user_data = []
    for row in rows:
        row_dict = dict(zip(columns, row))
        user_data.append(row_dict)
    conn.close()

    # 读取音乐数据
    with open('masterdata/musics.json', 'r', encoding='utf-8') as f:
        music_data = json.load(f)
    
    with open('masterdata/musics_local.json', 'r', encoding='utf-8') as f:
        sdhd_music_data = json.load(f)

    # 创建一个字典，以便于从 musicId 找到对应的音乐信息
    music_dict = {music['id']: music for music in music_data}
    sdhd_music_dict = {music['id']: music for music in sdhd_music_data}
    # 存储计算出的 rating
    ratings = []

    for data in user_data:
        music_id = str(data['music_id'])
        level_index = int(data['level'])
        level_dict = {0: "basic", 1: "advanced", 2: "expert", 3: "master", 4: "ultima", 5: "world's end"}
        isdeleted = False
        try:
            music_info = music_dict[music_id]
        except KeyError:
            try:
                music_info = sdhd_music_dict[music_id]
                isdeleted = True
                music_info['jaketFile'] = "dummy.png"
            except KeyError:
                continue
        music_name = music_info['name']
        jacket_file = music_info['jaketFile']
        try:
            difficulty = music_info['difficulties'][level_dict[level_index]]
        except KeyError:
            continue
        score = int(data['score_max'])
        rating = calculate_rating(difficulty, score)

        ratings.append({
            'musicName': music_name,
            'jacketFile': jacket_file,
            'playLevel': difficulty,
            'musicDifficulty': level_dict[level_index],
            'score': score,
            'rating': rating,
            'isFullCombo': data['is_full_combo'],
            'isAllJustice': data['is_all_justice'],
            'isdeleted': isdeleted,
        })

    ratings.sort(key=lambda x: x['rating'], reverse=True)
    
    return ratings

def truncate_two_decimal_places(number):
    str_number = str(number + 0.00000002)
    decimal_index = str_number.find('.')
    if decimal_index != -1:
        str_number = str_number[:decimal_index + 3]  # 保留两位小数
    return float(str_number)

def b30single(single_data, version='2.15'):
    color = {
        'master': (187, 51, 238),
        'expert': (238, 67, 102),
        'advanced': (254, 170, 0),
        'ultima': (0, 0, 0),
        'basic': (102, 221, 17),
    }
    musictitle = single_data['musicName']
    
    if version == '2.15':
        pic = Image.new("RGB", (620, 240), (255, 250, 243))
    else:
        pic = Image.new("RGB", (620, 240), (255, 255, 255))
    
    try:
        jacket = Image.open(f'jackets/{single_data["jacketFile"]}')
    except:
        jacket = Image.open(f'static/jackets/dummy.png')
    jacket = jacket.resize((186, 186))
    pic.paste(jacket, (32, 28))

    draw = ImageDraw.Draw(pic)
    font = ImageFont.truetype('fonts/YuGothicUI-Semibold.ttf', 36)
    size = font.getsize(musictitle)
    # if version == '2.20' and single_data['isdeleted']:
    #     musictitle = '(配信停止)' + musictitle
    if size[0] > 365:
        musictitle = musictitle[:int(len(musictitle)*(345/size[0]))] + '...'
    draw.text((240, 27), musictitle, '#000000', font)

    font = ImageFont.truetype('fonts/FOT-RodinNTLGPro-DB.ttf', 58)
    draw.text((234, 87), str(single_data['score']), '#000000', font)

    font = ImageFont.truetype('fonts/SourceHanSansCN-Bold.otf', 38)
    draw.ellipse((242, 165, 286, 209), fill=color[single_data['musicDifficulty']])
    draw.rectangle((262, 165, 334, 209), fill=color[single_data['musicDifficulty']])
    draw.ellipse((312, 165, 356, 209), fill=color[single_data['musicDifficulty']])
    draw.text((259, 157), str(single_data['playLevel']), (255, 255, 255), font)
    draw.text((370, 157), '→  ' + str(truncate_two_decimal_places(single_data['rating'])), (0, 0, 0), font)

    if 'isAllJustice' in single_data:
        font = ImageFont.truetype('fonts/FOT-RodinNTLGPro-DB.ttf', 35)
        if single_data['isAllJustice'] == 'true' or single_data['isAllJustice'] is True:
            draw.text((530, 105), "AJ", '#000000', font)
        elif single_data['isFullCombo'] == 'true' or single_data['isFullCombo'] is True:
            draw.text((530, 105), "FC", '#000000', font)
            
    pic = pic.resize((280, 105))
    
    return pic

def get_user_info_pic(id):
    #硬编码内容，没ddsImage资源我怎么写

    if(str(id) == '1'):
        trophy_name = "我真的好想玩最新最熱"
        img = Image.open("CHU_UI_NamePlate_00010129.png",'r')
        default_UI_Character = Image.open("CHU_UI_Character_1662_00_02.png")
        rarity = 7
    elif(str(id) == '2'):
        trophy_name = "Arcaea"
        img = Image.open("CHU_UI_NamePlate_00025004.png",'r')
        default_UI_Character = Image.open("CHU_UI_Character_1383_00_02.png")
        rarity = 2
    else:
        trophy_name = "NEW COMER"
        img = Image.open("CHU_UI_NamePlate_dummy.png",'r')
        default_UI_Character = Image.open("CHU_UI_Character_0000_00_02.png")
        rarity = 0

    # 获取用户数据
    conn = sqlite3.connect('../rinsama-aqua/data/db.sqlite')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM chusan_user_data WHERE id = '{}'".format(id))
    rows = cursor.fetchall()
    columns = [description[0] for description in cursor.description]
    user_data = []
    for row in rows:
        row_dict = dict(zip(columns, row))
        user_data.append(row_dict)
    conn.close()

    
    img = img.convert("RGBA")

    nameplate = Image.open('pics/chu_nameplate.png')
    img.paste(nameplate, (0, 0), nameplate.split()[3])

    
    default_UI_Character = default_UI_Character.resize((82,82))
    img.paste(default_UI_Character, (471, 89), default_UI_Character.split()[3])

    rating = create_rating_image(int(user_data[0]["player_rating"]))
    rating = rating.resize((int(rating.size[0] / 1.25), int(rating.size[1] / 1.25)))
    img.paste(rating, (222, 147), rating.split()[3])

    draw = ImageDraw.Draw(img)
    font_style = ImageFont.truetype("fonts/SourceHanSansCN-Bold.otf", 30)
    draw.text((184, 100), str(user_data[0]["level"]), fill=(0, 0, 0), font=font_style)
    font_style = ImageFont.truetype("fonts/ヒラギノ角ゴ ( Hira Kaku) Pro W6.otf", 30)
    draw.text((228, 107), str(user_data[0]["user_name"]), fill=(0, 0, 0), font=font_style)

    trophy_rarity_to_color = [
        'normal', 'bronze', 'silver', 'gold', 'gold', 'platina', 'platina', 'rainbow', 'ongeki', 'staff', 'ongeki'
    ]
    trophy_pic = Image.open(f'assets/trophy/{trophy_rarity_to_color[rarity]}.png')
    img.paste(trophy_pic, (145, 46), trophy_pic.split()[3])
    font_style = ImageFont.truetype("fonts/KOZGOPRO-BOLD.OTF", 23)
    left_bound = 157
    right_bound = 547

    # 计算文本大小
    text_width, text_height = draw.textsize(trophy_name, font=font_style)

    # 确定文本的x坐标和宽度
    if text_width < right_bound - left_bound:
        # 如果文本没有超过边界，则居中显示
        x = left_bound + (right_bound - left_bound - text_width) // 2
        text_to_draw = trophy_name
    else:
        # 如果文本超过边界，对齐到左边界并截断超出部分
        x = left_bound
        # 计算可以显示的文本长度
        while text_width > right_bound - left_bound:
            trophy_name = trophy_name[:-1]
            text_width, text_height = draw.textsize(trophy_name, font=font_style)
        text_to_draw = trophy_name

    # 绘制文本
    draw.text((x, 54), text_to_draw, fill=(0, 0, 0), font=font_style)

    return img

def chunib30(userid, server='aqua', version='2.15'):
    if version == '2.15':
        pic = Image.open('pics/chub30sunp.png')
    elif version == '2.20':
        pic = Image.open('pics/chub30lmn.png')
    draw = ImageDraw.Draw(pic)

    user_team = ""
    
    shadow = Image.new("RGBA", (320, 130), (0, 0, 0, 0))
    shadow.paste(Image.new("RGBA", (280, 105), (0, 0, 0, 50)), (5, 5))
    shadow = shadow.filter(ImageFilter.GaussianBlur(3))

    ratings = process_b30(userid)
    
    rating_sum = 0
    for i in range(0, 30):
        try:
            single = b30single(ratings[i], version)
        except IndexError:
            break
        r, g, b, mask = shadow.split()
        pic.paste(shadow, ((int(52 + (i % 5) * 290)), int(287 + int(i / 5) * 127)), mask)
        pic.paste(single, ((int(53+(i%5)*290)), int(289+int(i/5)*127)))
        rating_sum += truncate_two_decimal_places(ratings[i]['rating'])
    b30 = rating_sum / 30
    font_style = ImageFont.truetype("fonts/SourceHanSansCN-Bold.otf", 37)
    draw.text((1331, 205), str(round(b30, 3)), fill=(255,255,255,255), font=font_style, stroke_width=2, stroke_fill="#38809A")

    ratings = process_r10(userid)
    rating_sum = 0
    for i in range(0, 10):
        try:
            single = b30single(ratings[i], version)
        except IndexError:
            break
        r, g, b, mask = shadow.split()
        pic.paste(shadow, ((int(1582 + (i % 2) * 290)), int(287 + int(i / 2) * 127)), mask)
        pic.paste(single, ((int(1582+(i%2)*290)), int(289+int(i/2)*127)))
        rating_sum += truncate_two_decimal_places(ratings[i]['rating'])
    r10 = rating_sum / 10
    draw.text((1717, 205), str(round(r10, 3)), fill=(255,255,255,255), font=font_style, stroke_width=2, stroke_fill="#38809A")
    
    rank = round((b30 * 3 + r10) / 4, 3)

    font_style = ImageFont.truetype("fonts/SourceHanSansCN-Medium.otf", 16)
    
    
    # 创建一个单独的图层用于绘制rank阴影
    rankimg = Image.new("RGBA", (140, 55), (100, 110, 180, 0))
    draw = ImageDraw.Draw(rankimg)
    font_style = ImageFont.truetype("fonts/SourceHanSansCN-Bold.otf", 34)
    text_width = font_style.getsize(str(rank))
    draw.text((int(70 - text_width[0] / 2), int(20 - text_width[1] / 2)), str(rank), fill=(61, 74, 162, 210),
              font=font_style, stroke_width=2, stroke_fill=(61, 74, 162, 210))
    rankimg = rankimg.filter(ImageFilter.GaussianBlur(1.2))
    draw = ImageDraw.Draw(rankimg)
    draw.text((int(70 - text_width[0] / 2), int(20 - text_width[1] / 2)), str(rank), fill=(255, 255, 255), font=font_style)
    r, g, b, mask = rankimg.split()
    pic.paste(rankimg, (712, 118), mask)


    user_nameplate = get_user_info_pic(userid)
    pic.paste(user_nameplate, (57, 55), user_nameplate.split()[3])

    text = 'ottoNET 内部测试\nrating以姓名框为准\n'

    font_style = ImageFont.truetype("fonts/SourceHanSansCN-Medium.otf", 24)

    # 创建一个透明图层，用于绘制半透明文字
    shadow_layer = Image.new('RGBA', pic.size, (255, 255, 255, 0))
    shadow_draw = ImageDraw.Draw(shadow_layer)

    # 绘制文字阴影
    shadow_position = (1976, 996) if len(text.split('\n')) == 3 else (1976, 977)
    shadow_draw.text(shadow_position, text, fill=(0, 0, 0, 150), font=font_style, align='right')
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(0.5))
    # 将带有阴影的图层合并到原始图像上
    pic.paste(Image.alpha_composite(pic.convert('RGBA'), shadow_layer), (0, 0))

    # 在原始图像上绘制不透明的文字
    draw = ImageDraw.Draw(pic)
    text_position = (1975, 995) if len(text.split('\n')) == 3 else (1975, 976)
    draw.text(text_position, text, fill=(255, 255, 255), font=font_style, align='right')

    pic = pic.convert("RGB")
    pic.save(f'static/piccache/{hashlib.sha256(str(userid).encode()).hexdigest()}b30.jpg')

    # 开发时启用
    # pic.show()

    return(f'static/piccache/{hashlib.sha256(str(userid).encode()).hexdigest()}b30.jpg')
