import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="ナースダッシュ！", page_icon="💉", layout="wide")

# 🌟 st.markdownを使ってタイトルとサブタイトルの文字サイズを最適化
st.markdown(
    "<h1 style='font-size: 32px; margin-bottom: 0px;'>🏃‍♀️ ナースダッシュ！ 救命クイズラン V17</h1>", 
    unsafe_allow_html=True
)
st.markdown(
    "<p style='font-size: 24px; color: #555;'>信州上田医療センターを救え！</p>", 
    unsafe_allow_html=True
)

html_code = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
    body { 
        margin: 0; background: #f0f2f6; display: flex; flex-direction: column; align-items: center; 
        font-family: 'Helvetica Neue', Arial, sans-serif; overflow: hidden; 
        overscroll-behavior: none; touch-action: none; 
        -webkit-user-select: none; -moz-user-select: none; -ms-user-select: none; user-select: none;
    }
    
    #game-container { position: relative; width: 100%; max-width: 700px; aspect-ratio: 7 / 5; background: #87CEEB; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
    canvas { width: 100%; height: 100%; display: block; }
    
    #quiz-overlay { display: none; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: #f0f2f6; z-index: 30; box-sizing: border-box; padding: 10px; }
    
    #quiz-box { width: 100%; height: 100%; display: flex; flex-direction: column; justify-content: space-between; }
    
    .quiz-title { color: #e74c3c; font-size: 18px; font-weight: bold; text-align: center; flex-shrink: 0; margin-bottom: 5px; }
    
    .quiz-text { 
        background: #fff; padding: 10px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        font-size: 14px; color: #2c3e50; font-weight: bold; line-height: 1.4; 
        flex-grow: 1; overflow-y: auto; margin-bottom: 8px;
    }
    
    .quiz-btn-container { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; flex-shrink: 0; }
    
    .quiz-btn { 
        background: #3498db; color: white; border: none; border-radius: 6px; 
        padding: 6px; font-size: 13px; font-weight: bold; cursor: pointer; transition: 0.1s;
        min-height: 48px; display: flex; align-items: center; justify-content: center; text-align: center; line-height: 1.2;
    }
    .quiz-btn:active { background: #2980b9; transform: scale(0.95); }
    .game-over-btn { background: #e74c3c; grid-column: 1 / -1; min-height: 45px; } 
    .game-over-btn:active { background: #c0392b; }

    /* 🌟 文字をピカピカ点滅させるアニメーション（誤爆防止用演出） */
    @keyframes blink { 
        from { opacity: 0.3; transform: scale(0.98); } 
        to { opacity: 1; transform: scale(1.02); } 
    }
</style>
</head>
<body>
<div id="game-container">
    <canvas id="gameCanvas" width="700" height="500"></canvas>
    <div id="quiz-overlay"><div id="quiz-box"></div></div>
</div>

<script>
    const canvas = document.getElementById("gameCanvas");
    const ctx = canvas.getContext("2d");
    const overlay = document.getElementById("quiz-overlay");
    const quizBox = document.getElementById("quiz-box");

    let isPaused = false; let isGameClear = false; let isGameOver = false; 
    let frameCount = 0; let score = 0; let baseScrollSpeed = 4.5;
    const BOSS_SPAWN_FRAME = 18000; let boss = null;

    let bgScrollCloud = 0; let bgScrollMountain = 0; let bgScrollCity = 0;

    let player = { 
        x: 100, y: 300, size: 40, vy: 0, gravity: 0.6, jumpPower: -10.5, 
        isGrounded: false, invincible: 0, jumpCount: 0, maxJumps: 2, isHurt: 0,
        lives: 3, maxLives: 5 
    };

    let obstacles = []; let questionBlocks = []; let coins = []; let gems = []; let hearts = []; let effects = [];
    let gameMessage = { text: "🏥 勤務スタート！", subtext: "安全第一で進みましょう", life: 120, color: "#fff" };
    const groundY = 430; 

    const phaseConfigs = [
        { name: "☀️ 日勤帯", sky: "#87CEEB", mtn: "#546de5", city: "#2d3436", gnd: "#8B4513", grass: "#228B22" }, 
        { name: "🌇 午後勤帯", sky: "#ff9f43", mtn: "#ee5253", city: "#222f3e", gnd: "#833471", grass: "#006266" }, 
        { name: "🌙 夜勤入り", sky: "#2c3e50", mtn: "#34495e", city: "#111111", gnd: "#3b2a2a", grass: "#192a56" }, 
        { name: "🚑 救急搬送", sky: "#8e44ad", mtn: "#9b59b6", city: "#2c3e50", gnd: "#2d3436", grass: "#1e272e" }, 
        { name: "🚨 深夜の急変", sky: "#c0392b", mtn: "#e74c3c", city: "#2d3436", gnd: "#2c3e50", grass: "#b33939" }, 
        { name: "☣️ 謎の感染源", sky: "#1abc9c", mtn: "#16a085", city: "#111111", gnd: "#273c75", grass: "#192a56" }, 
        { name: "🏥 カオス病棟", sky: "#f39c12", mtn: "#d35400", city: "#2c3e50", gnd: "#8B4513", grass: "#e1b12c" }, 
        { name: "🌪️ 嵐の予感", sky: "#00a8ff", mtn: "#0097e6", city: "#2f3640", gnd: "#718093", grass: "#353b48" }, 
        { name: "🔥 ボスの前兆", sky: "#e84118", mtn: "#c23616", city: "#192a56", gnd: "#2f3640", grass: "#ff4757" }, 
        { name: "👹 総力戦", sky: "#2f3542", mtn: "#57606f", city: "#000000", gnd: "#2f3542", grass: "#ff4757" }  
    ];

    const nurseQuizzes = [
        { q: "透析アミロイドーシスで、骨や関節に沈着する原因物質はどれ？", options: ["β2-ミクログロブリン", "尿酸結晶", "シュウ酸カルシウム", "怨念"], ans: "β2-ミクログロブリン" },
        { q: "シャントトラブル。「スリルが消失し、拍動のみ触知する」場合に疑うのは？", options: ["シャント狭窄・閉塞", "シャント感染", "静脈高血圧", "恋の鼓動"], ans: "シャント狭窄・閉塞" },
        { q: "慢性腎不全（CKD）の進行に伴い、血液データで【低下】しやすいのはどれ？", options: ["カルシウム（Ca）", "リン（P）", "カリウム（K）", "モチベーション"], ans: "カルシウム（Ca）" },
        { q: "透析中の不均衡症候群で、最もよく見られる初期症状は？", options: ["頭痛・悪心・嘔吐", "全身の激しい痒み", "胸痛と呼吸困難", "謎の万能感"], ans: "頭痛・悪心・嘔吐" },
        { q: "腎不全患者における「腎性貧血」の最も主要な原因はどれ？", options: ["エリスロポエチンの分泌低下", "鉄分の摂取不足", "消化管からの慢性出血", "毎日のため息"], ans: "エリスロポエチンの分泌低下" },
        { q: "シャント肢（シャントを作った腕）の日常ケアとして【適切】なのはどれ？", options: ["毎日シャント音やスリルを確認", "血圧測定はシャント肢で行う", "重い荷物はシャント肢で持つ", "気合で毎日腕立て伏せをする"], ans: "毎日シャント音やスリルを確認" },
        { q: "慢性腎臓病(CKD)の重症度分類（Gステージ）は何の数値で分類される？", options: ["eGFR", "血清クレアチニン", "尿タンパク量", "戦闘力（スカウター）"], ans: "eGFR" },
        { q: "透析患者のリンコントロールで、リン吸着薬を内服する最も適切なタイミングは？", options: ["食直後", "食前30分", "就寝前", "全集中の呼吸で"], ans: "食直後" },
        { q: "二次性副甲状腺機能亢進症で過剰に分泌されるホルモンは？", options: ["PTH（副甲状腺ホルモン）", "インスリン", "コルチゾール", "覇王色の覇気"], ans: "PTH（副甲状腺ホルモン）" },
        { q: "透析患者の体重増加制限。中2日空く場合の適切な目安（DWに対する割合）は？", options: ["3〜5%", "10〜15%", "制限なし", "精神と時の部屋"], ans: "3〜5%" },
        { q: "エリスロポエチン製剤（ESA）は何を改善するために投与される？", options: ["腎性貧血", "骨粗鬆症", "糖尿病", "通信速度"], ans: "腎性貧血" },
        { q: "透析患者の頑固なかゆみ（そう痒症）の主な原因となるのはどれ？", options: ["高リン血症", "低カリウム血症", "低血圧", "妖怪のしわざ"], ans: "高リン血症" },
        { q: "正常な腎臓の糸球体でろ過されない（尿に出ない）成分はどれ？", options: ["タンパク質", "水分", "ナトリウム", "忖度（そんたく）"], ans: "タンパク質" },
        { q: "透析導入の原因疾患として、現在日本で最も多いのはどれ？", options: ["糖尿病性腎症", "慢性糸球体腎炎", "腎硬化症", "ガチャの爆死"], ans: "糖尿病性腎症" },
        { q: "心不全やCKDで使われる薬「MRA」の正式な略称は？", options: ["ミネラルコルチコイド受容体拮抗薬", "磁気共鳴血管画像", "メッセンジャーRNA", "マジで・リアルに・危ない"], ans: "ミネラルコルチコイド受容体拮抗薬" },
        { q: "急性心筋梗塞を疑う患者が到着。救急カート準備の次に優先される検査は？", options: ["12誘導心電図", "頭部CT", "腹部エコー", "院長への丸投げ"], ans: "12誘導心電図" },
        { q: "心電図で「心房細動（Af）」に最も特徴的な所見はどれ？", options: ["f波の出現とRR間隔の絶対的不整", "規則正しい鋸歯状波（F波）", "デルタ波の出現", "画面のバグ"], ans: "f波の出現とRR間隔の絶対的不整" },
        { q: "うっ血性心不全の患者でよく見られる、姿勢による呼吸状態の特徴は？", options: ["起座呼吸（横になると苦しい）", "クスマウル呼吸", "チェーンストークス呼吸", "全集中の呼吸"], ans: "起座呼吸（横になると苦しい）" },
        { q: "狭心症発作時に「舌下投与」される、血管拡張作用のあるお薬といえば？", options: ["ニトログリセリン", "アセトアミノフェン", "ロキソプロフェン", "フリスク"], ans: "ニトログリセリン" },
        { q: "狭心症と心筋梗塞を鑑別する上で、最も特異度が高い心筋マーカーは？", options: ["トロポニンT", "CRP", "AST（GOT）", "女の勘"], ans: "トロポニンT" },
        { q: "心電図のP波は何を表している？", options: ["心房の脱分極（興奮）", "心室の脱分極", "心室の再分極", "領域展開のサイン"], ans: "心房の脱分極（興奮）" },
        { q: "大動脈解離の典型的な初期症状はどれ？", options: ["突然の引き裂かれるような背部痛・胸痛", "徐々に増悪する鈍痛", "右下腹部の限局した痛み", "いつでしょ！？今でしょ！？"], ans: "突然の引き裂かれるような背部痛・胸痛" },
        { q: "ジギタリス製剤の副作用（ジギタリス中毒）で見られる症状はどれ？", options: ["悪心・嘔吐・不整脈", "高血圧", "多尿", "倍返しだ！と叫びたくなる"], ans: "悪心・嘔吐・不整脈" },
        { q: "急性心不全の治療で使われる「NPPV」とは何のこと？", options: ["非侵襲的陽圧換気療法", "経皮的冠動脈インターベンション", "大動脈内バルーンパンピング", "NiziUの新しいPV"], ans: "非侵襲的陽圧換気療法" },
        { q: "下肢深部静脈血栓症（DVT）の予防策として適切なのはどれ？", options: ["早期離床と弾性ストッキングの着用", "長時間のベッド上安静", "水分摂取の制限", "ペッパーミル"], ans: "早期離床と弾性ストッキングの着用" },
        { q: "心停止の波形で、AED（除細動）の適応となるのはどれ？", options: ["心室細動（VF）", "心静止（Asystole）", "無脈性電気活動（PEA）", "心の乱れ"], ans: "心室細動（VF）" },
        { q: "大動脈弁狭窄症（AS）の代表的な3徴候に含まれるのはどれ？", options: ["失神", "下痢", "視力低下", "圧倒的カリスマ性"], ans: "失神" },
        { q: "心電図で「ST上昇」がみられた場合、最も強く疑う疾患は？", options: ["急性心筋梗塞", "洞不全症候群", "肺塞栓症", "スタンド攻撃"], ans: "急性心筋梗塞" },
        { q: "循環器薬の「ループ利尿薬」を内服している患者で特に注意すべき電解質異常は？", options: ["低カリウム血症", "高カルシウム血症", "高ナトリウム血症", "承認欲求"], ans: "低カリウム血症" },
        { q: "心不全の増悪指標となる体重増加。一般的に注意すべき変化量は？", options: ["1週間で2kg以上の増加", "1ヶ月で500gの増加", "半年で1kgの増加", "幸せ太り"], ans: "1週間で2kg以上の増加" },
        { q: "意識障害の鑑別「AIUEOTIPS」の『I』が示す原因はどれ？", options: ["Infection（感染症）", "Iron Deficiency（鉄欠乏）", "Infectious Endocarditis（感染性心内膜炎）", "Ikemen（イケメン直視）"], ans: "Infection（感染症）" },
        { q: "急性動脈閉塞症などで見られる「5P徴候」に【含まれる】のはどれ？", options: ["Pallor（蒼白）", "Palpitation（動悸）", "Polyuria（多尿）", "Passion（情熱）"], ans: "Pallor（蒼白）" },
        { q: "JCS（ジャパン・コーマ・スケール）で「痛み刺激で開眼する」のはどれ？", options: ["JCS II-20", "JCS I-2", "JCS III-100", "奇跡の目覚め"], ans: "JCS II-20" },
        { q: "BLS（一次救命処置）における胸骨圧迫の適切なテンポは？", options: ["1分間に100〜120回", "1分間に60〜80回", "1分間に150回以上", "盆踊りのリズム"], ans: "1分間に100〜120回" },
        { q: "アナフィラキシー疑いの患者。気道浮腫を示唆する最も危険な聴診音は？", options: ["ストライダー（吸気性喘鳴）", "コースクラックル（水泡音）", "ウィーズ（呼気性喘鳴）", "謎の鼻歌"], ans: "ストライダー（吸気性喘鳴）" },
        { q: "糖尿病患者が冷や汗、手の震え、異常な空腹感を訴えた。まず疑うべきは？", options: ["低血糖", "高血糖緊急症", "脱水症", "恋の病"], ans: "低血糖" },
        { q: "成人の心肺蘇生における胸骨圧迫の深さの目安は？", options: ["約5cm", "約2cm", "約10cm", "地球の裏側まで届くくらい"], ans: "約5cm" },
        { q: "窒息時の異物除去法として背部叩打法とともに推奨されるのは？", options: ["腹部突き上げ法（ハイムリック法）", "指で無理やりかき出す", "水を大量に飲ませる", "かめはめ波を撃つ"], ans: "腹部突き上げ法（ハイムリック法）" },
        { q: "頭部外傷後の「ルシッド・インターバル（清明期）」が見られる疾患は？", options: ["急性硬膜外血腫", "くも膜下出血", "脳挫傷", "異世界転生"], ans: "急性硬膜外血腫" },
        { q: "瞳孔の対光反射で、光を当てても瞳孔が縮まない状態を何という？", options: ["対光反射消失", "縮瞳", "眼振", "邪気眼"], ans: "対光反射消失" },
        { q: "くも膜下出血の典型的な症状はどれ？", options: ["バットで殴られたような突然の激しい頭痛", "徐々に強くなる後頭部の痛み", "目の奥の鈍痛", "考えるのをやめた"], ans: "バットで殴られたような突然の激しい頭痛" },
        { q: "喀血（かっけつ）と吐血（とけつ）の鑑別。喀血の特徴はどれ？", options: ["泡沫状で鮮紅色", "暗赤色で食物残渣が混じる", "コーヒー残渣様", "鬼の血"], ans: "泡沫状で鮮紅色" },
        { q: "トリアージタグで「黄色（待機的治療）」が意味するのは？", options: ["バイタル安定だが入院や手術が必要", "直ちに命に関わる状態", "軽症で帰宅可能", "イエローカード"], ans: "バイタル安定だが入院や手術が必要" },
        { q: "脳卒中を疑う「FAST」の『S』が意味するのは？", options: ["Speech（言葉の障害）", "Smile（笑顔の消失）", "Sight（視力障害）", "スマイル0円"], ans: "Speech（言葉の障害）" },
        { q: "細胞内液に最も多く含まれている主要な陽イオンはどれ？", options: ["カリウム（K）", "ナトリウム（Na）", "カルシウム（Ca）", "気合"], ans: "カリウム（K）" },
        { q: "パルスオキシメーター（SpO2）が正確に測れない【原因となる】のはどれ？", options: ["末梢の冷え（血流低下）", "発熱", "高血圧", "患者のオーラ"], ans: "末梢の冷え（血流低下）" },
        { q: "ノロウイルスによる胃腸炎患者の吐物処理に有効な消毒薬は？", options: ["次亜塩素酸ナトリウム", "消毒用エタノール", "クロルヘキシジン", "ファブリーズ"], ans: "次亜塩素酸ナトリウム" },
        { q: "インスリンの「皮下注射」を行う際の適切な部位は？", options: ["上腕外側や腹部などの皮下脂肪が厚い部位", "前腕の筋肉内", "大腿部の静脈内", "眉間"], ans: "上腕外側や腹部などの皮下脂肪が厚い部位" },
        { q: "高齢者に多い「誤嚥性肺炎」の予防ケアとして適切なのは？", options: ["口腔ケアによる衛生保持", "食直後にすぐ仰臥位にする", "食事をすべて流動食にする", "ASMRを聞かせる"], ans: "口腔ケアによる衛生保持" },
        { q: "褥瘡（床ずれ）の予防で、体位変換の一般的な目安時間は？", options: ["2時間ごと", "12時間ごと", "1日1回", "果報は寝て待て"], ans: "2時間ごと" },
        { q: "患者誤認を防ぐための「フルネームの確認」として正しい方法は？", options: ["「お名前をフルネームで名乗っていただけますか？」", "「鈴木一郎さんですね？」", "部屋のネームプレートだけを見る", "「君の名は。」とエモく聞く"], ans: "「お名前をフルネームで名乗っていただけますか？」" },
        { q: "アナフィラキシーでアドレナリンを自己注射するキットの名前は？", options: ["エピペン", "インスリンペン", "サインペン", "どこでもドア"], ans: "エピペン" },
        { q: "胃ろう（PEG）からの経管栄養注入前、必ず確認すべき項目は？", options: ["胃残量の確認", "体重測定", "採血", "チャンネル登録と高評価"], ans: "胃残量の確認" },
        { q: "高齢者の転倒転落リスクを高めるお薬（ハイリスク薬）はどれ？", options: ["睡眠薬や抗不安薬", "ビタミン剤", "消化酵素薬", "プロテイン"], ans: "睡眠薬や抗不安薬" },
        { q: "麻薬性鎮痛薬（オピオイド）の代表的な副作用はどれ？", options: ["便秘・悪心・眠気", "頻尿", "難聴", "スーパーサイヤ人化"], ans: "便秘・悪心・眠気" },
        { q: "血液ガス分析で「PaCO2が上昇」している状態を何と呼ぶ？", options: ["呼吸性アシドーシス", "代謝性アシドーシス", "呼吸性アルカローシス", "オワコン"], ans: "呼吸性アシドーシス" },
        { q: "インフルエンザなどの主な感染経路はどれ？", options: ["飛沫感染", "空気感染", "血液媒介感染", "Bluetooth接続"], ans: "飛沫感染" }
    ];

    let availableQuizzes = [...nurseQuizzes];

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
                case 1: pool = [ {e: "👾", t: "normal", h: 30}, {e: "🦇", t: "wave", h: 100} ]; break;
                case 2: pool = [ {e: "👻", t: "chase", h: 100}, {e: "🦇", t: "wave", h: 80} ]; break;
                case 3: pool = [ {e: "🚑", t: "fast", h: 40}, {e: "🧟‍♂️", t: "normal", h: 40} ]; break;
                case 4: pool = [ {e: "💀", t: "waveAir", h: 120}, {e: "🦅", t: "fastAir", h: 150} ]; break;
                case 5: pool = [ {e: "💩", t: "normal", h: 30}, {e: "🦠", t: "chase", h: 80} ]; break;
                case 6: pool = [ {e: "🐉", t: "fast", h: 40}, {e: "🐍", t: "normal", h: 30} ]; break;
                case 7: pool = [ {e: "🌪️", t: "fastAir", h: 120}, {e: "👻", t: "chase", h: 90} ]; break;
                case 8: pool = [ {e: "🧟‍♂️", t: "fast", h: 40}, {e: "🚑", t: "fast", h: 40}, {e: "💀", t: "waveAir", h: 100} ]; break;
                default: pool = [ {e: "🧟‍♂️", t: "fast", h: 40}, {e: "👻", t: "chase", h: 120}, {e: "🦅", t: "fastAir", h: 160} ]; break;
            }
            let pick = pool[Math.floor(Math.random() * pool.length)];
            obstacles.push({ x: 800, y: groundY - pick.h, size: 30, emoji: pick.e, type: pick.t, baseY: groundY - pick.h, tick: 0 });
        }
        
        if (frameCount % 350 === 0) questionBlocks.push({ x: 800, y: groundY - 140, size: 40, emoji: "❓" });
        if (frameCount % 45 === 0 && Math.random() < 0.7) coins.push({ x: 800, y: groundY - 40 - Math.random() * 100, size: 25, emoji: "🪙" });
        if (frameCount % 180 === 0 && Math.random() < 0.7) gems.push({ x: 800, y: groundY - 200 - Math.random() * 80, size: 28, emoji: "💎" });
        if (frameCount % 450 === 0 && Math.random() < 0.5) hearts.push({ x: 800, y: groundY - 50 - Math.random() * 100, size: 28, emoji: "💖" });

        if (player.isGrounded && frameCount % 8 === 0) effects.push({ x: player.x, y: groundY - 10, text: "💨", life: 15, vx: -3, vy: -0.2 });
    }

    // 🌟 連打誤爆防止：クイズの表示ロジックを変更
    function triggerQuiz() {
        isPaused = true;
        if (availableQuizzes.length === 0) availableQuizzes = [...nurseQuizzes];
        let randIndex = Math.floor(Math.random() * availableQuizzes.length);
        let cq = availableQuizzes[randIndex];
        availableQuizzes.splice(randIndex, 1);

        let shuffled = [...cq.options].sort(() => 0.5 - Math.random());
        
        let html = `<div class="quiz-title">🚨 ナース・アセスメント</div>
                    <div class="quiz-text">${cq.q}</div>
                    
                    <!-- 🌟 演出：0.7秒間だけ「分析中...」と表示してボタンを隠す -->
                    <div id="quiz-loading" style="text-align: center; font-size: 18px; color: #e74c3c; font-weight: bold; margin: 15px 0; animation: blink 0.3s infinite alternate;">
                        💡 状況を分析中...
                    </div>
                    
                    <!-- 🌟 最初は display: none; で完全に隠しておく -->
                    <div class="quiz-btn-container" id="quiz-btn-container" style="display: none;">`;
                    
        shuffled.forEach(opt => { html += `<button class="quiz-btn" onclick="checkAnswer('${opt}', '${cq.ans}')">${opt}</button>`; });
        html += `</div>`;
        
        quizBox.innerHTML = html; 
        overlay.style.display = "block";

        // 🌟 0.7秒後にボタンを表示（この間はいくら画面を連打しても反応しない）
        setTimeout(() => {
            const loading = document.getElementById("quiz-loading");
            const btnContainer = document.getElementById("quiz-btn-container");
            if (loading && btnContainer) {
                loading.style.display = "none";
                btnContainer.style.display = "grid";
            }
        }, 700);
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
        isGameOver = true; isPaused = true;
        let title = ""; let comment = "";
        
        if (score < 3000) { title = "🐥 ひよっこナース"; comment = "まずは業務に慣れるところから！"; }
        else if (score < 8000) { title = "💉 中堅ナース"; comment = "落ち着いてアセスメントできています！"; }
        else if (score < 15000) { title = "🌟 ベテランナース"; comment = "素晴らしい反射神経と判断力！"; }
        else { title = "👑 ゴッドハンド・ナース"; comment = "もはや院内感染ボスの天敵です！"; }

        let html = `<div class="quiz-title" style="font-size:22px;">💀 勤務終了</div>
                    <div class="quiz-text" style="display:flex; flex-direction:column; justify-content:center; text-align:center;">
                        最終スコア：<span style="font-size:26px; color:#e74c3c; margin: 8px 0;">${score} 点</span>
                        <b>獲得称号：【${title}】</b><br>
                        <span style="font-size:14px; color:#555; margin-top:8px;">${comment}</span>
                    </div>
                    <div class="quiz-btn-container" style="grid-template-columns: 1fr;">
                        <button class="quiz-btn game-over-btn" onclick="location.reload()">もう一度シフトに入る</button>
                    </div>`;
        quizBox.innerHTML = html; overlay.style.display = "block";
    }

    function takeDamage() {
        if (player.invincible > 0 || player.isHurt > 0) return;
        player.lives--; player.invincible = 60; player.isHurt = 60;
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

        bgScrollCloud = (bgScrollCloud + 0.3) % 700; bgScrollMountain = (bgScrollMountain + 0.8) % 700; bgScrollCity = (bgScrollCity + 2.0) % 700;

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
            if (boss.x < -150) { boss.x = 800; let rageBonus = (4 - boss.hp) * 1.5; boss.speed = 2.5 + rageBonus + (Math.random() * 4.0); }
            let dist = Math.hypot((player.x + player.size/2) - (boss.x + boss.size/2), (player.y + player.size/2) - (boss.y + boss.size/2));
            if (dist < (player.size/2 + boss.size/2 - 15)) {
                if (player.invincible > 0 && player.isHurt === 0) { bossHit(); } 
                else if (player.vy > 0 && (player.y + player.size/2) < (boss.y + boss.size/2 - 10)) { player.vy = player.jumpPower * 1.3; player.jumpCount = 1; bossHit(); } 
                else { takeDamage(); }
            }
        }

        function bossHit() {
            boss.hp--;
            if (boss.hp <= 0) {
                score += 5000; effects.push({ x: boss.x, y: boss.y, text: "💥撃破!!💥", life: 100 });
                boss = null; isGameClear = true;
                gameMessage = { text: "🎊 完 全 治 癒 🎊", subtext: "5分間防衛成功！見事なアセスメントです！", life: 9999, color: "#f1c40f" };
            } else { score += 1000; effects.push({ x: boss.x, y: boss.y, text: "💢", life: 30 }); player.vy = player.jumpPower * 1.2; }
        }

        for (let i = obstacles.length - 1; i >= 0; i--) {
            let obs = obstacles[i];
            if (obs.type === 'slow') { obs.x -= currentScrollSpeed * 0.6; } 
            else if (obs.type === 'fast' || obs.type === 'fastAir') { obs.x -= currentScrollSpeed * 1.6; } 
            else if (obs.type === 'wave' || obs.type === 'waveAir') { obs.tick += 0.08; obs.y = obs.baseY + Math.sin(obs.tick) * 50; obs.x -= currentScrollSpeed; } 
            else if (obs.type === 'chase') { obs.y += (player.y - obs.y) * 0.02; obs.x -= currentScrollSpeed * 0.8; } 
            else { obs.x -= currentScrollSpeed; }
            
            let dist = Math.hypot((player.x + player.size/2) - (obs.x + obs.size/2), (player.y + player.size/2) - (obs.y + obs.size/2));
            if (dist < (player.size/2 + obs.size/2 - 5)) {
                if (player.invincible > 0 && player.isHurt === 0) {
                    obstacles.splice(i, 1); score += 100; effects.push({ x: obs.x, y: obs.y, text: "💥", life: 30 });
                } else if (player.invincible === 0) {
                    if (player.vy > 0 && (player.y + player.size/2) < (obs.y + obs.size/2)) {
                        obstacles.splice(i, 1); score += 200; player.vy = player.jumpPower * 0.8; player.jumpCount = 1; effects.push({ x: obs.x, y: obs.y, text: "👟ﾎﾟｲﾝ!", life: 30 });
                    } else { takeDamage(); if(isGameOver) break; }
                }
                continue;
            }
            if (obs.x < -50) obstacles.splice(i, 1);
        }

        for (let i = coins.length - 1; i >= 0; i--) {
            let c = coins[i]; c.x -= currentScrollSpeed; let dist = Math.hypot((player.x + player.size/2) - (c.x + c.size/2), (player.y + player.size/2) - (c.y + c.size/2));
            if (dist < (player.size/2 + c.size/2)) { score += 50; effects.push({ x: c.x, y: c.y, text: "✨", life: 20 }); coins.splice(i, 1); continue; }
            if (c.x < -50) coins.splice(i, 1);
        }

        for (let i = gems.length - 1; i >= 0; i--) {
            let g = gems[i]; g.x -= currentScrollSpeed; let dist = Math.hypot((player.x + player.size/2) - (g.x + g.size/2), (player.y + player.size/2) - (g.y + g.size/2));
            if (dist < (player.size/2 + g.size/2)) { score += 300; effects.push({ x: g.x, y: g.y, text: "💎+300!", life: 30 }); gems.splice(i, 1); continue; }
            if (g.x < -50) gems.splice(i, 1);
        }
        
        for (let i = hearts.length - 1; i >= 0; i--) {
            let h = hearts[i]; h.x -= currentScrollSpeed; let dist = Math.hypot((player.x + player.size/2) - (h.x + h.size/2), (player.y + player.size/2) - (h.y + h.size/2));
            if (dist < (player.size/2 + h.size/2)) { player.lives = Math.min(player.maxLives, player.lives + 1); effects.push({ x: h.x, y: h.y, text: "💖回復!", life: 30 }); hearts.splice(i, 1); continue; }
            if (h.x < -50) hearts.splice(i, 1);
        }

        for (let i = questionBlocks.length - 1; i >= 0; i--) {
            let qb = questionBlocks[i]; qb.x -= currentScrollSpeed; let dist = Math.hypot((player.x + player.size/2) - (qb.x + qb.size/2), (player.y + player.size/2) - (qb.y + qb.size/2));
            if (dist < (player.size/2 + qb.size/2)) { questionBlocks.splice(i, 1); triggerQuiz(); continue; }
            if (qb.x < -50) questionBlocks.splice(i, 1);
        }
        
        for (let i = effects.length - 1; i >= 0; i--) {
            effects[i].life--; effects[i].x += (effects[i].vx || 0); effects[i].y += (effects[i].vy || -1); if (effects[i].life <= 0) effects.splice(i, 1);
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
        
        questionBlocks.forEach(qb => {
            ctx.save();
            let hoverY = Math.sin(frameCount * 0.15) * 6; 
            ctx.translate(qb.x + qb.size/2, qb.y + qb.size/2 + hoverY);
            let pulse = Math.abs(Math.sin(frameCount * 0.1));
            ctx.fillStyle = `rgba(255, 255, 255, ${0.4 + pulse * 0.4})`; 
            ctx.beginPath(); ctx.arc(0, 0, 22 + pulse * 8, 0, Math.PI*2); ctx.fill();
            ctx.fillStyle = `rgba(241, 196, 15, ${0.6 + pulse * 0.4})`; 
            ctx.beginPath(); ctx.arc(0, 0, 16 + pulse * 4, 0, Math.PI*2); ctx.fill();
            ctx.font = "32px Arial"; ctx.shadowColor = "rgba(0,0,0,0.8)"; ctx.shadowBlur = 6; 
            ctx.fillText(qb.emoji, 0, 0);
            ctx.restore();
        });

        ctx.font = "25px Arial"; coins.forEach(c => ctx.fillText(c.emoji, c.x + c.size/2, c.y + c.size/2));
        ctx.font = "28px Arial"; gems.forEach(g => ctx.fillText(g.emoji, g.x + g.size/2, g.y + g.size/2));
        hearts.forEach(h => ctx.fillText(h.emoji, h.x + h.size/2, h.y + h.size/2));
        ctx.fillStyle = "#e74c3c"; ctx.font = "bold 20px Arial"; effects.forEach(eff => ctx.fillText(eff.text, eff.x + 20, eff.y));

        if (!isGameOver && (player.invincible <= 0 || player.isHurt === 0 || Math.floor(frameCount / 5) % 2 === 0)) {
            ctx.save();
            ctx.translate(player.x + player.size/2, player.y + player.size/2);
            if (player.isGrounded) { ctx.rotate(Math.sin(frameCount * 0.4) * 0.1); } else { ctx.rotate(0.15); }

            ctx.fillStyle = "#ffffff"; ctx.fillRect(-12, -26, 24, 10);
            ctx.fillStyle = "#e74c3c"; ctx.fillRect(-2, -24, 4, 6); ctx.fillRect(-3, -23, 6, 4);
            ctx.fillStyle = "#ffdbac"; ctx.beginPath(); ctx.arc(0, -8, 12, 0, Math.PI*2); ctx.fill();

            if (player.isHurt > 0) {
                ctx.strokeStyle = "#2c3e50"; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.moveTo(-7, -13); ctx.lineTo(-3, -11); ctx.stroke(); ctx.beginPath(); ctx.moveTo(7, -13); ctx.lineTo(3, -11); ctx.stroke();
                ctx.beginPath(); ctx.moveTo(-6, -10.5); ctx.lineTo(-4, -9); ctx.lineTo(-6, -7.5); ctx.stroke(); ctx.beginPath(); ctx.moveTo(6, -10.5); ctx.lineTo(4, -9); ctx.lineTo(6, -7.5); ctx.stroke();
                ctx.beginPath(); ctx.arc(0, -4, 3, 0, Math.PI, true); ctx.stroke();
            } else if (player.invincible > 0) {
                ctx.strokeStyle = "#2c3e50"; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.moveTo(-6, -10); ctx.lineTo(-4, -12); ctx.lineTo(-2, -10); ctx.stroke(); ctx.beginPath(); ctx.moveTo(2, -10); ctx.lineTo(4, -12); ctx.lineTo(6, -10); ctx.stroke();
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
                ctx.fillRect(-14, -2, 4, 12); ctx.fillRect(10, -2, 4, 12); ctx.fillRect(-8, 20, 6, 6); ctx.fillRect(2, 20, 6, 8); 
            }
            if (player.invincible > 0 && player.isHurt === 0) { ctx.strokeStyle = "#f1c40f"; ctx.lineWidth = 4; ctx.beginPath(); ctx.arc(0, 0, 32, 0, Math.PI*2); ctx.stroke(); }
            ctx.restore(); 
        }

        ctx.fillStyle = "#333"; ctx.textAlign = "left"; ctx.textBaseline = "alphabetic";
        ctx.font = "bold 24px Arial"; ctx.strokeStyle = "#fff"; ctx.lineWidth = 3; ctx.strokeText("SCORE: " + score, 20, 40); ctx.fillText("SCORE: " + score, 20, 40);
        
        let heartStr = ""; for(let i=0; i<player.maxLives; i++) { heartStr += (i < player.lives) ? "❤️" : "🤍"; }
        ctx.strokeText("LIVES: " + heartStr, 20, 75); ctx.fillText("LIVES: " + heartStr, 20, 75);

        ctx.font = "bold 16px Arial"; let jumpText = (player.invincible > 0 && player.isHurt === 0) ? "⚡ 4段ジャンプ解禁中！" : "2段ジャンプまで";
        ctx.strokeText(jumpText, 20, canvas.height - 20); ctx.fillStyle = (player.invincible > 0 && player.isHurt === 0) ? "#f1c40f" : "#333"; ctx.fillText(jumpText, 20, canvas.height - 20);
        
        let seconds = Math.floor(frameCount / 60); ctx.fillStyle = "#fff"; ctx.textAlign = "right"; ctx.strokeStyle = "#333"; ctx.lineWidth = 3;
        let timeStr = "TIME: " + Math.floor(seconds / 60) + ":" + (seconds % 60).toString().padStart(2, "0");
        ctx.strokeText(timeStr, canvas.width - 20, 30); ctx.fillText(timeStr, canvas.width - 20, 30);

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
components.html(html_code, height=600)