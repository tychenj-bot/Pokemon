import streamlit as st
import pandas as pd
import requests
import math

# --- 1. 網頁配置 ---
st.set_page_config(page_title="PokeEvolve Pro - 專業圖導航", layout="wide", page_icon="🐾")

# --- 2. 注入自定義 CSS (包含懸浮效果與標頭裝飾) ---
def local_css():
    st.markdown("""
        <style>
        /* 整體背景 */
        .main { background-color: #f8f9fa; }
        
        /* Pokedex 紅色標題裝飾 */
        .pokedex-header {
            background-color: #E63946;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            color: white;
            box-shadow: 0 4px 15px rgba(230, 57, 70, 0.3);
            margin-bottom: 30px;
        }

        /* 核心卡片懸浮效果 (滑鼠經過位移與陰影) */
        [data-testid="stVerticalBlockBorderWrapper"] {
            transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease !important;
            border-radius: 15px !important;
            background-color: white !important;
        }
        
        [data-testid="stVerticalBlockBorderWrapper"]:hover {
            transform: translateY(-8px) !important;
            box-shadow: 0 12px 24px rgba(0,0,0,0.15) !important;
            border-color: #E63946 !important;
        }

        /* 屬性標籤樣式 */
        .type-badge {
            color: white;
            padding: 3px 12px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: bold;
            text-transform: uppercase;
            margin-right: 5px;
            display: inline-block;
            box-shadow: 1px 1px 3px rgba(0,0,0,0.1);
        }

        /* 自定義捲軸樣式 */
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-thumb { background: #E63946; border-radius: 10px; }
        </style>
    """, unsafe_allow_html=True)

local_css()

# --- 3. 核心功能與資料處理 ---
TYPE_COLORS = {
    "fire": "#FF421C", "water": "#6390F0", "grass": "#7AC74C", "electric": "#F7D02C",
    "ice": "#96D9D6", "fighting": "#C22E28", "poison": "#A33EA1", "ground": "#E2BF65",
    "flying": "#A98FF3", "psychic": "#F95587", "bug": "#A8B820", "rock": "#B6A136",
    "ghost": "#735797", "dragon": "#6F35FC", "dark": "#705746", "steel": "#B7B7CE",
    "fairy": "#D685AD", "normal": "#A8A77A"
}

@st.cache_data
def load_data():
    try:
        # 讀取 GitHub 上的 evolution.csv
        df = pd.read_csv("evolution.csv")
        return df
    except:
        st.error("⚠️ 讀取失敗：請確認 evolution.csv 檔案存在且格式正確。")
        return pd.DataFrame()

@st.cache_data
def get_poke_data(en_name):
    """串接 PokeAPI 獲取圖片與種族值"""
    try:
        res = requests.get(f"https://pokeapi.co/api/v2/pokemon/{en_name.lower()}")
        if res.status_code == 200:
            d = res.json()
            return {
                "id": d["id"],
                "img": d["sprites"]["other"]["official-artwork"]["front_default"],
                "types": [t["type"]["name"] for t in d["types"]],
                "stats": {s["stat"]["name"]: s["base_stat"] for s in d["stats"]}
            }
    except: return None

def calc_cp_index(stats):
    """強度估算公式"""
    atk = stats.get("attack", 0)
    dfn = stats.get("defense", 0)
    sta = stats.get("hp", 0)
    return int((atk * math.sqrt(dfn) * math.sqrt(sta)) / 10)

# --- 4. 側邊欄配置 (過濾工具) ---
df = load_data()

st.sidebar.header("🔍 圖鑑搜尋與篩選")

# 文字搜尋框
search_query = st.sidebar.text_input("輸入名稱搜尋 (中/英)", "")

# 分類下拉選單
if not df.empty:
    cat_list = ["全部顯示"] + list(df["cat"].unique())
    selected_cat = st.sidebar.selectbox("進化分類過濾", cat_list)
else:
    selected_cat = "全部顯示"

st.sidebar.divider()

# 糖果計算機
st.sidebar.header("🍬 進化試算")
current_candy = st.sidebar.number_input("您目前擁有的糖果數", min_value=0, value=0)

# --- 5. 過濾邏輯實作 ---
if selected_cat == "全部顯示":
    temp_df = df
else:
    temp_df = df[df["cat"] == selected_cat]

if search_query:
    filtered_df = temp_df[
        temp_df["zh"].str.contains(search_query) | 
        temp_df["en"].str.contains(search_query.lower())
    ]
else:
    filtered_df = temp_df

# --- 6. 頁面主體顯示 ---
st.markdown('<div class="pokedex-header"><h1>🛡️ POKÉDEX PRO</h1><p>全地區型態進化特殊條件與戰力分析系統</p></div>', unsafe_allow_html=True)

if not filtered_df.empty:
    # 建立三欄佈局
    grid_cols = st.columns(3)
    
    for idx, row in filtered_df.reset_index().iterrows():
        with grid_cols[idx % 3]:
            # 建立具備 CSS 懸浮效果的容器
            with st.container(border=True):
                api_data = get_poke_data(row['en'])
                
                # 佈局：上方圖片與基本資訊
                img_col, info_col = st.columns([1, 1.2])
                with img_col:
                    if api_data:
                        st.image(api_data["img"], use_container_width=True)
                    else:
                        st.markdown("<h2 style='text-align:center;'>❓</h2>", unsafe_allow_html=True)
                
                with info_col:
                    st.subheader(row['zh'])
                    if api_data:
                        # 渲染屬性標籤
                        badges = ""
                        for t in api_data["types"]:
                            color = TYPE_COLORS.get(t, "#777")
                            badges += f'<span class="type-badge" style="background-color:{color};">{t.upper()}</span>'
                        st.markdown(badges, unsafe_allow_html=True)
                        
                        # 強度基數顯示
                        cp = calc_cp_index(api_data["stats"])
                        st.metric("戰力基數", f"⚡ {cp}")
                
                st.divider()
                
                # 下方詳細進化條件
                st.write(f"🍬 **進化糖果:** {row['candy']}")
                st.info(f"💡 **特殊條件:**\n{row['cond']}")
                
                # 糖果計算機結果
                diff = row['candy'] - current_candy
                if diff > 0:
                    st.caption(f"🚩 尚差 {diff} 顆糖果 (約捕捉 {math.ceil(diff/3)} 隻)")
                else:
                    st.success("✅ 糖果條件已達成！")
else:
    st.info("沒有找到符合條件的寶可夢，請嘗試調整搜尋字詞或分類。")

# --- 底部宣告 ---
st.divider()
st.caption("Data source: PokeAPI & Community Wiki | Created with Streamlit")
