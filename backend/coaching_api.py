# 파일 경로: backend/coaching_api.py
from fastapi import APIRouter, HTTPException
from backend.models import UserActivityRawInput
from backend.services.llm_service import get_coaching_feedback

# ==============================================================================
# 탄소 코칭 API 라우터 정의
# - 프론트엔드에서 카테고리별 "숫자 기반" 탄소 배출량을 받아 AI 코칭 리포트 생성
# ==============================================================================

router = APIRouter(
    prefix="/api/v1",
    tags=["coaching"]
)

@router.post("/generate-feedback")
async def generate_feedback_endpoint(user_data: UserActivityRawInput):
    """
    카테고리별 주간 탄소 배출 요약 데이터를 받아
    AI 코칭 피드백(리포트)을 생성하여 JSON 문자열로 반환합니다.

    요청 바디 예시:
    {
        "category_carbon_data": {
            "교통": 1.25,
            "식품": 0.80,
            "전기": 0.45,
            "의류": 2.0,
            "쓰레기 배출": 5.0,
            "물 사용 : 2.0
        },
        "total_carbon_kg": 2.50
    }

    ※ 각 카테고리별 수치는 모두 프론트에서 단위(km, 시간, g 등)를 고려해 계산한 값입니다.
    """
    try:
        feedback_json_string = get_coaching_feedback(user_data.model_dump())

        # 프론트에서 그대로 JSON.parse() 할 수 있도록 문자열로 전달
        return {
            "status": "success",
            "data": feedback_json_string
        }

    except Exception as e:
        print(f"Error during feedback generation: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error: Could not generate AI feedback."
        )
