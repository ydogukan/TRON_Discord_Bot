import discord
import datetime as dt

main_color = 0xc20000
# ctx.author.color for user based coloring


def get_embed(ctx, description, footer=False):
    embed = discord.Embed(
        description=description,
        color=main_color,
    )

    if footer:
        embed.timestamp = dt.datetime.utcnow()
        embed.set_footer(
            text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)

    return embed


def get_embed_with_title(ctx, title, description, footer=False):
    embed = discord.Embed(
        title=title,
        description=description,
        color=main_color,
    )

    if footer:
        embed.timestamp = dt.datetime.utcnow()
        embed.set_footer(
            text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)

    return embed


def get_command_error_embed(ctx, command_name, description, footer=False):
    embed = discord.Embed(
        title=command_name + " Error",
        description=description,
        color=main_color,
    )

    if footer:
        embed.timestamp = dt.datetime.utcnow()
        embed.set_footer(
            text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)

    return embed
