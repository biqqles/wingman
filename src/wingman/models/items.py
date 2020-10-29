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
from typing import Any, TypeVar, Optional

from PyQt5 import QtGui, QtCore
from dataclassy import dataclass
import flint as fl
import ago


T = TypeVar('T')


class GenericItem(QtGui.QStandardItem):
    """A generic item with no data beyond its text."""
    def __init__(self, initialData: T):
        super().__init__()
        self.putData(initialData)
        self.setEditable(False)
        self.setDragEnabled(False)
        self.setDropEnabled(False)

    def putData(self, data: T):
        """An abstraction over setData(). Sets data and updates the textual representation."""
        self.setData(self.represent(data), QtCore.Qt.DisplayRole)
        self.setData(data, QtCore.Qt.UserRole)

    def getData(self) -> T:
        """Retrieve this item's underlying data."""
        return self.data(QtCore.Qt.UserRole)

    @staticmethod
    def represent(data: T) -> str:
        """Represent this item's data as a string. The default implementation returns the data unchanged, i.e. assumes
        it is a string to begin with.

        The "official" way to do this sort of thing is to do it all in a subclassed data(). However I find this less
        declarative than I'd like."""
        return data

    def serialise(self) -> Any:
        """Reduce this item's data down to a primitive that can be serialised in a format such as JSON."""
        return self.getData()

    @classmethod
    def deserialise(cls, serialised: Any):
        """Construct a new item from deserialised data. In most cases, this is simply equivalent to initialising
        the class normally."""
        return cls(serialised)

    def data(self, role=QtCore.Qt.UserRole + 1):
        """Alert the QItemDelegate to edit this item's underlying data."""
        if role == QtCore.Qt.EditRole:
            return self.getData()
        return super().data(role)

    def setData(self, value: float, role=QtCore.Qt.UserRole + 1):
        """Allow edits to update the underlying data."""
        if role == QtCore.Qt.EditRole:
            self.putData(value)
        else:
            super().setData(value, role)

    def clone(self) -> 'GenericItem':
        """Allow QStandardItemModel to clone this item, which happens e.g. on move events."""
        return GenericItem(self.getData())


class BlankItem(GenericItem):
    """A blank item."""
    def __init__(self):
        super().__init__('')


class MonospaceItem(GenericItem):
    def __init__(self, data):
        super().__init__(data)
        self.setFont(QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.FixedFont))


class EntityItem(GenericItem):
    """An item holding a flint Entity."""
    @staticmethod
    def represent(entity: fl.entities.Entity):
        return entity.name()

    def data(self, role=QtCore.Qt.UserRole + 1):
        """Entities are never editable, but widgets such as QComboBox in text mode use the edit role."""
        if role == QtCore.Qt.EditRole:
            return self.text()
        return super().data(role)


class SystemItem(EntityItem):
    """An item holding a flint System."""
    def __init__(self, system: fl.entities.System):
        super().__init__(system)
        self.setToolTip(f'Region: {system.region()}')


class BaseItem(EntityItem):
    """An item holding a flint Base."""
    def __init__(self, base: fl.entities.Base):
        super().__init__(base)
        self.setToolTip(f'Sector: {base.sector()}\nIFF: {base.owner().name()}')


class FactionItem(EntityItem):
    """An item holding a flint Faction."""
    def __init__(self, faction: fl.entities.Faction):
        super().__init__(faction)


class CommodityItem(EntityItem):
    """An item holding a flint Commodity."""
    def __init__(self, commodity: fl.entities.Good):
        super().__init__(commodity)
        # self.setIcon(QtGui.QIcon(QtGui.QPixmap.fromImage(QtGui.QImage.fromData(commodity.icon(), 'TGA'))))


class NumberItem(GenericItem):
    """An item holding a number."""
    @staticmethod
    def represent(number):
        return f'{number:,}' if type(number) is int else f'{number:,.2f}'

    def __lt__(self, other):
        return self.getData() < other.getData()


class BooleanItem(NumberItem):
    """An item displaying a boolean state."""
    def __init__(self, checked: bool):
        super().__init__(int(checked))
        self.setText('')
        self.setCheckState(QtCore.Qt.Checked if checked else QtCore.Qt.Unchecked)

    def setEditable(self, editable: bool):
        """Override set editable to allow the checkbox to be toggled but not the text to be edited."""
        self.setCheckable(editable)
        super().setEditable(False)


class PercentageItem(NumberItem):
    """An item displaying a number as a percentage."""
    @staticmethod
    def represent(number):
        return f'{number * 100:.2f}%'


class CreditsItem(NumberItem):
    """An item displaying a number as an amount in credits."""
    @staticmethod
    def represent(credits_):
        return f'${credits_:,}'


class ProfitItem(CreditsItem):
    """An item holding information about the profit of a transaction. It displays like a CreditsItem."""
    @dataclass
    class ProfitData:
        """Data for this transaction."""
        buyPrice: int
        buyBase: fl.entities.Base
        sellPrice: int
        sellBase: fl.entities.Base
        commodity: fl.entities.Commodity

        def profit(self):
            return (self.sellPrice - self.buyPrice) // self.commodity.volume

    def __init__(self, *args):
        data = self.ProfitData(*args)
        super().__init__(data)
        self.setToolTip(f'Buy: ${data.buyPrice}\nSell: ${data.sellPrice}\nVolume: {data.commodity.volume}')

    @staticmethod
    def represent(profitData: ProfitData):
        return f'${profitData.profit():,}'

    def __lt__(self, other):
        return self.getData().profit() < other.getData().profit()


class AccountItem(GenericItem):
    @dataclass
    class Account:
        hash: str
        launcher_name: str
        launcher_description: str

    def __init__(self, account: Account):
        super().__init__(account)
        font = self.font()
        font.setBold(True)
        self.setFont(font)
        self.setDropEnabled(True)

    @staticmethod
    def represent(account: Account) -> str:
        return account.launcher_name

    def serialise(self) -> Any:
        return self.getData().hash


class DateItem(NumberItem):
    timer = QtCore.QTimer()
    timer.start(60_000)

    def __init__(self, initialDate: Optional[QtCore.QDateTime]):
        super().__init__(initialDate)
        self.timer.timeout.connect(self.tick)

    def tick(self):
        """Keep the the displayed time delta accurate."""
        self.setText(self.represent(self.getData()))

    @staticmethod
    def represent(dateTime: Optional[QtCore.QDateTime]):
        if dateTime is None:
            return 'Unknown'
        if abs(dateTime.secsTo(QtCore.QDateTime.currentDateTime())) < 30:
            return 'Now'
        return ago.human(dateTime.toPyDateTime(), precision=1)

    def serialise(self) -> int:
        try:
            return self.getData().toSecsSinceEpoch()
        except AttributeError:
            return 0

    @classmethod
    def deserialise(cls, serialised: int):
        return cls(QtCore.QDateTime.fromSecsSinceEpoch(serialised))

    def data(self, role=QtCore.Qt.UserRole + 1):
        """Alert the QItemDelegate to edit this item as a date."""
        if role == QtCore.Qt.EditRole:
            return self.getData().date()
        return super().data(role)

    def setData(self, date: QtCore.QDate, role=QtCore.Qt.UserRole + 1):
        """Confirm the date is valid before accepting it."""
        if role == QtCore.Qt.EditRole:
            if date.isValid():
                self.putData(QtCore.QDateTime(date))
        else:
            super().setData(date, role)
