import json
import subprocess
import sys
import tempfile
from pathlib import Path

from models.domain import ProblemData


# ===== PATHS =====
BASE_DIR = Path(__file__).parent / "build"
EXECUTABLE_EXTENSION = ".exe" if sys.platform.startswith("win") else ""


# ===== EXECUTABLE PATH =====
def get_executable_path(algorithm_name: str) -> Path:
    return (BASE_DIR / f"{algorithm_name}{EXECUTABLE_EXTENSION}").resolve()


# ===== EXECUTABLES =====
EXECUTABLES: dict[str, Path] = {
    # MAX FLOW
    "Ford–Fulkerson Method": get_executable_path("ford"),
    "Edmonds–Karp Method": get_executable_path("edmonds"),
    "Dinic Method": get_executable_path("dinic"),

    # MIN COST
    "Bellman–Ford Method": get_executable_path("bellman"),
    "d'Esopo–Pape Method": get_executable_path("desopopape"),

    # MIN COST MAX FLOW
    "Min-Cost Max-Flow": get_executable_path("mcmf"),

    # GEOMETRY
    "Graham Scan Method": get_executable_path("graham"),
    "Jarvis March Method": get_executable_path("jarvis"),
    "Monotone Chain Method": get_executable_path("monotonic"),

    # SEGMENT
    "Brute Force Method": get_executable_path("brute"),
    "Segment Tree Method": get_executable_path("segment"),
}


# ===== DATA CONVERSION =====
def problem_data_to_dict(problem_data: ProblemData) -> dict:
    if problem_data is None:
        raise ValueError("ProblemData is None")

    return {
        "miners": [
            {
                "id": miner.identifier,
                "resource": miner.resource,
                "x": miner.position.x,
                "y": miner.position.y,
            }
            for miner in problem_data.miners
        ],
        "mines": [
            {
                "id": mine.identifier,
                "resource": mine.resource_type,
                "capacity": mine.capacity,
                "x": mine.location.x,
                "y": mine.location.y,
                "guard_loudness": mine.assigned_guard.loudness,
                "boundary": mine.assigned_guard.boundary_position,
            }
            for mine in problem_data.mines
        ],
    }


# ===== RUN ALGORITHM =====
def run_cpp_algorithm(
    algorithm_name: str,
    input_data: ProblemData | dict,
    value_range: tuple[int, int] | None = None,
) -> dict:

    executable_path = EXECUTABLES.get(algorithm_name)

    if not executable_path:
        return {
            "error": True,
            "stderr": f"No executable found for: {algorithm_name}",
            "stdout": "",
        }

    if not executable_path.exists():
        return {
            "error": True,
            "stderr": f"Executable not found or not compiled: {executable_path}",
            "stdout": "",
        }

    # ===== PREPARE INPUT =====
    if isinstance(input_data, ProblemData):
        payload = problem_data_to_dict(input_data)
    else:
        payload = input_data

    if value_range is not None:
        payload["range"] = value_range

    temp_file_path: Path | None = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w+", delete=False, suffix=".json"
        ) as temp_file:

            temp_file_path = Path(temp_file.name)

            json.dump(payload, temp_file)
            temp_file.flush()

            process_result = subprocess.run(
                [str(executable_path), temp_file.name],
                capture_output=True,
                text=True,
            )

    except Exception as error:
        return {
            "error": True,
            "stderr": str(error),
            "stdout": "",
        }

    finally:
        if temp_file_path and temp_file_path.exists():
            try:
                temp_file_path.unlink()
            except OSError:
                pass

    stdout = process_result.stdout.strip()
    stderr = process_result.stderr.strip()

    if process_result.returncode != 0:
        return {
            "error": True,
            "stderr": stderr or "An unknown error occurred",
            "stdout": stdout,
        }

    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        return {
            "error": True,
            "stderr": "Invalid JSON output from C++ program",
            "stdout": stdout,
        }