from typing import Optional
from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem, QScrollArea, QVBoxLayout, QWidget
from PySide6.QtCore import QSize

from gui_components.widgets import *

from manager import RenderManager as RM


class ObjectWidget(QWidget):
    def __init__(self, object) -> None:
        super().__init__()
        self.object = object

    


class MeshController(QWidget):
    def __init__(self, *args, **kargs):
        super(MeshController, self).__init__( *args, **kargs)
        self.initUI()

    def initUI(self):
        # 스크롤 영역 생성
        scroll_area = QScrollArea(self)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(scroll_area)

        # 스크롤 영역에 배치될 위젯 생성
        self.scroll_widget = QWidget()
        self.scroll_widget_layout = QVBoxLayout(self.scroll_widget)

        # 스크롤 영역 설정
        scroll_area.setWidget(self.scroll_widget)
        scroll_area.setWidgetResizable(True)

        scroll_area.setStyleSheet("QScrollArea { border: none; background: none; }")


    def clearWidgets(self):
        layout = self.scroll_widget_layout
        while layout.count() > 0:
            item = layout.takeAt(0)  # 인덱스 0에 있는 위젯 가져오기
            widget = item.widget()  # 위젯 가져오기
            if widget:
                widget.deleteLater()  # 위젯 제거
            else:
                layout.removeItem(item)

    def loadAnimationMesh(self):
        self.clearWidgets()
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["Skeleton", ""])
        self.tree_widget.setUniformRowHeights(True)

        for root in RM.Animation.roots:
            self.loadAnimationTree(RM.Animation.skeletons[root], self.tree_widget)

        self.scroll_widget_layout.addWidget(self.tree_widget)
        self.tree_widget.expandAll()


    def loadAnimationTree(self, skeleton, parent):
        tree_item = QTreeWidgetItem(parent)
        tree_item.setSizeHint(0, QSize(0, 25))
        tree_item.setSizeHint(1, QSize(0, 25))

        label = CheckboxLabel(None, f"{skeleton.name}:")
                
        label.checkbox.stateChanged.connect(lambda state, name=skeleton.name: self.onCheckboxStateChanged(state, name))
        label.layout().setContentsMargins(0, 0, 0, 2)

        self.tree_widget.setItemWidget(tree_item, 0, label)

        colorbox = ColorBox(color=QColor(255*skeleton.color[0], 255*skeleton.color[1], 255*skeleton.color[2]))
        colorbox.colorChanged.connect(lambda color, name=skeleton.name: self.onColorChanged(color, name))

        self.tree_widget.setItemWidget(tree_item, 1, colorbox)
        
        for child in skeleton.children:
            self.loadAnimationTree(child, tree_item)


    def onColorChanged(self, color, name):
        Animation = RM.Animation
        for skeleton in Animation.skeletons:
            if name == skeleton.name:
                skeleton.color = (color.red() / 255, color.green() / 255, color.blue() / 255)
                
    def onCheckboxStateChanged(self, state, name):
        Animation = RM.Animation
        for skeleton in Animation.skeletons:
            if name == skeleton.name:
                def _func(skeleton=skeleton):
                    skeleton.enable_mesh = not skeleton.enable_mesh
                RM.execQueue.put(_func)

    def resizeEvent(self, event):
        width = event.size().width()
        if self.tree_widget is not None:
            self.tree_widget.setColumnWidth(0, width-85)