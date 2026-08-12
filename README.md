# SSIM-FWI

**This repository provides the official implementation for the paper "SSIM-FWI: Full Waveform Inversion based on Multi-scale Structural Similarity Index Measure", accepted by *Geophysics*.**

---

## Overview

Full waveform inversion (FWI) is a high-resolution seismic inversion technique popularly used in oil and gas exploration. Traditional FWI employs the $L_2$ norm measurement to minimize the misfit between observed and predicted seismic data, which easily suffers from cycle skipping when background velocity is inaccurate or data lacks low-frequency components.

To address this issue, we introduce a **multi-scale structural similarity index measure (MS-SSIM)** objective function for FWI.

---

## Installation

This project relies on `deepwave`. 
