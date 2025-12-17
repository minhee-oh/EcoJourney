# food.py

import reflex as rx
from ..states import AppState
from .help_modal import help_icon_button, help_modal
from .common_header import header, footer_bar

# 세부 카테고리 선택 컴포넌트가 누락되어 NameError가 발생해 추가합니다.
def subcategory_selection_section(label: str, options: list, selected_state: list) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.text(label, font_weight="bold", size="4", color="#333"),
            rx.vstack(
                *[
                    rx.checkbox(
                        text,
                        value=text,
                        is_checked=selected_state.contains(text),
                        on_change=lambda checked, t=text: AppState.toggle_food_subcategory(label, t),
                    )
                    for text in options
                ],
                spacing="1",
                align="start",
            ),
            spacing="2",
            align="start",
            padding="12px",
            border="1px solid",
            border_color="gray.200",
            border_radius="10px",
            background="white",
        ),
        width="100%",
    )

FOOD_SUBCATEGORIES = {
    "유제품": ["우유", "치즈", "두유"],
    "밥": ["쌀밥", "잡곡밥", "현미밥", "보리밥", "콩밥", "김밥", "비빔밥불고기", "비빔밥산채", "김치볶음밥"],
    "커피": ["에스프레소", "카페라떼"],  # 한국일보 기준만
    "패스트푸드": ["피자", "햄버거세트", "후라이드치킨"],  # 한국일보 기준만
    "면": ["물냉면", "비빔냉면", "잔치국수", "비빔국수", "해물칼국수"],  # 한국일보 기준만
    "국/찌개": ["된장국", "미역국", "콩나물국", "된장찌개", "김치찌개", "순두부찌개", "설렁탕", "갈비탕", "곰탕"],  # 한국일보 기준만
    "반찬": ["배추김치", "깍두기", "총각김치", "열무김치", "숙주나물", "콩나물무침", "시금치나물", "무생채", "소고기장조림", "멸치조림", "콩자반", "깻잎장아찌", "제육볶음", "오징어볶음", "불고기", "잡채", "고등어구이", "달걀프라이", "달걀찜"],
    "고기": ["소고기구이", "삼겹살구이"],
    "과일": ["딸기", "참외", "수박", "사과", "복숭아", "단감", "포도", "감귤", "키위", "토마토", "방울토마토"],
    # Climatiq API 사용 항목
    "파스타": ["카르보나라", "라자냐", "라비올리", "파스타샐러드"],  # Climatiq API 사용 (완성된 요리만)
}



# =======================================================
# 공통 버튼 UI
# =======================================================

def food_button(label: str, is_selected, on_click):
    """상위 카테고리 선택 버튼"""
    disabled = AppState.food_input_mode

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

def subcategory_checkbox(category: str, subcategory: str, selected_list):
    """세부 카테고리 체크박스"""
    return rx.hstack(
        rx.checkbox(
            checked=selected_list.contains(subcategory),
            on_change=lambda: AppState.toggle_food_subcategory(category, subcategory),
            color_scheme="green",
        ),
        rx.text(
            subcategory,
            font_size="0.95em",
            color="#333333",
        ),
        spacing="2",
        align="center",
        padding="10px 16px",
        border_radius="12px",
        background_color="#FFFFFF",
        border="1px solid #E0E0E0",
        cursor="pointer",
        transition="all 0.2s ease",
    )

# =======================================================
# 입력 필드 UI
# =======================================================

def food_input_field(label: str, value_name: str, unit_name: str, sub_name: str):
    sub_items = FOOD_SUBCATEGORIES.get(label, [])
    has_subcategories = len(sub_items) > 0

    return rx.box(
        rx.hstack(
            rx.text(
                label,
                font_weight="bold",
                min_width="80px",
                color="black",       # ← 여기만 바꾸면 바로 해결됨
            ),
            rx.cond(
                has_subcategories,
                rx.select(
                    items=sub_items,
                    placeholder=f"세부 카테고리 선택",
                    name=sub_name,
                    width="140px",
                    background_color="rgba(255, 255, 255, 0.9)",
                    color="black",
                    border_radius="8px",
                ),
                rx.box(width="140px"),  # 하위 카테고리가 없으면 빈 공간
            ),
            rx.input(
                type="hidden",
                name=unit_name,
                default_value="회",
            ),
            rx.text(
                "회",
                min_width="100px",
                color="black",
                font_weight="bold",
                text_align="center",
            ),
            rx.input(
                placeholder="섭취량/횟수 입력",
                type="number",
                name=value_name,
                width="140px",
                background_color="rgba(255, 255, 255, 0.9)",
                color="black",
                border_radius="8px",
            ),
            spacing="4",
            align="center",
            justify="center",
        ),
        spacing="2",
        align="start",
        width="100%",
        padding="20px",
        border_radius="20px",
        background_color="#FFFFFF",
        border="1px solid #E0E0E0",
        margin_y="12px",
    )

def quantity_input_field(category_key: str, subcategory: str):
    """횟수 입력 필드 (개별 세부 카테고리용)"""
    return rx.box(
        rx.hstack(
            rx.text(
                subcategory,
                font_weight="600",
                min_width="120px",
                color="#333333",
            ),
            rx.input(
                placeholder="횟수 입력",
                type="number",
                name=f"{category_key}_{subcategory}_value",
                width="150px",
                background_color="#FFFFFF",
                color="#333333",
                border_radius="12px",
                border="1px solid #E0E0E0",
                padding="3px 12px",
                _focus={
                    "border": "2px solid #4DAB75",
                    "outline": "none",
                },
                _placeholder={
                    "color": "#999999",
                },
            ),
            rx.text(
                "회",
                min_width="40px",
                color="#333333",
                font_weight="600",
                text_align="center",
            ),
            spacing="4",
            align="center",
            justify="center",
            padding="16px 20px",
            border_radius="16px",
            background_color="#FFFFFF",
            border="1px solid #E0E0E0",
        ),
        display="flex",
        justify_content="center",
        width="100%",
        margin_y="8px",
    )


# =======================================================
# 메인 페이지
# =======================================================

def food_page():
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
                                "식품 🍽️",
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
                                help_icon_button("식품"),
                                style={"pointer_events": "auto"},
                            ),
                            spacing="2",
                            align="center",
                        ),
                        rx.text(
                            "오늘 섭취한 음식을 모두 선택해주세요",
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
                        food_button("유제품", AppState.selected_dairy, AppState.toggle_dairy),
                        food_button("밥", AppState.selected_rice, AppState.toggle_rice),
                        food_button("커피", AppState.selected_coffee, AppState.toggle_coffee),
                        food_button("패스트푸드", AppState.selected_fastfood, AppState.toggle_fastfood),
                        food_button("면", AppState.selected_noodles, AppState.toggle_noodles),
                        food_button("국/찌개", AppState.selected_cooked, AppState.toggle_cooked),
                        food_button("반찬", AppState.selected_side_dish, AppState.toggle_side_dish),
                        food_button("고기", AppState.selected_grilled_meat, AppState.toggle_grilled_meat),
                        food_button("과일", AppState.selected_fruit, AppState.toggle_fruit),
                        food_button("파스타", AppState.selected_pasta, AppState.toggle_pasta),
                        wrap="wrap",
                        justify="center",
                        spacing="3",
                    ),
                    spacing="3",
                ),

                rx.box(height="20px"),

                # ----------------------------------
                # 1단계: 세부 카테고리 선택
                # ----------------------------------
                rx.cond(
                    AppState.food_step == 1,
                    rx.vstack(
                        rx.text(
                            "세부 카테고리를 선택해주세요",
                            color="#333333",
                            font_size="1.25em",
                            font_weight="700",
                            margin_bottom="20px",
                            text_align="center",
                        ),

                        # 유제품 세부 카테고리 선택
                        rx.cond(AppState.show_dairy,
                            subcategory_selection_section("유제품", FOOD_SUBCATEGORIES["유제품"], AppState.selected_dairy_subs)),

                        # 밥 세부 카테고리 선택
                        rx.cond(AppState.show_rice,
                            subcategory_selection_section("밥", FOOD_SUBCATEGORIES["밥"], AppState.selected_rice_subs)),

                        # 커피 세부 카테고리 선택
                        rx.cond(AppState.show_coffee,
                            subcategory_selection_section("커피", FOOD_SUBCATEGORIES["커피"], AppState.selected_coffee_subs)),

                        # 패스트푸드 세부 카테고리 선택
                        rx.cond(AppState.show_fastfood,
                            subcategory_selection_section("패스트푸드", FOOD_SUBCATEGORIES["패스트푸드"], AppState.selected_fastfood_subs)),

                        # 면 세부 카테고리 선택
                        rx.cond(AppState.show_noodles,
                            subcategory_selection_section("면", FOOD_SUBCATEGORIES["면"], AppState.selected_noodles_subs)),

                        # 국/찌개 세부 카테고리 선택
                        rx.cond(AppState.show_cooked,
                            subcategory_selection_section("국/찌개", FOOD_SUBCATEGORIES["국/찌개"], AppState.selected_cooked_subs)),

                        # 반찬 세부 카테고리 선택
                        rx.cond(AppState.show_side_dish,
                            subcategory_selection_section("반찬", FOOD_SUBCATEGORIES["반찬"], AppState.selected_side_dish_subs)),

                        # 고기 세부 카테고리 선택
                        rx.cond(AppState.show_grilled_meat,
                            subcategory_selection_section("고기", FOOD_SUBCATEGORIES["고기"], AppState.selected_grilled_meat_subs)),

                        # 과일 세부 카테고리 선택
                        rx.cond(AppState.show_fruit,
                            subcategory_selection_section("과일", FOOD_SUBCATEGORIES["과일"], AppState.selected_fruit_subs)),

                        # 파스타 세부 카테고리 선택
                        rx.cond(AppState.show_pasta,
                            subcategory_selection_section("파스타", FOOD_SUBCATEGORIES["파스타"], AppState.selected_pasta_subs)),

                        rx.box(height="30px"),

                        # 버튼 영역
                        rx.hstack(
                            # 다시 선택하기 버튼
                            rx.button(
                                "다시 선택하기",
                                type="button",
                                on_click=AppState.reset_food_selection,
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
                                type="button",
                                on_click=AppState.proceed_to_quantity_input,
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
                        spacing="3",
                        padding="20px",
                    ),
                ),

                # ----------------------------------
                # 2단계: 횟수 입력
                # ----------------------------------
                rx.cond(
                    AppState.food_step == 2,
                    rx.form(
                        rx.vstack(
                            rx.text(
                                "섭취 횟수를 입력해주세요",
                                color="#333333",
                                font_size="1.25em",
                                font_weight="700",
                                margin_bottom="20px",
                                text_align="center",
                            ),

                            # 유제품 횟수 입력
                            rx.cond(AppState.show_dairy,
                                rx.vstack(
                                    rx.foreach(
                                        AppState.selected_dairy_subs,
                                        lambda sub: quantity_input_field("dairy", sub)
                                    ),
                                    spacing="2",
                                    width="100%",
                                )),

                            # 밥 횟수 입력
                            rx.cond(AppState.show_rice,
                                rx.vstack(
                                    rx.foreach(
                                        AppState.selected_rice_subs,
                                        lambda sub: quantity_input_field("rice", sub)
                                    ),
                                    spacing="2",
                                    width="100%",
                                )),

                            # 커피 횟수 입력
                            rx.cond(AppState.show_coffee,
                                rx.vstack(
                                    rx.foreach(
                                        AppState.selected_coffee_subs,
                                        lambda sub: quantity_input_field("coffee", sub)
                                    ),
                                    spacing="2",
                                    width="100%",
                                )),

                            # 패스트푸드 횟수 입력
                            rx.cond(AppState.show_fastfood,
                                rx.vstack(
                                    rx.foreach(
                                        AppState.selected_fastfood_subs,
                                        lambda sub: quantity_input_field("fastfood", sub)
                                    ),
                                    spacing="2",
                                    width="100%",
                                )),

                            # 면 횟수 입력
                            rx.cond(AppState.show_noodles,
                                rx.vstack(
                                    rx.foreach(
                                        AppState.selected_noodles_subs,
                                        lambda sub: quantity_input_field("noodles", sub)
                                    ),
                                    spacing="2",
                                    width="100%",
                                )),

                            # 국/찌개 횟수 입력
                            rx.cond(AppState.show_cooked,
                                rx.vstack(
                                    rx.foreach(
                                        AppState.selected_cooked_subs,
                                        lambda sub: quantity_input_field("cooked", sub)
                                    ),
                                    spacing="2",
                                    width="100%",
                                )),

                            # 반찬 횟수 입력
                            rx.cond(AppState.show_side_dish,
                                rx.vstack(
                                    rx.foreach(
                                        AppState.selected_side_dish_subs,
                                        lambda sub: quantity_input_field("side_dish", sub)
                                    ),
                                    spacing="2",
                                    width="100%",
                                )),

                            # 고기 횟수 입력
                            rx.cond(AppState.show_grilled_meat,
                                rx.vstack(
                                    rx.foreach(
                                        AppState.selected_grilled_meat_subs,
                                        lambda sub: quantity_input_field("grilled_meat", sub)
                                    ),
                                    spacing="2",
                                    width="100%",
                                )),

                            # 과일 횟수 입력
                            rx.cond(AppState.show_fruit,
                                rx.vstack(
                                    rx.foreach(
                                        AppState.selected_fruit_subs,
                                        lambda sub: quantity_input_field("fruit", sub)
                                    ),
                                    spacing="2",
                                    width="100%",
                                )),

                            # 파스타 횟수 입력
                            rx.cond(AppState.show_pasta,
                                rx.vstack(
                                    rx.foreach(
                                        AppState.selected_pasta_subs,
                                        lambda sub: quantity_input_field("pasta", sub)
                                    ),
                                    spacing="2",
                                    width="100%",
                                )),

                            rx.box(height="30px"),

                            # 버튼 영역
                            rx.hstack(
                                # 다시 선택하기 버튼
                                rx.button(
                                    "다시 선택하기",
                                    type="button",
                                    on_click=AppState.reset_food_selection,
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
                                # 제출 버튼
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
                            spacing="3",
                            padding="20px",
                        ),
                        on_submit=AppState.handle_food_submit,
                    ),
                ),

                rx.box(height="20px"),

                # ----------------------------------
                # 입력하기 버튼 & 건너뛰기 버튼
                # ----------------------------------
                rx.cond(
                    ~AppState.food_input_mode,
                    rx.hstack(
                        rx.button(
                            "건너뛰기",
                            on_click=rx.redirect("/input/clothing"),
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
                            on_click=AppState.show_food_input_fields,
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
                        max_width="1000px",
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
            help_modal("식품"),
        ),
        rx.box(
            header(),
            footer_bar(),
            rx.center(
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
                width="100%",
                min_height="calc(100vh - 80px)",
            ),
            spacing="0",
            width="100%",
            min_height="100vh",
        ),
    )
