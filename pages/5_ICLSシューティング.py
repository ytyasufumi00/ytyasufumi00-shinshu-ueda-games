import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="ICLS Quiz", page_icon="📝", layout="wide")
st.markdown("<h1 style='font-size: 32px; margin-bottom: 0px;'>📝 ICLS マニアック・クイズアタック</h1>", unsafe_allow_html=True)
st.markdown("<p style='font-size: 16px; color: #555;'>シミュレーターで鍛えた後は知識の解像度を上げるテストです。3回間違える前に10問クリアを目指してください！</p>", unsafe_allow_html=True)

html_code = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
    body { margin: 0; background: #2c3e50; font-family: 'Helvetica Neue', Arial, sans-serif; color: #fff; user-select: none; -webkit-user-select: none; overflow: hidden; }
    #game-container { display: flex; flex-direction: column; height: 100vh; max-width: 800px; margin: 0 auto; background: #1a252f; border: 2px solid #34495e; box-sizing: border-box; position: relative; }
    
    #header-area { display: flex; justify-content: space-between; padding: 10px 15px; background: #000; border-bottom: 2px solid #7f8c8d; font-size: 16px; font-weight: bold; }
    #lives { color: #e74c3c; letter-spacing: 2px; }
    #score-box { color: #f1c40f; }
    
    #nurse-area { display: flex; padding: 15px; background: #ecf0f1; align-items: center; min-height: 120px; position: relative; z-index: 10; }
    #nurseCanvas { width: 100px; height: 130px; margin-top: -30px; margin-right: 10px; flex-shrink: 0; filter: drop-shadow(0px 4px 4px rgba(0,0,0,0.3)); }
    #nurse-message-container { display: flex; flex-direction: column; justify-content: center; flex-grow: 1; }
    .nurse-bubble-item { background: #fff; padding: 10px 15px; border-radius: 12px; position: relative; font-size: 14px; font-weight: bold; box-shadow: 0 2px 5px rgba(0,0,0,0.15); line-height: 1.4; color: #2c3e50; }
    .nurse-bubble-item::before { content: ''; position: absolute; left: -12px; top: 15px; border-top: 8px solid transparent; border-bottom: 8px solid transparent; border-right: 12px solid #fff; }
    
    #quiz-area { padding: 15px; flex-grow: 1; display: flex; flex-direction: column; gap: 15px; overflow-y: auto; background: #1a252f; }
    
    #question-panel { background: #34495e; padding: 15px; border-radius: 8px; border-left: 6px solid #3498db; box-shadow: 0 4px 6px rgba(0,0,0,0.2); }
    #q-number { font-size: 12px; color: #bdc3c7; margin-bottom: 5px; font-weight: bold; letter-spacing: 1px; }
    #question-text { font-size: 16px; font-weight: bold; line-height: 1.4; }
    
    #timer-wrapper { height: 8px; background: #2c3e50; border-radius: 4px; overflow: hidden; margin-top: 15px; border: 1px solid #7f8c8d; }
    #timer-bar { height: 100%; width: 100%; background: #2ecc71; transition: width 1s linear, background-color 0.5s; }
    
    #options-grid { display: grid; grid-template-columns: 1fr; gap: 10px; }
    .option-btn { background: #2c3e50; color: #fff; border: 2px solid #7f8c8d; padding: 12px 15px; border-radius: 8px; cursor: pointer; text-align: left; font-size: 14px; font-weight: bold; box-shadow: 0 4px #1a252f; transition: 0.1s; display: flex; align-items: center; }
    .option-btn:active { transform: translateY(4px); box-shadow: 0 0 #1a252f; }
    .option-btn:disabled { cursor: not-allowed; opacity: 0.8; transform: translateY(4px); box-shadow: 0 0 #1a252f; }
    .option-btn.correct { background: #27ae60 !important; border-color: #2ecc71 !important; color: white !important; }
    .option-btn.incorrect { background: #c0392b !important; border-color: #e74c3c !important; color: white !important; }
    
    #next-btn-container { text-align: center; margin-top: 10px; display: none; }
    #next-btn { background: #f39c12; color: #fff; border: none; padding: 12px 30px; font-size: 16px; font-weight: bold; border-radius: 8px; cursor: pointer; box-shadow: 0 4px #d35400; }
    #next-btn:active { transform: translateY(4px); box-shadow: 0 0 #d35400; }

    #overlay { display: flex; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(26, 37, 47, 0.95); z-index: 50; flex-direction: column; justify-content: center; align-items: center; text-align: center; padding: 20px; box-sizing: border-box; }
    .overlay-title { font-size: 32px; font-weight: bold; margin-bottom: 10px; }
    .overlay-score { font-size: 40px; color: #f1c40f; font-weight: bold; margin-bottom: 20px; }
    .overlay-desc { font-size: 16px; color: #bdc3c7; margin-bottom: 30px; line-height: 1.5; max-width: 80%; }
    .start-btn { background: #2ecc71; color: white; border: none; padding: 15px 40px; font-size: 18px; font-weight: bold; border-radius: 8px; cursor: pointer; box-shadow: 0 4px #27ae60; }
    .start-btn:active { transform: translateY(4px); box-shadow: 0 0 #27ae60; }
</style>
</head>
<body>
<div id="game-container">
    <div id="overlay">
        <div style="font-size: 60px; margin-bottom: 10px;">💉</div>
        <div class="overlay-title">ICLS マニアック・クイズ</div>
        <div class="overlay-desc">現場で「アミオダロン300入れて！」と指示するだけでは不十分です。<br>希釈液は？投与間隔は？細かい知識の解像度を試す10問のテストです。<br><span style="color:#e74c3c; font-weight:bold;">※3回間違える（または時間切れ）とゲームオーバーです。</span></div>
        <button class="start-btn" onclick="initGame()">テストを開始する</button>
    </div>

    <div id="header-area">
        <div>LIFE: <span id="lives">❤️❤️❤️</span></div>
        <div>SCORE: <span id="score-box">0</span> 点</div>
    </div>
    
    <div id="nurse-area">
        <canvas id="nurseCanvas" width="100" height="130"></canvas>
        <div id="nurse-message-container">
            <div id="nurse-msg" class="nurse-bubble-item">先生、細かい知識も完璧にして、病棟のレジデントを圧倒しましょう！</div>
        </div>
    </div>
    
    <div id="quiz-area">
        <div id="question-panel">
            <div id="q-number">QUESTION 1 / 10</div>
            <div id="question-text">読み込み中...</div>
            <div id="timer-wrapper"><div id="timer-bar"></div></div>
        </div>
        
        <div id="options-grid">
            </div>
        
        <div id="next-btn-container">
            <button id="next-btn" onclick="nextQuestion()">次の問題へ ➔</button>
        </div>
    </div>
</div>

<script>
    // 🌟 マニアックなICLS知識データベース
    const sourceQuestions = [
        {
            q: "アミオダロン（アンカロン）初回300mgの静注時、推奨される希釈液と液量は？",
            options: ["5%ブドウ糖液 20mL", "生理食塩水 20mL", "5%ブドウ糖液 100mL", "希釈せず原液のまま"],
            ans: 0,
            exp: "アミオダロンは生理食塩水で希釈すると結晶化して白濁する恐れがあるため、必ず「5%ブドウ糖液」で希釈します。急速静注のため液量は20mL程度とします。"
        },
        {
            q: "高度な気道確保（気管挿管やi-gelなど）が完了した後の、胸骨圧迫と換気のタイミングは？",
            options: ["非同期で、換気は6秒に1回", "非同期で、換気は3秒に1回", "圧迫30回に対し換気2回", "圧迫15回に対し換気2回"],
            ans: 0,
            exp: "高度な気道確保後は圧迫の手を止めず（非同期）、換気は10回/分（6秒に1回）のペースで行います。過換気は静脈還流を減少させるため厳禁です。"
        },
        {
            q: "リズムチェックで胸骨圧迫を中断する際、許容される最大の中断時間は？",
            options: ["10秒以内", "5秒以内", "15秒以内", "20秒以内"],
            ans: 0,
            exp: "胸骨圧迫の中断は「いかなる場合も10秒以内」が鉄則です。長く止まるほど脳や心筋への血流が途絶え、自己心拍再開率が低下します。"
        },
        {
            q: "PEA/Asystoleの可逆的な原因「4H4T」に含まれないのはどれ？",
            options: ["高カルシウム血症", "循環血液量減少", "緊張性気胸", "心タンポナーデ"],
            ans: 0,
            exp: "4H4Tの「H」は、Hypoxia(低酸素), Hypovolemia(循環血漿量減少), Hypo/Hyperkalemia(低/高カリウム等), Hydrogen ion(アシドーシス), Hypothermia(低体温)です。カルシウムは含まれません。"
        },
        {
            q: "リドカインをVF/pVTに対して初回投与する場合の適切な用量は？",
            options: ["1.0〜1.5 mg/kg", "0.5〜0.75 mg/kg", "3.0 mg/kg", "300 mg"],
            ans: 0,
            exp: "リドカインの初回投与量は「1.0〜1.5 mg/kg」です。アミオダロン（300mg固定）と違い、体重換算である点に注意が必要です。"
        },
        {
            q: "成人の質の高いCPRにおいて、胸骨圧迫の深さとテンポのガイドライン推奨は？",
            options: ["深さ5cm以上(6cm未満)、テンポ100〜120回/分", "深さ5cm以上、テンポ80〜100回/分", "深さ少なくとも5cm、上限なし", "深さ4cm以上、テンポ100〜120回/分"],
            ans: 0,
            exp: "深さは「少なくとも5cm（ただし6cmを超えない）」、テンポは「100〜120回/分」です。早すぎても深すぎても質が低下します。"
        },
        {
            q: "アドレナリン1mg静注後、薬剤を中心静脈に早く到達させるために行うべき「後押し（フラッシュ）」の適切な方法は？",
            options: ["生食20mLを静注し、下肢を挙上する", "生食10mLを静注するのみ", "5%ブドウ糖液20mLを静注する", "特に後押しは必要ない"],
            ans: 0,
            exp: "末梢静脈から投与した薬剤を心臓へ素早く送るため、投与直後に「20mLの生理食塩水」で後押しし、その腕（または下肢）を10〜20秒高く挙上します。"
        },
        {
            q: "呼気終末二酸化炭素分圧（PETCO2）モニタリング中。ROSC（自己心拍再開）を示唆する急激な上昇の目安となる値は？",
            options: ["35〜40 mmHg以上", "10〜15 mmHg以上", "20〜25 mmHg以上", "50〜60 mmHg以上"],
            ans: 0,
            exp: "ROSCすると肺血流が劇的に再開するため、PETCO2が急激に上昇し「35〜40 mmHg以上」の正常値付近を示すことがROSCの強力な指標となります。"
        },
        {
            q: "アミオダロンの追加投与（2回目）の適切な用量は？",
            options: ["150 mg", "300 mg", "1.5 mg/kg", "1.0 mg/kg"],
            ans: 0,
            exp: "初回は300mgですが、2回目（第5回ショック後）の追加投与量は「半量の150mg」です。これ以降の追加は推奨されておらず極量となります。"
        },
        {
            q: "心タンポナーデや緊張性気胸の迅速な原因検索に最も有用とされるベッドサイドの検査は？",
            options: ["超音波検査（POCUS）", "胸部X線ポータブル", "12誘導心電図", "血液ガス分析"],
            ans: 0,
            exp: "PEAの原因検索において、超音波検査（Point-of-Care Ultrasound: POCUS）は心嚢液貯留や肺スライディングの消失を数秒で確認できる最強のツールです。"
        },
        {
            q: "自己心拍再開（ROSC）後の目標体温管理（TTM）において、推奨される目標温度の範囲は？",
            options: ["32℃〜36℃の間で一定に維持", "30℃〜32℃の深低体温", "36℃〜38℃の正常体温", "一律に34℃に設定"],
            ans: 0,
            exp: "ガイドラインでは、32℃〜36℃の範囲から1つの目標温度を選択し、少なくとも24時間、その温度を厳格に一定に維持することが推奨されています。"
        },
        {
            q: "波形がAsystole（心静止）の場合、電極パッド（またはパドル）の確認として行うべき行動は？",
            options: ["リード線の外れや感度（ゲイン）の確認", "直ちに150Jで盲目的にショック", "ペーシングの準備", "アミオダロンの準備"],
            ans: 0,
            exp: "真のAsystoleか、単なる「リード線の外れ」や「感度不足による微細VFの波形フラット化」かを鑑別するため、接続と感度の確認（誘導の変更）が必須です。"
        }
    ];

    let gameQuestions = [];
    let currentQIndex = 0;
    let score = 0;
    let life = 3;
    let timer = 15;
    let timerInterval = null;
    let isAnswered = false;

    // --- ナースちゃんのアニメーションロジック ---
    const canvas = document.getElementById("ecgCanvas");
    let frame = 0;
    let nurseState = 'idle';

    function drawNurse() {
        const nCanvas = document.getElementById("nurseCanvas");
        if(!nCanvas) return;
        const nCtx = nCanvas.getContext("2d");
        nCtx.clearRect(0, 0, 100, 130); nCtx.save(); 
        nCtx.translate(50, 80);

        let bounce = 0;
        if (nurseState === 'idle') bounce = Math.sin(frame * 0.08) * 2;
        else if (nurseState === 'happy' || nurseState === 'cracker') bounce = Math.abs(Math.sin(frame * 0.3)) * -6; 
        else if (nurseState === 'ok_circle') bounce = Math.abs(Math.sin(frame * 0.2)) * -5; 
        else if (nurseState === 'sparkle' || nurseState === 'heart') bounce = Math.sin(frame * 0.1) * 2; 
        else if (nurseState === 'angry') nCtx.translate((Math.random()-0.5)*3, (Math.random()-0.5)*3);
        else if (nurseState === 'thinking') bounce = Math.sin(frame * 0.05) * 1; 
        else if (nurseState === 'shock') bounce = Math.random() * 4 - 2;

        nCtx.translate(0, bounce);

        // 髪・顔輪郭
        nCtx.fillStyle = "#ffffff"; nCtx.fillRect(-18, -32, 36, 12);
        nCtx.fillStyle = "#e74c3c"; nCtx.fillRect(-2, -30, 4, 8); nCtx.fillRect(-4, -28, 8, 4);
        nCtx.fillStyle = "#8e44ad"; nCtx.beginPath(); nCtx.arc(0, -10, 16, 0, Math.PI*2); nCtx.fill();
        nCtx.fillStyle = "#ffdbac"; nCtx.beginPath(); nCtx.arc(0, -12, 14, 0, Math.PI*2); nCtx.fill();
        nCtx.lineWidth = 1.5; nCtx.strokeStyle = "#2c3e50"; nCtx.fillStyle = "#2c3e50";
        
        // 表情
        if (nurseState === 'idle') {
            nCtx.fillRect(-6, -15, 3, 3); nCtx.fillRect(3, -15, 3, 3); nCtx.beginPath(); nCtx.arc(0, -7, 4, 0, Math.PI, false); nCtx.stroke();
        } else if (nurseState === 'happy' || nurseState === 'cracker' || nurseState === 'ok_circle') { 
            nCtx.beginPath(); nCtx.arc(-5, -13, 3, Math.PI, 0, false); nCtx.stroke(); nCtx.beginPath(); nCtx.arc(5, -13, 3, Math.PI, 0, false); nCtx.stroke();
            nCtx.beginPath(); nCtx.arc(0, -7, 5, 0, Math.PI, false); nCtx.stroke(); 
            nCtx.fillStyle = "#ff9999"; nCtx.beginPath(); nCtx.arc(-8, -9, 3, 0, Math.PI*2); nCtx.fill(); nCtx.beginPath(); nCtx.arc(8, -9, 3, 0, Math.PI*2); nCtx.fill(); 
        } else if (nurseState === 'sparkle' || nurseState === 'heart') { 
            nCtx.fillStyle = "#f1c40f"; nCtx.save(); nCtx.translate(-5, -13); nCtx.rotate(Math.PI/4); nCtx.fillRect(-2.5, -2.5, 5, 5); nCtx.restore();
            nCtx.save(); nCtx.translate(5, -13); nCtx.rotate(Math.PI/4); nCtx.fillRect(-2.5, -2.5, 5, 5); nCtx.restore();
            nCtx.fillStyle = "#ff9999"; nCtx.beginPath(); nCtx.arc(-9, -9, 2.5, 0, Math.PI*2); nCtx.fill(); nCtx.beginPath(); nCtx.arc(9, -9, 2.5, 0, Math.PI*2); nCtx.fill();
            nCtx.beginPath(); nCtx.arc(0, -7, 3, 0, Math.PI, false); nCtx.stroke();
        } else if (nurseState === 'thinking') {
            nCtx.beginPath(); nCtx.arc(-5, -15, 2, 0, Math.PI*2); nCtx.fill(); nCtx.beginPath(); nCtx.arc(5, -15, 2, 0, Math.PI*2); nCtx.fill();
            nCtx.beginPath(); nCtx.arc(0, -7, 3, 0, Math.PI*2); nCtx.stroke(); nCtx.fillStyle = "#3498db"; nCtx.beginPath(); nCtx.arc(12, -18, 3, 0, Math.PI*2); nCtx.fill(); nCtx.fillStyle = "#2c3e50";
        } else if (nurseState === 'angry' || nurseState === 'shock') {
            nCtx.beginPath(); nCtx.moveTo(-8, -18); nCtx.lineTo(-3, -15); nCtx.stroke(); nCtx.beginPath(); nCtx.moveTo(8, -18); nCtx.lineTo(3, -15); nCtx.stroke();
            if(nurseState==='shock') { nCtx.beginPath(); nCtx.arc(-5, -14, 2, 0, Math.PI*2); nCtx.stroke(); nCtx.beginPath(); nCtx.arc(5, -14, 2, 0, Math.PI*2); nCtx.stroke(); }
            else { nCtx.fillRect(-6, -14, 3, 3); nCtx.fillRect(3, -14, 3, 3); }
            nCtx.beginPath(); nCtx.arc(0, -6, 4, 0, Math.PI, true); nCtx.stroke();
            if(nurseState==='angry') { nCtx.strokeStyle = "#e74c3c"; nCtx.beginPath(); nCtx.moveTo(12, -22); nCtx.lineTo(16,-18); nCtx.lineTo(20,-22); nCtx.stroke(); nCtx.strokeStyle = "#2c3e50"; }
        }

        // 体
        nCtx.fillStyle = "#ffffff"; nCtx.fillRect(-14, 2, 28, 22);
        
        // 腕とエフェクト
        nCtx.fillStyle = "#ffdbac"; nCtx.strokeStyle = "#ffffff";
        if (nurseState === 'happy') {
            nCtx.fillRect(-22, -15, 5, 20); nCtx.fillRect(17, -15, 5, 20); 
        } else if (nurseState === 'cracker') {
            nCtx.fillRect(13, -25, 5, 20); nCtx.fillRect(-18, 4, 5, 10);
            nCtx.fillStyle = "#e67e22"; nCtx.beginPath(); nCtx.moveTo(15, -25); nCtx.lineTo(5, -35); nCtx.lineTo(25, -35); nCtx.fill();
            let pOffset = (frame % 20); let colors = ["#e74c3c", "#3498db", "#2ecc71", "#f1c40f"];
            for(let i=0; i<6; i++) { nCtx.fillStyle = colors[i%4]; nCtx.fillRect(15 + (i-3)*8, -45 - pOffset - (i%3)*5, 3, 3); }
        } else if (nurseState === 'ok_circle') {
            nCtx.strokeStyle = "#ffdbac"; nCtx.lineWidth = 5;
            nCtx.beginPath(); nCtx.arc(0, -28, 18, Math.PI, 0); nCtx.stroke(); nCtx.lineWidth = 1.5;
        } else if (nurseState === 'heart' || nurseState === 'sparkle') {
            nCtx.fillRect(-18, 4, 5, 14); nCtx.fillRect(13, 4, 5, 14); 
            if(nurseState === 'heart') {
                let hY = -45 + Math.sin(frame*0.2)*3; nCtx.fillStyle = "#e74c3c";
                nCtx.beginPath(); nCtx.arc(-4, hY, 4, 0, Math.PI*2); nCtx.fill();
                nCtx.beginPath(); nCtx.arc(4, hY, 4, 0, Math.PI*2); nCtx.fill();
                nCtx.beginPath(); nCtx.moveTo(-8, hY); nCtx.lineTo(8, hY); nCtx.lineTo(0, hY+7); nCtx.fill();
            }
        } else if (nurseState === 'thinking') {
            nCtx.fillRect(-18, 4, 5, 12); nCtx.fillRect(6, -6, 12, 5); 
        } else if (nurseState === 'angry' || nurseState === 'shock') {
            nCtx.fillRect(-15, 8, 15, 5); nCtx.fillRect(0, 8, 15, 5); 
        } else {
            nCtx.fillRect(-18, 4, 5, 14); nCtx.fillRect(13, 4, 5, 14); 
        }
        
        nCtx.restore();
        frame++;
        requestAnimationFrame(drawNurse);
    }
    requestAnimationFrame(drawNurse);

    function updateNurseMsg(msg, state) {
        document.getElementById("nurse-msg").innerHTML = msg;
        nurseState = state;
    }

    // --- ゲームロジック ---
    function shuffleArray(array) {
        let curId = array.length;
        while (0 !== curId) {
            let randId = Math.floor(Math.random() * curId);
            curId -= 1;
            let tmp = array[curId]; array[curId] = array[randId]; array[randId] = tmp;
        }
        return array;
    }

    function initGame() {
        document.getElementById("overlay").style.display = "none";
        
        // 10問をランダム抽出
        let shuffled = shuffleArray([...sourceQuestions]);
        gameQuestions = shuffled.slice(0, 10);
        
        currentQIndex = 0; score = 0; life = 3;
        updateLifeUI();
        document.getElementById("score-box").innerText = score;
        loadQuestion();
    }

    function loadQuestion() {
        isAnswered = false;
        document.getElementById("next-btn-container").style.display = "none";
        document.getElementById("q-number").innerText = `QUESTION ${currentQIndex + 1} / 10`;
        
        let qData = gameQuestions[currentQIndex];
        document.getElementById("question-text").innerHTML = qData.q;
        
        // 選択肢のシャッフルとボタン生成
        let ops = qData.options.map((opt, idx) => ({ text: opt, isCorrect: idx === qData.ans }));
        ops = shuffleArray(ops);
        
        let grid = document.getElementById("options-grid");
        grid.innerHTML = "";
        ops.forEach((o, i) => {
            let btn = document.createElement("button");
            btn.className = "option-btn";
            btn.innerHTML = `<span style="display:inline-block; width:24px; height:24px; background:#1a252f; border-radius:50%; text-align:center; line-height:24px; margin-right:10px;">${['A','B','C','D'][i]}</span> ${o.text}`;
            btn.onclick = () => checkAnswer(o.isCorrect, btn, ops);
            grid.appendChild(btn);
        });

        updateNurseMsg("先生、制限時間は15秒です！的確な指示を！", "idle");
        startTimer();
    }

    function startTimer() {
        timer = 15;
        let bar = document.getElementById("timer-bar");
        bar.style.transition = "none"; bar.style.width = "100%"; bar.style.backgroundColor = "#2ecc71";
        setTimeout(() => { bar.style.transition = "width 1s linear, background-color 0.5s"; }, 50);

        if(timerInterval) clearInterval(timerInterval);
        timerInterval = setInterval(() => {
            timer--;
            let pct = (timer / 15) * 100;
            bar.style.width = `${pct}%`;
            
            if(timer <= 5) bar.style.backgroundColor = "#e74c3c";
            else if(timer <= 10) bar.style.backgroundColor = "#f1c40f";

            if(timer <= 0) {
                clearInterval(timerInterval);
                timeOut();
            }
        }, 1000);
    }

    function checkAnswer(isCorrect, selectedBtn, allOps) {
        if(isAnswered) return;
        isAnswered = true;
        clearInterval(timerInterval);
        
        let btns = document.getElementById("options-grid").children;
        for(let i=0; i<btns.length; i++) {
            btns[i].disabled = true;
            if(allOps[i].isCorrect) btns[i].classList.add("correct");
        }

        let qData = gameQuestions[currentQIndex];
        
        if(isCorrect) {
            score += 10 + timer; // 残り時間がスコアに加算
            document.getElementById("score-box").innerText = score;
            let goodStates = ['happy', 'cracker', 'ok_circle', 'heart'];
            updateNurseMsg(`<span style='color:#2ecc71; font-size:16px;'>大正解です！👏</span><br>${qData.exp}`, goodStates[Math.floor(Math.random()*goodStates.length)]);
        } else {
            selectedBtn.classList.add("incorrect");
            loseLife();
            updateNurseMsg(`<span style='color:#e74c3c; font-size:16px;'>違います先生！！💢</span><br>${qData.exp}`, "angry");
        }
        
        if(life > 0) {
            document.getElementById("next-btn-container").style.display = "block";
        }
    }

    function timeOut() {
        if(isAnswered) return;
        isAnswered = true;
        
        let btns = document.getElementById("options-grid").children;
        for(let i=0; i<btns.length; i++) btns[i].disabled = true;
        
        loseLife();
        let qData = gameQuestions[currentQIndex];
        updateNurseMsg(`<span style='color:#e74c3c; font-size:16px;'>時間切れです！判断が遅い！！💢</span><br>${qData.exp}`, "shock");
        
        if(life > 0) document.getElementById("next-btn-container").style.display = "block";
    }

    function loseLife() {
        life--;
        updateLifeUI();
        if(life <= 0) {
            setTimeout(showGameOver, 2500);
        }
    }

    function updateLifeUI() {
        let lStr = "";
        for(let i=0; i<3; i++) { lStr += (i < life) ? "❤️" : "🖤"; }
        document.getElementById("lives").innerText = lStr;
    }

    function nextQuestion() {
        currentQIndex++;
        if(currentQIndex >= 10) { showClear(); } 
        else { loadQuestion(); }
    }

    function showGameOver() {
        let ov = document.getElementById("overlay");
        ov.innerHTML = `
            <div style="font-size: 60px; margin-bottom: 10px;">💔</div>
            <div class="overlay-title" style="color:#e74c3c;">救命失敗...</div>
            <div class="overlay-desc">知識の欠如が現場の崩壊を招きました。<br>ガイドラインをもう一度復習してください。</div>
            <div class="overlay-score">SCORE: ${score} 点</div>
            <button class="start-btn" onclick="location.reload()">再挑戦する</button>
        `;
        ov.style.display = "flex";
        updateNurseMsg("先生…しっかり復習してから出直してきてください。", "angry");
    }

    function showClear() {
        let ov = document.getElementById("overlay");
        let rank = score >= 200 ? "👑 ICLSマニア (神)" : (score >= 150 ? "🏅 優秀なリーダー" : "🎖️ 合格ライン");
        ov.innerHTML = `
            <div style="font-size: 60px; margin-bottom: 10px;">🎉</div>
            <div class="overlay-title" style="color:#2ecc71;">全問クリア！！</div>
            <div class="overlay-desc" style="color:#f1c40f; font-size:20px; font-weight:bold;">称号: ${rank}</div>
            <div class="overlay-score">最終スコア: ${score} 点</div>
            <button class="start-btn" style="background:#3498db; box-shadow:0 4px #2980b9;" onclick="location.reload()">もう一度プレイ</button>
        `;
        ov.style.display = "flex";
        updateNurseMsg("先生、すごいです！完璧な知識ですね！これなら現場でも頼りになります！", "sparkle");
    }
</script>
</body>
</html>
"""
components.html(html_code, height=750)