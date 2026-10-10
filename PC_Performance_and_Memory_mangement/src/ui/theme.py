ACCENT = {"cpu": "#7C5CFF", "ram": "#22D3EE", "gpu": "#F472B6", "temp": "#FBBF24", "disk": "#34D399"}


def status_color(score: float) -> str:
    return "#34D399" if score >= 75 else "#FBBF24" if score >= 55 else "#F87171"


STYLE = """
* { font-family: 'Segoe UI','Inter','SF Pro Display','Helvetica Neue',sans-serif; color:#E8EBFA; }
QMainWindow, QWidget#root { background:#090B10; }
QLabel { background:transparent; }
#sidebar { background:#0D1118; border-right:1px solid rgba(255,255,255,0.06); }
#logo { font-size:18px; font-weight:700; }
QPushButton#nav { text-align:left; padding:11px 14px; border:none; border-radius:12px;
    color:#8B93B5; font-size:14px; background:transparent; }
QPushButton#nav:hover { background:rgba(255,255,255,0.05); color:#FFFFFF; }
QPushButton#nav:checked { background:rgba(139,92,246,0.20); color:#FFFFFF; font-weight:600; }
#card { background:#111720; border:1px solid #252D39; border-radius:10px; }
#h1 { font-size:23px; font-weight:700; }
#cardTitle { font-size:11px; color:#8B93B5; font-weight:600; letter-spacing:1.5px; }
#cardValue { font-size:34px; font-weight:700; }
#cardSub { font-size:12px; color:#8B93B5; }
#grade { font-size:24px; font-weight:700; }
QProgressBar { background:rgba(255,255,255,0.07); border:none; border-radius:5px; max-height:10px; }
QProgressBar::chunk { border-radius:5px;
    background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #34D399,stop:1 #22D3EE); }
QTableWidget { background:transparent; border:none; font-size:13px;
    selection-background-color:rgba(124,92,255,0.22); }
QHeaderView::section { background:transparent; border:none; color:#8B93B5;
    padding:8px; font-size:11px; font-weight:600; }
QListWidget { background:transparent; border:none; font-size:13px; outline:0; }
QListWidget::item { padding:10px 12px; margin:3px 0; border-radius:10px; background:rgba(255,255,255,0.04); }
"""

STYLE += """
#kpiValue { font-size:23px; font-weight:700; color:#F1F5F9; }
#chartTitle { font-size:12px; color:#CBD5E1; font-weight:700; letter-spacing:1px; }
#scoreMeta { font-size:11px; color:#9CA3AF; font-weight:600; }
#footerMetric { font-size:11px; color:#A9B4C4; padding:4px 2px; }
QPushButton { background:#171F2B; border:1px solid #2B3544; border-radius:6px; padding:8px 12px; }
QPushButton:hover { background:#202B3A; }
QSpinBox { background:#111720; border:1px solid #2B3544; padding:4px; border-radius:4px; }
QTableWidget { alternate-background-color:#111720; }
"""
