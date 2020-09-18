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
from typing import List, Type

from PyQt5 import QtWidgets

from ...widgets.simpletable import SimpleTable
from ...models.items import *


class DatabasePage(QtWidgets.QSplitter):
    """A page in the database, with a main table and a secondary widget which displays further information about the
    entity currently selected in the main table."""
    mainTableHeadings: List[str]

    def __init__(self, parent, infocardView, secondaryWidget):
        super().__init__(parent=parent, orientation=QtCore.Qt.Vertical)
        self.infocardView = infocardView
        self.secondaryWidget = secondaryWidget

        self.mainTable = SimpleTable(self.mainTableHeadings)
        self.mainTable.rowSelected.connect(self.onSelectedRowChanged)
        self.addWidget(self.mainTable)
        self.setStretchFactor(0, 3)

        self.addWidget(self.secondaryWidget)
        self.setStretchFactor(1, 2)
        self.populate()

        self.instance = self

    def populate(self):
        """Populate the main table with the results of a flint query."""
        raise NotImplementedError

    def filter(self):
        """Decide whether to display an Entity. Unused currently."""
        # raise NotImplementedError

    def onSelectedRowChanged(self, selectedItems):
        """Handle the selected row in the main table being changed. Subclass implementations should call this
        method so that the infocard view is updated."""
        principal, *_ = selectedItems
        self.infocardView.setText(principal.infocard())
        return principal


class BasesPage(DatabasePage):
    """Database page for bases."""
    mainTableHeadings = ['Base', 'Owner', 'System', 'Sector', 'Region', 'Base Nickname', 'System Nickname',
                         'Name ID', 'Info ID']

    def __init__(self, parent, infocardView):
        self.marketBox = QtWidgets.QGroupBox('Market')
        self.marketLayout = QtWidgets.QHBoxLayout()
        self.marketBox.setLayout(self.marketLayout)
        self.commodityTable = SimpleTable(['Commodity', 'Price', 'Sells'])
        self.equipmentTable = SimpleTable(['Equipment', 'Type', 'Price'])
        self.shipTable = SimpleTable(['Ship', 'Class', 'Package price'])
        self.marketLayout.addWidget(self.commodityTable)
        self.marketLayout.addWidget(self.equipmentTable)
        self.marketLayout.addWidget(self.shipTable)

        super().__init__(parent, infocardView, secondaryWidget=self.marketBox)

    def populate(self):
        self.mainTable.populate([
            [
                BaseItem(base),
                GenericItem(base.solar().owner().name()),
                GenericItem(base.system_().name()),
                GenericItem(base.sector()),
                GenericItem(base.system_().region()),
                MonospaceItem(base.nickname),
                MonospaceItem(base.system_().nickname),
                GenericItem(base.ids_name),
                GenericItem(base.solar().ids_info),
            ]
            for base in fl.bases if base.has_solar()]
        )

    def onSelectedRowChanged(self, selectedItems):
        base = super().onSelectedRowChanged(selectedItems)
        self.commodityTable.populate([
            [
                GenericItem(commodity.name()),
                CreditsItem(price),
                BooleanItem(commodity in base.sells_commodities()),
            ] for commodity, price in {**base.sells_commodities(), **base.buys_commodities()}.items() if commodity
        ]
        )
        self.commodityTable.sortByColumn(2, QtCore.Qt.DescendingOrder)  # sort by "sells" column

        self.equipmentTable.populate([
                [
                    GenericItem(equipment.name()),
                    GenericItem(type(equipment).__name__),
                    CreditsItem(price),
                ] for equipment, price in base.sells_equipment().items() if equipment
            ]  # todo: rep required
        )

        self.shipTable.populate([
            [
                GenericItem(ship.name()),
                GenericItem(ship.type()),
                CreditsItem(price),
            ] for ship, price in base.sells_ships().items() if ship
        ]
        )


class CommoditiesPage(DatabasePage):
    """Database page for commodities."""
    mainTableHeadings = ['Commodity', 'Default price', 'Volume', 'Decay', 'Nickname', 'Name ID', 'Info ID']

    def __init__(self, parent, infocardView):
        marketBox = QtWidgets.QGroupBox('Economy')
        marketLayout = QtWidgets.QHBoxLayout()
        marketBox.setLayout(marketLayout)
        self.economyTable = SimpleTable(['Base', 'System', 'Price', 'Sells'])
        marketLayout.addWidget(self.economyTable)

        super().__init__(parent, infocardView, secondaryWidget=marketBox)

    def populate(self):
        self.mainTable.populate([
            [
                CommodityItem(commodity),
                CreditsItem(commodity.good().price),
                NumberItem(int(commodity.volume)),
                NumberItem(int(commodity.decay_per_second)),
                MonospaceItem(commodity.nickname),
                GenericItem(commodity.ids_name),
                GenericItem(commodity.ids_info),
            ]
            for commodity in fl.commodities]
        )

    def onSelectedRowChanged(self, selectedItems):
        commodity = super().onSelectedRowChanged(selectedItems)
        sold, bought = commodity.sold_at(), commodity.bought_at()

        self.economyTable.populate([
            [
                BaseItem(base),
                SystemItem(base.system_()),
                CreditsItem(price),
                BooleanItem(base in sold)
            ]
            for base, price in {**bought, **sold}.items() if base.has_solar()
        ])
        self.economyTable.sortByColumn(3, QtCore.Qt.DescendingOrder)  # sort by "sells" column


class EquipmentPage(DatabasePage):
    """Abstract. A page for a type of equipment."""
    mainTableHeadings = ['Name', 'Price', 'Nickname', 'Name ID', 'Info ID']
    equipmentType: Type[fl.entities.Equipment] = fl.entities.Equipment

    def __init__(self, parent, infocardView):
        availabilityBox = QtWidgets.QGroupBox('Availability')
        availabilityLayout = QtWidgets.QHBoxLayout()
        availabilityBox.setLayout(availabilityLayout)
        self.economyTable = SimpleTable(['Base', 'System', 'IFF'])
        availabilityLayout.addWidget(self.economyTable)

        super().__init__(parent, infocardView, secondaryWidget=availabilityBox)

    def populate(self):
        """This base implementation populates the main table with fields common to all equipment types."""
        self.mainTable.populate([
            [
                EntityItem(equipment),
                CreditsItem(equipment.price()),
                MonospaceItem(equipment.nickname),
                GenericItem(equipment.ids_name),
                GenericItem(equipment.ids_info)
            ]
            for equipment in fl.equipment.of_type(self.equipmentType) if equipment.good()
        ])

    def onSelectedRowChanged(self, selectedItems):
        equipment = super().onSelectedRowChanged(selectedItems)
        self.economyTable.populate([
            [
                BaseItem(base),
                SystemItem(base.system_()),
                FactionItem(base.owner()),
            ] for base in equipment.sold_at() if base.has_solar()
        ])


class GunsPage(EquipmentPage):
    """Database page displaying countermeasure droppers.
    Todo: needs stats from fl.entities.Munition."""
    mainTableHeadings = ['Name', 'Price', 'Power usage', 'Refire', 'Muzzle velocity', 'Nickname',
                         'Name ID', 'Info ID']
    equipmentType = fl.entities.Gun

    def populate(self):
        self.mainTable.populate([
            [
                EntityItem(gun),
                CreditsItem(gun.price()),
                NumberItem(gun.power_usage),
                NumberItem(1 / gun.refire_delay),
                NumberItem(gun.muzzle_velocity),
                MonospaceItem(gun.nickname),
                GenericItem(gun.ids_name),
                GenericItem(gun.ids_info)
            ]
            for gun in fl.equipment.of_type(self.equipmentType) if gun.good()
        ])


class ThrustersPage(EquipmentPage):
    """Database page displaying thrusters."""
    mainTableHeadings = ['Name', 'Hit points', 'Cargo space', 'Energy/s', 'Price', 'Nickname', 'Name ID', 'Info ID']
    equipmentType = fl.entities.Thruster

    def populate(self):
        self.mainTable.populate([
            [
                EntityItem(thruster),
                NumberItem(thruster.hit_pts),
                NumberItem(thruster.volume),
                NumberItem(thruster.power_usage),
                CreditsItem(thruster.price()),
                MonospaceItem(thruster.nickname),
                GenericItem(thruster.ids_name),
                GenericItem(thruster.ids_info),
            ]
            for thruster in fl.equipment.of_type(self.equipmentType) if thruster.good()
        ])


class IDsPage(EquipmentPage):
    """Database page displaying unofficial (non-serverside) IDs."""
    mainTableHeadings = ['Name', 'Nickname', 'Name ID', 'Info ID']
    equipmentType = fl.entities.Tractor

    def populate(self):
        self.mainTable.populate([
            [
                EntityItem(tractor),
                MonospaceItem(tractor.nickname),
                GenericItem(tractor.ids_name),
                GenericItem(tractor.ids_info),
            ]
            for tractor in fl.equipment.of_type(self.equipmentType) if tractor.good()
        ])


class ArmourPage(EquipmentPage):
    """Database page displaying armour upgrades."""
    mainTableHeadings = ['Name', 'Price', 'Hit points multiplier', 'Nickname', 'Name ID', 'Info ID']
    equipmentType = fl.entities.Armor

    def populate(self):
        self.mainTable.populate([
            [
                EntityItem(armour),
                CreditsItem(armour.price()),
                NumberItem(armour.hit_pts_scale),
                MonospaceItem(armour.nickname),
                GenericItem(armour.ids_name),
                GenericItem(armour.ids_info),
            ]
            for armour in fl.equipment.of_type(self.equipmentType) if armour.good()
        ])


class CountermeasuresPage(EquipmentPage):
    """Database page displaying countermeasure droppers.
    Todo: needs stats from fl.entities.CounterMeasure."""
    equipmentType = fl.entities.CounterMeasureDropper


class MinesPage(EquipmentPage):
    """Database page displaying mine droppers.
    Todo: needs stats from fl.entities.Mine."""
    equipmentType = fl.entities.MineDropper


class CloaksPage(EquipmentPage):
    """Database page displaying cloaking devices.
    Todo: needs stats."""
    equipmentType = fl.entities.CloakingDevice


class EnginesPage(EquipmentPage):
    """Database page displaying engines."""
    equipmentType = fl.entities.Engine


class ShieldsPage(EquipmentPage):
    """Database page displaying countermeasure droppers."""
    mainTableHeadings = ['Name', 'Price', 'Technology', 'Capacity', 'Resistance', 'Cargo space',
                         'Nickname', 'Name ID', 'Info ID']
    equipmentType = fl.entities.ShieldGenerator

    def populate(self):
        self.mainTable.populate([
            [
                EntityItem(shield),
                CreditsItem(shield.price()),
                GenericItem(shield.shield_type),
                NumberItem(shield.max_capacity),
                NumberItem(shield.explosion_resistance),
                NumberItem(shield.volume),
                MonospaceItem(shield.nickname),
                GenericItem(shield.ids_name),
                GenericItem(shield.ids_info),
            ]
            # temp hack to ignore shield_module_c1_fluxcoil which has the trade lane ring infocard as its name...
            for shield in fl.equipment.of_type(self.equipmentType) if 'RDL' not in shield.name()
        ])


class ShipsPage(EquipmentPage):
    """Database page displaying ships."""
    mainTableHeadings = ['Ship', 'Class', 'Price', 'Hit points', 'Hold size', 'Bots', 'Bats', 'Nickname',
                         'Name ID', 'Info ID']

    def populate(self):
        self.mainTable.populate([[
                EntityItem(ship),
                GenericItem(ship.type()),
                CreditsItem(ship.price()),
                NumberItem(ship.hit_pts),
                NumberItem(ship.hold_size),
                NumberItem(ship.nanobot_limit),
                NumberItem(ship.shield_battery_limit),
                MonospaceItem(ship.nickname),
                GenericItem(ship.ids_name),
                GenericItem(ship.ids_info),
            ] for ship in fl.ships
        ])


class FactionsPage(DatabasePage):
    """Database page displaying factions."""
    mainTableHeadings = ['Faction', 'Short name', 'Legality', 'Nickname', 'Name ID', 'Info ID']

    def __init__(self, parent, infocardView):
        self.sheetBox = QtWidgets.QGroupBox('Rep sheet')
        sheetLayout = QtWidgets.QHBoxLayout()
        self.sheetBox.setLayout(sheetLayout)
        self.sheetTable = SimpleTable(['Faction', 'Reputation towards'])
        sheetLayout.addWidget(self.sheetTable)

        super().__init__(parent, infocardView, secondaryWidget=self.sheetBox)

    def populate(self):
        self.mainTable.populate([[
                FactionItem(faction),
                GenericItem(faction.short_name()),
                GenericItem(faction.legality()),
                MonospaceItem(faction.nickname),
                GenericItem(faction.ids_name),
                GenericItem(faction.ids_info),
        ] for faction in fl.factions])

    def onSelectedRowChanged(self, selectedItems):
        """Display the currently selected faction's rep hacks and rep sheet."""
        faction = super().onSelectedRowChanged(selectedItems)
        self.sheetTable.populate([
            [
                FactionItem(other_faction),
                NumberItem(rep_towards),
            ] for other_faction, rep_towards in faction.rep_sheet().items()
        ])
        self.sheetTable.sortByColumn(1, QtCore.Qt.DescendingOrder)  # sort by "reputation with" column
