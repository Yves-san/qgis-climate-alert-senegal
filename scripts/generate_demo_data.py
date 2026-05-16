"""
Generate synthetic climate data for demo / testing.
Usage:  python scripts/generate_demo_data.py [--scenario SSP2-4.5] [--communes 5]
"""
import argparse
from loguru import logger
from models.multi_resolution_manager import ClimateDataManager
from data.communes_generator import SENEGAL_COMMUNES

parser = argparse.ArgumentParser()
parser.add_argument("--scenario",  default="SSP2-4.5")
parser.add_argument("--communes",  type=int, default=3,
                    help="Number of communes to generate (for speed)")
args = parser.parse_args()

mgr = ClimateDataManager()
target = []
for region, communes in SENEGAL_COMMUNES.items():
    for c in communes:
        target.append({"id":c["id"],"name":c["name"],"lat":c["lat"],
                       "lon":c["lon"],"region":region})
    if len(target) >= args.communes:
        break

mgr.process_all(scenario=args.scenario, communes=target[:args.communes])
stats = mgr.stats(args.scenario)
logger.info(f"Stats: {stats}")
mgr.close()
