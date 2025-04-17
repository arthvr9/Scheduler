import discord
from discord.ext import commands
from datetime import datetime
import mysql.connector as mysql
import asyncio

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

conexao = conectar()
cursor = conexao.cursor()

def Agendamento(nome, data, descricao, user):
    if isinstance(data, str):
        try:
            data = datetime.fromisoformat(data)
        except ValueError:
            data = datetime.strptime(data, '%Y-%m-%d %H:%M')

    data_formatada = data.strftime('%Y-%m-%d %H:%M:%S')
    
    comando = f'INSERT INTO schedule.agendamentos (nome_evento, data_evento, descricao_evento, user_agd) VALUES ("{nome}", "{data_formatada}", "{descricao}", "{user}")'
    cursor.execute(comando)
    conexao.commit()
    

@bot.command()
async def adicionar(ctx, nome, data, descricao):
    username = ctx.author.name
    pergunta = await ctx.send(f"Evento {nome}, dia {data}, {descricao} \ndeseja confirmar?\n✅ = Sim\n❌ = Cancelar")
    
    await pergunta.add_reaction('✅')
    await pergunta.add_reaction('❌')
    
    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ['✅', '❌'] and reaction.message.id == pergunta.id

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)

        if str(reaction.emoji) == '✅':
            await ctx.send(f"Evento confirmado por {user.name} !")
            Agendamento(nome, data, descricao, username)
        else:
            await ctx.send(f"Evento cancelado por {user.name} !")

    except asyncio.TimeoutError:
        await ctx.send(f"{ctx.author.name}, você não respondeu a tempo, tente novamente!")


bot.run(TOKEN)