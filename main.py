import discord
from discord.ext import commands
import os
import sqlite3
import random

# Configuración de Intents
intents = discord.Intents.default()
intents.voice_states = True 
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents)

ID_CANAL = 1446630362917896243

@bot.event
async def on_ready():
    configurar_bd()
    print(f'Bot conectado como: {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f"🌲 Se han sincronizado {len(synced)} comandos Slash.")
    except Exception as e:
        print(e)


# ---------AVISOS DE CANALES------------
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


# ________RULETA DE JUEGOS__________

def conectar_bd():
    # CREA LA BD "RULETA"
    conn = sqlite3.connect('ruleta.db')
    return conn

def configurar_bd():
    # SE CONECTA Y CREA UNA TABLA
    conn = conectar_bd()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS opciones_ruleta (
            nombre TEXT PRIMARY KEY
        )
    ''')
    conn.commit()
    conn.close()

# 1. COMANDO PARA AGREGAR OPCIONES
@bot.hybrid_command(name='agregar', description='Agrega una opción a la lista.')
async def agregar_opcion(ctx, *, opcion: str):
    """Agrega una opción a la lista."""
    try:
        conn = conectar_bd()
        cursor = conn.cursor()
        # Insertamos el juego (el (?) es por seguridad para evitar inyección SQL)
        cursor.execute("INSERT INTO opciones_ruleta (nombre) VALUES (?)", (opcion,))
        conn.commit()
        conn.close()
        await ctx.send(f'✅ Joya, agregué **{opcion}** a la lista.')
    except sqlite3.IntegrityError:
        await ctx.send(f'⚠️ Epa, **{opcion}** ya estaba en la lista.')

# 2. COMANDO PARA ELIMINAR JUEGOS
@bot.hybrid_command(name='eliminar', description='Elimina una opción de la lista.')
async def eliminar_opcion(ctx, *, opcion: str):
    """Elimina una opción de la lista."""
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM opciones_ruleta WHERE nombre = ?", (opcion,))
    
    # Verificamos si realmente borró algo (rowcount > 0)
    if cursor.rowcount > 0:
        await ctx.send(f'🗑️ Listo, **{opcion}** eliminado. Ya no lo volveremos a hacer.')
    else:
        await ctx.send(f'❌ No encontré **{opcion}** en la lista. Fíjate si lo escribiste bien.')
    
    conn.commit()
    conn.close()

# 3. COMANDO PARA VER LA LISTA
@bot.hybrid_command(name='lista', description='Muestra todas las opciones disponibles.')
async def ver_lista(ctx):
    """Muestra todas las opciones disponibles."""
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT nombre FROM opciones_ruleta")
    opciones = cursor.fetchall() # Esto nos devuelve una lista de tuplas: [('LoL',), ('CSGO',)]
    conn.close()

    if not opciones:
        await ctx.send('📭 La lista está vacía. Usá `!agregar <Nombre>` para agregar opciones a la ruleta.')
        return

    # Formateamos bonito: sacamos el texto de las tuplas y los unimos
    lista_texto = "\n".join([f"• {j[0]}" for j in opciones])
    
    # Creamos un Embed (tarjeta con diseño)
    embed = discord.Embed(title="🎮 Lista de opciones", description=lista_texto, color=discord.Color.blue())
    await ctx.send(embed=embed)

# 4. COMANDO DE LA RULETA
@bot.hybrid_command(name='ruleta', description='Elige una opción al azar de la lista.')
async def tirar_ruleta(ctx):
    """Elige una opción al azar de la base de datos."""
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT nombre FROM opciones_ruleta")
    opciones = cursor.fetchall()
    conn.close()

    if not opciones:
        await ctx.send('🤷‍♂️ No hay opciones en la lista para elegir.')
        return

    elegido = random.choice(opciones)[0] # [0] porque viene como tupla ('Juego',)
    await ctx.send(f'🎲 La ruleta giró y el destino eligió: **{elegido}** 🏆')


TOKEN = os.environ.get('DISCORD_TOKEN') 

if TOKEN is None:
    print("ERROR DE CONFIGURACIÓN: La variable de entorno 'DISCORD_TOKEN' no está configurada.")
else:
    bot.run(TOKEN)
