import reflex as rx
from ecojourney.state import AppState

def intro_page():
    return rx.center(
        rx.vstack(
            rx.heading("EcoJourney 서비스 소개 🌱", size="8", color="green.700"),
            
            rx.text(
                "EcoJourney는 당신의 일상 활동(교통, 식단, 에너지 소비 등)을 기반으로 탄소 발자국을 계산하고, 환경 목표 달성을 돕는 개인 맞춤형 코칭 앱입니다.",
                max_width="600px",
                text_align="center",
                margin_y="20px"
            ),
            
            rx.divider(),
            
            rx.vstack(
                rx.list(
                    rx.list_item("✅ **6가지 핵심 카테고리** 입력 기반 분석 (교통, 식품, 전기 등)", padding_y="5px"),
                    rx.list_item("📊 **AI 기반 리포트** 및 개인 맞춤형 탄소 저감 방안 제안", padding_y="5px"),
                    rx.list_item("🏆 **배지 시스템**을 통한 친환경 활동 동기 부여", padding_y="5px"),
                    spacing="3",
                ),
                align="start",
                width="100%",
                padding_x="40px"
            ),
            
            rx.divider(margin_top="20px"),
            
            # TODO: 홈 → 인트로 테스트 완료 후 활성화
            rx.button(
                "카테고리 입력 시작하기 ➡️",
                # 버튼 클릭 시 AppState의 next_category 함수를 호출하여 첫 번째 입력 페이지로 이동
                on_click=rx.redirect("/input/transportation"),
                size="3",
                color_scheme="blue",
                padding="15px 30px",
                border_radius="lg",
                margin_top="30px",
                _hover={"opacity": 0.8}
            ),
            
            spacing="5",
            align="center",
        ),
        width="100%",
        height="100vh",
        padding_top="100px",
    )