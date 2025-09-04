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

def getPulseDifference(pulse, delta=0):
    """
    Generates the difference between a pulse and a shifted version of itself.

    Parameters:
        pulse (list or np.ndarray): The input pulse waveform.
        delta (int, optional): The number of points to shift the pulse.
            - If delta > 0: shifts the pulse to the right by 'delta' points.
            - If delta < 0: shifts the pulse to the left by 'abs(delta)' points.
            - If delta == 0: returns an array of zeros with the same length as the input pulse.

    Returns:
        np.ndarray: The difference between the original and shifted pulse.
    """
    pulse = np.asarray(pulse)  # Ensure pulse is a NumPy array
    original_length = len(pulse)
    new_length = original_length + abs(delta)  # New length after shifting

    if delta == 0:
        return np.zeros(original_length)

    # Create new arrays filled with zeros of the appropriate size
    extended_pulse = np.zeros(new_length)
    shifted_pulse = np.zeros(new_length)

    # Copy the original pulse to the beginning of the new array
    extended_pulse[:original_length] = pulse

    if delta > 0:
        # Right shift: copy pulse 'delta' points to the right
        shifted_pulse[delta:original_length + delta] = pulse
    elif delta < 0:
        # Left shift: copy pulse 'abs(delta)' points to the left
        shifted_pulse[:original_length] = pulse[-delta:]  # Trim from the front if needed

    return extended_pulse - shifted_pulse

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

