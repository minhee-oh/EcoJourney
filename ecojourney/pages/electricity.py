# electricity.py

import reflex as rx

def electricity_page() -> rx.Component:
    return rx.vstack(
        rx.heading("전기 입력 페이지"),
        rx.text("전기 입력 데이터를 처리한 후 다음으로 이동합니다."),
        rx.button(
            "쓰레기 페이지로 ➡️",
            # 다음 페이지로 직접 리다이렉트
            on_click=rx.redirect("/input/waste"),
            color_scheme="green",
            size="3",
        )
    )