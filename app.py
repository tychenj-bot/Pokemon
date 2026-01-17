import streamlit as st
import pandas as pd
import requests
import math

# --- 網頁配置 ---
st.set_page_config(page_title="PokeEvolve Pro - 專業進化圖鑑", layout="wide", page_icon="🧪")

# --- 1. 顏色與常數定義 ---
TYPE_COLORS = {
    "fire": "#FF421C", "water": "#6390F0", "grass": "#7AC74C", "electric": "#F7D02C",
    "ice": "#96D9D6", "fighting": "#C22E28", "poison": "#A33EA1", "ground": "#E2BF65",
    "flying": "#A98FF3", "psychic": "#F95587", "bug": "#A8B820", "rock": "#B6A136",
    "ghost": "#735797", "dragon": "#6F35FC", "dark": "#705746", "steel": "#B7B7CE",
    "fairy": "#D685AD", "normal": "#A8A77A"
}

# --- 2. 核心功能函式 ---

@st.cache_data
def load_csv():
    """載入進化資料庫"""
    try:
        return pd.read_csv("evolution.csv")
    except:
        st.error("請確認 GitHub 儲存庫中是否有 evolution.csv 檔案")
        return pd.DataFrame()

@st.cache_data
def get_poke_api_data(en_name):
    """獲取 PokeAPI 詳細數據、種族值與進化鏈"""
    try:
        # 獲取基本資訊
        res = requests.get(f"https://pokeapi.co/api/v2/pokemon/{en_name.lower()}")
        if res.status_code != 200: return None
        data = res.json()
        
        # 獲取進化鏈資訊 (需先獲取 species)
        species_res = requests.get(data["species"]["url"])
        species_data = species_res.json()
        evol_chain_url = species_data["evolution_chain"]["url"]
        
        return {
            "id": data["id"],
            "img": data["sprites"]["other"]["official-artwork"]["front_default"],
            "types": [t["type"]["name"] for t in data["types"]],
            "stats": {s["stat"]["name"]: s["base_stat"] for s in data["stats"]},
            "height": data["height"] / 10,
            "weight": data["weight"] / 10,
            "evol_chain_url": evol_chain_url
        }
    except:
        return None

def calculate_estimated_cp(stats):
    """
    使用使用者提供的公式估算強度值 (CP Estimator)
    公式: CP = (Atk * sqrt(Def) * sqrt(Sta)) / 10
    注意: PokeAPI 的 hp 對應 Sta
    """
    atk = stats.get("attack", 0)
    dfn = stats.get("defense", 0)
    sta = stats.get("hp", 0)
    
    cp_value = (atk * math.sqrt(dfn) * math.sqrt(sta)) / 10
    return int(cp_value)

# --- 3. UI 介面實作 ---

st.title("🧪 PokeEvolve Pro 專業進化計算圖鑑")
st.markdown("---")

df = load_csv()

# 側邊欄：搜尋與過濾
st.sidebar.header("🔍 搜尋篩選")
cat_list = ["全部"] + list(df["cat"].unique())
selected_cat = st.sidebar.selectbox("進化分類", cat_list)
search_name = st.sidebar.text_input("輸入名稱 (中/英)", "")

# 側邊欄：糖果計算機全域設定
st.sidebar.divider()
st.sidebar.header("🍬 糖果計算機")
current_candies = st.sidebar.number_input("目前擁有的糖果總數", min_value=0, value=0)

# 過濾邏輯
filtered_df = df if selected_cat == "全部" else df[df["cat"] == selected_cat]
if search_name:
    filtered_df = filtered_df[filtered_df["zh"].str.contains(search_name) | filtered_df["en"].str.contains(search_name.lower())]

# --- 4. 顯示結果 ---

if not filtered_df.empty:
    for _, row in filtered_df.iterrows():
        with st.container(border=True):
            col_img, col_info, col_calc = st.columns([1.2, 2, 1.8])
            
            api_data = get_poke_api_data(row['en'])
            
            with col_img:
                if api_data:
                    st.image(api_data["img"], use_container_width=True)
                    # 屬性標籤
                    type_html = ""
                    for t in api_data["types"]:
                        color = TYPE_COLORS.get(t, "#777")
                        type_html += f'<span style="background-color:{color}; color:white; padding:2px 8px; border-radius:10px; margin-right:5px; font-size:12px;">{t.upper()}</span>'
                    st.markdown(type_html, unsafe_allow_html=True)
                else:
                    st.warning("無法載入圖片")

            with col_info:
                st.subheader(f"{row['zh']}")
                st.write(f"🧬 **進化條件:** {row['cond']}")
                
                if api_data:
                    # CP 估算顯示
                    cp = calculate_estimated_cp(api_data["stats"])
                    st.metric("估算強度基數 (CP Index)", f"⚡ {cp}")
                    
                    # 種族值簡單條形圖
                    st.write("**📊 種族值分佈**")
                    s = api_data["stats"]
                    chart_data = pd.DataFrame({
                        "屬性": ["HP", "攻擊", "防禦", "速度"],
                        "值": [s["hp"], s["attack"], s["defense"], s["speed"]]
                    })
                    st.bar_chart(chart_data.set_index("屬性"), horizontal=True, height=150)

            with col_calc:
                st.subheader("🧮 進化計算機")
                target_candy = row['candy']
                diff = target_candy - current_candies
                
                if diff <= 0:
                    st.success(f"✅ 糖果充足！可以進化。\n(剩餘: {abs(diff)} 顆)")
                else:
                    st.error(f"❌ 糖果不足：還差 {diff} 顆")
                    # 進階換算
                    st.write(f"🏃 需作為夥伴行走: **{diff * 5} km** (以 5km/顆計)")
                    st.write(f"🍎 需捕捉次數: **{math.ceil(diff / 3)}** 隻 (不含鳳梨果)")
                
                st.divider()
                # 簡單進化鏈提示 (顯示當前 ID 的關聯)
                if api_data:
                    st.caption(f"🔗 PokeAPI 索引 ID: #{api_data['id']}")
                    st.caption("🔍 進化鏈路徑已鎖定，建議查看遊戲內進化按鈕。")

else:
    st.info("請調整篩選條件或確認 CSV 資料。")

# --- 5. 下載功能 ---
st.sidebar.divider()
csv_data = df.to_csv(index=False).encode('utf-8-sig')
st.sidebar.download_button("📥 匯出資料庫 (CSV)", csv_data, "evolution_data.csv", "text/csv")
