"""
탄소 배출량 입력 및 저장 관련 State
"""

import reflex as rx
from typing import Dict, List, Any, Optional
from datetime import date
import logging
from .base import BaseState
from .auth import AuthState
from ..models import User, CarbonLog

logger = logging.getLogger(__name__)


class CarbonState(AuthState):
    """
    탄소 배출량 입력 및 저장 관련 상태 및 로직
    """
    # 저장 관련 상태
    save_message: str = ""
    is_saving: bool = False
    is_save_success: bool = False
    saved_logs_history: List[Dict[str, Any]] = []
    has_today_log: bool = False  # 오늘 날짜에 저장된 로그가 있는지
    
    # ---------- 교통수단 선택 상태 ----------
    selected_car: bool = False
    selected_bus: bool = False
    selected_subway: bool = False
    selected_walk: bool = False
    selected_bike: bool = False
    
    # 입력 필드 표시 여부
    show_car: bool = False
    show_bus: bool = False
    show_subway: bool = False
    show_walk: bool = False
    show_bike: bool = False
    trans_input_mode: bool = False

    # ---------- 식품 선택 상태 ----------
    selected_dairy: bool = False
    selected_rice: bool = False
    selected_coffee: bool = False
    selected_fastfood: bool = False
    selected_noodles: bool = False  # 면류 (한국일보 기준만)
    selected_cooked: bool = False  # 조리된 음식 (한국일보 기준만)
    selected_side_dish: bool = False  # 반찬
    selected_grilled_meat: bool = False  # 고기
    selected_fruit: bool = False  # 과일
    selected_pasta: bool = False  # 파스타 (Climatiq API)

    show_dairy: bool = False
    show_rice: bool = False
    show_coffee: bool = False
    show_fastfood: bool = False
    show_noodles: bool = False
    show_cooked: bool = False
    show_side_dish: bool = False
    show_grilled_meat: bool = False
    show_fruit: bool = False
    show_pasta: bool = False
    food_input_mode: bool = False
    
    # ------------------------------ 교통 관련 메서드 ------------------------------
    
    def toggle_car(self):
        self.selected_car = not self.selected_car
    
    def toggle_bus(self):
        self.selected_bus = not self.selected_bus
    
    def toggle_subway(self):
        self.selected_subway = not self.selected_subway
    
    def toggle_walk(self):
        self.selected_walk = not self.selected_walk
    
    def toggle_bike(self):
        self.selected_bike = not self.selected_bike
    
    def show_trans_input_fields(self):
        """선택된 항목들의 입력 필드를 표시"""
        self.show_car = self.selected_car
        self.show_bus = self.selected_bus
        self.show_subway = self.selected_subway
        self.show_walk = self.selected_walk
        self.show_bike = self.selected_bike
        self.trans_input_mode = True
    
    def handle_transport_submit(self, form_data: dict):
        """교통 입력값 폼 제출 -> 데이터 저장 -> 다음 페이지 이동"""
        # 기존 교통 데이터 제거
        self.all_activities = [
            act for act in self.all_activities 
            if act.get("category") != "교통"
        ]
        
        transport_data = []
        
        if self.show_car and form_data.get("car_value"):
            transport_data.append({
                "category": "교통",
                "activity_type": "자동차",
                "value": float(form_data.get("car_value", 0)),
                "unit": form_data.get("car_unit", "km"),
            })
        
        if self.show_bus and form_data.get("bus_value"):
            transport_data.append({
                "category": "교통",
                "activity_type": "버스",
                "value": float(form_data.get("bus_value", 0)),
                "unit": form_data.get("bus_unit", "km"),
            })
        
        if self.show_subway and form_data.get("subway_value"):
            transport_data.append({
                "category": "교통",
                "activity_type": "지하철",
                "value": float(form_data.get("subway_value", 0)),
                "unit": form_data.get("subway_unit", "km"),
            })
        
        if self.show_walk and form_data.get("walk_value"):
            transport_data.append({
                "category": "교통",
                "activity_type": "걷기",
                "value": float(form_data.get("walk_value", 0)),
                "unit": form_data.get("walk_unit", "km"),
            })
        
        if self.show_bike and form_data.get("bike_value"):
            transport_data.append({
                "category": "교통",
                "activity_type": "자전거",
                "value": float(form_data.get("bike_value", 0)),
                "unit": form_data.get("bike_unit", "km"),
            })
        
        self.all_activities = self.all_activities + transport_data
        
        # 입력모드 종료 + 선택 초기화
        self.trans_input_mode = False
        self.selected_car = False
        self.selected_bus = False
        self.selected_subway = False
        self.selected_walk = False
        self.selected_bike = False
        self.show_car = False
        self.show_bus = False
        self.show_subway = False
        self.show_walk = False
        self.show_bike = False
        
        return rx.redirect("/input/food")
    
    # ------------------------------ 식품 관련 메서드 ------------------------------
    
    def toggle_dairy(self):
        self.selected_dairy = not self.selected_dairy

    def toggle_rice(self):
        self.selected_rice = not self.selected_rice

    def toggle_coffee(self):
        self.selected_coffee = not self.selected_coffee

    def toggle_fastfood(self):
        self.selected_fastfood = not self.selected_fastfood

    def toggle_noodles(self):
        self.selected_noodles = not self.selected_noodles

    def toggle_cooked(self):
        self.selected_cooked = not self.selected_cooked

    def toggle_side_dish(self):
        self.selected_side_dish = not self.selected_side_dish

    def toggle_grilled_meat(self):
        self.selected_grilled_meat = not self.selected_grilled_meat

    def toggle_fruit(self):
        self.selected_fruit = not self.selected_fruit

    def toggle_pasta(self):
        self.selected_pasta = not self.selected_pasta

    def show_food_input_fields(self):
        """선택된 음식 항목들의 입력 필드를 표시"""
        self.show_dairy = self.selected_dairy
        self.show_rice = self.selected_rice
        self.show_coffee = self.selected_coffee
        self.show_fastfood = self.selected_fastfood
        self.show_noodles = self.selected_noodles
        self.show_cooked = self.selected_cooked
        self.show_side_dish = self.selected_side_dish
        self.show_grilled_meat = self.selected_grilled_meat
        self.show_fruit = self.selected_fruit
        self.show_pasta = self.selected_pasta
        self.food_input_mode = True

    def handle_food_submit(self, form_data: dict):
        """음식 입력값 제출 처리"""
        # 기존 음식 데이터 제거
        self.all_activities = [
            act for act in self.all_activities
            if act.get("category") != "식품"
        ]

        food_data = []

        if self.show_dairy and form_data.get("dairy_value"):
            # 유제품류: 우유/치즈/두유를 activity_type으로 저장
            dairy_sub = form_data.get("dairy_sub") or "우유"
            food_data.append({
                "category": "식품",
                "activity_type": dairy_sub,
                "subcategory": "유제품류",
                "value": float(form_data.get("dairy_value", 0)),
                "unit": "회",
            })

        if self.show_rice and form_data.get("rice_value"):
            # 쌀밥: 세부 선택을 activity_type으로 저장
            rice_sub = form_data.get("rice_sub") or "쌀밥"
            food_data.append({
                "category": "식품",
                "activity_type": rice_sub,
                "subcategory": "쌀밥",
                "value": float(form_data.get("rice_value", 0)),
                "unit": "회",
            })

        if self.show_coffee and form_data.get("coffee_value"):
            # 커피: 한국일보 기준만 (에스프레소, 카페라떼한국)
            coffee_sub = form_data.get("coffee_sub") or "에스프레소"
            food_data.append({
                "category": "식품",
                "activity_type": coffee_sub,
                "subcategory": "커피",
                "value": float(form_data.get("coffee_value", 0)),
                "unit": "회",
            })

        if self.show_fastfood and form_data.get("fastfood_value"):
            # 패스트푸드: 한국일보 기준만 (피자, 햄버거세트, 후라이드치킨)
            fastfood_sub = form_data.get("fastfood_sub") or "피자"
            food_data.append({
                "category": "식품",
                "activity_type": fastfood_sub,
                "subcategory": "패스트푸드",
                "value": float(form_data.get("fastfood_value", 0)),
                "unit": "회",
            })

        if self.show_noodles and form_data.get("noodles_value"):
            # 면류: 한국일보 기준만 (물냉면, 비빔냉면, 잔치국수, 비빔국수, 해물칼국수)
            noodles_sub = form_data.get("noodles_sub") or "물냉면"
            food_data.append({
                "category": "식품",
                "activity_type": noodles_sub,
                "subcategory": "면류",
                "value": float(form_data.get("noodles_value", 0)),
                "unit": "회",
            })

        if self.show_cooked and form_data.get("cooked_value"):
            # 조리된 음식: 한국일보 기준만 (된장국, 미역국, 콩나물국, 된장찌개, 김치찌개, 순두부찌개, 설렁탕, 갈비탕, 곰탕)
            cooked_sub = form_data.get("cooked_sub") or "된장국"
            food_data.append({
                "category": "식품",
                "activity_type": cooked_sub,
                "subcategory": "국/찌개",
                "value": float(form_data.get("cooked_value", 0)),
                "unit": "회",
            })

        if self.show_side_dish and form_data.get("side_dish_value"):
            # 반찬: 세부 선택을 activity_type으로 저장
            side_dish_sub = form_data.get("side_dish_sub") or "배추김치"
            food_data.append({
                "category": "식품",
                "activity_type": side_dish_sub,
                "subcategory": "반찬",
                "value": float(form_data.get("side_dish_value", 0)),
                "unit": "회",
            })

        if self.show_grilled_meat and form_data.get("grilled_meat_value"):
            # 고기: 세부 선택을 activity_type으로 저장
            grilled_meat_sub = form_data.get("grilled_meat_sub") or "소고기구이"
            food_data.append({
                "category": "식품",
                "activity_type": grilled_meat_sub,
                "subcategory": "고기",
                "value": float(form_data.get("grilled_meat_value", 0)),
                "unit": "회",
            })

        if self.show_fruit and form_data.get("fruit_value"):
            # 과일: 세부 선택을 activity_type으로 저장
            fruit_sub = form_data.get("fruit_sub") or "딸기"
            food_data.append({
                "category": "식품",
                "activity_type": fruit_sub,
                "subcategory": "과일",
                "value": float(form_data.get("fruit_value", 0)),
                "unit": "회",
            })

        if self.show_pasta and form_data.get("pasta_value"):
            # 파스타: 한끼 기준 로컬 계산
            pasta_sub = form_data.get("pasta_sub") or "카르보나라"
            food_data.append({
                "category": "식품",
                "activity_type": pasta_sub,
                "subcategory": "파스타",
                "value": float(form_data.get("pasta_value", 0)),
                "unit": "회",
            })

        self.all_activities = self.all_activities + food_data

        # 입력모드 종료 + 선택 초기화
        self.food_input_mode = False
        self.selected_dairy = False
        self.selected_rice = False
        self.selected_coffee = False
        self.selected_fastfood = False
        self.selected_noodles = False
        self.selected_cooked = False
        self.selected_side_dish = False
        self.selected_grilled_meat = False
        self.selected_fruit = False
        self.selected_pasta = False
        self.show_dairy = False
        self.show_rice = False
        self.show_coffee = False
        self.show_fastfood = False
        self.show_noodles = False
        self.show_cooked = False
        self.show_side_dish = False
        self.show_grilled_meat = False
        self.show_fruit = False
        self.show_pasta = False

        return rx.redirect("/input/clothing")
    
    # ------------------------------ 의류 관련 메서드 ------------------------------
    
    # 의류 입력 상태
    clothing_type: str = ""
    clothing_count: float = 0.0
    clothing_is_vintage: bool = False
    
    def handle_clothing_submit(self, form_data: dict):
        """의류 입력값 제출 처리"""
        # 기존 의류 데이터 제거
        self.all_activities = [
            act for act in self.all_activities
            if act.get("category") != "의류"
        ]

        clothing_items = []

        # 여러 종류를 한 번에 입력할 수 있도록 처리
        mapping = [
            ("상의", "top_count", "top_vintage"),
            ("하의", "bottom_count", "bottom_vintage"),
            ("신발", "shoes_count", "shoes_vintage"),
            ("가방/잡화", "bag_count", "bag_vintage"),
        ]

        for label, count_field, vintage_field in mapping:
            value_str = form_data.get(count_field)
            if value_str:
                try:
                    value = float(value_str)
                except ValueError:
                    continue
                if value > 0:
                    # 새제품/빈티지 선택 (기본값: 새제품)
                    vintage_selection = form_data.get(vintage_field, "새제품")
                    sub_category = "빈티지" if vintage_selection == "빈티지" else "새제품"
                    
                    clothing_items.append({
                        "category": "의류",
                        "activity_type": label,
                        "value": value,
                        "unit": "개",
                        "sub_category": sub_category,
                    })

        if clothing_items:
            self.all_activities = self.all_activities + clothing_items
        
        # 폼 초기화
        self.clothing_type = ""
        self.clothing_count = 0.0
        self.clothing_is_vintage = False
        
        return rx.redirect("/input/electricity")
    
    # ------------------------------ 전기 관련 메서드 ------------------------------
    
    # 전기 입력 상태
    electricity_type: str = ""
    electricity_hours: float = 0.0
    
    def handle_electricity_submit(self, form_data: dict):
        """전기 입력값 제출 처리"""
        # 기존 전기 데이터 제거
        self.all_activities = [
            act for act in self.all_activities
            if act.get("category") != "전기"
        ]

        electricity_items = []

        # 냉방기 / 난방기를 한 번에 입력
        cooling = form_data.get("cooling_hours")
        heating = form_data.get("heating_hours")

        if cooling:
            try:
                v = float(cooling)
                if v > 0:
                    electricity_items.append({
                        "category": "전기",
                        "activity_type": "냉방기",
                        "value": v,
                        "unit": "시간",
                    })
            except ValueError:
                pass

        if heating:
            try:
                v = float(heating)
                if v > 0:
                    electricity_items.append({
                        "category": "전기",
                        "activity_type": "난방기",
                        "value": v,
                        "unit": "시간",
                    })
            except ValueError:
                pass

        if electricity_items:
            self.all_activities = self.all_activities + electricity_items
        
        # 폼 초기화
        self.electricity_type = ""
        self.electricity_hours = 0.0
        
        return rx.redirect("/input/waste")
    
    # ------------------------------ 쓰레기 관련 메서드 ------------------------------
    
    # 쓰레기 입력 상태
    waste_type: str = ""
    waste_amount: float = 0.0
    waste_unit: str = "kg"
    
    def handle_waste_submit(self, form_data: dict):
        """쓰레기 입력값 제출 처리"""
        # 기존 쓰레기 데이터 제거
        self.all_activities = [
            act for act in self.all_activities
            if act.get("category") != "쓰레기"
        ]

        waste_items = []

        def add_waste(label: str, amount_key: str, unit_key: str):
            value_str = form_data.get(amount_key)
            if not value_str:
                return
            try:
                value = float(value_str)
            except ValueError:
                return
            if value <= 0:
                return
            unit = form_data.get(unit_key, "kg")
            waste_items.append({
                "category": "쓰레기",
                "activity_type": label,
                "value": value,
                "unit": unit,
            })

        add_waste("일반", "waste_general_amount", "waste_general_unit")
        add_waste("플라스틱", "waste_plastic_amount", "waste_plastic_unit")
        add_waste("종이", "waste_paper_amount", "waste_paper_unit")
        add_waste("유리", "waste_glass_amount", "waste_glass_unit")
        add_waste("캔", "waste_can_amount", "waste_can_unit")

        if waste_items:
            self.all_activities = self.all_activities + waste_items
        
        # 폼 초기화
        self.waste_type = ""
        self.waste_amount = 0.0
        self.waste_unit = "kg"
        
        return rx.redirect("/input/water")
    
    # ------------------------------ 물 관련 메서드 ------------------------------
    
    # 물 입력 상태
    water_type: str = ""
    water_amount: float = 0.0
    water_unit: str = "회"
    
    async def handle_water_submit(self, form_data: dict):
        """물 입력값 제출 처리"""
        # 기존 물 데이터 제거
        self.all_activities = [
            act for act in self.all_activities
            if act.get("category") != "물"
        ]

        water_items = []

        def add_water(label: str, count_key: str, unit_key: str):
            value_str = form_data.get(count_key)
            if not value_str:
                return
            try:
                value = float(value_str)
            except ValueError:
                return
            if value <= 0:
                return
            unit = form_data.get(unit_key, "회")
            water_items.append({
                "category": "물",
                "activity_type": label,
                "value": value,
                "unit": unit,
            })

        add_water("샤워", "water_shower_count", "water_shower_unit")
        add_water("설거지", "water_dish_count", "water_dish_unit")
        add_water("세탁", "water_laundry_count", "water_laundry_unit")

        if water_items:
            self.all_activities = self.all_activities + water_items
        
        # 폼 초기화
        self.water_type = ""
        self.water_amount = 0.0
        self.water_unit = "회"
        
        # 리포트로 이동하기 전에 자동으로 계산 수행
        await self.calculate_report()
        
        return rx.redirect("/report")
    
    # ------------------------------ 리포트 계산 메서드 ------------------------------
    
    async def calculate_report(self):
        """리포트 페이지에서 전체 탄소 배출량을 계산합니다."""
        logger.info("[리포트 계산] 시작 - 전체 활동 데이터 계산 중...")
        
        try:
            from ..service.carbon_calculator import calculate_carbon_emission
            
            total_emission = 0.0
            calculation_details = []  # 상세 계산 내역 저장
            
            logger.info(f"[리포트 계산] 총 {len(self.all_activities)}개의 활동 데이터 처리 시작")
            
            for idx, activity in enumerate(self.all_activities):
                category = activity.get("category", "")
                activity_type = activity.get("activity_type", "")
                value = activity.get("value", 0)
                unit = activity.get("unit", "")
                sub_category = activity.get("sub_category") or activity.get("subcategory") or activity.get("is_vintage")
                
                logger.info(f"[리포트 계산] [{idx+1}/{len(self.all_activities)}] 처리 중 - 카테고리: {category}, 활동: {activity_type}, 값: {value}{unit}")
                
                # 탄소 배출량 계산
                result = calculate_carbon_emission(
                    category=category,
                    activity_type=activity_type,
                    value=value,
                    unit=unit,
                    sub_category=sub_category
                )
                
                emission = result.get("carbon_emission_kg", 0.0)
                method = result.get("calculation_method", "local")
                total_emission += emission
                
                detail = {
                    "category": category,
                    "activity_type": activity_type,
                    "value": value,
                    "unit": unit,
                    "emission": emission,
                    "method": method
                }
                
                # 의류의 경우 새제품/빈티지 정보 추가
                if category == "의류" and sub_category:
                    detail["sub_category"] = sub_category
                
                calculation_details.append(detail)
                
                logger.info(f"[리포트 계산] ✅ [{idx+1}/{len(self.all_activities)}] 계산 완료: {category}/{activity_type} = {emission}kgCO2e (방법: {method})")
            
            # 결과 저장
            self.total_carbon_emission = round(total_emission, 3)
            self.is_report_calculated = True
            self.calculation_details = calculation_details  # 상세 내역 저장
            
            logger.info(f"[리포트 계산] ✅ 전체 계산 완료! 총 배출량: {self.total_carbon_emission}kgCO2e")
            logger.info(f"[리포트 계산] 계산 상세 내역: {calculation_details}")
            
            # 절약량 계산 (자전거/걷기 사용 시)
            await self._calculate_savings()
            
            # 포인트 계산 (리포트 표시용)
            await self._calculate_points_for_report()
            
            # 카테고리별 배출량 집계
            await self._calculate_category_breakdown()
            
        except Exception as e:
            logger.error(f"[리포트 계산] ❌ 계산 오류 발생: {e}", exc_info=True)
            self.total_carbon_emission = 0.0
            self.is_report_calculated = False
    
    # ------------------------------ DB 저장 메서드 ------------------------------
    
    async def _save_carbon_log_to_db_internal(self):
        """탄소 로그 저장 내부 로직 (헬퍼 메서드)"""
        # 가장 먼저 로그 출력 (메서드 호출 확인)
        print(f"[저장] 메서드 호출됨! 사용자: {self.current_user_id}, 로그인: {self.is_logged_in}")
        logger.info(f"[저장 시작] ========== 저장 프로세스 시작 ==========")
        logger.info(f"[저장 시작] 사용자: {self.current_user_id}, 로그인 상태: {self.is_logged_in}")
        
        if not self.is_logged_in or not self.current_user_id:
            self.save_message = "로그인이 필요합니다."
            logger.error("[저장 실패] 로그인되지 않음")
            print("[저장 실패] 로그인되지 않음")
            return
        
        self.is_saving = True
        self.save_message = ""
        print(f"[저장] is_saving 설정 완료, all_activities 개수: {len(self.all_activities)}")
        
        try:
            logger.info(f"[저장] all_activities 개수: {len(self.all_activities)}")
            logger.info(f"[저장] all_activities 내용: {self.all_activities}")
            print(f"[저장] all_activities: {self.all_activities}")
            import json
            from ..service.carbon_calculator import calculate_carbon_emission
            
            # 전체 탄소 배출량 계산 (이미 계산된 값이 있으면 사용)
            if not self.is_report_calculated or self.total_carbon_emission == 0.0:
                total_emission = 0.0
                for activity in self.all_activities:
                    category = activity.get("category")
                    activity_type = activity.get("activity_type")
                    value = activity.get("value", 0)
                    unit = activity.get("unit", "")
                    sub_category = activity.get("sub_category") or activity.get("subcategory") or activity.get("is_vintage")
                    
                    result = calculate_carbon_emission(
                        category=category,
                        activity_type=activity_type,
                        value=value,
                        unit=unit,
                        sub_category=sub_category
                    )
                    emission = result.get("carbon_emission_kg", 0.0)
                    total_emission += emission
            else:
                total_emission = self.total_carbon_emission
            
            # 간단한 통계 수집 (기존 호환성 유지)
            transport_km = 0.0
            ac_hours = 0.0
            cup_count = 0
            
            for activity in self.all_activities:
                category = activity.get("category")
                activity_type = activity.get("activity_type")
                value = activity.get("value", 0)
                unit = activity.get("unit", "")
                
                if category == "교통":
                    if unit == "km":
                        transport_km += value
                    elif unit == "분":
                        if activity_type == "자동차":
                            transport_km += value * 30 / 60
                        elif activity_type == "버스":
                            transport_km += value * 25 / 60
                        elif activity_type == "지하철":
                            transport_km += value * 30 / 60
                elif category == "전기":
                    if activity_type == "냉방기":
                        ac_hours += value
                elif category == "쓰레기":
                    if activity_type == "일회용컵":
                        cup_count += int(value)
            
            # all_activities를 JSON으로 변환
            activities_json = json.dumps(self.all_activities, ensure_ascii=False, default=str)
            
            # 오늘 날짜의 기존 로그 확인 (SQLModel Session 사용)
            from sqlmodel import Session, create_engine, select
            import os
            
            db_path = os.path.join(os.getcwd(), "reflex.db")
            db_url = f"sqlite:///{db_path}"
            engine = create_engine(db_url, echo=False)
            
            today = date.today()
            
            # 절약량이 계산되지 않았으면 계산
            print(f"[저장] 절약량 계산 전: hasattr={hasattr(self, 'total_saved_emission')}, 값={getattr(self, 'total_saved_emission', 'N/A')}")
            if not hasattr(self, 'total_saved_emission') or self.total_saved_emission == 0.0:
                logger.info("[저장] 절약량 계산 시작...")
                print("[저장] 절약량 계산 시작...")
                await self._calculate_savings()
                print(f"[저장] 절약량 계산 완료: {self.total_saved_emission}kg")
            
            # 리포트가 계산되지 않았으면 계산
            print(f"[저장] 리포트 계산 전: is_report_calculated={self.is_report_calculated}")
            if not self.is_report_calculated:
                logger.info("[저장] 리포트 계산 시작...")
                print("[저장] 리포트 계산 시작...")
                await self.calculate_report()
                print(f"[저장] 리포트 계산 완료: total_emission={self.total_carbon_emission}kg")
            
            logger.info(f"[저장] 절약량: {self.total_saved_emission}kg, 절약 금액: {self.saved_money}원")
            print(f"[저장] 절약량: {self.total_saved_emission}kg, 절약 금액: {self.saved_money}원")
            
            with Session(engine) as session:
                stmt = select(CarbonLog).where(
                    CarbonLog.student_id == self.current_user_id,
                    CarbonLog.log_date == today
                )
                existing_log = session.exec(stmt).first()
                is_new_log = existing_log is None
                # 오늘 날짜 로그 존재 여부 상태 반영
                self.has_today_log = not is_new_log
            logger.info(f"[저장] 기존 로그 존재 여부: {not is_new_log}")
            print(f"[저장] 기존 로그 존재 여부: {not is_new_log}, is_new_log={is_new_log}")
            
            # 테스트용: 같은 날에 여러 번 저장 가능 (제한 제거)
            
            print(f"[저장] DB 저장 시작 - total_emission={total_emission}kg")
            
            # 포인트 계산 (한 번만 계산)
            points_earned = await self._calculate_points(total_emission)
            logger.info(f"[저장] 계산된 포인트: {points_earned}점")
            
            with Session(engine) as session:
                # 사용자 조회
                user_stmt = select(User).where(User.student_id == self.current_user_id)
                user = session.exec(user_stmt).first()
                
                if not user:
                    self.save_message = "❌ 사용자 정보를 찾을 수 없습니다."
                    self.is_save_success = False
                    logger.error(f"탄소 로그 저장 오류: 사용자 {self.current_user_id}를 찾을 수 없음")
                    return
                
                # 오늘 로그 조회 (같은 세션에서)
                log_stmt = select(CarbonLog).where(
                    CarbonLog.student_id == self.current_user_id,
                    CarbonLog.log_date == today
                )
                log = session.exec(log_stmt).first()
                
                # 기존 포인트 저장 (로그 업데이트 전)
                old_points = log.points_earned if log and log.points_earned else 0
                logger.info(f"[저장] 기존 포인트: {old_points}점, 새 포인트: {points_earned}점")
                
                # 로그 생성 또는 업데이트
                if log:
                    logger.info(f"[저장] 기존 로그 업데이트 (기존 포인트: {log.points_earned})")
                    log.transport_km = transport_km
                    log.ac_hours = ac_hours
                    log.cup_count = cup_count
                    log.total_emission = total_emission
                    log.activities_json = activities_json
                    log.points_earned = points_earned
                else:
                    log = CarbonLog(
                        student_id=self.current_user_id,
                        log_date=today,
                        transport_km=transport_km,
                        ac_hours=ac_hours,
                        cup_count=cup_count,
                        total_emission=total_emission,
                        activities_json=activities_json,
                        points_earned=points_earned
                    )
                    logger.info("[저장] 새 로그 생성")
                
                session.add(log)
                
                # 사용자 포인트 업데이트 (같은 세션에서)
                if is_new_log:
                    # 새로운 로그: 포인트 추가
                    user.current_points += points_earned
                    logger.info(f"[저장] 새 로그 - 포인트 추가: {user.current_points - points_earned} + {points_earned} = {user.current_points}")
                else:
                    # 기존 로그 업데이트: 기존 포인트를 빼고 새 포인트 추가
                    user.current_points = user.current_points - old_points + points_earned
                    logger.info(f"[저장] 기존 로그 업데이트 - 포인트 조정: {user.current_points + old_points - points_earned} - {old_points} + {points_earned} = {user.current_points}")
                
                self.current_user_points = user.current_points
                session.add(user)
                
                # 한 번에 commit
                session.commit()
                session.refresh(log)
                session.refresh(user)
                
                logger.info(f"[저장 완료] 사용자: {self.current_user_id}, 배출량: {total_emission}kg, 절약량: {self.total_saved_emission}kg, 포인트: {points_earned}점 (총 포인트: {user.current_points})")
                logger.info(f"[저장 완료] DB 확인 - 사용자 포인트: {user.current_points}점, 로그 포인트: {log.points_earned}점")
                
                if points_earned > 0:
                    # 포인트 획득 이유 메시지 생성
                    reasons = []
                    if self.total_saved_emission > 0:
                        reasons.append(f"절약량 {self.total_saved_emission}kg")
                    # 빈티지 제품 사용 확인
                    vintage_count = sum(int(act.get("value", 0)) for act in self.all_activities 
                                      if act.get("category") == "의류" 
                                      and act.get("sub_category") == "빈티지")
                    if vintage_count > 0:
                        reasons.append(f"빈티지 제품 {vintage_count}개")
                    # 평균보다 낮은 배출량 확인
                    from ..service.average_data import get_total_average
                    avg_emission = get_total_average()
                    if total_emission < avg_emission:
                        diff = avg_emission - total_emission
                        reasons.append(f"평균보다 {diff:.1f}kg 낮음")
                    
                    reason_text = ", ".join(reasons) if reasons else "환경 친화적 활동"
                    self.save_message = f"✅ 저장 완료! {reason_text}으로 {points_earned}점을 획득했습니다."
                else:
                    self.save_message = "✅ 저장 완료!"
                
                self.is_save_success = True
                self.has_today_log = True  # 저장 완료 후 오늘 날짜 로그 존재 표시
            
            self.is_saving = False
            
            # 저장 성공 시 마이페이지 데이터 새로고침 (포인트 로그 업데이트)
            if self.is_save_success:
                try:
                    # 주간 챌린지 진행도 업데이트는 ChallengeState에서 오버라이드된 save_carbon_log_to_db에서 처리됨

                    # 사용자 포인트 정보 새로고침
                    with Session(engine) as session:
                        user_stmt = select(User).where(User.student_id == self.current_user_id)
                        user = session.exec(user_stmt).first()
                        if user:
                            self.current_user_points = user.current_points
                            logger.info(f"[저장] 사용자 포인트 새로고침: {self.current_user_points}점")
                    
                    # ChallengeState의 load_mypage_data 호출하여 포인트 로그 등 새로고침
                    # AppState는 ChallengeState이므로 self를 통해 호출 가능
                    if hasattr(self, 'load_mypage_data'):
                        await self.load_mypage_data()
                        logger.info("[저장] 마이페이지 데이터 새로고침 완료")
                    else:
                        # load_mypage_data가 없으면 포인트 로그만 직접 로드
                        if hasattr(self, 'load_points_log'):
                            await self.load_points_log()
                            logger.info("[저장] 포인트 로그 새로고침 완료")
                except Exception as refresh_error:
                    logger.warning(f"[저장] 마이페이지 데이터 새로고침 실패 (무시): {refresh_error}")
            
        except Exception as e:
            self.save_message = f"❌ 저장 중 오류가 발생했습니다: {str(e)}"
            self.is_save_success = False
            self.is_saving = False
            logger.error(f"[저장 오류] 탄소 로그 저장 실패: {e}", exc_info=True)
            logger.error(f"[저장 오류] 사용자: {self.current_user_id}, 활동 수: {len(self.all_activities)}")
            print(f"[저장 오류] 예외 발생: {e}")
            import traceback
            print(f"[저장 오류] 스택 트레이스:\n{traceback.format_exc()}")
    
    async def save_carbon_log_to_db(self):
        """현재 입력된 탄소 배출량을 데이터베이스에 저장"""
        await self._save_carbon_log_to_db_internal()
    
    async def load_saved_logs_history(self):
        """저장된 로그 이력을 불러옵니다."""
        self.saved_logs_history = await self.get_saved_logs_history(limit=10)
    
    async def load_saved_activities(self):
        """저장된 입력 데이터를 불러옵니다. 오늘 날짜의 데이터를 불러옵니다."""
        if not self.is_logged_in or not self.current_user_id:
            return
        
        try:
            target_date = date.today()
            
            logs = await CarbonLog.find(
                CarbonLog.student_id == self.current_user_id,
                CarbonLog.log_date == target_date
            )
            
            if logs:
                log = logs[0]
                activities = log.get_activities()
                if activities:
                    self.all_activities = activities
                    # 저장된 데이터가 있으면 자동으로 계산 수행
                    await self.calculate_report()
                    logger.info(f"저장된 데이터 불러오기 완료: {self.current_user_id}, 날짜: {target_date}, 활동 수: {len(activities)}")
                else:
                    logger.info(f"저장된 데이터가 없습니다: {self.current_user_id}, 날짜: {target_date}")
            else:
                logger.info(f"저장된 로그가 없습니다: {self.current_user_id}, 날짜: {target_date}")
                
        except Exception as e:
            logger.error(f"저장된 데이터 불러오기 오류: {e}", exc_info=True)
    
    async def get_saved_logs_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """저장된 로그 이력을 반환합니다."""
        if not self.is_logged_in or not self.current_user_id:
            return []
        
        try:
            logs = await CarbonLog.find(
                CarbonLog.student_id == self.current_user_id
            )
            
            # 날짜순으로 정렬 (최신순)
            logs.sort(key=lambda x: x.log_date, reverse=True)
            
            result = []
            for log in logs[:limit]:
                result.append({
                    "log_date": log.log_date,
                    "total_emission": log.total_emission,
                    "activities_count": len(log.get_activities()),
                    "created_at": log.created_at
                })
            
            return result
            
        except Exception as e:
            logger.error(f"로그 이력 조회 오류: {e}", exc_info=True)
            return []
    
    async def get_carbon_statistics(self) -> Dict[str, Any]:
        """탄소 배출량 통계 데이터 반환"""
        if not self.is_logged_in or not self.current_user_id:
            return {
                "total_logs": 0,
                "total_emission": 0.0,
                "average_daily_emission": 0.0,
                "total_activities": 0,
                "category_breakdown": []
            }
        
        try:
            from ..models import CarbonLog
            from sqlmodel import Session, create_engine, select
            import os
            
            # SQLModel Session을 직접 사용하여 조회
            db_path = os.path.join(os.getcwd(), "reflex.db")
            db_url = f"sqlite:///{db_path}"
            engine = create_engine(db_url, echo=False)
            
            logs = []
            with Session(engine) as session:
                statement = select(CarbonLog).where(CarbonLog.student_id == self.current_user_id)
                logs = list(session.exec(statement).all())
            
            if not logs:
                return {
                    "total_logs": 0,
                    "total_emission": 0.0,
                    "average_daily_emission": 0.0,
                    "total_activities": 0,
                    "category_breakdown": []
                }
            
            # 통계 계산
            total_logs = len(logs)
            total_emission = sum(log.total_emission for log in logs)
            average_daily_emission = total_emission / total_logs if total_logs > 0 else 0.0
            
            # 카테고리별 통계
            category_breakdown = {}
            total_activities = 0
            
            for log in logs:
                activities = log.get_activities()
                total_activities += len(activities)
                
                for activity in activities:
                    # activity가 딕셔너리인지 확인
                    if not isinstance(activity, dict):
                        logger.warning(f"활동 데이터가 딕셔너리가 아닙니다: {type(activity)}, 값: {activity}")
                        continue
                    
                    category = activity.get("category", "기타")
                    if category not in category_breakdown:
                        category_breakdown[category] = 0
                    category_breakdown[category] += 1
            
            # Dict를 리스트로 변환하고 비율 계산 (Reflex foreach에서 사용하기 위해)
            category_list = []
            for k, v in category_breakdown.items():
                percent = (v / total_activities * 100) if total_activities > 0 else 0
                category_list.append({
                    "name": k,
                    "count": v,
                    "percent": round(percent, 1)
                })
            
            return {
                "total_logs": total_logs,
                "total_emission": round(total_emission, 2),
                "average_daily_emission": round(average_daily_emission, 2),
                "total_activities": total_activities,
                "category_breakdown": category_list
            }
            
        except Exception as e:
            logger.error(f"탄소 통계 조회 오류: {e}", exc_info=True)
            return {
                "total_logs": 0,
                "total_emission": 0.0,
                "average_daily_emission": 0.0,
                "total_activities": 0,
                "category_breakdown": []
            }
    
    # 리포트용 카테고리별 배출량 및 AI 분석
    category_emission_breakdown: Dict[str, float] = {}
    average_comparison: Dict[str, Dict[str, float]] = {}
    average_comparison_list: List[Dict[str, Any]] = []  # foreach에서 사용하기 위한 리스트 형태 (사용 안 함)
    total_average_comparison: Dict[str, Any] = {}  # 총 평균 비교만 사용
    category_emission_list: List[Dict[str, Any]] = []  # foreach에서 사용하기 위한 리스트 형태
    donut_chart_svg: str = ""  # 도넛 차트 SVG 문자열
    ai_analysis_result: str = ""
    ai_suggestions: List[str] = []
    ai_alternatives: List[Dict[str, Any]] = []
    is_loading_ai: bool = False
    
    async def _calculate_savings(self):
        """자전거/걷기 사용 시 절약한 탄소 배출량 계산"""
        try:
            from ..service.carbon_calculator import convert_to_standard_unit, EMISSION_FACTORS
            
            total_saved = 0.0
            savings_list = []
            
            # 버스 배출 계수 (kgCO2/km)
            BUS_EMISSION_FACTOR = EMISSION_FACTORS.get("교통", {}).get("버스", 0.089)
            # 탄소 가격 (원/kgCO2)
            CARBON_PRICE_PER_KG = 100.0  # 1kg CO2 = 100원
            
            logger.info(f"[절약량 계산] 시작 - 활동 수: {len(self.all_activities)}")
            
            # 교통 활동 중 자전거/걷기 사용한 경우 찾기
            for activity in self.all_activities:
                if not isinstance(activity, dict):
                    continue
                    
                if activity.get("category") != "교통":
                    continue
                
                activity_type = activity.get("activity_type", "")
                if activity_type not in ["자전거", "걷기"]:
                    continue
                
                value = activity.get("value", 0)
                unit = activity.get("unit", "km")
                
                logger.info(f"[절약량 계산] {activity_type} 발견 - 값: {value}{unit}")
                
                # 거리로 변환
                distance_km, _ = convert_to_standard_unit(
                    category="교통",
                    activity_type=activity_type,
                    value=value,
                    unit=unit,
                    sub_category=None
                )
                
                if distance_km <= 0:
                    logger.warning(f"[절약량 계산] {activity_type} 거리가 0 이하: {distance_km}km")
                    continue
                
                # 같은 거리를 버스로 갔을 때의 배출량 계산
                bus_emission = distance_km * BUS_EMISSION_FACTOR
                # 실제 배출량은 0 (자전거/걷기는 배출 없음)
                saved_emission = bus_emission
                saved_money = saved_emission * CARBON_PRICE_PER_KG
                
                total_saved += saved_emission
                
                savings_list.append({
                    "activity_type": activity_type,
                    "distance_km": round(distance_km, 2),
                    "saved_emission": round(saved_emission, 3),
                    "saved_money": round(saved_money, 2),
                    "alternative": "버스"
                })
                
                logger.info(f"[절약량 계산] {activity_type} {distance_km}km → 절약: {saved_emission}kgCO2e ({saved_money}원)")
            
            self.total_saved_emission = round(total_saved, 3)
            self.saved_money = round(total_saved * CARBON_PRICE_PER_KG, 2)
            self.savings_details = savings_list
            
            logger.info(f"[절약량 계산] ✅ 총 절약량: {self.total_saved_emission}kgCO2e, 절약 금액: {self.saved_money}원, 상세: {len(savings_list)}개")
            
        except Exception as e:
            logger.error(f"[절약량 계산] 오류: {e}", exc_info=True)
            self.total_saved_emission = 0.0
            self.saved_money = 0.0
            self.savings_details = []
    
    async def _calculate_points_for_report(self):
        """리포트 표시용 포인트 계산 (상세 내역 포함)"""
        try:
            from ..service.average_data import get_total_average
            
            total_emission = self.total_carbon_emission
            total_points = 0
            points_breakdown = {
                "절약량": 0,
                "빈티지": 0,
                "평균 대비": 0
            }
            
            # 1. 절약량 기반 포인트 (자전거/걷기 사용 시)
            savings_points = int(self.saved_money) if hasattr(self, 'saved_money') else 0
            total_points += savings_points
            points_breakdown["절약량"] = savings_points
            
            # 2. 빈티지 제품 사용 포인트
            vintage_count = 0
            for activity in self.all_activities:
                category = activity.get("category")
                sub_category = activity.get("sub_category") or activity.get("subcategory")
                if category == "의류" and sub_category == "빈티지":
                    vintage_count += int(activity.get("value", 0))
            
            vintage_points = vintage_count * 10
            total_points += vintage_points
            points_breakdown["빈티지"] = vintage_points
            
            # 3. 평균보다 낮은 배출량 포인트
            avg_emission = get_total_average()  # 14.5 kgCO₂e/일
            if total_emission < avg_emission:
                diff = avg_emission - total_emission
                emission_points = min(int(diff * 20), 100)
                total_points += emission_points
                points_breakdown["평균 대비"] = emission_points
            
            self.points_breakdown = points_breakdown
            self.total_points_earned = total_points
            
            logger.info(f"[리포트 포인트 계산] 총 포인트: {total_points}점 (절약량: {savings_points}점, 빈티지: {vintage_points}점, 평균 대비: {points_breakdown['평균 대비']}점)")
            
        except Exception as e:
            logger.error(f"[리포트 포인트 계산] 오류: {e}", exc_info=True)
            self.points_breakdown = {"절약량": 0, "빈티지": 0, "평균 대비": 0}
            self.total_points_earned = 0
    
    async def _calculate_points(self, total_emission: float) -> int:
        """
        포인트 계산: 절약량 + 빈티지 제품 + 평균보다 낮은 배출량
        
        Args:
            total_emission: 총 탄소 배출량 (kgCO₂e)
        
        Returns:
            획득한 포인트 (점)
        """
        try:
            from ..service.average_data import get_total_average
            
            total_points = 0
            
            # 1. 절약량 기반 포인트 (자전거/걷기 사용 시)
            # 절약한 금액(원) = 포인트
            savings_points = int(self.saved_money) if hasattr(self, 'saved_money') else 0
            total_points += savings_points
            logger.info(f"[포인트 계산] 절약량 포인트: {savings_points}점 (절약량: {self.total_saved_emission}kg)")
            
            # 2. 빈티지 제품 사용 포인트
            vintage_count = 0
            logger.info(f"[포인트 계산] all_activities 개수: {len(self.all_activities)}")
            for activity in self.all_activities:
                category = activity.get("category")
                sub_category = activity.get("sub_category") or activity.get("subcategory")
                value = activity.get("value", 0)
                logger.info(f"[포인트 계산] 활동 확인: category={category}, sub_category={sub_category}, value={value}")
                if category == "의류" and sub_category == "빈티지":
                    vintage_count += int(value)
                    logger.info(f"[포인트 계산] 빈티지 제품 발견! {activity.get('activity_type')} {value}개")
            
            # 빈티지 제품 1개당 10점
            vintage_points = vintage_count * 10
            total_points += vintage_points
            logger.info(f"[포인트 계산] 빈티지 제품 포인트: {vintage_points}점 (빈티지 제품: {vintage_count}개)")
            
            # 3. 평균보다 낮은 배출량 포인트
            avg_emission = get_total_average()  # 14.5 kgCO₂e/일
            if total_emission < avg_emission:
                # 평균보다 낮은 배출량 1kg당 20점 (최대 100점)
                diff = avg_emission - total_emission
                emission_points = min(int(diff * 20), 100)
                total_points += emission_points
                logger.info(f"[포인트 계산] 평균 대비 낮은 배출량 포인트: {emission_points}점 (차이: {diff:.2f}kg)")
            else:
                logger.info(f"[포인트 계산] 평균보다 높은 배출량 (평균: {avg_emission}kg, 내 배출량: {total_emission}kg)")
            
            logger.info(f"[포인트 계산] 총 포인트: {total_points}점 (절약량: {savings_points}점, 빈티지: {vintage_points}점, 배출량: {total_points - savings_points - vintage_points}점)")
            return total_points
            
        except Exception as e:
            logger.error(f"[포인트 계산] 오류: {e}", exc_info=True)
            # 오류 시 절약량 포인트만 지급
            return int(self.saved_money) if hasattr(self, 'saved_money') else 0
    
    async def _calculate_category_breakdown(self):
        """카테고리별 배출량 집계 (총 평균만 비교)"""
        try:
            from ..service.average_data import get_total_average
            
            # 카테고리별 배출량 집계
            category_emission = {}
            for detail in self.calculation_details:
                category = detail.get("category", "기타")
                emission = detail.get("emission", 0.0)
                if category not in category_emission:
                    category_emission[category] = 0.0
                category_emission[category] += emission
            
            self.category_emission_breakdown = category_emission
            
            # 총 평균만 비교
            total_average = get_total_average()
            total_user_emission = self.total_carbon_emission
            difference = total_user_emission - total_average
            
            self.total_average_comparison = {
                "user": round(total_user_emission, 2),
                "average": round(total_average, 2),
                "difference": round(difference, 2),
                "abs_difference": round(abs(difference), 2),  # 절댓값 미리 계산
                "percentage": round((difference / total_average * 100), 1) if total_average > 0 else 0,
                "is_better": difference < 0
            }
            
            # 카테고리별 평균 비교는 제거
            self.average_comparison = {}
            self.average_comparison_list = []
            
            # 카테고리별 배출량도 리스트로 변환 (비율도 미리 계산, 도넛 차트용)
            total = self.total_carbon_emission if self.total_carbon_emission > 0 else 1
            category_list = []
            cumulative_percentage = 0
            
            # 색상 매핑
            color_map = {
                "교통": "#3b82f6",
                "식품": "#10b981",
                "전기": "#f59e0b",
                "물": "#06b6d4",
                "의류": "#8b5cf6",
                "쓰레기": "#ef4444"
            }
            
            for category, emission in category_emission.items():
                percentage = (emission / total) * 100 if total > 0 else 0
                category_list.append({
                    "category": category,
                    "emission": round(emission, 2),
                    "percentage": round(percentage, 1),
                    "progress_value": percentage,
                    "color": color_map.get(category, "#6b7280"),
                    "cumulative_percentage": cumulative_percentage,
                    "stroke_dasharray": f"{2 * 3.14159 * 80 * (percentage / 100)} {2 * 3.14159 * 80}",
                    "stroke_dashoffset": cumulative_percentage * 2 * 3.14159 * 80 / 100,
                    "rotation": -90 + cumulative_percentage * 360 / 100
                })
                cumulative_percentage += percentage
            
            self.category_emission_list = category_list
            
            # 도넛 차트 SVG 생성
            self._generate_donut_chart_svg()
            
            logger.info(f"카테고리별 배출량 집계 완료: {category_emission}")
            
        except Exception as e:
            logger.error(f"카테고리별 배출량 집계 오류: {e}", exc_info=True)
            self.category_emission_breakdown = {}
            self.average_comparison = {}
            self.average_comparison_list = []
            self.total_average_comparison = {}
            self.category_emission_list = []
            self.donut_chart_svg = ""
    
    def _generate_donut_chart_svg(self):
        """도넛 차트 SVG 문자열 생성"""
        try:
            if not self.category_emission_list or self.total_carbon_emission <= 0:
                self.donut_chart_svg = ""
                return
            
            svg_parts = []
            svg_parts.append('<svg width="200" height="200" viewBox="0 0 200 200">')
            svg_parts.append('<circle cx="100" cy="100" r="80" fill="none" stroke="#e5e7eb" stroke-width="20"/>')
            
            cumulative_percentage = 0
            for item in self.category_emission_list:
                percentage = item["percentage"]
                if percentage > 0:
                    circumference = 2 * 3.14159 * 80
                    dash_length = circumference * (percentage / 100)
                    dash_offset = circumference * (cumulative_percentage / 100)
                    rotation = -90 + (cumulative_percentage * 360 / 100)
                    
                    svg_parts.append(
                        f'<circle cx="100" cy="100" r="80" fill="none" stroke="{item["color"]}" '
                        f'stroke-width="20" stroke-dasharray="{dash_length} {circumference}" '
                        f'stroke-dashoffset="{dash_offset}" transform="rotate({rotation} 100 100)"/>'
                    )
                    cumulative_percentage += percentage
            
            # 중앙 텍스트
            svg_parts.append('<text x="100" y="95" text-anchor="middle" font-size="14" font-weight="bold" fill="#374151">총 배출량</text>')
            svg_parts.append(f'<text x="100" y="115" text-anchor="middle" font-size="18" font-weight="bold" fill="#1e40af">{self.total_carbon_emission:.2f}kg</text>')
            svg_parts.append('</svg>')
            
            self.donut_chart_svg = ''.join(svg_parts)
            logger.info("도넛 차트 SVG 생성 완료")
            
        except Exception as e:
            logger.error(f"도넛 차트 SVG 생성 오류: {e}", exc_info=True)
            self.donut_chart_svg = ""
    
    async def generate_ai_analysis(self):
        """AI 분석 결과 생성"""
        if not self.is_report_calculated:
            return
        
        self.is_loading_ai = True
        self.ai_analysis_result = ""
        self.ai_suggestions = []
        self.ai_alternatives = []
        
        try:
            from ..service.ai_coach import generate_coaching_message
            from ..service.models import AICoachRequest
            
            # AI 코칭 요청 생성
            request = AICoachRequest(
                total_carbon=self.total_carbon_emission,
                category_breakdown=self.category_emission_breakdown,
                activities=self.all_activities
            )
            
            # AI 분석 결과 생성
            response = generate_coaching_message(request)
            
            self.ai_analysis_result = response.analysis
            self.ai_suggestions = response.suggestions
            self.ai_alternatives = response.alternative_actions 
            
            logger.info(f"AI 분석 결과 생성 완료")
            
        except Exception as e:
            logger.error(f"AI 분석 결과 생성 오류: {e}", exc_info=True)
            self.ai_analysis_result = "AI 분석을 불러오는 중 오류가 발생했습니다."
            self.ai_suggestions = []
            self.ai_alternatives = []
        finally:
            self.is_loading_ai = False
