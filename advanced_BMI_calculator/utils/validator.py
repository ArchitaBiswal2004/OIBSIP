# utils/validator.py

def validate_weight(weight: str) -> float:
    if not weight.strip():
        raise ValueError("Weight cannot be empty")

    weight = float(weight)
    if weight <= 0 or weight > 500:
        raise ValueError("Enter a valid weight (1–500 kg)")

    return weight


def validate_height(height: str) -> float:
    if not height.strip():
        raise ValueError("Height cannot be empty")

    height = float(height)
    if height <= 0 or height > 300:
        raise ValueError("Enter a valid height (1–300 cm)")

    return height
