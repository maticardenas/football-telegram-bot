from src.db.fixtures_db_manager import FixturesDBManager
from src.db.notif_sql_models import LineUp as DBLineUp
from src.entities import LineUp, Player


class LineUpConverter:
    def __init__(self):
        self._fixtures_db_manager = FixturesDBManager()

    def response_to_db_model(
        self,
        fixture_id: int,
        team_id: int,
        formation: str,
        player_line_up_response: dict,
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

    def db_model_to_entity(self, formation: str, line_up: list[DBLineUp]) -> LineUp:
        return LineUp(
            formation=formation,
            goalkeeper=self.get_players_in_pos("G", line_up),
            defenders=self.get_players_in_pos("D", line_up),
            midfielders=self.get_players_in_pos("M", line_up),
            forward_strikers=self.get_players_in_pos("F", line_up),
        )

    def get_players_in_pos(self, pos: str, line_up: list[DBLineUp]) -> list[Player]:
        return [
            player
            for player in [
                self._fixtures_db_manager.get_player(play.player)[0]
                for play in list(filter(lambda lup: lup.pos == pos, line_up))
            ]
        ]
