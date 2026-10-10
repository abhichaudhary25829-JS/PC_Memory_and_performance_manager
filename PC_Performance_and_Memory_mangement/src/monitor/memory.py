import psutil


def read() -> dict:
    """Return real physical-memory and virtual-memory/swap readings."""
    vm, sw = psutil.virtual_memory(), psutil.swap_memory()
    return {
        "percent": vm.percent,
        "used_gb": vm.used / 2**30,
        "total_gb": vm.total / 2**30,
        "available_gb": vm.available / 2**30,
        "free_gb": vm.free / 2**30,
        "swap_percent": sw.percent,
        "swap_used_gb": sw.used / 2**30,
        "swap_total_gb": sw.total / 2**30,
    }
