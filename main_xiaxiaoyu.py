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
    if df is None or len(df) < 2: return None, 0
    try:
        temp_df = df.copy()
        temp_df['日期_ts'] = pd.to_datetime(temp_df['日期']).map(datetime.date.toordinal)
        x, y = temp_df['日期_ts'].values, temp_df['体重'].values.astype(float)
        slope, intercept = np.polyfit(x, y, 1)
        target_date = datetime.date.fromordinal(int((55.0 - intercept) / slope)) if slope < 0 else None
        return target_date, slope
    except: return None, 0

def calculate_calories(sports_list, sport_mins, pushups, floors, weight):
    met_map = {"散步": 2.5, "呼啦圈": 3.0, "羽毛球": 4.5, "健身房": 5.5, "拉伸": 2.0}
    total_kcal = 0
    active_sports = [s for s in sports_list if s in met_map]
    if active_sports and sport_mins > 0:
        avg_met = sum(met_map[s] for s in active_sports) / len(active_sports)
        total_kcal += avg_met * weight * (sport_mins / 60)
    if "俯卧撑" in sports_list: total_kcal += pushups * 0.5
    if "爬楼" in sports_list: total_kcal += floors * 3.0
    return round(total_kcal, 1)

# --- 3. UI 样式 (手机夜间模式强制适配) ---
st.set_page_config(page_title="2026东京之约", layout="wide", page_icon="🗼")
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #fff5f7 0%, #f0f4ff 100%); }
    h1, h2, h3 { color: #ff6b81 !important; text-align: center !important; }
    .diary-card { background-color: #ffffff; padding: 15px; border-radius: 12px; border-left: 5px solid #ff6b81; margin-top: 10px; color: #333; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .reply-card { background-color: #f0f7ff; padding: 12px; border-radius: 10px; border-left: 5px solid #4a90e2; margin-top: 8px; color: #333; font-size: 0.95em; }
    .kcal-box { background: #fff9db; border: 1px solid #fcc419; padding: 10px; border-radius: 8px; color: #e67700; font-weight: bold; text-align: center; }

    @media (prefers-color-scheme: dark) {
        .stApp { background: linear-gradient(135deg, #1a1a1a 0%, #0f1116 100%) !important; }
        .diary-card { background-color: #262626 !important; color: #efefef !important; border-left: 5px solid #ff8fa3 !important; }
        .reply-card { background-color: #1e2530 !important; color: #d1d1d1 !important; border-left: 5px solid #6a89cc !important; }
        .kcal-box { background: #332b00 !important; color: #ffd43b !important; }
        p, span, label, div, .stMarkdown { color: #dddddd !important; }
        [data-testid="stMetricValue"] { color: #ff8fa3 !important; }
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
    api_key_input = st.text_input("🔑 API 秘钥", value=DEFAULT_API_KEY, type="password")

load_all_data(current_user)

# --- 5. 主界面 ---
st.markdown(f"<h1>💖 {current_user} 的专属分区</h1>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["🌸 时光机", "📉 减脂美学", "🎒 东京冒险", "💌 元旦信箱"])

with tab1:
    col_l, col_r = st.columns([1.8, 1.2])
    with col_l:
        st.subheader("📝 深度记录")
        selected_sports = st.multiselect("🏃 今日运动项", ["呼啦圈", "散步", "羽毛球", "健身房", "拉伸", "俯卧撑", "爬楼"])
        
        # 实时获取最新体重用于计算
        active_w = 60.0
        if 'weight_data_list' in st.session_state and st.session_state.weight_data_list:
            active_w = st.session_state.weight_data_list[-1]['体重']

        log_date = st.date_input("📅 记录日期", datetime.date.today())
        
        pushup_cnt, floor_cnt, sport_mins = 0, 0, 0
        has_others = any(s in selected_sports for s in ["呼啦圈", "散步", "羽毛球", "健身房", "拉伸"])
        sc1, sc2, sc3 = st.columns(3)
        if has_others: sport_mins = sc1.slider("基础时长 (min)", 0, 180, 30)
        if "俯卧撑" in selected_sports: pushup_cnt = sc2.number_input("俯卧撑次数", 0, 1000, 30)
        if "爬楼" in selected_sports: floor_cnt = sc3.number_input("爬楼层数", 0, 200, 10)
        
        estimated_kcal = calculate_calories(selected_sports, sport_mins, pushup_cnt, floor_cnt, active_w)
        if selected_sports:
            st.markdown(f'<div class="kcal-box">🔥 本次运动预计消耗：{estimated_kcal} kcal</div>', unsafe_allow_html=True)

        st.divider()
        diet_detail = st.text_area("🍱 今日饮食明细") if current_user == "小夏" else ""
        diet_lv = st.select_slider("🥗 饮食控制", options=["放纵🍕", "正常🍚", "清淡🥗", "严格🥦"], value="正常🍚")
        
        is_poop, water, part_time = "N/A", 0.0, 0.0
        col_h1, col_h2 = st.columns(2)
        if current_user == "小夏":
            is_poop = col_h1.radio("💩 今日排便情况", ["未排便", "顺利排便 ✅"], horizontal=True)
            water = col_h2.slider("💧 饮水量 (L)", 0.5, 4.0, 2.0, 0.5)
        else:
            part_time = col_h1.number_input("⏳ 今日兼职时长 (h)", 0.0, 14.0, 0.0)

        work_h = st.slider("⏳ 专注/学术时长 (h)", 0.0, 14.0, 4.0, step=0.5)
        mood_val = st.select_slider("✨ 今日心情", options=["😢", "😟", "😐", "😊", "🥰"], value="😊")
        user_note = st.text_area("💌 备注/碎碎念", placeholder="今天有什么想对TA说的？")

        if st.button("🚀 同步数据到云端", use_container_width=True):
            prefix = ""
            if pushup_cnt > 0: prefix += f"【💪 俯卧撑：{pushup_cnt}个】"
            if floor_cnt > 0: prefix += f"【🪜 爬楼：{floor_cnt}层】"
            if estimated_kcal > 0: prefix += f"【🔥 消耗：{estimated_kcal}kcal】"
            final_detail = f"{prefix} {user_note}"
            final_sport_val = float(sport_mins) if has_others else (float(pushup_cnt) if pushup_cnt>0 else float(floor_cnt))
            
            supabase.table("daily_logs").insert({
                "user_name": current_user, "log_date": str(log_date), "sports": "|".join(selected_sports),
                "sport_minutes": final_sport_val, "diet": diet_lv, "diet_detail": diet_detail,
                "is_poop": is_poop, "water": water, "academic_hours": float(work_h), 
                "part_time_hours": float(part_time), "detail": final_detail, "mood": mood_val
            }).execute()
            st.success("✅ 同步成功！")
            st.rerun()

        st.divider()
        st.subheader("📜 历史互动存证")
        if "daily_logs" in st.session_state and st.session_state.daily_logs:
            for log in st.session_state.daily_logs[:15]:
                owner = "🌸" if log['user_name'] == "小夏" else "🐭"
                with st.expander(f"{owner} {log['log_date']} - 心情: {log['mood']}"):
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        if log['user_name'] == "小夏":
                            st.write(f"🍱 **饮食:** {log.get('diet_detail') or '未记'} | 💩 **排便:** {log['is_poop']} | 💧 **饮水:** {log['water']}L")
                        st.write(f"🏃 **运动:** {log['sports']} ({log['sport_minutes']}) | 💻 **学术:** {log.get('academic_hours')}h")
                        st.markdown(f'<div class="diary-card"><b>{owner} 碎碎念：</b><br>{log["detail"]}</div>', unsafe_allow_html=True)
                        reply = log.get('comment_from_haozhi')
                        if reply:
                            reply_label = "🐭 小耗子回应" if log['user_name'] == "小夏" else "🌸 小夏回应"
                            st.markdown(f'<div class="reply-card"><b>{reply_label}：</b><br>{reply}</div>', unsafe_allow_html=True)
                    with c2:
                        if current_user != log['user_name']:
                            ans = st.text_area("回复TA", key=f"ans_{log['id']}")
                            if st.button("发送", key=f"b_{log['id']}"):
                                supabase.table("daily_logs").update({"comment_from_haozhi": ans}).eq("id", log['id']).execute()
                                st.rerun()
                        if current_user == log['user_name']:
                            if st.button("🗑️", key=f"d_{log['id']}"):
                                supabase.table("daily_logs").delete().eq("id", log['id']).execute()
                                st.rerun()

    with col_r:
        st.markdown("### 🤖 智能深度审计")
        if st.button("🚀 生成小夏专项分析", use_container_width=True):
            if api_key_input and st.session_state.daily_logs:
                xia_logs = [l for l in st.session_state.daily_logs if l['user_name'] == "小夏"][:10]
                # 获取体重斜率逻辑
                slope_val = 0
                if 'weight_data_list' in st.session_state and len(st.session_state.weight_data_list) >= 2:
                    df_w = pd.DataFrame(st.session_state.weight_data_list)
                    _, slope_val = get_prediction(df_w)
                
                history_str = "\n".join([f"- {l['log_date']}: 排便[{l['is_poop']}], 饮水[{l['water']}L], 备注[{l['detail']}]" for l in xia_logs])
                
                client = OpenAI(api_key=api_key_input, base_url="https://api.deepseek.com")
                prompt = f"""你是理科伴侣小耗子。小夏正在服用氯氮平，近期体重斜率为 {slope_val:.3f} kg/d。
                历史数据如下：
                {history_str}
                请结合【排便频率】、【饮水量】和【备注里的情绪】给出一段专业且温柔的回复。"""
                
                res = client.chat.completions.create(model="deepseek-chat", messages=[{"role": "user", "content": prompt}])
                st.session_state.chat_history = [{"role": "assistant", "content": res.choices[0].message.content}]
                st.rerun()
        if "chat_history" in st.session_state:
            for m in st.session_state.chat_history:
                with st.chat_message(m["role"], avatar="🐭" if m["role"]=="assistant" else "🌸"):
                    st.markdown(m["content"])

with tab2:
    if current_user == "小夏":
        st.markdown("### 📉 减脂美学：目标 55.0 kg")
        if 'weight_data_list' in st.session_state and len(st.session_state.weight_data_list) > 0:
            df_w = pd.DataFrame(st.session_state.weight_data_list)
            df_w['日期'] = pd.to_datetime(df_w['日期'])
            calc_df = df_w.sort_values('日期').drop_duplicates('日期', keep='last')
            
            # 安全逻辑：只有超过2个点才计算预测
            pred_date, weight_slope = get_prediction(calc_df)
            
            c1, c2, c3 = st.columns(3)
            curr_w = calc_df['体重'].iloc[-1]
            c1.metric("当前斜率", f"{weight_slope:.3f} kg/d")
            c2.metric("距离目标", f"{round(curr_w - 55.0, 1)} kg", delta=f"{weight_slope:.3f}", delta_color="inverse")
            if pred_date: c3.metric("达标预估", pred_date.strftime('%Y-%m-%d'))
            
            st.plotly_chart(px.line(calc_df, x="日期", y="体重", markers=True, color_discrete_sequence=['#ff6b81']), use_container_width=True)
        else:
            st.info("尚未录入体重数据，请在下方开始同步吧！")

        with st.form("weight_form_fix"):
            ca, cb = st.columns(2)
            new_val = ca.number_input("体重 (kg)", value=60.0, step=0.1)
            new_dt = cb.date_input("测量日期", datetime.date.today())
            if st.form_submit_button("同步体重"):
                supabase.table("weight_data").insert({"user_name": "小夏", "weight_date": str(new_dt), "weight": new_val}).execute()
                st.rerun()
    else:
        st.info("📉 这是小夏的减脂管理区，小耗子请切换回小夏身份查看。")

with tab3: st.image("https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?auto=format&fit=crop&w=1200&q=80", use_container_width=True)
with tab4:
    st.markdown("## 📟 2026 跨年信箱")
    auth_code = st.text_input("Access Code：", type="password", key="final_auth")
    if auth_code == "wwhaxxy1314":
        st.balloons()
        st.markdown('<div class="diary-card">🌸 宝儿：跨年快乐！新的一年我们一起努力！</div>', unsafe_allow_html=True)
