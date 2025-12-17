# Reflex 앱 실행 가이드

## 개요
이 프로젝트는 Streamlit에서 Reflex로 마이그레이션되었습니다. Reflex는 Python으로 React 기반 웹 애플리케이션을 만들 수 있는 Full-stack 프레임워크입니다.

> **중요**: 아래 명령어는 기본적으로 **프로젝트 루트(루트 `README.md`, `rxconfig.py`가 있는 위치)**에서 실행한다고 가정합니다.

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
pip install -r requirements.txt
```

### 3. Reflex 초기화
```bash
reflex init
```

## 실행

### 개발 모드로 실행
```bash
reflex run
```

앱이 실행되면 기본적으로 `http://localhost:3000`에서 접근할 수 있습니다.

### 프로덕션 빌드
```bash
reflex export
```

## 프로젝트 구조

```
<project-root>/
├── rxconfig.py            # Reflex 설정 파일
├── requirements.txt
├── docs/
│   ├── QUICKSTART.md
│   ├── REFLEX_SETUP.md
│   └── CALCULATION.md
└── ecojourney/            # 앱 패키지
    ├── __init__.py
    ├── ecojourney.py      # 메인 앱 파일 (라우팅 정의)
    ├── state.py           # State 관리 (AppState 클래스)
    ├── models.py          # DB 모델(SQLModel)
    ├── pages/             # 페이지 컴포넌트
    ├── states/            # 상태(State) 로직
    ├── service/           # 서비스 로직(탄소 계산 등)
    ├── schemas/           # 요청/응답 스키마
    ├── api/               # API 라우터
    └── ai/                # AI 연동
```

## 주요 개념

### 1. 앱 초기화 및 라우팅

`ecojourney.py`에서 앱을 초기화하고 페이지를 등록합니다.

### 2. 페이지 함수 작성

페이지 함수는 **반드시 단일 컴포넌트를 반환**해야 합니다. `rx.box`, `rx.center` 같은 컨테이너를 사용하세요.

### 3. 페이지 네비게이션 (이벤트 핸들러)

Reflex는 React처럼 `<a href>`로 이동하지 않습니다. **반드시 이벤트 핸들러를 사용**해야 페이지 이동이 됩니다.

### 4. State 관리

State는 `rx.State`를 상속받는 클래스로 정의합니다.

## 문제 해결

### 페이지 이동이 안 될 때 (가장 흔한 원인 3가지)

1. 버튼에 `on_click=rx.redirect()` 처리를 안 넣음  
2. `ecojourney.py`에서 route 등록이 안 되어 있음  
3. 페이지 함수에서 `return`이 컴포넌트가 아닌 경우  

## 추가 리소스
- [Reflex 공식 문서](https://reflex.dev)
- [Reflex GitHub](https://github.com/reflex-dev/reflex)


