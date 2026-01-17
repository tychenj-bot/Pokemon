import streamlit as st
import pandas as pd
import requests

# --- 網頁配置 ---
st.set_page_config(page_title="PokeEvolve - 寶可夢進化百科", page_icon="⚡", layout="wide")

# --- PokeAPI 輔助函式 ---
def get_pokemon_info(name_en):
    """從 PokeAPI 抓取圖片與基本資訊"""
    url = f"https://pokeapi.co/api/v2/pokemon/{name_en.lower()}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return {
            "id": data["id"],
            "image": data["sprites"]["other"]["official-artwork"]["front_default"],
            "types": [t["type"]["name"] for t in data["types"]]
        }
    return None

# --- 進化資料庫 (自定義特殊條件) ---
# 這裡整理了 Pokemon GO 中常見的特殊進化
def get_evolution_data():
    return [
        {"中文名": "鯉魚王", "英文名": "magikarp", "分類": "高消耗進化", "糖果": 400, "條件": "無"},
        {"中文名": "大蔥鴨(伽勒爾)", "英文名": "farfetchd-galar", "分類": "戰鬥任務", "糖果": 50, "條件": "作為夥伴投出 10 次 Excellent"},
        {"中文名": "伊布(仙子伊布)", "英文名": "sylveon", "分類": "夥伴進化", "糖果": 25, "條件": "夥伴心心達到 70 顆"},
        {"中文名": "勇基拉", "英文名": "kadabra", "分類": "交換進化", "糖果": 100, "條件": "交換後可 0 糖果進化"},
        {"中文名": "小嘴蝸", "英文名": "shelmet", "分類": "交換進化", "糖果": 50, "條件": "需與蓋蓋蟲交換"},
        {"中文名": "頑皮熊貓", "英文名": "pancham", "分類": "特殊任務", "糖果": 50, "條件": "夥伴狀態捕捉 32 隻惡屬性"},
        {"中文名": "好啦魷", "英文名": "inkay", "分類": "體感操作", "糖果": 50, "條件": "將手機倒過來進行進化"},
    ]

# --- 介面開始 ---
st.title("🐾 寶可夢進化特殊條件索引 (PokeAPI 連動)")
st.write("本系統串接 PokeAPI 自動獲取圖片，並整理 Pokemon GO 特殊進化需求。")

# 讀取資料
raw_data = get_evolution_data()
df = pd.DataFrame(raw_data)

# --- 側邊欄過濾 ---
st.sidebar.header("搜尋篩選")
all_categories = ["全部"] + list(df["分類"].unique())
selected_cat = st.sidebar.selectbox("選擇進化分類", all_categories)

# 過濾邏輯
if selected_cat != "全部":
    display_df = df[df["分類"] == selected_cat]
else:
    display_df = df

# --- 分類標籤 (Tabs) ---
tab_list, tab_search = st.tabs(["📜 特殊進化清單", "🔍 單一寶可夢查詢"])

with tab_list:
    # 使用網格佈局 (Columns) 顯示卡片
    cols = st.columns(3)
    for index, row in display_df.iterrows():
        with cols[index % 3]:
            # 獲取 API 資料
            api_info = get_pokemon_info(row["英文名"])
            
            with st.container(border=True):
                if api_info:
                    st.image(api_info["image"], use_container_width=True)
                st.subheader(row["中文名"])
                st.markdown(f"**分類：** `{row['分類']}`")
                st.markdown(f"**🍬 糖果需求：** {row['糖果']}")
                st.info(f"**進化條件：**\n{row['條件']}")

with tab_search:
    st.subheader("任意寶可夢資訊查詢 (PokeAPI 直連)")
    search_input = st.text_input("輸入寶可夢英文名稱 (如: Pikachu, Eevee, Charizard)", "Eevee")
    
    if search_input:
        info = get_pokemon_info(search_input)
        if info:
            col_a, col_b = st.columns([1, 2])
            with col_a:
                st.image(info["image"])
            with col_b:
                st.write(f"### 編號: #{info['id']}")
                st.write(f"### 屬性: {', '.join(info['types'])}")
                st.success("此資料直接從 PokeAPI 抓取，若為特殊進化請參考左側清單。")
        else:
            st.error("找不到該寶可夢，請確認英文名稱是否正確。")

# --- 底部宣告 ---
st.divider()
st.caption("Data provided by PokeAPI.co | 寶可夢特殊進化數據由社群整理")
