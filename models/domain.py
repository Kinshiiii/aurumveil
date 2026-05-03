from dataclasses import dataclass


# ===== GEOMETRY =====
@dataclass(slots=True)
class Point:
    x: float
    y: float


# ===== BASE ENTITY =====
@dataclass(slots=True)
class Dwarf:
    identifier: str
    name: str
    position: Point


# ===== MINER =====
@dataclass(slots=True)
class Miner(Dwarf):
    resource: str = ""


# ===== GUARD =====
@dataclass(slots=True)
class Guard(Dwarf):
    loudness: int
    boundary_position: float


# ===== MINE =====
@dataclass(slots=True)
class Mine:
    identifier: str
    resource_type: str
    capacity: int
    location: Point
    assigned_guard: Guard


# ===== MAIN DATA CONTAINER =====
@dataclass(slots=True)
class ProblemData:
    miners: list[Miner]
    mines: list[Mine]