import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

# 1. 페이지 레이아웃 설정
st.set_page_config(page_title="Global Robot C2 Center", layout="wide", initial_sidebar_state="expanded")

# --- 가상 데이터 생성 엔진 (형님의 데모를 풍성하게 해줄 요소) ---
@st.cache_data
def get_robot_data():
    np.random.seed(42)
    robot_ids = [f"ROBOT-{i:03d}" for i in range(1, 101)]
    status = np.random.choice(['Operating', 'Idle', 'Maintenance'], size=100, p=[0.85, 0.1, 0.05])
    battery = np.random.randint(20, 100, size=100)
    vibration = np.random.uniform(0.1, 0.5, size=100)
    # AI가 예측한 고장 확률 (80% 이상이면 위험)
    failure_risk = np.random.uniform(0, 100, size=100)
    
    df = pd.DataFrame({
        'Robot ID': robot_ids,
        'Status': status,
        'Battery (%)': battery,
        'Vibration (mm)': vibration,
        'Failure Risk (%)': failure_risk
    })
    return df

df = get_robot_data()

# --- 사이드바: 관제 설정 ---
st.sidebar.header("🕹️ 관제 설정")
target_risk = st.sidebar.slider("AI 예지보전 타겟 리스크 (%)", 0, 100, 80)
refresh_btn = st.sidebar.button("전체 로봇 상태 스캔")

# --- 메인 대시보드 시작 ---
st.title("🌐 격오지 AI 로봇 통합 관제 시스템 (v2.0)")
st.markdown(f"**현재 관제 시각:** `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}` | **운영자:** `형님(Hyung-nim)`")

# --- 핵심 KPI 섹션 (형님이 강조하신 포인트!) ---
st.divider()
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    availability = (df['Status'] == 'Operating').sum()
    st.metric("📊 전체 가동률", f"{availability}%", delta="1.2%", help="현재 가동 중인 로봇의 비율")

with kpi2:
    # 예지 보전을 통해 방어한 다운타임 비용 계산 (가상 시나리오)
    saved_cost = (df['Failure Risk (%)'] > target_risk).sum() * 1250000 # 건당 125만원 절감 가정
    st.metric("💰 예지보전 절감액", f"₩{saved_cost:,}", delta="₩5,400,000", delta_color="normal")

with kpi3:
    st.metric("🛠️ 긴급 점검 대상", f"{(df['Failure Risk (%)'] > target_risk).sum()} 대", delta="신규 1대", delta_color="inverse")

with kpi4:
    st.metric("🔋 평균 배터리 잔량", f"{int(df['Battery (%)'].mean())}%", delta="-0.5%")

st.divider()

# --- 하단 상세 분석 구역 ---
col_map, col_log = st.columns([2, 1])

with col_map:
    st.subheader("📍 로봇 군집 리스크 맵")
    # 산점도로 로봇 상태 시각화
    fig = px.scatter(df, x='Vibration (mm)', y='Failure Risk (%)', 
                     color='Status', size='Battery (%)', hover_name='Robot ID',
                     color_discrete_map={'Operating': '#2ecc71', 'Idle': '#f1c40f', 'Maintenance': '#e74c3c'})
    # 위험선 표시
    fig.add_hline(y=target_risk, line_dash="dot", annotation_text="AI Critical Risk Line", line_color="red")
    st.plotly_chart(fig, use_container_width=True)

with col_log:
    st.subheader("🚨 AI 에이전트 브리핑")
    danger_robots = df[df['Failure Risk (%)'] > target_risk]
    
    if not danger_robots.empty:
        for _, row in danger_robots.iterrows():
            st.error(f"**[{row['Robot ID']}]** 위험 감지\n\n진동 수치: {row['Vibration (mm)']:.2f}mm\n\n**AI 진단:** 베어링 마모 임계치 도달. {np.random.randint(1, 5)}시간 내 현장 조치 권고.")
    else:
        st.success("✅ 모든 로봇이 정상 범위 내에서 작동 중입니다.")

# --- 데이터 테이블 구역 ---
with st.expander("📝 전체 로봇 상세 제원 보기"):
    st.dataframe(df.style.highlight_max(axis=0, subset=['Failure Risk (%)'], color='#ff9999'), use_container_width=True)