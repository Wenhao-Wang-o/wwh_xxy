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
    .stApp {{ background: linear-gradient(135deg, #fff5f7 0%, #f0f4ff 100%); }}
    [data-testid="stMetric"] {{
        background-color: rgba(255, 255, 255, 0.7) !important;
        border-radius: 20px !important;
        padding: 20px !important;
        text-align: center !important;
    }}
    [data-testid="stMetricValue"] > div {{ display: flex !important; justify-content: center !important; color: #ff6b81 !important; }}
    [data-testid="stMetricLabel"] > div {{ display: flex !important; justify-content: center !important; color: #6a89cc !important; }}
    h1, h2, h3 {{ color: #ff6b81 !important; text-align: center !important; }}
    .stButton>button {{ width: 100%; border-radius: 25px !important; background-color: #ff6b81 !important; color: white !important; border: none !important; height: 3em; }}
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
    st.markdown("<h2 style='text-align: center;'>🗼 状态监控</h2>", unsafe_allow_html=True)
    days_left = (datetime.date(2026, 6, 23) - datetime.date.today()).days
    st.metric("距离重逢还有", f"{days_left} 天")
    st.progress(max(0, min(100, 100 - int(days_left / 540 * 100))))
    st.divider()
    st.markdown("<p style='text-align: center; font-weight: bold;'>🌍 时空同步</p>", unsafe_allow_html=True)
    w_tokyo, w_shantou = get_weather("Tokyo"), get_weather("Shantou")
    c1, c2 = st.columns(2)
    if w_tokyo: c1.markdown(f"<div style='text-align:center;'><img src='http://openweathermap.org/img/wn/{w_tokyo['icon']}.png' width='40'><br>东京<br>{w_tokyo['temp']}°C</div>", unsafe_allow_html=True)
    if w_shantou: c2.markdown(f"<div style='text-align:center;'><img src='http://openweathermap.org/img/wn/{w_shantou['icon']}.png' width='40'><br>汕头<br>{w_shantou['temp']}°C</div>", unsafe_allow_html=True)
    st.divider()
    api_key_input = st.text_input("🔑 秘钥授权", value=DEFAULT_API_KEY, type="password")

# --- 5. 主界面 ---
st.markdown("<h1 style='text-align: center;'>💖 小耗子和小夏的秘密基地</h1>", unsafe_allow_html=True)

# 恋爱天数统计
days_together = (datetime.date.today() - LOVE_START_DATE).days
st.markdown(f"### 我们已经并肩作战了 {days_together} 天 🚀")
st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs(["🌸 生活时光机", "📉 数学减脂美学", "🎒 东京大冒险", "💌 元旦秘密信箱"])

with tab1:
    # 调整布局为两列：左侧日记记录 | 右侧AI审计
    col_log, col_ai = st.columns([2, 1])
    
    with col_log:
        with st.form("daily_form_v11", clear_on_submit=True):
            st.subheader("📝 记录今日数据点")
            log_date = st.date_input("日期", datetime.date.today())
            sports = st.multiselect("🏃 运动健身", ["呼啦圈", "散步", "打羽毛球"])
            sport_time = st.slider("⏱️ 运动时长 (分钟)", 0, 120, 30)
            diet = st.select_slider("🥗 饮食控制", options=["放纵餐🍕", "正常饮食🍚", "清淡少油🥗", "严格减脂🥦"], value="正常饮食🍚")
            st.write("---")
            ch1, ch2 = st.columns(2)
            is_poop = ch1.radio("💩 今日是否大便？", ["未排便", "顺利排便 ✅"], horizontal=True)
            water = ch2.slider("💧 饮水量 (L)", 0.5, 4.0, 2.0, 0.5)
            st.write("---")
            work = st.multiselect("💻 工作与学术", ["看文献", "写大论文", "写小论文", "阅读就业信息"])
            work_focus = st.select_slider("🎯 专注情况", options=["走神😴", "断续☕", "专注📚", "心流🔥"], value="专注📚")
            work_time = st.slider("⏳ 累计时长 (小时)", 0.0, 14.0, 4.0, step=0.5)
            detail = st.text_area("💌 碎碎念...", placeholder="在此录入需要小耗子知晓的信息...")
            mood = st.select_slider("✨ 心情", options=["😢", "😟", "😐", "😊", "🥰"], value="😊")
            if st.form_submit_button("同步数据至时光机"):
                st.session_state.daily_logs.append({
                    "日期": str(log_date), "运动": f"{'|'.join(sports)}({sport_time}min)",
                    "饮食": diet, "大便": is_poop, "饮水": water,
                    "工作": f"{'|'.join(work)}({work_time}h - {work_focus})", "详情": detail, "心情": mood
                })
                st.rerun()

        if st.session_state.daily_logs:
            st.subheader("📜 历史存证")
            for log in reversed(st.session_state.daily_logs):
                with st.expander(f"📅 {log['日期']} - {log['心情']}"):
                    st.write(f"**运动/饮食:** {log['运动']} | {log['饮食']}")
                    st.write(f"**肠道/饮水:** {log['大便']} | {log['饮水']}L")
                    if log['详情']: 
                        st.markdown(f"<div style='background-color:#fff0f3;padding:12px;border-radius:12px;border-left:4px solid #ff6b81;'>{log['详情']}</div>", unsafe_allow_html=True)

    with col_ai:
        st.markdown("### 🤖 小耗子审计报告")
        if st.button("运行全要素深度审计", use_container_width=True):
            if not st.session_state.daily_logs: st.warning("缺乏初始数据，请先同步记录。")
            else:
                try:
                    df_w = pd.DataFrame(st.session_state.weight_data_list)
                    pred_date, slope = get_prediction(df_w)
                    last = st.session_state.daily_logs[-1]
                    client = OpenAI(api_key=api_key_input, base_url="https://api.deepseek.com")
                    prompt = f"你是小耗子。当前体重{df_w['体重'].iloc[-1]}kg，减脂斜率{slope:.3f}。今日排便{last['大便']}，饮水{last['饮水']}L。工作{last['工作']}，运动{last['运动']}。请以理科生思维给出200字内严谨、不肉麻的新年审计方案。"
                    response = client.chat.completions.create(model="deepseek-chat", messages=[{"role": "system", "content": "你是一个理性的理科生伴侣，语气冷静、严谨。"},{"role": "user", "content": prompt}])
                    st.info(response.choices[0].message.content)
                except: st.error("核心审计模块响应超时。")

with tab2:
    # --- 减脂数学模型保持不变 ---
    df_weight = pd.DataFrame(st.session_state.weight_data_list)
    df_weight['日期'] = pd.to_datetime(df_weight['日期'])
    calc_df = df_weight.sort_values('日期').drop_duplicates('日期', keep='last')
    pred_res, slope = get_prediction(calc_df)
    st.markdown("### 📈 减脂动力学分析")
    c1, c2, c3 = st.columns(3)
    c1.metric("日均斜率", f"{slope:.3f}")
    c2.metric("待处理质量", f"{round(calc_df['体重'].iloc[-1] - 55.0, 1)} kg")
    c3.metric("预测达标日", pred_res.strftime('%Y-%m-%d') if isinstance(pred_res, datetime.date) else "测算中")
    with st.form("weight_v11"):
        cw1, cw2 = st.columns(2)
        nw, nd = cw1.number_input("录入体重 (kg)", value=float(calc_df['体重'].iloc[-1]), step=0.1), cw2.date_input("测量时间", datetime.date.today())
        if st.form_submit_button("更新数学模型"):
            st.session_state.weight_data_list.append({"日期": str(nd), "体重": nw})
            st.rerun()
    st.plotly_chart(px.line(calc_df, x="日期", y="体重", markers=True, color_discrete_sequence=['#ff6b81']), use_container_width=True)

with tab3:
    st.markdown("## 🎆 东京冒险清单：夏日花火之约")
    ca1, ca2 = st.columns([1, 1])
    with ca1:
        st.markdown("### 🎯 战略目标")
        st.checkbox("✨ 参加东京夏夜花火大会", value=False)
        st.write("备注：已锁定最佳观测坐标。")
    with ca2: st.image("https://img.picgo.net/2024/05/22/fireworks_kimono_anime18090543e86c0757.md.png", use_container_width=True)

with tab4:
    st.markdown("## 📟 2026 跨年系统指令")
    input_pass = st.text_input("授权码验证：", type="password")
    if input_pass == "wwhaxxy1314":
        st.snow()
        st.markdown(f"""
        <div style="background-color: #f8f9fa; padding: 25px; border-radius: 15px; border: 1px solid #dee2e6; font-family: monospace;">
            <h3>> ACCESS_GRANTED: 2026.01.01</h3><hr>
            <p>TO: 小夏 | 2025年度任务成功归档。<br><br>
            2026重逢概率推演：99.99%。<br>
            指令：严控斜率，保证水分摄入，系统 Bug 及时联络运维。<br>
            我们在终点汇合。<br><br>
            —— [运维负责人: 小耗子 🐭]</p>
        </div>
        """, unsafe_allow_html=True)
