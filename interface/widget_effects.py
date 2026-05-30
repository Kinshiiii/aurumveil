##
# @file widget_effects.py
# @brief Utility functions for Qt widget visual effects.
#
# Provides reusable helpers responsible for enhancing
# the appearance of user interface components.
#

from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QGraphicsDropShadowEffect,
    QWidget,
)


##
# @brief Applies a drop shadow effect to a widget.
#
# Creates and configures a QGraphicsDropShadowEffect
# instance and attaches it to the specified widget
# to improve visual depth and separation from the
# background.
#
# @param widget
# Target widget that will receive the shadow effect.
#
# @return None
#
def apply_shadow(widget: QWidget) -> None:

    shadow: QGraphicsDropShadowEffect = (
        QGraphicsDropShadowEffect()
    )

    shadow.setBlurRadius(18)
    shadow.setOffset(0, 4)
    shadow.setColor(QColor(0, 0, 0, 60))

    widget.setGraphicsEffect(shadow)