##################################
# Helpers ########################
##################################
from config.imports import *
from discord.ext import commands
from src import settings
from src.bot_client import bot
from thefuzz import fuzz
from thefuzz import process


def find_base_class_by_espec(target_value):
    for key, values in settings.CLASS_ELITE_SPECS.items():
        if target_value in values:
            return key
    return None  # Return None if the target_value is not found in any list


def command_to_cog(command):
    cmd2cog = re.sub(r'-', '_', command)
    cmd2cog = re.sub(r'_', '', (cmd2cog + "_cog").title())
    print(cmd2cog)


def get_by_name(nameable_objects, name):
    for nameable_object in nameable_objects:
        if nameable_object.name == name:
            return nameable_object
    return None


def get_by_list_of_names(nameable_objects, names):
    objects = []
    for name in names:
        obj = get_by_name(nameable_objects, name)
        if obj:
            objects.append(obj)
    return objects


def select_tag(available_tags, tag_name):
    selected_tag = None

    for tag in available_tags:
        for class_name, specializations in settings.CLASS_ELITE_SPECS.items():
            if tag.name == class_name and any(spec in tag_name for spec in specializations):
                selected_tag = tag
                break
        if selected_tag:
            break

    return selected_tag


def select_file(class_name):
    img_dir = os.path.dirname(os.path.abspath(__file__))

    selected_class = next((c for c in settings.BASE_CLASSES if c in class_name), None)

    if selected_class:
        selected_file = os.path.join(img_dir, f"../class_icons/120px-{selected_class}_tango_icon_200px.png")
    else:
        selected_file = None

    return selected_file


def select_icon(icon_name, file_type="png"):
    img_dir = os.path.dirname(os.path.abspath(__file__))

    if icon_name:
        selected_file = os.path.join(img_dir, f"../icons/{icon_name}.{file_type}")
    else:
        selected_file = None

    return selected_file


async def delete_thread(channel, thread_title):
    if channel:
        # Iterate through the threads in the guild
        for thread in channel.threads:
            if thread.name == thread_title:
                # Delete the thread
                await thread.delete()
                return


async def post_update(channel, thread, filename, title, user):
    img_dir = os.path.dirname(os.path.abspath(__file__))
    color = settings.CLASS_COLORS[find_base_class_by_espec(title)]

    embed = discord.Embed(title="New Comp Build Update", description=title, color=color)
    embed.add_field(name="Link", value=find_emoji_by_name_pattern(title) + " " + thread.jump_url, inline=False)

    file = discord.File(os.path.join(img_dir, f"../class_icons/{filename}"))

    embed.set_thumbnail(url=f"attachment://{file.filename}")
    embed.add_field(name="Updated By", value=user.name, inline=True)
    embed.add_field(name="Updated On", value=datetime.datetime.today().strftime("%m/%d/%y"), inline=True)
    await channel.send(
        embed=embed,
        file=file
    )


def align_list(list_to_align):
    result_array = []

    # Iterate through each sub-array and join its elements with proper spacing
    for sub_array in list_to_align:
        # Join the elements with a space and add the result to the result array
        result = " ".join(sub_array)
        result_array.append(result)

    return "\n".join(result_array)


def strip_emojis(text):
    # Define a regular expression pattern to match emojis
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # Emoticons
                               u"\U0001F300-\U0001F5FF"  # Miscellaneous Symbols and Pictographs
                               u"\U0001F680-\U0001F6FF"  # Transport and Map Symbols
                               u"\U0001F700-\U0001F77F"  # Alchemical Symbols
                               u"\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
                               u"\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
                               u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
                               u"\U0001FA00-\U0001FA6F"  # Chess Symbols
                               u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
                               u"\U0001F004-\U0001F0CF"  # Additional emoticons
                               u"\U0001F200-\U0001F251"  # Additional T-shaped images
                               "]+", flags=re.UNICODE)

    # Use re.sub to remove emojis
    text_without_emojis = emoji_pattern.sub('', text)

    return text_without_emojis


def check_guild_role(member=discord.Member):
    return Config.guild_member_role_id() in [role.id for role in member.roles]


async def find_role_by_name(guild, role_name):
    for role in guild.roles:
        if role.name.lower() == role_name.lower():
            return role
    return None


async def class_list(
        interaction: discord.Interaction,
        current: str,
) -> list[app_commands.Choice[str]]:
    classes = []
    for gw2_class in settings.CLASS_ELITE_SPECS:
        for gw2_spec in settings.CLASS_ELITE_SPECS[gw2_class]:
            classes.append(gw2_spec)
    return [
        app_commands.Choice(name=class_name, value=class_name)
        for class_name in classes if current.lower() in class_name.lower()
    ]


def find_emoji_by_name_pattern(name):
    guild = bot.get_guild(settings.GUILD_ID)
    best_match, score = process.extractOne(name, [emoji.name for emoji in guild.emojis])

    if score < 30:
        return "✅"

    full_emoji = None
    for emoji in guild.emojis:
        if best_match == emoji.name:
            full_emoji = emoji

    if full_emoji:
        return f"<:{full_emoji.name}:{full_emoji.id}>"
    else:
        return "✅"


def find_emoji_by_name(name):
    guild = bot.get_guild(settings.GUILD_ID)
    matching_emojis = []
    for emoji in guild.emojis:
        if emoji.name == name:
            matching_emojis.append(emoji)

    if not matching_emojis:
        return "✅"
    else:
        return f"<:{matching_emojis[0].name}:{matching_emojis[0].id}>"


def build_embed(user=discord.Member, class_name=str, name=str, link=str, chat_code=str, description=str):
    color = settings.CLASS_COLORS[find_base_class_by_espec(class_name)]

    embed = discord.Embed(title=name, description=f"[gw2skills.net - {class_name} Build]({link})", color=color)
    embed.add_field(name="Chat Code", value=f"```{chat_code}```", inline=False)
    if description != '':
        embed.add_field(name="Description", value=description, inline=False)
    # Add a field "Updated By" with the name of the invoking user
    embed.add_field(name="Updated By", value=user.name, inline=True)
    embed.add_field(name="Updated On", value=datetime.datetime.today().strftime("%m/%d/%y"), inline=True)

    # Find the correct tango icon
    file_name = select_file(class_name)
    file = discord.File(file_name)
    embed.set_thumbnail(url=f"attachment://{file.filename}")

    return embed, file


def check_raid_day():
    try:
        current_day = datetime.datetime.now().weekday()
        return current_day in Config.raid_days()
    except ValueError:
        # Handle invalid day format
        return False


def format_number(number):
    number = int(number)
    if number < 1000:
        return str(number)
    elif number < 10000:
        return f"{number // 1000}k"
    elif number < 1000000:
        return f"{number / 1000:.1f}k"
    elif number < 10000000:
        return f"{number // 1000000}M"
    else:
        return f"{number / 1000000:.1f}M"


def abbreviate_world_name(server_name):
    for listed_server in settings.SERVER_NAMES:
        if listed_server["name"] == server_name:
            return listed_server["abbreviation"]
    return "N/A"


def calculate_kd(kills: int, deaths: int):
    if kills == 0:
        return 0
    elif deaths == 0:
        return kills
    kd_float = kills / deaths
    return float("%.2f" % kd_float)


def get_timezone_from_str(timezone_str):
    # Split the timezone string to extract the offset hours and minutes
    parts = timezone_str.split("/")

    # Create a timedelta object for the offset
    offset_hours = int(parts[0])
    offset_minutes = int(parts[1])
    offset = datetime.timedelta(hours=offset_hours, minutes=offset_minutes)

    # Create a timezone object with the given offset
    tz = datetime.timezone(offset)
    return tz


async def emoji_list(position: str):
    guild = bot.get_guild(settings.GUILD_ID)

    if position == "first":
        emoji = find_emoji_by_name("reply_continue")

        if emoji == "✅":
            emoji = await guild.create_custom_emoji(
                name="reply_continue",
                image=open("icons/emoji/reply-continue.png", "rb").read()
            )
    elif position == "member":
        emoji = find_emoji_by_name("reply_continue_2")

        if emoji == "✅":
            emoji = await guild.create_custom_emoji(
                name="reply_continue_2",
                image=open("icons/emoji/reply-continue-2.png", "rb").read()
            )
    elif position == "end":
        emoji = find_emoji_by_name("reply_continue_end")

        if emoji == "✅":
            emoji = await guild.create_custom_emoji(
                name="reply_continue_end",
                image=open("icons/emoji/reply-continue-end.png", "rb").read()
            )
    else:
        emoji = find_emoji_by_name("reply_single")

        if emoji == "✅":
            emoji = await guild.create_custom_emoji(
                name="reply_single",
                image=open("icons/emoji/reply-single.png", "rb").read()
            )

    return emoji


def guild():
    return bot.get_guild(settings.GUILD_ID)
