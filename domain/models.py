##
# @file models.py
# @brief Domain models used by the Aurumveil platform.
#
# Defines geometric structures, dwarfs entities,
# mining infrastructure, and the world data model
# used throughout the application.
#

from dataclasses import dataclass


##
# @brief Two-dimensional point.
#
# Represents a position within the world coordinate
# system used by miners, wardens, and mines.
#
@dataclass(slots=True)
class Point:
    x: float
    y: float


##
# @brief Base dwarf entity.
#
# Represents a named entity occupying a position
# within the world.
#
@dataclass(slots=True)
class Dwarf:
    identifier: str
    name: str
    position: Point


##
# @brief Mining unit.
#
# Represents a dwarf assigned to collect a specific
# resource type.
#
@dataclass(slots=True)
class Miner(Dwarf):
    resource: str = ""


##
# @brief Defensive unit.
#
# Represents a dwarf responsible for protecting
# a mining site and monitoring its surroundings.
#
@dataclass(slots=True)
class Warden(Dwarf):
    loudness: int
    boundary_radius: int


##
# @brief Mining site.
#
# Represents a resource deposit together with its
# extraction capacity and assigned warden.
#
@dataclass(slots=True)
class Mine:
    identifier: str
    resource_type: str

    capacity: int

    location: Point
    assigned_warden: Warden


##
# @brief World state container.
#
# Aggregates all miners and mines currently
# participating in the simulation.
#
@dataclass(slots=True)
class WorldData:
    miners: list[Miner]
    mines: list[Mine]

    ##
    # @brief Converts world data into a serializable dictionary.
    #
    # Transforms domain objects into a structure suitable
    # for JSON serialization and persistent storage.
    #
    # @return dict[str, list[dict[str, object]]]
    # Dictionary representation of the world state.
    #
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