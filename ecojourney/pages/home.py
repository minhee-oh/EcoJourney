# home.py

import reflex as rx
from ecojourney.state import AppState

# --- 공통 컴포넌트 (나중에 별도 파일로 분리 가능) ---
def header() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.text("EcoJourney", font_size="2em", font_weight="bold", color="white"),
            # 나중에 여기에 네비게이션 링크를 추가할 수 있습니다.
            justify="between",
            align="center",
            padding="1em 2em",
        ),
        # border_bottom="1px solid #eee",
        width="100%",
        position="fixed", # 상단 고정
        top="0",
        z_index="100",
        background_color="transparent",
    )

def footer() -> rx.Component:
    return rx.box(
        rx.center(
            rx.text("© 2023 EcoJourney. All rights reserved.", color="gray.500", font_size="0.9em"),
            padding="1em",
        ),
        border_top="1px solid #eee",
        width="100%",
        position="fixed", # 하단 고정
        bottom="0",
        z_index="100",
        background_color="white",
    )

# --- 홈 페이지 본문 ---
def home_page() -> rx.Component:
    """홈 페이지 컴포넌트"""
    return rx.box(
        # 1. 배경 영상 컴포넌트
        rx.video(
            src="ecojourney/assets/eco_background.mp4", # assets 폴더에 넣은 영상 파일 경로
            autoplay=True,             # 자동 재생
            loop=True,                 # 반복 재생
            muted=True,                # 소리 제거 (배경 영상은 보통 무음)
            style={
                # 화면 전체를 덮도록 위치 설정
                "position": "fixed",
                "top": "0",
                "left": "0",
                "width": "100%",
                "height": "100%",
                "objectFit": "cover",  # 화면 비율에 맞게 영상을 늘려 채움
                "zIndex": "-1",        # 콘텐츠보다 뒤에 배치
                "filter": "brightness(0.6)" # 영상이 너무 밝으면 콘텐츠가 안 보이므로 어둡게 처리
            }
        ),
        
        # 2. 헤더 추가
        header(),
        
        # 3. 메인 콘텐츠 (움직이는 지구 대신 텍스트와 버튼만 중앙에 배치)
        rx.center(
            rx.vstack(
                # 콘텐츠가 영상 위에 잘 보이도록 색상 조정
                rx.heading("EcoJourney", size="9", color="white", font_weight="extrabold"),
                rx.text("당신의 탄소 발자국을 측정하고, 지구를 위한 작은 변화를 시작해보세요.",
                        size="5", color="white", max_width="500px", text_align="center",
                        margin_bottom="30px"),
                rx.button(
                    "탄소 발자국 측정 시작하기 🚀",
                    on_click=rx.redirect("/intro"),
                    size="3", color_scheme="green", padding="15px 30px", border_radius="lg",
                ),
                
                align_items="center",
                spacing="5",
                z_index="1", # 영상 위에 올라오도록 z-index 설정
            ),
            width="100%",
            height="100vh",
            padding_top="80px",
            padding_bottom="80px",
        ),
        
        # 4. 푸터 추가
        footer(),
        
        width="100%",
        min_height="100vh",
        background_color="transparent", # 배경색은 영상에 맡김
    )

# 이 코드 외에 전역 CSS 파일에 다음을 추가하면 지구 이미지에 회전 애니메이션이 적용됩니다.
# styles.py (또는 custom_styles.css 등)
"""
@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}
"""