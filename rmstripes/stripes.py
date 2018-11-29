import numpy as np
import pywt


def damp_coefficient(coeff, sigma):
    """Filter DWT coefficients by performing an FFT and applying a Gaussian
    kernel.
    """
    fft_coeff = np.fft.fft(coeff, axis=0)
    fft_coeff = np.fft.fftshift(fft_coeff, axes=[0])

    ydim, _ = fft_coeff.shape
    gauss1d = 1 - np.exp(-np.arange(-ydim // 2, ydim // 2)**2 / (2 * sigma**2))
    damped_fc = fft_coeff * gauss1d[:, np.newaxis]

    damped_coeff = np.fft.ifftshift(damped_fc, axes=[0])
    damped_coeff = np.fft.ifft(damped_coeff, axis=0)
    return damped_coeff.real


def remove_stripes(image, decomp_level, wavelet, sigma):
    """Removes stripes from `image` with a combined wavelet/FFT approach.

    Params
    ------
    image : 2d array
        containing the stripy image
    decomp_level : int
        Decomposition level of DWT (TODO: could be automatically calculated?)
    wavelet : str
        name of wavelet to use for DWT
    sigma : int
        sigma of Gaussian that is used to smooth FFT coefficients
    """
    coeffs = pywt.wavedec2(
        image, wavelet=wavelet, level=decomp_level, mode='symmetric')

    damped_coeffs = [coeffs[0]]

    for ii in range(1, len(coeffs)):
        ch, cv, cd = coeffs[ii]

        cv = damp_coefficient(cv, sigma)
        ch = damp_coefficient(ch, sigma)

        damped_coeffs.append((ch, cv, cd))

    rec_image = pywt.waverec2(damped_coeffs, wavelet=wavelet, mode='symmetric')
    return rec_image
