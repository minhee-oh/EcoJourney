# backend/services/llm_service.py

import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

GEMINI_API_KEY = "AIzaSyAkTtjvEMESxHdFebJ5CQs5Nd_d0nnHWnU"

MODEL_NAME = "gemini-flash-latest"

try:
    import google.generativeai as genai
except ImportError:
    genai = None
    logger.error(
        "[llm_service] google-generativeai 패키지가 없습니다. "
        "venv에서 `pip install google-generativeai` 먼저 실행하세요."
    )

if genai and GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    logger.info("[llm_service] Gemini API 키 설정 완료 → 실제 LLM 호출 사용")
else:
    logger.warning(
        "[llm_service] Gemini 설정 불가 → 시뮬레이션 응답만 사용됩니다."
    )


# ----------------------------------------------------------------------
# 폴백: Gemini 안 될 때 쓰는 시뮬레이션 응답
# ----------------------------------------------------------------------
def _build_simulated_response(user_data: Dict[str, Any]) -> Dict[str, Any]:
    carbon_data: Dict[str, float] = user_data.get("category_carbon_data", {}) or {}
    total_carbon_kg: float = user_data.get("total_carbon_kg", 0.0)

    if carbon_data:
        max_category = max(carbon_data, key=carbon_data.get)
        max_carbon_kg = carbon_data[max_category]
    else:
        max_category = "분석 불가"
        max_carbon_kg = 0.0

    highlight_message = (
        f"이번 주에는 **'{max_category}'** 카테고리에서 탄소 배출이 가장 많았어요. "
        f"이 영역에서만 약 {max_carbon_kg:.2f}kg CO₂e가 발생했습니다. "
    )

    return {
        "title": f"사용자 님의 주간 탄소 라이프 진단 결과 (총 {total_carbon_kg:.2f}kg CO₂e)",
        "summary": (
            f"이번 주 사용자 님은 여러 영역에서 환경을 신경 쓰셨지만, "
            f"특히 {max_category} 카테고리에서 배출량이 두드러졌어요. "
            "그래도 이미 데이터를 기록하고 돌아보는 것만으로 큰 첫걸음을 내디딘 상태예요. 💪"
        ),
        "highlight": highlight_message,
        "focus_area": f"다음 주에 함께 집중해서 조정해 보면 좋을 영역: {max_category}",
        "recommendations": [
            {
                "action": f"{max_category} 활동 15% 감축 챌린지",
                "detail": (
                    f"가장 많은 탄소를 배출한 {max_category} 관련 행동 중, "
                    "일주일에 2~3회만 대체 행동(대중교통, 걷기, 채식 선택 등)으로 바꿔보세요. "
                    "한 번에 완벽히 바꾸기보다는 '조금 줄이는 경험'을 쌓는 게 중요해요."
                ),
                "impact": f"최대 약 {max_carbon_kg * 0.15:.2f}kg CO₂e 감축 가능",
            },
            {
                "action": "주요 소비 전 '30초 멈춤' 루틴",
                "detail": (
                    f"'{max_category}'처럼 큰 소비를 하기 전, "
                    "'이 선택이 내 탄소 발자국과 지갑에 어떤 영향을 줄까?'를 30초만 떠올려보세요. "
                    "이 짧은 멈춤만으로도 충동적인 소비와 불필요한 배출을 줄이는 효과가 큽니다."
                ),
                "impact": "충동 소비 감소 및 장기적인 탄소 배출 예방 효과",
            },
        ],
        "closing_message": (
            "사용자 님은 이미 '기록하고 돌아보는 사람'이라는 점에서 큰 출발선을 통과하셨어요. "
            "다음 주에는 위 제안들 중 하나만 실천해도 충분합니다. "
            "환경 코치인 제가 계속 옆에서 응원할게요! 😊"
        ),
    }


# ----------------------------------------------------------------------
# 실제 Gemini 호출 함수
# ----------------------------------------------------------------------
def call_llm_api(prompt: str, user_data: Dict[str, Any]) -> str:
    if not genai or not GEMINI_API_KEY:
        logger.warning("[llm_service] Gemini 설정 불가 → 시뮬레이션 응답 사용")
        simulated = _build_simulated_response(user_data)
        return json.dumps(simulated, ensure_ascii=False, indent=4)

    try:
        logger.info("[llm_service] 실제 Gemini 1.5 Flash 호출 중...")
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        raw_text = (response.text or "").strip()

        # ```json ... ``` 형태로 오면 코드블록 제거
        if raw_text.startswith("```"):
            lines = raw_text.splitlines()
            if len(lines) >= 2 and lines[0].startswith("```") and lines[-1].startswith("```"):
                lines = lines[1:-1]
            if lines and lines[0].strip().lower() == "json":
                lines = lines[1:]
            raw_text = "\n".join(lines).strip()

        parsed = json.loads(raw_text)  # LLM이 반환한 JSON 파싱
        return json.dumps(parsed, ensure_ascii=False, indent=4)

    except Exception as e:
        logger.error(f"[llm_service] Gemini 호출 / JSON 파싱 실패 → 시뮬레이션 응답 사용: {e}")
        simulated = _build_simulated_response(user_data)
        return json.dumps(simulated, ensure_ascii=False, indent=4)

def get_coaching_feedback(user_data: Dict[str, Any]) -> str:
    from backend.config.coaching_rules import COACHING_KNOWLEDGE_RULE

    prompt = create_coaching_prompt(user_data, COACHING_KNOWLEDGE_RULE)
    llm_response_json = call_llm_api(prompt, user_data)
    return llm_response_json
# ----------------------------------------------------------------------
# 프롬프트 생성
# ----------------------------------------------------------------------
def create_coaching_prompt(user_data: Dict[str, Any], knowledge_rule: Dict[str, Any]) -> str:
    # 1) 카테고리 데이터 가져오기: carbon / activity 둘 다 대응
    carbon_data = (
        user_data.get("category_carbon_data")
        or user_data.get("category_activity_data")
        or {}
    )

    # 2) 총 배출량 계산: 우선 total_carbon_kg, 없으면 carbon_data 합
    total_carbon_kg = user_data.get("total_carbon_kg")
    if total_carbon_kg is None:
        # 숫자로 들어왔다고 가정하고 합산 (없으면 0)
        try:
            total_carbon_kg = float(sum(carbon_data.values())) if carbon_data else 0.0
        except Exception:
            total_carbon_kg = 0.0

    # 3) 카테고리 요약 텍스트 생성
    if carbon_data:
        category_summary = "\n".join(
            [f"- {k}: {float(v):.2f} kg CO2e" for k, v in carbon_data.items()]
        )
    else:
        category_summary = "- 상세 카테고리 데이터 없음"

    data_summary = (
        "## [사용자 주간 활동 요약 데이터]\n"
        f"1. 주간 총 탄소 배출량: {total_carbon_kg:.2f} kg CO2e\n"
        "## [상세 카테고리별 탄소 배출량 내역]\n"
        "(아래 값은 이미 'kg CO2e' 단위로 환산된 값이며, 분석의 핵심 근거입니다.)\n"
        f"{category_summary}\n"
    )

    system_instruction = knowledge_rule["system_instruction"]
    coaching_principles = "\n".join(
        [f"- {p}" for p in knowledge_rule.get("coaching_principles", [])]
    )
    json_schema = json.dumps(knowledge_rule["json_schema"], ensure_ascii=False, indent=2)

    prompt = f"""
{system_instruction}

[데이터 분석 원칙]
아래 원칙을 최대한 충실히 따르십시오:
{coaching_principles}

[분석 대상 데이터]
아래는 사용자의 실제 주간 활동 데이터를 정리한 내용입니다.
이 데이터를 기반으로 사용자의 패턴을 분석하고, 실천 가능한 코칭을 제공하십시오.

{data_summary}

[출력 형식]
반드시 아래 JSON 스키마를 따르는 하나의 JSON 객체만을 출력해야 합니다.
설명 문장이나 코드블록 기호( ``` )는 사용하지 마십시오.
JSON 이외의 어떤 텍스트도 출력하지 마십시오.

JSON 스키마:
{json_schema}

[추가 지침]
- 한국어로만 답변합니다.
- 뻔한 조언이 아니라, 위 데이터에 맞는 구체적인 분석과 행동 제안을 제공합니다.
"""
    return prompt.strip()
