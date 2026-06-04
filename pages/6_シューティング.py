import streamlit as st
import streamlit.components.v1 as components
import base64
import os

st.set_page_config(page_title="シューティング プロトタイプ", page_icon="🚀", layout="wide")

st.markdown(
    "<h1 style='font-size: 32px; margin-bottom: 0px;'>🚀 メディカル・ストライカー V10.2</h1>", 
    unsafe_allow_html=True
)
st.markdown(
    "<p style='font-size: 16px; color: #555;'>【UI修正完了】ゲーム画面（キャンバス）をスワイプして画面の位置調整ができるようになりました！</p>", 
    unsafe_allow_html=True
)

def get_image_base64(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    return "" 

b64_1 = get_image_base64("pages/images/boss1.png")
b64_2 = get_image_base64("pages/images/boss2.png")
b64_3 = get_image_base64("pages/images/boss3.png")
b64_4 = get_image_base64("pages/images/boss4.png")
b64_5 = get_image_base64("pages/images/boss5.png")
b64_6 = get_image_base64("pages/images/boss6.png")
b64_7 = get_image_base64("pages/images/boss7.png")
b64_8 = get_image_base64("pages/images/boss8.png")
b64_9 = get_image_base64("pages/images/boss9.png")
b64_10 = get_image_base64("pages/images/boss10.png")

html_code = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
    body { 
        margin: 0; background: #2c3e50; display: flex; flex-direction: column; align-items: center; 
        font-family: 'Helvetica Neue', Arial, sans-serif; 
        /* 🌟 ここから overflow: hidden; と touch-action: none; を削除してスクロールを許可！ */
        user-select: none; -webkit-user-select: none;
    }
    
    #game-container { 
        position: relative; width: 100%; max-width: 500px; 
        min-height: 750px; 
        background: #000; border: 4px solid #34495e; border-radius: 8px; overflow: hidden; 
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        display: flex; flex-direction: column;
    }
    
    #hanger-screen {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: #1a252f; color: white; display: flex; flex-direction: column;
        padding: 15px; box-sizing: border-box; z-index: 50;
    }
    .upg-item {
        background: rgba(255,255,255,0.05); border-left: 5px solid #f1c40f;
        padding: 8px 12px; border-radius: 8px; margin-bottom: 8px;
        display: flex; justify-content: space-between; align-items: center;
    }
    .upg-title { font-weight: 900; font-size: 14px; margin-bottom: 2px; color: #fff;}
    .upg-desc { font-size: 10px; color: #bdc3c7; font-weight: bold; }
    .upg-btn {
        background: #f1c40f; color: #2c3e50; border: none; padding: 8px 10px; 
        border-radius: 8px; font-weight: 900; font-size: 12px; cursor: pointer;
        box-shadow: 0 3px 0 #d35400; transition: 0.1s; min-width: 70px; text-align: center;
    }
    .upg-btn:active:not(:disabled) { transform: translateY(3px); box-shadow: 0 0 0 #d35400; }
    .upg-btn:disabled { background: #7f8c8d; box-shadow: 0 3px 0 #34495e; color: #bdc3c7; cursor: not-allowed; }

    canvas { 
        width: 100%; max-width: 500px; aspect-ratio: 500 / 666; 
        display: none; margin: 0 auto;
    }
    
    #controls-container {
        display: none; width: 100%; background: #1a252f; border-top: 2px solid #34495e; 
        padding: 10px 20px; box-sizing: border-box; justify-content: space-between; align-items: center; z-index: 20;
    }
    
    #joystick-zone {
        display: flex; 
        touch-action: none; /* 🌟 ジョイスティック操作時だけはスクロールさせない */
        width: 110px; height: 110px; background: rgba(255, 255, 255, 0.1); border-radius: 50%; 
        justify-content: center; align-items: center; border: 2px solid rgba(255,255,255,0.2); margin: 0; position: relative;
    }
    #joystick-knob {
        width: 45px; height: 45px; background: rgba(52, 152, 219, 0.8);
        border-radius: 50%; position: absolute; box-shadow: 0 4px 10px rgba(0,0,0,0.5); pointer-events: none;
    }
    
    #action-btn {
        display: flex; 
        touch-action: none; /* 🌟 ボタン操作時だけはスクロールさせない */
        width: 80px; height: 80px; background: rgba(231, 76, 60, 0.8);
        border-radius: 50%; flex-direction: column; justify-content: center; align-items: center;
        border: 2px solid rgba(255,255,255,0.3); cursor: pointer; box-shadow: 0 4px 10px rgba(0,0,0,0.5); margin: 0; position: relative;
    }
    #action-btn:active { transform: scale(0.95); }

    #overlay { 
        display: none; position: absolute; top: 0; left: 0; width: 100%; height: 100%; 
        background: rgba(0,0,0,0.85); z-index: 30; flex-direction: column; 
        justify-content: center; align-items: center; text-align: center; color: white;
    }
    .btn { border: none; border-radius: 8px; padding: 12px; font-size: 16px; font-weight: 900; cursor: pointer; }
    .start-btn { background: #3498db; color: white; box-shadow: 0 4px 0 #2980b9; margin-top: auto; }
    .start-btn:active { transform: translateY(4px); box-shadow: 0 0 0 #2980b9; }
</style>
</head>
<body>
<div id="game-container">
    
    <div id="hanger-screen">
        <h2 style="color: #f1c40f; text-align: center; margin-top: 0px; margin-bottom: 5px; font-size: 22px;">🛠️ 基地ハンガー</h2>
        <div style="text-align: center; margin-bottom: 10px; background: rgba(0,0,0,0.4); padding: 5px; border-radius: 8px;">
            <span style="font-size: 12px; color: #bdc3c7;">所持クレジット</span><br>
            <span id="display-credits" style="font-size: 24px; font-weight: 900; color: #2ecc71;">0</span> <span style="font-size: 14px;">C</span>
        </div>
        
        <div style="flex-grow: 1; overflow-y: auto;">
            <div class="upg-item"><div><div class="upg-title">🔫 連射速度UP (Lv.<span id="lvl-fire"></span>)</div><div class="upg-desc">主砲の発射間隔が劇的に短縮</div></div><button class="upg-btn" id="btn-fire" onclick="buyUpgrade('fire')">100 C</button></div>
            <div class="upg-item"><div><div class="upg-title">⚡ 貫通レーザー (Lv.<span id="lvl-laser"></span>)</div><div class="upg-desc">敵を貫く高威力の光線を自動発射</div></div><button class="upg-btn" id="btn-laser" onclick="buyUpgrade('laser')">100 C</button></div>
            <div class="upg-item"><div><div class="upg-title">🧨 対地サブボム (Lv.<span id="lvl-subBomb"></span>)</div><div class="upg-desc">前方に爆風を発生させる(ゼビウス風)</div></div><button class="upg-btn" id="btn-subBomb" onclick="buyUpgrade('subBomb')">100 C</button></div>
            <div class="upg-item"><div><div class="upg-title">🚀 追尾ミサイル (Lv.<span id="lvl-missile"></span>)</div><div class="upg-desc">敵を自動で追いかけるミサイルを発射</div></div><button class="upg-btn" id="btn-missile" onclick="buyUpgrade('missile')">100 C</button></div>
            
            <div class="upg-item"><div><div class="upg-title">🛸 防衛ビット (Lv.<span id="lvl-bit"></span>)</div><div class="upg-desc">自機の周りを回り敵を攻撃(R-TYPEビット風)</div></div><button class="upg-btn" id="btn-bit" onclick="buyUpgrade('bit')">100 C</button></div>
            <div class="upg-item"><div><div class="upg-title">🟠 追従オプション (Lv.<span id="lvl-option"></span>)</div><div class="upg-desc">自機の軌跡を追い主砲を撃つ(グラディウス風)</div></div><button class="upg-btn" id="btn-option" onclick="buyUpgrade('option')">200 C</button></div>
            
            <div class="upg-item"><div><div class="upg-title">💨 移動速度UP (Lv.<span id="lvl-speed"></span>)</div><div class="upg-desc">ジョイスティック操作時の速度上昇</div></div><button class="upg-btn" id="btn-speed" onclick="buyUpgrade('speed')">100 C</button></div>
            <div class="upg-item"><div><div class="upg-title">🛡️ バリア装備 (Lv.<span id="lvl-shield"></span>)</div><div class="upg-desc">被弾を無効化するシールド (1回/Lv)</div></div><button class="upg-btn" id="btn-shield" onclick="buyUpgrade('shield')">100 C</button></div>
            
            <div class="upg-item" style="border-left: 5px solid #e74c3c;"><div><div class="upg-title" style="color:#e74c3c;">🔥 必殺ボム増量 (Lv.<span id="lvl-bomb"></span>)</div><div class="upg-desc">画面一掃の必殺技 (初期2発 + 1発/Lv)</div></div><button class="upg-btn" id="btn-bomb" onclick="buyUpgrade('bomb')">200 C</button></div>
            
            <div class="upg-item" style="border-left: 5px solid #3498db; background: rgba(52,152,219,0.1);"><div><div class="upg-title" style="color:#3498db;">🔵 フォース＆波動砲 (Lv.<span id="lvl-force"></span>)</div><div class="upg-desc">着脱式の盾＆長押し波動砲(※必殺ボムと排他)</div></div><button class="upg-btn" id="btn-force" onclick="buyUpgrade('force')">300 C</button></div>
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
    const canvas = document.getElementById("gameCanvas");
    const ctx = canvas.getContext("2d");
    const overlay = document.getElementById("overlay");
    const hanger = document.getElementById("hanger-screen");
    const actionBtn = document.getElementById("action-btn");
    const controls = document.getElementById("controls-container");
    
    // ジョイスティック
    const joyZone = document.getElementById("joystick-zone");
    const joyKnob = document.getElementById("joystick-knob");
    let isDragging = false; let joyDx = 0; let joyDy = 0; const maxRadius = 35; 

    function handleJoyStart(e) { isDragging = true; handleJoyMove(e); }
    function handleJoyMove(e) {
        if (!isDragging) return; e.preventDefault();
        let clientX = e.touches ? e.touches[0].clientX : e.clientX;
        let clientY = e.touches ? e.touches[0].clientY : e.clientY;
        const rect = joyZone.getBoundingClientRect();
        let dx = clientX - (rect.left + rect.width / 2); let dy = clientY - (rect.top + rect.height / 2);
        let distance = Math.hypot(dx, dy);
        if (distance > maxRadius) { dx = (dx / distance) * maxRadius; dy = (dy / distance) * maxRadius; }
        joyKnob.style.transform = `translate(${dx}px, ${dy}px)`;
        joyDx = dx / maxRadius; joyDy = dy / maxRadius;
    }
    function handleJoyEnd(e) { isDragging = false; joyDx = 0; joyDy = 0; joyKnob.style.transform = `translate(0px, 0px)`; }

    joyZone.addEventListener("touchstart", handleJoyStart, {passive: false});
    joyZone.addEventListener("touchmove", handleJoyMove, {passive: false});
    joyZone.addEventListener("touchend", handleJoyEnd);
    joyZone.addEventListener("mousedown", handleJoyStart);
    window.addEventListener("mousemove", handleJoyMove);
    window.addEventListener("mouseup", handleJoyEnd);

    // ==========================================================================
    // 🌟 画像アセットの初期化関数
    // ==========================================================================
    function createBossImgObj(b64_string) {
        let obj = { img: new Image(), isLoaded: false };
        if (b64_string && b64_string !== "") {
            obj.img.src = "data:image/png;base64," + b64_string;
            obj.img.onload = () => { obj.isLoaded = true; };
        }
        return obj;
    }

    const bossImg1 = createBossImgObj("__B64_BOSS_01__");
    const bossImg2 = createBossImgObj("__B64_BOSS_02__");
    const bossImg3 = createBossImgObj("__B64_BOSS_03__");
    const bossImg4 = createBossImgObj("__B64_BOSS_04__");
    const bossImg5 = createBossImgObj("__B64_BOSS_05__");
    const bossImg6 = createBossImgObj("__B64_BOSS_06__");
    const bossImg7 = createBossImgObj("__B64_BOSS_07__");
    const bossImg8 = createBossImgObj("__B64_BOSS_08__");
    const bossImg9 = createBossImgObj("__B64_BOSS_09__");
    const bossImg10 = createBossImgObj("__B64_BOSS_10__");

    const bossList = [
        { name: "LV1: 狂乱のバナナ", imgObj: bossImg1, emoji: "🍌", hp: 80, speed: 0.5, size: 80, color: "#f1c40f" },
        { name: "LV2: 暴走ナノクローラー", imgObj: bossImg2, emoji: "🕷️", hp: 150, speed: 0.6, size: 85, color: "#9b59b6" },
        { name: "LV3: 猛毒スコーピオン", imgObj: bossImg3, emoji: "🦂", hp: 250, speed: 0.7, size: 90, color: "#e67e22" },
        { name: "LV4: 変異バクテリオファージ", imgObj: bossImg4, emoji: "🧬", hp: 400, speed: 0.8, size: 95, color: "#2ecc71" },
        { name: "LV5: 漆黒のネクロセル", imgObj: bossImg5, emoji: "💀", hp: 600, speed: 0.5, size: 100, color: "#95a5a6" },
        { name: "LV6: 監視者 ジ・アイ", imgObj: bossImg6, emoji: "👁️", hp: 850, speed: 0.4, size: 110, color: "#e74c3c" },
        { name: "LV7: 地球外病原体 X", imgObj: bossImg7, emoji: "👽", hp: 1200, speed: 1.0, size: 90, color: "#2ecc71" },
        { name: "LV8: 殺戮機兵 オメガ", imgObj: bossImg8, emoji: "🤖", hp: 1600, speed: 0.5, size: 120, color: "#34495e" },
        { name: "LV9: 終末の魔竜", imgObj: bossImg9, emoji: "🐉", hp: 2500, speed: 0.6, size: 140, color: "#e74c3c" },
        { name: "MAX: 医療神 アスクレピオス", imgObj: bossImg10, emoji: "👼", hp: 4000, speed: 0.4, size: 160, color: "#f1c40f" }
    ];
    let bossEncounterCount = 0; 

    const ynQuizzes = [
        { q: "成人の胸骨圧迫の深さは5cm以上である？", a: "⭕" },
        { q: "インスリン注射は毎回同じ場所に打つべきである？", a: "❌" },
        { q: "AEDのパッドはペースメーカーの真上に貼る？", a: "❌" },
        { q: "成人ICLSの高度気道確保後の換気は6秒に1回である？", a: "⭕" }
    ];

    let savedData = { credits: 0, upgrades: { fire: 0, speed: 0, shield: 0, bomb: 0, laser: 0, subBomb: 0, missile: 0, bit: 0, option: 0, force: 0 } };
    try {
        const localData = localStorage.getItem('medicalStrikerSaveV8');
        if (localData) {
            let parsed = JSON.parse(localData);
            if(parsed.upgrades) {
                ['laser', 'subBomb', 'missile', 'bit', 'option', 'force'].forEach(k => { if(parsed.upgrades[k] === undefined) parsed.upgrades[k] = 0; });
                savedData = parsed;
            }
        }
    } catch(e) {}

    function saveData() { try { localStorage.setItem('medicalStrikerSaveV8', JSON.stringify(savedData)); } catch(e) {} }
    window.resetSaveData = function() { if(confirm("データを初期化しますか？")) { localStorage.removeItem('medicalStrikerSaveV8'); location.reload(); } }

    const MAX_LEVEL = 10; const MAX_LEVEL_OPTION = 4; const MAX_LEVEL_FORCE = 3;
    function getCost(type, lvl) { 
        let multi = (lvl + 1) * (lvl + 1);
        if(type === 'force') return 200 * multi;
        if(type === 'shield' || type === 'option') return 150 * multi;
        if(type === 'bomb' || type === 'laser' || type === 'missile') return 100 * multi;
        return 50 * multi; 
    }

    const upgKeys = ['fire', 'speed', 'shield', 'bomb', 'laser', 'subBomb', 'missile', 'bit', 'option', 'force'];
    function updateHangerUI() {
        document.getElementById('display-credits').innerText = savedData.credits;
        upgKeys.forEach(type => {
            let lvl = savedData.upgrades[type];
            document.getElementById(`lvl-${type}`).innerText = lvl;
            let btn = document.getElementById(`btn-${type}`);
            let limit = (type === 'option') ? MAX_LEVEL_OPTION : (type === 'force' ? MAX_LEVEL_FORCE : MAX_LEVEL);
            if (lvl >= limit) { btn.innerText = "MAX"; btn.disabled = true; } 
            else { let cost = getCost(type, lvl); btn.innerText = cost + " C"; btn.disabled = (savedData.credits < cost); }
        });
    }

    window.buyUpgrade = function(type) {
        let lvl = savedData.upgrades[type];
        let limit = (type === 'option') ? MAX_LEVEL_OPTION : (type === 'force' ? MAX_LEVEL_FORCE : MAX_LEVEL);
        if (lvl >= limit) return;
        let cost = getCost(type, lvl);
        if (savedData.credits >= cost) {
            savedData.credits -= cost; savedData.upgrades[type]++;
            saveData(); updateHangerUI();
        }
    }
    updateHangerUI();

    let isGameOver = false; let score = 0; let frameCount = 0; let powerUpTime = 0; let activeQuiz = null;
    let exp = 0; let level = 1; let nextLevelExp = 500;
    
    let stars = []; for(let i=0; i<50; i++) { stars.push({ x: Math.random() * 500, y: Math.random() * 666, speed: 1 + Math.random() * 3, size: Math.random() * 3 }); }
    let player = { x: 250, y: 550, size: 40, emoji: "💉", speed: 5.0, shields: 0, invincible: 0, history: [] };
    
    let bullets = []; let enemies = []; let enemyBullets = []; let effects = []; let blasts = []; let gameLoopId;
    let bombs = 0; let isBombing = 0; 
    let isCharging = false; let chargeLevel = 0; let actionPressTime = 0;
    let forceObj = { exists: false, attached: true, returning: false, x: 0, y: 0, vx: 0, vy: 0 };
    let waveCannon = { active: false, life: 0, width: 0, damage: 0 };

    window.startGame = function() {
        hanger.style.display = "none"; canvas.style.display = "block"; controls.style.display = "flex"; 
        
        player.speed = 5.0 + (savedData.upgrades.speed * 0.4);
        player.shields = savedData.upgrades.shield; player.invincible = 0; player.history = []; 
        
        let forceLv = savedData.upgrades.force;
        if (forceLv > 0) {
            actionBtn.style.background = "rgba(52, 152, 219, 0.8)"; 
            actionBtn.innerHTML = `<div style="font-size: 26px;">🛡️</div><div style="font-size: 10px; font-weight: bold; color: white;">CHARGE</div>`;
            forceObj.exists = true; forceObj.attached = true;
        } else {
            actionBtn.style.background = "rgba(231, 76, 60, 0.8)"; 
            bombs = 2 + savedData.upgrades.bomb;
            actionBtn.innerHTML = `<div style="font-size: 26px;">🔥</div><div id="bomb-count-disp" style="font-size: 14px; font-weight: bold; color: white;">x${bombs}</div>`;
        }

        blasts = []; bullets = []; enemies = []; enemyBullets = []; effects = [];
        if (!gameLoopId) loop();
    }

    function damagePlayer() {
        if (player.invincible <= 0) {
            if (player.shields > 0) {
                player.shields--; player.invincible = 90; 
                effects.push({ x: player.x, y: player.y, text: "🛡️ シールド破損!", life: 40, vy: -1, color: "#3498db" });
                return false;
            } else {
                isGameOver = true; controls.style.display = "none";
                let earned = Math.floor(score / 25); savedData.credits += earned; saveData();
                effects.push({ x: player.x, y: player.y, text: "🔥", life: 60, vy: 0, color: "#fff" });
                document.getElementById("final-score").innerText = score;
                document.getElementById("earned-credits").innerText = "+" + earned + " C";
                overlay.style.display = "flex";
                return true; 
            }
        }
        return false;
    }

    window.startAction = function(e) {
        if(e) e.preventDefault();
        if (isGameOver) return;
        if (savedData.upgrades.force > 0) {
            isCharging = true; chargeLevel = 0; actionPressTime = Date.now();
            actionBtn.style.transform = "scale(0.9)";
        } else {
            if(bombs > 0 && isBombing === 0) fireNormalBomb();
        }
    }

    window.endAction = function(e) {
        if(e) e.preventDefault();
        if (isGameOver) return;
        actionBtn.style.transform = "scale(1.0)";
        
        let forceLv = savedData.upgrades.force;
        if (forceLv > 0 && isCharging) {
            isCharging = false;
            let holdTime = Date.now() - actionPressTime;
            if (holdTime < 300) {
                if (forceObj.attached) { forceObj.attached = false; forceObj.vx = 0; forceObj.vy = -12; } 
                else { forceObj.returning = true; }
            } else {
                if (chargeLevel > 60) {
                    waveCannon.active = true; waveCannon.life = 45; 
                    waveCannon.width = 40 + (chargeLevel / 3) + (forceLv * 20);
                    waveCannon.damage = 0.5 + (forceLv * 0.3) + (chargeLevel / 100);
                    effects.push({ x: player.x, y: player.y, text: "🌊 波動砲 発射! 🌊", life: 60, vy: -1, color: "#3498db" });
                }
            }
            chargeLevel = 0;
        }
    }

    function fireNormalBomb() {
        bombs--; document.getElementById("bomb-count-disp").innerText = "x" + bombs;
        isBombing = 40; player.invincible = 120;
        effects.push({ x: canvas.width/2, y: canvas.height/2, text: "🔥 MAXIMUM BOMB 🔥", life: 60, vy: -1, color: "#e74c3c" });
        enemies.forEach(enemy => {
            enemy.hp -= 50; 
            effects.push({ x: enemy.x + (Math.random()*40-20), y: enemy.y + (Math.random()*40-20), text: "💥", life: 30, vy: -1, color: "#fff" });
            if(enemy.hp <= 0 && !enemy.vanish) killEnemy(enemy);
        });
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
                effects.push({ x: canvas.width/2, y: canvas.height/2, text: "✨ 3WAY解放！ ✨", life: 60, vy: -1, color: "#f1c40f" });
            } else { effects.push({ x: canvas.width/2, y: canvas.height/2, text: "❌ 不正解...", life: 60, vy: -1, color: "#e74c3c" }); }
            activeQuiz = null; enemies.forEach(e => { if(e.isQuiz) e.vanish = true; });
        } else if (enemy.isBoss) {
            score += 10000; gainExp(2000);
            effects.push({ x: enemy.x, y: enemy.y, text: `🎊 ${enemy.name.split(' ')[0]} 撃破!! 🎊`, life: 60, vy: -2, color: enemy.color });
            enemies.forEach(e => { if(!e.isQuiz) e.vanish = true; }); 
            enemyBullets = []; 
        } else {
            let isMid = enemy.emoji === "👾"; score += (isMid ? 300 : 100); gainExp(isMid ? 150 : 50);
            effects.push({ x: enemy.x, y: enemy.y, text: "✨", life: 20, vy: -2, color: "#fff" });
        }
    }

    function update() {
        if (isGameOver) return; frameCount++;
        if (powerUpTime > 0) powerUpTime--;
        if (player.invincible > 0) player.invincible--;
        if (isBombing > 0) isBombing--;

        stars.forEach(s => { s.y += s.speed; if (s.y > canvas.height) { s.y = 0; s.x = Math.random() * canvas.width; } });

        player.x += joyDx * player.speed; player.y += joyDy * player.speed;
        if(player.x < 20) player.x = 20; if(player.x > canvas.width - 20) player.x = canvas.width - 20;
        if(player.y < 20) player.y = 20; if(player.y > canvas.height - 20) player.y = canvas.height - 20;

        player.history.unshift({x: player.x, y: player.y});
        let optLv = savedData.upgrades.option;
        if(player.history.length > optLv * 15 + 1) player.history.pop();

        if (forceObj.exists) {
            if (forceObj.attached) {
                forceObj.x = player.x; forceObj.y = player.y - 45; 
            } else if (forceObj.returning) {
                let dx = player.x - forceObj.x; let dy = (player.y - 45) - forceObj.y; let dist = Math.hypot(dx, dy);
                if (dist < 20) { forceObj.attached = true; forceObj.returning = false; } 
                else { forceObj.x += (dx / dist) * 15; forceObj.y += (dy / dist) * 15; }
            } else {
                forceObj.x += forceObj.vx; forceObj.y += forceObj.vy; forceObj.vy *= 0.95; 
                if (forceObj.x < 20) forceObj.x = 20; if (forceObj.x > canvas.width - 20) forceObj.x = canvas.width - 20;
                if (forceObj.y < 20) forceObj.y = 20; if (forceObj.y > canvas.height - 20) forceObj.y = canvas.height - 20;
            }
        }

        if (isCharging) { if (chargeLevel < 300) chargeLevel += 0.5; }

        let fireRate = Math.max(3, 14 - Math.floor(savedData.upgrades.fire * 1)); 
        if (frameCount % fireRate === 0 && !isCharging) { 
            if (powerUpTime > 0) {
                bullets.push({ x: player.x, y: player.y - 20, size: 15, vx: 0, vy: -15, type: 'main', emoji: "💊" });
                bullets.push({ x: player.x - 15, y: player.y - 15, size: 15, vx: -4, vy: -14, type: 'main', emoji: "💊" });
                bullets.push({ x: player.x + 15, y: player.y - 15, size: 15, vx: 4, vy: -14, type: 'main', emoji: "💊" });
            } else {
                bullets.push({ x: player.x - 12, y: player.y - 20, size: 15, vx: 0, vy: -15, type: 'main', emoji: "💊" });
                bullets.push({ x: player.x + 12, y: player.y - 20, size: 15, vx: 0, vy: -15, type: 'main', emoji: "💊" });
            }

            for(let i=1; i<=optLv; i++) {
                let pos = player.history[i*15];
                if(pos) bullets.push({ x: pos.x, y: pos.y - 20, size: 15, vx: 0, vy: -15, type: 'main', emoji: "💊" });
            }
        }

        let laserLv = savedData.upgrades.laser;
        if (laserLv > 0 && frameCount % Math.max(5, 25 - laserLv * 2) === 0 && !isCharging) {
            bullets.push({ x: player.x, y: player.y - 30, size: 5, vx: 0, vy: -30, type: 'laser' });
        }

        let subBombLv = savedData.upgrades.subBomb;
        if (subBombLv > 0 && frameCount % Math.max(30, 90 - subBombLv * 5) === 0 && !isCharging) {
            bullets.push({ x: player.x, y: player.y, size: 15, vx: 0, vy: -8, type: 'subBomb', targetY: player.y - 100 - (subBombLv * 15), emoji: "🧨" });
        }

        let missileLv = savedData.upgrades.missile;
        if (missileLv > 0 && frameCount % Math.max(20, 60 - missileLv * 3) === 0 && !isCharging) {
            bullets.push({ x: player.x, y: player.y, size: 12, vx: (Math.random()-0.5)*10, vy: -5, speed: 10, type: 'missile', emoji: "🚀" });
        }

        if (frameCount > 0 && frameCount % 1200 === 0) {
            let bossIndex = Math.min(bossEncounterCount, bossList.length - 1);
            let bossInfo = bossList[bossIndex];
            enemies.push({ 
                x: 250, y: -60, size: bossInfo.size, speed: bossInfo.speed, 
                emoji: bossInfo.emoji, imgObj: bossInfo.imgObj, 
                hp: bossInfo.hp, maxHp: bossInfo.hp, 
                name: bossInfo.name, color: bossInfo.color, isQuiz: false, isBoss: true 
            });
            effects.push({ x: 250, y: 300, text: `⚠️ ${bossInfo.name} 襲来 ⚠️`, life: 120, vy: 0, color: bossInfo.color });
            bossEncounterCount++; 
        }

        if (!activeQuiz && frameCount % 600 === 0 && (frameCount % 1200 !== 0)) {
            activeQuiz = ynQuizzes[Math.floor(Math.random() * ynQuizzes.length)];
            enemies.push({ x: 150, y: -30, size: 45, speed: 1.5, emoji: "⭕", hp: 3, isQuiz: true, ans: "⭕", invTime: 90 });
            enemies.push({ x: 350, y: -30, size: 45, speed: 1.5, emoji: "❌", hp: 3, isQuiz: true, ans: "❌", invTime: 90 });
        }

        let spawnRate = Math.max(8, 50 - Math.floor(score / 500)); 
        if (frameCount % spawnRate === 0) {
            let type = Math.random();
            enemies.push({ x: Math.random() * (canvas.width - 40) + 20, y: -30, size: 35, speed: 3 + Math.random() * 3 + (score / 3000), emoji: type > 0.8 ? "👾" : "🦠", hp: type > 0.8 ? 4 : 1, isQuiz: false, isBoss: false });
        }

        for (let i = enemyBullets.length - 1; i >= 0; i--) {
            let eb = enemyBullets[i]; eb.x += eb.vx; eb.y += eb.vy;
            if (eb.y > canvas.height + 20 || eb.x < -20 || eb.x > canvas.width + 20) { enemyBullets.splice(i, 1); continue; }
            if (forceObj.exists && checkCollision(eb, forceObj, 35)) {
                enemyBullets.splice(i, 1); effects.push({ x: eb.x, y: eb.y, text: "💥", life: 5, vy: 0, color: "#3498db" }); continue;
            }
            if (checkCollision(eb, player, 15)) { enemyBullets.splice(i, 1); damagePlayer(); }
        }

        for (let i = bullets.length - 1; i >= 0; i--) {
            let b = bullets[i];
            if (b.type === 'missile') {
                let target = null; let minDist = 9999;
                enemies.forEach(e => {
                    if(!e.vanish && e.y < canvas.height && !e.isQuiz) { let d = Math.hypot(e.x - b.x, e.y - b.y); if (d < minDist) { minDist = d; target = e; } }
                });
                if (target) {
                    let dx = target.x - b.x; let dy = target.y - b.y; let dist = Math.hypot(dx, dy);
                    b.vx += (dx / dist) * 0.8; b.vy += (dy / dist) * 0.8;
                    let currentSpeed = Math.hypot(b.vx, b.vy); b.vx = (b.vx / currentSpeed) * b.speed; b.vy = (b.vy / currentSpeed) * b.speed;
                }
            }
            b.x += b.vx; b.y += b.vy;
            
            if (b.type === 'subBomb' && b.y <= b.targetY) {
                blasts.push({ x: b.x, y: b.y, radius: 40 + (savedData.upgrades.subBomb * 5), life: 30, damage: 1 });
                bullets.splice(i, 1); continue;
            }
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

        let bitCount = savedData.upgrades.bit;
        if (bitCount > 0 && frameCount % 10 === 0) { 
            for(let i=0; i<bitCount; i++) {
                let angle = frameCount * 0.05 + (i * Math.PI * 2 / bitCount);
                let bx = player.x + Math.cos(angle) * 60; let by = player.y + Math.sin(angle) * 60;
                for(let j=enemyBullets.length-1; j>=0; j--) {
                    if(checkCollision({x:bx, y:by}, enemyBullets[j], 25)) {
                        enemyBullets.splice(j, 1); effects.push({ x: bx, y: by, text: "✨", life: 5, vy: 0, color: "#fff" });
                    }
                }
                enemies.forEach(e => {
                    if (e.isQuiz && e.invTime > 0) return;
                    if (!e.vanish && checkCollision({x:bx, y:by}, e, 35)) {
                        e.hp -= 2; effects.push({ x: e.x, y: e.y, text: "💥", life: 5, vy: -1, color: "#fff" });
                        if(e.hp <= 0 && !e.vanish) killEnemy(e);
                    }
                });
            }
        }

        if (forceObj.exists && frameCount % 5 === 0) {
            enemies.forEach(e => {
                if (e.isQuiz && e.invTime > 0) return;
                if (!e.vanish && checkCollision(e, forceObj, (e.isBoss ? e.size/2 : 25) + 20)) {
                    e.hp -= 2 + savedData.upgrades.force;
                    effects.push({ x: e.x + (Math.random()*40-20), y: e.y + (Math.random()*40-20), text: "💥", life: 5, vy: -1, color: "#3498db" });
                    if (e.hp <= 0 && !e.vanish) killEnemy(e);
                }
            });
        }

        if (waveCannon.active) {
            waveCannon.life--;
            enemies.forEach(e => {
                if (e.isQuiz && e.invTime > 0) return;
                if (!e.vanish && e.y < player.y && Math.abs(e.x - player.x) < (waveCannon.width/2 + e.size/2)) {
                    e.hp -= waveCannon.damage;
                    effects.push({ x: e.x + (Math.random()*40-20), y: e.y, text: "💥", life: 5, vy: -1, color: "#fff" });
                    if (e.hp <= 0 && !e.vanish) killEnemy(e);
                }
            });
            if (waveCannon.life <= 0) waveCannon.active = false;
        }

        for (let i = enemies.length - 1; i >= 0; i--) {
            let enemy = enemies[i]; enemy.y += enemy.speed;
            if (enemy.isQuiz && enemy.invTime > 0) enemy.invTime--;

            if (enemy.isBoss) { 
                enemy.x += Math.sin(frameCount * 0.03) * 2.5; 
                if (frameCount % 60 === 0 && enemy.y > 0) {
                    enemyBullets.push({ x: enemy.x, y: enemy.y, vx: -2, vy: 5, emoji: "🔴" });
                    enemyBullets.push({ x: enemy.x, y: enemy.y, vx: 0, vy: 6, emoji: "🔴" });
                    enemyBullets.push({ x: enemy.x, y: enemy.y, vx: 2, vy: 5, emoji: "🔴" });
                }
            } 
            else if (!enemy.isQuiz) { 
                enemy.x += Math.sin(frameCount * 0.05 + i) * 1.5; 
                if (enemy.emoji === "👾" && (frameCount + i * 10) % 90 === 0 && enemy.y > 0) {
                    let dx = player.x - enemy.x; let dy = player.y - enemy.y; let dist = Math.hypot(dx, dy);
                    let speed = 4 + (level * 0.1); 
                    enemyBullets.push({ x: enemy.x, y: enemy.y, vx: (dx/dist)*speed, vy: (dy/dist)*speed, emoji: "🟣" });
                }
            }

            if (enemy.y > canvas.height + 30 + (enemy.size/2)) { if (enemy.isQuiz) activeQuiz = null; enemies.splice(i, 1); continue; }

            for (let j = bullets.length - 1; j >= 0; j--) {
                let bullet = bullets[j];
                let hitRadius = enemy.isBoss ? (enemy.size / 2) + 10 : 25;
                if (checkCollision(enemy, bullet, hitRadius)) {
                    if (enemy.isQuiz && enemy.invTime > 0) {
                        bullets.splice(j, 1); effects.push({ x: bullet.x, y: bullet.y - 10, text: "🛡️", life: 5, vy: -1, color: "#fff" }); continue;
                    }
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
                if (!isDead && !enemy.isBoss) { enemy.hp = 0; killEnemy(enemy); }
            }
        }

        for (let i = effects.length - 1; i >= 0; i--) { effects[i].y += effects[i].vy; effects[i].life--; if (effects[i].life <= 0) effects.splice(i, 1); }
    }

    function draw() {
        ctx.fillStyle = "#000000"; ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = "#3498db"; stars.forEach(s => { ctx.beginPath(); ctx.arc(s.x, s.y, s.size, 0, Math.PI * 2); ctx.fill(); });

        if (isBombing > 0) { ctx.fillStyle = `rgba(255, 255, 255, ${isBombing / 40})`; ctx.fillRect(0, 0, canvas.width, canvas.height); }

        if (waveCannon.active) {
            ctx.fillStyle = `rgba(52, 152, 219, ${Math.min(1.0, waveCannon.life/10)})`;
            ctx.shadowColor = "#00ffff"; ctx.shadowBlur = 20;
            ctx.fillRect(player.x - waveCannon.width/2, 0, waveCannon.width, player.y);
            ctx.fillStyle = `rgba(255, 255, 255, 0.9)`;
            ctx.fillRect(player.x - waveCannon.width/4, 0, waveCannon.width/2, player.y);
            ctx.shadowBlur = 0;
        }

        blasts.forEach(b => { ctx.fillStyle = `rgba(231, 76, 60, ${b.life / 30})`; ctx.beginPath(); ctx.arc(b.x, b.y, b.radius, 0, Math.PI*2); ctx.fill(); });

        let optLv = savedData.upgrades.option;
        if (optLv > 0) {
            ctx.font = "25px Arial"; ctx.textAlign = "center"; ctx.textBaseline = "middle";
            for(let i=1; i<=optLv; i++) {
                let pos = player.history[i*15];
                if(pos) { ctx.save(); ctx.shadowColor = "#e67e22"; ctx.shadowBlur = 10; ctx.fillText("🟠", pos.x, pos.y); ctx.restore(); }
            }
        }

        ctx.textAlign = "center"; ctx.textBaseline = "middle";
        bullets.forEach(b => { 
            if (b.type === 'laser') {
                ctx.fillStyle = "#00ffff"; ctx.shadowColor = "#00ffff"; ctx.shadowBlur = 10;
                ctx.fillRect(b.x - 2, b.y, 4, 30); ctx.shadowBlur = 0;
            } else {
                ctx.font = "20px Arial"; ctx.fillText(b.emoji, b.x, b.y); 
            }
        });

        ctx.font = "15px Arial"; enemyBullets.forEach(eb => { ctx.fillText(eb.emoji, eb.x, eb.y); });
        
        enemies.forEach(e => { 
            if (e.isBoss) {
                if (e.imgObj && e.imgObj.isLoaded) {
                    ctx.drawImage(e.imgObj.img, e.x - e.size, e.y - e.size, e.size * 2, e.size * 2);
                } else {
                    ctx.font = e.size + "px Arial"; ctx.fillText(e.emoji, e.x, e.y); 
                }
                
                ctx.fillStyle = e.color || "#fff"; ctx.font = "bold 14px Arial"; ctx.fillText(e.name, e.x, e.y - e.size/2 - 25);
                ctx.fillStyle = "#e74c3c"; ctx.fillRect(e.x - 50, e.y - e.size/2 - 15, 100, 8);
                ctx.fillStyle = "#2ecc71"; ctx.fillRect(e.x - 50, e.y - e.size/2 - 15, 100 * (e.hp / e.maxHp), 8);
            } else if (e.isQuiz) { 
                if (e.invTime > 0) {
                    ctx.globalAlpha = 0.5 + Math.sin(frameCount * 0.3) * 0.5;
                    ctx.font = e.size + "px Arial"; ctx.fillText(e.emoji, e.x, e.y); ctx.globalAlpha = 1.0;
                    ctx.fillStyle = "#f1c40f"; ctx.font = "bold 16px Arial"; ctx.fillText("WAIT!", e.x, e.y - 35);
                } else {
                    ctx.font = e.size + "px Arial"; ctx.fillText(e.emoji, e.x, e.y); 
                    ctx.fillStyle = "#fff"; ctx.font = "bold 16px Arial"; ctx.fillText("撃て!", e.x, e.y - 35); 
                }
            } else {
                ctx.font = e.size + "px Arial"; ctx.fillText(e.emoji, e.x, e.y); 
            }
        });
        
        if (!isGameOver) { 
            ctx.font = "45px Arial"; 
            if (player.invincible > 0 && Math.floor(frameCount / 5) % 2 === 0) ctx.globalAlpha = 0.3;
            if (powerUpTime > 0) {
                ctx.save(); ctx.shadowColor = "#f1c40f"; ctx.shadowBlur = 20; ctx.fillStyle = "rgba(241, 196, 15, 0.3)";
                ctx.beginPath(); ctx.arc(player.x, player.y, 35, 0, Math.PI*2); ctx.fill(); ctx.restore();
            }
            if (player.shields > 0) {
                ctx.save(); ctx.shadowColor = "#3498db"; ctx.shadowBlur = 15;
                ctx.fillStyle = "rgba(52, 152, 219, 0.2)"; ctx.strokeStyle = "rgba(52, 152, 219, 0.8)"; ctx.lineWidth = 3;
                ctx.beginPath(); ctx.arc(player.x, player.y, 35, 0, Math.PI*2); ctx.fill(); ctx.stroke(); ctx.restore();
            }
            
            if (isCharging) {
                ctx.save(); ctx.shadowColor = "#3498db"; ctx.shadowBlur = 15;
                ctx.beginPath(); ctx.arc(player.x, player.y - 20, 20 + chargeLevel/6, 0, Math.PI*2);
                ctx.fillStyle = `rgba(52, 152, 219, ${chargeLevel/300 * 0.5})`; ctx.fill();
                ctx.strokeStyle = "#00ffff"; ctx.lineWidth = 2 + chargeLevel/50; ctx.stroke(); ctx.restore();
            }
            
            ctx.fillText(player.emoji, player.x, player.y); ctx.globalAlpha = 1.0;
            
            if (forceObj.exists) {
                ctx.save(); ctx.shadowColor = "#3498db"; ctx.shadowBlur = 15;
                ctx.font = "35px Arial"; ctx.fillText("🛡️", forceObj.x, forceObj.y); ctx.restore();
            }

            let bitCount = savedData.upgrades.bit;
            if (bitCount > 0) {
                for(let i=0; i<bitCount; i++) {
                    let angle = frameCount * 0.05 + (i * Math.PI * 2 / bitCount);
                    let bx = player.x + Math.cos(angle) * 60; let by = player.y + Math.sin(angle) * 60;
                    ctx.font = "20px Arial"; ctx.fillText("🛸", bx, by);
                }
            }
        }

        effects.forEach(eff => {
            ctx.globalAlpha = eff.life / 20; ctx.fillStyle = eff.color || "#ffffff";
            let fontSize = eff.text.includes("BOSS") || eff.text.includes("撃破") || eff.text.includes("BOMB") || eff.text.includes("波動砲") ? 28 : (eff.text.includes("解放") || eff.text.includes("不正解") ? 32 : 24);
            ctx.font = "bold " + fontSize + "px Arial"; ctx.fillText(eff.text, eff.x, eff.y); ctx.globalAlpha = 1.0;
        });

        if (activeQuiz) {
            ctx.fillStyle = "rgba(44, 62, 80, 0.85)"; ctx.strokeStyle = "#f1c40f"; ctx.lineWidth = 2;
            ctx.beginPath(); ctx.roundRect(25, 15, 450, 75, 10); ctx.fill(); ctx.stroke();
            ctx.fillStyle = "#f1c40f"; ctx.font = "bold 14px Arial"; ctx.fillText("🎯 ボーナス・クイズ (正解を撃破でパワーアップ！)", 250, 35);
            ctx.fillStyle = "#ffffff"; ctx.font = "bold 16px Arial"; ctx.fillText(activeQuiz.q, 250, 65);
        }

        ctx.fillStyle = "#ffffff"; ctx.textAlign = "left"; ctx.font = "bold 20px Arial";
        ctx.fillText("SCORE: " + score, 15, 30);
    }

    function loop() { update(); draw(); gameLoopId = requestAnimationFrame(loop); }
</script>
</body>
</html>
"""

html_code = html_code.replace("__B64_BOSS_01__", b64_1)
html_code = html_code.replace("__B64_BOSS_02__", b64_2)
html_code = html_code.replace("__B64_BOSS_03__", b64_3)
html_code = html_code.replace("__B64_BOSS_04__", b64_4)
html_code = html_code.replace("__B64_BOSS_05__", b64_5)
html_code = html_code.replace("__B64_BOSS_06__", b64_6)
html_code = html_code.replace("__B64_BOSS_07__", b64_7)
html_code = html_code.replace("__B64_BOSS_08__", b64_8)
html_code = html_code.replace("__B64_BOSS_09__", b64_9)
html_code = html_code.replace("__B64_BOSS_10__", b64_10)

components.html(html_code, height=900)