"""
탄소 배출량 입력 및 저장 관련 State
"""

import reflex as rx
from typing import Dict, List, Any, Optional
from datetime import date, datetime
import logging
from sqlalchemy import text
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
    
    # 정책/혜택 후보 (LLM은 이 목록 안에서만 선택)
    policy_candidates: List[Dict[str, str]] = []
    
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

    # 2단계 입력 모드 추가
    food_step: int = 0  # 0: 카테고리 선택, 1: 세부 카테고리 선택, 2: 횟수 입력

    # 선택된 세부 카테고리 저장
    selected_dairy_subs: List[str] = []
    selected_rice_subs: List[str] = []
    selected_coffee_subs: List[str] = []
    selected_fastfood_subs: List[str] = []
    selected_noodles_subs: List[str] = []
    selected_cooked_subs: List[str] = []
    selected_side_dish_subs: List[str] = []
    selected_grilled_meat_subs: List[str] = []
    selected_fruit_subs: List[str] = []
    selected_pasta_subs: List[str] = []

    # ---------- 의류 선택 상태 ----------
    selected_tshirts: bool = False
    selected_jeans: bool = False
    selected_shoes: bool = False
    selected_acc: bool = False

    show_tshirts: bool = False
    show_jeans: bool = False
    show_shoes: bool = False
    show_acc: bool = False

    clothing_input_mode: bool = False

    # ---------- 전기 선택 상태 ----------
    selected_ac: bool = False       # 냉방기
    selected_heater: bool = False   # 난방기

    show_ac: bool = False
    show_heater: bool = False

    electricity_input_mode: bool = False

    # ---------- 쓰레기 선택 상태 ----------
    selected_general: bool = False
    selected_plastic: bool = False
    selected_paper: bool = False
    selected_glass: bool = False
    selected_can: bool = False

    show_general: bool = False
    show_plastic: bool = False
    show_paper: bool = False
    show_glass: bool = False
    show_can: bool = False

    waste_input_mode: bool = False

    # ---------- 물 선택 상태 ----------
    selected_shower: bool = False
    selected_dish: bool = False
    selected_laundry: bool = False

    show_shower: bool = False
    show_dish: bool = False
    show_laundry: bool = False

    water_input_mode: bool = False
    
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

    def reset_transport_selection(self):
        """다시 선택하기: 모든 선택 초기화하고 카테고리 선택 단계로 돌아가기"""
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
    
    async def handle_transport_submit(self, form_data: dict):
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
        
        yield rx.redirect("/input/food")
    
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
        """선택된 음식 항목들의 입력 필드를 표시 (1단계: 세부 카테고리 선택)"""
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
        self.food_step = 1  # 세부 카테고리 선택 단계로 이동

    def toggle_food_subcategory(self, category: str, subcategory: str):
        """세부 카테고리 토글 (체크박스 선택/해제)"""
        if category == "유제품":
            if subcategory in self.selected_dairy_subs:
                self.selected_dairy_subs.remove(subcategory)
            else:
                self.selected_dairy_subs.append(subcategory)
        elif category == "밥":
            if subcategory in self.selected_rice_subs:
                self.selected_rice_subs.remove(subcategory)
            else:
                self.selected_rice_subs.append(subcategory)
        elif category == "커피":
            if subcategory in self.selected_coffee_subs:
                self.selected_coffee_subs.remove(subcategory)
            else:
                self.selected_coffee_subs.append(subcategory)
        elif category == "패스트푸드":
            if subcategory in self.selected_fastfood_subs:
                self.selected_fastfood_subs.remove(subcategory)
            else:
                self.selected_fastfood_subs.append(subcategory)
        elif category == "면":
            if subcategory in self.selected_noodles_subs:
                self.selected_noodles_subs.remove(subcategory)
            else:
                self.selected_noodles_subs.append(subcategory)
        elif category == "국/찌개":
            if subcategory in self.selected_cooked_subs:
                self.selected_cooked_subs.remove(subcategory)
            else:
                self.selected_cooked_subs.append(subcategory)
        elif category == "반찬":
            if subcategory in self.selected_side_dish_subs:
                self.selected_side_dish_subs.remove(subcategory)
            else:
                self.selected_side_dish_subs.append(subcategory)
        elif category == "고기":
            if subcategory in self.selected_grilled_meat_subs:
                self.selected_grilled_meat_subs.remove(subcategory)
            else:
                self.selected_grilled_meat_subs.append(subcategory)
        elif category == "과일":
            if subcategory in self.selected_fruit_subs:
                self.selected_fruit_subs.remove(subcategory)
            else:
                self.selected_fruit_subs.append(subcategory)
        elif category == "파스타":
            if subcategory in self.selected_pasta_subs:
                self.selected_pasta_subs.remove(subcategory)
            else:
                self.selected_pasta_subs.append(subcategory)

    def proceed_to_quantity_input(self):
        """세부 카테고리 선택 완료 후 횟수 입력 단계로 이동"""
        self.food_step = 2

    def reset_food_selection(self):
        """다시 선택하기: 모든 선택 초기화하고 카테고리 선택 단계로 돌아가기"""
        self.food_step = 0
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
        self.selected_dairy_subs = []
        self.selected_rice_subs = []
        self.selected_coffee_subs = []
        self.selected_fastfood_subs = []
        self.selected_noodles_subs = []
        self.selected_cooked_subs = []
        self.selected_side_dish_subs = []
        self.selected_grilled_meat_subs = []
        self.selected_fruit_subs = []
        self.selected_pasta_subs = []

    async def handle_food_submit(self, form_data: dict):
        """음식 입력값 제출 처리 (다중 선택 지원)"""
        # 기존 음식 데이터 제거
        self.all_activities = [
            act for act in self.all_activities 
            if act.get("category") != "식품"
        ]
        
        food_data = []

        # 유제품 처리
        if self.show_dairy:
            for dairy_sub in self.selected_dairy_subs:
                value_key = f"dairy_{dairy_sub}_value"
                if form_data.get(value_key):
                    food_data.append({
                        "category": "식품",
                        "activity_type": dairy_sub,
                        "subcategory": "유제품류",
                        "value": float(form_data.get(value_key, 0)),
                        "unit": "회",
                    })

        # 밥 처리
        if self.show_rice:
            for rice_sub in self.selected_rice_subs:
                value_key = f"rice_{rice_sub}_value"
                if form_data.get(value_key):
                    food_data.append({
                        "category": "식품",
                        "activity_type": rice_sub,
                        "subcategory": "쌀밥",
                        "value": float(form_data.get(value_key, 0)),
                        "unit": "회",
                    })

        # 커피 처리
        if self.show_coffee:
            for coffee_sub in self.selected_coffee_subs:
                value_key = f"coffee_{coffee_sub}_value"
                if form_data.get(value_key):
                    food_data.append({
                        "category": "식품",
                        "activity_type": coffee_sub,
                        "subcategory": "커피",
                        "value": float(form_data.get(value_key, 0)),
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

        # 면 처리
        if self.show_noodles:
            for noodles_sub in self.selected_noodles_subs:
                value_key = f"noodles_{noodles_sub}_value"
                if form_data.get(value_key):
                    food_data.append({
                        "category": "식품",
                        "activity_type": noodles_sub,
                        "subcategory": "면류",
                        "value": float(form_data.get(value_key, 0)),
                        "unit": "회",
                    })

        # 국/찌개 처리
        if self.show_cooked:
            for cooked_sub in self.selected_cooked_subs:
                value_key = f"cooked_{cooked_sub}_value"
                if form_data.get(value_key):
                    food_data.append({
                        "category": "식품",
                        "activity_type": cooked_sub,
                        "subcategory": "국/찌개",
                        "value": float(form_data.get(value_key, 0)),
                        "unit": "회",
                    })

        # 반찬 처리
        if self.show_side_dish:
            for side_dish_sub in self.selected_side_dish_subs:
                value_key = f"side_dish_{side_dish_sub}_value"
                if form_data.get(value_key):
                    food_data.append({
                        "category": "식품",
                        "activity_type": side_dish_sub,
                        "subcategory": "반찬",
                        "value": float(form_data.get(value_key, 0)),
                        "unit": "회",
                    })

        # 고기 처리
        if self.show_grilled_meat:
            for grilled_meat_sub in self.selected_grilled_meat_subs:
                value_key = f"grilled_meat_{grilled_meat_sub}_value"
                if form_data.get(value_key):
                    food_data.append({
                        "category": "식품",
                        "activity_type": grilled_meat_sub,
                        "subcategory": "고기",
                        "value": float(form_data.get(value_key, 0)),
                        "unit": "회",
                    })

        # 과일 처리
        if self.show_fruit:
            for fruit_sub in self.selected_fruit_subs:
                value_key = f"fruit_{fruit_sub}_value"
                if form_data.get(value_key):
                    food_data.append({
                        "category": "식품",
                        "activity_type": fruit_sub,
                        "subcategory": "과일",
                        "value": float(form_data.get(value_key, 0)),
                        "unit": "회",
                    })

        # 파스타 처리
        if self.show_pasta:
            for pasta_sub in self.selected_pasta_subs:
                value_key = f"pasta_{pasta_sub}_value"
                if form_data.get(value_key):
                    food_data.append({
                        "category": "식품",
                        "activity_type": pasta_sub,
                        "subcategory": "파스타",
                        "value": float(form_data.get(value_key, 0)),
                        "unit": "회",
                    })

        self.all_activities = self.all_activities + food_data

        # 입력모드 종료 + 선택 초기화
        self.food_input_mode = False
        self.food_step = 0
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
        self.selected_dairy_subs = []
        self.selected_rice_subs = []
        self.selected_coffee_subs = []
        self.selected_fastfood_subs = []
        self.selected_noodles_subs = []
        self.selected_cooked_subs = []
        self.selected_side_dish_subs = []
        self.selected_grilled_meat_subs = []
        self.selected_fruit_subs = []
        self.selected_pasta_subs = []

        yield rx.redirect("/input/clothing")
    
    # ------------------------------ 의류 관련 메서드 ------------------------------
    
    def toggle_tshirts(self):
        self.selected_tshirts = not self.selected_tshirts
    
    def toggle_jeans(self):
        self.selected_jeans = not self.selected_jeans
    
    def toggle_shoes(self):
        self.selected_shoes = not self.selected_shoes
    
    def toggle_acc(self):
        self.selected_acc = not self.selected_acc
    
    def show_clothing_input_fields(self):
        """선택된 항목들의 입력 필드를 표시"""
        self.show_tshirts = self.selected_tshirts
        self.show_jeans = self.selected_jeans
        self.show_shoes = self.selected_shoes
        self.show_acc = self.selected_acc
        self.clothing_input_mode = True

    def reset_clothing_selection(self):
        """다시 선택하기: 모든 선택 초기화하고 카테고리 선택 단계로 돌아가기"""
        self.clothing_input_mode = False
        self.selected_tshirts = False
        self.selected_jeans = False
        self.selected_shoes = False
        self.selected_acc = False
        self.show_tshirts = False
        self.show_jeans = False
        self.show_shoes = False
        self.show_acc = False
    
    async def handle_clothing_submit(self, form_data: dict):
        """의류 입력값 폼 제출 -> 데이터 저장 -> 다음 페이지 이동"""
        # 기존 의류 데이터 제거
        self.all_activities = [
            act for act in self.all_activities 
            if act.get("category") != "의류"
        ]
        
        clothing_data = []
        
        if self.show_tshirts and form_data.get("tshirts_value"):
            clothing_data.append({
                "category": "의류",
                "activity_type": "티셔츠",
                "value": float(form_data.get("tshirts_value", 0)),
                "sub_category": form_data.get("tshirts_sub", ""),
            })
        
        if self.show_jeans and form_data.get("jeans_value"):
            clothing_data.append({
                "category": "의류",
                "activity_type": "청바지",
                "value": float(form_data.get("jeans_value", 0)),
                "sub_category": form_data.get("jeans_sub", ""),
            })
        
        if self.show_shoes and form_data.get("shoes_value"):
            clothing_data.append({
                "category": "의류",
                "activity_type": "신발",
                "value": float(form_data.get("shoes_value", 0)),
                "sub_category": form_data.get("shoes_sub", ""),
            })
        
        if self.show_acc and form_data.get("acc_value"):
            clothing_data.append({
                "category": "의류",
                "activity_type": "가방/잡화",
                "value": float(form_data.get("acc_value", 0)),
                "sub_category": form_data.get("acc_sub", ""),
            })
        
        self.all_activities = self.all_activities + clothing_data
        
        # 입력모드 종료 + 선택 초기화
        self.clothing_input_mode = False
        self.selected_tshirts = False
        self.selected_jeans = False
        self.selected_shoes = False
        self.selected_acc = False
        self.show_tshirts = False
        self.show_jeans = False
        self.show_shoes = False
        self.show_acc = False
        
        yield rx.redirect("/input/electricity")
    
    # ------------------------------ 전기 관련 메서드 ------------------------------
    
    def toggle_ac(self):
        self.selected_ac = not self.selected_ac
    
    def toggle_heater(self):
        self.selected_heater = not self.selected_heater
    
    def show_electricity_input_fields(self):
        """선택된 항목들의 입력 필드를 표시"""
        self.show_ac = self.selected_ac
        self.show_heater = self.selected_heater
        self.electricity_input_mode = True

    def reset_electricity_selection(self):
        """다시 선택하기: 모든 선택 초기화하고 카테고리 선택 단계로 돌아가기"""
        self.electricity_input_mode = False
        self.selected_ac = False
        self.selected_heater = False
        self.show_ac = False
        self.show_heater = False
    
    async def handle_electricity_submit(self, form_data: dict):
        """전기 입력값 폼 제출 -> 데이터 저장 -> 다음 페이지 이동"""
        # 기존 전기 데이터 제거
        self.all_activities = [
            act for act in self.all_activities 
            if act.get("category") != "전기"
        ]
        
        electricity_data = []
        
        if self.show_ac and form_data.get("ac_value"):
            electricity_data.append({
                "category": "전기",
                "activity_type": "냉방기",
                "value": float(form_data.get("ac_value", 0)),
            })
        
        if self.show_heater and form_data.get("heater_value"):
            electricity_data.append({
                "category": "전기",
                "activity_type": "난방기",
                "value": float(form_data.get("heater_value", 0)),
            })
        
        self.all_activities = self.all_activities + electricity_data
        
        # 입력모드 종료 + 선택 초기화
        self.electricity_input_mode = False
        self.selected_ac = False
        self.selected_heater = False
        self.show_ac = False
        self.show_heater = False
        
        yield rx.redirect("/input/water")
    
    # ------------------------------ 쓰레기 관련 메서드 ------------------------------
    
    def toggle_general(self):
        self.selected_general = not self.selected_general
    
    def toggle_plastic(self):
        self.selected_plastic = not self.selected_plastic
    
    def toggle_paper(self):
        self.selected_paper = not self.selected_paper
    
    def toggle_glass(self):
        self.selected_glass = not self.selected_glass
    
    def toggle_can(self):
        self.selected_can = not self.selected_can
    
    def show_waste_input_fields(self):
        """선택된 항목들의 입력 필드를 표시"""
        self.show_general = self.selected_general
        self.show_plastic = self.selected_plastic
        self.show_paper = self.selected_paper
        self.show_glass = self.selected_glass
        self.show_can = self.selected_can
        self.waste_input_mode = True

    def reset_waste_selection(self):
        """다시 선택하기: 모든 선택 초기화하고 카테고리 선택 단계로 돌아가기"""
        self.waste_input_mode = False
        self.selected_general = False
        self.selected_plastic = False
        self.selected_paper = False
        self.selected_glass = False
        self.selected_can = False
        self.show_general = False
        self.show_plastic = False
        self.show_paper = False
        self.show_glass = False
        self.show_can = False
    
    def handle_waste_submit_direct(self):
        """쓰레기 입력값 직접 제출 (form 제출 강제)"""
        # JavaScript로 form 제출 강제
        return rx.call_script("""
            (function() {
                const form = document.getElementById('waste-form');
                if (!form) {
                    return;
                }
                // form 제출 강제
                const submitEvent = new Event('submit', { bubbles: true, cancelable: true });
                form.dispatchEvent(submitEvent);
            })()
        """)
    
    async def handle_waste_submit_from_script(self, form_data: dict):
        """스크립트에서 수집한 form 데이터로 쓰레기 제출 처리"""
        if not form_data:
            form_data = {}
        
        # 기존 쓰레기 데이터 제거
        self.all_activities = [
            act for act in self.all_activities 
            if act.get("category") != "쓰레기"
        ]
        
        waste_data = []
        
        if self.show_general and form_data.get("general_value"):
            waste_data.append({
                "category": "쓰레기",
                "activity_type": "일반쓰레기",
                "value": float(form_data.get("general_value", 0)),
                "unit": form_data.get("general_unit", "개"),
            })
        
        if self.show_plastic and form_data.get("plastic_value"):
            waste_data.append({
                "category": "쓰레기",
                "activity_type": "플라스틱",
                "value": float(form_data.get("plastic_value", 0)),
                "unit": form_data.get("plastic_unit", "개"),
            })
        
        if self.show_paper and form_data.get("paper_value"):
            waste_data.append({
                "category": "쓰레기",
                "activity_type": "종이",
                "value": float(form_data.get("paper_value", 0)),
                "unit": form_data.get("paper_unit", "개"),
            })
        
        if self.show_glass and form_data.get("glass_value"):
            waste_data.append({
                "category": "쓰레기",
                "activity_type": "유리",
                "value": float(form_data.get("glass_value", 0)),
                "unit": form_data.get("glass_unit", "개"),
            })
        
        if self.show_can and form_data.get("can_value"):
            waste_data.append({
                "category": "쓰레기",
                "activity_type": "캔",
                "value": float(form_data.get("can_value", 0)),
                "unit": form_data.get("can_unit", "개"),
            })
        
        self.all_activities = self.all_activities + waste_data
        
        # 입력모드 종료 + 선택 초기화
        self.waste_input_mode = False
        self.selected_general = False
        self.selected_plastic = False
        self.selected_paper = False
        self.selected_glass = False
        self.selected_can = False
        self.show_general = False
        self.show_plastic = False
        self.show_paper = False
        self.show_glass = False
        self.show_can = False
        
        # 리포트 계산 플래그 초기화 (리포트 페이지에서 다시 계산하도록)
        self.is_report_calculated = False
        
        # 리포트로 이동 (리포트 페이지에서 on_report_page_load가 자동으로 계산 수행)
        yield rx.redirect("/report")
    
    async def handle_waste_submit(self, form_data: dict):
        """쓰레기 입력값 폼 제출 -> 데이터 저장 -> 리포트로 이동"""
        # 기존 쓰레기 데이터 제거
        self.all_activities = [
            act for act in self.all_activities 
            if act.get("category") != "쓰레기"
        ]
        
        waste_data = []
        
        if self.show_general and form_data.get("general_value"):
            waste_data.append({
                "category": "쓰레기",
                "activity_type": "일반쓰레기",
                "value": float(form_data.get("general_value", 0)),
                "unit": form_data.get("general_unit", "개"),
            })
        
        if self.show_plastic and form_data.get("plastic_value"):
            waste_data.append({
                "category": "쓰레기",
                "activity_type": "플라스틱",
                "value": float(form_data.get("plastic_value", 0)),
                "unit": form_data.get("plastic_unit", "개"),
            })
        
        if self.show_paper and form_data.get("paper_value"):
            waste_data.append({
                "category": "쓰레기",
                "activity_type": "종이",
                "value": float(form_data.get("paper_value", 0)),
                "unit": form_data.get("paper_unit", "개"),
            })
        
        if self.show_glass and form_data.get("glass_value"):
            waste_data.append({
                "category": "쓰레기",
                "activity_type": "유리",
                "value": float(form_data.get("glass_value", 0)),
                "unit": form_data.get("glass_unit", "개"),
            })
        
        if self.show_can and form_data.get("can_value"):
            waste_data.append({
                "category": "쓰레기",
                "activity_type": "캔",
                "value": float(form_data.get("can_value", 0)),
                "unit": form_data.get("can_unit", "개"),
            })
        
        self.all_activities = self.all_activities + waste_data
        
        # 입력모드 종료 + 선택 초기화
        self.waste_input_mode = False
        self.selected_general = False
        self.selected_plastic = False
        self.selected_paper = False
        self.selected_glass = False
        self.selected_can = False
        self.show_general = False
        self.show_plastic = False
        self.show_paper = False
        self.show_glass = False
        self.show_can = False
        
        # 리포트 계산 플래그 초기화 (리포트 페이지에서 다시 계산하도록)
        self.is_report_calculated = False
        
        # 리포트로 이동 (리포트 페이지에서 on_report_page_load가 자동으로 계산 수행)
        yield rx.redirect("/report")
    
    # ------------------------------ 물 관련 메서드 ------------------------------
    
    def toggle_shower(self):
        self.selected_shower = not self.selected_shower
    
    def toggle_dish(self):
        self.selected_dish = not self.selected_dish
    
    def toggle_laundry(self):
        self.selected_laundry = not self.selected_laundry
    
    def show_water_input_fields(self):
        """선택된 항목들의 입력 필드를 표시"""
        self.show_shower = self.selected_shower
        self.show_dish = self.selected_dish
        self.show_laundry = self.selected_laundry
        self.water_input_mode = True

    def reset_water_selection(self):
        """다시 선택하기: 모든 선택 초기화하고 카테고리 선택 단계로 돌아가기"""
        self.water_input_mode = False
        self.selected_shower = False
        self.selected_dish = False
        self.selected_laundry = False
        self.show_shower = False
        self.show_dish = False
        self.show_laundry = False
    
    async def handle_water_submit(self, form_data: dict):
        """물 입력값 폼 제출 -> 데이터 저장 -> 리포트로 이동"""
        # 기존 물 데이터 제거
        self.all_activities = [
            act for act in self.all_activities 
            if act.get("category") != "물"
        ]
        
        water_data = []
        
        if self.show_shower and form_data.get("shower_value"):
            water_data.append({
                "category": "물",
                "activity_type": "샤워",
                "value": float(form_data.get("shower_value", 0)),
                "unit": form_data.get("shower_unit", "회"),
            })
        
        if self.show_dish and form_data.get("dish_count"):
            water_data.append({
                "category": "물",
                "activity_type": "설거지",
                "value": float(form_data.get("dish_count", 0)),
                "unit": "회",
            })
        
        if self.show_laundry and form_data.get("laundry_count"):
            water_data.append({
                "category": "물",
                "activity_type": "세탁",
                "value": float(form_data.get("laundry_count", 0)),
                "unit": "회",
            })
        
        self.all_activities = self.all_activities + water_data
        
        # 입력모드 종료 + 선택 초기화
        self.water_input_mode = False
        self.selected_shower = False
        self.selected_dish = False
        self.selected_laundry = False
        self.show_shower = False
        self.show_dish = False
        self.show_laundry = False
        
        # 리포트 계산 플래그 초기화 (리포트 페이지에서 다시 계산하도록)
        self.is_report_calculated = False
        
        # 쓰레기 페이지로 이동
        yield rx.redirect("/input/waste")
    
    # ------------------------------ 리포트 계산 메서드 ------------------------------
    
    async def calculate_report(self):
        """리포트 페이지에서 전체 탄소 배출량을 계산합니다."""
        # 새 리포트 계산을 시작할 때, 이전 저장 메시지/상태 초기화
        self.save_message = ""
        self.is_save_success = False
        
        try:
            from ..service.carbon_calculator import calculate_carbon_emission
            
            total_emission = 0.0
            calculation_details = []  # 상세 계산 내역 저장
            
            # 활동 데이터가 없으면 계산하지 않음
            if len(self.all_activities) == 0:
                self.total_carbon_emission = 0.0
                self.is_report_calculated = True
                self.calculation_details = []
                return
            
            for idx, activity in enumerate(self.all_activities):
                category = activity.get("category", "")
                activity_type = activity.get("activity_type", "")
                value = activity.get("value", 0)
                unit = activity.get("unit", "")
                sub_category = activity.get("sub_category") or activity.get("subcategory") or activity.get("is_vintage")
                
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
            
            # 결과 저장
            self.total_carbon_emission = round(total_emission, 3)
            self.is_report_calculated = True
            self.calculation_details = calculation_details  # 상세 내역 저장
            
            # 절약량 계산 (자전거/걷기 사용 시)
            await self._calculate_savings()
            
            # 포인트 계산 (리포트 표시용)
            await self._calculate_points_for_report()
            
            # 카테고리별 배출량 집계
            await self._calculate_category_breakdown()
            
            # 레벨 계산
            self._calculate_carbon_level()
            
        except Exception as e:
            logger.error(f"[리포트 계산] ❌ 계산 오류 발생: {e}", exc_info=True)
            self.total_carbon_emission = 0.0
            self.is_report_calculated = False
    
    def _calculate_carbon_level(self):
        """탄소 배출량 기준으로 레벨 계산 (배출량이 낮을수록 높은 레벨)"""
        emission = self.total_carbon_emission
        
        # 레벨 기준 (배출량이 낮을수록 높은 레벨)
        # Level 5: 0-2 kg (매우 낮음, 최고 등급)
        # Level 4: 2-5 kg (낮음)
        # Level 3: 5-10 kg (보통)
        # Level 2: 10-20 kg (높음)
        # Level 1: 20+ kg (매우 높음, 최하 등급)
        
        if emission <= 2.0:
            self.carbon_level = 5
            self.carbon_level_image = "/level_5.png"
            self.next_level_threshold = 0.0  # 이미 최고 레벨
            self.next_level_text = "최고 레벨을 달성하셨습니다! 🏆"
        elif emission <= 5.0:
            self.carbon_level = 4
            self.carbon_level_image = "/level_4.png"
            self.next_level_threshold = emission - 2.0  # 2kg까지 감소 필요
            self.next_level_text = f"Level 5까지 {self.next_level_threshold:.2f}kg 더 줄여보세요!"
        elif emission <= 10.0:
            self.carbon_level = 3
            self.carbon_level_image = "/level_3.png"
            self.next_level_threshold = emission - 5.0  # 5kg까지 감소 필요
            self.next_level_text = f"Level 4까지 {self.next_level_threshold:.2f}kg 더 줄여보세요!"
        elif emission <= 20.0:
            self.carbon_level = 2
            self.carbon_level_image = "/level_2.png"
            self.next_level_threshold = emission - 10.0  # 10kg까지 감소 필요
            self.next_level_text = f"Level 3까지 {self.next_level_threshold:.2f}kg 더 줄여보세요!"
        else:
            self.carbon_level = 1
            self.carbon_level_image = "/level_1.png"
            self.next_level_threshold = emission - 20.0  # 20kg까지 감소 필요
            self.next_level_text = f"Level 2까지 {self.next_level_threshold:.2f}kg 더 줄여보세요!"
        
        # 디버그 로그 제거 (배포용)
        pass
    
    # ------------------------------ DB 저장 메서드 ------------------------------
    
    async def _save_carbon_log_to_db_internal(self):
        """탄소 로그 저장 내부 로직 (헬퍼 메서드)"""
        # 가장 먼저 로그 출력 (메서드 호출 확인)
        
        if not self.is_logged_in or not self.current_user_id:
            self.save_message = "로그인이 필요합니다."
            logger.error("[저장 실패] 로그인되지 않음")
            return
        
        self.is_saving = True
        self.save_message = ""
        
        try:
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
            if not hasattr(self, 'total_saved_emission') or self.total_saved_emission == 0.0:
                await self._calculate_savings()
            
            # 리포트가 계산되지 않았으면 계산
            if not self.is_report_calculated:
                await self.calculate_report()
            
            with Session(engine) as session:
                # 과거 챌린지 로그(source가 잘못된 경우)를 정정하여 덮어쓰기 방지
                try:
                    session.exec(
                        text(
                            "UPDATE carbonlog "
                            "SET source = 'challenge' "
                            "WHERE (source IS NULL OR source = 'carbon_input') "
                            "AND ai_feedback LIKE '챌린지 보상:%'"
                        )
                    )
                    session.commit()
                except Exception as mig_err:
                    logger.error(f"[저장] 챌린지 로그 소스 수정 오류: {mig_err}")
                
                stmt = select(CarbonLog).where(
                    CarbonLog.student_id == self.current_user_id,
                    CarbonLog.log_date == today,
                    CarbonLog.source == "carbon_input"
                )
                existing_log = session.exec(stmt).first()
                is_new_log = existing_log is None
                # 오늘 날짜 탄소 입력 로그 존재 여부 상태 반영
                self.has_today_log = not is_new_log
            # is_new_log는 아래 DB 업데이트 로직에서 사용
            
            # 테스트용: 같은 날에 여러 번 저장 가능 (제한 제거)
            
            # 포인트 계산 (한 번만 계산)
            points_earned = await self._calculate_points(total_emission)
            
            with Session(engine) as session:
                # 사용자 조회
                user_stmt = select(User).where(User.student_id == self.current_user_id)
                user = session.exec(user_stmt).first()
                
                if not user:
                    self.save_message = "❌ 사용자 정보를 찾을 수 없습니다."
                    self.is_save_success = False
                    logger.error(f"탄소 로그 저장 오류: 사용자 {self.current_user_id}를 찾을 수 없음")
                    return
                
                # 오늘 탄소 입력 로그 조회 (같은 세션에서, source 필터)
                log_stmt = select(CarbonLog).where(
                    CarbonLog.student_id == self.current_user_id,
                    CarbonLog.log_date == today,
                    CarbonLog.source == "carbon_input"
                )
                log = session.exec(log_stmt).first()
                
                # 기존 포인트 저장 (로그 업데이트 전)
                old_points = log.points_earned if log and log.points_earned else 0
                
                # 로그 생성 또는 업데이트
                if log:
                    log.transport_km = transport_km
                    log.ac_hours = ac_hours
                    log.cup_count = cup_count
                    log.total_emission = total_emission
                    log.activities_json = activities_json
                    log.points_earned = points_earned
                    log.source = "carbon_input"
                else:
                    log = CarbonLog(
                        student_id=self.current_user_id,
                        log_date=today,
                        transport_km=transport_km,
                        ac_hours=ac_hours,
                        cup_count=cup_count,
                        total_emission=total_emission,
                        activities_json=activities_json,
                        points_earned=points_earned,
                        source="carbon_input",
                        created_at=datetime.now()
                    )
                
                session.add(log)
                
                # 사용자 포인트 업데이트 (같은 세션에서)
                if is_new_log:
                    # 새로운 로그: 포인트 추가
                    user.current_points += points_earned
                else:
                    # 기존 로그 업데이트: 기존 포인트를 빼고 새 포인트 추가
                    user.current_points = user.current_points - old_points + points_earned
                
                self.current_user_points = user.current_points
                session.add(user)
                
                # 포인트 획득 이유 설명 생성 (포인트가 있을 때만)
                description = "환경 친화적 활동"
                if points_earned > 0:
                    reasons = []
                    if self.total_saved_emission > 0:
                        reasons.append(f"절약량 {self.total_saved_emission}kg")
                    # 빈티지 제품 사용 확인
                    vintage_count = sum(
                        int(act.get("value", 0))
                        for act in self.all_activities
                        if act.get("category") == "의류"
                        and (
                            act.get("sub_category") == "빈티지"
                            or act.get("subcategory") == "빈티지"
                            or act.get("sub") == "빈티지"
                        )
                    )
                    if vintage_count > 0:
                        reasons.append(f"빈티지 제품 {vintage_count}개")
                    # 평균보다 낮은 배출량 확인
                    from ..service.average_data import get_total_average

                    avg_emission = get_total_average()
                    if total_emission < avg_emission:
                        diff = avg_emission - total_emission
                        reasons.append(f"평균보다 {diff:.1f}kg 낮음")
                    
                    description = ", ".join(reasons) if reasons else "환경 친화적 활동"
                
                # 한 번에 commit
                session.commit()
                session.refresh(log)
                session.refresh(user)
                
                if points_earned > 0:
                    # 포인트 획득 이유 메시지 생성 (위에서 생성한 description 재사용)
                    self.save_message = f"✅ 저장 완료! {description}으로 {points_earned}점을 획득했습니다."
                else:
                    self.save_message = "✅ 저장 완료!"
                
                self.is_save_success = True
                self.has_today_log = True  # 저장 완료 후 오늘 날짜 로그 존재 표시
            
            self.is_saving = False
            
            # 저장 완료 후 다시 저장할 수 있도록 저장 메시지를 일정 시간 후 초기화하지 않음
            # (사용자가 여러 번 저장할 수 있도록 상태 유지)
            
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
                    
                    # ChallengeState의 load_mypage_data 호출하여 포인트 로그 등 새로고침
                    # AppState는 ChallengeState이므로 self를 통해 호출 가능
                    if hasattr(self, 'load_mypage_data'):
                        await self.load_mypage_data()
                    else:
                        # load_mypage_data가 없으면 포인트 로그만 직접 로드
                        if hasattr(self, 'load_points_log'):
                            await self.load_points_log()
                except Exception as refresh_error:
                    pass
            
        except Exception as e:
            self.save_message = f"❌ 저장 중 오류가 발생했습니다: {str(e)}"
            self.is_save_success = False
            self.is_saving = False
            logger.error(f"[저장 오류] 탄소 로그 저장 실패: {e}", exc_info=True)
            logger.error(f"[저장 오류] 사용자: {self.current_user_id}, 활동 수: {len(self.all_activities)}")
            import traceback
    
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
                CarbonLog.log_date == target_date,
                CarbonLog.source == "carbon_input"
            )
            
            if logs:
                log = logs[0]
                activities = log.get_activities()
                if activities:
                    self.all_activities = activities
                    # 저장된 데이터가 있으면 자동으로 계산 수행
                    await self.calculate_report()
                    pass
                else:
                    pass
            else:
                pass
                
        except Exception as e:
            logger.error(f"저장된 데이터 불러오기 오류: {e}", exc_info=True)
    
    async def get_saved_logs_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """저장된 로그 이력을 반환합니다."""
        if not self.is_logged_in or not self.current_user_id:
            return []
        
        try:
            logs = await CarbonLog.find(
                CarbonLog.student_id == self.current_user_id,
                CarbonLog.source == "carbon_input"
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
                statement = select(CarbonLog).where(
                    CarbonLog.student_id == self.current_user_id,
                    CarbonLog.source == "carbon_input"
                )
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
                        # 디버그 로그 제거 (배포용)
                        pass
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
    has_average_comparison: bool = False  # 평균 비교 데이터 존재 여부
    category_emission_list: List[Dict[str, Any]] = []  # foreach에서 사용하기 위한 리스트 형태
    donut_chart_svg: str = ""  # 도넛 차트 SVG 문자열
    ai_analysis_result: str = ""
    ai_suggestions: List[str] = []
    ai_alternatives: List[Dict[str, Any]] = []
    is_loading_ai: bool = False
    
    # 레벨 시스템 관련 상태
    carbon_level: int = 1  # 현재 레벨 (1-5)
    next_level_threshold: float = 0.0  # 다음 레벨까지 필요한 탄소 배출량 감소량
    carbon_level_image: str = "/level_1.png"  # 레벨 배지 이미지 경로
    next_level_text: str = ""  # 다음 레벨 달성을 위한 안내 텍스트
    
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
            
            # 디버그 로그 제거 (배포용)
            pass
            
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
                
                # 디버그 로그 제거 (배포용)
                pass
                
                # 거리로 변환
                distance_km, _ = convert_to_standard_unit(
                    category="교통",
                    activity_type=activity_type,
                    value=value,
                    unit=unit,
                    sub_category=None
                )
                
                if distance_km <= 0:
                    # 디버그 로그 제거 (배포용)
                    pass
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
                
                # 디버그 로그 제거 (배포용)
                pass
            
            self.total_saved_emission = round(total_saved, 3)
            self.saved_money = round(total_saved * CARBON_PRICE_PER_KG, 2)
            self.savings_details = savings_list
            
            # 디버그 로그 제거 (배포용)
            pass
            
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
                sub_category = activity.get("sub_category") or activity.get("subcategory") or activity.get("sub")
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
            
            # 디버그 로그 제거 (배포용)
            pass
            
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
            # 디버그 로그 제거 (배포용)
            pass
            
            # 2. 빈티지 제품 사용 포인트
            vintage_count = 0
            # 디버그 로그 제거 (배포용)
            pass
            for activity in self.all_activities:
                category = activity.get("category")
                sub_category = activity.get("sub_category") or activity.get("subcategory") or activity.get("sub")
                value = activity.get("value", 0)
                # 디버그 로그 제거 (배포용)
                pass
                if category == "의류" and sub_category == "빈티지":
                    vintage_count += int(value)
                    # 디버그 로그 제거 (배포용)
                    pass
            
            # 빈티지 제품 1개당 10점
            vintage_points = vintage_count * 10
            total_points += vintage_points
            # 디버그 로그 제거 (배포용)
            pass
            
            # 3. 평균보다 낮은 배출량 포인트
            avg_emission = get_total_average()  # 14.5 kgCO₂e/일
            if total_emission < avg_emission:
                # 평균보다 낮은 배출량 1kg당 20점 (최대 100점)
                diff = avg_emission - total_emission
                emission_points = min(int(diff * 20), 100)
                total_points += emission_points
                # 디버그 로그 제거 (배포용)
                pass
            else:
                # 디버그 로그 제거 (배포용)
                pass
            
            # 디버그 로그 제거 (배포용)
            pass
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
            abs_difference = abs(difference)
            percentage = (difference / total_average * 100) if total_average > 0 else 0
            
            self.total_average_comparison = {
                "user": round(total_user_emission, 2),
                "average": round(total_average, 2),
                "difference": round(difference, 2),
                "abs_difference": round(abs_difference, 2),
                "percentage": round(percentage, 1),
                "is_better": difference < 0,
                # 문자열 포맷은 UI에서 Var 포맷 오류를 피하기 위해 미리 계산
                "average_str": f"{total_average:.2f} kgCO₂e",
                "user_str": f"{total_user_emission:.2f} kgCO₂e",
                "abs_difference_str": f"차이: {abs_difference:.2f} kgCO₂e",
                "percentage_str": f"({percentage:.1f}%)",
            }
            self.has_average_comparison = True
            
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
            
            # 카테고리별 평균값 가져오기
            from ..service.average_data import get_average_emission
            
            for category, emission in category_emission.items():
                percentage = (emission / total) * 100 if total > 0 else 0
                
                # 카테고리별 평균값과 비교
                avg_emission = get_average_emission(category)
                difference = emission - avg_emission
                diff_percentage = (difference / avg_emission * 100) if avg_emission > 0 else 0
                is_better = difference < 0
                
                # 포인트 계산 (평균 대비 포인트는 전체 포인트 계산에서 사용)
                # 여기서는 표시용으로만 저장
                category_list.append({
                    "category": category,
                    "emission": round(emission, 2),
                    "percentage": round(percentage, 1),
                    "progress_value": percentage,
                    "color": color_map.get(category, "#6b7280"),
                    "cumulative_percentage": cumulative_percentage,
                    "stroke_dasharray": f"{2 * 3.14159 * 80 * (percentage / 100)} {2 * 3.14159 * 80}",
                    "stroke_dashoffset": cumulative_percentage * 2 * 3.14159 * 80 / 100,
                    "rotation": -90 + cumulative_percentage * 360 / 100,
                    # 평균 비교 데이터
                    "average_emission": round(avg_emission, 2),
                    "difference": round(difference, 2),
                    "diff_percentage": round(diff_percentage, 1),
                    "is_better": is_better,
                    "diff_str": f"{abs(difference):.2f} kgCO₂e {'절감' if is_better else '초과'}",
                    "diff_percentage_str": f"{abs(diff_percentage):.1f}% {'낮음' if is_better else '높음'}"
                })
                cumulative_percentage += percentage
            
            self.category_emission_list = category_list
            
            # 도넛 차트 SVG 생성
            self._generate_donut_chart_svg()
            
            # 디버그 로그 제거 (배포용)
            pass
            
        except Exception as e:
            logger.error(f"카테고리별 배출량 집계 오류: {e}", exc_info=True)
            self.category_emission_breakdown = {}
            self.average_comparison = {}
            self.average_comparison_list = []
            self.total_average_comparison = {}
            self.has_average_comparison = False
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
            # 디버그 로그 제거 (배포용)
            pass
            
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
            # 정책 후보 기본 세트 주입 (빈 경우에만)
            if not self.policy_candidates:
                self.policy_candidates = [
                    {
                        "name": "광역알뜰교통카드",
                        "reason": "교통비를 절감하면서 대중교통 이용을 늘릴 때 적합합니다.",
                        "url": "https://www.alcard.kr",
                    },
                    {
                        "name": "탄소중립포인트",
                        "reason": "전기·가스·수도 절약 시 포인트 적립을 받을 수 있습니다.",
                        "url": "https://cpoint.or.kr",
                    },
                    {
                        "name": "다회용컵 보증금 제도",
                        "reason": "카페 일회용컵 사용을 줄이면 보증금을 환급받을 수 있습니다.",
                        "url": "https://www.zeroshop.kr",
                    },
                ]
            from ..ai.llm_service import get_coaching_feedback
            import json
            
            # 총배출량 정합성 검증: 카테고리 합계와 total_carbon_emission 일치 보정
            breakdown = self.category_emission_breakdown or {}
            try:
                breakdown_sum = float(sum(float(v) for v in breakdown.values())) if breakdown else 0.0
            except Exception:
                breakdown_sum = float(self.total_carbon_emission or 0.0)
            
            total_carbon = float(self.total_carbon_emission or 0.0)
            # 합계와 차이가 크면 합계 기준으로 보정
            if abs(breakdown_sum - total_carbon) > 1e-6:
                total_carbon = breakdown_sum
            
            payload = {
                "category_carbon_data": self.category_emission_breakdown or {},
                "total_carbon_kg": total_carbon,
                "category_activity_data": self.category_emission_breakdown or {},
                "policy_candidates": getattr(self, "policy_candidates", []),
            }
            
            feedback_json = get_coaching_feedback(payload)
            parsed = json.loads(feedback_json)
            
            # 분석 요약
            final_screen = parsed.get("final_report_screen", {}) if isinstance(parsed, dict) else {}
            today_screen = parsed.get("today_result_screen", {}) if isinstance(parsed, dict) else {}
            
            self.ai_analysis_result = (
                final_screen.get("total_summary_text")
                or today_screen.get("usage_summary_text")
                or "AI 분석 결과를 불러올 수 없습니다."
            )
            
            # 행동 제안
            recos = final_screen.get("recommendations", []) if isinstance(final_screen, dict) else []
            suggestions = []
            for r in recos:
                if isinstance(r, dict):
                    action = r.get("action")
                    detail = r.get("detail")
                    if action and detail:
                        suggestions.append(f"{action}: {detail}")
                    elif action:
                        suggestions.append(action)
            self.ai_suggestions = suggestions[:5] if suggestions else []
            
            # 정책/대안(폴백)
            policy_recos = final_screen.get("policy_recommendations", []) if isinstance(final_screen, dict) else []
            alternatives = []
            for p in policy_recos:
                if isinstance(p, dict):
                    name = p.get("name") or p.get("title") or ""
                    desc = p.get("description") or p.get("detail") or p.get("reason") or ""
                    url = p.get("url") or ""
                    if name or desc or url:
                        alternatives.append({
                            "current": name,
                            "alternative": desc,
                            "impact": url,
                        })
            # 정책 추천이 비어있으면 기본 정책 후보 사용
            if not alternatives and hasattr(self, "policy_candidates") and self.policy_candidates:
                for policy in self.policy_candidates:
                    alternatives.append({
                        "current": policy.get("name", ""),
                        "alternative": policy.get("reason", ""),
                        "impact": policy.get("url", ""),
                    })
            
            self.ai_alternatives = alternatives
            
            # 디버그 로그 제거 (배포용)
            pass
            
        except Exception as e:
            logger.error(f"AI 분석 결과 생성 오류: {e}", exc_info=True)
            self.ai_analysis_result = "AI 분석을 불러오는 중 오류가 발생했습니다."
            self.ai_suggestions = []
            # 오류 발생 시에도 기본 정책 후보 표시
            if hasattr(self, "policy_candidates") and self.policy_candidates:
                self.ai_alternatives = [
                    {
                        "current": policy.get("name", ""),
                        "alternative": policy.get("reason", ""),
                        "impact": policy.get("url", ""),
                    }
                    for policy in self.policy_candidates
                ]
            else:
                self.ai_alternatives = []
        finally:
            self.is_loading_ai = False

    async def on_report_page_load(self):
        """리포트 페이지 로드 시 자동으로 계산 및 AI 분석 실행"""
        try:
            # 새 리포트를 볼 때마다 이전 저장 메시지는 초기화
            self.save_message = ""
            self.is_save_success = False
            
            # 이미 계산된 리포트가 있으면 재계산하지 않음 (로딩 시간 단축)
            if self.is_report_calculated and self.total_carbon_emission > 0:
                # 이미 계산된 리포트가 있으면 AI 분석만 확인
                if not self.ai_analysis_result:
                    await self.generate_ai_analysis()
                return
            
            # 리포트가 계산되지 않았거나 활동 데이터가 변경된 경우에만 계산
            if len(self.all_activities) == 0:
                # 빈 리포트라도 계산 완료로 표시
                self.total_carbon_emission = 0.0
                self.is_report_calculated = True
                self.calculation_details = []
                self.ai_analysis_result = ""  # AI 분석도 초기화
            else:
                # 리포트 계산 (한 번만)
                if not self.is_report_calculated:
                    self.ai_analysis_result = ""  # AI 분석도 초기화하여 재생성
                    await self.calculate_report()
            
            # AI 분석 실행 (결과가 없을 때만)
            if self.is_report_calculated and not self.ai_analysis_result:
                await self.generate_ai_analysis()
        except Exception:
            # 오류 발생 시에도 리포트 표시 가능하도록
            if not self.is_report_calculated:
                self.total_carbon_emission = 0.0
                self.is_report_calculated = True

