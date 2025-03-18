from scipy.signal import find_peaks

def detect_peaks(absorbance):
    maxima, _ = find_peaks(absorbance,  distance=1)

    inverted_absorbance = -absorbance
    minima, _ = find_peaks(inverted_absorbance,  distance=1)
    
    return maxima, minima
