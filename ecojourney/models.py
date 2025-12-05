import reflex as rx
from datetime import datetime, date
from typing import Optional, Dict, List, Any
import json

# -----------------------------------------------------------------------------
# 1. 사용자 (User)
# -----------------------------------------------------------------------------
class User(rx.Model, table=True):
    """
    사용자 정보를 저장하는 테이블
    - student_id: 로그인 ID이자 고유 식별자 (Primary Key)
    - college: 대항전 매칭을 위한 소속 단과대
    - current_points: 베팅 및 마일리지 환산에 사용할 잔액
    """
    # Primary Key는 필드 이름이 id이거나 첫 번째 필드로 정의
    student_id: str  # Primary Key로 사용 (Reflex가 자동 처리)
    password: str
    college: str
    current_points: int = 0
    created_at: datetime = datetime.now()

# -----------------------------------------------------------------------------
# 2. 탄소 배출 기록 (Carbon Log & AI Analysis)
# -----------------------------------------------------------------------------
class CarbonLog(rx.Model, table=True):
    """
    일일 행동 데이터와 계산된 탄소 배출량, AI 피드백 저장
    """
    student_id: str  # User 테이블 참조 (수동 조인)
    log_date: date = date.today()
    
    # 입력 데이터 (간단한 예시 필드 - 필요시 확장 가능)
    transport_km: float = 0.0
    cup_count: int = 0
    ac_hours: float = 0.0
    
    # 상세 입력 데이터 (JSON 형태로 저장)
    # 교통, 의류, 식품, 쓰레기, 전기, 물 등 모든 입력 데이터를 JSON으로 저장
    activities_json: str = "[]"  # JSON 문자열로 저장 (all_activities 리스트)
    
    # 계산 결과
    total_emission: float = 0.0  # 단위: kgCO2eq
    
    # 포인트 지급 내역
    points_earned: int = 0  # 해당 날짜에 획득한 포인트
    
    # AI 분석 결과 (Gemini)
    ai_feedback: Optional[str] = None
    created_at: datetime = datetime.now()
    
    def get_activities(self) -> List[Dict[str, Any]]:
        """JSON 문자열을 파싱하여 활동 리스트 반환"""
        try:
            if not self.activities_json or self.activities_json.strip() == "":
                return []
            
            # JSON 파싱 시도
            parsed = json.loads(self.activities_json)
            
            # 파싱 결과가 리스트인지 확인
            if isinstance(parsed, list):
                # 리스트의 각 항목이 딕셔너리인지 확인
                return [item for item in parsed if isinstance(item, dict)]
            elif isinstance(parsed, dict):
                # 딕셔너리 하나면 리스트로 감싸서 반환
                return [parsed]
            else:
                # 다른 타입이면 빈 리스트 반환
                return []
        except json.JSONDecodeError as e:
            # JSON 파싱 실패 시 빈 리스트 반환
            return []
        except Exception as e:
            # 기타 오류 시 빈 리스트 반환
            return []
    
    def set_activities(self, activities: List[Dict[str, Any]]):
        """활동 리스트를 JSON 문자열로 저장"""
        self.activities_json = json.dumps(activities, ensure_ascii=False, default=str)

# -----------------------------------------------------------------------------
# 3. 단과대 대항전 (Battle System)
# -----------------------------------------------------------------------------
class Battle(rx.Model, table=True):
    """
    매주 월요일 생성되는 단과대 1:1 매칭 정보
    """
    # Primary Key는 Reflex가 자동으로 생성하지만, 명시적으로 id를 추가할 수도 있음
    # id: int = rx.Field(primary_key=True)  # 필요시 주석 해제
    
    start_date: date
    end_date: date
    
    college_a: str
    college_b: str
    
    score_a: int = 0  # A팀 실시간 점수 합계
    score_b: int = 0  # B팀 실시간 점수 합계
    
    winner: Optional[str] = None  # 승리한 단과대 코드
    status: str = "ACTIVE"  # 상태: 'READY', 'ACTIVE', 'FINISHED'
    created_at: datetime = datetime.now()

class BattleParticipant(rx.Model, table=True):
    """
    대항전 참가 및 베팅 내역 (승자 독식 로직용)
    """
    battle_id: int  # Battle 테이블 ID 참조
    student_id: str  # User 테이블 ID 참조
    
    bet_amount: int = 0      # 참가비 (내가 건 포인트)
    reward_amount: int = 0   # 승리 시 획득한 상금 (패배 시 0)
    joined_at: datetime = datetime.now()

# -----------------------------------------------------------------------------
# 4. 마일리지 환산 (Mileage Request)
# -----------------------------------------------------------------------------
class MileageRequest(rx.Model, table=True):
    """
    앱 내 포인트를 학교 BeCome 마일리지로 환산 신청한 내역
    """
    student_id: str
    request_points: int        # 차감할 포인트
    converted_mileage: int     # 실제 적립될 마일리지
    status: str = "APPROVED"   # 테스트용 자동 승인: 'PENDING', 'APPROVED', 'REJECTED'
    processed_at: datetime = datetime.now()

# -----------------------------------------------------------------------------
# 5. 챌린지 및 진행도 (Challenge System)
# -----------------------------------------------------------------------------
class Challenge(rx.Model, table=True):
    """
    주간 미션 마스터 데이터 (관리자가 생성하거나 미리 넣어둠)
    """
    # Primary Key는 Reflex가 자동으로 생성하지만, 명시적으로 id를 추가할 수도 있음
    # id: int = rx.Field(primary_key=True)  # 필요시 주석 해제
    
    title: str       # 예: "7일 연속 기록하기"
    type: str        # 예: 'STREAK', 'VIEW', 'SAVE'
    goal_value: int  # 예: 7
    reward_points: int = 500
    is_active: bool = True  # 챌린지 활성화 여부
    created_at: datetime = datetime.now()

class ChallengeProgress(rx.Model, table=True):
    """
    개인별 챌린지 달성 현황
    """
    challenge_id: int
    student_id: str
    
    current_value: int = 0     # 현재 달성치
    is_completed: bool = False # 보상 지급 여부
    completed_at: Optional[datetime] = None  # 완료 시점
    last_updated: datetime = datetime.now()