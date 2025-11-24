"""
Streamlit 메인 애플리케이션
탄소 발자국 계산 및 시각화 플랫폼
"""

import streamlit as st
import httpx
from datetime import datetime
from typing import List, Dict

from components.summary import render_summary_page

# 페이지 설정
st.set_page_config(
    page_title="🌍 탄소 발자국 계산기",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Plotly 경고 억제
import warnings
warnings.filterwarnings('ignore')

# API 기본 URL
API_BASE_URL = "http://localhost:8000"

# 세션 상태 초기화
if 'submitted' not in st.session_state:
    st.session_state.submitted = False
if 'all_activities' not in st.session_state:
    st.session_state.all_activities = []
if 'analysis_data' not in st.session_state:
    st.session_state.analysis_data = None
if 'ai_analysis' not in st.session_state:
    st.session_state.ai_analysis = None


@st.cache_resource(ttl=3600)  # 1시간 캐싱 (API 연결 설정)
def get_http_client():
    """HTTP 클라이언트 생성 (리소스 캐싱)"""
    return httpx.Client(timeout=10.0)

@st.cache_data(ttl=300)  # 5분간 캐싱
def call_api_cached(endpoint: str, method: str = "GET", data: dict = None):
    """API 호출 헬퍼 함수 (캐싱 적용)"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        client = get_http_client()
        if method == "GET":
            response = client.get(url, timeout=5.0)
        elif method == "POST":
            response = client.post(url, json=data, timeout=10.0)
        response.raise_for_status()
        return response.json()
    except httpx.RequestError as e:
        st.error(f"API 연결 오류: {str(e)}")
        return None
    except httpx.HTTPStatusError as e:
        st.error(f"API 오류: {e.response.status_code} - {e.response.text}")
        return None


def call_api(endpoint: str, method: str = "GET", data: dict = None):
    """API 호출 헬퍼 함수 (POST 요청은 캐싱하지 않음)"""
    if method == "GET":
        return call_api_cached(endpoint, method, data)
    else:
        # POST 요청은 캐싱하지 않음
        try:
            url = f"{API_BASE_URL}{endpoint}"
            response = httpx.post(url, json=data, timeout=10.0)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            st.error(f"API 연결 오류: {str(e)}")
            return None
        except httpx.HTTPStatusError as e:
            error_text = e.response.text
            st.error(f"API 오류: {e.response.status_code} - {error_text[:200]}")
            # 디버깅: 응답 본문 확인
            try:
                error_json = e.response.json()
                st.json(error_json)
            except:
                pass
            return None


def calculate_activity(category: str, activity_type: str, value: float, unit: str, sub_category: str = None):
    """활동 탄소 계산"""
    if value <= 0:
        return None
    
    activity_data = {
        "category": category,
        "activity_type": activity_type,
        "value": value,
        "unit": unit,
        "sub_category": sub_category,
        "timestamp": datetime.now().isoformat()
    }
    
    result = call_api("/calculate", method="POST", data=activity_data)
    
    if result:
        return {
            **activity_data,
            "carbon_emission_kg": result["carbon_emission_kg"],
            "converted_value": result["converted_value"],
            "converted_unit": result["converted_unit"]
        }
    return None


# 메인 UI
st.title("🌍 탄소 발자국 계산기")
st.markdown("---")

# 카테고리 목록 가져오기 (캐싱 - 초기 로드 시에만)
@st.cache_data(ttl=3600)  # 1시간 캐싱
def load_categories():
    """카테고리 목록 로드 (캐싱)"""
    result = call_api("/categories")
    if not result:
        return []
    return result.get("categories", [])

categories = load_categories()
if not categories:
    st.error("API 연결에 실패했습니다. 백엔드 서버가 실행 중인지 확인해주세요.")
    st.stop()

# 제출 상태 확인 (먼저 체크하여 중복 렌더링 방지)
# 입력 폼
if not st.session_state.submitted:
    st.header("📝 오늘의 활동 입력")
    st.info("모든 카테고리에 대해 오늘 하루 동안의 활동을 입력해주세요.")
    
    # 카테고리 데이터 로드 (캐싱 적용)
    @st.cache_data(ttl=3600)  # 1시간 캐싱
    def load_category_data(category):
        """카테고리별 데이터 로드 (캐싱)"""
        activities_result = call_api(f"/categories/{category}/activities")
        activity_types = activities_result.get("activities", []) if activities_result else []
        
        sub_categories_result = call_api(f"/categories/{category}/sub_categories")
        sub_categories = sub_categories_result.get("sub_categories", []) if sub_categories_result else []
        
        # 각 활동 유형별 단위 미리 로드
        units_by_activity = {}
        for activity in activity_types:
            units_result = call_api(f"/categories/{category}/units?activity_type={activity}")
            if not units_result:
                units_result = call_api(f"/categories/{category}/units")
            units = units_result.get("units", []) if units_result else []
            units_by_activity[activity] = units
        
        return {
            "activities": activity_types,
            "sub_categories": sub_categories,
            "units_by_activity": units_by_activity
        }
    
    # 카테고리 데이터 로드 (캐싱된 함수 사용)
    categories_data = {}
    for category in categories:
        categories_data[category] = load_category_data(category)
    
    with st.form("carbon_form", clear_on_submit=False):
        # 각 카테고리별 입력 폼
        for category in categories:
            cat_data = categories_data.get(category)
            if not cat_data:
                st.warning(f"{category} 카테고리 데이터를 불러올 수 없습니다.")
                continue
                
            activity_types = cat_data["activities"]
            sub_categories = cat_data["sub_categories"]
            
            if not activity_types:
                st.warning(f"{category} 카테고리의 활동 유형을 불러올 수 없습니다.")
                continue
            
            st.markdown(f"### {category}")
            
            # 활동 유형 선택
            selected_activity = st.selectbox(
                f"{category} 활동 유형",
                activity_types,
                key=f"activity_{category}"
            )
            
            # 하위 카테고리 선택 (있는 경우)
            selected_sub_category = None
            if sub_categories:
                selected_sub_category = st.selectbox(
                    f"{category} 하위 카테고리",
                    sub_categories,
                    key=f"sub_{category}"
                )
            
            # 활동 유형에 따른 단위 가져오기 (미리 로드된 데이터만 사용, API 호출 없음)
            units = cat_data["units_by_activity"].get(selected_activity, [])
            
            if not units:
                st.warning(f"{category}의 단위를 가져올 수 없습니다.")
                # continue 대신 빈 입력 필드 표시
                st.text_input("값", value="", key=f"value_{category}", disabled=True)
                continue
            
            # 입력 필드
            col1, col2 = st.columns([1, 2])
            
            with col1:
                selected_unit = st.selectbox(
                    "단위",
                    units,
                    key=f"unit_{category}"
                )
            
            with col2:
                # 단위에 따른 입력 라벨
                if category == "물":
                    if selected_activity == "샤워":
                        if selected_unit == "회":
                            label = "샤워 횟수"
                        else:
                            label = "샤워 시간(분)"
                    elif selected_activity == "설거지":
                        label = "설거지 횟수"
                    elif selected_activity == "세탁":
                        label = "세탁 횟수"
                    else:
                        label = "값"
                elif category == "식품" and selected_unit == "1회 식사":
                    label = "식사 횟수"
                elif category == "의류":
                    label = "개수"
                else:
                    label = "값"
                
                value = st.number_input(
                    label,
                    min_value=0.0,
                    step=0.1,
                    format="%.2f",
                    key=f"value_{category}"
                )
        
        st.markdown("---")
        
        # 제출 버튼
        submitted = st.form_submit_button("📊 분석하기", type="primary", use_container_width=True)
        
        # 폼 안에서 제출 처리 (Streamlit 폼 특성상 폼 안에서 처리해야 함)
        if submitted:
            # 제출 시점에 모든 활동 계산 (세션 상태에서 값 가져오기)
            all_activities_data = []
            for category in categories:
                activity_key = f"activity_{category}"
                unit_key = f"unit_{category}"
                value_key = f"value_{category}"
                sub_key = f"sub_{category}"
                
                # 세션 상태에서 값 가져오기
                if activity_key in st.session_state and value_key in st.session_state and unit_key in st.session_state:
                    selected_activity = st.session_state[activity_key]
                    selected_unit = st.session_state[unit_key]
                    value = st.session_state[value_key]
                    selected_sub_category = st.session_state.get(sub_key, None)
                    
                    if value and value > 0 and selected_activity and selected_unit:
                        activity_result = calculate_activity(
                            category, 
                            selected_activity, 
                            value, 
                            selected_unit, 
                            selected_sub_category
                        )
                        if activity_result:
                            all_activities_data.append(activity_result)
            
            if len(all_activities_data) == 0:
                st.warning("최소 하나 이상의 활동을 입력해주세요!")
            else:
                st.session_state.all_activities = all_activities_data
                st.session_state.submitted = True
                st.rerun()

# 요약 페이지
else:
    # 데이터 계산 (로컬 계산만, API 호출 없음)
    total_carbon = sum(a["carbon_emission_kg"] for a in st.session_state.all_activities)
    
    # 카테고리별 집계 (로컬 계산만)
    category_breakdown = {}
    for act in st.session_state.all_activities:
        cat = act["category"]
        category_breakdown[cat] = category_breakdown.get(cat, 0) + act["carbon_emission_kg"]
    
    # API 호출은 버튼 클릭 시에만 실행
    if 'analysis_data' not in st.session_state:
        st.session_state.analysis_data = None
    if 'ai_analysis' not in st.session_state:
        st.session_state.ai_analysis = None
    
    # 분석 실행 버튼
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("📊 상세 분석 실행", use_container_width=True, type="primary"):
            with st.spinner("📊 분석 중..."):
                # 전체 평균 비교
                total_avg_result = call_api("/average")
                total_average = total_avg_result.get("total_average", 10.0) if total_avg_result else 10.0
                
                total_comparison = call_api("/compare", method="POST", data={"total": total_carbon})
                
                # 카테고리별 평균 비교
                category_comparisons = []
                for category in categories:
                    user_emission = category_breakdown.get(category, 0)
                    comp_result = call_api("/compare", method="POST", data={
                        "category": category,
                        "emission": user_emission
                    })
                    if comp_result:
                        category_comparisons.append(comp_result)
                    else:
                        category_comparisons.append({
                            "user_emission": user_emission,
                            "average_emission": 0,
                            "difference": 0,
                            "percentage": 0,
                            "is_better": True,
                            "category": category
                        })
                
                # 배지 확인
                badges_result = call_api("/badges/check", method="POST", data=st.session_state.all_activities)
                badges = badges_result.get("badges", []) if badges_result else []
                
                # 평균 비교 기반 추가 배지
                if total_comparison and total_comparison.get("is_better", False):
                    diff_pct = abs(total_comparison.get("percentage", 0))
                    if diff_pct >= 30:
                        badges.append({
                            "id": "eco_hero",
                            "name": "에코 히어로",
                            "description": f"평균보다 {diff_pct:.1f}% 적게 배출하셨어요!",
                            "icon": "🦸",
                            "earned_date": datetime.now().isoformat()
                        })
                    elif diff_pct >= 20:
                        badges.append({
                            "id": "eco_friend",
                            "name": "환경 친구",
                            "description": f"평균보다 {diff_pct:.1f}% 적게 배출하셨어요!",
                            "icon": "🌿",
                            "earned_date": datetime.now().isoformat()
                        })
                
                st.session_state.analysis_data = {
                    "total_average": total_average,
                    "total_comparison": total_comparison,
                    "category_comparisons": category_comparisons,
                    "badges": badges
                }
                st.rerun()
    
    with col2:
        if st.button("🤖 AI 분석 실행", use_container_width=True, type="secondary"):
            with st.spinner("🤖 AI가 분석 중입니다..."):
                coach_request = {
                    "activities": st.session_state.all_activities,
                    "total_carbon": total_carbon,
                    "category_breakdown": category_breakdown
                }
                try:
                    ai_result = call_api("/coach", method="POST", data=coach_request)
                    # 디버깅: 응답 확인
                    if ai_result:
                        if isinstance(ai_result, dict):
                            # 세션 상태에 저장
                            st.session_state.ai_analysis = ai_result
                            st.success("✅ AI 분석이 완료되었습니다!")
                            # 디버깅 정보 표시
                            st.write("🔍 응답 키:", list(ai_result.keys()) if isinstance(ai_result, dict) else "N/A")
                            # 즉시 표시를 위해 rerun
                            st.rerun()
                        else:
                            st.error(f"❌ 예상하지 못한 응답 형식: {type(ai_result)}")
                            st.json(ai_result)
                            st.session_state.ai_analysis = None
                    else:
                        st.error("❌ AI 분석 결과를 받을 수 없습니다. (응답이 None입니다)")
                        st.session_state.ai_analysis = None
                except Exception as e:
                    st.error(f"❌ AI 분석 중 오류가 발생했습니다: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
                    st.session_state.ai_analysis = None
    
    # 기본 정보 표시 (API 호출 없음)
    if not st.session_state.analysis_data and not st.session_state.ai_analysis:
        st.info("💡 위 버튼을 클릭하여 상세 분석과 AI 분석을 실행하세요.")
    
    # 분석 데이터가 있으면 표시
    if st.session_state.analysis_data:
        analysis_data = st.session_state.analysis_data
        render_summary_page(
            total_carbon=total_carbon,
            category_breakdown=category_breakdown,
            average_comparison=analysis_data["total_comparison"] or {
                "user_emission": total_carbon,
                "average_emission": analysis_data["total_average"],
                "difference": total_carbon - analysis_data["total_average"],
                "percentage": ((total_carbon - analysis_data["total_average"]) / analysis_data["total_average"] * 100) if analysis_data["total_average"] > 0 else 0,
                "is_better": total_carbon < analysis_data["total_average"]
            },
            category_comparisons=analysis_data["category_comparisons"],
            badges=analysis_data["badges"],
            ai_analysis=st.session_state.ai_analysis
        )
    elif st.session_state.ai_analysis:
        # AI 분석만 있는 경우 (상세 분석 없이)
        st.header("📊 탄소 배출 요약")
        st.metric("총 탄소 배출량", f"{total_carbon:.3f} kgCO₂e")
        
        st.subheader("카테고리별 배출량")
        for cat, amount in category_breakdown.items():
            st.write(f"- **{cat}**: {amount:.3f} kgCO₂e")
        
        st.markdown("---")
        
        # AI 분석 결과 표시
        ai_analysis = st.session_state.ai_analysis
        if ai_analysis and isinstance(ai_analysis, dict):
            st.subheader("🤖 AI 분석 결과")
            
            # 디버깅: AI 분석 데이터 확인
            with st.expander("🔍 디버깅 정보 보기"):
                st.json(ai_analysis)
                st.write(f"데이터 타입: {type(ai_analysis)}")
                st.write(f"키 목록: {list(ai_analysis.keys()) if isinstance(ai_analysis, dict) else 'N/A'}")
            
            st.markdown("### 📊 분석")
            analysis_text = ai_analysis.get("analysis", "")
            if analysis_text:
                st.info(analysis_text)
            else:
                st.warning("분석 결과가 없습니다.")
            
            st.markdown("### 💡 탄소 저감 제안")
            suggestions = ai_analysis.get("suggestions", [])
            if suggestions and len(suggestions) > 0:
                for idx, suggestion in enumerate(suggestions, 1):
                    st.markdown(f"{idx}. {suggestion}")
            else:
                st.info("제안이 없습니다.")
            
            st.markdown("### 🌱 대안 행동")
            alternatives = ai_analysis.get("alternative_actions", [])
            if alternatives and len(alternatives) > 0:
                for alt in alternatives:
                    st.markdown(f"""
                    - **현재**: {alt.get('current', '')}  
                      **대안**: {alt.get('alternative', '')}  
                      **효과**: {alt.get('impact', '')}
                    """)
            else:
                st.info("대안 행동이 없습니다.")
            
            st.markdown("### 💬 격려 메시지")
            emotional_message = ai_analysis.get("emotional_message", "")
            if emotional_message:
                st.success(emotional_message)
            else:
                st.info("격려 메시지가 없습니다.")
        else:
            st.warning(f"AI 분석 데이터가 없거나 형식이 올바르지 않습니다. 타입: {type(ai_analysis)}")
            if ai_analysis:
                st.json(ai_analysis)
    else:
        # 기본 요약만 표시 (API 호출 없음)
        st.header("📊 탄소 배출 요약")
        st.metric("총 탄소 배출량", f"{total_carbon:.3f} kgCO₂e")
        
        st.subheader("카테고리별 배출량")
        for cat, amount in category_breakdown.items():
            st.write(f"- **{cat}**: {amount:.3f} kgCO₂e")
    
    # 다시 입력하기 버튼
    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🔄 다시 입력하기", use_container_width=True):
            # 세션 상태 초기화
            st.session_state.submitted = False
            st.session_state.all_activities = []
            st.session_state.analysis_data = None
            st.session_state.ai_analysis = None
            # 입력 필드 초기화
            for category in categories:
                activity_key = f"activity_{category}"
                unit_key = f"unit_{category}"
                value_key = f"value_{category}"
                sub_key = f"sub_{category}"
                if activity_key in st.session_state:
                    del st.session_state[activity_key]
                if unit_key in st.session_state:
                    del st.session_state[unit_key]
                if value_key in st.session_state:
                    del st.session_state[value_key]
                if sub_key in st.session_state:
                    del st.session_state[sub_key]
            st.rerun()
    with col2:
        if st.button("🗑️ 세션 초기화", use_container_width=True, help="모든 캐시와 입력값을 초기화합니다"):
            # 모든 세션 상태 완전 초기화
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

# 푸터
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🌍 작은 실천이 큰 변화를 만듭니다 🌱</p>
    <p>탄소 발자국 계산기 v1.0.0</p>
</div>
""", unsafe_allow_html=True)
