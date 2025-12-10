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

def calculate_food_emission_by_serving(food_type: str, servings: float) -> float:
    """
    한끼 기준 음식의 탄소 배출량 계산 (한국일보 한끼 밥상 탄소 계산기 출처)
    
    Args:
        food_type: 음식 종류
        servings: 한끼 수 (회)
    
    Returns:
        탄소 배출량 (kgCO2e)
    """
    # 한국일보 한끼 밥상 탄소 계산기 데이터 (한끼 기준 kgCO2e)
    serving_based_emissions = {
        # 밥
        "rice_bowl_plain": 0.5,  # 쌀밥
        "rice_bowl_mixed": 1.1,  # 잡곡밥
        "rice_bowl_brown": 0.2,  # 현미밥
        "rice_bowl_barley": 0.1,  # 보리밥
        "rice_bowl_bean": 0.1,  # 콩밥
        "gimbap": 0.4,  # 김밥
        "bibimbap_beef": 1.4,  # 비빔밥(불고기)
        "bibimbap_vegetable": 0.7,  # 비빔밥(산채)
        "kimchi_fried_rice": 0.4,  # 김치볶음밥
        # 면
        "naengmyeon_cold": 2.4,  # 물냉면
        "naengmyeon_bibim": 1.1,  # 비빔냉면
        "janchi_guksu": 1.8,  # 잔치국수
        "bibim_guksu": 1.3,  # 비빔국수
        "haemul_kalguksu": 0.4,  # 해물칼국수
        # 국/탕/찌개
        "doenjang_guk": 0.9,  # 된장국
        "miyeok_guk": 2.6,  # 미역국
        "kongnamul_guk": 0.5,  # 콩나물국
        "doenjang_jjigae": 1.5,  # 된찌
        "kimchi_jjigae": 2.3,  # 김찌
        "sundubu_jjigae": 0.7,  # 순두부찌개
        "seolleongtang": 10.0,  # 설렁탕
        "galbitang": 5.0,  # 갈비탕
        "gomtang": 9.7,  # 곰탕
        # 반찬
        "kimchi_cabbage": 0.3,  # 배추김치
        "kimchi_kkakdugi": 0.3,  # 깍두기
        "kimchi_chonggak": 0.1,  # 총각김치
        "kimchi_yeolmu": 0.2,  # 열무김치
        "sukju_namul": 0.1,  # 숙주나물
        "kongnamul_muchim": 0.2,  # 콩나물무침
        "spinach_namul": 0.5,  # 시금치나물
        "mu_saengchae": 0.0,  # 무생채
        "beef_jangjorim": 5.5,  # 소고기장조림
        "anchovy_jorim": 0.1,  # 멸치조림
        "kong_jaban": 0.7,  # 콩자반
        "perilla_jangajji": 0.1,  # 깻잎장아찌
        "jeyuk_bokkeum": 1.9,  # 제육볶음
        "squid_bokkeum": 0.6,  # 오징어볶음
        "bulgogi": 13.9,  # 불고기
        "japchae": 0.6,  # 잡채
        "mackerel_grilled": 0.3,  # 고등어구이
        "egg_fried": 0.1,  # 달걀 프라이
        "egg_steamed": 0.2,  # 달걀찜
        # 고기
        "beef_grilled": 7.7,  # 소고기 구이
        "pork_belly_grilled": 2.0,  # 삼겹살 구이
        # 과일
        "strawberry": 0.1,  # 딸기
        "melon": 0.1,  # 참외
        "watermelon": 0.1,  # 수박
        "apple": 0.1,  # 사과
        "peach": 0.1,  # 복숭아
        "persimmon": 0.0,  # 단감 (일주일 먹으면 0.2)
        "grape": 0.0,  # 포도 (일주일 먹으면 0.3)
        "mandarin": 0.0,  # 감귤 (일주일 먹으면 0.2)
        "kiwi": 0.0,  # 키위 (일주일 먹으면 0.2)
        "tomato": 0.1,  # 토마토
        "cherry_tomato": 0.2,  # 방울토마토
        # 패스트푸드
        "pizza_korean": 2.0,  # 피자 (한국일보 기준)
        "hamburger_set": 3.7,  # 햄버거 세트 (한국일보 기준)
        "fried_chicken": 2.1,  # 후라이드 치킨 (한국일보 기준)
        # 유제품
        "milk": 1.2,  # 우유
        "cheese": 11.3,  # 치즈
        "soy_milk": 0.3,  # 두유
        # 커피
        "espresso": 0.3,  # 에스프레소
        "cafe_latte_korean": 0.6,  # 카페라떼 (한국일보 기준)
        # 파스타는 API 사용하므로 serving_based_emissions에서 제외
    }
    
    emission_per_serving = serving_based_emissions.get(food_type, 0.0)
    result = servings * emission_per_serving
    logger.info(f"[식품 한끼 기준] 계산 결과: {servings}회 × {emission_per_serving} = {result}kgCO2e (food_type: {food_type})")
    return result


def calculate_food_emission(food_type: str, weight_kg: float) -> float:
    """
    음식 종류와 무게에 따른 배출량 계산
    Climatiq의 IPCC 데이터를 활용
    
    각 음식 항목의 기준과 계산 방법:
    
    **API 사용 항목** (Climatiq API 검색 결과에서 확인된 항목):
    - 샐러드 (salad): food-type_caesar_salad_chicken_croutons_sauce (FR region)
    - 샌드위치 (sandwich): food-type_vegetarian_sandwiches (GLOBAL)
    - 초밥 (sushi): food-type_sushi_ready_meals (DK, GB, NL)
    - 쌀국수 (rice_noodles): food-type_rice_noodles (ES, GB, FR)
    - 짜장면/짬뽕 (fried_noodles): food-type_noodles_with_shrimps_sauteed_pan_fried (FR)
    
    **Fallback 사용 항목** (검색 결과에 없거나 API 호출 실패):
    1. 파스타 (pasta)
       - 이유: Climatiq API 검색 결과에 정확한 항목 없음
       - Fallback 배출 계수: 3.5 kgCO2e/kg
       - 계산: 무게(kg) × 3.5
    
    2. 만두 (dumpling)
       - 이유: Climatiq API 검색 결과에 정확한 항목 없음
       - Fallback 배출 계수: 4.0 kgCO2e/kg
       - 계산: 무게(kg) × 4.0
    
    3. 찌개 (soup)
       - 이유: Climatiq API 검색 결과에 정확한 항목 없음
       - Fallback 배출 계수: 2.5 kgCO2e/kg
       - 계산: 무게(kg) × 2.5
    
    계산 우선순위:
    1. Climatiq API 사용 (검색 결과에서 확인된 항목만, activity_id로 조회, Global region)
    2. API 실패 또는 검색 결과 없음 시 Fallback 배출 계수 사용
    
    Args:
        food_type: 음식 종류 ("beef", "pork", "chicken", "coffee", "rice", "pasta" 등)
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
            "hamburger": 6.5,  # 패스트푸드 햄버거 (고기+가공)
            "pizza": 5.5,  # 피자 (치즈+가공)
            "chicken_fastfood": 7.0,  # 패스트푸드 치킨
            # 일상 음식 카테고리 (요청된 항목만)
            "pasta": 3.5,  # 파스타 (일반 파스타, 오일 파스타 포함)
            "salad": 2.0,  # 샐러드 (시저 샐러드 기준: 닭고기+크루통+소스 포함)
            "sandwich": 4.5,  # 샌드위치 (채소 샌드위치 기준)
            "sushi": 4.5,  # 초밥 (레디미얼 초밥 기준)
            "dumpling": 4.0,  # 만두 (일반 만두 기준)
            "rice_noodles": 3.5,  # 쌀국수 (쌀 면 기준)
            "fried_noodles": 4.5,  # 볶음면 (짜장면/짬뽕: 볶음 조리 방식 기준)
            "soup": 2.5,  # 찌개 (일반 수프/국 기준)
        }
        fallback_result = weight_kg * defaults.get(food_type, 4.0)  # 기본값: 쌀 기준
        logger.info(f"[식품 API] Fallback 계산 결과: {fallback_result}kgCO2e (food_type: {food_type})")
        return fallback_result
    
    # Climatiq API에 정확히 표시되어 있는 항목만 API 사용
    # check_ids.py 검색 결과를 기반으로 API 사용 여부 결정
    # 검색 결과에 없거나 API 호출이 실패하는 항목은 Fallback 사용
    
    # API 사용 가능한 항목 (검색 결과에서 확인된 항목)
    api_enabled_foods = {
        # 기본 식품 (기존에 작동 확인된 항목)
        "beef": "consumer_goods-type_meat_products_beef",
        "pork": "food-type_pork",
        "chicken": "consumer_goods-type_meat_products_poultry",
        "coffee": "consumer_goods-type_beverages_coffee_green_bean",
        "rice": "consumer_goods-type_cereals_rice",
        "rice_bowl": "consumer_goods-type_processed_rice",
        "hamburger": "food-type_hamburger_from_fast_foods_restaurant",
        "pizza": "food-type_pizza_vegetables_or_pizza_4_seasons",
        "chicken_fastfood": "food-type_chicken_grilled_fast_food",
        # 일상 음식 (검색 결과에서 확인된 항목만)
        "rice_noodles": "food-type_rice_noodles",  # 검색 결과: ES, GB, FR
        "fried_noodles": "food-type_noodles_with_shrimps_sauteed_pan_fried",  # 검색 결과: FR
        # 완성된 파스타 요리만 (면만은 제외)
        "carbonara": "food-type_carbonara_style_pasta_spaghetti_tagliatelle",  # FR - 카르보나라 파스타
        "lasagna": "food-type_lasagna_or_cannelloni_with_vegetables",  # FR - 라자냐/카넬로니
        "ravioli": "food-type_ravioli_filled_with_vegetables_in_tomato_sauce_canned",  # FR - 라비올리
        "pasta_salad": "food-type_prepared_pasta_salad_with_vegetable_meat_or_fish",  # FR - 파스타 샐러드
    }
    
    # Fallback만 사용하는 항목 (검색 결과에 없거나 API 호출 실패)
    fallback_only_foods = {
        "dumpling",  # 검색 결과에 없음
        "soup",  # 검색 결과에 없음
    }
    
    # API 사용 여부 확인
    use_api = food_type in api_enabled_foods and food_type not in fallback_only_foods
    
    if use_api:
        activity_id = api_enabled_foods[food_type]
        logger.info(f"[식품 API] API 사용 - activity_id: {activity_id}, food_type: {food_type}")
        
        # 음식은 지역 특성을 덜 타므로 Global 우선 사용 권장 (데이터가 더 많음)
        # KR 시도 -> 실패시 _call_climatiq 내부에서 Global로 재시도함
        result = _call_climatiq(
            activity_id=activity_id,
            region="Global",  # Global 우선 사용
            parameters={"weight": weight_kg, "weight_unit": "kg"},
            source="exiobase"  # 전세계 산업 연관 분석 데이터
        )
        
        if result is not None:
            return result
        else:
            logger.warning(f"[식품 API] API 호출 실패, Fallback 사용 - food_type: {food_type}")
    else:
        logger.info(f"[식품 API] Fallback 사용 (검색 결과 없음 또는 API 미지원) - food_type: {food_type}")
        result = None
    
    if result is None:
        # Fallback: 로컬 배출 계수 사용
        defaults = {
            "beef": 27.0, 
            "pork": 7.0, 
            "chicken": 6.9, 
            "coffee": 17.0, 
            "rice": 4.0,
            "rice_bowl": 4.0,
            "hamburger": 6.5,  # 패스트푸드 햄버거 (고기+가공)
            "pizza": 5.5,  # 피자 (치즈+가공)
            "chicken_fastfood": 7.0,  # 패스트푸드 치킨
        }
        # Fallback: 로컬 배출 계수 사용 (위의 defaults 재사용)
        defaults_fallback = {
            "beef": 27.0, 
            "pork": 7.0, 
            "chicken": 6.9, 
            "coffee": 17.0, 
            "rice": 4.0,
            "rice_bowl": 4.0,
            "hamburger": 6.5,
            "pizza": 5.5,
            "chicken_fastfood": 7.0,
            "pasta": 3.5,  # 파스타 (일반 파스타, 오일 파스타 포함)
            "salad": 2.0,  # 샐러드 (시저 샐러드 기준)
            "sandwich": 4.5,  # 샌드위치 (채소 샌드위치 기준)
            "sushi": 4.5,  # 초밥 (레디미얼 초밥 기준)
            "dumpling": 4.0,  # 만두 (일반 만두 기준)
            "rice_noodles": 3.5,  # 쌀국수 (쌀 면 기준)
            "fried_noodles": 4.5,  # 볶음면 (짜장면/짬뽕: 볶음 조리 방식 기준)
            "soup": 2.5,  # 찌개 (일반 수프/국 기준)
        }
        fallback_result = weight_kg * defaults_fallback.get(food_type, 4.0)  # 기본값: 쌀 기준
        logger.info(f"[식품 API] Fallback 계산 결과: {fallback_result}kgCO2e (food_type: {food_type})")
        return fallback_result
    
    return result


    # 한국어 음식 이름 → food_type 매핑
    # 한끼 기준 항목은 "serving_" 접두사로 구분
FOOD_TYPE_MAP = {
    # 기본 식품
    "소고기": "beef",
    "돼지고기": "pork",
    "닭고기": "chicken",
    "고기류": "beef",  # 기본값
    # 쌀밥과 커피
    "쌀밥": "rice_bowl_plain",
    "커피": "coffee",
    "아메리카노": "coffee",  # 커피 하위 카테고리
    "카페라떼": "cafe_latte_korean",  # 한끼 기준 항목
    # 패스트푸드
    "햄버거": "hamburger",
    "피자": "pizza",
    "치킨": "chicken_fastfood",
    "패스트푸드": "hamburger",  # 기본값
    # 양식 (완성된 파스타 요리만)
    "카르보나라": "carbonara",
    "라자냐": "lasagna",
    "카넬로니": "lasagna",
    "라비올리": "ravioli",
    "파스타샐러드": "pasta_salad",
    # 중식
    "만두": "dumpling",
    "교자": "dumpling",
    # 면류
    "쌀국수": "rice_noodles",
    "짜장면": "fried_noodles",  # 볶음면 기준 (유사한 조리 방식)
    "짬뽕": "fried_noodles",  # 볶음면 기준 (유사한 조리 방식)
    # 조리된 음식
    "찌개": "soup",  # 일반 수프/국 기준
    "국": "soup",
    "수프": "soup",
    
    # 한끼 기준 항목 (한국일보 한끼 밥상 탄소 계산기 출처)
    # 밥
    "잡곡밥": "rice_bowl_mixed",
    "현미밥": "rice_bowl_brown",
    "보리밥": "rice_bowl_barley",
    "콩밥": "rice_bowl_bean",
    "김밥": "gimbap",
    "비빔밥": "bibimbap_vegetable",  # 기본값: 산채
    "비빔밥불고기": "bibimbap_beef",
    "비빔밥산채": "bibimbap_vegetable",
    "김치볶음밥": "kimchi_fried_rice",
    # 면
    "물냉면": "naengmyeon_cold",
    "비빔냉면": "naengmyeon_bibim",
    "잔치국수": "janchi_guksu",
    "비빔국수": "bibim_guksu",
    "해물칼국수": "haemul_kalguksu",
    # 국/탕/찌개
    "된장국": "doenjang_guk",
    "미역국": "miyeok_guk",
    "콩나물국": "kongnamul_guk",
    "된찌": "doenjang_jjigae",
    "된장찌개": "doenjang_jjigae",
    "김찌": "kimchi_jjigae",
    "김치찌개": "kimchi_jjigae",
    "순두부찌개": "sundubu_jjigae",
    "설렁탕": "seolleongtang",
    "갈비탕": "galbitang",
    "곰탕": "gomtang",
    # 반찬
    "배추김치": "kimchi_cabbage",
    "깍두기": "kimchi_kkakdugi",
    "총각김치": "kimchi_chonggak",
    "열무김치": "kimchi_yeolmu",
    "숙주나물": "sukju_namul",
    "콩나물무침": "kongnamul_muchim",
    "시금치나물": "spinach_namul",
    "무생채": "mu_saengchae",
    "소고기장조림": "beef_jangjorim",
    "멸치조림": "anchovy_jorim",
    "콩자반": "kong_jaban",
    "깻잎장아찌": "perilla_jangajji",
    "제육볶음": "jeyuk_bokkeum",
    "오징어볶음": "squid_bokkeum",
    "불고기": "bulgogi",
    "잡채": "japchae",
    "고등어구이": "mackerel_grilled",
    "달걀프라이": "egg_fried",
    "달걀찜": "egg_steamed",
    # 고기
    "소고기구이": "beef_grilled",
    "삼겹살구이": "pork_belly_grilled",
    "삼겹살": "pork_belly_grilled",
    # 과일
    "딸기": "strawberry",
    "참외": "melon",
    "수박": "watermelon",
    "사과": "apple",
    "복숭아": "peach",
    "단감": "persimmon",
    "포도": "grape",
    "감귤": "mandarin",
    "키위": "kiwi",
    "토마토": "tomato",
    "방울토마토": "cherry_tomato",
    # 패스트푸드 (한국일보 기준)
    "피자한국": "pizza_korean",
    "햄버거세트": "hamburger_set",
    "후라이드치킨": "fried_chicken",
    # 유제품
    "우유": "milk",
    "치즈": "cheese",
    "두유": "soy_milk",
    # 커피 (한국일보 기준)
    "에스프레소": "espresso",
    "카페라떼한국": "cafe_latte_korean",
}


def calculate_food_by_name(food_name: str, weight_kg: float = None, servings: float = None) -> float:
    """
    한국어 음식 이름으로 탄소 배출량 계산
    한끼 기준 항목은 servings를 사용하고, 일반 항목은 weight_kg를 사용합니다.
    
    Args:
        food_name: 음식 이름 ("소고기", "돼지고기", "김밥" 등)
        weight_kg: 무게 (kg) - 일반 항목용
        servings: 한끼 수 (회) - 한끼 기준 항목용
    
    Returns:
        탄소 배출량 (kgCO2e)
    """
    logger.info(f"[식품] 한국어 이름 변환 - 입력: {food_name}, 무게: {weight_kg}kg, 한끼: {servings}회")
    food_type = FOOD_TYPE_MAP.get(food_name, "rice")  # 기본값: 쌀
    logger.info(f"[식품] 매핑된 food_type: {food_type}")
    
    # 한끼 기준 항목 목록 (한국일보 한끼 밥상 탄소 계산기 출처)
    serving_based_types = {
        "rice_bowl_plain", "rice_bowl_mixed", "rice_bowl_brown", "rice_bowl_barley", "rice_bowl_bean",
        "gimbap", "bibimbap_beef", "bibimbap_vegetable", "kimchi_fried_rice",
        "naengmyeon_cold", "naengmyeon_bibim", "janchi_guksu", "bibim_guksu", "haemul_kalguksu",
        "doenjang_guk", "miyeok_guk", "kongnamul_guk", "doenjang_jjigae", "kimchi_jjigae",
        "sundubu_jjigae", "seolleongtang", "galbitang", "gomtang",
        "kimchi_cabbage", "kimchi_kkakdugi", "kimchi_chonggak", "kimchi_yeolmu",
        "sukju_namul", "kongnamul_muchim", "spinach_namul", "mu_saengchae",
        "beef_jangjorim", "anchovy_jorim", "kong_jaban", "perilla_jangajji",
        "jeyuk_bokkeum", "squid_bokkeum", "bulgogi", "japchae", "mackerel_grilled",
        "egg_fried", "egg_steamed", "beef_grilled", "pork_belly_grilled",
        "strawberry", "melon", "watermelon", "apple", "peach", "persimmon",
        "grape", "mandarin", "kiwi", "tomato", "cherry_tomato",
        "pizza_korean", "hamburger_set", "fried_chicken",
        "milk", "cheese", "soy_milk", "espresso", "cafe_latte_korean"
        # 파스타는 API 사용하므로 serving_based_types에서 제외
    }
    
    # 한끼 기준 항목인지 확인
    if food_type in serving_based_types:
        if servings is None:
            servings = 1.0  # 기본값: 1회
        result = calculate_food_emission_by_serving(food_type, servings)
    else:
        if weight_kg is None:
            weight_kg = 0.2  # 기본값: 0.2kg
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
            # 파스타 항목만 Climatiq API 사용 (1회를 kg으로 변환하여 API 호출)
            pasta_items = {"카르보나라", "라자냐", "카넬로니", "라비올리", "파스타샐러드"}
            
            if activity_type in pasta_items:
                # 파스타는 1회를 약 0.25kg (250g)로 변환하여 API 호출
                # 일반적인 파스타 1인분은 약 200-300g이므로 평균 250g 사용
                weight_kg = (converted_value if converted_value else value) * 0.25
                result = calculate_food_by_name(activity_type, weight_kg=weight_kg)
                logger.info(f"[API 통합] 파스타 API 계산 완료: {converted_value}회 → {weight_kg}kg = {result}kgCO2e")
                return result
            else:
                # 나머지는 한끼 기준 로컬 계산
                logger.info(f"[API 통합] 식품 카테고리는 로컬 계산 사용 (한국일보 한끼 밥상 탄소 계산기)")
                return None

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
