import mathfunctions as mf
import pyvisa
import time
import matplotlib.pyplot as plt
import numpy as np

# Global load time (in seconds) for waiting after sending the pulse.
rm = pyvisa.ResourceManager()
defaultProfile = "ROUVEN"
loadTimeSeconds = 6
numberScaleFactor = 200

def safe_float(value_str, field_name="Value"):
    """
    Converts the given string to a float.
    Raises an error if the conversion fails.
    """
    try:
        return float(value_str)
    except ValueError:
        raise ValueError(f"{field_name} must be a number.")

def updatePlot(ax, canvas, pulse, pulseWidth, type="DEF"):
    """
    Updates the embedded plot showing the loaded pulse.
    
    Parameters:
      ax (matplotlib.axes.Axes): The axes to update.
      canvas (FigureCanvasTkAgg): The canvas to redraw.
      pulse (list or array of floats): The pulse amplitude values.
      pulseWidth (float): The pulse width in milliseconds.
    """
    ax.clear()
    if pulse is not None:
        # Create a time axis assuming the pulse spans the entire pulseWidth.
        N = len(pulse)
        time_axis = np.linspace(0, pulseWidth, N)
        if type == "SQU":
            if len(time_axis) == len(pulse):
                time_axis = np.append(time_axis, time_axis[-1] + (time_axis[-1] - time_axis[-2]))

            ax.stairs(pulse, time_axis, label="Pulse", linewidth=2)  # Reihenfolge beachten: `values, edges`
            ax.set_xlabel("Time [ms]")
            ax.set_ylabel("Amplitude [V]")
            ax.set_title("Loaded Pulse")
            ax.legend()
            ax.grid(True)

        else:
            ax.plot(time_axis, pulse, label="Pulse")
            ax.set_xlabel("Time (ms)")
            ax.set_ylabel("Amplitude (V)")
            ax.set_title("Loaded Pulse")
            ax.legend()
    else:
        ax.text(0.5, 0.5, "No pulse available", horizontalalignment='center',
                verticalalignment='center', transform=ax.transAxes)
        ax.set_title("Loaded Pulse")
    canvas.draw()

def loadProfile(signal_type, amplitude, drop_amplitude, peaktime, droptime, delta_t, burst, singlePulse, ax, canvas):
    """
    Sends the pulse based on the provided parameters.
    Evaluates the signal type and performs different actions,
    then updates the embedded plot with the loaded pulse.
    
    Parameters:
      signal_type (str): The type of signal ("Square", "Triangle", "Model").
      amplitude (float): Amplitude in Volts.
      drop_amplitude (float): Drop amplitude in Volts.
      peaktime (float): Peaktime in milliseconds.
      droptime (float): Droptime in milliseconds.
      delta_t (float): Delta time in milliseconds.
      burst (bool): Whether burst mode is enabled.
      pulseWidth (float): Pulse width in milliseconds.
      ax (matplotlib.axes.Axes): The axes to update.
      canvas (FigureCanvasTkAgg): The canvas to redraw.
    """
    pulseWidth = peaktime + droptime
    frequency = (1 / (float(peaktime + droptime) + delta_t)) * 10**3
    amplitdueVpp = 1
    offset = 0
    pulse = None
    maxVoltage = None

    if signal_type == "Square":
        # Generate the square pulse using the provided parameters.
        pulse = mf.generateSQUSQU(float(amplitude), float(drop_amplitude), peaktime, droptime, float(pulseWidth), numberScaleFactor)
        # Check if the user want a  difference-pulse or a single pulse
        if singlePulse:
            pulseDiff = pulse
            frequency = (1 / (float(peaktime + droptime))) * 10**3
        else: pulseDiff = mf.getPulseDifference(pulse, int(delta_t)*numberScaleFactor)
        datastring, amplitdueVpp, offset = mf.createArbString(pulseDiff, 0)

        sendAndSaveCustom(datastring)
        time.sleep(loadTimeSeconds)
        # Update the embedded plot with the normalized pulse.
        updatePlot(ax, canvas, pulseDiff, float(pulseWidth), "SQU")

    elif signal_type == "Triangle":
        print("Action: TRIANGLE is executed (e.g., triangular pulse in both phases).")
        # For demonstration, generate a dummy triangular pulse.
        N = 100  # number of points for half the pulse
        rising = np.linspace(0, 1, N)
        falling = np.linspace(1, 0, N)
        pulse = np.concatenate((rising, falling))
        updatePlot(ax, canvas, pulse, float(pulseWidth))
        
    elif signal_type == "Model":
        x_values = np.linspace(0, 20, 1000)  # Define an appropriate range
        pulse = mf.modelFunction(x_values, amplitude, drop_amplitude, 0.05)  # Compute y-values
        nom_pulse = mf.normalizePulse(pulse)
        datastring = ",".join(map(lambda x: f"{x:.3f}", nom_pulse))
        maxVoltage = max(abs(pulse))
       # print(datastring)
        sendAndSaveCustom("0," + datastring)
        time.sleep(loadTimeSeconds)
        updatePlot(ax, canvas, pulse, float(pulseWidth))
    
    else:
        print("Unknown type!")
        return

    # If burst mode is enabled, prepare the trigger.
    if burst:
        print("Preparing the trigger mode")
        prepareTrigger(frequency, amplitude=amplitdueVpp/2, offset=offset/2)
        time.sleep(3)
        global triggerActive
        triggerActive = True
        
    print("Profile has been loaded.")

def turnOnOutput():
    smu = rm.open_resource('ASRL6::INSTR')
    smu.write("OUTP ON")

def turnOffOutput():
    smu = rm.open_resource('ASRL6::INSTR')
    smu.write("OUTP OFF")

def sendAndSaveCustom(customDatastring):
    smu = rm.open_resource('ASRL6::INSTR')
    smu.write(f"DATA VOLATILE, {customDatastring}") # Write arbitary waveform in volatile memory of the device
    smu.write(f"DATA:COPY {defaultProfile}, VOLATILE")  # Copy the waveform into a profile (here ARB3)
    smu.write(f"FUNC:USER {defaultProfile}")  # Activate the profile for the User Mode
    smu.close()

def prepareTrigger(frequency, amplitude, offset=0, cycle_count=1, start_phase=0):
    """Applies the default settings for the Burst-Mode and applies the mode."""
    smu = rm.open_resource('ASRL6::INSTR')
    smu.write(f"FREQ {frequency}")      # Setzt die Frequenz
    smu.write(f"VOLT {amplitude}")      # Setzt die Amplitude
    smu.write(f"VOLT:UNIT VPP")      # Setzt die Amplitude 
    smu.write(f"VOLT:OFFS {offset}")    # Setzt den DC-Offset
    smu.write(f"FUNC:USER {defaultProfile}")  # Wählt das USER-Wellenform-Profil aus
    smu.write(f"BURS:NCYC {cycle_count}")
    smu.write(f"BURS:PHAS {start_phase}")
    smu.write("BURS:MODE TRIG")
    smu.write("TRIG:SOUR BUS")
    smu.write("BURS:STAT ON")
    smu.close()

def sendTrigger():
    """Sends a single external trigger. Only works in Burst-Mode"""
    print("Sending trigger:")
    smu = rm.open_resource('ASRL6::INSTR')
    smu.write("*TRG")
    smu.close()
    time.sleep(0.1)

def sendCustom(signal_str:str, frequency, amplitude, offset=0):
    """Sends and applies a custome signal string - also stores the pulsform."""
    smu = rm.open_resource('ASRL6::INSTR')
    smu.write(f"DATA VOLATILE, {signal_str}") # Write arbitary waveform in volatile memory of the device
    smu.write(f"DATA:COPY {defaultProfile}, VOLATILE")  # Copy the waveform into a profile (here ARB3)
    smu.write(f"FUNC:USER {defaultProfile}")  # Activate the profile for the User Mode
    smu.write(f"APPL:USER {frequency}, {amplitude}, {offset}") # Activate Profile
    smu.close()

def writeAndSaveCustom(signal_str:str):
    """Send a custom signal string and load it into a profile of the generator. Does not apply the profile."""
    smu = rm.open_resource('ASRL6::INSTR')
    smu.write(f"DATA VOLATILE, {signal_str}") # Write arbitary waveform in volatile memory of the device
    smu.write(f"DATA:COPY {defaultProfile}, VOLATILE")  # Copy the waveform into a profile (here ARB3)
    smu.write(f"FUNC:USER {defaultProfile}")  # Activate the profile for the User Mode
    smu.close()

def sendReset(durationSeconds: int, amplitude: float):
    """Temporarily sets the generator to DC voltage for the specified time and amplitude,
    then restores the previous waveform without overwriting any user-defined profiles."""
    
    smu = rm.open_resource('ASRL6::INSTR')
    
    try:
        # Speichere den aktuellen Zustand
        previous_function = smu.query("FUNC?").strip()  # Aktuelle Wellenform
        previous_amplitude = smu.query("VOLT?").strip()  # Aktuelle Amplitude
        previous_offset = smu.query("VOLT:OFFS?").strip()  # Aktueller Offset
        
        # Setze DC-Spannung mit gewünschter Amplitude
        smu.write("FUNC DC")  # Setzt DC-Modus
        smu.write(f"VOLT:OFFS {float(amplitude)/2}")  # Setzt den Offset auf die gewünschte DC-Spannung
        
        time.sleep(durationSeconds)  # Wartezeit für die DC-Phase
        
        # Kehre zum vorherigen Zustand zurück
        smu.write(f"FUNC {previous_function}")  # Setzt die vorherige Wellenform
        smu.write(f"VOLT {previous_amplitude}")  # Stellt die vorherige Amplitude wieder her
        smu.write(f"VOLT:OFFS {previous_offset}")  # Stellt den vorherigen Offset wieder her
        smu.write("BURS:STAT ON")

    finally:
        smu.close()
