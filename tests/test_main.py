import contextlib
import io
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import main as main_module


class MainProgramTests(unittest.TestCase):
    def test_get_weather_returns_placeholder(self):
        self.assertEqual(
            main_module.get_weather(" Seattle "),
            "Weather lookup for Seattle is not connected yet.",
        )

    def test_get_weather_rejects_empty_city(self):
        with self.assertRaisesRegex(ValueError, "City cannot be empty"):
            main_module.get_weather(" ")

    def test_read_employee_salary_uses_demo_data(self):
        self.assertEqual(main_module.read_employee_salary("E-101"), 50_000)

    def test_read_employee_salary_rejects_unknown_employee(self):
        with self.assertRaisesRegex(ValueError, "Employee not found"):
            main_module.read_employee_salary("missing")

    def test_delete_employee_removes_demo_employee(self):
        with patch.dict(main_module.DEMO_EMPLOYEES):
            result = main_module.delete_employee("E-101")

            self.assertEqual(result, "Deleted demo employee E-101")
            self.assertNotIn("E-101", main_module.DEMO_EMPLOYEES)

    def test_delete_employee_rejects_unknown_employee(self):
        with self.assertRaisesRegex(ValueError, "Employee not found"):
            main_module.delete_employee("missing")

    @patch.dict(os.environ, {}, clear=True)
    @patch("main.ChatGroq")
    @patch("main.load_dotenv")
    def test_loads_project_env_and_calls_configured_groq_model(
        self, load_dotenv, chat_groq
    ):
        def set_test_environment(env_path):
            self.assertEqual(env_path, PROJECT_ROOT / ".env")
            os.environ["GROQ_API_KEY"] = "test-key"
            os.environ["model"] = "test-model"

        load_dotenv.side_effect = set_test_environment
        chat_groq.return_value.invoke.return_value.content = "Hello from the agent."
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            main_module.main()

        load_dotenv.assert_called_once_with(PROJECT_ROOT / ".env")
        chat_groq.assert_called_once_with(
            model="test-model",
            temperature=0,
            api_key="test-key",
        )
        chat_groq.return_value.invoke.assert_called_once_with(
            "Introduce yourself as the Governed AI Agent in one short sentence."
        )
        self.assertEqual(output.getvalue(), "Hello from the agent.\n")

    @patch.dict(os.environ, {}, clear=True)
    @patch("main.load_dotenv")
    def test_requires_groq_api_key(self, _load_dotenv):
        with self.assertRaisesRegex(SystemExit, "GROQ_API_KEY is not set"):
            main_module.main()


if __name__ == "__main__":
    unittest.main()
