# 탄소 배출량 계산 API 통합 가이드

## 개요

EcoJourney는 탄소 배출량 계산을 위해 외부 API를 사용할 수 있습니다. API가 실패하거나 키가 없는 경우 자동으로 로컬 배출 계수로 Fallback됩니다.

## 지원하는 API

### 1. Climatiq API
- **용도**: 일상 생활 행동 (교통, 전기, 물, 쓰레기)
- **웹사이트**: https://www.climatiq.io/
- **API 문서**: https://docs.climatiq.io/
- **무료 티어**: 제공 (제한 있음)


## API 키 발급 방법

### Climatiq API 키 발급

1. **Climatiq 웹사이트 접속**
   - https://www.climatiq.io/ 접속
   - 회원가입 또는 로그인

2. **API 키 생성**
   - 대시보드에서 "API Keys" 섹션으로 이동
   - "Create API Key" 버튼 클릭
   - 생성된 API 키를 복사

3. **`.env` 파일에 추가**
   ```
   CLIMATIQ_API_KEY=your_climatiq_api_key_here
   ```

### CarbonCloud API 키 발급

1. **CarbonCloud 웹사이트 접속**
   - https://www.carboncloud.com/ 접속
   - 회원가입 또는 로그인

2. **API 키 생성**
   - 대시보드에서 API 설정으로 이동
   - API 키 생성 및 복사

3. **`.env` 파일에 추가**
   ```
   CARBONCLOUD_API_KEY=your_carboncloud_api_key_here
   ```

## 사용 방법

### 자동 Fallback 시스템

API는 자동으로 사용되며, 다음 경우에 로컬 배출 계수로 Fallback됩니다:

1. API 키가 설정되지 않은 경우
2. API 호출 실패 시
3. 네트워크 오류 시
4. 의류 카테고리 (API 미지원)

### 코드에서 사용

```python
from ecojourney.service.carbon_calculator import calculate_carbon_emission

# API 우선 사용 (기본값)
result = calculate_carbon_emission(
    category="교통",
    activity_type="자동차",
    value=10.0,
    unit="km"
)

# 결과에 계산 방법이 포함됨
print(result["calculation_method"])  # "api" 또는 "local"
print(result["carbon_emission_kg"])  # 탄소 배출량 (kgCO2e)
```

## API 매핑

### Climatiq 활동 ID

- **교통**
  - 자동차: `passenger_vehicle-vehicle_type_car-fuel_source_na-distance_na-engine_size_na`
  - 버스: `passenger_vehicle-vehicle_type_bus-fuel_source_na-distance_na`
  - 지하철: `passenger_vehicle-vehicle_type_train-fuel_source_electricity-distance_na`
  - 걷기/자전거: 탄소 배출 없음 (0.0 반환)

- **전기**
  - 냉방기/난방기: `electricity-energy_source_grid_mix-consumer_user_grid_mix`

- **물**
  - 샤워/설거지/세탁: `water-supply_chain-water_treatment`

- **쓰레기**
  - 일반: `waste-disposal_of_waste_to_landfill`
  - 플라스틱: `waste-disposal_of_waste_plastic_to_landfill`
  - 종이: `waste-disposal_of_waste_paper_to_landfill`
  - 유리: `waste-disposal_of_waste_glass_to_landfill`
  - 캔: `waste-disposal_of_waste_metal_to_landfill`

### CarbonCloud 제품 매핑

- 소고기: `beef`
- 돼지고기: `pork`
- 양파: `onion`
- 파: `spring_onion`
- 마늘: `garlic`

## 주의사항

1. **API 호출 제한**: 각 API는 무료 티어에서 호출 제한이 있을 수 있습니다.
2. **네트워크 지연**: API 호출은 네트워크 지연이 발생할 수 있으므로, Fallback 시스템이 중요합니다.
3. **의류 카테고리**: 현재 Climatiq와 CarbonCloud 모두 의류에 대한 데이터가 제한적이므로 로컬 배출 계수를 사용합니다.
4. **환경 변수**: API 키는 절대 Git에 커밋하지 마세요 (`.gitignore`에 포함되어 있습니다).

## 문제 해결

### API가 작동하지 않는 경우

1. `.env` 파일에 API 키가 올바르게 설정되었는지 확인
2. API 키가 유효한지 확인
3. 네트워크 연결 확인
4. 로그에서 오류 메시지 확인

API가 실패해도 자동으로 로컬 배출 계수를 사용하므로 앱은 정상 작동합니다.












