# app/bmi.py

def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    """
    Calculate BMI using weight (kg) and height (cm).
    """
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    return round(bmi, 2)


def bmi_category(bmi: float) -> str:
    """
    Categorize BMI into health ranges.
    """
    if bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi < 24.9:
        return "Normal"
    elif 25 <= bmi < 29.9:
        return "Overweight"
    else:
        return "Obese"
