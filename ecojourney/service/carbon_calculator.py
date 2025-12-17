"""
탄소 배출량 계산 모듈
사용자 친화적 입력을 국제 표준 단위로 변환하여 탄소 배출량을 계산합니다.

API 우선 사용, 실패 시 로컬 배출 계수 사용 (Fallback)
"""

from typing import Tuple, Dict, List, Optional
import logging
from .carbon_api import calculate_carbon_with_api, calculate_food_by_name

logger = logging.getLogger(__name__)
# 배포 환경에서 리포트 작성 시 계산 과정 로그가 콘솔에 과도하게 출력되지 않도록 에러만 남깁니다.
logger.setLevel(logging.ERROR)

# 카테고리별 탄소 배출 계수 (kgCO₂e per unit)
EMISSION_FACTORS = {
    "교통": {
        "자동차": 0.171,  # kgCO₂e/km
        "버스": 0.089,    # kgCO₂e/km
        "지하철": 0.014,  # kgCO₂e/km
        "걷기": 0.0,      # kgCO₂e/km
        "자전거": 0.0,    # kgCO₂e/km
    },
    "의류": {
        # 새제품 배출량 (kgCO₂e/개)
        "티셔츠_새제품": 2.0,
        "청바지_새제품": 33.4,
        "신발_새제품": 13.6,
        # 빈티지 배출량 (새제품의 10%)
        "티셔츠_빈티지": 0.2,
        "청바지_빈티지": 3.34,
        "신발_빈티지": 1.36,
        # 가방/잡화는 상의와 동일한 계수 사용
        "가방/잡화_새제품": 2.0,
        "가방/잡화_빈티지": 0.2,
    },
    "식품": {
        # 육류 (kgCO₂e/kg)
        "소고기": 27.0,
        "돼지고기": 12.1,
    },
    "쓰레기": {
        "일반": 0.5,      # kgCO₂e/kg (매립)
        "플라스틱": 2.5,  # kgCO₂e/kg
        "종이": 0.3,      # kgCO₂e/kg
        "유리": 0.2,      # kgCO₂e/kg
        "캔": 1.5,        # kgCO₂e/kg
    },
    "전기": {
        "냉방기": 0.424,  # kgCO₂e/kWh (한국 전력 배출계수)
        "난방기": 0.424,  # kgCO₂e/kWh
    },
    "물": {
        "샤워": 0.0003,   # kgCO₂e/L
        "설거지": 0.0003, # kgCO₂e/L
        "세탁": 0.0003,   # kgCO₂e/L
    }
}

# 교통: 시간당 평균 속도 (km/h)
TRANSPORT_SPEED = {
    "자동차": 30.0,  # km/h (도심 평균)
    "버스": 25.0,    # km/h
    "지하철": 30.0,  # km/h
    "걷기": 5.0,     # km/h
    "자전거": 15.0,  # km/h
}

# 전기: 기기별 소비전력 (kW)
ELECTRIC_POWER = {
    "냉방기": 2.0,   # kW (에어컨 평균)
    "난방기": 1.5,   # kW (히터 평균)
}

# 물: 사용량 변환 (횟수 기반 평균값)
WATER_USAGE = {
    "샤워": 70.0,   # L/회 (평균 5-10분, 평균 7분 × 10L/분 = 70L/회)
    "설거지": 15.0, # L/회 (평균 10-20L/회)
    "세탁": 60.0,   # L/회 (평균 50-70L/회, 일반 세탁기 기준)
}

# 쓰레기: 개수당 무게 (kg)
WASTE_WEIGHT = {
    "캔": 0.015,    # kg/개 (약 15g)
    "병": 0.4,      # kg/개 (약 300-500g, 평균 400g)
}

# 식품: 1회 식사 기준량 (g)
FOOD_SERVING = {
    "소고기": 200.0,   # g
    "돼지고기": 150.0, # g
    "닭고기": 150.0,   # g
    "쌀밥": 200.0,     # 1공기 200g 기준
    "커피": 15.0,      # 1잔 원두 15g 기준
    "아메리카노": 15.0,  # 1잔 원두 15g 기준
    "카페라떼": 15.0,   # 1잔 원두 15g 기준
    "우유": 200.0,     # 1잔 200ml ≈ 200g
    "치즈": 30.0,      # 1회 30g 기준
}


def convert_to_standard_unit(
    category: str, 
    activity_type: str, 
    value: float, 
    unit: str,
    sub_category: str = None  # 의류: 새제품/빈티지
) -> Tuple[float, str]:
    """
    사용자 입력을 표준 단위로 변환
    
    Args:
        category: 카테고리
        activity_type: 활동 유형
        value: 사용자 입력 값
        unit: 사용자 입력 단위
        sub_category: 하위 카테고리 (의류: 새제품/빈티지)
    
    Returns:
        (변환된 값, 표준 단위) 튜플
    """
    if category == "교통":
        if unit == "분":
            # 시간을 거리로 변환
            hours = value / 60.0
            speed = TRANSPORT_SPEED.get(activity_type, 30.0)
            distance_km = hours * speed
            return distance_km, "km"
        elif unit == "km":
            return value, "km"
    
    elif category == "의류":
        # 의류는 개수 그대로 반환 (배출량은 개당으로 계산)
        if unit in ["개", "벌"]:
            return value, "개"
    
    elif category == "식품":
        # 파스타는 API 사용 (1회 단위로 입력받지만 API 호출 시 kg으로 변환)
        # 나머지는 "회" 단위로 고정 (한국일보 한끼 밥상 탄소 계산기 기준)
        pasta_items = {"카르보나라", "라자냐", "카넬로니", "라비올리", "파스타샐러드"}
        
        if activity_type in pasta_items:
            # 파스타는 "회" 단위로 입력받지만, API 호출을 위해 그대로 유지
            # (calculate_carbon_with_api에서 kg으로 변환)
            if unit == "회":
                return value, "회"
            else:
                return value, "회"
        else:
            # 나머지는 "회" 단위로 고정
            if unit == "회":
                return value, "회"
            else:
                # 다른 단위가 들어와도 "회"로 처리
                return value, "회"
    
    elif category == "쓰레기":
        if unit == "kg":
            return value, "kg"
        elif unit == "개":
            # 개수를 무게로 변환
            if activity_type == "캔":
                weight_per_item = WASTE_WEIGHT.get("캔", 0.015)
            elif activity_type == "유리":
                weight_per_item = WASTE_WEIGHT.get("병", 0.4)
            else:
                weight_per_item = 0.1  # 기본값
            return value * weight_per_item, "kg"
    
    elif category == "전기":
        if unit == "시간":
            # 시간을 kWh로 변환
            power_kw = ELECTRIC_POWER.get(activity_type, 1.0)
            kwh = value * power_kw
            return kwh, "kWh"
        elif unit == "kWh":
            return value, "kWh"
    
    elif category == "물":
        # 모든 물 사용 항목을 횟수 기반으로 계산
        if unit == "회":
            # 횟수 × 평균 사용량
            if activity_type == "샤워":
                liters = value * WATER_USAGE.get("샤워", 70.0)
            elif activity_type == "설거지":
                liters = value * WATER_USAGE.get("설거지", 15.0)
            elif activity_type == "세탁":
                liters = value * WATER_USAGE.get("세탁", 60.0)
            else:
                # 기본값: 세탁기 평균값 사용
                liters = value * WATER_USAGE.get("세탁", 60.0)
            return liters, "L"
        elif activity_type == "샤워" and unit == "분":
            # 기존 분 단위도 지원 (하위 호환성)
            liters = value * 10.0  # 분당 10L
            return liters, "L"
        elif unit == "L":
            return value, "L"
    
    # 기본값: 변환 불가능한 경우 원래 값 반환
    return value, unit


def calculate_carbon_emission(
    category: str, 
    activity_type: str, 
    value: float, 
    unit: str,
    sub_category: str = None,
    use_api: bool = True  # API 사용 여부 (기본값: True)
) -> dict:
    """
    탄소 배출량 계산
    API를 우선 사용하고, 실패 시 로컬 배출 계수 사용 (Fallback)
    
    Args:
        category: 카테고리
        activity_type: 활동 유형
        value: 사용자 입력 값
        unit: 사용자 입력 단위
        sub_category: 하위 카테고리 (의류: 새제품/빈티지)
        use_api: API 사용 여부 (기본값: True)
    
    Returns:
        계산 결과 딕셔너리
    """
    # 표준 단위로 변환
    converted_value, standard_unit = convert_to_standard_unit(
        category, activity_type, value, unit, sub_category
    )
    
    carbon_emission = None
    calculation_method = "local"  # "api" 또는 "local"
    api_provider = None  # "climatiq" 또는 None
    
    # API 사용 시도 (모든 카테고리 대상, 실패 시 로컬 Fallback)
    if use_api:
        try:
            carbon_emission = calculate_carbon_with_api(
                category=category,
                activity_type=activity_type,
                value=value,
                unit=unit,
                converted_value=converted_value,
                standard_unit=standard_unit,
                sub_category=sub_category
            )
            if carbon_emission is not None:
                calculation_method = "api"
                api_provider = "climatiq"
            else:
                pass
        except Exception as e:
            # API 실패는 로컬 계산으로 자연스럽게 폴백(콘솔 로그 출력 금지)
            pass
    else:
        pass
    
    # API 실패 또는 API 비활성화인 경우 로컬 배출 계수 사용
    if carbon_emission is None:
        emission_factor = 0.0
        
        if category == "식품":
            # 파스타는 API로 계산되므로 여기서는 처리하지 않음
            # 나머지는 한끼 기준 로컬 계산 (한국일보 한끼 밥상 탄소 계산기 출처)
            pasta_items = {"카르보나라", "라자냐", "카넬로니", "라비올리", "파스타샐러드"}
            
            if activity_type in pasta_items:
                # 파스타는 이미 API로 계산되었으므로 여기서는 처리하지 않음
                # (API 실패 시에만 여기로 옴)
                # Fallback: 파스타는 weight-based 계산이므로 servings를 weight_kg로 변환
                # API 호출 시와 동일하게 1회를 0.25kg (250g)로 변환
                weight_kg = converted_value * 0.25
                carbon_emission = calculate_food_by_name(activity_type, weight_kg=weight_kg)
            else:
                # 한끼 기준 로컬 계산
                if standard_unit == "회":
                    carbon_emission = calculate_food_by_name(activity_type, servings=converted_value)
                else:
                    # 혹시 다른 단위가 들어온 경우도 처리
                    carbon_emission = calculate_food_by_name(activity_type, servings=converted_value)
        elif category == "의류":
            # 의류는 새제품/빈티지에 따라 다른 계수
            # UI 라벨을 배출 계수 키로 매핑
            clothing_type_mapping = {
                "상의": "티셔츠",
                "하의": "청바지",
                "신발": "신발",
                "가방/잡화": "가방/잡화",
            }
            
            mapped_type = clothing_type_mapping.get(activity_type, "티셔츠")
            sub_category = sub_category or "새제품"  # 기본값: 새제품
            
            key = f"{mapped_type}_{sub_category}"
            emission_factor = EMISSION_FACTORS["의류"].get(key, 0.0)
            
            if emission_factor == 0.0:
                # Fallback: 새제품 계수 사용
                key = f"{mapped_type}_새제품"
                emission_factor = EMISSION_FACTORS["의류"].get(key, 0.0)
            # 의류는 개당 배출량이므로 개수 그대로 사용
            carbon_emission = value * emission_factor
        else:
            # 나머지는 변환된 값 × 배출 계수
            if category in EMISSION_FACTORS and activity_type in EMISSION_FACTORS[category]:
                emission_factor = EMISSION_FACTORS[category][activity_type]
            else:
                emission_factor = EMISSION_FACTORS.get(category, {}).get("기본", 0.0)
            
            carbon_emission = converted_value * emission_factor
        
        calculation_method = "local"
    
    result = {
        "carbon_emission_kg": round(carbon_emission, 3),
        "converted_value": round(converted_value, 2),
        "converted_unit": standard_unit,
        "original_value": value,
        "original_unit": unit,
        "calculation_method": calculation_method,  # "api" 또는 "local"
        "api_provider": api_provider  # "climatiq" 또는 None
    }
    
    return result


def get_category_activities(category: str) -> List[str]:
    """카테고리별 활동 유형 목록 반환"""
    if category == "교통":
        return ["자동차", "버스", "지하철", "걷기", "자전거"]
    elif category == "의류":
        # UI 라벨 기준: 상의/하의/신발/가방/잡화
        return ["상의", "하의", "신발", "가방/잡화"]
    elif category == "식품":
        # API 매핑에 맞춘 주요 식품 하위 카테고리
        return ["소고기", "돼지고기", "닭고기", "우유", "치즈", "쌀밥", "커피"]
    elif category == "쓰레기":
        return ["일반", "플라스틱", "종이", "유리", "캔"]
    elif category == "전기":
        return ["냉방기", "난방기"]
    elif category == "물":
        return ["샤워", "설거지", "세탁"]
    return []


def get_category_units(category: str, activity_type: str = None) -> List[str]:
    """카테고리별 입력 가능한 단위 목록 반환"""
    if category == "교통":
        return ["분", "km"]
    elif category == "의류":
        return ["개"]
    elif category == "식품":
        return ["g", "1회 식사"]
    elif category == "쓰레기":
        if activity_type in ["캔", "유리"]:
            return ["개", "kg"]
        return ["kg", "개"]
    elif category == "전기":
        return ["시간"]
    elif category == "물":
        # 모든 물 사용 항목을 횟수 기반으로 통일
        if activity_type == "샤워":
            return ["회", "분"]  # 회 단위 우선, 분 단위도 지원
        elif activity_type == "설거지":
            return ["회"]
        elif activity_type == "세탁":
            return ["회"]
        return ["회", "L"]  # 기본값도 회 단위
    return []


def get_sub_categories(category: str) -> List[str]:
    """카테고리별 하위 카테고리 목록 반환"""
    if category == "의류":
        return ["새제품", "빈티지"]
    elif category == "식품":
        return ["육류"]
    return []