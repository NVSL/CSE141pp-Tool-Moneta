from setuptools import setup, find_packages, Extension


setup(name='Moneta',
      version='1.0',
      packages=find_packages(".", exclude=("vaextended",)),
      package_dir={'': 'moneta/moneta'},
      entry_points={
          'console_scripts' :[
              'mtrace=mtrace:main'
              ]
      }
)
          
