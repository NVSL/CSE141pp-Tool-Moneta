from setuptools import setup, find_packages, Extension


setup(name='Moneta',
      version='1.0',
      packages=find_packages("moneta", exclude=("vaextended",)),
      package_dir={'': 'moneta'},
      entry_points={
          'console_scripts' :[
              'mtrace=moneta.mtrace:main'
              ]
      }
)
          
