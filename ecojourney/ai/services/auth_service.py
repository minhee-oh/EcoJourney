# 파일 경로: ecojourney/ai/services/auth_service.py
# 회원가입·로그인·유저 조회에 필요한
# DB 처리와 비밀번호 검증을 실제로 수행하는 인증 로직 담당 파일
from typing import Optional

import sqlite3
import bcrypt

from ecojourney.db import get_connection
from ecojourney.schemas.user import UserCreate, User


# ======================================================
# 내부 전용: student_id로 users 테이블 row 조회
# ======================================================
def _get_user_row(student_id: str) -> Optional[sqlite3.Row]:
    """
    - DB 연결/쿼리 수행
    - 항상 conn.close() 되도록 보장
    - sqlite3.Error는 상위로 그대로 올림 (라우터에서 처리)
    """
    conn: Optional[sqlite3.Connection] = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM users WHERE student_id = ?",
            (student_id,),
        )
        row = cur.fetchone()
        return row
    finally:
        if conn is not None:
            conn.close()


# ======================================================
# 회원가입: 비밀번호 해싱 후 users 테이블에 저장
# ======================================================
def create_user(user: UserCreate) -> None:
    """
    - bcrypt로 비밀번호 해시 생성
    - users 테이블에 INSERT
    - IntegrityError(학번 중복)는 상위에서 처리
    - 기타 sqlite3.Error는 상위로 전파 (라우터에서 JSON 응답 처리)
    """
    # 1) 비밀번호 해시 생성 (bcrypt 예외 처리)
    try:
        hashed = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt())
        hashed_str = hashed.decode("utf-8")
    except (ValueError, TypeError, bcrypt.error) as e:
        # 해시 생성 자체가 실패한 경우 → 치명적이므로 상위에서 처리하게 raise
        print(f"[AUTH_SERVICE][CREATE_USER] bcrypt hash error: {e}")
        raise

    conn: Optional[sqlite3.Connection] = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO users (student_id, password_hash, college)
            VALUES (?, ?, ?)
            """,
            (user.student_id, hashed_str, user.college),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        # PK(student_id) 중복 등은 상위 라우터에서 400으로 처리
        if conn is not None:
            conn.rollback()
        raise
    except sqlite3.Error as e:
        # 기타 DB 에러 → 상위 라우터에서 500 처리
        if conn is not None:
            conn.rollback()
        print(f"[AUTH_SERVICE][CREATE_USER] DB error: {e}")
        raise
    finally:
        if conn is not None:
            conn.close()


# ======================================================
# 로그인 검증: ID + 비밀번호만 체크
# ======================================================
def verify_user(student_id: str, password: str) -> bool:
    """
    - 단과대(college)는 검증에 사용하지 않고,
      로그인 성공 후 별도로 조회해서 응답에 포함한다.
    - DB 에러 발생 시 sqlite3.Error를 상위로 전파
    - 해시가 비정상(손상/형식 오류)일 경우 False를 반환
    """
    try:
        row = _get_user_row(student_id)
    except sqlite3.Error as e:
        print(f"[AUTH_SERVICE][VERIFY_USER] DB error: {e}")
        # 라우터에서 sqlite3.Error를 받아서 JSON 에러 응답 생성
        raise

    if row is None:
        return False

    stored_hash = row["password_hash"]
    if not stored_hash:
        return False

    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            stored_hash.encode("utf-8"),
        )
    except (ValueError, TypeError, bcrypt.error) as e:
        # 해시 형식이 깨져 있거나, 비교 중 문제가 생기면 로그인 실패로 처리
        print(f"[AUTH_SERVICE][VERIFY_USER] bcrypt check error: {e}")
        return False


# ======================================================
# 유저 정보 조회: DB row → User 스키마로 변환
# ======================================================
def get_user(student_id: str) -> Optional[User]:
    """
    - DB에서 사용자 row 조회
    - sqlite3.Error 발생 시 상위로 전파 (라우터에서 처리)
    """
    try:
        row = _get_user_row(student_id)
    except sqlite3.Error as e:
        print(f"[AUTH_SERVICE][GET_USER] DB error: {e}")
        raise

    if row is None:
        return None

    return User(
        student_id=row["student_id"],
        college=row["college"],
        current_points=row["current_points"],
        created_at=row["created_at"],
    )
