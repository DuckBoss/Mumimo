import pathlib

import pytest

pytest_plugins = [
    "tests.fixtures.config_fixtures",
    "tests.fixtures.connection_fixtures",
]


@pytest.fixture(autouse=True)
def generated_files_teardown():
    generated_files_path = pathlib.Path("tests/data/generated")
    if not generated_files_path.exists():
        generated_files_path.mkdir(parents=True, exist_ok=True)
    yield
    for f in generated_files_path.glob("*"):
        if f.is_file():
            f.unlink()
            print(f"Removed generated test file: {f.name}")
    generated_files_path.rmdir()
