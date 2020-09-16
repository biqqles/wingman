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
from typing import Callable, Any
import os

from PyQt5 import QtWidgets


class PathEdit(QtWidgets.QWidget):
    """A widget that allows the user to select a path, consisting of a line edit and a button to open a file picker.
    The line edit changes colour to indicate whether the path is valid or invalid."""
    def __init__(self, initialPath: str, validityCondition: Callable[[Any], bool] = lambda path: True):
        super().__init__()
        self.validPathCase = validityCondition

        self.mainLayout = QtWidgets.QHBoxLayout()
        self.setLayout(self.mainLayout)

        self.lineEdit = QtWidgets.QLineEdit()
        self.lineEdit.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Preferred)
        self.lineEdit.setMinimumWidth(300)
        self.lineEdit.textChanged.connect(self.onTextChanged)
        self.lineEdit.setText(initialPath)
        self.mainLayout.addWidget(self.lineEdit)

        self.browseButton = QtWidgets.QPushButton('Browse')
        self.browseButton.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        self.browseButton.clicked.connect(self.onBrowseButtonClicked)
        self.mainLayout.addWidget(self.browseButton)

        self.updateDisplayValidity()

    def onTextChanged(self, text: str):
        """Handle the text box's text being changed."""
        self.updateDisplayValidity()

    def onBrowseButtonClicked(self):
        """Open a browse dialogue which sets the path."""
        path = QtWidgets.QFileDialog.getExistingDirectory(caption='Choose folder', directory=self.lineEdit.text(),
                                                          options=QtWidgets.QFileDialog.ShowDirsOnly |
                                                          QtWidgets.QFileDialog.DontUseNativeDialog)
        if path:  # i.e. if not cancelled
            self.lineEdit.setText(path)

    def updateDisplayValidity(self):
        """Update the visuals of the PathEdit to indicate its path's current validity."""
        self.colourCode(self.isValidPath())

    def isValidPath(self) -> bool:
        """Returns whether the currently entered path is valid."""
        return self.validatePath(self.lineEdit.text())

    def validatePath(self, path) -> bool:
        """Verify a path looks correct. Some checks are always done and additional checks can be defined by defining
        `condition`.
        Todo: maybe check if directory?"""
        return os.path.exists(path) and self.validPathCase(path)

    def colourCode(self, valid):
        """Colour code the line edit to indicate whether the path is valid or invalid."""
        self.setStyleSheet('QLineEdit {{ background-color: {} }}'.format('#22bb45' if valid else '#dc143c'))
