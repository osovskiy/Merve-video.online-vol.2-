# YouTube Merge

YouTube Merge - this is a website and a telegram bot for automatically editing videos from YouTube

YouTube Merge uses microservice architecture, for it to work, you need to include separately app_video, bot, site

## Telegram bot settings

There is a settings.ini file in the bot folder
In the [BOT] category, you need to specify the bot token with @botfather and the ID of the telegram
account from which files will be sent to the bot

In the [CLIENT] category, you need to specify the API ID, API HASH, username and phone number of the
account from which the video will be sent to the telegram bot.
You can get API ID and API HASH for the client at https://my.telegram.org/auth

CLIENT is needed to bypass telegram restrictions on the size of files that the bot can send.

To connect payments, you must receive a QIWI token https://qiwi.com/p2p-admin/transfers/api
And paste it into [QIWI]

## Site settings

Videos are sent to the mail via google drive, you need to create a new application in google and
upload cleint_secrets.json to the site folder. After the first authorization, it will create token.json
and authorization will take place automatically.

For the correct operation of sending letters to the mail, you need to create an application password
in your google account and write it in the [MAIL] category in settings.ini HOST and PORT I left the default gmail

you also need to duplicate the qiwi token in settings.ini in the site folder
