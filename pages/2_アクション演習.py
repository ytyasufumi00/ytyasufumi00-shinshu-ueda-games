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
<style>
    body { margin: 0; overflow: hidden; display: flex; justify-content: center; font-family: 'Helvetica Neue', Arial, sans-serif; }
    #game-wrapper { position: relative; width: 700px; height: 500px; box-shadow: 0 4px 8px rgba(0,0,0,0.2); border-radius: 8px; overflow: hidden; }
    canvas { background-color: #2c3e50; display: block; }
    
    #quiz-overlay {
        display: none; 
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0, 0, 0, 0.7); z-index: 10;
    }
    #quiz-box {
        position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
        background: #fdfdfd; padding: 30px; border-radius: 12px;
        text-align: center; width: 80%; border: 4px solid #f1c40f;
    }
    .quiz-title { color: #e74c3c; font-size: 24px; margin-top: 0; }
    .quiz-question { font-size: 18px; font-weight: bold; margin-bottom: 20px; color: #333; }
    .quiz-btn {
        display: block; width: 100%; margin: 10px 0; padding: 15px;
        background: #3498db; color: white; border: none; border-radius: 8px;
        font-size: 16px; cursor: pointer; transition: 0.2s;
    }
    .quiz-btn:hover { background: #2980b9; transform: scale(1.02); }
</style>
</head>
<body>

<div id="game-wrapper">
    <canvas id="gameCanvas" width="700" height="500"></canvas>
    
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

    // 🌟 エラーが起きたら画面に赤文字で表示する最強の探知機
    window.onerror = function(msg, url, line) {
        ctx.fillStyle = "red";
        ctx.font = "18px Arial";
        ctx.fillText("⚠️ エラー発生: " + msg, 20, 50);
        ctx.fillText("行番号: " + line, 20, 80);
    };

    let isPaused = false;
    let frameCount = 0;

    let keys = {};
    window.addEventListener("keydown", e => { 
        keys[e.key] = true; 
        if(["ArrowUp","ArrowDown","ArrowLeft","ArrowRight"].includes(e.key)) e.preventDefault(); 
    });
    window.addEventListener("keyup", e => keys[e.key] = false);

    let player = { 
        x: 350, y: 250, size: 24, speed: 3.5, 
        level: 1, exp: 0, nextExp: 3, 
        fireRate: 60, fireTimer: 0, bulletSpeed: 8 
    };

    let enemies = [];
    let bullets = [];
    let gems = [];

    const questions = [
        { q: "pH 7.25<br>PaCO2 60 mmHg<br>HCO3- 26 mEq/L", options: ["呼吸性アシドーシス", "代謝性アシドーシス", "呼吸性アルカローシス"], ans: "呼吸性アシドーシス" },
        { q: "pH 7.50<br>PaCO2 40 mmHg<br>HCO3- 32 mEq/L", options: ["代謝性アルカローシス", "呼吸性アルカローシス", "代謝性アシドーシス"], ans: "代謝性アルカローシス" },
        { q: "pH 7.20<br>PaCO2 40 mmHg<br>HCO3- 15 mEq/L", options: ["代謝性アシドーシス", "呼吸性アシドーシス", "代謝性アルカローシス"], ans: "代謝性アシドーシス" },
        { q: "pH 7.55<br>PaCO2 25 mmHg<br>HCO3- 22 mEq/L", options: ["呼吸性アルカローシス", "代謝性アルカローシス", "呼吸性アシドーシス"], ans: "呼吸性アルカローシス" }
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
        let enemySpeed = 1 + Math.random() * 0.5 + (player.level * 0.1);
        enemies.push({ x: ex, y: ey, size: 16, speed: enemySpeed, hp: 1 });
    }

    function triggerQuiz() {
        isPaused = true;
        let qData = questions[Math.floor(Math.random() * questions.length)];
        
        quizText.innerHTML = qData.q + "<br><br>最も疑われる一次性の異常は？";
        quizBtns.innerHTML = "";
        
        qData.options.forEach(opt => {
            let btn = document.createElement("button");
            btn.className = "quiz-btn";
            btn.innerText = opt;
            btn.onclick = () => checkAnswer(opt, qData.ans);
            quizBtns.appendChild(btn);
        });
        
        overlay.style.display = "block";
    }

    function checkAnswer(selected, correct) {
        overlay.style.display = "none";
        
        if (selected === correct) {
            player.fireRate = Math.max(10, player.fireRate - 10);
            alert("正解！見事な診断です。\\n【レベルアップボーナス】手裏剣の連射速度がアップしました！");
        } else {
            alert("不正解...\\nボーナス獲得ならず。次は頑張りましょう！");
        }
        
        isPaused = false;
        loop(); 
    }

    function update() {
        frameCount++;

        if (keys["ArrowUp"]) player.y -= player.speed;
        if (keys["ArrowDown"]) player.y += player.speed;
        if (keys["ArrowLeft"]) player.x -= player.speed;
        if (keys["ArrowRight"]) player.x += player.speed;
        
        player.x = Math.max(0, Math.min(canvas.width - player.size, player.x));
        player.y = Math.max(0, Math.min(canvas.height - player.size, player.y));

        let spawnRate = Math.max(10, 50 - player.level * 2);
        if (frameCount % spawnRate === 0) spawnEnemy();

        player.fireTimer++;
        if (player.fireTimer >= player.fireRate && enemies.length > 0) {
            player.fireTimer = 0;
            
            // 🌟 最も近い敵を探すロジック（より安全で頑丈な計算式に変更）
            let nearest = enemies[0];
            let minDist = Math.hypot(nearest.x - player.x, nearest.y - player.y);
            for(let i = 1; i < enemies.length; i++) {
                let d = Math.hypot(enemies[i].x - player.x, enemies[i].y - player.y);
                if(d < minDist) {
                    minDist = d;
                    nearest = enemies[i];
                }
            }
            
            let angle = Math.atan2(nearest.y - player.y, nearest.x - player.x);
            bullets.push({ 
                x: player.x + player.size/2, y: player.y + player.size/2, 
                vx: Math.cos(angle) * player.bulletSpeed, vy: Math.sin(angle) * player.bulletSpeed, 
                size: 6 
            });
        }

        for (let i = bullets.length - 1; i >= 0; i--) {
            let b = bullets[i];
            b.x += b.vx; b.y += b.vy;
            
            if (b.x < 0 || b.x > canvas.width || b.y < 0 || b.y > canvas.height) { 
                bullets.splice(i, 1); continue; 
            }
            
            for (let j = enemies.length - 1; j >= 0; j--) {
                let e = enemies[j];
                if (Math.hypot(b.x - e.x, b.y - e.y) < b.size + e.size) {
                    gems.push({ x: e.x, y: e.y, size: 8 });
                    enemies.splice(j, 1);
                    bullets.splice(i, 1);
                    break;
                }
            }
        }

        enemies.forEach(e => {
            let angle = Math.atan2(player.y - e.y, player.x - e.x);
            e.x += Math.cos(angle) * e.speed;
            e.y += Math.sin(angle) * e.speed;
        });

        for (let i = gems.length - 1; i >= 0; i--) {
            let g = gems[i];
            let dist = Math.hypot(player.x + player.size/2 - g.x, player.y + player.size/2 - g.y);
            
            if (dist < 80) { 
                let angle = Math.atan2(player.y + player.size/2 - g.y, player.x + player.size/2 - g.x);
                g.x += Math.cos(angle) * 6;
                g.y += Math.sin(angle) * 6;
                
                if (dist < player.size) { 
                    player.exp++;
                    gems.splice(i, 1);
                    
                    if (player.exp >= player.nextExp) {
                        player.level++;
                        player.exp = 0;
                        player.nextExp += Math.floor(player.level * 2); 
                        triggerQuiz(); 
                    }
                }
            }
        }
    }

    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        ctx.fillStyle = "#3498db";
        gems.forEach(g => { 
            ctx.beginPath(); ctx.arc(g.x, g.y, g.size, 0, Math.PI*2); ctx.fill(); 
        });
        
        ctx.fillStyle = "#e74c3c";
        enemies.forEach(e => ctx.fillRect(e.x, e.y, e.size, e.size));
        
        ctx.fillStyle = "#f1c40f";
        bullets.forEach(b => { 
            ctx.beginPath(); ctx.arc(b.x, b.y, b.size, 0, Math.PI*2); ctx.fill(); 
        });
        
        ctx.fillStyle = "white";
        ctx.font = "28px Arial";
        ctx.fillText("🥷", player.x, player.y + 24);
        
        ctx.fillStyle = "white";
        ctx.font = "bold 18px Arial";
        ctx.fillText("Lv: " + player.level, 15, 30);
        
        ctx.fillStyle = "#555";
        ctx.fillRect(80, 15, 200, 15);
        ctx.fillStyle = "#2ecc71";
        ctx.fillRect(80, 15, 200 * (player.exp / player.nextExp), 15);
    }

    function loop() {
        if (!isPaused) {
            update();
            draw();
            requestAnimationFrame(loop);
        }
    }
    
    // 全ての準備が整ってからゲームをスタートする
    window.onload = function() {
        loop();
    };
</script>

</body>
</html>
"""

components.html(html_code, height=550)