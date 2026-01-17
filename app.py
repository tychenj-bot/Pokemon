import streamlit as st
import pandas as pd
import requests
import math

# --- 1. 網頁配置 ---
st.set_page_config(page_title="PokeEvolve Pro - 互動圖鑑", layout="wide", page_icon="🐾")

# --- 2. 注入自定義 CSS (包含懸浮效果) ---
def local_css():
    st.markdown("""
        <style>
        /* 整體背景與字體 */
        .main { background-color: #f4f4f9; }
        
        /* Pokedex 紅色標題裝飾 */
        .pokedex-header {
            background-color: #E63946;
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            color: white;
            box-shadow: 0 4px 15px rgba(230, 57, 70, 0.3);
            margin-bottom: 25px;
        }

        /* 核心卡片懸浮效果 */
        [data-testid="stVerticalBlockBorderWrapper"] {
            transition: transform 0.3s ease, box-shadow 0.3s ease !important;
            border-radius: 15px !important;
        }
        
        [data-testid="stVerticalBlockBorderWrapper"]:hover {
            transform: translateY(-8px) scale(1.01) !important;
            box-shadow: 0 12px 24px rgba(0,0,0,0.15) !important;
            border-color: #E63946 !important;
        }

        /* 屬性標籤樣式 */
        .type-badge {
            color: white;
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: bold;
            text-transform: uppercase;
            margin-right: 5px;
            display: inline-block;
        }

        /* 自定義捲軸 */
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-thumb { background: #E63946; border-radius: 10px; }
        </style>
    """, unsafe_allow_html=True)

local_css()

# --- 3. 常數與輔助函式 ---
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
        df = pd.read_csv("evolution.csv")
        return df
    except:
        st.error("找不到 evolution.csv 檔案")
        return pd.DataFrame()

@st.cache_data
def get_poke_data(en_name):
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
    atk = stats.get("attack", 0)
    dfn = stats.get("defense", 0)
    sta = stats.get("hp", 0)
    return int((atk * math.sqrt(dfn) * math.sqrt(sta)) / 10)

# --- 4. 介面內容 ---
st.markdown('<div class="pokedex-header"><h1>🐾 POKÉDEX PRO</h1><p>互動式進化百科與戰力分析系統</p></div>', unsafe_allow_html=True)

df = load_data()

# 側邊欄設定
st.sidebar.header("⚙️ 控制面板")
search = st.sidebar.text_input("搜尋寶可夢 (中/英)", "")
current_candy = st.sidebar.number_input("當前糖果數量", min_value=0, value=0)

# 資料過濾
filtered_df = df[df["zh"].str.contains(search) | df["en"].str.contains(search.lower())] if search else df

# 顯示卡片網格
if not filtered_df.empty:
    cols = st.columns(3)
    for idx, row in filtered_df.reset_index().iterrows():
        with cols[idx % 3]:
            # 建立具備懸浮效果的容器
            with st.container(border=True):
                api_data = get_poke_data(row['en'])
                
                # 佈局：上方圖片與標題
                c1, c2 = st.columns([1, 1.2])
                with c1:
                    if api_data:
                        st.image(api_data["img"], use_container_width=True)
                    else:
                        st.write("❓")
                
                with c2:
                    st.subheader(row['zh'])
                    if api_data:
                        # 顯示彩色標籤
                        badge_html = ""
                        for t in api_data["types"]:
                            color = TYPE_COLORS.get(t, "#777")
                            badge_html += f'<span class="type-badge" style="background-color:{color};">{t}</span>'
                        st.markdown(badge_html, unsafe_allow_html=True)
                        
                        cp = calc_cp_index(api_data["stats"])
                        st.metric("戰力基數", f"⚡ {cp}")

                # 下方詳細資訊
                st.divider()
                st.write(f"🍬 **進化需求:** {row['candy']} 顆")
                st.info(f"💡 **條件:** {row['cond']}")
                
                # 糖果計算機邏輯
                diff = row['candy'] - current_candy
                if diff > 0:
                    st.caption(f"🚩 還差 {diff} 顆糖果 (約需捕捉 {math.ceil(diff/3)} 隻)")
                else:
                    st.success("✅ 糖果已達標！")
                
                # 加入叫聲彩蛋
                if api_data:
                    cry_url = f"https://raw.githubusercontent.com/PokeAPI/cries/master/cries/pokemon/latest/{api_data['id']}.ogg"
                    st.audio(cry_url, format="audio/ogg")
else:
    st.info("查無此寶可夢，請嘗試其他關鍵字。")
