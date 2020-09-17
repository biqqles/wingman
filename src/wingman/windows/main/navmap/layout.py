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

This file defines the layout of the Navmap tab.
"""
from PyQt5 import QtCore, QtGui, QtWidgets

from ....widgets import buttons, mapview, infocardview
from .... import icons, IS_WIN


class NavmapTab(QtWidgets.QWidget):
    """Defines the layout of the 'Navmap' tab."""
    title = 'Navmap'
    icon = icons.navmap

    def __init__(self, parent: QtWidgets.QTabWidget):
        super().__init__(parent)
        self.mainLayout = QtWidgets.QGridLayout(self)
        self.navmap = mapview.MapView(self)
        self.navmap.setMinimumSize(QtCore.QSize(512, 512))
        self.navmap.setSizePolicy(
            QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

        self.leftLayout = QtWidgets.QVBoxLayout()
        self.leftLayout.addWidget(self.navmap)

        self.mainLayout.addLayout(self.leftLayout, 0, 0)

        self.rightLayout = QtWidgets.QVBoxLayout()
        self.selectionLayout = QtWidgets.QHBoxLayout()

        self.followRadioButton = QtWidgets.QRadioButton('Follow', self)
        self.followRadioButton.setToolTip(
            'If toggled, the navmap will automatically switch to systems as you enter them')
        self.followRadioButton.setChecked(False)
        self.followRadioButton.setEnabled(False)

        self.selectionLayout.addWidget(self.followRadioButton)

        self.gotoRadioButton = QtWidgets.QRadioButton('Show: ', self)
        self.gotoRadioButton.setChecked(True)
        self.selectionLayout.addWidget(self.gotoRadioButton)

        self.searchEdit = QtWidgets.QLineEdit(self)
        searchFont = self.searchEdit.font()
        searchFont.setBold(True)
        self.searchEdit.setFont(searchFont)
        self.searchEdit.setPlaceholderText('Enter a system or base')
        self.searchEdit.setMinimumHeight(30)
        self.selectionLayout.addWidget(self.searchEdit)

        self.universeButton = buttons.UniverseMapButton(self)
        self.selectionLayout.addWidget(self.universeButton)

        self.rightLayout.addLayout(self.selectionLayout)

        self.infocard = infocardview.InfocardView(self)
        self.rightLayout.addWidget(self.infocard)

        self.mainLayout.addLayout(self.rightLayout, 0, 1)
