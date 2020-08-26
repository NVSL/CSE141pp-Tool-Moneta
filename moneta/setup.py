from setuptools import setup, find_packages

setup(name='Moneta',
        version='1.0',
        packages=find_packages(exclude=("vaextended",)),
        )
