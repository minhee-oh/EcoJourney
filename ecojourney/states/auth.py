"""
사용자 인증 관련 State
"""

import reflex as rx
from typing import Optional
import sqlite3
import logging
import json
import hashlib
from pydantic import ValidationError
from .base import BaseState
from ..ai.services import auth_service
from ..schemas.user import UserCreate

logger = logging.getLogger(__name__)


class AuthState(BaseState):
    """
    사용자 인증 관련 상태 및 로직
    """
    # 사용자 인증 관련 상태
    current_user_id: Optional[str] = None
    current_user_nickname: Optional[str] = None
    current_user_college: Optional[str] = None
    current_user_points: int = 0
    is_logged_in: bool = False

    # 로그인/회원가입 폼 상태
    login_student_id: str = ""
    login_password: str = ""
    signup_student_id: str = ""
    signup_password: str = ""
    signup_nickname: str = ""
    signup_college: str = ""
    auth_error_message: str = ""

    # 쿠키를 사용한 세션 저장 (Reflex 내장 기능)
    _session_user_id: str = rx.Cookie("")

    def _save_session_to_storage(self):
        """로그인 세션을 브라우저 localStorage 및 쿠키에 저장"""
        # 쿠키에 user_id 저장 (Reflex 방식)
        self._session_user_id = self.current_user_id or ""

        # localStorage에도 저장 (호환성을 위해)
        yield rx.call_script(
            f"""
            localStorage.setItem('eco_user_id', '{self.current_user_id}');
            localStorage.setItem('eco_user_college', '{self.current_user_college}');
            localStorage.setItem('eco_user_points', '{self.current_user_points}');
            localStorage.setItem('eco_is_logged_in', 'true');
            """
        )

    def _clear_session_storage(self):
        """localStorage 및 쿠키에서 세션 정보 삭제"""
        # 쿠키 삭제
        self._session_user_id = ""

        # localStorage 삭제
        yield rx.call_script(
            """
            localStorage.removeItem('eco_user_id');
            localStorage.removeItem('eco_user_college');
            localStorage.removeItem('eco_user_points');
            localStorage.removeItem('eco_is_logged_in');
            """
        )

    def check_and_restore_session(self):
        """
        페이지 로드 시 쿠키에서 세션을 확인하고 복원
        """
        # 이미 로그인되어 있으면 복원할 필요 없음
        if self.is_logged_in:
            return

        # 쿠키에서 user_id 확인
        user_id = self._session_user_id

        if not user_id or user_id == "":
            return

        try:
            # auth_service를 사용하여 사용자 존재 여부 확인
            from ..ai.services.auth_service import get_user

            user = get_user(user_id)
            if not user:
                # 사용자가 존재하지 않으면 세션 삭제
                yield from self._clear_session_storage()
                return

            # 세션 복원
            self.current_user_id = user.student_id
            self.current_user_nickname = user.nickname
            self.current_user_college = user.college
            self.current_user_points = user.current_points
            self.is_logged_in = True
            # 챌린지 상태는 페이지 로드 시 자동으로 로드됨 (/info 페이지 on_load에 load_quiz_state 추가됨)

        except Exception as e:
            logger.error(f"세션 복원 오류: {e}", exc_info=True)
            yield from self._clear_session_storage()
    
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
    
    def set_signup_nickname(self, value: str):
        self.signup_nickname = value
    
    def _hash_password(self, password: str) -> str:
        """비밀번호를 해시화합니다."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def signup(self):
        """회원가입 처리 (auth_service 사용 - FastAPI와 통합)"""
        self.auth_error_message = ""

        if not self.signup_student_id or not self.signup_password or not self.signup_nickname or not self.signup_college:
            self.auth_error_message = "모든 필드를 입력해주세요."
            return

        try:
            # 백엔드 Auth 서비스(bcrypt) 사용
            try:
                user_payload = UserCreate(
                    student_id=self.signup_student_id.strip(),
                    password=self.signup_password,
                    nickname=self.signup_nickname.strip(),
                    college=self.signup_college.strip(),
                )
            except ValidationError as ve:
                # 비밀번호 길이, 닉네임 길이 등 입력 검증 메시지 노출
                error_details = str(ve)
                if "password" in error_details.lower():
                    self.auth_error_message = "비밀번호는 최소 6자 이상 입력해주세요."
                elif "nickname" in error_details.lower():
                    self.auth_error_message = "닉네임은 2-20자 사이로 입력해주세요."
                else:
                    self.auth_error_message = "입력값을 확인해주세요."
                logger.warning(f"회원가입 검증 오류: {ve}")
                return
            try:
                auth_service.create_user(user_payload)
            except sqlite3.IntegrityError as e:
                error_msg = str(e)
                if "닉네임" in error_msg:
                    self.auth_error_message = "이미 사용 중인 닉네임입니다."
                else:
                    self.auth_error_message = "이미 존재하는 학번입니다."
                return
            
            # 가입 후 사용자 정보 조회
            user_info = auth_service.get_user(user_payload.student_id)
            if not user_info:
                self.auth_error_message = "회원정보를 불러오지 못했습니다."
                return
            
            # 로그인 상태로 전환
            self.current_user_id = user_info.student_id
            self.current_user_nickname = user_info.nickname
            self.current_user_college = user_info.college
            self.current_user_points = user_info.current_points
            self.is_logged_in = True
            
            # 로컬 스토리지 저장 시도 (EventSpec는 await 불가하므로 호출만 수행)
            if hasattr(rx, "set_local_storage"):
                try:
                    rx.set_local_storage(
                        "auth_user",
                        {
                            "student_id": self.current_user_id,
                            "nickname": self.current_user_nickname,
                            "college": self.current_user_college,
                            "current_points": self.current_user_points,
                        },
                    )
                except Exception as e:
                    logger.debug(f"로컬 스토리지 저장 실패(무시): {e}")
            
            # 폼 초기화
            self.signup_student_id = ""
            self.signup_password = ""
            self.signup_nickname = ""
            self.signup_college = ""

            logger.info(f"회원가입 성공: {self.current_user_id}")

            # 세션 저장
            yield from self._save_session_to_storage()

            return rx.redirect("/")

        except Exception as e:
            self.auth_error_message = f"회원가입 실패: {str(e)}"
            logger.error(f"회원가입 오류: {e}", exc_info=True)
    
    def login(self):
        """로그인 처리 (auth_service 사용 - FastAPI와 통합)"""
        self.auth_error_message = ""

        if not self.login_student_id or not self.login_password:
            self.auth_error_message = "학번과 비밀번호를 입력해주세요."
            return

        try:
            # 입력값 정규화
            login_id = self.login_student_id.strip()
            login_pw = self.login_password
            
            # 백엔드 검증 (해시 포함)
            ok = auth_service.verify_user(login_id, login_pw)
            if not ok:
                self.auth_error_message = "학번 또는 비밀번호가 올바르지 않습니다."
                return

            user_info = auth_service.get_user(login_id)
            if not user_info:
                self.auth_error_message = "존재하지 않는 학번입니다."
                return
            
            # 로그인 성공
            self.current_user_id = user_info.student_id
            self.current_user_nickname = user_info.nickname
            self.current_user_college = user_info.college
            self.current_user_points = user_info.current_points
            self.is_logged_in = True
            
            # 로컬 스토리지 저장 시도 (EventSpec는 await 불가하므로 호출만 수행)
            if hasattr(rx, "set_local_storage"):
                try:
                    rx.set_local_storage(
                        "auth_user",
                        {
                            "student_id": self.current_user_id,
                            "nickname": self.current_user_nickname,
                            "college": self.current_user_college,
                            "current_points": self.current_user_points,
                        },
                    )
                except Exception as e:
                    logger.debug(f"로컬 스토리지 저장 실패(무시): {e}")
            
            # 폼 초기화
            self.login_student_id = ""
            self.login_password = ""

            logger.info(f"로그인 성공: {self.current_user_id}")

            # 세션 저장
            yield from self._save_session_to_storage()
            # 챌린지 상태는 페이지 로드 시 자동으로 로드됨 (/info 페이지 on_load에 load_quiz_state 추가됨)

            return rx.redirect("/")

        except Exception as e:
            self.auth_error_message = f"로그인 실패: {str(e)}"
            logger.error(f"로그인 오류: {e}", exc_info=True)
    
    def logout(self):
        """로그아웃 처리"""
        if hasattr(rx, "remove_local_storage"):
            try:
                rx.remove_local_storage("auth_user")
            except Exception as e:
                logger.debug(f"로컬 스토리지 제거 실패(무시): {e}")
        self.current_user_id = None
        self.current_user_nickname = None
        self.current_user_college = None
        self.current_user_points = 0
        self.is_logged_in = False
        self.all_activities = []
        # 챌린지 상태는 로그아웃 후 페이지 이동 시 자동으로 초기화됨

        # 세션 스토리지 삭제
        yield from self._clear_session_storage()

        return rx.redirect("/")

    async def hydrate_auth(self):
        """클라이언트 로컬 스토리지에서 로그인 정보 복원"""
        try:
            # 현재 Reflex 0.8.x에서는 get_local_storage EventSpec await 불가 → 복원 생략
            return
        except Exception as e:
            logger.warning(f"로그인 정보 복원 실패: {e}")



