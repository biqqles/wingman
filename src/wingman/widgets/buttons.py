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


class SquareButton(QtWidgets.QPushButton):
    """A button whose width is fixed to its height, so that it expands to the maximum possible size while remaining
    square. """

    def __init__(self, text='', tooltip='', icon=None, dropdown=False, edge=36, parent=None):
        """Initialise the widget with parameters passed to constructor."""
        super().__init__()
        self.setText(text)
        self.setToolTip(tooltip)
        if icon:
            self.setIcon(icon)
        self.setParent(parent)

        policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.setSizePolicy(policy)
        self.setMinimumSize(edge, edge)

        if IS_WIN:  # symbols are weirdly small in Segoe UI
            self.setStyleSheet('QPushButton {font-size: 18px;}')

        if dropdown:
            # hide dropdown arrow indicator
            self.setStyleSheet('QPushButton { padding-right: -0.5px } QPushButton::menu-indicator { image: none }')

    def resizeEvent(self, event):
        """Handle a resize event so that the widget stays square."""
        self.setFixedWidth(self.height())


class UniverseMapButton(SquareButton):
    """A square push button displaying the "universe map" symbol."""

    def __init__(self, parent=None):
        """Initialise a SquareButton with some default values."""
        super().__init__(icon=icons.universemap, tooltip='Open universe map', parent=parent)
        # self.setFixedHeight(QtWidgets.QComboBox().height())