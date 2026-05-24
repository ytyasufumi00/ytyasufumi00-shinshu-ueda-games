import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="アクション演習", page_icon="🥷")

st.title("🥷 アクション演習場（JS導入テスト）")
st.write("Streamlitの中に「HTML/JavaScript」の窓を作り、その中でゲームを動かしています。")
st.write("キーボードの「矢印キー（↑↓←→）」を押して、忍者を動かしてみてください！")

# 👇 ここから下が「JavaScript」と「HTML」の世界です！
html_code = """
<!DOCTYPE html>
<html>
<head>
<style>
    /* ゲーム画面（キャンバス）のデザイン */
    canvas { 
        border: 4px solid #4a5d23; 
        background-color: #f0f7e6; 
        border-radius: 10px;
    }
    body { 
        display: flex; 
        justify-content: center; 
        margin: 0; 
        overflow: hidden; /* 画面スクロールを防ぐ */
    }
</style>
</head>
<body>
    <canvas id="gameCanvas" width="400" height="400"></canvas>

    <script>
        // 画用紙とペンの準備
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");

        // 忍者の初期データ（X座標、Y座標、サイズ、スピード）
        let ninja = { x: 180, y: 180, size: 40, speed: 5 };
        
        // どのキーが押されているかを記憶する箱
        let keys = {};

        // キーボードが押された時の処理
        window.addEventListener("keydown", function(e) {
            keys[e.key] = true;
            // 矢印キーで画面全体がスクロールしてしまうのを防ぐ
            if(["ArrowUp","ArrowDown","ArrowLeft","ArrowRight"].indexOf(e.key) > -1) {
                e.preventDefault();
            }
        });

        // キーボードが離された時の処理
        window.addEventListener("keyup", function(e) {
            keys[e.key] = false;
        });

        // 忍者の位置を計算する関数（毎秒60回呼ばれる）
        function update() {
            if (keys["ArrowUp"]) ninja.y -= ninja.speed;
            if (keys["ArrowDown"]) ninja.y += ninja.speed;
            if (keys["ArrowLeft"]) ninja.x -= ninja.speed;
            if (keys["ArrowRight"]) ninja.x += ninja.speed;

            // 画面の外に出ないようにする壁の判定
            if (ninja.x < 0) ninja.x = 0;
            if (ninja.x > canvas.width - ninja.size) ninja.x = canvas.width - ninja.size;
            if (ninja.y < 0) ninja.y = 0;
            if (ninja.y > canvas.height - ninja.size) ninja.y = canvas.height - ninja.size;
        }

        // 画面に絵を描く関数（毎秒60回呼ばれる）
        function draw() {
            // 一度画面を真っさらに消す
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // 忍者の四角形を描く
            ctx.fillStyle = "#2c3e50";
            ctx.fillRect(ninja.x, ninja.y, ninja.size, ninja.size);
            
            // 四角形の中に文字（絵文字）を描く
            ctx.fillStyle = "white";
            ctx.font = "24px Arial";
            ctx.fillText("🥷", ninja.x + 8, ninja.y + 28);
        }

        // ゲームのメインループ（ずっと繰り返し続ける）
        function loop() {
            update();
            draw();
            requestAnimationFrame(loop); // 次の画面更新のタイミングでまたloopを呼ぶ
        }

        // ゲーム開始！
        loop();
    </script>
</body>
</html>
"""

# Streamlitの中に、上で書いたHTML/JSの「窓」を高さ450pxで埋め込む
components.html(html_code, height=450)
