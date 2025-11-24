# 🚀 빠른 시작 가이드

## 1. 환경 설정

### 가상환경 생성 및 활성화

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python -m venv .venv
source .venv/bin/activate
```

> **참고**: `.venv`는 일반적으로 사용되는 가상환경 디렉토리 이름입니다. 이미 `.venv`가 있다면 활성화만 하면 됩니다.

### 의존성 설치

```bash
# 백엔드 의존성 설치
pip install -r backend/requirements.txt

# 프론트엔드 의존성 설치
pip install -r frontend/requirements.txt

# 또는 한 번에 설치
pip install -r backend/requirements.txt -r frontend/requirements.txt
```

## 2. 환경 변수 설정

프로젝트 루트에 `.env` 파일을 생성하고 Google Gemini API 키를 추가하세요:

```
GEMINI_API_KEY=your_gemini_api_key_here
```

### Gemini API 키 무료 발급 방법

1. **Google AI Studio 접속**
   - https://aistudio.google.com/app/apikey 접속
   - Google 계정으로 로그인

2. **API 키 생성**
   - "Create API Key" 버튼 클릭
   - 프로젝트 선택 또는 새 프로젝트 생성
   - 생성된 API 키를 복사

3. **무료 티어 정보**
   - `gemini-pro` 모델: **완전 무료** 사용 가능
   - 분당 요청 제한: 약 15회/분
   - 일일 요청 제한: 충분한 수준 (개인 프로젝트용으로 적합)
   - **결제 정보 불필요** - 무료 티어는 신용카드 등록 없이 사용 가능

4. **`.env` 파일 생성**
   - 프로젝트 루트 디렉토리에 `.env` 파일 생성
   - 다음 내용을 추가:
     ```
     GEMINI_API_KEY=여기에_발급받은_API_키_붙여넣기
     ```

> **참고**: 
> - Gemini API 키가 없어도 기본 기능은 사용할 수 있지만, AI 코칭 기능은 제한됩니다.
> - API 키는 환경 변수로 관리되며, 절대 Git에 커밋하지 마세요 (`.gitignore`에 포함되어 있습니다).
> - 무료 티어는 개발 및 테스트 목적으로 충분합니다.

## 3. 서버 실행

### 터미널 1: FastAPI 백엔드 서버 (포트 8001)

```bash
cd backend
uvicorn main:app --reload --port 8001
```

서버가 정상적으로 실행되면 다음 주소에서 API 문서를 확인할 수 있습니다:
- API 문서: http://localhost:8001/docs
- 대체 문서: http://localhost:8001/redoc

> **참고**: 포트 8001을 사용하는 이유는 Reflex와 포트 충돌을 방지하기 위함입니다.

### 터미널 2: Reflex 프론트엔드 (포트 3000)

```bash
cd frontend
reflex run
```

브라우저에서 자동으로 열리거나, 다음 주소로 접속하세요:
- Reflex 앱: http://localhost:3000
- Reflex는 자체 백엔드를 포트 3000에서 실행하며, WebSocket도 같은 포트를 사용합니다.

## 4. 사용 방법

1. **활동 입력**: 왼쪽 사이드바에서 카테고리를 선택하고 활동을 입력하세요
   - 예: 교통 > 자동차 > 30분
   - 예: 식품 > 쇠고기 > 1인분

2. **대시보드 확인**: 메인 화면에서 실시간으로 탄소 배출량을 확인하세요

3. **지구 아바타**: 아바타 탭에서 지구의 건강 상태를 확인하세요

4. **AI 코칭**: AI 코칭 탭에서 맞춤형 탄소 저감 제안을 받으세요

5. **배지 획득**: 다양한 활동을 통해 배지를 획득하세요

## 5. 문제 해결

### API 연결 오류
- FastAPI 서버가 실행 중인지 확인하세요 (포트 8001)
- `http://localhost:8001`에 접속 가능한지 확인하세요
- Reflex 서버는 포트 3000에서 실행되며, FastAPI 백엔드(포트 8001)의 API를 호출합니다

### Gemini API 오류
- `.env` 파일에 API 키가 올바르게 설정되었는지 확인하세요
- API 키가 유효한지 확인하세요

### Import 오류
- 가상환경이 활성화되어 있는지 확인하세요
- `pip install -r requirements.txt`를 다시 실행하세요

