from .base import Misfit
import torch
import torch.nn.functional as F


class Misfit_M_SSIM(Misfit):
    def __init__(self, gaussian_sigmas=[0.75, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0],
                 data_range = 1.0,
                 K=(0.01, 0.03),
                 alpha=1,
                 ct=0,
                 compensation=1):
        super(Misfit_M_SSIM, self).__init__()
        self.C1 = (K[0] * data_range) ** 2
        self.C2 = (K[1] * data_range) ** 2
        self.ct = ct
        size = int(4 * gaussian_sigmas[-1] + 1)
        self.pad = int(size / 2 * gaussian_sigmas[-1])
        self.alpha = alpha
        self.compensation=compensation
        filter_size = int(size * gaussian_sigmas[-1] + 1)

        self.pad = int(2 * gaussian_sigmas[-1])
        filter_size = int(4 * gaussian_sigmas[-1] + 1)
        
        # Create the Gaussian masks for convolution
        g_masks = torch.zeros((len(gaussian_sigmas), 1, filter_size, filter_size))
        for idx, sigma in enumerate(gaussian_sigmas):
            g_masks[idx, 0, :, :] = self._fspecial_gauss_2d(filter_size, sigma)
        
        self.g_masks = g_masks

    def _fspecial_gauss_1d(self, size, sigma):
        """Create 1-D gauss kernel"""
        coords = torch.arange(size).to(dtype=torch.float)
        coords -= size // 2
        g = torch.exp(-(coords ** 2) / (2 * sigma ** 2))
        g /= g.sum()
        return g.reshape(-1)

    def _fspecial_gauss_2d(self, size, sigma):
        """Create 2-D gauss kernel"""
        gaussian_vec = self._fspecial_gauss_1d(size, sigma)
        return torch.outer(gaussian_vec, gaussian_vec)
    def mean_filter(self,x, window_size=3):
    	kernel = torch.ones(1, 1, window_size, window_size) / (window_size ** 2)
    	kernel = kernel.to(x.device)
    	return F.conv2d(x, kernel, padding=window_size//2)

    def forward(self, obs, syn):
        max_val = torch.max(torch.abs(syn), dim=1, keepdim=True).values
        max_val = torch.max(max_val, dim=2, keepdim=True).values
        syn = syn/(1e-20 + max_val)
        max_val = torch.max(torch.abs(obs), dim=1, keepdim=True).values
        max_val = torch.max(max_val, dim=2, keepdim=True).values
        obs = obs/(1e-20 + max_val)
        
        obs = self.alpha  * obs.unsqueeze(1) 
        syn = self.alpha  * syn.unsqueeze(1)      
      
        self.g_masks = self.g_masks.to(syn.device)
               
        # Apply 2D convolution with Gaussian kernels to get the necessary statistics
        mux = F.conv2d(obs, self.g_masks, groups=1, padding=self.pad)
        muy = F.conv2d(syn, self.g_masks, groups=1, padding=self.pad)

        mux2 = mux * mux
        muy2 = muy * muy
        muxy = mux * muy

        sigmax2 = F.conv2d(obs * obs, self.g_masks, groups=1, padding=self.pad) - mux2
        sigmay2 = F.conv2d(syn * syn, self.g_masks, groups=1, padding=self.pad) - muy2
        sigmaxy = F.conv2d(obs * syn, self.g_masks, groups=1, padding=self.pad) - muxy
        sigmax = torch.sqrt(torch.clamp(sigmax2, min=1e-10))
        sigmay = torch.sqrt(torch.clamp(sigmay2, min=1e-10))

        # l, c, s in MS-SSIM
        L  = (2 * muxy    + self.C1) / (mux2    + muy2    + self.C1) 
        contrast = self.ct * torch.sqrt(torch.clamp(sigmax2 * sigmay2, min=1e-20))
        C = (2 * sigmax * sigmay + self.C2) / (sigmax2 + sigmay2 + self.C2 + contrast)
        S = (2 * sigmaxy + self.C2) / (2 * sigmax * sigmay + self.C2)  
        T = L*C*S

        loss_ms_ssim = torch.mean(-T)
            
        # loss
        loss_mix = self.compensation * loss_ms_ssim
        return loss_mix.mean()