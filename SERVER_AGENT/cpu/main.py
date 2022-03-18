#!/usr/bin/env python3.9
from time import sleep
from tracemalloc import stop
from cpuinfo import get_cpu_info
from cpuid import *
import cpuid_native
import openapi_client
from openapi_client.model import component_cpu



#if __name__ == "__main__":




def is_set(id, reg_idx, bit):
    regs = cpuid(id)

    if (1 << bit) & regs[reg_idx]:
        return "Yes"
    else:
        return "--"

print("Vendor ID         : %s" % cpu_vendor())
print("CPU name          : %s" % cpu_name())
print("Microarchitecture : %s%s" % cpu_microarchitecture())
# print("Vector instructions supported:")
# print("SSE       : %s" % is_set(1, 3, 25))
# print("SSE2      : %s" % is_set(1, 3, 26))
# print("SSE3      : %s" % is_set(1, 2, 0))
# print("SSSE3     : %s" % is_set(1, 2, 9))
# print("SSE4.1    : %s" % is_set(1, 2, 19))
# print("SSE4.2    : %s" % is_set(1, 2, 20))
# print("SSE4a     : %s" % is_set(0x80000001, 2, 6))
# print("AVX       : %s" % is_set(1, 2, 28))
# print("AVX2      : %s" % is_set(7, 1, 5))
# print("BMI1      : %s" % is_set(7, 1, 3))
# print("BMI2      : %s" % is_set(7, 1, 8))
# print("info from cpu_info package : {}".format(get_cpu_info()))



cpu_obj = component_cpu.ComponentCPU()
cpu_obj.core_units = get_cpu_info()["count"]

cpu_obj.manufacturer = cpu_vendor()
cpu_obj.family = str(cpu_microarchitecture())

print("cpu info : {}".format(cpu_obj.to_dict))