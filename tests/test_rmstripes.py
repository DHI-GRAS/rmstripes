import numpy as np
import rasterio
from click.testing import CliRunner

from rmstripes.scripts.cli import rmstripes


def create_stripe_file(infile):
    profile = {
        'count': 1,
        'height': 10,
        'width': 10,
        'dtype': 'float32',
        'driver': 'GTiff'}
    with rasterio.open(infile, 'w', **profile) as dst:
        image = np.zeros([10, 10], dtype=np.float32)
        image[:, 5] = 1.
        dst.write(image, 1)


def test_rmstripes(tmpdir):

    infile = tmpdir.join('infile.tif')
    outfile = tmpdir.join('outfile.tif')
    create_stripe_file(str(infile))

    runner = CliRunner()
    result = runner.invoke(rmstripes, [str(infile), '-o', str(outfile)])

    assert result.exit_code == 0
    assert outfile.exists()
