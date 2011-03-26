from PyQt4 import QtGui
from PyQt4.QtGui import QDialog, QHBoxLayout, QTextEdit

class ConsoleDialog(QDialog):
    def __init__(self, stream=None):
        QDialog.__init__(self)
        self.stream = stream
        self.setWindowTitle('Console Messages')
        self.layout=QHBoxLayout(self)
        self.layout.setSpacing(6)
        self.layout.setMargin(11)
        self.edit = QTextEdit(self)
        self.edit.setReadOnly(True)
        self.layout.addWidget(self.edit)
        self.resize(650,250)

    def write(self, msg):
        self.edit.moveCursor(QtGui.QTextCursor.End)
        self.edit.insertPlainText(msg)
        if self.stream: self.stream.write(msg)
