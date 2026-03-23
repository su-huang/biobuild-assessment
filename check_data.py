import wfdb
import matplotlib.pyplot as plt
import os

data_path = os.path.join('data', 'JS00001')

try:
    # rdrecord looks for both .hea and .mat in the specified path
    record = wfdb.rdrecord(data_path)
    
    # plot the first 1500 samples (3 seconds at 500Hz)
    plt.figure(figsize=(15, 5))
    plt.plot(record.p_signal[:1500, 0], color='blue', linewidth=1)
    
    plt.title(f"ECG Record: {record.record_name} | Sampling Rate: {record.fs}hz")
    plt.xlabel("Samples")
    plt.ylabel(f"Amplitude ({record.units[0]})")
    plt.grid(True, linestyle='--', alpha=0.7)
    
    print(f"successfully loaded {record.record_name} from the data/ folder.")
    print(f"sampling frequency: {record.fs} Hz")
    print(f"number of signals: {record.n_sig}")
    
    plt.savefig('ecg_plot.png')
    print("plot saved as ecg_plot.png")

except Exception as e:
    print(f"error: {e}")
    print("troubleshooting:")
    print("1. ensure JS00001.mat and JS00001.hea are both inside the 'data' folder.")
    print("2. check that your terminal is in 'biobuild-assessment' (type 'pwd').")
