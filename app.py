import streamlit as st
import pandas as pd
import requests

# --- 設定 ---
st.set_page_config(page_title="寶可夢進化大全", layout="wide")

# --- 讀取資料 (從 CSV 讀取) ---
@st.cache_data
def load_data():
    try:
        # 讀取同資料夾下的 evolution.csv
        df = pd.read_csv("evolution.csv")
        return df
    except FileNotFoundError:
        # 如果找不到檔案，回傳一個空表格避免程式崩潰
        st.error("找不到 evolution.csv 檔案，請確認檔案已上傳至 GitHub。")
        return pd.DataFrame(columns=["cat", "zh", "en", "candy", "cond"])

df = load_data()

# --- PokeAPI 獲取圖片 (加入快取) ---
@st.cache_data
def get_poke_img(en_name):
    try:
        res = requests.get(f"https://pokeapi.co/api/v2/pokemon/{en_name.lower()}")
        if res.status_code == 200:
            return res.json()["sprites"]["other"]["official-artwork"]["front_default"]
    except:
        return None

# --- UI 介面 ---
st.title("📖 寶可夢特殊進化條件百科")

# --- 側邊欄過濾工具 (改回下拉式選單) ---
st.sidebar.header("搜尋與篩選")

# 建立分類選單，加入「全部」選項
categories = ["全部"] + list(df["cat"].unique())
selected_cat = st.sidebar.selectbox("選擇進化類型", options=categories)

search_name = st.sidebar.text_input("搜尋名稱 (中/英文)", "")

# --- 過濾邏輯 ---
# 根據選單過濾
if selected_cat == "全部":
    filtered_df = df
else:
    filtered_df = df[df["cat"] == selected_cat]

# 根據搜尋框過濾
if search_name:
    filtered_df = filtered_df[
        filtered_df["zh"].str.contains(search_name) | 
        filtered_df["en"].str.contains(search_name.lower())
    ]

# --- 顯示結果 ---
if not filtered_df.empty:
    cols = st.columns(3)
    for idx, row in filtered_df.reset_index().iterrows():
        with cols[idx % 3]:
            with st.container(border=True):
                img_url = get_poke_img(row['en'])
                if img_url:
                    st.image(img_url, use_container_width=True)
                st.subheader(row['zh'])
                st.caption(f"英文名: {row['en'].capitalize()}")
                st.write(f"🍬 **所需糖果:** {row['candy']}")
                st.warning(f"💡 **條件:** {row['cond']}")
else:
    st.info("沒有找到符合條件的寶可夢。")

# --- 下載區 ---
st.sidebar.divider()
csv_data = df.to_csv(index=False).encode('utf-8-sig')
st.sidebar.download_button("📥 下載完整 CSV 清單", csv_data, "pokemon_evolution.csv", "text/csv")
