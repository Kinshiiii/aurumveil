# ===== APP THEME =====
APP_THEME: str = """
/* ===== GLOBAL ===== */
QWidget {
    color: #000;
    background: #e6e6e6;
}

QLabel {
    color: #2c2c2c;
}

QScrollArea {
    background: none;
    border: none;
}


/* ===== INPUTS ===== */
QTextEdit {
    background: white;
    color: black;
    border-radius: 8px;
    padding: 8px;
}

QListWidget {
    background: white;
    border-radius: 8px;
    padding: 6px;
}


/* ===== LAYOUT ===== */
#Background {
    background: #f5f5f5;
    border-radius: 18px;
    border: 1px solid #c7c7c7;
}

#LeftPanel,
#RightPanel {
    background: #f5f5f5;
    border-radius: 12px;
    border: 1px solid #c3c9d2;
}

#InnerBlock {
    background: white;
    border-radius: 10px;
    border: 1px solid #d0d5dd;
}


/* ===== RIGHT PANEL ===== */
#RightPanel QLabel {
    color: #2c3e50;
    font-weight: 600;
}

#RightPanel QListWidget {
    background: white;
    border: 1px solid #c9cfd8;
    border-radius: 8px;
}


/* ===== BUTTONS ===== */
QPushButton#ActionButton {
    background-color: white;
    border-radius: 14px;
    padding: 6px 14px;
    border: 1px solid #cfcfcf;
}

QPushButton#ActionButton:hover {
    background-color: #f2f4f7;
}

QPushButton#ActionButton:pressed {
    background-color: #e0e4ea;
}


/* ===== PRIMARY BUTTON ===== */
QPushButton#PrimaryButton {
    background-color: #4CAF50;
    color: white;
    border-radius: 14px;
    padding: 6px 14px;
    border: 1px solid #4CAF50;
}

QPushButton#PrimaryButton:hover {
    background-color: #43a047;
}

QPushButton#PrimaryButton:pressed {
    background-color: #388e3c;
}

QPushButton#PrimaryButton:disabled {
    background-color: #e0e0e0;
    color: #999999;
    border: 1px solid #dddddd;
}


/* ===== SEGMENT CONTROL ===== */
QPushButton#SegmentButton {
    background-color: white;
    border: 1px solid #cfcfcf;
    padding: 6px 12px;
    border-radius: 0px;
}

QPushButton#SegmentButton:first {
    border-top-left-radius: 8px;
    border-bottom-left-radius: 8px;
}

QPushButton#SegmentButton:last {
    border-top-right-radius: 8px;
    border-bottom-right-radius: 8px;
}

QPushButton#SegmentButton:checked {
    background-color: #4CAF50;
    color: white;
    border: 1px solid #4CAF50;
}

QPushButton#SegmentButton:hover {
    background-color: #f2f4f7;
}


/* ===== DISABLED ===== */
QPushButton:disabled {
    background-color: #e0e0e0;
    color: #9e9e9e;
    border: 1px solid #cfcfcf;
}


/* ===== TEXT ===== */
QLabel#TitleLabel {
    font-size: 18px;
    font-weight: bold;
}
"""