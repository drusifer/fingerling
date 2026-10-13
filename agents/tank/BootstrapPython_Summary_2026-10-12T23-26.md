# Bootstrap Python build environment — fingerling

Ran `*devops bootstrap python` per `agents/skills/build-env/SKILL.md`.

## Survey
- Manifest: only `requirements.txt` (PyYAML, python-jsonpath). No pyproject/setup.py/lockfile.
- Tools on box: no uv/poetry/pdm/hatch/ruff/pytest. System Python 3.13.5, PEP 668 managed.
- Third-party imports: `yaml`, `jsonpath` (package); `rich` (examples/demo.py only).
- No CI config in the repo. Tests use `unittest`.

## Choices
| Concern | Choice | Why |
|---|---|---|
| Manifest | `pyproject.toml`, PEP 621, setuptools | ecosystem default; nothing pre-existing to honour |
| Package manager | stdlib `venv` + `pip` | no other tool or lockfile present |
| Environment | isolated `.venv` (was `--system-site-packages`) | all deps are on PyPI; nothing is OS-only |
| Dev group | `dev = ["fingerling[demo]"]`, `demo = ["rich>=13"]` | rich is only needed by the TUI demo |
| Entry point | `fingerling = fingerling.__main__:main` | gives `.venv/bin/fingerling` |
| Version pin | `requires-python = ">=3.13"` | only version ever run; no version manager in use |
| Lockfile | none (plain pip) | lower bounds only — versions can drift between installs |

## Makefile
Added `run`, `clean`, `distclean`; `install` now `pip install -e ".[dev]"`; `test` accepts `ARGS`;
all env-using targets guard on `.venv`. `chat` and `via_index` left on system tools (bob tooling).
Not added: `lint`, `format`, `build` (no linter configured, no artifact shipped).

## Verified
- `make distclean` → `make test` prints the install hint → `make install` → `make test`: 178/178.
- Second `make install`: no change. `include-system-site-packages = false`; yaml/rich resolve inside `.venv`.
- `.venv/bin/fingerling` and `make run` work; `sudo .venv/bin/python` imports all deps.
- `pip install -r requirements.txt` still resolves (dry run).

## Not verified / left for others
- Interactive `sudo make demo-live` (needs a TTY).
- Python < 3.13 compatibility.
- `Makefile.prj` is tracked but nothing includes it — left alone; owner should decide.
- `--help` usage line still says `python -m fingerling` (app code, Neo's call).
