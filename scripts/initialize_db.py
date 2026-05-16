"""Initialize database and load all communes."""
from data.database_schema import DatabaseManager
from data.communes_generator import CommunesGenerator
from loguru import logger

if __name__ == "__main__":
    db  = DatabaseManager()
    gen = CommunesGenerator(db)
    gen.generate_all()
    gen.export_geojson()
    logger.success("Database initialised and communes loaded.")
    db.close()
