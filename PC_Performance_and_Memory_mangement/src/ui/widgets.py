from PySide6.QtCore import Property, QEasingCurve, QPointF, QPropertyAnimation, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget


class RingGauge(QWidget):
    """Animated circular gauge with a soft glow."""

    def __init__(self, label="", color="#7C5CFF", unit="%", parent=None):
        super().__init__(parent)
        self._v, self._label, self._unit = 0.0, label, unit
        self._color = QColor(color)
        self._anim = QPropertyAnimation(self, b"value", self)
        self._anim.setDuration(700)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)
        self.setMinimumSize(110, 110)

    def _get(self):
        return self._v

    def _set(self, v):
        self._v = v
        self.update()

    value = Property(float, _get, _set)

    def animate_to(self, v, color=None):
        if color:
            self._color = QColor(color)
        self._anim.stop()
        self._anim.setStartValue(self._v)
        self._anim.setEndValue(float(v))
        self._anim.start()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        side = min(self.width(), self.height()) - 24
        r = QRectF((self.width() - side) / 2, (self.height() - side) / 2, side, side)
        w = max(8, side / 11)
        span = -int(360 * 16 * max(0.0, min(self._v, 100.0)) / 100)
        p.setPen(QPen(QColor(255, 255, 255, 16), w, Qt.SolidLine, Qt.RoundCap))
        p.drawArc(r, 0, 360 * 16)
        glow = QColor(self._color)
        glow.setAlpha(45)
        p.setPen(QPen(glow, w + 8, Qt.SolidLine, Qt.RoundCap))
        p.drawArc(r, 90 * 16, span)
        p.setPen(QPen(self._color, w, Qt.SolidLine, Qt.RoundCap))
        p.drawArc(r, 90 * 16, span)
        f = QFont(p.font())
        f.setPixelSize(int(side * 0.28))
        f.setWeight(QFont.DemiBold)
        p.setFont(f)
        p.setPen(QColor("#F5F7FF"))
        p.drawText(self.rect().adjusted(0, 0, 0, -int(side * 0.08)), Qt.AlignCenter, f"{self._v:.0f}{self._unit}")
        f.setPixelSize(max(9, int(side * 0.085)))
        f.setWeight(QFont.Normal)
        p.setFont(f)
        p.setPen(QColor("#8B93B5"))
        p.drawText(self.rect().adjusted(0, int(side * 0.36), 0, 0), Qt.AlignHCenter | Qt.AlignVCenter, self._label)


class AreaChart(QWidget):
    """Smooth gradient-filled line chart, right-aligned to a sliding window."""

    def __init__(self, color="#7C5CFF", maxv=100.0, window=90, parent=None):
        super().__init__(parent)
        self.color, self.maxv, self.window, self.data = QColor(color), maxv, window, []
        self.setMinimumHeight(60)

    def push(self, v):
        self.data = (self.data + [v])[-self.window:]
        self.update()

    def set_data(self, values):
        self.data, self.window = list(values), max(len(values), 2)
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        p.setPen(QPen(QColor(255, 255, 255, 12), 1))
        for f in (0.25, 0.5, 0.75):
            p.drawLine(0, int(h * f), w, int(h * f))
        if len(self.data) < 2:
            return
        step = w / (self.window - 1)
        n = len(self.data)
        pts = [QPointF(w - (n - 1 - i) * step, h - 3 - min(v, self.maxv) / self.maxv * (h - 8))
               for i, v in enumerate(self.data)]
        path = QPainterPath(pts[0])
        for a, b in zip(pts, pts[1:]):
            mid = (a.x() + b.x()) / 2
            path.cubicTo(mid, a.y(), mid, b.y(), b.x(), b.y())
        fill = QPainterPath(path)
        fill.lineTo(pts[-1].x(), h)
        fill.lineTo(pts[0].x(), h)
        fill.closeSubpath()
        g = QLinearGradient(0, 0, 0, h)
        top = QColor(self.color)
        top.setAlpha(100)
        bottom = QColor(self.color)
        bottom.setAlpha(0)
        g.setColorAt(0, top)
        g.setColorAt(1, bottom)
        p.fillPath(fill, g)
        p.setPen(QPen(self.color, 2.2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.drawPath(path)


class MetricCard(QFrame):
    def __init__(self, title, color, maxv=100.0):
        super().__init__()
        self.setObjectName("card")
        v = QVBoxLayout(self)
        v.setContentsMargins(20, 16, 20, 14)
        v.setSpacing(2)
        self.title, self.value, self.sub = QLabel(title), QLabel("–"), QLabel("")
        self.title.setObjectName("cardTitle")
        self.value.setObjectName("cardValue")
        self.sub.setObjectName("cardSub")
        self.chart = AreaChart(color, maxv)
        for wdg in (self.title, self.value, self.sub):
            v.addWidget(wdg)
        v.addWidget(self.chart, 1)

    def update_metric(self, value_text, sub_text, chart_value=None):
        self.value.setText(value_text)
        self.sub.setText(sub_text)
        if chart_value is not None:
            self.chart.push(chart_value)


class CoreBars(QWidget):
    """Compact per-logical-CPU utilization bar chart."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.values = []
        self.setMinimumHeight(150)

    def set_values(self, values):
        self.values = [max(0.0, min(100.0, float(v))) for v in values]
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        left, right, top, bottom = 26, 8, 12, 24
        plot_h = max(1, h - top - bottom)
        plot_w = max(1, w - left - right)
        p.setPen(QPen(QColor(255, 255, 255, 22), 1))
        for pct in (0, 25, 50, 75, 100):
            y = top + plot_h - plot_h * pct / 100
            p.drawLine(left, int(y), w-right, int(y))
            p.setPen(QColor("#778398"))
            p.drawText(0, int(y+4), 22, 12, Qt.AlignRight, str(pct))
            p.setPen(QPen(QColor(255, 255, 255, 22), 1))
        if not self.values:
            return
        gap = 5
        bw = max(4, (plot_w - gap*(len(self.values)-1)) / len(self.values))
        for i, val in enumerate(self.values):
            x = left + i*(bw+gap)
            bh = plot_h * val/100
            rect = QRectF(x, top + plot_h - bh, bw, bh)
            color = QColor("#8B5CF6" if val < 80 else "#F59E0B")
            p.setPen(Qt.NoPen)
            p.setBrush(color)
            p.drawRoundedRect(rect, 2, 2)
            p.setPen(QColor("#A8B2C4"))
            if bw >= 13:
                p.drawText(QRectF(x-2, h-bottom+4, bw+4, 16), Qt.AlignHCenter, f"C{i+1}")
