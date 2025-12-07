import discord
from discord.ext import commands
# from keep_alive import keep_alive
import os

# Configuración de Intents
intents = discord.Intents.default()
intents.voice_states = True 
intents.guilds = True

bot = commands.Bot(command_prefix='$', intents=intents)

ID_CANAL = 1446630362917896243

@bot.event
async def on_ready():
    print(f'Bot conectado como: {bot.user}')

@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel == after.channel:
        return
    
    channel = bot.get_channel(ID_CANAL)

    if after.channel is not None:

        if after.channel.name == "General":
            await channel.send(f"Se acabó la tranquilidad, {member.mention} ha llegado al canal de voz.")
        elif after.channel.name == "Musiquita":
            await channel.send(f"{member.mention} está aquí. Si pone Lali, lo baneamos.")

TOKEN = os.environ.get('DISCORD_TOKEN') 

if TOKEN is None:
    print("ERROR DE CONFIGURACIÓN: La variable de entorno 'DISCORD_TOKEN' no está configurada.")
else:
    bot.run(TOKEN)
