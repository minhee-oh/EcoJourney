"""
지구 아바타 시각화 컴포넌트
"""

import streamlit as st
from typing import Dict

def render_avatar(avatar_state: Dict):
    """
    지구 아바타를 시각적으로 표시
    
    Args:
        avatar_state: 아바타 상태 딕셔너리
    """
    health_score = avatar_state.get("health_score", 50)
    mood = avatar_state.get("mood", "neutral")
    message = avatar_state.get("message", "")
    emoji = avatar_state.get("visual_emoji", "🌍")
    
    # 아바타 컨테이너
    st.markdown("### 🌍 나의 지구")
    
    # 큰 이모지로 아바타 표시
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"<div style='text-align: center; font-size: 80px;'>{emoji}</div>", 
                   unsafe_allow_html=True)
        
        # 건강 점수 프로그레스 바
        st.progress(health_score / 100)
        st.markdown(f"<div style='text-align: center;'><b>건강 점수: {health_score}/100</b></div>", 
                   unsafe_allow_html=True)
        
        # 상태 메시지
        st.info(f"💬 {message}")
    
    # 기분에 따른 색상 테마
    if mood == "happy":
        st.success("✨ 지구가 행복해하고 있어요!")
    elif mood == "neutral":
        st.info("🌍 지구가 괜찮아 보여요")
    elif mood == "sad":
        st.warning("😔 지구가 조금 힘들어하고 있어요")
    elif mood == "critical":
        st.error("🚨 지구가 위험해요! 지금 바로 행동이 필요해요!")





