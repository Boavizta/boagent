class MockLshw:
    def __init__(self):
        self.cpus = {
            "cpus": [
                {
                    "units": 1,
                    "name": "AMD Ryzen 5 5600H with Radeon Graphics",
                    "manufacturer": "Advanced Micro Devices [AMD]",
                    "core_units": 6,
                }
            ]
        }
        self.memories = {
            "rams": [
                {"units": 1, "manufacturer": "Samsung", "capacity": 8},
                {"units": 1, "manufacturer": "Kingston", "capacity": 16},
            ]
        }
        self.disks = {
            "disks": [
                {
                    "units": 1,
                    "logicalname": "/dev/nvme0n1",
                    "manufacturer": "samsung",
                    "type": "ssd",
                    "capacity": 476,
                }
            ],
        }
