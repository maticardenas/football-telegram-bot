cd /usr/football_api
/usr/local/bin/python -m poetry shell
# PSG
/usr/local/bin/python -m poetry run python /usr/football_api/team_fixture_notifier.py 2021 85
/usr/local/bin/python -m poetry run python /usr/football_api/team_fixture_notifier.py 2022 85
# River
/usr/local/bin/python -m poetry run python /usr/football_api/team_fixture_notifier.py 2021 435
/usr/local/bin/python -m poetry run python /usr/football_api/team_fixture_notifier.py 2022 435
# Argentina
/usr/local/bin/python -m poetry run python /usr/football_api/team_fixture_notifier.py 2021 26
/usr/local/bin/python -m poetry run python /usr/football_api/team_fixture_notifier.py 2022 26