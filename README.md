

# Football Telegram Bot


## Description

This application consumes, stores and processes football information and informs it on demand through a Telegram bot.

This bot is currently deployed and can be found in Telegram as `@card_football_bot`


## Main Functionalities

This telegram bot informs of past and future fixtures for many teams and leagues around the world.
For more details on what can be configured and queried you can refer to the **commands** section below.


![readme_video.gif](media/readme_video.gif)


## Bot Commands

- `/start` - Bot's introduction and start tips :).

- `/set_main_time_zone` - Sets your main time zone by id. Remember you can have only ONE main time zone.

- `/set_add_time_zone` - Sets an additional time zone by id.

- `/my_time_zones` - List of your configured time zones.

- `/subscribe_to_notifications` - Subscribe to existing notification types.

- `/notif_config` - Get your current notifications configuration.

- `/enable_notif_config` - Enables a specific notification.

- `/disable_notif_config` - Disables a specific notification.

- `/delete_time_zone` - Removes one of your configured time zones.

- `/help` - Information about bot's commands and what they provide.

- `/favourite_teams` - List of user's favourite teams.

- `/favourite_leagues` - List of user's favourite leagues.
 
- `/add_favourite_team` - Adds a team to user's favourites.

- `/add_favourite_league` - Adds a league to your favourites.

- `/delete_favourite_team` - Removes a team from your favourites.

- `/delete_favourite_league` - Removes a league from your favourites.

- `/available_leagues` - Available team's that can be queried with the other commands.

- `/next_match` - Retrieves information about next scheduled match for an specific team, including rival, date (in different timezones), league and round which is being played.

- `/last_match` - Retrieves information about last match played by the specific team, including  scores, rival, date (in different timezones), league, roung and highlights

- *`/upcoming_matches [optional [team_id] [ft-fteams-favourite_teams] [fl-fleagues-favourite_leagues]]` - List of upcoming matches.

- `/next_match_league` - Retrieves information about next scheduled match for an specific tournament, including rival, date (in different timezones), league and round which is being played.

- `/next_matches_league` - Retrieves information about matches to be played on the day that the next match of a tournament is happening.

- `/last_match_league` - Retrieves information about last match played by the specific tournament, including  scores, rival, date (in different timezones), league, roung and highlights

- **`/today_matches` - Retrieves information about matches to be played on the current day.

- **`/tomorrow_matches` - Retrieves information about matches to be played on the following day.

- **`/last_played_matches` - Retrieves information about matches played on the previous day.


## Requirements

- Python 3.8+
- [Docker](https://www.docker.com)
- [Telegram Bot Token](https://core.telegram.org/bots)
