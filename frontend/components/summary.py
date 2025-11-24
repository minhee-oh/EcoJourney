"""
요약 및 분석 결과 컴포넌트
"""

import streamlit as st
import plotly.graph_objects as go
from typing import Dict, List

def render_summary_page(
    total_carbon: float,
    category_breakdown: Dict[str, float],
    average_comparison: Dict,
    category_comparisons: List[Dict],
    badges: List[Dict],
    ai_analysis: Dict = None
):
    """
    요약 페이지 렌더링
    
    Args:
        total_carbon: 총 탄소 배출량
        category_breakdown: 카테고리별 배출량
        average_comparison: 전체 평균 비교 결과
        category_comparisons: 카테고리별 평균 비교 결과
        badges: 획득한 배지
        ai_analysis: AI 분석 결과
    """
    st.header("📊 오늘의 탄소 발자국 요약")
    st.markdown("---")
    
    # 전체 요약 카드
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "오늘 총 배출량",
            f"{total_carbon:.2f} kgCO₂e"
        )
    
    with col2:
        avg = average_comparison.get("average_emission", 0)
        diff = average_comparison.get("difference", 0)
        st.metric(
            "한국인 평균",
            f"{avg:.2f} kgCO₂e",
            delta=f"{diff:+.2f} kgCO₂e" if diff != 0 else "평균과 동일"
        )
    
    with col3:
        percentage = average_comparison.get("percentage", 0)
        is_better = average_comparison.get("is_better", False)
        st.metric(
            "평균 대비",
            f"{abs(percentage):.1f}%",
            delta="절약" if is_better else "초과"
        )
    
    with col4:
        badge_count = len(badges)
        st.metric(
            "획득 배지",
            f"{badge_count}개"
        )
    
    st.markdown("---")
    
    # 평균 비교 차트
    st.subheader("📈 평균과의 비교")
    
    categories = list(category_breakdown.keys())
    user_values = [category_breakdown[cat] for cat in categories]
    avg_values = [comp.get("average_emission", 0) for comp in category_comparisons]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='나의 배출량',
        x=categories,
        y=user_values,
        marker_color='#ff6b6b'
    ))
    
    fig.add_trace(go.Bar(
        name='한국인 평균',
        x=categories,
        y=avg_values,
        marker_color='#4ecdc4'
    ))
    
    fig.update_layout(
        title='카테고리별 배출량 비교',
        xaxis_title='카테고리',
        yaxis_title='탄소 배출량 (kgCO₂e)',
        barmode='group',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    # 카테고리별 상세 비교
    st.subheader("📋 카테고리별 상세 비교")
    
    for i, (cat, comp) in enumerate(zip(categories, category_comparisons)):
        with st.expander(f"{cat} - {comp.get('user_emission', 0):.2f} kgCO₂e"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**나의 배출량**: {comp.get('user_emission', 0):.2f} kgCO₂e")
                st.write(f"**평균 배출량**: {comp.get('average_emission', 0):.2f} kgCO₂e")
            
            with col2:
                diff = comp.get('difference', 0)
                pct = comp.get('percentage', 0)
                is_better = comp.get('is_better', False)
                
                if is_better:
                    st.success(f"✅ 평균보다 {abs(diff):.2f} kgCO₂e 적어요! ({abs(pct):.1f}% 절약)")
                else:
                    st.warning(f"⚠️ 평균보다 {diff:.2f} kgCO₂e 많아요 ({pct:.1f}% 초과)")
    
    st.markdown("---")
    
    # 배지 섹션
    if badges:
        st.subheader("🏆 획득한 배지")
        cols = st.columns(min(len(badges), 4))
        for idx, badge in enumerate(badges):
            with cols[idx % len(cols)]:
                st.markdown(f"""
                <div style='
                    border: 2px solid #4CAF50;
                    border-radius: 10px;
                    padding: 15px;
                    text-align: center;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    margin: 5px 0;
                '>
                    <div style='font-size: 40px;'>{badge.get('icon', '🏆')}</div>
                    <div style='font-size: 16px; font-weight: bold; margin-top: 5px;'>
                        {badge.get('name', '배지')}
                    </div>
                    <div style='font-size: 11px; margin-top: 3px; opacity: 0.9;'>
                        {badge.get('description', '')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # AI 분석 섹션
    if ai_analysis:
        st.subheader("🤖 AI 분석 결과")
        
        st.markdown("### 📊 분석")
        st.info(ai_analysis.get("analysis", ""))
        
        st.markdown("### 💡 탄소 저감 제안")
        suggestions = ai_analysis.get("suggestions", [])
        for idx, suggestion in enumerate(suggestions, 1):
            st.markdown(f"{idx}. {suggestion}")
        
        st.markdown("### 🌱 대안 행동")
        alternatives = ai_analysis.get("alternative_actions", [])
        if alternatives:
            for alt in alternatives:
                st.markdown(f"""
                - **현재**: {alt.get('current', '')}  
                  **대안**: {alt.get('alternative', '')}  
                  **효과**: {alt.get('impact', '')}
                """)
        
        st.markdown("### 💬 격려 메시지")
        st.success(ai_analysis.get("emotional_message", ""))





