import sys

from setuptools import setup, find_packages
from boagent import __version__

py_version = sys.version_info[:2]
if py_version < (3, 7):
    raise Exception("api requires Python >= 3.7.")

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='boagent',
      maintainer="Benoit Petit",
      maintainer_email="bpetit@hubblo.org",
      version=__version__,
      packages=find_packages(),
      include_package_data=True,
      description="Local API and monitoring agent focussed on exposing environmental impacts metrics of the host. Based on the Boavizta API and Scaphandre.",
      use_pipfile=True,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/Boavizta/boagent",
      test_suite='tests',
      setup_requires=['setuptools-pipfile'],
      keywords=['carbon', 'footprint', 'environment', 'climate', 'co2', 'gwp', 'adp', 'pe', 'energy', 'boagent', 'scaphandre', 'boavizta', 'api'],
      classifiers=[
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.7",
          "Programming Language :: Python :: 3.8",
          "Programming Language :: Python :: 3.9",
          "Intended Audience :: Developers",
          "Operating System :: OS Independent",
      ],
      python_requires='>=3.7',
      entry_points=''' ''')
