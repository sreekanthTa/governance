# Governed AI Agent

A beginner-friendly Python project to build a simple LLM-powered agent and
progressively integrate Microsoft's Agent Governance Toolkit (AGT). The agent
will use simple Python tools, with AGT checks controlling every tool execution.
The LLM will not execute tools directly or decide its own permissions.

## Roadmap

1. Verify the currently documented AGT APIs against the installed package and
   official documentation before using them.
2. Add deterministic governance tests before connecting an LLM.
3. Implement `get_weather`, `read_employee_salary`, and `delete_employee` as
   simple Python tools, and route every tool call through AGT governance
   checks.
4. Connect an LLM through the configurable Groq provider (`langchain_groq`).
   Keep tool execution and permission decisions in the application and AGT,
   not in the LLM.

This project does not include RAG, document retrieval, PDF loading, or a vector
database.

## Verified API notes (installed AGT 4.1.0)

These were confirmed against the installed packages, not from documentation:

- The runtime SDK is `agent_control_specification`. The public entry point is
  `AgentControl` (e.g. `AgentControl.from_path(...)`). There is no `HostSession`
  or session object.
- Enforcement methods are async: `evaluate_intervention_point`, `run`,
  `run_tool`, `protect_tool`, `agent_startup`, `agent_shutdown`,
  `guard_session`. Evaluate one tool call with
  `await control.evaluate_intervention_point(InterventionPoint.PRE_TOOL_CALL, {...})`.
- A verdict is read as `result.verdict.decision` and `result.verdict.reason`
  (there is no `reason_code`).
- Manifests declare `agent_control_specification_version`. Supported values are
  `0.3.1-beta`, `0.3.1-beta-agt`, `0.3.0-alpha`, `0.3.0-alpha-agt`.
- Every tool named by `tool_name_from` must also be declared in a top-level
  `tools:` section, or the call fails with `runtime_error:tool_unknown`.
- The runtime's default policy dispatcher supports only `rego` policies.
  `cedar`, `test`, and `custom` policies require a host-supplied
  `policy_dispatcher` that returns the verdict.
- `cedar` policies must declare exactly one of `policy_set` or `policy_path`.

## Install AGT

The official quick start recommends Python 3.11 or newer. Add AGT's full Python
stack with `uv`:

```powershell
uv add "agent-governance-toolkit[full]"
```

This adds AGT's core, integrations, CLI, and protocols packages. It does not
install ChromaDB or an LLM provider. The Groq integration is installed
separately as `langchain-groq`:

```powershell
uv add langchain-groq
```

## Configure Groq

The application loads `GROQ_API_KEY` and the optional lowercase `model`
variable from the project-root `.env` file. The model defaults to
`qwen/qwen3-32b`. Existing environment variables take precedence over `.env`.

```powershell
uv run python src/main.py
```

The application makes a single chat call and prints the model response. It
does not give the model tools to execute.

## Run the application

After configuring `GROQ_API_KEY` in `.env`, run with `uv`:

```powershell
uv run python src/main.py
```

The response comes from the configured Groq model and may vary between runs.
If the project virtual environment is activated, `python .\src\main.py` also
loads `.env` automatically.

## Run the test

The test uses Python's built-in `unittest` module, so no extra packages are
needed:

```powershell
uv run python -m unittest discover -s tests
```

## Project files

- `src/main.py` is the application entry point.
- `tests/test_main.py` checks the entry point's printed output.
- `pyproject.toml` contains the project's basic metadata and Python version
  requirement.
- `README.md` explains how to run the application and test.
