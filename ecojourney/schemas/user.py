# 파일 경로: ecojourney/schemas/user.py
# user.py는 로그인·회원가입·유저 조회에서 사용되는
# 요청/응답 데이터 구조를 정의하는 공통 스키마 파일이다.
from pydantic import BaseModel, Field
from pydantic import ConfigDict
from datetime import datetime


# ======================================================
# 공통 유저 기본 모델
#  - 여러 유저 관련 모델에서 공통으로 사용하는 필드 모음
#  - DB 조회 결과를 응답으로 보낼 때 기반이 되는 구조
# ======================================================
class UserBase(BaseModel):
    student_id: str = Field(..., description="학번 (로그인 ID)")
    college: str = Field(..., description="소속 단과대")
    current_points: int = Field(0, description="현재 보유 포인트")


# ======================================================
# 회원가입 요청 바디 모델
#  - 클라이언트가 회원가입 시 보내는 데이터 구조
#  - 비밀번호는 평문으로 전달되며, 저장 시 해싱됨
# ======================================================
class UserCreate(BaseModel):
    student_id: str = Field(..., description="학번 (로그인 ID)")
    password: str = Field(..., min_length=6, description="평문 비밀번호")
    college: str = Field(..., description="소속 단과대")


# ======================================================
# 로그인 요청 바디 모델
#  - 로그인 검증에 필요한 최소 정보만 포함
#  - 단과대 정보는 DB 조회 후 응답에 포함
# ======================================================
class UserLogin(BaseModel):
    student_id: str = Field(..., description="학번 (로그인 ID)")
    password: str = Field(..., min_length=6, description="로그인 비밀번호")


# ======================================================
# 유저 정보 응답 모델
#  - DB에서 조회한 row(sqlite3.Row)를
#    Pydantic 모델로 변환하기 위한 응답용 스키마
# ======================================================
class User(UserBase):
    created_at: datetime = Field(..., description="가입일")

    # Pydantic v2 설정:
    # DB row 객체의 속성을 그대로 읽어올 수 있도록 허용
    model_config = ConfigDict(from_attributes=True)
