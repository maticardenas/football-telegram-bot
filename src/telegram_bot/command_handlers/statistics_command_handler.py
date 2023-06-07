from datetime import datetime

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
        summary_text = f"{self._get_this_year_text()}<not_translate>\n\n</not_translate>{self._get_last_matches_record()}<not_translate>\n\n</not_translate>{self._get_last_match_text()}<not_translate>\n\n</not_translate>{self._get_next_match_text()}"

        return (summary_text, self._team.picture)

    def _get_top_scorers_text(self, top_scorers: dict) -> str:
        place_emojis = [
            Emojis.FIRST_PLACE_MEDAL,
            Emojis.SECOND_PLACE_MEDAL,
            Emojis.THIRD_PLACE_MEDAL,
        ]
        scorers_texts = []
        for i, (player, goals) in enumerate(top_scorers.items()):
            scorers_texts.append(
                f"{place_emojis[i].value} <em><not_translate>{player}</not_translate></em> ({goals})"
            )

        scorers_text = "\n".join(scorers_texts)

        return f"\n\nTop goal scorers:\n\n{scorers_text}" if scorers_texts else ""

    def _get_last_matches_record(self) -> str:
        last_matches_record = self._team_stats.team_record_in_last_n_matches(5)
        last_matches_record_text = ""

        if last_matches_record.games_played > 0:
            last_matches_record_text = f"""{Emojis.MAN_RUNNING.value} <strong>LAST MATCHES ({last_matches_record.games_played})</strong>\n\n{last_matches_record.overall_emoji} Record: {last_matches_record.all_record_matches_emojis}
{Emojis.SOCCER_BALL.value} Goals scored: <strong>{self._team_stats.number_of_goals(scored=True)}</strong>
{Emojis.GOAL_NET.value} Goals received: <strong>{self._team_stats.number_of_goals(scored=False)}</strong>{self._get_top_scorers_text(last_matches_record.top_scorers)}
            """

        return last_matches_record_text

    def _get_this_year_text(self) -> str:
        this_year_matches_record = self._team_stats.team_record_in_last_n_matches(
            number_of_matches=100, year=datetime.now().year
        )

        this_year_text = ""

        if this_year_matches_record.games_played > 0:
            this_year_text = f"""<strong>{Emojis.SPIRAL_CALENDAR.value} THIS YEAR {this_year_matches_record.overall_emoji}</strong>\n\n{Emojis.CHECK_MARK_BUTTON.value} Won Games: <strong>{this_year_matches_record.games_won}</strong>
{Emojis.EQUAL.value} Tied Games: <strong>{this_year_matches_record.games_drawn}</strong>
{Emojis.CROSS_MARK.value} Lost Games: <strong>{this_year_matches_record.games_lost}</strong>

{Emojis.SOCCER_BALL.value} Goals scored: <strong>{self._team_stats.number_of_goals(scored=True, number_of_matches=100, year=datetime.now().year)}</strong>
{Emojis.GOAL_NET.value} Goals received: <strong>{self._team_stats.number_of_goals(scored=False, number_of_matches=100, year=datetime.now().year)}</strong>{self._get_top_scorers_text(this_year_matches_record.top_scorers)}
            """

        return this_year_text

    def _get_last_match_text(self) -> str:
        last_match_db = self._fixtures_db_manager.get_last_fixture(
            team_id=int(self._team.id)
        )
        conv_last_match = (
            self._convert_fixture(last_match_db[0]) if len(last_match_db) else None
        )
        return (
            f"{Emojis.BACK_ARROW.value} <strong>LAST MATCH</strong>\n\n{conv_last_match.one_line_telegram_repr(played=True, with_date=True, with_league=True)}"
            if conv_last_match
            else ""
        )

    def _get_next_match_text(self) -> str:
        next_match_db = self._fixtures_db_manager.get_next_fixture(
            team_id=int(self._team.id)
        )
        conv_next_match = (
            self._convert_fixture(next_match_db[0]) if len(next_match_db) else None
        )
        return (
            f"{Emojis.SOON_ARROW.value} <strong>NEXT MATCH</strong>\n\n{conv_next_match.one_line_telegram_repr(with_date=True, with_league=True)}"
            if conv_next_match
            else ""
        )

    def _convert_fixture(self, fixture) -> Fixture:
        user_time_zones = self._fixtures_db_manager.get_user_time_zones(self._chat_id)
        converted_fixture = convert_db_fixture(fixture, user_time_zones=user_time_zones)
        converted_fixture.head_to_head = get_head_to_heads(
            converted_fixture.home_team.id, converted_fixture.away_team.id
        )

        return converted_fixture
