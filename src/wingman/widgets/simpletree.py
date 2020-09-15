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
from typing import List, Iterator

from PyQt5 import QtCore, QtGui, QtWidgets

from ..models import items


class SimpleTree(QtWidgets.QTreeView):
    rowSelected = QtCore.pyqtSignal('PyQt_PyObject')  # emits a list of the cells in the selected row

    class FixedHeightDelegate(QtWidgets.QStyledItemDelegate):
        def sizeHint(self, option, index):
            size = super().sizeHint(option, index)
            size.setHeight(26)
            return size

    def __init__(self, header: List[str]):
        super().__init__()
        # configure model
        self.itemModel = QtGui.QStandardItemModel()
        self.itemModel.setHorizontalHeaderLabels(header)
        self.itemModel.setItemPrototype(items.GenericItem(''))
        self.setModel(self.itemModel)

        # configure view
        self.delegate = self.FixedHeightDelegate()
        self.setItemDelegate(self.delegate)

        self.setSortingEnabled(True)
        self.setHeaderHidden(False)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.setDragEnabled(True)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setUniformRowHeights(True)
        self.setAnimated(True)

    def allItems(self) -> Iterator[QtGui.QStandardItem]:
        root = self.itemModel.invisibleRootItem()

        def recurse(parent):
            for row in range(parent.rowCount()):
                for column in range(parent.columnCount()):
                    child = parent.child(row, column)
                    yield child
                    if child is not None and child.hasChildren():
                        yield from recurse(child)

        yield from recurse(root)

    def getSelectedRow(self) -> List[QtGui.QStandardItem]:
        return [i.model().sourceModel().itemFromIndex(i.model().mapToSource(i)) for i in self.selectedIndexes()]

    def selectionChanged(self, selected: QtCore.QItemSelection, deselected: QtCore.QItemSelection):
        if not selected.indexes():
            return
        self.rowSelected.emit(self.getSelectedRow())
