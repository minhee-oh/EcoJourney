# 🚀 빠른 시작 가이드

> **중요**: 아래 명령어는 기본적으로 **프로젝트 루트(루트 `README.md`, `rxconfig.py`가 있는 위치)**에서 실행한다고 가정합니다.

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
# Python 의존성 설치
pip install -r requirements.txt

# Node.js 의존성 설치 (react-player 등)
npm install
```

## 2. 환경 변수 설정

프로젝트 루트에 `.env` 파일을 생성하고 Google Gemini API 키를 추가하세요:

```
GEMINI_API_KEY=your_gemini_api_key_here

# 탄소 배출량 계산 API (선택사항)
# API 키가 없어도 로컬 배출 계수로 계산됩니다
CLIMATIQ_API_KEY=your_climatiq_api_key_here
CARBONCLOUD_API_KEY=your_carboncloud_api_key_here
```

### Gemini API 키 무료 발급 방법

1. **Google AI Studio 접속**
   - `https://aistudio.google.com/app/apikey` 접속
   - Google 계정으로 로그인

2. **API 키 생성**
   - "Create API Key" 버튼 클릭
   - 프로젝트 선택 또는 새 프로젝트 생성
   - 생성된 API 키를 복사

3. **무료 티어 정보**
   - 분당 요청 제한/일일 제한은 정책에 따라 달라질 수 있습니다.
   - 무료 티어는 개발 및 테스트 목적으로 충분할 수 있습니다.

4. **`.env` 파일 생성**
   - 프로젝트 루트 디렉토리에 `.env` 파일 생성
   - 다음 내용을 추가:
     ```
     GEMINI_API_KEY=여기에_발급받은_API_키_붙여넣기
     ```

> **참고**:
> - API 키는 환경 변수로 관리되며, 절대 Git에 커밋하지 마세요 (`.gitignore`에 포함).

## 3. 데이터베이스 초기화

모델을 정의했으므로 데이터베이스를 초기화하고 마이그레이션을 적용해야 합니다:

```bash
# 1. DB 초기화 (아직 안 했다면)
reflex db init

# 2. 변경 사항(작성한 모델) 감지 및 스크립트 생성
reflex db makemigrations --message "init models"

# 3. 실제 DB에 테이블 생성
reflex db migrate
```

## 4. 서버 실행

### Reflex 앱 실행 (프론트엔드 + 백엔드 통합)

Reflex는 프론트엔드와 백엔드를 하나로 통합한 Full-stack 프레임워크입니다.  
별도의 백엔드 서버를 실행할 필요가 없습니다.

```bash
reflex run
```

브라우저에서 자동으로 열리거나, 다음 주소로 접속하세요:
- Reflex 앱: `http://localhost:3000`
- API 문서: `http://localhost:3000/api/docs`

## 5. 문제 해결

### 페이지 이동이 안 될 때

Reflex에서 페이지 이동이 안 되는 가장 흔한 원인 3가지:

#### ❌ 1) 버튼에 `on_click=rx.redirect()` 처리를 안 넣음

Reflex는 React처럼 `<a href>`로 이동하지 않습니다. 반드시 이벤트 핸들러를 사용해야 합니다.

#### ❌ 2) `ecojourney.py`에서 route 등록이 안 되어 있음

페이지를 등록하지 않으면 버튼을 잘 눌러도 페이지 자체가 없어서 이동이 안 됩니다.

#### ❌ 3) 페이지 함수에서 `return`이 컴포넌트가 아닌 경우

페이지 함수는 반드시 단일 컴포넌트를 반환해야 합니다.

자세한 내용은 [`REFLEX_SETUP.md`](./REFLEX_SETUP.md)를 참고하세요.


