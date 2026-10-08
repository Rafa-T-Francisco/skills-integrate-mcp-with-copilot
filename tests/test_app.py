import asyncio
import tempfile
import unittest
from pathlib import Path

from fastapi import HTTPException

import src.app as app_module
from src.activity_store import ActivityStore


class ActivityRouteTests(unittest.TestCase):
    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_directory.cleanup)
        self.original_store = app_module.activity_store
        self.addCleanup(
            setattr,
            app_module,
            "activity_store",
            self.original_store,
        )
        app_module.activity_store = ActivityStore(
            Path(self.temp_directory.name) / "activities.sqlite",
            {
                "Chess Club": {
                    "description": "Play chess",
                    "schedule": "Fridays",
                    "max_participants": 12,
                    "participants": ["student@example.com"],
                }
            },
        )
        app_module.activity_store.initialize()

    def test_activity_response_shape_is_unchanged(self):
        self.assertEqual(
            app_module.get_activities(),
            {
                "Chess Club": {
                    "description": "Play chess",
                    "schedule": "Fridays",
                    "max_participants": 12,
                    "participants": ["student@example.com"],
                }
            },
        )

    def test_lifespan_initializes_the_database_before_serving(self):
        uninitialized_store = ActivityStore(
            Path(self.temp_directory.name) / "startup.sqlite",
            {
                "Chess Club": {
                    "description": "Play chess",
                    "schedule": "Fridays",
                    "max_participants": 12,
                    "participants": [],
                }
            },
        )
        app_module.activity_store = uninitialized_store

        async def start_application():
            async with app_module.lifespan(app_module.app):
                return uninitialized_store.get_activities()

        self.assertIn("Chess Club", asyncio.run(start_application()))

    def test_signup_and_unregister_responses_are_unchanged(self):
        self.assertEqual(
            app_module.signup_for_activity("Chess Club", "new@example.com"),
            {"message": "Signed up new@example.com for Chess Club"},
        )
        self.assertEqual(
            app_module.unregister_from_activity("Chess Club", "new@example.com"),
            {"message": "Unregistered new@example.com from Chess Club"},
        )

    def test_signup_and_unregister_errors_keep_their_http_status(self):
        with self.assertRaises(HTTPException) as missing_activity:
            app_module.signup_for_activity("Unknown Club", "student@example.com")
        self.assertEqual(missing_activity.exception.status_code, 404)

        with self.assertRaises(HTTPException) as duplicate_signup:
            app_module.signup_for_activity("Chess Club", "student@example.com")
        self.assertEqual(duplicate_signup.exception.status_code, 400)

        with self.assertRaises(HTTPException) as missing_registration:
            app_module.unregister_from_activity("Chess Club", "unknown@example.com")
        self.assertEqual(missing_registration.exception.status_code, 400)


if __name__ == "__main__":
    unittest.main()
