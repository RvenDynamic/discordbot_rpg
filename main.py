import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

from commands import setup

load_dotenv()

token = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

setup(bot)

@bot.event
async def on_ready():
    print(f'Bot sudah online sebagai {bot.user}')

bot.run(token)
