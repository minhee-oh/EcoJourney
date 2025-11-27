# Reflex 앱 실행 가이드

## 개요
이 프로젝트는 Streamlit에서 Reflex로 마이그레이션되었습니다. Reflex는 Python으로 React 기반 웹 애플리케이션을 만들 수 있는 Full-stack 프레임워크입니다.

## 사전 요구사항
- Python 3.8 이상
- Reflex 0.8.20 이상

## 설치

### 1. 가상 환경 활성화
```bash
# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

### 2. 의존성 설치
```bash
cd ecojourney
pip install -r requirements.txt
```

### 3. Reflex 초기화
```bash
reflex init
```

## 실행

### 개발 모드로 실행
```bash
cd ecojourney
reflex run
```

앱이 실행되면 기본적으로 `http://localhost:3000`에서 접근할 수 있습니다.

### 프로덕션 빌드
```bash
reflex export
```

## 프로젝트 구조

```
ecojourney/
├── __init__.py
├── ecojourney.py          # 메인 앱 파일 (라우팅 정의)
├── state.py               # State 관리 (AppState 클래스)
├── rxconfig.py            # Reflex 설정 파일 (프로젝트 루트)
├── pages/                 # 페이지 컴포넌트
│   ├── __init__.py
│   ├── home.py           # 홈 페이지
│   ├── intro.py          # 인트로 페이지
│   ├── transportation.py # 교통 입력 페이지
│   ├── food.py           # 식품 입력 페이지
│   ├── clothing.py       # 의류 입력 페이지
│   ├── electricity.py    # 전기 입력 페이지
│   ├── water.py          # 물 입력 페이지
│   ├── waste.py          # 쓰레기 입력 페이지
│   └── report.py         # 리포트 페이지
└── service/              # 서비스 로직
    ├── __init__.py
    ├── carbon_calculator.py  # 탄소 계산 로직
    ├── ai_coach.py           # AI 코칭 로직
    ├── average_data.py       # 평균 데이터
    └── models.py             # 데이터 모델
```

## 주요 개념

### 1. 앱 초기화 및 라우팅

`ecojourney.py`에서 앱을 초기화하고 페이지를 등록합니다:

```python
import reflex as rx
from ecojourney.state import AppState
from ecojourney.pages.home import home_page
from ecojourney.pages.intro import intro_page

# AppState를 사용하여 앱을 초기화
app = rx.App(_state=AppState)

# 페이지 등록
app.add_page(home_page, route="/", title="EcoJourney | 시작")
app.add_page(intro_page, route="/intro", title="EcoJourney | 소개")
```

### 2. 페이지 함수 작성

페이지 함수는 **반드시 단일 컴포넌트를 반환**해야 합니다:

```python
# ✅ 올바른 예시
def home_page():
    return rx.box(
        rx.heading("홈 페이지"),
        rx.button("시작하기", on_click=rx.redirect("/intro"))
    )

# ❌ 잘못된 예시 (rx.fragment 사용 시 페이지 이동이 안 될 수 있음)
def home_page():
    return rx.fragment(
        rx.heading("홈 페이지"),
        rx.button("시작하기")
    )
```

**중요**: `rx.fragment`는 여러 컴포넌트를 그룹화하지만 실제 DOM 요소를 생성하지 않아, 페이지 이동 시 문제가 발생할 수 있습니다. 대신 `rx.box`, `rx.container`, `rx.center` 등의 단일 컨테이너 컴포넌트를 사용하세요.

### 3. 페이지 네비게이션 (이벤트 핸들러)

Reflex는 React처럼 `<a href>`로 이동하지 않습니다. **반드시 이벤트 핸들러를 사용**해야 페이지 이동이 됩니다:

```python
# ✅ 올바른 방법 1 (권장)
rx.button(
    "시작하기",
    on_click=rx.redirect("/intro")
)

# ✅ 올바른 방법 2
rx.button(
    "시작하기",
    on_click=lambda: rx.redirect("/intro")
)

# ❌ 잘못된 방법 1 (이동 안 됨)
rx.button("시작하기", href="/intro")

# ❌ 잘못된 방법 2 (이동 안 됨)
rx.button("시작하기")
```

### 4. State 관리

State는 `rx.State`를 상속받는 클래스로 정의합니다:

```python
import reflex as rx

class AppState(rx.State):
    # State 변수
    error_message: str = ""
    is_loading: bool = False
    
    # 이벤트 핸들러
    def go_to_intro(self):
        return rx.redirect("/intro")
```

페이지에서 State를 사용하려면 State 변수를 참조해야 합니다:

```python
def home_page():
    return rx.box(
        # State 변수 참조 (이벤트 핸들러 작동을 위해 필요)
        rx.cond(
            AppState.error_message != "",
            rx.text(AppState.error_message, color="red")
        ),
        rx.button(
            "시작하기",
            on_click=AppState.go_to_intro  # State 메서드 사용
        )
    )
```

## 주요 변경사항

### Streamlit vs Reflex

1. **상태 관리**
   - Streamlit: `st.session_state`
   - Reflex: `rx.State` 클래스

2. **UI 컴포넌트**
   - Streamlit: `st.button()`, `st.selectbox()` 등
   - Reflex: `rx.button()`, `rx.select()` 등

3. **이벤트 핸들러**
   - Streamlit: 폼 제출 시 자동 처리
   - Reflex: `on_click`, `on_change` 등의 이벤트 핸들러

4. **페이지 네비게이션**
   - Streamlit: 자동 라우팅
   - Reflex: `rx.redirect()`를 사용한 명시적 리다이렉트

5. **비동기 처리**
   - Streamlit: 동기적 API 호출
   - Reflex: `async/await`를 사용한 비동기 API 호출

## 문제 해결

### 페이지 이동이 안 될 때 (가장 흔한 원인 3가지)

#### ❌ 1) 버튼에 `on_click=rx.redirect()` 처리를 안 넣음

Reflex는 React처럼 `<a href>`로 이동하지 않습니다. 반드시 이벤트 핸들러를 사용해야 페이지 이동이 됩니다.

**해결법**:
```python
# ✅ 정답
rx.button(
    "시작하기",
    on_click=rx.redirect("/intro")
)
```

#### ❌ 2) `app.py`에서 route 등록이 안 되어 있음

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

### 백엔드 연결 오류

이 프로젝트는 Reflex Full-stack 프레임워크를 사용하므로 별도의 백엔드 서버가 필요하지 않습니다. 모든 로직은 `service/` 폴더의 서비스 함수로 처리됩니다.

### 포트 충돌

다른 포트를 사용하려면 `rxconfig.py`를 수정하거나 환경 변수를 설정하세요.

### 모듈 import 오류

프로젝트 루트에서 실행하거나 PYTHONPATH를 설정하세요:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### 이벤트 핸들러가 호출되지 않을 때

1. State 변수를 페이지에서 참조했는지 확인
2. `rx.App(_state=AppState)`로 앱을 초기화했는지 확인
3. 페이지 함수가 단일 컴포넌트를 반환하는지 확인

## 디버깅 팁

### 버튼 클릭 이벤트 확인

State 메서드에 로그를 추가하여 이벤트가 호출되는지 확인:

```python
def go_to_intro(self):
    print("🖱️ 버튼 클릭 이벤트 호출됨!", flush=True)
    return rx.redirect("/intro")
```

터미널에 로그가 출력되지 않으면 이벤트 핸들러가 호출되지 않는 것입니다.

## 추가 리소스
- [Reflex 공식 문서](https://reflex.dev)
- [Reflex GitHub](https://github.com/reflex-dev/reflex)
