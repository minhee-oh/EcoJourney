# 파일 경로: ecojourney/ai/llm_service.py
# 탄소 배출량 데이터를 바탕으로
# AI(Gemini)를 호출해 코칭 리포트를 생성하고,
# 실패 시에도 항상 사용할 수 있는 대체 응답을 제공하는 서비스 모듈
import json
import logging
import os
from typing import Dict, Any

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# -------------------------------
# 1) .env 파일에서 API 키 로드
# -------------------------------
load_dotenv(override=True) # 프로젝트 루트(OpenSourceProject/.env)에서 로드

# Gemini API 설정
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # .env에서 키 읽기
MODEL_NAME = "gemini-flash-latest"

# 🔍 디버그용: 키 앞부분만 찍어보기 (None일 때도 안전하게)
key_prefix = GEMINI_API_KEY[:8] if GEMINI_API_KEY else "NONE"
print(f"[DEBUG] llm_service loaded. GEMINI_API_KEY prefix: {key_prefix}")
logger.info(f"[llm_service] GEMINI_API_KEY prefix: {key_prefix}")

if not GEMINI_API_KEY:
    logger.error("[llm_service] ❌ GEMINI_API_KEY 환경변수가 없습니다. .env 파일을 확인하세요.")
else:
    logger.info("[llm_service] 🔑 Gemini API Key 로드 성공")

# -------------------------------
# 2) Gemini SDK 로딩
# -------------------------------
try:
    import google.generativeai as genai
except ImportError:
    genai = None
    logger.error("[llm_service] google-generativeai 패키지가 없습니다. pip install 필요.")

# -------------------------------
# 3) Gemini 초기화
# -------------------------------
if genai and GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        logger.info("[llm_service] Gemini API 설정 완료")
    except Exception as e:
        logger.error(f"[llm_service] Gemini 초기화 실패: {e}")
else:
    logger.warning("[llm_service] Gemini 사용 불가 → 시뮬레이션 응답 사용")


# ======================================================================
# 1) Gemini 실패 시 사용할 폴백(기본 응답)
# ======================================================================
def _build_simulated_response(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Gemini 호출 실패 시 기본 템플릿 기반 JSON 응답 생성"""

    def _safe_float(value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    # 원본 데이터
    raw_carbon_data = user_data.get("category_carbon_data", {}) or {}

    # 모든 값을 float으로 한 번 정리
    carbon_data = {
        k: _safe_float(v) for k, v in raw_carbon_data.items()
    }

    total_carbon_kg = _safe_float(user_data.get("total_carbon_kg", 0.0))

    # 데이터 있는지 체크 (0보다 큰 값이 하나라도 있는지)
    has_data = bool(carbon_data) and any(v > 0 for v in carbon_data.values())

    # 데이터가 있을 때
    if has_data:
        max_category = max(carbon_data, key=carbon_data.get)
        max_value = carbon_data[max_category]
        total = sum(carbon_data.values()) or 1.0
        max_ratio = (max_value / total) * 100

        # 두 번째 카테고리
        sorted_items = sorted(carbon_data.items(), key=lambda x: x[1], reverse=True)
        second_category, second_value = (None, 0.0)
        if len(sorted_items) >= 2:
            second_category, second_value = sorted_items[1]

        # 지구 상태 레벨(간단 계산)
        if total_carbon_kg <= 2:
            earth_level = "Level 1 - 아주 상쾌해요 🍃"
        elif total_carbon_kg <= 5:
            earth_level = "Level 2 - 꽤 괜찮은 하루예요 🙂"
        else:
            earth_level = "Level 3 - 조금 지친 하루예요 🌏"

        report_title = f"오늘 하루 탄소 진단 결과 ({total_carbon_kg:.2f} kg CO2e)"

        today_result_screen = {
            "usage_summary_text": f"오늘 탄소 사용량은 총 {total_carbon_kg:.2f} kg CO2e예요.",
            "category_ratio_text": (
                f"{max_ratio:.0f}%가 '{max_category}'에서 발생했고, "
                f"다음은 '{second_category}'입니다." if second_category
                else f"거의 대부분이 '{max_category}'에서 발생했어요."
            ),
            "money_saving_text": "오늘 패턴만 조정해도 한 달 기준 생활비 절감 여지가 있어요.",
            "earth_status_text": f"오늘의 지구 상태는 {earth_level}",
        }

        final_summary = (
            f"오늘 총 배출량은 {total_carbon_kg:.2f} kg CO2e. "
            f"'{max_category}' 비중이 가장 높고, "
            f"'{second_category}'가 뒤를 잇습니다." if second_category
            else f"오늘은 '{max_category}' 한 영역에 사용량이 몰린 패턴이에요."
        )

        category_chart_text = (
            f"그래프에서도 '{max_category}'와 '{second_category}'가 두드러집니다."
            if second_category else
            f"'{max_category}'가 다른 카테고리보다 높게 나타나요."
        )

        recommendations = [
            {
                "action": f"'{max_category}' 사용량 20% 줄이기",
                "detail": (
                    f"'{max_category}' 사용이 높았던 이유를 떠올리고, "
                    "가장 반복된 행동 1개만 20% 줄여보세요."
                ),
                "impact": f"{max_value * 0.2:.2f} kg CO2e 감축 가능",
                "reason": f"'{max_category}'가 오늘 배출의 핵심 요인이기 때문입니다.",
            },
            {
                "action": "비슷한 상황을 위한 플랜 B 만들기",
                "detail": (
                    "행동 패턴을 맞추거나 예측은 어렵기에 그냥 아예 대안 자체를 추천하는 걸로 가야합니다,"
                    "각 카테고리별로 뻔하지 않은 대안들을 추천하세요."
                ),
                "impact": "반복될수록 감축 효과가 누적됩니다.",
                "reason": "오늘 데이터가 반복 패턴의 힌트를 제공하기 때문입니다.",
            },
            {
                "action": "실생활에서 할 수 있는 현실적인 대안을 생각해서 추천해주기",
                "detail": (
                    "뻔한 내용이여도 디테일을 추가해서 더 섬세해보이게, "
                    "수치나 결과론적인 것들로 더욱더 잘 보이게 해주세요."
                ),
                "impact": "카테고리별 배출량을 파악해서 대안 추천하기, 뻔한 '채소를 드세요.', '승용차 대신 버스를 이용하세요', '옷을 오래 입으세요', '분리수거를 잘하세요', '물이나 전기를 아끼세요' 금지",
                "reason": "사용자가 흥미를 가지기 위해서, 그리고 다른 웹사이트나 정보에 대한 차별성을 두기 위해서 입니다.",
            },
        ]

        simulated = {
            "report_title": report_title,
            "today_result_screen": today_result_screen,
            "final_report_screen": {
                "total_summary_text": final_summary,
                "category_chart_text": category_chart_text,
                "focus_area": max_category,
                "recommendations": recommendations,
                "policy_recommendations": [],
                "closing_message": (
                    f"추천 중 한 가지만 실행해도 '{max_category}' 개선에 큰 도움이 됩니다."
                ),
            },
        }

    # 데이터 없을 때
    else:
        simulated = {
            "report_title": "오늘은 기록된 탄소 데이터가 부족해요.",
            "today_result_screen": {
                "usage_summary_text": "탄소 사용량 기록이 거의 없습니다.",
                "category_ratio_text": "카테고리 기록이 없으면 분석이 어렵습니다.",
                "money_saving_text": "기록을 시작하면 절감 지점을 더 정확히 찾을 수 있어요.",
                "earth_status_text": "내일부터 한 카테고리만 기록해봐도 의미가 생겨요.",
            },
            "final_report_screen": {
                "total_summary_text": "데이터가 부족하여 패턴 분석이 어렵습니다.",
                "category_chart_text": "차트를 그릴 수 있는 정보가 부족합니다.",
                "focus_area": "기록 시작하기",
                "recommendations": [
                    {
                        "action": "내일 카테고리 하나만 기록하기",
                        "detail": "교통·음식 등 한 영역만 숫자로 기록해보세요.",
                        "impact": "기록이 쌓이면 정확한 감축 전략 도출 가능",
                        "reason": "현재는 분석 가능한 정보가 없기 때문입니다.",
                    }
                ],
                "policy_recommendations": [],
                "closing_message": "부담 없이 내일 한 카테고리만 기록해봐요.",
            },
        }

    return simulated



# ======================================================================
# 2) Gemini 호출 + JSON 파싱
# ======================================================================
def call_llm_api(prompt: str, user_data: Dict[str, Any]) -> str:
    """Gemini 호출 → JSON 파싱 → 실패 시 폴백 JSON 반환"""
    if not genai or not GEMINI_API_KEY:
        simulated = _build_simulated_response(user_data)
        return json.dumps(simulated, ensure_ascii=False, indent=4)

    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        raw_text = (response.text or "").strip()

        # 코드블록(```) 제거
        if raw_text.startswith("```"):
            lines = raw_text.splitlines()
            if len(lines) >= 2 and lines[0].startswith("```") and lines[-1].startswith("```"):
                lines = lines[1:-1]
            if lines and lines[0].strip().lower() == "json":
                lines = lines[1:]
            raw_text = "\n".join(lines).strip()

        # JSON 파싱
        parsed = json.loads(raw_text)
        return json.dumps(parsed, ensure_ascii=False, indent=4)

    except Exception as e:
        logger.error("[llm_service] Gemini 실패 → 폴백 사용: %s", e)
        simulated = _build_simulated_response(user_data)
        return json.dumps(simulated, ensure_ascii=False, indent=4)


# ======================================================================
# 3) 외부 호출용 메인 함수
# ======================================================================
def get_coaching_feedback(user_data: Dict[str, Any]) -> str:
    """coaching_api에서 호출하는 LLM 피드백 생성 진입점"""
    from ecojourney.config.coaching_rules import COACHING_KNOWLEDGE_RULE

    prompt = create_coaching_prompt(user_data, COACHING_KNOWLEDGE_RULE)
    return call_llm_api(prompt, user_data)


# ======================================================================
# 4) 프롬프트 생성
# ======================================================================
def create_coaching_prompt(
    user_data: Dict[str, Any],
    knowledge_rule: Dict[str, Any],
) -> str:
    """오늘 하루 데이터 기반 프롬프트 생성"""
    carbon_data = (
        user_data.get("category_carbon_data")
        or user_data.get("category_activity_data")
        or {}
    )

    total_carbon_kg = user_data.get("total_carbon_kg")
    if total_carbon_kg is None:
        try:
            total_carbon_kg = float(sum(carbon_data.values())) if carbon_data else 0.0
        except Exception:
            total_carbon_kg = 0.0
    else:
        try:
            total_carbon_kg = float(total_carbon_kg)
        except Exception:
            total_carbon_kg = 0.0

    category_summary = (
        "\n".join([f"- {k}: {float(v):.2f} kg CO2e" for k, v in carbon_data.items()])
        if carbon_data else "- 상세 데이터 없음"
    )

    data_summary = (
        "## [사용자 오늘 하루 탄소 데이터]\n"
        f"- 총 배출량: {total_carbon_kg:.2f} kg CO2e\n"
        "## [카테고리별 배출량]\n"
        f"{category_summary}\n"
    )

    system_instruction = knowledge_rule["system_instruction"]
    coaching_principles = "\n\n".join(
        [f"- {p}" for p in knowledge_rule.get("coaching_principles", [])]
    )
    json_schema = json.dumps(
        knowledge_rule["json_schema"],
        ensure_ascii=False,
        indent=2,
    )

    # 최종 프롬프트 구성
    prompt = f"""
{system_instruction}

[데이터 분석 원칙]
{coaching_principles}

[사용자 입력 데이터]
{data_summary}

[출력 형식]
아래 JSON 스키마를 따르는 **하나의 JSON 객체만** 출력하세요.
설명문·코드블록(```) 금지.

JSON 스키마:
{json_schema}

[추가 조건]
- 한국어로 작성.
- 오늘 하루 데이터만 기준.
- 행동 추천 3~5개 포함.
- 정책/혜택 추천은 1~2개(없으면 빈 배열).
"""

    return prompt.strip()
