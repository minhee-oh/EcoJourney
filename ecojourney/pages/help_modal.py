"""
도움말 모달 공통 컴포넌트
"""
import reflex as rx
from ..states import AppState


def help_icon_button(category: str) -> rx.Component:
    """도움말 아이콘 버튼"""
    return rx.button(
        "?",
        on_click=AppState.toggle_help_modal(category),
        size="2",
        width="32px",
        height="32px",
        border_radius="50%",
        background_color="#6B7280",
        color="white",
        font_weight="bold",
        font_size="16px",
        cursor="pointer",
        box_shadow="0 2px 8px rgba(0, 0, 0, 0.15)",
        _hover={
            "background_color": "#4B5563",
            "transform": "scale(1.1)",
            "box_shadow": "0 4px 12px rgba(0, 0, 0, 0.2)",
        },
    )


def help_modal(category: str) -> rx.Component:
    """도움말 모달 (조건부 표시)"""
    return rx.cond(
        AppState.show_help_modal & (AppState.help_category == category),
        rx.box(
            # 오버레이
            rx.box(
                on_click=AppState.close_help_modal,
                position="fixed",
                top="0",
                left="0",
                width="100%",
                height="100%",
                background_color="rgba(0, 0, 0, 0.5)",
                z_index="1000",
            ),
            # 모달 콘텐츠
            rx.box(
                _build_modal_content(category),
                position="fixed",
                top="50%",
                left="50%",
                transform="translate(-50%, -50%)",
                width="90%",
                max_width="600px",
                max_height="80vh",
                background_color="white",
                border_radius="16px",
                padding="25px",
                z_index="1001",
                box_shadow="0 10px 40px rgba(0, 0, 0, 0.3)",
                overflow_y="auto",
            ),
            position="fixed",
            top="0",
            left="0",
            width="100%",
            height="100%",
            z_index="999",
        ),
    )


def _get_category_standards(category: str) -> dict:
    """카테고리별 단위 기준 정보 반환 (컴포넌트용)"""
    standards = {
        "교통": {
            "title": "교통 카테고리 기준",
            "units": {
                "km": {
                    "description": "이동 거리를 직접 입력합니다.",
                    "examples": ["집에서 학교까지 5km", "회사까지 10km"]
                },
                "분": {
                    "description": "이동 시간을 입력하면 평균 속도로 거리를 계산합니다.",
                    "conversion": {
                        "자동차": "30km/h (도심 평균)",
                        "버스": "25km/h",
                        "지하철": "30km/h",
                        "걷기": "5km/h",
                        "자전거": "15km/h"
                    },
                    "examples": ["지하철 30분 = 약 15km", "자동차 20분 = 약 10km"]
                }
            },
            "emission_factors": {
                "자동차": "0.171 kgCO₂e/km",
                "버스": "0.089 kgCO₂e/km",
                "지하철": "0.014 kgCO₂e/km",
                "걷기": "0 kgCO₂e/km",
                "자전거": "0 kgCO₂e/km"
            }
        },
        "식품": {
            "title": "식품 카테고리 기준",
            "units": {
                "회": {
                    "description": "한끼 기준으로 입력합니다. 각 식품별 한끼당 배출 계수가 자동 적용됩니다. (출처: 한국일보 한끼 밥상 탄소 계산기)",
                    "examples": ["김밥 2회 = 0.8 kgCO₂e", "물냉면 1회 = 2.4 kgCO₂e", "소고기구이 1회 = 7.7 kgCO₂e"]
                }
            },
            "emission_factors": {
                "밥": "쌀밥 0.5, 잡곡밥 1.1, 현미밥 0.2, 보리밥 0.1, 콩밥 0.1, 김밥 0.4, 비빔밥(불고기) 1.4, 비빔밥(산채) 0.7, 김치볶음밥 0.4 kgCO₂e/한끼",
                "면": "물냉면 2.4, 비빔냉면 1.1, 잔치국수 1.8, 비빔국수 1.3, 해물칼국수 0.4 kgCO₂e/한끼",
                "국/찌개": "된장국 0.9, 미역국 2.6, 콩나물국 0.5, 된장찌개 1.5, 김치찌개 2.3, 순두부찌개 0.7, 설렁탕 10.0, 갈비탕 5.0, 곰탕 9.7 kgCO₂e/한끼",
                "반찬": "배추김치 0.3, 깍두기 0.3, 총각김치 0.1, 열무김치 0.2, 숙주나물 0.1, 콩나물무침 0.2, 시금치나물 0.5, 무생채 0.0, 소고기장조림 5.5, 멸치조림 0.1, 콩자반 0.7, 깻잎장아찌 0.1, 제육볶음 1.9, 오징어볶음 0.6, 불고기 13.9, 잡채 0.6, 고등어구이 0.3, 달걀프라이 0.1, 달걀찜 0.2 kgCO₂e/한끼",
                "고기": "소고기구이 7.7, 삼겹살구이 2.0 kgCO₂e/한끼",
                "과일": "딸기 0.1, 참외 0.1, 수박 0.1, 사과 0.1, 복숭아 0.1, 단감 0.0, 포도 0.0, 감귤 0.0, 키위 0.0, 토마토 0.1, 방울토마토 0.2 kgCO₂e/한끼",
                "패스트푸드": "피자 2.0, 햄버거세트 3.7, 후라이드치킨 2.1 kgCO₂e/한끼",
                "유제품": "우유 1.2, 치즈 11.3, 두유 0.3 kgCO₂e/한끼",
                "커피": "에스프레소 0.3, 카페라떼 0.6 kgCO₂e/한끼",
                "파스타": "Climatiq API 사용 (카르보나라, 라자냐, 라비올리, 파스타샐러드) - 1회 = 0.25kg로 변환하여 계산"
            },
            "note": "대부분의 식품은 한국일보 한끼 밥상 탄소 계산기 기준을 사용하며, 파스타만 Climatiq API를 사용합니다."
        },
        "의류": {
            "title": "의류 카테고리 기준",
            "units": {
                "개": {
                    "description": "구매한 의류의 개수를 입력합니다.",
                    "examples": ["티셔츠 2개", "청바지 1개", "신발 1켤레"]
                }
            },
            "emission_factors": {
                "티셔츠 (새제품)": "2.0 kgCO₂e/개",
                "청바지 (새제품)": "33.4 kgCO₂e/개",
                "신발 (새제품)": "13.6 kgCO₂e/개",
                "티셔츠 (빈티지)": "0.2 kgCO₂e/개 (새제품의 10%)",
                "청바지 (빈티지)": "3.34 kgCO₂e/개 (새제품의 10%)",
                "신발 (빈티지)": "1.36 kgCO₂e/개 (새제품의 10%)"
            },
            "note": "빈티지 제품은 새제품 대비 90% 탄소 배출량 감소 효과가 있습니다."
        },
        "쓰레기": {
            "title": "쓰레기 카테고리 기준",
            "units": {
                "kg": {
                    "description": "쓰레기 무게를 직접 입력합니다.",
                    "examples": ["일반 쓰레기 2kg", "플라스틱 0.5kg"]
                },
                "개": {
                    "description": "개수로 입력하면 자동으로 무게로 변환됩니다.",
                    "conversion": {
                        "캔": "0.015kg/개 (약 15g)",
                        "병": "0.4kg/개 (약 400g)"
                    },
                    "examples": ["캔 10개 = 약 0.15kg", "병 2개 = 약 0.8kg"]
                }
            },
            "emission_factors": {
                "일반 쓰레기": "0.5 kgCO₂e/kg (매립)",
                "플라스틱": "2.5 kgCO₂e/kg",
                "종이": "0.3 kgCO₂e/kg",
                "유리": "0.2 kgCO₂e/kg",
                "캔": "1.5 kgCO₂e/kg"
            }
        },
        "전기": {
            "title": "전기 카테고리 기준",
            "units": {
                "시간": {
                    "description": "사용 시간을 입력하면 자동으로 전력량(kWh)으로 변환됩니다.",
                    "conversion": {
                        "냉방기 (에어컨)": "2.0kW × 시간 = kWh",
                        "난방기 (히터)": "1.5kW × 시간 = kWh"
                    },
                    "examples": ["에어컨 3시간 = 6kWh", "히터 2시간 = 3kWh"]
                },
                "kWh": {
                    "description": "전력량을 직접 입력합니다.",
                    "examples": ["에어컨 5kWh", "히터 3kWh"]
                }
            },
            "emission_factors": {
                "냉방기": "0.424 kgCO₂e/kWh (한국 전력 배출계수)",
                "난방기": "0.424 kgCO₂e/kWh"
            }
        },
        "물": {
            "title": "물 카테고리 기준",
            "units": {
                "회": {
                    "description": "사용 횟수를 입력하면 평균 사용량으로 자동 계산됩니다.",
                    "conversion": {
                        "샤워": "70L/회 (평균 7분 × 10L/분)",
                        "설거지": "15L/회",
                        "세탁": "60L/회 (일반 세탁기 기준)"
                    },
                    "examples": ["샤워 2회 = 140L", "설거지 3회 = 45L"]
                },
                "L": {
                    "description": "리터 단위로 직접 입력합니다.",
                    "examples": ["샤워 100L", "세탁 80L"]
                }
            },
            "emission_factors": {
                "샤워": "0.0003 kgCO₂e/L",
                "설거지": "0.0003 kgCO₂e/L",
                "세탁": "0.0003 kgCO₂e/L"
            }
        }
    }
    return standards.get(category, {})


def _build_modal_content(category: str) -> rx.Component:
    """모달 콘텐츠 빌드"""
    standards = _get_category_standards(category)
    
    if not standards:
        return rx.fragment()
    
    # 단위별 설명 컴포넌트 생성
    unit_components = []
    for unit_key, unit_info in standards.get("units", {}).items():
        unit_components.append(
            rx.box(
                rx.vstack(
                    rx.heading(
                        f"단위: {unit_key}",
                        size="5",
                        color="blue.700",
                        margin_bottom="10px",
                    ),
                    rx.text(
                        unit_info.get("description", ""),
                        size="3",
                        margin_bottom="8px",
                    ),
                    _build_conversion_info(unit_info),
                    _build_serving_info(unit_info),
                    _build_examples(unit_info),
                    spacing="2",
                    align="start",
                ),
                padding="15px",
                border="1px solid",
                border_color="gray.200",
                border_radius="8px",
                margin_bottom="10px",
                background="gray.50",
            )
        )
    
    # 배출 계수 컴포넌트 생성
    emission_factors = standards.get("emission_factors", {})
    has_emission_factors = bool(emission_factors)
    factor_components = []
    for factor_key, factor_value in emission_factors.items():
        factor_components.append(
            rx.text(
                f"• {factor_key}: {factor_value}",
                size="2",
                color="gray.600",
                margin_bottom="5px",
            )
        )
    
    return rx.vstack(
        # 헤더
        rx.hstack(
            rx.heading(standards.get("title", "기준 정보"), size="6"),
            rx.spacer(),
            rx.button(
                "✕",
                on_click=AppState.close_help_modal,
                variant="ghost",
                size="2",
            ),
            width="100%",
            align="center",
        ),
        rx.divider(margin_y="15px"),
        
        # 단위별 설명
        *unit_components,
        
        # 배출 계수
        rx.cond(
            has_emission_factors,
            rx.box(
                rx.vstack(
                    rx.heading("탄소 배출 계수", size="5", color="red.700", margin_bottom="10px"),
                    *factor_components,
                    spacing="1",
                    align="start",
                ),
                padding="15px",
                border="1px solid",
                border_color="red.200",
                border_radius="8px",
                background="red.50",
                margin_top="10px",
            ),
        ),
        
        # 추가 노트
        rx.cond(
            standards.get("note"),
            rx.text(
                standards.get("note", ""),
                size="2",
                color="blue.600",
                font_style="italic",
                margin_top="10px",
            ),
        ),
        
        # 닫기 버튼
        rx.button(
            "닫기",
            on_click=AppState.close_help_modal,
            color_scheme="blue",
            margin_top="20px",
        ),
        
        spacing="3",
        align="start",
        width="100%",
    )


def _build_conversion_info(unit_info: dict) -> rx.Component:
    """변환 기준 정보 빌드"""
    conversion = unit_info.get("conversion", {})
    if not conversion:
        return rx.fragment()
    
    conv_components = [
        rx.text(
            f"  • {k}: {v}",
            size="2",
            color="gray.600",
        )
        for k, v in conversion.items()
    ]
    
    return rx.vstack(
        rx.text("변환 기준:", font_weight="bold", size="3", margin_top="8px"),
        *conv_components,
        spacing="1",
        align="start",
    )


def _build_serving_info(unit_info: dict) -> rx.Component:
    """1회 기준량 정보 빌드"""
    serving_sizes = unit_info.get("serving_sizes", {})
    if not serving_sizes:
        return rx.fragment()
    
    serving_components = [
        rx.text(
            f"  • {k}: {v}",
            size="2",
            color="gray.600",
        )
        for k, v in serving_sizes.items()
    ]
    
    return rx.vstack(
        rx.text("1회 기준량:", font_weight="bold", size="3", margin_top="8px"),
        *serving_components,
        spacing="1",
        align="start",
    )


def _build_examples(unit_info: dict) -> rx.Component:
    """예시 정보 빌드"""
    examples = unit_info.get("examples", [])
    if not examples:
        return rx.fragment()
    
    example_components = [
        rx.text(
            f"  • {ex}",
            size="2",
            color="gray.600",
        )
        for ex in examples
    ]
    
    return rx.vstack(
        rx.text("예시:", font_weight="bold", size="3", margin_top="8px"),
        *example_components,
        spacing="1",
        align="start",
    )

