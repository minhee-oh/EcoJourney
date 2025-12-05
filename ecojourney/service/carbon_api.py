"""
탄소 배출량 계산 API 통합 모듈
Climatiq API (일상 생활 행동) 및 CarbonCloud API (식품) 사용
"""

import os
import requests
from typing import Optional, Dict, Any
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# API 키 (환경 변수에서 로드)
CLIMATIQ_API_KEY = os.getenv("CLIMATIQ_API_KEY", "")
CARBONCLOUD_API_KEY = os.getenv("CARBONCLOUD_API_KEY", "")

# API 엔드포인트
BASE_URL = "https://beta4.api.climatiq.io/estimate"


def get_headers():
    """Climatiq API 요청 헤더"""
    return {
        "Authorization": f"Bearer {CLIMATIQ_API_KEY}",
        "Content-Type": "application/json"
    }


def _call_climatiq(activity_id: str, region: str, parameters: Dict[str, Any], data_version: str = "^1", source: str = None) -> Optional[float]:
    """
    API 호출 공통 함수 (Fallback 로직 강화)
    1. 요청한 Region(예: KR)으로 시도
    2. 실패 시 Global로 재시도
    3. 그래도 실패하면 None 반환 (로컬 계산으로 넘어감)
    
    Args:
        activity_id: 활동 ID
        region: 지역 코드 (KR, Global 등)
        parameters: 계산 파라미터 (distance, energy, weight 등)
        data_version: 데이터 버전 (기본값: "^1")
    
    Returns:
        탄소 배출량 (kgCO2e) 또는 None (실패 시)
    """
    if not CLIMATIQ_API_KEY:
        logger.warning(f"[API] CLIMATIQ_API_KEY가 설정되지 않았습니다.")
        return None
    
    emission_factor = {
        "activity_id": activity_id,
        "data_version": data_version,
        "region": region
    }
    
    # source 파라미터가 있으면 추가 (식품 API 등)
    if source:
        emission_factor["source"] = source
    
    payload = {
        "emission_factor": emission_factor,
        "parameters": parameters
    }
    
    try:
        # 1차 시도: 요청된 Region (예: KR)
        response = requests.post(BASE_URL, json=payload, headers=get_headers(), timeout=10)
        logger.debug(f"[API] {region} 지역 시도 - 상태 코드: {response.status_code}")
        
        # 400(Bad Request) 중 'no_emission_factors_found' 에러이거나 404인 경우
        if response.status_code in [400, 404]:
            try:
                error_data = response.json()
                error_code = error_data.get("error_code", "")
                if error_code == "no_emission_factors_found" or response.status_code == 404:
                    logger.warning(f"[API 경고] {region} 지역 데이터 없음. Global로 재시도합니다. (ID: {activity_id})")
                    
                    # 2차 시도: Region을 'Global'로 변경
                    payload["emission_factor"]["region"] = "Global"
                    response = requests.post(BASE_URL, json=payload, headers=get_headers(), timeout=10)
                    logger.debug(f"[API] Global 재시도 - 상태 코드: {response.status_code}")
            except:
                pass
        
        # 2차 시도도 실패하면 에러 발생시킴
        response.raise_for_status()
        
        data = response.json()
        co2e_value = data.get("co2e", 0.0)
        co2e_unit = data.get("co2e_unit", "kg")
        
        # 톤 단위인 경우 kg으로 변환
        if co2e_unit == "t" or co2e_unit == "ton":
            co2e = co2e_value * 1000
        else:
            co2e = co2e_value
        
        logger.info(f"[API] ✅ 계산 성공: {co2e}kgCO2e (지역: {payload['emission_factor']['region']})")
        return co2e
        
    except requests.exceptions.RequestException as e:
        logger.error(f"[API 오류] {activity_id} 호출 실패: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                logger.error(f"[API] 상세 응답: {error_data}")
            except:
                logger.error(f"[API] 상세 응답 (텍스트): {e.response.text}")
        return None  # 로컬 계산으로 넘어가게 None 반환
    except Exception as e:
        logger.error(f"[API] ❌ 예상치 못한 오류: {e}")
        return None


# ---------------------------------------------------------
# 1. 🚗 교통 (Transport) 계산
# ---------------------------------------------------------

def calculate_transport_emission(
    distance_km: float, 
    vehicle_type: str = "passenger_vehicle-vehicle_type_automobile-fuel_source_na-distance_na-engine_size_na"
) -> float:
    """
    자동차 이동 거리에 따른 탄소 배출량 계산
    
    Args:
        distance_km: 이동 거리 (km)
        vehicle_type: 차량 유형 (기본값: 범용 휘발유 승용차)
    
    Returns:
        탄소 배출량 (kgCO2e)
    """
    logger.info(f"[교통 API] 계산 시작 - 거리: {distance_km}km, 차량 유형: {vehicle_type}")
    
    # 교통은 기본적으로 Global 데이터 사용 (KR 데이터가 제한적)
    result = _call_climatiq(
        activity_id=vehicle_type,
        region="Global",
        parameters={"distance": distance_km, "distance_unit": "km"}
    )
    
    if result is None:
        # Fallback: 로컬 배출 계수 사용
        fallback_result = distance_km * 0.192  # 자동차 기본값
        logger.info(f"[교통 API] Fallback 계산 결과: {fallback_result}kgCO2e")
        return fallback_result
    
    return result


# 교통 수단별 vehicle_type 매핑 (check_ids.py 검색 결과 기반)
TRANSPORT_VEHICLE_TYPES = {
    # 자동차: Automobile (GLOBAL, Road Travel)
    "자동차": "passenger_vehicle-vehicle_type_automobile-fuel_source_na-distance_na-engine_size_na",
    # 버스: Interurban and rural bus passenger transportation services
    "버스": "transport_services-type_interurban_and_rural_bus_passenger_transportation_services",
    # 지하철: Subway (GLOBAL, Rail Travel)
    "지하철": "passenger_train-route_subway-fuel_source_na",
    "걷기": None,  # 탄소 배출 없음
    "자전거": None,  # 탄소 배출 없음
}


def calculate_transport_by_type(distance_km: float, activity_type: str) -> float:
    """
    교통 수단 유형에 따른 탄소 배출량 계산
    
    Args:
        distance_km: 이동 거리 (km)
        activity_type: 교통 수단 ("자동차", "버스", "지하철", "걷기", "자전거")
    
    Returns:
        탄소 배출량 (kgCO2e)
    """
    logger.info(f"[교통] 계산 시작 - 수단: {activity_type}, 거리: {distance_km}km")
    
    if activity_type in ["걷기", "자전거"]:
        logger.info(f"[교통] {activity_type}는 탄소 배출 없음 (0.0kgCO2e)")
        return 0.0

    # 현재 Climatiq Free Tier에서 버스용 distance 기반 EF를 안정적으로 찾기 어려워
    # 버스는 로컬 배출 계수만 사용하도록 처리 (API 미호출)
    if activity_type == "버스":
        logger.info("[교통] 버스는 로컬 배출 계수만 사용 (Climatiq distance 기반 EF 미제공)")
        return None
    
    vehicle_type = TRANSPORT_VEHICLE_TYPES.get(activity_type)
    if vehicle_type:
        logger.info(f"[교통] {activity_type}에 대한 vehicle_type: {vehicle_type}")
        result = calculate_transport_emission(distance_km, vehicle_type)
        logger.info(f"[교통] 최종 결과: {result}kgCO2e")
        return result
    else:
        # 기본값: 자동차
        logger.warning(f"[교통] 알 수 없는 교통 수단: {activity_type}, 기본값(자동차) 사용")
        result = calculate_transport_emission(distance_km)
        logger.info(f"[교통] 최종 결과: {result}kgCO2e")
        return result


# ---------------------------------------------------------
# 2. ⚡ 에너지 (Electricity/AC) 계산
# ---------------------------------------------------------

def calculate_energy_emission(kwh: float, region: str = "KR") -> float:
    """
    전력 사용량(kWh)에 따른 탄소 배출량 계산
    한국(KR) 전력 믹스 기준 (실패 시 Global로 자동 재시도)
    
    Args:
        kwh: 전력 사용량 (kWh)
        region: 지역 코드 (기본값: "KR" - 한국)
    
    Returns:
        탄소 배출량 (kgCO2e)
    """
    logger.info(f"[전기 API] 계산 시작 - 사용량: {kwh}kWh, 지역: {region}")
    
    # 기본 전력 믹스 ID (search 결과 기반)
    # Electricity supplied from grid - residual mix - supplier CMS Energy Consumers Energy (US-MI)
    activity_id = "electricity-supply_grid-source_residual_mix-supplier_cms_energy_consumers_energy"
    
    # US-MI 데이터 우선 사용 (한국 평균 계수는 Fallback에서 보정)
    result = _call_climatiq(
        activity_id=activity_id,
        region="US-MI",
        parameters={"energy": kwh, "energy_unit": "kWh"}
    )
    
    if result is None:
        # Fallback: 로컬 배출 계수 사용
        fallback_result = kwh * 0.478  # 한국 평균 (0.478 kg/kWh)
        logger.info(f"[전기 API] Fallback 계산 결과: {fallback_result}kgCO2e")
        return fallback_result
    
    return result


# ---------------------------------------------------------
# 3. 🥩 음식/식재료 (Food) 계산
# ---------------------------------------------------------

def calculate_food_emission(food_type: str, weight_kg: float) -> float:
    """
    음식 종류와 무게에 따른 배출량 계산
    Climatiq의 IPCC 데이터를 활용
    
    Args:
        food_type: 음식 종류 ("beef", "pork", "chicken", "coffee", "rice" 등)
        weight_kg: 무게 (kg)
    
    Returns:
        탄소 배출량 (kgCO2e)
    """
    logger.info(f"[식품 API] 계산 시작 - 종류: {food_type}, 무게: {weight_kg}kg")
    
    if not CLIMATIQ_API_KEY:
        logger.warning("[식품 API] CLIMATIQ_API_KEY가 설정되지 않았습니다. Fallback 사용")
        # 음식 종류별 기본 배출 계수 (kgCO2e/kg)
        defaults = {
            "beef": 27.0, 
            "pork": 7.0, 
            "chicken": 6.9, 
            "coffee": 17.0, 
            "rice": 4.0,
            "rice_bowl": 4.0,
        }
        fallback_result = weight_kg * defaults.get(food_type, 4.0)  # 기본값: 쌀 기준 (채소/유제품 등)
        logger.info(f"[식품 API] Fallback 계산 결과: {fallback_result}kgCO2e (food_type: {food_type})")
        return fallback_result
    
    # 음식 종류별 Climatiq ID 매핑 (check_ids.py 검색 결과 기반)
    food_map = {
        # 소고기: Meat products (beef) - KR region 포함
        "beef": "consumer_goods-type_meat_products_beef",
        # 돼지고기: Pork (Food Production)
        "pork": "food-type_pork",
        # 닭고기: Meat products (poultry) - 대략적인 값
        "chicken": "consumer_goods-type_meat_products_poultry",
        # 커피: Coffee, green bean (1잔 기준: 원두 15g)
        "coffee": "consumer_goods-type_beverages_coffee_green_bean",
        # 쌀: Cereals, rice (일반 쌀)
        "rice": "consumer_goods-type_cereals_rice",
        # 쌀밥: Processed rice (1공기 200g 기준)
        "rice_bowl": "consumer_goods-type_processed_rice",
    }
    
    activity_id = food_map.get(food_type, "consumer_goods-type_meat_products_beef")  # 기본값
    logger.info(f"[식품 API] 매핑된 activity_id: {activity_id}")
    
    # 음식은 지역 특성을 덜 타므로 Global 우선 사용 권장 (데이터가 더 많음)
    # KR 시도 -> 실패시 _call_climatiq 내부에서 Global로 재시도함
    result = _call_climatiq(
        activity_id=activity_id,
        region="Global",  # Global 우선 사용
        parameters={"weight": weight_kg, "weight_unit": "kg"},
        source="exiobase"  # 전세계 산업 연관 분석 데이터
    )
    
    if result is None:
        # Fallback: 로컬 배출 계수 사용
        defaults = {
            "beef": 27.0, 
            "pork": 7.0, 
            "chicken": 6.9, 
            "coffee": 17.0, 
            "rice": 4.0,
            "rice_bowl": 4.0,
        }
        fallback_result = weight_kg * defaults.get(food_type, 4.0)  # 기본값: 쌀 기준 (채소/유제품 등)
        logger.info(f"[식품 API] Fallback 계산 결과: {fallback_result}kgCO2e (food_type: {food_type})")
        return fallback_result
    
    return result


    # 한국어 음식 이름 → Climatiq food_type 매핑
FOOD_TYPE_MAP = {
    "소고기": "beef",
    "돼지고기": "pork",
    "닭고기": "chicken",
    "고기류": "beef",  # 기본값
    "채소류": "rice",  # 채소는 쌀로 대체 (낮은 배출 계수)
    "양파": "rice",  # 채소는 쌀 배출 계수 사용
    "파": "rice",
    "마늘": "rice",
    # 쌀밥과 커피
    "쌀밥": "rice_bowl",
    "커피": "coffee",
    "아메리카노": "coffee",  # 커피 하위 카테고리
    "카페라떼": "coffee",  # 커피 하위 카테고리
    # 유제품 (쌀 배출 계수 사용 - 낮은 배출량)
    "우유": "rice",
    "치즈": "rice",
}


def calculate_food_by_name(food_name: str, weight_kg: float) -> float:
    """
    한국어 음식 이름으로 탄소 배출량 계산
    
    Args:
        food_name: 음식 이름 ("소고기", "돼지고기" 등)
        weight_kg: 무게 (kg)
    
    Returns:
        탄소 배출량 (kgCO2e)
    """
    logger.info(f"[식품] 한국어 이름 변환 - 입력: {food_name}, 무게: {weight_kg}kg")
    food_type = FOOD_TYPE_MAP.get(food_name, "rice")  # 기본값: 쌀 (채소/유제품 등 낮은 배출량)
    logger.info(f"[식품] 매핑된 food_type: {food_type}")
    result = calculate_food_emission(food_type, weight_kg)
    logger.info(f"[식품] 최종 결과: {result}kgCO2e")
    return result


# ---------------------------------------------------------
# 4. 의류 / 쇼핑 (Clothing & Shopping) 계산
# ---------------------------------------------------------


def calculate_clothing_emission(item_type: str, count: int) -> float:
    """
    의류/패션 아이템 개수에 따른 탄소 배출량 계산.
    무게 추정을 통해 소재 기반 ID에 매핑합니다.

    Args:
        item_type: 아이템 종류 ("티셔츠", "청바지", "신발", "가방" 등)
        count: 개수

    Returns:
        탄소 배출량 (kgCO2e)
    """
    logger.info(f"[의류 API] 계산 시작 - 종류: {item_type}, 개수: {count}")

    if not CLIMATIQ_API_KEY:
        logger.warning("[의류 API] CLIMATIQ_API_KEY가 설정되지 않았습니다. Fallback 사용")
        return 0.0

    # 아이템별 평균 무게(kg) 추정 (UI 라벨 기준)
    avg_weight_kg = {
        "상의": 0.2,        # 티셔츠 등 (Cotton t-shirt)
        "하의": 0.6,        # 청바지 등 (Cotton clothing)
        "신발": 0.9,        # Footwear
        "가방/잡화": 0.5,   # Clothing & accessories
    }
    weight_kg = count * avg_weight_kg.get(item_type, 0.5)

    # Climatiq 검색 결과 기반 ID 매핑 (UI 라벨 → 실제 activity_id, region)
    # 참고: check_ids.py 'Textiles & Clothing' 섹션
    if item_type == "상의":
        # Cotton t-shirt (CN, 2022)
        activity_id = "consumer_goods-type_cotton_t_shirt"
        region = "CN"
    elif item_type == "하의":
        # Cotton clothing (CN, 2022)
        activity_id = "consumer_goods-type_cotton_clothing"
        region = "CN"
    elif item_type == "신발":
        # 기존 footwear ID 사용 (전세계 일반 신발)
        activity_id = "consumer_goods-type_footwear"
        region = "Global"
    else:  # "가방/잡화" 등
        # 별도 액세서리 ID는 없어서 면 의류 평균으로 근사 (무게 기반 ID 유지)
        activity_id = "consumer_goods-type_cotton_clothing"
        region = "CN"

    logger.info(f"[의류 API] 매핑된 activity_id: {activity_id}, region: {region}, 추정 무게: {weight_kg}kg")

    result = _call_climatiq(
        activity_id=activity_id,
        region=region,
        parameters={"weight": weight_kg, "weight_unit": "kg"},
    )

    if result is None:
        # 대략적인 기본 계수 (12 kgCO2e/kg) 사용
        fallback_factor = 12.0
        fallback_result = weight_kg * fallback_factor
        logger.info(f"[의류 API] Fallback 계산 결과: {fallback_result}kgCO2e")
        return fallback_result

    return result


# ---------------------------------------------------------
# 5. 쓰레기 (Waste) 계산
# ---------------------------------------------------------


def calculate_waste_emission(waste_type: str, weight_kg: float) -> float:
    """
    쓰레기 배출에 따른 탄소 배출량 계산.

    Args:
        waste_type: "일반", "재활용" 등
        weight_kg: 배출 무게 (kg)
    """
    logger.info(f"[쓰레기 API] 계산 시작 - 종류: {waste_type}, 무게: {weight_kg}kg")

    if not CLIMATIQ_API_KEY:
        logger.warning("[쓰레기 API] CLIMATIQ_API_KEY가 설정되지 않았습니다. Fallback 사용")
        # 대략적인 기본 계수 (0.5 kgCO2e/kg) 사용
        return weight_kg * 0.5

    # Climatiq 검색 결과 기반 ID 매핑
    # 참고: check_ids.py 'Waste' 섹션
    if waste_type == "재활용":
        # Incineration plastics in municipal solid waste plant (incl. credits) - DE, 2023
        activity_id = "waste_management-type_incineration_plastics_in_municipal_solid_waste_plant_incl_credits-disposal_method_combustion"
        region = "DE"
    else:
        # Municipal solid waste (fuel) - AU, 2023/2024
        activity_id = "fuel-type_waste_solid_municipal-fuel_use_na"
        region = "AU"

    logger.info(f"[쓰레기 API] 매핑된 activity_id: {activity_id}, region: {region}")

    result = _call_climatiq(
        activity_id=activity_id,
        region=region,
        parameters={"weight": weight_kg, "weight_unit": "kg"},
    )

    if result is None:
        fallback_result = weight_kg * 0.5
        logger.info(f"[쓰레기 API] Fallback 계산 결과: {fallback_result}kgCO2e")
        return fallback_result

    return result


# ---------------------------------------------------------
# 6. 물 (Water) 계산
# ---------------------------------------------------------


def calculate_water_emission(volume_liters: float) -> float:
    """
    수돗물 사용량에 따른 탄소 배출량 계산.

    Args:
        volume_liters: 사용량 (리터)
    """
    logger.info(f"[물 API] 계산 시작 - 사용량: {volume_liters}L")

    if not CLIMATIQ_API_KEY:
        logger.warning("[물 API] CLIMATIQ_API_KEY가 설정되지 않았습니다. Fallback 사용")
        # 대략적인 기본 계수 (0.0003 kgCO2e/L) 사용
        return volume_liters * 0.0003

    # Climatiq 검색 결과 기반 ID 매핑
    # Tap water at user (AU, 2022) - unit_type: Weight
    activity_id = "water_supply-type_tap_water_at_user"
    region = "AU"

    # 1L ≈ 1kg 가정 (상수밀도 근사)
    weight_kg = volume_liters * 1.0

    result = _call_climatiq(
        activity_id=activity_id,
        region=region,
        parameters={"weight": weight_kg, "weight_unit": "kg"},
    )

    if result is None:
        fallback_result = volume_liters * 0.0003
        logger.info(f"[물 API] Fallback 계산 결과: {fallback_result}kgCO2e")
        return fallback_result

    return result


# ---------------------------------------------------------
# 7. 통합 계산 함수 (carbon_calculator.py에서 사용)
# ---------------------------------------------------------

def calculate_carbon_with_api(
    category: str,
    activity_type: str,
    value: float,
    unit: str,
    converted_value: float = None,
    standard_unit: str = None
) -> Optional[float]:
    """
    API를 사용하여 탄소 배출량 계산 (카테고리별로 적절한 API 선택)
    
    Args:
        category: 카테고리
        activity_type: 활동 유형
        value: 원본 값
        unit: 원본 단위
        converted_value: 변환된 값 (표준 단위)
        standard_unit: 표준 단위
    
    Returns:
        탄소 배출량 (kgCO2e) 또는 None (API 사용 불가 시)
    """
    logger.info(f"[API 통합] 계산 요청 - 카테고리: {category}, 활동: {activity_type}, 값: {value}{unit}")
    if converted_value:
        logger.info(f"[API 통합] 변환된 값: {converted_value}{standard_unit}")
    
    try:
        if category == "교통":
            logger.info(f"[API 통합] 교통 카테고리 처리 시작")
            # 거리 기반 계산
            distance = converted_value if converted_value else value
            result = calculate_transport_by_type(distance, activity_type)
            logger.info(f"[API 통합] 교통 계산 완료: {result}kgCO2e")
            return result
        
        elif category == "전기":
            logger.info(f"[API 통합] 전기 카테고리 처리 시작")
            # 전력 소비량 기반 계산
            kwh = converted_value if converted_value else value
            result = calculate_energy_emission(kwh, region="KR")
            logger.info(f"[API 통합] 전기 계산 완료: {result}kgCO2e")
            return result
        
        elif category == "식품":
            logger.info(f"[API 통합] 식품 카테고리 처리 시작")
            # 무게 기반 계산
            weight_kg = converted_value if converted_value else value
            result = calculate_food_by_name(activity_type, weight_kg)
            logger.info(f"[API 통합] 식품 계산 완료: {result}kgCO2e")
            return result

        elif category == "의류":
            logger.info(f"[API 통합] 의류 카테고리 처리 시작")
            item_count = converted_value if converted_value else value
            result = calculate_clothing_emission(activity_type, int(item_count))
            logger.info(f"[API 통합] 의류 계산 완료: {result}kgCO2e")
            return result

        elif category == "쓰레기":
            logger.info(f"[API 통합] 쓰레기 카테고리 처리 시작")
            weight_kg = converted_value if converted_value else value
            # activity_type: "일반", "플라스틱", "재활용" 등
            waste_type = "재활용" if activity_type in ["플라스틱", "종이", "유리", "캔"] else "일반"
            result = calculate_waste_emission(waste_type, weight_kg)
            logger.info(f"[API 통합] 쓰레기 계산 완료: {result}kgCO2e")
            return result

        elif category == "물":
            logger.info(f"[API 통합] 물 카테고리 처리 시작")
            volume_l = converted_value if converted_value else value
            result = calculate_water_emission(volume_l)
            logger.info(f"[API 통합] 물 계산 완료: {result}kgCO2e")
            return result

        # 그 외 카테고리는 아직 API 미지원 (로컬 계산 사용)
        logger.info(f"[API 통합] {category} 카테고리는 API 미지원, None 반환 (로컬 계산 사용)")
        return None
        
    except Exception as e:
        logger.error(f"[API 통합] ❌ 계산 오류 ({category}/{activity_type}): {e}", exc_info=True)
        return None
