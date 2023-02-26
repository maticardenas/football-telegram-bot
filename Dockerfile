FROM python:3.11
LABEL maintainer "Matias Cardenas"
LABEL description "Python 3.11 image containing Football Notifications APP"

USER root
RUN apt-get update \
&& apt-get install gcc -y \
&& apt-get clean \
&& apt-get install cron -y \
&& apt-get install bash \
&& apt-get install vim -y \
&& apt-get install libpq-dev python-dev -y

ADD football_notif_crontab /etc/cron.d/football_notif_crontab
RUN chmod 777 /etc/cron.d/football_notif_crontab
RUN crontab /etc/cron.d/football_notif_crontab
RUN touch /var/log/cron_log.log
RUN pip install poetry

WORKDIR /usr/football_api

COPY pyproject.toml .
COPY poetry.lock .

RUN poetry install -vvv --no-root

COPY ./config ./config
COPY ./dev_scripts ./dev_scripts
COPY ./src ./src
COPY ./tests ./tests
COPY team_fixture_notifier.py .
COPY head_to_head_updater.py .
COPY football_notifier.env .

RUN cat football_notifier.env >> /etc/environment

CMD cron && tail -f /var/log/cron_log.log
