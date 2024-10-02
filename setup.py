from setuptools import find_packages, setup

setup(
    name='spidb',
    packages=find_packages(),
    version='0.1.0',
    description='Stored Product Insect Database (SPIDB)',
    author='Daniel Kadyrov',
    license='MIT',
    install_requires=[
        "sonic @ git+https://github.com/dkadyrov/sonic",
    ]
)