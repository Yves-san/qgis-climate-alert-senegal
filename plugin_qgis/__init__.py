# -*- coding: utf-8 -*-
"""
Climate Alert Plugin - QGIS Plugin for Climate Risk Simulation in Senegal
"""

def classFactory(iface):
    from .climate_alert_plugin import ClimateAlertPlugin
    return ClimateAlertPlugin(iface)