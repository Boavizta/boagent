# Disk hardware information retrieval.
## Linux
### Drives detection
Hardware drive information can be retrieved with sysfs (mounted on `/sys`). Partitions and
disks (real ones and software raids) can be found under `/sys/dev/block/`. If we are only
interrested in drives, then `/sys/block/` will be the root path of choice.

Under the `/sys/block/` directory, we will find soft links pointing to devices.
For the running kernel, _virtual_ drives are pointing to paths that looks like `.*/devices/virtual/.*`.
Virtual drives can be `lvm` volumes or `software raid` volumes.
For now on, other patterns can be considered as _real_ drives. One big warning here though,
if we are running in a virtual machine or a containerized environnement then the kernel will think
it is running on real drives.

## MacOS
TBD
## Windows
TBD
