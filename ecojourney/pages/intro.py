import reflex as rx
from ..states import AppState
from .common_header import header, footer_bar

def footer() -> rx.Component:
    return rx.box(
        rx.center(
            # 💡 영상 위에서 잘 보이도록 텍스트 색상 조정
            rx.text("© 2025 EcoJourney. All rights reserved.", color="white", font_size="0.9em"),
            padding="1em",
        ),
        width="100%",
        position="fixed",
        bottom="0",
        z_index="100",
        background_color="transparent",
    )

def intro_page():
    return rx.cond(
        AppState.is_logged_in,
        rx.box(
            header(),
            footer_bar(),

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

        @keyframes slideUpFade {
            0% {
                opacity: 0;
                transform: translateY(40px);
            }
            100% {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .article-card {
            opacity: 0;
            animation: slideUpFade 0.6s ease forwards;
        }

        .article-card:nth-child(1) {
            animation-delay: 0.1s;
        }

        .article-card:nth-child(2) {
            animation-delay: 0.2s;
        }

        .article-card:nth-child(3) {
            animation-delay: 0.3s;
        }

        .article-card:nth-child(4) {
            animation-delay: 0.4s;
        }

        .article-card:nth-child(5) {
            animation-delay: 0.5s;
        }

        .article-card:nth-child(6) {
            animation-delay: 0.6s;
        }

        .article-card:nth-child(7) {
            animation-delay: 0.7s;
        }

        .article-card:nth-child(8) {
            animation-delay: 0.8s;
        }

        .article-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 12px 24px rgba(0,0,0,0.35);
            transition: all 0.3s ease;
        }
        </style>
        """),

        # 메인 콘텐츠
        rx.box(
            # 텍스트와 이미지 (세로 중앙 정렬)
            rx.hstack(
                rx.vstack(
                    rx.heading(
                        "리포트",
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
                        "일상 속 활동을 기록하고 나의 탄소 발자국 리포트를 확인하세요!",
                        color="gray.700",
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
                    padding_left="100px",
                ),

                # 이미지 영역
                rx.box(
                    rx.image(
                        src="/report.png",
                        width="90%",
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
                    padding_left="30px",
                ),
                width="100%",
                height="70vh",
                align="center",
                justify="between",
            ),

            # 기록하기 버튼 (화면 하단)
            rx.box(
                rx.button(
                    "기록하기",
                    on_click=rx.redirect("/input/transportation"),
                    color="#FFFFFF",
                    background_color="#4DAB75",
                    border_radius="40px",
                    padding="30px 60px",
                    font_size="1.2em",
                    font_weight="bold",
                    _hover={
                        "background_color": "#3d8f5f",
                        "transform": "translateY(-8px)",
                        "box_shadow": "0 6px 20px rgba(77, 171, 117, 0.4)",
                    },
                    style={
                        "opacity": 0,
                        "animation": "fadeInUp 1s ease forwards",
                        "animation-delay": "0.5s",
                        "transition": "all 0.3s ease",
                    },
                ),
                width="100%",
                display="flex",
                justify_content="center",
                padding_bottom="60px",
            ),

            width="100%",
            min_height="100vh",
            background="linear-gradient(135deg, rgba(77, 171, 117, 0.1) 0%, rgba(77, 171, 117, 0.15) 100%)",
            display="flex",
            flex_direction="column",
            justify_content="center",
        ),

            # 페이지 로드 시 퀴즈 상태 로드
            on_mount=AppState.load_quiz_state,
        ),
    )

    #     header(),

    #     rx.center(
    #         rx.vstack(
    #             rx.heading("EcoJourney는 이렇게 사용해요", size="8", color="white", margin_bottom="15px"),
                
    #             # rx.text(
    #             #     "EcoJourney는 일상 속 행동을 기반으로\n"
    #             #     "여섯 가지 카테고리를 순서대로 기록해요.",
    #             #     white_space="pre-line",
    #             #     color="white",
    #             #     max_width="600px",
    #             #     text_align="center",
    #             #     margin_y="10px"
    #             # ),

    #             rx.divider(background_color="white"),

    #             rx.vstack(
    #                 rx.list(
    #                     rx.list_item("1. 당신의 하루를 기록하세요.", color="white", font_weight="bold", text_align="center", padding_top="5px"),
    #                     rx.list_item("일상 속 6가지 카테고리(교통, 식품, 의류, 쓰레기, 전기, 물)마다 해당되는 활동을 선택합니다.", color="white", text_align="center", padding_bottom="15px"),
    #                     rx.list_item("2. 측정 기준을 정합니다", color="white", font_weight="bold", text_align="center", padding_top="5px"),
    #                     rx.list_item("선택한 활동에 대한 측정 단위(예: km 또는 시간)를 고르고 값을 입력합니다.", color="white", text_align="center", padding_bottom="15px"),
    #                     rx.list_item("3. 결과를 확인하세요.",color="white", font_weight="bold", text_align="center", padding_top="5px"),
    #                     rx.list_item("모든 카테고리의 기록이 완료되면, 당신의 라이프스타일에 대한 개인화된 탄소 발자국 리포트를 즉시 볼 수 있습니다.", color="white", text_align="center", padding_bottom="15px"),
    #                     spacing="3",
    #                 ),
    #                 align="start",
    #                 width="100%",
    #                 padding_x="40px"
    #             ),

    #             rx.divider(background_color="white"),

    #             rx.text(
    #                 "지금 바로 당신의 첫 걸음을 확인해보세요.",
    #                 color="white",
    #                 max_width="600px",
    #                 text_align="center",
    #                 margin_y="10px"
    #             ),

    #             rx.button(
    #                 "Start your Journey",
    #                 on_click=rx.redirect("/input/transportation"),
    #                 color="white",
    #                 background_color="rgba(0, 0, 0, 0.22)",
    #                 border_radius="40px",
    #                 padding="25px 40px",
    #                 border="4px solid rgba(255, 255, 255, 0.2)",
    #                 font_size="1.1em",
    #                 font_weight="semibold",
    #                 _hover={
    #                     "background_color": "rgba(0, 0, 0, 0.4)",
    #                 },
    #             ),

    #             spacing="5",
    #             align="center",
    #         ),
    #         height="100vh",    # ← 정중앙 배치의 핵심
    #         z_index="1",
    #     ),

    #     footer(),

    #     width="100%",
    #     min_height="100vh",
    #     background_color="transparent",
    #     position="relative",
    # )
