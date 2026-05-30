import json
import subprocess
import sys
import tempfile

from pathlib import Path

from domain.models import (
    WorldData,
)


# ===== EXECUTABLE CONFIGURATION =====
EXECUTABLE_DIRECTORY: Path = (
    Path(__file__).parent.parent
    / "build"
    / "bin"
)

PLATFORM_EXECUTABLE_SUFFIX: str = (
    ".exe"
    if sys.platform.startswith("win")
    else ""
)


# ===== EXECUTABLE PATH RESOLUTION =====
def get_executable_path(executable_name: str) -> Path:

    executable_path: Path = (
        EXECUTABLE_DIRECTORY
        / (
            f"{executable_name}"
            f"{PLATFORM_EXECUTABLE_SUFFIX}"
        )
    )

    return executable_path.resolve()


# ===== ALGORITHM EXECUTABLES =====
EXECUTABLES: dict[str, Path] = {

    # ===== MINIMUM COST MAXIMUM FLOW =====
    "Min-Cost Max-Flow Method": get_executable_path("mcmf"),

    # ===== COMPUTATIONAL GEOMETRY =====
    "Graham Scan Method": get_executable_path("graham"),
    "Jarvis March Method": get_executable_path("jarvis"),
    "Monotone Chain Method": get_executable_path("monotonic"),

    # ===== RANGE QUERY STRUCTURES =====
    "Brute Force Method": get_executable_path("brute"),
    "Segment Tree Method": get_executable_path("segment"),
}


# ===== ALGORITHM EXECUTION =====
def run_cpp_algorithm(
    algorithm_name: str,
    input_data: WorldData | dict[str, object],
    value_range: tuple[int, int] | None = None,
) -> dict[str, object]:

    # ===== EXECUTABLE LOOKUP =====
    executable_path: Path | None = (
        EXECUTABLES.get(
            algorithm_name
        )
    )

    # ===== EXECUTABLE VALIDATION =====
    if executable_path is None:
        return {
            "error": True,

            "stderr": (
                "The selected algorithm does not "
                "have a registered executable."
            ),

            "stdout": "",
        }

    if not executable_path.exists():
        return {
            "error": True,

            "stderr": (
                "The executable file for the selected "
                "algorithm could not be found."
            ),

            "stdout": "",
        }

    # ===== INPUT SERIALIZATION =====
    payload: dict[str, object]

    if isinstance(
        input_data,
        WorldData,
    ):
        payload = (
            input_data.to_dict()
        )

    else:
        payload = input_data


    # ===== RANGE INJECTION =====
    if value_range is not None:
        payload["range"] = value_range

    # ===== TEMPORARY FILE STATE =====
    temporary_file_path: Path | None = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w+",
            delete=False,
            suffix=".json",
        ) as temporary_file:

            temporary_file_path = Path(
                temporary_file.name
            )

            # ===== PAYLOAD EXPORT =====
            json.dump(
                payload,
                temporary_file,
            )

            temporary_file.flush()

            # ===== PROCESS EXECUTION =====
            process_result = subprocess.run(
                [
                    str(executable_path),
                    temporary_file.name,
                ],

                capture_output=True,
                text=True,
            )

    # ===== EXECUTION FAILURE =====
    except Exception as execution_error:
        return {
            "error": True,

            "stderr": str(
                execution_error
            ),

            "stdout": "",
        }

    # ===== TEMPORARY FILE CLEANUP =====
    finally:
        if (
            temporary_file_path is not None
            and temporary_file_path.exists()
        ):
            try:
                temporary_file_path.unlink()

            except OSError:
                pass


    # ===== PROCESS OUTPUT =====
    standard_output: str = (
        process_result.stdout.strip()
    )

    standard_error: str = (
        process_result.stderr.strip()
    )

    # ===== PROCESS STATUS VALIDATION =====
    if process_result.returncode != 0:
        return {
            "error": True,

            "stderr": (
                standard_error
                or "The executable process failed unexpectedly."
            ),

            "stdout": standard_output,
        }

    # ===== OUTPUT DESERIALIZATION =====
    try:
        return json.loads(
            standard_output
        )

    # ===== INVALID OUTPUT FORMAT =====
    except json.JSONDecodeError:
        return {
            "error": True,

            "stderr": (
                "The executable returned "
                "an invalid JSON response."
            ),

            "stdout": standard_output,
        }