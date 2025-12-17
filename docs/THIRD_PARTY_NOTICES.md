## Third-Party Notices (주요 의존성/서비스 라이선스 요약)

본 문서는 EcoJourney에서 사용하는 주요 오픈소스 라이브러리와 외부 API 서비스(약관)를 요약합니다.  


### 1. 오픈소스 라이브러리(코드)

| 구성요소 | 버전 | 라이선스 | 비고 |
|---|---:|---|---|
| Reflex (`reflex`) | 0.8.21 | Apache-2.0 | UI/서버(Reflex) 프레임워크 |
| FastAPI (`fastapi`) | 0.122.0 | MIT | API 라우팅/서버 구성(Reflex 내부에서 활용) |
| SQLAlchemy (`SQLAlchemy`) | 2.0.44 | MIT | ORM/DB 레이어 |
| SQLModel (`sqlmodel`) | 0.0.27 | MIT | SQLModel(내부적으로 SQLAlchemy/Pydantic 사용) |
| Pydantic (`pydantic`) | 2.12.5 | MIT | 데이터 검증/스키마 |
| Requests (`requests`) | 2.32.3 | Apache-2.0 | HTTP 클라이언트 |
| python-dotenv (`python-dotenv`) | 1.2.1 | BSD-3-Clause | `.env` 로딩 |
| Google Generative AI SDK (`google-generativeai`) | 0.8.5 | Apache-2.0 | Gemini 연동용 파이썬 SDK(라이브러리) |

### 2. 런타임/언어

- **Python**: 3.13.9 / PSF(Python Software Foundation) License (SPDX: `Python-2.0`)  
  - 참고: `https://docs.python.org/3/license.html`

재현 방법(로컬 확인):

```bash
python -m pip show reflex sqlmodel fastapi SQLAlchemy pydantic requests python-dotenv google-generativeai
```

### 3. 외부 API 서비스(오픈소스 아님)

아래는 “라이브러리”가 아니라 **서비스/API**이므로 오픈소스 라이선스가 아니라 **서비스 약관/사용정책**이 적용됩니다.

- **Google Gemini API**
  - **구분**: 상용/서비스형 API 
  - **적용**: Google의 API 약관/사용 정책, 할당량/요금/제한(Free tier 포함) 등
  - **주의**: API Key는 비밀정보이며 저장소에 커밋하면 안 됩니다.
  - **참고**: [Google AI for Developers](https://ai.google.dev/)

- **Climatiq API**
  - **구분**: 상용/서비스형 API 
  - **적용**: Climatiq의 이용약관/요금/할당량/데이터 사용 조건
  - **주의**: API Key는 비밀정보이며 저장소에 커밋하면 안 됩니다.
  - **주의(상업적 사용)**: Climatiq 플랜/약관에 따라 상업적 사용이 제한될 수 있습니다. 상업적 사용 전 약관을 확인하세요.
  - **참고**: [Climatiq](https://www.climatiq.io/)


