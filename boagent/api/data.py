from dataclasses import dataclass


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
    key: str
    acronym: str
    embedded: str
    use_stage: str


@dataclass
class ImpactCriteria:
    adp: ImpactCriterion
    gwp: ImpactCriterion
    pe: ImpactCriterion
    adpe: ImpactCriterion
    adpf: ImpactCriterion
    ap: ImpactCriterion
    ctue: ImpactCriterion
    ctuh_c: ImpactCriterion
    epf: ImpactCriterion
    epm: ImpactCriterion
    ept: ImpactCriterion
    fe: ImpactCriterion
    fw: ImpactCriterion
    gwppb: ImpactCriterion
    gwppf: ImpactCriterion
    gwpplu: ImpactCriterion
    ir: ImpactCriterion
    lu: ImpactCriterion
    mips: ImpactCriterion
    odp: ImpactCriterion
    pm: ImpactCriterion
    pocp: ImpactCriterion
    wu: ImpactCriterion


adp = ImpactCriterion(
    "Abiotic Depletion Potential",
    "adp",
    "ADP",
    "Embedded abiotic ressources consumed, from start_time to end_time.",
    "Abiotic ressources consumed during the usage stage, from start_time to end_time.",
)

adpe = ImpactCriterion(
    "Abiotic Depletion Potential (Mineral and metal)",
    "adpe",
    "ADPe",
    "Embedded abiotic ressources (mineral and metal) consumed, from start_time to end_time.",
    "Abiotic ressources (mineral and metal) consumed during the usage stage, from start_time to end_time.",
)

adpf = ImpactCriterion(
    "Abiotic Depletion Potential (Fossil)",
    "adpf",
    "ADPf",
    "Embedded abiotic ressources (fossil) consumed, from start_time to end_time.",
    "Abiotic ressources (fossil) consumed during the usage stage, from start_time to end_time.",
)

ap = ImpactCriterion(
    "Acidification Potential",
    "ap",
    "AP",
    "Embedded acidification impacts consumed, from start_time to end_time.",
    "Acidification impacts consumed during the usage stage, from start_time to end_time.",
)

ctue = ImpactCriterion(
    "Comparative Toxicity Units for Ecosystems",
    "ctue",
    "CTUE",
    "Embedded toxicity impacts for ecosystems consumed, from start_time to end_time.",
    "Toxicity impacts for ecosystems consumed during the usage stage, from start_time to end_time.",
)

ctuh_c = ImpactCriterion(
    "Comparative Toxicity Units for Humans (Carcinogenic effets)",
    "ctuh_c",
    "CTUH_c",
    "Embedded toxicity impacts for humans (carcinogenic) consumed, from start_time to end_time.",
    "Toxicity impacts for humans (carcinogenic) consumed during the usage stage, from start_time to end_time.",
)

ctuh_nc = ImpactCriterion(
    "Comparative Toxicity Units for Humans (Non-Carcinogenic effets)",
    "ctuh_nc",
    "CTUH_nc",
    "Embedded toxicity impacts for humans (non-carcinogenic) consumed, from start_time to end_time.",
    "Toxicity impacts for humans (non-carcinogenic) consumed during the usage stage, from start_time to end_time.",
)

epf = ImpactCriterion(
    "Eutrophication Potential Fresh Water",
    "epf",
    "EPF",
    "Embedded eutrophication of fresh water impacts consumed, from start_time to end_time.",
    "Eutrophication of fresh water impacts consumed during the usage stage, from start_time to end_time.",
)

epm = ImpactCriterion(
    "Eutrophication Potential Marine Water",
    "epm",
    "EPM",
    "Embedded eutrophication of marine water impacts consumed, from start_time to end_time.",
    "Eutrophication of marine water impacts consumed during the usage stage, from start_time to end_time.",
)

ept = ImpactCriterion(
    "Eutrophication Potential Terrestrial",
    "ept",
    "EPT",
    "Embedded eutrophication of land impacts consumed, from start_time to end_time.",
    "Eutrophication of land impacts consumed during the usage stage, from start_time to end_time.",
)

fe = ImpactCriterion(
    "Final Energy",
    "fe",
    "FE",
    "Embedded final energy consumed, from start_time to end_time.",
    "Final Energy consumed during the usage stage, from start_time to end_time.",
)

fw = ImpactCriterion(
    "Fresh Water use",
    "fw",
    "FW",
    "Embedded fresh water consumed, from start_time to end_time.",
    "Fresh water consumed during the usage stage, from start_time to end_time.",
)

gwp = ImpactCriterion(
    "Global Warming Potential",
    "gwp",
    "GWP",
    "Embedded greenhouse gases emissions, from start_time to end_time.",
    "Greenhouse Gases emissions consumed during the usage stage, from start_time to end_time.",
)

gwppb = ImpactCriterion(
    "Global Warming Potential (Biogenic Emissions)",
    "gwppb",
    "GWPpb",
    "Embedded greenhouse gases emissions (biogenic emissions), from start_time to end_time.",
    "Greenhouse Gases emissions (biogenic emissions) consumed during the usage stage, from start_time to end_time.",
)

gwppf = ImpactCriterion(
    "Global Warming Potential (Fossil Fuels)",
    "gwppf",
    "GWPpf",
    "Embedded greenhouse gases emissions (fossil fuels), from start_time to end_time.",
    "Greenhouse Gases emissions (fossil fuels) consumed during the usage stage, from start_time to end_time.",
)

gwpplu = ImpactCriterion(
    "Global Warming Potential (Land Use)",
    "gwpplu",
    "GWPplu",
    "Embedded greenhouse gases emissions (land use), from start_time to end_time.",
    "Greenhouse Gases emissions (land use) consumed during the usage stage, from start_time to end_time.",
)

ir = ImpactCriterion(
    "Ionising Radiation",
    "ir",
    "IR",
    "Embedded ionising radiation emissions, from start_time to end_time.",
    "Ionising radiation emissions consumed during the usage stage, from start_time to end_time.",
)

lu = ImpactCriterion(
    "Land use",
    "lu",
    "LU",
    "Embedded land use impacts, from start_time to end_time.",
    "Land use impacts during the usage stage, from start_time to end_time.",
)


mips = ImpactCriterion(
    "Material Input Per Unit of Service",
    "mips",
    "MIPS",
    "Embedded material inputs consumed per unit of service, from start_time to end_time.",
    "Material inputs per unit of service consumed during the usage stage, from start_time to end_time.",
)

odp = ImpactCriterion(
    "Ozone Depletion Potential",
    "odp",
    "ODP",
    "Embedded ozone depletion impacts, from start_time to end_time.",
    "Ozone depletion impacts consumed during the usage stage, from start_time to end_time.",
)


pe = ImpactCriterion(
    "Primary Energy",
    "pe",
    "PE",
    "Embedded primary energy consumed, from start_time to end_time.",
    "Primary Energy consumed during the usage stage, from start_time to end_time.",
)

pm = ImpactCriterion(
    "Particulate Matter",
    "pm",
    "PM",
    "Embedded particulate matter emissions consumed, from start_time to end_time.",
    "Particulate matter emissions consumed during the usage stage, from start_time to end_time.",
)

pocp = ImpactCriterion(
    "Photochemical Ozone Creation Potential",
    "pocp",
    "POCP",
    "Embedded photochemical ozone formation impacts consumed, from start_time to end_time.",
    "Photochemical ozone formation impacts consumed during the usage stage, from start_time to end_time.",
)

wu = ImpactCriterion(
    "Water Use",
    "wu",
    "WU",
    "Embedded water use impacts consumed, from start_time to end_time.",
    "Water use impacts consumed during the usage stage, from start_time to end_time.",
)

impact_criteria = ImpactCriteria(
    adp,
    adpe,
    adpf,
    ctue,
    ctuh_c,
    ctuh_nc,
    epf,
    epm,
    ept,
    fe,
    fw,
    gwp,
    gwppb,
    gwppf,
    gwpplu,
    ir,
    lu,
    mips,
    odp,
    pe,
    pm,
    pocp,
    wu,
)
