"""Global constants for Senegal Climate Alert System."""

# Climate periods
START_YEAR = 2025
END_YEAR = 2055
BASELINE_START = 1990
BASELINE_END = 2020

# Senegal geographic bounds
SENEGAL_BBOX = {
    "min_lon": -17.55, "max_lon": -11.35,
    "min_lat": 12.30,  "max_lat": 16.70,
}
SENEGAL_CENTER = {"lat": 14.5, "lon": -14.5}

# Risk classification
RISK_LEVELS = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
RISK_COLORS = {
    "LOW":      "#4CAF50",
    "MEDIUM":   "#FFC107",
    "HIGH":     "#FF9800",
    "CRITICAL": "#F44336",
}

# SSP Scenario temperature projections for Senegal by 2055
SCENARIO_TEMP_INCREASE = {
    "SSP1-1.9": 1.2,
    "SSP2-4.5": 1.8,
    "SSP5-8.5": 2.8,
}

# Crops and water needs (mm/season)
SENEGAL_CROPS = {
    "Arachide":   {"water": 450, "optimal_temp": (22, 32), "season_months": [6, 10]},
    "Mil":        {"water": 350, "optimal_temp": (25, 35), "season_months": [7, 9]},
    "Riz":        {"water": 1200, "optimal_temp": (20, 30), "season_months": [7, 10]},
    "Maïs":       {"water": 550, "optimal_temp": (20, 30), "season_months": [6, 9]},
    "Sorgho":     {"water": 400, "optimal_temp": (24, 34), "season_months": [7, 9]},
    "Anacarde":   {"water": 800, "optimal_temp": (22, 35), "season_months": [3, 6]},
    "Coton":      {"water": 700, "optimal_temp": (21, 32), "season_months": [7, 11]},
}

# CMIP6 model weights for ensemble
MODEL_WEIGHTS = {
    "MPI-ESM1-2-LR":    0.22,
    "IPSL-CM6A-LR":     0.20,
    "HadGEM3-GC31-LL":  0.20,
    "MIROC6":           0.20,
    "NorESM2-MM":       0.18,
}
