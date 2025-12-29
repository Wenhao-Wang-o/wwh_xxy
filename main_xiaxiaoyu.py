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
    """
    修正后的预测逻辑：
    y = ax + b
    55 = a * target_date_ordinal + b
    target_date_ordinal = (55 - b) / a
    """
    if len(df) < 3: return None, 0 # 至少需要3个点进行线性回归
    try:
        temp_df = df.copy()
        temp_df['日期_ts'] = pd.to_datetime(temp_df['日期']).map(datetime.date.toordinal)
        x, y = temp_df['日期_ts'].values, temp_df['体重'].values.astype(float)
        
        # 线性拟合
        slope, intercept = np.polyfit(x, y, 1)
        
        # 只有在体重下降的情况下计算日期
        if slope < 0:
            target_ordinal = (55.0 - intercept) / slope
            # 防止日期过远导致溢出
            target_ordinal = min(target_ordinal, datetime.date(2027, 1, 1).toordinal())
            return datetime.date.fromordinal(int(target_ordinal)), slope
        else:
            return "趋势平缓", slope
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
            diet_detail = st.text_area("🍱 今日饮食明细", placeholder="具体吃了什么？") if current_user == "小夏" else ""
            sports = st.multiselect("🏃 运动项目", ["呼啦圈", "散步", "羽毛球", "健身房", "拉伸"])
            sport_time = st.slider("⏱️ 运动时长 (分钟)", 0, 180, 30, step=5)
            diet_type = st.select_slider("🥗 饮食控制等级", options=["放纵🍕", "正常🍚", "清淡🥗", "严格🥦"], value="正常🍚")
            
            is_poop, water, part_time = "N/A", 0.0, 0.0
            if current_user == "小夏":
                ch1, ch2 = st.columns(2)
                is_poop = ch1.radio("💩 今日排便情况", ["未排便", "顺利排便 ✅"], horizontal=True)
                water = ch2.slider("💧 饮水量 (L)", 0.5, 4.0, 2.0, 0.5)
            else:
                part_time = st.number_input("⏳ 今日兼职时长 (小时)", 0.0, 14.0, 0.0, step=0.5)
            
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
                    history_logs = st.session_state.daily_logs[:10]
                    weight_df = pd.DataFrame(st.session_state.weight_data_list)
                    _, slope = get_prediction(weight_df)
                    history_str = "\n".join([f"- {l['log_date']}: 饮食[{l.get('diet_detail')}] 运动[{l['sports']}] 心情[{l['mood']}]" for l in history_logs])
                    client = OpenAI(api_key=api_key_input, base_url="https://api.deepseek.com")
                    prompt = f"你是理科伴侣小耗子。分析小夏近10天数据：{history_str}。体重斜率{slope:.3f}。请分析代谢并给予关心建议。" if current_user == "小夏" else f"分析小耗子近10天勤奋度：{history_str}"
                    response = client.chat.completions.create(model="deepseek-chat", messages=[{"role": "user", "content": prompt}])
                    st.markdown(f'<div class="report-box">{response.choices[0].message.content}</div>', unsafe_allow_html=True)

with tab2:
    if current_user == "小夏":
        st.markdown("### 📉 减脂美学：目标 55.0 kg")
        df_w = pd.DataFrame(st.session_state.weight_data_list)
        if not df_w.empty:
            df_w['日期'] = pd.to_datetime(df_w['日期'])
            calc_df = df_w.sort_values('日期').drop_duplicates('日期', keep='last')
            pred_date, slope = get_prediction(calc_df)
            
            c1, c2, c3 = st.columns(3)
            current_w = calc_df['体重'].iloc[-1]
            diff = round(current_w - 55.0, 1)
            c1.metric("当前体重", f"{current_w} kg")
            c2.metric("距离目标", f"{diff} kg", delta=f"{slope:.3f} kg/d", delta_color="inverse")
            c3.metric("预估达标日", str(pred_date) if pred_date else "计算中...")

            st.plotly_chart(px.line(calc_df, x="日期", y="体重", title="体重变化趋势", markers=True, color_discrete_sequence=['#ff6b81']), use_container_width=True)
        
        with st.form("w_form_new"):
            st.markdown("#### ⚖️ 记录今日数据")
            col_a, col_b = st.columns(2)
            val = col_a.number_input("体重 (kg)", value=60.0, step=0.1)
            dt = col_b.date_input("测量日期", datetime.date.today())
            if st.form_submit_button("存入云端"):
                supabase.table("weight_data").insert({"user_name": "小夏", "weight_date": str(dt), "weight": val}).execute()
                st.rerun()

with tab3:
    st.markdown("## 🎆 东京冒险清单：夏日花火之约")
    # 更换为稳定的图片链接 (Unsplash 随机动漫风格东京图)
    st.image("https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?auto=format&fit=crop&w=1200&q=80", 
             caption="2026, 重逢在东京的街头", use_container_width=True)
    st.markdown("""
    - [ ] ✨ 在夏夜的东京参加一场盛大的花火大会！
    - [ ] ✨ 穿着浴衣走在浅草寺的灯火下
    - [ ] ✨ 找一家藏在巷子里最好吃的鳗鱼饭
    """)

with tab4:
    if st.text_input("授权码", type="password") == "wwhaxxy1314":
        st.balloons()
        st.markdown('<div class="diary-card">2026, 我们东京见。</div>', unsafe_allow_html=True)
