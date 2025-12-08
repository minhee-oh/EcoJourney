# 파일 경로: backend/main.py
from fastapi import FastAPI
from backend import coaching_api

app = FastAPI(
    title="EcoJourney - Carbon AI Coach API",
    description="개인 맞춤형 탄소 라이프스타일 진단 및 코칭 리포트를 제공하는 백엔드 API",
    version="1.0.0",
)

# 코칭 관련 엔드포인트 그룹 등록 (/api/v1/generate-feedback 등)
app.include_router(coaching_api.router)


@app.get("/")
def read_root():
    """
    서버 정상 동작 여부 확인용 엔드포인트.
    """
    return {"message": "EcoJourney Carbon AI Coach API is running successfully!"}


# 로컬 개발 환경 실행 예시:
# uvicorn backend.main:app --reload
if __name__ == "__main__":
    import uvicorn

    # 개발용 실행
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
