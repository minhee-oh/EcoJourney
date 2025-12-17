from pathlib import Path
from . import get_connection, DB_PATH


def init_db():
    # 같은 폴더에 있는 schema.sql 경로
    schema_path = Path(__file__).with_name("schema.sql")

    with open(schema_path, encoding="utf-8") as f:
        sql_script = f.read()

    conn = get_connection()
    cur = conn.cursor()
    cur.executescript(sql_script)
    conn.commit()
    conn.close()

    print(f"✅ DB 초기화 완료: {DB_PATH}")


if __name__ == "__main__":
    init_db()
