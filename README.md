# ECG Signal Processing & Clinical Inference

Practical assessment submission for the Biostatistics / Bioinformatics Engineering 
Intern position at BioBuild. This repository contains the manual DSP pipeline used 
as a ground truth baseline to evaluate BioBuild's automated clinical inference 
capabilities on a 12-lead ECG record.

## Biological Question

Can an AI-driven bioinformatics platform reliably replicate a validated DSP workflow 
on a clinically complex ECG? The test case is record JS00001 from the CPSC 2021 
dataset, an 85-year-old male with Atrial Fibrillation (AFib) with Rapid Ventricular 
Response and Right Bundle Branch Block (RBBB).

## Pipeline Overview

Two-stage DSP chain implemented in Python using SciPy and wfdb:

- Bandpass filter: 4th-order Butterworth (0.5–45 Hz), zero-phase via filtfilt
- Notch filter: IIR (f꜀ = 50 Hz, Q = 35), manually set to the Chinese power-grid standard, not the US default of 60 Hz
- Peak detection: median RR-interval BPM (60 / median(RR)) with SDNN as an HRV metric, replacing an initial static threshold (0.5 × Vmax) that produced systematic Type II errors on low-amplitude AFib waveforms
- Verification: Welch's method PSD plots confirming >3 orders of magnitude attenuation at 50 Hz

## Setup
```bash
git clone https://github.com/su-huang/biobuild-assessment
cd biobuild-assessment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Data

This repository does not track the raw ECG data. Download record JS00001 from the CPSC 2021 dataset on PhysioNet and place JS00001.mat and JS00001.hea in the data/ directory:
https://physionet.org/content/ecg-arrhythmia/1.0.0/WFDBRecords/01/010/

## Usage
```bash
# Initial pipeline (static threshold)
python3 clean_data.py

# Refined pipeline with PSD verification
python3 improved_analysis.py
```

## Results

| Method | BPM | Notes |
|---|---|---|
| Static threshold | 48.0 | Type II error, misses low-amplitude peaks |
| Median RR (manual) | 102.7 | Robust to AFib irregularity |
| BioBuild autonomous | 106.8 | 1 peak plotted, visualization discrepancy |
| BioBuild guided | 111.1 | 8 peaks, consistent with clinical profile |

## Assessment Report

The full BioBuild evaluation report is available in the repository root as 
`Su Huang BioBuild Analysis Assessment.pdf`.

The following summarizes the analysis: 

| Metric | Manual Pipeline | BioBuild Autonomous | BioBuild Guided |
|---|---|---|---|
| Notch frequency | 50 Hz (manual) | 50 Hz (auto-inferred) | 50 Hz (auto-inferred) |
| Filter transparency | Full (Q, order, cutoffs) | Opaque | Partial (on request) |
| PSD verification | Default output | Not included | On request |
| BPM accuracy | 102.7 (median RR) | 106.8 (1 peak plotted) | 111.1 (8 peaks, robust) |
| Clinical inference | None | Full (SNOMED-CT) | Full (SNOMED-CT) |
| Audit trail | Complete | Absent | Partial |

