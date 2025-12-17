"""
공통 헤더 컴포넌트
모든 페이지에서 동일한 헤더를 사용하기 위한 공통 컴포넌트
"""

import reflex as rx
from ..states import AppState


def header() -> rx.Component:
    """공통 상단 헤더 컴포넌트"""
    return rx.box(
        rx.hstack(
            # 로고 버튼
            rx.button(
                "ECOJOURNEY",
                on_click=rx.redirect("/"),
                background_color="transparent",
                color="#FFFFFF",
                font_size="1.5em",
                font_weight="bold",
                padding="0",
                border="none",
                border_radius="8px",
                cursor="pointer",
            ),
            # 로그인 상태에 따른 메뉴
            rx.cond(
                AppState.is_logged_in,
                rx.hstack(
                    rx.button(
                        "챌린지",
                        on_click=rx.redirect("/info"),
                        background_color="transparent",
                        color="#FFFFFF",
                        border="none",
                        border_radius="25px",
                        padding="8px 20px",
                        font_weight="500",
                        _hover={"border": "1px solid #FFFFFF"},
                    ),
                    rx.button(
                        "배틀",
                        on_click=rx.redirect("/battle"),
                        background_color="transparent",
                        color="#FFFFFF",
                        border="none",
                        border_radius="25px",
                        padding="8px 20px",
                        font_weight="500",
                        _hover={"border": "1px solid #FFFFFF"},
                    ),
                    rx.button(
                        "랭킹",
                        on_click=rx.redirect("/ranking"),
                        background_color="transparent",
                        color="#FFFFFF",
                        border="none",
                        border_radius="25px",
                        padding="8px 20px",
                        font_weight="500",
                        _hover={"border": "1px solid #FFFFFF"},
                    ),
                    rx.button(
                        "리포트",
                        on_click=rx.redirect("/intro"),
                        background_color="transparent",
                        color="#FFFFFF",
                        border="none",
                        border_radius="25px",
                        padding="8px 20px",
                        font_weight="500",
                        _hover={"border": "1px solid #FFFFFF"},
                    ),
                    rx.button(
                        "마이페이지",
                        on_click=rx.redirect("/mypage"),
                        background_color="transparent",
                        color="#FFFFFF",
                        border="none",
                        border_radius="25px",
                        padding="8px 20px",
                        font_weight="500",
                        _hover={"border": "1px solid #FFFFFF"},
                    ),
                    # 닉네임 표시 (닉네임이 있으면 닉네임, 없으면 학번)
                    rx.cond(
                        AppState.current_user_nickname != "",
                        rx.text(
                            f"{AppState.current_user_nickname}님",
                            color="#FFFFFF",
                            font_size="1em",
                            margin_right="10px",
                        ),
                        rx.text(
                            f"{AppState.current_user_id}님",
                            color="#FFFFFF",
                            font_size="1em",
                            margin_right="10px",
                        ),
                    ),
                    rx.button(
                        "로그아웃",
                        on_click=AppState.logout,
                        background_color="#FFFFFF",
                        color="#4DAB75",
                        border="none",
                        border_radius="25px",
                        padding="8px 20px",
                        font_weight="600",
                        _hover={"opacity": "0.9"},
                    ),
                    spacing="3",
                    align="center",
                ),
                rx.button(
                    "로그인",
                    on_click=rx.redirect("/auth"),
                    background_color="#FFFFFF",
                    color="#4DAB75",
                    border="none",
                    border_radius="25px",
                    padding="8px 20px",
                    font_weight="600",
                    _hover={"opacity": "0.9"},
                ),
            ),
            justify="between",
            align="center",
            padding="1.5em 3em",
        ),
        width="100%",
        position="fixed",
        top="0",
        left="0",
        z_index="1000",
        background_color="#4DAB75",
        border_bottom="1px solid rgba(255, 255, 255, 0.1)",
    )


def footer_bar() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.hstack(
                rx.text("Powered by ", color="gray.700", font_size="0.85em"),
                rx.link(
                    "Google AI",
                    href="https://ai.google.dev",
                    is_external=True,
                    color="#4DAB75",
                    font_size="0.85em",
                    font_weight="600",
                    _hover={"text_decoration": "underline"},
                ),
                spacing="1",
                align="center",
                wrap="wrap",
            ),
            rx.text("·", color="gray.500", font_size="0.85em"),
            rx.hstack(
                rx.text("Carbon data provided by ", color="gray.700", font_size="0.85em"),
                rx.link(
                    "Climatiq",
                    href="https://www.climatiq.io",
                    is_external=True,
                    color="#4DAB75",
                    font_size="0.85em",
                    font_weight="600",
                    _hover={"text_decoration": "underline"},
                ),
                spacing="1",
                align="center",
                wrap="wrap",
            ),
            rx.spacer(),
            rx.text("© 2025 EcoJourney", color="gray.600", font_size="0.85em"),
            width="100%",
            align="center",
            padding="6px 16px",
        ),
        width="100%",
        position="fixed",
        bottom="0",
        left="0",
        z_index="900",
        background_color="rgba(255, 255, 255, 0.85)",
        backdrop_filter="blur(10px)",
        border_top="1px solid rgba(0, 0, 0, 0.06)",
    )


