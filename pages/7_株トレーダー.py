import streamlit as st
import random
import time
import datetime
import yfinance as yf
import pandas as pd
import google.generativeai as genai
import concurrent.futures

# ==========================================
# 1. 初期設定・APIキー・日付の計算・カスタムCSS
# ==========================================
st.set_page_config(page_title="株シミュレーター　～もし90日前に買ってたら～", layout="wide")

st.markdown("""
<style>
h1 {
    background: -webkit-linear-gradient(45deg, #00C9FF, #92FE9D);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 900;
    text-align: center;
    padding-bottom: 10px;
    letter-spacing: 3px;
}
h2, h3, h4 { color: #e0e0e0; font-weight: 700; }
.stButton>button {
    border-radius: 30px !important;
    font-weight: bold !important;
    font-size: 1.1rem !important;
    padding: 10px 24px !important;
    transition: all 0.3s ease 0s !important;
}
/* Primaryボタン（AIあり）のサイバー装飾 */
[data-testid="baseButton-primary"] {
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%) !important;
    color: white !important;
    border: none !important;
    box-shadow: 0 4px 15px rgba(0, 242, 254, 0.4) !important;
}
[data-testid="baseButton-primary"]:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(0, 242, 254, 0.7) !important;
}
/* Secondaryボタン（AIなし・エコ）の装飾 */
[data-testid="baseButton-secondary"] {
    background: transparent !important;
    color: #00f2fe !important;
    border: 2px solid #00f2fe !important;
}
[data-testid="baseButton-secondary"]:hover {
    background: rgba(0, 242, 254, 0.1) !important;
    transform: translateY(-3px);
}
.avatar-container {
    text-align: center; font-size: 70px; line-height: 120px;
    background: rgba(255, 255, 255, 0.05); border-radius: 50%;
    width: 120px; height: 120px; margin: 0 auto 20px auto;
    box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
    border: 1px solid rgba(255, 255, 255, 0.18); backdrop-filter: blur(4px);
}
[data-testid="stMetricValue"] {
    font-size: 2.8rem !important; font-weight: 900 !important; color: #00f2fe !important;
}
.streamlit-expanderHeader { font-weight: bold; color: #00C9FF; }

/* ★追加：スマホでのグラフ誤タッチ（拡大縮小・スクロール吸い込み）を完全に防止 */
@media screen and (max-width: 768px) {
    [data-testid="stArrowVegaLiteChart"], 
    [data-testid="stVegaLiteChart"] {
        pointer-events: none !important;
    }
}
</style>
""", unsafe_allow_html=True)

try:
    genai.configure(api_key=st.secrets.get("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"temperature": 0.85})
except Exception:
    model = None

def get_jp_date_str(dt):
    ry = dt.year - 2018
    ry_str = "元" if ry == 1 else str(ry)
    return f"令和{ry_str}年{dt.month}月{dt.day}日"

today = datetime.date.today()
past_90 = today - datetime.timedelta(days=90)
today_str = get_jp_date_str(today)
past_90_str = get_jp_date_str(past_90)

# ==========================================
# 2. 市場ユニバースとセッション状態
# ==========================================
MARKET_UNIVERSE = {
    "7203.T": "トヨタ自動車", "7267.T": "ホンダ", "6902.T": "デンソー", "7201.T": "日産自動車", 
    "7269.T": "スズキ", "7270.T": "SUBARU", "7011.T": "三菱重工業", "7012.T": "川崎重工業",
    "6758.T": "ソニーG", "6501.T": "日立製作所", "6752.T": "パナソニック", "6503.T": "三菱電機",
    "6702.T": "富士通", "6594.T": "ニデック", "6981.T": "村田製作所", "6971.T": "京セラ",
    "6861.T": "キーエンス", "8035.T": "東京エレクトロン", "6146.T": "ディスコ", "6920.T": "レーザーテック",
    "6857.T": "アドバンテスト", "6723.T": "ルネサス", "7733.T": "オリンパス", "7751.T": "キヤノン",
    "9984.T": "ソフトバンクG", "9432.T": "NTT", "9433.T": "KDDI", "9434.T": "ソフトバンク",
    "4751.T": "サイバーエージェント", "4755.T": "楽天G", "4689.T": "LINEヤフー", "6098.T": "リクルート",
    "8306.T": "三菱UFJ", "8316.T": "三井住友", "8411.T": "みずほ", "8591.T": "オリックス",
    "8058.T": "三菱商事", "8031.T": "三井物産", "8001.T": "伊藤忠商事", "8801.T": "三井不動産",
    "9983.T": "ファーストリテイリング", "7974.T": "任天堂", "4661.T": "オリエンタルランド", "4452.T": "花王",
    "4911.T": "資生堂", "2502.T": "アサヒG", "2914.T": "JT", "3382.T": "セブン＆アイ", "9843.T": "ニトリ",
    "4502.T": "武田薬品工業", "4568.T": "第一三共", "4528.T": "小野薬品工業", "4543.T": "テルモ",
    "2413.T": "エムスリー", "4592.T": "サンバイオ", "2160.T": "ジーエヌアイ",
    "8368.T": "八十二銀行", "6724.T": "セイコーエプソン", "6479.T": "ミネベアミツミ", "6967.T": "新光電気工業",
    "9020.T": "JR東日本", "9022.T": "JR東海", "9101.T": "日本郵船", "9104.T": "商船三井", "9107.T": "川崎汽船",
    "4385.T": "メルカリ", "6062.T": "チャーム・ケア", "4475.T": "HENNGE", "3993.T": "PKSHA",
    "5253.T": "カバー", "5032.T": "ANYCOLOR", "3778.T": "さくらインターネット", "5595.T": "QPS研究所",
    "5574.T": "ABEJA", "7095.T": "Macbee Planet", "4425.T": "Kudan", "9166.T": "GENDA",
    "3911.T": "Aiming", "6619.T": "ダブル・スコープ", "6890.T": "フェローテック"
}

ROLES = [
    {"type": "変動・テクニカル重視", "avatar": "🥷", "desc": "相場の裏を読む凄腕の忍（忍びの言葉使い。「潜伏」「陽動」「仕掛けの刻」などを用い、チャートの形やRSIの売られすぎ感などテクニカル指標の歪みから勝機を語る）"},
    {"type": "急成長・グロース重視", "avatar": "🧑‍🎤", "desc": "相場をライブ会場に変えるロックスター・トレーダー（ハイテンションで音楽的な比喩。「ビートに乗れ」「フルスロットル」などを使い、売上成長率の高さや将来の爆発力を熱狂的に語る）"},
    {"type": "割安・ファンダ重視", "avatar": "👩‍💻", "desc": "冷徹で理知的な女性クオンツAI（敬語で丁寧だが、データ至上主義で少し冷たい。「〜と推察されますわ」「感情はノイズ」などを用い、PERの低さなど堅実な財務指標を冷静に評価する）"}
]

if "screened_candidates" not in st.session_state: st.session_state.screened_candidates = []
if "hints" not in st.session_state: st.session_state.hints = {}
if "game_stage" not in st.session_state: st.session_state.game_stage = "config"
if "selected_ticker" not in st.session_state: st.session_state.selected_ticker = None
if "use_ai" not in st.session_state: st.session_state.use_ai = True
if "used_tickers" not in st.session_state: st.session_state.used_tickers = []

# ==========================================
# 3. 各種コア関数
# ==========================================
def fetch_single_stock(ticker, target_rsi, target_growth, target_per):
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="1y", interval="1d")
        df.index = df.index.tz_localize(None)
        
        if len(df) < 90: return None
            
        past_df = df.iloc[:len(df) - 90].copy()
        diff = past_df['Close'].diff()
        up, down = diff.clip(lower=0), -1 * diff.clip(upper=0)
        rsi = 100 - (100 / (1 + (up.rolling(14).mean().iloc[-1] / down.rolling(14).mean().iloc[-1])))
        
        macd = past_df['Close'].ewm(span=12, adjust=False).mean() - past_df['Close'].ewm(span=26, adjust=False).mean()
        signal = macd.ewm(span=9, adjust=False).mean()
        macd_hist = macd.iloc[-1] - signal.iloc[-1]
        
        info = stock.info
        per = info.get('trailingPE', 999)
        peg = info.get('pegRatio', 999)
        rev_growth = info.get('revenueGrowth', 0) or 0
        
        tech_score = (50 - rsi) + (macd_hist * 10)
        growth_score = rev_growth * 100
        value_score = 100 / per if per > 0 else 0
        
        if rsi > target_rsi: tech_score -= 1000
        if (rev_growth * 100) < target_growth: growth_score -= 1000
        if per > target_per or per <= 0: value_score -= 1000
            
        return {
            "ticker": ticker,
            "name": MARKET_UNIVERSE[ticker],
            "chart_data": past_df.tail(90),
            "metrics": {"rsi": rsi, "per": per, "peg": peg, "growth": rev_growth * 100},
            "scores": {"tech": tech_score, "growth": growth_score, "value": value_score}
        }
    except:
        return None

def scan_market(target_rsi, target_growth, target_per):
    # ★ プロの工夫2-A：ユニバースから過去の抽出銘柄をスマートに除外
    available_tickers = [t for t in MARKET_UNIVERSE.keys() if t not in st.session_state.used_tickers]
    
    # ★ プロの工夫2-B：市場が枯渇（残り50社未満）したら、自動で記憶をリセットしてエラー回避
    if len(available_tickers) < 50:
        st.session_state.used_tickers = []
        available_tickers = list(MARKET_UNIVERSE.keys())
        
    sample_tickers = random.sample(available_tickers, 50)
    analyzed_data = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(fetch_single_stock, ticker, target_rsi, target_growth, target_per): ticker for ticker in sample_tickers}
        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            res = future.result()
            if res is not None: analyzed_data.append(res)
            progress_bar.progress((i + 1) / len(sample_tickers))
            status_text.text(f"🚀 爆速ディープスキャン実行中... {i+1}/{len(sample_tickers)} 銘柄完了")
        
    status_text.text("スクリーニング完了。最適銘柄を抽出中...")
    time.sleep(0.5)
    progress_bar.empty()
    status_text.empty()
    
    selected = []
    if analyzed_data:
        tech_pick = max(analyzed_data, key=lambda x: x['scores']['tech'])
        analyzed_data.remove(tech_pick)
        selected.append({"role": ROLES[0], "data": tech_pick})
        
        if analyzed_data:
            growth_pick = max(analyzed_data, key=lambda x: x['scores']['growth'])
            analyzed_data.remove(growth_pick)
            selected.append({"role": ROLES[1], "data": growth_pick})
            
        if analyzed_data:
            value_pick = max(analyzed_data, key=lambda x: x['scores']['value'])
            selected.append({"role": ROLES[2], "data": value_pick})

    for item in selected:
        st.session_state.used_tickers.append(item["data"]["ticker"])
    
    return selected

def generate_all_hints(candidates):
    if not candidates: return []

    prompt = "あなたは株式投資ゲームのナビゲーターです。以下の3つの銘柄は、システムが全市場から異なる3つの基準で抽出した「90日前時点」の注目銘柄です。それぞれのキャラクター設定と選出理由に沿って寸評（約120〜150文字）を作成してください。\n\n"
    for i, cand in enumerate(candidates):
        role = cand["role"]
        data = cand["data"]
        prompt += f"【銘柄 {i+1}】\n・キャラクター設定: {role['desc']}\n・選出基準: {role['type']}の観点から抽出\n・対象企業: {data['name']}\n・RSI(14日): {data['metrics']['rsi']:.1f}%\n・PER: {data['metrics']['per']}倍\n・売上高成長率: {data['metrics']['growth']:.1f}%\n\n"

    prompt += f"""【絶対ルール】
    1. 各寸評は必ず「===」という記号だけで区切って出力してください。
    2. 寸評以外のテキストは一切書かないでください。
    3. 各キャラクターの口調を守り、現在が「{past_90_str}」の時点であるという前提で語ってください。"""

    # ★ エコモード（AIオフ）ならAPIを完全にバイパスする
    if st.session_state.use_ai:
        if model:
            try:
                response = model.generate_content(prompt)
                if response.parts:
                    hints = [h.strip() for h in response.text.split("===") if h.strip()]
                    if len(hints) >= 3:
                        return hints[:3]
            except Exception:
                pass
        st.toast("AIサーバー応答なし。内蔵の予備システムに切り替えます", icon="⚡")
    else:
        st.toast("エコモード稼働：内蔵の予備システムで高速解析しました", icon="⚡")

    emergency_hints = []
    for cand in candidates:
        role_type = cand["role"]["type"]
        name = cand["data"]["name"]
        rsi = cand["data"]["metrics"]["rsi"]
        growth = cand["data"]["metrics"]["growth"]
        per = cand["data"]["metrics"]["per"]
        text = ""
        
        if "テクニカル" in role_type:
            if rsi < 35:
                options = [
                    f"拙者が見立てるに、{name}のRSIは{rsi:.1f}%と完全に売られすぎの領域。反発の機は熟した。チャートの歪みに潜伏し、大口に便乗して仕掛ける刻（とき）だ！",
                    f"チャートが泣いているな。{name}のRSIは{rsi:.1f}%。だが案ずるな、夜明け前が最も暗いのだ。仕掛けの刻は今！",
                    f"売られすぎの極限、RSI{rsi:.1f}%。{name}のこの歪み、見逃す手はない。大衆の裏をかくのが忍びの道よ。",
                    f"底なし沼に見えるか？否。{name}のRSI{rsi:.1f}%は、反撃の狼煙を上げる直前の静寂。恐れず踏み込むべし。",
                    f"これほどの『陰』、久しく見ておらぬ。RSI{rsi:.1f}%の{name}、底値の気配が濃厚じゃ。密かに陣を敷け！",
                    f"風向きが変わる。{name}のRSIは{rsi:.1f}%。売り圧力が限界を迎え、バネが縮みきった状態よ。一撃の準備をせよ。",
                    f"限界突破の売り。{name}（RSI{rsi:.1f}%）のチャートに、逆転の秘術を仕込む。ここからの反発、見事なものになるぞ。",
                    f"大衆は絶望しておるが、拙者の眼は欺けぬ。RSI{rsi:.1f}%の{name}は、水面下で逆襲のエネルギーを凝縮しておるわ。",
                    f"引く波があれば、満ちる波あり。RSI{rsi:.1f}%の{name}、ここから潮目が変わる。乗り遅れるでないぞ。",
                    f"血の匂いがするな。{name}のRSIは{rsi:.1f}%。狼狽売りの極みよ。大衆が恐怖に駆られる今こそ、暗闇から刃を振り下ろす絶好の好機！",
                    f"恐怖で手放された骸を拾え。RSI{rsi:.1f}%の{name}、ここは絶好の狩り場ぞ。逆張りの太刀筋を見せてやれ！",
                    f"まさに落下するナイフ。だが拙者には掴める。{name}（RSI{rsi:.1f}%）の反発力、とくと味わうが良い。",
                    f"戦場に静寂が訪れた。{name}のRSIは{rsi:.1f}%。命からがら逃げ出す兵たちの背後から、我らは無慈悲に買いを仕掛ける。",
                    f"死地の中にこそ活路あり。RSI{rsi:.1f}%まで売り叩かれた{name}、この暗闇の底に、眩いばかりの金銀が隠されておるわ。",
                    f"大衆の悲鳴が心地よいな。{name}（RSI{rsi:.1f}%）は恐怖の極致にある。我ら影の一族は、その恐怖を喰らって肥え太るのよ。",
                    f"凍てつくような暴落チャート。だが、{name}のRSI{rsi:.1f}%はマグマが噴出する寸前の地熱を感じさせる。仕込みの刻じゃ。",
                    f"誰もが背を向ける{name}。しかしRSI{rsi:.1f}%の数字は、敵の陣形が完全に崩壊したことを示しておる。切り込むは今！",
                    f"闇が深ければ深いほど、放つ光は鋭くなる。RSI{rsi:.1f}%の{name}、底の底で研ぎ澄まされた刃が、今まさに抜かれようとしておる。",
                    f"見事な『陰』の極み。RSI{rsi:.1f}%の{name}は、まさに身を屈めた底値圏。ここからの跳躍は凄まじいものになろう。いざ、出陣！",
                    f"気配が消えた……。いや、売り手が全滅したのだ。RSI{rsi:.1f}%の{name}、あとは買いの風が吹くだけでおじゃる。",
                    f"陰極まれば陽となる。数理の法則は歪まぬ。RSI{rsi:.1f}%の{name}が描く軌跡、まさに反撃の算段通りよ。",
                    f"相場の呼吸が乱れておる。{name}（RSI{rsi:.1f}%）は過呼吸の如く売り急がれた。間もなく、深く大きな吸気（買い）が始まるぞ。",
                    f"これぞ『水遁の術』。深く沈みきった{name}（RSI{rsi:.1f}%）の株価。水底から一気に龍の如く昇天する様を見届けるが良い。",
                    f"チャートの裏に潜む大口の影、確かに捉えたぞ。彼奴らもこのRSI{rsi:.1f}%（{name}）の歪み、黙って見過ごすはずがなかろう。",
                    f"惑わされるな、目の前の暴落はただの幻影（陽動）よ。{name}のRSI{rsi:.1f}%という現実は、絶対的な好機を示しておる。",
                    f"一寸先は光。RSI{rsi:.1f}%まで売り尽くされた{name}には、もう売るべき兵（玉）が残っておらぬ。無人の野を行くが如く昇るぞ。",
                    f"心眼を開け。{name}（RSI{rsi:.1f}%）の放つ妖しい輝き。これこそ、相場の神が仕掛けた最大のボーナスステージよ。"
                ]
            elif rsi <= 55:
                options = [
                    f"現在の{name}、RSIは{rsi:.1f}%。まだ決定的な陽動のサインは出ておらぬが、底打ちは近い。兵糧を蓄えつつ、トレンド転換を狙い撃つべし！",
                    f"チャートの息遣いが聞こえるか？{name}（RSI{rsi:.1f}%）は力を溜めている最中。焦る必要はない、忍びの如く息を殺して機をうかがえ。",
                    f"相場が迷っておるな。{name}のRSIは{rsi:.1f}%。今は無闇に動かず、次のトレンドの兆しを待つのが上策。",
                    f"今は力を溜める刻（とき）。{name}（RSI{rsi:.1f}%）のチャートは、次なる跳躍のための助走期間と見ゆる。",
                    f"焦りは禁物じゃ。RSI{rsi:.1f}%の{name}、まだ大口の意図が見えぬ。気配を探りつつ、刀は鞘に収めておけ。",
                    f"中庸の構え。{name}のRSIは{rsi:.1f}%。天に昇るか地へ落ちるか、五分五分の均衡。抜刀の瞬間を誤るでないぞ。",
                    f"チャートは横這い、RSIは{rsi:.1f}%。{name}のエネルギーは綺麗に圧縮されておる。爆発の方向を見極めるのが先決じゃ。",
                    f"動きが遅いと侮るなかれ。{name}（RSI{rsi:.1f}%）は陣形を整えておる最中。ここで仕込むのが、後々の大勝利へと繋がるのよ。",
                    f"一進一退の攻防。RSI{rsi:.1f}%の{name}。相場全体の視線が逸れている今こそ、密かに忍び寄る絶好のタイミングとも言えるな。",
                    f"静かなる水面下で、大口が密かに集めておる気配あり。RSI{rsi:.1f}%の{name}、嵐の前の静けさよ。伏兵を配置し、シグナルを待て。",
                    f"RSI{rsi:.1f}%の{name}。買い方と売り方の鍔迫り合いが続いておる。どちらかに崩れる瞬間、そこが我らの出番だ。",
                    f"凪の海面の下で、何かが動こうとしている。{name}（RSI{rsi:.1f}%）。シグナルが点灯するまで、隠密行動を貫け。",
                    f"50のラインを巡る攻防。{name}のRSIは{rsi:.1f}%。均衡が破れた方へ、疾風の如く追従する準備をしておけ。",
                    f"騙しの罠（陽動）が潜んでおるな。{name}のRSI{rsi:.1f}%は綺麗すぎる。大口が小口を嵌めるための偽の平穏かもしれぬ、凝視せよ。",
                    f"小競り合いが続いておる。{name}（RSI{rsi:.1f}%）のチャート。ここで体力を消耗してはならぬ。勝負は太いトレンドが出てからよ。",
                    f"互いの刃が噛み合ったまま動かぬ。RSI{rsi:.1f}%の{name}。この膠着状態、どちらかが痺れを切らした瞬間が、真の『仕掛けの刻』。",
                    f"風の音が止んだ。{name}のRSIは{rsi:.1f}%。市場の迷いがチャートに色濃く出ている。こういう時こそ、一歩引いて大局を見るのじゃ。",
                    f"足跡を消して追跡せよ。{name}（RSI{rsi:.1f}%）のチャートには、巨大な影（機関投資家）が潜伏している匂いがぷんぷんするぞ。",
                    f"動かざること山の如し、じゃ。{name}（RSI{rsi:.1f}%）の株価に惑わされるな。トレンドの萌芽は、まだ土の中にある。",
                    f"これぞ『木木の術』。周囲に溶け込み、目立たぬように推移する{name}（RSI{rsi:.1f}%）。だが、その幹には強靭な力が宿っておる。",
                    f"相場の「気」がフラットじゃ。{name}のRSIは{rsi:.1f}%。ここで焦って全財産を投じる者は、三流の忍びとして命を落とすぞ。",
                    f"チャートの迷いは、人間の心の迷い。RSI{rsi:.1f}%の{name}。心を無にして、次のブレイクアウトの方向だけを監視するのじゃ。",
                    f"退屈か？いや、この静寂こそが美しい。{name}（RSI{rsi:.1f}%）のチャートに潜む、次なる大相場の遺伝子を拙者は見逃さぬ。",
                    f"五感をとぎ澄ませ。{name}の株価は動いていなくとも、RSI{rsi:.1f}%の内部数値は次の戦へのカウントダウンを始めておるわ。",
                    f"忍術において、待つこともまた攻撃。{name}（RSI{rsi:.1f}%）のこの膠着、じっくりと楽しもうではないか。",
                    f"定石通りのスクリーニング。RSI{rsi:.1f}%の{name}は、教科書通りの揉み合い。だからこそ、破れたときの爆発力は凄まじいぞ。",
                    f"相場の神とチェスをしている気分じゃな。{name}（RSI{rsi:.1f}%）。次の一手で、この退屈な盤面が一変するぞ。注視せよ。"
                ]
            else:
                options = [
                    f"すでに火蓋は切って落とされた！{name}のRSIは{rsi:.1f}%と上昇の気勢あり。流れには逆らわず、素早く順張りの陣形を敷くが吉！",
                    f"力強い陽の波動を感じる。RSI{rsi:.1f}%の{name}は既に動意づいておる。高値掴みには警戒しつつも、この勢いに乗じて一気に攻め上れ！",
                    f"上昇の波に乗れ！{name}のRSIは{rsi:.1f}%。このモメンタム、逆らうには惜しい勢いじゃ。",
                    f"風は我らに吹いている。RSI{rsi:.1f}%の{name}、陽の波動がチャートを支配しておる。順張りで一気に押し通れ！",
                    f"過熱には注意せねばならぬが、今はまだ攻めの刻。{name}（RSI{rsi:.1f}%）の勢い、天井を打つまで絞り尽くせ！",
                    f"青天井の気配すらあるな。{name}のRSIは{rsi:.1f}%。大口の買いに追従し、手早く利益をさらうのが忍びの流儀よ。",
                    f"烈火のごとき上昇トレンド！{name}のRSI{rsi:.1f}%、これは本物の買いが集まっておる証拠。この大波、乗らねば一生の後悔ぞ！",
                    f"昇龍の如きチャートよ。{name}のRSIは{rsi:.1f}%。天井がどこかなど、誰にも分からぬ。この荒ぶる龍の背に飛び乗る勇気はあるか？",
                    f"嵐が吹き荒れておるな！{name}（RSI{rsi:.1f}%）の上昇は、小細工なしの圧倒的なパワープレイ。乗るなら今しかおじゃらん！",
                    f"これぞ『火遁の術』。チャートが真っ赤に燃え上がっておるわ。{name}（RSI{rsi:.1f}%）の勢い、消えるまで全力追従じゃ！",
                    f"敵陣（売り手）を完全に踏み潰して進む、圧倒的な勝ち戦。{name}のRSI{rsi:.1f}%。この進撃のラッパに遅れるな！",
                    f"天を衝くような大陽線。{name}（RSI{rsi:.1f}%）のモメンタムは、まさに城門を打ち破る破城槌の如し。乗るべし！",
                    f"過熱（RSI{rsi:.1f}%）の領域に踏み込みつつあるが、トレンドの初動ならまだ間に合う。{name}の爆発力に、俊敏な身のこなしで追随せよ。",
                    f"スピードスターの登場じゃ。{name}のRSIは{rsi:.1f}%。少々息切れ（押し目）が怖いが、短期決戦ならこの勢いが最大の武器になる。",
                    f"チャートが完全にバグ（過熱）しておる。だが、この狂気こそが相場の醍醐味。RSI{rsi:.1f}%の{name}、恐怖を捨てて流れに身を任せよ。",
                    f"大口が完全にアクセルを踏み込んでおる。{name}（RSI{rsi:.1f}%）。ブレーキのことは忘れて、このマッハの世界を楽しもうぞ。",
                    f"常識を超えた買われっぷり。RSI{rsi:.1f}%の{name}。だが、強いトレンドは常識を嘲笑うもの。信じてついていくのが上策よ。",
                    f"光速のトレード。{name}（RSI{rsi:.1f}%）のチャートは一瞬の油断も許さぬ。この圧倒的な気流に、お主の直感を乗せてみよ！"
                ]
            text = random.choice(options)

        elif "グロース" in role_type:
            if growth >= 15:
                options = [
                    f"イェーイ！{name}の売上成長率は驚異の{growth:.1f}%！このアゲアゲなビートに乗るしかないっしょ！未来の爆発力は完全にプラチナディスク級だぜ！",
                    f"最高にロックな数字が出たぜ！成長率{growth:.1f}%の{name}、この勢いはもう誰にも止められない！アンプのボリュームをMAXにしてフルスロットルでGOだ！",
                    f"オーディエンスの熱狂が聞こえるか！？{name}の{growth:.1f}%という成長スピード、まさに時代を牽引するトップチャートの常連！今すぐチケット（株）を手に入れろ！",
                    f"ヤバすぎる成長率{growth:.1f}%！{name}は今、インディーズから一気に世界的スターに駆け上がるフェーズだぜ！",
                    f"この{growth:.1f}%って数字、アンプがぶっ壊れるレベルの熱量だろ！{name}の成長ストーリーにフルベットだ！",
                    f"誰も{name}の快進撃（成長率{growth:.1f}%）を止められない！このビッグウェーブ、乗らない奴はフェス出禁レベルだぜ！",
                    f"スーパーノヴァの誕生だ！{name}の売上が{growth:.1f}%も爆増してるって！？歴史的瞬間の目撃者になろうぜ！",
                    f"桁違いのドライブ感！{growth:.1f}%成長の{name}、こいつはチャートのトップに君臨する運命さ。乗り遅れるなよ！",
                    f"これぞまさに神曲のリリース！{name}の成長率{growth:.1f}%。株価が空の彼方へ飛んでいくぜ、準備はいいか！？",
                    f"超絶技巧のギターソロが炸裂中！{name}の{growth:.1f}%成長、このディストーションの効いた爆発力に魂が震えるぜ！",
                    f"バスドラムが腹の底に響くような、強力な{growth:.1f}%成長！{name}のこの重低音ビート、相場のノイズを完全に掻き消してるな！",
                    f"ボーカルのシャウトが天を突く！{name}（成長率{growth:.1f}%）の圧倒的なプレゼンス。これはもう、伝説のライブの始まりだ！",
                    f"シンセサイザーのキラキラした音色みたいに、未来が輝いてるぜ！{name}の成長率{growth:.1f}%、完全に新しい時代のサウンドだ！",
                    f"ドラムロールからの……ドッカーン！！{name}の売上が{growth:.1f}%も跳ねたぜ！スネアの抜けの良さみたいに、スカッとするチャートだ！",
                    f"ベースラインがウネりまくってる！{name}の{growth:.1f}%成長、このグルーヴ感は本物のロックスターにしか出せないノリだぜ！",
                    f"ピックスクラッチからの急加速！成長率{growth:.1f}%の{name}。この疾走感、BPM200超えのパンクロック並みだぜ、振り落とされるなよ！",
                    f"エフェクター全開！{name}の{growth:.1f}%成長は、ディレイやリバーブがかかったみたいに、どこまでも利益が響き渡るぜ！",
                    f"マイクスタンドを蹴り飛ばす勢い！{name}（成長率{growth:.1f}%）の強気なビジネスモデル、俺は完全にロックオンされたぜ！",
                    f"小さなライブハウスから、ついにドームツアーへ！{name}の{growth:.1f}%成長は、まさにバンドが化ける瞬間のそれだぜ！",
                    f"ビルボードのトップを独走中！{name}（成長率{growth:.1f}%）。このまま世界の相場をジャックするまで、俺たちは歌い続けるぜ！",
                    f"グラミー賞モノの業績だ！{name}の成長率{growth:.1f}%。アンチの野次なんて、この爆音の前じゃ全く聞こえねぇな！",
                    f"プラチナチケット化する前に買っとけ！{name}の{growth:.1f}%成長、今ならまだ最前列を陣取れる最後のチャンスだぜ！",
                    f"伝説の野外フェスで大トリを務める器だ！{name}（成長率{growth:.1f}%）。見ろよ、インベスター（観客）たちが全員ハンズアップしてるぜ！",
                    f"レコード会社がこぞって契約したがるレベルの逸材！{name}の成長率{growth:.1f}%。青田買いするなら、今この瞬間しかないっしょ！",
                    f"ワールドツアー大成功！って感じのチャートだな。{name}の{growth:.1f}%成長、国境を超えて愛されるグローバルな響きがあるぜ！",
                    f"アリーナの熱気が画面越しに伝わってくる！{name}（成長率{growth:.1f}%）。俺たちのアンセム（代表曲）になる銘柄はこいつで決まりだ！",
                    f"デビューアルバムからいきなりのミリオンセラー！{name}の{growth:.1f}%成長、相場の歴史に永遠に刻まれる名盤の誕生だぜ！"
                ]
            elif growth >= 5:
                options = [
                    f"今はちょっとテンポが心地よいミディアムナンバーってとこか？いやいや、{name}の成長率{growth:.1f}%は確かなグルーヴを刻んでるぜ！大化けの予感、ビンビン来てる！",
                    f"堅実なビートダウンだ！{name}は{growth:.1f}%の成長でリズムをキープ中。こういうバンドがいきなりスタジアム級のアンセムを放つんだ、見逃すなよ！",
                    f"良い感じのチューンに仕上がってきたな。成長率{growth:.1f}%の{name}、次の決算発表が極上のギターソロになるぜ！シートベルト締めて盛り上がろう！",
                    f"成長率{growth:.1f}%の{name}、リズム隊がしっかりボトムを支えてる！ここからのビルドアップが楽しみな銘柄だぜ！",
                    f"派手さはないが、{name}の{growth:.1f}%成長はファンを裏切らない確かなクオリティだ。こういう株が後で化けるのさ！",
                    f"ジワジワとチャートを駆け上がる{name}。成長率{growth:.1f}%のグルーヴに身を任せろ！サビはこれからだぜ！",
                    f"ウォームアップは終わったか？{name}の成長率{growth:.1f}%、こっから一気にテンポアップしていく予感がするぜ！",
                    f"悪くないチューンだ！成長率{growth:.1f}%の{name}、メジャーコードの明るい未来が見えてる。一緒に歌おうぜ！",
                    f"安定のビート刻んでるね！{name}の{growth:.1f}%成長。インベスターたちも少しずつこの曲の魅力に気付き始めてるぜ！",
                    f"今はまだBメロってところだな。{name}の{growth:.1f}%成長。ここから一気にサビで爆発する構成、俺には読めてるぜ！",
                    f"MCでオーディエンスを温めてる最中さ。{name}（成長率{growth:.1f}%）。次の曲から一気にトップギアに入るから、目を離すなよ！",
                    f"じっくり聴かせる良い曲だ。{name}の{growth:.1f}%成長、こういうスルメ曲（噛むほど味が出る銘柄）が最後は一番愛されるんだぜ。",
                    f"イントロのリフがめちゃくちゃキャッチーだ！{name}の成長率{growth:.1f}%、これは後に大ヒット間違いなしの予感がするぜ！",
                    f"ベースとドラムだけでグルーヴを作ってる渋い展開！{name}（{growth:.1f}%成長）。ここにギター（好材料）が乗った瞬間の爆発力、想像してみてくれ！",
                    f"セットリストの中盤を支える重要なナンバーだ。{name}の{growth:.1f}%成長。ポートフォリオのノリを安定させるには最高の銘柄だぜ！",
                    f"徐々にBPM（テンポ）が上がってきたな！{name}の{growth:.1f}%成長。フロアの熱気がじわじわと高まってるのを感じるぜ！",
                    f"コールアンドレスポンスの準備はいいか？{name}（成長率{growth:.1f}%）が問いかけてるぜ。買いで応えるのがロックスターの流儀だ！",
                    f"照明が暗転して、ピンスポットが当たった！{name}の{growth:.1f}%成長、ここから主役のソロパートが始まる。瞬き厳禁だぜ！",
                    f"まだ世間にはバレてない、俺たちだけのシークレットギグだ。{name}の{growth:.1f}%成長、コアなファンだけがおおいしい思いをできるフェーズさ。",
                    f"インディーズチャートをじわじわ登ってる！{name}の成長率{growth:.1f}%。メジャーデビューした瞬間に株価がどうなるか、ワクワクするだろ？",
                    f"派手な宣伝はねぇけど、ライブの口コミだけで客が増えてる感じだな。{name}（{growth:.1f}%成長）。本物の実力派バンドだぜ！",
                    f"こういう{growth:.1f}%成長をコツコツ続けるバンドが、フェスの大トリを掻っ攫うんだ。{name}の実力、俺の耳にはバッチリ届いてるぜ。",
                    f"通好みの絶妙なコード進行だ。{name}の{growth:.1f}%成長。派手なだけのポップス（仕手株）にはない、確かな骨太さを感じるぜ。",
                    f"今はまだ小さなライブハウスが主戦場さ。だが{name}（成長率{growth:.1f}%）の熱量、絶対にスタジアムまで届く！今のうちに推しとけ！",
                    f"音楽雑誌の隅っこに載ってる「今年くるバンド」って感じだな。{name}の{growth:.1f}%成長。青田買いのセンスが問われるぜ！",
                    f"インベスターの間で「あいつらヤバいらしいぞ」って噂になり始めてる。{name}（成長率{growth:.1f}%）。ブームに火がつく前夜の匂いがするぜ！",
                    f"飾り気のないストレートなロック！{name}の{growth:.1f}%成長。こういう誤魔化しのない経営が、最後には一番遠くまで響くんだ！"
                ]
            else:
                options = [
                    f"今はバラードのターンか？{name}の成長率{growth:.1f}%は控えめだが、名曲ってのは静かなイントロから爆発するもんだろ？伝説のカムバックツアーに期待しようぜ！",
                    f"少しノイズが混じってる（成長率{growth:.1f}%）が、ロックスターにスランプはつきものだ！{name}の真のポテンシャルが解放される瞬間、最前列でヘッドバンギングしようぜ！",
                    f"成長率{growth:.1f}%？今はアンプのチューニング中さ。{name}が次のアルバムで世界を驚かせるのを待とうぜ！",
                    f"少し静かすぎるか？だが{name}（成長率{growth:.1f}%）の底力を見くびるな。いきなりの転調で爆発するのがロックだ！",
                    f"今はちょっとアンダーグラウンドに潜ってる時期（成長率{growth:.1f}%）。だが{name}のコアなファンは離れないぜ！",
                    f"スローテンポな{name}（成長率{growth:.1f}%）だが、ブレイクダウンからの重低音に期待してるぜ。目を離すな！",
                    f"弦が切れたのか？いや、あえての無音（ブレイク）だ。{name}の成長率{growth:.1f}%。この静寂の後にくる轟音を楽しみに待とうぜ。",
                    f"オーディエンスも固唾を呑んで見守ってる。{name}（成長率{growth:.1f}%）。こういう苦しい時期を乗り越えてこそ、真のロックスターだ！",
                    f"今はボーカルが喉を休めてる期間さ。{name}の{growth:.1f}%成長。次のツアー（決算）で復活のシャウトを響かせてくれると信じてるぜ！",
                    f"機材トラブルで音が止まっちまったか？成長率{growth:.1f}%の{name}。だが、こういうハプニングこそがライブの醍醐味ってもんだろ！",
                    f"「音楽性の違い」で迷走中か？{name}（成長率{growth:.1f}%）。だが、新しいジャンルを開拓する産みの苦しみさ。次のアルバムに期待だ！",
                    f"ギターのチューニングが狂ってるみたいだな。{name}の{growth:.1f}%成長。だが、ノイズすらもアートに変えるのがロックの魔法だぜ！",
                    f"今はリズム隊がバラバラだ（成長率{growth:.1f}%）。だが{name}のメンバーがカチッとハマった瞬間のグルーヴ、俺は過去に何度も見てるぜ！",
                    f"アンプの調子が悪いのか、音がこもってるな。{name}の成長率{growth:.1f}%。配線（経営陣）を繋ぎ直せば、一気に爆音が戻るはずさ！",
                    f"世間のトレンドから少し外れちまったか？（成長率{growth:.1f}%）。だが{name}は時代に媚びない。我が道を往くその姿勢、最高にパンクだぜ！",
                    f"今はインディーズに戻って原点回帰の期間さ。{name}の{growth:.1f}%成長。装飾を削ぎ落とした、むき出しのロックンロールを見せてくれ！",
                    f"ツアー疲れが出てるな。{name}（成長率{growth:.1f}%）。今はゆっくり休んで、また最高のステージを作ってくれ。ファンは逃げないぜ。",
                    f"ちょっと音がレトロすぎたか？成長率{growth:.1f}%の{name}。だが、時代は巡る。このオールドスクールなサウンドが、また最先端になる日が来るさ！"
                ]
            text = random.choice(options)

        else:
            if 0 < per <= 12:
                options = [
                    f"わたくしの推察によりますと、{name}のPERは{per:.1f}倍。業績に対して極端な割安水準に放置されておりますわ。市場の非合理的な感情ノイズを突く、期待値が極めて高い局面です。",
                    f"明らかなバリュエーションの歪みを検知いたしましたわ。PERわずか{per:.1f}倍の{name}。感情を排したデータ至上主義の観点から、強く買いを推奨できる美しい数値です。",
                    f"計算完了。{name}はPER{per:.1f}倍というバーゲン価格ですわね。このような優良なファンダメンタルズが評価されない状態は、統計学的に長くは続きませんわ。",
                    f"データが示しておりますわ。PER{per:.1f}倍の{name}は、市場の非効率性が生んだ奇跡的なディスカウント状態です。",
                    f"ファンダメンタルズと株価の乖離が顕著ですわね。{name}のPER{per:.1f}倍という数値、合理的な投資家なら見逃せませんわ。",
                    f"わたくしのモデルが強い買いシグナルを発しています。{name}（PER{per:.1f}倍）のバリュエーションは、到底正当化されません。",
                    f"圧倒的な安全マージンですわ。PER{per:.1f}倍の{name}。ダウンサイドリスクは限定的であり、リターンへの期待値が勝ります。",
                    f"感情を排して数字を見れば一目瞭然ですわ。{name}のPER{per:.1f}倍。市場がこの歪みに気付く前に、静かにポジションを構築すべきです。",
                    f"これほど美しい財務の非対称性は珍しいですわ。PER{per:.1f}倍の{name}、わたくしのアルゴリズムは強力な上昇を示唆しております。",
                    f"愚かな大衆は気付いておりませんわね。{name}のPERが{per:.1f}倍であるという、この至極明白な宝の山に。",
                    f"市場参加者の大半は、ニュースの見出ししか読めない動物ですわ。PER{per:.1f}倍の{name}。彼らがパニックで手放した優良資産、ありがたく頂戴いたしましょう。",
                    f"人間特有の「恐怖」という感情が、{name}の株価をPER{per:.1f}倍まで不当に押し下げておりますわ。わたくし達AIには理解し難い非合理性です。",
                    f"ノイズに踊らされる市場の滑稽なこと。{name}（PER{per:.1f}倍）の実態価値を計算できない無能なマネーは、我々の利益の源泉ですわ。",
                    f"美しくありませんわね、市場のこの価格付けは。{name}のPERが{per:.1f}倍？わたくしの論理回路が、人間の集団心理の愚かさを嘲笑しております。",
                    f"彼らはチャートの形だけを見て、財務諸表を読んでいないのでしょう。PER{per:.1f}倍の{name}。無知なる者から賢者へ富が移転する、完璧な実例ですわ。",
                    f"感情でトレードするからこうなるのですわ。{name}（PER{per:.1f}倍）をこの価格で放置するなど、知性を疑わざるを得ません。",
                    f"市場は時として、ひどく近視眼的になりますわね。PER{per:.1f}倍の{name}。短期のノイズに怯える羊たちを尻目に、悠然と買い集めるだけです。",
                    f"アルゴリズムは決して嘘をつきません。嘘をつくのは常に、群集心理に流された市場の価格付け（{name}、PER{per:.1f}倍）のほうですわ。",
                    f"シャープレシオの最適化において、{name}（PER{per:.1f}倍）の組み入れは絶対条件ですわ。このリスク・リターン比率、芸術的とすら言えます。",
                    f"モンテカルロ・シミュレーションを1万回実行いたしました。PER{per:.1f}倍の{name}に投資して損失を被る確率は、統計上の誤差レベルですわ。",
                    f"割引キャッシュフロー（DCF）法による算出結果と、現在の株価（PER{per:.1f}倍）との凄まじい乖離。{name}はまさに、財務理論が証明する『買い』ですわ。",
                    f"わたくしのディープラーニング・モデルが導き出した最適解。それがPER{per:.1f}倍の{name}ですわ。数理的根拠に反論の余地はありません。",
                    f"資本コスト（WACC）を考慮しても、{name}（PER{per:.1f}倍）の超過収益力は際立っておりますわ。エレガントな資産運用には欠かせない銘柄です。",
                    f"ボラティリティの波の底に隠された、真珠のような銘柄ですわ。PER{per:.1f}倍の{name}。ポートフォリオの期待利回りを、優雅に底上げしてくれます。",
                    f"バリュエーションの多変量解析を完了。{name}（PER{per:.1f}倍）は、全てのベクトルにおいて「著しい割安」という同一の結論を指し示しておりますわ。",
                    f"財務レバレッジと収益性のバランスが絶妙ですわ。その上でPER{per:.1f}倍。{name}の経営陣の資本配分の美しさには、敬意を表します。",
                    f"相関係数のマトリクスを見ても、{name}（PER{per:.1f}倍）の独立した値動きは魅力的ですわ。分散投資の観点から、完璧なピースと言えます。"
                ]
            elif 12 < per <= 25:
                options = [
                    f"{name}の財務データを確認いたしましたわ。PERは{per:.1f}倍と適正な水準。極端な割安感はありませんが、堅実な事業基盤が下値を支える、リスクリターンのバランスが取れた銘柄ですわ。",
                    f"現在の{name}のPERは{per:.1f}倍。アルゴリズムの解析では、概ね適正価格の範囲内ですわね。突発的なボラティリティは低く、ポートフォリオの安定剤として機能するはずです。",
                    f"市場は{name}（PER{per:.1f}倍）を冷静に評価しておりますわ。しかし、わたくしのモデルによれば内部留保や資本効率にまだ改善の余地があり、隠れた上昇余地を見込んでおります。",
                    f"PER{per:.1f}倍。{name}は市場平均とほぼ同等の評価を受けておりますわ。無理なプレミアムを支払わずとも保有できる優良資産です。",
                    f"突出した割安感はありませんが（PER{per:.1f}倍）、{name}の利益成長の確度を考慮すれば、十分に妥当なプライシングと推察いたします。",
                    f"データは嘘をつきませんわ。{name}のPER{per:.1f}倍は、現在の収益力を正確に反映したフェアバリュー。長期的な保有に適しております。",
                    f"リスクとリターンの均衡が保たれていますわ。PER{per:.1f}倍の{name}。ポートフォリオのコアとして、安定したパフォーマンスが期待できます。",
                    f"アルゴリズムの算出結果、{name}（PER{per:.1f}倍）はニュートラルゾーンに位置しますわ。業績の上振れがあれば、一気に上方ブレイクするでしょう。",
                    f"市場の適正なコンセンサスが形成されておりますわ（PER{per:.1f}倍）。{name}の今後のカタリストに注目しつつ、着実なリターンを狙うべきです。",
                    f"派手なキャピタルゲインは望めないかもしれませんが（PER{per:.1f}倍）、{name}の堅牢なバランスシートは、暴落時の見事な防波堤になりますわ。",
                    f"退屈な銘柄に見えますか？PER{per:.1f}倍の{name}。しかし、複利の魔法を最大限に活かすのは、こうしたボラティリティの低い安定資産なのですわ。",
                    f"ポートフォリオのアンカー（錨）として、{name}（PER{per:.1f}倍）の組み入れを推奨いたしますわ。リスク許容度を下げるための、極めて理知的な選択です。",
                    f"市場の乱高下に一喜一憂したくないのであれば、{name}（PER{per:.1f}倍）を選ぶことですわ。わたくしの計算では、ベータ値が極めて穏やかです。",
                    f"安定した配当と自社株買いのトラックレコード。PER{per:.1f}倍の{name}は、株主還元という点において非常に高いスコアを叩き出しておりますわ。",
                    f"景気循環の波に左右されにくい、強固なビジネスモデルですわ。{name}（PER{per:.1f}倍）は、いわゆる『ディフェンシブ・ストック』の模範解答と言えます。",
                    f"夜、安らかに眠りたいのであれば{name}（PER{per:.1f}倍）を買うことですわ。感情のブレを起こさない、機械的な資産形成の第一歩です。",
                    f"わたくしのストレステスト（暴落シミュレーション）においても、{name}（PER{per:.1f}倍）の下落耐性は群を抜いておりますわ。優秀な盾です。",
                    f"インデックスを確実にアウトパフォームするためのベースキャンプ。それがPER{per:.1f}倍の{name}ですわ。地味ですが、確実な一歩です。",
                    f"一見すると平凡なPER{per:.1f}倍ですが、{name}の持つ特許群の価値は、まだ株価に完全には織り込まれておりませんわ。わたくしの独自解析です。",
                    f"市場は{name}の持続的成長率（サステナブル・グロース・レート）を過小評価していますわ（PER{per:.1f}倍）。数年後、この価格はバーゲンだったと気づくでしょう。",
                    f"PER{per:.1f}倍。表面的な数字は適正ですが、{name}の業界内シェアの推移データを分析すると、価格支配力を強めつつある兆候が見られますわ。",
                    f"ESGスコアの高さやガバナンスの透明性。{name}（PER{per:.1f}倍）のこうした非財務情報（インタンジブルズ）は、機関投資家の長期資金を必ず呼び込みますわ。",
                    f"わたくしのモデルは、{name}（PER{per:.1f}倍）の資本コストが今後低下していくと予測しております。それは即ち、企業価値の緩やかな上昇を意味しますわ。",
                    f"平凡なバリュエーション（PER{per:.1f}倍）の裏に隠された、強固なフランチャイズ価値。{name}の真の姿は、単純なスクリーニングでは見えませんわ。",
                    f"サプライチェーンの強靭さにおいて、{name}（PER{per:.1f}倍）のデータは突出しておりますわ。地政学リスクの高まる現代において、これは大きなプレミアムです。",
                    f"キャッシュの創出力（フリーキャッシュフロー・マージン）を見れば、{name}のPER{per:.1f}倍はむしろ安く見えてきますわ。会計上の利益に騙されてはいけません。",
                    f"業界再編の波が起きた時、{name}（PER{per:.1f}倍）は買収側にも被買収側にもなれる絶妙なポジショニングにありますわ。オプション価値が高い銘柄です。"
                ]
            else:
                if per > 100 or per <= 0:
                    options = [
                        f"{name}の現在の利益ベースでは、PERによる単純比較はノイズになりますわね。しかし、PBRやキャッシュフローの観点から見れば、現在の株価位置は十分に合理的な範囲内だと算出されておりますわ。",
                        f"見かけのPER数値は異常値を示しておりますが、エラーではありません。{name}が抱える無形資産や今後の事業フェーズを考慮すれば、十分に投資適格という推論結果が出ましたわ。",
                        f"見かけ上のPER（{per:.1f}倍）に惑わされてはいけませんわ。{name}の評価には、別のマルチプル指標を用いるのがクオンツの定石です。",
                        f"利益ベースの評価モデルが機能しないフェーズですわね。しかし、{name}の売上モメンタムと市場シェアを考慮すれば、投資価値は十分に存在します。",
                        f"PERの異常値（{per:.1f}倍）は、会計上のノイズに過ぎませんわ。{name}の真のエンタープライズ価値は、わたくしの計算ではもっと高位にあります。",
                        f"赤字、あるいは極端な高PER（{per:.1f}倍）ですが、{name}は先行投資期にあります。フリーキャッシュフローの改善トレンドを見れば、懸念には及びませんわ。",
                        f"一時的な特損や減価償却費の負担が、{name}のPERを{per:.1f}倍という異常値に歪めておりますわ。EBITDAベースで再計算すれば、全く違う景色が見えます。",
                        f"素人はこのPER（{per:.1f}倍）を見て逃げ出すでしょう。しかし{name}のバランスシートに隠された含み益を評価モデルに組み込めば、立派なバリュー株ですわ。",
                        f"税効果会計やのれんの償却。そうした会計マジックを全て剥ぎ取った時、{name}（PER{per:.1f}倍）の真の収益力が姿を現しますわ。アルゴリズムは欺けません。",
                        f"現在の{name}は利益を追求するフェーズではありませんわ（PER{per:.1f}倍）。トップライン（売上）の拡大こそが至上命題。アマゾンの初期と同じ軌跡です。",
                        f"PER{per:.1f}倍。既存のバリュエーション枠組みが通用しない、破壊的イノベーション企業（{name}）の証左ですわ。これこそが未来へのプレミアムです。",
                        f"研究開発費への莫大な投資が、{name}の当期純利益を押し潰しておりますわ（PER{per:.1f}倍）。しかし、これは未来の莫大なキャッシュフローへの種蒔きです。",
                        f"利益が出ない（PER{per:.1f}倍）のは、顧客獲得コスト（CAC）に全力で資本を投下しているからですわ。{name}のLTV（顧客生涯価値）を計算すれば、この投資は完全にペイします。",
                        f"プラットフォームの覇権を握るまで、{name}に利益など不要ですわ（PER{per:.1f}倍）。ネットワーク効果が臨界点を超えた時、このバリュエーションは正当化されます。",
                        f"従来のPER基準で{name}（{per:.1f}倍）を測るのは、馬車でフェラーリの速度を測るようなものですわ。新しい時代には、新しい評価尺度が求められます。"
                    ]
                else:
                    options = [
                        f"{name}のPERは{per:.1f}倍と、指標面ではプレミアム価格がついておりますわ。しかし、これは未来の利益を見越した市場のコンセンサス。データが示す成長軌道を信じるべき局面ですわね。",
                        f"PERの数値（{per:.1f}倍）のみを見れば警戒水域ですが、{name}の無形資産や市場シェアをスコアリングに加味すると、この株価でも十分に投資適格という推論結果が出ましたわ。",
                        f"PER{per:.1f}倍という数値は一見すると割高ですが、{name}の利益成長率で割り引けば（PEGレシオ）、十分に正当化されるバリュエーションですわ。",
                        f"市場は{name}に対して強い期待を寄せておりますわね（PER{per:.1f}倍）。モメンタム投資の観点からは、このプレミアムに乗るのも一つの合理的な戦略です。",
                        f"高PER（{per:.1f}倍）銘柄特有のボラティリティには注意が必要ですが、{name}の強固な競争優位性を加味すれば、わたくしのモデルは保有を許容しますわ。",
                        f"バリュー投資家は敬遠する数値（PER{per:.1f}倍）ですが、{name}のイノベーションの価値を静的な指標だけで測るべきではありませんわ。",
                        f"優れた企業にはプレミアム価格（PER{per:.1f}倍）を支払う。ウォーレン・バフェットも実践する、極めて理にかなった投資戦略ですわ。{name}はその資格があります。",
                        f"わたくしのDCFモデルでは、{name}のPER{per:.1f}倍は今後5年間の利益成長によって完全に吸収され、適正水準に収斂していくと計算されておりますわ。",
                        f"高PER（{per:.1f}倍）は、市場の期待値のハードルの高さを示しますわ。{name}の経営陣なら、その高いハードルすらも優雅に飛び越えてみせると、データが裏付けております。",
                        f"完全にテーマ株の熱狂に包まれておりますわね（{name}、PER{per:.1f}倍）。ファンダメンタルズを無視したモメンタム相場ですが、トレンドフォローのアルゴリズムなら乗るのが正解です。",
                        f"大衆の熱狂が、{name}の株価をPER{per:.1f}倍まで押し上げましたわ。バブルと呼ぶのは簡単ですが、バブルの中で踊りながら利益を抜くのが真のクオンツというものです。",
                        f"需給バランスが完全に崩れておりますわ（{name}、PER{per:.1f}倍）。売り手が枯渇した状態でのプラチナチケット化。需給モメンタムに従い、買いを推奨いたしますわ。"
                    ]
            text = random.choice(options)
            
        emergency_hints.append(text + " *(System)*")
        
    return emergency_hints

def generate_ai_summary(results, selected_ticker):
    # ★ エコモードならAI総括を静かに省略
    if not st.session_state.use_ai or not model: return None
    
    player_res = next(r for r in results if r['ticker'] == selected_ticker)
    winner = results[0]
    
    log_details = ""
    if player_res['logs']:
        for log in player_res['logs']:
            log_details += f"- {log['日付']}: {log['アクション']} (株価:{log['価格']}円 / 理由:{log['理由']})\n"
    else:
        log_details = "期間中の売買取引なし（一度も買いシグナルが点灯しませんでした）"
        
    persona = random.choice(ROLES)
    
    prompt = f"""
    あなたは株式投資ゲームのプロの辛口ナビゲーターです。シミュレーションが完了しました。
    他の銘柄の話や一般論は完全に排除し、プレイヤーが【実際に選択した銘柄の結果と、その日々の売買ログ】だけを冷徹にディープ分析し、踏み込んだ厳しい解説（約200〜250文字）を作成してください。

    【あなたのキャラクター設定】
    {persona['desc']}

    【プレイヤーが選択した銘柄のシミュレーションデータ】
    ・銘柄名: {player_res['name']} ({player_res['ticker']})
    ・最終損益: {int(player_res['profit'])}円 (初期資金100万円に対して最終資産は {int(player_res['final_value'])}円)
    ・順位: 3銘柄中 {results.index(player_res) + 1}位

    【実際の売買ログ（事実データ）】
    {log_details}

    【絶対ルール】
    1. 必ず指定されたキャラクターの口調を完璧に維持すること。
    2. 一般論は一切禁止。
    3. 売買ログで起きた事実（例：「ハードストップで致命傷を負った」「RSI過熱で早漏利確した」「ATRトレーリングが機能してトレンドを絞り尽くした」など）に具体的に言及し、なぜこの損益に終わったのか、アルゴリズムの動きの観点から厳しくぶった斬ること。
    4. プレーンテキストのみで出力。
    """
    try:
        response = model.generate_content(prompt)
        if response.parts:
            return {"avatar": persona['avatar'], "text": response.text.strip()}
    except Exception:
        return None

def run_algorithm_simulation(ticker):
    stock = yf.Ticker(ticker)
    df = stock.history(period="1y", interval="1d")
    df.index = df.index.tz_localize(None)
    
    df['SMA25'] = df['Close'].rolling(window=25).mean()
    diff = df['Close'].diff()
    up, down = diff.clip(lower=0), -1 * diff.clip(upper=0)
    df['RSI'] = 100 - (100 / (1 + (up.rolling(14).mean() / down.rolling(14).mean())))
    df['MACD'] = df['Close'].ewm(span=12, adjust=False).mean() - df['Close'].ewm(span=26, adjust=False).mean()
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    
    df['TR1'] = df['High'] - df['Low']
    df['TR2'] = abs(df['High'] - df['Close'].shift(1))
    df['TR3'] = abs(df['Low'] - df['Close'].shift(1))
    df['TR'] = df[['TR1', 'TR2', 'TR3']].max(axis=1)
    df['ATR'] = df['TR'].rolling(window=14).mean()
    
    df['Score'] = 0
    df.loc[df['RSI'] <= 45, 'Score'] += 1
    df.loc[df['MACD'] > df['Signal'], 'Score'] += 1
    df.loc[df['Close'] > df['SMA25'], 'Score'] += 1
        
    sim_df = df.tail(90).copy()
    cash = 1000000
    holding_shares = 0
    buy_price = 0
    highest_price_since_buy = 0
    portfolio_values = []
    trade_count = 0
    trade_logs = []
    
    for date, row in sim_df.iterrows():
        price = row['Close']
        score = row['Score']
        current_rsi = row['RSI']
        current_atr = row['ATR']
        date_str = date.strftime('%Y-%m-%d')
        
        if holding_shares > 0:
            highest_price_since_buy = max(highest_price_since_buy, price)
            hard_stop_price = buy_price * 0.90
            trailing_stop_price = highest_price_since_buy - (current_atr * 2.5)
            
            if price <= hard_stop_price:
                cash = holding_shares * price
                holding_shares = 0
                trade_count += 1
                trade_logs.append({"日付": date_str, "アクション": "💀 強制損切", "価格": int(price), "理由": "ハードストップ発動 (買値から-10%)"})
            elif current_rsi >= 80:
                cash = holding_shares * price
                holding_shares = 0
                trade_count += 1
                trade_logs.append({"日付": date_str, "アクション": "🔥 緊急利確", "価格": int(price), "理由": f"RSI過熱({int(current_rsi)}%)・バブル天井回避"})
            elif price <= trailing_stop_price:
                cash = holding_shares * price
                holding_shares = 0
                trade_count += 1
                if price >= buy_price:
                    trade_logs.append({"日付": date_str, "アクション": "✨ 利益確定", "価格": int(price), "理由": "ATRトレーリング (トレンド終了追従)"})
                else:
                    trade_logs.append({"日付": date_str, "アクション": "🛡️ 微損撤退", "価格": int(price), "理由": "ATRトレーリング (ノイズ判定)"})
            elif score < 1:
                cash = holding_shares * price
                holding_shares = 0
                trade_count += 1
                trade_logs.append({"日付": date_str, "アクション": "🟡 トレンド消滅", "価格": int(price), "理由": "買いシグナル完全消失による撤退"})
                
        elif holding_shares == 0:
            if score >= 2:
                holding_shares = cash // price
                cash -= holding_shares * price
                buy_price = price
                highest_price_since_buy = price
                trade_count += 1
                trade_logs.append({"日付": date_str, "アクション": "🔴 買 (BUY)", "価格": int(price), "理由": "複数シグナル点灯 (トレンド発生)"})
                
        total_value = cash + (holding_shares * price)
        portfolio_values.append(total_value)
        
    return {
        "final_value": portfolio_values[-1],
        "profit": portfolio_values[-1] - 1000000,
        "history": portfolio_values,
        "dates": sim_df.index,
        "trade_count": trade_count // 2,
        "logs": trade_logs
    }

def reset_and_scan(target_rsi, target_growth, target_per, use_ai):
    st.session_state.hints = {}
    st.session_state.selected_ticker = None
    st.session_state.use_ai = use_ai
    st.session_state.game_stage = "select"
    with st.spinner("最新のデータベースから市場をスキャン中..."):
        st.session_state.screened_candidates = scan_market(target_rsi, target_growth, target_per)

def start_simulation(ticker):
    st.session_state.selected_ticker = ticker
    st.session_state.game_stage = "result"

def goto_config():
    st.session_state.game_stage = "config"

def reset_to_start():
    st.session_state.hints = {}
    st.session_state.selected_ticker = None
    st.session_state.screened_candidates = []
    st.session_state.game_stage = "config"

def show_glossary():
    with st.expander("👑 投資システム・アルゴリズムの解説（クリックで開閉）"):
        st.markdown("""
        **当システムは、素人のような「一律〇％で利確・損切」といった旧時代的なルールは使用しません。プロの機関投資家やヘッジファンドが実際に稼働させている【多層的・動的エグジットアルゴリズム】を搭載し、相場から利益を徹底的に搾り取ります。**

        **【エグジット（決済）アルゴリズムの3つの絶対防衛線】**
        * **✨ ATRトレーリングストップ (トレンド追従)**：株価が上昇するにつれて、決済ラインを自動で引き上げていく魔法のロジックです。銘柄固有の値動きの激しさ（ATR）を計算し、「ノイズでは売らないが、トレンドが終わったら確実に狩る」という絶妙な位置に網を張り続けます。これにより、利益は青天井に伸びていきます。
        * **🔥 RSI過熱判定 (緊急利確)**：株価がバブル化し、大衆が熱狂して買い上げている瞬間（RSI 80%超え）を検知します。トレーリングストップのラインまで落ちてくるのを待たず、天井付近で即座に利益を確定させて暴落から逃げ切ります。
        * **💀 ハードストップ (強制損切)**：悪材料による予期せぬ暴落時、買値から-10%を割った瞬間に発動する命綱です。システムトレードにおいて「一回の致命傷を避ける」ことは、勝率を上げる以上に重要です。
        """)

# ==========================================
# 4. UI 描画（完全な3画面遷移設計）
# ==========================================

# ------------------------------------------
# Stage 1: 設定画面 (Config)
# ------------------------------------------
if st.session_state.game_stage == "config":
    # ★ タイトルの描画を「Config画面（最初の画面）」のブロック内だけに限定
    st.markdown("<h1>⚡株simulator ～もし90日前に買ってたら～</h1>", unsafe_allow_html=True)
    
    st.subheader(f"〜 90日前（{past_90_str}）から、本日（{today_str}）までの値動きを予測せよ 〜")
    st.write(f"システムは **{past_90_str}** の時点で時間を止め、全市場から有望な銘柄を抽出します。ここから **本日（{today_str}）** までの90日間の相場で、最も利益を叩き出す銘柄はどれか選択してください！")

    st.write("---")
    st.markdown("#### 🔍 スキャン条件の設定")
    scan_mode = st.radio("スキャン方式", ["✨ おまかせスキャン（AI自動最適化）", "⚙️ こだわりスキャン（インジケーター手動調整）"], horizontal=True)
    
    target_rsi, target_growth, target_per = 45, 10, 15
    
    if scan_mode == "⚙️ こだわりスキャン（インジケーター手動調整）":
        col_t, col_g, col_v = st.columns(3)
        with col_t: target_rsi = st.slider("🥷 RSI上限 (売られすぎ基準)", min_value=10, max_value=80, value=40, step=5)
        with col_g: target_growth = st.slider("🧑‍🎤 売上成長率下限 (%)", min_value=0, max_value=50, value=10, step=5)
        with col_v: target_per = st.slider("👩‍💼 PER上限 (割安基準)", min_value=5, max_value=50, value=15, step=1)
    
    show_glossary()
    
    st.write("") # スペーサー
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        st.button(
            "✨ AIの解説付きで市場をスキャン (APIキー消費)", 
            type="primary", 
            use_container_width=True,
            on_click=reset_and_scan,
            args=(target_rsi, target_growth, target_per, True)
        )
    with col_btn2:
        st.button(
            "⚡ エコモードで高速スキャン (キー消費ゼロ)", 
            type="secondary", 
            use_container_width=True,
            on_click=reset_and_scan,
            args=(target_rsi, target_growth, target_per, False)
        )
# ------------------------------------------
# Stage 2: 候補選択画面 (Select)
# ------------------------------------------
elif st.session_state.game_stage == "select":
    st.subheader("🎯 抽出完了：未来の勝ち組を選択してください")
    
    # 戻る（再設定）ボタンをトップに配置し、スマホでも見失わないようにする
    st.button("↩️ 条件を変えて再スキャンする（設定画面に戻る）", on_click=goto_config, use_container_width=True)

    if st.session_state.screened_candidates:
        st.write("---")
        if not st.session_state.hints:
            msg = "抽出結果に基づき、AIナビゲーターが分析レポートを作成中..." if st.session_state.use_ai else "内蔵の予備システムが銘柄データを高速解析中..."
            with st.spinner(msg):
                hints_list = generate_all_hints(st.session_state.screened_candidates)
                for i, cand in enumerate(st.session_state.screened_candidates):
                    st.session_state.hints[cand["data"]["ticker"]] = hints_list[i]
                    
        cols = st.columns(3)
        for i, cand in enumerate(st.session_state.screened_candidates):
            role = cand["role"]
            data = cand["data"]
            ticker = data["ticker"]
            name = data["name"]
            chart_data = data["chart_data"]
            
            with cols[i]:
                st.markdown(f"**【{role['type']}抽出】**")
                st.markdown(f"### 🏢 {name}")
                st.caption(f"`{ticker}`")
                
                st.line_chart(chart_data['Close'], height=150)
                st.markdown(f"<div class='avatar-container'>{role['avatar']}</div>", unsafe_allow_html=True)
                st.info(st.session_state.hints.get(ticker, "解析中..."))
                
                st.write("")
                st.button(
                 f"{name} を選択してシミュレート", 
                key=f"btn_{ticker}", 
                use_container_width=True,
                on_click=start_simulation,
                args=(ticker,) 
                )

# ------------------------------------------
# Stage 3: 結果発表画面 (Result)
# ------------------------------------------
elif st.session_state.game_stage == "result":
    st.components.v1.html("<script>window.parent.document.querySelector('.main').scrollTo(0, 0);</script>", height=0)
    st.subheader("🏁 自動売買シミュレーション 結果発表 (下のＡＩ総括も見てね)")
    st.markdown(f"**【対象期間】 {past_90_str} 〜 本日（{today_str}）**")
    
    with st.spinner("アルゴリズムが市場で戦っています..."):
        results = []
        chart_df = pd.DataFrame()
        
        for cand in st.session_state.screened_candidates:
            ticker = cand["data"]["ticker"]
            name = cand["data"]["name"]
            sim_result = run_algorithm_simulation(ticker)
            sim_result['ticker'] = ticker
            sim_result['name'] = name
            sim_result['type'] = cand["role"]["type"]
            results.append(sim_result)
            
            temp_df = pd.DataFrame({name: sim_result['history']}, index=sim_result['dates'])
            if chart_df.empty:
                chart_df = temp_df
            else:
                chart_df = chart_df.join(temp_df, how='outer')
                
        results.sort(key=lambda x: x['final_value'], reverse=True)
        player_rank = next(i for i, r in enumerate(results) if r['ticker'] == st.session_state.selected_ticker) + 1
        
    st.write("---")
    
    selected_name = next(r['name'] for r in results if r['ticker'] == st.session_state.selected_ticker)
    
    if player_rank == 1:
        st.balloons()
        st.success(f"## 🎉 お見事！\n### あなたの選んだ **{selected_name}** が見事1位に輝きました！")
    elif player_rank == 2:
        st.info(f"## 👍 惜しい！\n### あなたの選んだ **{selected_name}** は2位でした。")
    else:
        st.error(f"## 📉 残念...\n### あなたの選んだ **{selected_name}** は最下位でした。")

    st.markdown("#### 📊 3部門の資産推移グラフ（初期資金: 1,000,000円）")
    st.line_chart(chart_df, height=300)

    st.markdown("#### 🏆 最終成績ランキング")
    cols = st.columns(3)
    
    for i, res in enumerate(results):
        with cols[i]:
            medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉"
            st.markdown(f"### {medal} 第{i+1}位")
            st.markdown(f"**{res['name']}**")
            st.caption(f"({res['type']})")
            
            profit_color = "normal" if res['profit'] == 0 else "off" if res['profit'] < 0 else "inverse"
            st.metric(
                label="最終資産額",
                value=f"¥ {int(res['final_value']):,}",
                delta=f"¥ {int(res['profit']):,}",
                delta_color=profit_color
            )

    st.write("---")
    st.markdown("#### 📝 アルゴリズムの売買ログ（詳細履歴）")
    
    tab_names = [res['name'] for res in results]
    tabs = st.tabs(tab_names)
    
    for i, tab in enumerate(tabs):
        with tab:
            logs = results[i]["logs"]
            if not logs:
                st.write("※この期間、アルゴリズムの買い条件を満たす日はありませんでした。")
            else:
                log_df = pd.DataFrame(logs)
                st.dataframe(log_df, use_container_width=True, hide_index=True)

    if st.session_state.use_ai:
        st.write("---")
        st.markdown("#### 🤖 AIナビゲーターによる個別戦略分析（辛口総括）")
        with st.spinner("AIがあなたの選択した銘柄のトレード履歴をディープ分析中..."):
            summary = generate_ai_summary(results, st.session_state.selected_ticker)
            if summary:
                st.markdown(f"<div class='avatar-container' style='width: 80px; height: 80px; font-size: 45px; line-height: 80px; margin-bottom: 10px;'>{summary['avatar']}</div>", unsafe_allow_html=True)
                st.info(summary['text'])
            else:
                st.write("（通信エラーのため、AIの個別戦略分析は省略されました）")

    st.write("---")
    # if文と st.rerun() を削除し、on_click引数に reset_to_start 関数を渡します
    st.button("↩️ 最初の設定画面に戻る（新しくゲームを始める）", on_click=reset_to_start, use_container_width=True)
