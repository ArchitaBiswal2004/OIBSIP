# app/charts.py

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from datetime import datetime
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")


def plot_bmi_trend(records, username="user"):
    if not records:
        raise ValueError("No BMI history available to plot")

    # Ensure data directory exists
    os.makedirs(DATA_DIR, exist_ok=True)

    dates = [datetime.strptime(r[4], "%Y-%m-%d %H:%M:%S") for r in records]
    bmi_values = [r[2] for r in records]

    plt.figure(figsize=(8, 5))
    plt.plot(dates, bmi_values, marker='o')
    plt.xlabel("Date")
    plt.ylabel("BMI")
    plt.title("BMI Trend Over Time")
    plt.grid(True)
    plt.tight_layout()

    file_path = os.path.join(DATA_DIR, f"{username}_bmi_trend.png")
    plt.savefig(file_path)
    plt.close()

    return file_path


def bmi_statistics(records):
    if not records:
        raise ValueError("No BMI data available")

    bmi_values = [float(record[0]) for record in records]


    return {
        "min_bmi": round(min(bmi_values), 2),
        "max_bmi": round(max(bmi_values), 2),
        "avg_bmi": round(sum(bmi_values) / len(bmi_values), 2)
    }
