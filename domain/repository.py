##
# @file repository.py
# @brief Persistent storage utilities for world data.
#
# Provides functionality for loading, validating,
# serializing, compressing, and storing world data
# used by the Aurumveil platform.
#

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

##
# @brief Default runtime state file.
#
DEFAULT_DATA_FILE: Path = (
    DATA_DIRECTORY / "runtime_state.huff"
)

##
# @brief Directory containing importable datasets.
#
RAW_DATA_DIRECTORY: Path = (
    DATA_DIRECTORY / "datasets"
)


##
# @file repository.py
# @brief Persistent storage utilities for world data.
#
# Provides functionality for loading, validating,
# serializing, compressing, and storing world data
# used by the Aurumveil platform.
#
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


##
# @brief Validates the structure of serialized world data.
#
# Verifies that the provided JSON object contains
# all mandatory top-level sections required by
# the application.
#
# @param json_data
# JSON object to validate.
#
# @throws ValueError
# Raised when the structure is invalid.
#
def _validate_json_structure(json_data: dict) -> None:

    if (
        not isinstance(json_data, dict)
        or "miners" not in json_data
        or "mines" not in json_data
    ):
        raise ValueError(
            "The provided data file has an invalid structure."
        )


##
# @brief Loads the default world state.
#
# Loads and reconstructs the world model stored
# in the default runtime state file.
#
# @return WorldData | None
# Loaded world data or None if no state file exists.
#
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


##
# @brief Loads world data from a compressed file.
#
# Reads a Huffman-compressed data file, decompresses
# its contents, validates the resulting JSON structure,
# and reconstructs the corresponding domain model.
#
# @param file_path
# Path to the compressed data file.
#
# @return WorldData
# Reconstructed world model.
#
# @throws ValueError
# Raised when the file contains invalid data.
#
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


##
# @brief Saves the world state to the default location.
#
# Serializes and persists the specified world model
# using the default runtime state file.
#
# @param world_data
# World model to persist.
#
def save_default_data(world_data: WorldData) -> None:

    # ===== DATA DIRECTORIES =====
    _ensure_data_directories()

    # ===== SAVE FILE =====
    save_data_to_path(
        world_data,
        str(DEFAULT_DATA_FILE),
    )


##
# @brief Saves world data to a compressed file.
#
# Serializes the provided world model into JSON,
# compresses the result using Huffman coding,
# and writes the compressed data to disk.
#
# @param world_data
# World model to serialize.
#
# @param file_path
# Destination file path.
#
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


##
# @brief Saves a dataset snapshot to the dataset repository.
#
# Serializes the specified world model, generates a
# content-based hash, and stores the compressed dataset
# if an identical snapshot does not already exist.
#
# @param world_data
# World model to persist.
#
# @return str
# Generated dataset filename.
#
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


##
# @brief Creates a canonical representation of world data.
#
# Produces a deterministic dictionary representation
# independent of entity ordering. The resulting structure
# is suitable for hashing, comparisons, and duplicate
# dataset detection.
#
# @param world_data
# World model to normalize.
#
# @return dict[str, list[dict[str, object]]]
# Canonical world data representation.
#
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


##
# @brief Removes the default runtime state file.
#
# Deletes the persisted runtime state when it exists,
# allowing the application to start with an empty world.
#
def delete_data_file() -> None:

    # ===== DATA DIRECTORIES =====
    _ensure_data_directories()

    # ===== FILE REMOVAL =====
    if DEFAULT_DATA_FILE.exists():
        DEFAULT_DATA_FILE.unlink()