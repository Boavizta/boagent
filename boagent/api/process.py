import json


class Process:
    def __init__(self, metrics_data, pid):
        self.metrics_data = metrics_data
        self.pid = pid
        self.processed_metrics = self.process_metrics()
        self.process_info = self.get_process_info()
        self.total_ram_in_bytes = self.get_total_ram_in_bytes()
        self.ram_shares = self.get_ram_shares()
        self.ram_embedded_impact_shares = self.get_component_embedded_impact_shares(
            "RAM", self.ram_shares
        )
        self.cpu_load_shares = self.get_cpu_load_shares()
        self.cpu_embedded_impact_shares = self.get_component_embedded_impact_shares(
            "CPU", self.cpu_load_shares
        )
        self.cpu_average_embedded_impacts = self.get_component_average_embedded_impact(
            "cpu"
        )
        self.ram_average_embedded_impacts = self.get_component_average_embedded_impact(
            "ram"
        )

    def process_metrics(self):

        with open(self.metrics_data, "r") as metrics_data_file:
            metrics_data = json.load(metrics_data_file)

        return metrics_data

    def get_process_info(self):

        process_info = list()
        for timestamp in self.processed_metrics["raw_data"]["power_data"]["raw_data"]:
            for process in timestamp["consumers"]:
                if process["pid"] == self.pid:
                    process_info.append(process)
        return process_info

    def get_total_ram_in_bytes(self):

        ram_data = self.processed_metrics["raw_data"]["hardware_data"]["rams"]
        total_ram_in_bytes = (
            sum(ram_unit["capacity"] for ram_unit in ram_data) * 1073741824
        )

        return total_ram_in_bytes

    def get_ram_shares(self):
        process_ram_shares = list()
        for timestamp in self.process_info:
            process_ram_share = (
                int(timestamp["resources_usage"]["memory_usage"])
                / self.total_ram_in_bytes
            )
            process_ram_shares.append(process_ram_share)

        return process_ram_shares

    def get_cpu_load_shares(self):

        process_cpu_load_shares = list()
        for timestamp in self.process_info:
            process_cpu_load_share = float(timestamp["resources_usage"]["cpu_usage"])
            process_cpu_load_shares.append(process_cpu_load_share)

        return process_cpu_load_shares

    def get_component_embedded_impact_shares(self, queried_component, component_shares):

        component = f"{queried_component}-1"
        component_impacts_data = self.processed_metrics["raw_data"]["boaviztapi_data"][
            "verbose"
        ][component]["impacts"]
        component_embedded_impact_shares = list()
        for impact in component_impacts_data:
            impact_embedded_value = component_impacts_data[impact]["embedded"]["value"]
            for process_component_share in component_shares:
                if process_component_share == 0.0:
                    component_embedded_impact = {
                        f"{impact}_embedded_share": float(process_component_share)
                    }
                    component_embedded_impact_shares.append(component_embedded_impact)
                else:
                    component_embedded_impact_share = round(
                        float(impact_embedded_value) * float(process_component_share), 2
                    )
                    component_embedded_impact = {
                        f"{impact}_embedded_share": float(
                            component_embedded_impact_share
                        )
                    }
                    component_embedded_impact_shares.append(component_embedded_impact)
        return component_embedded_impact_shares

    def get_component_average_embedded_impact(self, queried_component):

        embedded_impacts_sums = {
            impact_criteria: sum(
                impact_dictionary[impact_criteria]
                for impact_dictionary in self.ram_embedded_impact_shares
                if impact_criteria in impact_dictionary
            )
            for impact_criteria in set(
                impact_criteria
                for impact_dictionary in self.ram_embedded_impact_shares
                for impact_criteria in impact_dictionary
            )
        }

        average_values = list()
        for impact_criteria in embedded_impacts_sums:
            average_result = embedded_impacts_sums[impact_criteria] / (
                len(self.ram_embedded_impact_shares) / 3
            )
            average_value = {f"{impact_criteria}_average": average_result}
            average_values.append(average_value)
