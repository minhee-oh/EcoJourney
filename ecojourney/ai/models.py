# 파일 경로: backend/models.py
from pydantic import BaseModel, Field, confloat
from typing import Dict

# 0 이상 값만 허용 (거리, 시간, 개수, 배출량 등)
NonNegativeFloat = confloat(ge=0)


# -------------------------------------------------------------
# 1) 프론트에서 전달받는 원본 입력 모델 (탄소 계산 전 단계)
# -------------------------------------------------------------
class UserActivityRawInput(BaseModel):
    """카테고리별 활동량(raw data)을 받는 입력 모델"""

    category_carbon_data: Dict[str, NonNegativeFloat] = Field(
        ...,
        description="카테고리별 원본 활동 수치"
    )


# -------------------------------------------------------------
# 2) 탄소 계산 후 LLM에 전달하는 최종 데이터 모델
# -------------------------------------------------------------
class UserCarbonProfile(BaseModel):
    """탄소 계산 후 생성된 최종 탄소 배출 정보"""

    category_carbon_data: Dict[str, NonNegativeFloat] = Field(
        ...,
        description="카테고리별 탄소 배출량 (kg CO2e)"
    )

    total_carbon_kg: NonNegativeFloat = Field(
        ...,
        description="총 탄소 배출량 (kg CO2e)"
    )
