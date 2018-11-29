import pathlib

import click
import numpy as np
import rasterio
import pywt
from scipy import interpolate

from rmstripes.fill_mask import fill_masked_values
from rmstripes.stripes import remove_stripes


WAVELETS = [wave for fam in pywt.families() for wave in pywt.wavelist(family=fam)]


@click.command(short_help='Removes stripes from a given band')
@click.argument('infile', type=pathlib.Path)
@click.option('--outfile', '-o', type=pathlib.Path, required=True)
@click.option('--wavelet', '-w', type=click.Choice(WAVELETS), default='db10',
              help='DWT wavelet name')
@click.option('--decomp-level', '-l', type=int, default=6,
              help='DWT decomposition level')
@click.option('--sigma', '-s', type=int, default=10,
              help='Sigma of Gaussian that is used for filtering FFT coefficients.')
@click.option('--band', '-b', type=int, default=1)
@click.option('--show-plots', is_flag=True)
def rmstripes(infile, outfile, wavelet, decomp_level, sigma, band, show_plots):
    """Remove stripes from an image by applying a wavelet-FFT approach as
    described in:

    Stripe and ring artifact removal with combined wavelet — Fourier filtering
        - Beat Münch, Pavel Trtik, Federica Marone, and Marco Stampanoni
    `https://www.osapublishing.org/oe/fulltext.cfm?uri=oe-17-10-8567&id=179485#ref11`

    Before the wavelet-FFT is applied masked values of the image are removed by
    interpolating missing values towards the closes valid pixel.
    """
    with np.errstate(invalid='ignore'):
        with rasterio.open(infile.as_posix(), 'r') as src:
            profile = src.profile.copy()
            image = src.read(band)

    click.echo('Removing stripes ...')
    no_stripes = remove_stripes(image, decomp_level, wavelet, sigma)

    profile.update({
        'dtype': no_stripes.dtype,
        'count': 1})
    with rasterio.open(outfile.as_posix(), 'w', **profile) as dst:
        dst.write(no_stripes, 1)

    if show_plots:
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(1, 2, sharex=True, sharey=True)
        ax[0].imshow(image, cmap='gray')
        ax[1].imshow(no_stripes, cmap='gray')
        plt.show()


@click.command(short_help='Interpolates masked values towards a constant')
@click.argument('infile', type=pathlib.Path)
@click.argument('maskfile', type=pathlib.Path)
@click.option('--outfile', '-o', type=pathlib.Path, required=True)
@click.option('--band', '-b', type=int, default=1)
@click.option('--constant', '-c', type=float, default=0,
              help='Masked values will be interpolated towards `constant`')
@click.option('--n-grow-mask', '-n', type=int, default=10,
              help='Number of steps before interpolation')
@click.option('--kernel-size', '-k', type=int, default=None,
              help='Kernel size that is used to fill missing values. '
              'Needs to be larger than n_grow_mask. Default: n_grow_mask + 5')
@click.option('--show-plots', is_flag=True)
def fill_mask_expand(infile, maskfile, outfile,
                     band, constant, n_grow_mask, kernel_size, show_plots):
    """Fill missing values in the input file by expanding the mask.
    The infile points to the geotiff that is to be filled and the maskfile
    points to a file of the same shape with zeros/ones for valid/invalid values.
    """
    if kernel_size is None:
        kernel_size = n_grow_mask + 5
    else:
        if kernel_size <= n_grow_mask:
            raise ValueError('kernel_size must be large than n_grow_mask')

    with np.errstate(invalid='ignore'):

        with rasterio.open(infile.as_posix(), 'r') as src:
            profile = src.profile.copy()
            image = src.read(band)

        with rasterio.open(maskfile.as_posix(), 'r') as src:
            mask = src.read(band)
            mask = mask == 1

            image[mask] = constant
            masked_image = np.ma.masked_array(image, mask)

    filled_image = fill_masked_values(
        masked_image, constant, n_grow_mask, kernel_size)

    profile.update({
        'dtype': filled_image.dtype,
        'count': 1})
    with rasterio.open(outfile.as_posix(), 'w', **profile) as dst:
        dst.write(filled_image, 1)

    if show_plots:
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(1, 2, sharex=True, sharey=True)
        ax[0].imshow(image, cmap='gray')
        ax[1].imshow(filled_image, cmap='gray')
        plt.show()


@click.command(
    short_help='Assigns the value of the nearest neighbour to masked values.')
@click.argument('infile', type=pathlib.Path)
@click.argument('maskfile', type=pathlib.Path)
@click.option('--outfile', '-o', type=pathlib.Path, required=True)
@click.option('--band', '-b', type=int, default=1)
@click.option('--show-plots', is_flag=True)
def fill_mask_nn(infile, maskfile, outfile, band, show_plots):
    """Fill in missing values in the input file with the nearest valid neighbor
    The infile points to the geotiff that is to be filled and the maskfile
    points to a file of the same shape with zeros/ones for valid/invalid values.
    """
    with np.errstate(invalid='ignore'):

        with rasterio.open(infile.as_posix(), 'r') as src:
            profile = src.profile.copy()
            image = src.read(band)

        with rasterio.open(maskfile.as_posix(), 'r') as src:
            mask = src.read(band)
            mask = mask == 1

    xi = np.argwhere(mask)
    points = np.argwhere(~mask)
    values = image[~mask]
    click.echo(f'Interpolating {xi.shape[0]} values ...')
    interp = interpolate.griddata(points, values, xi, method='nearest')

    new_image = image.copy()
    for val, (y, x) in zip(interp, xi):
        new_image[y, x] = val

    profile.update({
        'dtype': new_image.dtype,
        'count': 1})
    with rasterio.open(outfile.as_posix(), 'w', **profile) as dst:
        dst.write(new_image, 1)

    if show_plots:
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(1, 2, sharex=True, sharey=True)
        ax[0].imshow(image, cmap='gray')
        ax[1].imshow(new_image, cmap='gray')
        plt.show()
