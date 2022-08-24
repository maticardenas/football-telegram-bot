from typing import List

from src.db.notif_sql_models import Fixture


def remove_duplicate_fixtures(fixtures: List[Fixture]) -> List[Fixture]:
    result_fixtures = []
    for fixture in fixtures:
        if fixture.id not in [rf.id for rf in result_fixtures]:
            result_fixtures.append(fixture)

    return result_fixtures
