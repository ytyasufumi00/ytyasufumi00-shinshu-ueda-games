import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="ヴァンサバ風・酸塩基アクション", page_icon="🥷", layout="wide")

st.title("🥷 信州上田ヴァンサバ風・酸塩基サバイバル V12（難易度選択版）")
st.write("最初に難易度を選択できます。Lv5ごとの節目は通常問題ですが、正解すると超絶ボーナスが発動します！")

html_code = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
    body { margin: 0; background: #f0f2f6; display: flex; flex-direction: column; align-items: center; font-family: 'Helvetica Neue', Arial, sans-serif; overflow: hidden; }
    #game-container { display: flex; flex-direction: column; width: 100%; max-width: 700px; background: #fff; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); overflow: hidden; -webkit-touch-callout: none; user-select: none; }
    #canvas-wrapper { position: relative; width: 100%; aspect-ratio: 7 / 5; }
    canvas { width: 100%; height: 100%; background-color: #1a252c; display: block; }

    #controller-area { width: 100%; height: 180px; background: #e5e9f0; display: flex; justify-content: center; align-items: center; position: relative; border-top: 2px solid #ccc; }
    #joystick-zone { width: 120px; height: 120px; background: rgba(0, 0, 0, 0.1); border: 3px solid rgba(0, 0, 0, 0.2); border-radius: 50%; position: relative; touch-action: none; }
    #joystick-knob { position: absolute; top: 50%; left: 50%; width: 55px; height: 55px; background: #4a5568; border-radius: 50%; transform: translate(-50%, -50%); box-shadow: 0 4px 8px rgba(0,0,0,0.3); pointer-events: none; }

    /* 🌟 追加：スタート画面（難易度選択） */
    #start-screen-overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.85); z-index: 40; text-align: center; color: white; padding-top: 60px; box-sizing: border-box; }
    #start-screen-title { color: #f1c40f; font-size: 36px; font-weight: bold; margin-bottom: 30px; text-shadow: 0 0 10px #f1c40f; }
    .diff-btn { display: block; width: 80%; max-width: 300px; margin: 15px auto; padding: 15px; font-size: 18px; font-weight: bold; border: none; border-radius: 8px; cursor: pointer; transition: 0.2s; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }
    .diff-btn:active { transform: scale(0.95); }
    .easy-btn { background: #2ecc71; color: white; border-bottom: 4px solid #27ae60; }
    .hard-btn { background: #e74c3c; color: white; border-bottom: 4px solid #c0392b; }

    #quiz-overlay { display: none; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.85); z-index: 20; }
    #quiz-box { position: absolute; top: 15px; left: 50%; transform: translateX(-50%); background: #fff; padding: 20px; border-radius: 12px; text-align: center; width: 90%; max-height: 90%; overflow-y: auto; border: 4px solid #f1c40f; box-sizing: border-box; }

    #game-over-overlay { display: none; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.9); z-index: 30; text-align: center; color: white; padding-top: 80px; box-sizing: border-box; }
    #game-over-title { color: #e74c3c; font-size: 48px; font-weight: bold; margin-bottom: 10px; text-shadow: 0 0 15px #e74c3c; }
    #game-over-level { font-size: 24px; margin-bottom: 30px; color: #f1c40f; }
    .restart-btn { background: #e67e22; color: white; border: none; border-radius: 8px; padding: 15px 30px; font-size: 20px; font-weight: bold; cursor: pointer; transition: 0.2s; box-shadow: 0 4px 10px rgba(230, 126, 34, 0.5); }
    .restart-btn:active { transform: scale(0.95); background: #d35400; }

    .quiz-title { color: #e74c3c; font-size: 20px; margin: 0 0 10px 0; font-weight: bold; }
    .data-card { background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 8px; padding: 10px; margin-bottom: 15px; display: flex; flex-direction: column; gap: 4px; }
    .data-val { font-family: monospace; font-size: 18px; color: #2c3e50; font-weight: bold; }

    #quiz-buttons { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 10px; }
    .quiz-btn { background: #3498db; color: white; border: none; border-radius: 8px; padding: 15px 5px; font-size: 13px; font-weight: bold; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: 0.1s; }
    .quiz-btn:active { background: #2980b9; transform: scale(0.95); }

    .bonus-btn { background: #9b59b6 !important; }
    .bonus-btn:active { background: #8e44ad !important; transform: scale(0.95); }

    #reward-buttons { display: flex; flex-direction: column; gap: 10px; }
    .reward-btn { background: #f39c12; color: white; border: none; border-radius: 8px; padding: 12px; text-align: left; cursor: pointer; transition: 0.1s; border-left: 6px solid #e67e22; }
    .reward-btn b { font-size: 16px; display: block; margin-bottom: 4px; }
    .reward-btn small { font-size: 12px; opacity: 0.9; }
    .reward-btn:active { background: #e67e22; transform: scale(0.98); }
    /* 🌟 折りたたみヒント用スタイル */
    #hint-box { width: 95%; margin: 10px auto; background: #34495e; color: #fff; border-radius: 8px; padding: 5px; }
    summary { padding: 10px; cursor: pointer; font-weight: bold; text-align: center; }
    .hint-content { padding: 10px; background: #ecf0f1; color: #2c3e50; font-size: 14px; border-radius: 4px; }
</style>
</head>
<body>

<div id="game-container">
    <div id="canvas-wrapper">
        <canvas id="gameCanvas" width="700" height="500"></canvas>
        
        <div id="start-screen-overlay">
            <div id="start-screen-title">🥷 出陣準備</div>
            <button class="diff-btn easy-btn" onclick="startGame('easy')">🟢 EASY モード<br><small style="font-weight:normal;">敵が弱く、レベルが上がりやすい</small></button>
            <button class="diff-btn hard-btn" onclick="startGame('hard')">🔴 HARD モード<br><small style="font-weight:normal;">本来の容赦ない難易度</small></button>
        </div>

        <div id="quiz-overlay"><div id="quiz-box"></div></div>
        
        <div id="game-over-overlay">
            <div id="game-over-title">💀 討死...</div>
            <div id="game-over-level">最終到達レベル: <span id="final-level-text"></span></div>
            <button class="restart-btn" onclick="restartGame()">🔄 タイトルへ戻る</button>
        </div>
    </div>
    <div id="controller-area"><div id="joystick-zone"><div id="joystick-knob"></div></div></div>
    <div id="hint-box">
        <details>
            <summary>💡 診断のヒントを見る</summary>
            <div class="hint-content">
                <b>【基本ルール】</b><br>
                pH 7.35未満＝アシドーシス、7.45超＝アルカローシス<br>
                PaCO2(40)とHCO3(24)の向きに注目！<br>
                ・<b>呼吸性</b>：pHとPaCO2が逆向き  (PH↑かつPaCO2↓ or PH↓かつPaCO2↑)<br>
                ・<b>代謝性</b>：pHとHCO3が同じ向き (PH↑かつHCO3↑ or PH↓かつHCO3↓)
            </div>
        </details>
    </div>
    
    <div id="controller-area">...</div>
</div>

<script>
    const canvas = document.getElementById("gameCanvas");
    const ctx = canvas.getContext("2d");
    const overlay = document.getElementById("quiz-overlay");
    const quizBox = document.getElementById("quiz-box");
    const gameOverOverlay = document.getElementById("game-over-overlay");
    const startScreenOverlay = document.getElementById("start-screen-overlay");

    // 🌟 ゲーム状態の管理
    let gameStarted = false;
    let difficulty = 'hard';
    let isPaused = true;
    
    let frameCount = 0;
    let bossWarningTimer = 0;
    
    let player = { x: 350, y: 250, size: 24, speed: 3.5, level: 1, exp: 0, nextExp: 5, hp: 100, maxHp: 100, invincible: 0 };
    let enemies = []; let bullets = []; let gems = []; let effects = [];
    let joyVector = { x: 0, y: 0 }; let keys = {};

    const weaponDB = {
        shuriken:  { name: "🟡 クエン酸手裏剣", desc: "自動連射。Lvで弾数が爆発的に増加。" },
        shield:    { name: "🟢 重曹シールド", desc: "回転バリア。Lvで数と大きさが劇的アップ。" },
        piercer:   { name: "🔵 フロセミド貫通弾", desc: "直線貫通弾。Lvで極太レーザー化。" },
        potassium: { name: "🔴 カリウム爆弾", desc: "敵地で大爆発。Lvで爆発範囲が画面を覆う。" },
        calcium:   { name: "⚪ カルシウム・オーラ", desc: "周囲継続ダメージ。Lvで範囲拡大。" },
        dialyzer:  { name: "🌐 透析クロスレイ", desc: "多方向レーザー。Lvで回転しながら薙ぎ払う。" },
        resin:     { name: "⚫ レジン・トラップ", desc: "吸着罠。Lvで巨大化し敵を足止め。" },
        tolvaptan: { name: "🌊 トルバプタン波", desc: "広がる波。Lvで全方位大津波に進化。" },
        mra:       { name: "🟣 MRAブーメラン", desc: "往復弾。Lvで超巨大ブーメラン乱舞。" },
        epo:       { name: "✨ エリスロポエチン", desc: "移動・全武器の攻撃速度がパッシブ強化。" }
    };
    let wp = { shuriken: 1, shield: 0, piercer: 0, potassium: 0, calcium: 0, dialyzer: 0, resin: 0, tolvaptan: 0, mra: 0, epo: 0 };
    let timers = { shuriken: 0, piercer: 0, potassium: 0, dialyzer: 0, resin: 0, tolvaptan: 0, mra: 0 };
    let shieldAngle = 0; let globalDialyzerAngle = 0;

    const enemyTypes = [
        { name: "尿毒素",   emoji: "🦠", size: 24, speedBase: 1.2, hpBase: 2,   exp: 1, reqLv: 1,  moveType: 'chase' },
        { name: "過剰Na",   emoji: "🧂", size: 20, speedBase: 2.2, hpBase: 2,   exp: 1, reqLv: 3,  moveType: 'sine' }, 
        { name: "結石",     emoji: "🪨", size: 36, speedBase: 0.5, hpBase: 15,  exp: 3, reqLv: 5,  moveType: 'chase' }, 
        { name: "LDL",      emoji: "🍔", size: 28, speedBase: 1.0, hpBase: 8,   exp: 2, reqLv: 8,  moveType: 'random' }, 
        { name: "乳酸",     emoji: "👻", size: 28, speedBase: 1.8, hpBase: 12,  exp: 2, reqLv: 12, moveType: 'sine' }, 
        { name: "石灰化",   emoji: "🦴", size: 32, speedBase: 0.8, hpBase: 35,  exp: 4, reqLv: 15, moveType: 'chase' }, 
        { name: "重症アシ", emoji: "☠️", size: 40, speedBase: 1.5, hpBase: 50,  exp: 6, reqLv: 20, moveType: 'chase' },
        { name: "高K血症",  emoji: "⚡", size: 26, speedBase: 2.5, hpBase: 40,  exp: 4, reqLv: 25, moveType: 'sine' }, 
        { name: "AGEs",     emoji: "🍩", size: 30, speedBase: 1.3, hpBase: 60,  exp: 5, reqLv: 30, moveType: 'random' }, 
        { name: "低酸素",   emoji: "🌀", size: 34, speedBase: 1.6, hpBase: 80,  exp: 6, reqLv: 35, moveType: 'sine' }, 
        { name: "ｻｲﾄｶｲﾝ",   emoji: "🌪️", size: 36, speedBase: 2.0, hpBase: 120, exp: 8, reqLv: 40, moveType: 'chase' }, 
        { name: "多臓器不全",emoji: "💀", size: 44, speedBase: 1.0, hpBase: 300, exp: 12,reqLv: 45, moveType: 'chase' }, 
        { name: "DKA",      emoji: "🩸", size: 38, speedBase: 2.2, hpBase: 200, exp: 10,reqLv: 50, moveType: 'sine' } 
    ];

    const bossTypes = [
        { name: "巨大結石", emoji: "🪨", size: 90,  speedBase: 0.6, hpBase: 300,  exp: 100, moveType: 'chase' },
        { name: "メガLDL",  emoji: "🍔", size: 100, speedBase: 0.8, hpBase: 500, exp: 200, moveType: 'random' },
        { name: "大石灰化", emoji: "🦴", size: 120, speedBase: 0.5, hpBase: 1000, exp: 350, moveType: 'chase' },
        { name: "敗血症",   emoji: "🦠", size: 140, speedBase: 1.1, hpBase: 2000, exp: 500, moveType: 'sine' },
        { name: "末期腎不全",emoji: "🥀", size: 180, speedBase: 0.9, hpBase: 5000,exp: 1000,moveType: 'chase' },
        { name: "鬱血性心不全", emoji: "🌊", size: 200, speedBase: 0.7, hpBase: 10000, exp: 2000, moveType: 'sine' },
        { name: "劇症型DKA",   emoji: "🩸", size: 220, speedBase: 1.3, hpBase: 25000, exp: 4000, moveType: 'chase' },
        { name: "ｻｲﾄｶｲﾝｽﾄｰﾑ",  emoji: "🌪️", size: 240, speedBase: 1.5, hpBase: 50000, exp: 8000, moveType: 'random' },
        { name: "肝腎症候群",   emoji: "🧟", size: 260, speedBase: 0.5, hpBase: 100000, exp: 15000, moveType: 'chase' },
        { name: "尿毒症性脳症", emoji: "🧠", size: 280, speedBase: 1.2, hpBase: 200000, exp: 25000, moveType: 'sine' },
        { name: "重症DIC",      emoji: "🕸️", size: 300, speedBase: 1.0, hpBase: 300000, exp: 40000, moveType: 'chase' },
        { name: "多臓器不全",   emoji: "🌌", size: 350, speedBase: 0.8, hpBase: 500000, exp: 99999, moveType: 'chase' }
    ];

    function generateAcidBaseCase() {
        const disorders = ["呼吸性アシドーシス", "代謝性アシドーシス", "呼吸性アルカローシス", "代謝性アルカローシス"];
        const primary = disorders[Math.floor(Math.random() * disorders.length)];
        let pH, PaCO2, HCO3;
        switch(primary) {
            case "呼吸性アシドーシス": pH=(7.10+Math.random()*0.20).toFixed(2); PaCO2=Math.floor(50+Math.random()*20); HCO3=Math.floor(24+Math.random()*4); break;
            case "代謝性アシドーシス": pH=(7.10+Math.random()*0.20).toFixed(2); PaCO2=Math.floor(30+Math.random()*10); HCO3=Math.floor(10+Math.random()*10); break;
            case "呼吸性アルカローシス": pH=(7.50+Math.random()*0.15).toFixed(2); PaCO2=Math.floor(20+Math.random()*10); HCO3=Math.floor(20+Math.random()*4); break;
            case "代謝性アルカローシス": pH=(7.50+Math.random()*0.15).toFixed(2); PaCO2=Math.floor(40+Math.random()*10); HCO3=Math.floor(30+Math.random()*10); break;
        }
        return { pH: pH, PaCO2: PaCO2, HCO3: HCO3, ans: primary, options: disorders };
    }

    // 🌟 ゲーム開始処理
    function startGame(selectedDifficulty) {
        difficulty = selectedDifficulty;
        startScreenOverlay.style.display = 'none';
        gameStarted = true;
        isPaused = false;
    }

    function triggerGameOver() {
        isPaused = true;
        document.getElementById('final-level-text').innerText = player.level;
        gameOverOverlay.style.display = 'block';
    }

    function restartGame() {
        // 全リセットしてスタート画面に戻す
        player = { x: 350, y: 250, size: 24, speed: 3.5, level: 1, exp: 0, nextExp: 5, hp: 100, maxHp: 100, invincible: 0 };
        enemies = []; bullets = []; gems = []; effects = [];
        wp = { shuriken: 1, shield: 0, piercer: 0, potassium: 0, calcium: 0, dialyzer: 0, resin: 0, tolvaptan: 0, mra: 0, epo: 0 };
        timers = { shuriken: 0, piercer: 0, potassium: 0, dialyzer: 0, resin: 0, tolvaptan: 0, mra: 0 };
        shieldAngle = 0; globalDialyzerAngle = 0; frameCount = 0; bossWarningTimer = 0;
        
        gameOverOverlay.style.display = 'none';
        startScreenOverlay.style.display = 'block';
        gameStarted = false;
        isPaused = true;
    }

    function triggerQuiz() {
        isPaused = true; endJoy(); 
        let isMilestone = (player.level % 5 === 0); 
        let html = '';

        // 🌟 節目の問題も通常問題（一次性異常）に戻しました
        const q = generateAcidBaseCase();
        
        if (isMilestone) {
            html = `<div class="quiz-title" style="color:#9b59b6;">🌟 節目Lv${player.level}の試練（超ボーナス） 🌟</div>
                    <div class="data-card"><div class="data-val">pH : ${q.pH}</div><div class="data-val">PaCO2 : ${q.PaCO2} mmHg</div><div class="data-val">HCO3- : ${q.HCO3} mEq/L</div></div><div id="quiz-buttons">`;
            q.options.forEach(opt => { 
                html += `<button class="quiz-btn bonus-btn" onclick="checkAnswer('${opt}', '${q.ans}', true)">${opt}</button>`; 
            });
        } else {
            html = `<div class="quiz-title">🆙 レベルアップ！診断せよ</div>
                    <div class="data-card"><div class="data-val">pH : ${q.pH}</div><div class="data-val">PaCO2 : ${q.PaCO2} mmHg</div><div class="data-val">HCO3- : ${q.HCO3} mEq/L</div></div><div id="quiz-buttons">`;
            q.options.forEach(opt => { 
                html += `<button class="quiz-btn" onclick="checkAnswer('${opt}', '${q.ans}', false)">${opt}</button>`; 
            });
        }
        html += `</div>`; quizBox.innerHTML = html; overlay.style.display = "block";
    }

    function checkAnswer(selected, correct, isMilestone) {
        if (selected === correct) { 
            player.hp = Math.min(player.maxHp, player.hp + 50);
            
            if (isMilestone) {
                let upgradedNames = [];
                for(let k in wp) { if(wp[k] > 0) { wp[k]++; upgradedNames.push(weaponDB[k].name.split(" ")[1]); } }
                enemies = [];
                effects.push({ x: 350, y: 250, radius: 1000, life: 60, type: 'explosion', dmg: 9999 });
                alert("🎉 節目問題 正解！\\n\\n【HP 50回復！】\\n【スーパーボーナス！】\\n画面の敵を全滅させ、全武器Lv+1しました！");
                overlay.style.display = "none"; isPaused = false;
            } else {
                showRewardSelection(); 
            }
        } else {
            alert("誤診です...\\n武器強化ならず。"); 
            overlay.style.display = "none"; isPaused = false; 
        }
    }

    function showRewardSelection() {
        let available = Object.keys(weaponDB).sort(() => 0.5 - Math.random()).slice(0, 3);
        let html = `<div class="quiz-title">🎁 極限強化を選択（HP回復済）</div><div id="reward-buttons">`;
        available.forEach(key => {
            let w = weaponDB[key]; let currentLv = wp[key]; let nextLv = currentLv + 1;
            if (nextLv === 10) {
                html += `<button class="reward-btn" style="background: #8e44ad; border-left: 6px solid #9b59b6; box-shadow: 0 0 10px #9b59b6;" onclick="selectReward('${key}')">
                            <b style="color: #ff9ff3;">🔥【超覚醒】${w.name} (Lv MAX)</b><small>限界突破！究極の形態に進化します。</small></button>`;
            } else {
                html += `<button class="reward-btn" onclick="selectReward('${key}')">
                            <b>${w.name} <span style="color:#ffeaa7;">(Lv ${currentLv} → ${nextLv})</span></b><small>${w.desc}</small></button>`;
            }
        });
        html += `</div>`; quizBox.innerHTML = html;
    }

    function selectReward(weaponKey) { wp[weaponKey]++; overlay.style.display = "none"; isPaused = false; }

    const joyZone = document.getElementById("joystick-zone"); const joyKnob = document.getElementById("joystick-knob");
    let isDragging = false; let joyCenter = { x: 0, y: 0 }; const maxRadius = 45;
    function startJoy(e) { e.preventDefault(); isDragging = true; const rect = joyZone.getBoundingClientRect(); joyCenter = { x: rect.left + rect.width / 2, y: rect.top + rect.height / 2 }; }
    function moveJoy(e) {
        if (!isDragging) return;
        const cx = e.touches ? e.touches[0].clientX : e.clientX; const cy = e.touches ? e.touches[0].clientY : e.clientY;
        let dx = cx - joyCenter.x; let dy = cy - joyCenter.y; let dist = Math.hypot(dx, dy);
        if (dist > maxRadius) { dx *= maxRadius / dist; dy *= maxRadius / dist; }
        joyKnob.style.transform = `translate(calc(-50% + ${dx}px), calc(-50% + ${dy}px))`; joyVector = { x: dx / maxRadius, y: dy / maxRadius };
    }
    function endJoy() { isDragging = false; joyKnob.style.transform = `translate(-50%, -50%)`; joyVector = { x: 0, y: 0 }; }
    joyZone.addEventListener("touchstart", startJoy, {passive:false}); window.addEventListener("touchmove", moveJoy, {passive:false}); window.addEventListener("touchend", endJoy);
    joyZone.addEventListener("mousedown", startJoy); window.addEventListener("mousemove", moveJoy); window.addEventListener("mouseup", endJoy);
    window.addEventListener("keydown", e => { keys[e.key] = true; if(["ArrowUp","ArrowDown","ArrowLeft","ArrowRight"].includes(e.key)) e.preventDefault(); });
    window.addEventListener("keyup", e => keys[e.key] = false);

    function update() {
        if (!gameStarted || isPaused) return;
        frameCount++;
        if (player.invincible > 0) player.invincible--;

        let moveX = 0; let moveY = 0;
        if (keys["ArrowUp"]) moveY -= 1; if (keys["ArrowDown"]) moveY += 1; if (keys["ArrowLeft"]) moveX -= 1; if (keys["ArrowRight"]) moveX += 1;
        if (moveX !== 0 || moveY !== 0) { let dist = Math.hypot(moveX, moveY); moveX /= dist; moveY /= dist; } 
        else { moveX = joyVector.x; moveY = joyVector.y; }

        let speedBuff = 1 + (wp.epo * 0.15); let fireBuff = 1 + (wp.epo * 0.2); 
        player.x += moveX * player.speed * speedBuff; player.y += moveY * player.speed * speedBuff;
        player.x = Math.max(0, Math.min(canvas.width - player.size, player.x)); player.y = Math.max(0, Math.min(canvas.height - player.size, player.y));
        let px = player.x + 12; let py = player.y + 12;

        // 🌟 難易度による倍率設定
        let hpDiffMult = difficulty === 'easy' ? 0.8 : 1.0;
        let speedDiffMult = difficulty === 'easy' ? 0.9 : 1.0;

        if (frameCount % 1800 === 0 && frameCount > 0) {
            let bossIdx = Math.min(Math.floor(frameCount / 1800) - 1, bossTypes.length - 1);
            let b = bossTypes[bossIdx];
            
            let bossBaseHp = b.hpBase + (player.level * 25);
            let finalBossHp = bossBaseHp;
            if (player.level >= 15) {
                let levelDiff = player.level - 14;
                finalBossHp = Math.floor(bossBaseHp * Math.pow(1.2, levelDiff));
            }
            
            enemies.push({ 
                x: Math.random() < 0.5 ? -150 : 850, y: 250, 
                size: b.size, emoji: b.emoji, exp: b.exp,
                speed: (b.speedBase + (player.level * 0.01)) * speedDiffMult, 
                hp: Math.max(10, finalBossHp * hpDiffMult), // EASYならボスのHP大幅減
                moveType: b.moveType, timeOffset: 0, isBoss: true
            });
            bossWarningTimer = 180; 
        }

        let spawnInterval;
        if (player.level <= 5) spawnInterval = 60;
        else spawnInterval = Math.max(2, 40 - Math.floor(player.level * 1.2)); 

        if (frameCount % spawnInterval === 0) {
            let spawnCount = 1 + Math.floor(player.level / 3);
            for(let i=0; i<spawnCount; i++){
                let ex = Math.random() < 0.5 ? -40 : 740; let ey = Math.random() * 540 - 20;
                let availableTypes = enemyTypes.filter(t => player.level >= t.reqLv);
                let type = availableTypes[Math.floor(Math.random() * availableTypes.length)];
                
                let calculatedHp = type.hpBase + Math.floor(player.level / 3);
                if (player.level >= 10) {
                    let levelDiff = player.level - 9; 
                    calculatedHp = Math.floor(calculatedHp * Math.pow(1.2, levelDiff));
                }

                enemies.push({ 
                    x: ex, y: ey, size: type.size, emoji: type.emoji, exp: type.exp,
                    speed: (type.speedBase + (player.level * 0.015)) * speedDiffMult, 
                    hp: Math.max(1, calculatedHp * hpDiffMult), // EASYなら敵HP減
                    moveType: type.moveType, timeOffset: Math.random() * 100, isBoss: false
                });
            }
        }

        let nearest = enemies.length > 0 ? enemies.reduce((a, b) => Math.hypot((a.x+a.size/2)-px, (a.y+a.size/2)-py) < Math.hypot((b.x+b.size/2)-px, (b.y+b.size/2)-py) ? a : b) : null;
        let aimAngle = nearest ? Math.atan2((nearest.y+nearest.size/2)-py, (nearest.x+nearest.size/2)-px) : 0;

        if (wp.shuriken > 0) {
            timers.shuriken += fireBuff; let fireDelay = Math.max(4, 50 - wp.shuriken * 6);
            if (timers.shuriken > fireDelay && nearest) {
                timers.shuriken = 0; let sCount = 1 + Math.floor(wp.shuriken / 2);
                for (let i=0; i<sCount; i++) { let spread = (i - Math.floor(sCount/2)) * 0.2; bullets.push({ x: px, y: py, vx: Math.cos(aimAngle+spread)*9, vy: Math.sin(aimAngle+spread)*9, size: 5 + wp.shuriken, type: 'shuriken', life: 100, dmg: 1 + wp.shuriken*0.3 }); }
            }
        }
        if (wp.piercer > 0) {
            timers.piercer += fireBuff;
            if (timers.piercer > Math.max(15, 90 - wp.piercer * 8) && enemies.length > 0) {
                timers.piercer = 0; let rE = enemies[Math.floor(Math.random() * enemies.length)]; let a = Math.atan2((rE.y+rE.size/2)-py, (rE.x+rE.size/2)-px);
                bullets.push({ x: px, y: py, vx: Math.cos(a)*14, vy: Math.sin(a)*14, size: 8 + wp.piercer * 5, type: 'piercer', life: 100, dmg: 2 + wp.piercer*1.5 });
            }
        }
        if (wp.potassium > 0) {
            timers.potassium += fireBuff;
            if (timers.potassium > Math.max(20, 130 - wp.potassium * 10) && enemies.length > 0) {
                timers.potassium = 0; let bCount = 1 + Math.floor(wp.potassium / 3);
                for(let i=0; i<bCount; i++) { let rE = enemies[Math.floor(Math.random() * enemies.length)]; effects.push({ x: rE.x+rE.size/2, y: rE.y+rE.size/2, radius: 40 + (wp.potassium * 20), life: 25, type: 'explosion', dmg: 3 + wp.potassium*2.5 }); }
            }
        }
        if (wp.dialyzer > 0) {
            timers.dialyzer += fireBuff; 
            if (wp.dialyzer >= 10) {
                globalDialyzerAngle += 0.12; 
                if (timers.dialyzer > 2) {
                    timers.dialyzer = 0; let ways = 12; 
                    for(let i=0; i<ways; i++) { let d = globalDialyzerAngle + (Math.PI * 2 / ways) * i; bullets.push({ x: px, y: py, vx: Math.cos(d)*15, vy: Math.sin(d)*15, size: 25, type: 'dialyzer', life: 120, dmg: 40 }); }
                }
            } else {
                globalDialyzerAngle += 0.05 + (wp.dialyzer * 0.01);
                if (timers.dialyzer > Math.max(10, 80 - wp.dialyzer * 5)) {
                    timers.dialyzer = 0; let ways = 4 + Math.floor(wp.dialyzer / 2) * 2;
                    for(let i=0; i<ways; i++) { let d = globalDialyzerAngle + (Math.PI * 2 / ways) * i; bullets.push({ x: px, y: py, vx: Math.cos(d)*10, vy: Math.sin(d)*10, size: 5 + wp.dialyzer*2, type: 'dialyzer', life: 100, dmg: 1.5 + wp.dialyzer }); }
                }
            }
        }
        if (wp.resin > 0) {
            timers.resin += fireBuff;
            if (timers.resin > Math.max(20, 100 - wp.resin * 8)) { timers.resin = 0; bullets.push({ x: px, y: py, vx: 0, vy: 0, size: 15 + wp.resin * 6, type: 'resin', life: 250, dmg: 0.8 + wp.resin*0.3 }); }
        }
        if (wp.tolvaptan > 0) {
            timers.tolvaptan += fireBuff;
            if (timers.tolvaptan > Math.max(15, 90 - wp.tolvaptan * 8) && nearest) {
                timers.tolvaptan = 0; let tCount = 3 + wp.tolvaptan * 2;
                for (let i=0; i<tCount; i++) { let spread = (i - Math.floor(tCount/2)) * 0.25; bullets.push({ x: px, y: py, vx: Math.cos(aimAngle+spread)*7, vy: Math.sin(aimAngle+spread)*7, size: 10 + wp.tolvaptan, type: 'tolvaptan', life: 70, dmg: 1.2 + wp.tolvaptan*0.5 }); }
            }
        }
        if (wp.mra > 0) {
            timers.mra += fireBuff;
            if (timers.mra > Math.max(15, 90 - wp.mra * 8) && nearest) {
                timers.mra = 0; let mCount = 1 + Math.floor(wp.mra / 3);
                for(let i=0; i<mCount; i++) { let rndSpread = (Math.random() - 0.5); bullets.push({ x: px, y: py, vx: Math.cos(aimAngle+rndSpread)*11, vy: Math.sin(aimAngle+rndSpread)*11, size: 12 + wp.mra * 4, type: 'mra', life: 100, dmg: 2 + wp.mra*1.5 }); }
            }
        }

        let auraRadius = wp.calcium > 0 ? 60 + (wp.calcium * 20) : 0;
        let shields = [];
        if (wp.shield > 0) {
            shieldAngle += 0.05 + (wp.shield * 0.01);
            let sCount = Math.min(12, wp.shield * 2 + 2); let sRad = 50 + (wp.shield * 8); let sSize = 10 + (wp.shield * 3);
            for(let i=0; i<sCount; i++) shields.push({ x: px + Math.cos(shieldAngle + (Math.PI*2/sCount)*i)*sRad, y: py + Math.sin(shieldAngle + (Math.PI*2/sCount)*i)*sRad, size: sSize });
        }

        function damageEnemy(eIndex, dmg) {
            let e = enemies[eIndex]; e.hp -= dmg;
            if(e.hp <= 0) {
                let gemSize = e.isBoss ? 20 : 5;
                gems.push({ x: e.x + e.size/2, y: e.y + e.size/2, val: e.exp, size: gemSize });
                enemies.splice(eIndex, 1); return true;
            }
            return false;
        }

        for (let i = bullets.length - 1; i >= 0; i--) {
            let b = bullets[i]; b.x += b.vx; b.y += b.vy; b.life--;
            if (b.type === 'mra' && b.life === 50) { b.vx *= -1; b.vy *= -1; }
            if (b.life <= 0 || b.x < -100 || b.x > 800 || b.y < -100 || b.y > 600) { bullets.splice(i, 1); continue; }
            let destroyed = false;
            for (let j = enemies.length - 1; j >= 0; j--) {
                let e = enemies[j];
                if (Math.hypot(b.x - (e.x+e.size/2), b.y - (e.y+e.size/2)) < b.size + e.size/2) {
                    damageEnemy(j, b.dmg);
                    if (b.type === 'shuriken' || b.type === 'tolvaptan') { destroyed = true; break; } 
                }
            }
            if (destroyed) bullets.splice(i, 1);
        }

        for (let i = enemies.length - 1; i >= 0; i--) {
            let e = enemies[i]; let ex = e.x+e.size/2; let ey = e.y+e.size/2; let dmgToTake = 0;
            if (auraRadius > 0 && Math.hypot(ex - px, ey - py) < auraRadius) dmgToTake += 0.5 + wp.calcium * 0.2; 
            for (let s of shields) { if (Math.hypot(ex - s.x, ey - s.y) < e.size/2 + s.size) dmgToTake += 2 + wp.shield; } 
            for (let eff of effects) { if (eff.type === 'explosion' && Math.hypot(ex - eff.x, ey - eff.y) < eff.radius) dmgToTake += eff.dmg; }
            if (dmgToTake > 0) damageEnemy(i, dmgToTake);
        }

        enemies.forEach(e => { 
            e.timeOffset += 0.05;
            if (e.moveType === 'random') {
                if (!e.vx || Math.random() < 0.02) { let angle = Math.random() * Math.PI * 2; e.vx = Math.cos(angle) * e.speed; e.vy = Math.sin(angle) * e.speed; }
                e.x += e.vx; e.y += e.vy;
                if(e.x < -150) e.vx = Math.abs(e.vx); if(e.x > 850) e.vx = -Math.abs(e.vx); if(e.y < -150) e.vy = Math.abs(e.vy); if(e.y > 650) e.vy = -Math.abs(e.vy);
            } 
            else if (e.moveType === 'sine') {
                let baseAngle = Math.atan2(py - (e.y+e.size/2), px - (e.x+e.size/2));
                let waveAngle = baseAngle + Math.sin(e.timeOffset) * 1.5; 
                e.x += Math.cos(waveAngle) * e.speed; e.y += Math.sin(waveAngle) * e.speed;
            } 
            else {
                let a = Math.atan2(py - (e.y+e.size/2), px - (e.x+e.size/2)); e.x += Math.cos(a) * e.speed; e.y += Math.sin(a) * e.speed; 
            }
            
            if (player.invincible <= 0) {
                let distToPlayer = Math.hypot(px - (e.x + e.size/2), py - (e.y + e.size/2));
                if (distToPlayer < 12 + e.size/2) {
                    // 🌟 難易度による被ダメージの変化
                    let baseDmg = e.isBoss ? 30 : 10;
                    player.hp -= (difficulty === 'easy') ? Math.floor(baseDmg / 2) : baseDmg;
                    player.invincible = 60; 
                    
                    if (player.hp <= 0) {
                        player.hp = 0;
                        triggerGameOver();
                    }
                }
            }
        });

        for (let i = gems.length - 1; i >= 0; i--) {
            let g = gems[i]; let d = Math.hypot(px - g.x, py - g.y);
            if (d < 100 + (wp.epo * 15)) { 
                let a = Math.atan2(py - g.y, px - g.x); g.x += Math.cos(a)*8; g.y += Math.sin(a)*8;
                if (d < 20) { 
                    player.exp += g.val; gems.splice(i, 1);
                    if (player.exp >= player.nextExp) {
                        player.level++; 
                        player.exp = 0; 
                        // 🌟 EASYはレベルアップ必要経験値が少ない
                        let expBase = difficulty === 'easy' ? 3 : 5;
                        player.nextExp += Math.floor(expBase * Math.pow(player.level, 1.2)); 
                        triggerQuiz();
                    }
                }
            }
        }
        for (let i = effects.length - 1; i >= 0; i--) { effects[i].life--; if (effects[i].life <= 0) effects.splice(i, 1); }
    }

    function draw() {
        ctx.clearRect(0, 0, 700, 500);
        if (!gameStarted) return; // スタート前は描画しない

        if (wp.calcium > 0) { ctx.fillStyle = "rgba(255, 255, 255, 0.12)"; ctx.beginPath(); ctx.arc(player.x+12, player.y+12, 60 + (wp.calcium * 20), 0, Math.PI*2); ctx.fill(); }
        effects.forEach(eff => { if(eff.type === 'explosion') { ctx.fillStyle = `rgba(231, 76, 60, ${eff.life / 25})`; ctx.beginPath(); ctx.arc(eff.x, eff.y, eff.radius, 0, Math.PI*2); ctx.fill(); } });

        ctx.fillStyle = "#3498db"; gems.forEach(g => { ctx.beginPath(); ctx.arc(g.x, g.y, g.size, 0, Math.PI*2); ctx.fill(); });
        
        ctx.textAlign = "center"; ctx.textBaseline = "middle";
        enemies.forEach(e => { ctx.font = Math.floor(e.size) + "px Arial"; ctx.fillText(e.emoji, e.x + e.size/2, e.y + e.size/2); });
        
        ctx.fillStyle = "rgba(46, 204, 113, 0.8)";
        if (wp.shield > 0) {
            let count = Math.min(12, wp.shield * 2 + 2); let radius = 50 + (wp.shield * 8); let size = 10 + (wp.shield * 3);
            for(let i=0; i<count; i++) { let a = shieldAngle + (Math.PI * 2 / count) * i; ctx.beginPath(); ctx.arc(player.x+12 + Math.cos(a)*radius, player.y+12 + Math.sin(a)*radius, size, 0, Math.PI*2); ctx.fill(); }
        }

        bullets.forEach(b => { 
            if (b.type === 'shuriken') ctx.fillStyle = "#f1c40f"; else if (b.type === 'piercer') ctx.fillStyle = "#00a8ff"; else if (b.type === 'dialyzer') ctx.fillStyle = "#00d2d3"; else if (b.type === 'resin') ctx.fillStyle = "#2d3436"; else if (b.type === 'tolvaptan') ctx.fillStyle = "#48dbfb"; else if (b.type === 'mra') ctx.fillStyle = "#9b59b6";
            ctx.beginPath(); ctx.arc(b.x, b.y, b.size, 0, Math.PI*2); ctx.fill(); 
        });

        if (bossWarningTimer > 0) {
            bossWarningTimer--;
            ctx.fillStyle = "red"; ctx.font = "bold 40px Arial"; ctx.fillText("⚠️ 巨大ボス接近 ⚠️", 350, 100);
            if (bossWarningTimer % 20 > 10) { ctx.strokeStyle = "rgba(255, 0, 0, 0.5)"; ctx.lineWidth = 10; ctx.strokeRect(5, 5, 690, 490); }
        }

        if (player.invincible <= 0 || Math.floor(frameCount / 5) % 2 === 0) {
            ctx.font = "28px Arial"; 
            ctx.fillText("🥷", player.x + 12, player.y + 12);
        }

        ctx.fillStyle = "#e74c3c"; ctx.fillRect(player.x - 8, player.y + 35, 40, 6);
        ctx.fillStyle = "#2ecc71"; ctx.fillRect(player.x - 8, player.y + 35, 40 * (player.hp / player.maxHp), 6);
        
        ctx.textAlign = "left"; ctx.textBaseline = "alphabetic";
        ctx.fillStyle = "white"; ctx.font = "bold 18px Arial"; ctx.fillText("Lv: " + player.level, 15, 30);
        ctx.fillStyle = "#555"; ctx.fillRect(80, 15, 200, 12);
        ctx.fillStyle = "#2ecc71"; ctx.fillRect(80, 15, 200 * (player.exp / player.nextExp), 12);
    }

    function loop() { 
        if (gameStarted && !isPaused) { update(); draw(); } 
        requestAnimationFrame(loop); 
    }
    window.onload = loop;
</script>
</body>
</html>
"""

components.html(html_code, height=850)
