# MOE Login bonus script

This script reads data from user-defined chat channels for Myth of Empires in-game chat, and when a user types /dailyreward, it will give them the specified items.

We query the sqlite database to obtain the steam64 ID of a user, if you are using mysql (or some other variant), you'll need to modify this to work with mysql.


## Recommendations

It is intentionally simple and does not read or write redis, thus should be fairly safe. The chat service is extremely sensitive and reading or writing redis without using the native API would be a bad idea.

The first iteration does not support multiple webhooks tied to different channels, but you can simply run more than one instance of the script to accomplish that.


## Features

- Gives players free stuff daily.
- Resets at midnight server time.

## Configuration

You need mcrcon in the same directory as this script! https://github.com/Tiiffi/mcrcon

The script is configured via environment variables that can be set in a `.env` file located in the same directory as the script.

You can find the channel IDs in your chat logs C:\PATH\TO\MOESERVER\MatrixServerTool\chat_logs\, which look like this:

{"addr":"1.2.3.4:28328","conn id":16,"content":"GuildName^^\u0026\u0026Im a little chat log short and stout","content type":1,"conv type":2,"from":"610133034AD89937F996C9BA3AA4859A","from nick":"timex","level":"info","msg":"chat msg","role":"chater","time":"2024-02-23T09:33:16-05:00","to":"f3a3ffec643000"}

{"addr":"1.2.3.4:35237","conn id":23,"content":"Dogs of War^^\u0026\u0026here is my handle here is my spout","content type":1,"conv type":2,"from":"0C0D025C4A38BEAB5CEAE1AA309835D2","from nick":"timex-DOGS","level":"info","msg":"chat msg","role":"chater","time":"2024-02-25T11:09:34-05:00","to":"f3a3fe34324000"}

Add the value of to: here to the .env file under GLOBAL_CHANNELS

You can configure the CHANNEL_FRIENDLY_NAMES in the .env file to display the to: channel as something more readable.

Configure DISCORD_WEBHOOK to your webhook URL.

Configure the chat log path in .env.



Example:
DISCORD_WEBHOOK="https://discord.com/api/webhooks/somewebhook"
GLOBAL_CHANNELS=f3a3ffec543000,f3a3fe34432000
CHANNEL_FRIENDLY_NAMES=f3a3ffec543000=Eastern,f3a3fe34432000=Central
LOG_DIRECTORY=C:\moenew\MatrixServerTool\chat_logs\
DATABASE_PATH=C:\moenew\WindowsPrivateServer\MOE\Saved\SaveGames\BigPrivate\moe_role.db
RCON_PASSWORD="SomePassword"

The script will create a CSV file to track daily logins, which will look like this:
s_account_uid,from_nick,Date,Status
76561197992631099,timex,2024-04-10,0

The final column in each row is 0 or 1, if it is not 0, the user is banned, so change this number if someone is being naughty and needs punishment.

### Environment Variables


- `DISCORD_WEBHOOK`: The URL of the discord webhook.
- `GLOBAL_CHANNELS`: The comma-separated list of channel IDs.
- `CHANNEL_FRIENDLY_NAMES`: channelid=ChannelName, comma separated list of channelname=friendlyname relationships
- `LOG_DIRECTORY`: Directory where the chat logs reside.
- `RCON_PASSWORD`: Your remote/RCON password.
- `DATABASE_PATH`: The full path to your moe_role.db

## Windows installation

For this part, I'll do the steps using a windows admin account. You can do things how you want to suit your environment.
Download and install python (https://www.python.org/downloads/windows/), note that there is an option in the installer to install for all users, if preferred. Make sure to select the following options:
- Install pip
- Add python to the environment
- Make python the default program to run .py files

If haven't already, upgrade pip and install setuptools:
- python -m pip install --upgrade pip
- pip install setuptools

Install the module requirements (if you're missing any):
- pip install module_name_here

## Usage

You can run the script manually with:
```python moeDailyLogin.py```

or

`python3 /path/to/moeDailyLogin.py`

## Getting help

Feel free to submit a PR or issue as needed.

I can be found in the Dogs of War discord.  https://discord.com/invite/8y5keJYzK3

General community support is also available in the MOE Admins United discord. https://discord.gg/7vrFzfAMvG