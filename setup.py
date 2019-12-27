# pylint: skip-file
from setuptools import setup

setup(name='losanalyst',
      version='0.1',
      description='Line-of-Sight Analyst package',
      url='https://github.com/JanCaha/los_analyst',
      author='Jan Caha',
      author_email='jan.caha@outlook.com',
      license='MIT',
      packages=['losanalyst'],
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
