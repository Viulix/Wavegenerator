import mathfunctions as mf
import pyvisa
import time
import matplotlib.pyplot as plt
import numpy as np

# Global load time (in seconds) for waiting after sending the pulse.
rm = pyvisa.ResourceManager()
defaultProfile = "ROUVEN"
loadTimeSeconds = 7
triggerActive = False
# Dummy implementations for functions assumed to exist.
def sendAndSaveCustom(*args, **kwargs):
    print("sendAndSaveCustom called with", args, kwargs)
    
def prepareTrigger(frequency, maxVoltage):
    print("prepareTrigger called with frequency:", frequency, "maxVoltage:", maxVoltage)

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

def loadProfile(signal_type, amplitude, drop_amplitude, peaktime, droptime, delta_t, burst, ax, canvas):
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
    pulse = None
    maxVoltage = None

    if signal_type == "Square":
        # Generate the square pulse using the provided parameters.
        pulse = mf.generateSQUSQU(float(amplitude), float(drop_amplitude), peaktime, droptime, float(pulseWidth))
        frequency = (1 / (float(pulseWidth) + delta_t + 1)) * 10**3
        maxVoltage = max(abs(pulse))
        pulseDiff = mf.getPulseDifference(pulse, int(delta_t))
        normPulse = mf.normalizePulse(pulseDiff)
        datastring = ",".join(map(str, normPulse))
        print(datastring)
        sendAndSaveCustom("0," + datastring)
        time.sleep(loadTimeSeconds)
        # Update the embedded plot with the normalized pulse.
        updatePlot(ax, canvas, normPulse * maxVoltage, float(pulseWidth), "SQU")

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
        updatePlot(ax, canvas, None, float(pulseWidth))
        return

    # If burst mode is enabled, prepare the trigger.
    if burst:
        print("Preparing the trigger mode")
        print(amplitude + drop_amplitude)
        prepareTrigger(frequency, maxVoltage * 2)
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
    smu.write(f"BURS:NCYC {cycle_count}")
    smu.write(f"BURS:PHAS {start_phase}")
    smu.write("BURS:MODE TRIG")
    smu.write("TRIG:SOUR BUS")
    smu.write("BURS:STAT ON")
    smu.write(f"FREQ {frequency}")      # Setzt die Frequenz
    smu.write(f"VOLT {amplitude}")      # Setzt die Amplitude
    smu.write(f"VOLT:UNIT VPP")      # Setzt die Amplitude 
    smu.write(f"VOLT:OFFS {offset}")    # Setzt den DC-Offset
    smu.write(f"FUNC:USER {defaultProfile}")  # Wählt das USER-Wellenform-Profil aus
    smu.close()

def sendTrigger():
    """Sends a single external trigger. Only works in Burst-Mode"""
    if triggerActive:
        print("Sending trigger:")
        smu = rm.open_resource('ASRL6::INSTR')
        smu.write("*TRG")
        smu.close()
        time.sleep(0.1)
    else:
        print("No trigger profile has been prepared.")

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

def sendReset(durationSeconds:int, amplitude):
    smu = rm.open_resource('ASRL6::INSTR')
    smu.write(f"APPL:DC DEF, DEF, {amplitude}")
    time.sleep(durationSeconds)
    smu.write("BURS:MODE TRIG")
    smu.write("BURS:STAT ON")
    smu.write(f"FUNC:USER {defaultProfile}")  # Wählt das USER-Wellenform-Profil aus
    smu.close()