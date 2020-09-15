"""
Copyright © 2016-18 biqqles

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
from PyQt5 import QtCore, QtGui


class TextFilter(QtCore.QSortFilterProxyModel):
    """A simple proxy model that filters on a configurable text query."""
    def __init__(self, sourceModel: QtGui.QStandardItemModel):
        super().__init__()
        self.setSourceModel(sourceModel)
        self.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.setDynamicSortFilter(True)
        self.setRecursiveFilteringEnabled(True)
        self.setFilterKeyColumn(-1)  # filter on all columns

        # delegate QStandardItemModel methods
        self.invisibleRootItem = sourceModel.invisibleRootItem
        self.itemFromIndex = sourceModel.itemFromIndex

    def update(self, query: str):
        """Cause the filter to be updated with a new query."""
        self.setFilterFixedString(query)
