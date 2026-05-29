import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="ナースダッシュ！", page_icon="💉", layout="wide")
st.title("🏃‍♀️ ナースダッシュ！ 救命クイズラン V12")
st.write("ライフ（❤️）に気をつけて！クイズ正解や回復アイテム（💖）で回復し、高評価の称号を目指そう！")

html_code = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
    body { margin: 0; background: #f0f2f6; display: flex; flex-direction: column; align-items: center; font-family: 'Helvetica Neue', Arial, sans-serif; overflow: hidden; overscroll-behavior: none; touch-action: none; }
    #game-container { position: relative; width: 100%; max-width: 700px; aspect-ratio: 7 / 4; background: #87CEEB; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
    canvas { width: 100%; height: 100%; display: block; }
    
    #quiz-overlay { display: none; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.85); z-index: 20; }
    
    /* 🌟 クイズボックスのスマホ最適化（コンパクト化＆スクロール対応） */
    #quiz-box { 
        position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); 
        background: #fff; padding: 12px; border-radius: 10px; text-align: center; 
        width: 95%; max-width: 500px; max-height: 95%; overflow-y: auto; 
        border: 4px solid #e74c3c; touch-action: pan-y; box-sizing: border-box;
    }
    .quiz-title { color: #e74c3c; font-size: 18px; margin-bottom: 8px; font-weight: bold; }
    .quiz-text { font-size: 14px; color: #2c3e50; margin-bottom: 12px; text-align: left; line-height: 1.3; font-weight: bold; }
    .quiz-btn { 
        display: block; width: 100%; background: #3498db; color: white; border: none; 
        border-radius: 6px; padding: 10px 8px; font-size: 14px; font-weight: bold; 
        margin-bottom: 6px; cursor: pointer; transition: 0.1s; box-sizing: border-box;
    }
    .quiz-btn:active { background: #2980b9; transform: scale(0.98); }
    .game-over-btn { background: #e74c3c; margin-top: 10px; } .game-over-btn:active { background: #c0392b; }
</style>
</head>
<body>
<div id="game-container">
    <canvas id="gameCanvas" width="700" height="400"></canvas>
    <div id="quiz-overlay"><div id="quiz-box"></div></div>
</div>

<script>
    const canvas = document.getElementById("gameCanvas");
    const ctx = canvas.getContext("2d");
    const overlay = document.getElementById("quiz-overlay");
    const quizBox = document.getElementById("quiz-box");

    let isPaused = false;
    let isGameClear = false;
    let isGameOver = false; 
    let frameCount = 0;
    let score = 0;
    let baseScrollSpeed = 4.5;
    
    const BOSS_SPAWN_FRAME = 18000; 
    let boss = null;

    let bgScrollCloud = 0; let bgScrollMountain = 0; let bgScrollCity = 0;

    let player = { 
        x: 100, y: 300, size: 40, vy: 0, gravity: 0.6, jumpPower: -10.5, 
        isGrounded: false, invincible: 0, jumpCount: 0, maxJumps: 2, isHurt: 0,
        lives: 3, maxLives: 5 
    };

    let obstacles = []; let questionBlocks = []; let coins = []; let gems = []; let hearts = []; let effects = [];
    let gameMessage = { text: "🏥 勤務スタート！", subtext: "安全第一で進みましょう", life: 120, color: "#fff" };
    const groundY = 350; 

    const phaseConfigs = [
        { name: "☀️ 日勤帯", sky: "#87CEEB", mtn: "#546de5", city: "#2d3436", gnd: "#8B4513", grass: "#228B22" }, 
        { name: "🌇 夕勤帯", sky: "#ff9f43", mtn: "#ee5253", city: "#222f3e", gnd: "#833471", grass: "#006266" }, 
        { name: "🌙 夜勤入り", sky: "#2c3e50", mtn: "#34495e", city: "#111111", gnd: "#3b2a2a", grass: "#192a56" }, 
        { name: "🚑 救急搬送", sky: "#8e44ad", mtn: "#9b59b6", city: "#2c3e50", gnd: "#2d3436", grass: "#1e272e" }, 
        { name: "🚨 深夜の急変", sky: "#c0392b", mtn: "#e74c3c", city: "#2d3436", gnd: "#2c3e50", grass: "#b33939" }, 
        { name: "☣️ 謎の感染源", sky: "#1abc9c", mtn: "#16a085", city: "#111111", gnd: "#273c75", grass: "#192a56" }, 
        { name: "🏥 カオス病棟", sky: "#f39c12", mtn: "#d35400", city: "#2c3e50", gnd: "#8B4513", grass: "#e1b12c" }, 
        { name: "🌪️ 嵐の予感", sky: "#00a8ff", mtn: "#0097e6", city: "#2f3640", gnd: "#718093", grass: "#353b48" }, 
        { name: "🔥 ボス前兆", sky: "#e84118", mtn: "#c23616", city: "#192a56", gnd: "#2f3640", grass: "#ff4757" }, 
        { name: "👹 総力戦", sky: "#2f3542", mtn: "#57606f", city: "#000000", gnd: "#2f3542", grass: "#ff4757" }  
    ];

    const nurseQuizzes = [
        { q: "シャント音の聴取において、狭窄を疑う所見はどれ？", options: ["低調な連続性雑音（ザー）", "高調なピッチ音（ヒュー）", "拍動のみで音が聞こえない"], ans: "高調なピッチ音（ヒュー）" },
        { q: "透析中に患者が「目の前が暗くなる」と訴え、血圧が低下。最初の対応として適切なのは？", options: ["下肢を挙上する（トレンデレンブルグ位）", "頭部を挙上する（ファーラー位）", "除水速度を上げる"], ans: "下肢を挙上する（トレンデレンブルグ位）" },
        { q: "カリウム値が 6.5 mEq/L の患者。心電図で最初に見られる典型的な変化は？", options: ["テント状T波", "ST低下", "U波の出現"], ans: "テント状T波" },
        { q: "除水エラーを防ぐための最も基本で効果的な対策は？", options: ["ダブルチェックと指差呼称", "設定値を暗記する", "アラームが鳴るまで待つ"], ans: "ダブルチェックと指差呼称" }
    ];

    function jump() {
        if (!isPaused && !isGameClear && !isGameOver && player.jumpCount < player.maxJumps) {
            player.vy = player.jumpPower; player.isGrounded = false; player.jumpCount++;
            if (player.jumpCount > 1) effects.push({ x: player.x, y: player.y + player.size, text: "💨", life: 15, vx: -2, vy: 1 });
        }
    }
    window.addEventListener("mousedown", jump);
    window.addEventListener("touchstart", (e) => { if (overlay.style.display !== "block") e.preventDefault(); jump(); }, {passive: false});

    function spawnEntities(phase, scrollSpeed) {
        if (isGameClear || isGameOver || boss) return; 

        let spawnInterval = Math.max(35, 100 - (phase * 8)); 

        if (frameCount % spawnInterval === 0) {
            let pool = [];
            switch(phase) {
                case 0: pool = [ {e: "🦠", t: "normal", h: 30}, {e: "🐌", t: "slow", h: 25} ]; break;
                case 1: pool = [ {e: "💉", t: "normal", h: 30}, {e: "🦇", t: "wave", h: 100} ]; break;
                case 2: pool = [ {e: "👻", t: "chase", h: 100}, {e: "🦇", t: "wave", h: 80} ]; break;
                case 3: pool = [ {e: "🚑", t: "fast", h: 40}, {e: "🧟‍♂️", t: "normal", h: 40} ]; break;
                case 4: pool = [ {e: "💀", t: "waveAir", h: 120}, {e: "🦅", t: "fastAir", h: 150} ]; break;
                case 5: pool = [ {e: "☣️", t: "normal", h: 30}, {e: "🦠", t: "chase", h: 80} ]; break;
                case 6: pool = [ {e: "🛒", t: "fast", h: 40}, {e: "🐍", t: "normal", h: 30} ]; break;
                case 7: pool = [ {e: "🌪️", t: "fastAir", h: 120}, {e: "👻", t: "chase", h: 90} ]; break;
                case 8: pool = [ {e: "🧟‍♂️", t: "fast", h: 40}, {e: "🚑", t: "fast", h: 40}, {e: "💀", t: "waveAir", h: 100} ]; break;
                default: pool = [ {e: "🧟‍♂️", t: "fast", h: 40}, {e: "👻", t: "chase", h: 120}, {e: "🦅", t: "fastAir", h: 160} ]; break;
            }

            let pick = pool[Math.floor(Math.random() * pool.length)];
            obstacles.push({ x: 800, y: groundY - pick.h, size: 30, emoji: pick.e, type: pick.t, baseY: groundY - pick.h, tick: 0 });
        }
        
        if (frameCount % 350 === 0) questionBlocks.push({ x: 800, y: groundY - 140, size: 40, emoji: "❓" });
        if (frameCount % 45 === 0 && Math.random() < 0.7) coins.push({ x: 800, y: groundY - 40 - Math.random() * 100, size: 25, emoji: "🪙" });
        if (frameCount % 180 === 0 && Math.random() < 0.7) gems.push({ x: 800, y: groundY - 200 - Math.random() * 60, size: 28, emoji: "💎" });
        
        if (frameCount % 450 === 0 && Math.random() < 0.5) {
            hearts.push({ x: 800, y: groundY - 50 - Math.random() * 100, size: 28, emoji: "💖" });
        }

        if (player.isGrounded && frameCount % 8 === 0) effects.push({ x: player.x, y: groundY - 10, text: "💨", life: 15, vx: -3, vy: -0.2 });
    }

    function triggerQuiz() {
        isPaused = true;
        let cq = nurseQuizzes[Math.floor(Math.random() * nurseQuizzes.length)];
        let shuffled = [...cq.options].sort(() => 0.5 - Math.random());
        let html = `<div class="quiz-title">🚨 ナース・アセスメント</div><div class="quiz-text">${cq.q}</div>`;
        shuffled.forEach(opt => { html += `<button class="quiz-btn" onclick="checkAnswer('${opt}', '${cq.ans}')">${opt}</button>`; });
        quizBox.innerHTML = html; overlay.style.display = "block";
    }

    window.checkAnswer = function(selected, correct) {
        overlay.style.display = "none"; isPaused = false; 
        if (selected === correct) {
            player.invincible = 300; player.isHurt = 0; score += 1000;
            player.lives = Math.min(player.maxLives, player.lives + 1); 
            effects.push({ x: player.x, y: player.y, text: "✨", life: 60 });
            gameMessage = { text: "🎉 大正解！", subtext: "ライフ回復 ＆ 5秒無敵 ＆ 4段ジャンプ解放！", life: 120, color: "#f1c40f" };
        } else {
            gameMessage = { text: "💦 惜しい！", subtext: "正解は：「" + correct + "」でした", life: 150, color: "#e74c3c" };
        }
    };

    function triggerGameOver() {
        isGameOver = true;
        isPaused = true;
        let title = ""; let comment = "";
        
        if (score < 3000) { title = "🐥 ひよっこナース"; comment = "まずは業務に慣れるところから！日々の積み重ねが大事です。"; }
        else if (score < 8000) { title = "💉 中堅ナース"; comment = "落ち着いてアセスメントできています！頼りになる存在です。"; }
        else if (score < 15000) { title = "🌟 ベテランナース"; comment = "素晴らしい反射神経と判断力！病棟のリーダークラスです！"; }
        else { title = "👑 ゴッドハンド・ナース"; comment = "神がかったアセスメント！もはや院内感染ボスの天敵です！"; }

        let html = `<div class="quiz-title" style="color:#c0392b;">💀 勤務終了（ゲームオーバー）</div>
                    <div class="quiz-text" style="text-align:center;">
                        最終スコア：<span style="font-size:24px; color:#e74c3c;">${score}</span> 点<br><br>
                        <b>獲得称号：【${title}】</b><br><br>
                        <span style="font-size:14px; color:#555;">${comment}</span>
                    </div>
                    <button class="quiz-btn game-over-btn" onclick="location.reload()">もう一度シフトに入る</button>`;
        quizBox.innerHTML = html;
        overlay.style.display = "block";
    }

    function takeDamage() {
        if (player.invincible > 0 || player.isHurt > 0) return;
        player.lives--; 
        player.invincible = 60; player.isHurt = 60;
        effects.push({ x: player.x, y: player.y, text: "💔", life: 45 });
        if (player.lives <= 0) triggerGameOver();
    }

    function update() {
        if (isPaused) return;
        if (!isGameClear && !isGameOver) { frameCount++; score++; }

        let currentPhase = Math.floor(frameCount / 1800); 
        let currentConfig = phaseConfigs[Math.min(currentPhase, phaseConfigs.length - 1)];

        if (frameCount > 0 && frameCount % 1800 === 0 && !boss && !isGameClear && !isGameOver) {
            gameMessage = { text: currentConfig.name, subtext: "敵のパターンが変化した！", life: 150, color: currentConfig.sky };
        }

        let currentScrollSpeed = (isGameClear || isGameOver) ? 0 : baseScrollSpeed + (currentPhase * 0.25);

        bgScrollCloud = (bgScrollCloud + 0.3) % 700;
        bgScrollMountain = (bgScrollMountain + 0.8) % 700;
        bgScrollCity = (bgScrollCity + 2.0) % 700;

        if (player.invincible > 0) { player.invincible--; player.maxJumps = 4; } else { player.maxJumps = 2; }
        if (player.isHurt > 0) player.isHurt--; 
        if (gameMessage.life > 0) gameMessage.life--; 

        if (frameCount === BOSS_SPAWN_FRAME - 180) {
            gameMessage = { text: "⚠️ 警告 ⚠️", subtext: "巨大な院内感染ボスが接近中！", life: 180, color: "#e74c3c" };
        } else if (frameCount === BOSS_SPAWN_FRAME && !boss && !isGameClear && !isGameOver) {
            boss = { x: 800, y: groundY - 90, size: 90, emoji: "👹", hp: 4, maxHp: 4, speed: 3.5 };
        }

        player.vy += player.gravity; player.y += player.vy;
        if (player.y + player.size >= groundY) {
            player.y = groundY - player.size; player.vy = 0; player.isGrounded = true; player.jumpCount = 0; 
        }

        spawnEntities(currentPhase, currentScrollSpeed);

        if (boss && !isGameClear && !isGameOver) {
            boss.x -= boss.speed; 
            if (boss.x < -150) {
                boss.x = 800; 
                let rageBonus = (4 - boss.hp) * 1.5;
                boss.speed = 2.5 + rageBonus + (Math.random() * 4.0); 
            }

            let dist = Math.hypot((player.x + player.size/2) - (boss.x + boss.size/2), (player.y + player.size/2) - (boss.y + boss.size/2));
            if (dist < (player.size/2 + boss.size/2 - 15)) {
                if (player.invincible > 0 && player.isHurt === 0) {
                    bossHit(); 
                } else if (player.vy > 0 && (player.y + player.size/2) < (boss.y + boss.size/2 - 10)) {
                    player.vy = player.jumpPower * 1.3; player.jumpCount = 1; bossHit();
                } else {
                    takeDamage(); 
                }
            }
        }

        function bossHit() {
            boss.hp--;
            if (boss.hp <= 0) {
                score += 5000; effects.push({ x: boss.x, y: boss.y, text: "💥撃破!!💥", life: 100 });
                boss = null; isGameClear = true;
                gameMessage = { text: "🎊 完 全 治 癒 🎊", subtext: "5分間防衛成功！見事なアセスメントです！", life: 9999, color: "#f1c40f" };
            } else {
                score += 1000; effects.push({ x: boss.x, y: boss.y, text: "💢", life: 30 });
                player.vy = player.jumpPower * 1.2; 
            }
        }

        for (let i = obstacles.length - 1; i >= 0; i--) {
            let obs = obstacles[i];
            
            if (obs.type === 'slow') { obs.x -= currentScrollSpeed * 0.6; } 
            else if (obs.type === 'fast' || obs.type === 'fastAir') { obs.x -= currentScrollSpeed * 1.6; } 
            else if (obs.type === 'wave' || obs.type === 'waveAir') {
                obs.tick += 0.08; obs.y = obs.baseY + Math.sin(obs.tick) * 50; obs.x -= currentScrollSpeed;
            } else if (obs.type === 'chase') {
                obs.y += (player.y - obs.y) * 0.02; obs.x -= currentScrollSpeed * 0.8;
            } else { obs.x -= currentScrollSpeed; }
            
            let dist = Math.hypot((player.x + player.size/2) - (obs.x + obs.size/2), (player.y + player.size/2) - (obs.y + obs.size/2));
            if (dist < (player.size/2 + obs.size/2 - 5)) {
                if (player.invincible > 0 && player.isHurt === 0) {
                    obstacles.splice(i, 1); score += 100; effects.push({ x: obs.x, y: obs.y, text: "💥", life: 30 });
                } else if (player.invincible === 0) {
                    if (player.vy > 0 && (player.y + player.size/2) < (obs.y + obs.size/2)) {
                        obstacles.splice(i, 1); score += 200; player.vy = player.jumpPower * 0.8; player.jumpCount = 1; effects.push({ x: obs.x, y: obs.y, text: "👟ﾎﾟｲﾝ!", life: 30 });
                    } else {
                        takeDamage(); 
                        if(isGameOver) break; 
                    }
                }
                continue;
            }
            if (obs.x < -50) obstacles.splice(i, 1);
        }

        for (let i = coins.length - 1; i >= 0; i--) {
            let c = coins[i]; c.x -= currentScrollSpeed;
            let dist = Math.hypot((player.x + player.size/2) - (c.x + c.size/2), (player.y + player.size/2) - (c.y + c.size/2));
            if (dist < (player.size/2 + c.size/2)) { score += 50; effects.push({ x: c.x, y: c.y, text: "✨", life: 20 }); coins.splice(i, 1); continue; }
            if (c.x < -50) coins.splice(i, 1);
        }

        for (let i = gems.length - 1; i >= 0; i--) {
            let g = gems[i]; g.x -= currentScrollSpeed;
            let dist = Math.hypot((player.x + player.size/2) - (g.x + g.size/2), (player.y + player.size/2) - (g.y + g.size/2));
            if (dist < (player.size/2 + g.size/2)) { score += 300; effects.push({ x: g.x, y: g.y, text: "💎+300!", life: 30 }); gems.splice(i, 1); continue; }
            if (g.x < -50) gems.splice(i, 1);
        }
        
        for (let i = hearts.length - 1; i >= 0; i--) {
            let h = hearts[i]; h.x -= currentScrollSpeed;
            let dist = Math.hypot((player.x + player.size/2) - (h.x + h.size/2), (player.y + player.size/2) - (h.y + h.size/2));
            if (dist < (player.size/2 + h.size/2)) { 
                player.lives = Math.min(player.maxLives, player.lives + 1);
                effects.push({ x: h.x, y: h.y, text: "💖回復!", life: 30 }); 
                hearts.splice(i, 1); continue; 
            }
            if (h.x < -50) hearts.splice(i, 1);
        }

        for (let i = questionBlocks.length - 1; i >= 0; i--) {
            let qb = questionBlocks[i]; qb.x -= currentScrollSpeed;
            let dist = Math.hypot((player.x + player.size/2) - (qb.x + qb.size/2), (player.y + player.size/2) - (qb.y + qb.size/2));
            if (dist < (player.size/2 + qb.size/2)) { questionBlocks.splice(i, 1); triggerQuiz(); continue; }
            if (qb.x < -50) questionBlocks.splice(i, 1);
        }
        
        for (let i = effects.length - 1; i >= 0; i--) {
            effects[i].life--; effects[i].x += (effects[i].vx || 0); effects[i].y += (effects[i].vy || -1); 
            if (effects[i].life <= 0) effects.splice(i, 1);
        }
    }

    function drawBackground() {
        let currentPhase = Math.floor(frameCount / 1800);
        let conf = phaseConfigs[Math.min(currentPhase, phaseConfigs.length - 1)];

        ctx.fillStyle = conf.sky; ctx.fillRect(0, 0, canvas.width, groundY);
        ctx.fillStyle = "rgba(255, 255, 255, 0.4)";
        for (let i = 0; i < 2; i++) {
            let offsetX = (i * 700) - bgScrollCloud;
            ctx.beginPath(); ctx.arc(offsetX + 100, 80, 30, 0, Math.PI*2); ctx.arc(offsetX + 130, 70, 40, 0, Math.PI*2); ctx.arc(offsetX + 160, 80, 30, 0, Math.PI*2); ctx.fill();
            ctx.beginPath(); ctx.arc(offsetX + 450, 120, 20, 0, Math.PI*2); ctx.arc(offsetX + 470, 110, 25, 0, Math.PI*2); ctx.arc(offsetX + 490, 120, 20, 0, Math.PI*2); ctx.fill();
        }
        ctx.fillStyle = conf.mtn;
        for (let i = 0; i < 2; i++) {
            let offsetX = (i * 700) - bgScrollMountain;
            ctx.beginPath(); ctx.moveTo(offsetX - 100, groundY); ctx.lineTo(offsetX + 150, groundY - 180); ctx.lineTo(offsetX + 400, groundY); ctx.fill();
            ctx.beginPath(); ctx.moveTo(offsetX + 200, groundY); ctx.lineTo(offsetX + 450, groundY - 230); ctx.lineTo(offsetX + 700, groundY); ctx.fill();
            ctx.beginPath(); ctx.moveTo(offsetX + 450, groundY); ctx.lineTo(offsetX + 650, groundY - 160); ctx.lineTo(offsetX + 850, groundY); ctx.fill();
        }
        ctx.fillStyle = conf.city; 
        for (let i = 0; i < 2; i++) {
            let offsetX = (i * 700) - bgScrollCity;
            ctx.fillRect(offsetX + 30, groundY - 60, 50, 60); ctx.fillRect(offsetX + 100, groundY - 90, 40, 90); ctx.fillRect(offsetX + 160, groundY - 50, 60, 50);
            ctx.fillRect(offsetX + 260, groundY - 100, 80, 100); ctx.beginPath(); ctx.moveTo(offsetX + 240, groundY - 100); ctx.lineTo(offsetX + 300, groundY - 140); ctx.lineTo(offsetX + 360, groundY - 100); ctx.fill(); 
            ctx.fillStyle = (currentPhase % 2 === 0) ? "#dfe6e9" : "#636e72"; ctx.fillRect(offsetX + 270, groundY - 90, 60, 40); 
            ctx.fillStyle = conf.city; ctx.fillRect(offsetX + 285, groundY - 80, 12, 15); ctx.fillRect(offsetX + 305, groundY - 80, 12, 15); 
            ctx.fillRect(offsetX + 380, groundY - 70, 50, 70); ctx.fillRect(offsetX + 450, groundY - 110, 60, 110); ctx.fillRect(offsetX + 530, groundY - 40, 80, 40); ctx.fillRect(offsetX + 630, groundY - 80, 50, 80);
        }
        ctx.fillStyle = conf.gnd; ctx.fillRect(0, groundY, canvas.width, canvas.height - groundY);
        ctx.fillStyle = conf.grass; ctx.fillRect(0, groundY, canvas.width, 10);
    }

    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        drawBackground();

        if (boss && !isGameOver) {
            ctx.font = "90px Arial"; ctx.textAlign = "center"; ctx.textBaseline = "middle";
            ctx.fillText(boss.emoji, boss.x + boss.size/2, boss.y + boss.size/2);
            ctx.fillStyle = "#e74c3c"; ctx.fillRect(boss.x, boss.y - 15, boss.size, 8);
            ctx.fillStyle = "#2ecc71"; ctx.fillRect(boss.x, boss.y - 15, boss.size * (boss.hp / boss.maxHp), 8);
        }

        ctx.font = "30px Arial"; ctx.textAlign = "center"; ctx.textBaseline = "middle";
        obstacles.forEach(obs => ctx.fillText(obs.emoji, obs.x + obs.size/2, obs.y + obs.size/2));
        questionBlocks.forEach(qb => ctx.fillText(qb.emoji, qb.x + qb.size/2, qb.y + qb.size/2));
        
        ctx.font = "25px Arial";
        coins.forEach(c => ctx.fillText(c.emoji, c.x + c.size/2, c.y + c.size/2));
        
        ctx.font = "28px Arial";
        gems.forEach(g => ctx.fillText(g.emoji, g.x + g.size/2, g.y + g.size/2));
        hearts.forEach(h => ctx.fillText(h.emoji, h.x + h.size/2, h.y + h.size/2));

        ctx.fillStyle = "#e74c3c"; ctx.font = "bold 20px Arial";
        effects.forEach(eff => ctx.fillText(eff.text, eff.x + 20, eff.y));

        if (!isGameOver && (player.invincible <= 0 || player.isHurt === 0 || Math.floor(frameCount / 5) % 2 === 0)) {
            ctx.save();
            ctx.translate(player.x + player.size/2, player.y + player.size/2);
            if (player.isGrounded) { ctx.rotate(Math.sin(frameCount * 0.4) * 0.1); } else { ctx.rotate(0.15); }

            ctx.fillStyle = "#ffffff"; ctx.fillRect(-12, -26, 24, 10);
            ctx.fillStyle = "#e74c3c"; ctx.fillRect(-2, -24, 4, 6); ctx.fillRect(-3, -23, 6, 4);
            ctx.fillStyle = "#ffdbac"; ctx.beginPath(); ctx.arc(0, -8, 12, 0, Math.PI*2); ctx.fill();

            if (player.isHurt > 0) {
                ctx.strokeStyle = "#2c3e50"; ctx.lineWidth = 1.5;
                ctx.beginPath(); ctx.moveTo(-7, -13); ctx.lineTo(-3, -11); ctx.stroke(); ctx.beginPath(); ctx.moveTo(7, -13); ctx.lineTo(3, -11); ctx.stroke();
                ctx.beginPath(); ctx.moveTo(-6, -10.5); ctx.lineTo(-4, -9); ctx.lineTo(-6, -7.5); ctx.stroke(); ctx.beginPath(); ctx.moveTo(6, -10.5); ctx.lineTo(4, -9); ctx.lineTo(6, -7.5); ctx.stroke();
                ctx.beginPath(); ctx.arc(0, -4, 3, 0, Math.PI, true); ctx.stroke();
            } else if (player.invincible > 0) {
                ctx.strokeStyle = "#2c3e50"; ctx.lineWidth = 1.5;
                ctx.beginPath(); ctx.moveTo(-6, -10); ctx.lineTo(-4, -12); ctx.lineTo(-2, -10); ctx.stroke(); ctx.beginPath(); ctx.moveTo(2, -10); ctx.lineTo(4, -12); ctx.lineTo(6, -10); ctx.stroke();
                ctx.fillStyle = "#ff9999"; ctx.beginPath(); ctx.arc(-7, -6, 2.5, 0, Math.PI*2); ctx.fill(); ctx.beginPath(); ctx.arc(7, -6, 2.5, 0, Math.PI*2); ctx.fill();
                ctx.beginPath(); ctx.arc(0, -6, 4, 0, Math.PI, false); ctx.stroke();
            } else if (!player.isGrounded) {
                ctx.fillStyle = "#2c3e50"; ctx.fillRect(-5, -12, 2, 4); ctx.fillRect(3, -12, 2, 4); 
                ctx.fillStyle = "#e74c3c"; ctx.beginPath(); ctx.arc(0, -5, 3, 0, Math.PI*2); ctx.fill(); 
            } else {
                ctx.fillStyle = "#2c3e50"; ctx.fillRect(-5, -11, 2, 3); ctx.fillRect(3, -11, 2, 3); 
                ctx.strokeStyle = "#2c3e50"; ctx.lineWidth = 1; ctx.beginPath(); ctx.arc(0, -6, 3, 0, Math.PI, false); ctx.stroke();
            }

            ctx.fillStyle = "#ffffff"; ctx.fillRect(-10, 4, 20, 16);
            ctx.fillStyle = "#ffdbac";
            if (player.isGrounded) {
                let armSwing = Math.sin(frameCount * 0.4) * 5; ctx.fillRect(-14, 6, 4, 10 + armSwing); ctx.fillRect(10, 6, 4, 10 - armSwing);  
                if (Math.floor(frameCount / 5) % 2 === 0) { ctx.fillRect(-6, 20, 5, 10); ctx.fillRect(4, 20, 5, 4); } else { ctx.fillRect(-6, 20, 5, 4); ctx.fillRect(4, 20, 5, 10); }
            } else {
                ctx.fillRect(-14, -2, 4, 12); ctx.fillRect(10, -2, 4, 12);
                ctx.fillRect(-8, 20, 6, 6); ctx.fillRect(2, 20, 6, 8); 
            }
            if (player.invincible > 0 && player.isHurt === 0) { ctx.strokeStyle = "#f1c40f"; ctx.lineWidth = 4; ctx.beginPath(); ctx.arc(0, 0, 32, 0, Math.PI*2); ctx.stroke(); }
            ctx.restore(); 
        }

        ctx.fillStyle = "#333"; ctx.textAlign = "left"; ctx.textBaseline = "alphabetic";
        ctx.font = "bold 24px Arial";
        ctx.strokeStyle = "#fff"; ctx.lineWidth = 3; ctx.strokeText("SCORE: " + score, 20, 40);
        ctx.fillText("SCORE: " + score, 20, 40);
        
        let heartStr = "";
        for(let i=0; i<player.maxLives; i++) {
            heartStr += (i < player.lives) ? "❤️" : "🤍";
        }
        ctx.strokeText("LIVES: " + heartStr, 20, 75);
        ctx.fillText("LIVES: " + heartStr, 20, 75);

        ctx.font = "bold 16px Arial";
        let jumpText = (player.invincible > 0 && player.isHurt === 0) ? "⚡ 4段ジャンプ解禁中！" : "2段ジャンプまで";
        ctx.strokeText(jumpText, 20, canvas.height - 20);
        ctx.fillStyle = (player.invincible > 0 && player.isHurt === 0) ? "#f1c40f" : "#333";
        ctx.fillText(jumpText, 20, canvas.height - 20);
        
        let seconds = Math.floor(frameCount / 60);
        ctx.fillStyle = "#fff"; ctx.textAlign = "right";
        ctx.strokeStyle = "#333"; ctx.lineWidth = 3;
        let timeStr = "TIME: " + Math.floor(seconds / 60) + ":" + (seconds % 60).toString().padStart(2, "0");
        ctx.strokeText(timeStr, canvas.width - 20, 30);
        ctx.fillText(timeStr, canvas.width - 20, 30);

        if (gameMessage.life > 0 && !isGameOver) {
            ctx.fillStyle = "rgba(0, 0, 0, 0.6)"; ctx.fillRect(0, canvas.height / 2 - 60, canvas.width, 120);
            ctx.textAlign = "center"; ctx.textBaseline = "middle";
            ctx.font = "bold 46px Arial"; ctx.fillStyle = gameMessage.color; ctx.fillText(gameMessage.text, canvas.width / 2, canvas.height / 2 - 15);
            ctx.font = "bold 18px Arial"; ctx.fillStyle = "#FFF"; ctx.fillText(gameMessage.subtext, canvas.width / 2, canvas.height / 2 + 25);
        }
    }

    function loop() { update(); draw(); requestAnimationFrame(loop); }
    window.onload = loop;
</script>
</body>
</html>
"""
components.html(html_code, height=500)