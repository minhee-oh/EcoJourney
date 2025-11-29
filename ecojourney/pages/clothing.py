# clothing.py

import reflex as rx

def clothing_page() -> rx.Component:
    return rx.vstack(
        rx.heading("의류 입력 페이지"),
        rx.text("의류 입력 데이터를 처리한 후 다음으로 이동합니다."),
        rx.button(
            "전기 페이지로 ➡️",
            # 다음 페이지로 직접 리다이렉트
            on_click=rx.redirect("/input/electricity"),
            color_scheme="green",
            size="3",
        )
    )