import discord
from discord.ext import commands
import datetime
import mysql.connector as mysql

TOKEN = "" #remove before commit
CHANNEL_ID = 1362380936653705306

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
 
def conectar():
    return mysql.connect(
        host = 'localhost',
        user = 'root',
        password = '', #remove before commit
        database = 'schedule'
    )


@bot.command()
async def adicionar(ctx):
    await ctx.send("")


bot.run(TOKEN)