# -*- coding: utf-8 -*-
"""
Main Dialog for Climate Alert Plugin
"""

from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSlider,
    QComboBox, QTableWidget, QTableWidgetItem, QPushButton,
    QGroupBox, QSpinBox, QProgressBar
)
from qgis.PyQt.QtCore import Qt, QTimer
from qgis.PyQt.QtGui import QColor, QFont
from qgis.core import (
    QgsVectorLayer, QgsProject, QgsRectangle,
    QgsStyle, QgsRendererRange, QgsGraduatedSymbolRenderer,
    QgsSymbol
)
import json
import os


class ClimateAlertDialog(QDialog):
    """Main dialog for Climate Alert simulation"""

    def __init__(self, iface, parent=None):
        super().__init__(parent)
        self.iface = iface
        self.current_year = 2026
        self.scenario = "Moyen"
        self.setWindowTitle("Climate Alert - Sénégal (2026-2046)")
        self.setGeometry(100, 100, 1000, 600)
        self.init_ui()
        self.load_data()

    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()

        # Title
        title = QLabel("Simulation des Risques Climatiques - Sénégal 2026-2046")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Controls layout
        controls_layout = QHBoxLayout()

        # Scenario selector
        controls_layout.addWidget(QLabel("Scénario:"))
        self.scenario_combo = QComboBox()
        self.scenario_combo.addItems(["Optimiste", "Moyen", "Pessimiste"])
        self.scenario_combo.setCurrentText("Moyen")
        self.scenario_combo.currentTextChanged.connect(self.on_scenario_changed)
        controls_layout.addWidget(self.scenario_combo)

        controls_layout.addSpacing(20)

        # Year slider
        controls_layout.addWidget(QLabel("Année:"))
        self.year_slider = QSlider(Qt.Horizontal)
        self.year_slider.setMinimum(2026)
        self.year_slider.setMaximum(2046)
        self.year_slider.setValue(2026)
        self.year_slider.setTickPosition(QSlider.TicksBelow)
        self.year_slider.setTickInterval(5)
        self.year_slider.sliderMoved.connect(self.on_year_changed)
        controls_layout.addWidget(self.year_slider)

        self.year_label = QLabel("2026")
        controls_layout.addWidget(self.year_label)

        layout.addLayout(controls_layout)

        # Risk summary table
        group_risks = QGroupBox("Résumé des Risques par Région")
        table_layout = QVBoxLayout()
        self.risks_table = QTableWidget()
        self.risks_table.setColumnCount(4)
        self.risks_table.setHorizontalHeaderLabels(["Région", "Inondation (%)", "Sécheresse (%)", "Érosion (%)"])
        self.risks_table.setRowCount(6)  # 6 regions
        table_layout.addWidget(self.risks_table)
        group_risks.setLayout(table_layout)
        layout.addWidget(group_risks)

        # Recommendations
        group_reco = QGroupBox("Recommandations Agricoles")
        reco_layout = QVBoxLayout()
        self.reco_text = QLabel()
        self.reco_text.setWordWrap(True)
        self.reco_text.setText("Sélectionnez une année et un scénario pour voir les recommandations")
        reco_layout.addWidget(self.reco_text)
        group_reco.setLayout(reco_layout)
        layout.addWidget(group_reco)

        # Export button
        export_btn = QPushButton("Exporter Rapport")
        export_btn.clicked.connect(self.export_report)
        layout.addWidget(export_btn)

        self.setLayout(layout)

    def load_data(self):
        """Load climate data and scenarios"""
        # Load Senegal GeoJSON data
        plugin_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_path = os.path.join(plugin_dir, "data", "senegal_zones.geojson")

        if os.path.exists(data_path):
            layer = QgsVectorLayer(data_path, "Zones du Sénégal", "ogr")
            if layer.isValid():
                QgsProject.instance().addMapLayer(layer)
                self.iface.mapCanvas().setExtent(layer.extent())
                self.iface.mapCanvas().refresh()

        self.update_risks_table()

    def on_scenario_changed(self, scenario):
        """Handle scenario change"""
        self.scenario = scenario
        self.update_risks_table()
        self.update_recommendations()

    def on_year_changed(self):
        """Handle year slider change"""
        year = self.year_slider.value()
        self.current_year = year
        self.year_label.setText(str(year))
        self.update_risks_table()
        self.update_recommendations()

    def update_risks_table(self):
        """Update the risks table based on current scenario and year"""
        regions = ["Fleuve", "Saloum", "Casamance", "Sahel", "Côte", "Plateau"]
        years_passed = self.current_year - 2026
        multiplier = years_passed / 20  # 0 to 1

        scenario_factors = {
            "Optimiste": 0.5,
            "Moyen": 1.0,
            "Pessimiste": 1.5
        }
        factor = scenario_factors.get(self.scenario, 1.0)

        for idx, region in enumerate(regions):
            # Simulate risk progression
            inondation = min(100, int(20 * multiplier * factor))
            secheresse = min(100, int(15 * multiplier * factor))
            erosion = min(100, int(10 * multiplier * factor))

            self.risks_table.setItem(idx, 0, QTableWidgetItem(region))
            self.risks_table.setItem(idx, 1, QTableWidgetItem(f"{inondation}%"))
            self.risks_table.setItem(idx, 2, QTableWidgetItem(f"{secheresse}%"))
            self.risks_table.setItem(idx, 3, QTableWidgetItem(f"{erosion}%"))

    def update_recommendations(self):
        """Update agricultural recommendations"""
        recommendations = {
            "Optimiste": f"Année {self.current_year}: Conditions favorables. Maintenir les cultures traditionnelles avec irrigation améliorée.",
            "Moyen": f"Année {self.current_year}: Risques modérés. Intégrer cultures résilientes (mil, arachide améliorée). Renforcer stockage eau.",
            "Pessimiste": f"Année {self.current_year}: Risques élevés. Transition vers cultures tolérantes sécheresse (niébé, sorgho). Agroforesterie recommandée."
        }
        self.reco_text.setText(recommendations.get(self.scenario, "N/A"))

    def export_report(self):
        """Export simulation report"""
        report = f"""RAPPORT DE SIMULATION - CLIMATE ALERT SÉNÉGAL
        
Année: {self.current_year}
Scénario: {self.scenario}

Résumé:
Ce rapport simule l'évolution des risques climatiques au Sénégal de 2026 à 2046.
Les risques augmentent progressivement selon le scénario sélectionné.

Recommandations:
- Surveiller les zones côtières (érosion)
- Renforcer l'irrigation dans le Sahel
- Diversifier les cultures agricoles
        """
        self.iface.messageBar().pushMessage("Rapport", report, 1)
