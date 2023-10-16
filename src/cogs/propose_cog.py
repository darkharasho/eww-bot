import discord.ui

from config.imports import *
from discord.ext import commands
from src import settings
from src import helpers
from src import authorization
from src.bot_client import bot
from src.views import proposal_view

tree = bot.tree


class ProposeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild = bot.get_guild(settings.GUILD_ID)

    @tree.command(
        name="propose",
        description="Propose member for promotion",
        guild=discord.Object(id=settings.GUILD_ID)
    )
    async def propose(self, interaction, member: discord.Member, role: discord.Role):
        if await authorization.ensure_admin(interaction):
            db_member = Member.find_or_create(member=member)
            embed = discord.Embed(
                title="Proposal",
                description=f"**By:** {interaction.user.mention}\n**Member:** {member.mention}\n "
                            f"**Rank:** {role.mention}",
                color=member.top_role.color
            )

            review_channel = self.bot.get_channel(Config.review_forum_channel_id())
            reviewed_count = 0
            unreviewed_count = 0
            for thread in review_channel.threads:
                if thread.owner_id == member.id:
                    if "Reviewed" in [forum_tag.name for forum_tag in thread.applied_tags]:
                        reviewed_count += 1
                    else:
                        unreviewed_count += 1

            embed.add_field(name="Current Role", value=member.top_role.mention, inline=True)
            embed.add_field(name="Member Since", value=member.joined_at.strftime("%m/%d/%y"), inline=True)
            embed.add_field(name="Attendance", value=db_member.total_count(), inline=True)
            embed.add_field(name="Reviewed", value=reviewed_count, inline=True)
            embed.add_field(name="Unreviewed", value=unreviewed_count, inline=True)
            embed.add_field(name="Yays", value="", inline=False)
            embed.add_field(name="Nays", value="", inline=False)

            embed.set_thumbnail(url=member.display_avatar.url)

            view = proposal_view.ProposalView(embed)

            await interaction.response.send_message(embed=embed, view=view)

            events = [
                bot.wait_for('interaction',
                             check=lambda inter: inter.user == interaction.user and inter.channel == interaction.channel)
            ]

            # with asyncio.FIRST_COMPLETED, this triggers as soon as one of the events is fired
            done, pending = await asyncio.wait(events, return_when=asyncio.FIRST_COMPLETED)
            event = done.pop().result()
            try:
                await event.response.defer()
            except:
                pass


async def setup(bot):
    await bot.add_cog(ProposeCog(bot), guild=bot.get_guild(settings.GUILD_ID), override=True)
