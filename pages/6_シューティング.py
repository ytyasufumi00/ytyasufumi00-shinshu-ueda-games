import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="シューティング プロトタイプ", page_icon="🚀", layout="wide")

st.markdown(
    "<h1 style='font-size: 32px; margin-bottom: 0px;'>🚀 メディカル・ストライカー（プロトタイプ）</h1>", 
    unsafe_allow_html=True
)
st.markdown(
    "<p style='font-size: 18px; color: #555;'>指（マウス）でドラッグして自機を操作！オート連射でウイルスを撃破せよ！</p>", 
    unsafe_allow_html=True
)

html_code = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
    body { 
        margin: 0; background: #2c3e50; display: flex; flex-direction: column; align-items: center; 
        font-family: 'Helvetica Neue', Arial, sans-serif; overflow: hidden; 
        touch-action: none; /* スマホでのスワイプスクロールを防止 */
        user-select: none; -webkit-user-select: none;
    }
    
    #game-container { 
        position: relative; width: 100%; max-width: 500px; aspect-ratio: 3 / 4; 
        background: #000; border: 4px solid #34495e; border-radius: 8px; 
        overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.5); 
    }
    
    canvas { width: 100%; height: 100%; display: block; }
    
    #overlay { 
        display: none; position: absolute; top: 0; left: 0; width: 100%; height: 100%; 
        background: rgba(0,0,0,0.8); z-index: 30; flex-direction: column; 
        justify-content: center; align-items: center; text-align: center; color: white;
    }
    
    .restart-btn { 
        background: #e74c3c; color: white; border: none; border-radius: 8px; 
        padding: 15px 30px; font-size: 20px; font-weight: bold; cursor: pointer; 
        margin-top: 20px; box-shadow: 0 4px 10px rgba(231,76,60,0.4); transition: 0.2s;
    }
    .restart-btn:active { transform: scale(0.95); background: #c0392b; }
</style>
</head>
<body>
<div id="game-container">
    <canvas id="gameCanvas" width="500" height="666"></canvas>
    <div id="overlay">
        <div style="font-size: 40px; font-weight: 900; color: #e74c3c; margin-bottom: 10px;">GAME OVER</div>
        <div style="font-size: 20px;">最終スコア</div>
        <div id="final-score" style="font-size: 50px; font-weight: 900; color: #f1c40f;">0</div>
        <button class="restart-btn" onclick="location.reload()">再出撃</button>
    </div>
</div>

<script>
    const canvas = document.getElementById("gameCanvas");
    const ctx = canvas.getContext("2d");
    const overlay = document.getElementById("overlay");
    const finalScoreEl = document.getElementById("final-score");

    // 🌟 ゲームの基本状態
    let isGameOver = false;
    let score = 0;
    let frameCount = 0;

    // 🌟 背景の星（血流や細胞をイメージしたパーティクル）
    let stars = [];
    for(let i=0; i<50; i++) {
        stars.push({ x: Math.random() * canvas.width, y: Math.random() * canvas.height, speed: 1 + Math.random() * 3, size: Math.random() * 3 });
    }

    // 🌟 自機（プレイヤー）の設定
    // ※後日、このemoji部分を画像に差し替えます
    let player = { x: 250, y: 550, size: 40, emoji: "💉" };

    // 🌟 配列の初期化（弾、敵、爆発エフェクト）
    let bullets = [];
    let enemies = [];
    let effects = [];

    // 🌟 スマホ（タッチ）＆PC（マウス）の操作イベント
    function movePlayer(clientX, clientY) {
        if(isGameOver) return;
        const rect = canvas.getBoundingClientRect();
        // キャンバスの実際の表示サイズと内部座標（500x666）の比率を計算して座標を合わせる
        const scaleX = canvas.width / rect.width;
        const scaleY = canvas.height / rect.height;
        player.x = (clientX - rect.left) * scaleX;
        player.y = (clientY - rect.top) * scaleY;
        
        // 画面外に出ないように制限
        if(player.x < 20) player.x = 20;
        if(player.x > canvas.width - 20) player.x = canvas.width - 20;
        if(player.y < 20) player.y = 20;
        if(player.y > canvas.height - 20) player.y = canvas.height - 20;
    }

    canvas.addEventListener("touchmove", (e) => { e.preventDefault(); movePlayer(e.touches[0].clientX, e.touches[0].clientY); }, {passive: false});
    canvas.addEventListener("mousemove", (e) => { movePlayer(e.clientX, e.clientY); });

    // 🌟 当たり判定の計算関数（2点間の距離が半径の和より小さいか）
    function checkCollision(obj1, obj2, hitRadius) {
        let dx = obj1.x - obj2.x;
        let dy = obj1.y - obj2.y;
        let distance = Math.hypot(dx, dy);
        return distance < hitRadius;
    }

    // 🌟 メインの更新処理
    function update() {
        if (isGameOver) return;
        frameCount++;

        // 1. 背景のスクロール
        stars.forEach(s => {
            s.y += s.speed;
            if (s.y > canvas.height) { s.y = 0; s.x = Math.random() * canvas.width; }
        });

        // 2. 弾の自動発射（8フレームに1回）
        if (frameCount % 8 === 0) {
            // ダブルショット
            bullets.push({ x: player.x - 10, y: player.y - 20, size: 15, speed: 12, emoji: "💊" });
            bullets.push({ x: player.x + 10, y: player.y - 20, size: 15, speed: 12, emoji: "💊" });
        }

        // 3. 敵の出現（徐々に増える）
        let spawnRate = Math.max(15, 60 - Math.floor(score / 500)); // スコアが上がると出現間隔が短くなる
        if (frameCount % spawnRate === 0) {
            let type = Math.random();
            let enemyEmoji = type > 0.8 ? "👾" : "🦠";
            let enemyHp = type > 0.8 ? 3 : 1; // 👾は硬い
            enemies.push({ 
                x: Math.random() * (canvas.width - 40) + 20, 
                y: -30, 
                size: 35, 
                speed: 3 + Math.random() * 3 + (score / 3000), // スコアに応じて落下速度UP
                emoji: enemyEmoji,
                hp: enemyHp
            });
        }

        // 4. 弾の移動と画面外削除
        for (let i = bullets.length - 1; i >= 0; i--) {
            bullets[i].y -= bullets[i].speed;
            if (bullets[i].y < -20) bullets.splice(i, 1);
        }

        // 5. 敵の移動と当たり判定
        for (let i = enemies.length - 1; i >= 0; i--) {
            let enemy = enemies[i];
            enemy.y += enemy.speed;
            
            // 少し横揺れする動き（サイン波）
            enemy.x += Math.sin(frameCount * 0.05 + i) * 1.5;

            // 画面下へ逃した（ペナルティなし、ただ消える）
            if (enemy.y > canvas.height + 30) {
                enemies.splice(i, 1);
                continue;
            }

            // 【判定A】敵と弾の衝突
            for (let j = bullets.length - 1; j >= 0; j--) {
                let bullet = bullets[j];
                if (checkCollision(enemy, bullet, 25)) { // 25は当たり判定の広さ
                    bullets.splice(j, 1); // 弾を消す
                    enemy.hp--;
                    
                    // ダメージエフェクト
                    effects.push({ x: enemy.x, y: enemy.y, text: "💥", life: 10, vy: -1 });

                    if (enemy.hp <= 0) {
                        score += (enemy.emoji === "👾" ? 300 : 100);
                        effects.push({ x: enemy.x, y: enemy.y, text: "✨", life: 20, vy: -2 });
                        enemies.splice(i, 1); // 敵を消す
                        break; // 敵が死んだらこの敵への弾判定ループを抜ける
                    }
                }
            }

            // 【判定B】敵と自機（プレイヤー）の衝突（ゲームオーバー）
            if (enemies[i] && checkCollision(enemy, player, 20)) { // 自機の判定は少し小さめ(20)がプレイしやすい
                isGameOver = true;
                effects.push({ x: player.x, y: player.y, text: "🔥", life: 60, vy: 0 });
                finalScoreEl.innerText = score;
                overlay.style.display = "flex";
            }
        }

        // 6. エフェクトの更新
        for (let i = effects.length - 1; i >= 0; i--) {
            effects[i].y += effects[i].vy;
            effects[i].life--;
            if (effects[i].life <= 0) effects.splice(i, 1);
        }
    }

    // 🌟 描画処理
    function draw() {
        // 背景クリア
        ctx.fillStyle = "#000000";
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // 星（背景）の描画
        ctx.fillStyle = "#3498db";
        stars.forEach(s => {
            ctx.beginPath();
            ctx.arc(s.x, s.y, s.size, 0, Math.PI * 2);
            ctx.fill();
        });

        ctx.textAlign = "center";
        ctx.textBaseline = "middle";

        // 弾の描画
        ctx.font = "20px Arial";
        bullets.forEach(b => { ctx.fillText(b.emoji, b.x, b.y); });

        // 敵の描画
        ctx.font = "35px Arial";
        enemies.forEach(e => { ctx.fillText(e.emoji, e.x, e.y); });

        // 自機の描画（ゲームオーバーでなければ）
        if (!isGameOver) {
            ctx.font = "45px Arial";
            ctx.fillText(player.emoji, player.x, player.y);
        }

        // エフェクトの描画
        ctx.font = "30px Arial";
        effects.forEach(eff => {
            ctx.globalAlpha = eff.life / 20; // だんだん透明になる
            ctx.fillText(eff.text, eff.x, eff.y);
            ctx.globalAlpha = 1.0;
        });

        // スコア表示
        ctx.fillStyle = "#ffffff";
        ctx.textAlign = "left";
        ctx.font = "bold 24px Arial";
        ctx.fillText("SCORE: " + score, 15, 30);
    }

    // 🌟 ゲームループ
    function loop() {
        update();
        draw();
        requestAnimationFrame(loop);
    }

    // 開始
    loop();
</script>
</body>
</html>
"""
components.html(html_code, height=750)