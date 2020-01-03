# pylint: skip-file
from setuptools import setup, find_packages

setup(name='losanalyst',
      version='0.2.0',
      description='Line-of-Sight Analyst package',
      url='https://github.com/JanCaha/los_analyst',
      author='Jan Caha',
      author_email='jan.caha@outlook.com',
      license='MIT',
      packages=find_packages(),
      install_requires=[
          'markdown',
          'gdal',
          'numpy',
          'gdalhelpers',
          'nose'
      ],
      zip_safe=False,
      test_suite='nose.collector',
      tests_require=['nose']
      )
