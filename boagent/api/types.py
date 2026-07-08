from dataclasses import dataclass
from enum import Enum
from typing import List, Union
from boagent.api.models import WorkloadTime

TimeWorkload = Union[dict[str, float], dict[str, List[dict[str, WorkloadTime]]], None]
AveragePower = Union[float, None]


@dataclass
class Unit:
    name: str
    short_form: str
    long_form: str


@dataclass
class Units:
    co2_equivalent: Unit
    co2_equivalent_per_khw: Unit
    mega_joules: Unit
    sb_equivalent: Unit
    seconds: Unit
    watts: Unit


seconds = Unit("Second", "s", "Seconds")
mega_joules = Unit("Megajoule", "MJ", "Megajoules")
co2_equivalent = Unit("Kilogram CO2 equivalent", "kgCO2eq", "Kilograms CO2 equivalent")
sb_equivalent = Unit(
    "Kilogram Antimony equivalent", "kgSbeq", "Kilograms Sb equivalent"
)
watts = Unit("Watt", "W", "Watts")
co2_equivalent_per_khw = Unit(
    "Kilogram CO2 equivalent per Kilowatt-hour",
    "kgCO2eq / kWh",
    "Kilograms CO2 equivalent per Kilowatt-hour",
)

units = Units(
    co2_equivalent, co2_equivalent_per_khw, mega_joules, sb_equivalent, seconds, watts
)


@dataclass
class ImpactCriterion:
    name: str
    acronym: str
    embedded: str
    use_stage: str


@dataclass
class ImpactCriteria:
    adp: ImpactCriterion
    gwp: ImpactCriterion
    pe: ImpactCriterion


gwp = ImpactCriterion(
    "Global Warming Potential",
    "GWP",
    "Embedded greenhouse gases emissions, from start_time to end_time.",
    "Greenhouse Gases emissions consumed during the usage stage, from start_time to end_time.",
)

adp = ImpactCriterion(
    "Abiotic Depletion Potential",
    "ADP",
    "Embedded abiotic ressources consumed, from start_time to end_time.",
    "Abiotic ressources consumed during the usage stage, from start_time to end_time.",
)

pe = ImpactCriterion(
    "Primary Energy",
    "PE",
    "Embedded primary energy consumed, from start_time to end_time.",
    "Primary Energy consumed during the usage stage, from start_time to end_time.",
)

impact_criteria = ImpactCriteria(adp, gwp, pe)

MetricType = Enum("Metric", [("Gauge", "gauge"), ("Counter", "counter")])
