# ecojourney/api/auth.py
# 회원가입·로그인·유저 조회 요청을 받아
# 인증 서비스 로직을 호출하고,
# 결과를 표준화된 JSON 응답으로 반환하는 API 라우터
import sqlite3
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from ecojourney.schemas.user import UserCreate, UserLogin
from ecojourney.ai.services.auth_service import (
    create_user,
    verify_user,
    get_user,
)

router = APIRouter(prefix="/auth", tags=["auth"])


# ======================================================
# 회원가입
#  - users 테이블에 INSERT
#  - student_id(PK) 중복 시 400 반환
#  - DB 에러/예상 못한 에러도 서버가 죽지 않게 JSON으로 통일 반환
# ======================================================
@router.post("/signup")
def signup(user: UserCreate):
    try:
        create_user(user)

    # 중복 학번(UNIQUE/PK) → sqlite3.IntegrityError로 떨어짐
    # 그래서 프론트는 "이미 존재하는 학번"을 즉시 알 수 있음
    except sqlite3.IntegrityError:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"status": "error", "error_message": "이미 존재하는 학번입니다."},
        )

    # DB 자체 문제(파일 잠김, 스키마 문제 등) → 500 처리
    except sqlite3.Error as e:
        print(f"[AUTH][SIGNUP] DB Error: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "error_message": "회원가입 처리 중 데이터베이스 오류가 발생했습니다.",
            },
        )

    # 예상 못한 에러도 500으로 통일해서 서버가 죽지 않게 함
    except Exception as e:
        print(f"[AUTH][SIGNUP] Unknown Error: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "error_message": "회원가입 처리 중 알 수 없는 오류가 발생했습니다.",
            },
        )

    # 성공 응답도 표준 구조로 통일 (프론트는 status만 보고 분기 가능)
    return {
        "status": "success",
        "data": {"student_id": user.student_id, "college": user.college},
    }


# ======================================================
# 로그인
#  - verify_user()로 ID/PW만 검증
#  - 검증 성공하면 get_user()로 사용자 정보(단과대, 포인트)를 가져와 응답
#  - 실패/에러 응답도 표준 JSON 구조로 통일
# ======================================================
@router.post("/login")
def login(body: UserLogin):
    #  1) ID/PW 검증 단계
    try:
        ok = verify_user(body.student_id, body.password)

    except sqlite3.Error as e:
        # DB 조회 중 문제 → 500
        print(f"[AUTH][LOGIN] DB Error during verify_user: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "error_message": "로그인 검증 중 데이터베이스 오류가 발생했습니다."},
        )

    except Exception as e:
        # 예상 못한 오류 → 500
        print(f"[AUTH][LOGIN] Unknown Error during verify_user: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "error_message": "로그인 처리 중 알 수 없는 오류가 발생했습니다."},
        )

    # 2) 비밀번호 틀림/유저 없음 → 401
    if not ok:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"status": "error", "error_message": "학번 또는 비밀번호가 올바르지 않습니다."},
        )

    # 3) 검증 성공 후 사용자 정보 조회
    try:
        user = get_user(body.student_id)

    except sqlite3.Error as e:
        print(f"[AUTH][LOGIN] DB Error during get_user: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "error_message": "사용자 정보를 조회하는 중 데이터베이스 오류가 발생했습니다."},
        )

    except Exception as e:
        print(f"[AUTH][LOGIN] Unknown Error during get_user: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "error_message": "사용자 정보를 가져오는 중 알 수 없는 오류가 발생했습니다."},
        )

    # 유저가 없으면 404
    if user is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"status": "error", "error_message": "존재하지 않는 사용자입니다."},
        )

    # 성공 응답 표준화
    return {
        "status": "success",
        "data": {
            "student_id": user.student_id,
            "college": user.college,
            "current_points": user.current_points,
        },
    }


# ======================================================
# 유저 정보 조회 (디버깅/관리자용)
#  - 특정 학번의 유저 정보를 조회해 확인하기 위한 엔드포인트
# ======================================================
@router.get("/users/{student_id}")
def get_user_info(student_id: str):
    try:
        user = get_user(student_id)

    except sqlite3.Error as e:
        print(f"[AUTH][GET_USER] DB Error: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "error_message": "사용자 정보를 조회하는 중 데이터베이스 오류가 발생했습니다."},
        )

    except Exception as e:
        print(f"[AUTH][GET_USER] Unknown Error: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "error_message": "사용자 정보를 가져오는 중 알 수 없는 오류가 발생했습니다."},
        )

    if user is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"status": "error", "error_message": "존재하지 않는 사용자입니다."},
        )

    # created_at은 datetime이라 JSON 직렬화를 위해 isoformat으로 변환
    return {
        "status": "success",
        "data": {
            "student_id": user.student_id,
            "college": user.college,
            "current_points": user.current_points,
            "created_at": user.created_at.isoformat() if hasattr(user, "created_at") else None,
        },
    }
