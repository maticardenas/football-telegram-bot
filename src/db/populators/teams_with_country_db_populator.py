import inspect
import json
import os
import sys
from pathlib import Path

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
srcdir = os.path.join(parentdir, "..")
project_dir = os.path.join(srcdir, "..")
sys.path.insert(0, parentdir)
sys.path.insert(1, srcdir)
sys.path.insert(2, project_dir)

from src.db.fixtures_db_manager import FixturesDBManager
from src.db.notif_sql_models import Team

CURRENT_DIR = Path(__file__).parent.absolute()
TEAMS_DIR = CURRENT_DIR / "teams"

fixtures_db_manager = FixturesDBManager()


for country_teams_file in TEAMS_DIR.glob("*.json"):
    print(f"Checking file {country_teams_file}")

    with open(country_teams_file, "r") as file:
        # Load the JSON data from the file
        data = json.load(file)

        for team in data.get("response", []):
            try:
                print(f"Inserting team {team['team']['name']}")

                country = team["team"]["country"]

                db_countries = fixtures_db_manager.get_countries_by_name(country)

                country_id = db_countries[0].id

                db_team = Team(
                    id=team["team"]["id"],
                    name=team["team"]["name"],
                    picture=team["team"]["logo"],
                    country=country_id,
                )

                fixtures_db_manager.insert_team(db_team)
            except:
                print(
                    f"Failed to insert team {team.get('team',{}).get('name','')} for file {country_teams_file}"
                )
