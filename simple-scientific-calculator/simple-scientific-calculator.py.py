"""
Advanced Scientific Calculator - Mobile Enhanced Edition (Fixed)
Features:
- Large touch-friendly buttons
- Basic, Scientific, Converter, Graph, History tabs
- Full trigonometric & hyperbolic functions (DEG/RAD/GRAD)
- Unit converter (Length, Mass, Temperature, Area, Volume, Speed, Time)
- Function plotting (requires matplotlib)
- Memory with M+, M-, MR, MC
- History with timestamp and export
- Customizable theme (Dark/Light)
- Copy/Paste support
- Responsive layout
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import math
from functools import partial
from datetime import datetime

# Optional imports
try:
    import matplotlib.pyplot as plt
    import numpy as np
    MATPLOTLIB = True
except ImportError:
    MATPLOTLIB = False


class MobileCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Scientific Calculator")
        self.root.configure(bg="#121212")

        # Responsive sizing - FIXED: call root.update_idletasks()
        self.root.update_idletasks()
        width = self.root.winfo_screenwidth()
        height = self.root.winfo_screenheight()
        if width > 700:  # Desktop fallback
            width, height = 480, 700
        self.root.geometry(f"{width}x{height}")
        self.root.minsize(320, 700)
        self.root.bind("<Configure>", self.on_resize)

        # Calculator state
        self.expression = ""
        self.memory = 0.0
        self.last_result = 0.0
        self.angle_mode = "DEG"  # DEG, RAD, GRAD
        self.history = []  # list of (expr, result, timestamp)
        self.theme = "dark"

        # UI components (will be created later)
        self.display_var = tk.StringVar()
        self.mode_btn = None
        self.memory_label = None
        self.theme_btn = None
        self.history_listbox = None
        self.conv_category = None
        self.conv_from = None
        self.conv_to = None
        self.conv_value = None
        self.conv_result_label = None
        self.func_entry = None
        self.xmin = None
        self.xmax = None
        self.points = None

        # Build UI
        self._setup_styles()
        self._build_ui()
        self._bind_keys()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", font=("Segoe UI", 14, "bold"), padding=10)
        style.configure("TLabel", font=("Segoe UI", 12), background="#121212", foreground="white")
        style.configure("TFrame", background="#121212")
        style.configure("TLabelframe", background="#121212", foreground="white")
        style.configure("TLabelframe.Label", background="#121212", foreground="white")
        style.configure("TNotebook", background="#121212", tabmargins=(2, 5, 2, 0))
        style.configure("TNotebook.Tab", font=("Segoe UI", 12, "bold"), padding=[12, 6])
        style.map("TNotebook.Tab", background=[("selected", "#2c2c2c")])

    def _build_ui(self):
        # Display
        self.display = tk.Entry(
            self.root, textvariable=self.display_var, font=("Consolas", 32, "bold"),
            justify="right", bg="#1e1e1e", fg="#00e5ff", relief="flat",
            insertbackground="white", state="readonly", readonlybackground="#1e1e1e"
        )
        self.display.pack(fill="x", padx=8, pady=(8, 4), ipady=15)

        # Top bar
        top_bar = tk.Frame(self.root, bg="#121212")
        top_bar.pack(fill="x", padx=8, pady=(0, 5))

        self.mode_btn = tk.Button(
            top_bar, text="DEG", font=("Segoe UI", 12, "bold"),
            bg="#2c2c2c", fg="#00e5ff", command=self.toggle_angle_mode,
            padx=10, pady=5, relief="flat"
        )
        self.mode_btn.pack(side="left", padx=2)

        self.memory_label = tk.Label(
            top_bar, text="M=0", font=("Segoe UI", 12),
            bg="#121212", fg="#aaaaaa"
        )
        self.memory_label.pack(side="left", padx=10)

        self.theme_btn = tk.Button(
            top_bar, text="🌙", font=("Segoe UI", 12),
            command=self.toggle_theme, bg="#2c2c2c", fg="white",
            relief="flat", padx=8, pady=5
        )
        self.theme_btn.pack(side="right", padx=2)

        # Memory toolbar
        mem_toolbar = tk.Frame(self.root, bg="#121212")
        mem_toolbar.pack(fill="x", padx=8, pady=4)
        for text, cmd in [("MC", self.mem_clear), ("MR", self.mem_recall),
                          ("M+", self.mem_add), ("M-", self.mem_sub),
                          ("AC", self.clear_all), ("DEL", self.delete),
                          ("C", self.clear_entry), ("Ans", self.insert_ans)]:
            btn = tk.Button(mem_toolbar, text=text, command=cmd, font=("Segoe UI", 11, "bold"),
                            bg="#2c2c2c", fg="white", padx=6, pady=6, relief="flat")
            btn.pack(side="left", expand=True, fill="x", padx=2)

        # Notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)

        # Basic tab
        self.basic_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.basic_frame, text=" Basic ")

        # Scientific tab (scrollable)
        self.sci_canvas = tk.Canvas(self.notebook, bg="#121212", highlightthickness=0)
        self.sci_scroll = ttk.Scrollbar(self.notebook, orient="vertical", command=self.sci_canvas.yview)
        self.sci_frame = ttk.Frame(self.sci_canvas)
        self.sci_frame.bind("<Configure>", lambda e: self.sci_canvas.configure(scrollregion=self.sci_canvas.bbox("all")))
        self.sci_canvas.create_window((0, 0), window=self.sci_frame, anchor="nw")
        self.sci_canvas.configure(yscrollcommand=self.sci_scroll.set)
        self.notebook.add(self.sci_canvas, text=" Scientific ")
        self.notebook.add(self.sci_scroll, text="")
        

        # Converter tab
        self.converter_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.converter_frame, text=" Converter ")

        # Graph tab
        if MATPLOTLIB:
            self.graph_frame = ttk.Frame(self.notebook)
            self.notebook.add(self.graph_frame, text=" Graph ")
        else:
            self.graph_frame = None

        # History tab
        self.history_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.history_frame, text=" History ")

        # Build each tab
        self._build_basic_buttons()
        self._build_scientific_buttons()
        self._build_converter()
        if MATPLOTLIB:
            self._build_graph()
        self._build_history_panel()

        self._update_memory_display()

    # -------------------- Basic Tab --------------------
    def _build_basic_buttons(self):
        for i in range(6):
            self.basic_frame.grid_rowconfigure(i, weight=1)
        for j in range(5):
            self.basic_frame.grid_columnconfigure(j, weight=1)

        buttons = [
            ['7', '8', '9', '/','%'],
            ['4', '5', '6', '*','-'],
            ['1', '2', '3', '-','+'],
            ['0', '.', '=', '^','√'],
            ['(', ')','sin','cos','tan'],
            ['ln', 'π', 'e', 'Ans','log'],
            
        ]

        for r, row in enumerate(buttons):
            for c, text in enumerate(row):
                if text == '=':
                    cmd = self.calculate
                    bg = "#007acc"
                elif text in ('C', 'AC'):
                    cmd = self.clear_all
                    bg = "#d32f2f"
                else:
                    cmd = partial(self.add_to_expr, text)
                    bg = "#2d2d2d"
                btn = tk.Button(
                    self.basic_frame, text=text, command=cmd,
                    font=("Segoe UI", 14, "bold"), bg=bg, fg="white",
                    relief="flat", padx=3, pady=10
                )
                btn.grid(row=r, column=c, sticky="nsew", padx=2, pady=2)

    # -------------------- Scientific Tab --------------------
    def _build_scientific_buttons(self):
        
        groups = [
            ("Trigonometry", ["sin(", "cos(", "tan(", "asin(", "acos(", "atan("]),
            ("Hyperbolic", ["sinh(", "cosh(", "tanh(", "asinh(", "acosh(", "atanh("]),
            ("Log/Exp", ["ln(", "log(", "log10(", "log2(", "exp(", "10^("]),
            ("Power/Root", ["sqrt(", "cbrt(", "x²", "x³", "xʸ", "x^(1/y)"]),
            ("Constants", ["π", "e", "τ", "c", "h", "G"]),
            ("Combinatorics", ["fact(", "comb(", "perm(", "gcd(", "lcm(", "mod"]),
            ("Angle conv", ["deg->rad", "rad->deg", "deg->grad", "grad->deg"])
        ]

        row = 0
        for group_name, funcs in groups:
            lbl = tk.Label(self.sci_frame, text=f"── {group_name} ──",
                           font=("Segoe UI", 6, "bold"), bg="#121212", fg="#aaa")
            lbl.grid(row=row, column=0, columnspan=2, pady=(10, 2), sticky="w")
            row += 1
            for i, func in enumerate(funcs):
                r = row + i // 6
                c = i % 6
                cmd = partial(self._add_sci_func, func)
                btn = tk.Button(
                    self.sci_frame, text=func, command=cmd,
                    font=("Segoe UI", 8), bg="#2c2c2c", fg="white",
                    relief="flat", padx=6, pady=10
                )
                btn.grid(row=r, column=c, sticky="nsew", padx=2, pady=2)
            row += (len(funcs) + 5) // 6

        for j in range(6):
            self.sci_frame.grid_columnconfigure(j, weight=1)

    def _add_sci_func(self, func):
        mapping = {
            "x²": "^2", "x³": "^3", "xʸ": "^", "x^(1/y)": "^(1/",
            "10^(": "10^(",
            "π": "π", "e": "e", "τ": "τ", "c": "c", "h": "h", "G": "G",
            "deg->rad": "deg2rad(", "rad->deg": "rad2deg(",
            "deg->grad": "deg2grad(", "grad->deg": "grad2deg(",
            "fact(": "factorial(", "comb(": "comb(", "perm(": "perm(",
            "gcd(": "gcd(", "lcm(": "lcm(", "mod": "%"
        }
        if func in mapping:
            self.add_to_expr(mapping[func])
        else:
            self.add_to_expr(func)

    # -------------------- Converter Tab --------------------
    def _build_converter(self):
        main = ttk.Frame(self.converter_frame)
        main.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Label(main, text="Category:").grid(row=0, column=0, sticky="w", pady=5)
        self.conv_category = ttk.Combobox(main, values=["Length", "Mass", "Temperature", "Area", "Volume", "Speed", "Time"],
                                          state="readonly", width=20, font=("Segoe UI", 12))
        self.conv_category.grid(row=0, column=1, sticky="w", pady=5)
        self.conv_category.set("Length")
        self.conv_category.bind("<<ComboboxSelected>>", self._update_conv_units)

        ttk.Label(main, text="From:").grid(row=1, column=0, sticky="w", pady=5)
        self.conv_from = ttk.Combobox(main, state="readonly", width=20, font=("Segoe UI", 12))
        self.conv_from.grid(row=1, column=1, sticky="w", pady=5)

        ttk.Label(main, text="To:").grid(row=2, column=0, sticky="w", pady=5)
        self.conv_to = ttk.Combobox(main, state="readonly", width=20, font=("Segoe UI", 12))
        self.conv_to.grid(row=2, column=1, sticky="w", pady=5)

        ttk.Label(main, text="Value:").grid(row=3, column=0, sticky="w", pady=5)
        self.conv_value = tk.Entry(main, font=("Consolas", 14), bg="#2d2d2d", fg="white", width=20)
        self.conv_value.grid(row=3, column=1, sticky="w", pady=5)

        ttk.Button(main, text="Convert", command=self.convert_units).grid(row=4, column=0, columnspan=2, pady=10)

        self.conv_result_label = ttk.Label(main, text="Result: ", font=("Segoe UI", 14, "bold"), foreground="#00e5ff")
        self.conv_result_label.grid(row=5, column=0, columnspan=2, pady=10)

        self._init_conversion_data()
        self._update_conv_units()

    def _init_conversion_data(self):
        self.conv_factors = {
            "Length": {"Meters": 1, "Kilometers": 1000, "Centimeters": 0.01, "Millimeters": 0.001,
                       "Miles": 1609.344, "Feet": 0.3048, "Inches": 0.0254, "Yards": 0.9144},
            "Mass": {"Kilograms": 1, "Grams": 0.001, "Milligrams": 1e-6, "Pounds": 0.453592,
                     "Ounces": 0.0283495, "Tons": 1000},
            "Area": {"Square meters": 1, "Square kilometers": 1e6, "Square feet": 0.092903,
                     "Acres": 4046.86, "Hectares": 10000},
            "Volume": {"Liters": 1, "Milliliters": 0.001, "Gallons": 3.78541,
                       "Quarts": 0.946353, "Cups": 0.236588},
            "Speed": {"m/s": 1, "km/h": 0.277778, "mph": 0.44704, "knots": 0.514444},
            "Time": {"Seconds": 1, "Minutes": 60, "Hours": 3600, "Days": 86400}
        }
        self.temp_formulas = {
            ("Celsius", "Fahrenheit"): lambda c: c*9/5+32,
            ("Fahrenheit", "Celsius"): lambda f: (f-32)*5/9,
            ("Celsius", "Kelvin"): lambda c: c+273.15,
            ("Kelvin", "Celsius"): lambda k: k-273.15,
            ("Fahrenheit", "Kelvin"): lambda f: (f-32)*5/9+273.15,
            ("Kelvin", "Fahrenheit"): lambda k: (k-273.15)*9/5+32
        }

    def _update_conv_units(self, event=None):
        cat = self.conv_category.get()
        if cat == "Temperature":
            units = ["Celsius", "Fahrenheit", "Kelvin"]
        else:
            units = list(self.conv_factors[cat].keys())
        self.conv_from['values'] = units
        self.conv_to['values'] = units
        self.conv_from.set(units[0])
        self.conv_to.set(units[1] if len(units) > 1 else units[0])

    def convert_units(self):
        try:
            value = float(self.conv_value.get())
            cat = self.conv_category.get()
            from_u = self.conv_from.get()
            to_u = self.conv_to.get()
            if cat == "Temperature":
                key = (from_u, to_u)
                if key in self.temp_formulas:
                    result = self.temp_formulas[key](value)
                else:
                    rev = (to_u, from_u)
                    if rev in self.temp_formulas:
                        result = self.temp_formulas[rev](value)
                    else:
                        result = value
            else:
                result = value * self.conv_factors[cat][from_u] / self.conv_factors[cat][to_u]
            self.conv_result_label.config(text=f"Result: {result:.10g} {to_u}")
        except ValueError:
            messagebox.showerror("Error", "Invalid number")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # -------------------- Graph Tab --------------------
    def _build_graph(self):
        main = ttk.Frame(self.graph_frame)
        main.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Label(main, text="f(x) =", font=("Segoe UI", 12)).pack(anchor="w")
        self.func_entry = tk.Entry(main, font=("Consolas", 14), bg="#2d2d2d", fg="white")
        self.func_entry.pack(fill="x", pady=5)
        self.func_entry.insert(0, "x**2")

        range_frame = ttk.Frame(main)
        range_frame.pack(fill="x", pady=5)
        ttk.Label(range_frame, text="x min:").pack(side="left")
        self.xmin = tk.Entry(range_frame, width=8)
        self.xmin.insert(0, "-10")
        self.xmin.pack(side="left", padx=5)
        ttk.Label(range_frame, text="x max:").pack(side="left")
        self.xmax = tk.Entry(range_frame, width=8)
        self.xmax.insert(0, "10")
        self.xmax.pack(side="left", padx=5)
        ttk.Label(range_frame, text="points:").pack(side="left")
        self.points = tk.Entry(range_frame, width=6)
        self.points.insert(0, "200")
        self.points.pack(side="left", padx=5)

        ttk.Button(main, text="Plot", command=self.plot_func).pack(pady=10)

    def plot_func(self):
        if not MATPLOTLIB:
            messagebox.showinfo("Info", "Install matplotlib and numpy")
            return
        try:
            func_str = self.func_entry.get()
            xmin = float(self.xmin.get())
            xmax = float(self.xmax.get())
            pts = int(self.points.get())
            x = np.linspace(xmin, xmax, pts)
            ns = {'x': x, 'sin': np.sin, 'cos': np.cos, 'tan': np.tan,
                  'asin': np.arcsin, 'acos': np.arccos, 'atan': np.arctan,
                  'sinh': np.sinh, 'cosh': np.cosh, 'tanh': np.tanh,
                  'exp': np.exp, 'log': np.log, 'log10': np.log10, 'sqrt': np.sqrt,
                  'pi': np.pi, 'e': np.e}
            y = eval(func_str, {"__builtins__": {}}, ns)
            plt.figure(figsize=(6, 4))
            plt.plot(x, y, 'b-', linewidth=2)
            plt.grid(True)
            plt.title(f"f(x) = {func_str}")
            plt.xlabel("x")
            plt.ylabel("f(x)")
            plt.show()
        except Exception as e:
            messagebox.showerror("Plot Error", str(e))

    # -------------------- History Tab --------------------
    def _build_history_panel(self):
        btn_frame = tk.Frame(self.history_frame, bg="#121212")
        btn_frame.pack(fill="x", pady=5)
        tk.Button(btn_frame, text="Clear History", command=self.clear_history,
                  font=("Segoe UI", 12), bg="#5d4037", fg="white", relief="flat", padx=10, pady=8).pack(side="left", expand=True, fill="x", padx=5)
        tk.Button(btn_frame, text="Export", command=self.export_history,
                  font=("Segoe UI", 12), bg="#2c2c2c", fg="white", relief="flat", padx=10, pady=8).pack(side="left", expand=True, fill="x", padx=5)

        self.history_listbox = tk.Listbox(self.history_frame, font=("Consolas", 12),
                                          bg="#1e1e1e", fg="#00e5ff", selectbackground="#007acc")
        self.history_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        self.history_listbox.bind("<Double-Button-1>", self.on_history_select)

    # -------------------- Core Functions --------------------
    def add_to_expr(self, val):
        self.expression += str(val)
        self._refresh_display()

    def _refresh_display(self):
        self.display_var.set(self.expression)
        self.display.icursor(tk.END)

    def clear_all(self):
        self.expression = ""
        self._refresh_display()

    def clear_entry(self):
        self.expression = ""
        self._refresh_display()

    def delete(self):
        self.expression = self.expression[:-1]
        self._refresh_display()

    def insert_ans(self):
        self.add_to_expr(str(self.last_result))

    def toggle_angle_mode(self):
        modes = ["DEG", "RAD", "GRAD"]
        idx = modes.index(self.angle_mode)
        self.angle_mode = modes[(idx + 1) % 3]
        self.mode_btn.config(text=self.angle_mode)

    def mem_add(self):
        try:
            self.memory += float(self.display_var.get() or "0")
        except:
            pass
        self._update_memory_display()

    def mem_sub(self):
        try:
            self.memory -= float(self.display_var.get() or "0")
        except:
            pass
        self._update_memory_display()

    def mem_recall(self):
        self.add_to_expr(str(self.memory))

    def mem_clear(self):
        self.memory = 0.0
        self._update_memory_display()

    def _update_memory_display(self):
        self.memory_label.config(text=f"M={self.memory:.4g}")

    # Angle helpers
    def _to_radians(self, x):
        if self.angle_mode == "DEG":
            return math.radians(x)
        elif self.angle_mode == "GRAD":
            return x * math.pi / 200
        return x

    def _from_radians(self, x):
        if self.angle_mode == "DEG":
            return math.degrees(x)
        elif self.angle_mode == "GRAD":
            return x * 200 / math.pi
        return x

    def sin(self, x): return math.sin(self._to_radians(x))
    def cos(self, x): return math.cos(self._to_radians(x))
    def tan(self, x): return math.tan(self._to_radians(x))
    def asin(self, x): return self._from_radians(math.asin(x))
    def acos(self, x): return self._from_radians(math.acos(x))
    def atan(self, x): return self._from_radians(math.atan(x))

    # Evaluation
    def calculate(self):
        if not self.expression.strip():
            return
        expr = self.expression
        expr = expr.replace('^', '**')
        # Constants
        consts = {
            'π': math.pi, 'e': math.e, 'τ': 2*math.pi,
            'c': 299792458, 'h': 6.62607015e-34, 'G': 6.67430e-11
        }
        for name, val in consts.items():
            expr = expr.replace(name, str(val))

        def deg2rad(x): return math.radians(x)
        def rad2deg(x): return math.degrees(x)
        def deg2grad(x): return x * 200/180
        def grad2deg(x): return x * 180/200

        namespace = {
            'sin': self.sin, 'cos': self.cos, 'tan': self.tan,
            'asin': self.asin, 'acos': self.acos, 'atan': self.atan,
            'sinh': math.sinh, 'cosh': math.cosh, 'tanh': math.tanh,
            'asinh': math.asinh, 'acosh': math.acosh, 'atanh': math.atanh,
            'ln': math.log, 'log': math.log10, 'log10': math.log10,
            'log2': math.log2, 'exp': math.exp,
            'sqrt': math.sqrt, 'cbrt': lambda x: x**(1/3),
            'factorial': math.factorial, 'comb': math.comb, 'perm': math.perm,
            'gcd': math.gcd, 'lcm': math.lcm,
            'abs': abs, 'round': round,
            'deg2rad': deg2rad, 'rad2deg': rad2deg,
            'deg2grad': deg2grad, 'grad2deg': grad2deg,
            'ans': self.last_result
        }
        try:
            result = eval(expr, {"__builtins__": {}}, namespace)
            if isinstance(result, float):
                result = round(result, 12)
                if result == int(result):
                    result = int(result)
            # History
            timestamp = datetime.now().strftime("%H:%M:%S")
            hist_str = f"[{timestamp}] {self.expression} = {result}"
            self.history.append((self.expression, result))
            self.history_listbox.insert(tk.END, hist_str)
            self.history_listbox.see(tk.END)
            self.last_result = result
            self.expression = str(result)
            self._refresh_display()
        except ZeroDivisionError:
            messagebox.showerror("Error", "Division by zero")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # History
    def clear_history(self):
        self.history.clear()
        self.history_listbox.delete(0, tk.END)

    def export_history(self):
        if not self.history:
            messagebox.showinfo("Info", "No history")
            return
        filename = filedialog.asksaveasfilename(defaultextension=".txt")
        if filename:
            with open(filename, 'w') as f:
                for expr, res in self.history:
                    f.write(f"{expr} = {res}\n")
            messagebox.showinfo("Success", f"Saved to {filename}")

    def on_history_select(self, event):
        try:
            idx = self.history_listbox.curselection()[0]
            expr, _ = self.history[idx]
            self.expression = expr
            self._refresh_display()
        except:
            pass

    # Theme
    def toggle_theme(self):
        if self.theme == "dark":
            self.theme = "light"
            bg = "#f0f0f0"
            fg = "#000000"
            entry_bg = "#ffffff"
            entry_fg = "#000000"
            btn_bg = "#e0e0e0"
            self.theme_btn.config(text="☀️")
        else:
            self.theme = "dark"
            bg = "#121212"
            fg = "#ffffff"
            entry_bg = "#1e1e1e"
            entry_fg = "#00e5ff"
            btn_bg = "#2c2c2c"
            self.theme_btn.config(text="🌙")
        self.root.configure(bg=bg)
        self.display.config(bg=entry_bg, fg=entry_fg, readonlybackground=entry_bg)
        # Update all buttons (simplified: just change frame backgrounds)
        for frame in [self.basic_frame, self.sci_frame, self.history_frame, self.converter_frame]:
            for child in frame.winfo_children():
                if isinstance(child, tk.Button):
                    child.config(bg=btn_bg, fg=fg)
                elif isinstance(child, tk.Frame):
                    child.configure(bg=bg)
        # Update memory label and mode button
        self.memory_label.config(bg=bg, fg=fg)
        self.mode_btn.config(bg=btn_bg, fg=fg)
        # Update notebook tabs background (approximate)
        style = ttk.Style()
        style.configure("TNotebook", background=bg)

    # Responsive
    def on_resize(self, event):
        width = event.width
        if width < 400:
            btn_font = 14
        elif width < 600:
            btn_font = 16
        else:
            btn_font = 18
        # Only apply to basic tab buttons for simplicity
        for child in self.basic_frame.winfo_children():
            if isinstance(child, tk.Button):
                child.config(font=("Segoe UI", btn_font, "bold"))

    # Keyboard
    def _bind_keys(self):
        self.root.bind("<Return>", lambda e: self.calculate())
        self.root.bind("<Escape>", lambda e: self.clear_all())
        self.root.bind("<BackSpace>", lambda e: self.delete())
        self.root.bind("<Control-c>", lambda e: self.copy())
        self.root.bind("<Control-v>", lambda e: self.paste())

    def copy(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.display_var.get())

    def paste(self):
        try:
            text = self.root.clipboard_get()
            self.add_to_expr(text)
        except:
            pass


if __name__ == "__main__":
    root = tk.Tk()
    app = MobileCalculator(root)
    root.mainloop()