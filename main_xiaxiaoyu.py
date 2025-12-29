import streamlit as st
import pandas as pd
import plotly.express as px
from openai import OpenAI
import datetime
import numpy as np
import requests
from supabase import create_client, Client

# --- 0. 核心配置与 Supabase 连接 ---
DEFAULT_API_KEY = "sk-051a17fa2f404ba2a9459d5f356de93b"
LOVE_START_DATE = datetime.date(2025, 1, 1)

SUPABASE_URL = "https://tqtejtfkqxkfrnelqczn.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRxdGVqdGZrcXhrZnJuZWxxY3puIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY5NTgxMjksImV4cCI6MjA4MjUzNDEyOX0.9gBVQZhFBFg9a9hm0d6BUW-s8yhCGPIjwmbLLZ9F0Ow"

@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# --- 1. 增强型数据库函数 ---
def load_all_data(user):
    """根据当前用户加载历史记录"""
    try:
        # 加载体重
        w_res = supabase.table("weight_data").select("*").eq("user_name", user).order("weight_date").execute()
        st.session_state.weight_data_list = [{"日期": r['weight_date'], "体重": r['weight'], "id": r['id']} for r in w_res.data]
        
        # 加载日记
        l_res = supabase.table("daily_logs").select("*").eq("user_name", user).order("log_date", desc=True).execute()
        st.session_state.daily_logs = l_res.data
    except Exception as e:
        st.error(f"数据加载失败: {e}")

def delete_record(table_name, record_id):
    """从数据库物理删除记录"""
    try:
        supabase.table(table_name).delete().eq("id", record_id).execute()
        st.success("记录已成功抹除 ✨")
        st.rerun()
    except Exception as e:
        st.error(f"删除失败: {e}")

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
    h1, h2, h3 { color: #ff6b81 !important; text-align: center !important; }
    .stButton>button { border-radius: 25px !important; background-color: #ff6b81 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 侧边栏：身份切换与监控 ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>🗼 身份切换</h2>", unsafe_allow_html=True)
    current_user = st.radio("当前登录：", ["小夏", "小耗子"], horizontal=True)
    st.info(f"正在查看 **{current_user}** 的专属分区")
    
    st.divider()
    days_left = (datetime.date(2026, 6, 23) - datetime.date.today()).days
    st.metric("距离重逢还有", f"{days_left} 天")
    st.progress(max(0, min(100, 100 - int(days_left / 540 * 100))))
    
    st.divider()
    api_key_input = st.text_input("🔑 API 秘钥", value=DEFAULT_API_KEY, type="password")

# --- 4. 逻辑触发：切换身份时自动刷新数据 ---
load_all_data(current_user)

# --- 5. 主界面 ---
st.markdown(f"<h1>💖 {current_user} 的秘密基地</h1>", unsafe_allow_html=True)
days_together = (datetime.date.today() - LOVE_START_DATE).days
st.markdown(f"<p style='text-align:center;'>并肩作战的第 {days_together} 天 🎉</p>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["🌸 生活时光机", "📉 数学减脂美学", "🎒 东京大冒险", "💌 元旦秘密信箱"])

with tab1:
    col_l, col_r = st.columns([2, 1])
    with col_l:
        with st.form("daily_form", clear_on_submit=True):
            st.subheader(f"📝 记录 {current_user} 的今日点滴")
            log_date = st.date_input("日期", datetime.date.today())
            sports = st.multiselect("🏃 运动健身", ["呼啦圈", "散步", "打羽毛球", "健身房", "拉伸"])
            diet = st.select_slider("🥗 饮食控制", options=["放纵餐🍕", "正常饮食🍚", "清淡少油🥗", "严格减脂🥦"], value="正常饮食🍚")
            st.write("---")
            ch1, ch2 = st.columns(2)
            is_poop = ch1.radio("💩 今日是否大便？", ["未排便", "顺利排便 ✅"], horizontal=True)
            water = ch2.slider("💧 饮水量 (L)", 0.5, 4.0, 2.0, 0.5)
            detail = st.text_area("💌 碎碎念/备注", placeholder="录入错误请在下方删除后重新提交...")
            mood = st.select_slider("✨ 心情", options=["😢", "😟", "😐", "😊", "🥰"], value="😊")

            if st.form_submit_button("存入时光机"):
                supabase.table("daily_logs").insert({
                    "user_name": current_user, "log_date": str(log_date), "sports": "|".join(sports),
                    "diet": diet, "is_poop": is_poop, "water": water, "detail": detail, "mood": mood
                }).execute()
                st.rerun()

        if st.session_state.daily_logs:
            st.subheader("📜 历史数据管理 (可删除错误记录)")
            for log in st.session_state.daily_logs:
                with st.expander(f"📅 {log['log_date']} - 心情: {log['mood']}"):
                    st.write(f"**运动:** {log['sports']} | **饮食:** {log['diet']} | **排便:** {log['is_poop']}")
                    if log['detail']: st.info(f"💌 {log['detail']}")
                    if st.button("🗑️ 删除该条记录", key=f"del_log_{log['id']}"):
                        delete_record("daily_logs", log['id'])

    with col_r:
        st.markdown("### 🤖 AI 深度审计")
        if st.button("生成今日审计报告", use_container_width=True):
            if api_key_input and st.session_state.daily_logs:
                with st.spinner("AI 正在阅卷..."):
                    try:
                        df_w = pd.DataFrame(st.session_state.weight_data_list)
                        last = st.session_state.daily_logs[0]
                        client = OpenAI(api_key=api_key_input, base_url="https://api.deepseek.com")
                        prompt = f"你是理科生伴侣‘小耗子’。{current_user}今日排便{last.get('is_poop')}，饮水{last.get('water')}L，饮食{last.get('diet')}。请给出严谨且温柔的建议。"
                        response = client.chat.completions.create(model="deepseek-chat", messages=[{"role": "user", "content": prompt}])
                        st.info(response.choices[0].message.content)
                    except: st.error("AI 暂时休息了")

with tab2:
    st.subheader(f"📈 {current_user} 的减脂动力学曲线")
    df_weight = pd.DataFrame(st.session_state.weight_data_list)
    if not df_weight.empty:
        df_weight['日期'] = pd.to_datetime(df_weight['日期'])
        calc_df = df_weight.sort_values('日期').drop_duplicates('日期', keep='last')
        pred_res, slope = get_prediction(calc_df)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("日均斜率", f"{slope:.3f}")
        c2.metric("待减体重", f"{round(calc_df['体重'].iloc[-1] - 55.0, 1)} kg" if current_user=="小夏" else "保持中")
        c3.metric("预测达标日", pred_res.strftime('%Y-%m-%d') if isinstance(pred_res, datetime.date) else "计算中")
        
        st.plotly_chart(px.line(calc_df, x="日期", y="体重", markers=True, color_discrete_sequence=['#ff6b81']), use_container_width=True)
        
        with st.expander("📝 体重数据列表 (点击红色按钮删除错误值)"):
            for w_entry in reversed(st.session_state.weight_data_list):
                cw1, cw2, cw3 = st.columns([2, 2, 1])
                cw1.write(w_entry['日期'])
                cw2.write(f"{w_entry['体重']} kg")
                if cw3.button("❌", key=f"del_w_{w_entry['id']}"):
                    delete_record("weight_data", w_entry['id'])
    
    with st.form("weight_update"):
        st.markdown(f"**同步 {current_user} 的新体重**")
        w_val = st.number_input("体重 (kg)", value=60.0, step=0.1)
        w_date = st.date_input("测量日期", datetime.date.today())
        if st.form_submit_button("上传数据"):
            supabase.table("weight_data").insert({"user_name": current_user, "weight_date": str(w_date), "weight": w_val}).execute()
            st.rerun()

with tab3: # 东京大冒险
    st.markdown("## 🎆 夏日花火之约")
    st.image("https://img.picgo.net/2024/05/22/fireworks_kimono_anime18090543e86c0757.md.png", use_container_width=True)

with tab4: # 元旦信箱
    st.markdown("## 📟 跨年加密指令")
    if st.text_input("授权码：", type="password") == "wwhaxxy1314":
        st.balloons()
        st.markdown("""<div style="background-color: #fff0f3; padding: 25px; border-radius: 15px; border: 1px dashed #ff6b81;">
            亲爱的小夏/小耗子：任务仍在继续，重逢就在终点。</div>""", unsafe_allow_html=True)
