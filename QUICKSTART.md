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
# 의존성 설치
pip install -r ecojourney/requirements.txt
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

### Reflex 앱 실행 (프론트엔드 + 백엔드 통합)

Reflex는 프론트엔드와 백엔드를 하나로 통합한 Full-stack 프레임워크입니다.
별도의 백엔드 서버를 실행할 필요가 없습니다.

```bash
cd ecojourney
reflex run
```

브라우저에서 자동으로 열리거나, 다음 주소로 접속하세요:
- Reflex 앱: http://localhost:3000
- API 문서: http://localhost:3000/api/docs (FastAPI 라우터가 통합됨)

> **참고**: Reflex는 자체 백엔드를 포트 3000에서 실행하며, WebSocket도 같은 포트를 사용합니다.
> 모든 API는 `/api` 경로로 접근 가능합니다.

## 4. 사용 방법

1. **홈 화면**: 앱 시작 시 홈 화면이 표시됩니다
   - "탄소 발자국 측정 시작하기" 버튼을 클릭하여 인트로 페이지로 이동

2. **인트로 페이지**: 서비스 소개를 확인한 후 카테고리 입력을 시작하세요

3. **카테고리 입력**: 각 카테고리별로 활동을 입력하세요
   - 교통: 자동차, 버스, 지하철 등
   - 식품: 소고기, 돼지고기, 채소 등
   - 의류: 티셔츠, 청바지, 신발 등
   - 전기: 냉방기, 난방기 사용 시간
   - 물: 샤워, 설거지, 세탁 횟수
   - 쓰레기: 일반, 플라스틱, 종이 등

4. **결과 리포트**: 모든 입력을 완료하면 리포트 페이지에서 결과를 확인할 수 있습니다
   - 총 탄소 배출량
   - 카테고리별 배출량
   - AI 기반 맞춤형 코칭 제안

## 5. 문제 해결

### 페이지 이동이 안 될 때

Reflex에서 페이지 이동이 안 되는 가장 흔한 원인 3가지:

#### ❌ 1) 버튼에 `on_click=rx.redirect()` 처리를 안 넣음

Reflex는 React처럼 `<a href>`로 이동하지 않습니다. 반드시 이벤트 핸들러를 사용해야 합니다.

**해결법**:
```python
# ✅ 정답
rx.button(
    "시작하기",
    on_click=rx.redirect("/intro")
)
```

#### ❌ 2) `ecojourney.py`에서 route 등록이 안 되어 있음

페이지를 등록하지 않으면 버튼을 잘 눌러도 페이지 자체가 없어서 이동이 안 됩니다.

**해결법**:
```python
app = rx.App(_state=AppState)
app.add_page(home_page, route="/")
app.add_page(intro_page, route="/intro")  # 이게 없으면 이동 안 됨
```

#### ❌ 3) 페이지 함수에서 `return`이 컴포넌트가 아닌 경우

페이지 함수는 반드시 단일 컴포넌트를 반환해야 합니다.

**해결법**:
```python
# ✅ 올바른 예시
def intro():
    return rx.text("인트로 페이지")  # 단일 컴포넌트 반환

# ❌ 잘못된 예시
def intro():
    return rx.fragment(...)  # rx.fragment는 문제 발생 가능
```

자세한 내용은 [REFLEX_SETUP.md](./ecojourney/REFLEX_SETUP.md)를 참고하세요.

### Gemini API 오류
- `.env` 파일에 API 키가 올바르게 설정되었는지 확인하세요
- API 키가 유효한지 확인하세요
- API 키가 없어도 기본 기능은 사용할 수 있지만, AI 코칭 기능은 제한됩니다

### Import 오류
- 가상환경이 활성화되어 있는지 확인하세요
- `pip install -r ecojourney/requirements.txt`를 다시 실행하세요
- 프로젝트 루트에서 실행하고 있는지 확인하세요

### 이벤트 핸들러가 호출되지 않을 때
- State 변수를 페이지에서 참조했는지 확인하세요
- `rx.App(_state=AppState)`로 앱을 초기화했는지 확인하세요
- 페이지 함수가 단일 컴포넌트를 반환하는지 확인하세요

### Reflex 앱 실행 오류
- `reflex init`을 실행했는지 확인하세요
- Reflex 버전이 0.8.20 이상인지 확인하세요: `pip install reflex --upgrade`

