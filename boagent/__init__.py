"""
Boagent

Monitoring agent/framework for evaluating the environmental impacts of a machine and its applications, including several to all steps of the life cycle of the machine and service, plus multiple criterias of impacts (not just CO2eq metrics / Global Warming Potential). Part of the efforts of https://boavizta.org/en and https://sdialliance.org/.
"""
from importlib import metadata

md = metadata.metadata("boagent")
__version__ = metadata.version("boagent")
__author__ = md.get("Author-email")
