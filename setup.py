from setuptools import setup, find_packages

setup(
    name='tamdraw',
    version='0.3',
    packages=find_packages(),
    install_requires=[
        'xarray',
        'numpy',
        'matplotlib',
        'Pillow',
        'glob2',
        'cartopy',
        'scipy'
    ],
    author='y-tamura',
    description='Python package for plotting a figure created by ytamura. Most of functions are for geographical plotting.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/y-tamura/tamdraw',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
