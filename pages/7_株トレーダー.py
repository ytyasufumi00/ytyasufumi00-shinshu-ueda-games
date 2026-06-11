import streamlit as st
import random
import yfinance as yf
import pandas as pd
import google.generativeai as genai

# ==========================================
# 1. 初期設定とAPIキーの自動読み込み
# ==========================================
st.set_page_config(page_title="AI株式トレードシミュレーター", layout="wide")

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception:
    pass

# キャラクターの個性が強く出るようにtemperatureを維持
model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"temperature": 0.85})

# ==========================================
# 2. 銘柄プールとセッション・キャラクター設定
# ==========================================
TICKER_POOL = {
    "7203.T": "トヨタ自動車",
    "6758.T": "ソニーグループ",
    "9984.T": "ソフトバンクグループ",
    "4385.T": "メルカリ",
    "7974.T": "任天堂",
    "6501.T": "日立製作所",
    "6062.T": "チャーム・ケア・コーポレーション",
    "4475.T": "HENNGE"
}

# アイコンに合わせて個性を再定義
PERSONAS = [
    {
        "avatar": "🥷", 
        "desc": "相場の裏を読む凄腕の忍（忍びの言葉使い。「潜伏」「陽動」「仕掛けの刻（とき）」などの言葉を使い、チャートの裏に潜む大口投資家の動きや気配を語る）"
    },
    {
        "avatar": "👩‍💼", 
        "desc": "冷徹で理知的な女性クオンツAI（敬語で丁寧だが、データ至上主義で少し冷たい印象。「〜と推察されますわ」「感情はノイズに過ぎません」「期待値は極めて高いですわね」などのお嬢様・クール系女性口調を使う）"
    },
    {
        "avatar": "🧑‍🎤", 
        "desc": "相場をライブ会場に変えるロックスター・トレーダー（ハイテンションで音楽的な比喩を使う。「ビートに乗れ！」「ノイズを切り裂くギターソロ！」「アゲアゲのチューン」などを使い熱狂的に語る）"
    }
]

if "current_tickers" not in st.session_state:
    st.session_state.current_tickers = random.sample(list(TICKER_POOL.keys()), 3)
if "hints" not in st.session_state:
    st.session_state.hints = {}
if "game_stage" not in st.session_state:
    st.session_state.game_stage = "select"
if "selected_ticker" not in st.session_state:
    st.session_state.selected_ticker = None

# ==========================================
# 3. データ処理・分析・一括生成関数
# ==========================================
@st.cache_data(show_spinner=False)
def get_90days_ago_data(ticker):
    """90日前時点でのデータを取得する"""
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="1y", interval="1d")
        df.index = df.index.tz_localize(None)
        
        # ターゲットを90日前に変更
        target_idx = -90
        if len(df) < abs(target_idx):
            return None, None
            
        past_df = df.iloc[:len(df) + target_idx].copy()
        
        diff = past_df['Close'].diff()
        up, down = diff.clip(lower=0), -1 * diff.clip(upper=0)
        rsi = 100 - (100 / (1 + (up.rolling(14).mean().iloc[-1] / down.rolling(14).mean().iloc[-1])))
        
        info = stock.info
        per = info.get('trailingPE', 999)
        peg = info.get('pegRatio', 999)
        rev_growth = info.get('revenueGrowth', 0) or 0
        
        metrics = {"rsi": rsi, "per": per, "peg": peg, "growth": rev_growth * 100}
        
        # 90日前の時点から見た、さらに過去90日分のチャートデータを返す
        return metrics, past_df.tail(90)
    except:
        return {"rsi": 50, "per": 20, "peg": 1.5, "growth": 5.0}, None

def generate_all_hints(all_data):
    """3銘柄分の寸評を一括生成"""
    prompt = "あなたは株式投資ゲームのナビゲーターです。以下の3つの銘柄に対して、それぞれ指定されたキャラクター設定で寸評（約120〜150文字）を作成してください。\n\n"
    
    for i, data in enumerate(all_data):
        prompt += f"【銘柄 {i+1}】\n"
        prompt += f"・キャラクター設定: {data['persona']}\n"
        prompt += f"・対象企業: {data['company_name']}\n"
        prompt += f"・RSI(14日): {data['metrics']['rsi']:.1f}%\n"
        prompt += f"・PER: {data['metrics']['per']}倍\n"
        prompt += f"・PEGレシオ: {data['metrics']['peg']}\n"
        prompt += f"・売上高成長率: {data['metrics']['growth']:.1f}%\n\n"

    prompt += """【絶対ルール】
    1. 各寸評は必ず「===」という記号だけで区切って出力してください。
    2. 寸評以外のテキスト（見出しや挨拶など）は一切書かないでください。
    3. 各キャラクターの口調・個性を完全に守りきってください。
    4. 現在が「90日前」の時点であるという前提で語ってください。"""

    try:
        response = model.generate_content(prompt)
        
        # もしセーフティーフィルターでブロックされた場合の処理
        if not response.parts:
            return [f"安全装置作動: 表現がブロックされました"] * 3
            
        hints = [h.strip() for h in response.text.split("===") if h.strip()]
        while len(hints) < 3:
            hints.append("（分析データの受信に失敗しました）")
        return hints
        
    except Exception as e:
        # 「通信エラー発生」の代わりに、エラーの本当の理由を画面に出力する
        return [f"エラー詳細: {e}"] * 3

def shuffle_tickers():
    st.session_state.current_tickers = random.sample(list(TICKER_POOL.keys()), 3)
    st.session_state.hints = {}
    st.session_state.selected_ticker = None

# ==========================================
# 4. UI 描画
# ==========================================
st.title("📈 AI自動売買アルゴリズム・シミュレーションゲーム")
st.subheader("〜 90日前のデータとチャートから、未来の勝ち組を予測せよ 〜")

if st.session_state.game_stage == "select":
    
    if st.button("🔄 別の3銘柄にシャッフルする"):
        shuffle_tickers()
        st.rerun()

    st.write("---")
    
    all_data = []
    chart_data_list = []
    
    for i, ticker in enumerate(st.session_state.current_tickers):
        company_name = TICKER_POOL[ticker]
        metrics, chart_data = get_90days_ago_data(ticker)
        chart_data_list.append(chart_data)
        all_data.append({
            "ticker": ticker, 
            "company_name": company_name, 
            "metrics": metrics, 
            "persona": PERSONAS[i]["desc"]
        })

    if not st.session_state.hints:
        with st.spinner("3人の個性派ナビゲーターが会議中... (一括解析)"):
            hints_list = generate_all_hints(all_data)
            for i, ticker in enumerate(st.session_state.current_tickers):
                st.session_state.hints[ticker] = hints_list[i]
                
    cols = st.columns(3)
    
    for i, ticker in enumerate(st.session_state.current_tickers):
        company_name = TICKER_POOL[ticker]
        chart_data = chart_data_list[i]
        avatar_icon = PERSONAS[i]["avatar"]
        
        with cols[i]:
            st.markdown(f"### 🏢 {company_name}")
            st.caption(f"`{ticker}`")
            
            if chart_data is not None:
                st.caption("📊 90日前時点から見た過去90日間の推移")
                st.line_chart(chart_data['Close'], height=200)
            
            with st.chat_message("assistant", avatar=avatar_icon):
                st.write(st.session_state.hints.get(ticker, "解析中..."))
            
            st.write("")
            
            if st.button(f"{company_name} を選択してシミュレート", key=f"btn_{ticker}"):
                st.session_state.selected_ticker = ticker
                st.session_state.game_stage = "result"
                st.rerun()

elif st.session_state.game_stage == "result":
    selected_name = TICKER_POOL[st.session_state.selected_ticker]
    st.success(f"### 📈 {selected_name} の90日間自動売買シミュレーションを開始します")
    
    if st.button("↩️ 銘柄選択に戻る"):
        st.session_state.game_stage = "select"
        shuffle_tickers()
        st.rerun()