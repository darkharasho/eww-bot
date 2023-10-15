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

## Todo list

- [ ] Look into per user editing of attendance or something
- [ ] add optional description to the google sheet and import-builds
- [ ] Command to make a builds channel
- [x] Add vod review tracking
- [x] Register gw2 API key
  - [x] Personal stats
