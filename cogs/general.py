import discord
from discord.ext import commands
from embeds import get_embed, get_command_error_embed, main_color


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="send")
    async def _send(self, ctx, channel_name, *, arg):
        channel = discord.utils.get(ctx.guild.channels, name=channel_name)

        if channel:
            try:
                embed = get_embed(ctx, arg)
                await channel.send(embed=embed)

            except Exception as e:
                print(e)
                embed = get_command_error_embed(
                    ctx, "Send", f"Cannot send a message to the specified channel due to **missing permissions or access**.")
                await ctx.send(embed=embed)

        else:
            embed = get_command_error_embed(
                ctx, "Send", f"No channel with {channel_name} exists.")
            await ctx.send(embed=embed)

    @_send.error
    async def send_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = get_command_error_embed(
                ctx, "Send", f"Please enter a **channel name** and a **message** that you wish to send.\nExample usage: **$send general WASSUP YO**")
            await ctx.send(embed=embed)

    @commands.command()
    async def status(self, ctx):
        embed = get_embed(
            ctx, f"`{self.bot.user}` is **online** and **ready for commands**.", True)
        await ctx.send(embed=embed)

    @commands.command()
    async def help(self, ctx):
        all_commands = {}
        for command in self.bot.commands:
            if command.cog.qualified_name in all_commands:
                all_commands[command.cog.qualified_name].append(
                    f"`{command.name}`")

            else:
                all_commands[command.cog.qualified_name] = [
                    f"`{command.name}`"]

        embed = discord.Embed(
            title="Bot Commands",
            description="Use `$` prefix with the commands listed below.\nExample usage: **$play XP**",
            color=main_color,
        )

        for cog, commands in sorted(all_commands.items()):
            embed.add_field(
                name=f"{cog.capitalize()} — {len(commands)}",
                value=", ".join(sorted(commands)),
                inline=False
            )

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(General(bot))
