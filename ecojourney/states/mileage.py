"""
마일리지 환산 관련 State
"""

import reflex as rx
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from .battle import BattleState
from ..models import MileageRequest, User

logger = logging.getLogger(__name__)


class MileageState(BattleState):
    """
    마일리지 환산 관련 상태 및 로직
    """
    mileage_request_points: int = 0
    mileage_error_message: str = ""
    mileage_conversion_logs: List[Dict[str, Any]] = []  # 환산 내역 로그
    
    def set_mileage_request_points(self, value: str):
        """환산할 포인트 설정 (1000점 단위로만 입력 가능)"""
        try:
            if value:
                input_value = int(value)
                # 1000점 단위로 반올림 (1000점 미만은 0으로 처리)
                self.mileage_request_points = (input_value // 1000) * 1000
            else:
                self.mileage_request_points = 0
        except ValueError:
            self.mileage_request_points = 0
    
    async def request_mileage_conversion(self):
        """마일리지 환산 신청 (자동 승인)"""
        if not self.is_logged_in:
            self.mileage_error_message = "로그인이 필요합니다."
            return
        
        if self.mileage_request_points < 1000:
            self.mileage_error_message = "환산 신청은 최소 1000점 이상부터 가능합니다."
            return
        
        if self.mileage_request_points > self.current_user_points:
            self.mileage_error_message = "보유 포인트가 부족합니다."
            return
        
        try:
            from sqlmodel import Session, create_engine, select
            import os
            
            # 환산 비율: 포인트 1000점 = 비컴 마일리지 10점 (100:1 비율)
            # 즉, 포인트 1000점당 마일리지 10점
            converted_mileage = (self.mileage_request_points // 1000) * 10
            
            db_path = os.path.join(os.getcwd(), "reflex.db")
            db_url = f"sqlite:///{db_path}"
            engine = create_engine(db_url, echo=False)
            
            with Session(engine) as session:
                # 사용자 조회 및 포인트 차감
                user = session.exec(
                    select(User).where(User.student_id == self.current_user_id)
                ).first()
                
                if not user:
                    self.mileage_error_message = "사용자를 찾을 수 없습니다."
                    return
                
                user.current_points -= self.mileage_request_points
                self.current_user_points = user.current_points
                session.add(user)
                
                # 환산 신청 기록 (자동 승인)
                request = MileageRequest(
                    student_id=self.current_user_id,
                    request_points=self.mileage_request_points,
                    converted_mileage=converted_mileage,
                    status="APPROVED",  # 자동 승인
                    processed_at=datetime.now()
                )
                session.add(request)
                session.commit()
            
            # 환산 내역 로그에 추가
            await self.load_mileage_conversion_logs()
            
            # 환산된 포인트와 마일리지 저장 (로그용)
            converted_points = self.mileage_request_points
            
            self.mileage_request_points = 0
            self.mileage_error_message = ""
            logger.info(f"마일리지 환산 완료: {self.current_user_id}, 포인트: {converted_points}, 마일리지: {converted_mileage}")
            
            # 마이페이지 데이터 새로고침 (포인트 정보 업데이트)
            if hasattr(self, 'load_mypage_data'):
                await self.load_mypage_data()
            
        except Exception as e:
            self.mileage_error_message = f"마일리지 환산 실패: {str(e)}"
            logger.error(f"마일리지 환산 오류: {e}", exc_info=True)
    
    async def load_mileage_conversion_logs(self):
        """마일리지 환산 내역 로드"""
        if not self.is_logged_in:
            self.mileage_conversion_logs = []
            return
        
        try:
            from sqlmodel import Session, create_engine, select, desc
            import os
            
            db_path = os.path.join(os.getcwd(), "reflex.db")
            db_url = f"sqlite:///{db_path}"
            engine = create_engine(db_url, echo=False)
            
            with Session(engine) as session:
                statement = select(MileageRequest).where(
                    MileageRequest.student_id == self.current_user_id
                ).order_by(desc(MileageRequest.processed_at))
                
                requests = list(session.exec(statement).all())
                
                result = []
                for req in requests:
                    result.append({
                        "date": req.processed_at.strftime("%Y-%m-%d %H:%M:%S") if req.processed_at else "",
                        "request_points": req.request_points,
                        "converted_mileage": req.converted_mileage,
                        "status": req.status
                    })
                
                self.mileage_conversion_logs = result
                
        except Exception as e:
            logger.error(f"마일리지 환산 내역 로드 오류: {e}", exc_info=True)
            self.mileage_conversion_logs = []



