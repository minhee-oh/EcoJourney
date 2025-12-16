# report.py - 리포트 페이지 (대시보드 디자인)

import reflex as rx
from ..states import AppState
from .common_header import header


def report_page() -> rx.Component:
    return rx.cond(
        AppState.is_logged_in,
        # 로그인된 경우: 리포트 표시 (계산 중이거나 완료된 경우 모두)
        rx.cond(
            AppState.is_report_calculated,
            # 리포트 생성 완료 시: 리포트 표시
            rx.box(
                header(),
                # 헤더 공간 확보
                rx.box(height="100px"),
                # fade-in 애니메이션을 위한 CSS 삽입
                rx.html("""
                <style>
                @keyframes fadeInUp {
                    0% {
                        opacity: 0;
                        transform: translateY(20px);
                    }
                    100% {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }
                </style>
                """),
                # 배경 레이어 구성
                rx.box(
                    # 상단 배경 + 텍스트 + fade-in animation
                    rx.box(
                        rx.hstack(
                            rx.vstack(
                                rx.heading(
                                    "탄소 발자국 리포트",
                                    size="9",
                                    color="#333333",
                                    margin_bottom="18px",
                                    style={
                                        "opacity": 0,
                                        "transform": "translateY(20px)",
                                        "animation": "fadeInUp 0.8s ease forwards",
                                        "animation-delay": "0.1s",
                                    },
                                ),
                                rx.text(
                                    "당신의 탄소 배출량을 분석하고 AI 코칭을 받아보세요!",
                                    color="#333333",
                                    size="5",
                                    font_weight="bold",
                                    text_align="left",
                                    width="100%",
                                    style={
                                        "opacity": 0,
                                        "transform": "translateY(20px)",
                                        "animation": "fadeInUp 1s ease forwards",
                                        "animation-delay": "0.25s",
                                    },
                                ),
                                spacing="2",
                                align="start",
                                justify="center",
                                height="100%",
                                padding_top="50px",
                                padding_left="100px",
                            ),
                            # 오른쪽: 이미지 영역
                            rx.box(
                                rx.image(
                                    src="/report.png",
                                    width="100%",
                                    height="auto",
                                    object_fit="contain",
                                    style={
                                        "opacity": 0,
                                        "transform": "translateY(20px)",
                                        "animation": "fadeInUp 0.8s ease forwards",
                                        "animation-delay": "0.2s",
                                    },
                                ),
                                width="50%",
                                display="flex",
                                align_items="center",
                                justify_content="center",
                                padding_left="50px",
                                padding_top="70px",
                            ),
                            width="100%",
                            height="100%",
                            align="center",
                            justify="between",
                        ),
                        width="100%",
                        height="80vh",
                        background="linear-gradient(135deg, rgba(77, 171, 117, 0.1) 0%, rgba(77, 171, 117, 0.15) 100%)",
                        position="absolute",
                        top="0",
                        left="0",
                        z_index="0",
                    ),
                ),
                # 실제 콘텐츠
                rx.box(
                    rx.vstack(
                        # 상단 주요 통계 섹션 (레벨, 총 배출량, 절약량)
                        rx.box(
                            rx.card(
                                rx.hstack(
                                    # 레벨
                                    rx.cond(
                                        AppState.carbon_level_image != "",
                                        rx.vstack(
                                            rx.text("⭐ 탄소 레벨", color="gray.600", size="4", font_weight="bold"),
                                            rx.hstack(
                                                rx.image(src=AppState.carbon_level_image, width="60px", height="60px"),
                                                rx.vstack(
                                                    rx.text(f"Level {AppState.carbon_level}", size="6", font_weight="bold", color="#333333"),
                                                    rx.text(AppState.next_level_text, size="4", color="gray.600", font_weight="bold"),
                                                    spacing="1",
                                                    align="start",
                                                ),
                                                spacing="3",
                                                align="center",
                                            ),
                                            spacing="2",
                                            align="center",
                                            width="100%",
                                        ),
                                        rx.box(),  # 레벨 정보가 없으면 빈 공간
                                    ),
                                    
                                    # 구분선
                                    rx.box(
                                        width="1px",
                                        height="80px",
                                        background="rgba(0,0,0,0.1)",
                                    ),
                                    
                                    # 총 배출량
                                    rx.vstack(
                                        rx.text("🌍 총 배출량", color="gray.600", size="4", font_weight="bold"),
                                        rx.text(
                                            f"{AppState.total_carbon_emission} kg CO₂e",
                                            size="8",
                                            color="#4DAB75",
                                            font_weight="bold",
                                        ),
                                        rx.cond(
                                            AppState.has_average_comparison,
                                            rx.vstack(
                                                rx.text(
                                                    rx.cond(
                                                        AppState.total_average_comparison["is_better"],
                                                        f"평균보다 {AppState.total_average_comparison['abs_difference']:.1f} kg 적음",
                                                        f"평균보다 {AppState.total_average_comparison['abs_difference']:.1f} kg 많음",
                                                    ),
                                                    size="4",
                                                    color=rx.cond(
                                                        AppState.total_average_comparison["is_better"],
                                                        "#4DAB75",
                                                        "#E74C3C",
                                                    ),
                                                    font_weight="bold",
                                                ),
                                                spacing="0",
                                                align="center",
                                            ),
                                            rx.box(),
                                        ),
                                        rx.text(
                                            f"총 활동 수: {AppState.all_activities.length()}개",
                                            size="4",
                                            color="gray.600",
                                            font_weight="bold",
                                            margin_top="10px",
                                        ),
                                        spacing="2",
                                        align="center",
                                        width="100%",
                                    ),
                                    
                                    # 구분선
                                    rx.box(
                                        width="1px",
                                        height="80px",
                                        background="rgba(0,0,0,0.1)",
                                    ),
                                    
                                    
                                    spacing="6",
                                    width="100%",
                                    align="center",
                                    justify="center",
                                ),
                                width="100%",
                                background="white",
                                border="1px solid rgba(0,0,0,0.1)",
                                box_shadow="0 4px 12px rgba(0,0,0,0.1)",
                                padding="40px",
                                border_radius="16px",
                            ),
                            width="100%",
                            margin_bottom="30px",
                        ),

                        # 중간 섹션: 도넛 차트와 포인트 상세
                        rx.hstack(
                            # 카테고리별 배출 비율 도넛 차트 카드
                            rx.cond(
                                AppState.category_emission_list.length() > 0,
                                rx.card(
                                    rx.vstack(
                                        rx.heading("📊 카테고리별 배출 비율", size="6", color="#333333", margin_bottom="20px"),
                                        rx.hstack(
                                            # 도넛 차트
                                            rx.box(
                                                rx.html(AppState.donut_chart_svg),
                                                width="250px",
                                                height="250px",
                                                display="flex",
                                                align_items="center",
                                                justify_content="center",
                                            ),
                                            # 카테고리별 상세 정보
                                            rx.vstack(
                                                rx.foreach(
                                                    AppState.category_emission_list,
                                                    lambda cat: rx.hstack(
                                                        rx.box(
                                                            width="12px",
                                                            height="12px",
                                                            background_color=cat["color"],
                                                            border_radius="2px",
                                                        ),
                                                        rx.vstack(
                                                            rx.hstack(
                                                                rx.text(cat["category"], size="4", font_weight="bold", color="#333333"),
                                                                rx.text(f"{cat['percentage']}%", size="5", color="gray.600", font_weight="bold"),
                                                                spacing="2",
                                                            ),
                                                            rx.text(f"{cat['emission']} kgCO₂e", size="5", color="gray.600", font_weight="bold"),
                                                            spacing="1",
                                                            align="start",
                                                        ),
                                                        spacing="2",
                                                        align="start",
                                                        width="100%",
                                                        padding="12px",
                                                        border="1px solid rgba(0,0,0,0.1)",
                                                        border_radius="8px",
                                                        background="rgba(77, 171, 117, 0.05)",
                                                    ),
                                                ),
                                                spacing="2",
                                                width="100%",
                                                max_width="400px",
                                            ),
                                            spacing="6",
                                            align="start",
                                            width="100%",
                                            justify="center",
                                        ),
                                        spacing="4",
                                        align="center",
                                        width="100%",
                                    ),
                                    width="60%",
                                    background="white",
                                    border="1px solid rgba(0,0,0,0.1)",
                                    box_shadow="0 4px 12px rgba(0,0,0,0.1)",
                                    padding="30px",
                                    border_radius="16px",
                                ),
                                rx.box(width="60%"),  # 차트가 없으면 빈 공간
                            ),
                            
                            # 포인트 상세 정보 카드
                            rx.cond(
                                AppState.total_points_earned > 0,
                                rx.card(
                                    rx.vstack(
                                        rx.heading("💰 포인트 상세", size="6", color="#333333", margin_bottom="20px"),
                                        # 포인트 계산 방식 설명
                                        rx.box(
                                            rx.vstack(
                                                rx.text(
                                                    "💡 포인트 계산 기준",
                                                    size="4",
                                                    color="#333333",
                                                    font_weight="bold",
                                                    margin_bottom="8px",
                                                ),
                                                rx.vstack(
                                                    rx.text(
                                                        "• 절약량: 걷기/자전거 사용 시 대중교통(버스) 대비 절약한 비용만큼 포인트 지급",
                                                        size="3",
                                                        color="gray.600",
                                                        font_weight="500",
                                                    ),
                                                    rx.text(
                                                        "  (같은 거리를 버스로 갔을 때의 배출량 × 100원/kg)",
                                                        size="3",
                                                        color="gray.500",
                                                        font_weight="400",
                                                        font_style="italic",
                                                    ),
                                                    rx.text(
                                                        "• 빈티지: 빈티지 제품 1개당 10점",
                                                        size="3",
                                                        color="gray.600",
                                                        font_weight="500",
                                                    ),
                                                    rx.text(
                                                        "• 평균 대비: 평균보다 낮은 배출량 1kg당 20점 (최대 100점)",
                                                        size="3",
                                                        color="gray.600",
                                                        font_weight="500",
                                                    ),
                                                    spacing="4",
                                                    align="start",
                                                ),
                                                spacing="2",
                                                align="start",
                                            ),
                                            background="rgba(77, 171, 117, 0.1)",
                                            padding="16px 20px",
                                            border_radius="8px",
                                            margin_bottom="20px",
                                            border="1px solid rgba(77, 171, 117, 0.2)",
                                        ),
                                        rx.vstack(
                                            rx.hstack(
                                                rx.vstack(
                                                    rx.text("절약량", size="5", color="gray.600", font_weight="bold", text_align="center", width="100%"),
                                                    rx.text(
                                                        rx.cond(
                                                            AppState.points_breakdown["절약량"] != None,
                                                            f"{AppState.points_breakdown['절약량']}점",
                                                            "0점"
                                                        ),
                                                        size="6",
                                                        font_weight="bold",
                                                        color="#4DAB75",
                                                        text_align="center",
                                                        width="100%",
                                                    ),
                                                    spacing="1",
                                                    align="center",
                                                    flex="1",
                                                    min_width="80px",
                                                ),
                                                rx.vstack(
                                                    rx.text("빈티지", size="5", color="gray.600", font_weight="bold", text_align="center", width="100%"),
                                                    rx.text(
                                                        rx.cond(
                                                            AppState.points_breakdown["빈티지"] != None,
                                                            f"{AppState.points_breakdown['빈티지']}점",
                                                            "0점"
                                                        ),
                                                        size="6",
                                                        font_weight="bold",
                                                        color="#4DAB75",
                                                        text_align="center",
                                                        width="100%",
                                                    ),
                                                    spacing="1",
                                                    align="center",
                                                    flex="1",
                                                    min_width="80px",
                                                ),
                                                rx.vstack(
                                                    rx.text("평균 대비", size="5", color="gray.600", font_weight="bold", text_align="center", width="100%"),
                                                    rx.text(
                                                        rx.cond(
                                                            AppState.points_breakdown["평균 대비"] != None,
                                                            f"{AppState.points_breakdown['평균 대비']}점",
                                                            "0점"
                                                        ),
                                                        size="6",
                                                        font_weight="bold",
                                                        color="#4DAB75",
                                                        text_align="center",
                                                        width="100%",
                                                    ),
                                                    spacing="1",
                                                    align="center",
                                                    flex="1",
                                                    min_width="80px",
                                                ),
                                                spacing="6",
                                                justify="center",
                                                align="center",
                                                width="100%",
                                            ),
                                            rx.divider(margin_y="15px"),
                                            rx.text(
                                                f"총 {AppState.total_points_earned}점",
                                                size="6",
                                                font_weight="bold",
                                                color="#FF9800",
                                                margin_top="10px",
                                                text_align="center",
                                            ),
                                            spacing="2",
                                            align="center",
                                            width="100%",
                                        ),
                                        spacing="3",
                                    ),
                                    width="40%",
                                    background="white",
                                    border="1px solid rgba(0,0,0,0.1)",
                                    box_shadow="0 4px 12px rgba(0,0,0,0.1)",
                                    padding="30px",
                                    border_radius="16px",
                                ),
                                rx.box(width="40%"),  # 포인트가 없으면 빈 공간
                            ),
                            
                            spacing="4",
                            width="100%",
                            align="stretch",
                            margin_bottom="30px",
                        ),

                        # 하단 섹션: AI 분석과 제안
                        rx.vstack(
                            # AI 분석 결과 카드
                            rx.cond(
                                AppState.ai_analysis_result != "",
                                rx.card(
                                    rx.vstack(
                                        rx.heading("🤖 AI 분석 결과", size="6", color="#333333", margin_bottom="15px"),
                                        rx.text(
                                            AppState.ai_analysis_result,
                                            size="4",
                                            color="#333333",
                                            line_height="1.8",
                                            white_space="pre-wrap",
                                        ),
                                        spacing="2",
                                    ),
                                    width="100%",
                                    background="white",
                                    border="1px solid rgba(0,0,0,0.1)",
                                    box_shadow="0 4px 12px rgba(0,0,0,0.1)",
                                    padding="30px",
                                    border_radius="16px",
                                ),
                            ),
                            
                            # AI 탄소 저감 제안 카드
                            rx.cond(
                                AppState.ai_suggestions.length() > 0,
                                rx.card(
                                    rx.vstack(
                                        rx.heading("💡 AI 탄소 저감 제안", size="6", color="#333333", margin_bottom="15px"),
                                        rx.vstack(
                                            rx.foreach(
                                                AppState.ai_suggestions,
                                                lambda suggestion: rx.box(
                                                    rx.text(
                                                        suggestion,
                                                        size="4",
                                                        color="#333333",
                                                        line_height="1.8",
                                                        white_space="pre-wrap",
                                                    ),
                                                    padding="15px",
                                                    border="1px solid rgba(0,0,0,0.1)",
                                                    border_radius="8px",
                                                    background="rgba(77, 171, 117, 0.05)",
                                                    width="100%",
                                                    margin_bottom="10px",
                                                ),
                                            ),
                                            spacing="2",
                                            width="100%",
                                        ),
                                        spacing="3",
                                    ),
                                    width="100%",
                                    background="white",
                                    border="1px solid rgba(0,0,0,0.1)",
                                    box_shadow="0 4px 12px rgba(0,0,0,0.1)",
                                    padding="30px",
                                    border_radius="16px",
                                ),
                            ),
                            
                            spacing="4",
                            width="100%",
                            align="stretch",
                            margin_bottom="30px",
                        ),

                        # 정책/혜택 추천 카드
                        rx.cond(
                            AppState.ai_alternatives.length() > 0,
                            rx.card(
                                rx.vstack(
                                    rx.heading("📋 정책/혜택 추천", size="6", color="#333333", margin_bottom="15px"),
                                    rx.vstack(
                                        rx.foreach(
                                            AppState.ai_alternatives,
                                            lambda alt: rx.box(
                                                rx.vstack(
                                                    rx.text(alt["current"], size="4", color="#333333", font_weight="bold"),
                                                    rx.cond(
                                                        alt["alternative"] != "",
                                                        rx.text(alt["alternative"], size="5", color="gray.600", font_weight="bold", margin_top="5px"),
                                                    ),
                                                    rx.cond(
                                                        alt["impact"] != "",
                                                        rx.link(
                                                            "자세히 보기",
                                                            href=alt["impact"],
                                                            is_external=True,
                                                            color="#4DAB75",
                                                            underline="always",
                                                            size="3",
                                                            margin_top="5px",
                                                        ),
                                                    ),
                                                    spacing="1",
                                                ),
                                                padding="15px",
                                                border="1px solid rgba(0,0,0,0.1)",
                                                border_radius="8px",
                                                background="rgba(77, 171, 117, 0.05)",
                                                width="100%",
                                                margin_bottom="10px",
                                            ),
                                        ),
                                        spacing="2",
                                        width="100%",
                                    ),
                                    spacing="3",
                                ),
                                width="100%",
                                background="white",
                                border="1px solid rgba(0,0,0,0.1)",
                                box_shadow="0 4px 12px rgba(0,0,0,0.1)",
                                padding="30px",
                                border_radius="16px",
                                margin_bottom="30px",
                            ),
                        ),

                        # 하단 버튼
                        rx.card(
                            rx.hstack(
                                rx.button(
                                    "💾 저장하기",
                                    on_click=AppState.save_carbon_log_to_db,
                                    is_disabled=rx.cond(
                                        AppState.is_saving,
                                        True,
                                        ~AppState.is_report_calculated
                                    ),
                                    background_color="#4DAB75",
                                    color="#FFFFFF",
                                    border_radius="25px",
                                    padding="15px 40px",
                                    font_weight="600",
                                    size="3",
                                ),
                                rx.button(
                                    "🏠 처음으로",
                                    on_click=rx.redirect("/intro"),
                                    background_color="transparent",
                                    color="#4DAB75",
                                    border="1px solid rgba(77, 171, 117, 0.3)",
                                    border_radius="25px",
                                    padding="15px 40px",
                                    font_weight="600",
                                    size="3",
                                ),
                                rx.cond(
                                    AppState.save_message != "",
                                    rx.text(
                                        AppState.save_message,
                                        size="4",
                                        color=rx.cond(AppState.is_save_success, "#4DAB75", "#E74C3C"),
                                        font_weight="bold",
                                    ),
                                ),
                                spacing="3",
                                justify="center",
                                width="100%",
                            ),
                            width="100%",
                            background="white",
                            border="1px solid rgba(0,0,0,0.1)",
                            box_shadow="0 4px 12px rgba(0,0,0,0.1)",
                            padding="20px",
                            border_radius="16px",
                        ),

                        spacing="6",
                        width="100%",
                        max_width="1400px",
                        align="center",
                    ),
                    width="100%",
                    z_index="2",
                    padding="40px 20px",
                    display="flex",
                    justify_content="center",
                    margin_top="66vh",
                ),
            ),
            # 리포트 생성 중: 로딩 표시
            rx.box(
                header(),
                rx.center(
                    rx.vstack(
                        rx.text(
                            "리포트를 생성하고 있습니다",
                            size="6",
                            color="#333333",
                            font_weight="bold",
                            margin_bottom="10px",
                        ),
                        rx.text(
                            "잠시만 기다려 주세요...",
                            size="4",
                            color="gray.600",
                            margin_bottom="30px",
                        ),
                        rx.progress(
                            is_indeterminate=True,
                            width="300px",
                            color_scheme="green",
                        ),
                        spacing="4",
                        align="center",
                    ),
                    width="100%",
                    min_height="calc(100vh - 100px)",
                    padding_top="100px",
                ),
                width="100%",
                min_height="100vh",
                background="#F8F9FA",
                on_mount=AppState.on_report_page_load,
            ),
        ),
        # 로그인 안 된 경우
        rx.box(
            header(),
            rx.center(
                rx.vstack(
                    rx.text("로그인이 필요합니다.", size="4", color="red.600", font_weight="bold"),
                    rx.button(
                        "로그인하기",
                        on_click=rx.redirect("/auth"),
                        color_scheme="green",
                        size="3",
                        margin_top="20px",
                    ),
                    spacing="4",
                    align="center",
                ),
                width="100%",
                min_height="calc(100vh - 100px)",
                padding_top="100px",
            ),
            width="100%",
            min_height="100vh",
            background="#F8F9FA",
        ),
    )
