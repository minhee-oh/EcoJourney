# 파일 경로: ecojourney/init_db.py
# 데이터베이스를 처음 만들 때,
# schema.sql에 정의된 테이블 구조를 그대로 DB에 적용하는 초기화용 스크립트 
from pathlib import Path
import sqlite3

# DB 연결 함수와 DB 경로를 공통 모듈에서 가져옴
from . import get_connection, DB_PATH


def init_db() -> None:
    """
    schema.sql 파일을 읽어서 데이터베이스를 초기화하는 함수.

    - 테이블 생성 SQL(schema.sql)을 한 번에 실행
    - DB 초기 세팅용으로 개발자가 직접 실행
    - 에러 발생 시 서버를 종료하지 않고 콘솔에만 출력
    """

    # --------------------------------------------------
    # 1) schema.sql 파일 경로 설정
    #    - init_db.py와 같은 위치에 있는 schema.sql을 찾음
    # --------------------------------------------------
    schema_path = Path(__file__).with_name("schema.sql")

    # schema.sql 파일이 없으면 DB 초기화를 진행할 수 없음
    if not schema_path.exists():
        print(f"[DB INIT ERROR] schema.sql 파일을 찾을 수 없습니다: {schema_path}")
        return

    # --------------------------------------------------
    # 2) schema.sql 파일 읽기
    #    - 테이블 생성 SQL을 문자열로 로드
    # --------------------------------------------------
    try:
        with open(schema_path, encoding="utf-8") as f:
            sql_script = f.read()
    except OSError as e:
        # 파일 권한, 경로 문제 등
        print(f"[DB INIT ERROR] schema.sql 파일을 여는 중 오류: {e}")
        return

    # --------------------------------------------------
    # 3) DB 연결 후 SQL 스크립트 실행
    # --------------------------------------------------
    conn = None
    try:
        # 공통 DB 연결 함수 사용
        conn = get_connection()
        cur = conn.cursor()

        # schema.sql에 있는 모든 SQL을 한 번에 실행
        cur.executescript(sql_script)
        conn.commit()

        print(f"✅ DB 초기화 완료: {DB_PATH}")

    except sqlite3.Error as e:
        # SQL 문법 오류, 테이블 중복 생성 등 SQLite 관련 에러
        print(f"[DB INIT ERROR] SQLite 에러 발생: {e}")

    except Exception as e:
        # 예상하지 못한 기타 에러
        print(f"[DB INIT ERROR] 알 수 없는 에러가 발생했습니다: {e}")

    finally:
        # --------------------------------------------------
        # 4) DB 연결 정리
        #    - 에러 발생 여부와 상관없이 항상 연결 종료
        # --------------------------------------------------
        if conn is not None:
            conn.close()


# --------------------------------------------------
# 직접 실행 시 DB 초기화 수행
# --------------------------------------------------
if __name__ == "__main__":
    init_db()
