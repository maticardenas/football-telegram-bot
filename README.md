

# Football Telegram Bot

## Description

This application consumes, stores and processes football information and makes it available through a Telegram bot.


## Main Functionalities

So far, it processes information about specific team's **fixtures**, informing past and future games.


## Bot Commands

- `/next_match <team>` > Retrieves information about next scheduled match for an specific team, including rival, date (in different timezones), league and round which is being played.
- `/last_match <team>` > Retrieves information about last match played by the specific team, including  scores, rival, date (in different timezones), league, roung and highlights


## Implementation Overview

Application is written in Python, as database engine uses PostgreSQL, jobs are scheduled using cronjob and it is finally deployed with Docker.

It consumes [RAPID API - API FOOTBALL](https://rapidapi.com/api-sports/api/api-football) endpoints, processes its data and stores it to the database. This runs in cronjobs scheduled, and then on demand user can request the processed team's information through Telegram's commands.


## Requirements

- Python 3.8+
- [Docker](https://www.docker.com/
- [Telegram Bot Token](https://core.telegram.org/bots)
