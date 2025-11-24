"""
FastAPI 백엔드 서버
탄소 계산 및 AI 코칭 API 제공
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
from datetime import datetime

from service.models import (
    CarbonActivity, CarbonResult, AICoachRequest, AICoachResponse,
    DashboardData, AvatarState, Badge
)
from service.carbon_calculator import (
    calculate_carbon_emission, get_category_activities, get_category_units
)
from service.ai_coach import generate_coaching_message
from service.average_data import (
    get_average_emission, get_total_average, compare_with_average
)

app = FastAPI(title="탄소 발자국 계산 API", version="1.0.0")

# CORS 설정 (Streamlit에서 접근 가능하도록)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """API 상태 확인"""
    return {"message": "탄소 발자국 계산 API", "status": "running"}


@app.get("/categories")
async def get_categories():
    """지원하는 카테고리 목록 반환"""
    return {
        "categories": ["교통", "의류", "식품", "쓰레기", "전기", "물"]
    }


@app.get("/categories/{category}/activities")
async def get_activities(category: str):
    """카테고리별 활동 유형 목록 반환"""
    activities = get_category_activities(category)
    if not activities:
        raise HTTPException(status_code=404, detail=f"카테고리 '{category}'를 찾을 수 없습니다.")
    return {"category": category, "activities": activities}


@app.get("/categories/{category}/units")
async def get_units(category: str, activity_type: str = None):
    """카테고리별 입력 가능한 단위 목록 반환"""
    units = get_category_units(category, activity_type)
    if not units:
        raise HTTPException(status_code=404, detail=f"카테고리 '{category}'를 찾을 수 없습니다.")
    return {"category": category, "activity_type": activity_type, "units": units}


@app.get("/categories/{category}/sub_categories")
async def get_sub_categories(category: str):
    """카테고리별 하위 카테고리 목록 반환"""
    from service.carbon_calculator import get_sub_categories
    sub_cats = get_sub_categories(category)
    return {"category": category, "sub_categories": sub_cats}


@app.post("/calculate", response_model=CarbonResult)
async def calculate_carbon(activity: CarbonActivity):
    """
    탄소 배출량 계산
    
    Args:
        activity: 탄소 활동 입력 데이터
    
    Returns:
        탄소 계산 결과
    """
    try:
        result = calculate_carbon_emission(
            category=activity.category,
            activity_type=activity.activity_type,
            value=activity.value,
            unit=activity.unit,
            sub_category=activity.sub_category
        )
        
        return CarbonResult(
            activity=activity,
            carbon_emission_kg=result["carbon_emission_kg"],
            converted_value=result["converted_value"],
            converted_unit=result["converted_unit"]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"계산 중 오류 발생: {str(e)}")


@app.post("/coach", response_model=AICoachResponse)
async def get_ai_coaching(request: AICoachRequest):
    """
    AI 기반 맞춤형 코칭 제공
    
    Args:
        request: AI 코칭 요청 데이터
    
    Returns:
        AI 코칭 응답
    """
    try:
        return generate_coaching_message(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 코칭 생성 중 오류 발생: {str(e)}")


@app.post("/avatar/state")
async def get_avatar_state(total_carbon: float, daily_limit: float = 10.0):
    """
    지구 아바타 상태 계산
    
    Args:
        total_carbon: 오늘 총 탄소 배출량 (kgCO₂e)
        daily_limit: 일일 권장 한도 (kgCO₂e, 기본값 10.0)
    
    Returns:
        아바타 상태
    """
    # 건강 점수 계산 (0-100)
    if total_carbon <= daily_limit * 0.5:
        health_score = 100
        mood = "happy"
        message = "완벽해요! 지구가 행복해하고 있어요 🌍✨"
        emoji = "🌍✨"
    elif total_carbon <= daily_limit * 0.7:
        health_score = 80
        mood = "happy"
        message = "좋아요! 계속 이렇게 지켜주세요 🌱"
        emoji = "🌱"
    elif total_carbon <= daily_limit:
        health_score = 60
        mood = "neutral"
        message = "괜찮아요. 조금만 더 노력해볼까요? 🌍"
        emoji = "🌍"
    elif total_carbon <= daily_limit * 1.5:
        health_score = 40
        mood = "sad"
        message = "지구가 조금 힘들어하고 있어요. 조금만 줄여볼까요? 😔"
        emoji = "🌍😔"
    else:
        health_score = 20
        mood = "critical"
        message = "지구가 위험해요! 지금 바로 행동이 필요해요! 🚨"
        emoji = "🌍🚨"
    
    return AvatarState(
        health_score=health_score,
        mood=mood,
        message=message,
        visual_emoji=emoji
    )


@app.post("/badges/check")
async def check_badges(activities: List[Dict]):
    """
    배지 획득 조건 확인 (모든 사용자에게 랭크 배지 부여)
    
    Args:
        activities: 활동 내역
    
    Returns:
        획득한 배지 목록 (랭크 배지 포함)
    """
    badges = []
    
    # 활동 데이터에서 category와 activity_type 추출
    def get_category(act):
        if isinstance(act, dict):
            if "activity" in act and isinstance(act["activity"], dict):
                return act["activity"].get("category")
            return act.get("category")
        return None
    
    def get_activity_type(act):
        if isinstance(act, dict):
            if "activity" in act and isinstance(act["activity"], dict):
                return act["activity"].get("activity_type")
            return act.get("activity_type")
        return None
    
    def get_carbon(act):
        if isinstance(act, dict):
            return act.get("carbon_emission_kg", 0)
        return 0
    
    # 총 탄소 배출량 계산
    total_carbon = sum(get_carbon(act) for act in activities)
    
    # 평균 배출량 가져오기 (한국인 일일 평균)
    from service.average_data import get_total_average
    average_emission = get_total_average()
    
    # 랭크 배지 부여 (모든 사용자에게)
    if total_carbon <= average_emission * 0.5:
        # 평균의 50% 이하 - 최고 등급
        badges.append(Badge(
            id="rank_s",
            name="🌍 지구 수호자",
            description="평균보다 훨씬 낮은 배출량이에요! 정말 훌륭해요!",
            icon="🌍✨",
            earned_date=datetime.now()
        ))
    elif total_carbon <= average_emission * 0.7:
        # 평균의 70% 이하 - 우수 등급
        badges.append(Badge(
            id="rank_a",
            name="🌱 환경 지킴이",
            description="평균보다 낮은 배출량이에요! 잘하고 계세요!",
            icon="🌱",
            earned_date=datetime.now()
        ))
    elif total_carbon <= average_emission:
        # 평균 이하 - 양호 등급
        badges.append(Badge(
            id="rank_b",
            name="💚 친환경 실천가",
            description="평균 수준의 배출량이에요. 조금만 더 노력하면 더 좋아질 거예요!",
            icon="💚",
            earned_date=datetime.now()
        ))
    elif total_carbon <= average_emission * 1.3:
        # 평균의 130% 이하 - 보통 등급
        badges.append(Badge(
            id="rank_c",
            name="🌿 성장 중",
            description="평균보다 조금 높지만, 조금씩 줄여가면 좋을 거예요!",
            icon="🌿",
            earned_date=datetime.now()
        ))
    else:
        # 평균의 130% 초과 - 개선 필요 등급
        badges.append(Badge(
            id="rank_d",
            name="🌎 개선의 여지",
            description="평균보다 높지만, 작은 변화로도 큰 개선이 가능해요. 함께 노력해봐요!",
            icon="🌎",
            earned_date=datetime.now()
        ))
    
    # 특별 배지 (기존 조건 유지)
    # 채식주의자 배지 (식품 카테고리에서 육류 없음)
    has_meat = any(
        get_category(act) == "식품" and 
        get_activity_type(act) in ["소고기", "쇠고기", "돼지고기", "닭고기"]
        for act in activities
    )
    if not has_meat and any(get_category(act) == "식품" for act in activities):
        badges.append(Badge(
            id="vegetarian",
            name="채식주의자",
            description="하루 동안 육류 없이 식사하셨어요!",
            icon="🥬",
            earned_date=datetime.now()
        ))
    
    # 대중교통 이용 배지
    public_transport_count = sum(
        1 for act in activities
        if get_category(act) == "교통" and
        get_activity_type(act) in ["버스", "지하철"]
    )
    if public_transport_count >= 3:
        badges.append(Badge(
            id="public_transport",
            name="대중교통 애호가",
            description="대중교통을 3회 이상 이용하셨어요!",
            icon="🚇",
            earned_date=datetime.now()
        ))
    
    # 절약왕 배지 (하루 총 배출량이 5kgCO₂e 이하)
    if total_carbon <= 5.0 and len(activities) > 0:
        badges.append(Badge(
            id="saver",
            name="절약왕",
            description="하루 배출량을 5kgCO₂e 이하로 유지하셨어요!",
            icon="👑",
            earned_date=datetime.now()
        ))
    
    return {"badges": badges}


@app.get("/average/{category}")
async def get_category_average(category: str):
    """카테고리별 평균 배출량 반환"""
    return {
        "category": category,
        "average_emission": get_average_emission(category)
    }


@app.get("/average")
async def get_total_average_emission():
    """전체 평균 일일 배출량 반환"""
    return {
        "total_average": get_total_average(),
        "category_averages": {
            cat: get_average_emission(cat)
            for cat in ["교통", "의류", "식품", "쓰레기", "전기", "물"]
        }
    }


@app.post("/compare")
async def compare_emissions(user_data: Dict):
    """
    사용자 배출량과 평균 비교
    
    Args:
        user_data: {"category": "교통", "emission": 2.5} 또는 {"total": 8.0}
    """
    try:
        if "category" in user_data:
            return compare_with_average(
                user_data.get("emission", 0),
                user_data["category"]
            )
        else:
            return compare_with_average(
                user_data.get("total", 0),
                None
            )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"비교 중 오류 발생: {str(e)}")

