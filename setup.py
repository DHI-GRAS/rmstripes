from setuptools import setup, find_packages
import versioneer

setup(
    name='rmstripes',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    packages=find_packages(),
    author="Niklas Heim",
    author_email="nihe@dhigroup.com",
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
