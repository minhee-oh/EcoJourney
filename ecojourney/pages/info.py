# info.py - 정보 글 & OX 퀴즈 페이지

import reflex as rx
from ecojourney.state import AppState


def header() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.button(
                "EcoJourney",
                on_click=rx.redirect("/"),
                background_color="transparent",
                color="white",
                font_size="1.2em",
                font_weight="bold",
                padding="0",
                border="none",
                border_radius="8px",
                cursor="pointer",
            ),
            rx.hstack(
                rx.button(
                    "정보글",
                    on_click=rx.redirect("/info"),
                    background_color="rgba(255, 255, 255, 0.2)",
                    color="white",
                    border="1px solid rgba(255, 255, 255, 0.3)",
                    border_radius="16px",
                    padding="6px 14px",
                ),
                rx.button(
                    "대결",
                    on_click=rx.redirect("/battle"),
                    background_color="rgba(255, 255, 255, 0.2)",
                    color="white",
                    border="1px solid rgba(255, 255, 255, 0.3)",
                    border_radius="16px",
                    padding="6px 14px",
                ),
                rx.button(
                    "랭킹",
                    on_click=rx.redirect("/ranking"),
                    background_color="rgba(255, 255, 255, 0.2)",
                    color="white",
                    border="1px solid rgba(255, 255, 255, 0.3)",
                    border_radius="16px",
                    padding="6px 14px",
                ),
                rx.button(
                    "마이페이지",
                    on_click=rx.redirect("/mypage"),
                    background_color="rgba(255, 255, 255, 0.2)",
                    color="white",
                    border="1px solid rgba(255, 255, 255, 0.3)",
                    border_radius="16px",
                    padding="6px 14px",
                ),
                spacing="3",
                align="center",
            ),
            justify="between",
            align="center",
            padding="12px 20px",
        ),
        width="100%",
        position="relative",
        z_index="10",
    )


def info_card(title: str, description: str, on_read):
    return rx.card(
        rx.vstack(
            rx.heading(title, size="5", color="white"),
            rx.text(description, color="gray.300", size="3"),
            rx.button(
                "읽음 처리",
                on_click=on_read,
                color_scheme="blue",
                size="3",
                width="150px",
            ),
            spacing="3",
            align="start",
        ),
        width="100%",
        background="rgba(255, 255, 255, 0.08)",
        border="1px solid rgba(255, 255, 255, 0.15)",
    )


def quiz_card():
    return rx.card(
        rx.vstack(
            rx.heading("OX 퀴즈", size="5", color="white"),
            rx.text("지구 온난화를 막기 위해서는 일회용품 사용을 줄여야 한다. (O/X)", color="gray.300"),
            rx.hstack(
                rx.button("O", color_scheme="green", on_click=AppState.complete_daily_quiz_o),
                rx.button("X", color_scheme="red", on_click=AppState.complete_daily_quiz_x),
                spacing="3",
            ),
            spacing="3",
            align="start",
        ),
        width="100%",
        background="rgba(255, 255, 255, 0.08)",
        border="1px solid rgba(255, 255, 255, 0.15)",
    )


def info_page() -> rx.Component:
    return rx.box(
        header(),
        rx.vstack(
            rx.heading("정보 글 & 챌린지", size="8", color="white", margin_bottom="10px"),
            rx.text(
                "정보 글을 읽고 OX 퀴즈를 풀어 일일 챌린지를 완료하세요!",
                color="gray.200",
                size="3",
                margin_bottom="15px",
            ),
            rx.grid(
                info_card(
                    "탄소 중립이란?",
                    "인류 활동으로 발생한 온실가스 배출량을 줄이고, 남은 부분은 흡수·제거하여 순 배출량을 0으로 만드는 것.",
                    AppState.complete_daily_info,
                ),
                info_card(
                    "재생에너지의 필요성",
                    "태양광·풍력 같은 재생에너지는 화석연료 의존을 낮추고 온실가스 배출을 크게 줄입니다.",
                    AppState.complete_daily_info,
                ),
                columns={"base": "1", "md": "2"},
                spacing="4",
                width="100%",
            ),
            quiz_card(),
            rx.cond(
                AppState.challenge_message != "",
                rx.callout(
                    AppState.challenge_message,
                    icon="info",
                    color_scheme="green",
                    width="100%",
                ),
            ),
            spacing="5",
            width="100%",
            max_width="900px",
        ),
        width="100%",
        min_height="100vh",
        background="linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #111827 100%)",
        padding="30px 20px",
    )

