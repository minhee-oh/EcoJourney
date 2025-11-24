# Reflex 앱 실행 가이드

## 개요
이 프로젝트는 Streamlit에서 Reflex로 마이그레이션되었습니다. Reflex는 Python으로 React 기반 웹 애플리케이션을 만들 수 있는 프레임워크입니다.

## 사전 요구사항
- Python 3.8 이상
- 백엔드 서버가 실행 중이어야 함 (http://localhost:8000)

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
cd frontend
pip install -r requirements.txt
```

### 3. Reflex 초기화
```bash
reflex init
```

## 실행

### 개발 모드로 실행
```bash
cd frontend
reflex run
```

앱이 실행되면 기본적으로 `http://localhost:3000`에서 접근할 수 있습니다.

### 프로덕션 빌드
```bash
reflex export
```

## 프로젝트 구조

```
frontend/
├── rxconfig.py                    # Reflex 설정 파일
├── carbon_footprint/
│   ├── __init__.py
│   ├── carbon_footprint.py        # 메인 앱 파일
│   └── components/
│       ├── __init__.py
│       ├── summary.py             # 요약 컴포넌트
│       ├── avatar.py              # 아바타 컴포넌트
│       ├── badges.py              # 배지 컴포넌트
│       └── dashboard.py           # 대시보드 컴포넌트
└── requirements.txt
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

4. **비동기 처리**
   - Streamlit: 동기적 API 호출
   - Reflex: `async/await`를 사용한 비동기 API 호출

## 문제 해결

### 백엔드 연결 오류
백엔드 서버가 실행 중인지 확인하세요:
```bash
cd backend
uvicorn main:app --reload
```

### 포트 충돌
다른 포트를 사용하려면 `rxconfig.py`를 수정하거나 환경 변수를 설정하세요.

### 모듈 import 오류
프로젝트 루트에서 실행하거나 PYTHONPATH를 설정하세요:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/frontend"
```

## 추가 리소스
- [Reflex 공식 문서](https://reflex.dev)
- [Reflex GitHub](https://github.com/reflex-dev/reflex)




