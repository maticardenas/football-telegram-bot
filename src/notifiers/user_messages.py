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


CONVERSATION_ENABLEMENT = (
    f"{Emojis.SPEAKING_HEAD.value} {Emojis.SPEAKING_HEAD.value} <strong>NO MORE ID'S</strong> {Emojis.SMILEY_FACE.value}{Emojis.PARTYING_FACE.value}\n\n"
    f"Hi! {Emojis.WAVING_HAND.value}\n\n"
    f"We are pleased to announce that we have released a new improvement which changes the way commands work, making it not necessary to keep and use <em>ids</em> anymore :).\n\n"
    f"All commands have now a <em>search</em> of <em>teams</em> and <em>leagues</em> embedded, so therefore, whenever for example you would like to add a favourite team and look for a next match, you will be able just to call the command and, "
    f"in the form of a conversation (yes, not need to append anything after commands anymore!) enter the (part of) name of the team/league you want and the bot will start showing you a list of the found ones, in the form of "
    f"<strong>BUTTONS!</strong> (doesn't it sound good?). \n\n"
    f"{Emojis.RIGHT_FACING_FIST.value} This means that consequently, you don't need to manipulate the <em>ids</em> anymore, and you can just worry on pressing the commands. Also, "
    f"as <em>search</em> is embedded in all commands now, <em>search_team</em>, <em>search_league</em> and <em>seach_time_zone</em> commands will be deprecated, as they become unnecesary {Emojis.SMILEY_FACE.value}\n\n"
    f"{Emojis.ROBOT.value} This new feature has allowed to think and unblock us in the development of other news in the roadmap, so hold on tight! we are planning to add:\n\n"
    f"• <strong>Friendly setup</strong> - A handy and guided conversation for starting using the bot, when entering <em>/start</em> command.\n"
    f"• <strong>Follow players</strong> - Keep track of your favourite player games, stats and news.\n"
    f"• <strong>Standings and line-ups</strong> - Check how your team is doing in its tournaments, as well as getting line-ups before games\n\n"
    # f"{Emojis.DEVELOPER.value} <a href='https://www.buymeacoffee.com/maticardenas'>Buy me a coffee</a> - if you feel like contributing with this work "
)


LANGUAGES_ENABLEMENT = (
    f"{Emojis.SPEAKING_HEAD.value} {Emojis.SPEAKING_HEAD.value} <strong>CUSTOM LANGUAGES SUPPORT</strong> {Emojis.SMILEY_FACE.value}{Emojis.PARTYING_FACE.value}\n\n"
    f"Hi! {Emojis.WAVING_HAND.value}\n\n"
    f"We are pleased to announce that we have released a new feature which allows you to configure your preferred language.\n\n"
    f"You can configure you league through /set_language command, inserting the language by name (this is the only thing you need to always do in English :)) and choosing the one of your preference.\n"
    f"You can query you language through /my_language command and change it at any time :)\n\n"
    f"{Emojis.RIGHT_FACING_FIST.value} Bear in mind that the usage of a custom language MIGHT come with a slight degradation in performance when using the bot,"
    f" however we are already working in an improvement for this, which we will release soon. \n\nEnjoy!{Emojis.PARTYING_FACE.value}"
)


STATISTICS_KICK_OFF = (
    f"{Emojis.SPEAKING_HEAD.value} {Emojis.SPEAKING_HEAD.value} <strong>STATISTICS LAUNCH!</strong> {Emojis.CHART_INCREASING.value}{Emojis.CHART_INCREASING.value}\n\n"
    f"Hello! {Emojis.WAVING_HAND.value}\n\n"
    f"With a goal to continuously enhance our data handling and offerings, we are excited to introduce a new way for you to access"
    f" statistics about your favorite teams and leagues {Emojis.SMILEY_FACE.value}.\n\n"
    f"{Emojis.RIGHT_FACING_FIST.value} This is just the beginning of a long journey, but to demonstrate our commitment, we've already rolled out the command /team_summary {Emojis.DEVELOPER.value}\n\n"
    f"At the moment, this simple command provides a glimpse into your team's recent match history, including goals scored/received and"
    f" information on the last and next matches. \n\n{Emojis.LIGHT_BULB.value} This is just the first step in our ongoing effort to improve our statistics offerings, so just letting you know this and "
    f"you will hear from us again soon {Emojis.SMILEY_FACE.value}"
)


GAMES_EVENTS_KICK_OFF = f"""
    {Emojis.PARTYING_FACE.value} {Emojis.PARTYING_FACE.value} Exciting News! {Emojis.PARTYING_FACE.value} {Emojis.PARTYING_FACE.value}

We're thrilled to announce that from now on, you'll gain insights into players who scored goals, received yellow or red cards, and more in your notifications {Emojis.SMILEY_FACE.value}. 
This feature has been highly anticipated by all of you and is sure to provide valuable information about your favorite matches.

{Emojis.SOCCER_BALL.value} But wait, there's more! The debut of this feature will also unblock several other exciting features that will follow in the coming weeks. 
So once again, thanks for your continued support and stay tuned for more updates!

{Emojis.FAMILY.value} Don't forget to spread the word about this amazing update to your friends and fellow football enthusiasts. 

Happy football watching! 🎉
    """


TIMELINES = f"""
    {Emojis.PARTYING_FACE.value} {Emojis.PARTYING_FACE.value} More info for your games! {Emojis.PARTYING_FACE.value} {Emojis.PARTYING_FACE.value}

🎉 As promised, we've added more info about match events in your notifications, along with some extra goodies.

{Emojis.SMILEY_FACE.value} We have introduced <strong>TIMELINES</strong> for your favorite matches!. When you use the /last_match command, you'll see a <strong>"Show Timeline"</strong> button below the notification. Clicking on it will give you all the event from the game and their times. 😍

{Emojis.RIGHT_FACING_FIST.value} What better way to chat with friends and discuss your favorite team's and coach's decisions during the game? 👪

And guess what? When your favorite team finishes playing, you'll get the full timeline as a default message, along with the result. 

{Emojis.MAN_RUNNING.value} Now, if you feel like the timelines are too much for this specific case, you can easily disable this feature in your configuration. 
Just use the /notif_config command, and you're back to a simpler, result-focused experience.  🛏️

{Emojis.PARTYING_FACE.value} And there's more coming soon! 

Happy football watching!
    """
