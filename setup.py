from setuptools import setup, find_packages

setup(
    name='rmstripes',
    version=0.1,
    packages=find_packages(),
    install_requires=[
        'click',
        'matplotlib',
        'numpy',
        'pywavelets',
        'rasterio',
        'scipy',
        'tqdm',
    ],
    entry_points='''
        [console_scripts]
        rmstripes=rmstripes.scripts.cli:rmstripes
        fill-mask-expand=rmstripes.scripts.cli:fill_mask_expand
        fill-mask-nn=rmstripes.scripts.cli:fill_mask_nn
    ''',
)
