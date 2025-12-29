import streamlit as st
import pandas as pd
import plotly.express as px
from openai import OpenAI
import datetime
import numpy as np
import requests
from supabase import create_client, Client

# --- 0. 核心配置 ---
DEFAULT_API_KEY = "sk-051a17fa2f404ba2a9459d5f356de93b"
LOVE_START_DATE = datetime.date(2025, 1, 1)
SUPABASE_URL = "https://tqtejtfkqxkfrnelqczn.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRxdGVqdGZrcXhrZnJuZWxxY3puIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY5NTgxMjksImV4cCI6MjA4MjUzNDEyOX0.9gBVQZhFBFg9a9hm0d6BUW-s8yhCGPIjwmbLLZ9F0Ow"

@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# --- 1. 数据库函数 ---
def load_all_data(user):
    try:
        w_res = supabase.table("weight_data").select("*").eq("user_name", user).order("weight_date").execute()
        st.session_state.weight_data_list = [{"日期": r['weight_date'], "体重": r['weight'], "id": r['id']} for r in w_res.data]
        l_res = supabase.table("daily_logs").select("*").eq("user_name", user).order("log_date", desc=True).execute()
        st.session_state.daily_logs = l_res.data
    except Exception as e: st.error(f"加载失败: {e}")

def delete_record(table_name, record_id):
    supabase.table(table_name).delete().eq("id", record_id).execute()
    st.success("记录已抹除 ✨")
    st.rerun()

# --- 2. UI 样式 ---
st.set_page_config(page_title="2026东京之约", layout="wide", page_icon="🗼")
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #fff5f7 0%, #f0f4ff 100%); }
    [data-testid="stMetric"] { background-color: rgba(255, 255, 255, 0.7) !important; border-radius: 20px !important; text-align: center !important; }
    h1, h2, h3 { color: #ff6b81 !important; text-align: center !important; }
    .stButton>button { border-radius: 25px !important; background-color: #ff6b81 !important; color: white !important; }
    .diary-card { background-color: #fff0f3; padding: 12px; border-radius: 12px; border-left: 4px solid #ff6b81; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 工具函数 ---
def get_weather(city_pinyin):
    api_key = "3f4ff1ded1a1a5fc5335073e8cf6f722"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_pinyin}&appid={api_key}&units=metric&lang=zh_cn"
    try:
        res = requests.get(url, timeout=3).json()
        return {"temp": res['main']['temp'], "icon": res['weather'][0]['icon']}
    except: return None

def get_prediction(df):
    if len(df) < 2: return None, 0
    try:
        temp_df = df.copy()
        temp_df['日期_ts'] = pd.to_datetime(temp_df['日期']).map(datetime.date.toordinal)
        x, y = temp_df['日期_ts'].values, temp_df['体重'].values.astype(float)
        slope, intercept = np.polyfit(x, y, 1)
        target_date = datetime.date.fromordinal(int((55.0 - intercept) / slope)) if slope < 0 else None
        return target_date, slope
    except: return None, 0

# --- 4. 侧边栏 ---
with st.sidebar:
    st.markdown("### 👤 身份切换")
    current_user = st.radio("当前登录：", ["小夏", "小耗子"], horizontal=True)
    st.divider()
    days_left = (datetime.date(2026, 6, 23) - datetime.date.today()).days
    st.metric("距离重逢", f"{days_left} 天")
    st.progress(max(0, min(100, 100 - int(days_left / 540 * 100))))
    st.divider()
    w_tokyo, w_shantou = get_weather("Tokyo"), get_weather("Shantou")
    c1, c2 = st.columns(2)
    if w_tokyo: c1.markdown(f"<div style='text-align:center;'><img src='http://openweathermap.org/img/wn/{w_tokyo['icon']}.png' width='40'><br>东京 {w_tokyo['temp']}°C</div>", unsafe_allow_html=True)
    if w_shantou: c2.markdown(f"<div style='text-align:center;'><img src='http://openweathermap.org/img/wn/{w_shantou['icon']}.png' width='40'><br>汕头 {w_shantou['temp']}°C</div>", unsafe_allow_html=True)
    api_key_input = st.text_input("🔑 API 秘钥", value=DEFAULT_API_KEY, type="password")

load_all_data(current_user)

# --- 5. 主界面 ---
st.markdown("""
    <div style='text-align:center; padding:10px; border-radius:15px; background: rgba(255,107,129,0.1); border: 1px dashed #ff6b81; margin-bottom: 20px;'>
        <span style='color: #ff6b81; font-weight: bold;'>🔒 小夏 ❤️ 小耗子 的私人领地 (Private Space)</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown(f"<h1>💖 {current_user} 的专属分区</h1>", unsafe_allow_html=True)
days_together = (datetime.date.today() - LOVE_START_DATE).days
st.markdown(f"<p style='text-align:center;'>这是我们守护彼此的第 {days_together} 天 🎉</p>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["🌸 时光机", "📉 减脂美学", "🎒 东京冒险", "💌 元旦信箱"])

with tab1:
    col_l, col_r = st.columns([2, 1])
    with col_l:
        with st.form("daily_form_v_final_sql", clear_on_submit=True):
            st.subheader(f"📝 {current_user} 的记录")
            log_date = st.date_input("日期", datetime.date.today())
            
            # --- 饮食明细录入（仅小夏显示） ---
            diet_detail = ""
            if current_user == "小夏":
                diet_detail = st.text_area("🍱 今日饮食明细", placeholder="例如：早餐全麦面包，午餐鸡胸肉+黄豆面，晚餐半个红薯")

            sports = st.multiselect("🏃 运动健身", ["呼啦圈", "散步", "羽毛球", "健身房", "拉伸"])
            sport_time = st.slider("⏱️ 运动时长 (分钟)", 0, 180, 30, step=5)
            diet = st.select_slider("🥗 饮食总体控制", options=["放纵🍕", "正常🍚", "清淡🥗", "严格🥦"], value="正常🍚")
            
            is_poop, water, part_time = "N/A", 0.0, 0.0
            if current_user == "小夏":
                st.write("---")
                ch1, ch2 = st.columns(2)
                is_poop = ch1.radio("💩 今日是否大便？", ["未排便", "顺利排便 ✅"], horizontal=True)
                water = ch2.slider("💧 饮水量 (L)", 0.5, 4.0, 2.0, 0.5)
            else:
                st.write("---")
                part_time = st.number_input("⏳ 今日兼职时长 (小时)", 0.0, 14.0, 0.0, step=0.5)
            
            st.write("---")
            work = st.multiselect("💻 工作与学术", ["看文献", "写大论文", "写小论文", "阅读就业信息"])
            work_time = st.slider("⏳ 累计时长 (小时)", 0.0, 14.0, 4.0, step=0.5)
            work_focus = st.select_slider("🎯 专注情况", options=["走神😴", "断续☕", "专注📚", "心流🔥"], value="专注📚")
            detail = st.text_area("💌 碎碎念/备注")
            mood = st.select_slider("✨ 心情", options=["😢", "😟", "😐", "😊", "🥰"], value="😊")

            if st.form_submit_button("同步"):
                supabase.table("daily_logs").insert({
                    "user_name": current_user, 
                    "log_date": str(log_date), 
                    "sports": "|".join(sports),
                    "sport_minutes": float(sport_time),
                    "diet": diet, 
                    "diet_detail": diet_detail, # 存入详细描述
                    "is_poop": is_poop, 
                    "water": water,
                    "work": "|".join(work),
                    "academic_hours": float(work_time),
                    "part_time_hours": float(part_time),
                    "detail": detail, 
                    "mood": mood
                }).execute()
                st.rerun()

        if st.session_state.daily_logs:
            for log in st.session_state.daily_logs:
                with st.expander(f"📅 {log['log_date']} - 心情: {log['mood']}"):
                    if current_user == "小夏":
                        st.write(f"**排便:** {log['is_poop']} | **饮水:** {log['water']}L")
                        if log.get('diet_detail'): st.write(f"**🍱 饮食:** {log['diet_detail']}")
                    st.write(f"**🏃 运动:** {log['sports']} ({log.get('sport_minutes', 0)} min)")
                    st.write(f"**💻 学术:** {log['work']} ({log.get('academic_hours', 0)} h)")
                    if log['detail']: st.markdown(f'<div class="diary-card">💌 {log["detail"]}</div>', unsafe_allow_html=True)
                    if st.button("🗑️ 删除", key=f"del_{log['id']}"): delete_record("daily_logs", log['id'])

    with col_r:
        st.markdown("### 🤖 AI 审计")
        if st.button("生成审计报告", use_container_width=True):
            if api_key_input and st.session_state.daily_logs:
                with st.spinner("审计中..."):
                    last = st.session_state.daily_logs[0]
                    client = OpenAI(api_key=api_key_input, base_url="https://api.deepseek.com")
                    if current_user == "小夏":
                        # AI 会分析饮食明细
                        prompt = f"""
                        你是理科伴侣小耗子。小夏今天身体反馈如下：
                        - 饮食内容：{last.get('diet_detail', '未描述')}
                        - 饮食评价：{last['diet']}
                        - 排便情况：{last['is_poop']}
                        - 饮水量：{last['water']}L
                        - 运动：{last['sport_minutes']}分钟
                        
                        请结合饮食成分（比如纤维摄入是否利于肠道）和排便数据，给出理性的代谢分析与建议。
                        """
                    else:
                        prompt = f"你是伴侣小夏。小耗子今天兼职{last['part_time_hours']}小时，学术{last['academic_hours']}小时。请评价他的勤奋并给予鼓励。"
                    
                    response = client.chat.completions.create(model="deepseek-chat", messages=[{"role": "user", "content": prompt}])
                    st.info(response.choices[0].message.content)

with tab2:
    if current_user == "小夏":
        df_w = pd.DataFrame(st.session_state.weight_data_list)
        if not df_w.empty:
            df_w['日期'] = pd.to_datetime(df_w['日期'])
            calc_df = df_w.sort_values('日期').drop_duplicates('日期', keep='last')
            pred_res, slope = get_prediction(calc_df)
            c1, c2, c3 = st.columns(3)
            c1.metric("体重斜率", f"{slope:.3f}")
            c2.metric("距离目标", f"{round(calc_df['体重'].iloc[-1] - 55.0, 1)} kg")
            c3.metric("预测达标", pred_res.strftime('%Y-%m-%d') if pred_res else "测算中")
            st.plotly_chart(px.line(calc_df, x="日期", y="体重", markers=True, color_discrete_sequence=['#ff6b81']), use_container_width=True)
        with st.form("w_form"):
            val = st.number_input("体重 (kg)", 60.0, step=0.1); dt = st.date_input("日期", datetime.date.today())
            if st.form_submit_button("更新体重"):
                supabase.table("weight_data").insert({"user_name": "小夏", "weight_date": str(dt), "weight": val}).execute()
                st.rerun()
    else: st.info("💡 小耗子分区无需记录体重。")

with tab3: st.image("https://img.picgo.net/2024/05/22/fireworks_kimono_anime18090543e86c0757.md.png", use_container_width=True)
with tab4:
    if st.text_input("授权码", type="password") == "wwhaxxy1314":
        st.balloons()
        st.markdown('<div class="diary-card">2026, 重逢在即。加油！</div>', unsafe_allow_html=True)
