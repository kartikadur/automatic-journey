import tempfile
import unittest
from pathlib import Path

from py_agent_harness.tools import TOOL_SCHEMAS, TOOLS, replace_at_index


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
    def test_schemas_match_registered_tools(self) -> None:
        schema_names = {schema["function"]["name"] for schema in TOOL_SCHEMAS}

        self.assertEqual(schema_names, set(TOOLS))


if __name__ == "__main__":
    unittest.main()
