import json
import os

# 🌟 修正：counter.py がある場所（一番上のフォルダ）を基準にファイルを固定する
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(BASE_DIR, "visitor_counts.json")

def get_all_counts():
    """現在のアクセス数をすべて取得する"""
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return {}
    return {}

def add_count(game_name):
    """指定されたゲームのアクセス数を1増やす"""
    counts = get_all_counts()
    counts[game_name] = counts.get(game_name, 0) + 1
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(counts, f, ensure_ascii=False, indent=2)