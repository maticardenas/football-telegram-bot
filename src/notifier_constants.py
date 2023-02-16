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

# Surrounding days to check when retrieving fixtures, for validating them against
# the user's time zone
SURROUNDING_INDEXES = {
    "today": (-1, 0, 1),
    "tomorrow": (0, 1, 2),
    "yesterday": (-2, -1, 0),
}

TELEGRAM_MSG_LENGTH_LIMIT = 3500

# PAGE SIZES
TIME_ZONES_PAGE_SIZE = 10


# COMMANDS HANDLERS IDS
ADD_FAVOURITE_TEAM = 4
ADD_FAVOURITE_LEAGUE = 5
SEARCH_TEAM = 6
SEARCH_LEAGUE = 7
SEARCH_LEAGUES_BY_COUNTRY = 8
NEXT_MATCH = 9
LAST_MATCH = 10
NEXT_MATCH_LEAGUE = 11
LAST_MATCH_LEAGUE = 12
SET_MAIN_TIME_ZONE = 13
SET_ADD_TIME_ZONE = 14
SEARCH_TIME_ZONE = 15
