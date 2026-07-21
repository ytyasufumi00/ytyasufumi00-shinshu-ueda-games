import requests

# 🌟 コピーしたGASのWebアプリURLをここに貼り付けます
GAS_URL = "https://script.google.com/macros/s/AKfycbzWN8ku7pvpNc-bzPHLYOYfc2DEsJWyZndvC1mso0lOAIDqQ00vQhiUl1dmR1htlRfX/exec"

def get_all_counts():
    """GAS経由でスプレッドシートから現在のアクセス数を取得する"""
    try:
        response = requests.get(f"{GAS_URL}?action=get")
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return {}

def add_count(game_name):
    """指定されたゲームのアクセス数をGAS経由で1増やす"""
    try:
        requests.get(f"{GAS_URL}?action=add&game={game_name}")
    except Exception:
        pass