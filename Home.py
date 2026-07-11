import streamlit as st
import counter

# ページの基本設定
st.set_page_config(
    page_title="信州上田GAMES ポータル",
    page_icon="🏯",
    layout="centered"
)
counter.add_count("Home")
# 🏯 上田城・真田赤備え風のカスタムCSS
st.markdown("""
<style>
    /* 背景を少し和紙・石垣っぽい落ち着いた色に */
    .stApp {
        background-color: #f4f1eb;
    }
    
    /* 🏯 メインの看板（赤備え・漆黒の縁取り） */
    .sanada-banner {
        background: linear-gradient(135deg, #c0392b 0%, #8e44ad 100%); /* 真田赤から少し紫がかるグラデーション */
        color: white;
        padding: 30px;
        border-radius: 8px;
        text-align: center;
        border: 6px solid #2c3e50; /* 漆黒の枠 */
        box-shadow: 0 10px 20px rgba(0,0,0,0.4);
        margin-bottom: 40px;
        position: relative;
    }
    
    /* 🪙 六文銭のCSSアート */
    .rokumonsen {
        display: flex;
        justify-content: center;
        gap: 10px;
        margin-bottom: 8px;
    }
    .rokumonsen-row {
        margin-bottom: 10px;
    }
    .coin {
        width: 35px;
        height: 35px;
        background-color: #f1c40f; /* 黄金色 */
        border-radius: 50%;
        border: 3px solid #2c3e50;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: inset 0 0 5px rgba(0,0,0,0.5);
    }
    /* 穴（四角形） */
    .coin::after {
        content: '';
        width: 10px;
        height: 10px;
        background-color: #2c3e50;
    }
    
    /* タイトル文字 */
    .sanada-banner h1 {
        margin: 0;
        font-family: 'Yu Mincho', 'MS Mincho', serif; /* 明朝体で和風に */
        font-size: 3.5em;
        letter-spacing: 4px;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.6);
    }
    
    .sanada-banner p {
        margin-top: 10px;
        font-size: 1.2em;
        font-weight: bold;
        letter-spacing: 2px;
        color: #f1c40f;
    }

    /* 🚪 各ゲームへのリンクボタンを城の門風にカスタマイズ */
    div[data-testid="stLinkButton"] > a {
        background-color: #34495e !important;
        color: #ecf0f1 !important;
        border: 2px solid #bdc3c7 !important;
        border-radius: 8px !important;
        padding: 20px !important;
        font-size: 1.2em !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
        display: flex !important;
        justify-content: flex-start !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2) !important;
    }
    div[data-testid="stLinkButton"] > a:hover {
        background-color: #c0392b !important; /* ホバーで赤備えに */
        border-color: #f1c40f !important;
        color: white !important;
        transform: translateY(-4px) !important;
        box-shadow: 0 8px 15px rgba(0,0,0,0.3) !important;
    }
</style>
""", unsafe_allow_html=True)

# 🏯 ヘッダーバナーの描画
st.markdown("""
<div class="sanada-banner">
    <div class="rokumonsen-row">
        <div class="rokumonsen">
            <div class="coin"></div><div class="coin"></div><div class="coin"></div>
        </div>
        <div class="rokumonsen">
            <div class="coin"></div><div class="coin"></div><div class="coin"></div>
        </div>
    </div>
    <h1>信州上田 GAMES</h1>
    <p>〜 医療の知を束ね、いざ出陣 〜</p>
</div>
""", unsafe_allow_html=True)

st.markdown("### ⛩️ 出陣の門（演習一覧）")
st.write("各陣を突破し、強靭な臨床力とチーム連携を身につけよ。")

st.write("") # スペーサー

# 🚪 リンクボタンの配置
col1, col2 = st.columns(2)

with col1:
    st.page_link("pages/1_酸塩基合戦.py", label="第一陣：酸塩基合戦", icon="⚔️")
    st.write("")
    st.page_link("pages/2_アクション演習.py", label="第二陣：アクション演習", icon="🏃")
    st.write("")
    st.page_link("pages/3_ナースダッシュ.py", label="第三陣：ナースダッシュ", icon="💨")

with col2:
    st.page_link("pages/4_ICLSシミュレーター.py", label="第四陣：ICLSシミュレーター", icon="⚡")
    st.write("")
    st.page_link("pages/5_ICLSクイズ.py", label="第五陣：ICLS限界突破クイズ", icon="🧬")
    st.write("")
    st.page_link("pages/6_シューティング.py", label="第六陣：メディカルストライカー", icon="🚀")
    st.write("")
    st.page_link("pages/7_株トレーダー.py", label="第七陣：株トレーダー", icon="📈")

st.markdown("---")
st.markdown("<div style='text-align: center; color: #7f8c8d; font-size: 14px;'>© 2026 信州上田医療センター 総合教育ポータル</div>", unsafe_allow_html=True)
counts = counter.get_all_counts()


if counts:
    hidden_text = " | ".join([f"{k}: {v}" for k, v in counts.items()])
    
    # 🌟 修正：画面右下に固定配置するCSSに変更
    st.markdown(
        f"""
        <style>
        .fixed-footer {{
            position: fixed;
            bottom: 10px;
            right: 10px;
            font-size: 10px;
            color: transparent; /* 背景色と同化 */
            z-index: 9999;
            cursor: default;
        }}
        .fixed-footer:hover {{
            color: #bdc3c7; /* ホバーで浮かび上がる */
        }}
        </style>
        <div class="fixed-footer" title="Access - {hidden_text}">
            Access - {hidden_text} .
        </div>
        """, 
        unsafe_allow_html=True
    )