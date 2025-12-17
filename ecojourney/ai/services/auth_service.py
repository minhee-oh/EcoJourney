from typing import Optional
import hashlib
import sqlite3
from datetime import datetime
from sqlmodel import Session, create_engine, select
import os

from ecojourney.models import User as UserModel
from ecojourney.schemas.user import UserCreate, User
from ecojourney.db.init_db import init_db


# DB 연결 설정 (Reflex와 동일한 DB 사용)
def _get_engine():
    """SQLModel 엔진 생성 (Reflex DB와 동일)"""
    db_path = os.path.join(os.getcwd(), "reflex.db")
    db_url = f"sqlite:///{db_path}"
    return create_engine(db_url, echo=False)


# 전역 엔진 (SQLModel용)
engine = _get_engine()


_db_ready = False


def _ensure_db():
    """DB 스키마가 준비되었는지 확인하고 없으면 생성."""
    global _db_ready
    if _db_ready:
        return
    init_db()  # reflex.db에 user 테이블 등 생성
    _db_ready = True


def get_connection():
    """sqlite3 커넥션 반환 (Row 접근 용이하게 설정)"""
    db_path = os.path.join(os.getcwd(), "reflex.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def _hash_password(password: str) -> str:
    """SHA256 해시 생성"""
    return hashlib.sha256(password.encode()).hexdigest()


# ======================================================
# 비밀번호 해싱 (SHA256 - Reflex AuthState와 동일)
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
# 회원가입: 비밀번호 해싱 후 user 테이블에 저장
# ======================================================
def create_user(user: UserCreate) -> None:
    _ensure_db()
    engine = _get_engine()

    # 비밀번호 해시 생성 (SHA256)
    hashed_password = _hash_password(user.password)

    try:
        with Session(engine) as session:
            # 닉네임 중복 확인
            existing_nickname = session.exec(
                select(UserModel).where(UserModel.nickname == user.nickname)
            ).first()
            if existing_nickname:
                import sqlite3
                raise sqlite3.IntegrityError("이미 사용 중인 닉네임입니다.")
            
            new_user = UserModel(
                student_id=user.student_id,
                password=hashed_password,
                nickname=user.nickname,
                college=user.college,
                current_points=0,
                created_at=datetime.now()
            )
            session.add(new_user)
            session.commit()
    except sqlite3.IntegrityError:
        raise
    except Exception as e:
        # student_id 중복 등의 오류는 상위에서 처리
        error_str = str(e).lower()
        if "unique" in error_str or "duplicate" in error_str or "constraint" in error_str:
            import sqlite3
            raise sqlite3.IntegrityError("이미 존재하는 학번입니다.")
        raise


# ======================================================
# 로그인 검증: ID + 비밀번호만 체크
# ======================================================
def verify_user(student_id: str, password: str) -> bool:
    """
    학번과 비밀번호를 검증합니다.
    단과대(college)는 검증에 사용하지 않고, 로그인 성공 후 별도로 조회합니다.
    """
    _ensure_db()
    engine = _get_engine()

    with Session(engine) as session:
        statement = select(UserModel).where(UserModel.student_id == student_id)
        user = session.exec(statement).first()

        if not user:
            return False

        # 비밀번호 검증 (SHA256)
        hashed_password = _hash_password(password)
        return user.password == hashed_password


# ======================================================
# 유저 정보 조회: DB → User 스키마로 변환
# ======================================================
def get_user(student_id: str) -> Optional[User]:
    """
    학번으로 사용자 정보를 조회합니다.
    """
    _ensure_db()
    engine = _get_engine()

    with Session(engine) as session:
        statement = select(UserModel).where(UserModel.student_id == student_id)
        user = session.exec(statement).first()

        if not user:
            return None

        return User(
            student_id=user.student_id,
            nickname=user.nickname,
            college=user.college,
            current_points=user.current_points,
            created_at=user.created_at,
        )

