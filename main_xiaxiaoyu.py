import streamlit as st
import pandas as pd
import plotly.express as px
from openai import OpenAI
import datetime
from PIL import Image

# --- 1. 空间基础配置 ---
st.set_page_config(page_title="2026东京之约-专属空间", layout="wide")

# 初始化数据
if 'daily_logs' not in st.session_state:
    st.session_state.daily_logs = pd.DataFrame(columns=["日期", "项目", "详情", "心情"])
if 'weight_history' not in st.session_state:
    st.session_state.weight_history = pd.DataFrame([{"日期": "2025-01-01", "体重": 65.0}])

# --- 2. 侧边栏：我们的画像与倒计时 ---
with st.sidebar:
    st.title("🗼 东京重逢计划")

    # 放置两人的相片 (请将图片文件名替换为你的本地路径)
    col_a, col_b = st.columns(2)
    with col_a:
        st.image("https://via.placeholder.com/150?text=His+Photo", caption="你")
    with col_b:
        st.image("https://via.placeholder.com/150?text=Her+Photo", caption="她")

    # 倒计时逻辑
    target_date = datetime.date(2026, 6, 23)
    today = datetime.date.today()
    days_left = (target_date - today).days
    st.metric("距离东京重逢还有", f"{days_left} 天")

    st.divider()
    api_key = st.text_input("🔑 激活 AI 守护 (API Key)", type="password")

    # 减脂进度雷达
    st.subheader("📊 减脂与互动看板")
    # 这里的指标可以根据每天存储的事情自动计算
    radar_df = pd.DataFrame({
        "项目": ["运动频率", "饮食控制", "沟通时长", "心情指数", "东京期待值"],
        "分值": [70, 60, 95, 80, 100]
    })
    fig_radar = px.line_polar(radar_df, r='分值', theta='项目', line_close=True, range_r=[0, 100])
    st.plotly_chart(fig_radar, use_container_width=True)


# --- 3. AI 调用：暖心陪练模式 ---
def ask_ai_coach(prompt):
    if not api_key: return "请先在侧边栏输入 Key 激活 AI 老师"
    try:
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        sys_role = f"你是一个既温柔又专业的异地恋陪跑AI。由于你的女主人要在2026年6月23日去东京见男主人，她现在的体重是{st.session_state.weight_history.iloc[-1]['体重']}kg，目标是55kg。请根据她输入的内容给出鼓励和建议。"
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "system", "content": sys_role}, {"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI 正在休息: {str(e)}"


# --- 4. 主界面：记录与统计 ---
st.title("💑 我们的小空间：从 2025/1/1 到 东京铁塔")

tab1, tab2, tab3 = st.tabs(["📅 每日生活记录", "📈 减脂统计表", "🗼 东京攻略"])

with tab1:
    col_l, col_r = st.columns([2, 1])
    with col_l:
        st.subheader("✍️ 记录我们的一天")
        with st.form("daily_form", clear_on_submit=True):
            item = st.selectbox("类型", ["运动", "饮食", "心情", "异地日常"])
            detail = st.text_area("发生了什么？(比如吃了什么，走了多少步)")
            mood = st.select_slider("今日心情", options=["😢", "😟", "😐", "😊", "🥰"])
            submitted = st.form_submit_button("存入时光机")
            if submitted:
                new_data = pd.DataFrame([{"日期": today, "项目": item, "详情": detail, "心情": mood}])
                st.session_state.daily_logs = pd.concat([st.session_state.daily_logs, new_data], ignore_index=True)
                st.balloons()

        st.subheader("📜 历史存根")
        st.dataframe(st.session_state.daily_logs, use_container_width=True)

    with col_r:
        st.subheader("💡 AI 老师的私教建议")
        if not st.session_state.daily_logs.empty:
            last_event = st.session_state.daily_logs.iloc[-1]['详情']
            if st.button("获取今日建议"):
                feedback = ask_ai_coach(f"这是她今天的记录：{last_event}。请点评并给于减肥建议。")
                st.info(feedback)

with tab2:
    st.subheader("📉 体重变化曲线")
    new_w = st.number_input("今日更新体重 (kg)", value=65.0, step=0.1)
    if st.button("记录体重"):
        new_weight_data = pd.DataFrame([{"日期": str(today), "体重": new_w}])
        st.session_state.weight_history = pd.concat([st.session_state.weight_history, new_weight_data],
                                                    ignore_index=True)

    fig_weight = px.line(st.session_state.weight_history, x="日期", y="体重", title="迈向 55kg 目标线", markers=True)
    fig_weight.add_hline(y=55.0, line_dash="dot", annotation_text="目标 55kg", line_color="green")
    st.plotly_chart(fig_weight, use_container_width=True)

    st.subheader("📊 数据统计表")
    st.table(st.session_state.weight_history)

with tab3:
    st.subheader("🗼 我们的东京约定清单")
    st.markdown("""
    - [ ] 在东京铁塔下拍一张合照
    - [ ] 穿上 55kg 时买的那件裙子
    - [ ] 吃一次并不增肥的顶级刺身大餐
    """)
    st.image(
        "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?ixlib=rb-4.0.3&auto=format&fit=crop&w=1194&q=80",
        caption="期待我们的重逢")