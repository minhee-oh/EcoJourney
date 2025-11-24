"""
배지 시스템 컴포넌트
"""

import reflex as rx
from typing import List, Dict


def render_badges(badges: List[Dict]) -> rx.Component:
    """
    배지 목록을 시각적으로 표시
    
    Args:
        badges: 배지 딕셔너리 리스트
    """
    if not badges:
        return rx.callout(
            "아직 획득한 배지가 없어요. 활동을 시작해보세요! 🏆",
            icon="info",
            color_scheme="blue"
        )
    
    return rx.vstack(
        rx.heading("🏆 획득한 배지", size="5"),
        rx.responsive_grid(
            rx.foreach(
                badges,
                render_badge_card
            ),
            columns=[1, 2, 3],
            spacing="3",
            width="100%"
        ),
        spacing="4",
        width="100%"
    )


def render_badge_card(badge: Dict) -> rx.Component:
    """배지 카드"""
    return rx.card(
        rx.vstack(
            rx.text(
                badge.get('icon', '🏆'),
                font_size="3rem",
                text_align="center"
            ),
            rx.heading(
                badge.get('name', '배지'),
                size="4",
                text_align="center"
            ),
            rx.text(
                badge.get('description', ''),
                size="2",
                text_align="center",
                color="gray"
            ),
            spacing="2",
            align="center",
            width="100%"
        ),
        width="100%",
        padding="1.5rem",
        background="linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        color="white",
        border_radius="10px"
    )

