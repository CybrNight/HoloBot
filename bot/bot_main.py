import sys
import os

import discord
from discord.ext.commands import Bot
from bot.reference import *
from time import sleep

intents = discord.Intents.all()
intents.members = True
intents.presences = True
intents.bans = True

bot = Bot(command_prefix=BOT_PREFIX, intents=intents)
bot.remove_command("help")
cogs_dir = "cogs"
print(f"Running Python {sys.version}")

cogs = os.listdir(cogs_dir)


@bot.event
async def on_ready():
    print("Logged in!")

if __name__ == "__main__":
    for extension in [f.replace('.py', '') for f in cogs
                      if os.path.isfile(os.path.join(cogs_dir, f))]:
        try:
            bot.load_extension(f"{cogs_dir}.{extension}")
            print(f"Loaded extension: {extension}")
            sleep(0.1)
        except Exception as e:
            print(e)

            raise Warning(f'Failed to load extension: {extension}.')
    try:
        bot.run("NzU1NjY1MjA0MDQ5NzM5ODY3.X2GmEA.MEPoN8o4cIP2LBEgYgQMzPYF5-8")
    except Exception as e:
        print(f"{e} Stopping execution!")
        sys.exit()