"""
배지 시스템 컴포넌트
"""

import streamlit as st
from typing import List, Dict

def render_badges(badges: List[Dict]):
    """
    배지 목록을 시각적으로 표시
    
    Args:
        badges: 배지 딕셔너리 리스트
    """
    if not badges:
        st.info("아직 획득한 배지가 없어요. 활동을 시작해보세요! 🏆")
        return
    
    st.markdown("### 🏆 획득한 배지")
    
    # 배지를 그리드 형태로 표시
    cols = st.columns(min(len(badges), 3))
    
    for idx, badge in enumerate(badges):
        with cols[idx % len(cols)]:
            # 배지 카드
            st.markdown(f"""
            <div style='
                border: 2px solid #4CAF50;
                border-radius: 10px;
                padding: 20px;
                text-align: center;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                margin: 10px 0;
            '>
                <div style='font-size: 50px;'>{badge.get('icon', '🏆')}</div>
                <div style='font-size: 18px; font-weight: bold; margin-top: 10px;'>
                    {badge.get('name', '배지')}
                </div>
                <div style='font-size: 12px; margin-top: 5px; opacity: 0.9;'>
                    {badge.get('description', '')}
                </div>
            </div>
            """, unsafe_allow_html=True)





