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
from PyQt5 import QtCore, QtWidgets

from ....widgets.simpletree import SimpleTree
from .... import icons


class RosterTab(QtWidgets.QWidget):
    title = 'Roster'
    icon = icons.roster

    def __init__(self, parent: QtWidgets.QTabWidget):
        super().__init__(parent)
        self.mainLayout = QtWidgets.QHBoxLayout(self)

        self.treeLayout = QtWidgets.QVBoxLayout()
        self.filterLayout = QtWidgets.QHBoxLayout()
        self.filterLayout.setSpacing(50)
        self.warningLabel = QtWidgets.QLabel(
            'Wingman can only track characters for changes while they are logged in and while it is running.')
        self.filterLayout.addWidget(self.warningLabel)
        self.searchLineEdit = QtWidgets.QLineEdit()
        self.searchLineEdit.setPlaceholderText('Filter')
        self.filterLayout.addWidget(self.searchLineEdit)
        self.treeLayout.addLayout(self.filterLayout)

        self.tree = SimpleTree(['Name', 'Base', 'System', 'Credits', 'Last active', 'Description'])
        self.treeLayout.addWidget(self.tree)

        self.mainLayout.addLayout(self.treeLayout)

        self.controlsLayout = QtWidgets.QVBoxLayout()
        self.controlsLayout.setSpacing(15)
        self.controlsLayout.addSpacing(30)

        self.manualGroup = QtWidgets.QGroupBox('Edit')
        self.manualGroup.setAlignment(QtCore.Qt.AlignHCenter)
        self.manualLayout = QtWidgets.QVBoxLayout()
        self.addCharButton = QtWidgets.QPushButton('Add character')
        self.addCharButton.setToolTip('Manually add a new character (double click to edit)')
        self.manualLayout.addWidget(self.addCharButton)
        self.editCharButton = QtWidgets.QPushButton('Edit character')
        self.editCharButton.setToolTip('Allow the selected character to be edited')
        self.manualLayout.addWidget(self.editCharButton)
        self.moveCharButton = QtWidgets.QPushButton('Move character')
        self.moveCharButton.setToolTip('Allow the selected character to be moved between accounts')
        self.manualLayout.addWidget(self.moveCharButton)
        self.removeCharButton = QtWidgets.QPushButton('Remove character')
        self.removeCharButton.setToolTip('Remove the selected character')
        self.manualLayout.addWidget(self.removeCharButton)
        self.manualGroup.setLayout(self.manualLayout)
        self.controlsLayout.addWidget(self.manualGroup)

        self.fileGroup = QtWidgets.QGroupBox('File')
        self.fileGroup.setAlignment(QtCore.Qt.AlignHCenter)
        self.fileLayout = QtWidgets.QVBoxLayout()
        self.reloadButton = QtWidgets.QPushButton('Reload accounts')
        self.reloadButton.setToolTip('Reload account information from the launcher')
        self.fileLayout.addWidget(self.reloadButton)
        self.importExportButton = QtWidgets.QPushButton('Export')
        self.fileLayout.addWidget(self.importExportButton)
        self.fileGroup.setLayout(self.fileLayout)
        self.controlsLayout.addWidget(self.fileGroup)

        self.viewGroup = QtWidgets.QGroupBox('View')
        self.viewGroup.setAlignment(QtCore.Qt.AlignHCenter)
        self.viewLayout = QtWidgets.QVBoxLayout()
        self.collapseButton = QtWidgets.QPushButton('Collapse all')
        self.collapseButton.clicked.connect(lambda *args: self.tree.collapseAll())
        self.viewLayout.addWidget(self.collapseButton)
        self.expandButton = QtWidgets.QPushButton('Expand all')
        self.expandButton.clicked.connect(lambda *args: self.tree.expandAll())
        self.viewLayout.addWidget(self.expandButton)
        self.viewGroup.setLayout(self.viewLayout)
        self.controlsLayout.addWidget(self.viewGroup)

        self.controlsLayout.addStretch(1)

        self.mainLayout.addLayout(self.controlsLayout)
