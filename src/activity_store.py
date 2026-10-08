"""SQLite persistence for activities and their registered participants."""

from collections.abc import Generator, Mapping
from contextlib import contextmanager
import sqlite3
from pathlib import Path
from typing import TypedDict


class Activity(TypedDict):
    description: str
    schedule: str
    max_participants: int
    participants: list[str]


class ActivityNotFoundError(Exception):
    """Raised when an operation references an unknown activity."""


class AlreadyRegisteredError(Exception):
    """Raised when a student is already registered for an activity."""


class NotRegisteredError(Exception):
    """Raised when removing a student who is not registered."""


class ActivityStore:
    def __init__(
        self,
        database_path: Path,
        initial_activities: Mapping[str, Activity],
    ) -> None:
        self.database_path = Path(database_path)
        self.initial_activities = initial_activities

    def _connect(self) -> sqlite3.Connection:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.database_path, timeout=5)
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    @contextmanager
    def _connection(self) -> Generator[sqlite3.Connection, None, None]:
        connection = self._connect()
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def initialize(self) -> None:
        with self._connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS activities (
                    name TEXT PRIMARY KEY,
                    description TEXT NOT NULL,
                    schedule TEXT NOT NULL,
                    max_participants INTEGER NOT NULL,
                    display_order INTEGER NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS participants (
                    id INTEGER PRIMARY KEY,
                    activity_name TEXT NOT NULL REFERENCES activities(name)
                        ON DELETE CASCADE,
                    email TEXT NOT NULL,
                    UNIQUE (activity_name, email)
                )
                """
            )

            activity_count = connection.execute(
                "SELECT COUNT(*) FROM activities"
            ).fetchone()[0]
            if activity_count == 0:
                for order, (name, activity) in enumerate(
                    self.initial_activities.items()
                ):
                    connection.execute(
                        """
                        INSERT INTO activities
                            (name, description, schedule, max_participants, display_order)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            name,
                            activity["description"],
                            activity["schedule"],
                            activity["max_participants"],
                            order,
                        ),
                    )
                    connection.executemany(
                        """
                        INSERT INTO participants (activity_name, email)
                        VALUES (?, ?)
                        """,
                        (
                            (name, email)
                            for email in activity["participants"]
                        ),
                    )

    def get_activities(self) -> dict[str, Activity]:
        with self._connection() as connection:
            activity_rows = connection.execute(
                """
                SELECT name, description, schedule, max_participants
                FROM activities
                ORDER BY display_order
                """
            ).fetchall()
            participant_rows = connection.execute(
                """
                SELECT activity_name, email
                FROM participants
                ORDER BY id
                """
            ).fetchall()

        participants_by_activity = {}
        for activity_name, email in participant_rows:
            participants_by_activity.setdefault(activity_name, []).append(email)

        activities: dict[str, Activity] = {
            name: {
                "description": description,
                "schedule": schedule,
                "max_participants": max_participants,
                "participants": participants_by_activity.get(name, []),
            }
            for name, description, schedule, max_participants in activity_rows
        }
        return activities

    def add_participant(self, activity_name: str, email: str) -> None:
        with self._connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            activity_exists = connection.execute(
                "SELECT 1 FROM activities WHERE name = ?", (activity_name,)
            ).fetchone()
            if activity_exists is None:
                raise ActivityNotFoundError(activity_name)

            already_registered = connection.execute(
                """
                SELECT 1 FROM participants
                WHERE activity_name = ? AND email = ?
                """,
                (activity_name, email),
            ).fetchone()
            if already_registered is not None:
                raise AlreadyRegisteredError(email)

            connection.execute(
                "INSERT INTO participants (activity_name, email) VALUES (?, ?)",
                (activity_name, email),
            )

    def remove_participant(self, activity_name: str, email: str) -> None:
        with self._connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            activity_exists = connection.execute(
                "SELECT 1 FROM activities WHERE name = ?", (activity_name,)
            ).fetchone()
            if activity_exists is None:
                raise ActivityNotFoundError(activity_name)

            result = connection.execute(
                """
                DELETE FROM participants
                WHERE activity_name = ? AND email = ?
                """,
                (activity_name, email),
            )
            if result.rowcount == 0:
                raise NotRegisteredError(email)
