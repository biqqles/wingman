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
from typing import List, Optional, Any
import os

from PyQt5 import QtCore, QtGui, QtWidgets

from .. import app, IS_WIN
from ..models.filters import TextFilter


class SimpleTable(QtWidgets.QTableView):
    rowSelected = QtCore.pyqtSignal('PyQt_PyObject')  # emits a list of the cells in the selected row
    rowDeselected = QtCore.pyqtSignal('PyQt_PyObject')  # emits a list of the cells in the deselected row

    class FixedHeightDelegate(QtWidgets.QStyledItemDelegate):
        def sizeHint(self, option, index):
            size = super().sizeHint(option, index)
            size.setHeight(2)
            return size

    def __init__(self, header: List[str]):
        super().__init__()
        # configure model
        self.itemModel = QtGui.QStandardItemModel()
        self.itemModel.setHorizontalHeaderLabels(header)
        self.filterModel = TextFilter(self.itemModel)
        self.setModel(self.filterModel)

        # configure view
        self.setSortingEnabled(True)
        self.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        self.setSelectionMode(QtWidgets.QTableView.SingleSelection)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        verticalHeader = self.verticalHeader()
        verticalHeader.hide()
        verticalHeader.setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        verticalHeader.setDefaultSectionSize(self.defaultRowHeight())

        horizontalHeader = self.horizontalHeader()
        horizontalHeader.setStretchLastSection(True)
        horizontalHeader.setHighlightSections(False)  # fix for ugly/nonstandard bold header on Windows
        horizontalHeader.setSectionsMovable(True)
        horizontalHeader.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        horizontalHeader.setToolTip('Right-click for filters')

        # connections
        self.selectionModel().selectionChanged.connect(self.onSelectedRowChanged)
        self.customContextMenuRequested.connect(self.onMenuRequested)
        horizontalHeader.customContextMenuRequested.connect(self.onHeaderMenuRequested)

        if IS_WIN:
            # attempt to match the more modern styling of QTreeView and QListWidget. Hover still doesn't work, so
            # another approach (e.g. QStyledItemDelegate) will be needed in future.
            self.setStyleSheet('QTableView::item:selected {'
                               '    background-color: rgb(205, 232, 255);'
                               '    color: black;'
                               '};'
                               'QTableView::item:hover {'
                               '    background-color: rgb(0, 120, 215, 20%);'
                               '};')

    def horizontalHeaderLabels(self) -> List[str]:
        """Return the model's horizontal header labels (see setHorizontalHeaderLabels)"""
        return [self.itemModel.headerData(i, QtCore.Qt.Horizontal) for i in range(self.itemModel.columnCount())]

    def clear(self):
        """Clear the table, without clearing the headings."""
        self.itemModel.removeRows(0, self.itemModel.rowCount())

    def populate(self, rows: List[List[QtGui.QStandardItem]]):
        """Populate the table and its model with rows of items. In addition to adding this data, this method also
        readies the table for immediate use: sorting, resizing and selecting the first row."""
        self.clear()
        for row in rows:
            self.itemModel.appendRow(row)

        # unfortunately setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents) results in shockingly
        # poor performance when resizing, so resize the columns here
        if rows:
            self.resizeColumnsToContents()

        self.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.selectRow(0)
        self.horizontalHeader().reset()  # fix for stretchLastSection not being obeyed sometimes

    def onSelectedRowChanged(self, selected, deselected):
        """Handle the user selecting a new row."""
        if not selected.indexes():
            return
        selectedItems = (item.data(QtCore.Qt.UserRole) for item in selected.indexes())
        self.rowSelected.emit(selectedItems)
        deselectedItems = (item.data(QtCore.Qt.UserRole) for item in deselected.indexes())
        self.rowDeselected.emit(deselectedItems)

    def onHeaderMenuRequested(self, pos: QtCore.QPoint):
        """Show a context menu when the header is right-clicked."""
        menu = QtWidgets.QMenu()

        columnMenu = menu.addMenu('Column visibility')
        for i, text in enumerate(self.horizontalHeaderLabels()):
            item = columnMenu.addAction(text)
            item.setCheckable(True)
            item.setChecked(not self.isColumnHidden(i))
            item.toggled.connect(lambda checked, index=i: self.setColumnHidden(index, not checked))

        rowsMenu = menu.addMenu('Filter rows')
        rowsEdit = QtWidgets.QLineEdit(self.filterModel.query())
        rowsEdit.textChanged.connect(self.filterModel.update)
        rowsEdit.setPlaceholderText('Query')
        rowsEdit.setClearButtonEnabled(True)
        rowFilter = QtWidgets.QWidgetAction(rowsMenu)
        rowFilter.setDefaultWidget(rowsEdit)
        rowsMenu.addAction(rowFilter)

        menu.exec(QtGui.QCursor.pos())

    def onMenuRequested(self, point):
        """Show a context menu when a cell is right-clicked."""
        cell = self.indexAt(point)
        menu = QtWidgets.QMenu()
        copy = menu.addMenu('Copy')
        copy.setIcon(QtGui.QIcon.fromTheme('edit-copy'))
        copy.addAction('cell').triggered.connect(lambda: self.copyToClipboard(value=cell.data()))
        copy.addAction('row').triggered.connect(lambda: self.copyToClipboard(row=cell.row()))
        copy.addAction('table').triggered.connect(lambda: self.copyToClipboard())

        menu.exec(QtGui.QCursor.pos())

    def copyToClipboard(self, row: Optional[int] = None, value: Optional[Any] = None):
        """Copy data to the clipboard as a string. If value is specified, this one value should be added. If row is
        specified, it is the index to the singular row in the model to be exported as a TSV dump. If neither are
        specified, the entire model should be dumped as TSV."""
        clipboard = app.clipboard()
        if value is not None:
            clipboard.setText(str(value))
        else:
            clipboard.setText(self.modelToTSV(row))

    def modelToTSV(self, row: Optional[int] = None):
        """Represent the item model as a TSV dump of its data. If row is specified, it is the index to the singular row
        in the model to be exported. Otherwise, all rows will be exported."""
        columns = range(self.itemModel.columnCount())
        rows = range(self.itemModel.rowCount())
        result = []
        if row is not None:
            for column in columns:
                result.append(str(self.itemModel.index(row, column).data()))
            return '\t'.join(result)
        else:
            for row in rows:
                tmp = []
                for column in columns:
                    tmp.append(str(self.itemModel.index(row, column).data()))
                result.append('\t'.join(tmp))
            return os.linesep.join(result)

    @staticmethod
    def defaultRowHeight() -> int:
        """Calculate the default row height."""
        return QtGui.QFontMetrics(QtGui.QStandardItem().font()).height() + 12
