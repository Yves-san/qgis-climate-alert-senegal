"""
Senegal Climate Alert System — Main Entry Point
Usage:
  python main.py --init                # Init DB + communes
  python main.py --generate [N]        # Generate data for N communes
  python main.py --api                 # Start API
  python main.py --stats               # Show DB stats
"""
import argparse, sys
from loguru import logger

def main():
    parser = argparse.ArgumentParser(description="Senegal Climate Alert System")
    parser.add_argument("--init",     action="store_true", help="Initialise DB")
    parser.add_argument("--generate", type=int, nargs="?", const=5,
                        metavar="N", help="Generate data for N communes")
    parser.add_argument("--api",      action="store_true", help="Start FastAPI")
    parser.add_argument("--stats",    action="store_true", help="Show DB stats")
    parser.add_argument("--scenario", default="SSP2-4.5")
    args = parser.parse_args()

    if args.init:
        from scripts.initialize_db import *
    elif args.generate is not None:
        from models.multi_resolution_manager import ClimateDataManager
        from data.communes_generator import SENEGAL_COMMUNES
        mgr = ClimateDataManager()
        target = []
        for region, communes in SENEGAL_COMMUNES.items():
            for c in communes:
                target.append({"id":c["id"],"name":c["name"],
                               "lat":c["lat"],"lon":c["lon"],"region":region})
        mgr.process_all(scenario=args.scenario, communes=target[:args.generate])
        logger.info(mgr.stats(args.scenario))
        mgr.close()
    elif args.api:
        import uvicorn
        uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
    elif args.stats:
        from models.multi_resolution_manager import ClimateDataManager
        mgr = ClimateDataManager()
        for sc in ["SSP1-1.9","SSP2-4.5","SSP5-8.5"]:
            logger.info(f"{sc}: {mgr.stats(sc)}")
        mgr.close()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
