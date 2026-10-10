import sys
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QColor, QIcon
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QButtonGroup, QFrame, QGridLayout,
                               QHBoxLayout, QHeaderView, QLabel, QListWidget, QListWidgetItem,
                               QMainWindow, QProgressBar, QPushButton, QStackedWidget,
                               QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QFileDialog,
                               QMessageBox, QSpinBox, QScrollArea, QSizePolicy)

from src.alerts import AlertManager
from src.monitor import collect
from src.performance import History, compute_score, grade
from src.processes import top_processes
from src.ui.theme import ACCENT, STYLE, status_color
from src.ui.widgets import AreaChart, MetricCard, RingGauge, CoreBars

ASSETS = Path(__file__).resolve().parents[2] / "assets"


def card(layout_cls=QVBoxLayout, margins=(20, 16, 20, 16)):
    f = QFrame()
    f.setObjectName("card")
    lay = layout_cls(f)
    lay.setContentsMargins(*margins)
    return f, lay


def label(text, name):
    l = QLabel(text)
    l.setObjectName(name)
    return l


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PC Performance & Memory Management Suite")
        self.resize(1440, 900)
        self.history, self.alerts, self.bars = History(), AlertManager(), {}
        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)
        h = QHBoxLayout(root)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(0)
        self.pages = QStackedWidget()
        h.addWidget(self._sidebar())
        h.addWidget(self.pages, 1)
        for build in (self._dashboard, self._processes, self._memory, self._history, self._alerts):
            self.pages.addWidget(build())
        self.pages.currentChanged.connect(lambda i: self._refresh_history() if i == 3 else None)
        self.pages.currentChanged.connect(lambda i: self._refresh_memory() if i == 2 else None)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(1000)
        self.refresh()

    # ---------- layout ----------
    def _sidebar(self):
        f = QFrame()
        f.setObjectName("sidebar")
        f.setFixedWidth(178)
        v = QVBoxLayout(f)
        v.setContentsMargins(12, 22, 12, 16)
        v.addWidget(label("◉  PERFMONITOR", "logo"))
        v.addSpacing(20)
        self.group = QButtonGroup(self)
        for i, name in enumerate(("Dashboard", "Processes", "Memory Analyzer", "History", "Alerts")):
            b = QPushButton(name)
            b.setObjectName("nav")
            b.setCheckable(True)
            b.setChecked(i == 0)
            b.setCursor(Qt.PointingHandCursor)
            self.group.addButton(b, i)
            v.addWidget(b)
        self.group.idClicked.connect(self.pages.setCurrentIndex)
        v.addStretch()
        v.addWidget(label("● Live · refreshes every second", "cardSub"))
        return f

    def _page(self, title):
        page = QWidget()
        v = QVBoxLayout(page)
        v.setContentsMargins(28, 26, 28, 24)
        v.setSpacing(16)
        v.addWidget(label(title, "h1"))
        return page, v

    def _dashboard(self):
        page, outer = self._page("Dashboard")
        # Header metadata similar to a desktop performance console.
        meta = QHBoxLayout()
        self.system_meta = label("SYSTEM TELEMETRY  ·  Live readings", "cardSub")
        self.score_meta = label("PERFORMANCE SCORE  —", "scoreMeta")
        meta.addWidget(self.system_meta)
        meta.addStretch()
        meta.addWidget(self.score_meta)
        outer.addLayout(meta)

        # Four compact system KPI cards.
        kpis = QGridLayout()
        kpis.setSpacing(12)
        self.kpi_values = {}
        self.kpi_subs = {}
        specs = [
            ("cpu", "CPU USAGE", ACCENT["cpu"]),
            ("ram", "MEMORY", ACCENT["ram"]),
            ("swap", "SWAP", "#F59E0B"),
            ("disk", "DISK I/O", ACCENT["disk"]),
        ]
        for i, (key, title, color) in enumerate(specs):
            box, lay = card(QVBoxLayout, (15, 12, 15, 12))
            top = QHBoxLayout()
            dot = QLabel("●")
            dot.setStyleSheet(f"color:{color};font-size:17px;")
            top.addWidget(dot)
            top.addWidget(label(title, "cardTitle"))
            top.addStretch()
            lay.addLayout(top)
            self.kpi_values[key] = label("Collecting…", "kpiValue")
            self.kpi_subs[key] = label("Waiting for system data", "cardSub")
            lay.addWidget(self.kpi_values[key])
            lay.addWidget(self.kpi_subs[key])
            kpis.addWidget(box, 0, i)
        outer.addLayout(kpis)

        charts = QGridLayout()
        charts.setSpacing(12)
        # CPU trend
        box, lay = card(QVBoxLayout, (16, 12, 16, 12))
        lay.addWidget(label("CPU USAGE", "chartTitle"))
        self.cpu_chart = AreaChart(ACCENT["cpu"])
        self.cpu_chart.setMinimumHeight(180)
        lay.addWidget(self.cpu_chart, 1)
        charts.addWidget(box, 0, 0, 1, 2)
        # Per-core bars
        box, lay = card(QVBoxLayout, (16, 12, 16, 12))
        lay.addWidget(label("CPU THREADS", "chartTitle"))
        self.core_chart = CoreBars()
        lay.addWidget(self.core_chart, 1)
        charts.addWidget(box, 0, 2, 1, 1)
        # RAM trend
        box, lay = card(QVBoxLayout, (16, 12, 16, 12))
        lay.addWidget(label("RAM USAGE", "chartTitle"))
        self.ram_chart = AreaChart(ACCENT["ram"])
        self.ram_chart.setMinimumHeight(145)
        lay.addWidget(self.ram_chart, 1)
        charts.addWidget(box, 1, 0, 1, 2)
        # Swap trend
        box, lay = card(QVBoxLayout, (16, 12, 16, 12))
        lay.addWidget(label("SWAP / PAGE FILE", "chartTitle"))
        self.swap_chart = AreaChart(QColor("#F59E0B"), maxv=100.0)
        self.swap_chart.setMinimumHeight(145)
        lay.addWidget(self.swap_chart, 1)
        charts.addWidget(box, 1, 2, 1, 1)
        charts.setColumnStretch(0, 1)
        charts.setColumnStretch(1, 1)
        charts.setColumnStretch(2, 1)
        outer.addLayout(charts, 1)

        # Keep GPU and temperature visible without displacing the main charts.
        footer = QHBoxLayout()
        self.gpu_meta = label("GPU: collecting…", "footerMetric")
        self.temp_meta = label("TEMPERATURE: collecting…", "footerMetric")
        footer.addWidget(self.gpu_meta)
        footer.addWidget(self.temp_meta)
        footer.addStretch()
        outer.addLayout(footer)

        self.disk_box, self.disk_lay = card(QVBoxLayout, (15, 10, 15, 10))
        self.disk_lay.setSpacing(6)
        self.disk_title = label("STORAGE VOLUMES", "cardTitle")
        self.disk_lay.addWidget(self.disk_title)
        outer.addWidget(self.disk_box)
        self._cpu_history, self._ram_history, self._swap_history = [], [], []
        return page

    def _processes(self):
        page, v = self._page("Processes")
        box, lay = card()
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["PID", "NAME", "CPU %", "MEMORY (MB)"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        lay.addWidget(self.table)
        v.addWidget(box, 1)
        return page

    def _memory(self):
        page, v = self._page("Smart Memory Analyzer")
        v.addWidget(label("Real system measurements · Recorded locally · Exportable CA evidence", "cardSub"))
        row = QHBoxLayout()
        self.memory_stats = {}
        for key, title in (("used", "USED RAM"), ("available", "AVAILABLE RAM"),
                           ("swap", "SWAP / PAGE FILE")):
            box, lay = card()
            self.memory_stats[key] = label("Collecting…", "cardValue")
            lay.addWidget(label(title, "cardTitle"))
            lay.addWidget(self.memory_stats[key])
            row.addWidget(box)
        v.addLayout(row)

        box, lay = card()
        lay.addWidget(label("RAM UTILIZATION · RECORDED SAMPLES", "cardTitle"))
        self.memory_chart = AreaChart(ACCENT["ram"])
        lay.addWidget(self.memory_chart, 1)
        v.addWidget(box, 1)

        controls = QHBoxLayout()
        controls.addWidget(label("High RAM alert threshold (%)", "cardSub"))
        self.ram_threshold = QSpinBox()
        self.ram_threshold.setRange(50, 99)
        self.ram_threshold.setValue(90)
        self.ram_threshold.valueChanged.connect(self._set_ram_threshold)
        controls.addWidget(self.ram_threshold)
        export = QPushButton("Export memory history CSV")
        export.clicked.connect(self._export_memory)
        controls.addWidget(export)
        controls.addStretch()
        v.addLayout(controls)

        box, lay = card()
        lay.addWidget(label("TOP MEMORY-CONSUMING PROCESSES", "cardTitle"))
        self.memory_table = QTableWidget(0, 4)
        self.memory_table.setHorizontalHeaderLabels(["PID", "PROCESS", "RESIDENT RAM (MB)", "MEMORY %"])
        self.memory_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.memory_table.verticalHeader().setVisible(False)
        self.memory_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.memory_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        lay.addWidget(self.memory_table)
        v.addWidget(box, 2)
        return page

    def _set_ram_threshold(self, value):
        self.alerts.t.ram = float(value)

    def _refresh_memory(self):
        if not hasattr(self, "memory_table"):
            return
        samples = self.history.recent_memory(hours=24, limit=500)
        self.memory_chart.set_data([r[1] for r in samples])
        if samples:
            latest = samples[-1]
            self.memory_stats["used"].setText(f"{latest[2]:.2f} / {latest[3]:.2f} GB")
            self.memory_stats["available"].setText(f"{latest[4]:.2f} GB")
            self.memory_stats["swap"].setText(f"{latest[5]:.1f}% · {latest[6]:.2f}/{latest[7]:.2f} GB")
        else:
            self.memory_stats["used"].setText("Waiting for samples")
            self.memory_stats["available"].setText("Waiting for samples")
            self.memory_stats["swap"].setText("Waiting for samples")
        rows = top_processes(15, sort_by="memory")
        self.memory_table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            values = (row["pid"], row["name"], f'{row["mem_mb"]:.1f}', f'{row.get("mem_percent", 0):.2f}%')
            for j, value in enumerate(values):
                self.memory_table.setItem(i, j, QTableWidgetItem(str(value)))

    def _export_memory(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export recorded memory history",
                                              "memory_history.csv", "CSV files (*.csv)")
        if not path:
            return
        try:
            count = self.history.export_memory_csv(path, hours=24)
            QMessageBox.information(self, "Export complete",
                                    f"Exported {count} real recorded samples to:\\n{path}")
        except Exception as exc:
            QMessageBox.critical(self, "Export failed", str(exc))

    def _history(self):
        page, v = self._page("Performance history")
        row = QHBoxLayout()
        row.setSpacing(16)
        self.stats = {}
        for key, title in (("avg_score", "AVG SCORE · 24H"), ("min_score", "LOWEST SCORE"),
                           ("avg_cpu", "AVG CPU"), ("avg_ram", "AVG MEMORY")):
            box, lay = card()
            self.stats[key] = label("–", "cardValue")
            lay.addWidget(label(title, "cardTitle"))
            lay.addWidget(self.stats[key])
            row.addWidget(box)
        v.addLayout(row)
        box, lay = card()
        lay.addWidget(label("SCORE · LAST 60 MINUTES", "cardTitle"))
        self.hist_chart = AreaChart(ACCENT["cpu"])
        lay.addWidget(self.hist_chart, 1)
        v.addWidget(box, 1)
        return page

    def _alerts(self):
        page, v = self._page("Alerts")
        box, lay = card()
        self.alert_list = QListWidget()
        lay.addWidget(self.alert_list)
        v.addWidget(box, 1)
        return page

    # ---------- updates ----------
    def refresh(self):
        s = collect()
        self.alerts.t.ram = float(self.ram_threshold.value()) if hasattr(self, "ram_threshold") else self.alerts.t.ram
        score, parts = compute_score(s)
        self.history.record(s, score)
        c, m, g = s.cpu, s.memory, s.gpu
        # Keep score visible as a small status item rather than a large hero card.
        self.score_meta.setText(f"SCORE  {score:.0f}/100  ·  {grade(score)}")
        worst = min(parts, key=parts.get)
        self.system_meta.setText(f"LIVE SYSTEM TELEMETRY  ·  {c['cores']} cores / {c['threads']} threads")

        self.kpi_values["cpu"].setText(f"{c['percent']:.1f}%")
        self.kpi_subs["cpu"].setText(f"{c['cores']} cores · {c['threads']} logical CPUs")
        self.kpi_values["ram"].setText(f"{m['percent']:.1f}%")
        self.kpi_subs["ram"].setText(f"{m['used_gb']:.2f} / {m['total_gb']:.2f} GB used")
        self.kpi_values["swap"].setText(f"{m.get('swap_percent', 0):.1f}%")
        self.kpi_subs["swap"].setText(f"{m.get('swap_used_gb', 0):.2f} / {m.get('swap_total_gb', 0):.2f} GB")
        self.kpi_values["disk"].setText(f"↓ {s.storage['read_mb_s']:.1f}  ↑ {s.storage['write_mb_s']:.1f} MB/s")
        self.kpi_subs["disk"].setText("Read / write throughput")

        self._cpu_history = (self._cpu_history + [c["percent"]])[-90:]
        self._ram_history = (self._ram_history + [m["percent"]])[-90:]
        self._swap_history = (self._swap_history + [m.get("swap_percent", 0)])[-90:]
        self.cpu_chart.set_data(self._cpu_history)
        self.ram_chart.set_data(self._ram_history)
        self.swap_chart.set_data(self._swap_history)
        self.core_chart.set_values(c.get("per_core", []))

        if g:
            self.gpu_meta.setText(f"GPU  {g['name']}  ·  {g['util']:.0f}%  ·  {g['mem_used_gb']:.1f}/{g['mem_total_gb']:.1f} GB")
        else:
            self.gpu_meta.setText("GPU  No supported NVIDIA GPU data")
        temps = {k: v for k, v in s.temps.items() if v is not None}
        if temps:
            self.temp_meta.setText("TEMPERATURE  " + "  ·  ".join(f"{k.upper()} {v:.0f}°C" for k, v in temps.items()))
        else:
            self.temp_meta.setText("TEMPERATURE  Sensor data unavailable")
        self._update_storage(s.storage)

        for a in self.alerts.check(s):
            item = QListWidgetItem(f"{datetime.fromtimestamp(a.ts):%H:%M:%S}   {a.level.upper()}   {a.message}")
            item.setForeground(QColor("#F87171" if a.level == "critical" else "#FBBF24"))
            self.alert_list.insertItem(0, item)
        if self.pages.currentIndex() == 1:
            self._update_processes()
        if self.pages.currentIndex() == 2:
            self._refresh_memory()

    def _update_storage(self, st):
        self.disk_title.setText(f"STORAGE     ↓ {st['read_mb_s']:.1f} MB/s    ↑ {st['write_mb_s']:.1f} MB/s")
        for p in st["partitions"][:5]:
            if p["mount"] not in self.bars:
                lbl, bar = QLabel(), QProgressBar()
                bar.setTextVisible(False)
                self.disk_lay.addWidget(lbl)
                self.disk_lay.addWidget(bar)
                self.bars[p["mount"]] = (lbl, bar)
            lbl, bar = self.bars[p["mount"]]
            lbl.setText(f"{p['mount']}   {p['used_gb']:.0f} / {p['total_gb']:.0f} GB  ({p['percent']:.0f}%)")
            bar.setValue(int(p["percent"]))

    def _update_processes(self):
        rows = top_processes(15)
        self.table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            for j, val in enumerate((r["pid"], r["name"], f"{r['cpu']:.1f}", f"{r['mem_mb']:.0f}")):
                self.table.setItem(i, j, QTableWidgetItem(str(val)))

    def _refresh_history(self):
        sm = self.history.summary(24)
        self.stats["avg_score"].setText(f"{sm['avg_score']:.0f}")
        self.stats["min_score"].setText(f"{sm['min_score']:.0f}")
        self.stats["avg_cpu"].setText(f"{sm['avg_cpu']:.0f}%")
        self.stats["avg_ram"].setText(f"{sm['avg_ram']:.0f}%")
        self.hist_chart.set_data(self.history.recent_scores(60))


def run():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(STYLE)
    app.setWindowIcon(QIcon(str(ASSETS / "icon.svg")))
    win = MainWindow()
    win.showMaximized()
    sys.exit(app.exec())
