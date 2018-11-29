import numpy as np
import scipy.ndimage
from tqdm import tqdm


def grow_mask_count(mask, n_grow):
    structure = scipy.ndimage.generate_binary_structure(2, 2)
    grow_count = np.zeros(mask.shape, int)
    mask_new = mask.copy()
    for _ in range(n_grow):
        mask_new = scipy.ndimage.binary_dilation(mask_new, structure=structure)
        grow_count += (mask_new & ~mask).astype(int)
        mask_grow = grow_count > 0
    return mask_grow, grow_count


def fill_masked_values(masked_image, constant, n_grow, kernel_size):
    grown_mask, grown_count = grow_mask_count(~masked_image.mask, n_grow=n_grow)

    masked_image[~grown_mask & masked_image.mask] = constant

    filled_image = masked_image.copy()
    jjmask, iimask = np.where(grown_mask)

    jjmask, iimask = np.array(list(jjmask)), np.array(list(iimask))
    ystart, xstart = np.maximum(0, jjmask - kernel_size), np.maximum(0, iimask - kernel_size)
    yend, xend = jjmask + kernel_size, iimask + kernel_size

    for kk in tqdm(range(jjmask.shape[0]), total=jjmask.shape[0]):
        jj, ii = jjmask[kk], iimask[kk]
        val = masked_image[ystart[kk]:yend[kk], xstart[kk]:xend[kk]].mean()
        filled_image[jj, ii] = constant + (val - constant) / (n_grow) * grown_count[jj, ii]

    assert not np.any(filled_image.mask)
    return filled_image.data
