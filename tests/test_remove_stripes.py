import numpy as np
from rmstripes.stripes import remove_stripes


def test_remove_stripes():

    image = np.zeros([10, 10])
    image[:, 5] = 1.

    nostripes = remove_stripes(image, 4, 'haar', 10)

    assert np.allclose(nostripes, np.zeros(nostripes.shape), atol=0.1)
