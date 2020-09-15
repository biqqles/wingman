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

from ..database import layout
from ..boxes import configuration, about
from ... import config, IS_WIN

if IS_WIN:
    import flair
    from flair.augment import cli, clipboard, screenshot


class SimpleAction(QAction):
    """A simplified QAction abstraction."""
    def __init__(self, title: str, run: Callable = lambda: None, shortcut: str = '', tooltip='',
                 enabled=True, checkable=False):
        super().__init__(title)
        if shortcut:
            self.setShortcut(shortcut)
        if tooltip:
            self.setToolTip(tooltip)
        if checkable:
            self.toggled.connect(run)
        else:
            self.triggered.connect(run)
        self.setEnabled(enabled)
        self.setCheckable(checkable)


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

    def __init__(self, menuBar: QMenuBar):
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
    subprocess.call(fl.paths.construct_path('DSLauncher.exe'), cwd=config.install)


class Utilities(SimpleMenu):
    """'Utilities' menu."""
    title = '&Utilities'
    actions_ = [
        SimpleAction('&Database', lambda: layout.Database().exec(), 'Ctrl+D'),
    ]


class File(SimpleMenu):
    """'File' menu."""
    title = '&File'

    class Browser(SimpleMenu):
        """'Open in browser' submenu."""
        title = 'Open in browser'
        actions_ = [
            SimpleAction('Server &rules', lambda: openUrl(config.urls['rules'])),
            SimpleAction('House &laws', lambda: openUrl(config.urls['houselaws'])),
            SimpleAction('&Player status', lambda: openUrl(config.urls['playerstatus'])),
            SimpleAction('Online &navmap', lambda: openUrl(config.urls['navmap'])),
            SimpleAction('&Wiki', lambda: openUrl(config.urls['wiki'])),
            SimpleAction('&Forums', lambda: openUrl(config.urls['forums'])),
        ]

    actions_ = [
        SimpleAction('&Start launcher', startLauncher, shortcut='Ctrl+L', enabled=IS_WIN),
        SimpleAction('Open DSAce.log', lambda: openFile(config.dsace)),
        SimpleAction('Open Freelancer directory', lambda: openFile(config.install)),
        Separator(),
        SimpleAction('Reload game files', shortcut='Ctrl+R'),  # todo: run
    ]

    def __init__(self, menuBar: QMenuBar):
        self.submenus = [
            self.Browser(menuBar),
        ]
        super().__init__(menuBar)


class Freelancer(SimpleMenu):
    """'Freelancer' menu."""
    title = 'Fr&eelancer'
    augmentations: Set['flair.augment.Augmentation'] = set()

    class Augmentations(SimpleMenu):
        """'Augmentations' submenu."""
        title = 'Toggle client augmentations'
        actions_ = [
            SimpleAction('Clipboard', lambda c: Freelancer.toggleAugmentation(clipboard.Clipboard, c),
                         checkable=True,
                         tooltip='Adds clipboard functionality to the chat box. '
                                 'Use Ctrl+Shift+C to copy and Ctrl+Shift+V to paste'
                         ),
            SimpleAction('Named screenshots', lambda c: Freelancer.toggleAugmentation(screenshot.Screenshot, c),
                         checkable=True,
                         tooltip="Use Ctrl+PrintScreen to take a screenshot named using the current time and"
                                 " character's name and location.\nScreenshots are saved to"
                                 " Documents/My Games/Freelancer/Screenshots"
                         ),
            SimpleAction('Command line interface', lambda c: Freelancer.toggleAugmentation(cli.CLI, c),
                         checkable=True,
                         tooltip='Adds new commands to the chat box. Send "..help" to get started'
                         ),
        ]

    actions_ = [
        SimpleAction('Bring to foreground', shortcut='Ctrl+F', enabled=IS_WIN)
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

            if config['flair'].getboolean('clipboard'):
                self.submenus[0].actions_[0].toggle()
            if config['flair'].getboolean('screenshot'):
                self.submenus[0].actions_[1].toggle()
            if config['flair'].getboolean('cli'):
                self.submenus[0].actions_[2].toggle()
        else:
            self.submenus[0].setEnabled(False)
            self.actions_[0].setEnabled(False)

    @classmethod
    def toggleAugmentation(cls,  augmentation: Type['flair.augment.Augmentation'], toggled: bool):
        cls.loadAugmentation(augmentation) if toggled else cls.unloadAugmentation(augmentation)
        config['flair'][augmentation.__name__.lower()] = str(toggled)

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
        SimpleAction('Configure paths', lambda: configuration.ConfigurePaths().exec()),
        SimpleAction('Export preferences', lambda: Preferences.exportPreferences()),
        SimpleAction('Reset to defaults', config.reset),
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
        SimpleAction('Visit project thread', lambda: openUrl(config.urls['projectthread'])),
        SimpleAction('Visit project repo', lambda: openUrl(config.urls['repo'])),
        SimpleAction('About', lambda: about.About().exec()),
    ]
