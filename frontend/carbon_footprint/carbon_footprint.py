"""
Reflex 메인 애플리케이션
탄소 발자국 계산 및 시각화 플랫폼 (디자인 리팩터링 버전)
"""

import reflex as rx
import httpx
from datetime import datetime
from typing import List, Dict, Optional, Any
from carbon_footprint.components import summary

# API 기본 URL
API_BASE_URL = "http://localhost:8001"


class State(rx.State):
    """애플리케이션 상태 관리"""

    # 기본 상태
    submitted: bool = False
    all_activities: List[Dict] = []
    analysis_data: Optional[Dict] = None
    ai_analysis: Optional[Dict] = None

    # 카테고리 및 데이터
    categories: List[str] = []
    categories_data: Dict[str, Dict[str, Any]] = {}
    categories_loaded: bool = False  # 카테고리 로드 여부 추적

    # 카테고리별 활동 유형과 하위 카테고리를 별도 State 변수로 저장 (rx.select용)
    category_activities: Dict[str, List[str]] = {}  # {카테고리: [활동1, 활동2, ...]}
    category_sub_categories: Dict[str, List[str]] = {}  # {카테고리: [하위1, 하위2, ...]}
    category_units_by_activity: Dict[str, Dict[str, List[str]]] = {}  # {카테고리: {활동: [단위1, 단위2, ...]}}

    # 입력 폼 상태 (동적)
    form_values: Dict[str, Any] = {}
    # 카테고리별 선택된 활동 목록 (중복 선택 지원)
    selected_activities: Dict[str, List[str]] = {}  # {카테고리: [활동1, 활동2, ...]}
    # 카테고리별 활동별 입력값 (중복 선택 지원)
    activity_inputs: Dict[str, Dict[str, Dict[str, Any]]] = {}  # {카테고리: {활동: {unit, value, sub_category}}}

    # 로딩 상태
    loading_categories: bool = False
    loading_analysis: bool = False
    loading_ai: bool = False

    # 에러 메시지
    error_message: str = ""

    # 계산된 값들을 State 변수로 저장
    total_carbon: float = 0.0
    category_breakdown: Dict[str, float] = {}
    category_breakdown_list: List[tuple] = []

    def update_calculations(self):
        """탄소 배출량 계산 업데이트"""
        self.total_carbon = sum(a.get("carbon_emission_kg", 0) for a in self.all_activities)

        breakdown: Dict[str, float] = {}
        for act in self.all_activities:
            cat = act.get("category", "")
            if cat:
                breakdown[cat] = breakdown.get(cat, 0) + act.get("carbon_emission_kg", 0)

        self.category_breakdown = breakdown
        self.category_breakdown_list = list(breakdown.items())

    async def load_categories(self):
        """카테고리 목록 로드"""
        # 이미 로드되었거나 로딩 중이면 중복 실행 방지
        if self.categories_loaded or self.loading_categories:
            return

        self.loading_categories = True
        self.error_message = ""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{API_BASE_URL}/categories")
                response.raise_for_status()
                data = response.json()
                categories_list = data.get("categories", [])

                # State 변수에 직접 할당 (리스트 복사)
                if categories_list:
                    self.categories = list(categories_list)

                    # 각 카테고리별 데이터 로드
                    for category in categories_list:
                        await self.load_category_data(category)

                    self.categories_loaded = True
                else:
                    self.error_message = "카테고리 데이터가 비어있습니다."
        except httpx.ConnectError:
            self.error_message = (
                f"백엔드 서버에 연결할 수 없습니다. 백엔드가 실행 중인지 확인하세요. (URL: {API_BASE_URL})"
            )
        except httpx.HTTPStatusError as e:
            self.error_message = f"API 오류 ({e.response.status_code}): {e.response.text}"
        except Exception as e:
            self.error_message = f"API 연결 오류: {str(e)}"
        finally:
            self.loading_categories = False

    async def load_category_data(self, category: str):
        """카테고리별 데이터 로드"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # 활동 유형 가져오기
                activities_response = await client.get(
                    f"{API_BASE_URL}/categories/{category}/activities"
                )
                activities_data = activities_response.json() if activities_response.status_code == 200 else {}
                activity_types = activities_data.get("activities", [])

                # 하위 카테고리 가져오기
                sub_categories_response = await client.get(
                    f"{API_BASE_URL}/categories/{category}/sub_categories"
                )
                sub_categories_data = (
                    sub_categories_response.json()
                    if sub_categories_response.status_code == 200
                    else {}
                )
                sub_categories = sub_categories_data.get("sub_categories", [])

                # 각 활동 유형별 단위 가져오기
                units_by_activity: Dict[str, List[str]] = {}
                for activity in activity_types:
                    units_response = await client.get(
                        f"{API_BASE_URL}/categories/{category}/units",
                        params={"activity_type": activity},
                    )
                    units_data = units_response.json() if units_response.status_code == 200 else {}
                    units = units_data.get("units", [])
                    units_by_activity[activity] = units

                self.categories_data[category] = {
                    "activities": activity_types,
                    "sub_categories": sub_categories,
                    "units_by_activity": units_by_activity,
                }

                # rx.select를 위한 별도 State 변수에 저장
                self.category_activities[category] = activity_types
                self.category_sub_categories[category] = sub_categories
                self.category_units_by_activity[category] = units_by_activity

                # 선택된 활동 목록 초기화
                if category not in self.selected_activities:
                    self.selected_activities[category] = []
                if category not in self.activity_inputs:
                    self.activity_inputs[category] = {}
        except Exception as e:
            print(f"카테고리 데이터 로드 오류 ({category}): {e}")

    async def calculate_activity(
        self,
        category: str,
        activity_type: str,
        value: float,
        unit: str,
        sub_category: Optional[str] = None,
    ) -> Optional[Dict]:
        """단일 활동의 탄소 배출량 계산"""
        activity_data = {
            "category": category,
            "activity_type": activity_type,
            "value": value,
            "unit": unit,
            "sub_category": sub_category,
            "timestamp": datetime.now().isoformat(),
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{API_BASE_URL}/calculate",
                    json=activity_data,
                )
                response.raise_for_status()
                result = response.json()

                return {
                    **activity_data,
                    "carbon_emission_kg": result["carbon_emission_kg"],
                    "converted_value": result["converted_value"],
                    "converted_unit": result["converted_unit"],
                }
        except Exception as e:
            print(f"활동 계산 오류: {e}")
            return None

    async def submit_form(self):
        """폼 제출 처리 (중복 선택 지원)"""
        all_activities_data = []

        for category in self.categories:
            # 선택된 활동 목록 가져오기
            selected = self.selected_activities.get(category, [])

            for activity in selected:
                # 각 활동별 입력값 가져오기
                if category in self.activity_inputs and activity in self.activity_inputs[category]:
                    inputs = self.activity_inputs[category][activity]
                    unit = inputs.get("unit", "")
                    value = inputs.get("value", 0.0)
                    sub_category = inputs.get("sub_category", "")

                    # 값이 있고 단위가 선택된 경우에만 계산
                    if value and value > 0 and unit:
                        activity_result = await self.calculate_activity(
                            category,
                            activity,
                            value,
                            unit,
                            sub_category,
                        )
                        if activity_result:
                            all_activities_data.append(activity_result)

        if len(all_activities_data) == 0:
            self.error_message = "최소 하나 이상의 활동을 입력해주세요!"
            return

        self.all_activities = all_activities_data
        self.update_calculations()  # 계산값 업데이트
        self.submitted = True
        self.error_message = ""

        # 제출 시 자동으로 상세 분석 실행
        await self.run_detailed_analysis()

    async def run_detailed_analysis(self):
        """상세 분석 실행 (AI 분석도 함께 실행)"""
        self.loading_analysis = True
        self.error_message = ""

        try:
            # 총 탄소 배출량 계산
            total_carbon = sum(a["carbon_emission_kg"] for a in self.all_activities)

            # 카테고리별 집계
            category_breakdown: Dict[str, float] = {}
            for act in self.all_activities:
                cat = act["category"]
                category_breakdown[cat] = category_breakdown.get(cat, 0) + act["carbon_emission_kg"]

            async with httpx.AsyncClient(timeout=10.0) as client:
                # 전체 평균 비교
                total_avg_response = await client.get(f"{API_BASE_URL}/average")
                total_avg_data = (
                    total_avg_response.json() if total_avg_response.status_code == 200 else {}
                )
                total_average = total_avg_data.get("total_average", 10.0)

                # 전체 비교
                total_comp_response = await client.post(
                    f"{API_BASE_URL}/compare",
                    json={"total": total_carbon},
                )
                total_comparison = (
                    total_comp_response.json() if total_comp_response.status_code == 200 else {}
                )

                # 카테고리별 평균 비교
                category_comparisons = []
                for category in self.categories:
                    user_emission = category_breakdown.get(category, 0)
                    comp_response = await client.post(
                        f"{API_BASE_URL}/compare",
                        json={
                            "category": category,
                            "emission": user_emission,
                        },
                    )
                    if comp_response.status_code == 200:
                        comp_data = comp_response.json()
                        category_comparisons.append(
                            {
                                "category": category,
                                "user_emission": user_emission,
                                **comp_data,
                            }
                        )

                # 배지 확인
                badges_response = await client.post(
                    f"{API_BASE_URL}/badges/check",
                    json=self.all_activities,
                )
                badges = (
                    badges_response.json().get("badges", [])
                    if badges_response.status_code == 200
                    else []
                )

                self.analysis_data = {
                    "total_carbon": total_carbon,
                    "category_breakdown": category_breakdown,
                    "total_comparison": total_comparison,
                    "category_comparisons": category_comparisons,
                    "badges": badges,
                }

                # State 변수에 저장
                self.total_carbon = total_carbon
                self.category_breakdown = category_breakdown
                self.update_calculations()

                # 비교 데이터 저장
                if total_comparison:
                    self.average_comparison = total_comparison
                else:
                    self.average_comparison = {
                        "average_emission": total_average,
                        "difference": total_carbon - total_average,
                        "percentage": round(
                            (total_carbon / total_average * 100) if total_average > 0 else 0, 1
                        ),
                        "is_better": total_carbon < total_average,
                    }

                # 카테고리별 비교
                if category_comparisons:
                    self.category_comparisons = category_comparisons
                else:
                    self.category_comparisons = []

                # 배지
                if badges:
                    self.badges_list = badges
                else:
                    self.badges_list = []

                # AI 분석도 자동으로 실행
                await self.run_ai_analysis()

        except Exception as e:
            self.error_message = f"분석 중 오류 발생: {str(e)}"
        finally:
            self.loading_analysis = False

    async def run_ai_analysis(self):
        """AI 분석 실행"""
        self.loading_ai = True
        self.error_message = ""

        try:
            # 총 탄소 배출량 계산
            total_carbon = sum(a["carbon_emission_kg"] for a in self.all_activities)

            # 카테고리별 집계
            category_breakdown: Dict[str, float] = {}
            for act in self.all_activities:
                cat = act["category"]
                category_breakdown[cat] = category_breakdown.get(cat, 0) + act["carbon_emission_kg"]

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{API_BASE_URL}/coach",
                    json={
                        "activities": self.all_activities,
                        "total_carbon": total_carbon,
                        "category_breakdown": category_breakdown,
                    },
                )
                response.raise_for_status()
                result = response.json()

                # 디버깅 출력 (원하면 주석 처리 가능)
                print(f"[Frontend Debug] AI 분석 응답: {result}")
                print(f"[Frontend Debug] alternative_actions: {result.get('alternative_actions', [])}")

                # 응답 형식 변환 (alternative_actions -> alternatives)
                self.ai_analysis = {
                    "analysis": result.get("analysis", "분석 결과가 없습니다."),
                    "suggestions": result.get("suggestions", []),
                    "alternatives": result.get("alternative_actions", []),
                    "emotional_message": result.get(
                        "emotional_message", "격려 메시지가 없습니다."
                    ),
                }

                # AI 분석 결과를 안전하게 접근할 수 있도록 State 변수에 저장
                if self.ai_analysis:
                    self.ai_analysis_text = self.ai_analysis.get(
                        "analysis", "분석 결과가 없습니다."
                    )
                    self.ai_suggestions = self.ai_analysis.get("suggestions", [])
                    self.ai_alternatives = self.ai_analysis.get("alternatives", [])
                    self.ai_emotional_message = self.ai_analysis.get(
                        "emotional_message", "격려 메시지가 없습니다."
                    )
                else:
                    self.ai_analysis_text = "분석 결과가 없습니다."
                    self.ai_suggestions = []
                    self.ai_alternatives = []
                    self.ai_emotional_message = "격려 메시지가 없습니다."
        except Exception as e:
            self.error_message = f"AI 분석 중 오류 발생: {str(e)}"
            # 에러 발생 시에도 기존 데이터는 유지 (사라지지 않도록)
            # self.ai_analysis = None  # 주석 처리하여 기존 데이터 유지
        finally:
            self.loading_ai = False

    def reset_form(self):
        """폼 초기화"""
        self.submitted = False
        self.all_activities = []
        self.analysis_data = None
        self.ai_analysis = None
        self.error_message = ""
        self.update_calculations()

    # State 변수들 (분석 결과 안전 접근용)
    average_comparison: Dict = {}
    category_comparisons: List = []
    badges_list: List = []
    ai_analysis_text: str = ""
    ai_suggestions: List = []
    ai_alternatives: List = []
    ai_emotional_message: str = ""

    # Helper 메서드들
    def get_average_comparison(self) -> Dict:
        """평균 비교 데이터 안전하게 가져오기"""
        if self.analysis_data and "total_comparison" in self.analysis_data:
            return self.analysis_data["total_comparison"]
        return {}

    def get_category_comparisons(self) -> List:
        """카테고리별 비교 데이터 안전하게 가져오기"""
        if self.analysis_data and "category_comparisons" in self.analysis_data:
            return self.analysis_data["category_comparisons"]
        return []

    def get_badges(self) -> List:
        """배지 데이터 안전하게 가져오기"""
        if self.analysis_data and "badges" in self.analysis_data:
            return self.analysis_data["badges"]
        return []

    def get_ai_analysis_text(self) -> str:
        """AI 분석 텍스트 안전하게 가져오기"""
        if self.ai_analysis:
            return self.ai_analysis.get("analysis", "분석 결과가 없습니다.")
        return "분석 결과가 없습니다."

    def get_ai_suggestions(self) -> List:
        """AI 제안 안전하게 가져오기"""
        if self.ai_analysis:
            return self.ai_analysis.get("suggestions", [])
        return []

    def get_ai_alternatives(self) -> List:
        """AI 대안 안전하게 가져오기"""
        if self.ai_analysis:
            return self.ai_analysis.get("alternatives", [])
        return []

    def get_ai_emotional_message(self) -> str:
        """AI 격려 메시지 안전하게 가져오기"""
        if self.ai_analysis:
            return self.ai_analysis.get("emotional_message", "격려 메시지가 없습니다.")
        return "격려 메시지가 없습니다."

    def toggle_activity(self, category: Any, activity: str):
        """활동 유형 토글 (중복 선택 지원)"""
        cat_str = str(category) if not isinstance(category, str) else category
        if cat_str not in self.selected_activities:
            self.selected_activities[cat_str] = []

        if activity in self.selected_activities[cat_str]:
            # 이미 선택된 경우 제거
            self.selected_activities[cat_str].remove(activity)
            # 해당 활동의 입력값도 제거
            if cat_str in self.activity_inputs and activity in self.activity_inputs[cat_str]:
                del self.activity_inputs[cat_str][activity]
        else:
            # 선택되지 않은 경우 추가
            self.selected_activities[cat_str].append(activity)
            # 해당 활동의 입력값 초기화
            if cat_str not in self.activity_inputs:
                self.activity_inputs[cat_str] = {}
            if activity not in self.activity_inputs[cat_str]:
                # 단위 목록 가져오기
                units: List[str] = []
                if cat_str in self.category_units_by_activity:
                    units = self.category_units_by_activity[cat_str].get(activity, [])
                self.activity_inputs[cat_str][activity] = {
                    "unit": units[0] if units else "",
                    "value": 0.0,
                    "sub_category": "",
                }

    def set_activity_unit(self, category: Any, activity: str, unit: str):
        """활동별 단위 설정"""
        cat_str = str(category) if not isinstance(category, str) else category
        if cat_str in self.activity_inputs and activity in self.activity_inputs[cat_str]:
            self.activity_inputs[cat_str][activity]["unit"] = unit

    def set_activity_value(self, category: Any, activity: str, value: str):
        """활동별 값 설정"""
        cat_str = str(category) if not isinstance(category, str) else category
        if cat_str in self.activity_inputs and activity in self.activity_inputs[cat_str]:
            try:
                self.activity_inputs[cat_str][activity]["value"] = float(value) if value else 0.0
            except (ValueError, TypeError):
                self.activity_inputs[cat_str][activity]["value"] = 0.0

    def set_activity_sub_category(self, category: Any, activity: str, sub_category: str):
        """활동별 하위 카테고리 설정"""
        cat_str = str(category) if not isinstance(category, str) else category
        if cat_str in self.activity_inputs and activity in self.activity_inputs[cat_str]:
            self.activity_inputs[cat_str][activity]["sub_category"] = sub_category

    def is_activity_selected(self, category: Any, activity: str) -> bool:
        """활동이 선택되었는지 확인"""
        cat_str = str(category) if not isinstance(category, str) else category
        if cat_str in self.selected_activities:
            return activity in self.selected_activities[cat_str]
        return False

    def clear_session(self):
        """세션 완전 초기화"""
        self.submitted = False
        self.all_activities = []
        self.analysis_data = None
        self.ai_analysis = None
        self.form_values = {}
        self.categories = []
        self.categories_data = {}
        self.category_activities = {}
        self.category_sub_categories = {}
        self.category_units_by_activity = {}
        self.selected_activities = {}
        self.activity_inputs = {}
        self.error_message = ""
        self.update_calculations()  # 계산값 초기화


# =========================
# UI 컴포넌트 (디자인 리팩터링)
# =========================


def index() -> rx.Component:
    """메인 페이지"""
    return rx.center(
        rx.container(
            rx.vstack(
                # 헤더 섹션
                rx.center(
                    rx.box(
                        rx.vstack(
                            rx.badge(
                                "Reflex · Carbon Coach",
                                color_scheme="green",
                                size="2",
                                border_radius="999px",
                                padding_x="0.9rem",
                                padding_y="0.25rem",
                                background="rgba(15, 118, 110, 0.08)",
                                color="#047857",
                            ),
                            rx.heading(
                                "🌍 탄소 발자국 계산기",
                                size="9",
                                margin_top="0.75rem",
                                margin_bottom="0.5rem",
                                color="#0f172a",
                                text_align="center",
                            ),
                            rx.text(
                                "하루의 활동을 입력하면 탄소 배출량을 계산하고, AI 코치가 맞춤형 저감 전략을 제안해 줍니다.",
                                size="4",
                                color="#4b5563",
                                text_align="center",
                                max_width="640px",
                            ),
                            rx.text(
                                "지금 바로 오늘 하루를 기록해 보세요. 작은 습관이 큰 변화를 만듭니다.",
                                size="3",
                                color="#6b7280",
                                text_align="center",
                                margin_top="0.75rem",
                            ),
                            spacing="3",
                            align="center",
                            width="100%",
                        ),
                        width="100%",
                        max_width="820px",
                        padding="2.75rem 1.75rem",
                        border_radius="1.5rem",
                        background="white",
                        box_shadow="0 18px 45px rgba(15, 23, 42, 0.08)",
                        border="1px solid rgba(148, 163, 184, 0.4)",
                        margin_top="2.5rem",
                        margin_bottom="2.5rem",
                    ),
                    width="100%",
                ),

                # 입력 or 결과 영역
                rx.center(
                    rx.cond(
                        State.submitted,
                        render_summary(),
                        render_input_form(),
                    ),
                    width="100%",
                ),

                spacing="6",
                width="100%",
                align="center",
                padding_bottom="3rem",
                on_mount=State.load_categories,
            ),
            max_width="900px",
            center_content=True,
            padding_x="1.25rem",
            width="100%",
        ),
        width="100%",
        min_height="100vh",
        padding_bottom="3rem",
    )




def render_input_form() -> rx.Component:
    """입력 폼 렌더링"""
    return rx.vstack(

        # 제목 영역
        rx.vstack(
            rx.heading(
                "📝 오늘의 활동 입력",
                size="7",
                margin_bottom="0.25rem",
                color="#111827",
                weight="bold",
                text_align="center",
                width="100%",
            ),
            rx.text(
                "각 카테고리에 대해 오늘 하루 동안의 활동을 입력해주세요. 여러 활동을 중복 선택할 수 있습니다.",
                size="3",
                color="#6b7280",
                margin_bottom="1.5rem",
                text_align="center",
                width="100%",
            ),
            spacing="1",
            width="100%",
        ),

        # 로딩
        rx.cond(
            State.loading_categories,
            rx.center(
                rx.vstack(
                    rx.spinner(size="3", color="#16a34a"),
                    rx.text("카테고리를 불러오는 중입니다...", color="#6b7280", size="3"),
                    spacing="2",
                ),
                padding_y="2rem",
            )
        ),

        # 에러 표시
        rx.cond(
            (State.error_message != "") & (~State.loading_categories),
            rx.center(
                rx.callout(
                    State.error_message,
                    icon="triangle_alert",
                    color_scheme="red",
                    margin_bottom="1rem",
                    max_width="600px",
                )
            ),
        ),

        # 카테고리 카드 리스트 (완전 가운데 정렬)
        rx.cond(
            State.categories.length() > 0,
            rx.vstack(
                rx.foreach(
                    State.categories,
                    lambda category: rx.center(
                        render_category_input(category),
                        width="100%",
                    )
                ),
                spacing="3",
                width="100%",
                align="center",
                margin_top="0.5rem",
            ),
        ),

        rx.divider(margin_y="1.5rem"),

        # 제출 버튼
        rx.center(
            rx.button(
                "📊 분석하기",
                on_click=State.submit_form,
                color_scheme="green",
                size="4",
                width="100%",
                max_width="560px",
                background="#22c55e",
                color="white",
                padding_y="1.1rem",
                border_radius="0.9rem",
            )
        ),

        spacing="3",
        width="100%",
        align="center",
    )




def render_category_input(category: rx.Var[str]) -> rx.Component:
    """카테고리별 입력 필드 (중복 선택 지원)"""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.heading(
                    category,
                    size="5",
                    margin_bottom="0.25rem",
                    color="#111827",
                    weight="bold",
                ),
                rx.spacer(),
                rx.badge("카테고리", size="1", color_scheme="gray", variant="soft"),
                width="100%",
                align="center",
            ),

            rx.text(
                "해당 카테고리에서 오늘 수행한 활동 유형을 선택하고 값을 입력하세요.",
                size="2",
                color="#6b7280",
                margin_bottom="0.75rem",
            ),

            render_activity_checkboxes(category),

            rx.cond(
                State.selected_activities[category].length() > 0,
                rx.vstack(
                    rx.divider(margin_y="0.5rem"),
                    rx.foreach(
                        State.selected_activities[category],
                        lambda activity: render_activity_input_row(category, activity),
                    ),
                    spacing="3",
                    width="100%",
                ),
            ),

            spacing="3",
            width="100%",
        ),

        width="100%",
        max_width="650px",
        padding="1.5rem",
        background="white",
        border_radius="1rem",
        box_shadow="0 10px 30px rgba(15, 23, 42, 0.04)",
        border="1px solid rgba(226, 232, 240, 0.9)",
    )




def render_activity_checkboxes(category: rx.Var[str]) -> rx.Component:
    """활동 유형 체크박스 (중복 선택 지원)"""
    return rx.vstack(
        rx.text(
            "활동 유형 선택 (중복 선택 가능):",
            size="2",
            margin_bottom="0.35rem",
            color="#374151",
            weight="medium",
        ),
        rx.vstack(
            rx.foreach(
                State.category_activities[category],
                lambda activity: render_activity_checkbox(category, activity),
            ),
            spacing="1",
            width="100%",
        ),
        spacing="1",
        width="100%",
    )


def render_activity_checkbox(category: rx.Var[str], activity: rx.Var[str]) -> rx.Component:
    """개별 활동 체크박스"""
    return rx.hstack(
        rx.checkbox(
            checked=State.selected_activities[category].contains(activity),
            on_change=lambda checked: State.toggle_activity(category, activity),
            size="2",
        ),
        rx.text(
            activity,
            size="3",
            color="#374151",
            white_space="normal",
            word_break="keep-all",
        ),
        align="center",
        spacing="2",
        width="100%",
    )


def render_activity_input_row(category: rx.Var[str], activity: rx.Var[str]) -> rx.Component:
    """선택된 활동별 입력 행"""
    return rx.card(
        rx.vstack(
            rx.heading(
                activity,
                size="4",
                margin_bottom="0.35rem",
                text_align="left",
                white_space="normal",
                color="#111827",
            ),
            # 하위 카테고리 (의류만)
            rx.cond(
                category == "의류",
                render_activity_sub_category_select(category, activity),
            ),
            # 단위 및 값 입력
            render_activity_unit_and_value(category, activity),
            spacing="2",
            width="100%",
        ),
        width="100%",
        padding="0.9rem 1rem",
        margin_bottom="0.4rem",
        border_radius="0.75rem",
        border="1px dashed rgba(209, 213, 219, 0.9)",
        background="#f9fafb",
    )


def render_activity_sub_category_select(
    category: rx.Var[str], activity: rx.Var[str]
) -> rx.Component:
    """활동별 하위 카테고리 셀렉트박스 (의류만)"""
    return rx.cond(
        State.category_sub_categories[category].length() > 0,
        rx.select(
            State.category_sub_categories[category],
            placeholder="하위 카테고리 선택 (새 제품 / 빈티지 등)",
            value=State.activity_inputs[category][activity]["sub_category"],
            on_change=lambda value: State.set_activity_sub_category(category, activity, value),
            width="100%",
            margin_bottom="0.4rem",
            size="2",
        ),
    )


def render_activity_unit_and_value(
    category: rx.Var[str], activity: rx.Var[str]
) -> rx.Component:
    """활동별 단위 및 값 입력"""
    return rx.hstack(
        render_activity_unit_select(category, activity),
        rx.input(
            type="number",
            placeholder="값 입력",
            value=str(State.activity_inputs[category][activity]["value"]),
            on_change=lambda value: State.set_activity_value(category, activity, value),
            width="65%",
            size="2",
        ),
        spacing="2",
        width="100%",
    )


def render_activity_unit_select(category: rx.Var[str], activity: rx.Var[str]) -> rx.Component:
    """활동별 단위 셀렉트박스"""
    return rx.select(
        State.category_units_by_activity[category][activity],
        placeholder="단위 선택",
        value=State.activity_inputs[category][activity]["unit"],
        on_change=lambda value: State.set_activity_unit(category, activity, value),
        width="35%",
        size="2",
    )


def render_summary() -> rx.Component:
    """요약 페이지 렌더링"""
    return rx.vstack(
        rx.hstack(
            rx.vstack(
                rx.heading("📊 분석 결과", size="7", color="#111827"),
                rx.text(
                    "오늘 입력한 활동을 기반으로 탄소 발자국과 AI 분석 결과를 정리했어요.",
                    size="3",
                    color="#6b7280",
                ),
                spacing="1",
            ),
            rx.spacer(),
            rx.button(
                "🔄 다시 입력하기",
                on_click=State.reset_form,
                color_scheme="gray",
                size="2",
                variant="soft",
                border_radius="999px",
            ),
            align="center",
            width="100%",
            margin_bottom="1.25rem",
        ),
        rx.cond(
            State.loading_analysis | State.loading_ai,
            rx.center(
                rx.vstack(
                    rx.spinner(size="3", color="#16a34a"),
                    rx.text(
                        "분석을 진행하고 있습니다... (상세 분석 및 AI 코치 실행 중)",
                        color="#6b7280",
                        size="3",
                    ),
                    spacing="2",
                    padding_y="1.5rem",
                ),
            ),
            rx.cond(
                # analysis_data가 있거나, total_carbon이 0보다 크거나, ai_analysis_text가 있으면 표시
                (State.analysis_data != None) | (State.total_carbon > 0) | (State.ai_analysis_text.length() > 0),
                render_analysis_results(),
                rx.text("데이터를 입력하고 제출해주세요.", color="#6b7280"),
            ),
        ),
        spacing="4",
        width="100%",
    )


def render_basic_summary() -> rx.Component:
    """기본 요약 정보"""
    return rx.vstack(
        rx.heading("📊 기본 정보", size="5", color="#111827"),
        rx.card(
            rx.hstack(
                rx.vstack(
                    rx.text(
                        "총 탄소 배출량",
                        size="2",
                        color="#6b7280",
                    ),
                    rx.text(
                        f"{State.total_carbon:.2f} kgCO₂e",
                        size="5",
                        weight="bold",
                        color="#111827",
                    ),
                    spacing="1",
                ),
                rx.spacer(),
                rx.vstack(
                    rx.text(
                        "활동 수",
                        size="2",
                        color="#6b7280",
                    ),
                    rx.text(
                        f"{State.all_activities.length()}개",
                        size="4",
                        color="#111827",
                        weight="medium",
                    ),
                    spacing="1",
                    align_items="flex-end",
                ),
                width="100%",
            ),
            width="100%",
            padding="1.25rem",
            border_radius="1rem",
            background="white",
            box_shadow="0 10px 30px rgba(15, 23, 42, 0.04)",
            border="1px solid rgba(226, 232, 240, 0.9)",
        ),
        spacing="2",
        width="100%",
    )


def render_ai_only_summary() -> rx.Component:
    """AI 분석만 있는 경우"""
    return rx.vstack(
        render_basic_summary(),
        rx.divider(margin_y="1rem"),
        rx.cond(
            State.ai_analysis != None,
            render_ai_analysis_result(),
        ),
        spacing="4",
        width="100%",
    )


def render_analysis_results() -> rx.Component:
    """분석 결과 렌더링 - State 변수 사용"""
    return summary.render_summary_page(
        total_carbon=State.total_carbon,
        category_breakdown=State.category_breakdown,
        average_comparison=State.average_comparison,
        category_comparisons=State.category_comparisons,
        badges=State.badges_list,
        ai_analysis=State.ai_analysis,
        ai_analysis_text=State.ai_analysis_text,
        ai_suggestions=State.ai_suggestions,
        ai_alternatives=State.ai_alternatives,
        ai_emotional_message=State.ai_emotional_message,
    )


def render_ai_analysis_result() -> rx.Component:
    """AI 분석 결과 표시 - State 변수 사용"""
    return rx.vstack(
        rx.heading("🤖 AI 분석 결과", size="5", color="#111827"),
        rx.card(
            rx.vstack(
                rx.heading("📊 분석 요약", size="4", color="#111827"),
                rx.text(State.ai_analysis_text, size="3", color="#374151"),
                rx.heading("💡 탄소 저감 제안", size="4", margin_top="1rem", color="#111827"),
                rx.cond(
                    State.ai_suggestions.length() > 0,
                    rx.vstack(
                        rx.foreach(
                            State.ai_suggestions,
                            lambda suggestion: rx.text(f"• {suggestion}", size="3"),
                        ),
                        spacing="1",
                        align="start",
                    ),
                    rx.text("제안이 없습니다.", size="3", color="#6b7280"),
                ),
                rx.heading("🌱 대안 행동", size="4", margin_top="1rem", color="#111827"),
                rx.cond(
                    State.ai_alternatives.length() > 0,
                    rx.vstack(
                        rx.foreach(
                            State.ai_alternatives,
                            lambda alt: rx.text(
                                f"• 현재: {alt.to(dict)['current']}  →  "
                                f"대안: {alt.to(dict)['alternative']}  "
                                f"({alt.to(dict)['impact']})",
                                size="3",
                            ),
                        ),
                        spacing="1",
                        align="start",
                    ),
                    rx.text("대안 행동이 없습니다.", size="3", color="#6b7280"),
                ),
                rx.heading("💬 격려 메시지", size="4", margin_top="1rem", color="#111827"),
                rx.callout(
                    State.ai_emotional_message,
                    icon="heart",
                    color_scheme="green",
                    variant="soft",
                ),
                spacing="3",
                width="100%",
            ),
            width="100%",
            padding="1.25rem",
            border_radius="1rem",
            background="white",
            box_shadow="0 10px 30px rgba(15, 23, 42, 0.04)",
            border="1px solid rgba(226, 232, 240, 0.9)",
        ),
        spacing="3",
        width="100%",
    )


# Reflex 앱 생성
app = rx.App()
app.add_page(index, route="/")
