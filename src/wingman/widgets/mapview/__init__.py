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
import os
from collections import defaultdict

import flint as fl
from PyQt5 import QtWebEngineWidgets, QtCore, QtWidgets, QtGui

from ..buttons import SquareButton
from ... import config, icons, NAVMAP_DIR

DEV_JS_PATH = './widgets/mapview/navmap.js'


class MapView(QtWebEngineWidgets.QWebEngineView):
    """
    A widget that attempts to display Space's Interactive Navmap <http://space.discoverygc.com/navmap/> in such a way
    that it is seamlessly integrated into the native application.
    """
    navmapReady = QtCore.pyqtSignal(name='navmapReady')
    loadCompleted = QtCore.pyqtSignal(str, name='loadCompleted')

    # noinspection PyArgumentList
    def __init__(self, parent=None, url=config.navmap):
        """Initialise the widget."""
        QtWebEngineWidgets.QWebEngineView.__init__(self)
        self.page().profile().setCachePath(NAVMAP_DIR)  # link cache directory
        self.setHtml('<body style="background-color: transparent"></body>')  # in case the page doesn't load
        self.setUrl(QtCore.QUrl(url))
        self.setMinimumSize(512, 512)
        # Resize while maintaining aspect ratio. After much experimenting this policy and the contents of resizeEvent
        # were the best I could come up with. It's not ideal, though - it doesn't handle ExpandedMap being maximised.
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHeightForWidth(True)
        sizePolicy.setRetainSizeWhenHidden(True)
        self.setSizePolicy(sizePolicy)

        self.hide()  # hide until navmap initialised - this prevents a white flash

        if parent:
            self.setParent(parent)

        self.executeJS = self.page().runJavaScript  # create a more convenient alias

        # load JavaScript from resources, or from a file if it exists (useful for debugging)
        if os.path.isfile(DEV_JS_PATH):
            js = open(DEV_JS_PATH).read()
        else:
            jsFile = QtCore.QFile(':/javascript/navmap.js')
            if jsFile.open(QtCore.QIODevice.ReadOnly | QtCore.QFile.Text):
                js = QtCore.QTextStream(jsFile).readAll()
            else:
                raise FileNotFoundError("MapView: couldn't load hook.")

        # inject script and call initialiseNavmap when ready
        script = QtWebEngineWidgets.QWebEngineScript()
        script.setSourceCode(js)
        script.setName('navmap.js')
        script.setWorldId(QtWebEngineWidgets.QWebEngineScript.MainWorld)
        script.setInjectionPoint(QtWebEngineWidgets.QWebEngineScript.DocumentReady)
        self.page().scripts().insert(script)

        self.waitForHookLoaded()

        # create control panel
        self.controlsFrame = QtWidgets.QFrame(self)
        self.controlsFrame.setMinimumSize(30, 135)
        controlsLayout = QtWidgets.QVBoxLayout(self.controlsFrame)
        controlsLayout.setContentsMargins(0, 0, 0, 0)
        self.connInfoB = SquareButton(tooltip='Connected systems', icon=icons.jump, dropdown=True, edge=30)
        controlsLayout.addWidget(self.connInfoB)
        self.forwardB = SquareButton(tooltip='Forward', text='⭢', edge=30)
        self.forwardB.clicked.connect(self.goForward)
        controlsLayout.addWidget(self.forwardB)
        self.backB = SquareButton(tooltip='Back', text='⭠', edge=30)
        self.backB.clicked.connect(self.goBack)
        controlsLayout.addWidget(self.backB)
        self.expandB = SquareButton(tooltip='Show expanded map', icon=icons.expand, edge=30)
        controlsLayout.addWidget(self.expandB)
        self.controlsFrame.setLayout(controlsLayout)
        self.controlsFrame.show()

        # create context menu actions I tried for ages to get these options to be persistent, but among other issues
        # Qt would not emit the toggled signal when setChecked was called with the parameter set to False! In the end
        # I just dropped it, so all options will just default to ON when the application is initialised

        self.menu = QtWidgets.QMenu()

        sendState = lambda selector: lambda state: self.executeJS(
            'wingman.setState({}, {})'.format(selector, str(state).lower()))

        self.showLabels = QtWidgets.QAction('Show labels', checkable=True, checked=True)
        self.showLabels.toggled.connect(sendState('wingman.showLabels'))
        self.showZones = QtWidgets.QAction('Show nebulae', checkable=True, checked=True)
        self.showZones.toggled.connect(sendState('wingman.showZones'))
        self.showWrecks = QtWidgets.QAction('Show wrecks', checkable=True, checked=True)
        self.showWrecks.toggled.connect(sendState('wingman.showWrecks'))

        self.menu.addActions([self.showLabels, self.showWrecks, self.showZones])
        self.menu.addAction('Save map as image').triggered.connect(self.saveAsImage)

        # configure settings
        settings = self.page().view().settings()
        settings.setAttribute(QtWebEngineWidgets.QWebEngineSettings.SpatialNavigationEnabled, True)
        settings.setAttribute(QtWebEngineWidgets.QWebEngineSettings.ShowScrollBars, False)

        # initialise history
        self.backStack = []
        self.forwardsStack = []

    def initialiseNavmap(self):
        """Inject Wingman's code into the web app and change its background colour to blend in with the rest of the
        interface. """
        # Change background colour to that of window. This is the colour that will be shown when the web app is
        # loading. I found that whatever I tried, even pulling pixels(!), I could not get Qt to return the actual,
        # displayed colour of the QTabWidget (m.tw). This seems to be a known issue (see
        # <https://stackoverflow.com/a/23020483>) with no published, easy workaround. Unfortunately, we cannot set
        # the background to Qt.transparent because of a bug which prevents other widgets from being placed on top,
        # see comments at <goo.gl/pz5w5M>. n.b. if this is ever fixed, self.setAttribute(
        # QtCore.Qt.WA_TranslucentBackground) is required as well.

        # get and set background colour of background widget
        backgroundWidget = self.parentWidget() if self.parentWidget() else QtWidgets.QWidget()
        colour = backgroundWidget.palette().color(backgroundWidget.backgroundRole())
        self.page().setBackgroundColor(colour)
        self.page().runJavaScript(f'wingman.setBackgroundColour({colour.name()!r})')

        self.history().clear()  # a fresh start is always nice!

        self.urlChanged.connect(self.onUrlChange)

        if self.parentWidget():
            self.show()
        self.navmapReady.emit()

    def onUrlChange(self):
        """Handle a URL change. Wait for the variable to set, then emit loadCompleted."""
        self.page().runJavaScript('currentSystemNickname', lambda n: self.loadCompleted.emit(n) if n != 'Sirius' else 0)

        # update state of forward/backward navigation buttons and history queue
        if self.getDisplayed() and '_' not in self.getDisplayed():
            if not self.backStack or self.getDisplayed() != self.backStack[-1]:
                self.backStack.append(self.getDisplayed())

        self.backB.setEnabled(bool(len(self.backStack) - 1))
        self.forwardB.setEnabled(bool(self.forwardsStack))

    def displayEntity(self, entity: fl.entities.Entity):
        """Change the displayed object (system or solar) to the given item."""
        self.displayMap(entity.name())

    def displayMap(self, entityName: str):
        self.executeJS(f'wingman.displayMap({entityName.title()!r})')

    def displayUniverse(self):
        """Display universe map."""
        self.executeJS("wingman.displayUniverseMap()")

    def getDisplayed(self):
        """Parse URL to resolve selected object (system/base/planet) name, or 'Sirius' if the universe map is
        displayed. """
        fragment = self.url().fragment().split('&')[0]
        return fragment.replace('%20', ' ')[2:].title().replace('%27', "'") if fragment else 'Sirius'

    def setDisplayed(self, entityName):
        """Set the URL fragment to the display name of an entity, causing it to be displayed (assuming it is in the
        navmap's search array. This is useful for guaranteeing a display update, for example if Wingman's hook may have
        not loaded yet."""
        url = self.url()
        query, noClick = list(url.fragment().split('&'))
        url.setFragment(f'q={entityName}&{noClick}')
        self.setUrl(url)
        self.onUrlChange()

    def displayConnMenu(self, forSystem: fl.entities.System):
        """Add a menu of connected systems, sorted by system name. Clicking on these systems will display that
        system. """
        menu = QtWidgets.QMenu()
        menu.setToolTipsVisible(True)

        # group jumps by system
        connections = defaultdict(list)
        for jump, system in forSystem.connections().items():
            connections[system].append(jump)

        for system, jumps in sorted(connections.items(), key=lambda s_j: s_j[0].name()):
            action = menu.addAction(f'{system.name()} ({", ".join(j.type() for j in jumps)})')
            action.triggered.connect(lambda _, system=system: self.displayEntity(system))
            action.setToolTip(", ".join(j.sector() for j in jumps))
        self.connInfoB.setMenu(menu)

    def saveAsImage(self):
        """Show a dialogue allowing the user to save the currently displayed map as a PNG image."""
        defaultPath = os.path.expanduser('~/{}.png').format(self.getDisplayed())
        path = QtWidgets.QFileDialog.getSaveFileName(self,
                                                     'Save map as image',
                                                     defaultPath,
                                                     'Portable Network Graphics image (*.png)')[0]
        # Hide controls. Consider also temporarily setting the background to colour of forums (#090909) so it blends
        # in well
        self.controlsFrame.hide()
        # draw image
        image = QtGui.QImage(self.geometry().width(), self.geometry().height(), QtGui.QImage.Format_ARGB32)
        painter = QtGui.QPainter()
        painter.begin(image)
        self.page().view().render(painter)
        painter.end()

        if path:
            image.save(path)
        self.controlsFrame.show()

    def contextMenuEvent(self, event):
        """Provides a context menu that contains options to change the display settings of the map and save it as an
        image."""
        self.menu.exec(self.mapToGlobal(QtCore.QPoint(event.pos())))

    def resizeEvent(self, event):
        """Handle a resize event so that the widget stays square."""
        self.setMaximumWidth(self.height())
        self.controlsFrame.move(self.width() - 30, 0)  # keep controls stuck to top right

    def waitForHookLoaded(self, wingman=None):
        """Block until the hook has been loaded."""
        if wingman is None:
            try:
                self.page().runJavaScript('try {wingman} catch(error) {null}', self.waitForHookLoaded)
            except RuntimeError:  # thrown if process is killed
                return
        else:
            self.initialiseNavmap()

    def goForward(self):
        self.backStack.append(self.getDisplayed())
        self.displayMap(self.forwardsStack.pop())

    def goBack(self):
        self.forwardsStack.append(self.getDisplayed())
        self.backStack.pop()
        self.displayMap(self.backStack.pop())
