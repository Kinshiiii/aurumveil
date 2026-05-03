from models.domain import (
    ProblemData,
    Miner,
    Mine,
    Guard,
    Point,
)


# ===== INPUT PARSER =====
class InputParser:

    # ===== PARSE TEXT =====
    @staticmethod
    def parse(text: str) -> ProblemData:
        lines: list[str] = [line.strip() for line in text.splitlines() if line.strip()]

        section: str | None = None
        miners: list[Miner] = []
        mines: list[Mine] = []

        for line in lines:

            # ===== SECTION SWITCH =====
            if line == "MINERS":
                section = "miners"
                continue

            if line == "MINES":
                section = "mines"
                continue

            parts = line.split()

            # ===== VALIDATION =====
            if section is None:
                raise ValueError(f"Line outside of section: {line}")

            # ===== PARSE MINERS =====
            if section == "miners":
                if len(parts) != 3:
                    raise ValueError(f"Invalid miner format: {line}")

                miners.append(
                    Miner(
                        identifier=parts[0],
                        name="Krasnoludek",
                        position=Point(float(parts[1]), float(parts[2])),
                    )
                )

            # ===== PARSE MINES =====
            elif section == "mines":
                if len(parts) != 8:
                    raise ValueError(f"Invalid mine format: {line}")

                mine_id: str = parts[0]
                resource: str = parts[1]
                capacity: int = int(parts[2])
                x: float = float(parts[3])
                y: float = float(parts[4])
                loudness: int = int(parts[6])
                boundary: float = float(parts[7])

                guard: Guard = Guard(
                    identifier=f"{mine_id}_G",
                    name="Guard",
                    position=Point(x, y),
                    loudness=loudness,
                    boundary_position=boundary,
                )

                mines.append(
                    Mine(
                        identifier=mine_id,
                        resource_type=resource,
                        capacity=capacity,
                        location=Point(x, y),
                        assigned_guard=guard,
                    )
                )

        # ===== RESULT =====
        return ProblemData(miners=miners, mines=mines)