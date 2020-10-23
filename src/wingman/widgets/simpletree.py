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
from typing import List

from PyQt5 import QtCore, QtGui, QtWidgets

from .simpletable import SimpleTable


class SimpleTree(QtWidgets.QTreeView):
    rowSelected = QtCore.pyqtSignal('PyQt_PyObject')  # emits a list of the cells in the selected row

    class FixedHeightDelegate(QtWidgets.QStyledItemDelegate):
        def sizeHint(self, option, index):
            size = super().sizeHint(option, index)
            size.setHeight(SimpleTable.defaultRowHeight())
            return size

    def __init__(self, header: List[str]):
        super().__init__()
        # configure model
        self.itemModel = QtGui.QStandardItemModel()
        self.itemModel.setHorizontalHeaderLabels(header)
        self.itemModel.dataChanged.connect(self.resizeColumnsToContents)
        self.setModel(self.itemModel)

        # configure view
        self.setItemDelegate(self.FixedHeightDelegate())
        self.setSortingEnabled(True)
        self.setHeaderHidden(False)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.setDragEnabled(True)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setUniformRowHeights(True)
        self.setAnimated(True)

    def getSelectedRow(self) -> List[QtGui.QStandardItem]:
        """Return a list of the items in the currently selected row."""
        return [i.model().sourceModel().itemFromIndex(i.model().mapToSource(i)) for i in self.selectedIndexes()]

    def selectionChanged(self, selected: QtCore.QItemSelection, deselected: QtCore.QItemSelection):
        """Emit a signal when the selected row is changed."""
        if not selected.indexes():
            return
        self.rowSelected.emit(self.getSelectedRow())

    def horizontalHeaderLabels(self) -> List[str]:
        """Return the model's horizontal header labels (see setHorizontalHeaderLabels)"""
        return [self.itemModel.headerData(i, QtCore.Qt.Horizontal) for i in range(self.itemModel.columnCount())]

    def resizeColumnsToContents(self):
        """Resize all columns to their contents."""
        for column in range(self.itemModel.columnCount()):
            self.resizeColumnToContents(column)
