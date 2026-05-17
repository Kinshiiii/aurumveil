import json
import hashlib
from pathlib import Path

from models.domain import (
    ProblemData,
    Miner,
    Mine,
    Guard,
    Point,
)

from core.compression.huffman import (
    compress_text,
    decompress_text,
)


# ===== PATHS =====
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIRECTORY = BASE_DIR / "data"
DEFAULT_DATA_FILE = DATA_DIRECTORY / "data.huff"
RAW_DATA_DIRECTORY = DATA_DIRECTORY / "raw"


# ===== INTERNAL =====
def _ensure_data_directories() -> None:
    DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)
    RAW_DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)


def _validate_json_structure(json_data: dict) -> None:
    if not isinstance(json_data, dict) or "miners" not in json_data or "mines" not in json_data:
        raise ValueError("Invalid JSON structure")


# ===== LOAD =====
def load_default_data() -> ProblemData | None:
    _ensure_data_directories()

    if not DEFAULT_DATA_FILE.exists():
        return None

    return load_from_file(str(DEFAULT_DATA_FILE))


def load_from_file(file_path: str) -> ProblemData:
    with open(file_path, "rb") as file:
        compressed = file.read()

    decoded_json = decompress_text(compressed)

    json_data = json.loads(decoded_json)

    _validate_json_structure(json_data)

    miners: list[Miner] = [
        Miner(
            identifier=miner["id"],
            name=miner.get("name", "Krasnoludek"),
            resource=miner.get("resource", ""),
            position=Point(miner["x"], miner["y"]),
        )
        for miner in json_data["miners"]
    ]

    mines: list[Mine] = []

    for mine in json_data["mines"]:
        position_x: float = mine["x"]
        position_y: float = mine["y"]

        guard: Guard = Guard(
            identifier=f"{mine['id']}_G",
            name="Guard",
            position=Point(position_x, position_y),
            loudness=mine["guard_loudness"],
            boundary_position=float(mine.get("boundary", 0)),
        )

        mines.append(
            Mine(
                identifier=mine["id"],
                resource_type=mine["resource"],
                capacity=mine["capacity"],
                location=Point(position_x, position_y),
                assigned_guard=guard,
            )
        )

    return ProblemData(miners, mines)


# ===== SAVE =====
def save_default_data(problem_data: ProblemData) -> None:
    _ensure_data_directories()

    data_dict = _to_dict(problem_data)

    serialized = json.dumps(
        data_dict,
        indent=4,
    )

    compressed = compress_text(serialized)

    with open(DEFAULT_DATA_FILE, "wb") as file:
        file.write(compressed)


def save_data_to_path(problem_data: ProblemData, file_path: str) -> None:
    _ensure_data_directories()

    data_dict = _to_dict(problem_data)

    serialized = json.dumps(
        data_dict,
        indent=4,
    )

    compressed = compress_text(serialized)

    with open(file_path, "wb") as file:
        file.write(compressed)


def save_raw_data(data: ProblemData) -> str:
    _ensure_data_directories()

    data_dict = _to_dict(data)
    serialized_json = json.dumps(data_dict, sort_keys=True, separators=(",", ":"))
    hash_value = hashlib.sha256(serialized_json.encode()).hexdigest()

    filename = f"data_{hash_value}.huff"
    raw_file_path = RAW_DATA_DIRECTORY / filename

    if not raw_file_path.exists():
        serialized = json.dumps(
            data_dict,
            indent=4,
        )

        compressed = compress_text(serialized)

        with open(raw_file_path, "wb") as file:
            file.write(compressed)

    return filename


# ===== SERIALIZATION =====
def _to_dict(data: ProblemData) -> dict:
    return {
        "miners": [
            {
                "id": miner.identifier,
                "name": miner.name,
                "resource": miner.resource,
                "x": miner.position.x,
                "y": miner.position.y,
            }
            for miner in data.miners
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
            for mine in data.mines
        ],
    }


# ===== CLEANUP =====
def delete_data_file() -> None:
    _ensure_data_directories()

    if DEFAULT_DATA_FILE.exists():
        DEFAULT_DATA_FILE.unlink()