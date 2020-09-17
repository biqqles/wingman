"""
Copyright © 2016-2017, 2020 biqqles.

This file is part of Wingman.

Wingman is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Wingman is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Wingman.  If not, see <http://www.gnu.org/licenses/>.
"""
from PyQt5 import QtCore, QtGui, QtWidgets

from .. import app


class InfocardView(QtWidgets.QTextEdit):
    """A widget configured to display HTML-formatted infocards."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setReadOnly(True)

    def contextMenuEvent(self, event):
        """Show a context menu containing an action which copies the selected text to the clipboard, or the entire
        card if there isn't any."""
        text = self.textCursor().selectedText() or self.toPlainText()

        menu = QtWidgets.QMenu()
        copy = menu.addAction('Copy')
        copy.setIcon(QtGui.QIcon.fromTheme('edit-copy'))
        copy.setShortcut('Ctrl+C')
        copy.triggered.connect(lambda: app.clipboard().setText(text))

        menu.exec(QtGui.QCursor.pos())
