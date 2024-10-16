import sys

from setuptools import setup, find_packages
from boagent import __version__

py_version = sys.version_info[:2]
if py_version < (3, 9):
    raise Exception("api requires Python >= 3.9.")

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="boagent",
    maintainer="Benoit Petit",
    maintainer_email="bpetit@hubblo.org",
    version=__version__,
    packages=find_packages(),
    include_package_data=True,
    description="Monitoring agent/framework for evaluating the environmental impacts of a machine and its applications, including several to all steps of the life cycle of the machine and service, plus multiple criterias of impacts (not just CO2eq metrics / Global Warming Potential). Part of the efforts of https://boavizta.org/en and https://sdialliance.org/.",
    use_pipfile=True,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Boavizta/boagent",
    test_suite="tests",
    setup_requires=["setuptools-pipfile"],
    keywords=[
        "carbon",
        "footprint",
        "environment",
        "climate",
        "co2",
        "gwp",
        "adp",
        "pe",
        "energy",
        "boagent",
        "scaphandre",
        "boavizta",
        "api",
    ],
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    entry_points=""" """,
)
