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
        l_res = supabase.table("daily_logs").select("*").order("log_date", desc=True).execute()
        st.session_state.daily_logs = l_res.data
    except Exception as e: st.error(f"加载失败: {e}")

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
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #fff5f7 0%, #f0f4ff 100%); }
    h1, h2, h3 { color: #ff6b81 !important; text-align: center !important; }
    .diary-card { background-color: #fff0f3; padding: 15px; border-radius: 12px; border-left: 5px solid #ff6b81; margin-top: 10px; color: #333; }
    .comment-card { background-color: #e3f2fd; padding: 12px; border-radius: 10px; border-left: 5px solid #2196f3; margin-top: 5px; color: #333; }
    .stButton>button { border-radius: 25px !important; background-color: #ff6b81 !important; color: white !important; font-weight: bold; }
    @media (prefers-color-scheme: dark) {
        .stApp { background: linear-gradient(135deg, #1e1e1e 0%, #121212 100%) !important; }
        .diary-card { background-color: #2d2d2d !important; color: #efefef !important; }
        .comment-card { background-color: #0d47a1 !important; color: #e0e0e0 !important; }
    }
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
        st.subheader(f"📝 {current_user} 的深度记录")
        
        # 1. 运动项目（实时响应）
        selected_sports = st.multiselect("🏃 今日运动项目", ["呼啦圈", "散步", "羽毛球", "健身房", "拉伸", "俯卧撑"])
        
        with st.form("master_diary_form", clear_on_submit=True):
            log_date = st.date_input("日期", datetime.date.today())
            
            # 2. 运动详情逻辑
            pushup_cnt = 0
            sport_mins = 0
            has_pushup = "俯卧撑" in selected_sports
            has_others = any(s in selected_sports for s in ["呼啦圈", "散步", "羽毛球", "健身房", "拉伸"])
            
            if has_others:
                sport_mins = st.slider("⏱️ 基础运动时长 (分钟)", 0, 180, 30, step=5)
            if has_pushup:
                pushup_cnt = st.number_input("💪 俯卧撑总次数", min_value=0, value=30, step=5)
            
            st.divider()
            
            # 3. 核心健康指标（所有情况都包括）
            diet_detail = st.text_area("🍱 今日饮食明细") if current_user == "小夏" else ""
            diet_lv = st.select_slider("🥗 饮食控制等级", options=["放纵🍕", "正常🍚", "清淡🥗", "严格🥦"], value="正常🍚")
            
            is_poop, water, part_time = "N/A", 0.0, 0.0
            if current_user == "小夏":
                c1, c2 = st.columns(2)
                is_poop = c1.radio("💩 今日排便情况", ["未排便", "顺利排便 ✅"], horizontal=True)
                water = c2.slider("💧 饮水量 (L)", 0.5, 4.0, 2.0, 0.5)
            else:
                part_time = st.number_input("⏳ 今日兼职时长 (小时)", 0.0, 14.0, 0.0, step=0.5)
            
            # 4. 学术与心情
            st.divider()
            work_items = st.multiselect("💻 学术与工作", ["看文献", "写论文", "找工作", "日常业务"])
            work_h = st.slider("⏳ 专注时长 (小时)", 0.0, 14.0, 4.0, step=0.5)
            user_note = st.text_area("💌 碎碎念/备注", placeholder="想对另一半说的话，或者今天的小情绪...")
            mood_val = st.select_slider("✨ 心情状态", options=["😢", "😟", "😐", "😊", "🥰"], value="😊")

            if st.form_submit_button("🚀 同步到云端"):
                # 整合运动次数到备注前缀，不丢失原备注
                final_detail = f"【💪 俯卧撑：{pushup_cnt}个】 {user_note}" if has_pushup else user_note
                # 存储数值：主运动时长，若只有俯卧撑则存次数
                final_val = float(sport_mins) if has_others else float(pushup_cnt)
                
                supabase.table("daily_logs").insert({
                    "user_name": current_user, "log_date": str(log_date), 
                    "sports": "|".join(selected_sports), "sport_minutes": final_val,
                    "diet": diet_lv, "diet_detail": diet_detail, 
                    "is_poop": is_poop, "water": water,
                    "work": "|".join(work_items), "academic_hours": float(work_h), 
                    "part_time_hours": float(part_time), 
                    "detail": final_detail, "mood": mood_val
                }).execute()
                st.rerun()

        st.divider()
        st.subheader("📜 历史存证与互动")
        if st.session_state.daily_logs:
            for log in st.session_state.daily_logs[:15]:
                label = "🌸" if log['user_name'] == "小夏" else "🐭"
                with st.expander(f"{label} {log['log_date']} - 心情: {log['mood']}"):
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        if log['user_name'] == "小夏":
                            st.write(f"🍱 **饮食:** {log.get('diet_detail') or '未记'} | 💩 **排便:** {log['is_poop']} | 💧 **饮水:** {log['water']}L")
                        else:
                            st.write(f"💰 **兼职:** {log['part_time_hours']}h")
                        
                        unit = "个" if ("俯卧撑" in (log['sports'] or "") and not any(s in (log['sports'] or "") for s in ["散步", "羽毛球", "呼啦圈"])) else "min"
                        st.write(f"🏃 **运动:** {log['sports']} ({log['sport_minutes']}{unit})")
                        st.markdown(f'<div class="diary-card">💌 {log["detail"]}</div>', unsafe_allow_html=True)
                        
                        # 显示回复
                        reply = log.get('comment_from_haozhi')
                        if reply:
                            st.markdown(f'<div class="comment-card">🐭 小耗子回复：{reply}</div>', unsafe_allow_html=True)
                    
                    with c2:
                        if current_user == "小耗子" and log['user_name'] == "小夏":
                            ans = st.text_area("快速回复", key=f"ans_{log['id']}")
                            if st.button("提交", key=f"b_{log['id']}"):
                                supabase.table("daily_logs").update({"comment_from_haozhi": ans}).eq("id", log['id']).execute()
                                st.rerun()
                        if current_user == log['user_name']:
                            if st.button("🗑️ 删除", key=f"d_{log['id']}"):
                                supabase.table("daily_logs").delete().eq("id", log['id']).execute()
                                st.rerun()

    with col_r:
        st.markdown("### 🤖 智能复盘审计")
        if "chat_history" not in st.session_state: st.session_state.chat_history = []
        
        if st.button("🚀 生成小夏专项审计报告", use_container_width=True):
            if api_key_input and st.session_state.daily_logs:
                with st.spinner("小耗子AI正在深度穿透数据..."):
                    # 过滤小夏的数据
                    xia_logs = [l for l in st.session_state.daily_logs if l['user_name'] == "小夏"][:10]
                    weight_df = pd.DataFrame(st.session_state.weight_data_list)
                    _, slope = get_prediction(weight_df)
                    
                    # 构造 AI 上下文：包括所有情况（排便、碎碎念、饮水）
                    history_context = "\n".join([
                        f"- {l['log_date']}: 饮食[{l['diet']}], 排便[{l['is_poop']}], 饮水[{l['water']}L], 备注[{l['detail']}]" 
                        for l in xia_logs
                    ])
                    
                    system_prompt = f"""
                    你是理科伴侣小耗子。小夏在服用氯氮平，目标是稳步减重。
                    当前体重斜率: {slope:.3f} kg/d。
                    近期详细数据记录:
                    {history_context}
                    
                    请结合以上【所有情况】给出一份专业审计报告：
                    1. 代谢与肠道：氯氮平会导致肠蠕动慢，请死磕她的排便记录和饮水量。
                    2. 运动建议：根据记录的运动强度是否足以对冲药物导致的代谢下降。
                    3. 碎碎念回应：这是最重要的。请从她的备注中感受她的情绪，以小耗子的身份给予理性的分析和感性的支持。
                    """
                    
                    client = OpenAI(api_key=api_key_input, base_url="https://api.deepseek.com")
                    res = client.chat.completions.create(
                        model="deepseek-chat", 
                        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": "请综合分析我的记录。"}]
                    )
                    st.session_state.chat_history = [{"role": "assistant", "content": res.choices[0].message.content}]
                    st.rerun()

        # 审计展示区
        for m in st.session_state.chat_history:
            with st.chat_message(m["role"], avatar="🐭" if m["role"]=="assistant" else "🌸"):
                st.markdown(m["content"])
    # --- Tab 2/3/4 部分保持原样 ---
with tab2:
    if current_user == "小夏":
        st.markdown("### 📉 减脂美学：目标 55.0 kg")
        if 'weight_data_list' in st.session_state and st.session_state.weight_data_list:
            df_w = pd.DataFrame(st.session_state.weight_data_list)
            df_w['日期'] = pd.to_datetime(df_w['日期'])
            calc_df = df_w.sort_values('日期').drop_duplicates('日期', keep='last')
            pred_res, slope = get_prediction(calc_df)
            c1, c2, c3 = st.columns(3)
            current_w = calc_df['体重'].iloc[-1]
            c1.metric("当前斜率", f"{slope:.3f} kg/d")
            c2.metric("距离目标", f"{round(current_w - 55.0, 1)} kg", delta=f"{slope:.3f}", delta_color="inverse")
            if isinstance(pred_res, datetime.date): c3.metric("达标预估", pred_res.strftime('%Y-%m-%d'))
            st.plotly_chart(px.line(calc_df, x="日期", y="体重", markers=True, color_discrete_sequence=['#ff6b81']), use_container_width=True)
            with st.expander("🛠️ 历史数据管理"):
                for _, row in calc_df.sort_values('日期', ascending=False).iterrows():
                    c_d, c_v, c_b = st.columns([2, 2, 1])
                    c_d.write(row['日期'].strftime('%Y-%m-%d'))
                    c_v.write(f"{row['体重']} kg")
                    if c_b.button("🗑️ 删除", key=f"del_w_{row['id']}"):
                        supabase.table("weight_data").delete().eq("id", row['id']).execute()
                        st.rerun()
        with st.form("weight_form_new"):
            ca, cb = st.columns(2)
            new_val = ca.number_input("体重 (kg)", value=60.0, step=0.1)
            new_dt = cb.date_input("测量日期", datetime.date.today())
            if st.form_submit_button("同步"):
                supabase.table("weight_data").insert({"user_name": "小夏", "weight_date": str(new_dt), "weight": new_val}).execute()
                st.rerun()

with tab3:
    st.image("https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?auto=format&fit=crop&w=1200&q=80", caption="2026, 重逢在东京", use_container_width=True)

with tab4:
    st.markdown("## 📟 2026 跨年信箱")
    auth_code = st.text_input("输入 Access Code：", type="password", key="final_auth")
    if auth_code == "wwhaxxy1314":
        st.balloons()
        letter_content = """
        <div class="diary-card" style="line-height: 1.8; letter-spacing: 1px;">
            <h3 style='text-align: left !important;'>🌸 宝儿：</h3>
            <p><b>跨年快乐！</b></p>
            <p>再过一天，就是我们的一周年纪念日了...</p>
            <div style="text-align: right; margin-top: 20px;">
                <b>—— [运维负责人: 小耗子 🐭]</b><br>
                <i>2025/12/31</i>
            </div>
        </div>
        """
        st.markdown(letter_content, unsafe_allow_html=True)

