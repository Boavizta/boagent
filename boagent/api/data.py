from dataclasses import asdict, dataclass
from typing import List


@dataclass
class Unit:
    name: str
    short_form: str
    long_form: str


@dataclass
class Units:
    co2_equivalent: Unit
    co2_equivalent_per_khw: Unit
    cube_meter: Unit
    cube_meter_equivalent: Unit
    disease_occurence: Unit
    freon11_equivalent: Unit
    kilograms: Unit
    mega_joules: Unit
    mol_hydron_equivalent: Unit
    mol_nitrogen_equivalent: Unit
    nitrogen_equivalent: Unit
    nmvoc_equivalent: Unit
    not_applicable: Unit
    phosphorus_equivalent: Unit
    sb_equivalent: Unit
    seconds: Unit
    toxicity_ecosystems: Unit
    toxicity_humans: Unit
    uranium235_equivalent: Unit
    watts: Unit


co2_equivalent = Unit("Kilogram CO2 equivalent", "kgCO2eq", "Kilograms CO2 equivalent")
co2_equivalent_per_khw = Unit(
    "Kilogram CO2 equivalent per Kilowatt-hour",
    "kgCO2eq / kWh",
    "Kilograms CO2 equivalent per Kilowatt-hour",
)
cube_meter = Unit("Cube Meter", "m3", "Cube meters")
cube_meter_equivalent = Unit("Cube Meter equivalent", "m3eq", "Cube meters equivalent")
disease_occurence = Unit(
    "Disease Occurence per kilogram of PM2.5 emitted",
    "dis. occ.",
    "Disease occurences per kilogram of PM2.5 emitted",
)
freon11_equivalent = Unit(
    "Kilogram Freon-11 equivalent", "kgCFC11eq", "Kilograms Freon-11 equivalent"
)
kilograms = Unit("Kilogram", "kg", "Kilograms")
mega_joules = Unit("Megajoule", "MJ", "Megajoules")
mol_hydron_equivalent = Unit(
    "Mole Hydron equivalent", "molH+eq", "Moles Hydron equivalent"
)
mol_nitrogen_equivalent = Unit(
    "Mole Nitrogen equivalent", "molNeq", "Moles Nitrogen equivalent"
)
nitrogen_equivalent = Unit(
    "Kilogram Nitrogen equivalent", "kgNeq", "Kilograms Nitrogen equivalent"
)
nmvoc_equivalent = Unit(
    "Kilogram Non-Methane Volatile Organic Compound",
    "kgNMVOCeq",
    "Kilograms Non-Methane Volatine Organic Compound",
)
not_applicable = Unit("Not applicable", "NA", "Not applicable")
phosphorus_equivalent = Unit(
    "Kilogram Phosphorus equivalent", "kgPeq", "Kilograms Phosphorus equivalent"
)
sb_equivalent = Unit(
    "Kilogram Antimony equivalent", "kgSbeq", "Kilograms Sb equivalent"
)
seconds = Unit("Second", "s", "Seconds")
toxicity_ecosystems = Unit(
    "Toxicity Unit for Ecosystem", "CTUe", "Toxicity Units for Ecosystems"
)
toxicity_humans = Unit("Toxicity Unit for Human", "CTUh", "Toxicity Units for Humans")
uranium235_equivalent = Unit(
    "Kilogram Uranium-235 equivalent", "kgU235eq", "Kilograms Uranium-235 equivalent"
)
watts = Unit("Watt", "W", "Watts")

units = Units(
    co2_equivalent,
    co2_equivalent_per_khw,
    cube_meter,
    cube_meter_equivalent,
    disease_occurence,
    freon11_equivalent,
    kilograms,
    mega_joules,
    mol_hydron_equivalent,
    mol_nitrogen_equivalent,
    nitrogen_equivalent,
    nmvoc_equivalent,
    not_applicable,
    phosphorus_equivalent,
    sb_equivalent,
    seconds,
    toxicity_ecosystems,
    toxicity_humans,
    uranium235_equivalent,
    watts,
)


@dataclass
class ImpactCriterion:
    name: str
    key: str
    acronym: str
    embedded: str
    use_stage: str
    boagent_use_key: str
    boagent_embedded_key: str
    unit: Unit

    def __getitem__(self, key):
        return self[key]


@dataclass
class ImpactCriteria:
    adp: ImpactCriterion
    adpe: ImpactCriterion
    adpf: ImpactCriterion
    ap: ImpactCriterion
    ctue: ImpactCriterion
    ctuh_c: ImpactCriterion
    ctuh_nc: ImpactCriterion
    epf: ImpactCriterion
    epm: ImpactCriterion
    ept: ImpactCriterion
    fe: ImpactCriterion
    fw: ImpactCriterion
    gwp: ImpactCriterion
    gwppb: ImpactCriterion
    gwppf: ImpactCriterion
    gwpplu: ImpactCriterion
    ir: ImpactCriterion
    lu: ImpactCriterion
    mips: ImpactCriterion
    odp: ImpactCriterion
    pe: ImpactCriterion
    pm: ImpactCriterion
    pocp: ImpactCriterion
    wu: ImpactCriterion

    def main_criteria(self) -> List[ImpactCriterion]:
        main_criteria = filter(
            lambda c: c["key"] == impact_criteria.gwp.key
            or c["key"] == impact_criteria.adp.key
            or c["key"] == impact_criteria.pe.key,
            list(asdict(impact_criteria).values()),
        )
        return list(main_criteria)


adp = ImpactCriterion(
    "Abiotic Depletion Potential",
    "adp",
    "ADP",
    "Embedded abiotic ressources consumed, from start_time to end_time.",
    "Abiotic ressources consumed during the usage stage, from start_time to end_time.",
    "total_operational_abiotic_resources_depletion",
    "embedded_abiotic_resources_depletion",
    sb_equivalent,
)

adpe = ImpactCriterion(
    "Abiotic Depletion Potential Elements",
    "adpe",
    "ADPe",
    "Embedded abiotic ressources (mineral and metal) consumed, from start_time to end_time.",
    "Abiotic ressources (mineral and metal) consumed during the usage stage, from start_time to end_time.",
    "total_operational_abiotic_resources_elements_depletion",
    "embedded_abiotic_resources_elements_depletion",
    sb_equivalent,
)

adpf = ImpactCriterion(
    "Abiotic Depletion Potential Fossil",
    "adpf",
    "ADPf",
    "Embedded abiotic ressources (fossil) consumed, from start_time to end_time.",
    "Abiotic ressources (fossil) consumed during the usage stage, from start_time to end_time.",
    "total_operational_abiotic_resources_fossil_depletion",
    "embedded_abiotic_resources_fossil_depletion",
    mega_joules,
)

ap = ImpactCriterion(
    "Acidification Potential",
    "ap",
    "AP",
    "Embedded acidification impacts consumed, from start_time to end_time.",
    "Acidification impacts consumed during the usage stage, from start_time to end_time.",
    "total_operational_acidification_potential",
    "embedded_acidification_potential",
    mol_hydron_equivalent,
)

ctue = ImpactCriterion(
    "Comparative Toxicity Units for Ecosystems",
    "ctue",
    "CTUE",
    "Embedded toxicity impacts for ecosystems consumed, from start_time to end_time.",
    "Toxicity impacts for ecosystems consumed during the usage stage, from start_time to end_time.",
    "total_operational_comparative_toxicity_units_ecosystems",
    "embedded_comparative_toxicity_units_ecosystems",
    toxicity_ecosystems,
)

ctuh_c = ImpactCriterion(
    "Comparative Toxicity Units for Humans (Carcinogenic effets)",
    "ctuh_c",
    "CTUH_c",
    "Embedded toxicity impacts for humans (carcinogenic) consumed, from start_time to end_time.",
    "Toxicity impacts for humans (carcinogenic) consumed during the usage stage, from start_time to end_time.",
    "total_operational_comparative_toxicity_units_humans_carcinogenic",
    "embedded_comparative_toxicity_humans_carcinogenic",
    toxicity_humans,
)

ctuh_nc = ImpactCriterion(
    "Comparative Toxicity Units for Humans (Non-Carcinogenic effets)",
    "ctuh_nc",
    "CTUH_nc",
    "Embedded toxicity impacts for humans (non-carcinogenic) consumed, from start_time to end_time.",
    "Toxicity impacts for humans (non-carcinogenic) consumed during the usage stage, from start_time to end_time.",
    "total_operational_comparative_toxicity_units_humans_non_carcinogenic",
    "embedded_comparative_toxicity_humans_non_carcinogenic",
    toxicity_humans,
)

epf = ImpactCriterion(
    "Eutrophication Potential Fresh Water",
    "epf",
    "EPF",
    "Embedded eutrophication of fresh water impacts consumed, from start_time to end_time.",
    "Eutrophication of fresh water impacts consumed during the usage stage, from start_time to end_time.",
    "total_operational_eutrophication_potential_fresh_water",
    "embedded_eutrophication_potential_fresh_water",
    phosphorus_equivalent,
)

epm = ImpactCriterion(
    "Eutrophication Potential Marine Water",
    "epm",
    "EPM",
    "Embedded eutrophication of marine water impacts consumed, from start_time to end_time.",
    "Eutrophication of marine water impacts consumed during the usage stage, from start_time to end_time.",
    "total_operational_eutrophication_potential_marine_water",
    "embedded_eutrophication_potential_marine_water",
    nitrogen_equivalent,
)

ept = ImpactCriterion(
    "Eutrophication Potential Terrestrial",
    "ept",
    "EPT",
    "Embedded eutrophication of land impacts consumed, from start_time to end_time.",
    "Eutrophication of land impacts consumed during the usage stage, from start_time to end_time.",
    "total_operational_eutrophication_potential_terrestrial",
    "embedded_eutrophication_potential_terrestrial",
    mol_nitrogen_equivalent,
)

fe = ImpactCriterion(
    "Final Energy",
    "fe",
    "FE",
    "Embedded final energy consumed, from start_time to end_time.",
    "Final Energy consumed during the usage stage, from start_time to end_time.",
    "total_operational_final_energy",
    "embedded_eutrophication_final_energy",
    mega_joules,
)

fw = ImpactCriterion(
    "Fresh Water use",
    "fw",
    "FW",
    "Embedded fresh water consumed, from start_time to end_time.",
    "Fresh water consumed during the usage stage, from start_time to end_time.",
    "total_operational_fresh_water",
    "embedded_eutrophication_fresh_water",
    cube_meter,
)

gwp = ImpactCriterion(
    "Global Warming Potential",
    "gwp",
    "GWP",
    "Embedded greenhouse gases emissions, from start_time to end_time.",
    "Greenhouse Gases emissions consumed during the usage stage, from start_time to end_time.",
    "total_operational_emissions",
    "embedded_emissions",
    co2_equivalent,
)

gwppb = ImpactCriterion(
    "Global Warming Potential (Biogenic Emissions)",
    "gwppb",
    "GWPpb",
    "Embedded greenhouse gases emissions (biogenic emissions), from start_time to end_time.",
    "Greenhouse Gases emissions (biogenic emissions) consumed during the usage stage, from start_time to end_time.",
    "total_operational_biogenic_emissions",
    "embedded_biogenic_emissions",
    co2_equivalent,
)

gwppf = ImpactCriterion(
    "Global Warming Potential (Fossil Fuels)",
    "gwppf",
    "GWPpf",
    "Embedded greenhouse gases emissions (fossil fuels), from start_time to end_time.",
    "Greenhouse Gases emissions (fossil fuels) consumed during the usage stage, from start_time to end_time.",
    "total_operational_fossil_fuels_emissions",
    "embedded_fossil_fuels_emissions",
    co2_equivalent,
)

gwpplu = ImpactCriterion(
    "Global Warming Potential (Land Use)",
    "gwpplu",
    "GWPplu",
    "Embedded greenhouse gases emissions (land use), from start_time to end_time.",
    "Greenhouse Gases emissions (land use) consumed during the usage stage, from start_time to end_time.",
    "total_operational_land_use_emissions",
    "embedded_land_use_emissions",
    co2_equivalent,
)

ir = ImpactCriterion(
    "Ionising Radiation",
    "ir",
    "IR",
    "Embedded ionising radiation emissions, from start_time to end_time.",
    "Ionising radiation emissions consumed during the usage stage, from start_time to end_time.",
    "total_operational_ionising_radiation",
    "embedded_ionising_radiation",
    uranium235_equivalent,
)

lu = ImpactCriterion(
    "Land use",
    "lu",
    "LU",
    "Embedded land use impacts, from start_time to end_time.",
    "Land use impacts during the usage stage, from start_time to end_time.",
    "total_operational_land_use",
    "embedded_land_use",
    not_applicable,
)


mips = ImpactCriterion(
    "Material Input Per Unit of Service",
    "mips",
    "MIPS",
    "Embedded material inputs consumed per unit of service, from start_time to end_time.",
    "Material inputs per unit of service consumed during the usage stage, from start_time to end_time.",
    "total_operational_material_inputs_per_unit_of_service",
    "embedded_land_material_inputs_per_unit_of_service",
    kilograms,
)

odp = ImpactCriterion(
    "Ozone Depletion Potential",
    "odp",
    "ODP",
    "Embedded ozone depletion impacts, from start_time to end_time.",
    "Ozone depletion impacts consumed during the usage stage, from start_time to end_time.",
    "total_operational_ozone_depletion_potential",
    "embedded_ozone_depletion_potential",
    freon11_equivalent,
)


pe = ImpactCriterion(
    "Primary Energy",
    "pe",
    "PE",
    "Embedded primary energy consumed, from start_time to end_time.",
    "Primary Energy consumed during the usage stage, from start_time to end_time.",
    "total_operational_primary_energy_consumed",
    "embedded_primary_energy",
    mega_joules,
)

pm = ImpactCriterion(
    "Particulate Matter",
    "pm",
    "PM",
    "Embedded particulate matter emissions consumed, from start_time to end_time.",
    "Particulate matter emissions consumed during the usage stage, from start_time to end_time.",
    "total_operational_particulate_matter",
    "embedded_particulate_matter",
    disease_occurence,
)

pocp = ImpactCriterion(
    "Photochemical Ozone Creation Potential",
    "pocp",
    "POCP",
    "Embedded photochemical ozone formation impacts consumed, from start_time to end_time.",
    "Photochemical ozone formation impacts consumed during the usage stage, from start_time to end_time.",
    "total_operational_photochemical_ozone_creation_potential",
    "embedded_photochemical_ozone_creation_potential",
    nmvoc_equivalent,
)

wu = ImpactCriterion(
    "Water Use",
    "wu",
    "WU",
    "Embedded water use impacts consumed, from start_time to end_time.",
    "Water use impacts consumed during the usage stage, from start_time to end_time.",
    "total_operational_water_use",
    "embedded_water_use",
    cube_meter_equivalent,
)

impact_criteria = ImpactCriteria(
    adp,
    adpe,
    adpf,
    ap,
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
