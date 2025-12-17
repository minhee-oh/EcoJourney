import json
import os
from typing import Dict, Any

from dotenv import load_dotenv

# -------------------------------
# 1) .env 파일에서 API 키 로드
# -------------------------------
load_dotenv(override=True) # 프로젝트 루트(OpenSourceProject/.env)에서 로드

# Gemini API 설정
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # .env에서 키 읽기
PRIMARY_MODEL = "gemini-2.5-flash"  # 기본 모델
FALLBACK_MODELS = [
    "gemini-1.5-flash",    # 1차 대체 모델 (실제 사용 가능)
    "gemini-1.5-flash-latest",  # 2차 대체 모델
]

# -------------------------------
# 2) Gemini SDK 로딩
# -------------------------------
try:
    import google.generativeai as genai
except ImportError:
    genai = None

# -------------------------------
# 3) Gemini 초기화
# -------------------------------
if genai and GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
    except Exception as e:
        # 초기화 실패 시에는 폴백을 사용하도록 비활성화
        genai = None
else:
    genai = None


# ======================================================================
# 1) Gemini 실패 시 사용할 폴백(기본 응답)
# ======================================================================
def _build_simulated_response(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Gemini 호출 실패 시 기본 템플릿 기반 JSON 응답 생성"""
    carbon_data = user_data.get("category_carbon_data", {}) or {}
    total_carbon_kg = user_data.get("total_carbon_kg", 0.0)

    has_data = bool(carbon_data) and any(v > 0 for v in carbon_data.values())

    # 데이터가 있을 때
    if has_data:
        max_category = max(carbon_data, key=carbon_data.get)
        max_value = float(carbon_data[max_category])
        total = float(sum(carbon_data.values())) or 1.0
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
                    "바쁜 시간대에 쓰는 이동/소비 패턴을 떠올리고 "
                    "대체 행동 1가지만 미리 정해두세요."
                ),
                "impact": "반복될수록 감축 효과가 누적됩니다.",
                "reason": "오늘 데이터가 반복 패턴의 힌트를 제공하기 때문입니다.",
            },
            {
                "action": "탄소가 많이 오른 '위험 시간대' 인지하기",
                "detail": (
                    "탄소 사용이 증가한 시간대를 떠올리고, "
                    "해당 시간대에 선택을 한 번 더 점검해보세요."
                ),
                "impact": "충동 소비·이동 감소 효과",
                "reason": "시간대 기반 패턴 파악이 행동 조절에 효과적이기 때문입니다.",
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
# 2) Gemini 모델 호출 헬퍼 함수
# ======================================================================
def _call_gemini_model(model_name: str, prompt: str) -> str:
    """특정 Gemini 모델로 API 호출"""
    model = genai.GenerativeModel(model_name)
    response = model.generate_content(prompt)
    
    # 응답 텍스트 안전 추출 (candidates/parts 우선)
    raw_text = ""
    try:
        if hasattr(response, "candidates") and response.candidates:
            for cand in response.candidates:
                parts = getattr(cand, "content", None) or getattr(cand, "parts", None)
                if parts and hasattr(parts, "__iter__"):
                    texts = [
                        getattr(p, "text", None) or str(getattr(p, "data", "")) or ""
                        for p in parts
                        if p is not None
                    ]
                    joined = "\n".join([t for t in texts if t]).strip()
                    if joined:
                        raw_text = joined
                        break
        if not raw_text:
            raw_text = (getattr(response, "text", None) or "").strip()
    except Exception:
        raw_text = (getattr(response, "text", None) or "").strip()

    if not raw_text:
        raise ValueError("LLM 응답에 텍스트가 없습니다.")
    
    return raw_text

# ======================================================================
# 3) Gemini 호출 + JSON 파싱 + 다른 모델 폴백
# ======================================================================
def call_llm_api(prompt: str, user_data: Dict[str, Any]) -> str:
    """Gemini 기본 모델 호출 → 실패 시 다른 Gemini 모델들 시도 → 실패 시 폴백 JSON 반환"""
    if not genai or not GEMINI_API_KEY:
        simulated = _build_simulated_response(user_data)
        return json.dumps(simulated, ensure_ascii=False, indent=4)

    # 시도할 모델 목록 (기본 모델 + 대체 모델들)
    models_to_try = [PRIMARY_MODEL] + FALLBACK_MODELS
    
    for model_name in models_to_try:
        try:
            raw_text = _call_gemini_model(model_name, prompt)
            
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
            error_str = str(e)
            # 429 에러(할당량 초과) 또는 quota 관련 에러인 경우 다음 모델로 전환
            if "429" in error_str or "quota" in error_str.lower() or "Quota exceeded" in error_str:
                pass
            # 모델을 찾을 수 없는 경우 (404 에러 포함)
            elif "not found" in error_str.lower() or "invalid" in error_str.lower() or "does not exist" in error_str.lower() or "not available" in error_str.lower() or "404" in error_str:
                pass
            # API 키 관련 에러
            elif "api key" in error_str.lower() or "authentication" in error_str.lower() or "unauthorized" in error_str.lower() or "403" in error_str:
                # API 키 문제는 모든 모델에서 동일하므로 즉시 폴백
                break
            else:
                pass
            
            # 마지막 모델이 아니면 계속 시도
            if model_name != models_to_try[-1]:
                continue
    
    # 모든 Gemini 모델 실패 시 폴백
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

    policy_candidates = user_data.get("policy_candidates") or []
    policy_text = ""
    if isinstance(policy_candidates, list) and policy_candidates:
        lines = []
        for p in policy_candidates:
            if not isinstance(p, dict):
                continue
            name = p.get("name")
            reason = p.get("reason")
            url = p.get("url")
            if name or reason or url:
                line = f"- 이름: {name or ''} | 설명: {reason or ''} | 링크: {url or ''}"
                lines.append(line)
        if lines:
            policy_text = "\n".join(lines)

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

[정책/혜택 후보 목록]
아래 목록 안에서만 정책/혜택을 선택해 policy_recommendations를 작성하세요.
목록에 없는 정책 이름을 새로 만들지 마세요.
{policy_text or '- 제공된 정책 후보 없음'}

[추가 조건]
- 한국어로 작성.
- 오늘 하루 데이터만 기준.
- 행동 추천 3~5개 포함.
- 정책/혜택 추천은 1~2개(없으면 빈 배열).
"""

    return prompt.strip()
