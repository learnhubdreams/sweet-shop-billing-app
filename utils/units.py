# utils/units.py

def parse_quantity_unit(qty_str):
    """
    Parse quantity string with unit and convert to base unit:
    - grams (g) -> kilograms (kg)
    - kilograms (kg) -> kilograms (kg)
    - pieces (pcs, pc, piece) -> piece
    Returns (quantity_in_base_unit: float, base_unit: str or None)
    """
    qty_str = qty_str.strip().lower()
    if not qty_str:
        raise ValueError("Quantity cannot be empty")

    parts = qty_str.split()
    if len(parts) == 1:
        # Only number, no unit given (unit will be decided by caller)
        try:
            qty = float(parts[0])
            return qty, None
        except:
            raise ValueError("Invalid quantity format")
    elif len(parts) == 2:
        try:
            qty = float(parts[0])
        except:
            raise ValueError("Invalid quantity number")
        unit = parts[1]
        if unit in ("g", "gram", "grams"):
            return qty / 1000, "kg"
        elif unit in ("kg", "kilogram", "kilograms"):
            return qty, "kg"
        elif unit in ("pcs", "pc", "piece", "pieces"):
            return qty, "piece"
        else:
            raise ValueError(f"Unsupported unit: {unit}")
    else:
        raise ValueError("Invalid quantity format")
