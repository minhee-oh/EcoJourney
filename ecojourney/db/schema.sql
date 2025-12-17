-- SQLModel User 모델과 일치하도록 컬럼명/테이블명을 맞춘다.
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,        -- 내부 PK (SQLModel 기본)
    student_id TEXT UNIQUE NOT NULL,             -- 학번 (로그인 ID)
    password TEXT NOT NULL,                      -- 비밀번호 해시(SHA256)
    nickname TEXT UNIQUE NOT NULL,               -- 사용자 닉네임 (표시용)
    college TEXT NOT NULL,                       -- 소속 단과대 (예: 'Engineering')
    current_points INTEGER NOT NULL DEFAULT 0,   -- 현재 보유 포인트 (기본값: 0)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP -- 가입일
);

-- CarbonLog 테이블 (탄소 배출 기록 및 AI 분석)
CREATE TABLE IF NOT EXISTS carbonlog (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    log_date DATE DEFAULT (DATE('now')),
    source TEXT DEFAULT 'carbon_input',
    transport_km REAL DEFAULT 0.0,
    cup_count INTEGER DEFAULT 0,
    ac_hours REAL DEFAULT 0.0,
    activities_json TEXT DEFAULT '[]',
    total_emission REAL DEFAULT 0.0,
    points_earned INTEGER DEFAULT 0,
    ai_feedback TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Battle 테이블 (단과대 대항전)
CREATE TABLE IF NOT EXISTS battle (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    college_a TEXT NOT NULL,
    college_b TEXT NOT NULL,
    score_a INTEGER DEFAULT 0,
    score_b INTEGER DEFAULT 0,
    winner TEXT,
    status TEXT DEFAULT 'ACTIVE',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- BattleParticipant 테이블 (대항전 참가/베팅 내역)
CREATE TABLE IF NOT EXISTS battleparticipant (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    battle_id INTEGER NOT NULL,
    student_id TEXT NOT NULL,
    bet_amount INTEGER DEFAULT 0,
    reward_amount INTEGER DEFAULT 0,
    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- MileageRequest 테이블 (포인트→마일리지 환산 신청)
CREATE TABLE IF NOT EXISTS mileagerequest (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    request_points INTEGER NOT NULL,
    converted_mileage INTEGER NOT NULL,
    status TEXT DEFAULT 'APPROVED',
    processed_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Challenge 테이블 (챌린지 마스터)
CREATE TABLE IF NOT EXISTS challenge (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    type TEXT NOT NULL,
    goal_value INTEGER NOT NULL,
    reward_points INTEGER DEFAULT 500,
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ChallengeProgress 테이블 (챌린지 진행도)
CREATE TABLE IF NOT EXISTS challengeprogress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    challenge_id INTEGER NOT NULL,
    student_id TEXT NOT NULL,
    current_value INTEGER DEFAULT 0,
    is_completed BOOLEAN DEFAULT 0,
    completed_at DATETIME,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- PointsLog 테이블 (포인트 획득 로그)
CREATE TABLE IF NOT EXISTS pointslog (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    log_date DATE DEFAULT (DATE('now')),
    points INTEGER DEFAULT 0,
    source TEXT NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
