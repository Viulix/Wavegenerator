import numpy as np
import matplotlib.pyplot as plt
import numpy as np

def generateSQUSQU(amplitude1, amplitude2, uptime, downtime, periodInMilliseconds=10, factor=1, returnArray=True):
    """
    Generates a square-like (step) waveform and extends its total length by repeating each point.
    
    The original waveform is built with 'periodInMilliseconds' points:
      - The first 'uptime' points have the value amplitude1.
      - The next 'downtime' points have the value -amplitude2.
      - The remaining points are 0.
    
    After generating the original signal, if a factor > 1 is specified, each point is repeated 
    'factor' times. This results in a waveform that is factor times longer, while preserving the 
    relative duration of each segment.
    
    Parameters:
      amplitude1 (float): Amplitude for the first segment.
      amplitude2 (float): Amplitude for the second segment (negative level).
      uptime (int): Number of points with amplitude1.
      downtime (int): Number of points with -amplitude2.
      periodInMilliseconds (int, optional): Number of points in the original waveform.
      factor (int, optional): Factor by which to extend the total number of points (each point is repeated).
      returnArray (bool, optional): If True, returns a NumPy array; otherwise, returns a comma-separated string.
    
    Returns:
      np.array or str: The extended waveform.
    """
    # Generate the original signal
    original_length = int(round(periodInMilliseconds))
    result = []
    for i in range(original_length):
        if 0 <= i < uptime:
            result.append(amplitude1)
        elif uptime <= i < (uptime + downtime):
            result.append(-amplitude2)
        else:
            result.append(0)
    
    # Convert to a NumPy array
    result = np.array(result, dtype=float)
    
    # Extend the signal by repeating each element 'factor' times if factor > 1
    if factor > 1:
        result = np.repeat(result, factor)
    
    # Return the waveform in the requested format
    if returnArray:
        return result
    else:
        return ",".join(map(str, result))

def dreieck_signal(amp_peak, amp_low, ratio, n_points):
    """
    Erzeugt ein Signal mit folgendem Verlauf:
      1. Anstieg von 0 auf amp_peak
      2. Direkter Übergang von amp_peak zu amp_low
      3. Rücklauf von amp_low zu 0
      
    Der Parameter ratio bestimmt den Anteil der Gesamtpunkte (abzüglich 2 fester Punkte für den Übergang)
    für den oberen Teil (0 -> Peak) gegenüber dem unteren Teil (Low -> 0).
    
    :param amp_peak: Amplitude des Peaks (Maximum)
    :param amp_low:  Amplitude des Tiefs (Minimum, z.B. negativ)
    :param ratio: Anteil der Punkte für den oberen Teil (0 < ratio < 1)
    :param n_points: Gesamtzahl der Punkte im Signal (mindestens 4)
    :return: NumPy-Array mit dem Signal
    """
    if n_points < 4:
        raise ValueError("n_points muss mindestens 4 sein.")
    
    # Fixer Anteil für den direkten Übergang von amp_peak zu amp_low:
    n_middle = 2  # Enthält amp_peak und amp_low
    n_remaining = n_points - n_middle
    
    # Punkteaufteilung für den oberen (0 -> amp_peak) und unteren (amp_low -> 0) Teil:
    n_upper = int(n_remaining * ratio)
    n_lower = n_remaining - n_upper
    
    # Sicherstellen, dass beide Segmente mindestens 1 Punkt enthalten:
    if n_upper < 1:
        n_upper = 1
        n_lower = n_remaining - 1
    if n_lower < 1:
        n_lower = 1
        n_upper = n_remaining - 1

    # Segment 1: von 0 bis amp_peak (n_upper+1 Punkte, inkl. Start und Peak)
    seg1 = np.linspace(0, amp_peak, n_upper+1, endpoint=True)
    # Segment 2: Übergang von amp_peak zu amp_low (n_middle Punkte, inkl. beider Endpunkte)
    seg2 = np.linspace(amp_peak, amp_low, n_middle, endpoint=True)
    # Segment 3: von amp_low zurück zu 0 (n_lower+1 Punkte, inkl. Low und Endpunkt)
    seg3 = np.linspace(amp_low, 0, n_lower+1, endpoint=True)
    
    # An den Übergängen würden sonst Punkte doppelt vorkommen.
    # Daher entfernen wir das erste Element von seg2 und seg3:
    signal = np.concatenate([seg1, seg2[1:], seg3[1:]])
    return signal

import numpy as np
import matplotlib.pyplot as plt

def neuron_action_potential(A, B, a, b, xa, xb, points=10000, start=0, end=7, plot=False):
    """
    Model for a neuronal spike. This model works with two differently shaped exponential that are superpositioned to achieve a good pulseform. 
    A, B: Amplitudes of the exponentials. A for spike, B for drop. NOTE: B is the actual amplitude of the drop. A is only barely the amplitude of the peak due to superposition.
    a, b: Stretch factor for each spike. a > 1 and b < 1 normally.
    xa, xb: Time shift for each pulse. Must be used and should not be the same.

    """
    x = np.linspace(start, end, points)
    firstExponential = A*np.exp(-.5*(10*a*x-xa)**2)
    secondExponential = B*np.exp(-(10*b*x-xb)**2)
    y = firstExponential + secondExponential
    if plot:
        plt.figure(figsize=(8, 4))
        plt.plot(x, y, label="Model View")
        plt.legend()
        plt.grid()
        plt.show()
    return y

# Simulation ausführen
# neuron_action_potential(10, -3, 2, .85, 3, 3, plot=True)



def getPulseDifferenceAsString(puls1, puls2, delta=0):
    """Generates the difference between two pulses as a string."""
    print(puls1)
    print(puls2)
    newPuls1 = [0] * delta + str.split(puls1, ",")
    newPuls2 = str.split(puls2, ",") + [0] * delta
    
    diffPuls = [0] # Add a zero in order to make the default value 0 V. This is required for burst mode!
    for i in range(len(newPuls1)):
        diffPuls.append((float(newPuls1[i]) - float(newPuls2[i])) / 2)

    resultString = ",".join(map(str, diffPuls))
    return resultString


def getPulseDifference(pulse, delta=0):
    """
    """
    pulse = np.asarray(pulse)  # Sicherstellen, dass pulse ein NumPy-Array ist
    original_length = len(pulse)
    new_length = original_length + abs(delta)  # Neue Länge nach Verschiebung

    if(delta==0):
        return np.zeros(original_length) 

    # Neues Array mit 0-Werten der passenden Größe erstellen
    extended_pulse = np.zeros(new_length)
    shifted_pulse = np.zeros(new_length)


    # Originalen Puls an den Anfang des neuen Arrays kopieren
    extended_pulse[:original_length] = pulse

    if delta > 0:
        # Rechtsverschiebung: Kopiere Pulse um delta nach rechts
        shifted_pulse[delta:original_length + delta] = pulse
    elif delta < 0:
        # Linksverschiebung: Kopiere Pulse um -delta nach links
        shifted_pulse[:original_length] = pulse[-delta:]  # Kürze vorne, falls nötig
    print(extended_pulse)
    print(shifted_pulse)
    return extended_pulse - shifted_pulse

def modelFunction(x, A, B, C):
    """Returns a hard coded function of x. Used for calculation purposes. Only change, if you want to change the plot."""
    f = A * np.exp(-.5 *(x-2.94)**2)- B*np.exp(-.02*(x-7.94)**2) + C*np.exp(-.02 * (x+4.06)**2)
    return f

def sendMathFunction(smu, datastr: str):
    """Sends a command to the wavegenerator"""

def normalize_and_format_function(func, sampleNumber: int, a, b):
    """Normalizies a function to provide values from -1 to 1. It calculates all values of func from a to b."""

    datastr = "0,"
    
    # Calculates values
    x_values = np.linspace(a, b, sampleNumber)  
    y_values = func(x_values)
    
    # Get min and max values
    min_value = np.min(y_values)
    max_value = np.max(y_values)

    maximumValue = np.max([abs(min_value), abs(max_value)])
    print(maximumValue)
    normalized_values = y_values / maximumValue
    
    # Create string for the wave generator
    for value in normalized_values:
        datastr += f"{value:.4f},"
    
    return datastr

def normalizePulse(pulse):
    """Finds the maximum value of the function and normalizes it based on this. Output will be a pulse with max = 1/-1"""
    pulse = np.array(pulse)
    print(pulse)
    max = np.max(pulse)
    min = np.min(pulse)
    print("Max:", [abs(min), abs(max)])
    maximumValue = np.max([abs(min), abs(max)])
    print(maximumValue)
    if maximumValue == 0: return pulse
    return  pulse / maximumValue

def createArbString(pulse, startValue=None):
    """
    Converts the desired output voltages into a normalized waveform string for the 33220A.
    The device expects the arbitrary waveform data to be in the range [-1, 1]. 
    The function calculates the amplitude (Vpp) and DC offset from the input pulse,
    then transforms the pulse so that when the waveform is scaled by these parameters,
    the output exactly matches the desired voltages.
    
    Additionally, if a startValue is provided, the first point in the normalized
    waveform is adjusted so that the first output voltage equals startValue.
    
    For a pulse [2, 0, -1]:
        - Amplitude (Vpp) = max - min = 2 - (-1) = 3 V
        - DC Offset = (max + min) / 2 = (2 + (-1)) / 2 = 0.5 V
        - Normalization is done using:
              normalized_value = (value - offset) / (amplitude/2)
          Thus normally, 2V maps to +1, 0V to -0.333333, and -1V to -1.
    
    If a startValue is provided (for example, 0V), the first normalized value is recalculated as:
          norm_first = (startValue - offset) / (amplitude/2)
    so that when scaled back:
          final_voltage = norm_first*(amplitude/2) + offset = startValue
    
    Parameters:
        pulse (list or array-like): The desired output voltages.
        startValue (float, optional): The desired voltage for the first point in the pulse.
                                      Must be within the range of the pulse.
    
    Returns:
        tuple: A tuple containing:
            - normalized_str (str): The normalized waveform as a comma-separated string.
            - amplitude (float): The calculated peak-to-peak amplitude.
            - offset (float): The calculated DC offset.
    """
    # Convert the input pulse to a numpy array of floats
    pulse = np.array(pulse, dtype=float)
    
    # Determine the minimum and maximum values in the pulse
    pulse_min = np.min(pulse)
    pulse_max = np.max(pulse)
    
    # Calculate the amplitude (Vpp) and DC offset
    amplitude = pulse_max - pulse_min
    offset = (pulse_max + pulse_min) / 2.0
    
    # Check for constant pulse (zero amplitude)
    if amplitude == 0:
        raise ValueError("Pulse has zero amplitude; cannot normalize.")
    
    # Normalize the pulse to the range [-1, 1] using the derived amplitude and offset
    norm_pulse = (pulse - offset) / (amplitude / 2)
    
    # If a startValue is provided, override the first normalized value.
    # Ensure that startValue is within the original pulse range.
    if startValue is not None:
        if not (pulse_min <= startValue <= pulse_max):
            raise ValueError("startValue must be within the range of the pulse values.")
        # Calculate the normalized value corresponding to the provided startValue.
        norm_start = (startValue - offset) / (amplitude / 2)
        norm_pulse[0] = norm_start
    
    # Format the normalized values as a comma-separated string (adjust precision as needed)
    normalized_str = ','.join(f'{x:.6f}' for x in norm_pulse)
    
    return normalized_str, amplitude, offset

