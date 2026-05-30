from domain.models import (
    Mine,
    Miner,
    Point,
    Warden,
    WorldData,
)


# ===== INPUT PARSER =====
class InputParser:

    # ===== TEXT PARSING =====
    @staticmethod
    def parse(text: str) -> WorldData:

        # ===== CLEAN LINES =====
        clean_lines: list[str] = [
            raw_line.strip()
            for raw_line in text.splitlines()
            if raw_line.strip()
        ]

        # ===== CURRENT SECTION =====
        current_section: str | None = None

        # ===== DATA CONTAINERS =====
        miners: list[Miner] = []
        mines: list[Mine] = []

        # ===== LINE PARSING =====
        for raw_line in clean_lines:

            # ===== SECTION SWITCH =====
            if raw_line == "MINERS":
                current_section = "miners"
                continue

            if raw_line == "MINES":
                current_section = "mines"
                continue

            # ===== VALUE PARTS =====
            line_parts: list[str] = raw_line.split()

            # ===== SECTION VALIDATION =====
            if current_section is None:
                raise ValueError(
                    f"Line outside of section: {raw_line}"
                )

            # ===== MINER PARSING =====
            if current_section == "miners":

                if len(line_parts) != 3:
                    raise ValueError(
                        f"Invalid miner format: {raw_line}"
                    )

                miners.append(
                    Miner(
                        identifier=line_parts[0],

                        name="Dwarf",

                        resource="",

                        position=Point(
                            float(line_parts[1]),
                            float(line_parts[2]),
                        ),
                    )
                )

            # ===== MINE PARSING =====
            elif current_section == "mines":

                if len(line_parts) != 8:
                    raise ValueError(
                        f"Invalid mine format: {raw_line}"
                    )

                # ===== BASIC VALUES =====
                mine_identifier: str = line_parts[0]
                resource_type: str = line_parts[1]
                capacity: int = int(line_parts[2])

                # ===== POSITION =====
                position_x: float | int = float(line_parts[3])
                position_y: float | int = float(line_parts[4])

                # ===== WARDEN VALUES =====
                alert_volume: int = int(line_parts[6])
                boundary_radius: float | int = float(line_parts[7])

                # ===== LOCATION =====
                mine_location: Point = Point(
                    position_x,
                    position_y,
                )

                # ===== WARDEN =====
                assigned_warden: Warden = (
                    Warden(
                        identifier=(
                            f"{mine_identifier}W"
                        ),

                        name="Warden",

                        position=mine_location,

                        loudness=alert_volume,

                        boundary_radius=int(boundary_radius),
                    )
                )

                # ===== MINE =====
                mines.append(
                    Mine(
                        identifier=mine_identifier,

                        resource_type=resource_type,

                        capacity=capacity,

                        location=mine_location,

                        assigned_warden=assigned_warden,
                    )
                )

        # ===== RESULT =====
        return WorldData(miners=miners, mines=mines)