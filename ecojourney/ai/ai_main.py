# 파일 경로: ecojourney/ai/ai_main.py
# FastAPI 서버를 실행하고,
# 로그인/회원가입과 AI 코칭 API를 하나로 묶는 메인 진입 파일
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# 🔹 로그인 / 회원가입 관련 라우터 (/auth/...)
from ecojourney.api.auth import router as auth_router

#  AI 코칭 라우터 (/api/v1/generate-feedback)
from ecojourney.ai.coaching_api import router as coaching_router


# ======================================================
# FastAPI 앱 기본 설정
#  - 서비스 이름, 설명, 버전 정보만 설정하는 부분
# ======================================================
app = FastAPI(
    title="EcoJourney - Carbon AI Coach API",
    description="개인 맞춤형 탄소 라이프스타일 진단 및 코칭 리포트를 제공하는 백엔드 API",
    version="1.0.0",
)


# ======================================================
# 전역 예외 핸들러
#  - 라우터 내부에서 처리하지 못한 모든 예외를 마지막에 한 번 더 잡아줌
#  - 서버가 500 에러로 그대로 죽지 않게 하고
#    항상 {status, error_message} 형태로 응답을 맞춰주는 역할
# ======================================================
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"[GLOBAL ERROR] {exc} (path: {request.url.path})")
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "error_message": "서버 내부 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
        },
    )


# ======================================================
# API 라우터 등록
#  - 아래 두 include_router 때문에 실제 엔드포인트들이 활성화됨
#    /auth/...           → 로그인 / 회원가입 / 유저 조회
#    /api/v1/generate-feedback → AI 피드백 생성
# ======================================================

# 로그인 / 회원가입 API
app.include_router(auth_router)

# AI 피드백 API (/api/v1/generate-feedback)
app.include_router(coaching_router)
