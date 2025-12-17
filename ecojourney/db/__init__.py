from pathlib import Path
import sqlite3
import os

# 프로젝트 루트 경로 (Reflex 프로젝트 루트)
# ecojourney/db/__init__.py 위치에서 두 단계 위로 이동하면 프로젝트 루트
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Reflex가 사용하는 DB 파일과 동일한 경로 사용
DB_PATH = BASE_DIR / "reflex.db"


def get_connection():
    """SQLite 연결을 만들어서 반환 (Reflex DB와 동일한 파일 사용)"""
    conn = sqlite3.connect(str(DB_PATH))
    # row["student_id"] 이런 식으로 쓰려고
    conn.row_factory = sqlite3.Row
    return conn
