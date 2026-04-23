# -*- coding: utf-8 -*-
"""
Climate Alert Plugin - Main Plugin Class
"""

from qgis.PyQt.QtWidgets import QAction, QMainWindow
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import Qt, QSize
from qgis.core import QgsProject
import os

from .ui.main_dialog import ClimateAlertDialog


class ClimateAlertPlugin:
    """Main plugin class for Climate Alert"""

    def __init__(self, iface):
        """
        Constructor.

        :param iface: An interface instance that will be passed to this class
                which provides the hook by which you can manipulate the QGIS
                application at run time.
        :type iface: QgsInterface
        """
        self.iface = iface
        self.actions = []
        self.menu = 'Climate Alert'
        self.toolbar = self.iface.addToolBar('Climate Alert')
        self.toolbar.setObjectName('Climate Alert')
        self.dialog = None

    def add_action(self, icon_path, text, callback, enabled_flag=True, add_to_menu=True, add_to_toolbar=True, status_tip=None, whats_this=None, parent=None):
        """
        Add a toolbar icon to the Climate Alert toolbar.
        """
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(self.menu, action)

        self.actions.append(action)

        return action

    def initGui(self):
        """
        Create the menu entries and toolbar icons inside the QGIS GUI.
        """
        icon_path = os.path.join(os.path.dirname(__file__), 'resources', 'icon.png')
        self.add_action(
            icon_path,
            text='Climate Alert - Senegal',
            callback=self.run,
            parent=self.iface.mainWindow()
        )

    def unload(self):
        """
        Removes the plugin menu item and toolbar icon from QGIS GUI.
        """
        for action in self.actions:
            self.iface.removePluginMenu('&Climate Alert', action)
            self.iface.removeToolBarIcon(action)

        del self.toolbar

    def run(self):
        """
        Run method that performs all the real work
        """
        if self.dialog is None:
            self.dialog = ClimateAlertDialog(self.iface)

        self.dialog.show()
        self.dialog.raise_()
        self.dialog.activateWindow()