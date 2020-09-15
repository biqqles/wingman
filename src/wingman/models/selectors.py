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
from PyQt5 import QtGui
import flint as fl

from .items import SystemItem, FactionItem


class SystemSelectionModel(QtGui.QStandardItemModel):
    def __init__(self):
        super().__init__()
        for system in sorted(fl.systems, key=lambda s: s.name()):
            if system.bases() and system.connections():
                self.appendRow(SystemItem(system))


class FactionSelectionModel(QtGui.QStandardItemModel):
    def __init__(self):
        super().__init__()
        for group in sorted(fl.factions, key=lambda f: f.name()):
            self.appendRow(FactionItem(group))
