NOT_PLAYED_OR_FINISHED_MATCH_STATUSES = [
    "Match Abandoned",
    "Match Suspended",
    "Match Postponed",
    "Technical loss",
    "Walkover",
    "Match Cancelled",
    "Match Interrupted",
]

NOTIFICATION_TYPES = [
    {
        "name": "FT Today",
        "description": "Favourite teams matches of current day. (At 8 am local time)",
    },
    {
        "name": "FL Today",
        "description": "Favourite leagues matches of current day. (At 8 am local time)",
    },
    {
        "name": "Upcoming FT",
        "description": "Upcoming favourite team match. (30 min.)",
    },
    {
        "name": "Played FT",
        "description": "Played favourite team match with result after it finished.",
    },
]

TELEGRAM_MSG_LENGTH_LIMIT = 3500
