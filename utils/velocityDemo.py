'''
* Author: LiuFeng(USTC) : liufeng2317@mail.ustc.edu.cn
* Date: 2023-12-10 20:30:00
* LastEditors: LiuFeng
* LastEditTime: 2024-05-20 11:22:22
* FilePath: /ADFWI/TorchInversion/demo.py
* Description: 
* Copyright (c) 2023 by ${liufeng2317} email: ${liufeng2317}, All Rights Reserved.
'''

import numpy as np 
import matplotlib.pyplot as plt
import os 
import obspy
import scipy.io
from scipy.interpolate import interp2d
from scipy.ndimage import gaussian_filter


def get_linear_vel_model(model, vp_min=None, vp_max=None, mask_depth = 15):
    """Generate a linear velocity model based on the input Marmousi model.

    Args:
        model (dict): The original Marmousi model containing velocity and density data.
        vp_min (float, optional): Minimum value for the primary wave velocity.
        vp_max (float, optional): Maximum value for the primary wave velocity.
        vs_min (float, optional): Minimum value for the shear wave velocity.
        vs_max (float, optional): Maximum value for the shear wave velocity.

    Returns:
        dict: A new model dictionary with linearly varying velocities and original density.
    """
    
    vp_true = model
    nz, nx = vp_true.shape
    vp = np.ones_like(vp_true)

    vp[:mask_depth, :] = vp_true[:mask_depth, :]
    
    # Determine velocity limits if not provided
    if vp_min is None and vp_max is None:
        vp_min, vp_max = np.min(vp_true[mask_depth:, :]), np.max(vp_true[mask_depth:, :])

    # Create linearly spaced values for velocities below the mask depth
    vp_line = np.linspace(vp_min, vp_max, nz - mask_depth).reshape(-1, 1)
    #vp_line = (vp_min + (vp_max - vp_min) * np.linspace(0, 1, nz - mask_depth) **1.5).reshape(-1, 1)
    vp[mask_depth:, :] *= vp_line
    
    return vp
