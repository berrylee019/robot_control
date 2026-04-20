import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta
import time
import streamlit_analytics2 as streamlit_analytics

# ... 하단 코드는 그대로 사용하셔도 됩니다 ...
with streamlit_analytics.track():
    st.title("🛰️ 로봇 통합 관제 및 자동 충전 시스템")

# 1. 페이지 설정
st.set_page_config(page_title="Global Robot C2 - Full Ops", layout="wide")

# --- 데이터 엔진 ---
def fetch_integrated_data():
    data = {
        'Robot ID': ['ROBOT-H01', 'ROBOT-Y02', 'T-RAX-01', 'ROBOT-S04', 'ROBOT-G05'],
        'Latitude': [37.5500, 37.5300, 37.5400, 37.5450, 37.5100],
        'Longitude': [127.1900, 126.9700, 126.9500, 127.0400, 127.0600],
        'Status': ['Operating', 'Operating', 'Charging', 'Operating', 'Low Battery'],
        'Failure Risk (%)': [12, 45, 8, 5, 95],
        'Battery (%)': [85, 62, 15, 90, 12],
        'Last Update': [datetime.now().strftime('%H:%M:%S')] * 5
    }
    return pd.DataFrame(data)

def generate_charging_schedule(df):
    schedule = []
    low_battery_robots = df[(df['Battery (%)'] < 30) | (df['Status'] == 'Low Battery')]
    stations = ['강남-Station A', '마포-Station B', '용산-Station C']
    for i, (idx, row) in enumerate(low_battery_robots.iterrows()):
        start_time = datetime.now() + timedelta(minutes=15 * (i + 1))
        schedule.append({
            'ID': row['Robot ID'],
            '배터리': f"{row['Battery (%)']}%",
            '지정 충전소': stations[i % len(stations)],
            '예약 시각': start_time.strftime('%H:%M'),
            '예상 소요': "45분",
            '우선순위': "긴급" if row['Battery (%)'] < 15 else "보통"
        })
    return pd.DataFrame(schedule)

# --- 사이드바 ---
st.sidebar.header("📡 시스템 통합 관제")
live_mode = st.sidebar.toggle("라이브 스트리밍", value=True)
auto_charge = st.sidebar.checkbox("AI 자동 충전 스케줄링 활성화", value=True)
update_interval = st.sidebar.slider("새로고침 주기 (초)", 1, 10, 5)

# --- 메인 타이틀 (루프 밖) ---
st.title("🛰️ Mobility 통합 관제 및 자동 충전 시스템")

# 실시간 갱신을 위한 메인 컨테이너
main_container = st.empty()

# 고유 ID 생성을 위한 카운터
if 'count' not in st.session_state:
    st.session_state.count = 0

while live_mode:
    df = fetch_integrated_data()
    st.session_state.count += 1
    
    with main_container.container():
        st.markdown(f"**운영자:** `MisaTech` | **통신 상태:** `Online` | **업데이트 시각:** `{datetime.now().strftime('%H:%M:%S')}`")
        
        # 1. KPI
        k1, k2, k3, k4 = st.columns(4)
        danger_count = (df['Battery (%)'] < 30).sum()
        risk_count = (df['Failure Risk (%)'] > 80).sum()
        
        k1.metric("전체 함대", f"{len(df)}대", "Stable")
        k2.metric("긴급 충전 필요", f"{danger_count}대", "-1", delta_color="inverse")
        k3.metric("예지보전 대상", f"{risk_count}대", "High Risk")
        k4.metric("시스템 효율", "94%", "+2%")

        # 2. 지도 (중복 방지를 위해 key값 부여)
        st.subheader(" Mobilty 실시간 위치 및 상태")
        fig = px.scatter_mapbox(
            df, lat="Latitude", lon="Longitude", color="Status", size="Failure Risk (%)",
            hover_name="Robot ID", zoom=11, height=500,
            color_discrete_map={'Operating': '#2ecc71', 'Warning': '#f1c40f', 'Maintenance': '#e74c3c', 'Charging': '#3498db', 'Low Battery': '#e67e22'}
        )
        fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
        # key 파라미터가 중복 에러를 해결하는 핵심입니다.
        st.plotly_chart(fig, use_container_width=True, key=f"map_{st.session_state.count}")

        # 3. 하단 섹션
        st.divider()
        col_sch, col_log = st.columns([2, 1])
        
        with col_sch:
            st.subheader("🔋 AI 자동 충전 예약 현황")
            if auto_charge:
                sched_df = generate_charging_schedule(df)
                if not sched_df.empty:
                    st.table(sched_df)
                else:
                    st.success("모든 로봇 배터리 양호")
        
        with col_log:
            st.subheader("🚨 시스템 로그")
            danger_logs = df[df['Failure Risk (%)'] > 70]
            if not danger_logs.empty:
                for _, row in danger_logs.iterrows():
                    st.error(f"**{row['Robot ID']}**: {row['Status']}")
            else:
                st.write("로그 없음")

    if not live_mode:
        break
    time.sleep(update_interval)
