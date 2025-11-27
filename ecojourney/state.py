# state.py

import reflex as rx
import logging
from typing import Dict, List, Any, Optional

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 💡 서비스 함수를 직접 호출 (FastAPI 라우터 불필요)
# State에서 직접 서비스 로직을 호출합니다

# 탄소 배출량 데이터를 저장할 딕셔너리 구조 정의
# 필수 필드: category, activity_type, value, unit
CarbonActivity = Dict[str, Any]

class AppState(rx.State):
    """
    EcoJourney 앱의 전역 상태를 관리하는 클래스.
    """
    
    # 1. 화면 흐름 제어 변수
    current_category: str = "transportation" 
    # NOTE: 카테고리 이름은 FastAPI 백엔드의 데이터와 일치해야 합니다.
    CATEGORY_ORDER: List[str] = [
        "교통", "식품", "의류", "쓰레기", "전기", "물" 
    ]
    
    # 2. 카테고리별 사용자 입력값 저장소
    all_activities: List[CarbonActivity] = []
    
    # 카테고리별 입력 임시 저장소 (현재 페이지의 입력값)
    transport_inputs: List[Dict[str, Any]] = [] 
    food_inputs: List[Dict[str, Any]] = []
    clothing_inputs: List[Dict[str, Any]] = []
    electricity_inputs: List[Dict[str, Any]] = []
    water_inputs: List[Dict[str, Any]] = []
    waste_inputs: List[Dict[str, Any]] = []
    
    # UI 및 오류 메시지
    is_loading: bool = False
    error_message: str = ""
    should_redirect: bool = False
    redirect_path: str = ""
    
    # 3. 결과 리포트 데이터
    total_carbon_emission: float = 0.0
    category_breakdown: Dict[str, float] = {}
    is_report_calculated: bool = False
    
    # --- 4. 헬퍼 함수 및 라우팅 로직 ---

    def get_current_input_list(self) -> List[Dict[str, Any]]:
        """현재 카테고리에 해당하는 입력 리스트를 반환합니다."""
        if self.current_category == "교통":
            return self.transport_inputs
        elif self.current_category == "식품":
            return self.food_inputs
        elif self.current_category == "의류":
            return self.clothing_inputs
        elif self.current_category == "전기":
            return self.electricity_inputs
        elif self.current_category == "물":
            return self.water_inputs
        elif self.current_category == "쓰레기":
            return self.waste_inputs
        return []

    def set_current_input_list(self, new_list: List[Dict[str, Any]]):
        """현재 카테고리에 해당하는 입력 리스트를 설정합니다."""
        if self.current_category == "교통":
            self.transport_inputs = new_list
        elif self.current_category == "식품":
            self.food_inputs = new_list
        elif self.current_category == "의류":
            self.clothing_inputs = new_list
        # ... (나머지 카테고리도 필요하다면 구현)
        
    def _get_category_path(self, category: str) -> str:
        """카테고리 이름을 URL 경로로 변환합니다."""
        # 예: '교통' -> 'transportation' (URL에서 영문 사용 가정)
        mapping = {
            "교통": "transportation", "식품": "food", "의류": "clothing",
            "쓰레기": "waste", "전기": "electricity", "물": "water"
        }
        return mapping.get(category, category)

    # --- 5. 핵심 라우팅 및 액션 함수 ---

    def go_to_intro(self):
        """홈 화면에서 소개 화면으로 이동"""
        # 즉시 로그 출력 (함수 호출 확인용)
        print("=" * 60, flush=True)
        print("🖱️ [버튼 클릭 이벤트] go_to_intro 함수 호출됨!", flush=True)
        print("=" * 60, flush=True)
        
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        logger.info("=" * 60)
        logger.info(f"🖱️ [버튼 클릭 이벤트] go_to_intro 함수 호출됨!")
        logger.info(f"⏰ [타임스탬프] {timestamp}")
        logger.info(f"📍 [현재 경로] / (홈 페이지)")
        logger.info(f"🎯 [목적지] /intro (인트로 페이지)")
        logger.info("=" * 60)
        
        print(f"⏰ [타임스탬프] {timestamp}", flush=True)
        print(f"📍 [현재 경로] / (홈 페이지)", flush=True)
        print(f"🎯 [목적지] /intro (인트로 페이지)", flush=True)
        print("🔄 리다이렉트 명령 실행 중...", flush=True)
        
        # 리다이렉트 실행
        logger.info("🔄 리다이렉트 명령 실행 중...")
        redirect_result = rx.redirect("/intro")
        
        logger.info("✅ 리다이렉트 명령 완료")
        print("✅ 리다이렉트 명령 완료", flush=True)
        
        return redirect_result
    
    def next_category(self):
        """
        다음 카테고리 페이지 또는 리포트 페이지로 이동합니다.
        """
        logger.info("=" * 50)
        logger.info("➡️ next_category 함수 호출됨!")
        logger.info(f"현재 카테고리: {self.current_category}")
        print("=" * 50, flush=True)
        print(f"➡️ next_category 함수 호출됨! 현재 카테고리: {self.current_category}", flush=True)
        print("=" * 50, flush=True)
        self.error_message = "" # 오류 메시지 초기화
        
        try:
            current_index = self.CATEGORY_ORDER.index(self.current_category)
            
            if current_index < len(self.CATEGORY_ORDER) - 1:
                # 다음 카테고리로 이동
                next_category_name = self.CATEGORY_ORDER[current_index + 1]
                self.current_category = next_category_name
                next_path = self._get_category_path(next_category_name)
                return rx.redirect(f"/input/{next_path}")
            else:
                # 마지막 카테고리 후 리포트 페이지로 이동
                self.current_category = "report"
                return self.calculate_report()
                
        except ValueError:
            # 현재 카테고리가 목록에 없는 경우 (오류 방지)
            return rx.redirect("/intro")
    
    def back_category(self):
        """이전 카테고리 입력 페이지로 돌아갑니다."""
        self.error_message = "" # 오류 메시지 초기화
        
        try:
            current_index = self.CATEGORY_ORDER.index(self.current_category)
            
            if current_index > 0:
                # 이전 카테고리로 이동
                prev_category_name = self.CATEGORY_ORDER[current_index - 1]
                self.current_category = prev_category_name
                prev_path = self._get_category_path(prev_category_name)
                return rx.redirect(f"/input/{prev_path}")
            else:
                # 첫 카테고리에서는 소개 페이지로 이동
                self.current_category = ""
                return rx.redirect("/intro")
                
        except ValueError:
            # 오류 방지
            return rx.redirect("/intro")
            
    # --- 6. API 호출 및 데이터 저장 로직 ---
    
    async def _calculate_emission_for_activity(self, activity: CarbonActivity) -> Optional[float]:
        """서비스 함수를 직접 호출하여 탄소 배출량을 계산합니다."""
        
        try:
            # 서비스 함수를 직접 호출
            from service.carbon_calculator import calculate_carbon_emission
            
            result = calculate_carbon_emission(
                category=activity.get("category"),
                activity_type=activity.get("activity_type"),
                value=activity.get("value"),
                unit=activity.get("unit"),
                sub_category=activity.get("sub_category", None)
            )
            
            return result.get("carbon_emission_kg")
                
        except Exception as e:
            self.error_message = f"계산 오류: {e}"
            return None

    async def save_and_proceed(self, current_inputs: List[Dict[str, Any]]):
        """
        현재 페이지의 입력을 처리하고, API를 호출하여 계산 후 다음 페이지로 이동합니다.
        """
        logger.info("=" * 50)
        logger.info("💾 save_and_proceed 함수 호출됨!")
        logger.info(f"현재 카테고리: {self.current_category}, 입력 개수: {len(current_inputs)}")
        print("=" * 50, flush=True)
        print(f"💾 save_and_proceed 함수 호출됨! 카테고리: {self.current_category}, 입력: {len(current_inputs)}개", flush=True)
        print("=" * 50, flush=True)
        self.is_loading = True
        self.error_message = ""
        
        # 1. 이전 활동 저장소에서 현재 카테고리 활동을 제거
        self.all_activities = [
            act for act in self.all_activities if act.get("category") != self.current_category
        ]
        
        # 2. 유효한 입력만 필터링하고 탄소 배출량 계산
        valid_activities = []
        
        for inp in current_inputs:
            # 값(value)이 0보다 큰 유효한 입력만 처리
            if inp.get("value", 0.0) > 0:
                inp["category"] = self.current_category
                
                # 🚨 비동기 API 호출 및 계산
                carbon_kg = await self._calculate_emission_for_activity(inp)
                
                if carbon_kg is not None:
                    inp["carbon_emission_kg"] = carbon_kg
                    valid_activities.append(inp)
                else:
                    # 계산 실패 시 로딩 해제 후 함수 종료 (에러 메시지는 _calculate_emission_for_activity에서 설정됨)
                    self.is_loading = False
                    return 
                    
        # 3. 전체 활동 목록에 추가
        self.all_activities.extend(valid_activities)
        
        # 4. 다음 페이지로 이동
        self.is_loading = False
        return self.next_category()
        
    def skip_and_proceed(self):
        """입력 없이 다음 페이지로 이동합니다."""
        # 입력값 저장 없이 다음 페이지로 이동
        return self.next_category()
        
    # --- 7. 최종 리포트 계산 함수 ---

    async def calculate_report(self):
        """
        저장된 모든 활동을 바탕으로 최종 리포트 데이터를 계산하고 리포트 페이지로 이동합니다.
        """
        logger.info("=" * 50)
        logger.info("📊 calculate_report 함수 호출됨!")
        logger.info(f"활동 개수: {len(self.all_activities)}")
        print("=" * 50, flush=True)
        print(f"📊 calculate_report 함수 호출됨! 활동: {len(self.all_activities)}개", flush=True)
        print("=" * 50, flush=True)
        self.is_loading = True
        self.error_message = ""
        
        total = 0.0
        breakdown = {cat: 0.0 for cat in self.CATEGORY_ORDER}
        
        for activity in self.all_activities:
            emission = activity.get("carbon_emission_kg", 0.0)
            category = activity.get("category")
            
            total += emission
            if category in breakdown:
                breakdown[category] += emission
        
        self.total_carbon_emission = total
        self.category_breakdown = breakdown
        self.is_report_calculated = True
        
        self.is_loading = False
        return rx.redirect("/report")