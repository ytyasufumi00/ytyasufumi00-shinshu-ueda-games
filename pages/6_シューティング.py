import streamlit as st
import streamlit.components.v1 as components
import base64
import os
import io

st.set_page_config(page_title="シューティング プロトタイプ", page_icon="🚀", layout="wide")

st.markdown(
    "<h1 style='font-size: 32px; margin-bottom: 0px;'>🚀 メディカル・ストライカー V14</h1>", 
    unsafe_allow_html=True
)
st.markdown(
    "<p style='font-size: 16px; color: #555;'>上田医療センターに襲来するエイリアンたち</p>", 
    unsafe_allow_html=True
)

# ==============================================================================
# 🌟 画像を自動で軽量化してBase64文字列に変換する関数
# ==============================================================================
def get_image_base64(image_path):
    if not os.path.exists(image_path):
        return "" 
    try:
        from PIL import Image
        img = Image.open(image_path)
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        img.thumbnail((200, 200))
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        b64_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        return b64_str.replace('\n', '').replace('\r', '') 
    except ImportError:
        try:
            with open(image_path, "rb") as img_file:
                b64_str = base64.b64encode(img_file.read()).decode('utf-8')
                return b64_str.replace('\n', '').replace('\r', '')
        except: return ""
    except Exception: return ""

b64_1_a = get_image_base64("pages/images/boss1_a.png")
b64_1_b = get_image_base64("pages/images/boss1_b.png")
b64_1_c = get_image_base64("pages/images/boss1_c.png")

b64_2 = get_image_base64("pages/images/boss2.png")

b64_3 = get_image_base64("pages/images/boss3.png")
b64_3_L = get_image_base64("pages/images/boss3_L.png")
b64_3_R = get_image_base64("pages/images/boss3_R.png")

b64_4_a = get_image_base64("pages/images/boss4_a.png")
b64_4_b = get_image_base64("pages/images/boss4_b.png")
b64_4   = get_image_base64("pages/images/boss4.png")

b64_5 = get_image_base64("pages/images/boss5.png")

b64_6   = get_image_base64("pages/images/boss6.png")
b64_6_a = get_image_base64("pages/images/boss6_a.png")
b64_6_b = get_image_base64("pages/images/boss6_b.png")
b64_6_c = get_image_base64("pages/images/boss6_c.png")
b64_6_d = get_image_base64("pages/images/boss6_d.png")

b64_7 = get_image_base64("pages/images/boss7.png")
b64_8 = get_image_base64("pages/images/boss8.png")
b64_9 = get_image_base64("pages/images/boss9.png")
b64_10 = get_image_base64("pages/images/boss10.png")

# ==============================================================================
# 🌟 ゲームエンジンのコア部分 (HTML/JS)
# ==============================================================================
html_code = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
    body { margin: 0; background: #2c3e50; display: flex; flex-direction: column; align-items: center; font-family: 'Helvetica Neue', Arial, sans-serif; user-select: none; -webkit-user-select: none; }
    
    #game-container { position: relative; width: 100%; max-width: 500px; min-height: 750px; background: #000; border: 4px solid #34495e; border-radius: 8px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.5); display: flex; flex-direction: column; touch-action: none; }
    
    #hanger-screen { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: #1a252f; color: white; display: flex; flex-direction: column; padding: 15px; box-sizing: border-box; z-index: 50; touch-action: auto; overflow-y: auto; }
    
    /* 🌟 エッジスクロール用のレーン */
    .scroll-edge { display: none; position: absolute; top: 0; width: 40px; height: 100%; z-index: 15; touch-action: pan-y; align-items: center; justify-content: center; color: rgba(255,255,255,0.15); font-size: 24px; font-weight: bold; pointer-events: auto; }
    #edge-left { left: 0; background: linear-gradient(90deg, rgba(255,255,255,0.05), transparent); border-right: 1px solid rgba(255,255,255,0.05); }
    #edge-right { right: 0; background: linear-gradient(270deg, rgba(255,255,255,0.05), transparent); border-left: 1px solid rgba(255,255,255,0.05); }

    .style-select-box { background: rgba(52, 152, 219, 0.1); padding: 10px; border-radius: 8px; margin-bottom: 10px; border: 2px solid #3498db; }
    .style-select-box select { width: 100%; padding: 8px; border-radius: 5px; background: #2c3e50; color: #fff; border: 1px solid #3498db; font-weight: bold; margin-top: 5px; font-size: 14px; }
    
    .upg-item { background: rgba(255,255,255,0.05); border-left: 5px solid #f1c40f; padding: 8px 12px; border-radius: 8px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center; }
    .upg-title { font-weight: 900; font-size: 14px; margin-bottom: 2px; color: #fff;}
    .upg-desc { font-size: 10px; color: #bdc3c7; font-weight: bold; }
    .upg-btn { background: #f1c40f; color: #2c3e50; border: none; padding: 8px 10px; border-radius: 8px; font-weight: 900; font-size: 12px; cursor: pointer; box-shadow: 0 3px 0 #d35400; transition: 0.1s; min-width: 70px; text-align: center; }
    .upg-btn:active:not(:disabled) { transform: translateY(3px); box-shadow: 0 0 0 #d35400; }
    .upg-btn:disabled { background: #7f8c8d; box-shadow: 0 3px 0 #34495e; color: #bdc3c7; cursor: not-allowed; }
    canvas { width: 100%; max-width: 500px; aspect-ratio: 500 / 666; display: none; margin: 0 auto; }
    
    #controls-container { display: none; width: 100%; background: #1a252f; border-top: 2px solid #34495e; padding: 10px 20px; box-sizing: border-box; justify-content: space-between; align-items: center; z-index: 20; position: relative; touch-action: none; }
    #joystick-zone { display: flex; touch-action: none; width: 110px; height: 110px; background: rgba(255, 255, 255, 0.1); border-radius: 50%; justify-content: center; align-items: center; border: 2px solid rgba(255,255,255,0.2); margin: 0; position: relative; }
    #joystick-knob { width: 45px; height: 45px; background: rgba(52, 152, 219, 0.8); border-radius: 50%; position: absolute; box-shadow: 0 4px 10px rgba(0,0,0,0.5); pointer-events: none; }
    #action-btn { display: flex; touch-action: none; width: 80px; height: 80px; background: rgba(231, 76, 60, 0.8); border-radius: 50%; flex-direction: column; justify-content: center; align-items: center; border: 2px solid rgba(255,255,255,0.3); cursor: pointer; box-shadow: 0 4px 10px rgba(0,0,0,0.5); margin: 0; position: relative; }
    #action-btn:active { transform: scale(0.95); }
    #overlay { display: none; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); z-index: 30; flex-direction: column; justify-content: center; align-items: center; text-align: center; color: white; }
    .btn { border: none; border-radius: 8px; padding: 12px; font-size: 16px; font-weight: 900; cursor: pointer; }
    .start-btn { background: #3498db; color: white; box-shadow: 0 4px 0 #2980b9; margin-top: auto; }
    .start-btn:active { transform: translateY(4px); box-shadow: 0 0 0 #2980b9; }
</style>
</head>
<body>
<div id="game-container">
    <div id="edge-left" class="scroll-edge"><span>↕</span></div>
    <div id="edge-right" class="scroll-edge"><span>↕</span></div>

    <div id="hanger-screen">
        <h2 style="color: #f1c40f; text-align: center; margin-top: 0px; margin-bottom: 5px; font-size: 22px;">🛠️ 基地ハンガー</h2>
        
        <div style="display: flex; gap: 10px; margin-bottom: 10px;">
            <div style="flex: 1; text-align: center; background: rgba(0,0,0,0.4); padding: 5px; border-radius: 8px;">
                <span style="font-size: 12px; color: #bdc3c7;">所持クレジット</span><br><span id="display-credits" style="font-size: 24px; font-weight: 900; color: #2ecc71;">0</span> <span style="font-size: 14px;">C</span>
            </div>
        </div>

        <div class="style-select-box">
            <div style="font-size: 12px; color: #3498db; font-weight: bold;">📊 戦闘方針（ドロップアイテム傾向）</div>
            <select id="style-select">
                <option value="balanced">⚖️ バランス型 (全アイテム均等に出現)</option>
                <option value="assault">⚔️ 強襲型 (主砲/レーザー/ミサイル/OP 特化)</option>
                <option value="heavy">💣 重武装型 (ボム/サブボム/フォース 特化)</option>
                <option value="defense">🛡️ 防衛・機動型 (シールド/スピード/ビット 特化)</option>
            </select>
        </div>

        <div style="flex-grow: 1; overflow-y: auto;">
            <div class="upg-item"><div><div class="upg-title">🔫 連射速度UP (Lv.<span id="lvl-fire"></span>)</div><div class="upg-desc">主砲の発射間隔が劇的に短縮</div></div><button class="upg-btn" id="btn-fire" onclick="buyUpgrade('fire')">100 C</button></div>
            <div class="upg-item"><div><div class="upg-title">⚡ 貫通レーザー (Lv.<span id="lvl-laser"></span>)</div><div class="upg-desc">敵を貫く高威力の光線を自動発射</div></div><button class="upg-btn" id="btn-laser" onclick="buyUpgrade('laser')">100 C</button></div>
            <div class="upg-item"><div><div class="upg-title">🧨 对地サブボム (Lv.<span id="lvl-subBomb"></span>)</div><div class="upg-desc">前方に爆風を発生させる</div></div><button class="upg-btn" id="btn-subBomb" onclick="buyUpgrade('subBomb')">100 C</button></div>
            <div class="upg-item"><div><div class="upg-title">🚀 追尾ミサイル (Lv.<span id="lvl-missile"></span>)</div><div class="upg-desc">敵を自動で追いかけるミサイル</div></div><button class="upg-btn" id="btn-missile" onclick="buyUpgrade('missile')">100 C</button></div>
            <div class="upg-item"><div><div class="upg-title">🛸 防衛ビット (Lv.<span id="lvl-bit"></span>)</div><div class="upg-desc">自機の周りを回り敵を攻撃</div></div><button class="upg-btn" id="btn-bit" onclick="buyUpgrade('bit')">100 C</button></div>
            <div class="upg-item"><div><div class="upg-title">🟠 追従オプション (Lv.<span id="lvl-option"></span>)</div><div class="upg-desc">自機の軌跡を追い主砲を撃つ</div></div><button class="upg-btn" id="btn-option" onclick="buyUpgrade('option')">200 C</button></div>
            <div class="upg-item"><div><div class="upg-title">💨 移動速度UP (Lv.<span id="lvl-speed"></span>)</div><div class="upg-desc">ジョイスティック操作時の速度上昇</div></div><button class="upg-btn" id="btn-speed" onclick="buyUpgrade('speed')">100 C</button></div>
            <div class="upg-item"><div><div class="upg-title">🛡️ バリア装備 (Lv.<span id="lvl-shield"></span>)</div><div class="upg-desc">被弾を無効化するシールド</div></div><button class="upg-btn" id="btn-shield" onclick="buyUpgrade('shield')">100 C</button></div>
            <div class="upg-item" style="border-left: 5px solid #e74c3c;"><div><div class="upg-title" style="color:#e74c3c;">🔥 必殺ボム増量 (Lv.<span id="lvl-bomb"></span>)</div><div class="upg-desc">画面一掃の必殺技</div></div><button class="upg-btn" id="btn-bomb" onclick="buyUpgrade('bomb')">200 C</button></div>
            <div class="upg-item" style="border-left: 5px solid #3498db; background: rgba(52,152,219,0.1);"><div><div class="upg-title" style="color:#3498db;">🔵 フォース＆波動砲 (Lv.<span id="lvl-force"></span>)</div><div class="upg-desc">着脱式の盾＆長押し波動砲(排他)</div></div><button class="upg-btn" id="btn-force" onclick="buyUpgrade('force')">300 C</button></div>
        </div>
        <button class="btn start-btn" onclick="startGame()">🚀 出撃する</button>
        <button class="btn" style="background: transparent; color: #7f8c8d; font-size: 12px; margin-top: 0px; padding: 5px;" onclick="resetSaveData()">セーブデータ消去</button>
    </div>
    <canvas id="gameCanvas" width="500" height="666"></canvas>
    <div id="controls-container">
        <div id="joystick-zone"><div id="joystick-knob"></div></div>
        <div id="action-btn" onmousedown="startAction(event)" ontouchstart="startAction(event)" onmouseup="endAction(event)" ontouchend="endAction(event)" onmouseleave="endAction(event)"></div>
    </div>
    <div id="overlay">
        <div style="font-size: 40px; font-weight: 900; color: #e74c3c; margin-bottom: 10px;">MISSION FAILED</div>
        <div style="font-size: 18px; color: #bdc3c7;">今回のスコア</div>
        <div id="final-score" style="font-size: 40px; font-weight: 900; color: #fff; margin-bottom: 5px;">0</div>
        <div style="background: rgba(46, 204, 113, 0.2); border: 2px solid #2ecc71; padding: 15px; border-radius: 8px; margin-bottom: 20px; width: 80%;">
            <div style="font-size: 16px; color: #2ecc71; font-weight: bold;">獲得クレジット（報酬）</div>
            <div id="earned-credits" style="font-size: 36px; font-weight: 900; color: #2ecc71;">+0 C</div>
        </div>
        <button class="btn" style="background:#f1c40f; color:#2c3e50; width: 80%; box-shadow: 0 4px 0 #d35400;" onclick="location.reload()">ハンガーへ帰還する</button>
    </div>
</div>

<script>
    var DATA_B64_1_A = "__B64_BOSS_01_A__"; var DATA_B64_1_B = "__B64_BOSS_01_B__"; var DATA_B64_1_C = "__B64_BOSS_01_C__";
    var DATA_B64_2 = "__B64_BOSS_02__"; 
    var DATA_B64_3 = "__B64_BOSS_03__"; var DATA_B64_3_L = "__B64_BOSS_03_L__"; var DATA_B64_3_R = "__B64_BOSS_03_R__";
    var DATA_B64_4_A = "__B64_BOSS_04_A__"; var DATA_B64_4_B = "__B64_BOSS_04_B__"; var DATA_B64_4 = "__B64_BOSS_04__";
    var DATA_B64_5 = "__B64_BOSS_05__"; 
    
    var DATA_B64_6   = "__B64_BOSS_06__"; 
    var DATA_B64_6_A = "__B64_BOSS_06_A__"; 
    var DATA_B64_6_B = "__B64_BOSS_06_B__"; 
    var DATA_B64_6_C = "__B64_BOSS_06_C__"; 
    var DATA_B64_6_D = "__B64_BOSS_06_D__"; 
    
    var DATA_B64_7 = "__B64_BOSS_07__"; 
    var DATA_B64_8 = "__B64_BOSS_08__"; var DATA_B64_9 = "__B64_BOSS_09__"; var DATA_B64_10 = "__B64_BOSS_10__";
</script>

<script>
    const canvas = document.getElementById("gameCanvas"); const ctx = canvas.getContext("2d");
    const overlay = document.getElementById("overlay"); const hanger = document.getElementById("hanger-screen");
    const actionBtn = document.getElementById("action-btn"); const controls = document.getElementById("controls-container");
    const joyZone = document.getElementById("joystick-zone"); const joyKnob = document.getElementById("joystick-knob");
    
    let isDragging = false; let joyDx = 0; let joyDy = 0; const maxRadius = 35; 
    function handleJoyStart(e) { isDragging = true; handleJoyMove(e); }
    function handleJoyMove(e) {
        if (!isDragging) return; e.preventDefault();
        let clientX = e.touches ? e.touches[0].clientX : e.clientX; let clientY = e.touches ? e.touches[0].clientY : e.clientY;
        const rect = joyZone.getBoundingClientRect();
        let dx = clientX - (rect.left + rect.width / 2); let dy = clientY - (rect.top + rect.height / 2);
        let dist = Math.hypot(dx, dy);
        if (dist > maxRadius) { dx = (dx / dist) * maxRadius; dy = (dy / dist) * maxRadius; }
        joyKnob.style.transform = `translate(${dx}px, ${dy}px)`; joyDx = dx / maxRadius; joyDy = dy / maxRadius;
    }
    function handleJoyEnd(e) { isDragging = false; joyDx = 0; joyDy = 0; joyKnob.style.transform = `translate(0px, 0px)`; }
    joyZone.addEventListener("touchstart", handleJoyStart, {passive: false}); joyZone.addEventListener("touchmove", handleJoyMove, {passive: false});
    joyZone.addEventListener("touchend", handleJoyEnd); joyZone.addEventListener("mousedown", handleJoyStart);
    window.addEventListener("mousemove", handleJoyMove); window.addEventListener("mouseup", handleJoyEnd);

    function safeGetB64(varName) { try { return window[varName] || ""; } catch(e) { return ""; } }
    function createBossImgObj(b64_string) {
        let obj = { img: new Image(), isLoaded: false };
        if (b64_string && b64_string !== "" && !b64_string.startsWith("__B64")) {
            obj.img.src = "data:image/png;base64," + b64_string; obj.img.onload = () => { obj.isLoaded = true; };
        }
        return obj;
    }

    const boss1_A = createBossImgObj(safeGetB64("DATA_B64_1_A")); const boss1_B = createBossImgObj(safeGetB64("DATA_B64_1_B")); const boss1_C = createBossImgObj(safeGetB64("DATA_B64_1_C"));
    const bossImg2 = createBossImgObj(safeGetB64("DATA_B64_2")); 
    const bossImg3 = createBossImgObj(safeGetB64("DATA_B64_3")); 
    const boss3_L_Img = createBossImgObj(safeGetB64("DATA_B64_3_L")); 
    const boss3_R_Img = createBossImgObj(safeGetB64("DATA_B64_3_R")); 

    const bossImg4 = createBossImgObj(safeGetB64("DATA_B64_4"));
    const bossImg4_A = createBossImgObj(safeGetB64("DATA_B64_4_A"));
    const bossImg4_B = createBossImgObj(safeGetB64("DATA_B64_4_B"));

    const bossImg5 = createBossImgObj(safeGetB64("DATA_B64_5")); 
    const bossImg6 = createBossImgObj(safeGetB64("DATA_B64_6")); const bossImg6_A = createBossImgObj(safeGetB64("DATA_B64_6_A")); const bossImg6_B = createBossImgObj(safeGetB64("DATA_B64_6_B")); const bossImg6_C = createBossImgObj(safeGetB64("DATA_B64_6_C")); const bossImg6_D = createBossImgObj(safeGetB64("DATA_B64_6_D")); 
    const bossImg7 = createBossImgObj(safeGetB64("DATA_B64_7")); 
    const bossImg8 = createBossImgObj(safeGetB64("DATA_B64_8")); const bossImg9 = createBossImgObj(safeGetB64("DATA_B64_9")); 
    const bossImg10 = createBossImgObj(safeGetB64("DATA_B64_10"));

    const bossList = [
        { name: "LV1: ガンダム", imgAnims: [boss1_A, boss1_B, boss1_C], emoji: "🍌", hp: 120, speed: 0.5, size: 80, color: "#f1c40f" },
        { name: "LV2: 病床利用率将軍", imgAnims: [bossImg2], emoji: "🕷️", hp: 200, speed: 0.6, size: 85, color: "#9b59b6" },
        { name: "LV3: 冷蔵庫", imgAnims: [bossImg3], emoji: "🦂", hp: 400, speed: 0.4, size: 90, color: "#e67e22",
          parts: [ { name: "取り巻き1", imgObj: boss3_L_Img, emoji: "🦞", baseDx: -65, baseDy: 10, hp: 150, size: 45, isLeft: true, animPhase: 0 }, { name: "取り巻き2", imgObj: boss3_R_Img, emoji: "🦞", baseDx: 65, baseDy: 10, hp: 150, size: 45, isLeft: false, animPhase: Math.PI } ]
        },
        { name: "LV4: 超過勤務チェッカー", imgAnims: [bossImg4, bossImg4_A, bossImg4_B], emoji: "🧬", hp: 500, speed: 0.8, size: 95, color: "#2ecc71" },
        { name: "LV5: 漆黒のネクロセル", imgAnims: [bossImg5], emoji: "💀", hp: 700, speed: 0.5, size: 100, color: "#95a5a6" },
        { name: "LV6: 一人称オラ", imgAnims: [bossImg6, bossImg6_A, bossImg6_B, bossImg6_C, bossImg6_D], emoji: "👁️", hp: 1000, speed: 0.4, size: 110, color: "#e74c3c" },
        { name: "LV7: 地球外病原体 X", imgAnims: [bossImg7], emoji: "👽", hp: 1400, speed: 1.0, size: 90, color: "#2ecc71" },
        { name: "LV8: 殺戮機兵 オメガ", imgAnims: [bossImg8], emoji: "🤖", hp: 1800, speed: 0.5, size: 120, color: "#34495e",
          parts: [ { name: "左砲台", emoji: "🛰️", baseDx: -80, baseDy: 0, hp: 400, size: 50, isLeft: true, animPhase: 0 }, { name: "右砲台", emoji: "🛰️", baseDx: 80, baseDy: 0, hp: 400, size: 50, isLeft: false, animPhase: Math.PI } ]
        },
        { name: "LV9: 終末の魔竜", imgAnims: [bossImg9], emoji: "🐉", hp: 2800, speed: 0.6, size: 140, color: "#e74c3c" },
        { name: "MAX: 医療神 アスクレピオス", imgAnims: [bossImg10], emoji: "👼", hp: 5000, speed: 0.4, size: 160, color: "#f1c40f" }
    ];
    let bossEncounterCount = 0; 

    const ynQuizzes = [
        { q: "成人の胸骨圧迫の深さは5cm以上である？", a: "⭕" }, { q: "インスリン注射は毎回同じ場所に打つべきである？", a: "❌" },
        { q: "AEDのパッドはペースメーカーの真上に貼る？", a: "❌" }, { q: "成人ICLSの高度気道確保後の換気は6秒に1回である？", a: "⭕" }
    ];

    const itemIcons = { fire: "🔫", laser: "⚡", subBomb: "🧨", missile: "🚀", bit: "🛸", option: "🟠", speed: "💨", shield: "🛡️", bomb: "🔥", force: "🔵" };

    let savedData = { credits: 0, upgrades: { fire: 0, speed: 0, shield: 0, bomb: 0, laser: 0, subBomb: 0, missile: 0, bit: 0, option: 0, force: 0 } };
    let tempUpgrades = { fire: 0, speed: 0, shield: 0, bomb: 0, laser: 0, subBomb: 0, missile: 0, bit: 0, option: 0, force: 0 };
    let earnedCreditsInGame = 0;

    try {
        const localData = localStorage.getItem('medicalStrikerSaveV8');
        if (localData) {
            let parsed = JSON.parse(localData);
            if(parsed.upgrades) { ['laser', 'subBomb', 'missile', 'bit', 'option', 'force'].forEach(k => { if(parsed.upgrades[k] === undefined) parsed.upgrades[k] = 0; }); savedData = parsed; }
        }
    } catch(e) {}
    function saveData() { try { localStorage.setItem('medicalStrikerSaveV8', JSON.stringify(savedData)); } catch(e) {} }
    window.resetSaveData = function() { if(confirm("データを初期化しますか？")) { localStorage.removeItem('medicalStrikerSaveV8'); location.reload(); } }

    const MAX_LEVEL = 10; const MAX_LEVEL_OPTION = 4; const MAX_LEVEL_FORCE = 3;
    function getCost(type, lvl) { 
        let multi = (lvl + 1) * (lvl + 1);
        if(type === 'force') return 200 * multi; if(type === 'shield' || type === 'option') return 150 * multi;
        if(type === 'bomb' || type === 'laser' || type === 'missile') return 100 * multi; return 50 * multi; 
    }

    function getLevel(type) { return savedData.upgrades[type] + tempUpgrades[type]; }

    function updateHangerUI() {
        document.getElementById('display-credits').innerText = savedData.credits;
        upgKeys.forEach(type => {
            let lvl = savedData.upgrades[type]; document.getElementById(`lvl-${type}`).innerText = lvl;
            let btn = document.getElementById(`btn-${type}`); let limit = (type === 'option') ? MAX_LEVEL_OPTION : (type === 'force' ? MAX_LEVEL_FORCE : MAX_LEVEL);
            if (lvl >= limit) { btn.innerText = "MAX"; btn.disabled = true; } 
            else { let cost = getCost(type, lvl); btn.innerText = cost + " C"; btn.disabled = (savedData.credits < cost); }
        });
    }

    const upgKeys = ['fire', 'speed', 'shield', 'bomb', 'laser', 'subBomb', 'missile', 'bit', 'option', 'force'];
    window.buyUpgrade = function(type) {
        let lvl = savedData.upgrades[type]; let limit = (type === 'option') ? MAX_LEVEL_OPTION : (type === 'force' ? MAX_LEVEL_FORCE : MAX_LEVEL);
        if (lvl >= limit) return; let cost = getCost(type, lvl);
        if (savedData.credits >= cost) { savedData.credits -= cost; savedData.upgrades[type]++; saveData(); updateHangerUI(); }
    }
    updateHangerUI();

    let isGameOver = false; let score = 0; let frameCount = 0; let powerUpTime = 0; let activeQuiz = null;
    let exp = 0; let level = 1; let nextLevelExp = 500;
    
    let stars = []; for(let i=0; i<50; i++) { stars.push({ x: Math.random() * 500, y: Math.random() * 666, speed: 1 + Math.random() * 3, size: Math.random() * 3 }); }
    let player = { x: 250, y: 550, size: 40, emoji: "💉", speed: 5.0, shields: 0, invincible: 0, history: [] };
    
    let bullets = []; let enemies = []; let enemyBullets = []; let effects = []; let blasts = []; let items = []; let gameLoopId;
    let bombs = 0; let isBombing = 0; 
    let isCharging = false; let chargeLevel = 0; let actionPressTime = 0;
    let forceObj = { exists: false, attached: true, returning: false, x: 0, y: 0, vx: 0, vy: 0 };
    let waveCannon = { active: false, life: 0, width: 0, damage: 0 };
    let screenFlash = 0; 

    function spawnItem(x, y) {
        let style = document.getElementById("style-select").value;
        let pool = [];
        let weights = {
            balanced: { fire:1, laser:1, subBomb:1, missile:1, bit:1, option:1, speed:1, shield:1, bomb:1, force:1 },
            assault:  { fire:4, laser:4, subBomb:1, missile:4, bit:1, option:4, speed:1, shield:1, bomb:1, force:1 },
            heavy:    { fire:1, laser:1, subBomb:4, missile:1, bit:1, option:1, speed:1, shield:1, bomb:4, force:4 },
            defense:  { fire:1, laser:1, subBomb:1, missile:1, bit:4, option:1, speed:4, shield:4, bomb:1, force:1 }
        };
        let w = weights[style] || weights.balanced;
        for (let key in w) { for(let i = 0; i < w[key]; i++) { pool.push(key); } }
        let chosen = pool[Math.floor(Math.random() * pool.length)];
        items.push({ x: x, y: y, type: chosen, emoji: itemIcons[chosen], speed: 1.5, size: 20 });
    }

    window.startGame = function() {
        hanger.style.display = "none"; canvas.style.display = "block"; controls.style.display = "flex"; 
        
        // 🌟 プレイ開始時に左右のスクロールゾーンを表示
        document.getElementById("edge-left").style.display = "flex";
        document.getElementById("edge-right").style.display = "flex";

        tempUpgrades = { fire: 0, speed: 0, shield: 0, bomb: 0, laser: 0, subBomb: 0, missile: 0, bit: 0, option: 0, force: 0 };
        earnedCreditsInGame = 0;

        player.speed = 5.0 + (getLevel('speed') * 0.4); 
        player.shields = getLevel('shield'); 
        player.invincible = 0; player.history = []; 
        
        let forceLv = getLevel('force');
        if (forceLv > 0) {
            actionBtn.style.background = "rgba(52, 152, 219, 0.8)"; actionBtn.innerHTML = `<div style="font-size: 26px;">🛡️</div><div style="font-size: 10px; font-weight: bold; color: white;">CHARGE</div>`;
            forceObj.exists = true; forceObj.attached = true;
        } else {
            actionBtn.style.background = "rgba(231, 76, 60, 0.8)"; bombs = 2 + getLevel('bomb');
            actionBtn.innerHTML = `<div style="font-size: 26px;">🔥</div><div id="bomb-count-disp" style="font-size: 14px; font-weight: bold; color: white;">x${bombs}</div>`;
        }
        blasts = []; bullets = []; enemies = []; enemyBullets = []; effects = []; items = [];
        if (!gameLoopId) loop();
    }

    function damagePlayer() {
        if (player.invincible <= 0) {
            if (player.shields > 0) {
                player.shields--; player.invincible = 90; effects.push({ x: player.x, y: player.y, text: "🛡️ シールド破損!", life: 40, vy: -1, color: "#3498db" }); return false;
            } else {
                isGameOver = true; controls.style.display = "none";
                document.getElementById("edge-left").style.display = "none";
                document.getElementById("edge-right").style.display = "none";

                let earned = Math.floor(score / 25) + earnedCreditsInGame; 
                savedData.credits += earned; saveData();
                
                effects.push({ x: player.x, y: player.y, text: "🔥", life: 60, vy: 0, color: "#fff" });
                document.getElementById("final-score").innerText = score; document.getElementById("earned-credits").innerText = "+" + earned + " C"; overlay.style.display = "flex";
                return true; 
            }
        }
        return false;
    }

    window.startAction = function(e) {
        if(e) e.preventDefault(); if (isGameOver) return;
        if (getLevel('force') > 0) { isCharging = true; chargeLevel = 0; actionPressTime = Date.now(); actionBtn.style.transform = "scale(0.9)"; } 
        else { if(bombs > 0 && isBombing === 0) fireNormalBomb(); }
    }

    window.endAction = function(e) {
        if(e) e.preventDefault(); if (isGameOver) return; actionBtn.style.transform = "scale(1.0)";
        let forceLv = getLevel('force');
        if (forceLv > 0 && isCharging) {
            isCharging = false; let holdTime = Date.now() - actionPressTime;
            if (holdTime < 300) { if (forceObj.attached) { forceObj.attached = false; forceObj.vx = 0; forceObj.vy = -12; } else { forceObj.returning = true; } } 
            else {
                if (chargeLevel > 60) {
                    waveCannon.active = true; waveCannon.life = 45; waveCannon.width = 40 + (chargeLevel / 3) + (forceLv * 20); waveCannon.damage = 0.5 + (forceLv * 0.3) + (chargeLevel / 100);
                    effects.push({ x: player.x, y: player.y, text: "🌊 波動砲 発射! 🌊", life: 60, vy: -1, color: "#3498db" });
                }
            }
            chargeLevel = 0;
        }
    }

    function fireNormalBomb() {
        bombs--; let bd = document.getElementById("bomb-count-disp"); if(bd) bd.innerText = "x" + bombs; 
        isBombing = 40; player.invincible = 120;
        effects.push({ x: canvas.width/2, y: canvas.height/2, text: "🔥 MAXIMUM BOMB 🔥", life: 60, vy: -1, color: "#e74c3c" });
        enemies.forEach(enemy => { enemy.hp -= 50; effects.push({ x: enemy.x + (Math.random()*40-20), y: enemy.y + (Math.random()*40-20), text: "💥", life: 30, vy: -1, color: "#fff" }); if(enemy.hp <= 0 && !enemy.vanish) killEnemy(enemy); });
        enemyBullets = [];
    }

    function checkCollision(obj1, obj2, hitRadius) { return Math.hypot(obj1.x - obj2.x, obj1.y - obj2.y) < hitRadius; }

    function gainExp(amount) {
        exp += amount; let leveledUp = false;
        while (exp >= nextLevelExp) { exp -= nextLevelExp; level++; nextLevelExp = level * 500; leveledUp = true; }
        if (leveledUp) effects.push({ x: player.x, y: player.y - 40, text: "LEVEL UP!!", life: 60, vy: -1.5, color: "#f1c40f" });
    }

    function killEnemy(enemy) {
        enemy.vanish = true;
        if (enemy.isQuiz) {
            if (activeQuiz && enemy.ans === activeQuiz.a) {
                powerUpTime = 400; score += 500; 
                effects.push({ x: canvas.width/2, y: canvas.height/2, text: "✨ 正解ボーナス!! アイテム出現 ✨", life: 60, vy: -1, color: "#f1c40f" });
                spawnItem(canvas.width/2 - 40, canvas.height/2); spawnItem(canvas.width/2, canvas.height/2 - 25); spawnItem(canvas.width/2 + 40, canvas.height/2);
            } else { 
                effects.push({ x: canvas.width/2, y: canvas.height/2, text: "❌ 不正解...", life: 60, vy: -1, color: "#e74c3c" }); 
            }
            activeQuiz = null; enemies.forEach(e => { if(e.isQuiz) e.vanish = true; });
        } else if (enemy.isBossPart) {
            score += 3000; gainExp(800); effects.push({ x: enemy.x, y: enemy.y, text: `💥 部位破壊!!`, life: 60, vy: -2, color: "#f1c40f" });
        } else if (enemy.isBoss) {
            score += 10000; gainExp(2000);
            effects.push({ x: enemy.x, y: enemy.y, text: `🎊 ${enemy.name.split(' ')[0]} 撃破!! 🎊`, life: 60, vy: -2, color: enemy.color });
            
            enemies.forEach(e => { 
                if(!e.isQuiz && !e.isBoss && !e.isBossPart) e.vanish = true; 
                if(e.isBossPart && e.parentId === enemy.bId) e.vanish = true;
            }); 
            enemyBullets = []; 
        } else {
            let isMid = enemy.emoji === "👾"; score += (isMid ? 300 : 100); gainExp(isMid ? 150 : 50);
            effects.push({ x: enemy.x, y: enemy.y, text: "✨", life: 20, vy: -2, color: "#fff" });
            if (isMid && Math.random() < 0.4) spawnItem(enemy.x, enemy.y);
            else if (!isMid && Math.random() < 0.05) spawnItem(enemy.x, enemy.y);
        }
    }

    let difficultyScale = 1500; 
    let bossSpawnInterval = 1600; 
    let quizInvincibleTime = 150; 

    function update() {
        if (isGameOver) return; frameCount++;
        if (powerUpTime > 0) powerUpTime--; if (player.invincible > 0) player.invincible--; 
        if (isBombing > 0) isBombing--; if (screenFlash > 0) screenFlash--;

        stars.forEach(s => { s.y += s.speed; if (s.y > canvas.height) { s.y = 0; s.x = Math.random() * canvas.width; } });

        player.speed = 5.0 + (getLevel('speed') * 0.4); 
        player.x += joyDx * player.speed; player.y += joyDy * player.speed;
        if(player.x < 20) player.x = 20; if(player.x > canvas.width - 20) player.x = canvas.width - 20;
        if(player.y < 20) player.y = 20; if(player.y > canvas.height - 20) player.y = canvas.height - 20;

        player.history.unshift({x: player.x, y: player.y});
        let optLv = getLevel('option'); if(player.history.length > optLv * 15 + 1) player.history.pop();

        if (forceObj.exists) {
            if (forceObj.attached) { forceObj.x = player.x; forceObj.y = player.y - 45; } 
            else if (forceObj.returning) {
                let dx = player.x - forceObj.x; let dy = (player.y - 45) - forceObj.y; let dist = Math.hypot(dx, dy);
                if (dist < 20) { forceObj.attached = true; forceObj.returning = false; } else { forceObj.x += (dx / dist) * 15; forceObj.y += (dy / dist) * 15; }
            } else {
                forceObj.x += forceObj.vx; forceObj.y += forceObj.vy; forceObj.vy *= 0.95; 
                if (forceObj.x < 20) forceObj.x = 20; if (forceObj.x > canvas.width - 20) forceObj.x = canvas.width - 20;
                if (forceObj.y < 20) forceObj.y = 20; if (forceObj.y > canvas.height - 20) forceObj.y = canvas.height - 20;
            }
        }

        if (isCharging) { if (chargeLevel < 300) chargeLevel += 0.5; }

        let fireRate = Math.max(3, 14 - Math.floor(getLevel('fire') * 1)); 
        if (frameCount % fireRate === 0 && !isCharging) { 
            if (powerUpTime > 0) {
                bullets.push({ x: player.x, y: player.y - 20, size: 15, vx: 0, vy: -15, type: 'main', emoji: "💊" });
                bullets.push({ x: player.x - 15, y: player.y - 15, size: 15, vx: -4, vy: -14, type: 'main', emoji: "💊" });
                bullets.push({ x: player.x + 15, y: player.y - 15, size: 15, vx: 4, vy: -14, type: 'main', emoji: "💊" });
            } else {
                bullets.push({ x: player.x - 12, y: player.y - 20, size: 15, vx: 0, vy: -15, type: 'main', emoji: "💊" });
                bullets.push({ x: player.x + 12, y: player.y - 20, size: 15, vx: 0, vy: -15, type: 'main', emoji: "💊" });
            }
            for(let i=1; i<=optLv; i++) { let pos = player.history[i*15]; if(pos) bullets.push({ x: pos.x, y: pos.y - 20, size: 15, vx: 0, vy: -15, type: 'main', emoji: "💊" }); }
        }

        let laserLv = getLevel('laser');
        if (laserLv > 0 && frameCount % Math.max(5, 25 - laserLv * 2) === 0 && !isCharging) { bullets.push({ x: player.x, y: player.y - 30, size: 5, vx: 0, vy: -30, type: 'laser' }); }

        let subBombLv = getLevel('subBomb');
        if (subBombLv > 0 && frameCount % Math.max(30, 90 - subBombLv * 5) === 0 && !isCharging) { bullets.push({ x: player.x, y: player.y, size: 15, vx: 0, vy: -8, type: 'subBomb', targetY: player.y - 100 - (subBombLv * 15), emoji: "🧨" }); }

        let missileLv = getLevel('missile');
        if (missileLv > 0 && frameCount % Math.max(20, 60 - missileLv * 3) === 0 && !isCharging) { bullets.push({ x: player.x, y: player.y, size: 12, vx: (Math.random()-0.5)*10, vy: -5, speed: 10, type: 'missile', emoji: "🚀" }); }

        if (frameCount > 0 && frameCount % bossSpawnInterval === 0) {
            let bossIndex = Math.min(bossEncounterCount, bossList.length - 1);
            let bossInfo = bossList[bossIndex];
            let bossId = Date.now(); 
            
            enemies.push({ 
                x: 250, y: -60, size: bossInfo.size, speed: bossInfo.speed, 
                emoji: bossInfo.emoji, imgAnims: bossInfo.imgAnims,
                hp: bossInfo.hp, maxHp: bossInfo.hp, 
                name: bossInfo.name, color: bossInfo.color, isQuiz: false, isBoss: true, bId: bossId,
                lifetime: 0 
            });
            effects.push({ x: 250, y: 300, text: `⚠️ ${bossInfo.name} 襲来 ⚠️`, life: 120, vy: 0, color: bossInfo.color });
            
            if (bossInfo.parts) {
                bossInfo.parts.forEach(p => {
                    enemies.push({
                        x: 250 + p.baseDx, y: -60 + p.baseDy, size: p.size, speed: 0, 
                        emoji: p.emoji, imgObj: p.imgObj, 
                        hp: p.hp, maxHp: p.hp, name: p.name, 
                        isQuiz: false, isBossPart: true, parentId: bossId, 
                        baseDx: p.baseDx, baseDy: p.baseDy, isLeft: p.isLeft, animPhase: p.animPhase
                    });
                });
            }
            bossEncounterCount++; 
        }

        if (!activeQuiz && frameCount % 600 === 0 && (frameCount % bossSpawnInterval !== 0)) {
            activeQuiz = ynQuizzes[Math.floor(Math.random() * ynQuizzes.length)];
            enemies.push({ x: 150, y: -30, size: 45, speed: 1.5, emoji: "⭕", hp: 3, isQuiz: true, ans: "⭕", invTime: quizInvincibleTime });
            enemies.push({ x: 350, y: -30, size: 45, speed: 1.5, emoji: "❌", hp: 3, isQuiz: true, ans: "❌", invTime: quizInvincibleTime });
        }

        let spawnRate = Math.max(5, 60 - Math.floor(score / (difficultyScale * 0.4))); 
        if (frameCount % spawnRate === 0) {
            let type = Math.random();
            let speedBonus = Math.min(2.5, score / (difficultyScale * 2));
            let baseSpeed = 3 + Math.random() * 2 + speedBonus;
            enemies.push({ x: Math.random() * (canvas.width - 40) + 20, y: -30, size: 35, speed: baseSpeed, emoji: type > 0.8 ? "👾" : "🦠", hp: type > 0.8 ? 4 : 1, isQuiz: false, isBoss: false });
        }

        for (let i = items.length - 1; i >= 0; i--) {
            let item = items[i]; item.y += item.speed;
            if (item.y > canvas.height + 20) { items.splice(i, 1); continue; }
            
            if (checkCollision(item, player, 25)) {
                let type = item.type;
                let limit = (type === 'option') ? MAX_LEVEL_OPTION : (type === 'force' ? MAX_LEVEL_FORCE : MAX_LEVEL);
                
                if (getLevel(type) < limit) {
                    tempUpgrades[type]++; 
                    effects.push({ x: player.x, y: player.y, text: `GET! ${item.emoji}`, life: 40, vy: -1.5, color: "#f1c40f" });
                    
                    if (type === 'force' && !forceObj.exists) { 
                        forceObj.exists = true; forceObj.attached = true; 
                        actionBtn.style.background = "rgba(52, 152, 219, 0.8)"; 
                        actionBtn.innerHTML = `<div style="font-size: 26px;">🛡️</div><div style="font-size: 10px; font-weight: bold; color: white;">CHARGE</div>`; 
                    }
                    if (type === 'bomb' && getLevel('force') === 0) { bombs++; let bd = document.getElementById("bomb-count-disp"); if(bd) bd.innerText = "x" + bombs; }
                    if (type === 'shield') player.shields++;
                } else {
                    earnedCreditsInGame += 50; 
                    effects.push({ x: player.x, y: player.y, text: "+50 C", life: 40, vy: -1.5, color: "#2ecc71" });
                }
                items.splice(i, 1);
            }
        }

        for (let i = enemyBullets.length - 1; i >= 0; i--) {
            let eb = enemyBullets[i]; eb.x += eb.vx; eb.y += eb.vy;
            if (eb.y > canvas.height + 20 || eb.x < -20 || eb.x > canvas.width + 20) { enemyBullets.splice(i, 1); continue; }
            let hitRadiusForce = eb.isSuperHuge ? 70 : (eb.isHuge ? 50 : 35); let hitRadiusPlayer = eb.isSuperHuge ? 35 : (eb.isHuge ? 25 : 15);
            if (forceObj.exists && checkCollision(eb, forceObj, hitRadiusForce)) { enemyBullets.splice(i, 1); effects.push({ x: eb.x, y: eb.y, text: "💥", life: 5, vy: 0, color: "#3498db" }); continue; }
            if (checkCollision(eb, player, hitRadiusPlayer)) { enemyBullets.splice(i, 1); damagePlayer(); }
        }

        for (let i = bullets.length - 1; i >= 0; i--) {
            let b = bullets[i];
            if (b.type === 'missile') {
                let target = null; let minDist = 9999;
                enemies.forEach(e => { if(!e.vanish && e.y < canvas.height && !e.isQuiz) { let d = Math.hypot(e.x - b.x, e.y - b.y); if (d < minDist) { minDist = d; target = e; } } });
                if (target) {
                    let dx = target.x - b.x; let dy = target.y - b.y; let dist = Math.hypot(dx, dy);
                    b.vx += (dx / dist) * 0.8; b.vy += (dy / dist) * 0.8;
                    let currentSpeed = Math.hypot(b.vx, b.vy); b.vx = (b.vx / currentSpeed) * b.speed; b.vy = (b.vy / currentSpeed) * b.speed;
                }
            }
            b.x += b.vx; b.y += b.vy;
            if (b.type === 'subBomb' && b.y <= b.targetY) { blasts.push({ x: b.x, y: b.y, radius: 40 + (getLevel('subBomb') * 5), life: 30, damage: 1 }); bullets.splice(i, 1); continue; }
            if (b.y < -20 || b.x < -20 || b.x > canvas.width + 20) bullets.splice(i, 1);
        }

        for (let i = blasts.length - 1; i >= 0; i--) {
            let blast = blasts[i]; blast.life--;
            if (frameCount % 5 === 0) {
                enemies.forEach(e => {
                    if (e.isQuiz && e.invTime > 0) return;
                    if (!e.vanish && checkCollision(blast, e, blast.radius + (e.size/2))) { e.hp -= blast.damage; if(e.hp <= 0 && !e.vanish) killEnemy(e); }
                });
            }
            if (blast.life <= 0) blasts.splice(i, 1);
        }

        let bitCount = getLevel('bit');
        if (bitCount > 0 && frameCount % 10 === 0) { 
            for(let i=0; i<bitCount; i++) {
                let angle = frameCount * 0.05 + (i * Math.PI * 2 / bitCount);
                let bx = player.x + Math.cos(angle) * 60; let by = player.y + Math.sin(angle) * 60;
                for(let j=enemyBullets.length-1; j>=0; j--) { if(checkCollision({x:bx, y:by}, enemyBullets[j], 25)) { enemyBullets.splice(j, 1); effects.push({ x: bx, y: by, text: "✨", life: 5, vy: 0, color: "#fff" }); } }
                enemies.forEach(e => {
                    if (e.isQuiz && e.invTime > 0) return;
                    if (!e.vanish && checkCollision({x:bx, y:by}, e, 35)) { e.hp -= 2; effects.push({ x: e.x, y: e.y, text: "💥", life: 5, vy: -1, color: "#fff" }); if(e.hp <= 0 && !e.vanish) killEnemy(e); }
                });
            }
        }

        if (forceObj.exists && frameCount % 5 === 0) {
            enemies.forEach(e => {
                if (e.isQuiz && e.invTime > 0) return;
                if (!e.vanish && checkCollision(e, forceObj, (e.isBoss ? e.size/2 : 25) + 20)) { e.hp -= 2 + getLevel('force'); effects.push({ x: e.x + (Math.random()*40-20), y: e.y + (Math.random()*40-20), text: "💥", life: 5, vy: -1, color: "#3498db" }); if (e.hp <= 0 && !e.vanish) killEnemy(e); }
            });
        }

        if (waveCannon.active) {
            waveCannon.life--;
            enemies.forEach(e => {
                if (e.isQuiz && e.invTime > 0) return;
                if (!e.vanish && e.y < player.y && Math.abs(e.x - player.x) < (waveCannon.width/2 + e.size/2)) { e.hp -= waveCannon.damage; effects.push({ x: e.x + (Math.random()*40-20), y: e.y, text: "💥", life: 5, vy: -1, color: "#fff" }); if (e.hp <= 0 && !e.vanish) killEnemy(e); }
            });
            if (waveCannon.life <= 0) waveCannon.active = false;
        }

        let activeBosses = {}; enemies.forEach(e => { if(e.isBoss) activeBosses[e.bId] = e; });

        for (let i = enemies.length - 1; i >= 0; i--) {
            let enemy = enemies[i];
            
            if (enemy.isBossPart) {
                let parent = activeBosses[enemy.parentId];
                if (!parent || parent.vanish) {
                    if (!enemy.vanish) { enemy.vanish = true; effects.push({ x: enemy.x, y: enemy.y, text: "💥", life: 30, vy: -1, color: "#fff" }); }
                    enemies.splice(i, 1); continue;
                }
                let animOffset = Math.sin(frameCount * 0.05 + enemy.animPhase) * 15;
                let actualDx = enemy.isLeft ? enemy.baseDx - animOffset : enemy.baseDx + animOffset;
                enemy.x = parent.x + actualDx; enemy.y = parent.y + enemy.baseDy + Math.cos(frameCount * 0.05) * 5;
                
                if (frameCount % 80 === 0 && enemy.y > 0 && enemy.y < 300) {
                    let dx = player.x - enemy.x; let dy = player.y - enemy.y; let dist = Math.hypot(dx, dy);
                    enemyBullets.push({ x: enemy.x, y: enemy.y, vx: (dx/dist)*4, vy: (dy/dist)*4, emoji: "🟢" });
                }
            } 
            else {
                if (!enemy.isBoss) {
                    enemy.y += enemy.speed;
                } else {
                    enemy.lifetime = (enemy.lifetime || 0) + 1;
                    let stayTime = 1200; 
                    if (enemy.y < 120 || enemy.lifetime > stayTime) { 
                        enemy.y += enemy.speed; 
                    }
                }

                if (enemy.isQuiz && enemy.invTime > 0) enemy.invTime--;

                if (enemy.isBoss) { 
                    // 🌟 ボス共通の「ゆらゆら＋じわじわ追尾」計算
                    // ボスのスピードに合わせて揺れの速さと幅が変わります
                    let trackingSpeed = 0.008; 
                    let swaySpeed = 0.02 + (enemy.speed * 0.02); 
                    let swayAmount = 1.5 + enemy.speed; 
                    let baseMoveX = (player.x - enemy.x) * trackingSpeed + Math.sin(enemy.lifetime * swaySpeed) * swayAmount;

                    if (enemy.imgAnims && enemy.imgAnims.length >= 3) {
                        
                        if (enemy.name.includes("一人称オラ")) {
                            let cycleLength = 600; 
                            let phase1End = 120; 
                            let phase2End = 180; 
                            let phase3End = 240; 
                            let phase4End = 420; 
                            
                            let cycle = enemy.lifetime % cycleLength; 
                            
                            if (cycle < phase1End) {
                                enemy.animState = 0; 
                                enemy.x += baseMoveX; // 🌟 揺れ＋追尾
                                enemy.isFiringBeam = false;
                            } else if (cycle < phase2End) {
                                enemy.animState = 1; 
                                enemy.x += baseMoveX + (Math.random() - 0.5) * 4; // 🌟 揺れ＋追尾＋震え
                                enemy.y += (Math.random() - 0.5) * 4;
                                enemy.isFiringBeam = false;
                            } else if (cycle < phase3End) {
                                enemy.animState = 2; 
                                enemy.x += baseMoveX * 0.8; // 🌟 放射中は少し動きを抑える
                                enemy.isFiringBeam = false;
                                
                                if (cycle % 5 === 0 && enemy.y > 0 && enemy.y < canvas.height) {
                                    let angleBase = cycle * 0.15;
                                    for (let a = 0; a < Math.PI * 2; a += Math.PI / 4) {
                                        enemyBullets.push({ x: enemy.x, y: enemy.y, vx: Math.cos(angleBase + a)*4.5, vy: Math.sin(angleBase + a)*4.5, emoji: "🧿" });
                                    }
                                }
                            } else if (cycle < phase4End) {
                                enemy.animState = 3; 
                                enemy.isFiringBeam = false;
                                
                                enemy.x += baseMoveX * 0.5 + (Math.random() - 0.5) * 8; // 🌟 チャージ中は追尾を鈍くして激しく震える
                                enemy.y += (Math.random() - 0.5) * 4;
                                
                                if (cycle % 3 === 0) {
                                    let effX = enemy.x + (Math.random() - 0.5) * 150;
                                    let effY = enemy.y + 30 + Math.random() * 100;
                                    effects.push({ x: effX, y: effY, text: "⚡", life: 10, vy: -6, color: "#00ffff" });
                                }
                                
                                if (cycle === phase3End) {
                                    effects.push({ x: enemy.x, y: enemy.y - 80, text: "⚠️ ENERGY CHARGE ⚠️", life: 180, vy: 0, color: "#f1c40f" });
                                }
                                if (cycle % 20 === 0) screenFlash = 4; 
                            } else {
                                enemy.animState = 4; 
                                enemy.isFiringBeam = true; 
                                
                                enemy.x += baseMoveX * 0.3 + (Math.random() - 0.5) * 4; // 🌟 ビーム中もゆっくり追尾＋振動
                                
                                if (cycle === phase4End && enemy.y < canvas.height) {
                                    screenFlash = 25;
                                    effects.push({ x: enemy.x, y: enemy.y + 50, text: "💥 EXTREME BEAM 💥", life: 90, vy: -0.5, color: "#e74c3c" });
                                }
                                
                                let beamWidth = 120;
                                if (player.y > enemy.y && Math.abs(player.x - enemy.x) < beamWidth / 2) {
                                    if (frameCount % 4 === 0) damagePlayer(); 
                                }
                            }
                        } else {
                            let cycleLength = 240; 
                            let waitEnd = 160;     
                            let chargeEnd = 200;   

                            let cycle = enemy.lifetime % cycleLength; 
                            
                            if (cycle < waitEnd) {
                                enemy.animState = 0; 
                                enemy.x += baseMoveX; 
                            } else if (cycle < chargeEnd) {
                                enemy.animState = 1; 
                                enemy.x += baseMoveX + (Math.random() - 0.5) * 4.0; 
                            } else {
                                enemy.animState = 2; 
                                enemy.x += baseMoveX * 0.5; // 発射時は追尾を鈍らせる
                                
                                if (cycle === chargeEnd && enemy.y > 0 && enemy.y < canvas.height) {
                                    if (enemy.name.includes("超過勤務チェッカー")) {
                                        enemyBullets.push({ x: enemy.x, y: enemy.y + 20, vx: 0, vy: 14, emoji: "☄️", isSuperHuge: true });
                                        for (let angle = 0; angle <= Math.PI; angle += Math.PI/4) {
                                            enemyBullets.push({ x: enemy.x, y: enemy.y + 20, vx: Math.cos(angle)*8, vy: Math.sin(angle)*8, emoji: "🔥", isHuge: true });
                                            enemyBullets.push({ x: enemy.x, y: enemy.y + 20, vx: Math.cos(angle)*5, vy: Math.sin(angle)*5, emoji: "⚡", isHuge: false });
                                        }
                                        screenFlash = 25; 
                                        effects.push({ x: enemy.x, y: enemy.y + 30, text: "🌟 BIG BANG 🌟", life: 60, vy: -1, color: "#f1c40f" });
                                    } else {
                                        enemyBullets.push({ x: enemy.x, y: enemy.y + 20, vx: 0, vy: 12, emoji: "☄️", isSuperHuge: true });
                                        screenFlash = 10;
                                        effects.push({ x: enemy.x, y: enemy.y + 30, text: "💨", life: 20, vy: 1, color: "#fff" });
                                    }
                                }
                                
                                if (cycle >= chargeEnd && cycle <= chargeEnd + 4) { 
                                    enemy.y -= 6; 
                                } else if (cycle > chargeEnd + 4 && enemy.lifetime <= 1800) { 
                                    enemy.y += (120 - enemy.y) * 0.05; 
                                }
                            }
                        }
                    } else {
                        enemy.x += baseMoveX; // 🌟 3枚アニメなしのボスもゆらゆら追従
                        
                        if (enemy.lifetime % 60 === 0 && enemy.y > 0 && enemy.y < canvas.height) {
                            enemyBullets.push({ x: enemy.x, y: enemy.y, vx: -2, vy: 5, emoji: "🔴" });
                            enemyBullets.push({ x: enemy.x, y: enemy.y, vx: 0, vy: 6, emoji: "🔴" });
                            enemyBullets.push({ x: enemy.x, y: enemy.y, vx: 2, vy: 5, emoji: "🔴" });
                        }
                    }
                } 
            }

            if (enemy.y > canvas.height + 30 + (enemy.size/2)) { if (enemy.isQuiz) activeQuiz = null; enemies.splice(i, 1); continue; }

            for (let j = bullets.length - 1; j >= 0; j--) {
                let bullet = bullets[j];
                let hitRadius = enemy.isBoss ? (enemy.size / 2) + 10 : (enemy.isBossPart ? enemy.size / 2 + 5 : 25);
                if (checkCollision(enemy, bullet, hitRadius)) {
                    if (enemy.isQuiz && enemy.invTime > 0) { bullets.splice(j, 1); effects.push({ x: bullet.x, y: bullet.y - 10, text: "🛡️", life: 5, vy: -1, color: "#fff" }); continue; }
                    if (bullet.type !== 'laser') bullets.splice(j, 1); 
                    enemy.hp -= (bullet.type === 'laser' ? 0.5 : 1);
                    if(Math.random() > 0.5) effects.push({ x: enemy.x + (Math.random()*40-20), y: enemy.y + (Math.random()*40-20), text: "💥", life: 5, vy: -1, color: "#fff" });
                    if (enemy.hp <= 0 && !enemy.vanish) { killEnemy(enemy); break; }
                }
            }

            if (enemy.vanish) { enemies.splice(i, 1); continue; }

            let playerHitRadius = enemy.isBoss ? (enemy.size / 2) : 15;
            if (enemies[i] && checkCollision(enemy, player, playerHitRadius)) {
                let isDead = damagePlayer();
                if (!isDead && !enemy.isBoss && !enemy.isBossPart) { enemy.hp = 0; killEnemy(enemy); }
            }
        }

        for (let i = effects.length - 1; i >= 0; i--) { effects[i].y += effects[i].vy; effects[i].life--; if (effects[i].life <= 0) effects.splice(i, 1); }
    }

    function draw() {
        ctx.fillStyle = "#000000"; ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = "#3498db"; stars.forEach(s => { ctx.beginPath(); ctx.arc(s.x, s.y, s.size, 0, Math.PI * 2); ctx.fill(); });

        if (isBombing > 0) { ctx.fillStyle = `rgba(255, 255, 255, ${isBombing / 40})`; ctx.fillRect(0, 0, canvas.width, canvas.height); }
        if (screenFlash > 0) { ctx.fillStyle = `rgba(255, 255, 255, ${screenFlash / 15})`; ctx.fillRect(0, 0, canvas.width, canvas.height); }

        if (waveCannon.active) {
            ctx.fillStyle = `rgba(52, 152, 219, ${Math.min(1.0, waveCannon.life/10)})`; ctx.shadowColor = "#00ffff"; ctx.shadowBlur = 20;
            ctx.fillRect(player.x - waveCannon.width/2, 0, waveCannon.width, player.y); ctx.fillStyle = `rgba(255, 255, 255, 0.9)`;
            ctx.fillRect(player.x - waveCannon.width/4, 0, waveCannon.width/2, player.y); ctx.shadowBlur = 0;
        }

        blasts.forEach(b => { ctx.fillStyle = `rgba(231, 76, 60, ${b.life / 30})`; ctx.beginPath(); ctx.arc(b.x, b.y, b.radius, 0, Math.PI*2); ctx.fill(); });

        let optLv = getLevel('option');
        if (optLv > 0) {
            ctx.font = "25px Arial"; ctx.textAlign = "center"; ctx.textBaseline = "middle";
            for(let i=1; i<=optLv; i++) { let pos = player.history[i*15]; if(pos) { ctx.save(); ctx.shadowColor = "#e67e22"; ctx.shadowBlur = 10; ctx.fillText("🟠", pos.x, pos.y); ctx.restore(); } }
        }
        
        ctx.textAlign = "center"; ctx.textBaseline = "middle";
        items.forEach(item => {
            ctx.save(); ctx.shadowColor = "#f1c40f"; ctx.shadowBlur = 15; ctx.fillStyle = "rgba(241, 196, 15, 0.4)";
            ctx.beginPath(); ctx.arc(item.x, item.y, 18, 0, Math.PI*2); ctx.fill(); ctx.restore();
            ctx.font = "20px Arial"; ctx.fillText(item.emoji, item.x, item.y);
        });

        bullets.forEach(b => { 
            if (b.type === 'laser') { ctx.fillStyle = "#00ffff"; ctx.shadowColor = "#00ffff"; ctx.shadowBlur = 10; ctx.fillRect(b.x - 2, b.y, 4, 30); ctx.shadowBlur = 0; } 
            else { ctx.font = "20px Arial"; ctx.fillText(b.emoji, b.x, b.y); }
        });

        enemyBullets.forEach(eb => { 
            if (eb.isSuperHuge) { ctx.font = "80px Arial"; }
            else if (eb.isHuge) { ctx.font = "40px Arial"; }
            else { ctx.font = "15px Arial"; }
            ctx.fillText(eb.emoji, eb.x, eb.y); 
        });
        
        enemies.forEach(e => { 
            if (e.isBoss) {
                if (e.isFiringBeam) {
                    ctx.save();
                    ctx.globalCompositeOperation = "lighter"; 
                    ctx.shadowColor = "#ff0000";
                    ctx.shadowBlur = 30;
                    
                    let beamWidth = 120 + (Math.random() * 20 - 10);
                    
                    ctx.fillStyle = `rgba(255, 50, 0, 0.8)`;
                    ctx.fillRect(e.x - beamWidth/2, e.y, beamWidth, canvas.height);
                    
                    ctx.fillStyle = "#ffffff";
                    ctx.fillRect(e.x - beamWidth/4, e.y, beamWidth/2, canvas.height);
                    
                    ctx.restore();
                }

                let currentImgObj = null;
                if (e.imgAnims && e.imgAnims.length > 0) {
                    let animIndex = 0;
                    if (e.animState !== undefined && e.animState < e.imgAnims.length) { animIndex = e.animState; } 
                    else { animIndex = Math.floor(frameCount / 15) % e.imgAnims.length; }
                    let candidate = e.imgAnims[animIndex];
                    if (candidate && candidate.isLoaded) { currentImgObj = candidate.img; } 
                    else if (e.imgAnims[0] && e.imgAnims[0].isLoaded) { currentImgObj = e.imgAnims[0].img; }
                }

                if (currentImgObj) { ctx.drawImage(currentImgObj, e.x - e.size, e.y - e.size, e.size * 2, e.size * 2); } 
                else { ctx.font = e.size + "px Arial"; ctx.fillText(e.emoji, e.x, e.y); }
                
                ctx.fillStyle = e.color || "#fff"; ctx.font = "bold 14px Arial"; ctx.fillText(e.name, e.x, e.y - e.size/2 - 45);
                ctx.fillStyle = "#e74c3c"; ctx.fillRect(e.x - 50, e.y - e.size/2 - 35, 100, 8);
                ctx.fillStyle = "#2ecc71"; ctx.fillRect(e.x - 50, e.y - e.size/2 - 35, 100 * (e.hp / e.maxHp), 8);
            } else if (e.isBossPart) {
                if (e.imgObj && e.imgObj.isLoaded) { ctx.drawImage(e.imgObj.img, e.x - e.size, e.y - e.size, e.size * 2, e.size * 2); } 
                else { ctx.font = e.size + "px Arial"; ctx.fillText(e.emoji, e.x, e.y); }
                
                ctx.fillStyle = "#e74c3c"; ctx.fillRect(e.x - 20, e.y - e.size/2 - 20, 40, 5);
                ctx.fillStyle = "#f1c40f"; ctx.fillRect(e.x - 20, e.y - e.size/2 - 20, 40 * (e.hp / e.maxHp), 5);
                ctx.fillStyle = "#fff"; ctx.font = "10px Arial"; ctx.fillText(e.name, e.x, e.y - e.size/2 - 25);
            } else if (e.isQuiz) { 
                if (e.invTime > 0) {
                    ctx.globalAlpha = 0.5 + Math.sin(frameCount * 0.3) * 0.5; ctx.font = e.size + "px Arial"; ctx.fillText(e.emoji, e.x, e.y); ctx.globalAlpha = 1.0;
                    ctx.fillStyle = "#f1c40f"; ctx.font = "bold 16px Arial"; ctx.fillText("WAIT!", e.x, e.y - 35);
                } else {
                    ctx.font = e.size + "px Arial"; ctx.fillText(e.emoji, e.x, e.y); ctx.fillStyle = "#fff"; ctx.font = "bold 16px Arial"; ctx.fillText("撃て!", e.x, e.y - 35); 
                }
            } else {
                ctx.font = e.size + "px Arial"; ctx.fillText(e.emoji, e.x, e.y); 
            }
        });
        
        if (!isGameOver) { 
            ctx.font = "45px Arial"; 
            if (player.invincible > 0 && Math.floor(frameCount / 5) % 2 === 0) ctx.globalAlpha = 0.3;
            if (powerUpTime > 0) { ctx.save(); ctx.shadowColor = "#f1c40f"; ctx.shadowBlur = 20; ctx.fillStyle = "rgba(241, 196, 15, 0.3)"; ctx.beginPath(); ctx.arc(player.x, player.y, 35, 0, Math.PI*2); ctx.fill(); ctx.restore(); }
            if (player.shields > 0) { ctx.save(); ctx.shadowColor = "#3498db"; ctx.shadowBlur = 15; ctx.fillStyle = "rgba(52, 152, 219, 0.2)"; ctx.strokeStyle = "rgba(52, 152, 219, 0.8)"; ctx.lineWidth = 3; ctx.beginPath(); ctx.arc(player.x, player.y, 35, 0, Math.PI*2); ctx.fill(); ctx.stroke(); ctx.restore(); }
            
            if (isCharging) { ctx.save(); ctx.shadowColor = "#3498db"; ctx.shadowBlur = 15; ctx.beginPath(); ctx.arc(player.x, player.y - 20, 20 + chargeLevel/6, 0, Math.PI*2); ctx.fillStyle = `rgba(52, 152, 219, ${chargeLevel/300 * 0.5})`; ctx.fill(); ctx.strokeStyle = "#00ffff"; ctx.lineWidth = 2 + chargeLevel/50; ctx.stroke(); ctx.restore(); }
            
            ctx.fillText(player.emoji, player.x, player.y); ctx.globalAlpha = 1.0;
            
            if (forceObj.exists) { ctx.save(); ctx.shadowColor = "#3498db"; ctx.shadowBlur = 15; ctx.font = "35px Arial"; ctx.fillText("🛡️", forceObj.x, forceObj.y); ctx.restore(); }

            let bitCount = getLevel('bit');
            if (bitCount > 0) {
                for(let i=0; i<bitCount; i++) {
                    let angle = frameCount * 0.05 + (i * Math.PI * 2 / bitCount); let bx = player.x + Math.cos(angle) * 60; let by = player.y + Math.sin(angle) * 60;
                    ctx.font = "20px Arial"; ctx.fillText("🛸", bx, by);
                }
            }
        }

        effects.forEach(eff => {
            ctx.globalAlpha = eff.life / 20; ctx.fillStyle = eff.color || "#ffffff";
            let fontSize = eff.text.includes("BOSS") || eff.text.includes("破壊") || eff.text.includes("BOMB") || eff.text.includes("波動砲") ? 28 : (eff.text.includes("解放") || eff.text.includes("正解ボーナス") || eff.text.includes("不正解") ? 32 : 24);
            ctx.font = "bold " + fontSize + "px Arial"; ctx.fillText(eff.text, eff.x, eff.y); ctx.globalAlpha = 1.0;
        });

        if (activeQuiz) {
            ctx.fillStyle = "rgba(44, 62, 80, 0.85)"; ctx.strokeStyle = "#f1c40f"; ctx.lineWidth = 2; awake = null; ctx.beginPath(); ctx.roundRect(25, 15, 450, 75, 10); ctx.fill(); ctx.stroke();
            ctx.fillStyle = "#f1c40f"; ctx.font = "bold 14px Arial"; ctx.fillText("🎯 ボーナス・クイズ (正解を撃破でパワーアップ！)", 250, 35);
            ctx.fillStyle = "#ffffff"; ctx.font = "bold 16px Arial"; ctx.fillText(activeQuiz.q, 250, 65);
        }
        ctx.fillStyle = "#ffffff"; ctx.textAlign = "left"; ctx.font = "bold 20px Arial"; ctx.fillText("SCORE: " + score, 15, 30);
    }
    function loop() { update(); draw(); gameLoopId = requestAnimationFrame(loop); }
</script>
</body>
</html>
"""

html_code = html_code.replace("__B64_BOSS_01_A__", b64_1_a)
html_code = html_code.replace("__B64_BOSS_01_B__", b64_1_b)
html_code = html_code.replace("__B64_BOSS_01_C__", b64_1_c)

html_code = html_code.replace("__B64_BOSS_02__", b64_2)

html_code = html_code.replace("__B64_BOSS_03_L__", b64_3_L)
html_code = html_code.replace("__B64_BOSS_03_R__", b64_3_R)
html_code = html_code.replace("__B64_BOSS_03__", b64_3)

html_code = html_code.replace("__B64_BOSS_04_A__", b64_4_a)
html_code = html_code.replace("__B64_BOSS_04_B__", b64_4_b)
html_code = html_code.replace("__B64_BOSS_04__", b64_4)

html_code = html_code.replace("__B64_BOSS_05__", b64_5)

html_code = html_code.replace("__B64_BOSS_06_A__", b64_6_a)
html_code = html_code.replace("__B64_BOSS_06_B__", b64_6_b)
html_code = html_code.replace("__B64_BOSS_06_C__", b64_6_c)
html_code = html_code.replace("__B64_BOSS_06_D__", b64_6_d)
html_code = html_code.replace("__B64_BOSS_06__", b64_6)

html_code = html_code.replace("__B64_BOSS_07__", b64_7)
html_code = html_code.replace("__B64_BOSS_08__", b64_8)
html_code = html_code.replace("__B64_BOSS_09__", b64_9)
html_code = html_code.replace("__B64_BOSS_10__", b64_10)

components.html(html_code, height=900)