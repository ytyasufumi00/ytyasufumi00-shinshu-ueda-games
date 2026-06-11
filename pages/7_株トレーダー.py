import streamlit as st
import random
import time
import datetime
import yfinance as yf
import pandas as pd
import google.generativeai as genai
from openai import OpenAI
import anthropic

# ==========================================
# 1. 初期設定・APIキー・日付の計算
# ==========================================
st.set_page_config(page_title="AI株式トレードシミュレーター", layout="wide")

try:
    genai.configure(api_key=st.secrets.get("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"temperature": 0.85})
except Exception:
    model = None

try:
    openai_client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY"))
except Exception:
    openai_client = None

try:
    anthropic_client = anthropic.Anthropic(api_key=st.secrets.get("ANTHROPIC_API_KEY"))
except Exception:
    anthropic_client = None

# ★ 日付計算の関数（西暦から令和に変換）
def get_jp_date_str(dt):
    ry = dt.year - 2018
    ry_str = "元" if ry == 1 else str(ry)
    return f"令和{ry_str}年{dt.month}月{dt.day}日"

today = datetime.date.today()
past_90 = today - datetime.timedelta(days=90)
today_str = get_jp_date_str(today)
past_90_str = get_jp_date_str(past_90)

# ==========================================
# 2. 市場ユニバースと設定
# ==========================================
MARKET_UNIVERSE = {
    "7203.T": "トヨタ自動車", "6758.T": "ソニーG", "9984.T": "ソフトバンクG",
    "4385.T": "メルカリ", "7974.T": "任天堂", "6501.T": "日立製作所",
    "6062.T": "チャーム・ケア", "4475.T": "HENNGE", "6861.T": "キーエンス",
    "8035.T": "東京エレクトロン", "9983.T": "ファーストリテイリング", "4661.T": "オリエンタルランド",
    "8306.T": "三菱UFJ", "8058.T": "三菱商事", "9101.T": "日本郵船",
    "6981.T": "村田製作所", "7267.T": "ホンダ", "6902.T": "デンソー",
    "4502.T": "武田薬品工業", "4568.T": "第一三共", "6098.T": "リクルート",
    "4751.T": "サイバーエージェント", "3993.T": "PKSHA", "4452.T": "花王"
}

ROLES = [
    {"type": "変動・テクニカル重視", "avatar": "🥷", "desc": "相場の裏を読む凄腕の忍（忍びの言葉使い。「潜伏」「陽動」「仕掛けの刻」などを用い、チャートの形やRSIの売られすぎ感などテクニカル指標の歪みから勝機を語る）"},
    {"type": "急成長・グロース重視", "avatar": "🧑‍🎤", "desc": "相場をライブ会場に変えるロックスター・トレーダー（ハイテンションで音楽的な比喩。「ビートに乗れ」「フルスロットル」などを使い、売上成長率の高さや将来の爆発力を熱狂的に語る）"},
    {"type": "割安・ファンダ重視", "avatar": "👩‍🏫", "desc": "冷徹で理知的な女性クオンツAI（敬語で丁寧だが、データ至上主義で少し冷たい。「〜と推察されますわ」「感情はノイズ」などを用い、PERの低さなど堅実な財務指標を冷静に評価する）"}
]

if "screened_candidates" not in st.session_state:
    st.session_state.screened_candidates = []
if "hints" not in st.session_state:
    st.session_state.hints = {}
if "game_stage" not in st.session_state:
    st.session_state.game_stage = "select"
if "selected_ticker" not in st.session_state:
    st.session_state.selected_ticker = None

# ==========================================
# 3. エンジン：市場スキャンとAI解析
# ==========================================
def scan_market():
    sample_tickers = random.sample(list(MARKET_UNIVERSE.keys()), 15)
    analyzed_data = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, ticker in enumerate(sample_tickers):
        status_text.text(f"市場スキャン中... {i+1}/15 銘柄解析中 ({MARKET_UNIVERSE[ticker]})")
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period="1y", interval="1d")
            df.index = df.index.tz_localize(None)
            
            target_idx = -90
            if len(df) < abs(target_idx):
                continue
                
            past_df = df.iloc[:len(df) + target_idx].copy()
            
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
            
            analyzed_data.append({
                "ticker": ticker,
                "name": MARKET_UNIVERSE[ticker],
                "chart_data": past_df.tail(90),
                "metrics": {"rsi": rsi, "per": per, "peg": peg, "growth": rev_growth * 100},
                "scores": {"tech": tech_score, "growth": growth_score, "value": value_score}
            })
        except:
            pass
        progress_bar.progress((i + 1) / 15)
        
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
    prompt = "あなたは株式投資ゲームのナビゲーターです。以下の3つの銘柄は、システムが全市場から異なる3つの基準で抽出した「90日前時点」の注目銘柄です。それぞれのキャラクター設定と選出理由に沿って寸評（約120〜150文字）を作成してください。\n\n"
    
    for i, cand in enumerate(candidates):
        role = cand["role"]
        data = cand["data"]
        prompt += f"【銘柄 {i+1}】\n・キャラクター設定: {role['desc']}\n・選出基準: {role['type']}の観点から抽出\n・対象企業: {data['name']}\n・RSI(14日): {data['metrics']['rsi']:.1f}%\n・PER: {data['metrics']['per']}倍\n・売上高成長率: {data['metrics']['growth']:.1f}%\n\n"

    # ★AIにも日付を明記して、よりリアルなタイムスリップ感を演出
    prompt += f"""【絶対ルール】
    1. 各寸評は必ず「===」という記号だけで区切って出力してください。
    2. 寸評以外のテキストは一切書かないでください。
    3. 各キャラクターの口調を守り、現在が「{past_90_str}」の時点であるという前提で語ってください。"""

    # 第一陣：Gemini API
    if model:
        try:
            response = model.generate_content(prompt)
            if response.parts:
                hints = [h.strip() for h in response.text.split("===") if h.strip()]
                if len(hints) >= 3:
                    return hints[:3]
        except Exception:
            pass

    # 第二陣：OpenAI (ChatGPT) API
    if openai_client:
        try:
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.85
            )
            hints = [h.strip() for h in response.choices[0].message.content.split("===") if h.strip()]
            if len(hints) >= 3:
                return [h + " *(GPT)*" for h in hints][:3]
        except Exception:
            pass

    # 第三陣：Anthropic (Claude) API
    if anthropic_client:
        try:
            response = anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                temperature=0.85,
                messages=[{"role": "user", "content": prompt}]
            )
            hints = [h.strip() for h in response.content[0].text.split("===") if h.strip()]
            if len(hints) >= 3:
                return [h + " *(Claude)*" for h in hints][:3]
        except Exception:
            pass

   # ★最終防衛線：すべてのAIがダウンした場合は、自前のプログラムで寸評を自動生成する
    st.toast("全AIサーバー応答なし。内蔵の予備アルゴリズムで解析します", icon="⚡")
    emergency_hints = []
    
    for cand in candidates:
        role_type = cand["role"]["type"]
        name = cand["data"]["name"]
        rsi = cand["data"]["metrics"]["rsi"]
        growth = cand["data"]["metrics"]["growth"]
        per = cand["data"]["metrics"]["per"]
        text = ""
        
        # 🥷 忍（テクニカル・RSI重視）のバリエーション（各条件につき6〜9パターン）
        if "テクニカル" in role_type:
            if rsi < 35:
                options = [
                    f"拙者が見立てるに、{name}のRSIは{rsi:.1f}%と完全に売られすぎの領域。反発の機は熟した。チャートの歪みに潜伏し、大口に便乗して仕掛ける刻（とき）だ！",
                    f"血の匂いがするな。{name}のRSIは{rsi:.1f}%。狼狽売りの極みよ。大衆が恐怖に駆られる今こそ、暗闇から刃を振り下ろす絶好の好機！",
                    f"見事な『陰』の極み。RSI{rsi:.1f}%の{name}は、まさに身を屈めた底値圏。ここからの跳躍は凄まじいものになろう。いざ、出陣！",
                    f"底なし沼に見えるか？否。{name}のRSI{rsi:.1f}%は、反撃の狼煙を上げる直前の静寂。恐れず踏み込むべし。",
                    f"恐怖で手放された骸を拾え。RSI{rsi:.1f}%の{name}、ここは絶好の狩り場ぞ。逆張りの太刀筋を見せてやれ！",
                    f"チャートが泣いているな。{name}のRSIは{rsi:.1f}%。だが案ずるな、夜明け前が最も暗いのだ。仕掛けの刻は今！",
                    f"売られすぎの極限、RSI{rsi:.1f}%。{name}のこの歪み、見逃す手はない。大衆の裏をかくのが忍びの道よ。",
                    f"まさに落下するナイフ。だが拙者には掴める。{name}（RSI{rsi:.1f}%）の反発力、とくと味わうが良い。",
                    f"これほどの『陰』、久しく見ておらぬ。RSI{rsi:.1f}%の{name}、底値の気配が濃厚じゃ。密かに陣を敷け！"
                ]
            elif rsi <= 55:
                options = [
                    f"現在の{name}、RSIは{rsi:.1f}%。まだ決定的な陽動のサインは出ておらぬが、底打ちは近い。兵糧を蓄えつつ、トレンド転換を狙い撃つべし！",
                    f"静かなる水面下で、大口が密かに集めておる気配あり。RSI{rsi:.1f}%の{name}、嵐の前の静けさよ。伏兵を配置し、シグナルを待て。",
                    f"チャートの息遣いが聞こえるか？{name}（RSI{rsi:.1f}%）は力を溜めている最中。焦る必要はない、忍びの如く息を殺して機をうかがえ。",
                    f"相場が迷っておるな。{name}のRSIは{rsi:.1f}%。今は無闇に動かず、次のトレンドの兆しを待つのが上策。",
                    f"RSI{rsi:.1f}%の{name}。買い方と売り方の鍔迫り合いが続いておる。どちらかに崩れる瞬間、そこが我らの出番だ。",
                    f"今は力を溜める刻（とき）。{name}（RSI{rsi:.1f}%）のチャートは、次なる跳躍のための助走期間と見ゆる。",
                    f"焦りは禁物じゃ。RSI{rsi:.1f}%の{name}、まだ大口の意図が見えぬ。気配を探りつつ、刀は鞘に収めておけ。",
                    f"凪の海面の下で、何かが動こうとしている。{name}（RSI{rsi:.1f}%）。シグナルが点灯するまで、隠密行動を貫け。",
                    f"50のラインを巡る攻防。{name}のRSIは{rsi:.1f}%。均衡が破れた方へ、疾風の如く追従する準備をしておけ。"
                ]
            else:
                options = [
                    f"すでに火蓋は切って落とされた！{name}のRSIは{rsi:.1f}%と上昇の気勢あり。流れには逆らわず、素早く順張りの陣形を敷くが吉！",
                    f"力強い陽の波動を感じる。RSI{rsi:.1f}%の{name}は既に動意づいておる。高値掴みには警戒しつつも、この勢いに乗じて一気に攻め上れ！",
                    f"上昇の波に乗れ！{name}のRSIは{rsi:.1f}%。このモメンタム、逆らうには惜しい勢いじゃ。",
                    f"風は我らに吹いている。RSI{rsi:.1f}%の{name}、陽の波動がチャートを支配しておる。順張りで一気に押し通れ！",
                    f"過熱には注意せねばならぬが、今はまだ攻めの刻。{name}（RSI{rsi:.1f}%）の勢い、天井を打つまで絞り尽くせ！",
                    f"青天井の気配すらあるな。{name}のRSIは{rsi:.1f}%。大口の買いに追従し、手早く利益をさらうのが忍びの流儀よ。"
                ]
            text = random.choice(options)

        # 🧑‍🎤 ロックスター（グロース・売上成長率重視）のバリエーション
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
                    f"これぞまさに神曲のリリース！{name}の成長率{growth:.1f}%。株価が空の彼方へ飛んでいくぜ、準備はいいか！？"
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
                    f"安定のビート刻んでるね！{name}の{growth:.1f}%成長。インベスターたちも少しずつこの曲の魅力に気付き始めてるぜ！"
                ]
            else:
                options = [
                    f"今はバラードのターンか？{name}の成長率{growth:.1f}%は控えめだが、名曲ってのは静かなイントロから爆発するもんだろ？伝説のカムバックツアーに期待しようぜ！",
                    f"少しノイズが混じってる（成長率{growth:.1f}%）が、ロックスターにスランプはつきものだ！{name}の真のポテンシャルが解放される瞬間、最前列でヘッドバンギングしようぜ！",
                    f"成長率{growth:.1f}%？今はアンプのチューニング中さ。{name}が次のアルバムで世界を驚かせるのを待とうぜ！",
                    f"少し静かすぎるか？だが{name}（成長率{growth:.1f}%）の底力を見くびるな。いきなりの転調で爆発するのがロックだ！",
                    f"今はちょっとアンダーグラウンドに潜ってる時期（成長率{growth:.1f}%）。だが{name}のコアなファンは離れないぜ！",
                    f"スローテンポな{name}（成長率{growth:.1f}%）だが、ブレイクダウンからの重低音に期待してるぜ。目を離すな！"
                ]
            text = random.choice(options)

        # 👩‍🏫 クオンツAI（バリュー・PER重視）のバリエーション
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
                    f"これほど美しい財務の非対称性は珍しいですわ。PER{per:.1f}倍の{name}、わたくしのアルゴリズムは強力な上昇を示唆しております。"
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
                    f"市場の適正なコンセンサスが形成されておりますわ（PER{per:.1f}倍）。{name}の今後のカタリストに注目しつつ、着実なリターンを狙うべきです。"
                ]
            else:
                if per > 100 or per <= 0:
                    options = [
                        f"{name}の現在の利益ベースでは、PERによる単純比較はノイズになりますわね。しかし、PBRやキャッシュフローの観点から見れば、現在の株価位置は十分に合理的な範囲内だと算出されておりますわ。",
                        f"見かけのPER数値は異常値を示しておりますが、エラーではありません。{name}が抱える無形資産や今後の事業フェーズを考慮すれば、十分に投資適格という推論結果が出ましたわ。",
                        f"見かけ上のPER（{per:.1f}倍）に惑わされてはいけませんわ。{name}の評価には、別のマルチプル指標を用いるのがクオンツの定石です。",
                        f"利益ベースの評価モデルが機能しないフェーズですわね。しかし、{name}の売上モメンタムと市場シェアを考慮すれば、投資価値は十分に存在します。",
                        f"PERの異常値（{per:.1f}倍）は、会計上のノイズに過ぎませんわ。{name}の真のエンタープライズ価値は、わたくしの計算ではもっと高位にあります。",
                        f"赤字、あるいは極端な高PER（{per:.1f}倍）ですが、{name}は先行投資期にあります。フリーキャッシュフローの改善トレンドを見れば、懸念には及びませんわ。"
                    ]
                else:
                    options = [
                        f"{name}のPERは{per:.1f}倍と、指標面ではプレミアム価格がついておりますわ。しかし、これは未来の利益を見越した市場のコンセンサス。データが示す成長軌道を信じるべき局面ですわね。",
                        f"PERの数値（{per:.1f}倍）のみを見れば警戒水域ですが、{name}の無形資産や市場シェアをスコアリングに加味すると、この株価でも十分に投資適格という推論結果が出ましたわ。",
                        f"PER{per:.1f}倍という数値は一見すると割高ですが、{name}の利益成長率で割り引けば（PEGレシオ）、十分に正当化されるバリュエーションですわ。",
                        f"市場は{name}に対して強い期待を寄せておりますわね（PER{per:.1f}倍）。モメンタム投資の観点からは、このプレミアムに乗るのも一つの合理的な戦略です。",
                        f"高PER（{per:.1f}倍）銘柄特有のボラティリティには注意が必要ですが、{name}の強固な競争優位性を加味すれば、わたくしのモデルは保有を許容しますわ。",
                        f"バリュー投資家は敬遠する数値（PER{per:.1f}倍）ですが、{name}のイノベーションの価値を静的な指標だけで測るべきではありませんわ。"
                    ]
            text = random.choice(options)
            
        emergency_hints.append(text + " *(System)*")
        
    return emergency_hints

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
    
    df['Score'] = 0
    df.loc[df['RSI'] <= 45, 'Score'] += 1
    df.loc[df['MACD'] > df['Signal'], 'Score'] += 1
    df.loc[df['Close'] > df['SMA25'], 'Score'] += 1
        
    sim_df = df.tail(90).copy()
    cash = 1000000
    holding_shares = 0
    buy_price = 0
    portfolio_values = []
    trade_count = 0
    trade_logs = []
    
    for date, row in sim_df.iterrows():
        price = row['Close']
        score = row['Score']
        date_str = date.strftime('%Y-%m-%d')
        
        if holding_shares > 0:
            loss_rate = (price - buy_price) / buy_price
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
                trade_logs.append({"日付": date_str, "アクション": "🟡 売 (撤退)", "価格": int(price), "理由": "シグナル消滅"})
                
        elif holding_shares == 0:
            if score >= 2:
                holding_shares = cash // price
                cash -= holding_shares * price
                buy_price = price
                trade_count += 1
                trade_logs.append({"日付": date_str, "アクション": "🔴 買 (BUY)", "価格": int(price), "理由": f"複数シグナル点灯"})
                
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

def reset_and_scan():
    st.session_state.hints = {}
    st.session_state.selected_ticker = None
    st.session_state.game_stage = "select"
    with st.spinner("最新のデータベースから市場をスキャン中..."):
        st.session_state.screened_candidates = scan_market()

# ==========================================
# 4. UI 描画
# ==========================================
st.title("📈 AI株式スクリーニング・トレードゲーム")

if not st.session_state.screened_candidates:
    reset_and_scan()

if st.session_state.game_stage == "select":
    # ★ 見出しに日付を明記
    st.subheader(f"〜 90日前（{past_90_str}）から、本日（{today_str}）までの値動きを予測せよ 〜")
    st.write(f"システムは **{past_90_str}** の時点で時間を止め、全市場から3つの切り口で有望な銘柄を抽出しました。ここから **本日（{today_str}）** までの90日間の相場で、最も利益を叩き出す銘柄はどれか選択してください！")
    
    if st.button("🔄 市場を再スキャンして別の3銘柄を探す"):
        reset_and_scan()
        st.rerun()

    st.write("---")
    
    if not st.session_state.hints:
        with st.spinner("抽出結果に基づき、AIナビゲーターが分析レポートを作成中..."):
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
            
            # ★ HTMLタグを使い、キャラクターのアイコンを特大サイズで表示
            st.markdown(f"<div style='text-align: center; font-size: 70px; line-height: 1.2;'>{role['avatar']}</div>", unsafe_allow_html=True)
            
            # アイコンの下に寸評ボックスを配置
            st.info(st.session_state.hints.get(ticker, "解析中..."))
            
            st.write("")
            if st.button(f"{name} を選択してシミュレート", key=f"btn_{ticker}"):
                st.session_state.selected_ticker = ticker
                st.session_state.game_stage = "result"
                st.rerun()

elif st.session_state.game_stage == "result":
    st.subheader("🏁 自動売買シミュレーション 結果発表")
    # ★ 結果画面にも対象期間を明記
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

    st.write("---")
    if st.button("↩️ 市場を再スキャンして新しくゲームを始める"):
        reset_and_scan()
        st.rerun()