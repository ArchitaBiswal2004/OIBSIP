# app/main.py

import tkinter as tk
from app.gui import BMICalculatorApp
from app.database import initialize_database


def main():
    initialize_database()
    root = tk.Tk()
    app = BMICalculatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
