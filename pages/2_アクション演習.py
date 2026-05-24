import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="ヴァンサバ風・酸塩基アクション", page_icon="🥷", layout="wide")

st.title("🥷 ヴァンサバ風・酸塩基サバイバル V4")
st.write("キーボード（矢印キー）とスマホ（ジョイスティック）の両方で快適に操作できます！")
st.write("クイズ正解後、ランダムに提示される3つの武器から好きなものを選択してビルドを組みましょう。")

html_code = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
    body { margin: 0; background: #f0f2f6; display: flex; flex-direction: column; align-items: center; font-family: 'Helvetica Neue', Arial, sans-serif; overflow: hidden; }
    
    #game-container { display: flex; flex-direction: column; width: 100%; max-width: 700px; background: #fff; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); overflow: hidden; -webkit-touch-callout: none; user-select: none; }
    #canvas-wrapper { position: relative; width: 100%; aspect-ratio: 7 / 5; }
    canvas { width: 100%; height: 100%; background-color: #2c3e50; display: block; }

    #controller-area { width: 100%; height: 180px; background: #e5e9f0; display: flex; justify-content: center; align-items: center; position: relative; border-top: 2px solid #ccc; }
    #joystick-zone { width: 120px; height: 120px; background: rgba(0, 0, 0, 0.1); border: 3px solid rgba(0, 0, 0, 0.2); border-radius: 50%; position: relative; touch-action: none; }
    #joystick-knob { position: absolute; top: 50%; left: 50%; width: 55px; height: 55px; background: #4a5568; border-radius: 50%; transform: translate(-50%, -50%); box-shadow: 0 4px 8px rgba(0,0,0,0.3); pointer-events: none; }

    #quiz-overlay { display: none; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.85); z-index: 20; }
    #quiz-box { position: absolute; top: 15px; left: 50%; transform: translateX(-50%); background: #fff; padding: 20px; border-radius: 12px; text-align: center; width: 90%; max-height: 90%; overflow-y: auto; border: 4px solid #f1c40f; box-sizing: border-box; }

    .quiz-title { color: #e74c3c; font-size: 20px; margin: 0 0 10px 0; font-weight: bold; }
    .data-card { background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 8px; padding: 10px; margin-bottom: 15px; display: flex; flex-direction: column; gap: 4px; }
    .data-val { font-family: monospace; font-size: 18px; color: #2c3e50; font-weight: bold; }

    #quiz-buttons { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 10px; }
    .quiz-btn { background: #3498db; color: white; border: none; border-radius: 8px; padding: 15px 5px; font-size: 13px; font-weight: bold; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: 0.1s; }
    .quiz-btn:active { background: #2980b9; transform: scale(0.95); }

    /* 報酬選択用の1列ボタン */
    #reward-buttons { display: flex; flex-direction: column; gap: 10px; }
    .reward-btn { background: #f39c12; color: white; border: none; border-radius: 8px; padding: 12px; text-align: left; cursor: pointer; transition: 0.1s; }
    .reward-btn b { font-size: 16px; display: block; margin-bottom: 4px; }
    .reward-btn small { font-size: 12px; opacity: 0.9; }
    .reward-btn:active { background: #e67e22; transform: scale(0.98); }
</style>
</head>
<body>

<div id="game-container">
    <div id="canvas-wrapper">
        <canvas id="gameCanvas" width="700" height="500"></canvas>
        <div id="quiz-overlay">
            <div id="quiz-box">
                </div>
        </div>
    </div>
    
    <div id="controller-area">
        <div id="joystick-zone">
            <div id="joystick-knob"></div>
        </div>
    </div>
</div>

<script>
    const canvas = document.getElementById("gameCanvas");
    const ctx = canvas.getContext("2d");
    const overlay = document.getElementById("quiz-overlay");
    const quizBox = document.getElementById("quiz-box");

    let isPaused = false;
    let frameCount = 0;
    let player = { x: 350, y: 250, size: 24, speed: 3.5, level: 1, exp: 0, nextExp: 3 };
    let enemies = []; let bullets = []; let gems = []; let effects = [];
    let joyVector = { x: 0, y: 0 };
    let keys = {};

    // 🌟 10種類の武器データ庫
    const weaponDB = {
        shuriken:  { name: "🟡 クエン酸手裏剣", desc: "最も近い敵を自動で狙い撃つ基本弾" },
        shield:    { name: "🟢 重曹シールド", desc: "自身の周囲を回転し、敵を弾き飛ばす" },
        piercer:   { name: "🔵 フロセミド貫通弾", desc: "一直線に敵を貫通する水流を放つ" },
        potassium: { name: "🔴 カリウム爆弾", desc: "ランダムな敵の位置で大爆発を起こす" },
        calcium:   { name: "⚪ カルシウム・オーラ", desc: "自身の周囲に継続ダメージ領域を展開" },
        dialyzer:  { name: "🌐 透析クロスレイ", desc: "上下左右の4方向へ同時にビームを放つ" },
        resin:     { name: "⚫ レジン・トラップ", desc: "歩いた跡に敵を吸着する罠を設置する" },
        tolvaptan: { name: "🌊 トルバプタン波", desc: "敵に向かって3方向に広がる波を放つ" },
        mra:       { name: "🟣 MRAブーメラン", desc: "飛んでいき、一定時間後に手元に戻る" },
        epo:       { name: "✨ エリスロポエチン", desc: "[強化] 自身の移動と全攻撃速度がアップ" }
    };

    // 現在の所持レベル（初期状態は手裏剣Lv1のみ）
    let wp = { shuriken: 1, shield: 0, piercer: 0, potassium: 0, calcium: 0, dialyzer: 0, resin: 0, tolvaptan: 0, mra: 0, epo: 0 };
    let timers = { shuriken: 0, piercer: 0, potassium: 0, dialyzer: 0, resin: 0, tolvaptan: 0, mra: 0 };
    let shieldAngle = 0;

    // --- クイズ生成 ---
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

    function triggerQuiz() {
        isPaused = true;
        endJoy(); // ジョイスティックリセット
        const q = generateAcidBaseCase();
        
        let html = `
            <div class="quiz-title">🆙 レベルアップ！診断せよ</div>
            <div class="data-card">
                <div class="data-val">pH : ${q.pH}</div>
                <div class="data-val">PaCO2 : ${q.PaCO2} mmHg</div>
                <div class="data-val">HCO3- : ${q.HCO3} mEq/L</div>
            </div>
            <div id="quiz-buttons">
        `;
        q.options.forEach(opt => {
            html += `<button class="quiz-btn" onclick="checkAnswer('${opt}', '${q.ans}')">${opt}</button>`;
        });
        html += `</div>`;
        quizBox.innerHTML = html;
        overlay.style.display = "block";
    }

    function checkAnswer(selected, correct) {
        if (selected === correct) {
            showRewardSelection(); // 正解なら武器選択画面へ！
        } else {
            alert("誤診です...\\nボーナス獲得ならず。生き延びてください！");
            overlay.style.display = "none";
            isPaused = false;
            loop();
        }
    }

    // 🌟 3択の武器提示システム
    function showRewardSelection() {
        let available = Object.keys(weaponDB);
        available.sort(() => 0.5 - Math.random());
        let choices = available.slice(0, 3); // ランダムに3つ選出
        
        let html = `<div class="quiz-title">🎁 報酬を選択（3択）</div><div id="reward-buttons">`;
        choices.forEach(key => {
            let w = weaponDB[key];
            let currentLv = wp[key];
            html += `<button class="reward-btn" onclick="selectReward('${key}')">
                        <b>${w.name} (Lv ${currentLv} → ${currentLv + 1})</b>
                        <small>${w.desc}</small>
                     </button>`;
        });
        html += `</div>`;
        quizBox.innerHTML = html;
    }

    function selectReward(weaponKey) {
        wp[weaponKey]++;
        overlay.style.display = "none";
        isPaused = false;
        loop();
    }

    // --- コントローラー入力 ---
    const joyZone = document.getElementById("joystick-zone"); const joyKnob = document.getElementById("joystick-knob");
    let isDragging = false; let joyCenter = { x: 0, y: 0 }; const maxRadius = 45;

    function startJoy(e) { e.preventDefault(); isDragging = true; const rect = joyZone.getBoundingClientRect(); joyCenter = { x: rect.left + rect.width / 2, y: rect.top + rect.height / 2 }; }
    function moveJoy(e) {
        if (!isDragging) return;
        const clientX = e.touches ? e.touches[0].clientX : e.clientX; const clientY = e.touches ? e.touches[0].clientY : e.clientY;
        let dx = clientX - joyCenter.x; let dy = clientY - joyCenter.y; let dist = Math.hypot(dx, dy);
        if (dist > maxRadius) { dx *= maxRadius / dist; dy *= maxRadius / dist; }
        joyKnob.style.transform = `translate(calc(-50% + ${dx}px), calc(-50% + ${dy}px))`;
        joyVector = { x: dx / maxRadius, y: dy / maxRadius };
    }
    function endJoy() { isDragging = false; joyKnob.style.transform = `translate(-50%, -50%)`; joyVector = { x: 0, y: 0 }; }
    joyZone.addEventListener("touchstart", startJoy, {passive:false}); window.addEventListener("touchmove", moveJoy, {passive:false}); window.addEventListener("touchend", endJoy);
    joyZone.addEventListener("mousedown", startJoy); window.addEventListener("mousemove", moveJoy); window.addEventListener("mouseup", endJoy);

    window.addEventListener("keydown", e => { keys[e.key] = true; if(["ArrowUp","ArrowDown","ArrowLeft","ArrowRight"].includes(e.key)) e.preventDefault(); });
    window.addEventListener("keyup", e => keys[e.key] = false);

    // --- ゲームループ ---
    function update() {
        frameCount++;
        
        // 🌟 PCキーボードとスマホジョイスティックの両立修正！
        let moveX = 0; let moveY = 0;
        if (keys["ArrowUp"]) moveY -= 1;
        if (keys["ArrowDown"]) moveY += 1;
        if (keys["ArrowLeft"]) moveX -= 1;
        if (keys["ArrowRight"]) moveX += 1;
        if (moveX !== 0 || moveY !== 0) {
            let dist = Math.hypot(moveX, moveY); moveX = moveX / dist; moveY = moveY / dist;
        } else {
            moveX = joyVector.x; moveY = joyVector.y;
        }

        // EPOによる移動速度バフ
        let speedBuff = 1 + (wp.epo * 0.15);
        let fireBuff = 1 + (wp.epo * 0.1);

        player.x += moveX * player.speed * speedBuff; 
        player.y += moveY * player.speed * speedBuff;
        player.x = Math.max(0, Math.min(canvas.width - player.size, player.x));
        player.y = Math.max(0, Math.min(canvas.height - player.size, player.y));

        let px = player.x + 12; let py = player.y + 12;

        if (frameCount % Math.max(8, 45 - player.level * 2) === 0) {
            let ex = Math.random() < 0.5 ? -20 : 720; let ey = Math.random() * 500;
            enemies.push({ x: ex, y: ey, size: 16, speed: 1.2 + player.level * 0.1 });
        }

        // ================= 武器の発射ロジック =================
        let nearest = enemies.length > 0 ? enemies.reduce((a, b) => Math.hypot((a.x+8)-px, (a.y+8)-py) < Math.hypot((b.x+8)-px, (b.y+8)-py) ? a : b) : null;
        let aimAngle = nearest ? Math.atan2((nearest.y+8)-py, (nearest.x+8)-px) : 0;

        // 1. クエン酸手裏剣
        if (wp.shuriken > 0) {
            timers.shuriken += fireBuff;
            if (timers.shuriken > Math.max(10, 60 - wp.shuriken * 5) && nearest) {
                timers.shuriken = 0;
                bullets.push({ x: px, y: py, vx: Math.cos(aimAngle)*8, vy: Math.sin(aimAngle)*8, size: 5, type: 'shuriken', life: 100, maxLife: 100 });
                if(wp.shuriken >= 3) { // 3WAY
                    bullets.push({ x: px, y: py, vx: Math.cos(aimAngle+0.3)*8, vy: Math.sin(aimAngle+0.3)*8, size: 5, type: 'shuriken', life: 100, maxLife: 100 });
                    bullets.push({ x: px, y: py, vx: Math.cos(aimAngle-0.3)*8, vy: Math.sin(aimAngle-0.3)*8, size: 5, type: 'shuriken', life: 100, maxLife: 100 });
                }
            }
        }
        // 3. フロセミド貫通弾
        if (wp.piercer > 0) {
            timers.piercer += fireBuff;
            if (timers.piercer > Math.max(20, 100 - wp.piercer * 10) && enemies.length > 0) {
                timers.piercer = 0;
                let rndEnemy = enemies[Math.floor(Math.random() * enemies.length)];
                let a = Math.atan2((rndEnemy.y+8)-py, (rndEnemy.x+8)-px);
                bullets.push({ x: px, y: py, vx: Math.cos(a)*12, vy: Math.sin(a)*12, size: 6+wp.piercer, type: 'piercer', life: 100, maxLife: 100 });
            }
        }
        // 4. カリウム爆弾
        if (wp.potassium > 0) {
            timers.potassium += fireBuff;
            if (timers.potassium > Math.max(30, 150 - wp.potassium * 10) && enemies.length > 0) {
                timers.potassium = 0;
                let rndEnemy = enemies[Math.floor(Math.random() * enemies.length)];
                effects.push({ x: rndEnemy.x+8, y: rndEnemy.y+8, radius: 40 + (wp.potassium * 10), life: 20, type: 'explosion' });
            }
        }
        // 6. 透析クロスレイ
        if (wp.dialyzer > 0) {
            timers.dialyzer += fireBuff;
            if (timers.dialyzer > Math.max(15, 90 - wp.dialyzer * 8)) {
                timers.dialyzer = 0;
                let dirs = [0, Math.PI/2, Math.PI, Math.PI*1.5];
                dirs.forEach(d => bullets.push({ x: px, y: py, vx: Math.cos(d)*7, vy: Math.sin(d)*7, size: 5+wp.dialyzer, type: 'dialyzer', life: 100, maxLife: 100 }));
            }
        }
        // 7. レジントラップ
        if (wp.resin > 0) {
            timers.resin += fireBuff;
            if (timers.resin > Math.max(30, 120 - wp.resin * 10)) {
                timers.resin = 0;
                bullets.push({ x: px, y: py, vx: 0, vy: 0, size: 10+wp.resin*2, type: 'resin', life: 200, maxLife: 200 }); // 動かず留まる
            }
        }
        // 8. トルバプタン波
        if (wp.tolvaptan > 0) {
            timers.tolvaptan += fireBuff;
            if (timers.tolvaptan > Math.max(20, 100 - wp.tolvaptan * 10) && nearest) {
                timers.tolvaptan = 0;
                let angles = [aimAngle, aimAngle+0.2, aimAngle-0.2];
                if(wp.tolvaptan > 2) { angles.push(aimAngle+0.4, aimAngle-0.4); } // 広がる
                angles.forEach(a => bullets.push({ x: px, y: py, vx: Math.cos(a)*6, vy: Math.sin(a)*6, size: 8, type: 'tolvaptan', life: 60, maxLife: 60 }));
            }
        }
        // 9. MRAブーメラン
        if (wp.mra > 0) {
            timers.mra += fireBuff;
            if (timers.mra > Math.max(20, 100 - wp.mra * 10) && nearest) {
                timers.mra = 0;
                bullets.push({ x: px, y: py, vx: Math.cos(aimAngle)*9, vy: Math.sin(aimAngle)*9, size: 7+wp.mra, type: 'mra', life: 80, maxLife: 80 });
            }
        }

        // ================= 当たり判定 & 処理 =================
        // 5. カルシウムオーラ（バレットではなく範囲判定）
        let auraRadius = 0;
        if (wp.calcium > 0) {
            auraRadius = 50 + (wp.calcium * 15);
        }

        // 2. 重曹シールドの計算
        let shields = [];
        if (wp.shield > 0) {
            shieldAngle += 0.04 + (wp.shield * 0.005);
            let shieldCount = Math.min(6, wp.shield + 1);
            let shieldRadius = 45 + (wp.shield * 5);
            let shieldSize = 8 + (wp.shield * 2);
            for(let i=0; i<shieldCount; i++) {
                let a = shieldAngle + (Math.PI * 2 / shieldCount) * i;
                shields.push({ x: px + Math.cos(a)*shieldRadius, y: py + Math.sin(a)*shieldRadius, size: shieldSize });
            }
        }

        // 弾の移動と寿命
        for (let i = bullets.length - 1; i >= 0; i--) {
            let b = bullets[i];
            b.x += b.vx; b.y += b.vy;
            b.life--;
            
            // MRAブーメランの反転ギミック
            if (b.type === 'mra' && b.life === Math.floor(b.maxLife / 2)) {
                b.vx *= -1; b.vy *= -1;
            }

            if (b.life <= 0 || b.x < -50 || b.x > 750 || b.y < -50 || b.y > 550) { bullets.splice(i, 1); continue; }
            
            let destroyed = false;
            for (let j = enemies.length - 1; j >= 0; j--) {
                let e = enemies[j];
                if (Math.hypot(b.x - (e.x+8), b.y - (e.y+8)) < b.size + 8) {
                    gems.push({ x: e.x+8, y: e.y+8 }); enemies.splice(j, 1);
                    // 貫通しない弾は消える
                    if (b.type === 'shuriken' || b.type === 'tolvaptan') { destroyed = true; break; }
                }
            }
            if (destroyed) bullets.splice(i, 1);
        }

        // オーラ、シールド、爆発の判定
        for (let i = enemies.length - 1; i >= 0; i--) {
            let e = enemies[j = i]; let ex = e.x+8; let ey = e.y+8;
            let hit = false;
            // カルシウムオーラ
            if (auraRadius > 0 && Math.hypot(ex - px, ey - py) < auraRadius) hit = true;
            // 重曹シールド
            for (let s of shields) { if (Math.hypot(ex - s.x, ey - s.y) < 8 + s.size) hit = true; }
            // カリウム爆発エフェクト
            for (let eff of effects) { if (eff.type === 'explosion' && Math.hypot(ex - eff.x, ey - eff.y) < eff.radius) hit = true; }
            
            if (hit) { gems.push({ x: ex, y: ey }); enemies.splice(i, 1); }
        }

        // 敵移動
        enemies.forEach(e => { let a = Math.atan2(py - (e.y+8), px - (e.x+8)); e.x += Math.cos(a) * e.speed; e.y += Math.sin(a) * e.speed; });

        // ジェム回収
        for (let i = gems.length - 1; i >= 0; i--) {
            let g = gems[i]; let d = Math.hypot(px - g.x, py - g.y);
            if (d < 90 + (wp.epo * 10)) { // EPOで回収範囲も少し広がる
                let a = Math.atan2(py - g.y, px - g.x); g.x += Math.cos(a)*7; g.y += Math.sin(a)*7;
                if (d < 20) { 
                    player.exp++; gems.splice(i, 1);
                    if (player.exp >= player.nextExp) {
                        player.level++; player.exp = 0; player.nextExp += Math.floor(player.level * 1.5);
                        triggerQuiz();
                    }
                }
            }
        }

        // エフェクト寿命
        for (let i = effects.length - 1; i >= 0; i--) {
            effects[i].life--;
            if (effects[i].life <= 0) effects.splice(i, 1);
        }
    }

    function draw() {
        ctx.clearRect(0, 0, 700, 500);
        
        // カルシウムオーラ描画（白半透明）
        if (wp.calcium > 0) {
            ctx.fillStyle = "rgba(255, 255, 255, 0.15)";
            ctx.beginPath(); ctx.arc(player.x+12, player.y+12, 50 + (wp.calcium * 15), 0, Math.PI*2); ctx.fill();
        }

        // エフェクト描画
        effects.forEach(eff => {
            if(eff.type === 'explosion') {
                ctx.fillStyle = `rgba(231, 76, 60, ${eff.life / 20})`; // 赤から透明へ
                ctx.beginPath(); ctx.arc(eff.x, eff.y, eff.radius, 0, Math.PI*2); ctx.fill();
            }
        });

        // ジェム、敵
        ctx.fillStyle = "#3498db"; gems.forEach(g => { ctx.beginPath(); ctx.arc(g.x, g.y, 6, 0, Math.PI*2); ctx.fill(); });
        ctx.fillStyle = "#e74c3c"; enemies.forEach(e => ctx.fillRect(e.x, e.y, 16, 16));
        
        // 重曹シールド描画
        ctx.fillStyle = "rgba(46, 204, 113, 0.8)";
        if (wp.shield > 0) {
            let count = Math.min(6, wp.shield + 1); let radius = 45 + (wp.shield * 5); let size = 8 + (wp.shield * 2);
            for(let i=0; i<count; i++) {
                let a = shieldAngle + (Math.PI * 2 / count) * i;
                ctx.beginPath(); ctx.arc(player.x+12 + Math.cos(a)*radius, player.y+12 + Math.sin(a)*radius, size, 0, Math.PI*2); ctx.fill();
            }
        }

        // 弾描画 (種類で色分け)
        bullets.forEach(b => { 
            if (b.type === 'shuriken') ctx.fillStyle = "#f1c40f";
            else if (b.type === 'piercer') ctx.fillStyle = "#00a8ff";
            else if (b.type === 'dialyzer') ctx.fillStyle = "#00d2d3";
            else if (b.type === 'resin') ctx.fillStyle = "#2d3436";
            else if (b.type === 'tolvaptan') ctx.fillStyle = "#48dbfb";
            else if (b.type === 'mra') ctx.fillStyle = "#9b59b6";
            ctx.beginPath(); ctx.arc(b.x, b.y, b.size, 0, Math.PI*2); ctx.fill(); 
        });

        ctx.fillStyle = "white"; ctx.font = "28px Arial"; ctx.fillText("🥷", player.x, player.y + 24);
        ctx.fillStyle = "white"; ctx.font = "bold 18px Arial"; ctx.fillText("Lv: " + player.level, 15, 30);
        ctx.fillStyle = "#555"; ctx.fillRect(80, 15, 200, 12);
        ctx.fillStyle = "#2ecc71"; ctx.fillRect(80, 15, 200 * (player.exp / player.nextExp), 12);
    }

    function loop() { if (!isPaused) { update(); draw(); requestAnimationFrame(loop); } }
    window.onload = loop;
</script>
</body>
</html>
"""

components.html(html_code, height=850)