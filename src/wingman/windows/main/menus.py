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

This file defines the menus for the application's main window.
"""
from typing import Callable, List, Type, Set
import os.path
import subprocess

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QMenu, QAction, QMenuBar, QFileDialog
import flint as fl

from ..database.layout import Database
from ..boxes import configuration, about
from ... import config, IS_WIN

if IS_WIN:
    import flair
    from flair.augment import cli, clipboard, screenshot


# noinspection PyMissingOrEmptyDocstring
class SimpleAction(QAction):
    """A declarative QAction abstraction."""
    def onTrigger(self, callback: Callable):
        self.triggered.connect(callback)
        return self

    def onToggle(self, callback: Callable):
        self.toggled.connect(callback)
        return self

    def withShortcut(self, shortcut: str):
        self.setShortcut(shortcut)
        return self

    def withTooltip(self, tooltip: str):
        self.setToolTip(tooltip)
        return self

    def checkable(self):
        self.setCheckable(True)
        return self

    def disableIf(self, condition: bool):
        self.setDisabled(condition)
        return self

    def withConfig(self, section: str, key: str):
        self.triggered.connect(lambda state: config[section].update({key: str(state)}))
        if self.isEnabled() and config[section].getboolean(key):
            self.trigger()
        return self


class Separator(QAction):
    """A menu separator."""
    def __init__(self):
        super().__init__()
        self.setSeparator(True)


class SimpleMenu(QMenu):
    """A simplified QMenu abstraction."""
    title: str
    submenus: List['SimpleMenu'] = []
    actions_: List[SimpleAction]
    tooltip = ''

    def __init__(self, menuBar: QMenuBar = None):
        super().__init__(self.title, menuBar)
        self.setToolTipsVisible(True)
        for menu in self.submenus:
            self.addMenu(menu)
        self.addActions(self.actions_)


def openUrl(url: str):
    """Open a url in the default browser."""
    # noinspection PyArgumentList, PyCallByClass
    QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))


def openFile(path: str):
    """Open a file in the default application."""
    # noinspection PyArgumentList, PyCallByClass
    QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(path))


def startLauncher():
    """Start the Discovery launcher in the configured installation directory."""
    subprocess.Popen(fl.paths.construct_path('DSLauncher.exe'), cwd=config.install)


class Utilities(SimpleMenu):
    """'Utilities' menu."""
    title = '&Utilities'
    actions_ = [
        SimpleAction('&Database')
            .withTooltip(Database.tooltip)
            .onTrigger(lambda: Database().exec()),
    ]


class File(SimpleMenu):
    """'File' menu."""
    title = '&File'

    class Browser(SimpleMenu):
        """'Open in browser' submenu."""
        title = 'Open in browser'
        actions_ = [
            SimpleAction('Server &rules')
                .onTrigger(lambda: openUrl(config.urls['rules'])),

            SimpleAction('House &laws')
                .onTrigger(lambda: openUrl(config.urls['houselaws'])),

            SimpleAction('&Player status')
                .onTrigger(lambda: openUrl(config.urls['playerstatus'])),

            SimpleAction('Online &navmap')
                .onTrigger(lambda: openUrl(config.urls['navmap'])),

            SimpleAction('&Wiki')
                .onTrigger(lambda: openUrl(config.urls['wiki'])),

            SimpleAction('&Forums')
                .onTrigger(lambda: openUrl(config.urls['forums'])),
        ]

    actions_ = [
        SimpleAction('&Start launcher')
            .withShortcut('Ctrl+L')
            .disableIf(not IS_WIN)
            .onTrigger(startLauncher),

        SimpleAction('Open DSAce.log')
            .onTrigger(lambda: openFile(config.dsace)),

        SimpleAction('Open Freelancer directory')
            .onTrigger(lambda: openFile(config.install)),

        Separator(),

        SimpleAction('Reload game files')  # todo: run
            .withShortcut('Ctrl+R'),
    ]

    submenus = [
        Browser()
    ]


class Freelancer(SimpleMenu):
    """'Freelancer' menu."""
    title = 'Fr&eelancer'
    augmentations: Set['flair.augment.Augmentation'] = set()

    class Augmentations(SimpleMenu):
        """'Augmentations' submenu."""
        title = 'Toggle client augmentations'
        actions_ = [
            SimpleAction('Clipboard')
                .checkable()
                .withTooltip('Adds clipboard functionality to the chat box. '
                             'Use Ctrl+Shift+C to copy and Ctrl+Shift+V to paste')
                .disableIf(not IS_WIN)
                .onTrigger(lambda c: Freelancer.toggleAugmentation(clipboard.Clipboard, c)),

            SimpleAction('Named screenshots')
                .checkable()
                .withTooltip("Use Ctrl+PrintScreen to take a screenshot named using the current time and"
                             " character's name and location.\nScreenshots are saved to"
                             " Documents/My Games/Freelancer/Screenshots")
                .disableIf(not IS_WIN)
                .onTrigger(lambda c: Freelancer.toggleAugmentation(screenshot.Screenshot, c)),

            SimpleAction('Command line interface')
                .checkable()
                .withTooltip('Adds new commands to the chat box. Send "..help" to get started')
                .disableIf(not IS_WIN)
                .onTrigger(lambda c: Freelancer.toggleAugmentation(cli.CLI, c))
        ]

        def __init__(self, menuBar):
            super().__init__(menuBar)  # todo: this is ugly but required for delayed loading of augmentations
            self.actions_[0].withConfig('flair', 'clipboard')
            self.actions_[1].withConfig('flair', 'screenshot')
            self.actions_[2].withConfig('flair', 'cli')

    actions_ = [
        SimpleAction('Bring to foreground')
            .withShortcut('Ctrl+F')
            .disableIf(not IS_WIN)
    ]

    def __init__(self, menuBar):
        self.submenus = [
            self.Augmentations(menuBar)
        ]
        super().__init__(menuBar)
        if IS_WIN:
            self.actions_[0].setEnabled(flair.state.running)
            flair.events.freelancer_started.connect(lambda: self.actions_[0].setEnabled(True))
            flair.events.freelancer_stopped.connect(lambda: self.actions_[0].setEnabled(False))
            self.actions_[0].triggered.connect(flair.hook.window.make_foreground)
        else:
            self.submenus[0].setEnabled(False)

    @classmethod
    def toggleAugmentation(cls,  augmentation: Type['flair.augment.Augmentation'], toggled: bool):
        cls.loadAugmentation(augmentation) if toggled else cls.unloadAugmentation(augmentation)

    @classmethod
    def loadAugmentation(cls, augmentation: Type['flair.augment.Augmentation']):
        instance = augmentation(flair.state)
        cls.augmentations.add(instance)
        instance.load()

    @classmethod
    def unloadAugmentation(cls, augmentation: Type['flair.augment.Augmentation']):
        instance = next(filter(lambda a: isinstance(a, augmentation), cls.augmentations))
        instance.unload()


class Preferences(SimpleMenu):
    """'Preferences' menu."""
    title = '&Preferences'

    actions_ = [
        SimpleAction('Configure paths')
            .onTrigger(lambda: configuration.ConfigurePaths().exec()),
        SimpleAction('Export preferences')
            .onTrigger(lambda: Preferences.exportPreferences()),
        SimpleAction('Reset to defaults')
            .onTrigger(config.reset),
    ]

    @staticmethod
    def exportPreferences():
        """Show a dialogue to make a copy of the preferences file."""
        path = QFileDialog.getSaveFileName(caption='Export preferences', directory=os.path.expanduser('~/wingman.cfg'),
                                           filter='Configuration files (*.cfg)',
                                           options=QFileDialog.DontUseNativeDialog)
        if path[0]:
            config.saveAs(path[0])


class Help(SimpleMenu):
    """'Help' menu."""
    title = '&Help'

    actions_ = [
        SimpleAction('Visit project thread')
            .onTrigger(lambda: openUrl(config.urls['projectthread'])),
        SimpleAction('Visit project repo')
            .onTrigger(lambda: openUrl(config.urls['repo'])),
        SimpleAction('About')
            .onTrigger(lambda: about.About().exec()),
    ]
