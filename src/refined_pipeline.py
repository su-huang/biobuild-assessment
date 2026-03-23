import wfdb
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, iirnotch, find_peaks, welch
import os

# 1. Constants & Configuration
FS = 500.0
LOW_CUT = 0.5
HIGH_CUT = 45.0
Q = 35.0 # Narrower notch for better signal preservation

def calculate_snr(raw, clean):
    """Calculates Signal-to-Noise Ratio in dB."""
    noise = raw - clean
    p_signal = np.sum(clean**2)
    p_noise = np.sum(noise**2)
    return 10 * np.log10(p_signal / p_noise)

def get_clinical_notch(record_name):
    """Adaptive Notch selection based on dataset metadata."""
    # Example logic: JS records are CPSC2021 (China) -> 50Hz
    # If record starts with 'M' (MIT-BIH/USA) -> 60Hz
    return 50.0 if record_name.startswith('JS') else 60.0

# 2. Filtering Core
def apply_advanced_pipeline(signal, fs, notch_f):
    # Bandpass
    nyq = 0.5 * fs
    b, a = butter(4, [LOW_CUT/nyq, HIGH_CUT/nyq], btype='band')
    bandpassed = filtfilt(b, a, signal)
    
    # Notch
    b_n, a_n = iirnotch(notch_f/nyq, Q)
    cleaned = filtfilt(b_n, a_n, bandpassed)
    return cleaned

# 3. Execution
data_path = os.path.join('data', 'JS00001')
try:
    record = wfdb.rdrecord(data_path)
    # Using 10 seconds for better statistical significance
    raw_signal = record.p_signal[:, 0] 
    notch_f = get_clinical_notch(record.record_name)

    cleaned_signal = apply_advanced_pipeline(raw_signal, FS, notch_f)

    # Calculate Metrics
    snr_improvement = calculate_snr(raw_signal, cleaned_signal)
    
    # Robust Peak Detection (Distance-based for AFib)
    # distance=FS*0.4 allows for heart rates up to 150 BPM (relevant for this patient!)
    peaks, _ = find_peaks(cleaned_signal, distance=FS*0.4, height=np.mean(cleaned_signal) + np.std(cleaned_signal))
    
    # RR-Interval Analysis (Median is more robust to AFib outliers)
    rr_intervals = np.diff(peaks) / FS
    median_bpm = 60.0 / np.median(rr_intervals)
    sdnn = np.std(rr_intervals) * 1000 # Standard Deviation of Normal-to-Normal intervals

    # 4. Visualization & Logging
    print(f"--- Technical Validation: {record.record_name} ---")
    print(f"SNR Improvement: {snr_improvement:.2f} dB")
    print(f"Median Heart Rate: {median_bpm:.1f} BPM")
    print(f"SDNN (Heart Rate Variability): {sdnn:.1f} ms")

    plt.figure(figsize=(15, 12))
    
    # Time Domain Plot
    plt.subplot(2, 1, 1)
    plt.plot(raw_signal[:1500], label='Raw', alpha=0.4, color='blue')
    plt.plot(cleaned_signal[:1500], label='Filtered', color='green', linewidth=1.2)
    plt.plot(peaks[peaks < 1500], cleaned_signal[peaks[peaks < 1500]], "rx", label='R-Peaks')
    plt.title(f"ECG Analysis: {record.record_name} | BPM: {median_bpm:.1f} | SNR: {snr_improvement:.1f}dB")
    plt.legend()
    plt.grid(True, alpha=0.3)

    # Frequency Domain Plot (Power Spectral Density)
    plt.subplot(2, 1, 2)
    f_raw, p_raw = welch(raw_signal, FS, nperseg=1024)
    f_cln, p_cln = welch(cleaned_signal, FS, nperseg=1024)
    plt.semilogy(f_raw, p_raw, label='Raw Spectrum', alpha=0.5)
    plt.semilogy(f_cln, p_cln, label='Filtered Spectrum', color='green')
    plt.axvline(notch_f, color='red', linestyle='--', label=f'Notch ({notch_f}Hz)')
    plt.xlim(0, 100)
    plt.title("Power Spectral Density (PSD) - Verification of Noise Removal")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Power")
    plt.legend()

    plt.tight_layout()
    plt.savefig('improved_analysis.png')

except Exception as e:
    print(f"Processing Error: {e}")
