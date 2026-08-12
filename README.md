# SSIM-FWI

**This repository provides the official implementation for the paper "SSIM-FWI: Full Waveform Inversion based on Multi-scale Structural Similarity Index Measure", accepted by *Geophysics*.**

---

## Overview

Full waveform inversion (FWI) is a high-resolution seismic inversion technique popularly used in oil and gas exploration. Traditional FWI employs the $L_2$ norm measurement to minimize the misfit between observed and predicted seismic data, which easily suffers from cycle skipping when background velocity is inaccurate or data lacks low-frequency components.

To address this issue, we introduce a **multi-scale structural similarity index measure (M-SSIM)** objective function for FWI.

---

## Repository Structure

```text
.
├── FWI.ipynb             # Conventional FWI baseline implementation
├── EI-FWI.ipynb          # Envelope Inversion (EI-FWI) implementation
├── M-SSIM-FWI.ipynb      # Proposed Multi-scale SSIM-FWI method
├── misfit_test.ipynb     # Testing and validation script for objective functions
├── misfit/               # Modules containing different objective function definitions
├── utils/                # Utility functions
├── True.mat              # True velocity model data
└── wavelet.mat           # Source wavelet data
