# auth.py - 로그인 및 회원가입 페이지

import reflex as rx
from ..states import AppState
from .common_header import footer_bar

def auth_header() -> rx.Component:
    """인증 페이지 전용 헤더"""
    return rx.box(
        rx.hstack(
            # 로고 버튼
            rx.button(
                "ECOJOURNEY",
                on_click=rx.redirect("/"),
                background_color="transparent",
                color="#333333",
                font_size="1.5em",
                font_weight="bold",
                padding="0",
                border="none",
                border_radius="8px",
                cursor="pointer",
            ),
            rx.spacer(),
            # 홈으로 돌아가기 버튼
            rx.button(
                "홈으로",
                on_click=rx.redirect("/"),
                background_color="rgba(77, 171, 117, 0.1)",
                color="#4DAB75",
                border="1px solid rgba(77, 171, 117, 0.3)",
                border_radius="25px",
                padding="8px 20px",
                font_weight="500",
                _hover={"background_color": "rgba(77, 171, 117, 0.2)"},
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
        background_color="rgba(255, 255, 255, 0.9)",
        backdrop_filter="blur(10px)",
    )

def auth_page() -> rx.Component:
    """로그인 및 회원가입 페이지"""
    return rx.box(
        auth_header(),
        footer_bar(),
       
        # Google Fonts 및 스타일링
        rx.html("""
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800&family=Noto+Sans+KR:wght@300;400;600;700;800&display=swap" rel="stylesheet">
        <style>
        * {
            font-family: 'Poppins', 'Noto Sans KR', sans-serif;
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .auth-card {
            animation: fadeInUp 0.6s ease-out;
        }
        </style>
        """),
        
        # 배경 레이어 - 연두색 (화면 전체를 항상 덮도록 고정)
        rx.box(
            width="100%",
            height="100vh",
            background="rgba(144, 238, 144, 0.3)",
            position="fixed",
            top="0",
            left="0",
            z_index="0",
        ),
        
        # 메인 컨텐츠
        rx.center(
            rx.box(
                rx.vstack(
                    
                    
                    # 로그인/회원가입 카드
                    rx.box(
                        rx.tabs.root(
                            rx.tabs.list(
                                rx.tabs.trigger(
                                    "로그인",
                                    value="login",
                                    color="#666666",
                                    _selected={
                                        "color": "#333333",
                                        "border_bottom": "2px solid #4DAB75",
                                    },
                                    font_weight="600",
                                    font_size="1.1em",
                                    padding="12px 30px",
                                ),
                                rx.tabs.trigger(
                                    "회원가입",
                                    value="signup",
                                    color="#666666",
                                    _selected={
                                        "color": "#333333",
                                        "border_bottom": "2px solid #4DAB75",
                                    },
                                    font_weight="600",
                                    font_size="1.1em",
                                    padding="12px 30px",
                                ),
                                justify="center",
                                width="100%",
                            ),
                            rx.tabs.content(
                                # 로그인 폼
                                rx.vstack(
                                    rx.form(
                                        rx.vstack(
                                            rx.input(
                                                placeholder="학번",
                                                name="student_id",
                                                value=AppState.login_student_id,
                                                on_change=AppState.set_login_student_id,
                                                size="3",
                                                width="100%",
                                                background_color="#F8F9FA",
                                                color="#333333",
                                                border_radius="12px",
                                                border="1px solid #E0E0E0",
                                                padding="12px 16px",
                                                _focus={
                                                    "border": "2px solid #4DAB75",
                                                    "outline": "none",
                                                    "background_color": "#FFFFFF",
                                                },
                                                _placeholder={
                                                    "color": "#999999",
                                                },
                                            ),
                                            rx.input(
                                                type="password",
                                                placeholder="비밀번호",
                                                name="password",
                                                value=AppState.login_password,
                                                on_change=AppState.set_login_password,
                                                size="3",
                                                width="100%",
                                                background_color="#F8F9FA",
                                                color="#333333",
                                                border_radius="12px",
                                                border="1px solid #E0E0E0",
                                                padding="12px 16px",
                                                _focus={
                                                    "border": "2px solid #4DAB75",
                                                    "outline": "none",
                                                    "background_color": "#FFFFFF",
                                                },
                                                _placeholder={
                                                    "color": "#999999",
                                                },
                                            ),
                                            rx.cond(
                                                AppState.auth_error_message != "",
                                                rx.text(
                                                    AppState.auth_error_message,
                                                    color="#f87171",
                                                    size="2",
                                                    margin_top="10px",
                                                ),
                                            ),
                                            rx.button(
                                                "로그인",
                                                type="submit",
                                                width="100%",
                                                background_color="#4DAB75",
                                                color="#FFFFFF",
                                                border="none",
                                                border_radius="25px",
                                                padding="14px 28px",
                                                font_weight="600",
                                                font_size="1.05em",
                                                cursor="pointer",
                                                transition="all 0.25s ease",
                                                _hover={
                                                    "background_color": "#3d9a66",
                                                    "transform": "translateY(-2px)",
                                                    "box_shadow": "0 6px 24px rgba(77, 171, 117, 0.4)",
                                                },
                                                margin_top="10px",
                                            ),
                                            spacing="4",
                                        ),
                                        on_submit=AppState.login,
                                        width="100%",
                                    ),
                                    spacing="4",
                                    align="center",
                                    padding="30px 0",
                                    width="100%",
                                ),
                                value="login",
                            ),
                            rx.tabs.content(
                                # 회원가입 폼
                                rx.vstack(
                                    rx.form(
                                        rx.vstack(
                                            rx.input(
                                                placeholder="학번",
                                                name="student_id",
                                                value=AppState.signup_student_id,
                                                on_change=AppState.set_signup_student_id,
                                                size="3",
                                                width="100%",
                                                background_color="#F8F9FA",
                                                color="#333333",
                                                border_radius="12px",
                                                border="1px solid #E0E0E0",
                                                padding="12px 16px",
                                                _focus={
                                                    "border": "2px solid #4DAB75",
                                                    "outline": "none",
                                                    "background_color": "#FFFFFF",
                                                },
                                                _placeholder={
                                                    "color": "#999999",
                                                },
                                            ),
                                            rx.input(
                                                type="password",
                                                placeholder="비밀번호",
                                                name="password",
                                                value=AppState.signup_password,
                                                on_change=AppState.set_signup_password,
                                                size="3",
                                                width="100%",
                                                background_color="#F8F9FA",
                                                color="#333333",
                                                border_radius="12px",
                                                border="1px solid #E0E0E0",
                                                padding="12px 16px",
                                                _focus={
                                                    "border": "2px solid #4DAB75",
                                                    "outline": "none",
                                                    "background_color": "#FFFFFF",
                                                },
                                                _placeholder={
                                                    "color": "#999999",
                                                },
                                            ),
                                            rx.input(
                                                placeholder="닉네임 (2-20자)",
                                                name="nickname",
                                                value=AppState.signup_nickname,
                                                on_change=AppState.set_signup_nickname,
                                                size="3",
                                                width="100%",
                                                background_color="#F8F9FA",
                                                color="#333333",
                                                border_radius="12px",
                                                border="1px solid #E0E0E0",
                                                padding="12px 16px",
                                                _focus={
                                                    "border": "2px solid #4DAB75",
                                                    "outline": "none",
                                                    "background_color": "#FFFFFF",
                                                },
                                                _placeholder={
                                                    "color": "#999999",
                                                },
                                            ),
                                            rx.select(
                                                [
                                                    "인문대학",
                                                    "사회과학대학",
                                                    "경영대학",
                                                    "자연과학대학",
                                                    "의과대학",
                                                    "간호대학",
                                                    "글로벌융합대학",
                                                    "미디어스쿨",
                                                    "반도체·디스플레이스쿨",
                                                    "정보과학대학",
                                                    "미래융합스쿨",
                                                    "산학협력특성화대학",
                                                    "일송자유교양대학",
                                                    "자기설계융합전공"
                                                ],
                                                placeholder="단과대 선택",
                                                value=AppState.signup_college,
                                                on_change=AppState.set_signup_college,
                                                size="3",
                                                width="100%",
                                                background_color="#F8F9FA",
                                                color="#333333",
                                                border_radius="12px",
                                                border="1px solid #E0E0E0",
                                                padding="12px 16px",
                                            ),
                                            rx.cond(
                                                AppState.auth_error_message != "",
                                                rx.text(
                                                    AppState.auth_error_message,
                                                    color="#f87171",
                                                    size="2",
                                                    margin_top="10px",
                                                ),
                                            ),
                                            rx.button(
                                                "회원가입",
                                                type="submit",
                                                width="100%",
                                                background_color="#4DAB75",
                                                color="#FFFFFF",
                                                border="none",
                                                border_radius="25px",
                                                padding="14px 28px",
                                                font_weight="600",
                                                font_size="1.05em",
                                                cursor="pointer",
                                                transition="all 0.25s ease",
                                                _hover={
                                                    "background_color": "#3d9a66",
                                                    "transform": "translateY(-2px)",
                                                    "box_shadow": "0 6px 24px rgba(77, 171, 117, 0.4)",
                                                },
                                                margin_top="10px",
                                            ),
                                            spacing="4",
                                        ),
                                        on_submit=AppState.signup,
                                        width="100%",
                                    ),
                                    spacing="4",
                                    align="center",
                                    padding="30px 0",
                                    width="100%",
                                ),
                                value="signup",
                            ),
                            default_value="login",
                            width="100%",
                        ),
                        width="100%",
                        max_width="450px",
                        padding="30px 40px",
                        background="#FFFFFF",
                        border="1px solid rgba(77, 171, 117, 0.2)",
                        border_radius="24px",
                        box_shadow="0 8px 32px rgba(0, 0, 0, 0.1)",
                        class_name="auth-card",
                    ),
                    
                    spacing="6",
                    align="center",
                    width="100%",
                    padding_top="120px",
                    padding_bottom="60px",
                    position="relative",
                    z_index="1",
                ),
                width="100%",
                min_height="100vh",
                display="flex",
                align_items="center",
                justify_content="center",
                padding="40px 20px",
            ),
            width="100%",
            min_height="100vh",
            position="relative",
            z_index="1",
        ),
        width="100%",
        min_height="100vh",
        position="relative",
    )
