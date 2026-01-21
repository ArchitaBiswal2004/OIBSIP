def get_bmi_category_and_insight(bmi: float) -> dict:
    """
    Classify BMI based on WHO standards and return category with health insight.
    """

    if bmi < 18.5:
        return {
            "category": "Underweight",
            "risk": "Possible nutritional deficiency",
            "insight": (
                "Your BMI is below the healthy range. "
                "You may consider consulting a healthcare professional "
                "for proper nutritional guidance."
            )
        }

    elif 18.5 <= bmi < 25:
        return {
            "category": "Normal Weight",
            "risk": "Low health risk",
            "insight": (
                "You are within a healthy BMI range. "
                "Maintain a balanced diet and regular physical activity."
            )
        }

    elif 25 <= bmi < 30:
        return {
            "category": "Overweight",
            "risk": "Increased risk of cardiovascular diseases",
            "insight": (
                "Your BMI indicates that you are overweight. "
                "Regular exercise and a healthy diet are recommended."
            )
        }

    elif 30 <= bmi < 35:
        return {
            "category": "Obese Class I",
            "risk": "Moderate health risk",
            "insight": (
                "Your BMI falls under Obesity Class I. "
                "Lifestyle modifications and medical guidance are advised."
            )
        }

    elif 35 <= bmi < 40:
        return {
            "category": "Obese Class II",
            "risk": "Severe health risk",
            "insight": (
                "Your BMI indicates Obesity Class II, associated with severe health risks. "
                "Consulting a healthcare professional is strongly recommended."
            )
        }

    else:
        return {
            "category": "Obese Class III",
            "risk": "Very severe health risk",
            "insight": (
                "Your BMI falls under Obesity Class III. "
                "Immediate medical supervision is advised."
            )
        }
def detect_bmi_trend_warning(records):
    """
    Detects increasing BMI trend over last 3 records.
    Returns warning text or None.
    """
    if len(records) < 3:
        return None

    last_three = [float(r[0]) for r in records[-3:]]

    if last_three[0] < last_three[1] < last_three[2]:
        return (
            "⚠ Health Trend Alert\n\n"
            "Your BMI has shown a consistent upward trend over recent measurements.\n\n"
            "This may increase the risk of health issues if continued.\n"
            "Consider reviewing diet, physical activity, or consulting a healthcare professional."
        )

    return None
