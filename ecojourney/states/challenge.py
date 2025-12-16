"""
챌린지 시스템 관련 State
"""

import reflex as rx
from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
import logging
import random
from .mileage import MileageState
from ..models import Challenge, ChallengeProgress, User

logger = logging.getLogger(__name__)


class ChallengeState(MileageState):
    """
    챌린지 시스템 관련 상태 및 로직
    """
    active_challenges: List[Dict[str, Any]] = []
    user_challenge_progress: List[Dict[str, Any]] = []
    challenge_message: str = ""
    daily_info_title: str = ""
    daily_info_body: str = ""
    daily_quiz_question: str = ""
    daily_quiz_answer: str = ""
    daily_content_date: Optional[date] = None
    
    # 탄소 통계 개별 변수 (Reflex에서 Dict 접근 제한 때문에 분리)
    carbon_total_logs: int = 0
    carbon_total_emission: float = 0.0
    carbon_average_daily_emission: float = 0.0
    carbon_total_activities: int = 0
    carbon_category_breakdown: List[Dict[str, Any]] = []
    
    # 대시보드 통계 변수
    weekly_emission: float = 0.0  # 이번주 총 배출량
    monthly_emission: float = 0.0  # 한달 총 배출량
    weekly_daily_data: List[Dict[str, Any]] = []  # 이번주 일별 배출량 데이터
    monthly_daily_data: List[Dict[str, Any]] = []  # 한달 일별 배출량 데이터
    
    def ensure_default_challenges(self):
        """필수 기본 챌린지(주간/일일) 생성"""
        try:
            from sqlmodel import Session, create_engine, select
            import os

            db_path = os.path.join(os.getcwd(), "reflex.db")
            db_url = f"sqlite:///{db_path}"
            engine = create_engine(db_url, echo=False)

            # 보상/목표 기본값 정의
            default_challenges = [
                {"title": "7일 연속 기록", "type": "WEEKLY_STREAK", "goal_value": 7, "reward_points": 10},
                {"title": "아티클 읽기", "type": "DAILY_INFO", "goal_value": 1, "reward_points": 1},
                {"title": "OX 퀴즈 풀기", "type": "DAILY_QUIZ", "goal_value": 1, "reward_points": 1},
            ]

            with Session(engine) as session:
                titles = [item["title"] for item in default_challenges]
                existing = session.exec(select(Challenge).where(Challenge.title.in_(titles))).all()
                existing_map = {c.title: c for c in existing}

                created = 0
                for item in default_challenges:
                    existing_ch = existing_map.get(item["title"])
                    if existing_ch:
                        updated = False
                        if existing_ch.reward_points != item["reward_points"]:
                            existing_ch.reward_points = item["reward_points"]
                            updated = True
                        if existing_ch.goal_value != item["goal_value"]:
                            existing_ch.goal_value = item["goal_value"]
                            updated = True
                        if existing_ch.type != item["type"]:
                            existing_ch.type = item["type"]
                            updated = True
                        if updated:
                            session.add(existing_ch)
                            created += 1  # reuse counter for commit trigger
                    else:
                        ch = Challenge(
                            title=item["title"],
                            type=item["type"],
                            goal_value=item["goal_value"],
                            reward_points=item["reward_points"],
                            is_active=True,
                            created_at=datetime.now()
                        )
                        session.add(ch)
                        created += 1
                if created:
                    session.commit()
        except Exception as e:
            logger.error(f"기본 챌린지 생성 오류: {e}", exc_info=True)

    def load_active_challenges(self):
        """활성화된 챌린지 목록 로드"""
        try:
            self.ensure_default_challenges()

            from sqlmodel import Session, create_engine, select
            import os
            
            # SQLModel Session을 직접 사용하여 조회
            db_path = os.path.join(os.getcwd(), "reflex.db")
            db_url = f"sqlite:///{db_path}"
            engine = create_engine(db_url, echo=False)
            
            challenges = []
            with Session(engine) as session:
                statement = select(Challenge).where(Challenge.is_active == True)
                challenges = list(session.exec(statement).all())
            
            self.active_challenges = [
                {
                    "id": ch.id,
                    "title": ch.title,
                    "type": ch.type,
                    "goal_value": ch.goal_value,
                    "reward_points": ch.reward_points
                }
                for ch in challenges
            ]
        except Exception as e:
            logger.error(f"챌린지 로드 오류: {e}", exc_info=True)

    async def load_daily_content(self):
        """매일 하나의 정보글과 OX 퀴즈를 날짜 기반 랜덤으로 선택"""
        today = date.today()
        if self.daily_content_date == today and self.daily_info_title and self.daily_quiz_question:
            return

        info_items = [
            {
                "title": "해양 플라스틱 오염",
                "body": "전 세계 바다에는 이미 1억 5천만 톤의 플라스틱이 떠다니고 있고, 매년 800만 톤 이상이 새로 유입됩니다.",
            },
            {
                "title": "미세플라스틱의 역습",
                "body": "우리는 일주일마다 신용카드 한 장 무게만큼 미세플라스틱을 섭취하고 있습니다.",
            },
            {
                "title": "음식물 쓰레기와 메탄",
                "body": "음식물 쓰레기는 매립되면 CO₂보다 28배 강한 메탄가스를 배출합니다.",
            },
            {
                "title": "패스트패션의 그림자",
                "body": "패스트패션은 전 세계 탄소 배출의 10% 이상을 차지하며, 옷 한 벌에 수천 리터의 물이 쓰입니다.",
            },
            {
                "title": "자동차 배출량",
                "body": "자동차는 1km 이동할 때 약 120~200g CO₂를 배출합니다.",
            },
            {
                "title": "지구 온난화 현실",
                "body": "산업혁명 이후 지구 평균기온은 약 1.1℃ 상승했고, 이 변화가 폭염·폭우·산불을 더 자주 만듭니다.",
            },
            {
                "title": "전기의 탄소 발자국",
                "body": "우리가 쓰는 전기의 상당수는 여전히 화석연료 발전소에서 생산됩니다.",
            },
            {
                "title": "뜨거운 물 사용의 비용",
                "body": "뜨거운 물 1분 사용은 약 1.3kg CO₂ 배출과 비슷한 에너지를 소비합니다.",
            },
            {
                "title": "쓰레기 매립지의 한계",
                "body": "전 세계 주요 도시의 매립지는 포화 상태이며, 쓰레기는 더 이상 ‘버리면 끝’이 아닙니다.",
            },
            {
                "title": "소고기의 탄소 발자국",
                "body": "소고기 1kg 생산은 약 27kg CO₂를 배출해 자동차로 113km 주행한 것과 비슷합니다.",
            },
        ]

        quiz_items = [
            {"q": "물은 받을 때보다 틀어놓을 때가 더 많이 낭비된다.", "a": "O"},
            {"q": "사용하지 않는 전등을 끄는 것만으로도 탄소를 줄일 수 있다.", "a": "O"},
            {"q": "플라스틱을 재활용하면 새로 만드는 것보다 에너지가 더 든다.", "a": "X"},
            {"q": "가까운 거리를 걸어가면 탄소 배출을 줄일 수 있다.", "a": "O"},
            {"q": "음식물을 남겨도 환경에 큰 영향은 없다.", "a": "X"},
            {"q": "엘리베이터 대신 계단을 이용하면 탄소 배출을 줄일 수 있다.", "a": "O"},
            {"q": "샤워 시간을 조금만 줄여도 탄소가 줄어든다.", "a": "O"},
            {"q": "텀블러를 쓰는 것보다 일회용 컵을 쓰는 것이 환경에 더 좋다.", "a": "X"},
            {"q": "재활용은 분리만 잘하면 누구나 쉽게 실천할 수 있다.", "a": "O"},
            {"q": "방을 환기할 때는 잠깐 열어두는 것이 에너지 낭비를 줄인다.", "a": "O"},
            {"q": "에어컨 온도를 1℃만 올려도 전기 사용량이 줄어든다.", "a": "O"},
            {"q": "자동차 혼자 타는 것보다 함께 타는 것이 탄소 배출을 줄인다.", "a": "O"},
            {"q": "배달 음식을 시키는 것은 환경에 전혀 영향이 없다.", "a": "X"},
            {"q": "분리배출할 때 라벨이나 내용물을 제거하는 것이 재활용률을 높인다.", "a": "O"},
            {"q": "물을 데우는 것보다 찬물 사용이 탄소 배출을 줄인다.", "a": "O"},
        ]

        seed_val = today.toordinal()
        rng = random.Random(seed_val)
        info = rng.choice(info_items)
        quiz = rng.choice(quiz_items)

        self.daily_info_title = info["title"]
        self.daily_info_body = info["body"]
        self.daily_quiz_question = quiz["q"]
        self.daily_quiz_answer = quiz["a"]
        self.daily_content_date = today
    
    async def update_challenge_progress(self, challenge_id: int, increment: int = 1):
        """챌린지 진행도 업데이트 (일일/주간 리셋 포함)"""
        print(f"[챌린지 진행도] update_challenge_progress 호출됨, challenge_id: {challenge_id}, increment: {increment}")
        logger.info(f"[챌린지 진행도] update_challenge_progress 호출됨, challenge_id: {challenge_id}, increment: {increment}")
        
        if not self.is_logged_in:
            print("[챌린지 진행도] 로그인되지 않음, 종료")
            return
        
        try:
            from sqlmodel import Session, create_engine, select
            import os

            db_path = os.path.join(os.getcwd(), "reflex.db")
            db_url = f"sqlite:///{db_path}"
            engine = create_engine(db_url, echo=False)

            today = date.today()
            this_monday = today - timedelta(days=today.weekday())
            print(f"[챌린지 진행도] 오늘: {today}, 이번 주 월요일: {this_monday}")

            with Session(engine) as session:
                # 챌린지 조회
                challenge = session.exec(
                    select(Challenge).where(Challenge.id == challenge_id)
                ).first()
                if not challenge:
                    print(f"[챌린지 진행도] 챌린지 ID {challenge_id}를 찾을 수 없음")
                    return
                
                print(f"[챌린지 진행도] 챌린지 찾음: {challenge.title} (타입: {challenge.type})")

                # 진행도 조회 또는 생성
                progress = session.exec(
                    select(ChallengeProgress).where(
                        ChallengeProgress.challenge_id == challenge_id,
                        ChallengeProgress.student_id == self.current_user_id
                    )
                ).first()
                
                is_new_progress = False
                if not progress:
                    is_new_progress = True
                    progress = ChallengeProgress(
                        challenge_id=challenge_id,
                        student_id=self.current_user_id,
                        current_value=0,
                        is_completed=False,
                        last_updated=datetime.now() - timedelta(days=1),  # 어제로 설정하여 첫 기록 가능하도록
                    )

                # last_updated가 없거나 None이면 강제로 초기화 (오래된 날짜로 설정해 첫 기록이 가능하도록)
                last_updated_date = progress.last_updated.date() if progress.last_updated else None
                if last_updated_date is None:
                    last_updated_date = (datetime.now() - timedelta(days=1)).date()
                    progress.last_updated = datetime.combine(last_updated_date, datetime.min.time())

                # 일일 챌린지는 날짜가 바뀌면 리셋
                if challenge.type in ["DAILY_INFO", "DAILY_QUIZ"]:
                    if last_updated_date != today:
                        progress.current_value = 0
                        progress.is_completed = False
                        progress.completed_at = None

                # 주간 챌린지는 주가 바뀌면 리셋
                if challenge.type == "WEEKLY_STREAK":
                    print(f"[주간 챌린지] 진행도 체크 - last_updated_date: {last_updated_date}, this_monday: {this_monday}, today: {today}, is_new_progress: {is_new_progress}")
                    if last_updated_date < this_monday:
                        print(f"[주간 챌린지] 주가 바뀜, 진행도 리셋 (기존: {progress.current_value})")
                        progress.current_value = 0
                        progress.is_completed = False
                        progress.completed_at = None
                    # 같은 날 이미 기록했으면 진행도 증가하지 않음 (하루에 한 번만 카운트)
                    # 단, 새로 생성된 진행도는 제외 (is_new_progress가 True이면 진행도 증가)
                    elif not is_new_progress and last_updated_date == today:
                        print(f"[주간 챌린지] 오늘 이미 기록됨 (진행도: {progress.current_value}), 업데이트 건너뜀")
                        logger.info(f"주간 챌린지: 오늘 이미 기록됨 (진행도: {progress.current_value})")
                        return
                    else:
                        print(f"[주간 챌린지] 진행도 업데이트 가능 (last_updated_date: {last_updated_date}, today: {today})")

                # 이미 완료된 챌린지는 업데이트하지 않음
                if progress.is_completed:
                    return

                # 진행도 업데이트
                old_value = progress.current_value
                progress.current_value += increment
                progress.last_updated = datetime.now()
                print(f"[챌린지 진행도] 진행도 업데이트: {old_value} -> {progress.current_value} (목표: {challenge.goal_value})")
                logger.info(f"챌린지 진행도 업데이트: {challenge.title}, 진행도: {progress.current_value}/{challenge.goal_value}")

                # 챌린지 목표 달성 확인
                if progress.current_value >= challenge.goal_value:
                    progress.is_completed = True
                    progress.completed_at = datetime.now()
                    
                    # 보상 지급
                    user = session.exec(
                        select(User).where(User.student_id == self.current_user_id)
                    ).first()
                    if user:
                        user.current_points += challenge.reward_points
                        self.current_user_points = user.current_points
                        session.add(user)
                    
                    # 포인트 로그 기록 (챌린지 출처)
                    try:
                        from ..models import CarbonLog
                        log_entry = CarbonLog(
                            student_id=self.current_user_id,
                            log_date=today,
                            total_emission=0.0,
                            activities_json="[]",
                            points_earned=challenge.reward_points,
                            source="challenge",
                            ai_feedback=f"챌린지 보상: {challenge.title}",
                            created_at=datetime.now()
                        )
                        session.add(log_entry)
                    except Exception as log_error:
                        logger.error(f"챌린지 포인트 로그 생성 오류: {log_error}", exc_info=True)
                    
                    logger.info(f"챌린지 완료: {self.current_user_id}, 챌린지: {challenge.title}, 보상: {challenge.reward_points}")

                # 진행도 저장 (세션 커밋)
                session.add(progress)
                session.commit()
                session.refresh(progress)

        except Exception as e:
            logger.error(f"챌린지 진행도 업데이트 오류: {e}")
    
    def load_user_challenge_progress(self):
        """사용자의 챌린지 진행도 로드"""
        if not self.is_logged_in or not self.current_user_id:
            self.user_challenge_progress = []
            return

        try:
            # 활성화된 챌린지 로드
            self.load_active_challenges()
            
            # 사용자의 진행도 조회 (SQLModel Session 직접 사용)
            from sqlmodel import Session, create_engine, select
            import os
            
            db_path = os.path.join(os.getcwd(), "reflex.db")
            db_url = f"sqlite:///{db_path}"
            engine = create_engine(db_url, echo=False)
            
            today = date.today()
            this_monday = today - timedelta(days=today.weekday())
            
            with Session(engine) as session:
                statement = select(ChallengeProgress).where(
                    ChallengeProgress.student_id == self.current_user_id
                )
                all_progress = list(session.exec(statement).all())

                # 챌린지 정보와 진행도 결합
                progress_dict = {p.challenge_id: p for p in all_progress}
                
                result = []
                for challenge in self.active_challenges:
                    challenge_id = challenge["id"]
                    progress = progress_dict.get(challenge_id)
                    
                    # 주간 연속 기록용: 이번 주 기록 일수 재계산 (CarbonLog 기준)
                    weekly_streak_value = 0
                    if challenge["type"] == "WEEKLY_STREAK":
                        from ..models import CarbonLog  # 지연 import
                        weekly_logs = list(
                            session.exec(
                                select(CarbonLog).where(
                                    CarbonLog.student_id == self.current_user_id,
                                    CarbonLog.log_date >= this_monday,
                                    CarbonLog.log_date <= today,
                                    CarbonLog.source == "carbon_input",
                                )
                            ).all()
                        )
                        distinct_days = {log.log_date for log in weekly_logs if log.log_date}
                        weekly_streak_value = len(distinct_days)
                    
                    if progress:
                        # 일일/주간 리셋 처리 (UI 조회 시점에도 적용)
                        last_updated_date = progress.last_updated.date() if progress.last_updated else None
                        if last_updated_date is None:
                            last_updated_date = (datetime.now() - timedelta(days=1)).date()
                            progress.last_updated = datetime.combine(last_updated_date, datetime.min.time())
                        
                        if challenge["type"] in ["DAILY_INFO", "DAILY_QUIZ"]:
                            if last_updated_date != today:
                                progress.current_value = 0
                                progress.is_completed = False
                                progress.completed_at = None
                                progress.last_updated = datetime.now()
                                session.add(progress)
                                session.commit()
                                session.refresh(progress)
                        
                        if challenge["type"] == "WEEKLY_STREAK":
                            if last_updated_date and last_updated_date < this_monday:
                                # 주가 바뀐 경우 0부터 다시 시작
                                progress.current_value = 0
                                progress.is_completed = False
                                progress.completed_at = None
                                progress.last_updated = datetime.now()
                            # CarbonLog 기준으로 이번 주 연속 기록 일수 재계산
                            progress.current_value = weekly_streak_value
                            if progress.current_value >= challenge["goal_value"]:
                                progress.is_completed = True
                            session.add(progress)
                            session.commit()
                            session.refresh(progress)
                        
                        progress_percent = (
                            progress.current_value / challenge["goal_value"] * 100
                            if challenge["goal_value"] > 0
                            else 0
                        )
                        result.append(
                            {
                                "challenge_id": challenge_id,
                                "title": challenge["title"],
                                "type": challenge["type"],
                                "goal_value": challenge["goal_value"],
                                "current_value": progress.current_value,
                                "progress_percent": min(progress_percent, 100),
                                "is_completed": progress.is_completed,
                                "reward_points": challenge["reward_points"],
                            }
                        )
                    else:
                        # 진행도가 없으면, WEEKLY_STREAK는 이번 주 기록 일수로 초기화
                        current_value = weekly_streak_value if challenge["type"] == "WEEKLY_STREAK" else 0
                        progress_percent = (
                            current_value / challenge["goal_value"] * 100
                            if challenge["goal_value"] > 0
                            else 0
                        )
                        result.append(
                            {
                                "challenge_id": challenge_id,
                                "title": challenge["title"],
                                "type": challenge["type"],
                                "goal_value": challenge["goal_value"],
                                "current_value": current_value,
                                "progress_percent": min(progress_percent, 100),
                                "is_completed": False,
                                "reward_points": challenge["reward_points"],
                            }
                        )
                
                self.user_challenge_progress = result
            
        except Exception as e:
            logger.error(f"사용자 챌린지 진행도 로드 오류: {e}")
            self.user_challenge_progress = []

    async def complete_daily_info(self):
        """일일 챌린지 - 정보 글 읽기 완료 처리"""
        if not self.is_logged_in:
            self.challenge_message = "로그인 후 이용해주세요."
            return

        # 이미 오늘 읽었으면 무시
        if self.article_read_today:
            self.challenge_message = "오늘 이미 아티클을 읽었습니다. 내일 다시 도전해주세요!"
            return

        self.challenge_message = ""
        try:
            self.ensure_default_challenges()
            self.load_active_challenges()
            challenge = next((c for c in self.active_challenges if c["type"] == "DAILY_INFO"), None)
            if not challenge:
                self.challenge_message = "챌린지를 불러올 수 없습니다."
                return
            await self.update_challenge_progress(challenge["id"], 1)
            self.article_read_today = True  # 상태 업데이트
            self.challenge_message = "아티클 읽기 완료! 포인트가 적립됩니다."
            self.load_user_challenge_progress()
        except Exception as e:
            self.challenge_message = f"아티클 읽기 처리 중 오류: {e}"
            logger.error(self.challenge_message, exc_info=True)

    async def _complete_daily_quiz_with_answer(self, is_correct: bool):
        """일일 챌린지 - OX 퀴즈 완료 처리 (내부 메서드)
        
        Args:
            is_correct: 사용자가 선택한 답이 정답인지 여부 (True: O, False: X)
        """
        if not self.is_logged_in:
            self.challenge_message = "로그인 후 이용해주세요."
            return
        self.challenge_message = ""
        try:
            # 정답 확인: "지구 온난화를 막기 위해서는 일회용품 사용을 줄여야 한다"의 정답은 O(True)
            correct_answer = True  # O가 정답
            
            if is_correct != correct_answer:
                self.challenge_message = "틀렸습니다. 다시 시도해주세요."
                return
            
            self.ensure_default_challenges()
            self.load_active_challenges()
            challenge = next((c for c in self.active_challenges if c["type"] == "DAILY_QUIZ"), None)
            if not challenge:
                self.challenge_message = "챌린지를 불러올 수 없습니다."
                return
            await self.update_challenge_progress(challenge["id"], 1)
            self.challenge_message = "정답입니다! OX 퀴즈 완료! 포인트가 적립되었습니다."
            self.load_user_challenge_progress()
        except Exception as e:
            self.challenge_message = f"OX 퀴즈 처리 중 오류: {e}"
            logger.error(self.challenge_message, exc_info=True)

    async def complete_daily_quiz_o(self):
        """일일 챌린지 - OX 퀴즈 O 버튼 클릭 처리"""
        await self._complete_daily_quiz_with_answer(True)

    async def complete_daily_quiz_x(self):
        """일일 챌린지 - OX 퀴즈 X 버튼 클릭 처리"""
        await self._complete_daily_quiz_with_answer(False)

    async def complete_daily_quiz(self):
        """일일 챌린지 - 정답 처리 (기존 API 호환용)"""
        await self._complete_daily_quiz_with_answer(True)

    async def mark_daily_record(self):
        """주간 챌린지 - 7일 연속 기록 진행도 업데이트"""
        print(f"[주간 챌린지] mark_daily_record 호출됨, 로그인: {self.is_logged_in}, 사용자: {self.current_user_id}")
        logger.info(f"[주간 챌린지] mark_daily_record 호출됨, 로그인: {self.is_logged_in}, 사용자: {self.current_user_id}")
        
        if not self.is_logged_in:
            print("[주간 챌린지] 로그인되지 않음, 종료")
            return
        
        try:
            print("[주간 챌린지] 기본 챌린지 확인 중...")
            self.ensure_default_challenges()
            print("[주간 챌린지] 활성 챌린지 로드 중...")
            self.load_active_challenges()
            print(f"[주간 챌린지] 활성 챌린지 개수: {len(self.active_challenges)}")
            
            challenge = next((c for c in self.active_challenges if c["type"] == "WEEKLY_STREAK"), None)
            if not challenge:
                print("[주간 챌린지] WEEKLY_STREAK 챌린지를 찾을 수 없음")
                logger.warning("[주간 챌린지] WEEKLY_STREAK 챌린지를 찾을 수 없음")
                return
            
            print(f"[주간 챌린지] 챌린지 찾음: {challenge['title']} (ID: {challenge['id']})")
            logger.info(f"[주간 챌린지] 챌린지 찾음: {challenge['title']} (ID: {challenge['id']})")
            
            print(f"[주간 챌린지] 진행도 업데이트 시작 (challenge_id: {challenge['id']})")
            await self.update_challenge_progress(challenge["id"], 1)
            print("[주간 챌린지] 진행도 업데이트 완료")
            
            await self.load_user_challenge_progress()
            print("[주간 챌린지] 사용자 챌린지 진행도 로드 완료")
        except Exception as e:
            print(f"[주간 챌린지] 오류 발생: {e}")
            logger.error(f"주간 챌린지 업데이트 오류: {e}", exc_info=True)
    
    # 포인트 로그 관련 변수
    points_log: List[Dict[str, Any]] = []
    displayed_points_log: List[Dict[str, Any]] = []  # 화면에 표시할 포인트 로그
    points_log_display_limit: int = 10  # 표시할 포인트 로그 개수
    
    def load_more_points_log(self):
        """포인트 로그 더보기 (10개씩 추가)"""
        self.points_log_display_limit += 10
        # 표시할 로그 업데이트 (양수/음수 모두 포함)
        self.displayed_points_log = self.points_log[:self.points_log_display_limit] if self.points_log else []
    
    def load_points_log(self):
        """포인트 변동 내역 로드 (획득/차감 모두 포함)"""
        if not self.is_logged_in or not self.current_user_id:
            self.points_log = []
            return

        try:
            from ..models import CarbonLog, PointsLog
            from sqlmodel import Session, create_engine, select, desc, union_all
            from sqlalchemy import text
            import os

            db_path = os.path.join(os.getcwd(), "reflex.db")
            db_url = f"sqlite:///{db_path}"
            engine = create_engine(db_url, echo=False)

            with Session(engine) as session:
                result = []
                
                # 1. CarbonLog에서 포인트 획득 내역 (양수만)
                carbon_logs = session.exec(
                    select(CarbonLog).where(
                        CarbonLog.student_id == self.current_user_id,
                        CarbonLog.points_earned > 0
                    ).order_by(desc(CarbonLog.log_date), desc(CarbonLog.created_at))
                ).all()
                
                for log in carbon_logs:
                    source = getattr(log, "source", None) or "carbon_input"
                    description = "탄소배출 기록" if source == "carbon_input" else "챌린지 보상"
                    if log.ai_feedback:
                        description = log.ai_feedback
                    points = log.points_earned
                    result.append({
                        "date": log.log_date.strftime("%Y-%m-%d") if log.log_date else "",
                        "points": points,
                        "is_positive": True,  # CarbonLog는 항상 양수
                        "source": source,
                        "description": description,
                        "created_at": log.created_at if hasattr(log, "created_at") else None
                    })
                
                # 2. PointsLog에서 모든 포인트 변동 내역 (양수/음수 모두)
                points_logs = session.exec(
                    select(PointsLog).where(
                        PointsLog.student_id == self.current_user_id
                    ).order_by(desc(PointsLog.created_at))
                ).all()
                
                for log in points_logs:
                    points = log.points
                    # "탄소 배출 리포트 저장"으로 시작하는 description은 필터링 (중복 방지)
                    description = log.description or log.source or "포인트 변동"
                    if description and description.startswith("탄소 배출 리포트 저장"):
                        continue  # 이 항목은 건너뛰기 (CarbonLog에서 이미 표시됨)
                    # 양수/음수 모두 포함 (0은 제외하지 않음)
                    result.append({
                        "date": log.log_date.strftime("%Y-%m-%d") if log.log_date else (log.created_at.strftime("%Y-%m-%d") if hasattr(log, "created_at") and log.created_at else ""),
                        "points": points,
                        "is_positive": points > 0,  # 양수/음수 플래그
                        "source": log.source,
                        "description": description,
                        "created_at": log.created_at if hasattr(log, "created_at") else None
                    })
                
                # 3. 마일리지 환산 내역 (포인트 차감)
                from ..models import MileageRequest
                mileage_requests = session.exec(
                    select(MileageRequest).where(
                        MileageRequest.student_id == self.current_user_id,
                        MileageRequest.status == "APPROVED"
                    ).order_by(desc(MileageRequest.processed_at))
                ).all()
                
                for req in mileage_requests:
                    points = -req.request_points  # 음수로 표시
                    result.append({
                        "date": req.processed_at.strftime("%Y-%m-%d") if req.processed_at else "",
                        "points": points,
                        "is_positive": False,  # 마일리지 환산은 항상 음수
                        "source": "mileage_conversion",
                        "description": f"마일리지 환산 ({req.request_points}점 → {req.converted_mileage} 마일리지)",
                        "created_at": req.processed_at if req.processed_at else None
                    })
                
                # created_at 기준으로 정렬 (최신순)
                result.sort(key=lambda x: x.get("created_at") or datetime.min, reverse=True)
                
                self.points_log = result
                # 초기 표시 로그 설정 (최근 10개)
                self.points_log_display_limit = 10
                self.displayed_points_log = result[:10] if result else []

        except Exception as e:
            logger.error(f"포인트 로그 로드 오류: {e}", exc_info=True)
            self.points_log = []
    
    async def load_mypage_data(self):
        """마이페이지 모든 데이터 로드"""
        if not self.is_logged_in or not self.current_user_id:
            return
        
        try:
            # 사용자 포인트 정보 새로고침 - 모든 포인트 로그를 합산하여 총 포인트 계산
            from ..models import User, CarbonLog, PointsLog, MileageRequest
            from sqlmodel import Session, create_engine, select
            import os
            
            db_path = os.path.join(os.getcwd(), "reflex.db")
            db_url = f"sqlite:///{db_path}"
            engine = create_engine(db_url, echo=False)
            
            with Session(engine) as session:
                user_stmt = select(User).where(User.student_id == self.current_user_id)
                user = session.exec(user_stmt).first()
                if user:
                    # 포인트 로그를 합산하여 총 포인트 계산
                    total_points = 0
                    
                    # 1. CarbonLog에서 획득한 포인트 합산
                    carbon_logs = session.exec(
                        select(CarbonLog).where(
                            CarbonLog.student_id == self.current_user_id,
                            CarbonLog.points_earned > 0
                        )
                    ).all()
                    for log in carbon_logs:
                        total_points += log.points_earned
                    
                    # 2. PointsLog에서 모든 포인트 변동 합산
                    points_logs = session.exec(
                        select(PointsLog).where(
                            PointsLog.student_id == self.current_user_id
                        )
                    ).all()
                    for log in points_logs:
                        total_points += log.points
                    
                    # 3. 마일리지 환산으로 차감된 포인트 빼기
                    mileage_requests = session.exec(
                        select(MileageRequest).where(
                            MileageRequest.student_id == self.current_user_id,
                            MileageRequest.status == "APPROVED"
                        )
                    ).all()
                    for req in mileage_requests:
                        total_points -= req.request_points
                    
                    # 계산된 총 포인트를 사용자 포인트로 설정
                    self.current_user_points = max(0, total_points)  # 음수 방지
                    
                    # DB의 current_points도 업데이트 (동기화)
                    if user.current_points != self.current_user_points:
                        user.current_points = self.current_user_points
                        session.add(user)
                        session.commit()
                        logger.info(f"[마이페이지] 포인트 동기화: DB {user.current_points} -> 계산된 {self.current_user_points}")
        except Exception as e:
            logger.error(f"사용자 포인트 새로고침 오류: {e}", exc_info=True)
            # 오류 발생 시 DB 값 사용
            try:
                from ..models import User
                from sqlmodel import Session, create_engine, select
                import os
                
                db_path = os.path.join(os.getcwd(), "reflex.db")
                db_url = f"sqlite:///{db_path}"
                engine = create_engine(db_url, echo=False)
                
                with Session(engine) as session:
                    user_stmt = select(User).where(User.student_id == self.current_user_id)
                    user = session.exec(user_stmt).first()
                    if user:
                        self.current_user_points = user.current_points
            except:
                pass
        
        try:
            # 챌린지 진행도 로드
            self.load_user_challenge_progress()
        except Exception as e:
            logger.error(f"챌린지 진행도 로드 오류: {e}", exc_info=True)
        
        try:
            # 마일리지 환산 내역 로드
            self.load_mileage_conversion_logs()
        except Exception as e:
            logger.error(f"마일리지 환산 내역 로드 오류: {e}", exc_info=True)
        
        try:
            # 탄소 통계 로드 및 개별 변수에 할당
            stats = await self.get_carbon_statistics()
            self.carbon_total_logs = stats.get("total_logs", 0)
            self.carbon_total_emission = stats.get("total_emission", 0.0)
            self.carbon_average_daily_emission = stats.get("average_daily_emission", 0.0)
            self.carbon_total_activities = stats.get("total_activities", 0)
            self.carbon_category_breakdown = stats.get("category_breakdown", [])
        except Exception as e:
            logger.error(f"탄소 통계 로드 오류: {e}", exc_info=True)
            # 기본값 설정
            self.carbon_total_logs = 0
            self.carbon_total_emission = 0.0
            self.carbon_average_daily_emission = 0.0
            self.carbon_total_activities = 0
            self.carbon_category_breakdown = []
        
        try:
            # 포인트 로그 로드
            self.load_points_log()
        except Exception as e:
            logger.error(f"포인트 로그 로드 오류: {e}", exc_info=True)
            self.points_log = []
        
        try:
            # 대시보드 통계 로드 (이번주/한달 배출량)
            self.load_dashboard_statistics()
        except Exception as e:
            logger.error(f"대시보드 통계 로드 오류: {e}", exc_info=True)
            self.weekly_emission = 0.0
            self.monthly_emission = 0.0
            self.weekly_daily_data = []
            self.monthly_daily_data = []
    
    async def save_carbon_log_to_db(self):
        """탄소 로그 저장 후 주간 챌린지 진행도 업데이트"""
        # 부모 클래스(CarbonState)의 내부 헬퍼 메서드를 직접 호출
        await self._save_carbon_log_to_db_internal()
        
        # 저장 성공 시 주간 챌린지 진행도 업데이트
        if self.is_save_success:
            try:
                print("[ChallengeState] 저장 성공, 주간 챌린지 진행도 업데이트 시작...")
                await self.mark_daily_record()
                print("[ChallengeState] 주간 챌린지 진행도 업데이트 완료")
                logger.info("[ChallengeState] 주간 챌린지 진행도 업데이트 완료")
            except Exception as e:
                print(f"[ChallengeState] 주간 챌린지 업데이트 실패: {e}")
                logger.warning(f"[ChallengeState] 주간 챌린지 업데이트 실패: {e}", exc_info=True)
    
    def load_dashboard_statistics(self):
        """대시보드 통계 데이터 로드 (이번주/한달 배출량)"""
        if not self.is_logged_in or not self.current_user_id:
            self.weekly_emission = 0.0
            self.monthly_emission = 0.0
            self.weekly_daily_data = []
            self.monthly_daily_data = []
            return
        
        try:
            from ..models import CarbonLog
            from sqlmodel import Session, create_engine, select
            import os
            
            db_path = os.path.join(os.getcwd(), "reflex.db")
            db_url = f"sqlite:///{db_path}"
            engine = create_engine(db_url, echo=False)
            
            today = date.today()
            # 이번주 월요일 계산
            this_monday = today - timedelta(days=today.weekday())
            # 한달 전 날짜 계산
            one_month_ago = today - timedelta(days=30)
            
            with Session(engine) as session:
                # 이번주 로그 조회
                weekly_stmt = select(CarbonLog).where(
                    CarbonLog.student_id == self.current_user_id,
                    CarbonLog.log_date >= this_monday,
                    CarbonLog.log_date <= today
                )
                weekly_logs = list(session.exec(weekly_stmt).all())
                
                # 한달 로그 조회
                monthly_stmt = select(CarbonLog).where(
                    CarbonLog.student_id == self.current_user_id,
                    CarbonLog.log_date >= one_month_ago,
                    CarbonLog.log_date <= today
                )
                monthly_logs = list(session.exec(monthly_stmt).all())
            
            # 이번주 통계 계산
            self.weekly_emission = round(sum(log.total_emission for log in weekly_logs), 2)
            
            # 이번주 일별 데이터 생성
            weekly_daily_dict = {}
            for log in weekly_logs:
                day_key = log.log_date.strftime("%Y-%m-%d")
                if day_key not in weekly_daily_dict:
                    weekly_daily_dict[day_key] = 0.0
                weekly_daily_dict[day_key] += log.total_emission
            
            # 이번주 최대 배출량 계산 (그래프 높이 정규화용)
            max_weekly_emission = max(weekly_daily_dict.values()) if weekly_daily_dict else 1.0
            
            # 이번주 모든 날짜 채우기 (월요일부터 일요일까지 7일 모두)
            self.weekly_daily_data = []
            # 이번주 일요일 계산
            this_sunday = this_monday + timedelta(days=6)
            for i in range(7):
                current_date = this_monday + timedelta(days=i)
                day_key = current_date.strftime("%Y-%m-%d")
                day_name = ["월", "화", "수", "목", "금", "토", "일"][current_date.weekday()]
                # 오늘 이후 날짜는 배출량을 0으로 설정
                if current_date > today:
                    emission = 0.0
                    has_emission = False
                else:
                    emission = round(weekly_daily_dict.get(day_key, 0.0), 2)
                    has_emission = emission > 0.0
                # 그래프 높이 계산 (최대 200px, 최소 4px)
                height_percent = (emission / max_weekly_emission * 100) if max_weekly_emission > 0 else 0
                bar_height = max(4, min(200, int(height_percent * 2)))
                self.weekly_daily_data.append({
                    "date": day_key,
                    "day": day_name,
                    "emission": emission,
                    "height": bar_height,
                    "has_emission": has_emission
                })
            
            # 한달 통계 계산
            self.monthly_emission = round(sum(log.total_emission for log in monthly_logs), 2)
            
            # 한달 일별 데이터 생성 (최근 30일)
            monthly_daily_dict = {}
            for log in monthly_logs:
                day_key = log.log_date.strftime("%Y-%m-%d")
                if day_key not in monthly_daily_dict:
                    monthly_daily_dict[day_key] = 0.0
                monthly_daily_dict[day_key] += log.total_emission
            
            # 한달 최대 배출량 계산 (그래프 높이 정규화용)
            max_monthly_emission = max(monthly_daily_dict.values()) if monthly_daily_dict else 1.0
            
            # 더미 데이터 자동 생성 기능 제거 (회원가입 직후 포인트/배출량이 생성되는 문제 해결)
            # 사용자가 직접 리포트를 저장할 때만 데이터가 생성되도록 변경
            # 더미 데이터 생성 로직 전체 주석 처리
            # if len(monthly_logs) == 0:
            #     # 기존 더미 데이터 삭제
            #     self.delete_dummy_data()
            #     
            #     import random
            #     import json
            #     with Session(engine) as session:
            #         # 사용자 조회 (한 번만)
            #         user = session.exec(
            #             select(User).where(User.student_id == self.current_user_id)
            #         ).first()
            #         
            #         if not user:
            #             logger.error(f"[더미 데이터] 사용자를 찾을 수 없습니다: {self.current_user_id}")
            #             return
            #         
            #         total_points = 0
            #         # 최근 30일 동안의 더미 데이터 생성 (다양한 패턴으로)
            #         base_emission = 10.0  # 기본 배출량
            #         for i in range(30):
            #             current_date = one_month_ago + timedelta(days=i)
            #             if current_date > today:
            #                 break
            #             
            #             # 주기적인 패턴 추가 (주간 패턴)
            #             day_of_week = current_date.weekday()
            #             weekday_factor = 1.0 if day_of_week < 5 else 0.7  # 주말은 30% 감소
            #             
            #             # 장기 트렌드 추가 (시간에 따른 변화)
            #             trend_factor = 1.0 + (i / 30.0) * 0.3  # 점진적 증가
            #             
            #             # 랜덤 변동 추가 (일일 변동)
            #             random_variation = random.uniform(0.7, 1.3)
            #             
            #             # 주기적인 피크 추가 (일부 날짜에 높은 값)
            #             peak_factor = 1.0
            #             if i % 7 == 3:  # 목요일마다 약간 높게
            #                 peak_factor = 1.2
            #             elif i % 10 == 0:  # 10일마다 한 번씩 매우 높게
            #                 peak_factor = 1.5
            #             elif i % 5 == 2:  # 5일마다 한 번씩 낮게
            #                 peak_factor = 0.6
            #             
            #             # 최종 배출량 계산
            #             emission = round(base_emission * weekday_factor * trend_factor * random_variation * peak_factor, 2)
            #             # 범위 제한 (3~25kg)
            #             emission = max(3.0, min(25.0, emission))
            #             
            #             # 더미 포인트 생성 (배출량에 비례하되 변동 추가)
            #             points = random.randint(50, 200)
            #             total_points += points
            #             
            #             # 더미 활동 데이터 생성
            #             dummy_activities = [
            #                 {"category": "교통", "activity_type": "자동차", "value": random.uniform(10, 50), "unit": "km"},
            #                 {"category": "식품", "activity_type": "소고기", "value": random.uniform(100, 300), "unit": "g"},
            #             ]
            #             
            #             # CarbonLog 생성
            #             dummy_log = CarbonLog(
            #                 student_id=self.current_user_id,
            #                 log_date=current_date,
            #                 total_emission=emission,
            #                 points_earned=points,
            #                 activities_json=json.dumps(dummy_activities, ensure_ascii=False),
            #                 source="carbon_input",
            #                 created_at=datetime.now()
            #             )
            #             session.add(dummy_log)
            #         
            #         # 사용자 포인트 업데이트 (한 번만)
            #         user.current_points += total_points
            #         session.add(user)
            #         self.current_user_points = user.current_points
            #         
            #         session.commit()
            #         logger.info(f"[더미 데이터] {self.current_user_id} 사용자를 위한 더미 데이터 생성 완료 (총 {total_points}점 추가)")
            #         logger.info(f"[더미 데이터] {self.current_user_id} 사용자를 위한 더미 데이터 생성 완료")
            #         
            #         # 생성된 데이터 다시 조회
            #         monthly_stmt = select(CarbonLog).where(
            #             CarbonLog.student_id == self.current_user_id,
            #             CarbonLog.log_date >= one_month_ago,
            #             CarbonLog.log_date <= today
            #         )
            #         monthly_logs = list(session.exec(monthly_stmt).all())
            #         
            #         # 이번주 로그도 다시 조회
            #         weekly_stmt = select(CarbonLog).where(
            #             CarbonLog.student_id == self.current_user_id,
            #             CarbonLog.log_date >= this_monday,
            #             CarbonLog.log_date <= today
            #         )
            #         weekly_logs = list(session.exec(weekly_stmt).all())
            #         
            #         # weekly_daily_dict 재계산
            #         weekly_daily_dict = {}
            #         for log in weekly_logs:
            #             day_key = log.log_date.strftime("%Y-%m-%d")
            #             if day_key not in weekly_daily_dict:
            #                 weekly_daily_dict[day_key] = 0.0
            #             weekly_daily_dict[day_key] += log.total_emission
            #         
            #         # monthly_daily_dict 재계산
            #         monthly_daily_dict = {}
            #         for log in monthly_logs:
            #             day_key = log.log_date.strftime("%Y-%m-%d")
            #             if day_key not in monthly_daily_dict:
            #                 monthly_daily_dict[day_key] = 0.0
            #             monthly_daily_dict[day_key] += log.total_emission
            #         
            #         # 한달 최대 배출량 재계산
            #         max_monthly_emission = max(monthly_daily_dict.values()) if monthly_daily_dict else 1.0
            #         
            #         # 이번주 최대 배출량 재계산
            #         max_weekly_emission = max(weekly_daily_dict.values()) if weekly_daily_dict else 1.0
            #         
            #         # 이번주 통계 재계산
            #         self.weekly_emission = round(sum(log.total_emission for log in weekly_logs), 2)
            #         self.monthly_emission = round(sum(log.total_emission for log in monthly_logs), 2)
            
            # 한달 일별 데이터 생성 (날짜순으로 정렬)
            self.monthly_daily_data = []
            for i in range(30):
                current_date = one_month_ago + timedelta(days=i)
                if current_date > today:
                    break
                day_key = current_date.strftime("%Y-%m-%d")
                day_name = ["월", "화", "수", "목", "금", "토", "일"][current_date.weekday()]
                month_day = current_date.strftime("%m/%d")
                emission = round(monthly_daily_dict.get(day_key, 0.0), 2)
                # 그래프 높이 계산 (최대 150px, 최소 2px)
                height_percent = (emission / max_monthly_emission * 100) if max_monthly_emission > 0 else 0
                bar_height = max(2, min(150, int(height_percent * 1.5)))
                has_emission = emission > 0.0
                self.monthly_daily_data.append({
                    "date": day_key,
                    "day": day_name,
                    "month_day": month_day,
                    "emission": emission,
                    "height": bar_height,
                    "has_emission": has_emission
                })
            
            # 꺽은선 그래프 SVG 생성
            self._generate_monthly_line_chart_svg()

        except Exception as e:
            logger.error(f"대시보드 통계 로드 오류: {e}", exc_info=True)
            self.weekly_emission = 0.0
            self.monthly_emission = 0.0
            self.weekly_daily_data = []
            self.monthly_daily_data = []

    mypage_section: str = "points"  # 기본값은 "내 포인트"
    
    monthly_line_chart_svg: str = ""  # 한달 꺽은선 그래프 SVG

    def set_mypage_section(self, section: str):
        self.mypage_section = section
    
    def delete_dummy_data(self):
        """더미 데이터 삭제"""
        if not self.is_logged_in or not self.current_user_id:
            logger.warning("[더미 데이터 삭제] 로그인되지 않았습니다.")
            return
        
        try:
            from ..models import CarbonLog
            from sqlmodel import Session, create_engine, select
            import os
            
            db_path = os.path.join(os.getcwd(), "reflex.db")
            db_url = f"sqlite:///{db_path}"
            engine = create_engine(db_url, echo=False)
            
            with Session(engine) as session:
                # 최근 30일 이내의 더미 데이터 삭제
                today = date.today()
                one_month_ago = today - timedelta(days=30)
                
                # 더미 데이터 조회 (source="carbon_input"이고 최근 30일 이내)
                stmt = select(CarbonLog).where(
                    CarbonLog.student_id == self.current_user_id,
                    CarbonLog.log_date >= one_month_ago,
                    CarbonLog.log_date <= today,
                    CarbonLog.source == "carbon_input"
                )
                dummy_logs = list(session.exec(stmt).all())
                
                if len(dummy_logs) == 0:
                    logger.info(f"[더미 데이터 삭제] 삭제할 더미 데이터가 없습니다: {self.current_user_id}")
                    return
                
                # 포인트 차감 계산
                total_points_to_deduct = sum(log.points_earned for log in dummy_logs)
                
                # 더미 데이터 삭제
                for log in dummy_logs:
                    session.delete(log)
                
                # 사용자 포인트 차감
                user = session.exec(
                    select(User).where(User.student_id == self.current_user_id)
                ).first()
                if user:
                    user.current_points = max(0, user.current_points - total_points_to_deduct)
                    self.current_user_points = user.current_points
                    session.add(user)
                
                session.commit()
                logger.info(f"[더미 데이터 삭제] {len(dummy_logs)}개의 더미 데이터 삭제 완료 (차감된 포인트: {total_points_to_deduct}점)")
                
        except Exception as e:
            logger.error(f"[더미 데이터 삭제] 오류: {e}", exc_info=True)
    
    def _generate_monthly_line_chart_svg(self):
        """한달 꺽은선 그래프 SVG 생성"""
        try:
            if not self.monthly_daily_data or len(self.monthly_daily_data) == 0:
                self.monthly_line_chart_svg = ""
                return
            
            width = 800
            height = 200
            padding = {"top": 20, "right": 20, "bottom": 30, "left": 40}
            chart_width = width - padding["left"] - padding["right"]
            chart_height = height - padding["top"] - padding["bottom"]
            
            # 최대값 계산
            max_emission = max([d.get("emission", 0) for d in self.monthly_daily_data], default=1.0)
            if max_emission == 0:
                max_emission = 1.0
            
            # 포인트 계산
            points = []
            for i, day_data in enumerate(self.monthly_daily_data):
                x = (i / (len(self.monthly_daily_data) - 1)) * chart_width if len(self.monthly_daily_data) > 1 else 0
                y = chart_height - ((day_data.get("emission", 0) / max_emission) * chart_height)
                points.append({"x": x, "y": y})
            
            # SVG 생성
            svg_parts = []
            svg_parts.append(f'<svg width="{width}" height="{height}" style="overflow: visible;">')
            svg_parts.append('<defs>')
            svg_parts.append('<linearGradient id="monthlyLineGradient" x1="0%" y1="0%" x2="0%" y2="100%">')
            svg_parts.append('<stop offset="0%" style="stop-color:#2196F3;stop-opacity:0.3" />')
            svg_parts.append('<stop offset="100%" style="stop-color:#64B5F6;stop-opacity:0.1" />')
            svg_parts.append('</linearGradient>')
            svg_parts.append('</defs>')
            
            # 그룹 생성
            svg_parts.append(f'<g transform="translate({padding["left"]}, {padding["top"]})">')
            
            # 영역 채우기 (그라디언트)
            if len(points) > 0:
                area_path = f'M 0,{chart_height} L ' + ' L '.join([f'{p["x"]},{p["y"]}' for p in points]) + f' L {chart_width},{chart_height} Z'
                svg_parts.append(f'<path d="{area_path}" fill="url(#monthlyLineGradient)" opacity="0.5"/>')
                
                # 선 그리기
                line_path = 'M ' + ' L '.join([f'{p["x"]},{p["y"]}' for p in points])
                svg_parts.append(f'<path d="{line_path}" fill="none" stroke="#2196F3" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>')
                
                # 점 그리기
                for i, point in enumerate(points):
                    if self.monthly_daily_data[i].get("has_emission", False):
                        svg_parts.append(f'<circle cx="{point["x"]}" cy="{point["y"]}" r="4" fill="#2196F3" stroke="#fff" stroke-width="2"/>')
            
            svg_parts.append('</g>')
            svg_parts.append('</svg>')
            
            self.monthly_line_chart_svg = ''.join(svg_parts)
            
        except Exception as e:
            logger.error(f"한달 꺽은선 그래프 SVG 생성 오류: {e}", exc_info=True)
            self.monthly_line_chart_svg = ""

    article_modal_open: bool = False
    article_detail: dict = {}

    # 퀴즈 상태 변수
    quiz_answered: bool = False  # 오늘 퀴즈를 풀었는지 여부
    quiz_is_correct: bool = False  # 정답 여부

    # 아티클 상태 변수
    article_read_today: bool = False  # 오늘 아티클을 읽었는지 여부

    def open_article(self, article: dict):
        self.article_detail = article
        self.article_modal_open = True

    def close_article(self):
        self.article_modal_open = False

    async def load_quiz_state(self):
        """퀴즈 및 아티클 상태 로드 (오늘 이미 완료했는지 확인)"""
        if not self.is_logged_in or not self.current_user_id:
            self.quiz_answered = False
            self.quiz_is_correct = False
            self.article_read_today = False
            return

        try:
            from sqlmodel import Session, create_engine, select
            import os

            db_path = os.path.join(os.getcwd(), "reflex.db")
            db_url = f"sqlite:///{db_path}"
            engine = create_engine(db_url, echo=False)

            today = date.today()

            # 챌린지 로드
            self.ensure_default_challenges()
            self.load_active_challenges()

            quiz_challenge = next((c for c in self.active_challenges if c["type"] == "DAILY_QUIZ"), None)
            info_challenge = next((c for c in self.active_challenges if c["type"] == "DAILY_INFO"), None)

            with Session(engine) as session:
                # DAILY_QUIZ 진행도 조회
                if quiz_challenge:
                    quiz_progress = session.exec(
                        select(ChallengeProgress).where(
                            ChallengeProgress.challenge_id == quiz_challenge["id"],
                            ChallengeProgress.student_id == self.current_user_id
                        )
                    ).first()

                    if quiz_progress and quiz_progress.last_updated:
                        last_updated_date = quiz_progress.last_updated.date()
                        if last_updated_date == today:
                            # 오늘 날짜로 기록이 있고, 정답을 맞춘 경우에만 완료로 표시
                            # 오답인 경우는 데이터베이스에 기록되지 않으므로, is_completed가 True인 경우만 완료로 처리
                            if quiz_progress.is_completed:
                                self.quiz_answered = True
                                self.quiz_is_correct = True
                                logger.info(f"퀴즈 상태 로드: 오늘 정답을 맞춤")
                            else:
                                # is_completed가 False인 경우는 오래된 기록이거나 오류 상태
                                # 오늘 날짜지만 완료되지 않은 경우는 초기화
                                self.quiz_answered = False
                                self.quiz_is_correct = False
                                logger.info(f"퀴즈 상태 로드: 오늘 날짜 기록이 있지만 완료되지 않음, 초기화")
                        else:
                            self.quiz_answered = False
                            self.quiz_is_correct = False
                    else:
                        self.quiz_answered = False
                        self.quiz_is_correct = False
                else:
                    self.quiz_answered = False
                    self.quiz_is_correct = False

                # DAILY_INFO 진행도 조회
                if info_challenge:
                    info_progress = session.exec(
                        select(ChallengeProgress).where(
                            ChallengeProgress.challenge_id == info_challenge["id"],
                            ChallengeProgress.student_id == self.current_user_id
                        )
                    ).first()

                    if info_progress and info_progress.last_updated:
                        last_updated_date = info_progress.last_updated.date()
                        if last_updated_date == today and info_progress.is_completed:
                            self.article_read_today = True
                            logger.info("아티클 상태 로드: 오늘 이미 읽었음")
                        else:
                            self.article_read_today = False
                    else:
                        self.article_read_today = False
                else:
                    self.article_read_today = False

        except Exception as e:
            logger.error(f"챌린지 상태 로드 오류: {e}", exc_info=True)
            self.quiz_answered = False
            self.quiz_is_correct = False
            self.article_read_today = False

    async def answer_quiz(self, is_correct: bool):
        """퀴즈 답변 처리 (정답: True, 오답: False)"""
        if not self.is_logged_in:
            self.challenge_message = "로그인 후 이용해주세요."
            return

        # 이미 정답을 맞춘 경우 더 이상 진행 불가
        if self.quiz_is_correct:
            self.challenge_message = "오늘 퀴즈는 이미 완료했습니다."
            return

        # 정답인 경우에만 상태를 완료로 기록
        if is_correct:
            self.quiz_answered = True
            self.quiz_is_correct = True
            await self.complete_daily_quiz()
        else:
            # 오답은 재도전 가능하도록 상태를 유지하지 않음
            self.quiz_answered = False
            self.quiz_is_correct = False
            self.challenge_message = "틀렸습니다. 다시 시도해보세요."

