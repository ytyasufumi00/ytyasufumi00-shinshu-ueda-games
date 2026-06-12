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
st.set_page_config(page_title="QUANTUM TRADER | AIアルゴリズム・コロシアム", layout="wide")

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
    {"type": "割安・ファンダ重視", "avatar": "👩‍💼", "desc": "冷徹で理知的な女性クオンツAI（敬語で丁寧だが、データ至上主義で少し冷たい。「〜と推察されますわ」「感情はノイズ」などを用い、PERの低さなど堅実な財務指標を冷静に評価する）"}
]

if "screened_candidates" not in st.session_state: st.session_state.screened_candidates = []
if "hints" not in st.session_state: st.session_state.hints = {}
if "game_stage" not in st.session_state: st.session_state.game_stage = "select"
if "selected_ticker" not in st.session_state: st.session_state.selected_ticker = None
if "use_ai" not in st.session_state: st.session_state.use_ai = True

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
    sample_tickers = random.sample(list(MARKET_UNIVERSE.keys()), 50)
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
                options = [f"拙者が見立てるに、{name}のRSIは{rsi:.1f}%と完全に売られすぎの領域。反発の機は熟した。チャートの歪みに潜伏し、大口に便乗して仕掛ける刻（とき）だ！", f"血の匂いがするな。{name}のRSIは{rsi:.1f}%。狼狽売りの極みよ。大衆が恐怖に駆られる今こそ、暗闇から刃を振り下ろす絶好の好機！", f"見事な『陰』の極み。RSI{rsi:.1f}%の{name}は、まさに身を屈めた底値圏。ここからの跳躍は凄まじいものになろう。いざ、出陣！", f"底なし沼に見えるか？否。{name}のRSI{rsi:.1f}%は、反撃の狼煙を上げる直前の静寂。恐れず踏み込むべし。", f"これほどの『陰』、久しく見ておらぬ。RSI{rsi:.1f}%の{name}、底値の気配が濃厚じゃ。密かに陣を敷け！", f"限界突破の売り。{name}（RSI{rsi:.1f}%）のチャートに、逆転の秘術を仕込む。ここからの反発、見事なものになるぞ。", f"大衆は絶望しておるが、拙者の眼は欺けぬ。RSI{rsi:.1f}%の{name}は、水面下で逆襲のエネルギーを凝縮しておるわ。", f"まさに落下するナイフ。だが拙者には掴める。{name}（RSI{rsi:.1f}%）の反発力、とくと味わうが良い。", f"凍てつくような暴落チャート。だが、{name}のRSI{rsi:.1f}%はマグマが噴出する寸前の地熱を感じさせる。仕込みの刻じゃ。", f"誰もが背を向ける{name}。しかしRSI{rsi:.1f}%の数字は、敵の陣形が完全に崩壊したことを示しておる。切り込むは今！"]
            elif rsi <= 55:
                options = [f"現在の{name}、RSIは{rsi:.1f}%。まだ決定的な陽動のサインは出ておらぬが、底打ちは近い。兵糧を蓄えつつ、トレンド転換を狙い撃つべし！", f"チャートの息遣いが聞こえるか？{name}（RSI{rsi:.1f}%）は力を溜めている最中。焦る必要はない、忍びの如く息を殺して機をうかがえ。", f"相場が迷っておるな。{name}のRSIは{rsi:.1f}%。今は無闇に動かず、次のトレンドの兆しを待つのが上策。", f"今は力を溜める刻（とき）。{name}（RSI{rsi:.1f}%）のチャートは、次なる跳躍のための助走期間と見ゆる。", f"焦りは禁物じゃ。RSI{rsi:.1f}%の{name}、まだ大口の意図が見えぬ。気配を探りつつ、刀は鞘に収めておけ。", f"中庸の構え。{name}のRSIは{rsi:.1f}%。天に昇るか地へ落ちるか、五分五分の均衡。抜刀の瞬間を誤るでないぞ。", f"動きが遅いと侮るなかれ。{name}（RSI{rsi:.1f}%）は陣形を整えておる最中。ここで仕込むのが、後々の大勝利へと繋がるのよ。", f"一進一退の攻防。RSI{rsi:.1f}%の{name}。相場全体の視線が逸れている今こそ、密かに忍び寄る絶好のタイミングとも言えるな。", f"静かなる水面下で、大口が密かに集めておる気配あり。RSI{rsi:.1f}%の{name}、嵐の前の静けさよ。伏兵を配置し、シグナルを待て。", f"騙しの罠（陽動）が潜んでおるな。{name}のRSI{rsi:.1f}%は綺麗すぎる。大口が小口を嵌めるための偽の平穏かもしれぬ、凝視せよ。"]
            else:
                options = [f"すでに火蓋は切って落とされた！{name}のRSIは{rsi:.1f}%と上昇の気勢あり。流れには逆らわず、素早く順張りの陣形を敷くが吉！", f"力強い陽の波動を感じる。RSI{rsi:.1f}%の{name}は既に動意づいておる。高値掴みには警戒しつつも、この勢いに乗じて一気に攻め上れ！", f"上昇の波に乗れ！{name}のRSIは{rsi:.1f}%。このモメンタム、逆らうには惜しい勢いじゃ。", f"風は我らに吹いている。RSI{rsi:.1f}%の{name}、陽の波動がチャートを支配しておる。順張りで一気に押し通れ！", f"過熱には注意せねばならぬが、今はまだ攻めの刻。{name}（RSI{rsi:.1f}%）の勢い、天井を打つまで絞り尽くせ！", f"烈火のごとき上昇トレンド！{name}のRSI{rsi:.1f}%、これは本物の買いが集まっておる証拠。この大波、乗らねば一生の後悔ぞ！", f"昇龍の如きチャートよ。{name}のRSIは{rsi:.1f}%。天井がどこかなど、誰にも分からぬ。この荒ぶる龍の背に飛び乗る勇気はあるか？", f"嵐が吹き荒れておるな！{name}（RSI{rsi:.1f}%）の上昇は、小細工なしの圧倒的なパワープレイ。乗るなら今しかおじゃらん！", f"これぞ『火遁の術』。チャートが真っ赤に燃え上がっておるわ。{name}（RSI{rsi:.1f}%）の勢い、消えるまで全力追従じゃ！", f"光速のトレード。{name}（RSI{rsi:.1f}%）のチャートは一瞬の油断も許さぬ。この圧倒的な気流に、お主の直感を乗せてみよ！"]
            text = random.choice(options)
        elif "グロース" in role_type:
            if growth >= 15:
                options = [f"イェーイ！{name}の売上成長率は驚異の{growth:.1f}%！このアゲアゲなビートに乗るしかないっしょ！未来の爆発力は完全にプラチナディスク級だぜ！", f"最高にロックな数字が出たぜ！成長率{growth:.1f}%の{name}、この勢いはもう誰にも止められない！アンプのボリュームをMAXにしてフルスロットルでGOだ！", f"オーディエンスの熱狂が聞こえるか！？{name}の{growth:.1f}%という成長スピード、まさに時代を牽引するトップチャートの常連！今すぐチケット（株）を手に入れろ！", f"ヤバすぎる成長率{growth:.1f}%！{name}は今、インディーズから一気に世界的スターに駆け上がるフェーズだぜ！", f"この{growth:.1f}%って数字、アンプがぶっ壊れるレベルの熱量だろ！{name}の成長ストーリーにフルベットだ！", f"スーパーノヴァの誕生だ！{name}の売上が{growth:.1f}%も爆増してるって！？歴史的瞬間の目撃者になろうぜ！", f"超絶技巧のギターソロが炸裂中！{name}の{growth:.1f}%成長、このディストーションの効いた爆発力に魂が震えるぜ！", f"バスドラムが腹の底に響くような、強力な{growth:.1f}%成長！{name}のこの重低音ビート、相場のノイズを完全に掻き消してるな！", f"マイクスタンドを蹴り飛ばす勢い！{name}（成長率{growth:.1f}%）の強気なビジネスモデル、俺は完全にロックオンされたぜ！", f"プラチナチケット化する前に買っとけ！{name}の{growth:.1f}%成長、今ならまだ最前列を陣取れる最後のチャンスだぜ！"]
            elif growth >= 5:
                options = [f"今はちょっとテンポが心地よいミディアムナンバーってとこか？いやいや、{name}の成長率{growth:.1f}%は確かなグルーヴを刻んでるぜ！大化けの予感、ビンビン来てる！", f"堅実なビートダウンだ！{name}は{growth:.1f}%の成長でリズムをキープ中。こういうバンドがいきなりスタジアム級のアンセムを放つんだ、見逃すなよ！", f"良い感じのチューンに仕上がってきたな。成長率{growth:.1f}%の{name}、次の決算発表が極上のギターソロになるぜ！シートベルト締めて盛り上がろう！", f"派手さはないが、{name}の{growth:.1f}%成長はファンを裏切らない確かなクオリティだ。こういう株が後で化けるのさ！", f"ジワジワとチャートを駆け上がる{name}。成長率{growth:.1f}%のグルーヴに身を任せろ！サビはこれからだぜ！", f"今はまだBメロってところだな。{name}の{growth:.1f}%成長。ここから一気にサビで爆発する構成、俺には読めてるぜ！", f"MCでオーディエンスを温めてる最中さ。{name}（成長率{growth:.1f}%）。次の曲から一気にトップギアに入るから、目を離すなよ！", f"イントロのリフがめちゃくちゃキャッチーだ！{name}の成長率{growth:.1f}%、これは後に大ヒット間違いなしの予感がするぜ！", f"インディーズチャートをじわじわ登ってる！{name}の成長率{growth:.1f}%。メジャーデビューした瞬間に株価がどうなるか、ワクワクするだろ？", f"通好みの絶妙なコード進行だ。{name}の{growth:.1f}%成長。派手なだけのポップス（仕手株）にはない、確かな骨太さを感じるぜ。"]
            else:
                options = [f"今はバラードのターンか？{name}の成長率{growth:.1f}%は控えめだが、名曲ってのは静かなイントロから爆発するもんだろ？伝説のカムバックツアーに期待しようぜ！", f"少しノイズが混じってる（成長率{growth:.1f}%）が、ロックスターにスランプはつきものだ！{name}の真のポテンシャルが解放される瞬間、最前列でヘッドバンギングしようぜ！", f"成長率{growth:.1f}%？今はアンプのチューニング中さ。{name}が次のアルバムで世界を驚かせるのを待とうぜ！", f"少し静かすぎるか？だが{name}（成長率{growth:.1f}%）の底力を見くびるな。いきなりの転調で爆発するのがロックだ！", f"今はちょっとアンダーグラウンドに潜ってる時期（成長率{growth:.1f}%）。だが{name}のコアなファンは離れないぜ！", f"弦が切れたのか？いや、あえての無音（ブレイク）だ。{name}の成長率{growth:.1f}%。この静寂の後にくる轟音を楽しみに待とうぜ。", f"今はボーカルが喉を休めてる期間さ。{name}の{growth:.1f}%成長。次のツアー（決算）で復活のシャウトを響かせてくれると信じてるぜ！", f"機材トラブルで音が止まっちまったか？成長率{growth:.1f}%の{name}。だが、こういうハプニングこそがライブの醍醐味ってもんだろ！", f"ギターのチューニングが狂ってるみたいだな。{name}の{growth:.1f}%成長。だが、ノイズすらもアートに変えるのがロックの魔法だぜ！", f"今はインディーズに戻って原点回帰の期間さ。{name}の{growth:.1f}%成長。装飾を削ぎ落とした、むき出しのロックンロールを見せてくれ！"]
            text = random.choice(options)
        else:
            if 0 < per <= 12:
                options = [f"わたくしの推察によりますと、{name}のPERは{per:.1f}倍。業績に対して極端な割安水準に放置されておりますわ。市場の非合理的な感情ノイズを突く、期待値が極めて高い局面です。", f"明らかなバリュエーションの歪みを検知いたしましたわ。PERわずか{per:.1f}倍の{name}。感情を排したデータ至上主義の観点から、強く買いを推奨できる美しい数値です。", f"データが示しておりますわ。PER{per:.1f}倍の{name}は、市場の非効率性が生んだ奇跡的なディスカウント状態です。", f"ファンダメンタルズと株価の乖離が顕著ですわね。{name}のPER{per:.1f}倍という数値、合理的な投資家なら見逃せませんわ。", f"感情を排して数字を見れば一目瞭然ですわ。{name}のPER{per:.1f}倍。市場がこの歪みに気付く前に、静かにポジションを構築すべきです。", f"愚かな大衆は気付いておりませんわね。{name}のPERが{per:.1f}倍であるという、この至極明白な宝の山に。", f"市場参加者の大半は、ニュースの見出ししか読めない動物ですわ。PER{per:.1f}倍の{name}。彼らがパニックで手放した優良資産、ありがたく頂戴いたしましょう。", f"ノイズに踊らされる市場の滑稽なこと。{name}（PER{per:.1f}倍）の実態価値を計算できない無能なマネーは、我々の利益の源泉ですわ。", f"シャープレシオの最適化において、{name}（PER{per:.1f}倍）の組み入れは絶対条件ですわ。このリスク・リターン比率、芸術的とすら言えます。", f"割引キャッシュフロー（DCF）法による算出結果と、現在の株価（PER{per:.1f}倍）との凄まじい乖離。{name}はまさに、財務理論が証明する『買い』ですわ。"]
            elif 12 < per <= 25:
                options = [f"{name}の財務データを確認いたしましたわ。PERは{per:.1f}倍と適正な水準。極端な割安感はありませんが、堅実な事業基盤が下値を支える、リスクリターンのバランスが取れた銘柄ですわ。", f"現在の{name}のPERは{per:.1f}倍。アルゴリズムの解析では、概ね適正価格の範囲内ですわね。突発的なボラティリティは低く、ポートフォリオの安定剤として機能するはずです。", f"市場は{name}（PER{per:.1f}倍）を冷静に評価しておりますわ。しかし、わたくしのモデルによれば内部留保や資本効率にまだ改善の余地があり、隠れた上昇余地を見込んでおります。", f"データは嘘をつきませんわ。{name}のPER{per:.1f}倍は、現在の収益力を正確に反映したフェアバリュー。長期的な保有に適しております。", f"リスクとリターンの均衡が保たれていますわ。PER{per:.1f}倍の{name}。ポートフォリオのコアとして、安定したパフォーマンスが期待できます。", f"派手なキャピタルゲインは望めないかもしれませんが（PER{per:.1f}倍）、{name}の堅牢なバランスシートは、暴落時の見事な防波堤になりますわ。", f"ポートフォリオのアンカー（錨）として、{name}（PER{per:.1f}倍）の組み入れを推奨いたしますわ。リスク許容度を下げるための、極めて理知的な選択です。", f"景気循環の波に左右されにくい、強固なビジネスモデルですわ。{name}（PER{per:.1f}倍）は、いわゆる『ディフェンシブ・ストック』の模範解答と言えます。", f"夜、安らかに眠りたいのであれば{name}（PER{per:.1f}倍）を買うことですわ。感情のブレを起こさない、機械的な資産形成の第一歩です。", f"ESGスコアの高さやガバナンスの透明性。{name}（PER{per:.1f}倍）のこうした非財務情報（インタンジブルズ）は、機関投資家の長期資金を必ず呼び込みますわ。"]
            else:
                if per > 100 or per <= 0:
                    options = [f"{name}の現在の利益ベースでは、PERによる単純比較はノイズになりますわね。しかし、PBRやキャッシュフローの観点から見れば、現在の株価位置は十分に合理的な範囲内だと算出されておりますわ。", f"見かけのPER数値は異常値を示しておりますが、エラーではありません。{name}が抱える無形資産や今後の事業フェーズを考慮すれば、十分に投資適格という推論結果が出ましたわ。", f"利益ベースの評価モデルが機能しないフェーズですわね。しかし、{name}の売上モメンタムと市場シェアを考慮すれば、投資価値は十分に存在します。", f"赤字、あるいは極端な高PER（{per:.1f}倍）ですが、{name}は先行投資期にあります。フリーキャッシュフローの改善トレンドを見れば、懸念には及びませんわ。", f"一時的な特損や減価償却費の負担が、{name}のPERを{per:.1f}倍という異常値に歪めておりますわ。EBITDAベースで再計算すれば、全く違う景色が見えます。", f"素人はこのPER（{per:.1f}倍）を見て逃げ出すでしょう。しかし{name}のバランスシートに隠された含み益を評価モデルに組み込めば、立派なバリュー株ですわ。", f"現在の{name}は利益を追求するフェーズではありませんわ（PER{per:.1f}倍）。トップライン（売上）の拡大こそが至上命題。アマゾンの初期と同じ軌跡です。", f"プラットフォームの覇権を握るまで、{name}に利益など不要ですわ（PER{per:.1f}倍）。ネットワーク効果が臨界点を超えた時、このバリュエーションは正当化されます。", f"従来のPER基準で{name}（{per:.1f}倍）を測るのは、馬車でフェラーリの速度を測るようなものですわ。新しい時代には、新しい評価尺度が求められます。"]
                else:
                    options = [f"{name}のPERは{per:.1f}倍と、指標面ではプレミアム価格がついておりますわ。しかし、これは未来の利益を見越した市場のコンセンサス。データが示す成長軌道を信じるべき局面ですわね。", f"PERの数値（{per:.1f}倍）のみを見れば警戒水域ですが、{name}の無形資産や市場シェアをスコアリングに加味すると、この株価でも十分に投資適格という推論結果が出ましたわ。", f"PER{per:.1f}倍という数値は一見すると割高ですが、{name}の利益成長率で割り引けば（PEGレシオ）、十分に正当化されるバリュエーションですわ。", f"市場は{name}に対して強い期待を寄せておりますわね（PER{per:.1f}倍）。モメンタム投資の観点からは、このプレミアムに乗るのも一つの合理的な戦略です。", f"高PER（{per:.1f}倍）銘柄特有のボラティリティには注意が必要ですが、{name}の強固な競争優位性を加味すれば、わたくしのモデルは保有を許容しますわ。", f"バリュー投資家は敬遠する数値（PER{per:.1f}倍）ですが、{name}のイノベーションの価値を静的な指標だけで測るべきではありませんわ。", f"優れた企業にはプレミアム価格（PER{per:.1f}倍）を支払う。ウォーレン・バフェットも実践する、極めて理にかなった投資戦略ですわ。{name}はその資格があります。", f"わたくしのDCFモデルでは、{name}のPER{per:.1f}倍は今後5年間の利益成長によって完全に吸収され、適正水準に収斂していくと計算されておりますわ。", f"完全にテーマ株の熱狂に包まれておりますわね（{name}、PER{per:.1f}倍）。ファンダメンタルズを無視したモメンタム相場ですが、トレンドフォローのアルゴリズムなら乗るのが正解です。", f"需給バランスが完全に崩れておりますわ（{name}、PER{per:.1f}倍）。売り手が枯渇した状態でのプラチナチケット化。需給モメンタムに従い、買いを推奨いたしますわ。"]
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

def reset_to_start():
    st.session_state.hints = {}
    st.session_state.selected_ticker = None
    st.session_state.screened_candidates = []
    st.session_state.game_stage = "select"

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
# 4. UI 描画
# ==========================================
st.markdown("<h1>⚡ QUANTUM TRADER : AI多層アルゴリズム・コロシアム</h1>", unsafe_allow_html=True)

if st.session_state.game_stage == "select":
    # ★コンテナマジック：レイアウトの定義順を操作して、ボタンを下側の設定値で動かす
    header_container = st.container()
    btn_container = st.container()
    settings_container = st.container()
    results_container = st.container()

    with header_container:
        st.subheader(f"〜 90日前（{past_90_str}）から、本日（{today_str}）までの値動きを予測せよ 〜")
        st.write(f"システムは **{past_90_str}** の時点で時間を止め、全市場から有望な銘柄を抽出します。ここから **本日（{today_str}）** までの90日間の相場で、最も利益を叩き出す銘柄はどれか選択してください！")

    # 1. まず設定項目を描画し、変数を取得（表示上はボタンの下になります）
    with settings_container:
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

    # 2. 次にボタンを描画（表示上は設定項目の上になりますが、取得済みの変数を使用できます）
    with btn_container:
        st.write("") # スペーサー
        col_btn1, col_btn2 = st.columns(2)
        if not st.session_state.screened_candidates:
            with col_btn1:
                if st.button("✨ AIの解説付きで市場をスキャン (APIキー消費)", type="primary", use_container_width=True):
                    reset_and_scan(target_rsi, target_growth, target_per, use_ai=True)
                    st.rerun()
            with col_btn2:
                if st.button("⚡ エコモードで高速スキャン (キー消費ゼロ)", type="secondary", use_container_width=True):
                    reset_and_scan(target_rsi, target_growth, target_per, use_ai=False)
                    st.rerun()
        else:
            with col_btn1:
                if st.button("🔄 AIの解説付きで再スキャン (APIキー消費)", type="primary", use_container_width=True):
                    reset_and_scan(target_rsi, target_growth, target_per, use_ai=True)
                    st.rerun()
            with col_btn2:
                if st.button("⚡ エコモードで高速再スキャン (キー消費ゼロ)", type="secondary", use_container_width=True):
                    reset_and_scan(target_rsi, target_growth, target_per, use_ai=False)
                    st.rerun()

    # 3. 最後に結果を描画
    with results_container:
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
                    if st.button(f"{name} を選択してシミュレート", key=f"btn_{ticker}", use_container_width=True):
                        st.session_state.selected_ticker = ticker
                        st.session_state.game_stage = "result"
                        st.rerun()

elif st.session_state.game_stage == "result":
    st.subheader("🏁 自動売買シミュレーション 結果発表")
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
        st.success(f"🎉 お見事！あなたの選んだ **{selected_name}** が見事1位に輝きました！")
    elif player_rank == 2:
        st.info(f"👍 惜しい！あなたの選んだ **{selected_name}** は2位でした。")
    else:
        st.error(f"📉 残念... あなたの選んだ **{selected_name}** は最下位でした。")

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
    
    show_glossary()
    
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
    if st.button("↩️ 最初の設定画面に戻る（新しくゲームを始める）", use_container_width=True):
        reset_to_start()
        st.rerun()