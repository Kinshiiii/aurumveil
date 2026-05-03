from PySide6.QtWidgets import QGraphicsDropShadowEffect, QWidget
from PySide6.QtGui import QColor


# ===== SHADOW UTILS =====
def add_shadow(widget: QWidget) -> None:
    shadow_effect = QGraphicsDropShadowEffect()

    shadow_effect.setBlurRadius(18)
    shadow_effect.setOffset(0, 4)
    shadow_effect.setColor(QColor(0, 0, 0, 60))

    widget.setGraphicsEffect(shadow_effect)