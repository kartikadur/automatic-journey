import tempfile
import unittest
from pathlib import Path

from py_agent_harness.context import SEEN
from py_agent_harness.tasks import (
    TASKS,
    StatusProfile,
    TaskProfile,
    create_task_profiles,
)
from py_agent_harness.tools import TOOL_SCHEMAS, TOOLS, read_file, replace_at_index


class ReplaceAtIndexTests(unittest.TestCase):
    def test_replaces_first_occurrence(self) -> None:
        self.assert_replaces("x...x...x", "x", "Y", 0, "Y...x...x")

    def test_replaces_middle_occurrence(self) -> None:
        self.assert_replaces("x...x...x", "x", "Y", 1, "x...Y...x")

    def test_replaces_last_occurrence(self) -> None:
        self.assert_replaces("x...x...x", "x", "Y", 2, "x...x...Y")

    def test_occurrence_indices_are_non_overlapping(self) -> None:
        self.assert_replaces("aaaa", "aa", "Z", 1, "aaZ")

    def assert_replaces(
        self,
        content: str,
        old_str: str,
        new_str: str,
        index: int,
        expected_content: str,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            file_path = Path(directory) / "test.txt"
            file_path.write_text(content, encoding="utf-8")

            result = replace_at_index(str(file_path), old_str, new_str, index)

            self.assertIn("Successfully replaced", result)
            self.assertEqual(file_path.read_text(encoding="utf-8"), expected_content)


class ToolRegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        TASKS.clear()
        SEEN.clear()

    def test_schemas_match_registered_tools(self) -> None:
        schema_names = {schema["function"]["name"] for schema in TOOL_SCHEMAS}

        self.assertEqual(schema_names, set(TOOLS))

    def test_create_tasks_schema_describes_task_objects(self) -> None:
        schema = next(
            schema["function"]
            for schema in TOOL_SCHEMAS
            if schema["function"]["name"] == "create_tasks"
        )
        task_items = schema["parameters"]["properties"]["tasks"]["items"]

        self.assertEqual(schema["parameters"]["properties"]["tasks"]["type"], "array")
        self.assertEqual(schema["parameters"]["properties"]["tasks"]["minItems"], 1)
        self.assertEqual(task_items["type"], "object")
        self.assertEqual(
            task_items["required"], ["content", "status"]
        )

    def test_create_tasks_accepts_json_task_objects(self) -> None:
        result = TOOLS["create_tasks"](
            tasks=[
                {
                    "content": "Implement feature",
                    "status": "active",
                }
            ]
        )

        self.assertEqual(result, "[~] Implement feature")
        self.assertEqual(len(TASKS), 1)

    def test_create_tasks_rejects_empty_list_without_clearing_existing_tasks(self) -> None:
        existing_task = TaskProfile("Existing task", StatusProfile.ACTIVE)
        TASKS.append(existing_task)

        result = TOOLS["create_tasks"](tasks=[])

        self.assertEqual(result, "Error: tasks list cannot be empty")
        self.assertEqual(TASKS, [existing_task])

    def test_create_tasks_returns_error_for_invalid_task(self) -> None:
        result = TOOLS["create_tasks"](
            tasks=[
                {
                    "content": "Implement feature",
                    "status": "invalid",
                }
            ]
        )

        self.assertIn("Error creating tasks:", result)
        self.assertEqual(TASKS, [])

    def test_create_tasks_rejects_multiple_active_tasks_without_replacing_existing(self) -> None:
        existing_task = TaskProfile("Existing task", StatusProfile.ACTIVE)
        TASKS.append(existing_task)

        result = TOOLS["create_tasks"](
            tasks=[
                {"content": "First", "status": "active"},
                {"content": "Second", "status": "active"},
            ]
        )

        self.assertIn("exactly one active task", result)
        self.assertEqual(TASKS, [existing_task])

    def test_create_tasks_rejects_no_active_task_without_replacing_existing(self) -> None:
        existing_task = TaskProfile("Existing task", StatusProfile.ACTIVE)
        TASKS.append(existing_task)

        result = TOOLS["create_tasks"](
            tasks=[
                {"content": "First", "status": "pending"},
                {"content": "Second", "status": "done"},
            ]
        )

        self.assertIn("exactly one active task", result)
        self.assertEqual(TASKS, [existing_task])

    def test_create_task_profiles_rejects_empty_list_without_clearing_existing(self) -> None:
        existing_task = TaskProfile("Existing task", StatusProfile.ACTIVE)
        TASKS.append(existing_task)

        result = create_task_profiles([])

        self.assertEqual(result, "Error: Task list must not be empty")
        self.assertEqual(TASKS, [existing_task])

    def test_read_file_returns_error_for_missing_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            missing_path = Path(directory) / "missing.txt"

            result = read_file(str(missing_path))

        self.assertTrue(result.startswith("Error reading file:"))
        self.assertNotIn(str(missing_path), SEEN)

    def test_read_file_tracks_successfully_read_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            file_path = Path(directory) / "test.txt"
            file_path.write_text("contents", encoding="utf-8")

            result = read_file(str(file_path))

            self.assertEqual(result, "contents")
            self.assertIn(str(file_path), SEEN)


    def tearDown(self) -> None:
        TASKS.clear()
        SEEN.clear()


if __name__ == "__main__":
    unittest.main()
