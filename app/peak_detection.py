from scipy.signal import find_peaks

def detect_peaks(absorbance):
    # Detecting local maxima (peaks)
    maxima, _ = find_peaks(absorbance,  distance=1)

    # Detecting local minima by inverting the absorbance signal
    inverted_absorbance = -absorbance
    minima, _ = find_peaks(inverted_absorbance,  distance=1)
    
    return maxima, minima
