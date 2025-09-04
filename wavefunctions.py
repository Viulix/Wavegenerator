import mathfunctions as mf
import pyvisa
import time
import numpy as np

# Global load time (in seconds) for waiting after sending the pulse.
rm = pyvisa.ResourceManager() # Global variable for the pyvisa resource manager
defaultProfile = "ROUVEN" # Default profile to store the custom waveform. We are only using one profile and overwrite it each time.
loadTimeSeconds = 6 # Time to wait after loading a profile
numberScaleFactor = 200 # Factor to scale the number of points in the waveform. 
usbPort = 6  # USB Port where the device is connected. Check in device manager. This value will be overwritten in the GUI.
pyvisaAdress = f"ASRL{usbPort}::INSTR" # global variable for the pyvisa adress of the connected device

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

def loadProfile(signal_type, spike_amplitude, ref_amplitude, spike_time, ref_time, delta_t, burst, singlePulse, ax, canvas):
    """
    Sends the pulse based on the provided parameters.
    Evaluates the signal type and performs different actions,
    then updates the embedded plot with the loaded pulse.
    
    Parameters:
      signal_type (str): The type of signal ("Square", "Triangle", "Model").
      spike_amplitude (float): Amplitude in Volts.
      ref_amplitude (float): Reference amplitude in Volts.
      spike_time (float): Peaktime in milliseconds.
      ref_time (float): Reference time in milliseconds.
      delta_t (float): Delta time in milliseconds.
      burst (bool): Whether burst mode is enabled.
      pulseWidth (float): Pulse width in milliseconds.
      ax (matplotlib.axes.Axes): The axes to update.
      canvas (FigureCanvasTkAgg): The canvas to redraw.
    """
    pulseWidth = spike_time + ref_time
    frequency = (1 / (float(spike_time + ref_time) + delta_t)) * 10**3
    amplitdueVpp = 1
    offset = 0
    pulse = None

    if signal_type == "Square":
        # Generate the square pulse using the provided parameters.
        pulse = mf.generateSQUSQU(float(spike_amplitude), float(ref_amplitude), spike_time, ref_time, float(pulseWidth), numberScaleFactor)

        # Check if the user want a difference-pulse or a single pulse
        if singlePulse:
            pulseDiff = pulse
            frequency = (1 / (float(spike_time + ref_time))) * 10**3
        else: pulseDiff = mf.getPulseDifference(pulse, int(delta_t)*numberScaleFactor)
        datastring, amplitdueVpp, offset = mf.createArbString(pulseDiff, 0)

        # Send the pulse to the device and wait for it to load.
        sendAndSaveCustom("0," + datastring) # The 0, is important to tell the device to start with 0V. This is the idle DC value in burst mode. The device will always return to this value after the pulse.
        time.sleep(loadTimeSeconds)

        # Update the embedded plot with the normalized pulse.
        updatePlot(ax, canvas, pulseDiff, float(pulseWidth), "SQU")
    
    else:
        print("Unknown type!")
        return

    # If burst mode is enabled, prepare the trigger. Important: Without burst mode the trigger won't work and the profiles may not be applied correctly.
    if burst:
        print("Preparing the trigger mode")
        prepareTrigger(frequency, amplitude=amplitdueVpp/2, offset=offset/2)
        time.sleep(3)
        global triggerActive
        triggerActive = True
        
    print("Profile has been loaded.")

def turnOnOutput():
    """Turns on the output of the generator without changing any settings."""
    smu = rm.open_resource(pyvisaAdress)
    smu.write("OUTP ON")

def turnOffOutput():
    """Turns off the output of the generator without changing any settings."""
    smu = rm.open_resource(pyvisaAdress)
    smu.write("OUTP OFF")

def sendAndSaveCustom(customDatastring):
    """Sends and applies a custome signal string - also stores the pulsform. Does not apply the profile directly."""
    smu = rm.open_resource(pyvisaAdress)
    smu.write(f"DATA VOLATILE, {customDatastring}") # Write arbitary waveform in volatile memory of the device
    smu.write(f"DATA:COPY {defaultProfile}, VOLATILE")  # Copy the waveform into a profile (here ARB3)
    smu.write(f"FUNC:USER {defaultProfile}")  # Activate the profile for the User Mode
    smu.close()

def prepareTrigger(frequency, amplitude, offset=0, cycle_count=1, start_phase=0):
    """Applies the default settings for the Burst-Mode and applies the mode."""
    smu = rm.open_resource(pyvisaAdress)
    smu.write(f"FREQ {frequency}")      # Set the frequency
    smu.write(f"VOLT {amplitude}")      # Set the amplitude
    smu.write(f"VOLT:UNIT VPP")      # Set the amplitude unit
    smu.write(f"VOLT:OFFS {offset}")    # Set the DC offset
    smu.write(f"FUNC:USER {defaultProfile}")  # Select the USER waveform profile
    smu.write(f"BURS:NCYC {cycle_count}") # Set the number of cycles
    smu.write(f"BURS:PHAS {start_phase}") # Set the start phase
    smu.write("BURS:MODE TRIG") # Set the burst mode to trigger
    smu.write("TRIG:SOUR BUS") # Set the source of the trigger (basically tell the device how we send the trigger)
    smu.write("BURS:STAT ON") # Turn on the burst mode
    smu.close()

def sendTrigger():
    """Sends a single external trigger. Only works in Burst-Mode"""
    print("Sending trigger:")
    smu = rm.open_resource(pyvisaAdress)
    smu.write("*TRG")
    smu.close()
    time.sleep(0.1)

# This function is not really used, because it won't work with impulses as it tries to apply it immediately. However, in trigger mode it is not possible. Might be useful for other applications.
def sendCustom(signal_str:str, frequency, amplitude, offset=0):
    """Sends and applies a custome signal string - also stores the pulsform."""
    smu = rm.open_resource(pyvisaAdress)
    smu.write(f"DATA VOLATILE, {signal_str}") # Write arbitary waveform in volatile memory of the device
    smu.write(f"DATA:COPY {defaultProfile}, VOLATILE")  # Copy the waveform into a profile (here ARB3)
    smu.write(f"FUNC:USER {defaultProfile}")  # Activate the profile for the User Mode
    smu.write(f"APPL:USER {frequency}, {amplitude}, {offset}") # Apply the profile with the given parameters -> would change the output immediately
    smu.close()

### NOTE: The save wasn't working properly if I remember correctly. Be careful if you are using it.
def sendReset(durationSeconds: int, amplitude: float):
    """Temporarily sets the generator to DC voltage for the specified time and amplitude,
    then restores the previous waveform without overwriting any user-defined profiles."""
    
    smu = rm.open_resource(pyvisaAdress)
    
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
