import wfdb
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, iirnotch, find_peaks
import os

# filter settings 
FS = 500.0          # sampling frequency
LOWCUT = 0.5        # remove baseline wander 
HIGHCUT = 45.0      # remove muscle noise 
NOTCH_FREQ = 50.0   # power line frequency 
Q = 30.0            # quality factor for notch

def butter_bandpass_filter(data, lowcut, highcut, fs, order=4):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    y = filtfilt(b, a, data)    # zero-phase filtering (no time shift)
    return y

def apply_notch(data, notch_f, fs, q):
    nyq = 0.5 * fs
    w0 = notch_f / nyq
    b, a = iirnotch(w0, q)
    y = filtfilt(b, a, data)
    return y

data_path = os.path.join('data', 'JS00001')
try:
    record = wfdb.rdrecord(data_path)
    raw_signal = record.p_signal[:2500, 0] 

    # remove baseline wander and high-frequency noise 
    bandpassed = butter_bandpass_filter(raw_signal, LOWCUT, HIGHCUT, FS)

    # remove power line noise
    cleaned_signal = apply_notch(bandpassed, NOTCH_FREQ, FS, Q)

    # r-peak detection 
    peaks, _ = find_peaks(cleaned_signal, distance=FS*0.6, height=np.max(cleaned_signal)*0.5)
    bpm = (len(peaks) / 5.0) * 60.0     # bpm based on 5 seconds of data

    # visualization
    plt.figure(figsize=(15, 10))

    # top plot: raw data 
    plt.subplot(2, 1, 1)
    plt.plot(raw_signal, color='blue', alpha=0.6)
    plt.title("BEFORE: Raw ECG with Baseline Wander and 50Hz Noise")
    plt.ylabel("Amplitude (mV)")
    plt.grid(True, linestyle='--', alpha=0.5)

    # bottom plot: cleaned data
    plt.subplot(2, 1, 2)
    plt.plot(cleaned_signal, color='green', label='Cleaned Signal')
    plt.plot(peaks, cleaned_signal[peaks], "x", color='red', label='Detected R-Peaks')
    plt.title(f"AFTER: Cleaned ECG (0.5-45Hz + 50Hz Notch) | Estimated BPM: {bpm:.1f}")
    plt.xlabel("Samples")
    plt.ylabel("Amplitude (mV)")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig('ecg_cleaning_results.png')
    print(f"cleaned plot saved. estimated heart rate: {bpm:.1f} bpm")

except Exception as e:
    print(f"Error: {e}")
