# 파일 경로: backend/models.py
from pydantic import BaseModel, Field, confloat
from typing import Dict

# 음수가 들어올 수 없는 값(거리, 횟수 등)에 공통 사용
NonNegativeFloat = confloat(ge=0)


# ======================================================================
# 1) 프론트에서 전달받는 "원본 입력" 모델
#    (카테고리별 활동량 그대로 받음 — 탄소 계산 전 단계)
# ======================================================================
class UserActivityRawInput(BaseModel):
    """
    프론트에서 입력한 '카테고리별 활동량(raw data)'을 받는 모델.
    - 각 카테고리는 단위 그대로의 활동 수치(km, 시간, 개수 등)를 의미함.
    - 실제 탄소 배출량(kg CO2e) 변환은 백엔드 계산 로직에서 처리함.
    """

    category_carbon_data: Dict[str, NonNegativeFloat] = Field(
        ...,
        description="카테고리별 원본 활동 수치 (예: 교통 km, 음식 섭취량 g/개수, 전기 사용시간 등)"
    )


# ======================================================================
# 2) 탄소 계산 후 LLM에 전달하는 최종 "탄소 프로필" 모델
# ======================================================================
class UserCarbonProfile(BaseModel):
    """
    원본 입력 → 탄소 계산 로직을 거쳐 생성된 최종 탄소 배출 정보.
    이 구조가 그대로 AI 코칭 모델에 입력됨.
    """

    category_carbon_data: Dict[str, NonNegativeFloat] = Field(
        ...,
        description="카테고리별 탄소 배출량 (kg CO2e)"
    )

    total_carbon_kg: NonNegativeFloat = Field(
        ...,
        description="전체 탄소 배출량 총합 (kg CO2e)"
    )
