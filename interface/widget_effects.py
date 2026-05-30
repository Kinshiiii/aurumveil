from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QGraphicsDropShadowEffect,
    QWidget,
)


# ===== SHADOW UTILS =====
def apply_shadow(widget: QWidget) -> None:

    shadow: QGraphicsDropShadowEffect = (
        QGraphicsDropShadowEffect()
    )

    shadow.setBlurRadius(18)
    shadow.setOffset(0, 4)
    shadow.setColor(QColor(0, 0, 0, 60))

    widget.setGraphicsEffect(shadow)