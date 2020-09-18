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
from PyQt5 import QtWidgets

from .. import icons, IS_WIN


class SquareButton(QtWidgets.QToolButton):
    """A button whose width is fixed to its height, so that it always remains square, while adjusting its side length
    to match its layout."""

    def __init__(self, text='', tooltip='', icon=None, edge=0, parent=None):
        """Initialise the widget with parameters passed to constructor."""
        super().__init__(parent)
        self.setText(text)
        self.setToolTip(tooltip)
        if icon:
            self.setIcon(icon)

        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum))
        self.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self.setStyleSheet('QToolButton::menu-indicator { width: 0; image: none }')  # hide dropdown arrow indicator
        if edge:
            self.setMinimumSize(edge, edge)

        if IS_WIN:  # symbols are weirdly small in Segoe UI
            self.setStyleSheet(self.styleSheet() + 'QToolButton { font-size: 18px }')

    def resizeEvent(self, event):
        """Handle a resize event so that the widget stays square."""
        self.setFixedWidth(self.height())


class UniverseMapButton(SquareButton):
    """A square push button displaying the "universe map" symbol."""

    def __init__(self, parent=None):
        """Initialise a SquareButton with some default values."""
        super().__init__(tooltip='Open universe map', icon=icons.universemap, parent=parent)
