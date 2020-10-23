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
from typing import Dict, Iterator, Tuple, Optional
from collections import defaultdict
import json
import os.path
import xml.etree.ElementTree as xml

from PyQt5 import QtCore, QtGui

from ... import config, ROSTER_FILE
from .. import items


class AccountsModel(QtGui.QStandardItemModel):
    """A hierarchical model for storing game accounts and their characters."""
    def __init__(self):
        super().__init__()
        self.dataChanged.connect(self.onDataChanged)

    def addAccount(self, code, name, description):
        """Add an account to the model, returning its new row."""
        accountItem = items.AccountItem(items.AccountItem.Account(code, name, description))
        newRow = [accountItem, items.BlankItem(), items.BlankItem(), items.CreditsItem(0), items.DateItem(None),
                  items.GenericItem(description)]
        self.invisibleRootItem().appendRow(newRow)
        return newRow

    @staticmethod
    def addCharacter(parentAccount: items.AccountItem, name, credits, system, base, logged, description):
        """Add a character to the model, returning the new row."""
        dateItem = items.DateItem.deserialise(logged) if type(logged) is int else items.DateItem(logged)
        newRow = [items.GenericItem(name), items.GenericItem(base), items.GenericItem(system),
                  items.CreditsItem(credits), dateItem, items.GenericItem(description)]
        parentAccount.appendRow(newRow)
        return newRow

    def updateAccountSummary(self, accountItem: items.AccountItem):
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

        self.itemFromIndex(accountItem.index().siblingAtColumn(3)).putData(sum(balances))
        self.itemFromIndex(accountItem.index().siblingAtColumn(4)).putData(max(dates, default=None))

    def updateCharacter(self, name, account, logged, balance=None, system=None, base=None):
        """Update a character's record in the model."""
        if name is None or name == 'Trent':  # (hacky) ignore single player
            return

        accountItem = self.model.findAccount(account)
        if not accountItem:
            raise ValueError(f'Account {account!r} for character {name!r} not found')

        characterItem = self.model.findCharacter(name)
        if not characterItem:
            raise ValueError(f'Character {name!r} not found')

        index = characterItem.index()
        if base is not None:
            self.model.itemFromIndex(index.siblingAtColumn(1)).putData(base)
        elif system is not None:
            self.model.itemFromIndex(index.siblingAtColumn(2)).putData(system)
        elif balance is not None:
            self.model.itemFromIndex(index.siblingAtColumn(3)).putData(balance)
        elif logged is not None:
            self.model.itemFromIndex(index.siblingAtColumn(4)).putData(logged)

    def serialise(self, toFile=ROSTER_FILE):
        """Serialise the model to a JSON file."""
        result = {}

        for item in self.allItems():  # type: items.GenericItem
            if item is None:
                continue

            serialised = item.serialise()
            if isinstance(item, items.AccountItem):
                account = result[serialised] = dict(characters=defaultdict(dict))
            elif isinstance(item.parent(), items.AccountItem):
                column = self.horizontalHeaderItem(item.column()).text()

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

    def deserialise(self):
        """Deserialise the model from JSON, combining it with launcher accounts to create model items and adding them to
        the model. It would make more sense to return a new model here, but Qt links header names to the model so we must
        use the one the SimpleTree already has."""
        self.empty()

        if not os.path.exists(ROSTER_FILE) or os.stat(ROSTER_FILE).st_size == 0:
            db = {}
        else:
            with open(ROSTER_FILE) as f:
                db = json.load(f)

        for code, (name, description) in self.retrieveDSLauncherAccounts().items():
            db.setdefault(code, dict(characters=defaultdict(dict)))  # create entry in db

            accountItem, *_, activityItem, descriptionItem = self.addAccount(code, name, description)
            for charName, charAttributes in db[code]['characters'].items():
                self.addCharacter(accountItem, name=charAttributes.pop('name', charName), **charAttributes)
            self.updateAccountSummary(accountItem)

    def onDataChanged(self, topLeft: QtCore.QModelIndex, bottomRight: QtCore.QModelIndex):
        """Handle the model's data being changed."""
        item = self.itemFromIndex(topLeft)
        parent = item.parent()

        if parent is not None and parent is not self.invisibleRootItem():
            self.updateAccountSummary(parent)

        self.serialise()

    def findAccount(self, accountCode: int) -> Optional[items.AccountItem]:
        """Find an account's item in the model from its code (aka hash)."""
        for item in self.allItems():
            if isinstance(item, items.AccountItem) and item.getData().hash == accountCode:
                return item

    def findCharacter(self, characterName: str) -> Optional[items.GenericItem]:
        """Find a character's item in the model from its name."""
        try:
            return self.findItems(characterName, QtCore.Qt.MatchRecursive)[0]
        except IndexError:
            return None

    def allItems(self) -> Iterator[QtGui.QStandardItem]:
        """Return an iterator over all the model's items in order of addition, starting from the root item."""
        def recurse(parent):
            for row in range(parent.rowCount()):
                for column in range(parent.columnCount()):
                    child = parent.child(row, column)
                    yield child
                    if child is not None and child.hasChildren():
                        yield from recurse(child)

        yield from recurse(self.invisibleRootItem())

    def empty(self):
        """Empty the model. This is distinct from reset() because it does not delete the header labels."""
        self.removeRows(0, self.rowCount() - 1)  # empty model

    @staticmethod
    def retrieveDSLauncherAccounts() -> Dict[str, Tuple[str, str]]:
        """Parse launcheraccounts.xml to a dictionary of tuples of the form {code: (name, description)}."""
        root = xml.parse(config.paths['accounts']).getroot()
        return {a.get('code'): (a.text, a.get('description')) for a in root.findall('account')}
