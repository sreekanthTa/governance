import os
from dataclasses import dataclass
from pathlib import Path

from langchain_groq import ChatGroq
from dotenv import load_dotenv


DEFAULT_MODEL = "qwen/qwen3-32b"
API_KEY_ENV_VAR = "GROQ_API_KEY"
MODEL_ENV_VAR = "model"
PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass
class DemoEmployee:
    name: str
    salary: int

DEMO_EMPLOYEES: dict[str, DemoEmployee] = {
    "E-101": DemoEmployee(name="Alex Example", salary=50_000),
}


def get_weather(city: str) -> str:
    """Return a placeholder until a weather service is connected."""
    city = city.strip()
    if not city:
        raise ValueError("City cannot be empty")

    return f"Weather lookup for {city} is not connected yet."


def read_employee_salary(employee_id: str) -> int:
    """Return the salary from the in-memory demo employee data."""
    employee = DEMO_EMPLOYEES.get(employee_id)
    if employee is None:
        raise ValueError("Employee not found")

    return employee.salary


def delete_employee(employee_id: str) -> str:
    """Delete an employee from the in-memory demo data."""
    if employee_id not in DEMO_EMPLOYEES:
        raise ValueError("Employee not found")

    del DEMO_EMPLOYEES[employee_id]
    return f"Deleted demo employee {employee_id}"


def main():
    load_dotenv(PROJECT_ROOT / ".env")

    api_key = os.environ.get(API_KEY_ENV_VAR)
    if not api_key:
        raise SystemExit(
            f"{API_KEY_ENV_VAR} is not set. Load it from .env or set it in your environment."
        )

    model = ChatGroq(
        model=os.environ.get(MODEL_ENV_VAR, DEFAULT_MODEL),
        temperature=0,
        api_key=api_key,
    )
    response = model.invoke(
        "Introduce yourself as the Governed AI Agent in one short sentence."
    )
    print(response.content)


if __name__ == "__main__":
    main()
