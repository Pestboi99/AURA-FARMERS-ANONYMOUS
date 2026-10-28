"""
AURA FARMERS ANONYMOUS — Database Module
"Log in. Lose your dignity."

SQLite storage layer with WAL mode enabled.
Handles user profiles, aura calculations, challenge attempts,
achievements, and the emotional support compliment streak.
"""

import sqlite3
import os
from typing import Optional, List, Dict, Any, Union
from werkzeug.security import generate_password_hash

DB_PATH: str = "aura_farmers.db"


class EmbarrassingAnswer(str):
    """
    A string subclass representing the most embarrassing failed answer.
    Behaves as a regular string in formatting and displays, but also supports
    dictionary and attribute lookups for detailed attempt information.
    """

    def __new__(cls, answer_text: str, attempt_dict: Optional[Dict[str, Any]] = None):
        instance = super().__new__(cls, answer_text or "")
        instance._data = attempt_dict or {}
        for k, v in instance._data.items():
            setattr(instance, k, v)
        return instance

    def __getitem__(self, key: Union[str, int, slice]):
        if isinstance(key, str):
            if key == "user_answer":
                return str(self)
            if key in self._data:
                return self._data[key]
        return super().__getitem__(key)

    def get(self, key: str, default: Any = None) -> Any:
        if key == "user_answer":
            return str(self)
        return self._data.get(key, default)


class AchievementItem(dict):
    """
    Dictionary representing an achievement, formatted cleanly when
    converted to string or printed in templates.
    """

    def __str__(self) -> str:
        return self.get("achievement_name", "")


def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """
    Open and return a new SQLite database connection configured with
    sqlite3.Row factory and foreign keys enabled.
    """
    target = db_path if db_path is not None else DB_PATH
    conn = sqlite3.connect(target)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def calculate_rank(aura_points: int) -> str:
    """
    Return the satirical rank title corresponding to the given aura points.

    Rank brackets:
      <0:      'Ohio Resident'
      0-49:    'NPC'
      50-99:   'Side Character'
      100-199: 'Main Character Energy'
      200-299: 'Sigma Grindset'
      300-399: 'Aura Farmer'
      400+:    'Ohio Final Boss'
    """
    if aura_points < 0:
        return "Ohio Resident"
    elif aura_points <= 49:
        return "NPC"
    elif aura_points <= 99:
        return "Side Character"
    elif aura_points <= 199:
        return "Main Character Energy"
    elif aura_points <= 299:
        return "Sigma Grindset"
    elif aura_points <= 399:
        return "Aura Farmer"
    else:
        return "Ohio Final Boss"


def init_db(db_path: Optional[str] = None) -> None:
    """
    Create database tables if they do not already exist and enable WAL mode.
    """
    conn = get_connection(db_path)
    try:
        with conn:
            # Enable WAL mode for high concurrency
            conn.execute("PRAGMA journal_mode=WAL;")

            # 1. users table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    aura_points INTEGER DEFAULT 100,
                    rank_title TEXT DEFAULT 'NPC',
                    bouncer_mood TEXT DEFAULT 'chill',
                    login_attempts INTEGER DEFAULT 0,
                    failed_attempts INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

            # 2. attempts table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS attempts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    challenge_type TEXT,
                    user_answer TEXT,
                    ai_response TEXT,
                    passed BOOLEAN,
                    aura_change INTEGER,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                );
                """
            )

            # 3. achievements table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS achievements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    achievement_name TEXT NOT NULL,
                    achieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                    UNIQUE (user_id, achievement_name)
                );
                """
            )

            # 4. compliments table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS compliments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    compliment TEXT,
                    accepted BOOLEAN,
                    ai_response TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                );
                """
            )
    finally:
        conn.close()


def create_user(
    username: str,
    password_hash: str,
    aura_points: int = 100,
    rank_title: Optional[str] = None,
    bouncer_mood: str = "chill",
    login_attempts: int = 0,
    failed_attempts: int = 0,
) -> Optional[Dict[str, Any]]:
    """
    Insert a new user into the database and return the user dictionary.
    Returns None if the username already exists.
    """
    if rank_title is None:
        rank_title = "NPC" if aura_points == 100 else calculate_rank(aura_points)

    conn = get_connection()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO users (
                    username, password_hash, aura_points,
                    rank_title, bouncer_mood, login_attempts, failed_attempts
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    username,
                    password_hash,
                    aura_points,
                    rank_title,
                    bouncer_mood,
                    login_attempts,
                    failed_attempts,
                ),
            )
            user_id = cursor.lastrowid
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()


def get_user(username: str) -> Optional[Dict[str, Any]]:
    """
    Fetch a user record by username.
    Returns user dict or None if not found.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """
    Fetch a user record by user ID.
    Returns user dict or None if not found.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def update_aura(user_id: int, change: int) -> Optional[Dict[str, Any]]:
    """
    Add or subtract aura points for a user and update their rank_title
    based on the satirical rank thresholds. Returns the updated user dict.
    """
    conn = get_connection()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT aura_points FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            if not row:
                return None

            new_aura = row["aura_points"] + change
            new_rank = calculate_rank(new_aura)

            cursor.execute(
                """
                UPDATE users
                SET aura_points = ?, rank_title = ?
                WHERE id = ?
                """,
                (new_aura, new_rank, user_id),
            )
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            updated_row = cursor.fetchone()
            return dict(updated_row) if updated_row else None
    finally:
        conn.close()


def update_mood(user_id: int, mood: str) -> Optional[Dict[str, Any]]:
    """
    Update the bouncer_mood for a user.
    Returns updated user dict or None if not found.
    """
    conn = get_connection()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET bouncer_mood = ? WHERE id = ?",
                (mood, user_id),
            )
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    finally:
        conn.close()


def record_attempt(
    user_id: int,
    challenge_type: str,
    user_answer: str,
    ai_response: str,
    passed: bool,
    aura_change: int,
) -> int:
    """
    Insert a challenge attempt record for a user.
    Returns the newly created attempt ID.
    """
    conn = get_connection()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO attempts (
                    user_id, challenge_type, user_answer,
                    ai_response, passed, aura_change
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    challenge_type,
                    user_answer,
                    ai_response,
                    1 if passed else 0,
                    aura_change,
                ),
            )
            return cursor.lastrowid
    finally:
        conn.close()


def get_user_attempts(user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Fetch the most recent attempts for a user, ordered by newest first.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM attempts
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (user_id, limit),
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_worst_answer(user_id: int) -> Optional[EmbarrassingAnswer]:
    """
    Return the most embarrassing failed answer (the longest user_answer
    where passed is False). Returns an EmbarrassingAnswer string instance,
    or None if the user has no failed answers.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM attempts
            WHERE user_id = ?
              AND (passed = 0 OR passed IS FALSE)
              AND user_answer IS NOT NULL
              AND user_answer != ''
            ORDER BY LENGTH(user_answer) DESC, id DESC
            LIMIT 1
            """,
            (user_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return EmbarrassingAnswer(row["user_answer"], dict(row))
    finally:
        conn.close()


def increment_login_attempts(user_id: int) -> Optional[Dict[str, Any]]:
    """
    Increment the login_attempts counter for a user.
    Returns updated user dict or None if not found.
    """
    conn = get_connection()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE users
                SET login_attempts = login_attempts + 1
                WHERE id = ?
                """,
                (user_id,),
            )
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    finally:
        conn.close()


def increment_failed_attempts(user_id: int) -> Optional[Dict[str, Any]]:
    """
    Increment the failed_attempts counter for a user.
    Returns updated user dict or None if not found.
    """
    conn = get_connection()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE users
                SET failed_attempts = failed_attempts + 1
                WHERE id = ?
                """,
                (user_id,),
            )
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    finally:
        conn.close()


def get_leaderboard_shame(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Return top users ranked by highest number of failed_attempts (Hall of Shame).
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM users
            ORDER BY failed_attempts DESC, id ASC
            LIMIT ?
            """,
            (limit,),
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_leaderboard_aura(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Return top users ranked by highest aura_points.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM users
            ORDER BY aura_points DESC, id ASC
            LIMIT ?
            """,
            (limit,),
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def add_achievement(user_id: int, name: str) -> bool:
    """
    Add an achievement for a user if it does not already exist.
    Returns True if newly added, False if it was already earned or failed.
    """
    conn = get_connection()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR IGNORE INTO achievements (user_id, achievement_name)
                VALUES (?, ?)
                """,
                (user_id, name),
            )
            return cursor.rowcount > 0
    finally:
        conn.close()


def get_achievements(user_id: int) -> List[AchievementItem]:
    """
    Return list of achievements earned by the given user.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM achievements
            WHERE user_id = ?
            ORDER BY id ASC
            """,
            (user_id,),
        )
        return [AchievementItem(dict(row)) for row in cursor.fetchall()]
    finally:
        conn.close()


def record_compliment(
    user_id: int, compliment: str, accepted: bool, ai_response: str
) -> int:
    """
    Insert a compliment entry for password reset tracking.
    Returns the new compliment record ID.
    """
    conn = get_connection()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO compliments (user_id, compliment, accepted, ai_response)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, compliment, 1 if accepted else 0, ai_response),
            )
            return cursor.lastrowid
    finally:
        conn.close()


def get_accepted_compliments_count(user_id: int) -> int:
    """
    Return the total number of accepted compliments for a given user.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT COUNT(*) AS count FROM compliments
            WHERE user_id = ? AND (accepted = 1 OR accepted IS TRUE)
            """,
            (user_id,),
        )
        row = cursor.fetchone()
        return row["count"] if row else 0
    finally:
        conn.close()


def seed_demo_data() -> None:
    """
    Seed initial demo user and 5 fake leaderboard users with varied stats,
    funny failed attempts, achievements, and compliments.
    Idempotent: skips users if their username already exists.
    """
    init_db()

    # 1. Demo User
    demo_username = "demo"
    demo_password_plain = "🍎Sigma7prime!"
    if not get_user(demo_username):
        demo_hash = generate_password_hash(demo_password_plain)
        demo_user = create_user(
            username=demo_username,
            password_hash=demo_hash,
            aura_points=150,
            rank_title="Main Character Energy",
            bouncer_mood="chill",
            login_attempts=3,
            failed_attempts=1,
        )
        if demo_user:
            d_id = demo_user["id"]
            record_attempt(
                d_id,
                "spot_the_meme",
                "Loss (| || || |_)",
                "Classic meme recognized. You may pass.",
                True,
                15,
            )
            record_attempt(
                d_id,
                "meme_explainer",
                "I told the bouncer my aura was too heavy to measure on a standard scale",
                "The bouncer weighed your aura. It was 0 grams. Sad.",
                False,
                -10,
            )
            add_achievement(d_id, "First Timer: Survived your first trial")
            record_compliment(
                d_id,
                "Your jawline could cut glass, Mr. Bouncer sir.",
                True,
                "The Bouncer adjusts his sunglasses and nods solemnly.",
            )

    # 2. Fake Users with varied aura (-50 to 350) and failed attempts (2 to 47)
    fake_users_data = [
        {
            "username": "xX_SigmaGrinder_Xx",
            "password": "FakePassword1!",
            "aura_points": 350,
            "rank_title": "Aura Farmer",
            "bouncer_mood": "chill",
            "login_attempts": 15,
            "failed_attempts": 2,
            "achievements": [
                "Sigma Grindset: Achieved 200+ Aura",
                "Flawless: Passed all challenges perfectly",
            ],
            "attempts": [
                {
                    "type": "sigma_timer",
                    "answer": "I am the sigma who mews at the skibidi toilet in Ohio at 3am",
                    "ai_response": "Sigma speed detected. Your fingers have rizz. Proceed.",
                    "passed": True,
                    "aura_change": 15,
                },
                {
                    "type": "meme_explainer",
                    "answer": "I wake up at 2:59 AM so I can out-sigma the people who wake up at 3:00 AM",
                    "ai_response": "Sleep deprivation is not an aura multiplier, king.",
                    "passed": False,
                    "aura_change": -5,
                },
            ],
        },
        {
            "username": "TungTungEnjoyer",
            "password": "FakePassword2!",
            "aura_points": 240,
            "rank_title": "Sigma Grindset",
            "bouncer_mood": "grumpy",
            "login_attempts": 22,
            "failed_attempts": 14,
            "achievements": [
                "Sigma Grindset: Achieved 200+ Aura",
                "Clutch Gene: Passed with no time left",
            ],
            "attempts": [
                {
                    "type": "meme_explainer",
                    "answer": "tung tung tung sahur is actually an ancient indonesian percussion ritual representing spiritual enlightenment and sigma awakening",
                    "ai_response": "It is a wooden log bonking things. Stop overthinking the brainrot.",
                    "passed": False,
                    "aura_change": -10,
                },
                {
                    "type": "spot_the_meme",
                    "answer": "Steamed Hams",
                    "ai_response": "Lucky guess. The Bouncer remains suspicious.",
                    "passed": True,
                    "aura_change": 10,
                },
            ],
        },
        {
            "username": "SkibidiSurvivor",
            "password": "FakePassword3!",
            "aura_points": 75,
            "rank_title": "Side Character",
            "bouncer_mood": "sleepy",
            "login_attempts": 34,
            "failed_attempts": 23,
            "achievements": [
                "Certified NPC: Failed 3 times",
            ],
            "attempts": [
                {
                    "type": "meme_explainer",
                    "answer": "The skibidi toilet cinematic universe has deeper lore than the entire Lord of the Rings trilogy and I wrote an 8000 word dissertation to prove it",
                    "ai_response": "Touching grass is no longer enough. You need to consume an entire lawn.",
                    "passed": False,
                    "aura_change": -20,
                },
                {
                    "type": "vibe_check",
                    "answer": "Skibidium (atomic number 69)",
                    "ai_response": "Aura certified for the moment.",
                    "passed": True,
                    "aura_change": 10,
                },
            ],
        },
        {
            "username": "MewingMaxxer",
            "password": "FakePassword4!",
            "aura_points": 25,
            "rank_title": "NPC",
            "bouncer_mood": "unhinged",
            "login_attempts": 45,
            "failed_attempts": 38,
            "achievements": [
                "Certified NPC: Failed 3 times",
                "Down Bad: Failed 10 times",
            ],
            "attempts": [
                {
                    "type": "meme_explainer",
                    "answer": "If I hold my jawline at precisely a 47.3 degree angle while reciting the Patrick Bateman morning routine, my aura automatically multiplies by 10x",
                    "ai_response": "Your jawline is giving trapezoid. Immediate disqualification.",
                    "passed": False,
                    "aura_change": -15,
                },
                {
                    "type": "slider_of_doom",
                    "answer": "42",
                    "ai_response": "You missed by 8. Bestie, buy a mousepad.",
                    "passed": False,
                    "aura_change": -10,
                },
            ],
        },
        {
            "username": "RizzlessInOhio",
            "password": "FakePassword5!",
            "aura_points": -50,
            "rank_title": "Ohio Resident",
            "bouncer_mood": "grumpy",
            "login_attempts": 58,
            "failed_attempts": 47,
            "achievements": [
                "Certified NPC: Failed 3 times",
                "Down Bad: Failed 10 times",
            ],
            "attempts": [
                {
                    "type": "meme_explainer",
                    "answer": "i thought ohio was a myth created by kai cenat",
                    "ai_response": "Ohio is very real and you are currently in its deepest trench.",
                    "passed": False,
                    "aura_change": -15,
                },
                {
                    "type": "vibe_check",
                    "answer": "I tried to rizz up the bouncer by barking and doing the griddy towards the door",
                    "ai_response": "Security has been notified. This is not rizz, this is a wellness check.",
                    "passed": False,
                    "aura_change": -20,
                },
                {
                    "type": "meme_explainer",
                    "answer": "I spent 45 minutes practicing my mewing technique in the bathroom mirror while whispering skibidi toilet lyrics hoping the AI bouncer would recognize my unspoken rizz and grant me VIP access to the sigma sanctuary",
                    "ai_response": "The Bouncer watched through the security camera in absolute horror. Your rizz is strictly negative. Sentenced to 100 years in Ohio.",
                    "passed": False,
                    "aura_change": -25,
                },
            ],
        },
    ]

    for user_info in fake_users_data:
        if get_user(user_info["username"]):
            continue

        p_hash = generate_password_hash(user_info["password"])
        user = create_user(
            username=user_info["username"],
            password_hash=p_hash,
            aura_points=user_info["aura_points"],
            rank_title=user_info["rank_title"],
            bouncer_mood=user_info["bouncer_mood"],
            login_attempts=user_info["login_attempts"],
            failed_attempts=user_info["failed_attempts"],
        )

        if not user:
            continue

        u_id = user["id"]

        for att in user_info.get("attempts", []):
            record_attempt(
                user_id=u_id,
                challenge_type=att["type"],
                user_answer=att["answer"],
                ai_response=att["ai_response"],
                passed=att["passed"],
                aura_change=att["aura_change"],
            )

        for ach in user_info.get("achievements", []):
            add_achievement(u_id, ach)


if __name__ == "__main__":
    init_db()
    seed_demo_data()
    print("Database initialized and demo data seeded successfully.")
