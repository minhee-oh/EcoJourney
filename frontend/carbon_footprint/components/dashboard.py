"""
대시보드 시각화 컴포넌트
"""

import reflex as rx
from typing import List, Dict
from datetime import datetime


def render_category_chart(category_breakdown: Dict[str, float]) -> rx.Component:
    """
    카테고리별 탄소 배출량 표시
    
    Args:
        category_breakdown: 카테고리별 배출량 딕셔너리
    """
    if not category_breakdown:
        return rx.callout(
            "아직 데이터가 없어요. 활동을 입력해보세요!",
            icon="info",
            color_scheme="blue"
        )
    
    return rx.vstack(
        rx.heading("카테고리별 탄소 배출 비중", size="5"),
        rx.vstack(
            rx.foreach(
                list(category_breakdown.items()),
                lambda item: rx.hstack(
                    rx.text(item[0], flex="1"),
                    rx.progress(
                        value=item[1],
                        max=100,  # 최대값을 고정값으로 설정 (동적 계산 대신)
                        width="50%"
                    ),
                    rx.text(f"{item[1]:.2f} kgCO₂e", width="150px", text_align="right"),
                    spacing="2",
                    width="100%"
                )
            ),
            spacing="3",
            width="100%"
        ),
        spacing="4",
        width="100%"
    )


def render_activity_timeline(activities: List[Dict]) -> rx.Component:
    """
    활동 타임라인 표시
    
    Args:
        activities: 활동 내역 리스트
    """
    if not activities:
        return rx.box()
    
    # 활동을 시간순으로 정렬
    sorted_activities = sorted(
        activities,
        key=lambda x: x.get('timestamp', datetime.now()),
        reverse=True
    )
    
    # 최근 10개만 표시
    return rx.vstack(
        rx.heading("📊 오늘의 활동 내역", size="5"),
        rx.vstack(
            rx.foreach(
                sorted_activities[:10],
                render_activity_item
            ),
            spacing="2",
            width="100%"
        ),
        spacing="4",
        width="100%"
    )


def render_activity_item(act: Dict) -> rx.Component:
    """활동 항목"""
    category = act.get('category', '')
    activity_type = act.get('activity_type', '')
    carbon = act.get('carbon_emission_kg', 0)
    value = act.get('value', 0)
    unit = act.get('unit', '')
    
    return rx.card(
        rx.hstack(
            rx.vstack(
                rx.text(f"**{category}** > {activity_type}", align="start"),
                rx.text(f"{value} {unit}", size="2", color="gray", align="start"),
                spacing="1",
                align="start",
                flex="2"
            ),
            rx.spacer(),
            rx.stat(
                rx.stat_number(f"{carbon:.3f} kgCO₂e"),
                rx.stat_label("탄소"),
            ),
            spacing="4",
            width="100%"
        ),
        width="100%",
        padding="1rem"
    )


def render_summary_cards(total_carbon: float, category_breakdown: Dict[str, float]) -> rx.Component:
    """
    요약 카드 표시
    
    Args:
        total_carbon: 총 탄소 배출량
        category_breakdown: 카테고리별 배출량
    """
    max_category = max(category_breakdown.items(), key=lambda x: x[1])[0] if category_breakdown else "없음"
    activity_count = len(category_breakdown)
    
    return rx.hstack(
        rx.stat(
            rx.stat_number(f"{total_carbon:.2f} kgCO₂e"),
            rx.stat_label("오늘 총 배출량"),
            rx.stat_help_text("목표: 10.0 kgCO₂e"),
        ),
        rx.stat(
            rx.stat_number(max_category),
            rx.stat_label("최대 배출 카테고리"),
        ),
        rx.stat(
            rx.stat_number(f"{activity_count}개"),
            rx.stat_label("활동 카테고리 수"),
        ),
        spacing="4",
        width="100%",
        justify="between"
    )

