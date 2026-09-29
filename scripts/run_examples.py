import subprocess
import tomllib
from pathlib import Path

CURRENT_FILE = Path(__file__)
ROOT = CURRENT_FILE.parent.parent

EXAMPLES = ROOT / "examples"

BORDER = "====="


def _package_name(example_dir: Path) -> str:
    pyproject = tomllib.loads((example_dir / "pyproject.toml").read_text(encoding="utf-8"))
    return pyproject["project"]["name"]


def test_examples():
    entry_points = [entry for entry in EXAMPLES.iterdir() if entry.is_dir()]

    for entry_point in entry_points:
        print(BORDER, "Running tests on directory", entry_point.name, BORDER)
        package_name = _package_name(entry_point)

        executables: list[Path] = []
        for root, _, files in (entry_point / "src").walk():
            for file in files:
                if not file.endswith(".py"):
                    continue
                file_path = root / file
                with open(file_path, encoding="utf-8") as f:
                    if 'if __name__ == "__main__":' in f.read():
                        executables.append(file_path)

        for executable in executables:
            command = ["uv", "run", "--package", package_name, str(executable)]
            print(command)
            subprocess.check_output(command)


if __name__ == "__main__":
    test_examples()
