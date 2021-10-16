import discord
from discord.ext import commands
import datetime as dt
from embeds import get_embed, get_command_error_embed


def is_guild_owner():
    def predicate(ctx):
        return ctx.guild is not None and ctx.guild.owner_id == ctx.author.id
    return commands.check(predicate)


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @is_guild_owner()
    async def clear(self, ctx, limit=5):
        if (limit > 0):
            if (limit <= 50):
                await ctx.channel.purge(limit=int(limit) + 1)

            else:
                embed = get_command_error_embed(
                    ctx, "Clear", f"It is **prohibited** to delete more than 50 messages at once.")
                await ctx.send(embed=embed)

        else:
            embed = get_command_error_embed(
                ctx, "Clear", f"Number of messages to be deleted must be **positive**.")
            await ctx.send(embed=embed)

    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            embed = get_command_error_embed(
                ctx, "Clear", f"**{ctx.author}** lacks the necessary permissions to use **clear** command.")
            await ctx.send(embed=embed)

        elif isinstance(error, commands.BadArgument):
            embed = get_command_error_embed(
                ctx, "Clear", f"**clear** command requires an integer.\nExample usage: **$clear 5**")
            await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        try:
            await member.kick(reason=reason)
            embed = get_embed(
                ctx, f"**{member}** has been kicked from the server.")
            await ctx.send(embed=embed)

        except Exception as e:
            print(e)
            embed = get_command_error_embed(
                ctx, "Kick", f"Cannot kick **{member}** due to missing permissions.")
            await ctx.send(embed=embed)

    @kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = get_command_error_embed(
                ctx, "Kick", f"**{ctx.author}** lacks the necessary permissions to use **kick** command.")
            await ctx.send(embed=embed)

        elif isinstance(error, commands.BadArgument):
            embed = get_command_error_embed(
                ctx, "Kick", f"No such member **exists** in the server.")
            await ctx.send(embed=embed)

        elif isinstance(error, commands.MissingRequiredArgument):
            embed = get_command_error_embed(
                ctx, "Kick", f"**kick** command a requires username / display name / user ID / @mention.\nExample usage: **$kick Jaden**")
            await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        try:
            await member.ban(reason=reason)
            embed = get_embed(
                ctx, f"**{member}** has been banned from the server.")
            await ctx.send(embed=embed)

        except Exception as e:
            print(e)
            embed = get_command_error_embed(
                ctx, "Ban", f"Cannot ban **{member}** due to missing permissions.")
            await ctx.send(embed=embed)

    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = get_command_error_embed(
                ctx, "Ban", f"**{ctx.author}** lacks the necessary permissions to use **ban** command.")
            await ctx.send(embed=embed)

        elif isinstance(error, commands.BadArgument):
            embed = get_command_error_embed(
                ctx, "Ban", f"No such member **exists** in the server.")
            await ctx.send(embed=embed)

        elif isinstance(error, commands.MissingRequiredArgument):
            embed = get_command_error_embed(
                ctx, "Ban", f"**ban** command a requires username / display name / user ID / @mention.\nExample usage: **$ban Jaden**")
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Admin(bot))
