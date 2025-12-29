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

# --- 2. 工具函数 ---
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

# --- 3. UI 样式 ---
st.set_page_config(page_title="2026东京之约", layout="wide", page_icon="🗼")
st.markdown("""<style>
    .stApp { background: linear-gradient(135deg, #fff5f7 0%, #f0f4ff 100%); }
    h1, h2, h3 { color: #ff6b81 !important; text-align: center !important; }
    .stButton>button { border-radius: 25px !important; background-color: #ff6b81 !important; color: white !important; }
    .diary-card { background-color: #fff0f3; padding: 12px; border-radius: 12px; border-left: 4px solid #ff6b81; margin-top: 10px; }
    .report-box { background-color: #f0f4ff; padding: 20px; border-radius: 15px; border-left: 8px solid #6a89cc; margin-top: 20px; }
    </style>""", unsafe_allow_html=True)

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
st.markdown("<div style='text-align:center; padding:10px; border-radius:15px; background: rgba(255,107,129,0.1); border: 1px dashed #ff6b81; margin-bottom: 20px;'><span style='color: #ff6b81; font-weight: bold;'>🔒 小夏 ❤️ 小耗子 的私人领地</span></div>", unsafe_allow_html=True)
st.markdown(f"<h1>💖 {current_user} 的专属分区</h1>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["🌸 时光机", "📉 减脂美学", "🎒 东京冒险", "💌 元旦信箱"])

with tab1:
    col_l, col_r = st.columns([1.8, 1.2])
    with col_l:
        with st.form("daily_form_v_master", clear_on_submit=True):
            st.subheader(f"📝 {current_user} 的深度记录")
            log_date = st.date_input("日期", datetime.date.today())
            
            diet_detail = ""
            if current_user == "小夏":
                diet_detail = st.text_area("🍱 今日饮食明细", placeholder="具体吃了什么？(如：早起黑咖啡，中午瘦肉黄豆面，晚上一根黄瓜)")

            sports = st.multiselect("🏃 运动项目", ["呼啦圈", "散步", "羽毛球", "健身房", "拉伸"])
            sport_time = st.slider("⏱️ 运动时长 (分钟)", 0, 180, 30, step=5)
            diet_type = st.select_slider("🥗 饮食控制等级", options=["放纵🍕", "正常🍚", "清淡🥗", "严格🥦"], value="正常🍚")
            
            is_poop, water, part_time = "N/A", 0.0, 0.0
            if current_user == "小夏":
                st.write("---")
                ch1, ch2 = st.columns(2)
                is_poop = ch1.radio("💩 今日排便情况", ["未排便", "顺利排便 ✅"], horizontal=True)
                water = ch2.slider("💧 饮水量 (L)", 0.5, 4.0, 2.0, 0.5)
            else:
                st.write("---")
                part_time = st.number_input("⏳ 今日兼职时长 (小时)", 0.0, 14.0, 0.0, step=0.5)
            
            st.write("---")
            work = st.multiselect("💻 学术与工作内容", ["看文献", "写论文", "找工作", "其他"])
            work_time = st.slider("⏳ 专注时长 (小时)", 0.0, 14.0, 4.0, step=0.5)
            work_focus = st.select_slider("🎯 专注状态", options=["走神😴", "断续☕", "专注📚", "心流🔥"], value="专注📚")
            detail = st.text_area("💌 碎碎念/备注")
            mood = st.select_slider("✨ 心情", options=["😢", "😟", "😐", "😊", "🥰"], value="😊")

            if st.form_submit_button("同步到云端"):
                supabase.table("daily_logs").insert({
                    "user_name": current_user, "log_date": str(log_date), "sports": "|".join(sports),
                    "sport_minutes": float(sport_time), "diet": diet_type, "diet_detail": diet_detail,
                    "is_poop": is_poop, "water": water, "work": "|".join(work),
                    "academic_hours": float(work_time), "part_time_hours": float(part_time),
                    "detail": detail, "mood": mood, "focus_level": work_focus
                }).execute()
                st.rerun()

    with col_r:
        st.markdown("### 🤖 十日综合审计专家")
        if st.button("生成深度分析报告", use_container_width=True):
            if api_key_input and st.session_state.daily_logs:
                with st.spinner("正在复盘近十天数据..."):
                    # 提取近10天数据
                    history_logs = st.session_state.daily_logs[:10]
                    weight_df = pd.DataFrame(st.session_state.weight_data_list)
                    _, slope = get_prediction(weight_df)
                    
                    history_str = "\n".join([
                        f"- {l['log_date']}: 饮食[{l.get('diet_detail')}] 运动[{l['sports']} {l.get('sport_minutes')}min] 排便[{l['is_poop']}] 饮水[{l['water']}L] 专注[{l.get('focus_level')}] 心情[{l['mood']}]"
                        for l in history_logs
                    ])
                    
                    client = OpenAI(api_key=api_key_input, base_url="https://api.deepseek.com")
                    
                    if current_user == "小夏":
                        prompt = f"""
                        你是理科伴侣小耗子。请根据小夏近10天的数据进行深度综合分析：
                        历史数据：{history_str}
                        当前体重斜率：{slope:.3f}
                        
                        要求：
                        1. 综合分析饮食明细与【排便情况】的相关性。
                        2. 分析饮水量、运动时长对【体重斜率】的影响。
                        3. 观察【专注情况】与【心情】的波动规律。
                        4. 给出未来一周的综合建议（包括饮食调整、水分摄入建议）。
                        语气要严谨、理性、有数据支撑，但透着对小夏的关心。
                        """
                    else:
                        prompt = f"你是小夏。请分析小耗子近10天的兼职与学术时长数据：{history_str}。评价他的勤奋程度并嘱咐他平衡心情与休息。"
                    
                    response = client.chat.completions.create(model="deepseek-chat", messages=[{"role": "user", "content": prompt}])
                    st.markdown(f'<div class="report-box">{response.choices[0].message.content}</div>', unsafe_allow_html=True)

        st.divider()
        st.subheader("📜 历史存证")
        for log in st.session_state.daily_logs[:5]: # 仅显示最近5条防止过长
            with st.expander(f"📅 {log['log_date']} - {log['mood']}"):
                if current_user == "小夏":
                    st.write(f"🍱 **饮食:** {log.get('diet_detail', '未记录')}")
                    st.write(f"💩 **排便:** {log['is_poop']} | 💧 **饮水:** {log['water']}L")
                st.write(f"🏃 **运动:** {log['sports']} ({log.get('sport_minutes')}min)")
                st.write(f"📚 **学术:** {log.get('academic_hours')}h ({log.get('focus_level')})")

with tab2:
    if current_user == "小夏":
        df_w = pd.DataFrame(st.session_state.weight_data_list)
        if not df_w.empty:
            df_w['日期'] = pd.to_datetime(df_w['日期'])
            calc_df = df_w.sort_values('日期').drop_duplicates('日期', keep='last')
            pred_res, slope = get_prediction(calc_df)
            c1, c2, c3 = st.columns(3)
            c1.metric("体重斜率", f"{slope:.3f}"); c2.metric("距离目标", f"{round(calc_df['体重'].iloc[-1] - 55.0, 1)} kg"); c3.metric("达标预估", pred_res.strftime('%Y-%m-%d') if pred_res else "计算中")
            st.plotly_chart(px.line(calc_df, x="日期", y="体重", markers=True, color_discrete_sequence=['#ff6b81']), use_container_width=True)
        with st.form("w_form"):
            val = st.number_input("录入体重 (kg)", 60.0, step=0.1); dt = st.date_input("测量日期", datetime.date.today())
            if st.form_submit_button("更新"):
                supabase.table("weight_data").insert({"user_name": "小夏", "weight_date": str(dt), "weight": val}).execute()
                st.rerun()
    else: st.info("💡 小耗子分区，请在 Tab1 专注学术时长记录。")

# Tab 3 & 4 保持原有内容...
