import tempfile
import unittest
from pathlib import Path

from src.activity_store import (
    ActivityNotFoundError,
    ActivityStore,
    AlreadyRegisteredError,
    NotRegisteredError,
)


class ActivityStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_directory.cleanup)
        self.database_path = Path(self.temp_directory.name) / "activities.sqlite"
        self.initial_activities = {
            "Chess Club": {
                "description": "Play chess",
                "schedule": "Fridays",
                "max_participants": 12,
                "participants": ["student@example.com"],
            }
        }
        self.store = ActivityStore(self.database_path, self.initial_activities)
        self.store.initialize()

    def test_initial_activities_are_seeded_in_existing_api_shape(self):
        self.assertEqual(
            self.store.get_activities(),
            {
                "Chess Club": {
                    "description": "Play chess",
                    "schedule": "Fridays",
                    "max_participants": 12,
                    "participants": ["student@example.com"],
                }
            },
        )

    def test_registrations_survive_store_recreation(self):
        self.store.add_participant("Chess Club", "new@example.com")

        reopened_store = ActivityStore(
            self.database_path,
            {"Another Club": {
                "description": "Different defaults",
                "schedule": "Mondays",
                "max_participants": 5,
                "participants": [],
            }},
        )
        reopened_store.initialize()

        self.assertEqual(
            reopened_store.get_activities()["Chess Club"]["participants"],
            ["student@example.com", "new@example.com"],
        )
        self.assertNotIn("Another Club", reopened_store.get_activities())

    def test_unregister_is_persisted(self):
        self.store.remove_participant("Chess Club", "student@example.com")

        reopened_store = ActivityStore(self.database_path, self.initial_activities)
        reopened_store.initialize()

        self.assertEqual(
            reopened_store.get_activities()["Chess Club"]["participants"], []
        )

    def test_signup_rejects_unknown_activities_and_duplicates(self):
        with self.assertRaises(ActivityNotFoundError):
            self.store.add_participant("Unknown Club", "student@example.com")
        with self.assertRaises(AlreadyRegisteredError):
            self.store.add_participant("Chess Club", "student@example.com")

    def test_unregister_rejects_unknown_activities_and_unregistered_students(self):
        with self.assertRaises(ActivityNotFoundError):
            self.store.remove_participant("Unknown Club", "student@example.com")
        with self.assertRaises(NotRegisteredError):
            self.store.remove_participant("Chess Club", "unknown@example.com")


if __name__ == "__main__":
    unittest.main()
