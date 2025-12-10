"""
챌린지 시스템 관련 State
"""

import reflex as rx
from typing import List, Dict, Any
from datetime import datetime, date, timedelta
import logging
from .battle import BattleState
from ..models import Challenge, ChallengeProgress, User

logger = logging.getLogger(__name__)


class ChallengeState(BattleState):
    """
    챌린지 시스템 관련 상태 및 로직
    """
    active_challenges: List[Dict[str, Any]] = []
    user_challenge_progress: List[Dict[str, Any]] = []
    challenge_message: str = ""
    
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
    
    async def ensure_default_challenges(self):
        """필수 기본 챌린지(주간/일일) 생성"""
        try:
            from sqlmodel import Session, create_engine, select
            import os

            db_path = os.path.join(os.getcwd(), "reflex.db")
            db_url = f"sqlite:///{db_path}"
            engine = create_engine(db_url, echo=False)

            default_challenges = [
                {"title": "7일 연속 기록", "type": "WEEKLY_STREAK", "goal_value": 7, "reward_points": 700},
                {"title": "정보 글 읽기", "type": "DAILY_INFO", "goal_value": 1, "reward_points": 150},
                {"title": "OX 퀴즈 풀기", "type": "DAILY_QUIZ", "goal_value": 1, "reward_points": 200},
            ]

            with Session(engine) as session:
                titles = [item["title"] for item in default_challenges]
                existing = session.exec(select(Challenge).where(Challenge.title.in_(titles))).all()
                existing_titles = {c.title for c in existing}

                created = 0
                for item in default_challenges:
                    if item["title"] in existing_titles:
                        continue
                    ch = Challenge(
                        title=item["title"],
                        type=item["type"],
                        goal_value=item["goal_value"],
                        reward_points=item["reward_points"],
                        is_active=True,
                    )
                    session.add(ch)
                    created += 1
                if created:
                    session.commit()
        except Exception as e:
            logger.error(f"기본 챌린지 생성 오류: {e}", exc_info=True)

    async def load_active_challenges(self):
        """활성화된 챌린지 목록 로드"""
        try:
            await self.ensure_default_challenges()

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
            self.active_challenges = []
    
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

                    logger.info(f"챌린지 완료: {self.current_user_id}, 챌린지: {challenge.title}, 보상: {challenge.reward_points}")

                # 진행도 저장 (세션 커밋)
                session.add(progress)
                session.commit()
                session.refresh(progress)

        except Exception as e:
            logger.error(f"챌린지 진행도 업데이트 오류: {e}")
    
    async def load_user_challenge_progress(self):
        """사용자의 챌린지 진행도 로드"""
        if not self.is_logged_in or not self.current_user_id:
            self.user_challenge_progress = []
            return
        
        try:
            # 활성화된 챌린지 로드
            await self.load_active_challenges()
            
            # 사용자의 진행도 조회 (SQLModel Session 직접 사용)
            from sqlmodel import Session, create_engine, select
            import os
            
            db_path = os.path.join(os.getcwd(), "reflex.db")
            db_url = f"sqlite:///{db_path}"
            engine = create_engine(db_url, echo=False)
            
            all_progress = []
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
                
                if progress:
                    progress_percent = (progress.current_value / challenge["goal_value"]) * 100 if challenge["goal_value"] > 0 else 0
                    result.append({
                        "challenge_id": challenge_id,
                        "title": challenge["title"],
                        "type": challenge["type"],
                        "goal_value": challenge["goal_value"],
                        "current_value": progress.current_value,
                        "progress_percent": min(progress_percent, 100),
                        "is_completed": progress.is_completed,
                        "reward_points": challenge["reward_points"]
                    })
                else:
                    # 진행도가 없으면 0으로 시작
                    result.append({
                        "challenge_id": challenge_id,
                        "title": challenge["title"],
                        "type": challenge["type"],
                        "goal_value": challenge["goal_value"],
                        "current_value": 0,
                        "progress_percent": 0,
                        "is_completed": False,
                        "reward_points": challenge["reward_points"]
                    })
            
            self.user_challenge_progress = result
            
        except Exception as e:
            logger.error(f"사용자 챌린지 진행도 로드 오류: {e}")
            self.user_challenge_progress = []

    async def complete_daily_info(self):
        """일일 챌린지 - 정보 글 읽기 완료 처리"""
        if not self.is_logged_in:
            self.challenge_message = "로그인 후 이용해주세요."
            return
        self.challenge_message = ""
        try:
            await self.ensure_default_challenges()
            await self.load_active_challenges()
            challenge = next((c for c in self.active_challenges if c["type"] == "DAILY_INFO"), None)
            if not challenge:
                self.challenge_message = "챌린지를 불러올 수 없습니다."
                return
            await self.update_challenge_progress(challenge["id"], 1)
            self.challenge_message = "정보 글 읽기 완료! 포인트가 적립됩니다."
            await self.load_user_challenge_progress()
        except Exception as e:
            self.challenge_message = f"정보 글 읽기 처리 중 오류: {e}"
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
            
            await self.ensure_default_challenges()
            await self.load_active_challenges()
            challenge = next((c for c in self.active_challenges if c["type"] == "DAILY_QUIZ"), None)
            if not challenge:
                self.challenge_message = "챌린지를 불러올 수 없습니다."
                return
            await self.update_challenge_progress(challenge["id"], 1)
            self.challenge_message = "OX 퀴즈 완료! 포인트가 적립됩니다."
            await self.load_user_challenge_progress()
        except Exception as e:
            self.challenge_message = f"OX 퀴즈 처리 중 오류: {e}"
            logger.error(self.challenge_message, exc_info=True)

    async def complete_daily_quiz_o(self):
        """일일 챌린지 - OX 퀴즈 O 버튼 클릭 처리"""
        await self._complete_daily_quiz_with_answer(True)

    async def complete_daily_quiz_x(self):
        """일일 챌린지 - OX 퀴즈 X 버튼 클릭 처리"""
        await self._complete_daily_quiz_with_answer(False)

    async def mark_daily_record(self):
        """주간 챌린지 - 7일 연속 기록 진행도 업데이트"""
        print(f"[주간 챌린지] mark_daily_record 호출됨, 로그인: {self.is_logged_in}, 사용자: {self.current_user_id}")
        logger.info(f"[주간 챌린지] mark_daily_record 호출됨, 로그인: {self.is_logged_in}, 사용자: {self.current_user_id}")
        
        if not self.is_logged_in:
            print("[주간 챌린지] 로그인되지 않음, 종료")
            return
        
        try:
            print("[주간 챌린지] 기본 챌린지 확인 중...")
            await self.ensure_default_challenges()
            print("[주간 챌린지] 활성 챌린지 로드 중...")
            await self.load_active_challenges()
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
    
    async def load_points_log(self):
        """포인트 획득 내역 로드 (날짜별)"""
        if not self.is_logged_in or not self.current_user_id:
            self.points_log = []
            return
        
        try:
            from ..models import CarbonLog
            from sqlmodel import Session, create_engine, select
            import os
            
            db_path = os.path.join(os.getcwd(), "reflex.db")
            db_url = f"sqlite:///{db_path}"
            engine = create_engine(db_url, echo=False)
            
            with Session(engine) as session:
                # 포인트가 0보다 큰 로그만 조회 (포인트가 있는 기록만 표시)
                stmt = select(CarbonLog).where(
                    CarbonLog.student_id == self.current_user_id,
                    CarbonLog.points_earned > 0
                ).order_by(CarbonLog.log_date.desc())
                
                logger.info(f"[포인트 로그] 조회 조건: student_id={self.current_user_id}, points_earned > 0")
                print(f"[포인트 로그] 조회 조건: student_id={self.current_user_id}, points_earned > 0")
                
                logs = session.exec(stmt).all()
                print(f"[포인트 로그] 조회 결과: {len(logs)}개")
                
                result = []
                for log in logs:
                    result.append({
                        "date": log.log_date.strftime("%Y-%m-%d") if log.log_date else "",
                        "points": log.points_earned
                    })
                    print(f"[포인트 로그] 날짜: {log.log_date}, 포인트: {log.points_earned}점")
                
                self.points_log = result
                logger.info(f"포인트 로그 로드 완료: {len(result)}개")
                print(f"[포인트 로그] 최종 결과: {len(result)}개")
                
        except Exception as e:
            logger.error(f"포인트 로그 로드 오류: {e}", exc_info=True)
            self.points_log = []
    
    async def load_mypage_data(self):
        """마이페이지 모든 데이터 로드"""
        if not self.is_logged_in or not self.current_user_id:
            return
        
        try:
            # 사용자 포인트 정보 새로고침
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
                    logger.info(f"[마이페이지] 사용자 포인트 새로고침: {self.current_user_points}점")
        except Exception as e:
            logger.error(f"사용자 포인트 새로고침 오류: {e}", exc_info=True)
        
        try:
            # 챌린지 진행도 로드
            await self.load_user_challenge_progress()
        except Exception as e:
            logger.error(f"챌린지 진행도 로드 오류: {e}", exc_info=True)
        
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
            await self.load_points_log()
        except Exception as e:
            logger.error(f"포인트 로그 로드 오류: {e}", exc_info=True)
            self.points_log = []
        
        try:
            # 대시보드 통계 로드 (이번주/한달 배출량)
            await self.load_dashboard_statistics()
        except Exception as e:
            logger.error(f"대시보드 통계 로드 오류: {e}", exc_info=True)
            self.weekly_emission = 0.0
            self.monthly_emission = 0.0
            self.weekly_daily_data = []
            self.monthly_daily_data = []
        
        logger.info(f"마이페이지 데이터 로드 완료: {self.current_user_id}, 포인트: {self.current_user_points}점")
    
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
    
    async def load_dashboard_statistics(self):
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
            
            # 이번주 모든 날짜 채우기 (월요일부터 오늘까지)
            self.weekly_daily_data = []
            for i in range(7):
                current_date = this_monday + timedelta(days=i)
                if current_date > today:
                    break
                day_key = current_date.strftime("%Y-%m-%d")
                day_name = ["월", "화", "수", "목", "금", "토", "일"][current_date.weekday()]
                emission = round(weekly_daily_dict.get(day_key, 0.0), 2)
                # 그래프 높이 계산 (최대 200px, 최소 4px)
                height_percent = (emission / max_weekly_emission * 100) if max_weekly_emission > 0 else 0
                bar_height = max(4, min(200, int(height_percent * 2)))
                has_emission = emission > 0.0
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
            
            logger.info(f"대시보드 통계 로드 완료: 이번주 {self.weekly_emission}kg, 한달 {self.monthly_emission}kg")
            
        except Exception as e:
            logger.error(f"대시보드 통계 로드 오류: {e}", exc_info=True)
            self.weekly_emission = 0.0
            self.monthly_emission = 0.0
            self.weekly_daily_data = []
            self.monthly_daily_data = []



