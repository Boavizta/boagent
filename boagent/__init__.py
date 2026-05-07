"""
Boagent

Monitoring agent/framework for evaluating the environmental impacts of a machine and its applications, including several to all steps of the life cycle of the machine and service, plus multiple criterias of impacts (not just CO2eq metrics / Global Warming Potential). Part of the efforts of https://boavizta.org/en and https://sdialliance.org/.
"""

from pyproject_metadata import StandardMetadata
import tomli

toml_content = ""

with open("./pyproject.toml", 'r') as fd:
    toml_content = fd.read()
    fd.close()

metadata = StandardMetadata.from_pyproject(tomli.loads(toml_content), allow_extra_keys=False)

__version__ = metadata.version
__authors__ = metadata.authors
