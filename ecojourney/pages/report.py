# report.py

import reflex as rx
from ..states import AppState
from typing import Dict, Any

def report_page() -> rx.Component:
    """
    최종 탄소 발자국 리포트 페이지 컴포넌트입니다.
    페이지 로드 시 자동으로 탄소 배출량을 계산합니다.
    """
    # 페이지 로드 시 자동으로 계산 수행 (조건부 렌더링으로 트리거)
    # 리포트 페이지가 렌더링될 때 계산이 안 되어 있으면 자동으로 계산
    return rx.center(
        rx.vstack(
            rx.heading("🌍 탄소 발자국 측정 결과", size="7", margin_bottom="20px"),
            
            # 계산 버튼 (수동 재계산용)
            rx.cond(
                ~AppState.is_report_calculated,
                rx.button(
                    "📊 탄소 배출량 계산하기",
                    on_click=AppState.calculate_report,
                    color_scheme="blue",
                    size="3",
                    margin_bottom="20px"
                ),
            ),
            
            # 1. 계산 상태 확인
            rx.cond(
                AppState.is_report_calculated,
                rx.vstack(
                    rx.text("✅ 최종 계산이 완료되었습니다.", color="green.700", size="5"),
                    rx.text(
                        f"총 {AppState.all_activities.length()}개의 활동이 계산되었습니다.",
                        color="gray.600",
                        size="3"
                    ),
                    spacing="2"
                ),
                rx.text("⏳ 계산이 완료되지 않았습니다. 위 버튼을 클릭하여 계산하세요.", color="orange.700", size="5"),
            ),
            
            rx.divider(margin_y="20px"),
            
            # 2. 총 배출량 및 절약량
            rx.hstack(
                rx.vstack(
                    rx.text(
                        "총 배출량 (kg CO2e):", 
                        font_weight="bold",
                        size="4"
                    ),
                    rx.text(
                        AppState.total_carbon_emission, 
                        size="8", 
                        color="blue.700"
                    ),
                    spacing="1",
                    align="center",
                ),
                rx.cond(
                    AppState.total_saved_emission > 0,
                    rx.vstack(
                        rx.text(
                            "절약한 탄소 (kg CO2e):", 
                            font_weight="bold",
                            size="4"
                        ),
                        rx.text(
                            AppState.total_saved_emission, 
                            size="8", 
                            color="green.700"
                        ),
                        rx.text(
                            f"절약 금액: {AppState.saved_money}원",
                            size="3",
                            color="green.600"
                        ),
                        spacing="1",
                        align="center",
                    ),
                    rx.fragment(),
                ),
                spacing="8",
                justify="center",
                width="100%",
            ),
            
            # 3. 상세 내역 (데이터 개수 확인)
            rx.text(
                f"총 활동 기록 수: {AppState.all_activities.length()}",
                color="gray.600"
            ),
            
            rx.divider(margin_y="20px"),
            
            # 4. 상세 계산 내역 표시 및 도넛 차트
            rx.cond(
                AppState.is_report_calculated & (AppState.calculation_details.length() > 0),
                rx.hstack(
                    # 상세 계산 내역
                    rx.box(
                        rx.vstack(
                            rx.heading("📋 상세 계산 내역", size="5", margin_bottom="10px"),
                            rx.foreach(
                                AppState.calculation_details,
                                lambda detail: rx.vstack(
                                    # 카테고리 및 활동 유형
                                    rx.hstack(
                                        rx.text(detail["category"], font_weight="bold", size="3"),
                                        rx.text(" - ", font_weight="bold", size="3"),
                                        rx.text(
                                            detail["activity_type"], 
                                            font_weight="bold", 
                                            size="3",
                                            overflow="hidden",
                                            text_overflow="ellipsis",
                                            white_space="nowrap",
                                            max_width="100%",
                                        ),
                                        spacing="0",
                                        width="100%",
                                        align="start",
                                    ),
                                    # 값 및 배출량
                                    rx.hstack(
                                        rx.text(detail["value"], color="gray.600", size="3"),
                                        rx.text(detail["unit"], color="gray.600", size="3"),
                                        rx.text(" = ", color="gray.600", size="3"),
                                        rx.text(detail["emission"], color="blue.700", font_weight="bold", size="3"),
                                        rx.text("kgCO2e", color="blue.700", font_weight="bold", size="3"),
                                        spacing="1",
                                        width="100%",
                                        flex_wrap="wrap",
                                    ),
                                    # 계산 방법
                                    rx.hstack(
                                        rx.text("(", color="green.600", size="2"),
                                        rx.text(
                                            detail["method"], 
                                            color="green.600", 
                                            size="2",
                                            overflow="hidden",
                                            text_overflow="ellipsis",
                                            white_space="nowrap",
                                            max_width="100%",
                                        ),
                                        rx.text(")", color="green.600", size="2"),
                                        spacing="0",
                                        width="100%",
                                    ),
                                    spacing="1",
                                    margin_bottom="10px",
                                    padding="10px",
                                    border="1px solid",
                                    border_color="gray.200",
                                    border_radius="6px",
                                    width="100%",
                                    align="start",
                                )
                            ),
                            spacing="2",
                            width="100%",
                        ),
                        padding="20px",
                        border="1px solid",
                        border_color="gray.300",
                        border_radius="8px",
                        width="50%",
                        margin_right="10px",
                        overflow="hidden",
                    ),
                    
                    # 도넛 차트 (카테고리별 비율)
                    rx.cond(
                        AppState.category_emission_breakdown.length() > 0,
                        rx.box(
                            rx.vstack(
                                rx.heading("🍩 카테고리별 배출 비율", size="5", margin_bottom="15px"),
                                rx.cond(
                                    AppState.total_carbon_emission > 0,
                                    rx.vstack(
                                        # 도넛 차트 SVG
                                        rx.cond(
                                            AppState.donut_chart_svg != "",
                                            rx.box(
                                                rx.html(AppState.donut_chart_svg),
                                                width="200px",
                                                height="200px",
                                                display="flex",
                                                align_items="center",
                                                justify_content="center",
                                                margin_bottom="15px",
                                            ),
                                            rx.box(
                                                rx.text("차트 생성 중...", color="gray.400", size="3"),
                                                width="200px",
                                                height="200px",
                                                display="flex",
                                                align_items="center",
                                                justify_content="center",
                                                margin_bottom="15px",
                                            ),
                                        ),
                                        # 범례 및 상세 정보
                                        rx.vstack(
                                            rx.foreach(
                                                AppState.category_emission_list,
                                                lambda item: rx.hstack(
                                                    rx.box(
                                                        width="20px",
                                                        height="20px",
                                                        border_radius="4px",
                                                        background=item["color"],
                                                    ),
                                                    rx.vstack(
                                                        rx.hstack(
                                                            rx.text(
                                                                item["category"],
                                                                font_weight="bold",
                                                                size="3",
                                                                color="gray.800",
                                                            ),
                                                            rx.text(
                                                                f"{item['percentage']:.1f}%",
                                                                size="2",
                                                                color="gray.600",
                                                            ),
                                                            justify="between",
                                                            width="100%",
                                                        ),
                                                        rx.text(
                                                            f"{item['emission']:.2f}kg",
                                                            size="2",
                                                            color="gray.600",
                                                        ),
                                                        spacing="1",
                                                        width="100%",
                                                    ),
                                                    spacing="3",
                                                    width="100%",
                                                    margin_bottom="10px",
                                                ),
                                            ),
                                            spacing="2",
                                            align="start",
                                            width="100%",
                                        ),
                                        spacing="2",
                                        align="center",
                                    ),
                                    rx.text("데이터 없음", color="gray.400", size="3"),
                                ),
                                spacing="2",
                            ),
                            padding="20px",
                            border="1px solid",
                            border_color="gray.300",
                            border_radius="12px",
                            width="50%",
                            margin_left="10px",
                        ),
                        rx.fragment(),
                    ),
                    spacing="4",
                    width="100%",
                    align="start",
                    margin_bottom="20px",
                ),
            ),
            
            rx.divider(margin_y="20px"),
            
            # 절약량 상세 정보
            rx.cond(
                AppState.total_saved_emission > 0,
                rx.box(
                    rx.vstack(
                        rx.heading("🌱 탄소 절약 내역", size="6", margin_bottom="15px"),
                        rx.text(
                            f"자전거/걷기를 사용하여 총 {AppState.total_saved_emission}kg의 탄소를 절약했습니다!",
                            size="4",
                            color="green.700",
                            margin_bottom="10px",
                        ),
                        rx.text(
                            f"절약 금액: {AppState.saved_money}원 (포인트로 지급)",
                            size="3",
                            color="green.600",
                            margin_bottom="15px",
                        ),
                        rx.foreach(
                            AppState.savings_details,
                            lambda item: rx.hstack(
                                rx.text(
                                    f"• {item['activity_type']} {item['distance_km']}km",
                                    size="3",
                                    color="gray.700",
                                ),
                                rx.text(
                                    f"→ {item['saved_emission']}kg 절약 ({item['saved_money']}원)",
                                    size="3",
                                    color="green.600",
                                    font_weight="bold",
                                ),
                                spacing="2",
                                width="100%",
                            ),
                        ),
                        spacing="2",
                    ),
                    padding="20px",
                    border="1px solid",
                    border_color="green.300",
                    border_radius="12px",
                    background="green.50",
                    margin_bottom="20px",
                    width="100%",
                ),
                rx.fragment(),
            ),
            
            rx.divider(margin_y="20px"),
            
            # 카테고리별 비교 그래프
            rx.cond(
                AppState.is_report_calculated & (AppState.category_emission_breakdown.length() > 0),
                rx.vstack(
                    rx.heading("📊 카테고리별 배출량 분석", size="6", margin_bottom="20px"),
                    
                    # 평균 vs 내 배출량 비교 세로 막대 그래프
                    rx.box(
                        rx.vstack(
                            rx.heading("📈 평균 vs 내 배출량", size="5", margin_bottom="15px"),
                            rx.text("(단위: kg)", size="2", color="gray.600", margin_bottom="10px"),
                            # 범례
                            rx.hstack(
                                rx.hstack(
                                    rx.box(
                                        width="16px",
                                        height="16px",
                                        background="#3b82f6",
                                        border_radius="4px",
                                    ),
                                    rx.text("평균", size="2", color="gray.700"),
                                    spacing="2",
                                ),
                                rx.hstack(
                                    rx.box(
                                        width="16px",
                                        height="16px",
                                        background="#10b981",
                                        border_radius="4px",
                                    ),
                                    rx.text("내 배출량", size="2", color="gray.700"),
                                    spacing="2",
                                ),
                                spacing="4",
                                margin_bottom="15px",
                            ),
                            # 세로 막대 그래프
                            rx.hstack(
                                rx.foreach(
                                    AppState.average_comparison_list,
                                    lambda item: rx.vstack(
                                        # 막대들
                                        rx.hstack(
                                            # 평균 막대
                                            rx.vstack(
                                                rx.box(
                                                    height=f"{item['average_bar_height']}px",
                                                    width="20px",
                                                    background="#3b82f6",
                                                    border_radius="2px 2px 0 0",
                                                    display="flex",
                                                    align_items="end",
                                                    justify_content="center",
                                                ),
                                                spacing="0",
                                                align="center",
                                            ),
                                            # 내 배출량 막대
                                            rx.vstack(
                                                rx.box(
                                                    height=f"{item['user_bar_height']}px",
                                                    width="20px",
                                                    background=rx.cond(
                                                        item["is_better"],
                                                        "#10b981",
                                                        "#ef4444"
                                                    ),
                                                    border_radius="2px 2px 0 0",
                                                    display="flex",
                                                    align_items="end",
                                                    justify_content="center",
                                                ),
                                                spacing="0",
                                                align="center",
                                            ),
                                            spacing="4",
                                            align="end",
                                        ),
                                        # 값 표시
                                        rx.hstack(
                                            rx.vstack(
                                                rx.text(
                                                    f"{item['average']:.1f}",
                                                    size="2",
                                                    color="blue.600",
                                                    font_weight="bold",
                                                ),
                                                spacing="0",
                                                align="center",
                                            ),
                                            rx.vstack(
                                                rx.text(
                                                    f"{item['user']:.1f}",
                                                    size="2",
                                                    color=rx.cond(
                                                        item["is_better"],
                                                        "green.600",
                                                        "red.600"
                                                    ),
                                                    font_weight="bold",
                                                ),
                                                spacing="0",
                                                align="center",
                                            ),
                                            spacing="8",
                                            align="center",
                                            margin_top="5px",
                                        ),
                                        # 카테고리명
                                        rx.text(
                                            item["category"],
                                            size="2",
                                            color="gray.700",
                                            font_weight="bold",
                                            margin_top="5px",
                                        ),
                                        spacing="2",
                                        align="center",
                                        width="100px",
                                    ),
                                ),
                                spacing="4",
                                align="end",
                                justify="center",
                                width="100%",
                            ),
                            spacing="2",
                        ),
                        padding="20px",
                        border="1px solid",
                        border_color="gray.300",
                        border_radius="12px",
                        width="100%",
                        margin_bottom="20px",
                    ),
                    spacing="3",
                    align="center",
                    width="100%",
                ),
                rx.fragment(),
            ),
            
            rx.divider(margin_y="20px"),
            
            # AI 분석 결과 및 대안 추천
            rx.cond(
                AppState.is_report_calculated,
                rx.vstack(
                    rx.heading("🤖 AI 분석 및 대안 추천", size="6", margin_bottom="20px"),
                    
                    rx.cond(
                        AppState.is_loading_ai,
                        rx.vstack(
                            rx.text("AI 분석 중...", color="blue.600", size="4"),
                            rx.progress(is_indeterminate=True, width="100%", max_width="400px"),
                            spacing="3",
                            align="center",
                        ),
                        rx.cond(
                            AppState.ai_analysis_result != "",
                            rx.vstack(
                                # AI 분석 결과
                                rx.box(
                                    rx.vstack(
                                        rx.heading("📝 분석 결과", size="5", margin_bottom="10px"),
                                        rx.text(
                                            AppState.ai_analysis_result,
                                            size="3",
                                            line_height="1.8",
                                            white_space="pre-wrap",
                                        ),
                                        spacing="2",
                                    ),
                                    padding="20px",
                                    border="1px solid",
                                    border_color="blue.300",
                                    border_radius="12px",
                                    background="blue.50",
                                    margin_bottom="20px",
                                    width="100%",
                                    max_width="800px",
                                ),
                                
                                # 구체적 제안
                                rx.box(
                                    rx.vstack(
                                        rx.heading("💡 탄소 저감 제안", size="5", margin_bottom="10px"),
                                        rx.foreach(
                                            AppState.ai_suggestions,
                                            lambda suggestion: rx.hstack(
                                                rx.text("• ", color="green.600", font_weight="bold"),
                                                rx.text(
                                                    suggestion,
                                                    size="3",
                                                    line_height="1.8",
                                                ),
                                                spacing="2",
                                                width="100%",
                                                margin_bottom="8px",
                                            ),
                                        ),
                                        spacing="2",
                                    ),
                                    padding="20px",
                                    border="1px solid",
                                    border_color="green.300",
                                    border_radius="12px",
                                    background="green.50",
                                    margin_bottom="20px",
                                    width="100%",
                                    max_width="800px",
                                ),
                                
                                # 대안 행동
                                rx.cond(
                                    AppState.ai_alternatives.length() > 0,
                                    rx.box(
                                        rx.vstack(
                                            rx.heading("🔄 대안 행동 추천", size="5", margin_bottom="10px"),
                                            rx.foreach(
                                                AppState.ai_alternatives,
                                                lambda alt: rx.vstack(
                                                    rx.hstack(
                                                        rx.text("현재: ", font_weight="bold", size="3"),
                                                        rx.text(
                                                            alt.get("current", "") if isinstance(alt, dict) else "",
                                                            size="3",
                                                            color="red.600",
                                                        ),
                                                        spacing="2",
                                                    ),
                                                    rx.hstack(
                                                        rx.text("대안: ", font_weight="bold", size="3"),
                                                        rx.text(
                                                            alt.get("alternative", "") if isinstance(alt, dict) else "",
                                                            size="3",
                                                            color="green.600",
                                                        ),
                                                        spacing="2",
                                                    ),
                                                    rx.text(
                                                        f"예상 감소량: {alt.get('reduction', 0)}%" if isinstance(alt, dict) else "",
                                                        size="2",
                                                        color="blue.600",
                                                        margin_top="5px",
                                                    ),
                                                    padding="15px",
                                                    border="1px solid",
                                                    border_color="gray.300",
                                                    border_radius="8px",
                                                    margin_bottom="10px",
                                                    width="100%",
                                                ),
                                            ),
                                            spacing="2",
                                        ),
                                        padding="20px",
                                        border="1px solid",
                                        border_color="purple.300",
                                        border_radius="12px",
                                        background="purple.50",
                                        margin_bottom="20px",
                                        width="100%",
                                        max_width="800px",
                                    ),
                                ),
                                
                                spacing="3",
                                align="center",
                                width="100%",
                            ),
                            rx.vstack(
                                rx.text("AI 분석을 시작하려면 아래 버튼을 클릭하세요.", color="gray.600", size="3"),
                                rx.button(
                                    "🤖 AI 분석 시작하기",
                                    on_click=AppState.generate_ai_analysis,
                                    color_scheme="purple",
                                    size="3",
                                    margin_top="10px",
                                ),
                                spacing="2",
                                align="center",
                            ),
                        ),
                    ),
                    
                    spacing="3",
                    align="center",
                    width="100%",
                ),
            ),
            
            rx.divider(margin_y="20px"),
            
            # 저장 버튼 및 메시지 (로그인한 경우에만 표시)
            rx.cond(
                AppState.is_logged_in,
                rx.vstack(
                    rx.cond(
                        AppState.is_saving,
                        rx.text("💾 저장 중...", color="blue.600", size="4"),
                        rx.button(
                            "💾 데이터 저장하기",
                            on_click=AppState.save_carbon_log_to_db,
                            color_scheme="green",
                            size="3",
                            is_disabled=~AppState.is_report_calculated,
                            margin_bottom="10px"
                        )
                    ),
                    rx.cond(
                        AppState.save_message != "",
                        rx.text(
                            AppState.save_message,
                            color=rx.cond(
                                AppState.is_save_success,
                                "green.700",
                                "red.700"
                            ),
                            size="4",
                            margin_bottom="10px"
                        ),
                    ),
                    spacing="2",
                    margin_bottom="20px"
                ),
            ),
            
            # 4. 재시작 버튼
            rx.button(
                "다시 시작하기",
                # 홈 또는 인트로 페이지로 돌아갑니다.
                on_click=rx.redirect("/intro"), 
                color_scheme="gray",
                size="2"
            ),
            
            spacing="5",
            align="center",
            padding="50px"
        ),
        width="100%",
        min_height="100vh"
    )