# 파일 경로: ecojourney/db/__init__.py
# 이 파일은 DB 연결을 한 곳에서 관리해서
# 코드 중복을 줄이고,
# DB 오류를 API 레벨에서 상황에 맞게 처리할 수 있게 해준다.
from pathlib import Path
import sqlite3

# --------------------------------------------------
# DB 파일 위치 설정
#  - 프로젝트 루트 기준으로 eco_journey.db를 사용
#  - 실행 위치가 달라져도 항상 같은 DB를 가리키게 함
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "eco_journey.db"


def get_connection() -> sqlite3.Connection:
    """
    SQLite DB 연결을 생성해서 반환하는 공통 함수.

    ✔ 모든 DB 접근은 이 함수를 통해서만 이루어짐
    ✔ DB 경로/row_factory 설정을 한 곳에서 통제
    ✔ 연결 실패 시 예외를 숨기지 않고 상위로 전달
      → 라우터 단에서 JSON 에러 응답으로 처리 가능
    """
    try:
        # DB 연결 생성
        conn = sqlite3.connect(DB_PATH)

        # row["column_name"] 형태로 접근 가능하게 설정
        conn.row_factory = sqlite3.Row
        return conn

    except sqlite3.Error as e:
        # DB 파일 손상, 경로 오류, 권한 문제 등
        print(f"[DB ERROR] Failed to connect to database ({DB_PATH}): {e}")
        # 예외를 상위로 넘겨서 API 레벨에서 처리하도록 함
        raise

    except Exception as e:
        # sqlite3 이외의 예상치 못한 예외
        print(f"[DB ERROR] Unknown error during DB connection: {e}")
        raise
