import time
from src.performance.history import History
from src.monitor.snapshot import Snapshot


def make_snapshot(ts=None):
    ts = time.time() if ts is None else ts
    return Snapshot(
        ts=ts,
        cpu={"percent": 25},
        memory={"percent": 42.5, "used_gb": 6.8, "total_gb": 16.0,
                "available_gb": 9.2, "swap_percent": 1.0,
                "swap_used_gb": 0.2, "swap_total_gb": 8.0},
        gpu=None,
        temps={},
        storage={"max_percent": 50},
    )


def test_memory_samples_persist_and_export(tmp_path):
    db_path = tmp_path / "history.db"
    csv_path = tmp_path / "memory.csv"
    history = History(path=db_path, every=0)
    history.record(make_snapshot(), 85)
    rows = history.recent_memory(hours=24)
    assert len(rows) == 1
    assert rows[0][1] == 42.5
    count = history.export_memory_csv(str(csv_path), hours=24)
    assert count == 1
    text = csv_path.read_text(encoding="utf-8")
    assert "ram_percent" in text
    assert "42.5" in text
    history.close()


def test_memory_history_supports_older_snapshots(tmp_path):
    history = History(path=tmp_path / "old.db", every=0)
    snap = Snapshot(
        ts=time.time(), cpu={"percent": 10},
        memory={"percent": 30, "used_gb": 4, "total_gb": 16, "swap_percent": 0},
        gpu=None, temps={}, storage={"max_percent": 20}
    )
    history.record(snap, 90)
    row = history.recent_memory(hours=24)[0]
    assert row[4] == 12
    assert row[5] == 0
    history.close()
