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
import logging
import os.path

from PyQt5 import QtCore, QtGui, QtWidgets

from .... import IS_WIN
from .layout import RosterTab
from ....models import items
from ....models.filters import TextFilter
from ....models.special.accounts import AccountsModel

if IS_WIN:
    import flair


class Roster:
    """The "Roster" tab provides a persistent list of accounts and their characters, along with their attributes.
    This list updates upon receiving events from flair."""
    def __init__(self, widget: RosterTab):
        self.widget = widget
        self.tree = self.widget.tree

        # configure model and view
        self.sortModel = TextFilter(AccountsModel())
        self.model: AccountsModel = self.sortModel.sourceModel()
        self.model.setHorizontalHeaderLabels(self.tree.horizontalHeaderLabels())
        self.tree.setModel(self.sortModel)

        self.widget.searchLineEdit.textEdited.connect(self.onFilterTextEdited)
        self.tree.rowSelected.connect(self.onSelectedRowChanged)
        self.populateTree()

        # make UI connections
        self.widget.editCharButton.clicked.connect(self.makeCharacterEditable)
        self.widget.moveCharButton.clicked.connect(self.makeCharacterMovable)
        self.widget.addCharButton.clicked.connect(lambda: self.createCharacter(self.tree.getSelectedRow()[0]))
        self.widget.removeCharButton.clicked.connect(self.removeCharacter)

        self.widget.reloadButton.clicked.connect(self.populateTree)
        self.widget.importExportButton.clicked.connect(self.export)

        if IS_WIN:
            flair.events.character_changed.connect(self.onCharacterUpdate)
            flair.events.credits_changed.connect(self.onCharacterUpdate)
            flair.events.system_changed.connect(self.onCharacterUpdate)
            flair.events.docked.connect(self.onCharacterUpdate)

    def onSelectedRowChanged(self, selection: List[QtGui.QStandardItem]):
        """Enable or disable buttons based on the type of selection."""
        isAccountRow = isinstance(selection[0], items.AccountItem)

        self.widget.addCharButton.setEnabled(isAccountRow)
        self.widget.removeCharButton.setEnabled(not isAccountRow)
        self.widget.moveCharButton.setEnabled(not isAccountRow)
        self.widget.editCharButton.setEnabled(not isAccountRow)
        self.tree.setDragEnabled(not isAccountRow)

        for item in self.model.allItems():
            item.setEditable(False)
            item.setDragEnabled(False)

    def onFilterTextEdited(self, text):
        """Handle the filter text being changed."""
        if not text:
            self.tree.collapseAll()
        else:
            self.tree.expandAll()
        self.sortModel.update(text)

    def populateTree(self):
        """Populate the tree with deserialised data."""
        self.model.deserialise()
        self.model.serialise()  # commit merged model to disk
        self.tree.reset()
        self.tree.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.tree.expandAll()

    def makeCharacterEditable(self, row=None):
        """Make the character at row editable. If row is not provided, it defaults to the selected row."""
        row = row or self.tree.getSelectedRow()
        for item in row:
            item.setEditable(True)

    def makeCharacterMovable(self, row=None):
        """Make the character at row movable between accounts. If row is not provided, it defaults to the selected
        row."""
        row = row or self.tree.getSelectedRow()
        for item in row:
            item.setDragEnabled(True)

    def removeCharacter(self):
        """Remove a character's row from the tree."""
        row = self.tree.getSelectedRow()
        row[0].parent().removeRow(row[0].row())
        self.model.serialise()

    def createCharacter(self, parentAccount: items.AccountItem):
        """Create a new character and add it to the tree. Unlike addCharacter, this is intended to be triggered by the
        user."""
        newRow = self.model.addCharacter(parentAccount, name='', credits=0, system='', base='',
                                         logged=QtCore.QDateTime.currentDateTime(), description='')
        self.makeCharacterEditable(newRow)
        self.tree.expandAll()

    def onCharacterUpdate(self, **kwargs):
        """Handle a character record update from flair."""
        assert IS_WIN
        name = kwargs.setdefault('name', flair.state.name)
        account = kwargs.setdefault('account', flair.state.account)
        updateTime = QtCore.QDateTime.currentDateTime()

        if not name:  # if name has not been set in memory yet, we don't have a key to go on
            return

        if self.model.findCharacter(name):
            self.model.updateCharacter(logged=updateTime, **kwargs)
        else:
            self.model.addCharacter(self.model.findAccount(account), name, flair.state.credits or 0,
                                    flair.state.system or '', flair.state.base or '', updateTime, '')

        self.model.serialise()

    def export(self):
        """Allow the model to be exported to a file of the user's choice."""
        toFile = QtWidgets.QFileDialog.getSaveFileName(caption='Export characters',
                                                       directory=os.path.expanduser('~/roster.json'),
                                                       filter='JSON files (*.json)')[0]
        if toFile:
            self.model.serialise(toFile)
