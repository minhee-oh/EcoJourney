"""
대시보드 시각화 컴포넌트
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import List, Dict
from datetime import datetime

def render_category_chart(category_breakdown: Dict[str, float]):
    """
    카테고리별 탄소 배출량 파이 차트
    
    Args:
        category_breakdown: 카테고리별 배출량 딕셔너리
    """
    if not category_breakdown:
        st.info("아직 데이터가 없어요. 활동을 입력해보세요!")
        return
    
    df = pd.DataFrame({
        '카테고리': list(category_breakdown.keys()),
        '탄소 배출량 (kgCO₂e)': list(category_breakdown.values())
    })
    
    fig = px.pie(
        df, 
        values='탄소 배출량 (kgCO₂e)', 
        names='카테고리',
        title='카테고리별 탄소 배출 비중',
        color_discrete_sequence=px.colors.sequential.Viridis
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        hovermode='closest',
        margin=dict(l=0, r=0, t=30, b=0)
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


def render_activity_timeline(activities: List[Dict]):
    """
    활동 타임라인 표시
    
    Args:
        activities: 활동 내역 리스트
    """
    if not activities:
        return
    
    st.markdown("### 📊 오늘의 활동 내역")
    
    # 활동을 시간순으로 정렬
    sorted_activities = sorted(
        activities, 
        key=lambda x: x.get('timestamp', datetime.now()),
        reverse=True
    )
    
    # 최근 10개만 표시
    for act in sorted_activities[:10]:
        category = act.get('category', '')
        activity_type = act.get('activity_type', '')
        carbon = act.get('carbon_emission_kg', 0)
        
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            st.write(f"**{category}** > {activity_type}")
        with col2:
            st.write(f"{act.get('value', 0)} {act.get('unit', '')}")
        with col3:
            st.metric("탄소", f"{carbon:.3f} kgCO₂e")


def render_daily_trend(daily_trend: List[Dict]):
    """
    일일 추이 라인 차트
    
    Args:
        daily_trend: 일일 추이 데이터 리스트
    """
    if not daily_trend or len(daily_trend) < 2:
        return
    
    df = pd.DataFrame(daily_trend)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['time'],
        y=df['carbon'],
        mode='lines+markers',
        name='탄소 배출량',
        line=dict(color='#ff6b6b', width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title='오늘의 탄소 배출 추이',
        xaxis_title='시간',
        yaxis_title='누적 탄소 배출량 (kgCO₂e)',
        hovermode='x unified',
        template='plotly_white',
        margin=dict(l=0, r=0, t=30, b=0)
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


def render_summary_cards(total_carbon: float, category_breakdown: Dict[str, float]):
    """
    요약 카드 표시
    
    Args:
        total_carbon: 총 탄소 배출량
        category_breakdown: 카테고리별 배출량
    """
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "오늘 총 배출량",
            f"{total_carbon:.2f} kgCO₂e",
            delta=f"목표: 10.0 kgCO₂e"
        )
    
    with col2:
        max_category = max(category_breakdown.items(), key=lambda x: x[1])[0] if category_breakdown else "없음"
        st.metric(
            "최대 배출 카테고리",
            max_category
        )
    
    with col3:
        activity_count = len(category_breakdown)
        st.metric(
            "활동 카테고리 수",
            f"{activity_count}개"
        )

