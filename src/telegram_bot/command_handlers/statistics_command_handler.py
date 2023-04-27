from src.db.notif_sql_models import Team
from src.emojis import Emojis
from src.entities import Fixture
from src.statistics.team_stats import TeamStats
from src.telegram_bot.command_handlers.bot_commands_handler import (
    NotifierBotCommandsHandler,
)
from src.utils.fixtures_utils import convert_db_fixture, get_head_to_heads


class TeamStatisticsBotCommandsHandler(NotifierBotCommandsHandler):
    def __init__(self, team_id: int, chat_id: str = "") -> None:
        super().__init__(chat_id)
        self._team = self._get_team(team_id)
        self._team_stats = TeamStats(int(team_id))
        self._chat_id = str(chat_id)

    def _get_team(self, team_id: int) -> Team:
        return self._fixtures_db_manager.get_team(team_id)[0]

    def teams_summary(self) -> tuple[str, str]:
        last_match_db = self._fixtures_db_manager.get_last_fixture(
            team_id=int(self._team.id)
        )
        next_match_db = self._fixtures_db_manager.get_next_fixture(
            team_id=int(self._team.id)
        )

        conv_last_match = (
            self._convert_fixture(last_match_db[0]) if len(last_match_db) else None
        )
        conv_next_match = (
            self._convert_fixture(next_match_db[0]) if len(next_match_db) else None
        )

        last_match_text = (
            f"<strong>Last Match:</strong>\n\n{conv_last_match.one_line_telegram_repr(played=True, with_date=True, with_league=True)}<not_translate>\n\n</not_translate>"
            if conv_last_match
            else ""
        )
        next_match_text = (
            f"<strong>Next Match:</strong>\n\n{conv_next_match.one_line_telegram_repr(with_date=True, with_league=True)}"
            if conv_next_match
            else ""
        )
        last_matches_record = f"<strong> Last 5 Matches:</strong>\n\n{self._team_stats.team_record_in_last_n_matches(5).emoji} Record: {self._team_stats.team_record_emoji_text(5)}\n"
        goals_scored = f"{Emojis.SOCCER_BALL.value} Goals scored: <strong>{self._team_stats.number_of_goals(scored=True)}</strong>"
        goals_received = f"{Emojis.GOAL_NET.value} Goals received: <strong>{self._team_stats.number_of_goals(scored=False)}</strong>"

        return (
            f"{last_matches_record}{goals_scored}\n{goals_received}\n\n{last_match_text}{next_match_text}",
            self._team.picture,
        )

    def _convert_fixture(self, fixture) -> Fixture:
        user_time_zones = self._fixtures_db_manager.get_user_time_zones(self._chat_id)
        converted_fixture = convert_db_fixture(fixture, user_time_zones=user_time_zones)
        converted_fixture.head_to_head = get_head_to_heads(
            converted_fixture.home_team.id, converted_fixture.away_team.id
        )

        return converted_fixture
