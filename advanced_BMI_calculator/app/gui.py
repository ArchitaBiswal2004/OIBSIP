# app/gui.py
import csv
from tkinter import filedialog
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from utils.bmi_insights import get_bmi_category_and_insight
from app.bmi import calculate_bmi
from app.database import save_bmi_record, fetch_user_history
from app.charts import plot_bmi_trend, bmi_statistics
from utils.validator import validate_weight, validate_height
from utils.bmi_insights import detect_bmi_trend_warning

class BMICalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced BMI Calculator")
        self.root.geometry("420x480")
        self.root.resizable(False, False)

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="Username").pack(pady=5)
        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack()

        tk.Label(self.root, text="Weight (kg)").pack(pady=5)
        self.weight_entry = tk.Entry(self.root)
        self.weight_entry.pack()

        tk.Label(self.root, text="Height (cm)").pack(pady=5)
        self.height_entry = tk.Entry(self.root)
        self.height_entry.pack()

        tk.Button(self.root, text="Calculate BMI", command=self.calculate).pack(pady=10)
        tk.Button(self.root, text="📊 Show Statistics", command=self.show_stats).pack(pady=5)
        tk.Button(self.root, text="📈 Generate BMI Chart", command=self.generate_chart).pack(pady=5)
        tk.Button(self.root, text="📁 Export BMI History (CSV)", command=self.export_csv).pack(pady=5)
        tk.Button(self.root, text="📜 Show BMI History", command=self.show_history).pack(pady=5)


        self.bmi_result_label = tk.Label(self.root, text="", font=("Arial", 12, "bold"))
        self.bmi_result_label.pack(pady=8)
        self.bmi_progress = ttk.Progressbar(self.root, orient="horizontal", length=300, mode="determinate", maximum=40)  # realistic BMI upper bound
        self.bmi_progress.pack(pady=6)


        self.category_label = tk.Label(self.root, text="", font=("Arial", 11, "bold"))
        self.category_label.pack(pady=2)

        self.risk_label = tk.Label(self.root, text="", font=("Arial", 11))
        self.risk_label.pack(pady=2)

        self.insight_label = tk.Label(
            self.root,
            text="",
            wraplength=380,
            justify="left",
            font=("Arial", 10)
        )
        self.insight_label.pack(pady=6)

    def show_history(self):
        try:
            username = self.username_entry.get().strip()
            if not username:
                raise ValueError("Username is required")

            records = fetch_user_history(username)
            if not records:
                raise ValueError("No BMI records found for this user")

            history_window = tk.Toplevel(self.root)
            history_window.title(f"{username}'s BMI History")
            history_window.geometry("720x320")
            history_window.resizable(False, False)

            columns = ("Date", "BMI", "Category", "Health Risk")

            tree = ttk.Treeview(
            history_window,
            columns=columns,
            show="headings",
            height=12
            )
            tree.tag_configure("normal", background="#d4edda")
            tree.tag_configure("warning", background="#fff3cd")
            tree.tag_configure("danger", background="#f8d7da")


            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, anchor="center", width=170)

            for bmi, category, risk, insight, timestamp in records:
                category_lower = category.lower()

                if "normal" in category_lower:
                    tag = "normal"
                elif "underweight" in category_lower or "overweight" in category_lower:
                    tag = "warning"
                else:
                    tag = "danger"

                tree.insert( "", tk.END,values=(
                timestamp.split(" ")[0],
                round(float(bmi), 2),
                category,
                risk),tags=(tag,))


        except Exception as e:
            messagebox.showerror("Error", str(e))


    def calculate(self):
        try:
            username = self.username_entry.get().strip()
            if not username:
                raise ValueError("Username is required")

            weight = validate_weight(self.weight_entry.get())
            height = validate_height(self.height_entry.get())

            bmi = calculate_bmi(weight, height)
            self.bmi_progress["value"] = min(bmi, 40)
            insight_data = get_bmi_category_and_insight(bmi)

            colors = {
                "Underweight": "orange",
                "Normal Weight": "green",
                "Overweight": "orange",
                "Obese Class I": "red",
                "Obese Class II": "red",
                "Obese Class III": "darkred"
            }

            self.bmi_result_label.config(text=f"BMI: {bmi:.2f}")
            self.category_label.config(
                text=f"Category: {insight_data['category']}",
                fg=colors.get(insight_data["category"], "black")
            )
            self.risk_label.config(text=f"Health Risk: {insight_data['risk']}")
            self.insight_label.config(text=f"Insight: {insight_data['insight']}")

            save_bmi_record(
                username=username,
                weight=weight,
                height=height,
                bmi=bmi,
                category=insight_data["category"],
                health_risk=insight_data["risk"],
                insight=insight_data["insight"])
            records = fetch_user_history(username)
            warning = detect_bmi_trend_warning(records)

            if warning:
                messagebox.showwarning("BMI Trend Warning", warning)
    
            


        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_stats(self):
        try:
            username = self.username_entry.get().strip()
            if not username:
                raise ValueError("Username is required")

            records = fetch_user_history(username)
            if not records:
                raise ValueError("No records found for this user")

            stats = bmi_statistics(records)

            messagebox.showinfo(
                "BMI Statistics",
                f"Min BMI: {stats['min_bmi']}\n"
                f"Max BMI: {stats['max_bmi']}\n"
                f"Average BMI: {stats['avg_bmi']}"
            )

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def export_csv(self):
        try:
            username = self.username_entry.get().strip()
            if not username:
                raise ValueError("Username is required")

            records = fetch_user_history(username)
            if not records:
                raise ValueError("No records to export")

            file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"{username}_bmi_history.csv"
        )

            if not file_path:
                return

            with open(file_path, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Date", "BMI", "Category", "Health Risk", "Insight"])

                for bmi, category, risk, insight, timestamp in records:
                    writer.writerow([
                    timestamp.split(" ")[0],
                    round(float(bmi), 2),
                    category,
                    risk,
                    insight
                ])

            messagebox.showinfo("Success", "BMI history exported successfully")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def check_bmi_trend_warning(records):
        if len(records) < 3:
            return None

        last_three = [float(r[0]) for r in records[-3:]]

        if last_three[0] < last_three[1] < last_three[2]:
            return (
            "⚠ BMI Trend Alert\n\n"
            "Your BMI has increased consistently over recent entries.\n"
            "Consider reviewing diet, activity levels, or consulting a professional."
        )

        return None



    def generate_chart(self):
        try:
            username = self.username_entry.get().strip()
            if not username:
                raise ValueError("Username is required")

            records = fetch_user_history(username)
            if not records:
                raise ValueError("No records found for this user")

            path = plot_bmi_trend(records, username=username)

            messagebox.showinfo(
                "Chart Generated",
                f"BMI trend chart saved at:\n{path}"
            )

        except Exception as e:
            messagebox.showerror("Error", str(e))
