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

This file defines the interface of the application's main window.
"""
from PyQt5 import QtCore, QtWidgets
from ... import IS_WIN
if IS_WIN:
    import flair


class FlairBanner(QtWidgets.QLabel):
    """A banner label which displays live information provided by flair."""
    def __init__(self, window: QtWidgets.QMainWindow):
        super().__init__(parent=window)
        self.window = window
        self.setTextFormat(QtCore.Qt.RichText)
        self.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)

        if IS_WIN:
            self.timer = QtCore.QTimer(self)
            self.timer.setInterval(self.UPDATE_INTERVAL)
            self.timer.timeout.connect(self.updateContents)
            self.timer.start()

        self.updateContents()
        self.updatePosition()

    def updateContents(self):
        """Update the contents of the banner, using its template."""
        try:
            if not IS_WIN or not flair.state.running:
                self.hide()
            else:
                self.setText(self.TEMPLATE.format(flair.state.name, flair.state.system, flair.state.credits or 0))
                self.show()
        except AttributeError:  # flair has not been initialised yet
            self.hide()
            
    def updatePosition(self):
        """Update the position of the banner so that it "sticks" to the top right of the window."""
        tabBarBottom = self.window.tw.tabBar().tabRect(0).bottom()
        self.setFixedWidth(self.window.width() // 2)
        self.move(self.window.width() - self.X_OFFSET - self.width(), tabBarBottom - self.Y_OFFSET)

    X_OFFSET = 10  # offset from edge of screen
    Y_OFFSET = 4  # offset from top of tab widget
    UPDATE_INTERVAL = 1500  # ms
    TEMPLATE = ('&nbsp;' * 6).join(('Character: <i>{}</i>', 'System: <i>{}</i>', 'Credits: <i>${:,}</i>'))
