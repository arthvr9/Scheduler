import discord
from discord.ext import commands, tasks
from discord import app_commands
from datetime import datetime, timedelta
import mysql.connector as mysql
import asyncio

TOKEN = ""  # token here
CHANNEL_ID = 1362121049990496436

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# connecting with the database
def conectar():
    return mysql.connect(
        host='localhost',
        user='root',
        password='',  # Insira a senha do seu banco de dados
        database='schedule'
    )

conexao = conectar()
cursor = conexao.cursor()

# scheduling function
def Agendamento(nome, data, descricao, user):
    if isinstance(data, str):
        try:
            data = datetime.fromisoformat(data)
        except ValueError:
            data = datetime.strptime(data, '%Y-%m-%d %H:%M')

    data_formatada = data.strftime('%Y-%m-%d %H:%M:%S') #formatting to YYYY-MM-DD
    
    comando = f'INSERT INTO schedule.agendamentos (nome_evento, data_evento, descricao_evento, user_agd) VALUES ("{nome}", "{data_formatada}", "{descricao}", "{user}")'
    cursor.execute(comando)
    conexao.commit()

# /adicionar slash command
@bot.tree.command(name="adicionar", description="Adiciona um evento ao calendário")
async def adicionar(interaction: discord.Interaction, nome: str, data: str, descricao: str):
    """Adiciona um evento ao calendário"""
    username = interaction.user.name
    pergunta = await interaction.response.send_message(
        f"Confirmação pendente...",
        ephemeral=True
    )
    
    # Envia uma mensagem normal no canal de interação
    mensagem = await interaction.followup.send(
        f"Evento {nome}, dia {data}, {descricao} \ndeseja confirmar?\n✅ = Sim\n❌ = Cancelar"
    )
    
    # Aguarda reação
    await mensagem.add_reaction('✅')
    await mensagem.add_reaction('❌')

    def check(reaction, user):
        return user == interaction.user and str(reaction.emoji) in ['✅', '❌'] and reaction.message.id == mensagem.id

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)

        if str(reaction.emoji) == '✅':
            await interaction.followup.send(f"Evento confirmado por {user.name}!")
            Agendamento(nome, data, descricao, username)
        else:
            await interaction.followup.send(f"Evento cancelado por {user.name}!")

    except asyncio.TimeoutError:
        await interaction.followup.send(f"{interaction.user.name}, você não respondeu a tempo, tente novamente!")

# /eventos command
@bot.tree.command(name="eventos", description="Lista os eventos agendados")
async def eventos(interaction: discord.Interaction):
    comando = 'SELECT nome_evento, data_evento, user_agd FROM schedule.agendamentos'
    cursor.execute(comando)
    eventos = cursor.fetchall()

    if not eventos:
        await interaction.response.send_message("Nenhum evento agendado! 📅", ephemeral=True)
        return

    agora = datetime.now()

    embed = discord.Embed(
        title="📋 Eventos Agendados",
        description="Aqui estão os eventos que estão programados!",
        color=discord.Color.blue()
    )

    for evento in eventos:
        nome_evento, data_evento, user_agd = evento

        # convert to datetime
        if isinstance(data_evento, str):
            data_evento = datetime.strptime(data_evento, '%Y-%m-%d %H:%M:%S')

        tempo_restante = data_evento - agora

        dias = tempo_restante.days
        horas = tempo_restante.seconds // 3600
        minutos = (tempo_restante.seconds % 3600) // 60

        embed.add_field(
            name=f"🗓️ {nome_evento}",
            value=(f"**Data:** {data_evento.strftime('%d/%m/%Y %H:%M')}\n"
                   f"**Adicionado por:** {user_agd}\n"
                   f"**Tempo Restante:** {dias} dias, {horas} horas, {minutos} minutos"),
            inline=False
        )

    await interaction.response.send_message(embed=embed)

# alert function
@tasks.loop(hours=24)  # trigger to alert in the specified time, can alter to minutes or seconds
async def verificar_alertas():
    agora = datetime.now()

    comando = 'SELECT nome_evento, data_evento, user_agd FROM schedule.agendamentos'
    cursor.execute(comando)
    eventos = cursor.fetchall()

    for evento in eventos:
        nome_evento, data_evento, user_agd = evento

        # converting to datetime
        if isinstance(data_evento, str):
            data_evento = datetime.strptime(data_evento, '%Y-%m-%d %H:%M:%S')

        tempo_restante = data_evento - agora

        dias_restantes = tempo_restante.days

        if dias_restantes in [30, 14, 7, 1]:
            canal = bot.get_channel(CHANNEL_ID)
            if canal:
                await canal.send(f"🔔 Atenção: o evento **{nome_evento}** de {user_agd} acontece em {dias_restantes} dia(s)!")


#ping
@bot.tree.command(name="ping", description="ping")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("pong")

# initializing
@bot.event
async def on_ready():
    print(f'Bot {bot.user} está online!')
    await bot.tree.sync()  # syncing slash commands
    print("Comandos Slash sincronizados com o Discord!")
    verificar_alertas.start()

bot.run(TOKEN)
