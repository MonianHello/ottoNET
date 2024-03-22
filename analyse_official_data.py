import os
import csv
import json
import xml.etree.ElementTree as ET
import requests
from tqdm import tqdm
import io

# setup proxy
# PROXY = {'http': 'http://localhost:7890', 'https': 'http://localhost:7890'}


def parse_music_data(xml_file, musicid):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    if root.find("./name/id").text != musicid:
        return None

    difficulties = {}

    for fumen in root.findall("./fumens/MusicFumenData"):
        if fumen.find("./enable").text.lower() == 'false':
            level = 0
        else:
            level = float(fumen.find("./level").text)
            level += float(fumen.find("./levelDecimal").text) / 100
        difficulty_type = fumen.find("./type/str").text.lower()
        if difficulty_type in ['expert', 'master', 'ultima']:
            if difficulty_type in difficulties:
                difficulties[difficulty_type] = max(difficulties[difficulty_type], level)
            else:
                difficulties[difficulty_type] = level

    return difficulties

def cache_music_data(A000_dir, option_dir):
    music_data_cache = {}
    
    # Search in A000 directory
    music_dir = os.path.join(A000_dir, 'music')
    for musicid in os.listdir(music_dir):
        music_id_dir = os.path.join(music_dir, musicid)
        xml_file = os.path.join(music_id_dir, 'Music.xml')
        if os.path.isfile(xml_file):
            difficulties = parse_music_data(xml_file, musicid.replace('music', '').lstrip('0'))
            if difficulties is not None:
                music_data_cache[musicid.replace('music', '').lstrip('0')] = difficulties
    
    # Search in option directory
    for root, dirs, _ in os.walk(option_dir):
        for dir in dirs:
            music_dir = os.path.join(root, dir, 'music')
            if os.path.exists(music_dir):
                for item in os.listdir(music_dir):
                    item_path = os.path.join(music_dir, item)
                    xml_file = os.path.join(item_path, 'Music.xml')
                    if os.path.isfile(xml_file):
                        musicid = item.replace('music', '').lstrip('0')
                        difficulties = parse_music_data(xml_file, musicid)
                        if difficulties is not None:
                            if musicid in music_data_cache:
                                for difficulty_type in difficulties:
                                    if difficulty_type in music_data_cache[musicid]:
                                        music_data_cache[musicid][difficulty_type] = max(music_data_cache[musicid][difficulty_type], difficulties[difficulty_type])
                                    else:
                                        music_data_cache[musicid][difficulty_type] = difficulties[difficulty_type]
                            else:
                                music_data_cache[musicid] = difficulties
    return music_data_cache


def download_image(image_id):
    url = f'https://new.chunithm-net.com/chuni-mobile/html/mobile/img/{image_id}'
    path = f'chunithm/jackets/{image_id}'

    if not os.path.exists(path):
        for i in range(3):  # try 3 times
            try:
                response = requests.get(url, proxies=PROXY)
                response.raise_for_status()  # if not 200, raise exception
                with open(path, 'wb') as file:
                    file.write(response.content)
                break
            except requests.RequestException:
                pass


def process_difficulty(value):
    if value == "":
        return 0.0
    else:
        return float(value[:-1]) + 0.5 if value.endswith("+") else float(value)


# Load json
with open("chunithm/music.json", 'r', encoding='utf-8') as f:
    musics = json.load(f)

# Load csv
csv_path = "chunithm/music_difficulties.csv"
if not os.path.exists(csv_path):
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        writer.writerow(["musicid", "title", "expert", "master", "ultima"])

csv_data = {}

with open(csv_path, 'r', encoding='utf-8-sig') as file:
    reader = csv.DictReader(file)
    for row in reader:
        csv_data[row['musicid']] = {
            'expert': float(row['expert']) if row['expert'] else 0,
            'master': float(row['master']) if row['master'] else 0,
            'ultima': float(row['ultima']) if row['ultima'] else 0,
        }

A000_dir = r'D:\Chunithm\SDHD - CHUNITHM SUN PLUS\App\data\A000'
option_dir = r'D:\Chunithm\SDHD - CHUNITHM SUN PLUS\option'
output_data = []
music_data_cache = cache_music_data(A000_dir, option_dir)

# Iterate musics
for music in tqdm(musics):
    musicid = music['id']
    difficulties = csv_data.get(musicid, None)

    if difficulties is None:
        difficulties = difficulties = music_data_cache.get(musicid, None)

        if difficulties is None:
            csv_data[musicid] = {
                'expert': '',
                'master': '',
                'ultima': '',
            }
            with open(csv_path, 'a', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=['musicid', 'title', 'expert', 'master', 'ultima'])
                writer.writerow({'musicid': musicid, 'title': music['title'], 'expert': '', 'master': '', 'ultima': ''})

    try:
        output_data.append({
            "name": music['title'],
            "id": musicid,
            "genreNames": [music['catname']],
            "jaketFile": music['image'],
            "difficulties": {
                "basic": process_difficulty(music['lev_bas']),
                "advanced": process_difficulty(music['lev_adv']),
                "expert": difficulties.get('expert', 0),
                "master": difficulties.get('master', 0),
                "ultima": difficulties.get('ultima', 0),
                "world's end": 0.0
            }
        })
    except AttributeError:
        pass

    download_image(music['image'])

# Save output json
with io.open("chunithm/masterdata/musics.json", 'w', encoding='utf-8') as f:
    f.write(json.dumps(output_data, indent=4, ensure_ascii=False))