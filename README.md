

# Football Telegram Bot



## Description

This application consumes, stores and processes football information and informs it on demand through a Telegram bot.

This bot is currently deployed and can be found in Telegram as `@card_football_bot`


## Main Functionalities

This telegram bot informs of past and future fixtures for many different teams and leagues around the world.
For more details on what can be configured and queried you can refer to the **commands** section below.


## Bot Commands

- `/start` - Bot's introductory message.

- `/help` - Information about bot's commands and what they provide.

- `/search_team <team_name>` - Search for teams by name.

- `/search_league <league_name>` - Search for leagues by name.

- `/favourite_teams` - List of user's favourite teams.

- `/favourite_leagues` - List of user's favourite leagues.
 
- `/add_favourite_team <team_id>` - Adds a team to user's favourites.

- `/add_favourite_league <league_id>` - Adds a league to your favourites.

- `/delete_favourite_team <team_id>` - Removes a team from your favourites.

- `/delete_favourite_league <league_id>` - Removes a league from your favourites.

- `/available_leagues` - Available team's that can be queried with the other commands.

- `/next_match <team_id>` - Retrieves information about next scheduled match for an specific team, including rival, date (in different timezones), league and round which is being played.

- `/last_match <team_id>` - Retrieves information about last match played by the specific team, including  scores, rival, date (in different timezones), league, roung and highlights

- *`/upcoming_matches [optional [team_id] [ft-fteams-favourite_teams] [fl-fleagues-favourite_leagues]]` - List of upcoming matches.

- `/next_match_league <league_id>` - Retrieves information about next scheduled match for an specific tournament, including rival, date (in different timezones), league and round which is being played.

- `/next_matches_league <league_id>` - Retrieves information about matches to be played on the day that the next match of a tournament is happening.

- `/last_match_league <league_id>` - Retrieves information about last match played by the specific tournament, including  scores, rival, date (in different timezones), league, roung and highlights

- *`/today_matches [optional [league_ids] [ft-fteams-favourite_teams] [fl-fleagues-favourite_leagues]]` - Retrieves information about matches to be played on the current day.

- *`/tomorrow_matches [optional [league_ids] [ft-fteams-favourite_teams] [fl-fleagues-favourite_leagues]]` - Retrieves information about matches to be played on the following day.

- *`/last_played_matches [optional [league_ids] [ft-fteams-favourite_teams] [fl-fleagues-favourite_leagues]]` - Retrieves information about matches played on the previous day.

*<em>For these commands is possible to optionally specify `leagues_id` or user's favourite teams or leagues.</em>

## Implementation Overview

Application is written in Python, as database engine uses PostgreSQL, jobs are scheduled using cronjob and it is finally deployed with Docker.

It consumes [RAPID API - API FOOTBALL](https://rapidapi.com/api-sports/api/api-football) endpoints, processes its data and stores it to the database. This runs in cronjobs scheduled, and then on demand user can request the processed team's information through Telegram's commands.


## Requirements

- Python 3.8+
- [Docker](https://www.docker.com)
- [Telegram Bot Token](https://core.telegram.org/bots)
