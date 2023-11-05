import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel

class AddRemoveButtons(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()

        self.add_button = QPushButton("+")
        self.add_button.clicked.connect(self.addRemoveButton)
        self.layout.addWidget(self.add_button)

        self.setLayout(self.layout)

    def addRemoveButton(self):
        button_layout = QHBoxLayout()
        remove_button = QPushButton("-")
        exclamation_button = QPushButton("!")

        # ! 버튼 클릭 시 현재 인덱스 출력
        exclamation_button.clicked.connect(lambda: self.showIndex(button_layout))

        remove_button.clicked.connect(lambda: self.removeButton(button_layout))
        button_layout.addWidget(remove_button)
        button_layout.addWidget(exclamation_button)

        # ! 버튼 클릭 시 현재 인덱스 출력
        self.layout.addLayout(button_layout)

    def removeButton(self, button_layout):
        for i in reversed(range(self.layout.count())):
            layout_item = self.layout.itemAt(i)
            layout = layout_item.layout()
            if layout is not None and layout == button_layout:
                for j in reversed(range(layout.count())):
                    widget = layout.itemAt(j).widget()
                    if widget:
                        widget.deleteLater()
                break

    def showIndex(self, button_layout):
        index = self.layout.indexOf(button_layout)
        print("Clicked on index:", index)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        add_remove_buttons = AddRemoveButtons()
        self.setCentralWidget(add_remove_buttons)

        self.setWindowTitle("Add, Remove, and Show Index Example")
        self.setGeometry(100, 100, 400, 200)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec())
