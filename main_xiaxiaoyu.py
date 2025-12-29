import streamlit as st
import pandas as pd
import plotly.express as px
from openai import OpenAI
import datetime
import numpy as np
import requests

# --- 0. 核心配置 ---
DEFAULT_API_KEY = "sk-051a17fa2f404ba2a9459d5f356de93b"
LOVE_START_DATE = datetime.date(2025, 1, 1)

# --- 1. 基础配置与高级 UI 美化 ---
st.set_page_config(page_title="2026东京之约 | 专属空间", layout="wide", page_icon="🗼")

st.markdown(f"""
    <style>
    /* 全局背景：粉蓝浪漫渐变 */
    .stApp {{
        background: linear-gradient(135deg, #fff5f7 0%, #f0f4ff 100%);
    }}

    /* 核心指标居中魔法 */
    [data-testid="stMetric"] {{
        background-color: rgba(255, 255, 255, 0.7) !important;
        border-radius: 20px !important;
        padding: 20px !important;
        border: 1px solid #ffe4e8 !important;
        text-align: center !important;
        box-shadow: 0 4px 15px rgba(255, 182, 193, 0.1) !important;
    }}

    /* 强制数值和标签垂直居中对齐 */
    [data-testid="stMetricValue"] > div, [data-testid="stMetricLabel"] > div {{
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        text-align: center !important;
        width: 100%;
    }}

    [data-testid="stMetricValue"] > div {{ color: #ff6b81 !important; }}
    [data-testid="stMetricLabel"] > div {{ color: #6a89cc !important; }}

    /* 表单与卡片样式 */
    div[data-testid="stForm"], div[data-testid="stExpander"] {{
        background-color: rgba(255, 255, 255, 0.8) !important;
        border-radius: 20px !important;
        border: 1px solid #ffe4e8 !important;
    }}

    /* 标题居中与配色 */
    h1, h2, h3 {{
        color: #ff6b81 !important;
        text-align: center !important;
    }}

    /* 按钮样式：樱花粉 */
    .stButton>button {{
        width: 100%;
        border-radius: 25px !important;
        background-color: #ff6b81 !important;
        color: white !important;
        border: none !important;
        height: 3em;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. 工具函数 ---
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

# --- 3. 数据初始化 ---
if 'weight_data_list' not in st.session_state:
    st.session_state.weight_data_list = [{"日期": "2025-12-28", "体重": 65.0, "心情": "😊"}]
if 'daily_logs' not in st.session_state:
    st.session_state.daily_logs = []

# --- 4. 侧边栏 ---
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

# --- 5. 主界面 ---
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
                st.session_state.daily_logs.append({
                    "日期": str(log_date), "运动": f"{'|'.join(sports)}({sport_time}min)",
                    "饮食": diet, "大便": is_poop, "饮水": water,
                    "工作": f"{'|'.join(work)}({work_time}h - {work_focus})", "详情": detail, "心情": mood
                })
                st.rerun()

        # 展示历史记录
        if st.session_state.daily_logs:
            st.subheader("📜 往日回忆")
            for log in reversed(st.session_state.daily_logs):
                with st.expander(f"📅 {log['日期']} - 心情: {log['心情']}"):
                    st.write(f"**🏃 运动：** {log['运动']} | **🥗 饮食：** {log['饮食']} | **💩 排便：** {log['大便']}")
                    st.write(f"**💻 进度：** {log['工作']} | **💧 饮水：** {log.get('饮水', 2.0)}L")
                    if log.get('详情') and log['详情'].strip():
                        st.markdown(f"""
                        <div style="background-color: #fff0f3; padding: 12px; border-radius: 12px; border-left: 4px solid #ff6b81; margin-top: 10px;">
                            <span style="color: #ff6b81; font-weight: bold;">💌 给小耗子的私语：</span><br>
                            <span style="color: #555; font-style: italic;">{log['详情']}</span>
                        </div>
                        """, unsafe_allow_html=True)

    with col_r:
        st.markdown("### 💌 小耗子的叮嘱")
        quotes = ["为了见你，我正在东京努力变优秀。", "所有的数学斜率，最终都会指向我们的重逢。", "不仅要瘦，还要健康，这是小耗子唯一的命令。"]
        st.write(f"*{np.random.choice(quotes)}*")

        if st.button("查看全维度深度审计报告", use_container_width=True):
            if api_key_input:
                with st.spinner("审计计算中..."):
                    try:
                        df_w = pd.DataFrame(st.session_state.weight_data_list)
                        pred_date, slope = get_prediction(df_w)
                        last = st.session_state.daily_logs[-1]
                        client = OpenAI(api_key=api_key_input, base_url="https://api.deepseek.com")
                        prompt = f"""你是‘小耗子’。当前体重{df_w['体重'].iloc[-1]}kg，斜率{slope:.3f}。排便{last['大便']}，饮水{last['饮水']}L。饮食{last['饮食']}，工作{last['工作']}，运动{last['运动']}。心情{last['心情']}。请给出现状分析、饮食处方、运动方案和暖心总结。"""
                        response = client.chat.completions.create(model="deepseek-chat", messages=[{"role": "system", "content": "你是一个理性的理科生伴侣。"},{"role": "user", "content": prompt}], temperature=0.3)
                        st.info(response.choices[0].message.content)
                    except: st.error("AI 审计暂时不可用")

with tab2:
    # 减脂数学模型保持不变
    df_weight = pd.DataFrame(st.session_state.weight_data_list)
    df_weight['日期'] = pd.to_datetime(df_weight['日期'])
    calc_df = df_weight.sort_values('日期').drop_duplicates('日期', keep='last')
    pred_res, slope = get_prediction(calc_df)

    st.markdown("### 📈 数据背后的爱与科学")
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("日均斜率 (kg/d)", f"{slope:.3f}")
    with c2: st.metric("距离 55kg 还差", f"{round(calc_df['体重'].iloc[-1] - 55.0, 1)} kg")
    with c3: st.metric("预估达标日", pred_res.strftime('%Y-%m-%d') if isinstance(pred_res, datetime.date) else "数据收集中")
    # ... 表单和绘图代码 ...
    with st.form("weight_v12"):
        cw1, cw2 = st.columns(2)
        nw = cw1.number_input("体重 (kg)", value=float(calc_df['体重'].iloc[-1]), step=0.1)
        nd = cw2.date_input("测量日期", datetime.date.today())
        if st.form_submit_button("更新数学模型"):
            st.session_state.weight_data_list.append({"日期": str(nd), "体重": nw})
            st.rerun()
    fig = px.line(calc_df, x="日期", y="体重", markers=True, color_discrete_sequence=['#ff6b81'])
    st.plotly_chart(fig, use_container_width=True)

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
    input_pass = st.text_input("输入 Access Code 解锁：", type="password")
    if input_pass == "wwhaxxy1314":
        st.balloons()
        st.markdown(f"""
        <div style="background-color: #fff0f3; padding: 30px; border-radius: 20px; border: 2px dashed #ff6b81;">
            <h3 style="color: #ff6b81; text-align: center;">📅 2026.01.01</h3>
            <p style="color: #555; line-height: 1.8;">亲爱的小夏：跨过2025，我见证了你的努力。这个基地是我们的证明。新的一年，愿你少点焦虑，多点顺畅。我们在终点见。<br><br>
            <span style="float: right;">—— [运维负责人: 小耗子 🐭]</span></p>
        </div>
        """, unsafe_allow_html=True)
