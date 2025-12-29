import streamlit as st
import pandas as pd
import plotly.express as px
from openai import OpenAI
import datetime
import numpy as np
import requests
import base64
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
def analyze_food_with_gemini(uploaded_file, g_key):
    """使用原生请求识别图片（不留痕）"""
    if not g_key: return "请在侧边栏填入 Gemini Key"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={g_key}"
    img_b64 = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
    payload = {
        "contents": [{"parts": [
            {"text": "识别图片食物，估算热量和纤维素（对排便很重要），给出温柔建议。"},
            {"inline_data": {"mime_type": "image/jpeg", "data": img_b64}}
        ]}]
    }
    try:
        response = requests.post(url, json=payload, timeout=15)
        res_json = response.json()
        return res_json["candidates"][0]["content"]["parts"][0]["text"]
    except: return "识别暂时不可用，请检查网络或Key。"

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
    st.divider()
    deepseek_key = st.text_input("🔑 DeepSeek Key (审计)", value=DEFAULT_API_KEY, type="password")
    gemini_key = st.text_input("🔑 Gemini Key (识食)", type="password")

load_all_data(current_user)

# --- 5. 主界面 ---
st.markdown("<div style='text-align:center; padding:10px; border-radius:15px; background: rgba(255,107,129,0.1); border: 1px dashed #ff6b81; margin-bottom: 20px;'><span style='color: #ff6b81; font-weight: bold;'>🔒 小夏 ❤️ 小耗子 的私人领地</span></div>", unsafe_allow_html=True)
st.markdown(f"<h1>💖 {current_user} 的专属分区</h1>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["🌸 时光机", "📉 减脂美学", "🎒 东京冒险", "💌 元旦信箱"])

with tab1:
    col_l, col_r = st.columns([1.8, 1.2])
    with col_l:
        # 小夏专属识食
        if current_user == "小夏":
            st.markdown("#### 🥦 小夏识食 (不保存图片)")
            food_img = st.file_uploader("上传饮食照", type=["jpg", "jpeg", "png"])
            if food_img:
                st.image(food_img, width=250)
                if st.button("AI 识别食材"):
                    with st.spinner("识别中..."):
                        st.session_state.temp_food = analyze_food_with_gemini(food_img, gemini_key)
            if "temp_food" in st.session_state:
                st.info(st.session_state.temp_food)

        with st.form("daily_form_fixed", clear_on_submit=True):
            st.subheader("📝 今日深度记录")
            log_date = st.date_input("日期", datetime.date.today())
            
            diet_detail = ""
            if current_user == "小夏":
                diet_detail = st.text_area("🍱 今日饮食明细")

            sports = st.multiselect("🏃 运动项目", ["呼啦圈", "散步", "羽毛球", "健身房", "拉伸"])
            sport_time = st.slider("⏱️ 运动时长 (分钟)", 0, 180, 30)
            diet_type = st.select_slider("🥗 饮食等级", options=["放纵🍕", "正常🍚", "清淡🥗", "严格🥦"], value="正常🍚")
            
            is_poop, water, part_time = "N/A", 0.0, 0.0
            if current_user == "小夏":
                st.write("---")
                ch1, ch2 = st.columns(2)
                is_poop = ch1.radio("💩 今日排便", ["未排便", "顺利排便 ✅"], horizontal=True)
                water = ch2.slider("💧 饮水量 (L)", 0.5, 4.0, 2.0, 0.5)
            else:
                part_time = st.number_input("⏳ 兼职时长 (小时)", 0.0, 14.0, 0.0)
            
            st.write("---")
            work = st.multiselect("💻 工作学术", ["看文献", "写论文", "投简历"])
            work_time = st.slider("⏳ 投入时长 (小时)", 0.0, 14.0, 4.0)
            work_focus = st.select_slider("🎯 专注状态", options=["走神😴", "断续☕", "专注📚", "心流🔥"], value="专注📚")
            detail = st.text_area("💌 碎碎念")
            mood = st.select_slider("✨ 心情", options=["😢", "😟", "😐", "😊", "🥰"], value="😊")

            if st.form_submit_button("同步"):
                final_detail = detail
                if current_user == "小夏" and "temp_food" in st.session_state:
                    final_detail = f"【AI建议】:{st.session_state.temp_food}\n{detail}"
                
                supabase.table("daily_logs").insert({
                    "user_name": current_user, "log_date": str(log_date), "sports": "|".join(sports),
                    "sport_minutes": float(sport_time), "diet": diet_type, "diet_detail": diet_detail,
                    "is_poop": is_poop, "water": water, "work": "|".join(work),
                    "academic_hours": float(work_time), "part_time_hours": float(part_time),
                    "detail": final_detail, "mood": mood, "focus_level": work_focus
                }).execute()
                if "temp_food" in st.session_state: del st.session_state.temp_food
                st.rerun()

    with col_r:
        st.markdown("### 🤖 十日综合审计")
        if st.button("生成复盘报告", use_container_width=True):
            if deepseek_key and st.session_state.daily_logs:
                with st.spinner("复盘中..."):
                    history = st.session_state.daily_logs[:10]
                    history_str = "\n".join([f"- {l['log_date']}: 饮食[{l.get('diet_detail')}] 排便[{l['is_poop']}] 心情[{l['mood']}]" for l in history])
                    _, slope = get_prediction(pd.DataFrame(st.session_state.weight_data_list))
                    
                    client = OpenAI(api_key=deepseek_key, base_url="https://api.deepseek.com")
                    prompt = f"你是小耗子。请分析小夏近10天数据：{history_str}。当前体重斜率{slope:.3f}。请结合饮食和排便给出建议。" if current_user == "小夏" else f"你是小夏。分析小耗子近10天勤奋度：{history_str}"
                    res = client.chat.completions.create(model="deepseek-chat", messages=[{"role": "user", "content": prompt}])
                    st.markdown(f'<div class="report-box">{res.choices[0].message.content}</div>', unsafe_allow_html=True)

# 后续展示、体重、东京模块保持不变...
