from src.emojis import Emojis

NOTIFICATIONS_ENABLEMENT = (
    f"{Emojis.SPEAKING_HEAD.value} {Emojis.SPEAKING_HEAD.value} Announcement {Emojis.SPEAKING_HEAD.value} {Emojis.SPEAKING_HEAD.value}\n\n"
    f"Hi! {Emojis.WAVING_HAND.value}\n\n"
    f"We have just released a new BETA version with the <em>Notifications</em> feature!\n\n"
    f"You can now receive automatic notifications from me! Getting, for example, reminders when there are matches approaching corresponding to your favourite "
    f"teams or leagues, or when a match was just played. First, you need to subscribe to notifications with /subscribe_to_notifications command, then you will"
    f" be able to check them and their status with /notif_config and don't worry, you can enable/disable them as you please, with /enable_notif_config and /disable_notif_config commands.\n\n"
    f"{Emojis.FOLDED_HANDS.value} Please bear in mind that, even though it's tested, this is a BETA feature released in a basic version, so more improvements will come in the future.\n\n"
    f"Thanks! I hope you enjoy the new feature!"
)


SET_NOTIF_TIMES_ENABLEMENT = (
    f"{Emojis.SPEAKING_HEAD.value} {Emojis.SPEAKING_HEAD.value} Announcement {Emojis.SPEAKING_HEAD.value} {Emojis.SPEAKING_HEAD.value}\n\n"
    f"Hi! {Emojis.WAVING_HAND.value}\n\n"
    f"We have just released a new functionality that allow you configure the time you get your <strong>daily</strong> notifications!\n\n"
    f"With the World Cup {Emojis.GLOBE.value}{Emojis.TROPHY.value} approaching, you might want to have the tournament configured as your favourite, so automatically every day you will get the "
    f"daily agenda of it :). \n\nUntil now, daily notifications (for matches of favourite teams & leagues) were being informed always at <strong>8:00 am</strong> (time on the main time zone configured for the user). \n\n"
    f"Given time zone differences, sometimes matches happen at a time earlier than that in some user's time zones, like it will happen in the World Cup. "
    f" Therefore, the reason of releasing this new small functionality which allow you to choose the time in the morning you would like to get the daily notifications {Emojis.PARTYING_FACE.value}.\n\n"
    f"{Emojis.RIGHT_FACING_FIST.value} For doing so, a new command was introduced: /set_daily_notif_time. It will display you the times to you, and you can select it accordingly in order to set your desired notification time.\n\n"
    f"Thanks! And hope you enjoy the World Cup! \n\n*And good luck to your national team in case it's participating ;)"
)
