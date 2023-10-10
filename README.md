![image](https://github.com/darkharasho/eww-bot/assets/144265798/456fed62-a6a7-4149-abf1-0d75404bf2ab)

# Discord bot for WvW Guild Management

A Guild Wars 2 bot for ever growing WvW Guild management commands. Currently, this bot assumes self hosting. To run your own, download the code, follow the requirements below, and happy WvW-ing!

Made with ❤️ by Engaging Without Warning [EWW]

## Index
- [Features](#features)
  - [Attendance Tracking](#attendance-tracking)
    - [Take Attendance](#take-attendance)
    - [Historical Attendance](#historical-attendance)
    - [Check User Attendance History](#check-user-attendance-history)
  - [Build Management](#build-management)
    - [Set Build](#set-build)
    - [Build Import](#build-import)
  - [User Management](#user-management)
    - [Time In Role](#time-in-role)
    - [Applications](#applications)
  - [WvW](#wvw)
    - [Raid Notification](#raid-notification)
- [Requirements](#requirements)
  - [Settings](#settings)
    - [Mandatory](#mandatory)
    - [Optional](#optional)
    - [Application Options](#application-options)
  - [Discord Setup](#discord-setup)
- [Todo](#todo)

## Features:

### Attendance Tracking

#### Take Attendance

`/attendance channel: voice_channel` takes count of who is in a voice channel at the time
NOTE: Only counts attendance once per day

<img src="https://github.com/michaelstephens/eww-bot/assets/1581475/b33fede2-f525-4fc1-8ea2-c5779097891d" width="250">

**Required Configs:**
- `AttendanceJsonFile`
- `GuildMemberRole`
- `RaidTime`
- `RaidDays`

#### Historical Attendance

`/show-attendance` shows totals for attendance

<img src="https://github.com/michaelstephens/eww-bot/assets/1581475/505c885c-6c83-4dcb-bf91-5e2ed8d4e6ed" width="250">

**Required Configs:**
- `AttendanceJsonFile`
- `GuildMemberRole`
- `RaidTime`
- `RaidDays`

#### Check User Attendance History

`/check-attendance member: member` gets the full history of when the person attended raid, sorted by highest count

<img src="https://github.com/michaelstephens/eww-bot/assets/1581475/57a5eab1-2687-4d71-b583-91b02d45e145" width="250">

**Required Configs:**
- `AttendanceJsonFile`
- `GuildMemberRole`
- `RaidTime`
- `RaidDays`

### Build Management

#### Set Build

`/set-build class_name announce`, in discord command to make a new build and post it to a forum channel as well as modify
your spreadsheet.

<img src="https://github.com/michaelstephens/eww-bot/assets/1581475/03c53b1f-7980-4ba4-a112-7356c2c9f80e" width="400">


<img src="https://github.com/michaelstephens/eww-bot/assets/1581475/99b57acc-f167-4490-a155-2ef0e7f868ce" width="250">

**Required Configs:**
- `Channel-ID`
- `UpdateChannelID`
- `GoogleCredsFile`
- `GoogleSheetName`
- `BuildManagerRoles`

#### Build Import

`/import-builds announce: true/false` Imports builds from a google sheet and posts them in a forum channel, correctly
tagged with the base class and class icon

<img src="https://github.com/michaelstephens/eww-bot/assets/1581475/bafb42f4-aa5f-4600-b7be-9d7d2fac9acd" width="250">

**Required Configs:**
- `Channel-ID`
- `UpdateChannelID`
- `GoogleCredsFile`
- `GoogleSheetName`
- `BuildManagerRoles`

### User Management

#### Time in Role

`/time-in-role member: member` Shows how long a user has been in their roles (limited to discord's 90 day policy on
audit log)

<img src="https://github.com/michaelstephens/eww-bot/assets/1581475/5f2edde4-173f-44d9-b992-e3bbb2388d2a" width="250">

#### Applications

`/apply` - Have a user apply to join your guild (supports a questionaire and approve/deny with role setting). Anyone can use this command.
To see how to set it up look at [Application Options](#application-options)

<img src="https://github.com/michaelstephens/eww-bot/assets/1581475/2f6df484-7281-46c3-a569-50611622afd0" width="250">

Once a user applies, the bot will DM them your questions

<img src="https://github.com/michaelstephens/eww-bot/assets/1581475/2bee1ba6-22f4-4892-85ed-3a34abca25b4" width="250">

Once submitted it posts to a channel of your choosing for approval. 

<img src="https://github.com/michaelstephens/eww-bot/assets/1581475/a65b206c-357b-48a4-bb69-e1d474b0cadd" width="250">

Approve/Reject have a "Reason" modal to give more context

<img src="https://github.com/michaelstephens/eww-bot/assets/1581475/93f50773-c803-4098-8aad-af67911f0c1f" width="250">

**Required Configs:**
- `Applications`
  - `application_channel_id`
  - `accepted_roles`
  - `questions`
    - `text`
    - `field_type`
    - `options`

### WvW

#### Raid Notification

`/raid-notification [CHANNEL_NAME] [MAP] [OPEN_TAG]` - Puts a ping in a given channel and provides the map & team name, map colors, current scores, and k/d

<img src="https://github.com/michaelstephens/eww-bot/assets/1581475/1417d5a4-c1f7-4d45-8be1-1d52a078287b" width="250">

**Required Config:**
- `GW2ApiKey`
- `RaidNotification`
  - `Channel`
  - `Roles`
  - `OpenRoles`

## Requirements

```
sudo apt update
sudo apt install python3-pip
```

Install [poetry](https://python-poetry.org/docs/#installation)

`poetry install`
`poetry run python main.py`

### Settings
All settings are stored in `config/config.json`
#### Mandatory
- `Token` - `(Str)` Discord Bot Auth Token
- `Guild` - `(Str)` String name of your Discord server
- `Guild-ID` - `(Int)` ID of your Discord Server
- `ApplicationID` - `(Int)` Application ID of your Discord Bot
- `Channel-ID` - `(Int)` Channel ID of the builds forum channel
- `UpdateChannelID` - `(Int)` Announcement channel for new build posts
- `GoogleCredsFile` - `(Str)` Google credentials for Google sheets builds
- `GoogleSheetName` - `(Str)` Name of your Google Sheet
- 'GW2ApiKey` - `(Str)` Guild Wars 2 API key

#### Optional
- `AllowedRoles` - `(List[Str])` Roles allowed to use bot commands 
  - Default: `'Admin`
- `BuildManagerRoles` - `(List[Str])` Roles allowed to create/update builds
  - Default: `ALLOWED_ROLES`
- `AttendanceJsonFile` - `(Str)` JSON file to store attendance data
  - Default: `'attendance.json'`
- `AutoAttendance` - `(Bool)` NOT IMPLEMENTED 
  - Default: `False`
- `GuildMemberRole` - `(Str)` Basic member role
  - Default: `'Member'`
- `RaidTime` - `(Int)` Time your raids start, in Server time
  - Default: `18`
- `RaidDays` - `(List[Int])` Days you raid. Monday is 0 Sunday is 6
  - Default: `[1, 2, 3, 5]`
- `DisabledModules` - `(List[Int])` List of disabled `/` commands. Follows the kebab case command name in discord.
  - Default: `[]`
- 'RaidNotification` - `(Dict)` Posting raid pings
  - `Channels` - `(List[Str])` Which channels you would like your raid notification to go
  - `Roles` - `(List[Str])` List of roles to ping
  - `OpenRoles` - `(List[Str])` List of optional roles to ping (Ex. An open tag notification role)

#### Application Options
- `Applications` - `(Dict)` Top level
  - `application_channel_id` - `(Int)` Channel ID where applications will go for approval/rejection
  - `accepted_roles` - `(List[Str])` Role Names that will be automatically applied on approval
  - `questions` - `(List)` Top level of questions (Max of 24)
    - `text` - `(Str)` The question to ask
    - `field_type` - `(Str)` Options: `["input", "select"]` Whether the question is a dropdown or user's input
    - `options` - `(List[Str])` If the `field_type` is `"select"`, this is a list of the possible options

### Discord Setup

Build manager assumes two things:

1. Your build channel is a [discord
   forum](https://support.discord.com/hc/en-us/articles/6208479917079-Forum-Channels-FAQ)
2. Your channel has one tag per [base class](https://www.guildwars2.com/en/the-game/professions/) in GW2

## Todo list

- [ ] Look into per user editing of attendance or something
- [ ] add optional description to the google sheet and import-builds
- [ ] Command to make a builds channel
- [x] Add vod review tracking
- [x] Register gw2 API key
  - [x] Personal stats
