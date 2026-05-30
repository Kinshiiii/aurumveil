##
# @file runtime_initializer.py
# @brief Runtime initialization and build utilities.
#
# Provides functionality for configuring, building,
# and launching the native algorithm engine used
# by the Aurumveil platform.
#

import os
import logging
import subprocess

from pathlib import Path
from subprocess import CREATE_NO_WINDOW


logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)


##
# @brief Platform-specific process creation flags.
#
# Prevents console windows from being displayed
# on Microsoft Windows during subprocess execution.
#
PROCESS_FLAGS = (
    CREATE_NO_WINDOW
    if os.name == "nt"
    else 0
)


##
# @brief Executes an external process and streams its output.
#
# Launches a subprocess, forwards its output to the
# application logger, and raises an exception when
# the process terminates with an error.
#
# @param command
# Command and arguments passed to the subprocess.
#
# @param working_directory
# Working directory used during execution.
#
# @throws subprocess.CalledProcessError
# Raised when the process exits with a non-zero code.
#
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


##
# @brief Clears the terminal window.
#
# Invokes the operating system specific command
# used to clear the current console session.
#
def clear_terminal() -> None:

    os.system(
        "cls"
        if os.name == "nt"
        else "clear"
    )


##
# @brief Configures and builds the native engine.
#
# Creates the build directory when necessary,
# executes the CMake configuration step,
# compiles the native C++ components,
# and clears the terminal after a successful build.
#
# @throws subprocess.CalledProcessError
# Raised when the configuration or compilation
# process fails.
#
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