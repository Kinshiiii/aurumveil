from dataclasses import dataclass


# ===== GEOMETRIC TYPES =====
@dataclass(slots=True)
class Point:
    x: float
    y: float


# ===== DWARVEN ENTITIES =====
@dataclass(slots=True)
class Dwarf:
    identifier: str
    name: str
    position: Point


# ===== MINING UNIT =====
@dataclass(slots=True)
class Miner(Dwarf):
    resource: str = ""


# ===== DEFENSIVE UNIT =====
@dataclass(slots=True)
class Warden(Dwarf):
    loudness: int
    boundary_radius: int


# ===== MINING SITE =====
@dataclass(slots=True)
class Mine:
    identifier: str
    resource_type: str

    capacity: int

    location: Point
    assigned_warden: Warden


# ===== WORLD DATA =====
@dataclass(slots=True)
class WorldData:
    miners: list[Miner]
    mines: list[Mine]

    def to_dict(self) -> dict[str, list[dict[str, object]]]:

        return {
            "miners": [
                {
                    "id": miner.identifier,

                    "name": miner.name,

                    "resource": miner.resource,

                    "x": miner.position.x,
                    "y": miner.position.y,
                }
                for miner in self.miners
            ],

            "mines": [
                {
                    "id": mine.identifier,
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
                for mine in self.mines
            ],
        }