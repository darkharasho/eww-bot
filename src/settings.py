# settings.py
import json

import discord
from discord import SelectMenu, SelectOption

# Configuration variables
raw_config = open('config/config.json')
config = json.load(raw_config)

# Mandatory
TOKEN = config['Token']
GUILD = config['Guild']
GUILD_ID = config['GuildID']
APPLICATION_ID = config['ApplicationID']
GOOGLE_CREDS_FILE = config['GoogleCredsFile']
GOOGLE_SHEET_NAME = config['GoogleSheetName']
GW2_API_KEY = config['GW2ApiKey']
RAID_REMINDER_CLASSES = config.get('RaidReminderClasses', None)
MAX_LEADERBOARD_MEMBERS = config.get('MaxLeaderboardMembers', 10)
# (0 is Monday, 6 is Sunday)
APPLICATIONS = config.get('Applications', {})

MODULES = [
    "apply",
    "attendance",
    "check-attendance",
    "import-builds",
    "raid-notification",
    "raid-reminder",
    "set-build",
    "show-attendance",
    "time-in-role",
    "toggle-soundboard"
]

CONFIG_OPTIONS = [
    SelectOption(label="Guild Member Role",
                 value="GuildMemberRole",
                 description="Used In: Attendance, Raid Notifications, Raid Reminders",
                 emoji="🛡️"),
    SelectOption(label="Disable Module",
                 value="DisableModule",
                 description="Used In: None - Disables a module so the slash command is inaccessible",
                 emoji="❌"),
    SelectOption(label="Allowed Admin Roles",
                 value="AllowedAdminRoles",
                 description="Used In: All - which roles are allowed to run all bot commands",
                 emoji="👑"),
    SelectOption(label="Build Manager Roles",
                 value="BuildManagerRoles",
                 description="Used In: set-build, import-builds - which roles are allowed to run all build commands",
                 emoji="🦺"),
    SelectOption(label="Commander Roles",
                 value="CommanderRoles",
                 description="Used In: raid-notifications - which roles are allowed to run all raid commands",
                 emoji="🔰"),
    SelectOption(label="Raid Days",
                 value="RaidDays",
                 description="Used In: Raid Reminder, Attendance, Auto Attendance",
                 emoji="⚔️"),
    SelectOption(label="Build Forum Channel",
                 value="BuildForumChannel",
                 description="Used In: Set Build, Import Builds",
                 emoji="💬"),
    SelectOption(label="Build Update Channel",
                 value="BuildUpdateChannel",
                 description="Used In: Set Build, Import Builds",
                 emoji="🔔"),
    SelectOption(label="Auto Attendance",
                 value="AutoAttendance",
                 description="Requires: Attendance Module, Show Attendance Module",
                 emoji="📋"),
    SelectOption(label="Raid Notifications",
                 value="RaidNotification",
                 description="Used In: Raid Notification",
                 emoji="💥"),
    SelectOption(label="Raid Reminders",
                 value="RaidReminder",
                 description="Requires: Raid Days - Sets up a timed reminder post for your raid schedule.",
                 emoji="🎮"),
    SelectOption(label="Vod Review Channel",
                 value="ReviewForumChannel",
                 description="Used In: Propose - Which forum channel your vod reviews live in.",
                 emoji="🎬"),
    SelectOption(label="ArcDPS Updates",
                 value="ArcdpsUpdates",
                 description="Automatic notifications for ArcDPS updates",
                 emoji="🧮"),
    SelectOption(label="Game Update Notifications",
                 value="GameUpdates",
                 description="Automatic notifications for Guild Wars 2 updates",
                 emoji="📰")
]

SET_BUILD_UPDATE_CHANNEL =[
    {
        "text": "# Channel to post build updates:",
        "key": "$SINGLE - channel_id",
        "field_type": "input",
        "response_type": "text_channel"
    }
]

AUTO_ATTENDANCE_CONFIG = questions = [
    {
        "text": "# Enabled?",
        "key": "enabled",
        "field_type": "select",
        "options": [True, False],
        "response_type": bool
    },
    {
        "text": "# Channel to send attendance sheet:",
        "key": "channel_id",
        "field_type": "input",
        "response_type": "text_channel"
    },
    {
        "text": "# Time to run\n### In 24hr format UTC, ex: 1:05 is 6:05pm PST",
        "key": "time",
        "field_type": "input",
        "response_type": "time"
    }
]

RAID_NOTIFICATION_CONFIG = [
    {
        "text": "# Roles to ping",
        "key": "role_ids",
        "field_type": "input",
        "response_type": "roles"
    },
    {
        "text": "# Open Tag Roles to ping",
        "key": "open_tag_role_ids",
        "field_type": "input",
        "response_type": "roles"
    }
]

RAID_REMINDER_CONFIG = [
    {
        "text": "# Channel to post the reminder",
        "key": "channel_id",
        "field_type": "input",
        "response_type": "text_channel"
    },
    {
        "text": "# Roles to ping",
        "key": "role_ids",
        "field_type": "input",
        "response_type": "roles"
    },
    {
        "text": "# Style of the table",
        "key": "table_style",
        "field_type": "select",
        "options": ["fancy_grid", "simple", "list_view"]
    },
    {
        "text": "# Hide empty rows?",
        "key": "hide_empty_rows",
        "field_type": "select",
        "options": [True, False],
        "response_type": bool
    },
    {
        "text": "# Time to Post Notification\n### In 24hr format UTC, ex: 1:05 is 6:05pm PST",
        "key": "time",
        "field_type": "input",
        "response_type": "time"
    },
    {
        "text": "# Classes\n### Max: 25\n(list all numbers)",
        "key": "classes",
        "field_type": "input",
        "response_type": "gw2_classes"
    }
]

SET_ARCDPS_UPDATES = [
    {
        "text": "# Enabled?",
        "key": "enabled",
        "field_type": "select",
        "options": [True, False],
        "response_type": bool
    },
    {
        "text": "# Channel to post the updates in",
        "key": "channel_id",
        "field_type": "input",
        "response_type": "text_channel"
    }
]

SET_GAME_UPDATES = [
    {
        "text": "# Enabled?",
        "key": "enabled",
        "field_type": "select",
        "options": [True, False],
        "response_type": bool
    },
    {
        "text": "# Channel to post the updates in",
        "key": "channel_id",
        "field_type": "input",
        "response_type": "text_channel"
    }
]

SET_COMMANDER_ROLES = [
    {
        "text": "# Commander Roles",
        "key": "$LIST",
        "field_type": "input",
        "response_type": "roles"
    }
]

# Constants
CLASS_COLORS = {
    "Warrior": 0xFFD166,
    "Guardian": 0x72C1D9,
    "Revenant": 0xD16E5A,
    "Engineer": 0xD09C59,
    "Ranger": 0x8CDC82,
    "Thief": 0xC08F95,
    "Elementalist": 0xDC423E,
    "Mesmer": 0xB679D5,
    "Necromancer": 0x52A76F
}

CLASS_ELITE_SPECS = {
    "Warrior": ["Warrior", "Berserker", "Spellbreaker", "Bladesworn"],
    "Necromancer": ["Necromancer", "Reaper", "Scourge", "Harbinger"],
    "Elementalist": ["Elementalist", "Weaver", "Tempest", "Catalyst"],
    "Guardian": ["Guardian", "Firebrand", "Dragonhunter", "Willbender"],
    "Revenant": ["Revenant", "Renegade", "Herald", "Vindicator"],
    "Engineer": ["Engineer", "Scrapper", "Holosmith", "Mechanist"],
    "Thief": ["Thief", "Deadeye", "Specter", "Daredevil"],
    "Ranger": ["Ranger", "Druid", "Soulbeast", "Untamed"],
    "Mesmer": ["Mesmer", "Chronomancer", "Mirage", "Virtuoso"]
}

BASE_CLASSES = [
    "Warrior", "Berserker", "Spellbreaker", "Bladesworn",
    "Necromancer", "Reaper", "Scourge", "Harbinger",
    "Elementalist", "Weaver", "Tempest", "Catalyst",
    "Guardian", "Firebrand", "Dragonhunter", "Willbender",
    "Revenant", "Renegade", "Herald", "Vindicator",
    "Engineer", "Scrapper", "Holosmith", "Mechanist",
    "Thief", "Deadeye", "Specter", "Daredevil",
    "Ranger", "Druid", "Soulbeast", "Untamed",
    "Mesmer", "Chronomancer", "Mirage", "Virtuoso"
]

SERVER_NAMES = [
    {"id": 1001, "name": "Anvil Rock", "abbreviation": "AR"},
    {"id": 1002, "name": "Borlis Pass", "abbreviation": "BP"},
    {"id": 1003, "name": "Yak's Bend", "abbreviation": "YB"},
    {"id": 1004, "name": "Henge of Denravi", "abbreviation": "HoD"},
    {"id": 1005, "name": "Maguuma", "abbreviation": "Mag"},
    {"id": 1006, "name": "Sorrow's Furnace", "abbreviation": "SF"},
    {"id": 1007, "name": "Gate of Madness", "abbreviation": "GoM"},
    {"id": 1008, "name": "Jade Quarry", "abbreviation": "JQ"},
    {"id": 1009, "name": "Fort Aspenwood", "abbreviation": "FA"},
    {"id": 1010, "name": "Ehmry Bay", "abbreviation": "EB"},
    {"id": 1011, "name": "Stormbluff Isle", "abbreviation": "SBI"},
    {"id": 1012, "name": "Darkhaven", "abbreviation": "DH"},
    {"id": 1013, "name": "Sanctum of Rall", "abbreviation": "SoR"},
    {"id": 1014, "name": "Crystal Desert", "abbreviation": "CD"},
    {"id": 1015, "name": "Isle of Janthir", "abbreviation": "IoJ"},
    {"id": 1016, "name": "Sea of Sorrows", "abbreviation": "SoS"},
    {"id": 1017, "name": "Tarnished Coast", "abbreviation": "TC"},
    {"id": 1018, "name": "Northern Shiverpeaks", "abbreviation": "NSP"},
    {"id": 1019, "name": "Blackgate", "abbreviation": "BG"},
    {"id": 1020, "name": "Ferguson's Crossing", "abbreviation": "FC"},
    {"id": 1021, "name": "Dragonbrand", "abbreviation": "DB"},
    {"id": 1022, "name": "Kaineng", "abbreviation": "KN"},
    {"id": 1023, "name": "Devona's Rest", "abbreviation": "DR"},
    {"id": 1024, "name": "Eredon Terrace", "abbreviation": "ET"},
    {"id": 2001, "name": "Fissure of Woe", "abbreviation": "FoW"},
    {"id": 2002, "name": "Desolation", "abbreviation": "Des"},
    {"id": 2003, "name": "Gandara", "abbreviation": "Gan"},
    {"id": 2004, "name": "Blacktide", "abbreviation": "BT"},
    {"id": 2005, "name": "Ring of Fire", "abbreviation": "RoF"},
    {"id": 2006, "name": "Underworld", "abbreviation": "Und"},
    {"id": 2007, "name": "Far Shiverpeaks", "abbreviation": "FS"},
    {"id": 2008, "name": "Whiteside Ridge", "abbreviation": "WR"},
    {"id": 2009, "name": "Ruins of Surmia", "abbreviation": "RoS"},
    {"id": 2010, "name": "Seafarer's Rest", "abbreviation": "SR"},
    {"id": 2011, "name": "Vabbi", "abbreviation": "Vab"},
    {"id": 2012, "name": "Piken Square", "abbreviation": "PS"},
    {"id": 2013, "name": "Aurora Glade", "abbreviation": "AG"},
    {"id": 2014, "name": "Gunnar's Hold", "abbreviation": "GH"},
    {"id": 2101, "name": "Jade Sea [FR]", "abbreviation": "JS"},
    {"id": 2102, "name": "Fort Ranik [FR]", "abbreviation": "FR"},
    {"id": 2103, "name": "Augury Rock [FR]", "abbreviation": "AG"},
    {"id": 2104, "name": "Vizunah Square [FR]", "abbreviation": "VS"},
    {"id": 2105, "name": "Arborstone [FR]", "abbreviation": "Arb"},
    {"id": 2201, "name": "Kodash [DE]", "abbreviation": "Kod"},
    {"id": 2202, "name": "Riverside [DE]", "abbreviation": "RS"},
    {"id": 2203, "name": "Elona Reach [DE]", "abbreviation": "ER"},
    {"id": 2204, "name": "Abaddon's Mouth [DE]", "abbreviation": "AM"},
    {"id": 2205, "name": "Drakkar Lake [DE]", "abbreviation": "DL"},
    {"id": 2206, "name": "Miller's Sound [DE]", "abbreviation": "MS"},
    {"id": 2207, "name": "Dzagonur [DE]", "abbreviation": "Dzg"},
    {"id": 2301, "name": "Baruch Bay [SP]", "abbreviation": "BB"}
]
