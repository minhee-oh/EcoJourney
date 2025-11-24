"""
요약 및 분석 결과 컴포넌트
"""

import reflex as rx
from typing import Dict, List, Any

def render_summary_page(
    total_carbon: rx.Var[float],
    category_breakdown: rx.Var[Dict],
    average_comparison: rx.Var[Dict],
    category_comparisons: rx.Var[List],
    badges: rx.Var[List],
    ai_analysis: rx.Var[Dict],
    ai_analysis_text: rx.Var[str] = None,
    ai_suggestions: rx.Var[List] = None,
    ai_alternatives: rx.Var[List] = None,
    ai_emotional_message: rx.Var[str] = None,
) -> rx.Component:
    """
    요약 페이지 렌더링
    """
    
    badge_count = badges.length()
    
    return rx.vstack(
        rx.center(
            rx.vstack(
                rx.heading(
                    "📊 분석 결과",
                    size="8",
                    color="#0f172a",
                    font_weight="bold",
                    text_align="center",
                    align="center"
                ),
                rx.text(
                    "오늘의 탄소 발자국을 확인하고 지구를 위한 실천을 시작해요",
                    size="4",
                    color="#4b5563",
                    margin_top="0.5rem",
                    text_align="center",
                    align="center"
                ),
                spacing="2",
                width="100%",
                padding="3rem 2rem",
                align="center"
            ),
            width="100%",
            margin_bottom="3rem"
        ),
        
        # 1. 전체 요약 섹션 (평균과의 차이 강조)
        rx.heading(
            "📈 요약",
            size="6",
            margin_top="1rem",
            margin_bottom="1.5rem",
            color="#1f2937",
            weight="bold",
            text_align="center",
            align="center",
            width="100%"
        ),
        rx.grid(
            render_stat_card(
                "오늘 총 배출량",
                f"{total_carbon} kgCO₂e",
                icon="leaf"
            ),
            render_stat_card(
                "한국인 평균",
                f"{average_comparison['average_emission']} kgCO₂e",
                sub_text=rx.cond(
                    average_comparison['is_better'],
                    f"✅ 평균보다 {average_comparison['difference']} kgCO₂e 적어요!",
                    f"⚠️ 평균보다 {average_comparison['difference']} kgCO₂e 많아요"
                ),
                sub_color=rx.cond(average_comparison['is_better'], "green", "red"),
                icon="users"
            ),
            render_stat_card(
                "평균 대비",
                f"{average_comparison['percentage']}%",
                sub_text=rx.cond(average_comparison['is_better'], "절약 중! 🌱", "초과 주의! ⚠️"),
                sub_color=rx.cond(average_comparison['is_better'], "green", "red"),
                icon="percent"
            ),
            render_stat_card(
                "획득 배지",
                f"{badge_count}개",
                icon="trophy"
            ),
            columns=rx.breakpoints(initial="1", sm="2", lg="4"),
            spacing="4",
            width="100%"
        ),
        
        rx.divider(margin_y="1rem"),
        
        # 2. 카테고리별 그래프
        rx.heading(
            "📊 카테고리별 배출량 비교 그래프",
            size="6",
            margin_top="2rem",
            margin_bottom="1.5rem",
            color="#1f2937",
            weight="bold",
            text_align="center",
            align="center",
            width="100%"
        ),
        render_category_comparison_chart(category_comparisons),
        
        rx.divider(margin_y="1rem"),
        
        # 3. 배지 섹션 (항상 표시 - 랭크 배지는 항상 있음)
        rx.vstack(
            rx.heading(
                "🏆 오늘의 배지",
                size="6",
                margin_top="2rem",
                margin_bottom="1.5rem",
                color="#1f2937",
                weight="bold",
                text_align="center",
                align="center",
                width="100%"
            ),
            rx.grid(
                rx.foreach(
                    badges.to(List[Dict]),
                    render_badge_card
                ),
                columns=rx.breakpoints(initial="2", md="3", lg="4"),
                spacing="3",
                width="100%"
            ),
            spacing="3",
            width="100%"
        ),
        
        rx.divider(margin_y="1rem"),
        
        # 4. AI 분석 섹션 (항상 렌더링, 내부에서 조건 처리)
        render_ai_analysis_section(
            ai_analysis=ai_analysis,
            ai_analysis_text=ai_analysis_text,
            ai_suggestions=ai_suggestions,
            ai_alternatives=ai_alternatives,
            ai_emotional_message=ai_emotional_message,
        ),
        
        spacing="4",
        width="100%",
        align="center"
    )

def render_category_comparison_chart(category_comparisons: rx.Var[List]) -> rx.Component:
    """카테고리별 비교 바 차트"""
    return rx.card(
        rx.vstack(
            rx.foreach(
                category_comparisons.to(List[Dict]),
                render_category_bar_chart_item
            ),
            spacing="4",
            width="100%"
        ),
        padding="2rem",
        width="100%",
        background="white",
        border_radius="0.75rem",
        box_shadow="0 1px 3px 0 rgba(0, 0, 0, 0.08), 0 1px 2px 0 rgba(0, 0, 0, 0.04)",
        border="1px solid",
        border_color="#e5e7eb"
    )

def render_category_bar_chart_item(comp: rx.Var[Dict]) -> rx.Component:
    """카테고리별 바 차트 항목"""
    # Var 타입을 dict로 변환하여 접근
    item = comp.to(dict)
    
    # Var 타입끼리 직접 연산이 불가능하므로, 충분히 큰 고정값을 max로 사용
    # 일반적으로 탄소 배출량은 0~50kg 범위이므로, 100을 max로 설정
    max_value = 100
    
    return rx.vstack(
        rx.hstack(
            rx.heading(
                item['category'],
                size="4",
                color="#1f2937",
                weight="bold"
            ),
            rx.spacer(),
            rx.cond(
                comp['is_better'],
                rx.badge(
                    rx.fragment("✅ ", comp['percentage'], "% 절약"),
                    color_scheme="green",
                    size="2"
                ),
                rx.badge(
                    rx.fragment("⚠️ ", comp['percentage'], "% 초과"),
                    color_scheme="orange",
                    size="2"
                )
            ),
            width="100%",
            align="center"
        ),
        rx.vstack(
            rx.hstack(
                rx.text("나의 배출량", size="2", color="#6b7280", width="120px", weight="medium"),
                rx.cond(
                    comp['is_better'],
                    rx.progress(
                        value=comp['user_emission'],
                        max=max_value,
                        width="100%",
                        color_scheme="green"
                    ),
                    rx.progress(
                        value=comp['user_emission'],
                        max=max_value,
                        width="100%",
                        color_scheme="orange"
                    )
                ),
                rx.text(
                    rx.fragment(comp['user_emission'], " kg"),
                    size="2",
                    weight="bold",
                    color="#1f2937",
                    width="100px",
                    text_align="right"
                ),
                spacing="2",
                width="100%",
                align="center"
            ),
            rx.hstack(
                rx.text("평균 배출량", size="2", color="#6b7280", width="120px", weight="medium"),
                rx.progress(
                    value=comp['average_emission'],
                    max=max_value,
                    width="100%",
                    color_scheme="blue"
                ),
                rx.text(
                    rx.fragment(comp['average_emission'], " kg"),
                    size="2",
                    weight="bold",
                    color="#1f2937",
                    width="100px",
                    text_align="right"
                ),
                spacing="2",
                width="100%",
                align="center"
            ),
            spacing="2",
            width="100%"
        ),
        spacing="3",
        width="100%",
        padding="2"
    )

def render_stat_card(label: str, value: str, sub_text: Any = None, sub_color: str = "gray", icon: str = "info") -> rx.Component:
    """통계 카드"""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.box(
                    rx.icon(icon, size=28, color="white"),
                    padding="0.75rem",
                    background="#22c55e",
                    border_radius="0.75rem",
                    box_shadow="0 2px 4px rgba(34, 197, 94, 0.3)"
                ),
                rx.text(label, size="3", weight="medium", color="gray"),
                justify="between",
                width="100%",
                align="center"
            ),
            rx.heading(
                value,
                size="8",
                margin_top="1rem",
                color="#1f2937",
                weight="bold"
            ),
            rx.cond(
                sub_text,
                rx.text(
                    sub_text,
                    size="3",
                    color=sub_color,
                    weight="medium",
                    margin_top="0.5rem"
                )
            ),
            spacing="2",
            align="start"
        ),
        padding="1.5rem",
        width="100%",
        background="white",
        border_radius="1rem",
        box_shadow="0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)",
        border="1px solid",
        border_color="#e5e7eb",
        _hover={
            "box_shadow": "0 4px 6px -1px rgba(34, 197, 94, 0.1), 0 2px 4px -1px rgba(34, 197, 94, 0.06)",
            "border_color": "#22c55e",
            "transform": "translateY(-2px)"
        }
    )

def render_category_comparison_row(comp: rx.Var[Dict]) -> rx.Component:
    """카테고리별 비교 카드 (행 단위)"""
    # [안전장치] 딕셔너리로 변환
    item = comp.to(dict)
    
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.heading(item['category'], size="4"), 
                rx.spacer(),
                rx.cond(
                    item['is_better'],
                    rx.badge(f"✅ {item['percentage']}% 절약", color_scheme="green", size="2"),
                    rx.badge(f"⚠️ {item['percentage']}% 초과", color_scheme="orange", size="2")
                ),
                width="100%",
                align="center"
            ),
            rx.hstack(
                rx.vstack(
                    rx.text("나의 배출량", size="1", color="gray"),
                    rx.text(f"{item['user_emission']} kg", weight="bold"),
                    spacing="1"
                ),
                rx.divider(orientation="vertical", height="20px"),
                rx.vstack(
                    rx.text("평균 배출량", size="1", color="gray"),
                    rx.text(f"{item['average_emission']} kg", weight="bold"),
                    spacing="1"
                ),
                spacing="4",
                align="center"
            ),
            spacing="3",
            width="100%"
        ),
        width="100%",
        padding="3"
    )

def render_badge_card(badge: rx.Var[Dict]) -> rx.Component:
    """배지 카드"""
    # [안전장치] 딕셔너리로 변환
    item = badge.to(dict)
    
    # 랭크 배지에 따라 색상 변경 (Var 타입이므로 rx.cond 사용)
    # badge_id를 Var 타입으로 접근
    badge_id_var = badge.to(Dict)["id"]
    
    # 랭크별 색상 결정을 rx.cond로 처리
    # rank_s
    is_rank_s = badge_id_var == "rank_s"
    # rank_a
    is_rank_a = badge_id_var == "rank_a"
    # rank_b
    is_rank_b = badge_id_var == "rank_b"
    # rank_c
    is_rank_c = badge_id_var == "rank_c"
    # rank_d
    is_rank_d = badge_id_var == "rank_d"
    # 랭크 배지인지 확인
    is_rank_badge = rx.cond(
        is_rank_s,
        True,
        rx.cond(
            is_rank_a,
            True,
            rx.cond(
                is_rank_b,
                True,
                rx.cond(
                    is_rank_c,
                    True,
                    rx.cond(is_rank_d, True, False)
                )
            )
        )
    )
    
    # 배경색 결정 (깔끔한 색상)
    bg_color = rx.cond(
        is_rank_s,
        "#22c55e",  # 밝은 그린
        rx.cond(
            is_rank_a,
            "#3b82f6",  # 파란색
            rx.cond(
                is_rank_b,
                "#22c55e",  # 중간 그린
                rx.cond(
                    is_rank_c,
                    "#f59e0b",  # 주황색
                    rx.cond(
                        is_rank_d,
                        "#ef4444",  # 빨간색
                        "#e5e7eb"  # 회색
                    )
                )
            )
        )
    )
    
    # 텍스트 색상 결정
    text_color = rx.cond(
        is_rank_badge,
        "white",
        "inherit"
    )
    
    # 설명 텍스트 색상 결정
    desc_color = rx.cond(
        is_rank_badge,
        "white",
        "gray"
    )
    
    return rx.card(
        rx.vstack(
            rx.text(
                item['icon'],
                font_size="4rem",
                text_align="center",
                margin_bottom="0.5rem"
            ),
            rx.heading(
                item['name'],
                size="4",
                text_align="center",
                color=text_color,
                weight="bold",
                margin_bottom="0.5rem"
            ),
            rx.text(
                item['description'],
                size="2",
                text_align="center",
                color=desc_color,
                line_height="1.5"
            ),
            spacing="2",
            align="center",
            width="100%",
            padding="1rem"
        ),
        width="100%",
        padding="1.5rem",
        background=bg_color,
        border_radius="1rem",
        box_shadow="0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
        _hover={
            "box_shadow": "0 10px 15px -3px rgba(0, 0, 0, 0.2), 0 4px 6px -2px rgba(0, 0, 0, 0.1)",
            "transform": "translateY(-4px)"
        }
    )

def render_ai_analysis_section(
    ai_analysis: rx.Var[Dict],
    ai_analysis_text: rx.Var[str] = None,
    ai_suggestions: rx.Var[List] = None,
    ai_alternatives: rx.Var[List] = None,
    ai_emotional_message: rx.Var[str] = None,
) -> rx.Component:
    """AI 분석 섹션"""
    # ai_analysis가 있거나, ai_analysis_text가 비어있지 않으면 표시
    # 둘 중 하나라도 있으면 표시 (중첩 조건 사용)
    has_analysis = rx.cond(
        ai_analysis,
        True,
        rx.cond(
            ai_analysis_text.length() > 0,
            True,
            False
        )
    )
    
    return rx.cond(
        has_analysis,
        rx.vstack(
            rx.center(
                rx.heading(
                    "🤖 AI 분석 결과",
                    size="6",
                    color="#0f172a",
                    font_weight="bold",
                    text_align="center",
                    align="center"
                ),
                width="100%",
                padding="1.5rem",
            ),
            rx.card(
                rx.vstack(
                    rx.heading(
                        "📊 분석",
                        size="5",
                        color="#1f2937",
                        weight="bold",
                        margin_bottom="1rem"
                    ),
                    rx.cond(
                        ai_analysis_text,
                        rx.callout(
                            ai_analysis_text,
                            icon="chart-bar",
                            color_scheme="green",
                            variant="soft",
                            border_radius="0.75rem"
                        ),
                        rx.text("분석 결과를 불러오는 중...", color="gray", size="3")
                    ),
                    
                    rx.heading(
                        "💡 탄소 저감 제안",
                        size="5",
                        margin_top="1.5rem",
                        color="#1f2937",
                        weight="bold",
                        margin_bottom="1rem"
                    ),
                    rx.cond(
                        ai_suggestions.length() > 0,
                        rx.vstack(
                            rx.foreach(
                                ai_suggestions,
                                lambda text: rx.hstack(
                                    rx.box(
                                        rx.icon("check", size=20, color="white"),
                                        padding="0.5rem",
                                        background="#22c55e",
                                        border_radius="50%",
                                        margin_right="0.75rem"
                                    ),
                                    rx.text(
                                        text,
                                        size="4",
                                        color="gray",
                                        line_height="1.6"
                                    ),
                                    align="center",
                                    padding="0.75rem",
                                    background="#f0fdfa",
                                    border_radius="0.5rem",
                                    width="100%"
                                )
                            ),
                            spacing="2",
                            align="start",
                            width="100%"
                        ),
                        rx.text("제안이 없습니다.", color="gray", size="3")
                    ),
                    
                    rx.heading(
                        "🌱 대안 행동",
                        size="5",
                        margin_top="1.5rem",
                        color="#1f2937",
                        weight="bold",
                        margin_bottom="1rem"
                    ),
                    rx.cond(
                        ai_alternatives.length() > 0,
                        rx.vstack(
                            rx.foreach(
                                ai_alternatives,
                                render_alternative_row
                            ),
                            spacing="2",
                            align="start",
                            width="100%"
                        ),
                        rx.text("대안 행동이 없습니다.", color="gray", size="3")
                    ),
                    
                    rx.heading(
                        "💬 격려 메시지",
                        size="5",
                        margin_top="1.5rem",
                        color="#1f2937",
                        weight="bold",
                        margin_bottom="1rem"
                    ),
                    rx.cond(
                        ai_emotional_message,
                        rx.callout(
                            ai_emotional_message,
                            icon="heart",
                            color_scheme="green",
                            variant="soft",
                            border_radius="0.75rem"
                        ),
                        rx.text("격려 메시지를 불러오는 중...", color="gray", size="3")
                    ),
                    spacing="4",
                    width="100%"
                ),
                width="100%",
                padding="4"
            ),
            spacing="4",
            width="100%",
            align="center"
        ),
        rx.vstack(
            rx.heading("🤖 AI 분석 결과", size="5", margin_top="1rem", color="#1f2937"),
            rx.text("AI 분석 결과를 불러오는 중...", color="gray", size="3"),
            spacing="2",
            width="100%",
            align="center",
            padding="2rem"
        )
    )

def render_alternative_row(alt: rx.Var[Dict]) -> rx.Component:
    """대안 행동 한 줄 렌더링"""
    # [안전장치] 딕셔너리로 변환 (이게 없으면 에러 발생)
    item = alt.to(dict)
    
    return rx.card(
        rx.hstack(
            rx.vstack(
                rx.text("현재 행동", size="2", color="gray", weight="medium"),
                rx.text(
                    item['current'],
                    size="4",
                    weight="bold",
                    color="#374151",
                    margin_top="0.25rem"
                ),
                spacing="1",
                align="start",
                flex="1"
            ),
            rx.box(
                rx.icon("arrow-right", size=24, color="#22c55e"),
                padding="0.5rem",
                margin_x="1rem"
            ),
            rx.vstack(
                rx.text("대안 행동", size="2", color="#22c55e", weight="bold"),
                rx.text(
                    item['alternative'],
                    size="4",
                    weight="bold",
                    color="#22c55e",
                    margin_top="0.25rem"
                ),
                spacing="1",
                align="start",
                flex="1"
            ),
            rx.spacer(),
            rx.badge(
                f"효과: {item['impact']}",
                color_scheme="green",
                variant="solid",
                size="2",
                padding="0.5rem 1rem"
            ),
            align="center",
            width="100%",
            padding="1rem"
        ),
        padding="1.5rem",
        width="100%",
        background="white",
        border_radius="0.75rem",
        border="2px solid",
        border_color="#dcfce7",
        box_shadow="0 1px 3px 0 rgba(0, 0, 0, 0.08)",
        _hover={
            "border_color": "#22c55e",
            "box_shadow": "0 4px 6px -1px rgba(34, 197, 94, 0.2)"
        }
    )