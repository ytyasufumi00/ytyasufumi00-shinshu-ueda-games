import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="ヴァンサバ風・酸塩基アクション", page_icon="🥷", layout="wide")

st.title("🥷 ヴァンサバ風・酸塩基サバイバル")
st.write("迫り来る「尿毒素スライム（赤）」を避けながら、倒した敵が落とす「経験値（青）」を集めよう！")
st.write("レベルアップ時にクイズが発生。正解すると手裏剣の連射速度がアップします！")

html_code = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
    body { margin: 0; display: flex; justify-content: center; background: #fff; font-family: 'Helvetica Neue', Arial, sans-serif; }
    
    #game-wrapper { 
        position: relative; 
        width: 100%; 
        max-width: 700px;
        aspect-ratio: 7 / 5;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2); 
        border-radius: 8px; 
        overflow: hidden; 
        /* スマホの長押しでメニューが出るのを防ぐ */
        -webkit-touch-callout: none;
        user-select: none;
    }
    canvas { width: 100%; height: 100%; background-color: #2c3e50; display: block; }
    
    /* 🌟 バーチャルジョイスティックのデザイン（外側の円と内側のグリグリ） */
    #joystick-zone {
        position: absolute;
        bottom: 20px;
        left: 20px;
        width: 120px;
        height: 120px;
        background: rgba(255, 255, 255, 0.15);
        border: 2px solid rgba(255, 255, 255, 0.4);
        border-radius: 50%;
        z-index: 5;
        touch-action: none; /* ブラウザのスクロールを完全に無効化 */
    }
    #joystick-knob {
        position: absolute;
        top: 50%;
        left: 50%;
        width: 50px;
        height: 50px;
        background: rgba(255, 255, 255, 0.8);
        border-radius: 50%;
        transform: translate(-50%, -50%);
        box-shadow: 0 2px 5px rgba(0,0,0,0.3);
        pointer-events: none; /* タッチ判定は外側のzoneに任せる */
    }

    #quiz-overlay {
        display: none; 
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0, 0, 0, 0.7); z-index: 10;
    }
    #quiz-box {
        position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
        background: #fdfdfd; padding: 20px; border-radius: 12px;
        text-align: center; width: 85%; border: 4px solid #f1c40f; box-sizing: border-box;
    }
    .quiz-title { color: #e74c3c; font-size: 20px; margin-top: 0; }
    .quiz-question { font-size: 16px; font-weight: bold; margin-bottom: 15px; color: #333; }
    .quiz-btn {
        display: block; width: 100%; margin: 8px 0; padding: 12px;
        background: #3498db; color: white; border: none; border-radius: 8px;
        font-size: 14px; cursor: pointer;
    }
</style>
</head>
<body>

<div id="game-wrapper">
    <canvas id="gameCanvas" width="700" height="500"></canvas>
    
    <div id="joystick-zone">
        <div id="joystick-knob"></div>
    </div>

    <div id="quiz-overlay">
        <div id="quiz-box">
            <h2 class="quiz-title">🆙 レベルアップの試練！</h2>
            <div id="quiz-text" class="quiz-question"></div>
            <div id="quiz-buttons"></div>
        </div>
    </div>
</div>

<script>
    const canvas = document.getElementById("gameCanvas");
    const ctx = canvas.getContext("2d");
    const overlay = document.getElementById("quiz-overlay");
    const quizText = document.getElementById("quiz-text");
    const quizBtns = document.getElementById("quiz-buttons");

    window.onerror = function(msg, url, line) {
        ctx.fillStyle = "red"; ctx.font = "18px Arial";
        ctx.fillText("エラー: " + msg, 20, 50); ctx.fillText("行: " + line, 20, 80);
    };

    let isPaused = false;
    let frameCount = 0;
    let keys = {};

    // 🌟 ジョイスティックの計算ロジック
    const joyZone = document.getElementById("joystick-zone");
    const joyKnob = document.getElementById("joystick-knob");
    let isDragging = false;
    let joyCenter = { x: 0, y: 0 };
    const maxRadius = 40; // グリグリが動ける最大の半径
    
    // スティックの傾き（-1.0 ～ 1.0）を保存する変数
    let joyVector = { x: 0, y: 0 };

    function startJoy(e) {
        e.preventDefault();
        isDragging = true;
        const rect = joyZone.getBoundingClientRect();
        joyCenter = { x: rect.left + rect.width / 2, y: rect.top + rect.height / 2 };
        moveJoy(e);
    }

    function moveJoy(e) {
        if (!isDragging) return;
        e.preventDefault();
        
        // タッチとマウスの両方に対応
        let clientX = e.touches ? e.touches[0].clientX : e.clientX;
        let clientY = e.touches ? e.touches[0].clientY : e.clientY;

        // 中心からの距離を計算
        let dx = clientX - joyCenter.x;
        let dy = clientY - joyCenter.y;
        let distance = Math.hypot(dx, dy);

        // 外枠を越えないように制限
        if (distance > maxRadius) {
            dx = (dx / distance) * maxRadius;
            dy = (dy / distance) * maxRadius;
        }

        // グリグリを動かす（見た目の更新）
        joyKnob.style.transform = `translate(calc(-50% + ${dx}px), calc(-50% + ${dy}px))`;

        // ゲーム用のベクトルに変換（-1.0 ～ 1.0）
        joyVector.x = dx / maxRadius;
        joyVector.y = dy / maxRadius;
    }

    function endJoy(e) {
        e.preventDefault();
        isDragging = false;
        // 手を離したら真ん中に戻す
        joyKnob.style.transform = `translate(-50%, -50%)`;
        joyVector.x = 0;
        joyVector.y = 0;
    }

    // イベントリスナーを登録
    joyZone.addEventListener("touchstart", startJoy, {passive: false});
    joyZone.addEventListener("touchmove", moveJoy, {passive: false});
    joyZone.addEventListener("touchend", endJoy, {passive: false});
    joyZone.addEventListener("mousedown", startJoy);
    window.addEventListener("mousemove", moveJoy);
    window.addEventListener("mouseup", endJoy);


    // PC用のキーボード操作（そのまま残します）
    window.addEventListener("keydown", e => { 
        keys[e.key] = true; 
        if(["ArrowUp","ArrowDown","ArrowLeft","ArrowRight"].includes(e.key)) e.preventDefault(); 
    });
    window.addEventListener("keyup", e => keys[e.key] = false);

    let player = { x: 350, y: 250, size: 24, speed: 3.5, level: 1, exp: 0, nextExp: 3, fireRate: 60, fireTimer: 0, bulletSpeed: 8 };
    let enemies = []; let bullets = []; let gems = [];

    const questions = [
        { q: "pH 7.25<br>PaCO2 60<br>HCO3- 26", options: ["呼吸性アシドーシス", "代謝性アシドーシス", "呼吸性アルカローシス"], ans: "呼吸性アシドーシス" },
        { q: "pH 7.50<br>PaCO2 40<br>HCO3- 32", options: ["代謝性アルカローシス", "呼吸性アルカローシス", "代謝性アシドーシス"], ans: "代謝性アルカローシス" },
        { q: "pH 7.20<br>PaCO2 40<br>HCO3- 15", options: ["代謝性アシドーシス", "呼吸性アシドーシス", "代謝性アルカローシス"], ans: "代謝性アシドーシス" },
        { q: "pH 7.55<br>PaCO2 25<br>HCO3- 22", options: ["呼吸性アルカローシス", "代謝性アルカローシス", "呼吸性アシドーシス"], ans: "呼吸性アルカローシス" }
    ];

    function spawnEnemy() {
        let ex, ey;
        if (Math.random() < 0.5) {
            ex = Math.random() < 0.5 ? -20 : canvas.width + 20;
            ey = Math.random() * canvas.height;
        } else {
            ex = Math.random() * canvas.width;
            ey = Math.random() < 0.5 ? -20 : canvas.height + 20;
        }
        enemies.push({ x: ex, y: ey, size: 16, speed: 1 + Math.random() * 0.5 + (player.level * 0.1), hp: 1 });
    }

    function triggerQuiz() {
        isPaused = true;
        let qData = questions[Math.floor(Math.random() * questions.length)];
        quizText.innerHTML = qData.q + "<br><br>最も疑われる異常は？";
        quizBtns.innerHTML = "";
        qData.options.forEach(opt => {
            let btn = document.createElement("button");
            btn.className = "quiz-btn"; btn.innerText = opt;
            btn.onclick = () => checkAnswer(opt, qData.ans);
            quizBtns.appendChild(btn);
        });
        overlay.style.display = "block";
        endJoy(new Event('touchend')); // クイズが出たらスティックを真ん中に戻す
    }

    function checkAnswer(selected, correct) {
        overlay.style.display = "none";
        if (selected === correct) {
            player.fireRate = Math.max(10, player.fireRate - 10);
            alert("正解！\\n手裏剣の連射速度がアップしました！");
        } else {
            alert("不正解...\\n次は頑張りましょう！");
        }
        isPaused = false;
        loop(); 
    }

    function update() {
        frameCount++;

        // 🌟 移動の計算（キーボードとジョイスティックを統合）
        let moveX = 0;
        let moveY = 0;

        if (keys["ArrowUp"]) moveY -= 1;
        if (keys["ArrowDown"]) moveY += 1;
        if (keys["ArrowLeft"]) moveX -= 1;
        if (keys["ArrowRight"]) moveX += 1;

        // キーボード入力が優先。なければジョイスティックの傾きを使用
        if (moveX !== 0 || moveY !== 0) {
            // 斜め移動が速くならないように正規化
            let dist = Math.hypot(moveX, moveY);
            moveX = moveX / dist;
            moveY = moveY / dist;
        } else {
            // ジョイスティックのアナログな傾き（少し倒せばゆっくり歩く）
            moveX = joyVector.x;
            moveY = joyVector.y;
        }

        player.x += moveX * player.speed;
        player.y += moveY * player.speed;
        
        player.x = Math.max(0, Math.min(canvas.width - player.size, player.x));
        player.y = Math.max(0, Math.min(canvas.height - player.size, player.y));

        let spawnRate = Math.max(10, 50 - player.level * 2);
        if (frameCount % spawnRate === 0) spawnEnemy();

        player.fireTimer++;
        if (player.fireTimer >= player.fireRate && enemies.length > 0) {
            player.fireTimer = 0;
            let nearest = enemies[0];
            let minDist = Math.hypot(nearest.x - player.x, nearest.y - player.y);
            for(let i = 1; i < enemies.length; i++) {
                let d = Math.hypot(enemies[i].x - player.x, enemies[i].y - player.y);
                if(d < minDist) { minDist = d; nearest = enemies[i]; }
            }
            let angle = Math.atan2(nearest.y - player.y, nearest.x - player.x);
            bullets.push({ 
                x: player.x + player.size/2, y: player.y + player.size/2, 
                vx: Math.cos(angle) * player.bulletSpeed, vy: Math.sin(angle) * player.bulletSpeed, size: 6 
            });
        }

        for (let i = bullets.length - 1; i >= 0; i--) {
            let b = bullets[i]; b.x += b.vx; b.y += b.vy;
            if (b.x < 0 || b.x > canvas.width || b.y < 0 || b.y > canvas.height) { bullets.splice(i, 1); continue; }
            for (let j = enemies.length - 1; j >= 0; j--) {
                let e = enemies[j];
                if (Math.hypot(b.x - e.x, b.y - e.y) < b.size + e.size) {
                    gems.push({ x: e.x, y: e.y, size: 8 });
                    enemies.splice(j, 1); bullets.splice(i, 1); break;
                }
            }
        }

        enemies.forEach(e => {
            let angle = Math.atan2(player.y - e.y, player.x - e.x);
            e.x += Math.cos(angle) * e.speed; e.y += Math.sin(angle) * e.speed;
        });

        for (let i = gems.length - 1; i >= 0; i--) {
            let g = gems[i];
            let dist = Math.hypot(player.x + player.size/2 - g.x, player.y + player.size/2 - g.y);
            if (dist < 80) { 
                let angle = Math.atan2(player.y + player.size/2 - g.y, player.x + player.size/2 - g.x);
                g.x += Math.cos(angle) * 6; g.y += Math.sin(angle) * 6;
                if (dist < player.size) { 
                    player.exp++; gems.splice(i, 1);
                    if (player.exp >= player.nextExp) {
                        player.level++; player.exp = 0; player.nextExp += Math.floor(player.level * 2); 
                        triggerQuiz(); 
                    }
                }
            }
        }
    }

    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        ctx.fillStyle = "#3498db";
        gems.forEach(g => { ctx.beginPath(); ctx.arc(g.x, g.y, g.size, 0, Math.PI*2); ctx.fill(); });
        
        ctx.fillStyle = "#e74c3c";
        enemies.forEach(e => ctx.fillRect(e.x, e.y, e.size, e.size));
        
        ctx.fillStyle = "#f1c40f";
        bullets.forEach(b => { ctx.beginPath(); ctx.arc(b.x, b.y, b.size, 0, Math.PI*2); ctx.fill(); });
        
        ctx.fillStyle = "white"; ctx.font = "28px Arial";
        ctx.fillText("🥷", player.x, player.y + 24);
        
        ctx.fillStyle = "white"; ctx.font = "bold 18px Arial";
        ctx.fillText("Lv: " + player.level, 15, 30);
        
        ctx.fillStyle = "#555"; ctx.fillRect(80, 15, 200, 15);
        ctx.fillStyle = "#2ecc71"; ctx.fillRect(80, 15, 200 * (player.exp / player.nextExp), 15);
    }

    function loop() { if (!isPaused) { update(); draw(); requestAnimationFrame(loop); } }
    window.onload = function() { loop(); };
</script>
</body>
</html>
"""

components.html(html_code, height=600)