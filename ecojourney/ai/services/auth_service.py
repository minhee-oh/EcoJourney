from typing import Optional
import sqlite3
import bcrypt

from ecojourney.db import get_connection
from ecojourney.schemas.user import UserCreate, User


# ======================================================
# 내부 전용: student_id로 users 테이블 row 조회
# ======================================================
def _get_user_row(student_id: str) -> Optional[sqlite3.Row]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM users WHERE student_id = ?",
        (student_id,),
    )
    row = cur.fetchone()
    conn.close()
    return row


# ======================================================
# 회원가입: 비밀번호 해싱 후 users 테이블에 저장
# ======================================================
def create_user(user: UserCreate) -> None:
    conn = get_connection()
    cur = conn.cursor()

    # 비밀번호 해시 생성 (bcrypt)
    hashed = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt())
    hashed_str = hashed.decode("utf-8")

    try:
        cur.execute(
            """
            INSERT INTO users (student_id, password_hash, college)
            VALUES (?, ?, ?)
            """,
            (user.student_id, hashed_str, user.college),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        # PK(student_id) 중복 등은 상위에서 처리
        raise
    finally:
        conn.close()


# ======================================================
# 로그인 검증: ID + 비밀번호만 체크
# ======================================================
def verify_user(student_id: str, password: str) -> bool:
    """
    단과대(college)는 검증에 사용하지 않고,
    로그인 성공 후 별도로 조회해서 응답에 포함한다.
    """
    row = _get_user_row(student_id)
    if row is None:
        return False

    stored_hash = row["password_hash"]
    if not stored_hash:
        return False

    return bcrypt.checkpw(
        password.encode("utf-8"),
        stored_hash.encode("utf-8"),
    )


# ======================================================
# 유저 정보 조회: DB row → User 스키마로 변환
# ======================================================
def get_user(student_id: str) -> Optional[User]:
    row = _get_user_row(student_id)
    if row is None:
        return None

    return User(
        student_id=row["student_id"],
        college=row["college"],
        current_points=row["current_points"],
        created_at=row["created_at"],
    )
