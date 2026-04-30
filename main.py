import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# ========== Data Model ==========
class WeatherDiary:
    def __init__(self, filename="weather_data.json"):
        self.filename = filename
        self.records = []
        self.load_from_file()

    def add_record(self, date, temp, description, precipitation):
        """Add a new weather record."""
        record = {
            "date": date,
            "temperature": temp,
            "description": description,
            "precipitation": precipitation
        }
        self.records.append(record)
        self.save_to_file()
        return record

    def filter_by_date(self, target_date):
        """Return records matching exact date (YYYY-MM-DD)."""
        return [r for r in self.records if r["date"] == target_date]

    def filter_by_temperature(self, min_temp=None, max_temp=None):
        """Filter by temperature range."""
        result = self.records
        if min_temp is not None:
            result = [r for r in result if r["temperature"] >= min_temp]
        if max_temp is not None:
            result = [r for r in result if r["temperature"] <= max_temp]
        return result

    def save_to_file(self):
        """Save all records to JSON."""
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(self.records, f, indent=4, ensure_ascii=False)

    def load_from_file(self):
        """Load records from JSON if file exists."""
        if os.path.exists(self.filename):
            with open(self.filename, "r", encoding="utf-8") as f:
                self.records = json.load(f)
        else:
            self.records = []

# ========== GUI Application ==========
class WeatherDiaryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Diary")
        self.root.geometry("750x500")

        self.diary = WeatherDiary()

        # Create GUI elements
        self.create_input_frame()
        self.create_record_list()
        self.create_filter_frame()
        self.create_action_buttons()

        self.refresh_record_list()

    def create_input_frame(self):
        frame = tk.LabelFrame(self.root, text="Add New Weather Record", padx=10, pady=10)
        frame.pack(fill="x", padx=10, pady=5)

        # Date
        tk.Label(frame, text="Date (YYYY-MM-DD):").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.date_entry = tk.Entry(frame, width=15)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)
        self.date_entry.insert(0, datetime.today().strftime("%Y-%m-%d"))

        # Temperature
        tk.Label(frame, text="Temperature (°C):").grid(row=0, column=2, sticky="e", padx=5, pady=5)
        self.temp_entry = tk.Entry(frame, width=10)
        self.temp_entry.grid(row=0, column=3, padx=5, pady=5)

        # Description
        tk.Label(frame, text="Description:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.desc_entry = tk.Entry(frame, width=40)
        self.desc_entry.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky="w")

        # Precipitation
        self.precip_var = tk.BooleanVar()
        tk.Checkbutton(frame, text="Precipitation (Yes/No)", variable=self.precip_var).grid(row=2, column=0, columnspan=2, sticky="w", padx=5, pady=5)

        # Add button
        self.add_btn = tk.Button(frame, text="➕ Add Record", command=self.add_record, bg="lightgreen")
        self.add_btn.grid(row=2, column=2, columnspan=2, pady=5)

    def create_record_list(self):
        frame = tk.LabelFrame(self.root, text="Weather Records", padx=10, pady=10)
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("Date", "Temperature (°C)", "Description", "Precipitation")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", height=12)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_filter_frame(self):
        frame = tk.LabelFrame(self.root, text="Filter Records", padx=10, pady=10)
        frame.pack(fill="x", padx=10, pady=5)

        # Date filter
        tk.Label(frame, text="Filter by Date (YYYY-MM-DD):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.filter_date_entry = tk.Entry(frame, width=15)
        self.filter_date_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Button(frame, text="Apply Date Filter", command=self.filter_by_date).grid(row=0, column=2, padx=5)

        # Temperature filter
        tk.Label(frame, text="Temperature >=").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.filter_temp_min = tk.Entry(frame, width=8)
        self.filter_temp_min.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        tk.Label(frame, text="°C").grid(row=1, column=2, sticky="w")

        tk.Label(frame, text="Temperature <=").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.filter_temp_max = tk.Entry(frame, width=8)
        self.filter_temp_max.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        tk.Label(frame, text="°C").grid(row=2, column=2, sticky="w")

        tk.Button(frame, text="Apply Temp Filter", command=self.filter_by_temperature).grid(row=1, column=3, rowspan=2, padx=10)
        tk.Button(frame, text="Clear Filters", command=self.refresh_record_list).grid(row=0, column=4, rowspan=3, padx=10)

    def create_action_buttons(self):
        frame = tk.Frame(self.root)
        frame.pack(fill="x", padx=10, pady=10)

        tk.Button(frame, text="💾 Save to JSON (Auto-saves)", command=self.save_manually, bg="lightblue").pack(side="left", padx=5)
        tk.Button(frame, text="📂 Load from JSON", command=self.load_manually, bg="lightyellow").pack(side="left", padx=5)
        tk.Button(frame, text="❌ Exit", command=self.root.quit, bg="lightcoral").pack(side="right", padx=5)

    # ========== Validation ==========
    def validate_inputs(self, date_str, temp_str, desc):
        if not desc.strip():
            messagebox.showerror("Error", "Description cannot be empty!")
            return False
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Invalid date format! Use YYYY-MM-DD")
            return False
        try:
            temp = float(temp_str)
            return True
        except ValueError:
            messagebox.showerror("Error", "Temperature must be a number!")
            return False

    def add_record(self):
        date = self.date_entry.get().strip()
        temp_str = self.temp_entry.get().strip()
        desc = self.desc_entry.get().strip()
        precip = self.precip_var.get()

        if not self.validate_inputs(date, temp_str, desc):
            return

        temp = float(temp_str)
        self.diary.add_record(date, temp, desc, precip)
        self.refresh_record_list()
        self.clear_input_fields()
        messagebox.showinfo("Success", "Weather record added!")

    def clear_input_fields(self):
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.today().strftime("%Y-%m-%d"))
        self.temp_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.precip_var.set(False)

    def refresh_record_list(self, filtered_records=None):
        for row in self.tree.get_children():
            self.tree.delete(row)
        records = filtered_records if filtered_records is not None else self.diary.records
        for rec in records:
            precip_text = "Yes" if rec["precipitation"] else "No"
            self.tree.insert("", "end", values=(
                rec["date"],
                rec["temperature"],
                rec["description"],
                precip_text
            ))

    def filter_by_date(self):
        target = self.filter_date_entry.get().strip()
        if not target:
            messagebox.showwarning("Warning", "Enter a date to filter (YYYY-MM-DD)")
            return
        try:
            datetime.strptime(target, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Invalid date format!")
            return
        filtered = self.diary.filter_by_date(target)
        if not filtered:
            messagebox.showinfo("No results", f"No records found for {target}")
        self.refresh_record_list(filtered)

    def filter_by_temperature(self):
        min_str = self.filter_temp_min.get().strip()
        max_str = self.filter_temp_max.get().strip()
        min_temp = None
        max_temp = None
        if min_str:
            try:
                min_temp = float(min_str)
            except ValueError:
                messagebox.showerror("Error", "Min temperature must be a number")
                return
        if max_str:
            try:
                max_temp = float(max_str)
            except ValueError:
                messagebox.showerror("Error", "Max temperature must be a number")
                return
        filtered = self.diary.filter_by_temperature(min_temp, max_temp)
        if not filtered:
            msg = f"No records with temp"
            if min_temp is not None:
                msg += f" >= {min_temp}"
            if max_temp is not None:
                msg += f" <= {max_temp}"
            messagebox.showinfo("No results", msg)
        self.refresh_record_list(filtered)

    def save_manually(self):
        self.diary.save_to_file()
        messagebox.showinfo("Saved", f"Data saved to {self.diary.filename}")

    def load_manually(self):
        file = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file:
            self.diary.filename = file
            self.diary.load_from_file()
            self.refresh_record_list()
            messagebox.showinfo("Loaded", f"Loaded from {file}")

# ========== Main ==========
if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherDiaryApp(root)
    root.mainloop()