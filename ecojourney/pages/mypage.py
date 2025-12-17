# mypage.py - 마이페이지 (대시보드 디자인)

import reflex as rx
from ..states import AppState
from .common_header import header, footer_bar
import json

# fade-in 애니메이션 CSS
FADEIN_STYLE = {
    "opacity": 0,
    "animation": "fadeIn 0.6s ease forwards",
}

FADEIN_CSS = """
<style>
@keyframes fadeIn {
    0% {
        opacity: 0;
        transform: translateY(10px);
    }
    100% {
        opacity: 1;
        transform: translateY(0);
    }
}
</style>
"""


def mypage_page() -> rx.Component:
    """마이페이지 컴포넌트 (대시보드 디자인)"""
    return rx.cond(
        AppState.is_logged_in,
        rx.box(
            header(),
            footer_bar(),
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
                                "마이페이지",
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
                                "내 활동 현황과 통계를 한눈에 확인하세요!",
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
                            rx.vstack(
                                rx.text(
                                    "📊",
                                    font_size="8em",
                                    style={
                                        "opacity": 0,
                                        "transform": "translateY(20px)",
                                        "animation": "fadeInUp 0.8s ease forwards",
                                        "animation-delay": "0.2s",
                                    },
                                ),
                                spacing="2",
                                align="center",
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

                # 실제 콘텐츠
                rx.box(
                    rx.vstack(
                        # 상단 주요 통계 카드 그리드
                        rx.box(
                            rx.hstack(
                                # 포인트 카드
                                rx.card(
                                    rx.vstack(
                                        rx.text("💰 내 포인트", color="gray.600", size="4", font_weight="bold"),
                                        rx.text(
                                            f"{AppState.current_user_points:,}점",
                                            size="8",
                                            color="#4DAB75",
                                            font_weight="bold",
                                        ),
                                        rx.text(
                                            f"단과대: {AppState.current_user_college}",
                                            size="4",
                                            color="gray.600",
                                            font_weight="bold",
                                            margin_top="10px",
                                        ),
                                        spacing="2",
                                        align="center",
                                    ),
                                    width="100%",
                                    background="white",
                                    border="1px solid rgba(0,0,0,0.1)",
                                    box_shadow="0 4px 12px rgba(0,0,0,0.1)",
                                    padding="25px",
                                    border_radius="16px",
                                ),
                                
                                # 이번주 배출량 카드
                                rx.card(
                                    rx.vstack(
                                        rx.text("📅 이번주 배출량", color="gray.600", size="4", font_weight="bold"),
                                        rx.text(
                                            f"{AppState.weekly_emission}kg",
                                            size="8",
                                            color="#2196F3",
                                            font_weight="bold",
                                        ),
                                        spacing="2",
                                        align="center",
                                    ),
                                    width="100%",
                                    background="white",
                                    border="1px solid rgba(0,0,0,0.1)",
                                    box_shadow="0 4px 12px rgba(0,0,0,0.1)",
                                    padding="25px",
                                    border_radius="16px",
                                ),
                                
                                # 한달 배출량 카드
                                rx.card(
                                    rx.vstack(
                                        rx.text("📊 한달 배출량", color="gray.600", size="4", font_weight="bold"),
                                        rx.text(
                                            f"{AppState.monthly_emission}kg",
                                            size="8",
                                            color="#FF9800",
                                            font_weight="bold",
                                        ),
                                        spacing="2",
                                        align="center",
                                    ),
                                    width="100%",
                                    background="white",
                                    border="1px solid rgba(0,0,0,0.1)",
                                    box_shadow="0 4px 12px rgba(0,0,0,0.1)",
                                    padding="25px",
                                    border_radius="16px",
                                ),
                                
                                # 총 기록일 카드
                                rx.card(
                                    rx.vstack(
                                        rx.text("📝 총 기록일", color="gray.600", size="4", font_weight="bold"),
                                        rx.text(
                                            f"{AppState.carbon_total_logs}일",
                                            size="8",
                                            color="#9C27B0",
                                            font_weight="bold",
                                        ),
                                        spacing="2",
                                        align="center",
                                    ),
                                    width="100%",
                                    background="white",
                                    border="1px solid rgba(0,0,0,0.1)",
                                    box_shadow="0 4px 12px rgba(0,0,0,0.1)",
                                    padding="25px",
                                    border_radius="16px",
                                ),
                                
                                spacing="4",
                                width="100%",
                                align="stretch",
                            ),
                            width="100%",
                            margin_bottom="30px",
                        ),

                        # 중간 섹션: 포인트 내역과 챌린지
                        rx.hstack(
                            # 포인트 내역 카드
                            rx.card(
                                rx.vstack(
                                    rx.heading("📅 포인트 변동 내역", size="6", color="#333333", margin_bottom="20px"),
                                    rx.cond(
                                        AppState.displayed_points_log.length() > 0,
                                        rx.vstack(
                                            rx.foreach(
                                                AppState.displayed_points_log,
                                                lambda log: rx.hstack(
                                                    rx.vstack(
                                                        rx.text(
                                                            log["date"],
                                                            color="#333333",
                                                            size="4",
                                                            font_weight="normal",
                                                        ),
                                                        rx.text(
                                                            log.get("description", ""),
                                                            color="gray.600",
                                                            size="5",
                                                            font_weight="normal",
                                                        ),
                                                        spacing="1",
                                                        align="start",
                                                        width="60%",
                                                    ),
                                                    rx.cond(
                                                        log["is_positive"],
                                                        rx.text(
                                                            f"+{log['points']} 포인트",
                                                            color="#4DAB75",
                                                            size="4",
                                                            font_weight="bold",
                                                        ),
                                                        rx.text(
                                                            f"{log['points']} 포인트",
                                                            color="#E74C3C",
                                                            size="4",
                                                            font_weight="bold",
                                                        ),
                                                    ),
                                                    spacing="4",
                                                    justify="between",
                                                    width="100%",
                                                    padding="10px",
                                                    border_radius="8px",
                                                    background=rx.cond(
                                                        log["is_positive"],
                                                        "rgba(77, 171, 117, 0.1)",
                                                        "rgba(231, 76, 60, 0.1)"
                                                    ),
                                                    margin_bottom="8px",
                                                ),
                                            ),
                                            spacing="2",
                                            width="100%",
                                        ),
                                        rx.text(
                                            "아직 포인트 변동 내역이 없습니다.",
                                            color="gray.600",
                                            size="5",
                                            font_weight="bold",
                                        ),
                                    ),
                                    # 더보기 버튼
                                    rx.cond(
                                        AppState.points_log.length() > AppState.points_log_display_limit,
                                        rx.button(
                                            "더보기",
                                            on_click=AppState.load_more_points_log,
                                            color_scheme="green",
                                            variant="outline",
                                            size="3",
                                            width="100%",
                                            margin_top="10px",
                                        ),
                                    ),
                                    spacing="3",
                                ),
                                width="60%",
                                background="white",
                                border="1px solid rgba(0,0,0,0.1)",
                                box_shadow="0 4px 12px rgba(0,0,0,0.1)",
                                padding="30px",
                                border_radius="16px",
                            ),
                            
                            # 챌린지 진행률 카드
                            rx.card(
                                rx.vstack(
                                    rx.heading("🎯 참여 중인 챌린지", size="6", color="#333333", margin_bottom="20px"),
                                    rx.cond(
                                        AppState.user_challenge_progress.length() > 0,
                                        rx.vstack(
                                            rx.foreach(
                                                AppState.user_challenge_progress,
                                                lambda progress: rx.box(
                                                    rx.vstack(
                                                        rx.hstack(
                                                            rx.text(
                                                                progress["title"],
                                                                font_weight="bold",
                                                                color="#333333",
                                                                size="5",
                                                            ),
                                                            rx.cond(
                                                                progress["is_completed"],
                                                                rx.badge("완료", color_scheme="green"),
                                                                rx.badge("진행중", color_scheme="blue"),
                                                            ),
                                                            justify="between",
                                                            width="100%",
                                                        ),
                                                        rx.text(
                                                            f"{progress['current_value']} / {progress['goal_value']}",
                                                            color="gray.600",
                                                            size="5",
                                                            font_weight="bold",
                                                        ),
                                                        rx.progress(
                                                            value=progress["progress_percent"],
                                                            width="100%",
                                                            color_scheme="green",
                                                            margin_top="10px",
                                                        ),
                                                        rx.text(
                                                            f"보상: {progress['reward_points']}점",
                                                            color="#4DAB75",
                                                            size="4",
                                                            font_weight="bold",
                                                            margin_top="5px",
                                                        ),
                                                        spacing="2",
                                                    ),
                                                    padding="20px",
                                                    border_radius="12px",
                                                    background="rgba(77, 171, 117, 0.1)",
                                                    border="1px solid rgba(77, 171, 117, 0.2)",
                                                    margin_bottom="15px",
                                                    width="100%",
                                                ),
                                            ),
                                            spacing="2",
                                            width="100%",
                                        ),
                                        rx.text(
                                            "참여 중인 챌린지가 없습니다.",
                                            color="gray.600",
                                            size="5",
                                            font_weight="bold",
                                        ),
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
                            
                            spacing="4",
                            width="100%",
                            align="stretch",
                            margin_bottom="30px",
                        ),

                        # 하단 섹션: 그래프와 마일리지
                        rx.hstack(
                            # 이번주 그래프 카드
                            rx.card(
                                rx.vstack(
                                    rx.heading("📅 이번주 배출량 그래프", size="6", color="#333333", margin_bottom="20px"),
                                    rx.cond(
                                        AppState.weekly_daily_data.length() > 0,
                                        rx.vstack(
                                            # 막대 그래프 (카드 안에서 가로 기준 가운데 정렬)
                                            rx.hstack(
                                                rx.foreach(
                                                    AppState.weekly_daily_data,
                                                    lambda day_data: rx.vstack(
                                                        rx.text(
                                                            day_data["day"],
                                                            color="gray.600",
                                                            size="4",
                                                            font_weight="bold",
                                                        ),
                                                        rx.cond(
                                                            day_data["has_emission"],
                                                            rx.box(
                                                                width="40px",
                                                                height=f"{day_data['height']}px",
                                                                background="linear-gradient(to top, #4CAF50, #8BC34A)",
                                                                border_radius="4px 4px 0 0",
                                                                min_height="4px",
                                                                transition="all 0.3s",
                                                            ),
                                                            rx.box(
                                                                width="40px",
                                                                height="4px",
                                                                background="rgba(77, 171, 117, 0.1)",
                                                                border_radius="4px 4px 0 0",
                                                                min_height="4px",
                                                            ),
                                                        ),
                                                        rx.text(
                                                            f"{day_data['emission']}kg",
                                                            color="#333333",
                                                            size="3",
                                                            font_weight="bold",
                                                            margin_top="5px",
                                                        ),
                                                        spacing="1",
                                                        align="center",
                                                        width="50px",
                                                    ),
                                                ),
                                                spacing="2",
                                                justify="center",
                                                align="end",
                                                width="100%",
                                                height="250px",
                                                padding="10px",
                                            ),
                                            spacing="2",
                                            align="center",
                                            width="100%",
                                        ),
                                        rx.text("이번주 데이터가 없습니다.", color="gray.600", size="5", font_weight="bold"),
                                    ),
                                    spacing="2",
                                ),
                                width="50%",
                                background="white",
                                border="1px solid rgba(0,0,0,0.1)",
                                box_shadow="0 4px 12px rgba(0,0,0,0.1)",
                                padding="30px",
                                border_radius="16px",
                            ),
                            
                            # 마일리지 환산 카드
                            rx.card(
                                rx.vstack(
                                    rx.heading("💳 마일리지 환산", size="6", color="#333333", margin_bottom="20px"),
                                    rx.text(
                                        "포인트 1000점당 비컴 마일리지 10점으로 환산됩니다.",
                                        color="gray.700",
                                        size="5",
                                        font_weight="normal",
                                        margin_bottom="15px",
                                    ),
                                    rx.text(
                                        "최소 1000점 이상부터 환산 신청이 가능합니다. (1000점 단위로만 입력 가능)",
                                        color="gray.600",
                                        size="4",
                                        font_weight="normal",
                                        margin_bottom="20px",
                                    ),
                                    rx.hstack(
                                        rx.input(
                                            placeholder="환산할 포인트 입력 (최소 1000점, 1000점 단위)",
                                            value=AppState.mileage_request_points,
                                            on_change=AppState.set_mileage_request_points,
                                            type="number",
                                            min=1000,
                                            step=1000,
                                            width="200px",
                                        ),
                                        rx.button(
                                            "환산 신청",
                                            on_click=AppState.request_mileage_conversion,
                                            color_scheme="green",
                                            size="3",
                                            is_disabled=AppState.current_user_points < 1000,
                                        ),
                                        spacing="3",
                                        align="center",
                                        width="100%",
                                        justify="center",
                                    ),
                                    rx.cond(
                                        AppState.mileage_error_message != "",
                                        rx.text(
                                            AppState.mileage_error_message,
                                            color="red.600",
                                            size="5",
                                            margin_top="10px",
                                            font_weight="bold",
                                        ),
                                    ),
                                    rx.cond(
                                        AppState.mileage_request_points >= 1000,
                                        rx.text(
                                            f"환산 예상 마일리지: {(AppState.mileage_request_points // 1000) * 10}점",
                                            color="#4DAB75",
                                            size="5",
                                            font_weight="bold",
                                            margin_top="10px",
                                        ),
                                    ),
                                    rx.divider(margin_y="20px"),
                                    rx.heading("📋 환산 내역", size="5", color="#333333", margin_bottom="15px"),
                                    rx.cond(
                                        AppState.mileage_conversion_logs.length() > 0,
                                        rx.vstack(
                                            rx.foreach(
                                                AppState.mileage_conversion_logs,
                                                lambda log: rx.hstack(
                                                    rx.vstack(
                                                        rx.text(
                                                            log["date"],
                                                            color="#333333",
                                                            size="5",
                                                            font_weight="bold",
                                                        ),
                                                        rx.text(
                                                            f"-{log['request_points']} 포인트 → +{log['converted_mileage']} 마일리지",
                                                            color="#4DAB75",
                                                            size="5",
                                                            font_weight="bold",
                                                        ),
                                                        spacing="1",
                                                        align="start",
                                                    ),
                                                    rx.cond(
                                                        log["status"] == "APPROVED",
                                                        rx.badge(
                                                            "승인완료",
                                                            color_scheme="green",
                                                            size="2",
                                                        ),
                                                        rx.badge(
                                                            log["status"],
                                                            color_scheme="gray",
                                                            size="2",
                                                        ),
                                                    ),
                                                    spacing="4",
                                                    justify="between",
                                                    width="100%",
                                                    padding="15px",
                                                    border_radius="8px",
                                                    background="rgba(77, 171, 117, 0.1)",
                                                    margin_bottom="8px",
                                                ),
                                            ),
                                            spacing="2",
                                            width="100%",
                                        ),
                                        rx.text(
                                            "아직 환산 내역이 없습니다.",
                                            color="gray.600",
                                            size="5",
                                            font_weight="normal",
                                        ),
                                    ),
                                    spacing="3",
                                ),
                                width="50%",
                                background="white",
                                border="1px solid rgba(0,0,0,0.1)",
                                box_shadow="0 4px 12px rgba(0,0,0,0.1)",
                                padding="30px",
                                border_radius="16px",
                            ),
                            
                            spacing="4",
                            width="100%",
                            align="stretch",
                            margin_bottom="30px",
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
        ),
        rx.box(
            header(),
            footer_bar(),
            rx.center(
                rx.vstack(
                    rx.heading("로그인이 필요합니다", size="7", color="white", font_weight="bold"),
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
                min_height="calc(100vh - 80px)",
            ),
            spacing="0",
            width="100%",
            min_height="100vh",
        ),
    )
