import streamlit as st
import pandas as pd
import plotly.express as px
from openai import OpenAI
import datetime
import numpy as np
import requests
from supabase import create_client, Client # 新增：数据库连接库

# --- 0. 核心配置与 Supabase 连接 ---
DEFAULT_API_KEY = "sk-051a17fa2f404ba2a9459d5f356de93b"
LOVE_START_DATE = datetime.date(2025, 1, 1)

# 请在此处填入你的 Supabase 配置
SUPABASE_URL = "https://tqtejtfkqxkfrnelqczn.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRxdGVqdGZrcXhrZnJuZWxxY3puIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY5NTgxMjksImV4cCI6MjA4MjUzNDEyOX0.9gBVQZhFBFg9a9hm0d6BUW-s8yhCGPIjwmbLLZ9F0Ow"

@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# --- 1. 数据库持久化函数 ---
def load_all_data():
    """从数据库加载历史数据到 SessionState"""
    try:
        # 加载体重
        w_res = supabase.table("weight_data").select("*").order("weight_date").execute()
        st.session_state.weight_data_list = [{"日期": r['weight_date'], "体重": r['weight']} for r in w_res.data]
        if not st.session_state.weight_data_list: # 初始兜底
             st.session_state.weight_data_list = [{"日期": "2025-12-28", "体重": 65.0}]
        
        # 加载日记
        l_res = supabase.table("daily_logs").select("*").order("log_date", desc=True).execute()
        st.session_state.daily_logs = l_res.data
    except Exception as e:
        st.error(f"数据库读取失败: {e}")

def save_log_to_supabase(log_entry):
    """保存单条日记"""
    supabase.table("daily_logs").insert({
        "log_date": log_entry["日期"],
        "sports": log_entry["运动"],
        "diet": log_entry["饮食"],
        "is_poop": log_entry["大便"],
        "water": log_entry["饮水"],
        "work": log_entry["工作"],
        "detail": log_entry["详情"],
        "mood": log_entry["心情"]
    }).execute()

def save_weight_to_supabase(date, weight):
    """保存单条体重"""
    supabase.table("weight_data").insert({
        "weight_date": str(date),
        "weight": weight
    }).execute()

# --- 2. 基础配置与 UI 样式 ---
st.set_page_config(page_title="2026东京之约 | 专属空间", layout="wide", page_icon="🗼")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #fff5f7 0%, #f0f4ff 100%); }
    [data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.7) !important;
        border-radius: 20px !important; padding: 20px !important;
        border: 1px solid #ffe4e8 !important; text-align: center !important;
        box-shadow: 0 4px 15px rgba(255, 182, 193, 0.1) !important;
    }
    [data-testid="stMetricValue"] > div, [data-testid="stMetricLabel"] > div {
        display: flex !important; justify-content: center !important; align-items: center !important; width: 100%;
    }
    [data-testid="stMetricValue"] > div { color: #ff6b81 !important; }
    [data-testid="stMetricLabel"] > div { color: #6a89cc !important; }
    div[data-testid="stForm"], div[data-testid="stExpander"] {
        background-color: rgba(255, 255, 255, 0.8) !important; border-radius: 20px !important; border: 1px solid #ffe4e8 !important;
    }
    h1, h2, h3 { color: #ff6b81 !important; text-align: center !important; }
    .stButton>button { width: 100%; border-radius: 25px !important; background-color: #ff6b81 !important; color: white !important; border: none !important; height: 3em; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 工具函数 ---
def get_weather(city_pinyin):
    api_key = "3f4ff1ded1a1a5fc5335073e8cf6f722"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_pinyin}&appid={api_key}&units=metric&lang=zh_cn"
    try:
        res = requests.get(url, timeout=3).json()
        return {"temp": res['main']['temp'], "desc": res['weather'][0]['description'], "icon": res['weather'][0]['icon']}
    except: return None

def get_prediction(df):
    if len(df) < 2: return None, 0
    try:
        temp_df = df.copy()
        temp_df['日期_ts'] = pd.to_datetime(temp_df['日期']).map(datetime.date.toordinal)
        x, y = temp_df['日期_ts'].values, temp_df['体重'].values.astype(float)
        slope, intercept = np.polyfit(x, y, 1)
        if slope < 0:
            target_date = datetime.date.fromordinal(int((55.0 - intercept) / slope))
            return target_date, slope
        return "趋势平缓", slope
    except: return None, 0

# --- 4. 数据初始化 (修改为从 DB 加载) ---
if 'data_loaded' not in st.session_state:
    load_all_data()
    st.session_state.data_loaded = True

# --- 5. 侧边栏 ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>🗼 2026 东京之约</h2>", unsafe_allow_html=True)
    days_left = (datetime.date(2026, 6, 23) - datetime.date.today()).days
    st.metric("距离重逢还有", f"{days_left} 天")
    st.progress(max(0, min(100, 100 - int(days_left / 540 * 100))))
    st.divider()
    st.markdown("<p style='text-align: center; font-weight: bold;'>🌍 时空同步</p>", unsafe_allow_html=True)
    w_tokyo, w_shantou = get_weather("Tokyo"), get_weather("Shantou")
    c1, c2 = st.columns(2)
    if w_tokyo: c1.markdown(f"<div style='text-align:center;'><img src='http://openweathermap.org/img/wn/{w_tokyo['icon']}.png' width='45'><br>东京<br>{w_tokyo['temp']}°C</div>", unsafe_allow_html=True)
    if w_shantou: c2.markdown(f"<div style='text-align:center;'><img src='http://openweathermap.org/img/wn/{w_shantou['icon']}.png' width='45'><br>汕头<br>{w_shantou['temp']}°C</div>", unsafe_allow_html=True)
    st.divider()
    api_key_input = st.text_input("🔑 小耗子专属秘钥", value=DEFAULT_API_KEY, type="password")

# --- 6. 主界面 ---
st.markdown("<h1 style='text-align: center;'>💖 小耗子和小夏的秘密基地</h1>", unsafe_allow_html=True)
days_together = (datetime.date.today() - LOVE_START_DATE).days
st.markdown(f"### 我们已经并肩作战了 {days_together} 天 🎉")
st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs(["🌸 生活时光机", "📉 数学减脂美学", "🎒 东京大冒险", "💌 元旦秘密信箱"])

with tab1:
    col_l, col_r = st.columns([2, 1])
    with col_l:
        with st.form("daily_form_v12", clear_on_submit=True):
            st.subheader("📝 记录今日点滴")
            log_date = st.date_input("日期", datetime.date.today())
            sports = st.multiselect("🏃 运动健身", ["呼啦圈", "散步", "打羽毛球"])
            sport_time = st.slider("⏱️ 运动时长 (分钟)", 0, 120, 30)
            diet = st.select_slider("🥗 饮食控制", options=["放纵餐🍕", "正常饮食🍚", "清淡少油🥗", "严格减脂🥦"], value="正常饮食🍚")
            st.write("---")
            ch1, ch2 = st.columns(2)
            with ch1: is_poop = st.radio("💩 今日是否大便？", ["未排便", "顺利排便 ✅"], horizontal=True)
            with ch2: water = st.slider("💧 饮水量 (L)", 0.5, 4.0, 2.0, 0.5)
            st.write("---")
            work = st.multiselect("💻 工作与学术", ["看文献", "写大论文", "写小论文", "阅读就业信息"])
            work_focus = st.select_slider("🎯 专注情况", options=["完全走神😴", "断断续续☕", "比较专注📚", "深度心流🔥"], value="比较专注📚")
            work_time = st.slider("⏳ 累计时长 (小时)", 0.0, 14.0, 4.0, step=0.5)
            detail = st.text_area("💌 碎碎念...", placeholder="在此处写下你想对小耗子说的话...")
            mood = st.select_slider("✨ 心情", options=["😢", "😟", "😐", "😊", "🥰"], value="😊")

            if st.form_submit_button("存入时光机"):
                new_entry = {
                    "日期": str(log_date), "运动": f"{'|'.join(sports)}({sport_time}min)",
                    "饮食": diet, "大便": is_poop, "饮水": water,
                    "工作": f"{'|'.join(work)}({work_time}h - {work_focus})", "详情": detail, "心情": mood
                }
                # 保存到数据库
                save_log_to_supabase(new_entry)
                # 重新加载显示
                load_all_data()
                st.rerun()

        if st.session_state.daily_logs:
            st.subheader("📜 往日回忆")
            for log in st.session_state.daily_logs:
                # 适配数据库字段名（如果是从DB读出来的，Key可能是英文或中文，这里做个兼容）
                l_date = log.get("log_date") or log.get("日期")
                l_mood = log.get("mood") or log.get("心情")
                with st.expander(f"📅 {l_date} - 心情: {l_mood}"):
                    st.write(f"**🏃 运动：** {log.get('sports') or log.get('运动')} | **🥗 饮食：** {log.get('diet') or log.get('饮食')} | **💩 排便：** {log.get('is_poop') or log.get('大便')}")
                    st.write(f"**💻 进度：** {log.get('work') or log.get('工作')} | **💧 饮水：** {log.get('water') or log.get('饮水')}L")
                    txt = log.get('detail') or log.get('详情')
                    if txt:
                        st.markdown(f"""<div style="background-color: #fff0f3; padding: 12px; border-radius: 12px; border-left: 4px solid #ff6b81; margin-top: 10px;">
                            <span style="color: #ff6b81; font-weight: bold;">💌 给小耗子的私语：</span><br>
                            <span style="color: #555; font-style: italic;">{txt}</span></div>""", unsafe_allow_html=True)

    with col_r:
        st.markdown("### 💌 小耗子的叮嘱")
        quotes = ["为了见你，我正在东京努力变优秀。", "所有的数学斜率，最终都会指向我们的重逢。", "不仅要瘦，还要健康，这是小耗子唯一的命令。"]
        st.write(f"*{np.random.choice(quotes)}*")
        if st.button("查看全维度深度审计报告", use_container_width=True):
            if api_key_input and st.session_state.daily_logs:
                with st.spinner("审计中..."):
                    try:
                        df_w = pd.DataFrame(st.session_state.weight_data_list)
                        pred_date, slope = get_prediction(df_w)
                        last = st.session_state.daily_logs[0] # 数据库已排好序，最新的是第一个
                        client = OpenAI(api_key=api_key_input, base_url="https://api.deepseek.com")
                        prompt = f"你是‘小耗子’。当前体重{df_w['体重'].iloc[-1]}kg，斜率{slope:.3f}。排便{last.get('is_poop')}，饮水{last.get('water')}L。饮食{last.get('diet')}，工作{last.get('work')}。请给出现状分析、饮食处方、运动方案和暖心总结。"
                        response = client.chat.completions.create(model="deepseek-chat", messages=[{"role": "system", "content": "你是一个理性的理科生伴侣。"},{"role": "user", "content": prompt}], temperature=0.3)
                        st.info(response.choices[0].message.content)
                    except: st.error("AI 暂时离线")

with tab2:
    df_weight = pd.DataFrame(st.session_state.weight_data_list)
    df_weight['日期'] = pd.to_datetime(df_weight['日期'])
    calc_df = df_weight.sort_values('日期').drop_duplicates('日期', keep='last')
    pred_res, slope = get_prediction(calc_df)
    st.markdown("### 📈 数据背后的爱与科学")
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("日均斜率 (kg/d)", f"{slope:.3f}")
    with c2: st.metric("距离 55kg 还差", f"{round(calc_df['体重'].iloc[-1] - 55.0, 1)} kg")
    with c3: st.metric("预估达标日", pred_res.strftime('%Y-%m-%d') if isinstance(pred_res, datetime.date) else "测算中")
    with st.form("weight_v12"):
        cw1, cw2 = st.columns(2)
        nw, nd = cw1.number_input("体重 (kg)", value=float(calc_df['体重'].iloc[-1]), step=0.1), cw2.date_input("测量日期", datetime.date.today())
        if st.form_submit_button("更新数学模型"):
            save_weight_to_supabase(nd, nw)
            load_all_data()
            st.rerun()
    st.plotly_chart(px.line(calc_df, x="日期", y="体重", markers=True, color_discrete_sequence=['#ff6b81']), use_container_width=True)

with tab3:
    st.markdown("<h2 style='text-align: center;'>🎆 东京冒险清单：夏日花火之约</h2>", unsafe_allow_html=True)
    ca1, ca2 = st.columns([1, 1])
    with ca1:
        st.markdown("### 🎯 我们的专属约定")
        st.checkbox("✨ 参加东京夏夜花火大会！", value=False)
        st.write("（已规划最佳观赏点，和风浴衣也准备好了哦~）")
    with ca2: st.image("https://img.picgo.net/2024/05/22/fireworks_kimono_anime18090543e86c0757.md.png", use_container_width=True)

with tab4:
    st.markdown("## 📟 2026 跨年系统指令")
    input_pass = st.text_input("输入 Access Code：", type="password")
    if input_pass == "wwhaxxy1314":
        st.balloons()
        st.markdown("""<div style="background-color: #fff0f3; padding: 30px; border-radius: 20px; border: 2px dashed #ff6b81;">
            <h3 style="color: #ff6b81; text-align: center;">📅 2026.01.01</h3>
            <p style="color: #555; line-height: 1.8;">亲爱的小夏：跨过2025，我见证了你的努力。新的一年，愿你少一点焦虑，多一点顺畅。我们在终点见。<br><br>
            <span style="float: right;">—— [运维负责人: 小耗子 🐭]</span></p></div>""", unsafe_allow_html=True)
