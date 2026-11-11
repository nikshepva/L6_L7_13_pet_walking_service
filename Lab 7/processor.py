"""Validated input-processing functions for the Pet Walking Service lab."""

def parse_walk_schedule(schedule_spec):
    """Parse '<pets>-<minutes>-<YES|NO>' and return a formatted quote."""
    if not isinstance(schedule_spec, str):
        raise ValueError("Schedule must be a string")
    parts = schedule_spec.strip().split("-")
    if len(parts) != 3:
        raise ValueError("Schedule must contain exactly three fields")
    pets_str, mins_str, weekend_str = (part.strip() for part in parts)
    try:
        pets, mins = int(pets_str), int(mins_str)
    except (TypeError, ValueError):
        raise ValueError("Pet count and minutes must be integers") from None
    if pets <= 0:
        raise ValueError("Pet count must be greater than zero")
    if mins <= 0:
        raise ValueError("Walk duration must be greater than zero")
    weekend_map = {"YES": 15.0, "NO": 0.0}
    weekend = weekend_str.upper()
    if weekend not in weekend_map:
        raise ValueError("Weekend flag must be YES or NO")
    base_fee = 20.0 if mins <= 30 else 35.0
    total = base_fee + pets * 5.0 + weekend_map[weekend]
    return f"Walk: {pets} pets, {mins} mins - Total ${total:.2f}"


def compute_pace_per_pet(walk_metrics_str):
    """Parse '<minutes>/<pets>' and return minutes per pet."""
    if not isinstance(walk_metrics_str, str):
        raise ValueError("Walk metrics must be a string")
    parts = walk_metrics_str.split("/")
    if len(parts) != 2:
        raise ValueError("Walk metrics must contain exactly one '/'")
    try:
        mins, pets = float(parts[0].strip()), float(parts[1].strip())
    except (TypeError, ValueError):
        raise ValueError("Minutes and pet count must be numeric") from None
    if not (mins > 0 and pets > 0 and mins < float("inf") and pets < float("inf")):
        raise ValueError("Minutes and pet count must be finite and greater than zero")
    return round(mins / pets, 2)


def lookup_temperament_surcharge(temperament_code):
    """Return surcharge for CAL, PLY, REA, or AGG temperament codes."""
    if not isinstance(temperament_code, str):
        raise ValueError("Temperament code must be a string")
    prefix = temperament_code.strip().upper()[:3]
    surcharges = {"CAL": 0.0, "PLY": 5.0, "REA": 12.0, "AGG": 20.0}
    if prefix not in surcharges:
        raise ValueError("Unknown temperament code")
    return surcharges[prefix]


def main():
    print("==== Running parse_walk_schedule ====")
    try:
        print(parse_walk_schedule(input("Enter schedule (e.g. 2-30-YES): ")))
    except ValueError as exc:
        print("Invalid schedule:", exc)
    print("\n==== Running compute_pace_per_pet ====")
    try:
        print("Pace (min/pet):", compute_pace_per_pet(input("Enter minutes/pets (e.g. 45/3): ")))
    except ValueError as exc:
        print("Invalid walk metrics:", exc)
    print("\n==== Running lookup_temperament_surcharge ====")
    try:
        print("Surcharge: $", lookup_temperament_surcharge(
            input("Enter temperament code (e.g. CALM, PLAYFUL, AGGRESSIVE): ")))
    except ValueError as exc:
        print("Invalid temperament:", exc)

if __name__ == "__main__":
    main()
