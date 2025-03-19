import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# Import the functions from the separate file.
import wavefunctions as pf

def on_load_profile():
    """
    Converts all input values to their base units and calls loadProfile.
    Amplitudes are converted to Volts and time values to milliseconds.
    """
    try:
        amp = pf.safe_float(amplitude_entry.get(), "Amplitude")
        if amplitude_unit.get() == "mV":
            amp /= 1000.0
        
        drop_amp = pf.safe_float(drop_amplitude_entry.get(), "Drop Amplitude")
        if drop_amplitude_unit.get() == "mV":
            drop_amp /= 1000.0
        
        peak_time = pf.safe_float(peaktime_entry.get(), "Peaktime")
        if peaktime_unit.get() == "µs":
            peak_time /= 1000.0
        
        drop_time = pf.safe_float(droptime_entry.get(), "Droptime")
        if droptime_unit.get() == "µs":
            drop_time /= 1000.0
        
        delta_t = pf.safe_float(delta_t_entry.get(), "Delta t")
        if delta_t_unit.get() == "µs":
            delta_t /= 1000.0
        
        # Call loadProfile with the converted values and pass the UI's ax and canvas.
        pf.loadProfile(signal_var.get(), amp, drop_amp, peak_time, drop_time, delta_t,
                       burst_var.get(), ax, canvas)
    except Exception as e:
        messagebox.showerror("Error", f"Conversion error: {str(e)}")

def on_reset():
    """
    Asks for confirmation before sending an impulse that should "reset" the device.
    """
    if messagebox.askyesno("Confirmation", "Do you really want to execute Erase?"):
        duration = float(reset_duration_entry.get())
        amplitude = reset_amplitude_entry.get()
        pf.sendReset(durationSeconds=duration / 1000, amplitude=amplitude)
        print("Resetting device.")

# Global variable for output state: False = off, True = on.
output_state = False

def toggle_output():
    """
    Toggles the output state. Calls pf.turnOnOutput() when turning on and
    pf.turnOffOutput() when turning off. Also wechselt die Button-Farbe.
    """
    global output_state
    if not output_state:
        pf.turnOnOutput()
        output_state = True
        output_button.config(style="OutputOn.TButton")
    else:
        pf.turnOffOutput()
        output_state = False
        output_button.config(style="OutputOff.TButton")

# Create main window with increased size to accommodate the plot.
root = tk.Tk()
root.title("Signal Sender")
root.geometry("1100x500")
root.minsize(800, 500)
root.configure(bg="#f0f0f0")

# Set ttk style for a modern look.
style = ttk.Style(root)
style.theme_use("clam")
style.configure("TButton", font=("Arial", 12, "bold"))
style.configure("TLabel", font=("Arial", 12))
style.configure("TEntry", font=("Arial", 12))
style.configure("TCheckbutton", font=("Arial", 12))

# Custom button styles:
# "Send.TButton" has a distinct green color and "Reset.TButton" is red.
style.configure("Send.TButton", foreground="white", background="#4CAF50")
style.map("Send.TButton", background=[("active", "#45A049")])
style.configure("Reset.TButton", foreground="white", background="#f44336")
style.map("Reset.TButton", background=[("active", "#d32f2f")])
style.configure("Profile.TButton", foreground="white", background="#3464eb")
style.map("Profile.TButton", background=[("active", "#34cceb")])
# Zwei separate Stile für den Output-Button:
style.configure("OutputOn.TButton", foreground="white", background="#4CAF50")   # grün, wenn aktiv
style.map("OutputOn.TButton", background=[("active", "#45A049")])
style.configure("OutputOff.TButton", foreground="white", background="#f08a41")  # orange, wenn inaktiv
style.map("OutputOff.TButton", background=[("active", "#eb9659")])

# Create two main frames: one for controls and one for the plot.
control_frame = ttk.Frame(root, padding=(10, 10, 10, 10))
control_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

plot_frame = ttk.Frame(root, padding=(10, 10, 10, 10))
plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# Create the matplotlib Figure and embed it into the plot_frame.
fig = Figure(figsize=(5, 4), dpi=100)
ax = fig.add_subplot(111)
canvas = FigureCanvasTkAgg(fig, master=plot_frame)
canvas.draw()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

def add_labeled_entry(frame, label_text, row, unit_options=None, default_unit=None):
    """
    Adds a labeled entry field with an optional unit dropdown.
    
    Parameters:
      frame: The parent frame.
      label_text (str): The text for the label.
      row (int): The grid row.
      unit_options (list): List of unit options (e.g., ["ms", "µs"]).
      default_unit (str): Default selected unit.
      
    Returns:
      A tuple (entry_widget, unit_variable) or (entry_widget, None) if no unit options are provided.
    """
    label = ttk.Label(frame, text=label_text)
    label.grid(row=row, column=0, padx=5, pady=5, sticky="w")
    
    entry = ttk.Entry(frame)
    entry.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
    
    unit_var = None
    if unit_options:
        unit_var = tk.StringVar(value=default_unit if default_unit else unit_options[0])
        unit_dropdown = ttk.Combobox(frame, textvariable=unit_var,
                                     values=unit_options, state="readonly", width=5)
        unit_dropdown.grid(row=row, column=2, padx=5, pady=5, sticky="ew")
    return entry, unit_var

# --- UI Elements in the Control Frame ---

# Signal Type Dropdown (allowed profiles: "Square", "Triangle", "Model")
signal_var = tk.StringVar(value="Square")
ttk.Label(control_frame, text="Signal Type:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
signal_dropdown = ttk.Combobox(control_frame, textvariable=signal_var,
                               values=["Square", "Triangle", "Model"],
                               state="readonly")
signal_dropdown.grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky="ew")

# Entry fields with labels, default values, and unit selectors.
drop_amplitude_entry, drop_amplitude_unit = add_labeled_entry(control_frame, "Ref.  Amplitude:", 1, ["V", "mV"], "V")
drop_amplitude_entry.insert(0, "1")

amplitude_entry, amplitude_unit = add_labeled_entry(control_frame, "Spk. Amplitude:", 2, ["V", "mV"], "V")
amplitude_entry.insert(0, "2")

peaktime_entry, peaktime_unit = add_labeled_entry(control_frame, "Spike Time:", 3, ["ms", "µs"], "ms")
peaktime_entry.insert(0, "3")

droptime_entry, droptime_unit = add_labeled_entry(control_frame, "Ref. Time:", 4, ["ms", "µs"], "ms")
droptime_entry.insert(0, "7")

delta_t_entry, delta_t_unit = add_labeled_entry(control_frame, "Delta t:", 5, ["ms", "µs"], "ms")
delta_t_entry.insert(0, "1")

reset_amplitude_entry, reset_amplitude_unit = add_labeled_entry(control_frame, "Reset Amplitude:", 7, ["V", "mV"], "V")
reset_amplitude_entry.insert(0, "1")  # Standardwert

reset_duration_entry, reset_duration_unit = add_labeled_entry(control_frame, "Reset Duration:", 8, ["ms"], "ms")
reset_duration_entry.insert(0, "250")  # Standardwert

# Burst-Mode Checkbox.
burst_var = tk.BooleanVar(value=True)
burst_check = ttk.Checkbutton(control_frame, text="Burst-Mode", variable=burst_var)
burst_check.grid(row=10, column=0, columnspan=2, pady=5, sticky="w")

# Load Profile Button.
load_button = ttk.Button(control_frame, text="Load Profile", command=on_load_profile, style="Profile.TButton")
load_button.grid(row=10, column=2, padx=5, pady=6, sticky="ew")

# Send Button with custom green style.
send_button = ttk.Button(control_frame, text="Send Impuls", command=lambda: pf.sendTrigger(), style="Send.TButton")
send_button.grid(row=12, column=1, padx=5, pady=6, sticky="ew")

# Reset Button with custom red style.
reset_button = ttk.Button(control_frame, text="Reset Device", command=on_reset, style="Reset.TButton")
reset_button.grid(row=12, column=2, padx=5, pady=6, sticky="ew")

# Output Button: Startet im "aus"-Zustand (orange) und toggelt zwischen on/off.
output_button = ttk.Button(control_frame, text="Output", command=toggle_output, style="OutputOff.TButton")
output_button.grid(row=13, column=2, padx=5, pady=6, sticky="ew")

pf.turnOffOutput()

root.mainloop()
