"""
지구 아바타 시각화 컴포넌트
"""

import reflex as rx
from typing import Dict


def render_avatar(avatar_state: Dict) -> rx.Component:
    """
    지구 아바타를 시각적으로 표시
    
    Args:
        avatar_state: 아바타 상태 딕셔너리
    """
    health_score = avatar_state.get("health_score", 50)
    mood = avatar_state.get("mood", "neutral")
    message = avatar_state.get("message", "")
    emoji = avatar_state.get("visual_emoji", "🌍")
    
    # 기분에 따른 색상
    mood_colors = {
        "happy": "green",
        "neutral": "blue",
        "sad": "orange",
        "critical": "red"
    }
    
    mood_messages = {
        "happy": "✨ 지구가 행복해하고 있어요!",
        "neutral": "🌍 지구가 괜찮아 보여요",
        "sad": "😔 지구가 조금 힘들어하고 있어요",
        "critical": "🚨 지구가 위험해요! 지금 바로 행동이 필요해요!"
    }
    
    return rx.vstack(
        rx.heading("🌍 나의 지구", size="5"),
        rx.vstack(
            rx.text(
                emoji,
                font_size="5rem",
                text_align="center"
            ),
            rx.progress(
                value=health_score,
                max=100,
                width="100%",
                margin_top="1rem"
            ),
            rx.text(
                f"건강 점수: {health_score}/100",
                text_align="center",
                font_weight="bold",
                margin_top="0.5rem"
            ),
            rx.callout(
                f"💬 {message}",
                icon="💬",
                color_scheme="blue",
                margin_top="1rem"
            ),
            rx.callout(
                mood_messages.get(mood, "🌍 지구 상태 확인 중..."),
                icon="🌍",
                color_scheme=mood_colors.get(mood, "blue"),
                margin_top="0.5rem"
            ),
            spacing="3",
            align="center",
            width="100%"
        ),
        spacing="4",
        width="100%",
        padding="2rem"
    )




