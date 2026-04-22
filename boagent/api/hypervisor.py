import json
from pathlib import Path


def deserialize_virtual_machines_metrics(mount_path):
    virtual_machines_metrics = []
    virtual_machines = Path(f"{mount_path}/volumes")
    for vm in virtual_machines.iterdir():
        with open(f"{vm}/metrics.json") as metrics_fp:
            vm_metrics = json.load(metrics_fp)
            virtual_machines_metrics.append(vm_metrics)

    return virtual_machines_metrics


def generate_evaluated_process(process_data, hypervisor_hardware_data):
    process_name = process_data["exe"]
    process_id = process_data["pid"]
    process_memory_ratio = (
        int(process_data["resources_usage"]["memory_usage"])
        / hypervisor_hardware_data["total_memory"]
    ) * 100
    process_cpu_usage = float(process_data["resources_usage"]["cpu_usage"])
    evaluated_process = {
        "name": process_name,
        "id": process_id,
        "memory_ratio": process_memory_ratio,
        "cpu_usage": process_cpu_usage,
    }
    return evaluated_process


def generate_evaluated_virtual_machine(vm_data, hypervisor_metrics):
    vm_name = vm_data["name"]
    processes = [
        generate_evaluated_process(process, hypervisor_metrics)
        for process in vm_data["processes"]
    ]
    evaluated_vm = {"name": vm_name, "processes": processes}
    return evaluated_vm


def evaluate_virtual_machines(vms_metrics, hypervisor_hardware_data):
    hypervisor_memory_total_bytes = (
        sum([ram["capacity"] for ram in hypervisor_hardware_data["rams"]]) * 1073741824
    )
    hypervisor_aggregated_metrics = {"total_memory": hypervisor_memory_total_bytes}
    evaluated_virtual_machines = [
        generate_evaluated_virtual_machine(vm, hypervisor_aggregated_metrics)
        for vm in vms_metrics
    ]

    evaluation = {"virtual_machines": evaluated_virtual_machines}
    return evaluation
