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
from typing import Dict, Tuple, List
from collections import defaultdict
import json
import logging
import os.path
import xml.etree.ElementTree as xml

from PyQt5 import QtCore, QtGui, QtWidgets

from .... import config, IS_WIN, ROSTER_FILE
from .layout import RosterTab
from ....models import items
from ....models.filters import TextFilter

if IS_WIN:
    import flair


class Roster:
    """The "Roster" tab provides a persistent list of accounts and their characters, along with their attributes.
    This list updates upon receiving events from flair.

    Todo: this file's code is probably the worst in the project. At the very least the model code should be split
    off."""
    def __init__(self, widget: RosterTab):
        self.widget = widget
        self.tree = self.widget.tree
        self.populateTree()
        self.serialise()

        # configure model and view
        self.sortModel = TextFilter(self.tree.model())
        self.model = self.sortModel.sourceModel()
        self.model.dataChanged.connect(self.onDataChanged)
        self.tree.setModel(self.sortModel)
        self.widget.searchLineEdit.textEdited.connect(self.onFilterTextEdited)
        self.tree.rowSelected.connect(self.onSelectedRowChanged)

        # make UI connections
        self.widget.editCharButton.clicked.connect(self.makeCharacterEditable)
        self.widget.moveCharButton.clicked.connect(self.makeCharacterMovable)
        self.widget.addCharButton.clicked.connect(lambda: self.createCharacter(self.tree.getSelectedRow()[0]))
        self.widget.removeCharButton.clicked.connect(self.removeCharacter)

        self.widget.reloadButton.clicked.connect(self.populateTree)
        self.widget.importExportButton.clicked.connect(self.export)

        if IS_WIN:
            flair.events.character_changed.connect(self.onCharacterChanged)
            flair.events.credits_changed.connect(self.onCharacterChanged)
            flair.events.system_changed.connect(self.onCharacterChanged)
            flair.events.docked.connect(self.onCharacterChanged)

    def onSelectedRowChanged(self, selection: List[QtGui.QStandardItem]):
        """Enable or disable buttons based on the type of selection."""
        isAccountRow = isinstance(selection[0], items.AccountItem)

        self.widget.addCharButton.setEnabled(isAccountRow)
        self.widget.removeCharButton.setEnabled(not isAccountRow)
        self.widget.moveCharButton.setEnabled(not isAccountRow)
        self.widget.editCharButton.setEnabled(not isAccountRow)
        self.tree.setDragEnabled(not isAccountRow)

        for item in self.tree.allItems():
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
        model = self.tree.model()
        self.deserialise(model)

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
        self.serialise()

    def updateCharacter(self, name, account, balance=None, system=None, base=None):
        """Update a character's record."""
        model = self.model
        logged = QtCore.QDateTime.currentDateTime()

        if name is None or name == 'Trent':
            return

        # find account item
        for item in self.tree.allItems():
            if isinstance(item, items.AccountItem) and item.data(QtCore.Qt.UserRole).hash == account:
                account = item
                break
        else:
            raise ValueError(f'Account {account!r} for character {name!r} not found')

        try:
            character = self.tree.model().sourceModel().findItems(name, QtCore.Qt.MatchRecursive)[0]
        except IndexError:
            newCharacter = self.addCharacter(account, flair.state.name, flair.state.credits or 0,
                                             flair.state.system or '', flair.state.base or '', logged, '')
            logging.info(f'Added character {name!r}')
            character = newCharacter[0]
            self.tree.reset()

        else:
            index = character.index()
            if base is not None:
                model.itemFromIndex(index.siblingAtColumn(1)).putData(base)
            elif system is not None:
                model.itemFromIndex(index.siblingAtColumn(2)).putData(system)
            elif balance is not None:
                model.itemFromIndex(index.siblingAtColumn(3)).putData(balance)
            elif logged is not None:
                model.itemFromIndex(index.siblingAtColumn(4)).putData(logged)

        self.tree.scrollTo(character.index())
        self.tree.expand(character.parent().index())

    def createCharacter(self, parentAccount: items.AccountItem):
        """Create a new character and add it to the tree. Unlike addCharacter, this is intended to be triggered by the
        user."""
        newRow = self.addCharacter(parentAccount, name='', credits=0, system='', base='',
                                   logged=QtCore.QDateTime.currentDateTime().toSecsSinceEpoch(), description='')
        self.makeCharacterEditable(newRow)
        self.tree.expandAll()

    def onCharacterChanged(self, **kwargs):
        assert IS_WIN
        kwargs.update(name=flair.state.name)
        self.updateCharacter(account=flair.state.account, **kwargs)
        self.serialise()

    def onDataChanged(self, topLeft: QtCore.QModelIndex, bottomRight: QtCore.QModelIndex):
        """Handle a data edit"""
        item = self.model.itemFromIndex(topLeft)
        parent = item.parent()

        if parent is not None and parent is not self.model.invisibleRootItem():
            self.updateAccountSummary(self.model, parent)

        self.serialise()

        for column in range(self.model.columnCount()):
            self.tree.resizeColumnToContents(column)

    def export(self):
        """Allow the model to be exported to a file of the user's choice."""
        toFile = QtWidgets.QFileDialog.getSaveFileName(caption='Export characters',
                                                       directory=os.path.expanduser('~/roster.json'),
                                                       filter='JSON files (*.json)')[0]
        if toFile:
            self.serialise(toFile)

    def serialise(self, toFile=ROSTER_FILE):
        """Serialise the model to a JSON file."""
        result = {}

        for item in self.tree.allItems():  # type: GenericItem
            if item is None:
                continue

            serialised = item.serialise()
            if isinstance(item, items.AccountItem):
                account = result[serialised] = dict(characters=defaultdict(dict))
            elif isinstance(item.parent(), items.AccountItem):
                column = self.tree.itemModel.horizontalHeaderItem(item.column()).text()

                if column == 'Name':
                    character = account['characters'][serialised]
                elif column == 'Base':
                    character.update(base=serialised)
                elif column == 'System':
                    character.update(system=serialised)
                elif column == 'Credits':
                    # after a move event the model turns items back into the prototype (GenericItem). Turn them back
                    character.update(credits=items.CreditsItem(item.getData()).serialise())
                elif column == 'Last active':
                    character.update(logged=items.DateItem(item.getData()).serialise())
                elif column == 'Description':
                    character.update(description=serialised)
                else:
                    raise NotImplementedError

        with open(toFile, 'w') as f:
            json.dump(result, f, indent=2)

    @staticmethod
    def addAccount(model, code, name, description):
        """Add an account to the model, returning the new row."""
        rootItem = model.invisibleRootItem()

        accountItem = items.AccountItem(items.AccountItem.Account(code, name, description))
        newRow = [accountItem, items.BlankItem(), items.BlankItem(), items.CreditsItem(0), items.DateItem(None),
                  items.GenericItem(description)]
        rootItem.appendRow(newRow)
        return newRow

    @staticmethod
    def updateAccountSummary(model, accountItem: items.AccountItem):
        """Update an account row to summarise the attributes of the characters within."""
        balances = []
        dates = []

        for r in range(accountItem.rowCount()):
            creditsItem, dateItem = accountItem.child(r, 3), accountItem.child(r, 4)
            if None not in (creditsItem, dateItem):
                balances.append(creditsItem.getData())
                dates.append(dateItem.getData())
            # for some reason, when the row is moved these become null
            # todo: when this happens a row can be duplicated in the model if it's not edited before exit
            # todo: the old parent account also does not update

        model.itemFromIndex(accountItem.index().siblingAtColumn(3)).putData(sum(balances))
        model.itemFromIndex(accountItem.index().siblingAtColumn(4)).putData(max(dates, default=None))

    @staticmethod
    def addCharacter(parentAccount: items.AccountItem, name, credits, system, base, logged, description):
        """Add a character to the model, returning the new row."""
        dateItem = items.DateItem.deserialise(logged) if type(logged) is int else items.DateItem(logged)
        newRow = [items.GenericItem(name), items.GenericItem(base), items.GenericItem(system),
                  items.CreditsItem(credits), dateItem, items.GenericItem(description)]
        parentAccount.appendRow(newRow)
        return newRow

    @classmethod
    def deserialise(cls, model: QtGui.QStandardItemModel):
        """Deserialise roster.json, combining it with launcher accounts to create model items and adding them to the
        model. It would make more sense to return a new model here, but Qt links header names to the model so we must
        use the one the SimpleTree already has."""
        model.removeRows(0, model.rowCount() - 1)  # empty model

        if not os.path.exists(ROSTER_FILE) or os.stat(ROSTER_FILE).st_size == 0:
            db = {}
        else:
            with open(ROSTER_FILE) as f:
                db = json.load(f)

        for code, (name, description) in cls.retrieveDSLauncherAccounts().items():
            db.setdefault(code, dict(characters=defaultdict(dict)))  # create entry in db

            accountItem, *_, activityItem, descriptionItem = cls.addAccount(model, code, name, description)
            for charName, charAttributes in db[code]['characters'].items():
                cls.addCharacter(accountItem, name=charAttributes.pop('name', charName), **charAttributes)
            cls.updateAccountSummary(model, accountItem)
        return model

    @staticmethod
    def retrieveDSLauncherAccounts() -> Dict[str, Tuple[str, str]]:
        """Parse launcheraccounts.xml to a dictionary of tuples of the form {code: (name, description)}."""
        root = xml.parse(config.paths['accounts']).getroot()
        return {a.get('code'): (a.text, a.get('description')) for a in root.findall('account')}
