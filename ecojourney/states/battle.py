"""
대항전 시스템 관련 State
"""

import reflex as rx
from typing import Optional, Dict, Any, List
from datetime import date, datetime, timedelta
import logging
import random
from .carbon import CarbonState
from ..models import Battle, BattleParticipant, User

logger = logging.getLogger(__name__)

# 단과대 목록
COLLEGES = [
    "인문대학",
    "사회과학대학",
    "경영대학",
    "자연과학대학",
    "의과대학",
    "간호대학",
    "글로벌융합대학",
    "미디어스쿨",
    "반도체·디스플레이스쿨",
    "정보과학대학",
    "미래융합스쿨",
    "산학협력특성화대학",
    "일송자유교양대학",
    "자기설계융합전공"
]


class BattleState(CarbonState):
    """
    대항전 시스템 관련 상태 및 로직
    """
    current_battle: Optional[Dict[str, Any]] = None
    current_battle_participants: List[Dict[str, Any]] = []
    college_a_participants: List[Dict[str, Any]] = []  # 단과대 A 참가자 목록 (상위 5명)
    college_b_participants: List[Dict[str, Any]] = []  # 단과대 B 참가자 목록 (상위 5명)
    battle_bet_amount: int = 0
    battle_error_message: str = ""
    previous_battles: List[Dict[str, Any]] = []  # 저번주 대결 결과
    personal_rankings: List[Dict[str, Any]] = []  # 개인 포인트 랭킹 (1~10등)
    
    def set_battle_bet_amount(self, value: str):
        """베팅 포인트 설정"""
        try:
            self.battle_bet_amount = int(value) if value else 0
        except ValueError:
            self.battle_bet_amount = 0
    
    def _get_week_start_end(self, target_date: date = None) -> tuple[date, date]:
        """주어진 날짜가 속한 주의 월요일과 일요일 반환"""
        if target_date is None:
            target_date = date.today()
        
        # 월요일까지의 일수 계산 (월요일=0, 일요일=6)
        days_since_monday = target_date.weekday()
        monday = target_date - timedelta(days=days_since_monday)
        sunday = monday + timedelta(days=6)
        
        return monday, sunday
    
    async def check_and_reset_battles(self):
        """매주 월요일 대결 리셋 및 새 대결 생성"""
        try:
            from sqlmodel import Session, create_engine, select
            import os
            
            db_path = os.path.join(os.getcwd(), "reflex.db")
            db_url = f"sqlite:///{db_path}"
            engine = create_engine(db_url, echo=False)
            
            today = date.today()
            this_monday, this_sunday = self._get_week_start_end(today)
            
            with Session(engine) as session:
                # 이번 주 대결이 있는지 확인
                statement = select(Battle).where(
                    Battle.start_date == this_monday,
                    Battle.status == "ACTIVE"
                )
                existing_battle = session.exec(statement).first()
                
                if existing_battle:
                    # 이미 이번 주 대결이 있으면 리셋 불필요
                    return
                
                # 지난 주 대결 종료 처리 및 포인트 분배
                last_monday = this_monday - timedelta(days=7)
                last_sunday = this_sunday - timedelta(days=7)
                
                last_week_battles = session.exec(
                    select(Battle).where(
                        Battle.start_date == last_monday,
                        Battle.status == "ACTIVE"
                    )
                ).all()
                
                # 지난 주 대결 종료 처리
                for battle in last_week_battles:
                    await self._finalize_battle(battle.id, session)
                
                # 새 대결 생성
                await self._create_new_battles(this_monday, this_sunday, session)
                session.commit()
                
        except Exception as e:
            logger.error(f"대결 리셋 오류: {e}", exc_info=True)
    
    async def _finalize_battle(self, battle_id: int, session):
        """대결 종료 처리 및 포인트 분배"""
        try:
            from sqlmodel import select
            
            # session에서 battle 조회
            battle = session.exec(select(Battle).where(Battle.id == battle_id)).first()
            if not battle:
                return
            
            # 승자 결정
            if battle.score_a > battle.score_b:
                winner = battle.college_a
                loser = battle.college_b
            elif battle.score_b > battle.score_a:
                winner = battle.college_b
                loser = battle.college_a
            else:
                # 무승부 처리 (양쪽 모두 포인트 반환)
                winner = None
                loser = None
            
            battle.winner = winner
            battle.status = "FINISHED"
            session.add(battle)
            # 상태 업데이트는 보상 분배와 함께 원자적으로 커밋되어야 함
            
            # 참가자 조회
            participants = session.exec(
                select(BattleParticipant).where(BattleParticipant.battle_id == battle_id)
            ).all()
            
            if winner:
                # 승자 팀 참가자들
                winner_participants = []
                loser_participants = []
                
                for p in participants:
                    user_college = self._get_user_college(p.student_id, session)
                    # user_college가 None인 경우 처리 (사용자 조회 실패)
                    if user_college is None:
                        logger.warning(f"참가자 {p.student_id}의 단과대를 조회할 수 없습니다. 베팅 포인트를 반환합니다.")
                        # 조회 실패한 참가자에게 베팅 포인트 반환
                        p.reward_amount = p.bet_amount
                        session.add(p)
                        user = session.exec(select(User).where(User.student_id == p.student_id)).first()
                        if user:
                            user.current_points += p.bet_amount
                            session.add(user)
                        continue
                    
                    if (battle.college_a == winner and user_college == battle.college_a) or \
                       (battle.college_b == winner and user_college == battle.college_b):
                        winner_participants.append(p)
                    else:
                        loser_participants.append(p)
                
                # 패자 팀 총 베팅 포인트
                total_loser_bet = sum(p.bet_amount for p in loser_participants)
                
                # 승자 팀 총 베팅 포인트
                total_winner_bet = sum(p.bet_amount for p in winner_participants)
                
                # 승자 팀에게 포인트 분배 (패자 팀 베팅 포인트 + 자신의 베팅 포인트)
                if winner_participants and total_winner_bet > 0:
                    from ..models import PointsLog
                    for participant in winner_participants:
                        # 자신의 베팅 비율에 따라 분배
                        share_ratio = participant.bet_amount / total_winner_bet
                        reward = int(total_loser_bet * share_ratio) + participant.bet_amount
                        participant.reward_amount = reward
                        session.add(participant)
                        
                        # 사용자 포인트 지급
                        user = session.exec(select(User).where(User.student_id == participant.student_id)).first()
                        if user:
                            user.current_points += reward
                            session.add(user)
                            
                            # 포인트 획득 로그 기록
                            points_log = PointsLog(
                                student_id=participant.student_id,
                                log_date=date.today(),
                                points=reward,
                                source="battle_reward",
                                description=f"대항전 승리 보상 ({battle.college_a} vs {battle.college_b})"
                            )
                            session.add(points_log)
                
                # 패자 팀은 포인트 손실 (이미 차감되었으므로 추가 작업 없음)
            else:
                # 무승부: 모든 참가자에게 베팅 포인트 반환
                from ..models import PointsLog
                for participant in participants:
                    participant.reward_amount = participant.bet_amount
                    session.add(participant)
                    
                    user = session.exec(select(User).where(User.student_id == participant.student_id)).first()
                    if user:
                        user.current_points += participant.bet_amount
                        session.add(user)
                        
                        # 포인트 반환 로그 기록
                        points_log = PointsLog(
                            student_id=participant.student_id,
                            log_date=date.today(),
                            points=participant.bet_amount,
                            source="battle_draw",
                            description=f"대항전 무승부 포인트 반환 ({battle.college_a} vs {battle.college_b})"
                        )
                        session.add(points_log)
            
            # 모든 작업(상태 업데이트 + 보상 분배)이 성공적으로 완료된 후에만 커밋
            session.commit()
            logger.info(f"대결 종료 처리 완료: Battle {battle_id}, 승자: {winner}")
            
        except Exception as e:
            # 예외 발생 시 롤백하여 배틀 상태와 보상 분배가 모두 취소되도록 함
            session.rollback()
            logger.error(f"대결 종료 처리 오류: {e}", exc_info=True)
    
    def _get_user_college(self, student_id: str, session) -> Optional[str]:
        """사용자의 단과대 조회"""
        try:
            from sqlmodel import select
            user = session.exec(select(User).where(User.student_id == student_id)).first()
            return user.college if user else None
        except:
            return None
    
    async def _create_new_battles(self, start_date: date, end_date: date, session):
        """새 대결 생성 (랜덤 매칭)"""
        try:
            # 실제 사용자가 있는 단과대만 필터링
            from sqlmodel import select
            users = session.exec(select(User)).all()
            active_colleges = list(set([user.college for user in users if user.college in COLLEGES]))
            
            if len(active_colleges) < 2:
                logger.warning("대결을 생성할 충분한 단과대가 없습니다.")
                return
            
            # 랜덤 셔플
            random.shuffle(active_colleges)
            
            # 1:1 매칭 생성
            battles_created = 0
            for i in range(0, len(active_colleges) - 1, 2):
                college_a = active_colleges[i]
                college_b = active_colleges[i + 1]
                
                new_battle = Battle(
                    start_date=start_date,
                    end_date=end_date,
                    college_a=college_a,
                    college_b=college_b,
                    score_a=0,
                    score_b=0,
                    status="ACTIVE",
                    created_at=datetime.now()
                )
                session.add(new_battle)
                battles_created += 1
            
            logger.info(f"새 대결 {battles_created}개 생성 완료")
            
        except Exception as e:
            logger.error(f"새 대결 생성 오류: {e}", exc_info=True)
    
    async def load_current_battle(self):
        """현재 활성화된 대항전 정보 로드"""
        if not self.is_logged_in:
            return
        
        # 먼저 리셋 체크
        await self.check_and_reset_battles()
        
        try:
            today = date.today()
            this_monday, this_sunday = self._get_week_start_end(today)
            
            from sqlmodel import Session, create_engine, select
            import os
            
            db_path = os.path.join(os.getcwd(), "reflex.db")
            db_url = f"sqlite:///{db_path}"
            engine = create_engine(db_url, echo=False)
            
            with Session(engine) as session:
                statement = select(Battle).where(
                    Battle.start_date == this_monday,
                    Battle.status == "ACTIVE"
                )
                battles = list(session.exec(statement).all())
                
                # 사용자 단과대와 관련된 대결 찾기
                for battle in battles:
                    if battle.college_a == self.current_user_college or battle.college_b == self.current_user_college:
                        # 각 팀의 참가자 수와 총 베팅 포인트 계산
                        participants_a = session.exec(
                            select(BattleParticipant).where(
                                BattleParticipant.battle_id == battle.id
                            )
                        ).all()
                        
                        # 각 팀의 고유 참가자 수 계산 (중복 student_id 제거)
                        team_a_participants: Dict[str, BattleParticipant] = {}
                        team_b_participants: Dict[str, BattleParticipant] = {}
                        for p in participants_a:
                            user_college = self._get_user_college(p.student_id, session)
                            if user_college == battle.college_a:
                                team_a_participants[p.student_id] = p
                            elif user_college == battle.college_b:
                                team_b_participants[p.student_id] = p
                        
                        self.current_battle = {
                            "id": battle.id,
                            "college_a": battle.college_a,
                            "college_b": battle.college_b,
                            "score_a": battle.score_a,
                            "score_b": battle.score_b,
                            "participants_a": len(team_a_participants),
                            "participants_b": len(team_b_participants),
                            "start_date": battle.start_date.strftime("%Y-%m-%d") if battle.start_date else "",
                            "end_date": battle.end_date.strftime("%Y-%m-%d") if battle.end_date else ""
                        }
                        # 참가자 전체 목록 저장 (학번별 총 베팅 합산)
                        participant_list = []
                        bet_sum_map: Dict[str, int] = {}
                        for p in participants_a:
                            bet_sum_map[p.student_id] = bet_sum_map.get(p.student_id, 0) + p.bet_amount
                        
                        # 단과대별로 그룹화
                        participants_by_college_dict: Dict[str, List[Dict[str, Any]]] = {}
                        for sid, total_bet in bet_sum_map.items():
                            # 사용자 정보 조회하여 닉네임과 단과대 가져오기
                            user = session.exec(
                                select(User).where(User.student_id == sid)
                            ).first()
                            nickname = user.nickname if user else sid
                            college = user.college if user else "기타"
                            
                            participant_data = {
                                "student_id": sid,
                                "nickname": nickname,
                                "bet_amount": total_bet,
                            }
                            
                            # 단과대별로 그룹화
                            if college not in participants_by_college_dict:
                                participants_by_college_dict[college] = []
                            participants_by_college_dict[college].append(participant_data)
                        
                        # 각 단과대별로 베팅 포인트 기준 내림차순 정렬 후 상위 5명만 선택
                        college_a_list = participants_by_college_dict.get(battle.college_a, [])
                        college_b_list = participants_by_college_dict.get(battle.college_b, [])
                        
                        # 단과대 A 상위 5명
                        sorted_a = sorted(college_a_list, key=lambda x: x["bet_amount"], reverse=True)
                        top_a = []
                        for idx, p in enumerate(sorted_a[:5], 1):
                            p_with_rank = p.copy()
                            p_with_rank["rank"] = idx
                            top_a.append(p_with_rank)
                        
                        # 단과대 B 상위 5명
                        sorted_b = sorted(college_b_list, key=lambda x: x["bet_amount"], reverse=True)
                        top_b = []
                        for idx, p in enumerate(sorted_b[:5], 1):
                            p_with_rank = p.copy()
                            p_with_rank["rank"] = idx
                            top_b.append(p_with_rank)
                        
                        self.college_a_participants = top_a
                        self.college_b_participants = top_b
                        self.current_battle_participants = participant_list
                        return
                
                self.current_battle = None
                self.current_battle_participants = []
                self.college_a_participants = []
                self.college_b_participants = []
                
        except Exception as e:
            logger.error(f"대항전 로드 오류: {e}", exc_info=True)
            self.current_battle = None
    
    async def join_battle(self):
        """대항전 참가 및 베팅"""
        if not self.is_logged_in or not self.current_battle:
            self.battle_error_message = "대항전 정보를 불러올 수 없습니다."
            return
        
        if self.battle_bet_amount <= 0:
            self.battle_error_message = "베팅 포인트를 입력해주세요."
            return
        
        if self.battle_bet_amount > self.current_user_points:
            self.battle_error_message = "보유 포인트가 부족합니다."
            return
        
        try:
            from sqlmodel import Session, create_engine, select
            import os
            
            battle_id = self.current_battle["id"]
            
            db_path = os.path.join(os.getcwd(), "reflex.db")
            db_url = f"sqlite:///{db_path}"
            engine = create_engine(db_url, echo=False)
            
            with Session(engine) as session:
                # 오늘 날짜에 이미 참가했는지 확인 (하루 한 번 제한)
                today = date.today()
                existing_participant = session.exec(
                    select(BattleParticipant).where(
                        BattleParticipant.battle_id == battle_id,
                        BattleParticipant.student_id == self.current_user_id,
                        BattleParticipant.joined_at >= datetime.combine(today, datetime.min.time()),
                        BattleParticipant.joined_at < datetime.combine(today + timedelta(days=1), datetime.min.time())
                    )
                ).first()
                
                if existing_participant:
                    self.battle_error_message = "오늘은 이미 참가하셨습니다. 하루에 한 번만 참가할 수 있습니다."
                    return
                
                # 사용자 조회 및 포인트 차감
                user = session.exec(
                    select(User).where(User.student_id == self.current_user_id)
                ).first()
                
                if not user:
                    self.battle_error_message = "사용자를 찾을 수 없습니다."
                    return
                
                user.current_points -= self.battle_bet_amount
                self.current_user_points = user.current_points
                session.add(user)
                
                # 포인트 차감 로그 기록
                from ..models import PointsLog
                points_log = PointsLog(
                    student_id=self.current_user_id,
                    log_date=date.today(),
                    points=-self.battle_bet_amount,  # 음수로 기록
                    source="battle_participation",
                    description=f"대항전 참가 ({self.current_battle.get('college_a', '')} vs {self.current_battle.get('college_b', '')})"
                )
                session.add(points_log)
                
                # 참가자 등록
                participant = BattleParticipant(
                    battle_id=battle_id,
                    student_id=self.current_user_id,
                    bet_amount=self.battle_bet_amount,
                    reward_amount=0,
                    joined_at=datetime.now()
                )
                session.add(participant)
                
                # 대항전 점수 업데이트
                battle = session.exec(select(Battle).where(Battle.id == battle_id)).first()
                if battle:
                    if battle.college_a == self.current_user_college:
                        battle.score_a += self.battle_bet_amount
                    elif battle.college_b == self.current_user_college:
                        battle.score_b += self.battle_bet_amount
                    session.add(battle)
                
                session.commit()
            
            self.battle_bet_amount = 0
            self.battle_error_message = ""
            
            # 대결 정보 새로고침
            await self.load_current_battle()
            
            logger.info(f"대항전 참가 완료: {self.current_user_id}")
            
        except Exception as e:
            self.battle_error_message = f"대항전 참가 실패: {str(e)}"
            logger.error(f"대항전 참가 오류: {e}")
    
    async def load_previous_battles(self):
        """저번주 대결 결과 로드"""
        try:
            today = date.today()
            last_monday = self._get_week_start_end(today)[0] - timedelta(days=7)
            
            from sqlmodel import Session, create_engine, select
            import os
            
            db_path = os.path.join(os.getcwd(), "reflex.db")
            db_url = f"sqlite:///{db_path}"
            engine = create_engine(db_url, echo=False)
            
            with Session(engine) as session:
                statement = select(Battle).where(
                    Battle.start_date == last_monday,
                    Battle.status == "FINISHED"
                )
                battles = list(session.exec(statement).all())
                
                result = []
                for battle in battles:
                    result.append(
                        {
                            "college_a": battle.college_a,
                            "college_b": battle.college_b,
                            "score_a": battle.score_a,
                            "score_b": battle.score_b,
                            "winner": battle.winner,
                            "start_date": battle.start_date.strftime("%Y-%m-%d") if battle.start_date else "",
                            "end_date": battle.end_date.strftime("%Y-%m-%d") if getattr(battle, "end_date", None) else "",
                        }
                    )
                
                self.previous_battles = result
                
        except Exception as e:
            logger.error(f"저번주 대결 결과 로드 오류: {e}", exc_info=True)
            self.previous_battles = []
    
    async def load_personal_rankings(self):
        """개인 포인트 랭킹 로드 (1~10등)"""
        try:
            from sqlmodel import Session, create_engine, select, desc
            import os
            
            db_path = os.path.join(os.getcwd(), "reflex.db")
            db_url = f"sqlite:///{db_path}"
            engine = create_engine(db_url, echo=False)
            
            with Session(engine) as session:
                # 포인트 순으로 정렬하여 상위 10명 조회
                statement = select(User).order_by(desc(User.current_points)).limit(10)
                top_users = list(session.exec(statement).all())
                
                result = []
                for rank, user in enumerate(top_users, start=1):
                    result.append({
                        "rank": rank,
                        "student_id": user.student_id,
                        "nickname": user.nickname,
                        "college": user.college,
                        "points": user.current_points
                    })
                
                self.personal_rankings = result
                
        except Exception as e:
            logger.error(f"개인 랭킹 로드 오류: {e}", exc_info=True)
            self.personal_rankings = []
    
    async def load_ranking_data(self):
        """랭킹 페이지 데이터 로드 (저번주 대결 + 개인 랭킹)"""
        await self.load_previous_battles()
        await self.load_personal_rankings()



