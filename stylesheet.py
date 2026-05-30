##
# @file stylesheet.py
# @brief Global Qt stylesheet for the Aurumveil application.
#
# Defines the visual appearance of all user interface
# components used throughout the application.
#

##
# @brief Global application stylesheet.
#
# Contains the complete Qt Style Sheet (QSS) definition
# used by the graphical user interface.
#
APP_STYLESHEET: str = """
/* ===== GLOBAL ===== */
QWidget {
    color: black;
    background-color: #e6e6e6;
}

QLabel {
    color: #2c2c2c;
}

QScrollArea {
    background-color: transparent;

    border: none;
}

QRadioButton {
    background-color: #e3e3e3;

    border: none;
}


/* ===== LAYOUT ===== */
#AppContainer {
    background-color: #f5f5f5;

    border: 1px solid #c7c7c7;
    border-radius: 18px;
}

#ContentPanel,
#ControlPanel {
    background-color: #f5f5f5;

    border: 1px solid #c3c9d2;
    border-radius: 12px;
}

#ContentBlock {
    background-color: white;

    border: 1px solid #d0d5dd;
    border-radius: 10px;
}


/* ===== CONTROL PANEL ===== */
#ControlPanel QLabel {
    color: #2c3e50;

    font-weight: 600;
}

#ControlPanel QListWidget {
    background-color: white;

    border: 1px solid #c9cfd8;
    border-radius: 8px;
}


/* ===== TEXT ===== */
QLabel#TitleLabel {
    font-weight: bold;
    font-size: 18px;
}

QLabel#StatusLabel {
    padding-left: 2px;
}


/* ===== INPUTS ===== */
QTextEdit {
    color: black;
    background-color: white;

    border-radius: 8px;

    padding: 8px;
}

QListWidget {
    background-color: white;

    border-radius: 8px;

    padding: 6px;
}


/* ===== BUTTONS ===== */
QPushButton#PrimaryButton {
    color: white;
    background-color: #52a52e;

    border: 1px solid #cfcfcf;
    border-radius: 14px;

    padding: 6px 14px;

    font-size: 12px;
}

QPushButton#PrimaryButton:hover,
QPushButton#PrimaryButton:pressed {
    background-color: #9ec44d;
}

QPushButton#PrimaryButton:disabled {
    color: #999999;
    background-color: #e0e0e0;

    border: 1px solid #dddddd;
}


QPushButton#SecondaryButton {
    background-color: white;

    border: 1px solid #cfcfcf;
    border-radius: 14px;

    padding: 6px 14px;
    
    font-size: 12px;
}

QPushButton#SecondaryButton:hover {
    background-color: #f2f4f7;
}

QPushButton#SecondaryButton:pressed {
    background-color: #e0e4ea;
}


QPushButton#AnalyzeButton {
    color: white;
    background-color: #7fa4d1;

    border: 1px solid #aac8eb;
    border-radius: 14px;

    padding: 6px 14px;
    font-size: 12px;
    font-weight: 600;
}

QPushButton#AnalyzeButton:hover {
    background-color: #aac8eb;
    border: 1px solid #d5d0ca;
}

QPushButton#AnalyzeButton:pressed {
    background-color: #d5d0ca;
}


QPushButton#LocateButton {
    color: white;
    background-color: #9ec44d;

    border: 1px solid #b3d56a;
    border-radius: 14px;

    padding: 6px 14px;
    font-size: 12px;
    font-weight: 600;
}

QPushButton#LocateButton:hover {
    background-color: #b3d56a;
    border: 1px solid #d5d0ca;
}

QPushButton#LocateButton:pressed {
    background-color: #d5d0ca;
}

QPushButton#LocateButton:disabled {
    color: #999999;
    background-color: #e0e0e0;

    border: 1px solid #cfcfcf;
}


QPushButton#ExportButton {
    color: white;
    background-color: #ea9b20;

    border: 1px solid #f7c76b;
    border-radius: 14px;

    padding: 6px 14px;
    font-size: 12px;
    font-weight: 600;
}

QPushButton#ExportButton:hover {
    background-color: #f7c76b;
    border: 1px solid #d5d0ca;
}

QPushButton#ExportButton:pressed {
    background-color: #d5d0ca;
}


QPushButton#SegmentButton {
    color: black;
    background-color: white;

    border: 1px solid #cfcfcf;
    border-radius: 0;

    padding: 6px 11px;

    font-size: 12px;
}

QPushButton#SegmentButton:first {
    border-top-left-radius: 8px;
    border-bottom-left-radius: 8px;
}

QPushButton#SegmentButton:last {
    border-top-right-radius: 8px;
    border-bottom-right-radius: 8px;
}

QPushButton#SegmentButton:hover {
    color: white;
    background-color: #cfcfcf;

    border: 1px solid white;
}

QPushButton#SegmentButton:checked {
    color: white;
    background-color: #6578b4;

    border: 1px solid #7fa4d1;
}

QPushButton#SegmentButton:checked:hover {
    color: white;
    background-color: #7fa4d1;

    border: 1px solid #6578b4;
}


/* ===== STATES ===== */
QTableWidget[invalid="true"] {
    background-color: #ffe0e0;
}

QPushButton:disabled {
    color: #9e9e9e;
    background-color: #e0e0e0;

    border: 1px solid #cfcfcf;
}

QGroupBox#SegmentBox[active="false"] {
    color: #8a8a8a;
    background-color: #f2f2f2;
}

QGroupBox#SegmentBox[active="false"] QRadioButton {
    color: #cfcfcf;
    background-color: #efefef;
}
"""