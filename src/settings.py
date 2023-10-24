# settings.py
import json

import discord

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
OPEN_AI_KEY = config.get('OpenAIKey', {})

MODULES = [
    "apply",
    "attendance",
    "check-attendance",
    "clear-key",
    "funderboard",
    "import-builds",
    "leaderboard",
    "manual-raid-reminder",
    "propose",
    "raid-notification",
    "raid-reminder",
    "set-build",
    "set-key",
    "show-attendance",
    "stats",
    "sync-leaderboard",
    "time-in-role",
    "toggle-soundboard"
]

CONFIG_OPTIONS = [
    "guild_member_role_id",
    "disabled_modules",
    "allowed_admin_role_ids",
    "build_manager_role_ids",
    "game_updates",
    "arcdps_updates",
    "review_forum_channel_id",
    "raid_reminder",
    "raid_notification",
    "auto_attendance",
    "build_update_channel_id",
    "build_forum_channel_id",
    "raid_days",
    "commander_role_ids"
]

SET_BUILD_UPDATE_CHANNEL =[
    {
        "text": "# Channel to post build updates:",
        "field_type": "input",
        "response_type": "text_channel"
    }
]

AUTO_ATTENDANCE_CONFIG = questions = [
    {
        "text": "# Enabled?",
        "field_type": "select",
        "options": [True, False],
        "response_type": bool
    },
    {
        "text": "# Channel to send attendance sheet:",
        "field_type": "input",
        "response_type": "text_channel"
    },
    {
        "text": "# Time to run\n### In 24hr format UTC, ex: 1:05 is 6:05pm PST",
        "field_type": "input",
        "response_type": "time"
    }
]

RAID_NOTIFICATION_CONFIG = [
    {
        "text": "# Roles to ping",
        "field_type": "input",
        "response_type": "roles"
    },
    {
        "text": "# Closed Tag Notification Channel:",
        "field_type": "input",
        "response_type": "text_channel"
    },
    {
        "text": "# Open Tag Roles to ping",
        "field_type": "input",
        "response_type": "roles"
    },
    {
        "text": "# Open Tag Notification Channel:",
        "field_type": "input",
        "response_type": "text_channel"
    }
]

RAID_REMINDER_CONFIG = [
    {
        "text": "# Channel to post the reminder",
        "field_type": "input",
        "response_type": "text_channel"
    },
    {
        "text": "# Roles to ping",
        "field_type": "input",
        "response_type": "roles"
    },
    {
        "text": "# Style of the table",
        "field_type": "select",
        "options": ["fancy_grid", "simple", "list_view"]
    },
    {
        "text": "# Hide empty rows?",
        "field_type": "select",
        "options": [True, False],
        "response_type": bool
    },
    {
        "text": "# Time to Post Notification\n### In 24hr format UTC, ex: 1:05 is 6:05pm PST",
        "field_type": "input",
        "response_type": "time"
    },
    {
        "text": "# Classes\n### Max: 25\n(list all numbers)",
        "field_type": "input",
        "response_type": "gw2_classes"
    }
]

SET_ARCDPS_UPDATES = [
    {
        "text": "# Enabled?",
        "field_type": "select",
        "options": [True, False],
        "response_type": bool
    },
    {
        "text": "# Channel to post the updates in",
        "field_type": "input",
        "response_type": "text_channel"
    }
]

SET_GAME_UPDATES = [
    {
        "text": "# Enabled?",
        "field_type": "select",
        "options": [True, False],
        "response_type": bool
    },
    {
        "text": "# Channel to post the updates in",
        "field_type": "input",
        "response_type": "text_channel"
    }
]

SET_COMMANDER_ROLES = [
    {
        "text": "# Commander Roles",
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
