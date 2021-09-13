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
from collections import defaultdict
from math import degrees

from PyQt5 import QtWidgets

from ...widgets.simpletable import SimpleTable
from ...models.items import *


class DatabasePage(QtWidgets.QSplitter):
    """A page in the database, with a main table and a secondary widget which displays further information about the
    entity currently selected in the main table."""
    mainTableHeadings: List[str]

    def __init__(self, parent, secondaryWidget):
        super().__init__(parent=parent, orientation=QtCore.Qt.Vertical)
        self.infocardView = parent.infocardView
        self.secondaryWidget = secondaryWidget

        self.mainTable = SimpleTable(self.mainTableHeadings)
        self.mainTable.rowSelected.connect(self.onSelectedRowChanged)
        self.addWidget(self.mainTable)
        self.setStretchFactor(0, 3)

        self.addWidget(self.secondaryWidget)
        self.setStretchFactor(1, 1)
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

    def __init__(self, parent):
        self.marketBox = QtWidgets.QGroupBox('Market')
        self.marketLayout = QtWidgets.QHBoxLayout()
        self.marketBox.setLayout(self.marketLayout)
        self.commodityTable = SimpleTable(['Commodity', 'Price', 'Sells'])
        self.equipmentTable = SimpleTable(['Equipment', 'Type', 'Price'])
        self.shipTable = SimpleTable(['Ship', 'Class', 'Package price'])
        self.marketLayout.addWidget(self.commodityTable)
        self.marketLayout.addWidget(self.equipmentTable)
        self.marketLayout.addWidget(self.shipTable)

        super().__init__(parent, secondaryWidget=self.marketBox)

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

    def __init__(self, parent):
        marketBox = QtWidgets.QGroupBox('Economy')
        marketLayout = QtWidgets.QHBoxLayout()
        marketBox.setLayout(marketLayout)
        self.economyTable = SimpleTable(['Base', 'System', 'Price', 'Sells', 'Nickname'])
        marketLayout.addWidget(self.economyTable)

        super().__init__(parent, secondaryWidget=marketBox)

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
                BooleanItem(base in sold),
                MonospaceItem(base.nickname),
            ]
            for base, price in {**bought, **sold}.items() if base.has_solar()
        ])
        self.economyTable.sortByColumn(3, QtCore.Qt.DescendingOrder)  # sort by "sells" column


class EquipmentPage(DatabasePage):
    """Abstract. A page for a type of equipment."""
    mainTableHeadings = ['Name', 'Price', 'Nickname', 'Name ID', 'Info ID']
    equipmentType: Type[fl.entities.Equipment] = fl.entities.Equipment

    def __init__(self, parent):
        availabilityBox = QtWidgets.QGroupBox('Availability')
        availabilityLayout = QtWidgets.QHBoxLayout()
        availabilityBox.setLayout(availabilityLayout)
        self.economyTable = SimpleTable(['Base', 'System', 'IFF', 'Nickname'])
        availabilityLayout.addWidget(self.economyTable)

        super().__init__(parent, secondaryWidget=availabilityBox)

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
            for equipment in fl.equipment.of_type(self.equipmentType) if equipment.is_valid()
        ])

    def onSelectedRowChanged(self, selectedItems):
        equipment = super().onSelectedRowChanged(selectedItems)
        self.economyTable.populate([
            [
                BaseItem(base),
                SystemItem(base.system_()),
                FactionItem(base.owner()),
                MonospaceItem(base.nickname),
            ] for base in equipment.sold_at() if base.has_solar()
        ])


class GunsPage(EquipmentPage):
    """Database page displaying guns."""
    mainTableHeadings = ['Name', 'Price', 'Hardpoint', 'Energy/shot', 'Refire', 'Speed (ms⁻¹)', 'Range (m)',
                         'Dispersion (°)', 'Hull dmg', 'Shield dmg', 'Hull dps', 'Shield dps', 'Energy/s', 'Efficiency',
                         'Technology', 'Nickname', 'Name ID', 'Info ID']
    equipmentType = fl.entities.Gun

    @staticmethod
    def gunDiscriminator(gun: fl.entities.Gun) -> bool:
        """Determine what type of gun this is."""
        return gun.is_valid() and not (gun.is_turret() or gun.is_missile())

    def populate(self):
        self.mainTable.populate([
            [
                EntityItem(gun),
                CreditsItem(gun.price()),
                MonospaceItem(gun.hp_gun_type),
                NumberItem(gun.power_usage),
                NumberItem(gun.refire()),
                NumberItem(gun.muzzle_velocity),
                NumberItem(gun.range()),
                NumberItem(gun.dispersion_angle),
                NumberItem(gun.hull_damage()),
                NumberItem(gun.shield_damage()),
                NumberItem(gun.hull_dps()),
                NumberItem(gun.shield_dps()),
                NumberItem(gun.energy_per_second()),
                NumberItem(gun.efficiency()),
                MonospaceItem(gun.technology()),
                MonospaceItem(gun.nickname),
                GenericItem(gun.ids_name),
                GenericItem(gun.ids_info)
            ]
            for gun in fl.equipment.of_type(self.equipmentType) if self.gunDiscriminator(gun)
        ])


class TurretsPage(GunsPage):
    @staticmethod
    def gunDiscriminator(gun: fl.entities.Gun) -> bool:
        """Determine what type of gun this is."""
        return gun.is_valid() and gun.is_turret()


class MissilesPage(EquipmentPage):
    """Database page displaying missiles."""
    mainTableHeadings = ['Name', 'Price', 'Hardpoint', 'Energy/shot', 'Seeking', 'CD', 'Refire', 'Hull dmg',
                         'Shield dmg', 'Range (m)', 'Muzzle velocity (ms⁻¹)', 'Acceleration (ms⁻²)', 'Motor delay (s)',
                         'Nickname', 'Name ID', 'Info ID']
    equipmentType = fl.entities.Gun

    @staticmethod
    def gunDiscriminator(gun: fl.entities.Gun) -> bool:
        """Determine what type of gun this is."""
        return gun.is_valid() and gun.is_missile()

    def populate(self):
        self.mainTable.populate([
            [
                EntityItem(missile),
                CreditsItem(missile.price()),
                MonospaceItem(missile.hp_gun_type),
                NumberItem(missile.power_usage),
                BooleanItem(missile.munition().seeker == 'lock'),
                BooleanItem(missile.munition().cruise_disruptor or False),
                NumberItem(missile.refire()),
                NumberItem(missile.hull_damage()),
                NumberItem(missile.shield_damage()),
                NumberItem(missile.range()),
                NumberItem(missile.muzzle_velocity),
                NumberItem(missile.munition().motor_().accel if missile.munition().motor_() else 0),
                NumberItem(missile.munition().motor_().delay if missile.munition().motor_() else 0),
                MonospaceItem(missile.nickname),
                GenericItem(missile.ids_name),
                GenericItem(missile.ids_info)
            ]
            for missile in fl.equipment.of_type(self.equipmentType) if self.gunDiscriminator(missile)
        ])


class ThrustersPage(EquipmentPage):
    """Database page displaying thrusters."""
    mainTableHeadings = ['Name', 'Price', 'Hit points', 'Cargo space', 'Fuel/s', 'Nickname', 'Name ID', 'Info ID']
    equipmentType = fl.entities.Thruster

    def populate(self):
        self.mainTable.populate([
            [
                EntityItem(thruster),
                CreditsItem(thruster.price()),
                NumberItem(thruster.hit_pts),
                NumberItem(thruster.volume),
                NumberItem(thruster.power_usage),
                MonospaceItem(thruster.nickname),
                GenericItem(thruster.ids_name),
                GenericItem(thruster.ids_info),
            ]
            for thruster in fl.equipment.of_type(self.equipmentType) if thruster.is_valid()
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
            for tractor in fl.equipment.of_type(self.equipmentType) if tractor.is_valid()
        ])


class ArmourPage(EquipmentPage):
    """Database page displaying armour upgrades."""
    mainTableHeadings = ['Name', 'Price', 'Cargo space', 'Health multiplier', 'Nickname', 'Name ID', 'Info ID']
    equipmentType = fl.entities.Armor

    def populate(self):
        self.mainTable.populate([
            [
                EntityItem(armour),
                CreditsItem(armour.price()),
                NumberItem(int(armour.volume)),
                NumberItem(armour.hit_pts_scale),
                MonospaceItem(armour.nickname),
                GenericItem(armour.ids_name),
                GenericItem(armour.ids_info),
            ]
            for armour in fl.equipment.of_type(self.equipmentType) if armour.is_valid()
        ])


class CountermeasuresPage(EquipmentPage):
    """Database page displaying countermeasure droppers."""
    mainTableHeadings = ['Name', 'Dropper price', 'Flare price', 'Max flares', 'Refire', 'Range (m)', 'Effectiveness',
                         'Lifetime (s)', 'Nickname', 'Name ID', 'Info ID']
    equipmentType = fl.entities.CounterMeasureDropper

    def populate(self):
        """This base implementation populates the main table with fields common to all equipment types."""
        self.mainTable.populate([
            [
                EntityItem(dropper),
                CreditsItem(dropper.price()),
                CreditsItem(dropper.countermeasure().price()),
                NumberItem(dropper.countermeasure().ammo_limit),
                NumberItem(dropper.refire()),
                NumberItem(dropper.countermeasure().range),
                PercentageItem(dropper.countermeasure().effectiveness()),
                NumberItem(dropper.countermeasure().lifetime),
                MonospaceItem(dropper.nickname),
                GenericItem(dropper.ids_name),
                GenericItem(dropper.ids_info)
            ]
            for dropper in fl.equipment.of_type(self.equipmentType) if dropper.countermeasure()
        ])


class MinesPage(EquipmentPage):
    """Database page displaying mine droppers."""
    mainTableHeadings = ['Name', 'Dropper price', 'Ammo price', 'Max ammo', 'Refire', 'Hull dmg', 'Shield dmg',
                         'Explosive radius (m)', 'Seek distance (m)', 'Max speed (ms⁻¹)', 'Acceleration (ms⁻²)',
                         'Lifetime', 'Nickname', 'Name ID', 'Info ID']
    equipmentType = fl.entities.MineDropper

    def populate(self):
        """This base implementation populates the main table with fields common to all equipment types."""
        self.mainTable.populate([
            [
                EntityItem(dropper),
                CreditsItem(dropper.price()),
                CreditsItem(dropper.mine().price()),
                NumberItem(dropper.mine().ammo_limit),
                NumberItem(dropper.refire()),
                NumberItem(dropper.hull_damage()),
                NumberItem(dropper.shield_damage()),
                NumberItem(dropper.mine().explosion().radius),
                NumberItem(dropper.mine().seek_dist),
                NumberItem(dropper.mine().top_speed),
                NumberItem(dropper.mine().acceleration),
                NumberItem(dropper.mine().lifetime),
                MonospaceItem(dropper.nickname),
                GenericItem(dropper.ids_name),
                GenericItem(dropper.ids_info)
            ]
            for dropper in fl.equipment.of_type(self.equipmentType)
        ])


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
                MonospaceItem(shield.shield_type),
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


class ShipsPage(DatabasePage):
    """Database page displaying ships."""
    mainTableHeadings = ['Ship', 'Class', 'Package price', 'Hit points',
                         'Turn rate (°/s)', 'Distance 0-0.5s (°)', 'Response (s)',
                         'Hold size', 'Bots', 'Bats', 'Power core', 'Recharge',
                         'Impulse speed (ms⁻¹)', 'Reverse speed (ms⁻¹)', 'Cruise delay (s)',
                         'Nickname', 'Name ID', 'Info ID']

    def __init__(self, parent):
        secondaryWidget = QtWidgets.QWidget(parent)
        secondaryLayout = QtWidgets.QHBoxLayout()
        secondaryWidget.setLayout(secondaryLayout)

        availabilityBox = QtWidgets.QGroupBox('Availability')
        availabilityLayout = QtWidgets.QHBoxLayout()
        availabilityBox.setLayout(availabilityLayout)
        self.economyTable = SimpleTable(['Base', 'System', 'IFF', 'Nickname'])
        availabilityLayout.addWidget(self.economyTable)

        hardpointsBox = QtWidgets.QGroupBox('Hardpoints')
        hardpointsLayout = QtWidgets.QHBoxLayout()
        hardpointsBox.setLayout(hardpointsLayout)
        self.hardpointsTabs = QtWidgets.QTabWidget()

        self.weaponsTable = SimpleTable([])
        self.weaponsTable.verticalHeader().show()
        self.weaponsTable.horizontalHeader().hide()
        self.hardpointsTabs.addTab(self.weaponsTable, 'Weapons')

        self.externalTable = SimpleTable([])
        self.externalTable.verticalHeader().show()
        self.externalTable.horizontalHeader().hide()
        self.hardpointsTabs.addTab(self.externalTable, 'External')

        self.internalTable = SimpleTable([])
        self.internalTable.verticalHeader().show()
        self.internalTable.horizontalHeader().hide()
        self.hardpointsTabs.addTab(self.internalTable, 'Internal')

        hardpointsLayout.addWidget(self.hardpointsTabs)

        secondaryLayout.addWidget(availabilityBox)
        secondaryLayout.addWidget(hardpointsBox)

        super().__init__(parent, secondaryWidget=secondaryWidget)

    def populate(self):
        self.mainTable.populate([[
                EntityItem(ship),
                GenericItem(ship.type()),
                CreditsItem(ship.price()),
                NumberItem(ship.hit_pts),
                NumberItem(degrees(ship.turn_rate())),
                NumberItem(degrees(ship.angular_distance_in_time(0.5))),
                NumberItem(ship.response()),
                NumberItem(ship.hold_size),
                NumberItem(ship.nanobot_limit),
                NumberItem(ship.shield_battery_limit),
                NumberItem(ship.power_core().capacity),
                NumberItem(ship.power_core().charge_rate),
                NumberItem(ship.impulse_speed()),
                NumberItem(ship.reverse_speed()),
                NumberItem(ship.cruise_charge_time()),
                MonospaceItem(ship.nickname),
                GenericItem(ship.ids_name),
                GenericItem(ship.ids_info),
            ] for ship in fl.ships if ship.package()
        ])

    def onSelectedRowChanged(self, selectedItems):
        ship = super().onSelectedRowChanged(selectedItems)
        self.economyTable.populate([
            [
                BaseItem(base),
                SystemItem(base.system_()),
                FactionItem(base.owner()),
                MonospaceItem(base.nickname),
            ] for base in ship.sold_at() if base.has_solar()
        ])

        # organise hardpoints by category
        hardpoint_items = defaultdict(list)
        for h in ship.hardpoints().values():
            hardpoint_items[h[0].category()].append(GenericItem(' OR '.join((w.name() for w in h))))

        self.weaponsTable.populate(hardpoint_items['weapons'])
        self.weaponsTable.model().sort(-1)

        self.externalTable.populate(hardpoint_items['external'])
        self.externalTable.model().sort(-1)

        self.internalTable.populate(hardpoint_items['internal'])
        self.internalTable.model().sort(-1)


class FactionsPage(DatabasePage):
    """Database page displaying factions."""
    mainTableHeadings = ['Faction', 'Short name', 'Legality', 'Nickname', 'Name ID', 'Info ID']

    def __init__(self, parent):
        self.sheetBox = QtWidgets.QGroupBox('Rep sheet')
        sheetLayout = QtWidgets.QHBoxLayout()
        self.sheetBox.setLayout(sheetLayout)
        self.sheetTable = SimpleTable(['Faction', 'Reputation towards'])
        sheetLayout.addWidget(self.sheetTable)

        super().__init__(parent, secondaryWidget=self.sheetBox)

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
                RepItem(rep_towards),
            ] for other_faction, rep_towards in faction.rep_sheet().items()
        ])
        self.sheetTable.sortByColumn(1, QtCore.Qt.DescendingOrder)  # sort by "reputation with" column
