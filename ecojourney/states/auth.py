"""
사용자 인증 관련 State
"""

import reflex as rx
from typing import Optional
import hashlib
import logging
from .base import BaseState
from ..models import User

logger = logging.getLogger(__name__)


class AuthState(BaseState):
    """
    사용자 인증 관련 상태 및 로직
    """
    # 사용자 인증 관련 상태
    current_user_id: Optional[str] = None
    current_user_college: Optional[str] = None
    current_user_points: int = 0
    is_logged_in: bool = False
    
    # 로그인/회원가입 폼 상태
    login_student_id: str = ""
    login_password: str = ""
    signup_student_id: str = ""
    signup_password: str = ""
    signup_college: str = ""
    auth_error_message: str = ""
    
    # Setter 메서드들 (명시적 정의)
    def set_login_student_id(self, value: str):
        self.login_student_id = value
    
    def set_login_password(self, value: str):
        self.login_password = value
    
    def set_signup_student_id(self, value: str):
        self.signup_student_id = value
    
    def set_signup_password(self, value: str):
        self.signup_password = value
    
    def set_signup_college(self, value: str):
        self.signup_college = value
    
    def _hash_password(self, password: str) -> str:
        """비밀번호를 해시화합니다."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    async def signup(self):
        """회원가입 처리"""
        self.auth_error_message = ""
        
        if not self.signup_student_id or not self.signup_password or not self.signup_college:
            self.auth_error_message = "모든 필드를 입력해주세요."
            return
        
        try:
            # 새 사용자 생성 (기존 사용자 확인은 저장 시도 후 오류로 처리)
            hashed_password = self._hash_password(self.signup_password)
            new_user = User(
                student_id=self.signup_student_id,
                password=hashed_password,
                college=self.signup_college,
                current_points=0
            )
            
            try:
                # CarbonLog와 동일한 방식으로 저장
                # SQLModel Session을 직접 사용
                from sqlmodel import Session, create_engine
                import os
                
                # 데이터베이스 파일 경로 (Reflex 기본값)
                db_path = os.path.join(os.getcwd(), "reflex.db")
                db_url = f"sqlite:///{db_path}"
                engine = create_engine(db_url, echo=False)
                
                with Session(engine) as session:
                    session.add(new_user)
                    session.commit()
                    session.refresh(new_user)
            except Exception as save_error:
                error_str = str(save_error).lower()
                if "unique" in error_str or "duplicate" in error_str or "constraint" in error_str:
                    self.auth_error_message = "이미 존재하는 학번입니다."
                    return
                else:
                    raise  # 다른 오류는 다시 발생시킴
            
            # 로그인 상태로 전환
            self.current_user_id = self.signup_student_id
            self.current_user_college = self.signup_college
            self.current_user_points = 0
            self.is_logged_in = True
            
            # 폼 초기화
            self.signup_student_id = ""
            self.signup_password = ""
            self.signup_college = ""
            
            logger.info(f"회원가입 성공: {self.current_user_id}")
            return rx.redirect("/")
            
        except Exception as e:
            self.auth_error_message = f"회원가입 실패: {str(e)}"
            logger.error(f"회원가입 오류: {e}")
    
    async def login(self):
        """로그인 처리"""
        self.auth_error_message = ""
        
        if not self.login_student_id or not self.login_password:
            self.auth_error_message = "학번과 비밀번호를 입력해주세요."
            return
        
        try:
            # 사용자 조회 (student_id로 검색)
            # SQLModel Session을 직접 사용하여 조회 (회원가입과 동일한 방식)
            user = None
            try:
                from sqlmodel import Session, create_engine, select
                import os
                
                db_path = os.path.join(os.getcwd(), "reflex.db")
                db_url = f"sqlite:///{db_path}"
                engine = create_engine(db_url, echo=False)
                
                with Session(engine) as session:
                    statement = select(User).where(User.student_id == self.login_student_id)
                    result = session.exec(statement).first()
                    if result:
                        user = result
            except Exception as session_error:
                logger.error(f"사용자 조회 오류: {session_error}", exc_info=True)
                self.auth_error_message = f"로그인 처리 중 오류가 발생했습니다: {str(session_error)}"
                return
            
            if not user:
                self.auth_error_message = "존재하지 않는 학번입니다."
                return
            
            # 비밀번호 확인
            hashed_password = self._hash_password(self.login_password)
            if user.password != hashed_password:
                self.auth_error_message = "비밀번호가 일치하지 않습니다."
                return
            
            # 로그인 성공
            self.current_user_id = user.student_id
            self.current_user_college = user.college
            self.current_user_points = user.current_points
            self.is_logged_in = True
            
            # 폼 초기화
            self.login_student_id = ""
            self.login_password = ""
            
            # 저장된 오늘 날짜의 데이터 자동 불러오기 (CarbonState에 있으므로 조건부 호출)
            # load_saved_activities는 CarbonState에 정의되어 있음
            if hasattr(self, 'load_saved_activities'):
                try:
                    await self.load_saved_activities()
                except Exception as load_error:
                    logger.warning(f"저장된 데이터 불러오기 실패 (무시): {load_error}")
            
            logger.info(f"로그인 성공: {self.current_user_id}")
            return rx.redirect("/")
            
        except Exception as e:
            self.auth_error_message = f"로그인 실패: {str(e)}"
            logger.error(f"로그인 오류: {e}")
    
    async def logout(self):
        """로그아웃 처리"""
        self.current_user_id = None
        self.current_user_college = None
        self.current_user_points = 0
        self.is_logged_in = False
        self.all_activities = []
        return rx.redirect("/")



