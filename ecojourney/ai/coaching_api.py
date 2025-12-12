# 파일 경로: ecojourney/ai/coaching_api.py
# 탄소 계산이 끝난 결과를 받아
# AI에게 전달하고,
# AI 피드백을 다시 프론트로 돌려주는 중간 관문 API

from typing import Dict, Any
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from ecojourney.ai.llm_service import get_coaching_feedback

router = APIRouter(
    prefix="/api/v1",
    tags=["coaching"]
)


@router.post("/generate-feedback")
async def generate_feedback_endpoint(user_data: Dict[str, Any]):
    """
    EcoJourney 탄소 계산 로직을 거쳐 생성된
    '카테고리별 탄소 배출량(kg CO2e)' 데이터를 입력받아
    - 기본 구조 검증
    - total_carbon_kg 계산
    - AI 피드백 생성을 수행하는 엔드포인트.

    ※ 주의: 이 API는 '탄소 계산 전 원본 데이터(raw)'가 아니라
            '탄소 계산이 끝난 최종 CO2 배출량 값'을 받는다.
    """

    payload = dict(user_data)
    raw_carbon_data = payload.get("category_carbon_data")

    # --------------------------------------------------
    # 1) category_carbon_data 존재 + dict 구조 확인
    #    - 탄소 계산 결과는 반드시 {카테고리: 수치} 형태여야 함
    # --------------------------------------------------
    if not isinstance(raw_carbon_data, dict):
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "error_message": "category_carbon_data는 반드시 객체(딕셔너리) 형식이어야 합니다."
            }
        )

    # --------------------------------------------------
    # 2) 빈 dict → 분석할 데이터가 없음
    # --------------------------------------------------
    if len(raw_carbon_data) == 0:
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "error_message": "최소 한 개 이상의 카테고리 탄소값이 필요합니다."
            }
        )

    # --------------------------------------------------
    # 3) 탄소 계산 로직에서 이미 숫자로 보장된 값이 전달됨
    #    → 추가 변환 없이 그대로 사용
    # --------------------------------------------------
    carbon_data = raw_carbon_data

    # --------------------------------------------------
    # 4) 모든 값이 0이면 AI가 의미 있는 분석을 할 수 없음
    # --------------------------------------------------
    total = sum(carbon_data.values())
    if total <= 0:
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "error_message": "모든 카테고리 값이 0입니다. 분석을 위해 0보다 큰 값이 하나 이상 필요합니다."
            }
        )

    # --------------------------------------------------
    # 5) payload 정제 (total 자동 계산)
    # --------------------------------------------------
    payload["category_carbon_data"] = carbon_data
    payload["total_carbon_kg"] = total

    # DEBUG 로그
    print("\n====== [DEBUG] /generate-feedback payload (normalized) ======")
    print(payload)
    print("=============================================================\n")

    # --------------------------------------------------
    # 6) AI 분석 수행 (Gemini 또는 fallback)
    # --------------------------------------------------
    try:
        feedback_json_string = get_coaching_feedback(payload)
    except TimeoutError as e:
        print(f"[AI TIMEOUT] {e}")
        return JSONResponse(
            status_code=504,
            content={
                "status": "error",
                "error_message": "AI 응답이 지연되고 있습니다. 잠시 후 다시 시도해주세요."
            }
        )
    except Exception as e:
        print(f"[AI ERROR] {e}")
        return JSONResponse(
            status_code=502,
            content={
                "status": "error",
                "error_message": "AI 피드백 생성 중 오류가 발생했습니다."
            }
        )

    # --------------------------------------------------
    # 7) 정상 응답 반환
    # --------------------------------------------------
    return {
        "status": "success",
        "data": feedback_json_string
    }
