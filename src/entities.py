import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from src.emojis import Emojis


@dataclass
class MatchScore:
    home_score: int
    away_score: int


@dataclass
class Team:
    id: str
    name: str
    picture: str
    aliases: list


@dataclass
class Championship:
    league_id: int
    name: str
    country: str
    logo: str


@dataclass
class MatchHighlights:
    url: str
    embed_url: str


@dataclass
class Player:
    id: int
    name: str
    pos: str


@dataclass
class LineUp:
    formation: str
    goalkeeper: Player
    defenders: List[Player]
    midfielders: List[Player]
    forward_strikers: List[Player]

    def __str__(self):
        return (
            f"{Emojis.JOYSTICK.value} <strong>{self.formation}</strong>\n\n"
            f"{Emojis.GLOVES.value} <strong>{self.goalkeeper.name}</strong>\n"
            f"{Emojis.SHIELD.value} <strong>{', '.join([defender.name for defender in self.defenders])} </strong>\n"
            f"{Emojis.MAGIC_WAND.value} <strong>{', '.join([midfielder.name for midfielder in self.midfielders])}</strong>\n"
            f"{Emojis.SCORING.value} <strong>{', '.join([strike.name for strike in self.forward_strikers])}</strong>\n"
        )

    def email_like_repr(self):
        return (
            f"{Emojis.JOYSTICK.value} <strong>{self.formation}</strong><br /><br />"
            f"{Emojis.GLOVES.value} <strong>{self.goalkeeper.name}</strong><br />"
            f"{Emojis.SHIELD.value} <strong> {', '.join([defender.name for defender in self.defenders])} </strong><br />"
            f"{Emojis.MAGIC_WAND.value} <strong> {', '.join([midfielder.name for midfielder in self.midfielders])}</strong><br />"
            f"{Emojis.SCORING.value} <strong> {', '.join([strike.name for strike in self.forward_strikers])}</strong><br />"
        )


@dataclass
class RemainingTime:
    days: int
    hours: int
    minutes: int

    def _get_days_union(self) -> str:
        if self.hours and self.minutes:
            days_union = ", "
        elif (self.hours and not self.minutes) or (not self.hours and self.minutes):
            days_union = " and "
        else:
            days_union = ""

        return days_union

    def __str__(self):
        suf_days = "s" if self.days != 1 else ""
        suf_hours = "s" if self.hours != 1 else ""
        suf_minutes = "s" if self.minutes != 1 else ""

        days_phrase = (
            f"{self.days} day{suf_days}{self._get_days_union()}"
            if self.days > 0
            else ""
        )
        hours_union = " and " if self.minutes else ""
        hours_phrase = (
            f"{self.hours} hour{suf_hours}{hours_union}" if self.hours > 0 else ""
        )
        minutes_phrase = (
            f"{self.minutes} minute{suf_minutes}" if self.minutes > 0 else ""
        )

        return f"{days_phrase}{hours_phrase}{minutes_phrase}"


@dataclass
class FixtureForDB:
    id: int
    utc_date: str
    bsas_date: str
    date_diff: int
    referee: str
    match_status: str
    championship: Championship
    round: str
    home_team: Team
    away_team: Team
    match_score: MatchScore
    venue: str


@dataclass
class Fixture:
    id: int
    utc_date: datetime
    ams_date: datetime
    bsas_date: datetime
    date_diff: int
    referee: str
    match_status: str
    championship: Championship
    round: str
    home_team: Team
    away_team: Team
    match_score: MatchScore
    venue: str
    line_up: Optional[LineUp] = field(init=False)
    is_next_day: str = field(init=False)
    highlights: List[str] = field(init=False)
    head_to_head: List["Fixture"] = field(init=False)

    def __post_init__(self) -> None:
        self.is_next_day = "(+1)" if self._is_next_day_in_europe() else ""
        self.futbol_libre_url = "https://futbollibre.net"
        self.futbol_para_todos_url = "https://futbolparatodos.online/es/"
        self.line_up = None
        self.highlights = [
            f"https://www.youtube.com/results?search_query={self.home_team.name}+vs+{self.away_team.name}+jugadas+resumen"
        ]
        self.head_to_head = []

    def remaining_time(self) -> RemainingTime:
        days = self.date_diff // 86400
        hours = (self.date_diff - (days * 86400)) // 3600
        minutes = (self.date_diff - (days * 86400) - (hours * 3600)) // 60

        return RemainingTime(days, hours, minutes)

    def __str__(self):
        return (
            f"{Emojis.EUROPEAN_UNION.value} *{str(self.ams_date)[11:16]} HS {self.is_next_day}*\n"
            f"{Emojis.ARGENTINA.value} *{str(self.bsas_date)[11:16]} HS*\n\n"
            f"{Emojis.ALARM_CLOCK.value} _{str(self.remaining_time())} left for the game._\n\n"
            f"{Emojis.SOCCER_BALL.value} *{self.home_team.name} vs. {self.away_team.name}*\n"
            f"{Emojis.TROPHY.value} *{self.championship.name}*\n"
            f"{Emojis.PUSHPIN.value} *{self.round}*"
        )

    def matched_played_str(self) -> str:
        return (
            f"{Emojis.SOCCER_BALL.value} *{self.home_team.name} - {self.match_score.home_score} "
            f"vs. {self.match_score.away_score} - {self.away_team.name}*\n"
            f"{Emojis.TROPHY.value} *{self.championship.name}*\n"
            f"{Emojis.PUSHPIN.value} *{self.round}*"
        )

    def time_telegram_text(self) -> str:
        return (
            f"{Emojis.EUROPEAN_UNION.value} {str(self.ams_date)[11:16]} HS {self.is_next_day} / "
            f"{Emojis.ARGENTINA.value} {str(self.bsas_date)[11:16]} HS"
        )

    def head_to_head_text(self) -> str:
        h2h_text = ""

        if self.head_to_head:
            head_to_head_list = ""
            for h2h_fixture in reversed(self.head_to_head[-5:]):
                date_to_show = h2h_fixture.bsas_date.strftime("%Y-%m-%d")
                head_to_head_list += (
                    f"{Emojis.SPIRAL_CALENDAR.value} {date_to_show}\n"
                    f"{Emojis.SOCCER_BALL.value} {h2h_fixture.home_team.name} [{h2h_fixture.match_score.home_score}] vs [{h2h_fixture.match_score.away_score}] {h2h_fixture.away_team.name}\n\n"
                )

            h2h_text = (
                f"{Emojis.RIGHT_FACING_FIST.value}{Emojis.LEFT_FACING_FIST.value} last clashes between the two:\n\n"
                f"{head_to_head_list}"
            )

        return h2h_text

    def one_line_telegram_repr(
        self, played: bool = False, with_date: bool = False
    ) -> str:
        if (
            self.match_score.away_score is not None
            or self.match_score.home_score is not None
        ):
            played = True

        date_text = (
            f"{Emojis.SPIRAL_CALENDAR.value} {self.bsas_date.strftime('%d-%m-%Y')}\n"
            if with_date
            else ""
        )

        if played:
            if (
                "finished" in self.match_status.lower()
                or "half" in self.match_status.lower()
            ):
                match_in_progress_text = (
                    f"\n{Emojis.MAN_RUNNING.value} {self.match_status}"
                    if "half" in self.match_status.lower()
                    else ""
                )
                repr = (
                    f"{date_text}"
                    f"{Emojis.SOCCER_BALL.value} "
                    f"{self.home_team.name} [{self.match_score.home_score}] vs. [{self.match_score.away_score}] {self.away_team.name} \n"
                    f"{Emojis.TROPHY.value} {self.championship.name} ({self.championship.country[:3].upper()})"
                    f"{match_in_progress_text}"
                    # f"{Emojis.FILM_PROJECTOR.value} <a href='{self.highlights[0]}'>HIGHLIGHTS</a>"
                )
            else:
                repr = (
                    f"{date_text}"
                    f"{Emojis.SOCCER_BALL.value} {self.home_team.name} vs. {self.away_team.name} \n"
                    f"{Emojis.TROPHY.value} {self.championship.name} ({self.championship.country[:3].upper()})\n"
                    f"{Emojis.SAD_FACE.value} {self.match_status}"
                )
        else:
            repr = (
                f"{date_text}"
                f"{Emojis.SOCCER_BALL.value} "
                f"{self.home_team.name} vs. {self.away_team.name} \n"
                f"{Emojis.TROPHY.value} {self.championship.name} ({self.championship.country[:3].upper()})\n"
                f"{Emojis.ALARM_CLOCK.value} {self.time_telegram_text()}"
            )

        return repr

    def email_like_repr(self) -> str:
        return (
            f"<p>{Emojis.EUROPEAN_UNION.value} <strong>{str(self.ams_date)[11:16]} HS {self.is_next_day}<br />"
            f"{Emojis.ARGENTINA.value} <strong>{str(self.bsas_date)[11:16]} HS</strong><p>"
            f"{Emojis.ALARM_CLOCK.value} <em>{str(self.remaining_time())} left for the game.</em><p>"
            f"{Emojis.SOCCER_BALL.value} "
            f"<img src='{self.home_team.picture}' width='22' height='22'><strong> vs. "
            f"<img src='{self.away_team.picture}' width='22' height='22'></strong><br />"
            f"<img src='{self.championship.logo}' width='22' height='22'> <strong>{self.championship.name}</strong><br />"
            f"{Emojis.PUSHPIN.value} <strong>{self.round}</strong><p>"
            f"{self.head_to_head_text()}"
        )

    def telegram_like_repr(self) -> str:
        referee_line = (
            f"{Emojis.POLICE_WOMAN.value} <strong>{self.referee}</strong>\n"
            if self.referee
            else ""
        )
        stadium_line = (
            f"{Emojis.STADIUM.value} <strong>{self.venue}</strong>\n"
            if self.venue
            else ""
        )

        telegram_like_text = (
            f"{Emojis.EUROPEAN_UNION.value} <strong>{str(self.ams_date)[11:16]} HS {self.is_next_day}</strong>\n"
            f"{Emojis.ARGENTINA.value} <strong>{str(self.bsas_date)[11:16]} HS</strong>\n\n"
            f"{Emojis.ALARM_CLOCK.value} {str(self.remaining_time())} left for the game.\n\n"
            f"{Emojis.SOCCER_BALL.value} "
            f"<strong>{self.home_team.name} vs. {self.away_team.name}</strong>\n"
            f"{Emojis.TROPHY.value} <strong>{self.championship.name} ({self.championship.country[:3].upper()})</strong>\n"
            f"{stadium_line}"
            f"{referee_line}"
            f"\n{self.head_to_head_text()}"
        )

        return telegram_like_text

    def line_up_message(self) -> str:
        return (
            str(self.line_up)
            if self.line_up
            else f"<strong>Not yet available :(</strong>"
        )

    def line_up_email_message(self) -> str:
        return (
            self.line_up.email_like_repr() if self.line_up else f"Not yet available :("
        )

    def matched_played_email_like_repr(self) -> str:
        return (
            f"<p><img src='{self.home_team.picture}' width='22' height='22'><strong> - {self.match_score.home_score} vs. "
            f" {self.match_score.away_score} - <img src='{self.away_team.picture}' width='22' height='22'></strong><br />"
            f"<img src='{self.championship.logo}' width='25' height='25'> <strong>{self.championship.name}</strong><br />"
            f"{Emojis.PUSHPIN.value} <strong>{self.round}</strong><br /><br />"
        )

    def matched_played_telegram_like_repr(self) -> str:
        referee_line = (
            f"{Emojis.POLICE_WOMAN.value} <strong>{self.referee}</strong>\n\n"
            if self.referee
            else "\n"
        )
        stadium_line = (
            f"{Emojis.STADIUM.value} <strong>{self.venue}</strong>\n"
            if self.venue
            else ""
        )
        if (
            "finished" in self.match_status.lower()
            or "half" in self.match_status.lower()
        ):
            match_in_progress_text = (
                f"{Emojis.MAN_RUNNING.value} <strong>{self.match_status}</strong>\n\n"
                if "half" in self.match_status.lower()
                else ""
            )
            match_notification = (
                f"{match_in_progress_text}"
                f"<strong>{Emojis.SOCCER_BALL.value} {self.home_team.name} [{self.match_score.home_score}] vs. "
                f" [{self.match_score.away_score}] {self.away_team.name}</strong>\n"
                f"{Emojis.TROPHY.value} <strong>{self.championship.name} ({self.championship.country[:3].upper()})</strong>\n"
                f"{Emojis.PUSHPIN.value} <strong>{self.round}</strong>\n"
                f"{stadium_line}"
                f"{referee_line}"
            )
        else:
            match_notification = (
                f"{Emojis.SAD_FACE.value} <strong>{self.match_status}</strong>\n\n"
                f"<strong>{Emojis.SOCCER_BALL.value} {self.home_team.name} vs. {self.away_team.name}</strong>\n"
                f"{Emojis.TROPHY.value} <strong>{self.championship.name} ({self.championship.country[:3].upper()})</strong>\n"
                f"{Emojis.PUSHPIN.value} <strong>{self.round}</strong>\n"
                f"{stadium_line}"
                f"{referee_line}"
            )

        return match_notification

    def _is_next_day_in_europe(self) -> bool:
        return self.bsas_date.weekday() != self.ams_date.weekday()


@dataclass
class TeamStanding:
    championship: Championship
    position: int
    points: int
    goal_difference: int
    current_condition: str

    def __str__(self):
        return (
            f"{Emojis.CHART_INCREASING.value} Position: *{self.position}*\n"
            f"{Emojis.CHECK_MARK.value} Points: *{self.points}*\n"
            f"{Emojis.GOAL_NET.value} Goal difference: *{self.goal_difference}*\n"
            f"{Emojis.GLOBE_WITH_MERIDIANS.value} Qualification: *{self.current_condition}*"
        )

    def email_like_repr(self) -> str:
        return (
            f"<br /><br />{Emojis.CHART_INCREASING.value} Position: <strong>{self.position}</strong><br />"
            f"{Emojis.CHECK_MARK.value} Points: <strong>{self.points}</strong><br />"
            f"{Emojis.GOAL_NET.value} Goal difference: <strong>{self.goal_difference}</strong><br />"
            f"{Emojis.GLOBE_WITH_MERIDIANS.value} Qualification: <strong>{self.current_condition}</strong>"
        )

    def telegram_like_repr(self) -> str:
        return (
            f"{Emojis.CHART_INCREASING.value} Position: <strong>{self.position}</strong>\n"
            f"{Emojis.CHECK_MARK.value} Points: <strong>{self.points}</strong>\n"
            f"{Emojis.GOAL_NET.value} Goal difference: <strong>{self.goal_difference}</strong>"
        )


@dataclass
class PlayerStats:
    appearences: int
    minutes: int
    total_shots: int
    shots_on_target: int
    goals: int
    total_passes: int
    key_passes: int
    accuracy: int
    dribbles_attempts: int
    dribbles_success: int

    def __str__(self):
        return (
            f"_Appearances:_ *{self.appearences}*\n"
            f"_Goals:_ *{self.goals}*\n"
            f"_Minutes:_ *{self.minutes}*\n"
            f"_Total Shots:_ *{self.total_shots}*\n"
            f"_Shots on target:_ *{self.shots_on_target}*\n\n"
            f"_Total Passes:_ *{self.total_passes}*\n"
            f"_Key Passes:_ *{self.key_passes}*\n"
            f"_Accuracy:_ *{self.accuracy}*\n\n"
            f"_Dribbles Attempts:_ *{self.dribbles_attempts}*\n"
            f"_Dribbles Success:_ *{self.dribbles_success}*"
        )
