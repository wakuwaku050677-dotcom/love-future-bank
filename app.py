import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- Constants & Config ---
DATA_FILE = "couple_bank.csv"
USERS = ["阿部", "あや"]

ACTIONS = {
    "savings": {
        "label": "💰 貯金アクション",
        "items": [
            {"name": "つもり貯金", "points": 100, "type": "saving"},
            {"name": "外食我慢", "points": 300, "type": "saving"},
        ]
    },
    "diet": {
        "label": "🏃 ダイエットアクション",
        "items": [
            {"name": "筋トレした", "points": 50, "type": "diet"},
            {"name": "野菜食べた", "points": 30, "type": "diet"},
            {"name": "お菓子我慢", "points": 50, "type": "diet"},
        ]
    }
}

TICKETS = [
    {"name": "肩揉み10分券", "cost": 300},
    {"name": "皿洗い免除券", "cost": 500},
    {"name": "好きな夕飯リクエスト券", "cost": 1000},
    {"name": "週末お出かけプラン決定権", "cost": 2000},
]

# --- Functions ---

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            return pd.read_csv(DATA_FILE)
        except Exception:
            return pd.DataFrame(columns=["Timestamp", "User", "Type", "Category", "Item", "Value", "Points"])
    else:
        return pd.DataFrame(columns=["Timestamp", "User", "Type", "Category", "Item", "Value", "Points"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

def add_entry(user, type, category, item, value, points):
    df = load_data()
    new_entry = pd.DataFrame([{
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "User": user,
        "Type": type, # 'earn' or 'spend'
        "Category": category, # 'saving', 'diet', 'shop'
        "Item": item,
        "Value": value, # Amount for savings, or 1 for count
        "Points": points
    }])
    df = pd.concat([df, new_entry], ignore_index=True)
    save_data(df)

def get_balance(user):
    df = load_data()
    if df.empty:
        return 0
    user_data = df[df["User"] == user]
    return user_data["Points"].sum()

def get_global_stats():
    df = load_data()
    if df.empty:
        return 0, 0
    
    # Total Savings (Value where Category is saving)
    total_savings = df[df["Category"] == "saving"]["Value"].sum()
    
    # Total Diet Count (Count where Category is diet)
    total_diet = len(df[df["Category"] == "diet"])
    
    return total_savings, total_diet

# --- UI ---

st.set_page_config(page_title="ふたりの未来投資銀行", page_icon="🏦", layout="wide")

# Sidebar
st.sidebar.header("ログイン")
current_user = st.sidebar.radio("ユーザーを選択", USERS)

st.sidebar.markdown("---")
st.sidebar.markdown(f"### {current_user}さんの資産")
current_balance = get_balance(current_user)
st.sidebar.metric("現在のポイント", f"{current_balance} pt")


# Main Content
st.title("🏦 ふたりの未来投資銀行 🏦")
st.markdown("二人の頑張りを未来への投資に！")

# Global Settings / Stats
g_savings, g_diet = get_global_stats()
col1, col2 = st.columns(2)
with col1:
    st.metric("💰 ふたりの合計貯金額", f"¥{int(g_savings):,}")
with col2:
    st.metric("🏃 ふたりのダイエット回数", f"{g_diet} 回")

st.markdown("---")

tab1, tab2, tab3 = st.tabs(["💎 資産を増やす (稼ぐ)", "🎫 ご褒美ショップ (使う)", "📊 通帳を見る (履歴)"])

with tab1:
    st.header(f"{current_user}さんの投資アクション")
    
    col_save, col_diet = st.columns(2)
    
    with col_save:
        st.subheader(ACTIONS["savings"]["label"])
        for item in ACTIONS["savings"]["items"]:
            if st.button(f"{item['name']} (+{item['points']}pt)", key=f"save_{item['name']}"):
                add_entry(current_user, "earn", "saving", item['name'], item['points'], item['points']) # Approximation: Value=Points for fixed items, usually cash amount
                st.toast(f"{item['name']}を記録しました！ (+{item['points']}pt)", icon="💰")
                st.rerun()
        
        # Custom Saving Input
        with st.expander("入力をカスタマイズ (入金など)"):
            with st.form("custom_deposit"):
                amount = st.number_input("入金額 (円)", min_value=1, step=100)
                submit_deposit = st.form_submit_button("入金する (+金額分pt)")
                if submit_deposit:
                    add_entry(current_user, "earn", "saving", "入金", amount, amount)
                    st.toast(f"{amount}円を入金しました！ (+{amount}pt)", icon="💰")
                    st.rerun()

    with col_diet:
        st.subheader(ACTIONS["diet"]["label"])
        for item in ACTIONS["diet"]["items"]:
            if st.button(f"{item['name']} (+{item['points']}pt)", key=f"diet_{item['name']}"):
                add_entry(current_user, "earn", "diet", item['name'], 1, item['points'])
                st.toast(f"{item['name']}を記録しました！ (+{item['points']}pt)", icon="🏃")
                st.rerun()
        
        # Custom Diet Input
        with st.expander("入力をカスタマイズ"):
            with st.form("custom_diet"):
                diet_desc = st.text_input("内容")
                diet_pt = st.number_input("獲得ポイント", min_value=1, step=10)
                submit_diet = st.form_submit_button("記録する")
                if submit_diet and diet_desc:
                    add_entry(current_user, "earn", "diet", diet_desc, 1, diet_pt)
                    st.toast(f"{diet_desc}を記録しました！ (+{diet_pt}pt)", icon="🏃")
                    st.rerun()

with tab2:
    st.header("ご褒美チケットショップ")
    st.markdown(f"**{current_user}**さんが、パートナーのためにチケットを購入します。")
    st.caption("※購入するとポイントが消費されます")
    
    shop_cols = st.columns(2)
    for i, ticket in enumerate(TICKETS):
        col = shop_cols[i % 2]
        with col:
            with st.container(border=True):
                st.markdown(f"#### {ticket['name']}")
                st.markdown(f"**{ticket['cost']} pt**")
                if st.button("購入する", key=f"buy_{i}", disabled=(current_balance < ticket['cost'])):
                    add_entry(current_user, "spend", "shop", ticket['name'], 1, -ticket['cost'])
                    st.balloons()
                    st.success(f"{ticket['name']}を購入しました！")
                    st.rerun()
                if current_balance < ticket['cost']:
                    st.caption("ポイント不足")

with tab3:
    st.header("取引履歴")
    df = load_data()
    if not df.empty:
        # Latest first
        st.dataframe(df.sort_values(by="Timestamp", ascending=False), use_container_width=True)
        
        st.subheader("資産推移")
        # Simple cumulative sum for points by user
        # This is a bit complex to do cleanly in one line with pandas, need to pivot
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        df_sorted = df.sort_values('Timestamp')
        
        chart_data = pd.DataFrame()
        for u in USERS:
             user_df = df_sorted[df_sorted['User'] == u].copy()
             if not user_df.empty:
                 user_df['Cumulative Points'] = user_df['Points'].cumsum()
                 # We need to align timestamps for a nice multi-line chart, but for simplicty, let's just plot points over time per user
                 # A better way for Streamlit line chart is a wide format df
                 
        # Let's just group by Date for a simpler chart
        df_sorted['Date'] = df_sorted['Timestamp'].dt.date
        pivot_df = df_sorted.groupby(['Date', 'User'])['Points'].sum().groupby(level=0).cumsum().unstack().fillna(method='ffill')
        # This pivot might be wrong for cumulative balance. 
        # Correct approach: Calculate cumulative sum for each user, then merge or plot.
        
        # Simplified Chart: Just total points per category
        st.subheader("カテゴリー別貢献度")
        cat_chart = df[df['Points'] > 0].groupby(['User', 'Category'])['Points'].sum().unstack()
        st.bar_chart(cat_chart)

    else:
        st.info("データがまだありません。")