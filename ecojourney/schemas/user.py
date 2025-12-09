from pydantic import BaseModel, Field
from datetime import datetime


# ======================================================
# 공통 유저 필드 (DB 조회·응답용 기본 구조)
# ======================================================
class UserBase(BaseModel):
    student_id: str = Field(..., description="학번 (로그인 ID)")
    college: str = Field(..., description="소속 단과대")
    current_points: int = Field(0, description="현재 보유 포인트")


# ======================================================
# 회원가입 요청 바디
# ======================================================
class UserCreate(BaseModel):
    student_id: str = Field(..., description="학번 (로그인 ID)")
    password: str = Field(..., min_length=6, description="평문 비밀번호")
    college: str = Field(..., description="소속 단과대")


# ======================================================
# 로그인 요청 바디 (단과대는 검증에 사용하지 않음)
# ======================================================
class UserLogin(BaseModel):
    student_id: str = Field(..., description="학번 (로그인 ID)")
    password: str = Field(..., min_length=6, description="로그인 비밀번호")


# ======================================================
# 유저 정보 응답 모델
# ======================================================
class User(UserBase):
    created_at: datetime = Field(..., description="가입일")

    class Config:
        # ORM 객체를 Pydantic 모델로 변환 허용
        orm_mode = True
