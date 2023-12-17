![eww bot half page](https://github.com/darkharasho/eww-bot/assets/144265798/36832218-b1e3-4606-8483-057c50197a6f)

# Discord bot for WvW Guild Management

A Guild Wars 2 bot for ever growing WvW Guild management commands. Currently, this bot assumes self hosting. To run your own, download the code, follow the requirements below, and happy WvW-ing!

Made with ❤️ by Engaging Without Warning [EWW]

## Looking for more info?
[Check out the Wiki!](https://github.com/darkharasho/eww-bot/wiki)

## Start the App
```commandline
poetry run uvicorn main:app --reload --port 8000 --host 0.0.0.0
```
Start without uvicorn
```commandline
BOT_ONLY=true poetry run python main.py
```

Get into shell:
```commandline
poetry shell
BOT_ONLY=true PYTHONSTARTUP=main.py python
```

## Todo list

- [ ] add optional description to the google sheet and import-builds
- [ ] Command to make a builds channel
- [ ] Guild Rank Verification
- [ ] Allow pingable role for ArcDPS notifications
- [x] Limit bot commands to a set of channels
