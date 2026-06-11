import streamlit as st
import random
import yfinance as yf
import pandas as pd
import google.generativeai as genai

# ==========================================
# 1. 初期設定とAPIキーのセットアップ
# ==========================================
st.set_page_config(page_title="AI株式トレードシミュレーター", layout="wide")

# Gemini APIの初期化 (StreamlitのSecrets機能、または直接入力)
# ※ローカル環境では st.secrets["GEMINI_API_KEY"] を使用するのが安全です
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    # 開発用に画面上で入力できるようにフォールバック
    api_key = st.sidebar.text_input("Gemini API Key を入力してください", type="password")
    if api_key:
        genai.configure(api_key=api_key)

model = genai.GenerativeModel('gemini-2.5-flash')

# ==========================================
# 2. 銘柄プールとセッション状態の初期化
# ==========================================
# ゲームに登場させる候補銘柄リスト（大型バリュー・中小型グロース混合）
TICKER_POOL = {
    "7203.T": "大手自動車メーカー",
    "6758.T": "大手総合電機・エンタメ企業",
    "9984.T": "大手投資・通信グループ",
    "4385.T": "フリマアプリ運営の新興IT企業",
    "7974.T": "大手ゲーム玩具メーカー",
    "6501.T": "重電・システム大手のインフラ企業",
    "6062.T": "医療・福祉特化の人材サービス企業",
    "4475.T": "クラウドセキュリティを展開するIT企業"
}

# セッション状態でゲームのステージや選択銘柄を管理
if "current_tickers" not in st.session_state:
    st.session_state.current_tickers = random.sample(list(TICKER_POOL.keys()), 3)
if "hints" not in st.session_state:
    st.session_state.hints = {}
if "game_stage" not in st.session_state:
    st.session_state.game_stage = "select" # select（選択中） or result（結果発表）
if "selected_ticker" not in st.session_state:
    st.session_state.selected_ticker = None

# ==========================================
# 3. ビジネスロジック（データ取得・分析関数）
# ==========================================
@st.cache_data(show_spinner=False)
def get_30days_ago_metrics(ticker):
    """30日前時点の多面的指標を計算・取得する"""
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="1y", interval="1d")
        df.index = df.index.tz_localize(None)
        
        target_idx = -30
        if len(df) < abs(target_idx):
            return None
            
        past_df = df.iloc[:len(df) + target_idx].copy()
        
        # 指標計算
        diff = past_df['Close'].diff()
        up, down = diff.clip(lower=0), -1 * diff.clip(upper=0)
        rsi = 100 - (100 / (1 + (up.rolling(14).mean().iloc[-1] / down.rolling(14).mean().iloc[-1])))
        
        info = stock.info
        per = info.get('trailingPE', 999)
        peg = info.get('pegRatio', 999)
        rev_growth = info.get('revenueGrowth', 0) or 0
        
        return {"rsi": rsi, "per": per, "peg": peg, "growth": rev_growth * 100}
    except:
        return {"rsi": 50, "per": 20, "peg": 1.5, "growth": 5.0}

def generate_ai_hint(ticker, metrics):
    """Gemini APIを使用して、銘柄名を知らないAIに寸評を作らせる"""
    prompt = f"""
    あなたは投資ゲームのナビゲーターです。30日前時点の以下の指標を分析し、プレイヤーへの寸評（ヒント）を作ってください。
    ・RSI(14日): {metrics['rsi']:.1f}%
    ・PER: {metrics['per']}倍
    ・PEGレシオ: {metrics['peg']}
    ・売上高成長率: {metrics['growth']:.1f}%
    
    【条件】銘柄コードや実際の企業名は絶対に伏せ、「この銘柄」と呼んでください。100文字程度で、特徴（グロース株かバリュー株か、買い場か）をワクワクするトーンで解説してください。
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except:
        return "（APIエラーまたはキー未設定。データに基づいた裏側での自動計算は生きています。）"

def shuffle_tickers():
    """銘柄のシャッフル（引き直し）処理"""
    st.session_state.current_tickers = random.sample(list(TICKER_POOL.keys()), 3)
    st.session_state.hints = {} # ヒントをリセット
    st.session_state.selected_ticker = None

# ==========================================
# 4. UI 描画（メイン画面）
# ==========================================
st.title("📈 AI自動売買アルゴリズム・シミュレーションゲーム")
st.subheader("〜 30日前にタイムスリップして、ベストな銘柄を仕込め 〜")

st.markdown("""
システムが多面的な分析（テクニカル・成長性・財務面）からスクリーニングした3つの候補銘柄があります。
プレイヤーであるあなたは、30日前時点での**AIナビゲーターによる寸評（ヒント）**を頼りに、
これから30日間で「自動売買アルゴリズムが最も高い収益を叩き出す銘柄」を1つ選んでください。
""")

# 銘柄選択ステージ
if st.session_state.game_stage == "select":
    
    # シャッフルボタン
    if st.button("🔄 銘柄をシャッフル（選び直す）"):
        shuffle_tickers()
        st.rerun()

    st.write("---")
    
    # 3つの銘柄を横並びに表示（Streamlitのcolumns機能）
    cols = st.columns(3)
    
    for i, ticker in enumerate(st.session_state.current_tickers):
        with cols[i]:
            st.markdown(f"### 📦 候補銘柄 {chr(65+i)}") # 銘柄A, B, Cとして表示（名前は伏せる）
            st.caption(f"分類ヒント: {TICKER_POOL[ticker]}")
            
            # データの取得とヒント生成（セッションに保持して無駄なAPI呼び出しを防ぐ）
            if ticker not in st.session_state.hints:
                with st.spinner("AIが指標を解析中..."):
                    metrics = get_30days_ago_metrics(ticker)
                    hint_text = generate_ai_hint(ticker, metrics)
                    st.session_state.hints[ticker] = hint_text
            
            # 寸評カードの表示
            st.info(st.session_state.hints[ticker])
            
            # 選択ボタン
            if st.button(f"銘柄 {chr(65+i)} を選んでシミュレート", key=f"btn_{ticker}"):
                st.session_state.selected_ticker = ticker
                st.session_state.game_stage = "result"
                st.rerun()

# 結果発表ステージ（プレースホルダー。ここに前回のバックテストロジックが入ります）
elif st.session_state.game_stage == "result":
    st.success(f"### 選択完了: 銘柄 {st.session_state.selected_ticker}（正体: {st.session_state.selected_ticker}）")
    st.write("ここで裏側で30日間のループを回し、売買資産の推移グラフとランキングを発表します。")
    
    if st.button("↩️ もう一度遊ぶ（最初に戻る）"):
        st.session_state.game_stage = "select"
        shuffle_tickers()
        st.rerun()
