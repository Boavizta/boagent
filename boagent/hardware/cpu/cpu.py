#!/usr/bin/env python3
from cpuinfo import get_cpu_info
from cpuid import *
import cpuid_native
import sys


def get_socket_number_linux(location="/sys/devices/system/node/possible"):
    if sys.platform != "linux":
        return "cannot compute socket number for other OS than linux"
    with open(location, 'r') as f:
        data = f.read()
    return int(data.split('-')[-1])+1


def is_set(id, reg_idx, bit):
    regs = cpuid(id)

    if (1 << bit) & regs[reg_idx]:
        return "Yes"
    else:
        return "--"

def get_cpus():
    cpu_info = []
    for i in range(get_socket_number_linux()):
        cpu_info.append({
            "vendor": cpu_vendor(),
            "name": cpu_name(),
            "microarch": cpu_microarchitecture(),
            "vector_instructions": {
                "sse": is_set(1, 3, 25),
                "sse2": is_set(1, 3, 26),
                "sse3": is_set(1, 2, 0),
                "ssse3": is_set(1, 2, 9),
                "sse4.1": is_set(1, 2, 19),
                "sse4.2": is_set(1, 2, 20),
                "sse4a": is_set(0x80000001, 2, 6),
                "avx": is_set(1, 2, 28),
                "avx2": is_set(7, 1, 5),
                "bmi1": is_set(7, 1, 3),
                "bmi2": is_set(7, 1, 8),
            },
            "cpu_info": get_cpu_info(),
        })
    return cpu_info

if __name__ =="__main__":
    print("socket number linux from a file : {}".format(get_socket_number_linux()))
    print("Info from the library cpuid-py:")
    cpu_info = get_cpus()
    for toto in [cpu_info[0], get_cpu_info()]:
        print("\n\n\n")
        for key,value in toto.items():
            if(value is dict):
                for i,j in value.items():
                    if(j is dict):
                        for a,b in value.items():
                            print("{} : {}\n".format(a ,b))

                    print("{} : {}\n".format(i,j))

            else:
                print("{} : {}\n".format(key,value))
