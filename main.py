import discord
from discord.ext import commands
from secrets import BOT_TOKEN
from pathlib import Path
import datetime as dt


intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="$", intents=intents)
bot.remove_command("help")


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="The Weeknd"))
    print(
        f"Successfully logged in as {bot.user} | {dt.datetime.now().strftime('%H:%M:%S')}")
    print(f"----------------------------------------------")

if __name__ == "__main__":
    cogs = [file.stem for file in Path(
        r"./cogs").glob("*.py") if file.stem != "config"]

    for cog in cogs:
        try:
            bot.load_extension(f"cogs.{cog}")
        except Exception as e:
            print(f"An error occured while trying to load {cog}.")
            print(e)


bot.run(BOT_TOKEN)
