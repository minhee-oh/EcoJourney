import reflex as rx
from ecojourney.state import AppState

def home_page():
    """홈 페이지 컴포넌트"""
    # State를 사용하여 컴포넌트와 연결 (중요: State 변수를 참조해야 이벤트 핸들러가 작동함)
    # 페이지 함수는 단일 컴포넌트를 반환해야 함 (rx.fragment 대신 rx.box 사용)
    return rx.box(
        # State 변수를 참조하여 State와 연결 (에러 메시지 표시용)
        rx.cond(
            AppState.error_message != "",
            rx.text(AppState.error_message, color="red"),
        ),
        # State 변수를 참조하여 State와 연결 (로딩 상태 표시용)
        rx.cond(
            AppState.is_loading,
            rx.text("로딩 중...", color="blue"),
        ),
        rx.center(
            rx.vstack(
                rx.heading("EcoJourney", size="9", color="green.700"),

                rx.text(
                    "당신의 하루가 지구의 내일이 됩니다. 🌍",
                    size="6",
                    margin_bottom="20px",
                    color="gray.600"
                ),

                rx.button(
                    "탄소 발자국 측정 시작하기 🚀",
                    on_click=rx.redirect("/intro"),
                    size="3",
                    color_scheme="green",
                    padding="15px 30px",
                    border_radius="lg",
                    z_index="999",  # 모든 레이아웃보다 위에 오게 설정 (클릭 방해 요소 제거)
                    _hover={"opacity": 0.8},
                ),
                spacing="5",
                align="center",
            ),
            width="100%",
            height="100vh",
            padding_top="100px",
        ),
        width="100%",
        height="100vh",
    )