import discord
from discord.ext import commands
import json
from embeds import get_embed, get_command_error_embed

with open("responses.json") as f:
    responses = json.load(f)


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if message.content in responses:
            embed = get_embed(message, responses[message.content])
            await message.channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            embed = get_command_error_embed(ctx, "Command",
                                            f"The command **{ctx.message.content.split(' ')[0][1:]}** does not exist.\nPlease use **$help** to get a list of all the available commands.")
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Events(bot))
