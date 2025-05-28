from main import process_activities
import tkinter as tk
from tkinter import filedialog


def save_fit_file(activity_data: dict):
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.asksaveasfilename(
        defaultextension=".fit",
        filetypes=[("FIT Files", "*.fit")],
        title="Save merged activity as"
    )

    if not file_path:
        print("No save location selected. Exiting.")
        return


if __name__ == "__main__":
    activity_data = process_activities()
    save_fit_file(activity_data)