import inspect
import json
import os
import sys
from pathlib import Path

from src.entities import Championship

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
srcdir = os.path.join(parentdir, "..")
project_dir = os.path.join(srcdir, "..")
sys.path.insert(0, parentdir)
sys.path.insert(1, srcdir)
sys.path.insert(2, project_dir)

from src.db.fixtures_db_manager import FixturesDBManager
from src.db.notif_sql_models import League, Team

CURRENT_DIR = Path(__file__).parent.absolute()
LEAGUES_FILE = CURRENT_DIR / "leagues.json"

fixtures_db_manager = FixturesDBManager()

with open(LEAGUES_FILE, "r") as file:
    # Load the JSON data from the file
    data = json.load(file)

    for league in data.get("response", []):
        try:
            print(f"Inserting league {league['league']['name']}")

            db_league = Championship(
                id=league["league"]["id"],
                name=league["league"]["name"],
                logo=league["league"]["logo"],
                country=league["country"]["name"],
            )

            fixtures_db_manager.insert_league(db_league)
        except:
            print(f"Failed to insert league {league.get('league',{}).get('name','')}")
