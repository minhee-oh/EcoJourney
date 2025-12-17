# home.py - 홈 페이지

import reflex as rx
from ..states import AppState
from .common_header import footer_bar

def home_header() -> rx.Component:
    """홈페이지 전용 헤더 (투명 배경)"""
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
                        _hover={"border": "1px solid #FFFFFF", "background_color": "rgba(255, 255, 255, 0.1)"},
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
                        _hover={"border": "1px solid #FFFFFF", "background_color": "rgba(255, 255, 255, 0.1)"},
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
                        _hover={"border": "1px solid #FFFFFF", "background_color": "rgba(255, 255, 255, 0.1)"},
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
                        _hover={"border": "1px solid #FFFFFF", "background_color": "rgba(255, 255, 255, 0.1)"},
                    ),
                    rx.text(
                        f"{AppState.current_user_nickname}님",
                        color="#FFFFFF",
                        font_size="1em",
                        margin_right="10px",
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
                        _hover={"border": "1px solid #FFFFFF", "background_color": "rgba(255, 255, 255, 0.1)"},
                    ),
                    rx.button(
                        "로그아웃",
                        on_click=AppState.logout,
                        background_color="rgba(255, 255, 255, 0.2)",
                        color="#FFFFFF",
                        border="1px solid rgba(255, 255, 255, 0.5)",
                        border_radius="25px",
                        padding="8px 20px",
                        font_weight="500",
                        _hover={"background_color": "rgba(255, 255, 255, 0.3)"},
                    ),
                    spacing="3",
                    align="center",
                ),

                # 로그인 안 된 상태 → 로그인 버튼
                rx.button(
                    "로그인",
                    on_click=rx.redirect("/auth"),
                    background_color="rgba(255, 255, 255, 0.2)",
                    color="#FFFFFF",
                    border="1px solid rgba(255, 255, 255, 0.5)",
                    border_radius="25px",
                    padding="8px 20px",
                    font_weight="500",
                    _hover={"background_color": "rgba(255, 255, 255, 0.3)"},
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
        background_color="transparent",
    )


# --- 홈 페이지 본문 ---
def home_page() -> rx.Component:
    """홈 페이지 컴포넌트"""
    return rx.box(
        home_header(),
        footer_bar(),

        # 스크롤 스냅 컨테이너
        rx.box(
            # Google Fonts 및 스타일링
        rx.html("""
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800&family=Noto+Sans+KR:wght@300;400;600;700;800&display=swap" rel="stylesheet">
        <style>
        * {
            font-family: 'Poppins', 'Noto Sans KR', sans-serif;
        }
        
        /* 스크롤 스냅 컨테이너 */
        .scroll-container {
            scroll-snap-type: y mandatory;
            overflow-y: scroll;
            height: 100vh;
        }
        
        .scroll-section {
            scroll-snap-align: start;
            scroll-snap-stop: always;
            min-height: 100vh;
            overflow-y: auto;
        }
        
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
        
        @keyframes slideInFromRight {
            0% {
                opacity: 0;
                transform: translateX(50px);
            }
            100% {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        @keyframes slideInFromLeft {
            0% {
                opacity: 0;
                transform: translateX(-50px);
            }
            100% {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        .section-enter {
            animation: fadeInUp 0.8s ease forwards;
        }

        /* 스크롤 애니메이션 */
        .scroll-fade-in,
        .scroll-fade-in-delay,
        .scroll-fade-in-text,
        .scroll-fade-in-button {
            opacity: 0;
            transform: translateY(30px);
            transition: opacity 0.8s ease, transform 0.8s ease;
        }
        
        /* ECOJOURNEY 제목은 항상 보이도록 */
        .scroll-fade-in[style*="opacity"] {
            opacity: 1 !important;
        }

        .scroll-fade-in.visible {
            opacity: 1;
            transform: translateY(0);
        }

        .scroll-fade-in-delay.visible {
            opacity: 1;
            transform: translateY(0);
            transition-delay: 0.2s;
        }

        .scroll-fade-in-text.visible {
            opacity: 1;
            transform: translateY(0);
            transition-delay: 0.4s;
        }

        .scroll-fade-in-button.visible {
            opacity: 1;
            transform: translateY(0);
            transition-delay: 0.6s;
        }
        </style>
        """),
        
        # 스크롤 애니메이션 및 섹션 전환 JavaScript
        rx.script("""
        (function() {
            const observerOptions = {
                threshold: 0.1,
                rootMargin: '0px 0px -100px 0px'
            };

            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('visible');
                    }
                });
            }, observerOptions);

            // DOM이 로드된 후 관찰 시작
            setTimeout(() => {
                const elements = document.querySelectorAll('.scroll-fade-in, .scroll-fade-in-delay, .scroll-fade-in-text, .scroll-fade-in-button');
                elements.forEach(el => observer.observe(el));
                
                // 섹션 전환 애니메이션
                const sections = document.querySelectorAll('.scroll-section');
                const sectionObserver = new IntersectionObserver((entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            entry.target.style.animation = 'fadeInUp 0.8s ease forwards';
                        }
                    });
                }, { threshold: 0.5 });
                
                sections.forEach(section => sectionObserver.observe(section));
            }, 100);
        })();
        """),

        # 세션 복원 스크립트 (페이지 로드 시 localStorage 확인 후 백엔드 호출)
        rx.script("""
            (function() {
                // localStorage에서 세션 정보 확인
                const userId = localStorage.getItem('eco_user_id');
                const isLoggedIn = localStorage.getItem('eco_is_logged_in');

                // 로그인 상태이고 세션 정보가 있으면 복원 시도
                if (isLoggedIn === 'true' && userId && userId !== 'null' && userId !== 'None') {
                    // Reflex 이벤트 발생시키기 위해 커스텀 이벤트 사용
                    setTimeout(function() {
                        // window에 user_id 저장 (이후 on_mount에서 접근 가능)
                        window.ecoSessionUserId = userId;
                    }, 50);
                }
            })();
        """),

        # 히어로 섹션
        rx.box(
            # 배경 이미지 레이어
            rx.box(
                rx.image(
                    src="/earth.png",
                    width="100%",
                    height="100%",
                    object_fit="cover",
                    style={
                        "opacity": 0.3,
                    },
                ),
                width="100%",
                height="100vh",
                position="absolute",
                top="0",
                left="0",
                z_index="0",
                overflow="hidden",
            ),

            # 그라데이션 오버레이
            rx.box(
                width="100%",
                height="100vh",
                background="linear-gradient(135deg, rgba(0, 0, 0, 0.7) 0%, rgba(0, 0, 0, 0.5) 50%, rgba(0, 0, 0, 0.3) 100%)",
                position="absolute",
                top="0",
                left="0",
                z_index="1",
            ),

            # 히어로 콘텐츠 (텍스트 + 이미지)
            rx.box(
                rx.hstack(
                    # 왼쪽: 텍스트 콘텐츠
                rx.vstack(
                    rx.heading(
                        "ECOJOURNEY",
                        size="9",
                        color="#FFFFFF",
                            margin_bottom="24px",
                            font_weight="800",
                            letter_spacing="0.1em",
                            text_shadow="3px 3px 8px rgba(0,0,0,0.4), 0 0 20px rgba(77, 171, 117, 0.3)",
                        style={
                            "opacity": 0,
                            "transform": "translateY(20px)",
                            "animation": "fadeInUp 0.8s ease forwards",
                            "animation-delay": "0.1s",
                                "font-family": "'Poppins', sans-serif",
                                "font-weight": "800",
                                "letter-spacing": "0.15em",
                                "text-transform": "uppercase",
                        },
                    ),
                    rx.text(
                        "줄일수록 보이는 나의 변화.",
                        color="#FFFFFF",
                            size="7",
                            font_weight="700",
                            text_align="left",
                            text_shadow="2px 2px 6px rgba(0,0,0,0.4)",
                            line_height="1.4",
                        style={
                            "opacity": 0,
                            "transform": "translateY(20px)",
                            "animation": "fadeInUp 1s ease forwards",
                            "animation-delay": "0.25s",
                                "font-family": "'Noto Sans KR', 'Poppins', sans-serif",
                                "font-weight": "700",
                                "font-size": "2.2em",
                                "letter-spacing": "0.02em",
                        },
                    ),
                    rx.text(
                        "다함께 지속 가능한 에코 라이프를 만들어요.",
                        color="#FFFFFF",
                        size="6",
                            font_weight="600",
                            text_align="left",
                            text_shadow="1px 1px 4px rgba(0,0,0,0.4)",
                            margin_top="16px",
                            line_height="1.6",
                        style={
                            "opacity": 0,
                            "transform": "translateY(20px)",
                            "animation": "fadeInUp 1s ease forwards",
                            "animation-delay": "0.35s",
                                "font-family": "'Noto Sans KR', 'Poppins', sans-serif",
                                "font-weight": "600",
                                "font-size": "1.4em",
                                "letter-spacing": "0.01em",
                            },
                        ),
                        spacing="3",
                        align="start",
                        justify="center",
                        width="50%",
                        padding_left="100px",
                    ),
                    
                    # 오른쪽: 히어로 이미지
                    rx.box(
                        rx.image(
                            src="/earth.png",
                            width="100%",
                            height="auto",
                            object_fit="contain",
                            style={
                                "opacity": 0,
                                "transform": "translateY(20px)",
                                "animation": "fadeInUp 0.8s ease forwards",
                                "animation-delay": "0.2s",
                                "filter": "drop-shadow(0 10px 30px rgba(0,0,0,0.3))",
                            },
                        ),
                        width="50%",
                        display="flex",
                        align_items="center",
                        justify_content="center",
                        padding_right="100px",
                    ),
                    
                    width="100%",
                    height="100%",
                    align="center",
                    justify="between",
                ),
                width="100%",
                height="100vh",
                position="relative",
                z_index="2",
                display="flex",
                align_items="center",
                justify_content="center",
            ),
            width="100%",
            height="100vh",
            position="relative",
            margin_bottom="0",
            class_name="scroll-section",
        ),
        
        # 기후 위기 섹션
        rx.box(
            # 배경 레이어 - 진한 회색
            rx.box(
                    width="100%",
                    height="100vh",
                    background="#2A2A2A",
                    position="absolute",
                    top="0",
                    left="0",
                    z_index="0",
                ),
                rx.vstack(
                    # 현재 기후 상황
                    rx.heading(
                        "지금, 우리가 마주한 기후 위기",
                        text_align="center",
                        font_weight="800",
                        size="8",
                        color="#FFFFFF",
                        margin_bottom="60px",
                        width="100%",
                        style={
                            "font-family": "'Noto Sans KR', 'Poppins', sans-serif",
                            "letter-spacing": "0.02em",
                        },
                        class_name="scroll-fade-in",
                    ),

                    rx.hstack(
                        # =======================
                        # 왼쪽 : 이미지 콜라주 (3개) - 언밸런스 배치
                        # =======================
                        rx.box(
                            rx.vstack(
                                rx.hstack(
                                    rx.vstack(
                                        rx.image(
                                            src="/trash.jpg",
                                            width="280px",
                                            height="200px",
                                            object_fit="cover",
                                            border_radius="20px",
                                            style={
                                                "box-shadow": "0 10px 40px rgba(0, 0, 0, 0.5)",
                                            },
                                        ),
                                        rx.image(
                                            src="/glacier.jpg",
                                            width="280px",
                                            height="200px",
                                            object_fit="cover",
                                            border_radius="20px",
                                            margin_top="15px",
                                            style={
                                                "box-shadow": "0 10px 40px rgba(0, 0, 0, 0.5)",
                                            },
                                        ),
                                        spacing="0",
                                        align="stretch",
                                    ),
                                    rx.image(
                                        src="/dust.jpg",
                                        width="280px",
                                        height="415px",
                                        object_fit="cover",
                                        border_radius="20px",
                                        margin_left="15px",
                                        style={
                                            "box-shadow": "0 10px 40px rgba(0, 0, 0, 0.5)",
                                        },
                                    ),
                                    spacing="0",
                                    align="start",
                                    width="100%",
                                ),
                                spacing="0",
                                align="stretch",
                            ),
                            width="auto",
                            class_name="scroll-fade-in-delay",
                        ),

                        # =======================
                        # 중간 : 텍스트 영역
                        # =======================
                        rx.box(
                            rx.vstack(
                                rx.text(
                                    "기후 변화는 더 이상 먼 미래의 이야기가 아닙니다. 폭염, 이상 기후, 미세먼지, 해수면 상승과 같은 환경 문제는 이미 우리의 일상과 안전을 직접적으로 위협하고 있습니다.",
                                    color="#FFFFFF",
                                    size="5",
                                    font_weight="600",
                                    line_height="1.8",
                                    style={
                                        "font-family": "'Noto Sans KR', 'Poppins', sans-serif",
                                    },
                                ),
                                rx.text(
                                    "특히 온실가스 배출로 인한 지구 온난화는 자연 생태계의 붕괴뿐 아니라 식량 문제, 건강 문제, 사회·경제적 불균형까지 초래하고 있습니다.",
                                    color="#E0E0E0",
                                    size="5",
                                    font_weight="500",
                                    margin_top="24px",
                                    line_height="1.8",
                                    style={
                                        "font-family": "'Noto Sans KR', 'Poppins', sans-serif",
                                    },
                                ),
                                rx.html("""
                                    <p style="font-family: 'Noto Sans KR', 'Poppins', sans-serif; font-size: 1.25em; line-height: 1.8; color: #E0E0E0; margin-top: 24px;">
                                        하지만 기후 위기는 개인의 노력만으로 해결할 수 없는 문제인 동시에, 
                                        <span style="color: #4DAB75; font-weight: 700;">개인의 작은 실천이 모였을 때 가장 큰 변화를 만들 수 있는 문제이기도 합니다.</span>
                                        지금 행동하지 않으면, 그 피해는 고스란히 우리의 미래가 됩니다.
                                    </p>
                                """),
                                spacing="1",
                                justify="center",
                                align="start",
                            ),
                            flex="1",
                            padding_x="0px",
                            class_name="scroll-fade-in-text",
                        ),

                        width="100%",
                        align="stretch",
                        margin_top="40px",
                        spacing="6",
                    ),
                    width="100%",
                    max_width="1200px",
                    margin="0 auto",
                    height="100vh",
                    position="relative",
                    z_index="1",
                    padding="80px 20px",
                    display="flex",
                    align_items="center",
                    justify_content="center",
                ),
                width="100%",
                height="100vh",
                position="relative",
                class_name="scroll-section",
            ),
        
        # ECOJOURNEY 소개 섹션
        rx.box(
            # 배경 레이어 - 진한 회색
            rx.box(
                width="100%",
                min_height="100vh",
                background="#2A2A2A",
                position="absolute",
                top="0",
                left="0",
                z_index="0",
            ),
            rx.vstack(
                # ECOJOURNEY 소개
                rx.vstack(
                    rx.heading(
                        "행동으로 이어지는 환경 실천 플랫폼 ",
                        text_align="center",
                        font_weight="800",
                        size="8",
                        color="#FFFFFF",
                        margin_bottom="0px",
                        position="relative",
                        z_index="30",
                        style={
                            "font-family": "'Poppins', sans-serif",
                            "letter-spacing": "0.1em",
                            "text-transform": "uppercase",
                            "opacity": "1 !important",
                            "visibility": "visible !important",
                            "display": "block",
                        },
                    ),
                    rx.text(
                        "",
                        text_align="center",
                        color="#E0E0E0",
                        size="5",
                        font_weight="600",
                        margin_bottom="0px",
                        position="relative",
                        z_index="20",
                        style={
                            "font-family": "'Noto Sans KR', 'Poppins', sans-serif",
                            "opacity": "1",
                        },
                    ),
                        rx.hstack(
                            # 왼쪽 박스
                            rx.box(
                                rx.vstack(
                                    rx.text(
                                        "EcoJourney는 환경 문제를 '알아보는 것'에서 끝내지 않고, 실제 행동과 변화로 이어지도록 돕는 참여형 환경 플랫폼입니다.",
                                        text_align="center",
                                        color="#FFFFFF",
                                        size="4",
                                        font_weight="600",
                                        line_height="1.6",
                                        style={
                                            "font-family": "'Noto Sans KR', 'Poppins', sans-serif",
                                        },
                                    ),
                                    rx.text(
                                        "우리는 일상 속에서 발생하는 탄소 배출과 환경 행동을 기록하고, 눈에 보이는 데이터와 보상 시스템을 통해 지속 가능한 실천을 자연스럽게 이어갈 수 있도록 설계되었습니다.",
                                        text_align="center",
                                        color="#E0E0E0",
                                        size="4",
                                        font_weight="500",
                                        margin_top="16px",
                                        line_height="1.6",
                                        style={
                                            "font-family": "'Noto Sans KR', 'Poppins', sans-serif",
                                        },
                                    ),
                                    rx.text(
                                        "환경 보호는 거창한 결심이 아니라 매일의 선택과 작은 습관에서 시작됩니다. EcoJourney는 그 시작을 함께합니다.",
                                        text_align="center",
                                        color="#E0E0E0",
                                        size="4",
                                        font_weight="600",
                                        margin_top="16px",
                                        line_height="1.6",
                                        style={
                                            "font-family": "'Noto Sans KR', 'Poppins', sans-serif",
                                        },
                                    ),
                                    spacing="3",
                                    align="center",
                                    justify="center",
                                    height="100%",
                                ),
                                flex="1",
                                height="auto",
                                min_height="300px",
                                background="rgba(60, 60, 60, 0.6)",
                                border="1px solid rgba(255, 255, 255, 0.1)",
                                border_radius="24px",
                                padding="25px",
                                box_shadow="0 8px 32px rgba(0, 0, 0, 0.5)",
                                class_name="scroll-fade-in",
                            ),

                            # 오른쪽 박스
                            rx.box(
                                rx.vstack(
                                    rx.heading(
                                        "ECOJOURNEY 이렇게 활용하세요.",
                                        text_align="center",
                                        font_weight="700",
                                        size="6",
                                        color="#FFFFFF",
                                        margin_bottom="20px",
                                        width="100%",
                                        style={
                                            "font-family": "'Noto Sans KR', 'Poppins', sans-serif",
                                        },
                                        class_name="scroll-fade-in",
                                    ),
                                    rx.hstack(
                                        rx.image(
                                            src="/report.png",
                                            width="50px",
                                            height="50px",
                                            border_radius="12px",
                                        ),
                                        rx.text(
                                            "나의 환경 행동을 기록하고 확인하세요.",
                                            color="#FFFFFF",
                                            size="4",
                                            font_weight="600",
                                            text_align="center",
                                            style={
                                                "font-family": "'Noto Sans KR', 'Poppins', sans-serif",
                                            },
                                        ),
                                        width="100%",
                                        justify="center",
                                        align="center",
                                        spacing="3",
                                        margin_top="15px",
                                        padding="15px",
                                        background="rgba(60, 60, 60, 0.4)",
                                        border_radius="16px",
                                        class_name="scroll-fade-in-delay",
                                    ),
                                    rx.hstack(
                                        rx.text(
                                            "챌린지와 배틀로 실천을 이어가세요.",
                                            color="#FFFFFF",
                                            size="4",
                                            font_weight="600",
                                            text_align="center",
                                            style={
                                                "font-family": "'Noto Sans KR', 'Poppins', sans-serif",
                                            },
                                        ),
                                        rx.image(
                                            src="/battle.png",
                                            width="50px",
                                            height="50px",
                                            border_radius="12px",
                                        ),
                                        width="100%",
                                        justify="center",
                                        align="center",
                                        spacing="3",
                                        padding="15px",
                                        background="rgba(60, 60, 60, 0.4)",
                                        border_radius="16px",
                                        class_name="scroll-fade-in-delay",
                                    ),
                                    rx.hstack(
                                        rx.image(
                                            src="/point.png",
                                            width="50px",
                                            height="50px",
                                            border_radius="12px",
                                        ),
                                        rx.text(
                                            "포인트로 동기부여를 높이세요.",
                                            color="#FFFFFF",
                                            size="4",
                                            font_weight="600",
                                            text_align="center",
                                            style={
                                                "font-family": "'Noto Sans KR', 'Poppins', sans-serif",
                                            },
                                        ),
                                        width="100%",
                                        justify="center",
                                        align="center",
                                        spacing="3",
                                        padding="15px",
                                        background="rgba(60, 60, 60, 0.4)",
                                        border_radius="16px",
                                        class_name="scroll-fade-in-delay",
                                    ),
                                    rx.hstack(
                                        rx.text(
                                            "환경을 '의식하는 습관'을 만들어 보세요.",
                                            color="#FFFFFF",
                                            size="4",
                                            font_weight="600",
                                            text_align="center",
                                            style={
                                                "font-family": "'Noto Sans KR', 'Poppins', sans-serif",
                                            },
                                        ),
                                        rx.image(
                                            src="/earth2.png",
                                            width="50px",
                                            height="50px",
                                            border_radius="12px",
                                        ),
                                        width="100%",
                                        justify="center",
                                        align="center",
                                        spacing="3",
                                        padding="15px",
                                        background="rgba(60, 60, 60, 0.4)",
                                        border_radius="16px",
                                        class_name="scroll-fade-in-delay",
                                    ),
                                    spacing="3",
                                    align="center",
                                    justify="center",
                                    height="100%",
                                ),
                                flex="1",
                                height="auto",
                                min_height="300px",
                                background="rgba(60, 60, 60, 0.6)",
                                border="1px solid rgba(255, 255, 255, 0.1)",
                                border_radius="24px",
                                padding="25px",
                                box_shadow="0 8px 32px rgba(0, 0, 0, 0.5)",
                                class_name="scroll-fade-in-delay",
                            ),

                            spacing="5",
                            width="100%",
                            align="stretch",
                        ),
                        spacing="6",
                        width="100%",
                        max_width="1200px",
                        margin="0 auto",
                    ),

                spacing="6",
                width="100%",
                    max_width="1300px",
                align="center",
                    position="relative",
                    z_index="30",
                ),
            margin_top="80px",
            width="100%",
            position="relative",
            z_index="30",
            padding="80px 40px",
            display="flex",
            align_items="center",
            justify_content="center",
            min_height="100vh",
            class_name="scroll-section",
        ),
        
        # 마지막 섹션: 행동 촉구
        rx.box(
            # 배경 레이어 - 진한 회색
            rx.box(
                width="100%",
                min_height="100vh",
                background="#2A2A2A",
                position="absolute",
                top="0",
                left="0",
                z_index="0",
            ),
            rx.box(
                rx.vstack(
                    rx.text(
                        "환경 보호는 선택이 아닌 책임입니다. 그리고 그 책임은 오늘의 작은 실천에서 시작됩니다.",
                        text_align="center",
                        color="#FFFFFF",
                        size="6",
                        font_weight="700",
                        width="100%",
                        line_height="1.8",
                        style={
                            "font-family": "'Noto Sans KR', 'Poppins', sans-serif",
                        },
                        class_name="scroll-fade-in-text",
                    ),
                    rx.text(
                        "ECOJOURNEY와 함께 지금, 당신의 환경 여정을 시작해보세요",
                        text_align="center",
                        color="#E0E0E0",
                        size="5",
                        font_weight="600",
                        width="100%",
                        margin_top="20px",
                        style={
                            "font-family": "'Noto Sans KR', 'Poppins', sans-serif",
                        },
                        class_name="scroll-fade-in-text",
                    ),
                    rx.cond(
                        ~AppState.is_logged_in,
                        rx.button(
                            "함께하기",
                            on_click=rx.redirect("/auth"),
                            color="#000000",
                            background_color="#FFFFFF",
                            border_radius="50px",
                            padding="20px 50px",
                            font_size="1.1em",
                            font_weight="700",
                            margin_top="40px",
                            style={
                                "font-family": "'Noto Sans KR', 'Poppins', sans-serif",
                            },
                            _hover={
                                "background_color": "#E0E0E0",
                                "transform": "translateY(-4px)",
                                "box_shadow": "0 10px 30px rgba(255, 255, 255, 0.3)",
                            },
                            class_name="scroll-fade-in-button",
                        ),
                        rx.box(height="40px"),  # 로그인된 경우 빈 공간
                    ),
                    spacing="2",
                    width="100%",
                    max_width="1200px",
                    align="center",
                    justify="center",
                ),
                width="100%",
                position="relative",
                z_index="30",
                padding="80px 40px",
                min_height="100vh",
                display="flex",
                align_items="center",
                justify_content="center",
            ),
            width="100%",
            position="relative",
            class_name="scroll-section",
        ),
        
        width="100%",
        height="100vh",
        overflow_y="scroll",
        background="#1A1A1A",
        style={
            "scroll-snap-type": "y mandatory",
            "scroll-behavior": "smooth",
        },
    ),
    width="100%",
    min_height="100vh",
    background="#1A1A1A",
    )
