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
import os.path
from pathlib import Path
import sys

from PyQt5 import QtCore, QtGui, QtWidgets
import flint as fl

from ...widgets.pathedit import PathEdit
from ... import IS_WIN, config


class ConfigurePaths(QtWidgets.QDialog):
    """A dialogue that allows the paths needed by the application to be configured."""
    title = 'Configure paths'

    def __init__(self, mandatory=False):
        super().__init__()
        self.mandatory = mandatory
        self.setWindowTitle(self.title)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setWindowFlags(QtCore.Qt.Dialog)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        self.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Maximum)

        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.setLayout(self.mainLayout)

        self.formLayout = QtWidgets.QFormLayout()
        self.mainLayout.addLayout(self.formLayout)

        defaultFreelancerDir = config.paths['freelancer_dir'] or \
            os.path.expanduser('~')
        self.freelancerDirEdit = PathEdit(defaultFreelancerDir, fl.paths.is_probably_freelancer)
        self.freelancerDirEdit.lineEdit.textChanged.connect(self.validate)
        self.formLayout.addRow('Freelancer directory', self.freelancerDirEdit)

        defaultMyGamesDir = config.paths['my_games'] or \
            (os.path.expanduser(r'~\Documents\My Games' if IS_WIN else '~'))
        self.myGamesDirEdit = PathEdit(defaultMyGamesDir, lambda path: Path(path).name == 'My Games')
        self.myGamesDirEdit.lineEdit.textChanged.connect(self.validate)
        self.formLayout.addRow("'My Games' directory", self.myGamesDirEdit)

        self.buttons = QtWidgets.QDialogButtonBox()
        self.buttons.addButton(QtWidgets.QDialogButtonBox.Save)
        self.buttons.addButton(QtWidgets.QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.writeConfig)
        self.buttons.rejected.connect(self.close)
        self.mainLayout.addWidget(self.buttons)

        self.show()
        self.validate()

    def validate(self):
        """Validate the provided paths, enabling or disabling the accept role."""
        self.buttons.button(QtWidgets.QDialogButtonBox.Save).setEnabled(self.allPathsValid())

    def allPathsValid(self):
        """Returns whether all paths entered are valid."""
        return self.freelancerDirEdit.isValidPath() and self.myGamesDirEdit.isValidPath()

    def writeConfig(self):
        """Commit the changes to the config file to disk. It should only be possible to call this after the paths
        have been confirmed as valid."""
        config.paths['freelancer_dir'] = self.freelancerDirEdit.lineEdit.text()
        config.paths['my_games'] = self.myGamesDirEdit.lineEdit.text()
        config.commit()
        self.close()

    def closeEvent(self, event: QtGui.QCloseEvent):
        """If the dialogue is mandatory, quit the application."""
        if self.mandatory and not self.allPathsValid():
            sys.exit(1)
