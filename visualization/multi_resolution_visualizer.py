"""
Generate matplotlib figures at daily / monthly / annual resolutions.
"""
from __future__ import annotations
import os
from typing import Optional
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import folium

RISK_COLORS = {"LOW":"#4CAF50","MEDIUM":"#FFC107","HIGH":"#FF9800","CRITICAL":"#F44336"}
UNITS = {"temperature":"°C","precipitation":"mm","humidity":"%","wind_speed":"m/s","drought_index":"idx"}


class MultiResolutionVisualizer:

    def __init__(self, output_dir: str = "output/visualizations"):
        self.out = output_dir
        os.makedirs(output_dir, exist_ok=True)

    # ── Plot helpers ─────────────────────────────────────────────────────────
    def plot_daily(self, df: pd.DataFrame, commune: str, var: str = "temperature",
                   save: Optional[str] = None) -> plt.Figure:
        fig, ax = plt.subplots(figsize=(16, 5))
        dates  = pd.to_datetime(df["date"])
        values = df[var]
        conf   = df.get("confidence", pd.Series(np.ones(len(df)) * 0.85))
        ax.plot(dates, values, linewidth=0.7, alpha=0.85, color="#1976D2")
        ax.fill_between(dates, values - conf * 3, values + conf * 3,
                         alpha=0.1, color="#1976D2")
        ax.set_title(f"📅 {var.upper()} JOURNALIER — {commune}", fontweight="bold")
        ax.set_ylabel(f"{var} ({UNITS.get(var,'')})")
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
        fig.autofmt_xdate()
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        if save:
            fig.savefig(save, dpi=150, bbox_inches="tight")
        return fig

    def plot_monthly(self, df: pd.DataFrame, commune: str, var: str = "temperature",
                     save: Optional[str] = None) -> plt.Figure:
        fig, ax = plt.subplots(figsize=(14, 5))
        x = range(len(df))
        ax.plot(x, df[var], marker="o", linewidth=2, markersize=7, color="#FF9800")
        ax.fill_between(x,
                         df.get("temperature_min", df[var]),
                         df.get("temperature_max", df[var]),
                         alpha=0.15, color="#FF9800")
        ax.set_title(f"📆 {var.upper()} MENSUEL — {commune}", fontweight="bold")
        ax.set_ylabel(f"{var} ({UNITS.get(var,'')})")
        ax.set_xticks(x)
        ax.set_xticklabels(df["date"].tolist(), rotation=45, ha="right")
        ax.grid(True, alpha=0.3, axis="y")
        plt.tight_layout()
        if save:
            fig.savefig(save, dpi=150, bbox_inches="tight")
        return fig

    def plot_annual(self, df: pd.DataFrame, commune: str, var: str = "temperature",
                    save: Optional[str] = None) -> plt.Figure:
        fig, ax = plt.subplots(figsize=(14, 5))
        x = range(len(df))
        ax.bar(x, df[var], color="#4CAF50", alpha=0.7, edgecolor="black", linewidth=0.8)
        z = np.polyfit(x, df[var], 1)
        p = np.poly1d(z)
        ax.plot(np.linspace(0, len(df)-1, 200), p(np.linspace(0, len(df)-1, 200)),
                "r--", linewidth=2, label="Tendance")
        ax.set_title(f"📊 {var.upper()} ANNUEL — {commune}", fontweight="bold")
        ax.set_ylabel(f"{var} ({UNITS.get(var,'')})")
        ax.set_xticks(x)
        ax.set_xticklabels(df["date"].tolist(), rotation=45, ha="right")
        ax.legend()
        ax.grid(True, alpha=0.3, axis="y")
        plt.tight_layout()
        if save:
            fig.savefig(save, dpi=150, bbox_inches="tight")
        return fig

    def dashboard(self, daily: pd.DataFrame, monthly: pd.DataFrame,
                  annual: pd.DataFrame, commune: str, year: int,
                  save: Optional[str] = None) -> plt.Figure:
        fig = plt.figure(figsize=(18, 11))
        gs  = fig.add_gridspec(3, 2, hspace=0.4, wspace=0.3)
        # Row 0: daily temperature
        ax0 = fig.add_subplot(gs[0, :])
        if not daily.empty:
            d = pd.to_datetime(daily["date"])
            ax0.plot(d, daily["temperature"], linewidth=0.6, color="#1976D2")
            ax0.set_title(f"🌡️  Température journalière — {commune} {year}", fontweight="bold")
            ax0.set_ylabel("°C"); ax0.grid(True, alpha=0.25)
            fig.autofmt_xdate()
        # Row 1-left: daily precip
        ax1 = fig.add_subplot(gs[1, 0])
        if not daily.empty:
            d = pd.to_datetime(daily["date"])
            ax1.bar(d, daily["precipitation"], width=1.5, color="#2196F3", alpha=0.7)
            ax1.set_title("💧 Précipitations journalières", fontweight="bold")
            ax1.set_ylabel("mm"); ax1.grid(True, alpha=0.25, axis="y")
        # Row 1-right: monthly temperature
        ax2 = fig.add_subplot(gs[1, 1])
        if not monthly.empty:
            x = range(len(monthly))
            ax2.plot(x, monthly["temperature"], marker="o", linewidth=2, color="#FF9800")
            ax2.set_title("📆 Température mensuelle", fontweight="bold")
            ax2.set_ylabel("°C"); ax2.grid(True, alpha=0.25, axis="y")
        # Row 2: annual summary text
        ax3 = fig.add_subplot(gs[2, :])
        ax3.axis("off")
        if not daily.empty:
            txt = (f"RÉSUMÉ {year} — {commune}
"
                   f"Temp moy: {daily['temperature'].mean():.1f}°C  "
                   f"Min: {daily['temperature'].min():.1f}°C  "
                   f"Max: {daily['temperature'].max():.1f}°C
"
                   f"Précipitations totales: {daily['precipitation'].sum():.0f} mm  "
                   f"Jours de pluie: {(daily['precipitation'] > 0).sum()}")
            ax3.text(0.5, 0.5, txt, ha="center", va="center",
                     fontsize=13, transform=ax3.transAxes,
                     bbox=dict(boxstyle="round,pad=0.8", facecolor="#f5f5f5"))
        fig.suptitle(f"Tableau de bord climatique — {commune} {year}",
                     fontsize=15, fontweight="bold")
        if save:
            fig.savefig(save, dpi=150, bbox_inches="tight")
        return fig

    def risk_map(self, communes_data: dict, save: Optional[str] = None) -> folium.Map:
        m = folium.Map(location=[14.5, -14.5], zoom_start=6, tiles="OpenStreetMap")
        for name, info in communes_data.items():
            risk  = info.get("risk_level", "MEDIUM")
            color = RISK_COLORS.get(risk, "#999")
            popup = f"<b>{name}</b><br>Risque: {risk}<br>Temp: {info.get('temp','-')}°C"
            folium.CircleMarker(
                location=[info["lat"], info["lon"]], radius=8,
                popup=popup, color=color, fill=True, fillColor=color, fillOpacity=0.7
            ).add_to(m)
        if save:
            m.save(save)
        return m
