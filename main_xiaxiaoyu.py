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
    .diary-card { background-color: #fff0f3; padding: 12px; border-radius: 12px; border-left: 4px solid #ff6b81; margin-top: 10px; color: #333; }
    .report-box { background-color: #f0f4ff; padding: 20px; border-radius: 15px; border-left: 8px solid #6a89cc; margin-top: 20px; color: #333; }
    .stButton>button { border-radius: 25px !important; background-color: #ff6b81 !important; color: white !important; }
    
    @media (prefers-color-scheme: dark) {
        .stApp { background: linear-gradient(135deg, #1e1e1e 0%, #121212 100%) !important; }
        .diary-card { background-color: #2d2d2d !important; color: #efefef !important; border-left: 4px solid #ff6b81 !important; }
        .report-box { background-color: #1e2530 !important; color: #efefef !important; border-left: 8px solid #6a89cc !important; }
        h1, h2, h3 { color: #ff8fa3 !important; }
        [data-testid="stSidebar"] { background-color: #1a1a1a !important; }
        .stMarkdown, p, span { color: #dddddd !important; }
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

days_together = (datetime.date.today() - LOVE_START_DATE).days
st.markdown(f"<p style='text-align:center;'>这是我们守护彼此的第 {days_together} 天 🎉</p>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["🌸 时光机", "📉 减脂美学", "🎒 东京冒险", "💌 元旦信箱"])

with tab1:
    col_l, col_r = st.columns([1.8, 1.2])
    with col_l:
        st.subheader(f"📝 {current_user} 的深度记录")
        
        # --- 关键修改：将运动选择移出 form 以外以实现实时交互 ---
        selected_sports = st.multiselect("🏃 运动项目", ["呼啦圈", "散步", "羽毛球", "健身房", "拉伸", "俯卧撑"])
        is_pushup_mode = "俯卧撑" in selected_sports

        with st.form("daily_form_v_master", clear_on_submit=True):
            log_date = st.date_input("日期", datetime.date.today())
            diet_detail = st.text_area("🍱 今日饮食明细", placeholder="具体吃了什么？") if current_user == "小夏" else ""
            
            # 动态切换输入组件
            if is_pushup_mode:
                sport_value = st.number_input("💪 俯卧撑总次数 (个)", min_value=0, max_value=1000, value=30, step=5)
            else:
                sport_value = st.slider("⏱️ 运动时长 (分钟)", 0, 180, 30, step=5)
            
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
            
            work = st.multiselect("💻 学术与工作内容", ["看文献", "写论文", "找工作", "其他"])
            work_time = st.slider("⏳ 专注时长 (小时)", 0.0, 14.0, 4.0, step=0.5)
            work_focus = st.select_slider("🎯 专注状态", options=["走神😴", "断续☕", "专注📚", "心流🔥"], value="专注📚")
            detail = st.text_area("💌 碎碎念/备注")
            mood = st.select_slider("✨ 心情", options=["😢", "😟", "😐", "😊", "🥰"], value="😊")

            if st.form_submit_button("同步到云端"):
                supabase.table("daily_logs").insert({
                    "user_name": current_user, 
                    "log_date": str(log_date), 
                    "sports": "|".join(selected_sports),
                    "sport_minutes": float(sport_value), 
                    "diet": diet_type, 
                    "diet_detail": diet_detail,
                    "is_poop": is_poop, 
                    "water": water, 
                    "work": "|".join(work),
                    "academic_hours": float(work_time), 
                    "part_time_hours": float(part_time),
                    "detail": detail, 
                    "mood": mood, 
                    "focus_level": work_focus
                }).execute()
                st.rerun()

        st.divider()
        st.subheader("📜 历史存证")
        if st.session_state.daily_logs:
            for log in st.session_state.daily_logs[:10]:
                with st.expander(f"📅 {log['log_date']} - 心情: {log['mood']}"):
                    c_info, c_del = st.columns([4, 1])
                    with c_info:
                        if current_user == "小夏":
                            st.write(f"🍱 **饮食:** {log.get('diet_detail', '未记录')}")
                            st.write(f"💩 **排便:** {log['is_poop']} | 💧 **饮水:** {log['water']}L")
                        
                        # 历史记录单位适配
                        unit = "个" if "俯卧撑" in (log.get('sports') or "") else "min"
                        st.write(f"🏃 **运动:** {log['sports']} ({log.get('sport_minutes')}{unit})")
                        
                        st.write(f"📚 **学术:** {log.get('work')} ({log.get('academic_hours')}h)")
                        if log['detail']: st.markdown(f'<div class="diary-card">💌 {log["detail"]}</div>', unsafe_allow_html=True)
                    with c_del:
                        if st.button("🗑️ 删除", key=f"del_log_{log['id']}"):
                            supabase.table("daily_logs").delete().eq("id", log['id']).execute()
                            st.rerun()

    with col_r:
        st.markdown("### 🤖 智能审计与追问")
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        if st.button("🚀 生成深度分析复盘", use_container_width=True):
            if api_key_input and st.session_state.daily_logs:
                with st.spinner("小耗子正在复盘近十天数据..."):
                    history_logs = st.session_state.daily_logs[:10]
                    weight_df = pd.DataFrame(st.session_state.weight_data_list)
                    _, slope = get_prediction(weight_df)
                    history_str = "\n".join([f"- {l['log_date']}: 饮食[{l.get('diet_detail')}] 运动[{l['sports']}]" for l in history_logs])
                    system_prompt = f"你是理科伴侣小耗子。小夏在用氯氮平减重。历史数据：{history_str}\n当前体重斜率：{slope:.3f}"
                    client = OpenAI(api_key=api_key_input, base_url="https://api.deepseek.com")
                    response = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": "请提供报告。"}]
                    )
                    st.session_state.chat_history = [{"role": "assistant", "content": response.choices[0].message.content}]
            else: st.warning("请检查配置。")

        st.markdown("---")
        chat_container = st.container(height=500)
        with chat_container:
            for message in st.session_state.chat_history:
                with st.chat_message(message["role"], avatar="🐭" if message["role"]=="assistant" else "🌸"):
                    st.markdown(message["content"])

        if prompt := st.chat_input("你想追问小耗子什么？"):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with chat_container:
                with st.chat_message("user", avatar="🌸"): st.markdown(prompt)
            with st.chat_message("assistant", avatar="🐭"):
                client = OpenAI(api_key=api_key_input, base_url="https://api.deepseek.com")
                chat_response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[{"role": "system", "content": "你是理科伴侣小耗子。"}] + st.session_state.chat_history
                )
                full_response = chat_response.choices[0].message.content
                st.markdown(full_response)
            st.session_state.chat_history.append({"role": "assistant", "content": full_response})

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
        # 使用三引号包裹长文本，解决报错问题
        letter_content = """
        <div class="diary-card" style="line-height: 1.8; letter-spacing: 1px;">
            <h3 style='text-align: left !important;'>🌸 宝儿：</h3>
            <p><b>跨年快乐！</b></p>
            <p>再过一天，就是我们的一周年纪念日了。还是像以前一样，我想用文字把平时嘴笨说不出口的心里话，慢慢写给你听。</p>
            <p>回首这一年，我确实不算是一个合格的男朋友。我没能时刻陪在你身边，还总是惹你生气。虽然我们一直处于异地，但不得不承认，我们好像过早地跨越了那段无忧无虑的甜蜜期。在本该最腻歪的阶段，我没能守着你，甚至还眼睁睁看着病魔这只拦路虎闯进了你的生活，把你困在了医院里。</p>
            <p>现在回想起来，那段日子依然像石头一样压在我心口。我时常想起你在住院前跟我说过的那些话，那种无力感让我窒息，我真的很怕，怕失去你，怕那个熟悉的你离我远去。</p>
            <p>在东京的时候，我对你说过那样的话，我说你不够积极，想让你振作一点。现在想来，我真的很想抽自己一下。那时的我太粗心了，我唯独没有认真考虑药物对你的影响——我居然忘了，不是你不想积极，是药物的副作用在拖着你。</p>
            <p>宝儿，关于那句话，我郑重地向你说声对不起，以后我再也不会说这种话了。</p>
            <p>最近我又开始频繁地想这件事。我时常会问，为什么是你？为什么要让你这么善良的女孩承受这些？</p>
            <p>我也时常幻想：如果我每天都在你身边就好了。我想象着我能像个严格又温柔的管家，督促你吃药，为你搭配健康的饮食，拉着你去运动，陪你去面对医生……在我的幻想里，这是一个完美的剧本，我像个超级英雄一样把你从水火中拯救出来。</p>
            <p>虽然目前的阶段，现实让我没办法立刻做到这一步，但我不想放弃。我这人虽然时常悲观，总是习惯先把事情往最坏的地方想；但我又时常极其自信—我坚信我能避开所有坏的可能，找到那个唯一的解决办法。</p>
            <p>无论是以前读本科，还是现在，宝儿，你一直都是我的白月光。哪怕现在药物让你觉得身体沉重，哪怕现在我们隔着距离，但我会用我的方式去战斗。所以宝儿相信我，我会尽力帮助你，就算是异地，我也会尽全力帮你恢复健康，我会帮助你找回你已经忘记了的以前的面孔。我会陪你一起，把那个自信、爱笑、漂亮的你，一点点找回来。</p>
            <p>但是更重要的一点，宝儿，请你也相信你自己，新的一年，我们一起努力。把身体养好。以前是你一个人在对抗，以后，我们一起努力。</p>
            <div style="text-align: right; margin-top: 20px;">
                <b>—— [运维负责人: 小耗子 🐭]</b><br>
                <i>2025/12/31</i>
            </div>
        </div>
        """
        st.markdown(letter_content, unsafe_allow_html=True)





