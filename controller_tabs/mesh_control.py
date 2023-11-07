from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem, QScrollArea, QVBoxLayout, QWidget
from PySide6.QtCore import QSize

from gui_components.widgets import *

from manager import RenderManager as RM

class MeshController(QWidget):
    def __init__(self, *args, **kargs):
        super(MeshController, self).__init__( *args, **kargs)
        self.initUI()

    def initUI(self):
        # 스크롤 영역 생성
        scroll_area = QScrollArea(self)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(scroll_area)

        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["Skeleton", ""])
        self.tree_widget.setUniformRowHeights(True)

        # 스크롤 영역에 배치될 위젯 생성
        self.scroll_widget = QWidget()
        self.scroll_widget_layout = QVBoxLayout(self.scroll_widget)

        # 스크롤 영역 설정
        scroll_area.setWidget(self.scroll_widget)
        scroll_area.setWidgetResizable(True)

        scroll_area.setStyleSheet("QScrollArea { border: none; background: none; }")


    def loadMesh(self):
        self.tree_widget.clear()

        for root in RM.Animation.roots:
            self.loadTreeMesh(RM.Animation.skeletons[root], self.tree_widget)

        self.scroll_widget_layout.addWidget(self.tree_widget)
        self.tree_widget.expandAll()


    def loadTreeMesh(self, skeleton, parent):
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
            self.loadTreeMesh(child, tree_item)


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