from collections import defaultdict
from .exceptions import InvalidPIDException


class Process:
    def __init__(self, metrics_data, pid):
        self.metrics_data = metrics_data
        self.validate_pid(pid)
        self._pid = pid
        self.process_info = self.get_process_info()

    def validate_pid(self, value):

        timestamps = [
            timestamp
            for timestamp in self.metrics_data["raw_data"]["power_data"]["raw_data"]
        ]
        consumers = [timestamp["consumers"] for timestamp in timestamps]
        pids = set([process["pid"] for consumer in consumers for process in consumer])
        if value in pids:
            return value
        else:
            raise InvalidPIDException(value)

    @property
    def pid(self, pid):
        """The PID queried in data coming from Scaphandre."""
        return self._pid

    @pid.setter
    def pid(self, value):
        self._pid = self.validate_pid(value)

    def get_process_info(self):

        timestamps = [
            timestamp
            for timestamp in self.metrics_data["raw_data"]["power_data"]["raw_data"]
        ]
        consumers = [timestamp["consumers"] for timestamp in timestamps]
        process_info = [
            process
            for consumer in consumers
            for process in consumer
            if process["pid"] == self._pid
        ]
        return process_info

    @property
    def process_name(self):
        process_name = self.process_info[0]["exe"].split("/")[-1]
        return process_name

    @property
    def process_exe(self):
        process_exe = self.process_info[0]["exe"]
        return process_exe

    def get_total_ram_in_bytes(self):

        ram_data = self.metrics_data["raw_data"]["hardware_data"]["rams"]
        total_ram_in_bytes = (
            sum(ram_unit["capacity"] for ram_unit in ram_data) * 1073741824
        )

        return total_ram_in_bytes

    def get_disk_usage_in_bytes(self):

        disk_total_bytes = int(
            self.metrics_data["raw_data"]["power_data"]["raw_data"][1]["host"][
                "components"
            ]["disks"][0]["disk_total_bytes"]
        )
        disk_available_bytes = int(
            self.metrics_data["raw_data"]["power_data"]["raw_data"][1]["host"][
                "components"
            ]["disks"][0]["disk_available_bytes"]
        )
        disk_usage_in_bytes = disk_total_bytes - disk_available_bytes
        return disk_usage_in_bytes

    @property
    def ram_shares(self):

        process_ram_shares = [
            (
                (
                    int(timestamp["resources_usage"]["memory_usage"])
                    / self.get_total_ram_in_bytes()
                )
                * 100
            )
            for timestamp in self.process_info
        ]

        return process_ram_shares

    @property
    def cpu_load_shares(self):

        process_cpu_load_shares = [
            float(timestamp["resources_usage"]["cpu_usage"])
            for timestamp in self.process_info
        ]
        return process_cpu_load_shares

    @property
    def storage_shares(self):
        process_storage_shares = [
            (
                (
                    int(timestamp["resources_usage"]["disk_usage_write"])
                    / self.get_disk_usage_in_bytes()
                )
                * 100
            )
            for timestamp in self.process_info
        ]
        return process_storage_shares

    def get_component_embedded_impact_shares(self, queried_component, component_shares):

        component = f"{queried_component}-1"
        component_impacts_data = self.metrics_data["raw_data"]["boaviztapi_data"][
            "verbose"
        ][component]["impacts"]
        component_embedded_impact_shares = list()
        for impact in component_impacts_data:
            impact_embedded_value = component_impacts_data[impact]["embedded"]["value"]
            for process_component_share in component_shares:
                if process_component_share == 0.0:
                    component_embedded_impact = (
                        f"{impact}_embedded_share",
                        float(process_component_share),
                    )
                    component_embedded_impact_shares.append(component_embedded_impact)
                else:
                    component_embedded_impact_share = (
                        float(impact_embedded_value) * float(process_component_share)
                    ) / 100
                    component_embedded_impact = (
                        f"{impact}_embedded_share",
                        float(component_embedded_impact_share),
                    )
                    component_embedded_impact_shares.append(component_embedded_impact)
        return component_embedded_impact_shares

    def get_component_embedded_impact_values(self, queried_component):
        if queried_component == "cpu":
            component_impact_shares = self.get_component_embedded_impact_shares(
                "CPU", self.cpu_load_shares
            )
        elif queried_component == "ram":
            component_impact_shares = self.get_component_embedded_impact_shares(
                "RAM", self.ram_shares
            )
        elif queried_component == "ssd":
            component_impact_shares = self.get_component_embedded_impact_shares(
                "SSD", self.storage_shares
            )
        elif queried_component == "hdd":
            component_impact_shares = self.get_component_embedded_impact_shares(
                "HDD", self.storage_shares
            )
        else:
            return "Queried component is not available for evaluation."

        gwp_list = defaultdict(list)
        adp_list = defaultdict(list)
        pe_list = defaultdict(list)

        for impact_key, impact_value in component_impact_shares:
            if impact_key == "gwp_embedded_share":
                gwp_list[impact_key].append(impact_value)
            if impact_key == "adp_embedded_share":
                adp_list[impact_key].append(impact_value)
            if impact_key == "pe_embedded_share":
                pe_list[impact_key].append(impact_value)

        gwp_average = sum(gwp_list["gwp_embedded_share"]) / len(
            gwp_list["gwp_embedded_share"]
        )
        adp_average = sum(adp_list["adp_embedded_share"]) / len(
            adp_list["adp_embedded_share"]
        )
        pe_average = sum(pe_list["pe_embedded_share"]) / len(
            pe_list["pe_embedded_share"]
        )

        gwp_max = max(gwp_list["gwp_embedded_share"])
        adp_max = max(adp_list["adp_embedded_share"])
        pe_max = max(pe_list["pe_embedded_share"])

        gwp_min = min(gwp_list["gwp_embedded_share"])
        adp_min = min(adp_list["adp_embedded_share"])
        pe_min = min(pe_list["pe_embedded_share"])

        component_embedded_impact_values = {
            f"gwp_{queried_component}_average_impact": gwp_average,
            f"adp_{queried_component}_average_impact": adp_average,
            f"pe_{queried_component}_average_impact": pe_average,
            f"gwp_{queried_component}_max_impact": gwp_max,
            f"adp_{queried_component}_max_impact": adp_max,
            f"pe_{queried_component}_max_impact": pe_max,
            f"gwp_{queried_component}_min_impact": gwp_min,
            f"adp_{queried_component}_min_impact": adp_min,
            f"pe_{queried_component}_min_impact": pe_min,
        }
        return component_embedded_impact_values

    @property
    def embedded_impact_values(self):
        process_embedded_impact_values = {}
        components = ["cpu", "ram", "hdd", "ssd"]

        for component in components:
            try:
                process_component_embedded_impact_values = (
                    self.get_component_embedded_impact_values(component)
                )
                process_embedded_impact_values[
                    f"process_{component}_embedded_impact_values"
                ] = process_component_embedded_impact_values
            except KeyError as absent_component:
                print(
                    f"Queried component is not present in Boagent metrics: {absent_component}"
                )

        return process_embedded_impact_values
