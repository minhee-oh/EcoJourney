# battle.py - 단과대별 대결 페이지

import reflex as rx
from ..states import AppState
from .common_header import header


def battle_page() -> rx.Component:
    """단과대별 대결 페이지"""
    return rx.cond(
        AppState.is_logged_in,
        rx.box(
            header(),
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
            # ---------------------------------------------
            # 1) 상단 2/3 배경 + 텍스트 + fade-in animation
            # ---------------------------------------------
            rx.box(
                rx.hstack(
                    rx.vstack(
                        rx.heading(
                            "배틀",
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
                            "단과대별 배틀에 참여하여 포인트를 베팅하고 승리의 영광을 차지하세요!",
                            color="gray.200",
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
                        align="start",        # 가로: 왼쪽 정렬
                        justify="center",     # 세로: 중앙 정렬
                        height="100%",
                        padding_top="50px",
                        padding_left="100px",
                    ),

                    # -----------------------
                    # 오른쪽: 이미지 영역
                    # -----------------------
                    rx.box(
                        rx.image(
                            src="/battle.png",
                            width="100%",             # 이미지 너비
                            height="auto",
                            object_fit="contain",
                            style={
                                "opacity": 0,
                                "transform": "translateY(20px)",
                                "animation": "fadeInUp 0.8s ease forwards",
                                "animation-delay": "0.2s",
                            },
                        ),
                        width="50%",                 # 전체의 절반을 이미지 영역으로 사용
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

            # ----------------------------------------------------
            # ② 실제 콘텐츠
            # ----------------------------------------------------
            rx.box(
                rx.vstack(

                    # -------------------------------------------------------
                    # ⭐ 현재 대결 정보 섹션
                    # -------------------------------------------------------
                    rx.cond(
                        AppState.current_battle != None,
                        rx.box(
                            rx.card(
                                rx.vstack(
                                    rx.heading("현재 대결", size="7", color="#333333", margin_bottom="20px"),
                                    rx.hstack(
                                        rx.vstack(
                                            rx.text(AppState.current_battle["college_a"], size="6", font_weight="bold", color="blue.600"),
                                            rx.text(f"총 포인트: {AppState.current_battle['score_a']}", size="5", color="#333333", font_weight="bold"),
                                            rx.text(f"참가 인원: {AppState.current_battle['participants_a']}명", size="5", color="gray.600", font_weight="normal"),
                                            align="center",
                                            spacing="2",
                                        ),
                                        rx.text("VS", size="7", font_weight="bold", color="#4DAB75", margin_x="30px"),
                                        rx.vstack(
                                            rx.text(AppState.current_battle["college_b"], size="6", font_weight="bold", color="red.600"),
                                            rx.text(f"총 포인트: {AppState.current_battle['score_b']}", size="5", color="#333333", font_weight="bold"),
                                            rx.text(f"참가 인원: {AppState.current_battle['participants_b']}명", size="5", color="gray.600", font_weight="normal"),
                                            align="center",
                                            spacing="2",
                                        ),
                                        justify="center",
                                        align="center",
                                        spacing="2",
                                    ),
                                    align="center",
                                    justify="center",
                                    width="100%",
                                    margin_y="20px",
                                ),
                                rx.divider(margin_y="15px"),
                                rx.text(
                                    f"기간: {AppState.current_battle['start_date']} ~ {AppState.current_battle['end_date']}",
                                    size="5",
                                    color="gray.300",
                                    font_weight="bold",
                                ),
                                spacing="4",
                                padding="20px",
                            ),
                            width="100%",
                            background="rgba(255, 255, 255, 0.1)",
                            border="1px solid rgba(255, 255, 255, 0.2)",
                            border_radius="12px",
                            padding="8px",
                        ),
                    ),
                    
                    # 단과대별 참가자 목록 (상위 5명)
                    rx.cond(
                        AppState.current_battle != None,
                        rx.hstack(
                            # 단과대 A 참가자 목록
                            rx.card(
                                rx.vstack(
                                    rx.heading(
                                        AppState.current_battle["college_a"],
                                        size="6",
                                        color="blue.600",
                                        margin_bottom="15px",
                                    ),
                                    rx.cond(
                                        AppState.college_a_participants.length() > 0,
                                        rx.vstack(
                                            rx.foreach(
                                                AppState.college_a_participants,
                                                lambda p: rx.hstack(
                                                    rx.text(
                                                        f"{p['rank']}위",
                                                        width="50px",
                                                        font_weight="bold",
                                                        color="#4DAB75",
                                                    ),
                                                    rx.text(
                                                        p["nickname"],
                                                        width="150px",
                                                        font_weight="bold",
                                                        color="#333333",
                                                    ),
                                                    rx.text(
                                                        f"{p['bet_amount']:,}점",
                                                        width="100px",
                                                        color="#4DAB75",
                                                        font_weight="bold",
                                                    ),
                                                    spacing="3",
                                                    align="center",
                                                    width="100%",
                                                    padding="8px",
                                                    border_radius="8px",
                                                    background=rx.cond(
                                                        p["rank"] == 1,
                                                        "rgba(77, 171, 117, 0.15)",
                                                        "rgba(77, 171, 117, 0.05)",
                                                    ),
                                                ),
                                            ),
                                            spacing="2",
                                            width="100%",
                                        ),
                                        rx.text(
                                            "아직 참가자가 없습니다.",
                                            color="gray.600",
                                            size="3",
                                        ),
                                    ),
                                    spacing="3",
                                ),
                                padding="20px",
                                border="1px solid rgba(255, 255, 255, 0.2)",
                                background="rgba(255, 255, 255, 0.1)",
                                flex="1",
                                min_width="300px",
                            ),
                            # 단과대 B 참가자 목록
                            rx.card(
                                rx.vstack(
                                    rx.heading(
                                        AppState.current_battle["college_b"],
                                        size="6",
                                        color="red.600",
                                        margin_bottom="15px",
                                    ),
                                    rx.cond(
                                        AppState.college_b_participants.length() > 0,
                                        rx.vstack(
                                            rx.foreach(
                                                AppState.college_b_participants,
                                                lambda p: rx.hstack(
                                                    rx.text(
                                                        f"{p['rank']}위",
                                                        width="50px",
                                                        font_weight="bold",
                                                        color="#4DAB75",
                                                    ),
                                                    rx.text(
                                                        p["nickname"],
                                                        width="150px",
                                                        font_weight="bold",
                                                        color="#333333",
                                                    ),
                                                    rx.text(
                                                        f"{p['bet_amount']:,}점",
                                                        width="100px",
                                                        color="#4DAB75",
                                                        font_weight="bold",
                                                    ),
                                                    spacing="3",
                                                    align="center",
                                                    width="100%",
                                                    padding="8px",
                                                    border_radius="8px",
                                                    background=rx.cond(
                                                        p["rank"] == 1,
                                                        "rgba(77, 171, 117, 0.15)",
                                                        "rgba(77, 171, 117, 0.05)",
                                                    ),
                                                ),
                                            ),
                                            spacing="2",
                                            width="100%",
                                        ),
                                        rx.text(
                                            "아직 참가자가 없습니다.",
                                            color="gray.600",
                                            size="3",
                                        ),
                                    ),
                                    spacing="3",
                                ),
                                padding="20px",
                                border="1px solid rgba(255, 255, 255, 0.2)",
                                background="rgba(255, 255, 255, 0.1)",
                                flex="1",
                                min_width="300px",
                            ),
                            spacing="4",
                            width="100%",
                            align="stretch",
                            justify="center",
                        ),
                    ),
                    
                    # 참가 폼
                    rx.card(
                        rx.vstack(
                            rx.heading("대결 참가", size="6", color="#333333", margin_bottom="15px"),

                            rx.text(
                                "팀의 승리에 기여할 포인트를 베팅하세요!",
                                size="3",
                                color="gray.700",
                            ),
                            rx.text(
                                "승리한 팀은 상대팀의 베팅 포인트를 나눠 가집니다.",
                                size="2",
                                color="#4DAB75",
                                margin_bottom="20px",
                                font_weight="bold",
                            ),

                            # ⚙️ 베팅 입력 + 버튼
                            rx.hstack(
                                rx.input(
                                    type="number",
                                    placeholder="베팅 포인트",
                                    value=AppState.battle_bet_amount,
                                    on_change=AppState.set_battle_bet_amount,
                                    size="3",
                                    width="200px",
                                ),
                                rx.button(
                                    "참가하기",
                                    on_click=AppState.join_battle,
                                    color_scheme="green",
                                    size="3",
                                ),
                                spacing="4",
                                align="center",
                            ),

                            # ⚠️ 에러 메시지
                            rx.cond(
                                AppState.battle_error_message != "",
                                rx.text(
                                    AppState.battle_error_message,
                                    color="red.600",
                                    size="2",
                                    margin_top="10px",
                                    font_weight="bold",
                                ),
                            ),

                            spacing="4",
                            padding="20px",
                        ),
                        width="100%",
                        background="white",
                        border="1px solid rgba(0,0,0,0.1)",
                        box_shadow="0 4px 12px rgba(0,0,0,0.1)",
                        margin_bottom="30px",
                    ),

                    # -------------------------------------------------------
                    # ⭐ 내 포인트 정보 카드
                    # -------------------------------------------------------
                    rx.card(
                        rx.hstack(
                            rx.text("내 포인트", size="4", color="#333333"),
                            rx.text(
                                f"{AppState.current_user_points:,}",
                                size="6",
                                font_weight="bold",
                                color="#4DAB75",
                                margin_left="10px",
                            ),
                            spacing="2",
                            align="center",
                        ),
                        width="100%",
                        background="white",
                        border="1px solid rgba(0,0,0,0.1)",
                        box_shadow="0 4px 12px rgba(0,0,0,0.1)",
                        padding="20px",
                        margin_bottom="30px",
                    ),
                    spacing="6",
                    width="100%",
                    max_width="1200px",
                    align="center",
                ),

                width="100%",
                z_index="2",
                padding="40px 20px",
                display="flex",
                justify_content="center",

                # ⭐ 콘텐츠를 상단 66vh 바로 아래로 내리는 핵심 코드
                margin_top="66vh",
            ),

        ),
        ),
    )

