"""SQLite-backed personal knowledge base."""

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, Iterator, List, Optional

import config


class KnowledgeBase:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or str(config.DB_PATH)
        self._init_db()

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS favorites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    repo_id INTEGER UNIQUE,
                    full_name TEXT NOT NULL,
                    description TEXT,
                    html_url TEXT,
                    stargazers_count INTEGER DEFAULT 0,
                    forks_count INTEGER DEFAULT 0,
                    language TEXT,
                    topics TEXT,
                    analysis_data TEXT,
                    notes TEXT,
                    added_at TEXT NOT NULL,
                    last_viewed TEXT,
                    view_count INTEGER DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS qa_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    repo_full_name TEXT NOT NULL,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS learning_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    repo_full_name TEXT NOT NULL,
                    action TEXT NOT NULL,
                    details TEXT,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    repo_full_name TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                """
            )

    def add_favorite(self, repo: Dict[str, Any], analysis_report: str = "") -> None:
        now = datetime.now().isoformat(timespec="seconds")
        with self._connect() as conn:
            existing = conn.execute(
                "SELECT 1 FROM favorites WHERE full_name = ?",
                (repo.get("full_name"),),
            ).fetchone()
            values = (
                repo.get("id"),
                repo.get("full_name"),
                repo.get("description"),
                repo.get("html_url"),
                repo.get("stargazers_count", repo.get("stars", 0)),
                repo.get("forks_count", repo.get("forks", 0)),
                repo.get("language"),
                json.dumps(repo.get("topics", []), ensure_ascii=False),
                analysis_report,
                now,
            )
            if existing:
                conn.execute(
                    """
                    UPDATE favorites
                    SET repo_id = ?, description = ?, html_url = ?,
                        stargazers_count = ?, forks_count = ?, language = ?,
                        topics = ?,
                        analysis_data = COALESCE(NULLIF(?, ''), analysis_data)
                    WHERE full_name = ?
                    """,
                    (
                        values[0],
                        values[2],
                        values[3],
                        values[4],
                        values[5],
                        values[6],
                        values[7],
                        values[8],
                        values[1],
                    ),
                )
            else:
                conn.execute(
                    """
                    INSERT INTO favorites
                    (repo_id, full_name, description, html_url, stargazers_count,
                     forks_count, language, topics, analysis_data, added_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    values,
                )

    def remove_favorite(self, full_name: str) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM favorites WHERE full_name = ?", (full_name,))

    def get_favorites(self) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM favorites ORDER BY added_at DESC").fetchall()
        return [self._favorite_row(row) for row in rows]

    def is_favorited(self, full_name: str) -> bool:
        with self._connect() as conn:
            row = conn.execute("SELECT 1 FROM favorites WHERE full_name = ?", (full_name,)).fetchone()
        return bool(row)

    def save_analysis(self, full_name: str, report: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE favorites SET analysis_data = ? WHERE full_name = ?",
                (report, full_name),
            )

    def update_notes(self, full_name: str, notes: str) -> None:
        with self._connect() as conn:
            conn.execute("UPDATE favorites SET notes = ? WHERE full_name = ?", (notes, full_name))

    def mark_viewed(self, full_name: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE favorites
                SET view_count = view_count + 1, last_viewed = ?
                WHERE full_name = ?
                """,
                (datetime.now().isoformat(timespec="seconds"), full_name),
            )

    def add_qa_record(self, repo_full_name: str, question: str, answer: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO qa_records (repo_full_name, question, answer, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (repo_full_name, question, answer, datetime.now().isoformat(timespec="seconds")),
            )

    def get_qa_records(self, repo_full_name: Optional[str] = None, limit: int = 30) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            if repo_full_name:
                rows = conn.execute(
                    """
                    SELECT * FROM qa_records WHERE repo_full_name = ?
                    ORDER BY created_at DESC LIMIT ?
                    """,
                    (repo_full_name, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM qa_records ORDER BY created_at DESC LIMIT ?",
                    (limit,),
                ).fetchall()
        return [dict(row) for row in rows]

    def add_learning_record(self, repo_full_name: str, action: str, details: Optional[Dict[str, Any]] = None) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO learning_records (repo_full_name, action, details, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    repo_full_name,
                    action,
                    json.dumps(details or {}, ensure_ascii=False),
                    datetime.now().isoformat(timespec="seconds"),
                ),
            )

    def get_learning_records(self, limit: int = 30) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM learning_records ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def add_note(self, repo_full_name: str, title: str, content: str) -> None:
        now = datetime.now().isoformat(timespec="seconds")
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO notes (repo_full_name, title, content, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (repo_full_name, title, content, now, now),
            )

    def get_notes(self, repo_full_name: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            if repo_full_name:
                rows = conn.execute(
                    "SELECT * FROM notes WHERE repo_full_name = ? ORDER BY updated_at DESC",
                    (repo_full_name,),
                ).fetchall()
            else:
                rows = conn.execute("SELECT * FROM notes ORDER BY updated_at DESC").fetchall()
        return [dict(row) for row in rows]

    def statistics(self) -> Dict[str, int]:
        with self._connect() as conn:
            return {
                "favorites": conn.execute("SELECT COUNT(*) FROM favorites").fetchone()[0],
                "qa_records": conn.execute("SELECT COUNT(*) FROM qa_records").fetchone()[0],
                "learning_records": conn.execute("SELECT COUNT(*) FROM learning_records").fetchone()[0],
                "notes": conn.execute("SELECT COUNT(*) FROM notes").fetchone()[0],
            }

    def get_statistics(self) -> Dict[str, int]:
        stats = self.statistics()
        return {
            "favorites_count": stats["favorites"],
            "qa_count": stats["qa_records"],
            "learning_records": stats["learning_records"],
            "notes_count": stats["notes"],
            "cached_repos": 0,
        }

    @staticmethod
    def _favorite_row(row: sqlite3.Row) -> Dict[str, Any]:
        return {
            "id": row["repo_id"],
            "full_name": row["full_name"],
            "description": row["description"],
            "html_url": row["html_url"],
            "stargazers_count": row["stargazers_count"],
            "forks_count": row["forks_count"],
            "language": row["language"],
            "analysis_report": row["analysis_data"],
            "notes": row["notes"],
            "added_at": row["added_at"],
            "last_viewed": row["last_viewed"],
            "view_count": row["view_count"],
        }
