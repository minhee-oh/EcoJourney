"""
Google Gemini AI를 활용한 맞춤형 탄소 저감 코칭 모듈
"""

import os
from typing import List, Dict
import google.generativeai as genai
from dotenv import load_dotenv
from .models import AICoachRequest, AICoachResponse, CarbonResult

load_dotenv()

# Gemini API 키 설정
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# 사용 가능한 모델 캐싱 (한 번만 확인)
_available_model = None

def get_available_gemini_model():
    """사용 가능한 Gemini 모델 반환 (무료 티어 전용)"""
    global _available_model
    if _available_model:
        return _available_model
    
    # 무료 티어에서 사용 가능한 모델 (우선순위 순)
    free_tier_models = [
        'gemini-2.5-flash',  # 무료 티어 최신 모델
        'gemini-pro',  # 무료 티어 기본 모델 (대안)
    ]
    
    # 모델을 순서대로 시도
    for model_name in free_tier_models:
        try:
            # 모델이 존재하는지 확인
            model = genai.GenerativeModel(model_name)
            _available_model = model_name
            return model_name
        except Exception as e:
            # 404 오류면 다음 모델 시도, 다른 오류면 로그
            if '404' not in str(e):
                print(f"모델 {model_name} 시도 중 오류: {str(e)}")
            continue
    
    # 모든 시도 실패 시 기본값
    _available_model = 'gemini-2.5-flash'
    return _available_model


def generate_coaching_message(request: AICoachRequest) -> AICoachResponse:
    """
    사용자의 탄소 배출 데이터를 분석하여 맞춤형 코칭 메시지 생성
    
    Args:
        request: AI 코칭 요청 데이터
    
    Returns:
        AI 코칭 응답
    """
    if not GEMINI_API_KEY:
        # API 키가 없는 경우 기본 메시지 반환
        return AICoachResponse(
            analysis="AI 코칭 기능을 사용하려면 GEMINI_API_KEY를 설정해주세요.",
            suggestions=[
                "대중교통을 이용하세요",
                "채식 위주의 식단을 선택하세요",
                "물과 전기를 절약하세요"
            ],
            alternative_actions=[],
            emotional_message="작은 실천이 큰 변화를 만듭니다! 🌱"
        )
    
    try:
        # 활동 데이터를 텍스트로 변환
        activities_list = []
        for act in request.activities[-10:]:  # 최근 10개 활동만
            if isinstance(act, dict):
                # 평면 구조인 경우
                category = act.get("category", "알 수 없음")
                activity_type = act.get("activity_type", "알 수 없음")
                carbon = act.get("carbon_emission_kg", 0)
            else:
                # CarbonResult 객체인 경우
                category = act.activity.category if hasattr(act, 'activity') else "알 수 없음"
                activity_type = act.activity.activity_type if hasattr(act, 'activity') else "알 수 없음"
                carbon = act.carbon_emission_kg if hasattr(act, 'carbon_emission_kg') else 0
            activities_list.append(f"- {category} > {activity_type}: {carbon}kgCO₂e")
        
        activities_text = "\n".join(activities_list)
        
        # category_breakdown이 딕셔너리인지 확인
        if isinstance(request.category_breakdown, dict):
            category_text = "\n".join([
                f"- {cat}: {amount:.2f}kgCO₂e"
                for cat, amount in request.category_breakdown.items()
            ])
        else:
            category_text = str(request.category_breakdown)
        
        # 프롬프트 구성
        prompt = f"""당신은 친근하고 따뜻한 환경 코치입니다. 사용자의 탄소 배출 데이터를 분석하고, 
감성적이고 구체적인 행동 가이드를 제공해주세요.

[사용자 데이터]
오늘 총 탄소 배출량: {request.total_carbon:.2f}kgCO₂e

카테고리별 배출량:
{category_text}

최근 활동 내역:
{activities_text}

[요청사항]
1. 사용자의 탄소 배출 패턴을 간단히 분석해주세요 (2-3문장)
2. 구체적이고 실천 가능한 탄소 저감 제안 3가지를 제시해주세요
3. 각 제안에 대해 "소나무 X그루를 심는 효과" 같은 감성적 비유를 포함해주세요
4. 마지막으로 격려하는 메시지를 작성해주세요

응답 형식:
- 분석: [분석 내용]
- 제안1: [구체적 제안 + 비유]
- 제안2: [구체적 제안 + 비유]
- 제안3: [구체적 제안 + 비유]
- 격려 메시지: [감성적 메시지]
"""
        
        # Gemini 모델 호출 (무료 티어 모델 사용)
        import time
        import re
        
        # 무료 티어 모델 사용 (gemini-pro가 가장 안정적)
        model_name = get_available_gemini_model()
        model = genai.GenerativeModel(model_name)
        
        # 재시도 로직 (할당량 초과 시)
        max_retries = 3
        retry_delay = 1
        
        response = None
        for attempt in range(max_retries):
            try:
                response = model.generate_content(prompt)
                break  # 성공하면 루프 종료
            except Exception as e:
                error_str = str(e)
                # 할당량 초과 오류 (429)인 경우
                if '429' in error_str or 'quota' in error_str.lower() or 'rate limit' in error_str.lower():
                    if attempt < max_retries - 1:
                        # 재시도 대기 시간 계산
                        delay_match = re.search(r'retry in (\d+\.?\d*)s', error_str.lower())
                        if delay_match:
                            retry_delay = float(delay_match.group(1)) + 1
                        else:
                            retry_delay = min(retry_delay * 2, 60)
                        time.sleep(retry_delay)
                        continue
                    else:
                        # 최대 재시도 횟수 초과
                        raise Exception(f"Gemini API 할당량을 초과했습니다. 잠시 후 다시 시도해주세요. (모델: {model_name})")
                # 404 오류 (모델을 찾을 수 없음)
                elif '404' in error_str or 'not found' in error_str.lower():
                    raise Exception(f"Gemini 모델 '{model_name}'을 찾을 수 없습니다. API 키와 모델 이름을 확인해주세요.")
                else:
                    # 다른 오류는 즉시 전파
                    raise
        
        if response is None:
            raise Exception(f"Gemini 모델 호출 실패 (모델: {model_name})")
        
        # 응답 파싱
        response_text = response.text
        
        # 간단한 파싱 (실제로는 더 정교한 파싱 필요)
        lines = response_text.split('\n')
        analysis = ""
        suggestions = []
        emotional_message = ""
        
        current_section = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if '분석' in line or 'Analysis' in line:
                current_section = 'analysis'
                analysis = line.split(':', 1)[-1].strip() if ':' in line else line
            elif '제안' in line or '제안1' in line or '제안2' in line or '제안3' in line:
                current_section = 'suggestion'
                suggestion = line.split(':', 1)[-1].strip() if ':' in line else line
                if suggestion:
                    suggestions.append(suggestion)
            elif '격려' in line or '메시지' in line:
                current_section = 'message'
                emotional_message = line.split(':', 1)[-1].strip() if ':' in line else line
            else:
                if current_section == 'analysis' and not analysis:
                    analysis = line
                elif current_section == 'suggestion':
                    suggestions.append(line)
                elif current_section == 'message' and not emotional_message:
                    emotional_message = line
        
        # 기본값 설정
        if not analysis:
            analysis = f"오늘 총 {request.total_carbon:.2f}kgCO₂e의 탄소를 배출하셨습니다."
        if not suggestions:
            suggestions = [
                "대중교통을 이용하면 탄소 배출을 크게 줄일 수 있어요",
                "채소 위주의 식단을 선택해보세요",
                "물과 전기를 아껴 사용하세요"
            ]
        if not emotional_message:
            emotional_message = "작은 실천이 큰 변화를 만듭니다! 🌱"
        
        # 대안 행동 생성 (실제 사용한 활동만 확인)
        alternative_actions = []
        
        # 실제 활동 내역에서 사용한 활동 확인
        for act in request.activities:
            if isinstance(act, dict):
                category = act.get("category", "")
                activity_type = act.get("activity_type", "")
            else:
                category = act.activity.category if hasattr(act, 'activity') else ""
                activity_type = act.activity.activity_type if hasattr(act, 'activity') else ""
            
            # 디버깅: 활동 내역 출력
            print(f"[AI Coach Debug] Activity: category={category}, activity_type={activity_type}")
            
            # 교통 카테고리에서 자동차 사용 확인
            if category == "교통" and activity_type == "자동차":
                print(f"[AI Coach Debug] 자동차 대안 추가")
                alternative_actions.append({
                    "current": "자동차 이용",
                    "alternative": "대중교통 이용",
                    "impact": "탄소 배출량 50% 감소"
                })
                break  # 중복 방지
        
        # 육류를 실제로 섭취한 경우에만 대안 제시
        for act in request.activities:
            if isinstance(act, dict):
                category = act.get("category", "")
                activity_type = act.get("activity_type", "")
            else:
                category = act.activity.category if hasattr(act, 'activity') else ""
                activity_type = act.activity.activity_type if hasattr(act, 'activity') else ""
            
            # 식품 카테고리에서 육류 관련 활동 확인 (소고기, 돼지고기 등)
            if category == "식품" and activity_type in ["소고기", "돼지고기", "닭고기"]:
                print(f"[AI Coach Debug] 육류 대안 추가: {activity_type}")
                alternative_actions.append({
                    "current": f"{activity_type} 섭취",
                    "alternative": "채식 위주 식단",
                    "impact": "탄소 배출량 70% 감소"
                })
                break  # 중복 방지
        
        print(f"[AI Coach Debug] 최종 대안 행동 개수: {len(alternative_actions)}")
        
        return AICoachResponse(
            analysis=analysis,
            suggestions=suggestions[:3],  # 최대 3개
            alternative_actions=alternative_actions,
            emotional_message=emotional_message
        )
    
    except Exception as e:
        # 에러 발생 시 상세한 오류 정보와 함께 기본 메시지 반환
        error_msg = str(e)
        # 할당량 초과 오류인 경우 특별 처리
        if '429' in error_msg or 'quota' in error_msg.lower():
            analysis_msg = "AI 분석 서비스의 일일 사용 한도를 초과했습니다. 잠시 후 다시 시도해주세요."
        elif '404' in error_msg or 'not found' in error_msg.lower():
            analysis_msg = f"AI 모델을 찾을 수 없습니다. (오류: {error_msg[:100]})"
        else:
            analysis_msg = f"데이터 분석 중 오류가 발생했습니다: {error_msg[:200]}"
        
        # 디버깅을 위해 콘솔에 출력
        print(f"[AI Coach Error] {error_msg}")
        
        return AICoachResponse(
            analysis=analysis_msg,
            suggestions=[
                "대중교통을 이용하세요",
                "채식 위주의 식단을 선택하세요",
                "물과 전기를 절약하세요"
            ],
            alternative_actions=[],
            emotional_message="작은 실천이 큰 변화를 만듭니다! 🌱"
        )

