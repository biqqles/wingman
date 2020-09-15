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


class ReadErrorMsgBox(QtWidgets.QMessageBox):
    def __init__(self):
        QtWidgets.QMessageBox.__init__(self)
        self.setWindowTitle('Failed to load files')
        self.setIcon(QtWidgets.QMessageBox.Warning)
        self.setText('Check that the drive is mounted and try again, or reconfigure your paths.')
        self.addButton(QtWidgets.QPushButton('Retry'), QtWidgets.QMessageBox.NoRole)
        self.addButton(QtWidgets.QPushButton('Configure paths'), QtWidgets.QMessageBox.YesRole)
