import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
import io

# 1. 페이지 설정
st.set_page_config(page_title="Global Robot C2 Center", layout="wide")

# --- 데이터 생성 및 전처리 함수 ---
@st.cache_data
def get_robot_data():
    np.random.seed(42)
    df = pd.DataFrame({
        'Robot ID': [f"ROBOT-{i:03d}" for i in range(1, 101)],
        'Status': np.random.choice(['Operating', 'Idle', 'Maintenance'], size=100),
        'Battery (%)': np.random.randint(20, 100, size=100),
        'Vibration (mm)': np.random.uniform(0.1, 0.5, size=100),
        'Failure Risk (%)': np.random.uniform(0, 100, size=100)
    })
    return df

# --- 사이드바 설정 ---
st.sidebar.header("🕹️ 관제 설정")

# [강화된 기능] 샘플 파일 다운로드 (시연 준비용)
sample_df = get_robot_data().head(5)
csv_sample = sample_df.to_csv(index=False).encode('utf-8-sig')
st.sidebar.download_button("📥 시연용 샘플 양식 다운로드", data=csv_sample, file_name="robot_sample.csv", mime="text/csv")

uploaded_file = st.sidebar.file_uploader("📂 시연용 CSV 업로드", type=["csv"])
target_risk = st.sidebar.slider("AI 예지보전 타겟 리스크 (%)", 0, 100, 80)

# --- 데이터 로드 및 검증 ---
if uploaded_file is not None:
    try:
        raw_df = pd.read_csv(uploaded_file)
        # 컬럼 이름의 공백 제거 및 대소문자 통일 (에러 방지)
        raw_df.columns = raw_df.columns.str.strip()
       
        # 필수 컬럼 존재 확인
        required_cols = ['Robot ID', 'Status', 'Battery (%)', 'Vibration (mm)', 'Failure Risk (%)']
        if all(col in raw_df.columns for col in required_cols):
            df = raw_df
            st.sidebar.success("✅ 커스텀 데이터 적용 완료!")
        else:
            missing = [c for c in required_cols if c not in raw_df.columns]
            st.sidebar.error(f"❌ 필수 컬럼 누락: {missing}")
            df = get_robot_data()
    except Exception as e:
        st.sidebar.error(f"❌ 파일 읽기 오류: {e}")
        df = get_robot_data()
else:
    df = get_robot_data()

# --- 메인 UI 시작 ---
st.title("🌐 격오지 AI 로봇 통합 관제 시스템 (v2.1)")
st.info(f"운영자: MisaTech | 현재 상태: {'실제 데이터 분석 중' if uploaded_file else '가상 데모 모드'}")

# KPI 섹션
st.divider()
k1, k2, k3, k4 = st.columns(4)

# 에러 방지를 위한 데이터 가공
danger_mask = df['Failure Risk (%)'] > target_risk
danger_count = danger_mask.sum()

with k1:
    acc = (df['Status'] == 'Operating').sum() / len(df) * 100
    st.metric("📊 가동률", f"{acc:.1f}%")
with k2:
    st.metric("💰 절감 기대액", f"₩{(danger_count * 1250000):,}")
with k3:
    st.metric("🛠️ 긴급 점검", f"{danger_count} 대")
with k4:
    st.metric("🔋 평균 배터리", f"{int(df['Battery (%)'].mean())}%")

# 시각화 섹션
st.divider()
c1, c2 = st.columns([2, 1])

with c1:
    st.subheader("📍 로봇 군집 리스크 맵")
    fig = px.scatter(df, x='Vibration (mm)', y='Failure Risk (%)', color='Status', size='Battery (%)',
                     hover_name='Robot ID', color_discrete_map={'Operating': '#2ecc71', 'Idle': '#f1c40f', 'Maintenance': '#e74c3c'})
    fig.add_hline(y=target_risk, line_dash="dot", line_color="red", annotation_text="Risk Limit")
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("🚨 AI 실시간 브리핑")
    danger_robots = df[danger_mask].sort_values('Failure Risk (%)', ascending=False)
    if not danger_robots.empty:
        for _, row in danger_robots.head(5).iterrows():
            st.warning(f"**{row['Robot ID']}** ({row['Failure Risk (%)']:.1f}%)")
    else:
        st.success("이상 징후 없음")

# 전체 데이터
with st.expander("📝 상세 데이터 보기"):
    st.dataframe(df, use_container_width=True)
