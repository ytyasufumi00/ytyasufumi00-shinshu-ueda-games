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

PERSONAS = [
    {"avatar": "🥷", "desc": "相場の裏を読む凄腕の忍（忍びの言葉使い。「潜伏」「陽動」「仕掛けの刻（とき）」などの言葉を使い、チャートの裏に潜む大口投資家の動きや気配を語る）"},
    {"avatar": "👩‍💼", "desc": "冷徹で理知的な女性クオンツAI（敬語で丁寧だが、データ至上主義で少し冷たい印象。「〜と推察されますわ」「感情はノイズに過ぎません」「期待値は極めて高いですわね」などのお嬢様・クール系女性口調を使う）"},
    {"avatar": "🧑‍🎤", "desc": "相場をライブ会場に変えるロックスター・トレーダー（ハイテンションで音楽的な比喩を使う。「ビートに乗れ！」「ノイズを切り裂くギターソロ！」「アゲアゲのチューン」などを使い熱狂的に語る）"}
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
# 3. データ処理・シミュレーション関数
# ==========================================
@st.cache_data(show_spinner=False)
def get_90days_ago_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="1y", interval="1d")
        df.index = df.index.tz_localize(None)
        
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
        return metrics, past_df.tail(90)
    except:
        return {"rsi": 50, "per": 20, "peg": 1.5, "growth": 5.0}, None

def generate_all_hints(all_data):
    prompt = "あなたは株式投資ゲームのナビゲーターです。以下の3つの銘柄に対して、それぞれ指定されたキャラクター設定で寸評（約120〜150文字）を作成してください。\n\n"
    for i, data in enumerate(all_data):
        prompt += f"【銘柄 {i+1}】\n・キャラクター設定: {data['persona']}\n・対象企業: {data['company_name']}\n・RSI(14日): {data['metrics']['rsi']:.1f}%\n・PER: {data['metrics']['per']}倍\n・PEGレシオ: {data['metrics']['peg']}\n・売上高成長率: {data['metrics']['growth']:.1f}%\n\n"

    prompt += """【絶対ルール】
    1. 各寸評は必ず「===」という記号だけで区切って出力してください。
    2. 寸評以外のテキスト（見出しや挨拶など）は一切書かないでください。
    3. 各キャラクターの口調・個性を完全に守りきってください。
    4. 現在が「90日前」の時点であるという前提で語ってください。"""

    try:
        response = model.generate_content(prompt)
        if not response.parts:
            return [f"安全装置作動: 表現がブロックされました"] * 3
        hints = [h.strip() for h in response.text.split("===") if h.strip()]
        while len(hints) < 3:
            hints.append("（分析データの受信に失敗しました）")
        return hints
    except Exception as e:
        return [f"エラー詳細: {e}"] * 3

def run_algorithm_simulation(ticker):
    """90日間の自動売買バックテストを実行し、ログを記録する"""
    stock = yf.Ticker(ticker)
    df = stock.history(period="1y", interval="1d")
    df.index = df.index.tz_localize(None)
    info = stock.info
    peg_ratio = info.get('pegRatio', 2.0)
    
    df['SMA25'] = df['Close'].rolling(window=25).mean()
    diff = df['Close'].diff()
    up, down = diff.clip(lower=0), -1 * diff.clip(upper=0)
    df['RSI'] = 100 - (100 / (1 + (up.rolling(14).mean() / down.rolling(14).mean())))
    df['MACD'] = df['Close'].ewm(span=12, adjust=False).mean() - df['Close'].ewm(span=26, adjust=False).mean()
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    
    df['Score'] = 0
    df.loc[df['RSI'] <= 45, 'Score'] += 1
    df.loc[df['MACD'] > df['Signal'], 'Score'] += 1
    df.loc[df['Close'] > df['SMA25'], 'Score'] += 1
    if isinstance(peg_ratio, (int, float)) and peg_ratio <= 1.5:
        df['Score'] += 1
        
    sim_df = df.tail(90).copy()
    cash = 1000000
    holding_shares = 0
    buy_price = 0
    portfolio_values = []
    trade_count = 0
    trade_logs = [] # ★売買ログを保存するリスト
    
    for date, row in sim_df.iterrows():
        price = row['Close']
        score = row['Score']
        date_str = date.strftime('%Y-%m-%d')
        
        if holding_shares > 0:
            loss_rate = (price - buy_price) / buy_price
            
            # 売り判定
            if loss_rate <= -0.05:
                cash = holding_shares * price
                holding_shares = 0
                trade_count += 1
                trade_logs.append({"日付": date_str, "アクション": "🔵 売 (損切)", "価格": int(price), "理由": "損失 5% 超過"})
            elif loss_rate >= 0.10:
                cash = holding_shares * price
                holding_shares = 0
                trade_count += 1
                trade_logs.append({"日付": date_str, "アクション": "🟢 売 (利確)", "価格": int(price), "理由": "利益 10% 到達"})
            elif score < 1:
                cash = holding_shares * price
                holding_shares = 0
                trade_count += 1
                trade_logs.append({"日付": date_str, "アクション": "🟡 売 (撤退)", "価格": int(price), "理由": "シグナル消滅 (スコア低下)"})
                
        elif holding_shares == 0:
            # 買い判定
            if score >= 2:
                holding_shares = cash // price
                cash -= holding_shares * price
                buy_price = price
                trade_count += 1
                trade_logs.append({"日付": date_str, "アクション": "🔴 買 (BUY)", "価格": int(price), "理由": f"複数シグナル点灯 (スコア {int(score)}点)"})
                
        total_value = cash + (holding_shares * price)
        portfolio_values.append(total_value)
        
    return {
        "final_value": portfolio_values[-1],
        "profit": portfolio_values[-1] - 1000000,
        "history": portfolio_values,
        "dates": sim_df.index,
        "trade_count": trade_count // 2,
        "logs": trade_logs # ★ログを結果に追加
    }

def shuffle_tickers():
    st.session_state.current_tickers = random.sample(list(TICKER_POOL.keys()), 3)
    st.session_state.hints = {}
    st.session_state.selected_ticker = None
    st.session_state.game_stage = "select"

# ==========================================
# 4. UI 描画
# ==========================================
st.title("📈 AI自動売買アルゴリズム・シミュレーションゲーム")

# --- 銘柄選択ステージ ---
if st.session_state.game_stage == "select":
    st.subheader("〜 90日前のデータとチャートから、未来の勝ち組を予測せよ 〜")
    
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
                st.line_chart(chart_data['Close'], height=150)
            
            with st.chat_message("assistant", avatar=avatar_icon):
                st.write(st.session_state.hints.get(ticker, "解析中..."))
            
            st.write("")
            if st.button(f"{company_name} を選択してシミュレート", key=f"btn_{ticker}"):
                st.session_state.selected_ticker = ticker
                st.session_state.game_stage = "result"
                st.rerun()

# --- 結果発表ステージ ---
elif st.session_state.game_stage == "result":
    st.subheader("🏁 90日間 自動売買シミュレーション結果発表")
    
    with st.spinner("アルゴリズムが過去90日間の市場で戦っています..."):
        results = []
        chart_df = pd.DataFrame()
        
        for ticker in st.session_state.current_tickers:
            sim_result = run_algorithm_simulation(ticker)
            sim_result['ticker'] = ticker
            sim_result['name'] = TICKER_POOL[ticker]
            results.append(sim_result)
            
            temp_df = pd.DataFrame({sim_result['name']: sim_result['history']}, index=sim_result['dates'])
            if chart_df.empty:
                chart_df = temp_df
            else:
                chart_df = chart_df.join(temp_df, how='outer')
                
        results.sort(key=lambda x: x['final_value'], reverse=True)
        player_rank = next(i for i, r in enumerate(results) if r['ticker'] == st.session_state.selected_ticker) + 1
        
    st.write("---")
    
    if player_rank == 1:
        st.balloons()
        st.success(f"🎉 お見事！あなたの選んだ **{TICKER_POOL[st.session_state.selected_ticker]}** が見事1位に輝きました！相場を読む力は本物です。")
    elif player_rank == 2:
        st.info(f"👍 惜しい！あなたの選んだ **{TICKER_POOL[st.session_state.selected_ticker]}** は2位でした。堅実な判断でしたね。")
    else:
        st.error(f"📉 残念... あなたの選んだ **{TICKER_POOL[st.session_state.selected_ticker]}** は最下位でした。アルゴリズムとの相性が悪かったようです。")

    st.markdown("#### 📊 3銘柄の資産推移グラフ（初期資金: 1,000,000円）")
    st.line_chart(chart_df, height=300)

    st.markdown("#### 🏆 最終成績ランキング")
    cols = st.columns(3)
    
    for i, res in enumerate(results):
        with cols[i]:
            medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉"
            st.markdown(f"### {medal} 第{i+1}位")
            st.markdown(f"**{res['name']}**")
            profit_color = "normal" if res['profit'] == 0 else "off" if res['profit'] < 0 else "inverse"
            st.metric(
                label="最終資産額",
                value=f"¥ {int(res['final_value']):,}",
                delta=f"¥ {int(res['profit']):,}",
                delta_color=profit_color
            )
            st.caption(f"自動取引回数: {res['trade_count']} 回")

    st.write("---")
    
    # ★追加：売買ログ（取引履歴）の表示セクション
    st.markdown("#### 📝 アルゴリズムの売買ログ（詳細履歴）")
    st.markdown("アルゴリズムが90日間にわたり、いつ・いくらで・なぜ売買を行ったかの記録です。")
    
    # Streamlitのタブ機能を使って、3銘柄のログを切り替えて見れるようにする
    tab_names = [res['name'] for res in results]
    tabs = st.tabs(tab_names)
    
    for i, tab in enumerate(tabs):
        with tab:
            logs = results[i]["logs"]
            if not logs:
                st.write("※この90日間、アルゴリズムの買い条件（スコア2点以上）を満たす日はありませんでした。")
            else:
                # ログをデータフレーム化して表として綺麗に表示
                log_df = pd.DataFrame(logs)
                # インデックス番号を消してスッキリ表示させる
                st.dataframe(log_df, use_container_width=True, hide_index=True)

    st.write("---")
    if st.button("↩️ もう一度別の銘柄で挑戦する"):
        shuffle_tickers()