project is set up as a lib package
use `uv add <module_name>` to add module to project
use `uv run python -m py_agent_harness.<file_name>` to run that file as main.
use `uv run python -m unittest discover -s tests/ -v` to run unittests as tests is a directory and not a package.