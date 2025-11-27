from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

class CarbonActivity(BaseModel):
    """탄소 활동 입력 모델"""
    category: str  # 교통, 의류, 식품, 쓰레기, 전기, 물
    activity_type: str  # 구체적 활동 유형
    value: float  # 사용자 입력 값
    unit: str  # 사용자 입력 단위 (분, 인분, 개, km 등)
    sub_category: Optional[str] = None  # 하위 카테고리 (의류: 새제품/빈티지, 식품: 육류/채소)
    timestamp: Optional[datetime] = None

class CarbonResult(BaseModel):
    """탄소 계산 결과 모델"""
    activity: CarbonActivity
    carbon_emission_kg: float  # kgCO₂e
    converted_value: float  # 변환된 표준 값
    converted_unit: str  # 변환된 표준 단위

class AvatarState(BaseModel):
    """지구 아바타 상태 모델"""
    health_score: int  # 0-100
    mood: str  # happy, neutral, sad, critical
    message: str  # 상태 메시지
    visual_emoji: str  # 시각적 표현 이모지

class Badge(BaseModel):
    """배지 모델"""
    id: str
    name: str
    description: str
    icon: str
    earned_date: Optional[datetime] = None

class DashboardData(BaseModel):
    """대시보드 데이터 모델"""
    total_carbon_today: float  # 오늘 총 배출량
    category_breakdown: Dict[str, float]  # 카테고리별 배출량
    activities: List[CarbonResult]  # 활동 내역
    avatar_state: AvatarState
    badges: List[Badge]
    daily_trend: List[Dict[str, float]]  # 일일 추이

class AICoachRequest(BaseModel):
    """AI 코칭 요청 모델"""
    activities: List[Dict]  # 평면 구조 또는 CarbonResult 모두 허용
    total_carbon: float
    category_breakdown: Dict[str, float]

class AICoachResponse(BaseModel):
    """AI 코칭 응답 모델"""
    analysis: str  # 분석 내용
    suggestions: List[str]  # 구체적 제안
    alternative_actions: List[Dict[str, str]]  # 대안 행동
    emotional_message: str  # 감성적 메시지

