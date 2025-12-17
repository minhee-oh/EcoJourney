# 파일 경로: ecojourney/coaching_api.py
import logging
from fastapi import APIRouter, HTTPException
from ecojourney.ai.models import UserActivityRawInput
from ecojourney.ai.llm_service import get_coaching_feedback

logger = logging.getLogger(__name__)
# 배포 환경에서 불필요한 콘솔 출력 방지(에러만 기록)
logger.setLevel(logging.ERROR)

router = APIRouter(
    prefix="/api/v1",
    tags=["coaching"]
)

@router.post("/generate-feedback")
async def generate_feedback_endpoint(user_data: UserActivityRawInput):
    """카테고리별 탄소 배출 데이터를 받아 AI 코칭 리포트를 생성하는 엔드포인트"""
    try:
        # 입력 데이터 → dict 변환
        payload = user_data.model_dump()

        # 카테고리별 탄소 데이터
        carbon_data = payload.get("category_carbon_data") or {}

        # total_carbon_kg 자동 계산
        if "total_carbon_kg" not in payload:
            try:
                payload["total_carbon_kg"] = float(sum(carbon_data.values()))
            except Exception:
                payload["total_carbon_kg"] = 0.0

        # LLM 호출
        feedback_json_string = get_coaching_feedback(payload)

        return {
            "status": "success",
            "data": feedback_json_string,
        }

    except Exception as e:
        logger.error(f"[AI] Error during feedback generation: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error: Could not generate AI feedback.",
        )
