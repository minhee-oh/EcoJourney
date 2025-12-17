# electricity.py

import reflex as rx
from ..states import AppState
from .help_modal import help_icon_button, help_modal
from .common_header import header, footer_bar

# =======================================================
# 공통 버튼 UI
# =======================================================

def electricity_button(label: str, is_selected, on_click):
    disabled = AppState.electricity_input_mode

    base = rx.hstack(
        rx.text(label),
        spacing="2",
    )

    selected_bg = rx.cond(disabled, "rgba(77, 171, 117, 0.4)", "#4DAB75")
    default_bg  = rx.cond(disabled, "rgba(77, 171, 117, 0.05)", "rgba(77, 171, 117, 0.1)")

    text_color = rx.cond(is_selected, "#FFFFFF", "#4DAB75")
    cursor_style = rx.cond(disabled, "not-allowed", "pointer")

    return rx.button(
        base,
        on_click=rx.cond(disabled, None, on_click),
        disabled=disabled,
        background_color=rx.cond(is_selected, selected_bg, default_bg),
        color=text_color,
        border_radius="30px",
        padding=rx.cond(is_selected, "18px 36px", "16px 32px"),
        border=rx.cond(is_selected, "2px solid #4DAB75", "1px solid rgba(77, 171, 117, 0.3)"),
        font_size="1em",
        font_weight="600",
        cursor=cursor_style,
        transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
        box_shadow=rx.cond(is_selected, "0 4px 20px rgba(77, 171, 117, 0.4)", "0 2px 8px rgba(0, 0, 0, 0.1)"),
        class_name="category-button",
        _hover=rx.cond(
            disabled,
            {},
            {
                "transform": "translateY(-3px) scale(1.02)",
                "background_color": rx.cond(is_selected, "#3d9a66", "rgba(77, 171, 117, 0.25)"),
                "box_shadow": "0 8px 30px rgba(77, 171, 117, 0.5)",
            }
        ),
        _active=rx.cond(
            disabled,
            {},
            {
                "transform": "translateY(0) scale(0.98)",
            }
        ),
    )


# 입력 필드 UI
def electricity_input_field(label: str, value_name: str):
    return rx.box(
        rx.hstack(
            rx.text(
                label,
                font_weight="bold",
                min_width="80px",
                color="#333333",
                font_size="1em",
            ),
            rx.input(
                placeholder="시간 입력",
                type="number",
                name=value_name,
                width="150px",
                background_color="#FFFFFF",
                color="#333333",
                border_radius="12px",
                border="1px solid #E0E0E0",
                padding="3px 12px",
                font_size="0.95em",
                _focus={
                    "border": "2px solid #4DAB75",
                    "outline": "none",
                },
                _placeholder={
                    "color": "#999999",
                },
            ),
            rx.text(
                "시간",
                min_width="40px",
                color="#333333",
                font_weight="600",
                text_align="center",
            ),
            spacing="4",
            align="center",
            justify="center",
        ),
        padding="20px 24px",
        border_radius="20px",
        background_color="#FFFFFF",
        border="1px solid #E0E0E0",
        margin_y="12px",
        width="100%",
        max_width="500px",
    )


# =======================================================
# 메인 페이지
# =======================================================

def electricity_page():
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
            @keyframes pulse {
                0%, 100% {
                    transform: scale(1);
                }
                50% {
                    transform: scale(1.05);
                }
            }
            @keyframes bounce {
                0%, 100% {
                    transform: translateY(0);
                }
                50% {
                    transform: translateY(-5px);
                }
            }
            .category-button {
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }
            .category-button:hover:not(:disabled) {
                animation: pulse 0.6s ease-in-out;
            }
            .category-button:active:not(:disabled) {
                animation: bounce 0.3s ease-in-out;
            }
            </style>
            """),
            # 배경 레이어 구성
            rx.box(
                # 상단 배경 레이어 + 제목과 설명 (고정)
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.heading(
                                "전기 사용⚡",
                                size="7",
                                color="#333333",
                                margin_bottom="18px",
                                style={
                                    "opacity": 0,
                                    "transform": "translateY(20px)",
                                    "animation": "fadeInUp 0.8s ease forwards",
                                    "animation-delay": "0.1s",
                                    "pointer_events": "none",
                                },
                            ),
                            rx.box(
                                help_icon_button("전기"),
                                style={"pointer_events": "auto"},
                            ),
                            spacing="2",
                            align="center",
                        ),
                        rx.text(
                            "오늘 사용한 냉/난방 기기를 모두 선택해주세요",
                            color="#333333",
                            size="5",
                            font_weight="normal",
                            text_align="center",
                            width="100%",
                            style={
                                "opacity": 0,
                                "transform": "translateY(20px)",
                                "animation": "fadeInUp 1s ease forwards",
                                "animation-delay": "0.25s",
                                "pointer_events": "none",
                            },
                        ),
                        spacing="3",
                        align="center",
                        justify="center",
                        padding_top="40px",
                        padding_bottom="20px",
                    ),
                    width="100%",
                    background="transparent",
                    position="relative",
                    left="0",
                    z_index="10",
                    pointer_events="none",
                ),
                # 실제 콘텐츠
                rx.box(
                    rx.card(
                        rx.vstack(
                # 버튼 선택 영역
                rx.vstack(
                    rx.hstack(
                        electricity_button("냉방기", AppState.selected_ac, AppState.toggle_ac),
                        electricity_button("난방기", AppState.selected_heater, AppState.toggle_heater),
                        wrap="wrap",
                        justify="center",
                        spacing="3",
                    ),
                    spacing="3",
                ),

                rx.box(height="20px"),

                # 입력 필드 렌더링
                rx.cond(
                    AppState.electricity_input_mode,
                    rx.form(
                        rx.vstack(
                            rx.cond(
                                AppState.show_ac,
                                electricity_input_field("냉방기", "ac_value"),
                            ),

                            rx.cond(
                                AppState.show_heater,
                                electricity_input_field("난방기", "heater_value"),
                            ),

                            rx.box(height="30px"),

                            # 버튼 영역
                            rx.hstack(
                                # 다시 선택하기 버튼
                                rx.button(
                                    "다시 선택하기",
                                    type="button",
                                    on_click=AppState.reset_electricity_selection,
                                    color="#4DAB75",
                                    background_color="transparent",
                                    border_radius="30px",
                                    padding="16px 40px",
                                    border="1px solid rgba(77, 171, 117, 0.3)",
                                    font_size="1.05em",
                                    font_weight="600",
                                    cursor="pointer",
                                    transition="all 0.25s ease",
                                    _hover={
                                        "background_color": "rgba(77, 171, 117, 0.05)",
                                        "border": "1px solid #4DAB75",
                                    },
                                ),
                                # 다음 버튼
                                rx.button(
                                    "다음",
                                    type="submit",
                                    color="#FFFFFF",
                                    background_color="#4DAB75",
                                    border_radius="30px",
                                    padding="16px 52px",
                                    border="none",
                                    font_size="1.05em",
                                    font_weight="600",
                                    cursor="pointer",
                                    box_shadow="0 4px 20px rgba(77, 171, 117, 0.3)",
                                    transition="all 0.25s ease",
                                    _hover={
                                        "background_color": "#3d9a66",
                                        "transform": "translateY(-2px)",
                                        "box_shadow": "0 6px 24px rgba(77, 171, 117, 0.5)",
                                    },
                                ),
                                spacing="4",
                                justify="center",
                            ),

                            align="center",
                            width="100%",
                            spacing="2",
                        ),
                        on_submit=AppState.handle_electricity_submit,
                    ),
                ),

                rx.box(height="20px"),

                # 입력하기 버튼 & 건너뛰기 버튼
                rx.cond(
                    ~AppState.electricity_input_mode,
                    rx.hstack(
                        rx.button(
                            "건너뛰기",
                            on_click=rx.redirect("/input/water"),
                            color="#4DAB75",
                            background_color="transparent",
                            border_radius="30px",
                            padding="18px 48px",
                            border="1px solid rgba(77, 171, 117, 0.3)",
                            font_size="1.05em",
                            font_weight="600",
                            cursor="pointer",
                            transition="all 0.25s ease",
                            _hover={
                                "background_color": "rgba(77, 171, 117, 0.05)",
                                "border": "1px solid #4DAB75",
                            },
                        ),
                        rx.button(
                            "입력하기",
                            on_click=AppState.show_electricity_input_fields,
                            color="#FFFFFF",
                            background_color="#4DAB75",
                            border_radius="30px",
                            padding="18px 48px",
                            border="none",
                            font_size="1.05em",
                            font_weight="600",
                            cursor="pointer",
                            box_shadow="0 4px 20px rgba(77, 171, 117, 0.3)",
                            transition="all 0.25s ease",
                            _hover={
                                "background_color": "#3d9a66",
                                "transform": "translateY(-2px)",
                                "box_shadow": "0 6px 24px rgba(77, 171, 117, 0.5)",
                            },
                        ),
                        spacing="4",
                        justify="center",
                    ),
                ),

                            spacing="5",
                            align="center",
                            width="100%",
                        ),
                        width="100%",
                        background="white",
                        border="1px solid rgba(0,0,0,0.1)",
                        box_shadow="0 4px 12px rgba(0,0,0,0.1)",
                        padding="40px",
                        max_width="900px",
                    ),
                    width="100%",
                    z_index="2",
                    padding="40px 20px",
                    display="flex",
                    justify_content="center",
                    align_items="flex-start",
                    min_height="calc(100vh - 100px)",
                    margin_top="0",
                    padding_top="20px",
                ),
            ),
            help_modal("전기"),
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
