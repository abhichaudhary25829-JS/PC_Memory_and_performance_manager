import psutil


def top_processes(n: int = 15, sort_by: str = "cpu") -> list[dict]:
    """Return visible processes sorted by CPU or resident memory usage."""
    cores = psutil.cpu_count() or 1
    rows = []
    for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_info", "memory_percent"]):
        try:
            i = p.info
            memory_info = i.get("memory_info")
            rows.append({
                "pid": i.get("pid"),
                "name": i.get("name") or "?",
                "cpu": (i.get("cpu_percent") or 0.0) / cores,
                "mem_mb": memory_info.rss / 2**20 if memory_info else 0.0,
                "mem_percent": float(i.get("memory_percent") or 0.0),
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    key = "cpu" if sort_by == "cpu" else "mem_mb"
    rows.sort(key=lambda r: r[key], reverse=True)
    return rows[:n]
