import sqlite3
from fastapi import APIRouter, HTTPException, status

from ecojourney.schemas.user import UserCreate, UserLogin, User
from ecojourney.ai.services.auth_service import (
    create_user,
    verify_user,
    get_user,
)


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


# ======================================================
# 회원가입
# ======================================================
@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(user: UserCreate):
    try:
        create_user(user)
    except sqlite3.IntegrityError:
        # 학번 중복 시 오류 반환
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 존재하는 학번입니다.",
        )
    return {"message": "회원가입이 완료되었습니다.", "student_id": user.student_id}


# ======================================================
# 로그인
#   - ID + PW만 검증
#   - 단과대(college)는 DB 조회 후 응답에 포함
# ======================================================
@router.post("/login")
def login(body: UserLogin):
    ok = verify_user(body.student_id, body.password)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="학번 또는 비밀번호가 올바르지 않습니다.",
        )

    user = get_user(body.student_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="존재하지 않는 사용자입니다.",
        )

    return {
        "message": "로그인 성공",
        "student_id": user.student_id,
        "college": user.college,
        "current_points": user.current_points,
    }


# ======================================================
# 유저 정보 조회 (디버깅/관리자용)
# ======================================================
@router.get("/users/{student_id}", response_model=User)
def get_user_info(student_id: str):
    user = get_user(student_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="존재하지 않는 사용자입니다.",
        )
    return user
