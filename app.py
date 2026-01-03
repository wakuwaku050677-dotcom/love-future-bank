import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
from datetime import datetime
import time

# ---------------------------------------------------------
# 1. 認証とスプレッドシートへの接続（魔法の鍵）
# ---------------------------------------------------------
# キャッシュを使って接続を高速化
@st.cache_resource
def get_gspread_client():
    # SecretsからJSONの中身を取り出す（文字列 -> 辞書に変換）
    key_dict = json.loads(st.secrets["gcp_service_account"]["json_content"])
    
    # 認証スコープの設定
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(key_dict, scope)
    client = gspread.authorize(creds)
    return client

# スプレッドシートを開く関数
def get_sheet():
    client = get_gspread_client()
    sheet_name = "future_bank_db"  # 作成したシート名
    try:
        sheet = client.open(sheet_name).sheet1
        return sheet
    except gspread.SpreadsheetNotFound:
        st.error(f"エラー：スプレッドシート '{sheet_name}' が見つかりません。共有設定を確認してください。")
        st.stop()

# ---------------------------------------------------------
# 2. データの読み書き
# ---------------------------------------------------------
def load_data():
    sheet = get_sheet()
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    
    # 空っぽの場合は初期化
    if df.empty:
        df = pd.DataFrame(columns=["日付", "名前", "アクション", "ポイント", "内容"])
        
    return df

def add_log(name, action, points, note):
    sheet = get_sheet()
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # 行を追加
    row = [date_str, name, action, points, note]
    sheet.append_row(row)
    
    # 成功メッセージ
    st.toast(f"✅ {points}pt ゲット！ ({action})")
    time.sleep(1) # ちょっと待ってからリロード
    st.rerun()

# ---------------------------------------------------------
# 3. アプリの画面構成
# ---------------------------------------------------------
st.set_page_config(page_title="ふたりの未来投資銀行", page_icon="🏦")

st.title("🏦 ふたりの未来投資銀行")
st.caption("Our Love & Future Investment Bank")

# サイドバー：ユーザー切り替え
st.sidebar.header("👤 ログイン")
user_name = st.sidebar.selectbox("あなたはだれ？", ["阿部", "あや"])

# 現在のデータを読み込み
df = load_data()

# ポイント集計
if not df.empty:
    total_points = df["ポイント"].sum()
    abe_points = df[df["名前"] == "阿部"]["ポイント"].sum()
    aya_points = df[df["名前"] == "あや"]["ポイント"].sum()
else:
    total_points = 0
    abe_points = 0
    aya_points = 0

# メトリクス表示（資産状況）
col1, col2, col3 = st.columns(3)
col1.metric("💰 二人の総資産", f"{total_points:,} pt")
col2.metric("👨 阿部の貢献", f"{abe_points:,} pt")
col3.metric("👩 あやの貢献", f"{aya_points:,} pt")

st.divider()

# ---------------------------------------------------------
# 4. アクションエリア（入力）
# ---------------------------------------------------------
st.header(f"📝 {user_name}のアクション")

tab1, tab2 = st.tabs(["💰 貯金・投資", "🏃 健康・ダイエット"])

with tab1:
    st.info("未来のためにお金を残した！")
    c1, c2, c3 = st.columns(3)
    if c1.button("つもり貯金 (+100pt)"):
        add_log(user_name, "つもり貯金", 100, "カフェ我慢など")
    if c2.button("外食我慢 (+300pt)"):
        add_log(user_name, "外食我慢", 300, "自炊した")
    
    # カスタム入力
    with st.expander("自由に入力する"):
        custom_yen = st.number_input("貯金額（円）", min_value=0, step=100)
        if st.button("入金する"):
            if custom_yen > 0:
                add_log(user_name, "入金", custom_yen, f"{custom_yen}円貯金")

with tab2:
    st.success("未来のために体をメンテナンスした！")
    c1, c2, c3 = st.columns(3)
    if c1.button("筋トレした (+50pt)"):
        add_log(user_name, "筋トレ", 50, "えらい！")
    if c2.button("野菜食べた (+30pt)"):
        add_log(user_name, "野菜摂取", 30, "ヘルシー")
    if c3.button("お菓子我慢 (+50pt)"):
        add_log(user_name, "お菓子我慢", 50, "誘惑に勝った")

st.divider()

# ---------------------------------------------------------
# 5. ご褒美ショップ（チケット交換）
# ---------------------------------------------------------
st.header("🎟️ ご褒美ショップ")
st.caption("貯めたポイントを使って、相手にお願いしよう！")

ticket_menu = {
    "肩揉み10分券": 300,
    "皿洗い免除券": 500,
    "好きな夕飯リクエスト": 1000,
    "週末お出かけ決定権": 2000
}

selected_ticket = st.selectbox("チケットを選ぶ", list(ticket_menu.keys()))
cost = ticket_menu[selected_ticket]

if st.button(f"購入する (-{cost} pt)"):
    # 現在のポイントをチェック（簡易版なのでマイナスも許容してますが、運用でカバー！）
    add_log(user_name, "チケット購入", -cost, selected_ticket)
    st.balloons()
    st.success(f"🎉 {selected_ticket} を購入しました！相手に画面を見せてね。")

st.divider()

# ---------------------------------------------------------
# 6. 通帳（履歴）
# ---------------------------------------------------------
with st.expander("📖 通帳を見る（履歴）"):
    if not df.empty:
        # 新しい順に表示
        st.dataframe(df.sort_index(ascending=False))
    else:
        st.write("まだ履歴がありません。")
