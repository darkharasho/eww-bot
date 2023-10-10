import discord
from src import settings
from discord.ext import commands


class BotClient(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True

        super().__init__(command_prefix='$', intents=intents, application_id=settings.APPLICATION_ID)

    async def setup_hook(self) -> None:
        pass
        # from src.views.apply_view import ApplyView
        # from src.views.apply_mod_view import ApplyModView
        # from src.views.proposal_view import ProposalView
        # from src.views.set_config_view import SetConfigView
        # from src.views.set_build_view import SetBuildView
        # from src.views.set_multi_config_view import SetMultiConfigView
        # from src.views.class_select_view import ClassSelectView
        # from src.views.reason_view import ReasonView

        # # Register the persistent view for listening here.
        # # Note that this does not send the view to any message.
        # # In order to do this you need to first send a message with the View, which is shown below.
        # # If you have the message_id you can also pass it as a keyword argument, but for this example
        # # we don't have one.
        # self.add_view(ApplyView())
        # self.add_dynamic_items(ApplyModView)
        # self.add_view(ProposalView())
        # self.add_view(SetConfigView(embed=discord.Embed, msg=discord.Message))
        # self.add_view(SetBuildView())
        # self.add_view(SetMultiConfigView())
        # self.add_view(ClassSelectView(discord.Embed, discord.Message))
        # self.add_view(ReasonView())

    def guild(self):
        self.get_guild(settings.GUILD_ID)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')


bot = BotClient()
