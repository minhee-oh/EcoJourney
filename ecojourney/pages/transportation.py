import reflex as rx
from ecojourney.state import AppState

def transportation_page():
    return rx.center(
        rx.vstack(
            rx.heading("🚗 교통 편", size="8", color="blue.600"),
            rx.text("오늘 이용한 이동 수단을 입력해주세요.", size="5"),
            
            # 간단한 뒤로가기 버튼
            rx.button(
                "⬅️ 이전으로", 
                on_click=rx.redirect("/intro")
            ),
            spacing="5",
            align="center",
        ),
        width="100%",
        height="100vh",
        padding_top="100px"
    )