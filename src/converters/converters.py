from src.db.notif_sql_models import LineUp as DBLineUp
from src.entities import LineUp


class LineUpConverter:
    @staticmethod
    def response_to_db_model(
        fixture_id: int, team_id: int, formation: str, player_line_up_response: dict,
    ) -> DBLineUp:
        return DBLineUp(
            fixture=fixture_id,
            team=team_id,
            formation=formation,
            player=player_line_up_response["id"],
            pos=player_line_up_response["pos"],
            number=player_line_up_response["number"],
            grid=player_line_up_response["grid"],
        )

    @staticmethod
    def db_model_to_entity(formation: str, line_up: list[DBLineUp]) -> LineUp:
        return LineUp(
            formation=formation,
            goalkeeper=filter(lambda lup: lup.pos == "G", line_up),
            defenders=filter(lambda lup: lup.pos == "D", line_up),
            midfielders=filter(lambda lup: lup.pos == "M", line_up),
            forward_strikers=filter(lambda lup: lup.pos == "F", line_up),
        )
