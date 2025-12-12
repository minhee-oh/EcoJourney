# mypage.py - 마이페이지

import reflex as rx
from ecojourney.state import AppState
from typing import Dict, Any

def header() -> rx.Component:
    """공통 헤더"""
    return rx.box(
        rx.hstack(
            rx.button(
                "EcoJourney",
                on_click=rx.redirect("/"),
                background_color="transparent",
                color="white",
                font_size="1.5em",
                font_weight="bold",
                padding="0",
                border="none",
                border_radius="8px",
                cursor="pointer",
            ),
            rx.cond(
                AppState.is_logged_in,
                rx.hstack(
                    rx.button(
                        "정보글",
                        on_click=rx.redirect("/info"),
                        background_color="rgba(255, 255, 255, 0.2)",
                        color="white",
                        border="1px solid rgba(255, 255, 255, 0.3)",
                        border_radius="20px",
                        padding="8px 20px",
                        _hover={
                            "background_color": "rgba(255, 255, 255, 0.3)",
                        },
                    ),
                    rx.button(
                        "대결",
                        on_click=rx.redirect("/battle"),
                        background_color="rgba(255, 255, 255, 0.2)",
                        color="white",
                        border="1px solid rgba(255, 255, 255, 0.3)",
                        border_radius="20px",
                        padding="8px 20px",
                        _hover={
                            "background_color": "rgba(255, 255, 255, 0.3)",
                        },
                    ),
                    rx.button(
                        "랭킹",
                        on_click=rx.redirect("/ranking"),
                        background_color="rgba(255, 255, 255, 0.2)",
                        color="white",
                        border="1px solid rgba(255, 255, 255, 0.3)",
                        border_radius="20px",
                        padding="8px 20px",
                        _hover={
                            "background_color": "rgba(255, 255, 255, 0.3)",
                        },
                    ),
                    rx.text(
                        f"{AppState.current_user_id}님",
                        color="white",
                        font_size="1em",
                        margin_right="10px",
                    ),
                    rx.button(
                        "로그아웃",
                        on_click=AppState.logout,
                        background_color="rgba(255, 255, 255, 0.2)",
                        color="white",
                        border="1px solid rgba(255, 255, 255, 0.3)",
                        border_radius="20px",
                        padding="8px 20px",
                        _hover={
                            "background_color": "rgba(255, 255, 255, 0.3)",
                        },
                    ),
                    spacing="3",
                    align="center",
                ),
                rx.button(
                    "로그인",
                    on_click=rx.redirect("/auth"),
                    background_color="rgba(255, 255, 255, 0.2)",
                    color="white",
                    border="1px solid rgba(255, 255, 255, 0.3)",
                    border_radius="20px",
                    padding="8px 20px",
                    _hover={
                        "background_color": "rgba(255, 255, 255, 0.3)",
                    },
                ),
            ),
            justify="between",
            align="center",
            padding="1em 2em",
        ),
        width="100%",
        position="relative",
        z_index="10",
        background_color="transparent",
    )

def mypage_page() -> rx.Component:
    """마이페이지 컴포넌트"""
    # 페이지 로드 시 통계 데이터 로드
    return rx.center(
        rx.vstack(
            header(),
            
            rx.cond(
                AppState.is_logged_in,
                rx.vstack(
                    # 페이지 제목
                    rx.heading("📊 마이페이지", size="8", color="white", margin_bottom="30px"),
                    
                    # 포인트 섹션
                    rx.box(
                        rx.vstack(
                            rx.heading("💰 내 포인트", size="6", color="white", margin_bottom="10px"),
                            rx.text(
                                f"{AppState.current_user_points:,}점",
                                size="9",
                                color="yellow.300",
                                font_weight="bold",
                            ),
                            rx.text(
                                f"단과대: {AppState.current_user_college}",
                                size="3",
                                color="gray.300",
                                margin_top="10px",
                            ),
                            spacing="2",
                            align="center",
                        ),
                        padding="30px",
                        border_radius="16px",
                        background="linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                        width="100%",
                        max_width="600px",
                        margin_bottom="30px",
                    ),
                    
                    # 포인트 획득 내역 섹션
                    rx.box(
                        rx.vstack(
                            rx.heading("📅 포인트 획득 내역", size="6", color="white", margin_bottom="20px"),
                            rx.cond(
                                AppState.points_log.length() > 0,
                                rx.vstack(
                                    rx.foreach(
                                        AppState.points_log,
                                        lambda log: rx.hstack(
                                            rx.vstack(
                                                rx.text(
                                                    log["date"],
                                                    color="white",
                                                    size="4",
                                                    font_weight="bold",
                                                ),
                                                rx.text(
                                                    log.get("description", ""),
                                                    color="gray.300",
                                                    size="3",
                                                ),
                                                spacing="1",
                                                align="start",
                                                width="60%",
                                            ),
                                            rx.text(
                                                f"+{log['points']} 포인트",
                                                color="yellow.300",
                                                size="4",
                                                font_weight="bold",
                                            ),
                                            spacing="4",
                                            justify="between",
                                            width="100%",
                                            padding="10px",
                                            border_radius="8px",
                                            background="rgba(255, 255, 255, 0.1)",
                                            margin_bottom="8px",
                                        ),
                                    ),
                                    spacing="2",
                                    width="100%",
                                ),
                                rx.text(
                                    "아직 획득한 포인트가 없습니다.",
                                    color="gray.400",
                                    size="3",
                                ),
                            ),
                            spacing="3",
                        ),
                        padding="30px",
                        border_radius="16px",
                        background="rgba(0, 0, 0, 0.3)",
                        width="100%",
                        max_width="600px",
                        margin_bottom="30px",
                    ),
                    
                    # 마일리지 환산 섹션
                    rx.box(
                        rx.vstack(
                            rx.heading("💳 비컴 마일리지 환산", size="6", color="white", margin_bottom="20px"),
                            rx.text(
                                "포인트 1000점당 비컴 마일리지 10점으로 환산됩니다.",
                                color="gray.300",
                                size="3",
                                margin_bottom="15px",
                            ),
                            rx.text(
                                "최소 1000점 이상부터 환산 신청이 가능합니다. (1000점 단위로만 입력 가능)",
                                color="gray.400",
                                size="2",
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
                                    color="white",
                                    border="1px solid rgba(255, 255, 255, 0.3)",
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
                                    color="red.300",
                                    size="3",
                                    margin_top="10px",
                                ),
                                rx.text("", display="none"),
                            ),
                            rx.cond(
                                AppState.mileage_request_points >= 1000,
                                rx.text(
                                    f"환산 예상 마일리지: {(AppState.mileage_request_points // 1000) * 10}점",
                                    color="green.300",
                                    size="3",
                                    font_weight="bold",
                                    margin_top="10px",
                                ),
                                rx.text("", display="none"),
                            ),
                            spacing="3",
                        ),
                        padding="30px",
                        border_radius="16px",
                        background="rgba(0, 0, 0, 0.3)",
                        width="100%",
                        max_width="600px",
                        margin_bottom="30px",
                    ),
                    
                    # 마일리지 환산 내역 섹션
                    rx.box(
                        rx.vstack(
                            rx.heading("📋 마일리지 환산 내역", size="6", color="white", margin_bottom="20px"),
                            rx.cond(
                                AppState.mileage_conversion_logs.length() > 0,
                                rx.vstack(
                                    rx.foreach(
                                        AppState.mileage_conversion_logs,
                                        lambda log: rx.hstack(
                                            rx.vstack(
                                                rx.text(
                                                    log["date"],
                                                    color="white",
                                                    size="3",
                                                    font_weight="bold",
                                                ),
                                                rx.text(
                                                    f"-{log['request_points']} 포인트 → +{log['converted_mileage']} 마일리지",
                                                    color="green.300",
                                                    size="4",
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
                                            background="rgba(255, 255, 255, 0.1)",
                                            margin_bottom="8px",
                                        ),
                                    ),
                                    spacing="2",
                                    width="100%",
                                ),
                                rx.text(
                                    "아직 환산 내역이 없습니다.",
                                    color="gray.400",
                                    size="3",
                                ),
                            ),
                            spacing="3",
                        ),
                        padding="30px",
                        border_radius="16px",
                        background="rgba(0, 0, 0, 0.3)",
                        width="100%",
                        max_width="600px",
                        margin_bottom="30px",
                    ),
                    
                    # 챌린지 진행률 섹션
                    rx.box(
                        rx.vstack(
                            rx.heading("🎯 참여 중인 챌린지", size="6", color="white", margin_bottom="20px"),
                            rx.cond(
                                AppState.user_challenge_progress.length() > 0,
                                rx.foreach(
                                    AppState.user_challenge_progress,
                                    lambda progress: rx.box(
                                        rx.vstack(
                                            rx.hstack(
                                                rx.text(
                                                    progress["title"],
                                                    font_weight="bold",
                                                    color="white",
                                                    size="4",
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
                                                color="gray.300",
                                                size="3",
                                            ),
                                            rx.progress(
                                                value=progress["progress_percent"],
                                                width="100%",
                                                color_scheme="green",
                                                margin_top="10px",
                                            ),
                                            rx.text(
                                                f"보상: {progress['reward_points']}점",
                                                color="yellow.300",
                                                size="2",
                                                margin_top="5px",
                                            ),
                                            spacing="2",
                                        ),
                                        padding="20px",
                                        border_radius="12px",
                                        background="rgba(255, 255, 255, 0.1)",
                                        border="1px solid rgba(255, 255, 255, 0.2)",
                                        margin_bottom="15px",
                                        width="100%",
                                    ),
                                ),
                                rx.text(
                                    "참여 중인 챌린지가 없습니다.",
                                    color="gray.400",
                                    size="3",
                                ),
                            ),
                            spacing="3",
                        ),
                        padding="30px",
                        border_radius="16px",
                        background="rgba(0, 0, 0, 0.3)",
                        width="100%",
                        max_width="600px",
                        margin_bottom="30px",
                    ),
                    
                    # 대시보드 통계 섹션
                    rx.box(
                        rx.vstack(
                            rx.heading("📊 탄소 배출 대시보드", size="6", color="white", margin_bottom="20px"),
                            rx.cond(
                                AppState.carbon_total_logs > 0,
                                rx.vstack(
                                    # 요약 카드
                                    rx.hstack(
                                        rx.box(
                                            rx.vstack(
                                                rx.text("이번주 총 배출량", color="gray.300", size="2"),
                                                rx.text(
                                                    f"{AppState.weekly_emission}kg",
                                                    color="white",
                                                    size="6",
                                                    font_weight="bold",
                                                ),
                                                align="center",
                                                spacing="1",
                                            ),
                                            padding="20px",
                                            border_radius="12px",
                                            background="rgba(255, 255, 255, 0.1)",
                                            flex="1",
                                        ),
                                        rx.box(
                                            rx.vstack(
                                                rx.text("한달 총 배출량", color="gray.300", size="2"),
                                                rx.text(
                                                    f"{AppState.monthly_emission}kg",
                                                    color="white",
                                                    size="6",
                                                    font_weight="bold",
                                                ),
                                                align="center",
                                                spacing="1",
                                            ),
                                            padding="20px",
                                            border_radius="12px",
                                            background="rgba(255, 255, 255, 0.1)",
                                            flex="1",
                                        ),
                                        rx.box(
                                            rx.vstack(
                                                rx.text("총 기록일", color="gray.300", size="2"),
                                                rx.text(
                                                    f"{AppState.carbon_total_logs}일",
                                                    color="white",
                                                    size="6",
                                                    font_weight="bold",
                                                ),
                                                align="center",
                                                spacing="1",
                                            ),
                                            padding="20px",
                                            border_radius="12px",
                                            background="rgba(255, 255, 255, 0.1)",
                                            flex="1",
                                        ),
                                        spacing="4",
                                        width="100%",
                                    ),
                                    
                                    rx.divider(margin_y="20px"),
                                    
                                    # 이번주 그래프
                                    rx.box(
                                        rx.vstack(
                                            rx.heading("📅 이번주 일별 배출량", size="5", color="white", margin_bottom="15px"),
                                            rx.cond(
                                                AppState.weekly_daily_data.length() > 0,
                                                rx.vstack(
                                                    # 막대 그래프
                                                    rx.hstack(
                                                        rx.foreach(
                                                            AppState.weekly_daily_data,
                                                            lambda day_data: rx.vstack(
                                                                rx.text(
                                                                    day_data["day"],
                                                                    color="gray.300",
                                                                    size="2",
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
                                                                        background="rgba(255, 255, 255, 0.1)",
                                                                        border_radius="4px 4px 0 0",
                                                                        min_height="4px",
                                                                    ),
                                                                ),
                                                                rx.text(
                                                                    f"{day_data['emission']}kg",
                                                                    color="white",
                                                                    size="1",
                                                                    margin_top="5px",
                                                                ),
                                                                spacing="1",
                                                                align="center",
                                                                width="50px",
                                                            ),
                                                        ),
                                                        spacing="2",
                                                        justify="between",
                                                        align="end",
                                                        width="100%",
                                                        height="250px",
                                                        padding="10px",
                                                    ),
                                                    spacing="2",
                                                ),
                                                rx.text("이번주 데이터가 없습니다.", color="gray.400", size="3"),
                                            ),
                                            spacing="2",
                                        ),
                                        padding="20px",
                                        border_radius="12px",
                                        background="rgba(0, 0, 0, 0.2)",
                                        width="100%",
                                        margin_bottom="20px",
                                    ),
                                    
                                    # 한달 그래프
                                    rx.box(
                                        rx.vstack(
                                            rx.heading("📅 최근 30일 일별 배출량", size="5", color="white", margin_bottom="15px"),
                                            rx.cond(
                                                AppState.monthly_daily_data.length() > 0,
                                                rx.vstack(
                                                    # 막대 그래프 (스크롤 가능)
                                                    rx.box(
                                                        rx.hstack(
                                                            rx.foreach(
                                                                AppState.monthly_daily_data,
                                                                lambda day_data: rx.vstack(
                                                                    rx.text(
                                                                        day_data["month_day"],
                                                                        color="gray.300",
                                                                        size="1",
                                                                        font_weight="bold",
                                                                        transform="rotate(-45deg)",
                                                                        white_space="nowrap",
                                                                    ),
                                                                    rx.cond(
                                                                        day_data["has_emission"],
                                                                        rx.box(
                                                                            width="8px",
                                                                            height=f"{day_data['height']}px",
                                                                            background="linear-gradient(to top, #2196F3, #64B5F6)",
                                                                            border_radius="4px 4px 0 0",
                                                                            min_height="2px",
                                                                            transition="all 0.3s",
                                                                        ),
                                                                        rx.box(
                                                                            width="8px",
                                                                            height="2px",
                                                                            background="rgba(255, 255, 255, 0.1)",
                                                                            border_radius="4px 4px 0 0",
                                                                            min_height="2px",
                                                                        ),
                                                                    ),
                                                                    spacing="1",
                                                                    align="center",
                                                                    width="12px",
                                                                ),
                                                            ),
                                                            spacing="1",
                                                            justify="between",
                                                            align="end",
                                                            width="100%",
                                                            height="200px",
                                                            padding="10px",
                                                        ),
                                                        overflow_x="auto",
                                                        width="100%",
                                                    ),
                                                    spacing="2",
                                                ),
                                                rx.text("한달 데이터가 없습니다.", color="gray.400", size="3"),
                                            ),
                                            spacing="2",
                                        ),
                                        padding="20px",
                                        border_radius="12px",
                                        background="rgba(0, 0, 0, 0.2)",
                                        width="100%",
                                    ),
                                    
                                    spacing="3",
                                ),
                                rx.text(
                                    "아직 기록된 데이터가 없습니다.",
                                    color="gray.400",
                                    size="3",
                                ),
                            ),
                            spacing="3",
                        ),
                        padding="30px",
                        border_radius="16px",
                        background="rgba(0, 0, 0, 0.3)",
                        width="100%",
                        max_width="800px",
                        margin_bottom="30px",
                    ),
                    
                    # 새로고침 버튼
                    rx.button(
                        "🔄 통계 새로고침",
                        on_click=AppState.load_mypage_data,
                        color_scheme="blue",
                        size="3",
                        margin_bottom="20px",
                    ),
                    
                    spacing="4",
                    align="center",
                    width="100%",
                    max_width="800px",
                    padding="40px",
                ),
                rx.vstack(
                    rx.heading("로그인이 필요합니다", size="6", color="white"),
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
            ),
            
            spacing="4",
            align="center",
            width="100%",
            min_height="100vh",
            padding="20px",
            background="linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        ),
        width="100%",
        min_height="100vh",
    )

