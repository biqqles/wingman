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
from typing import List, Tuple

from PyQt5 import QtCore, QtGui, QtWidgets


class ScrollableList(QtWidgets.QListWidget):
    def __init__(self, entries: List[str]):
        super().__init__()
        self.addItems(entries)
        self.setCurrentRow(0)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.setMaximumWidth(self.sizeHintForColumn(0) + 10)  # fit width to contents (+ margin)

    def wheelEvent(self, event: QtGui.QWheelEvent):
        """Allow selected item to be scrolled with the mouse wheel."""
        degrees = event.angleDelta().y() // 8  # angle delta is in eighths of a degree
        steps = degrees // 15
        for _ in range(abs(steps)):
            new_index = self.currentRow() + (1 if steps < 0 else -1)
            if -1 < new_index < self.count():  # do not wrap around
                self.setCurrentRow(new_index)
            else:
                break
        event.accept()
