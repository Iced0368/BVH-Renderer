import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QScrollArea, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFrame, QColorDialog
from PySide6.QtGui import QColor

class ColorLabel(QHBoxLayout):
    def __init__(self, label_text):
        super().__init__()

        self.label = QLabel(label_text)
        self.color_frame = QFrame()
        self.color_frame.setFixedSize(20, 20)
        self.color_frame.setStyleSheet("background-color: red;")

        self.addWidget(self.label)
        self.addWidget(self.color_frame)

        self.color_frame.mousePressEvent = self.changeColor

    def changeColor(self, event):
        color_dialog = QColorDialog()
        color = color_dialog.getColor()
        if color.isValid():
            self.color_frame.setStyleSheet(f"background-color: {color.name()};")

class ScrollAreaDemo(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Scroll Area Demo")
        self.setGeometry(100, 100, 400, 300)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # 스크롤 영역 생성
        self.scroll_area = QScrollArea()
        central_widget.setLayout(QVBoxLayout())
        central_widget.layout().addWidget(self.scroll_area)

        # 스크롤 영역에 배치될 위젯 생성
        self.scroll_widget = QWidget()
        self.scroll_widget_layout = QVBoxLayout(self.scroll_widget)

        # 스크롤 영역에 추가할 커스텀 라벨들
        self.addColorLabels()

        # 스크롤 영역 설정
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)  # 스크롤 영역의 크기를 내부 위젯에 맞게 조절

    def addColorLabels(self):
        # 스크롤 영역에 커스텀 라벨들 추가
        for i in range(50):
            label = ColorLabel(f"Label {i}")
            self.scroll_widget_layout.addLayout(label)

def main():
    app = QApplication(sys.argv)
    window = ScrollAreaDemo()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
