# report.py

import reflex as rx
from ecojourney.state import AppState
from typing import Dict, Any

def report_page() -> rx.Component:
    """
    최종 탄소 발자국 리포트 페이지 컴포넌트입니다.
    """
    return rx.center(
        rx.vstack(
            rx.heading("🌍 탄소 발자국 측정 결과", size="7", margin_bottom="20px"),
            
            # 1. 계산 상태 확인
            rx.cond(
                AppState.is_report_calculated,
                rx.text("✅ 최종 계산이 완료되었습니다.", color="green.700", size="5"),
                rx.text("⏳ 계산이 완료되지 않았습니다.", color="orange.700", size="5"),
            ),
            
            rx.divider(margin_y="20px"),
            
            # 2. 총 배출량 (더미 값 또는 실제 State 값 참조)
            rx.text(
                "총 배출량 (kg CO2e):", 
                font_weight="bold"
            ),
            rx.text(
                AppState.total_carbon_emission, 
                size="8", 
                color="blue.700"
            ),
            
            # 3. 상세 내역 (데이터 개수 확인)
            rx.text(
                f"총 활동 기록 수: {AppState.all_activities.length}", 
                color="gray.600"
            ),
            
            rx.divider(margin_y="20px"),

            # 4. 재시작 버튼
            rx.button(
                "다시 시작하기",
                # 홈 또는 인트로 페이지로 돌아갑니다.
                on_click=rx.redirect("/intro"), 
                color_scheme="gray",
                size="2"
            ),
            
            spacing="5",
            align="center",
            padding="50px"
        ),
        width="100%",
        min_height="100vh"
    )