import reflex as rx
from ecojourney.state import AppState        # <-- ecojourney. 을 꼭 붙여야 합니다
from ecojourney.pages.home import home_page  # <-- 여기도 마찬가지입니다
from ecojourney.pages.intro import intro_page

# ----------------------------------------------------
# 앱 인스턴스 정의 및 라우팅
# ----------------------------------------------------

# AppState를 사용하여 앱을 초기화합니다.
# _state 파라미터를 사용하여 Reflex가 AppState를 인식하도록 함
app = rx.App(_state=AppState)

# 1. 메인 홈 화면 라우팅 (EcoJourney.py 파일 내 home_page 함수 사용)
app.add_page(home_page, route="/", title="EcoJourney | 시작")

# 2. 서비스 소개 화면 라우팅
app.add_page(intro_page, route="/intro", title="EcoJourney | 소개")

# 3. 카테고리 입력 화면 라우팅 (페이지 함수는 pages/ 폴더 내에 정의됨)
# NOTE: pages 폴더 내부의 함수명을 'transportation_page'와 같이 가정합니다.
# app.add_page(transportation.transportation_page, route="/input/transportation", title="EcoJourney | 교통")
# app.add_page(food.food_page, route="/input/food", title="EcoJourney | 식품")
# app.add_page(clothing.clothing_page, route="/input/clothing", title="EcoJourney | 의류")
# app.add_page(electricity.electricity_page, route="/input/electricity", route_alias="/input/water", title="EcoJourney | 전기") 
# TODO: waste와 water 페이지에 대한 정확한 함수명으로 업데이트 필요
# app.add_page(water.water_page, route="/input/water", title="EcoJourney | 물")
# app.add_page(waste.waste_page, route="/input/waste", title="EcoJourney | 쓰레기 배출")


# 4. 결과 리포트 화면 라우팅
# app.add_page(report.report_page, route="/report", title="EcoJourney | 결과 리포트")

