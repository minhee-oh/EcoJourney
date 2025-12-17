# clothing.py

import reflex as rx
from ..states import AppState
from .help_modal import help_icon_button, help_modal
from .common_header import header, footer_bar


# 의류 서브카테고리 옵션 (셀렉트에서 사용)
CLOTHING_SUBCATEGORIES = ["새제품", "빈티지"]


def clothing_button(label: str, is_selected, on_click):
    """의류 카테고리 선택 버튼."""
    return rx.button(
        label,
        on_click=on_click,
        background_color=rx.cond(is_selected, "#4DAB75", "rgba(77, 171, 117, 0.1)"),
        color=rx.cond(is_selected, "white", "#4DAB75"),
        border=rx.cond(is_selected, "2px solid #4DAB75", "1px solid rgba(77, 171, 117, 0.3)"),
        border_radius="30px",
        padding=rx.cond(is_selected, "18px 36px", "16px 32px"),
        font_weight="600",
        font_size="1em",
        box_shadow=rx.cond(
            is_selected,
            "0 4px 20px rgba(77, 171, 117, 0.4)",
            "0 2px 8px rgba(0, 0, 0, 0.1)",
        ),
        transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
        class_name="category-button",
        _hover={
            "background_color": rx.cond(is_selected, "#3d9a66", "rgba(77, 171, 117, 0.25)"),
            "transform": "translateY(-3px) scale(1.02)",
            "box_shadow": "0 8px 30px rgba(77, 171, 117, 0.5)",
        },
        _active={
            "transform": "translateY(0) scale(0.98)",
        },
    )

def clothing_input_field(label: str, value_name: str, unit_name: str, sub_name: str):
    """의류 입력 필드 (개수 + 옵션 선택)"""
    return rx.box(
        rx.hstack(
            rx.text(
                label,
                font_weight="bold",
                min_width="80px",
                color="#333333",
                font_size="1em",
            ),
            rx.select(
                CLOTHING_SUBCATEGORIES,
                placeholder=f"옵션 선택",
                name=sub_name,
                width="130px",
                background_color="#FFFFFF",
                color="#4DAB75",
                border_radius="12px",
                border="1px solid #E0E0E0",
                padding="8px 12px",
                font_size="0.95em",
                font_weight="600",
                _focus={
                    "border": "2px solid #4DAB75",
                    "outline": "none",
                },
            ),
            rx.input(
                placeholder="개수 입력",
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
        max_width="550px",
    )

def clothing_page() -> rx.Component:
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
                                "의류 소비👕",
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
                                help_icon_button("의류"),
                                style={"pointer_events": "auto"},
                            ),
                            spacing="2",
                            align="center",
                        ),
                        rx.text(
                            "오늘 구매한 의류를 모두 선택해주세요",
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
                # ----------------------------------
                # 버튼 선택 영역
                # ----------------------------------
                rx.vstack(
                    rx.hstack(
                        clothing_button("티셔츠", AppState.selected_tshirts, AppState.toggle_tshirts),
                        clothing_button("청바지", AppState.selected_jeans, AppState.toggle_jeans),
                        clothing_button("신발", AppState.selected_shoes, AppState.toggle_shoes),
                        clothing_button("가방/잡화", AppState.selected_acc, AppState.toggle_acc),
                        wrap="wrap",
                        justify="center",
                        spacing="3",
                    ),
                    spacing="3",
                ),

                rx.box(height="20px"),

                # ----------------------------------
                # 입력 필드 렌더링
                # ----------------------------------
                rx.cond(
                    AppState.clothing_input_mode,
                    rx.form(
                        rx.vstack(
                            rx.cond(AppState.show_tshirts,
                                clothing_input_field("티셔츠", "tshirts_value", "tshirts_unit", "tshirts_sub")),
                            rx.cond(AppState.show_jeans,
                                clothing_input_field("청바지", "jeans_value", "jeans_unit", "jeans_sub")),
                            rx.cond(AppState.show_shoes,
                                clothing_input_field("신발", "shoes_value", "shoes_unit", "shoes_sub")),
                            rx.cond(AppState.show_acc,
                                clothing_input_field("가방/잡화", "acc_value", "acc_unit", "acc_sub")),

                            rx.box(height="30px"),

                            # 버튼 영역
                            rx.hstack(
                                # 다시 선택하기 버튼
                                rx.button(
                                    "다시 선택하기",
                                    type="button",
                                    on_click=AppState.reset_clothing_selection,
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
                        on_submit=AppState.handle_clothing_submit,
                    ),
                ),

                rx.box(height="20px"),

                # ----------------------------------
                # 입력하기 버튼 & 건너뛰기 버튼
                # ----------------------------------
                rx.cond(
                    ~AppState.clothing_input_mode,
                    rx.hstack(
                        rx.button(
                            "건너뛰기",
                            on_click=rx.redirect("/input/electricity"),
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
                            on_click=AppState.show_clothing_input_fields,
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
                    padding_top="20px",
                    display="flex",
                    justify_content="center",
                    align_items="flex-start",
                    min_height="calc(100vh - 100px)",
                    margin_top="0",
                ),
            ),
            help_modal("의류"),
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
