"""
평균 탄소 배출량 데이터
한국인 평균 일일 탄소 배출량 (kgCO₂e)

출처: 지표누리 온실가스 총배출량과 GDP 대비 1인당 배출량 (2012-2022년 데이터 평균값)
"""

# 전체 평균 일일 탄소 배출량
# 출처: 지표누리 온실가스 총배출량과 GDP 대비 1인당 배출량 (2012-2022년 데이터 평균값)
TOTAL_AVERAGE_DAILY = 14.5  # kgCO₂e/일

# 카테고리별 한국인 평균 일일 탄소 배출량 (kgCO₂e)
# 참고: 아래 값들은 참고용 추정값이며, 총 평균(14.5 kgCO₂e/일)과의 비율로 계산됨
AVERAGE_DAILY_EMISSION = {
    "교통": 3.5,      # 통근/통학 및 이동
    "식품": 2.8,      # 식사
    "전기": 2.2,      # 가정용 전기 사용
    "물": 0.3,        # 상수도 사용
    "의류": 0.5,      # 의류 구매 (일일 평균)
    "쓰레기": 0.7     # 폐기물 처리
}

def get_average_emission(category: str) -> float:
    """카테고리별 평균 배출량 반환"""
    return AVERAGE_DAILY_EMISSION.get(category, 0.0)

def get_total_average() -> float:
    """전체 평균 일일 배출량 반환"""
    return TOTAL_AVERAGE_DAILY

def compare_with_average(user_emission: float, category: str = None) -> dict:
    """
    사용자 배출량과 평균 비교
    
    Args:
        user_emission: 사용자 배출량
        category: 카테고리 (None이면 전체 비교)
    
    Returns:
        비교 결과 딕셔너리
    """
    if category:
        average = get_average_emission(category)
    else:
        average = get_total_average()
    
    difference = user_emission - average
    percentage = (difference / average * 100) if average > 0 else 0
    
    return {
        "user_emission": user_emission,
        "average_emission": average,
        "difference": difference,
        "percentage": percentage,
        "is_better": difference < 0,  # 음수면 더 좋음 (배출량이 적음)
        "category": category
    }








