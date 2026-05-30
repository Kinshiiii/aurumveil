import os
import logging
import subprocess

from pathlib import Path
from subprocess import CREATE_NO_WINDOW


logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)


# ===== FLAGS =====
PROCESS_FLAGS = (
    CREATE_NO_WINDOW
    if os.name == "nt"
    else 0
)


# ===== PROCESS =====
def run_process(command: list[str], working_directory: Path) -> None:

    # ===== PROCESS INITIALIZATION =====
    process: subprocess.Popen = subprocess.Popen(
        command,
        cwd=working_directory,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        creationflags=PROCESS_FLAGS,
    )

    # ===== OUTPUT STREAM =====
    assert process.stdout is not None

    # ===== OUTPUT =====
    for line in process.stdout:
        logging.info(line.strip())

    process.wait()

    # ===== ERROR =====
    if process.returncode != 0:
        raise subprocess.CalledProcessError(
            process.returncode,
            command,
        )


# ===== TERMINAL =====
def clear_terminal() -> None:

    os.system(
        "cls"
        if os.name == "nt"
        else "clear"
    )


# ===== BUILD =====
def build_application() -> None:

    # ===== DIRECTORY =====
    build_dir: Path = (
        Path(__file__).resolve().parent.parent / "build"
    )

    build_dir.mkdir(exist_ok=True)

    # ===== CONFIGURE =====
    run_process(
        ["cmake", ".."],
        build_dir,
    )

    # ===== COMPILE =====
    run_process(
        ["cmake", "--build", "."],
        build_dir,
    )

    # ===== CLEAR =====
    clear_terminal()