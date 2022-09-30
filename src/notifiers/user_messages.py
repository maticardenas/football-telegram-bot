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
