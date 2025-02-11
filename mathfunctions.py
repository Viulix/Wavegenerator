import numpy as np
import matplotlib.pyplot as plt
def generateSQUSQU(amplitude1, amplitude2, uptime, downtime, periodInMilliseconds=10, returnArray=True):
    """Generates the Square-Square waveform as string."""
    result = [] 

    for i in range(int(round(periodInMilliseconds))):
        if 0 <= i < uptime:
            result.append(amplitude1)
        elif uptime <= i < downtime + uptime:
            result.append(-amplitude2)
        else: result.append(0)
    if returnArray: return  np.array(result)
    resultString = ",".join(map(str, result))
    return resultString



def getPulseDifferenceAsString(puls1, puls2, delta=0):
    """Generates the difference between two pulses as a string."""
    newPuls1 = [0] * delta + str.split(puls1, ",")
    newPuls2 = str.split(puls2, ",") + [0] * delta
    
    diffPuls = [0] # Add a zero in order to make the default value 0 V. This is required for burst mode!
    for i in range(len(newPuls1)):
        diffPuls.append((float(newPuls1[i]) - float(newPuls2[i])) / 2)

    resultString = ",".join(map(str, diffPuls))
    return resultString


def getPulseDifference(pulse, delta=0):
    """
    Berechnet die Differenz zwischen einem Puls und einem um delta verschobenen Puls.
    Der verschobene Puls wird mit 0 erweitert, sodass das Ergebnis die korrekte Länge hat.
    
    Parameter:
    - pulse: NumPy-Array, das den ursprünglichen Puls enthält.
    - delta: Ganzzahl, die die Verschiebung des zweiten Pulses bestimmt
             (positiv = nach rechts, negativ = nach links).
    
    Rückgabe:
    - NumPy-Array mit der differenzierten Pulsfolge.
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

    return extended_pulse - shifted_pulse

def modelFunction(x):
    """Returns a hard coded function of x. Used for calculation purposes. Only change, if you want to change the plot."""
    f = 20 * np.exp(.1 * np.log(abs(x)) - (x)**2)- 2*np.exp(-.02*(x)**2)
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

    normalized_values = y_values / maximumValue
    
    # Create string for the wave generator
    for value in normalized_values:
        datastr += f"{value:.4f},"
    
    return datastr

def normalizePulse(pulse):
    """Finds the maximum value of the function and normalizes it based on this. Output will be a pulse with max = 1/-1"""
    pulse = np.array(pulse)
    max = np.max(pulse)
    min = np.min(pulse)

    maximumValue = np.max([abs(min), abs(max)])
    if maximumValue == 0: return pulse
    return  pulse / maximumValue
