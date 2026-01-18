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
        # 这里的 user 逻辑：加载数据时我们通常需要看双方的记录
        # 但为了保持你原来的逻辑，我们加载当前 radio 选择的用户数据
        w_res = supabase.table("weight_data").select("*").eq("user_name", user).order("weight_date").execute()
        st.session_state.weight_data_list = [{"日期": r['weight_date'], "体重": r['weight'], "id": r['id']} for r in w_res.data]
        
        # 加载小夏的日志供小耗子评论，或者加载当前用户的日志
        target_user = "小夏" if current_user == "小耗子" else "小夏" 
        l_res = supabase.table("daily_logs").select("*").eq("user_name", "小夏").order("log_date", desc=True).execute()
        st.session_state.daily_logs = l_res.data
    except Exception as e: st.error(f"加载失败: {e}")

# --- 2. 工具函数 (天气/预测保持不变) ---
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
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #fff5f7 0%, #f0f4ff 100%); }
    h1, h2, h3 { color: #ff6b81 !important; text-align: center !important; }
    .diary-card { background-color: #fff0f3; padding: 12px; border-radius: 12px; border-left: 4px solid #ff6b81; margin-top: 10px; color: #333; }
    .comment-card { background-color: #f0f4ff; padding: 10px; border-radius: 10px; border-left: 4px solid #4a90e2; margin-top: 5px; font-size: 0.9em; color: #444; }
    .stButton>button { border-radius: 25px !important; }
    </style>
    """, unsafe_allow_html=True)

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
        # --- 小夏的输入表单 (仅小夏可见) ---
        if current_user == "小夏":
            st.subheader(f"📝 {current_user} 的深度记录")
            all_options = ["呼啦圈", "散步", "羽毛球", "健身房", "拉伸", "俯卧撑"]
            selected_sports = st.multiselect("🏃 运动项目", all_options)
            
            with st.form("daily_form", clear_on_submit=True):
                log_date = st.date_input("日期", datetime.date.today())
                diet_detail = st.text_area("🍱 今日饮食明细")
                # 运动逻辑拆分
                pushup_count = 0
                other_sport_time = 0
                has_other_sports = any(s in selected_sports for s in ["呼啦圈", "散步", "羽毛球", "健身房", "拉伸"])
                has_pushup = "俯卧撑" in selected_sports
                if has_other_sports: other_sport_time = st.slider("⏱️ 基础运动时长", 0, 180, 30, step=5)
                if has_pushup: pushup_count = st.number_input("💪 俯卧撑次数", 0, 1000, 30)
                
                detail = st.text_area("💌 碎碎念/备注", placeholder="今天有什么想对小耗子说的？")
                mood = st.select_slider("✨ 心情", options=["😢", "😟", "😐", "😊", "🥰"], value="😊")

                if st.form_submit_button("同步到云端"):
                    final_detail = f"【俯卧撑：{pushup_count}个】 " + detail if (has_pushup and has_other_sports) else detail
                    final_sport_val = float(pushup_count) if (has_pushup and not has_other_sports) else float(other_sport_time)
                    
                    supabase.table("daily_logs").insert({
                        "user_name": "小夏", "log_date": str(log_date), 
                        "sports": "|".join(selected_sports), "sport_minutes": final_sport_val,
                        "diet_detail": diet_detail, "detail": final_detail, "mood": mood
                    }).execute()
                    st.rerun()
        else:
            st.info("💡 小耗子模式：请在下方查看小夏的记录并进行评论。")

        st.divider()
        st.subheader("📜 历史存证与互动")
        
        if st.session_state.daily_logs:
            for log in st.session_state.daily_logs[:10]:
                with st.expander(f"📅 {log['log_date']} - 心情: {log['mood']}"):
                    c_info, c_action = st.columns([3, 1])
                    
                    with c_info:
                        st.write(f"🏃 **运动:** {log['sports']} ({log['sport_minutes']})")
                        st.markdown(f'<div class="diary-card">🌸 小夏的碎碎念：<br>{log["detail"]}</div>', unsafe_allow_html=True)
                        
                        # 显示小耗子的回复 (如果存在)
                        # 注意：这里假设数据库中有字段 'comment_from_haozhi'
                        haozhi_reply = log.get('comment_from_haozhi')
                        if haozhi_reply:
                            st.markdown(f'<div class="comment-card">🐭 小耗子的评论：<br>{haozhi_reply}</div>', unsafe_allow_html=True)
                    
                    with c_action:
                        # 小耗子的专属按键
                        if current_user == "小耗子":
                            new_reply = st.text_area("回复碎碎念", key=f"re_{log['id']}", placeholder="写下你的鼓励...")
                            if st.button("💬 提交评论", key=f"btn_{log['id']}"):
                                if new_reply:
                                    supabase.table("daily_logs").update({"comment_from_haozhi": new_reply}).eq("id", log['id']).execute()
                                    st.success("评论已同步！")
                                    st.rerun()
                        
                        # 只有小夏可以删除自己的
                        if current_user == "小夏":
                            if st.button("🗑️ 删除", key=f"del_{log['id']}"):
                                supabase.table("daily_logs").delete().eq("id", log['id']).execute()
                                st.rerun()

    with col_r:
        # 机器人复盘保持不变...
        st.markdown("### 🤖 智能审计")
        # (此处代码同前，省略以保持简洁)
        pass

# --- 后面 Tab 2/3/4 保持不变 ---
