# EcoJourney

일상 행동 기반 탄소 배출량을 **계산·시각화**하고, **AI 코칭**으로 저감 방향을 제안하는 Reflex 기반 웹앱입니다.  
단과대 기반 **대항전·랭킹·챌린지**를 통해 환경 보호를 게임처럼 즐길 수 있도록 설계했습니다.

- **문서**: [`docs/QUICKSTART.md`](./docs/QUICKSTART.md) · [`docs/REFLEX_SETUP.md`](./docs/REFLEX_SETUP.md) · [`docs/CALCULATION.md`](./docs/CALCULATION.md)

## 🎯 문제 제기

- 환경 문제의 심각성은 인지하지만, 개인의 행동이 배출량에 미치는 영향은 체감하기 어려움
- 기존 환경 앱은 기록 위주로 구성되어 지속적인 사용 동기 부족
- 친환경 활동 보상이 현실적인 혜택(대학 생활 마일리지 등)으로 연결되지 않음

## 💡 개발 배경

### 대학생 맞춤형 게이미피케이션
소속감(단과대)과 경쟁 심리를 자극하는 '대항전'과 한림BeCome 마일리지 연동을 통해 대학생들이 능동적으로 참여하는 친환경 문화를 조성.

## ✨ 주요 기능

### A. 행동 기반 탄소 관리 및 AI 분석

- **탄소 배출량 계산**: 교통/의류/식품/쓰레기/전기/물 입력값 기반 산정(외부 API 선택 + 로컬 계수 Fallback)
- **카테고리 도움말**: 각 카테고리 페이지의 `?` 버튼으로 입력 방법/산정 기준 모달 제공
- **AI 코칭**: Gemini 기반 분석 요약 + 저감 제안 + 정책/대안 추천
- **리포트**: 카테고리별 기여도/평균 대비 분석 시각화 + 저장(동일 날짜는 최신 리포트로 업데이트) + 포인트 적립
- **마이페이지**: 주/월 배출량 그래프, 포인트 내역, 챌린지 진행도 확인

### B. 단과대 대항전 및 챌린지

- **로그인/사용자 구분**: 닉네임·학번·단과대 기반 그룹화
- **단과대 대항전**: 주간 매칭/포인트 베팅/승자 독식 보상 구조
- **챌린지**: 일일 정보글 · 일일 OX 퀴즈 · 주간 7일 연속 리포트 등

### C. 보상 시스템 

- **마일리지 환산(테스트)**: 포인트 → 학교 마일리지 환산 신청(관리자 승인/차감/완료 안내)

## 🏗️ 프로젝트 구조

```
<project-root>/
├── docs/                      # 프로젝트 문서
│   ├── CALCULATION.md
│   ├── QUICKSTART.md
│   └── REFLEX_SETUP.md
├── ecojourney/                # 앱 패키지(Reflex)
│   ├── ecojourney.py          # 라우팅/앱 등록
│   ├── state.py               # AppState 진입점
│   ├── models.py              # DB 모델(SQLModel)
│   ├── pages/                 # UI 페이지
│   ├── states/                # 상태(State) 로직
│   ├── service/               # 탄소 계산/외부 API/유틸
│   ├── ai/                    # AI 연동
│   ├── api/                   # API 라우터
│   ├── schemas/               # 요청/응답 스키마
│   └── db/                    # DB 초기화/스키마
├── assets/                    # 이미지/정적 리소스
├── alembic/                   # DB 마이그레이션
├── rxconfig.py                # Reflex 설정 파일
├── requirements.txt
├── package.json
└── README.md                  # 프로젝트 문서(루트)
```

## 🚀 빠른 시작

자세한 설치 및 실행 방법은 [`docs/QUICKSTART.md`](./docs/QUICKSTART.md)를 참고하세요. (명령은 프로젝트 루트에서 실행)

### 1. 환경 설정

```bash
# 가상환경 생성 및 활성화
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux

# Python 의존성 설치
pip install -r requirements.txt

# Node.js 의존성 설치 (react-player 등)
npm install
```

### 2. 환경 변수 설정

프로젝트 루트에 `.env` 파일을 생성하고 Google Gemini API 키를 추가하세요:

```
GEMINI_API_KEY=your_gemini_api_key_here

# 탄소 배출량 계산 API (선택사항)
# API 키가 없어도 로컬 배출 계수로 계산됩니다
CLIMATIQ_API_KEY=your_climatiq_api_key_here
```

> **참고**:
> - Gemini API 키는 [Google AI Studio](https://aistudio.google.com/app/apikey)에서 무료로 발급받을 수 있습니다.
> - Climatiq API 키는 [Climatiq](https://www.climatiq.io/)에서 발급받을 수 있습니다.

#### BYOK(Bring Your Own Key) 원칙

- 이 저장소에는 **API 키를 포함하지 않습니다.** (키를 코드에 심어 배포하는 것은 약관 위반/보안 사고로 이어질 수 있습니다)
- Gemini/Climatiq 기능을 사용하려면 **사용자가 직접 발급받은 키**를 `.env`에 넣어 사용하세요.
- API는 오픈소스가 아니라 **서비스**이므로, 사용자는 각 서비스의 **약관/사용 정책/할당량**에 동의하고 사용해야 합니다.
- Climatiq의 무료/커뮤니티 플랜은 약관에 따라 **상업적 사용이 제한될 수 있으니**, 상업적 사용 전 반드시 약관을 확인하세요.

### 3. 데이터베이스 초기화

모델을 정의했으므로 데이터베이스를 초기화하고 마이그레이션을 적용해야 합니다:

```bash
# 1. DB 초기화 (아직 안 했다면)
reflex db init

# 2. 변경 사항(작성한 모델) 감지 및 스크립트 생성
reflex db makemigrations --message "init models"

# 3. 실제 DB에 테이블 생성
reflex db migrate
```

### 4. 서버 실행

Reflex는 프론트엔드와 백엔드를 하나로 통합한 Full-stack 프레임워크입니다.  
별도의 백엔드 서버를 실행할 필요가 없습니다.

```bash
reflex run
```

브라우저에서 `http://localhost:3000`으로 접속하세요.

## 📘 계산 기준 및 상세 문서

탄소 배출량 계산 방식, 배출계수, 단위 변환 규칙, 데이터 출처,  
AI 분석 기준 및 포인트 지급 로직은 별도 문서로 분리하여 관리합니다.

- [`docs/CALCULATION.md`](./docs/CALCULATION.md)

## 📚 문서

- **빠른 시작**: [`docs/QUICKSTART.md`](./docs/QUICKSTART.md)
- **Reflex 설정 가이드**: [`docs/REFLEX_SETUP.md`](./docs/REFLEX_SETUP.md)

## 🙏 Acknowledgments

- AI features are powered by **Google Gemini API**.
- Carbon emission data is provided by **Climatiq API**.

## 📄 라이선스

라이선스는 [`LICENSE`](./LICENSE)를 참고하세요.

오픈소스 의존성/외부 API(약관) 요약은 [`docs/THIRD_PARTY_NOTICES.md`](./docs/THIRD_PARTY_NOTICES.md)를 참고하세요.
