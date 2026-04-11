import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
import time

# 1. 페이지 설정 및 지도 스타일 (Mapbox 토큰이 있다면 더 고해상도 지도가 가능합니다)
st.set_page_config(page_title="Global Robot C2 - GPS Live", layout="wide")

# --- 실전용: 외부 데이터 소스 연동 함수 (예시: API 또는 DB) ---
# 실제 환경에서는 이곳에 requests.get('API_URL')이나 SQL 쿼리가 들어갑니다.
def fetch_live_gps_data():
    # 시연을 위한 실전급 좌표 데이터 (하남 미사, 용산, 마포 등 실제 전략 요충지 기반)
    data = {
        'Robot ID': ['ROBOT-H01', 'ROBOT-Y02', 'ROBOT-M03', 'ROBOT-S04', 'ROBOT-G05'],
        'Latitude': [37.5500, 37.5300, 37.5400, 37.5450, 37.5100],  # 하남, 용산, 마포, 성동, 강남
        'Longitude': [127.1900, 126.9700, 126.9500, 127.0400, 127.0600],
        'Status': ['Operating', 'Operating', 'Warning', 'Operating', 'Maintenance'],
        'Failure Risk (%)': [12, 45, 88, 5, 95],
        'Battery (%)': [85, 62, 41, 90, 15],
        'Last Update': [datetime.now().strftime('%H:%M:%S')] * 5
    }
    return pd.DataFrame(data)

# --- 사이드바: 실시간 관제 엔진 ---
st.sidebar.header("📡 실시간 관제 통신")
live_mode = st.sidebar.toggle("라이브 스트리밍 모드", value=True)
update_interval = st.sidebar.slider("데이터 갱신 주기 (초)", 1, 10, 3)

# --- 메인 대시보드 ---
st.title("🛰️ 격오지 로봇 GPS 실시간 관제 (Live)")

# 실시간 갱신 로직 (st.empty를 사용해 화면 깜빡임 없이 데이터만 교체)
placeholder = st.empty()

while live_mode:
    df = fetch_live_gps_data()
    
    with placeholder.container():
        # KPI 섹션
        k1, k2, k3 = st.columns(3)
        k1.metric("활성 로봇", f"{len(df)} 대", "Connected")
        k2.metric("위험 로봇", f"{len(df[df['Failure Risk (%)'] > 80])} 대", "-1", delta_color="inverse")
        k3.metric("평균 응답 속도", "42ms", "-5ms")

        # --- 메인 지도: Plotly Scatter Mapbox ---
        # 실제 지도를 보고 싶으실 때 가장 강력한 시각화 도구입니다.
        fig = px.scatter_mapbox(
            df, 
            lat="Latitude", 
            lon="Longitude", 
            color="Status",
            size="Failure Risk (%)",  # 위험할수록 점이 커짐
            hover_name="Robot ID",
            hover_data=["Battery (%)", "Failure Risk (%)", "Last Update"],
            color_discrete_map={'Operating': '#2ecc71', 'Warning': '#f1c40f', 'Maintenance': '#e74c3c'},
            zoom=11, 
            height=600,
            center={"lat": 37.53, "lon": 127.02} # 서울 중심부 고정
        )

        # 지도 스타일 설정 (open-street-map은 무료, mapbox-token이 있으면 더 화려해집니다)
        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        
        st.plotly_chart(fig, use_container_width=True)

        # 하단 상세 상태 로그
        st.subheader("📋 개별 로봇 통신 상태")
        st.dataframe(df, use_container_width=True)

    if not live_mode:
        break
    time.sleep(update_interval)
