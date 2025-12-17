# 파일 경로: ecojourney/ai/ai_main.py
from fastapi import FastAPI

# 로그인 관련 라우터
from ecojourney.api.auth import router as auth_router

# AI 코칭 라우터 (지금 방금 보여준 coaching_api.py의 router)
from ecojourney.ai.coaching_api import router as coaching_router
app = FastAPI(
    title="EcoJourney - Carbon AI Coach API",
    description="개인 맞춤형 탄소 라이프스타일 진단 및 코칭 리포트를 제공하는 백엔드 API",
    version="1.0.0",
)

# ✅ 로그인 / 회원가입 API
app.include_router(auth_router)

# ✅ AI 피드백(API) – /api/v1/generate-feedback
app.include_router(coaching_router)
