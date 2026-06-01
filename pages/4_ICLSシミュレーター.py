import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="ICLS Simulator", page_icon="⚡", layout="wide")
st.markdown("<h1 style='font-size: 32px; margin-bottom: 0px;'>⚡ ICLS コマンド・シミュレーター V21</h1>", unsafe_allow_html=True)
st.markdown("<p style='font-size: 16px; color: #555;'>採点システム実装！減点を避け、100点満点の「ICLSマスター」の称号を手に入れろ！</p>", unsafe_allow_html=True)

html_code = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
    body { margin: 0; background: #2c3e50; font-family: 'Helvetica Neue', Arial, sans-serif; color: #fff; user-select: none; -webkit-user-select: none; overflow: hidden; }
    #game-container { display: flex; flex-direction: column; height: 100vh; max-width: 700px; margin: 0 auto; background: #1a252f; border: 2px solid #34495e; box-sizing: border-box; position: relative; }
    
    #monitor { background: #000; height: 130px; position: relative; border-bottom: 2px solid #7f8c8d; background-image: linear-gradient(rgba(46, 204, 113, 0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(46, 204, 113, 0.1) 1px, transparent 1px); background-size: 20px 20px; }
    canvas { width: 100%; height: 100%; display: block; }
    #monitor-text { position: absolute; top: 50px; width: 100%; text-align: center; color: #e74c3c; font-weight: bold; font-size: 18px; animation: text-blink 1s infinite alternate; }
    
    .btn-reset { position: absolute; top: 8px; right: 8px; z-index: 100; background: rgba(52, 73, 94, 0.8); color: white; border: 1px solid #bdc3c7; padding: 6px 10px; border-radius: 6px; cursor: pointer; font-weight: bold; }
    .btn-reset:active { background: #2c3e50; }
    
    #middle-panel { display: flex; padding: 10px 15px; background: #2c3e50; border-bottom: 4px solid #bdc3c7; height: 175px; position: relative; }
    
    #anim-area { flex: 1; display: flex; justify-content: center; align-items: center; position: relative; background: #34495e; border-radius: 8px; margin-right: 15px; box-shadow: inset 0 0 10px rgba(0,0,0,0.5); }
    .prep-controls { position: absolute; top: 8px; left: 8px; display: flex; flex-direction: column; gap: 6px; z-index: 20; }
    .prep-btn { background: #e67e22; color: #fff; border: 2px solid #d35400; border-radius: 6px; padding: 6px 8px; font-size: 12px; font-weight: bold; cursor: pointer; box-shadow: 0 2px #a04000; transition: 0.1s; }
    .prep-btn:active { transform: translateY(2px); box-shadow: 0 0 #a04000; }
    .prep-btn.secured { background: #2ecc71; border-color: #27ae60; box-shadow: 0 2px #1e8449; }
    
    .iv-pole { position: absolute; right: 15px; bottom: 15px; font-size: 45px; z-index: 5; display: none; }
    .patient { font-size: 70px; position: absolute; bottom: 5px; left: 50%; transform: translateX(-50%); }
    #cpr-wrapper { position: absolute; bottom: 35px; left: 50%; transform: translateX(-50%); display: none; flex-direction: column; align-items: center; z-index: 10; }
    .cpr-active { display: flex !important; }
    #cpr-anim-group { display: flex; flex-direction: column; align-items: center; animation: cpr-pump 0.54s infinite; }
    .cpr-label { color: #e74c3c; font-size: 13px; font-weight: bold; background: rgba(255,255,255,0.9); padding: 3px 8px; border-radius: 8px; margin-bottom: 2px; box-shadow: 0 2px 4px rgba(0,0,0,0.2); white-space: nowrap; }
    .rescuer { font-size: 50px; line-height: 1; margin-bottom: -15px; z-index: 12; }
    .hands { font-size: 45px; z-index: 11; }
    
    @keyframes cpr-pump { 0% { transform: translateY(0px); } 50% { transform: translateY(12px) scaleY(0.95); } 100% { transform: translateY(0px); } }
    @keyframes text-blink { 0% { opacity: 1; } 100% { opacity: 0.5; } }
    
    #status-area { flex: 1; display: flex; flex-direction: column; justify-content: space-between; font-size: 14px; font-weight: bold; }
    .timer-box { background: #000; padding: 5px; border-radius: 6px; text-align: center; border: 1px solid #7f8c8d; }
    .text-red { color: #e74c3c; font-size: 16px; } .text-green { color: #2ecc71; }
    .history-box { font-size: 13px; text-align: left; padding: 4px 8px; line-height: 1.3; }
    .hist-title-dc { color: #e74c3c; margin-bottom: 2px; } .hist-title-adr { color: #9b59b6; margin-top: 4px; margin-bottom: 2px; }
    .hist-text { color: #bdc3c7; margin-left: 5px; font-weight: normal; font-size: 12px; }
    
    #nurse-area { display: flex; padding: 10px 15px; background: #ecf0f1; align-items: center; min-height: 90px; }
    #nurseCanvas { width: 80px; height: 80px; margin-right: 10px; flex-shrink: 0; }
    #nurse-message-container { display: flex; flex-direction: column; gap: 6px; flex-grow: 1; justify-content: center; max-height: 120px; overflow-y: auto; }
    .nurse-bubble-item { background: #fff; padding: 8px 12px; border-radius: 12px; position: relative; font-size: 13px; font-weight: bold; box-shadow: 0 3px 5px rgba(0,0,0,0.15); line-height: 1.3; color: #2c3e50; }
    .nurse-bubble-item:first-child::before { content: ''; position: absolute; left: -10px; top: 10px; border-top: 8px solid transparent; border-bottom: 8px solid transparent; border-right: 10px solid #fff; }
    
    #command-area { padding: 10px; flex-grow: 1; background: #1a252f; position: relative; }
    .cmd-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; height: 100%; }
    .cmd-btn { background: #2980b9; color: white; border: none; border-radius: 6px; padding: 10px 5px; font-size: 13px; font-weight: bold; cursor: pointer; box-shadow: 0 4px #1f618d; transition: 0.1s; }
    .cmd-btn:active { transform: translateY(4px); box-shadow: 0 0 #1f618d; }
    .btn-shock { background: #e74c3c; box-shadow: 0 4px #c0392b; } .btn-shock:active { box-shadow: 0 0 #c0392b; }
    .btn-drug { background: #8e44ad; box-shadow: 0 4px #732d91; } .btn-drug:active { box-shadow: 0 0 #732d91; }
    .btn-diag { background: #d35400; box-shadow: 0 4px #a04000; } .btn-diag:active { box-shadow: 0 0 #a04000; }
    .btn-exam { background: #f39c12; box-shadow: 0 4px #b9770e; } .btn-exam:active { box-shadow: 0 0 #b9770e; }
    .btn-test { background: #16a085; box-shadow: 0 4px #0e6655; } .btn-test:active { box-shadow: 0 0 #0e6655; }
    .btn-back { background: #95a5a6; box-shadow: 0 4px #7f8c8d; grid-column: 1 / -1; }
    
    /* 🌟 リザルト画面をダークトーンに変更して文字を目立たせる */
    #clear-overlay { display: none; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(26, 37, 47, 0.95); z-index: 50; flex-direction: column; justify-content: center; align-items: center; text-align: center; }
</style>
</head>
<body>
<div id="game-container">
    <!-- 🌟 リザルト画面の拡張 -->
    <div id="clear-overlay">
        <div style="font-size: 60px; margin-bottom: 5px;">🎉</div>
        <div style="font-size: 28px; font-weight: bold; color: white; margin-bottom: 10px;">ROSC 確認！</div>
        <div id="result-rank" style="font-size: 24px; font-weight: bold; margin-bottom: 10px;"></div>
        <div id="result-score" style="font-size: 32px; font-weight: bold; margin-bottom: 15px; color: white;">総合得点: 100点</div>
        <div id="result-breakdown" style="font-size: 14px; color: #ecf0f1; text-align: left; width: 80%; max-width: 400px; max-height: 180px; overflow-y: auto; background: rgba(0,0,0,0.5); padding: 15px; border-radius: 8px;"></div>
        <button onclick="location.reload()" style="margin-top: 25px; padding: 15px 30px; font-size: 16px; background: #fff; color: #2c3e50; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; box-shadow: 0 4px rgba(0,0,0,0.3);">別の症例に挑む</button>
    </div>

    <div id="monitor">
        <button class="btn-reset" onclick="location.reload()">🔄 新たな症例</button>
        <div id="monitor-text">⚠️ モニター未装着</div>
        <canvas id="ecgCanvas"></canvas>
    </div>
    
    <div id="middle-panel">
        <div id="anim-area">
            <div class="prep-controls">
                <button id="btn-monitor" class="prep-btn" onclick="actionMonitor()">🖥️ モニター装着</button>
                <button id="btn-iv" class="prep-btn" onclick="actionIV()">💉 ルート確保</button>
            </div>
            <div class="patient">🛌</div>
            <div id="iv-pole" class="iv-pole">💧</div>
            <div id="cpr-wrapper">
                <div id="cpr-anim-group">
                    <div class="cpr-label">🚨 胸骨圧迫中</div>
                    <div class="rescuer">🧑‍⚕️</div>
                    <div class="hands">👐</div>
                </div>
            </div>
            <div id="shock-effect" style="display:none; position:absolute; font-size: 70px; z-index:20;">⚡</div>
        </div>
        <div id="status-area">
            <div class="timer-box">全体経過: <span id="total-time" class="text-green">0 分</span></div>
            <div class="timer-box">リズム確認: <span id="cycle-time" class="text-green">約 0 分</span></div>
            <div class="timer-box" style="border-color:#e74c3c;">圧迫中断: <span id="interrupt-time" class="text-red">0</span> 秒</div>
            <div class="timer-box history-box">
                <div class="hist-title-dc">⚡ 最終DC</div>
                <div id="time-since-shock" class="hist-text">未実施</div>
                <div class="hist-title-adr">💉 最終Adr</div>
                <div id="time-since-adr" class="hist-text">未実施</div>
            </div>
        </div>
    </div>
    
    <div id="nurse-area">
        <canvas id="nurseCanvas" width="80" height="80"></canvas>
        <div id="nurse-message-container">
            <div class="nurse-bubble-item">患者が倒れています！意識なし、呼吸なし！指示をお願いします！</div>
        </div>
    </div>
    
    <div id="command-area">
        <div id="menu-main" class="cmd-grid">
            <button class="cmd-btn" id="btn-cpr" onclick="actionCPR()">🤲 胸骨圧迫開始/再開</button>
            <button class="cmd-btn" id="btn-check" onclick="actionCheck()">⏱ リズムチェック</button>
            <button class="cmd-btn btn-shock" onclick="showMenu('menu-dc')">⚡ 除細動 (DC) 準備</button>
            <button class="cmd-btn btn-drug" onclick="showMenu('menu-drug')">💉 薬剤投与 指示</button>
            <button class="cmd-btn btn-exam" id="btn-exam" style="display:none;" onclick="actionPhysicalExam()">🔍 身体所見の確認</button>
            <button class="cmd-btn btn-test" id="btn-test" style="display:none;" onclick="actionSimpleTests()">🧪 簡単な検査 4K</button>
            <button class="cmd-btn btn-diag" onclick="showMenu('menu-diag')">💡 原因診断(4H4T)</button>
            <button class="cmd-btn" id="btn-air" onclick="actionAirway()">🗣 高度な気道確保</button>
        </div>
        
        <div id="menu-dc" class="cmd-grid" style="display:none;">
            <button class="cmd-btn btn-shock" onclick="actionShock(150)">⚡ 150 J</button>
            <button class="cmd-btn btn-shock" onclick="actionShock(200)">⚡ 200 J</button>
            <button class="cmd-btn btn-shock" onclick="actionShock(270)">⚡ 270 J</button>
            <button class="cmd-btn btn-shock" onclick="actionShock(360)">⚡ 360 J</button>
            <button class="cmd-btn btn-back" onclick="showMenu('main')">🔙 戻る</button>
        </div>

        <div id="menu-drug" class="cmd-grid" style="display:none;">
            <button class="cmd-btn btn-drug" onclick="actionDrug('Adrenaline', '1mg')">💉 アドレナリン 1mg</button>
            <button class="cmd-btn btn-drug" onclick="actionDrug('Amiodarone', '300mg')">💉 アミオダロン 300mg</button>
            <button class="cmd-btn btn-drug" onclick="actionDrug('Amiodarone', '150mg')">💉 アミオダロン 150mg</button>
            <button class="cmd-btn btn-drug" onclick="actionDrug('Lidocaine', '1mg/kg')">💉 リドカイン 1mg/kg</button>
            <button class="cmd-btn btn-back" onclick="showMenu('main')">🔙 戻る</button>
        </div>
        
        <div id="menu-diag" class="cmd-grid" style="display:none;">
            <button class="cmd-btn btn-diag" onclick="actionDiagnose('Hypoxia')">低酸素血症</button>
            <button class="cmd-btn btn-diag" onclick="actionDiagnose('Hypovolemia')">循環血液量減少</button>
            <button class="cmd-btn btn-diag" onclick="actionDiagnose('TensionPneumothorax')">緊張性気胸</button>
            <button class="cmd-btn btn-diag" onclick="actionDiagnose('CardiacTamponade')">心タンポナーデ</button>
            <button class="cmd-btn btn-diag" onclick="actionDiagnose('Hyperkalemia')">高カリウム血症</button>
            <button class="cmd-btn btn-back" onclick="showMenu('main')">🔙 戻る</button>
        </div>
    </div>
</div>

<script>
    const canvas = document.getElementById("ecgCanvas");
    const ctx = canvas.getContext("2d");
    function resizeCanvas() { canvas.width = canvas.parentElement.clientWidth; canvas.height = canvas.parentElement.clientHeight; }
    window.addEventListener('resize', resizeCanvas); resizeCanvas();

    let nurseState = 'idle'; 
    let currentManualMsg = ""; let manualMsgState = 'idle'; let manualMsgTimer = 0;
    let currentAutoMsgs = []; 

    let isMonitorOn = false; let isIvSecured = false;
    let totalTime = 0; let cycleTime = 0; let interruptTime = 0;
    let isCPR = false; let hasStarted = false; let pendingShock = false;
    let shockCount = 0; let adrCount = 0; let amioCount = 0;
    let gameInterval = null; 
    
    let lastShockTime = -1; let lastShockJoules = 0;
    let lastAdrTime = -1;   let lastAdrDose = "";
    let timeAtSecondShock = -1; let pendingShockTimer = 0;  
    
    let rhythms = ["VF", "VT", "Asystole", "PEA"];
    let rhythm = rhythms[Math.floor(Math.random() * rhythms.length)]; 
    let causes = ["Hypoxia", "Hypovolemia", "TensionPneumothorax", "CardiacTamponade", "Hyperkalemia"];
    let peaCause = causes[Math.floor(Math.random() * causes.length)];
    let causeTreated = false; 
    
    const uiTotalTime = document.getElementById("total-time");
    const uiCycleTime = document.getElementById("cycle-time");
    const uiInterruptTime = document.getElementById("interrupt-time");
    const uiShockHist = document.getElementById("time-since-shock");
    const uiAdrHist = document.getElementById("time-since-adr");
    const msgContainer = document.getElementById("nurse-message-container");
    const cprWrapper = document.getElementById("cpr-wrapper"); 
    const shockEffect = document.getElementById("shock-effect");
    const clearOverlay = document.getElementById("clear-overlay");

    // 🌟 ミスと遅延のトラッキング（減点対象を網羅）
    let mistakes = { 
        notStarted: 0, earlyCheck: 0, checkWhileNotCPR: 0, shockNotIndicated: 0, 
        earlyAdr: 0, wrongAmio: 0, amioDose: 0, wrongDiag: 0, noMonitor: 0, noIV: 0,
        handsOffLong: 0, checkDelay: 0, adrDelay: 0
    };
    
    function isShockable(r) { return r === "VF" || r === "VT"; }

    function showMenu(menuId) {
        document.getElementById("menu-main").style.display = "none"; document.getElementById("menu-dc").style.display = "none";
        document.getElementById("menu-drug").style.display = "none"; document.getElementById("menu-diag").style.display = "none";
        if(menuId === 'main') document.getElementById("menu-main").style.display = "grid"; else document.getElementById(menuId).style.display = "grid";
    }

    function getRandomPraise() { const praises = ["了解！先生、指示が的確で助かります！", "はい！タイミングばっちりですね！", "了解です！スムーズな進行ですね✨"]; return praises[Math.floor(Math.random() * praises.length)]; }
    function getRandomGreatPraise() { const praises = ["正解です！素晴らしいアセスメント！✨", "さすが先生！見事な着眼点です！👏", "完璧です！すぐに特異的治療を開始します！"]; return praises[Math.floor(Math.random() * praises.length)]; }
    function getRandomHappyState() { const states = ['happy', 'guts', 'sparkle', 'nod']; return states[Math.floor(Math.random() * states.length)]; }

    function setNurseMessage(msg, state = 'idle', duration = 4) { currentManualMsg = msg; manualMsgState = state; manualMsgTimer = duration; updateBubbleUI(); }

    function getApproxMinutes(sec) { if(sec < 5) return "0 分"; return Math.floor(sec / 10) + " 分"; }
    function getCycleTimeStr(sec) {
        if(sec < 8) return "1 分未満"; if(sec < 18) return "約 1 分";
        if(sec < 21) return "<span style='color:#f1c40f;'>まもなく 2 分！</span>"; return "<span style='color:#e74c3c;'>2 分超過!!</span>";
    }
    function getActionTimeStr(diff, type) {
        if (diff < 5) return "さきほど"; if (diff < 15) return "約1分経過";
        if (type === 'DC') {
            if (diff < 19) return "<span style='color:#f1c40f; font-weight:bold;'>まもなく2分!</span>";
            if (diff < 25) return "<span style='color:#e74c3c; font-weight:bold;'>約2分経過!</span>"; return "<span style='color:#e74c3c;'>長期間未実施</span>";
        } else if (type === 'Adr') {
            if (diff < 25) return "約2分経過"; if (diff < 35) return "<span style='color:#2ecc71; font-weight:bold;'>約3分経過 (可)</span>";
            if (diff < 50) return "<span style='color:#2ecc71; font-weight:bold;'>約4分経過 (可)</span>"; return "<span style='color:#e74c3c; font-weight:bold;'>5分以上経過！</span>";
        } return "不明";
    }

    function updateActionTimers() {
        if (lastShockTime >= 0) uiShockHist.innerHTML = `[${shockCount}回目] ${lastShockJoules}J : ${getActionTimeStr(totalTime - lastShockTime, 'DC')}`;
        if (lastAdrTime >= 0) uiAdrHist.innerHTML = `[${adrCount}回目] ${lastAdrDose} : ${getActionTimeStr(totalTime - lastAdrTime, 'Adr')}`;
    }

    function triggerError(type) {
        mistakes[type]++; let count = mistakes[type]; let msg = ""; let nState = count === 1 ? 'thinking' : 'angry'; 
        if(type === 'noMonitor') msg = "先生、モニターがついていません！波形が分かりません！💢";
        else if(type === 'noIV') msg = "先生、まだ静脈ルートが確保されていません！薬剤が入りません💦";
        else if(type === 'notStarted') msg = count === 1 ? "先生、まずは胸骨圧迫を開始してください💦" : "先生！患者さんが目の前にいます！胸骨圧迫が最優先です！💢";
        else if(type === 'earlyCheck') msg = count === 1 ? "先生、リズムチェックは2分ごとです！まだ時間が来ていません💦" : "先生！まだ2分経ってません！むやみに胸骨圧迫を中断しないで！💢";
        else if(type === 'checkWhileNotCPR') msg = count === 1 ? "先生、今はすでに圧迫を中断して評価中です。早く次の指示を💦" : "先生！何度も評価しないで、早く指示を！💢";
        else if(type === 'shockNotIndicated') msg = count === 1 ? `先生、波形は${rhythm}です！ショック適応のタイミングではありません💦` : "先生、だからショックは打てません！波形とアルゴリズムを見て！💢";
        else if(type === 'earlyAdr') msg = count === 1 ? "先生、VF/VTの場合アドレナリンは「第2回ショックの後」です！まだ早いです💦" : "先生！アドレナリンはまだですって！アルゴリズム思い出して！💢";
        else if(type === 'wrongAmio') msg = count === 1 ? "先生、アミオダロンの波形・タイミングが違います。VF/pVTで第3回ショック後です💦" : "先生！アミオダロンは「VF/pVTで第3回ショック後」です！💢";
        else if(type === 'wrongDiag') msg = count === 1 ? "先生、身体所見と合わない気がします…もう一度所見を確認してください💦" : "先生！原因が違います！適当に選ばないでください！💢";
        setNurseMessage(`<span style='color:#e74c3c; font-weight:bold;'>${msg}</span>`, nState, 6);
    }

    // 🌟 スコア計算関数
    function calculateScore() {
        let score = 100;
        let breakdown = [];
        
        if(mistakes.notStarted > 0) { score -= mistakes.notStarted * 5; breakdown.push(`胸骨圧迫の開始遅延 (-${mistakes.notStarted * 5}点)`); }
        if(mistakes.noMonitor > 0) { score -= mistakes.noMonitor * 5; breakdown.push(`モニター未装着での進行 (-${mistakes.noMonitor * 5}点)`); }
        if(mistakes.noIV > 0) { score -= mistakes.noIV * 5; breakdown.push(`ルート未確保での薬剤指示 (-${mistakes.noIV * 5}点)`); }
        
        let checkErrs = mistakes.earlyCheck + mistakes.checkWhileNotCPR;
        if(checkErrs > 0) { score -= checkErrs * 10; breakdown.push(`不適切なリズムチェック (-${checkErrs * 10}点)`); }
        if(mistakes.shockNotIndicated > 0) { score -= mistakes.shockNotIndicated * 20; breakdown.push(`ショック非適応でのDC指示 (-${mistakes.shockNotIndicated * 20}点)`); }
        
        let drugErrs = mistakes.earlyAdr + mistakes.wrongAmio + mistakes.amioDose;
        if(drugErrs > 0) { score -= drugErrs * 15; breakdown.push(`不適切な薬剤投与 (-${drugErrs * 15}点)`); }
        if(mistakes.wrongDiag > 0) { score -= mistakes.wrongDiag * 10; breakdown.push(`不適切な原因診断(誤診) (-${mistakes.wrongDiag * 10}点)`); }
        
        if(mistakes.handsOffLong > 0) { score -= mistakes.handsOffLong * 10; breakdown.push(`長すぎる圧迫中断(10秒以上) (-${mistakes.handsOffLong * 10}点)`); }
        if(mistakes.checkDelay > 0) { score -= mistakes.checkDelay * 10; breakdown.push(`リズムチェックの過度な遅延 (-${mistakes.checkDelay * 10}点)`); }
        if(mistakes.adrDelay > 0) { score -= mistakes.adrDelay * 10; breakdown.push(`アドレナリン投与の過度な遅延 (-${mistakes.adrDelay * 10}点)`); }

        if(score < 0) score = 0;

        let rank = ""; let rankColor = "";
        if(score === 100) { rank = "👑 ICLSマスター (神レベル)"; rankColor = "#f1c40f"; }
        else if(score >= 80) { rank = "🏅 優秀なリーダー (臨床即戦力)"; rankColor = "#2ecc71"; }
        else if(score >= 60) { rank = "🎖️ 中堅プロバイダー (あと一歩！)"; rankColor = "#3498db"; }
        else { rank = "🔰 ICLS研修生 (要復習)"; rankColor = "#e74c3c"; }

        return { score, breakdown, rank, rankColor };
    }

    function triggerROSC() {
        if(gameInterval) clearInterval(gameInterval); gameInterval = null; isCPR = false; cprWrapper.classList.remove("cpr-active");
        
        // 🌟 最終スコアの計算とUI反映
        let res = calculateScore();
        document.getElementById("result-rank").innerText = res.rank;
        document.getElementById("result-rank").style.color = res.rankColor;
        document.getElementById("result-score").innerText = `総合得点: ${res.score}点`;
        
        let bdHtml = res.breakdown.length === 0 ? "<div style='color:#2ecc71; font-size:16px;'>減点なし！完璧なアルゴリズムです！</div>" 
                                                : "<div style='margin-bottom:5px; font-weight:bold; color:#e74c3c;'>【減点対象】</div>" + res.breakdown.map(item => `・${item}`).join("<br>");
        document.getElementById("result-breakdown").innerHTML = bdHtml;
        
        clearOverlay.style.display = "flex"; 
        setNurseMessage("<span style='color:#2ecc71; font-weight:bold;'>先生！すごいです！完璧なアルゴリズムでした！自己心拍再開(ROSC)です！！</span>", "sparkle", 999);
    }

    function updateBubbleUI() {
        let finalMsgs = [];
        if(manualMsgTimer > 0 && currentManualMsg !== "") finalMsgs.push(currentManualMsg);
        currentAutoMsgs.forEach(m => finalMsgs.push(m.text));
        
        if(finalMsgs.length === 0) { finalMsgs.push("指示をお願いします！"); nurseState = 'idle'; } 
        else {
            if(manualMsgTimer > 0) { nurseState = manualMsgState; } 
            else {
                let hasAngry = currentAutoMsgs.some(m => m.state === 'angry'); let hasThink = currentAutoMsgs.some(m => m.state === 'thinking');
                nurseState = hasAngry ? 'angry' : (hasThink ? 'thinking' : 'idle');
            }
        }
        let html = ""; finalMsgs.forEach(m => { html += `<div class="nurse-bubble-item">${m}</div>`; });
        msgContainer.innerHTML = html; msgContainer.scrollTop = msgContainer.scrollHeight;
    }

    function startGame() {
        if(gameInterval) clearInterval(gameInterval);
        hasStarted = true;
        gameInterval = setInterval(() => {
            totalTime++; uiTotalTime.innerText = getApproxMinutes(totalTime); uiCycleTime.innerHTML = getCycleTimeStr(cycleTime); updateActionTimers(); 
            if(manualMsgTimer > 0) manualMsgTimer--;
            let autoMsgs = [];
            
            if(isCPR) {
                cycleTime++; interruptTime = 0; 
                // 🌟 時間遅延ペナルティの記録（該当時刻に1回だけカウント）
                if(cycleTime === 32) mistakes.checkDelay++;
                
                if(cycleTime >= 32) autoMsgs.push({text: "<span style='color:red;'>先生！！もう3分経っちゃいます！リズムチェック！！！💢</span>", state: "angry"});
                else if(cycleTime >= 26) autoMsgs.push({text: "<span style='color:red;'>先生、2分過ぎてます！早くリズムチェックを！💦</span>", state: "thinking"});
                else if(cycleTime >= 21) autoMsgs.push({text: "<span style='color:red;'>2分経過！リズムチェックの指示を！</span>", state: "idle"});
                else if(cycleTime >= 18) autoMsgs.push({text: "圧迫開始からまもなく2分です！リズムチェックの準備をお願いします！", state: "idle"});
            } else {
                interruptTime++;
                if(!pendingShock && rhythm !== "ROSC") {
                    if(interruptTime === 12) mistakes.handsOffLong++; // 12秒中断でペナルティ
                    if(interruptTime >= 12) autoMsgs.push({text: "<span style='color:red;'>先生！！手が止まってます！早く圧迫を！！💢</span>", state: "angry"});
                    else if(interruptTime >= 6) autoMsgs.push({text: "<span style='color:red;'>中断が長いです！早く圧迫再開の指示を！</span>", state: "angry"});
                }
            }

            if(pendingShock) {
                pendingShockTimer++;
                if(pendingShockTimer === 20) mistakes.handsOffLong++; // DC指示忘れも圧迫中断とみなす
                if(pendingShockTimer >= 20) autoMsgs.push({text: "<span style='color:red;'>先生！！ショック適応です！早くDC指示を！！💢</span>", state: "angry"});
                else if(pendingShockTimer >= 10) autoMsgs.push({text: "<span style='color:red;'>先生、VF/VTです！早く除細動(DC)の指示を！💦</span>", state: "thinking"});
            } else { pendingShockTimer = 0; }

            if(rhythm !== "ROSC") {
                if(adrCount === 0) {
                    if(rhythm === "PEA" || rhythm === "Asystole") {
                        if(totalTime === 35) mistakes.adrDelay++;
                        if(totalTime >= 35) autoMsgs.push({text: "<span style='color:red;'>先生！！早く初回のアドレナリン指示を出して！！💢</span>", state: "angry"});
                        else if(totalTime >= 20) autoMsgs.push({text: "<span style='color:red;'>先生、非適応波形です！可及的速やかに初回アドレナリンを！💦</span>", state: "thinking"});
                    } else if(isShockable(rhythm) && shockCount >= 2 && timeAtSecondShock >= 0) {
                        let diff = totalTime - timeAtSecondShock;
                        if(diff === 35) mistakes.adrDelay++;
                        if(diff >= 35) autoMsgs.push({text: "<span style='color:red;'>先生！！早くアドレナリン投与して！！💢</span>", state: "angry"});
                        else if(diff >= 25) autoMsgs.push({text: "<span style='color:red;'>先生！初回アドレナリン忘れてませんか！？早く指示を！💦</span>", state: "thinking"});
                        else if(diff >= 15) autoMsgs.push({text: "先生、第2回ショックが終わりました。アドレナリンの指示をお願いします！", state: "idle"});
                    }
                } else {
                    let timeSinceAdr = totalTime - lastAdrTime;
                    if(timeSinceAdr === 60) mistakes.adrDelay++;
                    if(timeSinceAdr >= 60) autoMsgs.push({text: "<span style='color:red;'>先生！！アドレナリンの間隔空きすぎてます！！💢</span>", state: "angry"});
                    else if(timeSinceAdr >= 50) autoMsgs.push({text: "<span style='color:red;'>先生！アドレナリンから5分経過しました！次の投与指示を！💦</span>", state: "thinking"});
                    else if(timeSinceAdr >= 45) autoMsgs.push({text: "先生、アドレナリン投与からまもなく5分です！準備しますか？", state: "idle"});
                }
            }

            currentAutoMsgs = autoMsgs; updateBubbleUI(); uiInterruptTime.innerText = interruptTime;
        }, 1000);
    }

    let ecgX = 0; let frame = 0;
    
    function drawNurse() {
        const nCanvas = document.getElementById("nurseCanvas");
        if(!nCanvas) return;
        const nCtx = nCanvas.getContext("2d");
        nCtx.clearRect(0, 0, 80, 80); nCtx.save(); nCtx.translate(40, 45);

        let bounce = 0;
        if (nurseState === 'idle') bounce = Math.sin(frame * 0.08) * 2;
        else if (nurseState === 'roger') bounce = Math.abs(Math.sin(frame * 0.2)) * -4;
        else if (nurseState === 'happy') bounce = Math.abs(Math.sin(frame * 0.3)) * -6; 
        else if (nurseState === 'guts') bounce = Math.abs(Math.sin(frame * 0.2)) * -5; 
        else if (nurseState === 'sparkle') bounce = Math.sin(frame * 0.1) * 2; 
        else if (nurseState === 'nod') bounce = Math.sin(frame * 0.6) * 5; 
        else if (nurseState === 'angry') nCtx.translate((Math.random()-0.5)*3, (Math.random()-0.5)*3);
        else if (nurseState === 'thinking') bounce = Math.sin(frame * 0.05) * 1; 

        nCtx.translate(0, bounce);

        nCtx.fillStyle = "#ffffff"; nCtx.fillRect(-18, -32, 36, 12);
        nCtx.fillStyle = "#e74c3c"; nCtx.fillRect(-2, -30, 4, 8); nCtx.fillRect(-4, -28, 8, 4);
        nCtx.fillStyle = "#8e44ad"; nCtx.beginPath(); nCtx.arc(0, -10, 16, 0, Math.PI*2); nCtx.fill();
        nCtx.fillStyle = "#ffdbac"; nCtx.beginPath(); nCtx.arc(0, -12, 14, 0, Math.PI*2); nCtx.fill();
        nCtx.lineWidth = 1.5; nCtx.strokeStyle = "#2c3e50"; nCtx.fillStyle = "#2c3e50";
        
        if (nurseState === 'idle') {
            nCtx.fillRect(-6, -15, 3, 3); nCtx.fillRect(3, -15, 3, 3); nCtx.beginPath(); nCtx.arc(0, -7, 4, 0, Math.PI, false); nCtx.stroke();
        } else if (nurseState === 'roger' || nurseState === 'happy') {
            nCtx.beginPath(); nCtx.arc(-5, -13, 3, Math.PI, 0, false); nCtx.stroke(); nCtx.beginPath(); nCtx.arc(5, -13, 3, Math.PI, 0, false); nCtx.stroke();
            nCtx.beginPath(); nCtx.arc(0, -7, 5, 0, Math.PI, false); nCtx.stroke(); 
            if(nurseState === 'happy'){ nCtx.fillStyle = "#ff9999"; nCtx.beginPath(); nCtx.arc(-8, -9, 3, 0, Math.PI*2); nCtx.fill(); nCtx.beginPath(); nCtx.arc(8, -9, 3, 0, Math.PI*2); nCtx.fill(); }
        } else if (nurseState === 'guts') {
            nCtx.beginPath(); nCtx.arc(-5, -13, 3, Math.PI, 0, false); nCtx.stroke(); nCtx.beginPath(); nCtx.arc(5, -13, 3, Math.PI, 0, false); nCtx.stroke();
            nCtx.fillStyle = "#e74c3c"; nCtx.beginPath(); nCtx.arc(0, -7, 4, 0, Math.PI, false); nCtx.fill(); 
        } else if (nurseState === 'sparkle') {
            nCtx.fillStyle = "#f1c40f"; nCtx.save(); nCtx.translate(-5, -13); nCtx.rotate(Math.PI/4); nCtx.fillRect(-2.5, -2.5, 5, 5); nCtx.restore();
            nCtx.save(); nCtx.translate(5, -13); nCtx.rotate(Math.PI/4); nCtx.fillRect(-2.5, -2.5, 5, 5); nCtx.restore();
            nCtx.fillStyle = "#ff9999"; nCtx.beginPath(); nCtx.arc(-9, -9, 2.5, 0, Math.PI*2); nCtx.fill(); nCtx.beginPath(); nCtx.arc(9, -9, 2.5, 0, Math.PI*2); nCtx.fill();
            nCtx.beginPath(); nCtx.arc(0, -7, 3, 0, Math.PI, false); nCtx.stroke();
        } else if (nurseState === 'nod') {
            nCtx.beginPath(); nCtx.moveTo(-7,-14); nCtx.lineTo(-4,-12); nCtx.lineTo(-7,-10); nCtx.stroke(); nCtx.beginPath(); nCtx.moveTo(7,-14); nCtx.lineTo(4,-12); nCtx.lineTo(7,-10); nCtx.stroke();
            nCtx.beginPath(); nCtx.arc(0, -6, 3, 0, Math.PI, false); nCtx.stroke();
        } else if (nurseState === 'thinking') {
            nCtx.beginPath(); nCtx.arc(-5, -15, 2, 0, Math.PI*2); nCtx.fill(); nCtx.beginPath(); nCtx.arc(5, -15, 2, 0, Math.PI*2); nCtx.fill();
            nCtx.beginPath(); nCtx.arc(0, -7, 3, 0, Math.PI*2); nCtx.stroke(); nCtx.fillStyle = "#3498db"; nCtx.beginPath(); nCtx.arc(12, -18, 3, 0, Math.PI*2); nCtx.fill(); nCtx.fillStyle = "#2c3e50";
        } else if (nurseState === 'angry') {
            nCtx.beginPath(); nCtx.moveTo(-8, -18); nCtx.lineTo(-3, -15); nCtx.stroke(); nCtx.beginPath(); nCtx.moveTo(8, -18); nCtx.lineTo(3, -15); nCtx.stroke();
            nCtx.fillRect(-6, -14, 3, 3); nCtx.fillRect(3, -14, 3, 3); nCtx.beginPath(); nCtx.arc(0, -6, 4, 0, Math.PI, true); nCtx.stroke();
            nCtx.strokeStyle = "#e74c3c"; nCtx.beginPath(); nCtx.moveTo(12, -22); nCtx.lineTo(16,-18); nCtx.lineTo(20,-22); nCtx.stroke(); nCtx.strokeStyle = "#2c3e50";
        }

        nCtx.fillStyle = "#ffffff"; nCtx.fillRect(-14, 2, 28, 22);
        nCtx.fillStyle = "#ffdbac"; nCtx.strokeStyle = "#ffffff";
        if (nurseState === 'roger') {
            nCtx.beginPath(); nCtx.arc(0, -32, 18, Math.PI, 0); nCtx.lineWidth=5; nCtx.stroke(); nCtx.strokeStyle = "#ffdbac"; nCtx.stroke(); nCtx.lineWidth=1.5;
        } else if (nurseState === 'happy') {
            nCtx.fillRect(-22, -15, 5, 20); nCtx.fillRect(17, -15, 5, 20); 
        } else if (nurseState === 'guts') {
            nCtx.fillRect(13, -15, 5, 18); nCtx.beginPath(); nCtx.arc(15.5, -16, 4, 0, Math.PI*2); nCtx.fill(); nCtx.fillRect(-18, 4, 5, 10);  
        } else if (nurseState === 'sparkle') {
            nCtx.fillRect(-5, 0, 10, 8); 
        } else if (nurseState === 'nod') {
            nCtx.fillRect(-18, 4, 5, 14); nCtx.fillRect(13, 4, 5, 14); 
        } else if (nurseState === 'thinking') {
            nCtx.fillRect(-18, 4, 5, 12); nCtx.fillRect(6, -6, 12, 5); 
        } else if (nurseState === 'angry') {
            nCtx.fillRect(-15, 8, 15, 5); nCtx.fillRect(0, 8, 15, 5); 
        } else {
            nCtx.fillRect(-18, 4, 5, 14); nCtx.fillRect(13, 4, 5, 14); 
        }
        nCtx.restore();
    }

    function drawECG() {
        if(isMonitorOn) {
            ctx.fillStyle = 'rgba(0, 0, 0, 0.03)'; ctx.fillRect(0, 0, canvas.width, canvas.height); 
            ctx.fillStyle = '#000'; ctx.fillRect(ecgX, 0, 15, canvas.height);
            let targetY = canvas.height / 2;
            
            if(isCPR) targetY += Math.sin(frame * 0.4) * 30 + (Math.random() - 0.5) * 20;
            else if (rhythm === 'VF') targetY += Math.sin(frame * 0.15) * 25 + Math.sin(frame * 0.6) * 15 + (Math.random() - 0.5) * 10;
            else if (rhythm === 'VT') targetY += Math.sin(frame * 0.3) * 30 + Math.sin(frame * 0.3) * 5; 
            else if (rhythm === 'Asystole') targetY += Math.sin(frame * 0.05) * 2 + (Math.random() - 0.5) * 2;
            else if (rhythm === 'ROSC' || rhythm === 'PEA') {
                let cycle = frame % 80;
                if (cycle < 10) targetY -= 5; else if (cycle === 15) targetY += 10; else if (cycle === 17) targetY -= 45; 
                else if (cycle === 19) targetY += 15; else if (cycle > 40 && cycle < 55) targetY -= 10; 
                else targetY += (Math.random() - 0.5) * 2; 
            }

            ctx.beginPath(); ctx.moveTo(ecgX === 0 ? 0 : ecgX - 2, ecgX === 0 ? targetY : ctx.lastY || targetY);
            ctx.lineTo(ecgX, targetY); ctx.strokeStyle = '#2ecc71'; ctx.lineWidth = 2.5; ctx.stroke();
            ctx.lastY = targetY; ecgX += 2; if (ecgX >= canvas.width) ecgX = 0;
        }
        frame++; drawNurse(); requestAnimationFrame(drawECG);
    }
    requestAnimationFrame(drawECG);

    window.actionMonitor = function() {
        if(isMonitorOn) return; isMonitorOn = true;
        let btn = document.getElementById("btn-monitor"); btn.classList.add("secured"); btn.innerText = "🖥️ モニター装着済";
        document.getElementById("monitor-text").style.display = "none"; setNurseMessage("モニター装着しました！波形を確認できます！", "roger", 4);
    }

    window.actionIV = function() {
        if(isIvSecured) return; isIvSecured = true;
        let btn = document.getElementById("btn-iv"); btn.classList.add("secured"); btn.innerText = "💉 ルート確保済";
        document.getElementById("iv-pole").style.display = "block"; 
        setNurseMessage("静脈ルート確保しました！いつでも薬剤入ります！", "roger", 4);
    }

    window.actionCPR = function() {
        if(!hasStarted) { startGame(); cycleTime = 10; }
        isCPR = true; cprWrapper.classList.add("cpr-active"); 
        let action = ['roger', 'nod'][Math.floor(Math.random() * 2)]; setNurseMessage("胸骨圧迫、開始(再開)します！1、2、3、4...", action, 4);
    }

    window.actionCheck = function() {
        if(!hasStarted) { triggerError('notStarted'); return; }
        if(!isMonitorOn) { triggerError('noMonitor'); return; }
        if(isCPR) { if(cycleTime < 18) { triggerError('earlyCheck'); return; } } else { triggerError('checkWhileNotCPR'); return; }

        isCPR = false; cycleTime = 0; cprWrapper.classList.remove("cpr-active"); uiCycleTime.innerHTML = getCycleTimeStr(cycleTime);
        
        if(isShockable(rhythm)) {
            let rName = rhythm === "VF" ? "VF（心室細動）" : "VT（無脈性心室頻拍）";
            setNurseMessage(`波形は<span style='color:red;'>${rName}</span>です！ショック適応、準備指示と圧迫再開を！`, "thinking", 6);
            pendingShock = true; pendingShockTimer = 0;
        } else if(rhythm === "Asystole" || rhythm === "PEA") {
            let rName = rhythm === "PEA" ? "PEA（無脈性電気活動）" : "Asystole（心静止）";
            setNurseMessage(`波形は<span style='color:red;'>${rName}</span>です！ショック非適応（DC不要）です、直ちに圧迫再開と原因検索を！`, "thinking", 6);
            pendingShock = false; pendingShockTimer = 0;
        } else if(rhythm === "ROSC") { triggerROSC(); }
    }

    window.actionShock = function(joules) {
        showMenu('main');
        if(!hasStarted) { triggerError('notStarted'); return; }
        if(isShockable(rhythm)) { pendingShock = true; } else { triggerError('shockNotIndicated'); return; }
        
        shockCount++; pendingShock = false; pendingShockTimer = 0;
        if(shockCount === 2) timeAtSecondShock = totalTime; 
        lastShockTime = totalTime; lastShockJoules = joules; updateActionTimers();
        
        shockEffect.style.display = "block"; setTimeout(() => { shockEffect.style.display = "none"; }, 300);
        
        if(isShockable(rhythm) && shockCount >= 4 && amioCount >= 1) { rhythm = "ROSC"; setTimeout(triggerROSC, 2500); } 
        setNurseMessage(`${joules}Jで充電...クリア！ショック実施しました！<br><span style='color:red;'>直ちに「胸骨圧迫」を再開してください！</span>`, getRandomHappyState(), 6);
    }

    window.actionDrug = function(drug, dose) {
        showMenu('main');
        if(!hasStarted) { triggerError('notStarted'); return; }
        if(!isIvSecured) { triggerError('noIV'); return; }
        
        if(drug === 'Adrenaline') {
            if(isShockable(rhythm) && shockCount < 2) { triggerError('earlyAdr'); return; }
            adrCount++; lastAdrTime = totalTime; lastAdrDose = dose; updateActionTimers();
            
            if(adrCount === 1) {
                document.getElementById('btn-exam').style.display = 'block'; document.getElementById('btn-test').style.display = 'block';
                setNurseMessage(`アドレナリン${dose}静注しました！${getRandomPraise()}<br>※身体所見と検査の評価が可能です！`, getRandomHappyState(), 7);
            } else { setNurseMessage(`アドレナリン${dose}静注しました！${getRandomPraise()}`, getRandomHappyState(), 5); }
            
            if((rhythm === "PEA" || rhythm === "Asystole") && causeTreated) { setTimeout(() => { if(rhythm === "PEA" || rhythm === "Asystole") rhythm = "ROSC"; }, 5000); }
        } else if(drug === 'Amiodarone') {
            if(rhythm === "Asystole" || rhythm === "PEA" || (isShockable(rhythm) && shockCount < 3)) { triggerError('wrongAmio'); return; }
            amioCount++; setNurseMessage(`アミオダロン${dose}静注しました！${getRandomPraise()}`, getRandomHappyState(), 5);
            if(isShockable(rhythm) && shockCount >= 3) { setTimeout(() => { if(isShockable(rhythm)) rhythm = "ROSC"; }, 6000); }
        } else if(drug === 'Lidocaine') {
            setNurseMessage(`リドカイン${dose}静注しました！${getRandomPraise()}`, getRandomHappyState(), 5);
        }
    }

    window.actionPhysicalExam = function() {
        if(!hasStarted) { triggerError('notStarted'); return; }
        if((rhythm === "PEA" || rhythm === "Asystole") && !causeTreated) {
            if(peaCause === "Hypoxia") setNurseMessage("【身体所見】SpO2測定不能です！口唇チアノーゼを認めます！", "thinking", 7);
            else if(peaCause === "Hypovolemia") setNurseMessage("【身体所見】骨盤骨折が疑われます！皮膚は蒼白で冷感があります！", "thinking", 7);
            else if(peaCause === "TensionPneumothorax") setNurseMessage("【身体所見】右の呼吸音が減弱し、頸静脈が怒張しています！", "thinking", 7);
            else if(peaCause === "CardiacTamponade") setNurseMessage("【身体所見】頸静脈が怒張し、心音が遠いです！", "thinking", 7);
            else if(peaCause === "Hyperkalemia") setNurseMessage("【身体所見】左腕に透析シャントを認めます！", "thinking", 7);
        } else { setNurseMessage("【身体所見】現在、特記すべき明らかな異常所見は確認できません！", "idle", 5); }
    }

    window.actionSimpleTests = function() {
        if(!hasStarted) { triggerError('notStarted'); return; }
        if((rhythm === "PEA" || rhythm === "Asystole") && !causeTreated) {
            if(peaCause === "Hypoxia") setNurseMessage("【簡単な検査】血ガスで著明な低酸素（PaO2 40mmHg）です！", "thinking", 7);
            else if(peaCause === "Hypovolemia") setNurseMessage("【簡単な検査】エコーで下大静脈（IVC）が虚脱し、腹腔内に出血を認めます！", "thinking", 7);
            else if(peaCause === "TensionPneumothorax") setNurseMessage("【簡単な検査】エコーで右肺のLung slidingが消失しています！", "thinking", 7);
            else if(peaCause === "CardiacTamponade") setNurseMessage("【簡単な検査】エコーで明らかな心嚢液の貯留と右室虚脱を認めます！", "thinking", 7);
            else if(peaCause === "Hyperkalemia") setNurseMessage("【簡単な検査】血ガスでカリウム（K）7.5 mEq/Lと著明な高値です！", "thinking", 7);
        } else { setNurseMessage("【簡単な検査】エコーや簡易検査で、特記すべき明らかな異常所見は確認できません！", "idle", 5); }
    }

    window.actionDiagnose = function(diag) {
        showMenu('main');
        if(!hasStarted) { triggerError('notStarted'); return; }
        if((rhythm !== "PEA" && rhythm !== "Asystole") || causeTreated) { triggerError('wrongDiag'); return; }
        if(diag === peaCause) {
            causeTreated = true;
            let diagName = {"Hypoxia":"低酸素血症", "Hypovolemia":"循環血液量減少", "TensionPneumothorax":"緊張性気胸", "CardiacTamponade":"心タンポナーデ", "Hyperkalemia":"高カリウム血症"}[diag];
            setNurseMessage(`「${diagName}」ですね！${getRandomGreatPraise()}<br><span style='color:red;'>引き続きCPRとアドレナリンを！</span>`, getRandomHappyState(), 7);
            if(adrCount >= 1) { setTimeout(() => { if(rhythm === "PEA" || rhythm === "Asystole") rhythm = "ROSC"; }, 5000); }
        } else { triggerError('wrongDiag'); }
    }

    window.actionAirway = function() {
        if(!hasStarted) { triggerError('notStarted'); return; }
        let action = ['roger', 'nod'][Math.floor(Math.random() * 2)];
        setNurseMessage("挿管準備します！胸骨圧迫は中断せずに進めます！カプノメータも準備します。", action, 5);
    }
</script>
</body>
</html>
"""
components.html(html_code, height=750)