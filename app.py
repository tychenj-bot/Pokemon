import streamlit as st
import pandas as pd
import requests

# --- 設定 ---
st.set_page_config(page_title="寶可夢進化大全", layout="wide")

# --- 資料庫 (完整版預覽) ---
def load_full_data():
    data = [
        # 高耗能
        {"cat": "高耗能", "zh": "鯉魚王", "en": "magikarp", "candy": 400, "cond": "無"},
        {"cat": "高耗能", "zh": "美錄坦", "en": "meltan", "candy": 400, "cond": "需連接 Switch 或 Home 開啟神秘盒子"},
        {"cat": "高耗能", "zh": "燃燒蟲", "en": "larvesta", "candy": 400, "cond": "目前最難進化的非神獸"},
        {"cat": "高耗能", "zh": "童偶熊", "en": "stufful", "candy": 400, "cond": "無"},
        # 夥伴任務
        {"cat": "夥伴任務", "zh": "大蔥鴨(伽勒爾)", "en": "farfetchd-galar", "candy": 50, "cond": "夥伴狀態投 10 次 Excellent"},
        {"cat": "夥伴任務", "zh": "頑皮熊貓", "en": "pancham", "candy": 50, "cond": "夥伴狀態捕捉 32 隻惡屬性"},
        {"cat": "夥伴任務", "zh": "千針魚(洗翠)", "en": "qwilfish-hisui", "candy": 50, "cond": "夥伴狀態贏得 10 場團體戰"},
        {"cat": "夥伴任務", "zh": "布土撥", "en": "pawmo", "candy": 25, "cond": "夥伴狀態行走 25 公里"},
        {"cat": "夥伴任務", "zh": "火爆猴", "en": "primeape", "candy": 100, "cond": "夥伴狀態擊敗 30 隻幽靈或超能力系"},
        # 交換進化
        {"cat": "交換進化", "zh": "勇基拉", "en": "kadabra", "candy": 100, "cond": "交換後進化可免糖果"},
        {"cat": "交換進化", "zh": "地幔岩", "en": "boldore", "candy": 100, "cond": "交換後進化可免糖果"},
        {"cat": "交換進化", "zh": "小嘴蝸", "en": "shelmet", "candy": 50, "cond": "需與蓋蓋蟲交換"},
        # 環境與特殊
        {"cat": "環境/時間", "zh": "好啦魷", "en": "inkay", "candy": 50, "cond": "手機倒置 (螢幕朝下)"},
        {"cat": "環境/時間", "zh": "岩狗狗", "en": "rockruff", "candy": 50, "cond": "黃昏型態需在 17:00-18:00 進化"},
        {"cat": "環境/時間", "zh": "黏美兒", "en": "sliggoo", "candy": 100, "cond": "雨天或雨露誘餌模組"},
        {"cat": "環境/時間", "zh": "三蜜蜂", "en": "combee", "candy": 50, "cond": "僅限雌性可進化為蜂后"},
    ]
    return pd.DataFrame(data)

df = load_full_data()

# --- PokeAPI 獲取圖片 ---
@st.cache_data
def get_poke_img(en_name):
    try:
        res = requests.get(f"https://pokeapi.co/api/v2/pokemon/{en_name.lower()}")
        if res.status_code == 200:
            return res.json()["sprites"]["other"]["official-artwork"]["front_default"]
    except:
        return None

# --- UI 介面 ---
st.title("📖 寶可夢特殊進化條件完整百科")

# 側邊欄篩選
st.sidebar.header("過濾工具")
category = st.sidebar.multiselect("選擇進化類型", options=df["cat"].unique(), default=df["cat"].unique())
search_name = st.sidebar.text_input("搜尋名稱 (中/英文)", "")

# 邏輯過濾
mask = (df["cat"].isin(category)) & (df["zh"].str.contains(search_name) | df["en"].str.contains(search_name.lower()))
filtered_df = df[mask]

# 顯示網格
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
    st.info("沒有找到相符的寶可夢。")

# --- 下載區 ---
st.sidebar.divider()
csv = df.to_csv(index=False).encode('utf-8-sig')
st.sidebar.download_button("📥 下載完整對照表 CSV", csv, "pokemon_evolution.csv", "text/csv")
