from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt, pyqtSignal


class ColorButton(QtWidgets.QPushButton):

    colorChanged = pyqtSignal(str)

    def __init__(self, *args):
        super(ColorButton, self).__init__(*args)

        self._color = None
        self.setMaximumWidth(32)
        self.pressed.connect(self.onColorPicker)

    def setColor(self, color):
        if color != self._color:
            self._color = color
            self.colorChanged.emit(str(self._color))

        if self._color:
            self.setStyleSheet("QWidget { background-color: %s }" % self._color)
        else:
            self.setStyleSheet("")

    def color(self):
        return self._color

    def onColorPicker(self):

        dlg = QtWidgets.QColorDialog()
        # dlg.setStyleSheet("")
        if self._color:
            dlg.setCurrentColor(QtGui.QColor(self._color))

        if dlg.exec_():
            self.setColor(dlg.currentColor().name())

    def mousePressEvent(self, e):
        if e.button() == Qt.RightButton:
            self.setColor(None)

        return super(ColorButton, self).mousePressEvent(e)