import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="ICLS Quiz", page_icon="📝", layout="wide")
st.markdown("<h1 style='font-size: 32px; margin-bottom: 0px;'>📝 ICLS マニアック・クイズアタック</h1>", unsafe_allow_html=True)
st.markdown("<p style='font-size: 16px; color: #555;'>累積正解数(XP)を引き継ぎ、ナースが10段階の姿へ進化します！間違えた問題は次回優先出題！</p>", unsafe_allow_html=True)

html_code = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
    body { margin: 0; background: #2c3e50; font-family: 'Helvetica Neue', Arial, sans-serif; color: #fff; user-select: none; -webkit-user-select: none; overflow: hidden; }
    #game-container { display: flex; flex-direction: column; height: 100vh; max-width: 800px; margin: 0 auto; background: #1a252f; border: 2px solid #34495e; box-sizing: border-box; position: relative; }
    
    #header-area { display: flex; justify-content: space-between; align-items: center; padding: 10px 15px; background: #000; border-bottom: 2px solid #7f8c8d; font-size: 16px; font-weight: bold; }
    #lives { color: #e74c3c; letter-spacing: 2px; }
    #score-box { color: #f1c40f; }
    #xp-box { color: #3498db; margin-left: 10px; font-size: 14px; background: rgba(52,152,219,0.2); padding: 2px 6px; border-radius: 4px; }
    .reset-btn { background: #34495e; color: #bdc3c7; border: 1px solid #7f8c8d; border-radius: 4px; font-size: 10px; padding: 2px 5px; cursor: pointer; }
    .reset-btn:hover { background: #e74c3c; color: white; border-color: #c0392b; }
    
    #nurse-area { display: flex; padding: 15px; background: #ecf0f1; align-items: center; min-height: 120px; position: relative; z-index: 10; overflow: hidden; }
    #nurseCanvas { width: 120px; height: 150px; margin-top: -30px; margin-left: -10px; margin-right: 5px; flex-shrink: 0; filter: drop-shadow(0px 4px 4px rgba(0,0,0,0.3)); }
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
        <div style="font-size: 60px; margin-bottom: 10px;">🧬</div>
        <div class="overlay-title">ICLS 限界突破クイズ</div>
        <div class="overlay-desc">間違えた問題は次回優先して出題される「弱点克服アルゴリズム」搭載。<br>累積正解数(XP)でナースちゃんが<b>10段階の奇想天外な進化</b>を遂げます！<br><span style="color:#e74c3c; font-weight:bold;">※不正解または時間切れで経験値ロスト、Lv.0の新人からやり直しです。</span></div>
        <button class="start-btn" onclick="initGame()">テストを開始する</button>
    </div>

    <div id="header-area">
        <div>LIFE: <span id="lives">❤️❤️❤️</span></div>
        <button class="reset-btn" onclick="clearMemory()">学習履歴＆XPリセット</button>
        <div>SCORE: <span id="score-box">0</span> <span id="xp-box">0 XP (Lv.0)</span></div>
    </div>
    
    <div id="nurse-area">
        <canvas id="nurseCanvas" width="120" height="150"></canvas>
        <div id="nurse-message-container">
            <div id="nurse-msg" class="nurse-bubble-item">先生、私を究極の姿へ導いてください！間違えたら許しません！💢</div>
        </div>
    </div>
    
    <div id="quiz-area">
        <div id="question-panel">
            <div id="q-number">QUESTION 1 / 10</div>
            <div id="question-text">読み込み中...</div>
            <div id="timer-wrapper"><div id="timer-bar"></div></div>
        </div>
        
        <div id="options-grid"></div>
        
        <div id="next-btn-container">
            <button id="next-btn" onclick="nextQuestion()">次の問題へ ➔</button>
        </div>
    </div>
</div>

<script>
    const sourceQuestions = [
        { id: 1, q: "アミオダロン（アンカロン）初回300mgの静注時、推奨される希釈液と液量は？", options: ["5%ブドウ糖液 20mL", "生理食塩水 20mL", "5%ブドウ糖液 100mL", "希釈せず原液のまま"], ans: 0, exp: "アミオダロンは生理食塩水で希釈すると結晶化して白濁する恐れがあるため、必ず「5%ブドウ糖液」で希釈します。急速静注のため液量は20mL程度とします。" },
        { id: 2, q: "高度な気道確保（気管挿管やi-gelなど）が完了した後の、胸骨圧迫と換気のタイミングは？", options: ["非同期で、換気は6秒に1回", "非同期で、換気は3秒に1回", "圧迫30回に対し換気2回", "圧迫15回に対し換気2回"], ans: 0, exp: "高度な気道確保後は圧迫の手を止めず（非同期）、換気は10回/分（6秒に1回）のペースで行います。過換気は静脈還流を減少させるため厳禁です。" },
        { id: 3, q: "リズムチェックで胸骨圧迫を中断する際、許容される最大の中断時間は？", options: ["10秒以内", "5秒以内", "15秒以内", "20秒以内"], ans: 0, exp: "胸骨圧迫の中断は「いかなる場合も10秒以内」が鉄則です。長く止まるほど脳や心筋への血流が途絶え、自己心拍再開率が低下します。" },
        { id: 4, q: "PEA/Asystoleの可逆的な原因「4H4T」に含まれないのはどれ？", options: ["高カルシウム血症", "循環血液量減少", "緊張性気胸", "心タンポナーデ"], ans: 0, exp: "4H4Tの「H」は、Hypoxia(低酸素), Hypovolemia(循環血漿量減少), Hypo/Hyperkalemia(低/高カリウム等), Hydrogen ion(アシドーシス), Hypothermia(低体温)です。カルシウムは含まれません。" },
        { id: 5, q: "リドカインをVF/pVTに対して初回投与する場合の適切な用量は？", options: ["1.0〜1.5 mg/kg", "0.5〜0.75 mg/kg", "3.0 mg/kg", "300 mg"], ans: 0, exp: "リドカインの初回投与量は「1.0〜1.5 mg/kg」です。アミオダロン（300mg固定）と違い、体重換算である点に注意が必要です。" },
        { id: 6, q: "成人の質の高いCPRにおいて、胸骨圧迫の深さとテンポのガイドライン推奨は？", options: ["深さ5cm以上(6cm未満)、テンポ100〜120回/分", "深さ5cm以上、テンポ80〜100回/分", "深さ少なくとも5cm、上限なし", "深さ4cm以上、テンポ100〜120回/分"], ans: 0, exp: "深さは「少なくとも5cm（ただし6cmを超えない）」、テンポは「100〜120回/分」です。早すぎても深すぎても質が低下します。" },
        { id: 7, q: "アドレナリン1mg静注後、薬剤を中心静脈に早く到達させるために行うべき「後押し（フラッシュ）」の適切な方法は？", options: ["生食20mLを静注し、下肢または腕を挙上する", "生食10mLを静注するのみ", "5%ブドウ糖液20mLを静注する", "特に後押しは必要ない"], ans: 0, exp: "末梢静脈から投与した薬剤を心臓へ素早く送るため、投与直後に「20mLの生理食塩水」で後押しし、その腕（または下肢）を10〜20秒高く挙上します。" },
        { id: 8, q: "呼気終末二酸化炭素分圧（PETCO2）モニタリング中。ROSC（自己心拍再開）を示唆する急激な上昇の目安となる値は？", options: ["35〜40 mmHg以上", "10〜15 mmHg以上", "20〜25 mmHg以上", "50〜60 mmHg以上"], ans: 0, exp: "ROSCすると肺血流が劇的に再開するため、PETCO2が急激に上昇し「35〜40 mmHg以上」の正常値付近を示すことがROSCの強力な指標となります。" },
        { id: 9, q: "アミオダロンの追加投与（2回目）の適切な用量は？", options: ["150 mg", "300 mg", "1.5 mg/kg", "1.0 mg/kg"], ans: 0, exp: "初回は300mgですが、2回目（第5回ショック後）の追加投与量は「半量の150mg」です。これ以降の追加は推奨されておらず極量となります。" },
        { id: 10, q: "心タンポナーデや緊張性気胸の迅速な原因検索に最も有用とされるベッドサイドの検査は？", options: ["超音波検査（POCUS）", "胸部X線ポータブル", "12誘導心電図", "血液ガス分析"], ans: 0, exp: "PEAの原因検索において、超音波検査（POCUS）は心嚢液貯留や肺スライディングの消失を数秒で確認できる最強のツールです。" },
        { id: 11, q: "マグネシウム静注が特異的に推奨される、VF/pVTの特殊な病態はどれ？", options: ["Torsades de pointes (多形性心室頻拍)", "心筋梗塞に伴う単形性VT", "Brugada症候群", "WPW症候群"], ans: 0, exp: "QT延長に伴う多形性心室頻拍（Torsades de pointes: TdP）に対しては、硫酸マグネシウム1〜2gの静注が推奨されます。" },
        { id: 12, q: "静脈路(IV)や骨髄路(IO)が確保できず、気管内投与でアドレナリンを投与する場合の推奨用量は？", options: ["静注量の2〜2.5倍 (2〜2.5mg)", "静注量と同じ (1mg)", "静注量の5倍 (5mg)", "気管内投与は現在推奨されていない"], ans: 0, exp: "気管内投与は吸収が不安定なため、静脈内投与量の2〜2.5倍（2〜2.5mg）を生理食塩水で5〜10mLに希釈して投与します。" },
        { id: 13, q: "心停止中の炭酸水素ナトリウム（メイロン）投与が「適応となる」代表的な病態はどれ？", options: ["高カリウム血症や三環系抗うつ薬中毒", "すべての長時間の心停止", "呼吸性アシドーシス", "低カルシウム血症"], ans: 0, exp: "ルーチンのメイロン投与は推奨されませんが、既存の代謝性アシドーシス、高カリウム血症、三環系抗うつ薬中毒などの特殊な状況下では適応となります。" },
        { id: 14, q: "チームダイナミクスにおいて、指示を受けた者がその内容を復唱し、完了後に報告するコミュニケーション手法は？", options: ["クローズドループ・コミュニケーション", "SBAR", "ステップバック", "フィードフォワード"], ans: 0, exp: "指示の誤解を防ぎ、確実な実行を担保するための「クローズドループ・コミュニケーション」は蘇生チームにおいて極めて重要です。" },
        { id: 15, q: "質の高いCPRを維持するため、胸骨圧迫の交代を行う推奨タイミングは？", options: ["2分ごと（または疲労時）", "3分ごと", "アドレナリン投与ごと", "5サイクル（約1分）ごと"], ans: 0, exp: "圧迫の質は時間とともに低下するため、「2分ごと（リズムチェックのタイミング）」に、中断を5秒未満に抑えつつ交代することが推奨されます。" },
        { id: 16, q: "PEAの鑑別中、波形とは別に「脈拍の有無」を確認する際、触知すべき推奨部位は？", options: ["頸動脈または大腿動脈", "橈骨動脈", "上腕動脈", "足背動脈"], ans: 0, exp: "心拍出量が低下している状態でも触知しやすい中枢側の動脈（頸動脈または大腿動脈）を、10秒以内で確認します。" },
        { id: 17, q: "妊婦の心停止において、子宮による下大静脈圧迫を解除するために行うべき体位調整は？", options: ["用手的子宮左方移動 (LUD)", "トレンデレンブルグ体位", "右側臥位", "頭部挙上"], ans: 0, exp: "妊娠後半の妊婦では、増大した子宮が下大静脈を圧迫し静脈還流を妨げる（仰臥位低血圧症候群）ため、用手的に子宮を左側へずらすLUD（Left Uterine Displacement）を行います。" },
        { id: 18, q: "重症の高カリウム血症によるPEAが強く疑われる場合、即効性のある「心筋保護」を目的として投与する薬剤は？", options: ["グルコン酸カルシウム（カルチコール）", "インスリン＋ブドウ糖（GI療法）", "ポリスチレンスルホン酸ナトリウム", "フロセミド（ラシックス）"], ans: 0, exp: "高K血症による致死性不整脈の予防・治療として、細胞膜の閾値電位を変化させ心筋を安定化させるカルシウム製剤（カルチコール等）を最優先で投与します。" },
        { id: 19, q: "VF/pVTに対する二相性除細動器を用いた初回ショックのエネルギー量として推奨されるのは？", options: ["製造業者の推奨値（通常120〜200J）", "一律360J", "50J", "体重(kg) × 2J"], ans: 0, exp: "二相性除細動器の初回エネルギーは、その機種の製造業者の推奨値（通常120〜200J）を用います。推奨値が不明な場合は最大エネルギーを用います。" },
        { id: 20, q: "質の高い胸骨圧迫が行われているかを評価する際、最低限維持すべきPETCO2の目安は？", options: ["10 mmHg以上", "5 mmHg以上", "35 mmHg以上", "50 mmHg以上"], ans: 0, exp: "PETCO2が10mmHg未満の場合は心拍出量（胸骨圧迫の質）が不十分であることを示唆するため、圧迫の深さやテンポ、術者の疲労を改善する必要があります。" },
        { id: 21, q: "ROSC後、12誘導心電図でST上昇を認めた。次に行うべき最も優先される対応は？", options: ["冠動脈造影（緊急カテーテル）の検討", "直ちにアミオダロンの持続静注", "アドレナリンの持続静注", "大動脈バルーンパンピング（IABP）"], ans: 0, exp: "ROSC後のST上昇型心筋梗塞（STEMI）は心停止の直接原因であることが多いため、可及的速やかな冠動脈造影および再灌流療法が推奨されます。" },
        { id: 22, q: "波形がVT（心室頻拍）だが、患者には意識があり、橈骨動脈も触知可能である。次に行うべき対応は？", options: ["専門医へコールしカルディオバージョン等を検討", "直ちに胸骨圧迫を開始", "直ちに最大ジュールで除細動", "アドレナリン1mgを静注"], ans: 0, exp: "意識があり脈が触れる場合は「無脈性(pulseless)VT」ではなく「有脈性VT」です。ICLSのアルゴリズムから外れ、専門的な頻脈アルゴリズムの対応となります。" }
    ];

    let gameQuestions = [];
    let currentQIndex = 0;
    let score = 0;
    let life = 3;
    let timer = 15;
    let timerInterval = null;
    let isAnswered = false;
    
    // 🌟 永続経験値(XP)システム
    let totalXP = parseInt(localStorage.getItem('iclsTotalXP')) || 0;
    let nurseLevel = 0;

    function calcLevel(xp) {
        if (xp >= 100) return 10;
        if (xp >= 70) return 9;
        if (xp >= 50) return 8;
        if (xp >= 40) return 7;
        if (xp >= 30) return 6;
        if (xp >= 20) return 5;
        if (xp >= 15) return 4;
        if (xp >= 10) return 3;
        if (xp >= 6) return 2;
        if (xp >= 3) return 1;
        return 0;
    }
    
    // 🌟 形態ごとの名前
    function getLevelName(lvl) {
        const names = ["新人", "中堅ブルー", "ハードヒッター", "真田の赤備え", "ICLSの忍び", "メカ・ナース", "ネフロン魔法少女", "超・覚醒", "病棟の千手観音", "ギャラクシー", "ICLSの女神"];
        return names[lvl];
    }
    
    // 🌟 形態ごとの待機(アイドル)ランダムコメント (各4種類)
    function getFormIdleMsg(lvl) {
        let msgs = [];
        if (lvl === 0) {
            msgs = [
                "先生、制限時間は15秒です！的確な指示を！",
                "3回間違えると即ゲームオーバーです！慎重に！",
                "過去に間違えた問題は優先して出題されますよ！",
                "まずは落ち着いて。時間はまだあります！"
            ];
        } else if (lvl === 1) {
            msgs = [
                "先生、制限時間は15秒です。焦らずいきましょう。",
                "私の青いオーラ、見えますか？冷静な判断を。",
                "アルゴリズムは完璧ですか？次、来ますよ。",
                "無駄な動きは減らして。最短で指示を！"
            ];
        } else if (lvl === 2) {
            msgs = [
                "さあ来い！どんな問題でも強烈に打ち返します！",
                "制限時間は15秒！私のスピンに遅れないで！",
                "エースを狙うチャンスです！的確な指示を！",
                "フットワーク軽く！次々と裁いていきましょう！"
            ];
        } else if (lvl === 3) {
            msgs = [
                "先生、采配を！我ら赤備え、遅れはとりません！",
                "制限時間15秒！戦場での迷いは命取りですぞ！",
                "六文銭の誓い…いざ、決戦の刻！",
                "この赤き鎧、伊達ではありません！さあ、次へ！"
            ];
        } else if (lvl === 4) {
            msgs = [
                "……（気配を消している。制限時間は15秒）",
                "先生、指示を。誰にも気付かれず遂行します。",
                "忍法、迅速蘇生の術……さあ、次の問題を。",
                "影からサポートします。油断なきよう。"
            ];
        } else if (lvl === 5) {
            msgs = [
                "タイマー起動。制限時間15.00秒。論理的判断を。",
                "システム・オールグリーン。次の解析へ移行します。",
                "感情パラメーターをオフ。アルゴリズムに全振りします。",
                "先生の脳波、安定しています。指示をどうぞ。"
            ];
        } else if (lvl === 6) {
            msgs = [
                "魔法のステッキで、カリウムも浄化しちゃいますよ☆",
                "制限時間は15秒！魔法の時間は限られてるんです！",
                "先生、一緒に奇跡を起こしましょう！エイッ☆",
                "メロメロにさせちゃう前に、早く指示を出してね！"
            ];
        } else if (lvl === 7) {
            msgs = [
                "俺の闘気が見えねぇのか…？早く指示を出せ！",
                "15秒なんて、俺には止まって見えるぜ…！",
                "限界を超えろ、先生！宇宙の果てまで付き合うぜ！",
                "雷鳴の如く！一瞬で答えを導き出せ！"
            ];
        } else if (lvl === 8) {
            msgs = [
                "無数の腕が、先生の指示をお待ちしております。",
                "制限時間は15秒。すべて同時並行で処理しますよ。",
                "慈悲の心と千の腕。さあ、救済の時間です。",
                "どんな手技も一瞬で。次の指示をどうぞ。"
            ];
        } else if (lvl === 9) {
            msgs = [
                "宇宙の真理…ガイドラインの深淵に触れる時間です。",
                "時間は相対的なもの…しかし、この空間では15秒です。",
                "星々の囁きが、正しい答えを教えてくれるはずです。",
                "先生の知識は、銀河の如く広がっていますね。"
            ];
        } else {
            msgs = [
                "私の光に導かれなさい…。究極の救済を。",
                "神の領域で、先生の判断を拝見いたします。",
                "すべての命を繋ぐため…さあ、正しき道へ。",
                "もう恐れることはありません。あなたの直感を信じて。"
            ];
        }
        return msgs[Math.floor(Math.random() * msgs.length)];
    }
    
    function getFormCorrectMsg(lvl) {
        if (lvl === 0) return "正解です！👏 この調子で！";
        if (lvl === 1) return "完璧な判断です。👏";
        if (lvl === 2) return "クリーンショット！👏";
        if (lvl === 3) return "見事な采配！👏";
        if (lvl === 4) return "お見事、先生！👏";
        if (lvl === 5) return "正解。論理的です。👏";
        if (lvl === 6) return "電解質、浄化完了！👏";
        if (lvl === 7) return "バチバチきてんな！👏";
        if (lvl === 8) return "慈悲の正解！👏";
        if (lvl === 9) return "真理に一歩近づきました。👏";
        if (lvl === 10) return "神罰回避。👏";
        return "正解です。";
    }
    
    function getFormEvolutionMsg(lvl) {
        const special = ["", "", "", "【上田の魂】", "【隠密蘇生】", "【解析完了】", "【電解質浄化】", "【限界突破】", "【病棟無双】", "【真理悟得】", "【究極救済】"];
        return `<br><span style='color:#f1c40f;font-weight:bold;font-size:16px;'>✨${special[lvl]}【Lv.${lvl} ${getLevelName(lvl)}】に進化しました！✨</span>`;
    }
    
    function getFormIncorrectMsg(lvl) {
        if (lvl === 0) return "違います！アルゴリズムを思い出して！💢 (経験値全ロスト・新人に戻ります)";
        if (lvl === 1) return "違います、先生。冷静に！💢 (新人に戻ります)";
        if (lvl === 2) return "アウト！💢 (新人に戻ります)";
        if (lvl === 3) return "采配ミス！💢 (新人に戻ります)";
        if (lvl === 4) return "敵袭！💢 (新人に戻ります)";
        if (lvl === 5) return "エラー。論理破綻。💢 (新人に戻ります)";
        if (lvl === 6) return "違います！メロメロ💢 (新人に戻ります)";
        if (lvl === 7) return "バカな…！💢 (新人に戻ります)";
        if (lvl === 8) return "煩脳！💢 (新人に戻ります)";
        if (lvl === 9) return "真理から遠ざかりました。💢 (新人に戻ります)";
        if (lvl === 10) return "神罰。💢 (新人に戻ります)";
        return "違います。";
    }
    
    function getFormTimeoutMsg(lvl) {
        if (lvl === 0) return "時間切れ！判断が遅い！💢 (経験値全ロスト・新人に戻ります)";
        if (lvl === 1) return "時間切れ、先生。💢 (新人に戻ります)";
        if (lvl === 2) return "タイムオーバー！💢 (新人に戻ります)";
        if (lvl === 3) return "遅すぎた采配！💢 (新人に戻ります)";
        if (lvl === 4) return "時間が…！💢 (新人に戻ります)";
        if (lvl === 5) return "タイムアウト。💢 (新人に戻ります)";
        if (lvl === 6) return "時間が…メロ💢 (新人に戻ります)";
        if (lvl === 7) return "俺は…ここまでか…💢 (新人に戻ります)";
        if (lvl === 8) return "時間が足らん！💢 (新人に戻ります)";
        if (lvl === 9) return "時間が止まった…？💢 (新人に戻ります)";
        if (lvl === 10) return "神罰。💢 (新人に戻ります)";
        return "時間切れ。";
    }
    
    function getFormClearMsg(lvl) {
        if (lvl === 10) return "先生、究極の救済を成し遂げました！✨";
        return "先生、完璧です！✨ このまま究極の姿を目指しましょう！";
    }
    
    function getFormGameOverMsg(lvl) {
        if (lvl === 0) return "先生、しっかり復習してください。間違えたら即リセットですよ。";
        if (lvl === 10) return "先生…女神の領域からは遠ざかりました。💢";
        return "先生…次は神の領域へ。間違えないでください。";
    }

    function getWrongIds() { try { return JSON.parse(localStorage.getItem('iclsWrongQs')) || []; } catch(e) { return []; } }
    function saveWrongIds(ids) { try { localStorage.setItem('iclsWrongQs', JSON.stringify(ids)); } catch(e) {} }
    window.clearMemory = function() { 
        try { localStorage.removeItem('iclsWrongQs'); localStorage.removeItem('iclsTotalXP'); location.reload(); } 
        catch(e) { location.reload(); } 
    }

    const canvas = document.getElementById("ecgCanvas");
    let frame = 0;
    let nurseState = 'idle';

    // 🌟 究極進化した10段階ナースちゃんの描画関数
    function drawNurse() {
        const nCanvas = document.getElementById("nurseCanvas");
        if(!nCanvas) return;
        const nCtx = nCanvas.getContext("2d");
        nCtx.clearRect(0, 0, 120, 150); nCtx.save(); 
        nCtx.translate(60, 90); // 中心座標

        let bounce = 0;
        if (nurseState === 'idle') bounce = Math.sin(frame * 0.08) * 2;
        else if (nurseState === 'happy' || nurseState === 'cracker') bounce = Math.abs(Math.sin(frame * 0.3)) * -6; 
        else if (nurseState === 'ok_circle') bounce = Math.abs(Math.sin(frame * 0.2)) * -5; 
        else if (nurseState === 'sparkle' || nurseState === 'heart') bounce = Math.sin(frame * 0.1) * 2; 
        else if (nurseState === 'angry') nCtx.translate((Math.random()-0.5)*3, (Math.random()-0.5)*3);
        else if (nurseState === 'thinking') bounce = Math.sin(frame * 0.05) * 1; 
        else if (nurseState === 'shock') bounce = Math.random() * 4 - 2;

        nCtx.translate(0, bounce);

        // 🎨 形態ごとのカラーパレット
        let uniColor = "#ffffff"; let hairColor = "#8e44ad"; let skinColor = "#ffdbac"; let armColor = skinColor;
        if (nurseLevel === 1) uniColor = "#3498db";
        if (nurseLevel === 2) uniColor = "#f1c40f";
        if (nurseLevel === 3) uniColor = "#c0392b";
        if (nurseLevel === 4) { uniColor = "#111"; hairColor = "#222"; } // 忍び
        if (nurseLevel === 5) { uniColor = "#95a5a6"; armColor = "#bdc3c7"; } // メカ
        if (nurseLevel === 6) { uniColor = "#ff9ff3"; hairColor = "#fd79a8"; } // 魔法少女
        if (nurseLevel === 7) { uniColor = "#e67e22"; hairColor = "#f1c40f"; } // 超覚醒
        if (nurseLevel === 8) { uniColor = "#d35400"; } // 千手観音
        if (nurseLevel === 9) { uniColor = "#192a56"; hairColor = "#273c75"; skinColor = "#7f8fa6"; armColor = skinColor; } // 宇宙
        if (nurseLevel === 10) { uniColor = "#ffffff"; hairColor = "#ffffff"; } // 女神

        // 🌌 背面の装飾 (オーラ、翼、千手など)
        nCtx.save();
        if (nurseLevel >= 1 && nurseLevel <= 6) {
            let glow = Math.abs(Math.sin(frame * 0.1)) * 5;
            let auraC = ["", "rgba(52,152,219,0.3)", "rgba(241,196,15,0.4)", "rgba(192,57,43,0.4)", "rgba(0,0,0,0.5)", "rgba(0,255,255,0.3)", "rgba(253,121,168,0.4)"][nurseLevel];
            if (nurseLevel === 5) auraC = "rgba(0,255,255,0.2)"; // メカオーラ
            nCtx.fillStyle = auraC; nCtx.beginPath(); nCtx.arc(0, -10, 35 + glow, 0, Math.PI*2); nCtx.fill();
        }
        if (nurseLevel === 4) { // 忍びマフラー
            nCtx.fillStyle = "#e74c3c"; 
            let mufX = 15 + Math.sin(frame*0.2)*5;
            nCtx.beginPath(); nCtx.moveTo(10, -15); nCtx.lineTo(mufX+15, -20); nCtx.lineTo(mufX+10, -5); nCtx.fill();
        }
        if (nurseLevel === 7) { // 超覚醒 闘気と雷
            nCtx.fillStyle = "rgba(241,196,15,0.5)";
            nCtx.beginPath(); nCtx.ellipse(0, -10, 40+Math.random()*5, 50+Math.random()*10, 0, 0, Math.PI*2); nCtx.fill();
            if(Math.random()>0.7) { nCtx.strokeStyle="#fff"; nCtx.lineWidth=2; nCtx.beginPath(); nCtx.moveTo(-20+(Math.random()-0.5)*40, -40); nCtx.lineTo(-10+(Math.random()-0.5)*20, 10); nCtx.stroke(); }
        }
        if (nurseLevel === 8) { // 千手観音 (背後の腕と後光)
            nCtx.strokeStyle = "#f1c40f"; nCtx.lineWidth = 3;
            nCtx.beginPath(); nCtx.arc(0, -15, 35, 0, Math.PI*2); nCtx.stroke();
            nCtx.fillStyle = skinColor;
            nCtx.save(); nCtx.rotate(Math.PI/6); nCtx.fillRect(-35, -5, 70, 4); nCtx.restore();
            nCtx.save(); nCtx.rotate(-Math.PI/6); nCtx.fillRect(-35, -5, 70, 4); nCtx.restore();
            nCtx.fillRect(-35, -15, 70, 4);
        }
        if (nurseLevel === 9) { // ギャラクシー
            nCtx.fillStyle = "rgba(41,128,185,0.5)"; nCtx.beginPath(); nCtx.arc(0, -10, 45, 0, Math.PI*2); nCtx.fill();
            nCtx.fillStyle = "#fff";
            for(let i=0; i<10; i++) { nCtx.fillRect((Math.random()-0.5)*80, -50+Math.random()*80, 2, 2); }
        }
        if (nurseLevel === 10) { // 女神の黄金翼と後光
            let glow = Math.abs(Math.sin(frame * 0.05)) * 10;
            nCtx.fillStyle = "rgba(255,255,255,0.8)"; nCtx.beginPath(); nCtx.arc(0, -10, 50 + glow, 0, Math.PI*2); nCtx.fill();
            nCtx.fillStyle = "rgba(241,196,15,0.6)";
            nCtx.beginPath(); nCtx.ellipse(-25, -10, 15, 35, -Math.PI/4, 0, Math.PI*2); nCtx.fill(); // 左翼
            nCtx.beginPath(); nCtx.ellipse(25, -10, 15, 35, Math.PI/4, 0, Math.PI*2); nCtx.fill(); // 右翼
        }
        nCtx.restore();

        // 頭部・髪
        if (nurseLevel === 7) { // 超覚醒の逆立つ髪
            nCtx.fillStyle = hairColor;
            nCtx.beginPath(); nCtx.moveTo(-16, -10); nCtx.lineTo(-25, -40); nCtx.lineTo(-10, -25); nCtx.lineTo(0, -50); nCtx.lineTo(10, -25); nCtx.lineTo(25, -40); nCtx.lineTo(16, -10); nCtx.fill();
        } else {
            nCtx.fillStyle = hairColor; nCtx.beginPath(); nCtx.arc(0, -10, 16, 0, Math.PI*2); nCtx.fill();
        }
        
        nCtx.fillStyle = skinColor; nCtx.beginPath(); nCtx.arc(0, -12, 14, 0, Math.PI*2); nCtx.fill();
        nCtx.lineWidth = 1.5; nCtx.strokeStyle = "#2c3e50"; nCtx.fillStyle = "#2c3e50";
        
        // 額の装備
        if (nurseLevel === 2) { nCtx.fillStyle = "#2c3e50"; nCtx.fillRect(-12, -26, 24, 6); nCtx.fillStyle = "#f1c40f"; nCtx.fillRect(-8, -26, 16, 6); }
        if (nurseLevel === 3) { nCtx.fillStyle = "#c0392b"; nCtx.fillRect(-14, -28, 28, 8); nCtx.fillStyle = "#f1c40f"; for(let i=0; i<3; i++) { nCtx.beginPath(); nCtx.arc(-6+i*6, -26, 2, 0, Math.PI*2); nCtx.fill(); nCtx.beginPath(); nCtx.arc(-6+i*6, -22, 2, 0, Math.PI*2); nCtx.fill(); } }
        if (nurseLevel === 10) { nCtx.fillStyle = "#f1c40f"; nCtx.beginPath(); nCtx.moveTo(-10, -20); nCtx.lineTo(-15, -35); nCtx.lineTo(-5, -25); nCtx.lineTo(0, -40); nCtx.lineTo(5, -25); nCtx.lineTo(15, -35); nCtx.lineTo(10, -20); nCtx.fill(); } // 王冠

        // 🌟 メカ・ナース(Lv.5)の頭部ディテール追加
        if (nurseLevel === 5) {
            // アンテナ
            nCtx.strokeStyle = "#7f8c8d"; nCtx.lineWidth = 2;
            nCtx.beginPath(); nCtx.moveTo(-10, -25); nCtx.lineTo(-15, -45); nCtx.stroke();
            nCtx.fillStyle = "#e74c3c"; nCtx.beginPath(); nCtx.arc(-15, -45, 3, 0, Math.PI*2); nCtx.fill();
            // メカ眼帯
            nCtx.fillStyle = "#00ffff"; nCtx.fillRect(1, -16, 6, 6);
        }

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

        // ボディ
        nCtx.fillStyle = uniColor; nCtx.fillRect(-14, 2, 28, 22);
        
        // 🌟 メカ・ナース(Lv.5)のボディディテール追加
        if (nurseLevel === 5) {
            // パネルライン
            nCtx.strokeStyle = "#7f8c8d"; nCtx.lineWidth = 1;
            nCtx.beginPath(); nCtx.moveTo(-14, 10); nCtx.lineTo(14, 10); nCtx.stroke();
            nCtx.beginPath(); nCtx.moveTo(0, 2); nCtx.lineTo(0, 22); nCtx.stroke();
            // LED
            let ledF = Math.sin(frame*0.5);
            nCtx.fillStyle = ledF > 0 ? "#2ecc71" : "#1e8449"; nCtx.beginPath(); nCtx.arc(-7, 7, 2, 0, Math.PI*2); nCtx.fill();
            nCtx.fillStyle = ledF > 0.5 ? "#e74c3c" : "#922b21"; nCtx.beginPath(); nCtx.arc(-7, 13, 2, 0, Math.PI*2); nCtx.fill();
            nCtx.fillStyle = ledF < -0.5 ? "#3498db" : "#1f618d"; nCtx.beginPath(); nCtx.arc(-7, 19, 2, 0, Math.PI*2); nCtx.fill();
        }
        
        else if (nurseLevel === 2) { nCtx.fillStyle = "#2c3e50"; nCtx.fillRect(-14, 10, 28, 3); nCtx.fillRect(-14, 16, 28, 3); }
        else if (nurseLevel === 3) { nCtx.strokeStyle = "#f1c40f"; nCtx.lineWidth = 1; nCtx.strokeRect(-12, 4, 24, 18); nCtx.beginPath(); nCtx.moveTo(-12, 10); nCtx.lineTo(12, 10); nCtx.stroke(); nCtx.beginPath(); nCtx.moveTo(-12, 16); nCtx.lineTo(12, 16); nCtx.stroke(); }
        else if (nurseLevel === 6) { nCtx.fillStyle = "#e74c3c"; nCtx.beginPath(); nCtx.moveTo(0, 5); nCtx.lineTo(-8, -2); nCtx.lineTo(-8, 10); nCtx.fill(); nCtx.beginPath(); nCtx.moveTo(0, 5); nCtx.lineTo(8, -2); nCtx.lineTo(8, 10); nCtx.fill(); } // 胸リボン
        
        // 腕とアクション
        nCtx.fillStyle = armColor; nCtx.strokeStyle = "#ffffff";
        
        if (nurseState === 'happy') {
            nCtx.fillRect(-22, -15, 5, 20); nCtx.fillRect(17, -15, 5, 20); 
            // メカ腕関節
            if(nurseLevel===5) { nCtx.fillStyle="#7f8c8d"; nCtx.fillRect(-22, -5, 5, 2); nCtx.fillRect(17, -5, 5, 2); nCtx.fillStyle=armColor; }
        } else if (nurseState === 'cracker') {
            nCtx.fillRect(13, -25, 5, 20); nCtx.fillRect(-18, 4, 5, 10);
            if(nurseLevel===5) { nCtx.fillStyle="#7f8c8d"; nCtx.fillRect(13, -15, 5, 2); nCtx.fillRect(-18, 9, 5, 2); nCtx.fillStyle=armColor; }
            nCtx.fillStyle = "#e67e22"; nCtx.beginPath(); nCtx.moveTo(15, -25); nCtx.lineTo(5, -35); nCtx.lineTo(25, -35); nCtx.fill();
            let pOffset = (frame % 20); let colors = ["#e74c3c", "#3498db", "#2ecc71", "#f1c40f"];
            for(let i=0; i<6; i++) { nCtx.fillStyle = colors[i%4]; nCtx.fillRect(15 + (i-3)*8, -45 - pOffset - (i%3)*5, 3, 3); }
        } else if (nurseState === 'ok_circle') {
            nCtx.strokeStyle = armColor; nCtx.lineWidth = 5;
            nCtx.beginPath(); nCtx.arc(0, -28, 18, Math.PI, 0); nCtx.stroke(); nCtx.lineWidth = 1.5;
        } else if (nurseState === 'heart' || nurseState === 'sparkle') {
            nCtx.fillRect(-18, 4, 5, 14); nCtx.fillRect(13, 4, 5, 14); 
            if(nurseLevel===5) { nCtx.fillStyle="#7f8c8d"; nCtx.fillRect(-18, 11, 5, 2); nCtx.fillRect(13, 11, 5, 2); nCtx.fillStyle=armColor; }
            if(nurseState === 'heart') {
                let hY = -45 + Math.sin(frame*0.2)*3; nCtx.fillStyle = "#e74c3c";
                nCtx.beginPath(); nCtx.arc(-4, hY, 4, 0, Math.PI*2); nCtx.fill(); nCtx.beginPath(); nCtx.arc(4, hY, 4, 0, Math.PI*2); nCtx.fill();
                nCtx.beginPath(); nCtx.moveTo(-8, hY); nCtx.lineTo(8, hY); nCtx.lineTo(0, hY+7); nCtx.fill();
            }
        } else if (nurseState === 'thinking') {
            nCtx.fillRect(-18, 4, 5, 12); nCtx.fillRect(6, -6, 12, 5); 
            if(nurseLevel===5) { nCtx.fillStyle="#7f8c8d"; nCtx.fillRect(-18, 10, 5, 2); nCtx.fillStyle=armColor; }
        } else if (nurseState === 'angry' || nurseState === 'shock') {
            nCtx.fillRect(-15, 8, 15, 5); nCtx.fillRect(0, 8, 15, 5); 
            if(nurseLevel===5) { nCtx.fillStyle="#7f8c8d"; nCtx.fillRect(-7.5, 8, 2, 5); nCtx.fillRect(7.5, 8, 2, 5); nCtx.fillStyle=armColor; }
        } else {
            nCtx.fillRect(-18, 4, 5, 14); nCtx.fillRect(13, 4, 5, 14); 
            if(nurseLevel===5) { nCtx.fillStyle="#7f8c8d"; nCtx.fillRect(-18, 11, 5, 2); nCtx.fillRect(13, 11, 5, 2); nCtx.fillStyle=armColor; }
        }

        // 手持ちアイテム (前面)
        if (nurseLevel === 2) { // 黄金ラケット (ピュアアエロ風)
            nCtx.save(); nCtx.translate(15, 5); nCtx.rotate(Math.PI/4);
            nCtx.strokeStyle = "#2c3e50"; nCtx.lineWidth = 3; nCtx.beginPath(); nCtx.moveTo(0, 0); nCtx.lineTo(0, -15); nCtx.stroke();
            nCtx.strokeStyle = "#f1c40f"; nCtx.lineWidth = 3; nCtx.beginPath(); nCtx.arc(0, -25, 10, 0, Math.PI*2); nCtx.stroke();
            nCtx.strokeStyle = "rgba(255,255,255,0.6)"; nCtx.lineWidth = 1;
            nCtx.beginPath(); nCtx.moveTo(-8, -25); nCtx.lineTo(8, -25); nCtx.stroke(); nCtx.beginPath(); nCtx.moveTo(0, -33); nCtx.lineTo(0, -17); nCtx.stroke();
            nCtx.restore();
        } else if (nurseLevel === 3) { // 采配
            nCtx.save(); nCtx.translate(15, 5); nCtx.rotate(Math.PI/6);
            nCtx.fillStyle = "#2c3e50"; nCtx.fillRect(-2, -10, 4, 15); nCtx.fillStyle = "#f1c40f"; nCtx.fillRect(-3, -12, 6, 4);
            nCtx.fillStyle = "#fff"; let flutter = Math.sin(frame*0.3)*5;
            nCtx.beginPath(); nCtx.moveTo(-2, -12); nCtx.lineTo(-10+flutter, -30); nCtx.lineTo(10+flutter, -28); nCtx.fill();
            nCtx.restore();
        } else if (nurseLevel === 6) { // 魔法ステッキ (腎小体モチーフ)
            nCtx.save(); nCtx.translate(15, 5); nCtx.rotate(Math.PI/5);
            nCtx.fillStyle = "#e74c3c"; nCtx.fillRect(-2, -15, 4, 20);
            nCtx.fillStyle = "#f1c40f"; nCtx.beginPath(); nCtx.arc(0, -20, 8, 0, Math.PI*2); nCtx.fill();
            nCtx.fillStyle = "#3498db"; nCtx.beginPath(); nCtx.arc(0, -20, 4, 0, Math.PI*2); nCtx.fill();
            nCtx.restore();
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

    function shuffleArray(array) {
        let curId = array.length;
        while (0 !== curId) {
            let randId = Math.floor(Math.random() * curId); curId -= 1;
            let tmp = array[curId]; array[curId] = array[randId]; array[randId] = tmp;
        }
        return array;
    }

    window.initGame = function() {
        document.getElementById("overlay").style.display = "none";
        
        nurseLevel = calcLevel(totalXP);
        updateXpUI();
        
        let wrongIds = getWrongIds();
        let pool = [...sourceQuestions];
        
        let wrongQs = pool.filter(q => wrongIds.includes(q.id));
        let normalQs = pool.filter(q => !wrongIds.includes(q.id));
        
        wrongQs = shuffleArray(wrongQs);
        normalQs = shuffleArray(normalQs);
        
        let selected = wrongQs.slice(0, 10);
        if (selected.length < 10) selected = selected.concat(normalQs.slice(0, 10 - selected.length));
        gameQuestions = shuffleArray(selected); 
        
        currentQIndex = 0; score = 0; life = 3;
        updateLifeUI();
        document.getElementById("score-box").innerText = score;
        loadQuestion();
    }

    function updateXpUI() {
        nurseLevel = calcLevel(totalXP);
        document.getElementById("xp-box").innerText = `${totalXP} XP (Lv.${nurseLevel}: ${getLevelName(nurseLevel)})`;
    }

    function loadQuestion() {
        isAnswered = false;
        document.getElementById("next-btn-container").style.display = "none";
        
        let qData = gameQuestions[currentQIndex];
        let wrongIds = getWrongIds();
        let isReview = wrongIds.includes(qData.id) ? "<span style='color:#e74c3c; margin-left:8px;'>⚠️ 復習問題</span>" : "";
        
        document.getElementById("q-number").innerHTML = `QUESTION ${currentQIndex + 1} / 10 ${isReview}`;
        document.getElementById("question-text").innerHTML = qData.q;
        
        let ops = qData.options.map((opt, idx) => ({ text: opt, isCorrect: idx === qData.ans }));
        ops = shuffleArray(ops);
        
        let grid = document.getElementById("options-grid");
        grid.innerHTML = "";
        ops.forEach((o, i) => {
            let btn = document.createElement("button");
            btn.className = "option-btn";
            btn.innerHTML = `<span style="display:inline-block; width:24px; height:24px; background:#1a252f; border-radius:50%; text-align:center; line-height:24px; margin-right:10px;">${['A','B','C','D'][i]}</span> ${o.text}`;
            btn.onclick = () => checkAnswer(o.isCorrect, btn, ops, qData.id);
            grid.appendChild(btn);
        });

        // 🌟 形態ごとの待機(ランダム)コメント
        updateNurseMsg(getFormIdleMsg(nurseLevel), "idle");
        startTimer(qData.id);
    }

    function startTimer(qId) {
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
                timeOut(qId);
            }
        }, 1000);
    }

    function checkAnswer(isCorrect, selectedBtn, allOps, qId) {
        if(isAnswered) return;
        isAnswered = true;
        clearInterval(timerInterval);
        
        let btns = document.getElementById("options-grid").children;
        for(let i=0; i<btns.length; i++) {
            btns[i].disabled = true;
            if(allOps[i].isCorrect) btns[i].classList.add("correct");
        }

        let qData = gameQuestions[currentQIndex];
        let wrongIds = getWrongIds();
        
        if(isCorrect) {
            score += 10 + timer;
            document.getElementById("score-box").innerText = score;
            
            let oldLevel = nurseLevel;
            totalXP++;
            localStorage.setItem('iclsTotalXP', totalXP);
            updateXpUI();
            
            let levelUpMsg = "";
            if (nurseLevel > oldLevel) {
                levelUpMsg = getFormEvolutionMsg(nurseLevel);
            }
            
            wrongIds = wrongIds.filter(id => id !== qId);
            saveWrongIds(wrongIds);
            
            let goodStates = ['happy', 'cracker', 'ok_circle', 'heart'];
            updateNurseMsg(`<span style='color:#2ecc71; font-size:16px;'>${getFormCorrectMsg(nurseLevel)}</span>${levelUpMsg}<br>${qData.exp}`, goodStates[Math.floor(Math.random()*goodStates.length)]);
        } else {
            selectedBtn.classList.add("incorrect");
            loseLife();
            
            let oldLevel = nurseLevel;
            // 🌟 鬼畜仕様：間違えたらXP（経験値）とレベルをゼロに強制リセット
            totalXP = 0;
            localStorage.setItem('iclsTotalXP', totalXP);
            updateXpUI(); // ここで内部のLvが0に戻る
            
            if(!wrongIds.includes(qId)) { wrongIds.push(qId); saveWrongIds(wrongIds); }
            
            // 🌟 進化していた形態の断末魔コメントを表示
            updateNurseMsg(`<span style='color:#e74c3c; font-size:16px;'>${getFormIncorrectMsg(oldLevel)}</span><br>${qData.exp}`, "angry");
        }
        
        if(life > 0) document.getElementById("next-btn-container").style.display = "block";
    }

    function timeOut(qId) {
        if(isAnswered) return;
        isAnswered = true;
        
        let btns = document.getElementById("options-grid").children;
        for(let i=0; i<btns.length; i++) btns[i].disabled = true;
        
        let wrongIds = getWrongIds();
        if(!wrongIds.includes(qId)) { wrongIds.push(qId); saveWrongIds(wrongIds); }
        
        loseLife();
        
        let oldLevel = nurseLevel;
        // 🌟 鬼畜仕様：時間切れでもXP（経験値）とレベルをゼロに強制リセット
        totalXP = 0;
        localStorage.setItem('iclsTotalXP', totalXP);
        updateXpUI(); // ここで内部のLvが0に戻る
        
        let qData = gameQuestions[currentQIndex];
        // 🌟 進化していた形態の断末魔コメントを表示
        updateNurseMsg(`<span style='color:#e74c3c; font-size:16px;'>${getFormTimeoutMsg(oldLevel)}</span><br>${qData.exp}`, "shock");
        
        if(life > 0) document.getElementById("next-btn-container").style.display = "block";
    }

    function loseLife() {
        life--; updateLifeUI();
        if(life <= 0) setTimeout(showGameOver, 2500);
    }

    function updateLifeUI() {
        let lStr = "";
        for(let i=0; i<3; i++) { lStr += (i < life) ? "❤️" : "🖤"; }
        document.getElementById("lives").innerText = lStr;
    }

    window.nextQuestion = function() {
        currentQIndex++;
        if(currentQIndex >= 10) showClear(); 
        else loadQuestion();
    }

    function showGameOver() {
        let ov = document.getElementById("overlay");
        ov.innerHTML = `
            <div style="font-size: 60px; margin-bottom: 10px;">💔</div>
            <div class="overlay-title" style="color:#e74c3c;">救命失敗...</div>
            <div class="overlay-desc">知識の欠如が現場の崩壊を招きました。<br>間違えた問題は次回優先して出題されます。</div>
            <div class="overlay-score">SCORE: ${score} 点</div>
            <button class="start-btn" onclick="location.reload()">弱点を復習する</button>
        `;
        ov.style.display = "flex";
        updateNurseMsg(getFormGameOverMsg(nurseLevel), "angry");
    }

    function showClear() {
        let ov = document.getElementById("overlay");
        let wrongIds = getWrongIds();
        let wrongMsg = wrongIds.length > 0 ? `<br><span style="color:#e74c3c; font-size:14px;">※まだ過去に間違えた「弱点問題」が ${wrongIds.length}問 残っています。</span>` : `<br><span style="color:#2ecc71; font-size:14px;">✨ 弱点リストはゼロです！完璧！ ✨</span>`;
        let rank = score >= 200 ? "👑 ICLSマニア (神)" : (score >= 150 ? "🏅 優秀なリーダー" : "🎖️ 合格ライン");
        ov.innerHTML = `
            <div style="font-size: 60px; margin-bottom: 10px;">🎉</div>
            <div class="overlay-title" style="color:#2ecc71;">全問クリア！！</div>
            <div class="overlay-desc" style="color:#f1c40f; font-size:20px; font-weight:bold;">称号: ${rank}${wrongMsg}</div>
            <div class="overlay-score">最終スコア: ${score} 点</div>
            <button class="start-btn" style="background:#3498db; box-shadow:0 4px #2980b9;" onclick="location.reload()">次の周回へ</button>
        `;
        ov.style.display = "flex";
        updateNurseMsg(getFormClearMsg(nurseLevel), "sparkle");
    }
</script>
</body>
</html>
"""
components.html(html_code, height=750)