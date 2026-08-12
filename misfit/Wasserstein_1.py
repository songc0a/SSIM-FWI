import numpy as np
import torch
from .base import Misfit
from typing import Optional

"""
    Wasserstein distance (W1 Loss)
        https://github.com/YangFangShu/FWIGAN/blob/main/FWIGAN/utils/misfit.py
"""
    
def transform(f, g, trans_type, theta):
    """
        do the transform for the signal f and g
        Args:
            f, g: seismic data with the shape [num_time_steps,num_shots*num_receivers_per_shot]
            trans_type: type for transform
            theta:the scalar variable for transform            
        return:
            output with transfomation
    """ 
    c = 0.0 
    device = f.device
    if trans_type == 'linear':
        min_value = torch.min(f.detach().min(), g.detach().min())
        mu, nu = f, g
        c = -min_value if min_value<0 else 0
        c = c * theta
        d = torch.ones(f.shape).to(device)
    elif trans_type == 'abs':
        mu, nu = torch.abs(f), torch.abs(g)
        d = torch.sign(f).to(device)
    elif trans_type == 'square':
        mu = f * f
        nu = g * g
        d = 2 * f
    elif trans_type == 'exp':
        mu = torch.exp(theta*f)
        nu = torch.exp(theta*g)
        d = theta * mu
    elif trans_type == 'softplus':
        mu = torch.log(torch.exp(theta*f) + 1.01)
        nu = torch.log(torch.exp(theta*g) + 1.01)
        d = theta / torch.exp(-theta*f)

    elif trans_type == 'sigmoid':
    	mu = torch.sigmoid(f)
    	nu = torch.sigmoid(g)
    	d = torch.ones(f.shape).to(device)
    else:
        mu, nu = f, g
        d = torch.ones(f.shape).to(device)
    mu = mu + c + 1e-18 
    nu = nu + c + 1e-18
    return mu, nu, d

def trace_sum_normalize(x,time_dim=1):
    """
        normalization with the summation of each trace
        note that the channel should be 1
    """
    x = x / (x.sum(dim=time_dim,keepdim=True)+1e-18)
    return x

class Misfit_Wasserstein1(Misfit):
    def __init__(self,trans_type='linear',theta=1,dt=1) -> None:
        """
            trans_type: linear, abs, square, exp, softplus, envelope
        """
        super().__init__()
        self.trans_type = trans_type
        self.theta = theta
        self.dt     = dt
        
    def forward(self,syn:torch.Tensor,obs:torch.Tensor):
        assert syn.shape == obs.shape
        # max_value = torch.max(syn.max(), obs.max())
        # obs = obs / max_value
        # syn = syn / max_value
        mu, nu, d = transform(syn, obs, self.trans_type, self.theta)
        assert mu.min() > 0
        assert nu.min() > 0
        # mu = mu.permute(1, 0, 2)  ## t,s,r
        # nu = nu.permute(1, 0, 2)  ## t,s,r
        # t,s,r = mu.shape
        # mu = mu.reshape(t,s*r)
        # nu = nu.reshape(t,s*r)
        
        mu = trace_sum_normalize(mu,time_dim=1)
        nu = trace_sum_normalize(nu,time_dim=1)

        F = torch.cumsum(mu, dim=1)
        G = torch.cumsum(nu, dim=1)
        
        rsd = F-G
        w1loss = 1e0 * (torch.abs(rsd*self.dt)).sum()

        
        return w1loss
