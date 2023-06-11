from src.db.notif_sql_models import LineUp as DBLineUp
from src.entities import LineUp


class LineUpConverter:
    @staticmethod
    def response_to_db_model(
        fixture_id: int, team_id: int, player_line_up_response: dict
    ) -> DBLineUp:
        return DBLineUp(
            fixture=fixture_id,
            team=team_id,
            player=player_line_up_response["id"],
            pos=player_line_up_response["pos"],
            number=player_line_up_response["number"],
            grid=player_line_up_response["grid"],
        )
