import hashlib
import json

from pathlib import Path
from typing import Any

from engine.compression.huffman_codec import (
    compress_text,
    decompress_text,
)

from domain.models import (
    Mine,
    Miner,
    Point,
    Warden,
    WorldData,
)


# ===== PATHS =====
BASE_DIR: Path = (
    Path(__file__).resolve().parent.parent
)

DATA_DIRECTORY: Path = (
    BASE_DIR / "assets"
)

DEFAULT_DATA_FILE: Path = (
    DATA_DIRECTORY / "runtime_state.huff"
)

RAW_DATA_DIRECTORY: Path = (
    DATA_DIRECTORY / "datasets"
)


# ===== INTERNAL =====
def _ensure_data_directories() -> None:

    # ===== DATA DIRECTORY =====
    DATA_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ===== RAW DATA DIRECTORY =====
    RAW_DATA_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )


# ===== VALIDATION =====
def _validate_json_structure(json_data: dict) -> None:

    if (
        not isinstance(json_data, dict)
        or "miners" not in json_data
        or "mines" not in json_data
    ):
        raise ValueError(
            "The provided data file has an invalid structure."
        )


# ===== LOAD =====
def load_default_data() -> WorldData | None:

    # ===== DATA DIRECTORIES =====
    _ensure_data_directories()

    # ===== FILE VALIDATION =====
    if not DEFAULT_DATA_FILE.exists():
        return None

    # ===== LOAD FILE =====
    return load_from_file(
        str(DEFAULT_DATA_FILE)
    )


# ===== FILE LOAD =====
def load_from_file(file_path: str) -> WorldData:

    # ===== FILE READ =====
    with open(file_path, "rb") as file:
        compressed_data: bytes = (
            file.read()
        )

    # ===== DATA DECOMPRESSION =====
    decoded_json: str = (
        decompress_text(
            compressed_data
        )
    )

    # ===== JSON PARSING =====
    json_data: dict[str, Any] = (
        json.loads(
            decoded_json
        )
    )

    # ===== STRUCTURE VALIDATION =====
    _validate_json_structure(
        json_data
    )

    # ===== MINERS =====
    miners: list[Miner] = [
        Miner(
            identifier=miner["id"],

            name=miner.get(
                "name",
                "Dwarf",
            ),

            resource=miner.get(
                "resource",
                "",
            ),

            position=Point(
                miner["x"],
                miner["y"],
            ),
        )
        for miner in json_data["miners"]
    ]

    # ===== MINES =====
    mines: list[Mine] = []

    for mine in json_data["mines"]:

        # ===== POSITION =====
        position_x: float = mine["x"]
        position_y: float = mine["y"]

        # ===== LOCATION =====
        mine_location: Point = Point(
            position_x,
            position_y,
        )

        # ===== WARDEN =====
        assigned_warden: Warden = (
            Warden(
                identifier=(
                    f"{mine['id']}_W"
                ),

                name="Warden",

                position=mine_location,

                loudness=mine[
                    "guard_loudness"
                ],

                boundary_radius=int(
                    mine.get(
                        "boundary",
                        0,
                    )
                ),
            )
        )

        # ===== MINE =====
        mines.append(
            Mine(
                identifier=mine["id"],

                resource_type=mine[
                    "resource"
                ],

                capacity=mine[
                    "capacity"
                ],

                location=mine_location,

                assigned_warden=assigned_warden,
            )
        )

    # ===== RESULT =====
    return WorldData(miners, mines)


# ===== SAVE =====
def save_default_data(world_data: WorldData) -> None:

    # ===== DATA DIRECTORIES =====
    _ensure_data_directories()

    # ===== SAVE FILE =====
    save_data_to_path(
        world_data,
        str(DEFAULT_DATA_FILE),
    )


# ===== FILE SAVE =====
def save_data_to_path(world_data: WorldData, file_path: str) -> None:

    # ===== DATA DIRECTORIES =====
    _ensure_data_directories()

    # ===== SERIALIZATION =====
    data_dict: dict = world_data.to_dict()

    serialized_json: str = json.dumps(
        data_dict,
        indent=4,
    )

    # ===== COMPRESSION =====
    compressed_data: bytes = (
        compress_text(
            serialized_json
        )
    )

    # ===== FILE WRITE =====
    with open(file_path, "wb") as file:
        file.write(
            compressed_data
        )


# ===== RAW DATA SAVE =====
def save_raw_data(world_data: WorldData) -> str:

    # ===== DATA DIRECTORIES =====
    _ensure_data_directories()

    # ===== SERIALIZATION =====
    data_dict: dict = world_data.to_dict()

    serialized_json: str = json.dumps(
        data_dict,
        sort_keys=True,
        separators=(",", ":"),
    )

    # ===== HASH =====
    content_hash: str = (
        hashlib.sha256(
            serialized_json.encode()
        ).hexdigest()
    )

    # ===== FILE PATH =====
    filename: str = (
        f"data_{content_hash}.huff"
    )

    raw_file_path: Path = (
        RAW_DATA_DIRECTORY / filename
    )

    # ===== FILE SAVE =====
    if not raw_file_path.exists():

        formatted_json: str = json.dumps(
            data_dict,
            indent=4,
        )

        compressed_data: bytes = (
            compress_text(
                formatted_json
            )
        )

        with open(raw_file_path, "wb") as file:
            file.write(
                compressed_data
            )

    return filename


# ===== CANONICAL SERIALIZATION =====
def to_canonical_dict(world_data: WorldData) -> dict[str, list[dict[str, object]]]:

    # ===== MINERS =====
    miners: list[dict[str, object]] = sorted(
        [
            {
                "name": miner.name,

                "resource": miner.resource,

                "x": miner.position.x,
                "y": miner.position.y,
            }
            for miner in world_data.miners
        ],

        key=lambda miner_entry: (
            miner_entry["name"],
            miner_entry["resource"],

            miner_entry["x"],
            miner_entry["y"],
        ),
    )

    # ===== MINES =====
    mines: list[dict[str, object]] = sorted(
        [
            {
                "resource": mine.resource_type,

                "capacity": mine.capacity,

                "x": mine.location.x,
                "y": mine.location.y,

                "guard_loudness": (
                    mine.assigned_warden.loudness
                ),

                "boundary": (
                    mine.assigned_warden.boundary_radius
                ),
            }
            for mine in world_data.mines
        ],

        key=lambda mine_entry: (
            mine_entry["resource"],
            mine_entry["capacity"],

            mine_entry["x"],
            mine_entry["y"],

            mine_entry["guard_loudness"],
            mine_entry["boundary"],
        ),
    )

    # ===== RESULT =====
    return {
        "miners": miners,
        "mines": mines,
    }


# ===== CLEANUP =====
def delete_data_file() -> None:

    # ===== DATA DIRECTORIES =====
    _ensure_data_directories()

    # ===== FILE REMOVAL =====
    if DEFAULT_DATA_FILE.exists():
        DEFAULT_DATA_FILE.unlink()