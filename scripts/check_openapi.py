#!/usr/bin/env python3
"""
Pre-commit hook to ensure OpenAPI specification files are up-to-date.
"""

import json
import subprocess

# import sys
from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING

# import typer
from upkeeper.core import JSONDict
from upkeeper.logging_config import get_console

if TYPE_CHECKING:
    from _typeshed import StrOrBytesPath

# logger = get_logger(__name__)
# app = typer.Typer(help="Pre-commit hook to check OpenAPI specification files.")
console = get_console()


def run_command(cmd: "StrOrBytesPath | Sequence[StrOrBytesPath]") -> tuple[int, str]:
    """Run a command and return exit code and output."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        return result.returncode, result.stdout
    except Exception as e:  # noqa: BLE001
        return 1, str(e)


def generate_openapi_files(
    openapi_path: "StrOrBytesPath", client_path: "StrOrBytesPath"
) -> tuple[bool, str]:
    """Generate both openapi.json and openapi_client.json files."""
    errors: list[str] = []

    # Generate standard OpenAPI spec
    exit_code, output = run_command(
        ["uv", "run", "upkeeper", "devtools", "generate-openapi-spec", "-o", openapi_path]
    )
    if exit_code != 0:
        errors.append(f"Failed to generate openapi.json: {output}")

    # Generate client OpenAPI spec
    exit_code, output = run_command(
        [
            "uv",
            "run",
            "upkeeper",
            "devtools",
            "generate-openapi-spec",
            "--client",
            "-o",
            client_path,
        ]
    )
    if exit_code != 0:
        errors.append(f"Failed to generate openapi_client.json: {output}")

    if errors:
        return False, "\n".join(errors)

    return True, "OpenAPI files generated successfully"


def files_are_identical(file1: Path, file2: Path) -> bool:
    """Check if two JSON files have identical content."""
    if not file1.exists() or not file2.exists():
        return False

    try:
        with file1.open("r", encoding="utf-8") as f1, file2.open("r", encoding="utf-8") as f2:
            json1: JSONDict = json.load(f1)  # pyright: ignore[reportAny]
            json2: JSONDict = json.load(f2)  # pyright: ignore[reportAny]
            return json1 == json2
    except (json.JSONDecodeError, OSError):
        return False


# @app.command()
def main() -> int:
    """Main hook function."""
    project_root = Path.cwd()

    # File paths
    openapi_file = project_root / "openapi.json"
    client_file = project_root / "openapi_client.json"
    temp_openapi = project_root / ".openapi_temp.json"
    temp_client = project_root / ".openapi_client_temp.json"

    print("Checking OpenAPI specification files...")

    # Generate temporary files
    # success, message = generate_openapi_files(temp_openapi, temp_client)
    # if not success:
    #     print(f"[ERROR] Error generating OpenAPI files: {message}")
    #     return 1

    # Move generated files to temp location for comparison
    # if openapi_file.exists():
    #     _ = openapi_file.rename(temp_openapi)
    # if client_file.exists():
    #     _ = client_file.rename(temp_client)

    # Generate fresh files
    success, message = generate_openapi_files(openapi_file, client_file)
    if not success:
        print(f"[ERROR] Error generating fresh OpenAPI files: {message}")
        # Restore original files
        if temp_openapi.exists():
            _ = temp_openapi.rename(openapi_file)
        if temp_client.exists():
            _ = temp_client.rename(client_file)
        return 1

    return 0

    # Compare files
    # files_changed: list[str] = []

    # if not files_are_identical(openapi_file, temp_openapi):
    #     files_changed.append("openapi.json")

    # if not files_are_identical(client_file, temp_client):
    #     files_changed.append("openapi_client.json")

    # # Clean up temp files
    # if temp_openapi.exists():
    #     temp_openapi.unlink()
    # if temp_client.exists():
    #     temp_client.unlink()

    # if files_changed:
    #     print("[FAILED] OpenAPI specification files are out of date!")
    #     print(f"   Changed files: {', '.join(files_changed)}")
    #     print("   Run the following commands to update them:")
    #     print("   uv run upkeeper devtools generate-openapi-spec -o openapi.json")
    #     print("   uv run upkeeper devtools generate-openapi-spec --client -o openapi_client.json")
    #     print("   Then stage the updated files with: git add openapi*.json")
    #     return 1

    # print("[SUCCESS] OpenAPI specification files are up to date")
    # return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
