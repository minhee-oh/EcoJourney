"""
기본 UI 상태 및 공통 기능
"""

import reflex as rx
from typing import Dict, List, Any

# CATEGORY_CONFIG: 모든 카테고리 데이터를 담는 핵심 딕셔너리
CATEGORY_CONFIG = {
    "교통": {
        "path": "transportation",
        "description": "오늘의 교통 수단 이용량(거리 또는 시간)을 입력해주세요.",
        "activities": ["자동차", "지하철", "버스", "걷기", "자전거"],
        "units": ["km", "분"],
        "inputs_key": "transport_inputs"
    },
    "식품": {
        "path": "food",
        "description": "오늘 섭취한 주요 식품 카테고리를 입력해주세요.",
        "activities": ["육류", "채소/과일", "가공식품", "유제품"],
        "units": ["g", "회"],
        "inputs_key": "food_inputs"
    },
    "의류": {
        "path": "clothing",
        "description": "오늘 쇼핑한 의류 및 잡화의 종류와 개수를 입력해주세요.",
        "activities": ["상의", "하의", "신발", "가방/잡화"],
        "units": ["개"],
        "inputs_key": "clothing_inputs"
    }
}

CATEGORY_ORDER = list(CATEGORY_CONFIG.keys())

# 탄소 배출량 데이터를 저장할 딕셔너리 구조 정의
CarbonActivity = Dict[str, Any]

TRANSPORT_LIST = ["자동차", "버스", "지하철", "걷기", "자전거"]
FOOD_LIST = ["육류", "야채류", "유제품류", "기타"]


class BaseState(rx.State):
    """
    기본 UI 상태 및 공통 기능
    """
    current_category: str = "교통"
    all_activities: List[CarbonActivity] = []
    
    # 결과 리포트 데이터
    total_carbon_emission: float = 0.0
    is_report_calculated: bool = False
    calculation_details: List[Dict[str, Any]] = []  # 상세 계산 내역
    
    # 절약량 관련 데이터
    total_saved_emission: float = 0.0  # 총 절약한 탄소 배출량 (kgCO2e)
    saved_money: float = 0.0  # 절약한 금액 (원)
    savings_details: List[Dict[str, Any]] = []  # 절약 상세 내역
    
    # 포인트 관련 데이터
    points_breakdown: Dict[str, int] = {}  # 포인트 상세 내역 (절약량, 빈티지, 평균 대비)
    total_points_earned: int = 0  # 총 획득 포인트
    
    # 도움말 모달 상태
    show_help_modal: bool = False
    help_category: str = ""
    
    def toggle_help_modal(self, category: str = ""):
        """도움말 모달 토글"""
        self.help_category = category
        self.show_help_modal = not self.show_help_modal
    
    def close_help_modal(self):
        """도움말 모달 닫기"""
        self.show_help_modal = False
    
    def get_category_standards(self, category: str) -> Dict[str, Any]:
        """카테고리별 단위 기준 정보 반환"""
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
                        "description": "식사 횟수로 입력합니다. 각 식품별 1회 기준량이 자동 적용됩니다.",
                        "serving_sizes": {
                            "소고기": "200g/회",
                            "돼지고기": "150g/회",
                            "닭고기": "150g/회",
                            "쌀밥": "200g/회 (1공기)",
                            "커피": "15g/회 (원두 기준)",
                            "우유": "200ml/회 (1잔)"
                        }
                    },
                    "g": {
                        "description": "그램 단위로 직접 입력합니다.",
                        "examples": ["소고기 300g", "쌀밥 400g"]
                    }
                },
                "emission_factors": {
                    "소고기": "27.0 kgCO₂e/kg",
                    "돼지고기": "12.1 kgCO₂e/kg"
                }
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